"""rename fbref_id columns to espn_id

Revision ID: 4e1a0b2c3d5f
Revises: 8d9f2a4c6b71
Create Date: 2026-08-30

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "4e1a0b2c3d5f"
down_revision: Union[str, Sequence[str], None] = "8d9f2a4c6b71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    for table in ("teams", "matches", "players"):
        op.alter_column(
            table,
            "fbref_id",
            new_column_name="espn_id",
            existing_type=sa.String(length=50),
            existing_nullable=True,
        )
        op.execute(f"ALTER INDEX ix_{table}_fbref_id RENAME TO ix_{table}_espn_id")


def downgrade() -> None:
    for table in ("teams", "matches", "players"):
        op.execute(f"ALTER INDEX ix_{table}_espn_id RENAME TO ix_{table}_fbref_id")
        op.alter_column(
            table,
            "espn_id",
            new_column_name="fbref_id",
            existing_type=sa.String(length=50),
            existing_nullable=True,
        )
