import time
import logging
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)


class TeamsScraper:
    """Scraper para dados de times do FBref."""

    BASE_URL = "https://fbref.com"

    # Mapeamento de nomes de liga para IDs/códigos do FBref
    LEAGUE_CODES = {
        "Serie-A": "9",
        "Brasileirao-Serie-A": "9",
        "Serie A": "9",
        "Premier-League": "9",
        "La-Liga": "12",
        "Bundesliga": "20",
        "Serie-A-Italy": "11",
        "Ligue-1": "13",
        "Eredivisie": "23",
        "Primeira-Liga": "32",
        "MLS": "22",
        "Liga-MX": "31",
        "Libertadores": "18",
        "Champions-League": "8",
    }

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.USER_AGENT})

    def _resolve_league_code(self, league: str) -> str:
        """Resolve o código numérico da liga no FBref."""
        # Normaliza o nome da liga para busca
        normalized = league.strip().title()
        for key, code in self.LEAGUE_CODES.items():
            if key.lower() == normalized.lower() or key.lower() in league.lower() or league.lower() in key.lower():
                return code
        # Padrão: Serie A
        logger.warning(f"Liga '{league}' não mapeada, usando código 9 (Serie A)")
        return "9"

    def _get_soup(self, url: str) -> BeautifulSoup:
        """Faz a requisição e retorna o BeautifulSoup da página."""
        response = self.session.get(url, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        time.sleep(settings.REQUEST_DELAY)
        return BeautifulSoup(response.text, "lxml")

    def get_league_teams(self, league: str, season: str) -> List[dict]:
        """
        Obtém os times de uma liga específica.

        Args:
            league: Código da liga (ex: 'Serie-A', 'Premier-League')
            season: Temporada (ex: '2024-2025')

        Returns:
            Lista de dicionários com dados dos times.
        """
        league_code = self._resolve_league_code(league)
        url = f"{self.BASE_URL}/en/comps/{league_code}/{season}/stats/{league}-Stats"
        soup = self._get_soup(url)

        teams = []
        table = soup.find("table", {"id": "stats_squads_standard_for"})
        if not table:
            logger.warning(f"Tabela de times não encontrada para {league} {season}")
            return teams

        tbody = table.find("tbody")
        if not tbody:
            return teams

        for row in tbody.find_all("tr"):
            if row.get("class") and "thead" in row.get("class", []):
                continue

            team_link = row.find("th", {"data-stat": "team"}).find("a")
            if not team_link:
                continue

            team_data = {
                "name": team_link.text.strip(),
                "fbref_id": team_link.get("href", "").split("/")[-2] if team_link.get("href") else None,
                "league": league,
                "season": season,
            }

            # Extrair estatísticas básicas
            stats_cells = row.find_all("td")
            if len(stats_cells) > 0:
                team_data["matches_played"] = self._safe_int(stats_cells[0].text)
                team_data["wins"] = self._safe_int(stats_cells[1].text)
                team_data["draws"] = self._safe_int(stats_cells[2].text)
                team_data["losses"] = self._safe_int(stats_cells[3].text)
                team_data["goals_for"] = self._safe_int(stats_cells[4].text)
                team_data["goals_against"] = self._safe_int(stats_cells[5].text)

            teams.append(team_data)

        logger.info(f"Encontrados {len(teams)} times para {league} {season}")
        return teams

    def get_team_details(self, fbref_id: str) -> Optional[dict]:
        """
        Obtém detalhes de um time específico.

        Args:
            fbref_id: ID do time no FBref

        Returns:
            Dicionário com detalhes do time ou None se não encontrado.
        """
        url = f"{self.BASE_URL}/en/squads/{fbref_id}"
        soup = self._get_soup(url)

        team_info = {"fbref_id": fbref_id}

        # Nome do time
        title = soup.find("h1")
        if title:
            team_info["name"] = title.text.strip()

        # Informações gerais
        info_section = soup.find("div", {"id": "info"})
        if info_section:
            for item in info_section.find_all("p"):
                text = item.text.strip()
                if ":" in text:
                    key, value = text.split(":", 1)
                    key = key.strip().lower().replace(" ", "_")
                    value = value.strip()
                    if key in ["stadium", "founded", "website", "country"]:
                        team_info[key] = value

        return team_info

    def _safe_int(self, value: str) -> Optional[int]:
        """Converte string para int com segurança."""
        try:
            return int(value.replace(",", ""))
        except (ValueError, AttributeError):
            return None