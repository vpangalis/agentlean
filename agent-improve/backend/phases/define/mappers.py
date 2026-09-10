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
    read_case_record,
    uploads_for_phase,
    write_gate_document,
)

logger = logging.getLogger(__name__)

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

    # ── THE FALLBACK IS KEPT AND MADE LOUD (step 6.8) ─────────────────
    #
    # **The fallback itself is legitimate** and stays: a case record missing
    # one framing field should thin the prompt, not fail phase entry. What was
    # wrong was that it fired in TOTAL SILENCE. From 6.3, when the coach first
    # started being handed this context, to 6.8, EVERY prompt in the system was
    # composed from these labels — *"this project — the department. Belt belt,
    # led by the project leader"* — because WATCH 19's writer did not exist.
    # No error, no empty prompt, no log line. Six steps.
    #
    # **A silent fallback around a missing wire is the shape this project keeps
    # getting caught by** (§0.16's unfireable cap, §26's undeclared field, this).
    # So it is said in two places, because they have different readers: WARNING
    # for whoever reads logs, and a marker inside `phase_context` itself for
    # whoever reads the prompt in LangSmith and would otherwise see plausible
    # prose with nothing to distinguish it from the real thing.
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

    # Step 6.11: `case` is already in hand, so Define's uploads cost no
    # second Store read — the inventory rides the record the framing came from.
    return new_phase_state(
        parent, PHASE, phase_context,
        uploads_for_phase(case, PHASE), asks_for_phase(case, PHASE),
    )


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
