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


def create_client(name: str, email: str, phone: str) -> dict:
    response = client.post(
        "/clients", json={"name": name, "email": email, "phone": phone}
    )
    assert response.status_code == 201
    return response.json()


def create_trip(name: str) -> dict:
    response = client.post("/trips", json={"name": name})
    assert response.status_code == 201
    return response.json()


def test_unique_booking():
    cl = create_client("Alice", "alice@example.com", "+1 (555) 123-4567")
    tr = create_trip("Trip 1")
    r1 = client.post(
        "/bookings", json={"client_id": cl["id"], "trip_id": tr["id"]}
    )
    assert r1.status_code == 201
    r2 = client.post(
        "/bookings", json={"client_id": cl["id"], "trip_id": tr["id"]}
    )
    assert r2.status_code == 400
