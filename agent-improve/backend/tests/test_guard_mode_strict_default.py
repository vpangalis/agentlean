"""Founder 2026-09-30 (Azure wiring, Part A3): the default is GUARD_MODE=strict, nothing in the dev
set-up or the run-through scripts sets development implicitly, and every run record says which mode
it ran under. (The suite's own autouse fixture sets development explicitly — tests make no live call.)"""
from __future__ import annotations

import re
from pathlib import Path

from backend.core import content_safety

_PROJECT = Path(__file__).resolve().parents[2]
_REPO = _PROJECT.parent
#: Where a run or a local start could set the mode without anyone seeing it.
SET_UP = [*(_PROJECT / "scripts").glob("*.py"), _PROJECT / "start.ps1", *(_REPO / ".githooks").glob("*"),
          *(_REPO / ".claude" / "hooks").glob("*.py")]
_SETS_DEVELOPMENT = re.compile(r"GUARD_MODE[\"']?\s*[]=:,]\s*[\"']?development", re.I)


def test_nothing_in_the_set_up_sets_development_mode() -> None:
    hits = [str(p.relative_to(_REPO)) for p in SET_UP
            if p.is_file() and _SETS_DEVELOPMENT.search(p.read_text(encoding="utf-8", errors="replace"))]
    assert hits == [], hits
    env = _PROJECT / ".env"
    if env.is_file():
        assert not re.search(r"^\s*GUARD_MODE\s*=\s*development", env.read_text(encoding="utf-8"), re.M | re.I)


def test_a_run_record_names_its_guard_mode(monkeypatch) -> None:
    from scripts.define_runthrough import _guard_mode
    monkeypatch.setattr(content_safety.settings, "GUARD_MODE", "strict")
    got = _guard_mode()
    assert got["mode"] == "strict" and set(got) == {"mode", "content_safety_configured"}
