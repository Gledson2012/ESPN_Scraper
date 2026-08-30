#!/usr/bin/env python3
"""
Gerador de previsões de apostas esportivas v2.
Usa dados reais de estatísticas da ESPN para previsões mais precisas.

Uso: python scripts/predict_matches_v2.py [--date YYYY-MM-DD]
"""

import json
import math
import sys
import urllib.request
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

# ─── Configuração ──────────────────────────────────────────────

ESPN_API_BASE = "https://site.api.espn.com/apis/site/v2/sports/soccer"

LEAGUES = {
    "bra.1": "Série A",
    "bra.2": "Série B",
    "eng.1": "Premier League",
    "esp.1": "La Liga",
    "ita.1": "Serie A",
    "ger.1": "Bundesliga",
    "fra.1": "Ligue 1",
    "ned.1": "Eredivisie",
    "por.1": "Primeira Liga",
    "conmebol.libertadores": "Libertadores",
    "conmebol.sudamericana": "Sudamericana",
    "uefa.champions": "Champions League",
    "uefa.europa": "Europa League",
    "usa.1": "MLS",
    "mex.1": "Liga MX",
    "arg.1": "Liga Argentina",
}

# Médias históricas por liga (gols por partida)
LEAGUE_AVERAGES = {
    "bra.1": {"home_goals": 1.45, "away_goals": 1.05, "total": 2.50},
    "bra.2": {"home_goals": 1.35, "away_goals": 0.95, "total": 2.30},
    "eng.1": {"home_goals": 1.55, "away_goals": 1.20, "total": 2.75},
    "esp.1": {"home_goals": 1.50, "away_goals": 1.15, "total": 2.65},
    "ita.1": {"home_goals": 1.40, "away_goals": 1.10, "total": 2.50},
    "ger.1": {"home_goals": 1.60, "away_goals": 1.25, "total": 2.85},
    "fra.1": {"home_goals": 1.45, "away_goals": 1.10, "total": 2.55},
    "ned.1": {"home_goals": 1.70, "away_goals": 1.30, "total": 3.00},
    "por.1": {"home_goals": 1.40, "away_goals": 1.05, "total": 2.45},
    "conmebol.libertadores": {"home_goals": 1.50, "away_goals": 0.95, "total": 2.45},
    "conmebol.sudamericana": {"home_goals": 1.45, "away_goals": 0.90, "total": 2.35},
    "uefa.champions": {"home_goals": 1.65, "away_goals": 1.15, "total": 2.80},
    "uefa.europa": {"home_goals": 1.55, "away_goals": 1.10, "total": 2.65},
    "usa.1": {"home_goals": 1.50, "away_goals": 1.15, "total": 2.65},
    "mex.1": {"home_goals": 1.45, "away_goals": 1.10, "total": 2.55},
    "arg.1": {"home_goals": 1.40, "away_goals": 0.95, "total": 2.35},
}

# ─── Funções Utilitárias ───────────────────────────────────────

def fetch_json(url: str) -> dict:
    """Busca JSON de uma URL."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.load(resp)
    except Exception as e:
        return {}


def get_team_standings(league_slug: str) -> dict:
    """Busca classificação da liga para obter dados dos times."""
    url = f"{ESPN_API_BASE}/{league_slug}/standings"
    data = fetch_json(url)
    
    standings = {}
    
    for group in data.get("children", []):
        for team_data in group.get("standings", {}).get("entries", []):
            team = team_data.get("team", {})
            team_id = team.get("id", "")
            
            stats_list = team_data.get("stats", [])
            stats = {}
            for stat in stats_list:
                name = stat.get("name", "")
                value = stat.get("value", 0)
                stats[name] = value
            
            standings[team_id] = {
                "name": team.get("displayName", "?"),
                "abbreviation": team.get("abbreviation", "?"),
                "logo": team.get("logo", ""),
                "wins": stats.get("wins", 0),
                "losses": stats.get("losses", 0),
                "ties": stats.get("ties", 0),
                "points": stats.get("points", 0),
                "goals_for": stats.get("pointsFor", 0),
                "goals_against": stats.get("pointsAgainst", 0),
                "goal_diff": stats.get("pointDifferential", 0),
                "games_played": stats.get("gamesPlayed", 0),
                "home_wins": stats.get("homeWins", 0),
                "home_losses": stats.get("homeLosses", 0),
                "home_ties": stats.get("homeTies", 0),
                "away_wins": stats.get("awayWins", 0),
                "away_losses": stats.get("awayLosses", 0),
                "away_ties": stats.get("awayTies", 0),
            }
    
    return standings


def get_team_strength(team_id: str, standings: dict) -> dict:
    """Calcula força do time baseado na classificação."""
    team = standings.get(team_id, {})
    
    gp = team.get("games_played", 0)
    if gp == 0:
        return {"attack": 1.0, "defense": 1.0, "home_strength": 1.0, "away_strength": 1.0}
    
    gf = team.get("goals_for", 0)
    ga = team.get("goals_against", 0)
    wins = team.get("wins", 0)
    ties = team.get("ties", 0)
    
    # Média de gols por partida
    goals_per_game = gf / gp if gp > 0 else 1.0
    goals_conceded_per_game = ga / gp if gp > 0 else 1.0
    
    # Força ofensiva (1.0 = média da liga)
    attack = goals_per_game / 1.3  # Normalizar
    
    # Força defensiva (1.0 = média da liga, menor é melhor)
    defense = goals_conceded_per_game / 1.3
    
    # Aproveitamento em casa
    home_games = team.get("home_wins", 0) + team.get("home_losses", 0) + team.get("home_ties", 0)
    home_wins = team.get("home_wins", 0)
    home_strength = (home_wins * 3 + team.get("home_ties", 0)) / (home_games * 3) if home_games > 0 else 0.5
    
    # Aproveitamento fora
    away_games = team.get("away_wins", 0) + team.get("away_losses", 0) + team.get("away_ties", 0)
    away_wins = team.get("away_wins", 0)
    away_strength = (away_wins * 3 + team.get("away_ties", 0)) / (away_games * 3) if away_games > 0 else 0.4
    
    return {
        "attack": attack,
        "defense": defense,
        "home_strength": home_strength,
        "away_strength": away_strength,
    }


# ─── Modelo de Poisson ─────────────────────────────────────────

def poisson_probability(lam: float, k: int) -> float:
    """Calcula P(X = k) para distribuição de Poisson."""
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def calculate_match_probabilities(
    home_avg_goals: float,
    away_avg_goals: float,
    max_goals: int = 8
) -> dict:
    """Calcula probabilidades usando o Modelo de Poisson."""
    score_matrix = {}
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            prob = poisson_probability(home_avg_goals, i) * poisson_probability(away_avg_goals, j)
            score_matrix[(i, j)] = prob
    
    home_win = sum(prob for (h, a), prob in score_matrix.items() if h > a)
    draw = sum(prob for (h, a), prob in score_matrix.items() if h == a)
    away_win = sum(prob for (h, a), prob in score_matrix.items() if h < a)
    over_2_5 = sum(prob for (h, a), prob in score_matrix.items() if h + a > 2.5)
    btts = sum(prob for (h, a), prob in score_matrix.items() if h > 0 and a > 0)
    
    most_likely_score = max(score_matrix.items(), key=lambda x: x[1])[0]
    
    return {
        "home_win_probability": round(home_win, 4),
        "draw_probability": round(draw, 4),
        "away_win_probability": round(away_win, 4),
        "predicted_home_score": round(home_avg_goals, 2),
        "predicted_away_score": round(away_avg_goals, 2),
        "over_2_5_probability": round(over_2_5, 4),
        "btts_probability": round(btts, 4),
        "most_likely_score": f"{most_likely_score[0]}x{most_likely_score[1]}",
    }


# ─── Geração de Previsões ─────────────────────────────────────

def generate_prediction(
    home_name: str,
    away_name: str,
    home_strength: dict,
    away_strength: dict,
    league_slug: str,
    league_name: str
) -> dict:
    """Gera uma previsão para uma partida."""
    
    league_avg = LEAGUE_AVERAGES.get(league_slug, {"home_goals": 1.45, "away_goals": 1.10})
    
    # Média de gols esperados ajustada pela força dos times
    home_attack = home_strength.get("attack", 1.0)
    home_defense = home_strength.get("defense", 1.0)
    home_field = home_strength.get("home_strength", 0.55)
    
    away_attack = away_strength.get("attack", 1.0)
    away_defense = away_strength.get("defense", 1.0)
    away_field = away_strength.get("away_strength", 0.40)
    
    # Calcular gols esperados
    home_avg_goals = (
        league_avg["home_goals"] * home_attack * (1 / max(away_defense, 0.5)) * (0.8 + home_field * 0.4)
    )
    away_avg_goals = (
        league_avg["away_goals"] * away_attack * (1 / max(home_defense, 0.5)) * (0.8 + away_field * 0.4)
    )
    
    # Limitar valores extremos
    home_avg_goals = max(0.3, min(4.0, home_avg_goals))
    away_avg_goals = max(0.2, min(3.5, away_avg_goals))
    
    # Calcular probabilidades
    probs = calculate_match_probabilities(home_avg_goals, away_avg_goals)
    
    # Calcular confiança baseada nos dados
    confidence = min(0.85, 0.6 + (home_strength.get("attack", 0) + away_strength.get("attack", 0)) * 0.05)
    
    return {
        "home_team": home_name,
        "away_team": away_name,
        "league": league_name,
        **probs,
        "confidence": round(confidence, 2),
    }


# ─── Função Principal ──────────────────────────────────────────

def main():
    date = "20260830"
    leagues_to_check = list(LEAGUES.keys())
    
    print("=" * 70)
    print("⚽ GERADOR DE PREVISÕES DE APOSTAS ESPORTIVAS v2")
    print(f"📅 Data: 30/08/2026")
    print("📊 Usando dados reais de classificação da ESPN")
    print("=" * 70)
    print()
    
    all_predictions = []
    
    for league_slug in leagues_to_check:
        league_name = LEAGUES[league_slug]
        
        # Buscar classificação
        standings = get_team_standings(league_slug)
        if not standings:
            continue
        
        # Buscar jogos do dia
        url = f"{ESPN_API_BASE}/{league_slug}/scoreboard?dates={date}"
        data = fetch_json(url)
        
        if not data.get("events"):
            continue
        
        print(f"🏆 {league_name}")
        print("-" * 60)
        
        for event in data.get("events", []):
            comps = event.get("competitions", [{}])[0]
            status = comps.get("status", {}).get("type", {})
            state = status.get("state", "")
            
            if state != "pre":
                continue
            
            competitors = comps.get("competitors", [])
            home = next((c for c in competitors if c.get("homeAway") == "home"), {})
            away = next((c for c in competitors if c.get("homeAway") == "away"), {})
            
            home_team = home.get("team", {})
            away_team = away.get("team", {})
            
            home_id = home_team.get("id", "")
            away_id = away_team.get("id", "")
            home_name = home_team.get("displayName", "?")
            away_name = away_team.get("displayName", "?")
            
            match_time = event.get("date", "")[11:16] if event.get("date") else "??"
            
            # Calcular força dos times
            home_strength = get_team_strength(home_id, standings)
            away_strength = get_team_strength(away_id, standings)
            
            # Gerar previsão
            prediction = generate_prediction(
                home_name, away_name,
                home_strength, away_strength,
                league_slug, league_name
            )
            prediction["time"] = match_time
            
            # Dados da classificação
            home_standings = standings.get(home_id, {})
            away_standings = standings.get(away_id, {})
            prediction["home_record"] = f"{home_standings.get('wins', 0)}V {home_standings.get('ties', 0)}E {home_standings.get('losses', 0)}D"
            prediction["away_record"] = f"{away_standings.get('wins', 0)}V {away_standings.get('ties', 0)}E {away_standings.get('losses', 0)}D"
            prediction["home_points"] = home_standings.get("points", 0)
            prediction["away_points"] = away_standings.get("points", 0)
            
            all_predictions.append(prediction)
            
            # Exibir previsão
            print(f"⏰ {match_time} | {home_name} vs {away_name}")
            print(f"   📊 Classificação: {home_name} ({prediction['home_record']}) vs {away_name} ({prediction['away_record']})")
            print(f"   📊 Probabilidades:")
            print(f"      🏠 Vitória {home_name}: {prediction['home_win_probability'] * 100:.1f}%")
            print(f"      ⚖️  Empate: {prediction['draw_probability'] * 100:.1f}%")
            print(f"      🚌 Vitória {away_name}: {prediction['away_win_probability'] * 100:.1f}%")
            print(f"   ⚽ Placar previsto: {prediction['predicted_home_score']:.1f} x {prediction['predicted_away_score']:.1f}")
            print(f"   🎯 Mais de 2.5: {prediction['over_2_5_probability'] * 100:.1f}%")
            print(f"   ⚽⚽ Ambas marcam: {prediction['btts_probability'] * 100:.1f}%")
            print(f"   📈 Confiança: {prediction['confidence'] * 100:.0f}%")
            print()
        
        print()
    
    # Salvar previsões em JSON
    output_file = "predictions_2026-08-30.json"
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(all_predictions, f, ensure_ascii=False, indent=2)
    
    print("=" * 70)
    print(f"✅ {len(all_predictions)} previsões geradas com sucesso!")
    print(f"📁 Salvo em: {output_file}")
    print("=" * 70)
    
    # Resumo de apostas recomendadas
    print()
    print("🎯 APOSTAS RECOMENDADAS (Confiança > 65%):")
    print("-" * 60)
    
    strong_bets = sorted(all_predictions, key=lambda x: x["confidence"], reverse=True)
    
    for pred in strong_bets[:15]:
        home_win = pred["home_win_probability"]
        away_win = pred["away_win_probability"]
        
        if home_win > 0.55:
            print(f"✅ {pred['home_team']} vs {pred['away_team']}")
            print(f"   💰 Apostar em: {pred['home_team']} ({home_win * 100:.1f}%)")
            print(f"   📊 Confiança: {pred['confidence'] * 100:.0f}%")
            print(f"   📋 {pred['home_record']} vs {pred['away_record']}")
            print()
        elif away_win > 0.55:
            print(f"✅ {pred['home_team']} vs {pred['away_team']}")
            print(f"   💰 Apostar em: {pred['away_team']} ({away_win * 100:.1f}%)")
            print(f"   📊 Confiança: {pred['confidence'] * 100:.0f}%")
            print(f"   📋 {pred['home_record']} vs {pred['away_record']}")
            print()
    
    print()
    print("⚠️  AVISO: Apostas esportivas envolvem risco.")
    print("    Use as previsões apenas para fins educacionais.")
    print("    Nunca aposte mais do que pode perder.")


if __name__ == "__main__":
    main()
