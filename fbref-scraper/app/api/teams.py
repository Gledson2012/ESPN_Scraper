import logging
from typing import List, Optional

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.security import require_api_key, scrape_rate_limiter
from app.database import get_db
from app.models import Match, MatchStats, Player, Team
from app.schemas import MatchResponse, PlayerResponse, TeamCreate, TeamSummaryResponse, TeamUpdate, TeamResponse
from app.services.fbref import FBrefService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/teams", tags=["Times"])


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


@router.get(
    "/{team_id}/players",
    response_model=List[PlayerResponse],
    summary="Listar jogadores do time",
    description="Retorna os jogadores atualmente vinculados a um time.",
)
def list_team_players(
    team_id: int,
    position: Optional[str] = Query(None, description="Filtrar por posição", examples=["FW"]),
    skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Quantidade máxima de registros"),
    db: Session = Depends(get_db),
):
    """Lista jogadores vinculados a um time."""
    if not db.query(Team.id).filter(Team.id == team_id).first():
        raise HTTPException(status_code=404, detail="Time não encontrado")

    query = db.query(Player).filter(Player.team_id == team_id)
    if position:
        query = query.filter(Player.position == position)
    return query.order_by(Player.name).offset(skip).limit(limit).all()


@router.get(
    "/{team_id}/matches",
    response_model=List[MatchResponse],
    summary="Listar partidas do time",
    description="Retorna partidas em que o time participou, como mandante ou visitante.",
)
def list_team_matches(
    team_id: int,
    competition: Optional[str] = Query(None, description="Filtrar por competição", examples=["Serie-A"]),
    season: Optional[str] = Query(None, description="Filtrar por temporada", examples=["2024-2025"]),
    skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Quantidade máxima de registros"),
    db: Session = Depends(get_db),
):
    """Lista partidas de um time com filtros opcionais."""
    if not db.query(Team.id).filter(Team.id == team_id).first():
        raise HTTPException(status_code=404, detail="Time não encontrado")

    query = db.query(Match).filter(
        (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
    )
    if competition:
        query = query.filter(Match.competition == competition)
    if season:
        query = query.filter(Match.season == season)
    return query.order_by(Match.match_date.desc()).offset(skip).limit(limit).all()


@router.get(
    "/{team_id}/summary",
    response_model=TeamSummaryResponse,
    summary="Resumo de desempenho do time",
    description="Calcula campanha, gols, pontos e disponibilidade de estatísticas do time.",
)
def get_team_summary(team_id: int, db: Session = Depends(get_db)):
    """Retorna um resumo de desempenho baseado nos placares cadastrados."""
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Time não encontrado")

    matches = db.query(Match).filter(
        (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
    ).all()
    completed = [
        match for match in matches
        if match.home_score is not None and match.away_score is not None
    ]

    wins = draws = losses = goals_for = goals_against = points = 0
    for match in completed:
        is_home = match.home_team_id == team_id
        team_goals = match.home_score if is_home else match.away_score
        opponent_goals = match.away_score if is_home else match.home_score
        goals_for += team_goals
        goals_against += opponent_goals
        if team_goals > opponent_goals:
            wins += 1
            points += 3
        elif team_goals == opponent_goals:
            draws += 1
            points += 1
        else:
            losses += 1

    stats_available = db.query(MatchStats.match_id).filter(
        MatchStats.team_id == team_id
    ).distinct().count()

    return TeamSummaryResponse(
        team_id=team.id,
        team_name=team.name,
        matches=len(matches),
        completed_matches=len(completed),
        wins=wins,
        draws=draws,
        losses=losses,
        goals_for=goals_for,
        goals_against=goals_against,
        goal_difference=goals_for - goals_against,
        points=points,
        stats_available=stats_available,
    )


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
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe um time com esse FBref ID")
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

    updates = team.model_dump(exclude_unset=True)
    if "name" in updates and updates["name"] is None:
        raise HTTPException(status_code=422, detail="O nome do time é obrigatório")

    for key, value in updates.items():
        setattr(db_team, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe um time com esse FBref ID")
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

    has_players = db.query(Player.id).filter(Player.team_id == team_id).first() is not None
    has_matches = db.query(Match.id).filter(
        (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
    ).first() is not None
    if has_players or has_matches:
        raise HTTPException(
            status_code=409,
            detail="Não é possível excluir um time que possui jogadores ou partidas associadas",
        )

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
