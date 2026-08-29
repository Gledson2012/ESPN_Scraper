from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class CatalogOption(BaseModel):
    code: str = Field(..., description="Código usado nos filtros da API")
    name: str = Field(..., description="Nome legível da opção")


class CatalogResponse(BaseModel):
    competitions: list[CatalogOption]
    seasons: list[str]
    positions: list[str]
    nationalities: list[str]
    countries: list[str]


class SyncResourceStatus(BaseModel):
    resource: Literal["teams", "players", "matches", "stats"]
    count: int = Field(..., ge=0)
    last_updated_at: Optional[datetime] = None
    source: str = "ESPN"


class SyncStatusResponse(BaseModel):
    generated_at: datetime
    resources: list[SyncResourceStatus]


class OverviewTotals(BaseModel):
    teams: int = Field(..., ge=0)
    players: int = Field(..., ge=0)
    matches: int = Field(..., ge=0)
    completed_matches: int = Field(..., ge=0)
    upcoming_matches: int = Field(..., ge=0)
    stats: int = Field(..., ge=0)


class OverviewMatch(BaseModel):
    id: int
    home_team_id: int
    away_team_id: int
    home_team: str
    away_team: str
    competition: Optional[str] = None
    season: Optional[str] = None
    match_date: Optional[datetime] = None
    home_score: Optional[int] = None
    away_score: Optional[int] = None


class OverviewResponse(BaseModel):
    generated_at: datetime
    competition: Optional[str] = None
    season: Optional[str] = None
    totals: OverviewTotals
    next_matches: list[OverviewMatch]
    recent_matches: list[OverviewMatch]


class SearchResult(BaseModel):
    type: Literal["team", "player", "match"]
    id: int
    title: str
    subtitle: Optional[str] = None
    path: str


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResult]
    total: int = Field(..., ge=0)
