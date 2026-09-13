#!/usr/bin/env python3
"""Do the `paths:` globs in .claude/rules/ actually match anything?

**The failure this exists for is silent.** A `paths:` glob that matches no file
does not error — the rule simply never loads, and the only symptom is guidance
that should have been there. Step 6 shipped thirteen rule files whose globs read
`backend/**` while `.claude/` sits above `agent-improve/`; every one matched zero
files and nothing said so.

Two independent questions, deliberately kept apart:

  STATIC   does each glob match a file that exists in the tree right now?
           Answerable offline, in CI, on every commit.
  OBSERVED has the CLI ever actually loaded this rule file? Read from
           `.claude/logs/instructions-loaded.log`, written by the
           InstructionsLoaded hook.

Static failure is a defect. Observed-absence alone is weaker evidence — nobody
may have opened a matching file yet — so it is reported separately and never
conflated with the first.

Exit 1 if any glob matches nothing. Python 3.11+, standard library only.
"""

from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
RULES = ROOT / ".claude" / "rules"
LOG = ROOT / ".claude" / "logs" / "instructions-loaded.log"


def globs_of(rule: Path) -> list[str]:
    text = rule.read_text(encoding="utf-8")
    if not text.startswith("---"):
        return []
    fm = text.split("---", 2)[1]
    return re.findall(r'^\s*-\s*"(.+?)"\s*$', fm, re.M)


def matches(glob: str) -> list[Path]:
    """Files in the tree matching one `paths:` glob, repo-root relative."""
    if glob.endswith("/**"):
        base = ROOT / glob[:-3]
        return [p for p in base.rglob("*") if p.is_file()] if base.is_dir() else []
    return [p for p in ROOT.glob(glob) if p.is_file()]


def observed() -> set[str]:
    if not LOG.exists():
        return set()
    seen = set()
    for line in LOG.read_text(encoding="utf-8").splitlines():
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        if rec.get("reason") == "path_glob_match" and rec.get("file"):
            seen.add(Path(rec["file"]).name)
    return seen


def main() -> int:
    if not RULES.is_dir():
        print("no .claude/rules/ — nothing to verify")
        return 0
    seen, dead, pending = observed(), [], []
    files = sorted(RULES.glob("*.md"))
    print(f"{'rule file':<20}{'globs':>6}{'matched':>9}   status")
    print("-" * 62)
    for rule in files:
        gs = globs_of(rule)
        total = sum(len(matches(g)) for g in gs)
        bad, soon = [], []
        for g in gs:
            if matches(g):
                continue
            # A LITERAL path that does not exist is a file a scheduled step
            # will create — §2 designates `CircuitBreaker` into
            # `core/reliability.py` before step 8.3 builds it. A WILDCARD that
            # matches nothing, or any glob not rooted at the repo, is the
            # silent failure this check exists for.
            literal = not any(c in g for c in "*?[")
            if literal and g.startswith("agent-improve/"):
                soon.append(g)
            else:
                bad.append(g)
        if bad:
            dead.append((rule.name, bad))
            status = f"DEAD GLOB x{len(bad)}"
        else:
            status = ("ok - observed loading" if rule.name in seen
                      else "ok - not yet observed")
            if soon:
                pending.append((rule.name, soon))
                status += f" (+{len(soon)} pending)"
        print(f"{rule.name:<20}{len(gs):>6}{total:>9}   {status}")

    if pending:
        print("\nPENDING — a designated file no step has built yet. Not a "
              "defect; the glob starts matching when the file lands:")
        for name, gs in pending:
            for g in gs:
                print(f"  {name:<20} {g}")

    if dead:
        print("\nGLOBS MATCHING NOTHING — these rules can never load:")
        for name, gs in dead:
            for g in gs:
                print(f"  {name:<20} {g}")
        print("\nPaths are REPO-ROOT relative: `.claude/` sits above "
              "`agent-improve/`, so a glob must start `agent-improve/`.")
        return 1

    if not seen:
        print("\nNo path_glob_match events logged yet — every glob matches a "
              "real file, but no session has opened one. Static check passed; "
              "observation pending.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
