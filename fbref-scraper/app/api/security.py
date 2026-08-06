"""Segurança dos endpoints de scraping: chave de API e rate limiting.

- **Autenticação**: opcional — só é exigida quando ``API_KEY`` estiver configurada.
  Nesse caso, os clientes devem enviar o header ``X-API-Key``.
- **Rate limiting**: janela deslizante em memória (por processo). Para múltiplos
  workers/instâncias, considere um backend distribuído (ex: Redis).
  O orçamento é **global entre os endpoints de scraping** (soma de todas as
  requisições de um mesmo IP), não por endpoint.
"""

import logging
import threading
import time
from collections import defaultdict, deque
from typing import Callable, Deque, Dict

from fastapi import Header, HTTPException, Request

from app.config import settings

logger = logging.getLogger(__name__)


def require_api_key(x_api_key: str = Header(default="")) -> None:
    """Exige a chave de API quando ``API_KEY`` estiver configurada."""
    if settings.API_KEY and x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=401,
            detail="API key inválida ou ausente. Envie o header 'X-API-Key'.",
        )


class SlidingWindowRateLimiter:
    """Rate limiter de janela deslizante (em memória, por processo)."""

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


def rate_limit(limit: int, window_seconds: float) -> Callable[[Request], None]:
    """Cria uma dependência FastAPI que limita requisições por IP."""
    limiter = SlidingWindowRateLimiter(limit, window_seconds)

    def dependency(request: Request) -> None:
        ip = request.client.host if request.client else "unknown"
        if not limiter.allow(ip):
            logger.warning(f"Rate limit excedido para o IP {ip}")
            raise HTTPException(
                status_code=429,
                detail="Muitas requisições. Aguarde e tente novamente.",
            )

    return dependency


# Limite padrão dos endpoints de scraping (configurável via variáveis de ambiente)
scrape_rate_limiter = rate_limit(settings.SCRAPE_RATE_LIMIT, settings.SCRAPE_RATE_WINDOW)
