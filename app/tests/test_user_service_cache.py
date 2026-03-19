"""Testes da integração de cache na `UserService`."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from unittest.mock import AsyncMock

from app.db import UnitOfWork
from app.models import User
from app.schemas.user import UserCreate, UserUpdate
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


async def test_get_user_by_id_returns_cached_value_without_hitting_repository() -> None:
    repository = make_repository()
    cache = make_cache()
    user = make_user()
    cache.get_json.return_value = {
        "id": str(user.id),
        "name": user.name,
        "email": user.email,
        "active": user.active,
        "created_at": user.created_at.isoformat(),
        "updated_at": user.updated_at.isoformat(),
    }
    service = UserService(repository, make_unit_of_work(), cache)

    response = await service.get_user_by_id(user.id)

    assert response.id == user.id
    repository.get_by_id.assert_not_awaited()


async def test_get_user_by_id_caches_response_on_cache_miss() -> None:
    repository = make_repository()
    cache = make_cache()
    user = make_user()
    cache.get_json.return_value = None
    repository.get_by_id.return_value = user
    service = UserService(repository, make_unit_of_work(), cache)

    response = await service.get_user_by_id(user.id)

    assert response.id == user.id
    repository.get_by_id.assert_awaited_once_with(user.id)
    cache.set_json.assert_awaited_once()


async def test_list_users_returns_cached_payload_without_querying_repository() -> None:
    repository = make_repository()
    cache = make_cache()
    user = make_user()
    cache.get_json.return_value = {
        "items": [
            {
                "id": str(user.id),
                "name": user.name,
                "email": user.email,
                "active": user.active,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }
        ],
        "total": 1,
        "limit": 10,
        "offset": 0,
    }
    service = UserService(repository, make_unit_of_work(), cache)

    response = await service.list_users(limit=10, offset=0)

    assert response.total == 1
    assert len(response.items) == 1
    repository.list_users.assert_not_awaited()
    repository.count.assert_not_awaited()


async def test_list_users_caches_response_on_cache_miss() -> None:
    repository = make_repository()
    cache = make_cache()
    users = [make_user(email="a@example.com"), make_user(email="b@example.com")]
    cache.get_json.return_value = None
    repository.list_users.return_value = users
    repository.count.return_value = 2
    service = UserService(repository, make_unit_of_work(), cache)

    response = await service.list_users(limit=10, offset=5)

    assert response.total == 2
    assert len(response.items) == 2
    cache.set_json.assert_awaited_once()


async def test_create_user_commits_then_invalidates_list_cache() -> None:
    repository = make_repository()
    unit_of_work = make_unit_of_work()
    cache = make_cache()
    user = make_user()
    repository.get_by_email.return_value = None
    repository.create.return_value = user
    service = UserService(repository, unit_of_work, cache)

    call_order: list[str] = []
    unit_of_work.commit.side_effect = lambda: call_order.append("commit")
    cache.delete_by_prefix.side_effect = lambda *_: call_order.append("invalidate_list")

    await service.create_user(
        UserCreate(
            name="Lucas",
            email="lucas@example.com",
            password="senha-segura",
        )
    )

    unit_of_work.commit.assert_awaited_once()
    cache.delete_by_prefix.assert_awaited_once_with("users:list:")
    assert call_order == ["commit", "invalidate_list"]


async def test_update_user_commits_then_invalidates_detail_and_list_cache() -> None:
    repository = make_repository()
    unit_of_work = make_unit_of_work()
    cache = make_cache()
    user = make_user()
    updated_user = make_user(email="novo@example.com")
    updated_user.id = user.id
    repository.get_by_id.return_value = user
    repository.get_by_email.return_value = None
    repository.update.return_value = updated_user
    service = UserService(repository, unit_of_work, cache)

    call_order: list[str] = []
    unit_of_work.commit.side_effect = lambda: call_order.append("commit")
    cache.delete.side_effect = lambda *_: call_order.append("invalidate_detail")
    cache.delete_by_prefix.side_effect = lambda *_: call_order.append("invalidate_list")

    await service.update_user(
        user.id,
        UserUpdate(name="Novo nome", email="novo@example.com"),
    )

    unit_of_work.commit.assert_awaited_once()
    cache.delete.assert_awaited_once_with(f"users:detail:{user.id}")
    cache.delete_by_prefix.assert_awaited_once_with("users:list:")
    assert call_order == ["commit", "invalidate_detail", "invalidate_list"]


async def test_delete_user_commits_then_invalidates_detail_and_list_cache() -> None:
    repository = make_repository()
    unit_of_work = make_unit_of_work()
    cache = make_cache()
    user = make_user()
    user.active = False
    repository.get_by_id.return_value = user
    repository.delete.return_value = user
    service = UserService(repository, unit_of_work, cache)

    call_order: list[str] = []
    unit_of_work.commit.side_effect = lambda: call_order.append("commit")
    cache.delete.side_effect = lambda *_: call_order.append("invalidate_detail")
    cache.delete_by_prefix.side_effect = lambda *_: call_order.append("invalidate_list")

    await service.delete_user(user.id)

    unit_of_work.commit.assert_awaited_once()
    cache.delete.assert_awaited_once_with(f"users:detail:{user.id}")
    cache.delete_by_prefix.assert_awaited_once_with("users:list:")
    assert call_order == ["commit", "invalidate_detail", "invalidate_list"]
