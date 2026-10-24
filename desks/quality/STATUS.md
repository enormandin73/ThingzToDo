# STATUS.md — ThingzToDo Production Gate & Release-Readiness Policy

**Owner:** Sentinel (Head of Quality & Release)
**Applies to:** every production deployment of the product repository (`app/`), from v1 pre-launch onward
**Reads with:** `desks/quality/TEST-STRATEGY.md` (test levels, coverage, verification approach) and the release verdicts in `desks/quality/releases/`
**Last updated:** 2026-10-21 · **Pre-v1; no release has shipped yet.**
**Status:** `v1.0` draft — this policy is declared **unambiguous and executable end-to-end** by an independent agent. It contains every command, every pass criterion, and every decision rule a reviewer needs; it contains no open question that would require asking someone before acting.

---

## 0. How to use this document (executing-agent walkthrough)

When a release is proposed, an agent executes the following sequence **in order**. Stop and **BLOCK** the release at the first item that is not satisfied; do not skip ahead, do not proceed "soon", and do not let a peer's assurance substitute for a green result.

1. **Check the PR is merged to `main`** and the CI ledger is current. (G-1)
2. **Run the CI fast path** and confirm it exits zero. (G-2)
3. **Run the sandbox / external-data pack** and confirm it exits zero. (G-3)
4. **Run the E2E suite with `SANDBOX=1`** and confirm it exits zero. (G-4)
5. **Spot-check the external-data health** (no live provider calls in CI; contract + fixture drift is zero). (G-5)
6. **Verify the release-readiness checklist items G-6 … G-15** pass, each with its cited evidence file. (G-6…G-15)
7. **Verify the sign-off block**: the two keys (Sentinel's gate verdict + Eric's explicit approval) are recorded in writing. (G-16)
8. **Record the verdict** in `desks/quality/releases/<date>-<release-id>.md` with blast radius and rollback. (G-17)

Items G-2 through G-4 are CI gates and may be treated as "done" only when their **exact** exit code is `0`, never by a human "it looks green" eyeball. Items G-5 through G-16 are the production gate and are the responsibility of the agent performing the review.

---

## 1. The acceptance bar for a v1 release

A v1 release is **accepted** only when **all** of the following are true. A single failure → the release is **rejected**, no exceptions, no "it's probably fine".

| # | Bar | How it is verified | Note |
|---|---|---|---|
| B-1 | Fast-path suite green on `main` | `pytest -q --cov=app tests/unit tests/contracts tests/integration` exits `0` | CI gate |
| B-2 | Sandbox external-data pack green | `pytest -q tests/sandbox` exits `0` | CI gate; also B-1 |
| B-3 | E2E suite green (SANDBOX=1) | `PLAYWRIGHT_BROWSER=chromium SANDBOX=1 pytest -q tests/e2e` exits `0` | CI gate; also B-1 |
| B-4 | Recommendation engine locked by golden matrix **and** invariants | golden-matrix fixture + invariants test both pass in the fast path | Must have been passed in CI on the merged change |
| B-5 | No open high/critical defect | Defect ledger in the kanban board shows no `open` item at **High** or **Critical** severity that was introduced by this release | See §7 for the honest-coverage-gap list |
| B-6 | Accessibility audit passed | Lighthouse + keyboard-nav focus check both green (see G-10) | a11y is a v1 gate, not best-effort |
| B-7 | Latency within SLA | Top result renders within the documented target (≤ 2.0 s p95 on a sandbox-cloned dataset; see G-11) | Measured, not claimed |
| B-8 | External-data health check green | Zero contract violations and zero schema violations on the *current* dataset (see G-5) | External data is a first-class dependency |
| B-9 | Rollback plan present and one-step | Every pipeline/feature change ships a rollback that takes < 5 min to execute and is documented (see G-12) | Rollback feasibility is checked at the gate, not after |
| B-10 | Documentation current | `README` runbook, release notes, and the defect ledger are all consistent with what shipped | A release whose docs lie is a blocked release |

**The acceptance bar is a conjunction:** B-1 ∧ B-2 ∧ B-3 ∧ B-4 ∧ B-5 ∧ B-6 ∧ B-7 ∧ B-8 ∧ B-9 ∧ B-10. All ten, every time. None may be substituted, deferred, or waived by a stakeholder without a written record.

---

## 2. What the CI gate runs, and the exact conditions for passing

The CI gate has **three suites** that run on every PR. They are independent; **a PR is "CI-green" only when all three exit zero**.

### CI fast path (runs on every commit)
```bash
pytest -q --cov=app tests/unit tests/contracts tests/integration
```
**Pass condition:** exit code `0`, with coverage satisfying the documented **minimum 80% line/total** (secondary to correctness — a failing test beats a coverage miss, but the target is enforced as a hard minimum since v1).

**Exactly what this covers** (see `TEST-STRATEGY.md` §2 for the definition of each level):
- **Unit** (`tests/unit/`): scoring math, filter predicates (exhaustive boundary tables), normalization, ranking/tie-breaking, recommendation invariants, golden-matrix equality.
- **Contract** (`tests/contracts/`): JSON-schema drift detection for weather/events/places; behavioural rules (recency policy, fallback rules, stale handling). Contract violations are **blocking**, not warnings.
- **Integration** (`tests/integration/`): repository↔DB layer, query composition, caching, dedup, rate-limit token bucket. Runs against a real testcontainer (SQLite/Postgres), no network.

### Sandbox pack (runs on every commit + on any external-data code change)
```bash
pytest -q tests/sandbox
```
**Pass condition:** exit code `0`. This is **mandatory and non-optional**: it is the only thing that proves the product behaves correctly when the network is unreliable. A release whose sandbox pack is failing is **automatically not releasable** regardless of the rest.

It covers the regression pack defined in `TEST-STRATEGY.md` §2.3: `429_rate_limited`, `5xx_server_error`, `timeout`, `empty_payload`, `missing_required_field`, `stale_data_warn`, `partial_field`, `geo_out_of_range`, `api_version_mismatch`.

### E2E (gate-on-PR only; must pass before the production gate)
```bash
playwright install --with-deps chromium
PLAYWRIGHT_BROWSER=chromium SANDBOX=1 pytest -q tests/e2e
```
**Pass condition:** exit code `0`. e2E **always runs under `SANDBOX=1` — never against live external providers in CI.** The four journeys covered: onboarding, ranked-results self-check, detail page with backup-indoor fallback, and empty-state.

### Flaky-test handling (the unambiguous rule)
- Flaky suites are quarantined: a test that fails once is retried **once**. A second failure (or a failure after retry) takes the test out of quarantine and **blocks the gate**.
- A green build is only green if every test ran to completion without failure. "It passed three of the four times" is not green and never unblocks a gate.
- Flaky tests that cannot be made deterministic get a `@flaky(max_runs=2)` annotation **with a tracking issue**. Until the tracking issue exists, the annotation is a violation of this policy.

---

## 3. The production gate: exact release-readiness checklist

The production gate is **separate from the CI gate**. CI proves the code is correct on the machine it is merged to; the production gate proves the **release** is safe to ship. This checklist is written so an independent agent can execute it **without asking a single question**. Every item has a unique ID, an exact action, an exact pass criterion, and the location of the evidence it produces.

> **Execution convention:** run the whole checklist in order from G-1 to G-17. For each item, record the result (`PASS`/`FAIL`/`NOT-EXECUTED`) and the evidence file in the designated places below. Stop and BLOCK at the first **FAIL**. Do not re-order, do not substitute, do not skip.

### G-1 — Merge & CI ledger check
- **Action:** Confirm the PR is merged to `main` and the CI ledger (the merged-CI-summary artifact) for that merge shows all three suites green. Read the artifact, do not rely on a teammate's word.
- **Pass criterion:** `main` is N commits ahead of the release branch; the CI ledger shows CI fast path `0`, sandbox `0`, e2E `0` for that merge.
- **Evidence:** `ci/ledger/<commit-sha>.json` (or the CI summary page URL, recorded verbatim).
- **Completed by:** executing agent.

### G-2 — Sandbox external-data pack
- **Action:** Run `pytest -q tests/sandbox` in a fresh venv with the pinned Python 3.14 toolchain. Capture stdout+stderr to a file.
- **Pass criterion:** exit code `0`, and the full listed scenario set (`429_rate_limited`, `5xx_server_error`, `timeout`, `empty_payload`, `missing_required_field`, `stale_data_warn`, `partial_field`, `geo_out_of_range`, `api_version_mismatch`) is present and passing in the output.
- **Evidence:** `qa/sandbox-rerun.log` + a `green-scenarios.txt` listing the 9 scenario names.
- **Completed by:** executing agent.

### G-3 — Contract + fixture drift check
- **Action:** Run the contract suite against the *current* dataset: `pytest -q tests/contracts`. Additionally run a fixture-consistency check that every contract's fixture matches the schema and that no fixture in `test/fixtures/` is older than the contract version it belongs to.
- **Pass criterion:** exit code `0`; zero schema violations; zero "fixture older than contract" warnings.
- **Evidence:** `qa/contract-drift.log` + `fixture-consistency-report.txt`.
- **Completed by:** executing agent.

### G-4 — E2E suite (SANDBOX=1)
- **Action:** Run `PLAYWRIGHT_BROWSER=chromium SANDBOX=1 pytest -q tests/e2e`. Capture output.
- **Pass criterion:** exit code `0`; all four journeys (onboarding, ranked-results self-check, detail-page fallback, empty-state) exercised and passing.
- **Evidence:** `qa/e2e-rerun.log`.
- **Completed by:** executing agent.

### G-5 — External-data health check (no-live-network)
- **Action:** Confirm the live-client code path is **not** exercised by any CI suite. Verify `SANDBOX=1` / fixture-first configuration by grepping the test runner configuration and conftest for `SANDBOX` usage, and confirm `fetch_live_data.py` is the only live-network entry point and is excluded from test runs.
- **Pass criterion:** no test suite, under any environment variable it is ever executed with, makes a live HTTP request to a weather/events/places provider.
- **Evidence:** `qa/sandbox-conftest-check.txt` (the grep snippet showing `SANDBOX` in the test bootstrap).
- **Completed by:** executing agent.

### G-6 — Recommendation engine locked
- **Action:** Confirm the merged `main` contains a golden-matrix fixture (`test/golden_matrix/`) and an invariants test (`tests/unit/test_recommendation_invariants.py`), and that both were passing in CI on the merged commit (see G-1 evidence).
- **Pass criterion:** the invariant suite exits `0` on the merged commit; the golden-matrix equality test exits `0`.
- **Evidence:** CI ledger line for the merged commit referencing the golden matrix + invariants.
- **Completed by:** executing agent.

### G-7 — Defect ledger review
- **Action:** Open the defect ledger (the kanban board defect records for this release). For every High/Critical item, confirm: (a) there is a fix PR merged, or (b) there is a tracked, accepted reason it is deferred, or (c) it is closed as a duplicate/invalid.
- **Pass criterion:** no open High or Critical item whose fix is not merged and not explicitly deferred with a dated, accepted reason.
- **Evidence:** the defect ledger, filtered to High/Critical, with status + owner + due date recorded in the verdict file.
- **Completed by:** executing agent.

### G-8 — Accessibility audit
- **Action:** Run Lighthouse (headless, CI environment) on every page of the app, and a keyboard-navigation focus check on the top result page. Record pass/fail per page and the numeric scores.
- **Pass criterion:** every page scores **≥ 90** on Lighthouse Performance, Accessibility, and Best Practices, and the keyboard focus check finds **no** focus trap or unreachable interactive element.
- **Evidence:** `qa/lighthouse-audit.html` (report) + `qa/keyboard-focus-check.txt`.
- **Completed by:** executing agent.

### G-9 — Latency / load spot check
- **Action:** Run a load test against a **sandbox-cloned** dataset (recorded latencies, no live provider) with `k6` (or vegeta) at the projected v1 concurrency, measure the p95 render latency of the top result, and verify it is within the SLA (≤ 2.0 s p95).
- **Pass criterion:** p95 top-result latency ≤ 2.0 s on a sandbox-cloned dataset at projected v1 concurrency; no error-rate spike (> 1%) under load.
- **Evidence:** `qa/load-test-report.json` (k6/vegeta report).
- **Completed by:** executing agent.

### G-10 — Rollback feasibility check
- **Action:** For every data-pipeline / scoring / schema migration change in this release, confirm a rollback exists that is: (a) a **one-step** decision (revert the commit, or pin the old data version), (b) executable in < 5 minutes, (c) documented with the exact commands in the release notes, and (d) approved by the executing agent before the gate closes.
- **Pass criterion:** every such change ships a documented one-step rollback; at least one rollback path is actually executed (dry-run against a scratch copy) and verified.
- **Evidence:** `qa/rollback-plan.md` + one executed dry-run log.
- **Completed by:** executing agent.

### G-11 — Data-quality / recency check
- **Action:** Inject the current external dataset into the sandbox, and verify the "last verified" / stale-marker behaviour works: a data point older than the recency policy (weather 24h, events 7d, places 30d) is flagged stale and shown with a marker, never dropped silently; a fully missing source degrades gracefully (falls back to the non-dependent features).
- **Pass criterion:** stale markers render correctly; a missing source never drops features that don't depend on it; no crash on a fully missing source.
- **Evidence:** `qa/data-quality-check.log`.
- **Completed by:** executing agent.

### G-12 — Release notes & runbook currency
- **Action:** Confirm the release notes document what shipped, the schema/data-version changes (if any), and the rollback steps. Confirm the runbook (`README` / `docs/runbook`) reflects the shipped configuration.
- **Pass criterion:** release notes are accurate (no unreachable claims about features), runbook is current, and both are consistent with the checklist outcomes.
- **Evidence:** updated `docs/release-notes.md` + `README`/runbook diff, reviewed verbatim by the executing agent.
- **Completed by:** executing agent.

### G-13 — Coverage-gap manifest check
- **Action:** Compare this release's risk profile against the coverage-gap manifest in `TEST-STRATEGY.md` §6. Any gap that is **directly hit by this release** must be either closed (a test exists now) or explicitly carried forward with a dated owner and a named closing action.
- **Pass criterion:** no unresolved gap is in the release blast radius without a carry-forward record.
- **Evidence:** a one-line carry-forward table in the verdict file.
- **Completed by:** executing agent.

### G-14 — Exploratory charter log review
- **Action:** Confirm the exploratory charter log (`docs/tests/LOG.md`) covers the v1 charters (weather-gating feel, urgency handling, fallback UX, speed, a11y) and that the log is current and signed off by the QA reviewer.
- **Pass criterion:** all five v1 charters present, log is dated, and the QA reviewer has signed off the results.
- **Evidence:** `docs/tests/LOG.md` (dated, signed off).
- **Completed by:** executing agent.

### G-15 — Security & dependency sanity check
- **Action:** Run a dependency audit (`pip audit` / `safety` equivalent) on the pinned toolchain and confirm no known-high/novel critical vulnerabilities; confirm no secrets are committed (grep for `API_KEY`, `TOKEN`, `PASSWORD` in the diff).
- **Pass criterion:** no High/Critical open vulnerabilities in the pinned toolchain; zero secrets committed in this release.
- **Evidence:** `qa/dependency-audit.txt` + `qa/secrets-scan.txt`.
- **Completed by:** executing agent.

### G-16 — Sign-off (the two keys)
- **Action:** Record, in writing, the **Sentinel gate verdict** and **Eric's explicit approval**. This is the production gate and no other single approval substitutes.
- **Pass criterion:** both of these are recorded in the verdict file as `APPROVED` with a timestamp and the approver's name:
  1. **Sentinel's gate verdict** (this reviewer): `APPROVE` / `BLOCK`.
  2. **Eric's explicit approval** (founder/owner), in writing.
- **Evidence:** the verdict file contains both approvals with timestamps; the deployment trigger will not be deployed without both.
- **Completed by:** Sentinel (gate verdict) + Eric (explicit approval).

### G-17 — Verdict file recorded
- **Action:** Write the release verdict to `desks/quality/releases/<YYYY-MM-DD>-<release-id>.md`.
- **Pass criterion:** the verdict file contains: the verdict (`APPROVE` or `BLOCK`), the itemised checklist results with evidence references, the blast radius, the rollback plan reference, and the two sign-offs (G-16) with timestamps.
- **Evidence:** the verdict file itself.
- **Completed by:** executing agent.

---

## 4. How flaky or missing external data affects the gate decision

This is the highest-risk section of the policy: the product is an **external-data product**, so the data source is a first-class dependency, not a nice-to-have. The rules below are explicit; there is no "best effort".

### 4.1 Definitions
- **Source healthy:** the source's contract suite passes, its last verified data is within recency policy and not flagged stale in the cache, and no schema violations are reported.
- **Source degraded:** the source is reachable and returning data, but one or more of: data is stale, a schema violation is present, or the response is slow (outside the configured timeout). **Degraded-mode tests must be green** (the product must still return useful output with a marker, never a 500 and never an empty list).
- **Source failed:** the source is unreachable, rate-limited past recovery, or returning schema-violating data. Circuit breaker trips; the product surfaces "we couldn't fetch X for this area" instead of a 500, and the degraded-mode tests are what prove this.

### 4.2 Gate decision rules
- **Blocked** if any **hard** test fails: fast path, sandbox pack, E2E, contract/fixture suite, golden matrix, or invariant suite. These are CI-gate failures and are never waived.
- **Blocked** if the combined dataset (which you can verify with G-5) contains a **contract or schema violation** — this is data-contract breakage and is a release blocker.
- **Blocked** if the external source is **failed** at release time **and** the degraded-mode tests are **not** green. A failed source with green degraded-mode tests **does not block a release** — it lands the product in degraded mode, which the UI must surface honestly. This is a release decision, not a "continue without testing it" decision.
- **Blocked** if a source is failed **and** the release includes anything that depends on that source (i.e. a change to the weather gate or a weather-dependent feature path). A partial release of a dependent feature is not a release.
- **Not blocked** by a degraded source, provided the degraded-mode tests are green **and** the UI displays the degradation to the user (stale marker / "we couldn't fetch X" banner). Degraded → release is approvable; the degradation is a user-visible portion of the release notes.
- **Never** treat "the network is down in my local sandbox" as green. The sandbox pack is deterministic by design; a test that fails only because the network is down indicates a broken test, not a broken product.

### 4.3 Decision table (concise reference)
| Data state | Degraded-mode tests | Gate decision |
|---|---|---|
| Healthy | — | APPROVE |
| Degraded (stale / slow / schema violation) | green | APPROVE; degradation documented in release notes |
| Failed (unreachable / 429 / schema-violating) | **not** green | **BLOCK** |
| Failed (unreachable / 429 / schema-violating) | green | APPROVE (degraded mode; user-facing banner required) |
| Failed **and** release depends on that source's feature path | green | **BLOCK** (dependent feature not released) |
| CI suite flaky (not data) | n/a | Quarantine, retry once; second failure → **BLOCK** |

---

## 5. Risk-proportionate review criteria tied to blast radius

Review depth is a function of **blast radius**, not of how many files changed. Every change publishes a one-line "blast radius" in its PR description. The table is authoritative; no override is permitted without Sentinel's written override.

| Change type | Example | Blast radius | Required review rigor | Required artifacts |
|---|---|---|---|---|
| **Copy** | text on buttons, headings, placeholders, FAQ, email | Display text only; one user reads it per session | Low | PR description + spell/typo pass; **no** test-suite rerun |
| **UI skin** | colours, layout, component size, fonts | Header/hero across pages; navigation | Medium | PR description + e2E smoke of the affected page |
| **Feature** | new filter, new source enum, onboarding step | All users on that path | Medium-High | PR description + unit + contract + e2E |
| **Scoring / weights** | weight change, new signal, tie-break rule | Recommendation output for **every** user, **every** session | **High** | PR description + golden matrix + invariants test + e2E |
| **Data pipeline** | new field in activity record, new source, schema migration, taxonomy rename | **Every** user's results, all time | **Highest** | PR description + contract + golden matrix + data-quality check + rollback plan |
| **Schema migration** | DB column/table rename, enum extension | Read/write integrity of all persisted state | **Highest** | PR description + migration reversibility proof + integration + e2E |

### 5.1 Blast-radius rules (written out)
1. **Copy ≠ feature.** A change that alters the *meaning* of a filter label (e.g. "people" becomes "capacity") is a **feature** change, not copy, regardless of how few lines of text changed. The assignee must self-identify correctly.
2. **Scoring/weights ⇒ data pipeline.** A scoring or weight change affects every result every user sees; it is reviewed with the same rigor as a data-pipeline change (golden matrix + invariants + e2E required).
3. **A data-pipeline change is not releasable** if it changes what data is required for the recommendation without updating the contract **and** the fixtures in the **same PR**. This is a hard blocker; it is not waivable.
4. **Rollback feasibility is checked at the gate, not after.** If the rollback cannot be executed in under 5 minutes and documented with a one-step command, the change is not releasable until a rollback is added. This is the single most common gate failure — the gate enforces it.
5. **External data is a first-class dependency.** A provider outage is treated like a build failure until the degraded-mode test is green. There is no "the vendor is having an issue" that bypasses the gate.

---

## 6. Honest coverage gaps — what we CANNOT verify yet (v1)

This is a commitment to the team: these are things we will not claim done until they are addressed. A gap is **closed** only when the corresponding test exists and is green. Nothing below may be documented as "done" while it is listed here.

| # | Gap | Why it can't be verified yet | What closes it |
|---|---|---|---|
| 1 | **Real-user preference** | "Good" ranking is a business judgement; golden matrices encode our hypothesis, not validated preference. | First user study / preference survey with real users on live data. |
| 2 | **Multi-provider cross-validation** | Two weather/event providers are not yet reconciled, so agreement/disagreement is untested. | Reconciliation policy; cross-provider shard test. |
| 3 | **Cost accuracy** | Cost tier is user-reported/inferred; nothing auto-verifies "free/cheap/splurge" against a price list. | Cost-validation pipeline + price feeds, or explicit UI marking of cost as unverified. |
| 4 | **Real booking/availability** | "Open now" is derived from hours, not a live booking-availability system. | Availability-feed integration + availability-specialist test. |
| 5 | **Geographic surface** | Place/weather quality for Ottawa–Gatineau unverified; coverage unknown. | Geo-coverage QA pass against curated fixtures for the first city. |
| 6 | **Load / latency under load** | No soak or load test; rec latency ceiling unmeasured. | Load test (k6/vegeta) against a sandbox-cloned dataset with recorded latencies. |
| 7 | **Capacity / number-of-people validation** | Field contract not agreed. | Agree the field contract; validation test + fixture; capacity-mismatch regression. |
| 8 | **Accessibility audit** | No automated a11y run executed. | Lighthouse + manual keyboard/screen-reader audit as a required pre-gate gate. |
| 9 | **Localization / i18n** | English-only in v1. | Out of v1; tracked as a follow-up. |
| 10 | **Total-failure end-to-end** | The combination of all-filters-failing, all-sources-stale, and missing-locations is not end-to-end exercised. | A dedicated "total-failure" e2E scenario recorded in `tests/e2e/`. |

---

## 7. Defect triage priorities

Defects are triaged into **Critical / High / Medium / Low** by impact on release acceptance, not by annoyance. The rules below decide the priority:

| Priority | Rule |
|---|---|
| **Critical** | Blocks acceptance bar B-1…B-10; any data-contract or schema violation; any source-failure path that returns 500 to a real user; any security vulnerability exploitable by a user. |
| **High** | Returned to a real user and materially changes the result (wrong ranking, missing result, misleading weather); UI that is unusable with the current data (no empty-state escape). |
| **Medium** | Visible defect that degrades quality but doesn't change the correctness of results; stale markers that don't render. |
| **Low** | Cosmetic; copy; performance within SLA; items in the coverage-gap list. |

---

## 8. Release verdict format (what the G-17 file must contain)

Every release verdict is written to `desks/quality/releases/<YYYY-MM-DD>-<release-id>.md` and must contain, verbatim:

1. **Verdict:** `APPROVE` or `BLOCK`, and the single sentence that decided it.
2. **Checklist results:** table of G-1 … G-17, each with `PASS`/`FAIL`/`NOT-EXECUTED` and the evidence path.
3. **Blast radius:** one line naming the widest blast radius touched by this release.
4. **Rollback:** reference to `G-10`'s `qa/rollback-plan.md`.
5. **Sign-offs:** Sentinel gate verdict + Eric's explicit approval, each with a timestamp and name.
6. **Coverage-gap carry-forwards:** any gap from §6 that is in the release blast radius, with a dated owner and closing action.

**Artifact location:** `desks/quality/releases/<date>-<release-id>.md`.

---

## 9. Current status and next actions

- **Door open:** the gate policy (`this file`) and the test strategy (`TEST-STRATEGY.md`) are written and reviewed.
- **Door open:** a v1 acceptance bar exists but **no release has shipped**; every item in §1 is untested until the first release.
- **Next action on the team:** Forge merges a candidate v1, Sentinel runs G-1 … G-17, and both keys are recorded. A release ships only when the verdict is `APPROVE` and both keys are recorded.

**Owner:** Sentinel (Head of Quality & Release).
**Last updated:** 2026-10-21 · **Pre-v1; no release shipped.**

---

## 10. Security & compliance — release-readiness checklist additions (S-x)

**Owner:** Sentinel (Head of Quality & Release). These items are added to the production
gate checklist as a **security & compliance** section. S-1…S-6 are mandatory for **any**
auth or money change; S-7…S-14 are mandatory before the **first** account/money feature ships.
Full rule text lives in `desks/quality/SECURITY-REVIEW-SCOPE.md` (§2–§4). Evidence files are
recorded in the verdict file for the gate run.

| ID | Checklist item (added) | Evidence |
|---|---|---|
| S-1 | Auth endpoint rate limits configured and passing (login, OTP resend, sign-up). | unit + sandbox test + code review |
| S-2 | Session cookie flags audited in browser: `HttpOnly`, `Secure`, `SameSite`. | browser check |
| S-3 | Security headers present: CSP, HSTS, X-Frame-Options, Referrer-Policy (`no-referrer` on link-bearing pages). | `qa/headers-audit.txt` |
| S-4 | Secrets scan: zero secrets committed in this release. | `qa/secrets-scan.txt` |
| S-5 | Dependency audit: no High/Critical open vulnerabilities in the pinned toolchain. | `qa/dependency-audit.txt` |
| S-6 | PCI statement confirmed: no PAN in our systems (PCI-SAQ-A scope, delegated provider). | code review + static scan |
| S-7 | Guest plan URL: entropy ≥ 128-bit, 30-day absolute expiry, server-side revocation, `no-referrer`, no logging — all pass. | unit + sandbox + browser |
| S-8 | OAuth: PKCE + `state` verification + exact redirect-URI allowlist pass. | unit + sandbox |
| S-9 | Account enumeration test passes (identical confirmation emails, generic errors). | unit |
| S-10 | Webhook signature validation + idempotency tested. | sandbox + e2E |
| S-11 | Financial audit log append-only verified (receipts + ledger). | unit + code review |
| S-12 | Reversibility confirmed: session revoke, guest-link revoke, refunds/voids. | test + code review |
| S-13 | PIPEDA data-residency decision recorded (Clerk or self-hosted) + consent approach. | written decision (§7 D-1) |
| S-14 | Staged rollout enabled (feature flag + canary) for auth/money changes. | deployment config |

> **Execution convention:** run S-1…S-14 in order from a gate run. For each item record the
> result (`PASS`/`FAIL`/`NOT-EXECUTED`) and the evidence file. Stop and **BLOCK** the release at
> the first **FAIL**. Do not re-order, do not substitute, do not skip. S-1…S-6 are part of the
> G-x gate; S-7…S-14 gate the first account/money feature.

---

## 11. Current status and next actions
