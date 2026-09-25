#!/usr/bin/env python3
"""The section index — step 6.66 (founder ruling 2026-09-25).

CLAUDE.md §22 (b): never read ARCHITECTURE.md or the procedure whole — find the
section, read that region. This writes `agent-improve/docs/section-index.md`:
every heading of both documents with its line range, so a session reads
`offset`/`limit` straight from a table instead of grepping first.

GENERATED — the pre-commit hook rewrites and stages it on every commit that
touches either document; never hand-edit it. Headings inside fenced code are
not headings. A section's range runs to the line before the next heading of
the same or a higher level.

    python .claude/hooks/section_index.py          # write the index
    python .claude/hooks/section_index.py --check  # exit 1 if it is stale
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ("agent-improve/ARCHITECTURE.md", "agent-improve/docs/REFACTORING_PROCEDURE.md")
OUT = ROOT / "agent-improve" / "docs" / "section-index.md"
_HEADING = re.compile(r"^(#{1,4})\s+(.*\S)\s*$")
_FENCE = re.compile(r"^\s*(```|~~~)")


def sections(text: str) -> list[tuple[int, int, int, str]]:
    """(level, first line, last line, title) for every heading, 1-based lines."""
    lines = text.splitlines()
    heads: list[tuple[int, int, str]] = []
    fenced = False
    for i, line in enumerate(lines, 1):
        if _FENCE.match(line):
            fenced = not fenced
            continue
        m = None if fenced else _HEADING.match(line)
        if m:
            heads.append((len(m.group(1)), i, m.group(2)))
    out = []
    for k, (level, start, title) in enumerate(heads):
        end = len(lines)
        for nlevel, nstart, _ in heads[k + 1:]:
            if nlevel <= level:
                end = nstart - 1
                break
        out.append((level, start, end, title))
    return out


def render() -> str:
    parts = ["# Section index — GENERATED, never hand-edit",
             "",
             "Written by `.claude/hooks/section_index.py` on every commit that touches a",
             "document below (step 6.66). Find the section here, then read only its lines",
             "(CLAUDE.md §22 b). A range runs to the next heading of the same or higher level.",
             ""]
    for rel in DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        parts += [f"## `{rel}` — {len(text.splitlines())} lines", "",
                  "| Lines | Heading |", "|---|---|"]
        for level, start, end, title in sections(text):
            indent = " " * (level - 1)
            parts.append(f"| {start}–{end} | {indent}{title.replace('|', '/')} |")
        parts.append("")
    return "\n".join(parts)


def main(argv: list[str]) -> int:
    new = render()
    if "--check" in argv:
        old = OUT.read_text(encoding="utf-8") if OUT.is_file() else ""
        if old.replace("\r\n", "\n") != new:
            print("section-index.md is stale — run: python .claude/hooks/section_index.py")
            return 1
        return 0
    OUT.write_text(new, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
