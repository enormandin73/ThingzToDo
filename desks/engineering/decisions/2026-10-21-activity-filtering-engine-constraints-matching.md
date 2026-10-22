# Design — Activity Recommendation & Filtering Engine
## Constraints Matching for ThingzToDo

**ADR:** `desks/engineering/decisions/2026-10-21-activity-filtering-engine-constraints-matching.md`
**Owner:** Forge (Principal Software Architect) — this is the repository's first ADR
**Date:** 2026-10-21
**Status:** Accepted (design) — implementation owned by the engineering team
**Feeds:** the activity-catalog repository (`app/`), the activity-ingest pipeline, and the
public recommendation API surface

---

## 0. Purpose & scope

This ADR specifies **how the ThingzToDo recommendation/filtering engine matches a user's
request to candidate activities**, using the five constraints the product is built around:

1. **Weather** — indoor vs. outdoor, rain-safe, heat-cold safety
2. **Cost** — free / cheap / splurge
3. **Party size** — solo / pair / family / group
4. **Time of day** — morning / lunch-hour / evening / late night
5. **Distance** — how far the user will travel

It defines the **data model**, the **scoring approach**, and **how constraints are weighted or
filtered**, plus the handling for **missing or flaky external data** and the **graceful
degradation** of the engine when data or services are unavailable.

Scope of this document: the *matching engine* (candidate selection + scoring + ranking).
It does **not** cover the user-facing UI/UX copy, the activity-catalog ingestion pipeline in
full, or deployment infra. Where those interfaces matter, the boundary is stated so they can
be built against it.

---

## 1. Where this engine sits

```
User request (location + constraints)
        │
        ▼
[1] Normalize & validate constraints          (validator / type coercion)
        │
        ▼
[2] Candidate generation (activity "finder")   (bounded pool, source-agnostic)
        │
        ▼
[3] Engine core: hard-gate filter → soft-score → rank
        │
        ▼
[4] Score + reason envelope (matched/unmet reasons)
        │
        ▼
[5] Degradation layer (confidence gating, fallbacks)
        │
        ▼
Ranked recommendations + structured "why" + degrade code
```

Each stage is a discrete unit that can run independently, so a slow or failing stage can be
counted in, skipped, or extended without collapsing the whole query.

---

## 2. The candidate "finder"

A *finder* is any component that produces a bounded candidate pool for a request:

- **Area finder** — activities within a geographic radius (uses a geo-index / bounding box +
  haversine distance check). Supports "fall back to a broader area if the precise area has
  no data".
- **Type/player finder** — narrows by activity type, or by party-size band.
- **Event/calendar finder** — recurring or upcoming instances for a date/time window.
- **Curated fallback finder** — a small, team-maintained list of high-value activities for an
  area, used when provider feeds are empty.

The engine never demands that a finder cover every constraint. The finder is allowed to be
*over-generous* (return extra candidates); the engine then filters and ranks it. The finder is
*not* allowed to fabricate candidates that don't exist in any source.

---

## 3. Data model

The engine is built on five core entities. Field names are the schema contract between the
catalog, the ingest pipeline, the engine, and the API.

### 3.1 Activity (the recommended thing)

| Field | Type | Purpose |
|---|---|---|
| `id` | string | Stable primary key (provider + slug) |
| `slug` | string | Human-readable, URL-safe |
| `category` | string | Broad type, e.g. `park`, `museum`, `sports`, `cafe` |
| `subcategory` | string | Fine type, e.g. `hiking`, `indoor-climbing` |
| `outdoor` | boolean | Truly outdoor |
| `indoor` | boolean | Truly indoor |
| `mixed` | boolean | Either works / indoor-with-outdoor-element |
| `description` | text | |
| `location` | Geo Point | lat/lng of the venue (venue, not just the org) |
| `bounds` | Geo Rect/Polygon | For area-indexing (optional, for large grounds) |
| `geohash` | string | For fast radius queries |
| `address` | string | Display address |
| `price` | Price object | `currency`, `min`, `max`, `tiers` (list of {label, price, applies_to}) |
| `price_class` | enum | `free`, `cheap`, `moderate`, `premium`, `splurge` (derived, cached) |
| `party_size` | PartySize object | `min`, `max`, `capacity` (optional) |
| `party_suitable` | string[] | Which party-size bands it supports, e.g. `solo,pair,family,group` |
| `hours` | Hours object | `opens`, `closes`, `repeat` (e.g. `daily, weeekday, weekend`), `timezone` |
| `season` | Season object | `enabled_from`, `enabled_to`, `is_open(utc_now) → bool` |
| `availability_rules` | object | Free-text/structured rules for dynamic open/close or booking windows |
| `metadata` | object | Open free-form key/value (contact, booking URL, capacity notes, etc.) |
| `confidence` | enum | `curated` / `verified` / `inferred` / `user-generated` — marks data provenance |

### 3.2 ActivityInstance (a time-specific availability of an Activity)

| Field | Type | Purpose |
|---|---|---|
| `activity_id` | string | FK into Activity |
| `starts_at` | datetime | When the thing is available |
| `ends_at` | datetime | When it is no longer available |
| `available_seats` | int | Left (0 = sold out) |
| `venue_id` | string | When the venue can differ from the org |
| `created_at`, `updated_at` | datetime | For sync/retry |
| `source` | string | Which provider produced this instance |

Instances are what the time-of-day and "is it open right now" check evaluates. They also let
the engine rank by `available_seats` (a live, local-at-the-time signal).

### 3.3 WeatherState (external, per area + time)

| Field | Type | Purpose |
|---|---|---|
| `lat`, `lng` | float | Where the weather refers to |
| `observed_at` | datetime | When the reading was taken |
| `fetch_at` | datetime | When it was fetched/ingested |
| `source` | string | Provider + endpoint |
| `temperature_c` | float | Core signal |
| `temperature_feels_like_c` | float | Heat/cold perception |
| `precip_probability` | float 0–1 | Rain/snow likelihood |
| `precip_type` | enum | `none`, `rain`, `snow`, `sleet`, `hail`, `freezing` |
| `precip_amount_mm` | float | Amount (for severity) |
| `conditions` | enum | `clear`, `partly_cloudy`, `cloudy`, `rain`, `snow`, `storm`, `wind`, `fog` |
| `wind_kph` | float | |
| `humidity_pct` | float | |
| `uv_index` | float | |
| `confidence` | float 0–1 | Provider reliability during the observation |
| `staleness_seconds` | int | `now - fetch_at`; computed by the engine |
| `coverage` | float 0–1 | Fraction of requested area the reading covers |

### 3.4 UserRequest (the normalized incoming query)

| Field | Type | Purpose |
|---|---|---|
| `request_id` | string | Traceable ID (for logs/telemetry) |
| `user_lat`, `user_lng` | float | Center of the search |
| `timezone` | string | IANA zone (e.g. `America/Quebec`) — needed for "is it open now" |
| `radius_km` | float | User's travel willingness |
| `weather` | WeatherConstraint | keep home / avoid rain / keep warm / etc. (see §5) |
| `cost` | CostConstraint | max budget (optional), preferred classes |
| `party_size` | PartySizeConstraint | `solo|pair|family|group` or a band |
| `time` | TimeConstraint | desired window or time-of-day bands |
| `intent` | string | e.g. `outdoor`, `date-night`, `kids`, `workout` — feeds category preference |
| `rank_weights` | object | Overrides of the global constraint weights (per-request preference) |
| `preferred_place_ids` | string[] | Hard-preference overrides (e.g. "prefer venue X") |
| `fallback_priority` | string[] | Which fallbacks the user wants (e.g. `curated`, `indoor`) |

### 3.5 RecommendationResult (engine output)

| Field | Type | Purpose |
|---|---|---|
| `rank` | int | 1-based position |
| `activity_id` | string | |
| `score` | float 0–100 | Confidence in the match |
| `matched` | string[] | Constraints satisfied |
| `unmet` | string[] | Constraints not satisfied (always emitted, not just on failure) |
| `reasons` | string[] | Human-readable, evocative reason strings |
| `score_breakdown` | object | Sub-scores per dimension (for metrics/debug) |
| `distance_km` | float | |
| `distance_class` | string | `near`, `moderate`, `far`, `too_far` |
| `weather_state_ref` | string | Which weather snapshot was used |
| `confidence` | float 0–1 | Engine's confidence in this result (not the activity's) |

### 3.6 Why-result (degrade envelope)

| Field | Type | Purpose |
|---|---|---|
| `mode` | enum | `full`, `partial`, `sparse`, `empty` |
| `data_freshness` | object | Per-source {name, fresh, stale, missing} |
| `reasons` | string[] | "Because rain, outdoor activities were filtered; indoors shown." |
| `fallbacks_used` | string[] | Which fallback sources produced results |
| `warnings` | string[] | Non-fatal issues (e.g. "weather data stale > 30 min") |

---

## 4. Input contract

A request arrives as a **normalized constraint vector**. The validator coerces and rejects
malformed input early (e.g. bad timezone, radius < 0, cost < 0). Normalization turns the
user's free-form request into the typed fields above.

Normalization rules:
- **Distance** → kilometers, integer or decimal.
- **Time** → a UTC window `[starts_at, ends_at]` plus an optional *time-of-day* hint
  (morning/lunch/evening/late-night).
- **Party size** → one of `solo` (1), `pair` (2), `family` (3–5), `group` (6+), or a raw
  integer; the activity's `party_suitable` is matched against these bands.
- **Weather** → a *rule set*, not a boolean: the user picks which weather signals are
  acceptable, and the engine evaluates them per activity.
- **Cost** → a hard budget (`max`) plus optional preferred *classes*; `free` is always
  implicitly "max ≥ 0".

The request *may* omit any constraint. Omitted constraints are **not** applied as gates; they
become soft preferences. (Example: a user who omits cost still gets free options first via
scoring, but nothing is hard-filtered.)

---

## 5. How each constraint is handled

### 5.1 Weather

**Classification.** Every activity carries `outdoor` / `indoor` / `mixed`. Weather is assessed
against this classification plus the user's requested weather *rules*.

**Evaluation.** Given a `WeatherState`, the engine evaluates each activity as follows:

| User weather rule | Engine behaviour |
|---|---|
| `keep_weather` (any/neutral) | no gate; weather only affects scores lightly |
| `avoid_rain` / `no_precip` | hard-gates any `outdoor` activity where `precip_type != none` or `precip_probability > threshold`; `mixed`/`indoor` pass |
| `keep_dry` | maps to `avoid_rain` + `avoid_snow` |
| `avoid_cold` | hard-gates `outdoor` activities whose `temperature_feels_like_c < cold_floor` (activity's or global floor); indoor pass |
| `avoid_heat` | hard-gates `outdoor` activities whose `temperature_feels_like_c > heat_floor`; indoor pass |
| `no_storm` | hard-gates any activity (outdoor or indoor) where `conditions in {storm, freezing_rain}` |

**Weather as a soft signal** (not just a gate): even among passing candidates, an activity
whose weather is *comfortable* (inside its temperature band, low precip) scores higher than an
activity whose weather is merely "acceptable". Temperature bands come from the recreation
research Scout synthesized (comfort band ~21–27°C for active outdoor pursuits), per-activity
`weather_sensitivity` overrides where the provider specifies one.

**Caveat on rain.** A user who says "no rain" is implicitly requesting an *indoor fallback*
for when it rains. The engine keeps that in mind in the degrade section (the "backup" feature
Scout identified as a genuine differentiator).

### 5.2 Cost

**Hard gate.** `activity.max > user.max_budget` → the activity is **excluded** entirely.
Any activity with `max = null` (not disclosed) is **excluded** when the user has set a budget,
unless the user has explicitly said "show undisclosed/prices too".

**Soft score.** For activities under budget, the cost sub-score scales with **budget headroom**:
`cost_score = 1 - (activity.price / user.max_budget)` clamped to `[0,1]`; an activity that
costs nothing scores 1.0. Near the budget, score approaches 0 (so a $99.99 activity under a
$100 budget still ranks behind a free option).

**Classes.** If the user prefers `free`/`cheap`, a `preferred_class_bias` in the weighting
boosts `price_class` matches; `free` is still not hard-required unless the user sets a `$0`
budget.

### 5.3 Party size

**Hard gate (with nuance).** Activities whose `max < user.party_size` are hard-excluded
(e.g. a "family" area small-group booking with `max=1` cannot host you). But a hard gate on
`min` is applied **loosely**: if the user's party is larger than the activity's `min`, the
activity *fails* hard (you'd be the nth person above the stated minimum) — **unless** the
activity's `capacity` field is absent or much larger than `min`, in which case it's treated
as a soft preference. This prevents the engine from over-restricting venues where the
provider just never filled in a minimum.

**Soft score.** For sizes that pass, score by how comfortably the party fits: a party of 2
among `solo/pair` venues scores highest; a party of 4 among `family` venues scores near-top;
a party of 4 at a `pair`-only venue (if it passed) is penalized heavily. The penalty is
proportional to the mismatch fraction, not a binary cliff.

### 5.4 Time of day

**Hard gate.** The requested window `[starts_at, ends_at]` must overlap the activity's open
time for that day-of-week. An activity that is *closed* for the requested window is excluded.
This uses `hours.repeat` + `season.enabled_from/to` + `timezone` (so "open now in Ottawa" is
correct even during DST transitions).

**Soft score.** Among open activities, score by **time-of-day preference match**: the user's
requested `time` bands are converted to hour ranges (e.g. `evening` = 17:00–21:00); an
activity whose main peak falls in the user's preferred band scores higher. For events with
fixed `starts_at`, the score is the proximity to the *start* of the event (earliest suitable
start = highest). "Right now" requests are a special case: `starts_at` must be within the
requested window and `available_seats > 0`.

### 5.5 Distance

**Hard gate.** `haversine(distance(user, activity.venue) > radius_km)` → exclude. Activities
in a *nearby but non-requested* area are included only via the area-finder fallback path,
and get an explicit `distance_class: too_far_from_venue` marker so the UI can rank those
last or surface them behind a "show nearby other areas" control.

**Soft score.** Distance is a **decaying** signal, not a cliff: `dist_score = 1 / (1 + d)`
mapped so that `d ≈ 0 → 1.0`, `d ≈ radius → ≈ 0.5`, `d > radius (fallback) → near 0`.
This keeps "just outside radius" results ranked above "several towns over" rather than
hard-clipping them (the user may be happy to stretch for the *right* thing).

---

## 6. Scoring approach

### 6.1 Two-tier model

Matching is explicitly **two-tier**:

1. **Tier 1 — Hard gating.** A candidate that fails any *hard* constraint is excluded **before
   scoring**. Hard constraints are: cost (budget), time (open/overlap), distance (radius),
   and weather rules the user marked as mandatory (`avoid_xxx` rules that must pass for a
   given activity-class to even be eligible). Hard rules are rules the user sets with
   `mandatory: true` semantics (default: weather `avoid_` rules are hard; `keep_weather` is
   soft). The engine still emits the activity in `unmet` (never silently drops), but it is
   **not ranked**.
2. **Tier 2 — Soft scoring.** Among gated-passers, compute a 0–100 score from the soft
   sub-scores and weights. Rank. A best-effort rank is returned regardless of tier-1 results.

This separation means the engine can say *why* something is missing ("too expensive", "closed
today", "over 20 km") rather than just returning nothing.

### 6.2 Score composition

For a candidate that passes hard gates:

```
score = w_weather * weather_score
      + w_cost    * cost_score
      + w_party   * party_score
      + w_time    * time_score
      + w_dist    * distance_score
      + w_intent  * intent_score          (category preference)
      + w_seats   * seats_score           (live availability local to now)
      + w_recent  * recent_score          (how fresh the instance is)
      - w_mismatch * mismatch_penalty
```

All `w_*` sum to 1.0 and are **configurable per project** and **overridable per request**
(`rank_weights`). Defaults:

| Weight | Default | Rationale |
|---|---|---|
| `w_weather` | 0.20 | Primary product differentiator (Scout) |
| `w_cost` | 0.15 | User has a budget constraint in ~most requests |
| `w_party` | 0.10 | Parties vary widely |
| `w_time` | 0.15 | Time-of-day is a core ask |
| `w_dist` | 0.15 | Distance is core to "near me" |
| `w_intent` | 0.15 | Category/type preference from `intent` |
| `w_seats` | 0.05 | Live availability is a tie-breaker, not a driver |
| `w_recent`| 0.05 | Freshness |

Weights are deliberately **conservative** (no single dimension dominates), and the sum stays
in `[0,1]` so a low score never means "impossible", just "less matching".

### 6.3 Sub-score definitions

- **weather_score** (0–1): comfort-band match + precip/wind penalty. E.g. `1.0` if temp in
  comfort band and no precip; `0.7` if temp is slightly off but fine; `0.3` if it's bad but
  the activity is indoor (weather didn't matter); `0.0` if it's a severe event user asked to
  avoid (should have been gated).
- **cost_score** (0–1): as in §5.2, `1 - price/max` clamped; `1.0` for free.
- **party_score** (0–1): comfort fraction of party fit.
- **time_score** (0–1): overlap/peak match as in §5.4.
- **dist_score** (0–1): decay as in §5.5.
- **intent_score** (0–1): match of `activity.category`/`subcategory` to the user's `intent`
  (from a category preference table; default: broad == 0.5, exact == 1.0).
- **seats_score** (0–1): `min(available_seats / min_group_size, 1.0)`.
- **recent_score** (0–1): recency of the instance relative to request time.

### 6.4 Result envelope

The API returns the top-N by rank plus, for each item, the `matched`/`unmet`/`reasons` so
the UI can show "why this one" and, when the user narrows further, *why other things were
excluded*.

---

## 7. Weighted vs filtered — the decision

A natural alternative would be to fold everything into one weighted score and treat *all*
constraints softly. We **reject** that for three reasons:

1. It produces nonsense (expensive things rank high for a $5 family with no budget headroom),
   and to fix that you still need hard budget and distance gates — so you'd have gates anyway.
2. It conflates "must have" with "nice to have". The two-tier model keeps that separation
   clean and makes the degrade path well-defined.
3. It makes "no results but here's why" far easier: the engine reports which hard gates fired
   (cost/time/distance/weather), and the UI can suggest a relaxation ("raise budget", "go
   farther", "try indoor").

Filters alone (hard gates, no scoring) were rejected because "fastest to the right answer
among many eligible" is exactly what the product is: ranking matters, not just eligibility.

---

## 8. Handling missing or flaky external data

External data (weather, activity feeds, events, events calendars) is owned by third parties
and is **inherently untrustworthy**: rate limits, timeouts, stale readings, partial coverage,
and outages. The design treats data availability as a first-class input to the engine, not a
background assumption.

### 8.1 Confidence-per-source

Every external datum carries a `confidence` (weather) or `source` + `confidence_class`
(activity). The engine reads `data_freshness` per source at query time:

- `fresh` — within TTL; trusted at full weight.
- `stale` — beyond TTL but within a warning window; still usable, counted down in the
  sub-score (`recent_score` or a `data_freshness` dampener), and surfaced in the degrade
  envelope's `warnings` so the UI can say "based on older data".
- `missing` — no data for the area/time; the engine **must not** invent it. The query moves
  to the appropriate degrade mode.

### 8.2 Weather unavailability ladder

If weather data is unavailable, the engine does **not** collapse:

1. `avoid_*` rules cannot be evaluated → the weather rules are **downgraded from hard gates
   to soft signals** for that query (weather is the product's core, so we *never* drop it;
   we just make it scoring-only). The degrade envelope says `mode=partial`, `weather=soft`.
2. If there is **no weather data at all** for the area → treat all outdoor activities as
   "undetermined", score them with the neutral 0.5 weather default, keep all other constraints,
   and emit the `missing` weather in `unmet`/`warnings` so the user knows the result is weather-
   blind.
3. Fall back to the **area fallback** (wider region) before declaring the weather missing, so
   a single-station gap doesn't kill a query.

### 8.3 Activity-data unavailability

If an activity feed is missing/flaky:
- The engine **does not fabricate** activities. If an area truly has no data from any source,
  the result is an empty list **with** a structured reason code in the degrade envelope
  (`data_empty`, `data_stale`, `sources_down`).
- The engine surfaces the **curated fallback** over the empty result (a small curated list for
  the area), so "no results" never means "the database is empty and you get nothing".
- A slow source does **not** block the whole query: each source is fetched in parallel with
  per-source timeouts, results are staged into a queue, and the query completes as soon as
  the sources that *did* respond are integrated. (See §9.)

### 8.4 Date/calendar unavailability

Recurring-event feeds and calendars can lag or disappear. The engine treats the absence of an
event instance as "not confirmed for this window" rather than "guaranteed not to happen": it
shows the activity as "to confirm", drops it from the top-N if seats are tight, and recommends
the user check the venue directly. This is safer than asserting a hard "no" on calendar data.

---

## 9. Graceful degradation behaviour

Degradation is decided by the **data availability meter** (computed in §8) combined with the
user's `fallback_priority`. The engine produces a `mode` + reason envelope, and the product
surface renders the matching behaviour for that mode:

| Mode | Trigger | Behaviour |
|---|---|---|
| `full` | All sources fresh & present | Full scoring; weather gate active. |
| `partial` | Some source stale/missing | Weather/downgrades to soft; other constraints still scored; UI shows stale/missing warnings. |
| `sparse` | Area under-provided; only curated/fallback sources | Results limited to curated list; distance/fallback scope wider; UI says "only a few confirmed…" and offers "show more from nearby areas". |
| `empty` | No source has any matching candidate | Structured empty: `reason_codes` + suggested relaxations (`relax distance`, `allow indoor`, `expand weather`, `raise budget` → none, just none). |

**Never-fabricate rule (hard).** The engine never returns an activity it has no data for, and
never returns a weather reading it did not fetch or cache. When the product would otherwise
show "no results", it shows a *reasoned* empty with an explicit relaxation prompt. This is the
core honesty guarantee of the product.

### 9.1 Resilience patterns

- **Timeouts & timeouts-as-filter.** Per-source fetch timeouts (configurable, default
  short). A slow source is dropped, not allowed to stall the query; its results are marked
  `source_unavailable`.
- **Circuit breakers.** If a provider consistently errors (e.g. N consecutive failures or
  error rate > threshold over a window), open the circuit for a cool-down; the engine skips
  that source during the cool-down and re-opens. Prevents cascade cascades from one flaky
  provider.
- **Retry with backoff + jitter** on transient 5xx/timeouts; idempotent GETs only (so
  retries are safe).
- **Rate-limit courtesy.** Respect provider `Retry-After`; the ingest pipeline (§10) honors
  it, and the engine adds small jitter to query distribution so two simultaneous queries to
  the same provider don't pile up.
- **Caching.** A short TTL cache for weather reads (stale-while-revalidate: return the
  cached value immediately, refresh async, and refresh the user's results when fresh data
  arrives). Prevents re-fetching the same stale weather on every query and tolerates brief
  provider pauses.

---

## 10. Ingest pipeline (the data side, briefly)

The engine consumes the *catalog*. The catalog is produced by an ingest pipeline with the
same resilience philosophy:

1. **Sources** — curated/local list (team), provider REST APIs (events, recreation), event
   calendars (ICS/RSS), user-submitted listings (moderated, `confidence=user_generated`).
2. **Normalization.** Each source's records are mapped to the Activity/Instance schema with a
   schema drift handler (unknown fields are kept in `metadata`, never dropped). Fields the
   engine needs are *materialized* at ingest time (e.g. `price_class`, `party_suitable`,
   `geohash`), so the engine never has to derive them per query.
3. **Validation.** Required fields are enforced at ingest; records missing the minimum
   (`location`, `price`, `hours`) are flagged `confidence=inferred` and held for curation,
   not shipped as verified.
4. **Enrichment.** Weather, geocoding, and distance are materialized at ingest (cheap, batch,
   idempotent) so the engine's query path is purely lookups + math, not network calls.
5. **State.** The catalog is a versioned dataset with a migration layer for schema changes;
   the engine reads a *fixed snapshot per query* (immutable within a request), which makes
   scoring deterministic between queries and simplifies testing. Point-in-time snapshots are
   cheap (an append-only log keyed by `activity_id`).

This materializes the external-data risk *out of the query path*, and leaves the engine as a
pure, deterministic transformer over a known dataset — the right place to be for a small team.

---

## 11. Standing decisions & alternatives rejected

| Decision | Choice | Alternatives rejected | Why |
|---|---|---|---|
| Matching model | Two-tier (hard gates + soft score) | One weighted score for everything; filters only | Gates needed for nonsense; ranking still required |
| Budget enforcement | Hard gate when `max < user budget`; soft when `max >= budget` | Purely soft scoring | A $99.99 item under a $10 budget has no business being ranked #1 |
| Weather | Hard gate on `avoid_*` rules, soft score for comfort | Weather only a soft signal | Weather is the differentiator; but still never drop to "blind" on total missing |
| Missing weather | Downgrade to soft + degrade envelope | Drop weather constraints entirely | `avoid_*` still matters to the user; just can't gate on it |
| Distance | Decay score + hard gate at radius | No hard distance gate | Prevents "all results 300 km away" for a 5 km radius |
| Fabricating data | Never fabricate | (none) | Product honesty is a core requirement |
| Determinism | Immutable per-request dataset snapshot | Dynamic live scoring within a query | Testing + deterministic ranking |
| Source failures | Drop slow source, don't block | Retry-forever on flaky provider | Small team; flakiness must not stall the product |

---

## 12. Open questions (for later cards)

1. **Concrete weather temperature floors** per activity class — need calibration data or
   agreed safe defaults (heat/cold). Scout's research suggests ~21–27°C comfort band; exact
   floors are a config value.
2. **Which weather provider** to integrate first (NWS for the Ottawa-Gatineau area, with a
   fallback)? Requires Eric's geography call.
3. **The activity-catalog source of truth** (curated vs provider vs user) and its ownership.
4. **Top-N / page size** and the "no results" empty UX — product decision, owned by
   product/Concierge.
5. **Multi-provider weighting** for the catalog; currently assumed single provider + curated.

---

## 13. Verification & tests

This ADR is the contract. The matching engine is testable end-to-end against a *synthetic*
dataset generated for any of the constrain cases:

- **Gating tests** — cost/time/distance/weather each as a hard gate (cases where the
  activity is excluded and appears in `unmet`).
- **Scoring tests** — known-tie / ranking-order cases (e.g. free beats paid; closer beats
  farther among equals; indoor beats outdoor on heavy rain).
- **Degrade tests** — no weather data, stale weather, empty catalog, one-source-down,
  circuit-opened provider.
- **Determinism tests** — identical dataset + request → identical ranked output, within float
  tolerance.

The ingest pipeline materializing a deterministic test dataset is the API boundary the
tests exercise, so engine logic is independent of network calls.

---

*Design by Forge (Principal Software Architect), 2026-10-21. Accepted for implementation;
no external facts beyond Scout's labeled research are referenced here. Verifiable only by
running the tests against the generated dataset.*
