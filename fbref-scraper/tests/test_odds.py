import pytest
from unittest.mock import AsyncMock, patch
from app.services.cloudbet import CloudbetService


@pytest.fixture
def cloudbet_service():
    return CloudbetService()


@pytest.mark.asyncio
async def test_get_sports(cloudbet_service):
    """Testa a obtenção de esportes."""
    mock_data = {"sports": [{"key": "soccer", "name": "Futebol"}]}
    with patch.object(cloudbet_service, "_get", new=AsyncMock(return_value=mock_data)):
        result = await cloudbet_service.get_sports()
        assert result == [{"key": "soccer", "name": "Futebol"}]


@pytest.mark.asyncio
async def test_get_competitions(cloudbet_service):
    """Testa a obtenção de competições."""
    mock_data = {
        "categories": [
            {
                "name": "Brazil",
                "key": "brazil",
                "competitions": [
                    {"key": "soccer-brazil-brasileiro-serie-a", "name": "Brasileirão", "eventCount": 10}
                ],
            }
        ]
    }
    with patch.object(cloudbet_service, "_get", new=AsyncMock(return_value=mock_data)):
        result = await cloudbet_service.get_competitions("soccer")
        assert len(result) == 1
        assert result[0]["key"] == "soccer-brazil-brasileiro-serie-a"
        assert result[0]["category"] == "Brazil"
        assert result[0]["category_key"] == "brazil"


@pytest.mark.asyncio
async def test_get_competition_events(cloudbet_service):
    """Testa a obtenção de eventos de uma competição."""
    mock_data = {
        "events": [
            {"id": 123, "name": "Flamengo vs Palmeiras", "type": "EVENT_TYPE_MATCH"}
        ]
    }
    with patch.object(cloudbet_service, "_get", new=AsyncMock(return_value=mock_data)):
        result = await cloudbet_service.get_competition_events("soccer-brazil-brasileiro-serie-a")
        assert result == [{"id": 123, "name": "Flamengo vs Palmeiras", "type": "EVENT_TYPE_MATCH"}]


@pytest.mark.asyncio
async def test_get_soccer_odds(cloudbet_service):
    """Testa a obtenção de odds de futebol."""
    events = [
        {
            "id": 1,
            "name": "Flamengo vs Palmeiras",
            "type": "EVENT_TYPE_MATCH",
            "status": "TRADING",
            "startTime": "2026-04-10T20:00:00Z",
            "home": {"name": "Flamengo"},
            "away": {"name": "Palmeiras"},
            "markets": {"soccer.match_odds": {}},
            "competition": {"key": "soccer-brazil-brasileiro-serie-a", "name": "Brasileirão"},
        }
    ]
    with patch.object(cloudbet_service, "search_events", new=AsyncMock(return_value=events)):
        result = await cloudbet_service.get_soccer_odds()
        assert len(result) == 1
        assert result[0]["event_id"] == 1
        assert result[0]["home_team"] == "Flamengo"
        assert result[0]["away_team"] == "Palmeiras"
        assert result[0]["markets"] == {"soccer.match_odds": {}}


@pytest.mark.asyncio
async def test_get_match_odds_found(cloudbet_service):
    """Testa a busca de odds de uma partida específica."""
    events = [
        {
            "id": 1,
            "name": "Gremio vs Sao Paulo",
            "type": "EVENT_TYPE_MATCH",
            "status": "TRADING",
            "startTime": "2026-04-10T20:00:00Z",
            "home": {"name": "Gremio FB Porto Alegrense RS"},
            "away": {"name": "Sao Paulo FC SP"},
            "markets": {"soccer.match_odds": {}},
            "competition": {"key": "soccer-brazil-brasileiro-serie-a", "name": "Brasileirão"},
        }
    ]

    with patch.object(cloudbet_service, "search_events", new=AsyncMock(return_value=events)):
        result = await cloudbet_service.get_match_odds("Gremio", "Sao Paulo")
        assert result is not None
        assert result["event_id"] == 1
        assert result["home_team"] == "Gremio FB Porto Alegrense RS"
        assert result["away_team"] == "Sao Paulo FC SP"
        assert result["markets"] == {"soccer.match_odds": {}}


@pytest.mark.asyncio
async def test_get_match_odds_not_found(cloudbet_service):
    """Testa a busca de odds quando a partida não é encontrada."""
    events = [
        {
            "id": 1,
            "name": "Gremio vs Sao Paulo",
            "type": "EVENT_TYPE_MATCH",
            "home": {"name": "Gremio FB Porto Alegrense RS"},
            "away": {"name": "Sao Paulo FC SP"},
            "markets": {},
        }
    ]

    with patch.object(cloudbet_service, "search_events", new=AsyncMock(return_value=events)):
        result = await cloudbet_service.get_match_odds("TimeInexistente", "OutroTime")
        assert result is None


@pytest.mark.asyncio
async def test_get_event_odds(cloudbet_service):
    """Testa a obtenção de odds de um evento."""
    mock_data = {
        "id": 123,
        "name": "Flamengo vs Palmeiras",
        "type": "EVENT_TYPE_MATCH",
        "home": {"name": "Flamengo"},
        "away": {"name": "Palmeiras"},
        "markets": {"soccer.match_odds": {}},
        "startTime": "2026-04-10T20:00:00Z",
    }
    with patch.object(cloudbet_service, "_get", new=AsyncMock(return_value=mock_data)):
        result = await cloudbet_service.get_event_odds("123")
        assert result["event_id"] == 123
        assert result["markets"] == {"soccer.match_odds": {}}


@pytest.mark.asyncio
async def test_get_event_odds_not_found(cloudbet_service):
    """Testa a obtenção de odds quando o evento não existe."""
    import httpx
    from unittest.mock import AsyncMock

    mock_response = AsyncMock()
    mock_response.status_code = 404
    mock_error = httpx.HTTPStatusError("Not Found", request=AsyncMock(), response=mock_response)

    with patch.object(cloudbet_service, "_get", new=AsyncMock(side_effect=mock_error)):
        result = await cloudbet_service.get_event_odds("999")
        assert result == {}


@pytest.mark.asyncio
async def test_get_event_markets(cloudbet_service):
    """Testa a obtenção de mercados de um evento específico."""
    event = {
        "id": 123,
        "name": "Flamengo vs Palmeiras",
        "type": "EVENT_TYPE_MATCH",
        "home": {"name": "Flamengo"},
        "away": {"name": "Palmeiras"},
        "markets": {
            "soccer.match_odds": {
                "id": "soccer.match_odds",
                "name": "Match Odds",
                "selections": [],
            }
        },
        "startTime": "2026-04-10T20:00:00Z",
    }

    with patch.object(cloudbet_service, "get_event_odds", new=AsyncMock(return_value=event)):
        result = await cloudbet_service.get_event_markets("123")
        assert result == event["markets"]