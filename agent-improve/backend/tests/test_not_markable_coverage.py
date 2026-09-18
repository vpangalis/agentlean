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


def test_the_pending_list_is_exactly_the_eleven_founder_judgements() -> None:
    vb = _vb()
    assert vb.PENDING_CLASSIFICATION == {
        "§1", "§4", "§19", "§19.9", "§39", "§50",
        "§58", "§63", "§66", "§69", "§69.1"}
    assert vb.sections_awaiting_a_ruling() == "11"


def test_a_pending_section_that_gains_a_declaration_leaves_the_set() -> None:
    """**An exemption that outlives its reason is the shape §55.2 keeps
    finding.** Ruling on one of the eleven must lower the count, not merely
    stop it mattering.
    """
    vb = _vb()
    arch = _ARCH.read_text(encoding="utf-8")
    ruled = arch.replace(
        "## 1. What Agent Improve is",
        "## 1. What Agent Improve is\n\n> **NOT-MARKABLE:** orientation.", 1)
    assert ruled != arch, "§1's heading moved — this fixture is stale"
    assert vb.sections_awaiting_a_ruling(
        _PROC.read_text(encoding="utf-8"), ruled) == "10"


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
