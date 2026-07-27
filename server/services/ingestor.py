import asyncio
import os
from datetime import datetime, timezone
from typing import Optional

import instaloader
from geoalchemy2 import WKTElement
from loguru import logger
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Creator, InstagramPost, FoodPlace

from .extractor import extract_from_caption
from .geocoder import geocode_location


def _parse_instaloader_timestamp(post) -> Optional[datetime]:
    if post.date_utc:
        return post.date_utc.replace(tzinfo=timezone.utc)
    return None


def _media_type_str(post) -> str:
    if post.typename == "GraphImage":
        return "image"
    elif post.typename == "GraphVideo":
        return "video"
    elif post.typename == "GraphSidecar":
        return "carousel"
    return "image"


def _fetch_profile_posts(username: str, session_id: Optional[str], posts_limit: int) -> list[dict]:
    L = instaloader.Instaloader()
    
    if session_id:
        L.context._session.cookies.set("sessionid", session_id, domain=".instagram.com")
    logger.debug("Fetching instaloader profile from {}", username)
    profile = instaloader.Profile.from_username(L.context, username)
    
    results = []
    for i, post in enumerate(profile.get_posts()):
        if i >= posts_limit:
            break
        
        logger.debug("Fetching post: {}", f"https://www.instagram.com/p/{post.shortcode}/")
        results.append({
            "shortcode": post.shortcode,
            "caption": post.caption if post.caption else None,
            "image_url": post.url,
            "post_url": f"https://www.instagram.com/p/{post.shortcode}/",
            "taken_at": _parse_instaloader_timestamp(post),
            "media_type": _media_type_str(post),
            "raw_json": {
                "typename": post.typename,
                "likes": post.likes if hasattr(post, "likes") else None,
                "comments": post.comments if hasattr(post, "comments") else None,
                "is_video": post.is_video if hasattr(post, "is_video") else None,
            },
        })
    return results


async def ingest_creator_posts(creator: Creator, session: AsyncSession, posts_limit: int = 10) -> int:
    username = creator.username
    logger.info("Starting ingestion for creator: {}", username)

    session_id = os.getenv("INSTAGRAM_SESSION_ID")
    posts_data = await asyncio.to_thread(_fetch_profile_posts, username, session_id, posts_limit)

    ingest_count = 0
    for data in posts_data:
        shortcode = data["shortcode"]

        existing = await session.execute(
            select(InstagramPost).where(InstagramPost.shortcode == shortcode)
        )
        if existing.scalar_one_or_none():
            logger.debug("Skipping existing post: {}", shortcode)
            continue

        db_post = InstagramPost(
            shortcode=shortcode,
            creator_id=creator.id,
            caption=data["caption"],
            image_url=data["image_url"],
            post_url=data["post_url"],
            taken_at=data["taken_at"],
            media_type=data["media_type"],
            raw_json=data["raw_json"],
        )
        session.add(db_post)
        await session.flush()

        place_name = None
        address = None
        cuisine_tags = None

        if data["caption"]:
            extracted = await extract_from_caption(data["caption"])
            place_name = extracted.get("place_name")
            address = extracted.get("address")
            cuisine_tags = extracted.get("cuisine")

        lat, lng = None, None
        if place_name:
            lat, lng, geocoded_address = await geocode_location(f"{place_name}, Singapore")
            if not address:
                address = geocoded_address

        if place_name and lat is not None and lng is not None:
            geom_wkt = WKTElement(f"POINT({lng} {lat})", srid=4326)
            place_stmt = pg_insert(FoodPlace).values(
                name=place_name,
                address=address,
                geom=geom_wkt,
                cuisine_tags=cuisine_tags,
                source_post_id=db_post.id,
            ).on_conflict_do_nothing(
                index_elements=["name"]
            )
            await session.execute(place_stmt)

        ingest_count += 1
        logger.debug("Ingested post {} by {}: place={}", shortcode, username, place_name)

    creator.last_checked_at = datetime.now(timezone.utc)
    logger.info("Finished ingestion for {}: {} new posts", username, ingest_count)
    return ingest_count
