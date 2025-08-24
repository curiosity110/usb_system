"""CRUD operations for Booking objects."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import sync


def create_booking(db: Session, booking_in: schemas.BookingCreate) -> models.Booking:
    booking = models.Booking(
        client_id=booking_in.client_id,
        trip_id=booking_in.trip_id,
    )
    db.add(booking)
    db.flush()
    sync.enqueue_outbox(
        db,
        entity="booking",
        entity_id=booking.id,
        op="create",
        payload={
            "id": booking.id,
            "client_id": booking.client_id,
            "trip_id": booking.trip_id,
        },
    )
    db.commit()
    db.refresh(booking)
    return booking


def get_booking(db: Session, booking_id: int) -> models.Booking | None:
    return db.get(models.Booking, booking_id)


def list_bookings(db: Session) -> list[models.Booking]:
    stmt = select(models.Booking)
    return db.execute(stmt).scalars().all()


def delete_booking(db: Session, booking_id: int) -> None:
    booking = db.get(models.Booking, booking_id)
    if booking:
        sync.enqueue_outbox(
            db,
            entity="booking",
            entity_id=booking.id,
            op="delete",
            payload=None,
        )
        db.delete(booking)
        db.commit()
