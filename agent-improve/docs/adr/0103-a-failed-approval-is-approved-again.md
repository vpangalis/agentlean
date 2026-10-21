# ADR-0103: The approval node writes both records, has no error handler and no retry policy; a failed approval is approved again

Status: ACCEPTED (founder, 2026-10-21, option B; drafted by Claude Code from the ruling)
Requirements: T23 (both or neither), T29 (amended for the approval node by ADR-0087); DEF-170 (G-178, G-239)
Supersedes: ADR-0087's title, decision 3 and test 4 (partial; ADR-0087's decisions 1, 2, 4, 5 and 6 stand)

## Context

ADR-0087 decision 3 gave `define_approval` a LangGraph retry policy, on the premise that a retry re-runs the node and
its Define subgraph resumes from its checkpoint. Building it (2026-10-20) showed the premise does not hold:

- On a retry, the node re-calls the Define subgraph and it starts fresh as a coaching turn (planner
  `entry=decision turn_count=0`, `move=respond`). It returns without `final`, the node returns normally, and
  `POST /gate/decision` answered 200 "The Define report is approved" with neither record written and the pause used up.
- **Cause: LangGraph issue #9253.** A retry keeps the task's scratchpad, and its subgraph call counter names the
  retried call `define_approval:<task>|1`, a namespace with no checkpoint (the installed langgraph, pinned in
  agent-improve/requirements.txt: `pregel/_loop.py` lines 325–338; `_retry.py` only sets `CONFIG_KEY_RESUMING`). The
  issue is open with no maintainer fix, and community PR #9279 was closed unmerged.
- Brief storage failures are already retried below the graph. The Azure storage library's `ExponentialRetry` is on by
  default with 3 retries (15 s initial backoff), and none of our blob, Store or checkpoint clients overrides it
  (`storage/blob.py`, `core/store.py` ×2, `core/checkpointer.py`: `from_connection_string(...)` with no
  `retry_policy` or `retry_total`).
- A restart after a killed process resumes the subgraph correctly (ADR-0087 test 6 passes), because a new run's
  counter starts at 0.

## Decision

3 (replaces ADR-0087 decision 3). **The approval node has no error handler and no retry policy.** On any failure it
undoes both writes in place (the Store record as T29 does; the case record restored to what it held before, when it
now holds this run's approval) and re-raises. The task stays pending with its pause. `POST /gate/decision` answers 503:
"The approval could not be saved because the storage service is not reachable. Nothing you confirmed is lost. Please
approve again in a few minutes." A second approval completes it, writing both records exactly once.

This is an exception to the graph rule that a node with external writes carries an error_handler: a handler here
would use up the pending decision (ADR-0087 spike, Q1 and Q2).

3a. **The route answers "approved" only when it can see the result:** the Store record exists, the case record shows
the phase passed, and the case's phase has advanced; otherwise it answers 500 with a plain message.

3b. **A node that invokes a checkpointed subgraph never carries a `retry_policy`** (graph rule §3.6). This is
reviewed when LangGraph fixes #9253.

## Rejected options

- **A — patch LangGraph's private scratchpad** (reset the subgraph call counter at the start of the approval node, so
  a retry resumes). It keeps ADR-0087's text, but it depends on a private, frozen LangGraph structure
  (`__pregel_scratchpad`), which an upgrade can change silently. The storage library already retries what a graph-level
  retry would.
- **A separate write node after the subgraph node.** Its retries would not re-run the subgraph, but it adds a node to
  solve one problem (founder: no node per problem), and the subgraph's result would have to cross nodes through
  `SupervisorState`'s messages.

## Tests (replaces ADR-0087 test 4)

4. A failure at the case write, once the storage library's own retries are spent: 503 with the message above; neither
   record; `GET /gate/review` still shows the pause; a second approval writes both records exactly once.
4a. A run that returns without the case record is not answered as approved (decision 3a).
4b. Decision 3b: no node that invokes a checkpointed subgraph carries a `retry_policy`
   (`test_supervisor_graph.py::test_a_node_that_invokes_a_checkpointed_subgraph_carries_no_retry_policy`).
4c. Live, against real Azure storage with zero model calls (`scripts/live_approval_check.py`): an approval writes the
   Store record and the case record once each; a case write refused by storage answers 503 with the message above,
   removes the Store record, keeps the pause, and the second approval writes both once.

## Consequences

- A transient storage failure that outlasts the storage library's retries asks the lead to approve again. It is no
  longer absorbed silently.
- The defect is registered as G-239 (escape class `error_routine`); its D7 is decision 3b.
