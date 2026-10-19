# ADR-0101: The coach's inner agent is not checkpointed, and the Blob checkpointer writes without blocking the turn

Status: ACCEPTED (founder, 2026-10-19; drafted by Claude Code from the founder's ruling of 2026-10-17, item 7)
Requirements: R13 "Turn time", T88 "Every state change ships a tested migration"; defect G-232 (owner G-220 "Checkpoint
weight", feature DEF-219)
Refines: ADR-0080 "One turn deadline and request timeouts" (what a turn spends inside its 45 s)
Depends on: ADR-0066 "Unfinished phase work lives in the checkpoint only", ADR-0063 "One compiled runtime graph that
enters at the current phase"

## Context (verified 2026-10-17 on the checkpoints of IMPR-HOWTO-37FBF8)

- The how-to eval's SIPOC question ran past ADR-0080's deadline. Its last checkpoint was written at 40.6 s; the turn
  before it on the same case took 19 s. The difference was storage, not the model: each checkpoint step with no model
  call took 1.3–1.9 s instead of about 0.3 s, though this turn's checkpoints were the smaller ones.
- A turn makes about 70 Blob round trips, one after another. That minute each took about 360 ms instead of 60 ms.
- **The writes block the turn.** `core/checkpointer.py`'s `aput` and `aput_writes` call the synchronous Blob client
  inside the event loop ("For now delegate to sync … Step 6 may replace with truly async azure-storage-blob.aio
  calls"). A `put` is three round trips (history upload, properties read, `latest.json` upload); a `put_writes` is a
  download and an upload per task. While one runs, nothing else in the process moves.
- **The coach's inner agent is checkpointed.** `create_agent` in `phases/nodes_common.py` is built without a
  `checkpointer` setting, so it inherits the parent's: its ~10 internal steps per turn (middleware, model call, tool
  calls, structured reply) are each written to Blob in their own `|executor:` namespace — about 40 % of a turn's
  checkpoint writes. Nothing reads them back: the executor node returns its product to the phase subgraph, whose own
  checkpoints carry it.
- **The installed framework (versions as pinned in `agent-improve/requirements.txt`), read from its source:**
  `create_agent(..., checkpointer=...)` accepts `None | bool | BaseCheckpointSaver`; `False` "disables
  checkpointing, even if the parent graph has a checkpointer"; `None` inherits it. LangGraph's subgraph guide says
  the same (https://docs.langchain.com/oss/python/langgraph/use-subgraphs).
- **No interrupt lives inside the agent.** The contradiction middleware detects and does not pause; its pause is a
  node of its own, DEF-040 (`middleware/contradiction.py`). A turn that crashes inside the agent is abandoned and
  answered by ADR-0080's deadline reply; it is never resumed mid-agent.
- The Store (`core/store.py`) already writes through `azure.storage.blob.aio`, with its session lifecycle handled.

## Decision

1. **The coach's inner agent is compiled with `checkpointer=False`** (`create_agent(..., checkpointer=False)` in
   `phases/nodes_common.py`). The phase subgraph and the parent graph keep their checkpoints unchanged: what a turn
   produced, the pause at `gate_review`, and unfinished work (ADR-0066) are all in those.
2. **The Blob checkpointer's async methods are truly async.** `aput`, `aput_writes`, `aget_tuple` and `alist` use
   `azure.storage.blob.aio`, with the session handling the Store already uses. Each method's blob semantics stay as
   they are: the history blob written once, `latest.json` by ETag with one retry, pending writes keyed as the
   reference saver keys them. The synchronous methods stay for scripts and tests.
3. **Storage time is measured per turn.** The run records carry each turn's storage seconds and calls by kind
   (checkpoint, Store, case file), the measure G-232 asked for (in place since 2026-10-17). The proof of this ADR is
   read from them.
4. **No state change.** No field and no record shape changes; no schema version.

## Consequences

- A turn writes about 40 % fewer checkpoints, and no write stops the event loop: a slow Blob minute slows the
  storage, not the model calls running beside it.
- `|executor:` namespaces stop growing in new turns; old ones stay where they are, unread (deleting them is G-220's
  analysis, not this ADR).
- If DEF-040 ever moves the contradiction pause back inside the agent, decision 1 has to be revisited: an interrupt
  needs a checkpointer.
- ARCHITECTURE.md's persistence section gains one line on the inner agent; owed with the docs after Define.
- Size: M — one argument, four async methods and their tests, one live comparison.

## Rejected

- **Leave the agent checkpointed and only make the writes async.** Keeps ~40 % of the writes, each still a round
  trip a turn waits for in the end.
- **Raise the turn deadline.** Hides the cost; R13 is 45 s.
- **Write checkpoints in a background task the turn does not wait for.** A crash would lose a finished turn's state
  (ADR-0066), and two turns could reorder their `latest.json` writes.
- **A different checkpointer now (PostgreSQL).** Planned before production (rule §1.7); not a fix for the pilot.

## Verification

1. A test: one coaching turn through the real graph writes no checkpoint in an `|executor:` namespace, and the
   parent's and the phase subgraph's checkpoints are the same as before (the turn's product, the pause at
   `gate_review`, a reload).
2. A test: the async methods round-trip a checkpoint and its pending writes, the `latest.json` ETag retry included,
   against an async in-memory container — the same assertions as the sync saver's tests.
3. Live: the how-to eval (six cases) and one run-through, compared with the records before the change — storage
   seconds per turn and checkpoint calls per turn fall; no turn over 45 s.
