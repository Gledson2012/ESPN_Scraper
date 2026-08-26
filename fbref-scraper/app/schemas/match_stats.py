from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class MatchStatsBase(BaseModel):
    """Modelo base de estatísticas de uma partida."""

    match_id: int = Field(..., gt=0, description="ID da partida", examples=[1])
    team_id: int = Field(..., gt=0, description="ID do time", examples=[1])
    is_home: bool = Field(False, description="Se o time é o da casa", examples=[True])

    # Estatísticas gerais
    possession: Optional[float] = Field(None, ge=0, le=100, description="Posse de bola (%)", examples=[58.5])
    shots: Optional[int] = Field(None, ge=0, description="Finalizações", examples=[15])
    shots_on_target: Optional[int] = Field(None, ge=0, description="Finalizações no alvo", examples=[6])
    corners: Optional[int] = Field(None, ge=0, description="Escanteios", examples=[7])
    fouls: Optional[int] = Field(None, ge=0, description="Faltas cometidas", examples=[12])
    yellow_cards: Optional[int] = Field(None, ge=0, description="Cartões amarelos", examples=[2])
    red_cards: Optional[int] = Field(None, ge=0, description="Cartões vermelhos", examples=[0])
    offsides: Optional[int] = Field(None, ge=0, description="Impedimentos", examples=[3])

    # Estatísticas avançadas
    xg: Optional[float] = Field(None, ge=0, le=20, description="Gols esperados (xG)", examples=[1.85])
    xg_against: Optional[float] = Field(None, ge=0, le=20, description="xG sofrido", examples=[0.92])
    passes: Optional[int] = Field(None, ge=0, description="Passes completos", examples=[520])
    pass_accuracy: Optional[float] = Field(None, ge=0, le=100, description="Precisão de passes (%)", examples=[87.5])
    tackles: Optional[int] = Field(None, ge=0, description="Desarmes", examples=[18])
    interceptions: Optional[int] = Field(None, ge=0, description="Interceptações", examples=[9])
    saves: Optional[int] = Field(None, ge=0, description="Defesas do goleiro", examples=[4])


class MatchStatsCreate(MatchStatsBase):
    """Dados para criar estatísticas de uma partida."""


class MatchStatsResponse(MatchStatsBase):
    """Resposta com estatísticas de uma partida."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID único do registro")
    created_at: datetime = Field(..., description="Data de criação do registro")
    updated_at: datetime = Field(..., description="Data da última atualização")
