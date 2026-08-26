import pytest


def test_create_team(client, sample_team_data):
    response = client.post("/api/v1/teams/", json=sample_team_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Flamengo"
    assert data["league"] == "Serie-A"
    assert "id" in data


def test_list_teams(client, sample_team_data):
    client.post("/api/v1/teams/", json=sample_team_data)
    response = client.get("/api/v1/teams/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1


def test_get_team(client, sample_team_data):
    create_response = client.post("/api/v1/teams/", json=sample_team_data)
    team_id = create_response.json()["id"]

    response = client.get(f"/api/v1/teams/{team_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Flamengo"


def test_get_team_not_found(client):
    response = client.get("/api/v1/teams/99999")
    assert response.status_code == 404


def test_update_team(client, sample_team_data):
    create_response = client.post("/api/v1/teams/", json=sample_team_data)
    team_id = create_response.json()["id"]

    update_data = {"stadium": "Maracanã"}
    response = client.put(f"/api/v1/teams/{team_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["stadium"] == "Maracanã"


def test_delete_team(client, sample_team_data):
    create_response = client.post("/api/v1/teams/", json=sample_team_data)
    team_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/teams/{team_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/teams/{team_id}")
    assert get_response.status_code == 404


def test_filter_teams_by_league(client, sample_team_data):
    client.post("/api/v1/teams/", json=sample_team_data)
    response = client.get("/api/v1/teams/", params={"league": "Serie-A"})
    assert response.status_code == 200
    data = response.json()
    assert all(team["league"] == "Serie-A" for team in data)


def test_delete_team_with_associations_is_rejected(client, sample_team_data, sample_team2_data):
    team = client.post("/api/v1/teams/", json=sample_team_data).json()
    other = client.post("/api/v1/teams/", json=sample_team2_data).json()
    client.post(
        "/api/v1/matches/",
        json={
            "home_team_id": team["id"],
            "away_team_id": other["id"],
            "fbref_id": "protected-team-match",
        },
    )

    response = client.delete(f"/api/v1/teams/{team['id']}")
    assert response.status_code == 409
