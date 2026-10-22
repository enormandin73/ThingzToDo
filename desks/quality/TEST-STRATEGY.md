# TEST-STRATEGY.md — Test Levels, Coverage, and Verification Approach

**Owner:** Sentinel (Head of Quality & Release) · **Status:** v1.0 (draft, pre-product)
**Reads together with:** `desks/quality/STATUS.md` (production gate & release checklist)
**Applies to:** all of `app/` (product repo; owned by Forge; created after this file)

---

## 1. How to read this file

Every section below states (a) what is being tested, (b) the test level that covers it, and
(c) the concrete artifact/test to run. A change is "verified" only when it has a green test
on the level that covers it — never because a peer says it works.

## 2. Test levels

| Level | Where | What it covers | Tooling | CI runs |
|---|---|---|---|---|
| **Unit** | `tests/unit/` | Pure functions & single-module logic. No I/O, no network, no DB. | `pytest` (+ `pytest-cov`, Python 3.14) | **every commit** (fast path) |
| **Contract** | `tests/contracts/` + `test/fixtures/` | External data-source schemas and behavioural contracts (weather/events/places); JSON-schema drift detection. | `pytest` + JSON Schema validation; consumer-driven contracts (Pact or equivalent) | **every commit** (fast path) |
| **Sandbox** | `sandbox/` + `test/fixtures/` | Normalised external-data scenarios: rate-limit, timeout, partial/missing fields, stale data. Runs under the `--sandbox` client, never the real HTTP client. | `pytest` (client-in-the-loop, fixtures injected) | every commit + on any external-data code change |
| **Integration** | `tests/integration/` | Repository/DB layer, query composition, caching, dedup, rate-limit token-bucket logic. Real DB (test container), no network. | `pytest` + testcontainers | **every commit** (fast path) |
| **E2E** | `tests/e2e/` | Full user journeys across the rendered app. Local dev server + real DB + sandboxed (never live) external clients. | Playwright (headless Chromium) | **PR only**, and **blocked** on main-deploy; must pass before gate |
| **Exploratory** | `docs/tests/` | Charter-based manual testing; run before each release gate. | Human-led; log results in `docs/tests/LOG.md` | before each gate |

### 2.1 Unit tests (`tests/unit/`)
- **What:** pure functions, transformers, and single-module helpers. No network, no DB, no file
  system. Rules out nothing real; it locks in deterministic behaviour.
- **What the unit suite must contain (the v1 contract):**
  1. **Scoring math** — weighted linear score for a candidate activity, including zero/blank
     weights, negative inputs (asserted to be clamped, not propagated), and float rounding to
     a documented precision.
  2. **Filter predicates** — `weather_compatible`, `cost_within_budget`, `capacity_matches`,
     `open_at_time`, `distance_within`. Each exercised with an exhaustive boundary table.
  3. **Normalization** — weather → comfort-band mapping, cost tier mapping, time-of-day
     classification.
  4. **Ranking / tie-breaking** — tie-breaks are documented, deterministic, and tested (a
     "sort is stable and reproducible" test is a must).
- **CI fast-path command:**
  ```bash
  pytest -q --cov=app tests/unit
  ```
  Exit non-zero on any failure; coverage target is a **minimum of 80% line/total** but is
  secondary to correctness — a failing test trumps a coverage gating.

### 2.2 Contract tests (`tests/contracts/`) + fixtures (`test/fixtures/`)
Contract tests lock the *shape* and *behaviour* of the external data we depend on. Each
external source has its own contract file:

```
test/contracts/
  weather/      # e.g. Open-Meteo, AccuWeather, …
  events/       # e.g. Eventbrite, local API, …
  places/       # e.g. Google Places, Foursquare, …
  common/       # shared envelope fields (id, name, lat, lon, category)
```

Each contract file declares:
1. **Required fields** we consume, with JSON Schema type + `required: true`.
2. **Optional enrichment fields** (decayed if we cannot consume them).
3. **Allowed enums** (e.g. `cost_tier: [free, cheap, splurge]`), `category` vocabulary.
4. **A behavioural rule** (not just schema) — e.g. "a `next_run_at` in the past must be
   treated as `now`", or "a `rain` probability ≥ 0.6 must force outdoor → indoor fallback".
5. **A fixture** (`test/fixtures/<source>/<case>.json`) that is *independent* of the live
   provider — the same fixture is used by unit, sandbox, and e2E tests, so "works in e2E"
   implies "works in unit".

**Drift detection.** On every CI run the contract suite validates each current fixture
against the contract. If the provider changes a field name/type/enum, the contract (and a
fixture) must be updated **in the same PR**. A fixture that fails schema validation is a
blocking failure, not a warning.

### 2.3 Sandbox / stub modes (`sandbox/`)
The real HTTP client is only ever one candidate; a **sandbox client** (`sandbox/client.py`)
replaces the network with a fixture loader. Any test can switch a module from real→sandbox
by injecting a client that reads from `test/fixtures/` plus a scenario tag. Enablers:

- `SANDBOX=1` env var, or `--sandbox` CLI flag, or a `sandbox=True` constructor kwarg.
- Fixtures are namespaced per scenario so one source can serve many lab cases.

**Scenarios the sandbox suite must cover** (the "flaky/missing/external-misbehaviour"
regression pack):
| Scenario | What it proves |
|---|---|
| `429_rate_limited` | Client honors retry-after, does not retry indefinitely, backs off per policy |
| `5xx_server_error` | Client does not poison cache / does not return partial data on retry |
| `timeout` | Request that hangs is aborted; fall back to cached/derived data, not to silence |
| `empty_payload` | A valid envelope with zero results is handled (not `null`, not an exception) |
| `missing_required_field` | A required field absent → contract violation, surfaced as a failed test + metric, not swallowed |
| `stale_data_warn` | Data older than a threshold triggers a "last verified" marker and a UI warning, without dropping the row |
| `partial_field` | One enrichment field missing while required fields are present → still usable, flagged optional |
| `geo_out_of_range` | Coordinates beyond territory of the source → no crash, no false hit |
| `api_version_mismatch` | Contract version bump rejected until provider version is bumped |

The sandbox suite is **not optional**: it is the only thing that proves the product behaves
correctly when the network is unreliable, which is the normal state for an external-data
product. A release whose sandbox suite is failing is automatically "not releasable" regardless
of the rest of the suite.

### 2.4 Integration tests (`tests/integration/`)
- **What:** repository↔database, query composition, caching, dedup, rate-limit token bucket,
  and the plumbing that moves external data into the local store. No network.
- **Run:** testcontainers (real SQLite/Postgres) so SQL and indexing decisions are real.
- **CI:** fast path.

### 2.5 E2E tests (`tests/e2e/`)
- **What:** critical user journeys rendered in a real browser:
  1. **Onboarding** (locate → weather → cost → people → time) → results page renders.
  2. **Ranked results** — results are sorted and deduplicated, and the top result is a valid
     candidate under the supplied filters (self-check, not eyeball).
  3. **Detail page** — weather/cost/people/time all reflected; a "backup indoor" fallback is
     shown when the top outdoor result fails the weather gate.
  4. **Empty-state** — when no activity passes all filters, a helpful zero-result state is
     shown with a "relax filters" control. Locked in unit sandbox, exercised here.
- **Sandbox rule:** e2E always runs with `SANDBOX=1`; no live external network in CI e2E.
- **CI:** gate-on-PR only, must pass before the production gate. Command:
  ```bash
  playwright install --with-deps chromium
  pytest -q tests/e2e
  ```

### 2.6 Exploratory testing
Charter-based, manual, and documented in `docs/tests/LOG.md`. Run before every release gate,
led by Sentinel (or a QA engineer on the team). Charters are fixed and versioned so the same
release is re-tested the same way.

Charter templates (v1):
- **Weather-gating feel:** when rain rises, does the product visibly pivot toward indoor
  alternatives, or just show "no results"?
- **Urgency handling:** "tonight"/"this weekend" filters return what we claim they return.
- **Fallback UX:** zero-result state is legible and gives an escape hatch.
- **Speed:** the top result appears within the SLA (defined in STATUS.md); nothing blocks on a
  spinner longer than N seconds.
- **Accessibility:** a11y audit pass (Lighthouse + keyboard-nav focus check).

## 3. External data sources (weather / events / places)

This is the highest-risk area of the product, because the recommendation engine is only as
good as the data feeding it, and that data is controlled by third parties.

### 3.1 Data contracts (one per source)
Every source that feeds a recommendation is described by a data contract (see §2.2). The
contract is the source of truth for "what does the product require from this source". It lives
in `test/contracts/<source>/` alongside a matching fixture. Nothing else is allowed to peek
at the raw provider fields directly — all consumption goes through a thin client that maps
provider fields → our canonical fields, and that client is what the contract tests validate.

### 3.2 How we treat external data
1. **Fixture-first.** Tests never call the real provider. They consume fixtures, so tests are
   deterministic and cheap. A fixture collision is a bug, not a flake.
2. **Sandbox default.** Every consumer defaults to sandbox mode; the real client is opted-in
   and isolated (used only by a small `fetch_live_data.py` script for manual refresh — never
   from test code).
3. **Versioning.** A provider contract has a version. Bumping the provider version requires a
   contract bump **and** a fixture bump in the same PR. Old versions are retained in
   `test/fixtures/archive/` for a rolling 3 releases so time-travel tests (replaying last
   week's data) stay possible.
4. **Observability.** Every client reports: `fetched`, `fetched_ms`, `cached`, `stale`,
   `schema_violation`, `rate_limited`. These are metrics, not logs-only. When a source violates
   its contract, the product should still return useful output rather than fail-closed.
5. **Recency policy.** A data point older than the recency policy (default: 24 h for weather,
   7 d for events, 30 d for places) is flagged stale in the cache and shown with a "last
   verified" marker — never dropped silently. The rec engine treats stale as a *soft* constraint.

### 3.3 Rate-limit / missing-data scenarios
Covered fully by the sandbox suite in §2.3. In addition:
- **Circuit breaker:** if a source fails N times in a window, trip the circuit for a cool-down
  and surface "we couldn't fetch X for this area" instead of a 500.
- **Degraded mode:** a failed source never removes features that depend on it (e.g. missing
  event data still shows weather + places recommendations).
- **No silent fallback:** if weather data is entirely missing, the product shows "weather
  unavailable, show weather-independent activities" rather than rendering an empty list.

## 4. The recommendation engine — hardest thing to verify

The rec engine is the product. It turns (weather, cost, people, time, geography) into a ranked
list of activities. It is hard to verify because the "correct" answer is a business judgement,
not a single truth. So we verify it **three independent ways** and require all three:

### 4.1 Rule tests (predicate coverage)
Every recommendation is a conjunction of filters plus a scoring function. Each filter is a
pure predicate tested with an exhaustive boundary table (§2.1 item 2). The scoring function
itself is a pure function with hand-computed golden outputs (§4.3). This is the bulk of unit
coverage.

### 4.2 The golden matrix (the decisive test)
Before any rec-engine change is merged, a **golden matrix** must be produced for a fixed,
curated dataset. Do it by hand on paper (or spreadsheet), compute the expected ranked output,
and store it as a canonical fixture + unit test (no hand-computed numbers in test code that
aren't derived from a stored matrix):

```
test/golden_matrix/<scenario>.json      # expected ranked output, hand-derived
tests/unit/test_recommendation_golden.py # asserts engine output == golden matrix
```

A golden matrix is **mandatory** for any change to the rec engine, any scoring weight change,
any new filter, or any new data source. Without it, a rec change is not mergeable.

### 4.3 Scoring behaviour invariants (always tested)
Regardless of the model, these invariants must hold and be tested:
- **Monotonicity:** increasing a relevant positive signal (e.g. a matching weather condition)
  never lowers an activity's rank.
- **Score bounds:** scores are clamped to `[0, 1]` and rounded to a documented precision.
- **Determinism:** same inputs → same ranked output. No true randomness; "seeded exploration"
  must be a fixed-seed PRNG with a reproducible seed vector.
- **Weight normalization:** weights sum to 1; blank weights are treated as 0.
- **Filter integrity:** an activity that fails any hard filter is never returned with a score.
- **Empty handling:** zero candidates → a structured `EmptyRecommendation` result, not an
  exception, so the UI can render a helpful state.

### 4.4 Time-travel / recency tests
Using archived fixtures, replay "last week's" data and assert the rec output is unchanged from
a stored output. This catches "we re-ranked today's results using tomorrow's weather" style
bugs.

### 4.5 Exploratory charter for the rec (§2.6)
If the golden matrix and invariants pass but the product still feels wrong, the exploratory
charter is where the judgement call happens — e.g. "the rec over-prioritizes cheap indoor
options and ignores user willingness-to-pay." Those observations are tracked as findings,
not silently fixed.

## 5. Risk-proportionate review rules

Review depth is a function of **blast radius**, not of how many files changed. All changes
publish a one-line "blast radius" in the PR description.

| Change type | Example | Blast radius | Review rigor | Required artifacts |
|---|---|---|---|---|
| **Copy** | text on buttons, headings, placeholder, FAQ, email | Display text only; one user reads it per session | Low | PR description + one-page spell/typo pass; no test-suite rerun |
| **UI skin** | colours, layout, component size, fonts | Header/hero across pages; navigation | Medium | PR description + e2E smoke of the affected page |
| **Feature** | new filter, new source enum, onboarding step | All users on that path | Medium-High | PR description + unit + contract + e2E |
| **Scoring/weights** | weight change, new signal, tie-break rule | Recommendation output for every user | High | PR description + golden matrix + invariants test + e2E |
| **Data pipeline** | new field in activity record, new source, schema migration, taxonomy rename | **Every user's results** | Highest | PR description + contract + golden matrix + data-quality check + rollback plan |
| **Schema migration** | DB column/table rename, enum extension | Read/write integrity of all persisted state | Highest | PR description + migration reversibility proof + integration + e2E |

### 5.1 Blast radius rules (written out)
- **Copy changes** do not require running the full suite. They do require a spell/typo pass
  and that UI smoke tests on the affected page still pass. They cannot change the meaning of
  a filter label (that is a feature change, not copy).
- **Scoring/weight changes** are treated as a **data pipeline change** — they affect every
  result every user sees. They require a golden matrix and all invariant tests.
- **A data-pipeline change is not releasable** if it changes what data is required for the
  recommendation without updating the contract **and** the fixtures in the same PR.
- **Rollback:** every pipeline change ships a one-step rollback decision (e.g. reverting the
  commit, or pinning the old data version). Rollback feasibility is checked at gate, not after.

## 6. Honest coverage gaps (what we CANNOT verify yet)

This list is a commitment to the team: these are things we will not claim done until they are
addressed. A gap is closed only when the corresponding test exists.

| # | Gap | Why it can't be verified today | What would close it |
|---|---|---|---|
| 1 | **Real-user preference** | We don't know whether a "good" ranking matches real taste; golden matrices encode our hypothesis, not validated preference. | First user study / preference survey with real users on live data. |
| 2 | **Multi-provider cross-validation** | We have not decided how to reconcile two weather/event providers, so agreement/disagreement is untested. | Choose a reconciliation policy; test it with a cross-provider shard. |
| 3 | **Cost accuracy** | Cost tier is currently user-reported / inferred; nothing auto-verifies "free/cheap/splurge" against a price list. | A cost-validation pipeline + real price feeds; or explicitly mark cost as unverified in the UI. |
| 4 | **Real booking/availability** | "Open now" is derived from hours, not from a live booking-availability system. | Availability-feed integration and an availability-specialist test. |
| 5 | **Geographic surface** | Place/weather quality for Ottawa-Gatineau is unverified; coverage and completeness unknown. | Geo-coverage QA pass against a curated fixture list for the first city. |
| 6 | **Load / latency under load** | No soak or load test yet; the rec pipeline's latency ceiling under concurrent users is unmeasured. | Load test (k6/vegeta) against a sandbox-cloned dataset with recorded latencies. |
| 7 | **Capacity/number-of-people validation** | Source and validation of the `capacity`/`people` field are not agreed. | Agree the field contract; add a validation test + fixture; then regression-test capacity mismatches. |
| 8 | **Accessibility audit** | No automated a11y run has been executed. | Lighthouse + manual keyboard/screen-reader audit as a required pre-gate gate. |
| 9 | **Localization / i18n** | English-only in v1; not in scope, but "translate this later" is unverified. | Out of v1; tracked as a follow-up. |
| 10 | **"Doesn't break when everything is wrong"** | The full-stack combination of all-filters-failing, all-sources-stale, and missing-locations has not been end-to-end exercised. | A dedicated "total-failure" e2E scenario recorded in `tests/e2e/`. |

## 7. Conventions for the team

- **File layout:** tests live next to what they test where possible, else in the `tests/`
  trees above; fixtures in `test/fixtures/`; golden matrices in `test/golden_matrix/`;
  sandbox adapters in `sandbox/`.
- **Naming:** `test_<unit>_<behavior>.py`; fixtures `<source_or_scenario>/<case>.json`;
  golden matrices `<scenario>.json` in `test/golden_matrix/`.
- **No private helpers in test code that duplicate logic being tested.** If a test helper
  contains business logic, it masks the bug.
- **A red test on the level that covers the change is a blocker for that PR.** "It works on
  my machine" is not a test result.
- **External data is a first-class dependency.** A provider outage is treated like a build
  failure until the degraded-mode test is green, not like a warning.

## 8. Quick-reference commands

```bash
# fast path (every commit)
pytest -q --cov=app tests/unit tests/contracts tests/integration

# sandbox scenario pack (always green before any external-data change)
pytest -q tests/unit tests/sandbox

# e2E (PR + gate only)
playwright install --with-deps chromium
pytest -q tests/e2e

# exploratory charter log (before every gate)
vim docs/tests/LOG.md
```
