"""Step 6.61 — the proof that the coaching move is decided in code. Part 2.

**OUTSIDE PYTEST, ON PURPOSE**, like `coaching_proof_656.py`, whose tracing
switch and LangSmith send-counter it reuses: real model calls, real storage, a
NEW case titled "6.61 PROOF — do not use". Tracing is OFF; every run the
LangSmith client is asked to send is counted, and any count above zero fails.

THE AUDIT RECORD — one JSON line per turn or run, written as it happens.

PART A — THREE TURNS THROUGH `POST /ask` (brief items 7 and 9)
    opening · the AD5 business case (the £62,000, the three suppliers, the two
    stops) · "Yes, that's right." For each: the coach's FULL input exactly as
    the model received it (recorded at the chat-model boundary), the planner's
    judgment and the move code chose (read from the move record the reply
    carries), the pending value and what the case record stored.

PART B — EIGHT SITUATIONS, THREE RUNS EACH (rulings, fix 5)
    Each run is the real `planner` node and the real `executor` node — the
    real `create_agent` coach, the real middleware stack — started from the
    REAL conversation part A produced, so the five runs of a situation start
    from the same state. **Coherence and the grader are stood down in part B**
    (fixed pass verdicts, no model call): neither decides the move or the
    question, and both would spend two of the cap's calls per run. Part A runs
    them for real.

THE CAP — `--max-calls` (default 120, ruling R1) model calls, counted at the chat-model
boundary (`BaseChatModel.agenerate`), every role. The call past the cap raises
and the run stops with what it has.

    python -m scripts.move_proof_661 --out <dir>
"""
from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

from scripts.coaching_proof_656 import ANSWERS, SENDS, _tracing_off

CASE_TITLE = "6.61 PROOF — do not use"
USER = "move-proof-6.61"

OPENING = "Hi — I'm ready to start Define on our project."
AD5 = ANSWERS[1]
WEAK = "It's costing us money, and people are unhappy about it."
CONFIRM = "Yes, that's right."
CORRECT = ("Nearly — the interest and lost discounts came to about £64,000, not "
           "£62,000. The rest is right.")
AGAIN = "Before I say yes — can you show me that once more?"
WHERE = "Where do we stand?"


class CapReached(RuntimeError):
    """The model-call cap was reached; the run stops with what it has."""


CALLS: list[dict[str, Any]] = []
COACH_INPUTS: list[list[dict[str, Any]]] = []


def _serialise(message: Any) -> dict[str, Any]:
    blocks = getattr(message, "content_blocks", None)
    text = [b.get("text", "") for b in (blocks or []) if b.get("type") == "text"]
    return {"type": message.type,
            "blocks": text if text else [str(message.content)],
            "tool_calls": [c.get("name") for c in (getattr(message, "tool_calls", None) or [])],
            "name": getattr(message, "name", None)}


def _count_model_calls(cap: int) -> None:
    """Every chat-model call, counted — and the coach's input kept verbatim."""
    from langchain_core.language_models.chat_models import BaseChatModel
    original = BaseChatModel.agenerate

    async def agenerate(self: Any, messages: Any, *args: Any, **kwargs: Any) -> Any:
        if len(CALLS) >= cap:
            raise CapReached(f"model-call cap {cap} reached")
        first = messages[0] if messages else []
        system = next((m for m in first if m.type == "system"), None)
        text = " ".join(_serialise(system)["blocks"]) if system else " ".join(
            _serialise(m)["blocks"][0] for m in first[:1])
        kind = ("coach" if "## 1 · COACHING RULES" in text else
                "planner-judgment" if "You judge ONE thing" in text else
                "coherence" if "coheren" in text.lower() else
                "grader" if "grading ONE coaching turn" in text else "other")
        CALLS.append({"kind": kind, "at": dt.datetime.now(dt.timezone.utc).isoformat()})
        if kind == "coach":
            COACH_INPUTS.append([_serialise(m) for m in first])
        return await original(self, messages, *args, **kwargs)

    BaseChatModel.agenerate = agenerate  # type: ignore[method-assign]


def _write(path: Path, record: dict) -> None:
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def _question(blocks: dict, answer: str) -> str:
    """The question the coach asked — the `prompt` block, else the last
    sentence of the message that ends in a question mark."""
    if (blocks or {}).get("prompt"):
        return str(blocks["prompt"]).strip()
    qs = re.findall(r"[^.!?\n]*\?", answer or "")
    return qs[-1].strip() if qs else "(no question)"


# ══ part A — three turns through the route ═══════════════════════════════════


def part_a(client: Any, jsonl: Path) -> dict[str, Any]:
    from backend.phases import moves
    created = client.post("/cases", json={
        "title": CASE_TITLE, "belt_level": "green", "leader": "Priya Shah",
        "department": "Finance — Accounts Payable", "target_date": "2027-03-31", "team": []})
    created.raise_for_status()
    case_id = created.json()["case_id"]
    print(f"case {case_id} — {CASE_TITLE}")
    turns = []
    for n, (kind, belt) in enumerate((("opening", OPENING), ("good business-case answer", AD5),
                                      ("the Belt confirms", CONFIRM)), 1):
        calls_before, inputs_before = len(CALLS), len(COACH_INPUTS)
        t0 = time.time()
        resp = client.post("/ask", json={"case_id": case_id, "phase": "define",
                                         "message": belt, "user": USER})
        seconds = round(time.time() - t0, 1)
        if resp.status_code != 200:
            raise RuntimeError(f"turn {n} answered {resp.status_code}: {resp.text[:300]}")
        case = client.get(f"/cases/{case_id}").json()
        history = case.get("conversation_history") or []
        ai = [t for t in history if t.get("role") == "ai"][-1]
        record = ai.get(moves.MOVE_RECORD_KEY) or {}
        structured = ((case.get("phases") or {}).get("define") or {}).get("structured") or {}
        body = resp.json()
        rec = {
            "part": "A", "turn": n, "kind": kind, "belt": belt, "seconds": seconds,
            "model_calls": [c["kind"] for c in CALLS[calls_before:]],
            "coach_input_as_sent": COACH_INPUTS[inputs_before] if len(COACH_INPUTS) > inputs_before else None,
            "coach_calls_this_turn": len(COACH_INPUTS) - inputs_before,
            "judgment": record.get("judgment"), "move": record.get("move"),
            "field": record.get("field"), "status": record.get("status"),
            "pending": record.get("pending"), "stored": record.get("stored"),
            "case_record_structured": structured,
            "answer": body.get("answer"), "prompt_block": body.get("prompt"),
            "quality_feedback_on_reply": ai.get(moves.QUALITY_FEEDBACK_KEY),
        }
        _write(jsonl, rec)
        turns.append(rec)
        print(f"A{n} [{kind}] move={rec['move']} field={rec['field']} "
              f"judgment={(rec['judgment'] or {}).get('verdict')} calls={rec['model_calls']} "
              f"stored={list(structured)}")
    return {"case_id": case_id, "turns": turns}


# ══ part B — eight situations, three runs each, through the real nodes ══════


def _awaiting() -> dict[str, dict[str, Any]]:
    """`business_case` answered and read back, awaiting confirmation — the
    stored status (R5) the four read-back situations start from."""
    return {"business_case": {
        "status": "answered", "answer": AD5, "messages": 1,
        "pending": {"field": "business_case", "fields": ["business_case"],
                    "belt_words": AD5, "messages": 1, "store": {"business_case": AD5}}}}


ASKED = {"business_case": {"status": "asked"}}


def _section(inputs: list[dict], heading: str) -> str:
    """One labelled section of a coach input, by its heading's number."""
    for m in inputs:
        for block in m["blocks"]:
            if block.startswith(heading):
                return block
    return ""


def _tool_trace(messages: list) -> list[str]:
    """The coach's tool calls this run, in order; a call answered with the
    spent-budget result is marked `SPENT`."""
    trace: list[str] = []
    for m in messages:
        for call in (getattr(m, "tool_calls", None) or []):
            trace.append(call.get("name"))
        if m.type == "tool" and str(m.content).startswith("Retrieval budget for this turn is spent"):
            trace.append("SPENT")
    return trace


async def _one_run(case_id: str, messages: list, config: Any,
                   field_status: dict, action: str | None = None) -> dict:
    from backend.core.store import get_store
    from backend.phases import moves, nodes_common
    from backend.phases.define.mappers import define_input_mapper
    parent: Any = {"messages": messages, "history": [], "case_id": case_id, "phase_index": 0,
                   "current_phase": "define", "gate_passed": {}, "final_output": None}
    state = await asyncio.to_thread(define_input_mapper, parent, get_store())
    # R5 — the status is STORED; the situation sets it, as the case record would.
    state = {**state, "field_status": {f: dict(v) for f, v in field_status.items()}}
    cfg: Any = {**config, "configurable": {**config["configurable"], "belt_action": action}}
    cmd = await nodes_common.planner("define", state, cfg)
    state = {**state, **(cmd.update or {})}  # type: ignore[typeddict-item]
    inputs_before = len(COACH_INPUTS)
    out = await nodes_common.executor("define", state, cfg)
    plan = state["coaching_plan"]
    assert plan is not None, "the planner produced no plan"
    reply = [m for m in out["messages"] if m.type == "ai"][-1]
    blocks = reply.additional_kwargs.get("coaching_blocks") or {}
    record = reply.additional_kwargs.get(moves.MOVE_RECORD_KEY) or {}
    first = COACH_INPUTS[inputs_before] if len(COACH_INPUTS) > inputs_before else []
    return {"move": plan.move, "field": plan.focus_field, "status": plan.status,
            "judgment": plan.judgment.model_dump() if plan.judgment else None,
            "question": _question(blocks, str(reply.content)),
            "answer": str(reply.content),
            "fallback": bool(record.get("fallback")),
            "tools": _tool_trace(out["messages"]),
            "coach_calls": len(COACH_INPUTS) - inputs_before,
            "section_5": _section(first, "## 5 ·"),
            # The coach's last input past the six sections: what it had said
            # and been answered this run — where a loop shows itself.
            "trail": [{"type": m["type"], "tool_calls": m["tool_calls"], "name": m["name"],
                       "text": " ".join(m["blocks"])[:300]}
                      for m in (COACH_INPUTS[-1] if len(COACH_INPUTS) > inputs_before else [])[-12:]
                      if m["type"] != "system"],
            "status_after": {f: v.get("status") for f, v in (out.get("field_status") or {}).items()
                             if f in ("business_case", "team")},
            "stored": sorted(out.get("draft") or {})}


def _stand_down_judges() -> None:
    """Coherence and the grader give fixed pass verdicts in part B: neither
    decides the move or the question, and each would spend a call per run."""
    from backend.middleware.coherence import CoherenceMiddleware
    from backend.middleware.grader import DMAICGraderMiddleware
    from backend.validation.schemas import CoachingGraderVerdict, CoherenceResult

    async def coherent(self: Any, belt: str, coach: str) -> CoherenceResult:
        return CoherenceResult(coherent=True, is_conclusive=True, is_parroting=False,
                               on_topic=True, reason="")

    async def passing(self: Any, belt: str, coach: str) -> CoachingGraderVerdict:
        return CoachingGraderVerdict(criteria=[])

    CoherenceMiddleware._check = coherent            # type: ignore[method-assign]
    DMAICGraderMiddleware._grade = passing           # type: ignore[method-assign]


async def _history(case_id: str) -> list:
    from backend.core.conversation import turn_to_message
    from backend.storage import blob
    case = await blob.load_case(case_id)
    assert case is not None, f"{case_id} is not in storage"
    return [turn_to_message(t) for t in (case.conversation_history or [])]


CONFIG: Any = {"configurable": {"entry": "ask", "case_metadata": {"title": CASE_TITLE},
                                "v1_phase_inputs": {}}, "recursion_limit": 50}


def _config(case_id: str) -> Any:
    return {**CONFIG, "configurable": {**CONFIG["configurable"], "thread_id": case_id}}


async def _part_b(case_id: str, runs: int, jsonl: Path, skip: tuple[str, ...]) -> list[dict]:
    """ONE event loop for every run — the model clients are bound to the loop
    they were built on (a fresh `asyncio.run` per run failed, first proof)."""
    from langchain_core.messages import HumanMessage as H
    msgs = await _history(case_id)
    # The real conversation part A produced: [opening, teach reply, AD5,
    # read-back reply, ...]. The situations start from its prefixes.
    after_teach, after_read_back = msgs[:2], msgs[:4]
    situations = [
        ("opening", [H(content=OPENING)], {}, None),
        ("good answer", [*after_teach, H(content=AD5)], ASKED, None),
        ("weak answer", [*after_teach, H(content=WEAK)], ASKED, None),
        ("Belt clicks Confirm", [*after_read_back, H(content="Confirm")], _awaiting(), "confirm"),
        ('Belt types "yes, that\'s right"', [*after_read_back, H(content=CONFIRM)], _awaiting(), None),
        ("Belt types a correction", [*after_read_back, H(content=CORRECT)], _awaiting(), None),
        ("Belt clicks Change", [*after_read_back, H(content="Change")], _awaiting(), "change"),
        ('"where do we stand?"', [*after_teach, H(content=WHERE)], ASKED, None),
    ]
    out: list[dict] = []
    for name, messages, fs, action in situations:
        if name in skip:
            continue
        for run in range(1, runs + 1):
            before = len(CALLS)
            r = await _one_run(case_id, messages, _config(case_id), fs, action)
            rec = {"part": "B", "situation": name, "run": run, **r,
                   "model_calls": [c["kind"] for c in CALLS[before:]]}
            _write(jsonl, rec)
            out.append(rec)
            print(f"B [{name}] run {run}: move={r['move']} field={r['field']} "
                  f"fallback={r['fallback']} tools={r['tools']} calls={len(CALLS)}")
    return out


# ══ diagnose — the challenge loop, the grader-feedback hypothesis first ═════

#: The prior reply's feedback in the "feedback" arm: the criterion the old
#: loop's section 5 carried, verbatim from the rubric.
METHODOLOGY_FAIL = {"grader": {
    "status": "fail", "move": "teach",
    "criteria_failed": ["Coach must reference methodology when guiding (not just opinion)"],
    "feedback": ["Cite the methodology behind the business case"],
    "failed": [{"criterion": "Coach must reference methodology when guiding (not just opinion)",
                "feedback": "Cite the methodology behind the business case"}]},
    "coherence": {"coherent": True, "reason": ""}}


ARMS: tuple[str, ...] = ("feedback", "no feedback")


async def _diagnose(case_id: str, runs: int, jsonl: Path) -> list[dict]:
    """The weak-answer challenge, two arms: the teach reply carrying a failed
    "reference methodology" verdict in section 5, and carrying none."""
    from langchain_core.messages import HumanMessage as H
    from backend.phases import moves
    msgs = await _history(case_id)
    teach_reply = msgs[1].model_copy(deep=True)
    out: list[dict] = []
    for arm in ARMS:
        kw = dict(teach_reply.additional_kwargs)
        kw.pop(moves.QUALITY_FEEDBACK_KEY, None)
        if arm == "feedback":
            kw[moves.QUALITY_FEEDBACK_KEY] = METHODOLOGY_FAIL
        reply = teach_reply.model_copy(update={"additional_kwargs": kw})
        for run in range(1, runs + 1):
            before = len(CALLS)
            r = await _one_run(case_id, [msgs[0], reply, H(content=WEAK)], _config(case_id), ASKED)
            rec = {"part": "diagnose", "arm": arm, "run": run, **r,
                   "model_calls": [c["kind"] for c in CALLS[before:]]}
            _write(jsonl, rec)
            out.append(rec)
            print(f"D [{arm}] run {run}: move={r['move']} fallback={r['fallback']} "
                  f"coach_calls={r['coach_calls']} tools={r['tools']} calls={len(CALLS)}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True)
    ap.add_argument("--max-calls", type=int, default=120)
    ap.add_argument("--runs", type=int, default=3)
    ap.add_argument("--case", help="use this case; part A is skipped")
    ap.add_argument("--skip", action="append", default=[], help="a part-B situation already run")
    ap.add_argument("--arm", action="append", help="diagnose only these arms")
    ap.add_argument("--diagnose", action="store_true",
                    help="the challenge-loop A/B only (needs --case)")
    args = ap.parse_args()

    started = time.time()
    _tracing_off()
    _count_model_calls(args.max_calls)
    from fastapi.testclient import TestClient
    from backend.app import app

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now(dt.timezone.utc)
    jsonl = out / f"move_proof_661_{stamp:%Y%m%dT%H%M%S}.jsonl"
    summary: dict[str, Any] = {"started": stamp.isoformat()}
    runs: list[dict] = []
    try:
        if args.case:
            case_id = args.case
        else:
            with TestClient(app) as client:
                case_id = part_a(client, jsonl)["case_id"]
        summary["case_id"] = case_id
        _stand_down_judges()
        if args.diagnose:
            global ARMS
            ARMS = tuple(args.arm or ARMS)
            runs = asyncio.run(_diagnose(case_id, args.runs, jsonl))
        else:
            runs = asyncio.run(_part_b(case_id, args.runs, jsonl, tuple(args.skip)))
    except CapReached as exc:
        summary["stopped"] = str(exc)
        print(f"STOP: {exc}")
    summary.update({"model_calls": len(CALLS),
                    "by_kind": {k: sum(c["kind"] == k for c in CALLS)
                                for k in sorted({c["kind"] for c in CALLS})},
                    "fallbacks": sum(r.get("fallback", False) for r in runs),
                    "langsmith_sends": len(SENDS), "record": str(jsonl)})
    _write(jsonl, {"part": "summary", **summary})
    print(json.dumps(summary, indent=1, default=str))
    _time_it(started, "diagnose" if args.diagnose else "proof", len(CALLS))
    return 0 if not SENDS else 3


def _time_it(started: float, what: str, calls: int) -> None:
    """Rule (g) — the live-model minutes, measured by the run itself."""
    import importlib.util
    path = Path(__file__).resolve().parents[2] / ".claude" / "hooks" / "timing.py"
    spec = importlib.util.spec_from_file_location("timing", path)
    if spec is None or spec.loader is None:
        return
    timing = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(timing)
    timing.append({"kind": "live_model_calls", "what": f"6.61 {what}",
                   "seconds": round(time.time() - started, 1), "model_calls": calls})


if __name__ == "__main__":
    sys.exit(main())
