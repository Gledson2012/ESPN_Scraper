from typing import List, Optional
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match
from app.schemas import MatchCreate, MatchUpdate, MatchResponse
from app.services.fbref import FBrefService

router = APIRouter(prefix="/matches", tags=["matches"])


@router.get(
    "/",
    response_model=List[MatchResponse],
    summary="Listar partidas",
    description="""
    Retorna uma lista de partidas com filtros opcionais.

    **Filtros disponíveis:**
    - `competition`: Filtra por competição (ex: `Serie-A`)
    - `season`: Filtra por temporada (ex: `2024-2025`)
    - `team_id`: Filtra por time (casa ou fora)
    - `date_from`/`date_to`: Filtra por período de datas
    - `skip`/`limit`: Paginação dos resultados
    """,
)
def list_matches(
    competition: Optional[str] = Query(None, description="Filtrar por competição", examples=["Serie-A"]),
    season: Optional[str] = Query(None, description="Filtrar por temporada", examples=["2024-2025"]),
    team_id: Optional[int] = Query(None, description="Filtrar por time (casa ou fora)", examples=[1]),
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


@router.post(
    "/",
    response_model=MatchResponse,
    status_code=201,
    summary="Criar partida",
    description="Cria uma nova partida no banco de dados.",
)
def create_match(match: MatchCreate, db: Session = Depends(get_db)):
    """Cria uma nova partida."""
    db_match = Match(**match.model_dump())
    db.add(db_match)
    db.commit()
    db.refresh(db_match)
    return db_match


@router.put(
    "/{match_id}",
    response_model=MatchResponse,
    summary="Atualizar partida",
    description="Atualiza os dados de uma partida existente pelo seu ID.",
)
def update_match(match_id: int, match: MatchUpdate, db: Session = Depends(get_db)):
    """Atualiza uma partida existente."""
    db_match = db.query(Match).filter(Match.id == match_id).first()
    if not db_match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    for key, value in match.model_dump(exclude_unset=True).items():
        setattr(db_match, key, value)

    db.commit()
    db.refresh(db_match)
    return db_match


@router.delete(
    "/{match_id}",
    status_code=204,
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
    summary="Scraping de partidas do FBref",
    description="""
    Busca partidas de uma liga específica no FBref e salva no banco de dados.

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
def scrape_matches(
    league: str = Query(..., description="Código da liga (ex: Serie-A)", examples=["Serie-A"]),
    season: str = Query("2024-2025", description="Temporada", examples=["2024-2025"]),
    db: Session = Depends(get_db),
):
    """Busca partidas de uma liga no FBref e salva no banco."""
    service = FBrefService(db)
    matches = service.scrape_and_save_matches(league, season)
    return matches


@router.post(
    "/{match_id}/scrape-stats",
    response_model=MatchResponse,
    summary="Scraping de estatísticas da partida",
    description="""
    Busca estatísticas detalhadas de uma partida no FBref e salva no banco de dados.

    **Estatísticas coletadas:**
    - Posse de bola, finalizações, escanteios, faltas
    - Cartões amarelos e vermelhos
    - xG (gols esperados) e xG sofrido
    - Passes, precisão de passes, desarmes, interceptações
    - Defesas do goleiro
    """,
)
def scrape_match_statistics(match_id: int, db: Session = Depends(get_db)):
    """Busca estatísticas de uma partida no FBref e salva no banco."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    service = FBrefService(db)
    service.scrape_and_save_match_statistics(match.fbref_id)
    db.refresh(match)
    return match