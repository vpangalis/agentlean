"""Structured errors for external service failures — CLAUDE.md §12.3.

One schema for every external service failure, so the circuit breaker can
read `severity` to decide retry-vs-stop and the fallback chain can read
`retry_recommendation` to choose its backoff strategy (§4.8).
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class AgentImproveError(BaseModel):
    """Canonical external-failure envelope (§12.3)."""

    error_code: str              # "TIMEOUT", "RATE_LIMIT", "AUTH_FAILURE", …
    severity: str                # "transient" | "permanent"
    retry_recommendation: str    # "retry_after_backoff" | "do_not_retry" | …
    affected_identifier: str
    message: str
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc)
    )

    def to_step_log_entry(self, **extra: Any) -> dict[str, Any]:
        """Render as a `step_log` dict — §10.3 shape, named keys, never a
        tuple.

        `step_log` does not exist on `ImproveGraphState` yet; it arrives with
        `PhaseState` in refactor step 4.1. Until then callers log this dict
        through `logging`. Once `PhaseState` lands, a node holding this error
        appends the same dict to `step_log` with no reshaping.
        """
        entry = {
            "service": self.affected_identifier,
            "status": "failed",
            "error_code": self.error_code,
            "severity": self.severity,
            "retry_recommendation": self.retry_recommendation,
            "reason": self.message,
            "timestamp": self.timestamp.isoformat(),
        }
        entry.update(extra)
        return entry


class KnowledgeSearchError(Exception):
    """Raised when an Azure AI Search retrieval fails.

    Exists so callers can distinguish "retrieval broke" from "retrieval ran
    and matched nothing". Collapsing those two into an empty list is the bug
    this type prevents: a broken index filter looked exactly like a corpus
    with no relevant content, and stayed invisible for months.
    """

    def __init__(self, error: AgentImproveError) -> None:
        super().__init__(error.message)
        self.error = error
