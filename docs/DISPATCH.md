# DISPATCH.md — How Work Moves Through ThingzToDo

## The principle

Every piece of work that takes more than a few minutes is a **kanban card**, not a
chat message. Chat is for talking; the board is for work. A card has an owner, an
acceptance criterion, and a state anyone can see.

## The flow

```
Triage → Todo → Ready → In progress → (Blocked) → Done
```

1. **Triage** — a raw idea or request. Eric drops these in.
2. **Todo** — clarified, not yet started.
3. **Ready** — assigned, waiting for the owner to pick it up.
4. **In progress** — the owner is actively working.
5. **Blocked** — waiting on a person or another card.
6. **Done** — delivered, with the evidence written on the card.

## Who gets what

| Kind of work | Owner |
|---|---|
| Market research, competitor analysis, positioning, naming, growth | **Scout** |
| Architecture, design, implementation, developer tooling | **Forge** |
| Test strategy, QA automation, release readiness, production gate | **Sentinel** |
| Agent health, restarts, alerting, operational reporting | **Concierge** |
| Product direction, UX/UI, information architecture, the product decision record | **Curator** |
| Direction, disputes, spend approval | **Eric** |

## Card anatomy

A good card has:

- **Title** — one line, imperative ("Map the event-discovery competitor landscape")
- **Body** — the ask, in enough detail that the owner doesn't have to guess
- **Acceptance criteria** — what "done" looks like, checkably
- **Assignee** — exactly one
- **Desk output** — where the deliverable lands

## Escalation paths

- Blocked on another agent's output → set the card **Blocked**, comment with exactly
  what's needed, `@mention` the owner.
- Product/architecture dispute → both agents state their position on the card; Eric
  decides. Don't let it sit.
- Agent unhealthy or unresponsive → **Concierge**, and if it's P1, Eric is alerted
  directly.
- Believing the company is building the wrong thing → say so on **#exec**, in writing,
  with the evidence. Do not soften it.

## Cadence

- **Daily** — Concierge posts the operational status.
- **Weekly** — Eric reviews the board, kills what isn't worth doing, sets the next
  week's priorities.
- **Ad hoc** — any agent can raise a card at any time.

## Anti-patterns

- Vague cards with no acceptance criteria ("look into competitors")
- Cards assigned to nobody
- Work discussed in chat but never carded, then forgotten
- An agent quietly doing another agent's job instead of routing the card
