"""Compatibilidade para códigos antigos de ligas do FBref.

Os scrapers ativos usam os códigos da ESPN definidos em app.scrapers.espn.
"""

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


# O nome usado pela API nem sempre é o mesmo slug usado no caminho do FBref.
# Em especial, a Série A italiana e as três aliases do Brasileirão usam
# `Serie-A` no slug da página.
LEAGUE_SLUGS = {
    "Serie-A": "Serie-A",
    "Brasileirao-Serie-A": "Serie-A",
    "Serie A": "Serie-A",
    "Premier-League": "Premier-League",
    "Serie-A-Italy": "Serie-A",
    "La-Liga": "La-Liga",
    "Bundesliga": "Bundesliga",
    "Ligue-1": "Ligue-1",
    "Eredivisie": "Eredivisie",
    "Primeira-Liga": "Primeira-Liga",
    "MLS": "MLS",
    "Liga-MX": "Liga-MX",
    "Libertadores": "Libertadores",
    "Champions-League": "Champions-League",
}


def resolve_league_code(league: str) -> str:
    """Resolve o código numérico da liga no FBref.

    A prioridade é:
    1. Match exato (case-insensitive)
    2. Caso não exista correspondência, rejeita a liga em vez de retornar
       dados de outra competição silenciosamente.
    """
    normalized = league.strip().lower()

    for key, code in LEAGUE_CODES.items():
        if key.lower() == normalized:
            return code

    raise ValueError(
        f"Liga não suportada: '{league}'. Use um dos códigos documentados."
    )


def resolve_league_slug(league: str) -> str:
    """Resolve o slug textual utilizado nos URLs do FBref."""
    normalized = league.strip().lower()

    for key, slug in LEAGUE_SLUGS.items():
        if key.lower() == normalized:
            return slug

    raise ValueError(
        f"Liga não suportada: '{league}'. Use um dos códigos documentados."
    )
