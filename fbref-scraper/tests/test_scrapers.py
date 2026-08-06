"""Testes do mapeamento de ligas para os códigos do FBref (sem acesso à rede)."""

from app.scrapers.matches import MatchesScraper
from app.scrapers.teams import TeamsScraper


def _resolve_teams(league: str) -> str:
    return TeamsScraper()._resolve_league_code(league)


def _resolve_matches(league: str) -> str:
    return MatchesScraper()._resolve_league_code(league)


def test_brasileirao_maps_to_comp_24():
    assert _resolve_teams("Serie-A") == "24"
    assert _resolve_teams("Brasileirao-Serie-A") == "24"
    assert _resolve_teams("Serie A") == "24"


def test_serie_a_italy_not_captured_by_serie_a():
    """'Serie-A-Italy' não pode resolver para o Brasileirão (bug de substring)."""
    assert _resolve_teams("Serie-A-Italy") == "11"
    assert _resolve_matches("Serie-A-Italy") == "11"


def test_premier_league_maps_to_comp_9():
    assert _resolve_teams("Premier-League") == "9"
    assert _resolve_matches("Premier-League") == "9"


def test_other_leagues():
    assert _resolve_teams("La-Liga") == "12"
    assert _resolve_teams("Bundesliga") == "20"
    assert _resolve_teams("Ligue-1") == "13"
    assert _resolve_teams("Eredivisie") == "23"
    assert _resolve_teams("Primeira-Liga") == "32"
    assert _resolve_teams("MLS") == "22"
    assert _resolve_teams("Liga-MX") == "31"
    assert _resolve_teams("Libertadores") == "18"
    assert _resolve_teams("Champions-League") == "8"


def test_unknown_league_falls_back_to_brasileirao():
    assert _resolve_teams("Liga-Inexistente") == "24"


def test_partial_name_match():
    """Busca parcial continua funcionando (ex: 'Premier' → Premier-League)."""
    assert _resolve_teams("Premier") == "9"
