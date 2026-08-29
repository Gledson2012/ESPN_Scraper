from sqlalchemy import CheckConstraint, Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Match(Base):
    """Modelo de partida de futebol."""

    __tablename__ = "matches"

    __table_args__ = (
        CheckConstraint(
            "home_team_id <> away_team_id",
            name="ck_matches_different_teams",
        ),
        CheckConstraint(
            "(home_score IS NULL OR home_score >= 0) AND "
            "(away_score IS NULL OR away_score >= 0)",
            name="ck_matches_non_negative_scores",
        ),
        CheckConstraint(
            "(home_xg IS NULL OR home_xg >= 0) AND "
            "(away_xg IS NULL OR away_xg >= 0)",
            name="ck_matches_non_negative_xg",
        ),
    )

    id = Column(Integer, primary_key=True, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False, index=True)
    competition = Column(String(100), index=True)
    season = Column(String(20), index=True)
    match_date = Column(DateTime, index=True)
    venue = Column(String(255))
    home_score = Column(Integer)
    away_score = Column(Integer)
    home_xg = Column(Float)
    away_xg = Column(Float)
    attendance = Column(Integer)
    referee = Column(String(100))
    fbref_id = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relacionamentos
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    stats = relationship("MatchStats", back_populates="match", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Match(id={self.id}, {self.home_team_id} vs {self.away_team_id})>"
