from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, db
from ..schemas import BookingCreate          # <-- concrete schema import

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/bookings", response_class=HTMLResponse)
def list_bookings_page(request: Request, db_session: Session = Depends(db.get_db)):
    bookings = crud.bookings.list_bookings(db_session)
    return templates.TemplateResponse("bookings/list.html", {"request": request, "bookings": bookings})

@router.get("/bookings/new", response_class=HTMLResponse)
def new_booking_page(request: Request, db_session: Session = Depends(db.get_db)):
    clients = crud.clients.list_clients(db_session)
    trips = crud.trips.list_trips(db_session)
    return templates.TemplateResponse("bookings/new.html", {"request": request, "clients": clients, "trips": trips})

@router.post("/bookings", response_class=HTMLResponse)
def create_booking(
    request: Request,
    booking_in: Annotated[BookingCreate, Depends(BookingCreate.as_form)],  # <-- no “schemas.”
    db_session: Session = Depends(db.get_db),
):
    try:
        crud.bookings.create_booking(db_session, booking_in)
    except IntegrityError:
        db_session.rollback()
        return templates.TemplateResponse(
            "bookings/new.html",
            {"request": request, "error": "That client is already booked on this trip."},
            status_code=400,
        )
    return RedirectResponse(url="/bookings", status_code=status.HTTP_303_SEE_OTHER)
