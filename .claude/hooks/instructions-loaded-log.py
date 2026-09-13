#!/usr/bin/env python3
"""InstructionsLoaded hook — records which rule files actually load, and why.

**This exists because a `paths:` glob that matches nothing fails SILENTLY.**
The rule simply never loads; nothing errors, nothing warns, and the only
symptom is guidance that was supposed to be there and was not. Step 6 shipped
thirteen rule files whose globs were written `backend/**` when `.claude/` sits
above `agent-improve/` — every one of them matched zero files, and the only
reason it was caught was a matcher run by hand. This hook is that check, made
permanent and automatic.

Envelope fields are taken from the installed CLI's own schema (v2.1.131),
not from documentation:

    hook_event_name  "InstructionsLoaded"
    file_path        the instruction file being loaded
    memory_type      User | Project | Local | Managed
    load_reason      session_start | nested_traversal | path_glob_match
                     | include | compact
    globs            optional — the globs that matched
    trigger_file_path optional — the file whose opening triggered the load
    parent_file_path  optional

`load_reason == "path_glob_match"` is the one that proves a `paths:` frontmatter
fired, and `globs` + `trigger_file_path` say which glob and which file. That is
strictly more than file_path and load_reason alone.

Observe-only: writes a line and exits 0, always. A logger that can block is a
logger that will one day wedge a session.

Python 3.11+, standard library only.
"""

from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

LOG_REL = Path(".claude") / "logs" / "instructions-loaded.log"
MAX_BYTES = 512 * 1024


def project_dir() -> Path:
    return Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        env = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    if env.get("hook_event_name") != "InstructionsLoaded":
        return 0

    path = env.get("file_path") or "?"
    reason = env.get("load_reason") or "?"
    rec = {
        "at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "file": path,
        "reason": reason,
        "memory_type": env.get("memory_type"),
    }
    # Only meaningful for a glob match; omitted rather than logged as null so a
    # reader grepping the log is never asked to ignore empty columns.
    if env.get("globs"):
        rec["globs"] = env["globs"]
    if env.get("trigger_file_path"):
        rec["triggered_by"] = env["trigger_file_path"]

    log = project_dir() / LOG_REL
    try:
        log.parent.mkdir(parents=True, exist_ok=True)
        if log.exists() and log.stat().st_size > MAX_BYTES:
            log.replace(log.with_suffix(".log.1"))
        with log.open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")
    except OSError:
        pass                      # observe-only: never fail a load
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:             # noqa: BLE001 — a logger must never block
        sys.exit(0)
