## Prerequisites

- Node.js >= 18
- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [just](https://just.systems/man/en/) (command runner)
- Docker (for the PostgreSQL database)

## Setup

### 1. Environment variables

```bash
cp .env.example .env
```

Fill in the values in `.env` — see `.env.example` for all required keys.

| Variable                                                | How to get it                                                                                                                                                                                                                     |
| ------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `GOOGLE_MAPS_API_KEY`                                   | [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials → Create Credentials → API Key. Enable the Maps JavaScript API and Places API.                                                           |
| `GOOGLE_MAPS_MAP_ID`                                    | [Google Cloud Console](https://console.cloud.google.com) → Map Management → Create Map ID (or use an existing one). Must be associated with the API key above.                                                                    |
| `GOOGLE_OAUTH_CLIENT_ID` / `GOOGLE_OAUTH_CLIENT_SECRET` | [Google Cloud Console](https://console.cloud.google.com) → APIs & Services → Credentials → Create Credentials → OAuth 2.0 Client ID (Web application). Add `http://localhost:8000/api/auth/callback` to Authorized redirect URIs. |
| `POSTGRES_PASSWORD`                                     | Pick any password. If you change this you must also update `docker-compose.yml`.                                                                                                                                                  |
| `POSTGRES_URL`                                          | Leave blank — it's auto-built from the other `POSTGRES_*` vars.                                                                                                                                                                   |
| `INSTAGRAM_SESSION_ID`                                  | Log into Instagram in your browser, open DevTools → Application → Cookies → `sessionid`.                                                                                                                                          |
| `OPENROUTER_API_KEY`                                    | [OpenRouter](https://openrouter.ai/keys) → Create API key.                                                                                                                                                                        |

### 2. Database

```bash
just docker-up
```

This starts a PostgreSQL 16 container on port 5432.

### 3. Running the app

FoogleMaps and TelePromos each need **their own backend + frontend terminal pair**.

#### FoogleMaps

```bash
just backend          # Term 1 — API at http://localhost:8000
just frontend         # Term 2 — app at http://localhost:5173
```

#### TelePromos

```bash
just backend-telepromos  # Term 1 — API at http://localhost:8001
# Term 2 — frontend/telepromos mini app (scaffolded in a later phase)
```

## Project structure

```
fooglemaps/
├── backend/                  # Python monorepo (uv project)
│   ├── commons/              # Shared code between apps
│   │   ├── settings.py       # Base pydantic-settings (reads repo-root .env)
│   │   ├── db/               # Async engine, session factory, Base, get_db_session
│   │   ├── instagram/        # instagrapi / direct Instagram clients
│   │   ├── geocoder.py       # Google Geocoding (httpx)
│   │   ├── llm.py            # OpenRouter client factory
│   │   └── logger.py         # Loguru setup
│   ├── fooglemaps/           # FoogleMaps FastAPI app
│   │   ├── main.py           # app, lifespan (ingestion loop), CORS, routers
│   │   ├── deps.py           # verify_google_token
│   │   ├── schemas.py        # Pydantic response models
│   │   ├── models/           # SQLAlchemy ORM models
│   │   ├── routers/          # auth, settings, posts, creators, places, cuisines
│   │   └── services/         # ingestor, extractor, cuisines
│   ├── telepromos/           # TelePromos FastAPI app (Telegram Mini App backend)
│   │   ├── main.py           # app, lifespan, CORS (localhost:5174), routers
│   │   ├── schemas.py        # Deal + GeoJSON response models
│   │   ├── models/           # deal_sources, deal_posts, deals, telegram_users
│   │   └── routers/          # deals (list + detail)
│   ├── alembic/              # Database migrations
│   ├── pyproject.toml
│   └── alembic.ini
├── frontend/
│   ├── fooglemaps/           # React + Vite web app (src/, index.html, configs)
│   └── telepromos/           # Telegram Mini App (planned — React + Vite + Leaflet)
├── docker-compose.yml       # PostgreSQL + PostGIS service
└── .env.example
```

## Useful commands

| Command                                                | Description                   |
| ------------------------------------------------------ | ----------------------------- |
| `docker compose up -d`                                 | Start PostgreSQL              |
| `docker compose down`                                  | Stop PostgreSQL               |
| `cd backend && uv run alembic upgrade head`            | Apply migrations              |
| `cd backend && uv run alembic revision --autogenerate -m "desc"` | Generate a migration  |
| `cd backend && uv run alembic downgrade -1`            | Rollback last migration       |
| `cd backend && uv run uvicorn fooglemaps.main:app --reload` | Start FoogleMaps backend dev server |
| `cd backend && uv run uvicorn telepromos.main:app --reload --port 8001` | Start TelePromos backend dev server |
| `cd frontend/fooglemaps && npm run dev`                | Start frontend dev server     |
| `cd frontend/fooglemaps && npm run build`              | Build frontend for production |
