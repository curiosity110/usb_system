from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas


def create(session: Session, data: schemas.TripCreate) -> models.Trip:
    trip = models.Trip(name=data.name, start_date=data.start_date, end_date=data.end_date)
    session.add(trip)
    session.commit()
    session.refresh(trip)
    return trip


def list(session: Session) -> list[models.Trip]:
    return list(session.execute(select(models.Trip)).scalars())
