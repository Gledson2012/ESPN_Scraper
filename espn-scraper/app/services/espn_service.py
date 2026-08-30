import logging
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Team, Player, Match, MatchStats
from app.scrapers import TeamsScraper, PlayersScraper, MatchesScraper, StatisticsScraper
from app.seasons import resolve_season

logger = logging.getLogger(__name__)

SCRAPED_STAT_FIELDS = (
    "possession",
    "shots",
    "shots_on_target",
    "corners",
    "fouls",
    "yellow_cards",
    "red_cards",
    "offsides",
    "xg",
    "passes",
    "pass_accuracy",
    "tackles",
    "interceptions",
    "saves",
)


class ESPNService:
    """Serviço de sincronização que persiste dados da ESPN no banco."""

    def __init__(self, db: Session):
        self.db = db
        self.teams_scraper = TeamsScraper()
        self.players_scraper = PlayersScraper()
        self.matches_scraper = MatchesScraper()
        self.statistics_scraper = StatisticsScraper()

    # ===== Times =====

    def scrape_and_save_teams(self, league: str, season: Optional[str] = None) -> List[Team]:
        """Busca times de uma liga na ESPN e salva no banco."""
        season = resolve_season(league, season)
        teams_data = self.teams_scraper.get_league_teams(league, season)
        saved_teams = []

        for team_data in teams_data:
            team = self._get_or_create_team(team_data)
            saved_teams.append(team)

        self.db.commit()
        logger.info("Salvos %s times da liga %s %s", len(saved_teams), league, season)
        return saved_teams

    def _get_or_create_team(self, team_data: dict) -> Team:
        """Busca um time pelo identificador e atualiza os dados coletados."""
        espn_id = team_data.get("espn_id")
        team = None

        if espn_id:
            team = self.db.query(Team).filter(Team.espn_id == espn_id).first()
        elif team_data.get("name"):
            team = (
                self.db.query(Team)
                .filter(
                    Team.name == team_data["name"],
                    Team.league == team_data.get("league"),
                )
                .first()
            )

        if not team and team_data.get("name"):
            # Permite atualizar instalações antigas que ainda possuem o ID do
            # uma fonte anterior quando a mesma equipe passa a ser identificada pela ESPN.
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
                espn_id=espn_id,
                league=team_data.get("league"),
                short_name=team_data.get("short_name"),
                country=team_data.get("country"),
                stadium=team_data.get("stadium"),
                founded=team_data.get("founded"),
                website=team_data.get("website"),
                logo_url=team_data.get("logo_url"),
            )
            self.db.add(team)
            self.db.flush()

        else:
            self._update_fields(
                team,
                team_data,
                [
                    "name",
                    "league",
                    "espn_id",
                    "short_name",
                    "country",
                    "stadium",
                    "founded",
                    "website",
                    "logo_url",
                ],
            )

        return team

    # ===== Jogadores =====

    def scrape_and_save_players(self, espn_team_id: str, season: Optional[str] = None) -> List[Player]:
        """Busca jogadores de um time na ESPN e salva no banco."""
        team = self.db.query(Team).filter(Team.espn_id == espn_team_id).first()
        if not team:
            logger.warning("Time com espn_id %s não encontrado no banco", espn_team_id)
            return []

        syncing_current_squad = not (season and season.strip())
        season = resolve_season(team.league, season)
        players_data = self.players_scraper.get_team_players(
            espn_team_id,
            season,
            team.league,
        )
        if not players_data:
            logger.warning(
                "Nenhum jogador coletado para %s (%s); elenco existente foi preservado",
                espn_team_id,
                season,
            )
            return []

        saved_players = []

        for player_data in players_data:
            player = self._get_or_create_player(player_data, team.id)
            saved_players.append(player)

        if syncing_current_squad:
            self._detach_players_not_in_current_squad(team.id, players_data)

        self.db.commit()
        logger.info("Salvos %s jogadores do time %s", len(saved_players), espn_team_id)
        return saved_players

    def _get_or_create_player(self, player_data: dict, team_id: int) -> Player:
        """Busca um jogador pelo identificador e atualiza os dados coletados."""
        espn_id = player_data.get("espn_id")
        player = None

        if espn_id:
            player = self.db.query(Player).filter(Player.espn_id == espn_id).first()
        elif player_data.get("name"):
            player = (
                self.db.query(Player)
                .filter(Player.name == player_data["name"], Player.team_id == team_id)
                .first()
            )

        if not player and player_data.get("name"):
            # Reaproveita jogadores gravados por uma fonte anterior quando o
            # ID externo mudar entre provedores.
            player = (
                self.db.query(Player)
                .filter(
                    Player.name == player_data["name"],
                    Player.team_id == team_id,
                )
                .first()
            )

        if not player:
            player = Player(
                name=player_data.get("name"),
                espn_id=espn_id,
                team_id=team_id,
                position=player_data.get("position"),
                shirt_number=player_data.get("shirt_number"),
                nationality=player_data.get("nationality"),
                full_name=player_data.get("full_name"),
                birth_date=player_data.get("birth_date"),
                height_cm=player_data.get("height_cm"),
                weight_kg=player_data.get("weight_kg"),
                foot=player_data.get("foot"),
                photo_url=player_data.get("photo_url"),
            )
            self.db.add(player)
            self.db.flush()
        else:
            self._update_fields(
                player,
                player_data,
                [
                    "name",
                    "espn_id",
                    "position",
                    "shirt_number",
                    "nationality",
                    "full_name",
                    "birth_date",
                    "height_cm",
                    "weight_kg",
                    "foot",
                    "photo_url",
                ],
            )
            # Um jogador pode mudar de clube entre duas coletas.
            player.team_id = team_id

        if espn_id and any(
            getattr(player, field) is None
            for field in ["full_name", "birth_date", "height_cm", "weight_kg"]
        ):
            self._enrich_player(player, espn_id)

        return player

    # ===== Partidas =====

    def scrape_and_save_matches(self, league: str, season: Optional[str] = None) -> List[Match]:
        """Busca partidas de uma liga na ESPN e salva no banco."""
        season = resolve_season(league, season)
        matches_data = self.matches_scraper.get_league_matches(league, season)
        saved_matches = []

        for match_data in matches_data:
            match = self._get_or_create_match(match_data)
            if match:
                saved_matches.append(match)

        self.db.commit()
        logger.info("Salvas %s partidas da liga %s %s", len(saved_matches), league, season)
        return saved_matches

    def _detach_players_not_in_current_squad(
        self,
        team_id: int,
        players_data: List[dict],
    ) -> None:
        """Remove do elenco atual jogadores que não vieram na nova coleta.

        O registro é mantido no banco para preservar o histórico, mas fica
        sem `team_id` e deixa de aparecer em `/teams/{id}/players`. A
        reconciliação só é feita quando todos os jogadores coletados têm ID do
        ESPN, evitando falsos desligamentos em resposta incompleta.
        """
        current_ids = {
            player_data["espn_id"]
            for player_data in players_data
            if player_data.get("espn_id")
        }
        if len(current_ids) != len(players_data):
            logger.warning(
                "Coleta de elenco sem IDs completos para o time %s; reconciliação ignorada",
                team_id,
            )
            return

        for player in self.db.query(Player).filter(Player.team_id == team_id).all():
            if player.espn_id not in current_ids:
                player.team_id = None

    def _get_or_create_match(self, match_data: dict) -> Optional[Match]:
        """Busca uma partida pelo ID externo ou cria uma nova."""
        espn_id = match_data.get("espn_id")
        if not espn_id:
            return None

        match = self.db.query(Match).filter(Match.espn_id == espn_id).first()

        # Buscar times
        home_team = self.db.query(Team).filter(
            Team.espn_id == match_data.get("home_team_espn_id")
        ).first()
        away_team = self.db.query(Team).filter(
            Team.espn_id == match_data.get("away_team_espn_id")
        ).first()

        if match:
            # Atualiza o que veio da coleta, mas preserva valores já conhecidos
            # quando a ESPN retornar uma célula vazia.
            if home_team and away_team and home_team.id != away_team.id:
                match.home_team_id = home_team.id
                match.away_team_id = away_team.id
            self._update_fields(
                match,
                match_data,
                [
                    "competition",
                    "season",
                    "match_date",
                    "venue",
                    "attendance",
                    "referee",
                    "home_score",
                    "away_score",
                ],
            )
            return match

        if not home_team or not away_team or home_team.id == away_team.id:
            logger.warning("Times não encontrados para partida %s", espn_id)
            return None

        match = Match(
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            competition=match_data.get("competition"),
            season=match_data.get("season"),
            match_date=match_data.get("match_date"),
            venue=match_data.get("venue"),
            attendance=match_data.get("attendance"),
            referee=match_data.get("referee"),
            home_score=match_data.get("home_score"),
            away_score=match_data.get("away_score"),
            espn_id=espn_id,
        )
        self.db.add(match)
        self.db.flush()

        if not match_data.get("venue") or match_data.get("attendance") is None:
            self._enrich_match(match, espn_id)

        return match

    # ===== Estatísticas =====

    def scrape_and_save_match_statistics(self, espn_match_id: str) -> Optional[MatchStats]:
        """Busca estatísticas de uma partida na ESPN e salva no banco."""
        match = self.db.query(Match).filter(Match.espn_id == espn_match_id).first()
        if not match:
            logger.warning("Partida com espn_id %s não encontrada no banco", espn_match_id)
            return None

        stats_data = self.statistics_scraper.get_match_statistics(espn_match_id) or {}

        # Exige pelo menos uma métrica para cada lado. Uma resposta parcial de
        # bloqueio/alteração de HTML não deve apagar dados válidos já coletados.
        has_home_stats = any(
            stats_data.get(f"home_{field}") is not None
            for field in SCRAPED_STAT_FIELDS
        )
        has_away_stats = any(
            stats_data.get(f"away_{field}") is not None
            for field in SCRAPED_STAT_FIELDS
        )
        if not has_home_stats or not has_away_stats:
            logger.warning(
                "Estatísticas incompletas para a partida %s; mantendo dados existentes",
                espn_match_id,
            )
            return None

        # Atualiza somente valores presentes e preserva campos já preenchidos
        # quando o novo HTML não os trouxer. Se não existir, cria o registro.
        home_stats = self._upsert_match_stats(
            match,
            stats_data,
            prefix="home",
            opposing_prefix="away",
            team_id=match.home_team_id,
            is_home=True,
        )
        self._upsert_match_stats(
            match,
            stats_data,
            prefix="away",
            opposing_prefix="home",
            team_id=match.away_team_id,
            is_home=False,
        )

        self.db.commit()
        logger.info("Estatísticas salvas para partida %s", espn_match_id)
        return home_stats

    def _upsert_match_stats(
        self,
        match: Match,
        stats_data: dict,
        prefix: str,
        opposing_prefix: str,
        team_id: int,
        is_home: bool,
    ) -> MatchStats:
        """Atualiza ou cria estatísticas sem apagar valores ausentes no scrape."""
        values = {
            "possession": stats_data.get(f"{prefix}_possession"),
            "shots": stats_data.get(f"{prefix}_shots"),
            "shots_on_target": stats_data.get(f"{prefix}_shots_on_target"),
            "corners": stats_data.get(f"{prefix}_corners"),
            "fouls": stats_data.get(f"{prefix}_fouls"),
            "yellow_cards": stats_data.get(f"{prefix}_yellow_cards"),
            "red_cards": stats_data.get(f"{prefix}_red_cards"),
            "offsides": stats_data.get(f"{prefix}_offsides"),
            "xg": stats_data.get(f"{prefix}_xg"),
            "xg_against": stats_data.get(f"{opposing_prefix}_xg"),
            "passes": stats_data.get(f"{prefix}_passes"),
            "pass_accuracy": stats_data.get(f"{prefix}_pass_accuracy"),
            "tackles": stats_data.get(f"{prefix}_tackles"),
            "interceptions": stats_data.get(f"{prefix}_interceptions"),
            "saves": stats_data.get(f"{prefix}_saves"),
        }
        stat = self.db.query(MatchStats).filter(
            MatchStats.match_id == match.id,
            MatchStats.team_id == team_id,
        ).first()
        if not stat:
            stat = MatchStats(
                match_id=match.id,
                team_id=team_id,
                is_home=is_home,
                **values,
            )
            self.db.add(stat)
        else:
            stat.is_home = is_home
            self._update_fields(stat, values, list(values))
        return stat

    @staticmethod
    def _update_fields(model, data: dict, fields: List[str]) -> None:
        """Atualiza somente campos presentes e não nulos na coleta."""
        for field in fields:
            value = data.get(field)
            if value is not None:
                setattr(model, field, value)

    def _enrich_team(self, team: Team, espn_id: str) -> None:
        """Preenche detalhes opcionais do time sem invalidar a coleta principal."""
        try:
            details = self.teams_scraper.get_team_details(espn_id)
            if not details:
                return
            self._update_fields(team, details, ["short_name", "country", "stadium", "website"])
            founded = details.get("founded")
            if founded is not None:
                try:
                    team.founded = int(str(founded).replace(",", "").strip())
                except (TypeError, ValueError):
                    logger.debug("Ano de fundação inválido para o time %s: %s", espn_id, founded)
        except Exception as e:  # noqa: BLE001
            logger.warning("Erro ao buscar detalhes do time %s: %s", espn_id, e)

    def _enrich_player(self, player: Player, espn_id: str) -> None:
        """Preenche detalhes opcionais do jogador com parsing tolerante."""
        try:
            details = self.players_scraper.get_player_details(espn_id)
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
                    logger.debug("Altura inválida para o jogador %s: %s", espn_id, height_text)

            weight_text = details.get("weight")
            if weight_text:
                try:
                    player.weight_kg = float(
                        str(weight_text).lower().replace("kg", "").replace(",", ".").strip()
                    )
                except (ValueError, TypeError):
                    logger.debug("Peso inválido para o jogador %s: %s", espn_id, weight_text)
        except Exception as e:  # noqa: BLE001
            logger.warning("Erro ao buscar detalhes do jogador %s: %s", espn_id, e)

    def _enrich_match(self, match: Match, espn_id: str) -> None:
        """Preenche detalhes opcionais da partida sem ocultar falhas de rede."""
        try:
            details = self.matches_scraper.get_match_details(espn_id)
            if details:
                self._update_fields(match, details, ["venue", "attendance", "referee"])
                self._update_fields(match, details, ["home_score", "away_score"])
        except Exception as e:  # noqa: BLE001
            logger.warning("Erro ao buscar detalhes da partida %s: %s", espn_id, e)
