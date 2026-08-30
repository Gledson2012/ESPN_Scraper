"""Segurança da API: autenticação de escrita e rate limiting.

- **Autenticação**: exigida por padrão. Os bypasses só existem quando
  ``ALLOW_UNAUTHENTICATED_SCRAPING`` ou ``ALLOW_UNAUTHENTICATED_WRITES``
  estiverem explicitamente ativados (somente desenvolvimento/testes).
  Com chave configurada, os clientes devem enviar o header ``X-API-Key``.
- **Rate limiting**: janela deslizante. Por padrão é em memória (por processo);
  se ``REDIS_URL`` estiver configurada, usa Redis (distribuído entre workers).
  O orçamento é **global entre os endpoints de scraping** (soma de todas as
  requisições de um mesmo IP), não por endpoint.
"""

import logging
import secrets
import threading
import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict, Optional

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

from app.config import settings

logger = logging.getLogger(__name__)
api_key_header = APIKeyHeader(
    name="X-API-Key",
    scheme_name="ApiKeyAuth",
    description="Chave configurada em `API_KEY` para scraping e operações de escrita.",
    auto_error=False,
)


def _validate_api_key(
    x_api_key: str | None,
    disabled_detail: str,
    allow_unauthenticated: bool,
) -> None:
    """Valida a chave configurada para uma operação protegida."""
    if not settings.API_KEY:
        if allow_unauthenticated:
            return
        raise HTTPException(
            status_code=503,
            detail=disabled_detail,
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(
            status_code=401,
            detail="API key inválida ou ausente. Envie o header 'X-API-Key'.",
        )


def require_api_key(x_api_key: str | None = Security(api_key_header)) -> None:
    """Exige a chave de API para scraping."""
    _validate_api_key(
        x_api_key,
        "Scraping desabilitado: configure a variável API_KEY.",
        settings.ALLOW_UNAUTHENTICATED_SCRAPING,
    )


def require_write_api_key(x_api_key: str | None = Security(api_key_header)) -> None:
    """Exige a chave de API para criar, atualizar ou excluir dados."""
    _validate_api_key(
        x_api_key,
        "Operações de escrita desabilitadas: configure a variável API_KEY.",
        settings.ALLOW_UNAUTHENTICATED_WRITES,
    )


class SlidingWindowRateLimiter:
    """Rate limiter de janela deslizante em memória (por processo)."""

    def __init__(self, limit: int, window_seconds: float):
        self.limit = limit
        self.window = window_seconds
        self._hits: Dict[str, Deque[float]] = defaultdict(deque)
        self._lock = threading.Lock()
        self._last_sweep = 0.0

    def allow(self, key: str) -> bool:
        """Registra uma requisição; retorna False se o limite foi excedido."""
        now = time.monotonic()
        with self._lock:
            self._sweep(now)
            hits = self._hits[key]
            while hits and now - hits[0] > self.window:
                hits.popleft()
            if len(hits) >= self.limit:
                return False
            hits.append(now)
            return True

    def _sweep(self, now: float) -> None:
        """Remove chaves cujas entradas já expiraram, evitando crescimento sem limite."""
        if now - self._last_sweep < self.window:
            return
        self._last_sweep = now
        for key, hits in list(self._hits.items()):
            while hits and now - hits[0] > self.window:
                hits.popleft()
            if not hits:
                del self._hits[key]


class RedisSlidingWindowRateLimiter:
    """Rate limiter de janela deslizante usando sorted sets do Redis (distribuído)."""

    def __init__(
        self,
        redis_client,
        limit: int,
        window_seconds: float,
        key_prefix: str = "scrape",
        fallback: Optional[SlidingWindowRateLimiter] = None,
    ):
        self.redis = redis_client
        self.limit = limit
        self.window = window_seconds
        self.key_prefix = key_prefix
        self.fallback = fallback or SlidingWindowRateLimiter(limit, window_seconds)

    def allow(self, key: str) -> bool:
        """Registra uma requisição; retorna False se o limite foi excedido.

        Em caso de falha de conexão com o Redis, usa o fallback local para
        preservar alguma proteção sem derrubar a API.
        """
        now = time.time()
        rkey = f"rate_limit:{self.key_prefix}:{key}"

        try:
            member = f"{now}:{secrets.token_hex(6)}"
            result = self.redis.eval(
                """
                local now = tonumber(ARGV[1])
                local window = tonumber(ARGV[2])
                local limit = tonumber(ARGV[3])
                local member = ARGV[4]
                redis.call('ZREMRANGEBYSCORE', KEYS[1], '-inf', now - window)
                local count = redis.call('ZCARD', KEYS[1])
                if count >= limit then
                    redis.call('EXPIRE', KEYS[1], math.floor(window * 2) + 1)
                    return 0
                end
                redis.call('ZADD', KEYS[1], now, member)
                redis.call('EXPIRE', KEYS[1], math.floor(window * 2) + 1)
                return 1
                """,
                1,
                rkey,
                str(now),
                str(self.window),
                str(self.limit),
                member,
            )
            return int(result) == 1
        except Exception as e:  # noqa: BLE001
            # O fallback local mantém alguma proteção durante uma indisponibilidade
            # do Redis, evitando um bypass ilimitado do rate limit.
            logger.warning("Falha no rate limiter Redis (%s); usando fallback local", e)
            return self.fallback.allow(key)


def _limiter_dependency(limiter) -> Callable[[Request], None]:
    """Cria uma dependência FastAPI que limita requisições por IP."""

    def dependency(request: Request) -> None:
        ip = request.client.host if request.client else "unknown"
        if not limiter.allow(ip):
            logger.warning("Rate limit excedido para o IP %s", ip)
            raise HTTPException(
                status_code=429,
                detail="Muitas requisições. Aguarde e tente novamente.",
            )

    return dependency


def build_rate_limiter(limit: int, window: int, key_prefix: str) -> Callable[[Request], None]:
    """Cria uma dependência de rate limit, distribuída quando Redis está disponível.

    Usa Redis (distribuído) quando ``REDIS_URL`` está configurada; caso contrário,
    usa um limitador em memória (por processo).
    """
    if settings.REDIS_URL:
        try:
            import redis as redis_lib
        except ImportError:
            logger.warning("Pacote 'redis' não instalado; usando rate limiter em memória")
            return _limiter_dependency(SlidingWindowRateLimiter(limit, window))

        client = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
        logger.info("Rate limiter Redis ativo para o grupo %s", key_prefix)
        fallback = SlidingWindowRateLimiter(limit, window)
        return _limiter_dependency(
            RedisSlidingWindowRateLimiter(client, limit, window, key_prefix, fallback)
        )

    return _limiter_dependency(SlidingWindowRateLimiter(limit, window))


def build_scrape_rate_limiter() -> Callable[[Request], None]:
    """Mantém a fábrica pública do limitador de scraping."""
    return build_rate_limiter(
        settings.SCRAPE_RATE_LIMIT,
        settings.SCRAPE_RATE_WINDOW,
        "scrape",
    )


# Limitadores padrão (configuráveis via variáveis de ambiente).
scrape_rate_limiter = build_scrape_rate_limiter()
public_rate_limiter = build_rate_limiter(
    settings.API_RATE_LIMIT,
    settings.API_RATE_WINDOW,
    "public",
)
