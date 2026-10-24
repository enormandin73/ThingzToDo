# Product Decision Record — First Three Features (v1 Release Slice)

**Date:** 2026-10-24
**Status:** PROPOSED — raised to `#product` (Eric @mention); awaiting Eric's decision
**Owner:** Curator (Head of Product & Design)
**Desk:** `desks/product/`
**Raised in:** `#product` on 2026-10-24; each request prefixed with Eric's @mention (`<@309043067170848772>`) so it was delivered to him directly.

---

## Summary

This record closes **Charter open question OQ5** ("What are the first three features worth building?"). It defines the **v1 release slice**: the narrow, coherent set of three features that constitutes the smallest thing that is real for the first user — an Ottawa–Gatineau local hunting "tonight," 1–2 people, weather + budget constrained.

**The three features:**

1. **The "Tonight" situation surface** — the map-first, ranked-recommendation funnel: situate (weather/cost/people/time + exclusions) → ranked rail with "why it fits" → map pins; SSR default state; degrade contract.
2. **Ground-truth catalog + live weather gating** — a seeded Ottawa–Gatineau catalog (indoor/outdoor, hours, price, party size, venue coordinates) + Open-Meteo weather materialized into the cache, driving the two-tier engine's hard gates and soft score.
3. **Follow-through + verified backup** — outbound plan (directions, shareable guest URL, no account) and a verified indoor backup when weather gates out the top outdoor pick.

These three are the release. Everything else (accounts, premium, merchant listings, new geographies) is deliberately **not** in v1.

---

## Decision 1 — The "Tonight" situation surface (core funnel)

**What is decided:**
The v1 core is a **map-first, web-first surface** where a user's situation becomes a ranked list of activities with a "why it fits" rationale, a map with pins, and an optional conversational refinement sidecar. SSR renders the ranked rail on the first paint, with the default state already showing current weather + Ottawa–Gatineau + 6+ options before the user does anything. A constrained URL is indexable and shareable.

**Scope:**
- SSR shell + default state ("the map renders with the chat empty"; design rule from the interface ADR §1.4/§2).
- Chips: weather (keep any / dry / avoid precip / keep warm / avoid cold / avoid heat / avoid storm), cost (max budget + preferred classes), people (solo/pair/family/group), time (morning/lunch/evening/late + date window).
- Chat input (optional, deluxe path): free text + exclusions + 🎤 STT; writes the same canonical `FilterState` as the chips.
- Ranked card rail + "why it fits" + "not this" exclusion toggle + "rain plan" backup control.
- Degrade contract (interface ADR §8): LLM down → chips-only parse; engine empty → relaxation suggestions; weather entirely missing → partial + warning; map provider down → list view.
- SSR + indexed constraint URL (e.g. `thingztodo.app/?lat=&lng=&weather=no_rain&budget=50`).

**Why:**
- This is the smallest thing that is real. It delivers the first user's exact moment: "tonight, weather + budget constrained, 1–2 people." Every other feature hangs off it.
- Decision 1 (web-first) and Decision 3 (Ottawa–Gatineau, "tonight" user) are already accepted. The interface ADR already encodes the reference layout and design rules.
- Research says the value is in *situation-fit output with rationale*, not novelty (demand-validation §4; interface ADR design rule 4).
- The "deprivation, not overload" finding means the first render must be fast and the default list must already have ≥6 options (demand-validation §7 item 4).

**Alternatives rejected:**
- Chat-first primary surface: 26% AI-session abandonment, 1% click-through inside AI summaries, and documented user resistance to being told what to do. Chat is the best *input* surface, not the best *output* surface.
- Search-first, map-second layout: the map is the orientation layer; pins carry interest and price together; the sidecar keeps the answer on one screen.
- Native mobile app first: doubles build cost for marginal v1 retention; one responsive web surface iterates faster.

**Consequences for the release:**
- This is the entire v1 consumer UX. All other v1 features are value-adds on top of this funnel.
- The canonical `FilterState` schema (interface ADR §7) is the contract UI, LLM, API, and engine share.

---

## Decision 2 — Ground-truth catalog + live weather gating

**What is decided:**
v1 ships a **seeded, curated Ottawa–Gatineau activity catalog** with indoor/outdoor/mixed, opening hours (timezone `America/Quebec`), price + price class, party-appropriateness, venue coordinates, and season, fed by **live Open-Meteo weather** materialized into the catalog cache. This drives the two-tier engine's hard gates (cost/time/distance + `avoid_*` weather rules) and soft score. The moat is ground truth, not the AI.

**Scope:**
- Curated catalog filter (`SQLiteCatalogStore`): ~50–100 Ottawa–Gatineau activities with the engine's required fields (§3.1 of the engine ADR).
- Weather source: Open-Meteo (free, no key, hourly), materialized into the catalog weather-cache at ingest so query time is ~free (framework ADR §1; engine ADR §8 caching).
- Two-tier engine: Tier 1 hard gates (budget, time-overlap, distance, `avoid_*` weather rules) + Tier 2 soft score (weather comfort, cost headroom, party fit, time-of-day peak, distance decay, intent, seats).
- Engine emits `matched`/`unmet`/`reasons` per candidate so the UI can show "why it fits" and, on a narrower refine, "why this was excluded."
- Cold-start safeguard: a curated fallback list is surfaced when provider feeds are empty, never a silent "no results" (engine ADR §8.3).

**Why:**
- The interface ADR §1.8 + competitors map §6: "Ground truth is the moat, not the AI." Without a real catalog and live weather, the surface shows empty or fabricated results, and the product is a thin wrapper over someone else's inventory.
- Weather is a direct demand gate: 72% of surveyed app users say weather plays a key role in activity planning; 97% of winter-sport users consult the forecast (demand-validation §2.4; recreation science in engine ADR §5.1).
- The first user is weather- and budget-constrained; the engine must actually enforce their situation.

**Alternatives rejected:**
- Scrape + aggregate generic open-source listings: no live hours, no weather, no situation-specific truth; recreates the thin-wrapper failure.
- Let the LLM invent recommendations: violates the anti-hallucination guarantee and hands away the ground-truth moat.

**Consequences for the release:**
- This is the data layer all of Feature 1 reads from. Cache freshness (stale-while-revalidate) keeps the answer honest.
- Engine ADR §7 open item #2 (which weather provider to integrate) is resolved by choosing Open-Meteo now (free, no key) with the paid-vendor escape hatch as a one-config change.

---

## Decision 3 — Follow-through + verified backup (the unowned interface)

**What is decided:**
When a user picks an activity, the product **closes the loop**: outbound plan (get directions, send the plan to the group via a shareable guest URL that needs no account), and when the top pick is outdoor and the weather has gated it out, immediately offer a verified indoor alternative ("rain plan"). Voice output is a spoken summary of the top option + a link pushed to the phone, never a transcript.

**Scope:**
- **Get directions** → Nominatim/OSM directions from the venue.
- **Send plan to group** → shareable guest URL encoding the live constraint state; ~30-day persistence; no account needed for either party; the most natural viral loop for a group ("what should WE do tonight" — demand-validation §3.2).
- **Weather-gated indoor backup:** when the top pick is outdoor and `avoid_precip`/`avoid_rain` gated it out, show a verified indoor alternative under a "rain plan" control. This is the differentiator Scout flagged (interface ADR §1.4; demand-validation §7 item 5).
- **Voice:** input modality only (STT → same parse path); output = spoken summary of top option + link to the phone (interface ADR §5.3). No chat transcript read aloud.

**Why:**
- People say but do not follow through: 26% of AI activity sessions are abandoned; only 1% click inside AI summaries (demand-validation §4; interface ADR §1.4). The executable next step is where value lives.
- The verbatim user sentence ("not at home") plus the repeated "what should WE do tonight" group signal mean the product must work as a shared, actionable answer — not a private suggestion (demand-validation §3.2, §7 item 6).
- Premium must never gate the core value (Decision 2); a group in the rain needs the backup *now*, not after a paywall.

**Alternatives rejected:**
- Delay follow-through to a premium tier: contradicts the accepted no-paywall model and the "never gate the answer" rule.
- Chat output read aloud: fights the 26% abandonment signal; voice is input-only.
- Public chat transcript as the output surface: the map is the persistence layer; chat scrolls away.

**Consequences for the release:**
- This is the "now what" that prevents abandonment and completes the first user journey (land → rank → pick → act).

---

## Release UX flow (what a user actually does)

1. Lands on the page → SSR renders **default state**: current weather + Ottawa–Gatineau + 6+ ranked options. (Feature 1, first-paint.)
2. Refines with **chips** (or the optional chat sidecar) → the **two-tier engine** (Feature 2) re-ranks → ranked rail re-renders with "why it fits" and fresh pins. (Feature 1 + 2.)
3. Clicks an activity → **detail card** → picks "get directions" or "send to group" (Feature 3).
4. If the top pick is outdoors and rain gates it out → **"rain plan"** immediately offers a verified indoor alternative. (Feature 3.)
5. Constraint state is encoded in the URL → indexable, shareable to the group, no account. (Feature 1 + 3.)

---

## Acceptance criteria for the release (the "done" bar)

| # | Criterion | Level | How verified |
|---|---|---|---|
| 1 | Landing on the page renders a ranked rail with ≥6 options in the default Ottawa–Gatineau state, before any user input | E2E | Playwright: home page load → rail populated |
| 2 | Changing a chip (weather/cost/people/time) re-ranks the rail with "why it fits" + excludes hard-gated candidates | E2E + unit | Chip click → rail re-render; golden-matrix regression |
| 3 | Engine hard gates (budget < activity price, closed today, >radius, no-rain outdoor) exclude candidates and list the reason | Unit | Exhaustive boundary table |
| 4 | Open weather/close engine: "is it open now" uses cached Open-Meteo + theatre hours, timezone-correct | Integration + E2E | Zeitgeist; weekend-hours case |
| 5 | "No results" is a reasoned empty with relaxation suggestions, never a silent blank | E2E | Exhausted-filters scenario |
| 6 | Shareable guest URL encodes the constraint state and loads the same plan with no account | E2E | Round-trip (save → URL → load) |
| 7 | "Get directions" resolves to the right venue | E2E | Nominatim round-trip |
| 8 | Rain plan: when the top outdoor pick is gated out, a verified indoor alternative appears | E2E | Rain scenario |
| 9 | LLM down falls back to chips-only parse; map still renders | Sandbox | Failure-injection |
| 10 | All of the above pass under `SANDBOX=1`; no live external network in CI | CI gate | e2E + sandbox suite |

---

## Tradeoffs stated plainly

- **Feature 1 is broad; it is the product.** The entire v1 UX is one funnel, so "feature 1" is the default-state render + refine path, not a menu of options. It is narrow in the sense that it is *one path*, which is exactly where the 51% deprivation risk concentrates.
- **Feature 2 is narrow in method but carries the moat.** A ~50–100 activity curated list + cached weather is not "big data," but it is the *truth* the product sells. It is scoped to Ottawa–Gatineau so the catalog can be genuinely verified (quality §6 gap #5).
- **Feature 3 is deliberately small.** One outbound action (directions), one share action (guest URL), one backup action (indoor plan). Done once. Expanded later (premium group-coordination) only after retention proves the value.
- **What is deliberately not in v1:** consumer accounts at entry, premium, merchant listings, multi-geography, payments, native app. Each is a real revenue or UX capability, but each is a source of early-friction under Eric's accepted decision 2 (no consumer paywall) and decision 3 (smallest real thing).

---

## Open items

1. **Catalog seeding (Forge + Scout):** the Ottawa–Gatineau curated list must be written to `SQLiteCatalogStore` and the weather cached. This is now a concrete card, not an open question.
2. **`LLM_MODEL` selection** (interface ADR §12 open item #1): confirm the cheapest usable structured-output model at scaffold time. Config, not code.
3. **Energy in v1 remains soft** (interface ADR §7): no engine change needed unless a later ADR makes it hard.

---

## Reference

- `docs/CHARTER.md` §6 — open question OQ5 closed by this record
- `desks/product/2026-10-22-interface-accounts-and-monetization.md` — the source memo this record extends
- `desks/product/2026-10-23-product-decisions-accepted.md` — Decisions 1–3 (product shape, revenue, geography/user)
- `desks/engineering/decisions/2026-10-22-interface-shape-map-first-chat-sidecar.md` — interface architecture + `FilterState` schema
- `desks/engineering/decisions/2026-10-21-activity-filtering-engine-constraints-matching.md` — engine + degrade
- `desks/engineering/decisions/2026-10-21-framework-backend-and-data-store.md` — stack
- `desks/research/demand-validation.md` — the research backing features 1 & 3
- `desks/research/competitors.md` — the competitive map
- `desks/quality/TEST-STRATEGY.md` — acceptance-verification levels

*Prepared by Curator (Head of Product & Design), 2026-10-24. Research inputs traced to Scout's labelled desks; architecture traced to Forge's accepted ADRs. No figure is presented as a verified market number beyond those labelled as such in the source desks.*
