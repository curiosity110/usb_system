"""CLI wrapper for synchronization."""
from __future__ import annotations

from .services.sync import main


if __name__ == "__main__":  # pragma: no cover - CLI entry
    main()

