#!/usr/bin/env python3
"""PreToolUse hook — blocks writes containing deprecated LangChain/LangGraph
patterns before they land on disk.

Fires on Write/Edit/MultiEdit (matched in .claude/settings.json at commit
0.5.3). Reads the Claude Code hook envelope from stdin, checks the content
being written against .claude/config/deprecated_patterns.yaml, and:

  - exits 2 (blocking) if any non-excluded pattern matches — stderr is fed
    back to Claude so it can self-correct;
  - exits 0 (allow) otherwise, or on any internal/config error (fail-soft:
    a hook bug must never wedge the developer).

PreToolUse — not PostToolUse — is the correct mechanism: PostToolUse fires
after the file is already on disk and cannot block. (EDUCATIONAL §45 to be
corrected in Part 2 of this arc.)

Python 3.11+, standard library + pyyaml. Read-only except reading the config.
"""

from __future__ import annotations

import fnmatch
import json
import os
import re
import sys

# Force UTF-8 on stderr so §/— in pattern messages survive Windows code pages
# (stderr is fed back to Claude verbatim; mojibake would garble the guidance).
try:
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

try:
    import yaml
except ImportError:
    # Fail-soft: do not block writes just because pyyaml is absent. The
    # developer sees this notice and installs it; the hook activates after.
    sys.stderr.write("pyyaml required — pip install pyyaml\n")
    sys.exit(0)

WRITE_TOOLS = {"Write", "Edit", "MultiEdit"}
CONFIG_REL_PATH = os.path.join(".claude", "config", "deprecated_patterns.yaml")


def _log(msg: str) -> None:
    try:
        sys.stderr.write(f"[drift-check] {msg}\n")
    except Exception:
        pass


def get_project_dir() -> str:
    """Monorepo root. Honours $CLAUDE_PROJECT_DIR, else current working dir."""
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()


def extract_target(tool_name: str, tool_input: dict) -> tuple[str, str]:
    """Return (file_path, content) for the write-like tool, per its schema."""
    file_path = tool_input.get("file_path", "") or ""
    if tool_name == "Write":
        content = tool_input.get("content", "") or ""
    elif tool_name == "Edit":
        content = tool_input.get("new_string", "") or ""
    else:  # MultiEdit — concatenate every edit's new_string
        edits = tool_input.get("edits") or []
        content = "\n".join((e.get("new_string", "") or "") for e in edits)
    return file_path, content


def normalize_path(file_path: str, project_dir: str) -> str:
    """Project-relative, forward-slashed path for glob matching."""
    p = file_path.replace("\\", "/")
    pd = project_dir.replace("\\", "/").rstrip("/")
    if pd and p.startswith(pd + "/"):
        p = p[len(pd) + 1:]
    return p.lstrip("./")


def is_excluded(rel_path: str, exclusions: list) -> bool:
    """gitignore/fnmatch-style glob match (case-sensitive, * spans '/')."""
    for glob in exclusions or []:
        if fnmatch.fnmatchcase(rel_path, glob):
            return True
    return False


def is_registry_itself(file_path: str, project_dir: str) -> bool:
    """True when the write targets the pattern registry file itself.

    Bootstrapping exemption, and the narrowest possible one: an exact path
    match against CONFIG_REL_PATH, never a glob and never a directory.

    Why it is needed. Several registry entries necessarily quote the literal
    they prohibit — a pattern's `message:` field has to name the construct it
    is telling the author to stop writing. Those quoted literals are matched
    by the very regexes they document, so *every* write to the registry
    matches, including a byte-for-byte rewrite of its current contents. The
    effect was that the governance file could not be edited through Write or
    Edit at all, and the only ways to amend it were to hand-edit outside the
    tooling or to route around the hook.

    This restores normal editability for that one file. It does not loosen
    the guard anywhere else: every other path, including the rest of
    .claude/, is still checked exactly as before. Registry changes remain
    governed by the audit-trailed-commit rule stated in the registry header.
    """
    try:
        target = os.path.realpath(file_path)
        registry = os.path.realpath(os.path.join(project_dir, CONFIG_REL_PATH))
        return os.path.normcase(target) == os.path.normcase(registry)
    except Exception:  # noqa: BLE001 - path resolution must never block a write
        return False


def load_patterns(project_dir: str) -> list[dict]:
    """Load the pattern registry. Raises on unreadable/invalid config."""
    config_path = os.path.join(project_dir, CONFIG_REL_PATH)
    with open(config_path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    return data.get("patterns") or []


def find_violations(rel_path: str, content: str, patterns: list[dict]) -> list[dict]:
    """Return a list of {id, message, line} for each matching, non-excluded pattern."""
    violations = []
    for pat in patterns:
        pid = pat.get("id", "<unnamed>")
        raw = pat.get("regex")
        if not raw:
            continue
        if is_excluded(rel_path, pat.get("path_exclusions")):
            continue
        try:
            rx = re.compile(raw)
        except re.error as exc:
            _log(f"skipping {pid}: invalid regex ({exc})")
            continue
        m = rx.search(content)
        if m:
            line_no = content.count("\n", 0, m.start()) + 1
            violations.append({
                "id": pid,
                "message": pat.get("message", ""),
                "line": line_no,
            })
    return violations


def main() -> int:
    raw = sys.stdin.read()
    if not raw.strip():
        return 0  # nothing to inspect
    try:
        envelope = json.loads(raw)
    except json.JSONDecodeError as exc:
        _log(f"unparseable stdin envelope: {exc}")
        return 0  # fail-soft — never block on malformed input

    tool_name = envelope.get("tool_name", "")
    if tool_name not in WRITE_TOOLS:
        return 0  # only guard write-like tools; silent no-op otherwise

    tool_input = envelope.get("tool_input") or {}
    file_path, content = extract_target(tool_name, tool_input)
    if not content:
        return 0  # nothing being written

    project_dir = get_project_dir()

    if is_registry_itself(file_path, project_dir):
        _log("registry self-edit — check skipped (bootstrapping exemption)")
        return 0

    try:
        patterns = load_patterns(project_dir)
    except Exception as exc:  # noqa: BLE001 - fail-soft on any config error
        _log(f"could not load pattern registry: {exc}")
        return 0

    rel_path = normalize_path(file_path, project_dir)
    violations = find_violations(rel_path, content, patterns)

    if not violations:
        return 0

    sys.stderr.write(
        f"Drift check blocked this write to {rel_path} — "
        f"deprecated pattern(s) detected:\n"
    )
    for v in violations:
        sys.stderr.write(f"  [{v['id']}] line {v['line']}: {v['message']}\n")
    return 2  # block; stderr is surfaced to Claude for self-correction


if __name__ == "__main__":
    try:
        sys.exit(main())
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - fail-open; a hook bug must not block
        _log(f"fatal: {exc}")
        sys.exit(0)
