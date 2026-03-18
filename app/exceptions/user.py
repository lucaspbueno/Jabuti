"""Exceções de domínio da feature de usuário."""

import uuid


class UserDomainError(Exception):
    """Exceção base da feature de usuário."""


class UserNotFoundError(UserDomainError):
    """Lançada quando o usuário não é encontrado."""

    def __init__(self, user_id: uuid.UUID) -> None:
        super().__init__(f"Usuário com id '{user_id}' não encontrado.")


class UserEmailAlreadyExistsError(UserDomainError):
    """Lançada quando o email informado já está em uso."""

    def __init__(self, email: str) -> None:
        super().__init__(f"O email '{email}' já está em uso.")
