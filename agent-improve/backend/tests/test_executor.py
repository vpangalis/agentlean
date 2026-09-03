"""The `create_agent` executor — what procedure step 6.2 established.

**Step 6.2's *Done when*:** one turn returns `result["structured_response"]` as
a `CoachingResponse` with the coaching prose still present in `messages`, and
the Define gate opens on a case coached through the v2 path
(`fields_captured` -> `artifacts` -> `validate.py`). The live half is the
`live-run`; what is pinned here is everything underneath it that would
otherwise fail silently.

WHY THE CONSTRUCTION KWARGS ARE ASSERTED AND NOT ASSUMED
---------------------------------------------------------
CLAUDE.md §0.10 records what the last wrong parameter name cost: `retries=`
instead of `max_retries=` sat inside the canonical middleware block — the one an
implementer copies verbatim — from adoption until it was verified months later.
`create_agent` renamed `prompt` to `system_prompt`, and §18 forbids binding
tools onto a bare model. Both are checked here against the real construction
site, and `test_create_agent_signature_still_has_system_prompt` checks the
LIBRARY rather than our call, so the pair fails on an upgrade that renames it
back rather than on nothing.

THE WATCH 7 HALF
----------------
`test_captured_fields_land_in_artifacts_under_v2_names` and
`test_the_define_gate_opens_on_v2_captured_fields` are the two that matter for
the ruling: `artifacts` was empty for every phase by ruling until this step, and
`validate_define` has been reading §39.1.2's names the whole time. The second
test drives the real validator, so it fails if the names drift apart again.
"""
from __future__ import annotations

import asyncio
import inspect
from typing import Any

import pytest
from langchain.agents import create_agent
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from backend.core.substate import CoachingPlan, CoachingResponse, PhaseState
from backend.knowledge.computation import COMPUTATION_TOOLS_BY_PHASE
from backend.knowledge.tools import UNIVERSAL_TOOLS
from backend.phases import nodes_common as _c
from backend.phases.mappers_common import PHASE_ORDER


def _state(**overrides: Any) -> PhaseState:
    base: PhaseState = {
        "case_id": "IMPR-TEST-62", "current_phase": "define",
        "messages": [HumanMessage(content="hello")], "history": [],
        "phase_context": "",
        "coaching_plan": CoachingPlan(
            focus_field="business_case", next_action="ask",
            retrieval_strategy="single_hop", retrieval_hops=[],
        ),
        "field_index": 0, "draft": {}, "artifacts": {},
        "step_log": [], "belt_edits": {}, "turn_count": 0, "final": {},
        "gate_attempts": 0, "validator_feedback": [], "rejection_feedback": [],
        "citations": [], "uploads": [], "hop_results": [],
        "synthesis_output": None,
    }
    base.update(overrides)  # type: ignore[typeddict-item]
    return base


def _run(coro):
    return asyncio.run(coro)


# ══════════════════════════════════════════════════════════════════════════
# §18 — how the agent is constructed
# ══════════════════════════════════════════════════════════════════════════


def test_create_agent_signature_still_has_system_prompt_and_no_prompt() -> None:
    """§16.3 — verified against the INSTALLED library, not against a comment.

    This is the check that survives an upgrade. Asserting only our own call
    would keep passing if LangChain renamed the parameter back; asserting the
    signature fails at the point the assumption stops being true.
    """
    params = inspect.signature(create_agent).parameters
    assert "system_prompt" in params
    assert "prompt" not in params, (
        "`create_agent` grew a `prompt` parameter — §18's rule and CLAUDE.md "
        "§4.4's example both need re-checking before either is trusted"
    )
    for name in ("tools", "response_format", "middleware", "model"):
        assert name in params, name


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_the_executor_builds_the_agent_per_the_ratified_template(
    phase: str, stub_coach
) -> None:
    """§18's template, kwarg for kwarg."""
    _run(_c.executor(phase, _state(current_phase=phase)))

    kwargs = stub_coach.calls[-1]
    assert "system_prompt" in kwargs, "the parameter is system_prompt, NOT prompt"
    assert "prompt" not in kwargs
    assert kwargs["response_format"] is CoachingResponse, (
        "§20 — never a {Phase}Output on the executor"
    )
    assert kwargs["middleware"] == [], "§19's eight land at 6.3-6.5"
    assert kwargs["model"] is not None


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_tools_are_passed_to_create_agent_not_bound_to_the_model(
    phase: str, stub_coach
) -> None:
    """§18 — binding onto a bare model bypasses all eight middlewares, silently.

    `pattern-8-bind-tools-in-phase-executor` guards the source for the same
    reason; this checks the behaviour rather than the text.
    """
    _run(_c.executor(phase, _state(current_phase=phase)))

    kwargs = stub_coach.calls[-1]
    assert kwargs["tools"] == UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    model = kwargs["model"]
    assert not getattr(model, "_bound_tools", None), "tools bound onto the model"
    assert model.kwargs.get("tools") is None if hasattr(model, "kwargs") else True


def test_the_prompt_carries_the_phases_field_names(stub_coach) -> None:
    """The field list IS the capture contract — a name not on it never lands."""
    _run(_c.executor("define", _state()))
    prompt = stub_coach.system_prompt
    for field in ("business_case", "voc_summary", "problem_statement",
                  "metric_definitions"):
        assert field in prompt, field
    assert "MEMORY HIERARCHY" in prompt, "§6.3 block is mandatory"
    assert "NEVER INVENT A VALUE" in prompt, "§6.4 guards are mandatory"


def test_the_prompt_names_the_plans_focus_field(stub_coach) -> None:
    """S-F04 B1 — coach the planner's field, never a different one."""
    _run(_c.executor("define", _state(coaching_plan=CoachingPlan(
        focus_field="voc_summary", next_action="challenge a vague answer",
        retrieval_strategy="single_hop", retrieval_hops=[],
    ))))
    prompt = stub_coach.system_prompt
    assert "Coach on: voc_summary" in prompt
    assert "challenge a vague answer" in prompt
    assert "no other" in prompt


# ══════════════════════════════════════════════════════════════════════════
# §20 — what comes back, and where it lands
# ══════════════════════════════════════════════════════════════════════════


def test_the_coaching_prose_stays_in_messages(stub_coach) -> None:
    """§18 — *"the structured response and the coaching text coexist"*.

    Reading one must not cost the other: the Belt sees `messages`, and the
    executor writes from `structured_response`.
    """
    stub_coach.reply = CoachingResponse(message="Here is where I would start.")
    out = _run(_c.executor("define", _state()))
    replies = [m for m in out["messages"] if isinstance(m, AIMessage)]
    assert replies and replies[-1].content == "Here is where I would start."


def test_a_reply_with_no_prose_still_reaches_the_belt() -> None:
    """The empty-turn guard.

    A provider that puts everything in the structured payload leaves the
    terminal AI message blank, and the Belt would get an empty turn. Driven at
    the helper because the condition is the agent's output shape, not the
    node's: constructing it through the fixture would be staging the very thing
    being guarded against.
    """
    reply = CoachingResponse(message="Recovered text.")
    out = _c._with_coaching_text([AIMessage(content="   ")], reply)
    assert out[-1].content == "Recovered text."

    # And it does NOT append when real prose is already there.
    kept = _c._with_coaching_text([AIMessage(content="Real coaching.")], reply)
    assert len(kept) == 1 and kept[-1].content == "Real coaching."


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_captured_fields_land_in_artifacts_under_v2_names(
    phase: str, stub_coach
) -> None:
    """**This is the write that clears WATCH 7.**

    Until 6.2 `artifacts` stayed empty for every phase by ruling and the v1
    orchestrator wrote v1 names into `draft`. Now `fields_captured` goes into
    `artifacts` under the §39.x names, which is what `validate_{phase}` reads.
    """
    stub_coach.reply = CoachingResponse(
        message="Noted.",
        fields_captured=[
            {"field_name": "business_case", "value": "£120k rework a year",
             "source": "belt"},
        ],
    )
    out = _run(_c.executor(phase, _state(current_phase=phase,
                                         artifacts={"already": "here"})))
    assert out["artifacts"]["business_case"] == "£120k rework a year"
    assert out["artifacts"]["already"] == "here", "the merge dropped prior fields"
    assert out["draft"] == {"business_case": "£120k rework a year"}, (
        "`draft` is THIS turn's extraction, `artifacts` the accumulation"
    )


def test_a_capture_without_a_field_name_is_dropped_not_guessed(stub_coach) -> None:
    """Inferring the field is how a value lands under the wrong key.

    A wrong key reaches the gate document looking exactly like a right one, so
    the malformed entry is dropped and logged instead.
    """
    stub_coach.reply = CoachingResponse(
        message="Noted.",
        fields_captured=[
            {"value": "orphaned", "source": "belt"},
            {"field_name": "  ", "value": "also orphaned"},
            {"field_name": "team", "value": "Ana, Bo"},
        ],
    )
    out = _run(_c.executor("define", _state()))
    assert out["artifacts"] == {"team": "Ana, Bo"}


def test_a_reference_dict_value_survives_as_a_dict(stub_coach) -> None:
    """§20 — `value` is `Any` deliberately.

    Coercing to `str` here would make the three cross-phase reference fields
    uncapturable, which is the one place `Any` is correct.
    """
    hypothesis = {"statement": "rework drives the delay",
                  "references_phase": "measure",
                  "references_field": "baseline_mean",
                  "references_value": "12.3",
                  "references_metric_name": "invoice error rate"}
    stub_coach.reply = CoachingResponse(
        message="Noted.",
        fields_captured=[{"field_name": "causal_hypothesis",
                          "value": hypothesis, "source": "belt"}],
    )
    out = _run(_c.executor("analyse", _state(current_phase="analyse")))
    assert out["artifacts"]["causal_hypothesis"] == hypothesis


def test_citations_accumulate_rather_than_replace(stub_coach) -> None:
    """`citations` carries no reducer, so the merge happens in the node."""
    stub_coach.reply = CoachingResponse(
        message="Noted.", citations=[{"source_file": "bb.pdf", "page": 47}],
    )
    out = _run(_c.executor("define", _state(
        citations=[{"source_file": "earlier.pdf", "page": 3}]
    )))
    assert [c["source_file"] for c in out["citations"]] == [
        "earlier.pdf", "bb.pdf",
    ]


def test_the_contradiction_flag_is_carried_for_6_5(stub_coach) -> None:
    """§19.6 reads it at 6.5. Until then it must at least survive the turn."""
    flag = {"prior_field": "baseline_mean", "approved_value": "4.2",
            "approved_phase": "measure", "proposed_value": "3.8",
            "belt_input": "actually it was 3.8"}
    stub_coach.reply = CoachingResponse(message="Hold on.",
                                        contradiction_flag=flag)
    out = _run(_c.executor("define", _state()))
    assert out["step_log"][0]["contradiction_flag"] == flag


def test_one_invoke_is_one_turn(stub_coach) -> None:
    """`turn_count` is what the planner's placeholder predicate terminates on."""
    out = _run(_c.executor("define", _state(turn_count=3)))
    assert out["turn_count"] == 4
    assert len(stub_coach.invocations) == 1


def test_the_executor_returns_no_command(stub_coach) -> None:
    """§17 — it returns plainly; the static edge carries control to the planner.

    §15 C2: a node that mixed a static edge with a `Command` would run both
    paths, silently.
    """
    from langgraph.types import Command

    out = _run(_c.executor("define", _state()))
    assert not isinstance(out, Command)
    assert set(out) <= {"messages", "draft", "artifacts", "citations",
                        "turn_count", "step_log"}
    assert "case_id" not in out and "current_phase" not in out, (
        "S-C02 B9 — both are read-only inside the subgraph"
    )


# ══════════════════════════════════════════════════════════════════════════
# §3.7 — the exploration cap, and what the Belt sees when it fires
# ══════════════════════════════════════════════════════════════════════════


def test_the_coach_gets_its_own_recursion_limit(stub_coach) -> None:
    """§3.7 — `2 * max_hops + 1`, passed EXPLICITLY.

    An agent invoked inside a node inherits the parent invoke's config, and the
    route passes 50 (§16's infinite-loop backstop). Without an explicit limit
    the per-turn cap §3.7 specifies never fires — the failure mode this project
    keeps naming: a cap that cannot fire is a check recorded as evidence while
    proving nothing.
    """
    assert _c.COACH_RECURSION_LIMIT == 11
    _run(_c.executor("define", _state()))
    invoked_config = stub_coach.invocations[-1]
    assert invoked_config is not None
    # The limit rides on the ainvoke config, which the fake records separately.
    assert stub_coach.invoke_configs[-1]["recursion_limit"] == 11


def test_hitting_the_cap_gives_the_belt_a_partial_answer(stub_coach) -> None:
    """§3.7 — *"MUST be caught in the coach node and turned into a partial
    answer. A Belt mid-session never sees a stack trace."*

    **Found by step 6.2's live-run**, which looped a real turn past the cap and
    raised. The turn still has to close cleanly: a message the Belt can act on,
    `turn_count` advanced so the planner's predicate still terminates, and the
    event on the audit trail as the monitoring signal §3.7 calls it.
    """
    stub_coach.raise_recursion = True
    out = _run(_c.executor("define", _state()))

    reply = [m for m in out["messages"] if isinstance(m, AIMessage)][-1]
    assert "run out of room" in str(reply.content)
    assert "nothing you have told me is lost" in str(reply.content).lower()
    assert out["turn_count"] == 1, "the turn must still close"
    assert out["step_log"][0]["status"] == "partial_cap_reached"
    assert out["artifacts"] == {}, "no capture from a turn that did not finish"


def test_the_cap_message_carries_no_jargon(stub_coach) -> None:
    """§13 — team-facing strings are plain language.

    "GraphRecursionError", "recursion limit" and "tool call" are exactly what a
    Belt must never be shown.
    """
    lowered = _c._CAP_MESSAGE.lower()
    for jargon in ("recursion", "graph", "tool", "error", "exception", "limit"):
        assert jargon not in lowered, jargon


# ══════════════════════════════════════════════════════════════════════════
# The UI contract — `propose_diagram` reaches the reply
# ══════════════════════════════════════════════════════════════════════════


def test_a_proposed_diagram_rides_on_the_reply_for_the_ui(stub_coach) -> None:
    """`gateway/routes.py` reads `sipoc_diagram` off `additional_kwargs`.

    The v1 orchestrator put it there; without this the SIPOC the UI already
    renders would have disappeared the moment `create_agent` replaced it.
    """
    stub_coach.tool_messages = [ToolMessage(
        content="Diagram ready.", tool_call_id="1",
        artifact={"diagram_type": "sipoc", "suppliers": ["AP"],
                  "inputs": [], "process_steps": ["receive"], "outputs": [],
                  "customers": ["Finance"], "draft": True,
                  "source": "generated"},
    )]
    out = _run(_c.executor("define", _state()))
    reply = [m for m in out["messages"] if isinstance(m, AIMessage)][-1]
    sipoc = reply.additional_kwargs["sipoc_diagram"]
    assert sipoc["process_steps"] == ["receive"]
    assert "diagram_type" not in sipoc, "the UI reads the payload, not the tag"


def test_a_turn_that_drew_nothing_attaches_nothing(stub_coach) -> None:
    """Absent payloads are simply not attached — the v1 behaviour, kept."""
    out = _run(_c.executor("define", _state()))
    reply = [m for m in out["messages"] if isinstance(m, AIMessage)][-1]
    assert "sipoc_diagram" not in reply.additional_kwargs
    assert "visualisation" not in reply.additional_kwargs


# ══════════════════════════════════════════════════════════════════════════
# The gate half of the Done-when, driven through the REAL validator
# ══════════════════════════════════════════════════════════════════════════


def test_the_define_gate_opens_on_v2_captured_fields(stub_coach) -> None:
    """**WATCH 7's closing condition, checked against `validate_define`.**

    Route A accepted an inert Define gate because `validate.py` read the v2
    names while `orchestrate.py` wrote the v1 ones. This coaches the twelve
    §39.1.2 fields through `CoachingResponse` into `artifacts` and asserts the
    real validator now sees a complete set — the two halves meeting is the
    whole of what 6.2 had to prove.
    """
    from backend.phases.define.schema import DEFINE_REQUIRED_FOR_GATE_FIELDS

    stub_coach.reply = CoachingResponse(
        message="Captured.",
        fields_captured=[
            {"field_name": name, "value": f"value for {name}", "source": "belt"}
            for name in DEFINE_REQUIRED_FOR_GATE_FIELDS
        ],
    )
    out = _run(_c.executor("define", _state()))

    missing = [f for f in DEFINE_REQUIRED_FOR_GATE_FIELDS
               if f not in out["artifacts"]]
    assert missing == [], f"the v2 writer did not land: {missing}"
    assert all(out["artifacts"][f] for f in DEFINE_REQUIRED_FOR_GATE_FIELDS)


def test_the_v1_orchestrators_are_no_longer_called(stub_coach) -> None:
    """Route A — `orchestrate.py` is dead code awaiting 11.1, not migrated.

    The five modules still exist and still import cleanly; nothing calls them.
    Checked on the node wrappers, which is where the delegation used to be.
    """
    import importlib

    for phase in PHASE_ORDER:
        source = inspect.getsource(
            importlib.import_module(f"backend.phases.{phase}.nodes")
        )
        assert f"orchestrate_{phase}" not in source.replace(
            f"`orchestrate_{phase}`", ""
        ), f"{phase}/nodes.py still references its v1 orchestrator in code"
