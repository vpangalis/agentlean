"""R6 — formal acceptance of the Define report, through a graph-level pause.

Founder requirement R6 (`docs/requirements/business.md`, 2026-09-26): *"the Belt
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
from typing import Any, cast

import pytest

from backend.phases.mappers_common import PHASE_ORDER
from azure.core.exceptions import ResourceExistsError, ResourceModifiedError, ResourceNotFoundError
from fastapi.testclient import TestClient
from langchain_core.messages import AIMessage
from langgraph.store.memory import InMemoryStore

from backend.core.checkpointer import AzureBlobCheckpointSaver
from backend.middleware.grader import DMAICGraderMiddleware
from backend.phases import moves
from backend.phases.define.schema import DEFINE_REQUIRED_FOR_GATE_FIELDS
from backend.tests.test_define_report import COMPLETE
from backend.tests.test_wiring import _coach
from backend.validation.schemas import CoachingGraderVerdict

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
    metadata: Any = {"source": "input", "step": -1, "parents": {}}
    cfg = saver.put({"configurable": {"thread_id": "T", "checkpoint_ns": ""}},
                    empty_checkpoint(), metadata, {})
    saver.put_writes(cfg, [("__interrupt__", {"kind": "a"}), ("x", 1)], "task-1")
    saver.put_writes(cfg, [("__interrupt__", {"kind": "b"}), ("x", 2)], "task-1")
    tup = saver.get_tuple({"configurable": {"thread_id": "T", "checkpoint_ns": ""}})
    assert tup is not None
    got = {(t, c): v for t, c, v in tup.pending_writes or []}
    assert got == {("task-1", "__interrupt__"): {"kind": "b"}, ("task-1", "x"): 1}


class _AsyncBlob:
    """ADR-0101 — the aio face of `_Blob`, over the same in-memory blobs: what `azure.storage.blob.aio` offers."""

    def __init__(self, box: "_Container", path: str) -> None:
        self._sync = _Blob(box, path)

    async def upload_blob(self, body: bytes, overwrite: bool = False, etag: str | None = None,
                          match_condition: Any = None) -> None:
        self._sync.upload_blob(body, overwrite=overwrite, if_match=etag if match_condition is not None else None)

    async def download_blob(self) -> Any:
        held = self._sync.download_blob()

        async def readall() -> bytes:
            return held.readall()
        return SimpleNamespace(readall=readall)

    async def get_blob_properties(self) -> Any:
        return self._sync.get_blob_properties()


class _AsyncContainer:
    def __init__(self, box: "_Container") -> None:
        self._box = box
        self.calls = 0

    def get_blob_client(self, path: str) -> _AsyncBlob:
        self.calls += 1
        return _AsyncBlob(self._box, path)

    async def list_blobs(self, name_starts_with: str = "") -> Any:
        for item in self._box.list_blobs(name_starts_with=name_starts_with):
            yield item

    async def close(self) -> None:
        return None


def test_adr_0101_the_async_saver_round_trips_on_the_aio_client() -> None:
    """ADR-0101 decision 2: aput, aput_writes, aget_tuple and alist run on the aio client — never the sync one — with
    the sync methods' semantics: the history written once, `latest.json` by ETag (a concurrent write is retried once,
    then refused), pending writes keyed as the reference saver keys them, the list newest first."""
    import asyncio

    from langgraph.checkpoint.base import empty_checkpoint

    from backend.core.checkpointer import ConcurrentTurnError

    box = _Container()

    class _NoSync:
        def __getattr__(self, name: str) -> Any:
            raise AssertionError(f"the async path used the sync client ({name})")
    aio = _AsyncContainer(box)
    saver = AzureBlobCheckpointSaver(container_client=_NoSync(), async_container_factory=cast(Any, lambda: aio))  # type: ignore[arg-type]
    metadata: Any = {"source": "input", "step": -1, "parents": {}}
    root = {"configurable": {"thread_id": "T", "checkpoint_ns": ""}}

    async def run() -> dict:
        first = empty_checkpoint()
        cfg = await saver.aput(root, first, metadata, {})
        await saver.aput_writes(cfg, [("__interrupt__", {"kind": "a"}), ("x", 1)], "task-1")
        await saver.aput_writes(cfg, [("__interrupt__", {"kind": "b"}), ("x", 2)], "task-1")
        second: Any = {**empty_checkpoint(), "id": "z" + first["id"][1:]}
        await saver.aput(cfg, second, metadata, {})
        got = await saver.aget_tuple(cfg)
        latest = await saver.aget_tuple(root)
        assert got is not None and latest is not None and latest.parent_config is not None
        listed = [t.checkpoint["id"] async for t in saver.alist(root)]
        return {"pending": {(t, c): v for t, c, v in got.pending_writes or []}, "latest": latest.checkpoint["id"],
                "parent": latest.parent_config["configurable"]["checkpoint_id"], "listed": listed,
                "ids": (first["id"], second["id"])}
    out = asyncio.run(run())
    assert out["pending"] == {("task-1", "__interrupt__"): {"kind": "b"}, ("task-1", "x"): 1}, out["pending"]
    assert out["latest"] == out["ids"][1] and out["parent"] == out["ids"][0], out
    assert out["listed"] == [out["ids"][1], out["ids"][0]], out["listed"]
    assert aio.calls > 0

    # latest.json by ETag: a write that lands between the read and the write is retried once, then refused.
    real = aio.get_blob_client
    race_left = [0]

    def meddling(path: str) -> Any:
        blob = real(path)
        if path.endswith("latest.json"):
            async def changed() -> Any:
                held = box.blobs[path]
                if race_left[0] > 0:                                 # someone else writes it meanwhile
                    race_left[0] -= 1
                    box.blobs[path] = (held[0], f'"moved-{race_left[0]}"')
                return SimpleNamespace(etag=held[1])
            blob.get_blob_properties = changed                       # type: ignore[method-assign]
        return blob
    aio.get_blob_client = meddling                                   # type: ignore[method-assign]

    async def put(cid: str) -> None:
        await saver.aput(root, cast(Any, {**empty_checkpoint(), "id": cid}), metadata, {})
    race_left[0] = 1
    asyncio.run(put("zz1"))                                          # one conflict: retried, written
    now = asyncio.run(saver.aget_tuple(root))
    assert race_left[0] == 0 and now is not None and now.checkpoint["id"] == "zz1"
    race_left[0] = 2
    with pytest.raises(ConcurrentTurnError):
        asyncio.run(put("zz2"))                                      # two: refused


def test_adr_0101_a_coaching_turn_writes_no_checkpoint_of_the_inner_agent(env, monkeypatch) -> None:
    """ADR-0101 decision 1: the coach's inner agent is compiled with checkpointer=False. One coaching turn through
    the real graph, persisted by the production saver on its aio path: no checkpoint in an `|executor:` namespace;
    the parent's and the phase subgraph's checkpoints are written, and the turn reloads."""
    from urllib.parse import unquote

    from backend.core import graph as graph_mod

    box = env.holder["saver"]._container
    aio = _AsyncContainer(box)
    env.holder["saver"] = AzureBlobCheckpointSaver(container_client=box, async_container_factory=cast(Any, lambda: aio))  # type: ignore[arg-type]
    graph_mod.get_graph.cache_clear()
    r = env.client.post("/ask", json={"case_id": CASE_ID, "phase": "define", "user": ACTOR,
                                      "message": "Where do we stand?"})
    assert r.status_code == 200, r.text
    names = [unquote(n) for n in box.blobs]
    assert aio.calls > 0, "the turn did not use the aio path"
    assert not [n for n in names if "|executor:" in n], [n for n in names if "|executor:" in n][:3]
    assert any("/ns/define_phase:" in n for n in names) and any(n.startswith(f"checkpoints/{CASE_ID}/") for n in names)
    reloaded = env.client.get(f"/cases/{CASE_ID}")
    assert reloaded.status_code == 200 and reloaded.json()["conversation_history"], reloaded.text


def test_g232_the_run_records_time_every_storage_call(monkeypatch) -> None:
    """G-232 (owner G-220 "Checkpoint weight"): the run scripts time each checkpoint, Store and case-file call,
    and `storage_since` sums a turn's — so a run record says how much of a turn was storage. Timing changes
    nothing the saver does: the checkpoint written through the timed methods reads back."""
    from langgraph.checkpoint.base import empty_checkpoint

    from backend.core.store import AzureBlobStore
    from backend.storage import blob
    from scripts import move_proof_661 as proof

    for owner, names in ((AzureBlobCheckpointSaver, ("put", "put_writes", "get_tuple", "list", "aput", "aput_writes",
                                                     "aget_tuple", "alist")),
                         (AzureBlobStore, ("batch", "abatch")), (blob, ("load_case", "save_case"))):
        for name in names:                      # restored after the test: the timing patches the classes
            monkeypatch.setattr(owner, name, getattr(owner, name))
    monkeypatch.setattr(proof, "STORAGE", [])
    proof._time_storage()
    saver = AzureBlobCheckpointSaver(container_client=_Container())  # type: ignore[arg-type]
    metadata: Any = {"source": "input", "step": -1, "parents": {}}
    start = len(proof.STORAGE)
    cfg = saver.put({"configurable": {"thread_id": "T", "checkpoint_ns": ""}}, empty_checkpoint(), metadata, {})
    saver.put_writes(cfg, [("x", 1)], "task-1")
    assert saver.get_tuple({"configurable": {"thread_id": "T", "checkpoint_ns": ""}}) is not None
    assert len(list(saver.list({"configurable": {"thread_id": "T", "checkpoint_ns": ""}}))) == 1
    got = proof.storage_since(start)
    assert got["calls"] == 4 and got["checkpoint"]["calls"] == 4, got
    assert [c["op"] for c in proof.STORAGE[start:]] == ["put", "put_writes", "get_tuple", "list"]
    assert got["seconds"] >= 0 and set(got) == {"seconds", "calls", "checkpoint"}, got
    # ADR-0101: on the aio client the async methods are what the graph calls — each counted once.
    import asyncio
    aio_saver = AzureBlobCheckpointSaver(container_client=_Container(),  # type: ignore[arg-type]
                                         async_container_factory=cast(Any, lambda: _AsyncContainer(_Container())))
    start = len(proof.STORAGE)
    asyncio.run(aio_saver.aput({"configurable": {"thread_id": "T", "checkpoint_ns": ""}}, empty_checkpoint(),
                               metadata, {}))
    assert [c["op"] for c in proof.STORAGE[start:]] == ["aput"], proof.STORAGE[start:]


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
    saved: list = []                                 # every case-blob write (ADR-0066)

    async def load(_cid: str):
        return case

    async def save(c):
        saved.append(c)
        if c is not case:                            # as the blob does: the next load reads what was saved
            for name in type(c).model_fields:        # (ADR-0087: an undone approval restores the case)
                setattr(case, name, getattr(c, name))

    async def write_phase_gate(**kw: Any):
        # As storage/blob.py::write_phase_gate does: the record passes and the case moves on.
        written.append(kw)
        record = case.phases[kw["phase"]]
        if not record.gate_passed:                   # the approval stamp, on the transition only (DEF-101)
            from datetime import datetime, timezone
            record.submitted_by = kw.get("submitted_by")
            record.submitted_at = datetime.now(timezone.utc).isoformat()
        record.gate_passed = True
        order = list(PHASE_ORDER)
        i = order.index(kw["phase"])
        case.current_phase = order[i + 1] if i + 1 < len(order) else "complete"

    # G-234 (founder 2026-10-19): the case list in memory too — a passed gate clears the escalation, which
    # read the live registry.json before this fake existed.
    from backend.storage.models import CaseRegistry
    registry = {"held": CaseRegistry()}

    async def load_registry():
        return registry["held"].model_copy(deep=True)

    async def save_registry(r):
        registry["held"] = r.model_copy(deep=True)

    monkeypatch.setattr(routes.blob, "storage_configured", lambda: True)
    monkeypatch.setattr(routes.blob, "load_case", load)
    monkeypatch.setattr(routes.blob, "save_case", save)
    monkeypatch.setattr(routes.blob, "write_phase_gate", write_phase_gate)
    monkeypatch.setattr(routes.blob, "load_registry", load_registry)
    monkeypatch.setattr(routes.blob, "save_registry", save_registry)
    monkeypatch.setattr("backend.core.store.get_store", lambda: store)
    monkeypatch.setattr("backend.gateway.routes.get_store", lambda: store)  # the routes' own name (controls review, item 2)
    monkeypatch.setattr(graph_mod, "get_store", lambda: store)
    monkeypatch.setattr(routes, "_mirror_asks", lambda *a, **k: None)
    planner_llm = nodes_common.get_llm
    monkeypatch.setattr(nodes_common, "get_llm",
                        lambda role, **kw: _coach() if role == "coach" else planner_llm(role, **kw))

    async def passing(self, belt: str, coach: str) -> CoachingGraderVerdict:
        return CoachingGraderVerdict(criteria=[])

    monkeypatch.setattr(DMAICGraderMiddleware, "_grade", passing)
    # Layer 2d's judgment half (R7), faked to pass: this file is about the
    # pause; the rubric's own proofs are test_define_rubric.py.
    from backend.validation import rubric

    async def all_pass(criteria, document):
        return rubric.GraderVerdict(verdicts=[
            rubric.CriterionVerdict(criterion=c, status="pass") for c, _, _ in criteria])
    monkeypatch.setattr(rubric, "_llm_verdicts", all_pass)

    def restart() -> None:
        graph_mod.get_graph.cache_clear()
        holder["saver"] = AzureBlobCheckpointSaver(container_client=container)  # type: ignore[arg-type]

    client = TestClient(app)
    yield SimpleNamespace(client=client, case=case, written=written, restart=restart,
                          holder=holder, saved=saved)
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
    # ADR-0066: the re-opened statuses are unfinished work — in the checkpoint, read back
    # through the API's reload, never written to the case blob.
    status = env.client.get(f"/cases/{CASE_ID}").json()["phases"]["define"]["field_status"]
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
    status: dict[str, dict[str, Any]] = {f: {"status": moves.CONFIRMED} for f, _ in moves.positions("define")}
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
        pytest.fail("node is not installed — the controls cannot be rendered; the UI tests need Node.js (audit X5)", pytrace=False)
    src = UI.read_text(encoding="utf-8")
    js = (_fn(src, "escapeHtml") + "\n" + _fn(src, "defineReportActionsHtml")
          + f"\nprocess.stdout.write(defineReportActionsHtml({json.dumps(d)}, "
          f"{json.dumps(rep)}, {json.dumps(passed)}));")
    # The script on stdin, never `-e`: a report (ADR-0093's Gate view) outgrows Windows' 32K command line.
    out = subprocess.run([node], input=js, capture_output=True, text=True, encoding="utf-8")
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


@pytest.mark.degraded_expected
def test_g242_a_failed_assembly_at_approval_writes_nothing_and_answers_503(env, monkeypatch) -> None:
    """G-242 (audit 2026-10-22, A1/W1; founder wave 1, item 1): a gate document that cannot be assembled at approval
    raises — gate_apply never returns an empty `final`, so nothing is written: no Store record, no empty record over
    the case record's values, the phase does not advance; the route answers 503 with the approval message."""
    from backend.core import graph as graph_mod
    from backend.core.store import get_store
    from backend.phases.gate_registry import GATE_SPECS
    from backend.phases.mappers_common import read_gate_document

    _submit(env)
    before = dict(env.case.phases["define"].structured or {})

    def broken(*a, **k):
        raise ValueError("assembly failed")
    monkeypatch.setitem(GATE_SPECS, "define", GATE_SPECS["define"]._replace(assemble=broken))
    r = _decide(env, decision="approve")
    assert r.status_code == 503 and r.json()["detail"] == graph_mod.APPROVAL_FAILED, r.text
    assert env.written == [], env.written
    assert dict(env.case.phases["define"].structured or {}) == before, "the case record's values were overwritten"
    assert env.case.current_phase == "define" and not env.case.phases["define"].gate_passed
    assert not read_gate_document(get_store(), CASE_ID, "define")


def test_g242_the_case_write_refuses_an_empty_approved_record(monkeypatch) -> None:
    """G-242 (audit A1, blob.py): an approval never writes an empty record over the case record's values — the case
    write refuses structured={} before it loads or saves anything."""
    import asyncio

    from backend.storage import blob

    touched: list = []

    async def load(case_id):
        touched.append(case_id)
    monkeypatch.setattr(blob, "load_case", load)
    with pytest.raises(ValueError, match="empty"):
        asyncio.run(blob.write_phase_gate(case_id="C1", phase="define", structured={}, submitted_by="Ana", summary=""))
    assert touched == [], "the case was read for a write that must never happen"


def test_g243_only_a_missing_case_reads_as_not_found(monkeypatch) -> None:
    """G-243 (audit W2; founder wave 1, item 2): load_case answers None only for a case that does not exist; any other
    read error (the network, a corrupt record) raises — so an approval can never take a failed read for "no case" and
    write an empty upload list over the case's own."""
    import asyncio

    from azure.core.exceptions import ResourceNotFoundError, ServiceRequestError

    from backend.storage import blob

    async def missing(path):
        raise ResourceNotFoundError("missing")
    monkeypatch.setattr(blob, "_download", missing)
    assert asyncio.run(blob.load_case("C1")) is None

    async def down(path):
        raise ServiceRequestError("the storage service is not reachable")
    monkeypatch.setattr(blob, "_download", down)
    with pytest.raises(ServiceRequestError):
        asyncio.run(blob.load_case("C1"))

    async def corrupt(path):
        return "{not json"
    monkeypatch.setattr(blob, "_download", corrupt)
    with pytest.raises(ValueError):
        asyncio.run(blob.load_case("C1"))
