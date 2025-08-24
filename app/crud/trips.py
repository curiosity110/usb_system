"""CRUD operations for Trip objects."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import sync


def create_trip(db: Session, trip_in: schemas.TripCreate) -> models.Trip:
    trip = models.Trip(name=trip_in.name)
    db.add(trip)
    db.flush()
    sync.enqueue_outbox(
        db,
        entity="trip",
        entity_id=trip.id,
        op="create",
        payload={"id": trip.id, "name": trip.name},
    )
    db.commit()
    db.refresh(trip)
    return trip


def get_trip(db: Session, trip_id: int) -> models.Trip | None:
    return db.get(models.Trip, trip_id)


def list_trips(db: Session) -> list[models.Trip]:
    stmt = select(models.Trip)
    return db.execute(stmt).scalars().all()
