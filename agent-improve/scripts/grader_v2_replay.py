"""Grader v2 against the founder's labels (ADR-0084 decision 8; founder ruling 2026-10-14).

Reads evals/define/coach_labelling_sheet.xlsx (the founder's reply_good and C1–C4 labels on the 22 distinct
replies of run 154211) and grades each distinct reply REPEATS times with `validation/grader_v2.grade`, built
as the node builds it: the move and element of the run's turn, the element's acceptance criteria, the Belt's
message and their earlier messages (from the run's record; the record keeps no confirmed values, so the case
so far is the Belt's earlier messages).

Per criterion, on the replies the founder labelled pass or fail where the move asks that criterion:
  repeatability   share of replies whose REPEATS verdicts all agree        (accept: >= 90%)
  false fails     founder pass, grader's majority fail / founder passes     (accept: <= 20%)
  false passes    founder fail, grader's majority pass / founder fails      (accept: <= 20%)
and, for the whole reply, the grader's pass against reply_good. "not checked" (a fail with no quote in the
reply) counts as a pass.

    cd agent-improve; python -m scripts.grader_v2_replay --model mini|4o [--repeats 5]
"""
from __future__ import annotations

import argparse
import asyncio
import collections
import json
import sys
import time
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
EVALS = PROJECT / "evals" / "define"
SHEET = EVALS / "coach_labelling_sheet.xlsx"
CRITERIA = ("C1", "C2", "C3", "C4")
SKIP_BELT = {"confirm", "next, please."}


def labels() -> dict[int, dict[str, Any]]:
    """The founder's labels per distinct reply (by run turn), from the first labelled row of each."""
    from openpyxl import load_workbook
    rows = list(load_workbook(SHEET, read_only=True)["Turns"].iter_rows(values_only=True))
    col = {str(h or "").split(" ")[0]: i for i, h in enumerate(rows[0])}
    out: dict[int, dict[str, Any]] = {}
    for r in rows[1:]:
        source = str(r[col["new"]] or "")
        if "#" not in source:
            continue
        n = int(source.split("#")[1])
        good = str(r[col["reply_good"]] or "").strip().lower()
        crit = {c: str(r[col[c]] or "").strip().lower() for c in CRITERIA}
        if not good and not any(crit.values()):
            continue
        out.setdefault(n, {"id": r[col["id"]], "run": source.split("#")[0],
                           "reply_good": {"yes": True, "no": False}.get(good), **crit,
                           "reply": r[col["coach"]]})
    return out


def turn_context(run: str, n: int) -> dict[str, Any]:
    record = json.loads((PROJECT / "docs" / "runthrough" / f"define_runthrough_{run}.json").read_text(encoding="utf-8"))
    turns = {int(x["n"]): x for x in record if isinstance(x, dict) and x.get("kind") == "turn"}
    t = turns[n]
    earlier = [str(turns[i].get("belt") or "") for i in sorted(turns) if i < n
               and str(turns[i].get("belt") or "").strip().lower() not in SKIP_BELT]
    field = t.get("field") or (t.get("reply") or {}).get("move_field")
    return {"move": t.get("move"), "field": field, "belt": str(t.get("belt") or ""), "earlier": earlier[-12:]}


def model_for(name: str) -> Any:
    from backend.core import llm
    if name == "mini":
        return llm.get_llm("grader")
    return llm._build_llm(llm.PREMIUM_TIER, llm.role_temperature("grader"), None, llm.ROLE_TIMEOUTS["grader"] * 2)


async def run(lab: dict[int, dict[str, Any]], model_name: str, repeats: int) -> dict[int, dict[str, Any]]:
    from backend.core import guard_messages
    from backend.middleware.skills import acceptance_criteria
    from backend.validation.grader_v2 import grade
    model = model_for(model_name)
    out: dict[int, dict[str, Any]] = {}
    for n, l in sorted(lab.items()):
        ctx = turn_context(l["run"], n)
        field = ctx["field"] or ""
        element = guard_messages.element_name("define", field) if field else ""
        acceptance = [text for _cid, text in acceptance_criteria("define", field)] if field else []
        runs = []
        for _ in range(repeats):
            try:
                runs.append(await grade("define", ctx["move"], element, acceptance, str(l["reply"] or ""),
                                        ctx["belt"], {}, ctx["earlier"], model=model))
            except Exception as exc:  # noqa: BLE001 — counted, never a crash
                runs.append({"error": repr(exc)[:200]})
        out[n] = {"label": l, "context": ctx, "runs": runs}
    return out


def _verdict(r: dict[str, Any], c: str) -> str:
    v = next(x["verdict"] for x in r["criteria"] if x["criterion"] == c)
    return "pass" if v == "not checked" else v


def analyse(out: dict[int, dict[str, Any]]) -> dict[str, Any]:
    per: dict[str, Any] = {}
    for c in CRITERIA:
        rows = []
        for n, o in out.items():
            ok = [r for r in o["runs"] if "error" not in r]
            if not ok or c not in ok[0]["asked"]:
                continue
            label = o["label"].get(c)
            vs = [_verdict(r, c) for r in ok]
            majority = collections.Counter(vs).most_common(1)[0][0]
            rows.append({"n": n, "label": label, "verdicts": vs, "majority": majority, "repeat": len(set(vs)) == 1})
        judged = [r for r in rows if r["label"] in ("pass", "fail")]
        passes = [r for r in judged if r["label"] == "pass"]
        fails = [r for r in judged if r["label"] == "fail"]
        ff = [r["n"] for r in passes if r["majority"] == "fail"]
        fp = [r["n"] for r in fails if r["majority"] == "pass"]
        rep = sum(r["repeat"] for r in rows) / len(rows) if rows else None
        per[c] = {"asked_on": len(rows), "labelled": len(judged),
                  "repeatability": round(rep, 2) if rep is not None else None,
                  "false_fail_rate": round(len(ff) / len(passes), 2) if passes else None, "false_fails": ff,
                  "false_pass_rate": round(len(fp) / len(fails), 2) if fails else None, "false_passes": fp,
                  "founder_na_where_asked": [r["n"] for r in rows if r["label"] == "n/a"],
                  "accepted": bool(rows) and rep is not None and rep >= 0.9
                  and (not passes or len(ff) / len(passes) <= 0.2) and (not fails or len(fp) / len(fails) <= 0.2)}
    whole = []
    for n, o in out.items():
        ok = [r for r in o["runs"] if "error" not in r]
        if ok and o["label"].get("reply_good") is not None:
            passed = collections.Counter(r["passed"] for r in ok).most_common(1)[0][0]
            whole.append((n, o["label"]["reply_good"], passed))
    good = [w for w in whole if w[1]]
    bad = [w for w in whole if not w[1]]
    return {"criteria": per,
            "whole_reply": {"labelled": len(whole),
                            "false_fail_rate": round(sum(not w[2] for w in good) / len(good), 2) if good else None,
                            "false_pass_rate": round(sum(w[2] for w in bad) / len(bad), 2) if bad else None},
            "errors": sum("error" in r for o in out.values() for r in o["runs"])}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", choices=("mini", "4o"), default="mini")
    ap.add_argument("--repeats", type=int, default=5)
    args = ap.parse_args()
    from scripts.coaching_proof_656 import _tracing_off
    from scripts.define_runthrough import _cost
    from scripts.move_proof_661 import CALLS, _count_model_calls, token_totals
    _tracing_off()
    _count_model_calls(1000)
    lab = labels()
    if not lab:
        print("no labels yet in", SHEET)
        return 1
    t0 = time.time()
    out = asyncio.run(run(lab, args.model, args.repeats))
    result: dict[str, Any] = {"model": args.model, "repeats": args.repeats, "replies": len(out),
                              "analysis": analyse(out), "seconds": round(time.time() - t0, 1),
                              "calls": len(CALLS), "cost": _cost(token_totals(CALLS)),
                              "raw": {str(k): v for k, v in out.items()}}
    path = EVALS / f"grader_v2_replay_{args.model}_{time.strftime('%Y%m%dT%H%M%S', time.gmtime())}.json"
    path.write_text(json.dumps(result, indent=1, ensure_ascii=False, default=str) + "\n", encoding="utf-8")
    print(json.dumps(result["analysis"], indent=1, ensure_ascii=False))
    print(f"seconds {result['seconds']}, calls {result['calls']}, cost {result['cost'].get('usd')}; record {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
