"""Smoke: confirma que as dependências principais instalam e importam corretamente."""


def test_import_fastapi() -> None:
    import fastapi  # noqa: PLC0415

    assert fastapi.__version__


def test_import_sqlalchemy_async() -> None:
    from sqlalchemy.ext.asyncio import (  # noqa: PLC0415
        AsyncSession,
        create_async_engine,
    )

    assert AsyncSession is not None
    assert create_async_engine is not None


def test_import_asyncpg() -> None:
    import asyncpg  # noqa: PLC0415

    assert asyncpg is not None


def test_import_redis() -> None:
    import redis  # noqa: PLC0415

    assert redis.__version__


def test_import_alembic() -> None:
    import alembic  # noqa: PLC0415

    assert alembic is not None


def test_import_pydantic_settings() -> None:
    from pydantic_settings import BaseSettings  # noqa: PLC0415

    assert BaseSettings is not None
