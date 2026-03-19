"""Testes das dependências de sessão da API."""

from __future__ import annotations

from collections.abc import AsyncGenerator, AsyncIterator
from contextlib import asynccontextmanager
from typing import cast
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api import deps


class FakeSessionManager:
    """Expõe um contexto de sessão controlado para os testes."""

    def __init__(self, session: AsyncMock) -> None:
        self._session = session

    @asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncMock]:
        yield self._session


@pytest.mark.asyncio
async def test_get_db_session_does_not_commit_on_success(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = AsyncMock()
    manager = FakeSessionManager(session)
    monkeypatch.setattr(deps, "get_database_session_manager", lambda: manager)

    session_generator = cast(
        AsyncGenerator[AsyncSession, None],
        deps.get_db_session(),
    )

    yielded_session = await anext(session_generator)

    assert yielded_session is session

    with pytest.raises(StopAsyncIteration):
        await anext(session_generator)

    session.commit.assert_not_awaited()
    session.rollback.assert_not_awaited()


@pytest.mark.asyncio
async def test_get_db_session_rolls_back_on_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    session = AsyncMock()
    manager = FakeSessionManager(session)
    monkeypatch.setattr(deps, "get_database_session_manager", lambda: manager)

    session_generator = cast(
        AsyncGenerator[AsyncSession, None],
        deps.get_db_session(),
    )

    yielded_session = await anext(session_generator)

    assert yielded_session is session

    with pytest.raises(RuntimeError, match="falha"):
        await session_generator.athrow(RuntimeError("falha"))

    session.commit.assert_not_awaited()
    session.rollback.assert_awaited_once()
