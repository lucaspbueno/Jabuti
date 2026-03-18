"""Cliente Redis async reutilizável."""

from __future__ import annotations

from functools import lru_cache

from redis.asyncio import Redis

from app.core import get_settings


@lru_cache
def get_redis_client() -> Redis[str]:
    """Retorna uma instância singleton do cliente Redis async."""

    settings = get_settings()

    if settings.redis_url is None:
        raise ValueError("REDIS_URL não configurada nas settings.")

    return Redis.from_url(
        settings.redis_url,
        encoding="utf-8",
        decode_responses=True,
    )


async def close_redis_client() -> None:
    """Fecha o cliente Redis reutilizado, se ele já tiver sido criado."""

    try:
        client = get_redis_client()
    except ValueError:
        return

    try:
        close_method = getattr(client, "aclose", None)

        if close_method is None:
            close_method = client.close

        await close_method()
    finally:
        get_redis_client.cache_clear()
