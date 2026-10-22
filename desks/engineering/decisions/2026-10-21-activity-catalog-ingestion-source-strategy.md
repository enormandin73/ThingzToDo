# Design — Activity Catalog Ingestion: Source Strategy & Failure Handling

**ADR:** `desks/engineering/decisions/2026-10-21-activity-catalog-ingestion-source-strategy.md`
**Owner:** Forge (Principal Software Architect)
**Date:** 2026-10-21
**Status:** Accepted (design decision) — this is the data-side counterpart to the filtering-engine ADR
**Feeds:** the activity catalog, the ingest pipeline, and the engine's candidate finder (ADR
`2026-10-21-activity-filtering-engine-constraints-matching.md`, §10)

---

## 0. Purpose & scope

ThingzToDo's recommendation engine is only as good as the catalog it is scored against. This
ADR decides **where activity data comes from** for a team with no budget and very few
engineers, and how we keep the product alive when those sources fail.

The four source archetypes on the table are:

1. **Curated** — a small, team-maintained list of high-confidence activities.
2. **Scraped** — automated extraction from third-party websites (event calendars, recreation
   listings, guides).
3. **Licensed** — a paid commercial data/vendor product (subscription or per-query).
4. **User-generated** — listings submitted by end users, moderated before publication.

The acceptance criteria are:

1. A **clear recommendation** (which source type feeds the product first), with **at least one
   rejected alternative**.
2. A **plan for handling external service failures** (flakiness, rate limits, outages).
3. A **note on how ingestion failures affect the product** (what the user sees).

Scope: this ADR covers *source strategy and the ingest pipeline*. It does not cover the UI
surface, the recommendation engine scoring, or deployment infra.

---

## 1. Decision summary (TL;DR)

| Choice | Detail |
|---|---|
| **Primary source** | **Curated** — the team owns a seed list of verified activities for the local area. Highest confidence, fastest path to a working product. |
| **Enrichment (best-effort)** | **Free-tier provider REST APIs** (events, recreations, calendars) — used to *add* coverage and *refresh* the curated list, never as a dependency. |
| **User contributions** | **User-generated** — added later behind a moderated submission flow (`confidence=user_generated`), throttled until moderation capacity justifies it. |
| **Rejected** | **Scraped-only** (brittle, high-maintenance, legal risk) and **Licensed-only** (kills the no-budget constraint; nothing ships until a paid account exists). |

The rule that governs everything below: **the product must never fabricate data it does not
have** — that is the core honesty guarantee behind the filtering engine's `never-fabricate`
rule (ADR §8.4, §9.1). Every external source is therefore treated as a *candidate supplier*,
not a *guarantor*, and its failures surface as degrade modes in the product.

---

## 2. The four source archetypes

| Dimension | Curated | Scraped | Licensed | User-generated |
|---|---|---|---|---|
| **Cost** | $0 (staff time) | $0 (tooling) | $$$ (subscriptions / per-query) | $0 (but needs moderation labor) |
| **Reliability** | High (team verifies) | Low (layouts change, pages die, rate limits) | High (vendor SLA, but paid) | Medium (depends on volunteer users) |
| **Maintenance burden** | High per record, low volume | Very high (selectors, sites, fauna) | Low once integrated | Medium (needs moderation workflow) |
| **Data quality** | High for entries we vouch for | Variable; poor schema, no guarantees | High, but coverage varies by geography | Variable; needs vetting |
| **Scale ceiling** | Bounded by team effort | Bounded by scraper fragility | Bounded by budget + geography gaps | Bounded by user volume + moderation capacity |

---

## 3. Per-source evaluation

### 3.1 Curated (recommended as primary)

Why it wins for a team with no budget:

- **Cost is only staff time.** No API key, no subscription, no per-query bill. The product
  can ship immediately against whatever the team verifies.
- **Reliability is under our control.** We decide what we publish; we can verify hours,
  price, and location against reality, which is exactly what the engine's `confidence` field
  rewards (`curated` / `verified`).
- **It is the seed that makes everything else tractable.** A curated seed gives the ingest
  pipeline its schema contract, its dedup keys, and its downgrade path. Without it, every
  other source is optional and the product's "no results" path has no floor.

Costs: high per-record effort, but we start with a *small* seed (the team's own area), so the
surface area is bounded. Maintenance scales linearly with new entries, not with the number of
sites we watch.

### 3.2 Scraped (rejected as a primary source)

Scraping sounds free, but for a team this size it is a trap:

- **Brittleness.** Recreations, event pages, and guides change their HTML/CSS constantly.
  A selector that works today breaks tomorrow and needs re-deriving. The maintenance burden
  scales with the number of sites, not the number of activities — i.e., it is *inverted* from
  what we want.
- **No schema contract.** Scrape output is heterogeneous HTML, so normalizing it to the
  Activity schema requires expensive, fragile heuristic extraction, and quality is unpredictable.
- **Legal / ToS risk.** Scraping against a vendor's terms is an open question for a
  low-volume product, and it gets worse as volume grows. We should not bake a product on a
  practice that may later be either impossible or casualty-extra-expensive.
- **Rate limits / anti-bot** are the norm, not the exception. A scraper that gets throttled
  silently returns stale or empty data.

**Verdict:** scrapers have a place later, *as a complement to a curated core* (e.g., to watch
for changes on venues the team already vouches), never as the source of record. It is
rejected as the primary ingestion strategy.

### 3.3 Licensed (rejected as a primary source today)

- **Cost is the blocker.** A licensed-activity product means a subscription or per-query bill
  that a no-budget team cannot carry in the first release. The product would ship nothing
  until an account existed — the opposite of "smallest real thing first."
- **Geography gaps.** Licensed coverage of small/mid-size areas (e.g., Ottawa-Gatineau in the
  pilot) is often patchy, and the worst case (a vague "no data in this area") is exactly when
  a team needs data the most.
- **Maintenance** is low, but *start-up* cost is high.

**Verdict:** licensed data is the right *enrichment* layer once the team has revenue; not a
first-release dependency. Until then, the free tier of specific vendor APIs is the cheaper
experiments, but all of it is best-effort.

### 3.4 User-generated (deferred with moderation)

User-generated listings are the natural *long-scale* answer: unbounded volume, zero per-item
cost, and they cover the local holes that no corporate source will touch. But they carry a
moderation cost:

- **Quality risk** (outdated hours, fake venues, spam) — mitigated by a submission + review
  flow, and by tagging every record `confidence=user_generated` so the engine can down-weight
  or gate it.
- **Moderation cost** — real people have to read submissions. We start by *limiting* the
  inflow (a curator-requested submit link, or a waitlist) until the team can afford the
  review queue.

**Verdict:** build the *capacity* (a submission form + moderation workflow) but throttle the
*inflow*; enable public user submissions only when the moderation pipeline can keep pace.

---

## 4. Recommendation: a curated core with best-effort enrichment

The product's data shape is a **curated core + best-effort enrichment + degraded fallback**,
not a single source of truth:

```
User-visible catalog
   ▲
   │  (from highest confidence down)
   │
   ├─ Curated "verified" entries        (primary; team-owns; confidence=curated)
   ├─ Provider API entries (free tier)  (added/refresh; confidence=verified, source=provider)
   ├─ User submissions (moderated)      (confidence=user_generated; gated on moderation)
   └─ Scraped candidate archive         (best-effort watch; confidence=inferred; rarely surfaced)
```

The engine's per-query snapshot is frozen at request time, and each record carries a
`confidence` (curated / verified / inferred / user_generated). The engine can therefore
**down-rank or gate lower-confidence records instead of treating all data as equal** — this
is how we get breadth *and* honesty without fabricating anything.

---

## 5. Phased adoption plan

| Phase | What ships | What it enables |
|---|---|---|
| **0 — Curated seed** | Team verifies ~10–30 local activities with full `location`, `price`, `hours`. | Working "find something near me" with honest results and a no-results UX. |
| **1 — Free-tier providers** | Add events/recreations from free vendor APIs to *enrich* the seed and refresh hours/availability. Best-effort; degrade if the API is down. | More breadth without a budget; teaches the ingest pipeline's failure handling. |
| **2 — Curated refresh** | Scripted regen (batch, idempotent) of seed + provider data; dedup on stable ids; materialized derived fields (`price_class`, `party_suitable`, `geohash`). | Lower per-entry maintenance; deterministic snapshots for the engine. |
| **3 — User-generated** | Submission form + moderation workflow; records tagged `confidence=user_generated`; inflow throttled until the moderation queue is sustainable. | Scale the catalog with local knowledge the team can't hold. |

Scraping enters only after Phase 3, and only as a *watcher* on the curated core, never as a
source of new facts. Licensing is re-evaluated when budget exists and geography gaps become
painful.

---

## 6. Failure-handling plan for external services

External data (weather, provider APIs, calendar feeds) is inherently untrustworthy: rate
limits, timeouts, stale readings, partial coverage, and outages. The design treats availability
as a first-class input using the degradation philosophy already established in the filtering
engine (ADR §8–§9):

### 6.1 Fetch-level resilience

| Pattern | Behaviour |
|---|---|
| **Parallel fetch with per-source timeouts** | Every source is fetched concurrently; a slow/failed source is dropped, not allowed to stall the query. |
| **Retry with backoff + jitter** | Transient 5xx/timeouts are retried with capped backoff and jitter; idempotent GETs only, so retries are safe. |
| **Retry-After courtesy** | Respected for HTTP 429; the ingest pipeline and engine add jitter so concurrent queries don't pile on one provider. |
| **Circuit breaker** | After `N` consecutive failures or a high error rate over a window, open the circuit for a cool-down; the source is skipped during cool-down and re-checked after. Prevents one flaky provider from dragging down the product. |
| **Idempotency + dedup** | Ingestion is keyed by stable `id` (provider + slug); records are upserted, never duplicated. Idempotent GETs keep re-runs clean. |
| **Caching / staleness window** | Short TTL cache for reads (stale-while-revalidate: serve the cached value immediately, refresh async, refresh users when fresh data arrives). Staleness is tracked per record (`data_freshness`), never hidden. |

### 6.2 Catalog-level degradation ladder

When ingestion fails, the product degrades in this order — never fabricates, and always
explains itself:

1. **Partial** — some sources are stale/missing. Lower-confidence records are down-weighted;
   the degrade envelope reports per-source freshness and warnings ("based on older data").
2. **Sources down** — a provider's circuit is open. Results from that provider are dropped;
   the curated core still answers. The degrade envelope lists `sources_down`.
3. **Sparse** — the area is under-provided. Only the curated core (plus any verified
   enrichment) is returned; distance/fallback scope widens; UI prompts "only a few confirmed
   options, try nearby areas".
4. **Empty** — no source has a matching candidate. Structured empty + relaxation prompts
   (`relax distance`, `allow indoor`, `expand weather`, `raise budget`). No fabricated rows.

This ladder is the *product* of failure handling, not just the pipeline's.

---

## 7. How ingestion failures affect the product

Ingestion failures never go silently to the user. The effect is visible and reasoned:

- **Results shrink, not vanish into noise.** A down provider removes its records; it does not
  degrade into fake "results".
- **Confidence is surfaced.** The `activity.confidence` field (curated / verified / inferred /
  user_generated) is part of the catalog record. Lower-confidence results can be shown but
  clearly marked ("not yet confirmed"), so the user can trust the core more than the edges.
- **The degrade envelope travels with the response.** Every recommendation includes
  `mode` (`full` / `partial` / `sparse` / `empty`), per-source `data_freshness`, `reasons`,
  `fallbacks_used`, and `warnings` — so "why did I only get 3 results?" has an answer that
  lives in the API, not in a support ticket.
- **Empty is a *designed* state.** "No results" is a first-class UX moment with a
  relaxation prompt, not a silent failure. The product can always say: *we don't have data
  for this area yet* (honest), rather than *here's a place that doesn't exist* (harmful).
- **Metrics feed product improvement.** Per-source error, staleness, and coverage counters
  (ingest pipeline logs) tell the team *which* source failed and *how often*, so the next
  phase fixes the right thing — e.g., adding a licensed source to an area whose free provider
  is down, or commissioning a curated entry where the provider has none.

In short: **ingestion failures transform an over-confident product into an honest one.** The
product stays usable (the curated core still answers), it degrades gracefully (sparse → empty),
and it tells the user exactly why. That is the entire point of the no-budget constraint: we
cannot afford to ship data we don't control, so we design the failure modes into the product
instead of hiding them.

---

## 8. Provenance data model (schema contract)

Each catalog record is stamped with provenance so the engine can weight it correctly:

| Field | Type | Purpose |
|---|---|---|
| `id` | string | Stable primary key (`provider` + `slug`) — used for dedup across sources. |
| `confidence` | enum | `curated` \| `verified` \| `inferred` \| `user_generated` — provenance + vouch level. |
| `source` | string | Provider/feed name that produced the record (null for curated). |
| `source_data` | object | Raw source payload, kept untouched in `metadata` — enables schema-drift recovery and audit. |
| `verified_by` | string[] | Team members who vouched for the record (curated only). |

Unknown fields from a source are kept in `metadata`, never dropped (schema-drift handler),
and the *materialized* engine fields (`price_class`, `party_suitable`, `geohash`) are computed
at ingest time — never derived per-query.

---

## 9. Open questions (for later cards)

1. **Which free-tier provider APIs** to integrate in Phase 1 (need geography + free-tier
   access; NWS for weather is a strong candidate for the pilot area).
2. **Curated seed size** for Phase 0 — the team will decide by area (e.g., Ottawa-Gatineau).
3. **User-submission moderation capacity** — defined by the number of human reviewers
   available, not by the volume we attract.
4. **Scraping policy** (ToS/legal) — a decision to revisit before Phase 4.

---

## 10. Verification & tests

This ADR is the contract for the ingest pipeline. The pipeline is verifiable by driving it
against a **synthetic dataset** (a generated, self-consistent catalog that simulates each
source's behaviour):

- **Happy path** — curated seed + provider entries produce the expected ranked recommendations.
- **Partial failure** — one free-tier provider down → results still return from the curated core;
  `sources_down` and `data_freshness` carry the correct stamps.
- **Circuit breaker** — `N` consecutive failures open the circuit, then a re-check re-opens it.
- **Idempotency** — a second ingest of the same provider records does not duplicate rows.
- **Schema drift** — a source record with an unknown field lands in `metadata` and the
  materialized fields are still correct.
- **Degrade ladder** — sparse and empty modes emit the correct relax prompts and no fabricated
  rows.

The synthetic dataset is the API boundary; engine logic stays network-free and deterministic.
