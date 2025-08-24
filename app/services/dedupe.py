from __future__ import annotations

from datetime import date
from sqlalchemy.orm import Session
from rapidfuzz import fuzz

from .. import models, schemas
from ..crud.clients import normalize_email, normalize_phone


def _name_score(a_fn: str, a_ln: str, b_fn: str, b_ln: str) -> float:
    a = f"{a_fn} {a_ln}".strip()
    b = f"{b_fn} {b_ln}".strip()
    return fuzz.token_sort_ratio(a, b) / 100


def is_potential_duplicate(data: schemas.ClientCreate, existing: models.Client) -> bool:
    if data.email and existing.email:
        if normalize_email(data.email) == normalize_email(existing.email):
            return True
    if data.phone and existing.phone:
        new_phone = normalize_phone(data.phone)
        exist_phone = normalize_phone(existing.phone)
        if new_phone[-7:] == exist_phone[-7:]:
            if _name_score(data.first_name, data.last_name, existing.first_name, existing.last_name) >= 0.85:
                return True
    if _name_score(data.first_name, data.last_name, existing.first_name, existing.last_name) >= 0.9:
        return True
    return False


def merge_clients(session: Session, primary: models.Client, duplicate: models.Client) -> models.Client:
    """Merge duplicate into primary and delete duplicate."""
    if not primary.created_at or (duplicate.created_at and duplicate.created_at < primary.created_at):
        primary, duplicate = duplicate, primary
    if not primary.email:
        primary.email = duplicate.email
    if not primary.phone:
        primary.phone = duplicate.phone
    # Names: keep longer
    if len(duplicate.first_name) > len(primary.first_name):
        primary.first_name = duplicate.first_name
    if len(duplicate.last_name) > len(primary.last_name):
        primary.last_name = duplicate.last_name
    # DOB: keep earlier
    if duplicate.dob and (not primary.dob or duplicate.dob < primary.dob):
        primary.dob = duplicate.dob
    # move bookings
    for b in duplicate.bookings:
        b.client = primary
    session.delete(duplicate)
    session.commit()
    session.refresh(primary)
    return primary
