"""
Azure Blob checkpointer for Agent Improve.

Implements LangGraph's BaseCheckpointSaver interface backed by
Azure Blob Storage. In-flight graph state lives in:

    checkpoints/{thread_id}/latest.json
    checkpoints/{thread_id}/history/{checkpoint_id}.json

and, for a phase subgraph's own state, the same two files under
a namespace segment:

    checkpoints/{thread_id}/ns/{checkpoint_ns}/latest.json
    checkpoints/{thread_id}/ns/{checkpoint_ns}/history/{id}.json

where thread_id = case_id for Agent Improve and checkpoint_ns is
the value LangGraph assigns each subgraph (empty for the parent).
The namespace segment is not optional -- see _prefix() for why.

Each put() call writes one history blob AND overwrites latest.json.
Both writes are part of the same logical operation; the latest.json
overwrite uses an ETag conditional If-Match to detect concurrent
turns (raises ConcurrentTurnError on conflict).

Per CLAUDE.md this is the designated file for the
AzureBlobCheckpointSaver class. The factory function
get_checkpointer() is module-level (no class wrapping the
singleton).

Compatibility with the installed langgraph-checkpoint 4.1.0:
  - JsonPlusSerializer.dumps_typed() returns msgpack BINARY, not
    utf-8 text. The envelope therefore base64-encodes the serde
    bytes for safe JSON storage and base64-decodes them on restore.
  - put_writes()/aput_writes() take the 4.1.0 `task_path` argument.
  - The factory reads the settings names
    AZURE_BLOB_CONNECTION_STRING and AZURE_BLOB_CONTAINER_IMPROVE
    (matching storage/blob.py).
"""

from __future__ import annotations

import asyncio
import base64
import json
import logging
import threading
from urllib.parse import quote
from typing import Any, AsyncIterator, Callable, Iterator, List, Optional, Sequence, Tuple, cast

from azure.core import MatchConditions
from azure.core.exceptions import (
    ResourceExistsError,
    ResourceModifiedError,
    ResourceNotFoundError,
)
from azure.storage.blob import BlobClient, ContainerClient
from azure.storage.blob.aio import (
    BlobClient as AsyncBlobClient,
    ContainerClient as AsyncContainerClient,
)
from langgraph.checkpoint.base import (
    WRITES_IDX_MAP,
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from backend.core import migrations
from backend.core.config import settings
from backend.storage import layout

logger = logging.getLogger(__name__)


class ConcurrentTurnError(RuntimeError):
    """Raised when two turns attempt to update the same case's
    latest checkpoint simultaneously (ETag mismatch)."""


class AzureBlobCheckpointSaver(BaseCheckpointSaver):
    """
    LangGraph checkpointer backed by Azure Blob.

    Layout, with the namespace segment a subgraph's own state needs:
        checkpoints/{thread_id}/latest.json                    (parent)
        checkpoints/{thread_id}/history/{checkpoint_id}.json
        checkpoints/{thread_id}/ns/{ns}/latest.json            (subgraph)
        checkpoints/{thread_id}/ns/{ns}/history/{id}.json

    thread_id is read from config["configurable"]["thread_id"] and
    checkpoint_ns from config["configurable"]["checkpoint_ns"].

    Each put() writes:
      1. history/{checkpoint_id}.json (new blob, idempotent)
      2. latest.json (overwrite, conditional via If-Match ETag)

    The two writes constitute one logical save operation,
    consistent with the "one write per checkpoint" rule
    (one logical save event, not one physical blob write).
    """

    serde = JsonPlusSerializer()

    def __init__(
        self,
        container_client: ContainerClient,
        async_container_client: Optional[AsyncContainerClient] = None,
        async_container_factory: Optional[Callable[[], AsyncContainerClient]] = None,
    ) -> None:
        super().__init__()
        self._container = container_client
        self._async_container = async_container_client
        # ADR-0101 decision 2: the async methods use azure.storage.blob.aio. An aio client owns an aiohttp
        # session bound to the loop that made it, so one is built per running loop from this factory and closed
        # by `aclose` at shutdown. Without a factory or a client (the tests' in-memory container) the async
        # methods use the sync path.
        self._async_factory = async_container_factory
        self._aio: Optional[Tuple[asyncio.AbstractEventLoop, AsyncContainerClient, asyncio.Lock]] = None
        # Per-thread (case) lock to serialize put() on this process.
        # Cross-process safety relies on ETag conditional writes.
        self._lock = threading.Lock()

    # ──────────────────────── Path helpers ────────────────────────

    @staticmethod
    def _thread_id(config: dict) -> str:
        try:
            return config["configurable"]["thread_id"]
        except (KeyError, TypeError) as e:
            raise ValueError(
                "AzureBlobCheckpointSaver requires "
                "config['configurable']['thread_id'] (the case_id)."
            ) from e

    @staticmethod
    def _checkpoint_ns(config: dict) -> str:
        """The subgraph namespace, `""` for the parent graph.

        LangGraph assigns this automatically when a subgraph runs inside a
        parent node — `"define_phase:{task_id}"` for the Define subgraph — and
        it is the ONLY thing distinguishing the parent's checkpoint from its
        children's on a shared `thread_id`.
        """
        return (config.get("configurable") or {}).get("checkpoint_ns") or ""

    @classmethod
    def _prefix(cls, thread_id: str, checkpoint_ns: str) -> str:
        """The blob prefix for one (`thread_id`, `checkpoint_ns`) pair.

        ═══════════════════════════════════════════════════════════════════
        THE PARENT KEYS ON `thread_id`; A SUBGRAPH ADDS A NAMESPACE SEGMENT
        ═══════════════════════════════════════════════════════════════════
        The checkpointer sits on the parent and routes the subgraph's writes
        through it *distinguished by an auto-managed `checkpoint_ns`*. A path
        keyed on `thread_id` alone would have parent and subgraph write to one
        `latest.json` and read each other's state back.

        **The symptom is not an error.** The subgraph would load the parent's
        `messages` on top of its own and the conversation would double every
        turn, with every individual turn still looking correct.

        `""` — the parent — keeps `checkpoints/{thread_id}/…` **exactly**. The
        namespace is percent-encoded because it carries `:` and `|`, which are
        legal in a blob name but make the path unreadable and unsafe to split
        on.
        """
        if not checkpoint_ns:
            return layout.CHECKPOINT_THREAD.format(thread_id=thread_id)
        return layout.CHECKPOINT_NAMESPACED.format(thread_id=thread_id,
                                                   checkpoint_ns=quote(checkpoint_ns, safe=""))

    @classmethod
    def _latest_path(cls, thread_id: str, checkpoint_ns: str = "") -> str:
        return layout.CHECKPOINT_LATEST.format(prefix=cls._prefix(thread_id, checkpoint_ns))

    @classmethod
    def _history_path(cls, thread_id: str, checkpoint_id: str,
                      checkpoint_ns: str = "") -> str:
        return layout.CHECKPOINT_HISTORY.format(prefix=cls._prefix(thread_id, checkpoint_ns),
                                                checkpoint_id=checkpoint_id)

    @classmethod
    def _writes_prefix(cls, thread_id: str, checkpoint_id: str,
                       checkpoint_ns: str = "") -> str:
        """Where one checkpoint's PENDING WRITES live — one blob per task."""
        return layout.CHECKPOINT_WRITES.format(prefix=cls._prefix(thread_id, checkpoint_ns),
                                               checkpoint_id=checkpoint_id)

    def _blob(self, path: str) -> BlobClient:
        return self._container.get_blob_client(path)

    def _async_blob(self, path: str) -> AsyncBlobClient:
        if self._async_container is None:
            raise RuntimeError(
                "Async container client not configured. "
                "Pass async_container_client to constructor."
            )
        return self._async_container.get_blob_client(path)

    # ────────────────────── Serialization ──────────────────────

    def _envelope(
        self,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        parent_checkpoint_id: Optional[str],
    ) -> dict:
        ckpt_bytes = self.serde.dumps_typed(checkpoint)
        meta_bytes = self.serde.dumps_typed(metadata)
        return {
            "checkpoint_type": ckpt_bytes[0],
            # serde emits binary (msgpack); base64 for safe JSON storage
            "checkpoint_data": base64.b64encode(ckpt_bytes[1]).decode("ascii"),
            "metadata_type": meta_bytes[0],
            "metadata_data": base64.b64encode(meta_bytes[1]).decode("ascii"),
            "checkpoint_id": checkpoint["id"],
            "parent_checkpoint_id": parent_checkpoint_id,
        }

    def _restore(
        self, envelope: dict
    ) -> Tuple[Checkpoint, CheckpointMetadata, Optional[str]]:
        checkpoint = self.serde.loads_typed(
            (
                envelope["checkpoint_type"],
                base64.b64decode(envelope["checkpoint_data"]),
            )
        )
        metadata = self.serde.loads_typed(
            (
                envelope["metadata_type"],
                base64.b64decode(envelope["metadata_data"]),
            )
        )
        parent_id = envelope.get("parent_checkpoint_id")
        # ADR-0065 (T88): refused if a newer release wrote it; an older one is migrated, in
        # order, before the graph sees it. The stored blob is not rewritten.
        found = migrations.version_of(metadata)
        if found != migrations.current():
            checkpoint = {**checkpoint, "channel_values": migrations.migrate(
                checkpoint.get("channel_values") or {}, found, "checkpoint")}
        return checkpoint, metadata, parent_id

    # ──────────────────────── put (sync) ────────────────────────

    def put(
        self,
        config: dict,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict,
    ) -> dict:
        thread_id = self._thread_id(config)
        checkpoint_ns = self._checkpoint_ns(config)
        parent_id = (
            config.get("configurable", {}).get("checkpoint_id")
        )
        # ADR-0065 (T88): every checkpoint carries the state schema version it was written in.
        envelope = self._envelope(checkpoint, cast(CheckpointMetadata, migrations.stamp_metadata(metadata)),
                                  parent_id)
        body = json.dumps(envelope).encode("utf-8")

        with self._lock:
            # 1. Write history blob (idempotent — checkpoint id
            #    is content-derived and unique).
            history_blob = self._blob(
                self._history_path(thread_id, checkpoint["id"], checkpoint_ns)
            )
            try:
                history_blob.upload_blob(body, overwrite=False)
            except ResourceExistsError:
                # Already written — same checkpoint replay. Safe to ignore.
                logger.debug(
                    "Checkpoint %s already exists for %s, skipping history write",
                    checkpoint["id"],
                    thread_id,
                )

            # 2. Overwrite latest with ETag conditional. One retry on 412.
            self._update_latest(thread_id, body, retry=True,
                                checkpoint_ns=checkpoint_ns)

        # Return the config with the new checkpoint id for downstream resume
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_ns": checkpoint_ns,
                "checkpoint_id": checkpoint["id"],
            }
        }

    def _update_latest(self, thread_id: str, body: bytes, retry: bool,
                       checkpoint_ns: str = "") -> None:
        latest_blob = self._blob(self._latest_path(thread_id, checkpoint_ns))
        try:
            current = latest_blob.get_blob_properties()
            etag = current.etag
        except ResourceNotFoundError:
            etag = None

        try:
            if etag:
                latest_blob.upload_blob(
                    body,
                    overwrite=True,
                    if_match=etag,
                )
            else:
                # First checkpoint for this thread — no precondition
                latest_blob.upload_blob(body, overwrite=True)
        except ResourceModifiedError:
            if retry:
                logger.warning(
                    "ETag mismatch updating latest for %s, retrying once",
                    thread_id,
                )
                self._update_latest(thread_id, body, retry=False,
                                    checkpoint_ns=checkpoint_ns)
                return
            raise ConcurrentTurnError(
                f"Concurrent turn detected for case {thread_id} — "
                f"latest checkpoint was modified during this save."
            )

    # ─────────────────────── get_tuple (sync) ───────────────────────

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        thread_id = self._thread_id(config)
        checkpoint_ns = self._checkpoint_ns(config)
        checkpoint_id = (
            config.get("configurable", {}).get("checkpoint_id")
        )

        if checkpoint_id:
            path = self._history_path(thread_id, checkpoint_id, checkpoint_ns)
        else:
            path = self._latest_path(thread_id, checkpoint_ns)

        try:
            data = self._blob(path).download_blob().readall()
        except ResourceNotFoundError:
            return None

        envelope = json.loads(data.decode("utf-8"))
        checkpoint, metadata, parent_id = self._restore(envelope)
        pending = self._pending_writes(thread_id, checkpoint["id"], checkpoint_ns)

        return CheckpointTuple(
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_ns": checkpoint_ns,
                    "checkpoint_id": checkpoint["id"],
                }
            },
            checkpoint=checkpoint,
            metadata=metadata,
            pending_writes=pending,
            parent_config=(
                {
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": parent_id,
                    }
                }
                if parent_id
                else None
            ),
        )

    # ───────────────────────── list (sync) ─────────────────────────

    def list(
        self,
        config: Optional[dict],
        *,
        filter: Optional[dict] = None,
        before: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> Iterator[CheckpointTuple]:
        if config is None:
            return
        thread_id = self._thread_id(config)
        checkpoint_ns = self._checkpoint_ns(config)
        prefix = f"{self._prefix(thread_id, checkpoint_ns)}/history/"

        # List blobs and sort by name (checkpoint_ids are sortable
        # — LangGraph uses ULID-like ids by default).
        blob_names = sorted(
            (b.name for b in self._container.list_blobs(name_starts_with=prefix)),
            reverse=True,
        )

        before_id = (
            (before or {}).get("configurable", {}).get("checkpoint_id")
        )
        if before_id:
            blob_names = [
                n for n in blob_names if n.split("/")[-1].replace(".json", "") < before_id
            ]

        count = 0
        for name in blob_names:
            if limit is not None and count >= limit:
                break
            data = self._container.get_blob_client(name).download_blob().readall()
            envelope = json.loads(data.decode("utf-8"))
            ckpt, meta, parent_id = self._restore(envelope)
            yield CheckpointTuple(
                config={
                    "configurable": {
                        "thread_id": thread_id,
                        "checkpoint_ns": checkpoint_ns,
                        "checkpoint_id": ckpt["id"],
                    }
                },
                checkpoint=ckpt,
                metadata=meta,
                parent_config=(
                    {
                        "configurable": {
                            "thread_id": thread_id,
                            "checkpoint_ns": checkpoint_ns,
                            "checkpoint_id": parent_id,
                        }
                    }
                    if parent_id
                    else None
                ),
            )
            count += 1

    # ──────────────────────── put_writes ────────────────────────

    def put_writes(
        self,
        config: dict,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        """PENDING WRITES — what an `interrupt()` and its resume value ARE.

        LangGraph persists an `interrupt()` as an `__interrupt__` pending
        write, and the value `Command(resume=...)` delivers as a `__resume__`
        one; a saver that drops them leaves a pause — the Define report's (R6)
        — that cannot survive between two requests.

        Semantics are the reference saver's (`InMemorySaver.put_writes`,
        langgraph-checkpoint 4.1.0): a write is keyed (task, index); the
        special channels (`WRITES_IDX_MAP`: error, scheduled, interrupt,
        resume) take a fixed negative index and OVERWRITE, any other write
        keeps the first value stored at its index. One blob per task, under
        `{prefix}/writes/{checkpoint_id}/`.
        """
        checkpoint_id = (config.get("configurable") or {}).get("checkpoint_id")
        if not checkpoint_id:
            return None
        thread_id = self._thread_id(config)
        checkpoint_ns = self._checkpoint_ns(config)
        path = (self._writes_prefix(thread_id, checkpoint_id, checkpoint_ns)
                + quote(task_id, safe="") + ".json")
        blob = self._blob(path)
        with self._lock:
            try:
                envelope = json.loads(blob.download_blob().readall().decode("utf-8"))
            except ResourceNotFoundError:
                envelope = {"task_id": task_id, "task_path": task_path, "writes": {}}
            envelope[migrations.VERSION_KEY] = migrations.current()      # ADR-0065 (T88)
            stored = envelope.setdefault("writes", {})
            for idx, (channel, value) in enumerate(writes):
                inner = WRITES_IDX_MAP.get(channel, idx)
                if inner >= 0 and str(inner) in stored:
                    continue
                kind, data = self.serde.dumps_typed(value)
                stored[str(inner)] = {"channel": channel, "type": kind,
                                      "data": base64.b64encode(data).decode("ascii")}
            blob.upload_blob(json.dumps(envelope).encode("utf-8"), overwrite=True)
        return None

    def _pending_writes(self, thread_id: str, checkpoint_id: str,
                        checkpoint_ns: str = "") -> List[Tuple[str, str, Any]]:
        """`(task_id, channel, value)` for every write pending on a checkpoint."""
        prefix = self._writes_prefix(thread_id, checkpoint_id, checkpoint_ns)
        out: List[Tuple[str, str, Any]] = []
        for item in self._container.list_blobs(name_starts_with=prefix):
            try:
                raw = self._blob(item.name).download_blob().readall()
            except ResourceNotFoundError:
                continue
            envelope = json.loads(raw.decode("utf-8"))
            found = migrations.version_of(envelope)        # ADR-0065 (T88)
            for write in (envelope.get("writes") or {}).values():
                value = self.serde.loads_typed((write["type"], base64.b64decode(write["data"])))
                if found != migrations.current():
                    value = migrations.migrate({write["channel"]: value}, found,
                                               "pending write").get(write["channel"], value)
                out.append((envelope.get("task_id", ""), write["channel"], value))
        return out

    # ───────────────── Async variants — ADR-0101 decision 2 ─────────────────
    #
    # The same blob semantics as the sync methods above, on azure.storage.blob.aio, so a write never stops the
    # event loop: the history blob written once (ResourceExistsError ignored), `latest.json` by ETag with one
    # retry, pending writes keyed as the reference saver keys them. Without an async client (the tests'
    # in-memory container) each delegates to its sync twin.

    def _aio_parts(self) -> Optional[Tuple[AsyncContainerClient, asyncio.Lock]]:
        """The async container and the write lock for the running loop — built once per loop."""
        loop = asyncio.get_running_loop()
        if self._aio is not None and self._aio[0] is loop:
            return self._aio[1], self._aio[2]
        if self._async_container is not None:
            container = self._async_container
        elif self._async_factory is not None:
            container = self._async_factory()
        else:
            return None
        self._aio = (loop, container, asyncio.Lock())
        return container, self._aio[2]

    async def aclose(self) -> None:
        """Close the async client of the running loop (the shutdown hook). Idempotent."""
        if self._aio is None or self._async_container is not None:
            return
        _loop, container, _lock = self._aio
        self._aio = None
        await container.close()

    async def aput(
        self,
        config: dict,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict,
    ) -> Any:
        parts = self._aio_parts()
        if parts is None:
            return self.put(config, checkpoint, metadata, new_versions)
        container, lock = parts
        thread_id = self._thread_id(config)
        checkpoint_ns = self._checkpoint_ns(config)
        parent_id = config.get("configurable", {}).get("checkpoint_id")
        envelope = self._envelope(checkpoint, cast(CheckpointMetadata, migrations.stamp_metadata(metadata)),
                                  parent_id)
        body = json.dumps(envelope).encode("utf-8")
        async with lock:
            try:
                await container.get_blob_client(
                    self._history_path(thread_id, checkpoint["id"], checkpoint_ns)).upload_blob(body, overwrite=False)
            except ResourceExistsError:
                logger.debug("Checkpoint %s already exists for %s, skipping history write", checkpoint["id"], thread_id)
            await self._aupdate_latest(container, thread_id, body, retry=True, checkpoint_ns=checkpoint_ns)
        return {"configurable": {"thread_id": thread_id, "checkpoint_ns": checkpoint_ns,
                                 "checkpoint_id": checkpoint["id"]}}

    async def _aupdate_latest(self, container: AsyncContainerClient, thread_id: str, body: bytes, retry: bool,
                              checkpoint_ns: str = "") -> None:
        latest_blob = container.get_blob_client(self._latest_path(thread_id, checkpoint_ns))
        try:
            etag = (await latest_blob.get_blob_properties()).etag
        except ResourceNotFoundError:
            etag = None
        try:
            if etag:
                await latest_blob.upload_blob(body, overwrite=True, etag=etag,
                                              match_condition=MatchConditions.IfNotModified)
            else:
                await latest_blob.upload_blob(body, overwrite=True)
        except ResourceModifiedError:
            if retry:
                logger.warning("ETag mismatch updating latest for %s, retrying once", thread_id)
                await self._aupdate_latest(container, thread_id, body, retry=False, checkpoint_ns=checkpoint_ns)
                return
            raise ConcurrentTurnError(
                f"Concurrent turn detected for case {thread_id} — "
                f"latest checkpoint was modified during this save."
            )

    async def aget_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        parts = self._aio_parts()
        if parts is None:
            return self.get_tuple(config)
        container, _lock = parts
        thread_id = self._thread_id(config)
        checkpoint_ns = self._checkpoint_ns(config)
        checkpoint_id = config.get("configurable", {}).get("checkpoint_id")
        path = (self._history_path(thread_id, checkpoint_id, checkpoint_ns) if checkpoint_id
                else self._latest_path(thread_id, checkpoint_ns))
        try:
            data = await (await container.get_blob_client(path).download_blob()).readall()
        except ResourceNotFoundError:
            return None
        checkpoint, metadata, parent_id = self._restore(json.loads(data.decode("utf-8")))
        pending = await self._apending_writes(container, thread_id, checkpoint["id"], checkpoint_ns)
        return self._tuple(thread_id, checkpoint_ns, checkpoint, metadata, parent_id, pending)

    def _tuple(self, thread_id: str, checkpoint_ns: str, checkpoint: Checkpoint, metadata: CheckpointMetadata,
               parent_id: Optional[str], pending: Optional[List[Tuple[str, str, Any]]]) -> CheckpointTuple:
        def cfg(cid: Optional[str]) -> Any:
            return {"configurable": {"thread_id": thread_id, "checkpoint_ns": checkpoint_ns, "checkpoint_id": cid}}
        return CheckpointTuple(config=cfg(checkpoint["id"]), checkpoint=checkpoint, metadata=metadata,
                               pending_writes=pending, parent_config=cfg(parent_id) if parent_id else None)

    async def _apending_writes(self, container: AsyncContainerClient, thread_id: str, checkpoint_id: str,
                               checkpoint_ns: str = "") -> List[Tuple[str, str, Any]]:
        prefix = self._writes_prefix(thread_id, checkpoint_id, checkpoint_ns)
        out: List[Tuple[str, str, Any]] = []
        async for item in container.list_blobs(name_starts_with=prefix):
            try:
                raw = await (await container.get_blob_client(item.name).download_blob()).readall()
            except ResourceNotFoundError:
                continue
            envelope = json.loads(raw.decode("utf-8"))
            found = migrations.version_of(envelope)
            for write in (envelope.get("writes") or {}).values():
                value = self.serde.loads_typed((write["type"], base64.b64decode(write["data"])))
                if found != migrations.current():
                    value = migrations.migrate({write["channel"]: value}, found,
                                               "pending write").get(write["channel"], value)
                out.append((envelope.get("task_id", ""), write["channel"], value))
        return out

    async def alist(
        self,
        config: Optional[dict],
        *,
        filter: Optional[dict] = None,
        before: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        parts = self._aio_parts()
        if parts is None:
            for tup in self.list(config, filter=filter, before=before, limit=limit):
                yield tup
            return
        if config is None:
            return
        container, _lock = parts
        thread_id = self._thread_id(config)
        checkpoint_ns = self._checkpoint_ns(config)
        prefix = f"{self._prefix(thread_id, checkpoint_ns)}/history/"
        names = sorted([b.name async for b in container.list_blobs(name_starts_with=prefix)], reverse=True)
        before_id = (before or {}).get("configurable", {}).get("checkpoint_id")
        if before_id:
            names = [n for n in names if n.split("/")[-1].replace(".json", "") < before_id]
        for count, name in enumerate(names):
            if limit is not None and count >= limit:
                break
            data = await (await container.get_blob_client(name).download_blob()).readall()
            ckpt, meta, parent_id = self._restore(json.loads(data.decode("utf-8")))
            yield self._tuple(thread_id, checkpoint_ns, ckpt, meta, parent_id, None)

    async def aput_writes(
        self,
        config: dict,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        parts = self._aio_parts()
        if parts is None:
            return self.put_writes(config, writes, task_id, task_path)
        checkpoint_id = (config.get("configurable") or {}).get("checkpoint_id")
        if not checkpoint_id:
            return None
        container, lock = parts
        thread_id = self._thread_id(config)
        checkpoint_ns = self._checkpoint_ns(config)
        blob = container.get_blob_client(self._writes_prefix(thread_id, checkpoint_id, checkpoint_ns)
                                         + quote(task_id, safe="") + ".json")
        async with lock:
            try:
                envelope = json.loads((await (await blob.download_blob()).readall()).decode("utf-8"))
            except ResourceNotFoundError:
                envelope = {"task_id": task_id, "task_path": task_path, "writes": {}}
            envelope[migrations.VERSION_KEY] = migrations.current()
            stored = envelope.setdefault("writes", {})
            for idx, (channel, value) in enumerate(writes):
                inner = WRITES_IDX_MAP.get(channel, idx)
                if inner >= 0 and str(inner) in stored:
                    continue
                kind, data = self.serde.dumps_typed(value)
                stored[str(inner)] = {"channel": channel, "type": kind,
                                      "data": base64.b64encode(data).decode("ascii")}
            await blob.upload_blob(json.dumps(envelope).encode("utf-8"), overwrite=True)
        return None


# ─────────────────── Module-level factory ───────────────────

_singleton_lock = threading.Lock()
_singleton: Optional[AzureBlobCheckpointSaver] = None


def get_checkpointer() -> AzureBlobCheckpointSaver:
    """
    Singleton accessor — single shared instance per process, lazily
    initialised.
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
                "AzureBlobCheckpointSaver requires "
                "AZURE_BLOB_CONNECTION_STRING and "
                "AZURE_BLOB_CONTAINER_IMPROVE in settings."
            )

        container = ContainerClient.from_connection_string(conn, container_name)
        # ADR-0101: the async client is built per running loop, from this factory (see `_aio_parts`).
        _singleton = AzureBlobCheckpointSaver(
            container, async_container_factory=lambda: AsyncContainerClient.from_connection_string(
                conn, container_name))
        logger.info(
            "AzureBlobCheckpointSaver initialised on container=%s",
            container_name,
        )
        return _singleton
