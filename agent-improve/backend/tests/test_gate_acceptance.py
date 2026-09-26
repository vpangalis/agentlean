"""R6 — formal acceptance of the Define report, through a graph-level pause.

Founder requirement R6 (`docs/requirements/define.md`, 2026-09-26): *"the Belt
(with the team) reviews the report and approves or rejects it through a
graph-level pause. On rejection the coach guides the Belt back to the
element(s) to change. Every change is kept in phase state with its date."*

THE PAUSE — `gate_review` calls `interrupt()` once the Define gate has passed
validation; `POST /gate` returns "awaiting acceptance" and writes NOTHING;
`POST /gate/decision` resumes with `Command(resume=...)`.

PROVEN ON THE PRODUCTION SAVER — `AzureBlobCheckpointSaver` over an in-memory
fake of the blob container (every path and ETag it writes, kept in a dict), so
the pause is persisted as the saver persists it: an interrupt and its resume
value are PENDING WRITES, which the saver dropped until R6. The restart test
throws away the compiled graph AND the saver instance between the two requests.
"""
from __future__ import annotations

import asyncio
import itertools
from types import SimpleNamespace
from typing import Any

import pytest
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError, ResourceNotFoundError
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from langgraph.store.memory import InMemoryStore

from backend.core.checkpointer import AzureBlobCheckpointSaver
from backend.middleware.coherence import CoherenceMiddleware
from backend.middleware.grader import DMAICGraderMiddleware
from backend.phases import moves
from backend.phases.define.schema import DEFINE_REQUIRED_FOR_GATE_FIELDS
from backend.tests.test_define_report import COMPLETE
from backend.tests.test_wiring import _coach
from backend.validation.schemas import CoachingGraderVerdict, CoherenceResult

CASE_ID = "IMPR-TEST-R6"
ACTOR = "Priya Shah"


# ── a blob container, in memory, with ETags ────────────────────────────────


class _Blob:
    def __init__(self, box: "_Container", path: str) -> None:
        self._box, self._path = box, path

    def upload_blob(self, body: bytes, overwrite: bool = False, if_match: str | None = None) -> None:
        held = self._box.blobs.get(self._path)
        if held is not None and not overwrite:
            raise ResourceExistsError("exists")
        if if_match is not None and (held is None or held[1] != if_match):
            raise ResourceModifiedError("etag")
        self._box.blobs[self._path] = (bytes(body), f'"{next(self._box.etags)}"')

    def download_blob(self) -> Any:
        held = self._box.blobs.get(self._path)
        if held is None:
            raise ResourceNotFoundError("missing")
        return SimpleNamespace(readall=lambda: held[0])

    def get_blob_properties(self) -> Any:
        held = self._box.blobs.get(self._path)
        if held is None:
            raise ResourceNotFoundError("missing")
        return SimpleNamespace(etag=held[1])


class _Container:
    def __init__(self) -> None:
        self.blobs: dict[str, tuple[bytes, str]] = {}
        self.etags = itertools.count(1)

    def get_blob_client(self, path: str) -> _Blob:
        return _Blob(self, path)

    def list_blobs(self, name_starts_with: str = "") -> list[Any]:
        return [SimpleNamespace(name=p) for p in sorted(self.blobs) if p.startswith(name_starts_with)]


# ── the saver's pending writes ─────────────────────────────────────────────


def test_pending_writes_round_trip_and_the_special_channels_overwrite() -> None:
    """The reference semantics (InMemorySaver.put_writes): a special channel
    (`__interrupt__`, `__resume__`, …) overwrites; any other write keeps its
    first value; `get_tuple` returns them."""
    from langgraph.checkpoint.base import empty_checkpoint
    saver = AzureBlobCheckpointSaver(container_client=_Container())  # type: ignore[arg-type]
    cfg = saver.put({"configurable": {"thread_id": "T", "checkpoint_ns": ""}},
                    empty_checkpoint(), {"source": "input", "step": -1, "parents": {}}, {})
    saver.put_writes(cfg, [("__interrupt__", {"kind": "a"}), ("x", 1)], "task-1")
    saver.put_writes(cfg, [("__interrupt__", {"kind": "b"}), ("x", 2)], "task-1")
    tup = saver.get_tuple({"configurable": {"thread_id": "T", "checkpoint_ns": ""}})
    assert tup is not None
    got = {(t, c): v for t, c, v in tup.pending_writes or []}
    assert got == {("task-1", "__interrupt__"): {"kind": "b"}, ("task-1", "x"): 1}


# ── the route, the graph, the saver ───────────────────────────────────────


@pytest.fixture
def env(monkeypatch, stub_planner):
    """A complete Define case on the real routes and graph, persisted by the
    production saver over the in-memory container. `restart()` throws away the
    compiled graph and the saver instance, keeping only the stored blobs."""
    from backend.app import app
    from backend.core import graph as graph_mod
    from backend.gateway import routes
    from backend.phases import nodes_common
    from backend.storage.models import CaseDocument

    container, store = _Container(), InMemoryStore()
    holder = {"saver": AzureBlobCheckpointSaver(container_client=container)}  # type: ignore[arg-type]
    monkeypatch.setattr(graph_mod, "_persistence", lambda: (holder["saver"], store))
    graph_mod.get_graph.cache_clear()
    case = CaseDocument.new(case_id=CASE_ID, title="R6 proof", belt_level="green",
                            leader=ACTOR, department="Finance", target_date="2027-03-31", team=[])
    record = case.phases["define"]
    record.structured = {k: v for k, v in COMPLETE.items()}
    record.field_status = {f: {"status": moves.CONFIRMED} for f, _ in moves.positions("define")}
    written: list[dict] = []

    async def load(_cid: str):
        return case

    async def save(_c):
        return None

    async def write_phase_gate(**kw: Any):
        written.append(kw)

    monkeypatch.setattr(routes.blob, "storage_configured", lambda: True)
    monkeypatch.setattr(routes.blob, "load_case", load)
    monkeypatch.setattr(routes.blob, "save_case", save)
    monkeypatch.setattr(routes.blob, "write_phase_gate", write_phase_gate)
    monkeypatch.setattr("backend.core.store.get_store", lambda: store)
    monkeypatch.setattr(graph_mod, "get_store", lambda: store)
    monkeypatch.setattr(routes, "_mirror_asks", lambda *a, **k: None)
    planner_llm = nodes_common.get_llm
    monkeypatch.setattr(nodes_common, "get_llm",
                        lambda role, **kw: _coach() if role == "coach" else planner_llm(role, **kw))

    async def coherent(self, belt: str, coach: str) -> CoherenceResult:
        return CoherenceResult(coherent=True, is_conclusive=True, is_parroting=False,
                               on_topic=True, reason="")

    async def passing(self, belt: str, coach: str) -> CoachingGraderVerdict:
        return CoachingGraderVerdict(criteria=[])

    monkeypatch.setattr(CoherenceMiddleware, "_check", coherent)
    monkeypatch.setattr(DMAICGraderMiddleware, "_grade", passing)

    def restart() -> None:
        graph_mod.get_graph.cache_clear()
        holder["saver"] = AzureBlobCheckpointSaver(container_client=container)  # type: ignore[arg-type]

    client = TestClient(app)
    yield SimpleNamespace(client=client, case=case, written=written, restart=restart,
                          holder=holder)
    graph_mod.get_graph.cache_clear()


def _submit(env) -> dict:
    r = env.client.post("/gate", json={"case_id": CASE_ID, "submitted_by": ACTOR, "phase": "define"})
    assert r.status_code == 200, r.text
    return r.json()


def _review(env) -> dict:
    r = env.client.get(f"/gate/review/{CASE_ID}/define")
    assert r.status_code == 200, r.text
    return r.json()


def _decide(env, **body: Any):
    return env.client.post("/gate/decision", json={"case_id": CASE_ID, "phase": "define",
                                                    "actor": ACTOR, **body})


def test_the_complete_fixture_passes_the_gate_list() -> None:
    assert set(DEFINE_REQUIRED_FOR_GATE_FIELDS) <= set(COMPLETE)


def test_a_validated_define_report_pauses_and_nothing_is_written(env) -> None:
    body = _submit(env)
    assert body["awaiting_acceptance"] is True and body["passed"] is True
    assert body["next_phase"] is None
    assert env.written == [], "a gate was written before the team decided"
    assert _review(env)["awaiting_decision"] is True


def test_the_pause_survives_a_restart_and_an_approval_writes_once(env) -> None:
    _submit(env)
    env.restart()                                   # a new process: new graph, new saver
    assert _review(env)["awaiting_decision"] is True, "the pause did not survive the restart"
    r = _decide(env, decision="approve")
    assert r.status_code == 200, r.text
    assert r.json()["next_phase"] == "measure"
    assert len(env.written) == 1, env.written
    assert env.written[0]["submitted_by"] == ACTOR, "until R8 the Belt is recorded as the actor"
    assert ACTOR in env.written[0]["summary"]
    assert set(env.written[0]["structured"]) >= set(DEFINE_REQUIRED_FOR_GATE_FIELDS)
    assert _review(env)["awaiting_decision"] is False


def test_a_rejection_reopens_the_named_elements_and_the_coach_guides_back(env) -> None:
    _submit(env)
    r = _decide(env, decision="reject", elements=["goal_statement", "problem_5w2h"],
                reason="the target is too timid, and the 5W2H misses the second site")
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["reopened"] == ["goal_statement", "problem_statement"], "an inside field maps to its element"
    assert env.written == [], "a rejected report was written"
    status = env.case.phases["define"].field_status
    for element in ("goal_statement", "problem_statement"):
        assert status[element]["status"] == moves.ASKED
        assert "too timid" in status[element]["rejected"]["reason"]
        assert status[element]["rejected"]["actor"] == ACTOR
    assert status["business_case"]["status"] == moves.CONFIRMED, "only the named elements re-open"
    # The coach's turn guides the Belt back to the FIRST re-opened element.
    parent = env.holder["saver"].get_tuple({"configurable": {"thread_id": CASE_ID, "checkpoint_ns": ""}})
    ai = [m for m in parent.checkpoint["channel_values"]["messages"]
          if isinstance(m, AIMessage) and moves.MOVE_RECORD_KEY in m.additional_kwargs]
    record = ai[-1].additional_kwargs[moves.MOVE_RECORD_KEY]
    assert (record["field"], record["move"]) == ("problem_statement", moves.CHALLENGE)
    assert record["judgment"] is None, "no model judged anything — the Belt has not answered"
    assert body["answer"], "the coach's guidance is returned"
    assert _review(env)["awaiting_decision"] is False


def test_a_rejection_names_an_element_and_a_reason(env) -> None:
    _submit(env)
    assert _decide(env, decision="reject", elements=[], reason="no").status_code == 422
    assert _decide(env, decision="reject", elements=["goal_statement"], reason=" ").status_code == 422
    assert _decide(env, decision="reject", elements=["not_a_field"], reason="x").status_code == 422
    assert _review(env)["awaiting_decision"] is True, "a refused decision leaves the pause in place"


def test_there_is_nothing_to_decide_before_a_submission(env) -> None:
    assert _decide(env, decision="approve").status_code == 409
    assert env.written == []


def test_the_rejected_move_carries_the_teams_reason() -> None:
    """The move a rejection makes, in code: a challenge on the first re-opened
    element, showing the Belt's words, with the team's reason — no judgment."""
    status = {f: {"status": moves.CONFIRMED} for f, _ in moves.positions("define")}
    status["goal_statement"] = {"status": moves.ASKED, "answer": "to 8%", "messages": 1,
                                "rejected": {"reason": "too timid"}}

    async def never(*a: Any) -> Any:
        raise AssertionError("a rejection is not an answer — nothing to judge")
    d = asyncio.run(moves.decide("define", dict(COMPLETE), status, "", never, action=moves.REJECTED))
    assert (d["field"], d["move"], d["answer"]) == ("goal_statement", moves.CHALLENGE, "to 8%")
    assert "too timid" in d["reason"]


# ── the screen: the controls under the report, in node ─────────────────────


def _actions(d: dict, rep: dict, passed: bool = False) -> str:
    import json
    import shutil
    import subprocess
    from backend.tests.test_define_report import UI, _fn
    node = shutil.which("node")
    if node is None:
        pytest.skip("node is not installed — the controls cannot be rendered; this is NOT a pass")
    src = UI.read_text(encoding="utf-8")
    js = (_fn(src, "escapeHtml") + "\n" + _fn(src, "defineReportActionsHtml")
          + f"\nprocess.stdout.write(defineReportActionsHtml({json.dumps(d)}, "
          f"{json.dumps(rep)}, {json.dumps(passed)}));")
    out = subprocess.run([node, "-e", js], capture_output=True, text=True, encoding="utf-8")
    assert out.returncode == 0, out.stderr
    return out.stdout


def test_the_screen_offers_approve_and_reject_only_while_paused() -> None:
    from backend.phases.define.report import define_report
    rep = define_report(COMPLETE, {}, [])
    paused = _actions({"awaiting_decision": True}, rep)
    assert "decideDefineReport('approve')" in paused and "decideDefineReport('reject')" in paused
    assert paused.count('class="reject-element"') == 13, "every element can be named"
    assert 'id="reject-reason"' in paused
    ready = _actions({"awaiting_decision": False}, rep)
    assert "submitGateReview()" in ready and "decideDefineReport" not in ready
    assert "disabled" not in ready.split("submitGateReview()")[0][-200:]
    incomplete = _actions({"awaiting_decision": False}, {**rep, "complete": False})
    assert "disabled" in incomplete
    assert _actions({"awaiting_decision": True}, rep, passed=True) == "", "a passed gate is read-only"
