"""The defect loop's counts — founder ruling R-B change 2, 2026-10-20.

- Escape classes: every `docs/defects.json` entry carries `escape_class` — how the defect got past every check
  (error_routine | path_test | join | assumption | claim | xfail_mask | none), or null when its D4 ESCAPE does not say.
- The rule: two defects in one class with no D7 action in the register's `escape_controls` -> that D7 is owed
  before the next feature (`owed`). Class `none` (nothing escaped) owes nothing.
- Regression and capability, counted apart: regression is the rule 11b ratchet set (`docs/features-ratchet.json`,
  every feature that passed at any earlier commit; target 100% passing), capability every feature never passed yet.

Module-level functions only (CLAUDE.md §2); read by `build_control_board.py`.
"""
from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

PROJECT = Path(__file__).resolve().parents[2]
DEFECTS = PROJECT / "docs" / "defects.json"
RATCHET = PROJECT / "docs" / "features-ratchet.json"

#: The classes, in the order the board lists them.
CLASSES: tuple[str, ...] = ("error_routine", "path_test", "join", "assumption", "claim", "xfail_mask", "none")


def register(path: Path = DEFECTS) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def tally(reg: dict[str, Any]) -> dict[str, int]:
    """Defects per escape class, every class listed; `unclassified` for an entry whose class is null."""
    n = Counter(d.get("escape_class") or "unclassified" for d in reg["defects"])
    return {**{c: n.get(c, 0) for c in CLASSES}, "unclassified": n.get("unclassified", 0)}


def owed(reg: dict[str, Any]) -> list[str]:
    """The classes with two or more defects and no D7 action: each D7 is owed before the next feature."""
    controls = reg.get("escape_controls") or {}
    counts = tally(reg)
    return [c for c in CLASSES if c != "none" and counts[c] >= 2 and not str(controls.get(c) or "").strip()]


def ratchet(path: Path = RATCHET) -> set[str]:
    return set(json.loads(path.read_text(encoding="utf-8"))["passing"])


def split(statuses: dict[str, str], ever: set[str]) -> dict[str, int]:
    """Regression vs capability. `statuses` maps each feature to its status ("passing" or another), `ever` is
    the ratchet set. Regression: of the features that ever passed, how many pass now (target: all). Capability:
    the features never passed yet, and how many of them pass now (newly proven, joining the ratchet)."""
    reg_ids = [i for i in statuses if i in ever]
    cap_ids = [i for i in statuses if i not in ever]
    return {"regression_total": len(reg_ids), "regression_passing": sum(statuses[i] == "passing" for i in reg_ids),
            "capability_total": len(cap_ids), "capability_passing": sum(statuses[i] == "passing" for i in cap_ids)}
