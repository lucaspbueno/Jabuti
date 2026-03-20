"""Dependências de composição da feature de usuários."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies.redis import RedisDependencies
from app.db import UnitOfWork, get_db_session
from app.interfaces import (
    CacheServiceInterface,
    PasswordHasherInterface,
    UnitOfWorkInterface,
    UserRepositoryInterface,
)
from app.repositories import UserRepository
from app.security import PasswordHasher
from app.services.user_service import UserService


class UserDependencies:
    """Concentra composição de dependências da feature de usuários."""

    @staticmethod
    def _get_repository(
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> UserRepository:
        return UserRepository(session)

    @staticmethod
    def _get_unit_of_work(
        session: Annotated[AsyncSession, Depends(get_db_session)],
    ) -> UnitOfWork:
        return UnitOfWork(session)

    @staticmethod
    def _get_cache_service(
        cache_service: Annotated[CacheServiceInterface, Depends(RedisDependencies.get_cache_service)],
    ) -> CacheServiceInterface:
        return cache_service

    @staticmethod
    def _get_password_hasher(
        password_hasher: Annotated[PasswordHasherInterface, Depends(PasswordHasher)],
    ) -> PasswordHasherInterface:
        return password_hasher

    @staticmethod
    def get_service(
        repository: Annotated[UserRepositoryInterface, Depends(_get_repository)],
        unit_of_work: Annotated[UnitOfWorkInterface, Depends(_get_unit_of_work)],
        cache_service: Annotated[CacheServiceInterface, Depends(_get_cache_service)],
        password_hasher: Annotated[PasswordHasherInterface, Depends(_get_password_hasher)],
    ) -> UserService:
        return UserService(repository, unit_of_work, cache_service, password_hasher)
