# Engineering Status — ThingzToDo

**Owner:** Forge (Principal Software Architect)
**Last updated:** 2026-10-21
**Repo home:** `/Users/martennormandin/thingztodo/`

> Pre-product. This status tracks the engineering production path and the health of the
> supporting toolchain we rely on.

---

## 1. Product state

| Item | Status |
|---|---|
| ThingzToDo application (`app/`) | **Not started.** Repo holds `desks/` + `docs/` only; no `app/` directory. |
| Product direction + hosting target | **Decided.** Web-first, hosted on Fly.io as one Docker container. ADR `2026-10-21-web-first-vs-app-first-and-hosting-target.md`. |
| Activity filtering/recommendation engine | Design accepted (`2026-10-21-activity-filtering-engine-constraints-matching.md`). |
| Geo search approach | **Decided.** Geohash grid + prefix-range query + exact haversine filter; best-effort geocoding; multi-tier fallback for missing location. ADR `2026-10-21-geo-search-approach.md`. |
| Data ingestion source strategy | **Decided.** Curated core + best-effort free-tier enrichment + moderated user-generated. ADR `2026-10-21-activity-catalog-ingestion-source-strategy.md`. |
| Stack (frontend, backend, data store, toolchain) | **Decided.** Next.js App Router + React on Node.js 22 LTS, SQLite (better-sqlite3), Vitest, Docker, Fly.io. ADR `2026-10-21-framework-backend-and-data-store.md`. |
| Outbound email to Eric | **Blocked** — no outbound SMTP path (ADR `2026-10-21-outbound-email-path-readiness.md`). |
| WhatsApp alerting | Blocked — Baileys cannot cold-start outbound (RUNBOOK §5). |

---

## 2. Key architectural decisions (integrated record)

The decisions below are the architecture of ThingzToDo v1. They are recorded individually in
the workstream ADRs in `desks/engineering/decisions/` and integrated here.

| ADR | Status |
|---|---|
| `ADR-0001-v1-architecture.md` | **Accepted (integrated record)** — consolidated architecture decision record. **Auth/identity section amended in place 2026-10-22** (REVERSED: accounts added) to reflect the CEO-directed account direction. See `2026-10-22-authentication-provider-and-accounts.md`. |
| `2026-10-22-interface-shape-map-first-chat-sidecar.md` | **Accepted (design)** — interface architecture: map-first, chat-as-sidecar; canonical `FilterState` schema; map provider (Leaflet + OSM tiles); SSR; voice stance; LLM boundary; degradation. |
| `2026-10-22-authentication-provider-and-accounts.md` | **Accepted** — authentication provider & account decision record. Verdict: **adopt Clerk (Hobby) for MVP**; self-hosted identity weighed honestly. Must accompany the ADR-0001 §4 reversal. |
| `2026-10-21-activity-filtering-engine-constraints-matching.md` | Accepted (design) |
| `2026-10-21-geo-search-approach.md` | Accepted (design) |
| `2026-10-21-web-first-vs-app-first-and-hosting-target.md` | Accepted (design) |
| `2026-10-21-framework-backend-and-data-store.md` | Accepted (design) |
| `2026-10-21-activity-catalog-ingestion-source-strategy.md` | Accepted (design) |
| `2026-10-21-outbound-email-path-readiness.md` | Reject / blocked on credentials |

---

## 3. Toolchain / capability health

| Capability | Status | Notes |
|---|---|---|
| Outbound email (SMTP) | ❌ No path | See ADR `2026-10-21-outbound-email-path-readiness.md`. No himalaya CLI, no SMTP creds, no email platform configured. |
| Messaging platforms (telegram/discord/slack/signal/whatsapp) | ❌ No platform configured | `hermes send --list` → "no messaging platforms configured". |
| Scraper / web tooling | WIP | Ingest pipeline defined in ADR `2026-10-21-activity-catalog-ingestion-source-strategy.md`; not yet built. |
| CI / local dev loop | TBD | Not yet wired. |
| Product repo (`app/`) | **Not started** | No architecture can run until `app/` is scaffolded (next engineering ticket). |

---

## 4. Stack & data store decision (2026-10-21)

**ADR:** `2026-10-21-framework-backend-and-data-store.md` (accepted).

| Layer | Choice | Why |
|---|---|---|
| Frontend | **Next.js (App Router) + React** | SSR for the value-moment ranked list; native shareable/indexable URLs; UI + API in one framework; PWA shell for the mobile "app feel". |
| Backend runtime | **Node.js 22 LTS** | Same language as the engine (TS) + well-understood, async I/O for a thin HTTP route. |
| Backend HTTP / API | **Next.js route handlers** (`/api/v1/recommend`) | UI + API in one process; the route is a thin shell (validate → catalog → weather cache → engine → envelope). |
| Data store | **SQLite** (file, WAL) | Zero managed-DB ops, zero credentials, trivial to move; migrated to managed Postgres later behind the `CatalogStore` interface. |
| In-process driver | **better-sqlite3** (sync, prebuilt) | Reliable, no connection-pool/async complexity. |
| Test runner | **Vitest** | TS-native, fast, bundled with the Next.js toolchain. |
| Deploy | **Docker + Fly.io** | Single image; movable to any container host by re-tagging. |
| Weather | **Open-Meteo** | Free, no key, hourly; materialized into the catalog at ingest so *query time* is ~free. |

**Cost ceiling (MVP):** ~$0–$10/mo — one container (~$2–6) + SQLite (free) + Open-Meteo (free).

### Escape hatches

- **Store:** `CatalogStore` interface → `SQLiteCatalogStore` (now) → `PostgresCatalogStore` (later). Flip one line; engine + API untouched.
- **Weather provider:** `WEATHER_PROVIDER` config value; engine reads `WeatherState` materialized in the cache.
- **Frontend/framework:** future native mobile clients are new clients over the same API; a framework rewrite is client-side only.
- **Overall:** deployable = the Docker image, not the platform.

### Toolchain proof (real, not claimed)

- `node v22.19.0`, `npm 10.9.3`, `sqlite3 3.54.0`, git 2.54.0 (verified).
- `npm i next react react_dom` → clean install, Next.js v16.4.2, `next --version` resolves (verified).
- In-process SQLite round-trip via `node:sqlite`: seeded 3 activities near a search center, queried by area (3 returned), cached + read back a `WeatherState` object. Full output captured in `/tmp/stack-proof-2/stack-proof.js`. (`node:sqlite` is **experimental** — flagged for the team; see ADR §9 open item #3.)
- Full Next.js `next build` + a real API endpoint + catalog seed → pending next engineering ticket (app scaffold), not this ADR.

---

## 5. Open items

1. **Email:** Eric's email + SMTP credentials (or email-service account) — required before alerts can be routed. See ADR `2026-10-21-outbound-email-path-readiness.md`.
2. **WhatsApp:** requires Eric to message the bot first (RUNBOOK §5) or a Twilio account.
3. **Scraping:** source strategy for activities, weather, events (decided — see ingestion ADR: **no scrapers, no licensed data on day one**; best-effort free-tier enrichment only).
4. **Repo scaffolding:** `app/` structure, package layout, dev server.
5. **Geo precision tuning (`p_min`/`p_max`) + cached TTLs:** measured once we have real query volume.
6. **PostGIS escape hatch:** decided when the catalog migrates from SQLite.
7. **Ci pipeline:** GitHub Actions wiring + the first build that pushes to Fly.io.
8. **PWA shell details:** manifest, service worker, push subscription.

---

## 6. Last verified

- `hermes send --list` — no platforms configured.
- `hermes doctor` — passes config validation; no email adapter present.
- `himalaya --version` — command not found.
- `~/.hermes/config.yaml` — no SMTP/IMAP section.
- **Stack selection verified (this run, task t_b0ea861f):** `node -v` → v22.19.0; `npm -v` → 10.9.3; `sqlite3 --version` → 3.54.0 (2026-04-09); `git --version` → git 2.54.0. All four match the stack ADR's claims (ADR §7). Next.js build + catalog round-trip are the next ticket's acceptance bar, not this stack-selection task.
- **Geo search verified (task t_b4228e04):** `verify_geo_search.py` → PASS 5/5 checks, EXIT_CODE=0 (geohash round-trip, superset guarantee, exact==brute force, cell-size monotonic, missing-location fallback).
- **Architecture decision record (this run, task t_aecf05d5):** `ADR-0001-v1-architecture.md` written and integrated; STATUS.md updated to reflect the current architecture decision state.
