"""CRUD operations for Maintenance objects."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas


def create_maintenance(db: Session, maintenance_in: schemas.MaintenanceCreate) -> models.Maintenance:
    record = models.Maintenance(
        vehicle_id=maintenance_in.vehicle_id,
        kind=maintenance_in.kind,
        due_date=maintenance_in.due_date,
        completed_at=maintenance_in.completed_at,
        notes=maintenance_in.notes,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def list_maintenance(db: Session, vehicle_id: str | None = None) -> list[models.Maintenance]:
    stmt = select(models.Maintenance)
    if vehicle_id:
        stmt = stmt.where(models.Maintenance.vehicle_id == vehicle_id)
    return db.execute(stmt).scalars().all()
