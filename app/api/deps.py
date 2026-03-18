"""Dependências injetáveis nas rotas FastAPI."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheService, get_redis_client
from app.core.config import Settings, get_settings
from app.db.session import get_database_session_manager
from app.repositories import UserRepository
from app.services import UserService
from app.services.system_health_service import SystemHealthService


def get_system_health_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> SystemHealthService:
    return SystemHealthService(settings)


def get_cache_service(
    settings: Annotated[Settings, Depends(get_settings)],
) -> CacheService:
    """Cria serviço de cache reutilizável com Redis."""

    return CacheService(get_redis_client(), settings)


async def get_read_db_session() -> AsyncIterator[AsyncSession]:
    """Fornece sessão somente para leitura, sem commit automático."""

    session_manager = get_database_session_manager()

    async with session_manager.session() as session:
        yield session


async def get_write_db_session() -> AsyncIterator[AsyncSession]:
    """Fornece sessão transacional para operações de escrita."""

    session_manager = get_database_session_manager()

    async with session_manager.session() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


def get_read_user_repository(
    session: Annotated[AsyncSession, Depends(get_read_db_session)],
) -> UserRepository:
    """Cria repositório de usuário com sessão de leitura."""

    return UserRepository(session)


def get_write_user_repository(
    session: Annotated[AsyncSession, Depends(get_write_db_session)],
) -> UserRepository:
    """Cria repositório de usuário com sessão transacional."""

    return UserRepository(session)


def get_read_user_service(
    repository: Annotated[UserRepository, Depends(get_read_user_repository)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
) -> UserService:
    """Cria service de usuário para operações de leitura."""

    return UserService(repository, cache_service)


def get_write_user_service(
    repository: Annotated[UserRepository, Depends(get_write_user_repository)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
) -> UserService:
    """Cria service de usuário para operações de escrita."""

    return UserService(repository, cache_service)
