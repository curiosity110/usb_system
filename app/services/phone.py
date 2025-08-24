"""Utilities for working with phone numbers."""
from __future__ import annotations

import re


def normalize_phone(phone: str | None) -> str | None:
    """Normalize a phone number for uniqueness comparisons.

    - Strip all non-digit characters.
    - Keep the leading '+' if present on the original input.
    - Compare based on the last seven digits which helps avoid
      issues with country codes and formatting differences.

    Returns ``None`` when no digits are present.
    """
    if not phone:
        return None

    phone = phone.strip()
    plus = phone.startswith("+")
    digits = re.sub(r"\D", "", phone)
    if not digits:
        return None

    # Use only the last seven digits for comparisons
    digits = digits[-7:]
    return ("+" if plus else "") + digits
