"""Define's boundary mappers — procedure step 3.3.

Canonical: **S-F10** (`define_input_mapper`) and **S-F11**
(`define_output_mapper`), both marked *Rebuild test: met*. Architecture §9.

Define is the one phase whose framing does NOT come from a prior gate
document — it has no prior phase, so its source is the case record written to
the Store at session start (§9, §10).

**Execution site** (S-F10): a mapper runs inside the PARENT's uniquely-named
node function for this phase, not inside the subgraph. That node calls the
input mapper, invokes the compiled subgraph, and calls the output mapper on
the way back. It does not add a sixth node — §13's five-node rule governs the
subgraph, and this runs one level up. The unique node name is load-bearing:
checkpoint namespaces for subgraphs invoked inside node functions are assigned
by CALL ORDER, so reordering could mix up which subgraph loads which state.
"""
from __future__ import annotations

from typing import Any

from langgraph.store.base import BaseStore

from backend.core.state import SupervisorState
from backend.core.substate import PhaseState
from backend.phases.mappers_common import (
    advance,
    new_phase_state,
    read_case_record,
    write_gate_document,
)

PHASE = "define"


def define_input_mapper(parent: SupervisorState, store: BaseStore) -> PhaseState:
    """`SupervisorState` → `PhaseState` for Define.

    Context is composed HERE, at the boundary, and never carried on parent
    state (S-F10 B3) — `project_context` was removed from `SupervisorState`
    for exactly this reason, and it had failed instructively: no writer at
    all, and its only reader ran before the point it was meant to be set (§5).

    **Depends on `BaseStore` alone** (S-F10 B1). It is not handed a blob
    client: that would put untracked I/O inside a translation function, and
    the Store is the only mechanism that survives the process ending between
    two sessions nine days apart (§9).
    """
    case = read_case_record(store, parent["case_id"])

    # S-F10's own composition, kept verbatim in shape. `.get` with a labelled
    # fallback rather than `[]`: a case record missing a framing field should
    # produce a slightly thinner prompt, not a KeyError at phase entry — unlike
    # a MISSING GATE DOCUMENT, which is an ordering fault and does raise.
    phase_context = (
        f"{case.get('title', 'this project')} — "
        f"{case.get('department', 'the department')}. "
        f"{case.get('belt_level', 'Belt')} belt, "
        f"led by {case.get('leader', 'the project leader')}, "
        f"target {case.get('target_date', 'date not set')}."
    )
    return new_phase_state(parent, PHASE, phase_context)


def define_output_mapper(
    child: PhaseState,
    parent: SupervisorState,
    store: BaseStore,
) -> dict[str, Any]:
    """`PhaseState` → a `SupervisorState` update, at gate approval.

    The Define subgraph reaches `END` only through `gate_apply_node`, so
    arriving here MEANS the gate passed (§15) — there is no branch to take and
    no verdict to re-check.

    The gate document goes to the Store; **only orchestration-relevant values
    return to the parent** (S-F11 B3). Artifacts and gate documents do not
    travel on parent state — that is §5's structural rule, not a preference.
    """
    write_gate_document(store, parent, PHASE, child)
    return advance(parent, PHASE)


__all__ = ["define_input_mapper", "define_output_mapper", "PHASE"]
