import uuid
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    google_sub: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    avatar_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    settings: Mapped[list["UserSettings"]] = relationship(back_populates="user", cascade="all, delete-orphan")


class UserSettings(Base):
    __tablename__ = "user_settings"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    theme: Mapped[str] = mapped_column(String, nullable=False, default="system")
    default_zoom: Mapped[int] = mapped_column(Integer, nullable=False, default=12)
    map_type: Mapped[str] = mapped_column(String, nullable=False, default="roadmap")
    notify_new_spots: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    notify_recommendations: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="settings")


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
