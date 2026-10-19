"""The checks card — procedure step 6.49. Twelve capability rows, one check each.

**CHECKS ONLY.** Nothing in this file changes product code, and a row that goes
red here is the INPUT to clause 5's decision, not a licence to fix it inside
this card.

THE RULE EVERY ROW CHECK FOLLOWS — rows 18-21's
-----------------------------------------------
Each `test_row_NN_*` **reads what the system wrote** on the live Define case
(`CAPABILITY_CASE_ID`, default `IMPR-2026-0E5`) and **constructs no input**.
A seeded version of any of these would be green against a fixture nobody's
runtime produced, which is the escape rows 18-21 were written against.

When there is nothing to read, the row **SKIPS, and the skip says it is NOT a
pass** (Appendix H: a row is green or red, and a check that did not run is
neither). The one exception is row 35: tracing that is not configured is a
product fact about this environment, so it is RED with that reason.

THE ONE TURN
------------
Row 2 needs a turn it watched. With `CAPABILITY_LIVE_TURN=1` the `turn`
fixture drives ONE real `POST /ask` on the case — a real model, real storage,
real tracing — before anything is read. Without it, row 2 skips, and rows 33
and 35 read the most recent turn already on record: they ask a question of
"the turn just run", and the latest turn IS that turn.

HOW EACH CHECK IS SPLIT
-----------------------
A reader (live I/O) and a predicate `_row_NN(evidence) -> list[str]` that
returns the problems found — empty is green. The predicates are what the
mutation proofs at the bottom drive: for a checks card the mutation is on the
CHECK, so each proof hands its predicate the evidence the broken behaviour
would have written — derived from the real evidence where there is some — and
shows it goes red.
"""
from __future__ import annotations

import asyncio
import datetime as dt
import json
import os
import time
from typing import Any
from urllib.parse import unquote

import pytest

CASE_ID = os.environ.get("CAPABILITY_CASE_ID", "IMPR-2026-0E5")

#: Controls review, item 2 (2026-09-30): the explicit network allow — these rows read the live Define case from Azure (Blob, LangSmith) by design — procedure step 6.49.
pytestmark = pytest.mark.enable_socket


#: Row 3 — founder ruling R2 (2026-09-25): the script row reads THE PROOF CASE
#: OF THE STEP THAT LAST CHANGED THE DELIVERED SCRIPT, never the default case —
#: a script change makes every older case's delivery stale by construction,
#: and a live turn on an old case to refresh it proves nothing about the step.
#: Now step 6.61's proof case; the step that next changes the script moves it.
SCRIPT_PROOF_CASE = os.environ.get("CAPABILITY_SCRIPT_CASE_ID", "IMPR-2026-7F1")
#: Rows whose recorded live proof a founder-ruled change has staled, owed a re-proof in the
#: next planned traced run. CONTAINMENT: while listed, a stale-hash mismatch is an expected
#: failure, never a pass. REMOVE the entry when the traced run records a turn with the
#: current SKILL.md — the test then passes on its own.
REPROOF_OWED = {
    "3": "founder ruling 4 (2026-09-27): the Define SKILL.md changed outside its script "
         "section, and again on 2026-09-28 (G-115: two unbuilt tools left its allowed-tools); row 3 is "
         "re-proved in the next planned traced run (docs/harness-progress.md, Plan)",
}
PHASE = "define"
LIVE_TURN = os.environ.get("CAPABILITY_LIVE_TURN") == "1"
#: DEF-064 (founder 2026-10-14): the turn the run-through drove and traced, handed to row 2 as a file —
#: the same fields the `turn` fixture records when it drives one itself.
DRIVEN_TURN = os.environ.get("CAPABILITY_DRIVEN_TURN") or ""

#: What the one live turn says. A question, not an answer: it asks the coach
#: to take stock, so it captures nothing and cannot overwrite what the Belt
#: already gave on this case.
LIVE_TURN_MESSAGE = (
    "Before we go further, can you tell me where my Define charter stands "
    "and what, if anything, you would still push me on?"
)

#: §7's five keys on every `computation_results` row.
COMPUTATION_KEYS = {"tool", "inputs", "result", "turn", "phase"}

#: The LangGraph node name the coach's model call runs under inside the
#: executor's agent, and the prefix middleware hooks are traced with.
MODEL_NODE = "model"
MIDDLEWARE_MARK = "Middleware."

def _degraded() -> set[str]:
    from backend.phases.nodes_common import _CAP_MESSAGE, _TIMEOUT_MESSAGE
    return {_TIMEOUT_MESSAGE.strip(), _CAP_MESSAGE.strip()}


_DEGRADED = _degraded()

NOT_A_PASS = " — this is NOT a pass (Appendix H: a row that did not run is not green)."


# ══════════════════════════════════════════════════════════════════════════
# Readers — live I/O only, no judgement
# ══════════════════════════════════════════════════════════════════════════


def _require_storage(row: int) -> None:
    from backend.storage import blob
    if not blob.storage_configured():
        pytest.skip(f"no storage configured, so row {row} CANNOT BE EVALUATED" + NOT_A_PASS)


#: DEF-064 (founder 2026-10-15): read the case as it stood at this checkpoint — the parent graph's last one
#: before the approval — when the rows are run on a case approved since.
AT_CHECKPOINT = os.environ.get("CAPABILITY_AT_CHECKPOINT") or None


def _load_case():
    """The case as the app reloads it (GET /cases — ADR-0066: the blob, with the unfinished work read
    through the compiled graph from the checkpoint), at `AT_CHECKPOINT` when one is given. The blob alone
    holds no confirmed value of a case still in Define (T13: written only at approval)."""
    from backend.gateway.routes import _with_unfinished_work
    from backend.storage import blob

    async def reloaded():
        case = await blob.load_case(CASE_ID)
        return None if case is None else await _with_unfinished_work(case, at=AT_CHECKPOINT)
    return asyncio.run(reloaded())


def _case_or_skip(row: int):
    _require_storage(row)
    case = _load_case()
    if case is None:
        pytest.skip(f"{CASE_ID} not found — row {row} cannot be evaluated" + NOT_A_PASS)
    if PHASE not in case.phases:
        pytest.skip(f"{CASE_ID} has no define record — row {row} has no subject" + NOT_A_PASS)
    return case


def _checkpointer():
    from backend.core.checkpointer import get_checkpointer
    return get_checkpointer()


def _history(cp, ns: str = "") -> list[dict]:
    """Every checkpoint in one namespace, oldest first, as plain records."""
    cfg = {"configurable": {"thread_id": CASE_ID, "checkpoint_ns": ns}}
    out = []
    for t in cp.list(cfg):
        c = t.checkpoint
        out.append({
            "id": c["id"], "ts": c["ts"],
            "step": (t.metadata or {}).get("step"),
            "source": (t.metadata or {}).get("source"),
            "seen": {k: dict(v) for k, v in (c.get("versions_seen") or {}).items()},
            "values": c.get("channel_values") or {},
        })
    return sorted(out, key=lambda r: r["id"])


def _read_turn(cp) -> dict:
    """The most recent turn, as the checkpointer holds it.

    The parent namespace's last `input` checkpoint starts the turn; every
    checkpoint after it is the turn's. The subgraph namespaces are new each
    turn (the input mapper rebuilds the child), so the turn's are the ones
    whose FIRST checkpoint is at or after the turn's input checkpoint. A
    blob's modified time is only the candidate filter: back-to-back turns
    overlap it. No upper bound: this is the LATEST turn, and a turn that fails
    inside the subgraph has no parent checkpoint after its subgraph's work.
    """
    parent = _history(cp)
    starts = [i for i, r in enumerate(parent) if r["source"] == "input"]
    if not starts:
        return {}
    i = starts[-1]
    t0 = dt.datetime.fromisoformat(parent[i]["ts"])
    t1 = dt.datetime.fromisoformat(parent[-1]["ts"])
    prefix = f"checkpoints/{CASE_ID}/ns/"
    spaces = {}
    for b in cp._container.list_blobs(name_starts_with=prefix):
        if b.name.endswith("/latest.json") and b.last_modified >= t0 - dt.timedelta(seconds=60):
            ns = unquote(b.name[len(prefix):-len("/latest.json")])
            hist = _history(cp, ns)
            if hist and t0 <= dt.datetime.fromisoformat(hist[0]["ts"]):
                spaces[ns] = hist
    return {
        "prior": parent[i - 1] if i else None,
        "parent": parent[i:],
        "spaces": dict(sorted(spaces.items())),
        "t0": t0,
        "t1": max([t1, *(dt.datetime.fromisoformat(h[-1]["ts"]) for h in spaces.values())]),
    }


def _subgraph_ns(turn: dict) -> str | None:
    subs = [ns for ns in turn.get("spaces", {}) if "|" not in ns]
    return subs[0] if len(subs) == 1 else None


def _turn_final(turn: dict) -> dict:
    """The define subgraph's final state for the turn."""
    ns = _subgraph_ns(turn)
    return turn["spaces"][ns][-1]["values"] if ns else {}


def _turn_step_log(turn: dict) -> list[dict]:
    return [e for e in (_turn_final(turn).get("step_log") or []) if isinstance(e, dict)]


def _all_subgraph_finals(cp, case_id: str = CASE_ID) -> list[dict]:
    """Every recorded define turn's final subgraph state, oldest first."""
    prefix = f"checkpoints/{case_id}/ns/"
    finals = []
    for b in cp._container.list_blobs(name_starts_with=prefix):
        if not b.name.endswith("/latest.json"):
            continue
        ns = unquote(b.name[len(prefix):-len("/latest.json")])
        if "|" in ns or not ns.startswith(PHASE):
            continue
        t = cp.get_tuple({"configurable": {"thread_id": case_id, "checkpoint_ns": ns}})
        if t is not None:
            finals.append({"ts": t.checkpoint["ts"], "ns": ns,
                           "values": t.checkpoint.get("channel_values") or {}})
    return sorted(finals, key=lambda f: f["ts"])


def _langsmith():
    """A LangSmith client and project, or the reason there is none."""
    from backend.core.config import settings
    key = (settings.LANGCHAIN_API_KEY or "").strip()
    if not key:
        return None, None, "no LANGSMITH_API_KEY / LANGCHAIN_API_KEY in this environment"
    from langsmith import Client
    return Client(api_key=key), settings.LANGCHAIN_PROJECT, None


def _thread_filter() -> str:
    return (f'and(eq(metadata_key, "thread_id"), '
            f'eq(metadata_value, "{CASE_ID}"))')


# ══════════════════════════════════════════════════════════════════════════
# The one turn
# ══════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def turn():
    """The turn rows 2, 13, 33 and 35 read. Driven here when opted in."""
    _require_storage(2)
    driven = None
    if LIVE_TURN:
        from fastapi.testclient import TestClient
        from backend.app import app
        case = _load_case()
        if case is None:
            pytest.skip(f"{CASE_ID} not found — no turn can be driven" + NOT_A_PASS)
        before = [r for r in _history(_checkpointer()) if r["source"] == "input"]
        started = dt.datetime.now(dt.timezone.utc)
        with TestClient(app) as client:
            resp = client.post("/ask", json={
                "case_id": CASE_ID, "phase": case.current_phase,
                "message": LIVE_TURN_MESSAGE, "user": "capability-check-6.49",
            })
        driven = {"status": resp.status_code, "body": resp.json() if resp.content else {},
                  "inputs_before": len(before), "started": started}
    cp = _checkpointer()
    record = _read_turn(cp)
    if driven is not None:
        driven["inputs_after"] = len([r for r in _history(cp) if r["source"] == "input"])
    elif DRIVEN_TURN:
        driven = json.loads(open(DRIVEN_TURN, encoding="utf-8").read())
    return {"driven": driven, "record": record}


# ══════════════════════════════════════════════════════════════════════════
# Predicates — judgement only, no I/O. Each returns the problems; [] is green.
# ══════════════════════════════════════════════════════════════════════════


def _row_1(registry: list[dict], status: int, opened: dict) -> list[str]:
    problems = []
    if not any(e.get("case_id") == CASE_ID for e in registry):
        problems.append(f"the case list ({len(registry)} entries) does not return {CASE_ID}")
    if status != 200:
        problems.append(f"GET /cases/{CASE_ID} answered {status}, not 200")
    elif opened.get("case_id") != CASE_ID:
        problems.append(f"GET /cases/{CASE_ID} opened {opened.get('case_id')!r}")
    return problems


def _row_2(driven: dict) -> list[str]:
    problems = []
    if driven["status"] != 200:
        problems.append(f"POST /ask answered {driven['status']}: {str(driven['body'])[:300]}")
    answer = driven["body"].get("answer") if isinstance(driven["body"], dict) else None
    if not (isinstance(answer, str) and answer.strip()):
        problems.append(f"no coached message came back (answer={answer!r})")
    elif answer.strip() in _DEGRADED:
        # 6.52: a 200 carrying the node's own out-of-time or out-of-steps
        # message is the budget working, not the coach answering.
        problems.append("the reply is the degraded out-of-budget message, not a coached one")
    runs = driven["inputs_after"] - driven["inputs_before"]
    if runs != 1:
        problems.append(f"one POST started {runs} graph run(s) — the parent namespace "
                        f"gained {runs} `input` checkpoint(s), not 1")
    return problems


def _latest(entries: list[dict]) -> dict[str, dict]:
    last: dict[str, dict] = {}
    for e in entries:
        f = e.get("field")
        if f and (f not in last or (e.get("turn") or 0) >= (last[f].get("turn") or 0)):
            last[f] = e
    return last


def _same(a: Any, b: Any) -> bool:
    """Equal values. ADR-0071 (DEF-076): a MetricValue migrated from text (state schema version 2)
    holds that text as `raw`, and a field-log entry written before it holds the text itself —
    the same captured value."""
    if isinstance(a, dict) and "raw" in a and "value" in a and isinstance(b, str):
        return a["raw"] == b
    return json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)


def _row_5(field_log: list[dict], structured: dict) -> list[str]:
    """Every field ever captured is still held, at the value last captured."""
    problems = []
    for field, entry in sorted(_latest(field_log).items()):
        if entry.get("value") in (None, "", [], {}):
            continue
        if field not in structured:
            problems.append(f"{field} was captured at turn {entry.get('turn')} and is GONE "
                            "from the case record")
        elif not _same(structured[field], entry["value"]):
            problems.append(f"{field} holds a value other than the one captured at turn "
                            f"{entry.get('turn')}")
    return problems


def _row_6(field_log: list[dict]) -> list[str]:
    """Each correction is dated and keeps the value it replaced, readable."""
    problems = []
    by_field: dict[str, list[dict]] = {}
    for e in sorted(field_log, key=lambda e: (e.get("turn") or 0)):
        by_field.setdefault(str(e.get("field")), []).append(e)
    for field, entries in sorted(by_field.items()):
        for earlier, later in zip(entries, entries[1:]):
            where = f"{field} turn {earlier.get('turn')} -> {later.get('turn')}"
            if not later.get("timestamp"):
                problems.append(f"{where}: the correction carries no date")
            if later.get("prior_value") in (None, ""):
                problems.append(f"{where}: the correction kept no prior value")
            elif not _same(later["prior_value"], earlier.get("value")):
                problems.append(f"{where}: the prior value recorded is not the value it replaced")
    return problems


def _row_8(evidence: list[dict]) -> list[str]:
    """`evidence`: one record per EVIDENCE upload — blob found, index doc found."""
    problems = []
    for u in evidence:
        if not u["blob_exists"]:
            problems.append(f"{u['filename']}: no blob at {u['blob_path']}")
        if not u["index_id"]:
            problems.append(f"{u['filename']}: evidence upload was never indexed "
                            "(no evidence_index_id)")
        elif not u["index_doc"]:
            problems.append(f"{u['filename']}: evidence_index_id {u['index_id']} is not "
                            "in the evidence index")
    return problems


def _row_10(rows: list[dict]) -> list[str]:
    problems = []
    for r in rows:
        keys = set(r) if isinstance(r, dict) else set()
        if keys != COMPUTATION_KEYS:
            problems.append(f"a computation row carries {sorted(keys)}, not "
                            f"{sorted(COMPUTATION_KEYS)}")
    return problems


def _row_11(metrics: list[dict], structured: dict) -> list[str]:
    if not metrics:
        return ["the assembled gate document carries no phase_metrics entry"]
    primary = metrics[0]
    problems = []
    for key in ("baseline_estimate", "target_value"):
        if not _same(primary.get(key), structured.get(key)):
            problems.append(f"phase_metrics[0].{key} = {primary.get(key)!r}, but the case "
                            f"holds {structured.get(key)!r}")
    return problems


def _row_13(step_log: list[dict]) -> list[str]:
    ran = any(e.get("node") == "executor" for e in step_log)
    graded = [e for e in step_log if e.get("layer") == "coaching_grader"]
    if ran and not graded:
        return [f"the coach ran this turn and the coaching rubric left no score — "
                f"{len(step_log)} step_log entries, none with layer 'coaching_grader' "
                f"(nodes: {sorted({str(e.get('node')) for e in step_log})})"]
    return []


def _row_17(feedback: list[dict], required: set[str]) -> list[str]:
    problems = []
    for v in feedback:
        missing = set(v.get("missing") or [])
        if missing and v.get("passed"):
            problems.append(f"layer 2b PASSED a case missing {sorted(missing)}")
        if missing - required:
            problems.append(f"layer 2b named fields that are not required: "
                            f"{sorted(missing - required)}")
    return problems


def _nodes_recorded(history: list[dict]) -> set[str]:
    """Nodes whose completion a checkpoint in this history records."""
    seen: set[str] = set()
    for a, b in zip(history, history[1:]):
        for node, versions in b["seen"].items():
            if a["seen"].get(node) != versions:
                seen.add(node)
    return seen


def _row_33(turn: dict, expected_nodes: set[str]) -> list[str]:
    """One checkpoint per superstep, in every namespace the turn touched, and
    one recording each node the turn ran.
    """
    problems = []
    parent, prior = turn["parent"], turn["prior"]
    steps = [r["step"] for r in parent]
    if prior is not None and steps and steps[0] != prior["step"] + 1:
        problems.append(f"parent: the turn's first checkpoint is step {steps[0]}, the one "
                        f"before it step {prior['step']} — a superstep went unwritten")
    for ns, hist in [("(parent)", parent), *turn["spaces"].items()]:
        s = [r["step"] for r in hist]
        gaps = [(x, y) for x, y in zip(s, s[1:]) if y != x + 1]
        if gaps:
            problems.append(f"{ns[:60]}: steps {s} — no checkpoint for the superstep(s) "
                            f"between {gaps}")
    sub = _subgraph_ns(turn)
    if sub is None:
        problems.append(f"expected one define subgraph namespace for the turn, found "
                        f"{[ns for ns in turn['spaces'] if '|' not in ns]}")
    else:
        unrecorded = expected_nodes - _nodes_recorded(turn["spaces"][sub])
        if unrecorded:
            problems.append(f"nodes that ran with no checkpoint recording them: {sorted(unrecorded)}")
    # The parent's define_phase node COMPLETES only when the subgraph reaches
    # its last node; a turn that failed inside the subgraph never completed it,
    # and owes no checkpoint for a node that did not finish.
    if "gate_apply" in expected_nodes:
        chain = [turn["prior"], *parent] if turn["prior"] else parent
        if "define_phase" not in _nodes_recorded(chain):
            problems.append("parent: no checkpoint records the define_phase node completing")
    return problems


def _row_35(runs: list[dict] | None, tools_called: set[str], reason: str | None) -> list[str]:
    """`runs`: the turn's trace, each {name, type, node, tools, status}."""
    if reason:
        return [f"no trace can exist: {reason}"]
    if not runs:
        return ["the turn left NO LangSmith trace"]
    problems = []
    model = [r for r in runs if r["type"] == "llm" and r["node"] == MODEL_NODE]
    if not model:
        problems.append("the trace shows no model call at the coach's model node")
    elif not any(r["tools"] for r in model):
        problems.append("the coach's model call is traced without the tools bound to it")
    if not any(MIDDLEWARE_MARK in r["name"] for r in runs):
        problems.append("no middleware hook is visible in the trace")
    traced_tools = {r["name"] for r in runs if r["type"] == "tool"}
    if tools_called - traced_tools:
        problems.append(f"tools the turn called are missing from the trace: "
                        f"{sorted(tools_called - traced_tools)}")
    return problems


# ══════════════════════════════════════════════════════════════════════════
# THE ROW CHECKS — each reads what the system wrote
# ══════════════════════════════════════════════════════════════════════════


def test_row_1_a_case_can_be_created_and_opened() -> None:
    """**Row 1.** The case list returns the case, and it opens."""
    _case_or_skip(1)
    from fastapi.testclient import TestClient
    from backend.app import app
    with TestClient(app) as client:
        registry = client.get("/registry")
        opened = client.get(f"/cases/{CASE_ID}")
    assert registry.status_code == 200, f"GET /registry answered {registry.status_code}"
    problems = _row_1(registry.json(), opened.status_code,
                      opened.json() if opened.status_code == 200 else {})
    assert not problems, "; ".join(problems)


def test_row_2_a_turn_returns_a_coached_reply(turn) -> None:
    """**Row 2.** One POST, one graph run, a message back.

    Opt-in (`CAPABILITY_LIVE_TURN=1`): a turn costs a model call and writes to
    the case. **RED on its last two runs, 2026-09-24** — both turns hit the
    executor's 45 s run timeout. Trace `01a0d215-a216-75e2-ba80-1c80597f891f`:
    the grader failed the reply twice and was re-judging the same text.
    Trace `01a0d28e-d4da-7901-a75e-44d86b102098`: three knowledge lookups in a
    row took about 32 s (12.2 + 9.8 + 10.4). The executor soft budget
    (nodes_common.py:647) did not end either turn before the 45 s limit.
    """
    if turn["driven"] is None:
        pytest.skip("row 2 watches a turn it drove; set CAPABILITY_LIVE_TURN=1" + NOT_A_PASS)
    problems = _row_2(turn["driven"])
    assert not problems, "; ".join(problems)


def _row_3(step_log: list[dict], expected_sha: str) -> list[str]:
    entries = [e for e in step_log if e.get("node") == "coaching_script"]
    if not entries:
        return ["the turn left no coaching_script record — whether it had its script is unknowable"]
    e = entries[0]
    problems = []
    if not e.get("delivered"):
        problems.append(f"the turn's model calls went out WITHOUT the script ({e.get('script')})")
    if e.get("sha256") != expected_sha:
        problems.append(f"the delivered script hash {e.get('sha256')} is not today's SKILL.md ({expected_sha})")
    return problems


def test_row_3_the_coach_follows_the_define_script(turn) -> None:
    """**Row 3.** The latest turn the coach COMPLETED records that the Define
    script reached the model — delivered, and the hash of today's SKILL.md."""
    from backend.middleware.skills import script_record
    finals = [f for f in _all_subgraph_finals(_checkpointer(), SCRIPT_PROOF_CASE)
              if any(isinstance(e, dict) and e.get("node") == "executor"
                     and e.get("status") in ("coached", "coached_no_retrieval")
                     for e in (f["values"].get("step_log") or []))]
    if not finals:
        pytest.skip(f"no coaching turn on {SCRIPT_PROOF_CASE} completed" + NOT_A_PASS)
    log = [e for e in (finals[-1]["values"].get("step_log") or []) if isinstance(e, dict)]
    problems = _row_3(log, script_record(PHASE)["sha256"])
    if problems and "3" in REPROOF_OWED and all("is not today's SKILL.md" in p for p in problems):
        pytest.xfail("re-proof owed — " + REPROOF_OWED["3"] + " · " + "; ".join(problems))
    assert not problems, "; ".join(problems)


def test_row_5_a_captured_field_survives_the_next_turn() -> None:
    """**Row 5.** Read from `field_log` against `structured`."""
    case = _case_or_skip(5)
    record = case.phases[PHASE]
    log = list(record.field_log or [])
    turns = {e.get("turn") for e in log}
    if len(turns) < 2:
        pytest.skip(f"{CASE_ID} has captures from {len(turns)} turn(s); survival needs a "
                    "later turn" + NOT_A_PASS)
    problems = _row_5(log, dict(record.structured or {}))
    assert not problems, "; ".join(problems)


def test_row_6_every_change_is_kept_dated_with_its_prior_value() -> None:
    """**Row 6.** Every correction on record keeps both values, dated."""
    case = _case_or_skip(6)
    log = list(case.phases[PHASE].field_log or [])
    fields = [e.get("field") for e in log]
    if len(fields) == len(set(fields)):
        pytest.skip(f"no field on {CASE_ID} was ever corrected" + NOT_A_PASS)
    problems = _row_6(log)
    assert not problems, "; ".join(problems)


def test_row_8_the_belt_can_upload_evidence() -> None:
    """**Row 8.** Each EVIDENCE upload landed in storage and is in the index.

    Artefacts (a to-be map, a draft plan) are deliberately NOT indexed — ruling
    3 in `upload_file` — so they are not this row's subject.
    """
    case = _case_or_skip(8)
    from backend.upload.classifier import EVIDENCE
    uploads = [u for u in case.phases[PHASE].uploads if (u.kind or EVIDENCE) == EVIDENCE]
    if not uploads:
        pytest.skip(f"{CASE_ID} has no evidence upload" + NOT_A_PASS)
    from azure.core.credentials import AzureKeyCredential
    from azure.search.documents import SearchClient
    from backend.core.config import settings
    from backend.storage import blob

    async def exists(path: str) -> bool:
        return await blob._container().get_blob_client(path).exists()

    search = SearchClient(endpoint=settings.AZURE_SEARCH_ENDPOINT,
                          index_name=settings.AZURE_SEARCH_IMPROVE_EVIDENCE_INDEX,
                          credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY))
    evidence = []
    for u in uploads:
        doc = None
        if u.evidence_index_id:
            try:
                doc = search.get_document(key=u.evidence_index_id)
            except Exception:  # noqa: BLE001 — not found is the finding
                doc = None
        evidence.append({"filename": u.filename, "blob_path": u.blob_path,
                         "blob_exists": asyncio.run(exists(u.blob_path)),
                         "index_id": u.evidence_index_id, "index_doc": doc})
    problems = _row_8(evidence)
    assert not problems, "; ".join(problems)


def test_row_10_calculations_are_recorded() -> None:
    """**Row 10.** Every `computation_results` row on record has §7's five keys."""
    _case_or_skip(10)
    rows = [r for f in _all_subgraph_finals(_checkpointer())
            for r in ((f["values"].get("artifacts") or {}).get("computation_results") or [])]
    if not rows:
        pytest.skip(f"no calculation turn yet on {CASE_ID.removeprefix('IMPR-2026-')} — no "
                    "turn's artifacts carry a computation_results row" + NOT_A_PASS)
    problems = _row_10(rows)
    assert not problems, "; ".join(problems)


def test_row_11_the_metric_entry_mirrors_the_primary_scalars() -> None:
    """**Row 11.** The assembled gate document's metric entry equals the two
    scalars the Belt gave. Row 25 is the other half: whether they are usable.
    """
    case = _case_or_skip(11)
    from backend.phases.gate_registry import GATE_SPECS
    structured = dict(case.phases[PHASE].structured or {})
    missing = [f for f in GATE_SPECS[PHASE].tier_1 if f not in structured]
    if missing:
        pytest.skip(f"{CASE_ID} is missing {missing}; no gate document assembles" + NOT_A_PASS)
    doc = GATE_SPECS[PHASE].assemble(structured, [], [], [])
    problems = _row_11(list(getattr(doc, "phase_metrics", None) or []), structured)
    assert not problems, "; ".join(problems)


@pytest.mark.xfail(strict=True, reason=(
    "RED — layer 2a rejects and never re-asks. Until 6.52 B2 it re-checked the SAME "
    "reply up to three times (10 of 10 rejecting turns on IMPR-2026-0E5, no model "
    "call after the rejection); since B2 it checks once and degrades. A fresh "
    "reply on reject is step 6.53, gated on G-83. Bug in stories.py, S40."))
def _row_12_challenges(step_logs: list[list[dict]]) -> tuple[list[dict], list[str]]:
    """Row 12, re-pointed (founder 2026-10-14; ADR-0083's note): the planner's challenges of an answer it
    judged insufficient, and the problems — a challenge that names no failed criterion, or one that is not
    the element's own."""
    from backend.middleware.skills import acceptance_criteria
    found, problems = [], []
    for log in step_logs:
        for e in log:
            j = e.get("judgment") if isinstance(e, dict) and e.get("node") == "planner" else None
            if not (isinstance(j, dict) and e.get("move") == "challenge" and j.get("verdict") == "insufficient"):
                continue
            found.append(e)
            ids = [cid for cid, _ in acceptance_criteria(PHASE, str(e.get("focus_field") or ""))]
            crit = str(j.get("failed_criterion") or "")
            if not crit:
                problems.append(f"{e.get('key')}: the challenge of {e.get('focus_field')} names no failed criterion")
            elif ids and crit not in ids:
                problems.append(f"{e.get('key')}: {crit!r} is not one of {e.get('focus_field')}'s criteria {ids}")
    return found, problems


def test_row_12_vague_answers_are_caught_inside_the_turn() -> None:
    """**Row 12**, re-pointed from layer 2a (retired, ADR-0083) to the planner's judgment (founder ruling
    2026-10-14): a vague answer is caught inside its turn — the planner judges it insufficient, the move is
    a challenge, and the challenge names the element's failed criterion. Read from the case's step_log."""
    _require_storage(12)
    logs = [[e for e in (f["values"].get("step_log") or []) if isinstance(e, dict)]
            for f in _all_subgraph_finals(_checkpointer())]
    found, problems = _row_12_challenges(logs)
    if not found:
        pytest.skip(f"no answer on {CASE_ID} was ever judged insufficient and challenged" + NOT_A_PASS)
    assert not problems, "; ".join(problems)


def test_row_13_the_coaching_rubric_scores_the_turn(turn) -> None:
    """**Row 13.** The latest turn the coach COMPLETED carries the grader's
    score in its `step_log`. A turn that failed inside the executor wrote no
    `step_log` at all, so it cannot answer this row either way.
    """
    # COMPLETED means the coach's own loop finished: a `partial_timeout` or
    # `partial_cap_reached` turn was cut before its after_agent hooks could
    # settle, so it answers nothing about whether grading happens.
    finals = [f for f in _all_subgraph_finals(_checkpointer())
              if any(isinstance(e, dict) and e.get("node") == "executor"
                     and e.get("status") in ("coached", "coached_no_retrieval")
                     for e in (f["values"].get("step_log") or []))]
    if not finals:
        pytest.skip(f"no coaching turn on {SCRIPT_PROOF_CASE} completed" + NOT_A_PASS)
    log = [e for e in (finals[-1]["values"].get("step_log") or []) if isinstance(e, dict)]
    problems = _row_13(log)
    assert not problems, "; ".join(problems)


def test_row_17_required_fields_are_checked_before_the_gate() -> None:
    """**Row 17.** Every layer-2b verdict on record refused a case with a
    required field missing, and named only required fields.
    """
    _case_or_skip(17)
    from backend.phases.gate_registry import GATE_SPECS
    feedback = [v for f in _all_subgraph_finals(_checkpointer())
                for v in (f["values"].get("validator_feedback") or [])
                if isinstance(v, dict) and v.get("layer") == "2b"]
    if not any(v.get("missing") for v in feedback):
        pytest.skip(f"no gate was ever submitted on {CASE_ID} with a field missing"
                    + NOT_A_PASS)
    problems = _row_17(feedback, set(GATE_SPECS[PHASE].tier_1))
    assert not problems, "; ".join(problems)


def test_row_33_a_checkpoint_is_written_after_every_node(turn) -> None:
    """**Row 33.** Read from the blob checkpointer, for the turn just run."""
    record = turn["record"]
    if not record:
        pytest.skip(f"{CASE_ID} has no recorded turn" + NOT_A_PASS)
    # Graph nodes only: `step_log` also carries entries that are not nodes —
    # the grader's verdict (`coaching_grader`, 6.52) — and a checkpoint is
    # owed per NODE, not per audit record.
    from backend.phases.nodes_common import NODE_NAMES
    expected = {str(e["node"]) for e in _turn_step_log(record)
                if e.get("node") in NODE_NAMES}
    problems = _row_33(record, expected)
    assert not problems, "; ".join(problems)


def test_row_35_every_define_turn_leaves_a_langsmith_trace(turn) -> None:
    """**Row 35.** The turn's trace, read through the LangSmith API."""
    record = turn["record"]
    if not record:
        pytest.skip(f"{CASE_ID} has no recorded turn" + NOT_A_PASS)
    if not any("|" in ns for ns in record["spaces"]):
        pytest.skip("the latest turn never reached the coach (no executor ran), so it "
                    "made no model call to trace" + NOT_A_PASS)
    if _trace_aged_out(record["t0"]):
        pytest.skip(f"{CASE_ID}'s latest turn ({record['t0']:%Y-%m-%d}) is older than LangSmith's "
                    f"{TRACE_RETENTION_DAYS}-day trace retention, so its trace no longer exists to read; "
                    "a traced live turn re-proves the row (G-152)" + NOT_A_PASS)
    called = _tools_called(record)
    client, project, reason = _langsmith()
    runs = None
    if not reason:
        runs = _trace_for(client, project, record)
    problems = _row_35(runs, called, reason)
    assert not problems, "; ".join(problems)


#: G-152 — LangSmith keeps a base-tier trace 14 days; an older turn's trace is gone, not missing.
TRACE_RETENTION_DAYS = 14


def _trace_aged_out(t0: dt.datetime, now: dt.datetime | None = None) -> bool:
    """G-152: row 35 reads a recorded turn's trace; past the retention it cannot exist, and its
    absence then says nothing about the code — the row skips (NOT a pass) instead of failing."""
    now = now or dt.datetime.now(dt.timezone.utc)
    stamp = t0 if t0.tzinfo else t0.replace(tzinfo=dt.timezone.utc)
    return now - stamp > dt.timedelta(days=TRACE_RETENTION_DAYS)


def test_g152_a_trace_past_retention_is_not_read_as_missing() -> None:
    """G-152's control: the retention cut-off, tested without the network."""
    now = dt.datetime(2026, 10, 11, tzinfo=dt.timezone.utc)
    assert _trace_aged_out(dt.datetime(2026, 9, 24, tzinfo=dt.timezone.utc), now)
    assert not _trace_aged_out(dt.datetime(2026, 10, 1, tzinfo=dt.timezone.utc), now)
    assert _trace_aged_out(dt.datetime(2026, 9, 1), now), "a naive stamp is read as UTC"


def _tools_called(record: dict) -> set[str]:
    """Tools THIS turn called: ToolMessages after the Belt's message.

    The executor's state is seeded with the whole conversation, so its final
    messages carry every earlier turn's tool calls too; the turn begins at the
    last HumanMessage. That boundary also keeps the read the node dispatches
    BEFORE the agent runs (§17 option C), which is this turn's and is traced.
    The structured-response wrapper comes back as a ToolMessage named after
    the schema; it is the reply's shape, not a tool the coach reached for.
    """
    from langchain_core.messages import HumanMessage, ToolMessage
    from backend.core.substate import CoachingResponse
    called = set()
    for ns, hist in record["spaces"].items():
        if "|" not in ns:
            continue
        msgs = list(hist[-1]["values"].get("messages") or [])
        starts = [i for i, m in enumerate(msgs) if isinstance(m, HumanMessage)]
        for m in msgs[(starts[-1] + 1) if starts else 0:]:
            if isinstance(m, ToolMessage) and m.name:
                called.add(m.name)
    return called - {CoachingResponse.__name__}


def _trace_for(client, project: str, record: dict) -> list[dict]:
    """The root run for this turn, polled while LangSmith ingests it."""
    lo = record["t0"] - dt.timedelta(seconds=15)
    hi = record["t1"] + dt.timedelta(seconds=5)
    for _ in range(12):
        roots = [r for r in client.list_runs(project_name=project, is_root=True,
                                             filter=_thread_filter(), start_time=lo)
                 if r.start_time and lo <= r.start_time.replace(tzinfo=dt.timezone.utc) <= hi
                 and r.end_time]
        if roots:
            root = sorted(roots, key=lambda r: r.start_time)[-1]
            return [{"name": r.name, "type": r.run_type,
                     "node": ((r.extra or {}).get("metadata") or {}).get("langgraph_node"),
                     "tools": ((r.extra or {}).get("invocation_params") or {}).get("tools") or [],
                     "status": r.status}
                    for r in client.list_runs(project_name=project, trace_id=root.trace_id)]
        time.sleep(10)
    return []


# ══════════════════════════════════════════════════════════════════════════
# MUTATION PROOFS — the mutation is on the check. Each hands its predicate
# the evidence the BROKEN behaviour would have written, and shows red.
# ══════════════════════════════════════════════════════════════════════════


def _field_log_fixture() -> list[dict]:
    """The shape of a correction as 6.33 writes it — only for the proofs."""
    return [
        {"field": "team", "turn": 3, "value": ["A"], "prior_value": None,
         "timestamp": "2026-09-23T08:00:00Z", "reason": None},
        {"field": "team", "turn": 7, "value": ["A", "B"], "prior_value": ["A"],
         "timestamp": "2026-09-23T09:00:00Z", "reason": None},
        {"field": "business_case", "turn": 4, "value": "GBP 1", "prior_value": None,
         "timestamp": "2026-09-23T08:10:00Z", "reason": None},
    ]


def test_mutation_row_1_a_case_missing_from_the_list_is_red() -> None:
    assert not _row_1([{"case_id": CASE_ID}], 200, {"case_id": CASE_ID})
    assert _row_1([{"case_id": "IMPR-OTHER"}], 200, {"case_id": CASE_ID})
    assert _row_1([{"case_id": CASE_ID}], 404, {})


def test_mutation_row_2_two_graph_runs_or_no_reply_is_red() -> None:
    good = {"status": 200, "body": {"answer": "Here is where you stand."},
            "inputs_before": 5, "inputs_after": 6}
    assert not _row_2(good)
    assert _row_2({**good, "inputs_after": 7})
    assert _row_2({**good, "body": {"answer": ""}})
    from backend.phases.nodes_common import _TIMEOUT_MESSAGE
    assert _row_2({**good, "body": {"answer": _TIMEOUT_MESSAGE}}), (
        "a 200 carrying the out-of-time message passed as a coached reply")


def test_mutation_row_3_an_undelivered_or_stale_script_is_red() -> None:
    good = [{"node": "coaching_script", "delivered": True, "sha256": "abc"}]
    assert not _row_3(good, "abc")
    assert _row_3([{**good[0], "delivered": False}], "abc")
    assert _row_3(good, "def")
    assert _row_3([], "abc")


def test_mutation_row_5_the_assignment_6_33_replaced_is_red() -> None:
    """Break: `structured = this_turn` instead of a merge — earlier fields vanish."""
    log = _field_log_fixture()
    merged = {"team": ["A", "B"], "business_case": "GBP 1"}
    assert not _row_5(log, merged)
    assert _row_5(log, {"team": ["A", "B"]})


def test_mutation_row_6_a_correction_without_its_prior_value_is_red() -> None:
    log = _field_log_fixture()
    assert not _row_6(log)
    assert _row_6([{**e, "prior_value": None} if e["turn"] == 7 else e for e in log])
    assert _row_6([{**e, "timestamp": ""} if e["turn"] == 7 else e for e in log])


def test_mutation_row_8_an_evidence_file_that_was_not_indexed_is_red() -> None:
    good = {"filename": "b.csv", "blob_path": "p", "blob_exists": True,
            "index_id": "x", "index_doc": {"id": "x"}}
    assert not _row_8([good])
    assert _row_8([{**good, "index_id": None}])
    assert _row_8([{**good, "index_doc": None}])
    assert _row_8([{**good, "blob_exists": False}])


def test_mutation_row_10_a_row_short_a_key_is_red() -> None:
    row = {k: 1 for k in COMPUTATION_KEYS}
    assert not _row_10([row])
    assert _row_10([{k: v for k, v in row.items() if k != "turn"}])


def test_mutation_row_11_a_metric_entry_that_does_not_mirror_is_red() -> None:
    s = {"baseline_estimate": "12.8%", "target_value": "3%"}
    assert not _row_11([{"name": "m", **s}], s)
    assert _row_11([{"name": "m", "baseline_estimate": None, "target_value": "3%"}], s)
    assert _row_11([], s)


def test_mutation_row_12_a_challenge_naming_no_criterion_is_red() -> None:
    """Row 12 re-pointed (founder 2026-10-14): a vague answer judged insufficient and challenged, naming
    one of the element's own criteria, is green; a challenge naming none, or another element's, is red."""
    good: dict[str, Any] = {"node": "planner", "key": "define:4:planner", "focus_field": "problem_statement",
            "move": "challenge", "judgment": {"verdict": "insufficient", "failed_criterion": "defect", "reason": "vague"}}
    found, problems = _row_12_challenges([[good]])
    assert found and not problems
    assert _row_12_challenges([[{**good, "judgment": {**good["judgment"], "failed_criterion": None}}]])[1]
    assert _row_12_challenges([[{**good, "judgment": {**good["judgment"], "failed_criterion": "ctq-measurable"}}]])[1]
    assert not _row_12_challenges([[{**good, "move": "read_back"}]])[0], "a read-back is no challenge"


def test_mutation_row_13_a_grade_that_never_reaches_step_log_is_red() -> None:
    graded = [{"node": "executor"}, {"node": "executor", "layer": "coaching_grader"}]
    assert not _row_13(graded)
    assert _row_13([e for e in graded if e.get("layer") != "coaching_grader"])


def test_mutation_row_17_a_2b_that_passes_a_missing_field_is_red() -> None:
    req = {"team", "business_case"}
    assert not _row_17([{"layer": "2b", "passed": False, "missing": ["team"]}], req)
    assert _row_17([{"layer": "2b", "passed": True, "missing": ["team"]}], req)


def _turn_fixture() -> dict:
    def ck(step, seen, source="loop"):
        return {"step": step, "source": source, "seen": seen, "values": {}}
    parent = [ck(10, {}, "input"), ck(11, {"__start__": {"a": 1}}),
              ck(12, {"__start__": {"a": 1}, "define_phase": {"b": 1}})]
    sub = [ck(-1, {}, "input"), ck(0, {"__start__": {"a": 1}}),
           ck(1, {"__start__": {"a": 1}, "planner": {"x": 1}}),
           ck(2, {"__start__": {"a": 1}, "planner": {"x": 1}, "executor": {"y": 1}})]
    return {"prior": ck(9, {"define_phase": {"b": 0}}), "parent": parent,
            "spaces": {"define_phase:1": sub}}


def test_mutation_row_33_writing_only_at_exit_is_red() -> None:
    """Break: `durability="exit"` — one checkpoint per namespace, at the end."""
    good = _turn_fixture()
    assert not _row_33(good, {"planner", "executor"})
    assert _row_33({**good, "parent": good["parent"][:2]}, {"planner", "executor", "gate_apply"})
    exit_only = {**good, "parent": good["parent"][-1:],
                 "spaces": {k: v[-1:] for k, v in good["spaces"].items()}}
    assert _row_33(exit_only, {"planner", "executor"})


def test_mutation_row_35_tracing_off_or_stripped_is_red() -> None:
    good: list[dict[str, Any]] = [{"name": "AzureChatOpenAI", "type": "llm", "node": MODEL_NODE,
             "tools": [{"function": {"name": "load_skill"}}], "status": "success"},
            {"name": "DMAICGraderMiddleware.after_agent", "type": "chain", "node": None,
             "tools": [], "status": "success"},
            {"name": "load_skill", "type": "tool", "node": "tools", "tools": [],
             "status": "success"}]
    assert not _row_35(good, {"load_skill"}, None)
    assert _row_35(None, set(), "no LANGSMITH_API_KEY")
    assert _row_35([], set(), None)
    assert _row_35([r for r in good if r["type"] != "tool"], {"load_skill"}, None)
    assert _row_35([r for r in good if MIDDLEWARE_MARK not in r["name"]], set(), None)


# ══════════════════════════════════════════════════════════════════════════
# CAPABILITY ROWS 18, 20 AND 21 — moved here 2026-10-19 (founder ruling 2026-10-19 (2), item 2)
# ══════════════════════════════════════════════════════════════════════════
#
# They read the live cases by design. Until G-234 ("Tests read live storage") they did so from
# test_declared_types.py and test_gate_write.py, quietly, past the network block; now this file —
# the one allowed to reach the live case (`enable_socket`) — holds them, and every other file stays
# off live storage.

GATE_PHASE = "define"

#: **The gate-proof case, and it is a SECOND case on purpose** — founder
#: ruling 2026-09-23, option B. Submitting a gate ADVANCES the case out of
#: Define, so proving the write on `IMPR-2026-0E5` would have ended the Define
#: proofs still owed: the ten checks, 6.46, 10.3 and 6.44 all need a live
#: define case. `IMPR-2026-0E5` therefore stays in define, and this case
#: carries the gate.
#:
#: It was coached to 13 of 13 through **real turns with the real model** —
#: nothing constructed — and its gate was submitted ONCE. Its title says so:
#: *"GATE PROOF — step 6.42, do not use for Define coaching proofs."*
#:
#: **A submitted case has advanced and cannot carry the next gate proof**, so
#: 7.3 will need a fresh one. Overridable by `CAPABILITY_GATE_CASE_ID`.
GATE_PROOF_CASE_ID = "IMPR-2026-1FF"


# ══════════════════════════════════════════════════════════════════════════
# CAPABILITY ROWS 20 AND 21 — on the case the system wrote
# ══════════════════════════════════════════════════════════════════════════


def _live_record():
    """The live case's define record, or a skip explaining which row cannot
    be evaluated. **Never constructs one.**"""
    from backend.storage import blob
    case_id = os.environ.get("CAPABILITY_GATE_CASE_ID", GATE_PROOF_CASE_ID)
    if not blob.storage_configured():
        pytest.skip("no storage configured — the row cannot be evaluated")
    case = asyncio.run(blob.load_case(case_id))
    if case is None:
        pytest.skip(f"{case_id} not found — the row cannot be evaluated")
    record = case.phases.get(GATE_PHASE)
    if record is None or not record.gate_passed:
        pytest.skip(
            f"{case_id}'s {GATE_PHASE} gate has not been submitted, so no document "
            "has been written. The row asks about a WRITTEN document and there "
            "is none to ask of — this is NOT a pass."
        )
    return case, record


#: The Define fields R4 and R5 added on 2026-09-26 (the benefits analysis, the CTQs, the 5W2H).
ADDED_2026_09_26 = ("benefits_analysis", "critical_to_quality", "problem_5w2h")


def test_row_20_the_document_is_written_and_safe_to_write_twice() -> None:
    """**Capability row 20**, read from `IMPR-2026-1FF` — the gate-proof case.

    Two halves, both checkable without writing anything:

    1. what was WRITTEN is a complete gate document — every field the schema
       declares, not the captured subset and not an empty dict;
    2. it is **exactly what assembly produces from the same artifacts, and
       assembly is deterministic** — which is why a second write cannot produce
       a different record. `write_phase_gate` stamps the approval on the
       TRANSITION only, so the second write is a no-op on the stamp as well.
    """
    from backend.phases.gate_registry import GATE_SPECS
    case, record = _live_record()
    written = dict(record.structured or {})
    declared = set(GATE_SPECS[GATE_PHASE].model.model_fields)
    # R4/R5 (founder, 2026-09-26) added three fields. A document WRITTEN before
    # that date was complete under the schema of its day, and is read as such;
    # one written after it must carry them. Named, never a blanket allowance.
    if str(record.submitted_at or "") < "2026-09-26":
        declared -= set(ADDED_2026_09_26)

    assert set(written) == declared, (
        "what was written is not a complete gate document: missing "
        f"{sorted(declared - set(written))}, unexpected "
        f"{sorted(set(written) - declared)}"
    )

    # Determinism, from the case's own captured values — the property that
    # makes a repeated write harmless.
    artifacts = {k: v for k, v in written.items()
                 if k in set(GATE_SPECS[GATE_PHASE].tier_1)}
    # A pre-R4 document has no value for the three added fields; determinism is
    # a property of assembly, so named stand-ins serve both runs equally.
    stand_in = {"benefits_analysis": {"cost_of_gap": "-", "impact_type": "-",
                                      "realisation_schedule": "-", "finance_contact": "-"},
                "critical_to_quality": [{"customer": "-", "need": "-", "requirement": "-"}],
                "problem_5w2h": {k: "-" for k in ("what", "where", "when", "who", "why",
                                                  "how", "how_much")}}
    artifacts = {**{f: stand_in[f] for f in ADDED_2026_09_26 if f not in artifacts}, **artifacts}
    once = GATE_SPECS[GATE_PHASE].assemble(artifacts, [], [], []).model_dump()
    twice = GATE_SPECS[GATE_PHASE].assemble(artifacts, [], [], []).model_dump()
    assert once == twice, "assembly is not deterministic"
    assert record.submitted_at, "a passed gate carries no approval stamp"


def test_row_21_the_gate_write_preserves_the_change_log_and_the_uploads() -> None:
    """**Capability row 21**, read from `IMPR-2026-1FF` — the gate-proof case.

    The record that survived the gate still holds what the gate did not write.
    `field_log` is step 6.33's, and by the time a gate is approved the Belt has
    captured twelve fields, so it cannot legitimately be empty.
    """
    case, record = _live_record()
    assert record.field_log, (
        "the gate write dropped `field_log` — the change log 6.33 built is "
        "gone from the record the gate approved"
    )
    assert record.submitted_by, "the approval stamp lost its actor"


# ══════════════════════════════════════════════════════════════════════════


def test_row_18_captured_values_carry_their_declared_type() -> None:
    """**Row 18 · container 4.** Team, scope, the SIPOC map and the registry
    arrive structured, not as prose.

    Reads the case the system actually wrote. **Nothing here constructs a
    captured value** — that is the whole design of this check, because a seeded
    version of it would have been green while `IMPR-2026-0E5` held four
    structured fields as prose.
    """
    from backend.phases.gate_registry import split_by_declared_type
    from backend.storage import blob
    case_id = os.environ.get("CAPABILITY_CASE_ID", "IMPR-2026-0E5")

    if not blob.storage_configured():
        pytest.skip(
            "no storage configured, so row 18 CANNOT BE EVALUATED. A skipped "
            "row is not a green row (Appendix H) — run against a real case."
        )

    case = asyncio.run(blob.load_case(case_id))
    if case is None:
        pytest.skip(f"{case_id} not found — row 18 cannot be evaluated")

    record = case.phases.get("define")
    captured = dict((record.structured or {}) if record else {})
    if not captured:
        pytest.skip(f"{case_id} has captured nothing — row 18 has no subject")

    _, malformed = split_by_declared_type("define", captured)
    assert not malformed, (
        "captured values that do not carry their declared type: "
        + json.dumps(malformed)
        + f" — of {len(captured)} captured field(s). A gate document cannot "
          "be assembled from these."
    )
