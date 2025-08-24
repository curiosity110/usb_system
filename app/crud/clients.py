"""CRUD operations for Client objects."""
from __future__ import annotations

from sqlalchemy import Select, func, or_, select
from sqlalchemy.orm import Session

from .. import models, schemas
from ..services import audit, sync
from ..services.phone import normalize_phone


def create_client(db: Session, client_in: schemas.ClientCreate) -> models.Client:
    """Create a new client ensuring email and phone normalization."""
    client = models.Client(
        name=client_in.name,
        email=client_in.email.lower(),
        phone=client_in.phone,
        normalized_phone=normalize_phone(client_in.phone),
        dob=client_in.dob,
    )
    db.add(client)
    db.flush()
    sync.enqueue_outbox(
        db,
        entity="client",
        entity_id=client.id,
        op="create",
        payload={
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "normalized_phone": client.normalized_phone,
            "dob": client.dob.isoformat() if client.dob else None,
        },
    )
    audit.log_action(
        db,
        action="create",
        entity="client",
        entity_id=client.id,
        before=None,
        after={
            "id": client.id,
            "name": client.name,
            "email": client.email,
            "phone": client.phone,
            "dob": client.dob.isoformat() if client.dob else None,
        },
    )
    db.commit()
    db.refresh(client)
    return client


def get_client(db: Session, client_id: int) -> models.Client | None:
    return db.get(models.Client, client_id)


def list_clients(db: Session, query: str | None = None) -> list[models.Client]:
    stmt: Select[tuple[models.Client]] = select(models.Client)
    if query:
        pattern = f"%{query.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(models.Client.name).like(pattern),
                func.lower(models.Client.email).like(pattern),
                models.Client.phone.like(f"%{query}%"),
            )
        )
    return db.execute(stmt).scalars().all()
