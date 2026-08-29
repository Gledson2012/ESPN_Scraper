import pytest

from app.api import matches as matches_api


def test_create_match(client, sample_match_data):
    match_data, _, _ = sample_match_data
    response = client.post("/api/v1/matches/", json=match_data)
    assert response.status_code == 201
    data = response.json()
    assert data["home_score"] == 2
    assert data["away_score"] == 1
    assert "id" in data


def test_list_matches(client, sample_match_data):
    match_data, _, _ = sample_match_data
    client.post("/api/v1/matches/", json=match_data)
    response = client.get("/api/v1/matches/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_match(client, sample_match_data):
    match_data, _, _ = sample_match_data
    create_response = client.post("/api/v1/matches/", json=match_data)
    match_id = create_response.json()["id"]

    response = client.get(f"/api/v1/matches/{match_id}")
    assert response.status_code == 200
    assert response.json()["competition"] == "Serie-A"


def test_get_match_not_found(client):
    response = client.get("/api/v1/matches/99999")
    assert response.status_code == 404


def test_update_match(client, sample_match_data):
    match_data, _, _ = sample_match_data
    create_response = client.post("/api/v1/matches/", json=match_data)
    match_id = create_response.json()["id"]

    update_data = {"home_score": 3}
    response = client.put(f"/api/v1/matches/{match_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["home_score"] == 3


def test_delete_match(client, sample_match_data):
    match_data, _, _ = sample_match_data
    create_response = client.post("/api/v1/matches/", json=match_data)
    match_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/matches/{match_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/matches/{match_id}")
    assert get_response.status_code == 404


def test_filter_matches_by_competition(client, sample_match_data):
    match_data, _, _ = sample_match_data
    client.post("/api/v1/matches/", json=match_data)
    response = client.get("/api/v1/matches/", params={"competition": "Serie-A"})
    assert response.status_code == 200
    data = response.json()
    assert all(match["competition"] == "Serie-A" for match in data)


def test_filter_matches_by_team(client, sample_match_data):
    match_data, team1, _ = sample_match_data
    client.post("/api/v1/matches/", json=match_data)
    response = client.get("/api/v1/matches/", params={"team_id": team1["id"]})
    assert response.status_code == 200
    data = response.json()
    assert all(
        match["home_team_id"] == team1["id"] or match["away_team_id"] == team1["id"]
        for match in data
    )


def test_create_match_rejects_unknown_teams(client):
    response = client.post(
        "/api/v1/matches/",
        json={"home_team_id": 99999, "away_team_id": 99998},
    )
    assert response.status_code == 404


def test_create_match_rejects_same_team(client, sample_team_data):
    team = client.post("/api/v1/teams/", json=sample_team_data).json()
    response = client.post(
        "/api/v1/matches/",
        json={"home_team_id": team["id"], "away_team_id": team["id"]},
    )
    assert response.status_code == 422


FAKE_LIVE_MATCH = {
    "league": "Serie-A",
    "espn_event_id": "401882899",
    "status": "2nd Half",
    "clock": "67' - 2nd Half",
    "match_date": "2026-08-29T18:30:00",
    "venue": "Maracanã",
    "home_team": "Flamengo",
    "away_team": "Palmeiras",
    "home_score": 1,
    "away_score": 0,
    "home_team_logo": None,
    "away_team_logo": None,
}


def test_list_live_matches_returns_espn_data(client, monkeypatch):
    monkeypatch.setattr(
        matches_api.MatchesScraper,
        "get_live_matches",
        lambda self, league: [FAKE_LIVE_MATCH] if league == "Serie-A" else [],
    )

    response = client.get("/api/v1/matches/live", params={"league": "Serie-A"})

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["espn_event_id"] == "401882899"
    assert data[0]["home_team"] == "Flamengo"
    assert data[0]["home_score"] == 1
    assert data[0]["status"] == "2nd Half"


def test_list_live_matches_rejects_unknown_league(client):
    response = client.get("/api/v1/matches/live", params={"league": "Liga-Inexistente"})

    assert response.status_code == 422
    assert "não suportada" in response.json()["detail"].lower()


def test_list_live_matches_handles_espn_outage(client, monkeypatch):
    import requests

    def boom(self, league):
        raise requests.exceptions.ConnectionError("ESPN indisponível")

    monkeypatch.setattr(matches_api.MatchesScraper, "get_live_matches", boom)

    response = client.get("/api/v1/matches/live", params={"league": "Serie-A"})

    assert response.status_code == 502
