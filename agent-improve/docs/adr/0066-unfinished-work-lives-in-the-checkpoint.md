# ADR-0066 — Unfinished phase work lives in the checkpoint only

Status: ACCEPTED (founder, 2026-09-28)
Requirements: T13 (case blob written only at gate approval), W11 (nothing typed is lost), T17 (retention never removes a paused thread)
Refines: ADR-0038 (the record), ADR-0063 (one graph)

## Context

Unfinished work means the conversation and captured values of a phase before its gate is approved.
LangGraph already saves it in the checkpoint after every node, under `thread_id` = case id. The
`/ask` route also copies it into the case blob on every turn, and a reload reads that copy.

That gives two copies of the same state, with nothing to stop them diverging. A replay or rollback
moves the checkpoint and leaves the blob behind (ARCHITECTURE.md §2.5 Checkpoints and persistence:
"Rolling back a checkpoint does not roll back Store, Blob or index writes"). It also breaks §2.5's
rule "Three stores, three jobs" and T13.

LangGraph documents the checkpoint as the thread-scoped home for "conversation continuity,
human-in-the-loop … and fault tolerance", and the Store as cross-thread data
(https://docs.langchain.com/oss/python/langgraph/persistence).

## Decision

1. The checkpoint is the only home of unfinished work. The `/ask` route stops writing the case blob.
2. A reload, and any screen that shows the current phase's progress, reads the thread state through
   the compiled graph (`get_state` with the case's config, including subgraph state). No route
   reads unfinished work from the blob.
3. The case blob is written at three moments only: case creation, upload, and gate approval (once,
   the record the output mapper produced). The registry and case list keep reading the blob for case
   metadata.
4. The Store holds approved phase records and cross-phase data only.
5. Retention: no checkpoint of an open case is deleted. This extends T17 from paused threads to all
   open cases. Retention after a case closes is a later decision and is not part of this ADR.

## Consequences

- One copy of unfinished work, so the copies can no longer disagree. T13 becomes provable.
- W11 still holds: the checkpoint is written after every node, and the writes are conditional on
  the blob's ETag.
- The schema version from ADR-0065 travels in checkpoint metadata, so old unfinished work stays
  loadable across releases.
- The checkpoint becomes business-critical, so its storage needs the same backup as the case blob.
- §2.5's table changes: the case blob row's "Written" and "Read by" cells.

## Rejected

- **The Store's case record for unfinished work.** It keeps two copies (checkpoint and Store),
  reverses today's copy direction and uses the Store for thread-scoped data, against its documented role.
- **Keep the per-turn blob write.** It leaves T13 violated and the two-copy risk open.

## Verification

- A test proves `/ask` writes no case blob.
- An API test sends turns, simulates a reload, and sees every confirmed value and the conversation.
- An approval writes the blob exactly once.
- The existing development cases still reload.
