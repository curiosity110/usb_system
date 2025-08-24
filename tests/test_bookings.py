from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import models, schemas
from app.crud import clients, trips, bookings


@pytest.fixture
def session(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path/'test.db'}", connect_args={"check_same_thread": False}
    )
    models.Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    with Session() as session:
        yield session


def test_unique_booking(session):
    c = clients.create(session, schemas.ClientCreate(first_name="A", last_name="B"))
    t = trips.create(session, schemas.TripCreate(name="Trip"))
    bookings.create(session, schemas.BookingCreate(client_id=c.id, trip_id=t.id))
    with pytest.raises(Exception):
        bookings.create(session, schemas.BookingCreate(client_id=c.id, trip_id=t.id))
