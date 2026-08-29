# ESPN Football API

API para sincronização de dados de futebol da ESPN, geração de previsões de partidas e integração com odds de apostas da [Cloudbet](https://www.cloudbet.com).

## 📋 Funcionalidades

- **Times ESPN**: Busca times de ligas específicas
- **Jogadores ESPN**: Busca os elencos atuais dos times
- **Partidas ESPN**: Busca partidas de ligas e temporadas
- **Estatísticas ESPN**: Busca estatísticas detalhadas de partidas
- **Previsões**: Gera previsões de partidas usando modelo Poisson baseado em xG
- **Odds Cloudbet**: Integração com a API da Cloudbet para odds de apostas de futebol

## 🚀 Instalação

### Com Docker (recomendado)

```bash
# Configure credenciais locais (substitua os valores do arquivo)
cp .env.example .env
# Defina POSTGRES_PASSWORD e API_KEY no arquivo .env

# Subir os serviços (API + PostgreSQL)
docker-compose up -d

# A API estará disponível em http://localhost:8000
# Documentação interativa em http://localhost:8000/docs

# Sincronizar times, partidas e elencos reais da ESPN
docker compose exec api python scripts/sync_real_matches.py --league Serie-A --include-players
```

Sem `--season`, a API calcula a temporada vigente por competição: `2026`
para Brasileirão, Libertadores e MLS; `2026-2027` para as competições
europeias no segundo semestre de 2026. Use `--season` para sincronizar uma
temporada histórica. O parâmetro `--include-players` reconcilia o elenco atual
sem apagar registros históricos de jogadores.

### Localmente

```bash
# Criar ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# Instalar dependências
pip install -r requirements.txt

# Configurar banco de dados PostgreSQL
# Crie um banco chamado 'fbref_scraper' e ajuste a URL em app/config.py ou via variável de ambiente
export API_KEY="uma-chave-forte"

# Aplicar o schema versionado
alembic upgrade head

# Iniciar a API
uvicorn app.main:app --reload
```

## 📚 Endpoints da API

### Times (`/api/v1/teams`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/teams/` | Lista times (com filtros) |
| GET | `/api/v1/teams/{id}` | Obtém um time |
| GET | `/api/v1/teams/{id}/players` | Lista jogadores do time |
| GET | `/api/v1/teams/{id}/matches` | Lista partidas do time |
| GET | `/api/v1/teams/{id}/summary` | Resumo de desempenho do time |
| POST | `/api/v1/teams/` | Cria um time |
| PUT | `/api/v1/teams/{id}` | Atualiza um time |
| DELETE | `/api/v1/teams/{id}` | Deleta um time |
| POST | `/api/v1/teams/scrape?league=Serie-A` | Scraping de times na temporada atual |

### Jogadores (`/api/v1/players`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/players/` | Lista jogadores (com filtros) |
| GET | `/api/v1/players/{id}` | Obtém um jogador |
| POST | `/api/v1/players/` | Cria um jogador |
| PUT | `/api/v1/players/{id}` | Atualiza um jogador |
| DELETE | `/api/v1/players/{id}` | Deleta um jogador |
| POST | `/api/v1/players/scrape?fbref_team_id=xxx` | Scraping de jogadores |

### Partidas (`/api/v1/matches`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/matches/` | Lista partidas (com filtros) |
| GET | `/api/v1/matches/live?league=Serie-A` | Jogos ao vivo em tempo real (ESPN) |
| GET | `/api/v1/matches/{id}` | Obtém uma partida |
| POST | `/api/v1/matches/` | Cria uma partida |
| PUT | `/api/v1/matches/{id}` | Atualiza uma partida |
| DELETE | `/api/v1/matches/{id}` | Deleta uma partida |
| POST | `/api/v1/matches/scrape?league=Serie-A` | Scraping de partidas na temporada atual |
| POST | `/api/v1/matches/{id}/scrape-stats` | Scraping de estatísticas |
| GET | `/api/v1/matches/{id}/stats` | Lista estatísticas da partida |

### Estatísticas (`/api/v1/stats`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/stats/` | Lista estatísticas com filtros por partida/time |
| GET | `/api/v1/stats/{id}` | Obtém estatísticas pelo ID |
| POST | `/api/v1/stats/` | Cria estatísticas para um time da partida |
| PUT | `/api/v1/stats/{id}` | Atualiza estatísticas |
| DELETE | `/api/v1/stats/{id}` | Exclui estatísticas |

### Odds Cloudbet (`/api/v1/odds`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/odds/sports` | Lista esportes disponíveis |
| GET | `/api/v1/odds/competitions` | Lista competições de futebol |
| GET | `/api/v1/odds/soccer` | Odds de partidas de futebol (filtro por competição) |
| GET | `/api/v1/odds/match?home_team=X&away_team=Y` | Odds de uma partida específica |
| GET | `/api/v1/odds/event/{event_id}` | Odds de um evento pelo ID |
| GET | `/api/v1/odds/event/{event_id}/markets` | Mercados de apostas de um evento |

**Exemplo de resposta (`/odds/soccer`):**
```json
{
  "events": [
    {
      "event_id": "abc123",
      "event_name": "Flamengo vs Palmeiras",
      "start_time": "2026-04-10T20:00:00Z",
      "competition": {"id": "br-serie-a", "name": "Brasileirão Série A"},
      "markets": [
        {
          "id": "mkt_1x2",
          "name": "Resultado 1X2",
          "selections": [
            {"id": "sel_1", "name": "Flamengo", "price": 2.10},
            {"id": "sel_x", "name": "Empate", "price": 3.25},
            {"id": "sel_2", "name": "Palmeiras", "price": 3.40}
          ]
        }
      ]
    }
  ],
  "total": 1
}
```

### Previsões (`/api/v1/predictions`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| POST | `/api/v1/predictions/` | Gera previsão para uma partida |

**Exemplo de requisição:**
```json
{
  "home_team_id": 1,
  "away_team_id": 2
}
```

**Exemplo de resposta:**
```json
{
  "home_team_id": 1,
  "away_team_id": 2,
  "home_win_probability": 0.4521,
  "draw_probability": 0.2712,
  "away_win_probability": 0.2767,
  "predicted_home_score": 1.45,
  "predicted_away_score": 1.12,
  "over_2_5_probability": 0.5234,
  "btts_probability": 0.6123,
  "confidence": 0.75,
  "model_version": "1.1.0"
}
```

## 🏗️ Estrutura do Projeto

```
espn-scraper/
├── alembic/                 # Migrações de banco de dados (Alembic)
│   ├── env.py
│   └── versions/
├── alembic.ini              # Configuração do Alembic
├── app/
│   ├── main.py              # Ponto de entrada da API
│   ├── config.py            # Configurações da aplicação
│   ├── database.py          # Configuração do banco de dados
│   ├── models/              # Modelos SQLAlchemy
│   │   ├── team.py
│   │   ├── player.py
│   │   ├── match.py
│   │   └── match_stats.py
│   ├── schemas/             # Schemas Pydantic
│   │   ├── team.py
│   │   ├── player.py
│   │   ├── match.py
│   │   ├── match_stats.py
│   │   ├── prediction.py
│   │   └── odds.py
│   ├── services/
│   │   ├── fbref.py         # Serviço legado que orquestra ESPN e banco
│   │   └── cloudbet.py      # Serviço de integração com API Cloudbet
│   ├── scrapers/            # Clientes da ESPN
│   │   ├── espn.py          # Cliente e scrapers ESPN
│   │   ├── teams.py
│   │   ├── players.py
│   │   ├── matches.py
│   │   └── statistics.py
│   └── api/                 # Rotas da API
│       ├── security.py      # API key + rate limiting dos endpoints de scraping
│       ├── teams.py
│       ├── players.py
│       ├── matches.py
│       ├── predictions.py
│       └── odds.py
├── tests/                   # Testes automatizados
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

## 🧪 Testes

```bash
# Executar todos os testes
pytest

# Executar testes com cobertura (instale pytest-cov se necessário)
pip install pytest-cov
pytest --cov=app --cov-report=html
```

## 🔧 Configuração

As configurações podem ser definidas via variáveis de ambiente ou arquivo `.env`:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL do banco de dados | `postgresql://postgres:postgres@localhost:5432/fbref_scraper` |
| `API_V1_PREFIX` | Prefixo da API | `/api/v1` |
| `PROJECT_NAME` | Nome do projeto | `ESPN Football API` |
| `DEBUG` | Modo debug | `false` |
| `CORS_ORIGINS` | Origens permitidas separadas por vírgula | vazio |
| `AUTO_CREATE_SCHEMA` | Cria tabelas sem Alembic (somente desenvolvimento) | `false` |
| `REQUEST_TIMEOUT` | Timeout das requisições (s) | `30` |
| `REQUEST_DELAY` | Delay entre requisições (s) | `1.0` |
| `USER_AGENT` | User-Agent para scraping | Chrome UA |
| `CLOUDBET_API_KEY` | Chave de API da Cloudbet | vazio |
| `CLOUDBET_BASE_URL` | URL base da API Cloudbet | `https://sports-api.cloudbet.com/v2` |
| `API_KEY` | Chave para scraping e operações de escrita | vazio |
| `ALLOW_UNAUTHENTICATED_SCRAPING` | Libera scraping sem chave (somente desenvolvimento) | `false` |
| `ALLOW_UNAUTHENTICATED_WRITES` | Libera escrita sem chave (somente desenvolvimento) | `false` |
| `SCRAPE_RATE_LIMIT` | Máx. requisições de scraping por IP por janela | `30` |
| `SCRAPE_RATE_WINDOW` | Janela do rate limit (s) | `60` |
| `API_RATE_LIMIT` | Máx. requisições públicas por IP por janela | `120` |
| `API_RATE_WINDOW` | Janela do rate limit público (s) | `60` |
| `REDIS_URL` | URL do Redis para rate limit distribuído (vazio = em memória) | vazio |
| `CLOUDBET_MAX_COMPETITIONS` | Máximo de competições consultadas sem filtro | `20` |
| `CACHE_ENABLED` | Habilita o cache em disco dos scrapers | `true` |
| `CACHE_TTL_SECONDS` | TTL do cache em disco dos scrapers (s) | `3600` |
| `CACHE_DIR` | Diretório do cache em disco (vazio = temp do sistema) | vazio |

## 🔒 Segurança da API

Os endpoints de scraping e todas as operações de escrita do CRUD possuem:

- **Autenticação via API key** — configure `API_KEY` e envie o header `X-API-Key: <sua-chave>`; sem a configuração, as operações protegidas respondem `503`.
- O bypass de scraping e de escrita são independentes e devem ser explicitados somente em desenvolvimento, respectivamente com `ALLOW_UNAUTHENTICATED_SCRAPING=true` e `ALLOW_UNAUTHENTICATED_WRITES=true`.
- **Rate limiting por IP** — limite de `SCRAPE_RATE_LIMIT` requisições por janela de `SCRAPE_RATE_WINDOW` segundos (padrão: 30/min). Acima do limite, responde `429`.
- Os endpoints públicos de odds também possuem o limitador de `API_RATE_LIMIT`/`API_RATE_WINDOW`.

> Por padrão o rate limit é **em memória** (por processo). Configure `REDIS_URL` (ou use o `docker-compose`, que já sobe o Redis) para um rate limit **distribuído** entre workers. Se o Redis falhar, cada processo usa um fallback local limitado.

O endpoint `/health` também valida a conectividade com o banco e retorna `503` quando o banco está indisponível.

## 🗄️ Migrações de Banco de Dados (Alembic)

O schema é versionado com [Alembic](https://alembic.sqlalchemy.org/):

```bash
# Aplicar migrações (cria as tabelas)
poetry run alembic upgrade head

# Gerar uma nova migração a partir dos modelos
poetry run alembic revision --autogenerate -m "descrição da mudança"
```

> Em bancos novos, execute `alembic upgrade head` antes de iniciar a API. A inicialização ainda executa `create_all` como rede de segurança (não altera tabelas existentes).

```bash
 curl -X POST "http://localhost:8000/api/v1/teams/scrape?league=Serie-A" \
  -H "X-API-Key: sua-chave"
```

## 🏆 Ligas Suportadas

O scraper suporta as seguintes ligas (mapeadas automaticamente para os códigos da ESPN):

| Liga | Código ESPN |
|------|-------------|
| Serie-A (Brasil) | `bra.1` |
| Premier-League | `eng.1` |
| Serie-A-Italy | `ita.1` |
| La-Liga | `esp.1` |
| Bundesliga | `ger.1` |
| Ligue-1 | `fra.1` |
| Eredivisie | `ned.1` |
| Primeira-Liga | `por.1` |
| MLS | `usa.1` |
| Liga-MX | `mex.1` |
| Libertadores | `conmebol.libertadores` |
| Champions-League | `uefa.champions` |
| Serie-B (Brasil) | `bra.2` |
| Copa-do-Brasil | `bra.copa_do_brazil` |
| Liga-Argentina | `arg.1` |
| Sudamericana | `conmebol.sudamericana` |
| World-Cup | `fifa.world` |
| Championship | `eng.2` |
| Europa-League | `uefa.europa` |
| Conference-League | `uefa.europa.conf` |
| Copa-del-Rey | `esp.copa_del_rey` |
| Coppa-Italia | `ita.coppa_italia` |
| DFB-Pokal | `ger.dfb_pokal` |

## ⚠️ Aviso Legal

Este projeto é para fins educacionais. Respeite os termos de uso da ESPN e use o `REQUEST_DELAY` para evitar sobrecarregar o serviço.

> A coleta atual usa os endpoints JSON públicos da ESPN. O campo de banco `fbref_id` é mantido apenas por compatibilidade e armazena o ID externo da ESPN.

## 📄 Licença

MIT
