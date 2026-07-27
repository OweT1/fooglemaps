import uuid
from datetime import datetime
from typing import Any, Optional
from pydantic import BaseModel

class UserResponse(BaseModel):
    id: str
    sub: str
    email: str
    name: str
    picture: Optional[str] = None


class SettingsResponse(BaseModel):
    id: str
    user_id: str
    theme: str
    default_zoom: int
    map_type: str
    notify_new_spots: bool
    notify_recommendations: bool


class LoginResponse(BaseModel):
    user: UserResponse
    settings: SettingsResponse


class SettingsUpdate(BaseModel):
    theme: Optional[str] = None
    default_zoom: Optional[int] = None
    map_type: Optional[str] = None
    notify_new_spots: Optional[bool] = None
    notify_recommendations: Optional[bool] = None


class CreatorResponse(BaseModel):
    id: str
    username: str
    is_active: bool
    last_checked_at: Optional[datetime] = None
    created_at: datetime


class InstagramPostResponse(BaseModel):
    id: str
    shortcode: str
    creator_id: str
    caption: Optional[str] = None
    image_url: Optional[str] = None
    post_url: Optional[str] = None
    taken_at: Optional[datetime] = None
    media_type: Optional[str] = None
    created_at: datetime


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


class PlaceResponse(BaseModel):
    id: str
    name: str
    address: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    cuisine_tags: Optional[list[str]] = None
    source_post_id: Optional[str] = None
    created_at: datetime
