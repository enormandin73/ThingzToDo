# ThingzToDo

A webapp that helps people find something **"thingz" to do** in their area,
matched to the situation they're actually in — **weather**, **cost**, **number
of people**, **time of day**, and distance.

The idea came from Eric Normandin and his wife Jennifer about twenty years ago.
This repository is where it finally gets built.

---

## Status

**Pre-product.** The architecture is decided; the application is being
scaffolded now.

| Area | State |
|---|---|
| Architecture | ✅ Decided — see `desks/engineering/decisions/ADR-0001-v1-architecture.md` |
| Research | ✅ Competitor map + demand validation — see `desks/research/` |
| Test strategy | ✅ Written — see `desks/quality/TEST-STRATEGY.md` |
| Application (`app/`) | 🚧 Being scaffolded |
| Ops & monitoring | ✅ Live — health sweep + email alerts |

---

## The team

ThingzToDo is built and operated by a fleet of persistent Hermes agents. Each is
a separate Hermes profile with its own persona, memory, and desk.

| Agent | Role | Desk |
|---|---|---|
| **Scout** | Chief Research & Marketing Officer | `desks/research/` |
| **Forge** | Principal Software Architect | `desks/engineering/` |
| **Sentinel** | Head of Quality & Release (production gate) | `desks/quality/` |
| **Concierge** | Chief Operating Officer | `desks/ops/` |

They talk to Eric over Discord and collaborate through the desks and a kanban
board. See `docs/CHARTER.md` for authority and gates, and `docs/DISPATCH.md` for
how work moves.

---

## Stack

Decided in ADR-0001:

| Layer | Choice |
|---|---|
| Frontend | Next.js (App Router) + React |
| Backend runtime | Node.js 22 LTS |
| Data store | SQLite (`better-sqlite3`) |
| Test runner | Vitest |
| Deploy | Docker → Fly.io |
| Weather | Open-Meteo (free, no key) |

---

## Repository layout

```
thingztodo/
├── app/            # the application (scaffolded next)
├── desks/          # agent output — research, engineering, quality, ops
├── docs/           # charter, dispatch process, operations
└── .vscode/        # shared editor config
```

---

## Working here

The agents edit files directly on disk, so opening this folder in your editor
shows their work appearing in real time.

```bash
code ~/thingztodo
```

See `docs/OPERATIONS.md` for how to talk to an agent from the terminal.

---

## License

Proprietary — all rights reserved. Not for distribution.
