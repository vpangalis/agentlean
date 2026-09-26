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

IT ALSO CARRIES RULE 2b's WATCH-LIST INVARIANT
----------------------------------------------
**This is the guard's PATH-LIST test file**, and `STATUS_WATCHED` is one of its
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

    The row shape is `| **G-nn** |` for an open gap and `| ~~**G-nn**~~ |` for a
    closed one, and BOTH must parse: a closed gap is still a number that
    resolves, because a file added under a gap does not stop being scheduled
    when the gap closes.

    **Reads through `_known_gaps` since 6.37**, not through `STATUS_PATH`
    directly. The register moved to the procedure's Appendix G and
    `ARCHITECTURE.md` now parses to ZERO gap rows, so a test pinned to that one
    path asserted the register had been emptied rather than moved.
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
    the reason both calls sit above `startswith(GUARDED_PREFIX)` in `main`.
    """
    src = _HOOK.read_text(encoding="utf-8")
    scratch_at = src.index("check_scratch(added)")
    number_at = src.index("check_step_or_gap(root, subject, message, added)")
    gate_at = src.index("if not subject.startswith(GUARDED_PREFIX)")
    assert scratch_at < gate_at and number_at < gate_at


# ══════════════════════════════════════════════════════════════════════════
# Rule 2b's watch list — a source of truth, never a generator's output
# ══════════════════════════════════════════════════════════════════════════

#: Every path a generator in this repository writes, and what writes it. A
#: watched path may not appear here. Kept as data rather than inferred, because
#: inferring "is this generated" from file content is what missed the board:
#: `board.html` carries no DO-NOT-EDIT banner, and `routes.py` contains the word
#: "generated" in a user-facing error string and is hand-written.
GENERATED_PATHS = {
    "agent-improve/docs/board.html": "build_board.py rewrites the whole file",
    "agent-improve/docs/CONTINUITY.md": "pre-commit-continuity.py splices its status block",
    "agent-improve/docs/REFACTORING_PROCEDURE.md": "pre-commit-continuity.py splices its step board",
}


def test_no_watched_path_is_a_generators_output() -> None:
    """**The rule the list is held to, and the one the board broke.**

    A derived file changes when its INPUTS change, and `build_board.py` takes
    git log as an input — which moves on every commit. So a watch on it asks
    "did the generator run", never "did an architectural fact change", and the
    two are indistinguishable from inside the hook.

    **A gate that always fires is a gate that gets bypassed.** That is rule 3's
    argument for being a ratchet and rule 2b's own argument for being narrow,
    and it applies to 2b itself. Cost on the record: `ef59aa8`.
    """
    offenders = {p: GENERATED_PATHS[p] for p in g.STATUS_WATCHED
                 if p in GENERATED_PATHS}
    assert not offenders, (
        "rule 2b watches a DERIVED path, so it will fire on commits that change "
        f"no architectural fact: {offenders}. Verify a projection by "
        "REGENERATING it and comparing (verify_built.py), never by requiring a "
        "different file to be touched in the same commit."
    )


def test_every_watched_path_still_exists() -> None:
    """The opposite failure, and it is silent in the other direction.

    A watched path that has been renamed or deleted matches nothing and the rule
    simply never fires — no error, no warning. That is the class recorded twice
    already: a `paths:` glob rooted at `backend/**` when `.claude/` sits above
    it, and `.gitignore` carrying `ARTIFACTS/` against a directory named
    `_Artifacts/`.
    """
    missing = [w for w in g.STATUS_WATCHED
               if not (Path(_ROOT) / w.rstrip("/")).exists()]
    assert not missing, f"rule 2b watches paths that do not exist: {missing}"


def test_the_watch_list_still_has_teeth() -> None:
    """Removing an entry must not empty the rule. Guards the over-correction."""
    assert len(g.STATUS_WATCHED) >= 10, (
        f"STATUS_WATCHED is down to {len(g.STATUS_WATCHED)} entries — rule 2b "
        "was narrowed into irrelevance rather than corrected")


# ══════════════════════════════════════════════════════════════════════════
# Step 6.27 / G-58 — §55.2 and STATUS_WATCHED are ONE fact
# ══════════════════════════════════════════════════════════════════════════

#: §55.2 tabulates the watched paths for a human reader; the guard hardcodes
#: them for the gate. CLAUDE.md's *Facts have one owner* rule says a set is
#: stated once and cited everywhere else, and this is two copies of one set.
#:
#: **An equality test rather than a runtime read, deliberately.** Parsing a
#: prose section inside the hook would put a document on the critical path of
#: every commit and fail closed on a reformat — §55.2's block is authored for a
#: reader, not a data file. The assertion gets the ownership benefit without the
#: coupling: either copy may move, and the suite says so before the gate and the
#: document can disagree in production.
_ARCH_552_HEADING = "### 55.2"


def _watched_paths_from_arch() -> set:
    """The paths §55.2 tabulates, read from its fenced block ONLY.

    Anchored to the fence rather than to the whole section, because the removal
    note below the block names `board.html` twice and a section-wide scan would
    read those mentions as rows.
    """
    import re
    text = (Path(_ROOT) / "agent-improve" / "ARCHITECTURE.md").read_text(encoding="utf-8")
    section = text[text.index(_ARCH_552_HEADING):]
    end = section.find("\n## ")
    if end != -1:
        section = section[:end]
    fence = re.search(r"```[a-z]*\n(.*?)```", section, re.S)
    assert fence, "section 55.2 no longer carries a fenced path block"
    return {
        line.split()[0] for line in fence.group(1).splitlines()
        if line.strip().startswith("agent-improve/")
    }


def _norm(path: str) -> str:
    """`middleware/**` and `middleware/` are one entry in two notations.

    §55.2 writes a package as a glob because that is how it reads; the guard
    writes a trailing slash because `check_architecture_status` prefix-matches
    on it. Normalising is honest — asserting the raw strings match would not be.
    """
    return path.rstrip("*").rstrip("/")


def test_the_watch_list_and_ss552_state_the_same_paths() -> None:
    """**One fact, two owners — and it has already drifted twice.**

    The board was added to both on 2026-09-11 and removed from only the guard
    on 2026-09-14, so between `258d0dd` and step 6.27 the document said
    thirteen paths and the gate enforced twelve. The first drift cost
    `ef59aa8`; the second was created by the commit that fixed the first.
    """
    doc = {_norm(x) for x in _watched_paths_from_arch()}
    gate = {_norm(x) for x in g.STATUS_WATCHED}
    assert doc == gate, (
        "section 55.2 and STATUS_WATCHED disagree about which paths oblige an "
        "ARCHITECTURE.md re-check. "
        f"In 55.2 only: {sorted(doc - gate)}. "
        f"In the guard only: {sorted(gate - doc)}. "
        "One moved without the other; per CLAUDE.md's fact-ownership rule they "
        "are one fact, so fix whichever is wrong in the same commit."
    )


# Rule 9 (the build matrix) retired with the procedure at step 6.67; its tests are in
# docs/_archive/retired-tooling/tests/test_commit_guard_rule9.py.
