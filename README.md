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

You'll need **two terminals** — one for the backend and one for the frontend.

#### Terminal 1 — Backend

```bash
just backend
```

The API will be available at `http://localhost:8000`.

#### Terminal 2 — Frontend

```bash
just frontend
```

The app will be available at `http://localhost:5173`.

## Project structure

```
fooglemaps/
├── server/                  # FastAPI backend
│   ├── app/
│   │   ├── main.py          # FastAPI app, lifespan, CORS, routers
│   │   ├── db.py            # SQLAlchemy async engine / session factory
│   │   ├── models.py        # SQLAlchemy ORM models + Pydantic schemas
│   │   ├── deps.py          # Dependencies (auth, get_session)
│   │   └── routers/
│   │       ├── auth.py      # POST /api/auth/login, GET /api/auth/me
│   │       └── settings.py  # PUT /api/settings/
│   ├── alembic/             # Database migrations
│   ├── db/init.sql          # Initial schema (used by docker compose)
│   ├── pyproject.toml
│   └── alembic.ini
├── src/                     # React frontend
│   ├── components/
│   ├── context/             # Auth, Theme, Sidebar state
│   ├── pages/               # Home, Maps, Search, Saved, Settings, SignIn
│   └── config/
├── docker-compose.yml       # PostgreSQL service
└── .env.example
```

## Useful commands

| Command                                            | Description                   |
| -------------------------------------------------- | ----------------------------- |
| `docker compose up -d`                             | Start PostgreSQL              |
| `docker compose down`                              | Stop PostgreSQL               |
| `uv run alembic upgrade head`                      | Apply migrations              |
| `uv run alembic revision --autogenerate -m "desc"` | Generate a migration          |
| `uv run alembic downgrade -1`                      | Rollback last migration       |
| `uv run uvicorn app.main:app --reload`             | Start backend dev server      |
| `npm run dev`                                      | Start frontend dev server     |
| `npm run build`                                    | Build frontend for production |
