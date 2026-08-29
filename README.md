<div align="center">

# ⚽ ESPN Football API

**API de dados de futebol da ESPN, previsões de partidas com modelo Poisson e integração com odds da Cloudbet**

![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)
![CI/CD](https://github.com/Gledson2012/FBref-Scraper/actions/workflows/ci.yml/badge.svg)

[🚀 Início Rápido](#-início-rápido) • [📚 Endpoints](#-endpoints) • [🏆 Ligas Suportadas](#-ligas-suportadas) • [🛠️ Tecnologias](#️-tecnologias) • [📖 Documentação](#-documentação)

</div>

---

## 📋 Sobre o Projeto

Esta API coleta dados de futebol da **ESPN**, gera **previsões de partidas** usando um modelo estatístico baseado na distribuição de Poisson e xG (gols esperados), e se integra com a **[Cloudbet](https://www.cloudbet.com)** para odds de apostas em tempo real.

### ✨ Funcionalidades

- 🏟️ **Dados ESPN de Times** - Busca times de ligas específicas
- 👤 **Dados ESPN de Jogadores** - Busca elencos atuais
- ⚽ **Dados ESPN de Partidas** - Busca partidas com resultados e estatísticas
- 📊 **Previsões Inteligentes** - Modelo Poisson baseado em xG com análise de mando de campo
- 🎲 **Odds Cloudbet** - Integração em tempo real com a API da Cloudbet
- 🖥️ **Painel React** - Dashboard responsivo para partidas, times, previsões e odds
- 📚 **Documentação Interativa** - Swagger UI completo com exemplos
- 🐳 **Docker Ready** - Deploy facilitado com Docker Compose

---

## 🚀 Início Rápido

### Pré-requisitos

- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/)
- [Node.js](https://nodejs.org/) 18+ para o painel React
- Ou Python 3.10+ e PostgreSQL

### 🐳 Com Docker (recomendado)

```bash
# Clone o repositório
git clone https://github.com/Gledson2012/FBref-Scraper.git
cd FBref-Scraper/fbref-scraper

# Configure credenciais locais (substitua os valores do arquivo)
cp .env.example .env
# Defina POSTGRES_PASSWORD e API_KEY no arquivo .env

# Suba os serviços (API + PostgreSQL)
docker-compose up -d

# Acesse a documentação
open http://localhost:8000/docs

# Sincronize times, partidas e elencos reais da ESPN
docker compose exec api python scripts/sync_real_matches.py --league Serie-A --include-players
```

### 🖥️ Painel React

Com a API em execução, abra outro terminal:

```bash
cd FBref-Scraper/frontend
npm install
cp .env.example .env
npm run dev
```

O painel estará disponível em `http://localhost:5173`. Ele consome a API em
`http://localhost:8000/api/v1` por padrão; ajuste `VITE_API_URL` no `.env` se
necessário.

### 🐍 Localmente

```bash
# Clone o repositório
git clone https://github.com/Gledson2012/FBref-Scraper.git
cd FBref-Scraper/fbref-scraper

# Crie um ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac

# Instale as dependências
pip install -r requirements.txt

# Configure o PostgreSQL (crie o banco 'fbref_scraper')
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/fbref_scraper"
export API_KEY="uma-chave-forte"

# Aplique o schema versionado
alembic upgrade head

# Inicie a API
uvicorn app.main:app --reload
```

---

## 🔄 Fluxo de Uso

### 1️⃣ Scraping de Times

```bash
curl -X POST "http://localhost:8000/api/v1/teams/scrape?league=Serie-A" \
  -H "X-API-Key: uma-chave-forte"
```

### 2️⃣ Scraping de Jogadores

```bash
curl -X POST "http://localhost:8000/api/v1/players/scrape?fbref_team_id=flamengo" \
  -H "X-API-Key: uma-chave-forte"
```

### 3️⃣ Scraping de Partidas

```bash
curl -X POST "http://localhost:8000/api/v1/matches/scrape?league=Serie-A" \
  -H "X-API-Key: uma-chave-forte"
```

### 4️⃣ Gerar Previsão

```bash
curl -X POST "http://localhost:8000/api/v1/predictions/" \
  -H "Content-Type: application/json" \
  -d '{
    "home_team_id": 1,
    "away_team_id": 2
  }'
```

**Resposta:**
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

---

## 📚 Endpoints

### 🏟️ Times (`/api/v1/teams`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/teams/` | Lista times (com filtros) |
| `GET` | `/teams/{id}` | Obtém um time pelo ID |
| `GET` | `/teams/{id}/players` | Lista jogadores do time |
| `GET` | `/teams/{id}/matches` | Lista partidas do time |
| `GET` | `/teams/{id}/summary` | Resumo de desempenho do time |
| `POST` | `/teams/` | Cria um time |
| `PUT` | `/teams/{id}` | Atualiza um time |
| `DELETE` | `/teams/{id}` | Deleta um time |
| `POST` | `/teams/scrape` | Sincronização de times da ESPN |

### 👤 Jogadores (`/api/v1/players`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/players/` | Lista jogadores (com filtros) |
| `GET` | `/players/{id}` | Obtém um jogador pelo ID |
| `POST` | `/players/` | Cria um jogador |
| `PUT` | `/players/{id}` | Atualiza um jogador |
| `DELETE` | `/players/{id}` | Deleta um jogador |
| `POST` | `/players/scrape` | Sincronização de jogadores da ESPN |

### ⚽ Partidas (`/api/v1/matches`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/matches/` | Lista partidas (com filtros) |
| `GET` | `/matches/{id}` | Obtém uma partida pelo ID |
| `POST` | `/matches/` | Cria uma partida |
| `PUT` | `/matches/{id}` | Atualiza uma partida |
| `DELETE` | `/matches/{id}` | Deleta uma partida |
| `POST` | `/matches/scrape` | Sincronização de partidas da ESPN |
| `POST` | `/matches/{id}/scrape-stats` | Scraping de estatísticas da partida |
| `GET` | `/matches/{id}/stats` | Lista estatísticas da partida |

### 📈 Estatísticas (`/api/v1/stats`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/stats/` | Lista estatísticas com filtros por partida/time |
| `GET` | `/stats/{id}` | Obtém estatísticas pelo ID |
| `POST` | `/stats/` | Cria estatísticas para um time da partida |
| `PUT` | `/stats/{id}` | Atualiza estatísticas |
| `DELETE` | `/stats/{id}` | Exclui estatísticas |

### 📊 Previsões (`/api/v1/predictions`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `POST` | `/predictions/` | Gera previsão para uma partida |

### 🎲 Odds Cloudbet (`/api/v1/odds`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/odds/sports` | Lista esportes disponíveis |
| `GET` | `/odds/competitions` | Lista competições de futebol |
| `GET` | `/odds/soccer` | Odds de partidas de futebol |
| `GET` | `/odds/match` | Odds de uma partida específica |
| `GET` | `/odds/event/{event_id}` | Odds de um evento pelo ID |
| `GET` | `/odds/event/{event_id}/markets` | Mercados de apostas |

---

## 🏆 Ligas Suportadas

| Liga | Código API ESPN |
|------|----------------|
| 🇧🇷 Brasileirão Série A | `bra.1` |
| 🏴 Premier League | `eng.1` |
| 🇮🇹 Serie A (Itália) | `ita.1` |
| 🇪🇸 La Liga | `esp.1` |
| 🇩🇪 Bundesliga | `ger.1` |
| 🇫🇷 Ligue 1 | `fra.1` |
| 🇳🇱 Eredivisie | `ned.1` |
| 🇵🇹 Primeira Liga | `por.1` |
| 🇺🇸 MLS | `usa.1` |
| 🇲🇽 Liga MX | `mex.1` |
| 🌎 Libertadores | `conmebol.libertadores` |
| 🌍 Champions League | `uefa.champions` |

> O **Código API** é o valor usado na query string dos endpoints de sincronização. Os dados são obtidos pelos endpoints JSON públicos da ESPN. Se `season` for omitida, a API calcula a temporada vigente: ano civil para Brasileirão/Libertadores/MLS e `AAAA-AAAA` para as demais competições.

---

## 🏗️ Tecnologias

| Tecnologia | Uso |
|------------|-----|
| [FastAPI](https://fastapi.tiangolo.com/) | Framework web de alta performance |
| [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | ORM para banco de dados |
| [PostgreSQL](https://www.postgresql.org/) | Banco de dados relacional |
| [Requests](https://requests.readthedocs.io/) | Cliente HTTP para a API ESPN |
| [Pydantic](https://docs.pydantic.dev/) | Validação de dados |
| [Docker](https://www.docker.com/) | Containerização |
| [Poetry](https://python-poetry.org/) | Gerenciamento de dependências |
| [React + Vite](https://vitejs.dev/) | Painel web responsivo |

---

## 📁 Estrutura do Projeto

```
FBref-Scraper/
├── fbref-scraper/           # API principal
│   ├── app/
│   │   ├── api/             # Rotas da API
│   │   │   ├── teams.py     # Endpoints de times
│   │   │   ├── players.py   # Endpoints de jogadores
│   │   │   ├── matches.py   # Endpoints de partidas
│   │   │   ├── predictions.py # Endpoints de previsões
│   │   │   └── odds.py      # Endpoints de odds
│   │   ├── models/          # Modelos SQLAlchemy
│   │   ├── schemas/         # Schemas Pydantic
│   │   ├── scrapers/        # Clientes da ESPN
│   │   ├── services/        # Serviços de negócio
│   │   ├── main.py          # Ponto de entrada
│   │   ├── config.py        # Configurações
│   │   └── database.py      # Conexão com banco
│   ├── tests/               # Testes automatizados
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
├── frontend/                 # Painel React/Vite
│   ├── src/components/       # Navegação e componentes reutilizáveis
│   ├── src/pages/            # Dashboard, partidas, times, previsões e odds
│   ├── src/lib/              # Cliente HTTP e formatadores
│   └── README.md
├── pyproject.toml           # Configuração Poetry (empacota o módulo `app`)
└── README.md
```

---

## 🧪 Testes

```bash
cd fbref-scraper

# Executar todos os testes
pytest

# Executar com cobertura (instale pytest-cov se necessário)
pip install pytest-cov
pytest --cov=app --cov-report=html
```

---

## ⚙️ Configuração

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

---

## 🔒 Segurança da API

Os endpoints de scraping e todas as operações de escrita do CRUD possuem:

- **Autenticação via API key** — configure `API_KEY` e envie o header `X-API-Key: <sua-chave>`; sem a configuração, as operações protegidas respondem `503`.
- O bypass de scraping e de escrita são independentes e devem ser explicitados somente em desenvolvimento, respectivamente com `ALLOW_UNAUTHENTICATED_SCRAPING=true` e `ALLOW_UNAUTHENTICATED_WRITES=true`.
- **Rate limiting por IP** — limite de `SCRAPE_RATE_LIMIT` requisições por janela de `SCRAPE_RATE_WINDOW` segundos (padrão: 30/min). Acima do limite, responde `429`.
- Os endpoints públicos de odds também possuem o limitador de `API_RATE_LIMIT`/`API_RATE_WINDOW`.

> Por padrão o rate limit é **em memória** (por processo). Configure `REDIS_URL` (ou use o `docker-compose`, que já sobe o Redis) para um rate limit **distribuído** entre workers. Se o Redis falhar, cada processo usa um fallback local limitado.

O endpoint `/health` também valida a conectividade com o banco e retorna `503` quando o banco está indisponível.

```bash
curl -X POST "http://localhost:8000/api/v1/teams/scrape?league=Serie-A" \
  -H "X-API-Key: sua-chave"
```

---

## 🗄️ Migrações de Banco de Dados (Alembic)

O schema é versionado com [Alembic](https://alembic.sqlalchemy.org/):

```bash
cd fbref-scraper

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

---

## 📖 Documentação

A documentação interativa da API está disponível em:

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Siga estes passos:

1. Faça um **Fork** do projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. Faça **commit** das alterações (`git commit -m 'Add some AmazingFeature'`)
4. Faça **push** para a branch (`git push origin feature/AmazingFeature`)
5. Abra um **Pull Request**

---

## 📄 Licença

Este projeto está licenciado sob a licença **MIT**. Veja o arquivo [LICENSE](LICENSE) para mais detalhes.

## ⚠️ Aviso Legal

Este projeto é para fins **educacionais**. Respeite os termos de uso da ESPN e use o `REQUEST_DELAY` para evitar sobrecarregar o serviço.

> A coleta atual usa os endpoints JSON públicos da ESPN. O campo de banco `fbref_id` é mantido apenas por compatibilidade e armazena o ID externo da ESPN.

---

<div align="center">

**Feito com ❤️ e ⚽ por [Gledson Crist](https://github.com/Gledson2012)**

</div>
