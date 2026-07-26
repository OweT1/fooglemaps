# Instagram Ingestion Service

## Overview

A FastAPI-based backend service that polls Instagram food creators for new posts,
extracts location data, geocodes it to lat/lng via the Google Geocoding API, and
serves the data to the Fooglemaps frontend for display on an interactive map.

## Architecture

```
Instagram (public profiles)
      │
      │ polling via instaloader (every 15 min by default)
      ▼
┌────────────────────────────────────────┐
│  FastAPI Ingestion + API Service        │
│                                         │
│  /services/ingestor.py                  │
│    → instaloader → parse post           │
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
2. **Fetch**: For each creator, instaloader fetches recent posts (configurable limit).
3. **Dedup**: Skip posts already in DB (matched by Instagram shortcode).
4. **Extract**:
   - Caption, image URL, timestamp, post URL
   - Location name + Instagram-provided lat/lng (if available)
5. **Geocode**: If Instagram provides no coordinates, call Google Geocoding API with the location name.
6. **Store**: Insert `instagram_posts` row and upsert `food_places` row (with PostGIS geometry).
7. **Serve**: Frontend fetches `/api/places` (GeoJSON) for the map and `/api/posts` for the feed.

## Database Schema

### creators
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK, default gen_random_uuid() |
| username | VARCHAR(255) | Unique, Instagram handle |
| display_name | VARCHAR(255) | |
| profile_pic_url | TEXT | |
| is_active | BOOLEAN | Default true |
| last_checked_at | TIMESTAMPTZ | Last ingestion time |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

### instagram_posts
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| shortcode | VARCHAR(255) | Unique, Instagram shortcode |
| creator_id | UUID | FK → creators.id |
| caption | TEXT | |
| image_url | TEXT | |
| post_url | TEXT | |
| taken_at | TIMESTAMPTZ | |
| media_type | VARCHAR(20) | image / video / carousel |
| location_name | VARCHAR(500) | From Instagram location tag |
| location_id | VARCHAR(255) | Instagram internal location ID |
| raw_json | JSONB | Full post data from instaloader |
| created_at | TIMESTAMPTZ | |

### food_places
| Column | Type | Notes |
|--------|------|-------|
| id | UUID | PK |
| name | VARCHAR(500) | Location name |
| address | TEXT | Geocoded address |
| geom | GEOGRAPHY(Point, 4326) | PostGIS spatial point |
| cuisine_tags | TEXT[] | From caption analysis (future) |
| source_post_id | UUID | FK → instagram_posts.id |
| created_at | TIMESTAMPTZ | |
| updated_at | TIMESTAMPTZ | |

## API Endpoints

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/posts` | List posts (paginated, filterable) |
| GET | `/api/posts/{id}` | Single post detail |
| GET | `/api/creators` | List tracked creators |
| POST | `/api/creators` | Add a creator to track |
| DELETE | `/api/creators/{id}` | Stop tracking a creator |
| GET | `/api/places` | Food places as GeoJSON for map |
| GET | `/api/places/{id}` | Single place detail |
| POST | `/api/refresh` | Manually trigger ingestion |
| GET | `/health` | Health check |

## Ingestion Details

### instaloader Usage

```python
import instaloader

L = instaloader.Instaloader()
profile = instaloader.Profile.from_username(L.context, username)

for post in profile.get_posts():
    location = post.location  # instaloader.Location
    lat = location.lat if location else None
    lng = location.lng if location else None
    loc_name = location.name if location else None
    # ... store
```

### Google Geocoding Fallback

When Instagram provides a location name but no coordinates:

```
GET https://maps.googleapis.com/maps/api/geocode/json
  ?address={location_name}
  &key={GOOGLE_MAPS_API_KEY}
  &region=sg
```

The `region=sg` parameter biases results toward Singapore.

### Scheduling

- Background task via `asyncio` + `apscheduler` or simple `asyncio.create_task` loop
- Configurable interval (default: 15 minutes)
- `/api/refresh` endpoint for on-demand triggers
- Optional cron job calling `/api/refresh` for production

### Environment Variables

| Variable | Required | Default | Notes |
|----------|----------|---------|-------|
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `GOOGLE_MAPS_API_KEY` | Yes | - | Used for Geocoding API |
| `INSTAGRAM_SESSION_ID` | No | - | Optional, for authenticated instaloader |
| `POLL_INTERVAL_MINUTES` | No | 15 | Ingestion interval |
| `POSTS_PER_CREATOR` | No | 10 | Max posts to check per run |
| `CORS_ORIGINS` | No | `http://localhost:5173` | Frontend URL |

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
