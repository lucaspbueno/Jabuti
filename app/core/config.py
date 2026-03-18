"""Configuração centralizada via variáveis de ambiente e arquivo `.env`."""

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Parâmetros da aplicação carregados do ambiente."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    app_name: str = Field(
        default="Jabuti API",
        description="Nome exibido na documentação OpenAPI",
    )
    environment: str = Field(
        default="development",
        description="Ambiente de execução (ex.: development, staging, production)",
    )
    debug: bool = Field(default=False, description="Modo debug do FastAPI")
    api_prefix: str = Field(default="/api/v1", description="Prefixo das rotas da API")

    database_url: str | None = Field(
        default=None,
        description="URL async do PostgreSQL (etapa posterior)",
    )
    redis_url: str | None = Field(
        default=None,
        description="URL do Redis (etapa posterior)",
    )


@lru_cache
def get_settings() -> Settings:
    """Retorna instância única de settings (cacheada por processo)."""
    return Settings()
