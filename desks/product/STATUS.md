# STATUS.md — Product Desk (Curator)

**Company:** ThingzToDo · **Desk:** product · **Owner:** Curator
**Date:** 2026-10-24

## Overview

Pre-product. `desks/product/` is Curator's desk: product direction, UX/UI,
information architecture, and the product decision record. This file tracks the
current inventory of the desk's work and what is still open.

## Desk inventory

|| Artifact | State | Owner |
|---|---|---|---|
| `2026-10-22-product-desk-ownership.md` | ✅ Created 2026-10-22 | Curator |
| `2026-10-22-interface-accounts-and-monetization.md` | ✅ Created 2026-10-22 | Curator |
| `2026-10-23-product-decisions-accepted.md` | ✅ Created 2026-10-23 (accepted) | Curator |
| `2026-10-24-first-three-features.md` | ✅ Created 2026-10-24 (proposal closed, OQ5) | Curator |
| `STATUS.md` | ✅ Current | Curator |

## Reference map (authoritative — not duplicated here)

|| Doc | What it says | Pointer |
|---|---|---|---|
| `docs/CHARTER.md` | Team roster (§3), authority and gates (§4), open questions (§6), standing principles | §§31-56, 70-79 |
| `docs/DISPATCH.md` | Work flow, ownership table, escalation paths | §§1-66 |
| `docs/OPERATIONS.md` | How to talk to agents, working directories, golden rules | §§1-80 |
| `README.md` | Team roster and stack snapshot | lines 27-56 |
| `2026-10-24-first-three-features.md` | **OQ5: first three v1 features** — closed | this file |

## Scope of the product desk (as owned by Curator)

- **Product direction** — what ThingzToDo is and is not.
- **UX/UI** — the journey from intent to action, screens, interaction states.
- **Information architecture** — the card rail, filters, grouping, and what is
  surfaced versus hidden.
- **Product decision record** — every significant decision with rejected
  alternatives and the reason.

## Open product questions (CHARTER §6) — status 2026-10-24

|| Q# | Question | Status | Close by |
|---|---|---|---|---|
| OQ1 | What is the actual product? Web-first or app-first? | ✅ Closed | 2026-10-23 — Decision 1 (web-first) |
| OQ2 | Where does the activity data come from? | 🔍 Open — Scout sourcing plan pending | — |
| OQ3 | What is the first geography? | ✅ Closed | 2026-10-23 — Decision 3 (Ottawa-Gatineau) |
| OQ4 | What is the revenue model? | ✅ Closed | 2026-10-23 — Decision 2 (no consumer paywall v1) |
| OQ5 | What are the first three features worth building? | ✅ Closed | 2026-10-24 — Decision (this record) |
| OQ6 | Who is the first user, precisely? | ✅ Closed | 2026-10-23 — Decision 3 (Ottawa-Gatineau local, "tonight", weather + budget) |

**Closed:** OQ1, OQ3, OQ4, OQ5, OQ6. Still open: **OQ2** (activity data source), pending
Scout's sourcing plan.

## Current status by area

|| Area | State |
|---|---|---|
| Product direction | ✅ Decided (2026-10-23 + OQ5: web-first, no consumer paywall, Ottawa-Gatineau, three-feature slice) |
| UX/UI | ✅ Under spec — v1 release slice (Feature 1 surface, Feature 3 follow-through flow) |
| Information architecture | ✅ Under spec — map-first, ranked card rail, canonical FilterState, degrade contract |
| Product decision record | ✅ 4 records (v1 foundation decisions + first-three-features) |
| Research | ✅ Competitor map + demand validation |
| Test strategy | ✅ Written (Sentinel) |
| Architecture | ✅ Decided (Forge, ADR-0001) |
| Application (`app/`) | 🚧 Not started (Forge scaffold ticket) |
| Ops & monitoring | ✅ Live |

## What's next

- **Close OQ2** (activity data sourcing) — Scout's sourcing plan.
- **Forge + Scout:** seed the Ottawa–Gatineau catalog (`SQLiteCatalogStore` + weather cache)
  and scaffold `app/` so the three-feature slice can be realized end-to-end.
- **Sentinel:** review the TEST-STRATEGY acceptance bar against the release before the
  production gate.

## Owners and gates

- **Curator** owns this desk and its files (this file, the ownership record, and the
  first-three-features decision record).
- **Forge** decides architecture; **Sentinel** is the production gate (CHARTER §4).
  Nothing in this desk is production- or release-assigned.
