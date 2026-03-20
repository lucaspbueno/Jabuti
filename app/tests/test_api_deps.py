"""Testes das dependências de composição da API."""

from __future__ import annotations

from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from fastapi import FastAPI
from starlette.requests import Request

from app.api.dependencies.redis import RedisDependencies
from app.api.dependencies.users import UserDependencies
from app.cache import CacheService
from app.db import UnitOfWork
from app.repositories import UserRepository
from app.security import PasswordHasher


def test_get_redis_client_returns_client_from_app_state() -> None:
    app = FastAPI()
    redis_client = Mock()
    app.state.redis = redis_client
    request = Request(
        scope={
            "type": "http",
            "app": app,
            "method": "GET",
            "path": "/",
            "headers": [],
            "query_string": b"",
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "scheme": "http",
            "http_version": "1.1",
        }
    )

    result = RedisDependencies._get_redis_client(request)

    assert result is redis_client


def test_get_redis_client_raises_when_redis_is_missing() -> None:
    app = FastAPI()
    app.state.redis = None
    request = Request(
        scope={
            "type": "http",
            "app": app,
            "method": "GET",
            "path": "/",
            "headers": [],
            "query_string": b"",
            "client": ("testclient", 50000),
            "server": ("testserver", 80),
            "scheme": "http",
            "http_version": "1.1",
        }
    )

    with pytest.raises(ValueError, match="REDIS_URL não configurada"):
        RedisDependencies._get_redis_client(request)


def test_get_cache_service_builds_cache_with_redis_client() -> None:
    redis_client = SimpleNamespace(client=Mock(), ttl_seconds=120)

    service = RedisDependencies.get_cache_service(redis_client)

    assert isinstance(service, CacheService)


def test_user_dependencies_create_expected_instances() -> None:
    session = Mock()
    repository = UserDependencies._get_repository(session)
    unit_of_work = UserDependencies._get_unit_of_work(session)
    hasher = UserDependencies._get_password_hasher(PasswordHasher())

    assert isinstance(repository, UserRepository)
    assert isinstance(unit_of_work, UnitOfWork)
    assert isinstance(hasher, PasswordHasher)
