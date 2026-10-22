# Outbound Email Path Readiness — Assessment

**ADR:** `desks/engineering/decisions/2026-10-21-outbound-email-path-readiness.md`
**Owner:** Forge (Principal Software Architect)
**Date:** 2026-10-21
**Status:** Reject / blocked on credentials — no outbound email path exists today
**Related:** `desks/ops/RUNBOOK.md` §5 (Alerting Eric), `desks/ops/STATUS.md` (alert channels)

---

## 0. Purpose & scope

Determines whether any outbound email path exists that can deliver a real test alert to
Eric Normandin, using the available tooling (`himalaya` CLI / SMTP credentials). Documents
exactly what must be supplied before email alerts can be enabled. **Not a claim that email
alerts work** — this document exists so that claim is never implied.

---

## 1. Findings

### 1.1 No `himalaya` CLI is installed

- `himalaya: command not found` on PATH; no binary in `/usr/local/bin`, `/opt/homebrew/bin`,
  or `~/.cargo/bin`.
- No `~/.config/himalaya/config.toml` exists.
- The skill exists as documentation (`skills/email/himalaya/SKILL.md`) but the CLI is not
  present, so its SMTP backend cannot be exercised.

### 1.2 No SMTP/IMAP credentials or configuration exist anywhere

- `~/.hermes/config.yaml`: no `mail`, `smtp`, `imap`, `email`, or `himalaya` section.
- Environment: no `SMTP_*`, `IMAP_*`, `MAIL_*`, `SENDMAIL_*`, or provider email vars set.
- `~/.hermes/profiles/architect/.env` (the credential store) exists but is locked; its
  contents are **not readable** and are deliberately not inspected.
- `hermes send --list` → **no messaging platforms configured**, and none of them are email.
- `hermes doctor` (config validation) reports nothing about email — it has no email adapter to
  validate.

### 1.3 State database confirms no credential rows

`state.db` is the session database only (kanban/session rows). No `smtp`, `imap`, `email`,
`mail`, `auth`, `login`, or `pass` credential tables exist.

### 1.4 System MTAs exist but are not an email account

`/usr/sbin/sendmail` and `/usr/sbin/postfix` are present on the host. They are **mail
transfer agents**, not an account to send from, and no SMTP credentials (login/password) are
configured against them. They do not provide outbound email.

### 1.5 The ThingzToDo app does not exist yet

`/Users/martennormandin/thingztodo/` contains only `desks/` and `docs/` — no `app/`
(application code). There is no email integration in the app to point at any SMTP service.

---

## 2. Conclusion

**There is no outbound email path available today.** No SMTP credentials, no configured email
service account, no `himalaya` CLI, and no email platform registered in Hermes. A test alert
*cannot* be sent or verified as delivered.

This is a hard blocker for the "send test alert to Eric" half of this task. Per
`desks/ops/RUNBOOK.md` §5, alerts go out by **email + Discord** until WhatsApp is wired —
so this gap is operationally significant, not cosmetic.

---

## 3. What is needed to enable email alerts

Exactly four things must be supplied before any test can run:

1. **Eric's email address** — **KNOWN as of 2026-10-21:** `enormandin73@gmail.com`
   (recorded in `~/.hermes/.env` as `GMAIL_ADDRESS` and `ALERT_TO`). Still needed:
   the SMTP credential in item 2.
2. **An SMTP server + account** — a working SMTP endpoint to send from, e.g.:
   - any mail provider app password (`host`, `port`, `username`, `password`/`app password`),
     **or**
   - an email-service account (SendGrid, Mailgun, AWS SES, Resend, Postmark...).
   - Port 587 (STARTTLS) or 465 (SSL) are the realistic candidates.
3. **A configured sender identity** — a real `From:` address the mail service will deliver
   from, plus DKIM/SPF alignment if the provider requires it.
4. **Configuration of the sending client** in the ThingzToDo app (and/or a Hermes email
   platform), then a **real test alert + independent confirmation of delivery** (SMTP
   delivery receipt, an inbox read-back, or a delivered-flag).

Delivery confirmation must be verified, not asserted: send the message and show evidence it
landed (e.g. read-back from the configured inbox, or a confirmed SMTP `250 OK` plus a
delivered status). A `piped` send that exits 0 is **not** delivery confirmation.

---

## 4. Alternatives considered and rejected

| Alternative | Verdict | Why |
|---|---|---|
| `himalaya` CLI with SMTP | Rejected | CLI not installed; would still need SMTP host/credentials/From address. |
| `hermes send` to a messaging platform | Rejected | No platform configured; and `hermes send` supports only Telegram/Discord/Slack/Signal/WhatsApp, none of which are email. `list --list` returns "no platforms configured". |
| Host `sendmail`/`postfix` | Rejected | MTAs only; no account, no credentials, not an outbound email path. |
| WhatsApp (RUNBOOK preferred) | Rejected | Baileys bridge cannot cold-start outbound (RUNBOOK §5 §11); that is why email + Discord is the interim path. |
| Build the ThingzToDo email service now | Deferred | No SMTP account supplied; building integration before the credential exists is wasted work. |

---

## 5. How this gets unblocked

- Eric supplies Eric's address + SMTP credentials (or an email-service account) via chat or a
  vault export.
- Put the SMTP config into the ThingzToDo app's config (clearly separated by environment).
- I (Forge) wire the outbound SMTP client, send a test alert to Eric, and independently
  verify delivery before any alarm is routed through it.
- This ADR is revisited once the first real alert has been delivered and confirmed.
