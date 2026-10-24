"""DEF-204 — the project's status, computed once by the backend (W2; G-205).

Every figure the screens show about where a project stands — its phase, the days since the case was opened, the
target date and the days left, the days spent in each phase, how many elements are confirmed, what is open and what
waits — comes from here, so the progress bar, the chat, the overview, the Submit button and the case list cannot
disagree. Pure functions of the case record (and a registry row) and today's date; no model call, no storage.
"""
from __future__ import annotations

from datetime import date, datetime, timezone
from typing import Any, Optional

from backend.phases.mappers_common import PHASE_ORDER


def _day(value: Any) -> Optional[date]:
    """An ISO date or timestamp as a calendar day (UTC), or None when it is not one."""
    text = str(value or "").strip()
    if not text:
        return None
    try:
        when = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        try:
            return date.fromisoformat(text[:10])
        except ValueError:
            return None
    return (when.astimezone(timezone.utc) if when.tzinfo else when).date()


def days_between(start: Any, end: Any) -> Optional[int]:
    """Whole days from `start` to `end` (ISO strings or dates), or None when either is not a date."""
    a = start if isinstance(start, date) else _day(start)
    b = end if isinstance(end, date) else _day(end)
    return (b - a).days if a and b else None


def confirmed_figure(element_rows: list[dict[str, Any]]) -> dict[str, Any]:
    """"n of N confirmed" — from the progress view's element rows (`moves.element_rows`), the one count."""
    done = sum(1 for r in element_rows if r.get("status") == "confirmed")
    return {"done": done, "of": len(element_rows), "label": f"{done} of {len(element_rows)} confirmed"}


def days_per_phase(case: Any, today: date) -> list[dict[str, Any]]:
    """Each phase reached so far: a phase starts when the one before it was approved (Define when the case was
    opened) and ends at its own approval, or today while it is the current one."""
    out: list[dict[str, Any]] = []
    start: Any = getattr(case, "created_at", None)
    current = str(getattr(case, "current_phase", "define") or "define")
    for phase in PHASE_ORDER:
        record = (getattr(case, "phases", {}) or {}).get(phase)
        passed = bool(record is not None and record.gate_passed)
        end = (record.submitted_at if passed and record is not None else None) or today
        out.append({"phase": phase, "days": days_between(start, end), "done": passed})
        if phase == current or not passed:
            break
        start = record.submitted_at if record is not None else start
    return out


def project_status(case: Any, element_rows: list[dict[str, Any]], waiting: Optional[str],
                   today: Optional[date] = None) -> dict[str, Any]:
    """The status every screen shows. `element_rows` are the current phase's (Define's while in Define);
    `waiting` names what waits for the team, or None."""
    today = today or datetime.now(timezone.utc).date()
    phase = str(getattr(case, "current_phase", "define") or "define")
    figure = confirmed_figure(element_rows)
    if phase == "define":
        # G-259: in Define the one figure is define_progress's — the reply's and the bar's.
        from backend.phases.define.schema import define_progress
        record = (getattr(case, "phases", {}) or {}).get("define")
        p = define_progress(dict((record.structured if record is not None else None) or {}))
        figure = {"done": p["done"], "of": p["of"], "label": f"{p['done']} of {p['of']} confirmed"}
    return {"phase": phase,
            "days_since_opened": days_between(getattr(case, "created_at", None), today),
            "target_date": str(getattr(case, "target_date", "") or "") or None,
            "days_to_target": days_between(today, getattr(case, "target_date", None)),
            "days_per_phase": days_per_phase(case, today),
            "confirmed": figure, "open": figure["of"] - figure["done"], "waiting": waiting}


def days_in_phase(entry: Any, today: Optional[date] = None) -> int:
    """A case-list row's days in its current phase — the same count `days_per_phase` gives: from the phase's start
    (`phase_started_at`, else the case's opening) to today."""
    today = today or datetime.now(timezone.utc).date()
    days = days_between(getattr(entry, "phase_started_at", None) or getattr(entry, "created_at", None), today)
    return max(0, days) if days is not None else 0


WHERE_WE_STAND = "Where do we stand?"


def next_steps(element_name: str, card: Optional[dict[str, Any]]) -> list[str]:
    """DEF-095 (C4): two or three next steps under a reply, computed in code from what is missing — never a model
    call, and always about the element the reply works on (W4).
    What the reply's card still misses comes first ("Add …"); with nothing missing, an example of the element or what
    it needs; "Where do we stand?" always last."""
    missing = [str(m) for m in ((card or {}).get("missing") or [])]
    if missing:
        steps = [f"Add {m.lower()}" for m in missing[:2]]
    elif element_name:
        steps = [f"Show me an example for {element_name}", f"What does {element_name} need?"]
    else:
        steps = []
    return [*steps, WHERE_WE_STAND][:3]
