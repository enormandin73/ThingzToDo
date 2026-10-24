# SECURITY-REVIEW-SCOPE.md — Security Review Scope: Passwordless Auth & Payment Handling

**Owner:** Sentinel (Head of Quality & Release)
**Status:** v1.0 draft — for review; not yet ratified
**Applies to:** the two sensitive-data surfaces entering scope: **passwordless authentication**
  and **payment / transaction handling**.
**Reads with:** `desks/quality/STATUS.md` (production gate + release checklist), `TEST-STRATEGY.md`
  (test levels), `ADR-0001` §8 (auth/identity decision), `desks/product/2026-10-22-interface-
  accounts-and-monetization.md` (Clerk evaluation, monetization).
**Decision-independence:** this scope holds **regardless of provider** — Clerk, Auth.js/Lucia, or
  anything else. It is intentionally **not** gated on the Clerk decision.

---

## 0. Purpose

This document defines **what a security review must cover** for passwordless auth and payments,
so that the QA strategy (`TEST-STRATEGY.md`) can be written against concrete acceptance
criteria, and so the production gate (`STATUS.md`) has unambiguous pass/fail items. It is a
**scope document, not a test plan** — it states the rules a review must enforce; the tests that
enforce them are built from it.

This is **not a production feature**. I do not write product features. I define the review
criteria, the block list, and the gate conditions. Forge implements; I judge.

> **Two keys.** Nothing shipped in this surface ships without **Sentinel's gate verdict** (this
> document) **and** **Eric's explicit approval**. See §4.1 and §7.

---

## 1. In-scope / out-of-scope, stated as rules

Rules for **this release** (the auth + payments work entering scope now). "Release" means the
auth- and payment-adjacent changes going into v1; it is explicitly **not** a pass to build
features outside this list.

### 1.1 In scope (must be reviewed)

| ID | Item | Why it is in scope |
|---|---|---|
| S-A-1 | Passwordless sign-in — magic link and/or OTP | Direct auth surface; token handling, expiry, replay, enumeration. |
| S-A-2 | Guest plan URL (30-day, unauthenticated, shareable) | A **bearer credential**; real attack surface (entropy, expiry, revocation, scope). |
| S-A-3 | Account model contract: consumer + merchant | Defines authorization boundary; merchant dashboard is the future privilege-escalation target. |
| S-A-4 | OAuth (Apple / Google) redirect handling | Redirect URI, `state`/CSRF, PKCE — a high-exploitation auth vector. |
| S-A-5 | Payment entry point: affiliate redirect + direct checkout (where in scope) | Money movement; fraud/integrity/chargeback surface. |
| S-A-6 | Sessions, cookies, revocation, rate limiting on auth endpoints | Session theft is the highest-impact auth failure. |
| S-A-7 | Security baseline: headers, secrets hygiene, dependency audit, observability | Breadth baseline that protects every surface. |

### 1.2 Out of scope (explicitly, for this release)

| ID | Item | Reason |
|---|---|---|
| S-O-1 | Raw card data handling / PAN at any layer | **Blocked by design:** we stay out of PCI scope (§3.1). Never ship code that touches card numbers. |
| S-O-2 | Merchant dashboard implementation | Deferred. Only the **authorization-boundary model** (§2.6) is in scope; the dashboard itself is not built now. |
| S-O-3 | Stripe / payment-provider implementation | Owned by Forge/Payments; we define the gate, not the wiring. |
| S-O-4 | Consumer premium / billing feature | Not in this release; money flow is affiliate + (possibly) direct checkout. |
| S-O-5 | i18n / localization | Out of v1. |
| S-O-6 | Primary-account-number storage anywhere | Out of scope until proven absent. |

Rules: an item is **in scope only if** it touches (a) a credential, (b) personal identity data,
or (c) money. Everything else is out of scope and reviewed at its own depth by its owning card.

---

## 2. Authentication security scope

### 2.1 Passwordless flows (magic link / OTP)

| Attribute | Rule |
|---|---|
| Token storage | The magic-link / OTP secret must be **one-way hashed** (e.g. `SHA-256`/`SHA-512` with a per-customer salt) in any local store — never plaintext. Where Clerk is the provider, the secret is Clerk's, but we must still treat the verification token that flows to us as untrusted input. |
| Token lifetime | **Short-lived**: absolute expiry of **≤ 15 minutes** from issue for the clickable link; the link must be single-use ( invalidated immediately after one successful use or on first click, whichever first). Sliding/expiring-without-use expiry is not acceptable for the click path. |
| Entropy | The token must be high-entropy and **unguessable**: ≥ 128 bits of entropy (e.g. ≥ 21 random alphanumeric characters from a 64-symbol alphabet). Presumption of **no weaker fallback** — a 6-digit numeric OTP (10^6, ~20 bits) is **not** acceptable for the click path because it is brute-forceable. |
| Replay | Single-use is mandatory. After a successful sign-in from the link, the token is expired/invalidated server-side; a second click on the same link fails. |
| Transport | **HTTPS only.** Token must never appear in URLs of any persistent form — no logging, no analytics, no browser history, no `Referer` leak (see guest URL rules in §2.5 for propagation). |
| Rate limiting | The "resend / request link" endpoint must be rate-limited (per email + per IP, e.g. 5 sends/hour per email, 20/hour per IP) to blunt enumeration and spam. The sign-in endpoint must also rate-limit on failure. |
| Session on success | Signing in via a magic link **creates a fresh server session** and rotates any session identifier; the link carries no persistent session. |

### 2.2 Session handling

| Attribute | Rule |
|---|---|
| Where the session lives | Server-side session (canonical session record + session id), or a **server-side-signed** JWT held in an `httpOnly` cookie. We do **not** store a plaintext user password (auth is passwordless). Sessions must be revocable. |
| Cookie flags | Mandatory in production: `HttpOnly`, `Secure` (HTTPS), `SameSite=Lax` (Strict for sensitive routes), `Path=/`, `Domain` scoped to the root domain (no wildcard subdomains that could leak). No `Secure` flag + `HttpOnly` must be flagged as a defect. |
| Rotation | Session id rotates on privilege-level change (login, role change, plan change). Old sessions invalidated immediately. |
| Revocation on sign-out | Sign-out **invalidates the session server-side** (hard revoke, not "soft delete"). Additionally, sessions must be revocable by the user from any device (a "log out everywhere" path). |
| Timeout | Absolute expiry (e.g. **8 hours**) + idle timeout (e.g. **30 minutes**). Sliding expiry is permissible; the absolute bound is hard. |
| CSRF | State-changing API endpoints (create account, change email, refund) require a CSRF token for non-browser clients, or rely on `SameSite` + custom header for browser clients. `SameSite` alone is not sufficient proof for an API; the test must show the CSRF control. |

### 2.3 Account enumeration

**Rule: an attacker must not be able to tell whether an email address is registered.**

- The magic-link offer and the registration flow return the **same generic email** regardless of
  whether the address exists ("If that email is registered, a link is on its way").
- No "email not found", no "already registered", no timing distinguishable from noise on the
  registration/account-lookup endpoints. Any difference in response timing must be mitigated.
- The magic-link endpoint returns a single generic success/failure envelope; it does **not**
  disclose enumeration to the caller.
- OTP resend endpoint rate-limited (§2.1) so enumeration via repeated resends is not possible.
- Test: a test asserting that registered and unregistered emails receive byte-identical
  confirmation emails.

### 2.4 OAuth (Apple / Google) redirect handling and state/CSRF

| Attribute | Rule |
|---|---|
| `state` | **Mandatory.** A high-entropy unguessable random value, bound to the initiating session/account, **verified before** the OAuth provider code exchange completes. Failure to verify `state` is a **blocking defect** (CSRF / account-swap). |
| PKCE | **Mandatory** for the authorization-code flow (`code_challenge`/`code_verifier`, S256). No implicit flow. |
| Redirect URI | **Exact match** against an allowlist of registered redirect URIs. Wildcards are not allowed. Any mismatch is a redirect-malicious-target defect. |
| Redirect target allowlist | Only trusted, vetted domains; an internal/global allowlist. No open redirect via `?redirect=` style parameter. |
| Apple-specific | Apple requires domain association for sign-in; the alternative-identity provider (Apple) must be configured and its domain constraints verified. |
| Tokens returned to client | The OAuth `id` token is accepted **by the provider**, not from the client; we must never trust client-supplied id tokens as authority. |

### 2.5 Guest plan URL — bearer credential threat model

The guest plan URL is an **unauthenticated, time-limited, shareable link that lets anyone view a
plan without an account**. It is a **bearer credential**: possession is access. It must be
treated at the same rigour as a password.

**Bearer properties (what makes it secure):**

| Attribute | Rule |
|---|---|
| Entropy | **≥ 128 bits of cryptographic randomness** from a CSPRNG (e.g. `secrets`-class generator, ~21+ alphanumeric chars). **Not** a sequential counter, not an email hash, not a slug. **Test:** a randomness/entropy test (e.g. chi-squared on the token alphabet) plus absence of a sequential/predictable generator unit test. |
| Expiry | **Absolute 30-day TTL** (per product spec). A rolling/expiring-after-last-use window is **not** acceptable because the URL is shared and persisted in third-party clients (chat, email) where it is out of our control. The URL is also not usable after the 30 days. |
| Revocation | **Server-side revocation** at any time (admin or owner-triggered). Revocation must be an explicit write (`revoked_at` on the plan + invalidation) — not a silent expiry. On revocation the link becomes inert and shows a generic "this plan is no longer available" message. |
| Scope of what it grants | The guest link grants **read-only access** to the **specific shared plan**: view the plan's activities, map, and itinerary. It must **not** grant: (a) account creation or sign-in, (b) mutation of the plan, (c) access to other people's plans, (d) the consumer dashboard or any merchant surface. Revocation is scoped to that plan only. |
| Leakage — transport | **HTTPS only.** `Referrer-Policy: no-referrer` (or `same-origin`) **must** be set so the URL is not leaked to third parties through navigation. Never log the URL or its referer. |
| Leakage — embedding | Do **not** render the plan in a third-party site's iframe. If it *must* be embedded for a partner surface, enforce `X-Frame-Options: SAMEORIGIN` (or `frame-ancestors` in a CSP) and require an explicit flag. Avoid iframe embedding entirely for the MVP. |
| Leakage — history | The link must never be written to logs, analytics events, or server-side request logs. UI reminders: copy into chat, do not copy into email body. |
| Rate limiting on access | Plan access is rate-limited (e.g. 100 reqs/hour per URL) to blunt automated harvesting/scraping of many plans. |
| Single use vs. persisted | Because the URL is shared across chat clients, **persisted-by-default** is required; single-use would break the viral loop. Revocation is the controlled kill-switch. |
| Ownership/revocation targets | The owner of the plan (the user who created it) must be able to revoke; a generic admin revoke path is the escalation. The **creator** must not be able to revoke *other* plans' links. |

### 2.6 Two account types (consumer + merchant) — authorization boundaries

| Attribute | Rule |
|---|---|
| Account types | **Consumer** (passwordless sign-in; read plans, save, share, optionally pay for premium) and **merchant** (dashboard: list venues, manage offerings, view analytics, later process). |
| Boundary rule | The two types must be enforced **server-side** via a role/account-type claim that the client **cannot spoof**. Never trust a client-supplied `role` field as authority. |
| Role assertion | The provider (Clerk or self-hosted) asserts the role; the session carries a **server-side** mapping of account_type → capabilities. The dashboard and any money endpoints **verify** the role on every request. |
| Merchant dashboard → escalation | The merchant dashboard is a **future privilege-escalation target**. For now only the *model* is in scope; when it is built it must have: MFA on sign-in, an audit log of all admin actions, no direct consumer PII exposure, and an explicit admin-approval gate for sensitive actions. See §7. |
| Guest sessions | Guest plan access (§2.5) exists in a separate namespace from accounts — no claim of "guest role = consumer" or vice versa. |

### 2.7 Third-party dependency (Clerk) — trust boundary + PIPEDA

The Clerk decision is **open** (Forge is evaluating; the decision is not made). This scope holds
for Clerk **or** Auth.js/Lucia **or** any other provider.

| Attribute | Rule |
|---|---|
| What we trust | Clerk's **hosted auth** implementation itself (session, provider connection, email delivery) — we trust only what it publishes and we verify its behaviour through our own integration tests, not its claims. |
| What we verify | (a) The session/claims we receive are **authenticated by Clerk** and not client-forged; (b) we receive a stable, unique `userId`; (c) user metadata we store is exactly what we need; (d) the session expiry/refresh behaves as specified and is enforced server-side. |
| Outage behaviour | If Clerk is down: the app must degrade to **anonymous reading** (guest plan URL path still works); sign-in/sign-up must **not** return a 500 or misleading "register" state. No trade-off where an outage forces sign-ups. |
| Data-residency / PIPEDA | Clerk stores personal identity data of Canadians. **We must verify Clerk's hosting region** (US vs. Canadian region) and, if Canadian data leaves Canada, obtain **express consent** for the transfer and execute a DPA. If Clerk cannot commit to Canadian residency, **self-hosted Auth.js/Lucia** (identity stored in our own DB) becomes the compliant path. **Decision required by Eric** (see §7). |
| Reversibility | If Clerk is chosen, we must preserve a path to migrate away later **without losing user accounts**. The user record must carry a `userId` and a provider-agnostic identity, not a Clerk-specific key. |
| Secrets | Clerk publishable + secret keys must be **environment-scoped** (never committed); a secret-key leak triggers key rotation without a full re-auth of existing users. A secrets scan is part of the gate (§4.1). |

---

## 3. Payments / transactions

### 3.1 PCI-DSS — the clear statement

**We do not handle card data. We must not. Full stop.**

- This is a **design rule**, not a preference. Any code path that touches the raw
  **Primary Account Number (PAN)** in our backend is **blocked** until removed.
- We stay out of PCI scope by **delegating to a PCI-compliant provider** (Stripe, or an
  equivalent). The provider embeds card capture (Stripe Elements/Checkout) in the browser,
  **tokenizes at the card network**, and hands us only a **payment intent / client secret** and
  later an idempotent reference + status.
- **What we ever see:** amounts, currency, success/failure, payment method brand, a
  provider-generated `payment_intent`/`charge` id, and (optionally) the customer's last-4 for
  display. **We never see, store, or log the PAN.**
- **PCI scope we accept:** **PCI-SAQ-A** (the lowest-scope SAQ, because we have no battalion
  storing/transmitting card data). This is the named requirement; as long as we never touch PAN,
  the product's PCI scope is SAQ-A and we scope the verification accordingly.
- If any future requirement ever puts raw card data in our backend, that is a **separate,
  blocked** condition (S-O-1) and does not ship.
- Test: a static-analysis/grep test that **no string resembling a PAN or card number is ever
  written to a log** in the payment path, plus a review of all `console.log` / audit output in
  the checkout flow.

### 3.2 Refunds, disputes, chargebacks — who owns them

| Attribute | Rule |
|---|---|
| Refund ownership | The **product** owns the refund workflow: a merchant (or an admin, or on explicit consumer request) can request a refund; the payment provider processes it; the product records the outcome. Refund requires **authorization** — only the cardholder or an approved agent can trigger one; no bulk/unaudited refunds. |
| Disputes / chargebacks | The product records the **chargeback** beside the payment (see §3.4). The merchant is **not** given unfettered dispute handling; chargeback outcomes are visible to the merchant in the dashboard (deferred). A chargeback on a transaction the merchant did not author is a defect worth resolving quickly. |
| No chargebacks as a product | We do **not** play the role of chargeback lawyer. Refund/chargeback policy is owned by the **merchant** and the **payment provider**; our job is to surface outcomes and keep the audit trail. |

### 3.3 Affiliate link integrity — tampering, injection, redirect validation

Affiliate links are how we drive take-rate revenue. They are a **trust boundary** between us and
the merchant, and a vector for injection.

| Attribute | Rule |
|---|---|
| Integrity | Every affiliate link must be **signed** (HMAC or a signed-short-URL scheme) so a merchant **cannot swap their affiliate id** for another's (e.g. replacing `ref=merchant_a` with an attacker's). Signature validation is done **server-side** when the link is rendered/accessed. |
| Injection | Affiliate parameters are **URL-encoded and sanitized** when rendered; no raw affiliate param is placed into HTML attributes without escaping (XSS vector). |
| Redirect validation | Redirects through affiliate links must be validated against an **allowlist of trusted destinations** (no open redirect). A redirect target outside the allowlist is refused. |
| Same-origin policy | Affiliate clicks that cross origins must be careful with credentials; the origin of the affiliate link is known at render time. |

### 3.4 Receipts, receipts-as-evidence, and the financial audit trail

| Attribute | Rule |
|---|---|
| Receipt content | Every successful payment produces a **receipt** (PDF + embedded in email) containing: amount, currency, payment method brand, timestamp (UTC ISO8601), `payment_intent` id, reference, merchant/plan reference, and an affiliate reference where applicable. Receipts must be **evidence-quality** (immutable, dated, non-rewritten). |
| Audit trail | A **append-only financial log** records every transaction: `id`, `occurred_at`, `amount`, `currency`, `method`, `status` (succeeded/failed/refunded/chargeback), `provider_ref`, `affiliate_id` (if any), `ip_hash`, `user_id_or_guest_plan_id` (or "guest"). This log is the **chargeback evidence** and is retained per the retention policy (§7). |
| Immutability | The audit log is **append-only**; entries are never rewritten. A backdated/falsified entry is a high-severity defect. |
| No card data in logs | The audit log **must not** contain PAN, full card number, or CVV (§3.1). Only tokenized references. |

---

## 4. Production gate implications

### 4.1 What must be true before any account or money feature ships

A feature touching §2 or §3 ships only when **all** of the following are true. Each is a
pass/fail item the production gate enforces (§4.2).

| # | Pre-ship condition | How verified |
|---|---|---|
| P-1 | No secrets committed in the diff (Clerk keys, provider keys, DB creds, URLs containing tokens). | `qa/secrets-scan.txt` |
| P-2 | Dependency audit clean: no known-high / novel-critical vulnerabilities in the pinned toolchain. | `qa/dependency-audit.txt` |
| P-3 | Auth endpoints rate-limited (login, OTP resend, sign-up). | unit + sandbox test + code review |
| P-4 | Session cookie flags audited in the browser (HttpOnly, Secure, SameSite). | browser check |
| P-5 | Security headers present: CSP, HSTS, X-Frame-Options, Referrer-Policy (`no-referrer` where links appear). | `qa/headers-audit.txt` |
| P-6 | PCI statement confirmed: no PAN touches our systems; provider is PCI-compliant (SAQ-A scope). | code review + static scan |
| P-7 | Guest plan URL: entropy test + expiry logic + revocation + leakage (referrer, no-log) all pass. | unit + sandbox + browser |
| P-8 | OAuth: PKCE + `state` verification + redirect allowlist pass. | unit + sandbox |
| P-9 | Account enumeration test passes (identical confirmation emails, generic errors). | unit |
| P-10 | Webhook signature validation tested; idempotency and auto-ack verified. | sandbox + e2E |
| P-11 | Financial audit log append-only verified (receipts + ledger). | unit + code review |
| P-12 | Reversibility confirmed: sign-out revokes sessions; guest links revocable; cards can be refunded/voided. | test + code review |
| P-13 | PIPEDA data-residency decision recorded (Clerk or self-hosted) with consent approach. | written decision |
| P-14 | Staged rollout: auth/money changes deployed behind a feature flag; canary first. | deployment config |

### 4.2 Release-readiness checklist additions (S-x) in `desks/quality/STATUS.md`

These items are **added** to the production gate checklist in `desks/quality/STATUS.md` as a
**security & compliance** section. S-1…S-6 are mandatory for **any** auth or money change;
S-7…S-12 are mandatory before the **first** account/money feature ships.

| ID | Checklist item (added) |
|---|---|
| S-1 | Auth endpoint rate limits configured and passing. |
| S-2 | Session cookie flags audited (HttpOnly / Secure / SameSite) in browser. |
| S-3 | Security headers audit: CSP, HSTS, X-Frame-Options, Referrer-Policy (`no-referrer` on link-bearing pages). |
| S-4 | Secrets scan: zero secrets committed in this release. |
| S-5 | Dependency audit: no High/Critical open vulnerabilities in the pinned toolchain. |
| S-6 | PCI statement confirmed: no PAN in our systems; PCI-SAQ-A scope. |
| S-7 | Guest plan URL: entropy + expiry + revocation + leakage all tested. |
| S-8 | OAuth: PKCE + `state` verification + redirect allowlist tested. |
| S-9 | Account enumeration test passes. |
| S-10 | Webhook signature validation + idempotency tested. |
| S-11 | Financial audit log append-only verified (receipts + ledger). |
| S-12 | Reversibility confirmed: session revoke + guest-link revoke + refunds/voids. |
| S-13 | PIPEDA data-residency decision recorded (Clerk or self-hosted) + consent approach. |
| S-14 | Staged rollout enabled (feature flag + canary) for auth/money changes. |

### 4.3 Concierge — health sweep monitoring (auth + payment)

Concierge's operational health sweep should monitor **first-party** signals (it cannot fix the
provider, but it must know when the product is failing because of it):

| Signal | What to watch | Alert threshold (suggested) |
|---|---|---|
| Auth provider uptime | Clerk (or self-hosted) availability for sign-in. | < 99.9% over a window; 5xx spike |
| Auth error rate | 4xx/5xx on `/api/auth` endpoints. | > 1% error rate |
| Session expiry rate | Proportion of `/api/auth` requests returning 401. | > 1% of requests (round-trip expiry bug) |
| Webhook delivery | Stripe webhook endpoint delivery + signature acceptance. | < 99.9% delivery; failures > 0.1% |
| Payment failure rate | `payment_intent` failures (declined/refunded). | Maybe informational; never a hard block unless a dependent feature regresses |
| Rate-limit errors | 429s on auth endpoints (should be rare; if high, sign-ups are being throttled). | Informational, not blocking |
| Guest-plan access | 4xx/5xx on plan-view endpoints. | Not blocking, but should not be a 500 |

Concierge should alert **Eric** on any of these degrading (P1/P2 per RUNBOOK §5), because a
provider or webhook failure is a **product failure**, not an infra-only event.

---

## 5. Block list — what must be blocked until resolved

These are **hard blocks** at the production gate. A gate verdict is `BLOCK` until the
corresponding item is resolved and the evidence is recorded.

| # | Block | Why it blocks | What unblocks it |
|---|---|---|---|
| B-1 | Clerk data residency / cross-border transfer without explicit consent | PIPEDA non-compliance + loss of Canadian user data. | Written resolution: Clerk hosted in Canada **or** self-hosted; DPA + express consent obtained. |
| B-2 | Any code path that touches card/PAN data | PCI scope expansion; data-breach blast radius. | Confirm delegation to PCI-compliant provider; static scan zero findings. |
| B-3 | Guest plan URL with < 128-bit entropy, no expiry, no revocation, or loggable token | Bearer credential compromise; plan theft at scale. | Entropy ≥ 128 bits; 30-day absolute expiry; server-side revoke; `no-referrer`; no logging. |
| B-4 | OAuth without PKCE + `state` verification + exact redirect-URI allowlist | CSRF / account takeover. | Unit + sandbox pass; code review. |
| B-5 | Affiliate links without integrity (signature or allowlist) | Affiliate id tampering; fraud. | Signed links + allowlist; tests pass. |
| B-6 | Webhook signature validation not implemented | Payment fraud (double-apply, replayed webhooks). | Webhook validation + idempotency tests pass. |
| B-7 | Merchant dashboard without server-side RBAC | Privilege escalation into merchant functions. | Role claim server-enforced; dashboard not shipped before consumer plan ships. |
| B-8 | No staged rollout (feature flag / canary) for auth/money changes | One bad deploy → all users affected. | Feature flag enabled; canary rollout configurable. |
| B-9 | No written PIPEDA retention / breach-notification approach | Non-compliant data lifecycle. | Documented retention + 30-day breach detection mapping. |

---

## 6. Decisions & escalations — requiring Eric's explicit approval

These cannot be resolved by QA alone; they are **business/architecture decisions** with a
security consequence. All four require **Eric's explicit approval in writing** before I will
clear the corresponding block (§5).

| # | Decision | Consequence if wrong | Recommended position |
|---|---|---|---|
| D-1 | **Data residency:** Clerk vs self-hosted (Auth.js/Lucia) | Data leaves Canada → PIPEDA consent burden; self-hosted shifts security surface to us (our job to run). | Prefer **self-hosted** if we cannot commit to Canadian storage; prefer Clerk only if it commits to Canadian residency **and** we can verify via DPA. |
| D-2 | **Direct checkout in scope?** | If we ever pass raw card data to our backend, PCI scope explodes. | Keep out of scope **by delegation** (Stripe); reject any product direction that requires PAN in our backend. |
| D-3 | **Merchant dashboard scope** | An early, unscoped dashboard is a privilege-escalation target. | Deferred until RBAC + audit + MFA model is agreed; do not ship before consumer plan. |
| D-4 | **Financial retention** (how long receipts/audit log are kept) | Too short → un-chargebackable; too long → storage + privacy burden. | Draft retention + breach-notification mapping for Eric's approval. |
| D-5 | **Reversibility standard** (what counts as "reversible" for auth/money) | A "reversible" rollback that can't actually restore accounts or void a payment is not reversible. | Define: session revoke, guest-link revoke, refund/void, and a documented rollback command for the DB. |

---

## 7. Notes & further work

- **Tensibility.** This scope is written so the **QA automation** can be built from it (see
  `TEST-STRATEGY.md`). The next card will define the specific tests and fixtures for S-x items.
- **Documentation.** This document is a scope/rule set. A companion **checklist file** in
  `desks/quality/` records the gate verdict and evidence paths.
- **Open:** the Clerk decision (Forge), the direct-checkout decision (Eric), and the data
  residency resolution. Until D-1 is resolved, the **Clerk-specific** sub-scope (§2.7) is
  conditional and cannot be fully gated.
- **Fraud dependency.** Payment fraud and affiliate integrity (§3.3) are partially **merchant
  and provider-owned**; our scope is the integrity of the link, the webhook, and the audit trail.

---

## References

- `desks/quality/STATUS.md` — production gate + release-readiness checklist.
- `desks/quality/TEST-STRATEGY.md` — test levels and coverage.
- `desks/engineering/decisions/ADR-0001-v1-architecture.md` — stack (Next.js App Router, Node 22,
  `better-sqlite3`, Docker → Fly.io); auth/identity = §8 (open).
- `desks/product/2026-10-22-interface-accounts-and-monetization.md` — Clerk evaluation; two account
  types (consumer + merchant); 30-day guest plan URL; affiliate take-rate monetization.
- `docs/CHARTER.md` — production gate: Sentinel's sign-off **and** Eric's explicit approval.
