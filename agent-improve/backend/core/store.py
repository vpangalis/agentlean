"""`AzureBlobStore` — the `BaseStore` implementation carrying cross-phase artifacts.

Canonical definition: reference **§58.6 — S-C06**. Architecture: §9 (the Store)
and §10 (Azure Blob — two distinct concerns). Procedure step 3.2. S-C06 carries
a *rebuild test*: this class must be reconstructable from that entry alone.

Explicit — nodes call `put`/`get` — as opposed to the checkpointer, which
LangGraph drives automatically. **It is the only mechanism that moves a value
across a phase boundary**, because it is the only one that survives the process
ending between two sessions nine days apart (§9).

WHY THIS SUBCLASSES `BaseStore` RATHER THAN DEFINING ITS OWN API
---------------------------------------------------------------
CLAUDE.md §0.24: a framework gap is a real answer, but *supplying a backend to
a framework primitive is using the primitive; writing your own alongside it is
the violation*. LangGraph ships no Azure Blob store, so a custom backend is
warranted — and it is correct precisely because it implements `BaseStore`.

**`BaseStore`'s only abstract methods are `batch()` and `abatch()`** (verified
against the pinned langgraph 1.2.11). `get`, `put`, `search`, `delete`,
`list_namespaces` and their async twins are CONCRETE on the base class and are
expressed in terms of those two. So the whole public surface S-C06 names is
implemented here by implementing the two operation dispatchers and nothing
else. Overriding `put`/`get` directly would have produced a bespoke API wearing
a `BaseStore` name — the reinvention §0.24 exists to prevent — and would have
silently skipped whatever the base does around them (`delete()`, for one, is
literally `batch([PutOp(namespace, key, None)])`).

CONCERN SEPARATION (§10) — THIS IS NOT `storage/blob.py`
--------------------------------------------------------
§10 ratifies two distinct Blob concerns with two owners, and they are not
merged:

  * **checkpoints** — in-flight graph state, `checkpoints/{case_id}/...`,
    owned by `core/checkpointer.py` (S-C07).
  * **case records** — the system of record, `cases/case_{id}.json`,
    `registry.json`, `uploads/...`, owned by `storage/blob.py` via
    `ImproveBlobClient` (S-C08).

This file owns a third path prefix, `store/`, and none of the others. In
particular `cases/case_{id}.json` stays authoritative: the `case` namespace
here is a session-start COPY so that mappers depend on `BaseStore` alone, not a
second system of record (§9).
"""
from __future__ import annotations

import json
import logging
import threading
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Any, AsyncIterator, Iterable, Optional

from azure.core.exceptions import ResourceNotFoundError
from azure.storage.blob import ContainerClient
from azure.storage.blob.aio import (
    BlobServiceClient as AsyncBlobServiceClient,
    ContainerClient as AsyncContainerClient,
)
from langgraph.store.base import (
    BaseStore,
    GetOp,
    Item,
    ListNamespacesOp,
    Op,
    PutOp,
    Result,
    SearchOp,
)

from backend.core.config import settings

logger = logging.getLogger(__name__)

#: Every blob this class owns lives under this prefix and nothing else does.
STORE_PREFIX = "store"


def blob_path(namespace: tuple[str, ...], key: str) -> str:
    """`("projects", case_id, kind), "define"` -> the §9 blob prefix.

        store/projects/{case_id}/{kind}/{key}.json

    Generic over namespace depth on purpose: the convention is three segments
    (§9) but `BaseStore` does not constrain depth, and hard-coding three would
    make any other namespace silently collide at the root.
    """
    if not namespace:
        raise ValueError("namespace must have at least one segment")
    segments = "/".join(namespace)
    return f"{STORE_PREFIX}/{segments}/{key}.json"


class AzureBlobStore(BaseStore):
    """Cross-phase artifact store on Azure Blob.

    Namespaces (§9):

    | Namespace                             | Keys              | Contents |
    |---------------------------------------|-------------------|----------|
    | `("projects", case_id, "case")`       | `"record"`        | Case framing, written once at session start |
    | `("projects", case_id, "artifacts")`  | `"define"` … `"control"` | Each phase's approved gate document |
    | `("projects", case_id, "step_log")`   | timestamped       | Append-only cross-phase audit trail |

    **The `gate_documents` namespace is retired and must not return** — a
    phase's approved artifacts and its gate document are the same object, and
    two keys holding the same content pose an authority question with no
    answer (§9).

    On-blob format is **the value itself**, not an envelope. §10's physical
    layout says each `artifacts/{phase}.json` *holds the gate document*, so the
    blob is directly readable by a human or another tool. `Item.created_at` and
    `Item.updated_at` come from the blob's own `creation_time` and
    `last_modified` rather than from duplicated fields inside the body.
    """

    # ── construction ──────────────────────────────────────────────────
    def __init__(
        self,
        container_client: ContainerClient,
        connection_string: str,
        container_name: str,
    ) -> None:
        super().__init__()
        # Sync client, built once. A sync client holds no event-loop-bound
        # session, so keeping it costs nothing and matches how
        # ImproveBlobClient and the checkpointer already work.
        self._container = container_client
        # The async client is NOT held — see `_async_container`.
        self._connection_string = connection_string
        self._container_name = container_name
        self._lock = threading.Lock()

    # ── the aio session lifecycle ─────────────────────────────────────
    #
    # PER-OPERATION, and deliberately so.
    #
    # An `azure.storage.blob.aio` client owns an aiohttp session bound to the
    # running loop. Holding one for the process life is the faster shape, but
    # it needs a deterministic close at shutdown — and `app.py`'s shutdown hook
    # is procedure step **8.5**, which is GATED on `RunControl.request_drain()`
    # being confirmed to exist. Building this class to depend on 8.5 would
    # couple a Stage 3 step to a gate that may never clear, and closing over it
    # by editing `app.py` here is out of 3.2's scope.
    #
    # So each async operation opens and closes its own client. The session is
    # always closed on the way out, including on an exception, and nothing is
    # left for a shutdown hook to clean up. The cost is one client construction
    # per Store operation, which is the right trade here: Store writes happen
    # at session start and at gate pass — a handful per phase — not per token
    # and not per turn.
    #
    # When 8.5 lands, a cached client plus an `aclose()` on the shutdown hook is
    # a drop-in change behind this same context manager.
    @asynccontextmanager
    async def _async_container(self) -> AsyncIterator[AsyncContainerClient]:
        service = AsyncBlobServiceClient.from_connection_string(
            self._connection_string
        )
        async with service:
            yield service.get_container_client(self._container_name)

    # ── serialisation ─────────────────────────────────────────────────
    @staticmethod
    def _encode(value: dict[str, Any]) -> bytes:
        return json.dumps(value, indent=2, ensure_ascii=False).encode("utf-8")

    @staticmethod
    def _decode(raw: bytes) -> dict[str, Any]:
        return json.loads(raw.decode("utf-8"))

    @staticmethod
    def _item(
        namespace: tuple[str, ...],
        key: str,
        value: dict[str, Any],
        created_at: Optional[datetime],
        updated_at: Optional[datetime],
    ) -> Item:
        now = datetime.now(timezone.utc)
        return Item(
            value=value,
            key=key,
            namespace=namespace,
            created_at=created_at or now,
            updated_at=updated_at or created_at or now,
        )

    @staticmethod
    def _namespace_and_key(path: str) -> Optional[tuple[tuple[str, ...], str]]:
        """Invert `blob_path`. Returns None for anything not ours."""
        if not path.startswith(f"{STORE_PREFIX}/") or not path.endswith(".json"):
            return None
        parts = path[len(STORE_PREFIX) + 1: -len(".json")].split("/")
        if len(parts) < 2:
            return None
        return tuple(parts[:-1]), parts[-1]

    @staticmethod
    def _matches(value: dict[str, Any], filter: Optional[dict[str, Any]]) -> bool:
        """Exact-match filter over top-level value keys."""
        if not filter:
            return True
        return all(value.get(k) == v for k, v in filter.items())

    @staticmethod
    def _reject_semantic_query(query: Optional[str]) -> None:
        """`search(query=...)` is natural-language retrieval and is NOT this
        store's job.

        S-C06's invariant is explicit: the Store carries cross-*phase* data
        within one project; cross-*case* retrieval is `rag_lookup_case_history`
        (S-F16) — "two mechanisms, no overlap". Blob storage has no vector
        index, so answering a semantic query here would mean building a second
        retrieval path beside the one §24 already specifies.

        Raising beats returning [] silently: a caller that wanted semantic
        search and got an empty list would conclude the corpus was empty.
        """
        if query is not None:
            raise NotImplementedError(
                "AzureBlobStore.search() does not support natural-language "
                "`query=` — it has no vector index. Cross-case semantic "
                "retrieval is rag_lookup_case_history (reference §24, S-F16). "
                "`filter=`, `limit=` and `offset=` are supported."
            )

    # ── sync dispatch ─────────────────────────────────────────────────
    def batch(self, ops: Iterable[Op]) -> list[Result]:
        """Synchronous operation dispatch — one of `BaseStore`'s two abstract
        methods. Everything `get`/`put`/`search`/`delete` do arrives here."""
        results: list[Result] = []
        for op in ops:
            if isinstance(op, GetOp):
                results.append(self._get(op))
            elif isinstance(op, PutOp):
                self._put(op)
                results.append(None)
            elif isinstance(op, SearchOp):
                results.append(self._search(op))
            elif isinstance(op, ListNamespacesOp):
                results.append(self._list_namespaces(op))
            else:  # pragma: no cover — the Op union is closed
                raise NotImplementedError(f"Unsupported store op: {type(op).__name__}")
        return results

    def _get(self, op: GetOp) -> Optional[Item]:
        path = blob_path(op.namespace, op.key)
        blob = self._container.get_blob_client(path)
        try:
            downloader = blob.download_blob()
            raw = downloader.readall()
            props = downloader.properties
        except ResourceNotFoundError:
            # B2: a key not yet written returns None and never raises.
            return None
        return self._item(
            op.namespace, op.key, self._decode(raw),
            props.get("creation_time"), props.get("last_modified"),
        )

    def _put(self, op: PutOp) -> None:
        path = blob_path(op.namespace, op.key)
        blob = self._container.get_blob_client(path)
        if op.value is None:
            # BaseStore.delete() is expressed as PutOp(value=None).
            try:
                blob.delete_blob()
            except ResourceNotFoundError:
                pass
            return
        with self._lock:
            # B1: overwrite rather than append, so a replayed write is
            # idempotent (§47).
            blob.upload_blob(self._encode(op.value), overwrite=True)

    def _search(self, op: SearchOp) -> list[Item]:
        self._reject_semantic_query(op.query)
        prefix = f"{STORE_PREFIX}/{'/'.join(op.namespace_prefix)}/"
        items: list[Item] = []
        for props in self._container.list_blobs(name_starts_with=prefix):
            parsed = self._namespace_and_key(props.name)
            if parsed is None:
                continue
            namespace, key = parsed
            blob = self._container.get_blob_client(props.name)
            try:
                value = self._decode(blob.download_blob().readall())
            except ResourceNotFoundError:
                continue
            if not self._matches(value, op.filter):
                continue
            items.append(self._item(
                namespace, key, value,
                props.get("creation_time"), props.get("last_modified"),
            ))
        return items[op.offset: op.offset + op.limit]

    def _list_namespaces(self, op: ListNamespacesOp) -> list[tuple[str, ...]]:
        seen: set[tuple[str, ...]] = set()
        for props in self._container.list_blobs(name_starts_with=f"{STORE_PREFIX}/"):
            parsed = self._namespace_and_key(props.name)
            if parsed is None:
                continue
            namespace = parsed[0]
            if op.max_depth is not None:
                namespace = namespace[: op.max_depth]
            if self._namespace_matches(namespace, op):
                seen.add(namespace)
        ordered = sorted(seen)
        return ordered[op.offset: op.offset + op.limit]

    @staticmethod
    def _namespace_matches(namespace: tuple[str, ...], op: ListNamespacesOp) -> bool:
        for condition in op.match_conditions or ():
            path = tuple(condition.path)
            if condition.match_type == "prefix":
                if namespace[: len(path)] != path:
                    return False
            elif condition.match_type == "suffix":
                if namespace[-len(path):] != path:
                    return False
        return True

    # ── async dispatch ────────────────────────────────────────────────
    async def abatch(self, ops: Iterable[Op]) -> list[Result]:
        """Asynchronous operation dispatch — `BaseStore`'s other abstract
        method, and the one the graph actually travels (§1.4: async by
        default).

        Genuinely async, on `azure.storage.blob.aio`. Note the contrast with
        `core/checkpointer.py`, whose `aput`/`aget_tuple` are thin wrappers
        delegating to the sync path — a shortcut its own comment records. This
        class does not repeat it.
        """
        results: list[Result] = []
        async with self._async_container() as container:
            for op in ops:
                if isinstance(op, GetOp):
                    results.append(await self._aget(container, op))
                elif isinstance(op, PutOp):
                    await self._aput(container, op)
                    results.append(None)
                elif isinstance(op, SearchOp):
                    results.append(await self._asearch(container, op))
                elif isinstance(op, ListNamespacesOp):
                    results.append(await self._alist_namespaces(container, op))
                else:  # pragma: no cover — the Op union is closed
                    raise NotImplementedError(
                        f"Unsupported store op: {type(op).__name__}"
                    )
        return results

    async def _aget(
        self, container: AsyncContainerClient, op: GetOp
    ) -> Optional[Item]:
        path = blob_path(op.namespace, op.key)
        blob = container.get_blob_client(path)
        try:
            downloader = await blob.download_blob()
            raw = await downloader.readall()
            props = downloader.properties
        except ResourceNotFoundError:
            return None                      # B2
        return self._item(
            op.namespace, op.key, self._decode(raw),
            props.get("creation_time"), props.get("last_modified"),
        )

    async def _aput(self, container: AsyncContainerClient, op: PutOp) -> None:
        path = blob_path(op.namespace, op.key)
        blob = container.get_blob_client(path)
        if op.value is None:
            try:
                await blob.delete_blob()
            except ResourceNotFoundError:
                pass
            return
        await blob.upload_blob(self._encode(op.value), overwrite=True)   # B1

    async def _asearch(
        self, container: AsyncContainerClient, op: SearchOp
    ) -> list[Item]:
        self._reject_semantic_query(op.query)
        prefix = f"{STORE_PREFIX}/{'/'.join(op.namespace_prefix)}/"
        items: list[Item] = []
        async for props in container.list_blobs(name_starts_with=prefix):
            parsed = self._namespace_and_key(props.name)
            if parsed is None:
                continue
            namespace, key = parsed
            blob = container.get_blob_client(props.name)
            try:
                downloader = await blob.download_blob()
                value = self._decode(await downloader.readall())
            except ResourceNotFoundError:
                continue
            if not self._matches(value, op.filter):
                continue
            items.append(self._item(
                namespace, key, value,
                props.get("creation_time"), props.get("last_modified"),
            ))
        return items[op.offset: op.offset + op.limit]

    async def _alist_namespaces(
        self, container: AsyncContainerClient, op: ListNamespacesOp
    ) -> list[tuple[str, ...]]:
        seen: set[tuple[str, ...]] = set()
        async for props in container.list_blobs(name_starts_with=f"{STORE_PREFIX}/"):
            parsed = self._namespace_and_key(props.name)
            if parsed is None:
                continue
            namespace = parsed[0]
            if op.max_depth is not None:
                namespace = namespace[: op.max_depth]
            if self._namespace_matches(namespace, op):
                seen.add(namespace)
        ordered = sorted(seen)
        return ordered[op.offset: op.offset + op.limit]


# ─────────────────── Module-level factory ───────────────────

_singleton: Optional[AzureBlobStore] = None
_singleton_lock = threading.Lock()


def get_store() -> AzureBlobStore:
    """Singleton accessor, mirroring `get_checkpointer()`.

    **B3: attach to the PARENT graph only.** A phase subgraph compiles with no
    store — it reaches the parent's (§16).
    """
    global _singleton
    if _singleton is not None:
        return _singleton

    with _singleton_lock:
        if _singleton is not None:
            return _singleton

        conn = settings.AZURE_BLOB_CONNECTION_STRING
        container_name = settings.AZURE_BLOB_CONTAINER_IMPROVE
        if not conn or not container_name:
            raise RuntimeError(
                "AzureBlobStore requires AZURE_BLOB_CONNECTION_STRING and "
                "AZURE_BLOB_CONTAINER_IMPROVE in settings."
            )

        container = ContainerClient.from_connection_string(conn, container_name)
        _singleton = AzureBlobStore(container, conn, container_name)
        logger.info("AzureBlobStore initialised on container=%s", container_name)
        return _singleton


__all__ = ["AzureBlobStore", "get_store", "blob_path", "STORE_PREFIX"]
