"""Item 18 'How-to questions answered' (G-211) — the how-to eval set, run live.

Each case of evals/define/howto_turns.json starts from the saved case define_all_confirmed (schema 8, loaded
through the migrations) with every element from `element` on removed, so `element` is the current one. A first
POST /ask ("Next, please.") lets the coach teach and ask the element — the how-to question then comes after an
earlier coach turn, as on IMPR-2026-A99 (founder ruling 2026-10-16) — and a second carries the question. Recorded per case: the planner's verdict and move, the reply,
whether the reply asks the element's question again, and whether anything was stored.

    cd agent-improve; python -m scripts.howto_replay --scratch <dir>
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import uuid
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[1]
SET = PROJECT / "evals" / "define" / "howto_turns.json"
OUT = PROJECT / "evals" / "define"


def _case_at(element: str, title: str) -> str:
    """A saved case with every element before `element` confirmed, written as saved (schema 8)."""
    from azure.storage.blob import BlobServiceClient
    from backend.core.config import settings
    from backend.phases.moves import positions
    from backend.storage import blob
    data = json.loads((PROJECT / "scripts" / "saved_cases" / "define_all_confirmed.v8.json").read_text(encoding="utf-8"))
    data.pop("_saved", None)
    walk = positions("define")
    later = {f for i, (field, fs) in enumerate(walk) if i >= [x for x, _ in walk].index(element) for f in fs}
    if "benefits_analysis" in later:
        later.add("computation_results")
    structured = data["phases"]["define"]["structured"]
    data["phases"]["define"]["structured"] = {k: v for k, v in structured.items() if k not in later}
    # As on IMPR-2026-A99: the element has been taught and asked; the Belt's question comes before an answer.
    data["phases"]["define"]["field_status"] = {element: {"status": "asked"}}
    case_id = f"IMPR-HOWTO-{uuid.uuid4().hex[:6].upper()}"
    data.update({"case_id": case_id, "title": title})
    box = BlobServiceClient.from_connection_string(settings.AZURE_BLOB_CONNECTION_STRING) \
        .get_container_client(settings.AZURE_BLOB_CONTAINER_IMPROVE)
    box.upload_blob(blob.case_path(case_id), json.dumps(data), overwrite=True)
    return case_id


def run(client: Any, only: str = "") -> list[dict[str, Any]]:
    from backend.middleware.skills import teaching_blocks
    from scripts.coaching_proof_656 import _latest_final
    out = []
    for c in json.loads(SET.read_text(encoding="utf-8"))["cases"]:
        if only and c["id"] != only:
            continue
        case_id = _case_at(c["element"], f"HOW-TO EVAL — {c['id']}")
        warm = client.post("/ask", json={"case_id": case_id, "phase": "define", "user": "howto-eval",
                                         "message": "Next, please."})
        earlier = (warm.json() if warm.status_code == 200 else {}).get("answer") or ""
        before = (client.get(f"/cases/{case_id}").json().get("phases") or {}).get("define", {}).get("structured") or {}
        r = client.post("/ask", json={"case_id": case_id, "phase": "define", "user": "howto-eval",
                                      "message": c["question"]})
        body = r.json() if r.status_code == 200 else {"detail": r.text[:300]}
        after = (client.get(f"/cases/{case_id}").json().get("phases") or {}).get("define", {}).get("structured") or {}
        final = _latest_final(case_id)
        planner = next((e for e in final.get("step_log") or [] if isinstance(e, dict) and e.get("node") == "planner"
                        and e.get("judgment")), {})
        ask = teaching_blocks("define", c["element"]).get("prompt", "")
        reply = " ".join(str(body.get(k) or "") for k in ("answer", "explanation", "prompt"))
        out.append({"id": c["id"], "element": c["element"], "question": c["question"], "http": r.status_code,
                    "earlier_coach_turn": earlier[:600], "opens_with_welcome": "welcome" in str(body.get("answer") or "")[:200].lower(),
                    "verdict": (planner.get("judgment") or {}).get("verdict"), "move": body.get("move"),
                    "answer": body.get("answer"), "prompt": body.get("prompt"),
                    "asks_again": bool(ask) and (ask[:40] in reply or c["element"].replace("_", " ") in reply.lower()),
                    "repeats_only_the_ask": str(body.get("answer") or "").strip()[:60] == ask.strip()[:60],
                    "stored_nothing": after == before,
                    # G-173 "The coach calculates numbers itself": the figures the check rejected this turn, if any.
                    "rejected_numbers": next((e.get("unsourced_numbers") for e in final.get("step_log") or []
                                              if isinstance(e, dict) and e.get("unsourced_numbers")), None)})
        print(f"{c['id']}: {out[-1]['verdict']} / {out[-1]['move']} · stored nothing {out[-1]['stored_nothing']}")
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--only", default="", help="one case id")
    args = ap.parse_args()
    from fastapi.testclient import TestClient
    from backend.app import app
    from scripts.coaching_proof_656 import _tracing_off
    from scripts.define_runthrough import _cost
    from scripts.move_proof_661 import CALLS, _count_model_calls, token_totals
    _tracing_off()
    _count_model_calls(90)                     # two turns per case
    with TestClient(app) as client:
        results = run(client, args.only)
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y%m%dT%H%M%S")
    record: dict[str, Any] = {"run": stamp, "cases": results, "model_calls": len(CALLS),
                              "cost": _cost(token_totals(CALLS))}
    path = OUT / f"howto_replay_{stamp}.json"
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    Path(args.scratch).mkdir(parents=True, exist_ok=True)
    print(f"record {path}; USD {record['cost'].get('usd')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
