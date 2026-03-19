"""Testes HTTP das rotas da feature de usuário."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator
from datetime import UTC, datetime
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.api.deps import get_user_service
from app.core.config import Settings
from app.exceptions import UserNotFoundError
from app.main import create_app
from app.schemas.user import UserListResponse, UserResponse


def make_user_response(*, email: str = "lucas@example.com") -> UserResponse:
    now = datetime.now(UTC)
    return UserResponse(
        id=uuid.uuid4(),
        name="Lucas",
        email=email,
        active=True,
        created_at=now,
        updated_at=now,
    )


@pytest.fixture
def users_test_app() -> tuple[Settings, FastAPI, AsyncMock]:
    settings = Settings(
        app_name="Jabuti Test",
        environment="test",
        debug=False,
        api_prefix="/api/v1",
    )
    app = create_app(settings=settings)
    service = AsyncMock()
    app.dependency_overrides[get_user_service] = lambda: service
    return settings, app, service


@pytest.fixture
async def users_client(
    users_test_app: tuple[Settings, FastAPI, AsyncMock],
) -> AsyncIterator[tuple[AsyncClient, AsyncMock]]:
    _, app, service = users_test_app
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client, service
    app.dependency_overrides.clear()


async def test_create_user_returns_201_and_response_body(
    users_client: tuple[AsyncClient, AsyncMock],
) -> None:
    client, service = users_client
    response_schema = make_user_response()
    service.create_user.return_value = response_schema

    response = await client.post(
        "/api/v1/users",
        json={
            "name": "Lucas",
            "email": "lucas@example.com",
            "password": "senha-segura",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["id"] == str(response_schema.id)
    assert payload["email"] == "lucas@example.com"
    assert "password" not in payload
    service.create_user.assert_awaited_once()


async def test_get_user_by_id_returns_response(
    users_client: tuple[AsyncClient, AsyncMock],
) -> None:
    client, service = users_client
    response_schema = make_user_response()
    service.get_user_by_id.return_value = response_schema

    response = await client.get(f"/api/v1/users/{response_schema.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["id"] == str(response_schema.id)
    assert payload["email"] == response_schema.email


async def test_list_users_returns_paginated_payload(
    users_client: tuple[AsyncClient, AsyncMock],
) -> None:
    client, service = users_client
    users = [
        make_user_response(email="a@example.com"),
        make_user_response(email="b@example.com"),
    ]
    service.list_users.return_value = UserListResponse(
        items=users,
        total=2,
        limit=5,
        offset=10,
    )

    response = await client.get("/api/v1/users?limit=5&offset=10")

    assert response.status_code == 200
    payload = response.json()
    assert payload["total"] == 2
    assert payload["limit"] == 5
    assert payload["offset"] == 10
    assert len(payload["items"]) == 2
    service.list_users.assert_awaited_once_with(limit=5, offset=10)


async def test_update_user_returns_response(
    users_client: tuple[AsyncClient, AsyncMock],
) -> None:
    client, service = users_client
    response_schema = make_user_response(email="novo@example.com")
    service.update_user.return_value = response_schema

    response = await client.put(
        f"/api/v1/users/{response_schema.id}",
        json={"name": "Novo Nome", "email": "novo@example.com"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["email"] == "novo@example.com"
    assert payload["name"] == "Lucas"


async def test_delete_user_returns_deleted_user(
    users_client: tuple[AsyncClient, AsyncMock],
) -> None:
    client, service = users_client
    response_schema = make_user_response()
    response_schema.active = False
    service.delete_user.return_value = response_schema

    response = await client.delete(f"/api/v1/users/{response_schema.id}")

    assert response.status_code == 200
    payload = response.json()
    assert payload["active"] is False
    service.delete_user.assert_awaited_once_with(response_schema.id)


async def test_list_users_rejects_invalid_limit(
    users_client: tuple[AsyncClient, AsyncMock],
) -> None:
    client, _ = users_client

    response = await client.get("/api/v1/users?limit=0&offset=0")

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"


async def test_route_propagates_domain_error_to_global_handler(
    users_client: tuple[AsyncClient, AsyncMock],
) -> None:
    client, service = users_client
    user_id = uuid.uuid4()
    service.get_user_by_id.side_effect = UserNotFoundError(user_id)

    response = await client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "user_not_found"
