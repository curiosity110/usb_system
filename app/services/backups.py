from __future__ import annotations

import shutil
from datetime import datetime
from pathlib import Path

from ..config import settings

BACKUP_DIR = settings.db_path.parent / "backups"


def backup_now() -> Path:
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    dest = BACKUP_DIR / f"astraion-{ts}.db"
    if settings.db_path.exists():
        shutil.copy2(settings.db_path, dest)
    return dest
