"""G-153 (2026-10-11): the coach's call was cut off at its token limit (`finish_reason: length`) on a
read-back, so the agent loop ended with no structured reply — and the Belt got an EMPTY turn with no
move record, while the judges judged the PREVIOUS turn's text as this turn's
(run define_runthrough_20261011T152731, turn 5, element team).

The scripted coach answers as the API did: one response, no text, no tool call, finish reason
`length`. The turn runs through the real executor, `create_agent` and middleware stack.
"""
from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from backend.core.substate import CoachingPlan, SufficiencyJudgment
from backend.middleware.grader import DMAICGraderMiddleware
from backend.phases import moves
from backend.phases import nodes_common as _c
from backend.tests.test_executor import _state
from backend.validation.schemas import CoachingGraderVerdict


class _CutOff(GenericFakeChatModel):
    """One response cut off at the token limit: no text, no structured reply."""

    calls: list = []

    def bind_tools(self, tools: Any, **kwargs: Any) -> "_CutOff":
        return self

    def _generate(self, messages: Any, stop: Any = None, run_manager: Any = None, **kwargs: Any) -> Any:
        from langchain_core.outputs import ChatGeneration, ChatResult
        type(self).calls.append(1)
        msg = AIMessage(content="", response_metadata={"finish_reason": "length"})
        return ChatResult(generations=[ChatGeneration(message=msg)])


def test_g153_a_cut_off_coach_reply_is_written_in_code_never_empty(monkeypatch) -> None:
    _CutOff.calls = []
    real_llm = _c.get_llm
    monkeypatch.setattr(_c, "get_llm", lambda role, **kw: _CutOff(messages=iter([]))
                        if role == "coach" else real_llm(role, **kw))
    judged: list = []

    async def passing(self: Any, belt: str, coach: str) -> CoachingGraderVerdict:
        judged.append(coach)
        return CoachingGraderVerdict(criteria=[])
    monkeypatch.setattr(DMAICGraderMiddleware, "_grade", passing)

    plan = CoachingPlan(focus_field="benefits_analysis", status="asked", move="challenge",
                        judgment=SufficiencyJudgment(verdict="insufficient", reason="impact type missing"),
                        answer="about 9 pounds per late invoice", messages=1,
                        retrieval_strategy="single_hop", retrieval_hops=[])
    state = _state(coaching_plan=plan)
    state["messages"] = [AIMessage(content="An earlier turn's reply."), *state["messages"]]
    out = asyncio.run(_c.executor("define", state))

    reply = next(m for m in reversed(out["messages"]) if isinstance(m, AIMessage))
    assert str(reply.content).strip(), "the Belt was given an empty turn"
    record = reply.additional_kwargs[moves.MOVE_RECORD_KEY]
    assert record.get("fallback") is True, record
    assert "token limit" in record["limit"]["why"], record["limit"]
    assert len(_CutOff.calls) == 1, "the cut-off reply is not asked for again"
    assert "An earlier turn's reply." not in judged, "the grader judged the previous turn's text"


def test_g153_the_grader_reads_only_this_turns_coach_text() -> None:
    state = {"messages": [AIMessage(content="An earlier turn's reply."), HumanMessage(content="My answer."),
                          AIMessage(content="")]}
    assert DMAICGraderMiddleware._coach_text(state) == ""
    state["messages"].append(AIMessage(content="This turn's reply."))
    assert DMAICGraderMiddleware._coach_text(state) == "This turn's reply."
