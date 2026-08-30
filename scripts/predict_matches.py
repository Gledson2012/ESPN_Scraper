#!/usr/bin/env python3
"""
Gerador de previsões de apostas esportivas baseado em dados da ESPN.
Usa o Modelo de Poisson para calcular probabilidades de resultados.

Uso: python scripts/predict_matches.py [--date YYYY-MM-DD] [--league SLUG]
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

# ─── Funções Utilitárias ───────────────────────────────────────

def fetch_json(url: str) -> dict:
    """Busca JSON de uma URL."""
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.load(resp)
    except Exception as e:
        return {}


def get_team_stats(team_id: str, league_slug: str) -> dict:
    """Busca estatísticas do time na temporada atual."""
    url = f"{ESPN_API_BASE}/{league_slug}/teams/{team_id}/statistics"
    data = fetch_json(url)
    
    stats = {
        "goals_for": 0,
        "goals_against": 0,
        "matches_played": 0,
        "wins": 0,
        "draws": 0,
        "losses": 0,
        "home_goals": 0,
        "home_matches": 0,
        "away_goals": 0,
        "away_matches": 0,
    }
    
    # Tentar extrair do scoreboard
    scoreboard_url = f"{ESPN_API_BASE}/{league_slug}/scoreboard"
    scoreboard = fetch_json(scoreboard_url)
    
    for event in scoreboard.get("events", []):
        comps = event.get("competitions", [{}])[0]
        competitors = comps.get("competitors", [])
        
        home = next((c for c in competitors if c.get("homeAway") == "home"), {})
        away = next((c for c in competitors if c.get("homeAway") == "away"), {})
        
        home_team = home.get("team", {})
        away_team = away.get("team", {})
        
        if home_team.get("id") == team_id:
            stats["matches_played"] += 1
            stats["home_matches"] += 1
            h_score = int(home.get("score", 0) or 0)
            a_score = int(away.get("score", 0) or 0)
            stats["goals_for"] += h_score
            stats["goals_against"] += a_score
            stats["home_goals"] += h_score
            if h_score > a_score:
                stats["wins"] += 1
            elif h_score == a_score:
                stats["draws"] += 1
            else:
                stats["losses"] += 1
        
        if away_team.get("id") == team_id:
            stats["matches_played"] += 1
            stats["away_matches"] += 1
            h_score = int(home.get("score", 0) or 0)
            a_score = int(away.get("score", 0) or 0)
            stats["goals_for"] += a_score
            stats["goals_against"] += h_score
            stats["away_goals"] += a_score
            if a_score > h_score:
                stats["wins"] += 1
            elif h_score == a_score:
                stats["draws"] += 1
            else:
                stats["losses"] += 1
    
    return stats


# ─── Modelo de Poisson ─────────────────────────────────────────

def poisson_probability(lam: float, k: int) -> float:
    """Calcula P(X = k) para distribuição de Poisson."""
    return (lam ** k) * math.exp(-lam) / math.factorial(k)


def calculate_match_probabilities(
    home_avg_goals: float,
    away_avg_goals: float,
    max_goals: int = 8
) -> dict:
    """
    Calcula probabilidades usando o Modelo de Poisson.
    
    home_avg_goals: Média de gols do mandante por partida
    away_avg_goals: Média de gols do visitante por partida
    """
    # Matriz de probabilidades de placar exato
    score_matrix = {}
    for i in range(max_goals + 1):
        for j in range(max_goals + 1):
            prob = poisson_probability(home_avg_goals, i) * poisson_probability(away_avg_goals, j)
            score_matrix[(i, j)] = prob
    
    # Probabilidades de resultado
    home_win = sum(prob for (h, a), prob in score_matrix.items() if h > a)
    draw = sum(prob for (h, a), prob in score_matrix.items() if h == a)
    away_win = sum(prob for (h, a), prob in score_matrix.items() if h < a)
    
    # Mais de 2.5 gols
    over_2_5 = sum(prob for (h, a), prob in score_matrix.items() if h + a > 2.5)
    
    # Ambas marcam (BTTS)
    btts = sum(prob for (h, a), prob in score_matrix.items() if h > 0 and a > 0)
    
    # Gols esperados
    expected_home = home_avg_goals
    expected_away = away_avg_goals
    
    # Placar mais provável
    most_likely_score = max(score_matrix.items(), key=lambda x: x[1])[0]
    
    return {
        "home_win_probability": round(home_win, 4),
        "draw_probability": round(draw, 4),
        "away_win_probability": round(away_win, 4),
        "predicted_home_score": round(expected_home, 2),
        "predicted_away_score": round(expected_away, 2),
        "over_2_5_probability": round(over_2_5, 4),
        "btts_probability": round(btts, 4),
        "most_likely_score": f"{most_likely_score[0]}x{most_likely_score[1]}",
    }


# ─── Geração de Previsões ─────────────────────────────────────

def generate_prediction(
    home_name: str,
    away_name: str,
    home_stats: dict,
    away_stats: dict,
    league_name: str
) -> dict:
    """Gera uma previsão para uma partida."""
    
    # Calcular médias de gols (com fallback para dados insuficientes)
    home_matches = home_stats.get("matches_played", 0)
    away_matches = away_stats.get("matches_played", 0)
    
    if home_matches > 0:
        home_attack = home_stats["goals_for"] / home_matches
        home_defense = home_stats["goals_against"] / home_matches
    else:
        home_attack = 1.3  # Média da Série A
        home_defense = 1.1
    
    if away_matches > 0:
        away_attack = away_stats["goals_for"] / away_matches
        away_defense = away_stats["goals_against"] / away_matches
    else:
        away_attack = 1.1  # Média visitante
        away_defense = 1.3
    
    # Média de gols esperados (ajuste por mando de campo)
    home_avg_goals = (home_attack + away_defense) / 2 * 1.15  # Bônus mandante
    away_avg_goals = (away_attack + home_defense) / 2 * 0.85  # Desvantagem visitante
    
    # Calcular probabilidades
    probs = calculate_match_probabilities(home_avg_goals, away_avg_goals)
    
    # Calcular confiança baseada nos dados disponíveis
    confidence = min(0.95, 0.5 + (home_matches + away_matches) * 0.02)
    
    return {
        "home_team": home_name,
        "away_team": away_name,
        "league": league_name,
        **probs,
        "confidence": round(confidence, 2),
        "home_stats": {
            "matches": home_matches,
            "wins": home_stats.get("wins", 0),
            "draws": home_stats.get("draws", 0),
            "losses": home_stats.get("losses", 0),
            "goals_for": home_stats.get("goals_for", 0),
            "goals_against": home_stats.get("goals_against", 0),
        },
        "away_stats": {
            "matches": away_matches,
            "wins": away_stats.get("wins", 0),
            "draws": away_stats.get("draws", 0),
            "losses": away_stats.get("losses", 0),
            "goals_for": away_stats.get("goals_for", 0),
            "goals_against": away_stats.get("goals_against", 0),
        },
    }


# ─── Função Principal ──────────────────────────────────────────

def main():
    date = "20260830"
    leagues_to_check = list(LEAGUES.keys())
    
    print("=" * 70)
    print("⚽ GERADOR DE PREVISÕES DE APOSTAS ESPORTIVAS")
    print(f"📅 Data: 30/08/2026")
    print("=" * 70)
    print()
    
    all_predictions = []
    
    for league_slug in leagues_to_check:
        league_name = LEAGUES[league_slug]
        url = f"{ESPN_API_BASE}/{league_slug}/scoreboard?dates={date}"
        data = fetch_json(url)
        
        if not data.get("events"):
            continue
        
        print(f"🏆 {league_name}")
        print("-" * 50)
        
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
            
            # Buscar estatísticas dos times
            home_stats = get_team_stats(home_id, league_slug)
            away_stats = get_team_stats(away_id, league_slug)
            
            # Gerar previsão
            prediction = generate_prediction(
                home_name, away_name,
                home_stats, away_stats,
                league_name
            )
            prediction["time"] = match_time
            all_predictions.append(prediction)
            
            # Exibir previsão
            print(f"⏰ {match_time} | {home_name} vs {away_name}")
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
    print("🎯 APOSTAS RECOMENDADAS (Confiança > 70%):")
    print("-" * 50)
    
    strong_bets = [p for p in all_predictions if p["confidence"] >= 0.7]
    
    for pred in strong_bets[:10]:  # Top 10
        home_win = pred["home_win_probability"]
        away_win = pred["away_win_probability"]
        
        if home_win > 0.55:
            print(f"✅ {pred['home_team']} vs {pred['away_team']}")
            print(f"   💰 Apostar em: {pred['home_team']} ({home_win * 100:.1f}%)")
            print(f"   📊 Confiança: {pred['confidence'] * 100:.0f}%")
            print()
        elif away_win > 0.55:
            print(f"✅ {pred['home_team']} vs {pred['away_team']}")
            print(f"   💰 Apostar em: {pred['away_team']} ({away_win * 100:.1f}%)")
            print(f"   📊 Confiança: {pred['confidence'] * 100:.0f}%")
            print()
    
    print()
    print("⚠️  AVISO: Apostas esportivas envolvem risco.")
    print("    Use as previsões apenas para fins educacionais.")


if __name__ == "__main__":
    main()
