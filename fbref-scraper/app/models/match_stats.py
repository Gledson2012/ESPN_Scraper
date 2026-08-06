from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class MatchStats(Base):
    """Modelo de estatísticas de partida."""

    __tablename__ = "match_stats"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), index=True)
    team_id = Column(Integer, ForeignKey("teams.id"), index=True)
    is_home = Column(Boolean, default=False)

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