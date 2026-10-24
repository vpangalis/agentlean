#!/usr/bin/env python3
"""The code layout, generated from the code — founder, 2026-09-30 (ARCHITECTURE.md headroom, A1).
Was the hand-written table of ARCHITECTURE.md §3.1; now `docs/code-layout.md`, linked from there.

One row per module under `backend/` (tests and empty `__init__.py` excluded): its folder, its file
— marked **C** when the classes rule (.claude/rules/module-layout.md §2) designates it for classes —
the first line of its docstring, and its public top-level names (classes, functions, and UPPER_CASE
constants). Read with `ast`; nothing is imported. `class_violations` lists every class in a file the
rule does not designate (audit A10: the mark used to come from the class itself, so the check could
not fail).

    generate_layout.py --print | --write | --check | --stage
"""
from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generated_doc import GeneratedDoc  # noqa: E402


def _public(tree: ast.Module) -> tuple[bool, list[str]]:
    has_class, names = False, []
    for node in tree.body:
        if isinstance(node, ast.ClassDef):
            has_class = True
            if not node.name.startswith("_"):
                names.append(node.name)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and not node.name.startswith("_"):
            names.append(node.name)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            names += [t.id for t in targets if isinstance(t, ast.Name) and t.id.isupper() and not t.id.startswith("_")]
    return has_class, names


#: The classes rule, relative to the repository (the project's parent).
RULE = Path(".claude") / "rules" / "module-layout.md"
#: §2's one named exception, written in its prose rather than its lists.
EXCEPTION = "validation/gate_validator.py"


def designated(rule_text: str) -> list[re.Pattern[str]]:
    """The backend files §2 of the classes rule designates, as patterns over paths relative to `backend/` —
    `phases/{phase}/schema.py` stands for every phase's."""
    section = rule_text[rule_text.index("## 2. WHERE CLASSES ARE ALLOWED"):rule_text.index("All other files contain")]
    paths = set(re.findall(r"`([a-z_]+/[^`\s]+\.py)`", section)) | {EXCEPTION}
    return [re.compile("^" + re.escape(p).replace(r"\{phase\}", "[a-z_]+") + "$") for p in sorted(paths)]


def class_violations(project: Path) -> list[tuple[str, str]]:
    """(file, class) for every class, at any depth, in a backend file the classes rule does not designate."""
    allowed = designated((project.parent / RULE).read_text(encoding="utf-8"))
    out = []
    for path in sorted((project / "backend").rglob("*.py")):
        rel = path.relative_to(project / "backend").as_posix()
        if rel.startswith("tests/") or any(p.match(rel) for p in allowed):
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        out += [(rel, n.name) for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
    return out


def generate(project: Path) -> str:
    backend = project / "backend"
    allowed = designated((project.parent / RULE).read_text(encoding="utf-8"))
    rows = ["| Folder | File | Says | Public names |", "|---|---|---|---|"]
    last = None
    for path in sorted(backend.rglob("*.py")):
        rel = path.relative_to(backend)
        if rel.parts[0] == "tests":
            continue
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        _has_class, names = _public(tree)
        doc = (ast.get_docstring(tree) or "").strip().split("\n")[0].replace("|", "\\|")
        if path.name == "__init__.py" and not names and not doc:
            continue
        # backend/ itself is "—", not backticked: rule 17's reader (design_files) joins a bare
        # file name to a backticked folder cell, and to backend/ under a plain one.
        folder = (rel.parent.as_posix() + "/") if rel.parent.as_posix() != "." else "—"
        shown = "" if folder == last else (folder if folder == "—" else f"`{folder}`")
        last = folder
        listed = ", ".join(f"`{n}`" for n in names) or "—"
        marked = any(p.match(rel.as_posix()) for p in allowed)
        rows.append(f"| {shown} | `{rel.name}`{' C' if marked else ''} | {doc or '—'} | {listed} |")
    return ("### Code layout — `backend/`, generated\n\n"
            "Classes are allowed only in files marked **C**; elsewhere module-level functions "
            "(ARCHITECTURE.md §3.1).\n\n" + "\n".join(rows) + "\n")


DOC = GeneratedDoc("code layout", "agent-improve/docs/code-layout.md", generate)

if __name__ == "__main__":
    sys.exit(DOC.main(sys.argv[1:]))
