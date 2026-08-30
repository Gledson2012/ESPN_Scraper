from datetime import date

from app.api import matches as matches_api
from app.api import teams as teams_api
from app.models import Team
from app.seasons import current_season, resolve_season
from app.services.espn_service import ESPNService


def test_current_season_uses_calendar_year_for_brazilian_competitions():
    reference_date = date(2026, 8, 29)

    assert current_season("Serie-A", reference_date) == "2026"
    assert current_season("Libertadores", reference_date) == "2026"
    assert current_season("MLS", reference_date) == "2026"
    assert current_season("Serie-B", reference_date) == "2026"
    assert current_season("Copa-do-Brasil", reference_date) == "2026"
    assert current_season("Liga-Argentina", reference_date) == "2026"
    assert current_season("Sudamericana", reference_date) == "2026"
    assert current_season("World-Cup", reference_date) == "2026"


def test_current_season_uses_cross_year_format_for_european_competitions():
    assert current_season("Premier-League", date(2026, 8, 29)) == "2026-2027"
    assert current_season("La-Liga", date(2026, 1, 15)) == "2025-2026"


def test_explicit_season_is_preserved():
    assert resolve_season("Serie-A", "  2024  ") == "2024"
    assert resolve_season("Serie-A", None) == current_season("Serie-A")


def test_team_scrape_defaults_to_current_league_season(client, monkeypatch):
    captured = {}

    def fake_scrape(self, league, season):
        captured.update(league=league, season=season)
        return []

    monkeypatch.setattr(teams_api.ESPNService, "scrape_and_save_teams", fake_scrape)

    response = client.post("/api/v1/teams/scrape?league=Premier-League")

    assert response.status_code == 200
    assert captured == {
        "league": "Premier-League",
        "season": current_season("Premier-League"),
    }


def test_match_scrape_keeps_explicit_historical_season(client, monkeypatch):
    captured = {}

    def fake_scrape(self, league, season):
        captured.update(league=league, season=season)
        return []

    monkeypatch.setattr(matches_api.ESPNService, "scrape_and_save_matches", fake_scrape)

    response = client.post(
        "/api/v1/matches/scrape?league=Serie-A&season=2024"
    )

    assert response.status_code == 200
    assert captured == {"league": "Serie-A", "season": "2024"}


def test_player_service_uses_team_league_for_current_season(db_session, monkeypatch):
    team = Team(name="Real Madrid", espn_id="real-madrid", league="La-Liga")
    db_session.add(team)
    db_session.commit()

    service = ESPNService(db_session)
    captured = {}

    def fake_scrape(team_id, season, league):
        captured.update(team_id=team_id, season=season, league=league)
        return []

    monkeypatch.setattr(service.players_scraper, "get_team_players", fake_scrape)

    assert service.scrape_and_save_players("real-madrid") == []
    assert captured == {
        "team_id": "real-madrid",
        "season": current_season("La-Liga"),
        "league": "La-Liga",
    }
