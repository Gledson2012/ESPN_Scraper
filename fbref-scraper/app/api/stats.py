from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match, MatchStats, Team
from app.schemas import MatchStatsCreate, MatchStatsResponse, MatchStatsUpdate

router = APIRouter(prefix="/stats", tags=["Estatísticas"])


def _validate_stat_owner(
    db: Session,
    match_id: int,
    team_id: int,
    is_home: bool,
) -> Match:
    """Garante que as estatísticas pertencem a um dos times da partida."""
    match = db.query(Match).filter(Match.id == match_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Partida não encontrada")

    if not db.query(Team.id).filter(Team.id == team_id).first():
        raise HTTPException(status_code=404, detail="Time não encontrado")

    expected_is_home = team_id == match.home_team_id
    if team_id not in (match.home_team_id, match.away_team_id):
        raise HTTPException(
            status_code=422,
            detail="O time precisa participar da partida informada",
        )
    if is_home != expected_is_home:
        raise HTTPException(
            status_code=422,
            detail="O campo is_home não corresponde ao mando da partida",
        )
    return match


@router.get(
    "/",
    response_model=List[MatchStatsResponse],
    summary="Listar estatísticas",
    description="Lista estatísticas com filtros opcionais por partida e time.",
)
def list_stats(
    match_id: Optional[int] = Query(None, gt=0, description="Filtrar por partida", examples=[1]),
    team_id: Optional[int] = Query(None, gt=0, description="Filtrar por time", examples=[1]),
    skip: int = Query(0, ge=0, description="Quantidade de registros para pular"),
    limit: int = Query(100, ge=1, le=1000, description="Quantidade máxima de registros"),
    db: Session = Depends(get_db),
):
    """Lista estatísticas de partidas."""
    query = db.query(MatchStats)
    if match_id:
        query = query.filter(MatchStats.match_id == match_id)
    if team_id:
        query = query.filter(MatchStats.team_id == team_id)
    return query.order_by(MatchStats.match_id.desc(), MatchStats.is_home.desc()).offset(skip).limit(limit).all()


@router.get(
    "/{stat_id}",
    response_model=MatchStatsResponse,
    summary="Obter estatística por ID",
    description="Retorna um registro de estatísticas específico.",
)
def get_stat(stat_id: int = Path(..., gt=0, description="ID da estatística"), db: Session = Depends(get_db)):
    """Obtém uma estatística pelo ID."""
    stat = db.query(MatchStats).filter(MatchStats.id == stat_id).first()
    if not stat:
        raise HTTPException(status_code=404, detail="Estatística não encontrada")
    return stat


@router.post(
    "/",
    response_model=MatchStatsResponse,
    status_code=201,
    summary="Criar estatísticas",
    description="Cria estatísticas para um dos times de uma partida.",
)
def create_stat(stat: MatchStatsCreate, db: Session = Depends(get_db)):
    """Cria um registro de estatísticas validando partida, time e mando."""
    _validate_stat_owner(db, stat.match_id, stat.team_id, stat.is_home)
    if db.query(MatchStats.id).filter(
        MatchStats.match_id == stat.match_id,
        MatchStats.team_id == stat.team_id,
    ).first():
        raise HTTPException(status_code=409, detail="Já existem estatísticas para esse time nessa partida")

    db_stat = MatchStats(**stat.model_dump())
    db.add(db_stat)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Não foi possível criar as estatísticas")
    db.refresh(db_stat)
    return db_stat


@router.put(
    "/{stat_id}",
    response_model=MatchStatsResponse,
    summary="Atualizar estatísticas",
    description="Atualiza os números de um registro de estatísticas existente.",
)
def update_stat(
    stat_id: int,
    updates: MatchStatsUpdate,
    db: Session = Depends(get_db),
):
    """Atualiza estatísticas sem permitir trocar a partida ou o time."""
    stat = db.query(MatchStats).filter(MatchStats.id == stat_id).first()
    if not stat:
        raise HTTPException(status_code=404, detail="Estatística não encontrada")

    values = updates.model_dump(exclude_unset=True)
    if "is_home" in values:
        if values["is_home"] is None:
            raise HTTPException(status_code=422, detail="O campo is_home não pode ser nulo")
        _validate_stat_owner(db, stat.match_id, stat.team_id, values["is_home"])

    for key, value in values.items():
        setattr(stat, key, value)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Não foi possível atualizar as estatísticas")
    db.refresh(stat)
    return stat


@router.delete(
    "/{stat_id}",
    status_code=204,
    summary="Excluir estatísticas",
    description="Exclui um registro de estatísticas.",
)
def delete_stat(stat_id: int, db: Session = Depends(get_db)):
    """Exclui estatísticas pelo ID."""
    stat = db.query(MatchStats).filter(MatchStats.id == stat_id).first()
    if not stat:
        raise HTTPException(status_code=404, detail="Estatística não encontrada")
    db.delete(stat)
    db.commit()
