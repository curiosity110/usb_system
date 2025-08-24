from __future__ import annotations

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models, schemas
from app.crud import clients
from app.services import dedupe


def make_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session()


def test_dedupe_email():
    session = make_session()
    existing = clients.create(
        session,
        schemas.ClientCreate(first_name="John", last_name="Doe", email="john@example.com"),
    )
    new = schemas.ClientCreate(first_name="John", last_name="Doe", email="JOHN@example.com")
    assert dedupe.is_potential_duplicate(new, existing)
    session.close()


def test_dedupe_phone_name():
    session = make_session()
    existing = clients.create(
        session,
        schemas.ClientCreate(first_name="Alice", last_name="Smith", phone="+1 555 123 4567"),
    )
    new = schemas.ClientCreate(
        first_name="Alyce",
        last_name="Smyth",
        phone="5551234567",
        email=None,
    )
    assert dedupe.is_potential_duplicate(new, existing)
    session.close()
