#!/usr/bin/env python3
"""`SupervisorState`'s fields, generated from the code — founder ruling 2026-10-13 (tables that restate
the code are generated). ARCHITECTURE.md §4.1 listed them by hand in its writers table; the field list
and types are now a generated block there. Who writes and reads each field stays in the hand table
below it, which `test_generated_docs` holds to this list.

Read from `core/state.py::SupervisorState`'s annotations with `ast`; nothing is imported.

    generate_state_fields.py --print | --write | --check | --stage
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generated_doc import GeneratedDoc, GenerationError  # noqa: E402

SOURCE = "backend/core/state.py"
CLASS = "SupervisorState"


def fields(project: Path) -> list[tuple[str, str]]:
    tree = ast.parse((project / SOURCE).read_text(encoding="utf-8"), filename=SOURCE)
    cls = next((n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == CLASS), None)
    if cls is None:
        raise GenerationError(f"{SOURCE}: no class {CLASS}")
    return [(n.target.id, ast.unparse(n.annotation)) for n in cls.body
            if isinstance(n, ast.AnnAssign) and isinstance(n.target, ast.Name)]


def generate(project: Path) -> str:
    rows = ["| Field | Type |", "|---|---|"]
    rows += [f"| `{name}` | `{kind}` |" for name, kind in fields(project)]
    return "\n".join(rows) + "\n"


DOC = GeneratedDoc("state fields", "agent-improve/ARCHITECTURE.md", generate)

if __name__ == "__main__":
    sys.exit(DOC.main(sys.argv[1:]))
