import pytest


def test_predict_match(client, sample_stats_data):
    team1, team2 = sample_stats_data

    request_data = {
        "home_team_id": team1["id"],
        "away_team_id": team2["id"],
        "competition": "Serie-A",
        "season": "2024-2025",
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