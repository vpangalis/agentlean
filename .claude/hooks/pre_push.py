#!/usr/bin/env python3
"""pre-push — a push requires a passing FULL-suite run on the exact source being pushed.

Founder ruling 4.3, 2026-09-29 (the pre-push check proposed after the third loop run). Since
founder item 9 a commit's hook runs only the FAST tests its change reaches; the full suite runs
once per package. So a commit can be on main without the full suite ever having passed on its
source — and the push is the moment it leaves the machine.

THE LEDGER. Every full-suite run (`staged_tree.run_suite`: the pre-commit hook's full run, rule
4's own run, or `python .claude/hooks/staged_tree.py --suite-at <rev>`) appends its verdict to
`.claude/logs/full-runs.jsonl`, keyed by the SOURCE it ran on (`source_id`).

THE SOURCE. A tree's source id hashes every tracked path except what cannot change a test's
outcome and what the pre-commit hook writes after its test run: Markdown (other than the
skills the coach reads) and the generated outputs in GENERATED. So a commit's source equals the
source its own hook's full run tested, and a documentation-only commit keeps its parent's.

    git push ...                                         # runs this hook (.githooks/pre-push)
    python .claude/hooks/staged_tree.py --suite-at HEAD   # the full suite on HEAD's source

Fail-CLOSED: a push with no passing full run on its source is refused, naming the command.
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
LEDGER = Path(os.environ.get("AGENTLEAN_LOGS") or ROOT / ".claude" / "logs") / "full-runs.jsonl"
ZERO = "0" * 40
#: What the pre-commit hook writes after its test run — never part of the tested source.
GENERATED = frozenset({
    "agent-improve/docs/control-board.html", "agent-improve/docs/test-results.json",
    "agent-improve/docs/features-ratchet.json", ".claude/config/mypy-ratchet.json",
})


def _git(*args: str, root: Path = ROOT) -> str:
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    return subprocess.run(["git", *args], cwd=root, capture_output=True, encoding="utf-8",
                          errors="replace", check=True, env=env).stdout


def counts(path: str) -> bool:
    """Is this tracked path part of the tested source?"""
    if path in GENERATED:
        return False
    return not path.endswith(".md") or path.startswith("agent-improve/skills/")


def source_id(rev: str, root: Path = ROOT) -> str:
    """The source of a commit or tree: its tracked paths that count, with their blob ids."""
    h = hashlib.sha256()
    for line in _git("ls-tree", "-r", "--full-tree", rev, root=root).splitlines():
        meta, _, path = line.partition("\t")
        if counts(path):
            h.update(f"{meta}\t{path}\n".encode())
    return h.hexdigest()[:16]


def record(tree: str, code: int, summary: str, root: Path = ROOT, ledger: Path | None = None) -> None:
    """Append one full run's verdict. Never raises: a lost line only means a re-run."""
    path = ledger or LEDGER
    try:
        row = {"at": dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds"),
               "source": source_id(tree, root), "tree": tree, "exit": int(code), "summary": summary[-300:]}
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
    except (OSError, ValueError, subprocess.CalledProcessError):
        pass


def passed_sources(ledger: Path | None = None) -> set[str]:
    """Sources whose LATEST full run passed (a later failure on the same source revokes it)."""
    path = ledger or LEDGER
    last: dict[str, int] = {}
    if path.is_file():
        for line in path.read_text(encoding="utf-8").splitlines():
            try:
                r = json.loads(line)
                last[r["source"]] = int(r["exit"])
            except (ValueError, KeyError, TypeError):
                continue
    return {s for s, code in last.items() if code == 0}


def refusals(updates: list[tuple[str, str, str, str]], source_of, passed: set[str]) -> list[str]:
    """For each pushed (local ref, local sha, remote ref, remote sha): why it may not go."""
    out = []
    for local_ref, local_sha, remote_ref, _remote_sha in updates:
        if local_sha == ZERO:
            continue                                   # a delete pushes no source
        src = source_of(local_sha)
        if src not in passed:
            out.append(f"{remote_ref} <- {local_sha[:10]} ({local_ref}): no passing full-suite run on its "
                       f"source {src}")
    return out


def main() -> int:
    updates = [tuple(line.split()) for line in sys.stdin.read().splitlines() if len(line.split()) == 4]
    bad = refusals(updates, source_id, passed_sources())  # type: ignore[arg-type]
    if not bad:
        if updates:
            print(f"  [pre-push] PASS — {len(updates)} ref(s), each on a source whose full suite passed", file=sys.stderr)
        return 0
    print("\n  PUSH REFUSED — founder ruling 4.3 (2026-09-29): a push requires a passing full-suite run "
          "on the exact source being pushed.", file=sys.stderr)
    for b in bad:
        print(f"  !! {b}", file=sys.stderr)
    print("\n  Run the full suite on that source, then push again:\n"
          "    python .claude/hooks/staged_tree.py --suite-at <sha>\n"
          "  (or commit with AGENT_IMPROVE_FULL_SUITE=1, which records the same run)\n", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
