# Agent Improve — Architecture & Design Document
**Agentlean Platform · DMAIC Improvement Agent**
Version 2.2.16 · August 2026
Status: v2.2 architecture ratified · refactor in progress (Step 2.2 complete;
Step 3.6 index schema rename applied; state design closed — §4;
node names, tool binding and output schemas closed — §3.2.1, §3.3.2, §4.10;
eBook gaps closed — §4.10.5–§4.10.7, §3.4.2)

### Change log — v2.2.16 (2026-08-21)

Four facts propagated from `REFACTORING_AGENT_IMPROVE.md`, which had moved
ahead of this document. Same principle as the §44 boundary ruling: **the
design document cannot lag the document it is derived from.** No new
decisions — every item was already ratified and logged.

| # | Change | Sections |
|---|---|---|
| 1 | `PhaseState` 15 → **17 fields** (3 plumbing + 14 content). `hop_results` and `synthesis_output` added; `coaching_plan` retyped to `Optional[CoachingPlan]` | §4.2 |
| 2 | Middleware stack 5 → **8**. `ToolRetryMiddleware`, `ContradictionDetectionMiddleware`, `CoherenceMiddleware` added; `BeforeModelStateInjection` hook corrected `before_model` → **`before_agent`** | §3.4, §5 folder structure, §15 Step 5, §16 summary |
| 3 | `improve_evidence_index` gains **`phase`** and **`uploaded_at`**; `rag_lookup_evidence` gains an optional, default-off `phase` filter and regains `order_by` | §7.2, §8.1 |
| 4 | `improve_case_index.embedding` → **`content_vector`** ratified; "asymmetry is safe" no longer reads as an argument against the rename | §7.3, §7.4 |

**Two corrections found while propagating, both internal to this document:**

- **§3.7 named `DMAICGraderMiddleware` as validation Layer 2d.** It is not —
  Layer 2d runs in the `validation_stack` node against `PHASE_RUBRIC`, while
  `DMAICGraderMiddleware` is middleware position 8 running against
  `COACHING_QUALITY_RUBRIC` every turn. §3.4.1 on the same page already drew
  this distinction correctly, so the document contradicted itself.
- **Layer 2a's implementation was unstated.** It fires every turn, which the
  gate-boundary `validation_stack` node cannot do; it is `CoherenceMiddleware`.
  The four-layer stack is one concept spanning two mechanisms, and §3.7 now
  says which layer is which.

**Both Azure schema changes are documented, not applied.** §7.2 and §7.3 are
marked pending reindex, and code must use the live field names until then.

---

## 0. How to Read This Document

v2.2 is a **ground-up rewrite**, not an amendment. It aligns this
document with every decision ratified in the EDUCATIONAL.md
architectural review.

| Document | Answers | Binding? |
|---|---|---|
| CLAUDE.md v2.2 | **What the rule is** | Yes — quoted in every prompt |
| ARCHITECTURE.md (this file) | **How the system is shaped** | Yes — component design, contracts, sequencing |
| REFACTORING_AGENT_IMPROVE.md | **Why the decision was made** | No — evidence and rationale |

Where this document and CLAUDE.md describe the same thing, CLAUDE.md
states the rule and this document states the design. Neither restates
the other's job.

### 0.1 Anchor changes from v2.1.1

Existing cross-references from the review log and code comments land
as follows:

| Old reference | Now |
|---|---|
| §B2 "tool-calling coach agent" | §3.3 — `phase_executor` built with `create_agent` |
| §3.2 "bound tools list" | §3.3 (executor construction) and §8 (the tool tables) |
| §3.3 "coach subgraph" | §3.2 — the phase subgraph diagram |
| §7 "indexes" | §7 — unchanged anchor, now carries the **canonical schemas** |
| §15 "migration sequence" | §15 — unchanged anchor |

### 0.2 Canonical ownership of shared facts

To prevent the two governance documents drifting:

| Fact | Canonical home |
|---|---|
| **Azure AI Search index schemas** | **§7 of this document** |
| Rule numbers cited by the drift registry | CLAUDE.md §0.2 |
| Canonical tool names and signatures | CLAUDE.md §5.1 |
| Rubric and constraint text | CLAUDE.md §8.2 / §9.2 |

---

## 1. Overview

Agent Improve is the second agent in the Agentlean platform. It guides
cross-functional teams through structured DMAIC (Define, Measure,
Analyse, Improve, Control) Lean Six Sigma improvement projects.

**Core principle**: Agent Improve must work for a team with no Six
Sigma qualification. The AI guides every step in plain language. No
methodology jargon reaches the user unless they ask.

**Architectural principle (v2.2)**: Two state schemas, one runtime,
two persistence systems. The LangGraph compiled graph IS the
orchestrator. Routes are thin transport. Coaching strategy is explicit
and inspectable, never implicit in a prompt.

| Property | Value |
|---|---|
| Backend port | 8020 |
| Repo | `vpangalis/agentlean` → `agent-improve/` |
| Stack | Python 3.11 · FastAPI · LangGraph 1.2.10 · LangChain 1.x · Azure OpenAI · Azure AI Search · Azure Blob · Azure Cache for Redis |
| Persistence | Checkpointer + Store (Blob now → PostgreSQL before production) |
| Tracing | LangSmith (mandatory) |
| Protocol layer | **None. MCP is architecturally excluded (§1.2).** |

### 1.1 What changed from v2.1.1

| Area | v2.1.1 | v2.2 |
|---|---|---|
| LangGraph | 0.2+ (stated), 1.1.10 (pinned) | **1.2.10** — required for subgraph `checkpoint_ns` and native reliability primitives (floor ≥1.2.6) |
| Phase subgraph | 5 nodes, linear with one conditional | **6 nodes, conditional edges and cycles** (§3.2) |
| Coach | Bare LLM with 7 bound tools | **`create_agent`, 4 middlewares, per-phase tool subset** (§3.3, §3.4, §8) |
| Retrieval | 2 tools, single query | **3 tools, multi-query + RRF, metadata filters** (§7.4, §8.1) |
| Computation | None | **20 tools, bound per phase** (§8.2) |
| Gate | Interrupt → approve | **Nine steps, two nodes, four validation layers** (§3.6, §3.7) |
| Cross-phase data | Parent state | **Store-mediated boundary mappers** (§4.3, §6.3) |
| Phase routing | `phase_router` node | **Static edges** (§3.1) |
| Reliability | Retry ad hoc | **Timeouts, `error_handler=`, circuit breakers, 4-level fallback** (§9) |
| `improve_case_index` | Out of scope | **Active — `rag_lookup_case_history`** (§7.3) |

### 1.2 The data architecture principle

**`improve_evidence_index` is the only channel through which external,
real-world data enters AgentLean.**

Agent Improve, Agent Resolve, and Agent Flow will never use MCP or any
other protocol to connect to a live system. Users upload the data they
collect; the agent's job includes coaching them on what to collect and
how to structure it.

Three architectural consequences:

1. **Data-collection coaching is a first-class product surface**, not
   a workaround for missing integrations. Phase skills (§8.4) carry
   guidance on what to upload.
2. **Belt data-collection discipline is what the system's grounding
   depends on.** There is no automated substitute.
3. **No fallback path fetches a number the Belt did not provide.**
   The system asks; it does not reach.

The `@tool` decorator handles all tool composition. Cross-agent access
(Agent Improve reading Agent Resolve's indexes) is a Python import
from a shared module, read-only.

---

## 2. Design Principles

### 2.1 Plain language first
The AI translates Six Sigma into plain English. Technical terms are
hidden until explicitly requested.

### 2.2 Every data request comes with a collection guide
When the coach asks for data it explains what, how, and shows a
concrete example with column names.

### 2.3 Source citation is mandatory and transparent
Every AI suggestion carries `agent_origin`, `index_name`,
`document_id`, `relevance_summary`. Methodology retrieval additionally
surfaces `source_file` and `page_number` — "this came from page 47 of
the BB eBook."

### 2.4 Phase gates are one-way doors — with one defined exception
Once a gate passes and the phase record commits, that phase is locked.
The **only** way back is the re-approval cascade (§3.8), which is
deliberately heavy: it makes the affected phase and every downstream
phase provisional, and runs compensating actions against external
systems.

### 2.5 Multiple parallel cases from day one
Each case has its own `IMPR-YYYY-NNN` id, its own checkpoint thread,
its own case blob, its own state.

### 2.6 The graph is the orchestrator
Routes do not orchestrate. Routes invoke the compiled graph. All
dispatch, conditional logic, gating, and escalation live inside the
graph.

### 2.7 Planning is explicit, never implicit in a prompt
Coaching strategy lives in a structured plan object produced by a
planner node, not buried in a system prompt. This is what makes
coaching inspectable, testable, and auditable.

### 2.8 Transparency is the default; silence is the narrow exception
The Belt sees what the system is doing and participates in fixing it.
The single exception is a coherence failure mid-turn, where showing the
Belt that the AI produced gibberish adds no value and erodes trust.
Everything else — constraint failures, completeness, quality, value
contradictions — is visible and collaborative (§3.7).

### 2.9 Gate quality is a data integrity guarantee
Each phase consumes the previous phase's structured output. A problem
statement without a measurable baseline produces a Measure phase that
cannot establish a valid sigma level, which produces an Analyse phase
that cannot validate root causes. Gate validation is not bureaucracy —
it is the guarantee that downstream phases are operating on real
inputs.

---

## 3. Agent Architecture

### 3.1 Three levels, and the supervisor graph

The architecture is a **Planner-Executor pair applied recursively**.
At every non-leaf level a Planner reasons and an Executor dispatches.
The recursion stops at leaf tools, which are plain functions.

| Level | Planner | Executor | Dispatches to |
|---|---|---|---|
| 1 — Global | **Deterministic gate-checker** — reads `gate_passed`. No LLM. | Static edges | Phase subgraphs |
| 2 — Phase | `phase_planner` (LLM) | `phase_executor` (`create_agent`) | Leaf tools |
| 3 — Leaf | — | — | Tools are functions, not pairs |

```
supervisor_graph                     thread_id = case_id ("IMPR-2026-FS1")
                                     checkpointer + store attached HERE ONLY
  START
    │  add_edge(START, "define")
    ▼
 ┌────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐   ┌─────────┐
 │ define │──▶│ measure │──▶│ analyse │──▶│ improve │──▶│ control │──▶ END
 └────────┘   └─────────┘   └─────────┘   └─────────┘   └─────────┘
   static        static        static        static        static
    edge          edge          edge          edge          edge
      │             │             │             │             │
      └─────────────┴──────┬──────┴─────────────┴─────────────┘
                           │  conditional edge on gate_attempts
                           ▼
                  ┌────────────────────┐
                  │ escalation_subgraph│
                  └────────────────────┘

Each phase subgraph:
  · compiled WITHOUT a checkpointer and WITHOUT a store
  · gets its own auto-managed checkpoint_ns from LangGraph
  · owns its own interrupt
```

**Why static edges between phases.** Apply the decision test: *"Could
this transition vary at runtime?"* → dynamic. *"Always exactly once, in
this order?"* → static. DMAIC phase order is fixed, so there is nothing
to reason about. The `phase_router` node of v2.1.1 is deleted; an LLM
call to choose the next phase would be cost and latency purchasing no
decision.

**`Command` routing is used inside phase subgraphs**, where step order
genuinely is data-dependent. **Static edges and `Command` are never
mixed from the same node** — both paths execute, silently.

**Threading model.** One `thread_id` per project. LangGraph assigns
each subgraph its own `checkpoint_ns` within that thread. Per-subgraph
or concatenated thread ids (`{case_id}-define`) cause duplicate storage
and state-persistence problems, and are prohibited.

### 3.2 The phase subgraph — six nodes, conditional edges, cycles

**A phase subgraph is not a pipeline.** It has five functional stages;
the gate stage splits into two nodes (collection and application), so
six nodes total.

```
                     ┌──────────────────────────────────────────────┐
                     │                                              │
                     ▼                                              │
              ┌─────────────┐                                       │
   START ────▶│phase_planner│◀──────────────────────────┐           │
              └──────┬──────┘                           │           │
                     │ coaching_plan                    │           │
                     │ (structured — §3.5)              │ not clean │
                     ▼                                  │           │
              ┌─────────────┐                           │           │
              │phase_executor│  create_agent            │           │
              │              │  ReAct loop, ≤5 hops     │           │
              │  ┌────────┐  │  recursion_limit=11      │           │
              │  │ tools  │  │  7 universal +           │           │
              │  │ 8–15   │  │  phase computation       │           │
              │  └────────┘  │                          │           │
              └──────┬───────┘                          │           │
                     │ draft (dict)                     │           │
                     ▼                                  │           │
             ┌────────────────┐                         │           │
             │ mid-phase diff │  contradiction check    │           │
             │ (§3.8)         │  vs prior gates         │           │
             └───────┬────────┘  no LLM call            │           │
                     │                                  │           │
        ┌────────────┴─────────────┐                    │           │
        │ conditional edge         │                    │           │
        │                          │                    │           │
   contradiction?             field complete?           │           │
        │ yes                      │ no ────────────────┘           │
        ▼                          │ yes                            │
  ┌───────────┐                    │                                │
  │ interrupt │                    │ more fields? ──────────────────┘
  │ (mini-gate)│                   │ (field_index++, back to planner)
  └───────────┘                    │ all fields captured
                                   ▼
                       ┌─────────────────────┐
                       │ validation_stack    │  §3.7 — four layers
                       │  2a coherence       │  cheapest first
                       │  2b field presence  │  shared cap: 3 attempts
                       │  2c constraints     │  (gate_attempts)
                       │  2d PHASE_RUBRIC    │
                       └──────────┬──────────┘
                          fail    │    pass
                     ┌────────────┘          ▼
                     │             ┌──────────────────┐
                     │             │ gate_review      │  interrupt()
                     │             └────────┬─────────┘  Belt sees fields
                     │                      │
                     └──▶ back to planner   │ Command(resume=...)
                          (validator_       ▼
                           feedback)   ┌──────────────────┐
                                       │ gate_apply       │
                                       │ · apply edits    │
                                       │ · policy advisory│
                                       │ · assemble gate  │
                                       │   document       │
                                       │ · store.put()    │
                                       │ · final = doc    │
                                       └────────┬─────────┘
                                                ▼
                                               END
                                       (parent's static edge
                                        advances the phase)
```

**The five nodes are `planner`, `executor`, `validation_stack`,
`gate_review`, `gate_apply`.** Revision is an *edge* — the validation
stack routes back to the planner with accumulated `validator_feedback`
— not a node. There is no `policy_advisory` node and no `revise` node;
both names appeared in earlier revisions and are retired (§3.3.1).

**The planner fires many times per phase, not once.** After each
executor step, control returns to the planner to decide whether to
keep coaching the current field, advance to the next, or trigger the
gate. That cycle is why LangGraph rather than a DAG engine is the
runtime.

**The two-level cycle.** Level 1 is the phase chain
(Plan → Execute → Review → Revise, where Review is the gate
interrupt). Level 2 is the per-field cycle nested inside Level 1
Execute — plan the coaching action, run the coaching LLM and
extraction, check the captured field, loop or advance. For Define's six
required fields, Level 2 fires roughly 6–10 times inside a single
Level 1 Execute.

**Leaf tools are not nodes.** Retrieval, templates, diagrams, gate
status and computation are passed to the executor through `tools=`.
From the subgraph's perspective the executor is one node; from inside
it, several tools can fire per invocation.

**Gate validation and the policy advisory are NOT leaf tools.** The
validation stack is its own node, reached by an edge after the executor
finishes; the policy advisory is logic inside `gate_apply`. See §3.3.2.

#### 3.2.1 Node names — two retired, and why it mattered

| Retired name | Ratified | The problem it caused |
|---|---|---|
| `policy_advisory` (node 3) | **`validation_stack`** | The four-layer stack (§3.7) was absent from the node list entirely, so the subgraph as drawn had no validation. The policy advisory is not a node at all |
| `revise` (node 5) | **`gate_apply`** | A different name *and* a much smaller scope. `gate_apply` runs the policy advisory (step 6), processes approval (step 7), assembles the gate document and writes it to the store (§3.6.1) |

`gate_review` was correct throughout and is unchanged. Neither retired
name may reappear in a node list, an `add_node` call, or an edge.

### 3.3 Inside `phase_executor` — `create_agent` with per-phase tools

```python
executor = create_agent(
    model=get_llm("coach"),                          # operational-premium
    tools=UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase],
    response_format=CoachingResponse,                # §4.10 — per-turn, not the gate document
    middleware=[                                      # §3.4 — order is execution order
        BeforeModelStateInjection(...),               # before_model  — 1st
        DMAICSkillsMiddleware(...),                   # before_agent
        SummarizationMiddleware(...),                 # before_model
        ModelRetryMiddleware(retries=2),              # wrap_model_call
        DMAICGraderMiddleware(...),                   # after_agent
    ],
    prompt=PHASE_COACH_PROMPT[phase],
)
```

**`response_format` carries `CoachingResponse`, not a phase Output
schema.** The executor runs once per coaching turn; the gate document is
assembled once per phase, at `gate_apply`. Putting `DefineOutput` here
would ask the coach to emit a complete gate document on every turn,
which it cannot do and should not try. Detail in §4.10.

The executor is a **ReAct agent within the constrained scope of a
single phase**. It reasons about which tool it needs, calls it,
observes, and continues.

**Hop cap.** LangGraph counts steps, not hops. Each hop is two steps
(LLM node → tool node) plus one final synthesis step:

```
recursion_limit = 2 × max_hops + 1 = 2 × 5 + 1 = 11
```

```python
await graph.ainvoke(
    state,
    config={"recursion_limit": 11,
            "configurable": {"thread_id": case_id}},
)
```

`GraphRecursionError` is caught in the executor and turned into a
partial answer for the Belt. Hitting the cap is a **monitoring
signal** — it means the system prompt is encouraging too-broad
exploration, or the question warrants `operational-premium` for that
turn.

**Model tiering inside the loop.** Intermediate multi-hop retrieval
runs on `operational-model` (gpt-4o-mini); only the final synthesis
runs on `operational-premium` (gpt-4o). gpt-4o-mini is roughly 15×
cheaper, and this is the single largest cost lever in the design.

**Binding tools directly onto a bare LLM in a phase executor is an
architectural violation** — it bypasses the middleware stack.

#### 3.3.2 What is bound to the executor, and what is not

**Passed via `tools=`** — the universal seven (§8.1) plus that phase's
computation tools (§8.2). Nothing else.

**NOT tools, and never to be added as tools:**

| Component | What it actually is | Why not a tool |
|---|---|---|
| Validation stack | A **separate node**, reached by an edge after the executor finishes | Making it a tool puts "should I be validated?" in the coach's hands, which is backwards — the coach is the thing being validated |
| Policy advisory | **Logic inside `gate_apply`** | It fires after the Belt reviews and edits (step 6 of §3.6). At that moment the coach is no longer in the loop, so there is nothing for it to be a tool of |
| `record_field` | **Retired** — replaced by `response_format=CoachingResponse` | §4.10 |

Earlier revisions listed the gate validator and a "policy advisory
tool" among the executor's bound tools. Both were wrong, and the
validation-stack error was the more serious of the two: it left the
subgraph with no node that runs the four layers.

### 3.4 The middleware stack

**Eight middlewares** on every phase executor, built on the six
`AgentMiddleware` hooks. **Declaration order is execution order** for
hooks of the same kind, so the table below is the order in code.

| Order | Middleware | Hook | Purpose | Source |
|---|---|---|---|---|
| 1 | `BeforeModelStateInjection` | `before_agent` | Prepend structured project state at the top of the prompt | **Custom** |
| 2 | `DMAICSkillsMiddleware` | `before_agent` + registered tool | Progressive disclosure of phase coaching instructions | **Custom** |
| 3 | `SummarizationMiddleware` | `before_model` | Context compression for long coaching sessions | LangChain core |
| 4 | `ModelRetryMiddleware` | `wrap_model_call` | Invisible retry on transient **model API** failures | LangChain core |
| 5 | `ToolRetryMiddleware` | `wrap_tool_call` | Invisible retry on **tool execution** failures | LangChain core |
| 6 | `ContradictionDetectionMiddleware` | `after_agent` | Deterministic §3.8 check — captured field vs gate-approved value | **Custom** |
| 7 | `CoherenceMiddleware` | `after_agent` | Layer 2a coherence — real, conclusive, on-topic, not parroting | **Custom** |
| 8 | `DMAICGraderMiddleware` | `after_agent` | Coaching **process** quality against `COACHING_QUALITY_RUBRIC` | **Custom** |

**State injection runs first, deliberately, and its hook is
`before_agent`.** An earlier revision listed `BeforeModelStateInjection`
last and typed it `before_model`. Both were wrong. Declaration order is
execution order, so listing it last placed the project's established
facts *after* skills loading and summarisation had already shaped the
prompt. And state injection belongs at agent-loop start, not before every
individual model call within a turn — `before_agent` fires once per turn,
`before_model` fires per model invocation.

**Positions 6, 7 and 8 all fire `after_agent`** and therefore run in
declaration order: contradiction check, then coherence, then grader.
**If `CoherenceMiddleware` fails and its retries exhaust,
`DMAICGraderMiddleware` is skipped for that turn** — deliberately, since
grading a response already known to be incoherent spends a model call to
produce a meaningless score.

Positions 4 and 5 sit on `wrap_*` hooks and compete for no slot with
anything else; they are adjacent for readability, not for ordering.

**How the stack grew from four to eight**, and why no addition is
redundant:

| Added | Why nothing already in the stack covers it |
|---|---|
| `ModelRetryMiddleware` | Nothing else retried a failed model call. Distinct from the §9.3 fallback chain, which *swaps the model* rather than retrying the same call |
| `ToolRetryMiddleware` | A failed Azure Search call is not a failed model call — different hook, different failure mode. `on_failure="continue"` returns a failure result the coach can react to instead of killing the graph |
| `ContradictionDetectionMiddleware` | §3.8's mid-phase contradiction check needed a home. Deterministic dict comparison, no LLM call, placed here rather than inside the executor node so it is a named, LangSmith-visible step and the executor stays responsible only for coaching |
| `CoherenceMiddleware` | Layer 2a was previously a criterion inside `COACHING_QUALITY_RUBRIC`, conflating "is this a real statement at all?" with "is this good coaching?" — and paying for a full rubric grading call on responses already known to be incoherent |

**Five are custom by decision, not by necessity.** deepagents ships
`RubricMiddleware` and `SkillsMiddleware`, but the package is pre-1.0
with breaking changes shipping between minor versions, and adopting it
is all-or-nothing (`create_deep_agent` replaces `create_agent`).
Carrying a bounded amount of our own code is preferable to an unbounded
amount of someone else's pre-1.0 churn. They migrate together
when deepagents reaches 1.0.

**`ToolRetryMiddleware`** — LangChain core, `max_retries=2`,
`on_failure="continue"`, exponential backoff with jitter. **The class is
`ToolRetryMiddleware`, not `RetryMiddleware`** — the latter does not
exist in LangChain 1.x.

**`ModelRetryMiddleware`** — LangChain core, used as shipped, `retries=2`
with exponential backoff. It wraps each model call and retries transient
timeouts and rate limits silently.

**Its tier is distinct from the fallback chain (§9.3), and the two must
not be conflated.** `ModelRetryMiddleware` is *mechanical* retry — the
network flaked, try the same call again. The fallback chain is *model
swap* — gpt-4o → gpt-4o-mini → cache → degraded mode. Adopting the
middleware removes the hand-written try/except/sleep/counter plumbing
that would otherwise sit at the bottom of the chain; it does not replace
the chain. It is also the invisible-retry tier referenced in §3.7's
self-healing hierarchy: mechanical, never a coaching event.

**`DMAICGraderMiddleware`** — `grader` role at temperature 0.1,
`max_iterations=3`, per-criterion verdicts, `on_evaluation` callback
writing each iteration into `step_log`. Grader internals stay private
to the middleware and never reach `PhaseState`. The Belt never sees
the grader loop.

#### 3.4.1 Two graders, two rubrics — not redundant

**There are two graders in this architecture and they are easy to
mistake for one.** They differ in rubric, timing, and what they are
grading.

| | `DMAICGraderMiddleware` | Validation stack Layer 2d |
|---|---|---|
| **Where** | Middleware, inside the executor | The `validation_stack` node |
| **When** | **Every coaching turn**, via `after_agent` | **Once**, at the gate boundary |
| **Rubric** | `COACHING_QUALITY_RUBRIC` — one, shared | `PHASE_RUBRIC` — five, one per phase (§13) |
| **Grades** | The **coach's process** — is it coaching well? | The **gate document** — is it good enough? |
| **Sees** | One response at a time | The complete set of captured fields |

**`COACHING_QUALITY_RUBRIC`** — a single constant in `core/prompts.py`,
identical across all five phases:

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

**Why both are needed.** They catch different failures, and neither can
catch the other's:

- The **middleware** catches coaching-process failures in real time. If
  the coach passively accepts "poor morale" as a root cause, it is
  caught before the Belt sees the response — preventing eight further
  turns built on a weak foundation. A gate-boundary grader would catch
  this only after the whole phase was spent.
- The **validation node** catches document-product failures that no
  per-turn check can see. All four Analyse fields can look sound
  individually while the root cause discusses "error rate" and the
  baseline it references is "cycle time" — different measures, mutually
  inconsistent. Cross-field and cross-phase consistency is only visible
  once the document is complete.

**They also grade different actors.** The middleware grades the AI's
coaching; Layer 2d grades the artefact the Belt and coach produced
together. Collapsing them into one rubric would mean either checking
coaching behaviour against DMAIC content standards or checking a
finished document against "did you ask good follow-up questions" —
neither of which is a meaningful test.

#### 3.4.2 The seven-step computation coaching pattern

**A computation tool call is a teaching moment, not a calculation.** The
coach does not ask questions and then hand back a p-value — it teaches
the concept, explains what the analysis will prove, helps the Belt get
the data into shape, runs it, translates the output, shows it, and says
what to do next.

**Every one of the 20 computation tools (§8.2) follows the same seven
steps:**

| # | Step | What the coach does |
|---|---|---|
| 1 | **Educate on the concept** | What this *is*, in plain language, with a real-world analogy — and what the output numbers will mean, before any are produced |
| 2 | **Explain why now** | Why the Belt needs this analysis at this point in *their* project |
| 3 | **Guide data preparation** | What format the tool needs; check what the Belt already uploaded via `rag_lookup_evidence` |
| 4 | **Run the computation** | Call the tool — the Belt sees the call happening |
| 5 | **Interpret their result** | Translate the statistical output into plain language (§2.1) |
| 6 | **Visualise** | Call `propose_diagram` to show the result graphically, where applicable |
| 7 | **Coach the next move** | What does this mean for the project, and what happens next |

**Step 1 was added in v2.2.14 and is the one most often skipped.** The
original six-step pattern opened with "explain why", which assumes the
Belt already knows what a Cpk or a p-value *is*. Most do not. A Belt who
is told "this matters because it shows capability" and then handed
`Cpk = 0.82` has learned nothing — they cannot judge whether 0.82 is good,
and they cannot defend it at a gate.

**Educating first also sets the interpretation up.** By the time the
number arrives, the Belt already knows that above 1.33 is comfortable and
below 1.0 is not — so step 5 confirms a frame they already hold rather
than introducing one alongside a result.

**Steps 1, 5 and 7 are what make this coaching rather than a
calculator.** A Belt who receives `t_statistic: 4.23, p_value: 0.001`
with no concept and no interpretation has been given a number they cannot
act on and cannot defend at a gate.

**Worked shape, per phase — step 1 openings:**

| Phase | Tool | Step 1 — how the coach opens |
|---|---|---|
| Define | `calculate_expected_savings` | "Let's estimate the financial impact. If each rework costs €X and you have Y per month…" |
| Measure | `calculate_sigma_level` | "Your sigma level tells us how capable the process is. Let me calculate it from your defect data…" |
| Measure | `calculate_cpk` | "Cpk shows whether your process fits within the spec limits. You'll need USL, LSL, mean and standard deviation…" |
| Measure | `calculate_grr` | "Before we trust the data, we need to verify the measurement system. GR&R checks whether different people measuring the same thing get the same result…" |
| Analyse | `t_test` | "To prove the training gap is real, we'll compare error rates between the two groups statistically…" |
| Analyse | `linear_regression` | "Let's see how strongly training hours predict error rate. You'll need two columns of data…" |
| Control | `xbar_r_chart_limits` | "Control charts will monitor whether the improvement holds. I'll calculate the control limits from your post-improvement data…" |
| Control | `imr_chart_limits` | "You have one reading per period rather than batches, so we'll use an individuals chart — same idea, limits calculated from the point-to-point movement…" |

**This is enforced by `COACHING_QUALITY_RUBRIC`** (§3.4.1) — the criterion
reads: *"Coach must not dump raw statistical output without explanation.
When calling a computation tool, the coach must educate the Belt on the
concept first, explain why it matters for their project, then run the
tool."* Because the middleware grader fires on **every turn**, a
raw-output dump is caught before the Belt sees it.

**Consequence for SKILL.md authoring (§8.4).** Each phase skill must
carry the seven-step sequence for every computation tool in that phase's
`allowed-tools`. At 20–40 lines of guidance per tool, Measure's eight
computation tools alone account for 160–320 lines — **this is the
most content-heavy part of each skill.** The BB eBook extractions under
`skills/extraction/` supply the methodology content; the skill shapes it
into the seven-step conversation.

**The pattern is why §1.9's data-collection coaching is a first-class
surface.** Step 2 is where the coach teaches the Belt what to collect
and how to structure it — the only channel through which real-world data
enters the system (§1.2).

**`DMAICSkillsMiddleware`** — reads SKILL.md frontmatter at startup
(Level 1, under 2K tokens for all five phases), registers
`load_skill(name)` for the coach to call (Level 2), reference files on
demand (Level 3). `FilesystemBackend`, git-versioned alongside the
code.

**`SummarizationMiddleware`** — triggers at 100k tokens (~78% of
gpt-4o's window), keeps the last 20 messages raw. Prose summarisation
is safe here **because facts do not live in `messages[]`** — they live
in typed state and the store (§4).

**`BeforeModelStateInjection`** — models weight earlier prompt content
more heavily. Injecting project facts after the Belt's message lets the
response drift toward the Belt's framing rather than the project's
established state.

**Not used:** `HumanInTheLoopMiddleware` (two confirmed bugs — edited
tool-call args silently re-overwritten, and edit/reject broken in
subgraph contexts where only approve is reliable; both would discard a
Belt's correction), and `LLMToolSelectorMiddleware` (per-phase binding
already solves tool-count structurally).

### 3.5 The Planner / Executor contract

The planner produces a structured plan. The executor consumes it.
Neither does the other's job.

```python
coaching_plan = {
    "next_action":        "coach_root_cause_validation",
    "rationale":          "3 causes listed, none validated against data",
    "focus_field":        "root_cause_statement",
    "tools_needed":       ["rag_lookup_methodology", "chi_square_test",
                           "propose_diagram"],
    "retrieval_strategy": "multi_hop",          # §7.5 — planner decides
    "retrieval_hops": [
        "what tools validate root cause in DMAIC analyse phase",
        "how is {hop1_answer} applied to {root_cause_candidate}",
        "what threshold applies for {hop2_answer} in a call centre context",
    ],
    "expected_fields":    ["root_cause_statement", "validation_method"],
}
```

Produced with structured output (CLAUDE.md §4.6) — never prose parsed
downstream.

**Contract rules:**
- The planner never dispatches to tools directly
- The executor never decides strategy
- `retrieval_strategy` is decided at **plan** time, not retrieval time
- The two are separate nodes and are never fused — fusing them loses
  the boundary that makes cost, tracing, and testing separable

**`coaching_plan` is one `dict`, not a `list[dict]`.** One plan per
planner turn, overwritten each time the planner fires. There is no
upfront queue of plans.

The reason is the cycle in §3.2: the planner fires many times per phase,
and the Belt's answers change what the next plan should be. A plan made
at turn 1 cannot anticipate turn 4 — and a pre-planned list would either
be followed against the evidence or discarded, which makes it dead
weight either way. The planner reads current `artifacts` to know what is
captured and what is next; that is the queue, and it is derived rather
than stored.

**The plan is transient; its consequences are not.** Everything the plan
produces lands durably elsewhere — captured values and tool output in
`artifacts` (§4.8), sources in `citations`, the planner's decision and
rationale in `step_log`, the conversation in `messages`, and the full
LLM input/output in the LangSmith trace. Nothing is lost when the next
plan overwrites this one.

### 3.6 Gate flow — nine steps across two nodes

| Step | Node | What happens |
|---|---|---|
| 1 | `phase_executor` | Coach produces output; extraction captures fields |
| 2 | validation stack | Four layers (§3.7). **Belt does not see this loop.** |
| 3 | `gate_review_node` | `interrupt()` — Belt sees validated fields |
| 4–5 | *(frontend)* | Belt reviews, optionally edits |
| 6 | `gate_apply_node` | Policy advisory on the Belt's edits — **non-blocking** |
| 7 | `gate_apply_node` | Belt approves; the gate document is assembled and **written twice** — see below |
| 8 | checkpointer | State commits **only now** |
| 9 | output mapper → parent | Orchestration values return; static edge advances the phase |

**Two nodes, not one.** `gate_review_node` fires the interrupt and
stops; it does nothing with the response. `gate_apply_node` reads the
Belt's response, applies corrections, runs the advisory, and routes.
Separating collection from application keeps the interrupt boundary
clean and makes the resume path testable.

#### 3.6.1 What `gate_apply_node` writes — the two destinations

**This is the write the store-mediated handoff depends on.** Every
cross-phase read in §4.3 assumes the previous phase's gate document is
in the store; `gate_apply_node` is what puts it there, and until this
was specified the handoff had a reader with no writer.

After the Belt approves, `gate_apply_node` assembles the gate document
and writes it to **two** places:

```python
gate_document = {
    **child["artifacts"],                     # every captured field (§4.6)
    "computation_results": child["artifacts"].get("computation_results", []),
    "citations":           child["citations"],
    "uploads":             child["uploads"],
    "acknowledged_gaps":   acknowledged_gaps,  # Tier 2 gaps the Belt accepted (§3.7.1)
}

# 1. The store — what the next phase's input mapper reads
store.put(("projects", case_id, "artifacts"), phase_name, gate_document)

# 2. PhaseState — what survives a crash between the write and the checkpoint
return {"final": gate_document, "gate_attempts": 0, "validator_feedback": []}
```

**Physical blob path:**
```
store/projects/IMPR-2026-E9D/artifacts/define.json
```

**Read by the next phase:**
```python
store.get(("projects", case_id, "artifacts"), "define")
```

**Why both destinations, and not just the store.** The store write and
the checkpoint commit are two operations, and a crash between them would
leave a phase whose state says the gate has not been applied while the
store says it has. `final` holding the same dict makes the checkpoint
self-sufficient for recovery — the resumed graph can see what was
approved without re-reading the store. This is also why `final` is a
`dict` and not the `str` it was in earlier revisions (§4.2): it holds
the document, not a description of it.

**`gate_attempts` and `validator_feedback` reset here**, and only here.
The retry budget is per gate passage, so it is restored the moment a
gate passes (§4.2.1).

**Contents of the gate document:**

| Part | Source | Section |
|---|---|---|
| Captured fields | `artifacts` — all strings | §4.6 |
| Cross-phase reference dicts | `artifacts` — the three exceptions | §4.7 |
| `computation_results` | `artifacts["computation_results"]` | §4.8 |
| `citations` | `PhaseState.citations` | §4.2.3 |
| `uploads` | `PhaseState.uploads` | §4.2.3 |
| `acknowledged_gaps` | Tier 2 fields the Belt chose to proceed without | §3.7.1 |

**The `gate_documents` store namespace is retired.** It held the same
content under a second key, which made "which one is authoritative?" a
live question with no answer. The `artifacts` namespace holds the
approved gate document for each phase, and that document *is* the
phase's artifacts (§4.9, §6.3).

**Two quality checks, two actors, two moments.** The grader blocks at
step 2 because it is checking the AI's own output — there is no reason
to show the Belt work already known to be below standard. The advisory
does not block at step 6 because the Belt is the domain expert: it
offers a second opinion before the decision, not a veto after it.

**Implementation:** graph-level `interrupt()` + `Command(resume=...)`.
Not `HumanInTheLoopMiddleware` (§3.4).

**Frontend sequence:**
1. Belt clicks **Submit Gate** → `POST /gate/submit`
2. Backend resumes the graph; validation stack runs; `gate_review_node`
   interrupts with the validated field payload
3. Payload returned to the frontend and rendered for review
4. Belt edits if needed, then `POST /gate/approve` (or `/gate/reject`)
5. Backend resumes from the interrupt; `gate_apply_node` runs the
   advisory, applies edits, commits the checkpoint, writes artifacts to
   the store, and the parent's static edge advances the phase

### 3.7 The four-layer validation stack

All four run inside step 2, before the interrupt fires.

| Layer | Checks | Mechanism | Model | Fires | Implemented by |
|---|---|---|---|---|---|
| **2a** Coherence | Real, meaningful, conclusive? Catches gibberish, vague non-answers, self-contradiction, off-topic, parroting the Belt | Lightweight LLM | `coherence`, 0.1 | **Every turn** | **`CoherenceMiddleware`** (§3.4, position 7) |
| **2b** Field presence | All **Tier 1** fields populated? `DMAICGateValidator` static methods | **Deterministic** | None | Gate only | `validation_stack` node |
| **2c** Constraints | Addresses budget / timeline / risk / measurement? | Lightweight LLM | `constraint`, 0.1 | Gate + key mid-conversation decisions | `validation_stack` node |
| **2d** Quality rubric | Meets DMAIC standards per criterion? **Tier 1 fails, Tier 2 warns.** Uses `PHASE_RUBRIC` | LLM grader | `grader`, 0.1 | Gate only | `validation_stack` node |

**Layer 2a is a middleware; layers 2b–2d are the node.** This is not a
cosmetic distinction. Layer 2a fires **every coaching turn**, which a
gate-boundary node cannot do — so it is implemented as
`CoherenceMiddleware` on the `after_agent` hook (§3.4). Layers 2b–2d fire
once, at the gate, inside the `validation_stack` node. The four are one
conceptual stack and two mechanisms.

**Layer 2d is NOT `DMAICGraderMiddleware`.** An earlier revision of this
table named it as such, contradicting §3.4.1 on the same page. Layer 2d
runs in the `validation_stack` node against `PHASE_RUBRIC` (five, one per
phase) and grades the **gate document**. `DMAICGraderMiddleware` is
middleware position 8, runs against `COACHING_QUALITY_RUBRIC` (one,
shared) every turn, and grades the **coach's process**. Two graders, two
rubrics, two moments — see §3.4.1.

**Coherence is no longer a `COACHING_QUALITY_RUBRIC` criterion.** It moved
out when `CoherenceMiddleware` was added; `DMAICGraderMiddleware` grades
process quality only. Any rubric entry for coherence is stale.

**Cheapest first; each fires only if the previous passes. The
iteration cap is 3, shared across all four**, with accumulated
feedback — never three per layer. The counter is
`PhaseState.gate_attempts` and the feedback is
`PhaseState.validator_feedback` (§4.2.1, §4.2.2).

`CoherenceMiddleware` carries its **own** 2-retry cap on response quality,
independent of the shared gate cap of 3 and independent of
`ModelRetryMiddleware`'s 2-retry cap on transient API failure. Three caps,
three different failure modes, no shared counter. On a third coherence
failure the turn degrades and `DMAICGraderMiddleware` is skipped.

#### 3.7.1 Two tiers of field, and the `warning` verdict

**Layer 2b and Layer 2d used to be able to contradict each other.** The
gate blocked on a required-field list; the grader graded against a
rubric; the two sets were not the same set. A phase could pass the gate
and then be failed by the grader on a criterion the gate never required
— a contradiction with no defined resolution.

**Every rubric criterion is now classified into one of two tiers.**

| Tier | Layer 2b (presence) | Layer 2d (grader) | Belt's options |
|---|---|---|---|
| **Tier 1 — gate-required** | **Blocks.** Gate cannot pass | Fails | Must supply the field |
| **Tier 2 — rubric-recommended** | Not checked | **Warns** | Add it now, or proceed with an acknowledged gap |

**Tier 1 by phase:**

| Phase | Tier 1 fields | Count |
|---|---|---|
| Define | `problem_statement`, `voc_summary`, `project_scope`, `goal_statement`, `process_map_sipoc` (dict), `issues_and_barriers` | 6 |
| Measure | `baseline_mean`, `data_collection_plan`, `xy_matrix_summary`, `vital_few_xs`, `detailed_process_map` (dict), `stability_assessment`, `issues_and_barriers` | 7 |
| Analyse | `root_cause_statement`, `root_cause_validation`, `practical_significance`, `issues_and_barriers` | 4 |
| Improve | `selected_solution`, `pilot_result`, `experiment_justification`, `issues_and_barriers` | 4 |
| Control | `control_plan` (dict, §4.10.6), `post_improvement_metric`, `issues_and_barriers` | 3 |

**`issues_and_barriers` is Tier 1 in all five phases** (§4.10.5) — every
real project has blockers, and a Belt reporting none has not looked.

**Everything else in the rubric is Tier 2** — `baseline_sigma`,
`ruled_out_causes`, `handover_documented`, `financial_impact_verified`,
`implementation_plan`, `lessons_learned`, `transferability`,
`secondary_metrics`, `statistical_problem_statement`,
`process_owner_buyin`, `explanatory_power`, `project_signoff`, and the
rest.

**The grader's verdict gains a third status.** `CriterionVerdict.status`
is now `"pass" | "warning" | "fail"`, replacing the boolean `passed`:

```python
class CriterionVerdict(BaseModel):
    criterion: str
    tier:      int                    # 1 or 2
    status:    Literal["pass", "warning", "fail"]
    feedback:  str                    # per criterion, specific — never "try again"
```

**A gate can pass with warnings. It cannot pass with failures.** Only
Tier 1 criteria can produce `fail`; Tier 2 criteria produce at worst
`warning`.

**When the Belt proceeds past a warning, the gap is recorded**, not
silently dropped. `gate_apply_node` writes it into the gate document
(§3.6.1):

```python
"acknowledged_gaps": ["baseline_sigma — Belt accepted gap"]
```

The next phase's planner reads that list from the store and factors it
into its coaching plan — a Measure phase that proceeded without
`baseline_sigma` is something Analyse should know about when it comes to
validate a root cause against capability.

**Why two tiers rather than one strict list.** A gate that blocks on
every criterion teaches Belts to fill fields mechanically, which
produces complete gate documents and worse projects. Tier 1 catches
genuinely incomplete phases. Tier 2 coaches toward best practice while
leaving the Belt — who knows their own project — the decision. The audit
trail then records conscious decisions rather than silent omissions,
which is the more useful record.

#### 3.7.2 The grader is belt-level aware

**The grader reads `belt_level` from the case record and suppresses
recommendations the Belt has not been trained for.**

```
if belt_level == "Black Belt":
    flag FMEA, DOE, X-Y matrix, statistical problem statement as Tier 2
if belt_level == "Green Belt":
    suppress these — do not recommend heavy methodology GB isn't trained for
```

| Item | Green Belt | Black Belt |
|---|---|---|
| DOE | Suppressed | Tier 2 |

**DOE is the only belt-gated item left.** Stability left this table in
v2.2.12: it is now `stability_assessment`, a **Tier 1 field required of
both belt levels** (§4.10.7). It was never suppressed for a Green Belt —
what changed is that it is no longer advisory.

**Three items left this table in v2.2.11:**

| Item | Was | Now |
|---|---|---|
| **X-Y matrix** | BB-only Tier 2 rubric item, no field | **`xy_matrix_summary`, Tier 1, all Belts** (§4.10.5). It is how the vital few X's are produced, and Analyse cannot start without them |
| **Statistical problem statement** | BB-only, and placed in Define | **`statistical_problem_statement`, Tier 2, all Belts, in Analyse** — where the eBook asks it (§4.10.5) |
| **FMEA / updated FMEA** | BB-only Tier 2 | **Removed entirely.** Not tracked in any schema; see §4.10.5 |
| **Three-party sign-off** | Tier 2 rubric item with no field | **`project_signoff`, Tier 2 field on `ControlOutput`** (§4.10.5). Still simplified for a Green Belt in coaching, but now recorded |

**Coaching scope is both belt levels**, and the tier system is what
makes one rubric serve both. FMEA and DOE are heavy methodologies;
recommending them to a Green Belt produces either a bad FMEA or a Belt
who ignores the grader, and both outcomes cost more than the omission.

**Stability and special-cause analysis is not suppressed for either
level** — a baseline computed across an unstable process is not a
baseline, and that matters regardless of training.

Note this is the same `belt_level` that is **off by default as a
retrieval filter** on `improve_case_index` (§7.3). Filtering what a Belt
can *learn from* over-narrows; adjusting what the grader *asks of them*
does not.

**Only 2b is deterministic.** 2a and 2c are LLM calls because format
checks cannot detect content failures: a length check does not detect
fluent nonsense, and a keyword check rejects a decision that addresses
cost thoroughly without using the word "budget." Layer 2a costs roughly
$0.01–0.02 per phase session across 20–40 turns.

**Failure visibility — the self-healing hierarchy:**

| Level | Trigger | Belt sees | Retry |
|---|---|---|---|
| 1 Silent | Coherence failure mid-turn | Nothing — corrected response only | Max 2, then degraded mode |
| 2 Coached | Constraint failure on a Belt proposal | Teaching moment, collaborative | **No cap** — this is dialogue |
| 3 Validated | Full stack at gate | Pass/fail per criterion; corrects and approves | Max 3, accumulated feedback |
| 4 Escalated | Attempts exhausted | Unresolved constraints named | None — Belt decides |

Level 2 has no retry cap deliberately. Capping it would mean the coach
eventually accepts a weak root cause — the exact outcome DMAIC
discipline exists to prevent.

Every attempt at every layer writes a dict entry to `step_log` (§4.4).

### 3.8 Mid-phase conflict detection and the re-approval cascade

The mid-phase contradiction diff runs **before each coach response
reaches the Belt**, not only at gate boundaries. It is not a node — it is
logic that the executor path calls on its way out, and the same routine
runs again as the policy advisory inside `gate_apply` at step 6 (§3.6).

**Detection.** A structured diff — no LLM call, negligible latency —
comparing values extracted this turn against the `artifacts` committed
in prior gate documents. If any numeric or categorical value differs,
the coach's response is **suppressed** and an interrupt payload is
emitted carrying: field name, previously approved value, its approval
timestamp and gate, the proposed new value, and two options.

| Belt chooses | Consequence |
|---|---|
| Update the approved value | Affected phase's gate document becomes provisional; the cascade fires |
| Keep the approved value | Belt clarifies they misspoke; no state change |

**No tolerance threshold exists, and none may be added.** In production
DMAIC, baseline means, sigma levels, and target metrics are taken
seriously; silent drift across weeks is precisely the failure mode a
coaching system exists to prevent.

**The cascade.** If the Belt confirms the new value, the affected phase
and **every downstream phase that depends on it** return to provisional
and require re-review. A root cause validated against a baseline of 4.2
is not automatically valid against 3.8.

**Hard dependency on §9.2.** When the cascade fires, the affected
phase's `error_handler` compensating logic must run to clean up stale
values already written to Azure Blob and `improve_case_index`. A
cascade that marks phases provisional but leaves published values in
place is worse than no cascade — state and index then disagree
silently.

### 3.9 Escalation

`escalation_subgraph` is entered via conditional edge when the
validation stack exhausts its shared cap of 3 attempts, or when the
coach calls `request_human_approval`.

1. Produces a structured "stuck" report naming the unresolved
   constraints — not a generic failure message
2. Sets `escalated=True` in checkpointed state
3. Routes to END; the graph terminates this turn

`gate_attempts` is persisted in checkpointed state, never in route
scope. The frontend reads `escalated` and renders the escalation
banner.

---

## 4. State Model

### 4.1 `SupervisorState` — orchestration only

`core/state.py`

```python
class SupervisorState(TypedDict):
    messages:        Annotated[list[BaseMessage], operator.add]
    history:         Annotated[list[str], operator.add]
    case_id:         str                                   # canonical identifier (§4.6)
    phase_index:     int                                   # 0=Define … 4=Control
    current_phase:   str
    gate_passed:     dict[str, bool]                       # {"define": True, "measure": False, …}
    final_output:    Optional[dict]                        # set when the Control gate passes
```

**Seven fields. That is the whole schema**, and adding an eighth requires
an amendment under §18.1.

| Field | Reducer | Notes |
|---|---|---|
| `messages` | append | Compressed by `SummarizationMiddleware` |
| `gate_passed` | **replace** | What the supervisor routes on (§3.2). A dict, not a list — `gate_passed["measure"]` is a direct lookup, and a phase that has been reopened by the cascade (§3.8) can be set back to `False` without a list removal |
| `phase_index` | last write | Distinct from `field_index` on `PhaseState` |
| `final_output` | last write | `dict`, not `str` — the same rule as `PhaseState.final` (§4.2) |

#### 4.1.1 `case_id` is the canonical identifier

**The identifier is `case_id` everywhere — state, store namespaces, blob
paths, index fields, and prose.** `project_id` is retired.

This was a docs-vs-code split, not a design question. Every existing
artefact already said `case_id`: `improve_case_index.case_id`,
`improve_evidence_index.case_id` (§7.2, §7.3), `cases/case_{id}.json`
(§6.4), `uploads/{case_id}/{file}`, and all the storage models. Only the
governance documents said `project_id`. Changing the documents is one
sweep; changing the code, two live Azure AI Search indexes, and the blob
layout is a migration with no benefit at the end of it.

`case_id` is also the graph's `thread_id` (§3.1) and the store's
namespace segment (§6.3). One identifier, one name, everywhere.

**Artifacts and gate documents are deliberately absent.** They live in
the store (§6.3). Two reasons: parent state stays small enough to
checkpoint cheaply, and subgraph state does not reliably propagate to
the parent anyway (§4.3). *(Earlier revisions named these fields
`captured_fields` and `gate_documents`; both names are retired — §4.9.)*

**`dmaic_plan`, `key_decisions`, `open_items` and `project_context` are
also deliberately absent.** All four were removed as redundant. Each
duplicated something an existing mechanism already carries, and a
duplicate is a second source of truth that can drift out of agreement
with the first:

| Removed | Covered instead by |
|---|---|
| `dmaic_plan` | DMAIC order is fixed and encoded in static edges (§3.2) — there is no plan to store. The project's substantive plan is Define's gate document in the store, plus `improve_case_index` metadata (§7.3) |
| `key_decisions` | Decisions the Belt commits become captured fields via `CoachingResponse.fields_captured`, approved at a gate, written to `artifacts` and then the store. All three locations are outside `messages[]`, so they already survive compression |
| `open_items` | Derived on demand: `check_gate_status()` reports unpopulated required fields, and the four-layer validation stack (§9) is what surfaces blockers |
| `project_context` | Composed at the boundary by each input mapper (§4.3). Define's context comes from the case record in the store; every later phase's comes from the prior phase's artifacts. The substance — problem, goal, scope, business case — is Define's gate document; the framing — title, department, belt level, target date — is the case record and the `improve_case_index` row (§7.3) |

The compression argument that originally motivated `key_decisions` and
`open_items` still holds — facts must not live only in `messages[]` —
but it is satisfied without them. Captured fields and gate documents
were already outside `messages[]`, so the two fields added a parallel
copy rather than a new guarantee.

**Blockers and outstanding work are computed, never stored.** A stored
`open_items` list is a second answer to "is this gate ready?" that can
disagree with `DMAICGateValidator`. A derived one cannot.

**`project_context` failed the same test from the other direction.** It
was a prose summary of facts held structurally elsewhere, and it had no
writer: the schema comment said "set once after Define," while its only
declared reader was `define_input_mapper` — which runs *before* Define.
No later phase read it, because §4.3 already routes every later phase's
`phase_context` through the store. It was an inherited lab field
(REFACTORING_AGENT_IMPROVE.md §18, where the course's `task: str` maps
onto AgentLean), not a designed one, and the one job it was declared to
do is done by composing context at the boundary.

#### 4.1.2 `current_phase` and `phase_index` are derived — and kept

Both are computable from `gate_passed`: the current phase is the first
entry in `PHASE_ORDER` whose `gate_passed` value is not `True`, and
`phase_index` is its position. By the test that removed the four fields
above, that makes them redundant.

**They are kept anyway, as a deliberate, documented exemption.**
`state["current_phase"]` is read in dozens of places — every input
mapper, the state-injection middleware, every log line, the case index
writer — and deriving it at each site adds noise to code that is
otherwise about coaching. The two fields are cheap: one string and one
int, both scalar, neither able to grow.

**The exemption comes with an obligation.** These are derived values kept
for readability, so **the supervisor is responsible for keeping them
consistent with `gate_passed`**. They are written in exactly one place —
the output mapper at gate approval (§4.3) — which advances all three
together. Nothing else may write them.

The distinction from the removed fields is that these are *derivable and
trivially kept in sync from a single write site*, whereas `open_items`
and `key_decisions` were derivable but would have needed refreshing from
many sites, which is where drift comes from.

### 4.2 `PhaseState` — per-phase subgraph state

`core/substate.py`

```python
class PhaseState(TypedDict):
    # ── conversation plumbing (3) ───────────────────────────────
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]
    phase_context:      str                # composed at the boundary (§4.3)

    # ── the fourteen content fields ─────────────────────────────
    coaching_plan:      Optional[CoachingPlan]  # planner output, ONE plan (§3.5)
    field_index:        int                # field within the phase
    draft:              dict[str, Any]     # this turn's extraction
    artifacts:          dict[str, Any]     # accumulated for the phase
    step_log:           Annotated[list[dict[str, Any]], operator.add]
    belt_edits:         dict[str, Any]     # Belt corrections at the gate
    turn_count:         int                # coaching turns before the gate
    final:              dict[str, Any]     # approved gate document (§3.6)
    gate_attempts:      int                # validation retry counter, cap 3
    validator_feedback: list[dict]         # accumulated per-attempt feedback
    citations:          list[dict]         # sources the coach cited this phase
    uploads:            list[dict]         # files the Belt uploaded this phase
    hop_results:        list[str]          # ordered hop answers; [] otherwise
    synthesis_output:   Optional[dict]     # SynthesisOutput; None for single-hop
```

**Seventeen fields: fourteen content fields plus three conversation
plumbing fields.** `messages`, `history` and `phase_context` are not
under the content design — `messages` is what `create_agent` runs its
loop on, `history` is the node execution trail, and `phase_context` is
composed at the boundary by the input mapper (§4.3).

**`hop_results` and `synthesis_output` carry the planned multi-hop
chain**, and both exist because a local Python variable inside a node is
not inspectable. LangSmith traces node inputs and outputs, not
interpreter locals, so hop results held in a local dict are invisible in
the trace and lost on checkpoint restore. Returned into state they appear
in the state diff per node invocation and survive a resume.
`synthesis_output` holds the dedicated synthesis call's `SynthesisOutput`
so the coach call reads it from state rather than from a local variable.

Both are `[]` / `None` on every single-hop turn in every phase. They are
declared on `PhaseState` rather than an Analyse-only variant because
`CoachingPlan.retrieval_strategy` may select `multi_hop` in any phase.

**`coaching_plan` is a single typed `CoachingPlan`, not a list and not a
bare dict.** One plan per planner turn, overwritten each time the planner
fires (§3.5). It is produced via `with_structured_output(CoachingPlan)` —
a plain dict cannot be validated at planner-output time, and
`retrieval_strategy` in particular needs its `Literal` constraint, since
it selects the executor's whole retrieval path and a typo would fall
through silently to single-hop. `dict[str, Any]` is acceptable as an
interim annotation inside the `TypedDict`; the typed form is preferred.

**`draft`, `belt_edits` and `final` are `dict`, never `str`.**
String-typed handoffs force downstream nodes to parse prose out of an
upstream node's output — the anti-pattern this architecture exists to
remove. `final` is the approved gate document, which is structured data
by construction (§3.6).

**`artifacts` and `step_log` are separate and stay separate.**
`artifacts` is WHAT was captured; `step_log` is HOW. A DMAIC quality
system must show not just what the root cause was, but how it was
determined.

Per-phase variants (`DefineState`, `MeasureState`, …) extend
`PhaseState` with phase-specific transient fields. All use explicit
`TypedDict`, not `MessagesState` inheritance — their dominant content
is structured fields, not conversation.

#### 4.2.1 `gate_attempts` — the counter that fixes the v1 reset bug

**`gate_attempts` lives on `PhaseState`, and that placement is the
whole point.** It is the shared retry counter for the four-layer
validation stack (§3.7): incremented on each failed attempt, reset to
`0` when the gate passes, and at `>= 3` routes to escalation (§3.9).

It is **per phase, not per supervisor**, because each phase runs its own
validation loop with its own cap. A supervisor-level counter would let
a difficult Measure phase consume the budget Analyse needs.

v1 held the equivalent counter in route scope, so every request rebuilt
it at `0` and the cap never fired — the loop could retry indefinitely
while reporting attempt 1 each time. Putting it in checkpointed state is
what makes the cap real, and it is why the field is named in CLAUDE.md
§1.7 and §3.5 as a hard requirement rather than an implementation
detail.

#### 4.2.2 `validator_feedback` — accumulation is what makes retry work

Retry without memory repeats the same mistake. `validator_feedback`
accumulates one entry per failed attempt, across all four layers, and
the coach reads the full list on each retry:

```python
{"attempt": 1, "layer": "grader",
 "criteria_failed": ["root_cause_validation"],
 "feedback": "does not reference statistical evidence",
 "timestamp": "2026-08-03T11:04:19Z"}
```

Reset to `[]` when the gate passes. This is the state carrier for the
"accumulated feedback" the shared cap of 3 depends on (§3.7) — the cap
is only defensible because each attempt is better informed than the
last, and this field is what informs it.

**`validator_feedback` and `belt_edits` are different things and were
split for that reason.** `validator_feedback` is what the *system's*
validation layers said about the AI's output at step 2. `belt_edits` is
what the *Belt* corrected at step 5. Two actors, two moments (§3.6) —
the field previously called `feedback` conflated them, and a single
field could not carry both without the coach reading Belt corrections as
validation failures.

#### 4.2.3 `citations` and `uploads` — the evidence trail

The gate document has to show what the phase was grounded in, so both
are tracked per phase and both are written into it (§3.6).

```python
citations = [{"source": "improve_knowledge_index", "page": 47,
              "content_summary": "GR&R acceptance thresholds", "turn": 5}]

uploads   = [{"filename": "defect_data_q2.xlsx", "case_id": "IMPR-2026-E9D",
              "upload_turn": 3, "purpose": "baseline data"}]
```

`citations` carries the `source_file` / `page_number` metadata that §2.3
requires to be surfaced. `uploads` matters more than it looks:
`improve_evidence_index` is the only channel through which external data
enters the system (§1.2), so the upload list *is* the record of what
real-world evidence the phase had.

### 4.3 Boundary mappers — the store-mediated handoff

`SupervisorState` and `PhaseState` are different schemas, so something
must translate at the subgraph boundary. Two plain functions per phase,
in `phases/{phase}/mappers.py`.

```python
def define_input_mapper(parent: SupervisorState, store: BaseStore) -> PhaseState:
    """SupervisorState → DefineState. Context is composed from the store,
    never carried on parent state. Define has no prior phase, so its
    source is the case record loaded at session start (§6.3)."""
    case = store.get(("projects", parent["case_id"], "case"), "record").value
    return {
        "messages":           parent["messages"],
        "history":            [],
        "phase_context": (
            f"{case['title']} — {case['department']}. "
            f"{case['belt_level']} belt, led by {case['leader']}, "
            f"target {case['target_date']}."
        ),
        "coaching_plan":      {},
        "field_index":        0,
        "draft":              {},
        "artifacts":          {},
        "step_log":           [],
        "belt_edits":         {},
        "turn_count":         0,
        "final":              {},
        "gate_attempts":      0,
        "validator_feedback": [],
        "citations":          [],
        "uploads":            [],
    }


def define_output_mapper(child: PhaseState, parent: SupervisorState,
                         store: BaseStore) -> dict[str, Any]:
    """DefineState → SupervisorState update. The gate document goes to the
    store; only orchestration-relevant values return to the parent."""
    store.put(
        ("projects", parent["case_id"], "artifacts"),
        "define",
        child["final"],                      # the approved gate document (§3.6)
    )
    return {
        "current_phase": "measure",
        "phase_index":   1,
        "gate_passed":   {**parent["gate_passed"], "define": True},
    }
```

**The three orchestration values advance together, from this one site.**
That single write point is what makes the derived-field exemption in
§4.1.2 safe.

**Every input mapper composes `phase_context` from the store.** Define
reads the case record; Measure, Analyse, Improve and Control read the
prior phase's artifacts. The rule is uniform, which is what makes it
safe: an input mapper's only dependency is `BaseStore`, so there is no
parent-state field to keep current and no phase whose context can go
stale because a write was missed. An earlier revision made Define the
exception, reading `parent["project_context"]` — a field with no
declared writer and a stated lifecycle ("set once after Define") that
placed the write *after* the only read. §4.1 removed it.

**The case record reaches the store once, at session start.** It is
loaded from `cases/case_{id}.json` (§6.4) into
`("projects", pid, "case")` when the session opens, not re-read per
phase entry. Mappers are pure translation functions; giving one a blob
client would put untracked I/O inside the boundary.

**The output mapper returns orchestration values and nothing else.**
Everything the Belt produced is already in the store by the time it
returns. An earlier revision also lifted `key_decisions` and
`open_items` out of `child["artifacts"]` and back onto the parent;
that was the redundancy §4.1 removed — the values were in the store
already, and copying them up created a second copy to keep in sync.

**Why the store and not shared state keys.** LangGraph documents that a
subgraph's state updates may not be visible to the parent immediately,
because each subgraph manages its own checkpoint namespace — and names
the Store as the fix for data that must cross graph boundaries. The
design follows that guidance rather than testing around it.

**Concrete Define → Measure sequence:**

```
1. Define subgraph runs; Level 2 cycles capture its Tier 1 fields into
   PhaseState.artifacts. Nothing is written outside the subgraph yet.
2. Gate: validation stack → interrupt → Belt reviews, edits, advisory
   fires, Belt approves.
3. gate_apply_node assembles the gate document and writes it to BOTH
   PhaseState.final and the store (§3.6). Checkpoint commits.
4. define_output_mapper returns orchestration values to the parent.
5. Static edge fires: define → measure.
6. measure_input_mapper reads Define's gate document from the store and
   builds Measure's phase_context.
7. Measure's planner reads that context plus Measure's required fields
   and plans its first coaching turn.
```

At no point does Measure parse Define's output from a message. If it
needs Define's baseline metric it reads the field from Define's gate
document — as a string, which its computation tool parses at the point
of use (§4.6) — and if that value later changes, §3.8 fires.

**String-interpolating a previous phase's output into the next phase's
prompt is prohibited.**

### 4.4 `step_log` — the audit trail

Dict entries with named keys. Tuples are prohibited: field names make
the log self-documenting and queryable.

```python
{"layer": "constraint", "attempt": 2, "status": "failed",
 "reason": "does not address timeline", "decision_excerpt": "..."}

{"service": "gpt-4o", "attempt": 2, "status": "failed",
 "reason": "timeout after 45s", "timestamp": "..."}

{"iteration": 1, "result": "needs_revision",
 "criteria": [{"criterion": "goal_statement", "passed": False,
               "feedback": "no time-bound element"}]}
```

Writers: the four validation layers (§3.7), each grader iteration via
`on_evaluation` (§3.4), every fallback attempt (§9.3), and every
compensating action (§9.2).

**The four-part audit answer** — for any completed run:

| Question | Source |
|---|---|
| What happened | `artifacts`, `step_log`, LangSmith node spans |
| Why | `coaching_plan`, grader verdicts in `step_log`, validation entries |
| Who approved | Reviewer id + timestamp recorded at gate step 7 |
| When | Checkpoint timestamps; `created_at`, `days_in_phase` on the case index |

### 4.5 Persistence boundary

| Written | Where | When |
|---|---|---|
| Full graph state | Checkpointer | After every node transition |
| Gate document (the phase's artifacts) | Store | At gate approval — `gate_apply_node`, then the output mapper (§3.6) |
| Case record | Case blob | On create, gate pass, upload — **never per turn** |
| Case summary + embedding | `improve_case_index` | On gate pass |

### 4.6 Field typing — every captured field is a string

**All captured fields are `str`. There are no typed numerics in any
phase schema.** This is a project-wide design rule with one narrow,
enumerated exception (§4.7).

```python
baseline_mean = "12.3% invoice error rate, measured over Q2 2026"
```

**Computation tools parse at the point of use.** Each of the 20 tools
(§8.2) knows how to extract the number it needs from the string it is
given, and returns a clear reformatting request to the Belt when it
cannot. The parsing logic lives in 18 places that already had to
validate their inputs, rather than in a schema that would have to
anticipate every way a Belt writes a percentage.

**Why not typed numerics.** Roughly 25 numeric fields run across DMAIC.
Typing them means either losing the Belt's own words — a gate document
that reads `12.3` where the Belt wrote "12.3% measured over Q2" is a
worse audit record — or carrying raw, value and unit alongside each
other, which turns 25 fields into 75 and puts a three-way consistency
problem into every one of them.

**The gate document shows the Belt's exact words.** That is a
requirement of a quality system, not a side effect: the Belt has to be
able to show what they stated, not what the system parsed out of it.

> **This corrects an earlier claim.** Previous revisions of §4.3 and of
> CLAUDE.md §10.2 said "Measure reads Define's baseline metric as a
> typed float." No baseline field has ever been typed as a float in any
> schema in this project — every one is `str`. The prose promised a
> guarantee the schemas did not provide, which is exactly the kind of
> drift that gets discovered during implementation. Measure reads a
> string and parses it in `calculate_sigma_level`.

### 4.7 Cross-phase reference fields — the one exception

**Three fields are `dict`, not `str`.** They are the three points where
one phase's conclusion must be provably built on an earlier phase's
finding:

| Field | Phase | References |
|---|---|---|
| `causal_hypothesis` | Analyse | Measure's baseline |
| `solution_linked_to_root_cause` | Improve | Analyse's root cause |
| `post_improvement_metric` | Control | Measure's baseline |

Each carries the Belt's content **and** an explicit machine-checkable
reference:

```python
causal_hypothesis = {
    "hypothesis":       "Inadequate onboarding causes the error spike in the first 60 days",
    "references_phase": "measure",
    "references_field": "baseline_mean",
    "references_value": "12.3%",
}
```

**The grader verifies the link deterministically.** It reads the
referenced phase's gate document from the store and checks that
`references_field` exists with `references_value`. No LLM judgment is
involved in the linkage check itself, so the failure message is exact:

```
references baseline_mean = 12.3% but the Measure gate document
shows baseline_mean = 15%.
```

**Why these three are worth the exception.** They are the highest-stakes
checks in DMAIC — a broken link means the project built on the wrong
foundation, and nothing downstream will reveal it. Leaving the linkage
to LLM reasoning fails precisely when Belt terminology shifts between
phases ("high rework" in Analyse, "12.3% invoice error rate" in
Measure), which is the common case rather than the edge case. The
container is a dict so the reference is readable; the values inside it
are still strings, so §4.6 holds within the exception.

### 4.8 `computation_results` — where the 20 tools land

**Tool output is stored in `artifacts["computation_results"]`, a list of
typed dicts.** One container per phase; no per-phase typed fields.

```python
artifacts["computation_results"] = [
    {"tool": "t_test",
     "inputs":  {"sample1": "new_staff_errors", "sample2": "experienced_staff_errors"},
     "result":  {"t_statistic": "4.23", "p_value": "0.001", "significant": "yes"},
     "turn": 7,  "phase": "analyse"},
    {"tool": "calculate_cpk",
     "inputs":  {"usl": "5%", "lsl": "0%", "mean": "3.1%", "std_dev": "0.8%"},
     "result":  {"cpk": "1.33"},
     "turn": 12, "phase": "measure"},
]
```

All values are strings, per §4.6.

**The problem this solves.** A Belt runs `t_test` and gets p=0.001; the
result appears in the conversation and then disappears into it. The
grader cannot answer "was a hypothesis test actually run?", and neither
can the audit trail. Rubric criteria that depend on computation had no
evidence to read.

**The grader's check is mechanical:** scan
`artifacts["computation_results"]` for an entry whose `tool` is
`t_test`. `calculate_cpk` for capability, `calculate_grr` for
measurement system validation, and so on — each of the 20 tools writes
to the same structure, and only `tool` and `phase` differ.

**Why one list rather than typed destination fields.** Typed fields
would add three to five per phase for the same mechanical check, and
each new computation tool would then require a schema change. The list
absorbs all 20 and every future one.

**`computation_results` lives inside `artifacts`, so it reaches the
store with the rest of the gate document** (§3.6) — no new `PhaseState`
field is needed for it.

### 4.9 One name for one concept — `artifacts`

**`artifacts` is the canonical name.** It is the `PhaseState` field, the
store namespace segment, and the content of the gate document.

| Retired name | Was | Status |
|---|---|---|
| `captured_fields` | Prose name in the governance documents | **Retired.** Replaced by `artifacts` throughout |
| `phase_inputs` | v1 code field name | **Retired.** Replaced during the refactor |

`PhaseState.artifacts` holds the fields the Belt has produced in this
phase. Previous code called these `phase_inputs`; previous prose called
them `captured_fields`. Both names are retired, and neither may be
reintroduced — three names for one concept is how a reader ends up
believing there are three things.

### 4.10 Schemas — `CoachingResponse` in, `{Phase}Output` out

**Two schemas at two moments.** One runs on every coaching turn; the
other is built once, at the gate. Substituting either for the other is
the error this section exists to prevent.

| | `CoachingResponse` | `{Phase}Output` |
|---|---|---|
| Fires | **Every coaching turn** | **Once**, at `gate_apply` |
| Produced by | The executor, via `response_format=` | Pydantic construction — **no LLM call** |
| Holds | This turn's extraction | The complete gate document |
| Lands in | `artifacts`, `citations` | The store, and `PhaseState.final` |

#### 4.10.1 `CoachingResponse` — the per-turn contract

```python
class CoachingResponse(BaseModel):
    """Structured extraction from each coaching turn."""
    message: str                        # coaching text the Belt sees
    fields_captured: list[dict] = []    # [{field_name: str, value: Any, source: str}]
    citations: list[dict] = []          # sources referenced this turn
```

**`value` is `Any`, not `str`, and that is required rather than loose.**
It must carry both plain string fields and the three cross-phase
reference dicts of §4.7. Typing it `str` would make `causal_hypothesis`,
`solution_linked_to_root_cause` and `post_improvement_metric`
uncapturable — the coach would have nowhere to put them. The values
*inside* those dicts remain strings, so §4.6 is intact.

**Structured response and coaching text coexist.** The agent still runs
its ReAct loop and still writes prose into `messages`; only the terminal
response carries the additional structure, in
`result["structured_response"]`.

```python
result = await executor.ainvoke(state)

result["messages"][-1]
  → "Good — I've captured your baseline at 12.3%. Now, how was that measured?"

result["structured_response"]
  → CoachingResponse(
        message="Good — I've captured your baseline at 12.3%…",
        fields_captured=[{"field_name": "baseline_metric",
                          "value": "12.3%", "source": "belt_stated"}],
        citations=[],
    )
```

The executor node then writes:

```python
for f in resp.fields_captured:
    artifacts[f["field_name"]] = f["value"]     # str, or dict for cross-phase refs
citations.extend(resp.citations)
```

**This is what replaced `record_field`** (§8.1). A tool call is a
decision the model can omit; a response schema is not. A turn where the
Belt states a baseline and the coach forgets the tool call used to lose
the value silently — that failure mode no longer exists.

#### 4.10.2 The five gate document schemas

`phases/{phase}/schema.py`. **Every field is `str`** except the three
cross-phase reference dicts (§4.7). **Every schema carries the same four
gate-metadata fields**, assembled at gate time rather than captured per
turn.

```python
class DefineOutput(BaseModel):
    """Gate document for the Define phase."""
    # Tier 1 — gate-required
    problem_statement: str                  # measurable problem, baseline and target
    project_scope: str                      # explicit inclusions and exclusions
    goal_statement: str                     # SMART
    voc_summary: str                        # voice of customer
    process_map_sipoc: dict                 # SIPOC + KPIs, 6 sub-fields (§4.10.7)
    issues_and_barriers: str                # Belt-stated blockers (§4.10.5)
    # Tier 2 — rubric-recommended
    business_case: str                      # quantified business impact (COPQ)
    team: str                               # Belt, sponsor, 2+ members with roles
    baseline_metric: str                    # current measured state
    target_metric: str                      # target value
    secondary_metrics: str                  # what could get worse (§4.10.5)
    # Gate metadata
    computation_results: list[dict] = []
    acknowledged_gaps:   list[str]  = []
    citations:           list[dict] = []
    uploads:             list[dict] = []


class MeasureOutput(BaseModel):
    """Gate document for the Measure phase."""
    # Tier 1
    baseline_mean: str                      # value with units, as the Belt stated it
    data_collection_plan: str               # sample size, frequency, responsible person
    xy_matrix_summary: str                  # evidence prioritisation happened (§4.10.5)
    vital_few_xs: str                       # the ranked result Analyse consumes (§4.10.5)
    detailed_process_map: dict              # expanded map, 6 sub-fields (§4.10.7)
    stability_assessment: str               # checked BEFORE capability (§4.10.7)
    issues_and_barriers: str
    # Tier 2
    baseline_sigma: str                     # calculated sigma level
    measurement_system_validated: str       # GR&R or equivalent evidence
    secondary_metrics: str
    # Gate metadata
    computation_results: list[dict] = []
    acknowledged_gaps:   list[str]  = []
    citations:           list[dict] = []
    uploads:             list[dict] = []


class AnalyseOutput(BaseModel):
    """Gate document for the Analyse phase."""
    # Tier 1
    root_cause_statement: str               # specific and actionable
    root_cause_validation: str              # statistical or observational evidence
    practical_significance: str             # how much of the problem it explains (§4.10.5)
    issues_and_barriers: str
    # Tier 2
    causal_hypothesis: dict                 # cross-phase ref -> Measure baseline (§4.7)
    ruled_out_causes: str                   # alternatives rejected, with rationale
    statistical_problem_statement: str      # moved here from Define (§4.10.5)
    process_owner_buyin: str                # owner accepts the root causes (§4.10.5)
    secondary_metrics: str
    # Gate metadata
    computation_results: list[dict] = []
    acknowledged_gaps:   list[str]  = []
    citations:           list[dict] = []
    uploads:             list[dict] = []


class ImproveOutput(BaseModel):
    """Gate document for the Improve phase."""
    # Tier 1
    selected_solution: str                  # criteria-based selection documented
    pilot_result: str                       # practical AND statistical significance
    experiment_justification: str           # DOE / simplified / none — and why (§4.10.7)
    issues_and_barriers: str
    # Tier 2
    solution_linked_to_root_cause: dict     # cross-phase ref -> Analyse root cause (§4.7)
    implementation_plan: str                # timeline, owner, resources
    explanatory_power: str                  # R-squared / variance explained (§4.10.5)
    process_owner_buyin: str                # owner accepts the solution (§4.10.5)
    secondary_metrics: str
    # Gate metadata
    computation_results: list[dict] = []
    acknowledged_gaps:   list[str]  = []
    citations:           list[dict] = []
    uploads:             list[dict] = []


class ControlOutput(BaseModel):
    """Gate document for the Control phase."""
    # Tier 1
    control_plan: dict                      # FIVE sub-plans — see §4.10.6
    post_improvement_metric: dict           # cross-phase ref -> Measure baseline (§4.7)
    issues_and_barriers: str
    # Tier 2
    improvement_delta: str                  # change from baseline
    financial_impact_verified: str          # quantified saving (book pp677-679)
    sustainability_check: str               # process for maintaining the gains
    handover_documented: str                # named process owner accepting
    lessons_learned: str                    # feeds the case index
    transferability: str                    # yokoten — feeds rag_lookup_case_history
    project_signoff: str                    # Champion + Belt + Finance (§4.10.5)
    secondary_metrics: str
    # Gate metadata
    computation_results: list[dict] = []
    acknowledged_gaps:   list[str]  = []
    citations:           list[dict] = []
    uploads:             list[dict] = []
```

**The four gate-metadata fields are on all five schemas, and always come
from the same four sources:**

| Field | Source | Finding |
|---|---|---|
| `computation_results` | `artifacts["computation_results"]` | §4.8 |
| `acknowledged_gaps` | `validation_stack.get_acknowledged_gaps()` | §3.7.1 |
| `citations` | `state["citations"]` | §4.2.3 |
| `uploads` | `state["uploads"]` | §4.2.3 |

`citations` and `uploads` were on `PhaseState` but missing from the
Output schemas in an earlier revision, which meant the evidence trail
reached state and then stopped — never arriving in the document that
records what the phase was grounded in.

#### 4.10.3 Gate assembly — all five phases

Run in `gate_apply`, after Belt approval. **No LLM call** — this is
Pydantic validation over values already captured.

```python
# -- DEFINE ------------------------------------------------------------
gate_document = DefineOutput(
    problem_statement=artifacts["problem_statement"],
    project_scope=artifacts["project_scope"],
    goal_statement=artifacts["goal_statement"],
    voc_summary=artifacts["voc_summary"],
    process_map_sipoc=artifacts["process_map_sipoc"],
    issues_and_barriers=artifacts["issues_and_barriers"],
    business_case=artifacts.get("business_case", ""),
    team=artifacts.get("team", ""),
    baseline_metric=artifacts.get("baseline_metric", ""),
    target_metric=artifacts.get("target_metric", ""),
    secondary_metrics=artifacts.get("secondary_metrics", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=validation_stack.get_acknowledged_gaps(),
    citations=state["citations"],
    uploads=state["uploads"],
)

# -- MEASURE -----------------------------------------------------------
gate_document = MeasureOutput(
    baseline_mean=artifacts["baseline_mean"],
    data_collection_plan=artifacts["data_collection_plan"],
    xy_matrix_summary=artifacts["xy_matrix_summary"],
    vital_few_xs=artifacts["vital_few_xs"],
    detailed_process_map=artifacts["detailed_process_map"],
    stability_assessment=artifacts["stability_assessment"],
    issues_and_barriers=artifacts["issues_and_barriers"],
    baseline_sigma=artifacts.get("baseline_sigma", ""),
    measurement_system_validated=artifacts.get("measurement_system_validated", ""),
    secondary_metrics=artifacts.get("secondary_metrics", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=validation_stack.get_acknowledged_gaps(),
    citations=state["citations"],
    uploads=state["uploads"],
)

# -- ANALYSE ---------------- causal_hypothesis is a dict --------------
gate_document = AnalyseOutput(
    root_cause_statement=artifacts["root_cause_statement"],
    root_cause_validation=artifacts["root_cause_validation"],
    practical_significance=artifacts["practical_significance"],
    issues_and_barriers=artifacts["issues_and_barriers"],
    causal_hypothesis=artifacts.get("causal_hypothesis", {}),
    ruled_out_causes=artifacts.get("ruled_out_causes", ""),
    statistical_problem_statement=artifacts.get("statistical_problem_statement", ""),
    process_owner_buyin=artifacts.get("process_owner_buyin", ""),
    secondary_metrics=artifacts.get("secondary_metrics", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=validation_stack.get_acknowledged_gaps(),
    citations=state["citations"],
    uploads=state["uploads"],
)

# -- IMPROVE ----------- solution_linked_to_root_cause is a dict -------
gate_document = ImproveOutput(
    selected_solution=artifacts["selected_solution"],
    pilot_result=artifacts["pilot_result"],
    experiment_justification=artifacts["experiment_justification"],
    issues_and_barriers=artifacts["issues_and_barriers"],
    solution_linked_to_root_cause=artifacts.get("solution_linked_to_root_cause", {}),
    implementation_plan=artifacts.get("implementation_plan", ""),
    explanatory_power=artifacts.get("explanatory_power", ""),
    process_owner_buyin=artifacts.get("process_owner_buyin", ""),
    secondary_metrics=artifacts.get("secondary_metrics", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=validation_stack.get_acknowledged_gaps(),
    citations=state["citations"],
    uploads=state["uploads"],
)

# -- CONTROL ---- control_plan is a dict of five sub-plans (§4.10.6) ---
gate_document = ControlOutput(
    control_plan=artifacts["control_plan"],
    post_improvement_metric=artifacts.get("post_improvement_metric", {}),
    issues_and_barriers=artifacts["issues_and_barriers"],
    improvement_delta=artifacts.get("improvement_delta", ""),
    financial_impact_verified=artifacts.get("financial_impact_verified", ""),
    sustainability_check=artifacts.get("sustainability_check", ""),
    handover_documented=artifacts.get("handover_documented", ""),
    lessons_learned=artifacts.get("lessons_learned", ""),
    transferability=artifacts.get("transferability", ""),
    project_signoff=artifacts.get("project_signoff", ""),
    secondary_metrics=artifacts.get("secondary_metrics", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=validation_stack.get_acknowledged_gaps(),
    citations=state["citations"],
    uploads=state["uploads"],
)
```

**The access pattern encodes the tier**, and that is the point:

| Field kind | Access | If absent |
|---|---|---|
| Tier 1 | `artifacts["field"]` | **`KeyError`** — correct, Layer 2b should have blocked the gate (§3.7.1) |
| Tier 2 | `artifacts.get("field", "")` | Empty string — records that the Belt proceeded without it |
| Cross-phase dict | `artifacts.get("field", {})` | Empty dict |

**A Tier 1 `KeyError` at gate assembly is a bug in the validation stack,
not in the Belt's work.** It means Layer 2b passed a gate missing a field
it is required to block on. Letting it raise is deliberate: the
alternative — defaulting Tier 1 to `""` — would write a gate document
with a silently empty required field into the store, where the next
phase would build on it.

**`post_improvement_metric` is Tier 1 but assembled with `.get(…, {})`.**
That is not an inconsistency. Layer 2b enforces its presence; the `.get`
guards the *shape* so a malformed capture fails Pydantic validation with
a readable error rather than a `KeyError` that says nothing about what
was wrong with it.

**Then the two writes** (§3.6.1):

```python
store.put(("projects", case_id, "artifacts"), phase_name, gate_document.dict())
return {"final": gate_document.dict(), "gate_attempts": 0, "validator_feedback": []}
```

#### 4.10.4 Field flow — capture to store, verified

**Every field the coach can emit reaches the store, and every schema
field is reachable.** The chain is
`CoachingResponse.fields_captured` → `artifacts[field_name]` →
`{Phase}Output` → `store.put` → next phase's input mapper.

| Phase | Schema fields | Tier 1 | Tier 2 | Cross-phase dict | Gate metadata |
|---|---|---|---|---|---|
| Define | 15 | 6 | 5 | — | 4 |
| Measure | 14 | 7 | 3 | — | 4 |
| Analyse | 13 | 4 | 5 | 1 (`causal_hypothesis`) | 4 |
| Improve | 13 | 4 | 5 | 1 (`solution_linked_to_root_cause`) | 4 |
| Control | 15 | 3 | 8 | 1 (`post_improvement_metric`) | 4 |

**Verified properties, all five phases:**

- Every schema field is set by that phase's gate assembly — **no field
  is left unassembled**, so nothing in a schema can silently fail to
  reach the store
- Every Tier 1 field is reachable by the coach through
  `CoachingResponse.fields_captured`
- Every Tier 2 field is either coach-capturable or produced by a
  computation tool into `artifacts["computation_results"]` —
  `baseline_sigma` (`calculate_sigma_level`),
  `measurement_system_validated` (`calculate_grr`), `improvement_delta`
  (`post_improvement_cpk`), `explanatory_power` (`linear_regression`)
- **Every Tier 1 field is coach-capturable**, including the three
  structured dicts — `CoachingResponse.value: Any` carries a dict as
  readily as a string (§4.10.1), so the coach populates
  `process_map_sipoc` sub-field by sub-field across turns and emits the
  assembled dict. `stability_assessment` is coach-capturable **and**
  supported by `xbar_r_chart_limits` output in `computation_results`
- Every non-metadata field is `str` except the three cross-phase dicts,
  which `CoachingResponse.value: Any` carries without loss
- `PhaseState.artifacts` is `dict[str, Any]`, so it holds both string
  fields and dict-typed cross-phase fields with no type conflict
- Gate metadata always comes from the same four sources, in every phase

**Four Tier 1 fields are dicts**, and they fall into two kinds:

| Field | Phase | Kind |
|---|---|---|
| `post_improvement_metric` | Control | Cross-phase reference (§4.7) |
| `control_plan` | Control | Structured — five sub-plans (§4.10.6) |
| `process_map_sipoc` | Define | Structured — six sub-fields (§4.10.7) |
| `detailed_process_map` | Measure | Structured — six sub-fields (§4.10.7) |

Layer 2b enforces presence for all four. Only the cross-phase reference
is assembled with `.get(…, {})` to guard its shape (§4.10.3); the three
structured dicts are Tier 1 and use bracket access like any other Tier 1
field. **The grader checks that every sub-field of a structured dict is
populated** — a `process_map_sipoc` with four of six keys filled is the
partial-map failure §4.10.7 exists to catch.

### 4.10.5 Fields added from the eBook extraction

The five BB eBook extractions under `skills/extraction/` identified 57
deliverables with no corresponding field. Six cross-cutting decisions
resolve 25 of them; the rest are handled by SKILL.md coaching content or
by mechanisms that already exist.

#### `secondary_metrics` — all five phases, Tier 2

**A named eBook deliverable in every one of the five phases**, and
Control's closing checklist says "repeat same process for secondary
metrics." Nothing recorded them.

> "Secondary Metrics are put in place to measure potential changes that
> may occur as a result of making changes to our Primary Metric. They
> will measure ancillary changes in the process, **both positive and
> negative**." — book p57

**This is the field that catches a project which succeeded on its own
terms and did damage elsewhere.** A cycle-time improvement that raised
the error rate passes every other check in the system. Tier 2, because a
Belt may legitimately conclude there are none; the grader's warning is
*"you haven't identified what could get worse if this improvement
succeeds."*

#### `issues_and_barriers` — all five phases, **Tier 1**

A named eBook deliverable in every phase, and a General gate question in
every phase. **Gate-required**, because every real project has blockers
and a Belt who reports none has not looked.

**Distinct from `acknowledged_gaps`, and the two must not be merged:**

| | `issues_and_barriers` | `acknowledged_gaps` |
|---|---|---|
| Written by | The **Belt** | The **system** (§3.7.1) |
| Records | Real-world project blockers — sponsor availability, data access, team disagreement, resource constraints | Tier 2 schema fields the Belt chose to skip |
| Tier | **1** — gate-required | Gate metadata, not a tier |

If there genuinely are none, the Belt writes *"none identified at this
stage"* — a conscious statement rather than a silent omission, which is
the same principle `acknowledged_gaps` applies to skipped fields.

**The next phase's planner reads it from the store** and factors it into
coaching: *"the Belt reported IT will not grant database access — data
collection will be difficult."*

#### `xy_matrix_summary` and `vital_few_xs` — Measure, both **Tier 1**

The eBook's roadmap labels the Measure → Analyse hand-off "**Vital Few
X's Identified**", and Analyse's entry condition is that same list.
Neither the prioritisation nor its result was recorded anywhere, so the
labelled hand-off between two phases had no carrier.

- `xy_matrix_summary` — evidence that prioritisation actually happened.
  Gate question: *"Is there a completed X-Y Matrix?"*
- `vital_few_xs` — the ranked result. Gate question: *"Which X's are you
  taking into Analyse, and why?"*

**Both Tier 1.** Without knowing which X's are the vital few, Analyse
guesses at root causes instead of investigating data-driven priorities —
and the same question is then asked again at Analyse and at Control, with
nothing to answer it from.

**The Analyse planner reads both from the store** and uses them to focus
root-cause coaching.

#### `practical_significance` — Analyse, **Tier 1**

The eBook gates root causes on **two** tests in series (book p417):
statistically significant, *then* practically significant. Failing either
routes back.

> A root cause significant at p=0.001 that explains 0.1% of the problem
> is not worth building an Improve solution on.

`root_cause_validation` covers the statistical half. This is the other
half, and Improve's `pilot_result` rubric already demands both — so
Analyse was the asymmetric phase. Making it symmetric means the Belt
tests practical significance **before** designing a solution rather than
discovering the problem at the Improve pilot.

Coaching form: *"Your hypothesis test shows this is statistically
significant. But how much of the problem does it explain? If you fixed
this completely, how far would the error rate drop?"*

#### `statistical_problem_statement` — Analyse, Tier 2 — **relocated**

**Moved from Define (BB-only) to Analyse (all Belts).** The eBook asks
*"What is the statement of Statistical Problem?"* in the **Analyse** gate
checklist, of every Belt, immediately before the hypothesis tests it
governs. Two corrections in one: the phase was wrong and the belt-level
restriction was not in the source.

§3.7.2's Black-Belt-only list no longer carries it.

#### `process_owner_buyin` — Analyse and Improve, Tier 2

The eBook asks *"Does the process owner buy into these Root Causes?"* at
the Analyse gate and *"Present statistical promise to process owner"* at
the Improve gate. `handover_documented` covers owner acceptance at
**Control** — by which point disagreement is expensive.

A technically correct root cause the owner rejects does not survive
Improve; a solution the owner has not seen does not survive
implementation.

#### `explanatory_power` — Improve, Tier 2

Gate question: *"How much of the problem have you explained with these
X's?"* R², variance explained, or an equivalent statement. This is what
distinguishes a solution addressing the dominant driver from one
addressing a marginal factor, and it is the natural companion to
Analyse's `practical_significance`.

#### `project_signoff` — Control, Tier 2

Gate question, asked of every Belt in the eBook's **General** section:
*"Do the Champion, the Belt and Finance all agree this project is
complete?"* Control's roadblock list leads with *"Lack of project sign
off."*

§3.7.2 previously carried three-party sign-off as a Tier 2 rubric item
with **no field** — so the gate asked a question nothing could answer.
`handover_documented` covers the process owner only; this covers the
Champion and Finance.

#### FMEA — deliberately NOT in any schema

**No `fmea_summary` field exists in any phase, and none may be added.**
The eBook names FMEA as a Measure deliverable, an Analyse update step and
a Control monitoring mechanism — three phases, three asks. The extraction
flagged this chain as unrecorded end to end (gaps M-4, A-4, C-4).

**The decision is to not track it, and the reasoning is about fit rather
than effort.** FMEA is heavy manufacturing methodology built around
severity × occurrence × detection scoring of physical failure modes.
Agent Improve's typical case is a service or transactional DMAIC project,
where:

- **`xy_matrix_summary` and `vital_few_xs` already carry the
  prioritisation job** an FMEA would do, without the RPN overhead.
- The eBook's own FMEA taxonomy (System, Design DFMEA, Process PFMEA,
  Equipment — book p124) is oriented to product and equipment failure
  modes, not to invoice errors or onboarding gaps.
- Requiring it would push every Belt through a heavy artefact to satisfy
  a field, which is exactly the mechanical field-filling §3.7.1 exists to
  prevent.

**If a Black Belt does perform an FMEA, it lives in `uploads`** as an
attached document, and the Black Belt SKILL.md may present it as an
available technique. The schema does not track it, the grader does not
ask for it, and no gate blocks on it.

**This closes the FMEA chain by declining it, not by covering it** — a
distinction worth preserving in the record, because a future reader
finding three eBook asks and no field should find this paragraph rather
than assume an omission.

#### What the extraction raised that got no field

Recorded so the decisions are not re-litigated:

| Gap | Decision |
|---|---|
| Process map persistence (D-2, M-5) | **Superseded in v2.2.12** — now `process_map_sipoc` and `detailed_process_map`, both Tier 1 (§4.10.7) |
| Stakeholder analysis (D-3) | Define SKILL.md coaching content, distinct from `team` |
| Project plan (D-4, M-10, A-11, I-11) | Cross-phase coaching content, not a captured field per phase |
| Short- and long-term capability (M-1) | Coaching guidance to address both; numbers land in `computation_results` via `calculate_cpk` |
| Stability assessment (M-2) | **Superseded in v2.2.12** — now `stability_assessment`, Tier 1 (§4.10.7) |
| Experiment justification (I-1, I-2) | **Superseded in v2.2.12** — now `experiment_justification`, Tier 1 (§4.10.7). The valuable answer is still often "no DOE needed"; the field records the decision, not an experiment |
| Lean opportunities / waste (D-6) | Define SKILL.md coaching content |
| Benefits deferral date (D-7) | Coaching inside `business_case` |
| Finance involvement at Define (D-8) | Coaching content; the recorded sign-off is `project_signoff` at Control |

### 4.10.6 `control_plan` — one field, five sub-plans

**`control_plan` is a `dict`, not a `str`.** The eBook defines the
Control Plan as **five distinct plans** (book p664), each with its own
content and its own develop-then-implement step on the roadmap:

```python
control_plan: dict = {
    "documentation":    str,   # updated process maps, SOPs, training manuals
    "monitoring":       str,   # what charts, what frequency, what limits, who checks
    "response":         str,   # what happens when monitoring signals a problem
    "training":         str,   # who needs training, in what format, verified how
    "aligning_systems": str,   # HR, IT, budget changes needed to sustain
}
```

> "The **5 elements** of a Control Plan include the documentation,
> monitoring, response, training and aligning systems and structures."
> — book p664

**Tier 1. The gate requires the dict, and the grader checks all five
sub-plans are populated.** A single string could not show that four were
done and one was skipped — which is precisely what the eBook's ten
roadmap steps (five develop, five implement) are designed to surface, and
the most common real Control failure is a Training Plan that was written
and never delivered.

**The Belt works through them one at a time during coaching**, and the
Control SKILL.md must explain each sub-plan and guide the Belt through
it. This is a coaching sequence, not a form to fill at the gate.

**Four extraction gaps close with this one change** — C-1 (five
elements), C-2 (develop vs implement), C-5 (monitoring method), C-15
(mistake-proofing, which belongs inside `monitoring` and `response`).

### 4.10.7 Process maps, stability, and experiment justification

Three gaps the extraction had assigned to SKILL.md coaching content were
**promoted to schema fields**, all Tier 1. Each was reclassified for the
same reason: a coaching prompt produces a conversation, and a
conversation cannot be read by the next phase's planner or checked by the
grader.

#### `process_map_sipoc` — Define, **Tier 1**, dict

```python
process_map_sipoc: dict = {
    "suppliers":     str,   # who provides inputs
    "inputs":        str,   # what enters the process
    "process_steps": str,   # 5–7 high-level steps
    "outputs":       str,   # what the process produces
    "customers":     str,   # who receives outputs
    "process_kpis":  str,   # what is measured at each step
}
```

> "A process map is vital — if not visualised it will lead to more issues
> later… **Far too often Belts capture only segments of the process**,
> which in an improvement project are vital, as otherwise there is no way
> to measure the improvement."

**The partial-map failure is what makes this Tier 1.** A Belt who maps
steps 3–5 of a seven-step process produces a project that cannot show
improvement, because the baseline never covered the whole thing. The
failure is invisible at Define and expensive at Control.

**Coach responsibilities:**

- Guide the Belt through each SIPOC element in turn
- **Validate completeness** — end to end, no missing steps, inputs trace
  to suppliers, outputs reach customers
- **Challenge fragments** — *"you've described steps 3 to 5; what happens
  before and after?"*
- Verify consistency with `project_scope`
- **If the Belt uploads an existing process diagram**, decompose it into
  the structured SIPOC form and validate it rather than accepting the
  image as the deliverable

#### `detailed_process_map` — Measure, **Tier 1**, dict

```python
detailed_process_map: dict = {
    "steps":              str,   # detailed steps, expanded from the SIPOC
    "cycle_times":        str,   # timing per step
    "resources":          str,   # who and what is involved per step
    "value_vs_waste":     str,   # which steps add value, which are waste (VSM)
    "measurement_points": str,   # where data is collected per step
    "baseline_kpis":      str,   # current KPIs per step, before improvement
}
```

**Coach responsibilities:**

- Check the Measure map against Define's SIPOC — **does it expand
  correctly?** A detailed map that does not decompose the Define steps is
  a different process
- Verify `measurement_points` align with `data_collection_plan`
- Use `value_vs_waste` to surface improvement candidates
- `baseline_kpis` establish the "before" that Control's "after" is
  measured against

#### The before/after KPI chain

**Three fields across three phases carry one measurement thread**, and
this is what makes "we improved it" checkable rather than asserted:

| Phase | Field | Role |
|---|---|---|
| Define | `process_map_sipoc["process_kpis"]` | **What** is measured, per step |
| Measure | `detailed_process_map["baseline_kpis"]` | The **before** values |
| Control | `post_improvement_metric` | The **after** values (§4.7) |

**The grader verifies the same measurement points carry different
values.** A project whose Control metrics measure something Define never
listed has moved the goalposts; a project whose after-values sit on
different steps than its before-values has not measured an improvement.

#### `stability_assessment` — Measure, **Tier 1**

**The eBook is explicit: check stability BEFORE capability** (book p230).
An unstable process has special causes, and a baseline Cpk computed
across them is not a capability figure — it is an average of two
different processes.

Was previously a Tier 2 rubric criterion with no field and a strong
warning (§13.2). The warning was right and the tier was not: the eBook
sequences it as a precondition, not a recommendation.

**Coaching sequence for the Measure SKILL.md:**

```
run stability check
  → unstable?  → identify special causes → address or acknowledge
  → stable?    → proceed to capability calculation
```

#### `experiment_justification` — Improve, **Tier 1**

**The Belt must state one of three answers, and all three are valid:**

| Answer | When |
|---|---|
| "DOE conducted — here's why, and what we found" | Full designed experiment |
| "Simplified experiment — one factor at a time, before/after comparison" | Business Belts without DOE training |
| "No experiment needed — the solution follows directly from root cause analysis, here's why" | **Most common in service projects** |

**The field does not require an experiment. It requires a decision.**
The eBook's most-repeated Improve warning is *"do not force Designed
Experiments"* and its own estimate is that over 80% of projects find
their solution in Analyse. Tier 1 here means the Belt consciously
reasoned about whether an experiment was needed — the failure this
catches is not skipping DOE, it is drifting past the question.

**The Improve SKILL.md carries a simplified DOE explanation** so a Belt
without statistical training can make the choice in plain language rather
than defaulting to "no" out of unfamiliarity.

---

## 5. Folder Structure (v2.2 target)

```
agent-improve/
backend/
  app.py                          FastAPI app, lifespan, fail-fast env validation
  core/
    state.py                      SupervisorState
    substate.py                   PhaseState + per-phase variants
    graph.py                      Supervisor graph — static edges
    llm.py                        get_llm() factory, role → deployment map
    checkpointer.py               AzureBlobCheckpointSaver
    store.py                      AzureBlobStore                        (NEW)
    reliability.py                CircuitBreaker, backoff strategies    (NEW)
    errors.py                     AgentImproveError schema              (NEW)
    cache.py                      Azure Redis response cache            (NEW)
    config.py                     Settings
    prompts.py                    Prompts, rubrics, constraint sets
    citations.py                  Citation models
    diagrams.py                   Diagram type schemas
    tracing.py                    LangSmith integration
  middleware/                                                           (NEW)
    grader.py                     DMAICGraderMiddleware
    skills.py                     DMAICSkillsMiddleware
    state_injection.py            BeforeModelStateInjection (before_agent hook)
    contradiction.py              ContradictionDetectionMiddleware
    coherence.py                  CoherenceMiddleware
  validation/                                                           (NEW)
    gate_validator.py             DMAICGateValidator (static methods)
    coherence.py                  Layer 2a
    constraints.py                Layer 2c
    schemas.py                    Verdict models
  phases/
    define/
      graph.py                    Subgraph compilation (no checkpointer)
      nodes.py                    planner, executor, validation_stack
      gate.py                     gate_review_node, gate_apply_node
      mappers.py                  input/output boundary mappers         (NEW)
      schema.py                   DefinePhaseInput, DefineOutput
    measure/  analyse/  improve/  control/          (same shape)
  knowledge/
    retriever.py                  Azure AI Search clients
    tools.py                      The universal seven
    computation.py                The 20 per-phase computation tools    (NEW)
    fusion.py                     reciprocal_rank_fusion                (NEW)
    tool_args.py                  Pydantic arg schemas
  storage/
    blob.py                       Case blob CRUD (lifecycle only)
    models.py                     CaseDocument, PhaseRecord, RegistryEntry
  gateway/
    routes.py                     Thin transport
    schemas.py                    API envelopes
    sse.py                        SSE streaming
  escalate.py                     Escalation subgraph
  upload/
    agent.py
    classifier.py
skills/                                                                 (NEW)
  dmaic-define-phase/SKILL.md
  dmaic-measure-phase/SKILL.md
  dmaic-analyse-phase/SKILL.md
  dmaic-improve-phase/SKILL.md
  dmaic-control-phase/SKILL.md
eval/                                                                   (NEW)
  dataset.py                      LangSmith evaluation dataset
  evaluators.py                   Deterministic + LLM-judge evaluators
ui/
  index.html
menu.py                           Developer orchestrator (replaces start.ps1)
CLAUDE.md
ARCHITECTURE.md
REFACTORING_AGENT_IMPROVE.md
requirements.txt
```

**Deleted from v2.1.1:** `phases/{phase}/orchestrate.py`,
`phases/{phase}/validate.py`, `phases/{phase}/analyse.py` stub, and
the `phase_router` node.

---

## 6. Storage and Persistence

### 6.1 Two systems, not one

| System | Scope | Lifecycle | Injected |
|---|---|---|---|
| **Checkpointer** | Thread-scoped (one project) | Automatic — LangGraph writes after every node | `graph.compile(checkpointer=...)` |
| **Store** | Cross-thread, cross-phase | **Explicit** — nodes call `put`/`get` | `graph.compile(store=...)` + node parameter |

The asymmetry is deliberate: conversation history is structural, so
LangGraph manages it; long-term memory is a product decision, so we
write the code. **Passing only a checkpointer is the most common
architecture mistake.**

Both attach to the **parent graph only**. Phase subgraphs receive
neither.

### 6.2 Checkpointer — phased

| Stage | Implementation |
|---|---|
| During the refactor | `AzureBlobCheckpointSaver` — `core/checkpointer.py` |
| Post-refactor, pre-production | `PostgresSaver` |

**`InMemorySaver` is not used at any stage.**

- Container: `agent-improve-cases`
- Prefix: `checkpoints/{case_id}/`
- Files: `latest.json` (active) + `history/{checkpoint_id}.json`

**Known limitation.** The Blob implementation was not tested for
concurrent access, and Azure Blob has no row-level locking. Acceptable
for single-developer refactoring; **not** acceptable for production.
`PostgresSaver` is the officially maintained path, handles concurrency
correctly, is SQL-queryable for debugging, and is updated by the
LangChain team on every LangGraph release.

**Migration cost:** constructor and connection string. Both sides are
defined by LangGraph interfaces, so nothing above the persistence layer
changes. Run the existing unit tests against PostgreSQL before
switching.

#### 6.2.1 On-blob checkpoint format

Each checkpoint blob is a JSON document with this envelope:

```json
{
  "checkpoint_type": "msgpack",
  "checkpoint_data": "<base64-encoded msgpack bytes>",
  "metadata_type": "msgpack",
  "metadata_data": "<base64-encoded msgpack bytes>",
  "checkpoint_id": "<id>",
  "parent_checkpoint_id": "<id|null>"
}
```

The base64 wrapping is required because
`JsonPlusSerializer.dumps_typed()` (`langgraph-checkpoint` 4.x) returns
binary msgpack rather than utf-8 text. Wrapping the bytes in base64
keeps the blob a valid JSON document while preserving exact round-trip
semantics.

*This was surfaced during commit 2.1 implementation and is preserved
from v2.1.1 — it is a real deviation from the initial spec.*

### 6.3 `AzureBlobStore` — cross-phase artifacts

`core/store.py`, implementing `langgraph.store.base.BaseStore`.

```python
class AzureBlobStore(BaseStore):
    """BaseStore backed by Azure Blob Storage. Transitional —
    migrates to PostgresStore alongside the checkpointer."""

    def put(self, namespace: tuple[str, ...], key: str, value: dict) -> None: ...
    def get(self, namespace: tuple[str, ...], key: str) -> Item | None: ...
    def search(self, namespace: tuple[str, ...], *, query: str | None = None,
               limit: int = 10) -> list[Item]: ...
    def delete(self, namespace: tuple[str, ...], key: str) -> None: ...
```

**Namespace convention:** `("projects", case_id, <kind>)`

| Namespace | Keys | Contents |
|---|---|---|
| `("projects", case_id, "case")` | `"record"` | Case framing loaded once at session start — title, department, belt level, leader, target date. Read by `define_input_mapper` (§4.3) |
| `("projects", case_id, "artifacts")` | `"define"`, `"measure"`, … | **Each phase's approved gate document** — written by `gate_apply_node` (§3.6.1) |
| `("projects", case_id, "step_log")` | timestamped | Append-only cross-phase audit trail |

**The `gate_documents` namespace is retired** (§3.6.1). It duplicated
`artifacts` under a second key, and two keys holding the same content
is a question about which one is authoritative that the design could not
answer. A phase's approved artifacts and its gate document are the same
object.

**The `case` namespace is a session-start copy, not a second system of
record.** `cases/case_{id}.json` (§6.4) remains authoritative; the store
holds the framing fields so that mappers depend on `BaseStore` alone.
It is written once per session and never mid-conversation.

- Container: `agent-improve-cases`
- Prefix: `store/projects/{case_id}/{kind}/{key}.json`
- `case_id` is the same value as the graph's `thread_id` (§4.1.1)

**Complete physical layout**, across both persistence systems:

```
Azure Blob container: agent-improve-cases

store/projects/{case_id}/case/record.json
store/projects/{case_id}/artifacts/define.json
store/projects/{case_id}/artifacts/measure.json
store/projects/{case_id}/artifacts/analyse.json
store/projects/{case_id}/artifacts/improve.json
store/projects/{case_id}/artifacts/control.json
store/projects/{case_id}/step_log/{timestamp}.json

checkpoints/{case_id}/latest.json
checkpoints/{case_id}/history/{checkpoint_id}.json

cases/case_{case_id}.json                    ← system of record (§6.4)
registry.json
uploads/{case_id}/{file}
```

Each `artifacts/{phase}.json` holds the complete approved gate document
for that phase — captured fields as strings (§4.6), the three
cross-phase reference dicts where they apply (§4.7),
`computation_results` (§4.8), `citations`, `uploads`, and
`acknowledged_gaps` (§3.7.1).

**Ordering constraint:** implement the store **after** `thread_id` is
wired through `graph.ainvoke` (Step 6). A store is meaningless without
working checkpoint persistence — if the graph cannot resume, there is
no second session for stored artifacts to serve.

**The store is not the case index.** Cross-*case* retrieval for yokoten
is `rag_lookup_case_history` against `improve_case_index` (§7.3). The
store carries cross-*phase* data within one project. Two mechanisms,
two purposes, no overlap.

### 6.4 Case records — the system of record

- Container: `agent-improve-cases`
- Prefix: `cases/`
- Files: `case_{id}.json`, `registry.json`, `uploads/{case_id}/{file}`
- Owner: `storage/blob.py` → `ImproveBlobClient`
- Written on create, gate pass, upload — **never per turn**

### 6.5 Concurrency and atomicity

Checkpoint writes use blob ETag conditional writes; concurrent turns on
the same case are detected and the second retries. This is the
mitigation that the `PostgresSaver` migration replaces properly.

Gate-pass case blob write and registry update remain two separate
writes. Both are covered by the node's `error_handler` (§9.2), which is
the ratified answer to what v2.1.1 listed as "Saga pattern for
case-vs-registry atomicity — deferred."

### 6.6 Response cache — Azure Cache for Redis

**New infrastructure component, not yet provisioned.**

- Purpose: Level 3 of the fallback chain (§9.3)
- Stores: recent retrieval results keyed by query hash + phase; recent
  coaching responses for similar questions
- **Session-scoped, not global** — different projects have different
  context, and a cached answer from another Belt's project is worse
  than no answer
- Cache-key design, TTL, and invalidation follow the principles in
  REFACTORING_AGENT_IMPROVE.md §65. Methodology retrieval is stable
  (the eBook does not change); evidence and case history are not.
  A gate approval changes the project's artifacts and must invalidate
  the affected entries.

### 6.7 Why Blob and not Cosmos / Tables / SQLite

- Already provisioned, secured, and monitored
- Single Azure SDK dependency
- Append-only checkpoint history → simple time-travel debugging
- `BaseCheckpointSaver` / `BaseStore` interfaces make the PostgreSQL
  migration a constructor change

---

## 7. Azure AI Search Indexes — CANONICAL SCHEMAS

**This section is the single canonical record of the index schemas.**
CLAUDE.md §7.3 references it. Any schema change lands here first, in
the same commit as the Azure AI Search change.

### 7.1 `improve_knowledge_index` — methodology (semantic memory)

LSS Black Belt eBook. Static: same for every project, every Belt.
Never updated at runtime.

| Field | Type | Role |
|---|---|---|
| `id` | String | Key |
| `content` | String | Chunk text |
| `content_vector` | SingleCollection (3072d) | **Vector field** |
| `metadata` | String | JSON blob |
| `source_file` | String | **Returned for citation** — not a filter |
| `phase_relevance` | String | **Filter** — see below |
| `page_number` | Int32 | **Returned for citation** — not a filter |

**Retrieved by:** `rag_lookup_methodology(query, phase, top_k)`

**Filter:**
```
phase_relevance eq '{phase}' or phase_relevance eq 'general'
```
The second term is required: cross-phase eBook content must remain
reachable from any phase, so filtering strictly to the current phase
would over-narrow.

**Enumeration confirmed against the live index (Aug 2026)** — this
closes the former open item, and corrects the value:

| `phase_relevance` | Docs |
|---|---:|
| `measure` | 378 |
| `analyse` | 348 |
| `general` | 218 |
| `define` | 156 |
| `control` | 135 |
| `improve` | 134 |
| **total** | **1369** |

**The cross-phase bucket is `general`, not `all`.** No document carries
`all`; earlier revisions of this section specified it, which would have
silently excluded all 218 cross-phase documents from every phase-filtered
query — a wrong-results bug, not an error. The implementation constant is
`retriever.CROSS_PHASE_RELEVANCE`.

**The field is `phase_relevance`, not `phase`.** There is no `phase`
field on this index; Azure rejects the entire query if one is requested.
See §7.1.1.

#### 7.1.1 Retrieval failure is not an empty result

**All three retrieval functions in `knowledge/retriever.py` —
`search_knowledge`, `search_cases`, `search_evidence` — return `[]` only
when the search ran and matched nothing.** When the search itself fails
they raise `KnowledgeSearchError` (`core/errors.py`), carrying an
`AgentImproveError` (§12.3).

This distinction is load-bearing, and its absence hid a real bug. The
function previously filtered on `phase eq '{phase}'` — a field that does
not exist — so Azure rejected every phase-filtered query with
`HttpResponseError`. A bare `except Exception` turned that into `[]`, and
the caller rendered `[]` as *"No relevant methodology content found."*
Phase-filtered methodology retrieval had therefore never returned a
single document, and it reported the corpus as silent rather than itself
as broken.

Binding consequences:

- **Never catch bare `Exception` around a retrieval call.** Catch
  `retriever.RETRIEVAL_EXCEPTIONS` and classify via
  `retriever._search_error()`; `retriever._fail()` is the single
  classify-log-raise exit path all three functions share.
- **`RETRIEVAL_EXCEPTIONS` covers two services, not one.** Azure AI Search
  raises `HttpResponseError` / `ServiceRequestError` /
  `ClientAuthenticationError`; the query-embedding call to Azure OpenAI
  raises `OpenAIError`. The embedding call sits inside the same `try`, so
  omitting it would let a raw provider exception escape and take down the
  coaching turn. Embedding failures carry an `EMBEDDING_` code prefix so
  the failing service is readable in the log.
- **`ClientAuthenticationError` must be tested before `HttpResponseError`**
  — it is a subclass, so the reverse order classifies a bad key as a
  generic 4xx and marks a permanent auth failure retryable.
- **A 4xx from Search is `permanent` / `do_not_retry`.** It means a
  malformed query — our bug. Retrying spends latency to fail identically.
  Only 429 and 5xx are `transient`.
- **Materialise results inside the `try`.** `SearchClient.search()` returns
  a lazy pager; the HTTP call fires on iteration, so a list comprehension
  moved outside the `try` would raise unclassified.
- **Filter values are OData-escaped** (`'` → `''`) in `_phase_filter` and
  on `case_id` in `search_evidence`.
- **No coach-facing failure message may read as an absence of content.**
  Each of the three tools returns an explicit retrieval-failure string
  telling the coach not to claim the methodology is silent / no precedent
  exists / nothing was uploaded, and not to cite what it could not
  retrieve. The three failure strings are distinct from the three
  empty-result strings — that pairing is the whole point.
- **Node-level callers degrade, they do not propagate.**
  `build_knowledge_context` returns `None`, and `_generate_sipoc_draft`
  falls through to generating the SIPOC from problem fields. Coaching
  continues ungrounded rather than failing — the Search-breaker posture in
  §9.4. Both catch `KnowledgeSearchError` specifically; a bare `except`
  there would re-swallow exactly what this contract exists to surface.

**`step_log` wiring is outstanding.** `AgentImproveError.to_step_log_entry()`
already emits the §4.4 dict shape and is logged through `logging` today,
but `step_log` does not exist on `ImproveGraphState` — it arrives with
`PhaseState` in step 4.1. At that point the node holding the error appends
that same dict; no reshaping.

#### 7.1.2 Ingestion contract — how a value becomes a filterable field

Owned by `scripts/ingest_knowledge.py`. Two rules, both of which have
already produced a silent failure.

**Rule 1 — the metadata key name is the field name.** Documents are
written via LangChain's `AzureSearch.add_texts`, which stores the whole
metadata dict as a JSON blob in `metadata` and then promotes individual
keys to top-level fields with:

```python
additional_fields = {k: v for k, v in metadata.items()
                     if k in [x.name for x in self.fields]}
```

A key is promoted **only if its name matches a field**. The script
originally emitted `phase`, which is not a field on this index, so
`phase_relevance` was never written by it and phase filtering could not
work. There is no error for this — the value lands in the blob, where
`$filter` cannot see it.

**Rule 2 — `self.fields` is what the client was constructed with, not the
live schema.** LangChain never introspects the index. Left to its default,
`self.fields` is only `[id, content, content_vector, metadata]`, so Rule 1
can never match `source_file`, `phase_relevance`, or `page_number` however
carefully they are named. `get_knowledge_vectorstore()` therefore passes
`fields=KNOWLEDGE_INDEX_FIELDS` (`knowledge/retriever.py`), declaring the
real schema. Passing `fields` is safe on an existing index — LangChain
inspects it only when the index is absent, so it cannot mutate a schema.

Renaming the key without Rule 2, or applying Rule 2 without the rename,
both leave the index unfilterable. **They only work together.**

`char_count` is deliberately left unpromoted and lives in the blob only,
matching the shape of the documents already in the index.

**Document keys are deterministic** — `md5(source_file_page_chunkidx)`,
passed explicitly via `ids=`. LangChain generates a random UUID key when
none is given, which would make every re-ingest duplicate the corpus
instead of upserting it.

**Chunking is per page, never across pages.** `page_number` is a citation
field (§13); a chunk spanning a page boundary could not be cited honestly.
Long pages split at `CHUNK_CHARS` with `CHUNK_OVERLAP_CHARS` overlap.

##### Phase mapping — per-chunk keywords, not chapters

**`phase_relevance` is assigned by scoring each chunk against
`PHASE_KEYWORDS`; the highest-scoring phase wins, and a chunk matching
nothing becomes `general`.** It is not a chapter or section mapping. That
was checked against the live corpus rather than assumed:

- the BB eBook PDF carries **no outline or bookmarks**, so there is no
  chapter structure to read;
- DMAIC terms do not appear as sustained page headings;
- every 50-page band holds a **mix** of phases, where a chapter mapping
  would make each band almost entirely one phase:

| Pages | Top three |
|---|---|
| 100–149 | define 28 · analyse 25 · general 21 |
| 300–349 | analyse 44 · general 6 · measure 4 |
| 600–649 | measure 39 · control 34 · improve 9 |

The *dominant* phase per band does advance in DMAIC order, which is why a
chapter mapping looks plausible at a glance — the book is ordered by
phase, but its content is not partitioned by it.

**Excel toolkit sheets are exempt:** `EXCEL_SHEET_TOOL_MAP` assigns each
sheet a phase explicitly. That mapping is exact and is preferred wherever
a source has real structure to exploit.

**Re-ingestion reclassifies.** This classifier reproduces ~58% of the
existing `phase_relevance` values exactly; the pipeline that first
populated the index is not in the repository and cannot be recovered. A
re-ingest is therefore a **content change, not an idempotent refresh** —
ingest into a fresh index and compare before replacing a working one.

### 7.2 `improve_evidence_index` — uploaded evidence

Case-specific documents uploaded by the Belt. **Per §1.2 this is the
only channel through which external, real-world data enters
AgentLean** — which makes it architecturally more important than
"uploaded files" suggests.

| Field | Type | Role |
|---|---|---|
| `id` | String | Key |
| `content` | String | Chunk text |
| `content_vector` | SingleCollection (3072d) | **Vector field** |
| `metadata` | String | JSON blob |
| `case_id` | String | **Filter** — scopes to the current case |
| `phase` | String | **Optional filter, OFF by default** — *added, pending reindex* |
| `uploaded_at` | String | **Order by** — `uploaded_at desc`, ISO 8601 — *added, pending reindex* |

**Retrieved by:** `rag_lookup_evidence(query, case_id, top_k, phase=None)`

**Filter:** `case_id eq '{case_id}'`, plus `and phase eq '{phase}'` only
when `phase` is passed explicitly.
**Ordering:** `uploaded_at desc`.

> **Schema change ratified 2026-08-20 — NOT yet applied in Azure.**
> **Until the reindex runs, the live index is the five fields above and
> code must not reference `phase` or `uploaded_at`.**
>
> **`uploaded_at` closes a gap this section previously documented as a
> dead end.** The upload timestamp already exists, but inside the
> non-sortable `metadata` JSON blob as `"timestamp"`:
>
> ```json
> {"case_id": "IMPR-2026-E9D", "upload_phase": "define",
>  "content_type": "image", "filename": "test_sipoc.png",
>  "blob_path": "uploads/IMPR-2026-E9D/test_sipoc.png",
>  "uploaded_by": "Vassilis", "timestamp": "2026-05-27T09:19:24+00:00"}
> ```
>
> `$orderby` cannot reach inside an `Edm.String` blob, so recency ranking
> was unavailable and `rag_lookup_evidence` dropped its `order_by`
> argument. Promoting the value to a top-level field restores it.
> **Both new fields backfill from `metadata` at reindex time** —
> `uploaded_at` from `metadata.timestamp`, `phase` from
> `metadata.upload_phase`. No new data has to be collected; the values
> are already there, in the wrong shape.
>
> **`phase` closes a problem that was never articulated.** Two similar
> documents uploaded at different phases were indistinguishable at
> retrieval time — a Belt's Measure-phase defect data and their
> Control-phase defect data both match "defect data" with nothing to tell
> them apart. Since this index is the only channel for external data
> (§1.2), that ambiguity lands directly on the coaching answer.
>
> **The `phase` filter defaults OFF, deliberately.** Cross-phase evidence
> retrieval is the normal case — a Control Belt comparing against the
> Measure baseline — so filtering to the current phase by default would
> break the comparison the field exists to enable.
>
> Never sort client-side on the parsed blob as a substitute: that
> reorders only the `top_k` already returned, which is a different result.
>
> **Type note.** `uploaded_at` is ratified as `Edm.String` holding ISO
> 8601, which sorts lexicographically in correct chronological order. An
> earlier revision of this section proposed `Edm.DateTimeOffset` with
> `sortable=True`, which is the more idiomatic Azure type and gives real
> date arithmetic. Both work for ordering. **Flagged for confirmation
> before the reindex is written** — the ratified spec says `Edm.String`,
> and changing it afterwards is another reindex.
>
> **Batch with §7.3's `content_vector` rename** so the corpus is rebuilt
> once. Schema-change procedure: §7.7.

### 7.3 `improve_case_index` — case records (episodic memory)

Live case data with per-phase summaries and a vector embedding. This
index **is** the long-term cross-case memory mechanism, and it moves
from "out of scope" in v2.1.1 to **active** in v2.2.

| Field | Type | Role |
|---|---|---|
| `id` | String | Key |
| `case_id` | String | Case identifier |
| `title` | String | Case title |
| `belt_level` | String | **Optional filter, OFF by default** |
| `leader` | String | Project leader |
| `department` | String | Owning department |
| `current_phase` | String | Phase in flight |
| `rag_status` | String | Red / Amber / Green |
| `status` | String | **Filter** — `status eq 'completed'` |
| `created_at` | String | **Order by** — `created_at desc` |
| `target_date` | String | Planned completion |
| `days_in_phase` | Int32 | Duration metric |
| `phase_summary_define` | String | Pre-computed phase summary |
| `phase_summary_measure` | String | Pre-computed phase summary |
| `phase_summary_analyse` | String | Pre-computed phase summary — *renamed, landed Aug 2026* |
| `phase_summary_improve` | String | Pre-computed phase summary |
| `phase_summary_control` | String | Pre-computed phase summary |
| `content_text` | String | Concatenated case text |
| `embedding` | SingleCollection (3072d) | **Vector field** — renaming to `content_vector`, see below |

> **`embedding` → `content_vector` ratified 2026-08-20 — NOT yet applied
> in Azure.** This is the only one of the three indexes whose vector field
> is not called `content_vector`, and the difference has no justification
> beyond history. Each tool knowing its own index's field name locally
> makes the asymmetry *safe*; it does not make it *good*. Standardising
> removes a permanent trap for whoever writes a fourth retrieval tool.
>
> **Until the reindex runs, `embedding` is the live field name and
> `rag_lookup_case_history` must use it.** The change is a delete +
> recreate — the index holds 0 documents, so there is no data migration
> and nothing to lose. `knowledge/tools.py` and this table change in the
> same commit as the Azure change, not before it. **Batch with §7.2's
> `phase` / `uploaded_at` additions** so the corpus is rebuilt once.

**Retrieved by:**
`rag_lookup_case_history(query, top_k, exclude_current_case=True)`

**Filter:** `status eq 'completed'` — completed cases are more
authoritative than in-progress ones.
**Ordering:** `created_at desc` — freshness matters for yokoten.
**`belt_level` filtering is OFF by default** — over-narrowing risk,
since a Green Belt often benefits from Black Belt cases. Available as
an optional parameter.

**The five `phase_summary_*` fields are pre-computed per-phase
summaries.** The tool can retrieve compact per-phase context rather
than only raw chunks, and its docstring says so.

> ### ✅ Breaking schema change — LANDED Aug 2026
>
> **`phase_summary_analyse_phase` → `phase_summary_analyse`**
>
> Required for consistency with `_define`, `_measure`, `_improve`,
> `_control`. The naive pattern `phase_summary_{phase.lower()}` is now
> correct for all five phases.
>
> **How it was applied.** Azure AI Search does not support field
> renaming, so the index was deleted and recreated from
> `scripts/create_indexes.py`. **The live index held 0 documents at the
> time**, so no data was lost and there was nothing to reindex — the
> reindex step in §7.7 was a no-op for this change. Verified after
> recreation: 19 fields before and after, symmetric difference exactly
> `{phase_summary_analyse_phase, phase_summary_analyse}`, semantic
> configuration `improve-case-semantic` intact.
>
> A `PHASE_SUMMARY_FIELD_MAP` mapping constant was considered and
> **rejected**: fixing the name at the source means no permanent
> workaround exists in the codebase and no future reader is surprised
> by the inconsistency.
>
> **Writer side aligned — the internal phase key was renamed too.**
> The index field alone was not enough: the *internal phase key* was
> also `analyse_phase`, so `f"phase_summary_{phase}"` built from it
> would have targeted a field that no longer exists. The key is now
> `analyse` across the codebase — directory `phases/analyse/`, every
> `phase_order` list, `PhaseSummaryRecord.analyse`, the graph node
> names, and `EXTRACTION_MAP` / `ORCHESTRATOR_CONTEXT_MAP`. See §7.3.1.
>
> **Deferred:** a schema audit across all three indexes for other
> naming inconsistencies.

#### 7.3.1 The internal phase key — `analyse`, not `analyse_phase`

**The phase key is `analyse`.** It matches the index field suffix
(`phase_summary_analyse`), the `phase_relevance` values already present
in `improve_knowledge_index` (348 documents on `analyse`), and the bare
naming every other phase already used (`define`, `measure`, `improve`,
`control`).

`analyse_phase` was the anomaly in **four** places at once, all now
renamed together:

| Was | Now |
|---|---|
| `backend/phases/analyse_phase/` | `backend/phases/analyse/` |
| `orchestrate_analyse_phase`, `validate_analyse_phase` | `orchestrate_analyse`, `validate_analyse` |
| graph nodes `"orchestrate_analyse_phase"`, `"validate_analyse_phase"` | `"orchestrate_analyse"`, `"validate_analyse"` |
| key `"analyse_phase"` in `PHASE_ORDER`, `phase_inputs`, `EXTRACTION_MAP`, `ORCHESTRATOR_CONTEXT_MAP`, `GATE_CHECKS`, `PhaseSummaryRecord`, `CaseDocument.phases` | `"analyse"` |

**`AnalysePhaseInput` keeps its name** — `{Phase}PhaseInput` is the
convention every phase follows (`DefinePhaseInput`, `MeasurePhaseInput`,
…), so it was never part of the inconsistency.

**Renaming the graph node names was safe only because no checkpoints
existed.** LangGraph checkpoints record node names; had any been
present, the rename would have orphaned them. Verified before applying:
the blob container held no `checkpoints/` prefix. **Any future rename of
a graph node name must re-check this** — the checkpointer is being wired
in during this same refactor (§6.2), so the window in which this is free
is closing.

**Vector dimension — confirmed against the live index (Aug 2026):**
`embedding` is 3072-dimensional, consistent with
`text-embedding-3-large` and with `content_vector` on the other two
indexes. HNSW profile `improve-vector-profile`, cosine metric,
`m=4`, `efConstruction=400`, `efSearch=500`. Note the profile name
differs from the other two indexes, which use `default` — safe by
construction (§7.4), and worth normalising during the `content_vector`
reindex since the index is being recreated anyway.

### 7.4 The retrieval pipeline

All three tools share one shape. The differences are index, filter,
ordering, and vector field name.

```
Belt message
    ↓
phase_planner decides retrieval_strategy (§3.5)
    ↓
rag_lookup_* invoked by the executor
    ↓
  ┌─── INSIDE THE TOOL ─────────────────────────────────┐
  │  1. Variant generation — 3–5 alternative phrasings, │
  │     phase-shaped prompt, structured output          │
  │  2. Per-variant retrieval with the index's          │
  │     metadata filters applied                        │
  │  3. Reciprocal Rank Fusion, k=60                    │
  │  4. top_k returned, with source metadata            │
  └─────────────────────────────────────────────────────┘
    ↓
Executor may call again (multi-hop, ≤5 — §3.3)
```

**Multi-query + RRF is mandatory, not an enhancement.** Agent Resolve
production experience showed Azure AI Search ranking unreliable for
this corpus: with a single query it was not reliably returning the
right matches. RRF operationalises cross-variant consistency — when
several variants return the same document at moderate ranks, that
document is more likely genuinely relevant than one appearing once at
the top of a single variant. Native single-query ranking cannot make
that judgment, because it does not know the variants exist.

```python
def reciprocal_rank_fusion(ranked_lists, k: int = 60):
    """score(doc) = Σ 1/(k + rank) across variant result sets."""
```

Roughly fifteen lines, no LangChain class, no third-party dependency,
stable across framework versions. `MultiQueryRetriever` and
`EnsembleRetriever` both moved to `langchain-classic` in the 1.0
namespace split and are prohibited.

**The vector field asymmetry is safe by construction — and is still
being removed.** Each tool is bound to exactly one index and knows that
index's vector field name locally. There is no shared retriever, so no
shared code can hide the `content_vector` / `embedding` difference and
fail silently on it.

**"Safe" was the reason not to treat it as urgent; it was never a reason
to keep it.** `improve_case_index.embedding` is ratified for rename to
`content_vector` (§7.3), pending the reindex. Until that lands the
asymmetry is live and the local-knowledge property above is what makes it
harmless. Do not cite this paragraph as an argument against the rename.

### 7.5 Multi-hop policy per phase

The **planner** decides at plan time; the executor does not decide at
retrieval time.

| Phase | Default | Multi-hop when |
|---|---|---|
| Define | Single-hop | Never — scoping questions are direct |
| Measure | Single-hop | Complex measurement system validation (GR&R) |
| **Analyse** | **Multi-hop, planned — 3 typed hops** | Almost always — root cause validation is layered |
| Improve | Single-hop | Belt is comparing competing approaches |
| Control | Single-hop | Never — documentation questions are direct |
| **Gate validation** | **No retrieval** | **Never** |

**Analyse uses *planned* multi-hop:** the planner pre-decomposes the
question into a typed hop plan before any retrieval fires. More
predictable and fully inspectable in LangSmith — you can see each hop's
question and result. Correct for Analyse because root cause validation
is inherently layered and inspectability matters in a quality system.

**Other phases use *emergent* multi-hop:** the coach calls the tool
again when its own reasoning requires it. A structured planner is not
justified for rare occurrences.

**Gate validation never retrieves.** The rubric already encodes the
methodology standards; retrieval there is redundant *and* adds latency
at exactly the moment the Belt is waiting.

Multi-query and multi-hop compose: multi-query broadens within a hop,
multi-hop deepens across hops.

### 7.6 Cross-agent indexes — read-only

| Index | Tool | Notes |
|---|---|---|
| `case_index_v3` | `search_resolve_cases` | Agent Resolve |
| `knowledge_index_v2` | `search_resolve_knowledge` | Agent Resolve |
| `evidence_index_v1` | `search_resolve_evidence` | Agent Resolve |

These are `@tool` functions reading Agent Resolve's Azure AI Search
indexes directly via a shared Python module. **Not MCP servers**
(§1.2). Read-only — Agent Improve never writes to an Agent Resolve
index.

### 7.7 Schema change procedure

1. Update this section **first**, in the same commit
2. Apply the change in Azure AI Search
3. Reindex or migrate existing documents
4. Sweep the codebase for field-name references
5. Update the affected tool docstrings (§8.1)

Schema facts that are not written down here get rediscovered during
implementation — which is how the `phase_summary_analyse_phase`
inconsistency survived as long as it did.

---

## 8. Tool Architecture

### 8.1 The universal seven

Passed to every phase executor via `tools=`. Defined in
`knowledge/tools.py`, argument schemas in `knowledge/tool_args.py`.

| Tool | Purpose |
|---|---|
| `rag_lookup_methodology(query, phase, top_k)` | `improve_knowledge_index` — methodology grounding |
| `rag_lookup_evidence(query, case_id, top_k, phase=None)` | `improve_evidence_index` — this project's uploaded data; optional phase filter, off by default (§7.2) |
| `rag_lookup_case_history(query, top_k, exclude_current_case)` | `improve_case_index` — yokoten, cross-case precedent |
| `propose_template(template_type, fill_data)` | Fill-in template for the team |
| `propose_diagram(diagram_type, data)` | Structured diagram JSON (not SVG) |
| `check_gate_status()` | Gate readiness — which Tier 1 fields are populated |
| `request_human_approval(reason)` | Out-of-band interrupt |

**`record_field` is retired — the eighth tool is gone, not replaced.**
Field capture moved to `response_format=CoachingResponse` on the
executor (§4.10): the coach emits `fields_captured` as structured output
on every turn, and the executor node writes each entry into `artifacts`.

**Why this is better than a tool.** A tool call is a decision the model
may or may not make, so a turn where the Belt states a baseline and the
coach forgets to call `record_field` loses the value silently. Structured
output makes capture part of the response shape — the model cannot
return a well-formed `CoachingResponse` without addressing
`fields_captured`. It also removes a whole class of tool-argument
validation from the hot path.

`search_methodology` and `search_evidence` are renamed and superseded.
`rag_lookup_case_history` is new — added on methodology grounds:
**yokoten (horizontal deployment) is explicit Lean/DMAIC discipline**,
and an agent that coaches DMAIC while withholding cross-case learning
undermines its own methodology.

**Docstrings are interface, not commentary.** They are how the model
chooses between the three retrieval tools. Each must state when to use
it, which index it queries, which vector field it uses, and which
filters apply. `rag_lookup_case_history` additionally carries the
multi-tenancy note for future engineers.

### 8.2 Per-phase computation tools

20 tools, `knowledge/computation.py`. Each is a `@tool(args_schema=...)`
**pure function** — no LLM call, deterministic, unit-tested.

| Phase | Universal | Computation tools | Total |
|---|---|---|---|
| Define | 7 | `calculate_expected_savings` | **8** |
| Measure | 7 | `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean` | **15** |
| Analyse | 7 | `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression` | **12** |
| Improve | 7 | `calculate_doe_main_effects` | **8** |
| Control | 7 | `xbar_r_chart_limits`, `imr_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk` | **12** |

**Why per-phase binding.** Tool selection quality degrades past roughly
10–15 tools per agent. Binding all 27 everywhere would make every coach
carry 27 options per turn, most irrelevant to its phase. Under
per-phase binding the maximum is 15 and most sit at 8–12 — every phase
inside the tractable range, with Measure at its top edge.

**Retiring `record_field` moved every phase down one** and took Measure
from 16 to 15, off the boundary of the degradation range. That was a
side effect of the structured-output decision (§4.10), not its purpose,
but it is a real one.

> **Count correction, v2.2.13.** Every document said "18 computation
> tools" from v2.2 onward, while the table above has always enumerated
> **19**. Adding `imr_chart_limits` makes **20**, and the total tool
> count is 7 universal + 20 = **27**. The enumerated table was always
> right; the prose figure was an uncorrected off-by-one carried across
> nine amendments. Counts are now derived from the table rather than
> restated.

**Why separate named tools rather than parameterised groups.**
Parameterisation moves the selection burden from the tool namespace
into the argument space, and models handle distinct named tools more
reliably than mode arguments. Each canonical DMAIC calculation gets its
own name.

**Architectural consequence:** the phase subgraph builder takes the
phase as a parameter, because it must select the correct computation
subset:

```python
def build_phase_subgraph(phase: str, llm):
    tools = UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    ...
    return builder.compile()          # no checkpointer, no store
```

### 8.3 Where multi-query and RRF live

**Inside the tool.** Not a subgraph node, not a wrapper class around
the retriever. From the executor's perspective `rag_lookup_*` returns
documents; the variant generation and fusion are encapsulated.

The same holds for the gate validator, the coherence check, and the
constraint check — these are bound tools or middleware, not pipeline
stages and not nodes.

### 8.4 Phase skills

Five SKILL.md files under `skills/`, following the agentskills.io
standard, loaded by `DMAICSkillsMiddleware` (§3.4).

Each skill carries: phase coaching instructions, the phase rubric,
the phase-specific computation tool list, and coaching strategy
guidance.

**`allowed-tools` in each skill must match §8.2 for that phase.** The
skill and the tool binding must not drift apart.

**Two distinct kinds of skill exist in this repository:**

| Location | Consumed by | Example |
|---|---|---|
| `.claude/skills/` | Claude Code, during development | `/verify-current-version` |
| `agent-improve/skills/` | The coach, at runtime | `dmaic-analyse-phase` |

---

## 9. Reliability Architecture

### 9.1 The six-step failure pipeline, plus Step 0

```
Step 0. Per-node timeout        TimeoutPolicy(run_timeout=45)
Step 1. Error classification    transient vs permanent (§9.5)
Step 2. Context recovery        save partial results, resume
Step 3. Circuit breaker         3 failures / 30s → OPEN, 60s reset
Step 4. Safe reopen             one probe in HALF-OPEN
Step 5. Graceful degradation    four-level fallback chain (§9.3)
Step 6. Smart fallbacks         alternative model, cache, degraded mode
```

**Step 0 is the addition.** LangGraph 1.2's per-node `TimeoutPolicy`
bounds wall-clock at 45 seconds, and `NodeTimeoutError` triggers the
fallback chain — the timeout fires *before* the Belt notices the delay,
rather than after retries have already burned the budget.

**Backoff discipline:** exponential for managed services (Azure OpenAI
rate-limits predictably); jittered for shared resources (the cache,
which several subagents may hit simultaneously — lock-step retries
create their own thundering herd).

### 9.2 Compensation via native `error_handler=` — not a Saga framework

**No custom Saga orchestrator is built.** LangGraph 1.2 provides the
mechanism; hand-rolling a coordinator on top of it is redundant
machinery.

```python
def define_error_recovery(error: NodeError, state: PhaseState) -> Command:
    """Undoes external writes for define_executor."""
    delete_or_flag_stale_in_case_index(state["case_id"], "define")
    return Command(
        update={"extraction_error": str(error), "extraction_incomplete": True},
        goto="degraded_coaching_response",
    )


builder.add_node(
    "define_executor",
    define_executor_fn,
    timeout=TimeoutPolicy(run_timeout=45),
    error_handler=define_error_recovery,
)
```

**Every node that writes to an external system gets one.** The external
systems are Azure Blob, `improve_case_index`, and
`improve_evidence_index` — and that set is closed by design (§1.2).

| Phase | External write | Handler required |
|---|---|---|
| Define | artifacts → store + case index | ✅ |
| Measure | baseline + case index update | ✅ |
| Analyse | root cause + case index | ✅ |
| Improve | hypothesis + pilot results | ✅ |
| Control | control plan, final record | ✅ |

**Two dependencies, both correctness-critical:**

1. **Gate reopening (§3.8).** When the re-approval cascade fires, the
   affected phase's handler must run, or graph state and the index
   disagree silently.
2. **Time-travel debugging.** Resuming from an earlier checkpoint rolls
   back *state*, not *external writes*. Time travel is only correct for
   nodes that have a handler — these are not independent features.

**Graceful shutdown:** `RunControl.request_drain()` for deployment
rollouts. Mid-coaching sessions save their checkpoint and resume.

**`DeltaChannel` is not used** — beta API, and not needed until
sessions exceed roughly 200 turns.

### 9.3 The four-level fallback chain

```
Level 0: TimeoutPolicy(run_timeout=45)              fires first
    ↓ NodeTimeoutError
Level 1: Azure OpenAI gpt-4o  (operational-premium)
         exponential backoff — managed service
    ↓ rate-limited or unavailable
Level 2: Azure OpenAI gpt-4o-mini (operational-model)
         exponential backoff — same managed tier
    ↓ also unavailable
Level 3: Azure Cache for Redis, session-scoped       ← §6.6
         jittered backoff — shared resource
    ↓ cache miss or unavailable
Level 4: Degraded mode — always succeeds, never crashes
```

**Degraded mode uses actual state, never a generic error:**

```python
def degraded_mode_response(state: PhaseState) -> str:
    return (
        f"I'm experiencing a temporary connection issue. "
        f"Based on what we've captured so far in the {phase} phase "
        f"({n_captured} of {n_total} fields complete), "
        f"I'd suggest we pause here and continue once the system recovers. "
        f"Your progress is saved and nothing has been lost."
    )
```

Degraded mode is still a coaching interaction, not an error page. The
Belt knows what happened, that their work is safe, and how to continue.

**HTTP 400 (token limit exceeded) is not a fallback case.** It is a
context-management failure — retrying against a smaller model does not
fix it. Fix the context (§3.4).

### 9.4 Two circuit breakers, three states

| Breaker | Wraps | When OPEN |
|---|---|---|
| **LLM** | Azure OpenAI | Coaching turn cannot happen — fall to Level 2, then degraded |
| **Search** | Azure AI Search | Coaching **continues** without RAG grounding — **quality** degradation, not **availability** failure |

Threshold 3 failures in 30s trips open; 60s reset; one probe request in
HALF-OPEN before resuming full traffic.

**Two-state (CLOSED/OPEN) breakers are prohibited.** This is a
long-running FastAPI service and must recover without a restart — a
two-state breaker turns a 30-second Azure blip into an outage lasting
until someone redeploys.

When the search breaker is open, the coach's system prompt must
acknowledge the reduced grounding rather than presenting ungrounded
methodology as if it had been retrieved.

### 9.5 Structured error schema

`core/errors.py`

```python
class AgentImproveError(BaseModel):
    error_code: str              # "TIMEOUT", "RATE_LIMIT", "AUTH_FAILURE", …
    severity: str                # "transient" | "permanent"
    retry_recommendation: str    # "retry_after_backoff" | "do_not_retry" | …
    affected_identifier: str     # which service failed
    message: str
    timestamp: datetime
```

Used by the circuit breaker, the fallback chain, and the `step_log`
audit trail. `severity` is what lets the breaker distinguish "retry
this" from "stop trying"; `retry_recommendation` is what the fallback
chain reads to choose its backoff strategy.

Applies to **all** external service calls — Azure OpenAI, Azure AI
Search, Azure Blob, Redis.

---

## 10. API Surface

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Liveness |
| `/cases` | POST | Create case |
| `/cases/{id}` | GET | Full case document |
| `/registry` | GET | Case list |
| `/ask` | POST | Non-streaming turn (legacy clients) |
| `/ask/stream` | POST | SSE streaming turn (primary) |
| `/gate/submit` | POST | Run validation stack, fire `gate_review_node` interrupt |
| `/gate/approve` | POST | Resume from interrupt with approval + edits |
| `/gate/reject` | POST | Resume from interrupt with rejection |
| `/conflict/resolve` | POST | **NEW** — resolve a mid-phase value contradiction (§3.8) |
| `/upload` | POST | File upload to evidence |
| `/files/{case_id}/{file_id}` | DELETE | Remove uploaded file |
| `/context` | POST | Re-entry greeting |
| `/summarise` | POST | Session summary |

All endpoints are `async def` and return Pydantic models from
`gateway/schemas.py`.

**Versioning** (`/v1`, `/v2` parallel) becomes relevant **after** first
production launch. No production system exists yet, so there is nothing
live to avoid breaking.

---

## 11. UI Architecture

The structure (4 screens, 5 tabs per phase) is preserved. Integration
changes:

### 11.1 Streaming chat
The AI Guide tab connects to `/ask/stream` via EventSource and renders
tokens as they arrive.

### 11.2 Contextual progress messages
Spinner text is contextual, never generic: "Retrieving methodology…",
"Validating your root cause against Six Sigma standards…", "Checking
gate completeness…". A multi-hop turn takes longer than a simple
coaching response, and the message should say which operation is
running.

### 11.3 Connection status before first interaction
A status panel on session load shows Azure OpenAI, knowledge base, and
case index reachability, plus session id and phase. Without it, the
first coaching turn fails with a confusing error and the Belt does not
know why.

### 11.4 Gate review — extracted field transparency
Before approval, the Belt sees every extracted field in a readable,
editable panel with an explicit approve action. This is steps 4–7 of
§3.6 made concrete. Edits flow to `/gate/approve` and are validated by
the policy advisory before commit.

**This is the same component as §11.6, not a separate one** — see
§11.7.

### 11.5 Conflict resolution panel
**New.** When §3.8 fires, the Belt sees the field name, the previously
approved value with its approval timestamp and gate, the proposed new
value, and the two options. Choosing "update" surfaces which downstream
phases become provisional **before** the Belt confirms.

### 11.6 Completeness and trace surfacing
Progress is surfaced visually and continuously — **two counts, Tier 1
and Tier 2 separately**, derived from `PhaseState.artifacts` against the
phase's field list. There is no stored `completeness_score`; a stored
score is a second source of truth that can disagree with the gate
(§4.1). The LangSmith run id is available for support escalation.

### 11.7 The live gate document

**§11.4 and §11.6 are one component.** Showing the Belt their captured
fields and showing them their progress are the same view at different
zoom levels, and splitting them across two moments gave the wrong
behaviour: fields visible only at the gate, progress visible only as a
number.

The implementation is a **single live document tab** beside the chat,
always visible, updating the moment a field is captured via
`CoachingResponse.fields_captured` (§4.10.1). It reads as a document —
headers, tables, formatted content — because it is what the Belt shows a
sponsor and downloads as PDF or Word. Mid-phase downloads carry
`[not yet captured]` placeholders; post-gate downloads are the approved
document.

**The rendering format is defined per phase in the skills**, in each
SKILL.md's **Document Layout** section: which fields get headers, which
render as tables, where `computation_results` and `citations` appear.

| Phase | Skill section | Layout specifics |
|---|---|---|
| Define | `skills/dmaic-define-phase/SKILL.md` §8 | SIPOC as a row-per-step table |
| Measure | `skills/dmaic-measure-phase/SKILL.md` §8 | Process map with touch vs elapsed time; X-Y matrix as a table |
| Analyse | `skills/dmaic-analyse-phase/SKILL.md` §9 | `causal_hypothesis` as a callout; `ruled_out_causes` as a table |
| Improve | `skills/dmaic-improve-phase/SKILL.md` §8 | Before / after / change line; phased implementation table |
| Control | `skills/dmaic-control-phase/SKILL.md` §8 | Before/after block leads; five sub-plans with written / implemented status |

**No new backend work.** The data is `PhaseState.artifacts`, already
checkpointed and updated on every capture (§4.2). Full requirement:
REFACTORING_AGENT_IMPROVE.md §77, Patterns 3 + 4 merged.

UI modularisation of `index.html` remains a separate roadmap item.

---

## 12. Tracing and Observability

### 12.1 LangSmith integration
`core/tracing.py` initialises tracing at app startup. Production
without LangSmith credentials fails startup with a clear error.

### 12.2 What is traced
- Every `graph.ainvoke` call → top-level trace
- Every node → child span with input/output state slices
- Every LLM call → token cost, latency, model name
- Every tool call → args, result, duration
- Every retrieval → query, top-k, scores
- **Every validation layer** → via `@traceable`

### 12.3 `@traceable` on custom functions
LangSmith traces LangChain runnables and LangGraph nodes
automatically. It does **not** trace plain Python functions. Without
`@traceable`, the logic *between* nodes is invisible and a gate failure
surfaces as a 500 with no indication of which layer failed.

Required on: field extraction, **all four validation layers**,
completeness scoring, routing decisions outside LangGraph routing, and
direct Azure service calls made outside a LangChain runnable.

### 12.4 Diagnostic patterns
P50/P99 latency is a **coaching quality signal**, not only an ops
metric. The usual P99 outlier is multi-hop retrieval combined with a
grader call on the same turn. Fixes in order of preference: cache
(§9.3 Level 3), faster grader model, reorder the validation stack
cheapest-first (already mandated).

### 12.5 Fail-fast environment validation
`AZURE_OPENAI_KEY`, `AZURE_SEARCH_API_KEY` (**not**
`AZURE_SEARCH_KEY`), `LANGCHAIN_API_KEY` validated at startup; missing
credentials exit 1 with a clear message. Integrates with container
health checks — a container failing startup receives no traffic.

### 12.6 Logs
Structured logs via `logging.Logger`. Every request gets a
`request_id` (UUID4) propagated to child operations. Logs include
`request_id`, `case_id`, `phase`, `node_name`, `duration_ms`.

---

## 13. Phase Gate Requirements

**Every field below is `str`** unless marked **`dict`** — see §4.6 and
the three cross-phase exceptions in §4.7. Tier 1 blocks the gate at
Layer 2b; Tier 2 produces a grader warning the Belt may acknowledge
(§3.7.1).

**Fields and rubric criteria are not the same list.** Every row without
a backticked name is a **rubric criterion with no dedicated schema
field** — the grader evaluates it against the captured fields,
`artifacts["computation_results"]`, or the conversation. Only backticked
rows appear in the `{Phase}Output` schemas of §4.10.

### 13.1 Define — `DefineOutput`

| Field | Tier | Notes |
|---|---|---|
| `problem_statement` | **1** | Single consolidated statement. The 5W2H sub-fields feed it; the rubric checks the consolidated form |
| `voc_summary` | **1** | Customer perspective. Every DMAIC project needs one regardless of belt level |
| `project_scope` | **1** | Inclusions, exclusions, process boundaries |
| `goal_statement` | **1** | SMART |
| `business_case` | 2 | Rubric requires COPQ-style quantification |
| `team` | 2 | Belt, sponsor, 2+ named members |
| `baseline_metric` | 2 | Current measured state as the Belt states it. Measure refines this into `baseline_mean` |
| `target_metric` | 2 | The value the project is aiming at |
| `secondary_metrics` | 2 | What could get worse if this succeeds (§4.10.5) |
| `process_map_sipoc` | **1** | **`dict`** — suppliers, inputs, process_steps, outputs, customers, process_kpis (§4.10.7) |
| `issues_and_barriers` | **1** | Belt-stated project blockers (§4.10.5) |

*Statistical problem statement moved to Analyse, all Belts — §4.10.5.*

### 13.2 Measure — `MeasureOutput`

| Field | Tier | Notes |
|---|---|---|
| `baseline_mean` | **1** | The value every later phase references |
| `data_collection_plan` | **1** | Sample size, frequency, responsible person |
| `xy_matrix_summary` | **1** | Evidence prioritisation happened (§4.10.5) |
| `vital_few_xs` | **1** | The ranked result Analyse consumes (§4.10.5) |
| `detailed_process_map` | **1** | **`dict`** — steps, cycle_times, resources, value_vs_waste, measurement_points, baseline_kpis (§4.10.7) |
| `stability_assessment` | **1** | Checked **before** capability — an unstable baseline is not a baseline (§4.10.7) |
| `issues_and_barriers` | **1** | Belt-stated project blockers |
| `baseline_sigma` | 2 | Calculated sigma level from baseline data |
| `measurement_system_validated` | 2 | GR&R or equivalent |
| `secondary_metrics` | 2 | What could get worse if this succeeds |

*Stability was a Tier 2 rubric criterion with no field until v2.2.12;
it is now `stability_assessment`, Tier 1 — the eBook sequences it as a
precondition for capability, not a recommendation (§4.10.7).*

*FMEA is deliberately not tracked in any schema — §4.10.5.*

### 13.3 Analyse — `AnalyseOutput`

| Field | Tier | Notes |
|---|---|---|
| `root_cause_statement` | **1** | |
| `root_cause_validation` | **1** | Statistical or observational evidence, not opinion |
| `practical_significance` | **1** | How much of the problem this root cause explains (§4.10.5) |
| `issues_and_barriers` | **1** | Belt-stated project blockers |
| `causal_hypothesis` | 2 | **`dict`** — cross-phase reference to Measure's baseline (§4.7) |
| `ruled_out_causes` | 2 | Alternatives considered and rejected, with rationale |
| `statistical_problem_statement` | 2 | Moved here from Define, all Belts (§4.10.5) |
| `process_owner_buyin` | 2 | Owner accepts the root causes (§4.10.5) |
| `secondary_metrics` | 2 | What could get worse if this succeeds |

*The eBook gates root causes on statistical **and** practical
significance in series (book p417) — `root_cause_validation` covers the
first, `practical_significance` the second.*

### 13.4 Improve — `ImproveOutput`

| Field | Tier | Notes |
|---|---|---|
| `selected_solution` | **1** | Criteria-based selection: impact, effort, risk |
| `pilot_result` | **1** | Rubric requires practical **and** statistical significance |
| `experiment_justification` | **1** | DOE, simplified experiment, or none — with the reasoning (§4.10.7) |
| `issues_and_barriers` | **1** | Belt-stated project blockers |
| `solution_linked_to_root_cause` | 2 | **`dict`** — cross-phase reference to Analyse's root cause (§4.7) |
| `implementation_plan` | 2 | Timeline, owner, resources |
| `explanatory_power` | 2 | How much of the problem the selected X's explain (§4.10.5) |
| `process_owner_buyin` | 2 | Owner accepts the solution (§4.10.5) |
| `secondary_metrics` | 2 | What could get worse if this succeeds |
| DOE | 2 | **BB only** — no field; graded from `computation_results` |

### 13.5 Control — `ControlOutput`

| Field | Tier | Notes |
|---|---|---|
| `control_plan` | **1** | **`dict`** — five sub-plans: documentation, monitoring, response, training, aligning_systems (§4.10.6) |
| `issues_and_barriers` | **1** | Belt-stated project blockers |
| `post_improvement_metric` | **1** | **`dict`** — cross-phase reference to Measure's baseline (§4.7) |
| `improvement_delta` | 2 | "reduced from 12.3% to 3.1%" |
| `financial_impact_verified` | 2 | "saves 35 hours/month rework, ~€4,200/month" |
| `sustainability_check` | 2 | Process for maintaining the gains |
| `handover_documented` | 2 | Named process owner accepting responsibility |
| `lessons_learned` | 2 | Feeds cross-project learning via the case index |
| `transferability` | 2 | Yokoten — feeds `rag_lookup_case_history` |
| `project_signoff` | 2 | Champion + Belt + Finance agree the project is complete (§4.10.5) |
| `secondary_metrics` | 2 | Re-checked at close — "repeat same process for secondary metrics" |

**Why Control gained three fields.** A DMAIC project that cannot show
the baseline moved has not demonstrated anything, and the BB eBook
(book pp677–679) requires verified financial impact. `post_improvement_metric` is
Tier 1 and carries the reference to Measure's baseline, so the grader
can verify the shift deterministically rather than accepting a claim.
`improvement_delta` and `financial_impact_verified` are Tier 2 — the
change is meaningful without them, but a Belt who cannot state the
saving has not finished the project.

### 13.6 Three distinct things check these fields

Conflating them is a design error:

| Mechanism | Checks | Where |
|---|---|---|
| `PhaseInput` schema | Types and shape | `phases/{phase}/schema.py` |
| `DMAICGateValidator` | Presence of **Tier 1** fields | Layer 2b |
| Phase rubric | Meaningful quality per criterion, **both tiers** | Layer 2d |

A `root_cause_statement` reading "there are problems" satisfies the
schema and the presence check and fails the rubric. That gap is the
reason Layer 2d exists.

**The tiers are what keep 2b and 2d from contradicting each other.**
2b blocks only on Tier 1; 2d can fail only on Tier 1 and can warn on
either. There is no longer a criterion the grader can fail that the gate
never asked for (§3.7.1).

Rubric and constraint text are canonical in CLAUDE.md §8.2 / §9.2.

---

## 14. Evaluation and Regression Testing

**Built alongside the refactor, not before it.** Establishing a
baseline against the current system would produce a baseline of "bad."
The suite becomes load-bearing when the coach, retrieval tools, and
grader are wired — that is when output quality changes. Infrastructure
steps do not affect coaching quality.

**Authored jointly, not generated.** Coaching quality judgments are
domain judgments; a generated dataset measures agreement with a model
rather than correctness.

| Dimension | Target |
|---|---|
| Size | 20–30 examples, 4–6 per phase |
| Categories | Realistic turns · edge cases · tool-calling · failure/ambiguous · historical production data |
| Metrics | Accuracy · relevance · reasoning quality · tool usage · safety |
| Evaluator order | Deterministic ($0) → LLM-judge relevance (~$0.01) → LLM-judge reasoning (~$0.02) |
| Regression gate | **Block release if any metric drops >10% from baseline** |
| Frequency | Every commit touching prompts, graph structure, or model config |
| Cost | ~$0.60 per 20-example run |

Lives in `eval/`. Output format is ready for LangSmith's
`create_dataset` API.

**Rubrics and the eval dataset are complementary.** Rubrics define what
good looks like *for the grader*, in production, at every gate. The
eval dataset tests whether the whole system produces good outcomes, in
CI, at every commit.

---

## 15. Migration Sequence — v1 → v2.2

**Option B is the ratified sequence: refactor the foundation first,
then build Improve and Control on it.** Building two more phases on the
current foundation and rewriting them later was rejected — the cost is
building each twice.

Each step is one commit with prefix `refactor(arch-v2):`. Each step
must compile, tests pass, and IMPR-2026-E9D load, before the next
begins.

### Step 0 — Foundation ✅ COMPLETE
- **0.1** CLAUDE.md + ARCHITECTURE.md committed
- **0.5.0–0.5.5** Anti-drift scaffold: `/verify-current-version` skill,
  `PreToolUse` drift hook, `SessionStart` context hook. Smoke tested
  2026-07-03.

### Step 1 — Tracing first ✅ COMPLETE
- **1.1** `core/tracing.py`, LangSmith wired, fail-fast on missing creds
- **1.2** `request_id` middleware, structured logging

### Step 2 — Checkpointer ✅ COMPLETE
- **2.1** `AzureBlobCheckpointSaver` with unit tests
- **2.2** Wired into graph compilation

### Step 2.5 — Dependency upgrade ⬅ NEXT
- **2.5.1** Upgrade `langgraph` 1.1.10 → **1.2.10**. Required for the
  subgraph `checkpoint_ns` fix (§3.1) **and** the native reliability
  primitives (§9.2). Both need ≥1.2.6; 1.2.10 is the latest release.
- **2.5.2** Upgrade `langchain` → 1.3.11. Sweep for imports from
  `langgraph.prebuilt`; migrate to `langchain.agents`.
- **2.5.3** Repin adjacent packages after pip resolution.

### Step 3 — Tools and schemas
- **3.1** `knowledge/tool_args.py` — Pydantic arg schemas
- **3.2** `knowledge/fusion.py` — `reciprocal_rank_fusion`
- **3.3** `knowledge/tools.py` — the universal seven with multi-query + RRF
- **3.4** `knowledge/computation.py` — 20 computation tools, pure functions, unit tested
- **3.5** `core/diagrams.py` — diagram type schemas
- **3.6** ✔ **Index schema rename** — `phase_summary_analyse_phase` →
  `phase_summary_analyse` applied in Azure AI Search by delete +
  recreate (index was empty; no reindex needed); codebase sweep done —
  `scripts/create_indexes.py` was the only live reference (§7.3).
  Writer-side phase-key alignment still outstanding — see §7.3.

### Step 4 — State and store
- **4.1** `core/state.py` `SupervisorState`, `core/substate.py` `PhaseState`
- **4.2** `core/store.py` `AzureBlobStore` with unit tests
- **4.3** `phases/{phase}/mappers.py` — boundary mappers, all five phases

### Step 5 — Validation and middleware
- **5.1** `validation/` — gate validator, coherence, constraints, verdict schemas
- **5.2** `middleware/grader.py` — `DMAICGraderMiddleware`; five rubrics in prompts.py
- **5.3** `middleware/skills.py` — `DMAICSkillsMiddleware`; five SKILL.md files
- **5.4** `middleware/state_injection.py` — `BeforeModelStateInjection`, **`before_agent`** hook
- **5.5** Wire `SummarizationMiddleware`
- **5.6** Wire `ModelRetryMiddleware(retries=2)` and `ToolRetryMiddleware(max_retries=2, on_failure="continue")` — both LangChain core
- **5.7** `middleware/contradiction.py` — `ContradictionDetectionMiddleware` (§3.8, deterministic, no LLM)
- **5.8** `middleware/coherence.py` — `CoherenceMiddleware` (Layer 2a, every turn, own 2-retry cap)
- **5.9** Assemble the eight-middleware stack in declaration order (§3.4) — order is execution order

### Step 6 — Phase subgraph migration (Define first)
- **6.1** Migrate Define: `nodes.py` (planner, executor, validation_stack),
  `gate.py` (gate_review, gate_apply), `graph.py`.
  Delete `orchestrate.py`, `validate.py`, `analyse.py` stub.
- **6.2 → 6.5** Same for Measure, Analyse, Improve, Control — one
  commit per phase, each independently verifiable

### Step 7 — Supervisor and routing
- **7.1** `core/graph.py` — static edges, checkpointer + store on the
  parent only. Delete `phase_router`.
- **7.2** `escalate.py` — escalation subgraph

### Step 8 — Reliability
- **8.1** `core/errors.py`, `core/reliability.py` — circuit breakers, backoff
- **8.2** Provision **Azure Cache for Redis**; `core/cache.py`
- **8.3** Wire `TimeoutPolicy` and `error_handler=` on every node with
  external writes
- **8.4** Four-level fallback chain

### Step 9 — Routes
- **9.1** Rewrite `gateway/routes.py` — thin transport. Wire `thread_id`
  through `graph.ainvoke` and `recursion_limit=11`. *(This is the
  `routes.py:238` fix.)*
- **9.2** `/ask/stream` SSE endpoint
- **9.3** `/gate/submit`, `/gate/approve`, `/gate/reject`
- **9.4** `/conflict/resolve`

### Step 10 — UI integration
- **10.1** AI Guide tab — streaming, contextual progress messages
- **10.2** Gate tab — review/edit/approve against the new endpoints
- **10.3** Conflict resolution panel
- **10.4** Diagram rendering from `propose_diagram` JSON

### Step 11 — Cleanup and validation
- **11.1** Delete remaining v1 code; verify no dead imports
- **11.2** Run IMPR-2026-E9D end-to-end; document behavioural deltas
- **11.3** Create and run IMPR-2026-FS1 (financial services showcase)

### Step 12 — Then, and only then
- Build **Improve** phase on the correct foundation
- Build **Control** phase on the correct foundation

### Step 13 — Pre-production
- **13.1** Provision Azure Database for PostgreSQL
- **13.2** Migrate to `PostgresSaver` + `PostgresStore`; run existing
  tests against PostgreSQL
- **13.3** Multi-user identity, session isolation, tagged observability

**Parallel workstreams**, run alongside rather than after: the
evaluation dataset (§14) and the five phase skills (§8.4). Both encode
Black Belt domain judgment and are authored jointly.

**Early, cheap, do it first:** `menu.py`, the developer orchestrator
that replaces the destructive `start.ps1` (which hard-resets to
`origin/main` on every run). Roughly 30 minutes, removes a live
data-loss hazard.

---

## 16. Out of Scope

### 16.1 Architecturally excluded — not deferred

| Item | Why |
|---|---|
| **MCP — server, client, or dependency** | §1.2. No promotion trigger exists. |
| Live system integrations (SAP, KPI feeds) | §1.2 — the Belt uploads data |
| External verification benchmarks | Requires a live integration |
| deepagents dependency | Pre-1.0 with breaking changes between minors (§3.4) |

### 16.2 Out of scope for this refactor

- Agent Flow build-out
- Cosmos DB migration
- LangChain Hub for prompts
- Mobile UI
- `index.html` modularisation

### 16.3 Deferred to v2.2+ with promotion triggers

Fourteen tracked items with explicit triggers live in
REFACTORING_AGENT_IMPROVE.md §87. Architecturally significant ones:

| Item | Trigger |
|---|---|
| PostgreSQL migration | **Scheduled** — before production launch |
| Debate subgraph for root cause validation (Analyse) | Base coaching loop stable in production |
| Observer Agent — cross-project monitoring | Multiple concurrent projects in production |
| Multi-tenant filtering on `improve_case_index` | Deployment to multiple organisations |
| `DeltaChannel` checkpoint compression | Sessions exceeding ~200 turns |
| Feedback-driven chunk score adaptation | Retrieval evaluation shows systematic misses |

**Note the shape:** most triggers reduce to *"more than one deployment
or more than one customer."* The single-tenant assumption is
load-bearing in more places than it appears.

---

## 17. Decisions Resolved (v2.2)

| Decision | Resolution |
|---|---|
| Graph topology | Hierarchical subgraphs, **static edges between phases** |
| Threading | **One `thread_id` per project**, auto `checkpoint_ns` per subgraph |
| Checkpointer placement | **Parent graph only** — subgraphs compile without one |
| Checkpointer backend | **Phased** — Azure Blob → PostgreSQL before production |
| Cross-phase handoff | **Store-mediated boundary mappers**, not parent state |
| Coach pattern | **`create_agent`** with eight middlewares and a per-phase tool subset |
| Planner | Explicit node producing a structured plan; Level 1 planner is deterministic |
| Rubric grading | **Custom `DMAICGraderMiddleware`** on `create_agent`, not deepagents |
| HITL mechanism | **Graph-level `interrupt()`**, not `HumanInTheLoopMiddleware` |
| Gate flow | **Nine steps, two nodes, four validation layers** |
| Coherence and constraint checks | **Lightweight LLM**, not format checks |
| Mid-phase value conflicts | **Auto-flag, no threshold**, with re-approval cascade |
| Retrieval | **Three tools**, multi-query + RRF mandatory, metadata filters |
| `improve_case_index` | **Active** — yokoten via `rag_lookup_case_history` |
| Computation | **20 tools**, per-phase binding, pure functions |
| Context compression | `SummarizationMiddleware` + typed state fields |
| Compensation | **Native `error_handler=`**, no custom Saga framework |
| Fallback Level 3 | **Azure Cache for Redis** — new infrastructure |
| Deployment layer | **FastAPI** — LangGraph Server requires a commercial licence |
| Protocol layer | **None** — MCP architecturally excluded |
| Diagram generation | LLM emits JSON, frontend renders SVG from templates |
| Prompt management | Constants in `core/prompts.py` |
| Project identifier | **`case_id` everywhere** — documents match the code and the indexes (§4.1.1) |
| Name for a phase's captured fields | **`artifacts`** — `captured_fields` and `phase_inputs` retired (§4.9) |
| Captured field typing | **All `str`**; the 20 computation tools parse at the point of use (§4.6) |
| Cross-phase linkage | **Explicit reference dicts** on three fields — deterministic grader check, not LLM judgment (§4.7) |
| Computation tool output | **`artifacts["computation_results"]`** — one list per phase, not typed per-phase fields (§4.8) |
| Gate document write | **`gate_apply_node` writes both** the store and `PhaseState.final` (§3.6.1) |
| Gate-required fields | **Two tiers** — Tier 1 blocks, Tier 2 warns with an acknowledged gap (§3.7.1) |
| Grader verdict statuses | **`pass` / `warning` / `fail`**, belt-level aware (§3.7.1, §3.7.2) |
| `coaching_plan` shape | **Single transient `dict`**, overwritten per planner turn (§3.5) |

---

## 18. Change Log

| Date | Version | Change |
|---|---|---|
| May 2026 | 0.1 | Initial scaffold |
| Jun 2026 | 0.2 | Define + Measure complete |
| Jun 2026 | 1.0 | Analyse + Improve + Control complete. v1 in production. |
| Jun 2026 | 2.0 | DRAFT — Path C architecture proposed |
| Jun 2026 | 2.1 | Path C ratified: hierarchical subgraphs, tool-calling coach, Azure Blob checkpointer, interrupt-based gates, SSE streaming, LangSmith mandatory. |
| Jun 2026 | 2.1.1 | §6.1.1 base64 envelope for checkpoint blobs (surfaced during commit 2.1). |
| Aug 2026 | **2.2** | **Ground-up rewrite aligning with the EDUCATIONAL.md review.** Static edges between phases; one `thread_id` with auto `checkpoint_ns`; checkpointer and store on the parent only; phased Blob → PostgreSQL; `AzureBlobStore` and store-mediated boundary mappers; six-node phase subgraph with conditional edges and cycles; `create_agent` with a four-middleware stack; three retrieval tools with multi-query + RRF; 18 per-phase computation tools; nine-step gate across two nodes; four-layer validation stack; mid-phase conflict detection with re-approval cascade; native `error_handler=` compensation; per-node timeouts; two three-state circuit breakers; four-level fallback chain with Redis cache; `recursion_limit=11` hop cap; **canonical index schemas in §7**; MCP architecturally excluded; FastAPI confirmed as the deployment layer. |
| Aug 2026 | **2.2.1** | **Index schema facts resolved against the live service (§7).** `improve_case_index.phase_summary_analyse_phase` renamed to `phase_summary_analyse` by delete + recreate (index empty, no reindex required) — Step 3.6 closed; writer-side phase-key alignment carried forward in §7.3. `improve_evidence_index` confirmed to have **no** `uploaded_at` field — the timestamp lives in the non-sortable `metadata` blob, so the `uploaded_at desc` ordering clause is dropped from §7.2 and `rag_lookup_evidence` takes no `order_by`. `improve_case_index.embedding` confirmed 3072d on profile `improve-vector-profile`. |

| Aug 2026 | **2.2.2** | **Internal phase key `analyse_phase` renamed to `analyse` across the codebase (§7.3.1)** — completes the schema rename in 2.2.1 on the writer side. Directory `phases/analyse_phase/` → `phases/analyse/`; `orchestrate_analyse_phase` / `validate_analyse_phase` and their graph node names lose the suffix; the key is now `analyse` in `PHASE_ORDER`, `phase_inputs`, `EXTRACTION_MAP`, `ORCHESTRATOR_CONTEXT_MAP`, `GATE_CHECKS`, `PhaseSummaryRecord`, and `CaseDocument.phases`. `AnalysePhaseInput` unchanged — it already matched convention. Node rename was free only because no checkpoints existed yet. |

| Aug 2026 | **2.2.3** | **Methodology retrieval fixed and its failure contract defined (§7.1, §7.1.1).** `search_knowledge` filtered on `phase`, a field that does not exist on `improve_knowledge_index`, so Azure rejected every phase-filtered query and a bare `except Exception` rendered it as "No relevant methodology content found" — phase-filtered retrieval had never returned a document. Filter corrected to `phase_relevance`; cross-phase value corrected from the non-existent `all` to `general` (218 docs), closing the §7.1 open item with the confirmed enumeration. Failures now raise `KnowledgeSearchError` carrying an `AgentImproveError` (§12.3, `core/errors.py` added), classified by Azure exception type with 4xx as permanent/do-not-retry. `step_log` wiring deferred to step 4.1 — the dict shape is already emitted. |

| Aug 2026 | **2.2.4** | **Failure contract extended to all three retrieval functions (§7.1.1).** `search_cases` and `search_evidence` carried the same bare `except Exception` → `[]` as `search_knowledge`, so a broken case or evidence query also read as "nothing found". Both now raise `KnowledgeSearchError` with the same classification. `RETRIEVAL_EXCEPTIONS` additionally covers `OpenAIError`, since the query-embedding call runs inside the same `try` and would otherwise escape raw; embedding failures carry an `EMBEDDING_` code prefix. Result materialisation moved inside the `try` (the pager is lazy), imports hoisted out of it, `case_id` OData-escaped, and the metadata-blob parse narrowed to `JSONDecodeError`/`TypeError` with a warning instead of a silent `pass`. Callers `search_improve_cases`, `search_improve_evidence`, and `_generate_sipoc_draft` updated to catch the typed exception. |

| Aug 2026 | **2.2.5** | **Ingestion contract fixed and documented (§7.1.2).** `ingest_knowledge.py` emitted `phase`, not a field on the index, so `phase_relevance` was never populated by the script. Fixing the key name alone proved insufficient: LangChain promotes metadata keys only against `self.fields`, which defaults to `[id, content, content_vector, metadata]` and never introspects the live index — so `get_knowledge_vectorstore()` now passes `fields=KNOWLEDGE_INDEX_FIELDS`. Both changes are required; either alone leaves the index unfilterable. Also: metadata reduced to the live four-key shape, `source_file` emitted as a stable label rather than a filename, chunking moved to per-page so `page_number` is a real page rather than a chunk index, and document keys made deterministic and passed via `ids=` so re-ingest upserts instead of duplicating. Phase mapping confirmed empirically as per-chunk keyword scoring, not chapter mapping, and documented with the evidence. |

| Aug 2026 | **2.2.6** | **LangGraph upgrade target moved 1.2.7 → 1.2.10 (§1, §2.5.1).** Verified against PyPI and the verbatim GitHub release bodies for 1.2.6–1.2.10 via `/verify-current-version`. The **floor is unchanged at ≥1.2.6** — the nested-subgraph `checkpoint_ns` inheritance fix (#8053, a regression introduced in 1.2.3) landed there and nothing since has touched it. Of the three intervening releases, 1.2.7, 1.2.8 and 1.2.9 are **entirely `DeltaChannel` fixes**, and `DeltaChannel` is not used (CLAUDE.md §3.6, backlog item 12) — so they are no-ops for us. 1.2.10 adds v3 `stream_events` return typing with native projections, and exposes `trace_policy` as a **new additive kwarg on `add_node`** alongside the existing `timeout=` and `error_handler=`; no existing signature changes, no deprecations, no breaking changes. **`trace_policy` is deliberately not adopted:** the same release contains both "drop tags from TracePolicy" (#8402) and "revert: delete TracePolicy" (#8403), so the API is unsettled. Per-node `TimeoutPolicy` and node-level `error_handler=` are unchanged across all four releases, so §9.2 needs no revision. No code change accompanies this amendment — the upgrade itself is still step 2.5.1, not yet executed. |

| Aug 2026 | **2.2.7** | **`dmaic_plan`, `key_decisions` and `open_items` removed from `SupervisorState` (§4.1, §4.3).** All three were redundant against mechanisms that already existed, and each was a second source of truth able to drift out of agreement with the first. `dmaic_plan` stored a plan that is not variable — DMAIC order is fixed in static edges (§3.2) — while the project's substantive plan is Define's gate document in the store plus `improve_case_index` metadata. `key_decisions` duplicated captured fields: a decision the Belt commits goes through `record_field`, is approved at a gate, and lands in `artifacts` and then the store, all outside `messages[]`, so the compression guarantee that motivated the field was already satisfied without it. `open_items` duplicated gate readiness, which `check_gate_status()` and the four-layer validation stack (§9) compute on demand — and a stored copy can contradict `DMAICGateValidator`, which a derived one cannot. `gate_passed` added to the schema block: it is what the supervisor routes on and was referenced throughout while never being declared. The Define output mapper no longer lifts `key_decisions`/`open_items` back onto the parent; it returns orchestration values only. Parent state is now `messages`, `history`, `project_id`, `project_context`, `phase_index`, `current_phase`, `gate_passed`, `final_output`. No code change accompanies this amendment — `core/state.py` is written at the `SupervisorState`/`PhaseState` split, which is still ahead in the sequence. |

| Aug 2026 | **2.2.8** | **`project_context` removed from `SupervisorState` (§4.1, §4.3, §6.3).** The fourth field to fail the same test as 2.2.7's three, and the clearest case of it: an audit found the field had **no writer anywhere** — no node, mapper or middleware set it in any document or any code path — while its schema comment claimed "set once after Define" and its only declared reader, `define_input_mapper`, runs *before* Define. No later phase read it either; §4.3 already routes Measure through Control's `phase_context` through the store. Its provenance is the Edureka lab's `task: str` (REFACTORING_AGENT_IMPROVE.md §18) — an inherited field, like the renamed `step_index` and the removed `dmaic_plan`, not a designed one. **What covers it instead:** each input mapper composes `phase_context` at the boundary — Define from the case record, later phases from the prior phase's artifacts — so the rule is now uniform and an input mapper's only dependency is `BaseStore`. The substance was never in this field to begin with: problem, goal, scope and business case are Define's gate document in the store, and title, department, belt level and target date are the case record and the `improve_case_index` row (§7.3). The `before_model` middleware (§8.5 in CLAUDE.md) already injects captured fields and prior gate documents into every coach prompt, so no planner loses context. **One addition:** a `("projects", pid, "case")` store namespace, written once at session start from `cases/case_{id}.json`, giving `define_input_mapper` a store-only source — the case blob (§6.4) stays the system of record. Parent state is now `messages`, `history`, `project_id`, `phase_index`, `current_phase`, `gate_passed`, `final_output`. **Code change:** `ANALYST_MEASURE_SUMMARY` and `ANALYST_ANALYSE_SUMMARY` deleted from `core/prompts.py` — unreferenced v1 remnants, and the `{project_context}` placeholder in the first was the field's only trace in code. `core/state.py` is unaffected; it is still written at the `SupervisorState`/`PhaseState` split. |

| Aug 2026 | **2.2.9** | **State design closed — all 15 findings from `STATE_DESIGN_RESOLUTION.md` applied (§3.6.1, §3.7.1, §3.7.2, §4, §6.3, §13).** The audit that produced 2.2.7 and 2.2.8 was run to completion across both schemas, the store, the rubrics and the validation stack. **Naming:** `project_id` → **`case_id`** everywhere (§4.1.1) — the code, both Azure AI Search indexes, the blob layout and the case models already said `case_id`, and only the governance documents disagreed; `artifacts` is now the single name for a phase's captured fields, retiring `captured_fields` from prose and `phase_inputs` from v1 references (§4.9). **`SupervisorState` is seven fields**, with `gate_passed` retyped `list[str]` → `dict[str, bool]` and `final_output` `str` → `Optional[dict]`; `current_phase` and `phase_index` are documented as derived-but-kept, with the supervisor owning consistency from a single write site (§4.1.2). **`PhaseState` gains four fields and loses one name**: `gate_attempts` (the counter whose absence reintroduced the v1 "attempts always reset to 0" bug — §4.2.1), `validator_feedback` (accumulated per-attempt feedback, without which the shared cap of 3 is retry-without-memory — §4.2.2), and `citations` / `uploads` (the evidence trail the gate document could not previously show — §4.2.3); `feedback` → `belt_edits`, splitting the Belt's gate corrections from the system's validation results; `final` `str` → `dict`; `coaching_plan` confirmed a single transient `dict`, not a list (§3.5). **Finding 2 — the missing writer:** `gate_apply_node` writes the approved gate document to **both** `store.put(("projects", case_id, "artifacts"), phase, …)` and `PhaseState.final`, and the store-mediated handoff had until now been specified with a reader and no writer (§3.6.1). The `gate_documents` store namespace is retired as a duplicate of `artifacts`, and the store prefix becomes `store/projects/{case_id}/{kind}/{key}.json`. **Typing:** all captured fields are `str`, parsed by the 18 computation tools at the point of use — §4.6 corrects the earlier claim that Measure reads Define's baseline as a typed float, which no schema in this project ever provided. Three cross-phase reference fields are the enumerated exception, carrying `references_phase` / `references_field` / `references_value` so the grader verifies linkage deterministically rather than by LLM judgment (§4.7). Computation-tool output lands in `artifacts["computation_results"]` as a list of typed dicts, giving the grader a mechanical answer to "was a hypothesis test actually run?" (§4.8). **Two-tier fields (§3.7.1):** Tier 1 blocks at Layer 2b, Tier 2 produces a grader warning the Belt may proceed past with a recorded `acknowledged_gaps` entry — which resolves the Layer 2b / Layer 2d contradiction where the grader could fail what the gate never required. `CriterionVerdict` gains `"warning"` alongside `"pass"` and `"fail"`, plus a `tier` field. The grader is belt-level aware: FMEA, DOE, X-Y matrix and statistical problem statements are flagged for Black Belt only and suppressed for Green Belt; stability / special-cause analysis warns strongly for both (§3.7.2). **New fields (§13):** `voc_summary` (Define, Tier 1), `problem_statement` consolidated (Define, Tier 1), `baseline_sigma` (Measure), `ruled_out_causes` (Analyse), `post_improvement_metric` / `improvement_delta` / `financial_impact_verified` / `handover_documented` / `lessons_learned` / `transferability` (Control) — a project that cannot show the baseline moved has not demonstrated anything. No code change accompanies this amendment; `core/state.py` and `core/substate.py` are written at Step 4.1. The dead `ANALYST_MEASURE_SUMMARY` / `ANALYST_ANALYSE_SUMMARY` templates were already removed in 2.2.8 and are confirmed absent. |

| Aug 2026 | **2.2.10** | **Findings 16–23 applied — the executor contract, node names and output schemas closed (§3.2.1, §3.3.2, §3.4, §3.4.1, §4.10, §8.1, §8.2, §13).** A second reading pass over the three documents after 2.2.9 found eight further inconsistencies, all of them between prose that had been ratified and code examples that predated it. **Node names (16):** the phase subgraph is `planner → executor → validation_stack → gate_review → gate_apply`. `policy_advisory` as node 3 was the serious error — it left the subgraph with **no node running the four-layer stack** — and `revise` as node 5 both misnamed and undersized `gate_apply`, which runs the policy advisory, processes approval, and writes the gate document. Revision is an edge back to the planner carrying `validator_feedback`, not a node. **Executor tool binding (17):** the gate validator and the policy advisory were listed among the executor's bound tools; neither is a tool. The validation stack is a node reached by an edge — as a tool the coach would decide whether to be validated, which is backwards — and the policy advisory is logic inside `gate_apply`, firing when the coach is no longer in the loop. **Two graders, two rubrics (18, 20):** `DMAICGraderMiddleware` grades the coach's **process** against a single shared `COACHING_QUALITY_RUBRIC` on **every turn**; validation Layer 2d grades the **gate document** against the phase's `PHASE_RUBRIC` **once**, at the boundary. They are complementary — the middleware prevents eight turns built on a weak foundation, Layer 2d catches cross-field and cross-phase contradictions no per-turn check can see. §3.7's step 2d had named the middleware, which was wrong. **Middleware (21, 19):** `ModelRetryMiddleware` adopted, taking the stack to **five**; it is the mechanical-retry tier (retry the same call) and does not overlap the fallback chain (swap the model). `BeforeModelStateInjection` moved from **last to first** — declaration order is execution order for `before_model` hooks, so listing it last placed project facts after skills loading and summarisation had already shaped the prompt, inverting the rule §8.5 exists to enforce. **Output schemas (22):** two conflicting `DefineOutput` definitions existed, neither matching the ratified fields and both using `float` against §4.6; `MeasureOutput`, `AnalyseOutput`, `ImproveOutput` and `ControlOutput` were referenced throughout and defined nowhere. All five are now canonical in §4.10 with per-phase gate assembly, and all five carry the same four gate-metadata fields — the cross-check found `citations` and `uploads` reaching `PhaseState` but never the gate document. **Structured output (23):** `response_format` on the executor is correct and is retained; the error was the schema. It carries **`CoachingResponse`** — a per-turn extraction of `message`, `fields_captured` and `citations` — not a complete gate document the coach cannot produce on turn one. `value: Any` in `fields_captured` is required so the three cross-phase reference dicts remain capturable. **`record_field` is retired**, taking the universal eight to **seven**: capture is now part of the response shape rather than a tool call the coach can omit mid-retrieval. Per-phase totals become Define 8, Measure 15, Analyse 12, Improve 8, Control 11 — Measure moves off the top edge of the 10–15 selection-quality range. **Integrity check run across all three documents:** field types, node names, canonical identifiers, both rubrics, store namespaces, tier classification, verdict statuses, tool counts, and the complete capture-to-store schema chain verified mechanically — every schema field assembled, every Tier 1 field coach-reachable, every Tier 2 field capturable or computable (§4.10.4). No code change accompanies this amendment. |

| Aug 2026 | **2.2.11** | **eBook extraction gaps closed — Findings 24 and 25 (§3.4.2, §4.10.5, §4.10.6, §13).** The five BB eBook extractions under `skills/extraction/` identified **57 deliverables with no corresponding field**. Six cross-cutting decisions close 25 of them; the rest are handled by SKILL.md coaching content or by mechanisms that already exist, and both sets are recorded in §4.10.5 so they are not re-litigated. **Two fields land on all five schemas:** `issues_and_barriers` (**Tier 1** — every real project has blockers, and a Belt reporting none has not looked; distinct from `acknowledged_gaps`, which is system-generated and records skipped Tier 2 fields) and `secondary_metrics` (Tier 2 — the field that catches a project which succeeded on its own terms and did damage elsewhere; a named eBook deliverable in every phase). **Measure gains two Tier 1 fields:** `xy_matrix_summary` and `vital_few_xs`, carrying the eBook's own labelled Measure→Analyse hand-off, which previously had no carrier at all — Analyse's entry condition was a list nothing recorded. **Analyse gains `practical_significance` (Tier 1)**, restoring the eBook's two-gates-in-series rule: a root cause significant at p=0.001 that explains 0.1% of the problem is not worth an Improve solution, and Improve's `pilot_result` rubric already demanded both. Analyse also gains `statistical_problem_statement` and `process_owner_buyin` (Tier 2); Improve gains `explanatory_power` and `process_owner_buyin` (Tier 2); Control gains `project_signoff` (Tier 2), which the gate had been asking for with no field able to answer. **`control_plan` becomes a `dict` of five sub-plans** — documentation, monitoring, response, training, aligning_systems (§4.10.6). A single string could not show that four were done and one was skipped, which is what the eBook's ten roadmap steps (five develop, five implement) exist to surface; four extraction gaps close with this one change. **FMEA is deliberately NOT added to any schema** (§4.10.5) — heavy manufacturing methodology built around severity × occurrence × detection scoring of physical failure modes, where the typical Agent Improve case is service or transactional DMAIC and `xy_matrix_summary` / `vital_few_xs` already do the prioritisation job. If a Black Belt performs one it lives in `uploads`. **Two tier/placement corrections:** the statistical problem statement moves from Define BB-only to **Analyse, all Belts**, where the eBook asks it; and the X-Y matrix stops being BB-only, becoming a Tier 1 field for everyone. DOE is now the only belt-gated item in §3.7.2. **Finding 25 — the six-step computation coaching pattern (§3.4.2):** explain why → guide data preparation → run → interpret → visualise → coach the next move, for all 18 computation tools, enforced by a new `COACHING_QUALITY_RUBRIC` criterion checked on every turn. A coach that returns `p_value: 0.001` with no interpretation has handed the Belt a number they cannot act on or defend at a gate. This is the most content-heavy part of each SKILL.md — Measure's eight computation tools alone are 160–320 lines. **Page citation corrected:** §13.5 and REFACTORING §42 cited "eBook p681" for verified financial impact; that page is the Control quiz cover and the material is at **book pp677–679**. **Field counts:** Define 14 · Measure 12 · Analyse 13 · Improve 12 · Control 15. No code change accompanies this amendment. |

| Aug 2026 | **2.2.12** | **Process maps, stability and experiment justification promoted to schema — Finding 26 (§4.10.7, §13).** Three of the nine gaps that v2.2.11 assigned to SKILL.md coaching content were reclassified as **Tier 1 fields**, on one argument: a coaching prompt produces a conversation, and a conversation cannot be read by the next phase's planner or checked by the grader. **`process_map_sipoc` (Define, Tier 1, dict)** — six sub-fields: suppliers, inputs, process_steps, outputs, customers, process_kpis. The failure this catches is the partial map: *“far too often Belts capture only segments of the process”*, which produces a project that cannot show improvement because the baseline never covered the whole thing — invisible at Define, expensive at Control. The coach validates end-to-end coverage, challenges fragments, checks consistency with `project_scope`, and decomposes an uploaded diagram into the structured form rather than accepting the image as the deliverable. **`detailed_process_map` (Measure, Tier 1, dict)** — six sub-fields: steps, cycle_times, resources, value_vs_waste, measurement_points, baseline_kpis. The coach checks it expands Define's SIPOC correctly and that measurement_points align with `data_collection_plan`. **These two close the before/after KPI chain**: Define's `process_kpis` names what is measured, Measure's `baseline_kpis` holds the before values, Control's `post_improvement_metric` holds the after — and the grader verifies the same measurement points carry different values, so a project whose Control metrics sit on steps Define never listed is caught. **`stability_assessment` (Measure, Tier 1)** — was a Tier 2 rubric criterion with no field and a strong warning; the warning was right and the tier was not. The eBook sequences stability as a precondition for capability (book p230), because a Cpk computed across special causes is an average of two different processes, not a capability figure. **`experiment_justification` (Improve, Tier 1)** — does not require an experiment, it requires a decision, stated as one of three: DOE conducted, simplified one-factor experiment, or none needed because the solution follows from root cause analysis. All three are valid; the failure it catches is drifting past the question, not skipping DOE — consistent with the eBook's own *“do not force Designed Experiments”* and its estimate that over 80% of projects find their solution in Analyse. The Improve SKILL.md carries a plain-language DOE explanation so a Belt without statistical training chooses rather than defaults. **Structured dicts go from one to three** (§4.10.4) — `control_plan`, `process_map_sipoc`, `detailed_process_map` — distinct from the three cross-phase reference dicts, and the grader checks every sub-field is populated. All three are Tier 1 and use bracket access in gate assembly; only the cross-phase reference keeps `.get(…, {})` for shape-guarding. **Six gaps remain deliberately field-free** and are listed in §4.10.5: stakeholder analysis, project plan, short/long-term capability, lean opportunities, benefits deferral date, Define-stage finance involvement. **Field counts:** Define 15 · Measure 14 · Analyse 13 · Improve 13 · Control 15. **Tier 1:** 6 · 7 · 4 · 4 · 3. Schema/assembly parity and the per-phase compatibility table verified mechanically in both documents. No code change accompanies this amendment. |

| Aug 2026 | **2.2.13** | **`imr_chart_limits` added to the Control phase (§8.2, §13.5).** Control's chart set covered batched measurements (`xbar_r_chart_limits`), proportions (`p_chart_limits`) and counts (`c_chart_limits`), but not the individuals / moving-range chart — which the eBook recommends for most **inputs** and for low-volume or long-cycle processes (book p631). That is the common case in service and transactional work: most office processes produce one figure per week, not batches of five. Without the tool the Control skill had to coach a workaround — aggregate into weekly totals and use a proportion chart — which is the wrong chart for the data and produces limits that do not mean what the Belt thinks. **Control goes from 11 tools to 12**; the maximum across phases is unchanged at 15 (Measure), so the §5.2 cap of 16 is untouched. **A pre-existing count error was found and corrected in the same pass:** every document has said "18 computation tools" since v2.2, while the §8.2 table has always enumerated **19** (1 + 8 + 5 + 1 + 4). With the new tool the correct figures are **20 computation tools and 27 total**. The table was always right and the prose was wrong; the figure had been restated across nine amendments without anyone re-deriving it. Per-phase totals are now **8 / 15 / 12 / 8 / 12**. No code change accompanies this amendment — `knowledge/computation.py` is written at Step 3.4. |

| Aug 2026 | **2.2.14** | **Computation coaching goes from six steps to seven; three new `COACHING_QUALITY_RUBRIC` criteria; §87 backlog item 15 (§3.4.1, §3.4.2, §87).** The first SKILL.md review produced 17 notes, three of which change the coaching approach rather than its content. **Seven-step computation pattern (§3.4.2).** Step 1 is now *educate on the concept* — what this **is**, in plain language, with a real-world analogy, and what the output numbers will mean, before any are produced. The original pattern opened with “explain why”, which assumes the Belt already knows what a Cpk or a p-value is; most do not, and Agent Improve exists to serve teams with no Six Sigma qualification (§1). A Belt told “this matters because it shows capability” and then handed `Cpk = 0.82` has learned nothing — they cannot judge whether 0.82 is good, and cannot defend it at a gate. Educating first also front-loads the interpretation: by the time the number arrives the Belt already holds the frame, so step 5 confirms rather than introduces. **Three rubric criteria added (§3.4.1).** *Show a concrete example of a completed answer before asking the Belt to produce theirs* — describing what good looks like in a SKILL.md tells the developer, not the Belt, and show-first reaches a good answer in one turn instead of three of ask-and-correct. *No external URLs from training data* — a model asked about methodology will produce stale, unverifiable links outside the grounding contract of §1.9; methodology comes from `rag_lookup_methodology`, woven into the coach's own voice. *Educate before computing*, replacing the narrower “explain the purpose before calling”. **§87 backlog item 15 — multi-source knowledge index (Finding 27).** `source_document` and `tenant_id` on `improve_knowledge_index`, a priority-ordered retrieval filter in `rag_lookup_methodology`, and phase-classifier re-evaluation for non-BB-eBook documents. Deferred because the refactor builds against one knowledge source and the change is incremental — two fields and one filter clause — with no second document to test against. Overlaps item 1 (multi-tenant filtering on `improve_case_index`); both fire on the same trigger and should be planned together. **All five SKILL.md files rewritten** to the show-first pattern, with an A→F session flow (opening → resumption → per-field → capture feedback → Tier 2 offered → gate ready), a per-phase Document Layout section defining how the live gate document renders, upload handling, `CoachingResponse` capture instructions, and the seven-step sequence for all 20 computation tools. No code change accompanies this amendment. |

| Aug 2026 | **2.2.15** | **Frontend Patterns 3 and 4 merge into the live gate document (§11.4, §11.6, new §11.7; REFACTORING §77).** Showing the Belt their captured fields (Pattern 3) and showing them their progress (Pattern 4) are the same view at different zoom levels, and splitting them across two moments produced the wrong behaviour: fields visible only at the gate, progress visible only as a number. They are now one component — a single live document tab beside the chat, always visible, updating the moment a field is captured via `CoachingResponse.fields_captured` (§4.10.1), readable as a document rather than a field list, and downloadable as PDF or Word at any point with `[not yet captured]` placeholders mid-phase. **The rendering spec lives in the skills, not here.** Each SKILL.md carries a Document Layout section defining which fields get headers, which render as tables, and where `computation_results` and `citations` appear; §11.7 and REFACTORING §77 cross-reference all five. The layout is a coaching artefact — it decides what the Belt sees while being coached and what they hand a sponsor — and it changes when the field set changes, so keeping it beside the coaching guidance means one file changes rather than two. **Two stale claims corrected in the same pass.** Progress is derived from `PhaseState.artifacts` against the phase's Tier 1 / Tier 2 field list; there is no stored `completeness_score`, and a stored one would be a second source of truth able to disagree with the gate (§4.1). Tier 1 and Tier 2 get **separate** counts — a Belt at 6/6 required and 0/5 recommended can pass the gate, where a single blended percentage would read 55% and imply otherwise. §77's Pattern 3 example and its data-mapping list still used the v1 `what` / `why` / `scope` / `how_goal` field names and `captured_fields`; both now use the ratified schema. **No code change and no CLAUDE.md change** — no rule moved, so CLAUDE.md stays at 2.2.14. The data these patterns need is already checkpointed in `PhaseState.artifacts` (§4.2); what was missing was the rendering spec. |

### 18.1 Amendment procedure

1. The decision is recorded in REFACTORING_AGENT_IMPROVE.md with its
   rationale
2. The rule lands in CLAUDE.md
3. The design lands here
4. Version number incremented, change log entry added
5. **If the change touches an index schema, §7 is updated in the same
   commit as the Azure AI Search change** (§7.7)

Architecture changes are separate commits from feature changes.
