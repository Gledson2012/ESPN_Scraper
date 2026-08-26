<div align="center">

# ⚽ FBref Scraper

**API de scraping de dados de futebol do FBref, previsões de partidas com modelo Poisson e integração com odds da Cloudbet**

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

Esta API coleta dados de futebol do **[FBref](https://fbref.com)**, gera **previsões de partidas** usando um modelo estatístico baseado na distribuição de Poisson e xG (gols esperados), e se integra com a **[Cloudbet](https://www.cloudbet.com)** para odds de apostas em tempo real.

### ✨ Funcionalidades

- 🏟️ **Scraping de Times** - Busca times de ligas específicas
- 👤 **Scraping de Jogadores** - Busca jogadores com estatísticas detalhadas
- ⚽ **Scraping de Partidas** - Busca partidas com resultados e estatísticas
- 📊 **Previsões Inteligentes** - Modelo Poisson baseado em xG com análise de mando de campo
- 🎲 **Odds Cloudbet** - Integração em tempo real com a API da Cloudbet
- 📚 **Documentação Interativa** - Swagger UI completo com exemplos
- 🐳 **Docker Ready** - Deploy facilitado com Docker Compose

---

## 🚀 Início Rápido

### Pré-requisitos

- [Docker](https://www.docker.com/) e [Docker Compose](https://docs.docker.com/compose/)
- Ou Python 3.10+ e PostgreSQL

### 🐳 Com Docker (recomendado)

```bash
# Clone o repositório
git clone https://github.com/Gledson2012/FBref-Scraper.git
cd FBref-Scraper/fbref-scraper

# Configure uma chave para habilitar os endpoints de scraping
export API_KEY="uma-chave-forte"

# Suba os serviços (API + PostgreSQL)
docker-compose up -d

# Acesse a documentação
open http://localhost:8000/docs
```

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
curl -X POST "http://localhost:8000/api/v1/teams/scrape?league=Serie-A&season=2024-2025" \
  -H "X-API-Key: uma-chave-forte"
```

### 2️⃣ Scraping de Jogadores

```bash
curl -X POST "http://localhost:8000/api/v1/players/scrape?fbref_team_id=flamengo&season=2024-2025" \
  -H "X-API-Key: uma-chave-forte"
```

### 3️⃣ Scraping de Partidas

```bash
curl -X POST "http://localhost:8000/api/v1/matches/scrape?league=Serie-A&season=2024-2025" \
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
| `POST` | `/teams/` | Cria um time |
| `PUT` | `/teams/{id}` | Atualiza um time |
| `DELETE` | `/teams/{id}` | Deleta um time |
| `POST` | `/teams/scrape` | Scraping de times do FBref |

### 👤 Jogadores (`/api/v1/players`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/players/` | Lista jogadores (com filtros) |
| `GET` | `/players/{id}` | Obtém um jogador pelo ID |
| `POST` | `/players/` | Cria um jogador |
| `PUT` | `/players/{id}` | Atualiza um jogador |
| `DELETE` | `/players/{id}` | Deleta um jogador |
| `POST` | `/players/scrape` | Scraping de jogadores do FBref |

### ⚽ Partidas (`/api/v1/matches`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| `GET` | `/matches/` | Lista partidas (com filtros) |
| `GET` | `/matches/{id}` | Obtém uma partida pelo ID |
| `POST` | `/matches/` | Cria uma partida |
| `PUT` | `/matches/{id}` | Atualiza uma partida |
| `DELETE` | `/matches/{id}` | Deleta uma partida |
| `POST` | `/matches/scrape` | Scraping de partidas do FBref |
| `POST` | `/matches/{id}/scrape-stats` | Scraping de estatísticas da partida |

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

| Liga | Código API | Comp FBref |
|------|-----------|------------|
| 🇧🇷 Brasileirão Série A | `Serie-A` | `24` |
| 🏴 Premier League | `Premier-League` | `9` |
| 🇮🇹 Serie A (Itália) | `Serie-A-Italy` | `11` |
| 🇪🇸 La Liga | `La-Liga` | `12` |
| 🇩🇪 Bundesliga | `Bundesliga` | `20` |
| 🇫🇷 Ligue 1 | `Ligue-1` | `13` |
| 🇳🇱 Eredivisie | `Eredivisie` | `23` |
| 🇵🇹 Primeira Liga | `Primeira-Liga` | `32` |
| 🇺🇸 MLS | `MLS` | `22` |
| 🇲🇽 Liga MX | `Liga-MX` | `31` |
| 🌎 Libertadores | `Libertadores` | `18` |
| 🌍 Champions League | `Champions-League` | `8` |

> O **Código API** é o valor usado na query string dos endpoints de scraping; o **Comp FBref** é o ID numérico da competição em `fbref.com/en/comps/{ID}/`.

---

## 🏗️ Tecnologias

| Tecnologia | Uso |
|------------|-----|
| [FastAPI](https://fastapi.tiangolo.com/) | Framework web de alta performance |
| [SQLAlchemy 2.0](https://www.sqlalchemy.org/) | ORM para banco de dados |
| [PostgreSQL](https://www.postgresql.org/) | Banco de dados relacional |
| [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) | Scraping do FBref |
| [Pydantic](https://docs.pydantic.dev/) | Validação de dados |
| [Docker](https://www.docker.com/) | Containerização |
| [Poetry](https://python-poetry.org/) | Gerenciamento de dependências |

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
│   │   ├── scrapers/        # Scrapers do FBref
│   │   ├── services/        # Serviços de negócio
│   │   ├── main.py          # Ponto de entrada
│   │   ├── config.py        # Configurações
│   │   └── database.py      # Conexão com banco
│   ├── tests/               # Testes automatizados
│   ├── Dockerfile
│   ├── docker-compose.yml
│   └── requirements.txt
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
| `PROJECT_NAME` | Nome do projeto | `FBref Scraper` |
| `DEBUG` | Modo debug | `false` |
| `CORS_ORIGINS` | Origens permitidas separadas por vírgula | vazio |
| `AUTO_CREATE_SCHEMA` | Cria tabelas sem Alembic (somente desenvolvimento) | `false` |
| `REQUEST_TIMEOUT` | Timeout das requisições (s) | `30` |
| `REQUEST_DELAY` | Delay entre requisições (s) | `1.0` |
| `USER_AGENT` | User-Agent para scraping | Chrome UA |
| `CLOUDBET_API_KEY` | Chave de API da Cloudbet | vazio |
| `CLOUDBET_BASE_URL` | URL base da API Cloudbet | `https://sports-api.cloudbet.com/v2` |
| `API_KEY` | Chave de API obrigatória para endpoints de scraping | vazio |
| `ALLOW_UNAUTHENTICATED_SCRAPING` | Libera scraping sem chave (somente desenvolvimento) | `false` |
| `SCRAPE_RATE_LIMIT` | Máx. requisições de scraping por IP por janela | `30` |
| `SCRAPE_RATE_WINDOW` | Janela do rate limit (s) | `60` |
| `REDIS_URL` | URL do Redis para rate limit distribuído (vazio = em memória) | vazio |
| `CACHE_ENABLED` | Habilita o cache em disco dos scrapers | `true` |
| `CACHE_TTL_SECONDS` | TTL do cache em disco dos scrapers (s) | `3600` |
| `CACHE_DIR` | Diretório do cache em disco (vazio = temp do sistema) | vazio |

---

## 🔒 Segurança dos Endpoints de Scraping

Os endpoints de scraping (`/teams/scrape`, `/players/scrape`, `/matches/scrape` e `/matches/{id}/scrape-stats`) possuem:

- **Autenticação via API key** — configure `API_KEY` e envie o header `X-API-Key: <sua-chave>`; sem a configuração, os endpoints respondem `503`.
- Para desenvolvimento local, o bypass precisa ser explícito com `ALLOW_UNAUTHENTICATED_SCRAPING=true`.
- **Rate limiting por IP** — limite de `SCRAPE_RATE_LIMIT` requisições por janela de `SCRAPE_RATE_WINDOW` segundos (padrão: 30/min). Acima do limite, responde `429`.

> Por padrão o rate limit é **em memória** (por processo). Configure `REDIS_URL` (ou use o `docker-compose`, que já sobe o Redis) para um rate limit **distribuído** entre workers. Se o Redis falhar, as requisições são permitidas (fail-open).

```bash
curl -X POST "http://localhost:8000/api/v1/teams/scrape?league=Serie-A&season=2024-2025" \
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
curl -X POST "http://localhost:8000/api/v1/teams/scrape?league=Serie-A&season=2024-2025" \
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

Este projeto é para fins **educacionais**. O FBref é um site com direitos autorais. Respeite os termos de serviço do site e não faça scraping agressivo. Use o `REQUEST_DELAY` para evitar sobrecarregar o servidor.

> **Importante sobre scraping:** o FBref utiliza proteção anti-bot (Cloudflare) e pode responder **HTTP 403** para requisições automatizadas, mesmo com User-Agent de navegador. Nesse caso, os endpoints de scraping retornam `502` com mensagem clara. Para dados em tempo real, utilize a integração de odds da Cloudbet. Para scraping, considere executar a partir de um IP residencial ou usar um navegador headless.

---

<div align="center">

**Feito com ❤️ e ⚽ por [Gledson Crist](https://github.com/Gledson2012)**

</div>
