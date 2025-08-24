from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest

from app import models, schemas
from app.crud import clients


@pytest.fixture
def session(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path/'test.db'}", connect_args={"check_same_thread": False}
    )
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        yield session


def test_unique_email(session):
    clients.create(
        session,
        schemas.ClientCreate(first_name="A", last_name="B", email="Test@Example.com"),
    )
    with pytest.raises(ValueError):
        clients.create(
            session,
            schemas.ClientCreate(first_name="C", last_name="D", email="test@example.com"),
        )


def test_phone_normalization(session):
    clients.create(
        session,
        schemas.ClientCreate(first_name="A", last_name="B", phone="123-456-7890"),
    )
    with pytest.raises(ValueError):
        clients.create(
            session,
            schemas.ClientCreate(first_name="C", last_name="D", phone="(123)456-7890"),
        )
