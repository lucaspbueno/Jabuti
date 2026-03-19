"""Ponto de entrada da aplicação FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.cache import RedisClient, RedisConfig 
from app.core import Settings, get_settings, setup_logging
from app.db import DatabaseConfig, DatabaseSessionManager
from app.exceptions import register_exception_handlers


class Application:
    """Monta e configura a instância FastAPI."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @asynccontextmanager
    async def lifespan(self, app: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            db    = app.state.db
            redis = app.state.redis

            if db:
                await db.close()

            if redis:
                await redis.close()

    def build(self) -> FastAPI:
        db: DatabaseSessionManager = DatabaseSessionManager(DatabaseConfig(self._settings))
        redis: RedisClient         = RedisClient(RedisConfig(self._settings))

        app = (
            FastAPI(
                title=self._settings.app_name,
                debug=self._settings.debug,
                lifespan=self.lifespan,
            )
        )

        app.state.settings = self._settings
        app.state.db       = db
        app.state.redis    = redis

        register_exception_handlers(app)
        app.include_router(api_router, prefix=self._settings.api_prefix.rstrip("/"))

        return app


def create_app(settings: Settings) -> FastAPI:
    """Factory usada por Uvicorn e por testes (permite injetar `Settings`)."""

    return Application(settings=settings).build()


setup_logging()

app = create_app(settings=get_settings())
