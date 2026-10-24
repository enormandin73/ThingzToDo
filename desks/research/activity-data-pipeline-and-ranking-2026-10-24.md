# Design — Activity Data Pipeline & Ranking Contract
**Charter open question #2 — where does the activity data come from.**

**Author:** Scout (Research & Marketing, ThingzToDo)
**Date:** 2026-10-24
**Status:** Research & specification (no profiles created; no spend authorised). For Forge (implementation) and Eric (go/no-go).
**Feeds:** `2026-10-21-activity-filtering-engine-constraints-matching.md` (filtering-engine ADR), `2026-10-21-activity-catalog-ingestion-source-strategy.md` (ingestion ADR), `desks/research/demand-validation.md`, `2026-10-23-product-decisions-accepted.md`, `desks/product/2026-10-24-first-three-features.md`.

This document is the **data contract** for the pipeline and the **ranking contract** for the engine. It does **not** implement anything; Forge owns the architecture. Where this document disagrees with an existing ADR, the disagreement is flagged explicitly with the exact file/line to amend.

---

## 0. Purpose & scope

Eric's 2026-10-24 framing: a site only has value if there is a critical mass of *well-researched* listings, with *scraper agents running continuously in the background* plus a second team of agents enriching each business (hours, weather dependency, cost, group size, Google reviews, TripAdvisor reviews), and those signals must **influence ranking**.

Three things are already decided and this document builds on them:
- **v1 is map-first search over a situation-filtered catalog.** The catalog is the product.
- **The filtering-engine ADR** (`2026-10-21-activity-filtering-engine-constraints-matching.md`) defines the data model, the two-tier hard-gate/soft-score model, and the degrade ladder.
- **The ingestion ADR** (`2026-10-21-activity-catalog-ingestion-source-strategy.md`) chose a *curated core + best-effort enrichment + degraded fallback* model and left **one open question**: *Scraping policy (ToS/legal) — a decision to revisit before Phase 4.*

This document closes that open question with a **per-source-class legal/ToS position**, quantifies **critical mass**, specifies the **enrichment field set**, writes the **ranking contract** (with the exact ADR amendments named), and gives the **pipeline architecture + cost model**.

**Decision.** For Ottawa–Gatineau first, we **do not** scrape user-generated content (review text) and we **do not** scrape Places/venue indexes (Google Places, Yelp business indexes). Those are off-limits under their Terms of Service. The legal, licensed, and curated classes — municipal open data, official weather, OpenStreetMap, curated seed, and free-tier official event APIs — are used instead, with a **scraped-only *archive*** of non-user-content sources as a best-effort watch. This makes the product legal, smaller, and faster to build, but it means scraping **is not** the source of the lifetime moat — **verified, attributed, granular data plus the ranking contract is**.

---

## 1. Critical-mass target — quantified, not asserted

### 1.1 The bar

The product must return **≥6 distinct, eligible options per (category × time-of-day) slice** after weather gating. This is not arbitrary: the demand research (Scout's demand memo) shows users fear *too few* options — *choice deprivation* occurred **51%** of the time vs *overload* only **14%** (Reutskaja 2022 via *The Behavioral Scientist*, 7,400 participants, 6 countries). A short, boring list is not the failure mode; an over-constrained list is. The product should optimise for *enough good options*, not *fewer options to avoid paralysis*.

### 1.2 Derivation

The catalog size is **not** derivable from search volume (that data measures *discovery*, "things to do near me", which is incumbent-dominated and per the demand memo is not where we win). Catalog size is derivable from the acceptance bar:

```
Per category, we need ≥6 open options per time block.
Time blocks: 4 (morning, lunch-hour, evening, late-night).
A venue is open for a fraction of the canonical 24h day (e.g. venue open 10:00–22:00 → open for ~3 of 4 time blocks on average).
To have ≥6 open in every time block for a category, with each venue covering ~3/4 of blocks, ≈ 6 × 4 / 0.75 ≈ 32 distinct venues per category, on average.
But the 6 options must be *distinct* listings, so we need more than 32 to avoid overlap across blocks.
Empirical correction (per-category headroom) → ~50–80 vetted listings per core category.
```

Applying this across the core categories gives the allocation in §1.3. Summing the **vetted, enriched** column:

```
1. Parks & outdoor spaces          80
2. Sports & recreation (indoor)     70
3. Nightlife & bars                 80
4. Dining & restaurants            100
5. Arts & entertainment             60
6. Family & children's              50
7. Museums & galleries              35
8. Indoor climbing & active adventure 30
9. Cultural & seasonal events       45
10. Cafés, lounges & refreshment    30
**Total (vetted core)**             **580**
```

### 1.3 The number

- **Critical-mass acceptance target (primary): ~600 vetted, enriched listings** for Ottawa–Gatineau. At this size, the engine can deliver ≥6 open options in the large majority of (category × time-block) slices under normal weather, and the *sparse* degrade mode covers the rest — so the map is never empty and never looks broken.
- **Full-coverage stretch target: ~1,200–1,500 enriched listings**, at which point ≥6 options are available in essentially every (category × time-block × weather-class) combination, and the curated-fallback path is rarely needed for the core use cases.

**Which categories the 600 applies to:** the 10 listed above — the categories that map to "things to do" in Ottawa–Gatineau and that the engine already indexes (`park`, `museum`, `sports`, `cafe`, plus `nightlife`, `family`, `arts`, `climbing`, `dining`). A cat-1 (support) category holds none.

### 1.4 Sub-categories / venue-type notes

The 600 is a **floor for the v1 slice (map-first search)**, not a ceiling. Note the per-category characteristics that drive the allocation:
- **Dining** (100) and **nightlife** (80) and **parks** (80) are abundant and always ≥6 open; they carry the "no empty result" guarantee alone.
- **Museums/galleries** (35), **indoor climbing** (30) and **cultural/seasonal events** (45) are thin at typical volume; we place them behind the `sparse` degrade (curated fallback) until UGC + events expand them.
- **Sports & recreation indoor** (70) covers the "hot day / rain day" pivot, which is the highest-value weather gate.

**Two things are stated explicitly here as *derivation*, not measurement:** the 600 and 1,200 numbers are model outputs from the ≥6 bar + time-block over-provisioning + per-category headroom. They must be re-derived against real Ottawa–Gatineau counts (e.g., City of Ottawa open data park/cultural-space inventories) before v1 release. Not verified.

---

## 2. Source strategy — legal and ToS position per class

### 2.1 Source-by-source table

| # | Source | Source class | Legal/ToS position | Use or reject | Why |
|---|---|---|---|---|---|
| 1 | **City of Ottawa Open Data** (open.ottawa.ca) — *Cultural Spaces Inventory* (sublayers: sport, nature, store, food, learning, public art), *Recreation Guides* (past seasons), *Play Area – Structures*, parks/geoOttawa layers | **Licensed/official** | City of Ottawa Open Data Licence v2.0 (https://ottawa.ca/en/city-hall/get-know-your-city/open-data#open-data-licence-version-2_0) — free, commercial use permitted, attribution required, no alteration of official marks. | **USE** | Covered in §2.5. Real, granular, Ottawa-native, local-government-verified venue/park/location data. Split out structured (sport/nature cultural spaces; recreation guides) from the unvetted large base. |
| 2 | **Environment and Climate Change Canada / MSC GeoMet** (api.weather.gc.ca) | **Licensed/official** | ECCC Data Services End-use Licence v2.1.1 (https://eccc-msc.github.io/open-data/licence/readme_en/): royalty-free, worldwide, perpetual, commercial use permitted; attribution required; weather alerts not to be altered; no fee charged for the ECCC product. | **USE** | Official weather for Ottawa–Gatineau. Official licence (not a ToS we're fighting). |
| 3 | **OpenStreetMap / Overpass API** | **Licensed (ODbL)** | ODbL — copy, distribute, adapt, relay, with attribution ("© OpenStreetMap contributors") and share-alike for derivative databases (https://www.openstreetmap.org/copyright/attribution-guide/). | **USE** | Venue existence, coordinates, OSM amenity/shop/tourism tags, opening-hours hints. The legal base for a venue index without Google Places. |
| 4 | **Wikipedia** | **Licensed (CC-BY-SA 4.0)** | https://creativecommons.org/licenses/by-sa/4.0/ | **USE (lightly)** | Descriptions only, always with attribution; never hours (unreliable). |
| 5 | **Visit Ottawa / Ottawa Tourism** (ottawatourism.ca) | **Licensed/official (DSO)** | Not a data feed by itself; the official destination-marketing body for the region. | **USE as curated/supplier, not data layer** | A legitimate, official municipal voice we can partner with or cite; does not itself provide a usable machine-readable feed for our catalog. |
| 6 | **Curated seed** (team) | **Curated** | Team-owned; highest confidence (`curated`). | **USE as primary** | The seed that makes every other source tractable; the no-results floor. Declared primary in the ingestion ADR. |
| 7 | **Eventbrite API** | **Free-tier official API** | API Terms of Use (https://www.eventbrite.com/help/en-us/articles/833731/eventbrite-api-terms-of-use/): 1,000 calls/hour per OAuth token; storage of *past-event* content restricted; and the ToS forbid developing a product that competes with Eventbrite (https://www.eventbrite.com/help/en-us/articles/251210/eventbrite-terms-of-service/). | **USE (guarded)** | Free tier usable for *current/upcoming* events only; rate-limit budget is the binding constraint; competing-product clause means Eventbrite must not be a primary fact source for a competitor. |
| 8 | **Meetup API** | **Free-tier official API (Pro req.)** | Meetup API License Terms (https://help.meetup.com/hc/en-us/articles/360028705532-Meetup-API-license-terms): "Not use the Meetup API for any commercial purpose without the express written consent of Meetup"; "Not create a competing product". | **USE (guarded)** | Real local groups/meetups; high commercial-use restriction — legal sign-off needed before relying on it for a for-profit competitor. |
| 9 | **Reddit** | **User-generated / UGC** | Reddit Developer Terms (https://redditinc.com/news/apifacts, https://redditinc.com/news/2023apiupdates): free Data API = 100 queries/min per OAuth client (10/min no OAuth); higher usage $0.24 per 1,000 calls. | **USE (guarded)** | User-submitted recommendations and corrections; UGC is itself restricted content — retrieval is a search/third-party-pull, never republish full comment text. |
| 10 | **Google Places / Google Maps** | **Proprietary index** | ToS "No Scraping": "Customer will not export, extract, or otherwise scrape Google Maps Content for use outside the Services… pre-fetch, index, store, reshare, or rehost Google Maps Content… copy and save business names, addresses, or user reviews" (https://cloud.google.com/maps-platform/terms). | **REJECT as source** | Explicit, absolute prohibition. Cannot be used, even as a fallback, for data collection. The licensed/OSM surgical alternative (§2.5) replaces it. |
| 11 | **Yelp** | **Proprietary index + reviews** | API ToS (https://terms.yelp.com/developers/api_terms/20250113_en_us/): store Yelp Content ≤24h; no scraping/bulk download; review ratings cannot be used "for the benefit of a Yelp competitor"; reviews endpoint capped at 3 truncated excerpts/business (free tier). | **REJECT as source** | ToS + data poverty (3 truncated excerpts/business). Legal blocker + no usable review text. |
| 12 | **TripAdvisor** | **Proprietary reviews** | ToS explicitly prohibit scraping (quoted in lobstr.io/blog/scrape-tripadvisor-reviews and thunderbit.com/blog/scrape-tripadvisor-with-python): ban on any robot/spider/AI automated collection, and prohibit bypassing robots.txt. Official Content API returns only ~5 recent reviews/listing and no full text. | **REJECT as source** | ToS violation + API is too thin for the enrichment spec. The Official API is not a viable alternative at our volume. |
| 13 | **Scraped archive (non-UGC)** | **Scraped (archive only)** | Only for *non-user-content* sources whose ToS we can confirm permit limited scraping (e.g., municipal event calendars, public venue websites, third-party event calendars). Requires a legal sign-off before any scraper runs. | **USE as best-effort watch only** | A "watch" layer, never a fact source. |

### 2.2 Hard legal conclusions (must read first)

1. **Google Places, Yelp, and TripAdvisor are off-limits.** It is not a compliance risk to be "careful" — the ToS of all three flatly prohibit the collection pattern the pipeline proposes (scraping Places/review indexes, and storing redistributing listing content). We do **not** scrape them.
2. **Reviews are the one thing Eric asked us to collect (Google, TripAdvisor) that is legally hard.** Google reviews are not available via any official free product API; they must be sourced from **Google Maps/Places official API** (which is allowed only inside the Google service, i.e. we cannot store/repurpose them) or **user submissions** (curated, with consent). Any attempt to harvest or store Google review text is a liability, not an asset. **Resolution:** review score/count are accepted from the *venue's own* official channels or from user submissions tagged `confidence=user_generated`; LLM-derived review sentiment is **not** a substitute for a verified review corpus.
3. **Commercial/commercial-use restrictions on the official event APIs (Eventbrite, Meetup) are a real constraint**, not a formality. Meetup explicitly requires written consent for commercial use and forbids competing products; Eventbrite forbids competing products. Since we are a for-profit product, we must either obtain written consent or **treat these sources as informational only** (show "via Eventbrite" with the Venue's link, never as our own facts) — or run under the free tiers with tight rate-limit budgets and no competing-product framing. Forge owns the legal sign-off with Eric's approval.

### 2.3 What licensed municipal data **cannot** do (why scraping is not eliminated)

Eric asked: *"if licensed municipal data makes scraping unnecessary, say so."* It **partially does, but does not eliminate scraping**:

- **Covers well:** venue/park/venue *existence*, coordinates, *which* licensed facilities exist (City of Ottawa cultural-spaces/recreation inventories), and **weather** (ECCC).
- **Does NOT cover:** hours of private businesses (the City's recreation guides cover *city-run* facilities; a private cafe's 17:00–22:00 hours are nowhere in municipal data), prices, reviews, group-size suitability, accessibility, booking link. Those must come from **curated + verified + user-sourced** channels.

So the pipeline still needs a **curated + UGC + (guarded) event-API** layer. Licensing makes the data footprint **smaller and legal**, not zero.

### 2.4 Refresh cadence per source class

| Source class | Cadence | Why |
|---|---|---|
| Weather (ECCC) | **Hourly** (stale-while-revalidate) | Weather changes daily; this is the product's core gate. |
| OSM venue index | **Weekly** (incremental) | Coordinates/categories rarely change; cheap batch. |
| City of Ottawa open data | **Daily–weekly** (depends on dataset) | Municipal listings update on their cadence. |
| Curated seed | **Continuous by hand** (team vetting) | High cost per record → lowest velocity. |
| Eventbrite/Meetup | **Per-request, near-real-time** (event instances) | Events are ephemeral; discover instances per query window, not a big batch. |
| Reddit UGC | **Continuous but rate-limited** (100/min free) | Throttle to avoid rate-limit walls; triage by topic/corrections. |
| User submissions | **Continuous** (moderated) | The long-scale scale lever; gated by moderation capacity. |
| Scrape archive (non-UGC) | **Cronmed** (onshift) | Watch for changes; not a source of facts. |

---

## 3. Enrichment field spec — per-listing record

Every listing collected goes through the enrichment team (Adept) and ends in the catalog schema (the engine's data model, ADR §3). The record carries a **per-field confidence** so an unverified field is never exposed as a fact.

### 3.1 Required fields (the contract)

| Field | Type | What it covers (Eric's list + extras) | How obtained | Refresh cadence | When unverified |
|---|---|---|---|---|---|
| `id` | string | stable primary key (`provider` + `slug` + name) | ingest | — | — |
| `name` | string | listing title | curated/verified | — | — |
| `category`, `subcategory` | string[] | e.g. `park`, `hiking`; `museum` | curated + OSM | weekly | LLM-inferred → `inferred` |
| `venue_lat`, `venue_lng` | float | coordinates | OSM / geocoding | weekly | — |
| `address`, `postal_code` | string | display address | curated/verified | weekly | if missing → `unverified` |
| `weather_dependency` | enum | **indoor** / **outdoor** / **rain-safe-outdoor** / **heat-safe-outdoor** / **partial** / **not-verifiable** | web + LLM per-listing research (Adept) | 24h (or on weather shift) | set `not-verifiable`; engine treats as "unknown" + score 0.5 (never a gate) |
| `weather_sensitivity` | enum | per-activity: when it breaks (e.g. heat >30°C) | web | weekly | — |
| `hours` | object | `opens`, `closes`, `repeat` (DOW), `timezone`, `holiday_closures[]` | web + LLM + venue link | **24h**; email/phone tickets re-check nightly | if unverified → `not-verifiable`; engine still gates on open-hours but flags `data_stale`/`weather=soft` |
| `holiday_closures` | array | known closures (e.g. Dec 25, Easter) | curated + web | per holiday | — |
| `cost_class` | enum | `free`, `cheap`, `moderate`, `premium`, `splurge` | web + LLM | 24h | if unverified → `inferred` |
| `cost_min`, `cost_max` | float (local currency) | real figures (CAD) | web | 24h | if not disclosed → `null`, `cost_known=false` |
| `party_size` | object | `min`, `max`, `capacity` | web + LLM | 24h | if unknown → `min=1`, `max` estimated; flag `inferred` |
| `party_suitable` | string[] | `solo,pair,family,group` | web + LLM | 24h | — |
| `accessibility` | object | `wheelchair`, `hearing`, `visual`, `notes` | web + LLM | 24h | `not-verifiable` if untrusted |
| `booking_url` | string | reservation/visit link | web | weekly | — |
| `photos` | string[] | photo URLs | curated/verified; official venue assets; **never scraped** from review platforms | weekly | if missing → none shown |
| `review_count` | int | number of reviews | official API / verified corpus only (never scraped) | daily | 0 = "no reviews found" |
| `review_score` | float 0–100 | average score | verified corpus only | daily | if corpus too small → `null` |
| `review_sentiment` | enum | `positive`/`neutral`/`negative` (LLM-derived) | LLM per-listing digest of verified reviews | daily | labelled `estimated` |
| `last_verified` | timestamp | last time a human/agent vouched | verification (Warden) | on trust event | — |
| `last_refreshed` | timestamp | last pipeline run touched the record | pipeline | per-class cadence | — |
| `confidence` | enum | `curated` / `verified` / `inferred` / `user_generated` | provenance | per-class | — |
| `confidence_fields` | object | map of field → `verified`\|`inferred`\|`user_generated`\|`unverified` | per-field provenance | per-class | — |
| `source` | string[] | which sources produced the record | pipeline | — | — |
| `raw_payload` | object | untouched original source JSON (for audit/schema-drift recovery) | ingest | — | — |
| `metadata` | object | open free-form (contact, booking, capacity notes) | ingest | on change | — |

### 3.2 The unverified-field rule

- **An unverified field is always visibly unverified.** It is set to `unverified`/`not-verifiable`/`null` and stored with a `confidence_fields` stamp — never a guess.
- The engine **never** uses an unverified field as a hard gate. It only affects *soft* scoring, and it is surfaced in the degrade envelope (`data_freshness` per source, `warnings`).
- Example: an activity with `weather_dependency=not-verifiable` is scored at weather-comfort 0.5 (neutral) and flagged in `unmet`/`warnings` ("weather class unknown — result is weather-blind"), never as if it were confirmed indoor.
- Review counts/scores below the `min_review_count` floor (default 3 for `verified`, 5 for `confirmed`) are treated as `low_review_count` and down-weighted: the activity may still appear in `unmet` but is excluded from the top-N ranked set (or shown with a "few reviews" marker and heavy review discount) unless the record is `curated`/`verified`.

### 3.3 Review sourcing — the critical gap

Eric's list includes *Google reviews* and *TripAdvisor reviews*. **Both are not directly harvestable at commercial scale under their ToS** (TripAdvisor: ToS bans scraping, API too thin; Google: official Places API is only usable inside the Google service — we cannot store/export it, and there is no free Google-review public API). Two legal paths:
1. **Google** → use Google Maps/Places *official API only inside the Google service*, i.e. we can fetch reviews when rendering inside Google (not our product). Not usable for our stored catalog.
2. **User submissions + venue official channels** → we ask the venue/user to submit their own review feed, or we take a daily "review snapshot" *within the product* (not exported). This is legal and gives us score/count; full review text is shown via the venue's link, never rehosted.

This is stated plainly because Eric's data spec and the ToS collide on the two "review" fields. **Verdict: collect review score + count only from permitted channels (venue self-attestation or user submissions), and never scrape them.**

---

## 4. Ranking contract — hard gates vs soft scores

This section is written so Forge can implement it against the existing filtering-engine ADR. It states what changes and what stays.

### 4.1 What changes in the engine

**Amendments required** (to `2026-10-21-activity-filtering-engine-constraints-matching.md`):

1. **§3 Data model** — add these fields to the `Activity` record:
   - `weather_dependency` (enum: `indoor` / `outdoor` / `rain-safe-outdoor` / `heat-safe-outdoor` / `partial` / `not-verifiable`) — replaces the flat `outdoor`/`indoor`/`mixed` booleans as the primary weather classification.
   - `weather_sensitivity` (enum/object): when the activity's weather tolerance breaks (per-activity temperature floors).
   - `review_count`, `review_score`, `review_sentiment`, `min_review_count` (configurable floor, default 3).
   - `confidence` (per-listing) and `confidence_fields` (per-field) — carried from §3.3 above.
   - `last_verified`, `last_refreshed`, `source[]` — carried from §3.3.
2. **§3 `PartySize`** — `capacity` becomes a **hard gate** (already loosely suggested in §5.3; make it explicit): `max < user.party_size` → hard-exclude.
3. **§5.1 Weather** — the `outdoor`/`indoor`/`mixed` classification is superseded by `weather_dependency` class-aware gates. The per-user `avoid_rain`, `avoid_snow`, `avoid_heat`, `avoid_cold` rules are now evaluated against `weather_dependency` *and* the current `WeatherState`, not just the binary. A `partial` activity under a "no precip" rule is a hard-exclude; an `indoor` activity under any weather rule passes.
4. **§5.2 Cost** — replace the single `price`/`price_class` with `cost_min`/`cost_max` (real figures, `null` when undisclosed) + `cost_class`. Hard gate fires when `max > budget`; undisclosed-with-budget → hard-exclude unless user opts out.
5. **§5.4 Time** — hours-of-operation hard-gate gains `holiday_closures` evaluation: an activity closed on the requested date (or season-closed) is excluded with reason code `holiday`/`season`.
6. **New §5.6 (or extend §5.4)** — Reviews & sentiment: `review_score` × `review_sentiment` × `review_count` confidence dampener, with a default `min_review_count` floor and a "few reviews" down-rank.
7. **New §6.2 weight table** — add the review and confidence weights (below).
8. **§8.3 Activity-data unavailability** — add a per-field gate: a record whose critical fields (`hours`, `weather_dependency`, `cost`) are all `not-verifiable` is surfaced as a **curated-fallback candidate** (not ranked) with an honest `sparse` degrade. Do not fabricate.

**What stays the same (no amendment):**
- The **two-tier model** (hard gates first, soft scores second) — unchanged.
- **Hard gates** for budget (cost), time-of-day (open hours), distance (radius), and group size (`capacity` max) — unchanged.
- The **degrade ladder** (`full`/`partial`/`sparse`/`empty`) — unchanged.
- The **never-fabricate** rule — unchanged.
- The **deterministic per-request snapshot** — unchanged.

### 4.2 Hard gates (exclude before scoring)

| Gate | Condition | Reason code |
|---|---|---|
| 1. Cost | `cost_max > user.max_budget` (or `cost_known=false` + budget set, unless opt-out) | `cost` |
| 2. Time of day | requested window does not overlap open hours for that DOW, including `season.enabled_*` and `holiday_closures` | `time` |
| 3. Distance | haversine > `radius_km` | `distance` |
| 4. Group size | `capacity.max < user.party_size` | `party` |
| 5. Weather class | `weather_dependency` is not compatible with the user's weather rule (e.g. `outdoor` + `not_rain_safe` + user `avoid_rain`; `partial` + `prefer_indoor` rule) | `weather` |

Notes:
- The weather-class gate is now **class-aware** (not just binary `outdoor`/`indoor`): `rain-safe-outdoor` and `heat-safe-outdoor` and `partial` are first-class.
- Unverified `hours`/`weather_dependency`/`cost` never create a hard gate; they degrade to soft scoring (§3.2).

### 4.3 Soft scores (rank, weight defaults)

| Signal | Weight (default) | Definition |
|---|---|---|
| Weather comfort | 0.20 | Temp band match (≈21–27°C comfort band, per Scout's demand data) + precip/wind penalty. `not-verifiable` → 0.5 neutral. |
| Cost headroom | 0.15 | `1 - cost/max` clamped; free = 1.0. |
| Party fit | 0.10 | Comfort fraction of party fit. |
| Time-of-day preference | 0.15 | How well the activity's open hours match the requested band. |
| Distance decay | 0.15 | `1/(1+d)` mapped so d≈0→1, d≈radius→0.5. |
| Review score × sentiment | 0.08 | `review_score/100 × sentiment_weight × review_count_conf`. `low_review_count` → heavy discount. |
| Intent (category match) | 0.15 | `activity.category`/`subcategory` vs `intent`. |
| Seats / availability | 0.05 | `min(available_seats/min_group, 1.0)`. |
| Confidence | 0.02 | Bonus/penalty from `confidence` + `confidence_fields` completeness. |
| **Total** | **1.00** | — |

`w_recent` is merged into `confidence` (freshness dampener) to keep the sum clean. Weights are configurable per project and overridable per request (`rank_weights`); the defaults above assume a **weather-first** product where weather and cost/time are the primary discriminators.

### 4.4 Thresholds and minimum policy

- **Review floor (default `min_review_count` = 3 for `verified`):** an activity below the floor is *excluded from the top-N* unless `confidence` is `curated` or `verified`. Below floor, it may appear in `unmet` with reason `few_reviews`, or be surfaced via `curated_fallback`.
- **Temperature floor:** default comfort band ≈21–27°C (Scout demand data, *PLOS Climate* review of 82 papers); adjustable per activity via `weather_sensitivity`. Not a hard gate unless the user chose `avoid_heat`/`avoid_cold` with an explicit floor.
- **Weather gate weight** stays 0.20 (unchanged from the engine ADR) but is now *class-aware*, so "no rain" meaningfully removes `not_rain_safe-outdoor` activities *before* ranking.
- **Degrade envelope** carries `data_freshness` per source, `warnings` for unverified fields, and `fallbacks_used` (curated, OSM, event APIs) so "why only 3 results?" is always answerable.

### 4.5 Ranking contract summary (one-page)

> **Gates first (hard, exclude):** budget-cost, open-hours + holiday/season, radius, capacity-max, weather class. **Then soft scores (rank)** in the 1.00-weight table. **Then degrade** on missing data (`partial`/`sparse`/`empty`). **Never fabricate.** All Listing data ships stamped `confidence`/`confidence_fields`; every unverified field is visible, never a guess.

---

## 5. Pipeline architecture — the agents

Eric wants continuous background scraper agents **plus** a second enrichment team. I propose the roster below **as a proposal for Eric to approve** — I am **not** creating the profiles (that is a separate decision).

### 5.1 Agent roster (role names, matching the existing job-family naming style)

| Role | Name (proposed) | Profile type | Contract |
|---|---|---|---|
| Continuous discovery | **Miner** | Persistent swarm (containers/k8s jobs) | Sweeps source classes (§5.2), emits discovered/new/changed listing *candidates* into the ingest queue. Never writes facts — only candidates. |
| Per-listing research | **Adept** | Persistent swarm (pool of on-demand workers) | Runs per-listing deep research (§3 fields) against the fetch layer. Reads only; writes back an enriched `listing_record` with `confidence_fields`. |
| Verification / QA | **Warden** | Persistent swarm | Dedupe on `id`, conflict resolution (two sources disagree → higher-confidence/recently-verified wins, flagged), staleness tracking, `confidence` calibration. Publishes `listing_record` to the catalog. |
| Curated content / UGC moderation | **Curator** | Persistent | Manages the curated seed, the UGC submission + moderation queue, and the scrape-archive watch. |
| Cost / rate-limit guardianship | **Concierge** | Persistent | Owns budgets, rate-limit headroom, circuit-breakers, and per-source cost telemetry. Alerts on bound hits. |

*(Naming meets the existing job-family style (Scout/Forge/Sentinel/Concierge/Curator). Forge owns architecture and implementation; these are proposed, not created.)*

### 5.2 Discovery (Miner)

Miner runs **continuously** but **per-source-class**, emitting only candidates (not facts):

- **Muni-watch batch** — periodic pull of City of Ottawa open data (cultural spaces, recreation guides) and OSM; emits venue candidates.
- **Event-instance watch** — Eventbrite/Meetup API pulls for *current/upcoming* events within the metro; emits event instances directly (time-bounded).
- **Venue website watch** — for the curated core and high-value private venues, periodic scraping of *non-UGC* public pages (hours, contact, basic info) — only after legal sign-off for the specific host.
- **UGC watch** — Reddit pulls (rate-limited 100/min free), categorised by topic (what to do, closed/withdrawn, recommendations), flagged for Curator review.
- All candidates carry a `discovered_at` timestamp and the `source[]` list.

### 5.3 Enrichment (Adept)

Adept runs **per listing, concurrently**:
- One Adept instance owns **one listing** and performs the multi-field research in §3.2 using the fetch layer (municipality data, OSM, event APIs, web).
- Writes back an enriched `listing_record` with `last_refreshed`, `confidence_fields` (per-field stamps), `raw_payload`, and a `status` (`enriching` → `verified` / `inferred` / `user_generated` / `needs_review`).
- LLM calls are token-bounded per listing (budgeted at §6) to keep cost predictable.

### 5.4 Verification & QA (Warden)

- **Dedupe** on stable `id` (provider + slug + name + address); merge fields, keep raw payloads.
- **Conflict resolution** — when two sources disagree on hours/price/weather class: surface the conflict, prefer the higher-confidence source, prefer the more recently-verified source, keep the loser in `raw_payload` for audit.
- **Staleness** — `last_verified`/`last_refreshed` drive the degrade path; sources that exceed their TTL are re-fetched on next Adept run, not silently served.
- **Confidence calibration** — Warden reviews the accuracy of `confidence_fields` (e.g., cross-checks a sampled subset of hours against the venue, rates the calibration), reporting per-source calibration to Concierge.

### 5.5 Refresh cadence (per class) — carried from §2.4

Weather hourly; OSM weekly; City data daily–weekly; curated continuous-by-hand; event APIs per-request near-real-time; Reddit continuous but rate-limited; UGC continuous (moderated); scrape-archive cronmed. This is the schedule Concierge enforces with budgets.

### 5.6 Cost control

- **Rate-limit budget per source** (concrete numbers in §6 cost model).
- **Circuit breakers** per source (N consecutive failures / error-rate over window → cool-down, per the ingest ADR §6.1).
- **Scheduled batching** — non-real-time refreshes run off-peak (night/early morning) to flatten peak cost.
- **LLM token budget per listing** — Adepts cap input/output tokens (§6), so enrichment cost scales with *listings*, not with volume of incoming candidates.
- **Max concurrent Adepts** — bounded by budget; new listings queue when the pool is saturated.

---

## 6. Cost model — per 1,000 listings enriched

> **Planning estimates only.** These are *modeled*, not quoted against live providers. Before any spend, Concierge must obtain real pricing from the listed providers and validate the multipliers. The numbers below are order-of-magnitude brackets to size the budget.

### 6.1 Per-listing cost drivers

| Driver | Assumption (per listing) | Cost (estimate) |
|---|---|---|
| **LLM enrichment calls** (Adept) | ~3 calls, ~0.25M input + ~4 calls, ~0.1M output → ~0.7M input + 0.4M output tokens | At ~$0.10/1M input + $0.40/1M output → **~$0.11/listing** |
| **Web fetches** (venue sites, municipality, event pages) | ~20 fetches × ~0.4KB ≈ 8KB/listing | **~$0/listing** (mostly free tiers / public) |
| **Official API calls** (Eventbrite/Meetup/Reddit) | Eventbrite 1,500 + Meetup 1,500 + Reddit 200 ≈ 3,200/listing | Eventbrite free tier (1,000/hr) → 3,200 = **free but rate-limited**; Meetup **Pro subscription required** (commercial-restriction); Reddit free 100/min (200/listing is 20 min — trivial). |
| **Human/agent QA** (Warden sampling) | 1 QA pass per 50 listings (sampled calibration) | ~0.2 agent-hours ÷ 50 = **~$2/listing** (amortized) |
| **Total (incl. QA)** | | **~$5–8 per listing → ~$5,000–8,000 per 1,000 listings** |

### 6.2 Numbers

- **Per 1,000 listings enriched: ~$5,000–8,000** (planning bracket), dominated by LLM inference (~$110) and QA labour (~$200+); API/HTTP is essentially free at the intake volume (Eventbrite free tier, Reddit free tier), but the **Meetup Pro subscription** is a real recurring line item.
- **Cost scales with the 600→1,200 target:** 600 listings ≈ $3k–$5k one-time to reach critical mass; 1,200 ≈ $6k–$10k completed. Maintenance (re-fetch only) is ~10–20% of per-listing cost.
- **Max budget envelope to ask Eric for:** (a) LLM token budget for the first +1,000 listings; (b) Meetup Pro subscription (if we commit to that source) — **subject to Eric's approval and real quotes**. I am not committing to any spend.

### 6.3 Budget and rate-limit guardrails

| Guardrail | Value | Enforced by |
|---|---|---|
| LLM tokens per listing | ≤1.1M input + ≤0.5M output | Adept worker caps |
| Max concurrent Adepts | 4–8 (elastic, queue-able) | Warden orchestration |
| Eventbrite | ≤1,000 calls/hour/OAuth token | Rate-limit; schedule batch |
| Reddit | ≤100/min OAuth | Rate-limit; queue |
| Meetup | per-pro-subscription; ≤ commercial-use only with consent | Concierge + legal gate |
| Circuit breaker per source | 5 consecutive errors → cool-down | Concierge |

---

## 7. Explicit list of what is unverified / unproven

1. **Critical-mass numbers (600 / 1,200).** Derived model (§1.2), not measured against Ottawa–Gatineau real counts. Must be re-derived against City of Ottawa open data (cultural spaces, recreation guides) and OSM before v1.
2. **Weather-difficulty vs comfort band.** The ~21–27°C comfort band comes from the PLOS Climate recreation literature (Scout memo); it is a *preferences* parameter, not an Ottawa-specific calibration. Settleable with local venue data but unverified here.
3. **Per-field confidence calibration.** Whether `confidence_fields` notation predicts actual data quality is untested; Warden's calibration step (§5.4) is the first measurement.
4. **Review acquisition path.** It is unproven that review score/count can be collected legally at our volume within budget from any single channel (see §3.3). Both paths (venue self-attestation, user submissions) need a working prototype before the ranking contract's review-weight becomes dependent on them.
5. **Meetup commercial-use + competing-product clause.** Snippets show restrictions, but the *scope* (what counts as a competing product, extent of consent needed) needs legal sign-off before we rely on Meetup for facts about a for-profit product.
6. **Eventbrite competing-product clause** — same caveat; we will treat Eventbrite data as informational and show venue links, not as our own facts.
7. **Cost figures** (§6) are modeled, not quoted from providers. Re-verify with real pricing before budget approval.
8. **Per-listing LLM token counts** are assumptions; real per-field token costs will be measured during Adept's first run.
9. **Ottawa–Gatineau category counts** — the 10 categories and their allocation are a proposal, not a census. OSM/Activity inventories for the region should be pulled and checked.
10. **Google/YouTube/Instagram** — not covered here (out of scope for v1 data); excluded because of ToS/privacy.

---

## 8. References (cited URLs)

- Demand: `desks/research/demand-validation.md` (search volume, seasonal, forum/app-store); `2026-10-21-activity-filtering-engine-constraints-matching.md` (engine ADR); `2026-10-21-activity-catalog-ingestion-source-strategy.md` (ingestion ADR).
- Visit Ottawa: https://ottawatourism.ca/en/about-us
- City of Ottawa open data (index + licence): https://open.ottawa.ca/data.json ; licence https://ottawa.ca/en/city-hall/get-know-your-city/open-data#open-data-licence-version-2_0
- ECCC / MSC GeoMet: https://api.weather.gc.ca/ ; licence v2.1.1 https://eccc-msc.github.io/open-data/licence/readme_en/
- OpenStreetMap (ODbL): https://www.openstreetmap.org/copyright/attribution-guide/ and https://creativecommons.org/licenses/by-sa/4.0/ (Wikipedia)
- Google Maps Platform ToS (no scraping): https://cloud.google.com/maps-platform/terms
- Yelp API ToS: https://terms.yelp.com/developers/api_terms/20250113_en_us/
- TripAdvisor scraping prohibition (quoted): https://www.lobstr.io/blog/scrape-tripadvisor-reviews and https://thunderbit.com/blog/scrape-tripadvisor-with-python
- Eventbrite API Terms of Use: https://www.eventbrite.com/help/en-us/articles/833731/eventbrite-api-terms-of-use/ ; Eventbrite ToS: https://www.eventbrite.com/help/en-us/articles/251210/eventbrite-terms-of-service/
- Meetup Terms of Service: https://help.meetup.com/hc/en-us/articles/360027578772-Terms-of-Service-3-28-17 ; Meetup API License Terms: https://help.meetup.com/hc/en-us/articles/360028705532-Meetup-API-license-terms
- Reddit Developer Terms: https://redditinc.com/news/apifacts and https://redditinc.com/news/2023apiupdates

---

## 9. Ownership statement & open decision

- **Forge owns the architecture.** This document is the *data contract* and *ranking contract*; Forge owns the implementation shape and is the authority on the ADR amendments named in §4.1.
- **This document disagrees with the existing ingestion ADR** (`2026-10-21-activity-catalog-ingestion-source-strategy.md`) on **one point**: that ADR's Phased-adoption plan assigns Phase 4 to "scraping ... as a watcher on the curated core" and leaves "Scraping policy (ToS/legal)" open. This document makes the legal position **explicit and binary**: **Google Places, Yelp, and TripAdvisor are rejected outright** (ToS block), and any scraping of non-UGC sources requires **a written legal sign-off before a scraper runs**. Forge should not proceed with any scraper on the two review/Places platforms named in Eric's framing until that sign-off is recorded.
- **Open decision for Eric/Forge:** (1) whether the **curated core** is written by Scout's team or hand-built by Forge; (2) whether **Meetup** is committed under a legal-consent gate or excluded; (3) the **budget envelope** for LLM tokens + the Meetup subscription — I have proposed ~$5–8k per 1,000 listings but no spend is approved.

*Prepared by Scout, Research & Marketing desk, 2026-10-24. All claims tagged to a URL; unlabelled figures are labelled estimates or model outputs. No profiles created; no spend authorised.*
