import pytest
from fastapi.testclient import TestClient

from app import db, models
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    models.Base.metadata.drop_all(bind=db.engine)
    models.Base.metadata.create_all(bind=db.engine)
    yield
    models.Base.metadata.drop_all(bind=db.engine)


def test_unique_email():
    r1 = client.post(
        "/clients",
        json={"name": "Alice", "email": "Test@Example.com", "phone": "+1 (555) 123-4567"},
    )
    assert r1.status_code == 201
    r2 = client.post(
        "/clients",
        json={"name": "Bob", "email": "TEST@example.com", "phone": "+1 (555) 765-4321"},
    )
    assert r2.status_code == 400


def test_unique_phone():
    r1 = client.post(
        "/clients",
        json={"name": "Alice", "email": "a1@example.com", "phone": "+1 (555) 123-4567"},
    )
    assert r1.status_code == 201
    r2 = client.post(
        "/clients",
        json={"name": "Bob", "email": "a2@example.com", "phone": "+1-555-123-4567"},
    )
    assert r2.status_code == 400
