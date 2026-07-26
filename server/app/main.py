import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import utils.logger
from loguru import logger

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path)

from db.session import get_session_factory, close_session_factory
from .v1.routers import auth, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up FoogleMaps server")
    await get_session_factory()
    yield
    logger.info("Shutting down FoogleMaps server")
    await close_session_factory()


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.getenv("CORS_ORIGIN", "http://localhost:5173")],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/auth")
app.include_router(settings.router, prefix="/api/settings")


@app.get("/api/health")
async def health():
    logger.debug("Health check requested")
    return {"status": "ok"}
