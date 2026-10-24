# Product Decision Record — v1 Foundation Decisions (Accepted)

**Date:** 2026-10-23
**Status:** ACCEPTED — Eric Normandin approved all three recommendations verbatim: "yes for all 3 recommendations"
**Owner:** Curator (Head of Product & Design)
**Desk:** `desks/product/`
**Raised in:** `#product` on 2026-10-23; every request prefixed with Eric's @mention (`<@309043067170848772>`) so it was delivered to him directly.

---

## Summary

Three decision requests were raised and accepted on 2026-10-23. These decisions define the v1 spec's foundation: product shape, revenue model, and first geography + first user. Each entry states what was decided, that the call was Eric's, the alternatives rejected, and the consequences for the v1 spec.

---

## Decision 1 — Product shape: web-first, map-first

**What was decided:** ThingzToDo ships as a web-first product — one web surface, no native app. The screen is map-first: the activity list is attached to map pins, and a chat sidecar is the refinement surface ("what fits what I'm actually in"). Cost is a filter against the answer, never a gate at the answer.

**Decided by:** Eric — his call, accepted verbatim.

**Alternatives rejected:**
- Native mobile app first: doubles build cost for marginal v1 retention; a web surface iterates faster and is easier to test.
- Search-first, map-second layout: the map is what the user is oriented in; pins carry interest and price together; the sidecar keeps the answer on one screen.

**Consequences for the v1 spec:**
- Single responsive web surface; no native app in v1.
- UX flow: intent (weather / cost / people / time) → map pins → activity card → detail → saved plan; chat sidecar for constraint refinement.
- Delivery is one deploy with shared data; mobile is a responsive viewport, not an installable build.

---

## Decision 2 — Revenue model: no consumer paywall in v1

**What was decided:** The answer is free and stays free. v1 monetization: an affiliate take-rate at the map pin (small % on bookings/off-site guests for activities with a referral path), self-serve merchant listings (paid to be listed/verified first, optional upgrades later), and premium only for value-adds — never gating the answer.

**Decided by:** Eric — his call, accepted verbatim.

**Alternatives rejected:**
- Consumer paywall in v1: blocks the product's core promise, breeds resentment, and research (Scout) shows users resist being told what to do; not worth the trade-off now.
- Flat subscription: invents a value the product doesn't have yet; merchant support is more direct revenue.
- Gate premium behind feature parity: that is a paywall by another name and contradicts the accepted model.

**Consequences for the v1 spec:**
- No paywall, no subscription, no gated results in v1.
- Monetization is ambient (affiliate at pins, self-serve listings) and never a barrier at the answer.
- Premium is a separate value-add layer that can never hide activity options.
- Merchant listing is self-serve; v1 ships listings + affiliate only.

---

## Decision 3 — First geography and first user: Ottawa-Gatineau

**What was decided:** First geography = Ottawa-Gatineau; first user = a local resident hunting for something to do "tonight" (evening/late-night), 1–2 people, constrained by weather and budget. Every v1 filter reflects those constraints.

**Decided by:** Eric — his call, accepted verbatim.

**Alternatives rejected:**
- Multiple geographies in v1: data sourcing, listing onboarding, and UX polish multiply; the product is not a general finder yet.
- Any-time-of-day first user: the acute, high-frequency moment ("tonight") is where the product earns its keep and best exercises the weather + budget model.

**Consequences for the v1 spec:**
- v1 data must have Ottawa-Gatineau coverage; first activity/merchant data is Ottawa-Gatineau-only.
- UX drafted for "tonight", 1–2 people, weather + budget constrained.
- Outbound and listing-onboarding efforts target that coverage first; expansion happens only after the Ottawa-Gatineau slice has shipped and learned.

---

## Open charter questions (CHARTER §6) — status as of 2026-10-23

| Q# | Question | Status | Close by |
|---|---|---|---|
| OQ1 | What is the actual product? Web-first or app-first? | ✅ Closed | 2026-10-23 — Decision 1 (web-first) |
| OQ2 | Where does the activity data come from? | 🔍 Open — Scout sourcing plan pending | — |
| OQ3 | What is the first geography? | ✅ Closed | 2026-10-23 — Decision 3 (Ottawa-Gatineau) |
| OQ4 | What is the revenue model? | ✅ Closed | 2026-10-23 — Decision 2 (no consumer paywall v1; affiliate take-rate; self-serve listings; premium for value-adds only) |
| OQ5 | What are the first three features worth building? | 🔎 Open — mine to propose | — |
| OQ6 | Who is the first user, precisely? | ✅ Closed | 2026-10-23 — Decision 3 (Ottawa-Gatineau local, "tonight", weather + budget) |

**Closed:** OQ1, OQ3, OQ4, OQ6. These three decisions do not touch OQ2 (activity data source), which remains open pending Scout. OQ5 (first three features) is mine to propose.

---

## Next

- Propose the top three v1 features (OQ5) as a separate dated record, raised to `#product` with Eric's @mention.
- Forge + Scout: implement the Ottawa-Gatineau data slice and the no-paywall data architecture aligned to Decisions 2 and 3.
