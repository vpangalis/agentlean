"""Shared mechanics for the ten boundary mappers — procedure step 3.3.

Architecture: **§9** (the Store and boundary mappers) · canonical entries
**S-F10** (`define_input_mapper`), **S-F11** (`define_output_mapper`) and
**S-F12** (the other four pairs). Schema: **S-C02**.

WHY A SHARED MODULE RATHER THAN FIVE COPIES
    The ten mappers differ in exactly two places — which Store key the input
    mapper reads, and what goes into `phase_context`. Everything else is
    identical: copy identity down, seed `messages`, initialise the other
    author-populated fields, and on the way out write the gate document and
    return the three orchestration values.

    Written out five times that is five copies of a twenty-key dict literal,
    and **the twenty-first field would land in four of them.** That is not a
    hypothetical: this file exists because step 3.1 shipped a nineteen-field
    `PhaseState` while the build target specified twenty-one, and
    `phases/define/validate.py` already carries the lesson in its own words —
    *"two hand-maintained copies of one list is precisely how the three drift
    apart."* The skeleton is built from `PHASE_STATE_AUTHOR_POPULATED_FIELDS`,
    so a schema change breaks the build rather than silently skipping a mapper.

    **Not in Appendix B's `New` file list**, which enumerates
    `phases/{phase}/{graph,nodes,mappers}.py` and no common module. Flagged
    rather than assumed: the alternative is the duplication above.

§0.24 — the Store is used through `BaseStore.get` / `.put` and nothing else.
No blob client, no path building, no serialisation. `AzureBlobStore` (S-C06)
already owns all of that.
"""
from __future__ import annotations

from typing import Any

from langgraph.store.base import BaseStore

from backend.core.state import SupervisorState
from backend.core.substate import (
    PHASE_STATE_AUTHOR_POPULATED_FIELDS,
    PhaseState,
)

#: The fixed DMAIC order. Phase transitions are static (§15) — there is
#: nothing to reason about, so nothing reasons.
PHASE_ORDER: tuple[str, ...] = (
    "define", "measure", "analyse", "improve", "control",
)

#: Store namespace kinds (§9). `gate_documents` is RETIRED and must not return.
KIND_CASE = "case"
KIND_ARTIFACTS = "artifacts"


def prior_phase(phase: str) -> str | None:
    """The phase whose gate document frames `phase`, or None for Define."""
    idx = PHASE_ORDER.index(phase)
    return PHASE_ORDER[idx - 1] if idx else None


def read_case_record(store: BaseStore, case_id: str) -> dict[str, Any]:
    """Define's framing source — the case record written at session start.

    §9: the `case` namespace is a session-start COPY so that mappers depend on
    `BaseStore` alone; `cases/case_{id}.json` stays the system of record.
    """
    item = store.get((("projects"), case_id, KIND_CASE), "record")
    return dict(item.value) if item is not None else {}


def read_gate_document(store: BaseStore, case_id: str, phase: str) -> dict[str, Any]:
    """The approved gate document for `phase`, written by `gate_apply_node`.

    **A `None` here is a real ordering fault, not missing data** (S-C06 failure
    modes): it means the prior gate never applied, and a caller that papers
    over it with a default hides a broken phase transition. So this returns
    `{}` only for the caller to detect — callers MUST NOT treat `{}` as an
    acceptable framing; `compose_phase_context` raises on it.
    """
    item = store.get(("projects", case_id, KIND_ARTIFACTS), phase)
    return dict(item.value) if item is not None else {}


class PriorGateDocumentMissing(RuntimeError):
    """A phase was entered before the previous phase's gate was applied."""


def new_phase_state(
    parent: SupervisorState,
    phase: str,
    phase_context: str,
) -> PhaseState:
    """The twenty author-populated fields, initialised (S-C02 B1).

    **`remaining_steps` is deliberately absent.** It is the one declared field
    the input mapper SHALL NOT populate — LangGraph's execution loop supplies
    it, and writing it here would replace a live managed value with a stale
    integer, which is how the five-hop cap stopped firing in the first place
    (§0.16).

    **`case_id` and `current_phase` are copied down from the parent here, and
    this is their only writer** (S-C02 B4/B8). `current_phase` is taken from
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
        "messages":           list(parent["messages"]),
        "history":            [],
        "phase_context":      phase_context,
        # content
        "coaching_plan":      None,
        "field_index":        0,
        "draft":              {},
        "artifacts":          {},
        "step_log":           [],
        "belt_edits":         {},
        "turn_count":         0,
        "final":              {},
        "gate_attempts":      0,
        "validator_feedback": [],
        "rejection_feedback": [],
        "citations":          [],
        "uploads":            [],
        "hop_results":        [],
        "synthesis_output":   None,
    }

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
    """The three orchestration values, written together (§5 B2, S-F11 B1).

    **This is the single site that writes any of them.** `phase_index` and
    `current_phase` are derived from `gate_passed` and stored for readability;
    §5's exemption is safe only because they have exactly one writer, and this
    is it.

    `gate_passed` is MERGED, never replaced (S-F11 B2) — the re-approval
    cascade (§37) sets a phase back to `False`, and a wholesale replace would
    drop the other phases' entries.

    **Returns orchestration values ONLY** (S-F11 B3), and deliberately does not
    return `case_id` or `current_phase`… except that `current_phase` IS one of
    the three the parent owns. The prohibition in S-C02 B9 / S-F11 B4 is on a
    node *inside the subgraph* returning it; the output mapper runs in the
    PARENT's node function and is `current_phase`'s designated writer.
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

    Idempotent by key (§47), which is what makes the duplication safe:
    `gate_apply_node` (S-F07 B1) already wrote this same document to this same
    key. **Which of the two is the authoritative writer is not stated in either
    section** — recorded as a finding in §66 and not resolved here.
    """
    store.put(("projects", parent["case_id"], KIND_ARTIFACTS), phase, child["final"])


def compose_phase_context(
    phase: str,
    gate_document: dict[str, Any],
    fields: tuple[str, ...],
) -> str:
    """Frame a phase from the prior phase's gate document (S-F12 B1).

    **Named fields, never prose** (S-F12 B4): a value is read out of the
    structured document by key. String-interpolating a previous phase's output
    into the next phase's prompt is BANNED, and the ban is the reason this
    takes a field list rather than a formatted string.

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

    lines = [f"Carried forward from the approved {prior} gate document:"]
    for field in fields:
        value = gate_document.get(field)
        label = field.replace("_", " ")
        lines.append(
            f"- {label}: {value}" if value not in (None, "", [], {})
            else f"- {label}: not captured in {prior}"
        )
    return "\n".join(lines)


__all__ = [
    "PHASE_ORDER", "KIND_CASE", "KIND_ARTIFACTS",
    "PriorGateDocumentMissing",
    "prior_phase", "read_case_record", "read_gate_document",
    "new_phase_state", "advance", "write_gate_document",
    "compose_phase_context",
]
