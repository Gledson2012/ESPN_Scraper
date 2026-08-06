"""Testes de segurança: API key e rate limiter dos endpoints de scraping."""

import time

import pytest
from fastapi import HTTPException

from app.api.security import require_api_key, SlidingWindowRateLimiter
from app.config import settings


# ===== API key =====

def test_require_api_key_disabled_by_default(monkeypatch):
    """Com API_KEY vazio, os endpoints de scraping não exigem autenticação."""
    monkeypatch.setattr(settings, "API_KEY", "")
    require_api_key(x_api_key="")  # não deve lançar


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
