import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.config import settings
from app.database import Base, engine
from app.api import teams_router, players_router, matches_router, predictions_router, odds_router, stats_router

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Valida o schema ao iniciar; migrações são responsabilidade do deploy."""
    if settings.AUTO_CREATE_SCHEMA:
        logger.warning("AUTO_CREATE_SCHEMA ativo; use Alembic em ambientes de produção")
        Base.metadata.create_all(bind=engine)

    # Avisa quando o schema não é gerenciado pelo Alembic (migrações versionadas)
    try:
        with engine.connect() as conn:
            has_version_table = conn.execute(
                text("SELECT 1 FROM alembic_version")
            ).fetchone() is not None
    except Exception:
        has_version_table = False
    if not has_version_table and not settings.AUTO_CREATE_SCHEMA:
        logger.warning(
            "Tabela alembic_version ausente. Execute 'alembic upgrade head' "
            "antes de usar a API."
        )

    logger.info("Verificação do schema concluída.")
    yield


app = FastAPI(
    title="⚽ FBref Scraper API",
    summary="Dados de futebol, previsões e odds em uma API REST",
    version=settings.VERSION,
    debug=settings.DEBUG,
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
| 📈 **Estatísticas** | Consulta e manutenção de estatísticas por partida e time |
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
            "name": "Informações",
            "description": "Status da API e informações de configuração.",
        },
        {
            "name": "Times",
            "description": "🏟️ Cadastro, filtros, scraping e detalhes de times.",
        },
        {
            "name": "Jogadores",
            "description": "👤 Cadastro, filtros e scraping de jogadores.",
        },
        {
            "name": "Partidas",
            "description": "⚽ Cadastro, filtros, scraping e estatísticas de partidas.",
        },
        {
            "name": "Previsões",
            "description": "📊 Previsões de resultados com modelo Poisson baseado em xG.",
        },
        {
            "name": "Estatísticas",
            "description": "📈 Consulta e manutenção das estatísticas por time e partida.",
        },
        {
            "name": "Odds",
            "description": "🎲 Consulta de eventos e mercados de odds da Cloudbet.",
        },
    ],
    swagger_ui_parameters={
        "defaultModelsExpandDepth": 1,
        "docExpansion": "list",
        "filter": True,
        "displayRequestDuration": True,
        "persistAuthorization": True,
        "tryItOutEnabled": True,
    },
)

cors_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]

# Sem origens configuradas, mantém acesso público sem habilitar credenciais.
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins or ["*"],
    allow_credentials=bool(cors_origins),
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
app.include_router(teams_router, prefix=settings.API_V1_PREFIX)
app.include_router(players_router, prefix=settings.API_V1_PREFIX)
app.include_router(matches_router, prefix=settings.API_V1_PREFIX)
app.include_router(predictions_router, prefix=settings.API_V1_PREFIX)
app.include_router(stats_router, prefix=settings.API_V1_PREFIX)
app.include_router(odds_router, prefix=settings.API_V1_PREFIX)


@app.get("/", summary="Informações da API", tags=["Informações"])
def root():
    """Endpoint raiz com informações básicas da API."""
    return {
        "name": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api_prefix": settings.API_V1_PREFIX,
    }


@app.get("/health", summary="Health Check", tags=["Informações"])
def health_check():
    """Verifica se a API está saudável."""
    return {"status": "ok"}
