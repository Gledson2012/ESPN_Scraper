import logging

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from app.services.cloudbet import CloudbetService
from app.schemas.odds import EventOdds, MatchOddsResponse, SoccerOddsResponse

router = APIRouter(prefix="/odds", tags=["Odds"])
cloudbet_service = CloudbetService()
logger = logging.getLogger(__name__)


def _cloudbet_error(operation: str) -> HTTPException:
    logger.exception("Erro ao %s na Cloudbet", operation)
    return HTTPException(status_code=502, detail="Não foi possível consultar a Cloudbet")


@router.get(
    "/sports",
    summary="Listar esportes disponíveis",
    description="Obtém a lista de esportes disponíveis na Cloudbet.",
)
async def get_sports():
    """Obtém a lista de esportes disponíveis na Cloudbet."""
    try:
        return await cloudbet_service.get_sports()
    except Exception:
        raise _cloudbet_error("buscar esportes")


@router.get(
    "/competitions",
    summary="Listar competições de futebol",
    description="Obtém as competições de futebol disponíveis na Cloudbet.",
)
async def get_competitions(sport_key: str = Query("soccer", description="Chave do esporte", examples=["soccer"])):
    """Obtém competições de futebol disponíveis."""
    try:
        return await cloudbet_service.get_competitions(sport_key)
    except Exception:
        raise _cloudbet_error("buscar competições")


@router.get(
    "/competition/{competition_key}/events",
    summary="Eventos de uma competição",
    description="Obtém os eventos de uma competição específica com odds.",
)
async def get_competition_events(
    competition_key: str,
    sport_key: str = Query("soccer", description="Chave do esporte", examples=["soccer"]),
):
    """Obtém eventos de uma competição com odds."""
    try:
        events = await cloudbet_service.get_competition_events(competition_key, sport_key)
        return {"events": events, "total": len(events)}
    except HTTPException:
        raise
    except Exception:
        raise _cloudbet_error("buscar eventos da competição")


@router.get(
    "/soccer",
    response_model=SoccerOddsResponse,
    summary="Odds de futebol",
    description="""
    Obtém odds de partidas de futebol da Cloudbet.

    **Filtros disponíveis:**
    - `competition_key`: Filtra por competição específica
    """,
)
async def get_soccer_odds(
    competition_key: Optional[str] = Query(
        None,
        min_length=1,
        description="Filtrar por competição",
        examples=["br-serie-a"],
    )
):
    """Obtém odds de partidas de futebol da Cloudbet."""
    try:
        odds_data = await cloudbet_service.get_soccer_odds(competition_key)
        events = []
        for item in odds_data:
            event = EventOdds(
                event_id=item["event_id"],
                event_name=item["event_name"],
                home_team=item.get("home_team"),
                away_team=item.get("away_team"),
                start_time=item.get("start_time"),
                competition=item.get("competition"),
                markets=item.get("markets", {}),
                status=item.get("status"),
            )
            events.append(event)
        return SoccerOddsResponse(events=events, total=len(events))
    except Exception:
        raise _cloudbet_error("buscar odds de futebol")


@router.get(
    "/match",
    response_model=MatchOddsResponse,
    summary="Odds de uma partida específica",
    description="Busca odds para uma partida específica entre dois times.",
)
async def get_match_odds(
    home_team: str = Query(..., min_length=1, description="Time da casa", examples=["Flamengo"]),
    away_team: str = Query(..., min_length=1, description="Time visitante", examples=["Palmeiras"]),
):
    """Busca odds para uma partida específica entre dois times."""
    try:
        result = await cloudbet_service.get_match_odds(home_team, away_team)
        if not result:
            raise HTTPException(
                status_code=404,
                detail=f"Partida entre {home_team} e {away_team} não encontrada",
            )
        return MatchOddsResponse(
            event_id=result["event_id"],
            event_name=result["event_name"],
            start_time=result.get("start_time"),
            home_team=result.get("home_team", home_team),
            away_team=result.get("away_team", away_team),
            markets=result.get("markets", {}),
        )
    except HTTPException:
        raise
    except Exception:
        raise _cloudbet_error("buscar odds da partida")


@router.get(
    "/event/{event_id}",
    summary="Odds de um evento específico",
    description="Obtém odds de um evento específico pelo seu ID.",
)
async def get_event_odds(event_id: str):
    """Obtém odds de um evento específico pelo ID."""
    try:
        return await cloudbet_service.get_event_odds(event_id)
    except Exception:
        raise _cloudbet_error("buscar odds do evento")


@router.get(
    "/event/{event_id}/markets",
    summary="Mercados de um evento",
    description="Obtém os mercados de apostas de um evento específico.",
)
async def get_event_markets(event_id: str):
    """Obtém mercados de apostas de um evento específico."""
    try:
        return await cloudbet_service.get_event_markets(event_id)
    except Exception:
        raise _cloudbet_error("buscar mercados do evento")
