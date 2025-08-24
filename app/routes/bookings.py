"""Routes for booking resources."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, db, schemas

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/bookings", response_class=HTMLResponse)
def list_bookings_page(request: Request, db_session: Session = Depends(db.get_db)):
    bookings = crud.bookings.list_bookings(db_session)
    return templates.TemplateResponse(
        "bookings/list.html", {"request": request, "bookings": bookings}
    )


@router.get("/bookings/new", response_class=HTMLResponse)
def new_booking_page(
    request: Request,
    client_id: int | None = None,
    trip_id: int | None = None,
    db_session: Session = Depends(db.get_db),
):
    clients = crud.clients.list_clients(db_session)
    trips = crud.trips.list_trips(db_session)
    return templates.TemplateResponse(
        "bookings/new.html",
        {
            "request": request,
            "clients": clients,
            "trips": trips,
            "client_id": client_id,
            "trip_id": trip_id,
        },
    )


@router.get("/bookings/{booking_id}", response_class=HTMLResponse)
def booking_detail_page(
    request: Request, booking_id: int, db_session: Session = Depends(db.get_db)
):
    booking = crud.bookings.get_booking(db_session, booking_id)
    if not booking:
        raise HTTPException(status_code=404, detail="Booking not found")
    return templates.TemplateResponse(
        "bookings/detail.html", {"request": request, "booking": booking}
    )


@router.post(
    "/bookings",
    response_model=schemas.BookingRead,
    status_code=status.HTTP_201_CREATED,
)
def create_booking(
    booking_in: schemas.BookingCreate, db_session: Session = Depends(db.get_db)
):
    try:
        return crud.bookings.create_booking(db_session, booking_in)
    except IntegrityError as exc:
        db_session.rollback()
        raise HTTPException(
            status_code=400, detail="Booking for this client and trip already exists"
        ) from exc
