"""Rules 7 and 8 of the commit-msg guard — what may ENTER the tree (CLAUDE.md §0.32).

WHY THIS FILE EXISTS — G-57
---------------------------
**Ten cases were demonstrated when the rules landed, and nothing re-ran them.**
That is a demonstration, not a test: it proves the rules worked once, on one
tree, on one afternoon. `test_commit_guard_8d.py` states the argument for rule 6
and it transfers here without a word changed — *a message check fails SILENTLY
by letting commits through*, which is the one failure mode a gate must not have.

**An index check fails the same way, and has two extra ways to get there.** A
scratch pattern that stops matching reports nothing. And rule 8 resolves numbers
by parsing two tables it does not own: Appendix D of `REFACTORING_PROCEDURE.md`
and §66's register in `ARCHITECTURE.md`. **Rule 8 is the fourth hook parsing
Appendix D and the second parsing §66** — both tables carry format warnings in
their own headers because of the readers that came before, and a regex that
stops resolving after a reformat would let every new file through while
reporting success.

IT ALSO CARRIES RULE 17's NAMED-FILE INVARIANT (rule 2b's, carried over)
----------------------------------------------
**This is the guard's PATH-LIST test file**, and rule 17's named files are one of its
path lists. The invariant added 2026-09-14: **a watched path must be a source of
truth, never the output of a generator.** `docs/board.html` was on that list and
is regenerated from git log every commit, so rule 2b fired on every commit
whether or not an architectural fact had changed.

WHAT IS PINNED
--------------
What the rules RANGE OVER, not only what they match: that a modified path is
invisible to both (the ratchet), that a rename into a scratch name is caught,
that the registers are read from the INDEX rather than the disk, and that a
declared number must resolve. Plus the two live registers actually parsing —
the assertion that goes red on a reformat rather than on a rule change.

WHAT IS DELIBERATELY NOT PINNED
-------------------------------
**Whether a file genuinely belongs to the step it declares.** Rule 8 checks that
a number is declared and that it exists. `Step: 2.3` on a file with nothing to
do with the dependency upgrade passes, and that limit is in `check_step_or_gap`'s
docstring for the same reason it is here: so a green suite is not read as
evidence that the numbers are honest.

**And whether a scratch file is scratch.** Rule 7 reads the NAME. A draft called
`notes.md` passes, every time, by design.
"""
from __future__ import annotations

import importlib.util
import re

NEWLINE = chr(10)
import subprocess
from pathlib import Path
from typing import Any

import pytest

# ── Load the hook by path. It is a script, not an installed module. ────────
_ROOT = subprocess.run(
    ["git", "rev-parse", "--show-toplevel"],
    capture_output=True, text=True,
).stdout.strip() or str(Path(__file__).resolve().parents[3])
_HOOK = Path(_ROOT) / ".claude" / "hooks" / "commit-msg-refactor-guard.py"

pytestmark = pytest.mark.skipif(
    not _HOOK.exists(), reason=f"{_HOOK} not present",
)


def _guard() -> Any:
    spec = importlib.util.spec_from_file_location("commit_msg_guard_tree", _HOOK)
    assert spec and spec.loader, f"cannot load {_HOOK}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


#: `Any` for the same reason the 8D suite uses it: on a clone without the hook
#: this is None and every test is skipped, so the attribute access is
#: unreachable rather than unsafe.
g: Any = _guard() if _HOOK.exists() else None


# ══════════════════════════════════════════════════════════════════════════
# Rule 7 — what counts as scratch
# ══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("path", [
    "agent-improve/docs/scratch/notes.md",
    "agent-improve/docs/_drafts/plan.md",
    "scratchpad/x.py",
    "agent-improve/tmp/out.json",
    "_Artifacts/audit.md",
    "agent-improve/_Claude_chat_Prompts/handover.md",
])
def test_a_scratch_directory_segment_is_caught(path: str) -> None:
    """The segment list, matched on the DIRECTORY part and case-insensitively.

    The last two are the folders that were actually sitting untracked in this
    tree when the rule was written, so the list is pinned against what happened
    rather than against what someone imagined might.
    """
    assert g.scratch_reason(path), path


@pytest.mark.parametrize("path", [
    "agent-improve/docs/PLAN.md.bak",
    "agent-improve/backend/core/graph.py.orig",
    "notes.tmp",
    "agent-improve/docs/OLD.md.old",
    "run.log",
])
def test_a_scratch_suffix_is_caught(path: str) -> None:
    assert g.scratch_reason(path), path


@pytest.mark.parametrize("path", [
    "agent-improve/docs/Untitled-1.md",
    "agent-improve/docs/ARCHITECTURE - Copy.md",
    "agent-improve/docs/ARCHITECTURE (conflicted copy 2026-09-13).md",
    "agent-improve/docs/~$REPORT.docx",
    "agent-improve/docs/REPORT.md~",
])
def test_the_mirror_and_editor_shapes_are_caught(path: str) -> None:
    """**These are what a SYNCED MIRROR and an open Office document produce.**

    §0.32's first clause names that mirror by name: this tree lives inside
    OneDrive, which writes a conflicted copy when two machines edit one file.
    Both shapes look like content and are not.
    """
    assert g.scratch_reason(path), path


@pytest.mark.parametrize("path", [
    "agent-improve/backend/knowledge/scratchpad_tools.py",
    "agent-improve/docs/CONTINUITY.md",
    "agent-improve/backend/core/graph.py",
    ".claude/hooks/commit-msg-refactor-guard.py",
    "agent-improve/docs/_archive/response-to-audit-2026-08-19.md",
])
def test_a_real_path_is_not_scratch(path: str) -> None:
    """The false-positive side, and it is the side that decides adoption.

    `scratchpad_tools.py` is the shape that matters: the word is in the NAME and
    not in a directory segment, and a rule that blocked it would be routed
    around within a week — rule 3's ratchet argument applied to a path matcher.
    """
    assert not g.scratch_reason(path), path


def test_the_reason_names_the_pattern_not_a_verdict() -> None:
    """A developer can act on "a `.bak` suffix". They cannot act on "looks wrong"."""
    assert ".bak" in g.scratch_reason("docs/PLAN.md.bak")
    assert "scratch/" in g.scratch_reason("docs/scratch/notes.md")


def test_scratch_blocks_and_says_so() -> None:
    with pytest.raises(SystemExit) as exc:
        g.check_scratch(["agent-improve/docs/scratch/notes.md"])
    assert exc.value.code == 1


def test_a_clean_set_of_added_paths_passes() -> None:
    g.check_scratch(["agent-improve/backend/core/graph.py", "agent-improve/docs/X.md"])


# ══════════════════════════════════════════════════════════════════════════
# Rule 8 — the number, and where it may be declared
# ══════════════════════════════════════════════════════════════════════════


def test_a_spine_subject_declares_its_own_step() -> None:
    steps, gaps = g._declared_numbers(
        "refactor(arch-v2): commit 6.26 — the guard's tree rules get a test suite", "")
    assert steps == {"6.26"} and not gaps


def test_a_trailer_declares_a_step_on_any_commit_type() -> None:
    steps, _ = g._declared_numbers("docs: an archive note", "body\n\nStep: 6.25\n")
    assert steps == {"6.25"}


def test_a_trailer_declares_a_gap() -> None:
    _, gaps = g._declared_numbers("docs: an archive note", "body\n\nGap: G-57\n")
    assert gaps == {"G-57"}


def test_the_gap_trailer_is_case_insensitive_and_plural_tolerant() -> None:
    _, gaps = g._declared_numbers("docs: x", "gaps: g-52, G-57\n")
    assert gaps == {"G-52", "G-57"}


def test_a_number_merely_MENTIONED_in_the_body_does_not_count() -> None:
    """**Subject or trailer, never a mention** — rule 6's trigger-2 lesson.

    Half the commits in this log name a step or a G-number in passing. A rule
    that accepted a mention would be satisfiable by accident, which is the same
    as not being satisfiable at all.
    """
    steps, gaps = g._declared_numbers(
        "docs: the board names every number",
        "The chips now read G-52 and G-57, and step 6.25 is described.\n")
    assert not steps and not gaps


def test_an_undeclared_new_path_is_refused() -> None:
    with pytest.raises(SystemExit) as exc:
        g.check_step_or_gap(_ROOT, "docs: a new note", "no trailer here\n",
                            ["agent-improve/docs/NEW.md"])
    assert exc.value.code == 1


@pytest.mark.parametrize("trailer", ["Step: 99.9", "Gap: G-999"])
def test_a_number_that_resolves_nowhere_is_refused(trailer: str) -> None:
    """**A number that resolves nowhere schedules nothing**, so it is refused
    exactly like none at all. §66's own words: a gap without one does not render
    on the board and so is not scheduled by anything.
    """
    with pytest.raises(SystemExit) as exc:
        g.check_step_or_gap(_ROOT, "docs: a new note", f"body\n\n{trailer}\n",
                            ["agent-improve/docs/NEW.md"])
    assert exc.value.code == 1


def test_no_new_paths_means_the_rule_does_not_fire() -> None:
    """A commit that adds nothing needs no number, whatever its message says."""
    g.check_step_or_gap(_ROOT, "docs: an edit to a tracked file", "", [])


def test_tooling_work_needs_no_registration() -> None:
    """Founder ruling 2026-09-26: a `chore(tooling):` commit names no DEF id
    and passes on the checks alone — its new files need no number. Any other
    `chore(` still does."""
    g.check_step_or_gap(_ROOT, "chore(tooling): a new hook", "no trailer\n",
                        [".claude/hooks/new_hook.py"])
    with pytest.raises(SystemExit):
        g.check_step_or_gap(_ROOT, "chore(deps): a new file", "no trailer\n",
                            ["agent-improve/docs/NEW.md"])


# ══════════════════════════════════════════════════════════════════════════
# The two registers — the assertions that go red on a REFORMAT
# ══════════════════════════════════════════════════════════════════════════


def test_appendix_D_still_parses_into_step_numbers() -> None:
    """**Rule 8 is the fourth hook parsing this table**, and its header says so.

    If this goes red, Appendix D was reformatted and rule 8 stopped resolving
    steps — which would let every new file through while reporting success. The
    fix is the parser, never the table.
    """
    steps = set(g._APPENDIX_D_STEP_RE.findall(
        g._staged_text(_ROOT, g.cs.PROCEDURE)))
    assert len(steps) > 50, f"Appendix D parsed to {len(steps)} steps"
    assert {"6.25", "6.26", "2.3"} <= steps


def test_the_gap_register_still_parses_into_gap_numbers() -> None:
    """Same assertion for the register, which rule 8 is one of two hooks to parse.

    **The register is `docs/defects.json` since 2026-09-27** (founder), moved
    from the archived procedure's Appendix G. A closed gap is still an entry
    and must still resolve (G-52 was struck through in the old register),
    because a file added under a gap does not stop being scheduled when the
    gap closes. Read through `_known_gaps`, so a test pinned to one path does
    not assert the register emptied when it moves.
    """
    gaps = g._known_gaps(_ROOT)
    assert len(gaps) > 50, f"the register parsed to {len(gaps)} gaps"
    assert {"G-57", "G-52", "G-49"} <= gaps, "G-52 is struck through and must still parse"


def test_the_registers_are_read_from_the_INDEX_not_the_disk() -> None:
    """**This is §0.32's first clause applied to the guard's own reading.**

    `_staged_text` goes through `git show :<path>`, so what it returns is what
    the commit will contain. A gap registered in the same commit counts; a row
    edited on disk and left unstaged does not. Demonstrated by hand when the
    rule landed — `Gap: G-57` was refused with the row on disk and accepted
    once the row was staged — and pinned here so the demonstration survives.

    **It asserts the SOURCE, not a byte count.** An earlier cut compared
    `count("**Commit ")` between index and disk, which is equal only in a clean
    tree — so it went red on any working copy with an unstaged procedure edit,
    which is the normal state while writing a step. A test that fails for a
    reason unrelated to what it checks is a false-alarm generator, and this
    file already carries the argument for why that is not tolerable.

    The limit: when the tree is clean, index and disk agree, so the strong
    half of this test only bites when the path is genuinely dirty. That is
    stated rather than papered over.
    """
    rel = g.cs.PROCEDURE
    from_index = g._staged_text(_ROOT, rel)
    raw = subprocess.run(["git", "show", f":{rel}"], capture_output=True,
                         cwd=_ROOT).stdout.decode("utf-8", "replace")
    assert from_index == raw, "_staged_text no longer reads the index"

    on_disk = (Path(_ROOT) / rel).read_text(encoding="utf-8")
    if on_disk != raw:
        assert from_index != on_disk, (
            "the path is dirty and `_staged_text` returned the DISK content — "
            "the guard would resolve numbers against a version this commit is "
            "not making, which is the cached-copy failure §0.32 names")


def test_a_missing_register_fails_CLOSED() -> None:
    """A guard that cannot read its register BLOCKS. It never assumes.

    The whole file is fail-closed on this argument: a check that waves the
    commit through when its own logic breaks is worse than no check, because it
    is recorded as evidence.
    """
    with pytest.raises(RuntimeError):
        g._staged_text(_ROOT, "agent-improve/docs/NO_SUCH_REGISTER.md")


# ══════════════════════════════════════════════════════════════════════════
# The ratchet — what both rules deliberately cannot see
# ══════════════════════════════════════════════════════════════════════════


def test_both_rules_range_over_added_paths_only() -> None:
    """**The ratchet, and it is why the rules are adoptable.**

    Two `.bak` files are tracked deliberately under `docs/_archive/`. A rule
    reading every staged path would block every commit that touched one, and a
    guard people route around with --no-verify is worse than no guard — rule 3's
    argument, applied to paths. `added_paths` filters `AR`, so a modification is
    invisible to both rules.
    """
    src = _HOOK.read_text(encoding="utf-8")
    assert "--diff-filter=AR" in src, "added_paths stopped filtering to added/renamed"
    assert "check_scratch(added)" in src, "rule 7 stopped reading the added set"
    assert "check_step_or_gap(root, subject, message, added)" in src


def test_the_tracked_bak_archives_are_the_reason_for_the_ratchet() -> None:
    """Named, not assumed: the exemption exists because these files exist."""
    tracked = subprocess.run(
        ["git", "ls-files", "agent-improve/docs/_archive/"],
        capture_output=True, text=True, cwd=_ROOT,
    ).stdout
    assert ".bak" in tracked, (
        "no tracked .bak remains — if these were removed the ratchet's stated "
        "reason is gone and rule 7 could range over every staged path instead")


def test_a_rename_into_a_scratch_name_is_caught() -> None:
    """`git mv REPORT.md REPORT.md.bak` adds nothing and is still scratch entering
    the tree at a new name. `R` is in the filter for exactly this.
    """
    assert g.scratch_reason("agent-improve/docs/REPORT.md.bak")


# ══════════════════════════════════════════════════════════════════════════
# Both rules bind on EVERY commit — not only on the spine
# ══════════════════════════════════════════════════════════════════════════


def test_the_rules_run_ahead_of_the_prefix_gate() -> None:
    """A draft lands under a `docs(` subject as easily as under a `refactor(`.

    Scoping these to the spine prefix would exempt exactly the commits nobody
    reviews against it — the argument that put rule 2b ahead of the gate, and
    the reason both calls sit above the prefix gate (`gated_rules`) in `main`.
    """
    src = _HOOK.read_text(encoding="utf-8")
    scratch_at = src.index("check_scratch(added)")
    number_at = src.index("check_step_or_gap(root, subject, message, added)")
    gate_at = src.index("rules = gated_rules(subject, all_staged)")
    assert scratch_at < gate_at and number_at < gate_at


# ══════════════════════════════════════════════════════════════════════════
# Rule 17 — design stays true (replaces rule 2b, founder ruling 2026-09-27)
# ══════════════════════════════════════════════════════════════════════════

#: Paths a generator rewrites on every commit. A file ARCHITECTURE.md §3 names
#: must be a source of truth, never one of these (the invariant rule 2b's watch
#: list was held to, carried over).
GENERATED_PATHS = {
    "agent-improve/docs/control-board.html": "build_control_board.py",
    "agent-improve/docs/CONTINUITY.md": "pre-commit-continuity.py",
    "agent-improve/docs/test-results.json": "the pre-commit full run",
    "agent-improve/docs/section-index.md": "section_index.py",
}


def _named() -> set:
    return g.design_files((Path(_ROOT) / "agent-improve" / "ARCHITECTURE.md").read_text(encoding="utf-8"),
                          (Path(_ROOT) / "agent-improve" / "docs" / "code-layout.md").read_text(encoding="utf-8"))


def test_the_named_files_are_sources_of_truth_that_exist_and_have_teeth() -> None:
    named = _named()
    assert len(named) >= 20, f"ARCHITECTURE.md §3 names only {len(named)} files — rule 17 lost its teeth"
    missing = sorted(p for p in named if not (Path(_ROOT) / p).exists())
    assert not missing, f"ARCHITECTURE.md §3 names files that do not exist: {missing}"
    assert not named & set(GENERATED_PATHS), named & set(GENERATED_PATHS)
    for p in ("agent-improve/backend/phases/nodes_common.py", "agent-improve/backend/gateway/routes.py",
              "agent-improve/backend/core/checkpointer.py", "agent-improve/ui/index.html",
              "agent-improve/backend/phases/analyse/validate.py", "agent-improve/scripts/ingest_knowledge.py"):
        assert p in named, p


def test_design_files_reads_section_3_only_joins_folders_and_expands_phases() -> None:
    doc = NEWLINE.join([
        "## 2. Architecture", "`core/graph.py` is outside §3", "",
        "## 3. Components and interfaces", "",
        "| Folder | File | Holds |", "|---|---|---|",
        "| `core/` | `state.py` C | x |", "| | `llm.py` | y |",
        "| `phases/` | `{phase}/validate.py` | z |", "| — | `escalate.py` | e |", "",
        "Built in `phases/nodes_common.py::_build_executor`; the UI is `ui/index.html`.", "",
        "## 4. Data models", "`core/store.py` is outside §3"])
    named = g.design_files(doc)
    assert "agent-improve/backend/core/state.py" in named and "agent-improve/backend/core/llm.py" in named
    assert "agent-improve/backend/phases/control/validate.py" in named
    assert "agent-improve/backend/escalate.py" in named
    assert "agent-improve/backend/phases/nodes_common.py" in named and "agent-improve/ui/index.html" in named
    assert "agent-improve/backend/core/graph.py" not in named and "agent-improve/backend/core/store.py" not in named


def test_the_design_trailer_is_a_whole_line() -> None:
    assert g.DESIGN_TRAILER_RE.search("body" + NEWLINE + NEWLINE + "Design: unchanged" + NEWLINE)
    assert not g.DESIGN_TRAILER_RE.search("the Design: unchanged? no" + NEWLINE)


# Rule 9 (the build matrix) retired with the procedure at step 6.67; its tests are in
# docs/_archive/retired-tooling/tests/test_commit_guard_rule9.py.


# ══════════════════════════════════════════════════════════════════════════
# Types, tests and landing bind on EVERY code commit (founder ruling 2026-09-26)
# ══════════════════════════════════════════════════════════════════════════

CODE = ["agent-improve/backend/phases/define/report.py"]
DOCS = ["agent-improve/docs/harness-progress.md", "agent-improve/docs/control-board.html",
        "agent-improve/docs/test-results.json"]


@pytest.mark.parametrize("subject,staged,expected", [
    ("feat(define): a report section", CODE, ("11", "3", "3b", "4")),
    ("fix(ui): a label", ["agent-improve/ui/index.html"], ("11", "3", "3b", "4")),
    ("chore(tooling): a hook", [".claude/hooks/timing.py"], ("11", "3", "3b", "4")),
    ("chore(tooling): the budget", [".claude/config/size-budget.json"], ("11", "3", "3b", "4")),
    ("docs(requirements): a note", DOCS, ()),
    ("refactor(arch-v2): DEF-065 — x", DOCS, ("1", "11", "5", "3", "3b", "4")),
    ("refactor(arch-v2): DEF-065 — x", CODE, ("1", "11", "5", "3", "3b", "4")),
])
def test_types_tests_and_landing_apply_to_every_code_commit(subject, staged, expected) -> None:
    """A `feat(` commit carried two type errors to main (b940725) because rules
    3, 4 and 11 ran only under `refactor(arch-v2)`. Code or config, whatever the
    prefix, now gets all three; the spine keeps rules 1 and 5 besides."""
    assert g.gated_rules(subject, staged) == expected


def test_the_generated_outputs_alone_are_not_a_code_change() -> None:
    assert not g.changes_code(DOCS)
    assert g.changes_code(DOCS + [".githooks/pre-commit"])


def test_a_def_subject_lands_under_any_prefix() -> None:
    for subject in ("refactor(arch-v2): DEF-065 — x", "feat(define): DEF-065 — x", "fix: DEF-065 — x"):
        m = g._DEF_SUBJECT_RE.match(subject)
        assert m and m.group(1) == "DEF-065", subject
    assert not g._DEF_SUBJECT_RE.match("feat(define): requirements v2 part 8 — DEF-065")


# ══════════════════════════════════════════════════════════════════════════
# Rule 3b — the whole-tree type-error count may fall, never rise (2026-09-27)
# ══════════════════════════════════════════════════════════════════════════


def _ratchet():
    import sys
    sys.path.insert(0, str(Path(_ROOT) / ".claude" / "hooks"))
    import mypy_ratchet
    return mypy_ratchet


def test_the_ratchet_refuses_a_rise_a_raised_record_and_an_unfollowed_fall() -> None:
    mr = _ratchet()
    assert mr.refusal(67, 67, 67) == []
    assert mr.refusal(66, 66, 67) == [], "a record lowered with the count passes"
    assert "ROSE" in " ".join(mr.refusal(68, 67, 67))
    assert "RAISED" in " ".join(mr.refusal(68, 68, 67)), "raising the record by hand is refused"
    assert "FELL" in " ".join(mr.refusal(65, 67, 67)), "a fall the record did not follow is refused"
    assert mr.refusal(10, 10, None) == [], "the first commit of the record has no HEAD to compare"


def test_the_ratchet_counts_errors_and_nothing_else() -> None:
    mr = _ratchet()
    text = NEWLINE.join(["backend/a.py:3: error: Bad  [x]", "backend/a.py:4: note: see",
                         "scripts/b.py:9: error: Worse  [y]", ""])
    assert len(mr._ERROR.findall(text)) == 2


def test_the_record_is_committed_and_the_hooks_run_it() -> None:
    import json
    mr = _ratchet()
    data = json.loads((Path(_ROOT) / mr.RATCHET).read_text(encoding="utf-8"))
    assert isinstance(data["count"], int) and data["count"] >= 0
    assert "never rise" in data["_rule"]
    hook = (Path(_ROOT) / ".githooks" / "pre-commit").read_text(encoding="utf-8")
    assert "mypy_ratchet.py --lower" in hook
    assert '("3b", spine or code)' in _HOOK.read_text(encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════
# Rule 15 and rule 2b's skip — what counts as ANNOTATION-ONLY (2026-09-27)
# ══════════════════════════════════════════════════════════════════════════


def _ao():
    import sys
    sys.path.insert(0, str(Path(_ROOT) / ".claude" / "hooks"))
    import annotation_only
    return annotation_only


BASE = NEWLINE.join([
    "from typing import Any",
    "def run(graph, state: dict, n: int = 1) -> dict:",
    "    out: list = []  # a note",
    "    return {'s': state, 'n': n}",
    "class Model:",
    "    field: int",
    ""])


@pytest.mark.parametrize("new", [
    BASE.replace("state: dict", "state: Any"),                                  # a parameter
    BASE.replace(") -> dict:", ") -> dict[str, Any]:"),                        # a return
    BASE.replace("out: list = []", "out: list[int] = []"),                      # a local
    BASE.replace("from typing import Any", "from typing import Any, List"),     # a typing import
    BASE.replace("  # a note", "  # another note"),                             # a comment
    BASE.replace("def run(", "# why the state is Any" + NEWLINE + "def run("),  # a comment line
])
def test_these_changes_are_annotation_only(new: str) -> None:
    assert _ao().is_annotation_only(BASE, new)


@pytest.mark.parametrize("new", [
    BASE.replace("'n': n", "'n': n + 1"),                                       # behaviour
    BASE.replace("field: int", "field: str"),                                   # a model field
    BASE.replace("def run(", "@tool" + NEWLINE + "def run(").replace("state: dict", "state: Any"),
    BASE.replace("    out:", "    '''doc'''" + NEWLINE + "    out:"),           # a docstring
])
def test_these_changes_are_not(new: str) -> None:
    assert not _ao().is_annotation_only(BASE, new)


def test_added_deleted_and_unparseable_files_are_not_annotation_only() -> None:
    ao = _ao()
    assert not ao.is_annotation_only(None, BASE)
    assert not ao.is_annotation_only(BASE, None)
    assert not ao.is_annotation_only(BASE, "def (")


def test_the_two_commits_that_prompted_the_rule_classify_as_ruled() -> None:
    """82b9251's backend changes were annotations only (2b need not have fired);
    8f26a04's config.py change was behaviour under `chore(config)` (rule 15 refuses)."""
    ao = _ao()

    def show(spec: str) -> str:
        return subprocess.run(["git", "show", spec], cwd=_ROOT, capture_output=True,
                              encoding="utf-8", errors="replace").stdout
    for f in ("agent-improve/backend/core/checkpointer.py", "agent-improve/backend/gateway/routes.py"):
        assert ao.is_annotation_only(show(f"82b9251~1:{f}"), show(f"82b9251:{f}")), f
    f = "agent-improve/backend/core/config.py"
    assert not ao.is_annotation_only(show(f"8f26a04~1:{f}"), show(f"8f26a04:{f}"))


@pytest.mark.parametrize("subject,message,staged,refused", [
    ("chore(config): x", "", ["agent-improve/backend/core/config.py"], True),
    ("chore: x", "", ["agent-improve/backend/core/config.py"], True),
    ("chore(config): x", "body\n\nGap: G-112\n", ["agent-improve/backend/core/config.py"], False),
    ("fix(config): x", "", ["agent-improve/backend/core/config.py"], False),
    ("chore(tooling): x", "", [".claude/hooks/timing.py"], False),
    ("chore(tooling): x", "", ["agent-improve/backend/tests/test_turn_budget.py"], False),
])
def test_rule_15_refuses_a_chore_that_changes_backend_behaviour(
        monkeypatch, subject, message, staged, refused) -> None:
    ao = _ao()
    monkeypatch.setattr(ao, "staged_is_annotation_only", lambda root, p: False)
    if refused:
        with pytest.raises(SystemExit):
            g.check_chore_scope(_ROOT, subject, message, staged)
    else:
        g.check_chore_scope(_ROOT, subject, message, staged)


def test_rule_15_passes_a_chore_that_only_annotates(monkeypatch) -> None:
    ao = _ao()
    monkeypatch.setattr(ao, "staged_is_annotation_only", lambda root, p: True)
    g.check_chore_scope(_ROOT, "chore(types): x", "", ["agent-improve/backend/core/checkpointer.py"])


def test_rule_17_passes_annotations_the_trailer_or_a_design_change_and_fires_otherwise(monkeypatch) -> None:
    ao = _ao()
    named = "agent-improve/backend/phases/nodes_common.py"
    monkeypatch.setattr(g, "_staged_text", lambda root, rel: (Path(_ROOT) / rel).read_text(encoding="utf-8"))
    monkeypatch.setattr(g, "_status_changed_by_hand", lambda root: False)
    monkeypatch.setattr(ao, "staged_is_annotation_only", lambda root, p: True)
    g.check_design(_ROOT, "", [named])                                       # annotations only
    monkeypatch.setattr(ao, "staged_is_annotation_only", lambda root, p: False)
    g.check_design(_ROOT, "x" + NEWLINE + NEWLINE + "Design: unchanged" + NEWLINE, [named])
    with pytest.raises(SystemExit):
        g.check_design(_ROOT, "", [named])                                   # behaviour, no word
    monkeypatch.setattr(g, "_status_changed_by_hand", lambda root: True)
    g.check_design(_ROOT, "", [named, "agent-improve/ARCHITECTURE.md"])       # the design moved with it
    # not named in §3 — since 2026-09-30 §3.1's layout is generated over every backend module, so the
    # unnamed example is a script outside backend/
    g.check_design(_ROOT, "", ["agent-improve/scripts/move_proof_661.py"])


def test_the_suite_runs_serial_tests_alone_after_the_parallel_pass() -> None:
    src = (Path(_ROOT) / ".claude" / "hooks" / "staged_tree.py").read_text(encoding="utf-8")
    # Founder ruling 4, 2026-09-28 (G-127): `wallclock` tests leave both passes for the run-through stage.
    # Controls review item 1 (2026-09-30): the parallel pass steals work.
    assert '"-n", "auto", "--dist", "worksteal", "-m", "not serial and not wallclock"' in src
    assert '"-n", "0", "-m", "serial and not wallclock"' in src
    budget = (Path(_ROOT) / "agent-improve" / "backend" / "tests" / "test_turn_budget.py").read_text(
        encoding="utf-8")
    assert "@pytest.mark.serial" + NEWLINE + "def test_no_knowledge_tool_blocks_the_loop" in budget
    assert "@pytest.mark.wallclock" + NEWLINE + "def test_a_slow_turn_answers_before_the_wall" in budget

