import os
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = None
session_factory = None


def get_database_url() -> str:
    url = os.environ["POSTGRES_URL"]
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)
    return url


async def get_session_factory() -> async_sessionmaker[AsyncSession]:
    global engine, session_factory
    if engine is None:
        db_url = get_database_url()
        logger.info("Creating database engine")
        engine = create_async_engine(db_url, echo=False, pool_size=5, max_overflow=10)
    if session_factory is None:
        session_factory = async_sessionmaker(engine, expire_on_commit=False)
    return session_factory


async def close_session_factory():
    global engine, session_factory
    if engine:
        logger.info("Disposing database engine")
        await engine.dispose()
        engine = None
        session_factory = None
