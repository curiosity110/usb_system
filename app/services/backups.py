"""Database backup utilities."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

DB_PATH = Path("data/astraion.db")
BACKUP_DIR = Path("data/backups")


def backup_db(db_path: Path = DB_PATH, backup_dir: Path = BACKUP_DIR) -> Path:
    """Copy the SQLite database to a timestamped backup file.

    Args:
        db_path: Path to the SQLite database file.
        backup_dir: Directory where backups should be stored.

    Returns:
        Path to the created backup file.
    """
    backup_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d-%H%M")
    backup_path = backup_dir / f"{timestamp}.db"
    shutil.copy(db_path, backup_path)
    return backup_path
