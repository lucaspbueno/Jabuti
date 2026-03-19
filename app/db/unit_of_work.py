"""Abstração mínima de transação para a aplicação."""

from sqlalchemy.ext.asyncio import AsyncSession


class UnitOfWork:
    """Encapsula operações transacionais da sessão atual."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def commit(self) -> None:
        await self._session.commit()

    async def rollback(self) -> None:
        await self._session.rollback()
