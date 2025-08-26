"""Audit logging utilities."""
from __future__ import annotations

from sqlalchemy import select, desc
from sqlalchemy.orm import Session
from .. import models




def log_action(
    db: Session,
    *,
    action: str,
    entity: str,
    entity_id: int | None,
    before: dict | None,
    after: dict | None,
) -> models.AuditLog:
    """Persist an audit log entry.

    The caller is responsible for committing the session.
    """

    entry = models.AuditLog(
        action=action,
        entity=entity,
        entity_id=entity_id,
        before=before,
        after=after,
    )
    db.add(entry)
    return entry


def get_timeline_for_client(db: Session, client_id: int):
    stmt = (
        select(models.AuditLog)
        .where(models.AuditLog.entity == "client", models.AuditLog.entity_id == client_id)
        .order_by(desc(models.AuditLog.timestamp))
    )
    return db.execute(stmt).scalars().all()

def get_timeline_for_trip(db: Session, trip_id: int):
    stmt = (
        select(models.AuditLog)
        .where(models.AuditLog.entity == "trip", models.AuditLog.entity_id == trip_id)
        .order_by(desc(models.AuditLog.timestamp))
    )
    return db.execute(stmt).scalars().all()