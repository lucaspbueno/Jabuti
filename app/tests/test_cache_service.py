"""Testes unitários da camada de cache."""

from __future__ import annotations

from collections.abc import AsyncIterator
from unittest.mock import AsyncMock, Mock

from redis.asyncio import Redis

from app.cache import CacheService
from app.core import Settings


def make_settings() -> Settings:
    return Settings(
        database_url="postgresql+asyncpg://jabuti:jabuti@localhost:5432/jabuti",
        redis_url="redis://localhost:6379/0",
        redis_cache_ttl_seconds=300,
    )


def make_client() -> AsyncMock:
    client = AsyncMock(spec=Redis)
    client.get = AsyncMock()
    client.set = AsyncMock()
    client.delete = AsyncMock()
    client.scan_iter = Mock()
    return client


async def test_get_json_returns_none_when_key_is_missing() -> None:
    client = make_client()
    client.get.return_value = None
    service = CacheService(client, make_settings())

    value = await service.get_json("users:detail:1")

    assert value is None
    client.get.assert_awaited_once_with("users:detail:1")


async def test_get_json_deserializes_json_payload() -> None:
    client = make_client()
    client.get.return_value = '{"data":{"name":"Lucas","email":"lucas@example.com"}}'
    service = CacheService(client, make_settings())

    value = await service.get_json("users:detail:1")

    assert value == {
        "data": {"name": "Lucas", "email": "lucas@example.com"},
    }


async def test_get_json_returns_none_for_non_object_json() -> None:
    client = make_client()
    client.get.return_value = '[{"email":"lucas@example.com"}]'
    service = CacheService(client, make_settings())

    value = await service.get_json("users:list:10:0")

    assert value is None


async def test_set_json_uses_default_ttl_when_not_informed() -> None:
    client = make_client()
    service = CacheService(client, make_settings())

    await service.set_json(
        "users:list:10:0",
        {"data": [{"email": "lucas@example.com"}]},
    )

    client.set.assert_awaited_once_with(
        "users:list:10:0",
        '{"data": [{"email": "lucas@example.com"}]}',
        ex=300,
    )


async def test_set_json_uses_explicit_ttl_when_informed() -> None:
    client = make_client()
    service = CacheService(client, make_settings())

    await service.set_json(
        "users:detail:1",
        {"email": "lucas@example.com"},
        ttl_seconds=60,
    )

    client.set.assert_awaited_once_with(
        "users:detail:1",
        '{"email": "lucas@example.com"}',
        ex=60,
    )


async def test_delete_removes_single_key() -> None:
    client = make_client()
    service = CacheService(client, make_settings())

    await service.delete("users:detail:1")

    client.delete.assert_awaited_once_with("users:detail:1")


async def test_delete_by_prefix_removes_all_matching_keys() -> None:
    client = make_client()
    service = CacheService(client, make_settings())

    async def scan_keys() -> AsyncIterator[str]:
        yield "users:list:10:0"
        yield "users:list:10:10"

    client.scan_iter.return_value = scan_keys()
    client.delete.side_effect = [1, 1]

    deleted = await service.delete_by_prefix("users:list:")

    assert deleted == 2
    client.scan_iter.assert_called_once_with(match="users:list:*")
    assert client.delete.await_count == 2
