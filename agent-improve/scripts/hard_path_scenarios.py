"""The hard paths, proven live — founder rulings 2026-10-13 (scenarios (b)-(e); (a) is DEF-040's open proof).

Each scenario runs on its OWN fresh case, through the real routes and graph and the live models, a few
turns at the first elements, and writes one record entry `{"kind": "scenario_<x>", "passed", "checks",
"turns", "model_calls", "cost"}` to the run-through's record. A check is a named boolean, so a failed
scenario says which part failed. Called by `scripts/define_runthrough.py` after its walk.

  (b) a turn crashes mid-way (the coach's model fails after the planner ran) → the Belt is told it
      did not go through (T29's degraded reply, nothing changed) → the next message recovers from the
      last checkpoint: a coached reply, nothing stored.
  (c) the turn deadline is hit → the Belt is asked to send again → the resend succeeds.
  (d) an element fails three times → parked → the next element is taught → resumed → confirmed.
  (e) a team list uploaded → the upload turn names the file, says it covers the team, and reads the team
      back from the file (ADR-0085, G-169) → the Belt asks to use the file, which confirms it → stored, its
      source recorded as the upload.

The crash in (b) and the short deadline in (c) are made by this harness, never by the product: (b)
makes the coach's model fail once, (c) shortens the route's turn limit for one turn.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any, Callable

from scripts.move_proof_661 import CALLS, token_totals

USER = "define-runthrough-scenarios"
OPENING = "Hi — I'm ready to start Define on our project."


def _case(client: Any, title: str) -> str:
    r = client.post("/cases", json={"title": title, "belt_level": "green", "leader": "Priya Shah",
                                    "department": "Finance — Accounts Payable", "target_date": "2027-03-31",
                                    "team": []})
    r.raise_for_status()
    return str(r.json()["case_id"])


def _ask(client: Any, case_id: str, message: str, action: str | None = None,
         element: str | None = None) -> tuple[int, dict[str, Any], float]:
    body: dict[str, Any] = {"case_id": case_id, "phase": "define", "message": message, "user": USER}
    if action:
        body["action"] = action
    if element:
        body["element"] = element
    t0 = time.time()
    r = client.post("/ask", json=body)
    return r.status_code, (r.json() if r.status_code == 200 else {"detail": r.text[:300]}), round(time.time() - t0, 1)


def _case_state(client: Any, case_id: str) -> dict[str, Any]:
    case = client.get(f"/cases/{case_id}").json()
    define = (case.get("phases") or {}).get("define") or {}
    return {"history": case.get("conversation_history") or [], "structured": define.get("structured") or {},
            "status": define.get("field_status") or {}, "field_log": define.get("field_log") or []}


def _record(name: str, c0: int, turns: list[dict[str, Any]], checks: dict[str, bool]) -> dict[str, Any]:
    from scripts.define_runthrough import _cost
    calls = CALLS[c0:]
    return {"kind": f"scenario_{name}", "passed": all(checks.values()), "checks": checks, "turns": turns,
            "model_calls": [c["kind"] for c in calls], "tokens": token_totals(calls)["total"],
            "cost": _cost(token_totals(calls))}


def _turn(n: int, why: str, http: int, body: dict[str, Any], seconds: float) -> dict[str, Any]:
    return {"n": n, "why": why, "http": http, "seconds": seconds, "move": body.get("move"),
            "field": body.get("move_field"), "answer": str(body.get("answer") or body.get("detail") or "")[:400]}


def scenario_b_crash(client: Any) -> dict[str, Any]:
    """(b) A turn crashes after the planner checkpointed; the next message recovers."""
    from backend.phases import nodes_common
    c0 = len(CALLS)
    case_id = _case(client, "SCENARIO (b) — a crashed turn recovers")
    real = nodes_common.get_llm
    crashed = {"n": 0}

    def crash_once(role: str, *a: Any, **k: Any) -> Any:
        if role == "coach" and crashed["n"] == 0:
            crashed["n"] += 1
            raise RuntimeError("scenario (b): the coach's model failed mid-turn")
        return real(role, *a, **k)
    nodes_common.get_llm = crash_once  # type: ignore[assignment]
    try:
        h1, b1, s1 = _ask(client, case_id, OPENING)
    finally:
        nodes_common.get_llm = real  # type: ignore[assignment]
    h2, b2, s2 = _ask(client, case_id, OPENING)
    st = _case_state(client, case_id)
    from backend.core.graph import DEGRADED_REPLY
    replies = [str(t.get("text") or "") for t in st["history"] if t.get("role") == "ai"]
    checks = {"the crashed turn tells the Belt it did not go through": h1 == 200
              and b1.get("answer") == DEGRADED_REPLY and b1.get("move") is None,
              "the next message is coached (teach business_case)": h2 == 200 and b2.get("move") == "teach"
              and b2.get("move_field") == "business_case",
              "nothing stored": not st["structured"],
              "the history: the degraded reply, then the coached one": len(replies) == 2
              and replies[0] == DEGRADED_REPLY}
    return _record("b", c0, [_turn(1, "crash", h1, b1, s1), _turn(2, "resend", h2, b2, s2)], checks)


def scenario_c_deadline(client: Any) -> dict[str, Any]:
    """(c) The turn deadline is hit; the Belt resends; the resend succeeds."""
    from backend.gateway import routes
    c0 = len(CALLS)
    case_id = _case(client, "SCENARIO (c) — a turn stopped at its deadline")
    limit, reserve = routes.TURN_LIMIT_S, routes.TURN_CLOSE_RESERVE_S
    routes.TURN_LIMIT_S, routes.TURN_CLOSE_RESERVE_S = 6.0, 1.0      # a 5 s window: a teaching turn runs ~20 s
    try:
        h1, b1, s1 = _ask(client, case_id, OPENING)
    finally:
        routes.TURN_LIMIT_S, routes.TURN_CLOSE_RESERVE_S = limit, reserve
    time.sleep(2.0)
    h2, b2, s2 = _ask(client, case_id, OPENING)
    st = _case_state(client, case_id)
    replies = [t for t in st["history"] if t.get("role") == "ai"]
    checks = {"the turn was stopped at its deadline": h1 == 200 and b1.get("answer") == routes.TURN_DEADLINE_REPLY,
              "within the limit as the client measures it": s1 <= 6.5,
              "no Confirm offered on the stopped turn": b1.get("move") is None,
              "the resend is coached (teach business_case)": h2 == 200 and b2.get("move") == "teach"
              and b2.get("move_field") == "business_case",
              "nothing stored": not st["structured"],
              "one reply in the history (the stopped turn left none)": len(replies) == 1}
    return _record("c", c0, [_turn(1, "deadline", h1, b1, s1), _turn(2, "resend", h2, b2, s2)], checks)


def scenario_d_park(client: Any, good: dict[str, str]) -> dict[str, Any]:
    """(d) Three failed attempts → park → the next element → resume → confirmed."""
    c0 = len(CALLS)
    case_id = _case(client, "SCENARIO (d) — park an element and resume it")
    turns: list[dict[str, Any]] = []

    def say(why: str, message: str, action: str | None = None, element: str | None = None) -> dict[str, Any]:
        h, b, s = _ask(client, case_id, message, action, element)
        turns.append(_turn(len(turns) + 1, why, h, b, s))
        return b
    say("opening", OPENING)
    weak = ["It's slow.", "Payments are slow and people complain.", "It costs us money, I think."]
    moves_seen = [say(f"weak answer {i + 1}", w).get("move") for i, w in enumerate(weak)]
    parked = say("park", "Park and move on", action="park")
    st_parked = _case_state(client, case_id)
    resumed = say("resume", "Resume: business case", action="revise", element="business_case")
    read = say("good answer", good["business_case"])
    say("confirm", "Confirm", action="confirm")
    st = _case_state(client, case_id)
    checks = {"the third failed attempt offers the park": "offer_park" in moves_seen,
              "parking moves on to the next element": parked.get("move_field") not in (None, "business_case"),
              "the element is recorded parked": (st_parked["status"].get("business_case") or {}).get("status") == "parked",
              "resume returns to the parked element": resumed.get("move_field") == "business_case",
              "the resumed element is read back": read.get("move") == "read_back",
              "confirmed and stored": bool(st["structured"].get("business_case")),
              "the stored value is the answer given after the resume, alone (G-167)":
              st["structured"].get("business_case") == good["business_case"]}
    return _record("d", c0, turns, checks)


TEAM_CSV = "\n".join([
    "name,role,function,training",
    "Priya Shah,Green Belt (project lead),runs the project day to day,none",
    "Tom Okafor,Champion (sponsor),Finance Director; signs off and clears blockers,none",
    "Lena Hart,Process owner,Accounts Payable Manager,none",
    "Dev Patel,Team member,AP clerk who processes invoices,half a day on data collection before Measure",
    "Amira Khan,Team member,AP clerk who processes invoices,half a day on data collection before Measure",
    ""])


def scenario_e_upload(client: Any, good: dict[str, str]) -> dict[str, Any]:
    """(e) A team list uploaded: the upload turn names the file and reads the team back (ADR-0085, G-169);
    "use the file" confirms it; stored with the upload as its source."""
    c0 = len(CALLS)
    case_id = _case(client, "SCENARIO (e) — an uploaded team list read back and confirmed")
    filename = "project_team_ap_late_payments.csv"
    turns: list[dict[str, Any]] = []

    def say(why: str, message: str, action: str | None = None) -> dict[str, Any]:
        h, b, s = _ask(client, case_id, message, action)
        turns.append(_turn(len(turns) + 1, why, h, b, s))
        return b
    say("opening", OPENING)
    say("business case", good["business_case"])
    taught = say("confirm the business case", "Confirm", action="confirm")
    t0 = time.time()
    up = client.post("/upload", data={"case_id": case_id, "uploaded_by": USER, "phase": "define", "kind": "evidence"},
                     files={"file": (filename, TEAM_CSV.encode(), "text/csv")})
    turns.append({"n": len(turns) + 1, "why": "upload", "http": up.status_code, "seconds": round(time.time() - t0, 1)})
    seen = say("the upload turn", "I've uploaded our team list.")
    used = say("use the file", f"Please use the team exactly as listed in {filename}.")
    st = _case_state(client, case_id)
    team = st["structured"].get("team") or []
    sources = [e.get("source") for e in st["field_log"] if e.get("field") == "team"]
    names = {str(m.get("name") or "") for m in team if isinstance(m, dict)}
    checks = {"the team element is current": taught.get("move_field") == "team",
              "the upload lands": up.status_code == 200,
              "the upload turn names the file": filename in str(seen.get("answer") or ""),
              "the upload turn reads the team back": seen.get("move") == "read_back"
              and seen.get("move_field") == "team",
              "\"use the file\" confirms it": used.get("move") == "store_and_advance",
              "confirmed and stored, the five people in it": {"Priya Shah", "Tom Okafor", "Lena Hart", "Dev Patel",
                                                              "Amira Khan"} <= names,
              "its source is recorded as the upload": any("upload" in str(x or "") for x in sources)}
    return _record("e", c0, turns, checks)


# ══ the live slices (founder ruling 2026-10-14) — each from a SAVED case ══════════════════════════════════
#
# A saved case is a case record as an earlier release wrote it (state schema 8, `scripts/saved_cases/`, cut
# from run 154211's case IMPR-2026-15A), written to the case store as it was saved under a fresh id; the app
# loads it through the migrations to schema 9 (ADR-0065). No LangGraph checkpoint is saved with it: the
# first turn builds one from the record (ADR-0066), as for any case reloaded with no unfinished work.

SAVED = Path(__file__).resolve().parent / "saved_cases"


def saved_case(name: str, title: str) -> str:
    """Write the saved case `name` to the case store, as saved (schema 8), under a fresh id; its id."""
    import json
    import uuid
    from azure.storage.blob import BlobServiceClient
    from backend.core.config import settings
    from backend.storage import blob
    data = json.loads((SAVED / f"{name}.v8.json").read_text(encoding="utf-8"))
    data.pop("_saved", None)
    case_id = f"IMPR-SAVED-{uuid.uuid4().hex[:6].upper()}"
    data.update({"case_id": case_id, "title": title})
    box = BlobServiceClient.from_connection_string(settings.AZURE_BLOB_CONNECTION_STRING) \
        .get_container_client(settings.AZURE_BLOB_CONTAINER_IMPROVE)
    box.upload_blob(blob.case_path(case_id), json.dumps(data), overwrite=True)
    return case_id


def _loads_migrated(client: Any, case_id: str) -> bool:
    """The saved case (schema 8) opens in this release (schema 9): migrated on load, nothing refused."""
    from backend.core import migrations
    r = client.get(f"/cases/{case_id}")
    return r.status_code == 200 and migrations.current() == 9 and 8 in migrations.MIGRATIONS


def slice_1_upload(client: Any) -> dict[str, Any]:
    """Slice 1 — an upload covering the team element → read back → "use the file" stores (ADR-0085)."""
    c0 = len(CALLS)
    case_id = saved_case("define_team_next", "SLICE 1 — an uploaded team list read back and stored")
    filename = "project_team_ap_late_payments.csv"
    turns: list[dict[str, Any]] = []
    loaded = _loads_migrated(client, case_id)
    up = client.post("/upload", data={"case_id": case_id, "uploaded_by": USER, "phase": "define", "kind": "evidence"},
                     files={"file": (filename, TEAM_CSV.encode(), "text/csv")})
    turns.append({"n": 1, "why": "upload", "http": up.status_code})
    h, seen, s = _ask(client, case_id, "I've uploaded our team list.")
    turns.append(_turn(2, "the upload turn", h, seen, s))
    h, used, s = _ask(client, case_id, f"Please use the team exactly as listed in {filename}.")
    turns.append(_turn(3, "use the file", h, used, s))
    st = _case_state(client, case_id)
    names = {str(m.get("name") or "") for m in st["structured"].get("team") or [] if isinstance(m, dict)}
    sources = [e.get("source") for e in st["field_log"] if e.get("field") == "team"]
    checks = {"the saved case loads through the v9 migrations": loaded,
              "the upload lands": up.status_code == 200,
              "the upload turn names the file": filename in str(seen.get("answer") or ""),
              "the upload turn reads the team back": seen.get("move") == "read_back" and seen.get("move_field") == "team",
              "\"use the file\" stores it": used.get("move") == "store_and_advance",
              "the five people are stored": {"Priya Shah", "Tom Okafor", "Lena Hart", "Dev Patel", "Amira Khan"} <= names,
              "its source is the upload": "upload" in [str(x or "") for x in sources]}
    return {**_record("slice_1", c0, turns, checks), "case_id": case_id}


def slice_2_gate(client: Any) -> dict[str, Any]:
    """Slice 2 — T14, T15, T23: the report validated → the graph pauses, nothing written → a process restart
    → the pause survives → approve → the gate document in the Store and in the phase's final, agreeing with
    the case → a second approval writes nothing."""
    from backend.core import checkpointer as cp_mod
    from backend.core import graph as graph_mod
    from backend.core.store import get_store
    from backend.phases.mappers_common import read_gate_document
    from scripts.coaching_proof_656 import _latest_final
    from scripts.define_runthrough import t23_check
    c0 = len(CALLS)
    case_id = saved_case("define_all_confirmed", "SLICE 2 — the report paused, restarted, approved once")
    loaded = _loads_migrated(client, case_id)
    t0 = time.time()
    sub = client.post("/gate", json={"case_id": case_id, "submitted_by": USER, "phase": "define"})
    body = sub.json() if sub.status_code == 200 else {}
    turns: list[dict[str, Any]] = [{"n": 1, "why": "submit", "http": sub.status_code, "seconds": round(time.time() - t0, 1),
                                    "passed": body.get("passed"), "awaiting": body.get("awaiting_acceptance")}]
    before = read_gate_document(get_store(), case_id, "define") or {}
    case_before = client.get(f"/cases/{case_id}").json()
    # A process restart: a new graph and a new saver over the same storage.
    graph_mod.get_graph.cache_clear()
    cp_mod._singleton = None
    review = client.get(f"/gate/review/{case_id}/define").json()
    t0 = time.time()
    dec = client.post("/gate/decision", json={"case_id": case_id, "phase": "define", "decision": "approve",
                                             "actor": "Priya Shah"})
    turns.append({"n": 2, "why": "approve after the restart", "http": dec.status_code, "seconds": round(time.time() - t0, 1)})
    doc = read_gate_document(get_store(), case_id, "define") or {}
    final = dict((_latest_final(case_id) or {}).get("final") or {})
    t23 = t23_check(client, case_id)
    turns.append({"n": 3, "why": "a second approval", "http": t23["second_approval_http"]})
    checks = {"the saved case loads through the v9 migrations": loaded,
              "T14: the validated report pauses the graph": sub.status_code == 200 and bool(body.get("awaiting_acceptance")),
              "T14: nothing is written before the decision": not before
              and not ((case_before.get("phases") or {}).get("define") or {}).get("gate_passed"),
              "T15: the pause survives a process restart": bool(review.get("awaiting_decision")),
              "the approval is accepted": dec.status_code == 200,
              "T23: the gate document is in the Store": bool(doc),
              "T23: and in the phase's final, the same": bool(final) and all(final.get(k) == v for k, v in doc.items()
                                                                            if k in final),
              "T23: the Store agrees with the case": not t23["differ_from_case"],
              "T15/T23: a second approval writes nothing": t23["unchanged_after_second"]}
    return {**_record("slice_2", c0, turns, checks), "case_id": case_id, "t23": t23,
            "final_keys": len(final), "store_keys": len(doc)}


def slice_3_grader(client: Any, good: dict[str, str]) -> dict[str, Any]:
    """Slice 3 — five coaching turns; each coached reply's G1–G5 verdicts in step_log, every fail quoting a
    sentence of the reply it fails."""
    from scripts.define_runthrough import grader_entry
    c0 = len(CALLS)
    case_id = saved_case("define_baseline_next", "SLICE 3 — five coached turns, graded G1–G5")
    loaded = _loads_migrated(client, case_id)
    plan = [("teach the baseline", "Next, please.", None), ("the baseline", good["baseline_estimate"], None),
            ("confirm the baseline", "Confirm", "confirm"), ("the scope", good["project_scope"], None),
            ("confirm the scope", "Confirm", "confirm")]
    turns: list[dict[str, Any]] = []
    graded: list[dict[str, Any]] = []
    for n, (why, message, action) in enumerate(plan, 1):
        h, b, s = _ask(client, case_id, message, action)
        g = grader_entry(case_id, message)
        turns.append({**_turn(n, why, h, b, s), "grader": g})
        if g:
            graded.append({"n": n, "reply": str(b.get("answer") or "") + " " + " ".join(
                str(b.get(k) or "") for k in ("explanation", "example", "prompt")), **g})

    def quoted(ev: str, reply: str) -> bool:
        norm = lambda x: " ".join(str(x).replace("“", "").replace("”", "").replace('"', "").lower().split())  # noqa: E731
        return len(norm(ev)) >= 8 and norm(ev) in norm(reply)
    fails = [(t["n"], f) for t in graded for f in t.get("failed") or []]
    checks = {"the saved case loads through the v9 migrations": loaded,
              "five turns answered": len(turns) == 5 and all(t["http"] == 200 for t in turns),
              "every coached reply has a G1–G5 verdict in step_log": bool(graded)
              and all(t.get("status") for t in graded),
              "verdicts are G1–G5 (and the code check)": all(
                  set((t.get("verdicts") or {})) <= {"G1", "G2", "G3", "G4", "G5", "no external URLs"} for t in graded),
              "every fail quotes a sentence (counted only with one, in the text it graded)": all(
                  str(f.get("evidence") or "").strip() for t in graded for f in t.get("failed") or [])}
    # A finding, not a check (founder 2026-10-14: placement and calibration after Define): the grader runs in
    # the coach's after_agent hook, on the coach's own reply — before code replaces the example (G-170) and,
    # after a store, the teaching (G-175). A fail can quote a sentence the Belt never sees.
    unseen = [(n, f["criterion"], str(f.get("evidence") or "")[:120]) for n, f in fails
              if f.get("criterion") != "no external URLs"
              and not quoted(f.get("evidence") or "", next(t["reply"] for t in graded if t["n"] == n))]
    return {**_record("slice_3", c0, turns, checks), "case_id": case_id, "graded": len(graded), "fails": len(fails),
            "fails_quoting_text_the_belt_never_saw": unseen}


def run_slices(client: Any, write: Callable[[dict[str, Any]], None], good: dict[str, str],
               only: int | None = None) -> dict[str, bool]:
    """The three slices (or slice `only`), each written as it ends; returns {name: passed}."""
    out = {}
    for name, fn in (("slice_1", lambda: slice_1_upload(client)), ("slice_2", lambda: slice_2_gate(client)),
                     ("slice_3", lambda: slice_3_grader(client, good))):
        if only and name != f"slice_{only}":
            continue
        try:
            entry = fn()
        except Exception as exc:  # noqa: BLE001 — a slice that raises is a failed slice, recorded
            entry = {"kind": name, "passed": False, "checks": {"ran": False},
                     "error": f"{exc.__class__.__name__}: {exc}"[:400]}
        write(entry)
        out[name] = bool(entry.get("passed"))
        print(f"{name}: {'PASS' if entry.get('passed') else 'FAIL'} "
              f"{ {k: v for k, v in (entry.get('checks') or {}).items() if not v} } "
              f"USD {(entry.get('cost') or {}).get('usd')}")
    return out


def run_all(client: Any, write: Callable[[dict[str, Any]], None], good: dict[str, str]) -> dict[str, bool]:
    """Every scenario, each written as it ends; returns {name: passed}."""
    out = {}
    for name, fn in (("b", lambda: scenario_b_crash(client)), ("c", lambda: scenario_c_deadline(client)),
                     ("d", lambda: scenario_d_park(client, good)), ("e", lambda: scenario_e_upload(client, good))):
        try:
            entry = fn()
        except Exception as exc:  # noqa: BLE001 — a scenario that raises is a failed scenario, recorded
            entry = {"kind": f"scenario_{name}", "passed": False, "checks": {"ran": False},
                     "error": f"{exc.__class__.__name__}: {exc}"[:400]}
        write(entry)
        out[name] = bool(entry.get("passed"))
        print(f"scenario ({name}): {'PASS' if entry.get('passed') else 'FAIL'} "
              f"{ {k: v for k, v in (entry.get('checks') or {}).items() if not v} } "
              f"USD {(entry.get('cost') or {}).get('usd')}")
    return out
