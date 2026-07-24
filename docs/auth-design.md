# Auth Design — Google OAuth

## 1. Motivation

Users need to **save favorites, create collections, and view their history** across devices. A lightweight OAuth‑only login (Google) removes password management overhead and lets users authenticate with an account they already have.

## 2. Auth Flow

```
User clicks "Sign in with Google"
        │
        ▼
Frontend opens Google OAuth consent screen
        │
        ▼
User grants consent → Google redirects to backend callback
        │
        ▼
Backend exchanges auth code for Google tokens
        │
        ▼
Backend looks up / creates user in DB, issues JWT
        │
        ▼
Backend redirects to frontend with JWT in URL fragment / query param
        │
        ▼
Frontend stores JWT (httpOnly cookie or localStorage) and fetches user profile
```

**Token types:**
- **Access token** (short-lived, ~15 min) — sent as `Authorization: Bearer <token>` on API requests.
- **Refresh token** (long-lived, ~7 days) — stored in httpOnly cookie; used to silently refresh access tokens without re-prompting the consent screen.
- **Google ID token** — used only on the backend during callback to verify the user's identity.

## 3. Frontend Architecture

### Context

One `AuthContext` provider wrapping the app tree:

| State             | Description                                  |
| ----------------- | -------------------------------------------- |
| `user`            | Current user object or `null`                |
| `accessToken`     | Current JWT or `null`                        |
| `loading`         | `true` while checking stored session on mount |
| `error`           | Login failure message or `null`              |

| Method           | Purpose                                                    |
| ---------------- | ---------------------------------------------------------- |
| `signIn()`       | Redirect user to `/api/auth/google` (backend OAuth start)  |
| `signOut()`      | Clear tokens, call `/api/auth/logout`                      |
| `refreshToken()` | Silently refresh JWT via httpOnly cookie                   |

### Components

| Component             | Responsibilities                                                     |
| --------------------- | -------------------------------------------------------------------- |
| **AuthGate**          | Wraps protected routes; shows spinner while `loading`, redirects to sign‑in page if `user` is null. |
| **SignInPage**        | "Sign in with Google" button; calls `signIn()` from AuthContext.     |
| **UserMenu**          | Dropdown in AppHeader: avatar, "Profile", "Settings", "Sign out".   |
| **ProtectedRoute**    | Wraps <Outlet /> with AuthGate. Applied to `/saved`, `/settings`, etc. |

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

- **Access token** — held in a JavaScript variable (memory) + `sessionStorage` fallback for page refreshes.
- **Refresh token** — stored in an **httpOnly, Secure, SameSite=Strict** cookie set by the backend. The frontend never reads it directly.
- On mount, `AuthContext` calls `GET /api/auth/me` — if the httpOnly cookie is present, the backend returns a fresh access token + user profile. If not, the user is treated as unauthenticated.

## 4. Backend API

| Method | Endpoint               | Auth required | Purpose                                          |
| ------ | ---------------------- | ------------- | ------------------------------------------------ |
| GET    | `/api/auth/google`     | No           | Redirect user to Google OAuth consent screen      |
| GET    | `/api/auth/callback`   | No           | Google redirects here; exchange code, issue JWT   |
| GET    | `/api/auth/me`         | Refresh cookie | Return user profile (or 401)                    |
| POST   | `/api/auth/refresh`    | Refresh cookie | Issue new access token                           |
| POST   | `/api/auth/logout`     | No           | Clear refresh cookie and any server-side session  |

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

### Sessions (if server-side tracking needed)

```sql
CREATE TABLE sessions (
    id            UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id       UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    refresh_hash  TEXT NOT NULL,                 -- hashed refresh token
    expires_at    TIMESTAMPTZ NOT NULL,
    created_at    TIMESTAMPTZ DEFAULT now()
);
```

**Design choice:** The backend should **not** store the raw refresh token — only a hash. If the sessions table is breached, tokens cannot be replayed.

## 6. Security Considerations

- **PKCE (Proof Key for Code Exchange)** — use S256 code challenge during the OAuth flow to prevent authorization code interception.
- **State parameter** — include and validate a cryptographically random `state` value to prevent CSRF attacks on the callback.
- **JWT signing** — use RS256 (asymmetric) so the public key can be distributed without exposing the signing secret.
- **Refresh token rotation** — each refresh issues a new refresh token and invalidates the old one. If a stolen refresh token is used after the legitimate one, both are revoked.
- **Minimum Google scopes** — request only `openid email profile`. Do not request Google Contacts, Drive, or other scopes.
- **CORS** — restrict to the frontend origin. Block all other origins.
- **Rate limiting** — apply rate limits on `/api/auth/*` endpoints to prevent brute force or token harvesting.

## 7. Implementation Plan

1. **Backend:** Set up Express/FastAPI route for `/api/auth/google` — build the Google OAuth URL with PKCE + state.
2. **Backend:** Implement `/api/auth/callback` — exchange code, verify ID token, upsert user, set refresh cookie, return access token.
3. **Backend:** Implement `/api/auth/me` — validate refresh cookie, return user profile + new access token.
4. **Backend:** Implement `/api/auth/logout` — clear refresh cookie, delete session row.
5. **Frontend:** Create `AuthContext` with signIn/signOut/refreshToken methods.
6. **Frontend:** Create `SignInPage`, `UserMenu`, `AuthGate`, `ProtectedRoute` components.
7. **Frontend:** Wire router — add `/signin` route, wrap `/saved` and `/settings` with `ProtectedRoute`.
8. **Frontend:** Wire `AuthContext.Provider` in `src/app/index.jsx` around `<App />`.
9. **Integration:** Test end-to-end flow (local dev with Google Cloud Console OAuth credentials).
10. **Env vars:** Add `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, `AUTH_REDIRECT_URI`, `JWT_SECRET`, `SESSION_SECRET` to config.