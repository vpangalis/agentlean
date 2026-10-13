"""Every class and function the governing documents name in their code blocks exists — founder ruling
2026-10-13 ("document names checked against code").

The documents: `.claude/rules/*.md`, `agent-improve/CLAUDE.md`, `agent-improve/ARCHITECTURE.md`. In each
fenced code block that parses as Python, the names it USES — `from X import a`, a call `a(...)`, a method
call `x.a(...)` — must exist either in the repository (a `def` or `class` in its Python files, or a module
attribute it imports) or in the installed packages (an importable `X.a`, or a `def`/`class` of that name
in site-packages), or be a Python built-in. Names a block defines itself are not looked up. A block that
does not parse as Python is not read: prose, YAML, diagrams and shell are out of scope.

The documents name most things in INLINE code, so inline spans are read too: those that look like a
class (`CamelCase`, optionally dotted) or a call (`name(...)`); field names and paths are not.

Two lists, both here so a reader sees them: ABSENT_BY_DESIGN, names a document mentions because they do
not exist or are banned (each with its reason); and BASELINE, the stale names found on 2026-10-13, a
ratchet: a new hit fails, a fixed one must leave the list.

    python tools/architecture/doc_names.py          # every hit; exit 1 on one outside the baseline
"""
from __future__ import annotations

import ast
import builtins
import importlib
import re
import site
import sys
from functools import lru_cache
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
PROJECT = REPO / "agent-improve"
DOCUMENTS = (sorted((REPO / ".claude" / "rules").glob("*.md"))
             + [PROJECT / "CLAUDE.md", PROJECT / "ARCHITECTURE.md"])
FENCE = re.compile(r"^```(\w*)[^\n]*\n(.*?)^```", re.M | re.S)
DEF = re.compile(r"^[ \t]*(?:async[ \t]+def|def|class)[ \t]+(\w+)", re.M)
#: Fences that are never Python, whatever they contain.
#: Mentioned because they do NOT exist here, or are banned: never a stale name.
ABSENT_BY_DESIGN: dict[str, str] = {
    "RetryMiddleware": "named to forbid it: the class does not exist in LangChain 1.x (8.7)",
    "RubricMiddleware": "deepagents, banned while pre-1.0 (4.4)",
    "SkillsMiddleware": "deepagents, banned while pre-1.0 (4.4)",
    "compress_messages": "a banned custom compression function (8.4)",
    "calculate_sample_size": "the banned parameterised-tool form (5.2)",
    "PostgresSaver": "a later stage's checkpointer, not installed",
    "PostgresStore": "a later stage's store, not installed",
    "ContextHubBackend": "deferred (8.3)",
    "PhaseInput": "the family name; the classes are {Phase}PhaseInput",
    "check_gate_status": "planned, step 7.1 (founder ruling 2026-10-13: marked planned)",
    "CircuitBreaker": "not built, required before customers: DEF-124, T35 (founder ruling 2026-10-13)",
}
#: Stale names found 2026-10-13 (founder ruling: report them), named as if built; each leaves the list
#: when its document or the code is corrected. Keyed `path  name`, as `hits()` prints them without line.
BASELINE: frozenset[str] = frozenset()          # all seven fixed or marked, 2026-10-13
SPAN = re.compile(r"(?<!`)`([^`\n]+)`(?!`)")
INLINE_CLASS = re.compile(r"^(?:[\w.]*\.)?([A-Z][a-z0-9]+(?:[A-Z][A-Za-z0-9]*)+)(?:\(.*\))?$")
INLINE_CALL = re.compile(r"^(?:[\w.]*\.)?([a-z_]\w*)\((?:[^()]*)\)$")
NOT_PYTHON = {"yaml", "yml", "json", "mermaid", "text", "env", "bash", "sh", "powershell", "ps1", "toml", "ini",
              "markdown", "md", "html", "css", "js", "javascript", "sql"}


def blocks(path: Path) -> list[tuple[int, str]]:
    """(line, code) for each fenced block of `path` that parses as Python."""
    text = path.read_text(encoding="utf-8")
    out = []
    for m in FENCE.finditer(text):
        lang, code = m.group(1).lower(), m.group(2)
        if lang in NOT_PYTHON:
            continue
        try:
            ast.parse(code)
        except SyntaxError:
            continue
        out.append((text.count("\n", 0, m.start()) + 1, code))
    return out


def used_names(code: str) -> tuple[set[str], set[tuple[str, str]]]:
    """(names used and not defined in the block, (module, name) imports)."""
    tree = ast.parse(code)
    defined: set[str] = set()
    used: set[str] = set()
    imports: set[tuple[str, str]] = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            defined.update(t.id for t in node.targets if isinstance(t, ast.Name))
        elif isinstance(node, ast.ImportFrom) and node.module:
            for a in node.names:
                imports.add((node.module, a.name))
                defined.add(a.asname or a.name)
        elif isinstance(node, ast.Import):
            defined.update((a.asname or a.name).split(".")[0] for a in node.names)
        elif isinstance(node, ast.Call):
            fn = node.func
            if isinstance(fn, ast.Name):
                used.add(fn.id)
            elif isinstance(fn, ast.Attribute):
                used.add(fn.attr)
    return used - defined, imports


def _defined_in(roots: list[Path]) -> set[str]:
    names: set[str] = set()
    for root in roots:
        if not root.exists():
            continue
        for f in root.rglob("*.py"):
            try:
                names.update(DEF.findall(f.read_text(encoding="utf-8", errors="ignore")))
            except OSError:
                continue
    return names


def _site_names() -> set[str]:
    """The installed packages' `def`/`class` names, cached beside the interpreter per installed set (the
    first read of site-packages takes minutes on a synced folder; the cache, seconds)."""
    import hashlib
    import json
    found = (site.getsitepackages() if hasattr(site, "getsitepackages") else []) + \
        [p for p in sys.path if p.endswith("site-packages")]
    roots = sorted({Path(p) for p in found if Path(p).exists()})
    stamp = hashlib.sha256("|".join(sorted(d.name for r in roots for d in r.glob("*.dist-info"))).encode()).hexdigest()
    cache = Path(sys.prefix) / "doc-names-index.json"
    try:
        data = json.loads(cache.read_text(encoding="utf-8"))
        if data.get("stamp") == stamp:
            return set(data["names"])
    except (OSError, ValueError):
        pass
    names = _defined_in(roots)
    try:
        cache.write_text(json.dumps({"stamp": stamp, "names": sorted(names)}), encoding="utf-8")
    except OSError:
        pass
    return names


@lru_cache(maxsize=1)
def known_names() -> frozenset[str]:
    """Every `def`/`class` name in the repository's Python and in the installed packages, plus built-ins."""
    repo = _defined_in([PROJECT / "backend", PROJECT / "scripts", PROJECT / "tools", REPO / ".claude" / "hooks"])
    return frozenset(set(dir(builtins)) | repo | _site_names())


def inline_names(path: Path) -> list[tuple[int, str, str]]:
    """(line, span, name) for each inline code span outside fences that looks like a class or a call."""
    text = FENCE.sub(lambda m: "\n" * m.group(0).count("\n"), path.read_text(encoding="utf-8"))
    out = []
    for m in SPAN.finditer(text):
        span = m.group(1).strip()
        mm = INLINE_CLASS.match(span) or INLINE_CALL.match(span)
        if mm:
            out.append((text.count("\n", 0, m.start()) + 1, span, mm.group(1)))
    return out


def importable(module: str, name: str) -> bool:
    for mod in (module, module.replace("core.", "backend.core.", 1), f"backend.{module}"):
        try:
            m = importlib.import_module(mod)
        except Exception:  # noqa: BLE001 — not importable under this name; try the next
            continue
        if hasattr(m, name):
            return True
        try:
            importlib.import_module(f"{mod}.{name}")
            return True
        except Exception:  # noqa: BLE001
            continue
    return False


def hits() -> list[str]:
    """Every name a document's code block uses that exists nowhere: `path:line  name`."""
    sys.path.insert(0, str(PROJECT))
    out = []
    for path in DOCUMENTS:
        if not path.exists():
            continue
        for line, code in blocks(path):
            used, imports = used_names(code)
            for module, name in sorted(imports):
                if not importable(module, name) and name not in known_names():
                    out.append(f"{path.relative_to(REPO).as_posix()}:{line}  from {module} import {name}")
            for name in sorted(used):
                if name not in known_names() and name not in ABSENT_BY_DESIGN:
                    out.append(f"{path.relative_to(REPO).as_posix()}:{line}  {name}()")
        for line, span, name in inline_names(path):
            if name not in known_names() and name not in ABSENT_BY_DESIGN:
                shown = f"{name}()" if span.endswith(")") and not span[:1].isupper() else name
                out.append(f"{path.relative_to(REPO).as_posix()}:{line}  {shown}")
    return out


def _key(hit: str) -> str:
    path, _, rest = hit.partition(":")
    return f"{path}  {rest.split('  ', 1)[1]}"


def new_hits(found: list[str]) -> list[str]:
    """The hits outside the baseline: what fails."""
    return [h for h in found if _key(h) not in BASELINE]


def fixed(found: list[str]) -> list[str]:
    """Baseline entries no longer found: to be removed from BASELINE (the ratchet)."""
    keys = {_key(h) for h in found}
    return sorted(b for b in BASELINE if b not in keys)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # type: ignore[union-attr]
    found = hits()
    for h in found:
        print(("  (baseline) " if _key(h) in BASELINE else "  NEW        ") + h)
    new, gone = new_hits(found), fixed(found)
    for b in gone:
        print("  FIXED, remove from BASELINE: " + b)
    print(f"{len(found)} name(s) exist nowhere: {len(new)} new, {len(found) - len(new)} in the baseline; "
          f"{len(gone)} baseline entries fixed")
    return 1 if new or gone else 0


if __name__ == "__main__":
    raise SystemExit(main())
