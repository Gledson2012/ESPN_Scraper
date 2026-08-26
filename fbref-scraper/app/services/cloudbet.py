import httpx
import logging
from typing import Optional, Dict, Any, List
from app.config import settings

logger = logging.getLogger(__name__)

# Mercados primários para futebol
SOCCER_MARKETS = [
    "soccer.match_odds",
    "soccer.total_goals",
    "soccer.asian_handicap",
]


class CloudbetService:
    """Serviço para integração com a API da Cloudbet (v2)."""

    def __init__(self):
        self.base_url = settings.CLOUDBET_BASE_URL.rstrip("/")
        self.api_key = settings.CLOUDBET_API_KEY
        self.timeout = settings.REQUEST_TIMEOUT

    def _headers(self) -> Dict[str, str]:
        headers = {
            "Accept": "application/json",
            "User-Agent": settings.USER_AGENT,
        }
        if self.api_key:
            headers["X-Api-Key"] = self.api_key
        return headers

    async def _get(self, path: str, params: Optional[Dict] = None, params_list: Optional[List] = None) -> Dict[str, Any]:
        """Faz uma requisição GET à API da Cloudbet."""
        url = f"{self.base_url}{path}"
        request_params = params_list if params_list is not None else params
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(url, headers=self._headers(), params=request_params)
            response.raise_for_status()
            return response.json()

    async def get_sports(self) -> List[Dict[str, Any]]:
        """Obtém lista de esportes disponíveis."""
        data = await self._get("/sports")
        return data.get("sports", [])

    async def get_competitions(self, sport_key: str = "soccer") -> List[Dict[str, Any]]:
        """Obtém competições de um esporte, agrupadas por categoria."""
        data = await self._get(f"/sports/{sport_key}")
        competitions = []
        for category in data.get("categories", []):
            for competition in category.get("competitions", []):
                competition["category"] = category.get("name", "")
                competition["category_key"] = category.get("key", "")
                competitions.append(competition)
        return competitions

    async def get_competition_events(
        self, competition_key: str, sport_key: str = "soccer"
    ) -> List[Dict[str, Any]]:
        """Obtém eventos (partidas) de uma competição com odds."""
        # Parâmetros com múltiplos mercados
        params_list = [("include-pretrading", "true"), ("locale", "en")]
        markets = SOCCER_MARKETS if sport_key == "soccer" else []
        for market in markets:
            params_list.append(("markets", market))

        url = f"/sports/{sport_key}/competitions/{competition_key}/events"
        data = await self._get(url, params_list=params_list)
        return data.get("events", [])

    async def get_event_odds(self, event_id: str) -> Dict[str, Any]:
        """Busca odds de um evento por ID."""
        try:
            data = await self._get(f"/events/{event_id}")
            return {
                "event_id": data.get("id", event_id),
                "event_name": data.get("name", ""),
                "home": data.get("home"),
                "away": data.get("away"),
                "markets": data.get("markets", {}),
                "start_time": data.get("startTime", ""),
            }
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                logger.warning(f"Evento {event_id} não encontrado na Cloudbet")
                return {}
            raise

    async def get_event_markets(self, event_id: str) -> Dict[str, Any]:
        """Obtém mercados de apostas de um evento."""
        odds = await self.get_event_odds(event_id)
        return odds.get("markets", {})

    async def search_events(self, competition_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Busca eventos de futebol, opcionalmente filtrando por competição."""
        if competition_key:
            return await self.get_competition_events(competition_key)

        # Busca eventos de competições principais
        all_events = []
        competitions = await self.get_competitions("soccer")
        # Filtra competições com eventos
        active_competitions = [
            c for c in competitions
            if c.get("eventCount", 0) > 0
        ][:5]  # Limita a 5 competições para não sobrecarregar

        for comp in active_competitions:
            try:
                events = await self.get_competition_events(comp["key"])
                for event in events:
                    if event.get("type") != "EVENT_TYPE_OUTRIGHT":
                        event["competition"] = {
                            "key": comp["key"],
                            "name": comp["name"],
                        }
                        all_events.append(event)
            except Exception as e:
                logger.warning(f"Erro ao buscar eventos de {comp.get('name')}: {e}")

        return all_events

    async def get_soccer_odds(self, competition_key: Optional[str] = None) -> List[Dict[str, Any]]:
        """Obtém odds de futebol, opcionalmente filtrado por competição."""
        events = await self.search_events(competition_key)

        odds_list = []
        for event in events:
            home = event.get("home", {}) or {}
            away = event.get("away", {}) or {}
            odds_list.append({
                "event_id": event["id"],
                "event_name": event.get("name", ""),
                "home_team": home.get("name", ""),
                "away_team": away.get("name", ""),
                "start_time": event.get("startTime", ""),
                "competition": event.get("competition", {}),
                "markets": event.get("markets", {}),
                "status": event.get("status", ""),
            })

        return odds_list

    async def get_match_odds(self, home_team: str, away_team: str) -> Optional[Dict[str, Any]]:
        """Busca odds para uma partida específica entre dois times."""
        events = await self.search_events()
        requested_home = home_team.strip().casefold()
        requested_away = away_team.strip().casefold()
        if not requested_home or not requested_away:
            return None

        for event in events:
            home = event.get("home", {}) or {}
            away = event.get("away", {}) or {}
            home_name = home.get("name", "").strip().casefold()
            away_name = away.get("name", "").strip().casefold()
            if not home_name or not away_name:
                continue

            if (
                requested_home in home_name or home_name in requested_home
            ) and (
                requested_away in away_name or away_name in requested_away
            ):
                return {
                    "event_id": event["id"],
                    "event_name": event.get("name", ""),
                    "home_team": home.get("name", ""),
                    "away_team": away.get("name", ""),
                    "start_time": event.get("startTime", ""),
                    "competition": event.get("competition", {}),
                    "markets": event.get("markets", {}),
                    "status": event.get("status", ""),
                }
        return None
