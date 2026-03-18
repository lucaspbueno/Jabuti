"""Configuração de engine e sessão async do banco."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.core import get_settings
from app.db.config import DatabaseConfig


class DatabaseSessionManager:
    """Gerencia a engine e o factory de sessões assíncronas."""

    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._engine = create_async_engine(self._config.url, echo=self._config.debug)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    @property
    def engine(self) -> AsyncEngine:
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Fornece uma sessão async para uso em contextos async/await."""

        session = self.session_factory()

        try:
            yield session
        finally:
            await session.close()


@lru_cache
def get_database_session_manager() -> DatabaseSessionManager:
    """Retorna uma instância singleton do gerenciador de sessão."""

    config = DatabaseConfig(get_settings())

    return DatabaseSessionManager(config)
