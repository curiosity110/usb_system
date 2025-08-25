import pytest
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


def test_client_export():
    client.post("/clients", json={"name": "Alice", "email": "a@example.com", "phone": "123"})
    r = client.get("/clients/export")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]


def test_trip_export():
    client.post("/trips", json={"name": "Trip"})
    r = client.get("/trips/export")
    assert r.status_code == 200
    assert "text/csv" in r.headers["content-type"]
