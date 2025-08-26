# app/crud/clients.py
from sqlalchemy.orm import Session
from sqlalchemy import or_
from datetime import date

from .. import models, schemas
from ..services.phone import normalize_phone


def list_clients(db: Session, q: str = ""):
    query = db.query(models.Client)
    if q:
        q_like = f"%{q.lower()}%"
        conditions = [
            models.Client.first_name.ilike(q_like),
            models.Client.last_name.ilike(q_like),
            models.Client.email.ilike(q_like),
            models.Client.phone.ilike(q_like),
        ]
        try:
            dob = date.fromisoformat(q)
        except ValueError:
            dob = None
        if dob:
            conditions.append(models.Client.dob == dob)
        query = query.filter(or_(*conditions))
    return query.order_by(models.Client.created_at.desc()).all()


def get_client(db: Session, client_id: int):
    return db.query(models.Client).filter(models.Client.id == client_id).first()


def create_client(db: Session, client_in: schemas.ClientCreate):
    client = models.Client(
        first_name=client_in.first_name,
        last_name=client_in.last_name,
        email=(client_in.email or "").lower() if client_in.email else None,
        phone=client_in.phone,
        normalized_phone=normalize_phone(client_in.phone),
        dob=client_in.dob,
    )
    db.add(client)
    db.commit()
    db.refresh(client)
    return client
