def test_list_and_get_match_stats(client, sample_stats_data):
    client_team1, _ = sample_stats_data
    matches = client.get("/api/v1/matches/").json()
    match_id = matches[0]["id"]

    response = client.get("/api/v1/stats/", params={"match_id": match_id})
    assert response.status_code == 200
    stats = response.json()
    assert len(stats) == 2
    assert stats[0]["team_id"] == client_team1["id"]

    detail = client.get(f"/api/v1/stats/{stats[0]['id']}")
    assert detail.status_code == 200
    assert detail.json()["match_id"] == match_id

    nested = client.get(f"/api/v1/matches/{match_id}/stats")
    assert nested.status_code == 200
    assert len(nested.json()) == 2


def test_create_update_and_delete_stats(client, sample_match_data):
    match_data, team1, _ = sample_match_data
    match = client.post("/api/v1/matches/", json=match_data).json()
    payload = {
        "match_id": match["id"],
        "team_id": team1["id"],
        "is_home": True,
        "xg": 1.6,
        "xg_against": 0.7,
    }

    created = client.post("/api/v1/stats/", json=payload)
    assert created.status_code == 201
    stat_id = created.json()["id"]

    updated = client.put(f"/api/v1/stats/{stat_id}", json={"xg": 2.0})
    assert updated.status_code == 200
    assert updated.json()["xg"] == 2.0

    deleted = client.delete(f"/api/v1/stats/{stat_id}")
    assert deleted.status_code == 204
    assert client.get(f"/api/v1/stats/{stat_id}").status_code == 404


def test_stats_reject_team_not_in_match(client, sample_match_data, sample_team_data):
    match_data, _, _ = sample_match_data
    match = client.post("/api/v1/matches/", json=match_data).json()
    unrelated = client.post(
        "/api/v1/teams/",
        json={**sample_team_data, "name": "Time sem partida", "espn_id": "unrelated"},
    ).json()

    response = client.post(
        "/api/v1/stats/",
        json={
            "match_id": match["id"],
            "team_id": unrelated["id"],
            "is_home": False,
            "xg": 1.0,
        },
    )
    assert response.status_code == 422


def test_team_summary_and_nested_resources(client, sample_stats_data):
    team1, _ = sample_stats_data

    summary = client.get(f"/api/v1/teams/{team1['id']}/summary")
    assert summary.status_code == 200
    assert summary.json()["wins"] == 1
    assert summary.json()["points"] == 3
    assert summary.json()["stats_available"] == 1

    matches = client.get(f"/api/v1/teams/{team1['id']}/matches")
    assert matches.status_code == 200
    assert len(matches.json()) == 1

    players = client.get(f"/api/v1/teams/{team1['id']}/players")
    assert players.status_code == 200
    assert players.json() == []
