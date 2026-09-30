# G-139 D7 — every place the stack calls a model again by itself

Founder 2026-09-30 (review of 309f9fc), item 3. Checked against the code on main (68cd0f6) and the
live record define_runthrough_20260930T102427. T69's budget is **4 model calls per turn**
(`TURN_MODEL_CALLS`): the planner's judgment (1, when the Belt answered), the coach's share
(`coach_limit` = 4 − planner − 2), and two after-agent checks (coherence, grader).

| # | Where | What makes it call a model again | Counted by the coach's limit? | Within T69's 4 per turn? | State |
|---|---|---|---|---|---|
| 1 | `create_agent`'s structured output — `ToolStrategy(handle_errors=True)`, its default | the structured reply fails validation, or more than one structured reply comes back: an error goes back as a tool result and the model is called again | yes — an agent model call | on an answer turn the re-call is past the 1-call share, so the turn ends in a code-written reply | **two replies: prevented** (ADR-0073, `parallel_tool_calls=False`); **a reply that fails validation: still ends in a fallback** — G-140 keeps its Confirm honest |
| 2 | the agent loop itself | the coach asked for a tool; the result goes back and the model is called again | yes | teaching turns: a 2-call share, the last call offered no tools (G-131) | bounded |
| 3 | `ModelRetryMiddleware(max_retries=2)` | an exception on the call (rate limit, 5xx, connection) — never a content-filter refusal (T92) | **no** — the limit encloses the retry, so a retried call counts once | **no** — up to 3 HTTP requests per counted call; T69 counts calls, not requests | bounded (3×); latency and cost only |
| 4 | `ModelCallLimitMiddleware(run_limit=coach_limit, exit_behavior="end")` | — | it is the limit | — | — |
| 5 | `SummarizationMiddleware` (the `summarizer` model) | the conversation passes 100,000 tokens | **no** — its own call, before the coach's | **no** | dormant in Define (a run is far below the trigger); unguarded if reached |
| 6 | query variants inside the `rag_lookup_*` tools (`knowledge/fusion.py`, the `extraction` model) | every lookup, on teaching turns | **no** — a call inside a tool | **no — observed: turns 22 and 27 of 102427 made 5 model calls** (coach, variants, variants, coach, coherence) | **finding: T69's per-turn count leaves out tool-internal calls** |
| 7 | `ToolRetryMiddleware(max_retries=2)` | a tool raised | no | a retried lookup repeats its variant call (#6) | bounded (3×) |
| 8 | `CoherenceMiddleware` | once per turn; it never regenerates the reply | the after-agent share (1 of 2) | yes | — |
| 9 | `DMAICGraderMiddleware` | once per turn (its iterations are held); skipped when coherence degrades | the after-agent share (2 of 2) | yes | — |
| 10 | the planner's judgment — the node's `RetryPolicy(max_attempts=3)` | an exception on the judgment call re-runs the planner node | outside the agent; counted as the planner's one | **no** — up to 3 judgment calls on transient errors | bounded (3×) |
| 11 | the OpenAI client (`max_retries=0`) | never | — | — | — |
| 12 | the executor's `TimeoutPolicy` + `error_handler` | never: the move's reply is written in code | — | — | — |

## What the table asks the founder to decide

- **#6:** either count tool-internal model calls in T69's budget, or state in T69 that the budget
  counts the coach's own calls only. Today the four-call ceiling is exceeded on teaching turns with
  lookups (two variant calls on one turn).
- **#1:** a structured reply that fails validation on an answer turn still ends in a code-written
  reply. Allowing one validation retry on answer turns would need the coach's share raised to two
  there (a T69 change).
- **#3, #7, #10:** retries are bounded at three attempts and count once. That is the ruled design
  (ADR-0059); listed so the budget's meaning is on record.
