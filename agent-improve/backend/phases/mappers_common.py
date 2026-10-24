"""Shared mechanics for the ten boundary mappers.

The ten mappers differ in two places only: which Store key the input mapper
reads, and what goes into `phase_context`. Everything else is shared: copy
identity down, seed `messages`, initialise the other author-populated fields,
and on the way out write the gate document and return the three orchestration
values.

One module rather than five copies, so a new `PhaseState` field cannot land in
some mappers and not others. The skeleton is checked against
`PHASE_STATE_AUTHOR_POPULATED_FIELDS`, so a schema change fails loudly rather
than silently skipping a mapper.

The Store is used through `BaseStore.get` / `.put` and nothing else: no blob
client, no path building, no serialisation. `AzureBlobStore` owns all of that.
"""
from __future__ import annotations

from typing import Any

from langgraph.store.base import BaseStore

from backend.storage import layout

from backend.core.guard import without_blocked
from backend.core.state import SupervisorState
from backend.core.substate import (
    PHASE_STATE_AUTHOR_POPULATED_FIELDS,
    PhaseState,
)

#: The fixed DMAIC order. Phase transitions are static — there is
#: nothing to reason about, so nothing reasons.
PHASE_ORDER: tuple[str, ...] = (
    "define", "measure", "analyse", "improve", "control",
)

#: Store namespace kinds. `gate_documents` is retired and must not come back.
KIND_CASE = layout.KIND_CASE
KIND_ARTIFACTS = layout.KIND_ARTIFACTS


def prior_phase(phase: str) -> str | None:
    """The phase whose gate document frames `phase`, or None for Define."""
    idx = PHASE_ORDER.index(phase)
    return PHASE_ORDER[idx - 1] if idx else None


def read_case_record(store: BaseStore, case_id: str) -> dict[str, Any]:
    """Define's framing source — the case record written at session start.

    The `case` namespace is a session-start copy so that mappers depend on
    `BaseStore` alone; `cases/case_{id}.json` stays the system of record.
    """
    item = store.get((layout.STORE_ROOT, case_id, KIND_CASE), layout.CASE_RECORD_KEY)
    return dict(item.value) if item is not None else {}


#: The framing fields `define_input_mapper` composes `phase_context` from.
#: Named here, beside the writer, because the writer has to know what the
#: reader needs.
CASE_RECORD_FRAMING_FIELDS = (
    "title", "department", "belt_level", "leader", "target_date",
)

#: Where the uploads inventory sits inside the Store's `case` record.
#: Not one of the framing fields — it is not part of `phase_context` and
#: must not leak into it. It is carried in this record because the record is
#: already the one thing the input mappers read; a second Store namespace
#: would give `PhaseState.uploads` a writer that the `case` backfill could not
#: keep current.
CASE_RECORD_UPLOADS = "uploads_by_phase"

#: Where each phase's captured values sit inside the Store's `case` record —
#: the seed of `PhaseState.artifacts`, so a value captured on one turn is
#: still there on the next. The mapper is the only thing that builds
#: `PhaseState`, so without this seed nothing captured could reach a gate
#: document.
#:
#: A copy — `cases/case_{id}.json` stays the system of record and this is
#: rebuilt from it by `case_record_from_document` on every turn.
CASE_RECORD_CAPTURED = "captured_by_phase"

#: Where each phase's field change log sits inside the Store's `case` record.
#: Travels beside `CASE_RECORD_CAPTURED` because the log and the values it
#: records must cross the turn boundary together: persisted on different
#: schedules they can disagree, and a value that disagrees with its own
#: history looks like a change that never happened.
CASE_RECORD_FIELD_LOG = "field_log_by_phase"

#: Where the open asks sit inside the Store's `case` record.
#: The upload route cannot read `PhaseState`: an ask is created by the
#: planner during a coaching turn and must be resolvable by an upload arriving
#: moments later, and the route has the case blob and the Store, not the
#: checkpoint. Mirrors `CASE_RECORD_UPLOADS`, for the same reason in the other
#: direction.
CASE_RECORD_ASKS = "asks_by_phase"

#: Where each phase's field statuses sit inside the Store's `case` record
#: (R5). Beside the captured values and their log, for the same reason: the
#: three must cross the turn boundary together.
CASE_RECORD_FIELD_STATUS = "field_status_by_phase"


def case_record_from_document(case: Any) -> dict[str, Any]:
    """The Store's `case` copy, from the blob case document.

    A copy, and not the whole document: the `case` namespace exists so
    mappers depend on `BaseStore` alone; `cases/case_{id}.json` stays the
    system of record. Copying only the framing fields keeps the copy small and
    the drift surface obvious — if the mapper needs another field,
    `CASE_RECORD_FRAMING_FIELDS` is the one place that has to change.
    """
    record: dict[str, Any] = {
        f: getattr(case, f, None) for f in CASE_RECORD_FRAMING_FIELDS
        if getattr(case, f, None)
    }
    record[CASE_RECORD_UPLOADS] = uploads_from_document(case)
    # The captured values and their history, keyed by phase like the uploads
    # inventory above and carried for the same reason: the input mapper reads
    # `BaseStore` and nothing else, so anything it seeds has to arrive through
    # this record.
    record[CASE_RECORD_CAPTURED] = captured_from_document(case)
    record[CASE_RECORD_FIELD_LOG] = field_log_from_document(case)
    record[CASE_RECORD_FIELD_STATUS] = {
        phase: {f: dict(v) for f, v in (getattr(r, "field_status", None) or {}).items()}
        for phase, r in (getattr(case, "phases", {}) or {}).items()
    }
    return record


def captured_from_document(case: Any) -> dict[str, dict[str, Any]]:
    """Every phase's captured values, keyed by phase — the seed of
    `PhaseState.artifacts`.

    Without this seed `artifacts` would be blanked at the start of every turn
    and would always equal `draft`; `draft` is this turn's extraction and
    `artifacts` is the accumulation.

    Keyed by phase, and the whole inventory travels, as in
    `uploads_from_document`: the mapper takes its own slice, and a cross-phase
    view needs no second writer. A copy for mappers to read, rebuilt from
    `cases/case_{id}.json` every turn.
    """
    return {
        phase: dict(getattr(record, "structured", None) or {})
        for phase, record in (getattr(case, "phases", {}) or {}).items()
    }


def field_log_from_document(case: Any) -> dict[str, list[dict[str, Any]]]:
    """Every phase's field change log, keyed by phase."""
    return {
        phase: [dict(e) for e in (getattr(record, "field_log", None) or [])]
        for phase, record in (getattr(case, "phases", {}) or {}).items()
    }


def uploads_from_document(case: Any) -> dict[str, list[dict[str, Any]]]:
    """Every phase's uploads, in the `PhaseState.uploads` entry shape, keyed by
    phase.

    The Store end of `PhaseState.uploads`'s writer: the route persists an
    `UploadRecord` to the case blob, and this carries it to the input mapper.
    Gate assembly reads `PhaseState.uploads`, and an empty list there means the
    phase reached its conclusions from typed statements alone — so an upload
    missing here makes the gate document say that falsely. A file flagged as
    not for the coach is left out (T72).

    Keyed by phase, and the whole inventory travels. The input mapper takes
    its own phase's slice; carrying all five costs a few hundred bytes and
    means a cross-phase view (evidence supersession) needs no second writer.
    A copy for mappers to read; `cases/case_{id}.json` stays the system of
    record.
    """
    inventory: dict[str, list[dict[str, Any]]] = {}
    for phase, record in (getattr(case, "phases", {}) or {}).items():
        entries = []
        for upload in (getattr(record, "uploads", []) or []):
            if getattr(upload, "used_by_coach", True) is False or (
                    isinstance(upload, dict) and upload.get("used_by_coach") is False):
                continue                     # T72: a flagged file never reaches the coach
            if hasattr(upload, "to_phase_state_entry"):
                entries.append(upload.to_phase_state_entry(phase))
            elif isinstance(upload, dict):
                entries.append({**upload, "phase": phase})
        inventory[phase] = entries
    return inventory


def write_case_record(store: BaseStore, case_id: str, record: dict[str, Any]) -> None:
    """Put the case record at `("projects", case_id, "case") / "record"`.

    The writer `read_case_record` depends on: without it every read returns
    `{}` and Define's `phase_context` is composed entirely from labelled
    fallbacks. Idempotent by key, which is what makes the lazy backfill safe
    to run on every turn.
    """
    store.put((layout.STORE_ROOT, case_id, KIND_CASE), layout.CASE_RECORD_KEY, record)


def read_gate_document(store: BaseStore, case_id: str, phase: str) -> dict[str, Any]:
    """The approved gate document for `phase`, written by `gate_apply_node`.

    **A missing document is an ordering fault, not missing data**: it means
    the prior gate never applied, and a caller that papers over it with a
    default hides a broken phase transition. So this returns `{}` only for the
    caller to detect — callers MUST NOT treat `{}` as an acceptable framing;
    `compose_phase_context` raises on it.
    """
    item = store.get((layout.STORE_ROOT, case_id, KIND_ARTIFACTS), phase)
    return dict(item.value) if item is not None else {}


class PriorGateDocumentMissing(RuntimeError):
    """A phase was entered before the previous phase's gate was applied."""


def asks_for_phase(
    case_record: dict[str, Any], phase: str
) -> list[dict[str, Any]]:
    """This phase's asks, from the Store's `case` copy."""
    inventory = case_record.get(CASE_RECORD_ASKS) or {}
    return [dict(a) for a in (inventory.get(phase) or [])]


def write_asks(
    store: BaseStore, case_id: str, phase: str, asks: list[dict[str, Any]]
) -> None:
    """Mirror this phase's asks into the Store copy the upload route reads.

    **Called after a coaching turn, not during one.** The planner writes asks
    to `PhaseState`; this puts them where a route can see them. Idempotent by
    key, like every other write to this record.
    """
    item = store.get((layout.STORE_ROOT, case_id, KIND_CASE), layout.CASE_RECORD_KEY)
    record = dict(item.value) if item is not None else {}
    inventory = dict(record.get(CASE_RECORD_ASKS) or {})
    inventory[phase] = [dict(a) for a in asks or []]
    record[CASE_RECORD_ASKS] = inventory
    store.put((layout.STORE_ROOT, case_id, KIND_CASE), layout.CASE_RECORD_KEY, record)


def uploads_for_phase(
    case_record: dict[str, Any], phase: str
) -> list[dict[str, Any]]:
    """This phase's uploads, in the `PhaseState.uploads` entry shape.

    Returns `[]` when the phase has none — the honest answer, which the gate
    document reads as a phase that worked from typed statements alone.
    """
    inventory = case_record.get(CASE_RECORD_UPLOADS) or {}
    entries = inventory.get(phase) or []
    return [dict(e) for e in entries]


def captured_for_phase(
    case_record: dict[str, Any], phase: str
) -> dict[str, Any]:
    """This phase's captured values, from the Store's `case` copy.

    Returns `{}` when the phase has captured nothing yet.
    """
    inventory = case_record.get(CASE_RECORD_CAPTURED) or {}
    return dict(inventory.get(phase) or {})


def field_status_for_phase(
    case_record: dict[str, Any], phase: str
) -> dict[str, dict[str, Any]]:
    """This phase's field statuses, from the Store's `case` copy (R5).
    `{}` means every field is "not taught"."""
    inventory = case_record.get(CASE_RECORD_FIELD_STATUS) or {}
    return {f: dict(v) for f, v in (inventory.get(phase) or {}).items()}


def field_log_for_phase(
    case_record: dict[str, Any], phase: str
) -> list[dict[str, Any]]:
    """This phase's field change log, from the Store's `case` copy."""
    inventory = case_record.get(CASE_RECORD_FIELD_LOG) or {}
    return [dict(e) for e in (inventory.get(phase) or [])]


def new_phase_state(
    parent: SupervisorState,
    phase: str,
    phase_context: str,
    uploads: list[dict[str, Any]] | None = None,
    asks: list[dict[str, Any]] | None = None,
    artifacts: dict[str, Any] | None = None,
    field_log: list[dict[str, Any]] | None = None,
    field_status: dict[str, dict[str, Any]] | None = None,
) -> PhaseState:
    """The twenty author-populated fields, initialised.

    **`remaining_steps` is deliberately absent.** It is the one declared field
    the input mapper SHALL NOT populate — LangGraph's execution loop supplies
    it, and writing it here would replace a live managed value with a stale
    integer and stop the five-hop cap firing.

    **`case_id` and `current_phase` are copied down from the parent here, and
    this is their only writer.** `current_phase` is taken from
    `phase` rather than from `parent["current_phase"]` so the mapper cannot be
    invoked for one phase while carrying another's identity — the parent's
    value is asserted equal below.
    """
    if parent["current_phase"] != phase:
        raise ValueError(
            f"{phase}_input_mapper invoked while SupervisorState.current_phase "
            f"is {parent['current_phase']!r}. The identity copy-down has one "
            f"source and it is the parent (S-C02 B8)."
        )

    state: PhaseState = {
        # identity — copied down, read-only inside the subgraph
        "case_id":            parent["case_id"],
        "current_phase":      phase,
        # plumbing
        # ADR-0067 — a blocked turn never reaches a model: dropped here, the one way in.
        "messages":           without_blocked(list(parent["messages"])),
        "history":            [],
        "phase_context":      phase_context,
        # content
        "coaching_plan":      None,
        "field_index":        0,
        # THIS TURN's extraction, so it starts empty. The field beneath it is
        # the accumulation.
        "draft":              {},
        # **Seeded, not blanked**: this function is the only thing that builds
        # `PhaseState`, so a constant here would not be a default, it would be
        # a ceiling. `{}` means the phase has captured nothing yet.
        "artifacts":          dict(artifacts or {}),
        "step_log":           [],
        # Seeded for the same reason, and from the same record. The channel's
        # reducer (`merge_field_log`) stops a node REPLACING it; the seed
        # carries it across the turn boundary, which the reducer cannot — the
        # subgraph gets a fresh `checkpoint_ns` per parent turn, so nothing in
        # the child state survives a turn on its own.
        "field_log":          list(field_log or []),
        # Seeded, not blanked (R5): where each field stands.
        "field_status":       {f: dict(v) for f, v in (field_status or {}).items()},
        "belt_edits":         {},
        "turn_count":         0,
        "final":              {},
        "gate_attempts":      0,
        "gate_fingerprint":   "",
        "validator_feedback": [],
        "rejection_feedback": [],
        "citations":          [],
        # **Seeded, not blanked**: the mapper is the only thing that builds
        # this dict, so a constant here would mean no upload could ever reach
        # a gate document.
        "uploads":            list(uploads or []),
        # Seeded from the Store copy for the same reason `uploads` is: the
        # upload route has to resolve an arriving file against an ask created
        # in a coaching turn, and it reads the Store, not the checkpoint.
        "asks":               list(asks or []),
        "hop_results":        [],
        "synthesis_output":   None,
    }

    # ADR-0066 — unfinished work lives in the checkpoint: when the parent's messages carry
    # this phase's record (attached by the wrapper node to each reply), it is the seed. The
    # Store copy seeds only a phase's first turn and cases older than the record.
    from backend.phases import record as _record
    carried = _record.latest(parent.get("messages") or [], phase)
    if carried is not None:
        state["artifacts"] = dict(carried.get("structured") or {})
        state["field_log"] = [dict(e) for e in (carried.get("field_log") or [])]
        state["field_status"] = {f: dict(v) for f, v in (carried.get("field_status") or {}).items()}
        # ADR-0076 (G-150) — failed gate submissions so far: never reset by a new turn.
        state["gate_attempts"] = int(carried.get("gate_attempts") or 0)
        # G-192 — what the last failed submission submitted, so the same one again is not counted.
        state["gate_fingerprint"] = str(carried.get("gate_fingerprint") or "")
        # G-148 (DEF-061) — the citations earlier turns made.
        state["citations"] = [dict(c) for c in (carried.get("citations") or [])]
        # DEF-108 (W5) — an upload a turn read stays read; the Store copy never carries that.
        read = dict(carried.get("consumed") or {})
        state["uploads"] = [{**u, "consumed_at": u.get("consumed_at") or read.get(str(u.get("blob_path")))}
                            for u in state["uploads"]]

    # The skeleton and the schema cannot drift: a field added to
    # PhaseState without a value here fails loudly, at the boundary, rather
    # than surfacing as a KeyError deep inside a coaching turn.
    missing = [f for f in PHASE_STATE_AUTHOR_POPULATED_FIELDS if f not in state]
    if missing:
        raise AssertionError(
            f"input mapper does not populate {missing} — S-C02 B1 requires "
            f"every author-populated field."
        )
    return state


def advance(parent: SupervisorState, phase: str) -> dict[str, Any]:
    """The three orchestration values, written together.

    **This is the single site that writes any of them.** `phase_index` and
    `current_phase` are derived from `gate_passed` and stored for readability;
    storing derived values is safe only because they have exactly one writer,
    and this is it.

    `gate_passed` is MERGED, never replaced — the re-approval cascade sets a
    phase back to `False`, and a wholesale replace would drop the other
    phases' entries.

    **Returns orchestration values ONLY.** `current_phase` is one of the three
    the parent owns: the rule against returning it applies to a node *inside
    the subgraph*; the output mapper runs in the PARENT's node function and is
    `current_phase`'s designated writer.
    """
    idx = PHASE_ORDER.index(phase)
    is_last = idx == len(PHASE_ORDER) - 1
    return {
        "current_phase": "complete" if is_last else PHASE_ORDER[idx + 1],
        "phase_index":   idx if is_last else idx + 1,
        "gate_passed":   {**parent["gate_passed"], phase: True},
    }


def write_gate_document(
    store: BaseStore,
    parent: SupervisorState,
    phase: str,
    child: PhaseState,
) -> None:
    """Put the approved gate document at `("projects", case_id, "artifacts")`.

    Idempotent by key, which is what makes the duplication safe:
    `gate_apply_node` already writes this same document to this same key.
    Which of the two is the authoritative writer is not settled.
    """
    store.put((layout.STORE_ROOT, parent["case_id"], KIND_ARTIFACTS), phase, child["final"])


def compose_phase_context(
    phase: str,
    gate_document: dict[str, Any],
    fields: tuple[str, ...],
) -> str:
    """Frame a phase from the prior phase's gate document.

    **Named fields, never prose**: a value is read out of the structured
    document by key. String-interpolating a previous phase's output into the
    next phase's prompt is BANNED, which is why this takes a field list rather
    than a formatted string.

    A field the prior phase did not capture is rendered as an explicit
    "not captured" line rather than omitted — a planner that cannot tell
    "absent" from "never asked" will not ask.
    """
    prior = prior_phase(phase)
    if not gate_document:
        raise PriorGateDocumentMissing(
            f"{phase} was entered but {prior}'s gate document is not in the "
            f"Store. That is an ordering fault — the {prior} gate never "
            f"applied — not a missing-data condition to default past "
            f"(S-C06 failure modes)."
        )

    # G-252: display names and plain value text, never Python's dict text.
    from backend.middleware.state_injection import display_name, value_text
    lines = [f"Carried forward from the approved {prior} gate document:"]
    for field in fields:
        value = gate_document.get(field)
        label = display_name(prior or phase, field)
        if value in (None, "", [], {}):
            lines.append(f"- {label}: not captured in {prior}")
            continue
        text = value_text(value, "  ")
        lines.append(f"- {label}:" + (f"\n{text}" if isinstance(value, (dict, list)) else f" {text.strip()}"))
    return "\n".join(lines)


__all__ = [
    "PHASE_ORDER", "KIND_CASE", "KIND_ARTIFACTS",
    "CASE_RECORD_FRAMING_FIELDS", "CASE_RECORD_CAPTURED",
    "CASE_RECORD_FIELD_LOG",
    "case_record_from_document", "captured_from_document",
    "field_log_from_document", "captured_for_phase", "field_log_for_phase",
    "field_status_for_phase", "CASE_RECORD_FIELD_STATUS",
    "write_case_record",
    "PriorGateDocumentMissing",
    "prior_phase", "read_case_record", "read_gate_document",
    "new_phase_state", "advance", "write_gate_document",
    "compose_phase_context",
]
