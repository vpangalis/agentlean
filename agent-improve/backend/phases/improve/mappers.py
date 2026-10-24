"""Improve's boundary mappers.

Same contract as Define's mappers with one difference: `phase_context` is
composed from the **prior phase's gate document** in the Store rather than from
the case record.

Execution site, the copy-down invariant and the single-writer rule are
identical to Define's — see `phases/define/mappers.py`.
"""
from __future__ import annotations

from typing import Any

from langgraph.store.base import BaseStore

from backend.core.state import SupervisorState
from backend.core.substate import PhaseState
from backend.phases.mappers_common import (
    advance,
    compose_phase_context,
    new_phase_state,
    read_case_record,
    read_gate_document,
    asks_for_phase,
    captured_for_phase,
    field_log_for_phase,
    field_status_for_phase,
    uploads_for_phase,
    write_gate_document,
)

PHASE = "improve"
PRIOR_PHASE = "analyse"

# ─────────────────────────────────────────────────────────────────────────
# G-27 — this list is the ruling, not a proposal. The contract is compose
# from the Store, named fields only; the ruling fixes which fields of the
# prior gate document travel, in what form, and that `acknowledged_gaps`
# travels too:
#
#   FIELDS  the prior phase's Tier-1 (gate-required) fields, PLUS
#           `phase_metrics` PLUS `acknowledged_gaps`.
#   FORM    `field: value` lines, one per field.
#   TIER 2  EXCLUDED.
#
# WHY TIER 2 IS OUT. A Belt may consciously proceed without a Tier-2 field,
# so framing the next phase with one invites the planner to read a permitted
# absence as a finding. Tier 1 is by definition what the phase could not close
# without, so every value here is one the Belt actually committed to.
#
# WHY `acknowledged_gaps` IS IN, despite being system-generated bookkeeping
# rather than project content: it is the record of what was CONSCIOUSLY
# skipped, and the next planner needs to tell "the Belt decided to proceed
# without this" apart from "nobody asked". Excluding it would make a
# deliberate decision indistinguishable from an oversight — which is the
# distinction the two tiers exist to preserve.
#
# WHY NAMED FIELDS AND NOT PROSE. A value is read out of the structured
# document by key. String-interpolating a previous phase's output into the
# next phase's prompt is BANNED — that is the parse-prose-downstream
# anti-pattern this architecture exists to remove.
# ─────────────────────────────────────────────────────────────────────────
PHASE_CONTEXT_FIELDS: tuple[str, ...] = (
    "root_cause_statement",
    "root_cause_validation",
    "practical_significance",
    "issues_and_barriers",
    "phase_metrics",
    "acknowledged_gaps",
)


def improve_input_mapper(parent: SupervisorState, store: BaseStore) -> PhaseState:
    """`SupervisorState` → `PhaseState` for Improve.

    Reads analyse's approved gate document from the Store and frames this
    phase from named fields of it (G-27). Depends on `BaseStore` alone.

    **A missing prior gate document raises** rather than defaulting: it means
    the analyse gate never applied, which is an ordering fault, and callers
    must not paper over it.
    """
    gate_document = read_gate_document(store, parent["case_id"], PRIOR_PHASE)
    phase_context = compose_phase_context(PHASE, gate_document, PHASE_CONTEXT_FIELDS)
    # The case record supplies the per-phase inventories below, not the
    # framing: `phase_context` comes from the prior gate document above, and
    # `uploads` stays out of the framing prose because the gate document reads
    # the list and the coach reads the prose.
    case = read_case_record(store, parent["case_id"])
    return new_phase_state(
        parent, PHASE, phase_context,
        uploads_for_phase(case, PHASE), asks_for_phase(case, PHASE),
        # The accumulator is SEEDED from the case record, not blanked.
        # `case` is already in hand, so this costs no second read.
        captured_for_phase(case, PHASE), field_log_for_phase(case, PHASE),
        field_status_for_phase(case, PHASE),
    )


def improve_output_mapper(
    child: PhaseState,
    parent: SupervisorState,
    store: BaseStore,
) -> dict[str, Any]:
    """`PhaseState` → a `SupervisorState` update, at gate approval.

    Writes the gate document to the Store and returns only the three
    orchestration values, written together.
    """
    write_gate_document(store, parent, PHASE, child)
    return advance(parent, PHASE)


__all__ = ["improve_input_mapper", "improve_output_mapper",
           "PHASE", "PRIOR_PHASE", "PHASE_CONTEXT_FIELDS"]
