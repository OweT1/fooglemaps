from datetime import datetime, timezone

from geoalchemy2 import WKTElement
from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from commons import settings
from commons.geocoder import geocode_location
from commons.instagram import get_instagram_client
from telepromos.models import Deal, DealPost, DealSource

from .deals_extractor import extract_deal_from_caption


async def sync_deal_sources_from_config(session: AsyncSession) -> None:
    raw = settings.instagram_deal_creators
    configured_usernames = {u.strip().lower() for u in raw.split(",") if u.strip()}

    result = await session.execute(select(DealSource))
    all_sources = result.scalars().all()

    existing_usernames = {s.username: s for s in all_sources}

    for username in configured_usernames:
        if username in existing_usernames:
            source = existing_usernames[username]
            if not source.is_active:
                source.is_active = True
                logger.info("Re-activated deal source: {}", username)
        else:
            source = DealSource(username=username, is_active=True)
            session.add(source)
            logger.info("Added deal source from config: {}", username)

    for username, source in existing_usernames.items():
        if username not in configured_usernames and source.is_active:
            source.is_active = False
            logger.info("De-activated deal source (removed from config): {}", username)

    await session.commit()


async def ingest_source_posts(source: DealSource, session: AsyncSession, posts_limit: int = 10) -> list[Deal]:
    username = source.username
    logger.info("Starting deal ingestion for source: {}", username)

    client = await get_instagram_client()
    posts_data = await client.fetch_user_posts(username, posts_limit=posts_limit)

    new_deals: list[Deal] = []
    for data in posts_data:
        shortcode = data["shortcode"]

        existing = await session.execute(
            select(DealPost).where(DealPost.shortcode == shortcode)
        )
        if existing.scalar_one_or_none():
            logger.debug("Skipping existing deal post: {}", shortcode)
            continue

        db_post = DealPost(
            shortcode=shortcode,
            source_id=source.id,
            caption=data["caption"],
            raw_json=data["raw_json"],
            taken_at=data["taken_at"],
        )
        session.add(db_post)
        await session.flush()

        deal_data = {}
        if data["caption"]:
            deal_data = await extract_deal_from_caption(data["caption"])

        venue_name = deal_data.get("venue_name") or data.get("location_name")
        if not venue_name:
            logger.debug("No venue extracted for post {}, skipping deal", shortcode)
            continue

        title = (deal_data.get("title") or venue_name)[:500]
        address = deal_data.get("address")

        lat, lng = data.get("lat"), data.get("lng")
        if lat is None or lng is None:
            if venue_name:
                lat, lng, geocoded_address = await geocode_location(f"{venue_name}, Singapore")
                if not address:
                    address = geocoded_address

        geom = None
        if lat is not None and lng is not None:
            geom = WKTElement(f"POINT({lng} {lat})", srid=4326)

        deal = Deal(
            title=title,
            description=deal_data.get("description"),
            venue_name=venue_name[:500],
            address=address,
            geom=geom,
            discount_text=deal_data.get("discount_text"),
            pct_off=deal_data.get("pct_off"),
            valid_from=deal_data.get("valid_from"),
            valid_until=deal_data.get("valid_until"),
            terms=deal_data.get("terms"),
            source_post_id=db_post.id,
        )
        session.add(deal)
        new_deals.append(deal)
        logger.debug("Ingested deal for post {} by {}: venue={}", shortcode, username, venue_name)

    source.last_checked_at = datetime.now(timezone.utc)
    logger.info("Finished deal ingestion for {}: {} new deals", username, len(new_deals))
    return new_deals