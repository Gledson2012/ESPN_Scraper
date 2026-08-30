import logging
from typing import List, Optional
from datetime import datetime

import requests
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.api.security import require_api_key, require_write_api_key, scrape_rate_limiter, public_rate_limiter
from app.database import get_db
from app.models import Match, MatchStats, Team
from app.schemas import MatchCreate, MatchListResponse, MatchStatsResponse, MatchUpdate, MatchResponse, LiveMatchResponse
from app.scrapers.espn import ESPN_LEAGUE_SLUGS, MatchesScraper
from app.seasons import current_season, resolve_season
from app.services.espn_service import ESPNService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/matches", tags=["Partidas"])


@router.get(
    "/",
    response_model=List[MatchListResponse],
    summary="Listar partidas",
    description="""
    Retorna uma lista de partidas com filtros opcionais.

    **Filtros disponíveis:**
    - `competition`: Filtra por competição (ex: `Serie-A`)
    - `season`: Filtra por temporada (ex: `2026` ou `2026-2027`)
    - `team_id`: Filtra por time (casa ou fora)
    - `date_from`/`date_to`: Filtra por período de datas
    - `skip`/`limit`: Paginação dos resultados
    """,
)
def list_matches(
    competition: Optional[str] = Query(None, description="Filtrar por competição", examples=["Serie-A"]),
    season: Optional[str] = Query(
        None,
        description="Filtrar por temporada (ex.: 2026 ou 2026-2027)",
        examples=["2026", "2026-2027"],
    ),
    team_id: Optional[int] = Query(None, gt=0, description="Filtrar por time (casa ou fora)", examples=[1]),
    date_from: Optional[datetime] = Query(None, description="Data inicial (formato ISO)", examples=["2025-01-01T00:00:00"]),
    date_to: Optional[datetime] = Query(None, description="Data final (formato ISO)", examples=["2025-12-31T23:59:59"]),
    skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Quantidade máxima de registros"),
    db: Session = Depends(get_db),
):
    """Lista todas as partidas com filtros opcionais."""
    query = db.query(Match)

    if competition:
        query = query.filter(Match.competition == competition)
    if season:
        query = query.filter(Match.season == season)
    if team_id:
        query = query.filter(
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        )
    if date_from:
        query = query.filter(Match.match_date >= date_from)
    if date_to:
        query = query.filter(Match.match_date <= date_to)

    return query.order_by(Match.match_date.desc()).offset(skip).limit(limit).all()


@router.get(
    "/live",
    response_model=List[LiveMatchResponse],
    dependencies=[Depends(public_rate_limiter)],
    summary="Partidas ao vivo (tempo real da ESPN)",
    description="""
    Retorna as partidas que estão em andamento agora, consultadas em tempo
    real no scoreboard da ESPN (sem usar o banco de dados).

    - `league`: opcional; filtra por uma liga (ex: `Serie-A`). Se omitida,
      consulta todas as 25 ligas suportadas.

    **Ligas suportadas:** as mesmas do endpoint de scraping (`Serie-A`,
    `Premier-League`, `La-Liga`, `Bundesliga`, `Libertadores`, `Champions-League`,
    `Serie-B`, `Copa-do-Brasil`, entre outras — veja a tabela de ligas).
    """,
)
def list_live_matches(
    league: Optional[str] = Query(
        None,
        description="Código da liga; omita para consultar todas as ligas suportadas",
        examples=["Serie-A"],
    ),
):
    """Lista as partidas em andamento consultando a ESPN em tempo real."""
    scraper = MatchesScraper()
    try:
        if league:
            return scraper.get_live_matches(league)

        results: List[LiveMatchResponse] = []
        seen_slugs = set()
        for league_name, slug in ESPN_LEAGUE_SLUGS.items():
            if slug in seen_slugs:
                continue  # ignora aliases da mesma competição (ex: Serie A / Serie-A)
            seen_slugs.add(slug)
            results.extend(scraper.get_live_matches(league_name))
        return results
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except requests.exceptions.RequestException as e:
        logger.warning(f"Falha ao acessar a ESPN (jogos ao vivo): {e}")
        raise HTTPException(
            status_code=502,
            detail="Não foi possível acessar a ESPN (falha de rede ou limite temporário). Tente novamente mais tarde.",
        )


@router.get(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Obter partida por ID",
    description="Retorna os detalhes de uma partida específica pelo seu ID, incluindo estatísticas.",
)
def get_match(match_id: int, db: Session = Depends(get_db)):
    """Obtém uma partida pelo ID."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    return match


@router.get(
    "/{match_id}/stats",
    response_model=List[MatchStatsResponse],
    summary="Obter estatísticas da partida",
    description="Retorna as estatísticas dos dois times associadas à partida.",
)
def get_match_stats(match_id: int, db: Session = Depends(get_db)):
    """Lista estatísticas de uma partida, mandante primeiro."""
    if not db.query(Match.id).filter(Match.id == match_id).first():
        raise HTTPException(status_code=404, detail="Partida não encontrada")
    return db.query(MatchStats).filter(
        MatchStats.match_id == match_id
    ).order_by(MatchStats.is_home.desc()).all()


@router.post(
    "/",
    response_model=MatchResponse,
    status_code=201,
    dependencies=[Depends(require_write_api_key)],
    summary="Criar partida",
    description="Cria uma nova partida no banco de dados.",
)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    """Cria uma nova partida."""
    if not db.query(Team.id).filter(Team.id == match.home_team_id).first():
        raise HTTPException(status_code=404, detail="Time da casa não encontrado")
    if not db.query(Team.id).filter(Team.id == match.away_team_id).first():
        raise HTTPException(status_code=404, detail="Time visitante não encontrado")

    db_match = Match(**match.model_dump())
    db.add(db_match)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe uma partida com esse ID externo")
    db.refresh(db_match)
    return db_match


@router.put(
    "/{match_id}",
    response_model=MatchResponse,
    dependencies=[Depends(require_write_api_key)],
    summary="Atualizar partida",
    description="Atualiza os dados de uma partida existente pelo seu ID.",
)
def update_match(match_id: int, match: MatchUpdate, db: Session = Depends(get_db)):
    """Atualiza uma partida existente."""
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if not db_match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    updates = match.model_dump(exclude_unset=True)
    home_team_id = updates.get("home_team_id", db_match.home_team_id)
    away_team_id = updates.get("away_team_id", db_match.away_team_id)
    if home_team_id is None or away_team_id is None:
        raise HTTPException(status_code=422, detail="Os dois times da partida são obrigatórios")
    if home_team_id == away_team_id:
        raise HTTPException(status_code=422, detail="O time da casa deve ser diferente do time visitante")
    if not db.query(Team.id).filter(Team.id == home_team_id).first():
        raise HTTPException(status_code=404, detail="Time da casa não encontrado")
    if not db.query(Team.id).filter(Team.id == away_team_id).first():
        raise HTTPException(status_code=404, detail="Time visitante não encontrado")

    for key, value in updates.items():
        setattr(db_match, key, value)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Já existe uma partida com esse ID externo")
    db.refresh(db_match)
    return db_match


@router.delete(
    "/{match_id}",
    status_code=204,
    dependencies=[Depends(require_write_api_key)],
    summary="Deletar partida",
    description="Remove uma partida do banco de dados pelo seu ID.",
)
def delete_match(match_id: int, db: Session = Depends(get_db)):
    """Deleta uma partida."""
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if not db_match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    db.delete(db_match)
    db.commit()


@router.post(
    "/scrape",
    response_model=List[MatchResponse],
    dependencies=[Depends(require_api_key), Depends(scrape_rate_limiter)],
    summary="Sincronização de partidas da ESPN",
    description="""
    Busca partidas de uma liga específica na ESPN e salva no banco de dados.

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
    - `Serie-B` (Brasileirão Série B)
    - `Copa-do-Brasil`
    - `Liga-Argentina`
    - `Sudamericana`
    - `World-Cup`
    - `Championship`
    - `Europa-League`
    - `Conference-League`
    - `Copa-del-Rey`
    - `Coppa-Italia`
    - `DFB-Pokal`
    """,
)
def scrape_matches(
    league: str = Query(..., description="Código da liga (ex: Serie-A)", examples=["Serie-A"]),
    season: Optional[str] = Query(
        None,
        description="Temporada; se omitida, usa a temporada atual da liga",
        examples=[current_season("Serie-A"), current_season("Premier-League")],
    ),
    db: Session = Depends(get_db),
):
    """Busca partidas de uma liga na ESPN e salva no banco."""
    try:
        season = resolve_season(league, season)
        service = ESPNService(db)
        matches = service.scrape_and_save_matches(league, season)
        return matches
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except requests.exceptions.RequestException as e:
        logger.warning(f"Falha ao acessar a ESPN ({league} {season}): {e}")
        raise HTTPException(
            status_code=502,
            detail="Não foi possível acessar a ESPN (falha de rede ou limite temporário). Tente novamente mais tarde.",
        )


@router.post(
    "/{match_id}/scrape-stats",
    response_model=MatchResponse,
    dependencies=[Depends(require_api_key), Depends(scrape_rate_limiter)],
    summary="Scraping de estatísticas da partida",
    description="""
    Busca estatísticas detalhadas de uma partida na ESPN e salva no banco de dados.

    **Estatísticas coletadas:**
    - Posse de bola, finalizações, escanteios, faltas
    - Cartões amarelos e vermelhos
    - xG (gols esperados) e xG sofrido
    - Passes, precisão de passes, desarmes, interceptações
    - Defesas do goleiro
    """,
)
def scrape_match_statistics(match_id: int, db: Session = Depends(get_db)):
    """Busca estatísticas de uma partida na ESPN e salva no banco."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    try:
        service = ESPNService(db)
        service.scrape_and_save_match_statistics(match.espn_id)
    except requests.exceptions.RequestException as e:
        logger.warning(f"Falha ao acessar a ESPN (partida {match.espn_id}): {e}")
        raise HTTPException(
            status_code=502,
            detail="Não foi possível acessar a ESPN (falha de rede ou limite temporário). Tente novamente mais tarde.",
        )
    db.refresh(match)
    return match
