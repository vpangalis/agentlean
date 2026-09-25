#!/usr/bin/env python3
"""PreToolUse hook — the pre-flight runs before every `git commit`. Step 6.66.

Claude Code hands this the tool call on stdin. A Bash or PowerShell command
that runs `git commit` (not `--dry-run`) triggers `preflight.run()`; a failure
blocks the call with exit 2, and stderr reaches Claude as the reason
(https://code.claude.com/docs/en/hooks — "exit code 2: blocking error").

FAIL-SOFT, the opposite of the commit-msg guard: the pre-flight is an
accelerator, the commit hook is the gate. If this hook itself breaks it lets
the call through and says so — it never wedges a commit.

A failure you have judged to be pre-existing (it fails identically at HEAD) is
passed on the record by a comment in the command:
    git commit -F msg.txt   # preflight: acknowledged — <reason, 12+ chars>
The commit hook still runs the full suite and every guard rule after it.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

COMMIT_RE = re.compile(r"(?:^|[;&|(\s])git(?:\s+-C\s+\S+|\s+-c\s+\S+)*\s+commit\b")
ACK_RE = re.compile(r"#\s*preflight:\s*acknowledged\s*[—-]\s*(?P<why>.{12,})")


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
    code = run(echo=lines.append)
    report = "\n".join(lines)
    if code == 0:
        return 0, report
    ack = ACK_RE.search(command)
    if ack:
        return 0, report + f"\n[preflight] failure ACKNOWLEDGED: {ack.group('why').strip()}"
    return 2, (report + "\n\nPRE-FLIGHT FAILED — the commit was not attempted. Fix the "
               "knock-on above, or, if it fails identically at HEAD, re-run the commit "
               "with `# preflight: acknowledged — <why>` on the command.")


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
