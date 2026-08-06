import logging
from typing import List, Optional

import requests
from bs4 import BeautifulSoup

from app.config import settings
from app.scrapers.cache import get_soup

logger = logging.getLogger(__name__)


class PlayersScraper:
    """Scraper para dados de jogadores do FBref."""

    BASE_URL = "https://fbref.com"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": settings.USER_AGENT})

    def _get_soup(self, url: str) -> BeautifulSoup:
        """Busca a URL (com cache em disco) e retorna o BeautifulSoup da página."""
        return get_soup(self.session, url)

    def get_team_players(self, fbref_team_id: str, season: str = "2024-2025") -> List[dict]:
        """
        Obtém os jogadores de um time específico.

        Args:
            fbref_team_id: ID do time no FBref
            season: Temporada (ex: '2024-2025')

        Returns:
            Lista de dicionários com dados dos jogadores.
        """
        url = f"{self.BASE_URL}/en/squads/{fbref_team_id}/{season}/all_comps"
        soup = self._get_soup(url)

        players = []
        table = soup.find("table", {"id": "stats_standard_ks"})
        if not table:
            logger.warning(f"Tabela de jogadores não encontrada para time {fbref_team_id}")
            return players

        tbody = table.find("tbody")
        if not tbody:
            return players

        for row in tbody.find_all("tr"):
            if row.get("class") and "thead" in row.get("class", []):
                continue

            player_link = row.find("th", {"data-stat": "player"}).find("a")
            if not player_link:
                continue

            player_data = {
                "name": player_link.text.strip(),
                "fbref_id": player_link.get("href", "").split("/")[-2] if player_link.get("href") else None,
            }

            # Posição
            pos_cell = row.find("td", {"data-stat": "position"})
            if pos_cell:
                player_data["position"] = pos_cell.text.strip()

            # Número da camisa
            num_cell = row.find("td", {"data-stat": "shirtnumber"})
            if num_cell:
                player_data["shirt_number"] = self._safe_int(num_cell.text)

            # Idade
            age_cell = row.find("td", {"data-stat": "age"})
            if age_cell:
                player_data["age"] = age_cell.text.strip()

            # Nacionalidade
            nat_cell = row.find("td", {"data-stat": "nationality"})
            if nat_cell:
                player_data["nationality"] = nat_cell.text.strip()

            players.append(player_data)

        logger.info(f"Encontrados {len(players)} jogadores para time {fbref_team_id}")
        return players

    def get_player_details(self, fbref_player_id: str) -> Optional[dict]:
        """
        Obtém detalhes de um jogador específico.

        Args:
            fbref_player_id: ID do jogador no FBref

        Returns:
            Dicionário com detalhes do jogador ou None se não encontrado.
        """
        url = f"{self.BASE_URL}/en/players/{fbref_player_id}"
        soup = self._get_soup(url)

        player_info = {"fbref_id": fbref_player_id}

        # Nome do jogador
        title = soup.find("h1")
        if title:
            player_info["name"] = title.text.strip()

        # Informações do jogador
        info_section = soup.find("div", {"id": "info"})
        if info_section:
            for item in info_section.find_all("p"):
                text = item.text.strip()
                if ":" in text:
                    key, value = text.split(":", 1)
                    key = key.strip().lower().replace(" ", "_")
                    value = value.strip()
                    if key in ["position", "footed", "height", "weight", "national_team", "born"]:
                        player_info[key] = value

        return player_info

    def _safe_int(self, value: str) -> Optional[int]:
        """Converte string para int com segurança."""
        try:
            return int(value.replace(",", ""))
        except (ValueError, AttributeError):
            return None