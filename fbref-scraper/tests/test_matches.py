import pytest


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