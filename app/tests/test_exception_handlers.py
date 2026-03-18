"""Testes dos handlers globais de exceção."""

from __future__ import annotations

import uuid
from collections.abc import AsyncIterator

import pytest
from fastapi import Body, FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings
from app.exceptions import UserEmailAlreadyExistsError, UserNotFoundError
from app.main import create_app


@pytest.fixture
def exception_test_app() -> tuple[Settings, FastAPI]:
    settings = Settings(
        app_name="Jabuti Test",
        environment="test",
        debug=False,
        api_prefix="/api/v1",
    )
    app = create_app(settings=settings)

    @app.get("/__test/not-found")
    async def raise_not_found() -> None:
        raise UserNotFoundError(uuid.uuid4())

    @app.get("/__test/conflict")
    async def raise_conflict() -> None:
        raise UserEmailAlreadyExistsError("lucas@example.com")

    @app.get("/__test/unexpected")
    async def raise_unexpected() -> None:
        raise RuntimeError("boom")

    @app.post("/__test/validation")
    async def validation_payload(limit: int = Body(..., embed=True)) -> dict[str, int]:
        return {"limit": limit}

    return settings, app


@pytest.fixture
async def exception_client(
    exception_test_app: tuple[Settings, FastAPI],
) -> AsyncIterator[AsyncClient]:
    _, application = exception_test_app
    transport = ASGITransport(app=application, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


async def test_user_not_found_is_translated_to_404(
    exception_client: AsyncClient,
) -> None:
    response = await exception_client.get("/__test/not-found")

    assert response.status_code == 404
    payload = response.json()
    assert payload["error"]["code"] == "user_not_found"
    assert "não encontrado" in payload["error"]["message"]
    assert payload["error"]["details"] is None


async def test_email_already_exists_is_translated_to_409(
    exception_client: AsyncClient,
) -> None:
    response = await exception_client.get("/__test/conflict")

    assert response.status_code == 409
    payload = response.json()
    assert payload["error"]["code"] == "user_email_already_exists"
    assert "já está em uso" in payload["error"]["message"]


async def test_validation_error_is_translated_to_422(
    exception_client: AsyncClient,
) -> None:
    response = await exception_client.post(
        "/__test/validation",
        json={"limit": "abc"},
    )

    assert response.status_code == 422
    payload = response.json()
    assert payload["error"]["code"] == "validation_error"
    assert payload["error"]["message"] == "Erro de validação na requisição."
    assert isinstance(payload["error"]["details"], list)
    assert payload["error"]["details"]


async def test_unexpected_error_is_translated_to_500(
    exception_client: AsyncClient,
) -> None:
    response = await exception_client.get("/__test/unexpected")

    assert response.status_code == 500
    payload = response.json()
    assert payload["error"]["code"] == "internal_server_error"
    assert payload["error"]["message"] == "Ocorreu um erro interno na aplicação."
    assert payload["error"]["details"] is None
