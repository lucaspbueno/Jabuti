"""Hash de senha com PBKDF2-HMAC-SHA256."""

import base64
import hashlib
import hmac
import os


class PasswordHasher:
    """Responsavel por gerar e validar hash de senhas."""

    def __init__(
        self,
        algorithm: str = "pbkdf2_sha256",
        iterations: int = 600_000,
        salt_size: int = 16,
    ) -> None:
        """Configura algoritmo, custo e tamanho do salt para hash de senha."""
        self._algorithm = algorithm
        self._iterations = iterations
        self._salt_size = salt_size
        self._hash_algorithm = "sha256"

    def hash_password(self, password: str) -> str:
        """Gera digest com salt aleatorio e metadados embutidos."""

        salt = os.urandom(self._salt_size)
        digest = hashlib.pbkdf2_hmac(
            self._hash_algorithm,
            password.encode("utf-8"),
            salt,
            self._iterations,
        )
        encoded_salt = self._encode(salt)
        encoded_digest = self._encode(digest)

        return f"{self._algorithm}${self._iterations}${encoded_salt}${encoded_digest}"

    def verify_password(self, password: str, hashed_password: str) -> bool:
        """Valida senha em texto puro contra hash persistido."""

        algorithm, iterations, encoded_salt, expected_digest = hashed_password.split(
            "$",
            maxsplit=3,
        )

        if algorithm != self._algorithm:
            return False

        computed_digest = hashlib.pbkdf2_hmac(
            self._hash_algorithm,
            password.encode("utf-8"),
            self._decode(encoded_salt),
            int(iterations),
        )

        return hmac.compare_digest(self._encode(computed_digest), expected_digest)

    @staticmethod
    def _encode(value: bytes) -> str:
        """Converte bytes para string Base64 URL-safe sem padding final."""
        return base64.urlsafe_b64encode(value).decode("ascii").rstrip("=")

    @staticmethod
    def _decode(value: str) -> bytes:
        """Converte string Base64 URL-safe em bytes, restaurando o padding."""
        padded_value = value + "=" * (-len(value) % 4)
        return base64.urlsafe_b64decode(padded_value.encode("ascii"))
