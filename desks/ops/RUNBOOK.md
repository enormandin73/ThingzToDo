# ThingzToDo Agent Runbook

**Owner:** Concierge (COO) · **Maintained by:** Concierge · **Last updated:** 2026-10-21

This is the operational manual for keeping the ThingzToDo agent team alive. If you are
reading this because something broke, start at §2.

---

## 1. The fleet

| Agent | Role | Profile dir | Desk |
|---|---|---|---|
| **Scout** | Chief Research & Marketing Officer | `~/.hermes/profiles/scout/` | `thingztodo/desks/research/` |
| **Forge** | Principal Software Architect | `~/.hermes/profiles/architect/` | `thingztodo/desks/engineering/` |
| **Sentinel** | Head of Quality & Release | `~/.hermes/profiles/sentinel/` | `thingztodo/desks/quality/` |
| **Concierge** | Chief Operating Officer | `~/.hermes/profiles/concierge/` | `thingztodo/desks/ops/` |
| **Curator** | Head of Product & Design | `~/.hermes/profiles/curator/` | `thingztodo/desks/product/` |

Company home: `/Users/martennormandin/thingztodo/`

Each agent is a **Hermes profile** — its own `config.yaml`, `.env`, `SOUL.md`, memory,
skills, sessions, cron, and state DB. Never point two agents at one profile.

**Discord channels** (guild `1562613873335345334`, category "ThingzToDo Team"): `#research`
→ scout, `#engineering` → architect, `#quality` → sentinel, `#ops` → concierge,
`#product` → curator, `#exec` and `#decisions` → default (Irock). Routed via
`gateway.profile_routes` on the default profile; each routed profile also needs
`DISCORD_ALLOWED_USERS` set to Eric's **numeric** id in its own `.env`.

---

## 2. Health check (the 60-second version)

```bash
hermes profile list          # all four present?
hermes gateway status        # is the gateway up?
hermes cron list             # are the jobs still scheduled?
for p in scout architect sentinel concierge; do
  echo "== $p =="; ls -la ~/.hermes/profiles/$p/logs/ 2>/dev/null | tail -3
done
tail -50 ~/.hermes/logs/gateway.log
```

**What "healthy" actually means:** the agent is producing work — files appearing in its
desk, kanban cards moving, cron jobs firing. A connected gateway is *not* health.

---

## 2b. Kanban dispatch — the concurrency trap

**`hermes kanban create` dispatches immediately.** There is no review queue and no
"todo holding pen": a card assigned to a profile goes to `ready` and the running worker
spawns a session for that profile within about a minute.

**The trap:** filing **two cards to the same profile in one batch starts two concurrent
sessions in that one profile.** That is exactly what §1's invariant forbids — two writers
on one home corrupt each other's memory. It fails *silently*: the board shows both cards
as `running`, and `hermes -p <profile> sessions list` shows two entries stamped "just now".
Nothing errors.

**Fix — serialize with a parent link:**

```bash
hermes kanban link <parent-id> <child-id>
```

That alone is enough. The claim step re-checks parents, so the child drops from `ready` to
`todo` and auto-promotes only when the parent completes — no human unblock needed. Do not
also run `block --kind dependency`; it fails with "cannot block" because the dependency is
already implied by the link. That error is expected.

**If the child has already started**, stop it first:

```bash
hermes kanban reclaim <child-id> --reason "serializing the profile"
hermes kanban link <parent-id> <child-id>
```

**Order matters beyond serialization.** If card B's questions depend on card A's outcome
(e.g. "where does the LLM call run?" depends on the auth decision), B must be the child —
otherwise B's worker answers from assumption.

**Verify after filing a batch:**

```bash
hermes kanban list | grep -E "running|ready"   # more than one "running" on one profile = trap
hermes -p <profile> sessions list | head -5    # two "just now" entries on one profile = trap
```

---

## 3. Restarting an agent

Agents are profiles, so a "restart" is: stop whatever is running, then start it again.

### 3a. Check what's running

```bash
hermes gateway status
hermes gateway status --profile scout
ps aux | grep -i hermes | grep -v grep
```

### 3b. Restart a single agent's gateway

```bash
hermes -p scout gateway stop
hermes -p scout gateway start      # or: hermes gateway restart
```

### 3c. One-shot (fire and forget) — for a stuck agent

```bash
hermes -p scout chat -q "Status check: what are you working on right now?"
```

### 3d. Interactive (PTY) — for real back-and-forth

```bash
tmux new-session -d -s scout -x 120 -y 40 'hermes -p scout'
sleep 8
tmux send-keys -t scout 'Give me your current status.' Enter
sleep 20
tmux capture-pane -t scout -p | tail -30
tmux send-keys -t scout '/exit' Enter
```

### 3e. Verify the restart worked

```bash
hermes -p scout sessions list | head -5
```

Then check the agent actually did something: new file in its desk, or a kanban comment.

---

## 4. Failure modes and what to do

| Symptom | Likely cause | Fix |
|---|---|---|
| Agent silent, gateway up | Idle — nothing scheduled | Give it work; it's not broken, it's unemployed |
| Agent silent, gateway down | Gateway not started | `hermes -p <name> gateway start` |
| `whatsapp_unpaired` | WhatsApp session lost | `hermes whatsapp` → re-scan QR |
| Cron job never fires | Scheduler stopped / bad schedule | `hermes cron list`, `hermes cron run <id>` |
| Repeated auth errors | Expired credential | `hermes -p <name> auth list`, re-auth |
| Disk full | Cache/logs | Clear `~/.hermes/cache`, rotate logs |
| Agent looping / burning tokens | Runaway task | Kill the process; check `~/.hermes/logs/errors.log` |
| Two agents on one profile | Misconfig | Separate immediately — memory corruption |
| Two cards to one profile both `running` | Kanban auto-dispatch (§2b) | `reclaim` the child, then `link` parent→child |
| Card stuck in `todo` while parent is open | Normal dependency block | Nothing — it auto-promotes when the parent completes |
| Agent writes nothing for days | Wedge or wrong workdir | Restart; check it's reading the right desk |

---

## 5. Alerting Eric

**Channels — live status:**
- ✅ **Email — LIVE.** Alerts go to `enormandin73@gmail.com` via Gmail SMTP
  (`GMAIL_APP_PASSWORD` in `~/.hermes/.env`). **Test alert delivered 2026-10-21:
  self-test SENT, `smtp.gmail.com` accepted (250).**
- ✅ **Discord — LIVE.** Bot `ThingzToDo#1084` connected (gateway.log: "Connected as
  ThingzToDo#1084", "✓ discord reconnected successfully"). Self-test delivered
  2026-10-21 (SENT, HTTP 200 accepted). Automated sweep currently alerts by
  email; a Discord sender (`thingztodo_discord_alert.py`) is wired and ready — it
  sends to `DISCORD_HOME_CHANNEL` (`1562613874400690209`) via the bot token.
- ❌ **WhatsApp — NOT live.** See the constraint below.

### Verified test results (2026-10-21)

Outbound alert channels were proven live end-to-end with a real test alert:

- **Email** — `thingztodo_alert.py --self-test` → **SENT** (SMTP 250 accepted by
  `smtp.gmail.com`, delivered to `enormandin73@gmail.com`).
- **Discord** — `thingztodo_discord_alert.py --self-test` → **SENT** (HTTP 200
  accepted by Discord, posted to `1562613874400690209`).
- **WhatsApp** — **cannot be live today** (see constraint below); no test could be
  demonstrated because the bridge is not paired/running.

### ⚠️ The WhatsApp constraint — read this before promising alerts

Hermes's built-in WhatsApp bridge is **Baileys**, a paired WhatsApp Web session. Code
inspection (2026-10-21) of `bridge.js` `POST /send` and the Python adapter's `_standalone_send`
confirm there is **NO cold-start gate**: the transport only requires the bridge to be
connected and serving this profile's session, and Baileys delivers to any registered
WhatsApp JID. So "no cold-start outbound" is NOT supported by the code — the blocker is
purely operational, and it is a personal-device-limited account, not a verified business
API with opt-in.

**WhatsApp alerts do NOT work today** (operational reasons, not a code gate):
- The bridge session/QR pair is absent and no bridge process is running
  (`~/.hermes/whatsapp` does not exist). `WHATSAPP_ENABLED` and
  `WHATSAPP_ALLOWED_USERS` are set in `.env`, but without a paired session there is
  nothing to deliver on.
- It is a **personal WhatsApp Web account** (device-limited); not a reliable path for
  alerting arbitrary cold numbers.

**Work needed before any WhatsApp alert is live:**
1. QR-pair a phone (`hermes whatsapp` → pair) and confirm the bridge is running
   (`~/.hermes/whatsapp/session` present, a bridge process alive).
2. Ensure `WHATSAPP_ENABLED=true`, `WHATSAPP_ALLOWED_USERS` (or `*`) and
   `DISCORD_HOME_CHANNEL`/bot token are set.
3. Send a cold test from a *new* number and verify delivery.

Until then, alerts go out by **email + Discord** and the gap is stated plainly.
Never tell Eric WhatsApp alerts are working when they are not.

### Alert format (always)

```
[P1|P2|P3] <agent> — <one-line what broke>
Detected: <timestamp>
Evidence: <command + output>
Action taken: <what you did>
Needs from Eric: <what, or "nothing — resolved">
```

### Severity

- **P1** — agent down, or production ungated → alert immediately, every channel.
  Escalate to Eric if unresolved in 15 minutes.
- **P2** — degraded, erroring, cron stopped → alert within the hour, fix, report.
- **P3** — hygiene, capacity, drift → batch into the regular status report.

### Suppression

Never send the same alert twice in an hour. Aggregate repeats into one line. Flapping
alerts train Eric to ignore you — worse than no alerting at all.

---

## 6. The blind spot — nobody watches Concierge

**Concierge cannot restart itself.** If Concierge is down, the monitoring is down, and
the team degrades silently.

Mitigations, in order of effort:

1. **External cron check.** A launchd job / cron that pings `desks/ops/heartbeat` and
   emails Eric if it goes stale. *(To be built.)*
2. **Irock checks in.** The orchestrator periodically verifies Concierge is alive.
3. **Eric checks the status page.** `desks/ops/STATUS.md` is readable by anyone, anytime.

**Tell Eric this is here.** An honest known gap beats a silent one.

---

## 7. Routine maintenance

- **Daily** — Concierge posts operational status to `desks/ops/STATUS.md`.
- **Weekly** — review the board; archive stale cards; check disk and credential age.
- **Monthly** — review cron jobs, prune old sessions, verify desk output is landing.

---

## 8. Adding a new agent

```bash
hermes profile create <name> --clone \
  --description "One or two sentences on what this agent is good at."
```

Then:

1. Write `~/.hermes/profiles/<name>/SOUL.md` — persona, mandate, boundaries.
2. Write `~/.hermes/profiles/<name>/memories/MEMORY.md` — who it is, who the team is.
   Read the clone-seeded file first; it carries the *default* profile's memory, not yours.
3. Add its desk under `thingztodo/desks/<name>/`.
4. Add it to this runbook and to `thingztodo/docs/CHARTER.md` (and `docs/OPERATIONS.md`).
5. Give it its own messaging channel if it needs one — **never clone channels into two
   profiles**; two gateways holding one bot token fight over it. Instead:
   - Create the channel with the bot token (`POST /guilds/<gid>/channels`, type 0,
     `parent_id` = the team category).
   - Append a route to `gateway.profile_routes` on the **default** profile — read the
     current array first and append, never overwrite:
     `hermes config get gateway.profile_routes --json` → add
     `{"name":"<channel>","platform":"discord","guild_id":"<gid>","chat_id":"<id>","profile":"<name>"}`
     → `hermes config set gateway.profile_routes '<full array>'`.
   - Set `DISCORD_ALLOWED_USERS=<Eric's numeric id>` in the **new profile's own** `.env`.
     A username in the allowlist silently denies everyone.
   - Set `discord.home_channel` for that profile so its proactive posts land somewhere:
     `hermes -p <name> config set discord.home_channel <channel id>`.
   - The gateway picks up new routes without a restart — confirm via
     `served_profiles` in `~/.hermes/gateway_state.json`.
6. **Post to Discord with `hermes send`, not a bespoke script:**
   `hermes send -t discord:#<channel> -f <file>`. It reuses the gateway's credentials and
   needs no agent loop. It splits messages over 2000 chars automatically.
7. **Verify the agent actually produced its claimed deliverables.** A first-session agent
   will sometimes narrate a file write it never performed — check the path exists before
   reporting the work as done.
8. **File only one card per profile at a time** (§2b). Link dependents as children.

---

## 9. Emergency contacts

- **Eric Normandin** — founder, owner, final decision
  - WhatsApp: "Eric Normandin" — **613-447-3742**
  - LinkedIn: linkedin.com/in/jeneric
- **Irock** — orchestrator, created this team
