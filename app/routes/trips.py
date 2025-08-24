from __future__ import annotations

from fastapi import APIRouter, Depends

from .. import schemas, crud
from ..db import get_session

router = APIRouter(prefix="/trips", tags=["trips"])


@router.post("/", response_model=schemas.TripRead)
def create_trip(trip: schemas.TripCreate, session=Depends(get_session)):
    return crud.trips.create(session, trip)


@router.get("/", response_model=list[schemas.TripRead])
def list_trips(session=Depends(get_session)):
    return crud.trips.list(session)
