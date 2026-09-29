"""G-84 — an executor timeout must not reach the Belt as a 500.

**THE ESCAPE CAUSE IS WHY THIS FILE EXISTS, NOT THE DEFECT.** No test exercised
a node that exceeds its wall, because tests run fast — so the one failure mode
that needs wall-clock to reproduce was the one the suite could not reach. It
shipped a 500 carrying a stack trace against §4.8's *never a hard failure to
the Belt*, and the same module that promises *"a Belt mid-session never sees a
stack trace"* carries the policy that guaranteed they would.

**T70 (DEF-078, 2026-09-29): the limit is LangGraph's own** — the executor node's
`TimeoutPolicy` and its `error_handler=` (`nodes_common.executor_timeout_handler`),
which composes the move's reply in code when the wall fires. The hand-written
`asyncio.wait_for` budget this file used to pin is gone, and the tests below pin
its absence. The wall is still injected, never waited for: the timed turn is
`test_turn_budget.py::test_a_slow_turn_answers_before_the_wall`, under a one-second wall.
"""
from __future__ import annotations

import asyncio
from typing import Any

import pytest

from backend.phases import nodes_common
from backend.phases.nodes_common import (
    _TIMEOUT_MESSAGE,
    _executor_status,
)
from backend.phases.subgraph_common import EXECUTOR_RUN_TIMEOUT, PLANNER_RETRY


# ── the relationship the whole fix rests on ─────────────────────────────────

def test_the_executor_wall_leaves_the_turn_inside_r13() -> None:
    """T70: the engine's wall on the executor, 40 s, so the planner's judgment and the composed
    answer fit R13's 45 s turn."""
    assert EXECUTOR_RUN_TIMEOUT <= 40


def test_the_limit_the_handler_and_the_retry_are_langgraphs_on_the_compiled_graph() -> None:
    """T70: read off the COMPILED subgraph, never the source — the executor carries the engine's
    `TimeoutPolicy` and an `error_handler`, the planner a `RetryPolicy`."""
    from langgraph.types import TimeoutPolicy

    from backend.phases.subgraph_common import build_phase_subgraph
    for phase in ("define", "measure"):
        nodes = build_phase_subgraph(phase).builder.nodes
        ex = nodes["executor"]
        assert isinstance(ex.timeout, TimeoutPolicy) and ex.timeout.run_timeout == EXECUTOR_RUN_TIMEOUT, phase
        assert ex.error_handler_node is not None, f"{phase}: the executor has no error_handler"
        assert nodes["planner"].retry_policy == PLANNER_RETRY, phase


# ── the degraded turn ───────────────────────────────────────────────────────

# RETIRED at step 6.52 (G-92): `_SlowAgent` and
# `test_an_agent_that_outlives_the_budget_yields_a_degraded_answer`. It proved
# the budget by RE-IMPLEMENTING the executor's `wait_for` inside the test,
# around an agent that awaited a millisecond sleep — so it passed while two
# live turns hit the 45 s wall with a 500 (traces 01a0d215…, 01a0d28e…). The
# real executor node, under the real `TimeoutPolicy`, with a setup delay and a
# BLOCKING tool, is `test_turn_budget.py::test_a_slow_turn_answers_before_the_wall`.


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


def test_the_executor_has_no_hand_written_budget() -> None:
    """T70: no `asyncio.wait_for` and no `except asyncio.TimeoutError` in `executor` — parsed with
    `ast`, so a comment about either cannot satisfy or fail it."""
    import ast
    import inspect
    import textwrap

    from backend.phases import nodes_common as nc
    tree = ast.parse(textwrap.dedent(inspect.getsource(nc.executor)))
    waits = [n for n in ast.walk(tree) if isinstance(n, ast.Attribute) and n.attr == "wait_for"]
    catches = [h for n in ast.walk(tree) if isinstance(n, ast.Try) for h in n.handlers
               if isinstance(h.type, ast.Attribute) and h.type.attr == "TimeoutError"]
    assert not waits, "executor() still budgets its own agent call with asyncio.wait_for (T70)"
    assert not catches, "executor() still catches asyncio.TimeoutError itself (T70)"
    assert not hasattr(nc, "EXECUTOR_SOFT_BUDGET"), "the hand-written budget's constant is still defined"
