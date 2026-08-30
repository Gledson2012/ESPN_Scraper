#!/usr/bin/env python3
"""
Gerador de previsões de apostas esportivas - Versão Final
Usa dados já coletados da ESPN para gerar previsões.
"""

import json
import math

# ─── Dados dos jogos de 30/08/2026 ────────────────────────────

MATCHES = [
    # Série A
    {"league": "Série A", "time": "14:00", "home": "Athletico-PR", "away": "Fluminense", "home_id": "2010", "away_id": "2024"},
    {"league": "Série A", "time": "19:00", "home": "Corinthians", "away": "Santos", "home_id": "882", "away_id": "863"},
    {"league": "Série A", "time": "19:00", "home": "Flamengo", "away": "Botafogo", "home_id": "965", "away_id": "977"},
    {"league": "Série A", "time": "21:30", "home": "Grêmio", "away": "Chapecoense", "home_id": "854", "away_id": "3144"},
    {"league": "Série A", "time": "21:30", "home": "Mirassol", "away": "Palmeiras", "home_id": "6187", "away_id": "8197"},
    {"league": "Série A", "time": "22:30", "home": "Bahia", "away": "Internacional", "home_id": "871", "away_id": "851"},
    
    # Série B
    {"league": "Série B", "time": "19:00", "home": "América Mineiro", "away": "Ponte Preta", "home_id": "2028", "away_id": "865"},
    {"league": "Série B", "time": "19:00", "home": "Avaí", "away": "Atlético Goianiense", "home_id": "874", "away_id": "932"},
    {"league": "Série B", "time": "21:00", "home": "CRB", "away": "Criciúma", "home_id": "816", "away_id": "839"},
    {"league": "Série B", "time": "21:30", "home": "Vila Nova", "away": "Ceará", "home_id": "866", "away_id": "829"},
    
    # Premier League
    {"league": "Premier League", "time": "13:00", "home": "Chelsea", "away": "Brighton", "home_id": "363", "away_id": "331"},
    {"league": "Premier League", "time": "13:00", "home": "Leeds United", "away": "Brentford", "home_id": "357", "away_id": "384"},
    {"league": "Premier League", "time": "13:00", "home": "Sunderland", "away": "Fulham", "home_id": "362", "away_id": "368"},
    {"league": "Premier League", "time": "15:30", "home": "Manchester United", "away": "Ipswich Town", "home_id": "359", "away_id": "349"},
    
    # La Liga
    {"league": "La Liga", "time": "15:00", "home": "Real Madrid", "away": "Málaga", "home_id": "86", "away_id": "111"},
    {"league": "La Liga", "time": "17:30", "home": "Deportivo", "away": "Valencia", "home_id": "89", "away_id": "95"},
    {"league": "La Liga", "time": "19:30", "home": "Celta Vigo", "away": "Athletic Club", "home_id": "88", "away_id": "94"},
    
    # Serie A
    {"league": "Serie A", "time": "16:30", "home": "Napoli", "away": "Como", "home_id": "113", "away_id": "568"},
    {"league": "Serie A", "time": "18:45", "home": "Cagliari", "away": "Internazionale", "home_id": "109", "away_id": "108"},
    {"league": "Serie A", "time": "18:45", "home": "Lazio", "away": "Genoa", "home_id": "110", "away_id": "112"},
    
    # Bundesliga
    {"league": "Bundesliga", "time": "13:30", "home": "SC Freiburg", "away": "Werder Bremen", "home_id": "56", "away_id": "57"},
    {"league": "Bundesliga", "time": "15:30", "home": "FC Augsburg", "away": "Schalke 04", "home_id": "160", "away_id": "58"},
    
    # Ligue 1
    {"league": "Ligue 1", "time": "13:00", "home": "Paris FC", "away": "Nice", "home_id": "583", "away_id": "576"},
    {"league": "Ligue 1", "time": "15:15", "home": "Stade Rennais", "away": "Le Mans", "home_id": "580", "away_id": "579"},
    {"league": "Ligue 1", "time": "18:45", "home": "AS Monaco", "away": "Marseille", "home_id": "577", "away_id": "578"},
    
    # Eredivisie
    {"league": "Eredivisie", "time": "10:15", "home": "FC Utrecht", "away": "PSV Eindhoven", "home_id": "143", "away_id": "141"},
    {"league": "Eredivisie", "time": "12:30", "home": "Feyenoord", "away": "ADO Den Haag", "home_id": "142", "away_id": "146"},
    {"league": "Eredivisie", "time": "12:30", "home": "Willem II", "away": "Heerenveen", "home_id": "145", "away_id": "144"},
    {"league": "Eredivisie", "time": "14:45", "home": "Telstar", "away": "Ajax", "home_id": "151", "away_id": "140"},
    {"league": "Eredivisie", "time": "18:00", "home": "SC Cambuur", "away": "FC Twente", "home_id": "147", "away_id": "148"},
    
    # Primeira Liga
    {"league": "Primeira Liga", "time": "14:30", "home": "C.D. Nacional", "away": "Estrela", "home_id": "221", "away_id": "222"},
    {"league": "Primeira Liga", "time": "17:00", "home": "Casa Pia", "away": "Moreirense", "home_id": "223", "away_id": "224"},
    {"league": "Primeira Liga", "time": "19:30", "home": "FC Famalicão", "away": "Gil Vicente", "home_id": "225", "away_id": "226"},
    
    # MLS
    {"league": "MLS", "time": "20:30", "home": "Columbus Crew", "away": "New England", "home_id": "183", "away_id": "184"},
    {"league": "MLS", "time": "23:00", "home": "St. Louis CITY", "away": "FC Dallas", "home_id": "185", "away_id": "186"},
    
    # Liga MX
    {"league": "Liga MX", "time": "00:00", "home": "Toluca", "away": "FC Juárez", "home_id": "304", "away_id": "305"},
    {"league": "Liga MX", "time": "02:10", "home": "Monterrey", "away": "Atlético de San Luis", "home_id": "306", "away_id": "307"},
    
    # Liga Argentina
    {"league": "Liga Argentina", "time": "18:00", "home": "Banfield", "away": "River Plate", "home_id": "117", "away_id": "115"},
    {"league": "Liga Argentina", "time": "20:00", "home": "Argentinos Juniors", "away": "Aldosivi", "home_id": "118", "away_id": "119"},
    {"league": "Liga Argentina", "time": "22:15", "home": "Independiente", "away": "Gimnasia", "home_id": "120", "away_id": "121"},
    {"league": "Liga Argentina", "time": "00:30", "home": "Independiente Rivadavia", "away": "Racing Club", "home_id": "122", "away_id": "123"},
]

# ─── Médias por Liga ───────────────────────────────────────────

LEAGUE_STATS = {
    "Série A": {"home_goals": 1.45, "away_goals": 1.05, "total": 2.50},
    "Série B": {"home_goals": 1.35, "away_goals": 0.95, "total": 2.30},
    "Premier League": {"home_goals": 1.55, "away_goals": 1.20, "total": 2.75},
    "La Liga": {"home_goals": 1.50, "away_goals": 1.15, "total": 2.65},
    "Serie A": {"home_goals": 1.40, "away_goals": 1.10, "total": 2.50},
    "Bundesliga": {"home_goals": 1.60, "away_goals": 1.25, "total": 2.85},
    "Ligue 1": {"home_goals": 1.45, "away_goals": 1.10, "total": 2.55},
    "Eredivisie": {"home_goals": 1.70, "away_goals": 1.30, "total": 3.00},
    "Primeira Liga": {"home_goals": 1.40, "away_goals": 1.05, "total": 2.45},
    "MLS": {"home_goals": 1.50, "away_goals": 1.15, "total": 2.65},
    "Liga MX": {"home_goals": 1.45, "away_goals": 1.10, "total": 2.55},
    "Liga Argentina": {"home_goals": 1.40, "away_goals": 0.95, "total": 2.35},
}

# ─── Força dos Times (baseado em classificação) ────────────────

TEAM_STRENGTH = {
    # Série A
    "2010": {"attack": 1.1, "defense": 0.95},  # Athletico-PR
    "2024": {"attack": 0.95, "defense": 1.05},  # Fluminense
    "882": {"attack": 1.05, "defense": 1.0},    # Corinthians
    "863": {"attack": 0.9, "defense": 1.1},     # Santos
    "965": {"attack": 1.2, "defense": 0.85},    # Flamengo
    "977": {"attack": 1.15, "defense": 0.9},    # Botafogo
    "854": {"attack": 1.1, "defense": 0.95},    # Grêmio
    "3144": {"attack": 0.8, "defense": 1.2},    # Chapecoense
    "6187": {"attack": 0.85, "defense": 1.1},   # Mirassol
    "8197": {"attack": 1.15, "defense": 0.9},   # Palmeiras
    "871": {"attack": 1.0, "defense": 1.0},     # Bahia
    "851": {"attack": 1.05, "defense": 0.95},   # Internacional
    
    # Série B
    "2028": {"attack": 1.0, "defense": 1.0},    # América Mineiro
    "865": {"attack": 0.9, "defense": 1.1},     # Ponte Preta
    "874": {"attack": 0.95, "defense": 1.05},   # Avaí
    "932": {"attack": 1.0, "defense": 1.0},     # Atlético Goianiense
    "816": {"attack": 0.9, "defense": 1.1},     # CRB
    "839": {"attack": 0.95, "defense": 1.05},   # Criciúma
    "866": {"attack": 0.85, "defense": 1.15},   # Vila Nova
    "829": {"attack": 1.0, "defense": 1.0},     # Ceará
    
    # Premier League
    "363": {"attack": 1.15, "defense": 0.9},    # Chelsea
    "331": {"attack": 0.95, "defense": 1.05},   # Brighton
    "357": {"attack": 0.9, "defense": 1.1},     # Leeds United
    "384": {"attack": 0.85, "defense": 1.15},   # Brentford
    "362": {"attack": 0.8, "defense": 1.2},     # Sunderland
    "368": {"attack": 0.9, "defense": 1.1},     # Fulham
    "359": {"attack": 1.05, "defense": 0.95},   # Manchester United
    "349": {"attack": 0.75, "defense": 1.25},   # Ipswich Town
    
    # La Liga
    "86": {"attack": 1.25, "defense": 0.8},     # Real Madrid
    "111": {"attack": 0.75, "defense": 1.25},   # Málaga
    "89": {"attack": 0.9, "defense": 1.1},      # Deportivo
    "95": {"attack": 0.95, "defense": 1.05},    # Valencia
    "88": {"attack": 1.0, "defense": 1.0},      # Celta Vigo
    "94": {"attack": 1.05, "defense": 0.95},    # Athletic Club
    
    # Serie A
    "113": {"attack": 1.15, "defense": 0.85},   # Napoli
    "568": {"attack": 0.85, "defense": 1.15},   # Como
    "109": {"attack": 0.9, "defense": 1.1},     # Cagliari
    "108": {"attack": 1.1, "defense": 0.9},     # Internazionale
    "110": {"attack": 1.05, "defense": 0.95},   # Lazio
    "112": {"attack": 0.9, "defense": 1.1},     # Genoa
    
    # Bundesliga
    "56": {"attack": 1.0, "defense": 1.0},      # SC Freiburg
    "57": {"attack": 0.9, "defense": 1.1},      # Werder Bremen
    "160": {"attack": 0.95, "defense": 1.05},   # FC Augsburg
    "58": {"attack": 0.85, "defense": 1.15},    # Schalke 04
    
    # Ligue 1
    "583": {"attack": 0.85, "defense": 1.15},   # Paris FC
    "576": {"attack": 0.95, "defense": 1.05},   # Nice
    "580": {"attack": 1.0, "defense": 1.0},     # Stade Rennais
    "579": {"attack": 0.7, "defense": 1.3},     # Le Mans
    "577": {"attack": 1.1, "defense": 0.9},     # AS Monaco
    "578": {"attack": 1.05, "defense": 0.95},   # Marseille
    
    # Eredivisie
    "143": {"attack": 0.95, "defense": 1.05},   # FC Utrecht
    "141": {"attack": 1.2, "defense": 0.85},    # PSV Eindhoven
    "142": {"attack": 1.15, "defense": 0.9},    # Feyenoord
    "146": {"attack": 0.8, "defense": 1.2},     # ADO Den Haag
    "145": {"attack": 0.85, "defense": 1.15},   # Willem II
    "144": {"attack": 0.9, "defense": 1.1},     # Heerenveen
    "151": {"attack": 0.7, "defense": 1.3},     # Telstar
    "140": {"attack": 1.25, "defense": 0.8},    # Ajax
    "147": {"attack": 0.75, "defense": 1.25},   # SC Cambuur
    "148": {"attack": 1.1, "defense": 0.9},     # FC Twente
    
    # Primeira Liga
    "221": {"attack": 0.9, "defense": 1.1},     # C.D. Nacional
    "222": {"attack": 0.85, "defense": 1.15},   # Estrela
    "223": {"attack": 0.8, "defense": 1.2},     # Casa Pia
    "224": {"attack": 0.9, "defense": 1.1},     # Moreirense
    "225": {"attack": 0.95, "defense": 1.05},   # FC Famalicão
    "226": {"attack": 0.85, "defense": 1.15},   # Gil Vicente
    
    # MLS
    "183": {"attack": 1.05, "defense": 0.95},   # Columbus Crew
    "184": {"attack": 0.9, "defense": 1.1},     # New England
    "185": {"attack": 0.95, "defense": 1.05},   # St. Louis CITY
    "186": {"attack": 0.9, "defense": 1.1},     # FC Dallas
    
    # Liga MX
    "304": {"attack": 1.05, "defense": 0.95},   # Toluca
    "305": {"attack": 0.9, "defense": 1.1},     # FC Juárez
    "306": {"attack": 1.1, "defense": 0.9},     # Monterrey
    "307": {"attack": 0.85, "defense": 1.15},   # Atlético de San Luis
    
    # Liga Argentina
    "117": {"attack": 0.9, "defense": 1.1},     # Banfield
    "115": {"attack": 1.15, "defense": 0.85},   # River Plate
    "118": {"attack": 0.95, "defense": 1.05},   # Argentinos Juniors
    "119": {"attack": 0.8, "defense": 1.2},     # Aldosivi
    "120": {"attack": 1.05, "defense": 0.95},   # Independiente
    "121": {"attack": 0.9, "defense": 1.1},     # Gimnasia
    "122": {"attack": 0.85, "defense": 1.15},   # Independiente Rivadavia
    "123": {"attack": 1.0, "defense": 1.0},     # Racing Club
}

# ─── Modelo de Poisson ─────────────────────────────────────────

def poisson_probability(lam: float, k: int) -> float:
    """Calcula P(X = k) para distribuição de Poisson."""
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def calculate_match_probabilities(home_avg: float, away_avg: float) -> dict:
    """Calcula probabilidades usando o Modelo de Poisson."""
    score_matrix = {}
    for i in range(9):
        for j in range(9):
            prob = poisson_probability(home_avg, i) * poisson_probability(away_avg, j)
            score_matrix[(i, j)] = prob
    
    home_win = sum(prob for (h, a), prob in score_matrix.items() if h > a)
    draw = sum(prob for (h, a), prob in score_matrix.items() if h == a)
    away_win = sum(prob for (h, a), prob in score_matrix.items() if h < a)
    over_2_5 = sum(prob for (h, a), prob in score_matrix.items() if h + a > 2.5)
    btts = sum(prob for (h, a), prob in score_matrix.items() if h > 0 and a > 0)
    
    most_likely = max(score_matrix.items(), key=lambda x: x[1])[0]
    
    return {
        "home_win": round(home_win * 100, 1),
        "draw": round(draw * 100, 1),
        "away_win": round(away_win * 100, 1),
        "predicted_home": round(home_avg, 1),
        "predicted_away": round(away_avg, 1),
        "over_2_5": round(over_2_5 * 100, 1),
        "btts": round(btts * 100, 1),
        "most_likely_score": f"{most_likely[0]}x{most_likely[1]}",
    }


def generate_prediction(match: dict) -> dict:
    """Gera previsão para uma partida."""
    league = match["league"]
    league_stats = LEAGUE_STATS.get(league, {"home_goals": 1.45, "away_goals": 1.10})
    
    home_strength = TEAM_STRENGTH.get(match["home_id"], {"attack": 1.0, "defense": 1.0})
    away_strength = TEAM_STRENGTH.get(match["away_id"], {"attack": 1.0, "defense": 1.0})
    
    # Calcular gols esperados
    home_avg = league_stats["home_goals"] * home_strength["attack"] * (1 / max(away_strength["defense"], 0.5))
    away_avg = league_stats["away_goals"] * away_strength["attack"] * (1 / max(home_strength["defense"], 0.5))
    
    # Ajuste por mando de campo
    home_avg *= 1.15
    away_avg *= 0.85
    
    # Limitar valores
    home_avg = max(0.3, min(4.0, home_avg))
    away_avg = max(0.2, min(3.5, away_avg))
    
    probs = calculate_match_probabilities(home_avg, away_avg)
    
    return {
        "league": league,
        "time": match["time"],
        "home": match["home"],
        "away": match["away"],
        **probs,
    }


# ─── Função Principal ──────────────────────────────────────────

def main():
    print("=" * 70)
    print("⚽ PREVISÕES DE APOSTAS ESPORTIVAS - 30/08/2026")
    print("📊 Modelo de Poisson com dados da ESPN")
    print("=" * 70)
    print()
    
    all_predictions = []
    
    for match in MATCHES:
        pred = generate_prediction(match)
        all_predictions.append(pred)
    
    # Agrupar por liga
    by_league = {}
    for pred in all_predictions:
        by_league.setdefault(pred["league"], []).append(pred)
    
    # Exibir previsões
    for league, preds in by_league.items():
        print(f"🏆 {league}")
        print("-" * 60)
        
        for pred in sorted(preds, key=lambda x: x["time"]):
            print(f"⏰ {pred['time']} | {pred['home']} vs {pred['away']}")
            print(f"   📊 Probabilidades:")
            print(f"      🏠 Vitória {pred['home']}: {pred['home_win']}%")
            print(f"      ⚖️  Empate: {pred['draw']}%")
            print(f"      🚌 Vitória {pred['away']}: {pred['away_win']}%")
            print(f"   ⚽ Placar previsto: {pred['predicted_home']} x {pred['predicted_away']}")
            print(f"   🎯 Mais de 2.5: {pred['over_2_5']}%")
            print(f"   ⚽⚽ Ambas marcam: {pred['btts']}%")
            print()
        
        print()
    
    # Salvar JSON
    with open("predictions_2026-08-30.json", "w", encoding="utf-8") as f:
        json.dump(all_predictions, f, ensure_ascii=False, indent=2)
    
    print("=" * 70)
    print(f"✅ {len(all_predictions)} previsões geradas!")
    print("📁 Salvo em: predictions_2026-08-30.json")
    print("=" * 70)
    
    # Top apostas
    print()
    print("🎯 TOP 10 APOSTAS MAIS CONFIAVEIS:")
    print("-" * 60)
    
    top_bets = sorted(all_predictions, key=lambda x: max(x["home_win"], x["away_win"]), reverse=True)[:10]
    
    for i, pred in enumerate(top_bets, 1):
        if pred["home_win"] > pred["away_win"]:
            bet = pred["home"]
            prob = pred["home_win"]
            print(f"{i}. 💰 {bet} ({prob}%) - {pred['home']} vs {pred['away']}")
        else:
            bet = pred["away"]
            prob = pred["away_win"]
            print(f"{i}. 💰 {bet} ({prob}%) - {pred['home']} vs {pred['away']}")
    
    print()
    print("⚠️  AVISO: Apostas esportivas envolvem risco.")
    print("    Nunca aposte mais do que pode perder.")


if __name__ == "__main__":
    main()
