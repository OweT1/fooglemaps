from fastapi import APIRouter, Depends, HTTPException, Query
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils import get_db_session
from db import InstagramPostResponse, InstagramPost

router = APIRouter()


@router.get("/", response_model=list[InstagramPostResponse])
async def list_posts(
    creator_id: str = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    logger.debug("Listing posts: creator_id={}, limit={}, offset={}", creator_id, limit, offset)
    stmt = select(InstagramPost).order_by(InstagramPost.taken_at.desc().nullslast()).limit(limit).offset(offset)
    if creator_id:
        from uuid import UUID
        stmt = stmt.where(InstagramPost.creator_id == UUID(creator_id))
    result = await session.execute(stmt)
    posts = result.scalars().all()
    return [
        InstagramPostResponse(
            id=str(p.id),
            shortcode=p.shortcode,
            creator_id=str(p.creator_id),
            caption=p.caption,
            image_url=p.image_url,
            post_url=p.post_url,
            taken_at=p.taken_at,
            media_type=p.media_type,
            created_at=p.created_at,
        )
        for p in posts
    ]


@router.get("/{post_id}", response_model=InstagramPostResponse)
async def get_post(post_id: str, session: AsyncSession = Depends(get_db_session)):
    from uuid import UUID
    result = await session.execute(select(InstagramPost).where(InstagramPost.id == UUID(post_id)))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Post not found")
    return InstagramPostResponse(
        id=str(p.id),
        shortcode=p.shortcode,
        creator_id=str(p.creator_id),
        caption=p.caption,
        post_url=p.post_url,
        taken_at=p.taken_at,
        media_type=p.media_type,
        created_at=p.created_at,
    )
