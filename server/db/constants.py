import uuid
from typing import Optional
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
