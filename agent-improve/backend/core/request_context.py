"""
Request-scoped context for Agent Improve.

Provides a contextvar that carries request_id (and optionally
case_id, phase) from the FastAPI middleware down to any code
running within that request — including async nodes, LLM
callbacks, and tools.

Per CLAUDE.md §9.3 and ARCHITECTURE.md §10.3 every request
gets a request_id propagated to all child operations.

Module-level functions only (no classes) per CLAUDE.md §2.
contextvars.ContextVar is a stdlib primitive, not a class
we define — its use is permitted.
"""

from __future__ import annotations

import contextvars
import uuid
from typing import Optional

# ContextVars survive across `await` points in asyncio
_request_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "agentlean_request_id", default=None
)
_case_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "agentlean_case_id", default=None
)
_phase_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    "agentlean_phase", default=None
)


def new_request_id() -> str:
    """Generate a fresh request id (UUID4)."""
    return str(uuid.uuid4())


def set_request_id(value: str) -> None:
    _request_id_var.set(value)


def get_request_id() -> Optional[str]:
    return _request_id_var.get()


def set_case_id(value: Optional[str]) -> None:
    _case_id_var.set(value)


def get_case_id() -> Optional[str]:
    return _case_id_var.get()


def set_phase(value: Optional[str]) -> None:
    _phase_var.set(value)


def get_phase() -> Optional[str]:
    return _phase_var.get()


def current_context() -> dict:
    """Snapshot of the current request context (for log enrichment)."""
    return {
        "request_id": _request_id_var.get(),
        "case_id": _case_id_var.get(),
        "phase": _phase_var.get(),
    }
