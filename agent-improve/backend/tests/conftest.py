"""Shared test fixtures — added at procedure step 6.1.

**One fixture, and it exists because step 6.1 gave the planner a real model
call.** Before 6.1 the planner built a stub dict and every test could call it
directly; now `phases/nodes_common._plan_turn` invokes the `planner`-role model
through structured output, so any test that reaches the planner would reach
Azure. Two test modules need the same stub — `test_phase_subgraphs.py` calls the
node directly, `test_turn_graph.py` drives it through the compiled graph — and a
second copy of it is a second thing to keep true.

**It stubs `get_llm`, not `_plan_turn`.** Patching the helper would skip the
code under test: the prompt build, the `with_structured_output(CoachingPlan)`
wiring and the role choice would all go unexercised while the tests still
looked green. Patching the factory leaves all three live and replaces only the
network call — and it lets the fixture ASSERT the role and the schema, which is
how §17's "planner role, temp 0.1" and S-C04 B1's "never JSON from raw text"
become checkable rather than conventions.
"""
from __future__ import annotations

from typing import Any

import pytest

from langchain_core.messages import AIMessage
from langgraph.errors import GraphRecursionError

from backend.core.llm import role_temperature
from backend.core.substate import CoachingPlan, CoachingResponse

#: What the fake planner returns unless a test sets `stub_planner.plan`.
#: A Define field name, since `_state()` defaults to that phase.
DEFAULT_PLAN = CoachingPlan(
    focus_field="business_case",
    next_action="ask the Belt for the business case",
    retrieval_strategy="single_hop",
    retrieval_hops=[],
)


class _FakePlannerModel:
    """Stands in for `get_llm("planner")` and its structured-output wrapper.

    Records what it was asked so the tests can assert on it rather than on the
    fact that nothing raised.
    """

    def __init__(self) -> None:
        self.plan: CoachingPlan = DEFAULT_PLAN
        self.prompts: list[str] = []
        self.schemas: list[Any] = []
        self.roles: list[str] = []
        self.temperatures: list[float | None] = []

    # `get_llm(role, temperature=None, ...)` — recorded, then returns self.
    def __call__(self, role: str, temperature: float | None = None,
                 **kwargs: Any) -> "_FakePlannerModel":
        self.roles.append(role)
        self.temperatures.append(temperature)
        return self

    def with_structured_output(self, schema: Any, **kwargs: Any) -> "_FakePlannerModel":
        self.schemas.append(schema)
        return self

    async def ainvoke(self, prompt: Any, *args: Any, **kwargs: Any) -> CoachingPlan:
        self.prompts.append(str(prompt))
        return self.plan

    # ── what the tests read ───────────────────────────────────────────────

    @property
    def calls(self) -> int:
        """How many times the planner actually invoked the model."""
        return len(self.prompts)

    @property
    def effective_temperature(self) -> float:
        """The temperature the call resolves to.

        `_plan_turn` passes none, so the role default applies — which is the
        point: §17 and §4.7 put the planner at 0.1, and `get_llm` documents an
        explicit temperature as a deliberate override.
        """
        assert self.temperatures and self.temperatures[-1] is None, (
            "the planner passed an explicit temperature — §17's 0.1 is the "
            "role default, not an override the call site should restate"
        )
        return role_temperature(self.roles[-1])


@pytest.fixture
def stub_planner(monkeypatch) -> _FakePlannerModel:
    """Replace the planner's model so no Azure call is made (step 6.1)."""
    fake = _FakePlannerModel()
    monkeypatch.setattr("backend.phases.nodes_common.get_llm", fake)
    return fake


# ── the executor's agent — step 6.2 ───────────────────────────────────────

DEFAULT_REPLY = CoachingResponse(
    message="Let's start with the business case. Here is what a good one "
            "looks like, then you build yours.",
    fields_captured=[],
    citations=[],
)


class _FakeAgent:
    """One `create_agent(...)` result, and the turns invoked through it."""

    def __init__(self, recorder: "_CreateAgentRecorder") -> None:
        self._rec = recorder

    async def ainvoke(self, payload: dict, *args: Any, **kwargs: Any) -> dict:
        self._rec.invocations.append(payload)
        self._rec.invoke_configs.append(dict(kwargs.get("config") or {}))
        if self._rec.raise_recursion:
            # §3.7's cap, as the real agent raises it. The executor must turn
            # this into a partial answer rather than letting it reach the Belt.
            raise GraphRecursionError("recursion limit reached")
        reply = self._rec.reply
        return {
            # The agent echoes what it was given and appends its own turn —
            # the shape the executor's tail-slice depends on.
            "messages": [*payload.get("messages", []),
                         *self._rec.tool_messages,
                         AIMessage(content=reply.message)],
            "structured_response": reply,
        }


class _CreateAgentRecorder:
    """Stands in for `create_agent`, recording HOW it was called.

    **The kwargs are the point, not just the stub.** CLAUDE.md §0.10 records
    that `prompt=` vs `system_prompt=` sat wrong in the canonical block for
    months, and §18 forbids binding tools onto a bare model. Recording the call
    lets a test assert both against the real construction site rather than
    against a comment.
    """

    def __init__(self) -> None:
        self.calls: list[dict[str, Any]] = []
        self.invocations: list[dict[str, Any]] = []
        self.invoke_configs: list[dict[str, Any]] = []
        self.reply: CoachingResponse = DEFAULT_REPLY
        self.tool_messages: list[Any] = []
        #: Make the next `ainvoke` raise §3.7's cap, as the real agent does.
        self.raise_recursion = False

    def __call__(self, **kwargs: Any) -> _FakeAgent:
        self.calls.append(kwargs)
        return _FakeAgent(self)

    @property
    def system_prompt(self) -> str:
        """The composed prompt from the most recent construction."""
        return str(self.calls[-1]["system_prompt"])

    @property
    def tool_names(self) -> list[str]:
        return [t.name for t in self.calls[-1]["tools"]]


@pytest.fixture
def stub_coach(monkeypatch) -> _CreateAgentRecorder:
    """Replace `create_agent` so the executor makes no Azure call (step 6.2).

    Stubs the CONSTRUCTOR rather than the model, for the same reason
    `stub_planner` stubs `get_llm` rather than `_plan_turn`: everything the
    executor node actually does — composing the prompt, reading
    `structured_response`, writing `fields_captured` into `artifacts`, merging
    citations, attaching the diagram payload — stays live, and only the model
    and its tool loop are replaced.
    """
    rec = _CreateAgentRecorder()
    monkeypatch.setattr("backend.phases.nodes_common.create_agent", rec)
    return rec
