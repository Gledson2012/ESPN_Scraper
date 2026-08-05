# FBref Scraper

API para scraping de dados de futebol do [FBref](https://fbref.com), geração de previsões de partidas e integração com odds de apostas da [Cloudbet](https://www.cloudbet.com).

## 📋 Funcionalidades

- **Scraping de Times**: Busca times de ligas específicas
- **Scraping de Jogadores**: Busca jogadores de times específicos
- **Scraping de Partidas**: Busca partidas de ligas e temporadas
- **Scraping de Estatísticas**: Busca estatísticas detalhadas de partidas
- **Previsões**: Gera previsões de partidas usando modelo Poisson baseado em xG
- **Odds Cloudbet**: Integração com a API da Cloudbet para odds de apostas de futebol

## 🚀 Instalação

### Com Docker (recomendado)

```bash
# Subir os serviços (API + PostgreSQL)
docker-compose up -d

# A API estará disponível em http://localhost:8000
# Documentação interativa em http://localhost:8000/docs
```

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

# Iniciar a API
uvicorn app.main:app --reload
```

## 📚 Endpoints da API

### Times (`/api/v1/teams`)

| Método | Endpoint | Descrição |
|--------|----------|-----------|
| GET | `/api/v1/teams/` | Lista times (com filtros) |
| GET | `/api/v1/teams/{id}` | Obtém um time |
| POST | `/api/v1/teams/` | Cria um time |
| PUT | `/api/v1/teams/{id}` | Atualiza um time |
| DELETE | `/api/v1/teams/{id}` | Deleta um time |
| POST | `/api/v1/teams/scrape?league=Serie-A&season=2024-2025` | Scraping de times |

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
| GET | `/api/v1/matches/{id}` | Obtém uma partida |
| POST | `/api/v1/matches/` | Cria uma partida |
| PUT | `/api/v1/matches/{id}` | Atualiza uma partida |
| DELETE | `/api/v1/matches/{id}` | Deleta uma partida |
| POST | `/api/v1/matches/scrape?league=Serie-A&season=2024-2025` | Scraping de partidas |
| POST | `/api/v1/matches/{id}/scrape-stats` | Scraping de estatísticas |

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
  "away_team_id": 2,
  "competition": "Serie-A",
  "season": "2024-2025"
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
fbref-scraper/
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
│   │   ├── fbref.py         # Serviço que orquestra scrapers e banco
│   │   └── cloudbet.py      # Serviço de integração com API Cloudbet
│   ├── scrapers/            # Scrapers do FBref
│   │   ├── teams.py
│   │   ├── players.py
│   │   ├── matches.py
│   │   └── statistics.py
│   └── api/                 # Rotas da API
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

# Executar testes com cobertura
pytest --cov=app --cov-report=html
```

## 🔧 Configuração

As configurações podem ser definidas via variáveis de ambiente ou arquivo `.env`:

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `DATABASE_URL` | URL do banco de dados | `postgresql://postgres:postgres@localhost:5432/fbref_scraper` |
| `API_V1_PREFIX` | Prefixo da API | `/api/v1` |
| `PROJECT_NAME` | Nome do projeto | `FBref Scraper` |
| `DEBUG` | Modo debug | `true` |
| `REQUEST_TIMEOUT` | Timeout das requisições (s) | `30` |
| `REQUEST_DELAY` | Delay entre requisições (s) | `1.0` |
| `USER_AGENT` | User-Agent para scraping | Chrome UA |
| `CLOUDBET_API_KEY` | Chave de API da Cloudbet | vazio |
| `CLOUDBET_BASE_URL` | URL base da API Cloudbet | `https://sports-api.cloudbet.com/v2` |

## 🏆 Ligas Suportadas

O scraper suporta as seguintes ligas (mapeadas automaticamente para os códigos do FBref):

| Liga | Código FBref |
|------|-------------|
| Serie-A (Brasil) | 9 |
| Premier-League | 9 |
| La-Liga | 12 |
| Bundesliga | 20 |
| Serie-A-Italy | 11 |
| Ligue-1 | 13 |
| Eredivisie | 23 |
| Primeira-Liga | 32 |
| MLS | 22 |
| Liga-MX | 31 |
| Libertadores | 18 |
| Champions-League | 8 |

## ⚠️ Aviso Legal

Este projeto é para fins educacionais. O FBref é um site com direitos autorais. Respeite os termos de serviço do site e não faça scraping agressivo. Use o `REQUEST_DELAY` para evitar sobrecarregar o servidor.

## 📄 Licença

MIT