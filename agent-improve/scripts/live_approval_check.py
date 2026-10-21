"""DEF-170's live proof without a run-through (founder ruling 2026-10-21, item 1): Define's approval against REAL
Azure storage, with zero model calls.

Each path starts from a saved case with all thirteen elements confirmed (scripts/saved_cases/
define_all_confirmed.v8.json, the slices' case) and reaches the report's pause through POST /gate. The
submission's one model call — the rubric's judgment (layer 2d) — is replayed from the recorded run
define_runthrough_20261020T143753, whose gate submission passed with no failed check: every criterion "pass".
Every chat-model call is counted, and the cap is 0: any call fails the run.

  A — approve: both records written once (the Store's gate document, the case record), the phase is Measure;
      a second approval answers 409 and writes nothing.
  B — the case write refused by storage (an HttpResponseError raised once at blob.write_phase_gate): 503 with
      the founder's words, the Store record removed, the case unchanged, the pause still there; the second
      approval writes both records once.

    cd agent-improve; python -m scripts.live_approval_check

The record goes to docs/runthrough/live_approval_<stamp>.json, with the product hash it ran on.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

from scripts.move_proof_661 import CALLS, STORAGE, CapReached, _count_model_calls, _time_storage, storage_since

OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "runthrough"
REPLAYED_FROM = "define_runthrough_20261020T143753 gate_submit: passed, failed_checks [] (every criterion pass)"
ACTOR = "Priya Shah"

#: Every write of Define's gate document — the Store's (put / delete at artifacts/define) and the case's.
WRITES: list[dict[str, Any]] = []


def _count_gate_writes() -> None:
    """The writes this check is about, counted where they reach storage: the Store's batch (a PutOp at
    artifacts/define — a value is a write, None a delete) and blob.write_phase_gate (the case record)."""
    import functools

    from langgraph.store.base import PutOp

    from backend.core.store import AzureBlobStore
    from backend.storage import blob, layout

    def gate_ops(ops: Any) -> list[str]:
        return ["store_delete" if op.value is None else "store_write" for op in ops
                if isinstance(op, PutOp) and op.key == "define" and tuple(op.namespace)[-1:] == (layout.KIND_ARTIFACTS,)]

    real_batch, real_abatch = AzureBlobStore.batch, AzureBlobStore.abatch

    @functools.wraps(real_batch)
    def batch(self: Any, ops: Any) -> Any:
        ops = list(ops)
        WRITES.extend({"kind": k} for k in gate_ops(ops))
        return real_batch(self, ops)

    @functools.wraps(real_abatch)
    async def abatch(self: Any, ops: Any) -> Any:
        ops = list(ops)
        WRITES.extend({"kind": k} for k in gate_ops(ops))
        return await real_abatch(self, ops)
    AzureBlobStore.batch, AzureBlobStore.abatch = batch, abatch  # type: ignore[method-assign]

    real_gate = blob.write_phase_gate

    @functools.wraps(real_gate)
    async def write_phase_gate(**kw: Any) -> Any:
        WRITES.append({"kind": "case_write", "phase": kw.get("phase")})
        return await real_gate(**kw)
    blob.write_phase_gate = write_phase_gate                   # type: ignore[assignment]


def _replay_rubric() -> None:
    """The rubric's judgment, replayed: every criterion "pass", as the recorded submission found."""
    from backend.validation import rubric

    async def recorded(criteria: Any, document: str) -> Any:
        return rubric.GraderVerdict(verdicts=[rubric.CriterionVerdict(criterion=c, status="pass")
                                              for c, _, _ in criteria])
    rubric._llm_verdicts = recorded                            # type: ignore[assignment]


def _writes_since(start: int) -> dict[str, int]:
    out: dict[str, int] = {}
    for w in WRITES[start:]:
        out[w["kind"]] = out.get(w["kind"], 0) + 1
    return out


def _state(client: Any, case_id: str) -> dict[str, Any]:
    from backend.core.store import get_store
    from backend.phases.mappers_common import read_gate_document
    case = client.get(f"/cases/{case_id}").json()
    define = (case.get("phases") or {}).get("define") or {}
    review = client.get(f"/gate/review/{case_id}/define")
    return {"store_record": bool(read_gate_document(get_store(), case_id, "define")),
            "case_gate_passed": bool(define.get("gate_passed")), "current_phase": case.get("current_phase"),
            "awaiting_decision": bool(review.json().get("awaiting_decision")) if review.status_code == 200 else None}


def _decide(client: Any, case_id: str) -> tuple[int, dict[str, Any], dict[str, Any], dict[str, int]]:
    s0, w0 = len(STORAGE), len(WRITES)
    r = client.post("/gate/decision", json={"case_id": case_id, "phase": "define", "decision": "approve",
                                            "actor": ACTOR})
    return r.status_code, r.json(), storage_since(s0), _writes_since(w0)


def _paused_case(client: Any, title: str) -> tuple[str, dict[str, Any]]:
    from scripts.hard_path_scenarios import saved_case
    case_id = saved_case("define_all_confirmed", title)
    r = client.post("/gate", json={"case_id": case_id, "submitted_by": ACTOR, "phase": "define"})
    return case_id, {"http": r.status_code, "awaiting_acceptance": (r.json() or {}).get("awaiting_acceptance"),
                     "failed_checks": (r.json() or {}).get("failed_checks")}


def path_a(client: Any) -> dict[str, Any]:
    case_id, submit = _paused_case(client, "LIVE APPROVAL CHECK A — approved once (DEF-170)")
    before = _state(client, case_id)
    http, body, storage, writes = _decide(client, case_id)
    after = _state(client, case_id)
    http2, _, storage2, writes2 = _decide(client, case_id)
    checks = {
        "the report paused (POST /gate)": submit["http"] == 200 and bool(submit["awaiting_acceptance"]),
        "nothing written before the decision": not before["store_record"] and not before["case_gate_passed"],
        "the approval answered 200": http == 200,
        "the Store record written once": writes.get("store_write") == 1 and not writes.get("store_delete"),
        "the case record written once": writes.get("case_write") == 1,
        "both records exist after it": after["store_record"] and after["case_gate_passed"],
        "the phase is Measure": after["current_phase"] == "measure",
        "a second approval answers 409": http2 == 409,
        "and writes nothing": not writes2,
    }
    return {"kind": "path_a", "case_id": case_id, "passed": all(checks.values()), "checks": checks,
            "submit": submit, "decision": {"http": http, "message": body.get("message"), "storage": storage,
                                           "gate_writes": writes},
            "second": {"http": http2, "storage": storage2, "gate_writes": writes2}, "after": after}


def path_b(client: Any) -> dict[str, Any]:
    from azure.core.exceptions import HttpResponseError

    from backend.core import graph as graph_mod
    from backend.storage import blob
    case_id, submit = _paused_case(client, "LIVE APPROVAL CHECK B — a refused write, then approved (DEF-170)")
    counting = blob.write_phase_gate

    async def refused(**kw: Any) -> Any:
        WRITES.append({"kind": "case_write_refused", "phase": kw.get("phase")})
        raise HttpResponseError(message="This request is not authorized to perform this operation. (simulated 403)")
    blob.write_phase_gate = refused                            # type: ignore[assignment]
    try:
        http, body, storage, writes = _decide(client, case_id)
    finally:
        blob.write_phase_gate = counting                       # type: ignore[assignment]
    mid = _state(client, case_id)
    http2, body2, storage2, writes2 = _decide(client, case_id)
    after = _state(client, case_id)
    checks = {
        "the report paused (POST /gate)": submit["http"] == 200 and bool(submit["awaiting_acceptance"]),
        "the refused write answered 503": http == 503,
        "with the founder's message": body.get("detail") == graph_mod.APPROVAL_FAILED,
        "the Store record was written, then removed": writes.get("store_write") == 1 and writes.get("store_delete") == 1,
        "no Store record after it": not mid["store_record"],
        "the case unchanged": not mid["case_gate_passed"] and mid["current_phase"] == "define",
        "the pause is still there (GET /gate/review)": mid["awaiting_decision"] is True,
        "the second approval answered 200": http2 == 200,
        "it wrote the Store record once": writes2.get("store_write") == 1 and not writes2.get("store_delete"),
        "and the case record once": writes2.get("case_write") == 1,
        "both records exist, the phase is Measure": after["store_record"] and after["case_gate_passed"]
        and after["current_phase"] == "measure",
    }
    return {"kind": "path_b", "case_id": case_id, "passed": all(checks.values()), "checks": checks,
            "submit": submit, "refused": {"http": http, "detail": body.get("detail"), "storage": storage,
                                          "gate_writes": writes},
            "after_refusal": mid,
            "second": {"http": http2, "message": body2.get("message"), "storage": storage2, "gate_writes": writes2},
            "after": after}


def path_c(client: Any) -> dict[str, Any]:
    """G-240 (live run define_runthrough_20261021T105808): a case that carries an upload — the approval writes the
    case record's own upload records and completes; before the fix it answered 503 ("2 validation errors for
    UploadRecord")."""
    import asyncio

    from backend.storage import blob
    from backend.storage.models import UploadRecord
    from scripts.hard_path_scenarios import saved_case
    case_id = saved_case("define_all_confirmed", "LIVE APPROVAL CHECK C — a case with an upload (G-240)")
    upload = UploadRecord(filename="team.csv", blob_path=f"uploads/{case_id}/team.csv", uploaded_by=ACTOR,
                          uploaded_at="2026-10-21T08:00:00+00:00", classification="purpose=Team list · spreadsheet",
                          rows=5, summary="The project team, five people.")

    async def with_upload() -> None:
        case = await blob.load_case(case_id)
        assert case is not None
        case.phases["define"].uploads = [upload]
        await blob.save_case(case)
    asyncio.run(with_upload())
    r = client.post("/gate", json={"case_id": case_id, "submitted_by": ACTOR, "phase": "define"})
    submit = {"http": r.status_code, "awaiting_acceptance": (r.json() or {}).get("awaiting_acceptance")}
    http, body, storage, writes = _decide(client, case_id)
    after = _state(client, case_id)
    stored = client.get(f"/cases/{case_id}").json()
    uploads = [u.get("filename") for u in ((stored.get("phases") or {}).get("define") or {}).get("uploads") or []]
    checks = {
        "the report paused (POST /gate)": submit["http"] == 200 and bool(submit["awaiting_acceptance"]),
        "the approval answered 200": http == 200,
        "both records written once": writes.get("store_write") == 1 and writes.get("case_write") == 1,
        "the case record keeps its upload": uploads == ["team.csv"],
        "both records exist, the phase is Measure": after["store_record"] and after["case_gate_passed"]
        and after["current_phase"] == "measure",
    }
    return {"kind": "path_c", "case_id": case_id, "passed": all(checks.values()), "checks": checks, "submit": submit,
            "decision": {"http": http, "detail": body.get("detail"), "message": body.get("message"),
                         "storage": storage, "gate_writes": writes}, "uploads": uploads, "after": after}


def main() -> int:
    from scripts.define_runthrough import _product_hash, _source_hash, _tracing_off
    _tracing_off()
    _count_model_calls(0)                    # zero model calls: the first one raises CapReached
    _time_storage()
    _count_gate_writes()
    _replay_rubric()
    from fastapi.testclient import TestClient

    from backend.app import app
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    entries: list[dict[str, Any]] = []
    with TestClient(app) as client:
        for path in (path_a, path_b, path_c):
            try:
                entries.append(path(client))
            except CapReached as exc:
                entries.append({"kind": path.__name__, "passed": False, "error": f"a model was called: {exc}"})
    summary = {"kind": "summary", "started": stamp, "source_hash": _source_hash(), "product_hash": _product_hash(),
               "model_calls": len(CALLS), "rubric_replayed_from": REPLAYED_FROM,
               "storage": storage_since(0), "gate_writes": _writes_since(0),
               "passed": all(e.get("passed") for e in entries) and not CALLS}
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    out = OUT_DIR / f"live_approval_{stamp}.json"
    out.write_text(json.dumps([*entries, summary], indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    for e in entries:
        print(f"{e['kind']}: {'PASS' if e.get('passed') else 'FAIL'} {e.get('case_id', '')}")
        for name, ok in (e.get("checks") or {}).items():
            print(f"  {'ok ' if ok else 'NO '} {name}")
        if e.get("error"):
            print("  " + e["error"])
    print(f"model calls: {len(CALLS)} · gate writes: {summary['gate_writes']} · storage: {summary['storage']}")
    print(f"record: {out}")
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
