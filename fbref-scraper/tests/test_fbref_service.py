from app.models import Match, MatchStats, Player, Team
from app.services.fbref import FBrefService


def _teams(db_session):
    home = Team(name="Time A", fbref_id="time-a", league="Serie-A")
    away = Team(name="Time B", fbref_id="time-b", league="Serie-A")
    other = Team(name="Time C", fbref_id="time-c", league="Serie-A")
    db_session.add_all([home, away, other])
    db_session.commit()
    return home, away, other


def test_existing_match_is_updated_during_scrape(db_session):
    home, away, _ = _teams(db_session)
    match = Match(
        home_team_id=home.id,
        away_team_id=away.id,
        competition="Serie-A",
        season="2024-2025",
        home_score=None,
        away_score=None,
        fbref_id="match-upsert",
    )
    db_session.add(match)
    db_session.commit()

    service = FBrefService(db_session)
    updated = service._get_or_create_match(
        {
            "fbref_id": "match-upsert",
            "home_team_fbref_id": "time-a",
            "away_team_fbref_id": "time-b",
            "competition": "Serie-A",
            "season": "2024-2025",
            "home_score": 2,
            "away_score": 1,
        }
    )
    db_session.commit()

    assert updated.id == match.id
    assert updated.home_score == 2
    assert updated.away_score == 1


def test_existing_player_moves_to_current_team(db_session, monkeypatch):
    home, _, other = _teams(db_session)
    player = Player(
        name="Jogador",
        fbref_id="jogador-1",
        team_id=home.id,
    )
    db_session.add(player)
    db_session.commit()

    service = FBrefService(db_session)
    monkeypatch.setattr(service.players_scraper, "get_player_details", lambda _: None)
    updated = service._get_or_create_player(
        {
            "name": "Jogador Atualizado",
            "fbref_id": "jogador-1",
            "position": "FW",
            "shirt_number": 9,
        },
        other.id,
    )
    db_session.commit()

    assert updated.id == player.id
    assert updated.team_id == other.id
    assert updated.name == "Jogador Atualizado"


def test_invalid_stats_do_not_replace_existing_data(db_session, monkeypatch):
    home, away, _ = _teams(db_session)
    match = Match(
        home_team_id=home.id,
        away_team_id=away.id,
        fbref_id="match-stats-safe",
    )
    db_session.add(match)
    db_session.commit()
    db_session.add_all(
        [
            MatchStats(match_id=match.id, team_id=home.id, is_home=True, xg=1.4, xg_against=0.8),
            MatchStats(match_id=match.id, team_id=away.id, is_home=False, xg=0.8, xg_against=1.4),
        ]
    )
    db_session.commit()

    service = FBrefService(db_session)
    monkeypatch.setattr(
        service.statistics_scraper,
        "get_match_statistics",
        lambda _: {
            "home_team": "Time A",
            "away_team": "Time B",
            "home_xg": None,
            "away_xg": None,
        },
    )

    assert service.scrape_and_save_match_statistics("match-stats-safe") is None
    assert db_session.query(MatchStats).filter(MatchStats.match_id == match.id).count() == 2
