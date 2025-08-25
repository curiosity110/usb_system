# app/crud/trips.py
from __future__ import annotations
from sqlalchemy.orm import Session
from .. import models, schemas

def list_trips(db: Session) -> list[models.Trip]:
    return db.query(models.Trip).order_by(models.Trip.created_at.desc()).all()

def get_trip(db: Session, trip_id: int) -> models.Trip | None:
    return db.get(models.Trip, trip_id)

def create_trip(db: Session, trip_in: schemas.TripCreate) -> models.Trip:
    trip = models.Trip(
        name=trip_in.name,
        destination=trip_in.destination,
        start_date=trip_in.start_date,
        end_date=trip_in.end_date,
        notes=trip_in.notes,
    )
    db.add(trip)
    db.commit()
    db.refresh(trip)
    return trip
