"""G-138 — an empty teaching block is filled from the skill (founder rulings 2026-09-29, item 2;
DEF-005: every teaching reply carries an explanation, an example and the ask).

Run 113121, turn 31: the store-and-advance reply teaching the SIPOC came back with all three
blocks empty; the executor logged the finding and the Belt saw no example. A teaching block the
coach returns empty is now written in code from the element's script — the same source the coach
is given — and a block the coach wrote is never replaced.
"""
from __future__ import annotations

import asyncio

import pytest
from langchain_core.messages import AIMessage

from backend.core.substate import CoachingPlan, CoachingResponse
from backend.middleware.skills import teaching_blocks
from backend.phases import nodes_common as _c
from backend.phases.define.schema import DEFINE_FIELD_ORDER


@pytest.mark.parametrize("field", DEFINE_FIELD_ORDER)
def test_g138_every_element_has_three_teaching_blocks_in_its_script(field: str) -> None:
    blocks = teaching_blocks("define", field)
    assert set(blocks) == {"explanation", "example", "prompt"}, (field, blocks)
    assert blocks["example"].startswith("Illustration — not your data:"), field
    assert "{" not in "".join(blocks.values()), field
    assert "?" in blocks["prompt"], field


def test_g138_a_table_example_keeps_its_rows() -> None:
    """The SIPOC's and the 5W2H's Show is a table: one row per line, as the script has it."""
    for field, header in (("process_map_sipoc", "| Suppliers | Inputs | Process | Outputs | Customers |"),
                          ("problem_statement", "| What |")):
        example = teaching_blocks("define", field)["example"]
        rows = [ln for ln in example.splitlines() if ln.startswith("|")]
        assert len(rows) >= 3 and any(header in r for r in rows), (field, rows[:2])


def _reply(**blocks: str) -> CoachingResponse:
    return CoachingResponse(message="Next, the SIPOC.", fields_captured=[], citations=[],
                            **{"explanation": "", "example": "", "prompt": "", "progress": "", **blocks})


def test_g138_an_empty_teaching_block_is_written_from_the_script_and_a_written_one_kept() -> None:
    script = teaching_blocks("define", "process_map_sipoc")
    plan = CoachingPlan(focus_field="process_map_sipoc", status="answered", move="store_and_advance",
                        stored_field="secondary_metrics")
    reply = _reply(explanation="The coach's own explanation.")
    out = _c._with_teaching_blocks("define", plan, reply, ["example", "prompt", "progress"])
    assert out.explanation == "The coach's own explanation."
    assert out.example == script["example"] and out.prompt == script["prompt"]
    assert reply.example == reply.prompt == "", "a copy — the coach's reply object is not changed"


@pytest.mark.parametrize("move", ["read_back", "challenge", "respond"])
def test_g138_a_move_that_does_not_teach_is_left_as_the_coach_wrote_it(move: str) -> None:
    plan = CoachingPlan(focus_field="team", status="answered", move=move)
    reply = _reply()
    out = _c._with_teaching_blocks("define", plan, reply, ["explanation", "example", "prompt"])
    assert out is reply and out.explanation == out.example == out.prompt == ""


def test_g138_an_empty_teaching_block_never_reaches_the_belt(stub_coach) -> None:
    """End to end through the executor: the stub coach returns all three blocks empty on a teach
    move; the blocks the reply carries to the Belt are the script's."""
    from backend.tests.test_executor import _state
    plan = CoachingPlan(focus_field="team", status="untaught", move="teach",
                        retrieval_strategy="single_hop", retrieval_hops=[])
    out = asyncio.run(_c.executor("define", _state(coaching_plan=plan)))
    reply = next(m for m in reversed(out["messages"]) if isinstance(m, AIMessage))
    blocks = reply.additional_kwargs["coaching_blocks"]
    script = teaching_blocks("define", "team")
    for k in ("explanation", "example", "prompt"):
        assert blocks[k] == script[k], k
