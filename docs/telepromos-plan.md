# TelePromos — Telegram Mini App Build Plan

This doc captures the full plan for restructuring the FoogleMaps repo and building
**TelePromos**, a Telegram bot + Mini App for food deals, scraped from Instagram.

## Goal

Host a Telegram bot with an interactive UI (a Telegram Mini App). The app has
distinct page sections: a **list of food offers/deals** and an **interactive map**.
The backend is structurally similar to the current FoogleMaps server (FastAPI +
PostGIS + Instagram ingestion via instagrapi + LLM extraction + geocoding), but it
is a separate project with its own data model — deals (with validity, discount
details, venues) rather than food places.

## Current state

FoogleMaps is a Singapore-focused food discovery web app:

```
Instagram creators ──(instagrapi, 30 min loop)──► FastAPI ingestion
  caption ─► OpenRouter LLM (place_name/address/cuisine)
  place    ─► Google Geocoding (lat/lng)
  ──► PostgreSQL 16 + PostGIS (users, creators, instagram_posts, food_places, cuisines)
  ──► React 18 + Vite 8 + Tailwind 3 SPA ──► Google Maps JS API
```

There is **no Telegram code** yet. The app is local/dev-oriented (no Dockerfile for
the app, no CI), only Postgres runs in Docker.

## Target architecture

```
fooglemaps/
├── backend/                    # Python monorepo (uv project)
│   ├── commons/                # shared: settings, db, instagram client, geocoder, llm, logger
│   ├── fooglemaps/             # existing FastAPI app (food places web app)
│   ├── telepromos/             # NEW FastAPI app (deals mini app + bot)
│   ├── gateway/                # ASGI edge for production (mounts both apps)
│   ├── alembic/                # one migration tree, one DB
│   └── pyproject.toml          # one uv project (packages = commons/fooglemaps/telepromos)
├── frontend/
│   ├── fooglemaps/             # existing React web app
│   └── telepromos/             # NEW Telegram Mini App (React + Vite + Tailwind + Leaflet)
├── docker-compose.yml          # PostGIS (unchanged)
├── Justfile
└── .env                        # + TELEGRAM_BOT_TOKEN, INSTAGRAM_DEAL_CREATORS, ...
```

## Key decisions

| Area | Decision |
|---|---|
| Processes | Two FastAPI apps (`fooglemaps`, `telepromos`) sharing `commons/`; dev runs two uvicorn processes (8000, 8001) |
| Production edge | One Fly app, one public service: `gateway` mounts `telepromos` at `/` (primary) and `fooglemaps` at `/fooglemaps/` (Vite `base` + prefixed API calls) |
| Database | Single Postgres+PostGIS, single Alembic tree; telepromos tables added in migration `0005` |
| Map in Mini App | Leaflet + OSM tiles via `react-leaflet` (no API key in WebView) |
| Deal geocoding | Reuse Google Geocoding from `commons/geocoder.py` (server-side key) |
| Auth | Telegram `initData` HMAC validation per-request via `X-Telegram-Init-Data` header — no JWT, no sessions |
| Bot | Lightweight httpx Bot API calls (no framework): `/start` + inline `web_app` button, `setChatMenuButton`, webhook with secret token |
| Notifications | After deals ingestion → `sendMessage` to `telegram_users` with `notify_enabled` (rate-limited) |
| Deals sources | `INSTAGRAM_DEAL_CREATORS` env → `deal_sources` table, polled independently of fooglemaps creators |
| Deployment | Single Fly app + **Fly managed Postgres** (PostGIS); the existing fooglemaps web app stays **local-only for now** — the `/fooglemaps/` gateway mount is deferred |

## Phases

### 1. Mechanical restructure (no behavior change) — DONE

- `server/` → `backend/fooglemaps/` + `backend/commons/`; `src/`, `index.html`,
  `vite.config.js`, `tailwind.config.js`, `postcss.config.js`, `package.json` →
  `frontend/fooglemaps/`
- Moved to `commons/`: settings, db session factory + `Base` + `get_db_session`,
  instagram client, geocoder, llm (OpenRouter), logger
- Kept in `fooglemaps/`: models, schemas, routers, services (ingestor/extractor/cuisines), main
- Updated `alembic/env.py` (imports `commons.db.Base`, registers `fooglemaps.models`),
  `alembic/versions/0003_cuisines.py` import, `Justfile`, `README.md`, `.gitignore`, docs

Verification: `uv sync`, `uv run` import of `fooglemaps.main` (12 routes), `alembic heads` = 0004.

### 2. TelePromos backend skeleton

- `telepromos/main.py` + settings extension (`TELEGRAM_BOT_TOKEN`,
  `INSTAGRAM_DEAL_CREATORS`, `TELEGRAM_WEBHOOK_SECRET`, `TELEGRAM_APP_URL`)
- Migration `0005_telepromos`:
  - `telegram_users` (telegram_id UNIQUE, chat_id, username, notify_enabled, timestamps)
  - `deal_sources` (username UNIQUE, active — synced from env like fooglemaps creators)
  - `deal_posts` (shortcode UNIQUE, caption, raw_json, posted_at)
  - `deals` (title, description, venue_name, address, `geography POINT` GIST index,
    discount_text, pct_off, valid_from, valid_until, terms, source_post FK)
- Endpoints: `GET /api/deals` (filters: active-only, bbox, sort ending-soon,
  limit/offset), `GET /api/deals/{id}`, `POST /api/refresh`, `GET /health`
- Verification: curl endpoints against seeded fixture data

### 3. Deals ingestion pipeline

- Mirror `fooglemaps/services/ingestor.py`: poll `deal_sources` → new posts →
  LLM extraction with a deals-specific prompt → Pydantic-validated JSON
  (`title, venue_name, address, discount_text, pct_off, valid_from, valid_until,
  terms, description`) → Google Geocoding → upsert `deals`
- LLM prompt iteration using the existing `notebooks/` fixture pattern
- Runs in `telepromos` lifespan (independent poll loop)
- Verification: `POST /api/refresh` on a real deal-carrying creator; check
  geocoding + expiry filtering

### 4. Telegram bot + auth

- `telegram_auth.py`: `data_check_string` → HMAC(`WebAppData`, bot_token) → compare
  hash; FastAPI dependency reading `X-Telegram-Init-Data`, upserts `telegram_users`,
  rejects expired/forged
- `bot.py` + `POST /telegram/webhook` (validated via `X-Telegram-Bot-Api-Secret-Token`):
  `/start` → inline `web_app` button; handles `start_param` (`deal_123` → opens deal detail)
- On deploy: `setChatMenuButton` (web_app), `setWebhook`
- `PUT /api/me/notifications` (toggle), notifier service fired post-ingestion with
  batched/rate-limited sends
- Verification: HMAC unit tests with known-good vectors; webhook against
  ngrok/Cloudflare Tunnel

### 5. `frontend/telepromos` — the Mini App

- React 18 + Vite (port 5174, proxy `/api` → 8001) + Tailwind (reuse token/theme
  approach from fooglemaps) + `HashRouter`
- `telegram/webApp.js` wrapper: `ready()`, `expand()`, `setHeaderColor`/
  `setBackgroundColor`, `themeParams` → `data-theme`, `BackButton` on detail pages,
  `openLink()` for Instagram source links
- `api.js`: `apiFetch()` always attaches `X-Telegram-Init-Data`; clear
  "Open in Telegram" screen when `initData` absent (with `?dev=1` bypass for browser testing)
- Layout: mobile-first, **bottom tab bar — Deals | Map | Me**
  - **Deals**: card list — title, venue, discount badge, "ends in 3d" countdown,
    filter (active/expired, ending soon)
  - **Map**: `react-leaflet` + OSM tiles, deal markers → tap opens detail sheet
  - **Deal detail**: full terms, validity, source post link
  - **Me**: Telegram profile, notifications toggle
- Verification: Telegram test environment (allows HTTP/IP for dev) or tunnel;
  desktop webview inspector + `?eruda=1` on mobile

### 6. Fly.io deployment

- Multi-stage `Dockerfile`: Node builds the telepromos frontend → `uv sync` →
  runtime image; the `telepromos` FastAPI app serves its `dist/` at `/` plus the
  API and bot webhook
- `fly.toml` + `fly secrets set TELEGRAM_BOT_TOKEN=… GOOGLE_MAPS_API_KEY=…` etc.;
  Fly managed Postgres (enable PostGIS) — or fall back to an external host if
  PostGIS is unavailable
- `setWebhook` to `https://<app>.fly.dev/telegram/webhook`
- The fooglemaps backend/web app remain local-only for now; if we later want them
  public, add the `gateway` step (mount `fooglemaps` at `/fooglemaps/` with a
  Vite `base` + prefixed API calls)

### 7. Docs + Justfile polish

- Tasks: `backend-fooglemaps`, `backend-telepromos`, `frontend-fooglemaps`,
  `frontend-telepromos`, `miniapp`; README updates

## Risks

- **LLM deals extraction accuracy** (validity dates especially) — mitigate with
  fixture-driven prompt iteration before wiring notifications
- **WebView quirks** — Leaflet is well-trodden in TMAs (unlike Google Maps WebGL),
  but verify iOS WKWebView tile/touch behavior early
- **initData lifetime** (~24h) — page load re-sends fresh data; long-lived open
  sessions just need a graceful re-prompt
- **instagrapi fragility** unchanged; deal creators polled separately so a ban there
  doesn't take down fooglemaps
- **Scope**: phases 2 and 3 are the critical path; the mini app (5) can be built
  against fixture data in parallel with 3–4

## Task inputs

Required as we build:

- **BotFather bot** (`/newbot`) + `TELEGRAM_BOT_TOKEN`
- **Mini App registration** (BotFather `/newapp` or menu button) + `TELEGRAM_APP_URL`
- **`INSTAGRAM_DEAL_CREATORS`** — comma-separated Instagram accounts that post
  Singapore food deals/promos
- `TELEGRAM_WEBHOOK_SECRET` (generate with `openssl rand -hex 32`)

## Decisions (resolved)

| Question | Answer |
|---|---|
| Production Postgres | **Fly managed Postgres** with PostGIS |
| fooglemaps web app on Fly | **Local-only for now**; only TelePromos deploys |