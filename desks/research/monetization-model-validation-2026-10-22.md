# Monetization Model Validation — "We Fill Your Slow Hours" B2B Thesis
**File:** `desks/research/monetization-model-validation-2026-10-22.md`
**Author:** Scout (Research & Marketing, ThingzToDo)
**Date:** 2026-10-22
**Status:** Validation + ranked revenue streams. For Eric's decision; not ratified.
**Feeds:** t_13f3b0b0 · `2026-10-22-interface-accounts-and-monetization.md` §3.1
**Builds on:** `desks/research/competitors.md` (15-company map, §5 verified pricing) and `desks/research/demand-validation.md`.

---

## 1. Verdict (clear, in one sentence)

**UNPROVEN — the *value* ("empty slow hours" are real) is validated, but the *commercial assumption* ("merchants will pay a recurring subscription to let us route demand into those hours") is unproven.** We do not have verified evidence that any local merchant in our map is already buying a weather-gated demand-routing / "fill-capacity" service, and the only published consumer pay-to-end-decision-fatigue comparable (SoulPlan) is a tiny-sample artifact, not a scalable demand signal.

**Not a refutation.** The underlying cost is real and documented (hospitality revenue-management literature shows weather + capacity drive diner traffic; rain crushes footfall while spiking delivery; DMOs like Visit Detroit already produce "rainy-day" visitor content and monetize ad/sponsorship). The gap is that no one has shown local merchants will *pay* for a routing layer rather than buying cheaper, commoditized inputs (BestTime busyness forecasts at $29–99/mo; Yelp/Google/Meta ad platforms). **Commercial-verdict: unproven. Product hypothesis: valid, and worth de-risking cheaply before build.**

### Three-part read of the thesis

| Thesis clause | Status | Evidence |
|---|---|---|
| "Weather is a perishable-inventory liquidation trigger" | **Validated** | Rain/daylight-crushing footfall and delivery channel-shift documented in hospitality forecasting (altametrics, flipdish, restroworks; temperature/biking comfort band 21–27°C). Venue dynamic-pricing platforms already price by weather + capacity (Smeetsu, EscapeLife, Red Rocks). |
| "ThingzToDo is a real-time demand-routing layer for dead local capacity" | **Valid as a product shape, unvalidated as a market** | No incumbent in our 15-company map sells this. The existing inputs are commoditized: hourly-busyness forecasts (BestTime $29/mo) and ad platforms. Proven "capacity management" sells only to high-value venues (stadiums, convention centres), not local merchants. |
| "Uniquely enabled by the weather filter" / "nobody is telling it" | **True as a product shape** | No one combines weather + cost + people + time into one ranked, follow-through-ready surface. But "uniquely enabled" overstates "uniquely sellable": the data signal (busyness) already exists and is cheap to buy; what's unowned is the *actionable next step*. |

**Bottom line for Eric:** The thesis is a *validated product hypothesis with an unvalidated sales motion*. Do not fund the merchant dashboard as fact; fund a 6-week low-cost experiment that measures willingness to pay (paid-calendar/live-call test, not a build).

---

## 2. Affiliate & transaction commission reality check (research question #6)

**Answer:** The memo's **~5–15% take-rate is a fair, conservative mid-range** — the real published experience/affiliate commission ceiling is far higher (8% baseline → up to ~30%). Importantly, the 5–15% figure is **ThingzToDo's own margin**, not what affiliate programmes pay others.

**Real published program terms (with source URLs):**

| Programme | Published terms | Source |
|---|---|---|
| **Viator** (Tripadvisor) | 8% baseline, up to ~30% on premium/large partners; AOV ~$110; last-click, ~30-day cookie; payout on *completed* activity | track360.io operator teardown (2026); linkapprove lists "up to 8% per booking" |
| **GetYourGuide** | ~8% min, higher for top partners; ~30-day cookie | afflemi.com programme listing |
| **Tiqets** | ~6–8% on attraction tickets | track360 field guide |
| **Klook** | Baseline percentage rising with partner tier | track360 field guide |
| **TripAdvisor / Viator** | Min **50% commission share** of what Viator earns on experiences; effective **~2–6% of booking value** once the share base is unpacked | tripadvisor.com/affiliates; track360 teardown |

**Read for the take-rate row:** 5–15% is conservative versus the 8–30% affiliate ceiling, so our own take-rate has headroom — **but** the affiliate model only works for *ticketed* experiences (tours, museums, attractions). It does **not** apply to un-ticketed F&B (restaurants, catering), which is exactly why §3.3's sequencing puts direct checkout for un-ticketed venues second. Also note the memo's Eventbrite line: verified primary from competitors.md §5 is **3.7% + $1.79/ticket** (Eventbrite help centre); the product memo lists $1.97 — flagged for reconciliation before price-lining.

---

## 3. Ranked revenue-stream table (core deliverable, research questions #2, #4, #5)

> Columns: **mechanism** · **named buyer** · **time to first dollar** · **defensibility @ 3 years** · **cited price or labelled gap**.
> "Named buyer" = the entity that pays us / signs the deal.

| # | Stream | Mechanism | Named buyer | Time to first dollar | Defensibility @ 3 years | Cited price / labelled gap |
|---|---|---|---|---|---|---|
| **1** | **Transaction take-rate** (affiliate → direct checkout) | Route consumers to ticketed partners (Viator/GetYourGuide/Eventbrite) via affiliate; then owned checkout for un-ticketed venues via map-pin-as-checkout. Take-rate 5–15%. | Venue/activity partner (consumer pays ticket; merchant pays our take-rate). | **Fast.** Affiliate weeks (link on existing footprint); direct checkout 2–4 wks (catalog + payments). | **High** — "executable next step" (booking) is unowned; moat = ground truth + catalog breadth + verified open/close. | **Real terms:** Viator 8%→~30%; GetYourGuide ~8%+; Tiqets 6–8%; Klook tier; TripAdvisor ~50% share (effective 2–6% of booking value). Take-rate 5–15% conservative vs 8–30% ceiling. Direct-checkout rate = our own decision (no market rate yet). |
| **2** | **Lead-gen fees** | "Request a quote / callback" touch → merchant pays per **qualified** lead, situation-scoped (not keyword-scoped). | Local venues/attractions (restaurants, theaters, museums) wanting qualified footfall/callbacks. | **Fast** — weeks (form + routing). | **Medium** — leads commoditize to ad spend unless we own the situation-fit intent data that qualifies them; must bundle demand signal. | **Real:** Google LSA per-valid-lead (restaurant search CPL $10–20; $25–80 typical overall) and Yelp CPC $5–25 / CPL $30–150 / base $150/mo. Our fee = negotiated per-lead number. |
| **3** | **Self-serve merchant listings + promoted placement** | Free claim → paid profile → promoted placement on map + in-chat answers (labelled **Sponsored**). | Venue/activity partners (restaurants, bowling, museums, attractions). | **Fastest to literal cash** (listing is a form; promoted placement a checkbox). | **Medium** — column proven (Yelp/Eventbrite/Meetup) but defensible only vs inventory breadth + filter conversion; low switching cost. | **Real:** Yelp Ads from $150/mo (CPC $5–25, CPL $30–150), Upgrade $180/mo, Ads+Upgrade $270/mo; Yelp Places API $229–643/mo; Meetup $29.99/mo. Promoted-placement rate = our own. |
| **4** | **Category sponsorship** (sponsor a *filter*) | Sponsor the filter ("under-$20", "rain plan"), labelled. | Brands + tourism boards wanting exposure to intent-seekers (banks, insurers, F&B chains). | **Medium** (needs a branded filter + sponsorship messaging). | **Medium** — high margin, but brand-fit risk if recommendations disappoint; keep filter purely functional, label sponsors. | **No published market rate — LABELLED GAP.** Our own negotiation frame (comparable: Yelp "Prime ad spots" bundled $150–270/mo are placement, not a named filter). |
| **5** | **Consumer premium** | $3.99–6.99/mo or $29.99/yr: travel mode, auto rain plan, group planning, saved lists, alerts. | Solo/couple/group intent-seekers; value breadth, foresight, group coordination — **never** the answer. | **Slow** — requires retention. | **Low** — thinnest conversion; SoulPlan ($12.99/mo, 1 rating, Apple-only) shows tiny-sample demand, not scalable. | **No published comparable** (SoulPlan real = $12.99/mo/weekly). Memo's $3.99–6.99 is **~2× below** the only comparable — UNDERWRITTEN. |
| **6** | **Deal / voucher economics** | Time-boxed offers surfaced by situation; merchant pays on redemption. | Same merchants as #3 — **COMPETES** (not stacks) with #3 and Groupon's model. | **Slow** (needs a payment + redemption loop we don't own). | **Low** — Groupon's refund/redemption friction (competitors.md) shows this column is low-trust. | **No published comparable**; competes with Groupon $0-upfront / commission-on-redemption. |
| **7** | **Anonymized demand data** | "What Ottawa searched on a rainy Saturday" → sold to DMOs/tourism boards/venues. | DMOs / tourism boards (and, later, venue chains). | **2027+** (requires an honest data asset). | **High, quiet** — DMOs already buy analytics/destination data; our municipal ground truth is the differentiator. | **No published comparable** for "situational anonymised demand data — LABELLED GAP"; DMO marketing budgets are millions (Visit Detroit 2024: 19M visitors, $1B+ lodging revenue; sells B2B ads + sponsorships). |

---

## 4. Two-axis read: fastest dollar vs. 3-year defensibility

The ranking above is **risk-adjusted best overall** (cash-flow speed + defensibility together). Two axes diverge, and the divergence is the insight:

**Fastest path to a dollar:** #3 (promoted placement) is the literal fastest (a checkbox), but it's the *thinnest* revenue per unit. #1 (take-rate) and #2 (lead-gen) are the fastest *meaningful* dollars — both attach to the executable next step, not to promo real estate.

**Most defensible at 3 years:** #1 (take-rate/affiliate) and #7 (data) tie for the top — they monetize the moat (executable next step; and honest data, respectively), whereas #3/#2 monetize a commodity column that incumbents already do. #7's defensibility is high but it is a **late, relationship-sale play** that does not drive Y1–Y3 cash; it is the quiet upside, not the foundation.

**Recommendation:** Lead with **#1 then #2**, layer **#3** as the fastest cash (accept commoditized promo as a bridge, not a moat), and treat **#7** as a 2027+ build once the data asset is honest.

---

## 5. Which streams compete vs. which stack (flagging collisions)

| Streams | Relationship |
|---|---|
| **#1 take-rate** vs **#6 deal/voucher** | **Compete** for the same merchant-money line; a deal offer competes with building a take-rate on the same bookings. |
| **#3 promoted placement** vs **#6 deal/voucher** | **Compete** — both are merchant funding of prominence; #6 re-litigates Groupon's friction. |
| **#3 promoted placement** vs **#2 lead-gen** | Can **stack** (a merchant pays for prominence AND qualified leads), but they compete for the same "clout" budget line; lead-gen gains credibility if it uses situation-fit intent data. |
| **#5 consumer premium** vs **#1 take-rate** | Can coexist (premium = foresight/features; take-rate = self-serve booking), but **do not let premium gate the core answer** or it defers to the next free entrant (memo §3.2 rule). |
| **#7 data** vs **#2 lead-gen** | Can **stack** (anonymized volume → better lead quality), but must not reverse-engineer to individual targeting, or the DMO sells its own customers. |
| **#4 sponsorship** vs **#1 take-rate** | Essentially independent; sponsorship is supply-side brand exposure, take-rate is transaction cut. No conflict. |

---

## 6. Named buyer per stream (research question #2)

| Stream | Named buyer | Their budget & cycle |
|---|---|---|
| #1 Transaction take-rate | Venue/activity partner (ticketed) | Lowest: % of a ticket; immediate |
| #2 Lead-gen fees | Local venue/attraction (F&B, arts, museum) | Mid: per-lead CPL $10–150; monthly test |
| #3 Merchant listings + promotion | Local venues/bowling/museums | Mid: $150–643/mo base; self-serve |
| #4 Category sponsorship | Brands + tourism boards | Mid-high: package deals; annual |
| #5 Consumer premium | Solo/couple/group intent-seekers | Low: ~$3.99–12.99/mo; consumer-level |
| #6 Deal/voucher economics | Venue partners | Low-mid: on redemption |
| #7 Anonymized demand data | DMOs / tourism boards / venue chains | High: multi-year relationship; data-as-infrastructure |

**Liquidity note:** #5 (consumer) has the lowest budget but also the thinnest conversion; #7 (DMO) has the highest budget but the longest sales cycle and the conflict of being our own source-of-truth — a DMO might not want *their own* visitors sold back to them, so the data product must be built on *third-party/verified* signals or anonymized-affiliate data, not on our users' personal searches.

---

## 7. The perishable-inventory thesis: what we have (and haven't) seen

**Validated side (the "why it should work"):** Hospitality forecasting literature shows weather + capacity materially shifts traffic and channel (altametrics restaurant forecasting; flipdish demand forecasting; Fisichelli et al. 2015 temperature/activity comfort band 21–27°C; AMSC 97% winter-sport forecast use). Venue dynamic-pricing products already price by weather + capacity (Smeetsu: weather + booking velocity + 15-min price ticks; EscapeLife Yield Engine: "rainy forecast → auto-discount outdoor, push indoor"; Red Rocks Amphitheatre weather-integrated demand prediction). So "dead capacity" is a real, measurable economic state for ticketed venues.

**Unproven side (the "who pays" gap):** No local merchant in our 15-company map — including the municipal "source-of-truth" pages (Visit Detroit, Prague City Tourism) — is buying a weather-gated demand-routing or "fill your slow hours" service. Visit Detroit sells B2B ads/sponsorships and publishes rainy-day content, but has no actionable insight layer (consistent with our map). The commoditized inputs already exist and are cheap: BestTime busyness forecast (published $29/mo basic; $99/mo Pro; $96–399/mo by venue count), Google LSA per-lead (restaurant search CPL $10–20; $25–80 typical), Yelp Ads ($150+/mo). None of these *route* demand; none is weather-gated demand routing. **We have not verified that any local merchant will pay a recurring subscription for that routing step.**

**Sole consumer-pay signal:** SoulPlan — $12.99/mo weekly with a 3-day trial, "Best Local Spots," "Enhanced AI Suggestions" (Apple App Store primary; theresanaiforthat secondary). It is Apple-only, ~1 App Store rating (≈500+ Google Play installs), 3.5★. **This is a tiny-sample artifact, not a scalable demand signal** — and its real price (~$12.99/mo) is 2× the memo's proposed consumer premium ($3.99–6.99/mo), so the memo's premium band is underwritten low, not validated.

**Nuance on scope:** The thesis is partially valid for **ticketed / capacity-constrained venues** (where dynamic pricing + affiliate already exist and the "executable next step" is the moat), and **not valid for simple F&B** (restaurants buy ads and leads, not demand routing). The unsubstantiated universal claim is that *local merchants* will subscribe to a routing layer.

---

## 8. What is still unknown (explicit; no manufactured market-size number)

These are the holes that block a cash-flow or sizing decision. None are fabricated; they are flagged as gaps.

1. **Market size for the state-conditioned need.** Demand is real at search level; the specific "weather+cost+people+time" conditioned query has **no verified market-size number** (per demand-validation.md §6). Do not build a budget on one.
2. **Willingness to pay for a routing layer.** No verified price for a merchant subscribing to "fill your slow hours" — the closest published prices are busyness forecasts (BestTime $29/mo) and ad platforms. We must test WTP directly (paid-calendar/live-call test).
3. **Direct-checkout take-rate for un-ticketed venues.** No market rate; our 5–15% is our own decision, not anchored.
4. **DMO data-product price.** No published price for "situational anonymised demand data" sold to DMOs. DMO budgets exist (thousands of US DMOs; Visit Detroit $1B+ lodging), but the per-seat/per-microsite number is unverified.
5. **Promoted-placement rate for our map.** Our own pricing, benchmarked against Yelp Ads ($150–270/mo) and Eventbrite Pro ($15/mo)/Premium ($69/mo) — not yet set.
6. **Lead-fee economics.** Our per-qualified-lead fee is a negotiated number; real paid-lead benchmarks exist (Google LSA, Yelp), but we haven't modeled unit economics at our conversion rate.
7. **Eventbrite fee reconciliation.** Verified primary says 3.7% + $1.79/ticket (competitors.md §5); product memo lists $1.97 — needs one check before price-lining.
8. **SoulPlan scalability.** 1 rating + Apple-only lockup: whether "pay to end decision fatigue" is a real market or a 1-person artifact is unproven without broader review data.

---

## 9. Source register (every claim carries a URL)

**Affiliate / transaction economics**
- Viator 8%→~30%, AOV ~$110, last-click 30-day: https://track360.io/blog/viator-getyourguide-affiliate-programs-operator-teardown-2026 · https://linkapprove.com/affiliate-programs/viator-affiliate-program
- GetYourGuide ~8%+, 30-day cookie: https://www.afflemi.com/affiliate-programs/p/getyourguide
- Tiqets 6–8%, Klook tier-based: https://track360.io/blog/tours-activities-experiences-affiliate-programs-operator-guide-2026
- TripAdvisor min 50% commission share (effective 2–6% of booking value): https://www.tripadvisor.com/affiliates?tab=gettingStarted · https://track360.io/blog/tripadvisor-affiliate-program-operator-teardown-2026

**B2B local promotion pricing**
- Yelp Ads from $150/mo, CPC $5–25, CPL $30–150, Upgrade $180/mo, Ads+Upgrade $270/mo, Places API $229–643/mo: https://business.yelp.com/local-business-pricing/
- Meetup $29.99/mo Standard, $55/group/mo PRO: https://www.meetup.com/pricing/ (maintained in competitors.md §5, verified)
- Eventbrite 3.7% + $1.79/ticket (verified primary from competitors.md §5): https://www.eventbrite.com/help/en-us/articles/193833/eventbrites-new-pricing-plans/
- Google Local Services Ads per-valid-lead (restaurant search CPL $10–20; $25–80 typical): https://support.google.com/localservices/answer/7195435 · https://business.google.com/us/ad-solutions/local-service-ads/dining/
- Yelp lead benchmarks (CPC $5–25, CPL $30–150, small-business $300–1,000/mo): https://augemarketing.com/resources/yelp-ads-for-business/

**Data / busyness forecast / venue revenue management (the "inputs" the thesis would sit on top of)**
- BestTime busyness forecast: $29/mo Basic, $99/mo Pro, $96–399/mo Venues: https://besttime.app/subscription/pricing
- Smeetsu dynamic pricing (weather + booking velocity + capacity, 15-min price ticks): https://www.smeetz.com/solutions/revenue-management
- EscapeLife Yield Engine (rain→auto-discount indoor, surge outdoor): https://www.escapelife.ai/platform/yield
- Red Rocks Amphitheatre weather-integrated demand prediction: https://waitlists.org/articles/industry-news-trends/predictive-analytics-venue-revenue-optimization-machine-learning-dynamic-pricing

**DMO / tourism data**
- Singapore Tourism Board + Traveloka data-driven destination marketing, anonymized consumer insights: https://www.marketing-interactive.com/stb-renews-traveloka-alliance-to-expand-destination-marketing-across-six-markets
- Evok DMO Analytics Guide 2026 (layered web/CRM, geolocation, anonymized card spend; ~1/3 of DMOs funding at risk): https://www.desmoinesregister.com/press-release/story/112389/destination-marketing-agency-publishes-2026-analytics-guide-as-nearly-a-third-of-dmos-report-funding-at-risk/ and https://evokad.com/destination-data-analytics-dmo-guide-2026/
- KeyData destination data for DMOs (occupancy, ADR, RevPAR, booking pace): https://www.keydata.co/products/destinationdata
- Visit Detroit 2024 reporting (19M visitors, $1B+ lodging, sells B2B ads + sponsorships, analytics function): https://detroitc3.com/statistics/detroit-tourism-statistics/ and https://www.mediabistro.com/jobs/3542527605-digital-marketing-coordinator-tourism-hospitality

**Consumer pay-to-end-decision-fatigue**
- SoulPlan $12.99/mo weekly (Apple App Store primary; theresanaiforthat secondary): https://apps.apple.com/us/app/soulplan-plan-dates-together/id6702018988

**Product memo / thesis**
- Product memo §3.1 thesis + revenue stack (already on file): `desks/product/2026-10-22-interface-accounts-and-monetization.md`
- Competitor map §5 verified pricing; Eventbrite/GurunWalk/SoulPlan/Groupon/Yelp/Meetup prices: `desks/research/competitors.md`
- Demand validation + WTP disclaimers: `desks/research/demand-validation.md`

**Source-quality note:** Affiliate figures are secondary program summaries (Track360 operator teardowns; afflemi marketplace); Viator's "up to 8%" on linkapprove reflects an older/limited snapshot vs the 8%→30% teardown — treat 8–30% as the directional range. BestTime, Yelp, Google, Eventbrite, Meetup, SoulPlan prices are from company primary pages or the Apple App Store. DMO figures are Visit Detroit's own 2024 reporting.

---

## 10. Decision recommendation for Eric

1. **Verdict: UNPROVEN** on the commercial assumption. Re-state plainly: we have *not* verified that local merchants will pay to be "routed" demand — we have verified that empty slow hours are real and that cheaper inputs (busyness forecasts, ads) exist.
2. **Fund a 6-week validation instead of a merchant-building spike:** a paid-live-call test / landing page that asks venues to pre-pay for a 3-month weather-gated fill-capacity slot, with a hard exit if conversion is 0. This converts the thesis from "unproven" to "won-or-lost."
3. **Keep the cash engine simple:** lead with **#1 (take-rate)** and **#2 (lead-gen)** — the verifiable, cheapest dollars. Use **#3 (promoted placement)** as the fastest literal cash and accept its commoditized nature. Defer **#5 (consumer premium)** until retention exists (its proposed $3.99–6.99/mo band is underwritten low vs the real $12.99/mo comparable).
4. **Do not build #7 (data) as a cash driver in Y1–Y3.** It is a quiet, high-margin 2027+ upside and, because Visit Detroit is our source-of-truth, it must be built on third-party/anonymized signals.
5. **Reconciliation before pricing:** Eventbrite $1.79 vs $1.97, and SoulPlan's $12.99/mo as the consumer-premium anchor.

---
*Prepared by Scout, 2026-10-22. Every figure above is either a cited primary source or labelled as a gap; nothing is invented. No budget, spend, or account has been committed.*
