"""Testes estruturais do modelo User."""


from sqlalchemy import Boolean, DateTime, DefaultClause, String
from sqlalchemy.dialects.postgresql import UUID

from app.models import User


def test_user_tablename() -> None:
    assert User.__tablename__ == "user"


def test_user_columns_basic_types_and_constraints() -> None:
    table = User.__table__.c

    id, name, email, password, active, created_at, updated_at, deleted_at = table

    id_col = id
    assert isinstance(id_col.type, UUID)
    assert id_col.primary_key is True
    assert isinstance(id_col.server_default, DefaultClause)

    name_col = name
    assert isinstance(name_col.type, String)
    assert name_col.nullable is False

    email_col = email
    assert isinstance(email_col.type, String)
    assert email_col.nullable is False
    assert email_col.unique is True
    assert email_col.index is True

    password_col = password
    assert isinstance(password_col.type, String)
    assert password_col.nullable is False

    active_col = active
    assert isinstance(active_col.type, Boolean)
    assert active_col.nullable is False
    assert active_col.server_default is not None

    created_at_col = created_at
    assert isinstance(created_at_col.type, DateTime)
    assert created_at_col.nullable is False
    assert created_at_col.server_default is not None

    updated_at_col = updated_at
    assert isinstance(updated_at_col.type, DateTime)
    assert updated_at_col.nullable is False
    assert updated_at_col.server_default is not None
    assert updated_at_col.onupdate is not None

    deleted_at_col = deleted_at
    assert isinstance(deleted_at_col.type, DateTime)
    assert deleted_at_col.nullable is True

