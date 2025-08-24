"""Duplicate detection and merging utilities."""
from __future__ import annotations

from datetime import date
from typing import List, Tuple

from rapidfuzz.fuzz import token_sort_ratio
from sqlalchemy import select
from sqlalchemy.orm import Session

from .. import models, schemas
from . import audit
from .phone import normalize_phone


def normalized_email(email: str) -> str:
    """Normalize email for comparison.

    For Gmail addresses dots in the local part are ignored and comparison is
    case-insensitive.
    """

    local, domain = email.lower().split("@")
    if domain in {"gmail.com", "googlemail.com"}:
        local = local.replace(".", "")
    return f"{local}@{domain}"


def find_potential_duplicates(
    db: Session, candidate: schemas.ClientCreate
) -> List[Tuple[models.Client, float]]:
    """Return potential duplicates for the candidate client."""

    results: List[Tuple[models.Client, float]] = []
    norm_email = normalized_email(candidate.email)
    norm_phone = normalize_phone(candidate.phone)
    phone_tail = norm_phone[-7:] if norm_phone else None

    existing_clients = db.execute(select(models.Client)).scalars().all()
    for existing in existing_clients:
        # email match rule
        if norm_email == normalized_email(existing.email):
            results.append((existing, 1.0))
            continue

        name_sim = token_sort_ratio(candidate.name, existing.name) / 100
        # name + dob rule
        if candidate.dob and existing.dob:
            if candidate.dob == existing.dob and name_sim >= 0.9:
                results.append((existing, name_sim))
                continue
        # name + phone rule
        if phone_tail and existing.normalized_phone:
            if existing.normalized_phone[-7:] == phone_tail and name_sim >= 0.85:
                results.append((existing, name_sim))
                continue

    return results


def _name_preference(n1: str | None, n2: str | None) -> str | None:
    """Choose better name preferring non-empty and longer tokenized strings."""

    if n1 and not n2:
        return n1
    if n2 and not n1:
        return n2
    if not n1 and not n2:
        return None
    tokens1 = len(n1.split())
    tokens2 = len(n2.split())
    if tokens2 > tokens1:
        return n2
    if tokens1 > tokens2:
        return n1
    return n2 if len(n2) > len(n1) else n1


def _client_to_dict(client: models.Client) -> dict:
    return {
        "id": client.id,
        "name": client.name,
        "email": client.email,
        "phone": client.phone,
        "dob": client.dob.isoformat() if client.dob else None,
    }


def merge_clients(db: Session, a: models.Client, b: models.Client) -> models.Client:
    """Merge two client records and return the surviving one."""

    # Determine survivor by oldest created_at then id
    if (a.created_at, a.id) <= (b.created_at, b.id):
        survivor, duplicate = a, b
    else:
        survivor, duplicate = b, a

    before = {"survivor": _client_to_dict(survivor), "duplicate": _client_to_dict(duplicate)}

    survivor.name = _name_preference(survivor.name, duplicate.name)
    if not survivor.email:
        survivor.email = duplicate.email
    if not survivor.phone:
        survivor.phone = duplicate.phone
        survivor.normalized_phone = duplicate.normalized_phone
    if duplicate.dob and (not survivor.dob or duplicate.dob < survivor.dob):
        survivor.dob = duplicate.dob

    # Re-point foreign keys
    for booking in list(duplicate.bookings):
        booking.client_id = survivor.id

    db.delete(duplicate)
    audit.log_action(
        db,
        action="merge",
        entity="client",
        entity_id=survivor.id,
        before=before,
        after=_client_to_dict(survivor),
    )
    db.commit()
    db.refresh(survivor)
    return survivor
