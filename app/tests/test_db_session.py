"""Testes da infraestrutura de banco (sem model de domínio)."""

import pytest

from app.core import Settings
from app.db import Database, DatabaseConfig


def test_database_config_uses_url_from_settings() -> None:
    url = "postgresql+asyncpg://user:pass@localhost:5432/db"
    settings = Settings(
        database_url=url,
        redis_url="redis://localhost:6379/0",
    )
    config = DatabaseConfig(settings)
    assert config.url == url


@pytest.mark.asyncio
async def test_session_context_yields_and_closes_session() -> None:
    url = "postgresql+asyncpg://user:pass@localhost:5432/db"
    settings = Settings(
        database_url=url,
        redis_url="redis://localhost:6379/0",
    )
    config = DatabaseConfig(settings)
    database = Database(config)

    async def _use_session() -> None:
        async with database.session() as session:
            assert session.is_active

    await _use_session()
