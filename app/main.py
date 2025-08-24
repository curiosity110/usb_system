"""Entry point for the FastAPI application."""

from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
