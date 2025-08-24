"""Application configuration settings."""

from pydantic import BaseSettings


class Settings(BaseSettings):
    """Base configuration loaded from environment variables."""

    app_name: str = "astraion-travel-usb-app"

    class Config:
        env_file = ".env"


settings = Settings()
