# Task 3B — Verification Log for AGENT_IMPROVE_BIBLE.md

**Date:** 2026-08-21
**Scope:** Every architectural and technical claim in the Bible that could have
drifted — API signatures and parameter names, deprecation status, version
floors, cited GitHub issues, and the Anthropic engineering post index.
**Method:** `/verify-current-version` source tiers. PyPI JSON API and the
Anthropic engineering index first, per the skill's own instruction.

**Outcome: 3 corrections, 2 now-stale-and-fixed, 4 enhancements, 15 confirmed.
No finding invalidates a ratified architectural decision.** Every correction is
a parameter name, a version number, or an over-stated justification — the
designs themselves held.

---

## Verdict summary

| Verdict | Count | Meaning |
|---|---|---|
| **CORRECTED** | 3 | The Bible was wrong; fixed in place |
| **NOW-STALE-AND-FIXED** | 2 | True when written, no longer true; fixed |
| **ENHANCED** | 4 | Not wrong, but incomplete in a way worth closing |
| **CONFIRMED** | 15 | Verified current, no change |

---

## CORRECTED — the Bible was wrong

### C-1 · `ModelRetryMiddleware` parameter name

| | |
|---|---|
| **Claim** | `ModelRetryMiddleware(retries=2)` |
| **Source** | `reference.langchain.com/python/langchain/agents/middleware/model_retry/ModelRetryMiddleware` |
| **Verdict** | **CORRECTED** |

The parameter is **`max_retries`**, not `retries`. Full signature:

```python
ModelRetryMiddleware(*, max_retries=2, retry_on=default_retry_on,
                     on_failure='continue', backoff_factor=2.0,
                     initial_delay=1.0, max_delay=60.0, jitter=True)
```

**`retries=` does not exist and would raise at construction.** This is the most
consequential finding in the pass: the wrong keyword appeared in the Bible,
`CLAUDE.md`, `ARCHITECTURE.md` and `DECISIONS.md`, and it sat inside the
canonical middleware stack — the block an implementer copies verbatim.

Worth noting *why* it survived: `ToolRetryMiddleware` was verified against the
reference when it was added (B3.1, 2026-08-12) and is correct;
`ModelRetryMiddleware` was adopted earlier and never re-checked. **The two
middlewares share a parameter vocabulary, which is exactly the situation where
remembering one and inferring the other goes wrong.**

**Fixed:** Bible §19 and §19.4. Still to propagate: `CLAUDE.md` §8.1/§8.7,
`ARCHITECTURE.md` §3.4, `DECISIONS.md` §B3.

### C-2 · `create_agent` prompt parameter

| | |
|---|---|
| **Claim** | `create_agent(..., prompt=PHASE_COACH_PROMPT[phase])` |
| **Source** | `reference.langchain.com/python/langchain/agents/create_agent`; LangGraph v1 migration guide |
| **Verdict** | **CORRECTED** |

The parameter is **`system_prompt`**. `create_react_agent` took `prompt`;
`create_agent` renamed it, and the migration guide calls this out explicitly as
a difference to watch when porting.

Verified full signature confirms `middleware=` and `response_format=` as the
Bible states, and adds `state_schema`, `context_schema`, `checkpointer`,
`store`, `interrupt_before`, `interrupt_after`, `cache`, `transformers`.

**Fixed:** Bible §18, with the rename noted inline.

### C-3 · "the six `AgentMiddleware` hooks"

| | |
|---|---|
| **Claim** | Middleware is built on *the six* hooks — stated as a complete set |
| **Source** | `reference.langchain.com/python/langchain/agents/middleware` |
| **Verdict** | **CORRECTED** |

The six named are all real and all present. **But they are not the complete
set** — the reference also lists `dynamic_prompt()`, `hook_config()` and
`configure_trace_policy()`.

A small error with a real consequence: "the six hooks" framed the middleware
surface as closed, which would mislead anyone extending the stack.

**Fixed:** Bible §19 now says these are the six *we use*, not the six that
exist.

---

## NOW-STALE-AND-FIXED — true when written, not now

### S-1 · `BaseStore.search()` capability

| | |
|---|---|
| **Claim** | The Store lacks metadata filtering, hybrid BM25+vector scoring, and multi-query+RRF — three reasons to keep `improve_case_index` on Azure AI Search |
| **Source** | `docs.langchain.com/oss/python/langgraph/stores`; `reference.langchain.com/python/langgraph.store/base/BaseStore` |
| **Verdict** | **NOW-STALE-AND-FIXED** |

`search()` supports `query`, **`filter`**, `limit`, **`mode`
(`text` | `vector` | `hybrid` | `auto`)**, `offset`, `similarity_threshold`,
`vector_weight` and `distance_metric`.

- **Metadata filtering** — already corrected on 2026-08-20 (`filter=` exists)
- **Hybrid scoring** — `mode="hybrid"` now undercuts the second reason too

**The conclusion survives on the third reason plus migration cost:** the Store
has no multi-query + RRF (§25), which is the mechanism Agent Resolve production
experience showed this corpus needs.

**But the decision now rests on one technical reason rather than three.**
Recorded in §9 rather than left looking better-supported than it is, and
flagged for re-examination if the Store's search surface keeps growing.

### S-2 · Pinned dependency targets

| | |
|---|---|
| **Claim** | Upgrade targets `langgraph` 1.2.10, `langchain` 1.3.11, `langchain-classic` 1.0.3 |
| **Source** | PyPI JSON API |
| **Verdict** | **NOW-STALE-AND-FIXED** |

| Package | Documented target | Actual latest |
|---|---|---|
| `langgraph` | 1.2.10 | **1.2.11** |
| `langchain` | 1.3.11 | **1.3.16** |
| `langchain-classic` | 1.0.3 | **1.0.8** |

**Two findings the version numbers alone do not show:**

1. **`langchain` 1.3.16 requires `langgraph>=1.2.11,<1.3.0`** — so upgrading
   `langchain` satisfies the LangGraph floor automatically, with margin.
2. **`langchain` 1.3.16 requires `langchain-core>=1.6.0`; installed is 1.3.3.**
   That is a three-minor jump and is the most likely source of surprises in the
   upgrade — larger than any document had recorded.

**Fixed:** Bible §53 rewritten with verified versions and both findings.

---

## ENHANCED — not wrong, but incomplete

### E-1 · `set_node_defaults` for graph-wide policy

**Source:** `docs.langchain.com/oss/python/langgraph/fault-tolerance`

The Bible says `TimeoutPolicy` and `error_handler` are "required on every phase
executor node" / "every node with external writes," implying per-node
repetition. LangGraph provides **`set_node_defaults`** for exactly this — a
better fit for a rule phrased as "on every node."

Two constraints came with it, both now recorded: **`cache_policy` and
`error_handler` defaults apply to regular nodes only** — caching a handler's
result is unsafe, and **a handler must never catch itself.**

**Added:** Bible §45.

### E-2 · Retry/handler composition order

**Source:** as above

**When a node raises — including `NodeTimeoutError` — the retry policy decides
first, and `error_handler` runs only after retries are exhausted.**

The Bible's §44 pipeline could be read as "timeout → compensation directly."
The real order has retries in between, which changes how long a failing node
takes to reach the fallback chain.

**Added:** Bible §45.

### E-3 · `TimeoutPolicy(idle_timeout=...)`

**Source:** as above

`TimeoutPolicy` accepts `idle_timeout` — refreshed by progress signals —
alongside the wall-clock `run_timeout`. A bare number or `timedelta` is a hard
cap that is *not* refreshed.

`run_timeout=45` stays ratified. `idle_timeout` is now recorded as available if
a long legitimate tool call ever needs distinguishing from a hang.

**Added:** Bible §45.

### E-4 · Anthropic index — three posts missing from Tier 1

**Source:** `anthropic.com/engineering` index, read in full

**Nothing has been published after the list's August 2026 cutoff.** Newest
dated post is *"An update on recent Claude Code quality reports"* (Apr 23,
2026).

**But three in-window posts were never picked up:**

| Post | Date | Bears on |
|---|---|---|
| Designing AI-resistant technical evaluations | Jan 21, 2026 | §52 |
| Quantifying infrastructure noise in agentic coding evals | Feb 05, 2026 | §52's >10% regression threshold |
| Introducing advanced tool use on the Claude Developer Platform | Nov 24, 2025 | §29, §30, §31 |

Two bear on evaluation design — **the part of this architecture with the least
production evidence behind it**, and where the >10% threshold is currently an
asserted number.

Four further posts were reviewed and **deliberately not added** as
product/model-specific rather than architectural.

**Added:** Bible Appendix C, with the refresh recorded.

---

## CONFIRMED — verified current, no change

| # | Claim | Source | Note |
|---|---|---|---|
| 1 | `ToolRetryMiddleware(max_retries=2, tools=None, on_failure='continue', backoff_factor=2.0, initial_delay=1.0, max_delay=60.0, jitter=True)` on `wrap_tool_call` | reference | **Every parameter and default matches exactly.** `on_failure` accepts `'continue'`, `'error'`, or a callable |
| 2 | `SummarizationMiddleware` takes `trigger=` and `keep=` | reference | Confirmed. `trigger` accepts a `ContextSize` tuple, a `TriggerClause` dict, or a list; `keep` takes one `ContextSize` and defaults to 20 messages — matching our `keep=("messages", 20)` |
| 3 | `create_react_agent` deprecated, superseded by `langchain.agents.create_agent` | LangGraph v1 migration guide | Deprecated in v1.0, **scheduled for removal in v2.0** |
| 4 | `langgraph.prebuilt` must not be imported | as above | Confirmed |
| 5 | `MultiQueryRetriever` and `EnsembleRetriever` moved to `langchain_classic` | LangChain v1 migration guide; reference | **Confirms the 2026-08-20 C3 ruling** — `CLAUDE.md` §7.4 was right, `DECISIONS.md` §E1 was wrong |
| 6 | `RemainingSteps` is a LangGraph managed value readable as `state["remaining_steps"]` | reference; docs | Confirmed. `RemainingStepsManager` computes `scratchpad.stop - scratchpad.step`. **The `remaining_steps <= 2` graceful-degradation pattern is a documented use**, not our invention |
| 7 | Cited issue: `langchain-ai/docs` #475 on `RemainingSteps` docs | GitHub | Real and correctly characterised |
| 8 | LangGraph floor **≥1.2.6** for the subgraph `checkpoint_ns` fix | GitHub releases API | **Precisely attributable.** 1.2.6 (2026-06-18): *"nested subgraph inherits parent `checkpoint_ns` (regression in 1.2.3)"* |
| 9 | `TimeoutPolicy(run_timeout=...)` and `error_handler=` on `add_node`, LangGraph 1.2+ | fault-tolerance docs | Confirmed, incl. the Saga-compensation framing |
| 10 | `DeltaChannel` exists and is not production-ready for us | GitHub releases | Confirmed — active fixes through 1.2.7/1.2.8/1.2.9. Deferral stands |
| 11 | `RubricMiddleware` requires deepagents, not core LangChain | built-in middleware docs | Confirmed: *"requires `deepagents>=0.6.5`"* and marked **beta**. §18's exclusion holds |
| 12 | deepagents is pre-1.0 | PyPI | **0.4.11 stable.** The "revisit at 1.0" trigger has not fired |
| 13 | `create_agent` takes `middleware=` and `response_format=` | reference | Confirmed in the full signature |
| 14 | `AzureSearch.similarity_search(query, k=, filters=)` — filter at call time | in-repo code + LangChain community | Confirmed; the 2026-08-21 E4 rewrite holds |
| 15 | `AzureAISearchRetriever` offers no advantage justifying adoption | reference | **The brief's explicit question. No advantage found — decision stands.** Recorded in §24 so it is not re-opened without new evidence |

---

## Not verified — stated plainly

| Claim | Why not | Risk |
|---|---|---|
| `RunControl.request_drain()` | Absent from releases 1.2.5–1.2.11; not located in the reference within this pass | **RERATED 2026-08-21 → UNCONFIRMED — MAY NOT EXIST.** See below |
| `HumanInTheLoopMiddleware` edit/reject bugs in subgraphs | Behavioural claim; no specific issue number recorded to re-check | **Low.** The ban is over-determined — graph-level `interrupt()` is independently required by the nine-step gate (§33) |
| GitHub issues #30482, Discussion #1260, deepagents #1698 | Not individually re-opened this pass | **Low.** #30482 concerns `AzureAISearchRetriever`, now explicitly not adopted; #1260 and #1698 support a `RemainingSteps` decision independently confirmed at line 6 |
| `langgraph-checkpoint` 4.x `JsonPlusSerializer.dumps_typed()` returns msgpack | Implementation detail discovered during commit 2.1 | **Low.** Empirically established in working code |

---

### `RunControl.request_drain()` — rerated 2026-08-21

**"Unverified" understated it. The correct marker is UNCONFIRMED — MAY NOT
EXIST**, and it is now recorded that way everywhere the API appears.

The distinction matters. *Unverified* suggests a claim awaiting confirmation.
This one has **no evidence behind it at all**: it entered the architecture as a
recommendation, was carried forward on citation, and has never been checked
against a release or against source. It was searched for across LangGraph
1.2.5–1.2.11 and in the reference during this pass and was **not found**.

**Binding consequences, applied:**

1. **No work may be scheduled against it — including in Task 4.** A task naming
   `request_drain()` may be unbuildable.
2. **If it does not exist, §45 needs a real fallback drain design**, not a
   replacement citation. Named candidates: a readiness probe that fails while
   in-flight turns complete, or a shutdown hook that stops accepting new
   `ainvoke` calls and awaits the current node.
3. **Confirmation means** the symbol found in the installed package, in the
   LangGraph source at a named version, or in the API reference with a version
   stamp. **A blog post or a model's recollection is not confirmation.**

**Marked at:** Bible §1 and §45 · `CLAUDE.md` §3.6 · `ARCHITECTURE.md` §9.2 ·
`docs/DECISIONS.md` §F1 · `docs/CONTINUITY.md`. It was also **removed from the
≥1.2.6 blocker list** in the Bible and `CONTINUITY.md`: it is not gated on the
version upgrade, it is gated on existing.

---

## Follow-up status — 2026-08-21 propagation pass

The five recommendations at the foot of this log, and what happened to each.

| # | Follow-up | Status |
|---|---|---|
| 1 | Propagate C-1 (`max_retries`) | **DONE.** `CLAUDE.md` §8.1 + §8.7 (with the full verified signature), `ARCHITECTURE.md` §3.3 + §3.4 + §15 Step 5.6, `docs/DECISIONS.md` §B3, `docs/REFACTORING_AGENT_IMPROVE.md` §80 + §84 stack, `docs/REVIEW_DECISIONS.md`, `docs/CONTINUITY.md` |
| 2 | Propagate C-2 (`system_prompt`) | **DONE.** `CLAUDE.md` §4.4, `ARCHITECTURE.md` §3.3, `docs/REFACTORING_AGENT_IMPROVE.md` §82 examples |
| 3 | Verify `RunControl.request_drain` | **NOT DONE — deliberately.** Rerated and gated instead (above). Verification is a Task 4 precondition, not a Task 4 task |
| 4 | Read the two eval posts before finalising §52 | **OPEN.** The >10% threshold in §52 is still asserted |
| 5 | Re-examine S-1 if `BaseStore.search` gains multi-query or fusion | **OPEN**, as designed — a watch item with a trigger |

**C-3 was propagated in the same pass** though it was not on the follow-up
list: `CLAUDE.md` §8.1 said "the six `AgentMiddleware` hooks" as though the set
were closed. It now says the six *this stack uses*, and names the three it does
not.

**S-2 was propagated in the same pass** for the same reason: `CLAUDE.md` §16.1
still carried the stale 1.2.10 / 1.3.11 / 1.0.3 targets the Bible §53 had
already corrected, and §1.9 said "LangGraph 1.2.10+" where the rule is the
**≥1.2.6 floor**. A constitution stating a version target its design document
has corrected is the §0.9 failure mode repeating.

**Live-code exposure: none.** `create_agent`, `ModelRetryMiddleware` and
`ToolRetryMiddleware` do not yet appear anywhere in `backend/` — the v1 code
predates all three. **Every occurrence of both wrong keywords was in
documentation**, which is why they survived: nothing executed them. They would
have been executed first by whoever implemented Step 5.6 from the canonical
stack.

**Remaining occurrences of `retries=`, left deliberately:**
`docs/EDUCATIONAL.md` and `docs/STATE_DESIGN_RESOLUTION.md` — pre-decision
working documents, not build targets. Corrections are recorded against the
documents that are.

---

## What this pass did not cover

- **Azure AI Search index schemas** — verified against the live index in prior
  sessions, not re-checked here. The two pending schema changes (§23) remain
  `RATIFIED — NOT YET APPLIED`.
- **The `UNVERIFIED` marker in §26** — whether planned multi-hop should extend
  beyond Analyse is an empirical question about our own system. **No external
  source can settle it; it needs the §52 eval dataset.** The marker stays.
- **LangSmith API surface** — tracing claims are generic (`@traceable`, spans)
  and not version-sensitive.

---

## Recommended follow-up

1. **Propagate C-1** (`max_retries`) to `CLAUDE.md` §8.1/§8.7,
   `ARCHITECTURE.md` §3.4 and `DECISIONS.md` §B3. **The wrong keyword is
   currently in the constitution.**
2. **Propagate C-2** (`system_prompt`) to `CLAUDE.md` §4.4.
3. **Verify `RunControl.request_drain`** before any work depends on it.
4. **Read the two eval posts** (E-4) before finalising §52 — the >10% threshold
   is currently asserted, and one post is specifically about telling real
   regressions from infrastructure noise.
5. **Re-examine S-1** if `BaseStore.search` gains multi-query or fusion.

---

## Sources consulted

- `https://pypi.org/pypi/langgraph/json`
- `https://pypi.org/pypi/langchain/json`
- `https://pypi.org/pypi/deepagents/json`
- `https://pypi.org/pypi/langchain-classic/json`
- `https://www.anthropic.com/engineering`
- `https://api.github.com/repos/langchain-ai/langgraph/releases`
- `https://docs.langchain.com/oss/python/langchain/middleware`
- `https://docs.langchain.com/oss/python/langchain/middleware/built-in`
- `https://reference.langchain.com/python/langchain/agents/create_agent`
- `https://reference.langchain.com/python/langchain/agents/middleware`
- `https://reference.langchain.com/python/langchain/agents/middleware/model_retry/ModelRetryMiddleware`
- `https://reference.langchain.com/python/langchain/agents/middleware/tool_retry/ToolRetryMiddleware`
- `https://reference.langchain.com/python/langchain/agents/middleware/summarization/SummarizationMiddleware`
- `https://docs.langchain.com/oss/python/migrate/langchain-v1`
- `https://docs.langchain.com/oss/python/migrate/langgraph-v1`
- `https://docs.langchain.com/oss/python/langgraph/fault-tolerance`
- `https://docs.langchain.com/oss/python/langgraph/stores`
- `https://reference.langchain.com/python/langgraph.store/base/BaseStore`
- `https://reference.langchain.com/python/langchain-classic/retrievers/ensemble/EnsembleRetriever`
- `https://reference.langchain.com/python/langchain-classic/retrievers/multi_query/MultiQueryRetriever`

**Sources that failed:**
- `https://reference.langchain.com/python/langgraph/store/base/BaseStore` — 404
  (correct path is `langgraph.store`, not `langgraph/store`; reached via the
  working path above)

---

*End of log.*
