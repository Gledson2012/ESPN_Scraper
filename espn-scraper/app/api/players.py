import logging
from typing import List, Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.security import require_api_key, require_write_api_key, scrape_rate_limiter
from app.database import get_db
from app.models import Player, Team
from app.schemas import PlayerCreate, PlayerUpdate, PlayerResponse
from app.seasons import current_season
from app.services.espn_service import ESPNService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/players", tags=["Jogadores"])


@router.get(
    "/",
    response_model=List[PlayerResponse],
    summary="Listar jogadores",
    description="""
    Retorna uma lista de jogadores com filtros opcionais.

    **Filtros disponíveis:**
    - `team_id`: Filtra por time
    - `position`: Filtra por posição (ex: `FW`, `MF`, `DF`, `GK`)
    - `nationality`: Filtra por nacionalidade (ex: `Brasil`)
    - `skip`/`limit`: Paginação dos resultados
    """,
)
def list_players(
    team_id: Optional[int] = Query(None, description="Filtrar por time", examples=[1]),
    position: Optional[str] = Query(None, description="Filtrar por posição (FW, MF, DF, GK)", examples=["FW"]),
    nationality: Optional[str] = Query(None, description="Filtrar por nacionalidade", examples=["Brasil"]),
    skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Quantidade máxima de registros"),
    db: Session = Depends(get_db),
):
    """Lista todos os jogadores com filtros opcionais."""
    query = db.query(Player)

    if team_id:
        query = query.filter(Player.team_id == team_id)
    if position:
        query = query.filter(Player.position == position)
    if nationality:
        query = query.filter(Player.nationality == nationality)

    return query.offset(skip).limit(limit).all()


@router.get(
    "/{player_id}",
    response_model=PlayerResponse,
    summary="Obter jogador por ID",
    description="Retorna os detalhes de um jogador específico pelo seu ID.",
)
def get_player(player_id: int, db: Session = Depends(get_db)):
    """Obtém um jogador pelo ID."""
    player = db.query(Player).filter(Player.id == player_id).first()
    if not player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    return player


@router.post(
    "/",
    response_model=PlayerResponse,
    status_code=201,
    dependencies=[Depends(require_write_api_key)],
    summary="Criar jogador",
    description="Cria um novo jogador no banco de dados.",
)
def create_player(player: PlayerCreate, db: Session = Depends(get_db)):
    """Cria um novo jogador."""
    if player.team_id is not None and not db.query(Team.id).filter(Team.id == player.team_id).first():
        raise HTTPException(status_code=404, detail="Time não encontrado")

    db_player = Player(**player.model_dump())
    db.add(db_player)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe um jogador com esse ID externo")
    db.refresh(db_player)
    return db_player


@router.put(
    "/{player_id}",
    response_model=PlayerResponse,
    dependencies=[Depends(require_write_api_key)],
    summary="Atualizar jogador",
    description="Atualiza os dados de um jogador existente pelo seu ID.",
)
def update_player(player_id: int, player: PlayerUpdate, db: Session = Depends(get_db)):
    """Atualiza um jogador existente."""
    db_player = db.query(Player).filter(Player.id == player_id).first()
    if not db_player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    updates = player.model_dump(exclude_unset=True)
    if "name" in updates and updates["name"] is None:
        raise HTTPException(status_code=422, detail="O nome do jogador é obrigatório")
    if updates.get("team_id") is not None and not db.query(Team.id).filter(
        Team.id == updates["team_id"]
    ).first():
        raise HTTPException(status_code=404, detail="Time não encontrado")

    for key, value in updates.items():
        setattr(db_player, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe um jogador com esse ID externo")
    db.refresh(db_player)
    return db_player


@router.delete(
    "/{player_id}",
    status_code=204,
    dependencies=[Depends(require_write_api_key)],
    summary="Deletar jogador",
    description="Remove um jogador do banco de dados pelo seu ID.",
)
def delete_player(player_id: int, db: Session = Depends(get_db)):
    """Deleta um jogador."""
    db_player = db.query(Player).filter(Player.id == player_id).first()
    if not db_player:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    db.delete(db_player)
    db.commit()


@router.post(
    "/scrape",
    response_model=List[PlayerResponse],
    dependencies=[Depends(require_api_key), Depends(scrape_rate_limiter)],
    summary="Sincronização de jogadores da ESPN",
    description="""
    Busca jogadores de um time específico na ESPN e salva no banco de dados.

    **Como obter o `espn_team_id`:**
    1. Sincronize a liga desejada pelo endpoint de times
    2. Consulte o campo `espn_id` do time, que contém o ID ESPN
    """,
)
def scrape_players(
    espn_team_id: str = Query(..., description="ID ESPN do time", examples=["86"]),
    season: Optional[str] = Query(
        None,
        description="Temporada; se omitida, usa a temporada atual do time",
        examples=[current_season("Serie-A"), current_season("Premier-League")],
    ),
    db: Session = Depends(get_db),
):
    """Busca jogadores de um time na ESPN e salva no banco."""
    try:
        service = ESPNService(db)
        players = service.scrape_and_save_players(espn_team_id, season)
        return players
    except requests.exceptions.RequestException as e:
        logger.warning("Falha ao acessar a ESPN (%s %s): %s", espn_team_id, season, e)
        raise HTTPException(
            status_code=502,
            detail="Não foi possível acessar a ESPN (falha de rede ou limite temporário). Tente novamente mais tarde.",
        )
