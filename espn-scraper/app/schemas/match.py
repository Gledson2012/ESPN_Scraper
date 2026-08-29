from pydantic import BaseModel, ConfigDict, Field, model_validator
from datetime import datetime
from typing import Optional, List

from app.schemas.match_stats import MatchStatsResponse
from app.seasons import current_season


SEASON_EXAMPLES = [current_season("Serie-A"), current_season("Premier-League")]


class MatchBase(BaseModel):
    """Modelo base de uma partida de futebol."""

    home_team_id: int = Field(..., gt=0, description="ID do time da casa", examples=[1])
    away_team_id: int = Field(..., gt=0, description="ID do time visitante", examples=[2])
    competition: Optional[str] = Field(None, description="Competição", examples=["Serie-A"])
    season: Optional[str] = Field(
        None,
        description="Temporada (ex.: 2026 ou 2026-2027)",
        examples=SEASON_EXAMPLES,
    )
    match_date: Optional[datetime] = Field(None, description="Data da partida", examples=["2025-03-15T20:00:00"])
    venue: Optional[str] = Field(None, description="Local da partida", examples=["Maracanã"])
    home_score: Optional[int] = Field(None, ge=0, description="Gols do time da casa", examples=[2])
    away_score: Optional[int] = Field(None, ge=0, description="Gols do time visitante", examples=[1])
    home_xg: Optional[float] = Field(None, ge=0, le=20, description="xG do time da casa", examples=[1.85])
    away_xg: Optional[float] = Field(None, ge=0, le=20, description="xG do time visitante", examples=[0.92])
    attendance: Optional[int] = Field(None, ge=0, description="Público presente", examples=[65000])
    referee: Optional[str] = Field(None, description="Árbitro da partida", examples=["Anderson Daronco"])
    fbref_id: Optional[str] = Field(None, description="ID externo da partida na ESPN (campo legado)", examples=["401882899"])

    @model_validator(mode="after")
    def teams_must_be_different(self):
        if self.home_team_id == self.away_team_id:
            raise ValueError("O time da casa deve ser diferente do time visitante")
        return self


class MatchCreate(MatchBase):
    """Dados para criar uma nova partida."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "home_team_id": 1,
                    "away_team_id": 2,
                    "competition": "Serie-A",
                    "season": current_season("Serie-A"),
                    "home_score": 2,
                    "away_score": 1,
                    "fbref_id": "match-123",
                }
            ]
        }
    )


class MatchUpdate(BaseModel):
    """Dados para atualizar uma partida existente."""

    model_config = ConfigDict(json_schema_extra={"examples": [{"home_score": 3, "away_score": 1}]})

    home_team_id: Optional[int] = Field(None, gt=0, description="ID do time da casa", examples=[1])
    away_team_id: Optional[int] = Field(None, gt=0, description="ID do time visitante", examples=[2])
    competition: Optional[str] = Field(None, description="Competição", examples=["Serie-A"])
    season: Optional[str] = Field(
        None,
        description="Temporada (ex.: 2026 ou 2026-2027)",
        examples=SEASON_EXAMPLES,
    )
    match_date: Optional[datetime] = Field(None, description="Data da partida", examples=["2025-03-15T20:00:00"])
    venue: Optional[str] = Field(None, description="Local da partida", examples=["Maracanã"])
    home_score: Optional[int] = Field(None, ge=0, description="Gols do time da casa", examples=[2])
    away_score: Optional[int] = Field(None, ge=0, description="Gols do time visitante", examples=[1])
    home_xg: Optional[float] = Field(None, ge=0, le=20, description="xG do time da casa", examples=[1.85])
    away_xg: Optional[float] = Field(None, ge=0, le=20, description="xG do time visitante", examples=[0.92])
    attendance: Optional[int] = Field(None, ge=0, description="Público presente", examples=[65000])
    referee: Optional[str] = Field(None, description="Árbitro da partida", examples=["Anderson Daronco"])
    fbref_id: Optional[str] = Field(None, description="ID externo da partida na ESPN (campo legado)", examples=["401882899"])

    @model_validator(mode="after")
    def teams_must_be_different_when_present(self):
        if (
            self.home_team_id is not None
            and self.away_team_id is not None
            and self.home_team_id == self.away_team_id
        ):
            raise ValueError("O time da casa deve ser diferente do time visitante")
        return self


class MatchListResponse(MatchBase):
    """Resposta resumida usada em listagens de partidas."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID único da partida")
    created_at: datetime = Field(..., description="Data de criação do registro")
    updated_at: datetime = Field(..., description="Data da última atualização")


class MatchResponse(MatchListResponse):
    """Resposta detalhada de uma partida."""

    stats: List[MatchStatsResponse] = Field(default_factory=list, description="Estatísticas da partida")


class LiveMatchResponse(BaseModel):
    """Partida em andamento, consultada em tempo real na ESPN."""

    league: str = Field(..., description="Liga na nomenclatura da API", examples=["Serie-A"])
    espn_event_id: str = Field(..., description="ID do evento na ESPN", examples=["401882899"])
    status: str = Field(..., description="Situação da partida", examples=["2nd Half"])
    clock: Optional[str] = Field(None, description="Tempo decorrido exibido pela ESPN", examples=["67' - 2nd Half"])
    match_date: Optional[datetime] = Field(None, description="Data/hora de início da partida")
    venue: Optional[str] = Field(None, description="Estádio da partida", examples=["Anfield"])
    home_team: str = Field(..., description="Nome do time da casa", examples=["Liverpool"])
    away_team: str = Field(..., description="Nome do time visitante", examples=["Everton"])
    home_score: Optional[int] = Field(None, ge=0, description="Gols do time da casa", examples=[1])
    away_score: Optional[int] = Field(None, ge=0, description="Gols do time visitante", examples=[0])
    home_team_logo: Optional[str] = Field(None, description="URL do escudo do time da casa")
    away_team_logo: Optional[str] = Field(None, description="URL do escudo do time visitante")
