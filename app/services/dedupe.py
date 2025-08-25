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


def _full_name(first: str | None, last: str | None) -> str:
    return " ".join([first or "", last or ""]).strip()

def find_potential_duplicates(db: Session, candidate: schemas.ClientCreate):
    cand_email = (candidate.email or "").lower()
    cand_phone = normalize_phone(candidate.phone)
    cand_name  = _full_name(candidate.first_name, candidate.last_name)

    results: list[tuple[models.Client, float]] = []
    for c in db.execute(select(models.Client)).scalars():
        score = 0.0
        # Exact email = certain duplicate
        if c.email and cand_email and c.email.lower() == cand_email:
            score = 1.0
        else:
            if cand_phone and c.normalized_phone and cand_phone == c.normalized_phone:
                score = max(score, 0.9)
            name_score = token_sort_ratio(cand_name, _full_name(c.first_name, c.last_name)) / 100.0
            score = max(score, name_score)

        if score >= 0.85:
            results.append((c, score))
    return sorted(results, key=lambda x: x[1], reverse=True)
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
        booking.client = survivor

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
