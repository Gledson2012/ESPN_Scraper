import time
import logging
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from app.config import settings

logger = logging.getLogger(__name__)


class StatisticsScraper:
    """Scraper para estatísticas de partidas do FBref."""

    BASE_URL = "https://fbref.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.USER_AGENT})

    def _get_soup(self, url: str) -> BeautifulSoup:
        """Faz a requisição e retorna o BeautifulSoup da página."""
        response = self.session.get(url, timeout=settings.REQUEST_TIMEOUT)
        response.raise_for_status()
        time.sleep(settings.REQUEST_DELAY)
        return BeautifulSoup(response.text, "lxml")

    def get_match_statistics(self, fbref_match_id: str) -> Optional[dict]:
        """
        Obtém as estatísticas de uma partida específica.

        Args:
            fbref_match_id: ID da partida no FBref

        Returns:
            Dicionário com estatísticas da partida ou None se não encontrado.
        """
        url = f"{self.BASE_URL}/en/matches/{fbref_match_id}"
        soup = self._get_soup(url)

        stats = {"fbref_match_id": fbref_match_id}

        # Tabela de estatísticas da partida
        table = soup.find("table", {"id": "stats_match"})
        if not table:
            logger.warning(f"Tabela de estatísticas não encontrada para partida {fbref_match_id}")
            return stats

        tbody = table.find("tbody")
        if not tbody:
            return stats

        rows = tbody.find_all("tr")
        if len(rows) < 2:
            return stats

        # Primeira linha = time da casa, segunda = time visitante
        home_row = rows[0]
        away_row = rows[1]

        # Nomes dos times
        home_team_cell = home_row.find("th", {"data-stat": "team"})
        away_team_cell = away_row.find("th", {"data-stat": "team"})
        if home_team_cell:
            stats["home_team"] = home_team_cell.text.strip()
        if away_team_cell:
            stats["away_team"] = away_team_cell.text.strip()

        # Estatísticas gerais
        stat_mappings = {
            "possession": "possession",
            "shots_on_target": "shots_on_target",
            "shots": "shots",
            "touches": "touches",
            "passes": "passes",
            "tackles": "tackles",
            "clearances": "clearances",
            "corners": "corner_kicks",
            "offsides": "offsides",
            "fouls": "fouls_committed",
            "yellow_cards": "yellow_cards",
            "red_cards": "red_cards",
            "saves": "gk_saves",
            "xg": "xg",
        }

        for stat_key, data_stat in stat_mappings.items():
            home_cell = home_row.find("td", {"data-stat": data_stat})
            away_cell = away_row.find("td", {"data-stat": data_stat})
            if home_cell:
                stats[f"home_{stat_key}"] = self._safe_float(home_cell.text)
            if away_cell:
                stats[f"away_{stat_key}"] = self._safe_float(away_cell.text)

        return stats

    def get_team_season_stats(self, fbref_team_id: str, season: str = "2024-2025") -> List[dict]:
        """
        Obtém estatísticas de um time na temporada.

        Args:
            fbref_team_id: ID do time no FBref
            season: Temporada (ex: '2024-2025')

        Returns:
            Lista de dicionários com estatísticas por partida.
        """
        url = f"{self.BASE_URL}/en/squads/{fbref_team_id}/{season}/matchlogs/all_comps/schedule"
        soup = self._get_soup(url)

        stats_list = []
        table = soup.find("table", {"id": "matchlogs_for"})
        if not table:
            logger.warning(f"Tabela de estatísticas não encontrada para time {fbref_team_id}")
            return stats_list

        tbody = table.find("tbody")
        if not tbody:
            return stats_list

        for row in tbody.find_all("tr"):
            if row.get("class") and "thead" in row.get("class", []):
                continue

            match_stats = {"fbref_team_id": fbref_team_id}

            # Data
            date_cell = row.find("td", {"data-stat": "date"})
            if date_cell:
                match_stats["date"] = date_cell.text.strip()

            # Oponente
            opp_cell = row.find("td", {"data-stat": "opponent"})
            if opp_cell:
                match_stats["opponent"] = opp_cell.text.strip()

            # Resultado
            result_cell = row.find("td", {"data-stat": "result"})
            if result_cell:
                match_stats["result"] = result_cell.text.strip()

            # Gols
            gf_cell = row.find("td", {"data-stat": "goals_for"})
            ga_cell = row.find("td", {"data-stat": "goals_against"})
            if gf_cell:
                match_stats["goals_for"] = self._safe_int(gf_cell.text)
            if ga_cell:
                match_stats["goals_against"] = self._safe_int(ga_cell.text)

            # xG
            xg_cell = row.find("td", {"data-stat": "xg"})
            xga_cell = row.find("td", {"data-stat": "xg_against"})
            if xg_cell:
                match_stats["xg"] = self._safe_float(xg_cell.text)
            if xga_cell:
                match_stats["xg_against"] = self._safe_float(xga_cell.text)

            # Posse
            poss_cell = row.find("td", {"data-stat": "possession"})
            if poss_cell:
                match_stats["possession"] = self._safe_float(poss_cell.text)

            stats_list.append(match_stats)

        logger.info(f"Encontradas {len(stats_list)} estatísticas para time {fbref_team_id}")
        return stats_list

    def _safe_int(self, value: str) -> Optional[int]:
        """Converte string para int com segurança."""
        try:
            return int(value.replace(",", ""))
        except (ValueError, AttributeError):
            return None

    def _safe_float(self, value: str) -> Optional[float]:
        """Converte string para float com segurança."""
        try:
            return float(value.replace(",", "").replace("%", ""))
        except (ValueError, AttributeError):
            return None