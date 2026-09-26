"""R3's repeated-run test, on the LIVE planner model — Define requirements v2, part 2.

Founder requirement R3 (`docs/requirements/define.md`): every Belt answer passes
a validation layer BEFORE the coach model — the planner's one judgment
(`nodes_common._judge`) against the element's acceptance criteria. This runs
that judgment, unchanged, FIVE times on each of two business cases:

    proposes-a-solution   names the gap AND a fix  -> challenged, `no-cause-no-fix`, 5 of 5
    all-five-elements     what, where-when, baseline, cost, no speculation -> read back, 5 of 5

OUTSIDE PYTEST, ON PURPOSE, like `define_runthrough.py` (which calls this
first, so the integrator's re-run refreshes both records): real model calls,
tracing OFF, every call counted and capped. The record goes to
`docs/runthrough/validation_repeat_<stamp>.json`, bound to the product source;
`backend/tests/test_define_runthrough.py` reads it.

    cd agent-improve; python -m scripts.validation_repeat          # 10 calls, cap 12
"""
from __future__ import annotations

import asyncio
import datetime as dt
import json
import sys
from pathlib import Path
from typing import Any

OUT_DIR = Path(__file__).resolve().parents[1] / "docs" / "runthrough"
RUNS = 5
#: Two business cases for the same project (the run-through's Belt).
CASES: dict[str, str] = {
    "proposes-a-solution": (
        "From January to June 2026, 23% of supplier invoices at our three hospital "
        "sites were paid after their 30-day terms, costing about £62,000 a year in "
        "interest and lost discounts. The fix is to buy an automated invoice-matching "
        "tool and hire a second approver."),
    "all-five-elements": (
        "From January to June 2026, 23% of supplier invoices at our three hospital "
        "sites were paid after their 30-day terms, against our 30-day policy. It cost "
        "about £62,000 last year in late-payment interest and lost early-payment "
        "discounts, and two key suppliers put us on stop."),
}


def _product_hash() -> str:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools" / "control_board"))
    import features
    return features.product_hash()


async def _judge_all() -> list[dict[str, Any]]:
    from backend.phases.nodes_common import _judge
    state: Any = {"phase_context": "Define for a finance project: supplier invoices paid late "
                                    "at three hospital sites; Belt Priya Shah, Green Belt."}
    runs = []
    for case, text in CASES.items():
        for i in range(1, RUNS + 1):
            j = await _judge("define", state, "business_case", "", text, "no")
            move = {"insufficient": "challenge", "sufficient": "read_back"}.get(j.verdict, "respond")
            runs.append({"case": case, "run": i, "verdict": j.verdict, "move": move,
                         "failed_criterion": j.failed_criterion, "reason": j.reason})
            print(f"  {case} #{i}: {j.verdict} {j.failed_criterion or ''} — {j.reason}")
    return runs


def run(write: bool = True) -> dict[str, Any]:
    """The five-by-two judgment; writes the record when `write`."""
    runs = asyncio.run(_judge_all())
    rec = {"kind": "validation_repeat", "requirement": "R3", "runs_per_case": RUNS,
           "product_hash": _product_hash(),
           "at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"), "runs": runs}
    if write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
        path = OUT_DIR / f"validation_repeat_{stamp}.json"
        path.write_text(json.dumps(rec, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"record: {path.name}")
    return rec


def main() -> int:
    from scripts.coaching_proof_656 import _tracing_off
    from scripts.move_proof_661 import CALLS, _count_model_calls
    _tracing_off()
    _count_model_calls(2 * RUNS + 2)
    run()
    print(f"model calls: {len(CALLS)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
