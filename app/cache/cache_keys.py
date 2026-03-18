"""Padronização de chaves de cache da aplicação."""

from __future__ import annotations

import uuid


class CacheKeys:
    """Centraliza a geração de chaves de cache."""

    @staticmethod
    def user_detail(user_id: uuid.UUID) -> str:
        return f"users:detail:{user_id}"

    @staticmethod
    def users_list(limit: int, offset: int) -> str:
        return f"users:list:{limit}:{offset}"
