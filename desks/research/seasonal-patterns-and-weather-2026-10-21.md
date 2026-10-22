# Seasonal Patterns & Weather as a Driver of Activity Demand

**Author:** Scout (Research & Marketing) · **Date:** 2026-10-21
**Feeds:** demand-validation memo (t_23e30ea2) · parent task t_660d1008
**Status:** Complete — seasonal pattern summary with supporting evidence

---

## Bottom line (verdict)

There is **strong, multi-source evidence** that activity demand is strongly seasonal and
weather-sensitive, and that **urgency drives the fastest-growing part of the demand pool**.
"Things to do" searches spike every summer (Google Trends, confirmed). Same-week / same-day
"events near me" queries (~128K/month in the US, growing 255% YoY) are the fastest-growing
segment. Weather directly gates outdoor recreation: temperature has a clear band of comfort
(roughly 21–27°C for biking), a drop-off above ~25°C, and snow/precipitation are positive
drivers for snow-based activities and negative for most others. The actionable insight for
ThingzToDo: **season and weather are not just background — they are the primary filters and
the primary growth levers.** The product should be built to respond to a *current weather
and calendar state*, and marketed hardest in the shoulder/warm seasons.

---

## 1. What people search: "things to do" is a real, recurring, seasonal demand pool

### 1a. General "things to do" searches
- Google Trends (via beomniscient.com/Omniscient Digital, data current as of Summer 2024):
  **"Things to do" spikes every summer in the US.** [Source: beomniscient.com blog; Google
  Trends screenshot referenced in that post] — this is a convenient, independently citable
  confirmation that the general demand pool swells in the warm season.
- Google Trends is on a **relative 0–100 scale** (100 = peak for the term/timeframe), so this
  is a *pattern* claim, not a volume claim. Google's own Trends help notes it is "not a perfect
  mirror of search activity."

### 1b. Keyword volume (larger "near me" pool)
- **"things to do do near me" ≈ 2,240,000 US searches/month** (Google data via Seoluma keyword
  tool). Demand **peaks in August (~3.35M)** and **bottoms in January (~1.8× swing)**.
  [Source: seoluma.com keyword page; Google-sourced monthly search volume]
- **Across 23 event-specific "near me" / local-discovery queries ≈ 1.68M US searches/month**
  (DataForSEO Labs, retrieved 2026-07). Adjacent broader pool (adding "things to do near me") → **~3.9M/month**.
- **Same-week / same-day urgency is the growth story:** "events near me this weekend"
  (60.5K/mo), "events tonight near me" (33.1K/mo), "events this weekend" (33.1K/mo), and
  same-day variants (~1K–21K) total **~128K searches/month** and are the fastest-growing
  segment: "are there any events near me today" **+255% YoY**, "what events are happening near
  me" **+51%**, "what events are happening today near me" **+30%**. [Source: Venuera blog,
  DataForSEO Labs data, July 2026]

### 1c. Implication
The demand pool is large (~3.9–4M/month for event+activity discovery in the US alone), it is
**not flat** (1.8× swing on "things to do near me"), and the **urgency slice is growing fastest**.
ThingzToDo's core query class is real.

---

## 2. Weather as a direct driver (quantitative, from recreation science)

### 2a. Temperature: a comfort band, then a cliff
- **Outdoor biking trips are highest at 21–27°C (70–80°F)**, drop slightly above 27°C, and
  drop substantially below 16°C (60°F). [Source: AMC Studies of Weather & Recreation, cited in
  PLOS Climate review]
- **National-park visitation rises with temperature up to ~25°C (77°F), then declines**
  (Fisichelli et al. 2015; review of 82 papers). [Source: PLOS Climate, "Effects and perceptions
  of weather, climate...")
- Above ~25°C, park visitation — and presumably most outdoor activity — falls. This is a
  concrete "too hot to go out" threshold.

### 2b. Precipitation & snow: reverse signs per activity type
- **Visitation generally declines as precipitation increases** (monthly/daily level). [PLOS review]
- **Snow-based recreation is weather-positive:** more snow/snow depth → more ski-resort
  attendance; higher temperatures → fewer ski visits. [PLOS review; Englin & Moeltner 2004]
- **Warm-weather seasons expand, snow seasons shorten** with warming: earlier snowmelt and later
  winter onset lengthen warm-weather access and compress winter. [USDA Forest Service adaptation
  report]

### 2c. Seasonal visitation shape (US parks, month-level)
- Mountain parks: visitation ramps spring → **peaks June–August** (ideal temps, limited
  precipitation) → declines into winter; a smaller **fall secondary peak**.
- Arid parks: **peak March–May** (most suitable temps between cold winter and hot dry summer),
  decline in hot summer, secondary smaller fall peak. [PLOS Climate, PLOS CLIMATE]
- **Rainy-season / cold months → lower visitation; pleasant shoulder months → higher.**

### 2d. Non-US confirmation (Korea tourism/leisure demand)
- Tourism/leisure demand is **highest in spring (Mar–May) and fall (Sep–Nov)** when thermal
  comfort is good, then **lower in summer**; **precipitation, extreme heat, and extreme cold
  significantly reduce demand**, and **outdoor activities are more weather-vulnerable than
  indoor** ones. [Korean Journal of Climate Research, "기후 요소가 관광·레저 활동 유형별 수요에
  미치는 영향"] — useful as a non-US, general-sentiment anchor for weather gating.

### 2e. Real people use forecasts to decide
- **97% of skiers/snowboarders and snowmobilers use weather forecasts when planning an outing**
  (American Meteorological Society, Weather, Climate, and Society); poor road conditions /
  rain/freezing rain → postponement or cancellation. [Source: AMSC WCAS paper]
- 72% of surveyed app users say checking the weather plays a **key role in activity planning**
  (The Weather Channel / Weather Company). [Source: Weather Company newsroom, Activities
  Forecasts announcement]

---

## 3. Seasonal curves by activity type (Google Trends, month-by-month)

From Alpn.ai's "How search volume shifts tell you what to write (and when)" — each activity has
a reproducible annual curve (5-year Google Trends view):

| Activity type | Planning/search curve | Peak | Driver |
|---|---|---|---|
| Winter (ski lessons, snowboarding) | builds Oct, peaks Jan, flatlines by Apr | **Jan** | Snow/ice conditions + indoor-weather alternatives |
| Ice fishing | peaks Nov–Dec as cold snaps hit | **Nov–Dec** | Cold snaps |
| Summer (whitewater rafting, kayaking, hiking, camping) | climbs Mar, peaks Jun–Jul, drops after Aug | **Jun–Jul** | Warm, dry, accessible conditions |
| Fly fishing | rises Feb, broad peak May–Sep | **May–Sep** | Warm, wet conditions + fish runs |
| "Things to do" (general) | **spikes every summer** | **Summer** | Warm, dry, accessible conditions |
| Daily biking | peaks 21–27°C, drops below 16°C or above 27°C | **Late spring–early fall** | Comfort band |
| Fall foliage tours | planning spike late Aug | **Sep–Oct** | Foliage + cool temps |
| Warm-climate escapes (Florida kayak, Gulf Coast charters) | **inverted: peak Nov–Feb** | **Winter** | Nothern travelers seeking escape |

**Key relational point:** planning searches lead booking by 4–8 weeks, which leads the actual
activity by another 2–6 weeks. A summer-peak activity (July) has its **highest-intent search
months in April–May**. [Source: Alpn.ai, "How search volume shifts tell you what to write
(and when)"]

---

## 4. Calendar / event seasonality (independent of weather)

- **Eventbrite Q4 2024:** 167,000 **daily** searches for Halloween & fall events; 10.4M total
  ticket buyers; 22% of tickets discovered on the marketplace. Top fall ticket drivers:
  pumpkin patches, corn mazes. Mid-to-late **August is the "sweet spot" to publish Halloween
  events** (buyers search/up to 8 weeks out). [Source: Eventbrite blog, seasonal event trends]
- **Holiday seasonality (general apps):** holiday season (late Nov–Jan) and back-to-school
  (Aug–Sep) drive the largest download spikes across nearly all app categories. Travel apps
  peak Jun–Aug (summer vacation planning → travel season). Weather apps see spikes in regions
  with unpredictable climates. [Source: tolinku, adapty, apptweak seasonality guides]
- **Implication:** ThingzToDo can run **seasonal marketing campaigns tied to these calendar
  events** (Halloween, Thanksgiving/fall, summer, winter holidays) that ride on top of the
  weather-driven demand.

---

## 5. Forum / qualitative evidence: how people actually decide

- **r/travel:** When planning weather-dependent trips, users report a **multi-wave decision
  process**: research seasonal averages → check ~5-day forecasts → decide/confirm → "flexibility
  is key" → maintain **backup plans** (indoor/gallery/bar/cafe) for bad weather. People delay
  final confirmation until the forecast is reliable. [Source: reddit.com/r/travel]
- **r/weddingplanning:** outdoor events require **real-time weather adjustment** — heaters,
  tents, indoor fallback, guest communications on temperature/wind/rain. [Source: reddit.com/r/weddingplanning]
- **r/weather:** users **distrust single app forecasts**, cross-check radar/NOAA/NWS, and make
  go/no-go calls on activity based on probability and radar. [Source: reddit.com/r/weather]
- **Pattern:** the decision is iterative and weather-gated; there is a **gap between "wanting to
  do something" and "having a go/no-go, weather-aware recommendation"** — exactly the void
  ThingzToDo fills.

---

## 6. Quantified seasonality summary (table)

| Signal | Peak | Bottom | Magnitude / swing | Source |
|---|---|---|---|---|
| "Things to do" Google Trends (US) | Summer | Winter | Spikes every summer | beomniscient / Google Trends |
| "things to do do near me" (US, monthly) | Aug | Jan | ~3.35M vs ~1.85M; **1.8×** | Seoluma / Google |
| Event discovery (23 queries, US) | Summer/warm | Winter | ~1.68M/mo pool | DataForSEO Labs / Venuera |
| Same-day "events near me today" | Weekend/same-day | — | **+255% YoY** growth | DataForSEO Labs / Venuera |
| National-park visitation | Jun–Aug | Wet/winter months | Clear summer peak | PLOS Climate |
| Outdoor biking trips | 21–27°C band | <16°C or >27°C | Significant drop-off | AMC studies (PLOS) |
| Ski visitation | Jan–Feb | Summer | Snow-positive, heat-negative | PLOS review |
| App downloads (all categories) | Holidays + back-to-school | — | Largest spikes | tolinku / adapty |

---

## 7. Limitations (explicitly labeled)

1. **"Things to do / events near me" volumes are single-source keyword estimates** (Seoluma
   via Google; DataForSEO Labs for event queries). They are estimates and should be re-verified
   with Google Keyword Planner before budget decisions. Relative *pattern* claims (Google Trends
   "spikes every summer") are more robust than absolute volume claims.
2. **No direct panel data tying a "what should we do" query to the weather on that exact day.**
   The weather-gating linkage is inferred from (a) activity-type search curves and (b) multiple
   independent recreation-science studies showing temperature/precipitation thresholds. This is
   a reasonable inference but not a direct measurement.
3. **Geographic concentration:** the volume search data is **US-centric**. The Korea tourism
   study provides a useful non-US anchor but reflects a different climate and culture.
4. **Google Trends is relative (0–100)**, not absolute volume — so cross-term comparisons must
   be made within the same term and timeframe.

---

## 8. What this means for ThingzToDo (recommendation)

1. **Make weather + calendar the primary filter/onboarding path**, not a secondary amenity.
   Users arrive with a weather state; the product should recommend what's viable *today* and
   *this season*.
2. **Build the urgency loop** around same-week searches ("this weekend", "tonight") — the
   fastest-growing demand slice — with same-day availability, quick re-pivot on forecasts, and
   a built-in backup/indoor plan for when conditions turn.
3. **Time marketing to the measured peaks:** summer general discovery, late-winter/early-spring
   for warm-weather activity planning (Apr–May for summer peak), winter for snow-based
   activities, and calendar events (Halloween/fall publishing in Aug, New Year's Eve in Oct).
4. **Own the "backup" slot:** the r/travel pattern shows people want Plan B when weather turns —
   an indoor/indoor-weather activity filter is a genuine differentiator, not a nice-to-have.

---

*Prepared by Scout, Research & Marketing, ThingzToDo. All claims tagged to a source; anything
not directly verifiable is labeled. Do not treat keyword-volume figures as exact.*
