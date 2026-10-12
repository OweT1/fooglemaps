from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from geoalchemy2 import Geometry, functions as geo_func
from loguru import logger
from sqlalchemy import cast, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from commons.db import get_db_session
from telepromos.models import Deal, DealPost
from telepromos.schemas import (
    DealDetail,
    GeoJSONFeature,
    GeoJSONFeatureCollection,
    GeoJSONGeometry,
)

router = APIRouter(tags=["deals"])

_geom_as_geometry = cast(
    Deal.geom,
    Geometry(geometry_type="POINT", srid=4326, spatial_index=False),
)


@router.get("/", response_model=GeoJSONFeatureCollection)
async def list_deals(
    active_only: bool = Query(True),
    bbox: str = Query(None, description="minLng,minLat,maxLng,maxLat"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    session: AsyncSession = Depends(get_db_session),
):
    logger.debug(
        "Listing deals: active_only={}, bbox={}, limit={}, offset={}",
        active_only,
        bbox,
        limit,
        offset,
    )

    stmt = select(
        Deal.id,
        Deal.title,
        Deal.venue_name,
        Deal.address,
        geo_func.ST_Y(_geom_as_geometry).label("lat"),
        geo_func.ST_X(_geom_as_geometry).label("lng"),
        Deal.discount_text,
        Deal.pct_off,
        Deal.valid_from,
        Deal.valid_until,
        Deal.source_post_id,
    )

    if active_only:
        from datetime import datetime, timezone

        now = datetime.now(timezone.utc)
        stmt = stmt.where(
            or_(
                Deal.valid_until.is_(None),
                Deal.valid_until >= now,
            )
        )
        stmt = stmt.where(
            or_(
                Deal.valid_from.is_(None),
                Deal.valid_from <= now,
            )
        )

    if bbox:
        parts = [float(p) for p in bbox.split(",")]
        if len(parts) != 4:
            raise HTTPException(status_code=400, detail="bbox must be minLng,minLat,maxLng,maxLat")
        min_lng, min_lat, max_lng, max_lat = parts
        envelope = geo_func.ST_MakeEnvelope(min_lng, min_lat, max_lng, max_lat, 4326)
        stmt = stmt.where(geo_func.ST_Within(_geom_as_geometry, envelope))

    stmt = (
        stmt.order_by(Deal.valid_until.asc().nullslast(), Deal.created_at.desc())
        .limit(limit)
        .offset(offset)
    )

    result = await session.execute(stmt)
    rows = result.all()

    features = []
    for row in rows:
        if row.lat is None or row.lng is None:
            continue
        features.append(
            GeoJSONFeature(
                geometry=GeoJSONGeometry(coordinates=[float(row.lng), float(row.lat)]),
                properties={
                    "id": str(row.id),
                    "title": row.title,
                    "venue_name": row.venue_name,
                    "address": row.address,
                    "discount_text": row.discount_text,
                    "pct_off": row.pct_off,
                    "valid_from": row.valid_from.isoformat() if row.valid_from else None,
                    "valid_until": row.valid_until.isoformat() if row.valid_until else None,
                    "source_post_id": str(row.source_post_id) if row.source_post_id else None,
                },
            )
        )

    return GeoJSONFeatureCollection(features=features)


@router.get("/{deal_id}", response_model=DealDetail)
async def get_deal(deal_id: str, session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(
        select(Deal, DealPost.shortcode)
        .outerjoin(DealPost, DealPost.id == Deal.source_post_id)
        .where(Deal.id == UUID(deal_id))
    )
    row = result.first()
    if not row:
        raise HTTPException(status_code=404, detail="Deal not found")
    deal, source_shortcode = row

    lat, lng = None, None
    if deal.geom:
        coord_result = await session.execute(
            select(
                geo_func.ST_Y(_geom_as_geometry).label("lat"),
                geo_func.ST_X(_geom_as_geometry).label("lng"),
            ).where(Deal.id == deal.id)
        )
        coord_row = coord_result.one()
        lng, lat = float(coord_row.lng), float(coord_row.lat)

    return DealDetail(
        id=str(deal.id),
        title=deal.title,
        description=deal.description,
        venue_name=deal.venue_name,
        address=deal.address,
        lat=lat,
        lng=lng,
        discount_text=deal.discount_text,
        pct_off=deal.pct_off,
        valid_from=deal.valid_from,
        valid_until=deal.valid_until,
        terms=deal.terms,
        source_post_id=str(deal.source_post_id) if deal.source_post_id else None,
        source_post_url=(
            f"https://www.instagram.com/p/{source_shortcode}/" if source_shortcode else None
        ),
        created_at=deal.created_at,
    )