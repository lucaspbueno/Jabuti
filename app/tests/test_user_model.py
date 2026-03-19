"""Testes estruturais do modelo User."""

from sqlalchemy import Boolean, DateTime, DefaultClause, String
from sqlalchemy.dialects.postgresql import UUID

from app.constants import UserConstraints
from app.models import User


def test_user_tablename() -> None:
    assert User.__tablename__ == "user"


def test_user_columns_basic_types_and_constraints() -> None:
    table = User.__table__.c

    id_col = table.id
    assert isinstance(id_col.type, UUID)
    assert id_col.primary_key is True
    assert isinstance(id_col.server_default, DefaultClause)

    name_col = table.name
    assert isinstance(name_col.type, String)
    assert name_col.nullable is False
    assert name_col.type.length == UserConstraints.NAME_MAX_LENGTH

    email_col = table.email
    assert isinstance(email_col.type, String)
    assert email_col.nullable is False
    assert email_col.type.length == UserConstraints.EMAIL_MAX_LENGTH
    assert email_col.unique is True
    assert email_col.index is True

    password_col = table.password
    assert isinstance(password_col.type, String)
    assert password_col.nullable is False
    assert password_col.type.length == UserConstraints.PASSWORD_MAX_LENGTH

    active_col = table.active
    assert isinstance(active_col.type, Boolean)
    assert active_col.nullable is False
    assert active_col.server_default is not None

    created_at_col = table.created_at
    assert isinstance(created_at_col.type, DateTime)
    assert created_at_col.nullable is False
    assert created_at_col.server_default is not None

    updated_at_col = table.updated_at
    assert isinstance(updated_at_col.type, DateTime)
    assert updated_at_col.nullable is False
    assert updated_at_col.server_default is not None
    assert updated_at_col.onupdate is not None

    deleted_at_col = table.deleted_at
    assert isinstance(deleted_at_col.type, DateTime)
    assert deleted_at_col.nullable is True
