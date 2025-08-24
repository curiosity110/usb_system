"""CRUD operations for Reminder objects."""
from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas


def create_reminder(db: Session, reminder_in: schemas.ReminderCreate) -> models.Reminder:
    reminder = models.Reminder(
        scope=reminder_in.scope,
        ref_id=reminder_in.ref_id,
        title=reminder_in.title,
        due_date=reminder_in.due_date,
        assigned_role=reminder_in.assigned_role,
        done_at=reminder_in.done_at,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def list_reminders(db: Session, scope: str | None = None) -> list[models.Reminder]:
    stmt = select(models.Reminder)
    if scope:
        stmt = stmt.where(models.Reminder.scope == scope)
    return db.execute(stmt).scalars().all()
