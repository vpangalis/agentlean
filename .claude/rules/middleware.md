---
paths:
  - "agent-improve/backend/middleware/**"
  - "agent-improve/backend/phases/nodes_common.py"
---
# §8 — Middleware stack

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

## 8. MIDDLEWARE STACK

### 8.1 — Eight middlewares, all on `create_agent`

**Canonical: ARCHITECTURE.md §19.** The stack's members and order are owned by
`_build_executor()` in `backend/phases/nodes_common.py`, enforced by
`test_the_declared_middleware_list_is_the_ratified_layering` (verify_built.py retired at 6.67).
**Read the list there; do not restate it.**

**The list is NESTING order; for `after_*` hooks execution is the reverse.**
`before_*` fire first → last; `after_*` fire last → first; `wrap_*` nest, the
first declared outermost. Re-derive from the installed
`langchain/agents/factory.py` if it matters — never copy it here.

- **`BeforeModelStateInjection` MUST be first, on `before_agent`** (once per
  turn), never `before_model`.
- **If `CoherenceMiddleware` exhausts its retries, `DMAICGraderMiddleware` is
  skipped** — this works only because coherence sits **inside** the grader.
- **Position 1's `wrap_model_call` encloses `ModelRetryMiddleware`** — a retry
  re-sends the built request, never rebuilds it
  (`test_position_1_wrap_encloses_position_4_retry`).
- **The six lifecycle hooks are the complete set** — `before_agent`,
  `before_model`, `after_model`, `after_agent`, `wrap_model_call`,
  `wrap_tool_call`, plus `a`-prefixed async twins. `dynamic_prompt()`,
  `hook_config()`, `configure_trace_policy()` are module-level names, not
  hooks (ARCHITECTURE.md §19).
- **Three independent retry caps, never merged:** `ModelRetryMiddleware` 2,
  `CoherenceMiddleware` 2, the validation stack's shared gate cap 3 (§9.2).
- **Prefer built-in middleware**; custom only for domain-specific logic.

### 8.2 — `DMAICGraderMiddleware` — coaching-quality grading

**Custom, on `create_agent`. Not deepagents' `RubricMiddleware`** (§4.4).

**THERE ARE TWO GRADERS. They are not redundant, and confusing them is a
violation.**

| | `DMAICGraderMiddleware` (this rule) | Validation stack Layer 2d (§9.2) |
|---|---|---|
| When | **Every coaching turn** (`after_agent`) | **Once**, at the gate |
| Rubric | **`COACHING_QUALITY_RUBRIC`** — one, shared | **`PHASE_RUBRIC`** — one per phase |
| Grades | The coach's **process** | The **gate document** |

**Never point `DMAICGraderMiddleware` at a phase rubric, and never
point Layer 2d at `COACHING_QUALITY_RUBRIC`.** All rubric constants live in
`core/prompts.py` — read the criteria there. Coverage and tiers:
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §35, §36.

**Seven-step pattern on every computation tool call:** (1) educate on the
concept, (2) why now, (3) guide data preparation (check uploads via
`rag_lookup_evidence`), (4) run the tool, (5) interpret in plain language
(§13), (6) visualise with `propose_diagram` where applicable, (7) coach the
next move. **Step 1 is mandatory and most often skipped** — never assume the
Belt knows what a Cpk, a p-value or a control limit is. **A p-value with no
concept and no interpretation is a rubric failure.** Every SKILL.md must carry
the sequence for each tool in its `allowed-tools` (§8.3; §43.1).

**Show before asking is a rubric criterion** — a concrete completed example
per field, carried in each SKILL.md.

**Mechanism, both graders:** `grader` role, temperature 0.1 (§4.7);
`max_iterations=3`, then pass through **with a warning flag visible to the
Belt**; verdict per criterion (`GraderVerdict` → `list[CriterionVerdict]`,
§9.7); feedback **per criterion and specific**, never "try again"; Layer 2d is
**belt-level aware** (§9.7).

**Cross-phase criteria are checked deterministically** against the referenced
gate document in the store (§10.6); computation criteria by scanning
`artifacts["computation_results"]` for the `tool` entry.

**`on_evaluation` writes each iteration to `step_log`** (§10.3). Grader
internals stay **private to the middleware**, never on `PhaseState` or
`SupervisorState`. **The Belt does not see the grader loop.**

### 8.3 — `DMAICSkillsMiddleware` — progressive disclosure

**Custom, on `create_agent`. Not deepagents' `SkillsMiddleware`** (§4.4).
Skills: `agent-improve/skills/dmaic-{phase}-phase/SKILL.md`.

**Each skill's `allowed-tools` MUST match that phase's tool subset (§5.2).**

**Three levels:** (1) at startup, descriptions only — **under 2K tokens for
all five combined**; (2) full phase instructions on demand via a registered
`load_skill(name)` tool; (3) reference files when explicitly needed.
Backend: `FilesystemBackend` (`ContextHubBackend` deferred).

**Never confuse** development-workflow skills (`.claude/skills/`, Claude Code)
with runtime coaching skills (`agent-improve/skills/`, the coach).

### 8.4 — `SummarizationMiddleware` — context compression policy

**LangChain core, used as shipped** (settings in `nodes_common.py`). **Custom
compression functions are BANNED** — no `compress_messages()`, no
`conversation_context` builder.

**Facts do not live in `messages[]`.** Anything that must survive compression
lives in typed state or the store (§10.2); decisions survive as captured
fields (§10.1).

**Deprecated memory classes are BANNED:** `ConversationBufferMemory`,
`ConversationBufferWindowMemory`, `ConversationSummaryMemory`,
`ConversationEntityMemory`, `VectorStoreRetrieverMemory`,
`ConversationChain`.

### 8.5 — state injection — injection timing

*Canonical: ARCHITECTURE.md §19.1.*

**Custom · `before_agent` + `wrap_model_call` · position 1.** Prepends
project state at the **top** of the prompt: this phase's `artifacts`, prior
phases' gate documents from the store, phase requirements, and the missing
fields from `check_gate_status()`.

**`before_agent` composes once per turn; `wrap_model_call` only prepends —
a pure read, recomputing nothing.** Missing fields are computed at injection
time, never read from a stored list (§10.1). **Injecting in `messages[]`
append order is a violation.**

### 8.6 — Middleware that is deliberately NOT used

- **`HumanInTheLoopMiddleware`** — edited args can be silently overwritten
  and edit/reject break in subgraphs. Use graph-level `interrupt()` (§1.6, §9.1).
- **`LLMToolSelectorMiddleware`** — per-phase binding (§5.2) already bounds
  the tool count.
- **deepagents `RubricMiddleware` / `SkillsMiddleware`** — pre-1.0 (§4.4).

### 8.7 — `ModelRetryMiddleware` — the invisible-retry tier

**LangChain core, used as shipped:** `max_retries=2`, exponential backoff,
`wrap_model_call`. **The keyword is `max_retries`; `retries=` raises at
construction** — on `ToolRetryMiddleware` too. **Hand-written retry plumbing
is BANNED.**

**Distinct from the fallback chain (§4.8):** this retries **the same call**,
invisibly; the fallback chain **swaps the model**, and degraded mode is
visible.

**`ToolRetryMiddleware` is the second half of the tier, not a synonym** —
`max_retries=2`, `on_failure="continue"`, `wrap_tool_call`; it catches tool
failures `ModelRetryMiddleware` never sees. `on_failure="continue"` returns a
failure result the coach can work around instead of killing the graph.
**`RetryMiddleware` does not exist in LangChain 1.x — never write it.**

### 8.8 — `ContradictionDetectionMiddleware` — the §9.4 check

**Custom, `after_agent`. It reads a flag; it detects nothing itself:**

```python
def after_agent(self, state, runtime):
    flag = state["structured_response"].contradiction_flag
    if flag:
        raise HITLInterrupt(**flag)
```

**No store read, no LLM call, no field-name matching, no tolerance
threshold** (§9.4, §10.7). **Never reintroduce the mechanical dict
comparison** (`docs/_archive/DECISIONS.md` §R1).

### 8.9 — `CoherenceMiddleware` — validation Layer 2a

**Custom, `after_agent`, immediately inside the grader.** Layer 2a (§9.2):
one `coherence` call, temperature 0.1. **Fires every coaching turn**, which
is why it is middleware, not the `validation_stack` node.

**On failure: silent retry, max 2** (§9.3); on the third the turn degrades
and `DMAICGraderMiddleware` is skipped.

**Coherence is NOT a `COACHING_QUALITY_RUBRIC` criterion** — any rubric entry
for it is stale.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §19, §32, §36.*


## Never

*§14's bans that belong to this file — 6 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never write `RetryMiddleware` — the class does not exist in LangChain
  1.x. Model-call retries are `ModelRetryMiddleware`, tool-call retries
  are `ToolRetryMiddleware`, and they are not interchangeable (§8.7)
- Never hand-roll a retry loop around an LLM call — no try/except/sleep/counter
  around `.invoke()`. The middleware provides the wrap, the backoff and the
  counter (§0.24, §8.7)
- Never hand-roll the agent loop — `create_agent`, with the eight middlewares
  (§0.24, §4.4, §8.1)
- Never set `BeforeModelStateInjection` to the `before_model` hook — it is
  `before_agent`, once per turn, not once per model call (§8.1, §8.5)
- Never merge the three retry caps — `ModelRetryMiddleware` (2),
  `CoherenceMiddleware` (2) and the validation stack's shared gate cap (3)
  count different failure modes (§8.1, §9.2)
- Never treat Layer 2a as part of the `validation_stack` node — it fires
  every turn and lives in `CoherenceMiddleware` (§8.9, §9.2)
