"""Hash de senha com bcrypt."""

import bcrypt


class PasswordHasher:
    """Responsavel por gerar e validar hash de senhas com bcrypt."""

    def __init__(self, rounds: int = 12) -> None:
        """Configura o custo (rounds) usado na derivacao bcrypt."""
        self._rounds = rounds

    def hash_password(self, password: str) -> str:
        """Gera hash bcrypt em formato textual para persistencia."""

        hashed_password = bcrypt.hashpw(
            password.encode("utf-8"),
            bcrypt.gensalt(rounds=self._rounds),
        )
        return hashed_password.decode("utf-8")

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Valida senha em texto puro contra hash bcrypt persistido."""

        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8"),
        )


def get_password_hasher() -> PasswordHasher:
    """Factory para injeção de dependência do PasswordHasher."""

    return PasswordHasher()
