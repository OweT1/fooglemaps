from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2 import functions as geo_func
from loguru import logger
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from utils import get_db_session
from db import GeoJSONFeature, GeoJSONFeatureCollection, GeoJSONGeometry, PlaceResponse, FoodPlace

router = APIRouter()


@router.get("/")
async def list_places(session: AsyncSession = Depends(get_db_session)):
    logger.debug("Listing food places as GeoJSON")
    result = await session.execute(
        select(
            FoodPlace.id,
            FoodPlace.name,
            FoodPlace.address,
            FoodPlace.geom,
            FoodPlace.cuisine_tags,
            FoodPlace.source_post_id,
            FoodPlace.created_at,
        )
    )
    rows = result.all()

    features = []
    for row in rows:
        geom = row.geom
        if geom is None:
            continue
        stmt = text("SELECT ST_X(:geom) AS lng, ST_Y(:geom) AS lat")
        coord_result = await session.execute(stmt, {"geom": geom})
        coord_row = coord_result.one()
        lng, lat = float(coord_row.lng), float(coord_row.lat)

        features.append(GeoJSONFeature(
            geometry=GeoJSONGeometry(coordinates=[lng, lat]),
            properties={
                "id": str(row.id),
                "name": row.name,
                "address": row.address,
                "cuisine_tags": row.cuisine_tags or [],
                "source_post_id": str(row.source_post_id) if row.source_post_id else None,
            },
        ))

    return GeoJSONFeatureCollection(features=features)


@router.get("/{place_id}")
async def get_place(place_id: str, session: AsyncSession = Depends(get_db_session)):
    from uuid import UUID
    result = await session.execute(select(FoodPlace).where(FoodPlace.id == UUID(place_id)))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Place not found")

    lat, lng = None, None
    if p.geom:
        stmt = text("SELECT ST_X(:geom) AS lng, ST_Y(:geom) AS lat")
        coord_result = await session.execute(stmt, {"geom": p.geom})
        row = coord_result.one()
        lng, lat = float(row.lng), float(row.lat)

    return PlaceResponse(
        id=str(p.id),
        name=p.name,
        address=p.address,
        lat=lat,
        lng=lng,
        cuisine_tags=p.cuisine_tags or [],
        source_post_id=str(p.source_post_id) if p.source_post_id else None,
        created_at=p.created_at,
    )
