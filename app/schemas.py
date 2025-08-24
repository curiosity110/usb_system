"""Pydantic models for request and response bodies."""
from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel


class ClientBase(BaseModel):
    name: str
    email: str
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


class VehicleBase(BaseModel):
    plate: str
    model: str
    year: int | None = None
    notes: str | None = None


class VehicleCreate(VehicleBase):
    pass


class VehicleRead(VehicleBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class MaintenanceBase(BaseModel):
    vehicle_id: str
    kind: str
    due_date: date
    notes: str | None = None
    completed_at: datetime | None = None


class MaintenanceCreate(MaintenanceBase):
    pass


class MaintenanceRead(MaintenanceBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ReminderBase(BaseModel):
    scope: str
    ref_id: str | None = None
    title: str
    due_date: date
    assigned_role: str | None = None
    done_at: datetime | None = None


class ReminderCreate(ReminderBase):
    pass


class ReminderRead(ReminderBase):
    id: str

    class Config:
        from_attributes = True
