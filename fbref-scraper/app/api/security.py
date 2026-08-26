"""Segurança dos endpoints de scraping: chave de API e rate limiting.

- **Autenticação**: exigida por padrão. O bypass só existe quando
  ``ALLOW_UNAUTHENTICATED_SCRAPING`` estiver explicitamente ativado.
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
from typing import Callable, Deque, Dict

from fastapi import HTTPException, Request, Security
from fastapi.security import APIKeyHeader

from app.config import settings

logger = logging.getLogger(__name__)
api_key_header = APIKeyHeader(
    name="X-API-Key",
    scheme_name="ApiKeyAuth",
    description="Chave configurada em `API_KEY` para acessar endpoints de scraping.",
    auto_error=False,
)


def require_api_key(x_api_key: str | None = Security(api_key_header)) -> None:
    """Exige a chave de API, exceto quando o bypass foi explicitamente ativado."""
    if not settings.API_KEY:
        if settings.ALLOW_UNAUTHENTICATED_SCRAPING:
            return
        raise HTTPException(
            status_code=503,
            detail="Scraping desabilitado: configure a variável API_KEY.",
        )

    if not x_api_key or not secrets.compare_digest(x_api_key, settings.API_KEY):
        raise HTTPException(
            status_code=401,
            detail="API key inválida ou ausente. Envie o header 'X-API-Key'.",
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
    ):
        self.redis = redis_client
        self.limit = limit
        self.window = window_seconds
        self.key_prefix = key_prefix

    def allow(self, key: str) -> bool:
        """Registra uma requisição; retorna False se o limite foi excedido.

        Em caso de falha de conexão com o Redis, permite a requisição (fail-open)
        para não derrubar a API — apenas registra o problema.
        """
        now = time.time()
        rkey = f"rate_limit:{self.key_prefix}:{key}"
        min_score = now - self.window

        # Check-then-act não é atômico: em concorrência extrema pode haver um
        # leve estouro do limite — aceitável para rate limiting.
        try:
            with self.redis.pipeline() as pipe:
                pipe.zremrangebyscore(rkey, "-inf", min_score)
                pipe.zcard(rkey)
                count = pipe.execute()[1]

            if count >= self.limit:
                return False

            member = f"{now}:{secrets.token_hex(6)}"
            self.redis.zadd(rkey, {member: now})
            self.redis.expire(rkey, int(self.window * 2) + 1)
        except Exception as e:  # noqa: BLE001
            logger.warning(f"Falha no rate limiter Redis ({e}); permitindo requisição")
        return True


def _limiter_dependency(limiter) -> Callable[[Request], None]:
    """Cria uma dependência FastAPI que limita requisições por IP."""

    def dependency(request: Request) -> None:
        ip = request.client.host if request.client else "unknown"
        if not limiter.allow(ip):
            logger.warning(f"Rate limit excedido para o IP {ip}")
            raise HTTPException(
                status_code=429,
                detail="Muitas requisições. Aguarde e tente novamente.",
            )

    return dependency


def build_scrape_rate_limiter() -> Callable[[Request], None]:
    """Cria a dependência de rate limit para os endpoints de scraping.

    Usa Redis (distribuído) quando ``REDIS_URL`` está configurada; caso contrário,
    usa um limitador em memória (por processo).
    """
    limit = settings.SCRAPE_RATE_LIMIT
    window = settings.SCRAPE_RATE_WINDOW

    if settings.REDIS_URL:
        try:
            import redis as redis_lib
        except ImportError:
            logger.warning("Pacote 'redis' não instalado; usando rate limiter em memória")
            return _limiter_dependency(SlidingWindowRateLimiter(limit, window))

        client = redis_lib.from_url(settings.REDIS_URL, decode_responses=True)
        logger.info("Rate limiter Redis ativo")
        return _limiter_dependency(RedisSlidingWindowRateLimiter(client, limit, window))

    return _limiter_dependency(SlidingWindowRateLimiter(limit, window))


# Rate limiter padrão dos endpoints de scraping (configurável via variáveis de ambiente)
scrape_rate_limiter = build_scrape_rate_limiter()
