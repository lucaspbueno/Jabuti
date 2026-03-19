"""Cliente Redis async reutilizável."""

from __future__ import annotations

from redis.asyncio import Redis

from app.cache.config import RedisConfig

class RedisClient:
    """Cliente Redis async reutilizável."""

    def __init__(self, settings: RedisConfig) -> None:
        self._redis_client = Redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True,
        )
        self._ttl_seconds = settings.redis_cache_ttl_seconds

    @property
    def client(self) -> Redis[str]:
        return self._redis_client

    async def close(self) -> None:
        await self._redis_client.close()

    @property
    def ttl_seconds(self) -> int:
        return self._ttl_seconds
