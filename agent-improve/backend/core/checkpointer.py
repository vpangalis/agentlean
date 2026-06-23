"""
Azure Blob checkpointer for Agent Improve.

Implements LangGraph's BaseCheckpointSaver interface backed by
Azure Blob Storage. Per CLAUDE.md §1.7 and §8.1, in-flight
graph state lives in:

    checkpoints/{thread_id}/latest.json
    checkpoints/{thread_id}/history/{checkpoint_id}.json

where thread_id = case_id for Agent Improve.

Each put() call writes one history blob AND overwrites latest.json.
Both writes are part of the same logical operation; the latest.json
overwrite uses an ETag conditional If-Match to detect concurrent
turns (raises ConcurrentTurnError on conflict).

Per CLAUDE.md §2 this is the designated file for the
AzureBlobCheckpointSaver class. The factory function
get_checkpointer() is module-level (no class wrapping the
singleton).

Compatibility note (deviation from the original spec, applied with
approval against the installed langgraph-checkpoint 4.1.0):
  - JsonPlusSerializer.dumps_typed() returns msgpack BINARY, not
    utf-8 text. The envelope therefore base64-encodes the serde
    bytes for safe JSON storage and base64-decodes them on restore.
  - put_writes()/aput_writes() take the 4.1.0 `task_path` argument.
  - The factory reads the existing settings names
    AZURE_BLOB_CONNECTION_STRING and AZURE_BLOB_CONTAINER_IMPROVE
    (matching storage/blob.py), not invented names.
"""

from __future__ import annotations

import base64
import json
import logging
import threading
from typing import Any, AsyncIterator, Iterator, Optional, Sequence, Tuple

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
    BaseCheckpointSaver,
    Checkpoint,
    CheckpointMetadata,
    CheckpointTuple,
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from backend.core.config import settings

logger = logging.getLogger(__name__)


class ConcurrentTurnError(RuntimeError):
    """Raised when two turns attempt to update the same case's
    latest checkpoint simultaneously (ETag mismatch)."""


class AzureBlobCheckpointSaver(BaseCheckpointSaver):
    """
    LangGraph checkpointer backed by Azure Blob.

    Layout per CLAUDE.md §1.7:
        checkpoints/{thread_id}/latest.json
        checkpoints/{thread_id}/history/{checkpoint_id}.json

    thread_id is read from config["configurable"]["thread_id"].

    Each put() writes:
      1. history/{checkpoint_id}.json (new blob, idempotent)
      2. latest.json (overwrite, conditional via If-Match ETag)

    The two writes constitute one logical save operation,
    consistent with the "one write per checkpoint" rule in §1.7
    (interpreted as: one logical save event, not one physical
    blob write).
    """

    serde = JsonPlusSerializer()

    def __init__(
        self,
        container_client: ContainerClient,
        async_container_client: Optional[AsyncContainerClient] = None,
    ) -> None:
        super().__init__()
        self._container = container_client
        self._async_container = async_container_client
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
    def _latest_path(thread_id: str) -> str:
        return f"checkpoints/{thread_id}/latest.json"

    @staticmethod
    def _history_path(thread_id: str, checkpoint_id: str) -> str:
        return f"checkpoints/{thread_id}/history/{checkpoint_id}.json"

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
        parent_id = (
            config.get("configurable", {}).get("checkpoint_id")
        )
        envelope = self._envelope(checkpoint, metadata, parent_id)
        body = json.dumps(envelope).encode("utf-8")

        with self._lock:
            # 1. Write history blob (idempotent — checkpoint id
            #    is content-derived and unique).
            history_blob = self._blob(
                self._history_path(thread_id, checkpoint["id"])
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
            self._update_latest(thread_id, body, retry=True)

        # Return the config with the new checkpoint id for downstream resume
        return {
            "configurable": {
                "thread_id": thread_id,
                "checkpoint_id": checkpoint["id"],
            }
        }

    def _update_latest(self, thread_id: str, body: bytes, retry: bool) -> None:
        latest_blob = self._blob(self._latest_path(thread_id))
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
                self._update_latest(thread_id, body, retry=False)
                return
            raise ConcurrentTurnError(
                f"Concurrent turn detected for case {thread_id} — "
                f"latest checkpoint was modified during this save."
            )

    # ─────────────────────── get_tuple (sync) ───────────────────────

    def get_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        thread_id = self._thread_id(config)
        checkpoint_id = (
            config.get("configurable", {}).get("checkpoint_id")
        )

        if checkpoint_id:
            path = self._history_path(thread_id, checkpoint_id)
        else:
            path = self._latest_path(thread_id)

        try:
            data = self._blob(path).download_blob().readall()
        except ResourceNotFoundError:
            return None

        envelope = json.loads(data.decode("utf-8"))
        checkpoint, metadata, parent_id = self._restore(envelope)

        return CheckpointTuple(
            config={
                "configurable": {
                    "thread_id": thread_id,
                    "checkpoint_id": checkpoint["id"],
                }
            },
            checkpoint=checkpoint,
            metadata=metadata,
            parent_config=(
                {
                    "configurable": {
                        "thread_id": thread_id,
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
            return iter([])
        thread_id = self._thread_id(config)
        prefix = f"checkpoints/{thread_id}/history/"

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
                        "checkpoint_id": ckpt["id"],
                    }
                },
                checkpoint=ckpt,
                metadata=meta,
                parent_config=(
                    {
                        "configurable": {
                            "thread_id": thread_id,
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
        # Intermediate node writes — Agent Improve treats checkpoint
        # saves as the only durable boundary, so we no-op here.
        # (LangGraph still calls this; it's required by the interface.)
        return None

    # ───────────────── Async variants (thin wrappers) ─────────────────

    async def aput(
        self,
        config: dict,
        checkpoint: Checkpoint,
        metadata: CheckpointMetadata,
        new_versions: dict,
    ) -> dict:
        # For now delegate to sync — Azure blob sync calls are
        # fast enough at low concurrency. Step 6 may replace with
        # truly async azure-storage-blob.aio calls.
        return self.put(config, checkpoint, metadata, new_versions)

    async def aget_tuple(self, config: dict) -> Optional[CheckpointTuple]:
        return self.get_tuple(config)

    async def alist(
        self,
        config: Optional[dict],
        *,
        filter: Optional[dict] = None,
        before: Optional[dict] = None,
        limit: Optional[int] = None,
    ) -> AsyncIterator[CheckpointTuple]:
        for tup in self.list(config, filter=filter, before=before, limit=limit):
            yield tup

    async def aput_writes(
        self,
        config: dict,
        writes: Sequence[Tuple[str, Any]],
        task_id: str,
        task_path: str = "",
    ) -> None:
        return None


# ─────────────────── Module-level factory ───────────────────

_singleton_lock = threading.Lock()
_singleton: Optional[AzureBlobCheckpointSaver] = None


def get_checkpointer() -> AzureBlobCheckpointSaver:
    """
    Singleton accessor. Mirrors the ImproveBlobClient pattern in
    storage/blob.py — single shared instance per process, lazily
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
        async_container = AsyncContainerClient.from_connection_string(
            conn, container_name
        )

        _singleton = AzureBlobCheckpointSaver(container, async_container)
        logger.info(
            "AzureBlobCheckpointSaver initialised on container=%s",
            container_name,
        )
        return _singleton
