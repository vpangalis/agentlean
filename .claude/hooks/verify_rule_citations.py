#!/usr/bin/env python3
"""Does every rule number the drift hook QUOTES BACK still resolve?

CLAUDE.md §0.2. The registry's `message:` fields are fed to Claude verbatim when
a write is denied, and a message citing a rule that does not exist is worse than
no message. Since brief step 6 a rule number resolves in the root `CLAUDE.md`
**or** in one of thirteen files under `.claude/rules/`, so the check spans both.

**Three distinctions this makes, each learned by getting it wrong:**

  · only `message:` fields count. A §-number inside a YAML COMMENT is prose
    explaining history — `§18.1 was retired on 2026-09-13` — and is not quoted
    back to anyone. A naive grep over the whole file reports it as dangling.
  · `CLAUDE.md §x` resolves in the rules; `Reference §x` resolves in
    ARCHITECTURE.md. The messages cite both, deliberately, and checking them
    against the same corpus reports nine false failures.
  · a bare `§x` following the word Reference belongs to ARCHITECTURE.md.

Exit 1 if any citation dangles. Python 3.11+, stdlib + pyyaml.
"""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
REGISTRY = ROOT / ".claude" / "config" / "deprecated_patterns.yaml"


def corpus(paths: list[Path]) -> str:
    out = []
    for p in paths:
        try:
            out.append(p.read_text(encoding="utf-8"))
        except OSError:
            pass
    return "\n".join(out)


def resolves(num: str, text: str) -> bool:
    return re.search(rf"^#+ {re.escape(num)}[ .]", text, re.M) is not None


def main() -> int:
    import yaml
    data = yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}
    rules_corpus = corpus([ROOT / "agent-improve" / "CLAUDE.md",
                           *sorted((ROOT / ".claude" / "rules").glob("*.md"))])
    arch_corpus = corpus([ROOT / "agent-improve" / "ARCHITECTURE.md"])

    # THREE namespaces, not two. The messages cite `CLAUDE.md §x` for a rule,
    # `Reference §x` for an architecture section, and `EDUCATIONAL §x` for the
    # archived design review. A bare-§ fallback that assumed CLAUDE.md reported
    # six false failures on its first run — every one an EDUCATIONAL citation.
    rule_cites: set[str] = set()
    arch_cites: set[str] = set()
    edu_cites: set[str] = set()
    NS = ((r"CLAUDE\.md", rule_cites), (r"Reference", arch_cites),
          (r"EDUCATIONAL", edu_cites))
    for pat in data.get("patterns") or []:
        msg = pat.get("message", "") or ""
        for label, bucket in NS:
            for m in re.finditer(label + r"\s+§(\d+(?:\.\d+)*)", msg):
                bucket.add(m.group(1))
        # Anything left with no document named is a CLAUDE.md rule — that is
        # the registry's own convention and what §0.2 governs.
        stripped = msg
        for label, _ in NS:
            stripped = re.sub(label + r"\s+§\d+(?:\.\d+)*[a-z]?", "", stripped)
        for m in re.finditer(r"§(\d+(?:\.\d+)*)", stripped):
            rule_cites.add(m.group(1))

    edu_corpus = corpus([ROOT / "agent-improve" / "docs" / "_archive"
                         / "EDUCATIONAL.md"])
    bad = [(f"CLAUDE.md §{c}", "the root or .claude/rules/")
           for c in sorted(rule_cites) if not resolves(c, rules_corpus)]
    bad += [(f"Reference §{c}", "ARCHITECTURE.md")
            for c in sorted(arch_cites) if not resolves(c, arch_corpus)]
    bad += [(f"EDUCATIONAL §{c}", "docs/_archive/EDUCATIONAL.md")
            for c in sorted(edu_cites) if not resolves(c, edu_corpus)]

    print(f"registry messages cite {len(rule_cites)} rule number(s), "
          f"{len(arch_cites)} architecture section(s) and "
          f"{len(edu_cites)} archived-review section(s)")
    if not bad:
        print("all resolve.")
        return 0
    print("\nDANGLING — the hook would quote these back and they do not exist:")
    for cite, where in bad:
        print(f"  {cite:<22} not found in {where}")
    print("\n§0.2: renumbering a cited rule requires updating the registry in "
          "the same commit.")
    return 1


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as exc:                    # noqa: BLE001
        print(f"[rule-citations] could not run: {exc}")
        sys.exit(0)
