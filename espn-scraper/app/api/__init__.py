from app.api.teams import router as teams_router
from app.api.players import router as players_router
from app.api.matches import router as matches_router
from app.api.predictions import router as predictions_router
from app.api.odds import router as odds_router
from app.api.stats import router as stats_router

__all__ = ["teams_router", "players_router", "matches_router", "predictions_router", "odds_router", "stats_router"]
