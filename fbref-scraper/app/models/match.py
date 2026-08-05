from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Match(Base):
    """Modelo de partida de futebol."""

    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    home_team_id = Column(Integer, ForeignKey("teams.id"), index=True)
    away_team_id = Column(Integer, ForeignKey("teams.id"), index=True)
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
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    stats = relationship("MatchStats", back_populates="match", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Match(id={self.id}, {self.home_team_id} vs {self.away_team_id})>"