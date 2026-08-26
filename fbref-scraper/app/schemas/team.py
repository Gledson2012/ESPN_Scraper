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
    fbref_id: Optional[str] = Field(None, description="ID do time no FBref", examples=["flamengo"])
    logo_url: Optional[str] = Field(None, description="URL do logo do time", examples=["https://example.com/logo.png"])


class TeamCreate(TeamBase):
    """Dados para criar um novo time."""


class TeamUpdate(BaseModel):
    """Dados para atualizar um time existente."""

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome completo do time", examples=["Flamengo"])
    short_name: Optional[str] = Field(None, description="Nome abreviado", examples=["FLA"])
    country: Optional[str] = Field(None, description="País do time", examples=["Brasil"])
    league: Optional[str] = Field(None, description="Liga do time", examples=["Serie-A"])
    stadium: Optional[str] = Field(None, description="Estádio do time", examples=["Maracanã"])
    founded: Optional[int] = Field(None, ge=0, le=2100, description="Ano de fundação", examples=[1895])
    website: Optional[str] = Field(None, description="Site oficial", examples=["https://www.flamengo.com.br"])
    fbref_id: Optional[str] = Field(None, description="ID do time no FBref", examples=["flamengo"])
    logo_url: Optional[str] = Field(None, description="URL do logo do time", examples=["https://example.com/logo.png"])


class TeamResponse(TeamBase):
    """Resposta com dados de um time."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID único do time")
    created_at: datetime = Field(..., description="Data de criação do registro")
    updated_at: datetime = Field(..., description="Data da última atualização")
