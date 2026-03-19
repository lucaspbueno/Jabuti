"""Modelo ORM de usuário."""

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.constants import UserConstraints
from app.models.base import Base


class User(Base):
    """Usuário do sistema."""

    __tablename__ = "user"

    name: Mapped[str] = mapped_column(
        String(length=UserConstraints.NAME_MAX_LENGTH),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(length=UserConstraints.EMAIL_MAX_LENGTH),
        nullable=False,
        unique=True,
        index=True,
    )
    password: Mapped[str] = mapped_column(
        String(length=UserConstraints.PASSWORD_MAX_LENGTH),
        nullable=False,
    )
