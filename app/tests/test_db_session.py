"""Testes da infraestrutura de banco (sem model de domínio)."""

import pytest

from app.core import Settings
from app.db.config import DatabaseConfig
from app.db.session import DatabaseSessionManager


def test_database_config_requires_url() -> None:
    settings = Settings(database_url=None)
    with pytest.raises(ValueError):
        DatabaseConfig(settings)


def test_database_config_uses_url_from_settings() -> None:
    url = "postgresql+asyncpg://user:pass@localhost:5432/db"
    settings = Settings(database_url=url)
    config = DatabaseConfig(settings)
    assert config.url == url


@pytest.mark.asyncio
async def test_session_manager_initializes_engine_and_session_factory() -> None:
    url = "postgresql+asyncpg://user:pass@localhost:5432/db"
    settings = Settings(database_url=url)
    config = DatabaseConfig(settings)
    manager = DatabaseSessionManager(config)

    engine = manager.engine
    session_factory = manager.session_factory

    assert engine is not None
    assert session_factory is not None


@pytest.mark.asyncio
async def test_session_context_yields_and_closes_session() -> None:
    url = "postgresql+asyncpg://user:pass@localhost:5432/db"
    settings = Settings(database_url=url)
    config = DatabaseConfig(settings)
    manager = DatabaseSessionManager(config)

    async def _use_session() -> None:
        async with manager.session() as session:
            assert session.is_active

    await _use_session()
