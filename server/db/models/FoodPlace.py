import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
from geoalchemy2 import Geography

from .Base import Base


class FoodPlace(Base):
    __tablename__ = "food_places"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    name: Mapped[str] = mapped_column(String(500), nullable=False, unique=True)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    geom: Mapped[Optional[str]] = mapped_column(Geography(geometry_type="POINT", srid=4326), nullable=True)
    source_post_id: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("instagram_posts.id", ondelete="SET NULL"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    cuisines: Mapped[list["FoodPlaceCuisine"]] = relationship(
        back_populates="place",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
