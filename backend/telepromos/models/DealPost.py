import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from commons.db import Base


class DealPost(Base):
    __tablename__ = "deal_posts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid()
    )
    source_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("deal_sources.id", ondelete="CASCADE"), nullable=False
    )
    shortcode: Mapped[str] = mapped_column(
        String(255), unique=True, nullable=False, index=True
    )
    caption: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    raw_json: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    taken_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    source: Mapped["DealSource"] = relationship(back_populates="posts")
    deals: Mapped[list["Deal"]] = relationship(back_populates="source_post")