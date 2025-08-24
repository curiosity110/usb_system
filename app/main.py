"""Entry point for the FastAPI application."""
from __future__ import annotations

from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from . import db, models, routes
from .services import backups
from apscheduler.schedulers.background import BackgroundScheduler

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

models.Base.metadata.create_all(bind=db.engine)

templates = Jinja2Templates(directory="app/templates")


scheduler = BackgroundScheduler()
scheduler.add_job(backups.backup_db, "cron", hour=2, minute=30)
scheduler.start()


@app.get("/", response_class=HTMLResponse)
def home(request: Request, db_session: Session = Depends(db.get_db)):
    client_count = db_session.query(func.count(models.Client.id)).scalar() or 0
    trip_count = db_session.query(func.count(models.Trip.id)).scalar() or 0
    booking_count = db_session.query(func.count(models.Booking.id)).scalar() or 0
    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "client_count": client_count,
            "trip_count": trip_count,
            "booking_count": booking_count,
        },
    )


@app.post("/admin/backup-now", response_class=PlainTextResponse)
def backup_now() -> str:
    backups.backup_db()
    return "Backup created"


# Include routers for resources
app.include_router(routes.clients.router)
app.include_router(routes.trips.router)
app.include_router(routes.bookings.router)
