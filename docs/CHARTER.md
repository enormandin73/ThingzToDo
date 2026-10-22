# ThingzToDo — Company Charter

**Version:** 0.1 · **Owner:** Eric Normandin · **Status:** pre-product, team forming
**Home:** `/Users/martennormandin/thingztodo/`

---

## 1. The idea

ThingzToDo is a webapp / website that helps end users find something **"thingz" to do**
in their geographic area, matched to the situation they are actually in:

- **Weather** — indoor vs. outdoor, rain-safe, heat-safe, snow-day
- **Cost** — free, cheap, splurge
- **Number of people** — solo, pair, family, group
- **Time of day** — morning, lunch hour, evening, late night
- **Distance / travel willingness**, and more constraints to be decided

The idea came from Eric Normandin and his wife Jennifer roughly 20 years ago and was
never launched. That is a genuine asset: the concept has survived two decades of real
life and still feels worth building. It is not, however, a settled spec — nothing about
the product is decided yet.

## 2. Where we are

**Pre-product.** No repository, no running system, no users. The team exists and the
work starts now. Everything below is direction, not done.

## 3. The team

| Agent | Role | Desk |
|---|---|---|
| **Scout** | Chief Research & Marketing Officer | `desks/research/` |
| **Forge** | Principal Software Architect | `desks/engineering/` |
| **Sentinel** | Head of Quality & Release | `desks/quality/` |
| **Concierge** | Chief Operating Officer | `desks/ops/` |
| **Irock** | Orchestrator (oversees the above) | — |

Agent profile directories live at `~/.hermes/profiles/<name>/`.

## 4. Authority and gates

These are real, not decorative:

- **Forge** decides architecture and owns implementation. No one else commits to the
  product repo.
- **Sentinel** holds the **production gate**. Nothing ships to production without
  Sentinel's sign-off **and** Eric's explicit approval. Two keys.
- **Scout** owns market truth and messaging. Scout does not set the build order alone.
- **Concierge** keeps every agent alive and alerts Eric when one is not. Concierge does
  not do the other agents' work.
- **Eric** sets direction, resolves disputes, and approves spend.

## 5. How the agents work together

- **Desks** — each agent writes durable output to its own desk directory. This is the
  real collaboration surface: files, not chat history.
- **Kanban board** — work items live on the shared board (`hermes kanban`). Anything
  that takes more than a few minutes is a card, assigned to the right agent, with
  acceptance criteria.
- **#decisions** — when an agent changes a decision another agent made, it says so
  loudly, in writing, with the reason.
- **#exec** — escalations to Eric.
- **Discord / WhatsApp** — Eric talks to the team; the team talks to each other.

## 6. Current open questions

Deliberately unanswered — this is the work:

1. What is the actual product? Web-first or app-first? Both?
2. Where does the activity data come from? Curated, scraped, licensed, user-generated?
3. What is the first geography — Ottawa-Gatineau, or somewhere else?
4. What is the revenue model, if any?
5. What are the first three features worth building?
6. Who is the first user, precisely?

## 7. Standing principles

- **Build the smallest thing that is real.** A narrow thing that works beats a broad
  thing that never ships.
- **Cite everything.** Unverified claims get labelled as such.
- **Prove it runs.** "Done" means demonstrated, not intended.
- **Say no with a reason.** Quietly building the wrong thing is the failure mode.
- **Cost is a constraint.** No budget yet. Design cheap, ask before spending.
- **Record decisions.** A decision nobody can find gets re-litigated.

---

## Appendices

- `docs/CHARTER.md` — this document
- `docs/AGENTS.md` — how to operate this team from the CLI
- `docs/DISPATCH.md` — how work gets assigned and tracked
