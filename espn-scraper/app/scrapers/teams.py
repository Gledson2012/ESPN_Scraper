"""Compatibilidade para o scraper de equipes.

O provedor ativo é a ESPN; o nome deste módulo é mantido para não quebrar
imports existentes da aplicação.
"""

from app.scrapers.espn import TeamsScraper

__all__ = ["TeamsScraper"]
