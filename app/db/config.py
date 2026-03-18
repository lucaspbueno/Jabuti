"""Configuração de conexão com o banco de dados."""

from app.core import Settings


class DatabaseConfig:
    """Responsável por entregar a URL de conexão do banco."""

    def __init__(self, settings: Settings) -> None:
        if settings.database_url is None:
            msg = "DATABASE_URL não configurada nas settings."
            raise ValueError(msg)
        self._url = settings.database_url

    @property
    def url(self) -> str:
        return self._url
