FROM python:3.12-slim

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Criar usuário não-root para rodar a aplicação
RUN adduser --disabled-password --gecos "" appuser

WORKDIR /app

# Copiar requirements e instalar dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código da aplicação
COPY . .

# Garantir que o diretório de cache existe e pertence ao usuário correto
RUN mkdir -p /tmp/espn_cache && chown -R appuser:appuser /app /tmp/espn_cache

# Trocar para o usuário não-root
USER appuser

# Expor porta da API
EXPOSE 8000

# Comando para iniciar a aplicação (PORT é injetado por plataformas de deploy;
# localmente/Docker Compose usa 8000)
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
