# app/crud/bookings.py
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from .. import models, schemas


def list_bookings(db: Session):
    return db.query(models.Booking).order_by(models.Booking.created_at.desc()).all()


def get_booking(db: Session, booking_id: int):
    return db.query(models.Booking).filter(models.Booking.id == booking_id).first()


def create_booking(db: Session, booking_in: schemas.BookingCreate):
    booking = models.Booking(
        client_id=booking_in.client_id,
        trip_id=booking_in.trip_id,
        status=booking_in.status,
        notes=booking_in.notes,
    )
    db.add(booking)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise
    db.refresh(booking)
    return booking
