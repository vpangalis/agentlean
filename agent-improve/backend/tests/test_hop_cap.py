"""G-83 — the hop cap must be REACHABLE, not merely declared. Step 6.35.

**AN UNREACHABLE CAP IS UNFALSIFIABLE, AND THAT IS HOW FIVE SURVIVED ELEVEN
STEPS.** `COACH_HOP_BUDGET = 5` was written at step 6.7 on top of a per-hop
cost introduced at step 5.2 that already excluded it: at ~9.5s a hop, a fifth
lands near 47.5s against a 40s node budget, so every turn died on the wall
before the cap could fire. `_HOP_BUDGET_SPENT` was unreachable code, and 6.7's
live half — *"the opening turns coach rather than cap"* — was trivially true
because capping was impossible.

**The existing cap tests in `test_executor.py` are budget-RELATIVE** — they
drive `COACH_HOP_BUDGET + 1` calls and assert the last is refused, so they pass
at any value including one that cannot be reached in practice. They prove the
mechanism. **This file proves the NUMBER**, which is the half that was missing.
"""
from __future__ import annotations

import backend.phases.nodes_common as nc
from backend.phases.nodes_common import (
    COACH_HOP_BUDGET,
    EXECUTOR_SOFT_BUDGET,
    HOP_BUDGET_COMPOSE_RESERVE,
    MEASURED_HOP_SECONDS,
)


def _worst_case_seconds(cap: int) -> float:
    """Wall-clock for a turn that spends its whole budget, then composes."""
    return cap * MEASURED_HOP_SECONDS + HOP_BUDGET_COMPOSE_RESERVE


def test_the_cap_can_actually_fire_inside_the_node_budget() -> None:
    """**THE POINT OF THE CHANGE, AND THE TEST THAT WAS MISSING.**

    A coach that spends every hop must still reach `_HOP_BUDGET_SPENT` and
    compose, INSIDE `EXECUTOR_SOFT_BUDGET`. If the arithmetic does not fit, the
    node's own timeout fires first (6.34), the Belt gets the degraded answer,
    and the cap is decoration.
    """
    worst = _worst_case_seconds(COACH_HOP_BUDGET)
    assert worst <= EXECUTOR_SOFT_BUDGET, (
        f"a full-budget turn needs ~{worst:.1f}s "
        f"({COACH_HOP_BUDGET} hops x {MEASURED_HOP_SECONDS}s + "
        f"{HOP_BUDGET_COMPOSE_RESERVE}s to compose) against a "
        f"{EXECUTOR_SOFT_BUDGET}s node budget — the cap cannot fire, so it is "
        f"dead configuration exactly as COACH_HOP_BUDGET = 5 was (G-83)")


def test_the_old_cap_of_five_would_fail_this_test() -> None:
    """The check must REJECT the value it was written to retire.

    A test that passes at both 3 and 5 would not have caught the defect and
    would not catch its return. Asserted on the arithmetic rather than by
    re-importing, so it holds whatever the constant currently is.
    """
    assert _worst_case_seconds(5) > EXECUTOR_SOFT_BUDGET, (
        "five hops now fit the budget — either the node budget was raised or "
        "per-hop cost fell. Re-measure MEASURED_HOP_SECONDS and revisit the "
        "cap deliberately; do not let this test quietly start allowing five")


def test_the_cap_is_three() -> None:
    """Pins the ruled value. The two tests above say the number is SOUND;
    this says it is the number the founder ruled on 2026-09-18."""
    assert COACH_HOP_BUDGET == 3


def test_one_more_hop_would_not_fit() -> None:
    """The cap is the LARGEST value that fits, not merely a value that does.

    A cap of 1 would pass the reachability test and throw away retrieval the
    turn could afford. This pins that 3 is the ceiling rather than a guess
    under it.
    """
    assert _worst_case_seconds(COACH_HOP_BUDGET + 1) > EXECUTOR_SOFT_BUDGET, (
        f"{COACH_HOP_BUDGET + 1} hops also fit — the cap is lower than it "
        f"needs to be and is discarding retrieval the turn could afford")


def test_the_measurement_carries_its_provenance() -> None:
    """**A constant justified by a measurement nobody can find is a constant
    nobody can revise**, which is how the per-hop cost went unexamined from
    5.2 to 6.35. The docstring must name where the number came from."""
    import inspect
    src = inspect.getsource(nc)
    i = src.index("MEASURED_HOP_SECONDS = ")
    provenance = src[max(0, i - 700):i]
    assert "9.5" in provenance or "~9.5s" in provenance
    for cite in ("G-63", "ca6ba417"):
        assert cite in provenance, (
            f"the measurement does not cite {cite} — a future reader cannot "
            f"check it and so cannot revise it")


def test_the_reserve_is_not_zero() -> None:
    """Hops are not the only cost in a turn. A reserve of 0 would make the
    arithmetic pass while leaving nothing for the coach's own model calls,
    which is how a turn that 'fits' still dies on the wall."""
    assert HOP_BUDGET_COMPOSE_RESERVE > 0
    assert HOP_BUDGET_COMPOSE_RESERVE >= MEASURED_HOP_SECONDS, (
        "the reserve should cover at least one hop's worth of model and "
        "composition time, or a slow model day eats it")
