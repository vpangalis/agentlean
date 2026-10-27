# ADR-0113: A coaching turn is never thrown away — 45 s is a progress threshold, the hard limit is 120 s, and a failed turn is retried once from where it started

Status: ACCEPTED (founder, 2026-10-27, ruling R-F and the register-report rulings 2 and 3; drafted by Claude Code from the ruling — decision 1 is the founder's text, verbatim)
Requirements: R13 "Turn time" (amended 2026-10-27, R-F), W10 "Failures stay readable", W11 "Nothing typed is lost"; founder test 2026-10-27 findings 59 and 62; G-331, G-336 to G-340
Supersedes: ADR-0080 "A coaching turn has one deadline, and every model call a request timeout" (its decisions 1, 2 and 6 — the request timeouts and the judges that keep a reply — are carried over unchanged)
Depends on: ADR-0043 (durability "async", unchanged), ADR-0066 (unfinished work lives in the checkpoint), ADR-0101 (the async Blob saver)

## Context — measured on the founder's test, case IMPR-2026-PDLWG9 (LangSmith project agent-improve, Store step_log)

| Turn (UTC) | Belt's message | Before the graph | Guard | Planner | Coach | Grader | After the last node (saves) | Outcome |
|---|---|---|---|---|---|---|---|---|
| 15:26 | flawed SIPOC | 5.8 s | 1.4 s | 7.7 s | 16.3 s | 1.8 s | 4.5 s, cut | cancelled at 42 s; every node had finished |
| 15:28 | same, resent | — | 1.6 s | 4.9 s | 15.0 s | 2.1 s | 5.0 s | answered (30.2 s) |
| 15:30 | complete SIPOC | 0.9 s | 2.5 s | 10.4 s timed out, then 7.2 s | cut at 19 s | — | — | cancelled at 42 s |
| 15:31 (T-mvquf3c7-33qp) | same, resent | 1.3 s | 1.7 s | 8.3 s | 13.4 s | 2.2 s | 4.9 s | answered (32.9 s): the R18 link check |
| 15:33 (T-mvquhjs6-u4hy) | the barriers answer | 1.6 s | 1.7 s | 8.9 s | 20.3 s | 2.8 s | 5.5 s, cut | cancelled at 42 s; every node had finished |
| 15:34 | same, resent | — | 2.3 s | 10.2 s × 3, all timed out | — | — | — | T29's degraded reply: "Something went wrong on our side" |

- Two of the three cancelled turns had produced their answer; the 42 s cancellation landed in LangGraph's loop exit while it waited for the checkpoint writes. The founder lost finished work and was asked to retype it.
- Each cancelled turn left the Belt's message stored with no reply; every resend stored it a second time (messages 90/91, 97/98 and 102/103 of the case).
- The deadline reply is an HTTP 200 by design (ADR-0080 decision 4), which is why the terminal showed `POST /ask 200` for a turn the page showed as timed out.

## Decision

1. **The founder's ruling (verbatim):** "The 45 s turn deadline becomes a progress threshold, not a cancellation. At 45 s the Belt is told the coach is still working; the turn continues to a hard limit of 120 s. A turn whose answer has been produced always completes its save. A failed turn is retried once automatically; only a failed retry is shown, with the Belt's message returned to the input and a Send again control. The Belt is never asked to retype."
2. **The numbers** are owned by `core/config.py`: `TURN_LIMIT_S = 45` (the progress threshold; the page's `TURN_PROGRESS_MS` reads the same 45 and a test keeps them equal) and `TURN_HARD_LIMIT_S = 120`, less the 3 s closing reserve. The route alone enforces the hard limit, from the request's arrival (G-166 kept).
3. **"Answer produced" is marked in code**: the executor marks the turn's record (`request_context.mark_answered`) when it returns its reply. From then on the route never cancels the run — not at the hard limit, not on a disconnect — and waits for its save. Before it, a disconnect still abandons the run (§47) and the hard limit cancels it.
4. **The automatic retry is a fork, not a node retry.** A failed turn (T29's degraded reply, or an error out of the run) is run once more with the same input from the checkpoint the turn started from (`ainvoke(input, {checkpoint_id: <that checkpoint>})`). LangGraph forks the thread there and the saver's `latest.json` then names the fork, so the failed attempt leaves nothing in the conversation — no second copy of the Belt's message, no degraded reply. Probed on the installed LangGraph 1.2.11 with the project's own Blob saver before it was built.
5. **What is not retried:** the hard limit itself, a disconnect, a refusal the route answers by name (busy case, phase not wired, newer state version), a case's first turn (no checkpoint to start from), a retry that would start with under 30 s of the hard limit left, a token-limit failure (§4.8: the same call fails the same way), and a content-filter refusal.
6. **The retry stays inside the 120 s** (founder, 2026-10-27, ruling 3). The hard limit is the turn's as the Belt experiences it, so the retry runs in what is left of it, and only with at least 30 s left; a turn that reached 120 s is shown as failed, not run again.
7. **Two more failures count as failed turns**: both models down through their retries (T34 level 4) and G-140's unusable read-back. Both are marked as T29's handler marks a failure, so they are retried and then shown with Send again.
8. **What the Belt sees on a final failure**: the reply carries `failed: "degraded" | "time"`; the page shows the failed-turn card with the message back in the box and a **Send again** button. No failure text asks the Belt to send or retype; the six such texts were reworded (deadline, turn failed, degraded, level 4, G-140, the safety check unavailable), and the busy-case text points at the Send again button.
9. **The progress text** at 45 s: "Still working on your answer — long answers take a little longer", in the page's working indicator.

## Consequences

- No answered turn is lost to a clock again; the worst case a Belt waits is 120 s.
- R12's run-through criterion "no turn over 45 s" is unchanged: 45 s stays the target every run-through measures. Only the cancellation moved.
- A failed attempt's checkpoints remain in Blob history, unread (the fork is the thread's latest); G-220's checkpoint-weight analysis counts them.
- The route now runs the graph through `_run_coaching_turn`; `TurnDeadline` is raised only at the hard limit with no answer.

## Rejected

- **`retry_policy` on the phase node** — banned on a node that invokes a checkpointed subgraph (G-239, LangGraph issue #9253): the retry re-calls the subgraph under a new namespace.
- **A retry in the page** — the failed attempt's Belt message stays in the checkpoint, so every retry stores it twice; the founder's case shows the result.
- **A fresh 120 s for the retry** (worst case 240 s) — rejected by the founder, 2026-10-27 (ruling 3).
- **Durability `exit`** to make a failed turn leave nothing — breaks DEF-003's guarantee (ADR-0043 facts, 2026-10-22).

## Verification

- `backend/tests/test_define_e2e.py::test_rf_a_turn_is_never_thrown_away_and_the_belt_never_retypes` — the threshold cancels nothing; an answered turn's save runs past the hard limit and completes; a failure is retried from where it started (the Belt's message held once, no degraded reply); a failed retry is flagged; no failure text asks to send or retype; the page shows the progress text and the Send again card.
- `test_g157_a_turn_never_runs_past_its_deadline` (the hard limit with no answer), `test_t38_…` and `test_t34_…` (retries counted across the two runs).
- Live: a slice of element 12 with the founder's exact SIPOC texts — no turn discarded, no "send again", the time of every step logged.
