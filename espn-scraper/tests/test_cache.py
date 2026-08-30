"""Testes do cache em disco usado pelos scrapers."""

import time

from app.config import settings
from app.scrapers.cache import cache_get, cache_set, get_soup


def _html(text: str) -> str:
    """HTML de teste com tamanho acima do mínimo cacheável (100 chars)."""
    return f"<html><body><h1>{text}</h1><p>{'x' * 120}</p></body></html>"


def _enable_cache(monkeypatch, tmp_path, ttl=3600):
    monkeypatch.setattr(settings, "CACHE_ENABLED", True)
    monkeypatch.setattr(settings, "CACHE_TTL_SECONDS", ttl)
    monkeypatch.setattr(settings, "CACHE_DIR", str(tmp_path))


def test_cache_roundtrip(monkeypatch, tmp_path):
    _enable_cache(monkeypatch, tmp_path)
    url = "https://fbref.com/en/comps/24/schedule"
    assert cache_get(url) is None
    cache_set(url, _html("teste"))
    assert cache_get(url) == _html("teste")


def test_cache_expired(monkeypatch, tmp_path):
    """Com TTL zerado, o cache é considerado expirado imediatamente."""
    _enable_cache(monkeypatch, tmp_path, ttl=0)
    cache_set("https://fbref.com/x", _html("expirado"))
    time.sleep(0.01)
    assert cache_get("https://fbref.com/x") is None


def test_cache_disabled(monkeypatch, tmp_path):
    _enable_cache(monkeypatch, tmp_path)
    cache_set("https://fbref.com/y", _html("ok"))
    monkeypatch.setattr(settings, "CACHE_ENABLED", False)
    assert cache_get("https://fbref.com/y") is None


def test_cache_is_per_url(monkeypatch, tmp_path):
    _enable_cache(monkeypatch, tmp_path)
    cache_set("https://fbref.com/a", _html("a"))
    assert cache_get("https://fbref.com/b") is None
    assert cache_get("https://fbref.com/a") == _html("a")


def test_cache_ignores_too_short_content(monkeypatch, tmp_path):
    """Conteúdo muito curto (resposta vazia/truncada) não é cacheado."""
    _enable_cache(monkeypatch, tmp_path)
    cache_set("https://fbref.com/short", "<html/>")
    assert cache_get("https://fbref.com/short") is None


class FakeSession:
    """Sessão que falha se for usada (para testar que o cache evita a rede)."""

    def __init__(self):
        self.calls = 0

    def get(self, url, timeout):
        self.calls += 1
        raise AssertionError(f"Não deveria acessar a rede: {url}")


def test_get_soup_uses_cache_without_network(monkeypatch, tmp_path):
    _enable_cache(monkeypatch, tmp_path)
    cache_set("https://fbref.com/pagina", _html("em cache"))
    session = FakeSession()
    soup = get_soup(session, "https://fbref.com/pagina")
    assert soup.find("h1").text == "em cache"
    assert session.calls == 0


def test_get_soup_fetches_and_stores_on_miss(monkeypatch, tmp_path):
    _enable_cache(monkeypatch, tmp_path)
    # Elimina o delay entre requisições nos testes
    monkeypatch.setattr("app.scrapers.cache.time.sleep", lambda seconds: None)

    class FakeResponse:
        text = _html("novo")

        def raise_for_status(self):
            pass

    class FakeSession:
        def get(self, url, timeout):
            return FakeResponse()

    soup = get_soup(FakeSession(), "https://fbref.com/outra")
    assert soup.find("h1").text == "novo"
    assert cache_get("https://fbref.com/outra") == _html("novo")
