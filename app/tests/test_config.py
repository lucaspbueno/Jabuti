"""Testes de carregamento de configuração."""

import pytest
from pydantic import ValidationError

from app.core.config import Settings, get_settings


def test_settings_from_explicit_values() -> None:
    s = Settings(
        app_name="X",
        environment="staging",
        debug=True,
        api_prefix="/v2",
        database_url="postgresql+asyncpg://u:p@h/d",
        redis_url="redis://localhost:1",
    )
    assert s.app_name == "X"
    assert s.environment == "staging"
    assert s.debug is True
    assert s.api_prefix == "/v2"
    assert s.database_url is not None
    assert s.redis_url is not None


def test_settings_rejects_none_urls() -> None:
    with pytest.raises(ValidationError) as exc:
        Settings(
            database_url=None,  # type: ignore[arg-type]
            redis_url=None,  # type: ignore[arg-type]
        )
    errors = {e["loc"][0] for e in exc.value.errors()}
    assert errors == {"database_url", "redis_url"}


def test_get_settings_cached(monkeypatch: pytest.MonkeyPatch) -> None:
    get_settings.cache_clear()
    monkeypatch.setenv("APP_NAME", "From Env")
    try:
        a = get_settings()
        b = get_settings()
        assert a is b
        assert a.app_name == "From Env"
    finally:
        get_settings.cache_clear()
        monkeypatch.delenv("APP_NAME", raising=False)
