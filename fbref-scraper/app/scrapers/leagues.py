"""Mapeamento de ligas para os códigos numéricos do FBref (https://fbref.com/en/comps/)."""

import logging

logger = logging.getLogger(__name__)

LEAGUE_CODES = {
    "Serie-A": "24",  # Brasileirão Série A
    "Brasileirao-Serie-A": "24",
    "Serie A": "24",
    "Premier-League": "9",
    "Serie-A-Italy": "11",  # Serie A (Itália)
    "La-Liga": "12",
    "Bundesliga": "20",
    "Ligue-1": "13",
    "Eredivisie": "23",
    "Primeira-Liga": "32",
    "MLS": "22",
    "Liga-MX": "31",
    "Libertadores": "18",
    "Champions-League": "8",
}

# Código padrão usado quando a liga não é reconhecida (Série A do Brasil)
DEFAULT_LEAGUE_CODE = "24"


def resolve_league_code(league: str) -> str:
    """Resolve o código numérico da liga no FBref.

    A prioridade é:
    1. Match exato (case-insensitive)
    2. Match por conteúdo — testando as chaves mais longas primeiro para
       evitar que "Serie-A" capture "Serie-A-Italy" indevidamente
    3. Fallback para a Série A do Brasil
    """
    normalized = league.strip().lower()

    for key, code in LEAGUE_CODES.items():
        if key.lower() == normalized:
            return code

    for key, code in sorted(LEAGUE_CODES.items(), key=lambda kv: len(kv[0]), reverse=True):
        if key.lower() in normalized or normalized in key.lower():
            return code

    logger.warning(f"Liga '{league}' não mapeada, usando código {DEFAULT_LEAGUE_CODE} (Série A Brasil)")
    return DEFAULT_LEAGUE_CODE
