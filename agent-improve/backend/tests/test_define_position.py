"""Step 6.57 — "Step n of 12" is computed, not counted by the model.

THE DEFECT, MEASURED
--------------------
Every coaching turn on `IMPR-2026-0E5` on 2026-09-24 — 12:37, 13:14, and the
G-96 live turn at 14:50 (trace 01a0d3e5-6246-7de3-b768-2ee767a5130c) — wrote
`progress = "Define · 13 of 13"`. Define's coached walk has TWELVE positions
(§39.1.2); 13 is the GATE's list, twelve fields plus `metric_definitions`,
which is captured inside position 5 (§39.1.9). The only count the model was
ever given was the gate block's "STILL MISSING FOR THE DEFINE GATE (n of 13)",
so it counted that — capability row 28 (§43.3) could not go green.

FOUNDER RULING 2026-09-24
-------------------------
Compute the Define position from DEFINE_FIELD_ORDER (12 positions;
metric_definitions sits inside position 5) and deliver it every turn, as v1.71
delivers the script. Keep the gate's "missing (… of 13)" list separate and
labelled as the gate list. Step 10.3's progress bar uses the same function.
"""
from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from backend.core.substate import CoachingResponse, PhaseState
from backend.middleware.state_injection import BeforeModelStateInjection
from backend.phases import nodes_common as _nc
from backend.phases.define.schema import (
    DEFINE_FIELD_ORDER,
    define_position,
    define_progress,
)

EVERY_12 = {f: "x" for f in DEFINE_FIELD_ORDER}
EVERY_13 = {**EVERY_12, "metric_definitions": [{"name": "m", "unit": "%", "meaning": "m"}]}


# ── the function ─────────────────────────────────────────────────────────────


def test_an_empty_case_is_at_step_1() -> None:
    assert define_position({}) == 1


def test_the_position_is_the_first_field_not_yet_captured() -> None:
    three = {f: "x" for f in DEFINE_FIELD_ORDER[:3]}
    assert define_position(three) == 4


def test_position_5_waits_for_metric_definitions() -> None:
    """§39.1.9: the registry is captured INSIDE position 5, so position 5 is
    not done until both halves are in — whatever comes after it."""
    assert define_position(EVERY_12) == 5
    assert define_position({**EVERY_12, "metric_definitions": []}) == 5


def test_a_complete_walk_rests_on_12_never_13() -> None:
    assert define_position(EVERY_13) == 12
    assert define_progress(EVERY_13)["of"] == 12


def test_a_blank_value_is_not_captured() -> None:
    assert define_position({DEFINE_FIELD_ORDER[0]: "   "}) == 1


def test_the_label_names_the_step_and_the_twelve() -> None:
    p = define_progress({f: "x" for f in DEFINE_FIELD_ORDER[:4]})
    assert p == {"position": 5, "of": 12, "field": "baseline_estimate",
                 "label": "Define · Step 5 of 12"}


def test_field_index_is_the_same_function() -> None:
    """One computation for the step the Belt is told and the index the planner
    walks — two would be free to disagree."""
    for artifacts in ({}, {DEFINE_FIELD_ORDER[0]: "x"}, EVERY_12, EVERY_13):
        assert _nc._advance_field_index("define", artifacts) == define_position(artifacts) - 1


# ── delivered every turn ─────────────────────────────────────────────────────


def _state(artifacts: dict) -> PhaseState:
    base: PhaseState = {
        "case_id": "IMPR-TEST-657", "current_phase": "define",
        "messages": [HumanMessage(content="where are we?")],
        "history": [], "phase_context": "framing", "coaching_plan": None,
        "field_index": 0, "draft": {}, "artifacts": artifacts, "step_log": [],
        "field_log": [], "belt_edits": {}, "turn_count": 0, "final": {},
        "gate_attempts": 0, "validator_feedback": [], "rejection_feedback": [],
        "citations": [], "uploads": [], "asks": [], "hop_results": [],
        "synthesis_output": None,
    }
    return base


def _block(artifacts: dict, phase: str = "define") -> str:
    mw = BeforeModelStateInjection(phase, _state(artifacts))
    mw.before_agent({}, None)
    return mw._block


def test_the_block_delivers_the_computed_step() -> None:
    block = _block({f: "x" for f in DEFINE_FIELD_ORDER[:4]})
    assert "Define · Step 5 of 12" in block
    assert "baseline_estimate" in block.split("Step 5 of 12")[1].splitlines()[0]


def test_the_step_comes_before_the_gate_list() -> None:
    """Models weight earlier content (§19.1 B2); the count the Belt is told
    must not be the second number the coach reads."""
    block = _block({})
    assert block.index("Step 1 of 12") < block.index("GATE LIST")


def test_the_gate_list_is_labelled_as_the_gate_list_and_keeps_its_13() -> None:
    block = _block({})
    header = next(line for line in block.splitlines() if "GATE LIST" in line)
    assert "of 13" in header, header
    assert "not the step" in header.lower(), header


def test_the_other_phases_are_given_no_define_step() -> None:
    assert "of 12" not in _block({}, phase="measure")


def test_the_progress_field_tells_the_model_to_copy_never_count() -> None:
    desc = CoachingResponse.model_fields["progress"].description or ""
    assert "copy" in desc.lower() and "never count" in desc.lower(), desc


# ── recorded every turn ──────────────────────────────────────────────────────


class _Agent:
    """The agent as `create_agent` returns it with `response_format`: the AI
    message, then the structured-response ToolMessage rendered the way the
    installed LangChain renders it (`factory.py`: f"Returning structured
    response: {structured_response}")."""

    def __init__(self, progress: str) -> None:
        self.progress = progress

    async def ainvoke(self, payload: dict, *_: Any, **__: Any) -> dict:
        reply = CoachingResponse(explanation="e", example="x", prompt="p",
                                 progress=self.progress, message="m")
        return {"messages": [*payload["messages"], AIMessage(content="m"),
                             ToolMessage(content=f"Returning structured response: {reply}",
                                         tool_call_id="call_1", name="CoachingResponse")],
                "structured_response": reply}


def _run(monkeypatch, progress: str, artifacts: dict) -> dict:
    monkeypatch.setattr(_nc, "create_agent", lambda **kw: _Agent(progress))
    return asyncio.run(_nc.executor("define", _state(artifacts)))


def _record(out: dict) -> dict:
    entries = [e for e in out["step_log"] if e.get("node") == "define_position"]
    assert len(entries) == 1, [e.get("node") for e in out["step_log"]]
    return entries[0]


def test_step_log_records_the_delivered_step_and_what_the_model_wrote(
        monkeypatch, stub_planner) -> None:
    e = _record(_run(monkeypatch, "Define · 13 of 13", {f: "x" for f in DEFINE_FIELD_ORDER[:2]}))
    assert (e["position"], e["of"], e["label"]) == (3, 12, "Define · Step 3 of 12")
    assert e["reply_progress"] == "Define · 13 of 13"
    assert e["reply_matches"] is False, "a model that counted for itself is on the record"


def test_a_reply_that_copies_the_step_is_recorded_as_matching(
        monkeypatch, stub_planner) -> None:
    e = _record(_run(monkeypatch, "Define · Step 1 of 12", {}))
    assert e["reply_matches"] is True


def test_the_reply_carries_the_computed_step_not_the_models_count(
        monkeypatch, stub_planner) -> None:
    """**The live finding, 2026-09-24 15:05 (trace 01a0d3f3-6f67-7100-b04d-
    214e7fe1f720):** the step was delivered at the top of the model's input and
    the model still wrote "13 of 13" — its own earlier replies put "of 13" in
    that input 55 times. So the reply the turn RECORDS carries the computed
    step: the structured-response message the next turn reads, and nothing of
    the model's count in it."""
    out = _run(monkeypatch, "Define · 13 of 13", {f: "x" for f in DEFINE_FIELD_ORDER[:2]})
    stored = [m for m in out["messages"] if isinstance(m, ToolMessage)
              and str(m.content).startswith("Returning structured response:")]
    assert len(stored) == 1
    assert "progress='Define · Step 3 of 12'" in str(stored[0].content)
    assert "13 of 13" not in str(stored[0].content)
    assert stored[0].tool_call_id == "call_1", "the tool-call pairing survives the rewrite"
    assert _record(out)["progress_written"] == "Define · Step 3 of 12"
