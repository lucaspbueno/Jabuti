"""Dependências injetáveis nas rotas FastAPI."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import Settings, get_settings
from app.db.session import get_database_session_manager
from app.repositories import UserRepository
from app.services import UserService
from app.services.system_health_service import SystemHealthService


def get_system_health_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SystemHealthService:
    return SystemHealthService(settings)


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Fornece sessão transacional por requisição."""

    session_manager = get_database_session_manager()

    async with session_manager.session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepository:
    return UserRepository(session)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
) -> UserService:
    return UserService(repository)
