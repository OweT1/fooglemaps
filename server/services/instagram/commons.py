from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class InstagramMedia:
    shortcode: str
    caption: Optional[str]
    image_url: Optional[str]
    post_url: str
    taken_at: Optional[datetime]
    media_type: str
    raw_json: dict
    location_name: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    location_external_id: Optional[str] = None


@dataclass
class InstagramUser:
    pk: str
    username: str
    full_name: Optional[str]
    profile_pic_url: Optional[str]
    is_private: bool