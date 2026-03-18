"""Exceções base da aplicação."""


class AppError(Exception):
    """Exceção base com metadados para tradução em HTTP."""

    def __init__(self, *, message: str, error_code: str, status_code: int) -> None:
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.status_code = status_code
