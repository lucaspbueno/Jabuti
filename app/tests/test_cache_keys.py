"""Testes das chaves de cache padronizadas."""

from __future__ import annotations

import uuid

from app.cache import CacheKeys


def test_user_detail_key_pattern() -> None:
    user_id = uuid.uuid4()

    key = CacheKeys.user_detail(user_id)

    assert key == f"users:detail:{user_id}"


def test_users_list_key_pattern() -> None:
    key = CacheKeys.users_list(limit=10, offset=20)

    assert key == "users:list:10:20"
