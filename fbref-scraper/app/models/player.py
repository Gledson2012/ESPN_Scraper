from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime, timezone

from app.database import Base


class Player(Base):
    """Modelo de jogador de futebol."""

    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    full_name = Column(String(255))
    birth_date = Column(DateTime)
    nationality = Column(String(100))
    position = Column(String(50))
    foot = Column(String(10))
    height_cm = Column(Float)
    weight_kg = Column(Float)
    shirt_number = Column(Integer)
    team_id = Column(Integer, ForeignKey("teams.id"), index=True)
    fbref_id = Column(String(50), unique=True, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    # Relacionamentos
    team = relationship("Team", back_populates="players")

    def __repr__(self):
        return f"<Player(id={self.id}, name={self.name})>"