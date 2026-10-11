"""Create TelePromos tables (deal_sources, deal_posts, deals, telegram_users)

Revision ID: 0005
Revises: 0004
Create Date: 2026-10-11 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geography

revision: str = "0005"
down_revision: Union[str, None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "deal_sources",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("username", sa.String(255), unique=True, nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_checked_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    op.create_table(
        "deal_posts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("source_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("deal_sources.id", ondelete="CASCADE"), nullable=False),
        sa.Column("shortcode", sa.String(255), unique=True, nullable=False),
        sa.Column("caption", sa.Text(), nullable=True),
        sa.Column("raw_json", postgresql.JSONB, nullable=True),
        sa.Column("taken_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_deal_posts_shortcode", "deal_posts", ["shortcode"])

    op.create_table(
        "deals",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("venue_name", sa.String(500), nullable=False),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("geom", Geography(geometry_type="POINT", srid=4326), nullable=True),
        sa.Column("discount_text", sa.Text(), nullable=True),
        sa.Column("pct_off", sa.Integer(), nullable=True),
        sa.Column("valid_from", sa.DateTime(timezone=True), nullable=True),
        sa.Column("valid_until", sa.DateTime(timezone=True), nullable=True),
        sa.Column("terms", sa.Text(), nullable=True),
        sa.Column("source_post_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("deal_posts.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_deals_geom", "deals", ["geom"], postgresql_using="gist")
    op.create_index("ix_deals_valid_until", "deals", ["valid_until"])

    op.create_table(
        "telegram_users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("telegram_id", sa.BigInteger(), unique=True, nullable=False),
        sa.Column("chat_id", sa.BigInteger(), nullable=True),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("first_name", sa.String(255), nullable=True),
        sa.Column("notify_enabled", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_telegram_users_telegram_id", "telegram_users", ["telegram_id"])


def downgrade() -> None:
    op.drop_index("ix_telegram_users_telegram_id", table_name="telegram_users")
    op.drop_table("telegram_users")
    op.drop_index("ix_deals_valid_until", table_name="deals")
    op.drop_index("ix_deals_geom", table_name="deals")
    op.drop_table("deals")
    op.drop_index("ix_deal_posts_shortcode", table_name="deal_posts")
    op.drop_table("deal_posts")
    op.drop_table("deal_sources")