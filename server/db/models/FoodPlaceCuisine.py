from uuid import UUID

from sqlalchemy import ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .Base import Base


class FoodPlaceCuisine(Base):
    __tablename__ = "food_place_cuisines"

    place_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("food_places.id", ondelete="CASCADE"),
        primary_key=True,
    )
    cuisine_name: Mapped[str] = mapped_column(
        String(100),
        ForeignKey("cuisines.name", ondelete="RESTRICT"),
        primary_key=True,
    )

    place: Mapped["FoodPlace"] = relationship(back_populates="cuisines")
