## Prerequisites

- Node.js >= 18
- Python >= 3.10
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- Docker (for the PostgreSQL database)

## Setup

### 1. Environment variables

```bash
cp .env.example .env
```

Fill in the values in `.env` — see `.env.example` for all required keys.

### 2. Database

```bash
docker compose up -d
```

This starts a PostgreSQL 16 container on port 5432 and runs the schema from `server/db/init.sql`.

### 3. Backend

```bash
cd server
uv sync                    # create venv + install dependencies
uv run alembic upgrade head   # apply any pending migrations
uv run uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8080`.

### 4. Frontend

```bash
npm install
npm run dev
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

| Command | Description |
|---------|-------------|
| `docker compose up -d` | Start PostgreSQL |
| `docker compose down` | Stop PostgreSQL |
| `uv run alembic upgrade head` | Apply migrations |
| `uv run alembic revision --autogenerate -m "desc"` | Generate a migration |
| `uv run alembic downgrade -1` | Rollback last migration |
| `uv run uvicorn app.main:app --reload` | Start backend dev server |
| `npm run dev` | Start frontend dev server |
| `npm run build` | Build frontend for production |
