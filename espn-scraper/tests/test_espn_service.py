from app.models import Match, MatchStats, Player, Team
from app.services.espn_service import ESPNService


def _teams(db_session):
    home = Team(name="Time A", espn_id="time-a", league="Serie-A")
    away = Team(name="Time B", espn_id="time-b", league="Serie-A")
    other = Team(name="Time C", espn_id="time-c", league="Serie-A")
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
        espn_id="match-upsert",
    )
    db_session.add(match)
    db_session.commit()

    service = ESPNService(db_session)
    updated = service._get_or_create_match(
        {
            "espn_id": "match-upsert",
            "home_team_espn_id": "time-a",
            "away_team_espn_id": "time-b",
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
        espn_id="jogador-1",
        team_id=home.id,
    )
    db_session.add(player)
    db_session.commit()

    service = ESPNService(db_session)
    monkeypatch.setattr(service.players_scraper, "get_player_details", lambda _: None)
    updated = service._get_or_create_player(
        {
            "name": "Jogador Atualizado",
            "espn_id": "jogador-1",
            "position": "FW",
            "shirt_number": 9,
        },
        other.id,
    )
    db_session.commit()

    assert updated.id == player.id
    assert updated.team_id == other.id
    assert updated.name == "Jogador Atualizado"


def test_player_scrape_reconciles_current_squad_without_deleting_history(db_session, monkeypatch):
    team = Team(name="Real Madrid", espn_id="real-madrid", league="La-Liga")
    db_session.add(team)
    db_session.flush()
    stale = Player(name="Jogador que saiu", espn_id="stale-player", team_id=team.id)
    db_session.add(stale)
    db_session.commit()

    service = ESPNService(db_session)
    monkeypatch.setattr(
        service.players_scraper,
        "get_team_players",
        lambda team_id, season, league: [
            {
                "name": "Jogador atual",
                "espn_id": "current-player",
                "position": "FW",
            }
        ],
    )
    monkeypatch.setattr(service.players_scraper, "get_player_details", lambda _: None)

    saved = service.scrape_and_save_players("real-madrid")

    assert [player.espn_id for player in saved] == ["current-player"]
    assert db_session.query(Player).filter(Player.id == stale.id).one().team_id is None
    assert db_session.query(Player).filter(Player.espn_id == "current-player").one().team_id == team.id


def test_historical_player_scrape_does_not_reconcile_current_squad(db_session, monkeypatch):
    team = Team(name="Real Madrid", espn_id="real-madrid-history", league="La-Liga")
    db_session.add(team)
    db_session.flush()
    stale = Player(name="Jogador atual", espn_id="current-player", team_id=team.id)
    db_session.add(stale)
    db_session.commit()

    service = ESPNService(db_session)
    monkeypatch.setattr(
        service.players_scraper,
        "get_team_players",
        lambda team_id, season, league: [
            {"name": "Jogador histórico", "espn_id": "historical-player"}
        ],
    )
    monkeypatch.setattr(service.players_scraper, "get_player_details", lambda _: None)

    service.scrape_and_save_players("real-madrid-history", "2024-2025")

    assert db_session.query(Player).filter(Player.id == stale.id).one().team_id == team.id


def test_invalid_stats_do_not_replace_existing_data(db_session, monkeypatch):
    home, away, _ = _teams(db_session)
    match = Match(
        home_team_id=home.id,
        away_team_id=away.id,
        espn_id="match-stats-safe",
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

    service = ESPNService(db_session)
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


def test_partial_stats_do_not_replace_existing_data(db_session, monkeypatch):
    """Uma resposta com apenas um dos lados não pode apagar o histórico."""
    home, away, _ = _teams(db_session)
    match = Match(
        home_team_id=home.id,
        away_team_id=away.id,
        espn_id="match-stats-partial",
    )
    db_session.add(match)
    db_session.commit()
    db_session.add_all(
        [
            MatchStats(match_id=match.id, team_id=home.id, is_home=True, xg=1.4, shots=12),
            MatchStats(match_id=match.id, team_id=away.id, is_home=False, xg=0.8, shots=7),
        ]
    )
    db_session.commit()

    service = ESPNService(db_session)
    monkeypatch.setattr(
        service.statistics_scraper,
        "get_match_statistics",
        lambda _: {"home_team": "Time A", "home_xg": 2.0},
    )

    assert service.scrape_and_save_match_statistics("match-stats-partial") is None
    saved = db_session.query(MatchStats).filter(MatchStats.match_id == match.id).order_by(MatchStats.is_home.desc()).all()
    assert [(stat.xg, stat.shots) for stat in saved] == [(1.4, 12), (0.8, 7)]


def test_complete_stats_update_without_erasing_missing_fields(db_session, monkeypatch):
    """Um scrape completo atualiza o que veio e conserva colunas ausentes."""
    home, away, _ = _teams(db_session)
    match = Match(home_team_id=home.id, away_team_id=away.id, espn_id="match-stats-upsert")
    db_session.add(match)
    db_session.commit()
    db_session.add_all(
        [
            MatchStats(match_id=match.id, team_id=home.id, is_home=True, xg=1.4, shots=12),
            MatchStats(match_id=match.id, team_id=away.id, is_home=False, xg=0.8, shots=7),
        ]
    )
    db_session.commit()

    service = ESPNService(db_session)
    monkeypatch.setattr(
        service.statistics_scraper,
        "get_match_statistics",
        lambda _: {
            "home_xg": 2.0,
            "away_xg": 1.0,
            "home_possession": 58.0,
            "away_possession": 42.0,
        },
    )

    service.scrape_and_save_match_statistics("match-stats-upsert")
    saved = db_session.query(MatchStats).filter(MatchStats.match_id == match.id).order_by(MatchStats.is_home.desc()).all()
    assert [(stat.xg, stat.shots, stat.possession) for stat in saved] == [
        (2.0, 12, 58.0),
        (1.0, 7, 42.0),
    ]
