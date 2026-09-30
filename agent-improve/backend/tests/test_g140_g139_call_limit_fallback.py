"""G-140 and G-139 — founder rulings 2026-09-30, items 1 and 2.

Run define_runthrough_20260929T174434, turns 25-27: at element 10 (the benefits analysis) the
coach's one-call share on two answer turns ran out with no structured reply; code wrote the replies,
and the code-written read-back showed a Confirm that could not store (the Confirm at 27 stored
nothing).

G-140: a code-written read-back that carries nothing a Confirm could store is not offered — the
reply is "I couldn't process that answer — please send it again", no Confirm, and the element keeps
its status from before the turn. A code-written read-back that CAN store (a plain-words field) keeps
its Confirm.

G-139 (diagnosis only, no fix): when the call limit ends the coach, step_log and the move record
carry what the coach returned — its raw text, the tools it asked for, the tool results sent back —
and why the loop wanted another call. The run record copies the move record's `limit`.
"""
from __future__ import annotations

import asyncio
from typing import Any

import pytest
from langchain_core.messages import AIMessage, ToolMessage

from backend.core.prompts import FALLBACK_RESEND
from backend.core.substate import CoachingPlan, PhaseState
from backend.phases import moves
from backend.phases import nodes_common as _c
from backend.tests.test_executor import _state

WORDS = ("Cost of the gap: about £68,000 a year in interest and lost discounts, from the savings "
         "calculation. It is sustainable — every year, not one-off. It would start in Q2 2027 at about "
         "£17,000 a quarter. Our finance contact is Sam Reid, management accountant, who will validate it.")


class _LimitedAgent:
    """What `create_agent`'s loop returns when ModelCallLimitMiddleware ends it: the coach's own
    output, then the limit's notice, and no structured response."""

    def __init__(self, tail: list[Any]) -> None:
        self.tail = tail

    async def ainvoke(self, payload: dict, *args: Any, **kwargs: Any) -> dict:
        return {"messages": [*payload.get("messages", []), *self.tail,
                             AIMessage(content=f"{_c._LIMIT_NOTICE}: run limit (1/1)")],
                "structured_response": None}


def _limited(monkeypatch, tail: list[Any]) -> None:
    monkeypatch.setattr("backend.phases.nodes_common.create_agent", lambda **kw: _LimitedAgent(tail))


def _read_back_turn(field: str, before: dict[str, Any]) -> PhaseState:
    pending = {"field": field, "fields": [field], "belt_words": WORDS, "messages": 1}
    plan = CoachingPlan(focus_field=field, status="asked", move="read_back", answer=WORDS, messages=1,
                        pending=pending, field_status={field: {"status": "answered", "answer": WORDS,
                                                               "messages": 1, "pending": pending}},
                        retrieval_strategy="single_hop", retrieval_hops=[])
    return _state(coaching_plan=plan, field_status={field: before})


def _reply(out: dict) -> AIMessage:
    return next(m for m in reversed(out["messages"]) if isinstance(m, AIMessage))


TOOL_TURN = [AIMessage(content="", tool_calls=[{"name": "calculate_expected_savings", "id": "c1",
                                                "args": {"annual_volume": 42000, "unit_cost": 9}}]),
             ToolMessage(content="Error: calculate_expected_savings is not a valid tool", name="calculate_expected_savings",
                         tool_call_id="c1", status="error")]


def test_g140_a_code_written_read_back_that_cannot_store_asks_for_the_answer_again(monkeypatch) -> None:
    _limited(monkeypatch, TOOL_TURN)
    before = {"status": "asked", "answer": "Roughly £9 an invoice.", "messages": 1}
    out = asyncio.run(_c.executor("define", _read_back_turn("benefits_analysis", before)))
    reply = _reply(out)
    assert reply.content == FALLBACK_RESEND
    record = reply.additional_kwargs[moves.MOVE_RECORD_KEY]
    assert record["move"] == moves.RESPOND and record["pending"] is None and record["resend"] is True
    assert record["fallback"] is True
    assert out["field_status"]["benefits_analysis"] == before, "the turn changes nothing"
    blocks = reply.additional_kwargs["coaching_blocks"]
    assert blocks["explanation"] == blocks["example"] == blocks["prompt"] == ""
    step = next(e for e in out["step_log"] if "resend" in e)
    assert step["resend"] is True


def test_g140_a_code_written_read_back_that_can_store_keeps_its_confirm(monkeypatch) -> None:
    """A plain-words element stores the Belt's own words, so the Confirm under the code-written
    read-back can store — it stays a read-back."""
    _limited(monkeypatch, [AIMessage(content="Here is what you said.")])
    out = asyncio.run(_c.executor("define", _read_back_turn("business_case", {"status": "asked"})))
    record = _reply(out).additional_kwargs[moves.MOVE_RECORD_KEY]
    assert record["move"] == moves.READ_BACK and not record.get("resend")
    assert record["pending"]["store"] == {"business_case": WORDS}
    assert out["field_status"]["business_case"]["status"] == moves.ANSWERED


def test_g139_the_limit_records_the_tool_the_coach_asked_for_and_why(monkeypatch) -> None:
    _limited(monkeypatch, TOOL_TURN)
    out = asyncio.run(_c.executor("define", _read_back_turn("benefits_analysis", {"status": "asked"})))
    diag = _reply(out).additional_kwargs[moves.MOVE_RECORD_KEY]["limit"]
    assert diag["responses"][0]["tool_calls"][0]["name"] == "calculate_expected_savings"
    assert "42000" in diag["responses"][0]["tool_calls"][0]["args"]
    assert diag["tool_results"][0]["status"] == "error" and "not a valid tool" in diag["tool_results"][0]["content"]
    assert "calculate_expected_savings" in diag["why"] and "error" in diag["why"]
    step = next(e for e in out["step_log"] if e.get("limit"))
    assert step["limit"] == diag


@pytest.mark.parametrize("tail, why", [
    ([AIMessage(content="Here is your benefits analysis.")], "text with no structured reply"),
    ([], "no coach response was recorded"),
])
def test_g139_the_limit_says_why_another_call_was_wanted(monkeypatch, tail: list, why: str) -> None:
    _limited(monkeypatch, tail)
    out = asyncio.run(_c.executor("define", _read_back_turn("benefits_analysis", {"status": "asked"})))
    diag = _reply(out).additional_kwargs[moves.MOVE_RECORD_KEY]["limit"]
    assert why in diag["why"]


def test_g139_a_turn_the_limit_did_not_end_carries_no_diagnosis(stub_coach) -> None:
    out = asyncio.run(_c.executor("define", _state()))
    assert not any(e.get("limit") for e in out["step_log"])
