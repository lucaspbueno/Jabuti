"""Ponto de entrada da aplicação FastAPI."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.cache import close_redis_client
from app.core.config import Settings, get_settings
from app.exceptions import register_exception_handlers


class Application:
    """Monta e configura a instância FastAPI."""

    def __init__(self, settings: Settings) -> None:
        self._settings = settings

    @asynccontextmanager
    async def lifespan(self, _: FastAPI) -> AsyncIterator[None]:
        try:
            yield
        finally:
            await close_redis_client()

    def build(self) -> FastAPI:
        app = FastAPI(
            title=self._settings.app_name,
            debug=self._settings.debug,
            lifespan=self.lifespan,
        )
        register_exception_handlers(app)
        app.include_router(
            api_router,
            prefix=self._settings.api_prefix.rstrip("/") or "",
        )
        return app


def create_app(settings: Settings) -> FastAPI:
    """Factory usada por Uvicorn e por testes (permite injetar `Settings`)."""

    return Application(settings=settings).build()


app = create_app(settings=get_settings())
