"""Contrato do repositório de usuário."""

from __future__ import annotations

import uuid
from typing import Protocol

from app.models import User


class UserRepositoryInterface(Protocol):
    """Contrato mínimo esperado de um repositório de usuário."""

    async def get_by_id(self, user_id: uuid.UUID) -> User | None: ...

    async def get_by_email(self, email: str) -> User | None: ...

    async def list_users(self, *, limit: int, offset: int) -> list[User]: ...

    async def count(self) -> int: ...

    async def create(self, *, name: str, email: str, password: str) -> User: ...

    async def update(
        self,
        user: User,
        *,
        name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        active: bool | None = None,
    ) -> User: ...

    async def delete(self, user: User) -> User: ...
