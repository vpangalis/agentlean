"""DEF-200 — the Define welcome, assembled by the server in code (W3; G-201).

No model call. Built from two sources only: the phase state (which elements are confirmed, with their values, and
which are open — the progress view's own `moves.element_rows`) and the welcome's owner in code,
`phases/define/criteria.py` (the five phases' one-line purposes, how Define is worked and how it ends — the founder's
text, never parsed from the skill: B7, founder ruling 2026-10-27, item 4; the skill's `[OPENING]` block is generated
from the same owner). Served on `GET /cases/{id}` while the case is in Define, for a fresh case and for every return;
the page lays it out in blocks (`ui/index.html` `welcomeHtml`).
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from backend.core import guard_messages
from backend.phases import moves
from backend.phases.define import criteria as define_criteria


def opening() -> tuple[tuple[tuple[str, str], ...], str]:
    """(the five phases as (name, purpose), how Define is worked) — the owner's welcome (B7)."""
    return define_criteria.PHASES, define_criteria.HOW_DEFINE_IS_WORKED.replace("**", "")


def value_text(value: Any) -> str:
    """A confirmed value as plain text, whole: a list item by item, a structured value by its parts."""
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, list):
        return "; ".join(t for t in (value_text(v) for v in value) if t)
    if isinstance(value, dict):
        return ", ".join(t for t in (value_text(v) for v in value.values()) if t)
    return "" if value is None else str(value)


def welcome(name: str, artifacts: dict[str, Any], field_status: dict[str, dict[str, Any]]) -> dict[str, Any]:
    """The welcome's blocks: the greeting's name, the phases (Define current), how Define is worked, the confirmed
    elements with their values, the open ones, and the element to work on next."""
    rows = moves.element_rows("define", artifacts, field_status,
                              lambda f: guard_messages.element_name("define", f))
    confirmed = [{"n": r["n"], "name": r["name"], "value": value_text(artifacts.get(r["field"]))}
                 for r in rows if r["status"] == "confirmed"]
    open_ = [{"n": r["n"], "name": r["name"], "status": r["status"]} for r in rows if r["status"] != "confirmed"]
    nxt = next((r for r in rows if r["status"] == "current"), None) or (open_[0] if open_ else None)
    phases, how = opening()
    # R-A (DEF-267, founder test 2026-10-27 #9): on a fresh case the welcome flows straight into the first element's
    # card (R-C) — the Belt answers it, never types "let's start". Once the element is taught, its card is in the chat.
    card = None
    if nxt is not None and not confirmed and (field_status.get(nxt["field"]) or {}).get("status") in (
            None, moves.NOT_TAUGHT):
        from backend.phases.define.templates import teaching_card
        card = teaching_card(nxt["field"], artifacts, field_status)
    return {"name": name, "returning": bool(confirmed),
            "phases": [{"name": p, "line": line, "current": p.lower() == "define"} for p, line in phases],
            "how": how, "confirmed": confirmed, "open": open_,
            "next": {"n": nxt["n"], "name": nxt["name"]} if nxt else None,
            **({"card": card} if card else {})}


#: The skill's internal references, left out of team-facing text: "(section 6)", "(requirement R6)".
_INTERNAL = re.compile(r"\s*\((?:section \d+|requirement [A-Z]\d+\w*)\)")


@lru_cache(maxsize=1)
def overview() -> dict[str, Any]:
    """DEF-214 (W1): the Define overview — the thirteen elements (numbered and named as in the sidebar, each with the
    first sentence of what it is, from the skill), how Define is worked and how it ends (the owner's, B7), without the
    skill's internal references."""
    from backend.middleware.skills import teaching_blocks
    ends = " ".join(_INTERNAL.sub("", "\n".join(define_criteria.HOW_DEFINE_ENDS)).replace("**", "").split())
    elements = []
    for n, (field, _fields) in enumerate(moves.positions("define"), start=1):
        what = str(teaching_blocks("define", field).get("explanation") or "")
        elements.append({"n": n, "name": guard_messages.element_name("define", field),
                         "what": (what.split(". ")[0].rstrip(".") + ".") if what else ""})
    return {"elements": elements, "how": opening()[1], "ends": ends}


#: G-258: the screen's tool briefings for Define's 5W2H and SIPOC, keyed by the page's tool name.
BRIEFED: dict[str, str] = {"5W2H problem statement": "problem_statement", "SIPOC diagram": "process_map_sipoc"}
#: A SIPOC column's label where it is not its key with the underscore dropped.
_SIPOC_LABELS = {"process_steps": "Process steps", "process_metrics": "Measures"}
_PAGE_REF = re.compile(r"\s*\((?:p\.|R\d)[^)]*\)")


def _first_sentence(text: str) -> str:
    return (text.split(". ")[0].rstrip(".") + ".") if text else ""


def briefings() -> dict[str, dict[str, Any]]:
    """G-258: the 5W2H and SIPOC briefings the page shows, built from the
    skill — what the element is and why it matters, how each part is formulated, the skill's own ask and its
    worked example — and the SIPOC's criteria from their owner (B7), so the screen teaches exactly what is graded.
    Shaped as the page's briefing card reads it."""
    import json

    from backend.middleware.skills import SKILLS_ROOT, element_text, show_table
    from backend.phases.define.schema import SIPOC_KEYS
    from backend.phases.define.visuals import SIPOC_EXAMPLE
    out: dict[str, dict[str, Any]] = {}
    for tool, field in BRIEFED.items():
        show = element_text("define", field, "Show")
        card: dict[str, Any] = {"tagline": _first_sentence(element_text("define", field, "What it is")),
                                "why": element_text("define", field, "Why it matters"),
                                "firstQuestion": element_text("define", field, "Ask")}
        if field == "problem_statement":
            rows = show_table("define", field)
            card["steps"] = [f"{r[0]} — {r[1]}." for r in rows if len(r) > 1]
            card["exampleFields"] = [{"q": r[0], "a": r[2]} for r in rows if len(r) > 2]
            composed = next((ln for ln in show.splitlines() if "composed from it" in ln), "")
            card["exampleSummary"] = composed.split(":**", 1)[-1].strip(" *\"“”") if composed else ""
        else:
            crit = dict(define_criteria.criteria(field))
            how = next((ln for ln in show.splitlines() if ln.startswith("How each part is formulated")), "")
            card["steps"] = [_PAGE_REF.sub("", crit[c]).strip().capitalize() + "."
                             for c in (define_criteria.START_TO_END, define_criteria.ALL_SIX) if c in crit] \
                + ([how] if how else [])
            example = json.loads((SKILLS_ROOT / "dmaic-define-phase" / SIPOC_EXAMPLE).read_text(encoding="utf-8"))

            def words(v: Any) -> str:
                if isinstance(v, list):
                    return (" → " if v and isinstance(v[0], dict) else ", ").join(
                        str(x.get("name") if isinstance(x, dict) else x) for x in v)
                return str(v or "")
            card["exampleFields"] = [{"q": _SIPOC_LABELS.get(k, k.capitalize()), "a": words(example.get(k))}
                                     for k in SIPOC_KEYS]
            card["exampleSummary"] = show.split("drawn below:", 1)[-1].splitlines()[0].strip().rstrip(".").capitalize() \
                + "." if "drawn below:" in show else ""
        out[tool] = card
    return out
