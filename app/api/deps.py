"""Dependências de composição para as rotas FastAPI."""

from typing import Annotated, cast

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.cache import CacheService, RedisClient
from app.db import UnitOfWork, get_db_session
from app.repositories import UserRepository
from app.security import PasswordHasher
from app.services import UserService


def get_redis_client(request: Request) -> RedisClient:
    redis = cast(RedisClient | None, request.app.state.redis)

    if redis is None:
        raise ValueError("REDIS_URL não configurada nas settings.")

    return redis


def get_cache_service(client: RedisClient = Depends(get_redis_client)) -> CacheService:
    return CacheService(client)


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


def get_password_hasher() -> PasswordHasher:
    """Cria utilitário de hash de senha."""

    return PasswordHasher()


def get_user_service(
    repository: Annotated[UserRepository, Depends(get_user_repository)],
    unit_of_work: Annotated[UnitOfWork, Depends(get_unit_of_work)],
    cache_service: Annotated[CacheService, Depends(get_cache_service)],
    password_hasher: Annotated[PasswordHasher, Depends(get_password_hasher)],
) -> UserService:
    """Cria service de usuário."""

    return UserService(repository, unit_of_work, cache_service, password_hasher)
