"""`PhaseState` — the Level 2 per-phase subgraph state.

Canonical definition: reference **§58.2 — S-C02**. Architecture rationale: §6.
Procedure step 3.1. S-C02 carries a *rebuild test*: this file's `PhaseState`
must be reconstructable from that entry alone, so the field list, the order
and the reducers below are transcribed from it rather than designed here.

Private to one phase subgraph and checkpointed through the parent's saver
under an auto-managed `checkpoint_ns` (§16). It holds the phase's working
data — the plan in flight, what has been captured, the audit trail, the retry
budget — and it is where every value that must survive context compression
lives (§19.3).

**Explicit `TypedDict`, never `MessagesState` inheritance** (§6). The
dominant content here is structured fields, not conversation;
`MessagesState` is appropriate only where the content genuinely is
conversational exchange, which in this architecture is the deferred debate
subgraph and nothing else.

**Nothing is wired into a graph in this step** (procedure 3.1) — this module
declares the schema and no more. The v1 `ImproveGraphState` in `state.py`
remains the live schema until step 11.1.
"""
from __future__ import annotations

import operator
from typing import Annotated, Any, Optional, TypedDict

from langchain_core.messages import BaseMessage


class PhaseState(TypedDict):
    """Nineteen fields — two identity, three plumbing, fourteen content.

    **Any new field requires a §56 amendment**, whatever category it is
    placed in. `test_state.py` asserts the count and the names.
    """

    # ── identity, copied down by the input mapper (2) ────────────────
    #
    # THE COPY-DOWN INVARIANT (S-C02). Both are copied down from the parent
    # `SupervisorState` by the input mapper at phase entry, from no other
    # source — not config, not a build-time constant. They are READ-ONLY
    # inside the subgraph: no node may return either key in its state-update
    # dict (B9). `SupervisorState.current_phase` stays authoritative and
    # keeps its single writer, the output mapper (§5).
    #
    # This is a boundary-time copy, not a second writer: parent and child are
    # two fields on two schemas, and the child's is derived from the parent's
    # exactly once, at entry.
    case_id:            str
    current_phase:      str

    # ── conversation plumbing (3) ────────────────────────────────────
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]
    phase_context:      str

    # ── content fields (14) ──────────────────────────────────────────
    #
    # `coaching_plan` is ONE typed plan, not a queue — overwritten every time
    # the planner fires (B2). Its canonical type is the `CoachingPlan`
    # Pydantic model at S-C04, which lands with the planner at step 6.1;
    # until then §6 explicitly sanctions `dict[str, Any]` as the interim
    # annotation ("typed is preferred"). Read it by attribute once it is
    # typed — `coaching_plan.retrieval_hops`, never `["retrieval_hops"]` (B7).
    coaching_plan:      Optional[dict[str, Any]]
    field_index:        int

    # `draft`, `belt_edits` and `final` are dicts and NEVER str (B6). A
    # string-typed handoff forces the next node to parse prose out of the
    # last one's output — the anti-pattern this architecture exists to remove.
    draft:              dict[str, Any]

    # Everything captured so far, keyed by field name. Every value is a `str`
    # (§7's field typing law), except the three cross-phase reference dicts
    # (S-C32) and the three structured dicts (S-C33). Also holds
    # `computation_results` — §7 forbids a top-level field for those.
    artifacts:          dict[str, Any]

    # The audit trail: HOW each thing was captured, as against WHAT, which is
    # `artifacts`. The two must stay separate. Dicts only — tuples are
    # banned (§10.3).
    step_log:           Annotated[list[dict[str, Any]], operator.add]

    # The Belt's corrections at gate step 5. NOT the same thing as
    # `validator_feedback` and must never be merged with it: two actors, two
    # moments (§33). Conflating them has the coach read the Belt's own
    # corrections as validation failures.
    belt_edits:         dict[str, Any]
    turn_count:         int
    final:              dict[str, Any]

    # The shared retry counter for the four-layer validation stack (§34).
    # PER PHASE and IN THE CHECKPOINT — never in route scope. v1 held the
    # equivalent counter in route scope, so every request rebuilt it at 0,
    # the cap never fired, and the loop reported attempt 1 indefinitely.
    # This placement is the fix for that specific defect (§6).
    gate_attempts:      int

    # Accumulated per-attempt validation failures. Accumulation is the entire
    # point: the shared cap of 3 is defensible only because each attempt is
    # better informed than the last, and this field carries the memory.
    validator_feedback: list[dict]
    citations:          list[dict]

    # An EMPTY list is meaningful, not merely empty: because
    # `improve_evidence_index` is the only channel through which external
    # data enters (§29.1), an empty `uploads` means the phase reached its
    # conclusions from the Belt's typed statements alone, and a reviewer
    # should be able to see that.
    uploads:            list[dict]

    # Both carry the planned multi-hop chain (§26) and are `[]` / `None` on
    # every single-hop turn in every phase (B5). They are state rather than
    # node locals because LangSmith traces node inputs and outputs, not
    # interpreter locals: held in a local dict they would be invisible in the
    # trace AND lost on checkpoint restore.
    hop_results:        list[str]
    synthesis_output:   Optional[dict]


# The field census, kept next to the schema so the count in §6 and the count
# in the code cannot drift apart silently. Asserted in `test_state.py`.
PHASE_STATE_IDENTITY_FIELDS = ("case_id", "current_phase")
PHASE_STATE_PLUMBING_FIELDS = ("messages", "history", "phase_context")
PHASE_STATE_CONTENT_FIELDS = (
    "coaching_plan", "field_index", "draft", "artifacts", "step_log",
    "belt_edits", "turn_count", "final", "gate_attempts",
    "validator_feedback", "citations", "uploads", "hop_results",
    "synthesis_output",
)

# Read-only inside the subgraph — see the copy-down invariant above. §55.1
# rule 5's check is a grep of every node's return dict for these two keys;
# any hit is a violation.
PHASE_STATE_READ_ONLY_FIELDS = PHASE_STATE_IDENTITY_FIELDS


__all__ = [
    "PhaseState",
    "PHASE_STATE_IDENTITY_FIELDS",
    "PHASE_STATE_PLUMBING_FIELDS",
    "PHASE_STATE_CONTENT_FIELDS",
    "PHASE_STATE_READ_ONLY_FIELDS",
]
