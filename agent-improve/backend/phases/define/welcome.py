"""DEF-200 — the Define welcome, assembled by the server in code (W3; G-201, founder findings 11 and 15).

No model call. Built from two sources only: the phase state (which elements are confirmed, with their values, and
which are open — the progress view's own `moves.element_rows`) and the skill's own `[OPENING]` block (the five
phases' one-line purposes and how Define is worked — the founder's text, never retyped here). Served on
`GET /cases/{id}` for a fresh case and for every return; the page lays it out in blocks (`ui/index.html`
`welcomeHtml`), replacing the browser's opener, its recap and the retired `/context` route.
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Any

from backend.core import guard_messages
from backend.middleware.skills import instructions
from backend.phases import moves

#: The skill's opening: `**[OPENING — the welcome]**` and its quoted lines.
_OPENING = re.compile(r"^\*\*\[OPENING[^\]]*\]\*\*[ \t]*\n((?:>.*(?:\n|$))+)", re.M)
_PHASE_LINE = re.compile(r"^•\s*\*\*(\w+)\*\*\s*—\s*(.+)$")


@lru_cache(maxsize=1)
def opening() -> tuple[tuple[tuple[str, str], ...], str]:
    """(the five phases as (name, purpose), how Define is worked) — read from the skill's [OPENING] block."""
    m = _OPENING.search(instructions("define"))
    lines = [line.lstrip(">").strip() for line in (m.group(1).splitlines() if m else [])]
    phases = tuple((p.group(1), p.group(2).strip()) for p in (_PHASE_LINE.match(x) for x in lines) if p)
    how = next((x for x in lines if x.startswith("Right now")), "")
    return phases, how.replace("**", "")


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
    return {"name": name, "returning": bool(confirmed),
            "phases": [{"name": p, "line": line, "current": p.lower() == "define"} for p, line in phases],
            "how": how, "confirmed": confirmed, "open": open_,
            "next": {"n": nxt["n"], "name": nxt["name"]} if nxt else None}


#: DEF-214: the skill's section F — how Define ends.
_SECTION_F = re.compile(r"^### F — The Define report\n\n(.*?)\n\n---", re.M | re.S)
#: The skill's internal references, left out of team-facing text: "(section 6)", "(requirement R6)".
_INTERNAL = re.compile(r"\s*\((?:section \d+|requirement [A-Z]\d+\w*)\)")


@lru_cache(maxsize=1)
def overview() -> dict[str, Any]:
    """DEF-214 (W1; founder ruling 2026-10-22 afternoon, item 2): the Define overview, from the skill only — the
    thirteen elements (numbered and named as in the sidebar, each with the first sentence of what it is), how Define
    is worked (the [OPENING] block) and how it ends (section F), without the skill's internal references."""
    from backend.middleware.skills import teaching_blocks
    m = _SECTION_F.search(instructions("define"))
    ends = " ".join(_INTERNAL.sub("", m.group(1)).replace("**", "").split()) if m else ""
    elements = []
    for n, (field, _fields) in enumerate(moves.positions("define"), start=1):
        what = str(teaching_blocks("define", field).get("explanation") or "")
        elements.append({"n": n, "name": guard_messages.element_name("define", field),
                         "what": (what.split(". ")[0].rstrip(".") + ".") if what else ""})
    return {"elements": elements, "how": opening()[1], "ends": ends}
