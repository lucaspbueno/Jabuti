"""Configuração de conexão com o banco de dados."""

from app.core import Settings


class DatabaseConfig:
    """Responsável por entregar a configuração de conexão com o banco de dados."""

    def __init__(self, settings: Settings) -> None:
        self._url = settings.database_url
        self._debug = settings.debug

    @property
    def url(self) -> str:
        return self._url

    @property
    def debug(self) -> bool:
        return self._debug
