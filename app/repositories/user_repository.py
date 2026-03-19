"""Repository da feature de usuário."""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User


class UserRepository:
    """Centraliza o acesso persistente da entidade `User`."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: uuid.UUID) -> User | None:
        # fmt: off
        statement = (
            select(User)
            .where(
                User.id == user_id,
                User.deleted_at.is_(None),
            )
        )
        # fmt: on
        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        # fmt: off
        statement = (
            select(User)
            .where(
                User.email == email,
            )
        )
        # fmt: on
        result = await self._session.execute(statement)

        return result.scalar_one_or_none()

    async def list_users(self, *, limit: int, offset: int) -> list[User]:
        # fmt: off
        statement = (
            select(User)
            .where(User.deleted_at.is_(None))
            .order_by(User.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        # fmt: on
        result = await self._session.execute(statement)

        return list(result.scalars().all())

    async def count(self) -> int:
        # fmt: off
        statement = (
            select(func.count())
            .select_from(User)
            .where(User.deleted_at.is_(None))
        )
        # fmt: on
        result = await self._session.execute(statement)

        return int(result.scalar_one())

    async def create(self, *, name: str, email: str, password: str) -> User:
        user = User(name=name, email=email, password=password)

        self._session.add(user)

        await self._session.flush()
        await self._session.refresh(user)

        return user

    async def update(
        self,
        user: User,
        *,
        name: str | None = None,
        email: str | None = None,
        password: str | None = None,
        active: bool | None = None,
    ) -> User:
        updates: dict[str, object | None] = {
            "name": name,
            "email": email,
            "password": password,
            "active": active,
        }

        for key, value in updates.items():
            if value is not None:
                setattr(user, key, value)

        await self._session.flush()
        await self._session.refresh(user)

        return user

    async def delete(self, user: User) -> User:
        user.deleted_at = datetime.now(UTC)
        user.active = False

        await self._session.flush()
        await self._session.refresh(user)

        return user
