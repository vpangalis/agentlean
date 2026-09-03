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

from backend.core.llm import role_temperature
from backend.core.substate import CoachingPlan

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
