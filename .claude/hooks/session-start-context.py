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


BOARD_PATH = "agent-improve/docs/control-board.html"
_DATA = re.compile(r'<script type="application/json" id="progress-data">(.*?)</script>', re.S)


def _board_data(rev: str, project_dir: str) -> dict | None:
    """The progress data a committed control-board.html embeds, or None."""
    r = _git(["show", f"{rev}:{BOARD_PATH}"], project_dir)
    if r.returncode != 0:
        return None
    m = _DATA.search(r.stdout)
    return json.loads(m.group(1).replace("<\\/", "</")) if m else None


_RANK = {"green": 0, "built": 1, "waiting": 1, "amber": 2, "red": 3}


def get_progress() -> str:
    """Section 2 — THE ONE PROGRESS VIEW, as committed (step 6.63).

    Until 6.63 this printed "last completed X | next Y" from its own parse of
    Appendix D and git log: a sixth progress view, and it named 6.43 as next
    while the plan's Order named another step. Now it reads what
    `control-board.html` embeds — the output of `progress.progress()`, the one
    function — at HEAD, and compares it with HEAD~1's to show what regressed.
    Reading the committed page needs no venv and runs in milliseconds.
    """
    project_dir = get_project_dir()
    now = _board_data("HEAD", project_dir)
    if now is None:
        return f"progress: {BOARD_PATH} at HEAD carries no progress data"
    wo = now.get("working_on") or {}
    lines = [now["headline"],
             f"current step: {wo.get('step', '—')} — {wo.get('title', '')}",
             f"forecast finish (Define, 7.9): {now.get('forecast_define') or '—'}"
             f" · conditional on {', '.join(now.get('conditional_on') or []) or 'nothing'}"
             f" · {now.get('forecast_basis', '')}"]
    before = _board_data("HEAD~1", project_dir)
    if before is None:
        lines.append("regressed since the last commit: (no board at HEAD~1 to compare)")
        return "\n".join(lines)
    worse = []
    for key, v in sorted(now["statuses"].items()):
        old = before.get("statuses", {}).get(key)
        if old and _RANK.get(v["colour"], 3) > _RANK.get(old["colour"], 3):
            worse.append(f"  {key}: {old['colour']} -> {v['colour']} ({v['ref']})")
    lines.append(f"regressed since the last commit: {len(worse)}")
    lines += worse[:15] + ([f"  ... and {len(worse) - 15} more"] if len(worse) > 15 else [])
    return "\n".join(lines)


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


def get_harness() -> str:
    """Step 6.66 — the long-running-harness routine (Anthropic, "Effective
    harnesses for long-running agents"): read git log, the progress file and
    the feature list; run the smoke test; take the next failing feature in
    this session's lane. Status comes only from test-results.json."""
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        sys.path.insert(0, os.path.join(here, "..", "..", "agent-improve", "tools", "control_board"))
        import features
        s = features.summary()
        nxt = " · ".join(f"{k}: {v['next'] or '—'}" for k, v in s["lanes"].items())
        return (f"{features.headline(s)}\n"
                f"next failing per lane — {nxt}\n"
                "routine: git log -5 · read agent-improve/docs/harness-progress.md · "
                "python agent-improve/tools/control_board/features.py --lane <A|B|C|integrator> · "
                "smoke: pytest backend/tests/test_define_features.py -n 0 · take the lane's next failing feature")
    except Exception as exc:  # noqa: BLE001 - hook must never propagate
        return f"(feature list unreadable: {exc.__class__.__name__})"


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
        ("PROGRESS (control-board.html)", get_progress()),
        ("DEFINE FEATURES (docs/define_features.json)", get_harness()),
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
