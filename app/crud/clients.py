from __future__ import annotations

import re
from sqlalchemy import select, func
from sqlalchemy.orm import Session

from .. import models, schemas


def normalize_email(email: str | None) -> str | None:
    if not email:
        return None
    email = email.strip().lower()
    local, _, domain = email.partition("@")
    if domain == "gmail.com":
        local = local.replace(".", "")
    return f"{local}@{domain}"


def normalize_phone(phone: str | None) -> str | None:
    if not phone:
        return None
    digits = re.sub(r"[^0-9+]", "", phone)
    if digits.startswith("+"):
        prefix = "+"
        digits = digits[1:]
    else:
        prefix = ""
    return prefix + digits


def create(session: Session, data: schemas.ClientCreate) -> models.Client:
    email = normalize_email(data.email)
    phone = normalize_phone(data.phone)
    if email:
        existing = session.execute(
            select(models.Client).where(func.lower(models.Client.email) == email)
        ).scalar_one_or_none()
        if existing:
            raise ValueError("email exists")
    if phone:
        existing = session.execute(
            select(models.Client).where(models.Client.phone == phone)
        ).scalar_one_or_none()
        if existing:
            raise ValueError("phone exists")
    client = models.Client(
        first_name=data.first_name,
        last_name=data.last_name,
        email=email,
        phone=phone,
        dob=data.dob,
    )
    session.add(client)
    session.commit()
    session.refresh(client)
    return client


def get(session: Session, client_id: int) -> models.Client | None:
    return session.get(models.Client, client_id)


def list(session: Session) -> list[models.Client]:
    return list(session.execute(select(models.Client)).scalars())
