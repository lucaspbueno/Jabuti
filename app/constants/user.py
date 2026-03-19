"""Constantes compartilhadas da feature de usuário."""

from typing import Final


class UserConstraints:
    """Fonte única de restrições compartilhadas entre model e schemas."""

    NAME_MIN_LENGTH: Final[int] = 1
    NAME_MAX_LENGTH: Final[int] = 255
    EMAIL_MAX_LENGTH: Final[int] = 255
    PASSWORD_MIN_LENGTH: Final[int] = 8
    PASSWORD_MAX_LENGTH: Final[int] = 255
