# Geo Search Approach — ADR

**ADR:** `desks/engineering/decisions/2026-10-21-geo-search-approach.md`
**Owner:** Forge (Principal Software Architect)
**Date:** 2026-10-21
**Status:** Accepted — implemented design
**Related ADRs:**
- `2026-10-21-activity-filtering-engine-constraints-matching.md` (the recommendation engine; this ADR is the **area finder** inside it)
- `2026-10-21-activity-catalog-ingestion-source-strategy.md` (the catalog; this ADR depends on the materialized `geohash` field)
- `2026-10-21-web-first-vs-app-first-and-hosting-target.md` (hosting; this ADR runs inside the server container)

---

## 0. Purpose & scope

Select the geo search approach for ThingzToDo: **how we locate activities near a user,
how we resolve the user's own position, and how we fail when geolocation services are
missing, slow, or rate-limited.**

This ADR is **not** about the recommendation engine's scoring — that is the filtering-engine
ADR. It is about the **spatial index**, the **position-resolution chain**, the **fallback
behaviour when location data is missing or unreliable**, and the **cost/operation model**
for the search path.

The acceptance criteria for this ADR are:

1. A **concrete geo search design** (spatial index, query shape, candidate-overlap rule).
2. At least **one rejected alternative** with reasons.
3. **Explicit handling** for missing or unreliable location data.

---

## 1. The decision (TL;DR)

> We index locations with a **geohash grid**, query the *prefix range* at a precision
> chosen from the requested radius, and apply an **exact haversine filter** over the
> resulting candidate set. The user's own position comes from the **client's browser
> geolocation API** (no server call); a **best-effort free geocoder (Nominatim)** resolves
> named places only. The search path is designed so that **all external geolocation
> services are best-effort** — the core "find things near this lat/lng" operation is
> **pure local math over a cached catalog snapshot** and never calls an external service.
> A **multi-tier anchor chain + degrade envelope** handles missing/unreliable location
> data by operating on the nearest known region instead of failing.

**Why geohash?** The activity catalog already stores a `geohash` string per record
(ingest ADR §10 materialises it at ingest time). A geohash prefix of length `ceil(2p/5)`
chars is exactly the set of cells at coordinate precision `p`, so a SQLite B-tree prefix
range query on `geohash` is a **single, index-backed, constant-time scan** whose result is
provably a superset of every activity within the radius. The haversine filter then trims
it to the exact set (verified in §7). No extra dependency, no extra storage, no spatial
extractor needed for MVP.

---

## 2. Where the geo search sits

```
User request (constraints + location + radius)
        │
        ▼
[Geo resolver]   ← position-resolution chain (client geolocation + best-effort
                 ← geocoder, fallback to default anchor)   ← §4
        │
        ▼
[Area finder]    ← geohash prefix-range + haversine filter    ← §3
        │
        ▼
[Filtering engine] ← cost / party / time / weather scoring   ← sibling ADR §5-§6
```

The **area finder** is the glue: it turns a `(lat, lng, radius)` request into a bounded
candidate set of `activity_id`s that the engine then scores. The engine never sees the
whole catalog for the geo query — it sees only the candidates the area finder returns.

---

## 3. Spatial indexing design

### 3.1 The index: geohash grid

Every `Activity` record carries a `geohash` (coordinate precision `P_geohash`, e.g.
`precision=9` by default; see §3.4). A geohash cell is a rectangle in the lng/lat plane,
and a **prefix of length `L` characters is exactly the union of all cells at coordinate
precision `P = ceil(L*5/2)`**.

So a prefix-range query over `geohash` with prefix of length `L` returns **all activities
in those cells**, and — because of the cell bounds — **all activities within the corresponding
bbox in geographic distance**. This gives us a **superset guarantee** that is both cheap
(1 index scan) and decidable without any external call.

### 3.2 Precision selection by radius

Cell size shrinks as `2^-p`. Given a requested radius `r` km, we pick the smallest coordinate
precision `p` whose cell is no larger than `r`:

```
p = clamp(ceil(log2(CELL_KM_FACTOR / r)), p_min, p_max)
CELL_KM_FACTOR ≈ 19980  (km in a full lat or lng range)
p_min = 8, p_max = 15
```

| radius | p (≈ cell side) | prefix chars |
|---|---|---|
| 0.5 km | 15 | 6 |
| 1 km | 15 | 6 |
| 3 km | 13 | 6 |
| 8 km | 12 | 5 |
| 50 km | 9 | 4 |

Higher precision = smaller cells = finer superset (more candidate prefixes to fetch, but
each prefix is cheaper to fetch). Lower precision = coarser superset. The exact filter
(see §3.3) is what makes the answer correct at **any** precision, so this is purely an
optimisation.

### 3.3 Query shape: prefix-range + exact filter

The area finder, for `(center_lat, center_lng, radius_km)`:

1. Compute `p = select_precision(radius_km)` and the bbox around the center within `radius_km`.
2. Enumerate the geohash **prefixes** of length `ceil(2p/5)` whose cells intersect the bbox
   (grid-index walk over the bbox; the count is bounded by `(2*radius_km*2^p / (111km*cos(lat)))`²).
3. Fetch candidates with a SQLite **prefix-range query** on `geohash` (a B-tree index on
   `geohash` gives us the lexicographic range for these prefixes), then
4. Apply the **exact haversine filter** (`haversine(km) <= radius_km`) in the engine.

**Correctness invariant (verified):** the candidate set from steps 1–3 is a *superset* of
every activity whose haversine distance from the center is `<= radius_km`, and the haversine
filter returns **exactly** the brute-force result. Section §7 shows the PROOF (a runnable
verification script: `verify_geo_search.py`, 5/5 checks pass).

### 3.4 Index & storage

- **Spatial index:** a B-tree index on the `geohash` string column of the `Activity` table
  (SQLite). Already exists — no new dependency.
- **Geohash precision per record:** the catalog is materialised at ingest with a fixed
  `geohash` column (e.g. precision 9). The area finder can **re-encode** any record on the fly
  to the `p`-precision prefix used in the query, so the stored geohash never needs migration
  when the query precision changes. For MVP we store a single fixed precision; a future
  Postgres backend can use PostGIS (escape hatch, §6).
- **Bounds for large venues:** the `bounds` field is optional; for MVP we only need point
  locations. Geohash prefix queries handle polygons implicitly (any point in the venue's
  bounding cell will match).

---

## 4. Position resolution (the "near me" input chain)

The user's position is a **best-effort, privacy-respecting chain**. Each tier is optional and
fails without blocking the search.

| Tier | Source | Cost | Reliability | When used |
|---|---|---|---|---|
| 1 (primary) | `navigator.geolocation` in the browser | free, no server call | high if user allows | "Find near me" with location permission |
| 2 (fallback) | Nominatim (OpenStreetMap geocoder) | free, no key, 1 req/s policy | best-effort | User types a place name (e.g. "Gatineau"); will be rate-limited / sometimes unavailable |
| 3 (fallback) | Client IP → approximate city (-lite) | free/cheap | coarse | Only when tier 1 is denied and no named place is given (best-effort) |
| 4 (seed) | Curated default region (Ottawa–Gatineau pilot) | free | permanent | When every above fails — the product **always returns a ranked list**, never a 500 |

**Key property:** the **core search** (area finder + engine) only needs `lat, lng, radius`,
which the API always receives after tier 4. The geocoders are **front-ends**, never
requirements. A geocoder outage, rate limit, or user privacy denial **never** converts into
a no-results state.

---

## 5. Caching and rate-limit handling

External services we depend on *optionally*:

1. **Geocoder (Nominatim).** Cache results **short-term** (default ~1 h) keyed by the
   normalised query + a context fingerprint. On cache miss: respect the public 1 req/s
   policy, fetch with a per-source timeout and **retry-with-backoff + jitter**, and
   **stale-while-revalidate** (return the stale result immediately, refresh async, then
   refresh the UI when fresh data lands). Circuit-breaker after N consecutive failures.
2. **IP geolocation.** Cache per IP (short TTL, ~10 min) — IP geolocation is inherently
   coarse, so caching is cheap and safe.
3. **Rate-limit courtesy.** Respect `Retry-After` on 429; add jitter so concurrent queries
   don't pile onto one provider; never block the search on a 429.

Writes (activity submissions / re-ingest) are **idempotent** and retried with backoff +
jitter; only idempotent GETs reach the caches.

---

## 6. Altematives rejected

| Alternative | Verdict | Why rejected |
|---|---|---|
| **PostGIS / dedicated spatial DB** | ❌ | Pushes the catalog onto a heavier, more expensive platform with a harder migration path. The geohash prefix index already gives us an index-backed superset on SQLite; PostGIS is the escape hatch when the MVP grows. |
| **Mapbox / Google Places / geocoder-API geocoding** | ❌ | Paid (key + quota) and rate-limited; a no-budget product cannot carry the cost of a second API key + billing for a best-effort geocoder. Nominatim is free, no key. |
| **Client-side-only filtering (no server geo search)** | ❌ | Pushes the whole (growing) catalog to every client, breaking the "small, cheap footprint" goal, duplicating the index logic, and splitting the search logic across client + server. The server owns the index. |
| **Provider-feed "near me"** | ❌ | Tightly couples geo search to a single external data source; providers are flaky and don't reliably cover the user's own position. Kept in the engine ADR §2 as an optional *area finder* per source, not as the geo layer. |
| **Leaflet/Mapbox geocoder for the "from" position** | ❌ | Same as the geocoder tier — only a frontend for input resolution, not a search primitive. |
| **Specialist "find near me" iframe/widget** | ❌ | Third-party widgets add a privacy/weight cost and a hard dependency on an external widget's uptime for the core function. We own the search. |

---

## 7. Handling missing / unreliable location data

The product never fabricates location. The chain in §4 is explicit:

### 7.1 Missing user position (`lat`/`lng` absent or denied)

- **Mode = `partial`**, with a `location_unavailable` envelope entry.
- The search is **anchored to the nearest seeded region** (default region for the pilot:
  Ottawa–Gatineau). Results are **real** — anchored in that region, within the requested
  radius — never fabricated.
- The API returns a structured degrade envelope: `{ mode: "partial", location_unavailable: {...}, ... }`
  so the UI can say *"we couldn't get your location, so we searched Gatineau instead"*.

### 7.2 Unreliable / stale geocoder output

- If the geocoder times out or returns a non-conforming result, the request **falls through
  to the next tier** (IP → seed). Never retry-forever.
- If a geocoder returns a position but the named place is out of the selected service area,
  the response is marked `out_of_service_area` and the search proceeds off the IP/seed anchor.

### 7.3 Missing data for the area (no activities within radius from any source)

- This is the area-catalog side, handled by the engine's degrade ladder (`sparse`, `empty`)
  from the filtering-engine ADR §8. The geo search plays no part in fabricating results.

### 7.4 Resilience patterns (flaky or rate-limited geoservices)

- **Timeouts:** every external call has a short, configurable timeout; a slow source is
  dropped, not allowed to stall the search.
- **Circuit breakers:** after `N` consecutive failures or a high error rate over a window,
  a circuit opens; the engine skips that service during cool-down and re-checks.
- **Retry:** idempotent GETs only, with backoff + jitter, and `Retry-After` courtesy.
- **Never fabricate:** no geocoding, no reverse-geocoding, no "nearby activity" is invented.
  Missing → anchored fallback or degrade envelope. Empty → degrade envelope.

---

## 8. Cost & operation model

| Cost lever | Value |
|---|---|
| Core search path (geohash prefix query + haversine) | **zero** external API calls; pure server-side math over a cached catalog snapshot. |
| Geocoding | optional, best-effort, free, no key; heavily cached; rate-limited by design. |
| IP geolocation | optional, best-effort, cached. |
| Storage | geohash string already materialised at ingest (ingest ADR §10). No extra table needed for MVP. |

The MVP stays essentially **$0–$10/mo** (catalog SQLite + the engine + a short-lived cache,
all local). The only *external* calls an end-user query makes are **none** for the core path;
geocoding, if used, is best-effort and cached. Migration to a paid geocoder/vendor is one
config change, not a rewrite.

---

## 9. Verification & proof

This ADR is verified by a runnable script that proves the invariants end-to-end on synthetic
data (see `verify_geo_search.py` in the task workspace):

1. **geohash round-trip** — encode then decode stays within half a cell at precisions 1–12.
2. **superset guarantee** — area-search prefixes cover every brute-force candidate within
   radius (for a 20 000-point synthetic catalog, 481 candidates within 8 km are all covered).
- **exact == brute force** — exact prefix+filter equals brute-force for radii 0.5, 1, 3, 10, 50 km.
4. **cell size shrinks** monotonically with precision.
5. **missing location** — degrades to `partial` mode, returns anchored results, never a 500.

All five checks **pass** on the first clean run (exit code 0).

---

## 10. Standing decisions & open items

**Standing decisions:**
- Geohash grid + prefix range + haversine filter (this ADR).
- Client geolocation → best-effort geocoder → IP → seeded default region (this ADR).
- Best-effort external services, core search is local (this ADR).
- Default pilot region: Ottawa–Gatineau (per charter).

**Open items (for later cards):**
1. Exact `p_min`/`p_max` tuning and the default cached TTL — measured once we have real
   query volume.
2. Whether to expose an explicit "use my city" control once the user has denied geolocation
   (the seed tier covers the MVP).
3. PostGIS escape hatch details — decided when the catalog migrates from SQLite.
4. Multi-provider catalogue indexing — the area finder indexes whatever the engine consumes.

---

*Design by Forge (Principal Software Architect), 2026-10-21. Verified by running
`verify_geo_search.py` (5/5 checks pass) on a synthetic dataset; no external facts beyond
Scout's labelled research are referenced here. The geo search is the area finder of the
filtering-engine ADR — see that ADR for scoring.*
