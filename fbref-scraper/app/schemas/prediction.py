from typing import Optional

from pydantic import BaseModel, ConfigDict, Field, model_validator


class PredictionRequest(BaseModel):
    """Dados para gerar uma previsão de partida."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "home_team_id": 1,
                    "away_team_id": 2,
                    "competition": "Serie-A",
                    "season": "2024-2025",
                }
            ]
        }
    )

    home_team_id: int = Field(..., gt=0, description="ID do time da casa", examples=[1])
    away_team_id: int = Field(..., gt=0, description="ID do time visitante", examples=[2])
    competition: Optional[str] = Field(None, min_length=1, description="Filtrar o histórico por competição", examples=["Serie-A"])
    season: Optional[str] = Field(None, min_length=1, description="Filtrar o histórico por temporada", examples=["2024-2025"])

    @model_validator(mode="after")
    def teams_must_be_different(self):
        if self.home_team_id == self.away_team_id:
            raise ValueError("O time da casa deve ser diferente do time visitante")
        return self


class PredictionResponse(BaseModel):
    """Resposta com a previsão da partida."""

    home_team_id: int = Field(..., description="ID do time da casa", examples=[1])
    away_team_id: int = Field(..., description="ID do time visitante", examples=[2])
    home_win_probability: float = Field(..., ge=0, le=1, description="Probabilidade de vitória do time da casa (0-1)", examples=[0.4521])
    draw_probability: float = Field(..., ge=0, le=1, description="Probabilidade de empate (0-1)", examples=[0.2712])
    away_win_probability: float = Field(..., ge=0, le=1, description="Probabilidade de vitória do time visitante (0-1)", examples=[0.2767])
    predicted_home_score: float = Field(..., ge=0, description="Gols esperados do time da casa", examples=[1.45])
    predicted_away_score: float = Field(..., ge=0, description="Gols esperados do time visitante", examples=[1.12])
    over_2_5_probability: float = Field(..., ge=0, le=1, description="Probabilidade de over 2.5 gols (0-1)", examples=[0.5234])
    btts_probability: float = Field(..., ge=0, le=1, description="Probabilidade de ambos marcarem - BTTS (0-1)", examples=[0.6123])
    confidence: float = Field(..., ge=0, le=1, description="Nível de confiança da previsão (0-1)", examples=[0.75])
    model_version: str = Field(..., description="Versão do modelo de previsão", examples=["1.1.0"])
