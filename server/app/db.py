import os
from loguru import logger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

engine = None
session_factory = None


def get_database_url() -> str:
    try:
        if os.environ.get("POSTGRES_URL"):
            return os.environ["POSTGRES_URL"]
        else:
            user = os.environ["POSTGRES_USER"]
            password = os.environ["POSTGRES_PASSWORD"]
            host = os.environ.get("POSTGRES_HOST", "localhost")
            port = os.environ.get("POSTGRES_PORT", "5432")
            db = os.environ["POSTGRES_DB"]
            return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
    except KeyError as e:
        logger.error("Please set either 'POSTGRES_URL' or the respective 'POSTGRES' environmental variables.")
        raise e
    except Exception as e:
        logger.error("Unable to fetch database url: {}", e)
        raise e


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
