import re

from app.services import backups


def test_backup_db_creates_timestamped_file(tmp_path):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    db_file = data_dir / "astraion.db"
    db_file.write_text("content")

    backup_dir = data_dir / "backups"
    result = backups.backup_db(db_path=db_file, backup_dir=backup_dir)

    assert result.exists()
    assert result.parent == backup_dir
    assert re.match(r"\d{8}-\d{4}\.db", result.name)
