from __future__ import annotations

import base64


def normalize_action(action: str | None) -> str:
    """Canonical action text normalizer. Single source of truth."""
    value = (action or "").strip().upper()
    return value.replace("-", "_").replace(" ", "_")


def decode_base64(data_base64: str) -> bytes:
    """Decode a base64-encoded string to bytes. Returns b"" for empty input."""
    if not data_base64:
        return b""
    return base64.b64decode(data_base64)
