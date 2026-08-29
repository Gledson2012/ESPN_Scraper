import pytest

from app.models import MatchStats


def test_predict_match(client, sample_stats_data):
    team1, team2 = sample_stats_data

    request_data = {
        "home_team_id": team1["id"],
        "away_team_id": team2["id"],
    }

    response = client.post("/api/v1/predictions/", json=request_data)
    assert response.status_code == 200
    data = response.json()

    # Verificar campos da resposta
    assert data["home_team_id"] == team1["id"]
    assert data["away_team_id"] == team2["id"]
    assert 0 <= data["home_win_probability"] <= 1
    assert 0 <= data["draw_probability"] <= 1
    assert 0 <= data["away_win_probability"] <= 1
    assert data["predicted_home_score"] >= 0
    assert data["predicted_away_score"] >= 0
    assert 0 <= data["over_2_5_probability"] <= 1
    assert 0 <= data["btts_probability"] <= 1
    assert 0 <= data["confidence"] <= 1
    assert data["model_version"] == "1.1.0"

    # As probabilidades devem somar aproximadamente 1
    total = (
        data["home_win_probability"]
        + data["draw_probability"]
        + data["away_win_probability"]
    )
    assert abs(total - 1.0) < 0.01


def test_predict_match_team_not_found(client):
    request_data = {
        "home_team_id": 99999,
        "away_team_id": 99998,
    }

    response = client.post("/api/v1/predictions/", json=request_data)
    assert response.status_code == 404


def test_predict_match_insufficient_data(client, sample_team_data, sample_team2_data):
    # Criar times sem estatísticas
    team1 = client.post("/api/v1/teams/", json=sample_team_data).json()
    team2 = client.post("/api/v1/teams/", json=sample_team2_data).json()

    request_data = {
        "home_team_id": team1["id"],
        "away_team_id": team2["id"],
    }

    response = client.post("/api/v1/predictions/", json=request_data)
    assert response.status_code == 400


def test_predict_match_fallback_away_only_stats(client, sample_team_data, sample_team2_data, db_session):
    """
    Time da casa com apenas jogos como visitante: a previsão deve funcionar
    via fallback (usando todas as partidas) em vez de retornar 400.
    """
    team1 = client.post("/api/v1/teams/", json=sample_team_data).json()
    team2 = client.post("/api/v1/teams/", json=sample_team2_data).json()

    match = client.post(
        "/api/v1/matches/",
        json={
            "home_team_id": team1["id"],
            "away_team_id": team2["id"],
            "competition": "Serie-A",
            "season": "2024-2025",
            "fbref_id": "fallback-match",
        },
    ).json()

    # Team 1 (que será o mandante na previsão) só tem estatísticas como visitante
    db_session.add_all([
        MatchStats(match_id=match["id"], team_id=team1["id"], is_home=False, xg=1.5, xg_against=1.2),
        MatchStats(match_id=match["id"], team_id=team2["id"], is_home=True, xg=1.1, xg_against=1.4),
    ])
    db_session.commit()

    response = client.post(
        "/api/v1/predictions/",
        json={"home_team_id": team1["id"], "away_team_id": team2["id"]},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["predicted_home_score"] >= 0
    assert data["predicted_away_score"] >= 0


def test_predict_match_can_filter_history_by_competition(client, sample_stats_data):
    team1, team2 = sample_stats_data
    response = client.post(
        "/api/v1/predictions/",
        json={
            "home_team_id": team1["id"],
            "away_team_id": team2["id"],
            "competition": "Outra-Liga",
        },
    )
    assert response.status_code == 400
