# Scoutly — frontend

Painel React para consumir a API do ESPN Scraper.

## Executar

```bash
npm install
cp .env.example .env
npm run dev
```

O painel estará disponível em `http://localhost:5173`. Por padrão, ele consome
`http://localhost:8000/api/v1`; altere `VITE_API_URL` no `.env` quando necessário.
Em produção, `VITE_API_URL` pode ser o domínio da API ou o endereço completo com
`/api/v1`; o cliente adiciona esse prefixo automaticamente quando necessário.

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

Para substituir o snapshot por dados reais atualizados da ESPN, execute na
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

## Aplicativo Android

O app Android usa Capacitor e reaproveita a mesma interface React. É necessário
ter o Android Studio, um SDK Android instalado e um emulador ou aparelho com
depuração USB habilitada.

Antes de gerar o app, configure no `.env` a URL pública da API (com HTTPS em
produção):

```bash
VITE_API_URL=https://seu-dominio.example.com/api/v1
```

Com a API já configurada, execute na pasta `frontend`:

```bash
npm install
npm run android:build
```

O APK de debug será criado em
`android/app/build/outputs/apk/debug/app-debug.apk`. Para abrir o projeto no
Android Studio use `npm run android:open`; para executar em um emulador ou
dispositivo conectado use `npm run android:run`.

Durante o desenvolvimento local, o emulador Android acessa a API do computador
por `http://10.0.2.2:8000/api/v1` (em um aparelho físico, use o IP da máquina na
rede local). A configuração `usesCleartextTraffic` do projeto permite esse
acesso HTTP local; em produção, prefira sempre HTTPS.
