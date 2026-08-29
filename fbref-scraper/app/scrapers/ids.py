"""Utilitários para extrair IDs de recursos do FBref."""

from typing import Optional
from urllib.parse import urlparse


def extract_fbref_id(href: str | None, resource: str) -> Optional[str]:
    """Retorna o ID após ``resource`` em uma URL do FBref.

    Exemplos aceitos: ``/en/squads/abc123/2026/`` e
    ``https://fbref.com/en/matches/def456/report``.
    """
    if not href:
        return None

    parts = [part for part in urlparse(href).path.split("/") if part]
    resource_index = next(
        (index for index, part in enumerate(parts) if part.casefold() == resource.casefold()),
        None,
    )
    if resource_index is None or resource_index + 1 >= len(parts):
        return None
    return parts[resource_index + 1]
