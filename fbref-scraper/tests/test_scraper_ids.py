from app.scrapers.ids import extract_fbref_id


def test_extract_fbref_id_from_team_url():
    assert extract_fbref_id("/en/squads/639950ae/2026/", "squads") == "639950ae"


def test_extract_fbref_id_from_absolute_match_url():
    assert extract_fbref_id(
        "https://fbref.com/en/matches/abc123/report", "matches"
    ) == "abc123"


def test_extract_fbref_id_returns_none_for_invalid_url():
    assert extract_fbref_id("/en/teams/abc123", "squads") is None
