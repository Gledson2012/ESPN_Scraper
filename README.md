# futebolBR

API para scraping de dados de futebol do [FBref](https://fbref.com), geração de previsões de partidas e integração com odds de apostas da [Cloudbet](https://www.cloudbet.com).

## 📦 Estrutura

```
futebolBR/
├── fbref-scraper/     # API principal (FastAPI + SQLAlchemy + PostgreSQL)
├── src/futebolbr/     # Pacote Python (placeholder)
├── tests/             # Testes do pacote raiz
├── pyproject.toml     # Configuração Poetry
└── README.md
```

## 🚀 Início Rápido

O projeto principal está em `fbref-scraper/`. Consulte o [README do fbref-scraper](fbref-scraper/README.md) para instruções detalhadas de instalação e uso.

```bash
# Com Docker
cd fbref-scraper
docker-compose up -d

# A API estará em http://localhost:8000
# Documentação em http://localhost:8000/docs
```

## 🏗️ Tecnologias

- **FastAPI** - Framework web
- **SQLAlchemy 2.0** - ORM
- **PostgreSQL** - Banco de dados
- **BeautifulSoup** - Scraping
- **Pydantic** - Validação de dados
- **Docker** - Containerização

## 📄 Licença

MIT