"""CRUD operations for Vehicle objects."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas


def create_vehicle(db: Session, vehicle_in: schemas.VehicleCreate) -> models.Vehicle:
    vehicle = models.Vehicle(
        plate=vehicle_in.plate,
        model=vehicle_in.model,
        year=vehicle_in.year,
        notes=vehicle_in.notes,
    )
    db.add(vehicle)
    db.commit()
    db.refresh(vehicle)
    return vehicle


def list_vehicles(db: Session) -> list[models.Vehicle]:
    stmt = select(models.Vehicle)
    return db.execute(stmt).scalars().all()
