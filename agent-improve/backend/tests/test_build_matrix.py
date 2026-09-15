"""Appendix F — the build matrix, and §56 amendment v1.64. Step 6.31.

**WHY THESE ARE TESTS AND NOT JUST HOOK CHECKS.** `verify_built.py` is the
referee, but it is invoked by `build_board.py` (fail-soft) and by hand. `pytest`
is rule 4 of the commit-msg guard, so a test is a GATE where the hook alone is
advisory — the same move `test_built_markers.py` made for the 24 checks and
`test_ContradictionDetectionMiddleware_does_not_call_interrupt` made for the
position-6 guard.

**The anchor evaluator is tested against CONSTRUCTED anchors, not against the
live matrix.** The live matrix is `verify_built.py`'s job and moves every
commit; these pin the GRAMMAR, which must not move without a ruling.
"""
from __future__ import annotations

import importlib.util
import subprocess
from pathlib import Path
from typing import Any

import pytest

from backend.core.substate import (
    PRESENTATIONAL_FIELDS,
    CoachingResponse,
    presentational_gaps,
)

_ROOT = Path(
    subprocess.run(["git", "rev-parse", "--show-toplevel"],
                   capture_output=True, text=True).stdout.strip() or ".")
_HOOK = _ROOT / ".claude" / "hooks" / "verify_built.py"

pytestmark = pytest.mark.skipif(
    not _HOOK.exists(), reason="verify_built.py not present in this checkout")


def _vb() -> Any:
    """Import the hook as a module. It is not on a package path."""
    spec = importlib.util.spec_from_file_location("verify_built", _HOOK)
    assert spec and spec.loader, f"cannot load {_HOOK}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ── §56 amendment v1.64 — the four presentational fields ────────────────────

def test_the_four_presentational_fields_are_no_longer_required() -> None:
    """A model omitting `progress` must not fail the whole turn.

    They were REQUIRED `str` from 6.19 until v1.64. §4.8 says *never a hard
    failure to the Belt*, and a Belt asking a coaching question getting an
    error because a position indicator was missing is exactly that.
    """
    r = CoachingResponse(message="here is the thing")
    assert r.explanation == ""
    assert r.example == ""
    assert r.prompt == ""
    assert r.progress == ""


def test_message_is_still_required() -> None:
    """`message` is NOT one of the four, and that is the point of the split.

    A turn with no coaching text has nothing to say to the Belt and nothing to
    append to `messages`. That is a real failure, not a presentational gap.
    """
    with pytest.raises(Exception):
        CoachingResponse()                                      # type: ignore


def test_an_empty_presentational_field_is_reported_as_a_finding() -> None:
    """Optional without a finding would trade a loud failure for a silent one.

    The UI would draw four blocks, one of them blank, and nothing anywhere
    would have noticed.
    """
    r = CoachingResponse(message="m", explanation="e", example="x")
    assert presentational_gaps(r) == ["prompt", "progress"]


def test_whitespace_counts_as_empty() -> None:
    """`progress=" "` breaks the layout exactly as `""` does (§58.5 B6)."""
    r = CoachingResponse(message="m", explanation="e", example="x",
                         prompt="p", progress="   ")
    assert presentational_gaps(r) == ["progress"]


def test_a_complete_response_reports_no_finding() -> None:
    r = CoachingResponse(message="m", explanation="e", example="x",
                         prompt="p", progress="Define · 4 of 12")
    assert presentational_gaps(r) == []


def test_the_four_are_exactly_section_50_1s_four() -> None:
    """Pins the SET, not the count — S-C05's ratified render contract."""
    assert set(PRESENTATIONAL_FIELDS) == {
        "explanation", "example", "prompt", "progress"}
    assert "message" not in PRESENTATIONAL_FIELDS


# ── The anchor grammar ──────────────────────────────────────────────────────

@pytest.mark.parametrize("cell,verdict", [
    ("backend.core.substate::CoachingResponse", "PASS"),
    ("absent: backend.core.substate::NoSuchSymbol", "PASS"),
    ("backend.core.substate::NoSuchSymbol", "FAIL"),
    ("absent: backend.core.substate::CoachingResponse", "FAIL"),
    ("backend.core.substate", "PASS"),
    ("absent: backend.no_such_module", "PASS"),
    ("installed: langgraph", "PASS"),
    ("installed: no_such_distribution_at_all", "DEPENDENCY"),
    ("azure: improve-knowledge-index", "EXTERNAL"),
    ("", "MALFORMED"),
])
def test_the_anchor_grammar(cell: str, verdict: str) -> None:
    got, _ = _vb().evaluate_anchor(cell, str(_ROOT))
    assert got == verdict, f"{cell!r} -> {got}, expected {verdict}"


def test_a_set_anchor_compares_the_member_set() -> None:
    vb = _vb()
    ok, _ = vb.evaluate_anchor(
        "backend.core.substate::CoachingResponse {message,explanation,example,"
        "prompt,progress,fields_captured,citations,contradiction_flag}",
        str(_ROOT))
    assert ok == "PASS"
    bad, detail = vb.evaluate_anchor(
        "backend.core.substate::CoachingResponse {message}", str(_ROOT))
    assert bad == "FAIL"
    assert "unexpected" in detail


def test_a_value_anchor_compares_the_value() -> None:
    vb = _vb()
    assert vb.evaluate_anchor(
        "backend.knowledge.fusion::RRF_K =60", str(_ROOT))[0] == "PASS"
    assert vb.evaluate_anchor(
        "backend.knowledge.fusion::RRF_K =61", str(_ROOT))[0] == "FAIL"


def test_a_repo_path_resolves_from_the_repository_root() -> None:
    """`.claude/` sits ABOVE `agent-improve/` — the ambiguity is the reason
    `repo:` is explicit, and it cost five false FAILs on the first run."""
    vb = _vb()
    assert vb.evaluate_anchor(
        "repo:.claude/hooks/verify_built.py", str(_ROOT))[0] == "PASS"
    assert vb.evaluate_anchor(
        "absent: repo:.claude/hooks/no_such_hook.py", str(_ROOT))[0] == "PASS"


def test_a_bare_path_without_the_repo_prefix_is_malformed() -> None:
    """Rejected rather than guessed. A guessed root reports a present file as
    absent, which is a silent pass on an `absent:` cell."""
    got, _ = _vb().evaluate_anchor(".claude/hooks/verify_built.py", str(_ROOT))
    assert got == "MALFORMED"


def test_an_unimportable_module_path_is_MALFORMED_never_a_silent_pass() -> None:
    """**The false pass this caught on its own row.**

    Step 6.31's seed carried `absent: .claude.hooks.verify_built::read_matrix`.
    That module name starts with a dot and can never import, so the `absent:`
    was trivially true and would have stayed true FOREVER — including after
    the symbol was built.

    **An `absent:` anchor is where an unfailable check hides.** A positive
    anchor that cannot resolve fails loudly; a negative one goes quiet.
    """
    got, detail = _vb().evaluate_anchor(
        "absent: .claude.hooks.verify_built::read_matrix", str(_ROOT))
    assert got == "MALFORMED"
    assert "never resolve" in detail


# ── The two referee checks ──────────────────────────────────────────────────

def test_the_matrix_covers_appendix_d_in_both_directions() -> None:
    """SET equality, not the count that was originally asked for.

    A count of 69 passes when one step is dropped and another added — which is
    exactly the edit a renumber makes. It would also have been wrong by one the
    moment step 6.31 added its own Appendix D row.
    """
    vb = _vb()
    want = vb.appendix_d_steps()
    got = {r["step"].strip() for r in vb.read_matrix()}
    assert want == got, (
        f"in Appendix D not the matrix: {sorted(want - got)}; "
        f"in the matrix not Appendix D: {sorted(got - want)}")
    assert len(want) >= 69


def test_every_evidence_cell_holds_against_the_tree() -> None:
    """The matrix is the leading document; this is what makes that true."""
    assert _vb().matrix_anchors() == ""


def test_every_matrix_row_carries_an_evidence_cell() -> None:
    """An empty cell is a row nothing proves — the condition Appendix F
    replaced, where 45 of 69 markers were backed by no check at all."""
    empty = [r["step"].strip() for r in _vb().read_matrix()
             if not r["evidence"].strip().strip("`")]
    assert empty == [], f"rows with no anchor: {empty}"


def test_the_order_column_is_a_sequence_with_no_duplicates() -> None:
    """Two items numbered 3 is a person having edited one and not the other."""
    ns = [int(r["order"].strip()) for r in _vb().read_matrix()
          if r["order"].strip().isdigit()]
    assert len(ns) == len(set(ns)), f"duplicate Order numbers: {sorted(ns)}"
    assert ns == sorted(ns) or sorted(ns) == list(range(1, len(ns) + 1))


def test_the_referee_fails_closed_when_appendix_f_is_missing() -> None:
    """A referee that reports success when its own document is gone is the
    failure mode §55.2 exists to name."""
    vb = _vb()
    original = vb.PROCEDURE
    try:
        vb.PROCEDURE = str(_ROOT / "no_such_procedure.md")
        with pytest.raises(Exception):
            vb.read_matrix()
    finally:
        vb.PROCEDURE = original
