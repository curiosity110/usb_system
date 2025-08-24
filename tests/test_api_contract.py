import os
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

os.environ["DEV_SYNC"] = "1"

from app import db, models, schemas
from app.crud import bookings, clients, trips
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_db():
    models.Base.metadata.drop_all(bind=db.engine)
    models.Base.metadata.create_all(bind=db.engine)
    yield
    models.Base.metadata.drop_all(bind=db.engine)


def test_outbox_format_and_clock_increment():
    with db.SessionLocal() as session:
        trip = trips.create_trip(session, schemas.TripCreate(name="T"))
        cl = clients.create_client(
            session,
            schemas.ClientCreate(name="A", email="a@example.com", phone="1"),
        )
        booking = bookings.create_booking(
            session, schemas.BookingCreate(client_id=cl.id, trip_id=trip.id)
        )
        bookings.delete_booking(session, booking.id)
        stmt = (
            select(models.SyncOutbox)
            .where(
                models.SyncOutbox.entity == "booking",
                models.SyncOutbox.entity_id == booking.id,
            )
            .order_by(models.SyncOutbox.logical_clock)
        )
        entries = session.execute(stmt).scalars().all()
        assert [e.logical_clock for e in entries] == [1, 2]
        assert entries[0].op == "create"
        assert entries[1].op == "delete"
        assert entries[1].payload is None


def test_lww_behavior():
    with db.SessionLocal() as session:
        cl = clients.create_client(
            session,
            schemas.ClientCreate(name="Alice", email="a@example.com", phone="1"),
        )
        client_id = cl.id
        r = client.get("/sync/pull", params={"after_clock": 0})
        assert r.status_code == 200
        assert r.json()["changes"][0]["entity"] == "client"

        old = {
            "entity": "client",
            "entity_id": client_id,
            "logical_clock": 1,
            "op": "update",
            "payload": {
                "id": client_id,
                "name": "Old",
                "email": cl.email,
                "phone": cl.phone,
                "normalized_phone": cl.normalized_phone,
                "dob": None,
            },
            "updated_at": (datetime.utcnow() - timedelta(seconds=5)).isoformat(),
        }
        resp = client.post("/sync/push", json={"changes": [old]})
        assert resp.status_code == 200
        session.refresh(cl)
        assert cl.name == "Alice"

        new = old.copy()
        new["logical_clock"] = 2
        new["payload"] = new["payload"].copy()
        new["payload"]["name"] = "New"
        new["updated_at"] = datetime.utcnow().isoformat()
        client.post("/sync/push", json={"changes": [new]})
        session.refresh(cl)
        assert cl.name == "New"

        delete = {
            "entity": "client",
            "entity_id": client_id,
            "logical_clock": 3,
            "op": "delete",
            "payload": None,
            "updated_at": datetime.utcnow().isoformat(),
        }
        client.post("/sync/push", json={"changes": [delete]})
        session.expire_all()
        assert session.get(models.Client, client_id) is None

