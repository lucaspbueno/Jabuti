"""Testes unitários do `UserService`."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest

from app.db import UnitOfWork
from app.exceptions import UserEmailAlreadyExistsError, UserNotFoundError
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
from app.security import PasswordHasher
from app.services import UserService


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


def make_repository() -> AsyncMock:
    return AsyncMock()


def make_unit_of_work() -> AsyncMock:
    return AsyncMock(spec=UnitOfWork)


def make_cache() -> AsyncMock:
    return AsyncMock()


def make_service(
    repository: AsyncMock,
    unit_of_work: AsyncMock,
    cache: AsyncMock,
) -> UserService:
    return UserService(repository, unit_of_work, cache, PasswordHasher())


async def test_get_user_by_id_returns_response() -> None:
    repository = make_repository()
    cache = make_cache()
    user = make_user()
    cache.get_json.return_value = None
    repository.get_by_id.return_value = user
    service = make_service(repository, make_unit_of_work(), cache)

    response = await service.get_user_by_id(user.id)

    assert response.id == user.id
    assert response.email == user.email
    repository.get_by_id.assert_awaited_once_with(user.id)


async def test_get_user_by_id_raises_when_user_does_not_exist() -> None:
    repository = make_repository()
    cache = make_cache()
    cache.get_json.return_value = None
    repository.get_by_id.return_value = None
    service = make_service(repository, make_unit_of_work(), cache)
    user_id = uuid.uuid4()

    with pytest.raises(UserNotFoundError):
        await service.get_user_by_id(user_id)


async def test_list_users_returns_paginated_response() -> None:
    repository = make_repository()
    cache = make_cache()
    users = [make_user(email="a@example.com"), make_user(email="b@example.com")]
    cache.get_json.return_value = None
    repository.list_users.return_value = users
    repository.count.return_value = 2
    service = make_service(repository, make_unit_of_work(), cache)

    response = await service.list_users(limit=10, offset=0)

    assert response.total == 2
    assert response.limit == 10
    assert response.offset == 0
    assert len(response.items) == 2
    assert response.items[0].email == "a@example.com"
    assert response.items[1].email == "b@example.com"
    repository.list_users.assert_awaited_once_with(limit=10, offset=0)
    repository.count.assert_awaited_once_with()


async def test_create_user_raises_when_email_already_exists() -> None:
    repository = make_repository()
    cache = make_cache()
    payload = UserCreate(
        name="Lucas",
        email="lucas@example.com",
        password="senha-segura",
    )
    repository.get_by_email.return_value = make_user(email="lucas@example.com")
    service = make_service(repository, make_unit_of_work(), cache)

    with pytest.raises(UserEmailAlreadyExistsError):
        await service.create_user(payload)


async def test_create_user_raises_when_email_exists_even_if_soft_deleted() -> None:
    repository = make_repository()
    cache = make_cache()
    payload = UserCreate(
        name="Lucas",
        email="lucas@example.com",
        password="senha-segura",
    )
    existing = make_user(email="lucas@example.com")
    existing.deleted_at = datetime.now(UTC)
    repository.get_by_email.return_value = existing
    service = make_service(repository, make_unit_of_work(), cache)

    with pytest.raises(UserEmailAlreadyExistsError):
        await service.create_user(payload)


async def test_create_user_creates_and_returns_response() -> None:
    repository = make_repository()
    unit_of_work = make_unit_of_work()
    cache = make_cache()
    payload = UserCreate(
        name="Lucas",
        email="lucas@example.com",
        password="senha-segura",
    )
    created_user = make_user(email="lucas@example.com")
    repository.get_by_email.return_value = None
    repository.create.return_value = created_user
    service = make_service(repository, unit_of_work, cache)

    response = await service.create_user(payload)

    assert response.id == created_user.id
    repository.create.assert_awaited_once()
    create_kwargs = repository.create.await_args.kwargs
    assert create_kwargs["name"] == payload.name
    assert create_kwargs["email"] == "lucas@example.com"
    assert create_kwargs["password"] != payload.password
    assert create_kwargs["password"].startswith("$2")
    unit_of_work.commit.assert_awaited_once()


async def test_update_user_raises_when_user_does_not_exist() -> None:
    repository = make_repository()
    cache = make_cache()
    cache.get_json.return_value = None
    repository.get_by_id.return_value = None
    service = make_service(repository, make_unit_of_work(), cache)

    with pytest.raises(UserNotFoundError):
        await service.update_user(uuid.uuid4(), UserUpdate(name="Novo nome"))


async def test_update_user_raises_when_email_is_used_by_other_user() -> None:
    repository = make_repository()
    cache = make_cache()
    current_user = make_user(email="lucas@example.com")
    other_user = make_user(email="outro@example.com")
    repository.get_by_id.return_value = current_user
    repository.get_by_email.return_value = other_user
    service = make_service(repository, make_unit_of_work(), cache)

    with pytest.raises(UserEmailAlreadyExistsError):
        await service.update_user(
            current_user.id,
            UserUpdate(email="outro@example.com"),
        )


async def test_update_user_updates_and_returns_response() -> None:
    repository = make_repository()
    unit_of_work = make_unit_of_work()
    cache = make_cache()
    current_user = make_user(email="lucas@example.com")
    updated_user = make_user(email="novo@example.com")
    updated_user.id = current_user.id
    repository.get_by_id.return_value = current_user
    repository.get_by_email.return_value = None
    repository.update.return_value = updated_user
    service = make_service(repository, unit_of_work, cache)

    response = await service.update_user(
        current_user.id,
        UserUpdate(name="Novo nome", email="novo@example.com", active=False),
    )

    assert response.id == current_user.id
    assert response.email == "novo@example.com"
    repository.update.assert_awaited_once_with(
        current_user,
        name="Novo nome",
        email="novo@example.com",
        password=None,
        active=False,
    )
    unit_of_work.commit.assert_awaited_once()


async def test_update_user_hashes_password_when_informed() -> None:
    repository = make_repository()
    unit_of_work = make_unit_of_work()
    cache = make_cache()
    current_user = make_user(email="lucas@example.com")
    repository.get_by_id.return_value = current_user
    repository.update.return_value = current_user
    service = make_service(repository, unit_of_work, cache)

    await service.update_user(
        current_user.id,
        UserUpdate(password="nova-senha-segura"),
    )

    repository.update.assert_awaited_once()
    update_kwargs = repository.update.await_args.kwargs
    assert update_kwargs["password"] != "nova-senha-segura"
    assert update_kwargs["password"].startswith("$2")
    unit_of_work.commit.assert_awaited_once()


async def test_delete_user_raises_when_user_does_not_exist() -> None:
    repository = make_repository()
    cache = make_cache()
    repository.get_by_id.return_value = None
    service = make_service(repository, make_unit_of_work(), cache)

    with pytest.raises(UserNotFoundError):
        await service.delete_user(uuid.uuid4())


async def test_delete_user_returns_deleted_response() -> None:
    repository = make_repository()
    unit_of_work = make_unit_of_work()
    cache = make_cache()
    user = make_user()
    user.active = False
    repository.get_by_id.return_value = user
    repository.delete.return_value = user
    service = make_service(repository, unit_of_work, cache)

    response = await service.delete_user(user.id)

    assert response.id == user.id
    assert response.active is False
    repository.delete.assert_awaited_once_with(user)
    unit_of_work.commit.assert_awaited_once()
