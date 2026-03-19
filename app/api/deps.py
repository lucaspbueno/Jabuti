"""Dependências injetáveis nas rotas FastAPI."""

from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheService, get_redis_client
from app.core.config import Settings, get_settings
from app.db import UnitOfWork
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


async def get_db_session() -> AsyncIterator[AsyncSession]:
    """Fornece sessão com proteção de rollback para leitura e escrita."""

    session_manager = get_database_session_manager()

    async with session_manager.session() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def get_user_repository(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UserRepository:
    """Cria repositório de usuário."""

    return UserRepository(session)


def get_unit_of_work(
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UnitOfWork:
    """Cria unidade de trabalho da requisição atual."""

    return UnitOfWork(session)


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
) -> UserService:
    """Cria service de usuário."""

    return UserService(repository, unit_of_work, cache_service)
