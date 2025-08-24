"""Development-only sync routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import db, models
from ..services import sync as sync_service

router = APIRouter(prefix="/sync", tags=["sync"])


@router.post("/push")
def push(payload: dict, db_session: Session = Depends(db.get_db)) -> dict:
    changes = payload.get("changes", [])
    sync_service.apply_inbound_changes(db_session, changes)
    db_session.commit()
    return {"status": "ok"}


@router.get("/pull")
def pull(after_clock: int = 0, db_session: Session = Depends(db.get_db)) -> dict:
    stmt = (
        select(models.SyncOutbox)
        .where(models.SyncOutbox.id > after_clock)
        .order_by(models.SyncOutbox.id)
    )
    entries = db_session.execute(stmt).scalars().all()
    return {"changes": [sync_service.serialize_outbox(e) for e in entries]}


