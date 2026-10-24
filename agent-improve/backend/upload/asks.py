"""Asks — the coach's recorded requests for data (`PhaseState.asks`).

**AN ASK IS THE LOGICAL IDENTITY OF A DOCUMENT; FILES ARE ITS VERSIONS.** The
binding is recorded *when the coach asks*, never reconstructed afterwards from
a filename.

THE PLANNER DERIVES THE ASK; THE MODEL DOES NOT DECLARE IT
    `CoachingResponse` has no field for "I am asking for data", and adding one
    would be an amendment on a load-bearing schema. It would also be the weaker
    mechanism: **an ask whose existence depends on the model emitting a field
    is absent whenever the model forgets, and nothing anywhere says it should
    have been there.** The planner is code. When it routes to a field with a
    declared shape, the ask exists.

NO CLASSES (`CLAUDE.md`)
    `backend/upload/` is not on the permitted-class list, so an ask is a plain
    dict and everything here is a module-level function.
"""
from __future__ import annotations

import hashlib
import logging
from typing import Any

from backend.core.clock import utc_now

logger = logging.getLogger(__name__)

OPEN = "open"
ANSWERED = "answered"

#: `shape_match` values. `unsolicited` is the honest answer for a file that
#: answers no ask — it is not a failure; unreadable files are refused, which is
#: a different thing from incomplete ones.
FULL, PARTIAL, NONE, UNSOLICITED = "full", "partial", "none", "unsolicited"

#: The MIGRATION SENTINEL, used by the evidence-index backfill
#: (`scripts/backfill_evidence_index.py`).
#:
#: **It lives here rather than in that script.** `role` is a filter value that
#: retrieval, supersession scoping and the uploads entry all read; a role
#: defined only inside a one-off migration would be a value no query filters on
#: and no reviewer can see.
#:
#: **Carried ONLY by uploads that predate the ask-binding.** An upload has
#: either an ask or a declared purpose, and both yield a real role — so a
#: sentinel appearing on a new upload is a write-path defect, not a
#: classification.
SENTINEL_ROLE = "unclassified (pre-ask-binding)"
SENTINEL_KIND = "evidence"
SENTINEL_SHAPE = UNSOLICITED        # true by construction: there was no ask

#: **Measure's shapes.** Only these of Measure's coached fields are answered
#: by a file, so only these appear here. The coaching prose in `skills/dmaic-measure-phase/SKILL.md` teaches
#: the Belt; this structure is what the system validates against, and **the two
#: must agree**.
#:
#: **Keyed by the field the shape answers**, but asks are keyed by `role` —
#: see `open_ask_for_role`. `baseline_mean` and `baseline_sigma` are two fields
#: on one dataset, and stability is usually the same file read as a run chart,
#: so per-field asks would produce three asks for one upload.
#:
#: **`unit` is `None` where it comes from `metric_definitions`.** The primary
#: metric's unit is a project value, not a methodology constant, so hardcoding
#: it here would make the SKILL.md wrong for every project whose metric is not
#: the one the example used.
MEASURE_SHAPES: dict[str, dict[str, Any]] = {
    "baseline_mean": {
        "role": "baseline defect data",
        "columns": ["identifier", "measured value", "date"],
        "unit": None,                      # from metric_definitions
        "period": "the baseline window agreed in the data collection plan",
        "rule": "one row per observation, never pre-aggregated",
    },
    "baseline_sigma": {
        "role": "baseline defect data",
        "columns": ["identifier", "measured value", "date"],
        "unit": None,
        "period": "the baseline window agreed in the data collection plan",
        "rule": "one row per observation, never pre-aggregated",
    },
    "stability_assessment": {
        "role": "baseline defect data",
        "columns": ["measured value", "date or sequence number"],
        "unit": None,
        "period": "long enough to show the process moving",
        "rule": "in collection order — a run chart and a baseline are two "
                "reads of one dataset",
    },
    "measurement_system_validated": {
        # The role vocabulary has NO role for a measurement-system study, and
        # GR&R is not a capability study. `other evidence` is the honest
        # placeholder and is what that row exists for. The vocabulary is
        # extended once, for all four remaining phases, rather than four times.
        "role": "other evidence",
        "columns": ["part", "operator", "trial", "measurement"],
        "unit": None,
        "period": None,                    # a study, not a window
        "rule": "every part measured by every operator, repeated per trial",
    },
}

#: Per phase. Only Measure is populated; the other four phases' shapes are
#: owed, and their empty entries say so rather than hiding it.
SHAPES_BY_PHASE: dict[str, dict[str, dict[str, Any]]] = {
    "define": {},
    "measure": MEASURE_SHAPES,
    "analyse": {},
    "improve": {},
    "control": {},
}


def shape_for_field(phase: str, field: str) -> dict[str, Any] | None:
    """The declared shape for `field` in `phase`, or None if it takes no file."""
    return (SHAPES_BY_PHASE.get(phase) or {}).get(field)


def content_digest(file_bytes: bytes) -> str:
    """SHA-256 of the uploaded bytes — the VERSION identity.

    The same bytes re-uploaded are not a new version; different bytes under the
    same `(case_id, role)` supersede.
    """
    return hashlib.sha256(file_bytes or b"").hexdigest()


def new_ask(phase: str, field: str, shape: dict[str, Any]) -> dict[str, Any]:
    """One ask, in the `PhaseState.asks` entry shape.

    `ask_id` is derived from `(phase, role)` rather than randomly, so the same
    ask is the same id across turns and a checkpoint restore cannot mint a
    duplicate for a request that is already open.
    """
    role = shape["role"]
    return {
        "ask_id": hashlib.sha256(f"{phase}|{role}".encode()).hexdigest()[:16],
        "role": role,
        "expected_shape": {k: v for k, v in shape.items() if k != "role"},
        "phase": phase,
        "asked_at": utc_now().isoformat(),
        "status": OPEN,
        "for_field": field,
    }


def open_ask_for_role(asks: list[dict], role: str) -> dict[str, Any] | None:
    """The open ask for `role`, if one exists.

    **Asks are keyed on ROLE, not on field**, and that is a rule rather than
    an optimisation. Measure's first two shapes are usually one file, and
    `baseline_mean` / `baseline_sigma` are two fields on one dataset — keying
    per field would open three asks for one upload and leave two of them
    permanently unanswered, which is exactly the unread-evidence condition
    `consumed_at` exists to detect.
    """
    for ask in asks or []:
        if ask.get("role") == role and ask.get("status") == OPEN:
            return ask
    return None


def ensure_ask(asks: list[dict], phase: str, field: str) -> list[dict]:
    """`asks` with an ask for `field` present, reusing an open one by role.

    Returns a NEW list; the caller decides whether to write it to state.
    """
    shape = shape_for_field(phase, field)
    if shape is None:
        return list(asks or [])
    existing = open_ask_for_role(asks or [], shape["role"])
    if existing is not None:
        return list(asks or [])
    created = new_ask(phase, field, shape)
    logger.info(
        "%s.planner: opened ask %s for role %r (field %s)",
        phase, created["ask_id"], created["role"], field,
    )
    return [*(asks or []), created]


#: **Methodology label → what a Belt's file actually calls it.**
#: `expected_shape.columns` holds descriptions — "one identifier per
#: observation" — because that is what teaches a Belt in the SKILL.md. **A real
#: export never matches a methodology label literally**: it says `invoice_id`,
#: not `identifier`. Without this table every well-formed file would report a
#: mismatch, and `shape_match` would mean "the Belt did not use our words"
#: rather than "a column is missing".
#:
#: **Generous on purpose.** A false `partial` costs one coaching question about
#: a column that is present. A false `full` lets a genuinely missing column
#: through, which is the thing `shape_match` exists to catch — so the bias runs
#: toward matching, and the coach asks.
_COLUMN_SYNONYMS: dict[str, tuple[str, ...]] = {
    "identifier": ("id", "ref", "reference", "number", "no", "key", "case",
                   "invoice", "order", "item", "unit", "serial"),
    "measured value": ("value", "count", "amount", "measure", "measurement",
                       "result", "qty", "quantity", "defect", "error",
                       "seconds", "minutes", "hours", "duration", "time",
                       "cycle", "score", "rate"),
    "date": ("date", "day", "week", "month", "period", "timestamp", "when"),
    "date or sequence number": ("date", "day", "week", "month", "period",
                                "timestamp", "seq", "sequence", "order",
                                "index", "n", "run"),
    "part": ("part", "item", "unit", "sample", "piece"),
    "operator": ("operator", "appraiser", "inspector", "person", "who",
                 "rater"),
    "trial": ("trial", "repeat", "replicate", "run", "attempt"),
    "measurement": ("measurement", "value", "reading", "result", "measure"),
}


def _matches(declared: str, column: str) -> bool:
    """Whether a Belt's `column` answers a `declared` shape column."""
    token = declared.strip().lower()
    col = column.strip().lower().replace("_", " ")
    if token in col or col in token:
        return True
    return any(
        syn == col or syn in col.split() or f" {syn}" in f" {col}"
        for syn in _COLUMN_SYNONYMS.get(token, ())
    )


def check_shape(
    ask: dict[str, Any] | None, columns: list[str]
) -> tuple[str, list[str]]:
    """`(shape_match, missing_columns)` for a file against an ask.

    **A mismatch is a coaching question, not a rejection**, so this classifies
    and never raises. `unsolicited` is returned for
    a file that answers no ask — an honest label, not a failure.

    Matching is on a normalised substring, not equality: a declared column
    `"measured value"` is answered by `cycle_seconds` only if the Belt named it
    so, and real exports never match a methodology label exactly. **The
    generosity is deliberate** — a false `partial` produces a coaching question
    about a column that is present, which wastes a turn; a false `full` lets a
    missing column through, which is what `shape_match` exists to catch.
    """
    if ask is None:
        return UNSOLICITED, []
    declared = list((ask.get("expected_shape") or {}).get("columns") or [])
    if not declared:
        return UNSOLICITED, []

    missing = [
        str(want) for want in declared
        if not any(_matches(str(want), str(col)) for col in columns or [])
    ]

    if not missing:
        return FULL, []
    if len(missing) == len(declared):
        return NONE, missing
    return PARTIAL, missing


def mark_answered(asks: list[dict], ask_id: str) -> list[dict]:
    """`asks` with `ask_id` marked answered. Returns a new list."""
    return [
        {**a, "status": ANSWERED} if a.get("ask_id") == ask_id else dict(a)
        for a in (asks or [])
    ]
