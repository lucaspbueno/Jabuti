"""Exceções de domínio da feature de usuário."""

from __future__ import annotations

import uuid

from app.exceptions.base import AppError


class UserDomainError(AppError):
    """Exceção base da feature de usuário."""


class UserNotFoundError(UserDomainError):
    """Lançada quando o usuário não é encontrado."""

    def __init__(self, user_id: uuid.UUID) -> None:
        super().__init__(
            message=f"Usuário com id '{user_id}' não encontrado.",
            error_code="user_not_found",
            status_code=404,
        )


class UserEmailAlreadyExistsError(UserDomainError):
    """Lançada quando o email informado já está em uso."""

    def __init__(self, email: str) -> None:
        super().__init__(
            message=f"O email '{email}' já está em uso.",
            error_code="user_email_already_exists",
            status_code=409,
        )
