"""Regras para identificar a temporada vigente em cada competição."""

from datetime import date


# Competições disputadas no ano civil. As demais competições suportadas pelo
# projeto seguem o calendário europeu (ex.: 2026-2027).
CALENDAR_YEAR_LEAGUES = frozenset(
    {
        "serie-a",
        "brasileirao-serie-a",
        "serie a",
        "brasileirão série a",
        "serie-b",
        "copa-do-brasil",
        "liga-argentina",
        "libertadores",
        "sudamericana",
        "mls",
        "world-cup",
    }
)


def _normalize_league(league: str | None) -> str:
    return " ".join((league or "").strip().lower().split())


def current_season(league: str | None = None, today: date | None = None) -> str:
    """Retorna o identificador da temporada vigente na ESPN.

    Competições de calendário, como o Brasileirão, Libertadores e MLS, usam
    somente o ano. As demais usam o formato ``AAAA-AAAA`` e mudam de temporada
    em julho, o que também funciona para consultas feitas entre janeiro e
    junho (por exemplo, janeiro de 2026 retorna ``2025-2026``).

    ``today`` existe para permitir testes determinísticos e não deve ser
    necessário em chamadas normais.
    """
    reference_date = today or date.today()
    if _normalize_league(league) in CALENDAR_YEAR_LEAGUES:
        return str(reference_date.year)

    start_year = reference_date.year if reference_date.month >= 7 else reference_date.year - 1
    return f"{start_year}-{start_year + 1}"


def resolve_season(league: str | None, season: str | None = None) -> str:
    """Preserva uma temporada informada ou usa a temporada vigente."""
    normalized_season = (season or "").strip()
    return normalized_season or current_season(league)
