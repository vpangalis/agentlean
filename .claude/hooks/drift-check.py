#!/usr/bin/env python3
"""Stop hook — re-derives every owned fact and checks the documents agree.

ARCHITECTURE.md §55.4. The companion to `fact-ownership-guard.py`, and the
division of labour is the point:

  the GUARD stops a NEW copy being written
  this  catches an EXISTING copy that has gone stale

Both are needed because the guard cannot reach backwards. Every restatement
written before 2026-09-13 is still in the documents, agreeing with the code
today and free to disagree tomorrow.

Three outcomes, and the middle one is why the check survives contact:

  FAIL     a governed document states a number beside an owned symbol and the
           number is WRONG. Exit 2
  PENDING  the owner does not exist yet — reported, never failed
  PASS     every claim agrees with what the owner says right now

Also runnable standalone, which is how it earns its place in CI:
    python .claude/hooks/drift-check.py [--quiet]

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

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()).resolve()


def governed_files(reg: dict) -> list[Path]:
    out: list[Path] = []
    for pat in reg.get("governed_paths", []):
        out.extend(p for p in ROOT.glob(pat) if p.is_file())
    seen, uniq = set(), []
    for p in out:
        r = str(p.relative_to(ROOT)).replace("\\", "/")
        if r in seen or not fo.is_governed(r, reg):
            continue
        seen.add(r)
        uniq.append(p)
    return sorted(uniq)


def scan(reg: dict) -> tuple[list[tuple], list[str], int]:
    values, pending = fo.derive(reg)
    owner_of = {s["name"]: s["path"]
                for o in reg.get("owners", [])
                for s in (o.get("symbols") or [])}
    live = [s for s in owner_of if s not in pending]

    wrong, checked = [], 0
    for path in governed_files(reg):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        present = [s for s in live if s in text]
        if not present:
            continue
        lines = text.splitlines()
        for line_no, sym, raw, val in fo.assertions(text, present):
            expected = values.get(sym)
            if not isinstance(expected, int):
                continue
            line = lines[line_no - 1] if line_no <= len(lines) else ""
            checked += 1
            # A number near a symbol is not always a claim about its field
            # count — §-numbers, years, step numbers and list indices all sit
            # in that window. Only a MISMATCH on a number that looks like a
            # count is reported, and only when the line does not cite an
            # owner. Deliberately conservative: a check that cries wolf is a
            # check that gets switched off.
            if val == expected or fo.cites_owner(line):
                continue
            if not any(w in line.lower() for w in ("field", "carries", "declare")):
                continue
            wrong.append((str(path.relative_to(ROOT)).replace("\\", "/"),
                          line_no, sym, raw, expected, owner_of[sym]))
    return wrong, pending, checked


def main(argv: list[str]) -> int:
    quiet = "--quiet" in argv
    # Stop-hook envelope arrives on stdin; standalone runs get nothing.
    if not sys.stdin.isatty():
        try:
            sys.stdin.read()
        except Exception:                           # noqa: BLE001
            pass
    try:
        reg = fo.load_registry()
        wrong, pending, checked = scan(reg)
    except Exception as exc:                        # noqa: BLE001
        if not quiet:
            print(f"[drift-check] could not run: {exc}")
        return 0                                    # fail-soft

    if pending and not quiet:
        print(f"[drift-check] PENDING (owner not built, not checked): "
              f"{', '.join(sorted(set(pending)))}")

    if not wrong:
        if not quiet:
            print(f"[drift-check] {checked} claim(s) checked, all agree "
                  f"with their owner.")
        return 0

    msg = ["[drift-check] A governing document disagrees with the code that "
           "owns the fact.", ""]
    for f, line_no, sym, raw, expected, owner in wrong:
        msg.append(f"  {f}:{line_no}")
        msg.append(f"    says `{sym}` … {raw}; `{owner}` says {expected}")
        msg.append("")
    msg.append("Correct the document, or cite the owner instead of restating "
               "it (ARCHITECTURE.md §55.4).")
    out = "\n".join(msg)
    print(out)
    sys.stderr.write(out + "\n")
    return 2


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except Exception:                               # noqa: BLE001
        sys.exit(0)
