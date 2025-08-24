"""Application configuration settings."""

from pydantic import BaseModel


class Settings(BaseModel):
    """Base configuration."""

    app_name: str = "astraion-travel-usb-app"


settings = Settings()
