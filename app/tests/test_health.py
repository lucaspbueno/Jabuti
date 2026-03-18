"""Testes do endpoint de health."""

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import Settings, get_settings
from app.main import create_app


@pytest.fixture
def test_settings() -> Settings:
    return Settings(
        app_name="Jabuti Test",
        environment="test",
        debug=False,
        api_prefix="/api/v1",
    )


@pytest.fixture
async def client(test_settings: Settings) -> AsyncIterator[AsyncClient]:
    application = create_app(settings=test_settings)
    application.dependency_overrides[get_settings] = lambda: test_settings
    transport = ASGITransport(app=application)
    try:
        async with AsyncClient(
            transport=transport,
            base_url="http://test",
        ) as ac:
            yield ac
    finally:
        application.dependency_overrides.clear()


async def test_health_returns_200_and_payload(
    client: AsyncClient,
    test_settings: Settings,
) -> None:
    response = await client.get("/api/v1/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == test_settings.app_name
    assert data["environment"] == test_settings.environment


async def test_unknown_path_returns_404(client: AsyncClient) -> None:
    response = await client.get("/api/v1/inexistente")
    assert response.status_code == 404
