# ADR-0087: The approval node writes both records — the Store's and the case's — has no error handler, and LangGraph's retry completes it

Status: ACCEPTED (founder, 2026-10-19, amended after the spike of 2026-10-17; drafted by Claude Code from the founder's
choice of option A for DEF-170)
Requirements: T23 (both or neither), T29 (every node with an external write undoes it — amended here for this one
node), T13 (the case blob is written at approval); DEF-170 (G-178)
Refines: ADR-0063 "One compiled runtime graph that enters at the current phase", decision 3 (the approval node writes
the case record too; the route writes none)
Depends on: ADR-0066 "Unfinished phase work lives in the checkpoint only", the T29 error handler
(`core/graph.py::degraded_handler`, `_undo_gate_write`)

## Context

An approval (`POST /gate/decision`) resumed the paused Define subgraph; in the phase node the output mapper wrote the
Store record, and then the route, outside the graph, wrote the case record. If the case write failed, the Store held the
approval, the graph had moved to Measure and the case record held neither (G-178). The spike of 2026-10-17 (branch
`spike/adr-0087-approval-writes-both`) measured LangGraph's behaviour through the real graph:

| Spike | What happened |
|---|---|
| Q1 — the node's T29 handler answers the failure | 503, but the report no longer awaits a decision; a second approval is refused (409) |
| Q2 — a handler that re-raises instead | the same: the handler's presence uses up the pending decision |
| Q3 — no handler | the task stays pending with its error and its interrupt; LangGraph's retry re-runs it and the approval completes |
| T1–T5 — both writes in the node, undone and re-raised | each failure point leaves neither record and the decision pending; a second approval, or a restarted process, completes with one record each |

So the decision survives a failure only when the node that holds the report's pause has no error handler. Removing the
handler from the Define phase node altogether turned every coaching-turn failure into a 500 instead of the degraded reply.

## Decision

1. **The approval runs in its own node, `define_approval`,** a second parent node around the same Define subgraph. The
   gate path enters it: a submission (`POST /gate`) is routed there, so the report's pause belongs to it, and the
   decision (`POST /gate/decision`) resumes it. Coaching turns (`POST /ask`) enter `define_phase`, which keeps its T29
   handler.
2. **It writes both records:** the Store record (the output mapper), then the case record (`blob.write_phase_gate`, with
   the document from the Store and the evidence from the subgraph's own state), then the move to Measure. The route writes
   neither.
3. **It has no error handler and a LangGraph retry policy.** On any failure it undoes both writes in place — the Store
   record as T29 does, the case record restored to what it held before when it now holds this run's approval — and
   re-raises; LangGraph re-runs it. When the retries are exhausted the task stays pending with its pause: the report still
   awaits the decision, and the route answers in plain words that the approval did not go through, nothing is lost, and
   to try again. A second approval completes it.
4. **Both writes are idempotent** — a node is re-run from its start on a retry or a resume
   (https://docs.langchain.com/oss/python/langgraph/interrupts): the Store record is an upsert by its key; the case record
   merges the approved document into the phase record and stamps the approval on the transition only. Never a second
   record.
5. A second approval after one that completed still answers 409 and writes nothing (T15, T23).
6. **T29 is amended for this node:** "every node with an external write has an error handler that undoes it and routes
   to a degraded answer — except the approval node, which undoes its writes in place and re-raises, because a handler on
   the node that holds the report's pause uses up the pending decision (ADR-0087)".

## Tests

1. Failure after the Store write: the Store record removed, the case record unwritten, the readable answer, the report
   still awaits the decision, a second approval completes with one record each.
2. Failure at the case write: the same.
3. Failure after the case write (G-178): the case record restored, the Store record removed, still awaiting; the second
   approval completes.
4. A transient failure the retry absorbs: one approval, one record each.
5. **Written once (mandatory):** however many times the node runs, one Store record and one approved case record, the
   approval stamped once.
6. A killed process between the two writes, then a restart: the decision still pending; the approval completes; one
   record each; the phase is Measure.
7. Coaching turns keep the degraded reply on a failure (T29).

## Consequences

- T23 holds at every failure point of an approval; the lead never meets a dead end.
- The parent graph gains one node (`define_approval`); ARCHITECTURE.md's graph section owes it (docs after Define).
- Size: M.

## Rejected

- **Keep the route's write and, on its failure, rewind the graph to the paused checkpoint (option B).** Fragile (a rewind
  outside the node that wrote) and two writers of one approval.
- **A separate node after the phase node.** The phase node would already have used up the pause: a failed approval could
  not be approved again.
- **No handler on the Define phase node at all.** Every coaching-turn failure would become a 500 instead of T29's reply.
