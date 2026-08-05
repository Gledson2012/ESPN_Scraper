from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """Configurações da aplicação."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Banco de dados
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/fbref_scraper"

    # API
    API_V1_PREFIX: str = "/api/v1"
    PROJECT_NAME: str = "FBref Scraper"
    VERSION: str = "1.1.0"
    APP_DEBUG: bool = True

    # Scraping
    REQUEST_TIMEOUT: int = 30
    REQUEST_DELAY: float = 1.0  # Segundos entre requisições
    USER_AGENT: str = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Cache
    CACHE_ENABLED: bool = True
    CACHE_TTL_SECONDS: int = 3600

    # Cloudbet API
    CLOUDBET_API_KEY: str = ""
    CLOUDBET_BASE_URL: str = "https://sports-api.cloudbet.com/v2"


settings = Settings()