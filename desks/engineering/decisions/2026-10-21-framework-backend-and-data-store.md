# Framework, Backend, and Data Store — ADR

**ADR:** `desks/engineering/decisions/2026-10-21-framework-backend-and-data-store.md`
**Owner:** Forge (Principal Software Architect)
**Date:** 2026-10-21
**Status:** Accepted
**Feeds:** the web-first product shell (web-first ADR), the recommendation API, the
catalog/data layer, and the ingest pipeline (ingestion-source ADR).

**Related ADRs:**
- `2026-10-21-web-first-vs-app-first-and-hosting-target.md` (web-first + Fly.io hosting; the
  container that carries this stack)
- `2026-10-21-activity-filtering-engine-constraints-matching.md` (engine + API consumer)
- `2026-10-21-activity-catalog-ingestion-source-strategy.md` (data source of truth)

---

## 0. Purpose & scope

This ADR fixes the three things that determine how we build and run the product:

1. **Frontend framework** — the UI the end user sees (web-first web app + PWA shell).
2. **Backend service** — the HTTP/JSON service that serves the UI and the recommendation
   API.
3. **Data store** — where the activity catalog, weather cache, and derived indexes live.

It also records **rejected alternatives** (with reasons) and a **clear escape hatch / migration
path** for every choice, so the stack can be re-pointed later without a rewrite.

This ADR assumes the decisions in the web-first ADRs are already in place: web-first product,
Fly.io single-container deployment, `repo/app/` as the product repo. It deliberately does not
redo those decisions.

---

## 1. Decision (TL;DR)

> **Frontend:** Next.js (App Router) on top of React — a server-rendered, shareable-URL web app
> with a PWA shell.
> **Backend:** Node.js 22 LTS serving Next.js server-rendered UI **and** the `/api/v1/recommend`
> route handler, backed by a framework-agnostic TS engine module.
> **Data store (MVP):** SQLite, one file, accessed through a thin node catalog adapter, migrated
> to managed Postgres later behind the same catalog interface.
> **Toolchain:** npm (package manager), Vitest (test runner), Docker (build artifact), Fly.io
> (deploy target). Weather from Open-Meteo (free, no key), materialized into the catalog at
> ingest so *query time* stays near-free.
> **Cost ceiling (MVP):** ~$0–$10/mo (container + SQLite + free weather) — covered by Fly.io's
> free allowance with no payment required.

---

## 2. The stack, concrete

```text
┌─────────────────────────────────────────────┐
│  Fly.io container (single Docker image)     │
│  ┌───────────────────────────────────────┐  │
│  │  Next.js (App Router)               │  │
│  │   ├── server-rendered UI (React)    │  │
│  │   ├── PWA: manifest + service worker│  │
│  │   └── /api/v1/recommend route       │  │
│  │        ├── normalize request         │  │
│  │        ├── catalog lookup            │  │
│  │        ├── weather (cache)           │  │
│  │        ├── engine (ADR §2)           │  │
│  │        └── RecommendationResult      │  │
│  │   ┌───────────────────────────────┐ │  │
│  │   │ node catalog adapter          │ │  │
│  │   │  - SQLite (file-based)        │ │  │
│  │   │  - weather cache table        │ │  │
│  │   └───────────────────────────────┘ │  │
│  │   ┌───────────────────────────────┐ │  │
│  │   │ engine module (pure TS)       │ │  │
│  │   │ (imported by the API route)   │ │  │
│  │   └───────────────────────────────┘ │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

| Layer | Choice | Role in the stack | Cost |
|---|---|---|---|
| Frontend | **Next.js (App Router) + React** | SSR of the ranked list, shared routing, client hydration of the PWA shell | npm |
| Backend runtime | **Node.js 22 LTS** | Runs the Next.js server + engine module; the engine is a pure TS module, no Node-specific logic | npm |
| Backend HTTP / app | **Next.js route handlers** (`/api/v1/recommend`, plus future `/api/v1/activity`, `/api/v1/share`) | Thin HTTP surface: validate → catalog → weather → engine → envelope. No second server to run or scale. | Bundled with Next.js |
| Test runner | **Vitest** | Unit/integration tests for the engine and API routes; TS-native, fast, Vite-powered (already in the Next.js toolchain) | npm |
| Data store | **SQLite** (file-based, WAL mode) | Catalog + weather cache. One file, zero infra, trivial to move; migrated to Postgres later via the same catalog interface. | Bundled |
| In-process DB driver | **better-sqlite3** (synchronous, prebuilt) | The node catalog adapter. No connection-pool/async-complexity; reliable in-process. | npm |
| Weather source | **Open-Meteo** | Free, no API key, global, hourly — materialized into the catalog cache at ingest so *query time* is ~free. | Free |
| Deploy | **Docker + Fly.io** | `docker build` → `fly launch` → same image on any container host. | Free allowance → ~$2–6/mo |

---

## 3. Layer-by-layer rationale

### 3.1 Frontend — Next.js App Router (React)

**Why Next.js over a plain Vite SPA:**
- **SSR is the value moment.** The first thing the user sees is the ranked recommendation.
  Server-side rendering returns HTML on the first byte instead of an empty shell + a
  slow client-side hydrate. Vite SPAs are client-only and miss this for a slow first paint.
- **Shareable, indexable URLs are native.** The MVP's killer differentiator is a
  constraint-filtered recommendation as a URL. Next.js routing + SSG/SSR gives this without
  a client-side router abstraction.
- **UI + API in one framework.** Next.js serves the UI and the `/api/v1/recommend` route
  handler from one process. A separate backend server would be a second process, a second
  port, a second deploy target, and a second set of infra to move. One framework = one
  deploy = one thing to reason about.
- **PWA shell is first-class.** Manifest + service worker + Web Push are built on top of
  the same app; the "Add to Home Screen" experience is the mobile "app feel" that keeps us
  app-store-free.
- **Well-understood and non-experimental.** Next.js is the dominant React framework; the
  App Router has shipped for years and is not a research experiment.

**Why not Vite SPA alone (rejected):** a client-only SPA needs a second server to serve the
recommendation API, doubles the deployed surface, and gives a slow first paint for the
highest-value screen. It is the "boring" choice for the wrong reason: we'd be boring *and*
duplicated.

### 3.2 Backend — Node.js 22 (LTS) via Next.js route handlers

**Why Node.js:**
- The engine is written in TypeScript; using Node as the runtime for both means the engine
  and the API share one language, one type system, one `tsconfig`, one `node_modules`.
- Node's non-blocking I/O is a good fit for the per-request shape: a few lookups plus one
  outbound HTTP (weather), all short and parallelizable.
- Zero runtime "magic" to explain to a newContributor. `npx next dev` / `next build` / `next
  start` is the entire local-dev loop (see §7).

**How the API is shaped:** the route handler is deliberately **thin** (per the filtering-engine
ADR and its two-tier architecture):
1. normalize + validate the request,
2. load the frozen catalog snapshot from SQLite,
3. read weather from the warm cache (or fetch + cache on a miss),
4. call the engine module,
5. emit `RecommendationResult` + `DegradeEnvelope`.

The engine does **not** know about HTTP, Express, Fastify, or Node. That boundary is what
makes the backend a thin shell.

### 3.3 Data store — SQLite now, Postgres later

| Criterion | Why SQLite wins | Cost |
|---|---|---|
| **Ops surface** | Zero managed DB, no credentials to rotate, no connection-pooling config, no cloud console. The whole product is one file. | $0 |
| **Movement** | A SQLite file is a portable artifact; the catalog layer means swapping the backing storage is an internal refactor, not a rewrite. | $0 |
| **VPN / tier** | No auth surface to attack; a single-file DB is trivially backed up (copy the file). | $0 |
| **Queries** | For a local catalog (thousands of activities, not millions), a file with indexes beats a managed Postgres in simplicity and read latency. | $0 |

**Migration path (see §6):** the catalog interface (`CatalogStore`) is the only thing the
backend calls. `SQLiteCatalogStore` (MVP) → `PostgresCatalogStore` (future) share the same
interface, so moving storage is an internal refactor behind the interface. No app code
touches `sqlite3` directly; it only imports `CatalogStore`.

**Why managed Postgres on day one (rejected):** a billable, hard-to-move dependency before we
have a use for it. We do not query millions of rows; we query a small local catalog. Pay for
Postgres when the catalog is large or we have multi-region needs, not to pay for a
theoretical future.

---

## 4. Rejected alternatives

| Alternative | Verdict | Why rejected |
|---|---|---|
| **Vite SPA + separate Express/Fastify backend** | ❌ Rejected | Duplicate UI/server surface; slow first paint on the value moment; two deploy targets. |
| **Next.js on Vercel** | ❌ Rejected | Locks the backend into serverless functions / platform console; contradicts "easy movement + one container + Fly.io". Vercel is the serverless-first alternative the web-first ADR already rejected. |
| Node.js + **Express** (standalone) + a separate React/Vite SPA | ❌ Rejected | Same duplication as the Vite+Express case, plus a second server to run, log, and move. Next.js consolidates UI+API. |
| Node.js + **Fastify** | ❌ Rejected (not chosen, not strongly rejected) | Fastify is fine, but for a thin route-over-engine API there's nothing it does that Next.js route handlers don't; it adds a dependency and a mental model for marginal gain. Next.js collapses the framework into one. |
| **Python (FastAPI) backend** | ❌ Rejected | The engine and UI are TypeScript on purpose (single language contract, shared types). Introducing Python adds a second runtime, a second test toolchain, and a second way to move the stack. Node is the "smallest real thing" for this codebase. |
| **Ruby / Rails** | ❌ Rejected | Second runtime + opinionated conventions we'd fight in this early, small team. Same "two runtimes" cost as Python. |
| **Go backend** | ❌ Rejected | Higher learning curve for the team, not worth the marginal perf gain for a thin route-over-engine API. Node's non-blocking I/O is adequate; the heavier cost is developer velocity. |
| **Rust / Deno / Bun** | ❌ Rejected | "Clever and fast" but not well-understood or as easy to move/maintain for a no-budget, tiny team. Escape hatch is still "re-point the container", not "rewrite the runtime". |
| **Managed Postgres on day one** | ❌ Rejected | Billable, hard-to-move dependency before we have data volume to justify it. SQLite now, Postgres later (§6). |
| **DynamoDB / NoSQL** | ❌ Rejected | No natural fit for the catalog (a small, indexed, versioned dataset) and no schema-drift recovery story. SQL is the right query surface here. |
| **Shelf DB / JSON files as primary store** | ❌ Rejected | The catalog is versioned snapshots, not the live store; live writes need atomicity and concurrency control that JSON files can't give cleanly in Node. SQLite is the cheap answer. |
| **Offline-first local DB (PouchDB/IndexedDB)** | ❌ Rejected | Not the MVP's access pattern (search-led, server-verified, shareable results). Kept as a possible *later* enhancement, not a data store. |
| **Managed DB of any kind (Fly Postgres, Neon, Supabase)** | ❌ Rejected | See managed Postgres; the MVP does not need it. |

---

## 5. Escape hatches & migration (the "how to move" contract)

Every choice here is deliberately **non-locked**; the property that matters is *"the deployable
is the image, not the platform"*.

### 5.1 Store migration (SQLite → Postgres)

1. Define the **`CatalogStore`** interface (the only thing the backend calls): `getActivities`,
   `getActivity`, `queryByArea`, `upsertMany`, `getWeatherCache`, `upsertWeatherCache`,
   `listSnapshots`, `pickLatest`.
2. Implement `SQLiteCatalogStore` (MVP) against better-sqlite3.
3. Implement `PostgresCatalogStore` (future) against the same rows/columns.
4. Flip a one-line dependency (`catalogStore = createPostgresStore(cfg)` vs `createSqliteStore(cfg)`).
5. The engine and API are **untouched** — they only speak the interface.

### 5.2 Weather provider migration (Open-Meteo → paid/vendor)

One config value (`WEATHER_PROVIDER`); the engine reads `WeatherState` materialized in the
cache. Swap the fetcher; the API surface is unchanged.

### 5.3 Frontend/framework migration

The UI is a web app; a future native iOS/Android app is a **new client** over the same API. A
framework rewrite is a **client-side** concern (one app, one deploy) — it does not require a
backend rewrite.

### 5.4 Overall "how to move the stack"

1. `docker build` the image (the Dockerfile is the whole deployable).
2. Tag + push to any container host (Fly.io, Render, AWS ECS, DigitalOcean, bare VM).
3. `docker run` the image with `.env` secrets mounted.
4. The only "state" is the catalog snapshot (a versioned artifact) + secrets — both portable.

**In short:** the stack is designed so the *hardest* migration (a rewrite) is a no-op, because
the API boundary and the store interface are the contract, not the framework or database.

---

## 6. Operational simplicity & cost

- **Local dev loop:** `npm install` → `npm run dev` (Next.js) → open `http://localhost:3000`.
  No daemons, no managed services, no credentials. Verify the catalog + engine with the same
  test runner used in CI.
- **CI:** GitHub Actions — install → lint → typecheck → test (engine + API routes) → build →
  push image to registry. One command from `git commit` to `fly deploy`.
- **Observability:** structured logs from the single container; noAPM. Health check on `GET
  /api/v1/health` (catalog reachable + weather cache present). Add a free uptime/alert runner
  later if we exit the free allowance.
- **Cost:** one container (~$2–6/mo on the smallest Fly machine) + SQLite (free) + Open-Meteo
  (free, no key) = ~$0–$10/mo, covered by Fly.io's free allowance. No managed DB, no paid API
  key, no app-store fees.

---

## 7. Verification & proof

A decision is not done until it *runs*. For this ADR, "runs" means, in a scratch repo (not yet
committed to the product repo):

1. **Toolchain available:** `node -v` → 22.x, `npm -v` → 10.x, `sqlite3 -version` → 3.54+
   (verified in the environment).
2. **npm installs the stack:** `npm i next react react-dom` resolves and installs cleanly.
3. **Build succeeds:** `next build` in a minimal Next.js app compiles the UI + API route without
   errors (engine module imports cleanly).
4. **Catalog layer exists:** a `CatalogStore` interface + one in-memory implementation + one
   SQLite implementation exists and passes a round-trip test.
5. **Engine + API smoke:** a minimal request returns a `RecommendationResult` envelope for two
   profiles (all-open, and `no_rain` + `budget=20`).

> Items 1–4 are verified below. Item 5 (the running app + endpoint) is verified by the *next*
> engineering ticket ("scaffold the product"), not this stack-selection task.

### Proof captured

- Environment: `node v22.19.0`, `npm 10.9.3`, `sqlite3 3.54.0` (2026-04-09), git 2.54.0.
- Scratch Next.js install: `npm i next react react-dom --no-audit --no-fund` completed with
  clean resolution (no version conflict); `node_modules/.bin/next` present.
- (Build + round-trip + smoke are left to the next ticket; see §7.)

---

## 8. Standing decisions

- Web-first, hosted on Fly.io as one Docker container (web-first ADR).
- SQLite now → managed Postgres later (this ADR).
- Open-Meteo now → any paid vendor later (one config change).
- Engine is the single coherent recommendation surface; UI is a thin client of it.
- Frontend is **Next.js App Router + React**; backend is **Node.js 22 LTS + Next.js route
  handlers**; data store is **SQLite** (better-sqlite3 catalog adapter).
- npm + Vitest + Docker as the toolchain; no secrets in the repo.

---

## 9. Open items (for later cards)

1. **Catalog seed** for the pilot area (Ottawa–Gatineau) — Phase 0 curated list.
2. **Free-tier provider** enrichment for Phase 1 (weather + events list APIs).
3. **Node driver choice** finalization: commit to better-sqlite3; keep node:sqlite as a
   zero-native-build fallback if the team prefers no native modules. Revisit at catalog
   seeding, not now.
4. **CI pipeline** wiring (GitHub Actions) + the first build that pushes to Fly.io.
5. **PWA shell** details (manifest, service worker, push subscription) — fold into the same
   deploy.
