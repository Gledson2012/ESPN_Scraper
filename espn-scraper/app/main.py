import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import inspect, text
from sqlalchemy.exc import SQLAlchemyError

from app.config import settings
from app.database import Base, engine
from app.api import teams_router, players_router, matches_router, predictions_router, odds_router, stats_router, discovery_router

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

    # Valida conectividade e avisa quando o schema não é gerenciado pelo Alembic.
    database_available = False
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
            database_available = True
            has_version_table = inspect(conn).has_table("alembic_version")
    except SQLAlchemyError as exc:
        logger.error("Não foi possível verificar o banco de dados no startup: %s", exc)
        has_version_table = False
    if database_available and not has_version_table and not settings.AUTO_CREATE_SCHEMA:
        logger.warning(
            "Tabela alembic_version ausente. Execute 'alembic upgrade head' "
            "antes de usar a API."
        )

    logger.info("Verificação do schema concluída.")
    yield


app = FastAPI(
    title="⚽ ESPN Football API",
    summary="Dados de futebol, previsões e odds em uma API REST",
    version=settings.VERSION,
    debug=settings.DEBUG,
    description="""
# ⚽ ESPN Football API

API para **dados de futebol da ESPN**, geração de **previsões de partidas** usando modelo Poisson baseado em xG, e integração com **odds de apostas** da [Cloudbet](https://www.cloudbet.com).

---

## 📋 Funcionalidades

| Módulo | Descrição |
|--------|-----------|
| 🏟️ **Times** | Sincronização ESPN e CRUD de times de ligas específicas |
| 👤 **Jogadores** | Sincronização ESPN e CRUD de jogadores de times |
| ⚽ **Partidas** | Sincronização ESPN e CRUD de partidas com estatísticas |
| 📈 **Estatísticas** | Consulta e manutenção de estatísticas por partida e time |
| 📊 **Previsões** | Modelo Poisson para prever resultados de partidas |
| 🎲 **Odds** | Integração com a API da Cloudbet para odds de apostas |

---

## 🚀 Início Rápido

1. **Scraping de times**: `POST /api/v1/teams/scrape?league=Serie-A` (temporada atual por padrão)
2. **Sincronização de jogadores**: `POST /api/v1/players/scrape?fbref_team_id=86` (ID ESPN; nome do parâmetro mantido por compatibilidade)
3. **Sincronização de partidas**: `POST /api/v1/matches/scrape?league=Serie-A` (temporada atual por padrão)
4. **Gerar previsão**: `POST /api/v1/predictions/`

---

## 🏆 Ligas Suportadas

| Liga | Código ESPN |
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
| Série B (Brasil) | `Serie-B` |
| Copa do Brasil | `Copa-do-Brasil` |
| Liga Argentina | `Liga-Argentina` |
| Sudamericana | `Sudamericana` |
| Copa do Mundo | `World-Cup` |
| Championship | `Championship` |
| Europa League | `Europa-League` |
| Conference League | `Conference-League` |
| Copa del Rey | `Copa-del-Rey` |
| Coppa Italia | `Coppa-Italia` |
| DFB-Pokal | `DFB-Pokal` |

---

## ⚠️ Aviso

Este projeto é para fins educacionais. Respeite os termos de serviço da ESPN e use o `REQUEST_DELAY` para evitar sobrecarregar o serviço.
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
app.include_router(discovery_router, prefix=settings.API_V1_PREFIX)


@app.get(
    settings.API_V1_PREFIX,
    summary="Endpoints disponíveis",
    tags=["Informações"],
)
def api_v1_root():
    """Lista todos os módulos disponíveis na API v1."""
    return {
        "version": settings.VERSION,
        "modules": {
            "teams": f"{settings.API_V1_PREFIX}/teams",
            "players": f"{settings.API_V1_PREFIX}/players",
            "matches": f"{settings.API_V1_PREFIX}/matches",
            "stats": f"{settings.API_V1_PREFIX}/stats",
            "predictions": f"{settings.API_V1_PREFIX}/predictions",
            "odds": f"{settings.API_V1_PREFIX}/odds",
            "overview": f"{settings.API_V1_PREFIX}/overview",
            "sync_status": f"{settings.API_V1_PREFIX}/sync/status",
            "catalog": f"{settings.API_V1_PREFIX}/catalog",
            "search": f"{settings.API_V1_PREFIX}/search",
        },
        "docs": "/docs",
    }


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
    """Verifica a API e a conectividade com o banco de dados."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except SQLAlchemyError as exc:
        logger.error("Health check falhou ao consultar o banco: %s", exc)
        raise HTTPException(status_code=503, detail="Banco de dados indisponível")

    return {"status": "ok", "database": "ok"}
