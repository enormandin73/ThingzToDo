# Web-First vs App-First and Hosting Target — ADR

**ADR:** `desks/engineering/decisions/2026-10-21-web-first-vs-app-first-and-hosting-target.md`
**Owner:** Forge (Principal Software Architect)
**Date:** 2026-10-21
**Status:** Accepted
**Related ADRs:**
- `2026-10-21-activity-filtering-engine-constraints-matching.md` (the recommendation engine)
- `2026-10-21-outbound-email-path-readiness.md` (alerting)

---

## 0. Purpose & scope

Decides two things that determine where and how we build:

1. **Product direction**: deploy ThingzToDo as a *web-first* product, with a Progressive
   Web App (PWA) shell for a mobile "app feel", rather than a first-class native iOS/Android
   app.
2. **Hosting target**: a concrete, cheap-to-run, easy-to-move deployment host for the MVP and
   beyond.

This ADR is a *deployment and product-shape* decision. It deliberately does **not** redo the
filtering engine (already accepted in a sibling ADR) — it only decides how the engine and its
API are packaged, hosted, and reached by the user.

---

## 1. Decision

> **We ship ThingzToDo as a *web-first* product** — a responsive, mobile-friendly web app
> (PWA-capable, "Add to Home Screen") that is the primary and first-deployed surface — with a
> small, framework-agnostic *recommendation API* behind it. **We host it on *Fly.io*** as a
> single Docker container (a Node.js/Next.js app + the engine + a local catalog cache),
> starting on Fly.io's cheapest machine and migrating to any other container host by re-tagging
> the image when the free allowance is exhausted.

**Why "web-first" and not "app-first":**

- The demand is *already on the web*. The core user question is a search-led question
  ("what should we do near Ottawa when it rains today"). Users arrive via Google/search,
  share a result via a link, and may or may not have the app installed.
- Zero install removes the biggest barrier for a team with no budget and no app-store
  relationships: no iOS Developer Program fee (~$99/yr), no Android Play Console fee
  (~$25 one-time), no store review queue.
- A responsive web app reaches every device with a browser — phone, tablet, desktop, TV —
  from day one, without a second build.
- **Search engines can index it** (the demand is web-native), and the *result is shareable as a
  URL* — a constraint-filtered recommendation is a genuinely useful, citable object:
  `thingztodo.app/?lat=...&lng=...&weather=no_rain&budget=...`.
- Mobile "app feel" is **not** sacrificed: a PWA (manifest + service worker + Web Push) can be
  added to the home screen, run full-screen, and receive push. App-store distribution is a
  *later* decision, not an early one.
- The constraining inputs (location + live weather + time) are **server-side** by nature, so a
  web app does not hand-craft the hard parts; the API owns them.

**Why "app-first" would be the wrong call today:**

- App stores are a tax: fees, review latency, and a two-codebase problem, for a product whose
  *search discovery* is the bottle neck.
- A native app *cannot* win the "shareable, indexable, `what should I do given the actual
  state of the day`" query anyway — that's a web/Search property.
- The research does not justify two products yet: Scout's solution review (t_fe2dc987)
  identifies a *single-product* gap (weather + cost + party-size + time-of-day in one ranked
  list) that is worth solving once, well, before we multiply surfaces.

**Hosting decision, stated plainly:**

- **Concrete target: Fly.io**, deployed as one Docker container (Node.js serving the Next.js
  app + API + engine, plus a small local catalog cache). Cheapest machine ≈ **$1.94–$5.92/mo**
  (published), with a usable free allowance for low-volume side projects (3 shared-cpu-1x VMs,
  1 GB managed Postgres, 160 GB outbound/month) before payment is needed.
- **If Fly.io's free allowance is insufficient or we want to move:** the *same image* runs on
  any container host (Render, AWS ECS Anywhere, DigitalOcean App Platform, a bare VM). No
  platform-specific services are used in the container, so migration is `docker tag` +
  `docker push` + `docker run` (see §6).

---

## 2. Why web-first fits a tiny team with no budget

| Constraint | How web-first wins |
|---|---|
| **No budget** | No app-store fees, no managed-DB cost, no app-review pipeline. Free weather source (Open-Meteo, no key). Cheapest possible hosting footprint. |
| **Tiny team** | One build, one deploy, one surface. A single person can ship, deploy, and iterate without hand-offs. |
| **Search discovery** | The demand is search-led ("things to do near me" ≈ 2.2M US searches/mo, ~1.8× swing). Search *requires* the web. |
| **Same-day urgency** | The fastest-growing demand slice is same-day ("tonight", "this weekend" ≈ +255% YoY). Those users are on a phone *searching*, not in an app store. |
| **Follow-through** | Users abandon AI answers after 26% of sessions (iPullRank); what they want is a *persisted, executable* next step. A web page + "Add to Home Screen" + shareable URL + calendar is the executable step, with no install. |
| **Choice deprivation** | The dominating risk is *too few* options [1], not too many. A web page renders a ranked list fast; a native app's install friction would only delay that. |
| **Migration** | The API is the generalization surface. Adding iOS/Android later = new clients over the same API, not a rewrite. |

The product is *about* results and *about* sharing. Both are native web capacities.

---

## 3. Hosting target — concrete and cheap

**Fly.io** is recommended, for these reasons:

1. **It runs Docker containers** we already build locally (`docker build`).
2. **Cheap at the size we need.** Smallest published machine ≈ $1.94/mo (256 MB RAM) to
   ~$5.92/mo (1 vCPU + 1 GB) at always-on rates; low-volume side projects get a usable free
   allowance before payment is required. No minimum-billing plan, no per-seat fees.
3. **Easy to move.** You can run the identical container on AWS ECS, DigitalOcean, Render, or a
   bare VM with no code change.
4. **Not serverless-locked.** We are not forced into functions-with-cold-start semantics, which
   matters because the engine is compute-and-lookup per request (not a bursty function workload).

**Concrete deployment shape (MVP):**

```text
┌─────────────────────────────────────────────┐
│  Docker container (fly launch / docker run) │
│  ┌───────────────────────────────────────┐  │
│  │  Next.js app (server components + UI) │  │
│  │  ┌───────────────────────────────┐   │  │
│  │  │ recommendation API (route)    │   │  │
│  │  │   - loads catalog snapshot    │   │  │
│  │  │   - fetches weather (cache)   │   │  │
│  │  │   - runs engine (ADR §2)      │   │  │
│  │  └───────────────────────────────┘   │  │
│  │  ┌───────────────────────────────┐   │  │
│  │  │ catalog store (SQLite/JSON)   │   │  │
│  │  │ + short-lived weather cache   │   │  │
│  │  └───────────────────────────────┘   │  │
│  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────┘
```

- **Database:** SQLite (file-based) for the catalog + weather cache in MVP. Zero infra, single
  file, trivial to move. Migratable to managed Postgres later — the catalog layer isolates the
  store. *No managed database required on day one.*
- **Weather:** Open-Meteo (free, no API key, no signup; non-commercial up to 10,000 calls/day,
  attribution CC BY 4.0). Raw JSON over HTTP. Swap provider in one config file if we exceed the
  free tier. *No API key to lift.*

**Cheap-to-run arithmetic for MVP:** one container (~$2–6/mo) + SQLite (free) + Open-Meteo
(free) = essentially **$0–$10/mo** in the first months. Fly.io's free allowance should cover it
without payment being added at all.

**Simpler alternative (and why we didn't pick it):** Render/Netlify are even more "one-button"
for the frontend, but they are *platform-locked* (serverless functions, host-specific APIs)
and do not package the backend engine cleanly. We chose Fly.io because it is both cheap *and*
portable — the two criteria of this task.

---

## 4. Stack and data

| Piece | Choice | Why |
|---|---|---|
| Frontend | **React via Vite** (or Next.js App Router for SSR + shareable URLs) | Small, well-understood, fast to build. SSR matters because the initial recommendation render is the value moment. |
| Recommendation API | **Node.js + the engine module** | Framework-agnostic engine from the sibling ADR; thin HTTP route, no reimplementation. |
| Engine | **Framework-agnostic TS module** | Already accepted in the filtering-engine ADR; pure logic over a snapshot + weather, testable deterministically. |
| Catalog data | **Versioned JSON/GeoJSON snapshot + SQLite index** | Immutable per-query dataset (ADR §10) keeps scoring deterministic and testing easy. SQLite for MVP; Postgres later. |
| Weather | **Open-Meteo** (free, no key) | Zero-API-key, global, hourly up to ~16 days. Materialize into catalog cache at ingest to keep *query time* near-free. |
| Auth / identity | None for MVP | Nothing in the product requires accounts today. Kill the target, not the scope. |
| Deploy | Docker + GitHub Actions (build → push image) | One command from "commit" to "running". |

---

## 5. How this choice supports future migration

The single most important property for "easy to move" is **no platform lock-in**:

- **Portable artifact.** Everything runs in one Docker image. The image, not a platform
  console, is the deployable. To move hosts: `docker tag` → `docker push` → `docker run` (or
  `fly deploy` → `helm template` → anything). Zero code changes.
- **Secrets as environment variables.** No platform-bound config; `.env.example` + `docker
  compose`, not a provider console.
- **Store abstraction.** SQLite (MVP) → Postgres (future). The catalog layer means moving
  storage is an internal refactor, not a rewrite.
- **Weather provider swappable.** Open-Meteo (free) → paid key (NWS/Synoptic/Weather.gov or a
  commercial vendor) is one config change.
- **Dual UI path.** The frontend is a web SPA; a *future* native iOS/Android app is a *new
  client* over the same API. Web-first means the API and its data contract get designed first,
  so the mobile product is an implementation detail of the same contract — the reverse would
  be true for an app-first product.
- **New owner surfaces are cheap.** A future "backup indoor plan" UI, a bookmark/share, a
  calendar export, or a newsletter are all web-native features that add to the *same* deploy.

**Migration path, if it ever becomes necessary:** pick up the `Dockerfile` + `docker-compose.yml`
+ `.env.example` + CI workflow from the repo, run `docker build`, and target whatever container
host owns the traffic. The only "state" is the catalog snapshot (a versioned artifact) and any
secrets — both are portable.

---

## 6. Alternatives rejected

| Alternative | Rejected | Why |
|---|---|---|
| **Native iOS/Android app first** | ❌ | App-store fees + review latency + two codebases; the discovery/search demand is web-native; can't be shared as a URL. |
| **PWA-only with no app shell** | ❌ | We will include the "Add to Home Screen" PWA shell anyway (it's free and improves feel). |
| **Serverless-first (Vercel/Netlify)** | ❌ | Great for the frontend alone, but locks the backend into functions and makes the engine/hourly caching awkward; harder to move. |
| **Heroku** | ❌ | Free tier is gone; platform is heavier and less portable. |
| **Managed Postgres on day one** | ❌ | Adds a billable, hard-to-move dependency before we have a use for it. SQLite now, Postgres later. |
| **Build a mobile app + web in parallel** | ❌ | Wasted budget; one product, one deploy, one surface. Add a client (web, then app) later. |
| **NWS as the only weather source** | ❌ | Open-Meteo is strictly easier to stand up (no key), and NWS is overkill for a first version. Open-Meteo is the low-risk choice. |

---

## 7. Verification and proof

A decision is not done until it runs. For this ADR, "runs" means:

1. **Repo shape exists** — `app/` (the product repo) with `Dockerfile`, `docker-compose.yml`,
   `.env.example`, CI workflow, and an engine module that imports cleanly.
2. **`docker compose up` starts the app** locally and serves the home page (`GET /`) with HTTP 200.
3. **The recommendation endpoint answers** (`GET /api/v1/recommend`) with a structured
   `RecommendationResult` envelope, for at least two constraint profiles (all-open, and
   `no_rain` + `budget=20`).
4. **Weather is materialized into the catalog cache** and the engine reads it from there, not
   from the request path (keeps per-query cost ~0).
5. **Container is portable** — the image tags and runs on the host without any platform-specific
   SDK.

*None of this is yet running — the `app/` repo does not exist. Items 1–5 are the first
engineering ticket after this ADR, and are the acceptance bar for it.*

---

## 8. Standing decisions & open items

**Standing decisions:**
- Web-first, hosted on Fly.io (this ADRs). Migration to any container host by re-tagging the
  image.
- SQLite now → managed Postgres later.
- Open-Meteo now → any paid vendor later (one config change).
- Engine is the single coherent recommendation surface; UI is a thin client of it.

**Open items (for later cards):**
1. Exact frontend choice (Vite SPA vs Next.js SSR) — product/UX decision after the first
   screenshot of the search screen.
2. Where the activity catalog comes from (curated + provider feeds) — ingest pipeline (done as
   part of engine ADR's §10).
3. First geography (Ottawa-Gatineau per the charter) — Scout's materials already assume Canada.
4. Whether the "shareable constraint URL" is a tracked feature (it is the MVP's killer
   differentiator; recommend yes).
5. PWA manifest + Web Push for the "add to home screen" experience — can fold into the same
   deploy.

---

*Design by Forge, Principal Software Architect, 2026-10-21. All host pricing verified from the
vendors' published pages on 2026-10-21 (Fly.io pricing; Open-Meteo pricing). All product/user
claims trace to Scout's labeled research deck.*
