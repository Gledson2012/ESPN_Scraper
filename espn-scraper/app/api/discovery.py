from datetime import datetime, timezone
from typing import Optional
from urllib.parse import quote

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_
from sqlalchemy.orm import Session, aliased

from app.api.security import public_rate_limiter
from app.database import get_db
from app.models import Match, MatchStats, Player, Team
from app.schemas import (
    CatalogOption,
    CatalogResponse,
    OverviewMatch,
    OverviewResponse,
    OverviewTotals,
    SearchResponse,
    SearchResult,
    SyncResourceStatus,
    SyncStatusResponse,
)
from app.scrapers.espn import ESPN_LEAGUE_SLUGS

router = APIRouter(tags=["Informações"])


def _now_utc() -> datetime:
    return datetime.now(timezone.utc)


def _db_now() -> datetime:
    """Retorna um datetime sem timezone para comparar com colunas legadas."""
    return _now_utc().replace(tzinfo=None)


def _match_preview(match: Match, teams_by_id: dict[int, Team]) -> OverviewMatch:
    home = teams_by_id.get(match.home_team_id)
    away = teams_by_id.get(match.away_team_id)
    return OverviewMatch(
        id=match.id,
        home_team_id=match.home_team_id,
        away_team_id=match.away_team_id,
        home_team=home.name if home else f"Time {match.home_team_id}",
        away_team=away.name if away else f"Time {match.away_team_id}",
        competition=match.competition,
        season=match.season,
        match_date=match.match_date,
        home_score=match.home_score,
        away_score=match.away_score,
    )


@router.get(
    "/overview",
    response_model=OverviewResponse,
    dependencies=[Depends(public_rate_limiter)],
    summary="Resumo operacional do painel",
    description="Retorna KPIs e partidas recentes/próximas em uma única chamada.",
)
def get_overview(
    competition: Optional[str] = Query(None, description="Filtrar por competição"),
    season: Optional[str] = Query(None, description="Filtrar por temporada"),
    db: Session = Depends(get_db),
):
    match_query = db.query(Match)
    if competition:
        match_query = match_query.filter(Match.competition == competition)
    if season:
        match_query = match_query.filter(Match.season == season)

    completed_filter = and_(Match.home_score.is_not(None), Match.away_score.is_not(None))
    upcoming_filter = and_(
        Match.match_date.is_not(None),
        Match.match_date >= _db_now(),
        or_(Match.home_score.is_(None), Match.away_score.is_(None)),
    )
    total_matches = match_query.count()
    completed_matches = match_query.filter(completed_filter).count()
    upcoming_matches = match_query.filter(upcoming_filter).count()

    previews_query = match_query.filter(upcoming_filter).order_by(Match.match_date.asc()).limit(5)
    next_matches = previews_query.all()
    recent_matches = (
        match_query.filter(completed_filter)
        .order_by(Match.match_date.desc())
        .limit(5)
        .all()
    )
    team_ids = {
        team_id
        for match in [*next_matches, *recent_matches]
        for team_id in (match.home_team_id, match.away_team_id)
    }
    teams_by_id = {
        team.id: team
        for team in db.query(Team).filter(Team.id.in_(team_ids)).all()
    } if team_ids else {}

    return OverviewResponse(
        generated_at=_now_utc(),
        competition=competition,
        season=season,
        totals=OverviewTotals(
            teams=db.query(Team).count(),
            players=db.query(Player).count(),
            matches=total_matches,
            completed_matches=completed_matches,
            upcoming_matches=upcoming_matches,
            stats=db.query(MatchStats).count(),
        ),
        next_matches=[_match_preview(match, teams_by_id) for match in next_matches],
        recent_matches=[_match_preview(match, teams_by_id) for match in recent_matches],
    )


@router.get(
    "/sync/status",
    response_model=SyncStatusResponse,
    dependencies=[Depends(public_rate_limiter)],
    summary="Status da sincronização",
    description="Informa volume e última atualização de cada recurso persistido.",
)
def get_sync_status(db: Session = Depends(get_db)):
    resources = [
        ("teams", Team),
        ("players", Player),
        ("matches", Match),
        ("stats", MatchStats),
    ]
    statuses = []
    for resource, model in resources:
        statuses.append(
            SyncResourceStatus(
                resource=resource,
                count=db.query(model).count(),
                last_updated_at=db.query(func.max(model.updated_at)).scalar(),
            )
        )
    return SyncStatusResponse(generated_at=_now_utc(), resources=statuses)


@router.get(
    "/catalog",
    response_model=CatalogResponse,
    dependencies=[Depends(public_rate_limiter)],
    summary="Opções para filtros",
    description="Lista competições suportadas e valores existentes no banco.",
)
def get_catalog(db: Session = Depends(get_db)):
    canonical_competitions = []
    seen_slugs = set()
    for code, slug in ESPN_LEAGUE_SLUGS.items():
        if slug in seen_slugs:
            continue
        seen_slugs.add(slug)
        canonical_competitions.append(
            CatalogOption(code=code, name=code.replace("-", " "))
        )

    return CatalogResponse(
        competitions=canonical_competitions,
        seasons=[value for (value,) in db.query(Match.season).filter(Match.season.is_not(None)).distinct().order_by(Match.season).all()],
        positions=[value for (value,) in db.query(Player.position).filter(Player.position.is_not(None)).distinct().order_by(Player.position).all()],
        nationalities=[value for (value,) in db.query(Player.nationality).filter(Player.nationality.is_not(None)).distinct().order_by(Player.nationality).all()],
        countries=[value for (value,) in db.query(Team.country).filter(Team.country.is_not(None)).distinct().order_by(Team.country).all()],
    )


@router.get(
    "/search",
    response_model=SearchResponse,
    dependencies=[Depends(public_rate_limiter)],
    summary="Busca global",
    description="Busca times, jogadores e partidas por texto.",
)
def search(
    q: str = Query(..., min_length=2, max_length=100, description="Texto da busca"),
    types: Optional[str] = Query(None, description="Tipos separados por vírgula: team,player,match"),
    limit: int = Query(10, ge=1, le=50, description="Máximo de resultados por tipo"),
    db: Session = Depends(get_db),
):
    requested_types = {
        value.strip().lower()
        for value in (types.split(",") if types else ["team", "player", "match"])
        if value.strip()
    }
    allowed_types = {"team", "player", "match"}
    if not requested_types:
        requested_types = allowed_types
    invalid_types = requested_types - allowed_types
    if invalid_types:
        raise HTTPException(
            status_code=422,
            detail=f"Tipos de busca inválidos: {', '.join(sorted(invalid_types))}",
        )

    pattern = f"%{q.strip()}%"
    results: list[SearchResult] = []

    if "team" in requested_types:
        teams = (
            db.query(Team)
            .filter(or_(Team.name.ilike(pattern), Team.short_name.ilike(pattern), Team.country.ilike(pattern)))
            .order_by(Team.name)
            .limit(limit)
            .all()
        )
        results.extend(
            SearchResult(
                type="team",
                id=team.id,
                title=team.name,
                subtitle=" · ".join(value for value in (team.league, team.country) if value) or None,
                path=f"/times/{team.id}",
            )
            for team in teams
        )

    if "player" in requested_types:
        players = (
            db.query(Player)
            .filter(or_(Player.name.ilike(pattern), Player.full_name.ilike(pattern), Player.nationality.ilike(pattern)))
            .order_by(Player.name)
            .limit(limit)
            .all()
        )
        results.extend(
            SearchResult(
                type="player",
                id=player.id,
                title=player.name,
                subtitle=player.nationality or "Jogador",
                path=f"/jogadores?search={quote(player.name)}",
            )
            for player in players
        )

    if "match" in requested_types:
        home_team = aliased(Team)
        away_team = aliased(Team)
        matches = (
            db.query(Match, home_team.name, away_team.name)
            .join(home_team, Match.home_team_id == home_team.id)
            .join(away_team, Match.away_team_id == away_team.id)
            .filter(
                or_(
                    home_team.name.ilike(pattern),
                    away_team.name.ilike(pattern),
                    Match.competition.ilike(pattern),
                )
            )
            .order_by(Match.match_date.desc())
            .limit(limit)
            .all()
        )
        for match, home_name, away_name in matches:
            details = " · ".join(value for value in (match.competition, match.season) if value) or None
            results.append(
                SearchResult(
                    type="match",
                    id=match.id,
                    title=f"{home_name} x {away_name}",
                    subtitle=details,
                    path=f"/partidas/{match.id}",
                )
            )

    return SearchResponse(query=q.strip(), results=results, total=len(results))
