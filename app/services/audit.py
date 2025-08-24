"""Audit logging utilities."""
from __future__ import annotations

from sqlalchemy.orm import Session

from .. import models


def log_action(
    db: Session,
    *,
    action: str,
    entity: str,
    entity_id: int | None,
    before: dict | None,
    after: dict | None,
) -> models.AuditLog:
    """Persist an audit log entry.

    The caller is responsible for committing the session.
    """

    entry = models.AuditLog(
        action=action,
        entity=entity,
        entity_id=entity_id,
        before=before,
        after=after,
    )
    db.add(entry)
    return entry
