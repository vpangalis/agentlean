"""Founder ruling 2026-10-13, item 4 — coherence option B, DESIGN ONLY (nothing switches): could layer 2a's
three questions be answered in code? On the evaluation set's 40 turns, each code check's verdict beside
the recorded model verdict, and — once the founder's labels are in — beside `reply_good`.

The checks (each a pure function of the reply, the Belt's message and the move code decided):
  real       the reply has text (message or a block) — never empty
  asks       the reply asks something: a [QUESTION TO THE BELT] block or a question mark — not required on
             a store of the LAST element or a reply that ends the phase (it has nothing left to ask)
  parroting  the share of the reply's content words that come from the Belt's message stays under
             PARROT_SHARE — not checked on a read-back or a store (they must restate the Belt's words)
  on_phase   the reply names the phase, or a Define element (all the words of its name or its field) — the one in focus
             or any other: a store names the element it stored, which the step has moved past

    cd agent-improve; python -m scripts.coherence_option_b
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

EVALS = Path(__file__).resolve().parents[1] / "evals" / "define"
PARROT_SHARE = 0.6
RESTATING = {"read_back", "store_and_advance"}
STOP = set("""a an the and or but of to in on for with at by from as is are was were be been it its this that
these those you your we our i me my they their he she them his her not no do does did have has had will would can
could should what which who how when where why so if then than there here about into over under up down out
""".split())


def _words(text: str) -> list[str]:
    return [w for w in re.findall(r"[a-z0-9£€%]+", (text or "").lower()) if w not in STOP and len(w) > 2]


def checks(turn: dict[str, Any]) -> dict[str, bool]:
    from backend.core import guard_messages
    reply, belt, move = turn["reply_judged"], turn["belt"], turn["move"]
    field = (turn.get("script_step") or {}).get("field") or ""
    words = _words(reply)
    from_belt = set(_words(belt))
    share = sum(w in from_belt for w in words) / len(words) if words else 1.0
    from backend.phases.define.schema import DEFINE_FIELD_ORDER
    last_store = move == "store_and_advance" and ("is now confirmed" in reply or "Define report" in reply)
    # Any Define element counts, not only the one in focus: a store names the element it stored, which the
    # script step has already moved past (fixed 2026-10-13 — 132229#33 was rejected for naming the SIPOC).
    fields = [f for f in (*DEFINE_FIELD_ORDER, field) if f]
    elements = {guard_messages.element_name("define", f).lower() for f in fields} | {f.replace("_", " ") for f in fields}
    on_phase = "define" in reply.lower() or any(
        all(w in reply.lower() for w in _words(e)) for e in elements if _words(e))
    return {
        "real": bool(reply.strip()),
        "asks": "[QUESTION TO THE BELT]" in reply or "?" in reply or last_store,
        "not_parroting": move in RESTATING or share < PARROT_SHARE,
        "on_phase": on_phase,
    }


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    turns = json.loads((EVALS / "judge_turns.json").read_text(encoding="utf-8"))["turns"]
    labels_path = EVALS / "judge_labels.json"
    labels = json.loads(labels_path.read_text(encoding="utf-8")) if labels_path.exists() else {}
    rows = []
    for t in turns:
        c = checks(t)
        rows.append({"id": t["id"], "move": t["move"], "model_accepts": bool(t["coherence"]["coherent"]),
                     "code_accepts": all(c.values()), "failed_checks": [k for k, v in c.items() if not v],
                     "reply_good": (labels.get(t["id"]) or {}).get("reply_good")})
    agree = sum(r["model_accepts"] == r["code_accepts"] for r in rows)
    print(f"model vs code: agree on {agree} of {len(rows)}; model rejects {sum(not r['model_accepts'] for r in rows)}, "
          f"code rejects {sum(not r['code_accepts'] for r in rows)}")
    for r in rows:
        if not r["code_accepts"] or not r["model_accepts"]:
            print(f"  {r['id']:22} {r['move']:18} model {'accept' if r['model_accepts'] else 'REJECT'}  "
                  f"code {'accept' if r['code_accepts'] else 'REJECT ' + ','.join(r['failed_checks'])}"
                  + (f"  label {r['reply_good']}" if r["reply_good"] is not None else ""))
    labelled = [r for r in rows if r["reply_good"] is not None]
    if labelled:
        for who in ("model", "code"):
            good = [r for r in labelled if r["reply_good"]]
            bad = [r for r in labelled if not r["reply_good"]]
            fr = sum(not r[f"{who}_accepts"] for r in good) / len(good) if good else None
            fa = sum(r[f"{who}_accepts"] for r in bad) / len(bad) if bad else None
            print(f"{who}: false-reject {fr}, false-accept {fa} on {len(labelled)} labelled")
    (EVALS / "coherence_option_b.json").write_text(json.dumps(rows, indent=1, ensure_ascii=False) + "\n",
                                                   encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
