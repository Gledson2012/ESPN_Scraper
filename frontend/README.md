# Scoutly — frontend

Painel React para consumir a API do FBref Scraper.

## Executar

```bash
npm install
cp .env.example .env
npm run dev
```

O painel estará disponível em `http://localhost:5173`. Por padrão, ele consome
`http://localhost:8000/api/v1`; altere `VITE_API_URL` no `.env` quando necessário.

## Estrutura

```text
src/
├── components/       # Shell, navegação e componentes visuais reutilizáveis
├── data/             # Dados locais para modo demonstração
├── lib/              # Cliente HTTP e formatadores
├── pages/            # Dashboard, partidas, times, previsões e odds
├── styles/            # Design system e responsividade
├── types/             # Tipos alinhados aos schemas da API FastAPI
├── App.tsx            # Rotas da aplicação
└── main.tsx           # Entrada React
```

O modo demonstração usa um snapshot local de jogos reais quando algum endpoint
está vazio ou não responde. Isso permite desenvolver a interface sem expor
`API_KEY` no navegador; essa chave deve permanecer somente no backend.

Para substituir o snapshot por dados reais atualizados do FBref, execute na
pasta da API:

```bash
python scripts/sync_real_matches.py --league Serie-A --season 2026
```

Com Docker, use `docker compose exec api python scripts/sync_real_matches.py
--league Serie-A --season 2026`.

## Build

```bash
npm run build
npm run preview
```
