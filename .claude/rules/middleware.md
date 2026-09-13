---
paths:
  - "agent-improve/backend/middleware/**"
---
# §8 — Middleware stack

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## 8. MIDDLEWARE STACK

### 8.1 — Eight middlewares, all on `create_agent`

**Canonical: ARCHITECTURE.md §19.** §19 owns the stack and its ordering rules;
this section reproduces them. The block below is generated from
`_build_executor()` in `backend/phases/nodes_common.py` by AST parse, not
transcribed — a reorder in the code shows up here as a diff.

**The list is NESTING order. The position numbers are EXECUTION order. For
`after_*` hooks the two are opposite.**

```python
middleware=[
    BeforeModelStateInjection(...),                             # 1
    DMAICSkillsMiddleware(...),                                 # 2
    SummarizationMiddleware(
        trigger=("tokens", 100_000), keep=("messages", 20)),    # 3
    ModelRetryMiddleware(max_retries=2),                        # 4
    ToolRetryMiddleware(max_retries=2, on_failure="continue"),  # 5
    DMAICGraderMiddleware(...),                                 # 6
    CoherenceMiddleware(...),                                   # 7
    ContradictionDetectionMiddleware(...),                      # 8
]
```

| # | Middleware | | Hook(s) it implements |
|---|---|---|---|
| 1 | `BeforeModelStateInjection` §8.5 | custom | `before_agent`, `wrap_model_call` |
| 2 | `DMAICSkillsMiddleware` §8.3 | custom | `before_agent`, `wrap_model_call` |
| 3 | `SummarizationMiddleware` §8.4 | core | `before_model` |
| 4 | `ModelRetryMiddleware` §8.7 | core | `wrap_model_call` |
| 5 | `ToolRetryMiddleware` §8.7 | core | `wrap_tool_call` |
| 6 | `DMAICGraderMiddleware` §8.2 | custom | `after_agent` |
| 7 | `CoherenceMiddleware` §8.9 | custom | `after_agent` |
| 8 | `ContradictionDetectionMiddleware` §8.8 | custom | `after_agent` |

Applying the three clauses to that list:

- **`before_*` fire 1 → 2 → 3** — `BeforeModelStateInjection`,
  `DMAICSkillsMiddleware`, `SummarizationMiddleware`.
- **`after_*` fire 8 → 7 → 6** — `ContradictionDetectionMiddleware`,
  `CoherenceMiddleware`, `DMAICGraderMiddleware`.
- **`wrap_*` nest 1 ⊃ 2 ⊃ 4 ⊃ 5** — `BeforeModelStateInjection`,
  `DMAICSkillsMiddleware`, `ModelRetryMiddleware`, `ToolRetryMiddleware`;
  position 1 is the outermost layer.

Five are custom, three are core.

**Three ordering clauses, not one.** LangChain states them separately. An
earlier revision of this section collapsed them into *"declaration order is
execution order for hooks of the same kind, so this order is binding"* — a
sentence that is true of `before_*`, **false of `after_*`**, and not even the
right shape for `wrap_*`.

| Hook kind | Ordering, relative to the declared list |
|---|---|
| `before_*` | first to last — **same** as declaration order |
| `after_*` | **last to first** — the **reverse** of declaration order |
| `wrap_*` | nested; the first declared wraps all the others |

Read off the installed `langchain` 1.3.16's own graph construction, not the
documentation alone — the reading is quoted in the commit that made this
correction. **Not reproduced here: `langchain/agents/factory.py` is the
framework's code and the framework owns it**, so a copy in this file would be
one more transcription to go stale. Re-derive it rather than trusting this
paragraph if it ever matters.

**`BeforeModelStateInjection` MUST be first, and the `before_*` clause is why.**
Project facts have to reach the top of the prompt before skills loading and
summarisation shape it; `before_*` fires first-to-last, so first in the list is
first to run. Listing it last, as an earlier revision did, defeats the ordering
rule §8.5 exists to enforce.

**`BeforeModelStateInjection`'s hook is `before_agent`, not
`before_model`.** State injection belongs at agent-loop start, once per
turn — `before_model` fires before every individual model call within a
turn, which re-injects the same project facts repeatedly and wastes
context. An earlier revision typed it `before_model`; that is corrected.

**Positions 6, 7 and 8 all fire `after_agent`**, so they execute in the reverse
of how they are declared: **declared** grader, coherence, contradiction and
therefore **executing** contradiction, coherence, grader.
`test_all_eight_positions_execute_in_the_ratified_order` asserts what executes
rather than what is listed — cite it; do not restate the order. **If
`CoherenceMiddleware` exhausts its retries, `DMAICGraderMiddleware` is skipped
for that turn** — deliberately: grading a response already known to be
incoherent spends a model call for a meaningless score. The skip travels
outward on the way out, which works only because coherence sits **inside** the
grader.

**Positions 4 and 5 do compete for a slot.** An earlier revision said they
"compete for no slot with the others; they are adjacent for readability, not
ordering" — false, and it is the same conflation. `wrap_*` hooks nest, so a
`wrap_*` middleware wraps everything declared after it. Since 6.3 positions 1
and 2 also implement `wrap_model_call`, so position 1 **encloses** position 4's
retry: the project-state block is composed and prepended once, and a retry
re-sends the built request rather than rebuilding it per attempt
(`test_position_1_wrap_encloses_position_4_retry`). Position 5 wraps tool calls
rather than model calls, so it is independent of the other three — independent
of *them*, not of position.

**The six named lifecycle hooks ARE the complete set** — `before_agent`,
`before_model`, `after_model`, `after_agent`, `wrap_model_call` and
`wrap_tool_call`, each with an `a`-prefixed async twin. An earlier revision
wrote that `AgentMiddleware` "also exposes `dynamic_prompt()`, `hook_config()`
and `configure_trace_policy()`" and that the set was therefore open. **It does
not.** Those three are module-level names in `langchain.agents.middleware` —
two decorators and a process-wide trace-policy setter — not members of
`AgentMiddleware` and not lifecycle hooks — `vars(AgentMiddleware)` on the
installed 1.3.16 returns the six, their six async twins, and `name`,
`state_schema`, `trace_policy`, `transformers`, and none of those three.
ARCHITECTURE.md §19 owns this and carries the check;
`docs/_archive/BIBLE_VERIFICATION_LOG.md` C-3, which asserted the opposite, is
withdrawn in place.

**Three independent retry caps, and they must not be merged:**
`ModelRetryMiddleware` 2 retries on transient API failure,
`CoherenceMiddleware` 2 retries on response quality, and the four-layer
validation stack's shared cap of 3 at the gate (§9.2). Three different
failure modes, three counters, no shared state.

**Prefer built-in middleware wherever it exists.** Custom middleware is
reserved for genuinely domain-specific logic.

### 8.2 — `DMAICGraderMiddleware` — coaching-quality grading

**Custom, on `create_agent`. Not deepagents' `RubricMiddleware`** (§4.4).

**THERE ARE TWO GRADERS IN THIS ARCHITECTURE. They are not redundant,
and confusing them is a violation.**

| | `DMAICGraderMiddleware` (this rule) | Validation stack Layer 2d (§9.2) |
|---|---|---|
| Where | Middleware, inside the executor | The `validation_stack` node |
| When | **Every coaching turn** (`after_agent`) | **Once**, at the gate boundary |
| Rubric | **`COACHING_QUALITY_RUBRIC`** — one, shared | **`PHASE_RUBRIC`** — five, one per phase |
| Grades | The coach's **process** | The **gate document** |
| Sees | One response | The complete field set |

**Never point `DMAICGraderMiddleware` at a phase rubric, and never
point Layer 2d at `COACHING_QUALITY_RUBRIC`.**

**`COACHING_QUALITY_RUBRIC`** — a single constant in `core/prompts.py`,
identical for all five phases:

```
- Coach must not accept vague or unmeasurable statements as captured fields
- Coach must not invent data, metrics, or values the Belt didn't provide
- Coach must not do the Belt's work (writing their problem statement for them)
- Coach must stay on the current phase's topic
- Coach must challenge weak inputs with specific follow-up questions
- Coach must reference methodology when guiding (not just opinion)
- Coach must show a concrete example of a completed answer before asking
  the Belt to produce theirs
- Coach must not provide external URLs from training data. When
  referencing methodology, retrieve via rag_lookup_methodology and weave
  the content into natural coaching voice
- Coach must not dump raw statistical output without explanation. When
  calling a computation tool, the coach must educate the Belt on the
  concept first, explain why it matters for their project, then run the
  tool
```

**Two criteria bind on every computation tool call**, and the coach
follows a **seven-step** pattern, every tool, every time:

| # | Step |
|---|---|
| 1 | **Educate on the concept** — what this *is*, plain language, real-world analogy, and what the output numbers will mean |
| 2 | **Explain why now** — why the Belt needs it at this point in their project |
| 3 | **Guide data preparation** — what format is needed; check uploads via `rag_lookup_evidence` |
| 4 | **Run the computation** — call the tool |
| 5 | **Interpret their result** — plain language, no jargon (§13) |
| 6 | **Visualise** — `propose_diagram` where applicable |
| 7 | **Coach the next move** — what it means for the project |

**Step 1 is mandatory and is the one most often skipped.** Never assume
the Belt knows what a Cpk, a p-value or a control limit *is*. Teach the
concept and say what the numbers will mean **before** producing any.

**Returning a p-value with no concept and no interpretation is a rubric
failure**, not a style preference. A Belt handed `t_statistic: 4.23,
p_value: 0.001` has a number they cannot act on and cannot defend at a
gate. Because this grader fires **every turn**, the dump is caught before
the Belt sees it.

**Every SKILL.md must carry the seven-step sequence for each computation
tool in its phase's `allowed-tools`** (§8.3). Design detail and worked
per-tool openings: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §43.1.

**Show before asking is also a rubric criterion.** For every field, the
coach shows a concrete example of a completed answer, explains why it
works, then invites the Belt to build theirs in the same shape. Each
SKILL.md carries the example per field.

**Why both exist.** The middleware catches coaching-process failures in
real time — a coach that accepts "poor morale" as a root cause is
corrected before the Belt sees the response, preventing eight further
turns on a weak foundation. The validation node catches document-product
failures a per-turn check cannot see: four Analyse fields can each look
sound while the root cause discusses "error rate" and the baseline it
references is "cycle time." Cross-field and cross-phase consistency is
only visible once the document is complete.

**Mechanism, both graders:**

- Hook: `after_agent` (middleware) / node logic (Layer 2d)
- Model: `grader` role, temperature 0.1 (§4.7)
- `max_iterations=3`. On `max_iterations_reached`, output passes
  through **with a warning flag visible to the Belt**.
- Verdict is per criterion, not overall: `GraderVerdict` carries a
  `list[CriterionVerdict]`, each with `criterion`, `tier`, `status`
  (`"pass" | "warning" | "fail"`) and `feedback` (§9.7).
- Feedback injected back to the coach is **per criterion and specific**
  — never "try again."
- **Layer 2d is belt-level aware** — reads `belt_level` from the case
  record and suppresses Black-Belt-only recommendations for a Green Belt
  (§9.7).

**Rubric management.** Five `PHASE_RUBRIC` constants in
`core/prompts.py`, one per phase, plus the single
`COACHING_QUALITY_RUBRIC`. Layer 2d receives the phase-appropriate
rubric based on `current_phase`. Rubrics evolve from production
experience **without changing the grader mechanism** — that separation
is the point.

The ratified rubrics cover: Define (problem_statement, voc_summary,
business_case, project_scope, team, goal_statement), Measure
(baseline_mean, baseline_sigma, measurement_system_validated,
data_collection_plan, stability), Analyse (root_cause_statement,
root_cause_validation, causal_hypothesis, ruled_out_causes), Improve
(selected_solution, solution_linked_to_root_cause, pilot_result,
implementation_plan), Control (control_plan, sustainability_check,
post_improvement_metrics, improvement_delta, financial_impact_verified,
handover_documented, lessons_learned, transferability). Each criterion
carries its tier (§9.7). Full coverage in `../AGENTIC_ARCHITECTURE_REFERENCE.md` §36;
the tier table is `../AGENTIC_ARCHITECTURE_REFERENCE.md` §35.

**Three criteria are verified deterministically, not by judgment.**
`causal_hypothesis`, `solution_linked_to_root_cause` and
`post_improvement_metrics` are cross-phase reference dicts (§10.6); the
grader reads the referenced phase's gate document from the store and
checks the named field carries the named value. Criteria that depend on
a computation are checked the same way, by scanning
`artifacts["computation_results"]` for the relevant `tool` entry.

**Audit trail integration.** The `on_evaluation` callback writes each
grading iteration to `step_log` (§10.3). Grader internals — iteration
count, accumulated evaluations, attempt tracking — stay **private to
the middleware** and never reach `PhaseState` or `SupervisorState`.

**The Belt does not see the grader loop.** It runs at step 2 of the
nine-step gate, before the interrupt (§9.1).

### 8.3 — `DMAICSkillsMiddleware` — progressive disclosure

**Custom, on `create_agent`. Not deepagents' `SkillsMiddleware`** (§4.4).

Five phase skills under `agent-improve/skills/`, following the
agentskills.io SKILL.md standard:

```
dmaic-define-phase/SKILL.md
dmaic-measure-phase/SKILL.md
dmaic-analyse-phase/SKILL.md
dmaic-improve-phase/SKILL.md
dmaic-control-phase/SKILL.md
```

**Each skill's `allowed-tools` MUST match that phase's tool subset in
§5.2.** Skill and tool binding must not drift apart.

**Progressive disclosure — three levels:**

| Level | When | What loads |
|---|---|---|
| 1 | Startup | Skill descriptions only — **under 2K tokens for all five combined** |
| 2 | On demand | Full phase instructions, when the coach enters that phase |
| 3 | On demand | Reference files, when explicitly needed |

Level 2 is reached by the coach calling a registered `load_skill(name)`
tool.

**Storage backend: `FilesystemBackend`** — git-versioned alongside the
code, so a skill change is reviewable in the same PR as the code that
depends on it. `ContextHubBackend` is deferred.

**Two distinct kinds of skill exist in this repository** and must not
be confused:
- **Development-workflow skills** under `.claude/skills/` — consumed by
  Claude Code (e.g. `/verify-current-version`)
- **Runtime coaching skills** under `agent-improve/skills/` — consumed
  by the coach

### 8.4 — `SummarizationMiddleware` — context compression policy

**LangChain core, used as shipped.**

```python
SummarizationMiddleware(
    model="azure/operational-model",       # gpt-4o-mini for cost
    trigger=("tokens", 100_000),           # ~78% of gpt-4o's 128k window
    keep=("messages", 20),                 # preserve the last 20 turns raw
)
```

**Custom compression functions are BANNED.** Do not hand-write
`compress_messages()` or a `conversation_context` builder — this
middleware provides the trigger, the summarisation call, and the
message-list replacement.

**The policy that makes prose summarisation safe:** facts do not live
in `messages[]`. Anything that must survive compression lives in typed
state:

| Lives in | Field |
|---|---|
| `SupervisorState` | `current_phase`, `phase_index`, `gate_passed` — orchestration only |
| `PhaseState` | `artifacts`, `draft`, `belt_edits`, `step_log`, `citations`, `uploads`, `validator_feedback`, `final` |
| Store | Cross-phase gate documents (§10.2) |

Summarising *conversation* into prose is correct — that is what
conversation is. Summarising *facts* into prose is the failure this
policy prevents.

**Decisions survive compression as captured fields, not as a decision
list.** When the Belt commits a decision it arrives via
`CoachingResponse.fields_captured` and is approved at a gate, which puts
it in `artifacts` and then the store
— all three outside `messages[]`. That is why no `key_decisions` field
is needed here (§10.1).

**Deprecated memory classes are BANNED:** `ConversationBufferMemory`,
`ConversationBufferWindowMemory`, `ConversationSummaryMemory`,
`ConversationEntityMemory`, `VectorStoreRetrieverMemory`,
`ConversationChain`. All are scheduled for removal in LangChain 2.0.
The replacement is checkpointer (thread-scoped) + store (cross-thread)
+ this middleware.

### 8.5 — state injection — injection timing

*Canonical: ARCHITECTURE.md §19.1.*

**Custom · `before_agent` + `wrap_model_call` · position 1.** Prepends
structured project state at the **top** of the prompt, ahead of the
conversation: captured fields (this phase's `artifacts` plus prior
phases' gate documents from the store), current phase requirements, and
the missing fields reported by `check_gate_status()`.

**Two hooks, and the division of labour is the design.** `before_agent`
composes the block once per turn; `wrap_model_call` prepends the composed
block to each request and recomputes nothing — a pure read, or the
once-per-turn guarantee would be decorative. Both are defined on the
class rather than inherited, so both are its hooks:
`'wrap_model_call' in vars(BeforeModelStateInjection)` is `True`. This
heading read *"`before_model` state injection"* until 2026-09-12, naming
a hook the class does not implement and hiding the one it does.

**Missing fields are computed at injection time, never read from a
stored list.** The middleware derives them the same way the gate does,
so the prompt and `DMAICGateValidator` cannot disagree (§10.1).

Models weight earlier prompt content more heavily. Injecting project
facts *after* the Belt's message lets the response drift toward the
Belt's framing rather than the project's established state.

**Injecting in `messages[]` append order is a violation.** There is no
"just add it to the history" option.

### 8.6 — Middleware that is deliberately NOT used

| Middleware | Why not |
|---|---|
| `HumanInTheLoopMiddleware` | **Two confirmed bugs hit our exact use case.** Edited tool-call args can be silently re-overwritten by the agent re-attempting the original call; and edit/reject are broken in subgraph contexts, where only approve is reliable. Both would silently discard a Belt's correction. Use graph-level `interrupt()` (§1.6, §9.1). |
| `LLMToolSelectorMiddleware` | Per-phase binding (§5.2) already keeps every coach at 8–15 tools. Adding a selector LLM spends a model call solving a problem solved structurally. |
| deepagents `RubricMiddleware` / `SkillsMiddleware` | Pre-1.0 dependency (§4.4). |

### 8.7 — `ModelRetryMiddleware` — the invisible-retry tier

**LangChain core, used as shipped, ADOPTED.** `max_retries=2` with
exponential backoff, on the `wrap_model_call` hook. It wraps each model
call and silently retries transient timeouts and rate limits.

**The keyword is `max_retries`, not `retries`.** `retries=` does not
exist on this class and raises at construction. The full verified
signature is:

```python
ModelRetryMiddleware(*, max_retries=2, retry_on=default_retry_on,
                     on_failure='continue', backoff_factor=2.0,
                     initial_delay=1.0, max_delay=60.0, jitter=True)
```

`ModelRetryMiddleware` and `ToolRetryMiddleware` share a parameter
vocabulary, which is exactly the situation where remembering one and
inferring the other goes wrong — and it did: `retries=` sat in this
stack, uncaught, from adoption until 2026-08-21
(`docs/_archive/BIBLE_VERIFICATION_LOG.md` C-1). (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

**Hand-writing retry plumbing is BANNED.** Do not write
try / except / sleep / counter loops around an LLM call — this
middleware provides the wrap, the backoff, and the attempt counter.

**Its tier is distinct from the fallback chain (§4.8), and the two must
not be conflated:**

| | `ModelRetryMiddleware` | Fallback chain (§4.8) |
|---|---|---|
| Handles | Mechanical failure — the network flaked | Service-level failure |
| Action | Retry **the same call** | **Swap the model**: gpt-4o → gpt-4o-mini → cache → degraded |
| Visible | Never | Degraded mode is visible to the Belt |

This is the invisible-retry tier named in §9.3's self-healing
hierarchy: mechanical, never a coaching event.

**`ToolRetryMiddleware` is the second half of that tier, and is a
different middleware — not a synonym.** LangChain core, used as shipped,
`max_retries=2`, `on_failure="continue"`, on the `wrap_tool_call` hook.

| | `ModelRetryMiddleware` | `ToolRetryMiddleware` |
|---|---|---|
| Hook | `wrap_model_call` | `wrap_tool_call` |
| Catches | Azure OpenAI rate limits, timeouts, transient 5xx | Tool execution failures — Azure Search timeouts, computation tool errors |
| Wraps | Each model call | Each individual tool invocation |

A failed retrieval call is not a failed model call; `ModelRetryMiddleware`
never sees it. Both are needed and neither substitutes for the other.

**`on_failure="continue"` is what keeps the coaching loop alive.** When
retries are exhausted the tool returns a failure result the coach can
read and work around, rather than raising and killing the graph
mid-session.

**The class is `ToolRetryMiddleware`.** `RetryMiddleware` does not exist
in LangChain 1.x — never write it.

### 8.8 — `ContradictionDetectionMiddleware` — the §9.4 check

**Custom, `after_agent`, position 6.** Implements the mid-phase conflict
detection of §9.4. **It reads a flag; it does not detect anything itself.**

```python
def after_agent(self, state, runtime):
    flag = state["structured_response"].contradiction_flag
    if flag:
        raise HITLInterrupt(**flag)
```

**No store read. No LLM call. No field-name matching.** Detection is done by
the coach in the response call that already runs every turn, and arrives as
`CoachingResponse.contradiction_flag` (§10.7). **No tolerance threshold**, per
§9.4.

**The mechanical dict comparison this replaced could not work** — it read
`store.get(..., current_phase)`, which `gate_apply` does not write until phase
end, and it matched on field names where 38 of 41 fields are unique to one
phase. Full analysis: `docs/_archive/DECISIONS.md` §R1. **Never reintroduce the
comparison.**

**Why middleware rather than logic inside the executor node:** the check
polices the executor's own output, so it does not belong to the thing it
polices. As middleware it is a named, LangSmith-visible step
(`ContradictionDetectionMiddleware.after_agent`) and the executor node
stays responsible only for coaching.

### 8.9 — `CoherenceMiddleware` — validation Layer 2a

**Custom, `after_agent`, position 7 — immediately before the grader.**
Implements Layer 2a of the validation stack (§9.2). One LLM call,
`coherence` role, temperature 0.1: is this a real, conclusive statement?
Is it parroting the Belt's own words? Is it on-topic for this phase?

**Layer 2a fires every coaching turn**, which is why it is middleware and
not part of the `validation_stack` node — that node runs once, at the
gate. Layers 2b–2d live there; 2a lives here. One conceptual stack, two
mechanisms (§9.2).

**On failure: Level 1 silent retry, max 2** (§9.3). The Belt never sees a
failed coherence response. On the third failure the turn degrades and
`DMAICGraderMiddleware` is skipped.

**Coherence is NOT a `COACHING_QUALITY_RUBRIC` criterion.** It moved out
of the rubric when this middleware was added. `DMAICGraderMiddleware`
grades coaching *process* only — seven-step computation pattern,
show-first, citations, no external URLs. Any rubric entry for coherence
is stale (§8.2).

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
