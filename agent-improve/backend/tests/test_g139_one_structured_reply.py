"""G-139 (8D ratified 2026-09-30): on an answer turn the coach's one allowed call returned TWO
identical `CoachingResponse` structured replies (parallel tool calls); LangChain's ToolStrategy
rejected them and asked again, the call limit ended the loop, and code wrote the reply
(run define_runthrough_20260930T102427, turn 25, element 10).

The scripted coach answers as the API does: two identical structured replies in one response when
parallel tool calls are allowed, one when the request says `parallel_tool_calls=False`. The turn runs
through the real executor, `create_agent` and middleware stack, as an answer turn (a judgment was
made, so the coach's share is ONE call), and must end in the coach's own reply.
"""
from __future__ import annotations

import asyncio
from typing import Any

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage

from backend.core.substate import CoachingPlan, SufficiencyJudgment
from backend.middleware.coherence import CoherenceMiddleware
from backend.middleware.grader import DMAICGraderMiddleware
from backend.phases import moves
from backend.phases import nodes_common as _c
from backend.tests.test_executor import _state
from backend.validation.schemas import CoachingGraderVerdict, CoherenceResult

REPLY = {"message": "Thanks — for your benefits analysis, is the saving sustainable or one-off?",
         "explanation": "", "example": "", "prompt": "Sustainable or one-off?", "progress": "x",
         "fields_captured": []}


class _TwiceUnlessSerial(GenericFakeChatModel):
    """Two identical structured replies per response unless the bind says parallel_tool_calls=False."""

    calls: list = []
    parallel: list = []

    def bind_tools(self, tools: Any, **kwargs: Any) -> "_TwiceUnlessSerial":
        type(self).parallel.append(kwargs.get("parallel_tool_calls", True))
        return self

    def _generate(self, messages: Any, stop: Any = None, run_manager: Any = None, **kwargs: Any) -> Any:
        from langchain_core.outputs import ChatGeneration, ChatResult
        type(self).calls.append(1)
        n = 1 if type(self).parallel and type(self).parallel[-1] is False else 2
        msg = AIMessage(content="", tool_calls=[
            {"name": "CoachingResponse", "args": REPLY, "id": f"call_{i}"} for i in range(n)])
        return ChatResult(generations=[ChatGeneration(message=msg)])


def test_g139_two_identical_structured_replies_still_end_in_a_coached_reply(monkeypatch) -> None:
    _TwiceUnlessSerial.calls, _TwiceUnlessSerial.parallel = [], []
    real_llm = _c.get_llm
    monkeypatch.setattr(_c, "get_llm", lambda role, **kw: _TwiceUnlessSerial(messages=iter([]))
                        if role == "coach" else real_llm(role, **kw))

    async def coherent(self: Any, belt: str, coach: str) -> CoherenceResult:
        return CoherenceResult(coherent=True, is_conclusive=True, is_parroting=False, on_topic=True, reason="")

    async def passing(self: Any, belt: str, coach: str) -> CoachingGraderVerdict:
        return CoachingGraderVerdict(criteria=[])
    monkeypatch.setattr(CoherenceMiddleware, "_check", coherent)
    monkeypatch.setattr(DMAICGraderMiddleware, "_grade", passing)

    plan = CoachingPlan(focus_field="benefits_analysis", status="asked", move="challenge",
                        judgment=SufficiencyJudgment(verdict="insufficient", reason="impact type missing"),
                        answer="about 9 pounds per late invoice", messages=1,
                        retrieval_strategy="single_hop", retrieval_hops=[])
    out = asyncio.run(_c.executor("define", _state(coaching_plan=plan)))

    reply = next(m for m in reversed(out["messages"]) if isinstance(m, AIMessage))
    record = reply.additional_kwargs[moves.MOVE_RECORD_KEY]
    assert not record.get("fallback"), record.get("limit")
    assert "sustainable or one-off" in str(reply.content)
    assert len(_TwiceUnlessSerial.calls) == 1, "one coach call — within the answer turn's share"
    assert _TwiceUnlessSerial.parallel and all(p is False for p in _TwiceUnlessSerial.parallel)
