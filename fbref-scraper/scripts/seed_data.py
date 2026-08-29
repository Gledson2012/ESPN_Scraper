#!/usr/bin/env python3
"""Popula o banco de dados com dados fictícios para teste do frontend."""

import httpx
import random
import sys

BASE_URL = "http://localhost:8000/api/v1"
HEADERS = {"X-API-Key": "local-dev-api-key"}

client = httpx.Client(base_url=BASE_URL, headers=HEADERS, timeout=30)


def create_team(data: dict) -> dict:
    resp = client.post("/teams/", json=data)
    resp.raise_for_status()
    return resp.json()


def create_player(data: dict) -> dict:
    resp = client.post("/players/", json=data)
    resp.raise_for_status()
    return resp.json()


def create_match(data: dict) -> dict:
    resp = client.post("/matches/", json=data)
    resp.raise_for_status()
    return resp.json()


def create_stats(data: dict) -> dict:
    resp = client.post("/stats/", json=data)
    resp.raise_for_status()
    return resp.json()


# ============================================================
# TIMES - SÉRIE A BRASILEIRA
# ============================================================
serie_a_teams = [
    {"name": "Flamengo", "short_name": "FLA", "country": "Brasil", "league": "Serie-A", "stadium": "Maracanã", "founded": 1895, "fbref_id": "flamengo"},
    {"name": "Palmeiras", "short_name": "PAL", "country": "Brasil", "league": "Serie-A", "stadium": "Allianz Parque", "founded": 1914, "fbref_id": "palmeiras"},
    {"name": "Botafogo", "short_name": "BOT", "country": "Brasil", "league": "Serie-A", "stadium": "Nilton Santos", "founded": 1904, "fbref_id": "botafogo"},
    {"name": "São Paulo", "short_name": "SPF", "country": "Brasil", "league": "Serie-A", "stadium": "Morumbi", "founded": 1930, "fbref_id": "sao-paulo"},
    {"name": "Corinthians", "short_name": "COR", "country": "Brasil", "league": "Serie-A", "stadium": "Neo Química Arena", "founded": 1910, "fbref_id": "corinthians"},
    {"name": "Internacional", "short_name": "INT", "country": "Brasil", "league": "Serie-A", "stadium": "Beira-Rio", "founded": 1909, "fbref_id": "internacional"},
    {"name": "Grêmio", "short_name": "GRE", "country": "Brasil", "league": "Serie-A", "stadium": "Arena do Grêmio", "founded": 1903, "fbref_id": "gremio"},
    {"name": "Atlético-MG", "short_name": "CAM", "country": "Brasil", "league": "Serie-A", "stadium": "Arena Independência", "founded": 1908, "fbref_id": "atletico-mg"},
    {"name": "Cruzeiro", "short_name": "CRU", "country": "Brasil", "league": "Serie-A", "stadium": "Mineirão", "founded": 1921, "fbref_id": "cruzeiro"},
    {"name": "Fluminense", "short_name": "FLU", "country": "Brasil", "league": "Serie-A", "stadium": "Maracanã", "founded": 1902, "fbref_id": "fluminense"},
    {"name": "Santos", "short_name": "SAN", "country": "Brasil", "league": "Serie-A", "stadium": "Vila Belmiro", "founded": 1912, "fbref_id": "santos"},
    {"name": "Vasco da Gama", "short_name": "VAS", "country": "Brasil", "league": "Serie-A", "stadium": "São Januário", "founded": 1898, "fbref_id": "vasco-da-gama"},
    {"name": "Bahia", "short_name": "BAH", "country": "Brasil", "league": "Serie-A", "stadium": "Arena Fonte Nova", "founded": 1931, "fbref_id": "bahia"},
    {"name": "Athletico-PR", "short_name": "CAP", "country": "Brasil", "league": "Serie-A", "stadium": "Arena da Baixada", "founded": 1924, "fbref_id": "athletico-pr"},
    {"name": "Fortaleza", "short_name": "FOR", "country": "Brasil", "league": "Serie-A", "stadium": "Castelão", "founded": 1913, "fbref_id": "fortaleza"},
    {"name": "Cuiabá", "short_name": "CUI", "country": "Brasil", "league": "Serie-A", "stadium": "Arena Pantanal", "founded": 2001, "fbref_id": "cuiaba"},
    {"name": "Juventude", "short_name": "JUV", "country": "Brasil", "league": "Serie-A", "stadium": "Alfredo Jaconi", "founded": 1913, "fbref_id": "juventude"},
    {"name": "Criciúma", "short_name": "CRI", "country": "Brasil", "league": "Serie-A", "stadium": "Heriberto Hülse", "founded": 1921, "fbref_id": "criciuma"},
    {"name": "Vitória", "short_name": "VIT", "country": "Brasil", "league": "Serie-A", "stadium": "Barradão", "founded": 1899, "fbref_id": "vitoria"},
    {"name": "Atlético-GO", "short_name": "ACG", "country": "Brasil", "league": "Serie-A", "stadium": "Antácio Accioly", "founded": 1937, "fbref_id": "atletico-go"},
]

# ============================================================
# TIMES - PREMIER LEAGUE
# ============================================================
premier_league_teams = [
    {"name": "Manchester City", "short_name": "MCI", "country": "Inglaterra", "league": "Premier-League", "stadium": "Etihad Stadium", "founded": 1880, "fbref_id": "manchester-city"},
    {"name": "Arsenal", "short_name": "ARS", "country": "Inglaterra", "league": "Premier-League", "stadium": "Emirates Stadium", "founded": 1886, "fbref_id": "arsenal"},
    {"name": "Liverpool", "short_name": "LIV", "country": "Inglaterra", "league": "Premier-League", "stadium": "Anfield", "founded": 1892, "fbref_id": "liverpool"},
    {"name": "Aston Villa", "short_name": "AVL", "country": "Inglaterra", "league": "Premier-League", "stadium": "Villa Park", "founded": 1874, "fbref_id": "aston-villa"},
    {"name": "Tottenham Hotspur", "short_name": "TOT", "country": "Inglaterra", "league": "Premier-League", "stadium": "Tottenham Hotspur Stadium", "founded": 1882, "fbref_id": "tottenham-hotspur"},
    {"name": "Chelsea", "short_name": "CHE", "country": "Inglaterra", "league": "Premier-League", "stadium": "Stamford Bridge", "founded": 1905, "fbref_id": "chelsea"},
    {"name": "Newcastle United", "short_name": "NEW", "country": "Inglaterra", "league": "Premier-League", "stadium": "St James' Park", "founded": 1892, "fbref_id": "newcastle-united"},
    {"name": "Manchester United", "short_name": "MUN", "country": "Inglaterra", "league": "Premier-League", "stadium": "Old Trafford", "founded": 1878, "fbref_id": "manchester-united"},
    {"name": "West Ham United", "short_name": "WHU", "country": "Inglaterra", "league": "Premier-League", "stadium": "London Stadium", "founded": 1895, "fbref_id": "west-ham-united"},
    {"name": "Brighton & Hove Albion", "short_name": "BHA", "country": "Inglaterra", "league": "Premier-League", "stadium": "Amex Stadium", "founded": 1901, "fbref_id": "brighton-and-hove-albion"},
    {"name": "Bournemouth", "short_name": "BOU", "country": "Inglaterra", "league": "Premier-League", "stadium": "Vitality Stadium", "founded": 1899, "fbref_id": "bournemouth"},
    {"name": "Wolverhampton", "short_name": "WOL", "country": "Inglaterra", "league": "Premier-League", "stadium": "Molineux Stadium", "founded": 1877, "fbref_id": "wolverhampton-wanderers"},
    {"name": "Fulham", "short_name": "FUL", "country": "Inglaterra", "league": "Premier-League", "stadium": "Craven Cottage", "founded": 1879, "fbref_id": "fulham"},
    {"name": "Brentford", "short_name": "BRE", "country": "Inglaterra", "league": "Premier-League", "stadium": "Gtech Community Stadium", "founded": 1889, "fbref_id": "brentford"},
    {"name": "Crystal Palace", "short_name": "CRY", "country": "Inglaterra", "league": "Premier-League", "stadium": "Selhurst Park", "founded": 1905, "fbref_id": "crystal-palace"},
    {"name": "Nottingham Forest", "short_name": "NFO", "country": "Inglaterra", "league": "Premier-League", "stadium": "City Ground", "founded": 1865, "fbref_id": "nottingham-forest"},
    {"name": "Everton", "short_name": "EVE", "country": "Inglaterra", "league": "Premier-League", "stadium": "Goodison Park", "founded": 1878, "fbref_id": "everton"},
    {"name": "Leicester City", "short_name": "LEI", "country": "Inglaterra", "league": "Premier-League", "stadium": "King Power Stadium", "founded": 1884, "fbref_id": "leicester-city"},
    {"name": "Ipswich Town", "short_name": "IPS", "country": "Inglaterra", "league": "Premier-League", "stadium": "Portman Road", "founded": 1878, "fbref_id": "ipswich-town"},
    {"name": "Southampton", "short_name": "SOU", "country": "Inglaterra", "league": "Premier-League", "stadium": "St Mary's Stadium", "founded": 1885, "fbref_id": "southampton"},
]

# ============================================================
# JOGADORES (5 por time dos 6 primeiros da Serie A)
# ============================================================
player_templates = {
    "Flamengo": [
        {"name": "Pedro", "position": "FW", "nationality": "Brasil", "shirt_number": 9},
        {"name": "Everton Cebolinha", "position": "FW", "nationality": "Brasil", "shirt_number": 11},
        {"name": "De la Cruz", "position": "MF", "nationality": "Uruguai", "shirt_number": 18},
        {"name": "David Luiz", "position": "DF", "nationality": "Brasil", "shirt_number": 3},
        {"name": "Rossi", "position": "GK", "nationality": "Argentina", "shirt_number": 1},
    ],
    "Palmeiras": [
        {"name": "Endrick", "position": "FW", "nationality": "Brasil", "shirt_number": 9},
        {"name": "Rony", "position": "FW", "nationality": "Brasil", "shirt_number": 10},
        {"name": "Zé Rafael", "position": "MF", "nationality": "Brasil", "shirt_number": 8},
        {"name": "Murilo", "position": "DF", "nationality": "Brasil", "shirt_number": 3},
        {"name": "Weverton", "position": "GK", "nationality": "Brasil", "shirt_number": 1},
    ],
    "Botafogo": [
        {"name": "Tiquinho Soares", "position": "FW", "nationality": "Brasil", "shirt_number": 9},
        {"name": "Luiz Henrique", "position": "FW", "nationality": "Brasil", "shirt_number": 7},
        {"name": "Marlon Freitas", "position": "MF", "nationality": "Brasil", "shirt_number": 8},
        {"name": "Bastos", "position": "DF", "nationality": "Brasil", "shirt_number": 4},
        {"name": "John", "position": "GK", "nationality": "Colômbia", "shirt_number": 1},
    ],
    "São Paulo": [
        {"name": "Lucas Moura", "position": "FW", "nationality": "Brasil", "shirt_number": 10},
        {"name": "Calleri", "position": "FW", "nationality": "Argentina", "shirt_number": 9},
        {"name": "Michel Araújo", "position": "MF", "nationality": "Uruguai", "shirt_number": 11},
        {"name": "Diego Costa", "position": "DF", "nationality": "Brasil", "shirt_number": 4},
        {"name": "Rafael", "position": "GK", "nationality": "Brasil", "shirt_number": 1},
    ],
    "Corinthians": [
        {"name": "Yuri Alberto", "position": "FW", "nationality": "Brasil", "shirt_number": 9},
        {"name": "Wesley", "position": "FW", "nationality": "Brasil", "shirt_number": 11},
        {"name": "Maycon", "position": "MF", "nationality": "Brasil", "shirt_number": 7},
        {"name": "Fagner", "position": "DF", "nationality": "Brasil", "shirt_number": 2},
        {"name": "Cássio", "position": "GK", "nationality": "Brasil", "shirt_number": 1},
    ],
    "Internacional": [
        {"name": "Borré", "position": "FW", "nationality": "Colômbia", "shirt_number": 9},
        {"name": "Alan Patrick", "position": "MF", "nationality": "Brasil", "shirt_number": 10},
        {"name": "Enner Valencia", "position": "FW", "nationality": "Equador", "shirt_number": 11},
        {"name": "Cuesta", "position": "DF", "nationality": "Colômbia", "shirt_number": 4},
        {"name": "Sergio Rochet", "position": "GK", "nationality": "Uruguai", "shirt_number": 1},
    ],
}

# ============================================================
# EXECUÇÃO
# ============================================================

def main():
    print("=" * 60)
    print("⚽ SEEDING DATABASE")
    print("=" * 60)

    # --- Times da Serie A ---
    print("\n🏟️  Criando times da Serie A...")
    serie_a_ids = []
    for t in serie_a_teams:
        team = create_team(t)
        serie_a_ids.append(team["id"])
        print(f"  ✅ {t['name']} (ID: {team['id']})")

    # --- Times da Premier League ---
    print("\n🏟️  Criando times da Premier League...")
    pl_ids = []
    for t in premier_league_teams:
        team = create_team(t)
        pl_ids.append(team["id"])
        print(f"  ✅ {t['name']} (ID: {team['id']})")

    # --- Jogadores ---
    print("\n👤 Criando jogadores...")
    player_count = 0
    for i, team_name in enumerate(player_templates.keys()):
        team_id = serie_a_ids[i]
        for p in player_templates[team_name]:
            create_player({**p, "team_id": team_id})
            player_count += 1
        print(f"  ✅ {team_name}: 5 jogadores criados")
    print(f"  📊 Total: {player_count} jogadores")

    # --- Partidas da Serie A ---
    print("\n⚽ Criando partidas da Serie A...")
    match_ids = []
    match_dates = [
        "2024-04-14T16:00:00", "2024-04-17T20:00:00", "2024-04-21T16:00:00",
        "2024-04-24T20:30:00", "2024-04-28T16:00:00", "2024-05-01T20:00:00",
        "2024-05-05T16:00:00", "2024-05-08T20:30:00", "2024-05-12T16:00:00",
        "2024-05-15T20:00:00", "2024-05-19T16:00:00", "2024-05-22T20:30:00",
        "2024-05-26T16:00:00", "2024-05-29T20:00:00", "2024-06-02T16:00:00",
    ]
    referees = [
        "Anderson Daronco", "Rafael Claus", "Wilton Sampaio",
        "Bruno Arleu", "Leandro Pedro", "Braga Danilo",
        "Savio Perez", "Edina Alves", "Flávio de Souza",
    ]

    # Gerar 15 partidas entre times da Serie A
    random.seed(42)  # Para reprodutibilidade
    for i in range(15):
        home_idx = i % len(serie_a_ids)
        away_idx = (i + 1) % len(serie_a_ids)
        if home_idx == away_idx:
            away_idx = (away_idx + 1) % len(serie_a_ids)

        home_score = random.randint(0, 3)
        away_score = random.randint(0, 2)
        home_xg = round(random.uniform(0.5, 3.0), 2)
        away_xg = round(random.uniform(0.3, 2.5), 2)

        match = create_match({
            "home_team_id": serie_a_ids[home_idx],
            "away_team_id": serie_a_ids[away_idx],
            "competition": "Serie-A",
            "season": "2024",
            "match_date": match_dates[i],
            "venue": serie_a_teams[home_idx]["stadium"],
            "home_score": home_score,
            "away_score": away_score,
            "home_xg": home_xg,
            "away_xg": away_xg,
            "attendance": random.randint(20000, 65000),
            "referee": referees[i % len(referees)],
        })
        match_ids.append(match["id"])
        home_name = serie_a_teams[home_idx]["short_name"]
        away_name = serie_a_teams[away_idx]["short_name"]
        print(f"  ✅ {home_name} {home_score} x {away_score} {away_name} (ID: {match['id']})")

    # --- Partidas da Premier League ---
    print("\n⚽ Criando partidas da Premier League...")
    pl_match_ids = []
    for i in range(15):
        home_idx = i % len(pl_ids)
        away_idx = (i + 3) % len(pl_ids)
        if home_idx == away_idx:
            away_idx = (away_idx + 1) % len(pl_ids)

        home_score = random.randint(0, 3)
        away_score = random.randint(0, 2)
        home_xg = round(random.uniform(0.5, 3.0), 2)
        away_xg = round(random.uniform(0.3, 2.5), 2)

        match = create_match({
            "home_team_id": pl_ids[home_idx],
            "away_team_id": pl_ids[away_idx],
            "competition": "Premier-League",
            "season": "2024-2025",
            "match_date": match_dates[i],
            "venue": premier_league_teams[home_idx]["stadium"],
            "home_score": home_score,
            "away_score": away_score,
            "home_xg": home_xg,
            "away_xg": away_xg,
            "attendance": random.randint(30000, 75000),
            "referee": random.choice(referees),
        })
        pl_match_ids.append(match["id"])
        home_name = premier_league_teams[home_idx]["short_name"]
        away_name = premier_league_teams[away_idx]["short_name"]
        print(f"  ✅ {home_name} {home_score} x {away_score} {away_name} (ID: {match['id']})")

    # --- Estatísticas ---
    print("\n📊 Criando estatísticas das partidas...")
    stats_count = 0

    # Pair (match_id, home_team_id, away_team_id) para cada partida criada
    all_matches = []
    for i in range(15):
        home_idx = i % len(serie_a_ids)
        away_idx = (i + 1) % len(serie_a_ids)
        if home_idx == away_idx:
            away_idx = (away_idx + 1) % len(serie_a_ids)
        all_matches.append((match_ids[i], serie_a_ids[home_idx], serie_a_ids[away_idx]))

    for i in range(15):
        home_idx = i % len(pl_ids)
        away_idx = (i + 3) % len(pl_ids)
        if home_idx == away_idx:
            away_idx = (away_idx + 1) % len(pl_ids)
        all_matches.append((pl_match_ids[i], pl_ids[home_idx], pl_ids[away_idx]))

    for match_id, home_team_id, away_team_id in all_matches:
        for is_home in [True, False]:
            team_id = home_team_id if is_home else away_team_id
            possession = random.uniform(40, 65) if is_home else 100 - random.uniform(40, 65)
            create_stats({
                "match_id": match_id,
                "team_id": team_id,
                "is_home": is_home,
                "possession": round(possession, 1),
                "shots": random.randint(5, 18),
                "shots_on_target": random.randint(1, 8),
                "corners": random.randint(2, 10),
                "fouls": random.randint(8, 20),
                "yellow_cards": random.randint(0, 4),
                "red_cards": random.randint(0, 1),
                "offsides": random.randint(0, 5),
                "xg": round(random.uniform(0.3, 3.0), 2),
                "xg_against": round(random.uniform(0.3, 2.5), 2),
                "passes": random.randint(300, 600),
                "pass_accuracy": round(random.uniform(70, 95), 1),
                "tackles": random.randint(10, 25),
                "interceptions": random.randint(5, 15),
                "saves": random.randint(0, 6),
            })
            stats_count += 1
    print(f"  📊 Total: {stats_count} registros de estatísticas")

    # --- Resumo ---
    print("\n" + "=" * 60)
    print("✅ SEEDING CONCLUÍDO!")
    print("=" * 60)
    print(f"  🏟️  Times Serie A:      {len(serie_a_ids)}")
    print(f"  🏟️  Times Premier League: {len(pl_ids)}")
    print(f"  👤  Jogadores:          {player_count}")
    print(f"  ⚽  Partidas Serie A:   {len(match_ids)}")
    print(f"  ⚽  Partidas PL:        {len(pl_match_ids)}")
    print(f"  📊  Estatísticas:       {stats_count}")
    print(f"\n  🌐 Acesse: http://localhost:5173")
    print(f"  📚 Docs:   http://localhost:8000/docs")


if __name__ == "__main__":
    main()
