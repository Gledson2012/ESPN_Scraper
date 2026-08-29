import pytest


def test_create_player(client, sample_player_data):
    response = client.post("/api/v1/players/", json=sample_player_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Gabriel Barbosa"
    assert data["position"] == "FW"
    assert "id" in data


def test_list_players(client, sample_player_data):
    response = client.get("/api/v1/players/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


def test_get_player(client, sample_player_data):
    create_response = client.post("/api/v1/players/", json=sample_player_data)
    player_id = create_response.json()["id"]

    response = client.get(f"/api/v1/players/{player_id}")
    assert response.status_code == 200
    assert response.json()["name"] == "Gabriel Barbosa"


def test_get_player_not_found(client):
    response = client.get("/api/v1/players/99999")
    assert response.status_code == 404


def test_update_player(client, sample_player_data):
    create_response = client.post("/api/v1/players/", json=sample_player_data)
    player_id = create_response.json()["id"]

    update_data = {"shirt_number": 10}
    response = client.put(f"/api/v1/players/{player_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["shirt_number"] == 10


def test_delete_player(client, sample_player_data):
    create_response = client.post("/api/v1/players/", json=sample_player_data)
    player_id = create_response.json()["id"]

    response = client.delete(f"/api/v1/players/{player_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/v1/players/{player_id}")
    assert get_response.status_code == 404


def test_filter_players_by_position(client, sample_player_data):
    client.post("/api/v1/players/", json=sample_player_data)
    response = client.get("/api/v1/players/", params={"position": "FW"})
    assert response.status_code == 200
    data = response.json()
    assert all(player["position"] == "FW" for player in data)