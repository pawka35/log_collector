"""Сервисы приложения log_collector."""

from __future__ import annotations

import base64


def decode_base64(field: str) -> bytes:
    """Decode a base64 encoded string."""
    if field and isinstance(field, str):
        return base64.b64decode(field)

    return b''
