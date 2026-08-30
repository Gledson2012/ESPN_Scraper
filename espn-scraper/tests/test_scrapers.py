"""Testes do mapeamento e das requisições ESPN (sem acesso à rede)."""

import pytest

from app.scrapers.matches import MatchesScraper
from app.scrapers.teams import TeamsScraper
from app.scrapers.espn import resolve_espn_league


def _resolve_teams(league: str) -> str:
    return resolve_espn_league(league)


def _resolve_matches(league: str) -> str:
    return resolve_espn_league(league)


def test_brasileirao_maps_to_comp_24():
    assert _resolve_teams("Serie-A") == "bra.1"
    assert _resolve_teams("Brasileirao-Serie-A") == "bra.1"
    assert _resolve_teams("Serie A") == "bra.1"


def test_serie_a_italy_not_captured_by_serie_a():
    """'Serie-A-Italy' não pode resolver para o Brasileirão (bug de substring)."""
    assert _resolve_teams("Serie-A-Italy") == "ita.1"
    assert _resolve_matches("Serie-A-Italy") == "ita.1"


def test_premier_league_maps_to_comp_9():
    assert _resolve_teams("Premier-League") == "eng.1"
    assert _resolve_matches("Premier-League") == "eng.1"


def test_other_leagues():
    assert _resolve_teams("La-Liga") == "esp.1"
    assert _resolve_teams("Bundesliga") == "ger.1"
    assert _resolve_teams("Ligue-1") == "fra.1"
    assert _resolve_teams("Eredivisie") == "ned.1"
    assert _resolve_teams("Primeira-Liga") == "por.1"
    assert _resolve_teams("MLS") == "usa.1"
    assert _resolve_teams("Liga-MX") == "mex.1"
    assert _resolve_teams("Libertadores") == "conmebol.libertadores"
    assert _resolve_teams("Champions-League") == "uefa.champions"
    assert _resolve_teams("Serie-B") == "bra.2"
    assert _resolve_teams("Copa-do-Brasil") == "bra.copa_do_brazil"
    assert _resolve_teams("Liga-Argentina") == "arg.1"
    assert _resolve_teams("Sudamericana") == "conmebol.sudamericana"
    assert _resolve_teams("World-Cup") == "fifa.world"
    assert _resolve_teams("Championship") == "eng.2"
    assert _resolve_teams("Europa-League") == "uefa.europa"
    assert _resolve_teams("Conference-League") == "uefa.europa.conf"
    assert _resolve_teams("Copa-del-Rey") == "esp.copa_del_rey"
    assert _resolve_teams("Coppa-Italia") == "ita.coppa_italia"
    assert _resolve_teams("DFB-Pokal") == "ger.dfb_pokal"


def test_unknown_league_is_rejected():
    with pytest.raises(ValueError, match="Liga não suportada pela ESPN"):
        _resolve_teams("Liga-Inexistente")


def test_partial_name_match_is_rejected():
    """Evita que uma entrada ambígua consulte uma competição diferente."""
    with pytest.raises(ValueError, match="Liga não suportada pela ESPN"):
        _resolve_teams("Premier")


def test_team_scraper_builds_current_espn_stats_url(monkeypatch):
    scraper = TeamsScraper()
    captured = {}
    monkeypatch.setattr(
        scraper,
        "_get_json",
        lambda path, params: (
            captured.update(path=path, params=params)
            or {"sports": [{"leagues": [{"slug": "esp.1", "teams": []}]}]}
        ),
    )

    assert scraper.get_league_teams("La-Liga", "2026-2027") == []
    assert captured == {"path": "esp.1/teams", "params": {"limit": 1000}}


def test_match_scraper_builds_current_espn_schedule_url(monkeypatch):
    scraper = MatchesScraper()
    captured = {}
    monkeypatch.setattr(
        scraper,
        "_get_json",
        lambda path, params: (
            captured.update(path=path, params=params)
            or {"events": []}
        ),
    )

    assert scraper.get_league_matches("Serie-A", "2026") == []
    assert captured == {
        "path": "bra.1/scoreboard",
        "params": {"dates": "20260101-20261231", "limit": 1000},
    }


def test_espn_team_scraper_normalizes_team_payload(monkeypatch):
    scraper = TeamsScraper()
    monkeypatch.setattr(
        scraper,
        "_get_json",
        lambda path, params: {
            "sports": [
                {
                    "leagues": [
                        {
                            "slug": "esp.1",
                            "teams": [
                                {
                                    "team": {
                                        "id": "86",
                                        "displayName": "Real Madrid",
                                        "shortDisplayName": "Real Madrid",
                                        "abbreviation": "RMA",
                                        "logos": [{"href": "https://cdn.test/86.png"}],
                                    }
                                }
                            ],
                        }
                    ]
                }
            ]
        },
    )

    assert scraper.get_league_teams("La-Liga", "2026-2027") == [
        {
            "name": "Real Madrid",
            "short_name": "Real Madrid",
            "country": "Spain",
            "espn_id": "86",
            "logo_url": "https://cdn.test/86.png",
            "league": "La-Liga",
            "season": "2026-2027",
        }
    ]


def test_espn_player_scraper_converts_roster_fields(monkeypatch):
    from app.scrapers.players import PlayersScraper

    scraper = PlayersScraper()
    monkeypatch.setattr(
        scraper,
        "_get_json",
        lambda path, params: {
            "athletes": [
                {
                    "id": "231388",
                    "displayName": "Kylian Mbappé",
                    "fullName": "Kylian Mbappé Lottin",
                    "jersey": "10",
                    "citizenship": "France",
                    "dateOfBirth": "1998-12-20T08:00Z",
                    "height": 5.8,
                    "weight": 161,
                    "position": {"abbreviation": "F"},
                }
            ]
        },
    )

    player = scraper.get_team_players("86", "2026-2027", "La-Liga")[0]
    assert player["espn_id"] == "231388"
    assert player["position"] == "FW"
    assert player["shirt_number"] == 10
    assert player["height_cm"] == 14.73
    assert player["weight_kg"] == 73.03


def test_espn_match_scraper_keeps_scheduled_scores_empty(monkeypatch):
    scraper = MatchesScraper()
    monkeypatch.setattr(
        scraper,
        "_get_json",
        lambda path, params: {
            "events": [
                {
                    "id": "401882899",
                    "date": "2026-08-30T15:00Z",
                    "competitions": [
                        {
                            "status": {"type": {"state": "pre"}},
                            "venue": {"fullName": "Santiago Bernabéu"},
                            "attendance": 0,
                            "competitors": [
                                {
                                    "homeAway": "home",
                                    "team": {"id": "86", "displayName": "Real Madrid"},
                                    "score": "0",
                                },
                                {
                                    "homeAway": "away",
                                    "team": {"id": "99", "displayName": "Málaga"},
                                    "score": "0",
                                },
                            ],
                        }
                    ],
                }
            ]
        },
    )

    match = scraper.get_league_matches("La-Liga", "2026-2027")[0]
    assert match["home_score"] is None
    assert match["away_score"] is None
    assert match["venue"] == "Santiago Bernabéu"
