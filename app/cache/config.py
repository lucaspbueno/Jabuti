from app.core import Settings


class RedisConfig:
    def __init__(self, settings: Settings) -> None:
        self._redis_url = settings.redis_url
        self._redis_cache_ttl_seconds = settings.redis_cache_ttl_seconds

    @property
    def redis_url(self) -> str:
        return self._redis_url

    @property
    def redis_cache_ttl_seconds(self) -> int:
        return self._redis_cache_ttl_seconds
