import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
import utils.logger
from loguru import logger
from sqlalchemy import select

from core import settings
from db import get_session_factory, close_session_factory, Creator
from services import ingest_creator_posts, close_instagram_client
from utils import get_db_session
from sqlalchemy.ext.asyncio import AsyncSession
from .v1.routers import auth_router, settings_router, posts_router, creators_router, places_router, cuisines_router

poll_interval_minutes = settings.poll_interval_minutes
posts_per_creator = settings.posts_per_creator
_scheduler_task = None

async def sync_creators_from_config(session: AsyncSession):
    raw = settings.instagram_creators
    configured_usernames = {u.strip().lower() for u in raw.split(",") if u.strip()}

    result = await session.execute(select(Creator))
    all_creators = result.scalars().all()

    existing_usernames = {c.username: c for c in all_creators}

    for username in configured_usernames:
        if username in existing_usernames:
            creator = existing_usernames[username]
            if not creator.is_active:
                creator.is_active = True
                logger.info("Re-activated creator: {}", username)
        else:
            creator = Creator(username=username, is_active=True)
            session.add(creator)
            logger.info("Added creator from config: {}", username)

    for username, creator in existing_usernames.items():
        if username not in configured_usernames and creator.is_active:
            creator.is_active = False
            logger.info("De-activated creator (removed from config): {}", username)

    await session.commit()


async def ingestion_loop():
    logger.info("Ingestion scheduler started (interval={}min)", poll_interval_minutes)
    while True:
        try:
            factory = await get_session_factory()
            async with factory() as session:
                await sync_creators_from_config(session)
                result = await session.execute(
                    select(Creator).where(Creator.is_active == True)
                )
                active_creators = result.scalars().all()
                if active_creators:
                    logger.info("Scheduled ingestion for {} creator(s)", len(active_creators))
                    for creator in active_creators:
                        await ingest_creator_posts(creator, session, posts_limit=posts_per_creator)
                    await session.commit()
                else:
                    logger.debug("No active creators to ingest")
        except Exception as e:
            logger.error("Ingestion loop error: {}", e)
        await asyncio.sleep(poll_interval_minutes * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler_task
    logger.info("Starting up FoogleMaps server")
    await get_session_factory()
    _scheduler_task = asyncio.create_task(ingestion_loop())
    yield
    logger.info("Shutting down FoogleMaps server")
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
    await close_instagram_client()
    await close_session_factory()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth")
app.include_router(settings_router, prefix="/api/settings")
app.include_router(posts_router, prefix="/api/posts")
app.include_router(creators_router, prefix="/api/creators")
app.include_router(places_router, prefix="/api/places")
app.include_router(cuisines_router, prefix="/api/cuisines")


@app.get("/api/health")
async def health():
    logger.debug("Health check requested")
    return {"status": "ok"}


@app.post("/api/refresh")
async def refresh(
    session: AsyncSession = Depends(get_db_session),
):
    logger.info("Manual refresh triggered")
    await sync_creators_from_config(session)
    result = await session.execute(select(Creator).where(Creator.is_active == True))
    active_creators = result.scalars().all()
    counts = {}
    for creator in active_creators:
        count = await ingest_creator_posts(creator, session, posts_limit=posts_per_creator)
        counts[creator.username] = count
    await session.commit()
    logger.info("Manual refresh complete: {}", counts)
    return {"ingested": counts}
