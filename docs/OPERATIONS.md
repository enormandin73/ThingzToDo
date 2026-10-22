# OPERATIONS.md — Operating the ThingzToDo Agent Team

> Note: this was originally drafted as `AGENTS.md`, which Hermes treats as a protected
> agent-instruction path and refused to write without explicit approval. It lives here
> instead. If you want it as `AGENTS.md`, say so and approve the write.

How to talk to, and operate, the ThingzToDo agent team. Meant to be read by every agent
in the company and by Eric.

## The team

| Agent | Profile | Role | Desk |
|---|---|---|---|
| **Scout** | `scout` | Chief Research & Marketing Officer | `desks/research/` |
| **Forge** | `architect` | Principal Software Architect | `desks/engineering/` |
| **Sentinel** | `sentinel` | Head of Quality & Release | `desks/quality/` |
| **Concierge** | `concierge` | Chief Operating Officer | `desks/ops/` |
| **Irock** | *(orchestrator, this session)* | Creates and oversees agents | — |

## Talking to an agent

```bash
scout chat                 # open Scout's interactive chat
scout chat -q "question"   # one-shot question
hermes -p architect chat   # same, via the -p flag
hermes -p sentinel chat
hermes -p concierge chat
```

Each profile has its own `SOUL.md` (persona), memory, skills, sessions, and credentials.
Never point two agents at the same profile — they corrupt each other's memory.

## Working directories

- Company home: `/Users/martennormandin/thingztodo/`
- Desks: `thingztodo/desks/{research,engineering,quality,ops,product}/`
- Docs: `thingztodo/docs/`
- Product repo: `thingztodo/app/` *(created when Forge starts building)*

## Work items — the kanban board

```bash
hermes kanban list
hermes kanban create "Title" --assignee scout --body "Acceptance criteria..."
hermes kanban show <id>
hermes kanban comment <id> "note"
hermes kanban complete <id>
```

Assignees are the profile names: `scout`, `architect`, `sentinel`, `concierge`.
The board auto-routes work to the right profile when the gateway is running.

## Cron jobs

```bash
hermes cron list
hermes cron create "0 9 * * *" --profile scout --prompt "..."
```

Jobs appear as `[bot:<name>] …` in the list.

## Health

```bash
hermes gateway status
hermes profile list
hermes -p scout sessions list
```

Concierge owns ongoing health monitoring. Its runbook is at
`thingztodo/desks/ops/RUNBOOK.md`.

## Golden rules

1. **One agent per profile.** Two writers on one home destroy each other's memory.
2. **Production needs two keys:** Sentinel's sign-off + Eric's approval.
3. **Durable work goes to a desk directory**, not just into a chat transcript.
4. **Never invent a competitor, a statistic, or a user quote.**
5. **If you can't verify it, say so.**
