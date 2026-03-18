"""Base ORM do projeto (SQLAlchemy)."""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Classe base para todos os modelos ORM."""

    pass

