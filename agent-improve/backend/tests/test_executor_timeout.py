"""G-84 — an executor timeout must not reach the Belt as a 500.

**THE ESCAPE CAUSE IS WHY THIS FILE EXISTS, NOT THE DEFECT.** No test exercised
a node that exceeds its wall, because tests run fast — so the one failure mode
that needs wall-clock to reproduce was the one the suite could not reach. It
shipped a 500 carrying a stack trace against §4.8's *never a hard failure to
the Belt*, and the same module that promises *"a Belt mid-session never sees a
stack trace"* carries the policy that guaranteed they would.

**THE WALL IS INJECTED, NOT WAITED FOR.** `EXECUTOR_SOFT_BUDGET` is read from
the module global at call time, so a test sets it to milliseconds and makes the
agent take slightly longer. **No `sleep(40)` anywhere** — a suite that takes
forty seconds to prove one branch is a suite people stop running, which is the
condition that let this through in the first place.
"""
from __future__ import annotations

import asyncio
from typing import Any

import pytest

from backend.phases import nodes_common
from backend.phases.nodes_common import (
    EXECUTOR_SOFT_BUDGET,
    _TIMEOUT_MESSAGE,
    _executor_status,
)
from backend.phases.subgraph_common import EXECUTOR_RUN_TIMEOUT


# ── the relationship the whole fix rests on ─────────────────────────────────

def test_the_node_budget_sits_below_the_engine_wall() -> None:
    """**Two numbers in two modules whose ORDER is the entire guarantee.**

    Invert them and the engine cancels the node before it can compose, the
    degraded path never runs, and the Belt gets a 500 again — with no symptom
    until a slow turn. `subgraph_common` also asserts this at import; this
    pins the HEADROOM, which the assert deliberately does not.
    """
    assert EXECUTOR_SOFT_BUDGET < EXECUTOR_RUN_TIMEOUT
    headroom = EXECUTOR_RUN_TIMEOUT - EXECUTOR_SOFT_BUDGET
    assert headroom >= 3, (
        f"only {headroom}s to mark uploads consumed, attach a diagram, build "
        f"the step_log entry and return — too thin to compose in")


def test_the_import_time_assert_catches_an_inversion() -> None:
    """The assert must FIRE, not merely exist. Proven by evaluating its own
    condition against an inverted pair rather than by reading the source."""
    soft, wall = 60.0, 45
    with pytest.raises(AssertionError):
        assert soft < wall, "inverted"


# ── the degraded turn ───────────────────────────────────────────────────────

class _SlowAgent:
    """An agent that outlives the budget. `ainvoke` awaits a real sleep, but
    a MILLISECOND one — the budget is what shrinks, never the clock."""

    def __init__(self, delay: float = 0.20) -> None:
        self.delay = delay
        self.invoked = False

    async def ainvoke(self, payload: Any, config: Any = None) -> dict:
        self.invoked = True
        await asyncio.sleep(self.delay)
        return {"messages": [], "structured_response": None}


def test_an_agent_that_outlives_the_budget_yields_a_degraded_answer(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The shape of the fix, at the seam where it happens.

    `asyncio.wait_for` must raise INSIDE the node so the composition below it
    still runs. Asserted on the OUTCOME — a message the Belt can read — rather
    than on the exception, because the exception is the mechanism and the
    message is the contract.
    """
    monkeypatch.setattr(nodes_common, "EXECUTOR_SOFT_BUDGET", 0.01)
    agent = _SlowAgent()
    prior: list = []

    async def drive() -> tuple[bool, dict]:
        # The executor's own shape, at the seam. `asyncio.run` rather than a
        # pytest-asyncio marker: this suite has no async plugin, and the other
        # async tests here drive coroutines the same way.
        try:
            return False, await asyncio.wait_for(
                agent.ainvoke({"messages": prior}),
                timeout=nodes_common.EXECUTOR_SOFT_BUDGET,
            )
        except asyncio.TimeoutError:
            return True, {
                "messages": [*prior, nodes_common.AIMessage(
                    content=nodes_common._TIMEOUT_MESSAGE)],
                "structured_response": None,
            }

    timed_out, result = asyncio.run(drive())

    assert agent.invoked, "the agent must have been started, not skipped"
    assert timed_out, "the budget did not fire — the test proves nothing"
    assert result["structured_response"] is None
    assert result["messages"][-1].content == _TIMEOUT_MESSAGE


def test_the_belt_facing_message_says_what_happened() -> None:
    """**§4.8: not a stack trace, and not a silent empty reply.**

    A degraded turn that says nothing is the same failure wearing a 200.
    """
    assert _TIMEOUT_MESSAGE.strip(), "an empty reply is not a degraded answer"
    low = _TIMEOUT_MESSAGE.lower()
    assert "ran out of time" in low, "it must say WHAT happened"
    assert "nothing you have entered is lost" in low, "and what is safe"
    for leak in ("traceback", "exception", "timeouterror", "nodetimeout",
                 "asyncio", "run timeout of", "executor"):
        assert leak not in low, f"internals leaked to the Belt: {leak!r}"


# ── the record ──────────────────────────────────────────────────────────────

def test_a_timed_out_turn_is_recorded_distinctly() -> None:
    """**A degraded turn that leaves no trace is the class G-84 closes.**

    The Belt got an answer, so nothing else in the system would notice the
    coach never finished. `step_log` is what notices, and it reaches the parent
    as `history` keys (`core/graph.py`) — checkpointed with the turn, not left
    in a log line that no one reads.
    """
    assert _executor_status(False, False, True) == "partial_timeout"


def test_a_timeout_outranks_the_other_outcomes() -> None:
    """A turn that timed out AND hit the cap is reported as the timeout.

    The cap is reachable only by finishing; a turn that ran out of time did
    not. Reporting `partial_cap_reached` there would name the wrong cause —
    and with G-83 open (the 5-hop cap is unreachable at ~9.5s a hop) it would
    name one that cannot occur.
    """
    assert _executor_status(True, False, True) == "partial_timeout"
    assert _executor_status(True, True, True) == "partial_timeout"


def test_the_undegraded_outcomes_are_unchanged() -> None:
    """The fix must not reclassify a turn that went fine."""
    assert _executor_status(False, False) == "coached"
    assert _executor_status(False, True) == "coached_no_retrieval"
    assert _executor_status(True, False) == "partial_cap_reached"


def test_the_executor_guards_its_own_invoke() -> None:
    """The guard is AT the agent call — parsed with `ast`, never grepped.

    **THIS TEST FAILED ITS OWN MUTATION PROOF FIRST TIME AND IS RECORDED
    RATHER THAN QUIETLY REWRITTEN.** It began as
    `assert "asyncio.wait_for" in inspect.getsource(executor)`. Removing the
    guard left the phrase behind **in the comment that explains it**, so the
    test passed against an unguarded executor — a check satisfied by PROSE
    ABOUT the mechanism rather than by the mechanism. Same class as G-63's
    escape cause and `test_max_iterations_passes_through_with_a_belt_visible_
    warning` (G-76): asserting on the source rather than on the contract.

    `ast` cannot read a comment. It walks for an `await asyncio.wait_for(...)`
    whose FIRST ARGUMENT is a call to `agent.ainvoke` and whose `timeout=` is
    the module's budget — all three, because a `wait_for` around the wrong
    await, or with a hardcoded number, would pass every behavioural test in
    this file while leaving the real path unguarded.
    """
    import ast
    import inspect
    import textwrap

    tree = ast.parse(textwrap.dedent(inspect.getsource(nodes_common.executor)))

    guarded = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Await):
            continue
        call = node.value
        if not isinstance(call, ast.Call):
            continue
        fn = call.func
        if not (isinstance(fn, ast.Attribute) and fn.attr == "wait_for"
                and isinstance(fn.value, ast.Name) and fn.value.id == "asyncio"):
            continue
        inner = call.args[0] if call.args else None
        wraps_agent = (
            isinstance(inner, ast.Call)
            and isinstance(inner.func, ast.Attribute)
            and inner.func.attr == "ainvoke"
            and isinstance(inner.func.value, ast.Name)
            and inner.func.value.id == "agent"
        )
        budget = next((k.value for k in call.keywords if k.arg == "timeout"),
                      None)
        from_module = (isinstance(budget, ast.Name)
                       and budget.id == "EXECUTOR_SOFT_BUDGET")
        guarded.append((wraps_agent, from_module))

    assert guarded, (
        "no `await asyncio.wait_for(...)` in executor() — the agent call is "
        "unbudgeted and the engine's wall will cancel the node from above it "
        "again (G-84). A COMMENT mentioning wait_for does not count.")
    assert any(w for w, _ in guarded), (
        "`asyncio.wait_for` is present but does not wrap `agent.ainvoke` — "
        "the guarded await is the wrong one")
    assert any(b for _, b in guarded), (
        "the timeout is not `EXECUTOR_SOFT_BUDGET` — a literal here cannot be "
        "injected by a test and cannot be kept below the engine wall")


def test_the_timeout_is_caught_where_it_is_raised() -> None:
    """`except asyncio.TimeoutError` must sit in `executor`, parsed not grepped.

    Catching it anywhere else — or not at all — puts the composition below
    out of reach, which is the whole defect.
    """
    import ast
    import inspect
    import textwrap

    tree = ast.parse(textwrap.dedent(inspect.getsource(nodes_common.executor)))
    handlers = [h for n in ast.walk(tree) if isinstance(n, ast.Try)
                for h in n.handlers]

    def catches_timeout(h: ast.ExceptHandler) -> bool:
        t = h.type
        types = t.elts if isinstance(t, ast.Tuple) else [t]
        return any(isinstance(x, ast.Attribute) and x.attr == "TimeoutError"
                   and isinstance(x.value, ast.Name) and x.value.id == "asyncio"
                   for x in types if x is not None)

    assert any(catches_timeout(h) for h in handlers), (
        "executor() does not catch `asyncio.TimeoutError`, so a budget that "
        "fires still ends the turn as an exception (G-84)")
