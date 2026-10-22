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
    return {"phase": phase, "structured": {}, "field_status": {}, "field_log": [], "consumed": {},
            "citations": []}


def _citation_key(c: dict[str, Any]) -> tuple[str, str]:
    return (str(c.get("index_name") or ""), str(c.get("document_id") or ""))


def merge(prior: dict[str, Any], payload: dict[str, Any], phase: str) -> dict[str, Any]:
    """Fold one turn's product into the record — MERGE, never replace (step 6.33). A capture
    that is empty or not of its declared type does not reach the record (step 6.48); the field
    statuses are replaced whole (step 6.61); the log merges with the channel's own reducer."""
    structured: dict[str, Any] = dict(prior.get("structured") or {})
    status: dict[str, dict[str, Any]] = {f: dict(v) for f, v in (prior.get("field_status") or {}).items()}
    log: list[dict[str, Any]] = [dict(e) for e in (prior.get("field_log") or [])]
    # DEF-108 (W5) — the uploads a turn has read, {blob_path: when}: kept, never unread again.
    consumed: dict[str, str] = {**dict(prior.get("consumed") or {}),
                                **dict(payload.get("uploads_consumed") or {})}
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
    # G-148 (DEF-061) — the coach's citations, kept across turns (one per source document).
    cites: dict[tuple[str, str], dict[str, Any]] = {_citation_key(c): dict(c) for c in prior.get("citations") or []}
    for c in payload.get("citations") or []:
        cites.setdefault(_citation_key(c), dict(c))
    out = {"phase": phase, "structured": structured, "field_status": status, "field_log": log,
           "consumed": consumed, "citations": list(cites.values()),
           # ADR-0076 (G-150): failed gate submissions so far — replaced by each submission's count.
           "gate_attempts": int(payload["gate_attempts"] if "gate_attempts" in payload
                                else prior.get("gate_attempts") or 0),
           # G-192: what the last failed submission submitted — replaced by each submission's.
           "gate_fingerprint": str(payload["gate_fingerprint"] if "gate_fingerprint" in payload
                                   else prior.get("gate_fingerprint") or "")}
    return out


#: ADR-0109 — the kept verdicts in an element's `field_status` entry (`validation/kept.py`, DEF-098's offer).
VERDICT_KEYS = ("judged", "gate", "offered")
#: ADR-0109 — the reply key that carries them, only on the reply whose turn changed them.
KEPT_KEY = "kept_verdicts"


def split(field_status: dict[str, Any] | None) -> tuple[dict[str, dict[str, Any]], dict[str, dict[str, Any]]]:
    """`field_status` without its kept verdicts, and the verdicts alone ({element: {key: value}})."""
    stripped: dict[str, dict[str, Any]] = {}
    kept: dict[str, dict[str, Any]] = {}
    for field, entry in (field_status or {}).items():
        entry = dict(entry or {})
        held = {k: entry.pop(k) for k in VERDICT_KEYS if k in entry}
        stripped[field] = entry
        if held:
            kept[field] = held
    return stripped, kept


def latest_kept(messages: Iterable[Any], phase: str) -> dict[str, dict[str, Any]]:
    """The newest kept verdicts of `phase`: from the newest reply that carries them, or — for a reply written before
    ADR-0109 — from the newest record holding them inline. `{}` when there are none."""
    for m in reversed(list(messages or [])):
        extra = getattr(m, "additional_kwargs", None) or {}
        carried = extra.get(KEPT_KEY)
        if isinstance(carried, dict) and carried.get("phase") == phase:
            return {f: dict(v) for f, v in (carried.get("verdicts") or {}).items()}
        rec = extra.get(KEY)
        if isinstance(rec, dict) and rec.get("phase") == phase:
            _, inline = split(rec.get("field_status"))
            if inline:
                return inline
    return {}


def _joined(rec: dict[str, Any], kept: dict[str, dict[str, Any]]) -> dict[str, Any]:
    status = {f: dict(v) for f, v in (rec.get("field_status") or {}).items()}
    for field, held in kept.items():
        status.setdefault(field, {}).update(held)
    return {**rec, "field_status": status}


def for_reply(payload: dict[str, Any], messages: Iterable[Any], phase: str) -> dict[str, Any]:
    """ADR-0109 — the turn's payload as the reply stores it: the record and the turn's `field_status` without the kept
    verdicts, and the verdicts under `KEPT_KEY` only when they differ from the newest ones before this turn."""
    out = dict(payload)
    full = dict(out.get(KEY) or {})
    stripped, kept = split(full.get("field_status"))
    out[KEY] = {**full, "field_status": stripped}
    if isinstance(out.get("field_status"), dict):
        out["field_status"] = split(out["field_status"])[0]
    if kept != latest_kept(messages, phase):
        out[KEPT_KEY] = {"phase": phase, "verdicts": kept}
    return out


def latest(messages: Iterable[Any], phase: str) -> dict[str, Any] | None:
    """The newest record of `phase` carried by a message, with the newest kept verdicts joined in (ADR-0109), or None."""
    msgs = list(messages or [])
    for m in reversed(msgs):
        rec = (getattr(m, "additional_kwargs", None) or {}).get(KEY)
        if isinstance(rec, dict) and rec.get("phase") == phase:
            return _joined(rec, latest_kept(msgs, phase))
    return None


def latest_by_phase(messages: Iterable[Any]) -> dict[str, dict[str, Any]]:
    """The newest record of every phase the messages carry, each with its kept verdicts joined in."""
    msgs = list(messages or [])
    out: dict[str, dict[str, Any]] = {}
    for m in reversed(msgs):
        rec = (getattr(m, "additional_kwargs", None) or {}).get(KEY)
        if isinstance(rec, dict) and rec.get("phase") and rec["phase"] not in out:
            out[rec["phase"]] = _joined(rec, latest_kept(msgs, rec["phase"]))
    return out


__all__ = ["KEY", "KEPT_KEY", "VERDICT_KEYS", "empty", "merge", "latest", "latest_by_phase", "latest_kept",
           "split", "for_reply"]
