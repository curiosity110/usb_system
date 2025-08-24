"""Pydantic models for request and response bodies."""

from pydantic import BaseModel


class Item(BaseModel):
    """Example schema."""
    id: int
    name: str
