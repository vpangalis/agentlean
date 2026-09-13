"""The ordering of the middleware stack, OBSERVED rather than asserted — G-52.

**Why this file exists beside `test_middleware.py`'s stack tests.**
`test_the_declared_middleware_list_is_the_ratified_layering` runs under the
`stub_coach` fixture, which replaces `create_agent` itself. No graph is built,
no hook fires, and the assertion reduces to `reversed(declared)` — the ratified
order restated, then compared with itself. It is a useful check of the LIST and
it cannot observe EXECUTION.

The cost was measured: CLAUDE.md §8.1 carried the declaration order backwards
from step 6.5 until 2026-09-12, ARCHITECTURE.md §19 until v1.22, and the
package docstring until `886b987`. The suite was green every one of those days.

**No live model.** The defect is in the graph LangChain builds at construction
time, which is decided before any completion is requested, so
`GenericFakeChatModel` is sufficient — and G-53 means a live model is not
reliably available anyway. Nothing here touches the network.
"""
from __future__ import annotations

import asyncio
import functools
from typing import Any

import pytest
from langchain.agents.middleware import AgentMiddleware
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from backend.core.substate import PhaseState
from backend.middleware import coherence as coherence_module
from backend.middleware import grader as grader_module
from backend.middleware.coherence import CoherenceMiddleware
from backend.middleware.contradiction import ContradictionDetectionMiddleware
from backend.middleware.grader import DMAICGraderMiddleware
from backend.middleware.skills import DMAICSkillsMiddleware
from backend.middleware.state_injection import BeforeModelStateInjection
from backend.phases import nodes_common as _c

#: The async twin on `AgentMiddleware` delegates to the sync hook, so an
#: instrumented class reports both for ONE entry into the middleware.
_TWIN = {"aafter_agent": "after_agent", "abefore_agent": "before_agent"}


class _Structured:
    """`get_llm(...).with_structured_output(S)` -> something returning an S."""

    def __init__(self, schema: Any) -> None:
        self._schema = schema

    async def ainvoke(self, _prompt: Any) -> Any:
        if self._schema.__name__ == "CoherenceResult":
            return self._schema(coherent=True, is_conclusive=True,
                                is_parroting=False, on_topic=True)
        return self._schema()

    def invoke(self, _prompt: Any) -> Any:
        raise AssertionError("the coach loop is async (§1.4)")


class _FakeLLM(GenericFakeChatModel):
    def with_structured_output(self, schema: Any, **_: Any) -> Any:
        return _Structured(schema)


def _fake_llm(*_a: Any, **_k: Any) -> Any:
    return _FakeLLM(messages=iter([AIMessage(content="A coaching turn.")] * 60))


def _state() -> PhaseState:
    return {                                       # type: ignore[return-value]
        "case_id": "IMPR-G52", "current_phase": "define", "messages": [],
        "history": [], "phase_context": "", "coaching_plan": None,
        "field_index": 0, "draft": {}, "artifacts": {}, "step_log": [],
        "belt_edits": {}, "turn_count": 0, "final": {}, "gate_attempts": 0,
        "validator_feedback": [], "rejection_feedback": [], "citations": [],
        "uploads": [], "asks": [], "hop_results": [], "synthesis_output": None,
    }


@pytest.fixture
def observed(monkeypatch) -> list[tuple[str, str]]:
    """Run ONE turn through the REAL `create_agent`, recording what fires.

    Instrumentation wraps each middleware's own hook **at class level, before
    the agent is built**, so LangChain's
    `m.__class__.after_agent is not AgentMiddleware.after_agent` discrimination
    is unchanged and every hook body still runs.
    """
    fired: list[tuple[str, str]] = []
    seen: set[tuple[str, str]] = set()

    for module in (_c, coherence_module, grader_module):
        monkeypatch.setattr(module, "get_llm", _fake_llm, raising=False)

    for cls in (BeforeModelStateInjection, DMAICSkillsMiddleware,
                DMAICGraderMiddleware, CoherenceMiddleware,
                ContradictionDetectionMiddleware):
        for hook in ("before_agent", "abefore_agent",
                     "after_agent", "aafter_agent"):
            original = getattr(cls, hook, None)
            if original is None or original is getattr(AgentMiddleware, hook, None):
                continue

            # `functools.wraps` is load-bearing, not tidiness: LangChain
            # INSPECTS each hook's signature to decide whether to pass
            # `runtime`, so a bare `*a, **kw` wrapper makes it pass one
            # argument to a two-argument hook. The first cut of this file
            # failed exactly that way.
            @functools.wraps(original)
            def record(self, *a, _o=original, _c=cls, _h=hook, **kw):
                key = (_c.__name__, _TWIN.get(_h, _h))
                if key not in seen:
                    seen.add(key)
                    fired.append(key)
                return _o(self, *a, **kw)

            @functools.wraps(original)
            async def arecord(self, *a, _o=original, _c=cls, _h=hook, **kw):
                key = (_c.__name__, _TWIN.get(_h, _h))
                if key not in seen:
                    seen.add(key)
                    fired.append(key)
                return await _o(self, *a, **kw)

            monkeypatch.setattr(
                cls, hook,
                arecord if asyncio.iscoroutinefunction(original) else record)

    agent, _log = _c._build_executor("define", _state())
    asyncio.run(agent.ainvoke({"messages": [HumanMessage(content="Where do I start?")]},
                              config={"recursion_limit": 12}))
    return fired


def _order(fired: list[tuple[str, str]], hook: str) -> list[str]:
    return [name for name, h in fired if h == hook]


def test_after_agent_executes_contradiction_then_coherence_then_grader(observed):
    """**The assertion this whole file exists for.**

    Positions 6, 7 and 8 are DECLARED grader, coherence, contradiction and
    EXECUTE contradiction, coherence, grader — because `after_*` hooks fire
    innermost-first. Nothing here reads the declared list; this is what the
    compiled graph actually did.
    """
    assert _order(observed, "after_agent") == [
        "ContradictionDetectionMiddleware",
        "CoherenceMiddleware",
        "DMAICGraderMiddleware",
    ], (
        "after_* hooks fire in the REVERSE of declaration order. If this fails "
        "while the declaration list is unchanged, LangChain's composition "
        "changed and §19's ordering rules need re-deriving — not this test "
        "re-baselining"
    )


def test_before_agent_executes_state_injection_then_skills(observed):
    """The other direction, in the same turn: `before_*` fires first-to-last.

    Both clauses are checked on one run precisely because they are OPPOSITE and
    a test that saw only one could not tell the difference.
    """
    assert _order(observed, "before_agent") == [
        "BeforeModelStateInjection",
        "DMAICSkillsMiddleware",
    ], "position 1 must reach the prompt before skills loading (S-C11 B4)"


def test_this_observes_a_real_graph_and_not_a_stub(observed):
    """The property that makes the two assertions above worth anything.

    `test_middleware.py`'s stack test replaces `create_agent`; this one does
    not, so hooks genuinely fired. If nothing fired, the assertions above would
    pass vacuously on two empty lists — which is the G-52 shape reappearing
    inside its own fix.
    """
    assert observed, "no hook fired — the agent was stubbed and nothing ran"
    assert len({name for name, _ in observed}) == 5, (
        "all five custom middlewares must have been entered"
    )
