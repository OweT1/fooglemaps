import uuid
from datetime import datetime
from typing import Optional

from geoalchemy2 import Geography
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from commons.db import Base


class Deal(Base):
    __tablename__ = "deals"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    venue_name: Mapped[str] = mapped_column(String(500), nullable=False)
    address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    geom: Mapped[Optional[str]] = mapped_column(
        Geography(geometry_type="POINT", srid=4326), nullable=True
    )
    discount_text: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    pct_off: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    valid_from: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    valid_until: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_post_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("deal_posts.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    source_post: Mapped[Optional["DealPost"]] = relationship(back_populates="deals")