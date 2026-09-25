"""WIRED — step 6.63's second state, proven the only way that counts.

A step is **wired** when a test drives THE REAL COMPILED GRAPH through THE REAL
API ROUTE and shows the step's component ran — in `step_log`, the checkpoint,
or the response. Built (its symbol exists) is not wired: a symbol can exist
and be reached by nothing, which is how G-49, G-69 and G-76 all shipped.

WHAT IS REAL AND WHAT IS NOT
    real   `POST /ask`, `get_graph` and the compiled graph, the input mapper,
           the planner node, the executor node, `create_agent`, EVERY
           middleware on the stack, the capture merge, the output mapper,
           the route's projection
    fake   the model calls (a LangChain fake chat model returns a fixed
           `CoachingResponse` tool call; the planner, coherence and grader
           return fixed verdicts), the blob store (an in-memory case), and
           persistence (an in-memory checkpointer and store)

Each test here is named in Appendix F's *Wiring proofs* table with the
symbols it claims; `verify_built.py` checks those symbols are reachable from
`app.py`'s routes by an AST call-graph walk.
"""
from __future__ import annotations

from typing import Any

import pytest
from fastapi.testclient import TestClient
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.store.memory import InMemoryStore

from backend.core.substate import CoachingResponse
from backend.middleware.coherence import CoherenceMiddleware
from backend.middleware.grader import DMAICGraderMiddleware
from backend.validation.schemas import (
    CoachingGraderVerdict,
    CoherenceResult,
    CriterionResult,
)

CASE_ID = "IMPR-TEST-WIRED"
BELT = ("Late payments to our suppliers are costing us about £62,000 a year in "
        "interest and lost discounts.")
REPLY = {
    "message": "Here is your business case as you gave it — is this right?",
    "explanation": "The business case says why the project is worth doing.",
    "example": "Invoice errors cost ~€35k/month in rework.",
    "prompt": "Is this right, or would you change anything?",
    "progress": "anything the model writes",
    "fields_captured": [{"field_name": "business_case", "value": BELT, "source": "belt"}],
}


class _FakeCoach(GenericFakeChatModel):
    """LangChain's own fake chat model, with tool binding: `create_agent`
    binds the structured-response tool, and the fake answers with it."""

    def bind_tools(self, tools: Any, **kwargs: Any) -> "_FakeCoach":
        return self


def _coach() -> _FakeCoach:
    return _FakeCoach(messages=iter([AIMessage(content="", tool_calls=[
        {"name": "CoachingResponse", "args": REPLY, "id": "call_wired_1"}])]))


@pytest.fixture
def wired(monkeypatch, stub_planner):
    """One turn through the real route and graph; returns (response, saver)."""
    from backend.app import app
    from backend.core import graph as graph_mod
    from backend.gateway import routes
    from backend.phases import nodes_common
    from backend.storage.models import CaseDocument

    saver, store = InMemorySaver(), InMemoryStore()
    monkeypatch.setattr(graph_mod, "_persistence", lambda: (saver, store))
    # `get_graph` is lru_cached: a graph compiled earlier in the process holds
    # the REAL checkpointer, and the route would reuse it. Clear it so this
    # turn compiles against the in-memory saver — and clear it again after,
    # so no later test inherits the in-memory one.
    graph_mod.get_graph.cache_clear()
    request_cleanup = graph_mod.get_graph.cache_clear
    case = CaseDocument.new(case_id=CASE_ID, title="wiring proof", belt_level="green",
                            leader="Priya Shah", department="Finance",
                            target_date="2027-03-31", team=[])

    async def load(_cid: str):
        return case

    async def save(_c):
        return None

    monkeypatch.setattr(routes.blob, "storage_configured", lambda: True)
    monkeypatch.setattr(routes.blob, "load_case", load)
    monkeypatch.setattr(routes.blob, "save_case", save)
    monkeypatch.setattr(routes, "_ensure_case_record", lambda c: None)
    monkeypatch.setattr(routes, "_mirror_asks", lambda *a, **k: None)

    planner_llm = nodes_common.get_llm      # stub_planner's recorder
    monkeypatch.setattr(nodes_common, "get_llm",
                        lambda role, **kw: _coach() if role == "coach" else planner_llm(role, **kw))

    async def coherent(self, belt: str, coach: str) -> CoherenceResult:
        return CoherenceResult(coherent=True, is_conclusive=True, is_parroting=False,
                               on_topic=True, reason="")

    async def failing(self, belt: str, coach: str) -> CoachingGraderVerdict:
        return CoachingGraderVerdict(criteria=[CriterionResult(
            criterion="Coach must challenge weak inputs with specific follow-up questions",
            status="fail", feedback="ask how the figure was measured")])

    monkeypatch.setattr(CoherenceMiddleware, "_check", coherent)
    monkeypatch.setattr(DMAICGraderMiddleware, "_grade", failing)

    resp = TestClient(app).post("/ask", json={"case_id": CASE_ID, "user": "wired",
                                              "message": BELT, "phase": "define"})
    request_cleanup()
    assert resp.status_code == 200, resp.text
    assert saver.storage.get(CASE_ID), "the turn did not run on the in-memory saver"
    return resp.json(), saver


def _checkpoints(saver: InMemorySaver) -> list:
    """Every checkpoint of the turn, in EVERY namespace — `step_log` and
    `artifacts` live in the phase subgraph's, not the parent's."""
    out = []
    for ns in list(saver.storage.get(CASE_ID, {})):
        out += list(saver.list({"configurable": {"thread_id": CASE_ID, "checkpoint_ns": ns}}))
    return out


def _step_log(saver: InMemorySaver) -> list[dict]:
    entries: list[dict] = []
    for t in _checkpoints(saver):
        for e in (t.checkpoint.get("channel_values") or {}).get("step_log") or []:
            if isinstance(e, dict) and e not in entries:
                entries.append(e)
    return entries


def _artifacts(saver: InMemorySaver) -> dict:
    latest: dict = {}
    for t in _checkpoints(saver):
        a = (t.checkpoint.get("channel_values") or {}).get("artifacts")
        if a and len(a) >= len(latest):
            latest = a
    return latest


def test_wired_10_0_the_blocks_reach_the_response(wired) -> None:
    """10.0 — the four blocks and the grader's warning, through the real graph."""
    body, _ = wired
    for k in ("explanation", "example", "prompt"):
        assert body[k] == REPLY[k], k
    assert body["progress"].startswith("Define · Step"), body["progress"]
    assert body["grader_warning"], "the grader FAILED this turn; its warning must reach the Belt"


def test_wired_6_57_the_computed_step_is_recorded(wired) -> None:
    """6.57 — `define_position` in step_log, the computed step written over the model's."""
    body, saver = wired
    pos = [e for e in _step_log(saver) if e.get("node") == "define_position"]
    assert pos, [e.get("node") for e in _step_log(saver)]
    assert pos[-1]["reply_progress"] == REPLY["progress"]
    assert body["progress"] == pos[-1]["label"]


def test_wired_6_46_the_script_reaches_the_model(wired) -> None:
    """6.46 — `coaching_script` delivered, by the real skills middleware."""
    _, saver = wired
    script = [e for e in _step_log(saver) if e.get("node") == "coaching_script"]
    assert script and script[-1]["delivered"] is True, script


def test_wired_6_33_a_capture_reaches_the_artifacts(wired) -> None:
    """6.33 — the captured value is merged into `artifacts` and checkpointed."""
    _, saver = wired
    assert _artifacts(saver).get("business_case") == BELT
