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


def decide(payload: dict, run) -> tuple[int, str]:
    """(exit code, message) for one PreToolUse payload. `run` is preflight.run."""
    if payload.get("tool_name") not in ("Bash", "PowerShell"):
        return 0, ""
    command = (payload.get("tool_input") or {}).get("command") or ""
    if not is_commit(command):
        return 0, ""
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
