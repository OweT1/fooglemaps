import asyncio
from contextlib import asynccontextmanager

import commons.logger  # noqa: F401  (configures loguru)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from commons import settings
from commons.db import get_session_factory, close_session_factory
from telepromos.routers import deals_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up TelePromos server")
    await get_session_factory()
    yield
    logger.info("Shutting down TelePromos server")
    await close_session_factory()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.telepromos_cors_origin],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(deals_router, prefix="/api/deals")


@app.get("/health")
async def health():
    logger.debug("TelePromos health check requested")
    return {"status": "ok"}