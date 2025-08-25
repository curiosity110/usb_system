"""Routes for trip resources."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

import csv
import io

from .. import crud, db, schemas
from ..services import audit

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
    logs = audit.get_logs(db_session, entity="trip", entity_id=trip_id)
    return templates.TemplateResponse(
        "trips/detail.html", {"request": request, "trip": trip, "logs": logs}
    )


@router.post("/trips", response_model=schemas.TripRead, status_code=status.HTTP_201_CREATED)
def create_trip(trip_in: schemas.TripCreate, db_session: Session = Depends(db.get_db)):
    return crud.trips.create_trip(db_session, trip_in)


@router.get("/trips/export")
def export_trips(db_session: Session = Depends(db.get_db)):
    trips = crud.trips.list_trips(db_session)
    stream = io.StringIO()
    writer = csv.writer(stream)
    writer.writerow(["ID", "Name"])
    for trip in trips:
        writer.writerow([trip.id, trip.name])
    stream.seek(0)
    headers = {"Content-Disposition": "attachment; filename=trips.csv"}
    return StreamingResponse(
        iter([stream.getvalue()]),
        media_type="text/csv",
        headers=headers,
    )
