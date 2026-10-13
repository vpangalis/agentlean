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
  (e) a team list uploaded → the upload turn names the file and what it covers (ADR-0074) → the Belt
      asks to use it → read back → Confirm → stored, its source recorded as the upload. On the team
      element: a structured value stores the version read back; a plain-text one stores the Belt's own
      words, so a file can never be its value (moves.pending_store).

The crash in (b) and the short deadline in (c) are made by this harness, never by the product: (b)
makes the coach's model fail once, (c) shortens the route's turn limit for one turn.
"""
from __future__ import annotations

import time
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
    """(e) A team list uploaded: named by the upload turn, read back, confirmed, stored with its source."""
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
    read = say("use the file", f"Please use the team exactly as listed in {filename}.")
    say("confirm the team", "Confirm", action="confirm")
    st = _case_state(client, case_id)
    team = st["structured"].get("team") or []
    sources = [e.get("source") for e in st["field_log"] if e.get("field") == "team"]
    names = {str(m.get("name") or "") for m in team if isinstance(m, dict)}
    checks = {"the team element is current": taught.get("move_field") == "team",
              "the upload lands": up.status_code == 200,
              "the upload turn names the file": filename in str(seen.get("answer") or ""),
              "the team is read back": read.get("move") == "read_back",
              "confirmed and stored, the five people in it": {"Priya Shah", "Tom Okafor", "Lena Hart", "Dev Patel",
                                                              "Amira Khan"} <= names,
              "its source is recorded as the upload": any("upload" in str(x or "") for x in sources)}
    return _record("e", c0, turns, checks)


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
