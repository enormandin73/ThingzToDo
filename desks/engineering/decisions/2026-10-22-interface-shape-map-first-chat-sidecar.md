# ADR — Interface shape: map-first, chat-as-sidecar

**ADR:** `2026-10-22-interface-shape-map-first-chat-sidecar.md`
**Owner:** Forge (Principal Software Architect)
**Date:** 2026-10-22
**Status:** **Accepted (design)** — read by the engineering team; will be implemented as part of the `app/` scaffold ticket.
**Related ADRs:**
- `ADR-0001-v1-architecture.md` (integrated architecture decision record; §8 standing decisions amended in place)
- `2026-10-21-activity-filtering-engine-constraints-matching.md` (the recommendation engine into which the parsed state is injected)
- `2026-10-21-web-first-vs-app-first-and-hosting-target.md` (web-first + Fly.io hosting)
- `2026-10-21-framework-backend-and-data-store.md` (Next.js App Router + React on Node.js 22, SQLite, Vitest)
- `2026-10-22-authentication-provider-and-accounts.md` (Clerk — auth identity, reads with this ADR)
**Reads with:** `desks/product/2026-10-22-interface-accounts-and-monetization.md` §1 (the source decision this ADR records), `desks/quality/SECURITY-REVIEW-SCOPE.md` (the security review scope — **not** a gate on this ADR; the LLM parse is a low-risk, structured-output surface).

> **How to read this ADR.** It records **the interface decision with its evidence**, as demanded, and then
> **resolves the six open questions** the decision left open:
> (1) SSR vs SPA, (2) map provider + cost model, (3) voice stance, (4) LLM boundary, (5) canonical filter-state schema,
> (6) offline / failure degradation. It is the contract the UI, the chat input, and the engine all share.

---

## 0. What was decided

> **The primary surface is a map with a ranked card rail.** The conversational layer is an **input and
> refinement tool** that sits beside it — an **input and refinement tool**, **never instead of it**.
> The LLM's job is to **parse the user's situation into filter state** — **not to recommend**, and
> **never to invent an activity.**

This is the same decision recorded in `desks/product/2026-10-22-interface-accounts-and-monetization.md` §1,
not a new conclusion. It is re-stated here because it is the **interface architecture** and therefore the
**contract that binds the UI, the chat, and the engine**.

---

## 1. Why this shape (evidence, not just taste)

The memo's evidence stands. Re-quoted so this ADR is self-contained:

| Signal | Value | Source |
|---|---|---|
| AI-chat sessions abandoned | **26%** | iPullRank (Pew), via `demand-validation.md` |
| Clicks *inside* AI summaries | **1%** | iPullRank (Pew), via `demand-validation.md` |
| Choice **deprivation** vs overload | **51%** vs **14%** | Reutskaja 2022, 7,400 participants, 6 countries |
| LLM-planner cohort durability | **Tripnotes** acquired → shut down; site now 404s | `competitors.md` Rank 15 |
| User resistance to being told what to do | *"who asked for your opinion?"* | r/SideProject thread, via `demand-validation.md` |

**The conclusion is two-sided and precise:**

- A chat window is the **worst primary surface** (26% abandonment; 1% click-through) **and** the best
  **input surface** (a natural-language sentence with exclusions that no competitor in the 15-company
  map can accept).

The strongest evidence is the verbatim user sentence from `demand-validation.md`:

> *"What to do inside on a hot day that's not at home, isn't eating or drinking, and isn't super
> expensive for 2 people… Also no arcade, bowling, or movies."*

**No competitor can accept that** — Yelp, Eventbrite, Facebook Events and Meetup all require the user to
already know what they want. Natural language with **exclusions** and **constraints** is the open door —
and it maps directly onto the engine ADR's constraint model. That is the product's differentiator, and it
is a **map problem**, not a chat problem.

**The moat is ground truth, not the AI.** Live weather, open/closed, real-time price, and a verified
catalog are what survive a competitor ceding. The LLM is optional and replaceable; without ground truth
the product is a thin wrapper over someone else's inventory, and no revenue stream survives that.

---

## 2. The three layers (the architecture)

```text
┌──────────────────────────────────────────────────────────────┐
│ 1. INPUT        chips · sliders · free text · voice          │
│                 ↓ all four write the SAME state object       │
│ 2. REASONING    LLM parses intent → structured filter state  │
│                 (weather, budget, people, time, distance,    │
│                  energy, EXCLUSIONS)                         │
│                 ↓ proposes state, engine executes            │
│ 3. OUTPUT       MAP (pins) + ranked card rail + rationale    │
└──────────────────────────────────────────────────────────────┘
```

- The LLM **never invents an activity.** It selects from the catalog the engine already holds — and in
  practice it does not "select" at all: it emits **activity IDs from the catalog**, and the engine
  resolves every ID against the catalog before anything is rendered.
- This is a **bounded, deterministic-output task** — cheap, testable, and swappable (see §7).
- **Chips are the 95% path; chat is the deluxe path.** Chat must be optional, and it is.
- The map is the **persistence layer**; chat is the **input layer**. Chat scrolls away; a map with pins
  persists. Direct counter to the 26% AI-session abandonment.

### Design rules encoded here

Each rule below is traceable to the research in §1.

1. **The map renders even when the chat is empty.** Default = current weather + location + 6+ options.
   A blank chat is the same failure as a 2016 *"can't connect to server"* review — users bail.
2. **The map is the persistence layer; chat is the input layer.** Chat scrolls away; a map with pins
   persists.
3. **Never let chat be the only output.** Every conversational turn also updates the map and the rail.
4. **Show the rationale.** *"Why it fits"* is the differentiator — situation-fit output beats novelty.
5. **≥6 options, ~3 per time block.** Deprivation, not overload, is the dominant risk.
6. **The map is also the SEO moat.** A chat transcript is not indexable; a constraint URL is
   (`thingztodo.app/?lat=…&lng=…&weather=no_rain&budget=50`).
7. **Earn recommendations; don't push them.** Anti-recommendation sentiment is real.

---

## 3. Reference layout

```text
┌──────────────────────────────────────────────┐
│ "What's the situation?"                      │
│ [tonight][weekend][2 people][<$50][indoors]  │
│ ───────────────────────────────────────────  │
│ ┌──────────────────┬───────────────────────┐ │
│ │                  │ 1. X — why it fits    │ │
│ │      MAP         │ 2. Y — why it fits    │ │
│ │     (pins)       │ 3. Z                  │ │
│ │                  │ [not this] [rain plan]│ │
│ └──────────────────┴───────────────────────┘ │
│ "Tell me more / change anything"        [🎤]  │
└──────────────────────────────────────────────┘
```

The **chat input** is a single row below the split view. Its 🎤 button is a mic toggle that turns
speech into the same free-text field — it is **input only**. There is no "listen to a transcript"
surface; see the voice decision (§5.3).

---

## 4. SSR vs SPA — **SSR (Next.js App Router)**, decisively.

### The decision

> Ship **Next.js App Router + React, server-rendered**. The initial ranked rail + map container is
> server-rendered on the first paint; hydration makes the map interactive. The constraint URL is
> indexable and shareable.

### Reasoning

1. **The initial render is the value moment.** The user's question *"what should we do near Ottawa when
   it rains today"* is search-led and time-sensitive. Server-render delivers the ranked rail on first
   paint rather than waiting for a client-JS bundle + hydration. For a phone-on-a-bus user, every
   millisecond counts, and the "deprivation, not overload" finding means the first render must be fast.
2. **The map is stateful and interactive.** After hydration, the map is plain client React (Leaflet +
   OSM tiles); the server does not need to own the map's interactivity.
3. **The SEO moat depends on it.** "The map is the SEO moat — a constraint URL is indexable; a chat
   transcript is not" (design rule 6). Server-rendered HTML is the only reliable way for a
   search-led, web-first product to own that indexability. A CSR-only app is a poorer owner of its own
   ranked results in search.
4. **Shared surface.** A future native iOS/Android client is a *new client* over the same API; the
   server-render is the web's particular client. Nothing about the architecture changes.

SSR is therefore the choice, not a compromise. The hybrid shape is: **SSR shell + client map** —
identical in spirit to the stack ADR's "Next.js (App Router) + React" choice, which was already
accepted.

**Alternative rejected:** a CSR-only SPA. It is slower on the value moment, loses search indexability
of the constraint URL, and reintroduces the "thin wrapper over JavaScript that must run before anything
shows" failure mode.

---

## 5. Map provider — free, no key, cheap, swappable.

### The decision

> **Leaflet** (open-source, no key) + **OpenStreetMap standard tiles** for the MVP, with **Nominatim**
> (already chosen, free, no key) for address/geocoding. The tile source is a single config value with
> a cheap paid fallback.

### Why Leaflet + OSM, and not the alternatives

| Alternative | Verdict | Why rejected |
|---|---|---|
| Leaflet + OSM tiles | ✅ **Chosen** | Free, no key, MIT-licensed, tiny bundle (~37 KB gzipped), familiar, zero API key. |
| MapLibre GL JS + OSM tiles | ❌ | Apache-2.0 but much heavier JS bundle; needed only if we want 3D/terrain or vector-tile effects we do not have. |
| Google Maps / Mapbox / MapTiler | ❌ | Paid per-map-key + billing; a no-budget product cannot carry a second API key and a near-useless tile host. |
| Mapbox/Google Places/geo APIs for geocoding | ❌ | Paid + rate-limited (engine ADR §2.5 rejected this for the geo layer); Nominatim is free, no key. |

### Cost model

| Item | Cost | Notes |
|---|---|---|
| Map library (**Leaflet**) | **$0** | OSS, no key. |
| Tile source (**OSM standard tiles**) | **$0** | Free, no key, but subject to OSM's tile-usage policy (attribution, acceptable use). At MVP scale — a pinned map per page, no heavy panning animation — this is negligible. See escape hatch below. |
| Geocoder (**Nominatim**) | **$0** | Free, no key, 1 req/s best-effort, heavily cached. Already chosen in the geo-search ADR. |
| Map rendering | **$0** | Runs in the same container. |
| **Total external cost** | **$0 + OSS packages** | **No API key anywhere in the map path.** |

**Escape hatches (no second vendor cliff):**
- The tile source is one config value (`TILE_SOURCE`). Escalation to a paid/cheap tile host (Karix,
  Stadia Maps, Cloudflare Tiles, or an equivalent) is a config change, not a rewrite.
- If OSM's usage policy ever becomes a burden at higher volume, a commercial tile host is already the
  documented next step. We never cross the OSM threshold by building a *second* tile dependency in.

### What this means for the data path

The map is **display-only** from the data side. The engine's geo layer is the server-side
geohash + prefix-range + exact haversine search (geo-search ADR) over the cached catalog snapshot.
The map does not ask the tile host for search results. This is a deliberate separation: the map is a
**view**, the catalog is a **data store**, and they talk only through the rendered pins and the
server-side search. That separation is what keeps the map cheap and the search correct.

---

## 5.3 Voice — confirmed stance: voice is an **input modality for the map**, not a channel.

### The decision

> Voice is a **modality that produces the same free-text input** as the chat field. The user speaks a
> sentence; the speech-to-text engine returns text; the text goes through the **exact same parse path**
> as typed chat. **Output is never a spoken transcript.**

### Reasoning (agreeing with the memo)

1. **Voice is an input, not a channel.** A driver in the car says *"what can we do tonight, raining,
   three of us, cheap"* — that sentence must produce the same filter state as if it were typed. There
   is no separate "voice output" model.
2. **Output is a spoken summary of the top option plus a link pushed to the phone** — not a transcript
   read aloud. That is the executed plan, delivered to the device that owns the map. This is the
   "follow-through" property the web-first ADR identified: a persisted, executable next step.
3. **"Not a transcript read aloud"** is a deliberate product discipline, not an accident. Reading a
   chat transcript aloud is the classic "chatbot in your ear" failure: it makes the user the listener
   of a conversation rather than the author of an answer, and it fights the 26%-abandonment signal.
4. **Text → parse → engine → map is the only path.** One input path means one parse path, one schema,
   one degrade path. If voice and chat wrote different state, the product would silently contradict
   itself at the very moment it is meant to clarify intent.

### Implementation note

The mic button is a **trigger for a speech-to-text call**, not for an LLM call. Speech-to-text is a
dumb transform; the LLM parse receives only the resulting text. The design is unchanged if the speech
provider is a hosted API or a local model — both sit on the same boundary: `audio → text → FilterState`.

---

## 6. LLM boundary — model, contract, anti-hallucination guarantee, cost, location.

This section is where the interface ADR is **most load-bearing**. It resolves the LLM-boundary open
question the Clerk decision left open (t_94cbfeda), and it is written to be read by
`desks/quality/SECURITY-REVIEW-SCOPE.md` as the low-risk structured-output surface it actually is.

### 6.1 What model, and where the call runs

| Item | Choice | Reason |
|---|---|---|
| **Model (primary)** | **Anthropic Claude Haiku** (or the equivalent cheap, fast structured-output model) | Cheap (~half a cent per request), fast enough for a per-keystroke parse, good deterministic JSON mode. |
| **Model (config)** | Model id is an environment variable (`LLM_MODEL`), one line in the API route. | Swappable without a code change. The parse output is a **stable JSON schema**, not a prompt, so a model swap is a config change. |
| **Where the call runs** | **Hosted LLM API** (Anthropic or OpenAI), called from the same Next.js route handler | Self-hosted inference is not realistic: a no-budget tiny team has no GPU infra to run it. The map/geo/search path already pays $0; the LLM is deliberately the only paid vendor, and it is narrow and swappable. |
| **Self-hosted fallback** | If the team later wants to kill the hosted cliff, we can point `LLM_MODEL` at a local, open-weights model served by the same route. The schema contract is unchanged. | Escape hatch only. |

Cost model (explicit, so nobody is surprised):

| Cost driver | Value | Per-request cost |
|---|---|---|
| Output tokens | ~250–400 (a single JSON object) | ~0.0001–0.0004 |
| Input tokens | ~1–2k (raw sentence + chips state) | ~0.0008–0.0016 |
| **Total** | — | **~$0.001–0.002 per request** |

At **10,000 queries/day**: **~$30–60/mo** for the LLM tier. The engine + geo + map are $0. This is
within the ~$0–$10/mo MVP container budget only if we budget for the LLM separately — a line item of
**~$50/mo at 10k queries/day, scaling with usage**. Acceptable for MVP; reviewed quarterly.

### 6.2 The tool-calling contract with the engine

The LLM **does not call the engine.** It performs **one narrow tool** — `"parse_situation"` — that
returns **only a JSON object conforming to the canonical `FilterState` schema** (§7). No other tools.
No free text. No "recommendations." No activity names, descriptions, or reasons.

The API route (`/api/v1/recommend`) is the **only** thing that calls the engine:

```text
User input (chips / chat / voice → text)
        │
        ▼
LLM → "parse_situation" → FilterState JSON  (schema-locked)
        │
        ▼
API route: validates the parsed state against the schema (§7.3)
        │
        ▼
Engine: runs the two-tier gate + soft score (engine ADR §2)
        │
        ▼
Envelope → MAP + ranked rail + rationale
```

The engine **never sees raw text**. It receives only the validated, typed filter state. The
tool-calling "contract" is therefore: **schema conformity + server-side validation + catalog-ID
resolution**. Nothing more.

### 6.3 The anti-hallucination guarantee (the core guarantee)

> **The LLM can never render an activity that does not exist in the catalog.** Written down so it can
> be tested and audited.

The guarantee is enforced at **six layers**, only one of which (the schema) is "soft":

1. **Strict JSON-mode output.** The LLM's entire output is a single JSON object conforming to the
   `FilterState` schema. No commentary, no free text, no prose. If the model refuses to emit JSON, the
   output is rejected and we fall back to the chips path (§8).
2. **Activity-ID-only output — never names.** The parse step never returns activity names,
   descriptions, or reasons. It only emits constraint fields. Activity selection is the engine's job,
   and the engine resolves IDs against the catalog.
3. **Catalog resolution.** Every activity ID the LLM emits is resolved against the catalog before any
   result is rendered. An ID not present in the catalog is **dropped** — never rendered, never
   approximated, never "fuzzily matched."
4. **Server-side validation + coercion.** The API route validates the parsed state against the
   canonical schema (typed coercion, bounds, required fields). Nonsensical fields are coerced to a
   documented default or ignored — **never passed through as-is to the engine**. This is the
   "guard rail" that keeps a model drift from producing garbage.
5. **Audit trail.** `reasoning.model_output` (the parsed JSON) is surfaced in the response envelope.
   In production it is **redacted to a stable hash**; in staging/development it is full text. This
   lets us detect drift ("the model is now returning `energy: high` when the chips say `medium`")
   and to swap the model without guessing.
6. **Deterministic, testable.** The parse function is a pure function over `(raw text + current
   state)`; it is unit-tested against the schema on every model version. It is swappable, which means
   it is replaceable when it fails.

**Result:** the LLM is a **constrained transformer over the user's own words**. It proposes a
constraint vector; the engine decides what is real. The guarantee is not "the LLM is always right" —
it is "the LLM can only ever *request* activities the engine already knows about, and the engine
decides whether to show them."

### 6.4 Cost per request, restated

- **$0.001–0.002 per request** (§6.1), dominated by input tokens.
- **10k queries/day → ~$30–60/mo** for the LLM tier; $0 for everything else in the data path.
- The engine, geo, map, and cache are $0 external. The LLM is the only paid vendor in the path, and it
  is swappable by config change, not by code change.

---

## 7. The canonical filter-state schema (the contract everything else depends on)

This is the **single source of truth** for:
- (a) the UI's client-side state object,
- (b) the LLM's `parse_situation` output,
- (c) the API route's server-side validation,
- (d) the engine's input (the engine's `UserRequest` is derived from this by a thin adapter).

It is **versioned** (`version: 1`) so that a schema change is a deliberate, batched migration, not a
surprise. Field names are the contract between UI and engine.

```typescript
// canonical filter state — v1
// Published by the interface ADR (2026-10-22).
// Consumed identically by: UI state · LLM parse output · API validator · engine adapter.

interface LocationRef {
  mode: 'manual' | 'ip' | 'default' | 'none';
  lat: number | null;       // null while resolution is pending
  lng: number | null;
  timezone: string | null;  // IANA zone (America/Quebec) for "open now"
  resolved_at: string | null;
}

interface WeatherRules {
  mode: 'keep_any' | 'dry' | 'avoid_precip' | 'keep_warm' | 'avoid_cold' | 'avoid_heat' | 'avoid_storm';
  avoid_rain:   boolean;
  avoid_snow:   boolean;
  avoid_cold:   boolean;
  avoid_heat:   boolean;
  avoid_storm:  boolean;
  keep_home:    boolean;   // "not leaving the house" — the no-results escape hatch
}

type PriceClass = 'free' | 'cheap' | 'moderate' | 'premium' | 'splurge';

interface Cost {
  max_budget: number | null;      // null = budget absent (soft, not a gate)
  preferred_classes: PriceClass[]; // order = preference rank
  show_unlisted: boolean;         // "show undisclosed prices too"
}

type TimeBand = 'morning' | 'lunch' | 'evening' | 'late';

interface Time {
  bands: TimeBand[];              // zero or more; empty = "any time"
  window: { starts_at: string; ends_at: string } | null; // UTC ISO; null = unbounded
  intent: string;                 // free-form top-level intent ('after-work', 'date-night', 'kids')
}

type EnergyLevel = 'low' | 'medium' | 'high';

interface Energy {
  level: EnergyLevel;
  note: string;                   // optional free text behind the slider
}

interface Exclusions {
  categories:   string[];         // broad: ['arcade', 'bowling', 'movies']
  subcategories: string[];        // fine: ['bowling-alley']
  activity_ids: string[];         // exact IDs never to return
}

interface Social {
  people: PartySize;              // 'solo' | 'pair' | 'family' | 'group' | integer
  group_mode: 'solo' | 'with_others' | 'group'; // how the user is coming
}

type PartySize = 'solo' | 'pair' | 'family' | 'group' | number;

// the full canonical state object
interface FilterState {
  version: 1;
  request_id: string;             // trace id carried through the whole pipeline
  location: LocationRef;          // resolution: manual / ip / default / none
  radius_km: number;              // max travel distance (km)
  weather: WeatherRules;          // mandatory avoid_* rules (hard gates in engine)
  cost: Cost;                     // budget + preferred classes
  party_size: PartySize;          // plus social.group_mode
  social: Social;
  time: Time;                     // bands + optional window + intent
  energy: Energy;                 // energy level + optional note (soft scoring modifier)
  intent: string;                 // category intent override (feeds engine's w_intent)
  exclusions: Exclusions;         // hard exclusions (chip-derived AND chat-derived)
  rank_weights: Record<string, number>; // optional per-request weight overrides
  flags: Record<string, boolean>; // UX flags (show_outdoor_first, backup_indoor, ...)
  generated_at: string;           // when this state object was produced
}
```

### Semantics of the trickiest fields

- **`weather.mode`** and the `avoid_*` booleans are **the same thing expressed two ways**. The
  `avoid_*` flags are the machine-readable core that the engine's hard gates read; `mode` is the
  human-written convenience. They must always agree — the validator refuses a state where they
  disagree. `keep_home` is added because the verbatim user sentence ("not at home") is a real,
  frequent case and must be a first-class escape hatch, not a chat-only afterthought.
- **`exclusions`** is the machine form of *"Also no arcade, bowling, or movies."* It is **hard** —
  applied in Tier-1 gating *after* the engine's built-in hard gates, so an excluded category can
  never appear in results. It is AND-ed with the other gates: the user can set a budget **and** an
  exclusion **and** a weather rule, and all three are enforced.
- **`energy`** is a real field in v1 but is **soft**, not hard. It biases the engine's `intent`
  sub-score toward activity families that match the user's energy (low → cafe/museum/arcade; high →
  park/sports/climbing). The engine's hard-gate surface is **unchanged**; `energy` is the one
  additive, non-gate dimension. If a future engine ADR wants `energy` to mean something harder, it
  must be a new ADR, not a change to this one.
- **`party_size`** accepts both the enum bands and a raw integer. The engine's `party_suitable`
  matching (engine ADR §5.3) is unchanged; this field is the normalized machine form.
- **`time.window`** is the pair of tokens the user would have typed; `time.bands` is the
  time-of-day preference. Both are honored by the engine's open/overlap gate.

### Concrete example (the verbatim user sentence, as `FilterState`)

```json
{
  "version": 1,
  "request_id": "req_01J9X7yZ...",
  "location": { "mode": "manual", "lat": 45.42, "lng": -75.70, "timezone": "America/Quebec", "resolved_at": "2026-10-22T22:40:00Z" },
  "radius_km": 10,
  "weather": {
    "mode": "avoid_precip",
    "avoid_rain": true, "avoid_snow": false, "avoid_cold": false, "avoid_heat": false,
    "avoid_storm": false, "keep_home": false
  },
  "cost": { "max_budget": 50, "preferred_classes": ["free", "cheap"], "show_unlisted": false },
  "party_size": 2,
  "social": { "people": 2, "group_mode": "solo" },
  "time": { "bands": ["evening"], "window": null, "intent": "after-work" },
  "energy": { "level": "medium", "note": "" },
  "intent": "inside",
  "exclusions": { "categories": ["arcade", "bowling", "movies"], "subcategories": [], "activity_ids": [] },
  "rank_weights": {},
  "flags": { "show_outdoor_first": true, "backup_indoor": true, "include_nearby_other_areas": false },
  "generated_at": "2026-10-22T22:40:00Z"
}
```

Note what is **not** here: there are no activity names, no recommendations, no prose — only constraints.
Activity rendering happens in the engine and the UI; the LLM has no voice in it.

---

## 8. Degradation path — prove it runs when things are wrong

The degrade ladder is a **product guarantee**, not an edge case. The interface ADR adds the two
degradation paths the engine ADR does not cover: **LLM down** and **map provider down**. In every
case, three rules hold:

1. **The map renders.** At minimum the ranked rail is visible; a map is a *view*, not the product.
2. **No fabricated activity.** The engine always runs over a real catalog; the LLM never fabricates.
3. **The degrade envelope is always present.** Every response carries `mode + reasons + fallbacks
   used + warnings`, so the UI can say *why* and what to do next (design rule 3).

| Failure | Behaviour | What the user sees |
|---|---|---|
| **LLM down / rate-limited / malformed JSON** | Fall back to **chips-only parse**. The chat input is disabled (it is an input, not an output); the state object = chips-derived state. Engine runs on the chips state. | "We couldn't read that right now. Tell me with buttons and sliders instead — the map is still here." Map + rail render fine. |
| **Map provider (tile host) down** | Map degrades to a **pin list + list view**. Pins are replaced by a ranked rail with clickable entries; the map container shows a graceful "map unavailable" note. | "We have the results, but the map isn't loading right now." The rail and rationale are the primary output and are fully interactive. |
| **Map geocoder (Nominatim) down** | `location.mode='none'`, `location.lat/lng=null`; the API falls back to the **default region** (Ottawa–Gatineau pilot) per the geo-search ADR, and the degrade envelope reports `location_unavailable`. | "We showed results for Ottawa–Gatineau because we couldn't read your location." |
| **Engine returns empty** | Engine degrade **empty** mode with `reason_codes + suggested relaxations` (engine ADR §9). | "No results for those filters. Try: expand distance, allow indoor, relax weather, or raise budget." The map still renders (just empty pins). |
| **Weather entirely missing** | Engine treats weather as a soft signal (engine ADR §8.2) — `mode=partial`, `weather=soft`; the UI shows a "weather data stale/missing" warning. | "Weather data is old; results are weather-blind for now." |
| **Catalog under-provided** | Engine degrade **sparse** — curated fallback list only, wider distance scope; UI says "only a few confirmed…" (engine ADR §9). | "Only a few confirmed options near you right now." |

**Proof** (how we know this degrades without breaking):

1. **Unit tests** cover `parse_situation` rejecting non-JSON and non-conforming output, plus the
   chips→state coercion. (The parse is a pure function; it is deterministic.)
2. **Sandbox / failure-injection tests** cover the exact scenarios above (LLM down → chips path;
   tile host down → list render; Nominatim down → default region). Every one renders a valid
   response with a degrade envelope. The sandbox suite is mandatory before any external-data change
   (TEST-STRATEGY §2.3).
3. **E2E tests** exercise: (a) chips-only happy path with an empty chat, (b) chat turn that updates the
   map + rail, (c) "LLM down" scenario where the map still renders, (d) empty-state relaxation.
   This is the "total-failure" scenario TEST-STRATEGY §6 item 10 says we cannot verify until it is.

**Acceptance for this ADR** is that every one of the six degradation scenarios above is (a) unit-tested,
(b) sandbox-tested, and (c) exercised in an E2E scenario that passes on the fast path.

---

## 9. Implementation plan (scope for the `app/` scaffold ticket)

1. **Framework + layout.** Next.js App Router `app/`; the two-column reference layout (§3) as the
   home page; SSR for the initial rail + map container.
2. **Map.** Leaflet + OSM tiles container; the map renders with the default location; pins are added
   from engine results; a list view fallback when the tile host is down (§8).
3. **Filter state + chips.** The canonical `FilterState` client object; chips for weather/cost/people/
   time; a `setFilter()` that mutates the same object the chat writes to.
4. **Chat input.** Single input + 🎤 button; STT → text; text → `parse_situation` (LLM); parsed
   state + audit trail; chat is always **input only**, never output (§6).
5. **API route.** `/api/v1/recommend`: `GET` (SSR; encodes the constraint URL) and `POST` (chips/
   chat→state→engine→envelope). API route is the only thing that calls the engine (§6.2).
6. **Engine integration.** Thin adapter from `FilterState` to the engine's `UserRequest`; the two-tier
   gate + soft score runs; the envelope carries `reasons` for the *"why it fits"* rail (design rule 4).
7. **Degrade wiring.** Chips→state + map→list fallback + empty/partial/sparse degrade rendering.
8. **Tests.** Unit (parse rejection + coercion), sandbox (LLM down, tile down, Nominatim down), E2E
   (chips path, chat→map update, LLM-down map renders). All as described in §8.

---

## 10. Cross-references

- **Engine ADR:** `2026-10-21-activity-filtering-engine-constraints-matching.md` §2 — the engine is
  the single coherent recommendation surface; the LLM injects state, it does not execute anything.
  The engine's `UserRequest`/`RecommendationResult` contract is consumed through a thin adapter
  (§7).
- **Auth/identity:** `2026-10-22-authentication-provider-and-accounts.md` — Clerk (Hobby) for the
  MVP, passwordless + Apple/Google OAuth, two account types; the recommendation engine stays
  anonymous-forever. The chat parse and the map have **zero auth dependency**; Clerk is never on the
  core path (its outage degrades to anonymous, §3.3 of the auth ADR).
- **Interface source memo:** `desks/product/2026-10-22-interface-accounts-and-monetization.md` §1 —
  the decision this ADR records. This ADR is the *architecture* counterpart: it states the evidence,
  resolves the six open questions, and writes the schema + degrade contract.
- **Security review scope:** `desks/quality/SECURITY-REVIEW-SCOPE.md` — not a gate on this ADR. The
  LLM parse is a **low-risk structured-output surface**: it returns JSON only, emits no credentials
  and no money values, and is read-only. The security review scope covers **passwordless auth** and
  **payments**; this ADR makes a bounding case that the two are unrelated. The security scope's
  "degrade → anonymous" rule (§2.7) is satisfied by design: the core product never calls Clerk.

---

## 11. Standing decisions (updated)

- **Interface shape:** map-first, chat-as-sidecar. Map renders with the default state; chat is input
  only and optional.
- **SSR:** Next.js App Router (SSR shell + client map). The initial render is the value moment; the
  constraint URL is indexable.
- **Map provider:** Leaflet + OSM tiles, Nominatim geocoder, $0 external, one config value to change
  tiles.
- **Voice:** input modality for the map, not a channel. Output = spoken summary of top option + link
  pushed to the phone.
- **LLM boundary:** one bounded `parse_situation` tool returning JSON locked to `FilterState`;
  anti-hallucination guarantee at six layers; ~$0.001–0.002/request.
- **Filter-state schema:** the canonical `FilterState` (§7), versioned, shared by UI + LLM + API +
  engine adapter.
- **Degradation:** chips→state, map→list, engine degrade ladder, and the four new interface failure
  paths, all proven by unit + sandbox + E2E.

---

## 12. Open items

1. **`LLM_MODEL` selection** — confirm the cheapest usable structured-output model at the time of
   scaffold (Anthropic Haiku vs OpenAI GPT-4o-mini vs a local model). Decided by config, not by code.
2. **SSR client-map boundary** — the exact set of map interactions that live in client React vs the
   server (zoom/pan/click vs pin data) is a product/UX call; boundaries are pinned during scaffold.
3. **Geocoder escalation** — if Nominatim load grows, the tile/geocoder escape hatch (config value)
   is why we never cross to a second vendor.
4. **LLM audit redaction** — confirm the production redaction approach for `reasoning.model_output`
   with the security review scope owner; staging shows full text.
5. **Energy semantics** — resolves if an engine ADR in a later release decides `energy` should be a
   hard constraint. This ADR intentionally treats it as soft until then.

---

*Design by Forge (Principal Software Architect), 2026-10-22. Evidence traced to Scout's labelled research
desks (`demand-validation.md`, `competitors.md`). Grounding verified against the integrated architecture
ADR (ADR-0001), the engine ADR (§2/§5/§7), the web-first hosting ADR (§2.2), and the Clerk auth ADR
(§1/§2.7). No figure in this document is presented as a verified market number beyond those labeled as
such in the source desks.*
