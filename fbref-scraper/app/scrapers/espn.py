"""Cliente e scrapers para a API pública de futebol da ESPN.

Os nomes ``fbref_id`` continuam sendo usados no banco por compatibilidade com
o schema existente, mas os valores gravados por estes scrapers são IDs da ESPN.
"""

import logging
import re
import time
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from app.config import settings
from app.seasons import resolve_season

logger = logging.getLogger(__name__)

ESPN_API_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"

ESPN_LEAGUE_SLUGS = {
    "Serie-A": "bra.1",
    "Brasileirao-Serie-A": "bra.1",
    "Serie A": "bra.1",
    "Premier-League": "eng.1",
    "Serie-A-Italy": "ita.1",
    "La-Liga": "esp.1",
    "Bundesliga": "ger.1",
    "Ligue-1": "fra.1",
    "Eredivisie": "ned.1",
    "Primeira-Liga": "por.1",
    "MLS": "usa.1",
    "Liga-MX": "mex.1",
    "Libertadores": "conmebol.libertadores",
    "Champions-League": "uefa.champions",
    "Serie-B": "bra.2",
    "Copa-do-Brasil": "bra.copa_do_brazil",
    "Liga-Argentina": "arg.1",
    "Sudamericana": "conmebol.sudamericana",
    "World-Cup": "fifa.world",
    "Championship": "eng.2",
    "Europa-League": "uefa.europa",
    "Conference-League": "uefa.europa.conf",
    "Copa-del-Rey": "esp.copa_del_rey",
    "Coppa-Italia": "ita.coppa_italia",
    "DFB-Pokal": "ger.dfb_pokal",
}

ESPN_LEAGUE_COUNTRIES = {
    "Serie-A": "Brazil",
    "Brasileirao-Serie-A": "Brazil",
    "Serie A": "Brazil",
    "Premier-League": "England",
    "Serie-A-Italy": "Italy",
    "La-Liga": "Spain",
    "Bundesliga": "Germany",
    "Ligue-1": "France",
    "Eredivisie": "Netherlands",
    "Primeira-Liga": "Portugal",
    "MLS": "United States",
    "Liga-MX": "Mexico",
    "Libertadores": "South America",
    "Champions-League": "Europe",
    "Serie-B": "Brazil",
    "Copa-do-Brasil": "Brazil",
    "Liga-Argentina": "Argentina",
    "Sudamericana": "South America",
    "World-Cup": "International",
    "Championship": "England",
    "Europa-League": "Europe",
    "Conference-League": "Europe",
    "Copa-del-Rey": "Spain",
    "Coppa-Italia": "Italy",
    "DFB-Pokal": "Germany",
}

# Permite que estatísticas consultadas logo após a sincronização encontrem a
# competição do evento sem uma nova chamada de descoberta.
ESPN_EVENT_LEAGUES: Dict[str, str] = {}


def resolve_espn_league(league: str) -> str:
    """Resolve o código de competição aceito pela ESPN."""
    normalized = league.strip().lower()
    for name, slug in ESPN_LEAGUE_SLUGS.items():
        if name.lower() == normalized:
            return slug
    raise ValueError(f"Liga não suportada pela ESPN: '{league}'.")


def _season_year(league: str, season: Optional[str]) -> int:
    resolved = resolve_season(league, season)
    match = re.match(r"(\d{4})", resolved)
    if not match:
        raise ValueError(f"Temporada inválida: '{resolved}'.")
    return int(match.group(1))


def _season_date_range(league: str, season: Optional[str]) -> str:
    """Monta o intervalo que a ESPN aceita para uma temporada completa."""
    resolved = resolve_season(league, season)
    year = _season_year(league, resolved)
    if "-" not in resolved:
        return f"{year}0101-{year}1231"
    return f"{year}0801-{year + 1}0630"


def _parse_datetime(value: Any) -> Optional[datetime]:
    if not value or not isinstance(value, str):
        return None
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if parsed.tzinfo:
            parsed = parsed.astimezone(timezone.utc).replace(tzinfo=None)
        return parsed
    except ValueError:
        return None


def _safe_int(value: Any) -> Optional[int]:
    if value is None or value == "":
        return None
    try:
        return int(float(str(value).replace(",", ".")))
    except (TypeError, ValueError):
        return None


def _safe_float(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(str(value).replace(",", ".").replace("%", ""))
    except (TypeError, ValueError):
        return None


def _team_logo(team: dict) -> Optional[str]:
    if team.get("logo"):
        return team["logo"]
    logos = team.get("logos") or []
    return logos[0].get("href") if logos and logos[0].get("href") else None


def _athlete_photo(athlete: dict) -> Optional[str]:
    """Extrai a foto do atleta nos formatos usados pela API da ESPN."""
    headshot = athlete.get("headshot")
    if isinstance(headshot, dict) and headshot.get("href"):
        return headshot["href"]
    if isinstance(headshot, str) and headshot:
        return headshot

    for image in athlete.get("images") or []:
        if isinstance(image, dict) and image.get("href"):
            return image["href"]
        if isinstance(image, dict) and image.get("url"):
            return image["url"]
    return None


def _espn_id(value: str) -> str:
    """Aceita IDs novos e IDs prefixados por versões anteriores do adaptador."""
    return str(value).removeprefix("espn:")


class ESPNClient:
    """Cliente HTTP compartilhado pelos scrapers ESPN."""

    BASE_URL = ESPN_API_BASE

    def __init__(self):
        self.session = requests.Session()

    def _get_json(self, path: str, params: Optional[dict] = None, apply_delay: bool = True) -> dict:
        response = self.session.get(
            f"{self.BASE_URL}/{path.lstrip('/')}",
            params=params,
            timeout=settings.REQUEST_TIMEOUT,
        )
        response.raise_for_status()
        if apply_delay and settings.REQUEST_DELAY:
            time.sleep(settings.REQUEST_DELAY)
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("A ESPN retornou um payload JSON inválido.")
        return payload


class TeamsScraper(ESPNClient):
    """Scraper de equipes da ESPN, mantendo a interface legada do projeto."""

    def get_league_teams(self, league: str, season: Optional[str] = None) -> List[dict]:
        season = resolve_season(league, season)
        league_slug = resolve_espn_league(league)
        payload = self._get_json(f"{league_slug}/teams", {"limit": 1000})
        country = ESPN_LEAGUE_COUNTRIES.get(league)
        result: List[dict] = []

        for sport in payload.get("sports", []):
            for league_data in sport.get("leagues", []):
                if league_data.get("slug") != league_slug and len(sport.get("leagues", [])) > 1:
                    continue
                for item in league_data.get("teams", []):
                    team = item.get("team", item)
                    team_id = team.get("id")
                    name = team.get("displayName") or team.get("name")
                    if not team_id or not name:
                        continue
                    result.append(
                        {
                            "name": name,
                            "short_name": team.get("shortDisplayName") or team.get("abbreviation"),
                            "country": country,
                            "fbref_id": str(team_id),
                            "logo_url": _team_logo(team),
                            "league": league,
                            "season": season,
                        }
                    )

        logger.info("Encontrados %s times da ESPN para %s %s", len(result), league, season)
        return result

    def get_team_details(self, fbref_id: str) -> Optional[dict]:
        team_id = _espn_id(fbref_id)
        payload = self._get_json(f"teams/{team_id}")
        team = payload.get("team") or {}
        if not team:
            return None
        return {
            "fbref_id": team.get("id", team_id),
            "name": team.get("displayName") or team.get("name"),
            "short_name": team.get("shortDisplayName") or team.get("abbreviation"),
            "logo_url": _team_logo(team),
        }


class PlayersScraper(ESPNClient):
    """Scraper de elencos atuais da ESPN."""

    POSITION_MAP = {
        "G": "GK",
        "GK": "GK",
        "D": "DF",
        "DF": "DF",
        "M": "MF",
        "MF": "MF",
        "F": "FW",
        "FW": "FW",
    }

    def get_team_players(
        self,
        fbref_team_id: str,
        season: Optional[str] = None,
        league: Optional[str] = None,
    ) -> List[dict]:
        league = league or "La-Liga"
        season = resolve_season(league, season)
        league_slug = resolve_espn_league(league)
        year = _season_year(league, season)
        payload = self._get_json(
            f"{league_slug}/teams/{_espn_id(fbref_team_id)}/roster",
            {"season": year},
        )
        players: List[dict] = []

        for athlete in payload.get("athletes", []):
            athlete_id = athlete.get("id")
            name = athlete.get("displayName") or athlete.get("fullName")
            if not athlete_id or not name:
                continue
            position = athlete.get("position") or {}
            position_code = position.get("abbreviation") or position.get("name")
            position_code = self.POSITION_MAP.get(position_code, position_code)
            players.append(
                {
                    "name": name,
                    "full_name": athlete.get("fullName") or name,
                    "fbref_id": str(athlete_id),
                    "position": position_code,
                    "shirt_number": _safe_int(athlete.get("jersey")),
                    "nationality": athlete.get("citizenship"),
                    "photo_url": _athlete_photo(athlete),
                    "birth_date": _parse_datetime(athlete.get("dateOfBirth")),
                    # ESPN fornece altura em polegadas e peso em libras.
                    "height_cm": round(float(athlete["height"]) * 2.54, 2)
                    if athlete.get("height") is not None
                    else None,
                    "weight_kg": round(float(athlete["weight"]) / 2.20462, 2)
                    if athlete.get("weight") is not None
                    else None,
                }
            )

        logger.info(
            "Encontrados %s jogadores da ESPN para o time %s (%s)",
            len(players),
            fbref_team_id,
            season,
        )
        return players

    def get_player_details(self, fbref_player_id: str) -> Optional[dict]:
        # O endpoint de roster já entrega os campos disponíveis no modelo. A
        # ESPN não oferece um endpoint individual estável para este recurso.
        return {"fbref_id": _espn_id(fbref_player_id)}


class MatchesScraper(ESPNClient):
    """Scraper de calendário, resultados e detalhes de partidas da ESPN."""

    def get_league_matches(self, league: str, season: Optional[str] = None) -> List[dict]:
        season = resolve_season(league, season)
        league_slug = resolve_espn_league(league)
        payload = self._get_json(
            f"{league_slug}/scoreboard",
            {"dates": _season_date_range(league, season), "limit": 1000},
        )
        matches: List[dict] = []

        for event in payload.get("events", []):
            competitors = (event.get("competitions") or [{}])[0].get("competitors", [])
            home = next((item for item in competitors if item.get("homeAway") == "home"), None)
            away = next((item for item in competitors if item.get("homeAway") == "away"), None)
            if not home or not away:
                continue

            competition = (event.get("competitions") or [{}])[0]
            status = ((competition.get("status") or {}).get("type") or {}).get("state")
            home_score = _safe_int(home.get("score")) if status != "pre" else None
            away_score = _safe_int(away.get("score")) if status != "pre" else None
            venue = competition.get("venue") or {}
            event_id = str(event.get("id"))
            ESPN_EVENT_LEAGUES[event_id] = league_slug

            matches.append(
                {
                    "fbref_id": event_id,
                    "home_team": (home.get("team") or {}).get("displayName"),
                    "away_team": (away.get("team") or {}).get("displayName"),
                    "home_team_fbref_id": str(home.get("team", {}).get("id")),
                    "away_team_fbref_id": str(away.get("team", {}).get("id")),
                    "competition": league,
                    "league": league,
                    "season": season,
                    "match_date": _parse_datetime(event.get("date") or competition.get("date")),
                    "venue": venue.get("fullName"),
                    "attendance": _safe_int(competition.get("attendance")),
                    "home_score": home_score,
                    "away_score": away_score,
                }
            )

        logger.info("Encontradas %s partidas da ESPN para %s %s", len(matches), league, season)
        return matches

    def get_live_matches(self, league: str) -> List[dict]:
        """Retorna as partidas em andamento de uma liga neste momento.

        Consulta o scoreboard do dia na ESPN e mantém somente eventos com
        estado ``in`` (jogo em progresso). Não usa o atraso entre requisições
        porque consulta apenas o scoreboard atual.
        """
        league_slug = resolve_espn_league(league)
        payload = self._get_json(f"{league_slug}/scoreboard", {"limit": 400}, apply_delay=False)
        live: List[dict] = []

        for event in payload.get("events", []):
            status_type = ((event.get("status") or {}).get("type") or {})
            if status_type.get("state") != "in":
                continue

            competition = (event.get("competitions") or [{}])[0]
            competitors = competition.get("competitors", [])
            home = next((item for item in competitors if item.get("homeAway") == "home"), None)
            away = next((item for item in competitors if item.get("homeAway") == "away"), None)
            if not home or not away:
                continue

            event_id = str(event.get("id"))
            ESPN_EVENT_LEAGUES[event_id] = league_slug
            status = (
                status_type.get("shortDetail")
                or status_type.get("detail")
                or "Ao vivo"
            )

            live.append(
                {
                    "league": league,
                    "espn_event_id": event_id,
                    "status": status,
                    "clock": status_type.get("displayClock") or status,
                    "match_date": _parse_datetime(event.get("date") or competition.get("date")),
                    "venue": (competition.get("venue") or {}).get("fullName"),
                    "home_team": (home.get("team") or {}).get("displayName"),
                    "away_team": (away.get("team") or {}).get("displayName"),
                    "home_score": _safe_int(home.get("score")),
                    "away_score": _safe_int(away.get("score")),
                    "home_team_logo": _team_logo(home.get("team") or {}),
                    "away_team_logo": _team_logo(away.get("team") or {}),
                }
            )

        if live:
            logger.info("Encontradas %s partidas ao vivo na ESPN para %s", len(live), league)
        return live

    def _get_event_summary(self, event_id: str) -> dict:
        preferred = ESPN_EVENT_LEAGUES.get(str(event_id))
        slugs = [preferred] if preferred else []
        slugs.extend(slug for slug in dict.fromkeys(ESPN_LEAGUE_SLUGS.values()) if slug not in slugs)
        last_error = None
        for slug in slugs:
            try:
                return self._get_json(f"{slug}/summary", {"event": event_id})
            except requests.exceptions.HTTPError as exc:
                if getattr(exc.response, "status_code", None) != 404:
                    raise
                last_error = exc
        if last_error:
            raise last_error
        raise ValueError(f"Não foi possível localizar o evento ESPN {event_id}.")

    def get_match_details(self, fbref_match_id: str) -> Optional[dict]:
        payload = self._get_event_summary(fbref_match_id)
        game_info = payload.get("gameInfo") or {}
        venue = game_info.get("venue") or {}
        officials = game_info.get("officials") or []
        referee = None
        if officials:
            referee = officials[0].get("displayName") or officials[0].get("fullName")
        return {
            "fbref_id": str(fbref_match_id),
            "venue": venue.get("fullName"),
            "attendance": _safe_int(game_info.get("attendance")),
            "referee": referee,
        }


class StatisticsScraper(MatchesScraper):
    """Scraper das estatísticas de uma partida a partir do resumo ESPN."""

    STAT_MAP = {
        "foulsCommitted": "fouls",
        "yellowCards": "yellow_cards",
        "redCards": "red_cards",
        "offsides": "offsides",
        "wonCorners": "corners",
        "saves": "saves",
        "possessionPct": "possession",
        "totalShots": "shots",
        "shotsOnTarget": "shots_on_target",
        "accuratePasses": "passes",
        "passPct": "pass_accuracy",
        "effectiveTackles": "tackles",
        "interceptions": "interceptions",
    }

    def get_match_statistics(self, fbref_match_id: str) -> Optional[dict]:
        payload = self._get_event_summary(fbref_match_id)
        stats: Dict[str, Any] = {"fbref_match_id": str(fbref_match_id)}
        for team_data in (payload.get("boxscore") or {}).get("teams", []):
            prefix = "home" if team_data.get("homeAway") == "home" else "away"
            for item in team_data.get("statistics", []):
                name = self.STAT_MAP.get(item.get("name"))
                if not name:
                    continue
                value = _safe_float(item.get("displayValue"))
                if name == "pass_accuracy" and value is not None and value <= 1:
                    value *= 100
                if name in {
                    "fouls",
                    "yellow_cards",
                    "red_cards",
                    "offsides",
                    "corners",
                    "saves",
                    "shots",
                    "shots_on_target",
                    "passes",
                    "tackles",
                    "interceptions",
                }:
                    value = _safe_int(item.get("displayValue"))
                stats[f"{prefix}_{name}"] = value
        return stats

    def get_team_season_stats(self, fbref_team_id: str, season: Optional[str] = None) -> List[dict]:
        logger.warning("A ESPN não expõe este relatório no endpoint público; retornando lista vazia")
        return []
