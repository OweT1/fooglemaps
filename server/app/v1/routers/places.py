from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from geoalchemy2 import Geometry, functions as geo_func
from loguru import logger
from sqlalchemy import cast, select
from sqlalchemy.ext.asyncio import AsyncSession

from utils import get_db_session
from db import GeoJSONFeature, GeoJSONFeatureCollection, GeoJSONGeometry, PlaceResponse, FoodPlace, FoodPlaceCuisine

router = APIRouter()

_geom_as_geometry = cast(FoodPlace.geom, Geometry(geometry_type="POINT", srid=4326, spatial_index=False))


@router.get("/")
async def list_places(session: AsyncSession = Depends(get_db_session)):
    logger.debug("Listing food places as GeoJSON")
    result = await session.execute(
        select(
            FoodPlace.id,
            FoodPlace.name,
            FoodPlace.address,
            geo_func.ST_Y(_geom_as_geometry).label("lat"),
            geo_func.ST_X(_geom_as_geometry).label("lng"),
            FoodPlace.source_post_id,
            FoodPlace.created_at,
        )
    )
    rows = result.all()

    cuisines_by_place: dict[str, list[str]] = {}
    if rows:
        cuisine_result = await session.execute(
            select(FoodPlaceCuisine.place_id, FoodPlaceCuisine.cuisine_name)
            .where(FoodPlaceCuisine.place_id.in_([row.id for row in rows]))
            .order_by(FoodPlaceCuisine.cuisine_name)
        )
        for place_id, cuisine_name in cuisine_result.all():
            cuisines_by_place.setdefault(str(place_id), []).append(cuisine_name)

    features = []
    for row in rows:
        if row.lat is None or row.lng is None:
            continue
        features.append(GeoJSONFeature(
            geometry=GeoJSONGeometry(coordinates=[float(row.lng), float(row.lat)]),
            properties={
                "id": str(row.id),
                "name": row.name,
                "address": row.address,
                "cuisine_tags": cuisines_by_place.get(str(row.id), []),
                "source_post_id": str(row.source_post_id) if row.source_post_id else None,
            },
        ))

    return GeoJSONFeatureCollection(features=features)


@router.get("/{place_id}")
async def get_place(place_id: str, session: AsyncSession = Depends(get_db_session)):
    result = await session.execute(select(FoodPlace).where(FoodPlace.id == UUID(place_id)))
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Place not found")

    lat, lng = None, None
    if p.geom:
        coord_result = await session.execute(
            select(
                geo_func.ST_Y(_geom_as_geometry).label("lat"),
                geo_func.ST_X(_geom_as_geometry).label("lng"),
            ).where(FoodPlace.id == p.id)
        )
        coord_row = coord_result.one()
        lng, lat = float(coord_row.lng), float(coord_row.lat)

    return PlaceResponse(
        id=str(p.id),
        name=p.name,
        address=p.address,
        lat=lat,
        lng=lng,
        cuisine_tags=sorted(link.cuisine_name for link in p.cuisines),
        source_post_id=str(p.source_post_id) if p.source_post_id else None,
        created_at=p.created_at,
    )
