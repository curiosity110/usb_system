from __future__ import annotations

from datetime import date, datetime
from pydantic import BaseModel, EmailStr, Field


class ClientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    dob: date | None = None


class ClientCreate(ClientBase):
    pass


class ClientRead(ClientBase):
    id: int
    created_at: datetime
    updated_at: datetime | None = None

    class Config:
        orm_mode = True


class TripBase(BaseModel):
    name: str
    start_date: date | None = None
    end_date: date | None = None


class TripCreate(TripBase):
    pass


class TripRead(TripBase):
    id: int

    class Config:
        orm_mode = True


class BookingCreate(BaseModel):
    client_id: int
    trip_id: int


class BookingRead(BookingCreate):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True
