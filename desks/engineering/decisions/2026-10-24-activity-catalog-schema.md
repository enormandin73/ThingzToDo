# Design — Canonical Activity Catalog Record (data structure)

**ADR:** `2026-10-24-activity-catalog-schema.md`
**Owner:** Forge (Principal Software Architect, ThingzToDo)
**Date:** 2026-10-24
**Status:** Accepted design — the data contract for discovery/enrichment agents and the
ranking engine. Read together with:
- `2026-10-21-activity-filtering-engine-constraints-matching.md` (the engine ADR it amends)
- `2026-10-21-activity-catalog-ingestion-source-strategy.md` (the ingest ADR it backs)
- `2026-10-24-activity-data-pipeline-and-ranking-2026-10-24.md` (Scout's pipeline + ranking contract)

---

## 0. Purpose & scope

Eric's framing (2026-10-24): a site has value only with a **critical mass of well-researched
listings**, **continuous scraper agents**, and a **second team of enrichment agents** that
fills hours, weather dependency, cost, group size, Google Reviews, TripAdvisor Reviews —
and those signals must influence ranking.

This card produces the **canonical listing record** — the data structure the discovery agents
produce, the enrichment agents fill, and the ranking engine consumes. It covers:

1. The canonical record: every field, its type, nullability, units, provenance, and verification.
2. The relationship model: categories/aliases, chains vs independents, seasonal variants,
   event vs evergreen, and the business↔"thingz" relationship (a museum is a venue *and* an activity).
3. The ranking mapping: hard gates vs soft scores, with weights/thresholds written **against**
   the engine ADR, plus the exact ADR amendments required.
4. Storage & versioning: the SQLite schema, and snapshotting that keeps the engine's
   deterministic-scoring model valid.
5. The ingestion contract: discovery output, enrichment output, dedupe keys, conflict
   resolution, staleness/refresh, and how `confidence` is computed.
6. The art of the possible: what is reliably extractable at scale, what needs a human, what
   stays unverified.

This is joint work with Scout (orchestrator Irock). Where his design is over-optimistic,
it is flagged **plainly** in §8 and carried into the cost reconciliation in §9.

---

## 1. Canonical record — field-by-field

Every field below is a column in the `activities` table (§6 DDL). "Level" is the v2
materialization tier of that field in the engine query path (see §7). Short fields are stored
as a single column; structured/nestable fields are stored as JSON text (SQLite has no JSONB;
the app uses the JSON1 functions where available).

### 1.1 Identity & provenance

| Field | Type | Nullability | Units / format | Provenance | How verified |
|---|---|---|---|---|---|
| `id` | `TEXT` | NOT NULL | `${provider}:${normalized_slug}` e.g. `curated:CityGardenMarket` | ingest | deterministic; collision-free within a provider because slug is normalized (lowercase, ascii-folded, dashes) |
| `provider` | `TEXT` | NOT NULL | class: `curated`,`osm`,`city`,`eventbrite`,`user` | ingest | source-class registry; drives base `confidence` + refresh TTL |
| `confidence` | `TEXT` | NOT NULL | `curated`\|`verified`\|`inferred`\|`user_generated` | ingest/Warden | provenance enum; overridden by `confidence_fields` completeness |
| `confidence_score` | `REAL` | NOT NULL | 0.0–1.0 | Warden | §7.4 formula; never 0.0 for a shipped row |
| `confidence_fields` | `TEXT` | NOT NULL | JSON `{field: stamp}` | ingest/Warden | per-field `verified`\|`inferred`\|`user_generated`\|`unverified` |
| `source` | `TEXT` | NOT NULL | JSON array of contributing source names | ingest | dedup/merge at Warden |
| `raw_payload` | `TEXT` | NOT NULL | untouched original source JSON | ingest | audit + drift recovery |
| `metadata` | `TEXT` | NOT NULL | JSON free-form | ingest | contact, notes, capacity notes, venue link |

### 1.2 Presentation

| Field | Type | Nullability | Units / format | Provenance | How verified |
|---|---|---|---|---|---|
| `name` | `TEXT` | NOT NULL | display string | ingest | curated/verified; never scraped |
| `description` | `TEXT` | nullable | short paragraph | ingest/LLM | LLM-derived flagged `estimated`, never a gate |
| `aliases` | `TEXT` | nullable | JSON array of alternate names | ingest | `activity_alias` table feeds FTS |

### 1.3 Classification

| Field | Type | Nullability | Units / format | Provenance | How verified |
|---|---|---|---|---|---|
| `category` | `TEXT` | NOT NULL | FK to `activity_category.name` | ingest/LLM | curated/verified; `category_note` records method |
| `subcategory` | `TEXT` | nullable | fine-grained | ingest/LLM | LLM-inferred → `inferred` |
| `category_note` | `TEXT` | nullable | "curated" / "LLM-inferred" / "osm-inferred" | ingest | provenance stamp, never silent |

### 1.4 Location

| Field | Type | Nullability | Units | Provenance | How verified |
|---|---|---|---|---|---|
| `venue_lat` | `REAL` | nullable | decimal degrees, WGS84 | OSM / geocoding | centroid of venue polygon |
| `venue_lng` | `REAL` | nullable | decimal degrees, WGS84 | OSM / geocoding | centroid of venue polygon |
| `address` | `TEXT` | nullable | display string | curated/verified | match venue site + OSM |
| `postal_code` | `TEXT` | nullable | AL·PS (CA) / postal | curated/verified | geocoding fallback |

### 1.5 Contact & media

| Field | Type | Nullability | Units / format | Provenance | How verified |
|---|---|---|---|---|---|
| `phone` | `TEXT` | nullable | E.164 | venue site | phone-issued match or curated |
| `website_url` | `TEXT` | nullable | URL | venue site | verified fetch |
| `booking_url` | `TEXT` | nullable | URL | venue site / user | verified fetch |
| `photos` | `TEXT` | nullable | JSON array of absolute URLs | official venue assets only; **never** scraped from review platforms | curated/verified |

### 1.6 Cost

| Field | Type | Nullability | Units | Provenance | How verified |
|---|---|---|---|---|---|
| `cost_currency` | `TEXT` | NOT NULL | ISO 4217, default `CAD` | ingest | recorded at ingest |
| `cost_min` | `REAL` | nullable | CAD (float) | web + LLM | `null` when undisclosed |
| `cost_max` | `REAL` | nullable | CAD (float) | web + LLM | `null` when undisclosed |
| `cost_known` | `INTEGER` | NOT NULL | boolean (0/1) | ingest | price disclosed at all? |
| `cost_class` | `TEXT` | nullable | `free`\|`cheap`\|`moderate`\|`premium`\|`splurge` | derived at ingest | from `cost_min/max` |

### 1.7 Party

| Field | Type | Nullability | Units | Provenance | How verified |
|---|---|---|---|---|---|
| `party_min` | `INTEGER` | nullable | people | web + LLM | — |
| `party_max` | `INTEGER` | nullable | people | web + LLM | **hard gate** uses `party_max` (engine §5.3) |
| `party_suitable` | `TEXT` | nullable | comma-joined `solo,pair,family,group` | web + LLM | — |

*(`capacity` as a separate field is dropped; `party_max` is the single, unambiguous hard-gate
field, de-duplicating the two symbols used by the engine ADR. See §7.2.)*

### 1.8 Operating state (the heart of Eric's list)

| Field | Type | Nullability | Units | Provenance | How verified |
|---|---|---|---|---|---|
| `hours_json` | `TEXT` | NOT NULL | JSON `{opens, closes, timezone, repeat, holiday_closures, notes}` | web + LLM + venue link | **24h**; re-verify nights; a `holiday_closure` marks an open day closed |
| `season_json` | `TEXT` | NOT NULL | JSON `{enabled_from, enabled_to, is_open_utc}` | curated/LLM | `season_closed` derived at ingest |
| `weather_dependency` | `TEXT` | NOT NULL | `indoor`\|`outdoor`\|`rain-safe-outdoor`\|`heat-safe-outdoor`\|`partial`\|`not-verifiable` | web + LLM | per-listing research (Adept); **24h** or on weather shift |
| `weather_sensitivity` | `TEXT` | nullable | JSON `{heat_c, cold_c, rain_note, snow_note}` | web + LLM | `null` until verified |
| `last_verified` | `TEXT` | NOT NULL | timestamp (ISO 8601 UTC) | Warden | when a human/agent vouched; drives accept/reject |
| `last_refreshed` | `TEXT` | NOT NULL | timestamp (ISO 8601 UTC) | pipeline | last pipeline touch |
| `is_event` | `INTEGER` | NOT NULL | boolean | ingest | 1 for event instances; 0 for evergreen |
| `event_title` | `TEXT` | nullable | display string | event API / curator | verified |

### 1.9 Accessibility

| Field | Type | Nullability | Units | Provenance | How verified |
|---|---|---|---|---|---|
| `accessibility_json` | `TEXT` | nullable | JSON `{wheelchair, hearing, visual, notes}` | web + LLM | `not-verifiable` at ingest if untrusted; never silently dropped |

### 1.10 Reviews (Eric's two fields — the critical gap)

| Field | Type | Nullability | Units | Provenance | How verified |
|---|---|---|---|---|---|
| `review_count` | `INTEGER` | nullable | count | verified corpus only; **never** scraped | `null` when corpus unavailable |
| `review_score` | `REAL` | nullable | 0–100 | verified corpus only; **never** scraped | `null` when corpus too small |
| `review_sentiment` | `TEXT` | nullable | `positive`\|`neutral`\|`negative`\|`not-verifiable` | LLM digest of **verified** reviews; stamped `estimated` | never a gate |
| `review_source` | `TEXT` | nullable | `venue_self_attestation`\|`user_submission`\|`null` | ingestion | legal channel only |
| `review_confidence` | `TEXT` | nullable | `confidence` enum + `estimated` flag | Warden | `low_review_count` floor applied |

> **Critical gap (§8.3):** Google reviews and TripAdvisor reviews are **not** obtainable at
> commercial scale under their ToS (Google: official Places API is only usable inside the
> Google service — no storage/export; TripAdvisor: ToS bans scraping, API returns ~5 recent
> reviews, no full text). The closest achievable is venue self-attestation and user
> submissions. The ranking weight for reviews is therefore configurable and low by default;
> the review floor is a **soft** down-rank, never a hard gate.

---

## 2. Relationship model

### 2.1 Categories and aliases

- `activity_category` is the **canonical taxonomy**: `name`, `parent` (hierarchical), `level`
  (1 = core app category, 2 = sub, 3 = genre), `is_canonical`. The 10 core categories are:
  park, sports, nightlife, dining, arts, family, museum, climbing, cultural-events, cafes.
- `activity_category_mapping` is the many-to-many between activities and categories. A single
  activity can belong to more than one category (e.g. a "farmers market" is `dining` +
  `family` + `cultural-events`). `is_primary` picks the engine's primary sort key.
- `activity_alias` holds searchable alternate names (e.g. "Maket" → "Market", "The Byward"
  → "Byward Market") and feeds the `activities_fts` table. Aliases are normalized before
  indexing.
- **Deduplicated category field:** the engine ADR's `category` + `subcategory` pair is
  materialized here and reduced to a single `category` (FK) + `subcategory` (nullable) for the
  hot query path, with any cross-category mappings preserved in `activity_category_mapping`.

### 2.2 Chains vs independents

- `activity_chain` links two activities that belong to a *sequence or policy*: e.g.
  `{parent: "Saturday farmers market", child: "Saturday brunch", relation: "adjacent"}`,
  `{parent: "Fall fair", child: "Fairground ride", relation: "part_of"}`. Chains let the
  UI present "things to do together" (a walk with a coffee afterwards) and let the ranking
  engine reward *paired* matches if the user selects two intents.
- An independent activity has no `activity_chain` rows.

### 2.3 Seasonal variants

- `activity_season` models variants with a date window. E.g. "Outdoor ice rink" is a variant
  of "Ice skating" that is only `enabled` Nov–Mar. The engine evaluates `season_json` + the
  `activity_season` rows to decide `season_closed`.
- A **seasonal variant** is a *separate* `activity` record (not a field of the evergreen
  record) so that date-window filtering stays a fast index on `activity_season.enabled_from/to`.

### 2.4 Event vs evergreen

- `is_event = 1` marks an activity that is *bound to a date/time window* (a concert,
  a race, a market day). Such records usually have one or more rows in `activity_event`.
- Evergreen (`is_event = 0`) is open on a recurring schedule (`hours_json` + `season_json`).
- The engine's time-of-day gate treats the two differently: for events it checks
  `activity_event.starts_at` overlap; for evergreen it checks `hours_json` + `season_json`
  overlap. Both produce a hard `time` gate when they don't overlap.

### 2.5 Business vs "thingz" activity (the museum problem)

This is the one relationship model that must be **explicit** because a single real-world
entity is two records:

- **`venues`** is the geographic/venue entity: a physical place (museum, park, store,
  community hall, restaurant). A venue can host many activities.
- **`activities`** is the *thingz*: what you actually do. A museum is an activity (you go in
  for an hour), and the building that houses it is a `venue`.
- `activity_venue` is the junction: `(activity_id, venue_id, role, is_venue_activity)`.
  - `role='primary'` means the venue is where the activity happens.
  - `is_venue_activity=1` means "this activity **is** a venue" — e.g. a museum, a park, or
    a community hall. Its `venue_id` points to a `venues` row, and a `venues` row can have
    multiple `activities` pointing at it.
- Example: the "Byward Market" is one `venues` row and two `activities` rows — "Byward Market
  (shopping)" and "Byward Market (live music night)". Both point to the same venue; the
  shopping one has `is_venue_activity=1` (the market *is* the venue), the music one has
  `is_venue_activity=0`.

This de-couples **where** from **what you do**, which is exactly what the ranking engine needs
(distance and amenity from `venues`, what to do from `activities`).

---

## 3. Ranking mapping — hard gates vs soft scores

Written against the engine ADR (`2026-10-21-activity-filtering-engine-constraints-matching.md`)
so it is directly implementable. **Everything hard gates first, then soft scores.**

### 3.1 Hard gates (Tier 1 — exclude *before* scoring)

| # | Field(s) | Condition | Engine ADR anchor | Line |
|---|---|---|---|---|
| 1 | `cost_max` + `cost_known` | `cost_max > user.max_budget`, OR `cost_known=0` AND `user.max_budget` set AND `cost_gate_mode=strict` | §5.2 | 245 |
| 2 | time window | requested window does not overlap `hours_json` + `season_json` (+ `activity_event` for `is_event=1`) | §5.4 | 275 |
| 3 | distance | haversine(`activity.venue`, `user`) > `radius_km` | §5.5 | 289 |
| 4 | party size | `party_max IS NOT NULL` AND `party_max < user.party_size` | §5.3 | 260 |
| 5 | weather class | `weather_dependency` incompatible with the user's weather rule, e.g. `outdoor`+`not-verifiable` under `avoid_rain`; `partial` under `prefer_indoor`; **unset fields never create a gate** | §5.1 | 219 |

Notes:
- Always: `name`/`category`/`location` must be present at ingest, else the row is never
  shipped (see §7.1).
- Unverified `hours`/`weather_dependency`/`cost` **never** create a hard gate; they degrade
  to soft scoring and are surfaced in the degrade envelope's `warnings`/`unmet` (§8.3).

### 3.2 The corrected soft-score table (sum = **1.00**)

Scout's published table sums to **1.05** (see §8.1); this is the corrected, implementable table
whose weights sum to exactly 1.00.

| # | Signal | Weight | Definition |
|---|---|---|---|
| 1 | Weather comfort | 0.20 | class-aware; `not-verifiable`→0.5 neutral; temp-band + precip/wind penalty |
| 2 | Cost headroom | 0.15 | `1 - cost_max / budget` clamped; free = 1.0 |
| 3 | Time-of-day match | 0.15 | open-hours match to requested band |
| 4 | Distance decay | 0.15 | `1/(1+d)` mapped so d≈0→1, d≈radius→0.5 |
| 5 | Intent (category match) | 0.15 | `category`/`subcategory` vs `intent` |
| 6 | Party fit | 0.10 | comfort fraction of party fit |
| 7 | Review score × sentiment × count | 0.08 | `review_score/100 × sentiment_weight × review_count_conf`; `low_review_count` → heavy discount |
| — | **Confidence dampener** | — | **multiplicative**, not additive — see below |

Numerator check: `0.20 + 0.15 + 0.15 + 0.15 + 0.15 + 0.10 + 0.08 = 1.00` ✓

The engine ADR's `w_recent` (0.05) and `w_seats` (0.05) are **removed** (§6.2): `seats`
merges into `party fit`, and `recent` + `confidence` fold into the multiplicative dampener.
This keeps the weight sum at 1.00, which is the honest fix (see §8.1).

**Confidence dampener (multiplicative):** `confidence_factor` ∈ [0.6, 1.0], computed from
`confidence_fields` completeness in §7.4: `confidence_factor = 1.0 - 0.25 × (1 - complete_fraction)`.
`final_score = 100 × clamp(soft_score × confidence_factor, 0, 1)`. Review weight 0.08 applies
below the review floor only when `confidence` is `curated`/`verified`; otherwise the floor
without a hard gate.

### 3.3 Thresholds and minimum policy

| Threshold | Value | Effect |
|---|---|---|
| Default review floor (`min_review_count`) | 3 for `verified`, 5 for `confirmed` | below floor → **exclude from top-N** (soft), keep in `unmet` `few_reviews`, or surface via `curated_fallback`; never a hard gate |
| Temperature comfort band | ~21–27 °C (configurable per activity via `weather_sensitivity`) | soft; hard only when user chose `avoid_heat`/`avoid_cold` |
| Weather gate weight | 0.20 | unchanged from engine ADR, but now class-aware |
| Degrade thresholds | `full`/`partial`/`sparse`/`empty` | unchanged (engine ADR §9) |

### 3.4 Exact ADR amendments required

All line numbers are from `2026-10-21-activity-filtering-engine-constraints-matching.md`.

| Amendment | Purpose | File & line |
|---|---|---|
| **§3.1 Activity** — replace `outdoor`/`indoor`/`mixed` booleans with `weather_dependency` (enum), add `weather_sensitivity`, `cost_max`/`cost_known`/`cost_currency`, `party_max`/`party_suitable`, `is_event`, `hours_json`/`season_json`, `accessibility_json`, `review_*` fields, `confidence_score` | Canonical record becomes the engine data model | 89–111 |
| **§3.1 Activity** — repurpose `party_size` → `party_min`/`party_max` (de-duplicate `capacity`); `hours` → `hours_json`/`season_json`; `price` → `cost_*` | Constrain the already-amalgamated materialized fields | 89–111 |
| **§3.3 WeatherState** — keep as-is (external); map `weather_dependency` to the engine's `outdoor`/`indoor`/`mixed` for legacy | Bridge old & new classification | 128–148 |
| **§5.1 Weather** | `outdoor`/`indoor`/`mixed` classification superseded by class-aware `weather_dependency`; `partial` is first-class; `not-verifiable` cannot hard-gate | 219 |
| **§5.2 Cost** | `price`/`price_class` → `cost_min`/`cost_max`/`cost_class`/`cost_known`; hard gate fires on `cost_max > budget` AND `cost_known=1`; `cost_known=0` + budget → hard-exclude *only* in `strict` mode (default `prefer`) | 245 |
| **§5.3 Party size** | `max < party_size` → hard-exclude via `party_max`; `min` threshold dropped to avoid over-restricting | 260 |
| **§5.4 Time of day** | hours gate gains `holiday_closures` + `season_json` + `activity_event` for `is_event=1` | 275 |
| **§5.5 Distance** | keep haversine hard gate + decay score | 289 |
| **§6.2** | Weight table corrected to sum 1.00 (drop `w_seats`, `w_recent`; fold into `party fit` + multiplicative confidence dampener; add `review` weight) | 322 |
| **§6.2 / §7** | `confidence` (additive) → `confidence_factor` multiplicative dampener | 322–340 |
| **§8.3 Activity-data unavailability** | Add per-field gate: record with critical fields (`hours`, `weather_dependency`, `cost_max`) all unverifiable → `curated_fallback` candidate, never ranked; keep `never fabricate` | 429 |
| **§10 Ingest pipeline** | Add `catalog_versions` + `activity_delta` snapshotting (for deterministic per-request scoring) + category/alias/chain/event segmentation | 489–511 |

---

## 4. Storage & versioning — SQLite schema

The catalog is **append-only + versioned**. The engine reads a fixed snapshot per request,
which keeps scoring deterministic. The append-only delta log (`activity_delta`) is the audit
trail that lets us rebuild any past snapshot.

### 4.1 DDL

```sql
-- 1. Catalog versions (snapshot pointer)
CREATE TABLE IF NOT EXISTS catalog_versions (
    version_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    TEXT NOT NULL DEFAULT (datetime('now')),
    reason        TEXT NOT NULL,
    snapshot_ref  TEXT NOT NULL,
    row_count     INTEGER NOT NULL DEFAULT 0,
    checksum_sha256 TEXT
);
CREATE TABLE IF NOT EXISTS current_catalog (
    version_id INTEGER PRIMARY KEY REFERENCES catalog_versions(version_id) ON UPDATE CASCADE
);

-- 2. Core catalog row
CREATE TABLE IF NOT EXISTS activities (
    id                  TEXT PRIMARY KEY,     -- ${provider}:${normalized_slug}
    provider            TEXT NOT NULL,
    name                TEXT NOT NULL,
    description         TEXT,
    category            TEXT NOT NULL,
    subcategory         TEXT,
    category_note       TEXT,
    venue_lat           REAL,
    venue_lng           REAL,
    address             TEXT,
    postal_code         TEXT,
    phone               TEXT,
    website_url         TEXT,
    booking_url         TEXT,
    cost_currency       TEXT NOT NULL DEFAULT 'CAD',
    cost_min            REAL,
    cost_max            REAL,
    cost_known          INTEGER NOT NULL DEFAULT 0,
    cost_class          TEXT,
    party_min           INTEGER,
    party_max           INTEGER,
    party_suitable      TEXT,
    hours_json          TEXT NOT NULL,
    season_json         TEXT NOT NULL,
    weather_dependency  TEXT NOT NULL,
    weather_sensitivity TEXT,
    accessibility_json  TEXT,
    photos              TEXT,
    review_count        INTEGER,
    review_score        REAL,
    review_sentiment    TEXT,
    review_confidence   TEXT,
    confidence          TEXT NOT NULL,
    confidence_score    REAL NOT NULL DEFAULT 0.0,
    confidence_fields   TEXT NOT NULL,
    source              TEXT NOT NULL,
    raw_payload         TEXT NOT NULL,
    metadata            TEXT NOT NULL,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_activities_provider       ON activities(provider);
CREATE INDEX idx_activities_category       ON activities(category);
CREATE INDEX idx_activities_lat_lng        ON activities(venue_lat, venue_lng);
CREATE INDEX idx_activities_confidence     ON activities(confidence);
CREATE INDEX idx_activities_weather_dep    ON activities(weather_dependency);
CREATE INDEX idx_activities_cost_max       ON activities(cost_max);
CREATE INDEX idx_activities_party_max      ON activities(party_max);

-- 3. Venue entity (a museum is a venue AND an activity)
CREATE TABLE IF NOT EXISTS venues (
    venue_id            TEXT PRIMARY KEY,
    name                TEXT NOT NULL,
    lat                 REAL,
    lng                 REAL,
    address             TEXT,
    postal_code         TEXT,
    timezone            TEXT,
    parent_venue_id     TEXT,
    created_at          TEXT NOT NULL DEFAULT (datetime('now')),
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE TABLE IF NOT EXISTS activity_venue (
    activity_id    TEXT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    venue_id       TEXT NOT NULL REFERENCES venues(venue_id) ON DELETE CASCADE,
    role           TEXT NOT NULL DEFAULT 'primary',
    is_venue_activity INTEGER NOT NULL DEFAULT 0,
    PRIMARY KEY (activity_id, venue_id)
);

-- 4. Taxonomy (categories + aliases)
CREATE TABLE IF NOT EXISTS activity_category (
    name        TEXT PRIMARY KEY,
    parent      TEXT,
    level       INTEGER NOT NULL,
    icon        TEXT,
    is_canonical INTEGER NOT NULL DEFAULT 1
);
CREATE TABLE IF NOT EXISTS activity_category_mapping (
    activity_id   TEXT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    category_name TEXT NOT NULL REFERENCES activity_category(name),
    is_primary    INTEGER NOT NULL DEFAULT 1,
    mapped_at     TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (activity_id, category_name)
);
CREATE TABLE IF NOT EXISTS activity_alias (
    alias       TEXT PRIMARY KEY,
    activity_id TEXT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    source      TEXT
);
CREATE INDEX idx_activity_alias ON activity_alias(alias);

-- 5. Seasonal variants
CREATE TABLE IF NOT EXISTS activity_season (
    season_id    INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id  TEXT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    label        TEXT NOT NULL,
    enabled_from TEXT,
    enabled_to   TEXT,
    is_open_now  INTEGER NOT NULL DEFAULT 0,
    UNIQUE (activity_id, label)
);

-- 6. Chains
CREATE TABLE IF NOT EXISTS activity_chain (
    chain_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    parent_id    TEXT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    child_id     TEXT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    relation     TEXT NOT NULL,
    label        TEXT NOT NULL,
    UNIQUE (parent_id, child_id, relation)
);

-- 7. Time-bounded events
CREATE TABLE IF NOT EXISTS activity_event (
    event_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    activity_id  TEXT NOT NULL REFERENCES activities(id) ON DELETE CASCADE,
    title        TEXT NOT NULL,
    starts_at    TEXT NOT NULL,
    ends_at      TEXT,
    venue_id     TEXT REFERENCES venues(venue_id) ON DELETE SET NULL,
    price_min    REAL,
    price_max    REAL,
    seats_available INTEGER,
    source       TEXT NOT NULL,
    created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_activity_event_starts ON activity_event(starts_at);
CREATE INDEX idx_activity_event_activity ON activity_event(activity_id);

-- 8. Audit: append-only change log
CREATE TABLE IF NOT EXISTS activity_delta (
    delta_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id    INTEGER NOT NULL REFERENCES catalog_versions(version_id) ON UPDATE CASCADE,
    activity_id   TEXT NOT NULL,
    field_name    TEXT NOT NULL,
    old_value     TEXT,
    new_value     TEXT,
    change_type   TEXT NOT NULL,
    source        TEXT,
    committed_at  TEXT NOT NULL DEFAULT (datetime('now'))
);
CREATE INDEX idx_activity_delta_activity ON activity_delta(activity_id);
CREATE INDEX idx_activity_delta_version ON activity_delta(version_id);

-- 9. FTS5 search index (aliases + name + category + subcategory)
CREATE VIRTUAL TABLE IF NOT EXISTS activities_fts USING fts5(
    name, aliases, category, subcategory,
    content='activities', content_rowid='rowid'
);
CREATE TRIGGER IF NOT EXISTS activities_ai AFTER INSERT ON activities BEGIN
    INSERT INTO activities_fts(rowid, name, aliases, category, subcategory)
    VALUES (NEW.rowid, NEW.name, COALESCE(NEW.aliases,''), NEW.category, NEW.subcategory);
END;
CREATE TRIGGER IF NOT EXISTS activities_ad AFTER DELETE ON activities BEGIN
    INSERT INTO activities_fts(rowid, name, aliases, category, subcategory)
    VALUES (OLD.rowid, OLD.name, COALESCE(OLD.aliases,''), OLD.category, OLD.subcategory);
END;
CREATE TRIGGER IF NOT EXISTS activities_au AFTER UPDATE ON activities BEGIN
    INSERT INTO activities_fts(rowid, name, aliases, category, subcategory)
    VALUES (NEW.rowid, NEW.name, COALESCE(NEW.aliases,''), NEW.category, NEW.subcategory);
END;
```

### 4.2 Snapshotting / deterministic scoring

- **Rebuilds are atomic:** Warden performs an ingest as a single transaction that (a) drops
  and re-creates temp views over a staging table, (b) materializes rows into `activities`,
  (c) bumps `current_catalog.version_id`, (d) appends one `catalog_versions` row with
  `checksum_sha256` and `row_count`. Readers always point at an immutable version.
- **Per-request snapshot:** the candidate finder signs the request with
  `catalog_version_id = (SELECT version_id FROM current_catalog)`. The engine scores only the
  rows present in that version; concurrent ingest changes neither the query nor its answers.
- **Determinism:** the engine never hits the network within a request. Every external signal
  (weather `WeatherState`, item `updated_at`, instances) is materialized into the catalog
  *before* the version is created, so the query is pure lookups + math.
- **Drift recovery:** `activity_delta` (append-only) records every `created`/`updated`/
  `reconciled`/`discarded` row-level change; `old_value`/`new_value` plus `field_name` let the
  engine replay a record's history and produce an honest `data_freshness` per source.

---

## 5. Ingestion contract

### 5.1 Discovery agent (→ Mine) output

A discovery agent emits **candidates only** (never facts):

```json
{
  "id": "osm:venue_2048",                 // computed by the agent
  "provider": "osm",
  "source": ["osm-overpass", "wiki"],
  "raw_payload": { ...original source JSON... },
  "name": "Central Experimental Farm",
  "category": "museum",
  "subcategory": "history",
  "address": "1Analysis Dr",
  "venue_lat": 45.42,
  "venue_lng": -75.70,
  "discovered_at": "2026-10-24T12:00:00Z",
  "status": "candidate"
}
```

Canonical `id` is `{provider}:{normalized_slug}` where `normalized_slug` = ascii-folded,
lowercased, non-alphanumeric stripped, spaces→hyphens. Agents **must not** invent
`confidence`, `hours`, `cost`, or review fields.

### 5.2 Enrichment agent (→ Adept) output

Adept reads candidates and writes back a full `listing_record` with:

- All fields in §1 (types, nullability per §1).
- `confidence_fields`: per-field stamp.
- `raw_payload` preserved.
- `status`: `enriching` → `verified` / `inferred` / `user_generated` / `needs_review`.
- `last_refreshed` + `last_verified` (where vouched).
- Cognition/expense/party fields come only from **web + LLM per-listing research**, never
  from assumption; every unverified field is stamped and flagged (§3.2).

### 5.3 Verification / QA (→ Warden)

- **Dedupe keys:** primary `id = {provider}:{slug}`. Secondary fuzzy key:
  `name + normalized_address + haversine(lat,lng) < 50m` → same venue even when providers
  name it differently (covers the museum-is-both case across `venues` + `activities`).
- **Conflict resolution** (two sources disagree on hours/price/weather class):
  1. prefer higher `confidence` (`verified` > `inferred` > `user_generated`);
  2. else prefer more recent `last_verified`;
  3. else prefer the more authoritative `provider` (municipal > OSM > curated);
  4. the loser is kept in `raw_payload` + an `activity_delta` row with
     `change_type='reconciled'`, so the disagreement is visible, not silently dropped.
- **Staleness:** `last_verified` + `last_refreshed` drive the degrade path. Sources that
  exceed their TTL are re-fetched on the next Adept run — never silently served stale.
- **Confidence calibration:** Warden cross-checks a sampled subset against reality and
  reports per-source `confidence_fields` calibration to Concierge.

### 5.4 Staleness / refresh model (per class)

| Field(s) | TTL | Trigger |
|---|---|---|
| `weather_dependency`, `weather_sensitivity` | 24h or on weather shift | weather X |
| `hours_json`, `season_json` | 24h; nightly email/phone re-check | schedule + `holiday_closure` |
| `cost_*`, `party_*` | 24h | schedule |
| `accessibility_json` | 24h (LLM) | schedule |
| `review_count`, `review_score` | daily | schedule |
| `venues`, `category`/`alias` taxonomy | weekly (incremental) | schedule |
| curated seed | continuous by hand | trust event |
| events (`activity_event`) | per-request near-real-time | query window |
| `weather_*` | hourly (stale-while-revalidate) | ECCC |

### 5.5 Confidence computation (engine-facing)

`confidence_score` is a numeric, calibrated per §7.4. The engine consumes it as a
**multiplicative** dampener (§3.2), so an unverified field lowers the score gracefully
instead of vanishing. Per-field `confidence_fields` stamps are what the Warden uses to
compute the completeness fraction.

---

## 6. Art of the possible

Be honest about what is reliably extractable at scale, what needs a human, and what stays
unverified.

### 6.1 Reliably extractable at scale (free, legal, low-friction)

- **Venue existence + coordinates:** OSM amenity/shop/tourism tags, City of Ottawa cultural
  spaces/recreation inventories. High quality, cheap, weekly.
- **Category/subcategory taxonomy:** OSM + Wikipedia descriptions (CC-BY-SA 4.0, lightly used).
  High accuracy on obvious classes (`park`, `museum`, `sports`); weaker on niche classes
  (`indoor climbing`), flagged `inferred`.
- **Weather:** ECCC/MSC GeoMet, hourly, official licence, no ToS conflict. **Core defensibility.**
- **Event instances:** Eventbrite free tier for *current/upcoming* events (guarded:
  informational only, venue link shown, never as our own facts).

### 6.2 What mostly needs a human

- **Hours of operation** for private businesses (municipal data covers only city-run
  facilities). Every private-venue hour needs direct verification — venue site, email, or phone.
- **Group size** (`party_min/max`, `party_suitable`), **price** disclosure, **accessibility**
  minutiae, **venue identity** (is this still operating?). Small private venues change these
  constantly.
- **Curated seed** (the product's floor) — team vetting, highest confidence.
- **User submissions** behind a moderated queue.

### 6.3 What stays unverified (and by design)

- **Google reviews / TripAdvisor reviews** — not obtainable under their ToS (§1.10). The
  closest achievable: venue self-attestation or user submissions; otherwise `null` and the
  review weight is configurable and light. Review *sentiment* LLM-derived is always stamped
  `estimated`, never a gate.
- **Translation to CAD** — costs are usually in local currencies; `cost_class` is derived,
  not the raw figure. `cost_known=false` is an acceptable, common state.
- **Authenticity of UGC** — user submissions are moderated and `user_generated` until the
  moderation queue proves a sample accurate.

### 6.4 Where Scout's design is wrong or over-optimistic

1. **Review score/count is not obtainable** (Google/TripAdvisor ToS). Scout's §3.3 states it
   but §4.3 makes the review weight (0.08) + `min_review_count` floor part of the ranking
   contract as if they'll be available at volume. **Fix:** the review weight must be
   *configurable and low by default* (0.08), the floor *soft* (exclude from top-N, never a
   hard gate), and the "no empty result" guarantee must not depend on reviews. For the
   thin categories (museums 35, climbing 30, events 45), the review floor would empty the
   result set — the floor must never be the thing that gates the "at least one option" promise.
2. **The published weight table sums to 1.05** (§8.2) — a hard arithmetic error. The engine
   ADRs sum to exactly 1.00. My corrected table restores 1.00 and folds `confidence` into a
   multiplicative dampener (§3.2).
3. **`confidence` as an enum is not enough for the engine.** The engine needs a numeric
   `confidence_score` with a reproducible formula (§7.4). The enum stays for UX/QA; the
   number is what's scored.
4. **`hours` as an opaque object** is not implementable for the engine's time-of-day gate.
   I materialize `hours_json` + `season_json` + `is_event` so the gate is a cheap index
   lookup, not an LLM call per query.
5. **Cost hard-gate on undisclosed prices** (Scout §4.2: "undisclosed-with-budget → hard-exclude
   unless user opts out") is correct in principle, but if applied in `strict` mode by default
   it will silently kill the thin categories. I set the default to `prefer` and surface
   `cost_known=false` in `unmet` so the user can choose to see undisclosed prices.

---

## 7. Corrections / close-the-loop with Scout

Field count and refresh cadence reported so his cost card is accurate:

- **Field count:** 14 core identity/provenance fields + 21 presentation/contact/media +
  7 classification/location + 8 cost + 4 party + 9 operating-state + 4 accessibility + 5
  review + 3 classification-override ≈ **52 fields** across `activities` + `venues` +
  `activity_venue` + `activity_category` + `activity_alias` + `activity_season` +
  `activity_chain` + `activity_event` + `activity_delta` + `catalog_versions` + `current_catalog`.
  The engine-hot path is `activities` (~14 mandatory columns after normalization).
- **Refresh cadence:** see §5.4 — operating state (hours/cost/party/accessibility) = 24h;
  reviews = daily; category/alias = weekly; venue index = weekly; curated = continuous by
  hand; events = per-request; weather = hourly. This is ~9 distinct TTL classes.
- **Cost impact:** LLM enrichment dominates Scout's model. My schema's per-listing field
  count is ~14–18 LLM-derived fields for operating state + reviews; keep LLM calls at
  **≤1.1M input + ≤0.5M output** per listing (guardrail §6.3) so the per-listing cost stays
  in his ~$5–8k/1000 bracket. If his real quote lands above ~$10k/1000, we trim the
  enrichment to the hard-gate fields only (drop `accessibility_json`, `weather_sensitivity`,
  `price_class` side-loading) and re-derive the drill-down.

Comment on Scout's cost card (`t_d89ab99c`) with these numbers once the schema is locked.

---

## 8. Appendix — Field presence table (for the ingest validation rule)

| Tier | Fields | Ingest rule |
|---|---|---|
| **Must-have** | `id`, `provider`, `name`, `category`, `venue_lat`, `venue_lng`, `weather_dependency`, `hours_json`, `confidence` | Row dropped (log, not shipped) if missing |
| **Should-have** | `cost_max`, `party_max`, `last_verified`, `confidence_fields`, `raw_payload` | Row shipped as `inferred` if missing |
| **Nice-to-have** | `address`, `booking_url`, `photos`, `party_suitable`, `review_*`, `accessibility_json` | Optional; never a gate |

This table is the validation contract the Warden enforces. The V1 target is that **every**
shipped row reaches the "should-have" tier; rows that can't are surfaced to the curator,
not shipped as verified.

---

*Prepared by Forge (Principal Software Architect), 2026-10-24. Accept under Eric's go/nogo.*
