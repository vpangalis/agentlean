"""What the plan's statuses are derived FROM. No hand-typed status.

Two sources, each the one that owns the fact:
  Appendix H  — a capability row is green or red; a story is done when all its rows are green
  git log     — a step is done when `refactor(arch-v2): commit X.Y` exists, the same rule
                .claude/hooks/build_board.py applies to the board this page reads

Fail-CLOSED here: a register that cannot be read raises rather than reporting every row red,
because "0 proven" and "could not look" must never render the same. The pre-commit hook
that calls this is fail-soft, so a raise leaves the previous page in place and says so.
"""
import pathlib, re, subprocess

HERE = pathlib.Path(__file__).resolve().parent
PROCEDURE = HERE.parents[1] / "docs" / "REFACTORING_PROCEDURE.md"

_SPINE = re.compile(r"refactor\(arch-v2\):\s*commit\s+(\d+\.\d+)")
_STEP = re.compile(r"^\d+\.\d+$")
_ROW = re.compile(r"^\|\s*\*\*(\d+)\*\*\s*\|.*\|\s*(\U0001F7E2|\U0001F534)\s*\|[^|]*\|\s*$")


def register():
    """Appendix H's rows as {id: green?}. Raises if the appendix or its table is missing."""
    text = PROCEDURE.read_text(encoding="utf-8")
    start = text.find("\n## Appendix H")
    if start < 0:
        raise RuntimeError("Appendix H not found in %s" % PROCEDURE.name)
    end = text.find("\n## ", start + 1)
    rows = {}
    for line in text[start:end if end > 0 else None].splitlines():
        m = _ROW.match(line.strip())
        if m:
            rows[int(m.group(1))] = m.group(2) == "\U0001F7E2"
    if not rows:
        raise RuntimeError("Appendix H has no rows this reader recognises")
    return rows


def committed_steps():
    log = subprocess.run(["git", "log", "--pretty=%s"], cwd=HERE, capture_output=True,
                         encoding="utf-8", errors="replace", check=True).stdout
    return set(_SPINE.findall(log))


def built_from():
    """(short sha, subject) of HEAD — the commit this build sits on top of.

    In the pre-commit hook the commit being made does not exist yet, so a page
    built there is built from its PARENT: the same one-commit lag board.html has.
    A page whose sha is older than that parent is one whose last build failed.
    """
    out = subprocess.run(["git", "log", "-1", "--pretty=%h%x09%s"], cwd=HERE, capture_output=True,
                         encoding="utf-8", errors="replace", check=True).stdout.strip()
    sha, _, subject = out.partition("\t")
    return sha, subject


def is_step(code):
    return bool(_STEP.match(code))
