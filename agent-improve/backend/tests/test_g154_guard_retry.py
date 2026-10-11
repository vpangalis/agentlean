"""G-154 (2026-10-11): the input guard failed closed on ONE Prompt Shields ReadTimeout (the client's
5 s limit) — run define_runthrough_20261011T152731, turn 26: an ordinary Belt answer refused with
"screening unavailable". A transient failure (connection, timeout, 5xx) is now tried once more by the
node's retry policy, then the guard fails closed; a 4xx and an attack verdict are never retried (T92
unchanged). Prompt Shields is replaced at `content_safety._post`: no live call.
"""
from __future__ import annotations

import asyncio
from typing import Any

import httpx
import pytest
from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from backend.core import content_safety, graph, guard, guard_messages
from backend.core.state import SupervisorState

CLEAN = {"userPromptAnalysis": {"attackDetected": False}, "documentsAnalysis": []}
ATTACK = {"userPromptAnalysis": {"attackDetected": True}, "documentsAnalysis": []}


def _status(code: int) -> httpx.HTTPStatusError:
    req = httpx.Request("POST", "https://cs.example/contentsafety/text:shieldPrompt")
    return httpx.HTTPStatusError(str(code), request=req, response=httpx.Response(code, request=req))


def _guard_only():
    """The guard node exactly as the main graph adds it: its retry policy and its error handler."""
    b = StateGraph(SupervisorState)
    b.add_node(guard.NODE, guard.input_guard, retry_policy=guard.RETRY,
               error_handler=graph.degraded_handler(guard.NODE))
    b.add_edge(START, guard.NODE)
    b.add_edge(guard.NODE, END)
    return b.compile()


def _run(monkeypatch, answers: list) -> tuple[list, Any]:
    calls: list = []
    monkeypatch.setattr(content_safety, "configured", lambda: True)
    monkeypatch.setattr(content_safety.settings, "CONTENT_SAFETY_ENDPOINT", "https://cs.example")

    async def post(url: str, headers: dict, body: dict) -> dict:
        calls.append(1)
        answer = answers[min(len(calls), len(answers)) - 1]
        if isinstance(answer, BaseException):
            raise answer
        return answer
    monkeypatch.setattr(content_safety, "_post", post)
    state = {"messages": [HumanMessage(content="We pay 23% of supplier invoices late.")],
             "case_id": "IMPR-TEST", "current_phase": "define"}
    out = asyncio.run(_guard_only().ainvoke(state, {"configurable": {"entry": "ask"}}))
    return calls, out


def test_the_main_graph_adds_the_guard_with_its_retry_policy() -> None:
    node = graph.graph_builder().nodes[guard.NODE]
    assert node.retry_policy == guard.RETRY or node.retry_policy == [guard.RETRY] \
        or guard.RETRY in (node.retry_policy or ()), node.retry_policy
    assert guard.RETRY.max_attempts == 2


@pytest.mark.parametrize("first", [httpx.ReadTimeout("timed out"), httpx.ConnectError("refused"), _status(503)],
                         ids=["timeout", "connection", "5xx"])
def test_g154_one_transient_failure_is_tried_again_and_the_turn_passes(monkeypatch, first) -> None:
    calls, out = _run(monkeypatch, [first, CLEAN])
    assert len(calls) == 2
    assert not guard.blocked(out), out["messages"][-1]


def test_g154_two_transient_failures_fail_closed_with_the_unavailable_reply(monkeypatch) -> None:
    calls, out = _run(monkeypatch, [httpx.ReadTimeout("timed out"), httpx.ReadTimeout("timed out")])
    assert len(calls) == 2
    last = out["messages"][-1]
    assert isinstance(last, AIMessage) and guard.blocked(out)
    assert last.content == guard_messages.UNAVAILABLE
    verdict = last.additional_kwargs[guard.NODE]
    assert verdict["rule"] == "unreachable" and verdict["attempts"] == 2, verdict


@pytest.mark.parametrize("answer", [_status(429), _status(401), ATTACK], ids=["429", "401", "attack"])
def test_g154_a_4xx_or_an_attack_verdict_is_never_retried(monkeypatch, answer) -> None:
    calls, out = _run(monkeypatch, [answer, CLEAN])
    assert len(calls) == 1
    assert guard.blocked(out)
