"""Configuração de engine e sessão async do banco."""

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from app.db.config import DatabaseConfig


class DatabaseSessionManager:
    """Gerencia a engine e o factory de sessões assíncronas."""

    def __init__(self, config: DatabaseConfig) -> None:
        self._config = config
        self._engine: AsyncEngine | None = None
        self._session_factory: async_sessionmaker[AsyncSession] | None = None

    def init_engine(self) -> None:
        if self._engine is not None:
            return
        self._engine = create_async_engine(self._config.url, echo=False)
        self._session_factory = async_sessionmaker(
            self._engine,
            expire_on_commit=False,
        )

    @property
    def engine(self) -> AsyncEngine:
        if self._engine is None:
            self.init_engine()
        assert self._engine is not None
        return self._engine

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        if self._session_factory is None:
            self.init_engine()
        assert self._session_factory is not None
        return self._session_factory

    async def session(self) -> AsyncIterator[AsyncSession]:
        """Fornece uma sessão async para uso em contextos async/await."""

        session = self.session_factory()
        try:
            yield session
        finally:
            await session.close()

