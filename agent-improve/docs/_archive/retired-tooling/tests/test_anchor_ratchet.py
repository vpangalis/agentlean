"""G-87 — one bound became three. Step 6.41.

WHY THIS FILE EXISTS
--------------------
`register facts carrying no symbol anchor` pinned how many register rows carry
an em dash where a symbol belongs. It moved **70 → 166** and would have moved
again, every rise legitimate and every rise upward.

**A bound raised whenever it is exceeded constrains regression and nothing
else.** It caught a new row parked at an em dash, which is what it was built
for, and it could not tell a register that was GROWING from one that was
ROTTING — because three different things were being counted as one:

    50   built (✅ / ⚠️) and not anchored — **a BACKLOG.** Something exists in
         the tree and nobody has pointed at it. A rise is unambiguously bad
    16   ratified but unbuilt (☐) — **a SPECIFICATION.** Nothing exists to
         point at, so the em dash is the honest cell. A rise is NORMAL and
         means the spec grew
    96   never assessed (State is itself `—`) — **NEITHER.** The spec entries
         arrived this way at 6.39, which is how 70 became 166 in one step and
         read as a collapse rather than as a population change

THE POINT IS NOT THE SMALLER NUMBER
-----------------------------------
6.41's own body says so: *lowering the number is not the goal — making it able
to fall is.* Four facts were anchored here and each was verified individually
rather than swept, because the cheapest way to satisfy this step is the one it
must not take: deleting rows, or inventing anchors that resolve without proving
anything. `matrix_anchors` evaluates every anchor against the tree, so a
decorative one fails there — which is the structural reason this cannot be
gamed quietly rather than a promise that it will not be.

§10's anchor is the one worth reading. Its fact claims the class is GONE, so
the anchor is `absent: backend.storage.blob::ImproveBlobClient`, and the
evaluator answers *"absent, as claimed"* — the anchor proves the sentence
rather than merely resolving somewhere near it.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from typing import Any

import pytest

_ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                       capture_output=True, text=True).stdout.strip()
_HOOK = Path(_ROOT) / ".claude" / "hooks" / "verify_built.py"
_PROC = Path(_ROOT) / "agent-improve" / "docs" / "REFACTORING_PROCEDURE.md"

pytestmark = pytest.mark.skipif(not _HOOK.exists(), reason=f"{_HOOK} not present")


def _vb() -> Any:
    spec = importlib.util.spec_from_file_location("verify_built_641", _HOOK)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_the_three_categories_partition_the_unanchored_rows() -> None:
    """**No row falls in two categories and none falls in none.**

    A split that did not partition would let a row escape counting entirely,
    which is the failure the single bound at least did not have.
    """
    vb = _vb()
    proc = _PROC.read_text(encoding="utf-8")
    total = len(vb._unanchored(proc))
    parts = (int(vb.facts_anchorable_not_anchored(proc))
             + int(vb.facts_with_nothing_to_anchor(proc))
             + int(vb.facts_unassessed(proc)))
    assert parts == total, (
        f"the three categories sum to {parts} against {total} unanchored rows "
        "— a row is being counted twice or not at all")


def test_the_backlog_is_the_category_that_must_fall() -> None:
    """50 → 49 on 2026-09-23, and the direction is the point.

    §63.9's row read *"the field is on all five schemas"* with an em dash where
    a symbol belongs — built, and nobody pointing at it. Step 6.20 gave
    `phase_metrics` a writer for Define and the row gained
    `define_phase_metrics`. **This is the first fall since 6.41 split one bound
    into three**, and 6.41's own body said why that mattered: *lowering the
    number is not the goal — making it able to fall is.*
    """
    vb = _vb()
    assert vb.facts_anchorable_not_anchored() == "49"


def test_the_four_anchors_applied_here_actually_resolve() -> None:
    """**An anchor is evidence or it is decoration.**

    Each was verified individually before being written, not swept: a naive
    pass over backticked tokens produced `backend.escalate` for §14, which
    resolves and proves nothing about that section's claim.
    """
    vb = _vb()
    root = str(Path(_ROOT))
    for anchor, expect in [
        ("backend.core.state::SupervisorState", "PASS"),
        ("backend.core.prompts::PHASE_COACH_PROMPT", "PASS"),
        ("absent: backend.storage.blob::ImproveBlobClient", "PASS"),
        ("repo:agent-improve/backend/gateway/routes.py", "PASS"),
    ]:
        verdict, detail = vb.evaluate_anchor(anchor, root)
        assert verdict == expect, f"{anchor} -> {verdict} {detail}"


def test_section_10s_anchor_proves_its_own_sentence() -> None:
    """The claim is that the class is GONE. The anchor says so, not merely that
    something exists nearby."""
    vb = _vb()
    verdict, detail = vb.evaluate_anchor(
        "absent: backend.storage.blob::ImproveBlobClient", str(Path(_ROOT)))
    assert verdict == "PASS" and "absent" in detail


def test_a_built_fact_losing_its_anchor_raises_the_backlog() -> None:
    """**The mutation the old bound could not distinguish from growth.**

    Stripping an anchor off a ✅ row is rot. Adding a ☐ row is growth. The
    single number moved the same way for both.
    """
    vb = _vb()
    proc = _PROC.read_text(encoding="utf-8")
    before = int(vb.facts_anchorable_not_anchored(proc))
    rotted = proc.replace("`backend.core.state::SupervisorState`", "—", 1)
    assert rotted != proc, "§57.2's anchor moved — this fixture is stale"
    assert int(vb.facts_anchorable_not_anchored(rotted)) == before + 1
    # **Inject INSIDE Appendix F.** `| §49 |` appears four times and the first
    # is a step body's Reference cell, so a naive replace put the new row where
    # `read_matrix` never looks: the count did not move and the fixture tested
    # nothing while reading exactly like a test that worked.
    head = proc.index("## Appendix F — The build matrix")
    row = proc.index("| L1 |", head)
    grown = proc[:row] + (
        "| L1 |  | UI | — | a ratified thing not yet built | ☐ | — | §99.9 |\n"
    ) + proc[row:]
    assert int(vb.facts_anchorable_not_anchored(grown)) == before, (
        "adding an unbuilt row moved the BACKLOG count — the split is not "
        "separating growth from rot, which is the whole of G-87")
    assert int(vb.facts_with_nothing_to_anchor(grown)) == \
        int(vb.facts_with_nothing_to_anchor(proc)) + 1
