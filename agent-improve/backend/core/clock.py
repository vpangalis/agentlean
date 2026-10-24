"""The one clock: the current time in UTC, timezone-aware — every stamp the product writes reads it."""
from __future__ import annotations

from datetime import datetime, timezone


def utc_now() -> datetime:
    """Now, in UTC, timezone-aware."""
    return datetime.now(timezone.utc)
