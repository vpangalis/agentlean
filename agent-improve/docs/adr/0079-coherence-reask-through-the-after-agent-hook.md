# ADR-0079: A coherence rejection asks the coach again through layer 2a's after_agent hook

Status: ACCEPTED (founder, 2026-10-12; drafted by Claude Code from the rulings)
Requirements: R1 (guide the Belt through the method); DEF-014
Depends on: ADR-0059 (framework call limits), ADR-0069 (answer turns bind no tools), ADR-0041 (two graders)

## Context

Layer 2a (`CoherenceMiddleware`, `after_agent`) judged the coach's reply and, on a rejection, only
degraded the turn: the reply went to the Belt unchanged and the grader stood down (S-C13 B3). The
founder ruled DEF-014 on 2026-10-12, option B: one re-ask within T69's four calls, the second reply
not re-checked, never on an answer turn, and only when the turn's remaining time allows it within
45 s. The change gives a middleware hook a new jump, which `.claude/rules/adr.md` requires an ADR for;
the commit that built it (7cabf9d) declared "Design: unchanged". This ADR records it.

The same day the offline evaluation set showed the judge's rejections mostly false (G-161), and the
founder ruled a containment: the judge runs log-only until its false-reject rate is under 20%.

## Decision

1. **The re-ask is the framework's own loop, not a loop in the node.** `CoherenceMiddleware.aafter_agent`
   is declared `@hook_config(can_jump_to=["model"])`; on a rejection it returns
   `{"jump_to": "model", "messages": [SystemMessage(COHERENCE_REASK)]}` — the rejection's reason as
   quality feedback, never as the Belt's message (§21). The agent calls the coach once more.
2. **The second reply is not re-checked**; it is the reply the Belt receives. The grader stands down
   on the turn, as for any rejection (DEF-015 option A, grading rejected replies, is paused).
3. **When there is no re-ask** — an answer turn (ADR-0069's single call), the coach's share of T69's
   calls spent, or no time left for a second reply inside R13's 45 s and T70's node wall — the first
   reply goes out, and the turn's one layer-2a record in `step_log` says which:
   `"coherence rejected, no re-ask (<reason>)"`.
4. **The call budget is the call limit's own count**: `run_model_call_count` in the agent state, kept
   by `ModelCallLimitMiddleware` (ADR-0059; G-164 — never a count of AI messages).
5. **Containment in force (G-161, founder 2026-10-12):** `coherence.COHERENCE_MODE = "log_only"` — every
   verdict is recorded and no re-ask is made. Removal condition: `scripts/judge_replay.py` shows the
   judge's false-reject rate under 20% against the founder's labels; then the mode is `"enforce"` and
   points 1-3 apply as written.

## Verified

- The installed langchain (its pin is in `agent-improve/requirements.txt`): `langchain/agents/factory.py`
  wires `after_agent` hooks with `model_destination=loop_entry_node` and resolves `jump_to` in
  `_resolve_jump`, so a jump to the model from `after_agent` returns to the loop entry (read 2026-10-12).
- Documentation, checked 2026-10-12: https://docs.langchain.com/oss/python/langchain/middleware/custom
  describes `'model'` as "Jump to the model node (or the first `before_model` hook)", and
  https://reference.langchain.com/python/langchain/agents/middleware/types/hook_config says to use
  the decorator "on `before_model` or `after_model` methods". **The jump from `after_agent` is wired in
  the source but not documented**; DEF-014's end-to-end test pins it, so a library change that removes
  it fails the suite rather than silently ending the re-ask.

## Consequences

- A rejected teaching, read-back or store turn can take one more coach call; the time guard keeps the
  turn inside 45 s (DEF-093's turn deadline is the hard bound).
- `step_log`'s coherence record carries `reask` and `mode`.

## Rejected

- **A re-ask loop in the executor node** — a hand-written agent loop (rule 0.24); the framework's jump
  already re-enters the model with the middleware stack around it.
- **Re-checking the second reply** — a second judge call per turn, and a possible third coach call,
  over T69's budget and the 45 s.
- **A re-ask on answer turns** — they keep ADR-0069's single call.

## Verification

- `backend/tests/test_define_e2e.py::test_a_coherence_rejection_asks_the_coach_again`: in log-only mode
  a rejection changes nothing and is recorded so; in enforce mode a teaching turn is asked again (the
  feedback as a system message, the second reply not re-checked and sent), an answer turn is not, a
  turn without time is not; the call budget is read from `run_model_call_count`.
