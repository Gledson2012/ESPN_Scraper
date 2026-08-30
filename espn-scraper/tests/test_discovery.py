def test_overview_returns_filtered_totals(client, sample_match_data):
    match_data, _, _ = sample_match_data
    client.post("/api/v1/matches/", json=match_data)

    response = client.get(
        "/api/v1/overview",
        params={"competition": "Serie-A", "season": "2024-2025"},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["totals"]["matches"] == 1
    assert data["totals"]["completed_matches"] == 1
    assert data["recent_matches"][0]["home_team"] == "Flamengo"


def test_sync_status_returns_resource_counts(client, sample_team_data):
    client.post("/api/v1/teams/", json=sample_team_data)

    response = client.get("/api/v1/sync/status")

    assert response.status_code == 200
    resources = {item["resource"]: item for item in response.json()["resources"]}
    assert resources["teams"]["count"] == 1
    assert resources["players"]["count"] == 0


def test_catalog_returns_supported_competitions_and_values(client, sample_team_data):
    client.post("/api/v1/teams/", json=sample_team_data)

    response = client.get("/api/v1/catalog")

    assert response.status_code == 200
    data = response.json()
    assert any(item["code"] == "Serie-A" for item in data["competitions"])
    assert "Brasil" in data["countries"]


def test_global_search_returns_teams_players_and_matches(client, sample_match_data):
    match_data, team, _ = sample_match_data
    client.post("/api/v1/matches/", json=match_data)
    client.post(
        "/api/v1/players/",
        json={
            "name": "Gabriel Barbosa",
            "nationality": "Brasil",
            "position": "FW",
            "team_id": team["id"],
            "espn_id": "gabriel-barbosa-search",
        },
    )

    team_response = client.get("/api/v1/search", params={"q": "Flamengo", "types": "team"})
    player_response = client.get("/api/v1/search", params={"q": "Gabriel", "types": "player"})
    match_response = client.get("/api/v1/search", params={"q": "Palmeiras", "types": "match"})

    assert team_response.status_code == 200
    assert team_response.json()["results"][0]["path"] == f"/times/{team['id']}"
    assert player_response.status_code == 200
    assert player_response.json()["results"][0]["type"] == "player"
    assert match_response.status_code == 200
    assert match_response.json()["results"][0]["title"] == "Flamengo x Palmeiras"
