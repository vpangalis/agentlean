"""Grader v2 — the coaching evaluator (ADR-0084, founder rulings 2026-10-14).

It judges the composed reply the Belt would see — after every code check of the executor (G-168, G-170 to
G-175) — on four criteria, C1 to C4 (`prompts.GRADER_V2_CRITERIA`), each with a definition and a pass and a
fail example from the founder's labels. Which criteria a move is judged on is the explicit table
`MOVE_CRITERIA`, never a keyword in a criterion's text. The model writes, per criterion, its reasoning, then
a sentence quoted from the reply, then the verdict — pass, fail or not applicable. A fail whose quoted
sentence is not in the reply is recorded as not checked, never as a fail.

The old rubric's two lines outside C1–C4 are code checks here (ADR-0084): no external address, and on the
phase's topic. A failed code check fails the reply as a failed criterion does.

Module-level functions only (§2); the schemas are `validation/schemas.py::GraderV2Verdict`, `CriterionCheck`.
"""
from __future__ import annotations

import json
import re
from typing import Any, Optional

from backend.core.llm import get_llm
from backend.core.prompts import GRADER_V2_CRITERIA, GRADER_V2_PROMPT
from backend.validation.schemas import GraderV2Verdict

#: ADR-0084 decision 4 (C2 on read-backs and C1 on stores confirmed by the founder, 2026-10-14).
MOVE_CRITERIA: dict[str, tuple[str, ...]] = {
    "teach": ("C1", "C3", "C4"),
    "challenge": ("C2", "C3", "C4"),
    "read_back": ("C2", "C3", "C4"),
    "store_and_advance": ("C1", "C4"),
    "respond": ("C3", "C4"),
    "offer_park": ("C4",),
}
#: The verdict a criterion gets when it was not asked about, or its fail could not be tied to the reply.
NOT_APPLICABLE, NOT_CHECKED = "not_applicable", "not checked"
_ADDRESS = re.compile(r"https?://|\bwww\.", re.I)
_WORD = re.compile(r"[a-z0-9]+")


def criteria_for(move: Optional[str]) -> tuple[str, ...]:
    return MOVE_CRITERIA.get(move or "", ())


def _words(text: str) -> list[str]:
    return [w for w in _WORD.findall((text or "").lower()) if len(w) > 2]


def code_checks(phase: str, reply: str) -> list[dict[str, Any]]:
    """ADR-0084: the old rubric's two lines outside C1–C4, in code. `passed` per check."""
    from backend.core import guard_messages
    from backend.phases.gate_registry import GATE_SPECS
    fields = list(GATE_SPECS[phase].tier_1) if phase in GATE_SPECS else []
    names = {guard_messages.element_name(phase, f).lower() for f in fields} | {f.replace("_", " ") for f in fields}
    low = (reply or "").lower()
    on_phase = phase in low or any(all(w in low for w in _words(n)) for n in names if _words(n))
    address = _ADDRESS.search(reply or "")
    return [{"check": "no external address", "passed": address is None,
             "detail": address.group(0) if address else ""},
            {"check": "on the phase's topic", "passed": on_phase,
             "detail": "" if on_phase else "names neither the phase nor any of its elements"}]


def _norm(text: str) -> str:
    return " ".join(re.sub(r"[“”\"'‘’*_`]", "", text or "").lower().split())


def context_text(confirmed: dict[str, Any], earlier: list[str]) -> str:
    rows = [f"- {k}: {v if isinstance(v, str) else json.dumps(v, ensure_ascii=False, default=str)}"[:400]
            for k, v in confirmed.items() if k != "computation_results" and v not in (None, "", [], {})]
    rows += [f"- the Belt said: {s[:400]}" for s in earlier if str(s).strip()]
    return "\n".join(rows[-24:]) or "(nothing yet)"


async def grade(phase: str, move: Optional[str], element: str, acceptance: list[str], reply: str, belt: str,
                confirmed: dict[str, Any], earlier: list[str], model: Any = None) -> dict[str, Any]:
    """One grading call on the composed `reply`. Returns the record for step_log: per criterion its verdict
    (pass | fail | not_applicable | not checked), reasoning and evidence; the code checks; and `passed` —
    no code check failed and no applicable criterion failed."""
    asked = criteria_for(move)
    checks = code_checks(phase, reply)
    result: dict[str, Any] = {"move": move, "element": element, "asked": list(asked), "code": checks}
    verdicts: dict[str, dict[str, Any]] = {c: {"criterion": c, "verdict": NOT_APPLICABLE, "reasoning": "not "
                                               "judged on this move (MOVE_CRITERIA)", "evidence": ""}
                                           for c in GRADER_V2_CRITERIA}
    if asked:
        prompt = GRADER_V2_PROMPT.format(
            move=move, element=element or "(none)",
            acceptance="\n".join(f"- {a}" for a in acceptance) or "(none given)",
            context=context_text(confirmed, earlier), belt=belt[:2000], reply=reply[:6000],
            criteria="\n\n".join(GRADER_V2_CRITERIA[c] for c in asked))
        llm = (model or get_llm("grader")).with_structured_output(GraderV2Verdict)
        out = GraderV2Verdict.model_validate(await llm.ainvoke(prompt))
        shown = _norm(reply)
        for c in out.criteria:
            if c.criterion not in asked:
                continue
            verdict: str = c.verdict
            if verdict == "fail" and (not c.evidence.strip() or _norm(c.evidence) not in shown):
                verdict = NOT_CHECKED          # ADR-0084 decision 6: a fail must quote the reply
            verdicts[c.criterion] = {"criterion": c.criterion, "verdict": verdict, "reasoning": c.reasoning,
                                     "evidence": c.evidence}
    result["criteria"] = [verdicts[c] for c in GRADER_V2_CRITERIA]
    result["passed"] = all(x["passed"] for x in checks) and not any(
        v["verdict"] == "fail" for v in verdicts.values())
    return result


__all__ = ["MOVE_CRITERIA", "NOT_APPLICABLE", "NOT_CHECKED", "criteria_for", "code_checks", "context_text",
           "grade"]
