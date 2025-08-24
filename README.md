# Astraion Travel USB App

## Development Setup

1. **Create and activate a virtual environment** (Python 3.11 required)

```bash
python -m venv .venv
source .venv/bin/activate
```

2. **Install dependencies**

```bash
pip install -e .
pip install pre-commit
pre-commit install
```

3. **Run the development server**

```bash
uvicorn app.main:app --reload
```

4. **Run tests**

```bash
pytest
```

## Policy

- No binaries committed.
