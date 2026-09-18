"""Assertion 7 — every section owns a row or declares it cannot. Step 6.40.

WHY THIS FILE EXISTS
--------------------
§66's header has always claimed the marker-to-row correspondence *"is
checkable"*. **In the section-to-row direction it was not**, because the
population it ranges over was never defined: nothing distinguished the 198
sections carrying no annotation from the 17 that carried one, since the 17 were
simply the ones somebody had annotated.

HOW 198 BECAME 11
-----------------
Measured, at each stage, rather than estimated:

    198   the 6.37 audit's figure
    112   at HEAD — 6.39's 96 spec rows already covered their own sections
     78   applying §16's own convention, *"One marker per item, never one per
          section that mentions it"*: a sub-section whose ANCESTOR owns a row
          is marked at its canonical home
     38   §39.2–§39.5 given rows. **Four missing markers cost 40 sections** —
          §39.1 owned a row and the other four phase sections did not, though
          all five are "complete specification" sections of the same kind
     11   §43 given rows, and §56/§57/§67/§68 declared NOT-MARKABLE by category

The 11 that remain are founder judgements and sit in `PENDING_CLASSIFICATION`,
pinned so the list can only shrink.

**The ancestor clause is what makes this a check rather than a backlog.**
Without it the population is 112 and assertion 7 reports 112 violations on its
first run — the failure `section_title_sources` records happening twice to the
typed-title probe, and the reason the 31 DONE steps are excluded by name from
the unbanded-step check.
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
_ARCH = Path(_ROOT) / "agent-improve" / "ARCHITECTURE.md"

pytestmark = pytest.mark.skipif(not _HOOK.exists(), reason=f"{_HOOK} not present")


def _vb() -> Any:
    spec = importlib.util.spec_from_file_location("verify_built_640", _HOOK)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_assertion_7_is_clean_on_the_real_documents() -> None:
    assert _vb().every_section_declares_itself() == ""


def test_a_section_with_neither_a_row_nor_a_declaration_is_caught() -> None:
    """**The check must fail on the shape that shipped**, or it proves nothing.

    **§7 is the right fixture and §23.5 is not.** §23.5 owns a row AND sits
    under §23, which owns one too — so stripping its row leaves it covered by
    the ancestor clause and the check correctly says nothing. §7 is top-level
    and held only by its own row, which is the state 112 sections were in
    before this step.
    """
    vb = _vb()
    proc = _PROC.read_text(encoding="utf-8")
    assert proc.count("| §7 |") == 1, "§7's row is no longer unique — fixture stale"
    broken = proc.replace("| §7 |", "| §7-GONE |")
    assert "§7" in vb.every_section_declares_itself(broken).split(", ")


def test_the_ancestor_clause_is_what_makes_this_checkable() -> None:
    """**Remove it and the check reports a backlog instead of a defect.**

    §16's convention is *one marker per item, never one per section that
    mentions it*, so a sub-section of a marked item is marked at its canonical
    home. Counting those as undeclared gives 112 findings on a clean tree.
    """
    vb = _vb()
    proc, arch = _PROC.read_text(encoding="utf-8"), _ARCH.read_text(encoding="utf-8")
    rows, _ = vb._register_facts(proc)
    order, declared = vb._sections_and_declarations(arch)
    without_ancestors = [
        s for s in order
        if s not in rows and s not in declared
        and s not in vb.PENDING_CLASSIFICATION
    ]
    assert len(without_ancestors) > 30, (
        "the ancestor clause is carrying nothing — either the register grew to "
        "cover these sections directly, in which case simplify the check, or "
        "the clause is no longer doing what this test says it does")
    assert vb.every_section_declares_itself(proc, arch) == ""


def test_nothing_is_parked_pending_a_ruling() -> None:
    """**All eleven were ruled on 2026-09-18 and the set is EMPTY.**

    Ten are NOT-MARKABLE — six parents whose children own the facts (§19, §39,
    §50, §58, §63, §69), two deliberate absences (§19.9, §66), §1 a statement
    of purpose with nothing to anchor, and §4 a summary that MENTIONS facts
    owned elsewhere rather than owning them.

    §69.1 got a ROW instead, and the reason is the interesting one: its
    conventions were factored OUT of the twenty computation-tool entries to
    avoid twenty repetitions, so no child restates them and the parent
    genuinely owns them. The parent-of-facts rule does not apply where the
    parent is where the fact was deliberately put.
    """
    vb = _vb()
    assert vb.PENDING_CLASSIFICATION == set()
    assert vb.sections_awaiting_a_ruling() == "0"


def test_the_pending_mechanism_still_bites_if_something_is_parked() -> None:
    """**Emptied, not deleted, so parking cannot become free again.**

    A set that exists and is pinned at zero means a future section cannot be
    quietly exempted: adding one fails the check and the number has to be
    raised in the open. Deleting the mechanism would have removed the cost.
    """
    vb = _vb()
    proc = _PROC.read_text(encoding="utf-8")
    arch = _ARCH.read_text(encoding="utf-8")
    try:
        vb.PENDING_CLASSIFICATION.add("§99.9")
        assert vb.sections_awaiting_a_ruling(proc, arch) == "1", (
            "parking a section did not move the count — the mechanism is inert "
            "and an exemption could be added for free")
    finally:
        vb.PENDING_CLASSIFICATION.discard("§99.9")
    assert vb.sections_awaiting_a_ruling(proc, arch) == "0"


def test_section_69_1_owns_a_row_rather_than_an_exemption() -> None:
    """The one of the eleven that is a FACT, not an absence."""
    vb = _vb()
    rows, _ = vb._register_facts(_PROC.read_text(encoding="utf-8"))
    assert "§69.1" in rows


def test_the_four_phase_sections_now_own_rows() -> None:
    """**Four missing markers cost 40 sections**, and they are the finding.

    §39.1 owned a row and §39.2–§39.5 did not, though all five are "complete
    specification" sections of the same kind. Every `Purpose`, `Tools bound
    to X` and `Conditions` under Measure, Analyse, Improve and Control was
    unclassified only because its parent had none.
    """
    vb = _vb()
    rows, _ = vb._register_facts(_PROC.read_text(encoding="utf-8"))
    for sec in ("§39.1", "§39.2", "§39.3", "§39.4", "§39.5"):
        assert sec in rows, f"{sec} owns no register row"
