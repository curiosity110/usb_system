# Astraion Travel USB App

Local-first travel agency manager that runs from a USB drive. It exposes a
lightweight web interface on `http://localhost:8787` and stores data in a local
SQLite database.

## Development

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]
pre-commit install
uvicorn app.main:app --reload --port 8787
```

## Database

Initialize the database tables:

```bash
python scripts/init_db.py
```

## Tests

```bash
pytest -q
```

## Building the executable

The project uses PyInstaller in one-file mode. The spec file lives in
`packaging/build.spec`.

```bash
pyinstaller packaging/build.spec
```

This produces `dist/Astraion.exe`. Create a `Start.bat` alongside the exe to run
on Windows:

```bat
@echo off
start Astraion.exe run --port 8787
```
