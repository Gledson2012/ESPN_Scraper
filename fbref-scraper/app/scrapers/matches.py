import time
import logging
from typing import List, Optional
from datetime import datetime

import requests
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)


class MatchesScraper:
    """Scraper para dados de partidas do FBref."""

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
        normalized = league.strip().title()
        for key, code in self.LEAGUE_CODES.items():
            if key.lower() == normalized.lower() or key.lower() in league.lower() or league.lower() in key.lower():
                return code
        logger.warning(f"Liga '{league}' não mapeada, usando código 9 (Serie A)")
        return "9"

    def _get_soup(self, url: str) -> BeautifulSoup:
        """Faz a requisição e retorna o BeautifulSoup da página."""
        response = self.session.get(url, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        time.sleep(settings.REQUEST_DELAY)
        return BeautifulSoup(response.text, "lxml")

    def get_league_matches(self, league: str, season: str) -> List[dict]:
        """
        Obtém as partidas de uma liga específica.

        Args:
            league: Código da liga (ex: 'Serie-A', 'Premier-League')
            season: Temporada (ex: '2024-2025')

        Returns:
            Lista de dicionários com dados das partidas.
        """
        league_code = self._resolve_league_code(league)
        url = f"{self.BASE_URL}/en/comps/{league_code}/{season}/schedule/{league}-Scores-and-Fixtures"
        soup = self._get_soup(url)

        matches = []
        table = soup.find("table", {"id": "sched_ks"})
        if not table:
            logger.warning(f"Tabela de partidas não encontrada para {league} {season}")
            return matches

        tbody = table.find("tbody")
        if not tbody:
            return matches

        for row in tbody.find_all("tr"):
            if row.get("class") and "thead" in row.get("class", []):
                continue

            match_data = {}

            # Data
            date_cell = row.find("td", {"data-stat": "date"})
            if date_cell and date_cell.find("a"):
                date_text = date_cell.find("a").text.strip()
                try:
                    match_data["match_date"] = datetime.strptime(date_text, "%Y-%m-%d")
                except ValueError:
                    match_data["match_date"] = None

            # Times
            home_cell = row.find("td", {"data-stat": "home_team"})
            away_cell = row.find("td", {"data-stat": "away_team"})
            if home_cell and home_cell.find("a"):
                match_data["home_team"] = home_cell.find("a").text.strip()
                match_data["home_team_fbref_id"] = home_cell.find("a").get("href", "").split("/")[-2]
            if away_cell and away_cell.find("a"):
                match_data["away_team"] = away_cell.find("a").text.strip()
                match_data["away_team_fbref_id"] = away_cell.find("a").get("href", "").split("/")[-2]

            # Placar
            score_cell = row.find("td", {"data-stat": "score"})
            if score_cell and score_cell.find("a"):
                score_text = score_cell.find("a").text.strip()
                if "–" in score_text:
                    home, away = score_text.split("–")
                    match_data["home_score"] = self._safe_int(home)
                    match_data["away_score"] = self._safe_int(away)

            # Link da partida
            match_link = row.find("td", {"data-stat": "match_report"})
            if match_link and match_link.find("a"):
                href = match_link.find("a").get("href", "")
                match_data["fbref_id"] = href.split("/")[-2] if href else None

            # Competição
            comp_cell = row.find("td", {"data-stat": "comp"})
            if comp_cell:
                match_data["competition"] = comp_cell.text.strip()

            match_data["season"] = season
            match_data["league"] = league

            if match_data.get("home_team") and match_data.get("away_team"):
                matches.append(match_data)

        logger.info(f"Encontradas {len(matches)} partidas para {league} {season}")
        return matches

    def get_match_details(self, fbref_match_id: str) -> Optional[dict]:
        """
        Obtém detalhes de uma partida específica.

        Args:
            fbref_match_id: ID da partida no FBref

        Returns:
            Dicionário com detalhes da partida ou None se não encontrado.
        """
        url = f"{self.BASE_URL}/en/matches/{fbref_match_id}"
        soup = self._get_soup(url)

        match_info = {"fbref_id": fbref_match_id}

        # Título da partida
        title = soup.find("h1")
        if title:
            match_info["title"] = title.text.strip()

        # Informações da partida
        info_section = soup.find("div", {"class": "scorebox"})
        if info_section:
            # Times
            teams = info_section.find_all("a")
            if len(teams) >= 2:
                match_info["home_team"] = teams[0].text.strip()
                match_info["away_team"] = teams[1].text.strip()

            # Placar
            score = info_section.find("div", {"class": "score"})
            if score:
                score_text = score.text.strip()
                if "–" in score_text:
                    home, away = score_text.split("–")
                    match_info["home_score"] = self._safe_int(home)
                    match_info["away_score"] = self._safe_int(away)

        # Venue / Attendance / Referee
        extra_info = soup.find("div", {"class": "scorebox_meta"})
        if extra_info:
            for item in extra_info.find_all("div"):
                text = item.text.strip()
                if "Venue" in text:
                    venue_text = text.replace("Venue:", "").strip()
                    match_info["venue"] = venue_text
                elif "Attendance" in text:
                    attendance_text = text.replace("Attendance:", "").strip()
                    match_info["attendance"] = self._safe_int(attendance_text)
                elif "Referee" in text:
                    referee_text = text.replace("Referee:", "").strip()
                    match_info["referee"] = referee_text

        return match_info

    def _safe_int(self, value: str) -> Optional[int]:
        """Converte string para int com segurança."""
        try:
            return int(value.replace(",", ""))
        except (ValueError, AttributeError):
            return None