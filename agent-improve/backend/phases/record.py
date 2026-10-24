"""A phase's unfinished work, carried in the checkpoint — ADR-0066, T13.

Unfinished work is a phase's captured values, field statuses and field log before its gate is
approved. Its only home is the checkpoint: the wrapper node (`core/graph.py::phase_node`)
merges each turn's product into the phase's record and attaches the merged record to the turn's
reply as `additional_kwargs["phase_record"]`. The reply is a message on `SupervisorState`, so
the record is saved in the checkpoint with it — no eighth state field, no Store copy, no
case-blob write.

The next turn's input mapper seeds from the newest record of its phase (`new_phase_state`); a
reload reads it through the compiled graph (`gateway/routes.py::_with_unfinished_work`). This
module holds the one merge, so no route keeps a second copy that could disagree with it.
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
    """Fold one turn's product into the record — MERGE, never replace. A capture that is empty
    or not of its declared type does not reach the record; the field statuses are replaced
    whole; the log merges with the channel's own reducer."""
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


#: DEF-219: a reply carries only what its turn changed in the record — marked so a reader folds it onto the record
#: before it; a record without the mark (an older reply) is whole.
DELTA = "delta"
_SCALARS = ("gate_attempts", "gate_fingerprint")


def diff(prev: dict[str, Any], new: dict[str, Any]) -> dict[str, Any]:
    """DEF-219: what `new` changed against `prev` — the changed values, the changed or removed field statuses, the log
    entries added or changed, the new uploads read and citations, the changed counters. Only `phase` and the mark when
    nothing changed."""
    out: dict[str, Any] = {"phase": new.get("phase"), DELTA: True}
    old_s, new_s = dict(prev.get("structured") or {}), dict(new.get("structured") or {})
    if changed := {k: v for k, v in new_s.items() if old_s.get(k) != v}:
        out["structured"] = changed
    old_f, new_f = dict(prev.get("field_status") or {}), dict(new.get("field_status") or {})
    if status := {k: v for k, v in new_f.items() if old_f.get(k) != v}:
        out["field_status"] = status
    if gone := [k for k in old_f if k not in new_f]:
        out["field_status_removed"] = gone
    old_log = list(prev.get("field_log") or [])
    if log := [e for e in (new.get("field_log") or []) if e not in old_log]:
        out["field_log"] = log
    old_c = dict(prev.get("consumed") or {})
    if consumed := {k: v for k, v in (new.get("consumed") or {}).items() if old_c.get(k) != v}:
        out["consumed"] = consumed
    known = {_citation_key(c) for c in prev.get("citations") or []}
    if cites := [c for c in new.get("citations") or [] if _citation_key(c) not in known]:
        out["citations"] = cites
    for key in _SCALARS:
        if key in new and new.get(key) != prev.get(key):
            out[key] = new[key]
    return out


def changed(delta: dict[str, Any]) -> bool:
    """Whether a delta carries any change at all."""
    return any(k not in ("phase", DELTA) for k in delta)


def apply_delta(prev: dict[str, Any] | None, rec: dict[str, Any], phase: str) -> dict[str, Any]:
    """DEF-219: `rec` folded onto `prev` — a delta adds its changes; a record without the mark replaces `prev` whole."""
    if not rec.get(DELTA):
        return {k: v for k, v in rec.items() if k != DELTA}
    base = prev or empty(phase)
    status = {f: dict(v) for f, v in (base.get("field_status") or {}).items()
              if f not in (rec.get("field_status_removed") or [])}
    status.update({f: dict(v) for f, v in (rec.get("field_status") or {}).items()})
    out = {**base, "phase": phase,
           "structured": {**dict(base.get("structured") or {}), **dict(rec.get("structured") or {})},
           "field_status": status,
           "field_log": merge_field_log([dict(e) for e in base.get("field_log") or []],
                                        [dict(e) for e in rec.get("field_log") or []]),
           "consumed": {**dict(base.get("consumed") or {}), **dict(rec.get("consumed") or {})},
           "citations": [*(base.get("citations") or []), *(rec.get("citations") or [])]}
    for key in _SCALARS:
        if key in rec:
            out[key] = rec[key]
    return out


def _folded(messages: Iterable[Any], phase: str) -> dict[str, Any] | None:
    """The record of `phase` as the messages carry it: every reply's record folded on, oldest first."""
    out: dict[str, Any] | None = None
    for m in messages:
        rec = (getattr(m, "additional_kwargs", None) or {}).get(KEY)
        if isinstance(rec, dict) and rec.get("phase") == phase:
            out = apply_delta(out, rec, phase)
    return out


def for_reply(payload: dict[str, Any], messages: Iterable[Any], phase: str) -> dict[str, Any]:
    """ADR-0109 — the turn's payload as the reply stores it: the record and the turn's `field_status` without the kept
    verdicts, and the verdicts under `KEPT_KEY` only when they differ from the newest ones before this turn.

    DEF-219: the record rides only as what this turn changed against the record
    the messages already carry (none when nothing changed); the turn's `field_status` and `field_log` beside it are
    the changed statuses and the added entries — never whole copies."""
    msgs = list(messages or [])
    out = dict(payload)
    full = dict(out.get(KEY) or {})
    stripped, kept = split(full.get("field_status"))
    prev = _folded(msgs, phase) or {}
    prev = {**prev, "field_status": split(prev.get("field_status"))[0]}
    delta = diff(prev, {**full, "field_status": stripped})
    out.pop(KEY, None)
    if changed(delta):
        out[KEY] = delta
    out["field_status"] = dict(delta.get("field_status") or {})
    out["field_log"] = list(delta.get("field_log") or [])
    if kept != latest_kept(msgs, phase):
        out[KEPT_KEY] = {"phase": phase, "verdicts": kept}
    return out


def latest(messages: Iterable[Any], phase: str) -> dict[str, Any] | None:
    """The record of `phase` the messages carry — their records folded, oldest first (DEF-219) — with the newest kept
    verdicts joined in (ADR-0109), or None."""
    msgs = list(messages or [])
    rec = _folded(msgs, phase)
    return _joined(rec, latest_kept(msgs, phase)) if rec is not None else None


def latest_by_phase(messages: Iterable[Any]) -> dict[str, dict[str, Any]]:
    """The record of every phase the messages carry, each folded and with its kept verdicts joined in."""
    msgs = list(messages or [])
    phases = []
    for m in msgs:
        rec = (getattr(m, "additional_kwargs", None) or {}).get(KEY)
        if isinstance(rec, dict) and rec.get("phase") and rec["phase"] not in phases:
            phases.append(rec["phase"])
    return {p: _joined(_folded(msgs, p) or empty(p), latest_kept(msgs, p)) for p in phases}


__all__ = ["KEY", "KEPT_KEY", "VERDICT_KEYS", "DELTA", "empty", "merge", "diff", "apply_delta", "latest", "latest_by_phase", "latest_kept",
           "split", "for_reply"]
