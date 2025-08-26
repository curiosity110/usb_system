import pytest
from fastapi.testclient import TestClient
from datetime import date

from app import db, models, crud, schemas
from app.main import app

client = TestClient(app, follow_redirects=False)


@pytest.fixture(autouse=True)
def setup_db():
    models.Base.metadata.drop_all(bind=db.engine)
    models.Base.metadata.create_all(bind=db.engine)
    yield
    models.Base.metadata.drop_all(bind=db.engine)


def test_unique_email():
    r1 = client.post(
        "/clients",
        data={
            "first_name": "Alice",
            "last_name": "A",
            "email": "Test@Example.com",
            "phone": "+1 (555) 123-4567",
        },
    )
    assert r1.status_code == 303
    r2 = client.post(
        "/clients",
        data={
            "first_name": "Bob",
            "last_name": "B",
            "email": "TEST@example.com",
            "phone": "+1 (555) 765-4321",
        },
    )
    assert r2.status_code == 400


def test_unique_phone():
    r1 = client.post(
        "/clients",
        data={
            "first_name": "Alice",
            "last_name": "A",
            "email": "a1@example.com",
            "phone": "+1 (555) 123-4567",
        },
    )
    assert r1.status_code == 303
    r2 = client.post(
        "/clients",
        data={
            "first_name": "Bob",
            "last_name": "B",
            "email": "a2@example.com",
            "phone": "+1-555-123-4567",
        },
    )
    assert r2.status_code == 409


def test_search_by_dob():
    with db.SessionLocal() as session:
        crud.clients.create_client(
            session,
            schemas.ClientCreate(
                first_name="Alice",
                last_name="A",
                email="alice@example.com",
                phone="111",
                dob=date.fromisoformat("1990-01-01"),
            ),
        )
        crud.clients.create_client(
            session,
            schemas.ClientCreate(
                first_name="Bob",
                last_name="B",
                email="bob@example.com",
                phone="222",
                dob=date.fromisoformat("1985-05-05"),
            ),
        )
        results = crud.clients.list_clients(session, "1990-01-01")
        assert len(results) == 1
        assert results[0].first_name == "Alice"
