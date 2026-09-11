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
from backend.knowledge.tools import RAG_LOOKUP_TOOLS, UNIVERSAL_TOOLS
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
        "citations": [], "uploads": [], "asks": [], "hop_results": [],
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
    declared = [type(m).__name__ for m in kwargs["middleware"]]
    assert declared == [
        # 1-5 fire before_agent / before_model / wrap_*, where declaration
        # order IS execution order.
        "BeforeModelStateInjection",         # 1
        "DMAICSkillsMiddleware",             # 2
        "SummarizationMiddleware",           # 3
        "ModelRetryMiddleware",              # 4
        "ToolRetryMiddleware",               # 5
        # 6-8 fire after_agent, which executes in REVERSE — so they are
        # declared backwards to EXECUTE as 6, 7, 8. See
        # `test_all_eight_positions_execute_in_the_ratified_order`.
        "DMAICGraderMiddleware",             # executes 8th (last)
        "CoherenceMiddleware",               # executes 7th
        "ContradictionDetectionMiddleware",  # executes 6th (first)
    ], "§19's eight — 1-5 in declaration order, 6-8 reversed for after_agent"
    assert kwargs["model"] is not None


@pytest.mark.parametrize("phase", PHASE_ORDER)
def test_tools_are_passed_to_create_agent_not_bound_to_the_model(
    phase: str, stub_coach
) -> None:
    """§18 — binding onto a bare model bypasses all eight middlewares, silently.

    `pattern-8-bind-tools-in-phase-executor` guards the source for the same
    reason; this checks the behaviour rather than the text.

    **Identity holds for every tool but the retrieval three** (6.7). Those are
    passed as per-turn copies carrying §3.7's hop budget — `model_copy` with only
    the coroutine swapped, so `name`, `description`, `args_schema` and
    `response_format` are the originals' and §5.4's load-bearing docstrings reach
    the model unchanged. The set and its order are unchanged, which is what
    this test is actually about.
    """
    _run(_c.executor(phase, _state(current_phase=phase)))

    kwargs = stub_coach.calls[-1]
    expected = UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    passed = kwargs["tools"]
    assert [t.name for t in passed] == [t.name for t in expected]
    for got, want in zip(passed, expected):
        if want in RAG_LOOKUP_TOOLS:
            assert got is not want, "the retrieval three are budgeted copies"
            assert got.description == want.description
            assert got.args_schema is want.args_schema
            assert got.response_format == want.response_format
        else:
            assert got is want, f"{want.name} must be passed as-is"
    model = kwargs["model"]
    assert not getattr(model, "_bound_tools", None), "tools bound onto the model"
    assert model.kwargs.get("tools") is None if hasattr(model, "kwargs") else True


def test_the_static_prompt_keeps_the_two_mandatory_blocks(stub_coach) -> None:
    """§6.3 and §6.4 — both mandatory on every coach prompt.

    The system prompt is STATIC per phase as of 6.3: the per-turn facts moved
    into `BeforeModelStateInjection`. These two blocks did not move — they are
    the coach's standing instructions, not this turn's state.
    """
    _run(_c.executor("define", _state()))
    prompt = stub_coach.system_prompt
    assert "MEMORY HIERARCHY" in prompt, "§6.3 block is mandatory"
    assert "NEVER INVENT A VALUE" in prompt, "§6.4 guards are mandatory"


def test_the_per_turn_facts_are_no_longer_in_the_system_prompt(stub_coach) -> None:
    """**Step 6.3 removed 6.2's hand-composition, and that is the point.**

    §19.1 is the ratified home for project-state injection. Leaving 6.2's
    hand-composed copy in place alongside the middleware would inject the same
    facts twice — and the duplicate would be the one that drifted, since only
    the middleware derives its missing-field list from the shared gate
    computation.
    """
    _run(_c.executor("define", _state(artifacts={"business_case": "b"})))
    prompt = stub_coach.system_prompt
    assert "FIELD LIST for" not in prompt
    assert "STILL MISSING" not in prompt
    assert "CAPTURED THIS PHASE" not in prompt
    assert "THIS PROJECT" not in prompt


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
                        "uploads",
                        "turn_count", "step_log"}
    assert "case_id" not in out and "current_phase" not in out, (
        "S-C02 B9 — both are read-only inside the subgraph"
    )


# ══════════════════════════════════════════════════════════════════════════
# §3.7 / §26 — the two guards, and what the Belt sees when each one fires
#
# WATCH 26. These are two DIFFERENT guards in two DIFFERENT units, and the
# build had neither: `recursion_limit=11` was standing in for both and could
# do the job of neither. The tests are grouped so that is legible.
# ══════════════════════════════════════════════════════════════════════════


def test_recursion_limit_is_the_backstop_not_the_hop_cap(stub_coach) -> None:
    """§16 — set high, and passed EXPLICITLY.

    It was 11 from 6.2 to 6.6 and that was the defect: §16 rejects
    `recursion_limit` as the hop cap outright, and `2 * max_hops + 1 = 11` is
    short by one besides — measured, five hops consume all eleven steps and
    raise before the model can compose, so a well-behaved five-hop turn could
    only ever end in the cap message.

    **Explicit rather than inherited** because an agent invoked inside a node
    inherits the parent's LIMIT with a FRESH counter — right when the route
    sets 50, silently wrong when a test or a script invokes this node directly.
    """
    assert _c.COACH_RECURSION_BACKSTOP == 50
    assert not hasattr(_c, "COACH_RECURSION_LIMIT"), (
        "the 11-step cap is gone, not renamed"
    )
    _run(_c.executor("define", _state()))
    assert stub_coach.invoke_configs[-1]["recursion_limit"] == 50


def test_the_coach_backstop_matches_the_graph_backstop() -> None:
    """One backstop, two names — §16 has a single number in it.

    `nodes_common` cannot import `core.graph` (that module imports the phase
    subgraphs, which import this one), so the constant is duplicated by
    necessity. This test is what stops the copies drifting.
    """
    from backend.core.graph import RECURSION_LIMIT

    assert _c.COACH_RECURSION_BACKSTOP == RECURSION_LIMIT


def test_the_hop_cap_is_five_retrieval_calls(stub_coach) -> None:
    """§3.7 — the cap is a COUNT OF `rag_lookup_*` CALLS, enforced in the tool.

    Neither step counter can do this: `recursion_limit` is rejected by §16, and
    `remaining_steps` moves by 1 per executor turn however many hops the turn
    made, because the whole loop runs inside one node.
    """
    assert _c.COACH_HOP_BUDGET == 5
    _run(_c.executor("define", _state()))

    names = stub_coach.tool_names
    for name in ("rag_lookup_methodology", "rag_lookup_evidence",
                 "rag_lookup_case_history"):
        assert name in names, f"{name} must stay bound on an ordinary turn"


def test_the_sixth_lookup_answers_instead_of_searching(stub_coach) -> None:
    """§3.7 — past the budget the tool ANSWERS; it does not vanish or raise.

    That is the graceful half. A tool that disappeared mid-loop, or one that
    raised, would end the turn with nothing to say; a tool that replies "you
    are out of lookups, answer from what you have" is a result the coach can
    read and act on, exactly like a search that found nothing.
    """
    _run(_c.executor("define", _state()))
    lookup = next(t for t in stub_coach.calls[-1]["tools"]
                  if t.name == "rag_lookup_methodology")

    results = [_run(lookup.coroutine(query="q", phase="define"))
               for _ in range(_c.COACH_HOP_BUDGET + 1)]
    contents = [content for content, _artifact in results]

    assert all("budget for this turn is spent" not in c
               for c in contents[:-1]), "the first five lookups must search"
    assert "budget for this turn is spent" in contents[-1]
    assert "Do not search again" in contents[-1]


def test_the_hop_budget_is_per_turn_not_per_process(stub_coach) -> None:
    """The count is a fresh list per turn, so it cannot leak.

    A module-level counter would spend one Belt's budget on another Belt's
    turn — and with one event loop serving concurrent cases, that is not a
    theoretical failure.
    """
    _run(_c.executor("define", _state()))
    first = next(t for t in stub_coach.calls[-1]["tools"]
                 if t.name == "rag_lookup_methodology")
    for _ in range(_c.COACH_HOP_BUDGET):
        _run(first.coroutine(query="q", phase="define"))

    _run(_c.executor("define", _state()))          # a second turn
    second = next(t for t in stub_coach.calls[-1]["tools"]
                  if t.name == "rag_lookup_methodology")
    content, _artifact = _run(
        second.coroutine(query="q", phase="define"))
    assert "budget for this turn is spent" not in content


def test_low_remaining_steps_coaches_without_retrieval(stub_coach) -> None:
    """§26 / S-F09 B1 — *"rather than beginning a hop chain it cannot finish"*.

    **This is a coached turn, not a capped one.** The three `rag_lookup_*`
    tools are not bound; the other four of the universal seven are, because the
    off-ramp is about not STARTING new retrieval rather than about coaching
    with one hand tied.
    """
    out = _run(_c.executor("define", _state(remaining_steps=1)))

    names = stub_coach.tool_names
    assert not [n for n in names if n.startswith("rag_lookup_")]
    assert "propose_template" in names and "propose_diagram" in names, (
        "the rest of the universal set stays — the off-ramp is about not "
        "STARTING new retrieval, not about coaching with one hand tied"
    )
    assert any(t.name not in [u.name for u in UNIVERSAL_TOOLS] for t
               in stub_coach.calls[-1]["tools"]), "phase tools stay too"

    assert out["step_log"][0]["status"] == "coached_no_retrieval"
    assert out["turn_count"] == 1
    reply = [m for m in out["messages"] if isinstance(m, AIMessage)][-1]
    assert "run out of room" not in str(reply.content), (
        "the off-ramp coaches; it does not show the Belt a cap message"
    )


def test_an_ordinary_turn_keeps_its_retrieval_tools(stub_coach) -> None:
    """The off-ramp must not fire on a healthy turn.

    `remaining_steps` counts down from ~50, so an ordinary turn sits nowhere
    near the floor. A guard that fired anyway would silently switch retrieval
    off for the whole product.
    """
    out = _run(_c.executor("define", _state(remaining_steps=48)))
    assert "rag_lookup_methodology" in stub_coach.tool_names
    assert out["step_log"][0]["status"] == "coached"


def test_an_absent_remaining_steps_does_not_trip_the_off_ramp(
        stub_coach) -> None:
    """The §0.16 failure, in the other direction.

    Undeclared, `state.get("remaining_steps", 10)` returned 10 forever and the
    guard could never fire. A default here would make it fire on EVERY turn
    instead — retrieval off for everyone — which is worse, because it looks
    like the product working.
    """
    state = _state()
    state.pop("remaining_steps", None)
    out = _run(_c.executor("define", state))
    assert "rag_lookup_methodology" in stub_coach.tool_names
    assert out["step_log"][0]["status"] == "coached"


def test_both_guards_are_written_to_the_step_log(stub_coach) -> None:
    """§26 — *"hitting the cap is a monitoring signal"*.

    A signal nobody can read is not one. WATCH 26 went four steps undiagnosed
    partly because the hop count was never written down: the see-saw could only
    be seen by re-running turns and watching them fall over.
    """
    out = _run(_c.executor("define", _state(remaining_steps=40)))
    entry = out["step_log"][0]
    assert entry["hop_budget"] == _c.COACH_HOP_BUDGET
    assert entry["hops_spent"] == 0
    assert entry["remaining_steps"] == 40


def test_hitting_the_backstop_gives_the_belt_a_partial_answer(
        stub_coach) -> None:
    """§3.7 — *"MUST be caught in the coach node and turned into a partial
    answer. A Belt mid-session never sees a stack trace."*

    **Belt-and-braces since 6.7, not the primary guard** (§26). Reaching here
    now means the coach burned 50 graph steps without stopping — a genuine
    runaway loop, which is what §16 says the backstop is for. The turn still
    has to close cleanly: a message the Belt can act on, `turn_count` advanced
    so the planner's predicate still terminates, and the event on the trail.
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


# ══════════════════════════════════════════════════════════════════════════
# G-49 / procedure step 6.18 — THE DIAGNOSIS
#
# **These three tests are the instrument, not the fix.** 6.18 is a diagnosis
# step: it ends when the cause is named at one of four layers, and each test
# below rules one layer in or out. The `live-run` came FIRST, deliberately — a
# test written before the cause was known would have pinned the 45s node
# timeout, and a pinned timeout passes the day the timeout is raised.
#
# Reproduction, re-run 2026-09-11 on `09960df`: `POST /ask` on
# `IMPR-2026-ED8` — *"what does our to-be process look like"* — planner routes
# to the unread upload, executor issues 18 evidence searches across 3
# multi-query calls, fetches no `uploads/` blob at all, and the node timeout
# ends the turn at 45.141s (2026-09-10 recorded 45.157s on `1714d75`).
# ══════════════════════════════════════════════════════════════════════════


def _model_channels(stub_coach) -> dict[str, str]:
    """Every channel the executor can reach the model through, this turn.

    **Deliberately channel-agnostic.** The fix may deliver the plan through the
    injected block, through a message, or through the system prompt; a test
    that named one of those would fail a valid fix made through another. What
    cannot change is that the model reads only what arrives in these three.
    """
    payload = stub_coach.invocations[-1]
    return {
        "system_prompt": stub_coach.system_prompt,
        "injected_block": stub_coach.injected_block,
        "messages": "\n".join(
            str(getattr(m, "content", m)) for m in payload.get("messages") or []
        ),
    }


def _unread_upload() -> dict:
    """One upload in the shape the live case carries it (`IMPR-2026-ED8`)."""
    return {
        "filename": "complaints.csv",
        "blob_path": "uploads/IMPR-TEST-618/complaints.csv",
        "role": "other evidence",
        "shape_match": "unsolicited",
        "consumed_at": None,
        "summary": "five days of complaint counts and reasons",
    }


@pytest.mark.xfail(strict=True, reason=(
    "G-49, layer 2 — the executor invokes the agent with {'messages': prior} "
    "and the plan reaches no channel the model reads. STRICT: the day the "
    "transport lands this test PASSES, the suite goes RED on the unexpected "
    "pass, and removing this marker is step 6.21's first Done-when clause. "
    "A pinned defect that quietly starts passing is not pinned."
))
def test_the_planners_instruction_reaches_the_model(stub_coach) -> None:
    """**G-49, LAYER 2 — the plan does not reach the executor's context.**

    THIS TEST FAILS ON TODAY'S BUILD, AND THAT IS ITS PURPOSE — it is marked
    `xfail(strict=True)` so the suite stays green on a defect that is
    diagnosed and deliberately unfixed, and goes red the moment it is fixed
    without the marker being removed.

    §17 gives the planner the routing decision. The planner makes it — it
    rewrites `CoachingPlan.next_action` into an imperative naming a tool and a
    blob path, and logs that it did. `executor()` then reads `coaching_plan`
    for the logger and the `step_log` and **invokes the agent with
    `{"messages": prior}`**, so the decision is recorded and never delivered.

    The sentinel is deliberately NOT the bare tool name: the upload manifest
    (§19.1, step 6.12) already says *"call load_evidence_series with the
    blob_path above"*, so asserting on `load_evidence_series` alone would pass
    on the manifest and prove nothing. What only the plan carries is the
    planner's imperative — *"before asking for anything further"*.
    """
    directive = (
        "Call load_evidence_series on uploads/IMPR-TEST-618/complaints.csv "
        "before asking for anything further, then interpret what it shows."
    )
    state = _state(
        uploads=[_unread_upload()],
        coaching_plan=CoachingPlan(
            focus_field="business_case",
            next_action=directive,
            retrieval_strategy="single_hop",
            retrieval_hops=[],
        ),
    )

    _run(_c.executor("define", state))

    channels = _model_channels(stub_coach)
    carried = [name for name, text in channels.items()
               if "before asking for anything further" in text]
    assert carried, (
        "THE PLANNER'S ROUTING INSTRUCTION REACHES NO CHANNEL THE MODEL "
        "READS (G-49, layer 2). Searched "
        + ", ".join(f"{n} ({len(t)} chars)" for n, t in channels.items())
        + ". The plan is in PhaseState and in the step_log; §17's routing "
          "decision is therefore advisory at runtime, and what the coach does "
          "with the upload stays entirely its own discretion."
    )


def test_load_evidence_series_is_bound_on_every_phase(stub_coach) -> None:
    """**LAYER 1 RULED OUT — the tool IS bound at call time.**

    `load_evidence_series` joined `UNIVERSAL_TOOLS` at step 6.12, so it is
    bound in all five phases, and `_executor_tools`' off-ramp strips only the
    three `rag_lookup_*`. The failing turn made retrieval calls, so its budget
    was non-zero and the whole universal set was bound.

    Left behind as the standing check that the diagnosis stays true: if this
    ever fails, G-49's cause moves from layer 2 to layer 1 and the fix is a
    different one.
    """
    for phase in PHASE_ORDER:
        _run(_c.executor(phase, _state(current_phase=phase)))
        assert "load_evidence_series" in stub_coach.tool_names, (
            f"{phase}: the tool the planner names is not bound — that is "
            f"layer 1, not layer 2"
        )


def test_the_upload_manifest_reaches_the_coach(stub_coach) -> None:
    """**LAYERS 3 AND 4, AND WHAT THE COACH DOES SEE.**

    Awareness is not the gap. The manifest puts the file, its `NOT YET READ`
    state, its `blob_path` and the tool that opens it in front of the model
    every turn — measured live at 2893 composed chars on the failing run. So
    the coach that issued 18 evidence searches was not uninformed; it was
    uninstructed, which is what makes layer 2 the cause and layer 4 an
    aggravator rather than the explanation.

    Layer 3 — *the model sees the plan and deprioritises it* — is excluded by
    construction, not by measurement: a model cannot deprioritise what is not
    in its request.

    **This also closes a coverage hole.** The manifest landed at 6.12 with no
    test; `_upload_manifest` appears in no assertion anywhere in the suite.
    """
    state = _state(uploads=[_unread_upload()])
    _run(_c.executor("define", state))

    block = stub_coach.injected_block
    assert "FILES THE BELT HAS UPLOADED THIS PHASE" in block
    assert "uploads/IMPR-TEST-618/complaints.csv" in block
    assert "NOT YET READ" in block
    assert "load_evidence_series" in block, (
        "the manifest names the tool that opens the file — without it the "
        "coach is told a file exists and not how to read it"
    )
