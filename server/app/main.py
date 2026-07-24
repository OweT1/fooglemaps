import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

dotenv_path = os.path.join(os.path.dirname(__file__), "..", "..", ".env")
load_dotenv(dotenv_path)

from .db import get_session_factory, close_session_factory
from .routers import auth, settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    await get_session_factory()
    yield
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
    return {"status": "ok"}
