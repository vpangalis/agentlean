"""Founder 2026-09-30 (ARCHITECTURE.md headroom, A1 and A3): the code layout and the API routes are
generated from the code into docs/code-layout.md and docs/api-routes.md, as §4.2's declarations are
into docs/data-models.md. The pre-commit hook regenerates both; this checks each file equals a fresh
generation, and that ARCHITECTURE.md links them."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
TOOLS = PROJECT / "tools" / "architecture"
sys.path.insert(0, str(TOOLS))

import generate_layout  # noqa: E402
import generate_routes  # noqa: E402
import generate_value_keys  # noqa: E402
import generate_index_fields  # noqa: E402
import generate_middleware_order  # noqa: E402


@pytest.mark.parametrize("gen", [generate_layout, generate_routes, generate_value_keys, generate_index_fields,
                                 generate_middleware_order],
                         ids=["code layout", "api routes", "value keys", "index fields", "middleware order"])
def test_the_generated_document_is_current(gen) -> None:
    doc = gen.DOC
    text = (PROJECT.parent / doc.doc_rel).read_text(encoding="utf-8")
    assert doc.span(text) is not None, f"{doc.doc_rel} has no generated block"
    assert doc.is_current(text, PROJECT), f"{doc.doc_rel} differs from a fresh generation — run {gen.__name__}.py --write"


def test_architecture_links_both() -> None:
    arch = (PROJECT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    assert "(docs/code-layout.md)" in arch and "(docs/api-routes.md)" in arch


def test_every_route_is_listed() -> None:
    body = generate_routes.generate(PROJECT)
    for path in ("/ask", "/upload", "/gate", "/gate/decision", "/cases", "/health"):
        assert f"| `{path}` |" in body, path


def test_the_graph_route_table_names_real_routes() -> None:
    """Founder ruling 2026-10-13 (tables that restate the code): §2.4's route → graph table stays
    hand-written — its cells are prose — but its route column is checked against `gateway/routes.py`:
    every route it names exists, and every handler that runs the graph (`_run_turn`) is in it."""
    import ast
    import re
    arch = (PROJECT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    start = arch.index("| Route | Graph input |")
    table = arch[start:arch.index("\n\n", start)]
    named = set(re.findall(r"^\| `(GET|POST|PUT|PATCH|DELETE) ([^`]+)` \|", table, re.M))
    tree = ast.parse((PROJECT / "backend" / "gateway" / "routes.py").read_text(encoding="utf-8"))
    routes, runs_graph = set(), set()
    for node in tree.body:
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for dec in node.decorator_list:
            if (isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute)
                    and isinstance(dec.func.value, ast.Name) and dec.func.value.id == "router"
                    and isinstance(dec.args[0], ast.Constant)):
                route = (dec.func.attr.upper(), str(dec.args[0].value))
                routes.add(route)
                if any(isinstance(n, ast.Name) and n.id == "_run_turn" for n in ast.walk(node)):
                    runs_graph.add(route)
    assert named, "§2.4's route table not found"
    assert named <= routes, f"§2.4 names routes that do not exist: {sorted(named - routes)}"
    assert runs_graph <= named, f"routes that run the graph, missing from §2.4: {sorted(runs_graph - named)}"


def test_the_middleware_table_is_in_the_declared_order() -> None:
    """Founder ruling 2026-10-13: §3.3's order is generated from `_build_executor`; the hand-written
    table of what each middleware does keeps one row per entry, in that order."""
    arch = (PROJECT / "ARCHITECTURE.md").read_text(encoding="utf-8")
    start = arch.index("| Middleware | Where, and what it does |")
    rows = [r.split("|")[1] for r in arch[start:arch.index("\n\n", start)].splitlines()[2:]]
    declared = [row for _, row in generate_middleware_order.entries(PROJECT)]
    assert len(rows) == len(declared), f"{len(rows)} table rows, {len(declared)} declared middleware"
    for n, (cell, name) in enumerate(zip(rows, declared), 1):
        assert name in cell, f"row {n} is {cell.strip()!r}; the declared list has {name} there"
