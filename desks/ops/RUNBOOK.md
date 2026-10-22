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

Company home: `/Users/martennormandin/thingztodo/`

Each agent is a **Hermes profile** — its own `config.yaml`, `.env`, `SOUL.md`, memory,
skills, sessions, cron, and state DB. Never point two agents at one profile.

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
| Agent writes nothing for days | Wedge or wrong workdir | Restart; check it's reading the right desk |

---

## 5. Alerting Eric

**Channels — live status:**
- ✅ **Email — LIVE.** Alerts go to `enormandin73@gmail.com` via Gmail SMTP
  (`GMAIL_APP_PASSWORD` in `~/.hermes/.env`). Verified 2026-10-21.
- ✅ **Discord — LIVE.** Bot `ThingzToDo#1084` connected; DM it or `@mention` it.
- ❌ **WhatsApp — NOT live.** See the constraint below.

### ⚠️ The WhatsApp constraint — read this before promising alerts

Hermes's built-in WhatsApp bridge is **Baileys**, a paired WhatsApp Web session. Its
outbound path (`POST /send` on the local Node.js bridge, called from the Python adapter's
`_standalone_send`) is **not** gated on the target having messaged the bot first: it only
requires the bridge to be connected and to serve this profile's session, and Baileys
delivers to any registered WhatsApp JID. So "no cold-start outbound" at the transport layer
is not supported by the code — verified by inspection, 2026-10-21.

**WhatsApp alerts do NOT work today**, for operational reasons, not a code gate:
- The bridge is not configured or connected in this profile (`WHATSAPP_ENABLED` is not
  set, no session/QR pair is present, and no bridge process is running), so no cold-start
  delivery can be demonstrated here.
- It is a **personal WhatsApp Web account** (device-limited; not a verified business API
  with opt-in) — not a reliable path for alerting arbitrary numbers.

A true "text me when an agent breaks" needs one of:

1. **Eric messages the bot once** from **613-447-3742** ("Eric Normandin") to open the
   thread, after which the bot can reply. *Fragile: the session can drop.* The bot's number
   must also be reachable, and inbound must be allowed (see `WHATSAPP_ALLOWED_USERS` /
   `dm_policy` in the profile config).
2. **Twilio** (SMS or WhatsApp Business API) — real outbound, needs an account and a
   little spend. *Recommended for P1 alerts* — it is the only path that can reach a cold
   number directly.

**Work needed before any WhatsApp alert is live:** enable `WHATSAPP_ENABLED`, QR-pair a
phone, and add the target number to the allowlist (`WHATSAPP_ALLOWED_USERS`); then send a
cold test and verify delivery. Until then, alerts go out by email + Discord and the gap is
stated plainly. Never tell Eric WhatsApp alerts are working when they are not.

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
3. Add its desk under `thingztodo/desks/<name>/`.
4. Add it to this runbook and to `thingztodo/docs/CHARTER.md`.
5. Give it its own messaging channel if it needs one — **never clone channels into two
   profiles**; two gateways holding one bot token fight over it.

---

## 9. Emergency contacts

- **Eric Normandin** — founder, owner, final decision
  - WhatsApp: "Eric Normandin" — **613-447-3742**
  - LinkedIn: linkedin.com/in/jeneric
- **Irock** — orchestrator, created this team
