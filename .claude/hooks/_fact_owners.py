#!/usr/bin/env python3
"""Shared derivation for the two ownership hooks — ARCHITECTURE.md §55.4.

`fact-ownership-guard.py` (PreToolUse, denies a new restatement) and
`drift-check.py` (Stop, catches an existing restatement that has gone stale)
must agree about what each owner says. They agree by importing this, not by
each implementing it.

**Every value is derived at check time. Nothing is cached and nothing is
stored in the registry** — a stored value would be one more copy of the fact
the registry governs.

PENDING is a first-class result, not an error: an owner that does not exist
yet has no value to cite, so a document cannot be restating it.
"""

from __future__ import annotations

import fnmatch
import importlib
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd())
REGISTRY = ROOT / ".claude" / "config" / "fact_owners.yaml"
PROJECT = "agent-improve"

WORDS = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
    "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15,
    "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19,
    "twenty": 20, "twenty-one": 21, "twenty-two": 22, "twenty-three": 23,
}


def load_registry() -> dict:
    import yaml
    return yaml.safe_load(REGISTRY.read_text(encoding="utf-8")) or {}


def _venv_python() -> str:
    exe = ROOT / PROJECT / ".venv" / "Scripts" / "python.exe"
    if exe.exists():
        return str(exe)
    exe = ROOT / PROJECT / ".venv" / "bin" / "python"
    return str(exe) if exe.exists() else sys.executable


def derive(reg: dict) -> tuple[dict[str, object], list[str]]:
    """(symbol -> live value, [symbols whose owner does not exist yet]).

    Field counts are read in the project's pinned venv, because the schema
    modules import langchain/langgraph and this hook may run under another
    interpreter. WATCH 2's rule: which interpreter answers is the question.
    """
    values: dict[str, object] = {}
    pending: list[str] = []

    for owner in reg.get("owners", []):
        kind = owner.get("derive")

        if kind == "requirements":
            path = ROOT / owner["owner_path"]
            if not path.exists():
                pending.append(owner["id"])
                continue
            for line in path.read_text(encoding="utf-8").splitlines():
                m = re.match(r"^([A-Za-z0-9_.\-]+)\s*==\s*([0-9][^\s#]*)", line)
                if m:
                    values[m.group(1).lower()] = m.group(2)

        elif kind == "python_symbols":
            wanted = [s for s in owner.get("symbols", [])
                      if (ROOT / s["path"]).exists()]
            pending += [s["name"] for s in owner.get("symbols", [])
                        if not (ROOT / s["path"]).exists()]
            if not wanted:
                continue
            probe = (
                "import json,typing,importlib\n"
                f"S={[(s['module'], s['name']) for s in wanted]!r}\n"
                "out={}\n"
                "for mod,name in S:\n"
                "    try:\n"
                "        c=getattr(importlib.import_module(mod),name)\n"
                "    except Exception:\n"
                "        continue\n"
                "    f=getattr(c,'model_fields',None)\n"
                "    out[name]=len(f) if f is not None "
                "else len(typing.get_type_hints(c))\n"
                "print(json.dumps(out))\n"
            )
            try:
                r = subprocess.run([_venv_python(), "-c", probe],
                                   cwd=str(ROOT / PROJECT), capture_output=True,
                                   text=True, timeout=90)
                import json as _j
                for k, v in _j.loads(r.stdout.strip() or "{}").items():
                    values[k] = v
            except Exception:
                pending += [s["name"] for s in wanted]

    return values, pending


def is_governed(rel_path: str, reg: dict) -> bool:
    rel = rel_path.replace("\\", "/")
    for pat in reg.get("governed_exclusions", []):
        if fnmatch.fnmatch(rel, pat) or rel.startswith(pat.rstrip("*")):
            return False
    return any(fnmatch.fnmatch(rel, p) or rel == p
               for p in reg.get("governed_paths", []))


def cites_owner(line: str) -> bool:
    """Does this line name an owner file? Then it is a citation, not a copy."""
    return bool(re.search(
        r"requirements\.txt|core/state\.py|core/substate\.py|"
        r"phases/[a-z*]+/schema\.py|schema module", line))


#: A dated record is true when written, and is never a live restatement.
#: Same principle that keeps `docs/_archive/**` out of scope: §0's change
#: records, ARCHITECTURE.md's §56 changelog entries, and the version-history
#: table all state what was true on a date.
DATE_ANY = re.compile(r"20\d\d-\d\d-\d\d")

DATED = re.compile(
    r"^\s*(>\s*)?(\*\*)?v\d+\.\d+\s*\(\d{4}-\d{2}-\d{2}\)"      # **v1.26 (2026-09-11)**
    r"|^\s*\|\s*\w{3,9}\s+20\d\d\s*\|"                          # | Aug 2026 | 2.2.10 |
    r"|^\s*(>\s*)?\*\*[A-Z][a-z]+ 20\d\d\b"                      # **August 2026 —
    r"|^\s*\|[^|]*\|\s*20\d\d-\d\d-\d\d\s*\|",                   # | **4.0** | 2026-08-26 |
    re.I)


#: `four of its eight fields` / `BUILT AT 4 OF S-C05's 8 FIELDS` — a
#: SPEC-vs-BUILT pair. It carries two numbers deliberately and G-50 owns the
#: gap between them; neither number is a copy of an owned value. Also catches
#: `N of M` with any short phrase between, which is how these are written.
SPEC_VS_BUILT = re.compile(
    r"\b(\d{1,3}|" + "|".join(WORDS) + r")\s+of\s+\S{0,14}\s*"
    r"(\d{1,3}|" + "|".join(WORDS) + r")[\s\u2011-]*field",
    re.I)

def assertions(text: str, symbols: list[str]) -> list[tuple[int, str, str, int]]:
    """(line_no, symbol, raw, value) for each COUNT CLAIM about an owned symbol.

    **A number near a symbol is not a claim about it.** The first cut matched
    any number within 80 characters and produced 200+ false positives on its
    first run — §58.2 beside `PhaseState`, step numbers, years. The second
    cut bound every count on a line to every symbol on it, which is a cross
    product: one changelog sentence naming six schemas and six numbers
    reported thirty-six claims. **A check that cries wolf gets switched off**,
    which is the failure this registry exists to prevent, so:

      · a claim has a SHAPE — a number bound to a count noun: `22 fields`,
        `22-field`, `seven fields`;
      · it belongs to the NEAREST symbol on the line, not to all of them;
      · it must sit within 60 characters of that symbol; and
      · a DATED record is skipped entirely.
    """
    out = []
    num = r"(\d{1,3}|" + "|".join(WORDS) + r")"
    claim = re.compile(rf"\b{num}[\s\u2011-]+field", re.I)
    for i, line in enumerate(text.splitlines(), 1):
        if DATED.search(line):
            continue
        spots = [(m.start(), s) for s in symbols for m in re.finditer(re.escape(s), line)]
        if not spots:
            continue
        # `§6 field table` is a cross-reference, not a count.
        # `four of its eight fields` is a SPEC-vs-BUILT pair — it carries two
        # numbers on purpose and G-50 owns the gap between them. Both read as
        # claims to a regex and neither is a copy of an owned value.
        if SPEC_VS_BUILT.search(line):
            continue
        for m in claim.finditer(line):
            if m.start() and line[m.start() - 1] in "§#":
                continue
            raw = m.group(1)
            val = WORDS.get(raw.lower()) if not raw.isdigit() else int(raw)
            if val is None:
                continue
            pos, sym = min(spots, key=lambda sp: abs(sp[0] - m.start()))
            if abs(pos - m.start()) > 60:
                continue
            out.append((i, sym, raw, val))
    return out


def derive_singletons(reg: dict) -> tuple[dict[str, int], list[str]]:
    """Facts that are ONE number for the whole project, not one per symbol.

    The middleware stack has a length; the registry has a pattern count. Each
    is derived from its owner, never stored.
    """
    out: dict[str, int] = {}
    pending: list[str] = []
    for owner in reg.get("owners", []):
        kind = owner.get("derive")

        if kind == "middleware_list":
            src = ROOT / owner["owner_path"]
            if not src.exists():
                pending.append(owner["id"])
                continue
            import ast
            tree = ast.parse(src.read_text(encoding="utf-8"))
            found = None
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    f = node.func
                    name = getattr(f, "id", None) or getattr(f, "attr", None)
                    if name == "create_agent":
                        for kw in node.keywords:
                            if kw.arg == "middleware" and isinstance(kw.value, ast.List):
                                found = len(kw.value.elts)
            if found is None:
                pending.append(owner["id"])
            else:
                out[owner["id"]] = found

        elif kind == "pattern_registry":
            src = ROOT / owner["owner_path"]
            if not src.exists():
                pending.append(owner["id"])
                continue
            import yaml
            data = yaml.safe_load(src.read_text(encoding="utf-8")) or {}
            out[owner["id"]] = len(data.get("patterns") or [])

        elif kind == "skills_dirs":
            base = ROOT / owner["owner_path"]
            scripts = sorted(base.glob("dmaic-*-phase/coaching_script.md")) \
                if base.is_dir() else []
            if not scripts:
                pending.append(owner["id"])
            else:
                out[owner["id"]] = len(scripts)
    return out, pending


def singleton_claims(text: str, noun: str) -> list[tuple[int, str, int]]:
    """(line_no, raw, value) for `N <noun>` in live prose.

    Same discipline as `assertions`: dated records are skipped, and a number
    written as `§8` is a reference rather than a count.
    """
    out = []
    num = r"(\d{1,3}|" + "|".join(WORDS) + r")"
    rx = re.compile(rf"\b{num}[\s\u2011-]+{noun}s?\b", re.I)
    for i, line in enumerate(text.splitlines(), 1):
        if DATED.search(line) or SPEC_VS_BUILT.search(line):
            continue
        for m in rx.finditer(line):
            if m.start() and line[m.start() - 1] in "\u00a7#":
                continue
            raw = m.group(1)
            val = WORDS.get(raw.lower()) if not raw.isdigit() else int(raw)
            if val is not None:
                out.append((i, raw, val))
    return out


def coaching_leaks(text: str, reg: dict) -> list[tuple[int, str]]:
    """A governed document carrying a run of a phase's coaching script.

    Step 8 moved those scripts OUT of ARCHITECTURE.md precisely so the phase
    directory owns them. This is what stops them coming back: the opening line
    of each script is distinctive, and finding it in a governed document means
    the content was copied rather than cited.
    """
    base = ROOT / "agent-improve" / "skills"
    hits = []
    for script in sorted(base.glob("dmaic-*-phase/coaching_script.md")):
        try:
            first = next((ln for ln in script.read_text(encoding="utf-8")
                          .splitlines() if len(ln.strip()) > 60), None)
        except OSError:
            continue
        if not first:
            continue
        probe = first.strip()[:80]
        for i, line in enumerate(text.splitlines(), 1):
            if probe in line:
                hits.append((i, script.parent.name))
                break
    return hits


def version_claims(text: str, packages: list[str],
                   current: dict[str, object] | None = None
                   ) -> list[tuple[int, str, str]]:
    """(line_no, package, version) for each PIN restated in prose.

    **A floor is not a pin, and the difference is the whole rule.** §55.4 puts
    the floor in the documents deliberately — `langgraph >= 1.2.6` is a rule and
    belongs where rules live — and the pin in `requirements.txt`, which owns it.
    So `>= 1.2.6` is allowed and `1.2.11` beside the same package name is not.

    Same discipline the prose-count check was deleted for: measure before
    enforcing. A version is distinctive where a count is not — `1.2.11` cannot
    be confused with ordinary English — but a §-number, a document version and
    a dated record all look like one, so each is excluded explicitly.
    """
    out = []
    ver = re.compile(r"(?<![\w.§#])(\d+\.\d+(?:\.\d+)?)\b")
    floor = re.compile(r"(>=|≥|>|at least|floor|minimum)\s*$", re.I)
    rows = text.splitlines()
    for i, line in enumerate(rows, 1):
        # A dated line is a record. `Introspected against langgraph 1.2.11 on
        # 2026-09-12` is EVIDENCE — the G-54 discipline working — not a copy.
        # The date often sits one line up, because a record is a sentence and
        # a sentence wraps: `As of 2026-08-21 that resolved to` / `langgraph
        # 1.2.11, langchain 1.3.16`. Both lines belong to the same record.
        near = line + (chr(10) + rows[i - 2] if i >= 2 else "")
        if DATED.search(line) or cites_owner(line) or DATE_ANY.search(near):
            continue
        spots = [(m.start(), p) for p in packages
                 for m in re.finditer(rf"\b{re.escape(p)}\b", line, re.I)]
        if not spots:
            continue
        for m in ver.finditer(line):
            before = line[max(0, m.start() - 14):m.start()]
            if floor.search(before):
                continue                       # a floor: documents may state it
            if before.rstrip().endswith(("v", "V")):
                continue                       # a document version
            # ADJACENCY, not proximity. `langgraph 1.2.11` is a pin restated;
            # "langgraph ... step 2.3" is a step number that happens to sit on
            # the same line. A 40-character window reported 82 claims across
            # four documents, nearly all of them step numbers — the same
            # cry-wolf failure the prose-count check was deleted for. A pin
            # written as a pin touches its package name.
            best = None
            for pos, pkg in spots:
                gap = (m.start() - (pos + len(pkg))) if pos < m.start()                       else (pos - m.end())
                if 0 <= gap <= 3 and (best is None or gap < best[0]):
                    best = (gap, pkg)
            if best is None:
                continue
            # **Only the CURRENT pin is a restatement.** `langgraph 1.1.10 ->
            # 1.2.11` records a migration and states a version that is no
            # longer the pin; nothing can drift out of a fact about the past.
            # What creates a second copy is writing today's value.
            if current is not None:
                live = current.get(best[1].lower())
                if not isinstance(live, str) or live != m.group(1):
                    continue
            out.append((i, best[1], m.group(1)))
    return out
