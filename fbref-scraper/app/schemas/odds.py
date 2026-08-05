from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List


class OddsSelection(BaseModel):
    """Seleção de aposta dentro de um mercado."""

    id: str = Field(..., description="ID da seleção", examples=["sel_1"])
    name: str = Field(..., description="Nome da seleção", examples=["Flamengo"])
    price: float = Field(..., description="Odd/preço da seleção", examples=[2.10])
    outcome: Optional[str] = Field(None, description="Resultado da seleção", examples=["win"])


class OddsMarket(BaseModel):
    """Mercado de apostas (ex: 1X2, Total de Gols, etc)."""

    id: str = Field(..., description="ID do mercado", examples=["mkt_1x2"])
    name: str = Field(..., description="Nome do mercado", examples=["Resultado 1X2"])
    selections: List[OddsSelection] = Field(..., description="Seleções de apostas do mercado")


class EventOdds(BaseModel):
    """Odds de um evento/partida."""

    event_id: str = Field(..., description="ID do evento", examples=["abc123"])
    event_name: str = Field(..., description="Nome do evento", examples=["Flamengo vs Palmeiras"])
    home_team: Optional[str] = Field(None, description="Time da casa", examples=["Flamengo"])
    away_team: Optional[str] = Field(None, description="Time visitante", examples=["Palmeiras"])
    start_time: Optional[str] = Field(None, description="Horário de início", examples=["2026-04-10T20:00:00Z"])
    competition: Optional[Dict[str, Any]] = Field(None, description="Informações da competição")
    markets: Dict[str, Any] = Field(default={}, description="Mercados de apostas do evento")
    status: Optional[str] = Field(None, description="Status do evento", examples=["pre_match"])


class MatchOddsResponse(BaseModel):
    """Resposta com odds de uma partida específica."""

    event_id: str = Field(..., description="ID do evento", examples=["abc123"])
    event_name: str = Field(..., description="Nome do evento", examples=["Flamengo vs Palmeiras"])
    start_time: Optional[str] = Field(None, description="Horário de início", examples=["2026-04-10T20:00:00Z"])
    home_team: str = Field(..., description="Time da casa", examples=["Flamengo"])
    away_team: str = Field(..., description="Time visitante", examples=["Palmeiras"])
    markets: Dict[str, Any] = Field(default={}, description="Mercados de apostas do evento")


class SoccerOddsResponse(BaseModel):
    """Resposta com odds de futebol."""

    events: List[EventOdds] = Field(..., description="Lista de eventos com odds")
    total: int = Field(..., description="Total de eventos retornados", examples=[1])