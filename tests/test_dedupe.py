import datetime as dt

import pytest

from app import db, models, schemas
from app.crud import clients as crud_clients
from app.services import dedupe


@pytest.fixture(autouse=True)
def setup_db():
    models.Base.metadata.drop_all(bind=db.engine)
    models.Base.metadata.create_all(bind=db.engine)
    yield
    models.Base.metadata.drop_all(bind=db.engine)


def test_dedupe_rules():
    session = db.SessionLocal()
    crud_clients.create_client(
        session,
        schemas.ClientCreate(
            name="Alice Smith",
            email="ali.ce@gmail.com",
            phone="+1 (555) 123-4567",
            dob=dt.date(1990, 1, 1),
        ),
    )
    # rule 1: name similarity >=0.9 and dob equal
    candidate1 = schemas.ClientCreate(
        name="Alyce Smith",
        email="alyce@example.com",
        phone="+1 (555) 765-4321",
        dob=dt.date(1990, 1, 1),
    )
    matches = dedupe.find_potential_duplicates(session, candidate1)
    assert matches, "should detect duplicate via name+dob"

    # rule 2: name similarity >=0.85 and last-7 digits of phone match
    candidate2 = schemas.ClientCreate(
        name="Alice Smyth",
        email="alice2@example.com",
        phone="5551234567",
        dob=dt.date(1991, 2, 2),
    )
    matches = dedupe.find_potential_duplicates(session, candidate2)
    assert matches, "should detect duplicate via phone tail"

    # rule 3: email match ignoring case and dots for gmail
    candidate3 = schemas.ClientCreate(
        name="Another",
        email="ALICE@gmail.com",
        phone="5550000000",
        dob=dt.date(1980, 3, 3),
    )
    matches = dedupe.find_potential_duplicates(session, candidate3)
    assert matches, "should detect duplicate via email"
    session.close()


def test_merge_rewires_bookings():
    session = db.SessionLocal()
    c1 = crud_clients.create_client(
        session,
        schemas.ClientCreate(
            name="Primary",
            email="primary@example.com",
            phone="5550000001",
            dob=dt.date(1980, 1, 1),
        ),
    )
    c2 = crud_clients.create_client(
        session,
        schemas.ClientCreate(
            name="Secondary",
            email="secondary@example.com",
            phone="5550000002",
            dob=dt.date(1985, 1, 1),
        ),
    )
    trip = models.Trip(name="Trip")
    session.add(trip)
    session.commit()
    booking = models.Booking(client_id=c2.id, trip_id=trip.id)
    session.add(booking)
    session.commit()

    dedupe.merge_clients(session, c1, c2)

    updated = session.get(models.Booking, booking.id)
    assert updated.client_id == c1.id
    assert session.get(models.Client, c2.id) is None
    session.close()


def test_merge_creates_audit():
    session = db.SessionLocal()
    c1 = crud_clients.create_client(
        session,
        schemas.ClientCreate(
            name="Old",
            email="old@example.com",
            phone="5551111111",
            dob=dt.date(1980, 1, 1),
        ),
    )
    c2 = crud_clients.create_client(
        session,
        schemas.ClientCreate(
            name="New",
            email="new@example.com",
            phone="5552222222",
            dob=dt.date(1990, 1, 1),
        ),
    )

    dedupe.merge_clients(session, c1, c2)

    logs = session.query(models.AuditLog).all()
    assert any(log.action == "merge" for log in logs)
    session.close()
