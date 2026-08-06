import logging
from typing import List, Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.security import require_api_key, scrape_rate_limiter
from app.database import get_db
from app.models import Team
from app.schemas import TeamCreate, TeamUpdate, TeamResponse
from app.services.fbref import FBrefService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teams", tags=["teams"])


@router.get(
    "/",
    response_model=List[TeamResponse],
    summary="Listar times",
    description="""
    Retorna uma lista de times com filtros opcionais.

    **Filtros disponíveis:**
    - `league`: Filtra por liga (ex: `Serie-A`, `Premier-League`)
    - `country`: Filtra por país (ex: `Brasil`, `Inglaterra`)
    - `skip`/`limit`: Paginação dos resultados
    """,
)
def list_teams(
    league: Optional[str] = Query(None, description="Filtrar por liga (ex: Serie-A)", examples=["Serie-A"]),
    country: Optional[str] = Query(None, description="Filtrar por país (ex: Brasil)", examples=["Brasil"]),
    skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Quantidade máxima de registros"),
    db: Session = Depends(get_db),
):
    """Lista todos os times com filtros opcionais."""
    query = db.query(Team)

    if league:
        query = query.filter(Team.league == league)
    if country:
        query = query.filter(Team.country == country)

    return query.offset(skip).limit(limit).all()


@router.get(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Obter time por ID",
    description="Retorna os detalhes de um time específico pelo seu ID.",
)
def get_team(team_id: int, db: Session = Depends(get_db)):
    """Obtém um time pelo ID."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Time não encontrado")
    return team


@router.post(
    "/",
    response_model=TeamResponse,
    status_code=201,
    summary="Criar time",
    description="Cria um novo time no banco de dados.",
)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    """Cria um novo time."""
    db_team = Team(**team.model_dump())
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return db_team


@router.put(
    "/{team_id}",
    response_model=TeamResponse,
    summary="Atualizar time",
    description="Atualiza os dados de um time existente pelo seu ID.",
)
def update_team(team_id: int, team: TeamUpdate, db: Session = Depends(get_db)):
    """Atualiza um time existente."""
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Time não encontrado")

    for key, value in team.model_dump(exclude_unset=True).items():
        setattr(db_team, key, value)

    db.commit()
    db.refresh(db_team)
    return db_team


@router.delete(
    "/{team_id}",
    status_code=204,
    summary="Deletar time",
    description="Remove um time do banco de dados pelo seu ID.",
)
def delete_team(team_id: int, db: Session = Depends(get_db)):
    """Deleta um time."""
    db_team = db.query(Team).filter(Team.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Time não encontrado")

    db.delete(db_team)
    db.commit()


@router.post(
    "/scrape",
    response_model=List[TeamResponse],
    dependencies=[Depends(require_api_key), Depends(scrape_rate_limiter)],
    summary="Scraping de times do FBref",
    description="""
    Busca times de uma liga específica no FBref e salva no banco de dados.

    **Ligas suportadas:**
    - `Serie-A` (Brasileirão)
    - `Premier-League`
    - `La-Liga`
    - `Bundesliga`
    - `Serie-A-Italy`
    - `Ligue-1`
    - `Eredivisie`
    - `Primeira-Liga`
    - `MLS`
    - `Liga-MX`
    - `Libertadores`
    - `Champions-League`
    """,
)
def scrape_teams(
    league: str = Query(..., description="Código da liga (ex: Serie-A)", examples=["Serie-A"]),
    season: str = Query("2024-2025", description="Temporada", examples=["2024-2025"]),
    db: Session = Depends(get_db),
):
    """Busca times de uma liga no FBref e salva no banco."""
    try:
        service = FBrefService(db)
        teams = service.scrape_and_save_teams(league, season)
        return teams
    except requests.exceptions.RequestException as e:
        logger.warning(f"Falha ao acessar o FBref ({league} {season}): {e}")
        raise HTTPException(
            status_code=502,
            detail="Não foi possível acessar o FBref (proteção anti-bot ou falha de rede). Tente novamente mais tarde.",
        )