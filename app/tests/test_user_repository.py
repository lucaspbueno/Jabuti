"""Testes unitários do `UserRepository`."""

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock, Mock

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import User
from app.repositories import UserRepository


def make_user(*, email: str = "lucas@example.com") -> User:
    now = datetime.now(UTC)
    return User(
        id=uuid.uuid4(),
        name="Lucas",
        email=email,
        password="hashed-password",
        active=True,
        created_at=now,
        updated_at=now,
    )


def make_session() -> Mock:
    session = Mock(spec=AsyncSession)
    session.execute = AsyncMock()
    session.flush = AsyncMock()
    session.refresh = AsyncMock()
    session.delete = AsyncMock()
    return session


async def test_get_by_id_returns_user_when_found() -> None:
    session = make_session()
    user = make_user()
    result = Mock()
    result.scalar_one_or_none.return_value = user
    session.execute.return_value = result

    repository = UserRepository(session)

    found = await repository.get_by_id(user.id)

    assert found is user
    session.execute.assert_awaited_once()


async def test_get_by_email_returns_user_when_found() -> None:
    session = make_session()
    user = make_user()
    result = Mock()
    result.scalar_one_or_none.return_value = user
    session.execute.return_value = result

    repository = UserRepository(session)

    found = await repository.get_by_email(user.email)

    assert found is user
    session.execute.assert_awaited_once()


async def test_list_users_returns_paginated_collection() -> None:
    session = make_session()
    users = [make_user(email="a@example.com"), make_user(email="b@example.com")]
    scalars = Mock()
    scalars.all.return_value = users
    result = Mock()
    result.scalars.return_value = scalars
    session.execute.return_value = result

    repository = UserRepository(session)

    found = await repository.list_users(limit=10, offset=20)

    assert found == users
    session.execute.assert_awaited_once()


async def test_count_returns_total_users() -> None:
    session = make_session()
    result = Mock()
    result.scalar_one.return_value = 7
    session.execute.return_value = result

    repository = UserRepository(session)

    total = await repository.count()

    assert total == 7
    session.execute.assert_awaited_once()


async def test_create_adds_flushes_refreshes_and_returns_user() -> None:
    session = make_session()
    repository = UserRepository(session)

    user = await repository.create(
        name="Lucas",
        email="lucas@example.com",
        password="hashed-password",
    )

    assert isinstance(user, User)
    assert user.name == "Lucas"
    assert user.email == "lucas@example.com"
    session.add.assert_called_once_with(user)
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)


async def test_update_changes_only_informed_fields() -> None:
    session = make_session()
    repository = UserRepository(session)
    user = make_user()
    original_password = user.password

    updated = await repository.update(
        user,
        name="Novo Nome",
        active=False,
    )

    assert updated is user
    assert user.name == "Novo Nome"
    assert user.active is False
    assert user.password == original_password
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)


async def test_delete_soft_deletes_user_and_flushes() -> None:
    session = make_session()
    repository = UserRepository(session)
    user = make_user()

    deleted = await repository.delete(user)

    assert deleted is user
    assert user.active is False
    assert user.deleted_at is not None
    session.flush.assert_awaited_once()
    session.refresh.assert_awaited_once_with(user)
