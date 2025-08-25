# app/crud/trips.py
from sqlalchemy.orm import Session

from .. import models, schemas

def list_trips(db: Session) -> list[models.Trip]:
    # no created_at dependency
    return db.query(models.Trip).order_by(models.Trip.id.desc()).all()

def get_trip(db: Session, trip_id: int):
    return db.query(models.Trip).filter(models.Trip.id == trip_id).first()


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
