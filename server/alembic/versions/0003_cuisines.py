"""Create cuisines lookup table and seed Singapore-relevant cuisines

Revision ID: 0003
Revises: 0002
Create Date: 2026-10-05 00:00:00.000000

Note: seeds from services.cuisines.CUISINES. Once this revision has shipped,
edit a new revision rather than changing the seed list here.

"""

import sys
from pathlib import Path
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from services.cuisines import CUISINES

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "cuisines",
        sa.Column("name", sa.String(100), primary_key=True),
    )

    cuisines_table = sa.table("cuisines", sa.column("name", sa.String(100)))
    op.bulk_insert(cuisines_table, [{"name": name} for name in CUISINES])


def downgrade() -> None:
    op.drop_table("cuisines")
