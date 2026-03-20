"""Dependências de infraestrutura reutilizadas pela camada HTTP."""

from __future__ import annotations

from typing import Annotated, cast

from fastapi import Depends, Request

from app.cache import CacheService, RedisClient


def _get_redis_client(request: Request) -> RedisClient:
    redis = cast(RedisClient | None, request.app.state.redis)

    if redis is None:
        raise ValueError("REDIS_URL não configurada nas settings.")

    return redis


def get_cache_service(
    client: Annotated[RedisClient, Depends(_get_redis_client)],
) -> CacheService:
    """Monta o CacheService. Deve ser função de módulo: `@staticmethod` não aplica `Depends` no FastAPI."""

    return CacheService(client)
