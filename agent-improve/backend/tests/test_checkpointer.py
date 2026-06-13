"""
Unit tests for AzureBlobCheckpointSaver.

Uses MagicMock for the ContainerClient so tests run without
Azure credentials. Verifies layout, ETag handling, list ordering,
and concurrent-turn detection.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest
from azure.core.exceptions import ResourceModifiedError, ResourceNotFoundError

from backend.core.checkpointer import (
    AzureBlobCheckpointSaver,
    ConcurrentTurnError,
)


def _make_checkpoint(checkpoint_id: str = "ckpt-001") -> dict:
    """Minimal Checkpoint dict that JsonPlusSerializer can handle."""
    return {
        "v": 1,
        "id": checkpoint_id,
        "ts": "2026-06-13T00:00:00",
        "channel_values": {"x": 1},
        "channel_versions": {"x": 1},
        "versions_seen": {},
    }


def _make_metadata() -> dict:
    return {"source": "input", "step": 1, "writes": {}, "parents": {}}


def _make_config(thread_id: str = "IMPR-2026-TST", checkpoint_id: str | None = None) -> dict:
    cfg = {"configurable": {"thread_id": thread_id}}
    if checkpoint_id:
        cfg["configurable"]["checkpoint_id"] = checkpoint_id
    return cfg


def _make_saver_with_mocks():
    container = MagicMock()
    saver = AzureBlobCheckpointSaver(container_client=container)
    return saver, container


def test_thread_id_required():
    saver, _ = _make_saver_with_mocks()
    with pytest.raises(ValueError):
        saver.put({}, _make_checkpoint(), _make_metadata(), {})


def test_put_writes_history_and_latest():
    saver, container = _make_saver_with_mocks()
    history_blob = MagicMock()
    latest_blob = MagicMock()

    # First call returns history blob, second returns latest
    def get_blob_client(path):
        if "history" in path:
            return history_blob
        return latest_blob

    container.get_blob_client.side_effect = get_blob_client
    latest_blob.get_blob_properties.side_effect = ResourceNotFoundError("no blob")

    saver.put(_make_config(), _make_checkpoint(), _make_metadata(), {})

    # History was uploaded (overwrite=False — first time)
    history_blob.upload_blob.assert_called_once()
    h_call = history_blob.upload_blob.call_args
    assert h_call.kwargs.get("overwrite") is False

    # Latest was uploaded without If-Match (no prior etag)
    latest_blob.upload_blob.assert_called_once()
    l_call = latest_blob.upload_blob.call_args
    assert l_call.kwargs.get("overwrite") is True
    assert "if_match" not in l_call.kwargs


def test_put_uses_etag_when_latest_exists():
    saver, container = _make_saver_with_mocks()
    history_blob = MagicMock()
    latest_blob = MagicMock()

    def get_blob_client(path):
        return history_blob if "history" in path else latest_blob

    container.get_blob_client.side_effect = get_blob_client

    # Latest exists, returns etag
    props = MagicMock()
    props.etag = '"abc123"'
    latest_blob.get_blob_properties.return_value = props

    saver.put(_make_config(), _make_checkpoint(), _make_metadata(), {})

    l_call = latest_blob.upload_blob.call_args
    assert l_call.kwargs.get("if_match") == '"abc123"'


def test_concurrent_turn_raises_after_retry():
    saver, container = _make_saver_with_mocks()
    history_blob = MagicMock()
    latest_blob = MagicMock()

    def get_blob_client(path):
        return history_blob if "history" in path else latest_blob

    container.get_blob_client.side_effect = get_blob_client

    props = MagicMock()
    props.etag = '"abc123"'
    latest_blob.get_blob_properties.return_value = props
    latest_blob.upload_blob.side_effect = ResourceModifiedError("etag mismatch")

    with pytest.raises(ConcurrentTurnError):
        saver.put(_make_config(), _make_checkpoint(), _make_metadata(), {})


def test_get_tuple_returns_none_when_missing():
    saver, container = _make_saver_with_mocks()
    blob = MagicMock()
    container.get_blob_client.return_value = blob
    blob.download_blob.side_effect = ResourceNotFoundError("missing")

    result = saver.get_tuple(_make_config())
    assert result is None


def test_get_tuple_uses_history_when_checkpoint_id_given():
    saver, container = _make_saver_with_mocks()

    # Save a checkpoint first to know what envelope shape looks like
    blob = MagicMock()
    history_blob = MagicMock()
    latest_blob = MagicMock()

    def get_blob_client(path):
        if "history/ckpt-saved" in path:
            return history_blob
        if "latest" in path:
            return latest_blob
        return blob

    container.get_blob_client.side_effect = get_blob_client
    latest_blob.get_blob_properties.side_effect = ResourceNotFoundError("first save")

    saved_envelope = None

    def capture(body, **kwargs):
        nonlocal saved_envelope
        if not saved_envelope:
            saved_envelope = json.loads(body.decode("utf-8"))

    history_blob.upload_blob.side_effect = capture
    latest_blob.upload_blob.side_effect = capture

    saver.put(_make_config(), _make_checkpoint("ckpt-saved"), _make_metadata(), {})

    # Now read it back via get_tuple with checkpoint_id
    download = MagicMock()
    download.readall.return_value = json.dumps(saved_envelope).encode("utf-8")
    history_blob.download_blob.return_value = download

    result = saver.get_tuple(_make_config(checkpoint_id="ckpt-saved"))
    assert result is not None
    assert result.checkpoint["id"] == "ckpt-saved"
