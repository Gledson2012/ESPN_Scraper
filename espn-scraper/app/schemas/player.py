from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional


class PlayerBase(BaseModel):
    """Modelo base de um jogador de futebol."""

    name: str = Field(..., min_length=1, max_length=255, description="Nome do jogador", examples=["Vinícius Júnior"])
    full_name: Optional[str] = Field(None, description="Nome completo do jogador", examples=["Vinícius José Paixão de Oliveira Júnior"])
    birth_date: Optional[datetime] = Field(None, description="Data de nascimento", examples=["2000-07-12T00:00:00"])
    nationality: Optional[str] = Field(None, description="Nacionalidade", examples=["Brasil"])
    position: Optional[str] = Field(None, description="Posição em campo", examples=["FW"])
    foot: Optional[str] = Field(None, description="Pé dominante", examples=["Esquerdo"])
    height_cm: Optional[float] = Field(None, ge=0, le=300, description="Altura em centímetros", examples=[176.0])
    weight_kg: Optional[float] = Field(None, ge=0, le=500, description="Peso em quilogramas", examples=[73.0])
    shirt_number: Optional[int] = Field(None, ge=0, le=99, description="Número da camisa", examples=[7])
    team_id: Optional[int] = Field(None, gt=0, description="ID do time", examples=[1])
    espn_id: Optional[str] = Field(None, description="ID externo do jogador na ESPN", examples=["231388"])
    photo_url: Optional[str] = Field(None, description="URL da foto do jogador na ESPN")


class PlayerCreate(PlayerBase):
    """Dados para criar um novo jogador."""

    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "name": "Gabriel Barbosa",
                    "full_name": "Gabriel Barbosa Almeida",
                    "nationality": "Brasil",
                    "position": "FW",
                    "shirt_number": 9,
                    "team_id": 1,
                    "espn_id": "gabriel-barbosa",
                }
            ]
        }
    )


class PlayerUpdate(BaseModel):
    """Dados para atualizar um jogador existente."""

    model_config = ConfigDict(json_schema_extra={"examples": [{"shirt_number": 10, "position": "FW"}]})

    name: Optional[str] = Field(None, min_length=1, max_length=255, description="Nome do jogador", examples=["Vinícius Júnior"])
    full_name: Optional[str] = Field(None, description="Nome completo do jogador", examples=["Vinícius José Paixão de Oliveira Júnior"])
    birth_date: Optional[datetime] = Field(None, description="Data de nascimento", examples=["2000-07-12T00:00:00"])
    nationality: Optional[str] = Field(None, description="Nacionalidade", examples=["Brasil"])
    position: Optional[str] = Field(None, description="Posição em campo", examples=["FW"])
    foot: Optional[str] = Field(None, description="Pé dominante", examples=["Esquerdo"])
    height_cm: Optional[float] = Field(None, ge=0, le=300, description="Altura em centímetros", examples=[176.0])
    weight_kg: Optional[float] = Field(None, ge=0, le=500, description="Peso em quilogramas", examples=[73.0])
    shirt_number: Optional[int] = Field(None, ge=0, le=99, description="Número da camisa", examples=[7])
    team_id: Optional[int] = Field(None, gt=0, description="ID do time", examples=[1])
    espn_id: Optional[str] = Field(None, description="ID externo do jogador na ESPN", examples=["231388"])
    photo_url: Optional[str] = Field(None, description="URL da foto do jogador na ESPN")


class PlayerResponse(PlayerBase):
    """Resposta com dados de um jogador."""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="ID único do jogador")
    created_at: datetime = Field(..., description="Data de criação do registro")
    updated_at: datetime = Field(..., description="Data da última atualização")
