# app/crud/clients.py
from datetime import date, datetime
from typing import Optional

from sqlalchemy.orm import Session
from sqlalchemy import and_, or_, extract

from .. import models, schemas
from ..services.phone import normalize_phone
def _dob_filter(q: str):
    """Return a SQLAlchemy expression for DOB matching based on the query.

    Supports formats:
    - DD-MM-YYYY or DD/MM/YYYY for exact date matches
    - DD-MM or DD/MM for day-month matches (any year)
    """

    for fmt in ("%d-%m-%Y", "%d/%m/%Y"):
        try:
            dt = datetime.strptime(q, fmt).date()
            return models.Client.dob == dt
        except ValueError:
            continue

    for fmt in ("%d-%m", "%d/%m"):
        try:
            dt = datetime.strptime(q, fmt)
            return and_(
                extract("day", models.Client.dob) == dt.day,
                extract("month", models.Client.dob) == dt.month,
            )
        except ValueError:
            continue

    return None


def list_clients(
    db: Session,
    q: str = "",
    *,
    first: str = "",
    last: str = "",
    email: str = "",
    phone: str = "",
    dob_from: Optional[date] = None,
    dob_to: Optional[date] = None,
):
    query = db.query(models.Client)

    if q:
        q_like = f"%{q.lower()}%"
        filters = [
            models.Client.first_name.ilike(q_like),
            models.Client.last_name.ilike(q_like),
            models.Client.email.ilike(q_like),
            models.Client.phone.ilike(q_like),
        ]
        dob_expr = _dob_filter(q)
        if dob_expr is not None:
            filters.append(dob_expr)
        query = query.filter(or_(*filters))

    if first:
        query = query.filter(models.Client.first_name.ilike(f"%{first.lower()}%"))
    if last:
        query = query.filter(models.Client.last_name.ilike(f"%{last.lower()}%"))
    if email:
        query = query.filter(models.Client.email.ilike(f"%{email.lower()}%"))
    if phone:
        query = query.filter(models.Client.phone.ilike(f"%{phone.lower()}%"))
    if dob_from:
        query = query.filter(models.Client.dob >= dob_from)
    if dob_to:
        query = query.filter(models.Client.dob <= dob_to)

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
