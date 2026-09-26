"""Code citations in the feature list — `path::symbol`, checked at HEAD. Step 6.67.

Founder ruling 2026-09-26, Part C: a feature's code citation names WHERE,
never HOW FAR ALONG — no line numbers (they drift with every edit) and no
status words (status comes only from tests). A citation is

    agent-improve/<path>::<symbol>      a def, a class, Class.method or a module-level name
    agent-improve/<path>                a file with no nameable symbol (recorded as such)

`check()` verifies every cited path is tracked at HEAD, every symbol is defined
in it, and every feature's test node id exists; `normalise()` turned the
6.66 draft's `path:line — status (note)` strings into this form once.

    python tools/control_board/citations.py          # list what does not resolve
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import features  # noqa: E402

REPO = features.PROJECT.parent
STATUS_WORDS = ("passed", "missing", "wired", "built", "defect")
_PATHLINE = re.compile(r"^(?P<path>agent-improve/[\w./-]+?)(?::(?P<line>\d+)|::(?P<sym>[\w.\[\]-]+))?(?=\s|$)")


#: The only form a code citation may take: a path, optionally ::symbol — no line, no status.
_FORM = re.compile(r"agent-improve/[\w./-]+(?:::[\w.\[\]-]+)?")


def is_citation(text: str) -> bool:
    return bool(_PATHLINE.match(text.strip()))


def _tracked() -> set[str]:
    out = subprocess.run(["git", "ls-files"], cwd=REPO, capture_output=True, encoding="utf-8").stdout
    return {ln.strip() for ln in out.splitlines()}


def _defs(path: Path) -> dict[str, tuple[int, int]]:
    """name -> (first line, last line) for defs, classes, methods and module-level names."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    out: dict[str, tuple[int, int]] = {}
    for node in tree.body:
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            out[node.name] = (node.lineno, node.end_lineno or node.lineno)
            if isinstance(node, ast.ClassDef):
                for sub in node.body:
                    if isinstance(sub, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        out[f"{node.name}.{sub.name}"] = (sub.lineno, sub.end_lineno or sub.lineno)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            for t in targets:
                if isinstance(t, ast.Name):
                    out[t.id] = (node.lineno, node.end_lineno or node.lineno)
    return out


def _enclosing(defs: dict[str, tuple[int, int]], line: int) -> str | None:
    """The innermost definition containing `line`."""
    hits = [(b - a, name) for name, (a, b) in defs.items() if a <= line <= b]
    return min(hits)[1] if hits else None


def normalise(cite: str) -> str:
    """'path:line — status (note)' -> 'path::symbol' (or 'path')."""
    m = _PATHLINE.match(cite.strip())
    if not m:
        return cite.strip()
    path, line, sym = m.group("path"), m.group("line"), m.group("sym")
    if sym:
        return f"{path}::{sym}"
    full = REPO / path
    note = cite[m.end():]
    if path.endswith(".py") and full.is_file() and line:
        name = _enclosing(_defs(full), int(line))
        if name:
            return f"{path}::{name}"
    if full.is_file() and not path.endswith(".py"):
        text = full.read_text(encoding="utf-8", errors="replace")
        for word in re.findall(r"[A-Za-z_][A-Za-z0-9_]{3,}", note):
            if word not in STATUS_WORDS and re.search(rf"\b{re.escape(word)}\b", text):
                return f"{path}::{word}"
    return path


def resolves(cite: str, tracked: set[str]) -> str:
    """'' when the citation resolves at HEAD, else why not."""
    path, _, sym = cite.partition("::")
    if path not in tracked:
        return "path not tracked at HEAD"
    if not sym:
        return ""
    full = REPO / path
    if path.endswith(".py"):
        base = sym.split("[")[0]
        return "" if base in _defs(full) else f"no symbol {sym}"
    text = full.read_text(encoding="utf-8", errors="replace")
    return "" if re.search(rf"\b{re.escape(sym)}\b", text) else f"no symbol {sym}"


def check(feats: list[dict] | None = None) -> list[tuple[str, str, str]]:
    """(feature id, citation or test, why) for everything that does not resolve."""
    feats = features.load() if feats is None else feats
    tracked = _tracked()
    bad = []
    for f in feats:
        for cite in f["sources"]["code"]:
            if not _FORM.fullmatch(cite):
                bad.append((f["id"], cite, "not in path::symbol form"))
                continue
            why = resolves(cite, tracked)
            if why:
                bad.append((f["id"], cite, why))
        test = "agent-improve/" + features.node_id(f["test"])
        why = resolves(test, tracked)
        if why:
            bad.append((f["id"], f["test"], "test " + why))
    return bad


if __name__ == "__main__":
    problems = check()
    for fid, cite, why in problems:
        print(f"{fid}  {cite}  — {why}")
    print(f"{len(problems)} citation(s) or test(s) do not resolve")
    sys.exit(1 if problems else 0)
