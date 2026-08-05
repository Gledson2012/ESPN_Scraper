from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime

from app.database import Base


class Team(Base):
    """Modelo de time de futebol."""

    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    short_name = Column(String(50))
    country = Column(String(100))
    league = Column(String(100), index=True)
    stadium = Column(String(255))
    founded = Column(Integer)
    website = Column(String(255))
    fbref_id = Column(String(50), unique=True, index=True)
    logo_url = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    players = relationship("Player", back_populates="team")

    def __repr__(self):
        return f"<Team(id={self.id}, name={self.name})>"