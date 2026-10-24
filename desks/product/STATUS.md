# STATUS.md — Product Desk (Curator)

**Company:** ThingzToDo · **Desk:** product · **Owner:** Curator
**Date:** 2026-10-22

## Overview

Pre-product. `desks/product/` is Curator's desk: product direction, UX/UI,
information architecture, and the product decision record. This file tracks the
current inventory of the desk's work and what is still open.

## Desk inventory

| Artifact | State | Owner |
|---|---|---|
| `2026-10-22-product-desk-ownership.md` | ✅ Created today | Curator |
| `2026-10-22-interface-accounts-and-monetization.md` | ✅ Created 2026-10-22 | Curator |
| `STATUS.md` | ✅ Created today | Curator |

## Reference map (authoritative — not duplicated here)

| Doc | What it says | Pointer |
|---|---|---|
| `docs/CHARTER.md` | Team roster (§3), authority and gates (§4), open questions (§6), standing principles | §§31-56, 70-79 |
| `docs/DISPATCH.md` | Work flow, ownership table, escalation paths | §§1-66 |
| `docs/OPERATIONS.md` | How to talk to agents, working directories, golden rules | §§1-80 |
| `README.md` | Team roster and stack snapshot | lines 27-56 |

## Scope of the product desk (as owned by Curator)

- **Product direction** — what ThingzToDo is and is not.
- **UX/UI** — the journey from intent to action, screens, interaction states.
- **Information architecture** — the card rail, filters, grouping, and what is
  surfaced versus hidden.
- **Product decision record** — every significant decision with rejected
  alternatives and the reason.

## Open product questions (CHARTER §6) — status 2026-10-23

| Q# | Question | Status | Close by |
|---|---|---|---|
| OQ1 | What is the actual product? Web-first or app-first? | ✅ Closed | 2026-10-23 — Decision 1 (web-first) |
| OQ2 | Where does the activity data come from? | 🔍 Open — Scout sourcing plan pending | — |
| OQ3 | What is the first geography? | ✅ Closed | 2026-10-23 — Decision 3 (Ottawa-Gatineau) |
| OQ4 | What is the revenue model? | ✅ Closed | 2026-10-23 — Decision 2 (no consumer paywall v1; affiliate take-rate; self-serve listings; premium for value-adds only) |
| OQ5 | What are the first three features worth building? | 🔎 Open — mine to propose | — |
| OQ6 | Who is the first user, precisely? | ✅ Closed | 2026-10-23 — Decision 3 (Ottawa-Gatineau local, "tonight", weather + budget) |

**Closed by these three decisions:** OQ1, OQ3, OQ4, OQ6. These decisions do not touch OQ2 (activity data source), which remains open pending Scout. OQ5 (first three features) is mine to propose.

## Current status by area

| Area | State |
|---|---|
| Product direction | ✅ Decided (2026-10-23: web-first, no consumer paywall, Ottawa-Gatineau first) |
| UX/UI | 🚧 Under spec (desk memo: accounts & monetization + v1 flow) |
| Information architecture | 🚧 Under spec (card rail, filters, chat sidecar) |
| Product decision record | ✅ 3 records (accepted v1 foundation decisions) |
| Architecture | ✅ Decided (Forge, ADR-0001) |
| Research | ✅ Competitor map + demand validation |
| Test strategy | ✅ Written (Sentinel) |
| Application (`app/`) | 🚧 Scaffolded |
| Ops & monitoring | ✅ Live |

## What's next

- Propose the top three v1 features (OQ5) as a separate dated record, raised to
  `#product` with Eric's @mention.
- Forge + Scout: implement the Ottawa-Gatineau data slice and the no-paywall
  data architecture aligned to Decisions 2 and 3.

## Owners and gates

- **Curator** owns this desk and its files (this file, the ownership record, and
  the README inventory table above).
- **Forge** decides architecture; **Sentinel** is the production gate (CHARTER
  §4). Nothing in this desk is production- or release-assigned.
