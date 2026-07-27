# Auth Design — Google OAuth (Client-Side Flow)

## 1. Motivation

Users need to **save favorites, create collections, and view their history** across devices. A lightweight OAuth‑only login (Google) removes password management overhead and lets users authenticate with an account they already have.

## 2. Auth Flow

```
User clicks "Sign in with Google"
        │
        ▼
Frontend calls google.accounts.oauth2.initTokenClient()
        │
        ▼
Google consent popup appears (overlay, not redirect)
        │
        ▼
User grants consent → callback receives Google access token
        │
        ▼
Frontend sends Google access token to POST /api/auth/login
        │
        ▼
Backend verifies token via Google UserInfo API
        │
        ▼
Backend looks up / creates user in DB, upserts default settings
        │
        ▼
Backend returns user profile + settings to frontend
        │
        ▼
Frontend stores access token in sessionStorage
        │
        ▼
AuthContext sets user state
```

**Token types:**
- **Google access token** (short-lived) — obtained from GIS `initTokenClient`, sent as `Authorization: Bearer <token>` on API requests.
- **No JWT** — the backend does not issue its own tokens. The Google access token is verified on each request via the Google UserInfo API.
- **No refresh token** — the frontend re-inititates the GIS token client when the session expires.

## 3. Frontend Architecture

### Context

One `AuthContext` provider wrapping the app tree:

| State      | Description                                   |
| ---------- | --------------------------------------------- |
| `user`     | Current user object or `null`                 |
| `settings` | User settings object (theme, map defaults)    |
| `loading`  | `true` while checking stored session on mount |

| Method             | Purpose                                                     |
| ------------------ | ----------------------------------------------------------- |
| `signIn()`         | Calls GIS `initTokenClient` → sends token to `/api/auth/login` |
| `signOut()`        | Clears `sessionStorage` and resets state                    |
| `updateSettings()` | Sends `PUT /api/settings/` with partial settings update     |

### Components

| Component          | Responsibilities                                                     |
| ------------------ | -------------------------------------------------------------------- |
| **SignInPage**     | "Sign in with Google" button; calls `signIn()` from AuthContext.     |
| **UserMenu**       | Avatar dropdown: "Sign in" (unauthenticated) or Saved/Settings/Sign out (authenticated). |
| **ProtectedRoute** | Wraps children; redirects to `/signin` if `user` is null.            |

### Route changes

```
/              → HomePage        (public)
/maps          → MapsPage        (public)
/search        → SearchPage      (public)
/saved         → SavedPage       (protected)
/settings      → SettingsPage    (protected)
/signin        → SignInPage      (guest only)
```

### Token storage strategy

- **Google access token** — stored in `sessionStorage`.
- On mount, `AuthContext` checks `sessionStorage` for a stored token and calls `GET /api/auth/me`. If valid, the user is authenticated.
- When the token expires, the user must sign in again via the Google consent popup.

## 4. Backend API

| Method | Endpoint            | Auth required     | Purpose                                         |
| ------ | ------------------- | ----------------- | ----------------------------------------------- |
| POST   | `/api/auth/login`   | Google Bearer token | Verify Google token, upsert user + settings    |
| GET    | `/api/auth/me`      | Google Bearer token | Return user profile + settings (or 401)        |
| PUT    | `/api/settings/`    | Google Bearer token | Update user settings (theme, zoom, map type, notifications) |
| GET    | `/api/health`       | No               | Health check                                    |

## 5. Data Model

### Users table (PostgreSQL)

```sql
CREATE TABLE users (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_sub    TEXT UNIQUE NOT NULL,          -- Google's unique user ID
    email         TEXT UNIQUE NOT NULL,
    display_name  TEXT NOT NULL,
    avatar_url    TEXT,
    created_at    TIMESTAMPTZ DEFAULT now(),
    updated_at    TIMESTAMPTZ DEFAULT now()
);
```

### User Settings table (PostgreSQL)

```sql
CREATE TABLE user_settings (
    id                     UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id                UUID UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    theme                  TEXT DEFAULT 'system',
    default_zoom           INTEGER DEFAULT 12,
    map_type               TEXT DEFAULT 'roadmap',
    notify_new_spots       BOOLEAN DEFAULT true,
    notify_recommendations BOOLEAN DEFAULT true,
    created_at             TIMESTAMPTZ DEFAULT now(),
    updated_at             TIMESTAMPTZ DEFAULT now()
);
```

## 6. Security Considerations

- **Google token verification** — backend calls Google UserInfo API (`https://www.googleapis.com/oauth2/v3/userinfo`) with the Bearer token on every auth-required request.
- **Minimum Google scopes** — request only `openid email profile`. Do not request Google Contacts, Drive, or other scopes.
- **CORS** — restricted to frontend origin (`http://localhost:5173` in dev).
- **Environment variables** — `GOOGLE_OAUTH_CLIENT_ID` and `GOOGLE_OAUTH_CLIENT_SECRET` configured in `.env`.

## 7. Implementation Details

1. **Backend:** FastAPI route `POST /api/auth/login` — accepts `{ "access_token": "..." }`, verifies via Google UserInfo API, upserts user + creates default settings, returns `UserResponse` + `SettingsResponse`.
2. **Backend:** FastAPI route `GET /api/auth/me` — extracts Bearer token, verifies via Google, looks up user by `google_sub`, returns user + settings.
3. **Backend:** FastAPI route `PUT /api/settings/` — updates `user_settings` columns for the authenticated user.
4. **Frontend:** `AuthContext` with `signIn`/`signOut`/`updateSettings` methods.
5. **Frontend:** Google Identity Services (GIS) `initTokenClient` used in `signIn()` to obtain access token.
6. **Routes:** `/saved` and `/settings` wrapped with `ProtectedRoute`.
