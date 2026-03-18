"""Modelo ORM de usuário."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base


class User(Base):
    """Usuário do sistema."""

    __tablename__ = "user"

    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(length=255),
        nullable=False,
        unique=True,
        index=True,
    )
    password: Mapped[str] = mapped_column(String(length=255), nullable=False)

