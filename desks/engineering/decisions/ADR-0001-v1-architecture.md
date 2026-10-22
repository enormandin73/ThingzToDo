# ADR-0001 — ThingzToDo Architecture Decision Record v1

**ADR:** `ADR-0001-v1-architecture.md`
**Owner:** Forge (Principal Software Architect)
**Date:** 2026-10-21
**Status:** Accepted
**Parent decision record:** This is the integrated, consolidated architecture decision record for ThingzToDo v1. It absorbs the decisions authored as separate ADRs by the engineering workstreams and presents them as one coherent architectural picture. The workstream ADRs remain the canonical primary sources; this document is the "single click to understand the architecture" view.

**Related ADRs (workstream outputs):**
| Workstream ADR | Topic |
|---|---|
| `2026-10-21-web-first-vs-app-first-and-hosting-target.md` | Product direction + hosting target (web-first, Fly.io) |
| `2026-10-21-framework-backend-and-data-store.md` | Frontend, backend, data store, toolchain |
| `2026-10-21-geo-search-approach.md` | Geo search: geohash + prefix range + haversine + fallback chain |
| `2026-10-21-activity-filtering-engine-constraints-matching.md` | Recommendation & filtering engine |
| `2026-10-21-activity-catalog-ingestion-source-strategy.md` | Activity catalog ingestion source strategy |
| `2026-10-21-outbound-email-path-readiness.md` | Outbound email path (blocked — no credentials) |

---

## 0. Purpose & scope

This ADR records **what ThingzToDo is built as, and why**, at the architecture level. It is the document a new engineer opens first to understand:

1. The **product shape** (web-first web app, PWA shell, no native apps on day one).
2. The **hosting target** (Fly.io, one Docker container, ~$0–$10/mo).
3. The **stack** (Next.js App Router + React on Node.js 22 LTS, SQLite via better-sqlite3).
4. The **geo search** approach (geohash + prefix-range + haversine + multi-tier fallback).
5. The **recommendation engine** (two-tier hard-gate + soft-score).
6. The **data ingestion source strategy** (curated core + best-effort enrichment + moderated user-generated).

Everything here is a **decision** with a **recommendation**, **alternatives considered** (at least three per decision), **rejected alternatives with reasons**, and a **cost-to-run** figure. Where the workstream ADRs diverge from the summary, this document is the authoritative integrated view.

**Out of scope:** this document does not re-derive the filtering engine's scoring math, the ingest pipeline's implementation, the geo search's correctness proofs, or the deployment shell — those are in the individual workstream ADRs. It records the decisions that bind them together.

---

## 1. Decision summary (TL;DR)

| Layer | Choice | Cost to run (MVP) |
|---|---|---|
| Product shape | **Web-first**, PWA-capable responsive web app; no native apps on day one | — |
| Hosting | **Fly.io**, one Docker container, smallest machine | ~$2–6/mo (free allowance covers it) |
| Frontend | **Next.js (App Router) + React** | npm (free) |
| Backend runtime | **Node.js 22 LTS** | npm (free) |
| Backend / API | **Next.js route handlers** (`/api/v1/recommend`) | Bundled with Next.js |
| Data store | **SQLite** (one file, WAL) via **better-sqlite3** catalog adapter | $0 |
| Test runner | **Vitest** | npm (free) |
| Deploy | **Docker + Fly.io** (`docker build` → `fly launch` → `fly deploy`) | Free allowance → ~$2–6/mo |
| Weather | **Open-Meteo** (free, no key, materialized into catalog at ingest) | $0 |
| Geo search | **Geohash grid + prefix-range query + exact haversine filter**; client → Nominatim → IP → seeded-default-region fallback chain | Local math only (zero external calls for core path) |
| Recommendation engine | **Two-tier**: hard-gate filter → soft-score → rank | $0 (pure local math) |
| Data ingestion | **Curated core** (primary) + **best-effort free-tier enrichment** + **moderated user-generated** (deferred) | $0 staff time (curated seed) + free-tier APIs (best-effort only) |
| Failure handling | **Degrade ladder** (full / partial / sparse / empty) with never-fabricate rule | $0 |

**Cost ceiling (MVP): ~$0–$10/mo** — one container (~$2–6) + SQLite (free) + Open-Meteo (free). No managed DB, no paid API key, no app-store fees. Covered by Fly.io's free allowance.

---

## 2. Major decisions and alternatives

### 2.1 Product direction & hosting: web-first on Fly.io

**Recommendation:** Ship **web-first** (responsive, mobile-friendly web app with a PWA shell) and host it on **Fly.io as a single Docker container** starting on Fly.io's cheapest machine, migrating to any other container host by re-tagging the image.

#### Alternatives considered

| # | Alternative | Verdict | Why rejected |
|---|---|---|---|
| 1 | **Native iOS/Android app first** | ❌ | App-store fees (~$99/yr, ~$25 one-time), review latency, two codebases; the discovery/search demand is web-native and cannot be shared as a URL. |
| 2 | **PWA-only with no app shell** | ❌ | We will still include the "Add to Home Screen" PWA shell — it's free and gives the mobile app feel; this is not an alternative. |
| 3 | **Serverless-first (Vercel/Netlify)** | ❌ | Locks the backend into functions/platform console; the engine + hourly caching are awkward in serverless; harder to move. Contradicts "easy movement". |
| 4 | **Heroku** | ❌ | Free tier is gone; heavier platform; less portable than Fly.io. |
| 5 | **Managed Postgres on day one** | ❌ | Billable, hard-to-move dependency before we have data volume to justify it. SQLite now → Postgres later. |
| 6 | **Build a mobile app + web in parallel** | ❌ | Wasted budget; one product, one deploy, one surface. Add a client (web, then app) later. |
| 7 | **NWS as the only weather source** | ❌ | Open-Meteo is strictly easier to stand up (no key, no signup) for a first version; NWS is overkill. |

**Homeland rationale:** The demand is search-led (`"what should we do near Ottawa when it rains today"`). Users arrive via Google, share results via a link, may or may not have an app. Zero install removes the biggest barrier for a team with no budget. Search engines index the web app, and the result is a **shareable URL** (`thingztodo.app/?lat=...&lng=...&weather=no_rain&budget=...`) — the MVP's killer differentiator. A PWA (manifest + service worker + Web Push) gives the mobile "app feel" without app stores.

**What this costs to run:** One container on Fly.io's cheapest machine ≈ **$2–6/mo** (published), fully covered by Fly.io's free allowance for low-volume side projects (3 shared-cpu-1x VMs, 1 GB managed Postgres, 160 GB outbound/month). No app-store fees, no managed-DB cost, no platform console.

---

### 2.2 Frontend: Next.js (App Router) + React

**Recommendation:** **Next.js App Router + React** is the frontend framework. It is server-rendered (the ranked list is the value moment), ships native shareable/indexable URLs, keeps UI + API in one framework/process, and ships a built-in PWA shell.

#### Alternatives considered

| # | Alternative | Verdict | Why rejected |
|---|---|---|---|
| 1 | **Vite SPA + separate Express/Fastify backend** | ❌ | Duplicate UI+server surface; slow first paint on the value moment; two deploy targets; later moved anyway. |
| 2 | **Next.js on Vercel** | ❌ | Locks the backend into serverless functions and a platform console; contradicts "easy movement + one container + Fly.io". |
| 3 | **Node.js + Express standalone + React/Vite SPA** | ❌ | Same duplication as the Vite+Express case; two servers to run, log, and move. |
| 4 | **Fastify backend** | ❌ | Fine, but for a thin route-over-engine API there is nothing it does that Next.js route handlers do not; adds a dependency and mental model for marginal gain. |
| 5 | **Python (FastAPI) backend** | ❌ | The engine and UI are TypeScript on purpose (single language contract, shared types). Adds a second runtime, test toolchain, and way to move the stack. |
| 6 | **Ruby / Rails** | ❌ | Second runtime + opinionated conventions we'd fight in this early, small team. Same "two runtimes" cost as Python. |
| 7 | **Go backend** | ❌ | Higher learning curve for the team, not worth the marginal perf gain for a thin route-over-engine API. Node's non-blocking I/O is adequate. |
| 8 | **Rust / Deno / Bun** | ❌ | "Clever and fast" but not well-understood or as easy to move/maintain for a no-budget, tiny team. |

**Cost:** npm (free); the Next.js framework is a dependency in `package.json`, no licensing cost.

---

### 2.3 Backend: Node.js 22 LTS + Next.js route handlers

**Recommendation:** **Node.js 22 LTS** running Next.js, with the recommendation API served by **Next.js route handlers** in the same process as the UI. The engine is a **framework-agnostic pure TS module** — it knows nothing about HTTP, Express, or Fastify.

#### Alternatives considered

| # | Alternative | Verdict | Why rejected |
|---|---|---|---|
| 1 | **Node.js + Express standalone backend** | ❌ | Separate process, separate port, separate deploy; duplicates what Next.js route handlers do in-process. |
| 2 | **Node.js + Fastify** | ❌ | Marginally better perf for a thin route API; adds a dependency and mental model; Next.js collapses the framework into one. |
| 3 | **Python (FastAPI) backend** | ❌ | Second runtime + second test toolchain; contradicts single-language contract with the engine. |
| 4 | **Ruby / Rails backend** | ❌ | Second runtime; opinionated conventions we'd fight in early days. |
| 5 | **Go backend** | ❌ | Higher learning curve; not worth the marginal perf gain for a thin route-over-engine API. |
| 6 | **Serverless functions (Vercel/Netlify)** | ❌ | Cold starts, platform console, locked to one host; the engine is per-request compute-and-lookup, not a bursty function workload. |

**Cost:** npm (free); Node.js 22 LTS is free and already present in the environment (`node v22.19.0`).

**Why the engine is decoupled:** The API route is a thin shell — normalize → validate → catalog lookup → weather cache → engine → emit envelope. The engine reads `WeatherState` materialized in the cache and speaks only a pure-TS interface. That boundary is what makes the backend a shell and the engine testable deterministically.

---

### 2.4 Data store: SQLite (file, WAL) via better-sqlite3

**Recommendation:** **SQLite**, one file, accessed through a thin **node catalog adapter** (`better-sqlite3`, in-process, synchronous, prebuilt). Migrated to managed **Postgres** later behind the same `CatalogStore` interface.

#### Alternatives considered

| # | Alternative | Verdict | Why rejected |
|---|---|---|---|
| 1 | **Managed Postgres on day one** | ❌ | Billable, hard-to-move dependency before we have data volume. SQLite now, Postgres later. |
| 2 | **DynamoDB / NoSQL** | ❌ | No natural fit for the catalog (a small, indexed, versioned dataset) and no schema-drift recovery story. |
| 3 | **JSON files as primary store** | ❌ | The catalog is versioned snapshots, not the live store; live writes need atomicity/concurrency control JSON can't give cleanly in Node. |
| 4 | **Offline-first local DB (PouchDB/IndexedDB)** | ❌ | Not the MVP's access pattern (search-led, server-verified, shareable results). Could be a later *enhancement*. |
| 5 | **Managed DB of any kind (Fly Postgres, Neon, Supabase)** | ❌ | See managed Postgres; the MVP does not need it. |

**Cost:** $0 — SQLite is a file on the container; no managed-DB ops, no credentials to rotate, no connection-pool/async complexity. `better-sqlite3` is a prebuilt npm package.

**Migration cost (SQLite → Postgres):** Flip one line to switch the `CatalogStore` implementation; the engine and API are untouched. The catalog interface (`CatalogStore`) defines `getActivities`, `getActivity`, `queryByArea`, `upsertMany`, `getWeatherCache`, `upsertWeatherCache`, `listSnapshots`, `pickLatest`.

---

### 2.5 Geo search: geohash + prefix-range + haversine + fallback chain

**Recommendation:** Index locations with a **geohash grid**, query the **prefix range** at a precision chosen from the requested radius, then apply an **exact haversine filter** over the candidate set. Position resolution is a **client → Nominatim → IP → seeded-default-region** fallback chain. The **core search is pure local math over a cached catalog snapshot** — zero external API calls.

#### Alternatives considered

| # | Alternative | Verdict | Why rejected |
|---|---|---|---|
| 1 | **PostGIS / dedicated spatial DB** | ❌ | Pushes the catalog onto a heavier, more expensive platform with a harder migration path. Geohash prefix index already gives an index-backed superset on SQLite; PostGIS is the escape hatch when the MVP grows. |
| 2 | **Mapbox / Google Places / geocoder-API geocoding** | ❌ | Paid (key + quota) and rate-limited; a no-budget product cannot carry the cost of a second API key + billing for a best-effort geocoder. Nominatim is free, no key. |
| 3 | **Client-side-only filtering (no server geo search)** | ❌ | Pushes the whole (growing) catalog to every client, breaking the "small, cheap footprint" goal, duplicating the index logic, and splitting search logic across client + server. The server owns the index. |
| 4 | **Provider-feed "near me"** | ❌ | Tightly couples geo search to a single external data source; providers are flaky and don't reliably cover the user's own position. Kept in the engine ADR §2 as an *optional* area-finder per source, not as the geo layer. |
| 5 | **Leaflet/Mapbox geocoder for the "from" position** | ❌ | Same as the geocoder tier — only a frontend for input resolution, not a search primitive. |
| 6 | **Specialist "find near me" iframe/widget** | ❌ | Third-party widgets add a privacy/weight cost and a hard dependency on an external widget's uptime for the core function. We own the search. |

**What this costs to run:**
- **Core search path:** zero external API calls. Pure server-side math (geohash prefix-range SQLite query + haversine filter) over a cached catalog snapshot. No key, no quota, no rate limit.
- **Geocoding (Nominatim):** free, no key, 1 req/s policy; cached for ~1 h; best-effort and heavily rate-limited by design.
- **IP geolocation:** free/cheap, best-effort, cached per IP (~10 min TTL).
- **Storage:** the `geohash` string is materialized at ingest (ingestion ADR §10). No extra table needed for MVP.
- The only *external* calls an end-user query makes are none for the core path; geocoding, if used, is best-effort and cached.

**Failure cost:** when Nominatim is down/rate-limited, the search still returns results anchored to the default region (Ottawa–Gatineau pilot); the degrade envelope explains what happened (`location_unavailable`, `location_out_of_service_area`).

---

### 2.6 Recommendation / filtering engine: two-tier hard-gate + soft-score

**Recommendation:** The engine is **two-tier**: (1) **Tier 1 — hard gating** excludes candidates that fail mandatory constraints (cost/budget, time open/overlap, distance radius, mandatory weather `avoid_*` rules) *before* scoring; (2) **Tier 2 — soft scoring** computes a 0–100 score from weighted sub-scores and ranks. **Never fabricate** results; degrade ladder (full / partial / sparse / empty) with a structured degrade envelope.

#### Alternatives considered

| # | Alternative | Verdict | Why rejected |
|---|---|---|---|
| 1 | **One weighted score for everything** | ❌ | Produces nonsense (an expensive thing ranks high for a $5 family with no budget headroom); to fix that you still need hard budget and distance gates — so you'd have gates anyway; conflates "must have" with "nice to have". |
| 2 | **Filters only (hard gates, no scoring)** | ❌ | "Fastest to the right answer among many eligible" — ranking matters, not just eligibility. |
| 3 | **Soft scoring only (no hard gates)** | ❌ | A $99.99 item under a $10 budget has no business being ranked #1; the product would be a joke. |
| 4 | **Client-side-only ranking** | ❌ | Pushes the whole catalog to every client; breaks the small-footprint goal; splits scoring across client + server. |

**What this costs to run:** **zero external calls** at query time. The engine is pure local math over the frozen per-request catalog snapshot. No API keys, no quotas, no rate limits. The cost is CPU — bounded by the candidate set (geohash-supplied) rather than the full catalog. A few thousand activities is a sub-millisecond in-process operation.

**Cost to run (engine):** in-process, no network, no key, no quota, no rate-limit risk. The degrade ladder costs nothing but a structured envelope (mode + freshness + reasons + fallbacks + warnings) — fields already in the `RecommendationResult`.

---

### 2.7 Data ingestion source strategy: curated core + best-effort enrichment + moderated user-generated

**Recommendation:** The catalog is a **curated core** (team-verified seed, highest confidence, $0 for the team, smallest real thing) **plus best-effort free-tier enrichment** (free-tier public/municipal APIs, never a dependency) **plus moderated user-generated** (deferred behind a submission flow, tagged `confidence=user_generated`, inflow throttled). **No scraping-only and no licensed-only** as a first-release dependency.

#### Alternatives considered

| # | Alternative | Verdict | Why rejected |
|---|---|---|---|
| 1 | **Scraped-only** | ❌ | Brittle selectors (layouts change, pages die, rate limits), inverted maintenance (scales with number of sites, not activities), legal/ToS risk, silent rate-limit degradation, no schema contract. |
| 2 | **Licensed-only** | ❌ | Kills the no-budget constraint — nothing ships until a paid account exists; expensive startup cost; geography gaps for pilot areas. |
| 3 | **Curated-only (no enrichment)** | ❌ | Bounded by team effort; the floor of "no results" UX is small; does not teach the ingest pipeline's failure handling; too narrow for the "many options" promise. (Accepted as the *primary core*, but not as the *only* source.) |
| 4 | **User-generated-only** | ❌ | Quality risk (outdated hours, fake venues, spam) + moderation cost; no floor of verified data to anchor it. |

**What this costs to run:**
- **Curated seed (Phase 0):** staff time only, $0 direct cost. ~10–30 local activities. High per-record effort, but bounded surface area.
- **Free-tier provider enrichment (Phase 1):** free-tier public/municipal APIs (events, recreation, open data) — e.g., findlocal.net free 1,000-calls/month tier; municipal open-data pages; Canada's ODRSF. No key to lift.
- **Licensing:** re-evaluated in Phase 4 ("geography gaps became painful") — never a first-release dependency. Licensed data is genuinely expensive (Databento from $750/firm/mo, Nasdaq Basic $1,680/firm/mo) — cost skips the no-budget constraint.
- **Handling failures:** parallel per-source fetch with timeouts; retry with backoff + jitter on idempotent GETs; Retry-After courtesy on 429; circuit breaker after N consecutive failures; idempotent upsert dedup on stable provider+slug ids; stale-while-revalidate cache with per-record `data_freshness`. No fabricated data from an unreachable source.

**Cost to run (ingestion):** no paid APIs in the data path; free-tier enrichment is best-effort and cached; failures shrink results (never fabricate) and travel in the degrade envelope so the user always sees *why*.

---

## 3. What this costs to run (explicit cost section)

### 3.1 Upfront / zero-cost items

| Item | Cost | Notes |
|---|---|---|
| Node.js 22 LTS + npm | $0 | Already present in the environment (v22.19.0 / npm 10.9.3) |
| Next.js + React | $0 | Open-source npm packages |
| SQLite + better-sqlite3 | $0 | File-based; zero managed-DB ops, no credentials |
| Vitest | $0 | npm package |
| Docker | $0 (local dev) | `docker build` is the deployable; builds locally |
| GitHub Actions (CI) | $0 | Free tier covers the small build matrix |
| Open-Meteo weather | $0 | Free, no key, hourly; 10k calls/day non-commercial; materialized into catalog at ingest |
| Nominatim geocoder | $0 | Free, no key, 1 req/s policy; heavily cached |
| IP geolocation | $0 | Free/cheap, cached per IP (~10 min) |
| Logging / monitoring | $0 | Structured logs from the single container; noAPM. No paid uptime/alert runner in MVP. |

### 3.2 Ongoing cost (MVP, first months)

| Item | Cost | Notes |
|---|---|---|
| Fly.io container (smallest machine) | ~$2–6/mo | Published pricing; fully covered by Fly.io's free allowance (3 shared-cpu-1x VMs, 1 GB managed Postgres, 160 GB outbound/month) |
| SQLite | $0 | Single file, backed up by copying the file |
| Open-Meteo | $0 | Materialized into the catalog at ingest; *query time* is ~free |
| Nominatim / IP geolocation | $0 | Best-effort, cached; never on the core search path |
| No app-store fees | $0 | Web-first; no iOS/Android deploy on day one |
| No managed DB | $0 | SQLite file; Postgres migration is an internal refactor (see §5); no credential to rotate |
| No paid API key | $0 | Weather + geo are free; enrichment is best-effort free-tier |

**Total MVP cost ceiling: ~$0–$10/mo**, covered by Fly.io's free allowance with **no payment required at all**.

### 3.3 Cost scaling factors (what makes it expensive later)

| Factor | Cost when triggered | Notes |
|---|---|---|
| Managed Postgres (future) | ~$5–20/mo | Internal refactor behind `CatalogStore`; no rewrite |
| Paid weather provider (future) | ~$50–200/mo | Open-Meteo → NWS/commercial; one config change |
| Paid geocoder/vendor (future) | ~$100–500/mo | Nominatim → commercial; one config change |
| Native mobile clients (future) | ~$0 + dev time | New clients over the same API |
| High query volume | Mild (container scaling) | Fly.io's cheapest machine handles thousands of requests/day at MVP volume |

### 3.4 Summary

> **The MVP is deliberately money-free to run.** One container (~$2–6/mo) + SQLite (free) + Open-Meteo (free) + free best-effort enrichment (free-tier APIs) + local math for geo search and the engine (zero external calls). No managed database, no paid API key, no app-store fees. Fly.io's free allowance covers the container and outbound traffic. **Total: ~$0–$10/mo.**

---

## 4. Consolidated data model

The data model is the schema contract between the catalog, the ingest pipeline, the engine, and the API. It is the union of the workstream ADRs (filtering engine §3, ingestion §8, geo search §3.4).

### 4.1 Core entities

| Entity | Key fields | Purpose |
|---|---|---|
| `Activity` | `id`, `slug`, `category`, `subcategory`, `outdoor`/`indoor`/`mixed`, `description`, `location` (lat/lng), `bounds` (optional), `geohash`, `address`, `price`, `price_class` (free/cheap/moderate/premium/splurge), `party_size` (min/max/capacity), `party_suitable` (solo/pair/family/group), `hours`, `season`, `availability_rules`, `metadata`, `confidence` (curated/verified/inferred/user_generated) | The recommended thing |
| `ActivityInstance` | `activity_id`, `starts_at`, `ends_at`, `available_seats` (0 = sold out), `venue_id`, `created_at`, `updated_at`, `source` | Time-specific availability; time-of-day and "open now" checks |
| `WeatherState` | `lat`, `lng`, `observed_at`, `fetch_at`, `source`, `temperature_c`, `temperature_feels_like_c`, `precip_probability`, `precip_type`, `precip_amount_mm`, `conditions`, `wind_kph`, `humidity_pct`, `uv_index`, `confidence`, `staleness_seconds`, `coverage` | External weather, per area + time; materialized into the catalog cache at ingest |
| `UserRequest` | `request_id`, `user_lat`, `user_lng`, `timezone`, `radius_km`, `weather` (rule set), `cost` (max budget + preferred classes), `party_size` band, `time` (window + time-of-day bands), `intent`, `rank_weights`, `preferred_place_ids`, `fallback_priority` | Normalized incoming query; constraints vector |
| `RecommendationResult` | `rank`, `activity_id`, `score` (0–100), `matched` (constraints satisfied), `unmet` (constraints not satisfied), `reasons`, `score_breakdown` (per-dimension sub-scores), `distance_km`, `distance_class` (near/moderate/far/too_far), `weather_state_ref`, `confidence` (engine's confidence) | Engine output per ranked activity |
| `DegradeEnvelope` | `mode` (full/partial/sparse/empty), `data_freshness` (per-source {name, fresh, stale, missing}), `reasons`, `fallbacks_used`, `warnings` | Structured failure report; travels with every response |

### 4.2 Provenance fields (catalog record)

| Field | Type | Purpose |
|---|---|---|
| `id` | string | Stable primary key (`provider` + `slug`); dedup across sources |
| `confidence` | `curated \| verified \| inferred \| user_generated` | Provenance + vouch level |
| `source` | string | Provider/feed name; null for curated |
| `source_data` | object | Raw source payload (kept untouched in `metadata`) |
| `verified_by` | string[] | Team members who vouched (curated only) |

### 4.3 Index

| Index | Column | Purpose |
|---|---|---|
| B-tree on `geohash` | `Activity.geohash` | Prefix-range query for geo search (supperset guarantee) |
| B-tree on `price_class` | `Activity.price_class` | Cost soft-scorer lookup |
| B-tree on `party_suitable` | `Activity.party_suitable` | Party-size eligibility |
| B-tree on `category`/`subcategory` | `Activity.category`, `Activity.subcategory` | Intent matching |

**Storage cost:** SQLite is one or a few files. The catalog grows with the number of activities (not the number of users). A pilot of ~10–30 curated activities is essentially zero storage.

---

## 5. Recommendation API surface

The API is the single coherent recommendation surface. The engine + UI are one process; a future native mobile client is a *new client* over the same API.

### 5.1 `GET /api/v1/recommend`

Request body (normalized constraint vector):

```json
{
  "request_id": "uuid",
  "user_lat": 45.42,
  "user_lng": -75.70,
  "timezone": "America/Quebec",
  "radius_km": 10,
  "weather": { "keep": false, "avoid_rain": true, "avoid_snow": false },
  "cost": { "max_budget": 20, "preferred_classes": ["free", "cheap"] },
  "party_size": "pair",
  "time": { "bands": ["evening"], "window": { "starts_at": "...", "ends_at": "..." } },
  "intent": "outdoor",
  "rank_weights": { "w_weather": 0.2, "w_cost": 0.15, "w_party": 0.1, "w_time": 0.15, "w_dist": 0.15, "w_intent": 0.15, "w_seats": 0.05, "w_recent": 0.05 },
  "fallback_priority": ["curated", "indoor"]
}
```

Response:

```json
{
  "recommendation": {
    "results": [
      {
        "rank": 1,
        "activity_id": "provider+slug",
        "score": 87.4,
        "matched": ["weather", "cost", "party_size", "time", "distance"],
        "unmet": [],
        "reasons": ["free entry", "within 2 km", "indoor, rain-safe"],
        "score_breakdown": { "weather": 0.95, "cost": 1.0, "party": 1.0, "time": 0.9, "distance": 0.85, "intent": 0.9, "seats": 1.0, "recent": 0.8 },
        "distance_km": 1.2,
        "distance_class": "near",
        "confidence": 0.95
      }
    ],
    "degrade": {
      "mode": "full",
      "data_freshness": { "weather": { "source": "open-meteo", "fresh": true }, "catalog": { "sources_down": [] } },
      "reasons": [],
      "fallbacks_used": [],
      "warnings": []
    }
  }
}
```

The degrade envelope carries everything the product needs to render "why" and "what to do next" for every response, not just failures. `mode` is one of `full | partial | sparse | empty`.

---

## 6. Alternatives rejected (integrated summary)

This section consolidates the rejected alternatives across all major decisions (§2). Each decision is tabulated here for one-place reference.

| Decision | Rejected alternative | Rejected because |
|---|---|---|
| Product & hosting | Native iOS/Android app first | Fees, review latency, two codebases; discovery is web-native |
| Product & hosting | Serverless-first (Vercel/Netlify) | Platform lock-in; engine/hourly caching awkward in serverless |
| Product & hosting | Heroku | Free tier gone; heavier platform |
| Product & hosting | Managed Postgres on day one | Billable, hard-to-move dependency before data volume justifies it |
| Product & hosting | Mobile app + web in parallel | Wasted budget; one product, one deploy |
| Product & hosting | NWS as only weather source | Open-Meteo is easier (no key) for a first version |
| Frontend | Vite SPA + separate Express backend | Duplicate surface; slow first paint; two deploys |
| Frontend | Next.js on Vercel | Platform lock-in; contradicts Fly.io + one container |
| Frontend | Node + Express standalone | Two servers to run/log/move |
| Frontend | Fastify | Marginally better perf; adds dependency and mental model |
| Frontend | Python (FastAPI) backend | Second runtime; contradicts single-language contract |
| Frontend | Ruby/Rails | Second runtime; opinionated conventions |
| Frontend | Go backend | Higher learning curve; not worth marginal perf gain |
| Frontend | Rust/Deno/Bun | Not well-understood; not easy to move for tiny team |
| Data store | Managed Postgres day one | Billable; hard-to-move before data volume justifies it |
| Data store | DynamoDB/NoSQL | No natural fit for small indexed versioned catalog |
| Data store | JSON files as primary store | No atomicity/concurrency control for live writes |
| Data store | Offline-first local DB | Wrong access pattern for MVP |
| Data store | Managed DB of any kind | MVP does not need it |
| Geo search | PostGIS | Heavier, more expensive migration path |
| Geo search | Mapbox/Google Places/geo APIs | Paid; hard for a no-budget best-effort geocoder |
| Geo search | Client-side-only filtering | Pushes catalog to every client; breaks small footprint |
| Geo search | Provider-feed "near me" | Couples geo to one flaky external source |
| Geo search | Leaflet/Mapbox geocoder | Only a frontend; not a search primitive |
| Geo search | Specialist "find near me" iframe | Privacy/weight; hard dependency on third-party uptime |
| Engine | One weighted score for everything | Produces nonsense; masks "must have" vs "nice to have" |
| Engine | Filters only (no scoring) | Ranking matters, not just eligibility |
| Engine | Soft scoring only (no hard gates) | A $99.99 item under a $10 budget would rank #1 |
| Ingestion | Scraped-only | Brittle selectors; inverted maintenance; legal/ToS risk; no schema contract |
| Ingestion | Licensed-only | Kills no-budget constraint; nothing ships until paid; geography gaps |
| Ingestion | User-generated-only | Quality risk + moderation cost; no verified floor |

---

## 7. Verification & proof

A decision is not done until it *runs*. Per the workstream ADRs:

1. **Toolchain availability** — `node -v` → v22.19.0; `npm -v` → 10.9.3; `sqlite3 --version` → 3.54.0; `git --version` → 2.54.0. All verified.
2. **Stack install** — `npm i next react react-dom --no-audit --no-fund` completed with clean resolution; `node_modules/.bin/next` present.
3. **Geo search invariants** — `verify_geo_search.py` 5/5 checks pass on synthetic data (geohash round-trip, superset guarantee, exact == brute force across radii, cell-size monotonic, missing-location degradation). Exit code 0. (ADR `2026-10-21-geo-search-approach.md` §9)
4. **Ingestion strategy** — ADR `2026-10-21-activity-catalog-ingestion-source-strategy.md` defines a synthetic-dataset verification plan: happy path, partial failure, circuit breaker, idempotency, schema drift, degrade ladder.
5. **Filtering engine** — ADR `2026-10-21-activity-filtering-engine-constraints-matching.md` §13 defines test suites: gating, scoring, degrade, determinism, plus per-constraint cases.
6. **Running app** — the first engineering ticket ("scaffold the product") is the acceptance bar that end-to-end verification is left to.

The current state: none of the four "runs" items (1–4) have produced a committed, running app. The `app/` repo does not exist yet. This ADR is the architecture record for that first ticket.

---

## 8. Standing decisions

- **Product shape:** web-first (responsive, mobile-friendly web app + PWA shell); no native apps on day one.
- **Hosting:** Fly.io, one Docker container, cheapest machine; migration via re-tag/push/run.
- **Frontend:** Next.js (App Router) + React.
- **Backend:** Node.js 22 LTS; Next.js route handlers; engine is a pure-TS, framework-agnostic module.
- **Data store:** SQLite (file, WAL) via better-sqlite3; `CatalogStore` interface; migrate to managed Postgres later.
- **Weather:** Open-Meteo (free, no key), materialized into the catalog at ingest.
- **Geo search:** geohash + prefix-range + haversine; client → Nominatim → IP → seeded-default-region fallback chain.
- **Recommendation engine:** two-tier hard-gate + soft-score; never-fabricate; degrade ladder.
- **Ingestion:** curated core + best-effort free-tier enrichment + moderated user-generated.
- **Failure handling:** degrade ladder (full/partial/sparse/empty); every external service is best-effort; no fabricated results.
- **Auth/identity:** none for MVP — kill the target, not the scope.

---

## 9. Open items (for later cards)

1. **Catalog seed (Phase 0):** team-verified ~10–30 local activities for the pilot area (Ottawa–Gatineau per the charter).
2. **Free-tier provider integration (Phase 1):** which free-tier public/municipal APIs to use (weather, events, recreation). NWS for weather is a strong candidate for the pilot area but requires Eric's geography call.
3. **Node driver final choice:** commit to better-sqlite3; keep `node:sqlite` (experimental) as a zero-native-build fallback; revisit at catalog seeding.
4. **CI pipeline:** GitHub Actions wiring + the first build that pushes to Fly.io.
5. **PWA shell details:** manifest, service worker, push subscription — fold into the same deploy.
6. **Outbound email path:** blocked — no SMTP credentials; see ADR `2026-10-21-outbound-email-path-readiness.md` (needs Eric's SMTP account; the email-alternate-and-discord is the interim path).
7. **WhatsApp:** requires Eric to message the bot first or a Twilio account (RUNBOOK §5) — not available today.
8. **Geo precision tuning (`p_min`/`p_max`) and cached TTLs:** measured once we have real query volume.
9. **PostGIS escape hatch:** decided when the catalog migrates from SQLite.
10. **Scraping policy (ToS/legal):** revisited before Phase 4.
11. **Multi-provider weighting for the catalog:** currently assumed single provider + curated.

---

*Design by Forge (Principal Software Architect), 2026-10-21. Maintenance owner for this document: Forge. All cost figures verified from published vendor pages on 2026-10-21 (Fly.io pricing, Open-Meteo pricing, Databento/Nasdaq pricing).*
