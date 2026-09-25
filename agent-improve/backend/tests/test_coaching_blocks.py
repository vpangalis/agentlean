"""Step 10.0 — the coaching turn's output reaches the Belt: four blocks and
the grader's warning.

THE DEFECT, MEASURED
--------------------
Coherence audit, `IMPR-2026-AD5` (2026-09-25, six turns, 0 traces): the Belt
received `CoachingResponse.message` and nothing else. `routes.py` builds
`answer=(reply.content …)` from the last AI message, whose content is
`message`; `explanation`, `example`, `prompt` and `progress` were produced on
every turn and dropped at the route. Turn 1 showed the welcome WITHOUT the
business-case question — the question was in `prompt`. And the grader's
warning (`{"grader_warning": …}` from `after_agent`) was read by nothing
(G-76, G-103).

THE TRANSPORT
-------------
The route never holds the `CoachingResponse` — only the graph's messages. The
seam the product already uses for a turn's extras is the reply message's
`additional_kwargs` (the SIPOC diagram rides there, `_attach_diagram`), and
`core/conversation.py` round-trips named keys into `conversation_history`. So:
the executor puts the four blocks and the warning on the reply message; the
route projects them onto `AskResponse` beside `answer`; the history keeps them
so the UI can rebuild from it (G-79).

These tests drive the REAL executor into the REAL route — the card's *"asserted
against the ROUTE rather than against the schema alone"* — and the UI's own
`renderTurn`, run in node.
"""
from __future__ import annotations

import asyncio
import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any

import pytest
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

from backend.core import conversation
from backend.core.substate import CoachingResponse, PhaseState
from backend.gateway.schemas import AskResponse
from backend.middleware.grader import DMAICGraderMiddleware, MAX_ITERATIONS_WARNING
from backend.phases import nodes_common as _nc
from backend.validation.schemas import CoachingGraderVerdict, CriterionResult

UI = Path(__file__).resolve().parents[2] / "ui" / "index.html"

# Turn 1 of the audit, as the coach drafted it (IMPR-2026-AD5).
REPLY = CoachingResponse(
    message=("Welcome — I'm here to coach you through your improvement project "
             "step by step, so you don't need to be an expert."),
    explanation="Define is the first phase of DMAIC, where we clarify the problem, scope, and goals.",
    example="Phases: Define, Measure, Analyse, Improve, Control — a structured approach to problem-solving.",
    prompt="Let's start with the business case. Why is this project worth doing, and what does it cost the business?",
    progress="Define · Step 1 of 12",
)
BLOCKS = ("explanation", "example", "prompt", "progress")


def _failing() -> CoachingGraderVerdict:
    return CoachingGraderVerdict(criteria=[CriterionResult(
        criterion="Coach must challenge weak inputs with specific follow-up questions",
        status="fail", feedback="ask how the cost was measured")])


class _Agent:
    """The coach reduced to its reply and its after_agent pass: the REAL
    grader the executor mounted runs on the reply, its model call stubbed."""

    def __init__(self, middleware: list[Any], grade: CoachingGraderVerdict | None) -> None:
        self.grader = next(m for m in middleware if isinstance(m, DMAICGraderMiddleware))
        self.grade = grade

    async def ainvoke(self, payload: dict, *_: Any, **__: Any) -> dict:
        messages = [*payload["messages"], AIMessage(content=REPLY.message),
                    ToolMessage(content=f"Returning structured response: {REPLY}",
                                tool_call_id="call_1", name="CoachingResponse")]
        state = {"structured_response": REPLY, "messages": messages}
        if self.grade is not None:
            async def grade(belt: str, coach: str) -> CoachingGraderVerdict:
                return self.grade  # type: ignore[return-value]
            self.grader._grade = grade  # type: ignore[method-assign]
            await self.grader.aafter_agent(state, None)
        return {"messages": messages, "structured_response": REPLY.model_copy()}


def _state() -> PhaseState:
    base: PhaseState = {
        "case_id": "IMPR-TEST-100", "current_phase": "define",
        "messages": [HumanMessage(content="Hi — I'm ready to start Define on our project.")],
        "history": [], "phase_context": "", "coaching_plan": None,
        "field_index": 0, "draft": {}, "artifacts": {}, "step_log": [],
        "field_log": [], "belt_edits": {}, "turn_count": 0, "final": {},
        "gate_attempts": 0, "validator_feedback": [], "rejection_feedback": [],
        "citations": [], "uploads": [], "asks": [], "hop_results": [],
        "synthesis_output": None,
    }
    return base


def _executor_messages(monkeypatch, grade: CoachingGraderVerdict | None) -> list:
    monkeypatch.setattr(_nc, "create_agent", lambda **kw: _Agent(kw["middleware"], grade))
    # The grader stands down when coherence degrades; keep coherence passing.
    from backend.middleware import coherence as _coh

    async def coherent(self, belt: str, coach: str):  # noqa: ANN001
        from backend.validation.schemas import CoherenceResult
        return CoherenceResult(coherent=True, is_conclusive=True, is_parroting=False,
                               on_topic=True, reason="")
    monkeypatch.setattr(_coh.CoherenceMiddleware, "_check", coherent)
    out = asyncio.run(_nc.executor("define", _state()))
    return [*_state()["messages"], *out["messages"]]


# ── the reply message carries the blocks ────────────────────────────────────


def test_the_reply_message_carries_the_four_blocks(monkeypatch, stub_planner) -> None:
    msgs = _executor_messages(monkeypatch, None)
    reply = [m for m in msgs if isinstance(m, AIMessage)][-1]
    blocks = reply.additional_kwargs.get("coaching_blocks")
    assert blocks is not None, f"no coaching_blocks on the reply: {sorted(reply.additional_kwargs)}"
    for k in BLOCKS:
        assert blocks[k] == getattr(REPLY, k), k
    assert reply.content == REPLY.message, "message stays the transcript entry (§50.1)"


def test_a_failed_grade_puts_the_warning_on_the_reply(monkeypatch, stub_planner) -> None:
    reply = [m for m in _executor_messages(monkeypatch, _failing())
             if isinstance(m, AIMessage)][-1]
    assert reply.additional_kwargs.get("grader_warning") == MAX_ITERATIONS_WARNING


def test_a_passed_grade_carries_no_warning(monkeypatch, stub_planner) -> None:
    passed = CoachingGraderVerdict(criteria=[CriterionResult(
        criterion="Coach must stay on the current phase's topic", status="pass", feedback="")])
    reply = [m for m in _executor_messages(monkeypatch, passed) if isinstance(m, AIMessage)][-1]
    assert not reply.additional_kwargs.get("grader_warning")


# ── the ROUTE carries them to the Belt ─────────────────────────────────────


def _ask(monkeypatch, messages: list) -> dict:
    from backend.app import app
    from backend.gateway import routes
    from backend.storage.models import CaseDocument
    case = CaseDocument.new(case_id="IMPR-TEST-100", title="t", belt_level="green",
                            leader="L", department="D", target_date="2027-01-01", team=[])
    saved: list = []

    async def load(_cid: str):
        return case

    async def save(c):
        saved.append(c)

    async def graph_input(*a: Any, **k: Any) -> dict:
        return {}

    async def run_turn(*a: Any, **k: Any) -> dict:
        return {"messages": messages}

    monkeypatch.setattr(routes.blob, "storage_configured", lambda: True)
    monkeypatch.setattr(routes.blob, "load_case", load)
    monkeypatch.setattr(routes.blob, "save_case", save)
    monkeypatch.setattr(routes, "_ensure_case_record", lambda c: None)
    monkeypatch.setattr(routes, "_graph_input", graph_input)
    monkeypatch.setattr(routes, "_run_turn", run_turn)
    monkeypatch.setattr(routes, "_mirror_asks", lambda *a, **k: None)
    monkeypatch.setattr("backend.core.graph.get_graph", lambda phase: object())
    resp = TestClient(app).post("/ask", json={"case_id": "IMPR-TEST-100", "user": "b",
                                              "message": "hi", "phase": "define"})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    body["_saved_history"] = saved[-1].conversation_history if saved else []
    return body


def test_the_response_carries_four_blocks_and_the_warning(monkeypatch, stub_planner) -> None:
    """**The card's Done-when, on the route.** Turn 1's business-case question
    is in the RESPONSE, not only in the checkpoint."""
    body = _ask(monkeypatch, _executor_messages(monkeypatch, _failing()))
    assert body["answer"] == REPLY.message
    for k in BLOCKS:
        assert body.get(k) == getattr(REPLY, k), (k, body.get(k))
    assert "business case" in body["prompt"]
    assert body.get("grader_warning") == MAX_ITERATIONS_WARNING


def test_the_schema_declares_them_defaulted() -> None:
    """A missing block is a finding, never a failed turn (§4.8, v1.64)."""
    fields = AskResponse.model_fields
    for k in (*BLOCKS, "grader_warning"):
        assert k in fields, k
        assert not fields[k].is_required(), k


# ── the history keeps them (G-79) ───────────────────────────────────────────


def test_the_saved_history_keeps_the_blocks(monkeypatch, stub_planner) -> None:
    body = _ask(monkeypatch, _executor_messages(monkeypatch, _failing()))
    ai = [t for t in body["_saved_history"] if t.get("role") == "ai"][-1]
    for k in BLOCKS:
        assert ai.get(k) == getattr(REPLY, k), k
    assert ai.get("grader_warning") == MAX_ITERATIONS_WARNING


def test_a_history_turn_round_trips_the_blocks() -> None:
    msg = AIMessage(content="m", additional_kwargs={
        "coaching_blocks": {k: f"{k}!" for k in BLOCKS}, "grader_warning": "w"})
    turn = conversation.message_to_turn(msg, 0)
    back = conversation.turn_to_message(turn)
    assert back.additional_kwargs.get("coaching_blocks") == {k: f"{k}!" for k in BLOCKS}
    assert back.additional_kwargs.get("grader_warning") == "w"


# ── the UI renders them — renderTurn, run in node ──────────────────────────


def _render_turn(turn: dict) -> str:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed — renderTurn cannot be run; this is NOT a pass")
    src = UI.read_text(encoding="utf-8")
    m = re.search(r"^function renderTurn\(turn\)\{.*?^\}", src, re.M | re.S)
    assert m, "renderTurn not found in ui/index.html"
    helpers = re.search(r"^function escapeHtml\(v\) \{.*?^\}", src, re.M | re.S)
    js = ("const S={user:'Belt'};\n" + (helpers.group(0) if helpers else "") + "\n"
          + m.group(0) + "\nprocess.stdout.write(renderTurn(" + json.dumps(turn) + "));")
    out = subprocess.run([node, "-e", js], capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stderr
    return out.stdout


def _esc(v: str) -> str:
    """The UI's own `escapeHtml`, so the test finds the text as rendered."""
    return (v.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
             .replace('"', "&quot;").replace("'", "&#39;"))


def test_the_ui_renders_one_block_per_field() -> None:
    turn = {"role": "ai", "text": REPLY.message, "citations": [],
            **{k: getattr(REPLY, k) for k in BLOCKS}, "grader_warning": MAX_ITERATIONS_WARNING}
    html = _render_turn(turn)
    for k in BLOCKS:
        assert _esc(getattr(REPLY, k)) in html, f"{k} is not on the screen"
    assert 'class="blk blk-example"' in html, "the example is not visually distinct (B6)"
    assert MAX_ITERATIONS_WARNING.split(" — ")[0][:40] in html
    order = [html.index(_esc(getattr(REPLY, k))) for k in ("explanation", "example", "prompt")]
    assert order == sorted(order), "§50.1 order: explanation, example, prompt"


def test_an_empty_block_renders_as_absent() -> None:
    html = _render_turn({"role": "ai", "text": "m", "citations": [],
                         "explanation": "", "example": "", "prompt": "Ask?", "progress": ""})
    assert "blk-explanation" not in html and "blk-example" not in html
    assert "Ask?" in html


# ── G-79 — a page reload redraws past turns from conversation_history ──────


def _run_js(js: str) -> str:
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed — the UI cannot be run; this is NOT a pass")
    out = subprocess.run([node, "-e", js], capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stderr
    return out.stdout


def _fn(src: str, name: str) -> str:
    m = re.search(r"^(?:async )?function " + name + r"\(.*?^\}", src, re.M | re.S)
    assert m, f"{name} not found in ui/index.html"
    return m.group(0)


def test_a_reload_redraws_past_turns_with_their_blocks() -> None:
    """After a reload `S.localChat` is empty and the case's history is all
    there is: every stored turn is drawn, the AI turn with its blocks."""
    src = UI.read_text(encoding="utf-8")
    history = [{"role": "user", "user": "Belt", "text": "Hi — ready."},
               {"role": "ai", "text": REPLY.message, "citations": [],
                **{k: getattr(REPLY, k) for k in BLOCKS}}]
    js = ("const S={user:'Belt'};\n" + _fn(src, r"escapeHtml") + "\n" + _fn(src, "renderTurn")
          + "\n" + _fn(src, "renderHistoryTurns")
          + f"\nprocess.stdout.write(renderHistoryTurns({json.dumps(history)}, []));")
    html = _run_js(js)
    assert "Hi — ready." in html, "the Belt's past turn is not redrawn"
    assert _esc(REPLY.prompt) in html and 'class="blk blk-example"' in html, \
        "the past AI turn is redrawn without its blocks"


def test_turns_already_on_screen_are_not_drawn_twice() -> None:
    """A tab switch re-appends this session's turns; the history must not
    draw them again after a reload of the case record (the gate tab does one)."""
    src = UI.read_text(encoding="utf-8")
    turn = {"role": "ai", "text": "Only once.", "citations": []}
    js = ("const S={user:'Belt'};\n" + _fn(src, r"escapeHtml") + "\n" + _fn(src, "renderTurn")
          + "\n" + _fn(src, "renderHistoryTurns")
          + f"\nprocess.stdout.write(renderHistoryTurns({json.dumps([turn])}, {json.dumps([turn])}));")
    assert "Only once." not in _run_js(js)


def test_a_returning_case_draws_its_history() -> None:
    """`renderChat`'s returning-case branch is where a reload lands."""
    assert "renderHistoryTurns(" in _fn(UI.read_text(encoding="utf-8"), "renderChat")


def test_the_warning_is_the_founders_text() -> None:
    """Founder, 2026-09-25, verbatim."""
    assert MAX_ITERATIONS_WARNING == (
        "My quality check flagged this reply as weaker than it should be. "
        "If it doesn't help, tell me and I'll try again.")


# ── G-79, the diagram half — founder's manual check, IMPR-2026-8D4:
#    "the 5W2H diagram DISAPPEARS after switching tabs and back" ────────────

_DOM_STUB = """
const calls=[];
const el=()=>({classList:{toggle(){},add(){},remove(){}},scrollTop:0,scrollHeight:0,innerHTML:''});
const document={getElementById:(id)=>el()};
function renderChat(){calls.push('renderChat');}
function loadSessionGreeting(){}
function appendMsgToDOM(h){calls.push('turn');}
function renderTurn(t){return '';}
function renderPhaseNav(){} function renderOverview(){} function renderHistory(){} function renderGate(){}
function renderLiveViz(){calls.push('renderLiveViz');}
"""


def _select_chat(state_js: str) -> list[str]:
    src = UI.read_text(encoding="utf-8")
    js = (_DOM_STUB + state_js + "\n" + _fn(src, "selectTab")
          + "\nselectTab('chat'); process.stdout.write(JSON.stringify(calls));")
    return json.loads(_run_js(js))


def test_switching_back_to_the_chat_tab_redraws_the_diagram() -> None:
    """A tab switch keeps this session's turns in S.localChat; the diagram is
    redrawn after them, not lost."""
    calls = _select_chat("const S={localChat:[{role:'ai',text:'m'}],case:{conversation_history:[]}};")
    assert "renderLiveViz" in calls, f"the diagram is not redrawn on a tab switch: {calls}"
    assert calls.index("renderLiveViz") > max(i for i, c in enumerate(calls) if c == "turn"), \
        "the diagram must follow the re-appended turns, as it does after a send"


def test_opening_the_chat_after_a_reload_redraws_the_diagram() -> None:
    """After a reload S.localChat is empty and S.lastAsk is gone; opening the
    chat tab must still draw the diagram."""
    calls = _select_chat("const S={localChat:[],case:{conversation_history:[{role:'ai',text:'m'}]}};")
    assert "renderLiveViz" in calls, f"the diagram is not redrawn after a reload: {calls}"


def test_after_a_reload_the_diagram_comes_from_the_stored_turn() -> None:
    """S.lastAsk only exists after a send; after a reload the visual the
    server stored on the turn is the source."""
    src = UI.read_text(encoding="utf-8")
    viz = {"type": "mindmap_5w2h", "data": {"problem_summary": "stored"}}
    js = ("const S={lastAsk:null,localChat:[],case:{conversation_history:["
          "{role:'ai',text:'a'},{role:'ai',text:'b',visualisation:" + json.dumps(viz) + "}]}};\n"
          + _fn(src, "lastVizSource") + "\nprocess.stdout.write(JSON.stringify(lastVizSource()));")
    assert json.loads(_run_js(js)).get("visualisation") == viz


def test_a_sent_turn_keeps_its_visual_for_the_next_redraw() -> None:
    """The live turn in S.localChat carries the visual, so a tab switch in the
    same session redraws the same diagram."""
    body = _fn(UI.read_text(encoding="utf-8"), "sendMessage")
    assert "visualisation:resp.visualisation" in body and "sipoc_diagram:resp.sipoc_diagram" in body
