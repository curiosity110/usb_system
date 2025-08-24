from __future__ import annotations

from pathlib import Path
import sys
from pydantic import BaseSettings, Field


def _base_dir() -> Path:
    """Return directory containing the executable or project root."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent

BASE_DIR = _base_dir()
ENV_PATH = BASE_DIR / "config" / "app.env"


class Settings(BaseSettings):
    port: int = Field(8787, alias="PORT")
    db_path: Path = Field(BASE_DIR / "data" / "astraion.db", alias="DB_PATH")
    auto_sync: bool = Field(False, alias="AUTO_SYNC")
    api_url: str = Field("", alias="API_URL")
    log_level: str = Field("INFO", alias="LOG_LEVEL")

    class Config:
        env_file = ENV_PATH
        env_file_encoding = "utf-8"
        case_sensitive = False


settings = Settings()
