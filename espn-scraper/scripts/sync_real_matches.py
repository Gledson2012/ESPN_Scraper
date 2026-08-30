"""Sincroniza times, partidas e elencos reais da ESPN para o banco.

Uso:
    python scripts/sync_real_matches.py --league Serie-A
    python scripts/sync_real_matches.py --league La-Liga --include-players
"""

import argparse
import logging
import sys
from pathlib import Path

import requests

# Permite executar o arquivo diretamente a partir da pasta da API.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.database import SessionLocal
from app.seasons import resolve_season
from app.services.espn_service import ESPNService


def main() -> None:
    parser = argparse.ArgumentParser(description="Sincroniza dados reais da ESPN")
    parser.add_argument("--league", default="Serie-A", help="Código da liga, por exemplo Serie-A")
    parser.add_argument(
        "--season",
        default=None,
        help="Temporada da ESPN; se omitida, usa a temporada atual da liga",
    )
    parser.add_argument(
        "--include-players",
        action="store_true",
        help="Sincroniza também o elenco atual de cada time encontrado",
    )
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    db = SessionLocal()
    try:
        season = resolve_season(args.league, args.season)
        service = ESPNService(db)
        teams = service.scrape_and_save_teams(args.league, season)
        matches = service.scrape_and_save_matches(args.league, season)
        player_count = 0
        if args.include_players:
            for team in teams:
                if team.espn_id:
                    # Mantém None quando a temporada não foi informada para
                    # que o serviço também reconcilie o elenco atual.
                    player_count += len(service.scrape_and_save_players(team.espn_id, args.season))
        print(
            f"Sincronização concluída ({args.league} {season}): "
            f"{len(teams)} times, {len(matches)} partidas e {player_count} jogadores."
        )
    finally:
        db.close()


if __name__ == "__main__":
    try:
        main()
    except requests.exceptions.RequestException as exc:
        status_code = getattr(exc.response, "status_code", None)
        if status_code == 403:
            print(
                "A ESPN recusou a coleta (HTTP 403). Nenhum dado foi alterado "
                "nesta execução; tente novamente mais tarde ou use uma fonte/API "
                "autorizada conforme os termos do serviço.",
                file=sys.stderr,
            )
        else:
            print(f"Falha ao consultar a ESPN: {exc}", file=sys.stderr)
        raise SystemExit(2) from None
