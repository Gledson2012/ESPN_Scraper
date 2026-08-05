from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, List

from app.schemas.match_stats import MatchStatsResponse


class MatchBase(BaseModel):
    """Modelo base de uma partida de futebol."""

    home_team_id: int = Field(..., description="ID do time da casa", examples=[1])
    away_team_id: int = Field(..., description="ID do time visitante", examples=[2])
    competition: Optional[str] = Field(None, description="Competição", examples=["Serie-A"])
    season: Optional[str] = Field(None, description="Temporada", examples=["2024-2025"])
    match_date: Optional[datetime] = Field(None, description="Data da partida", examples=["2025-03-15T20:00:00"])
    venue: Optional[str] = Field(None, description="Local da partida", examples=["Maracanã"])
    home_score: Optional[int] = Field(None, description="Gols do time da casa", examples=[2])
    away_score: Optional[int] = Field(None, description="Gols do time visitante", examples=[1])
    home_xg: Optional[float] = Field(None, description="xG do time da casa", examples=[1.85])
    away_xg: Optional[float] = Field(None, description="xG do time visitante", examples=[0.92])
    attendance: Optional[int] = Field(None, description="Público presente", examples=[65000])
    referee: Optional[str] = Field(None, description="Árbitro da partida", examples=["Anderson Daronco"])
    fbref_id: Optional[str] = Field(None, description="ID da partida no FBref", examples=["abc123"])


class MatchCreate(MatchBase):
    """Dados para criar uma nova partida."""


class MatchUpdate(BaseModel):
    """Dados para atualizar uma partida existente."""

    home_team_id: Optional[int] = Field(None, description="ID do time da casa", examples=[1])
    away_team_id: Optional[int] = Field(None, description="ID do time visitante", examples=[2])
    competition: Optional[str] = Field(None, description="Competição", examples=["Serie-A"])
    season: Optional[str] = Field(None, description="Temporada", examples=["2024-2025"])
    match_date: Optional[datetime] = Field(None, description="Data da partida", examples=["2025-03-15T20:00:00"])
    venue: Optional[str] = Field(None, description="Local da partida", examples=["Maracanã"])
    home_score: Optional[int] = Field(None, description="Gols do time da casa", examples=[2])
    away_score: Optional[int] = Field(None, description="Gols do time visitante", examples=[1])
    home_xg: Optional[float] = Field(None, description="xG do time da casa", examples=[1.85])
    away_xg: Optional[float] = Field(None, description="xG do time visitante", examples=[0.92])
    attendance: Optional[int] = Field(None, description="Público presente", examples=[65000])
    referee: Optional[str] = Field(None, description="Árbitro da partida", examples=["Anderson Daronco"])
    fbref_id: Optional[str] = Field(None, description="ID da partida no FBref", examples=["abc123"])


class MatchResponse(MatchBase):
    """Resposta com dados de uma partida."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID único da partida")
    created_at: datetime = Field(..., description="Data de criação do registro")
    updated_at: datetime = Field(..., description="Data da última atualização")
    stats: List[MatchStatsResponse] = Field(default=[], description="Estatísticas da partida")