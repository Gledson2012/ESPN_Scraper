"""Cache em disco (best-effort) para as respostas HTML dos scrapers do FBref.

Evita re-requisições ao FBref quando o mesmo URL já foi coletado dentro do TTL
(``CACHE_TTL_SECONDS``). Desativável via ``CACHE_ENABLED=false``.
O diretório padrão é o diretório temporário do sistema; configure ``CACHE_DIR``
para persistir entre execuções (ex: um volume no Docker).
"""

import hashlib
import logging
import os
import tempfile
import time
from pathlib import Path
from typing import Optional

from bs4 import BeautifulSoup, Comment

from app.config import settings

logger = logging.getLogger(__name__)

# Tamanho mínimo (chars) para considerar o conteúdo cacheável
MIN_CONTENT_LENGTH = 100


def _cache_dir() -> Path:
    base = (
        Path(settings.CACHE_DIR)
        if settings.CACHE_DIR
        else Path(tempfile.gettempdir()) / "fbref-scraper-cache"
    )
    base.mkdir(parents=True, exist_ok=True)
    return base


def _cache_path(url: str) -> Path:
    digest = hashlib.sha1(url.encode("utf-8")).hexdigest()
    return _cache_dir() / f"{digest}.html"


def cache_get(url: str) -> Optional[str]:
    """Retorna o HTML em cache se ainda estiver dentro do TTL; senão None."""
    if not settings.CACHE_ENABLED:
        return None
    path = _cache_path(url)
    try:
        if time.time() - path.stat().st_mtime < settings.CACHE_TTL_SECONDS:
            return path.read_text(encoding="utf-8")
    except OSError:
        pass
    return None


def cache_set(url: str, content: str) -> None:
    """Grava o HTML em disco de forma atômica (best-effort)."""
    if not settings.CACHE_ENABLED:
        return
    # Evita cachear respostas vazias/truncadas (ex: bloqueio anti-bot sem conteúdo)
    if len(content) < MIN_CONTENT_LENGTH:
        logger.debug(f"Conteúdo muito curto ({len(content)} chars); não gravando cache de {url}")
        return
    path = _cache_path(url)
    tmp = path.with_suffix(".tmp")
    try:
        tmp.write_text(content, encoding="utf-8")
        os.replace(tmp, path)
    except OSError:
        logger.debug(f"Falha ao gravar cache para {url}")


def _parse_soup(content: str) -> BeautifulSoup:
    """Parseia HTML e também expõe tabelas que o FBref entrega em comentários."""
    soup = BeautifulSoup(content, "lxml")
    comments = soup.find_all(string=lambda value: isinstance(value, Comment))
    for comment in comments:
        if "<table" not in comment.lower():
            continue
        fragment = BeautifulSoup(str(comment), "lxml")
        for table in fragment.find_all("table"):
            soup.append(table)
    return soup


def get_soup(session, url: str) -> BeautifulSoup:
    """Busca a URL usando cache em disco e retorna o BeautifulSoup da página."""
    cached = cache_get(url)
    if cached is not None:
        logger.info(f"Cache hit: {url}")
        return _parse_soup(cached)

    response = session.get(url, timeout=settings.REQUEST_TIMEOUT)
    response.raise_for_status()
    time.sleep(settings.REQUEST_DELAY)
    cache_set(url, response.text)
    return _parse_soup(response.text)
