"""Configuração de engine e sessão async do banco."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.config import DatabaseConfig


class Database:
    """Encapsula a conexão com o banco de dados."""

    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._engine = create_async_engine(self._config.url, echo=self._config.debug)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        """Fornece sessão com rollback em caso de erro"""

        session = self._session_factory()

        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    async def close(self) -> None:
        """Fecha a conexão com o banco de dados."""

        await self._engine.dispose()
