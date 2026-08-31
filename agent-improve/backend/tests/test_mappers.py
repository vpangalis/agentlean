"""Tests for the ten boundary mappers — procedure step 3.3's `pytest` Verify.

Architecture §9 · S-F10 (`define_input_mapper`) · S-F11 (`define_output_mapper`)
· S-F12 (the other four pairs) · S-C02 (the schema they populate).

Every Store interaction goes through a real `InMemoryStore` — LangGraph's own
`BaseStore` implementation — rather than a mock. A mock would let a mapper
"pass" while calling a method `BaseStore` does not have, which is the class of
failure §0.24 exists to prevent.
"""
from __future__ import annotations

import importlib

import pytest
from langchain_core.messages import HumanMessage
from langgraph.store.base import BaseStore
from langgraph.store.memory import InMemoryStore

from backend.core.state import SupervisorState
from backend.core.substate import (
    PHASE_STATE_AUTHOR_POPULATED_FIELDS,
    PHASE_STATE_ENGINE_MANAGED_FIELDS,
)
from backend.phases.mappers_common import (
    PHASE_ORDER,
    PriorGateDocumentMissing,
    advance,
    prior_phase,
)

CASE = "IMPR-2026-E9D"

CASE_RECORD = {
    "title": "Reduce customer complaint rate",
    "department": "Call centre",
    "belt_level": "Green",
    "leader": "V. Pangalis",
    "target_date": "2026-12-31",
}


def mappers(phase: str):
    m = importlib.import_module(f"backend.phases.{phase}.mappers")
    return getattr(m, f"{phase}_input_mapper"), getattr(m, f"{phase}_output_mapper")


def parent_state(phase: str, gate_passed: dict | None = None) -> SupervisorState:
    return {
        "messages": [HumanMessage(content="hello")],
        "history": [],
        "case_id": CASE,
        "phase_index": PHASE_ORDER.index(phase),
        "current_phase": phase,
        "gate_passed": gate_passed or {},
        "final_output": None,
    }


def seeded_store(phase: str) -> BaseStore:
    """A store carrying whatever `phase`'s input mapper needs to run."""
    store = InMemoryStore()
    store.put(("projects", CASE, "case"), "record", CASE_RECORD)
    prior = prior_phase(phase)
    if prior is not None:
        m = importlib.import_module(f"backend.phases.{phase}.mappers")
        doc = {f: f"{f} value from {prior}" for f in m.PHASE_CONTEXT_FIELDS}
        store.put(("projects", CASE, "artifacts"), prior, doc)
    return store


# ── the shape every pair holds ────────────────────────────────────────────

@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_every_phase_has_both_mappers(phase: str) -> None:
    """Ten mappers, five files (S-F10, S-F11, S-F12)."""
    inp, out = mappers(phase)
    assert callable(inp) and callable(out)


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_input_mapper_populates_every_author_populated_field(phase: str) -> None:
    """S-C02 B1: no author-populated field is left undeclared."""
    inp, _ = mappers(phase)
    state = inp(parent_state(phase), seeded_store(phase))
    assert set(state) == set(PHASE_STATE_AUTHOR_POPULATED_FIELDS)
    assert len(state) == 20


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_input_mapper_does_not_populate_remaining_steps(phase: str) -> None:
    """S-C02 B1: the ONE declared field the mapper must not write.

    LangGraph's execution loop supplies it. Writing it here would replace a
    live managed value with a stale integer — which is how the five-hop cap
    stopped firing in the first place (§0.16).
    """
    inp, _ = mappers(phase)
    state = inp(parent_state(phase), seeded_store(phase))
    for field in PHASE_STATE_ENGINE_MANAGED_FIELDS:
        assert field not in state


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_input_mapper_copies_identity_down(phase: str) -> None:
    """S-C02 B4/B8: copied from the parent, from no other source."""
    inp, _ = mappers(phase)
    state = inp(parent_state(phase), seeded_store(phase))
    assert state["case_id"] == CASE
    assert state["current_phase"] == phase


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_input_mapper_refuses_a_mismatched_parent_phase(phase: str) -> None:
    """The copy-down has one source; being invoked for the wrong phase is a bug
    at the call site, not something to silently absorb."""
    inp, _ = mappers(phase)
    wrong = parent_state(phase)
    wrong["current_phase"] = "improve" if phase != "improve" else "define"
    with pytest.raises(ValueError, match="copy-down"):
        inp(wrong, seeded_store(phase))


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_input_mapper_seeds_messages_and_starts_the_rest_empty(phase: str) -> None:
    inp, _ = mappers(phase)
    state = inp(parent_state(phase), seeded_store(phase))
    assert [m.content for m in state["messages"]] == ["hello"]
    assert state["history"] == []
    assert state["gate_attempts"] == 0
    assert state["turn_count"] == 0
    assert state["field_index"] == 0
    assert state["coaching_plan"] is None
    assert state["synthesis_output"] is None
    for f in ("draft", "artifacts", "belt_edits", "final"):
        assert state[f] == {}
    for f in ("step_log", "validator_feedback", "rejection_feedback",
              "citations", "uploads", "hop_results"):
        assert state[f] == []


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_input_mapper_does_not_alias_parent_messages(phase: str) -> None:
    """`messages` carries `operator.add`; handing the parent's own list down
    would let a subgraph append into parent state behind the boundary."""
    inp, _ = mappers(phase)
    parent = parent_state(phase)
    state = inp(parent, seeded_store(phase))
    assert state["messages"] is not parent["messages"]


# ── phase_context composition (§9) ────────────────────────────────────────

def test_define_context_comes_from_the_case_record() -> None:
    """S-F10: Define has no prior phase, so its source is the case record."""
    inp, _ = mappers("define")
    ctx = inp(parent_state("define"), seeded_store("define"))["phase_context"]
    assert "Reduce customer complaint rate" in ctx
    assert "Call centre" in ctx
    assert "V. Pangalis" in ctx


def test_define_context_survives_a_thin_case_record() -> None:
    """A missing framing field thins the prompt; it does not raise. Contrast
    with a missing gate document, which is an ordering fault."""
    inp, _ = mappers("define")
    store = InMemoryStore()
    store.put(("projects", CASE, "case"), "record", {"title": "T"})
    ctx = inp(parent_state("define"), store)["phase_context"]
    assert "T" in ctx


@pytest.mark.parametrize("phase", PHASE_ORDER[1:])
def test_later_phases_frame_from_the_prior_gate_document(phase: str) -> None:
    """S-F12 B1: composed from the Store, named fields only."""
    inp, _ = mappers(phase)
    m = importlib.import_module(f"backend.phases.{phase}.mappers")
    ctx = inp(parent_state(phase), seeded_store(phase))["phase_context"]
    assert prior_phase(phase) in ctx
    for field in m.PHASE_CONTEXT_FIELDS:
        assert field.replace("_", " ") in ctx


@pytest.mark.parametrize("phase", PHASE_ORDER[1:])
def test_uncaptured_field_is_named_not_omitted(phase: str) -> None:
    """A planner that cannot tell 'absent' from 'never asked' will not ask."""
    inp, _ = mappers(phase)
    m = importlib.import_module(f"backend.phases.{phase}.mappers")
    store = InMemoryStore()
    store.put(("projects", CASE, "case"), "record", CASE_RECORD)
    prior = prior_phase(phase)
    assert prior is not None
    store.put(("projects", CASE, "artifacts"), prior, {"unrelated": "x"})
    ctx = inp(parent_state(phase), store)["phase_context"]
    assert "not captured" in ctx
    for field in m.PHASE_CONTEXT_FIELDS:
        assert field.replace("_", " ") in ctx


@pytest.mark.parametrize("phase", PHASE_ORDER[1:])
def test_missing_prior_gate_document_raises(phase: str) -> None:
    """S-C06 failure modes: a `get` returning None where a prior gate document
    was expected is a REAL ORDERING FAULT, and callers must not default past
    it."""
    inp, _ = mappers(phase)
    store = InMemoryStore()
    store.put(("projects", CASE, "case"), "record", CASE_RECORD)
    with pytest.raises(PriorGateDocumentMissing):
        inp(parent_state(phase), store)


# ── the ratified G-27 composition ─────────────────────────────────────────

@pytest.mark.parametrize("phase", PHASE_ORDER[1:])
def test_context_carries_phase_metrics_and_acknowledged_gaps(phase: str) -> None:
    """G-27's ruling (2026-08-31): Tier-1 fields + `phase_metrics` +
    `acknowledged_gaps`.

    `acknowledged_gaps` travels so the next planner can tell "the Belt decided
    to proceed without this" from "nobody asked" — the distinction §9.7's two
    tiers exist to preserve.
    """
    m = importlib.import_module(f"backend.phases.{phase}.mappers")
    assert "phase_metrics" in m.PHASE_CONTEXT_FIELDS
    assert "acknowledged_gaps" in m.PHASE_CONTEXT_FIELDS


@pytest.mark.parametrize("phase", PHASE_ORDER[1:])
def test_context_excludes_tier_2_fields(phase: str) -> None:
    """G-27's ruling: Tier 2 is EXCLUDED. A Belt may consciously proceed
    without one, so carrying it invites the planner to read a permitted
    absence as a finding.

    Sampled against §9.7's named Tier-2 fields for the relevant prior phases.
    """
    tier_2 = {
        "baseline_sigma", "ruled_out_causes", "handover_documented",
        "financial_impact_verified", "implementation_plan", "lessons_learned",
        "transferability", "statistical_problem_statement",
        "process_owner_buyin", "explanatory_power", "project_signoff",
        "causal_hypothesis", "actual_close_date",
    }
    m = importlib.import_module(f"backend.phases.{phase}.mappers")
    assert not (set(m.PHASE_CONTEXT_FIELDS) & tier_2)


# ── the output mappers (§5 B2, S-F11) ─────────────────────────────────────

@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_output_mapper_writes_the_gate_document_to_the_store(phase: str) -> None:
    _, out = mappers(phase)
    store = seeded_store(phase)
    child = {"final": {"phase": phase, "approved": "yes"}}
    out(child, parent_state(phase), store)
    item = store.get(("projects", CASE, "artifacts"), phase)
    assert item is not None and item.value == {"phase": phase, "approved": "yes"}


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_output_mapper_returns_only_the_three_orchestration_values(phase: str) -> None:
    """S-F11 B3: artifacts and gate documents do not travel on parent state."""
    _, out = mappers(phase)
    update = out({"final": {}}, parent_state(phase), seeded_store(phase))
    assert set(update) == {"current_phase", "phase_index", "gate_passed"}


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_output_mapper_does_not_return_case_id(phase: str) -> None:
    """S-F11 B4 / S-C02 B9 — the copy-down invariant's greppable check."""
    _, out = mappers(phase)
    update = out({"final": {}}, parent_state(phase), seeded_store(phase))
    assert "case_id" not in update


def test_gate_passed_is_merged_not_replaced() -> None:
    """S-F11 B2: the re-approval cascade (§37) sets a phase back to False, so a
    wholesale replace would drop the other phases' entries."""
    _, out = mappers("analyse")
    parent = parent_state("analyse", gate_passed={"define": True, "measure": True})
    update = out({"final": {}}, parent, seeded_store("analyse"))
    assert update["gate_passed"] == {
        "define": True, "measure": True, "analyse": True,
    }


@pytest.mark.parametrize("phase,nxt,idx", [
    ("define", "measure", 1), ("measure", "analyse", 2),
    ("analyse", "improve", 3), ("improve", "control", 4),
])
def test_advance_moves_all_three_together(phase, nxt, idx) -> None:
    """§5 B2: written together, in a single update, by this one site."""
    update = advance(parent_state(phase), phase)
    assert update["current_phase"] == nxt
    assert update["phase_index"] == idx
    assert update["gate_passed"][phase] is True


def test_control_completes_rather_than_advancing() -> None:
    """Control is last; there is no sixth phase to point at."""
    update = advance(parent_state("control"), "control")
    assert update["current_phase"] == "complete"
    assert update["phase_index"] == 4
    assert update["gate_passed"]["control"] is True


# ── §0.24: the Store is used through BaseStore, not around it ─────────────

def test_mappers_take_a_basestore_and_nothing_else() -> None:
    """§9 B1: an input mapper's only dependency is `BaseStore`. Handing it a
    blob client would put untracked I/O in a translation function."""
    import inspect
    for phase in PHASE_ORDER:
        inp, out = mappers(phase)
        assert list(inspect.signature(inp).parameters) == ["parent", "store"]
        assert list(inspect.signature(out).parameters) == ["child", "parent", "store"]


def test_no_mapper_module_imports_a_blob_client() -> None:
    import inspect
    for phase in PHASE_ORDER:
        src = inspect.getsource(
            importlib.import_module(f"backend.phases.{phase}.mappers")
        )
        assert "blob" not in src.lower() or "BaseStore" in src
        assert "ImproveBlobClient" not in src
        assert "AzureBlobStore" not in src


def test_works_against_langgraphs_own_store_implementation() -> None:
    """The mappers are written against `BaseStore`, so any implementation
    serves — `InMemoryStore` here, `AzureBlobStore` (S-C06) in production."""
    inp, _ = mappers("define")
    assert isinstance(seeded_store("define"), BaseStore)
    assert inp(parent_state("define"), seeded_store("define"))["case_id"] == CASE
