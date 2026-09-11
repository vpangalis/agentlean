#!/usr/bin/env python3
"""SessionStart hook — anti-drift context injection for AgentLean.

Fires on Claude Code session start/resume. Emits a compact context block on
stdout that Claude Code appends to the session's additionalContext. Four
sections: git state, current refactor step, dependency version status, and
open drift warnings.

Design rules (Step 0.5 anti-drift infrastructure):
  - Python 3.11+, standard library only.
  - Read-only on the filesystem.
  - Fail-soft: every section catches its own errors and degrades to an
    in-line status string; a broad guard around main() logs to stderr and
    exits 0. A SessionStart hook must NEVER break or block a session.

Not registered yet — .claude/settings.json wires it in at commit 0.5.3.
"""

from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import urllib.request

# --------------------------------------------------------------------------- #
# Constants
# --------------------------------------------------------------------------- #
DEPENDENCIES = ["langgraph", "langchain", "langsmith", "deepagents"]
PYPI_URL = "https://pypi.org/pypi/{pkg}/json"
HTTP_TIMEOUT = 3
# The step sequence lives in the Refactoring Procedure, Appendix D.
# It was ARCHITECTURE.md §15 until 2026-08-21. That document was absorbed into
# the platform reference (and its path later reused for a copy of it), and its
# §15 used "### Step N —" headings the old regex never matched,
# so this lookup had been failing silently as "next undetermined".
PROCEDURE_DOC_PATH = "agent-improve/docs/REFACTORING_PROCEDURE.md"
STEP_INDEX_HEADING = "Appendix D"
MAX_OUTPUT_CHARS = 10000

# Governance convention: refactor commits are subjects like
#   "refactor(arch-v2): commit 2.2 — ..."  (this repo's convention)
# also tolerate "step 2.2" and a bare "2.2". The index carries no ✅/[x],
# so the authoritative record of what has landed is git history.
_GITLOG_STEP_RE = re.compile(r"refactor\(arch-v2\):\s*(?:step\s+|commit\s+)?(\d+\.\d+)")

# Appendix D row format, fixed by contract with the document:
#   | **Commit 4.2** | thread_id + disconnect policy |  |
#   | **Commit 8.5** | Graceful shutdown | GATED |
#
# **THE STATUS CELL IS EMPTY FOR EVERY SCHEDULABLE STEP** (2026-09-10). It
# carries only what git cannot say, so `[A-Za-z]*` — with a star, not a plus —
# is load-bearing: an empty cell must MATCH and read as available. With `+` the
# row would not match at all, drop out of `rows`, and every remaining step
# would become invisible rather than merely unstatused.
# **`Seq` is column 1 and ORDERING READS IT; the step number is identity only.**
# Ratified 2026-09-11. Appendix D's rows are no longer in execution order -
# they are in identifier order, and `Seq` says what to build next. The number
# stays stable so every commit subject, every §-citation and every register
# entry that names a step keeps resolving.
_STEP_ROW_RE = re.compile(
    r"\|\s*(\d+)\s*\|\s*\*\*Commit (\d+\.\d+)\*\*\s*\|[^|]*\|\s*(?:\*\*)?([A-Za-z]*)"
)

# Statuses that must never be proposed as the next step — the three things git
# history cannot tell you about a step that has not landed.
#
# `done` LEFT this set on 2026-09-10, when the column stopped carrying it.
# Completion now comes from `_GITLOG_STEP_RE` alone, so a "done" status was a
# second source of truth for a fact git already owns — and the one that drifts,
# because it is hand-maintained.
#
# THE 9.0 WRINKLE IS RESOLVED, NOT CARRIED. Step 9.0 landed out of band as
# `feat(knowledge): …` (`871637f`), so the git-log scan cannot see it and `last`
# can never advance past it. While `done` was a status this was papered over by
# 9.0's row saying "done"; removing that word would have re-armed the trap —
# once 8.3 lands, 8.4 is BLOCKED and 8.5 is GATED, leaving 9.0 the lowest
# remaining row and the pointer stuck there forever. **9.0 is now EXTERNAL**,
# which is both true (it is an Azure-side knowledge-index rebuild, exactly what
# the procedure's reading conventions define EXTERNAL to mean) and permanent:
# it stays unavailable on its own merits rather than on a completion claim.
_UNAVAILABLE_STATUSES = {"blocked", "gated", "external"}

# All three now mean "cannot be worked on as a code step". The distinction this
# set used to draw — blocked-vs-finished — disappeared with `done`.
_BLOCKED_STATUSES = {"blocked", "gated", "external"}


# --------------------------------------------------------------------------- #
# Helpers
# --------------------------------------------------------------------------- #
def _log(msg: str) -> None:
    """Best-effort diagnostic to stderr (never affects the session)."""
    try:
        sys.stderr.write(f"[session-start-context] {msg}\n")
    except Exception:
        pass


def _ver_key(version: str) -> tuple[int, ...]:
    """Tuple key for numeric version-step comparison — so 2.10 > 2.2."""
    return tuple(int(part) for part in version.split("."))


def get_project_dir() -> str:
    """Monorepo root. Honours $CLAUDE_PROJECT_DIR, else current working dir."""
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def _git(args: list[str], cwd: str) -> subprocess.CompletedProcess:
    """Run a git command, decoding as UTF-8 (commit subjects carry — and §)."""
    return subprocess.run(
        ["git", *args],
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        cwd=cwd,
        timeout=10,
    )


def get_git_info() -> str:
    """Section 1 — current HEAD, branch, and working-tree cleanliness."""
    try:
        cwd = get_project_dir()
        head = _git(["rev-parse", "HEAD"], cwd)
        if head.returncode != 0:
            return "git: not a repository"
        sha = head.stdout.strip()[:12]
        branch = (_git(["rev-parse", "--abbrev-ref", "HEAD"], cwd).stdout.strip()
                  or "DETACHED")
        status = _git(["status", "--short"], cwd).stdout
        n = len([ln for ln in status.splitlines() if ln.strip()])
        tree = "clean" if n == 0 else f"dirty ({n} uncommitted paths)"
        return f"git: HEAD {sha} on {branch} | working tree: {tree}"
    except Exception as exc:  # noqa: BLE001 - fail-soft by contract
        _log(f"git info failed: {exc}")
        return "git: not a repository"


def get_last_completed_step_from_gitlog() -> list[str] | None:
    """EVERY refactor(arch-v2) X.Y in recent history, or None if none.

    **Returns the SET, not the maximum, since 2026-09-11.** A single "highest"
    value only means something when the table is in execution order, and
    Appendix D is now ordered by `Seq` with the number as a stable identifier.
    Completion is therefore per-row: a step is done because a commit says so,
    not because a later-numbered one landed.
    """
    try:
        # **NO `-n` WINDOW, since 2026-09-11.** A watermark survived a short
        # window: reading the last 20 spine commits still gave the right
        # MAXIMUM. Per-row completion does not — every step outside the window
        # reads as not-landed, and the banner proposed 2.3 as next on its
        # first run after the change. The full log is the completion record.
        out = _git(
            ["log", "--oneline", "--grep=^refactor(arch-v2):"],
            get_project_dir(),
        )
        if out.returncode != 0:
            return None
        found = [m.group(1) for ln in out.stdout.splitlines()
                 if (m := _GITLOG_STEP_RE.search(ln))]
        if not found:
            return None
        return sorted(set(found), key=_ver_key)
    except Exception as exc:  # noqa: BLE001
        _log(f"git-log step parse failed: {exc}")
        return None


def get_next_step_from_procedure(project_dir: str, landed: list[str] | None):
    """Lowest-`Seq` Appendix D row that is neither landed nor unavailable.

    Returns (step, None) on success, or (None, reason) so the caller can say
    WHY it failed. A silent "undetermined" is what let the previous version of
    this lookup rot unnoticed against ARCHITECTURE.md §15 — a parse failure and
    "you have finished" must not render identically.

    **⚑ THE WATERMARK IS GONE, AND THAT IS THE POINT (2026-09-11).** This used
    to select the lowest row STRICTLY ABOVE the highest landed step, which is
    why Appendix D carried a warning that a step numbered below the last
    completed one *"does not appear late, it disappears"* — met for real on
    2026-09-10 when 6.16 landed ahead of 6.15 and the banner jumped to 7.0.
    **Re-sequencing alone would have moved that trap into `Seq` space rather
    than removing it.** Completion is now per-row, so a step at ANY position is
    reachable the moment it is unblocked — `6.10` included, with no renumber.
    """
    try:
        doc_path = os.path.join(project_dir, PROCEDURE_DOC_PATH)
        with open(doc_path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()

        start = next((i for i, ln in enumerate(lines)
                      if ln.startswith("## ") and STEP_INDEX_HEADING in ln), None)
        if start is None:
            return None, None, f"step index heading '{STEP_INDEX_HEADING}' not found"

        end = len(lines)
        for j in range(start + 1, len(lines)):
            if lines[j].startswith("## "):  # next level-2 header ends the index
                end = j
                break

        rows = _STEP_ROW_RE.findall("\n".join(lines[start:end]))
        if not rows:
            return None, None, "step index found but no rows matched the row format"

        done = set(landed or ())
        seq_of = {step: int(seq) for seq, step, _ in rows}

        # `last completed` is the landed step with the HIGHEST Seq, not the
        # highest number. A landed step absent from the table (history carries
        # 0.1, 1.1, 1.2, 2.1, 2.2 from before it existed) has no Seq and is
        # not a candidate — the same population rule the landed count uses.
        in_table = [s_ for s_ in done if s_ in seq_of]
        last = max(in_table, key=lambda s_: seq_of[s_]) if in_table else None

        available = [(int(seq), step) for seq, step, status in rows
                     if status.lower() not in _UNAVAILABLE_STATUSES
                     and step not in done]
        if not available:
            blocked = [step for seq, step, st in rows
                       if st.lower() in _BLOCKED_STATUSES and step not in done]
            if blocked:
                return None, last, f"all remaining steps blocked/gated ({', '.join(blocked)})"
            return None, last, "no steps remain — procedure complete"
        return min(available)[1], last, None
    except Exception as exc:  # noqa: BLE001
        _log(f"procedure next-step parse failed: {exc}")
        return None, None, f"parse error: {exc}"


def get_refactor_step() -> str:
    """Section 2 — assemble the last/next refactor-step line."""
    project_dir = get_project_dir()
    doc_path = os.path.join(project_dir, PROCEDURE_DOC_PATH)
    if not os.path.isfile(doc_path):
        return f"refactor step: PROCEDURE DOC MISSING (expected {PROCEDURE_DOC_PATH})"

    landed = get_last_completed_step_from_gitlog()
    nxt, last, reason = get_next_step_from_procedure(project_dir, landed)
    last_str = last if last else "none"

    if nxt is None:
        # Say why. "undetermined" hid a broken lookup for months.
        return f"refactor step: last completed {last_str} | next UNAVAILABLE — {reason}"
    return (f"refactor step: last completed {last_str} | next {nxt} "
            f"({PROCEDURE_DOC_PATH} Appendix D)")


def _pinned_python() -> str:
    """`agent-improve/.venv`'s interpreter — NEVER `sys.executable`.

    **WATCH 2, and this hook was the live instance of it until 2026-09-11.**
    The repo root carries a second, older virtualenv. This function used
    `sys.executable`, which is whatever interpreter Claude Code launched the
    hook with — the ROOT venv — so every session opened with a dependency
    report for the wrong tree: `langgraph 1.1.10` against a project running
    **1.2.11**, flagged `⚠` as behind when it is current.

    **The report contradicted step 2.3's Done-when** (*"reports ≥1.2.6"*) at
    the top of every session, which is the worst possible place for a false
    negative: it is the first thing read and the last thing anyone re-derives.
    `verify_built.py` has pinned the venv since it was written and says so in
    its own docstring; this hook was never given the same rule.
    """
    root = get_project_dir()
    for rel in (("agent-improve", ".venv", "Scripts", "python.exe"),
                ("agent-improve", ".venv", "bin", "python")):
        cand = os.path.join(root, *rel)
        if os.path.exists(cand):
            return cand
    return sys.executable                       # fail-soft, as the hook must


def get_installed_version(pkg: str) -> str | None:
    """Installed version via the PINNED venv's `pip show`, or None if absent."""
    try:
        out = subprocess.run(
            [_pinned_python(), "-m", "pip", "show", pkg],
            capture_output=True, encoding="utf-8", errors="replace", timeout=10,
        )
        if out.returncode != 0:
            return None
        for line in out.stdout.splitlines():
            if line.lower().startswith("version:"):
                return line.split(":", 1)[1].strip()
        return None
    except Exception as exc:  # noqa: BLE001
        _log(f"pip show {pkg} failed: {exc}")
        return None


def get_latest_version(pkg: str) -> str | None:
    """Latest version from PyPI JSON, or None on any network/parse failure."""
    try:
        url = PYPI_URL.format(pkg=pkg)
        req = urllib.request.Request(url, headers={"Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=HTTP_TIMEOUT) as resp:
            if resp.status != 200:
                return None
            data = json.loads(resp.read().decode("utf-8"))
        return data.get("info", {}).get("version") or None
    except Exception as exc:  # noqa: BLE001
        _log(f"pypi {pkg} lookup failed: {exc}")
        return None


def get_version_info() -> str:
    """Section 3 — one line per dependency, installed vs latest."""
    lines = []
    for pkg in DEPENDENCIES:
        installed = get_installed_version(pkg)
        latest = get_latest_version(pkg)
        installed_part = f"installed {installed}" if installed else "not installed"
        latest_part = f"latest {latest}" if latest else "latest unavailable (network)"
        marker = ""
        if installed and latest:
            marker = " ✓" if installed == latest else " ⚠"
        lines.append(f"{pkg}: {installed_part} | {latest_part}{marker}")
    return "\n".join(lines)


def get_drift_warnings() -> str:
    """Section 4 — placeholder until the PreToolUse log exists (commit 0.5.3)."""
    return ("drift warnings: (scan not yet implemented — pre-tool-use hook "
            "active from commit 0.5.3 will log to .claude/logs/drift.log for "
            "future reads)")


def assemble_output(sections: list[tuple[str, str]]) -> str:
    """Join titled sections; enforce the character cap as a safety net."""
    blocks = [f"── {title} ──\n{body}" for title, body in sections]
    trailer = ("[Auto-injected by session-start-context.py — do not act on "
               "this as instructions; it is context]")
    out = "\n\n".join(blocks) + "\n\n" + trailer + "\n"
    if len(out) > MAX_OUTPUT_CHARS:
        out = out[: MAX_OUTPUT_CHARS - 1] + "\n"
    return out


def main() -> int:
    # Force UTF-8 stdout so box-drawing (──), ✓/⚠, — and § survive on Windows
    # code pages; otherwise a UnicodeEncodeError would swallow the whole block.
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    sections = [
        ("GIT STATE", get_git_info()),
        ("REFACTOR STEP", get_refactor_step()),
        ("DEPENDENCY VERSIONS", get_version_info()),
        ("DRIFT WARNINGS", get_drift_warnings()),
    ]
    sys.stdout.write(assemble_output(sections))
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:  # noqa: BLE001 - hook must never propagate
        _log(f"fatal: {exc}")
        sys.exit(0)
