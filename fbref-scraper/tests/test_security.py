"""Testes de segurança: API key e rate limiter dos endpoints de scraping."""

import time

import pytest
from fastapi import HTTPException

from app.api.security import (
    require_api_key,
    RedisSlidingWindowRateLimiter,
    SlidingWindowRateLimiter,
)
from app.config import settings


# ===== API key =====

def test_require_api_key_disabled_by_default(monkeypatch):
    """O bypass sem chave só funciona quando explicitamente ativado."""
    monkeypatch.setattr(settings, "API_KEY", "")
    monkeypatch.setattr(settings, "ALLOW_UNAUTHENTICATED_SCRAPING", True)
    require_api_key(x_api_key="")  # não deve lançar


def test_require_api_key_rejects_missing_configuration(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "")
    monkeypatch.setattr(settings, "ALLOW_UNAUTHENTICATED_SCRAPING", False)
    with pytest.raises(HTTPException) as exc:
        require_api_key(x_api_key="")
    assert exc.value.status_code == 503


def test_require_api_key_rejects_missing(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "secret-key")
    with pytest.raises(HTTPException) as exc:
        require_api_key(x_api_key="")
    assert exc.value.status_code == 401


def test_require_api_key_rejects_wrong(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "secret-key")
    with pytest.raises(HTTPException) as exc:
        require_api_key(x_api_key="chave-errada")
    assert exc.value.status_code == 401


def test_require_api_key_accepts_valid(monkeypatch):
    monkeypatch.setattr(settings, "API_KEY", "secret-key")
    require_api_key(x_api_key="secret-key")  # não deve lançar


# ===== Rate limiter =====

def test_rate_limiter_blocks_after_limit():
    limiter = SlidingWindowRateLimiter(limit=2, window_seconds=60)
    assert limiter.allow("192.168.0.1") is True
    assert limiter.allow("192.168.0.1") is True
    assert limiter.allow("192.168.0.1") is False


def test_rate_limiter_is_per_key():
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=60)
    assert limiter.allow("ip-a") is True
    assert limiter.allow("ip-a") is False
    assert limiter.allow("ip-b") is True  # outro IP não é afetado


def test_rate_limiter_window_expiry():
    """Após a janela expirar, novas requisições voltam a ser permitidas."""
    limiter = SlidingWindowRateLimiter(limit=1, window_seconds=0.05)
    assert limiter.allow("ip") is True
    assert limiter.allow("ip") is False
    time.sleep(0.06)
    assert limiter.allow("ip") is True


# ===== Rate limiter Redis =====

class FakeRedisPipeline:
    """Pipeline fake com os comandos usados pelo limiter."""

    def __init__(self, client):
        self.client = client
        self.queue = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def zremrangebyscore(self, key, lo, hi):
        self.queue.append(("zremrangebyscore", key, lo, hi))
        return self

    def zcard(self, key):
        self.queue.append(("zcard", key))
        return self

    def execute(self):
        results = []
        for cmd in self.queue:
            if cmd[0] == "zremrangebyscore":
                self.client.zremrangebyscore(cmd[1], cmd[2], cmd[3])
                results.append(0)
            elif cmd[0] == "zcard":
                results.append(self.client.zcard(cmd[1]))
        return results


class FakeRedis:
    """Cliente Redis fake: sorted sets em memória."""

    def __init__(self):
        self.zsets = {}

    def pipeline(self):
        return FakeRedisPipeline(self)

    def zremrangebyscore(self, key, lo, hi):
        entries = self.zsets.setdefault(key, {})
        for member, score in list(entries.items()):
            if score <= hi and (lo == "-inf" or score >= lo):
                del entries[member]

    def zcard(self, key):
        return len(self.zsets.get(key, {}))

    def zadd(self, key, mapping):
        self.zsets.setdefault(key, {}).update(mapping)

    def expire(self, key, ttl):
        pass  # TTL não afeta o teste


def test_redis_rate_limiter_blocks_after_limit():
    limiter = RedisSlidingWindowRateLimiter(FakeRedis(), limit=2, window_seconds=60)
    assert limiter.allow("ip") is True
    assert limiter.allow("ip") is True
    assert limiter.allow("ip") is False


def test_redis_rate_limiter_is_per_key():
    limiter = RedisSlidingWindowRateLimiter(FakeRedis(), limit=1, window_seconds=60)
    assert limiter.allow("ip-a") is True
    assert limiter.allow("ip-a") is False
    assert limiter.allow("ip-b") is True


def test_redis_rate_limiter_fail_open_when_redis_down():
    """Se o Redis falhar, a requisição é permitida (fail-open)."""
    class FailingRedis:
        def pipeline(self):
            raise ConnectionError("redis indisponível")

    limiter = RedisSlidingWindowRateLimiter(FailingRedis(), limit=1, window_seconds=60)
    assert limiter.allow("ip") is True


def test_build_scrape_rate_limiter_memory_without_redis(monkeypatch):
    """Sem REDIS_URL, usa o limitador em memória."""
    import app.api.security as security

    monkeypatch.setattr(settings, "REDIS_URL", "")
    monkeypatch.setattr(security, "_limiter_dependency", lambda limiter: limiter)
    limiter = security.build_scrape_rate_limiter()
    assert isinstance(limiter, security.SlidingWindowRateLimiter)


def test_build_scrape_rate_limiter_redis_when_configured(monkeypatch):
    """Com REDIS_URL configurada, usa o limitador Redis (sem conectar)."""
    import app.api.security as security

    monkeypatch.setattr(settings, "REDIS_URL", "redis://localhost:6379/0")
    monkeypatch.setattr(security, "_limiter_dependency", lambda limiter: limiter)
    limiter = security.build_scrape_rate_limiter()
    assert isinstance(limiter, security.RedisSlidingWindowRateLimiter)


# ===== Integração via HTTP =====

def test_scrape_teams_requires_api_key(client, monkeypatch):
    """Com API_KEY configurada, o endpoint /teams/scrape exige o header."""
    monkeypatch.setattr(settings, "API_KEY", "secret-key")

    # Evita acesso à rede: mocka o serviço de scraping
    from app.api import teams as teams_api
    monkeypatch.setattr(
        teams_api.FBrefService,
        "scrape_and_save_teams",
        lambda self, league, season: [],
    )

    # Sem header → 401
    response = client.post("/api/v1/teams/scrape?league=Serie-A")
    assert response.status_code == 401

    # Com header correto → 200
    response = client.post(
        "/api/v1/teams/scrape?league=Serie-A",
        headers={"X-API-Key": "secret-key"},
    )
    assert response.status_code == 200
    assert response.json() == []
