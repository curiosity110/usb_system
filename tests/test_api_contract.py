from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app import models
from app.db import get_session


def override_session():
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    models.Base.metadata.create_all(engine)
    TestingSession = sessionmaker(bind=engine)

    def _get_session():
        with TestingSession() as session:
            yield session

    return _get_session


def test_create_entities():
    app.dependency_overrides[get_session] = override_session()
    client = TestClient(app)

    # create client
    resp = client.post("/clients/", json={"first_name": "John", "last_name": "Doe"})
    assert resp.status_code == 200
    cid = resp.json()["id"]

    # create trip
    resp = client.post("/trips/", json={"name": "Trip"})
    assert resp.status_code == 200
    tid = resp.json()["id"]

    # create booking
    resp = client.post("/bookings/", json={"client_id": cid, "trip_id": tid})
    assert resp.status_code == 200

    # list clients
    resp = client.get("/clients/")
    assert resp.status_code == 200
    assert len(resp.json()) == 1

    app.dependency_overrides.clear()
