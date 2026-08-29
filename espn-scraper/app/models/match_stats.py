from sqlalchemy import CheckConstraint, Column, Integer, String, Float, DateTime, ForeignKey, Boolean, UniqueConstraint
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class MatchStats(Base):
    """Modelo de estatísticas de partida."""

    __tablename__ = "match_stats"

    __table_args__ = (
        UniqueConstraint("match_id", "team_id", name="uq_match_stats_match_team"),
        CheckConstraint(
            "(possession IS NULL OR (possession >= 0 AND possession <= 100)) AND "
            "(pass_accuracy IS NULL OR (pass_accuracy >= 0 AND pass_accuracy <= 100))",
            name="ck_match_stats_percentages",
        ),
        CheckConstraint(
            "(xg IS NULL OR xg >= 0) AND "
            "(xg_against IS NULL OR xg_against >= 0)",
            name="ck_match_stats_non_negative_xg",
        ),
        CheckConstraint(
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
            name="ck_match_stats_non_negative_counts",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False, index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    is_home = Column(Boolean, default=False, nullable=False)

    # Estatísticas gerais
    possession = Column(Float)
    shots = Column(Integer)
    shots_on_target = Column(Integer)
    corners = Column(Integer)
    fouls = Column(Integer)
    yellow_cards = Column(Integer)
    red_cards = Column(Integer)
    offsides = Column(Integer)

    # Estatísticas avançadas
    xg = Column(Float)
    xg_against = Column(Float)
    passes = Column(Integer)
    pass_accuracy = Column(Float)
    tackles = Column(Integer)
    interceptions = Column(Integer)
    saves = Column(Integer)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relacionamentos
    match = relationship("Match", back_populates="stats")
    team = relationship("Team")

    def __repr__(self):
        return f"<MatchStats(id={self.id}, match_id={self.match_id}, team_id={self.team_id})>"
