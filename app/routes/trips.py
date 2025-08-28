# app/routes/trips.py
from typing import Annotated
from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session, selectinload

from .. import crud, db, models
from ..schemas import TripCreate  # concrete schema

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/trips", response_class=HTMLResponse)
def list_trips_page(request: Request, db_session: Session = Depends(db.get_db)):
    today = date.today()
    trips = (
        db_session.query(models.Trip)
        .options(selectinload(models.Trip.bookings))
        .order_by(models.Trip.created_at.desc())
        .all()
    )
    upcoming = [t for t in trips if t.start_date is None or t.start_date >= today]
    past = [t for t in trips if t.start_date is not None and t.start_date < today]
    tab = request.query_params.get("tab", "upcoming")
    return templates.TemplateResponse(
        "trips/list.html",
        {
            "request": request,
            "upcoming": upcoming,
            "past": past,
            "tab": tab,
        },
    )


@router.get("/trips/new", response_class=HTMLResponse)
def new_trip_page(request: Request):
    return templates.TemplateResponse("trips/new.html", {"request": request})


@router.post("/trips", response_class=HTMLResponse)
def create_trip(
    request: Request,
    trip_in: Annotated[TripCreate, Depends(TripCreate.as_form)],
    db_session: Session = Depends(db.get_db),
):
    trip = crud.trips.create_trip(db_session, trip_in)
    return RedirectResponse(url="/trips", status_code=status.HTTP_303_SEE_OTHER)


@router.get("/trips/{trip_id}", response_class=HTMLResponse)
def trip_detail_page(
    request: Request, trip_id: int, db_session: Session = Depends(db.get_db)
):
    trip = crud.trips.get_trip(db_session, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")

    bookings = crud.bookings.list_bookings_for_trip(db_session, trip_id)
    return templates.TemplateResponse(
        "trips/detail.html",
        {"request": request, "trip": trip, "bookings": bookings},
    )
