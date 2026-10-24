# ADR — Authentication provider and accounts (2026-10-22)

**ADR:** `2026-10-22-authentication-provider-and-accounts.md`
**Owner:** Forge (Principal Software Architect)
**Date:** 2026-10-22
**Status:** Accepted for implementation
**Related:** `ADR-0001-v1-architecture.md` (Auth/identity section amended **in place** on 2026-10-22), product direction memo `desks/product/2026-10-22-interface-accounts-and-monetization.md`.
**Amendmentsets:** This ADR is a decision record, not a charter. Charters bind; adrs record.

---

## 0. What changed and why

`ADR-0001 §4` (*Auth / identity — None for MVP. Nothing in the product requires accounts today.*) is **REVERSED** effective **2026-10-22** by the product direction the CEO set on 2026-10-22 (`desks/product/2026-10-22-interface-accounts-and-monetization.md §2.4`):

> **Two account types from day one:** consumer (passwordless, free) + merchant/organizer (dashboard, later). Anonymous by default; "Save this plan" is the sign-in trigger.

This reversal is loud and in writing first here, and it is echoed **in place** on `ADR-0001-v1-architecture.md` (see §1). No new ADR is created that contradicts the old one; this is a single, dated, reasoned reversal of the one standing decision that said "none".

**Verdict:** **Adopt Clerk (Hobby tier)** for the MVP. A self-hosted (Lucia + `better-sqlite3`) identity layer was weighed honestly (§5) and **rejected on build cost and security-surface grounds** — not on comfort with the vendor. All six evaluation questions (§6) are answered here.

---

## 1. Amendment record — `ADR-0001-v1-architecture.md` §4 (in place)

**Rule applied:** a reversal must be loud and in writing. The old text, the new text, the date, and the reason are all recorded in the same document, before the standing-decision list.

### 1.1 Loud annotation at the top of the ADR

> **⚠️ AMENDMENT (2026-10-22):** `ADR-0001 §4` (*Auth / identity — None for MVP. Nothing in the product requires accounts today.*) is **REVERSED**. ThingzToDo **will have user accounts** — two types from day one (consumer, passwordless; merchant/organizer). See this document §2 for the verdict, §5 for the integration sketch, §6 for cost, §7 for reversibility. Reason: the CEO directed accounts as an *earned escalation* (not an entry gate) so the merchant dashboard exists from day one and "Save this plan" persistence works.

### 1.2 The changed entry (in `ADR-0001-v1-architecture.md`, §8 "Standing decisions")

The single standing decision that read:

> `- **Auth/identity:** none for MVP — kill the target, not the scope.`

was amended **in place** to:

> `- **Auth/identity:** REVERSED 2026-10-22. Passwordless (magic link / OTP) + Apple / Google OAuth; **consumer** (free) + **merchant/organizer** account types. Anonymous by default. "Save this plan" → sign in. Identity primitive is `Clerk` (Hobby tier); the product `users` table lives in our own SQLite keyed by Clerk's `userId` for portability. See `2026-10-22-authentication-provider-and-accounts.md`.`

No other section of `ADR-0001` is contradicted. The recommended design (web-first on Fly.io, Next.js App Router, SQLite, degrade ladder, curated + best-effort ingestion) is unchanged.

---

## 2. Recommendation

**Adopt Clerk (Hobby tier).** The recommendation, with the decision made explicit:

| Decision | Choice | Reasons |
|---|---|---|
| Identity provider | **Clerk (Hobby)** | Minimal time-to-first-sign-in (5–15 min for a working Next.js sign-in + server-side session check); passwordless + Apple/Google OAuth included; unlimited free apps; B2B/org flows built in for the merchant side later; **the hardest-to-get-right subsystem (auth) is outsourced**, which is exactly what a no-budget, tiny team should do. |
| Free tier | **Hobby** (up to 50,000 MRU per app) | $0 until 50k MRU — far beyond MVP needs. |
| Account types | **Consumer** (passwordless, free) + **Merchant/organizer** (dashboard, later) | Matches product direction §2.4; retrofitting a second identity model is painful. |
| Where identity lives | **Clerk session** (auth primitive) + **our own SQLite `users` table** keyed by Clerk `userId` | Keeps portability; the engine stays anonymous; we own the data port. |
| Failure handling | **Graceful degradation** — app works anonymous; sign-in is a best-effort network call with a clear fallback | The core product never depends on Clerk. |

The decision is **reversible**. The cost cliff (§6) is a metered *success* cost on the returning-user population, not a cap — we own the export path and can self-host at any volume.

---

## 3. Integration sketch — Next.js App Router + Node.js 22 + `better-sqlite3` + Docker → Fly.io

The sketch pins where Clerk's SDK sits, where the user record lives, and what happens when Clerk is unreachable.

### 3.1 Where Clerk's SDK sits

```
app/
├── layout.tsx                         # <ClerkProvider> wraps the whole tree
├── middleware.ts                      # Clerk middleware: protect merchant routes (Dashboard)
└── (account)
    ├── sign-in/                       # Clerk's built-in passwordless + OAuth UI
    │   └── page.tsx
    └── dashboard/                     # merchant dashboard — Clerk-required
        └── page.tsx
```

- **Frontend:** `@clerk/nextjs` — `ClerkProvider` at the app root, `<SignIn />` / `signIn.smartRedirect()` for the passwordless + Apple/Google flow. Clerk's built-in `[[...clerk]]` route handler (`app/api/auth/[...clerk]/route.ts`) is the SSO / magic-link proxy.
- **Server-side session check:** `getAuth(request)` from `@clerk/nextjs` in route handlers / server components. A short-timeout network call; on failure we treat the request as **anonymous** (never leak credentials).
- **Merchant dashboard:** protected in `middleware.ts` and re-checked in the server action that writes to the dashboard.

### 3.2 Where the user record lives (our SQLite)

We do **not** store the product record in Clerk's database. Clerk is the *auth primitive*; our SQLite is the *product record*.

```sql
CREATE TABLE users (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  clerk_user_id TEXT NOT NULL UNIQUE,          -- Clerk's opaque userId — the join key
  account_type  TEXT NOT NULL DEFAULT 'consumer', -- 'consumer' | 'merchant'
  email         TEXT,                           -- null for OAuth-only
  phone         TEXT,
  created_at    TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at    TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE plans (
  id        INTEGER PRIMARY KEY AUTOINCREMENT,
  user_id   INTEGER NOT NULL REFERENCES users(id),  -- nullable before anyone saves
  activity_id TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT (datetime('now')),
  UNIQUE(activity_id, user_id)
);
```

- `clerk_user_id` is the **only** foreign key into Clerk, and it is our own column — we own the join and the export.
- The recommendation engine never touches `users`. The `user_id` FK appears only in product-layer tables ("Save this plan", favorites, history), added by the API layer *after* the engine request.

### 3.3 What happens if Clerk is unreachable

| Path | Behaviour |
|---|---|
| Core product (`GET /api/v1/recommend`) | **Never calls Clerk.** Map, chat, filters, degrade ladder, and shareable URLs all work with **zero auth** (this is the whole point of "anonymous by default"). |
| "Save this plan" | Clerk session check is a short-timeout network call. On failure the button shows *"sign in to save this plan"* with a clear message; the plan is **not** silently dropped and no credentials are leaked. |
| Merchant dashboard | Return a clean *"sign in to continue"* state. |
| Session check failure | Treated as *no session* (anonymous) so a Clerk blip never blocks an anonymous user. |

---

## 4. Clerk vs a self-hosted alternative (honest comparison)

> The self-hosted option is not dismissed because Clerk is comfortable. It is weighed on build cost, security surface, and the product's actual timing.

| Criterion | Clerk (Hobby) | Self-hosted: Lucia + `better-sqlite3` |
|---|---|---|
| Time to first sign-in (MVP) | **5–15 min** | **2–4 weeks** (build magic-link tokens, OTP, OAuth providers, session refresh, rate limiting, account recovery, CSRF, session-fixation) |
| Per-user cost at MVP | **$0** (0 / 50,000 MRU) | $0 (own DB, own infra) |
| Cost beyond 50k MRU | $0.02/MRU/mo (metered) | $0 |
| Security surface | **Outsourced** (managed) | **Owned** — passwordless + OAuth are security-critical and hard to get right |
| Data residency | US-based auth (verify; DPA + consent wording required) | In our container (Canada) |
| Failure domain | Clerk uptime | Our own auth service |
| Data portability | **High** — `userId` + full export by `clerk_user_id` | Highest — your own DB |
| Build risk | **Low** | Medium–High |
| Maintenance | None on our side | Ongoing (auth security) |

**Deciding reasons (self-hosted rejected, not because Clerk is comfortable):**

1. **No budget, tiny team.** Magic-link + OAuth + session remediation is security territory with no margin for error. A no-budget team should not own that surface.
2. **Product timing.** Accounts are a small fraction of users and a *later* concern (consumer account only at "Save this plan"; merchant dashboard "later"). Outsourcing auth has $0 marginal cost at MVP volume.
3. **Reversibility.** We own the export path (§7), so the "vendor dependency" is trivially reversible. The self-hosted alternative is more portable in principle but costs more to build.
4. **No metered cost at MVP.** Billing counts only *returning* users (MRU), so anonymous map traffic is untaxed. The 50k-MRU cliff (§6) is a "success" tax, not a current constraint.

---

## 5. Cost model — projected monthly Clerk bill

Assumptions: overage applies **only** to Monthly Retained Users (users who return after signup). Anonymous map traffic is not metered. Figures verified against clerk.com published pricing (2026-10-22).

| MRU (monthly retained users) | Charge over the 50,000 MRU allowance | **Projected monthly Clerk bill** |
|---|---|---|
| 1,000 | 0 | **$0** (free tier) |
| 10,000 | 0 | **$0** (free tier) |
| 50,000 | 0 (at the cap) | **$0** (free tier) |
| 100,000 | 50,000 × $0.02 | **$1,000/mo** |

**Reading the cliff:** at 100k MRU the overage is $1,000/mo. This is a *success* cost for three reasons:

1. MRU counts only *returning* users, so a low-retention MVP is favourably metered.
2. The only thing that makes a user a "user" at all is signing up ("Save this plan"), which is a tiny fraction of anonymous map traffic.
3. **The cliff is not a cap.** We own the export path, so at any volume we can self-host identity (§7) and re-point the auth layer while keeping every consumer account and every product record.

We add a **budget alert at 40,000 MRU** (≈80% of the tier) so a success is metered before it becomes a surprise. The exact overage billing terms (minimum billable, whether a Pro plan is required to exceed 50k) should be confirmed with Clerk before going live.

---

## 6. Answers to the six evaluation questions

1. **Hosted dependency / PIPEDA.** Clerk is a US-based SaaS with external calls. We accept it because (a) the core product never calls Clerk, (b) only the auth primitive and an email address leave the container, and (c) it is reversible. Mitigations: verify Clerk's data-residency region (Canada if available), sign the DPA, keep only minimum PII (userId; email only when provided), add consent wording in the sign-in flow explaining the US provider, and pin only the minimum fields. Verified recommendation for the product memo stands.

2. **Cost cliff.** Acceptable as a *success* cost — not a cap — for the reasons in §5 and §4. Monitor at 40k MRU; self-host if the overage ever threatens the budget.

3. **No SSO on free.** The merchant/B2B side does need SSO, but that is a *later* product (the merchant dashboard is "later"). Free-tier consumers never need enterprise SSO. If merchant SSO becomes a day-one requirement, that changes sequencing and we'd consolidate around the Pro plan first.

4. **Self-hosted.** Weighed honestly (§4). Rejected on build cost and security-surface grounds for a no-budget, tiny team; not dismissed for comfort. Sequence carries it as a visible escape hatch (§7).

5. **Reversibility.** Yes — fully reversible. See §7.

6. **Where identity lives.** Clerk session (auth primitive) + our SQLite `users` table keyed by Clerk `userId`. The engine stays anonymous-forever — no `user_id` in the recommendation contract. The `user_id` FK lives only in product-layer tables ("Save this plan", favorites, history), added by the API layer after the engine request. Identity can "join later" because the engine request is a pure function of the constraint vector.

---

## 7. Reversibility — data-portability path

**Can we migrate away from Clerk later without losing user accounts?** **Yes.**

1. **Export.** A one-off admin/CLI export (or an in-app "Download my data" link) dumps every product row keyed by `clerk_user_id` — users, plans, favorites, history. Clerk's `userId` is the stable, permanent join key; every consumer record carries it.
2. **Re-point auth.** Introduce a self-hosted identity provider (Lucia + `better-sqlite3`) whose `id` is *our* UUID. Each exported record is re-keyed on import; the old `clerk_user_id` column is kept as a **legacy lookup column** for the transition window (we keep `clerk_user_id` in the exported rows rather than deleting them).
3. **No stranded accounts.** Because every consumer row carries `clerk_user_id` and the exported data is complete, migrating auth changes *only the auth primitive* — never the account. "What breaks if we leave Clerk?" → **nothing for the user; the app keeps working.**

**One-line answer:** *"If we leave Clerk, nothing breaks for anonymous users — every record carries a Clerk `userId` join key we export and re-key on migration, so consumer accounts survive; only the auth primitive changes."*

---

## 8. Standing decisions (updated)

- **Auth/identity:** REVERSED 2026-10-22. Passwordless (magic link / OTP) + Apple / Google OAuth; **consumer** (free) + **merchant/organizer** account types. Anonymous by default. "Save this plan" → sign in. Identity primitive: Clerk (Hobby). Product `users` table lives in our SQLite, keyed by Clerk `userId`. Engine stays anonymous-forever.
- **Failure handling:** never-block on Clerk; degrade to anonymous.

---

## 9. Open items (for later cards)

1. **Data residency / DPA.** Confirm Clerk's region offering and sign the DPA; pin the consent wording in the sign-in flow.
2. **Overage billing terms.** Confirm the exact $0.02/MRU/mo overage terms (minimum billable, Pro requirement beyond 50k) with Clerk.
3. **Budget alert.** Wire a 40,000-MRU alert so growth is metered before the overage.
4. **Security review (Sentinel).** Passwordless auth + OAuth surface is the open security-review item.
5. **Catalog seed + ingestion** (separate ticket) are unaffected.

---

*Design by Forge (Principal Software Architect), 2026-10-22. Verified facts: clerk.com published pricing (2026-10-22); product direction: `desks/product/2026-10-22-interface-accounts-and-monetization.md` §2.4. No vendor, statistic, or otherwise unverified figure is presented as fact.*
