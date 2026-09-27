"""Where Agent Improve keeps things — the ONE owner of the storage layout.

Founder, 2026-09-27 (Part G): every Blob path, Store namespace and search-index
field list that had no single owner is declared HERE, the code that reads and
writes them points here, and ARCHITECTURE.md's generated data-models block is
generated from here (`tools/architecture/generate_models.py`, which reads this
file with `ast` and never imports it). The knowledge index keeps its own owner,
`knowledge/retriever.py::KNOWLEDGE_INDEX_FIELDS`.

**Every constant here is a literal** (strings, tuples, dicts of literals), so
the generator can read it with `ast.literal_eval`. Only `search_fields` builds
SDK objects, and it imports the SDK lazily.

Nothing here reads live Azure. Changing a value here changes where data goes:
it is a storage migration, not a rename.
"""
from __future__ import annotations

from typing import Any

# ── Blob — the case container (`settings.AZURE_BLOB_CONTAINER_IMPROVE`) ─────
#: `storage/blob.py` — the system of record, one per case.
CASE_BLOB = "cases/case_{case_id}.json"
#: `storage/blob.py` — the case registry the case list reads.
REGISTRY_BLOB = "registry.json"
#: `storage/blob.py` — an uploaded file's bytes.
UPLOAD_BLOB = "uploads/{case_id}/{filename}"
#: `core/checkpointer.py` — a thread's checkpoints: the parent graph's …
CHECKPOINT_THREAD = "checkpoints/{thread_id}"
#: … and a subgraph's, under its percent-encoded `checkpoint_ns`.
CHECKPOINT_NAMESPACED = "checkpoints/{thread_id}/ns/{checkpoint_ns}"
#: Under either prefix: the newest checkpoint, every checkpoint, and one
#: checkpoint's pending writes (one blob per task).
CHECKPOINT_LATEST = "{prefix}/latest.json"
CHECKPOINT_HISTORY = "{prefix}/history/{checkpoint_id}.json"
CHECKPOINT_WRITES = "{prefix}/writes/{checkpoint_id}/"
#: `core/store.py` — every Store item, `store/{namespace}/{key}.json`.
STORE_PREFIX = "store"
STORE_BLOB = "store/{namespace}/{key}.json"

#: The table the generated block prints: literals, so `ast` reads them; a test
#: keeps each equal to the template constant above it.
BLOB_PATHS: tuple[tuple[str, str, str], ...] = (
    ("cases/case_{case_id}.json", "storage/blob.py", "The case record — the system of record"),
    ("registry.json", "storage/blob.py", "The case registry"),
    ("uploads/{case_id}/{filename}", "storage/blob.py", "An uploaded file's bytes"),
    ("checkpoints/{thread_id}/latest.json", "core/checkpointer.py", "The parent graph's newest checkpoint"),
    ("checkpoints/{thread_id}/history/{checkpoint_id}.json", "core/checkpointer.py", "Every parent checkpoint"),
    ("checkpoints/{thread_id}/writes/{checkpoint_id}/{task_id}.json", "core/checkpointer.py",
     "A checkpoint's pending writes, one blob per task"),
    ("checkpoints/{thread_id}/ns/{checkpoint_ns}/…", "core/checkpointer.py",
     "The same three for a subgraph namespace (percent-encoded)"),
    ("store/{namespace}/{key}.json", "core/store.py", "One Store item"),
)

# ── Store — `BaseStore` namespaces (§9) ─────────────────────────────────────
STORE_ROOT = "projects"
KIND_CASE = "case"
KIND_ARTIFACTS = "artifacts"
KIND_STEP_LOG = "step_log"
#: The one key under `KIND_CASE`.
CASE_RECORD_KEY = "record"

STORE_NAMESPACES: tuple[tuple[str, str, str], ...] = (
    ("(projects, {case_id}, case)", "record", "The case framing and session copy of the case"),
    ("(projects, {case_id}, artifacts)", "define … control", "Each phase's approved gate document"),
    ("(projects, {case_id}, step_log)", "timestamped", "Append-only cross-phase audit trail"),
)

# ── Search indexes without another owner ────────────────────────────────────
# One dict per field. `kind` picks the SDK class (simple / searchable /
# vector); the flags are the SDK's keyword arguments, unset means the SDK
# default. `knowledge/retriever.py::KNOWLEDGE_INDEX_FIELDS` owns the knowledge
# index.

#: `improve_evidence_index` (§23.2). Written by `gateway/routes.py::_index_upload`
#: (its document's keys are exactly these names), read by `search_evidence`.
EVIDENCE_INDEX: tuple[dict[str, Any], ...] = (
    {"name": "id", "kind": "simple", "type": "Edm.String", "key": True, "filterable": True},
    {"name": "content", "kind": "searchable", "type": "Edm.String"},
    {"name": "content_vector", "kind": "vector", "type": "Collection(Edm.Single)",
     "dimensions": 3072, "profile": "default"},
    {"name": "metadata", "kind": "searchable", "type": "Edm.String"},
    {"name": "case_id", "kind": "simple", "type": "Edm.String", "filterable": True},
    {"name": "phase", "kind": "simple", "type": "Edm.String", "filterable": True},
    {"name": "uploaded_at", "kind": "simple", "type": "Edm.String", "filterable": True,
     "sortable": True},
    {"name": "role", "kind": "searchable", "type": "Edm.String", "filterable": True},
    {"name": "kind", "kind": "simple", "type": "Edm.String", "filterable": True},
    {"name": "description", "kind": "searchable", "type": "Edm.String"},
    {"name": "content_digest", "kind": "simple", "type": "Edm.String", "filterable": True},
    {"name": "shape_match", "kind": "simple", "type": "Edm.String", "filterable": True},
)
#: What `search_evidence` asks the index to return — every field but the vector.
EVIDENCE_SELECT: tuple[str, ...] = (
    "id", "content", "metadata", "case_id",
    "phase", "uploaded_at", "role", "kind",
    "description", "content_digest", "shape_match",
)

#: `improve_case_index` (§23.3). Created by `scripts/create_indexes.py`, read by
#: `search_cases`; no code writes it yet (inventory Z07).
CASE_INDEX: tuple[dict[str, Any], ...] = (
    {"name": "id", "kind": "simple", "type": "Edm.String", "key": True, "filterable": True},
    {"name": "case_id", "kind": "simple", "type": "Edm.String", "filterable": True, "sortable": True},
    {"name": "title", "kind": "searchable", "type": "Edm.String"},
    {"name": "belt_level", "kind": "simple", "type": "Edm.String", "filterable": True,
     "facetable": True},
    {"name": "leader", "kind": "simple", "type": "Edm.String", "filterable": True},
    {"name": "department", "kind": "searchable", "type": "Edm.String", "filterable": True},
    {"name": "current_phase", "kind": "simple", "type": "Edm.String", "filterable": True,
     "facetable": True},
    {"name": "rag_status", "kind": "simple", "type": "Edm.String", "filterable": True,
     "facetable": True},
    {"name": "status", "kind": "simple", "type": "Edm.String", "filterable": True, "facetable": True},
    {"name": "created_at", "kind": "simple", "type": "Edm.String", "filterable": True,
     "sortable": True},
    {"name": "target_date", "kind": "simple", "type": "Edm.String", "filterable": True,
     "sortable": True},
    {"name": "days_in_phase", "kind": "simple", "type": "Edm.Int32", "filterable": True,
     "sortable": True},
    {"name": "phase_summary_define", "kind": "searchable", "type": "Edm.String"},
    {"name": "phase_summary_measure", "kind": "searchable", "type": "Edm.String"},
    {"name": "phase_summary_analyse", "kind": "searchable", "type": "Edm.String"},
    {"name": "phase_summary_improve", "kind": "searchable", "type": "Edm.String"},
    {"name": "phase_summary_control", "kind": "searchable", "type": "Edm.String"},
    {"name": "content_text", "kind": "searchable", "type": "Edm.String"},
    {"name": "embedding", "kind": "vector", "type": "Collection(Edm.Single)",
     "dimensions": 3072, "profile": "improve-vector-profile"},
)
#: What `search_cases` asks the index to return. `id` is there for RRF dedup (S-F17).
CASE_SELECT: tuple[str, ...] = (
    "id", "content_text", "case_id", "title", "current_phase", "rag_status",
)

_FLAGS = ("key", "filterable", "sortable", "facetable")


def search_fields(spec: tuple[dict[str, Any], ...]) -> list:
    """The Azure SDK field objects for an index spec above (the SDK imported lazily)."""
    from azure.search.documents.indexes.models import (
        SearchableField,
        SearchField,
        SearchFieldDataType,
        SimpleField,
    )
    out = []
    for f in spec:
        flags = {k: f[k] for k in _FLAGS if k in f}
        if f["kind"] == "simple":
            out.append(SimpleField(name=f["name"], type=f["type"], **flags))
        elif f["kind"] == "searchable":
            out.append(SearchableField(name=f["name"], type=f["type"], **flags))
        elif f["kind"] == "vector":
            out.append(SearchField(
                name=f["name"],
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                searchable=True,
                vector_search_dimensions=f["dimensions"],
                vector_search_profile_name=f["profile"],
            ))
        else:
            raise ValueError(f"unknown field kind {f['kind']!r} for {f['name']!r}")
    return out


__all__ = [
    "BLOB_PATHS", "CASE_BLOB", "CASE_INDEX", "CASE_RECORD_KEY", "CASE_SELECT",
    "CHECKPOINT_HISTORY", "CHECKPOINT_LATEST", "CHECKPOINT_NAMESPACED", "CHECKPOINT_THREAD",
    "CHECKPOINT_WRITES", "EVIDENCE_INDEX", "EVIDENCE_SELECT", "KIND_ARTIFACTS", "KIND_CASE",
    "KIND_STEP_LOG", "REGISTRY_BLOB", "STORE_BLOB", "STORE_NAMESPACES", "STORE_PREFIX",
    "STORE_ROOT", "UPLOAD_BLOB", "search_fields",
]
