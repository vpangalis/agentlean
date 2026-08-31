"""Graph state schemas.

Holds TWO schemas during the v1 → v2 migration:

* `SupervisorState` — the v2 Level 1 orchestration state. Canonical
  definition: reference **§57.2 — S-C01**; rationale §5; procedure step 3.1.
* `ImproveGraphState` — the v1 schema. Still the live one. It is deleted at
  step **11.1**, not here; both coexist until the last v1 consumer is gone.

**Neither is wired into a graph by step 3.1** — that step declares the v2
schemas and nothing else. The v1 capture path is deliberately NOT pointed at
`SupervisorState` (WATCH 7: the Define gate stays inert until step 6.2).
"""
from __future__ import annotations

import operator
from typing import Annotated, TypedDict, Optional

from langchain_core.messages import BaseMessage


class SupervisorState(TypedDict):
    """The Level 1 orchestration state — orchestration ONLY.

    S-C01 carries a *rebuild test*: this class must be reconstructable from
    that entry alone, so the fields and reducers below are transcribed from
    it rather than designed here.

    **Exactly seven fields. Adding an eighth requires a §56 amendment.**

    It is a `TypedDict` and not a Pydantic model because it is consumed by
    `create_agent`-based nodes, which do not support Pydantic state.

    **Captured fields and gate documents are NOT here** (§5). They live on
    `PhaseState` (§6, `core/substate.py`) and in the Store (§9). Putting them
    back is a violation, and a structural one rather than a stylistic one.

    Four fields were removed as redundant and may not return: `dmaic_plan`
    (DMAIC order is fixed and static — §15), `key_decisions`, `open_items`
    (derived by `check_gate_status()`), and `project_context` (composed at
    the boundary by each input mapper — §9). The test any proposed eighth
    field must pass: **name the node that writes it and the node that reads
    it.** `project_context` failed exactly there — it had no writer at all,
    and its only reader ran before the point it was supposed to be set.
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
    # all three orchestration values together (§9). Nothing else may write
    # them. A second write site is what turns a derived field into a second
    # source of truth that can disagree with what it was derived from.
    phase_index:   int
    current_phase: str

    # A dict, not a list: `gate_passed["measure"]` is a direct lookup, and
    # the re-approval cascade (§37) sets a phase back to False rather than
    # removing it from a list. Both operations stay total. An ABSENT key
    # means "not yet reached" — readers use `.get(phase, False)`; a KeyError
    # here is a contract violation in the reader, not an expected path.
    gate_passed:   dict[str, bool]

    # The assembled final deliverable, written only when Control's gate
    # passes. `None` until then, and callers must read `None` as "project not
    # yet complete" rather than as an error.
    final_output:  Optional[dict]


# The field census, kept next to the schema so §5's count and the code's count
# cannot drift apart silently. Asserted in `test_state.py`.
SUPERVISOR_STATE_FIELDS = (
    "messages", "history", "case_id", "phase_index", "current_phase",
    "gate_passed", "final_output",
)

# Written together, by the output mapper, and by nothing else (§5 B2).
SUPERVISOR_STATE_DERIVED_FIELDS = ("phase_index", "current_phase", "gate_passed")

# Removed as redundant in v2 and may not return without a §56 amendment (§5).
SUPERVISOR_STATE_REMOVED_FIELDS = (
    "dmaic_plan", "key_decisions", "open_items", "project_context",
)


class ImproveGraphState(TypedDict, total=False):
    """Single source of truth for Agent Improve.
    All fields optional (total=False).
    Nodes return dict slices only — never the full state.

    **v1 — superseded by `SupervisorState` above and `PhaseState` in
    `core/substate.py`. Deleted at procedure step 11.1**, once the last v1
    consumer is gone. It stays live until then, deliberately: nothing in
    step 3.1 repoints a consumer at the v2 schemas."""

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
