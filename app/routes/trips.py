from typing import Annotated
from fastapi import APIRouter, Depends, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from .. import crud, db
from ..schemas import TripCreate             # <-- concrete schema import

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/trips", response_class=HTMLResponse)
def list_trips_page(request: Request, db_session: Session = Depends(db.get_db)):
    trips = crud.trips.list_trips(db_session)
    return templates.TemplateResponse("trips/list.html", {"request": request, "trips": trips})

@router.get("/trips/new", response_class=HTMLResponse)
def new_trip_page(request: Request):
    return templates.TemplateResponse("trips/new.html", {"request": request})

@router.post("/trips", response_class=HTMLResponse)
def create_trip(
    request: Request,
    trip_in: Annotated[TripCreate, Depends(TripCreate.as_form)],         # <-- no “schemas.”
    db_session: Session = Depends(db.get_db),
):
    crud.trips.create_trip(db_session, trip_in)
    return RedirectResponse(url="/trips", status_code=status.HTTP_303_SEE_OTHER)
