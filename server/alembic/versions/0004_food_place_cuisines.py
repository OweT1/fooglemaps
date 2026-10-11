"""Move food_places.cuisine_tags from a free-text array to a food_place_cuisines join table

Existing array values are matched case-insensitively against cuisines.name; values
with no match are dropped, since the join table's FK cannot represent them.

Revision ID: 0004
Revises: 0003
Create Date: 2026-10-05 00:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: Union[str, None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "food_place_cuisines",
        sa.Column("place_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("cuisine_name", sa.String(100), nullable=False),
        sa.ForeignKeyConstraint(
            ["place_id"],
            ["food_places.id"],
            name="fk_food_place_cuisines_place_id",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["cuisine_name"],
            ["cuisines.name"],
            name="fk_food_place_cuisines_cuisine_name",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("place_id", "cuisine_name"),
    )
    op.create_index(
        "ix_food_place_cuisines_cuisine_name",
        "food_place_cuisines",
        ["cuisine_name"],
    )

    op.execute(
        """
        INSERT INTO food_place_cuisines (place_id, cuisine_name)
        SELECT DISTINCT fp.id, c.name
        FROM food_places fp
        CROSS JOIN LATERAL unnest(fp.cuisine_tags) AS tag
        JOIN cuisines c ON lower(c.name) = lower(tag)
        WHERE fp.cuisine_tags IS NOT NULL
        ON CONFLICT DO NOTHING
        """
    )

    op.drop_column("food_places", "cuisine_tags")


def downgrade() -> None:
    op.add_column(
        "food_places",
        sa.Column("cuisine_tags", postgresql.ARRAY(sa.String()), nullable=True),
    )

    op.execute(
        """
        UPDATE food_places fp
        SET cuisine_tags = agg.tags
        FROM (
            SELECT place_id, array_agg(cuisine_name ORDER BY cuisine_name) AS tags
            FROM food_place_cuisines
            GROUP BY place_id
        ) agg
        WHERE agg.place_id = fp.id
        """
    )

    op.drop_index("ix_food_place_cuisines_cuisine_name", table_name="food_place_cuisines")
    op.drop_table("food_place_cuisines")
