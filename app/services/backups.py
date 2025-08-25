# app/services/backups.py
"""Database backup utilities."""
from __future__ import annotations

import os
import shutil
from datetime import datetime
from pathlib import Path

def backup_db() -> Path:
    db_path = Path(os.getenv("DB_PATH", "./data/astraion.db")).resolve()
    if not db_path.exists():
        raise FileNotFoundError(f"Database not found at {db_path}")
    backups_dir = db_path.parent / "backups"
    backups_dir.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d-%H%M")
    backup_path = backups_dir / f"{ts}.db"
    shutil.copy(db_path, backup_path)
    return backup_path
