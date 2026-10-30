"""Founder 2026-09-30 (review of 309f9fc), item 4: a run records its tokens per role, per model and in
total, so its cost can be computed. The counter reads them from each call's result.

Founder rulings 2026-10-27, item 10 and ADR-0111 D7 (a): each call also records the input tokens the provider
served from its prompt cache (`cached_input_tokens`), and the run sums them per role, per model and in total."""
from __future__ import annotations

import asyncio
from types import SimpleNamespace
from typing import Any

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from scripts import move_proof_661 as mp


def test_each_call_records_its_tokens_and_the_run_totals_them(monkeypatch) -> None:
    from langchain_core.language_models.chat_models import BaseChatModel
    monkeypatch.setattr(BaseChatModel, "agenerate", BaseChatModel.agenerate)   # restored after
    monkeypatch.setattr(mp, "CALLS", [])
    monkeypatch.setattr(mp, "COACH_INPUTS", [])
    mp._count_model_calls(cap=10)
    cached = AIMessage(content="ok", usage_metadata={"input_tokens": 1200, "output_tokens": 80, "total_tokens": 1280,
                                                     "input_token_details": {"cache_read": 1024}},
                       response_metadata={"model_name": "gpt-4o-2024-11-20"})
    plain = AIMessage(content="ok", usage_metadata={"input_tokens": 1200, "output_tokens": 80, "total_tokens": 1280},
                      response_metadata={"model_name": "gpt-4o-2024-11-20"})
    model = GenericFakeChatModel(messages=iter([cached, plain]))
    for text in ("## 1 · COACHING RULES — how to behave", "You judge ONE thing"):
        asyncio.run(model.ainvoke([SystemMessage(content=text), HumanMessage(content="hi")]))
    assert [c["kind"] for c in mp.CALLS] == ["coach", "planner-judgment"]
    assert mp.CALLS[0]["input_tokens"] == 1200 and mp.CALLS[0]["output_tokens"] == 80
    assert mp.CALLS[0]["cached_input_tokens"] == 1024 and mp.CALLS[1]["cached_input_tokens"] == 0
    assert mp.CALLS[0]["model"] == "gpt-4o-2024-11-20"
    t = mp.token_totals(mp.CALLS)
    assert t["total"] == {"calls": 2, "input_tokens": 2400, "cached_input_tokens": 1024, "output_tokens": 160}
    assert t["by_role"]["coach"]["input_tokens"] == 1200 and t["by_role"]["coach"]["cached_input_tokens"] == 1024
    assert t["by_role"]["planner-judgment"]["cached_input_tokens"] == 0
    assert t["by_model"]["gpt-4o-2024-11-20"] == {"calls": 2, "input_tokens": 2400, "cached_input_tokens": 1024,
                                                  "output_tokens": 160}


def _result(msg: AIMessage, llm_output: dict[str, Any] | None = None) -> Any:
    return SimpleNamespace(generations=[[SimpleNamespace(message=msg)]], llm_output=llm_output or {})


def test_the_cached_input_is_read_where_langchain_openai_puts_the_providers_cached_tokens() -> None:
    """ADR-0111 D7 (a): the installed langchain-openai's own usage builder turns the provider's
    `usage.prompt_tokens_details.cached_tokens` into `usage_metadata["input_token_details"]["cache_read"]`
    (`priority_cache_read` / `flex_cache_read` on those service tiers) — the counter reads that; without it, the
    provider's `llm_output["token_usage"]["prompt_tokens_details"]["cached_tokens"]`; 0 when neither reports one."""
    from langchain_openai.chat_models.base import _create_usage_metadata

    provider = {"prompt_tokens": 7000, "completion_tokens": 200, "total_tokens": 7200,
                "prompt_tokens_details": {"cached_tokens": 6144, "audio_tokens": 0},
                "completion_tokens_details": {"reasoning_tokens": 0, "audio_tokens": 0}}
    for tier in (None, "priority", "flex"):
        msg = AIMessage(content="", usage_metadata=_create_usage_metadata(provider, tier))
        got = mp._usage(None, _result(msg))
        assert got["input_tokens"] == 7000 and got["cached_input_tokens"] == 6144, (tier, got)
    no_metadata = AIMessage(content="")
    assert mp._usage(None, _result(no_metadata, {"token_usage": provider}))["cached_input_tokens"] == 6144
    none_cached = {"prompt_tokens": 7000, "completion_tokens": 200, "prompt_tokens_details": {"cached_tokens": 0}}
    msg = AIMessage(content="", usage_metadata=_create_usage_metadata(none_cached))
    assert mp._usage(None, _result(msg))["cached_input_tokens"] == 0
    assert mp._usage(None, _result(no_metadata))["cached_input_tokens"] == 0
    # A call recorded before the cache was counted (no key) adds 0, never fails.
    old = [{"kind": "coach", "model": "m", "input_tokens": 6800, "output_tokens": 250}]
    assert mp.token_totals(old)["by_role"]["coach"] == {"calls": 1, "input_tokens": 6800, "cached_input_tokens": 0,
                                                        "output_tokens": 250}


def test_each_coach_call_is_counted_as_a_read_back_or_a_question_call(monkeypatch) -> None:
    """Founder ruling 2026-10-30 (the coach-input ratchet, two ceilings): a coach call is a read-back call when the
    move code gave it in section 5 is READ BACK — the verbatim and the composed read-back — and a question call
    for every other move, `respond_pending`'s repeated read-back included (it answers a question first). The run
    totals the coach's tokens per kind (`by_coach_class`); a call of another role is in neither."""
    from backend.core.prompts import MOVE_INSTRUCTIONS
    read_backs = {k for k in MOVE_INSTRUCTIONS if mp.coach_class(MOVE_INSTRUCTIONS[k]) == "read_back"}
    assert read_backs == {"read_back_verbatim", "read_back_composed"}, read_backs
    assert mp.coach_class("") == "question"

    from langchain_core.language_models.chat_models import BaseChatModel
    monkeypatch.setattr(BaseChatModel, "agenerate", BaseChatModel.agenerate)   # restored after
    monkeypatch.setattr(mp, "CALLS", [])
    monkeypatch.setattr(mp, "COACH_INPUTS", [])
    mp._count_model_calls(cap=10)

    def reply(n: int) -> AIMessage:
        return AIMessage(content="ok", usage_metadata={"input_tokens": n, "output_tokens": 10, "total_tokens": n + 10},
                         response_metadata={"model_name": "gpt-4o-2024-11-20"})
    model = GenericFakeChatModel(messages=iter([reply(9000), reply(7000), reply(5000), reply(1500)]))
    rules = "## 1 · COACHING RULES — how to behave\n## 5 · THIS TURN'S MOVE\n"
    for text in (rules + MOVE_INSTRUCTIONS["read_back_composed"], rules + MOVE_INSTRUCTIONS["read_back_verbatim"],
                 rules + MOVE_INSTRUCTIONS["challenge"], "You judge ONE thing"):
        asyncio.run(model.ainvoke([SystemMessage(content=text), HumanMessage(content="hi")]))
    assert [c.get("coach_class") for c in mp.CALLS] == ["read_back", "read_back", "question", None]
    by_class = mp.token_totals(mp.CALLS)["by_coach_class"]
    assert by_class["read_back"] == {"calls": 2, "input_tokens": 16000, "cached_input_tokens": 0, "output_tokens": 20}
    assert by_class["question"] == {"calls": 1, "input_tokens": 5000, "cached_input_tokens": 0, "output_tokens": 10}
    assert set(by_class) == {"read_back", "question"}
