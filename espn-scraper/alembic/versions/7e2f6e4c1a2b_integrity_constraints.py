"""add integrity constraints for matches and match statistics

Revision ID: 7e2f6e4c1a2b
Revises: 2951e956d4d8
Create Date: 2026-08-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "7e2f6e4c1a2b"
down_revision: Union[str, Sequence[str], None] = "2951e956d4d8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Make match references mandatory and prevent invalid duplicate stats."""
    op.alter_column(
        "matches",
        "home_team_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "matches",
        "away_team_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "match_stats",
        "match_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "match_stats",
        "team_id",
        existing_type=sa.Integer(),
        nullable=False,
    )
    op.alter_column(
        "match_stats",
        "is_home",
        existing_type=sa.Boolean(),
        nullable=False,
    )

    op.create_check_constraint(
        "ck_matches_different_teams",
        "matches",
        "home_team_id <> away_team_id",
    )
    op.create_check_constraint(
        "ck_matches_non_negative_scores",
        "matches",
        "(home_score IS NULL OR home_score >= 0) AND "
        "(away_score IS NULL OR away_score >= 0)",
    )
    op.create_check_constraint(
        "ck_matches_non_negative_xg",
        "matches",
        "(home_xg IS NULL OR home_xg >= 0) AND "
        "(away_xg IS NULL OR away_xg >= 0)",
    )
    op.create_check_constraint(
        "ck_match_stats_percentages",
        "match_stats",
        "(possession IS NULL OR (possession >= 0 AND possession <= 100)) AND "
        "(pass_accuracy IS NULL OR (pass_accuracy >= 0 AND pass_accuracy <= 100))",
    )
    op.create_check_constraint(
        "ck_match_stats_non_negative_xg",
        "match_stats",
        "(xg IS NULL OR xg >= 0) AND "
        "(xg_against IS NULL OR xg_against >= 0)",
    )
    op.create_check_constraint(
        "ck_match_stats_non_negative_counts",
        "match_stats",
        "(shots IS NULL OR shots >= 0) AND "
        "(shots_on_target IS NULL OR shots_on_target >= 0) AND "
        "(corners IS NULL OR corners >= 0) AND "
        "(fouls IS NULL OR fouls >= 0) AND "
        "(yellow_cards IS NULL OR yellow_cards >= 0) AND "
        "(red_cards IS NULL OR red_cards >= 0) AND "
        "(offsides IS NULL OR offsides >= 0) AND "
        "(passes IS NULL OR passes >= 0) AND "
        "(tackles IS NULL OR tackles >= 0) AND "
        "(interceptions IS NULL OR interceptions >= 0) AND "
        "(saves IS NULL OR saves >= 0)",
    )
    op.create_unique_constraint(
        "uq_match_stats_match_team",
        "match_stats",
        ["match_id", "team_id"],
    )


def downgrade() -> None:
    """Remove the integrity constraints."""
    op.drop_constraint("uq_match_stats_match_team", "match_stats", type_="unique")
    op.drop_constraint("ck_match_stats_non_negative_counts", "match_stats", type_="check")
    op.drop_constraint("ck_match_stats_non_negative_xg", "match_stats", type_="check")
    op.drop_constraint("ck_match_stats_percentages", "match_stats", type_="check")
    op.drop_constraint("ck_matches_non_negative_xg", "matches", type_="check")
    op.drop_constraint("ck_matches_non_negative_scores", "matches", type_="check")
    op.drop_constraint("ck_matches_different_teams", "matches", type_="check")

    op.alter_column(
        "match_stats",
        "is_home",
        existing_type=sa.Boolean(),
        nullable=True,
    )
    op.alter_column(
        "match_stats",
        "team_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "match_stats",
        "match_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "matches",
        "away_team_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
    op.alter_column(
        "matches",
        "home_team_id",
        existing_type=sa.Integer(),
        nullable=True,
    )
