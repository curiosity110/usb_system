from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import crud, db
from ..schemas import ClientCreate            # <-- concrete schema import
from ..services import dedupe, audit
import csv
import io

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/clients", response_class=HTMLResponse)
def list_clients_page(request: Request, q: str = "", db_session: Session = Depends(db.get_db)):
    clients = crud.clients.list_clients(db_session, q)
    return templates.TemplateResponse("clients/list.html", {"request": request, "clients": clients, "q": q})

@router.get("/clients/new", response_class=HTMLResponse)
def new_client_page(request: Request):
    return templates.TemplateResponse("clients/new.html", {"request": request})

@router.post("/clients", response_class=HTMLResponse)
def create_client(
    request: Request,
    client_in: Annotated[ClientCreate, Depends(ClientCreate.as_form)],   # <-- no “schemas.” prefix
    db_session: Session = Depends(db.get_db),
):
    matches = dedupe.find_potential_duplicates(db_session, client_in)
    if matches and not any(score == 1.0 for _, score in matches):
        return templates.TemplateResponse(
            "clients/merge.html",
            {"request": request, "candidate": client_in, "matches": matches},
            status_code=409,
        )

    try:
        client = crud.clients.create_client(db_session, client_in)
    except IntegrityError:
        db_session.rollback()
        return templates.TemplateResponse(
            "clients/new.html",
            {"request": request, "error": "Client with this email or phone already exists."},
            status_code=400,
        )

    return RedirectResponse(url=f"/clients/{client.id}", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/clients/{client_id}", response_class=HTMLResponse)
def client_detail_page(request: Request, client_id: int, db_session: Session = Depends(db.get_db)):
    client = crud.clients.get_client(db_session, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    trips = crud.trips.list_trips(db_session)
    timeline = audit.get_timeline_for_client(db_session, client_id)
    return templates.TemplateResponse(
        "clients/detail.html",
        {"request": request, "client": client, "trips": trips, "timeline": timeline},
    )

# CSV & Excell Exports
@router.get("/clients/export")
def export_clients_csv(q: str = "", db_session: Session = Depends(db.get_db)):
    rows = crud.clients.list_clients(db_session, q)

    def generate():
        buf = io.StringIO()
        writer = csv.writer(buf)
        writer.writerow(["id", "first_name", "last_name", "email", "phone", "dob"])
        yield buf.getvalue(); buf.seek(0); buf.truncate(0)
        for c in rows:
            writer.writerow([
                c.id,
                c.first_name,
                c.last_name,
                c.email or "",
                c.phone or "",
                c.dob.isoformat() if c.dob else "",
            ])
            yield buf.getvalue(); buf.seek(0); buf.truncate(0)

    headers = {"Content-Disposition": "attachment; filename=clients.csv"}
    return StreamingResponse(generate(), media_type="text/csv", headers=headers)