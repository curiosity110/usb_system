"""Entry point for the FastAPI application."""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

from apscheduler.schedulers.background import BackgroundScheduler
from fastapi import Depends, FastAPI, Request
from fastapi.responses import HTMLResponse, PlainTextResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func
from sqlalchemy.orm import Session

from . import db, models, routes
from .services import backups

app = FastAPI()


# ----- resource paths that work in dev and PyInstaller one-file -----
def _base_dir() -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(getattr(sys, "_MEIPASS"))
    return Path(__file__).resolve().parents[1]


def resource_path(*parts: str) -> str:
    return str(_base_dir().joinpath(*parts))


STATIC_DIR = resource_path("static")
TEMPLATES_DIR = resource_path("app", "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ----- DB & models -----
models.Base.metadata.create_all(bind=db.engine)

# ----- Scheduler -----
scheduler = BackgroundScheduler()
scheduler.add_job(backups.backup_db, "cron", hour=2, minute=30)
scheduler.start()


# ----- Routes -----
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


app.include_router(routes.clients.router)
app.include_router(routes.trips.router)
app.include_router(routes.bookings.router)
if os.getenv("DEV_SYNC") == "1":
    app.include_router(routes.sync.router)


# ----- CLI entry (USB Start.bat passes --db, --port) -----
def run_server(db_path: str, port: int, logdir: str | None = None):
    os.environ.setdefault("DB_PATH", db_path)
    if logdir:
        os.makedirs(logdir, exist_ok=True)
        os.environ.setdefault("LOG_DIR", logdir)
    import uvicorn

    uvicorn.run("app.main:app", host="127.0.0.1", port=port, log_level="info")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", dest="db_path", default="./data/astraion.db")
    parser.add_argument("--port", dest="port", type=int, default=8787)
    parser.add_argument("--logdir", dest="logdir", default="./logs")
    args = parser.parse_args()
    run_server(args.db_path, args.port, args.logdir)
