from fastapi import APIRouter, Depends
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commons import settings
from commons.db import get_db_session
from telepromos.models import DealSource
from telepromos.services import ingest_source_posts, sync_deal_sources_from_config

router = APIRouter(tags=["refresh"])


@router.post("")
async def refresh(session: AsyncSession = Depends(get_db_session)):
    logger.info("Manual TelePromos refresh triggered")
    await sync_deal_sources_from_config(session)
    result = await session.execute(select(DealSource).where(DealSource.is_active == True))
    active_sources = result.scalars().all()
    counts = {}
    for source in active_sources:
        counts[source.username] = await ingest_source_posts(
            source, session, posts_limit=settings.posts_per_creator
        )
    await session.commit()
    logger.info("Manual TelePromos refresh complete: {}", counts)
    return {"ingested": counts}