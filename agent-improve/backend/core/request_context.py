"""
Request-scoped context for Agent Improve.

Provides a contextvar that carries request_id (and optionally
case_id, phase) from the FastAPI middleware down to any code
running within that request — including async nodes, LLM
callbacks, and tools.

Every request gets a request_id propagated to all child
operations.

Module-level functions only (no classes), per CLAUDE.md.
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


# ── the turn's record — R-F (founder ruling 2026-10-27) and #63 ─────────────
#
# One dict per coaching turn, set by the route before the graph's task is created: the task copies the
# context, so every node of the run sees the SAME dict. Nodes add the time of their step; the executor marks
# the moment the answer exists. The route reads it to log one timing line per step, and — at the hard limit —
# to let a turn whose answer is produced finish its save rather than cancel it.

_turn_var: contextvars.ContextVar[Optional[dict]] = contextvars.ContextVar("agentlean_turn", default=None)


def start_turn(arrived: float) -> dict:
    """A fresh record for this turn: when it arrived (`time.time()`), its steps, and when it was answered."""
    record: dict = {"arrived": arrived, "steps": [], "answered": None}
    _turn_var.set(record)
    return record


def current_turn() -> Optional[dict]:
    """The current turn's record, or None outside a coaching turn."""
    return _turn_var.get()


def turn_step(name: str, seconds: float) -> None:
    """One step's time, on the current turn's record (nothing outside a turn)."""
    record = _turn_var.get()
    if record is not None:
        record["steps"].append((name, round(float(seconds), 2)))


def mark_answered(at: float) -> None:
    """The coach's answer exists (`time.time()`): from here the turn only finishes its steps and its save."""
    record = _turn_var.get()
    if record is not None and record.get("answered") is None:
        record["answered"] = at
