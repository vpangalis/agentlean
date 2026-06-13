"""
Logging configuration for Agent Improve.

Per CLAUDE.md §9.3 and ARCHITECTURE.md §10.3, every log line
includes request_id, case_id, and phase pulled from the
request_context contextvars when available.

Module-level functions only per CLAUDE.md §2. The logging.Filter
subclass is a stdlib extension point, not a domain class — its
use is permitted (analogous to extending BaseSettings for config).
"""

from __future__ import annotations

import logging
import sys

from backend.core.request_context import current_context


class _ContextFilter(logging.Filter):
    """
    Inject request_context fields onto every LogRecord so the
    formatter can emit them. If a field is None it renders as '-'.
    """

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: D401
        ctx = current_context()
        record.request_id = ctx.get("request_id") or "-"
        record.case_id = ctx.get("case_id") or "-"
        record.phase = ctx.get("phase") or "-"
        return True


_FORMAT = (
    "%(asctime)s %(levelname)s [%(name)s] "
    "rid=%(request_id)s case=%(case_id)s phase=%(phase)s "
    "%(message)s"
)


def configure_logging(level: str = "INFO") -> None:
    """
    Configure root logger with the context-aware formatter.

    Safe to call multiple times — replaces existing handlers
    rather than appending.
    """
    root = logging.getLogger()
    root.setLevel(level.upper())

    # Remove any handlers from a previous basicConfig call
    for handler in list(root.handlers):
        root.removeHandler(handler)

    handler = logging.StreamHandler(stream=sys.stdout)
    handler.setFormatter(logging.Formatter(_FORMAT))
    handler.addFilter(_ContextFilter())
    root.addHandler(handler)
