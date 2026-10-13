"""Founder ruling 2026-10-12 (quality stop, item 2): the offline evaluation set of the two per-turn judges.

From the live runs' own records — each run's case checkpoints (the turn's Belt message, the reply the
Belt received, and step_log's coherence and coaching-grader entries) and the run's coach-input log
(the FIRST reply of a re-asked turn, the one the judge actually saw) — it picks about 30 coaching
turns: every coherence rejection, every grader fail, then accepted turns spread over the moves. It
writes them to `evals/define/judge_turns.json`, each with what the judges were given, so
`scripts/judge_replay.py` can replay the judges offline. Labels are the founder's, kept apart in
`evals/define/judge_labels.json`.

    cd agent-improve; python -m scripts.judge_eval_set --inputs <run stamp>=<coach-input .jsonl> ...
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

OUT = Path(__file__).resolve().parents[1] / "evals" / "define" / "judge_turns.json"
RECORDS = Path(__file__).resolve().parents[1] / "docs" / "runthrough"
#: The runs the ruling names, and their record files (a failed run keeps its `failed_` record).
RUNS = ("20261012T124425", "20261012T132229", "20261012T134606", "20261012T140839")
#: The labels of a reply's blocks, as the judges are shown them (coherence._REPLY_BLOCKS).
BLOCKS = (("EXPLANATION", "explanation"), ("EXAMPLE - an illustration, not the Belt's data", "example"),
          ("QUESTION TO THE BELT", "prompt"))


def _record(stamp: str) -> list[dict[str, Any]]:
    for name in (f"define_runthrough_{stamp}.json", f"failed_define_runthrough_{stamp}.json"):
        if (RECORDS / name).exists():
            return json.loads((RECORDS / name).read_text(encoding="utf-8"))
    raise FileNotFoundError(stamp)


def _text(content: Any) -> str:
    if isinstance(content, str):
        return content
    return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in content or [])


def _coach_text(message: str, blocks: dict[str, Any]) -> str:
    parts = [message]
    for label, key in BLOCKS:
        if str(blocks.get(key) or "").strip():
            parts.append(f"[{label}] {str(blocks[key]).strip()}")
    return "\n\n".join(parts)


#: "Returning structured response: message='...' explanation='...' ..." — the tool message ToolStrategy
#: writes for the coach's structured reply; its fields are Python string literals.
_FIELD = re.compile(r"(\w+)=('(?:[^'\\]|\\.)*'|\"(?:[^\"\\]|\\.)*\")")


def _first_reply(inputs: dict[int, Any], n: int) -> str | None:
    """A re-asked turn's first reply — the one the judge rejected. It is the structured reply ToolStrategy
    returned before the re-ask's feedback: the `tool` message "Returning structured response: …" in the
    re-ask call's input (the AI message beside it is an empty tool call). Fixed 2026-10-13: the first version
    took the last AI message WITH text, which is the previous turn's reply."""
    import ast
    calls = (inputs.get(n) or {}).get("coach_inputs") or []
    for call in calls[1:]:
        tools = [m for m in call if m.get("type") == "tool"
                 and any(str(b).startswith("Returning structured response:") for b in m.get("blocks") or [])]
        if tools:
            text = next(str(b) for b in tools[-1]["blocks"] if str(b).startswith("Returning structured response:"))
            fields = {k: ast.literal_eval(v) for k, v in _FIELD.findall(text)}
            if fields.get("message"):
                return _coach_text(str(fields["message"]), fields)
    return None


def turns_of(stamp: str, inputs_path: Path | None) -> list[dict[str, Any]]:
    from backend.tests import test_capability_rows as C
    record = _record(stamp)
    summary = next(x for x in record if x.get("kind") == "summary")
    by_belt: dict[str, list[dict[str, Any]]] = {}
    for t in (x for x in record if x.get("kind") == "turn"):
        by_belt.setdefault(str(t.get("belt") or ""), []).append(t)
    inputs = ({x["n"]: x for x in (json.loads(l) for l in inputs_path.read_text(encoding="utf-8").splitlines()
                                   if l.strip())} if inputs_path else {})
    out: list[dict[str, Any]] = []
    for final in C._all_subgraph_finals(C._checkpointer(), summary["case_id"]):
        values = final["values"]
        log = [e for e in values.get("step_log") or [] if isinstance(e, dict)]
        coh = next((e for e in log if e.get("node") == "coherence"), None)
        if coh is None:
            continue
        grade = next((e for e in log if e.get("node") == "coaching_grader"), None)
        messages = list(values.get("messages") or [])
        belt = next((_text(m.content) for m in reversed(messages) if getattr(m, "type", "") == "human"), "")
        ai = next((m for m in reversed(messages) if getattr(m, "type", "") == "ai" and _text(m.content).strip()), None)
        if ai is None:
            continue
        kw = ai.additional_kwargs or {}
        sent = _coach_text(_text(ai.content), kw.get("coaching_blocks") or {})
        rec = by_belt[belt].pop(0) if by_belt.get(belt) else None
        n = rec["n"] if rec else None
        reasked = "asked again" in str(coh.get("reask") or "")
        judged = (_first_reply(inputs, n) if reasked and n else None) or sent
        out.append({
            "id": f"{stamp}#{n}", "run": stamp, "case_id": summary["case_id"], "turn": n,
            "move": (grade or {}).get("move") or (rec or {}).get("move"),
            "script_step": coh.get("script_step"), "belt": belt,
            "reply_judged": judged, "reply_sent": sent, "reasked": reasked,
            "coherence": {k: coh.get(k) for k in ("coherent", "is_conclusive", "is_parroting", "on_topic",
                                                  "reason", "degraded", "grader_skipped", "reask")},
            "grader": ({k: grade.get(k) for k in ("status", "criteria_failed", "feedback", "move")}
                       if grade else None),
        })
    return out


def _round_robin(pool: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    """Up to `n` turns from `pool`, one move at a time, spread over each move's turns."""
    by_move: dict[str, list[dict[str, Any]]] = {}
    for t in pool:
        by_move.setdefault(str(t["move"]), []).append(t)
    out: list[dict[str, Any]] = []
    while len(out) < n and any(by_move.values()):
        for move in sorted(by_move):
            if by_move[move] and len(out) < n:
                out.append(by_move[move].pop(len(by_move[move]) // 2))
    return out


#: Founder ruling 2026-10-12 asked for about 30 turns: every coherence rejection, every grader fail,
#: and accepted turns. The four runs hold 22 rejections and 57 grader fails (the grader failed 57 of the
#: 111 turns it graded), so every rejection is kept, the grader fails are SAMPLED across the moves, and
#: accepted turns (both judges passed) are added — 40 turns, reported as such.
FAILS_SAMPLED = 12
ACCEPTED = 6


def pick(turns: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Every coherence rejection; FAILS_SAMPLED grader fails and ACCEPTED accepted turns, by move."""
    rejected = [t for t in turns if not t["coherence"]["coherent"]]
    failed = [t for t in turns if t["coherence"]["coherent"] and (t["grader"] or {}).get("status") == "failed"]
    accepted = [t for t in turns if t["coherence"]["coherent"] and (t["grader"] or {}).get("status") == "pass"]
    return rejected + _round_robin(failed, FAILS_SAMPLED) + _round_robin(accepted, ACCEPTED)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    ap = argparse.ArgumentParser()
    ap.add_argument("--inputs", nargs="*", default=[], help="<run stamp>=<coach-input .jsonl>")
    args = ap.parse_args()
    paths = dict(a.split("=", 1) for a in args.inputs)
    turns = [t for s in RUNS for t in turns_of(s, Path(paths[s]) if s in paths else None)]
    chosen = pick(turns)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"about": __doc__.split("\n\n")[0], "runs": list(RUNS), "turns": chosen},
                              indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    rej = sum(not t["coherence"]["coherent"] for t in chosen)
    fails = sum((t["grader"] or {}).get("status") == "failed" for t in chosen)
    print(f"{len(turns)} judged turns in {len(RUNS)} runs; picked {len(chosen)}: {rej} coherence rejections, "
          f"{fails} grader fails -> {OUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
