#!/usr/bin/env python3
"""The API routes, generated from the code — founder, 2026-09-30 (ARCHITECTURE.md headroom, A3).
Was the route table of ARCHITECTURE.md §3.9; now `docs/api-routes.md`, linked from there.

One row per route declared in `backend/gateway/routes.py` (`@router.get/post/put/delete(path)`):
method, path, handler, response model, and the first line of the handler's docstring. Read with
`ast`; nothing is imported.

    generate_routes.py --print | --write | --check | --stage
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generated_doc import GeneratedDoc, GenerationError  # noqa: E402

METHODS = ("get", "post", "put", "patch", "delete")


def generate(project: Path) -> str:
    path = project / "backend" / "gateway" / "routes.py"
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    rows = ["| Method | Path | Handler | Response | Says |", "|---|---|---|---|---|"]
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if not (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                    and dec.func.attr in METHODS and isinstance(dec.func.value, ast.Name)
                    and dec.func.value.id == "router"):
                continue
            if not (dec.args and isinstance(dec.args[0], ast.Constant) and isinstance(dec.args[0].value, str)):
                raise GenerationError(f"route of {node.name} has no literal path")
            model = next((ast.unparse(k.value) for k in dec.keywords if k.arg == "response_model"), "—")
            says = (ast.get_docstring(node) or "").strip().split("\n")[0].replace("|", "\\|") or "—"
            rows.append(f"| {dec.func.attr.upper()} | `{dec.args[0].value}` | `{node.name}` | "
                        f"{'`' + model + '`' if model != '—' else '—'} | {says} |")
    if len(rows) == 2:
        raise GenerationError("no route found in backend/gateway/routes.py")
    return ("### API routes — `backend/gateway/routes.py`, generated\n\n" + "\n".join(rows) + "\n")


DOC = GeneratedDoc("api routes", "agent-improve/docs/api-routes.md", generate)

if __name__ == "__main__":
    sys.exit(DOC.main(sys.argv[1:]))
