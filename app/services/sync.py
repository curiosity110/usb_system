from __future__ import annotations

from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .. import models


def enqueue(
    session: Session,
    model: str,
    model_id: int,
    action: str,
    payload: dict,
    tombstone: bool = False,
) -> models.SyncOutbox:
    last_clock = session.execute(
        select(func.max(models.SyncOutbox.logical_clock))
    ).scalar()
    next_clock = (last_clock or 0) + 1
    entry = models.SyncOutbox(
        model=model,
        model_id=model_id,
        action=action,
        payload=payload,
        logical_clock=next_clock,
        tombstone=tombstone,
    )
    session.add(entry)
    session.commit()
    session.refresh(entry)
    return entry


def pending(session: Session) -> list[models.SyncOutbox]:
    return list(session.execute(select(models.SyncOutbox).order_by(models.SyncOutbox.logical_clock)).scalars())


def mark_synced(session: Session, entry: models.SyncOutbox):
    session.delete(entry)
    session.commit()
