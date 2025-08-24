from __future__ import annotations

from datetime import datetime
from sqlalchemy.orm import Session

from .. import models


def log(session: Session, action: str, model: str, model_id: int, data: dict) -> models.AuditLog:
    entry = models.AuditLog(
        action=action,
        model=model,
        model_id=model_id,
        data=data,
        created_at=datetime.utcnow(),
    )
    session.add(entry)
    session.commit()
    return entry
