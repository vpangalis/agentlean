#!/usr/bin/env python3
"""PreToolUse hook — the pre-flight runs before every `git commit`. Step 6.66.

Claude Code hands this the tool call on stdin. A Bash or PowerShell command
that runs `git commit` (not `--dry-run`) triggers `preflight.run()`; a failure
blocks the call with exit 2, and stderr reaches Claude as the reason
(https://code.claude.com/docs/en/hooks — "exit code 2: blocking error").

FAIL-SOFT, the opposite of the commit-msg guard: the pre-flight is an
accelerator, the commit hook is the gate. If this hook itself breaks it lets
the call through and says so — it never wedges a commit.

6.68 (founder rulings 2026-09-26): it checks what is STAGED (a `commit -a` or
`--only` carries the working copy, so those are checked on disk), and there is
NO hand-written override — the `# preflight: acknowledged` comment is retired.
A failure passes only when the last commit's record already had it; that
comparison is `preflight.run`'s.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

COMMIT_RE = re.compile(r"(?:^|[;&|(\s])git(?:\s+-C\s+\S+|\s+-c\s+\S+)*\s+commit\b")
#: A commit that takes the working copy, not only the index.
WORKING_RE = re.compile(r"\scommit\b[^;&|]*\s(-a|--all|--only|-o|-[a-zA-Z]*a[a-zA-Z]*)\b")


def is_commit(command: str) -> bool:
    return bool(COMMIT_RE.search(command)) and "--dry-run" not in command


#: DEF-249 — the commit message as the command gives it: `-F <file>` / `--file <file>`, or each `-m <text>`.
_FILE_RE = re.compile(r"""\s(?:-F|--file)(?:\s+|=)(?:"([^"]+)"|'([^']+)'|(\S+))""")
_M_RE = re.compile(r"""\s-m\s+(?:"((?:[^"\\]|\\.)*)"|'([^']*)')""")


def commit_message(command: str) -> str | None:
    """DEF-249: the message a `git commit` command carries, or None (an editor opens: nothing to check here)."""
    m = _FILE_RE.search(command)
    if m:
        try:
            return Path(next(g for g in m.groups() if g)).read_text(encoding="utf-8")
        except OSError:
            return None
    parts = [next((g for g in mm.groups() if g is not None), "") for mm in _M_RE.finditer(command)]
    return "\n\n".join(parts) if parts else None


def message_problems(message: str) -> list[str]:
    """DEF-249 (founder ruling 2026-10-20, hook time c): the commit guard's message rules, run on the message before
    any test — the 8D of a fix (rule 6), `Design:` (rule 17), `Ruling:` (rule 20). Each refusal, in the guard's
    words. Rules 1, 8 and 23 retired (founder ruling 2026-10-27, item 6)."""
    import contextlib
    import importlib.util
    import io
    hooks = Path(__file__).resolve().parent
    spec = importlib.util.spec_from_file_location("guard_preflight", hooks / "commit-msg-refactor-guard.py")
    assert spec and spec.loader
    guard = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(guard)
    root = str(hooks.parents[1])
    lines = [ln for ln in message.splitlines() if not ln.startswith("#")]
    subject = (lines[0] if lines else "").strip()
    body = "\n".join(lines)
    try:
        staged = guard.staged_paths(root)
    except Exception:                               # noqa: BLE001 — without the index, the message rules alone
        staged = []
    checks = [lambda: guard.check_8d(subject, body),
              lambda: guard.check_design(root, body, staged),
              lambda: guard.check_founder_ownership(root, body, staged)]
    out = []
    for check in checks:
        err = io.StringIO()
        try:
            with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()):
                check()
        except SystemExit:
            out.append(err.getvalue().strip())
    return out


def decide(payload: dict, run) -> tuple[int, str]:
    """(exit code, message) for one PreToolUse payload. `run` is preflight.run."""
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        return 0, ""
    command = (payload.get("tool_input") or {}).get("command") or ""
    if not is_commit(command):
        return 0, ""
    message = commit_message(command)
    if message is not None:
        problems = message_problems(message)
        if problems:
            return 2, ("\n\n".join(problems) + "\n\nPRE-FLIGHT FAILED on the commit message (DEF-249) — nothing was "
                       "run. Fix the message; the commit-msg guard would refuse it after the whole suite.")
    lines: list[str] = []
    working = bool(WORKING_RE.search(command))
    code = run(echo=lines.append, **({"working": True} if working else {}))
    report = "\n".join(lines)
    if code == 0:
        return 0, report
    return 2, (report + "\n\nPRE-FLIGHT FAILED — the commit was not attempted. Fix what "
               "is named above. A failure passes only when HEAD's own record has it "
               "(docs/test-results.json at HEAD; the drift check on HEAD's tree).")


def main() -> int:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import preflight
        code, msg = decide(payload, preflight.run)
    except Exception as exc:                        # noqa: BLE001 — fail soft
        print(f"[preflight] the hook itself failed ({exc!r}); the commit proceeds "
              "and the commit hook still checks everything", file=sys.stderr)
        return 0
    if msg:
        print(msg, file=sys.stderr if code else sys.stdout)
    return code


if __name__ == "__main__":
    sys.exit(main())
