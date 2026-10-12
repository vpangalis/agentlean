# ADR-0080: A coaching turn has one deadline, and every model call a request timeout

Status: ACCEPTED (founder, 2026-10-12, option B; drafted by Claude Code from the ruling)
Requirements: R12 (no turn over 45 s), R13 (45 s per turn); DEF-093; G-157
Depends on: ADR-0043 (native reliability primitives: the executor's `TimeoutPolicy` and `error_handler`
stay), ADR-0044 (fallback chain: this is its level 0, the timeout), ADR-0059 (call limits), ADR-0066
(unfinished work lives in the checkpoint)
Completes: ADR-0043 and ADR-0044 (both PROPOSED) for the turn as a whole; neither is superseded.

## Context

Run 121314 (stop condition 4) took 50.4 s on one turn: the grader's call never answered, the executor's
40 s wall (T70) discarded the coach's finished reply, and closing took 2.7 s more. The limits inside a
turn added up past 45 s and nothing bounded the turn as a whole (G-157): the guard up to about 10.5 s,
the planner's judgment with no timeout (the SDK default of 600 s), the executor's 40 s, closing 1-3 s.

What the framework offers, checked 2026-10-12: a per-node `TimeoutPolicy` (async nodes, per attempt),
`Pregel.step_timeout` (per superstep) and the model client's per-request `timeout`
(https://docs.langchain.com/oss/python/langgraph/fault-tolerance,
https://docs.langchain.com/oss/python/langchain/models). **LangGraph has no deadline for a whole run.**
The founder chose option B of three (A: framework limits only, the executor's wall cut to about 25 s;
C: `step_timeout`, which bounds a superstep, not a turn).

## Decision

1. **Every model role has a request timeout on its client** (`llm.ROLE_TIMEOUTS`, the client's own
   `timeout`): the coach 25 s, the planner's judgment 10 s, coherence and the grader 8 s, the rest
   between 8 and 20 s. `max_retries` stays 0 on the client (retry is the middleware's).
2. **A judge whose call runs out keeps the reply.** Coherence and the grader catch the client's timeout
   (`llm.REQUEST_TIMEOUTS`, by name) and record "not checked (time)"; the coach's finished reply goes
   out. A stalled check never discards a reply.
3. **One turn deadline, in the route.** `/ask` runs the graph against `turn_started` (stamped when the
   turn is configured) + 45 s − a 3 s closing reserve; at the deadline the run is cancelled, exactly as a
   client disconnect cancels it (§47's ABANDON). Nothing after the last completed step is checkpointed.
   Both numbers are owned by `core/config.py` (`TURN_LIMIT_S`, `TURN_CLOSE_RESERVE_S`), and the re-ask's
   time guard (ADR-0079) reads the same deadline, so it never plans a second reply past it.
4. **At the deadline the Belt is asked to send the message again**, in code
   (`prompts.TURN_DEADLINE_REPLY`): nothing new was stored and nothing is lost. **Not the move's own
   reply**: the cancelled turn changed nothing, so a store turn's reply ("Recorded — … is stored") would
   be false (G-117) and a read-back's would offer a Confirm with no pending value behind it (G-163). The
   same reason G-140's resend has. `step_log` records the deadline.
5. **The checkpoint after a deadline is an abandoned turn's**: the Belt's message, no reply, no status
   or value changed. The next turn runs from it as from any abandoned turn.
6. `NodeTimeoutError` is caught by its own name in the executor's `error_handler`: it does not inherit
   from `TimeoutError` (`langgraph/errors.py`; the use-graph-api page says otherwise and is wrong).

## Consequences

- No coaching turn's reply arrives after 45 s; the worst case is the resend reply at 42 s.
- A judge that times out leaves a turn ungraded or unchecked, recorded as such.
- T34's model fallback (ADR-0059 decision 2) is built next, inside this deadline.

## Rejected

- **A: framework limits only.** Node `TimeoutPolicy` values summing under 45 s cut the executor's wall to
  about 25 s, below teaching turns' 90th percentile (28.6 s on run 165140): more replies written in code.
- **C: `step_timeout`.** It bounds a superstep, not the turn.
- **The move's code-written reply at the deadline** — see decision 4.
- **Writing the deadline reply into the checkpoint from the route** — a state write outside the graph;
  an abandoned turn already has a defined shape (§47) and the next turn resumes from it.

## Verification

- `backend/tests/test_define_e2e.py::test_g157_a_turn_never_runs_past_its_deadline`: every role's client
  carries its timeout; a judge that times out keeps the reply and records "not checked (time)"; a coach
  that would run past the deadline is cancelled — the resend reply arrives within the limit, the
  checkpoint holds the Belt's message and nothing else changed, the cancelled reply never lands, and the
  next turn runs the move normally.
- The live run of the bundle: no turn over 45 s.
