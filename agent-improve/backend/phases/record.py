"""A phase's unfinished work, carried in the checkpoint — ADR-0066 (ACCEPTED), T13.

Unfinished work is a phase's captured values, field statuses and field log before its gate is
approved. Its only home is the checkpoint: the wrapper node (`core/graph.py::phase_node`)
merges each turn's product into the phase's record and attaches the merged record to the turn's
reply as `additional_kwargs["phase_record"]`. The reply is a message on `SupervisorState`, so
the record is saved in the checkpoint with it — no eighth state field, no Store copy, no
case-blob write.

The next turn's input mapper seeds from the newest record of its phase (`new_phase_state`); a
reload reads it through the compiled graph (`gateway/routes.py::_with_unfinished_work`). The
merge is the one the `/ask` route used to apply to the case blob (step 6.33, 6.48, 6.61), moved
here unchanged so the two cannot disagree.
"""
from __future__ import annotations

import logging
from typing import Any, Iterable

from backend.core.substate import merge_field_log, split_captures
from backend.phases.gate_registry import split_by_declared_type

logger = logging.getLogger(__name__)

KEY = "phase_record"


def empty(phase: str) -> dict[str, Any]:
    return {"phase": phase, "structured": {}, "field_status": {}, "field_log": []}


def merge(prior: dict[str, Any], payload: dict[str, Any], phase: str) -> dict[str, Any]:
    """Fold one turn's product into the record — MERGE, never replace (step 6.33). A capture
    that is empty or not of its declared type does not reach the record (step 6.48); the field
    statuses are replaced whole (step 6.61); the log merges with the channel's own reducer."""
    structured: dict[str, Any] = dict(prior.get("structured") or {})
    status: dict[str, dict[str, Any]] = {f: dict(v) for f, v in (prior.get("field_status") or {}).items()}
    log: list[dict[str, Any]] = [dict(e) for e in (prior.get("field_log") or [])]
    captured, empty_fields = split_captures(payload.get("v1_draft") or {})
    captured, malformed = split_by_declared_type(phase, captured)
    if malformed:
        logger.warning("%s: FINDING — %d capture(s) did not carry their declared type and did NOT "
                       "reach the record: %s (step 6.48)", phase, len(malformed),
                       ", ".join(f"{f} (needs {t})" for f, t in sorted(malformed.items())))
    if empty_fields:
        logger.warning("%s: FINDING — %d capture(s) arrived with no value and did NOT reach the "
                       "record: %s (step 6.33)", phase, len(empty_fields), ", ".join(empty_fields))
    structured.update(captured)
    if payload.get("field_status"):
        status = {f: dict(v) for f, v in payload["field_status"].items()}
    entries = list(payload.get("field_log") or [])
    if entries:
        log = merge_field_log(log, entries)
    out = {"phase": phase, "structured": structured, "field_status": status, "field_log": log}
    return out


def latest(messages: Iterable[Any], phase: str) -> dict[str, Any] | None:
    """The newest record of `phase` carried by a message, or None."""
    for m in reversed(list(messages or [])):
        rec = (getattr(m, "additional_kwargs", None) or {}).get(KEY)
        if isinstance(rec, dict) and rec.get("phase") == phase:
            return rec
    return None


def latest_by_phase(messages: Iterable[Any]) -> dict[str, dict[str, Any]]:
    """The newest record of every phase the messages carry."""
    out: dict[str, dict[str, Any]] = {}
    for m in reversed(list(messages or [])):
        rec = (getattr(m, "additional_kwargs", None) or {}).get(KEY)
        if isinstance(rec, dict) and rec.get("phase") and rec["phase"] not in out:
            out[rec["phase"]] = rec
    return out


__all__ = ["KEY", "empty", "merge", "latest", "latest_by_phase"]
