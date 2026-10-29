"""The run-through's scripted Belt meets the rules its walk is checked against (G-349, G-350; 2026-10-29).

A rule that changes what an element needs (DEF-289's soft benefits) also changes what the scripted Belt must say:
the run-through of 2026-10-29 parked at element 10 because its benefits answer stated no soft benefit. And a change
that makes a turn faster (R-C: the teaching card written in code) can take away the slowness a scenario relied on.
Read from the scripts; no model call."""
from __future__ import annotations


def test_g349_the_walk_s_benefits_answer_states_its_soft_benefits() -> None:
    """DEF-289 (R7 amended): the benefits element needs the soft benefits, each with how it is seen, or a conscious
    none — the walk's good answer gives one, so its Confirm opens."""
    from backend.phases.define import parse
    from scripts.define_runthrough import GOOD
    benefits = parse.soft_benefits(GOOD["benefits_analysis"])
    assert benefits and parse.soft_benefits_stated({"soft_benefits": benefits}), benefits


def test_g350_scenario_c_puts_its_deadline_on_an_answer_turn() -> None:
    """Scenario (c) stops a turn at a 5 s hard limit. The opening is a teaching card written in code (~3 s, R-C),
    so the window is put on an answer to the business case, which the planner judges and the coach answers."""
    import inspect

    from scripts import hard_path_scenarios as h
    source = inspect.getsource(h.scenario_c_deadline)
    window = source.split("routes.TURN_HARD_LIMIT_S, routes.TURN_CLOSE_RESERVE_S = 6.0, 1.0", 1)[1].split("finally:")[0]
    assert "DEADLINE_ANSWER" in window and "OPENING" not in window, window
    assert h.DEADLINE_ANSWER.strip() and h.DEADLINE_ANSWER != h.OPENING
