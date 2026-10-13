#!/usr/bin/env python3
"""The search indexes' fields, generated from the code — founder ruling 2026-10-13 (tables that restate
the code are generated). Was the hand-written "Indexes" table in ARCHITECTURE.md §4.1; now a generated
block there, with what each field is used for kept as hand-written notes below it.

The knowledge index's fields are read from `knowledge/retriever.py::KNOWLEDGE_INDEX_FIELDS` (the SDK
calls, read with `ast`); the evidence and case indexes' from `storage/layout.py::EVIDENCE_INDEX` and
`CASE_INDEX`, and what a search returns from `EVIDENCE_SELECT` and `CASE_SELECT`. Nothing is imported.

    generate_index_fields.py --print | --write | --check | --stage
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
from generated_doc import GeneratedDoc, GenerationError  # noqa: E402

RETRIEVER = "backend/knowledge/retriever.py"
LAYOUT = "backend/storage/layout.py"
FLAGS = ("key", "filterable", "sortable", "facetable")
#: The SDK class each knowledge field is built with, as layout's `kind` names it.
SDK_KIND = {"SimpleField": "simple", "SearchableField": "searchable", "SearchField": "vector"}


def _constant(project: Path, rel: str, name: str) -> ast.expr:
    tree = ast.parse((project / rel).read_text(encoding="utf-8"), filename=rel)
    for node in tree.body:
        target: ast.expr
        value: ast.expr | None
        if isinstance(node, ast.AnnAssign):
            target, value = node.target, node.value
        elif isinstance(node, ast.Assign) and len(node.targets) == 1:
            target, value = node.targets[0], node.value
        else:
            continue
        if isinstance(target, ast.Name) and target.id == name and value is not None:
            return value
    raise GenerationError(f"{rel}: no constant {name}")


def _sdk_type(node: ast.expr) -> str:
    """`SearchFieldDataType.String` -> `Edm.String`; `....Collection(....Single)` -> `Collection(Edm.Single)`."""
    if isinstance(node, ast.Attribute):
        return f"Edm.{node.attr}"
    if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.args:
        return f"{node.func.attr}({_sdk_type(node.args[0])})"
    raise GenerationError(f"{RETRIEVER}: a field type it cannot read: {ast.dump(node)[:80]}")


def _knowledge(project: Path) -> list[dict[str, Any]]:
    value = _constant(project, RETRIEVER, "KNOWLEDGE_INDEX_FIELDS")
    if not isinstance(value, ast.List):
        raise GenerationError(f"{RETRIEVER}: KNOWLEDGE_INDEX_FIELDS is not a list")
    fields = []
    for call in value.elts:
        if not (isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and call.func.id in SDK_KIND):
            raise GenerationError(f"{RETRIEVER}: a knowledge field it cannot read")
        kw = {k.arg: k.value for k in call.keywords if k.arg}
        field: dict[str, Any] = {"name": ast.literal_eval(kw["name"]), "kind": SDK_KIND[call.func.id],
                                 "type": _sdk_type(kw["type"])}
        field.update({f: ast.literal_eval(kw[f]) for f in FLAGS if f in kw})
        if "vector_search_profile_name" in kw:
            field["dimensions"] = ast.literal_eval(kw["vector_search_dimensions"])
            field["profile"] = ast.literal_eval(kw["vector_search_profile_name"])
        fields.append(field)
    return fields


def _row(index: str, f: dict[str, Any], returned: str) -> str:
    flags = [k for k in FLAGS if f.get(k)]
    if f["kind"] == "searchable":
        flags.insert(0, "searchable")
    if f["kind"] == "vector":
        flags.append(f"vector {f['dimensions']}, profile `{f['profile']}`")
    return f"| {index} | `{f['name']}` | `{f['type']}` | {', '.join(flags) or '—'} | {returned} |"


def generate(project: Path) -> str:
    rows = ["| Index | Field | Type | Flags | Returned by search |", "|---|---|---|---|---|"]
    for f in _knowledge(project):
        rows.append(_row("knowledge", f, "LangChain's choice"))
    for index, spec, select in (("evidence", "EVIDENCE_INDEX", "EVIDENCE_SELECT"),
                                ("case", "CASE_INDEX", "CASE_SELECT")):
        returned = set(ast.literal_eval(_constant(project, LAYOUT, select)))
        for f in ast.literal_eval(_constant(project, LAYOUT, spec)):
            rows.append(_row(index, f, "yes" if f["name"] in returned else "—"))
    return "\n".join(rows) + "\n"


DOC = GeneratedDoc("index fields", "agent-improve/ARCHITECTURE.md", generate)

if __name__ == "__main__":
    sys.exit(DOC.main(sys.argv[1:]))
