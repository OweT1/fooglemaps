# Low-Level Design: Fooglemaps (Singapore Food Map)

## 1. Overview

Fooglemaps is a Google‑Maps‑style web application that displays Singapore food spots on an interactive map. Users can search by cuisine/location, save favorites, and customize their experience. Data is currently static (hardcoded in `src/data/foodPlaces.js`) with plans to ingest from Instagram in the future.

## 2. Architecture

```
┌──────────────────────────────────────────────────────────┐
│  Frontend (React + Vite)                                 │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ Pages    │ │Contexts  │ │Components│ │ Map (Google│  │
│  │(Home,    │ │(Auth,    │ │(Header,  │ │  Maps JS   │  │
│  │ Maps,    │ │ Theme,   │ │ Sidebar, │ │  API)      │  │
│  │ Search,  │ │ Sidebar) │ │ Layout)  │ │            │  │
│  │ Saved,   │ │          │ │          │ │            │  │
│  │ Settings,│ │          │ │          │ │            │  │
│  │ SignIn)  │ │          │ │          │ │            │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
│                          │                               │
│                    HTTP / JSON                           │
│                          │                               │
└──────────────────────────┼───────────────────────────────┘
                           │
              ┌────────────┴────────────┐
              │                         │
              ▼                         ▼
┌─────────────────────────┐  ┌──────────────────────┐
│  FastAPI Backend         │  │  Google APIs         │
│  ┌───────────────────┐  │  │  - Identity Services │
│  │ /api/auth/login   │  │  │  - Maps JS API       │
│  │ /api/auth/me      │──┼──│  - UserInfo API      │
│  │ /api/settings/    │  │  └──────────────────────┘
│  │ /api/health       │  │
│  └────────┬──────────┘  │
│           │             │
│           ▼             │
│  ┌───────────────────┐  │
│  │ PostgreSQL (16)    │  │
│  │ - users            │  │
│  │ - user_settings    │  │
│  └───────────────────┘  │
└─────────────────────────┘
```

## 3. Components

| Component            | Responsibility                                                                 | Tech Stack                                      |
| -------------------- | ------------------------------------------------------------------------------ | ----------------------------------------------- |
| **Frontend**         | Interactive map UI, search, auth, settings, saved places, responsive layout    | React 18, Vite 8, Tailwind CSS 3, React Router 7 |
| **FastAPI Backend**  | Auth token verification (Google UserInfo API), user/settings CRUD, health check | Python 3, FastAPI, SQLAlchemy (async), asyncpg   |
| **PostgreSQL**       | User accounts and per-user settings                                            | PostgreSQL 16 with pgcrypto extension            |
| **Google Maps API**  | Map tiles, markers (`AdvancedMarkerElement`), InfoWindows                       | `@googlemaps/js-api-loader`                      |
| **Google Identity**  | OAuth consent popup, access token issuance                                     | Google Identity Services (GIS)                   |

## 4. Data Model

### `users`
| Column       | Type         | Notes                                |
| ------------ | ------------ | ------------------------------------ |
| id           | UUID         | PK, `gen_random_uuid()`              |
| google_sub   | TEXT         | UNIQUE NOT NULL, Google's user ID     |
| email        | TEXT         | UNIQUE NOT NULL                       |
| display_name | TEXT         | NOT NULL                              |
| avatar_url   | TEXT         |                                       |
| created_at   | TIMESTAMPTZ  | `now()`                               |
| updated_at   | TIMESTAMPTZ  | `now()`                               |

### `user_settings`
| Column                | Type         | Notes                              |
| --------------------- | ------------ | ---------------------------------- |
| id                    | UUID         | PK, `gen_random_uuid()`            |
| user_id               | UUID         | UNIQUE NOT NULL, FK → users(id) ON DELETE CASCADE |
| theme                 | TEXT         | Default `'system'`                 |
| default_zoom          | INTEGER      | Default `12`                       |
| map_type              | TEXT         | Default `'roadmap'`                |
| notify_new_spots      | BOOLEAN      | Default `true`                     |
| notify_recommendations| BOOLEAN      | Default `true`                     |
| created_at            | TIMESTAMPTZ  | `now()`                            |
| updated_at            | TIMESTAMPTZ  | `now()`                            |

## 5. API Endpoints

| Method | Path              | Auth Required       | Purpose                              |
| ------ | ----------------- | ------------------- | ------------------------------------ |
| POST   | `/api/auth/login` | Google Bearer token | Verify token, upsert user + settings |
| GET    | `/api/auth/me`    | Google Bearer token | Return user + settings               |
| PUT    | `/api/settings/`  | Google Bearer token | Update user settings                 |
| GET    | `/api/health`     | No                  | Health check                         |

## 6. Frontend Routes

| Path       | Page          | Access    | Description                            |
| ---------- | ------------- | --------- | -------------------------------------- |
| `/`        | HomePage      | Public    | Dashboard with Quick Actions + stats   |
| `/maps`    | MapsPage      | Public    | Google Map with food place markers     |
| `/search`  | SearchPage    | Public    | Search form with cuisine/location      |
| `/saved`   | SavedPage     | Protected | List of saved food places              |
| `/settings`| SettingsPage  | Protected | Theme, map defaults, notifications     |
| `/signin`  | SignInPage    | Guest     | Google Sign-In button                  |

## 7. Auth Flow

- Frontend uses Google Identity Services `initTokenClient` to obtain an access token.
- Token is sent to `POST /api/auth/login` — backend verifies it via Google UserInfo API, upserts user + default settings.
- Token stored in `sessionStorage`; sent as `Authorization: Bearer` on subsequent requests.
- `GET /api/auth/me` verifies the token and returns the user profile.

## 8. Current Limitations / Future Work

- **Static data**: Food places are hardcoded in `src/data/foodPlaces.js` (5 entries). See `docs/instagram-ingestion.md` for the planned ingestion pipeline.
- **No spatial queries**: PostgreSQL does not have PostGIS installed; no spatial data types are used.
- **No recommendations**: A recommendation service (Redis + ML) is planned but not implemented.
- **No refresh tokens**: The current flow requires re-authentication when the Google access token expires.
