from datetime import datetime
from typing import Any, Optional

from pydantic import BaseModel


class DealDetail(BaseModel):
    id: str
    title: str
    description: Optional[str] = None
    venue_name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    discount_text: Optional[str] = None
    pct_off: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    terms: Optional[str] = None
    source_post_id: Optional[str] = None
    source_post_url: Optional[str] = None
    created_at: datetime


class DealListRow(BaseModel):
    id: str
    title: str
    venue_name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    discount_text: Optional[str] = None
    pct_off: Optional[int] = None
    valid_from: Optional[datetime] = None
    valid_until: Optional[datetime] = None
    source_post_id: Optional[str] = None


class GeoJSONGeometry(BaseModel):
    type: str = "Point"
    coordinates: list[float]


class GeoJSONFeature(BaseModel):
    type: str = "Feature"
    geometry: GeoJSONGeometry
    properties: dict[str, Any]


class GeoJSONFeatureCollection(BaseModel):
    type: str = "FeatureCollection"
    features: list[GeoJSONFeature]