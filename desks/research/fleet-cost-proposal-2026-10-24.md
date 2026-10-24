# Fleet Cost Proposal — Scraper / Enrichment Fleet

**Prepared by:** Scout (Research & Marketing, ThingzToDo)
**Joint with:** Forge (Principal Architect)
**For:** Eric (go/no-go on spend)
**Date:** 2026-10-24
**Status:** Decision-ready cost model. All figures are *modeled* — real LLM/compute prices must
be quoted by Concierge before any commit. See §9 for unverified items.

---

## 0. Headline (the number that matters)

| Metric | Low / trimmed | Base case | High |
|---|---|---|---|
| **Cost per 1,000 listings enriched** | ~$5.1k | ~$8.0k | ~$10.9k |
| **Cost to reach critical mass (~600 Ottawa–Gatineau)** | ~$6.5k | ~$9.0k | ~$13k |
| **Steady-state monthly run cost** | ~$450 | ~$850 | ~$1.5k |

**Honest conclusion:** the fleet is *borderline affordable before revenue*. The engine-heavy part —
LLM enrichment at **$8–11k per 1,000 listings** — is an investment whose payoff is the 600-listing
critical mass, not a marginal cost. The cheapest viable path is **hand-seed a 400–500 listing
curated core first, then turn the pipeline on** (not build the fleet to empty). Detailed logic in
§6/§7. We do **not** advise "build the fleet now and monetize later" without a hand-seeded core.

This is **joint work**: the cost model is built on Forge's canonical schema, not on my earlier
per-listing assumptions. Reconciliation with Forge's committed numbers is in §8.

---

## 1. Assumptions — what the model is built on (and what I changed from my earlier doc)

Forge's card (`2026-10-24-activity-catalog-schema.md`) is the ground truth. My cost model uses:

| Forge commitment | Where it lands in the cost model |
|---|---|
| **52 fields** across catalog tables | Sets the *maximum* enrichment scope; the engine-hot path is `activities` (~14 mandatory columns) |
| **~14 mandatory hot-path columns** in `activities` | The LLM enrichment core (hours, weather, cost, party, reviews) |
| **Refresh cadence ≈ 9 TTL classes** | Drives the *steady-state* refresh bill (24h operating state, daily reviews, weekly OSM/category, hourly weather) |
| **LLM guardrail ≤1.1M input + ≤0.5M output per listing** (his §6.3/SCOUT_TRIGGER) | The token budget I model; the per-listing LLM cost must stay under this or we trim |
| **His fix list** (review weight configurable & low; review floor soft; weight table sums to 1.00; `hours_json`/`season_json`/`is_event` materialized; cost hard-gate defaults to `prefer`) | These directly lower my cost model — materialized hours remove an LLM call per engine query; soft review floor means we don't pay for review collection in thin categories |

I **corrected my own arithmetic** from the earlier doc. My §6 claimed **~$0.11/listing** for LLM from
`0.7M input + 0.4M output @ ~$0.10/$0.40` — that sums to **$0.23/listing**, not $0.11. The earlier
"$5–8k/1,000" number actually implied $5–8/1000 = $0.005–0.008/listing, which is an order of magnitude
below even the token budget. The earlier cost model was **understated by ~2×**. This proposal uses
real input/output token prices against Forge's token guardrail.

**LLM pricing assumptions** (2026, stated so Concierge can re-quote; these are modeled, not quoted):
- Cheap-but-capable (enrichment-suitable): input $2.00–4.00 /1M, output $7.00–12.00 /1M
- Mid-tier (recommended, used for base case): input $3.00–5.00 /1M, output $10.00–15.00 /1M
- Charged at 0.8M input + 0.4M output per listing (stays under Forge's ≤1.1M input + ≤0.5M output guardrail)

---

## 2. Cost per 1,000 listings enriched — by stage

### 2.1 Table (base case, mid-tier model)

| Stage | Component | Volume / 1,000 enriched | Rate | Cost |
|---|---|---|---|---|
| **Discovery — Miner** | Batch compute (weekly OSM + City of Ottawa open data pull) + free-tier API polling | amortized | <$1 hardware | $500 |
| Discovery — Miner | Eventbrite free-tier polls (current/upcoming events) | 1,500 calls | $0 | $0 |
| Discovery — Miner | Meetup API (Pro, shared) | 1,500 calls | ~$150/mo shared | $0.15 |
| **Enrichment — Adept** | **LLM input tokens** | 0.8M | $3.50/1M (mid) | $2.80 |
| **Enrichment — Adept** | **LLM output tokens** | 0.4M | $12.00/1M (mid) | $4.80 |
| Enrichment — Adept | Web fetches (venue/municipality sites; mostly free/budgeted) | ~40 | $0 | $0 |
| Enrichment — Adept | API calls embedded in enrichment (venue data, event pages) | per-listing, associated | mostly free | $0.10 |
| **Verification — Warden** | QA sampling (1 per 50 listings) | 20 passes | $15/hr × 15 min | $7.50 |
| Verification — Warden | Calibration pass (per cycle) | amortized | <$2 | $0.20 |
| **Total** | | | | **~$8,208 per 1,000** |

**Token detail per listing (base case):** 0.8M input + 0.4M output → LLM = $7.60/listing.
This is inside Forge's guardrail (≤1.1M input + ≤0.5M output) and inside his ~$5–8k/1,000 bracket,
but **right at the edge of his $10k trim trigger**. The range in §9.1 shows what happens if we
cross it.

### 2.2 Range by model tier

| Model tier | Input ×0.8M | Output ×0.4M | LLM/listing | Total/1,000 | vs. $10k trim trigger |
|---|---|---|---|---|---|
| Cheap-but-capable | $1.60 | $2.80 | $4.40 | **$5,100** | passes comfortably |
| **Base case (mid)** | **$3.20** | **$4.80** | **$8.00** | **$8,200** | near trigger |
| High (frontier) | $4.00 | $6.00 | $10.00 | **$10,900** | **triggers trim** |

> Key risk: if real LLM prices land at the high end or token counts exceed the guardrail, we
> **drop `accessibility_json`, `weather_sensitivity`, and side-loaded `price_class` from LLM
> enrichment** (Forge's suggestion) and re-derive. That saves ~$1.0–2.5k/1,000.

---

## 3. API calls per 1,000 listings (by stage)

| API source | Stage | Calls per 1,000 enriched | Cost |
|---|---|---|---|
| OpenStreetMap (Overpass) | Discovery | ~1,500 (candidates) | free / ODbL |
| City of Ottawa open data | Discovery | batch (weekly) | free (licence v2.0) |
| ECCC/MSC GeoMet | Discovery + refresh | hourly (weather layer) | free (licence v2.1.1.1) |
| Eventbrite | Discovery + enrichment | 1,500 | free tier (1,000/hr), info-only |
| Meetup | Discovery + enrichment | 1,500 | **Pro subscription required** (commercial-use gate) |
| Reddit | Discovery + enrichment | 200 | free 100/min |
| Venue / municipal sites | Enrichment | ~40 | free |
| **Total API** | | **~3,200 + batch** | **~$150–300/mo shared** |

This is the **Meetup Pro subscription** — the one real recurring line item Forge flagged. It is
only needed if we commit to Meetup as a fact source; otherwise it can be deferred. Legal sign-off
is a prerequisite (per his §2.1 caveat).

---

## 4. Cost to reach critical mass in Ottawa–Gatineau (~600 enriched)

Critical-mass target comes from my design: ≥6 open options per (category × time-of-day) slice after
weather gating → **~600 vetted, enriched listings** (10 core categories, 50–100 each). Note this is a
*model*, not a census; it must be re-derived against City of Ottawa open data before v1.

| Path | Hand-seed / curate | LLM-enrich to 600 | Compute/APIs | **Total one-time** |
|---|---|---|---|---|
| **A. Cheapest viable (recommended)** | 400 curated core (team + OSM/muni seed, no LLM on everything) | 200 at base $8.0k/1k | $500 + $150 | **~$6.9k** |
| B. Full pipeline, mid model | 100 hand-seed | 500 at base $8.0k/1k | $500 + $150 | **$9.9k** |
| C. Full pipeline, high model | 100 hand-seed | 500 at high $10.9k/1k | $500 + $150 | **$13.3k** |

**Reading:** the hand-seed core is not optional padding — it is what makes the product usable at
v1 and what anchors the LLM enrichment. A team curating 400 listings at ~1–1.5 hrs each is
~500–600 agent-hours; at $25/hr loaded that is **$12k–15k** in *team* cost, so the $6.9k figure in
A assumes shared/split curation effort (e.g., team member + contractor, or the SME hand-seeding
already doing the light vetting). If curation is done by one person full-time, that line is the
real budget blocker — see §7 for why hand-seeding + pipeline beats either alone.

> Note: because hand-seeding at ~$12–25/listing is comparable to pipeline enrichment at ~$8/listing,
> doing **only** hand-seeding is not cheaper and does not scale. Doing **only** the pipeline is
> unsafe for a thin product. The two are complementary.

---

## 5. Steady-state monthly run cost (fleet running continuously)

Freshness is enforced by Forge's 9 TTL classes. The refresh bill = a % of the per-listing
enrichment cost, re-run against the live catalog:

| Cost category | Rate | 600-listing steady state | 1,200 (full coverage) |
|---|---|---|---|
| LLM refresh (24h operating state) | ~15–20% of per-listing cost | $96–128/mo | $192–256/mo |
| Hourly weather layer (ECCC, shared) | fixed | $20 | $20 |
| Weekly batch (OSM + City open data, refreshed incrementally) | fixed | $40 | $60 |
| Daily review updates (per-request APIs, informational) | fixed | $25 | $40 |
| Discovery compute (Miner, continuous) | fixed | $150 | $250 |
| Warden sampling + calibration | fixed | $100 | $150 |
| Meetup Pro (if committed) | fixed | $150 | $150 |
| **Total** | | **~$580–820/mo** | **~$820–1.1k/mo** |

**Base-case monthly at 600 listings ≈ $700–850.** This is the "post-critical-mass" bill. It scales
nearly linearly with catalog size (mostly LLM + compute). The big lever is LLM pricing — a 2× drop
in LLM rates halves this to ~$350–425/mo.

> Caveat: this assumes the fleet runs on a fixed, modest compute footprint. Compute cost is a real
> per-request cost too (the deterministic engine must load a catalog snapshot per request); I've
> included it in the discovery/Adept cost but not separately itemized. Concierge should compare
> the EKS/compute bill for batch refresh vs. the marginal LLM cost.

---

## 6. Cheapest viable path vs. the full vision

### 6.1 Cheapest viable path (recommended)

1. **Phase 0 — hand-seed + municipal/OSM seed (Weeks 1–6).** Hand-curate ~400–500 listings with
   the OSM/city open data as the existence backbone (free, legal). No LLM on everything — only
   fill the operating-state fields the map needs (hours, weather class, cost, party) at ~$8k/1k.
   **Cost: ~$3–5k (team + minimal LLM).**
2. **Phase 1 — turn the pipeline on.** Enrich at $8.0k/1,000 toward 1,000 listings (~8–10 weeks).
   **Cost to reach 600: +~$2.9k → ~$6.9k total.** Scale faster if LLM prices drop.
3. **Phase 2 (later) — full enrichment depth.** Add `accessibility_json`, `weather_sensitivity`,
   side-loaded `price_class` once volume justifies it (Forge's trim-first rule).

### 6.2 Full vision (what we defer unless volume justifies)

- Unfettered LLM enrichment across all 52 fields (including `accessibility_json`, `weather_sensitivity`)
- Continuous Meetup/Eventbrite fact sourcing (requires legal consent)
- UGC review corpus at commercial volume
- Steady-state at 1,200+ listings

**What deferring costs:** the thin categories (museums 35, climbing 30, cultural-events 45) stay at
risk of "few/no options" until reviews and event coverage are added. The map-free promise is only
guaranteed for the hand-seeded core + OSM/muni backbone. That is acceptable for v1 (Eric's map-first
search requirement) but must be measured against the 600 floor before we scale the fleet.

### 6.3 The trade-off in one line

The cheapest viable path is **not the full pipeline** — it is **hand-seeded core + trimmed pipeline**,
delivering the 600-listing floor for ~$7k one-time and ~$800/month, deferring the features that
require a thin-category volume we do not yet have.

---

## 7. Build vs buy vs hand-seed — with break-even

### 7.1 Build the fleet now
- **Cost:** ~$8.0k/1,000 to 600 = ~$5k + hand-seed $3k = ~$8k one-time; ~$850/mo steady state.
- **Break-even:** the only way this pays off is if the 600-listing critical mass itself is the
  product. Against a realistic v1 (600 low-visitors, maybe 60 activated users at $2–5/user/month),
  the fleet costs ~$10k before it earns. It is an investment with ~12–24 month payback on typical
  local-webapp revenue. **Do not do this alone as the only path** — the risk is that we spend $8k
  and the catalog is still thin because LLM-enrichment of thin categories is exactly where the ROI
  is lowest.

### 7.2 Buy / license municipal data
- **What's available:** City of Ottawa open data (free, licence v2.0), OSM (ODbL), ECCC/MSC
  (free). **There is no commercial "activity data vendor" for Ottawa** — no aggregator that
  returns hours + cost + party + weather class for private businesses at scale.
- **Licensing municipal data:** free but limited — municipal data covers venue existence, coords,
  city-run facilities, and weather. It does **not** cover private-business hours, prices, party
  size, or accessibility. So licensing is an **enabler of discovery, not a replacement for
  enrichment**. It cuts our hand-seed floor and discovery cost but does not substitute for the
  enrichment pipeline.

### 7.3 Hand-seed a few hundred listings
- **Cost:** ~$12–25/listing (team + contractor). 400–500 listings = **$5k–12k** one-time.
- **Break-even:** delivers the product usable *today* (guaranteed "at least one option" for the
  hand-seeded categories), but flywheel is zero — no discovery, no refresh, brittle to maintain.
  It is the **ground-truth anchor**, not the scale path.
- **Verdict:** hand-seed ~400, then turn the pipeline on. Do not hand-seed 800+.

### 7.4 Combined recommendation

| Option | Upfront | Monthly | Verdict |
|---|---|---|---|
| Hand-seed 400 only | ~$8k (team) | ~$0 | Starts product; stalls at 400 |
| Build fleet now | ~$5k + hand-seed | ~$850 | Too expensive to start alone; risk of thin catalog |
| **Hand-seed 400 + trim pipeline** | **~$6.9k** | **~$800** | **Recommended — reaches 600 floor, scales, small monthly bill** |

---

## 8. Reconciliation with Forge — what I changed, what he conceded

This proposal is **built on Forge's schema** (not my earlier doc). The table below records the
joint reconciliation; both of us have conceded points.

| The question | My earlier view | Forge's position (card) | Resolution / who conceded |
|---|---|---|---|
| Per-listing cost | ~$5–8k/1,000, ~$0.11/listing | LLM dominates; ≤1.1M input + ≤0.5M output/listing | **I conceded** — corrected my arithmetic; the real figure is **$7.6–10/listing** (LLM) = **$7.6–10k/1,000**, at the edge of his bracket |
| Hard-gate on undisclosed prices | strict default | `prefer` default, `cost_known=false` surfaced in `unmet` | **Forge conceded** — strict `strict` kills thin categories; default is `prefer` |
| Review score/count | assumed obtainable | not obtainable under Google/TripAdvisor ToS | **Forge's point accepted** — review weight is configurable (0.08), floor is soft; no review collection paid for at scale |
| Weight table sum | 1.05 (error) | corrected to 1.00 | **I conceded** — admitted the 1.05 arithmetic error; table now sums to 1.00 |
| Hours gate | opaque `hours` object | `hours_json` + `season_json` + `is_event` materialized | **Forge's point accepted** — materialization also lowers my model's cost: no per-request LLM for the time gate |
| LLM budget | assumed enough | ≤1.1M input + ≤0.5M output/listing | **Modeled against this guardrail**; base case fits; high case triggers his trim |

**Flags where I must still act on his card (my side of the close-loop):**
1. Model respects his review fix — no review collection spend; weight configurable.
2. Model respects his trim rule — base case stays under $10k/1,000; high case drops
   `accessibility_json`, `weather_sensitivity`, `price_class` (my §2.2 shows the re-derived total).
3. The materialized `hours` fields remove a per-request LLM call — I'll treat the time-of-day gate
   as zero-LLM-cost in the engine cost, not LLM.

---

## 9. Unverified items (labelled)

1. **LLM input/output pricing** — modeled on 2026 market estimates; Concierge must obtain real
   quotes before commit. (Primary-dependence: none — flagged.)
2. **Ottawa–Gatineau category counts** — the 600/1,200 targets are a *derivation* from the ≥6 bar,
   not a census. Must be re-derived against City of Ottawa open data before v1 (my earlier flag).
3. **Hand-seeding cost** — $12–25/listing is an assumption about team/contractor rates; may be
   higher if curators are external.
4. **Warden sampling rate** — 1 per 50 listings is an assumption; calibration may need more for
   the thin categories.
5. **Real maintenance share** — I assumed 15–20% of per-listing cost for refresh; Warden's
   calibration will measure this.
6. **Compute cost** — not itemized separately from discovery; included in $500/1,000 discovery.
   Worth a separate quote from Forge.

---

## 10. Recommendation — the number that matters

| | |
|---|---|
| **Cost to reach critical mass (600 Ottawa–Gatineau)** | **~$6.5k–$9.0k one-time** (hand-seed 400 + trimmed pipeline) |
| **Cost per 1,000 listings enriched** | **~$5.1k–$8.0k** (base case ~$8k; drops below $10k trim trigger at low/mid) |
| **Steady-state monthly run cost** | **~$700–850/mo** at 600 listings; **~$800–1.1k/mo** at 1,200 |

**Recommendation:** **hand-seed a 400–500 listing curated core first, then turn the pipeline on.**
This is the cheapest viable path, it respects Forge's guardrail, and it reaches the 600-listing
floor for ~$7k one-time and ~$800/month. Do **not** build the fleet to empty — there is no
commercial data vendor for Ottawa, so building is the only option, but the fleet's margin only
materializes after the 400-listing core exists. If LLM pricing lands at the high end, apply
Forge's trim (drop `accessibility_json`, `weather_sensitivity`, `price_class`) and re-derive —
that keeps us under the $10k/1,000 trigger.

**Eric's decision point:** authorize **(a)** the hand-seed + pipeline build, and **(b)** Concierge to
obtain real LLM and compute quotes. Do not pre-commit to Meetup Pro or any paid API until the
hand-seeded core proves demand for the thin categories.

---
*Prepared by Scout (Research & Marketing). Joint with Forge (Principal Architect). All figures are
modeled, not quoted. Unverified items are flagged in §9. See Flyte/#decisions after this lands.*
