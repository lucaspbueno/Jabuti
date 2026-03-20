"""Dependências de banco reutilizáveis para a aplicação."""

from collections.abc import AsyncIterator
from typing import cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.db import Database


def get_db(request: Request) -> Database:
    """Obtém o banco de dados anexado ao estado da aplicação."""

    db = cast(Database | None, request.app.state.db)

    if db is None:
        raise ValueError("DATABASE_URL não configurada nas settings.")

    return db


async def get_db_session(db: Database = Depends(get_db)) -> AsyncIterator[AsyncSession]:
    async with db.session() as session:
        yield session
