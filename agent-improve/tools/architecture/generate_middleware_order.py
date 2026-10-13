#!/usr/bin/env python3
"""The coach's middleware, in declared order, generated from the code — founder ruling 2026-10-13 (tables
that restate the code are generated). ARCHITECTURE.md §3.3 kept the order by hand; now a generated block
there. What each middleware does stays in the hand-written table below it, whose rows
`test_generated_docs` holds to this order.

Read from `phases/nodes_common.py::_build_executor`'s `middleware=[...]` with `ast`; nothing is
imported. An entry is a class call, a `cast(..., Class(...))`, a factory call, a `*factory()` spread, or
a name bound to a class call earlier in the function.

    generate_middleware_order.py --print | --write | --check | --stage
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generated_doc import GeneratedDoc, GenerationError  # noqa: E402

SOURCE = "backend/phases/nodes_common.py"
BUILDER = "_build_executor"
#: The hand table's row for an entry built by a factory (a class entry's row names the class).
FACTORY_ROW = {"turn_tools.turn_tools_middleware": "Turn tools", "pii.executor_middleware": "PIIMiddleware"}


def _callee(call: ast.Call) -> str:
    if isinstance(call.func, ast.Name) and call.func.id == "cast" and len(call.args) == 2 \
            and isinstance(call.args[1], ast.Call):
        return _callee(call.args[1])
    return ast.unparse(call.func)


def entries(project: Path) -> list[tuple[str, str]]:
    """(what the list declares, the hand table's row name), outermost first."""
    tree = ast.parse((project / SOURCE).read_text(encoding="utf-8"), filename=SOURCE)
    fn = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == BUILDER), None)
    if fn is None:
        raise GenerationError(f"{SOURCE}: no {BUILDER}")
    bound = {n.targets[0].id: _callee(n.value) for n in ast.walk(fn)
             if isinstance(n, ast.Assign) and len(n.targets) == 1 and isinstance(n.targets[0], ast.Name)
             and isinstance(n.value, ast.Call)}
    listed = next((k.value for n in ast.walk(fn) if isinstance(n, ast.Call)
                   for k in n.keywords if k.arg == "middleware" and isinstance(k.value, ast.List)), None)
    if listed is None:
        raise GenerationError(f"{SOURCE}: {BUILDER} passes no middleware=[...]")
    out = []
    for e in listed.elts:
        if isinstance(e, ast.Starred) and isinstance(e.value, ast.Call):
            name = f"*{_callee(e.value)}()"
            row = FACTORY_ROW.get(_callee(e.value), "")
        elif isinstance(e, ast.Call):
            callee = _callee(e)
            name = f"{callee}()" if "." in callee else callee
            row = FACTORY_ROW.get(callee, callee)
        elif isinstance(e, ast.Name) and e.id in bound:
            name, row = f"{bound[e.id]}`, bound to `{e.id}", bound[e.id]
        else:
            raise GenerationError(f"{SOURCE}: a middleware entry it cannot read: {ast.unparse(e)}")
        if not row:
            raise GenerationError(f"{SOURCE}: no table row for factory {name}; add it to FACTORY_ROW")
        out.append((name, row))
    return out


def generate(project: Path) -> str:
    rows = ["| Declared | Middleware |", "|---|---|"]
    for i, (name, _) in enumerate(entries(project), 1):
        rows.append(f"| {i} | `{name}` |")
    return "\n".join(rows) + "\n"


DOC = GeneratedDoc("middleware order", "agent-improve/ARCHITECTURE.md", generate)

if __name__ == "__main__":
    sys.exit(DOC.main(sys.argv[1:]))
