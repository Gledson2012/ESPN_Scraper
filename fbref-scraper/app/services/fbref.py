import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Team, Player, Match, MatchStats
from app.scrapers import TeamsScraper, PlayersScraper, MatchesScraper, StatisticsScraper

logger = logging.getLogger(__name__)


class FBrefService:
    """Serviço que orquestra os scrapers e persiste os dados no banco."""

    def __init__(self, db: Session):
        self.db = db
        self.teams_scraper = TeamsScraper()
        self.players_scraper = PlayersScraper()
        self.matches_scraper = MatchesScraper()
        self.statistics_scraper = StatisticsScraper()

    # ===== Times =====

    def scrape_and_save_teams(self, league: str, season: str) -> List[Team]:
        """Busca times de uma liga no FBref e salva no banco."""
        teams_data = self.teams_scraper.get_league_teams(league, season)
        saved_teams = []

        for team_data in teams_data:
            team = self._get_or_create_team(team_data)
            saved_teams.append(team)

        self.db.commit()
        logger.info(f"Salvos {len(saved_teams)} times da liga {league} {season}")
        return saved_teams

    def _get_or_create_team(self, team_data: dict) -> Team:
        """Busca um time pelo identificador e atualiza os dados coletados."""
        fbref_id = team_data.get("fbref_id")
        team = None

        if fbref_id:
            team = self.db.query(Team).filter(Team.fbref_id == fbref_id).first()
        elif team_data.get("name"):
            team = (
                self.db.query(Team)
                .filter(
                    Team.name == team_data["name"],
                    Team.league == team_data.get("league"),
                )
                .first()
            )

        if not team:
            team = Team(
                name=team_data.get("name"),
                fbref_id=fbref_id,
                league=team_data.get("league"),
            )
            self.db.add(team)
            self.db.flush()

        else:
            self._update_fields(team, team_data, ["name", "league"])

        # O endpoint de elenco contém os dados atuais; detalhes extras só são
        # buscados quando ainda faltam no registro, evitando chamadas repetidas.
        if fbref_id and any(
            getattr(team, field) is None
            for field in ["short_name", "country", "stadium", "founded", "website"]
        ):
            self._enrich_team(team, fbref_id)

        return team

    # ===== Jogadores =====

    def scrape_and_save_players(self, fbref_team_id: str, season: str = "2024-2025") -> List[Player]:
        """Busca jogadores de um time no FBref e salva no banco."""
        team = self.db.query(Team).filter(Team.fbref_id == fbref_team_id).first()
        if not team:
            logger.warning(f"Time com fbref_id {fbref_team_id} não encontrado no banco")
            return []

        players_data = self.players_scraper.get_team_players(fbref_team_id, season)
        saved_players = []

        for player_data in players_data:
            player = self._get_or_create_player(player_data, team.id)
            saved_players.append(player)

        self.db.commit()
        logger.info(f"Salvos {len(saved_players)} jogadores do time {fbref_team_id}")
        return saved_players

    def _get_or_create_player(self, player_data: dict, team_id: int) -> Player:
        """Busca um jogador pelo identificador e atualiza os dados coletados."""
        fbref_id = player_data.get("fbref_id")
        player = None

        if fbref_id:
            player = self.db.query(Player).filter(Player.fbref_id == fbref_id).first()
        elif player_data.get("name"):
            player = (
                self.db.query(Player)
                .filter(Player.name == player_data["name"], Player.team_id == team_id)
                .first()
            )

        if not player:
            player = Player(
                name=player_data.get("name"),
                fbref_id=fbref_id,
                team_id=team_id,
                position=player_data.get("position"),
                shirt_number=player_data.get("shirt_number"),
                nationality=player_data.get("nationality"),
            )
            self.db.add(player)
            self.db.flush()
        else:
            self._update_fields(
                player,
                player_data,
                ["name", "position", "shirt_number", "nationality"],
            )
            # Um jogador pode mudar de clube entre duas coletas.
            player.team_id = team_id

        if fbref_id and any(
            getattr(player, field) is None
            for field in ["full_name", "birth_date", "height_cm", "weight_kg", "foot"]
        ):
            self._enrich_player(player, fbref_id)

        return player

    # ===== Partidas =====

    def scrape_and_save_matches(self, league: str, season: str) -> List[Match]:
        """Busca partidas de uma liga no FBref e salva no banco."""
        matches_data = self.matches_scraper.get_league_matches(league, season)
        saved_matches = []

        for match_data in matches_data:
            match = self._get_or_create_match(match_data)
            if match:
                saved_matches.append(match)

        self.db.commit()
        logger.info(f"Salvas {len(saved_matches)} partidas da liga {league} {season}")
        return saved_matches

    def _get_or_create_match(self, match_data: dict) -> Optional[Match]:
        """Busca uma partida pelo fbref_id ou cria uma nova."""
        fbref_id = match_data.get("fbref_id")
        if not fbref_id:
            return None

        match = self.db.query(Match).filter(Match.fbref_id == fbref_id).first()

        # Buscar times
        home_team = self.db.query(Team).filter(
            Team.fbref_id == match_data.get("home_team_fbref_id")
        ).first()
        away_team = self.db.query(Team).filter(
            Team.fbref_id == match_data.get("away_team_fbref_id")
        ).first()

        if match:
            # Atualiza o que veio da coleta, mas preserva valores já conhecidos
            # quando o FBref retornar uma célula vazia.
            if home_team and away_team and home_team.id != away_team.id:
                match.home_team_id = home_team.id
                match.away_team_id = away_team.id
            self._update_fields(
                match,
                match_data,
                ["competition", "season", "match_date", "home_score", "away_score"],
            )
            return match

        if not home_team or not away_team or home_team.id == away_team.id:
            logger.warning(f"Times não encontrados para partida {fbref_id}")
            return None

        match = Match(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            competition=match_data.get("competition"),
            season=match_data.get("season"),
            match_date=match_data.get("match_date"),
            home_score=match_data.get("home_score"),
            away_score=match_data.get("away_score"),
            fbref_id=fbref_id,
        )
        self.db.add(match)
        self.db.flush()

        self._enrich_match(match, fbref_id)

        return match

    # ===== Estatísticas =====

    def scrape_and_save_match_statistics(self, fbref_match_id: str) -> Optional[MatchStats]:
        """Busca estatísticas de uma partida no FBref e salva no banco."""
        match = self.db.query(Match).filter(Match.fbref_id == fbref_match_id).first()
        if not match:
            logger.warning(f"Partida com fbref_id {fbref_match_id} não encontrada no banco")
            return None

        stats_data = self.statistics_scraper.get_match_statistics(fbref_match_id) or {}

        # Não apagar dados existentes quando a coleta não retorna estatísticas reais
        stat_keys = [
            key
            for key in stats_data
            if key.startswith(("home_", "away_"))
            and key not in ("home_team", "away_team")
        ]
        has_stats = any(stats_data.get(key) is not None for key in stat_keys)
        if not has_stats:
            logger.warning(f"Nenhuma estatística coletada para a partida {fbref_match_id}; mantendo dados existentes")
            return None

        # Evitar duplicação: re-scraping substitui as estatísticas existentes da partida
        self.db.query(MatchStats).filter(MatchStats.match_id == match.id).delete(synchronize_session=False)

        # Salvar estatísticas do time da casa (xg_against = xG do visitante)
        home_stats = MatchStats(
            match_id=match.id,
            team_id=match.home_team_id,
            is_home=True,
            possession=stats_data.get("home_possession"),
            shots=stats_data.get("home_shots"),
            shots_on_target=stats_data.get("home_shots_on_target"),
            corners=stats_data.get("home_corners"),
            fouls=stats_data.get("home_fouls"),
            yellow_cards=stats_data.get("home_yellow_cards"),
            red_cards=stats_data.get("home_red_cards"),
            offsides=stats_data.get("home_offsides"),
            xg=stats_data.get("home_xg"),
            xg_against=stats_data.get("away_xg"),
            passes=stats_data.get("home_passes"),
            tackles=stats_data.get("home_tackles"),
            saves=stats_data.get("home_saves"),
        )
        self.db.add(home_stats)

        # Salvar estatísticas do time visitante (xg_against = xG do time da casa)
        away_stats = MatchStats(
            match_id=match.id,
            team_id=match.away_team_id,
            is_home=False,
            possession=stats_data.get("away_possession"),
            shots=stats_data.get("away_shots"),
            shots_on_target=stats_data.get("away_shots_on_target"),
            corners=stats_data.get("away_corners"),
            fouls=stats_data.get("away_fouls"),
            yellow_cards=stats_data.get("away_yellow_cards"),
            red_cards=stats_data.get("away_red_cards"),
            offsides=stats_data.get("away_offsides"),
            xg=stats_data.get("away_xg"),
            xg_against=stats_data.get("home_xg"),
            passes=stats_data.get("away_passes"),
            tackles=stats_data.get("away_tackles"),
            saves=stats_data.get("away_saves"),
        )
        self.db.add(away_stats)

        self.db.commit()
        logger.info(f"Estatísticas salvas para partida {fbref_match_id}")
        return home_stats

    @staticmethod
    def _update_fields(model, data: dict, fields: List[str]) -> None:
        """Atualiza somente campos presentes e não nulos na coleta."""
        for field in fields:
            value = data.get(field)
            if value is not None:
                setattr(model, field, value)

    def _enrich_team(self, team: Team, fbref_id: str) -> None:
        """Preenche detalhes opcionais do time sem invalidar a coleta principal."""
        try:
            details = self.teams_scraper.get_team_details(fbref_id)
            if not details:
                return
            self._update_fields(team, details, ["short_name", "country", "stadium", "website"])
            founded = details.get("founded")
            if founded is not None:
                try:
                    team.founded = int(str(founded).replace(",", "").strip())
                except (TypeError, ValueError):
                    logger.debug("Ano de fundação inválido para o time %s: %s", fbref_id, founded)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Erro ao buscar detalhes do time {fbref_id}: {e}")

    def _enrich_player(self, player: Player, fbref_id: str) -> None:
        """Preenche detalhes opcionais do jogador com parsing tolerante."""
        try:
            details = self.players_scraper.get_player_details(fbref_id)
            if not details:
                return
            self._update_fields(player, details, ["full_name"])
            if details.get("footed") is not None:
                player.foot = details["footed"]

            birth_text = details.get("born")
            if birth_text:
                for date_format in ("%B %d, %Y", "%b %d, %Y", "%Y-%m-%d"):
                    try:
                        player.birth_date = datetime.strptime(birth_text.strip(), date_format)
                        break
                    except (ValueError, TypeError):
                        continue

            height_text = details.get("height")
            if height_text:
                try:
                    height_clean = str(height_text).lower().replace(",", ".").strip()
                    if "cm" in height_clean:
                        player.height_cm = float(height_clean.replace("cm", "").strip())
                    elif "m" in height_clean:
                        player.height_cm = float(height_clean.replace("m", "").strip()) * 100
                    else:
                        height_value = float(height_clean)
                        player.height_cm = height_value * 100 if height_value < 3 else height_value
                except (ValueError, TypeError):
                    logger.debug("Altura inválida para o jogador %s: %s", fbref_id, height_text)

            weight_text = details.get("weight")
            if weight_text:
                try:
                    player.weight_kg = float(
                        str(weight_text).lower().replace("kg", "").replace(",", ".").strip()
                    )
                except (ValueError, TypeError):
                    logger.debug("Peso inválido para o jogador %s: %s", fbref_id, weight_text)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Erro ao buscar detalhes do jogador {fbref_id}: {e}")

    def _enrich_match(self, match: Match, fbref_id: str) -> None:
        """Preenche detalhes opcionais da partida sem ocultar falhas de rede."""
        try:
            details = self.matches_scraper.get_match_details(fbref_id)
            if details:
                self._update_fields(match, details, ["venue", "attendance", "referee"])
                self._update_fields(match, details, ["home_score", "away_score"])
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Erro ao buscar detalhes da partida {fbref_id}: {e}")
