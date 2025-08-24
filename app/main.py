from __future__ import annotations

import logging
from pathlib import Path
import typer
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from .config import settings
from .db import Base, engine
from .routes import clients, trips, bookings, home

logging.basicConfig(level=settings.log_level)

app = FastAPI(title="Astraion Travel")
app.include_router(home.router)
app.include_router(clients.router)
app.include_router(trips.router)
app.include_router(bookings.router)

static_dir = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


def init_db():
    Base.metadata.create_all(bind=engine)


cli = typer.Typer()


@cli.command()
def run(port: int = settings.port):
    """Run the web server."""
    import uvicorn

    init_db()
    uvicorn.run("app.main:app", port=port, log_level=settings.log_level.lower())


@cli.command()
def sync(push: bool = False, pull: bool = False, api: str = ""):
    """Placeholder sync command."""
    if push:
        typer.echo(f"Would push to {api}")
    if pull:
        typer.echo(f"Would pull from {api}")


if __name__ == "__main__":
    cli()
