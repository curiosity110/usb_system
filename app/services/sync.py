"""Synchronization utilities and CLI."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

import httpx
from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session

from .. import models

# Mapping of entity names to model classes
ENTITY_MODELS = {
    "client": models.Client,
    "trip": models.Trip,
    "booking": models.Booking,
}


def enqueue_outbox(
    db: Session,
    *,
    entity: str,
    entity_id: int,
    op: str,
    payload: dict | None,
) -> models.SyncOutbox:
    """Append an entry to the sync outbox with an incrementing logical clock."""

    max_clock = db.execute(
        select(func.max(models.SyncOutbox.logical_clock)).where(
            models.SyncOutbox.entity == entity,
            models.SyncOutbox.entity_id == entity_id,
        )
    ).scalar()
    next_clock = (max_clock or 0) + 1
    entry = models.SyncOutbox(
        entity=entity,
        entity_id=entity_id,
        logical_clock=next_clock,
        op=op,
        payload=payload,
        updated_at=datetime.utcnow(),
    )
    db.add(entry)
    return entry


def serialize_outbox(entry: models.SyncOutbox) -> dict:
    """Convert an outbox entry to a serializable dict."""

    return {
        "id": entry.id,
        "entity": entry.entity,
        "entity_id": entry.entity_id,
        "logical_clock": entry.logical_clock,
        "op": entry.op,
        "payload": entry.payload,
        "updated_at": entry.updated_at.isoformat(),
    }


def get_outbox_since(db: Session, after_clock: int) -> list[dict]:
    """Return serialized outbox entries after a given global clock."""

    stmt: Select[tuple[models.SyncOutbox]] = (
        select(models.SyncOutbox)
        .where(models.SyncOutbox.id > after_clock)
        .order_by(models.SyncOutbox.id)
    )
    entries = db.execute(stmt).scalars().all()
    return [serialize_outbox(e) for e in entries]


def apply_inbound_changes(db: Session, changes: Iterable[dict]) -> None:
    """Apply inbound changes using a last-write-wins policy."""

    for change in changes:
        entity = change["entity"]
        entity_id = change["entity_id"]
        clock = change["logical_clock"]
        updated_at = datetime.fromisoformat(change["updated_at"])
        op = change["op"]
        payload = change.get("payload")

        last = db.execute(
            select(models.SyncOutbox.logical_clock, models.SyncOutbox.updated_at)
            .where(
                models.SyncOutbox.entity == entity,
                models.SyncOutbox.entity_id == entity_id,
            )
            .order_by(models.SyncOutbox.logical_clock.desc())
            .limit(1)
        ).first()

        if last:
            local_clock, local_updated_at = last
            if (clock, updated_at) <= (local_clock, local_updated_at):
                continue

        Model = ENTITY_MODELS.get(entity)
        if not Model:
            continue

        obj = db.get(Model, entity_id)
        if op == "delete":
            if obj:
                db.delete(obj)
        else:
            if obj:
                for k, v in (payload or {}).items():
                    if k != "id":
                        setattr(obj, k, v)
            else:
                db.add(Model(**(payload or {})))

        db.add(
            models.SyncOutbox(
                entity=entity,
                entity_id=entity_id,
                logical_clock=clock,
                op=op,
                payload=payload,
                updated_at=updated_at,
            )
        )


def push_outbox(db: Session, api: str, post_fn=httpx.post) -> None:
    """Push local outbox entries to a remote API."""

    changes = get_outbox_since(db, 0)
    post_fn(f"{api}/sync/push", json={"changes": changes})


def pull_updates(db: Session, api: str, get_fn=httpx.get) -> None:
    """Pull remote changes and apply them locally."""

    after = db.execute(select(func.max(models.SyncOutbox.id))).scalar() or 0
    resp = get_fn(f"{api}/sync/pull", params={"after_clock": after})
    payload = resp.json()
    changes = payload.get("changes", [])
    apply_inbound_changes(db, changes)
    db.commit()


def main() -> None:
    """CLI entry point for pushing or pulling sync changes."""

    import argparse
    from .. import db as _db

    parser = argparse.ArgumentParser(description="Sync CLI")
    parser.add_argument("--api", required=True, help="Base API URL")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--push", action="store_true", help="Push local changes")
    group.add_argument("--pull", action="store_true", help="Pull remote changes")
    args = parser.parse_args()

    with _db.SessionLocal() as session:
        if args.push:
            push_outbox(session, args.api)
        else:
            pull_updates(session, args.api)


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()

