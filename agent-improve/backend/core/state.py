"""Graph state schemas.

Holds TWO schemas:

* `SupervisorState` — the v2 Level 1 orchestration state.
* `ImproveGraphState` — the v1 schema, kept while a v1 consumer still reads
  it; both coexist until the last v1 consumer is gone.
"""
from __future__ import annotations

import operator
from typing import Annotated, TypedDict, Optional

from langchain_core.messages import BaseMessage

#: ADR-0065 (T88): the version of every state class and phase record this release writes — into
#: each checkpoint's metadata, each Store record and each case blob. Raised by one with EVERY change
#: to `SupervisorState`, `PhaseState`, a `{Phase}Output` or a phase record, together with its
#: migration in `core/migrations.py` and that migration's fixture test. Never lowered.
STATE_SCHEMA_VERSION = 14
#: What each version changed is the docstring of its migration in `core/migrations.py`
#: (`migrate_vN_to_vN+1`); version 1 is everything written before versioning (ADR-0065).


class SupervisorState(TypedDict):
    """The Level 1 orchestration state — orchestration ONLY.

    This class must be reconstructable from the ratified state definition
    alone, so the fields and reducers below are transcribed from it rather
    than designed here.

    **Exactly seven fields. Adding an eighth requires an amendment.**

    It is a `TypedDict` and not a Pydantic model because it is consumed by
    `create_agent`-based nodes, which do not support Pydantic state.

    **Captured fields and gate documents are NOT here.** They live on
    `PhaseState` (`core/substate.py`) and in the Store. Putting them
    back is a violation, and a structural one rather than a stylistic one.

    Four fields are redundant and may not return: `dmaic_plan`
    (DMAIC order is fixed and static), `key_decisions`, `open_items`
    (derived by `check_gate_status()`), and `project_context` (composed at
    the boundary by each input mapper). The test any proposed eighth
    field must pass: **name the node that writes it and the node that reads
    it.**
    """

    # Append-only conversation and breadcrumbs — the only two reduced fields.
    messages:      Annotated[list[BaseMessage], operator.add]
    history:       Annotated[list[str], operator.add]

    # Stable project identifier. Also the LangGraph `thread_id` and the first
    # Store namespace segment. Set once, never mutated.
    case_id:       str

    # `phase_index` and `current_phase` are DERIVED from `gate_passed` and
    # stored anyway, as a documented exemption for readability — they are
    # read in dozens of places. The exemption is safe only because they have
    # EXACTLY ONE WRITER: the output mapper at gate approval, which writes
    # all three orchestration values together. Nothing else may write
    # them. A second write site is what turns a derived field into a second
    # source of truth that can disagree with what it was derived from.
    phase_index:   int
    current_phase: str

    # A dict, not a list: `gate_passed["measure"]` is a direct lookup, and
    # the re-approval cascade sets a phase back to False rather than
    # removing it from a list. Both operations stay total. An ABSENT key
    # means "not yet reached" — readers use `.get(phase, False)`; a KeyError
    # here is a contract violation in the reader, not an expected path.
    gate_passed:   dict[str, bool]

    # The assembled final deliverable, written only when Control's gate
    # passes. `None` until then, and callers must read `None` as "project not
    # yet complete" rather than as an error.
    final_output:  Optional[dict]


# The field census, kept next to the schema so the documented count and the
# code's count cannot drift apart silently. Asserted in `test_state.py`.
SUPERVISOR_STATE_FIELDS = (
    "messages", "history", "case_id", "phase_index", "current_phase",
    "gate_passed", "final_output",
)

# Written together, by the output mapper, and by nothing else.
SUPERVISOR_STATE_DERIVED_FIELDS = ("phase_index", "current_phase", "gate_passed")

# Redundant, and may not return without an amendment.
SUPERVISOR_STATE_REMOVED_FIELDS = (
    "dmaic_plan", "key_decisions", "open_items", "project_context",
)


class ImproveGraphState(TypedDict, total=False):
    """Single source of truth for Agent Improve.
    All fields optional (total=False).
    Nodes return dict slices only — never the full state.

    **v1 — superseded by `SupervisorState` above and `PhaseState` in
    `core/substate.py`**, and kept while a v1 consumer (the phases'
    `validate.py`) still reads it."""

    # Case identity — set at session start from blob
    case_id: str | None
    current_phase: str | None          # define|measure|analyse|improve|control
    current_user: str | None           # name of team member active this turn

    # Phase inputs — partial dict built turn by turn from extraction
    # Written by orchestrate nodes, read by validate nodes and UI
    phase_inputs: dict | None

    # Conversation history — append-only, never modified
    # [{turn, role, user, text, timestamp, citations}]
    chat_history: list | None

    # Gate state — reset to 0 on phase advance
    gate_attempts: int
    escalated: bool

    # Citations accumulated this session
    # [CitationRecord dicts] — see core/citations.py
    citations: list | None

    # Analyst output — written after gate pass
    analyst_output: dict | None

    # Uploaded files this session
    # [{filename, blob_path, classification, phase, uploaded_by, uploaded_at}]
    uploaded_files: list | None

    # Case metadata — loaded from blob at session start
    # {title, belt_level, leader, team, created_at, target_date, department}
    case_metadata: dict | None

    # SIPOC diagram payload — written by orchestrate_define when the
    # problem statement is complete, or when a confirmed SIPOC exists.
    # Shape: {suppliers, inputs, process_steps, outputs, customers, draft}
    sipoc_diagram: dict | None

    # Which Define gate section just became complete this turn — written
    # by orchestrate_define. One of: problem_statement|sipoc|goal_scope|
    # business_case|charter, or None.
    section_completed: str | None
