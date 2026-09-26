# 0018. A custom Azure Blob checkpointer with conditional writes

**Status:** PROPOSED (architecture sort, 2026-09-26)

**Source:** [ARCHITECTURE.md](../../ARCHITECTURE.md) §8, §10, §16

## Context

No maintained LangGraph saver writes to Azure Blob, and two turns on one case could overwrite each other.

## Decision

`AzureBlobCheckpointSaver` stores checkpoints and pending writes under the thread. Writes are conditional on the blob ETag; a losing writer retries and then raises.

## Consequences

We own the saver's correctness, including pending writes (fixed at part 6). Concurrency is detected, not prevented; a single writer per case is still unbuilt (T-list T11).
