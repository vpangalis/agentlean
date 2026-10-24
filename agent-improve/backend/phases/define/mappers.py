"""Define's boundary mappers.

Define is the one phase whose framing does NOT come from a prior gate
document — it has no prior phase, so its source is the case record written to
the Store at session start.

**Execution site**: a mapper runs inside the PARENT's uniquely-named node
function for this phase, not inside the subgraph. That node calls the input
mapper, invokes the compiled subgraph, and calls the output mapper on the way
back. It does not add a sixth node — the subgraph keeps its five nodes, and
this runs one level up. The unique node name is load-bearing:
checkpoint namespaces for subgraphs invoked inside node functions are assigned
by CALL ORDER, so reordering could mix up which subgraph loads which state.
"""
from __future__ import annotations

import logging
from typing import Any

from langgraph.store.base import BaseStore

from backend.core.state import SupervisorState
from backend.core.substate import PhaseState
from backend.phases.mappers_common import (
    CASE_RECORD_FRAMING_FIELDS,
    advance,
    new_phase_state,
    asks_for_phase,
    captured_for_phase,
    field_log_for_phase,
    field_status_for_phase,
    read_case_record,
    uploads_for_phase,
    write_gate_document,
)

logger = logging.getLogger(__name__)

PHASE = "define"


def define_input_mapper(parent: SupervisorState, store: BaseStore) -> PhaseState:
    """`SupervisorState` → `PhaseState` for Define.

    Context is composed HERE, at the boundary, and never carried on parent
    state: a context field on parent state can be read before anything has
    written it.

    **Depends on `BaseStore` alone.** It is not handed a blob client: that
    would put untracked I/O inside a translation function, and the Store is
    the only mechanism that survives the process ending between two sessions
    days apart.
    """
    case = read_case_record(store, parent["case_id"])

    # `.get` with a labelled fallback rather than `[]`: a case record missing
    # a framing field produces a slightly thinner prompt, not a KeyError at
    # phase entry — unlike a MISSING GATE DOCUMENT, which is an ordering fault
    # and does raise.
    phase_context = (
        f"{case.get('title', 'this project')} — "
        f"{case.get('department', 'the department')}. "
        f"{case.get('belt_level', 'Belt')} belt, "
        f"led by {case.get('leader', 'the project leader')}, "
        f"target {case.get('target_date', 'date not set')}."
    )

    # ── THE FALLBACK IS LOUD ──────────────────────────────────────────
    #
    # A case record missing one framing field thins the prompt rather than
    # failing phase entry, but a silent fallback hides a missing writer: every
    # prompt would read *"this project — the department. Belt belt, led by the
    # project leader"* with no error and no log line. So it is said in two
    # places, because they have different readers: a WARNING for whoever reads
    # logs, and a marker inside `phase_context` itself for whoever reads the
    # prompt in LangSmith and would otherwise see plausible prose with nothing
    # to distinguish it from the real thing.
    missing = [f for f in CASE_RECORD_FRAMING_FIELDS if not case.get(f)]
    if missing:
        detail = "no case record in the Store at all" if not case else (
            f"case record present but missing {', '.join(missing)}")
        logger.warning(
            "define.input_mapper: phase_context FELL BACK to generic labels "
            "for %d of %d framing field(s) — %s. The coach is being framed "
            "with placeholder prose, not this project's facts. Writer is "
            "`write_case_record` (POST /cases, and the lazy backfill on /ask); "
            "if this fires in normal operation, that write is not happening. "
            "case_id=%s",
            len(missing), len(CASE_RECORD_FRAMING_FIELDS), detail,
            parent["case_id"],
        )
        phase_context += (
            f"  [!] PROJECT DETAILS UNAVAILABLE — {len(missing)} of "
            f"{len(CASE_RECORD_FRAMING_FIELDS)} framing fields "
            f"({', '.join(missing)}) are placeholders, not this project's "
            f"values. Do not treat them as facts about this project."
        )

    # `case` is already in hand, so Define's uploads cost no second Store
    # read — the inventory rides the record the framing came from.
    return new_phase_state(
        parent, PHASE, phase_context,
        uploads_for_phase(case, PHASE), asks_for_phase(case, PHASE),
        # The accumulator is SEEDED from the case record, not blanked.
        # `case` is already in hand, so this costs no second read.
        captured_for_phase(case, PHASE), field_log_for_phase(case, PHASE),
        field_status_for_phase(case, PHASE),
    )


def define_output_mapper(
    child: PhaseState,
    parent: SupervisorState,
    store: BaseStore,
) -> dict[str, Any]:
    """`PhaseState` → a `SupervisorState` update, at gate approval.

    The Define subgraph reaches `END` only through `gate_apply_node`, so
    arriving here MEANS the gate passed — there is no branch to take and no
    verdict to re-check.

    The gate document goes to the Store; **only orchestration-relevant values
    return to the parent**. Artifacts and gate documents do not travel on
    parent state — a structural rule, not a preference.
    """
    write_gate_document(store, parent, PHASE, child)
    return advance(parent, PHASE)


__all__ = ["define_input_mapper", "define_output_mapper", "PHASE"]
