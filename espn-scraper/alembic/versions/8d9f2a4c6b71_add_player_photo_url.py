"""add ESPN player photo URL

Revision ID: 8d9f2a4c6b71
Revises: 7e2f6e4c1a2b
Create Date: 2026-08-29

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8d9f2a4c6b71"
down_revision: Union[str, Sequence[str], None] = "7e2f6e4c1a2b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("players", sa.Column("photo_url", sa.String(length=500), nullable=True))


def downgrade() -> None:
    op.drop_column("players", "photo_url")
