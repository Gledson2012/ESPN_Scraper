import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.database import Base, engine
from app.api import teams_router, players_router, matches_router, predictions_router, odds_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Cria as tabelas no banco de dados ao iniciar."""
    logger.info("Criando tabelas no banco de dados...")
    Base.metadata.create_all(bind=engine)
    logger.info("Tabelas criadas com sucesso.")
    yield


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="""
# ⚽ FBref Scraper API

API para **scraping de dados de futebol** do [FBref](https://fbref.com), geração de **previsões de partidas** usando modelo Poisson baseado em xG, e integração com **odds de apostas** da [Cloudbet](https://www.cloudbet.com).

---

## 📋 Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| 🏟️ **Times** | Scraping e CRUD de times de ligas específicas |
| 👤 **Jogadores** | Scraping e CRUD de jogadores de times |
| ⚽ **Partidas** | Scraping e CRUD de partidas com estatísticas |
| 📊 **Previsões** | Modelo Poisson para prever resultados de partidas |
| 🎲 **Odds** | Integração com a API da Cloudbet para odds de apostas |

---

## 🚀 Início Rápido

1. **Scraping de times**: `POST /api/v1/teams/scrape?league=Serie-A&season=2024-2025`
2. **Scraping de jogadores**: `POST /api/v1/players/scrape?fbref_team_id=xxx`
3. **Scraping de partidas**: `POST /api/v1/matches/scrape?league=Serie-A&season=2024-2025`
4. **Gerar previsão**: `POST /api/v1/predictions/`

---

## 🏆 Ligas Suportadas

| Liga | Código FBref |
|------|-------------|
| Brasileirão Série A | `Serie-A` |
| Premier League | `Premier-League` |
| La Liga | `La-Liga` |
| Bundesliga | `Bundesliga` |
| Serie A (Itália) | `Serie-A-Italy` |
| Ligue 1 | `Ligue-1` |
| Eredivisie | `Eredivisie` |
| Primeira Liga | `Primeira-Liga` |
| MLS | `MLS` |
| Liga MX | `Liga-MX` |
| Libertadores | `Libertadores` |
| Champions League | `Champions-League` |

---

## ⚠️ Aviso

Este projeto é para fins educacionais. Respeite os termos de serviço do FBref e use o `REQUEST_DELAY` para evitar sobrecarregar o servidor.
""",
    lifespan=lifespan,
    contact={
        "name": "Gledson Crist",
        "email": "Gledsoncrist@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    openapi_tags=[
        {
            "name": "teams",
            "description": "🏟️ **Times** - Operações de scraping e CRUD de times de futebol",
        },
        {
            "name": "players",
            "description": "👤 **Jogadores** - Operações de scraping e CRUD de jogadores",
        },
        {
            "name": "matches",
            "description": "⚽ **Partidas** - Operações de scraping e CRUD de partidas com estatísticas",
        },
        {
            "name": "predictions",
            "description": "📊 **Previsões** - Modelo Poisson para prever resultados de partidas",
        },
        {
            "name": "odds",
            "description": "🎲 **Odds Cloudbet** - Integração com a API da Cloudbet para odds de apostas",
        },
    ],
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(teams_router, prefix=settings.API_V1_PREFIX)
app.include_router(players_router, prefix=settings.API_V1_PREFIX)
app.include_router(matches_router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions_router, prefix=settings.API_V1_PREFIX)
app.include_router(odds_router, prefix=settings.API_V1_PREFIX)


@app.get("/", summary="Informações da API", tags=["info"])
def root():
    """Endpoint raiz com informações básicas da API."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
    }


@app.get("/health", summary="Health Check", tags=["info"])
def health_check():
    """Verifica se a API está saudável."""
    return {"status": "ok"}