"""Rule 9 of the commit guard (the build matrix) — retired with the procedure at step 6.67.
Moved verbatim from backend/tests/test_commit_guard_tree_rules.py; not collected."""

# ── Rule 9 — the matrix referee binds on EVERY commit ──────────────────────
#
# **THE REFEREE WAS FAIL-CLOSED AND UNREACHABLE.** `verify_built.py` exits
# non-zero when Appendix F and Appendix D disagree, but its only route to a
# commit's exit code ran through rule 4's `pytest`, and rule 4 sits BEHIND the
# `GUARDED_PREFIX` gate. Measured 2026-09-18 by deleting Appendix F's row for
# `6.16 — the board is generated, not written`: the referee reported it, pytest
# went red, and the guard handed a `docs(ops):` subject exit 0.
#
# `docs(` is precisely the subject that edits an appendix.

def _verify_built() -> Any:
    hook = Path(_ROOT) / ".claude" / "hooks" / "verify_built.py"
    spec = importlib.util.spec_from_file_location("verify_built_r9", hook)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_rule_9_runs_ahead_of_the_prefix_gate() -> None:
    """**The assertion that protects the whole point of rule 9.**

    Moving the call below `if not subject.startswith(GUARDED_PREFIX)` restores
    the exact hole it was written to close, and every other test here would
    still pass — the check works perfectly, it just never runs for the subjects
    that edit appendices.
    """
    src = _HOOK.read_text(encoding="utf-8")
    call = src.index("check_build_matrix(root)")
    gate = src.index("if not subject.startswith(GUARDED_PREFIX)")
    assert call < gate, (
        "check_build_matrix runs BEHIND the prefix gate, so a docs( or fix( "
        "commit can land a broken matrix — the condition rule 9 exists to end")


def test_the_matrix_verdict_is_clean_on_the_real_index() -> None:
    g, vb = _guard(), _verify_built()
    verdict = vb.matrix_covers_appendix_d(g._staged_text(_ROOT, g.cs.PROCEDURE))
    assert vb.MATRIX_CLEAN_RE.match(verdict.strip()), verdict


def test_a_step_missing_from_the_matrix_is_not_clean() -> None:
    """The shape that shipped: a row deleted from Appendix F."""
    g, vb = _guard(), _verify_built()
    text = g._staged_text(_ROOT, g.cs.PROCEDURE)
    # The row gained a `Zone` cell at 6.37, so the fixture matches the cells
    # either side of it rather than the row's literal text.
    rows = text.split(NEWLINE)
    idx = next(i for i, l in enumerate(rows)
               if re.match(r"^\| L0 \|[^|]*\|[^|]*\|\s*\*\*6\.16\*\*", l))
    broken = NEWLINE.join(rows[:idx] + rows[idx + 1:])
    assert broken != text, "the 6.16 row moved — this fixture is stale"
    verdict = vb.matrix_covers_appendix_d(broken)
    assert not vb.MATRIX_CLEAN_RE.match(verdict.strip())
    assert "6.16" in verdict


def test_the_matrix_check_reads_the_text_it_is_given_not_the_disk() -> None:
    """§0.32 clause 1, applied to the guard's own reading.

    Reading the working tree would pass a commit whose STAGED matrix is broken
    and block one whose staged matrix is fine while the tree is mid-edit. Rule
    8 resolves its registers from the index for the same reason.

    **And a text with no Appendix F RAISES rather than returning a verdict**,
    which is `read_matrix`'s deliberate fail-closed contract: reporting success
    for a document it could not find is the failure §55.2 exists to name. The
    guard wraps the call and converts the raise into a blocked commit, so the
    fail-closed path reaches the exit code either way.
    """
    vb = _verify_built()
    with pytest.raises(RuntimeError, match="Appendix F is missing"):
        vb.matrix_covers_appendix_d("no appendices in this string at all")
