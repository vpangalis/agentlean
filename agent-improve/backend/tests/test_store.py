"""Tests for `AzureBlobStore` — procedure step 3.2.

Reference §9 (the Store) · §10 (two Blob concerns) · S-C06 · CLAUDE.md §0.24.

The step's Verify is a `live-run` (`scripts/verify_store.py`), which needs real
Azure credentials. These tests cover what can be asserted WITHOUT a network:
the §0.24 interface shape, the §9 path convention, and the op-dispatch
semantics. Both matter in CI, where the live-run cannot run.
"""
from __future__ import annotations

import json
from typing import Any
from unittest.mock import MagicMock

import pytest
from azure.core.exceptions import ResourceNotFoundError
from langgraph.store.base import BaseStore, GetOp, Item, PutOp, SearchOp

from backend.core.store import STORE_PREFIX, AzureBlobStore, blob_path

CASE = "IMPR-2026-E9D"
NS = ("projects", CASE, "artifacts")


# ── §0.24: the interface shape is the whole point ─────────────────────────

def test_subclasses_basestore() -> None:
    """§0.24: a custom Azure backend is correct BECAUSE it implements the
    framework primitive. A bespoke save/load API would be the reinvention."""
    assert issubclass(AzureBlobStore, BaseStore)


def test_implements_only_the_two_abstract_dispatchers() -> None:
    """`BaseStore`'s abstract methods are `batch` and `abatch`; everything
    else is concrete on the base and routes through them."""
    assert BaseStore.__abstractmethods__ == frozenset({"batch", "abatch"})
    assert "batch" in AzureBlobStore.__dict__
    assert "abatch" in AzureBlobStore.__dict__
    assert not AzureBlobStore.__abstractmethods__


@pytest.mark.parametrize(
    "method", ["get", "put", "search", "delete", "list_namespaces",
               "aget", "aput", "asearch", "adelete", "alist_namespaces"]
)
def test_public_surface_is_inherited_not_reimplemented(method: str) -> None:
    """The §0.24 regression guard.

    Overriding `put`/`get` directly would produce a bespoke API wearing a
    `BaseStore` name, and would skip whatever the base does around them —
    `delete()` is literally `batch([PutOp(ns, key, None)])`, so an override
    that forgot that would break deletion silently.
    """
    assert method not in AzureBlobStore.__dict__, (
        f"{method}() must be inherited from BaseStore, not reimplemented"
    )
    assert getattr(AzureBlobStore, method) is getattr(BaseStore, method)


# ── §9: the namespace convention and blob prefix ──────────────────────────

def test_blob_path_matches_the_reference_prefix() -> None:
    """§9 / §10: `store/projects/{case_id}/{kind}/{key}.json`."""
    assert blob_path(NS, "define") == (
        f"store/projects/{CASE}/artifacts/define.json"
    )


@pytest.mark.parametrize("kind,key", [
    ("case", "record"),
    ("artifacts", "define"),
    ("artifacts", "control"),
    ("step_log", "2026-08-31T09:52:49Z"),
])
def test_all_three_namespaces_produce_the_documented_layout(kind, key) -> None:
    """§10's complete physical layout, transcribed."""
    assert blob_path(("projects", CASE, kind), key) == (
        f"store/projects/{CASE}/{kind}/{key}.json"
    )


def test_blob_path_rejects_an_empty_namespace() -> None:
    with pytest.raises(ValueError):
        blob_path((), "define")


def test_namespace_and_key_inverts_blob_path() -> None:
    path = blob_path(NS, "define")
    assert AzureBlobStore._namespace_and_key(path) == (NS, "define")


@pytest.mark.parametrize("foreign", [
    f"cases/case_{CASE}.json",          # §10 concern 2 — storage/blob.py
    f"checkpoints/{CASE}/latest.json",  # §10 concern 1 — core/checkpointer.py
    "registry.json",
    f"{STORE_PREFIX}/notjson.txt",
])
def test_foreign_paths_are_not_claimed(foreign: str) -> None:
    """§10 ratifies three separate Blob concerns. This class owns `store/`
    and must not mistake another owner's blob for one of its items."""
    assert AzureBlobStore._namespace_and_key(foreign) is None


# ── op dispatch, against a fake container (no network) ────────────────────

class FakeBlob:
    def __init__(self, store: dict[str, bytes], path: str) -> None:
        self._store, self._path = store, path

    def download_blob(self):
        if self._path not in self._store:
            raise ResourceNotFoundError(self._path)
        downloader = MagicMock()
        downloader.readall.return_value = self._store[self._path]
        downloader.properties = {"creation_time": None, "last_modified": None}
        return downloader

    def upload_blob(self, data: bytes, overwrite: bool = False) -> None:
        assert overwrite is True, "B1 requires an overwriting put"
        self._store[self._path] = data

    def delete_blob(self) -> None:
        if self._path not in self._store:
            raise ResourceNotFoundError(self._path)
        del self._store[self._path]


def make_store(blobs: dict[str, bytes] | None = None):
    blobs = blobs if blobs is not None else {}
    container = MagicMock()
    container.get_blob_client.side_effect = lambda p: FakeBlob(blobs, p)

    def list_blobs(name_starts_with: str = ""):
        for name in sorted(blobs):
            if name.startswith(name_starts_with):
                props = MagicMock()
                props.name = name
                props.get.return_value = None
                yield props

    container.list_blobs.side_effect = list_blobs
    return AzureBlobStore(container, "conn", "container"), blobs


def test_put_then_get_round_trips() -> None:
    store, blobs = make_store()
    value: dict[str, Any] = {"phase": "define", "goal_statement": "Reduce to 20"}
    store.put(NS, "define", value)
    assert blob_path(NS, "define") in blobs
    item = store.get(NS, "define")
    assert isinstance(item, Item)
    assert item.value == value
    assert item.namespace == NS and item.key == "define"


def test_blob_body_is_the_value_itself_not_an_envelope() -> None:
    """§10: each `artifacts/{phase}.json` HOLDS the gate document, so the
    blob stays directly readable rather than wrapping it in metadata."""
    store, blobs = make_store()
    value = {"phase": "define", "baseline_metric": "38 per week"}
    store.put(NS, "define", value)
    assert json.loads(blobs[blob_path(NS, "define")].decode("utf-8")) == value


def test_get_returns_none_for_an_unwritten_key() -> None:
    """S-C06 B2: never raise."""
    store, _ = make_store()
    assert store.get(NS, "measure") is None


def test_put_is_idempotent_on_replay() -> None:
    """S-C06 B1: overwrite rather than append (§47)."""
    store, blobs = make_store()
    value = {"phase": "define"}
    store.put(NS, "define", value)
    store.put(NS, "define", value)
    assert len(blobs) == 1
    assert store.get(NS, "define").value == value


def test_delete_arrives_as_a_putop_with_value_none() -> None:
    """`BaseStore.delete()` is expressed as `batch([PutOp(ns, key, None)])`.
    An override of `delete()` would have hidden this."""
    store, blobs = make_store()
    store.put(NS, "define", {"phase": "define"})
    store.delete(NS, "define")
    assert blobs == {}
    assert store.get(NS, "define") is None


def test_delete_of_a_missing_key_is_a_no_op() -> None:
    store, _ = make_store()
    store.delete(NS, "never-written")


def test_batch_dispatches_mixed_ops_in_order() -> None:
    store, _ = make_store()
    results = store.batch([
        PutOp(NS, "define", {"phase": "define"}, index=None, ttl=None),
        GetOp(NS, "define", refresh_ttl=False),
        GetOp(NS, "absent", refresh_ttl=False),
    ])
    assert results[0] is None
    assert isinstance(results[1], Item) and results[1].value == {"phase": "define"}
    assert results[2] is None


def test_search_filters_and_limits() -> None:
    store, _ = make_store()
    store.put(NS, "define", {"phase": "define"})
    store.put(NS, "measure", {"phase": "measure"})
    assert {i.key for i in store.search(NS, limit=10)} == {"define", "measure"}
    hits = store.search(NS, filter={"phase": "measure"}, limit=10)
    assert [i.key for i in hits] == ["measure"]
    assert len(store.search(NS, limit=1)) == 1


def test_search_does_not_cross_into_another_case() -> None:
    """The Store carries cross-PHASE data within ONE project (S-C06)."""
    store, _ = make_store()
    store.put(NS, "define", {"phase": "define"})
    store.put(("projects", "IMPR-2026-XXX", "artifacts"), "define", {"phase": "x"})
    assert [i.key for i in store.search(NS, limit=10)] == ["define"]
    assert all(i.namespace == NS for i in store.search(NS, limit=10))


def test_semantic_query_is_rejected_and_names_the_other_mechanism() -> None:
    """S-C06 invariant: cross-case retrieval is `rag_lookup_case_history` —
    'two mechanisms, no overlap'. Returning [] would make an empty result
    indistinguishable from an empty corpus."""
    store, _ = make_store()
    with pytest.raises(NotImplementedError, match="rag_lookup_case_history"):
        store.search(NS, query="what was the root cause")


def test_retired_gate_documents_namespace_is_not_referenced() -> None:
    """§9: 'The `gate_documents` namespace is retired.' Reintroducing it is a
    violation — a phase's approved artifacts and its gate document are the
    same object."""
    import inspect

    from backend.core import store as store_module
    assert "gate_documents" not in inspect.getsource(store_module).replace(
        "The `gate_documents` namespace is retired", ""
    ).replace("gate_documents` namespace is retired and must not return", "")


def test_list_namespaces_derives_from_written_blobs() -> None:
    store, _ = make_store()
    store.put(NS, "define", {"phase": "define"})
    store.put(("projects", CASE, "case"), "record", {"title": "t"})
    assert set(store.list_namespaces()) == {
        ("projects", CASE, "artifacts"),
        ("projects", CASE, "case"),
    }
    assert set(store.list_namespaces(max_depth=2)) == {("projects", CASE)}
