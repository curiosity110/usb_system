"""Pydantic models for request and response bodies."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, EmailStr


class ClientBase(BaseModel):
    name: str
    email: EmailStr
    phone: str | None = None
    dob: date | None = None


class ClientCreate(ClientBase):
    pass


class ClientRead(ClientBase):
    id: int
    uuid: str
    created_at: datetime

    class Config:
        from_attributes = True


class TripBase(BaseModel):
    name: str


class TripCreate(TripBase):
    pass


class TripRead(TripBase):
    id: int

    class Config:
        from_attributes = True


class BookingBase(BaseModel):
    client_id: int
    trip_id: int


class BookingCreate(BookingBase):
    pass


class BookingRead(BookingBase):
    id: int

    class Config:
        from_attributes = True
