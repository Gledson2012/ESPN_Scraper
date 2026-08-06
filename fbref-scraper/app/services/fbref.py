import logging
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
        """Busca um time pelo fbref_id ou cria um novo."""
        fbref_id = team_data.get("fbref_id")
        team = None

        if fbref_id:
            team = self.db.query(Team).filter(Team.fbref_id == fbref_id).first()

        if not team:
            team = Team(
                name=team_data.get("name"),
                fbref_id=fbref_id,
                league=team_data.get("league"),
            )
            self.db.add(team)
            self.db.flush()

            # Tentar enriquecer com detalhes do time
            try:
                details = self.teams_scraper.get_team_details(fbref_id)
                if details:
                    for field in ["short_name", "country", "stadium", "founded", "website"]:
                        if details.get(field):
                            setattr(team, field, details[field])
            except Exception as e:
                logger.warning(f"Erro ao buscar detalhes do time {fbref_id}: {e}")

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
        """Busca um jogador pelo fbref_id ou cria um novo."""
        fbref_id = player_data.get("fbref_id")
        player = None

        if fbref_id:
            player = self.db.query(Player).filter(Player.fbref_id == fbref_id).first()

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

            # Tentar enriquecer com detalhes do jogador
            try:
                details = self.players_scraper.get_player_details(fbref_id)
                if details:
                    if details.get("full_name"):
                        player.full_name = details["full_name"]
                    if details.get("born"):
                        birth_text = details["born"]
                        try:
                            from datetime import datetime
                            player.birth_date = datetime.strptime(birth_text, "%B %d, %Y")
                        except (ValueError, TypeError):
                            pass
                    if details.get("height"):
                        height_text = details["height"]
                        try:
                            # Ex: "1,85m" ou "185cm"
                            height_clean = height_text.replace("m", "").replace("cm", "").replace(",", ".").strip()
                            if "." in height_clean and float(height_clean) < 3:
                                player.height_cm = float(height_clean) * 100
                            else:
                                player.height_cm = float(height_clean)
                        except (ValueError, TypeError):
                            pass
                    if details.get("weight"):
                        weight_text = details["weight"]
                        try:
                            player.weight_kg = float(weight_text.replace("kg", "").replace(",", ".").strip())
                        except (ValueError, TypeError):
                            pass
            except Exception as e:
                logger.warning(f"Erro ao buscar detalhes do jogador {fbref_id}: {e}")

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
        if match:
            return match

        # Buscar times
        home_team = self.db.query(Team).filter(
            Team.fbref_id == match_data.get("home_team_fbref_id")
        ).first()
        away_team = self.db.query(Team).filter(
            Team.fbref_id == match_data.get("away_team_fbref_id")
        ).first()

        if not home_team or not away_team:
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

        # Tentar enriquecer com detalhes da partida
        try:
            details = self.matches_scraper.get_match_details(fbref_id)
            if details:
                if details.get("venue"):
                    match.venue = details["venue"]
                if details.get("attendance"):
                    match.attendance = details["attendance"]
                if details.get("referee"):
                    match.referee = details["referee"]
        except Exception as e:
            logger.warning(f"Erro ao buscar detalhes da partida {fbref_id}: {e}")

        return match

    # ===== Estatísticas =====

    def scrape_and_save_match_statistics(self, fbref_match_id: str) -> Optional[MatchStats]:
        """Busca estatísticas de uma partida no FBref e salva no banco."""
        match = self.db.query(Match).filter(Match.fbref_id == fbref_match_id).first()
        if not match:
            logger.warning(f"Partida com fbref_id {fbref_match_id} não encontrada no banco")
            return None

        stats_data = self.statistics_scraper.get_match_statistics(fbref_match_id)

        # Não apagar dados existentes quando a coleta não retorna estatísticas reais
        has_stats = any(
            key.startswith(("home_", "away_")) and key not in ("home_team", "away_team")
            for key in stats_data
        )
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