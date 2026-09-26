#!/usr/bin/env python3
"""Relative links in a Markdown file resolve — the docs-only commit's fast check. Step 6.67.

Founder addendum 2026-09-26, speed item 1: a commit touching only
documentation runs the fast checks (citations, size budget, links), never the
suite. This is the links check: every `[text](target)` in a STAGED `.md` file
whose target is a relative path must name a file that exists — resolved from
the linking file's directory, the `#anchor` stripped. Web links, mail links
and bare anchors are not checked. Only staged files are read, so a document
nobody touches never blocks a commit for an old link.

    python .claude/hooks/check_links.py [paths...]     # default: the staged .md files
"""
from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
_SKIP = ("http://", "https://", "mailto:", "#", "file:")


def staged_md(root: Path = ROOT) -> list[str]:
    out = subprocess.run(["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"], cwd=root,
                         capture_output=True, encoding="utf-8", errors="replace", timeout=30).stdout
    return [p.strip() for p in out.splitlines() if p.strip().endswith(".md")]


def broken(rel: str, root: Path = ROOT) -> list[str]:
    path = root / rel
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    text = re.sub(r"```.*?```", "", text, flags=re.S)          # links in code are not links
    bad = []
    for target in _LINK.findall(text):
        if target.startswith(_SKIP) or "{" in target:
            continue
        file_part = target.split("#", 1)[0]
        if not file_part:
            continue
        if not (path.parent / file_part).exists():
            bad.append(target)
    return bad


def main(argv: list[str]) -> int:
    files = argv or staged_md()
    problems = [(f, t) for f in files for t in broken(f)]
    for f, t in problems:
        print(f"  !! {f}: link to {t} does not resolve")
    print(f"links: {'PASS' if not problems else 'FAIL'} — {len(files)} file(s), {len(problems)} broken")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
