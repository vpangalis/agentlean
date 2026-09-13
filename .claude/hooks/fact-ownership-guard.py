#!/usr/bin/env python3
"""PreToolUse hook — denies a governing document that RESTATES an owned fact.

ARCHITECTURE.md §55.4. Two ratified owners: `requirements.txt` for dependency
versions, the schema modules for state and output field names, counts and
types. **Cite the owner; do not copy its value.**

**This is the countermeasure G-56 names.** `deprecated_patterns.yaml` excludes
`agent-improve/**/*.md` — correctly, because architecture markdown must be able
to show a superseded form beside its replacement — which leaves the governing
documents guarded by nothing. This hook matches OWNERSHIP rather than patterns,
so it needs no exclusion and can watch exactly the files that one cannot.

Three outcomes, and the middle one is why the check survives contact:

  DENY     a governed document states a number beside an owned symbol, with
           no owner cited on that line
  PENDING  the owner does not exist yet — `phases/*/schema.py` for a phase not
           built. No owner, nothing to restate, so ALLOW and say so
  ALLOW    everything else, including the same sentence with the owner named

Fail-soft throughout: a hook bug must never wedge a write.
Python 3.11+, stdlib + pyyaml.
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

try:
    import _fact_owners as fo
except Exception:                                   # noqa: BLE001
    sys.exit(0)

WRITE_TOOLS = {"Write", "Edit", "MultiEdit"}


def extract(tool: str, ti: dict) -> tuple[str, str]:
    path = ti.get("file_path", "") or ""
    if tool == "Write":
        return path, ti.get("content", "") or ""
    if tool == "Edit":
        return path, ti.get("new_string", "") or ""
    return path, "\n".join((e.get("new_string", "") or "")
                           for e in (ti.get("edits") or []))


def rel(path: str, root: Path) -> str:
    try:
        return str(Path(path).resolve().relative_to(root)).replace("\\", "/")
    except Exception:                               # noqa: BLE001
        return path.replace("\\", "/").lstrip("./")


def deny(reason: str) -> int:
    print(json.dumps({"hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "permissionDecision": "deny",
        "permissionDecisionReason": reason}}))
    sys.stderr.write(reason + "\n")
    return 2


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0
    try:
        env = json.loads(raw)
    except json.JSONDecodeError:
        return 0
    if env.get("tool_name") not in WRITE_TOOLS:
        return 0

    path, content = extract(env["tool_name"], env.get("tool_input") or {})
    if not content:
        return 0

    root = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()
    target = rel(path, root)

    try:
        reg = fo.load_registry()
    except Exception:                               # noqa: BLE001
        return 0
    if not fo.is_governed(target, reg):
        return 0                                    # code, archives, anything else
    if Path(target).name == "fact_owners.yaml":
        return 0                                    # bootstrapping exemption

    try:
        values, pending = fo.derive(reg)
    except Exception:                               # noqa: BLE001
        return 0

    owner_of = {}
    for owner in reg.get("owners", []):
        for s in owner.get("symbols", []) or []:
            owner_of[s["name"]] = s["path"]
    symbols = [s for s in owner_of if s in content]
    if not symbols:
        return 0

    hits, held = [], []
    lines = content.splitlines()
    for line_no, sym, raw_num, val in fo.assertions(content, symbols):
        line = lines[line_no - 1] if line_no <= len(lines) else ""
        if fo.cites_owner(line):
            continue                                # a citation, not a copy
        if sym in pending:
            held.append(sym)                        # no owner yet — nothing to copy
            continue
        hits.append((line_no, sym, raw_num, owner_of[sym], values.get(sym)))

    if held:
        sys.stderr.write(
            "[fact-ownership] PENDING, allowed: "
            + ", ".join(sorted(set(held)))
            + " — the owner does not exist yet, so there is nothing to restate.\n")

    if not hits:
        return 0

    out = [f"Blocked — {target} restates a fact it does not own "
           f"(ARCHITECTURE.md §55.4).", ""]
    for line_no, sym, raw_num, owner_path, live in hits:
        out.append(f"  line {line_no}: `{sym}` … {raw_num}")
        out.append(f"    this fact is owned by `{owner_path}` — cite it, "
                   f"do not restate it.")
        if live is not None:
            out.append(f"    (it currently says {live}; a second copy is a "
                       f"copy that can drift, whether or not it agrees today)")
        out.append("")
    out.append("Name the owner on the same line and this passes — the rule is "
               "CITE, NOT RESTATE, not silence.")
    return deny("\n".join(out))


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception:                               # noqa: BLE001 — fail-open
        sys.exit(0)
