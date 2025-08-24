from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from .. import schemas, crud
from ..db import get_session

router = APIRouter(prefix="/clients", tags=["clients"])


@router.post("/", response_model=schemas.ClientRead)
def create_client(client: schemas.ClientCreate, session=Depends(get_session)):
    try:
        return crud.clients.create(session, client)
    except ValueError as exc:  # duplicate
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/", response_model=list[schemas.ClientRead])
def list_clients(session=Depends(get_session)):
    return crud.clients.list(session)
