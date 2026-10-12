import asyncio
from contextlib import asynccontextmanager

import commons.logger  # noqa: F401  (configures loguru)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commons import settings
from commons.db import get_session_factory, close_session_factory
from commons.instagram import close_instagram_client
from telepromos.models import Deal, DealSource
from telepromos.notifier import notify_new_deals
from telepromos.routers import deals_router, me_router, refresh_router, telegram_router
from telepromos.services import ingest_source_posts, sync_deal_sources_from_config

poll_interval_minutes = settings.poll_interval_minutes
posts_per_creator = settings.posts_per_creator
_scheduler_task = None


async def deals_ingestion_loop() -> None:
    logger.info("TelePromos deals ingestion scheduler started (interval={}min)", poll_interval_minutes)
    while True:
        try:
            factory = await get_session_factory()
            async with factory() as session:
                await sync_deal_sources_from_config(session)
                result = await session.execute(
                    select(DealSource).where(DealSource.is_active == True)
                )
                active_sources = result.scalars().all()
                new_deals: list[Deal] = []
                if active_sources:
                    logger.info("Scheduled deal ingestion for {} source(s)", len(active_sources))
                    for source in active_sources:
                        new_deals.extend(
                            await ingest_source_posts(source, session, posts_limit=posts_per_creator)
                        )
                await session.commit()
                if new_deals:
                    await notify_new_deals(session, new_deals)
        except Exception as e:
            logger.error("TelePromos deals ingestion loop error: {}", e)
        await asyncio.sleep(poll_interval_minutes * 60)


@asynccontextmanager
async def lifespan(app: FastAPI):
    global _scheduler_task
    logger.info("Starting up TelePromos server")
    await get_session_factory()
    _scheduler_task = asyncio.create_task(deals_ingestion_loop())
    yield
    logger.info("Shutting down TelePromos server")
    if _scheduler_task and not _scheduler_task.done():
        _scheduler_task.cancel()
        try:
            await _scheduler_task
        except asyncio.CancelledError:
            pass
    await close_instagram_client()
    await close_session_factory()


app = FastAPI(
    title="TelePromos API",
    version="0.1.0",
    lifespan=lifespan,
    description=(
        "Backend for TelePromos, the Telegram Mini App for Singapore food deals. "
        "Deals are scraped from Instagram via instagrapi, extracted with an LLM, "
        "and geocoded to PostGIS points.\n\n"
        "Interactive docs: [/docs](/docs) (Swagger UI) and [/redoc](/redoc)."
    ),
    openapi_tags=[
        {"name": "deals", "description": "Food deals listing and detail (GeoJSON for the map)."},
        {"name": "refresh", "description": "Manual ingestion trigger for deal sources."},
    ],
    swagger_ui_parameters={
        "docExpansion": "none",
        "filter": True,
        "defaultModelsExpandDepth": -1,
    },
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.telepromos_cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deals_router, prefix="/api/deals")
app.include_router(me_router)
app.include_router(refresh_router, prefix="/api/refresh")
app.include_router(telegram_router)


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse("/docs")


@app.get("/health")
async def health():
    logger.debug("TelePromos health check requested")
    return {"status": "ok"}