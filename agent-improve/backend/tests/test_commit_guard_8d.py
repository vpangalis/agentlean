"""Rule 6 of the commit-msg guard — the 8D body on a fix commit (CLAUDE.md §20).

WHY THIS FILE EXISTS
--------------------
**A gate exists to outlive the discipline it enforces, so it has to outlive its
own author's assumptions too.** §20's own argument is that *"convention decays;
a gate does not"* — and a gate with no test is a convention wearing a gate's
clothes. `.githooks/commit-msg` runs this rule on every commit in the repository;
nothing else re-runs its logic, and a regex that stops matching fails SILENTLY by
letting commits through, which is the one failure mode a gate must not have.

WHAT IS PINNED, AND WHAT DELIBERATELY IS NOT
--------------------------------------------
Pinned: which commits are gated (three triggers), which six labels are required,
that an empty discipline needs the word NONE **and** a reason, and that the
opt-out cannot exempt a commit that calls itself a fix.

Not pinned, because the rule cannot check it: whether an answer is CORRECT. A
plausible `D4 ESCAPE` naming the wrong blind spot passes the gate. That limit is
stated in `check_8d`'s docstring and restated here so a green suite is not read
as evidence of good 8D work.

THE FIXTURE IS A REAL MESSAGE
-----------------------------
`_full()` is the body G-49's fix would carry, not a lorem-ipsum stand-in, so a
change to the label vocabulary breaks these tests against something a human
would actually have written.
"""
from __future__ import annotations

import importlib.util
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
    spec = importlib.util.spec_from_file_location("commit_msg_guard", _HOOK)
    assert spec and spec.loader, f"cannot load {_HOOK}"
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


#: `Any`, not the module type: on a clone without the hook this is None and
#: every test is skipped, so the attribute access below is unreachable rather
#: than unsafe. Annotating it keeps rule 3 clean without a cast per call.
g: Any = _guard() if _HOOK.exists() else None

SUBJECT = "fix(executor): the plan reaches the model"

_ANSWERS = {
    "D2 IS": ("a Define turn on IMPR-2026-ED8 with an unread upload times out "
              "at 45s after 18 evidence searches and no uploads/ blob fetch"),
    "D2 IS-NOT": ("not a retrieval-quality problem and not the hop cap, which "
                  "fired correctly and returned documents"),
    "D4 OCCURRENCE": ("the executor invoked the agent with messages only, so "
                      "the plan never entered the request"),
    "D4 ESCAPE": ("no test asserted what the model RECEIVES; every executor "
                  "test stubbed create_agent and asserted its kwargs"),
    "D5 FIX": ("the node executes the routed call itself — transport C, which "
               "makes the guarantee deterministic"),
    "D7 PREVENT": ("a channel-agnostic assertion on the model request, run for "
                   "all five phases, so a future transport is covered too"),
}


def _full(**overrides: str) -> str:
    """The whole message, with any discipline replaced or dropped (`""`)."""
    answers = dict(_ANSWERS)
    answers.update(overrides)
    body = "\n".join(f"{label}: {text}" for label, text in answers.items() if text)
    return (f"{SUBJECT}\n\n{body}\n\n"
            "Co-Authored-By: Claude Opus 5 (1M context) <noreply@anthropic.com>\n")


def _blocked(subject: str, message: str) -> list[str]:
    """The labels rule 6 rejects — empty means the commit passes."""
    found = g.eightd_disciplines(message)
    return [name for name, _ in g.EIGHTD if g.eightd_verdict(found[name])]


# ══════════════════════════════════════════════════════════════════════════
# Which commits are gated — the three triggers
# ══════════════════════════════════════════════════════════════════════════


@pytest.mark.parametrize("subject", [
    "fix: the executor calls the tool",
    "fix(executor): the executor calls the tool",
    "fix!: the executor calls the tool",
    "hotfix: the executor calls the tool",
    "FIX(executor): case is not a way out",
])
def test_a_fix_type_is_always_gated(subject: str) -> None:
    """Trigger 1. Case-insensitive, scoped or not, breaking-change bang or not."""
    assert g.is_fix_commit(subject, "body with no labels\n")


def test_a_defect_code_in_the_subject_is_gated() -> None:
    """Trigger 2 — this project's fixes land as spine commits, not as `fix(`.

    G-49's own fix lands as `refactor(arch-v2): commit 6.21`. A type-only
    trigger would have exempted the single most important fix commit in the
    backlog, which is how a gate becomes decorative.
    """
    for subject in ("refactor(arch-v2): commit 6.21 — G-49's transport lands",
                    "refactor(arch-v2): commit 7.1 — F-15 is checked",
                    "refactor(arch-v2): commit 6.7 — WATCH 26's hop cap"):
        assert g.is_fix_commit(subject, "no labels here\n"), subject


def test_a_defect_code_in_the_BODY_alone_is_not_gated() -> None:
    """Deliberately subject-only.

    Half the commits in this log mention a G-number in passing — the board
    commit that named every chip mentions four. A rule that fired on a mention
    would be routed around within a week, and a routed-around gate is worse
    than none (rule 3's ratchet argument, applied to a message check).
    """
    assert not g.is_fix_commit(
        "governance: the board names every number",
        "The chips now read G-47, G-49, G-50 and G-51 with their names.\n")


def test_one_label_opts_the_whole_body_in() -> None:
    """Trigger 3 — a half-written 8D is what a presence check invites."""
    why = g.is_fix_commit("chore: tidy the logs",
                          "chore: tidy the logs\n\nD2 IS: the log was unreadable.\n")
    assert why == "the body already carries an 8D label"


# ══════════════════════════════════════════════════════════════════════════
# The opt-out, and the two things it may never exempt
# ══════════════════════════════════════════════════════════════════════════


def test_the_opt_out_clears_a_defect_code_subject() -> None:
    """A register-row edit is not a fix, and says so on the record.

    On the record beats `--no-verify`: the declaration is greppable and
    auditable, where a bypass leaves nothing behind at all.
    """
    assert not g.is_fix_commit(
        "docs: G-49's register row gains the cause",
        "8D: NOT A FIX — a register row edit; no code path changes here.\n")


def test_the_opt_out_needs_a_reason() -> None:
    assert g.is_fix_commit("docs: G-49's register row gains the cause",
                           "8D: NOT A FIX\n")


def test_the_opt_out_cannot_exempt_a_fix_subject() -> None:
    """**A commit that calls itself a fix does not get to opt out of being one.**"""
    assert g.is_fix_commit("fix(executor): the plan reaches the model",
                           "8D: NOT A FIX — I would rather not write six lines.\n")


def test_the_opt_out_cannot_exempt_a_body_that_carries_labels() -> None:
    assert g.is_fix_commit(
        "docs: G-49's row",
        "8D: NOT A FIX — only a row edit, honestly\nD2 IS: it times out\n")


# ══════════════════════════════════════════════════════════════════════════
# What the six disciplines have to contain
# ══════════════════════════════════════════════════════════════════════════


def test_a_complete_8d_passes() -> None:
    assert _blocked(SUBJECT, _full()) == []


@pytest.mark.parametrize("label", [
    "D2 IS", "D2 IS-NOT", "D4 OCCURRENCE", "D4 ESCAPE", "D5 FIX", "D7 PREVENT",
])
def test_each_discipline_is_required_on_its_own(label: str) -> None:
    """Drop exactly one and the commit fails naming exactly that one.

    Parametrised rather than looped so a failure says WHICH discipline stopped
    being enforced.
    """
    assert _blocked(SUBJECT, _full(**{label: ""})) == [label]


def test_the_missing_D4_ESCAPE_is_the_case_this_rule_was_written_for() -> None:
    """§20's first weight-bearing clause, as a test.

    Five answered disciplines and no escape cause is the shape of a fix that
    repairs the instance and leaves the blind spot — so the four others passing
    must not carry the commit.
    """
    assert _blocked(SUBJECT, _full(**{"D4 ESCAPE": ""})) == ["D4 ESCAPE"]


def test_an_empty_discipline_passes_with_the_word_NONE_and_a_reason() -> None:
    """§20: *an empty discipline is a finding and says so.*

    G-49's D3 and D7 are empty, and §20 calls that the most useful thing the
    structure produced.
    """
    reasoned = ("NONE — the class needs a bound-tool ordering rule, which is a "
                "§17 amendment and its own step")
    assert _blocked(SUBJECT, _full(**{"D7 PREVENT": reasoned})) == []


@pytest.mark.parametrize("content", ["NONE", "NONE.", "NONE — n/a", "none"])
def test_a_bare_NONE_does_not_pass(content: str) -> None:
    """The reason IS the finding. Without it the word is a way through the gate."""
    assert _blocked(SUBJECT, _full(**{"D7 PREVENT": content})) == ["D7 PREVENT"]


@pytest.mark.parametrize("content", ["tbd", "see above", "unknown", "n/a"])
def test_a_token_answer_is_treated_as_empty(content: str) -> None:
    """What a decaying convention produces, and what a presence check misses."""
    assert _blocked(SUBJECT, _full(**{"D4 ESCAPE": content})) == ["D4 ESCAPE"]


# ══════════════════════════════════════════════════════════════════════════
# Parsing — the ways a real message differs from a fixture
# ══════════════════════════════════════════════════════════════════════════


def test_an_answer_may_run_over_several_lines() -> None:
    """The interesting answers are paragraphs, not one-liners."""
    message = _full(**{"D4 ESCAPE": ""}).replace(
        "D5 FIX:",
        "D4 ESCAPE: no test asserted what the model receives.\n"
        "    Every executor test stubbed create_agent and read its kwargs,\n"
        "    so the middleware that composes the request never ran.\n"
        "D5 FIX:")
    found = g.eightd_disciplines(message)
    assert "middleware that composes the request" in found["D4 ESCAPE"]
    assert _blocked(SUBJECT, message) == []


def test_the_trailer_block_is_not_swallowed_by_the_last_discipline() -> None:
    found = g.eightd_disciplines(_full())
    assert "Co-Authored-By" not in (found["D7 PREVENT"] or "")


def test_D2_IS_does_not_match_the_IS_NOT_line() -> None:
    """Two labels share a prefix, and a greedy match would read one as both.

    With `D2 IS` matching `D2 IS-NOT`, a body carrying only IS-NOT would report
    both answered — the exact half-written 8D trigger 3 exists to catch.
    """
    message = f"{SUBJECT}\n\nD2 IS-NOT: not the hop cap and not retrieval quality\n"
    found = g.eightd_disciplines(message)
    assert found["D2 IS"] is None
    assert found["D2 IS-NOT"] == "not the hop cap and not retrieval quality"


def test_labels_survive_emphasis_and_indentation() -> None:
    """Bodies get formatted by hand; the label is the content, not the markup."""
    message = _full(**{"D4 ESCAPE": ""}).replace(
        "D5 FIX:",
        "  **D4 ESCAPE**: no assertion existed on what the model receives\n"
        "D5 FIX:")
    assert _blocked(SUBJECT, message) == []


def test_a_comment_line_cannot_supply_a_discipline(tmp_path) -> None:
    """`read_message` strips `#` lines before rule 6 sees the message.

    git's own template is comments, and so is the verbose `>8` scissors block —
    which carries the whole staged diff. An 8D "answered" by the template, or by
    a diff hunk that happens to contain the word ESCAPE, would be a gate
    satisfied by git itself.
    """
    path = tmp_path / "COMMIT_EDITMSG"
    path.write_text(
        f"{SUBJECT}\n\n"
        "# D2 IS: a comment cannot answer a discipline\n"
        "  # D4 ESCAPE: nor can an indented one\n"
        "# ------------------------ >8 ------------------------\n"
        "# diff --git a/x b/x\n"
        "D5 FIX: this line is the only real content in the body\n",
        encoding="utf-8")

    subject, message = g.read_message(str(path))
    assert subject == SUBJECT
    found = g.eightd_disciplines(message)
    assert found["D2 IS"] is None and found["D4 ESCAPE"] is None
    assert found["D5 FIX"] == "this line is the only real content in the body"


def test_the_scissors_diff_cannot_answer_a_discipline(tmp_path) -> None:
    """The verbose-commit case, stated on its own because it is the sharp one.

    `git commit --verbose` appends the staged diff below the scissors line. A
    diff of THIS repository contains every one of the six labels — the guard's
    own source defines them — so a body-wide search over an unstripped message
    would pass every commit made with `-v`.
    """
    path = tmp_path / "COMMIT_EDITMSG"
    path.write_text(
        f"{SUBJECT}\n\nnothing answered here\n"
        "# ------------------------ >8 ------------------------\n"
        "# D2 IS: from the diff\n# D2 IS-NOT: from the diff\n"
        "# D4 OCCURRENCE: from the diff\n# D4 ESCAPE: from the diff\n"
        "# D5 FIX: from the diff\n# D7 PREVENT: from the diff\n",
        encoding="utf-8")

    subject, message = g.read_message(str(path))
    assert _blocked(subject, message) == [n for n, _ in g.EIGHTD], (
        "a -v commit answered its 8D out of the diff"
    )


# ══════════════════════════════════════════════════════════════════════════
# The rule's own shape
# ══════════════════════════════════════════════════════════════════════════


def test_the_six_labels_are_the_ratified_set() -> None:
    """Pinned separately, because deleting a label is the cheapest way to make
    this file stop complaining — the same hole `test_the_check_count_is_pinned`
    closes for the BUILT markers."""
    assert [name for name, _ in g.EIGHTD] == [
        "D2 IS", "D2 IS-NOT", "D4 OCCURRENCE", "D4 ESCAPE", "D5 FIX",
        "D7 PREVENT",
    ]


def test_the_guard_docstring_carries_rule_6() -> None:
    """The docstring is what a person reads when the gate blocks them."""
    doc = _HOOK.read_text(encoding="utf-8")
    assert "6. 8D" in doc
    assert "D4 ESCAPE" in doc
    assert "§20" in doc
