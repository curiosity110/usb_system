"""Routes for client resources."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, db, schemas
from ..services import dedupe

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/clients", response_class=HTMLResponse)
def list_clients_page(
    request: Request, q: str = "", db_session: Session = Depends(db.get_db)
):
    clients = crud.clients.list_clients(db_session, q)
    return templates.TemplateResponse(
        "clients/list.html", {"request": request, "clients": clients, "q": q}
    )


@router.get("/clients/new", response_class=HTMLResponse)
def new_client_page(request: Request) -> HTMLResponse:
    return templates.TemplateResponse("clients/new.html", {"request": request})


@router.get("/clients/{client_id}", response_class=HTMLResponse)
def client_detail_page(
    request: Request, client_id: int, db_session: Session = Depends(db.get_db)
):
    client = crud.clients.get_client(db_session, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return templates.TemplateResponse(
        "clients/detail.html", {"request": request, "client": client}
    )


@router.post(
    "/clients",
    response_model=schemas.ClientRead,
    status_code=status.HTTP_201_CREATED,
)
def create_client(
    request: Request,
    client_in: schemas.ClientCreate,
    db_session: Session = Depends(db.get_db),
):
    matches = dedupe.find_potential_duplicates(db_session, client_in)
    if matches:
        return templates.TemplateResponse(
            "clients/merge.html",
            {"request": request, "candidate": client_in, "matches": matches},
            status_code=409,
        )
    try:
        return crud.clients.create_client(db_session, client_in)
    except IntegrityError as exc:
        db_session.rollback()
        raise HTTPException(
            status_code=400, detail="Client with this email or phone already exists",
        ) from exc


@router.post(
    "/clients/{survivor_id}/merge/{duplicate_id}",
    response_model=schemas.ClientRead,
)
def merge_client_records(
    survivor_id: int,
    duplicate_id: int,
    db_session: Session = Depends(db.get_db),
):
    survivor = crud.clients.get_client(db_session, survivor_id)
    duplicate = crud.clients.get_client(db_session, duplicate_id)
    if not survivor or not duplicate:
        raise HTTPException(status_code=404, detail="Client not found")
    merged = dedupe.merge_clients(db_session, survivor, duplicate)
    return merged
