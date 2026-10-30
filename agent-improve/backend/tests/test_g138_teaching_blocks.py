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
    # R10 (ADR-0095 decision 1, ACCEPTED 2026-10-30): the SIPOC's ask is the founder's one ask, word for word — an
    # imperative; every other element's ask is a question.
    one_ask = "Upload any process file or picture, or describe the process."
    assert ("?" in blocks["prompt"]) if field != "process_map_sipoc" else blocks["prompt"] == one_ask, field


def test_g138_a_table_example_keeps_its_rows() -> None:
    """The 5W2H's Show is a table: one row per line, as the script has it. (The SIPOC's example is the skill's
    structured file, drawn by code — DEF-211, founder note under ADR-0070, 2026-10-22 — so its Show is no table.)"""
    for field, header in (("problem_statement", "| What |"),):
        example = teaching_blocks("define", field)["example"]
        rows = [ln for ln in example.splitlines() if ln.startswith("|")]
        assert len(rows) >= 3 and any(header in r for r in rows), (field, rows[:2])
    sipoc = teaching_blocks("define", "process_map_sipoc")["example"]
    assert "drawn below" in sipoc and not [ln for ln in sipoc.splitlines() if ln.startswith("|")], sipoc


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
    """End to end through the executor, on a Define teach move.

    R-C (ADR-0114): the coach is not called — the reply is the element card, assembled in code; the
    card carries the teaching, so the three blocks beside it are empty by design and the call budget
    records no coach call. G-138's filler still runs where a teaching move is the coach's — an
    upload turn (`test_g138_on_an_upload_turn_an_empty_teaching_block_never_reaches_the_belt`)."""
    from backend.middleware.skills import card_parts
    from backend.tests.test_executor import _state
    plan = CoachingPlan(focus_field="team", status="untaught", move="teach",
                        retrieval_strategy="single_hop", retrieval_hops=[])
    out = asyncio.run(_c.executor("define", _state(coaching_plan=plan)))
    assert stub_coach.invocations == [], "a Define teach move makes no coach call"
    executor = [e for e in out["step_log"] if e.get("node") == "executor"][-1]
    assert executor["call_budget"]["coach"] == 0, executor["call_budget"]
    reply = next(m for m in reversed(out["messages"]) if isinstance(m, AIMessage))
    blocks = reply.additional_kwargs["coaching_blocks"]
    for k in ("explanation", "example", "prompt"):
        assert blocks[k] == "", k
    card = reply.additional_kwargs["teaching_card"]
    assert card["field"] == "team", card
    assert card["your_turn"]["question"] == card_parts("define", "team")["question"], card


def test_g138_on_an_upload_turn_an_empty_teaching_block_never_reaches_the_belt(stub_coach) -> None:
    """End to end through the executor: the stub coach returns all three blocks empty on a teach
    move; the blocks the reply carries to the Belt are the script's. An upload turn, because there a
    Define teaching move is still the coach's (R-C, ADR-0114: it reads the file)."""
    from backend.tests.test_executor import _state, _unread_upload
    plan = CoachingPlan(focus_field="team", status="untaught", move="teach",
                        retrieval_strategy="single_hop", retrieval_hops=[])
    out = asyncio.run(_c.executor("define", _state(coaching_plan=plan, uploads=[_unread_upload()])))
    assert len(stub_coach.invocations) == 1, "an upload turn is the coach's"
    reply = next(m for m in reversed(out["messages"]) if isinstance(m, AIMessage))
    blocks = reply.additional_kwargs["coaching_blocks"]
    script = teaching_blocks("define", "team")
    from backend.core.prompts import SAMPLE_MARK
    for k in ("explanation", "example", "prompt"):
        # C3 (DEF-083): the sample the Belt is shown carries its mark, written in code.
        assert blocks[k] == (f"{SAMPLE_MARK}\n{script[k]}" if k == "example" else script[k]), k
