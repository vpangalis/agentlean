"""Control's boundary mappers — procedure step 3.3.

Canonical: **S-F12** (the Measure, Analyse, Improve and Control mapper pairs).
Same contract as S-F10 / S-F11 with one difference: `phase_context` is composed
from the **prior phase's gate document** in the Store rather than from the case
record. Architecture §9.

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
    read_gate_document,
    write_gate_document,
)

PHASE = "control"
PRIOR_PHASE = "improve"

# ─────────────────────────────────────────────────────────────────────────
# G-27 — RATIFIED 2026-08-31. This list is the ruling, not a proposal.
#
# S-F12 stated the CONTRACT (compose from the Store, named fields only) and
# left the COMPOSITION open: which fields of the prior gate document, in what
# form, and whether `acknowledged_gaps` travels. All three are now ruled:
#
#   FIELDS  the prior phase's Tier-1 (gate-required) fields per CLAUDE.md
#           §9.7, PLUS `phase_metrics` PLUS `acknowledged_gaps`.
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
# distinction §9.7 created the two tiers to preserve in the first place.
#
# WHY NAMED FIELDS AND NOT PROSE. §9 B4: a value is read out of the structured
# document by key. String-interpolating a previous phase's output into the
# next phase's prompt is BANNED — that is the parse-prose-downstream
# anti-pattern this architecture exists to remove.
# ─────────────────────────────────────────────────────────────────────────
PHASE_CONTEXT_FIELDS: tuple[str, ...] = (
    "selected_solution",
    "pilot_result",
    "experiment_justification",
    "issues_and_barriers",
    "phase_metrics",
    "acknowledged_gaps",
)


def control_input_mapper(parent: SupervisorState, store: BaseStore) -> PhaseState:
    """`SupervisorState` → `PhaseState` for Control.

    Reads improve's approved gate document from the Store and frames this
    phase from named fields of it (S-F12 B1, B4, G-27 ruling). Depends on `BaseStore`
    alone.

    **A missing prior gate document raises** rather than defaulting: it means
    the improve gate never applied, which is an ordering fault, and S-C06's
    failure modes are explicit that callers must not paper over it.
    """
    gate_document = read_gate_document(store, parent["case_id"], PRIOR_PHASE)
    phase_context = compose_phase_context(PHASE, gate_document, PHASE_CONTEXT_FIELDS)
    return new_phase_state(parent, PHASE, phase_context)


def control_output_mapper(
    child: PhaseState,
    parent: SupervisorState,
    store: BaseStore,
) -> dict[str, Any]:
    """`PhaseState` → a `SupervisorState` update, at gate approval.

    Writes the gate document to the Store and returns only the three
    orchestration values, written together (S-F12 B3, §5 B2).
    """
    write_gate_document(store, parent, PHASE, child)
    return advance(parent, PHASE)


__all__ = ["control_input_mapper", "control_output_mapper",
           "PHASE", "PRIOR_PHASE", "PHASE_CONTEXT_FIELDS"]
