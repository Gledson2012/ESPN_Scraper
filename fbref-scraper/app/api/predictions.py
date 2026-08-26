import math
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Match, MatchStats, Team
from app.schemas import PredictionRequest, PredictionResponse

router = APIRouter(prefix="/predictions", tags=["Previsões"])

MODEL_VERSION = "1.1.0"

# Constantes do modelo
DEFAULT_LEAGUE_AVG_GOALS = 2.7  # Usado quando não há dados suficientes
MAX_GOALS = 20
MAX_LAMBDA = 10.0


@router.post(
    "/",
    response_model=PredictionResponse,
    summary="Gerar previsão de partida",
    description="""
    Gera uma previsão para uma partida entre dois times usando um **modelo Poisson** baseado nas estatísticas históricas.

    **Como funciona:**
    1. Obtém as estatísticas históricas dos times (gols marcados, sofridos e xG)
    2. Calcula as forças de ataque e defesa, diferenciando mando de campo (casa/fora)
    3. Aplica a distribuição de Poisson para calcular as probabilidades de cada resultado
    4. Calcula probabilidades de over 2.5 gols e ambos marcarem (BTTS)

    **Requisitos:**
    - Os times devem existir no banco de dados
    - É necessário ter estatísticas de partidas anteriores (execute o scraping de partidas primeiro)
    """,
)
def predict_match(
    request: PredictionRequest,
    db: Session = Depends(get_db),
):
    """
    Gera uma previsão para uma partida entre dois times.

    Utiliza um modelo Poisson baseado nas estatísticas históricas
    dos times (gols marcados, sofridos e xG), diferenciando
    mandos de campo (casa/fora).
    """
    home_team = db.query(Team).filter(Team.id == request.home_team_id).first()
    away_team = db.query(Team).filter(Team.id == request.away_team_id).first()

    if not home_team or not away_team:
        raise HTTPException(status_code=404, detail="Time(s) não encontrado(s)")

    # Obter estatísticas históricas dos times (casa/fora é aplicado nas funções de força)
    home_stats = _get_team_stats(
        db,
        request.home_team_id,
        competition=request.competition,
        season=request.season,
    )
    away_stats = _get_team_stats(
        db,
        request.away_team_id,
        competition=request.competition,
        season=request.season,
    )

    if not _has_usable_stats(home_stats) or not _has_usable_stats(away_stats):
        raise HTTPException(
            status_code=400,
            detail="Dados insuficientes para gerar previsão. Execute o scraping de partidas primeiro.",
        )

    # Calcular forças de ataque e defesa (diferenciando casa/fora)
    # Média de gols da liga calculada dinamicamente
    league_avg_goals = _calculate_league_avg_goals(
        db,
        competition=request.competition,
        season=request.season,
    )
    if league_avg_goals <= 0:
        league_avg_goals = DEFAULT_LEAGUE_AVG_GOALS
    average_goals_per_team = league_avg_goals / 2

    home_attack = _calculate_attack_strength(
        home_stats, is_home=True, average_goals_per_team=average_goals_per_team
    )
    home_defense = _calculate_defense_strength(
        home_stats, is_home=True, average_goals_per_team=average_goals_per_team
    )
    away_attack = _calculate_attack_strength(
        away_stats, is_home=False, average_goals_per_team=average_goals_per_team
    )
    away_defense = _calculate_defense_strength(
        away_stats, is_home=False, average_goals_per_team=average_goals_per_team
    )

    # Calcular gols esperados (lambda do Poisson)
    home_lambda = min(
        MAX_LAMBDA,
        max(0.1, average_goals_per_team * home_attack * away_defense),
    )
    away_lambda = min(
        MAX_LAMBDA,
        max(0.1, average_goals_per_team * away_attack * home_defense),
    )

    # Calcular probabilidades
    home_win_prob = _poisson_match_probability(home_lambda, away_lambda, "home")
    draw_prob = _poisson_match_probability(home_lambda, away_lambda, "draw")
    away_win_prob = _poisson_match_probability(home_lambda, away_lambda, "away")

    # Normalizar probabilidades
    total = home_win_prob + draw_prob + away_win_prob
    if total > 0:
        home_win_prob /= total
        draw_prob /= total
        away_win_prob /= total

    # Probabilidade de over 2.5
    over_2_5_prob = _over_2_5_probability(home_lambda, away_lambda)

    # Probabilidade de ambos marcarem (BTTS)
    btts_prob = (1 - math.exp(-home_lambda)) * (1 - math.exp(-away_lambda))

    # Confiança baseada na quantidade de dados
    home_samples = sum(1 for stat in home_stats if _has_usable_stat(stat))
    away_samples = sum(1 for stat in away_stats if _has_usable_stat(stat))
    confidence = min(0.95, 0.5 + home_samples * 0.01 + away_samples * 0.01)

    return PredictionResponse(
        home_team_id=request.home_team_id,
        away_team_id=request.away_team_id,
        home_win_probability=round(home_win_prob, 4),
        draw_probability=round(draw_prob, 4),
        away_win_probability=round(away_win_prob, 4),
        predicted_home_score=round(home_lambda, 2),
        predicted_away_score=round(away_lambda, 2),
        over_2_5_probability=round(over_2_5_prob, 4),
        btts_probability=round(btts_prob, 4),
        confidence=round(confidence, 4),
        model_version=MODEL_VERSION,
    )


def _get_team_stats(
    db: Session,
    team_id: int,
    competition: str | None = None,
    season: str | None = None,
) -> List[MatchStats]:
    """Obtém estatísticas do time, opcionalmente limitadas a uma competição/temporada."""
    query = db.query(MatchStats).join(Match, Match.id == MatchStats.match_id).filter(
        MatchStats.team_id == team_id
    )
    if competition:
        query = query.filter(Match.competition == competition)
    if season:
        query = query.filter(Match.season == season)
    return query.all()


def _calculate_league_avg_goals(
    db: Session,
    competition: str | None = None,
    season: str | None = None,
) -> float:
    """Calcula a média de gols usando o recorte de competição informado."""
    total_goals = 0
    total_matches = 0

    query = db.query(Match)
    if competition:
        query = query.filter(Match.competition == competition)
    if season:
        query = query.filter(Match.season == season)

    matches = query.all()
    for match in matches:
        if match.home_score is not None and match.away_score is not None:
            total_goals += match.home_score + match.away_score
            total_matches += 1

    if total_matches == 0:
        return DEFAULT_LEAGUE_AVG_GOALS

    return total_goals / total_matches


def _calculate_attack_strength(
    stats: List[MatchStats],
    is_home: bool,
    average_goals_per_team: float = DEFAULT_LEAGUE_AVG_GOALS / 2,
) -> float:
    """
    Calcula a força de ataque de um time.

    Diferencia se as estatísticas são de jogos em casa ou fora.
    Se não houver dados para o mando informado, usa todas as partidas.
    """
    if not stats:
        return 1.0

    subset = [s for s in stats if s.is_home == is_home]
    if not subset:
        subset = stats  # fallback: usa todas as partidas

    total_xg = 0
    matches = 0

    for stat in subset:
        if _is_valid_metric(stat.xg):
            total_xg += stat.xg
            matches += 1

    if matches == 0:
        return 1.0

    avg_goals_for = total_xg / matches
    # Força relativa (1.0 = média da liga)
    return avg_goals_for / max(0.1, average_goals_per_team)


def _calculate_defense_strength(
    stats: List[MatchStats],
    is_home: bool,
    average_goals_per_team: float = DEFAULT_LEAGUE_AVG_GOALS / 2,
) -> float:
    """
    Calcula a força de defesa de um time.

    Diferencia se as estatísticas são de jogos em casa ou fora.
    Se não houver dados para o mando informado, usa todas as partidas.
    """
    if not stats:
        return 1.0

    subset = [s for s in stats if s.is_home == is_home]
    if not subset:
        subset = stats  # fallback: usa todas as partidas

    total_xg_against = 0
    matches = 0

    for stat in subset:
        if _is_valid_metric(stat.xg_against):
            total_xg_against += stat.xg_against
            matches += 1

    if matches == 0:
        return 1.0

    avg_goals_against = total_xg_against / matches
    # Força relativa (1.0 = média da liga)
    return avg_goals_against / max(0.1, average_goals_per_team)


def _is_valid_metric(value: float | None) -> bool:
    """Aceita apenas métricas numéricas finitas e não negativas."""
    return value is not None and math.isfinite(value) and value >= 0


def _has_usable_stat(stat: MatchStats) -> bool:
    return _is_valid_metric(stat.xg) or _is_valid_metric(stat.xg_against)


def _has_usable_stats(stats: List[MatchStats]) -> bool:
    return any(_has_usable_stat(stat) for stat in stats)


def _poisson_probability(k: int, lam: float) -> float:
    """Calcula a probabilidade de Poisson P(X = k)."""
    if lam < 0 or not math.isfinite(lam):
        return 0.0
    return (lam**k * math.exp(-lam)) / math.factorial(k)


def _poisson_match_probability(home_lambda: float, away_lambda: float, outcome: str) -> float:
    """
    Calcula a probabilidade de um resultado usando distribuição de Poisson.

    Args:
        home_lambda: Gols esperados do time da casa
        away_lambda: Gols esperados do time visitante
        outcome: 'home', 'draw' ou 'away'

    Returns:
        Probabilidade do resultado
    """
    prob = 0.0

    for i in range(MAX_GOALS + 1):
        for j in range(MAX_GOALS + 1):
            p = _poisson_probability(i, home_lambda) * _poisson_probability(j, away_lambda)
            if outcome == "home" and i > j:
                prob += p
            elif outcome == "draw" and i == j:
                prob += p
            elif outcome == "away" and i < j:
                prob += p

    return prob


def _over_2_5_probability(home_lambda: float, away_lambda: float) -> float:
    """Calcula a probabilidade de over 2.5 gols."""
    prob_under = 0.0

    for i in range(MAX_GOALS + 1):
        for j in range(MAX_GOALS + 1):
            if i + j <= 2:
                p = _poisson_probability(i, home_lambda) * _poisson_probability(j, away_lambda)
                prob_under += p

    return max(0.0, min(1.0, 1 - prob_under))
