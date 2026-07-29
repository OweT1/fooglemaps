# Instagram Ingestion Service

> **Status: Implemented** — Uses Instagram's internal Web API (via managed session) to fetch posts from tracked creators.

## Overview

A FastAPI-based backend service that polls Instagram food creators for new posts,
extracts location data, geocodes it to lat/lng via the Google Geocoding API, and
serves the data to the Fooglemaps frontend for display on an interactive map.

## Architecture

```
Instagram (public profiles)
      │
      │ polling via Instagram Web API (every 15 min by default)
      ▼
┌────────────────────────────────────────┐
│  FastAPI Ingestion + API Service        │
│                                         │
│  /services/instagram_client.py          │
│    → managed session → Instagram API    │
│    → login / cookie persistence         │
│    → rate limiting / retries            │
│                                         │
│  /services/ingestor.py                  │
│    → fetch_user_posts()                 │
│    → extract location / lat-lng         │
│    → store in DB                        │
│                                         │
│  /services/geocoder.py                  │
│    → Google Geocoding API fallback      │
│                                         │
│  /routers/posts.py                      │
│  /routers/creators.py                   │
│  /routers/places.py                     │
└──────────────┬──────────────────────────┘
               │ REST API (JSON / GeoJSON)
               ▼
┌────────────────────────────────────────┐
│  React Frontend                         │
│  - MapsPage: dynamic markers from API   │
│  - FeedPage: post cards with images     │
│  - Creator management in sidebar         │
└─────────────────────────────────────────┘
```

## Data Flow

1. **Polling**: On startup + every N minutes, the ingestor checks tracked creators.
2. **Fetch**: For each creator, `InstagramClient.fetch_user_posts()` hits Instagram's internal Web API endpoints.
3. **Dedup**: Skip posts already in DB (matched by Instagram shortcode).
4. **Extract**:
   - Caption, image URL, timestamp, post URL
5. **Geocode**: If the LLM extracts a place name, call Google Geocoding API with the location name.
6. **Store**: Insert `instagram_posts` row and upsert `food_places` row (with PostGIS geometry).
7. **Serve**: Frontend fetches `/api/places` (GeoJSON) for the map and `/api/posts` for the feed.

## Authentication

The client supports two authentication methods, checked in order:

1. **Username/Password (Recommended)**: Set `INSTAGRAM_USERNAME` and `INSTAGRAM_PASSWORD`. The client will log in programmatically and persist cookies to `data/instagram_cookies.json` for reuse across restarts.
2. **Session ID (Fallback)**: Set `INSTAGRAM_SESSION_ID` — copy the `sessionid` cookie value from your browser after logging into instagram.com. The client will use this directly without a full login flow.

Cookies are cached to disk to avoid re-authenticating on every restart.

## API Endpoints Used

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/v1/users/web_profile_info/?username={user}` | Look up user PK |
| GET | `/api/v1/feed/user/{pk}/?count=N&max_id={cursor}` | Fetch paginated media |

These are the same endpoints the official Instagram web app uses internally.

## Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `GOOGLE_MAPS_API_KEY` | Yes | - | Used for Geocoding API |
| `INSTAGRAM_USERNAME` | No* | - | Instagram login username |
| `INSTAGRAM_PASSWORD` | No* | - | Instagram login password |
| `INSTAGRAM_SESSION_ID` | No* | - | Session cookie from browser |
| `POLL_INTERVAL_MINUTES` | No | 30 | Ingestion interval |
| `POSTS_PER_CREATOR` | No | 10 | Max posts to check per run |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Frontend URL |

\* At least one auth method is required to fetch posts from private/protected profiles. For public profiles, the API may still work without authentication but rates are stricter.

## Rate Limiting

The client has built-in retry logic for 429 (rate limited) responses. If you hit rate limits:
- Reduce `POLL_INTERVAL_MINUTES` to a higher value
- Use a dedicated Instagram account with a good reputation
- Avoid running multiple concurrent ingestion jobs

## Frontend Integration

### MapsPage Changes
- Fetch `/api/places` on mount
- Replace static `foodPlaces.js` import
- Add AdvancedMarkerElement for each place
- InfoWindow shows place name + post thumbnail + link to Instagram

### New FeedPage
- Grid of post cards with image, caption, creator, location
- "View on Map" button → navigates to MapsPage centered on the place
- Pagination or infinite scroll

### New Creator Management
- Sidebar section or settings page to add/remove tracked creators
- Shows profile pic and username
