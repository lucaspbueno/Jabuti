"""Serviço reutilizável de cache JSON com Redis."""

from __future__ import annotations

import json
from typing import Any

from redis.asyncio import Redis

from app.core import Settings


class CacheService:
    """Encapsula operações de cache e serialização JSON."""

    def __init__(self, client: Redis[str], settings: Settings) -> None:
        self._client = client
        self._settings = settings

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
        serialized = json.dumps(value)
        await self._client.set(key, serialized, ex=self._resolve_ttl(ttl_seconds))

    async def delete(self, key: str) -> None:
        await self._client.delete(key)

    async def delete_by_prefix(self, prefix: str) -> int:
        deleted = 0

        async for key in self._client.scan_iter(match=f"{prefix}*"):
            deleted += await self._client.delete(key)

        return deleted

    def _resolve_ttl(self, ttl_seconds: int | None) -> int:
        if ttl_seconds is not None:
            return ttl_seconds

        return self._settings.redis_cache_ttl_seconds
