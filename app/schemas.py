# app/schemas.py
from datetime import date, datetime
from fastapi import Form
from pydantic import BaseModel, EmailStr
from pydantic import ConfigDict
from sqlalchemy import String



# -------------------------
# Clients
# -------------------------
def _none_if_blank(s: str | None) -> str | None:
    s = (s or "").strip()
    return s or None

# Shared config for ORM mode (Pydantic v2)
class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

class ClientBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr | None = None
    phone: str | None = None
    dob: date | None = None

class ClientCreate(ClientBase):
    @classmethod
    def as_form(
        cls,
        first_name: str = Form(...),
        last_name: str = Form(...),
        email: EmailStr | None = Form(None),
        phone: str | None = Form(None),
        dob: str | None = Form(None),  # <-- string from form
    ) -> "ClientCreate":
        dob_val = date.fromisoformat(dob) if dob else None
        return cls(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone=phone,
            dob=dob_val,
        )

class ClientRead(ORMModel, ClientBase):
    id: int
    uuid: str
    normalized_phone: str | None = None
    created_at: datetime


# -------------------------
# Trips
# -------------------------
class TripBase(BaseModel):
    name: str
    destination: str | None = None
    start_date: date | None = None
    end_date: date | None = None
    notes: str | None = None


class TripCreate(TripBase):
    @classmethod
    def as_form(
        cls,
        name: str = Form(...),
        destination: str | None = Form(None),
        start_date: date | None = Form(None),
        end_date: date | None = Form(None),
        notes: str | None = Form(None),
    ) -> "TripCreate":
        return cls(
            name=name,
            destination=destination,
            start_date=start_date,
            end_date=end_date,
            notes=notes,
        )


class TripRead(ORMModel, TripBase):
    id: int
    created_at: datetime
    updated_at: datetime


# -------------------------
# Bookings
# -------------------------
class BookingBase(BaseModel):
    client_id: int
    trip_id: int
    status: str | None = None
    notes: str | None = None


class BookingCreate(BookingBase):
    @classmethod
    def as_form(
        cls,
        client_id: int = Form(...),
        trip_id: int = Form(...),
        status: str | None = Form(None),
        notes: str | None = Form(None),
    ) -> "BookingCreate":
        return cls(
            client_id=client_id,
            trip_id=trip_id,
            status=status,
            notes=notes,
        )


class BookingRead(ORMModel, BookingBase):
    id: int
    created_at: datetime
    updated_at: datetime