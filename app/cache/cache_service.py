"""Serviço reutilizável de cache JSON com Redis."""

from __future__ import annotations

import json
from typing import Any

from app.cache.redis_client import RedisClient


class CacheService:
    """Encapsula operações de cache e serialização JSON."""

    def __init__(self, redis_client: RedisClient) -> None:
        self._client = redis_client.client
        self._ttl_seconds = redis_client.ttl_seconds

    async def get_json(self, key: str) -> dict[str, Any] | None:
        cached_value = await self._client.get(key)

        if cached_value is None:
            return None

        value = json.loads(cached_value)

        if not isinstance(value, dict):
            return None

        return value

    async def set_json(
        self,
        key: str,
        value: dict[str, Any],
        *,
        ttl_seconds: int | None = None,
    ) -> None:
        serialized_data = json.dumps(value)
        expiration_seconds = ttl_seconds or self._ttl_seconds

        await self._client.set(key, serialized_data, ex=expiration_seconds)

    async def delete(self, key: str) -> int:
        return await self._client.delete(key)

    async def delete_by_prefix(self, prefix: str) -> int:
        deleted = 0

        async for key in self._client.scan_iter(match=f"{prefix}*"):
            deleted += await self._client.delete(key)

        return deleted
