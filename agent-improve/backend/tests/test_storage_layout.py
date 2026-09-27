"""`storage/layout.py` is the one owner of the storage layout — founder, 2026-09-27 (Part G).

The code that reads and writes Blob paths, Store namespaces and the evidence and
case index fields now takes them from `storage/layout.py`. **Behaviour is
unchanged**, and these tests are the proof: each compares what the code builds
NOW against a verbatim copy of what it built BEFORE the move (the literals
below are the pre-move code, copied, not re-derived).
"""
from __future__ import annotations

import ast
from pathlib import Path

from azure.search.documents.indexes.models import (
    SearchableField,
    SearchField,
    SearchFieldDataType,
    SimpleField,
)

from backend.storage import layout

_PROJECT = Path(__file__).resolve().parents[2]


# ── the pre-move definitions, verbatim ──────────────────────────────────────

def _old_evidence_fields() -> list:
    """`knowledge/retriever.py::EVIDENCE_INDEX_FIELDS` before 2026-09-27."""
    return [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SearchField(name="content_vector",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=3072,
                    vector_search_profile_name="default"),
        SearchableField(name="metadata", type=SearchFieldDataType.String),
        SimpleField(name="case_id", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="phase", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="uploaded_at", type=SearchFieldDataType.String, filterable=True,
                    sortable=True),
        SearchableField(name="role", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="kind", type=SearchFieldDataType.String, filterable=True),
        SearchableField(name="description", type=SearchFieldDataType.String),
        SimpleField(name="content_digest", type=SearchFieldDataType.String, filterable=True),
        SimpleField(name="shape_match", type=SearchFieldDataType.String, filterable=True),
    ]


def _old_case_fields() -> list:
    """`scripts/create_indexes.py::create_improve_case_index`'s fields before 2026-09-27."""
    S = SearchFieldDataType.String
    return [
        SimpleField(name="id", type=S, key=True, filterable=True),
        SimpleField(name="case_id", type=S, filterable=True, sortable=True),
        SearchableField(name="title", type=S),
        SimpleField(name="belt_level", type=S, filterable=True, facetable=True),
        SimpleField(name="leader", type=S, filterable=True),
        SearchableField(name="department", type=S, filterable=True),
        SimpleField(name="current_phase", type=S, filterable=True, facetable=True),
        SimpleField(name="rag_status", type=S, filterable=True, facetable=True),
        SimpleField(name="status", type=S, filterable=True, facetable=True),
        SimpleField(name="created_at", type=S, filterable=True, sortable=True),
        SimpleField(name="target_date", type=S, filterable=True, sortable=True),
        SimpleField(name="days_in_phase", type=SearchFieldDataType.Int32, filterable=True,
                    sortable=True),
        SearchableField(name="phase_summary_define", type=S),
        SearchableField(name="phase_summary_measure", type=S),
        SearchableField(name="phase_summary_analyse", type=S),
        SearchableField(name="phase_summary_improve", type=S),
        SearchableField(name="phase_summary_control", type=S),
        SearchableField(name="content_text", type=S),
        SearchField(name="embedding",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True, vector_search_dimensions=3072,
                    vector_search_profile_name="improve-vector-profile"),
    ]


# ── the index fields ────────────────────────────────────────────────────────

def test_the_evidence_index_fields_are_what_they_were() -> None:
    from backend.knowledge import retriever
    assert retriever.EVIDENCE_INDEX_FIELDS == _old_evidence_fields()
    assert list(retriever.EVIDENCE_SELECT) == [
        "id", "content", "metadata", "case_id", "phase", "uploaded_at", "role", "kind",
        "description", "content_digest", "shape_match"]


def test_the_case_index_fields_are_what_they_were() -> None:
    assert layout.search_fields(layout.CASE_INDEX) == _old_case_fields()


def test_the_case_index_script_builds_its_fields_from_the_layout() -> None:
    src = (_PROJECT / "scripts" / "create_indexes.py").read_text(encoding="utf-8")
    assert "search_fields(layout.CASE_INDEX)" in src
    import importlib.util
    spec = importlib.util.spec_from_file_location("create_indexes",
                                                  _PROJECT / "scripts" / "create_indexes.py")
    assert spec is not None and spec.loader is not None
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    assert mod.VECTOR_DIMENSIONS == 3072 and mod.VECTOR_PROFILE == "improve-vector-profile", \
        "the case index's vector literals in layout.py must equal the script's constants"


def test_the_case_search_selects_what_it_did() -> None:
    src = (_PROJECT / "backend" / "knowledge" / "retriever.py").read_text(encoding="utf-8")
    assert "select=list(layout.CASE_SELECT)" in src
    assert list(layout.CASE_SELECT) == ["id", "content_text", "case_id", "title",
                                        "current_phase", "rag_status"]


def test_the_evidence_writer_writes_exactly_the_index_fields() -> None:
    """`routes._index_upload` builds its document by hand; its keys ARE the index's names."""
    tree = ast.parse((_PROJECT / "backend" / "gateway" / "routes.py").read_text(encoding="utf-8"))
    fn = next(n for n in ast.walk(tree)
              if isinstance(n, ast.AsyncFunctionDef) and n.name == "_index_upload")
    doc = next(n.value for n in ast.walk(fn) if isinstance(n, ast.Assign)
               and any(isinstance(t, ast.Name) and t.id == "document" for t in n.targets))
    assert isinstance(doc, ast.Dict)
    keys = [k.value for k in doc.keys if isinstance(k, ast.Constant)]
    assert keys == [f["name"] for f in layout.EVIDENCE_INDEX]


# ── the Blob paths and the Store namespaces ─────────────────────────────────

def test_the_blob_paths_are_what_they_were() -> None:
    from backend.core.checkpointer import AzureBlobCheckpointSaver as S
    from backend.core.store import STORE_PREFIX, blob_path
    from backend.storage import blob

    assert blob.case_path("IMPR-2026-ABC") == "cases/case_IMPR-2026-ABC.json"
    assert blob.REGISTRY_BLOB_PATH == "registry.json"
    assert STORE_PREFIX == "store"
    assert blob_path(("projects", "C1", "artifacts"), "define") == "store/projects/C1/artifacts/define.json"
    assert S._prefix("C1", "") == "checkpoints/C1"
    assert S._prefix("C1", "define_phase:x|y") == "checkpoints/C1/ns/define_phase%3Ax%7Cy"
    assert S._latest_path("C1") == "checkpoints/C1/latest.json"
    assert S._history_path("C1", "k9") == "checkpoints/C1/history/k9.json"
    assert S._writes_prefix("C1", "k9") == "checkpoints/C1/writes/k9/"


def test_the_upload_path_is_what_it_was() -> None:
    src = (_PROJECT / "backend" / "storage" / "blob.py").read_text(encoding="utf-8")
    assert "layout.UPLOAD_BLOB.format(case_id=case_id, filename=filename)" in src
    assert layout.UPLOAD_BLOB.format(case_id="C1", filename="a.csv") == "uploads/C1/a.csv"


def test_the_store_namespaces_are_what_they_were() -> None:
    from backend.phases import mappers_common as mc
    assert (layout.STORE_ROOT, mc.KIND_CASE, mc.KIND_ARTIFACTS, layout.CASE_RECORD_KEY) == \
        ("projects", "case", "artifacts", "record")
    tree = ast.parse((_PROJECT / "backend" / "phases" / "mappers_common.py").read_text(encoding="utf-8"))
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
            and n.body and isinstance(n.body[0], ast.Expr) and isinstance(n.body[0].value, ast.Constant)}
    spelled = [n.lineno for n in ast.walk(tree) if isinstance(n, ast.Constant)
               and n.value in ("projects", "record") and id(n) not in docs]
    assert not spelled, f"a Store namespace is spelled in mappers_common, not taken from layout: {spelled}"


def test_every_layout_constant_is_a_literal_the_generator_can_read() -> None:
    tree = ast.parse((_PROJECT / "backend" / "storage" / "layout.py").read_text(encoding="utf-8"))
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)) and node.value is not None:
            ast.literal_eval(node.value)


def test_the_printed_blob_table_spells_the_templates_the_code_uses() -> None:
    printed = {p for p, _, _ in layout.BLOB_PATHS}
    for t in (layout.CASE_BLOB, layout.REGISTRY_BLOB, layout.UPLOAD_BLOB, layout.STORE_BLOB):
        assert t in printed, t
    assert layout.CHECKPOINT_LATEST.format(prefix=layout.CHECKPOINT_THREAD) in printed
    assert layout.CHECKPOINT_HISTORY.format(prefix=layout.CHECKPOINT_THREAD,
                                            checkpoint_id="{checkpoint_id}") in printed
