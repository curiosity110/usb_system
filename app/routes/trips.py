"""Routes for trip resources."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import crud, db, schemas

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/trips", response_class=HTMLResponse)
def list_trips_page(request: Request, db_session: Session = Depends(db.get_db)):
    trips = crud.trips.list_trips(db_session)
    return templates.TemplateResponse(
        "trips/list.html", {"request": request, "trips": trips}
    )


@router.get("/trips/new", response_class=HTMLResponse)
def new_trip_page(request: Request):
    return templates.TemplateResponse("trips/new.html", {"request": request})


@router.get("/trips/{trip_id}", response_class=HTMLResponse)
def trip_detail_page(
    request: Request, trip_id: int, db_session: Session = Depends(db.get_db)
):
    trip = crud.trips.get_trip(db_session, trip_id)
    if not trip:
        raise HTTPException(status_code=404, detail="Trip not found")
    return templates.TemplateResponse(
        "trips/detail.html", {"request": request, "trip": trip}
    )


@router.post("/trips", response_model=schemas.TripRead, status_code=status.HTTP_201_CREATED)
def create_trip(trip_in: schemas.TripCreate, db_session: Session = Depends(db.get_db)):
    return crud.trips.create_trip(db_session, trip_in)
