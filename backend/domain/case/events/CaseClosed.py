from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CaseClosed:
    """Domain event representing the factual occurrence of a case being closed.

    This event is an immutable fact and does not trigger behavior.
    """

    case_id: str
    closed_at: datetime
    version: int
