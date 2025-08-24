from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas


def create(session: Session, data: schemas.BookingCreate) -> models.Booking:
    booking = models.Booking(client_id=data.client_id, trip_id=data.trip_id)
    session.add(booking)
    session.commit()
    session.refresh(booking)
    return booking


def list(session: Session) -> list[models.Booking]:
    return list(session.execute(select(models.Booking)).scalars())
