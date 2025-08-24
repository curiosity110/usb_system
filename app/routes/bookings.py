from __future__ import annotations

from fastapi import APIRouter, Depends

from .. import schemas, crud
from ..db import get_session

router = APIRouter(prefix="/bookings", tags=["bookings"])


@router.post("/", response_model=schemas.BookingRead)
def create_booking(booking: schemas.BookingCreate, session=Depends(get_session)):
    return crud.bookings.create(session, booking)


@router.get("/", response_model=list[schemas.BookingRead])
def list_bookings(session=Depends(get_session)):
    return crud.bookings.list(session)
