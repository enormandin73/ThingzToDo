# Product Decision Memo — Interface Shape, Accounts, and Monetization

**Date:** 2026-10-22
**Author:** Irock (orchestrator / GM)
**Status:** Recommendations for Eric's decision · not yet ratified
**Triggers:** Eric's request for thinking on (1) chatbot-style interface, (2) map component,
(3) user accounts, (4) monetization.
**Conflicts raised:** `ADR-0001 §4` (Auth / identity = None for MVP) is reversed by §2 below.
Forge owns that ADR; the reversal is carded, not silent.

---

## 0. Sources this memo stands on

| Source | File |
|---|---|
| Charter | `docs/CHARTER.md` |
| Architecture ADR | `desks/engineering/decisions/ADR-0001-v1-architecture.md` |
| Web-first/hosting ADR | `desks/engineering/decisions/2026-10-21-web-first-vs-app-first-and-hosting-target.md` |
| Filtering engine ADR | `desks/engineering/decisions/2026-10-21-activity-filtering-engine-constraints-matching.md` |
| Ranked competitive map | `desks/research/competitors.md` |
| Demand-validation memo | `desks/research/demand-validation.md` |

> **Rule applied (from the charter):** cite everything. Where a number is a range or
> unverified, it is labelled. No competitor, statistic, or user quote is invented.

---

## 1. Interface shape — map-first, chat-as-sidecar

### 1.1 The decision

> The primary surface is a **map with a ranked card rail**. The conversational layer is an
> **input and refinement tool** that sits beside it, never instead of it. The LLM's job is to
> **parse the user's situation into filter state** — not to recommend, and never to invent an
> activity.

### 1.2 Why not a chat-first product

The case against is already in our own research:

| Signal | Value | Source |
|---|---|---|
| AI-chat sessions abandoned | **26%** | iPullRank (Pew), via `demand-validation.md` |
| Clicks *inside* AI summaries | **1%** | iPullRank (Pew), via `demand-validation.md` |
| Choice **deprivation** vs overload | **51%** vs **14%** | Reutskaja 2022, 7,400 participants, 6 countries |
| LLM-planner cohort durability | **Tripnotes** acquired → shut down; site now 404s | `competitors.md` Rank 15 |
| User resistance to being told what to do | *"who asked for your opinion?"* | r/SideProject thread, via `demand-validation.md` |

A chat window is the **worst primary surface** and the **best input surface**. Both are true.

### 1.3 Why chat is the best *input* surface

The strongest evidence is a real user's sentence, captured verbatim in `demand-validation.md`:

> *"What to do inside on a hot day that's not at home, isn't eating or drinking, and isn't
> super expensive for 2 people… Also no arcade, bowling, or movies."*

**No competitor in the 15-company map can accept that.** Yelp, Eventbrite, Facebook Events and
Meetup all require the user to already know what they want. Natural language with **exclusions**
and **constraints** is the open door — and it maps directly onto the engine ADR's constraint
model.

### 1.4 The three layers

```
┌──────────────────────────────────────────────────────────────┐
│ 1. INPUT        chips · sliders · free text · voice          │
│                   ↓ all three write the SAME state object    │
│ 2. REASONING    LLM parses intent → structured filter state  │
│                   (weather, budget, people, time, distance,  │
│                    energy, EXCLUSIONS)                       │
│                   ↓ proposes state, engine executes          │
│ 3. OUTPUT       MAP (pins) + ranked card rail + rationale    │
└──────────────────────────────────────────────────────────────┘
```

- The LLM **never invents an activity.** It selects from the catalog the engine already holds.
- This is a bounded, deterministic-output task — cheap, testable, and swappable.
- **Chips are the 95% path; chat is the deluxe path.** Chat must be optional.

### 1.5 Reference layout

```
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

### 1.6 Design rules (each traceable to research)

1. **The map renders even when the chat is empty.** Default = current weather + location +
   6+ options. A blank chat is the same failure as Mommy Poppins' 2016 *"can't connect to
   server"* reviews — users bail.
2. **The map is the persistence layer; chat is the input layer.** Chat scrolls away; a map
   with pins persists. This is the direct counter to the 26% AI-session abandonment.
3. **Never let chat be the only output.** Every conversational turn must also update the map
   and the rail.
4. **Show the rationale.** *"Why it fits"* is the differentiator — situation-fit output beats
   novelty (`demand-validation.md` §4).
5. **≥6 options, ~3 per time block.** Deprivation, not overload, is the dominant risk.
6. **The map is also the SEO moat.** A chat transcript is not indexable; a constraint URL is
   (`thingztodo.app/?lat=…&weather=no_rain&budget=50`). Forge already flagged this as the MVP's
   killer differentiator (ADR open item 4).
7. **Earn recommendations; don't push them.** The anti-recommendation sentiment is real.

### 1.7 Voice

Voice is an **input modality for the map, not a channel.** Use case: in the car, hands full —
*"what can we do tonight, raining, three of us, cheap."* The output is a **spoken summary of the
top option plus a link pushed to the phone**, not a chat transcript read aloud.

### 1.8 The moat

**Ground truth is the moat, not the AI.** Live weather, open/closed, real-time price, and a
verified catalog. The LLM is optional and replaceable; without ground truth the product is a thin
wrapper over someone else's inventory, and no revenue stream in §3 survives that.

---

## 2. User accounts — earned escalation, not an entry gate

### 2.1 Conflict with an accepted ADR

`ADR-0001 §4` states: *"Auth / identity — None for MVP. Nothing in the product requires accounts
today. Kill the target, not the scope."*

Eric's direction reverses this. **Forge owns architecture** (charter §4) and the charter requires
a reversal to be **loud, in writing, with the reason.** That is carded below — it is not being
silently contradicted.

### 2.2 The product argument for not gating entry

- **Every fast-eval incumbent removes signup.** GuruWalk Kiara (the only *durable* LLM-planner
  benchmark in our map) is free, no account, no sign-up. Flinder: *"No account, no ads, no
  sign-up."*
- Accounts are a **tax at the moment of maximum motivation.** Someone searching *"what to do
  tonight"* will not create an account. That is a conversion cliff.
- The core value — *given this state, here is the thing* — works perfectly anonymously.

### 2.3 What accounts buy

Persistence (saved places, history) · personalization (learned taste) · re-engagement (push /
email) · **and the merchant side needs login for a dashboard.** So accounts are eventually
required; the only question is *when*.

### 2.4 Recommendation

| Decision | Rationale |
|---|---|
| **Anonymous by default.** Map, chat, filters, follow-through — all work with zero auth. | Removes the cliff at the moment of maximum motivation |
| **Trigger = "Save this plan."** Save → sign in. | Conversion is highest exactly at the value moment |
| **Passwordless** — magic link / OTP, then Apple / Google OAuth. | No password to manage; lowest-friction modern default |
| **Guest plan URL persisting ~30 days, no account.** | *"Send this to the group chat"* is the most natural viral loop, and it should work with neither party signing up |
| **Plan two account types from day one:** consumer (passwordless, free) + **merchant/organizer** (dashboard, later). | Retrofitting a second identity model is painful; the merchant side will need one |

### 2.5 Candidate provider — Clerk

Eric's direction: **evaluate Clerk.** Eric has used it before and reports a usable free tier.

Verified 2026-10-22:

| Fact | Value | Source |
|---|---|---|
| Free tier name | **Hobby** | clerk.com Next.js auth guide |
| Free tier allowance | **50,000 Monthly Retained Users (MRU) per app** | clerk.com; expanded 2026-02-05 |
| MRU definition | A user who **returns** after signing up. A signup that never comes back **does not count**. | clerk.com |
| Free tier apps | Unlimited applications | clerk.com |
| Free tier orgs | 100 monthly retained organizations, up to 20 members each | clerk.com |
| **SSO on free tier** | **No** — enterprise SSO is metered separately | clerk.com |
| Pro tier | $25/mo, or $20/mo billed annually | clerk.com |
| Pro overage | **$0.02 per MRU/mo** beyond 50,000, tiering down at volume | clerk.com |
| Next.js setup | CLI; **5–15 minutes** for a working sign-in + server-side session check | clerk.com |
| B2B support | Organizations, invitations, switching, Admin/Member roles included | clerk.com |
| AI-apps note | `@clerk/agent-toolkit`; *"first day free"* — users aren't counted until they return after 24h | clerk.com |

**Why the MRU definition matters commercially:** an app with low early retention is *favourably*
metered. A user who signs up once and never returns costs nothing.

**Questions Forge must answer** (not resolved here):

1. **Hosted dependency.** Clerk is a third-party SaaS with external network calls. For a
   Canadian product this raises **PIPEDA** consent questions and adds a failure domain outside
   our container. Do we accept that?
2. **Cost cliff.** Free ends at 50,000 MRU. Beyond that, $0.02/MRU/mo (~$1,025/mo at 100k).
   Is that acceptable as a *success* cost, or does it cap the business?
3. **No SSO on free.** Does the merchant/B2B side need SSO? If yes, that is a paid tier from day one.
4. **Self-hosted alternative.** Our stack is Next.js + `better-sqlite3`. Auth.js (formerly
   NextAuth) / Lucia with a magic-link flow would keep identity in our own database and our own
   container — no per-user metering, no vendor dependency, but we own the security surface.
   **This should be weighed honestly, not dismissed because Clerk is the comfortable choice.**
5. **Reversibility.** Can we migrate away from Clerk later without losing user accounts?

---

## 3. Monetization

### 3.1 The strategic insight

`competitors.md` §6, point 2:

> *"The price signal is in the wrong column. In every incumbent, pricing lives on the
> organizer/merchant side, not the consumer side."*

All 15 competitors monetize **supply**: Eventbrite (3.7% + $1.97/ticket), Meetup
($29.99/mo organizer), Yelp ($150–643/mo), Groupon (commission on redeemed voucher). Almost nobody
successfully charges the *consumer* for "things to do."

**The insight that makes the concept commercially coherent:**

> **Weather is a perishable-inventory liquidation trigger.** A rainy Tuesday means a restaurant
> with empty tables, a bowling alley at 12% capacity, a museum with dead hours. ThingzToDo is not
> a discovery tool — it is a **real-time demand-routing layer for dead local capacity**.
> *"We fill your slow hours"* is a B2B story nobody in our map is telling, and it is uniquely
> enabled by the weather filter.

### 3.2 Revenue stack

| # | Stream | Mechanism | Time to cash | Defensibility |
|---|---|---|---|---|
| **1** | **Transaction take-rate** | Affiliate (Viator, GetYourGuide, Eventbrite ticketing) → then direct checkout for un-ticketed venues. ~5–15% | Medium | **High** — aligns with map-pin-as-checkout |
| **2** | **Self-serve merchant listings** | Free claim → paid profile → promoted placement on the map + in chat answers (labelled *Sponsored*) | **Fastest** | Medium — proven column; needs a listing product |
| **3** | **Lead-gen fees** | "Request a quote / callback" → merchant pays per qualified lead | Fast | Medium |
| **4** | **Consumer premium** | $3.99–6.99/mo or $29.99/yr: travel mode, auto "rain plan", shared group planning, saved lists, alerts | Slow | Low — thinnest conversion in this category |
| **5** | **Deal / voucher economics** | Time-boxed offers surfaced by situation; merchant pays on redemption | Slow | Low — competes with #2; risks Groupon's friction |
| **6** | **Anonymized demand data** | "What Ottawa searched on a rainy Saturday" → sold to DMOs, tourism boards, venues | 2027+ | **High, quiet** — our municipal sites have no insight layer |
| **7** | **Category sponsorship** | *"The under-$20 filter, presented by [bank]"* — sponsor the **filter**, not the page | Medium | Medium, high-margin |

**Rule for #4:** premium must **never** gate the core value. Gate the core and the next free
entrant eats us. Charge for *breadth* (other cities), *foresight* (auto rain plans, alerts), and
*group coordination* — not for the answer itself.

### 3.3 Recommended sequencing

1. **Ship free + anonymous.** No accounts at entry, no paywall. Prove the value and get usage —
   which also *measures* which stream has real pull before we build billing.
2. **First revenue: affiliate + booking take-rate.** Near-zero sales motion, and it directly
   attacks the GuruWalk Kiara weakness Scout flagged (*no in-browser booking*). **The map pin is
   the checkout.**
3. **Second: self-serve merchant claims + promoted placement.** Fastest path to a dollar; the
   proven column.
4. **Third: consumer premium** — once there is retention to convert.
5. **Later: data licensing + sponsorships** — quiet, defensible, high-margin.

### 3.4 Honest caveats

- Scout states plainly: **no verified market-size number exists for the state-conditioned need.**
  Demand is real at search level; *willingness to pay* is unproven.
- The take-rate percentages above are **industry ranges, not negotiated terms** for ThingzToDo.
- The commercial risk mirrors the product risk: without owned ground truth, we are a thin
  wrapper over someone else's catalog — and no stream above survives that.

---

## 4. Cards filed from this memo

| Card | Owner | Deliverable |
|---|---|---|
| Evaluate Clerk for accounts; amend `ADR-0001 §4` | Forge | Recommendation + amended ADR |
| Write ADR: map-first / chat-as-sidecar interface | Forge | New ADR |
| Validate the "we fill your slow hours" B2B thesis + revenue prioritization | Scout | Research memo |
| Security review scope: passwordless auth + payment handling | Sentinel | Review checklist |

---

## 5. Open items for Eric

1. **The product desk has no owner.** `docs/DISPATCH.md` "Who gets what" lists research,
   architecture, QA, and ops — no product/UX owner. This memo landed in an empty `desks/product/`.
   Either that desk needs an owner, or product decisions should route somewhere defined.
2. **Charter open questions #1, #4, #5, #6** remain open. §1 and §3 above inform them; the charter
   has not been updated. Eric owns the charter.
3. **Sentinel's production gate** applies to anything in §3 that handles money. Nothing ships
   without Sentinel's sign-off **and** Eric's approval — two keys.

---

*Prepared by Irock, orchestrator, 2026-10-22. Research inputs trace to Scout's labelled desk
files. Architecture inputs trace to Forge's accepted ADRs. No figure in this memo is presented as
a verified market number.*
