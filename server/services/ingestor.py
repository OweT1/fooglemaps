from datetime import datetime, timezone

from geoalchemy2 import WKTElement
from loguru import logger
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from db import Creator, InstagramPost, FoodPlace
from services import get_instagram_client

from .extractor import extract_from_caption
from .geocoder import geocode_location


async def ingest_creator_posts(creator: Creator, session: AsyncSession, posts_limit: int = 10) -> int:
    username = creator.username
    logger.info("Starting ingestion for creator: {}", username)

    client = await get_instagram_client()
    posts_data = await client.fetch_user_posts(username, posts_limit=posts_limit)

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

        place_name = data.get("location_name")
        address = None
        cuisine_tags = None

        if data["caption"]:
            extracted = await extract_from_caption(data["caption"])
            if not place_name:
                place_name = extracted.get("place_name")
            address = extracted.get("address")
            cuisine_tags = extracted.get("cuisine")

        lat = data.get("lat")
        lng = data.get("lng")
        if lat is None or lng is None:
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
