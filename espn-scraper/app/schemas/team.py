from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class TeamBase(BaseModel):
    """Modelo base de um time de futebol."""

    name: str = Field(..., min_length=1, max_length=255, description="Nome completo do time", examples=["Flamengo"])
    short_name: Optional[str] = Field(None, description="Nome abreviado", examples=["FLA"])
    country: Optional[str] = Field(None, description="País do time", examples=["Brasil"])
    league: Optional[str] = Field(None, description="Liga do time", examples=["Serie-A"])
    stadium: Optional[str] = Field(None, description="Estádio do time", examples=["Maracanã"])
    founded: Optional[int] = Field(None, ge=0, le=2100, description="Ano de fundação", examples=[1895])
    website: Optional[str] = Field(None, description="Site oficial", examples=["https://www.flamengo.com.br"])
    espn_id: Optional[str] = Field(None, description="ID externo do time na ESPN", examples=["86"])
    logo_url: Optional[str] = Field(None, description="URL do logo do time", examples=["https://example.com/logo.png"])


class TeamCreate(TeamBase):
    """Dados para criar um novo time."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Flamengo",
                    "short_name": "FLA",
                    "country": "Brasil",
                    "league": "Serie-A",
                    "founded": 1895,
                    "espn_id": "flamengo",
                }
            ]
        }
    )


class TeamUpdate(BaseModel):
    """Dados para atualizar um time existente."""

    model_config = ConfigDict(
        json_schema_extra={"examples": [{"stadium": "Maracanã", "website": "https://www.flamengo.com.br"}]}
    )

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome completo do time", examples=["Flamengo"])
    short_name: Optional[str] = Field(None, description="Nome abreviado", examples=["FLA"])
    country: Optional[str] = Field(None, description="País do time", examples=["Brasil"])
    league: Optional[str] = Field(None, description="Liga do time", examples=["Serie-A"])
    stadium: Optional[str] = Field(None, description="Estádio do time", examples=["Maracanã"])
    founded: Optional[int] = Field(None, ge=0, le=2100, description="Ano de fundação", examples=[1895])
    website: Optional[str] = Field(None, description="Site oficial", examples=["https://www.flamengo.com.br"])
    espn_id: Optional[str] = Field(None, description="ID externo do time na ESPN", examples=["86"])
    logo_url: Optional[str] = Field(None, description="URL do logo do time", examples=["https://example.com/logo.png"])


class TeamResponse(TeamBase):
    """Resposta com dados de um time."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID único do time")
    created_at: datetime = Field(..., description="Data de criação do registro")
    updated_at: datetime = Field(..., description="Data da última atualização")


class TeamSummaryResponse(BaseModel):
    """Resumo de desempenho de um time em partidas com placar conhecido."""

    team_id: int = Field(..., gt=0, description="ID do time", examples=[1])
    team_name: str = Field(..., description="Nome do time", examples=["Flamengo"])
    matches: int = Field(..., ge=0, description="Partidas cadastradas", examples=[38])
    completed_matches: int = Field(..., ge=0, description="Partidas com placar conhecido", examples=[38])
    wins: int = Field(..., ge=0, description="Vitórias", examples=[25])
    draws: int = Field(..., ge=0, description="Empates", examples=[8])
    losses: int = Field(..., ge=0, description="Derrotas", examples=[5])
    goals_for: int = Field(..., ge=0, description="Gols marcados", examples=[72])
    goals_against: int = Field(..., ge=0, description="Gols sofridos", examples=[35])
    goal_difference: int = Field(..., description="Saldo de gols", examples=[37])
    points: int = Field(..., ge=0, description="Pontos (3 por vitória, 1 por empate)", examples=[83])
    stats_available: int = Field(..., ge=0, description="Partidas com estatísticas coletadas", examples=[32])
