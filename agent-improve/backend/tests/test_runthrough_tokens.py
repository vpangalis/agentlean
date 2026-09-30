"""Founder 2026-09-30 (review of 309f9fc), item 4: a run records its tokens per role, per model and
in total, so its cost can be computed. The counter reads them from each call's result."""
from __future__ import annotations

import asyncio

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from scripts import move_proof_661 as mp


def test_each_call_records_its_tokens_and_the_run_totals_them(monkeypatch) -> None:
    from langchain_core.language_models.chat_models import BaseChatModel
    monkeypatch.setattr(BaseChatModel, "agenerate", BaseChatModel.agenerate)   # restored after
    monkeypatch.setattr(mp, "CALLS", [])
    monkeypatch.setattr(mp, "COACH_INPUTS", [])
    mp._count_model_calls(cap=10)
    reply = AIMessage(content="ok", usage_metadata={"input_tokens": 1200, "output_tokens": 80, "total_tokens": 1280},
                      response_metadata={"model_name": "gpt-4o-2024-11-20"})
    model = GenericFakeChatModel(messages=iter([reply, reply]))
    for text in ("## 1 · COACHING RULES — how to behave", "You judge ONE thing"):
        asyncio.run(model.ainvoke([SystemMessage(content=text), HumanMessage(content="hi")]))
    assert [c["kind"] for c in mp.CALLS] == ["coach", "planner-judgment"]
    assert mp.CALLS[0]["input_tokens"] == 1200 and mp.CALLS[0]["output_tokens"] == 80
    assert mp.CALLS[0]["model"] == "gpt-4o-2024-11-20"
    t = mp.token_totals(mp.CALLS)
    assert t["total"] == {"calls": 2, "input_tokens": 2400, "output_tokens": 160}
    assert t["by_role"]["coach"]["input_tokens"] == 1200
    assert t["by_model"]["gpt-4o-2024-11-20"]["calls"] == 2
