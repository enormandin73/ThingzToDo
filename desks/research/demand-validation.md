# Demand-Validation Memo — ThingzToDo

**Author:** Scout (Research & Marketing, ThingzToDo)
**Date:** 2026-10-21
**Feeds:** t_23e30ea2 (demand validation, already completed) · this synthesis (t_cd3824b4)
**Input tasks:** t_3b33beb6 (search volume) · t_660d1008 (seasonal/weather) · t_b18cda78 (forum/Reddit) · t_c9d78503 (app-store complaints) · t_fe2dc987 (literature/solutions)

---

## 1. Verdict (clear, in one sentence)

**Real.** Activity demand for "what to do, given the situation I'm actually in" is large, frequent, and seasonal — millions of head-term searches, recurring 1.8× (or larger) seasonal swings, and a fast-growing urgency slice — and the decision-friction problem that drives it is corroborated across independent sources (search, search volume, social posts, app-store complaints, and behavioral science). The demand is **real at the search/behavioral level**. The *solution-adoption* demand — people actually paying for or reliably adopting a weather+cost+people+time-personalized, follow-through-ready tool — is **real but unproven at scale**, because head terms are already dominated by established incumbents and no verified market-size number exists for the specific state-conditioned need.

Three caveats, quantified below: (1) the demand pool is large but crowded at the head; (2) people are already partially served by search/AI for general discovery; (3) the specific "state-conditioned" combination has no verified market-size number.

---

## 2. What people actually search for (quantitative, the "real" half)

### 2.1 Head terms — US, ~5.0M searches/month
From Google-sourced keyword data via Seoluma (single-source estimates, labeled so throughout):

| Query | US estimates, monthly avg |
|---|---|
| things to do | 2,740,000 |
| things to do near me | 2,240,000 |
| attractions and activities near me / attractions near to me (related) | 2,240,000 |
| tourist things near me | 1,500,000 |
| fun things to do near me | 368,000 |
| things to do with kids | 40,500 |
| things to do outdoors near me | 4,400 |
| fun things to do today near me | 8,100 |

**Head-term pool: ~2.74M + ~2.24M ≈ 5.0M US searches/month** for the two core phrases. Adding nearby event-discovery queries pushes the near-me discovery pool to **~3.9M+/month** (2.24M near-me + 1.68M events-near-me, the latter a *sum of 23 distinct queries*, not deduplicated unique searchers). [t_3b33beb6]

### 2.2 Immediate/urgency slice — the fastest-growing part
Same-week / same-day intent from DataForSEO Labs (via Venuera, retrieved 2026-07-26):

| Query | US, monthly |
|---|---|
| events tonight near me | 33,100 |
| events this weekend | 33,100 |
| what events are happening today near me | 1,000 |
| are there any events near me today | 210 |
| **Pool (4 queries)** | **~67,400** |

Across 23 nearby-event queries the pool is **1.68M/month**. The urgency slice is the growth story: same-day event searches are growing **+255% YoY** for "are there any events near me today" (+51% for "what events are happening near me", +30% for "what events are happening today near me"). Combined same-week/same-day volume **~128K/month** and is the fastest-growing segment. [t_3b33beb6 · t_660d1008]

### 2.3 Seasonality — demand swells, clearly
- **"Things to do" spikes every summer** on Google Trends (US) — pattern claim, relative 0–100 scale, via a cited blog post. [t_660d1008]
- **"things to do do near me" peaks in August (~3.35M) and bottoms in January (~1.85M)** — a **1.8× swing**. [t_3b33beb6 · t_660d1008]
- **Seasonal spikes documented:** "board games for kids" ~1,300/mo normally → **20,000+ around Christmas**; "outdoors eating near me" 40,500/mo (inherently warm-weather). [t_3b33beb6 · t_660d1008]
- **Activity-type curves** (Alpn.ai, 5-year Google Trends): winter sports peak Jan; ice fishing Nov–Dec; summer water sports Jun–Jul; daily biking peaks in the 21–27°C comfort band. Planning searches lead booking by 4–8 weeks. [t_660d1008]

### 2.4 Weather is a direct demand gate (recreation science)
- **Outdoor biking trips peak at 21–27°C (70–80°F)** and drop off below 16°C or above 27°C; above ~25°C most outdoor activity becomes uncomfortable. [t_660d1008]
- **National-park visitation rises with temperature up to ~25°C then declines** (Fisichelli et al. 2015; 82-paper review). [t_660d1008]
- **97% of skiers/snowboarders/snowmobilers use weather forecasts when planning an outing** (AMSC WCAS); **72% of surveyed app users say weather plays a key role in activity planning** (Weather Company). [t_660d1008]

**Search-level read:** The demand pool is genuinely large and clearly non-flat — millions of head-term searches, a 1.8× seasonal swing on the core near-me term, a fast-growing +255% YoY urgency slice, and weather that directly gates participation. The *thingz-to-do* query class is real.

---

## 3. What people say they want (qualitative, the "say" half)

### 3.1 Decision paralysis is the dominant form of the problem — mostly "too few options," not "too many"
- **Choice deprivation (too few options) is 51% of the time**, vs. overload (too many) only 14% — five times more common, and more harmful to satisfaction (e.g., having too few doctors to choose from made US respondents up to 6× less satisfied). [t_fe2dc987]
- **Consequence for ThingzToDo:** a short, boring list is *not* the failure mode most users fear; an over-constrained list is. The product should optimise for "**enough good options**," not "fewer options to avoid paralysis." [t_fe2dc987]

### 3.2 Weather/cost/time are already the natural segmentation signals users ask for
- Forum threads (15–22, 19, 20) self-segment requests by heat wave, rain, holiday, budget — e.g., a fully constraint-stuffed post: *"What to do inside on a hot day that's not at home, isn't eating or drinking, and isn't super expensive for 2 people… Also no arcade, bowling, or movies."* [t_b18cda78]
- r/SideProject comments enumerate exactly the inputs ThingzToDo consumes: *"ask for the current time… inquire about the local weather."* [t_b18cda78]
- The group "what should WE do tonight" is a distinct, repeated relationship chore. [t_b18cda78]

### 3.3 Explicit-ask rate is high
The majority of the 38 threads in the collection are direct requests ("what should I do…", "any suggestions?"), which supports strong *problem* validation — people are actively asking, not silently suffering. [t_b18cda78]

---

## 4. What people actually search for (vs. what they say) — the critical distinction

The synthesis lives here. What people **say** and what people **search** are correlated but not identical:

| Dimension | What people say | What they actually search | Gap / read |
|---|---|---|---|
| **Core problem** | "I can't decide what to do" — decision paralysis, usually *too few options* (51% vs 14%). | "things to do near me" — a **discovery/list** query, not a paralysis query. | People frame the problem as paralysis, but search behaves like discovery. ThingzToDo must lead with **ranked, situation-filtered options** that *look* like a list but are *narrowed* by weather/cost/people/time — the middle path the deprivation/overload tension demands. |
| **Urgency** | "I'm bored / it's hot / it's raining *right now*." | "+255% YoY same-day event searches" — **fastest-growing slice**, ~128K/month. | The urgency slice is the growth lever *and* the product's core moment ("what's viable *today*"). Capture intent with weather+time-of-day fields, not calendar subscriptions. |
| **Inputs** | Self-segment by weather, cost, group size, time of day. | Head terms are generic ("things to do near me"); specificity appears in **long-tail** variants ("things to do outdoors near me today" 1K/mo). | Do **not** win on head terms (dominated by incumbents). Build the onboarding to be the constraint collector, then target long-tail/seasonal/location-specific queries. |
| **Output expectation** | "Not generic — something new/surprising." | Generic head terms dominate volume. | The defensible edge is **situation-fit output** (cost, people, weather rationale), not novelty for its own sake. |
| **Follow-through** | Repeat asks ("what should WE do *tonight*?"). | AI-generation sessions abandon at **26%**; only **1%** click inside AI summaries. | "Here's an option" is not the product. The executable next step (book/reserve/directions/backup plan) is where the product's value lives. |

**Bottom line:** People say they suffer from decision paralysis, but they *search* like they want discovery. They say "weather/cost/time matter," and search urgency is the fastest-growing slice. The job is to convert the discovery-style search into a **situation-filtered, ranked, follow-through-ready** answer.

---

## 5. Counter-evidence (what could argue the case is weak or unproven)

1. **High search volume ≠ unmet product problem.** Google, Google Maps, Search AI Overviews, TikTok, and review platforms already capture a large share of "what should we do" intent. The head terms are dominated by established incumbents — the demand is real, but a new entrant should target long-tail/seasonal/location-specific queries, not the head. [t_3b33beb6]
2. **No verified market-size number for the specific state-conditioned need.** The 5M+ head-term figures measure *general* "things to do" discovery, not the narrow "what should we do given *this* weather/cost/people/time state" query. That specific combination has **no verified market-size number** — it is inferred from adjacent data. [t_fe2dc987]
3. **Counter-evidence to "the space is underserved":** LLM activity/plan chatbots (Wanderlog Energy Mode, Tripnotes Mood Sync, Google Travel Pace Assistant) already offer mood/energy + weather + cost; WeatherMate merges weather + events in one list; Outdoor Nudge gives a one-mission weather/time answer. The open gap is not "any weather-aware answer" — it's the **specific constrained combination + follow-through**, which no solution owns. [t_fe2dc987]
4. **App-store sample is small and directional.** ~45–55% of the readable review sample shows a target complaint, but the sampling is complaint-weighted (upper-bound), and the core complaint classes are *product-quality* (generic output, stuck state, friction, paywall), **not** "no app helps me decide." [t_c9d78503]
5. **Web/forum data is largely unverified.** 95% of threads have unverified dates; content reconstructed from indexed snippets; pages bot-blocked. [t_b18cda78]
6. **Anti-recommendation sentiment exists.** One rant thread shows people resist being told what to do ("who asked for your opinion?"). Design implication: earn recommendations, don't push them. [t_b18cda78]

**Strongest counter-argument assembled:** The demand is real in aggregate, but the *specific* "give me a ranked list constrained by today's weather, my budget, and my group size" query is not what the 5M head-term searches measure — the head terms measure discovery, and discovery is already well-served by search. What's unproven is whether a new entrant can capture a durable share of a fragmented, incumbent-dominating market. [t_3b33beb6 · t_fe2dc987]

---

## 6. Evidence ledger — what is verified, what is unverified

### Verified (source-tagged)
- ~5.0M US "things to do" / "things to do near me" searches/month — Seoluma/Google Keyword Planner (single-source estimates, label as estimates). [t_3b33beb6]
- 1.68M/month event-discovery pool (23 queries, not deduplicated); ~67.4K immediate events queries; urgency +255% YoY — DataForSEO Labs via Venuera (2026-07-26). [t_3b33beb6 · t_660d1008]
- 1.8× seasonal swing on "things to do near me" (Aug 3.35M vs Jan 1.85M); summer "things to do" spike — Seoluma via Google; Google Trends pattern via cited blog. [t_3b33beb6 · t_660d1008]
- 21–27°C comfort band, drop-off above 25°C — PLOS Climate review of 82 papers (AMC studies, Fisichelli 2015). [t_660d1008]
- 97% winter-sport forecast use; 72% weather key in planning — AMSC WCAS; Weather Company. [t_660d1008]
- Choice deprivation 51% vs overload 14% (7,400 participants, 6 countries) — Reutskaja 2022 via Behavioral Scientist. [t_fe2dc987]
- AI session abandonment 26%; only 1% click inside AI summaries — iPullRank (Pew). [t_fe2dc987]
- "No existing solution combines weather + cost + party-size + time-of-day + preference into one ranked list" — gap map from literature review. [t_fe2dc987]
- 4 complaint categories with directional frequency, sample = 16 apps / 11 readable / ~20 review units, labeled directional & upper-bound — t_c9d78503.

### Explicitly unverified (label as such)
- Google Trends relative series not programmatically extracted (public API returned 400; explore endpoint embedded client-side JS) — stated as limitation, not fabricated. [t_3b33beb6]
- Review counts for PlayCompass and ThingsToDo (Play) unverified; Play-complaint quotes are snippet/indirect. [t_c9d78503]
- All but verbatim-in-page quotes (App Store pages) are snippet/indirect — flagged throughout. [t_c9d78503]
- Exact thread dates (95% unverified) and full thread text (reconstructed from snippets). [t_b18cda78]
- "things to do in [city]" generic volume unavailable (only DFW-weekend example); seasonal month-terms and "activity ideas" / "what should we do" unavailable in the sampled free tool. [t_3b33beb6]
- No verified market-size number for the specific state-conditioned need — inferred from adjacent data. [t_fe2dc987]

---

## 7. What this means for ThingzToDo (the read for the product team)

1. **Demand is real and should be treated as a real market.** It is large (millions of searches), frequent (1.8× seasonal swing; weekend/urgency growth +255% YoY), and the decision-friction problem is corroborated by search, social, app-store complaints, and behavioral science independently.
2. **Win the long tail, not the head.** Head terms are incumbent-dominated; target location-specific, seasonal, and weather-triggered long-tail queries.
3. **Make weather + calendar the primary filter,** and time marketing to measured peaks (summer general discovery; Apr–May for summer peaks; winter for snow; Halloween publishing in August; New Year's Eve in October). [t_660d1008]
4. **Optimize for "enough good options"** (deprivation 51% > overload 14%), show 3 rigorously filtered options per time block with a "why it fits" rationale, and keep the list ≥~6 options to avoid frustration. [t_fe2dc987]
5. **Own follow-through:** real-time verification of weather/price/availability + an executable next step (reserve, get directions, add to calendar, built-in backup/indoor plan). This is the unowned interface (26% AI-session abandonment). [t_fe2dc987 · t_c9d78503]
6. **Be explicit in onboarding about the situation inputs** (weather, cost, party size, time of day) — users already self-segment by exactly these; collect them early and use them to rank.

---

*Copyright notice: This is a research input for the ThingzToDo product team, not for external publication. Claims are tagged to a source; unverified claims are explicitly labeled. Do not treat keyword-volume figures as exact.*  
*Prepared by Scout, Research & Marketing desk, 2026-10-21.*
