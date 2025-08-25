# app/crud/bookings.py
from __future__ import annotations
from sqlalchemy.orm import Session
from .. import models, schemas

def list_bookings(db: Session) -> list[models.Booking]:
    return (
        db.query(models.Booking)
        .order_by(models.Booking.created_at.desc())
        .all()
    )

def list_bookings_for_trip(db: Session, trip_id: int) -> list[models.Booking]:
    return (
        db.query(models.Booking)
        .filter(models.Booking.trip_id == trip_id)
        .all()
    )


def create_booking(db: Session, booking_in: schemas.BookingCreate) -> models.Booking:
    booking = models.Booking(
        client_id=booking_in.client_id,
        trip_id=booking_in.trip_id,
        status=booking_in.status,
        notes=booking_in.notes,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking