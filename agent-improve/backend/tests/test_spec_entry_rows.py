"""The spec-entry population, and assertion 5 — step 6.39.

WHY THIS FILE EXISTS
--------------------
6.37 moved the 70 facts that carry a `> **BUILT:**` marker, all anchored in
§1–§56. **The specification layer is a different population and barely
overlaps it**: 96 entries in Part XII, §57–§69, of which only 4 sit under a
section that also carries a marker. Measured 2026-09-18 at `1469d08`.

Until they had rows, **26 open gaps referenced an `S-id` that named nothing in
the register** — so assertion 5, *every gap names a fact that exists*, could not
be enforced without forcing those 26 to `unscheduled` to satisfy a check rather
than to state a truth.

THE TWO SHAPES A SPEC ENTRY TAKES
---------------------------------
Found by counting, not assumed: **81 are headings** (`### 58.2 S-C02 ·
PhaseState`) and **20 are table rows** in §69's computation-tool tables, with 5
defined both ways. 81 + 20 − 5 = 96, and **nothing is left dangling** — every
`S-id` mentioned anywhere in the bible resolves to one shape or the other. A
parse that knew only the heading form would have silently missed 15.
"""
from __future__ import annotations

import importlib.util
import re
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
    spec = importlib.util.spec_from_file_location("verify_built_639", _HOOK)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _spec_ids_in_the_bible() -> set:
    return set(re.findall(r"\bS-[CF]\d+\b", _ARCH.read_text(encoding="utf-8")))


def test_every_spec_entry_in_the_bible_has_a_register_row() -> None:
    """96 entries, both shapes, no exceptions.

    **The count is derived from the bible rather than pinned here.** A pinned
    96 would pass the day someone adds an entry and forgets its row, which is
    the whole failure this register exists to end.
    """
    vb = _vb()
    _, rows = vb._register_facts(_PROC.read_text(encoding="utf-8"))
    missing = sorted(_spec_ids_in_the_bible() - rows)
    assert not missing, (
        f"{len(missing)} spec entries carry no row in the register: "
        f"{', '.join(missing[:12])}")


def test_assertion_5_is_clean_on_the_real_register() -> None:
    assert _vb().gap_refs_resolve() == ""


def test_assertion_5_catches_a_gap_naming_a_spec_entry_that_has_no_row() -> None:
    """**The check must fail on the shape that shipped**, or it proves nothing.

    Before 6.39 this was the state of 26 open gaps at once.
    """
    vb = _vb()
    text = _PROC.read_text(encoding="utf-8")
    broken = text.replace("**S-C02**", "**S-C02-GONE**", 1)
    assert broken != text, "the S-C02 row moved — this fixture is stale"
    verdict = vb.gap_refs_resolve(broken)
    assert "S-C02" in verdict, (
        "a gap naming a spec entry with no row was not reported")


def test_a_closed_gap_is_out_of_scope() -> None:
    """§66.6's rows use `Attaches to` for a RESOLUTION NOTE, not a reference
    list, and a resolved gap owes no live fact. Ranging over them would report
    prose as an unresolved reference.
    """
    vb = _vb()
    text = _PROC.read_text(encoding="utf-8")
    assert "### 66.6 Closed" in text
    assert vb.gap_refs_resolve(text) == ""


def test_the_non_fact_attachments_are_enumerated_with_a_reason() -> None:
    """**Ten things a gap attaches to that are not facts and never will be.**

    `ui/index.html` is the sharpest: **G-71 IS the gap that it has no owner**,
    so a check demanding a fact row for it would force inventing the very thing
    G-71 records as absent. Declared, never baselined.
    """
    vb = _vb()
    assert "ui/index.html" in vb.ATTACH_NOT_A_FACT
    assert len(vb.ATTACH_NOT_A_FACT) == 10, (
        f"{len(vb.ATTACH_NOT_A_FACT)} non-fact attachments, not 10 — if one "
        "was added, say in the commit body why it can never be a fact")


def test_the_section_half_of_assertion_5_is_not_yet_claimed() -> None:
    """**The condition, asserted rather than left as a promise.**

    19 distinct sections an open gap names carry neither a fact row nor a
    `NOT-MARKABLE` declaration. Most are governance rules that are probably
    NOT-MARKABLE, so creating a row for each would pre-empt exactly the
    judgement 6.40 exists to make — and then delete it again.

    This test goes RED when 6.40 lands, which is the point: it is the reminder
    that assertion 5 gains its § half then.
    """
    vb = _vb()
    text = _PROC.read_text(encoding="utf-8")
    secs, _ = vb._register_facts(text)
    referenced = set()
    sub = ""
    for ln in text[text.find("## Appendix G"):].splitlines():
        h = re.match(r"^### (66\.\d+)", ln)
        if h:
            sub = h.group(1)
        m = vb._GAP_OPEN.match(ln)
        if not m or m.group("struck") or sub == "66.6":
            continue
        cells = ln.split("|")
        if len(cells) < 4:
            continue
        for tok in re.split(r"[,·]", cells[-3]):
            tok = tok.strip().strip("`").strip()
            if re.fullmatch(r"§[\d.]+", tok):
                referenced.add(tok)
    unresolved = referenced - secs
    assert unresolved, (
        "every § an open gap names now resolves — 6.40 has landed, so give "
        "assertion 5 its § half and delete this test")
