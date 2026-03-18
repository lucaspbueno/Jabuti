"""Ponto de entrada da aplicação FastAPI."""


from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import Settings, get_settings


class Application:
    """Monta e configura a instância FastAPI."""

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings = settings if settings is not None else get_settings()

    def build(self) -> FastAPI:
        app = FastAPI(
            title=self._settings.app_name,
            debug=self._settings.debug,
        )
        app.include_router(
            api_router,
            prefix=self._settings.api_prefix.rstrip("/") or "",
        )
        return app


def create_app(settings: Settings | None = None) -> FastAPI:
    """Factory usada por Uvicorn e por testes (permite injetar `Settings`)."""
    return Application(settings=settings).build()


app = create_app()
