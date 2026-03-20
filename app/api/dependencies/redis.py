"""Dependências de infraestrutura reutilizadas pela camada HTTP."""

from __future__ import annotations

from typing import cast

from fastapi import Depends, Request

from app.cache import CacheService, RedisClient


class RedisDependencies:
    """Concentra composição de dependências da feature de Redis."""

    @staticmethod
    def _get_redis_client(request: Request) -> RedisClient:
        redis = cast(RedisClient | None, request.app.state.redis)

        if redis is None:
            raise ValueError("REDIS_URL não configurada nas settings.")

        return redis

    @staticmethod
    def get_cache_service(client: RedisClient = Depends(_get_redis_client)) -> CacheService:
        return CacheService(client)
