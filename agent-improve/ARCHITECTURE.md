# Agent Improve — Architecture & Design Document
**Agentlean Platform · DMAIC Improvement Agent**
Version 2.2.5 · August 2026
Status: v2.2 architecture ratified · refactor in progress (Step 2.2 complete;
Step 3.6 index schema rename applied)

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
| Stack | Python 3.11 · FastAPI · LangGraph 1.2.7 · LangChain 1.x · Azure OpenAI · Azure AI Search · Azure Blob · Azure Cache for Redis |
| Persistence | Checkpointer + Store (Blob now → PostgreSQL before production) |
| Tracing | LangSmith (mandatory) |
| Protocol layer | **None. MCP is architecturally excluded (§1.2).** |

### 1.1 What changed from v2.1.1

| Area | v2.1.1 | v2.2 |
|---|---|---|
| LangGraph | 0.2+ (stated), 1.1.10 (pinned) | **1.2.7** — required for subgraph `checkpoint_ns` and native reliability primitives |
| Phase subgraph | 5 nodes, linear with one conditional | **6 nodes, conditional edges and cycles** (§3.2) |
| Coach | Bare LLM with 7 bound tools | **`create_agent`, 4 middlewares, per-phase tool subset** (§3.3, §3.4, §8) |
| Retrieval | 2 tools, single query | **3 tools, multi-query + RRF, metadata filters** (§7.4, §8.1) |
| Computation | None | **18 tools, bound per phase** (§8.2) |
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
| 1 — Global | **Deterministic gate-checker** — reads `gate_passed[]`. No LLM. | Static edges | Phase subgraphs |
| 2 — Phase | `phase_planner` (LLM) | `phase_executor` (`create_agent`) | Leaf tools |
| 3 — Leaf | — | — | Tools are functions, not pairs |

```
supervisor_graph                     thread_id = project_id ("IMPR-2026-FS1")
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
              │  │ tools  │  │  8 universal +           │           │
              │  │ 9–16   │  │  phase computation       │           │
              │  └────────┘  │                          │           │
              └──────┬───────┘                          │           │
                     │ draft (dict)                     │           │
                     ▼                                  │           │
             ┌────────────────┐                         │           │
             │policy_advisory │  contradiction check    │           │
             │                │  vs prior gates (§3.8)  │           │
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
                       │  VALIDATION STACK   │  §3.7 — four layers
                       │  2a coherence       │  cheapest first
                       │  2b field presence  │  shared cap: 3 attempts
                       │  2c constraints     │
                       │  2d rubric grader   │
                       └──────────┬──────────┘
                          fail    │    pass
                     ┌────────────┘
                     ▼                          ▼
              ┌────────────┐          ┌──────────────────┐
              │  revise    │          │ gate_review_node │  interrupt()
              └─────┬──────┘          └────────┬─────────┘  Belt sees fields
                    │                          │
                    └──▶ back to planner        │ Command(resume=...)
                         (accumulated feedback) ▼
                                       ┌──────────────────┐
                                       │ gate_apply_node  │
                                       │ · apply edits    │
                                       │ · policy advisory│
                                       │ · output mapper  │
                                       │   → store.put()  │
                                       └────────┬─────────┘
                                                ▼
                                               END
                                       (parent's static edge
                                        advances the phase)
```

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

**Leaf tools are not nodes.** Extraction, retrieval, computation, gate
validation, and the advisory tool are bound to the executor. From the
subgraph's perspective the executor is one node; from inside it,
several tools can fire per invocation.

### 3.3 Inside `phase_executor` — `create_agent` with per-phase tools

```python
executor = create_agent(
    model=get_llm("coach"),                          # operational-premium
    tools=UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase],
    response_format=ProviderStrategy(PhaseOutput),   # CLAUDE.md §4.6
    middleware=[                                      # §3.4 — order matters
        DMAICSkillsMiddleware(...),
        DMAICGraderMiddleware(...),
        SummarizationMiddleware(...),
        BeforeModelStateInjection(...),
    ],
    prompt=PHASE_COACH_PROMPT[phase],
)
```

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
            "configurable": {"thread_id": project_id}},
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

### 3.4 The middleware stack

Four middlewares on every phase executor, built on the six
`AgentMiddleware` hooks.

| Order | Middleware | Hook | Purpose | Source |
|---|---|---|---|---|
| 1 | `DMAICSkillsMiddleware` | `before_agent` + registered tool | Progressive disclosure of phase coaching instructions | **Custom** |
| 2 | `DMAICGraderMiddleware` | `after_agent` | Per-criterion quality evaluation against the phase rubric | **Custom** |
| 3 | `SummarizationMiddleware` | `before_model` | Context compression for long coaching sessions | LangChain core |
| 4 | `BeforeModelStateInjection` | `before_model` | Prepend structured project state at the top of the prompt | **Custom** |

**Three are custom by decision, not by necessity.** deepagents ships
`RubricMiddleware` and `SkillsMiddleware`, but the package is pre-1.0
with breaking changes shipping between minor versions, and adopting it
is all-or-nothing (`create_deep_agent` replaces `create_agent`).
Carrying a bounded amount of our own code is preferable to an unbounded
amount of someone else's pre-1.0 churn. All three migrate together
when deepagents reaches 1.0.

**`DMAICGraderMiddleware`** — `grader` role at temperature 0.1,
`max_iterations=3`, per-criterion verdicts, `on_evaluation` callback
writing each iteration into `step_log`. Grader internals stay private
to the middleware and never reach `PhaseState`. The Belt never sees
the grader loop.

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
                           "record_field"],
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

### 3.6 Gate flow — nine steps across two nodes

| Step | Node | What happens |
|---|---|---|
| 1 | `phase_executor` | Coach produces output; extraction captures fields |
| 2 | validation stack | Four layers (§3.7). **Belt does not see this loop.** |
| 3 | `gate_review_node` | `interrupt()` — Belt sees validated fields |
| 4–5 | *(frontend)* | Belt reviews, optionally edits |
| 6 | `gate_apply_node` | Policy advisory on the Belt's edits — **non-blocking** |
| 7 | `gate_apply_node` | Belt approves |
| 8 | checkpointer | State commits **only now** |
| 9 | output mapper → parent | `store.put()`, static edge advances the phase |

**Two nodes, not one.** `gate_review_node` fires the interrupt and
stops; it does nothing with the response. `gate_apply_node` reads the
Belt's response, applies corrections, runs the advisory, and routes.
Separating collection from application keeps the interrupt boundary
clean and makes the resume path testable.

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

| Layer | Checks | Mechanism | Model | Fires |
|---|---|---|---|---|
| **2a** Coherence | Real, meaningful, conclusive? Catches gibberish, vague non-answers, self-contradiction, off-topic, parroting the Belt | Lightweight LLM | `coherence`, 0.1 | **Every turn** |
| **2b** Field presence | All required fields populated? `DMAICGateValidator` static methods | **Deterministic** | None | Gate only |
| **2c** Constraints | Addresses budget / timeline / risk / measurement? | Lightweight LLM | `constraint`, 0.1 | Gate + key mid-conversation decisions |
| **2d** Quality rubric | Meets DMAIC standards per criterion? `DMAICGraderMiddleware` | LLM grader | `grader`, 0.1 | Gate only |

**Cheapest first; each fires only if the previous passes. The
iteration cap is 3, shared across all four**, with accumulated
feedback — never three per layer.

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

`policy_advisory` runs **before each coach response reaches the Belt**,
not only at gate boundaries.

**Detection.** A structured diff — no LLM call, negligible latency —
comparing values extracted this turn against `captured_fields`
committed at prior gates. If any numeric or categorical value differs,
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
    project_id:      str
    project_context: str                                  # set once after Define
    dmaic_plan:      list[dict[str, Any]]
    phase_index:     int                                  # 0=Define … 4=Control
    current_phase:   str
    key_decisions:   Annotated[list[str], operator.add]   # appended at each gate
    open_items:      list[str]                            # replaced at each gate
    final_output:    str
```

| Field | Reducer | Notes |
|---|---|---|
| `messages` | append | Compressed by `SummarizationMiddleware` |
| `key_decisions` | **append** | Decisions accumulate across the project |
| `open_items` | **replace** | Always reflects *currently* outstanding items |
| `phase_index` | last write | Distinct from `field_index` on `PhaseState` |

**`captured_fields` and `gate_documents` are deliberately absent.**
They live in the store (§6.3). Two reasons: parent state stays small
enough to checkpoint cheaply, and subgraph state does not reliably
propagate to the parent anyway (§4.3).

**`key_decisions` and `open_items` exist because of context
compression.** Anything that must survive `messages[]` compression has
to live in typed state, because it never lived in `messages[]`.

### 4.2 `PhaseState` — per-phase subgraph state

`core/substate.py`

```python
class PhaseState(TypedDict):
    messages:      Annotated[list[BaseMessage], operator.add]
    history:       Annotated[list[str], operator.add]
    phase_context: str                                    # what this phase coaches toward
    coaching_plan: list[dict[str, Any]]                   # planner output (§3.5)
    field_index:   int                                    # field within the phase
    draft:         dict[str, Any]                         # this turn's extraction
    artifacts:     dict[str, Any]                         # accumulated for the phase
    step_log:      Annotated[list[dict[str, Any]], operator.add]
    feedback:      dict[str, Any]                         # Belt corrections at gate
    final:         str                                    # approved gate document
    turn_count:    int                                    # coaching turns before the gate
```

**`draft` and `feedback` are `dict`, never `str`.** String-typed
handoffs force downstream nodes to parse prose out of an upstream
node's output — the anti-pattern this architecture exists to remove.

**`artifacts` and `step_log` are separate and stay separate.**
`artifacts` is WHAT was captured; `step_log` is HOW. A DMAIC quality
system must show not just what the root cause was, but how it was
determined.

Per-phase variants (`DefineState`, `MeasureState`, …) extend
`PhaseState` with phase-specific transient fields. All use explicit
`TypedDict`, not `MessagesState` inheritance — their dominant content
is structured fields, not conversation.

### 4.3 Boundary mappers — the store-mediated handoff

`SupervisorState` and `PhaseState` are different schemas, so something
must translate at the subgraph boundary. Two plain functions per phase,
in `phases/{phase}/mappers.py`.

```python
def define_input_mapper(parent: SupervisorState, store: BaseStore) -> PhaseState:
    """SupervisorState → DefineState. Prior artifacts come from the
    store, never from parent state."""
    return {
        "messages":      parent["messages"],
        "history":       [],
        "phase_context": parent["project_context"],
        "coaching_plan": [],
        "field_index":   0,
        "draft":         {},
        "artifacts":     {},
        "step_log":      [],
        "feedback":      {},
        "final":         "",
        "turn_count":    0,
    }


def define_output_mapper(child: PhaseState, parent: SupervisorState,
                         store: BaseStore) -> dict[str, Any]:
    """DefineState → SupervisorState update. Artifacts go to the store;
    only orchestration-relevant values return to the parent."""
    store.put(
        ("projects", parent["project_id"], "artifacts"),
        "define",
        child["artifacts"],
    )
    return {
        "current_phase": "measure",
        "phase_index":   1,
        "key_decisions": child["artifacts"].get("key_decisions", []),
        "open_items":    child["artifacts"].get("open_items", []),
    }
```

**Why the store and not shared state keys.** LangGraph documents that a
subgraph's state updates may not be visible to the parent immediately,
because each subgraph manages its own checkpoint namespace — and names
the Store as the fix for data that must cross graph boundaries. The
design follows that guidance rather than testing around it.

**Concrete Define → Measure sequence:**

```
1. Define subgraph runs; Level 2 cycles capture six fields into
   PhaseState.artifacts. Nothing is written outside the subgraph yet.
2. Gate: validation stack → interrupt → Belt reviews, edits, advisory
   fires, Belt approves.
3. Checkpoint commits. THEN define_output_mapper writes artifacts to
   the store and returns orchestration values to the parent.
4. Static edge fires: define → measure.
5. measure_input_mapper reads Define's artifacts from the store and
   builds Measure's phase_context.
6. Measure's planner reads that context plus Measure's required fields
   and plans its first coaching turn.
```

At no point does Measure parse Define's output from a message. If it
needs Define's baseline metric it reads a float — and if that float
later changes, §3.8 fires.

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
| Phase artifacts | Store | At gate approval (output mapper) |
| Gate document | Store | At gate approval |
| Case record | Case blob | On create, gate pass, upload — **never per turn** |
| Case summary + embedding | `improve_case_index` | On gate pass |

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
    state_injection.py            before_model injection
  validation/                                                           (NEW)
    gate_validator.py             DMAICGateValidator (static methods)
    coherence.py                  Layer 2a
    constraints.py                Layer 2c
    schemas.py                    Verdict models
  phases/
    define/
      graph.py                    Subgraph compilation (no checkpointer)
      nodes.py                    planner, executor, policy_advisory, revise
      gate.py                     gate_review_node, gate_apply_node
      mappers.py                  input/output boundary mappers         (NEW)
      schema.py                   DefinePhaseInput, DefineOutput
    measure/  analyse/  improve/  control/          (same shape)
  knowledge/
    retriever.py                  Azure AI Search clients
    tools.py                      The universal eight
    computation.py                The 18 per-phase computation tools    (NEW)
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
- Prefix: `checkpoints/{project_id}/`
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

**Namespace convention:** `("projects", project_id, <kind>)`

| Namespace | Keys | Contents |
|---|---|---|
| `("projects", pid, "artifacts")` | `"define"`, `"measure"`, … | Each phase's approved artifacts |
| `("projects", pid, "gate_documents")` | `"define"`, `"measure"`, … | Final approved gate document per phase |
| `("projects", pid, "step_log")` | timestamped | Append-only cross-phase audit trail |

- Container: `agent-improve-cases`
- Prefix: `store/{project_id}/{kind}/{key}.json`
- `project_id` is the same value as the graph's `thread_id`

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

**Retrieved by:** `rag_lookup_evidence(query, case_id, top_k)`

**Filter:** `case_id eq '{case_id}'`
**Ordering:** none — see below.

> **Verified against the live index (Aug 2026) — there is no
> `uploaded_at` field, and the ordering clause is dropped.**
>
> The live schema is exactly the five fields above. The upload
> timestamp *does* exist, but inside the `metadata` JSON blob, as
> `"timestamp"` — not `"uploaded_at"`:
>
> ```json
> {"case_id": "IMPR-2026-E9D", "upload_phase": "define",
>  "content_type": "image", "filename": "test_sipoc.png",
>  "blob_path": "uploads/IMPR-2026-E9D/test_sipoc.png",
>  "uploaded_by": "Vassilis", "timestamp": "2026-05-27T09:19:24+00:00"}
> ```
>
> `metadata` is a non-sortable `Edm.String`, so `$orderby` cannot reach
> the timestamp inside it. **`rag_lookup_evidence` therefore takes no
> `order_by` argument.** Recency ranking is not available on this index
> as currently shaped.
>
> If recency ordering is later judged necessary, it is a **schema
> change under §7.7**, not a tool change: add a first-class sortable
> `uploaded_at` field (`Edm.DateTimeOffset`, `sortable=True`) and
> backfill it from `metadata.timestamp` at reindex time. Do not attempt
> to sort client-side on the parsed blob — that reorders only the
> `top_k` already returned, which is not the same result.

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
| `embedding` | SingleCollection (3072d) | **Vector field** — note the name |

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
differs from the other two indexes, which use `default` — the
asymmetry is safe by construction (§7.4).

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

**The vector field asymmetry is safe by construction.** Each tool is
bound to exactly one index and knows that index's vector field name
locally. There is no shared retriever, so no shared code can hide the
`content_vector` / `embedding` difference and fail silently on it.

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

### 8.1 The universal eight

Bound to every phase executor. Defined in `knowledge/tools.py`,
argument schemas in `knowledge/tool_args.py`.

| Tool | Purpose |
|---|---|
| `record_field(field_name, value)` | Writes a field to the phase artifacts |
| `rag_lookup_methodology(query, phase, top_k)` | `improve_knowledge_index` — methodology grounding |
| `rag_lookup_evidence(query, case_id, top_k)` | `improve_evidence_index` — this project's uploaded data |
| `rag_lookup_case_history(query, top_k, exclude_current_case)` | `improve_case_index` — yokoten, cross-case precedent |
| `propose_template(template_type, fill_data)` | Fill-in template for the team |
| `propose_diagram(diagram_type, data)` | Structured diagram JSON (not SVG) |
| `check_gate_status()` | Gate readiness — which required fields are populated |
| `request_human_approval(reason)` | Out-of-band interrupt |

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

18 tools, `knowledge/computation.py`. Each is a `@tool(args_schema=...)`
**pure function** — no LLM call, deterministic, unit-tested.

| Phase | Universal | Computation tools | Total |
|---|---|---|---|
| Define | 8 | `calculate_expected_savings` | **9** |
| Measure | 8 | `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean` | **16** |
| Analyse | 8 | `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression` | **13** |
| Improve | 8 | `calculate_doe_main_effects` | **9** |
| Control | 8 | `xbar_r_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk` | **12** |

**Why per-phase binding.** Tool selection quality degrades past roughly
10–15 tools per agent. Binding all 26 everywhere would make every coach
carry 26 options per turn, most irrelevant to its phase. Under
per-phase binding no phase exceeds 16; most sit at 9–13.

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

### 11.5 Conflict resolution panel
**New.** When §3.8 fires, the Belt sees the field name, the previously
approved value with its approval timestamp and gate, the proposed new
value, and the two options. Choosing "update" surfaces which downstream
phases become provisional **before** the Belt confirms.

### 11.6 Completeness and trace surfacing
`completeness_score` is surfaced visually at gate review. The LangSmith
run id is available for support escalation.

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
`request_id`, `project_id`, `phase`, `node_name`, `duration_ms`.

---

## 13. Phase Gate Requirements

| Phase | Required for gate |
|---|---|
| Define | problem statement, business case, project scope, team, goal statement |
| Measure | baseline mean, baseline sigma, measurement system validated, data collection plan |
| Analyse | root causes, root cause validation, causal hypothesis, ruled-out causes |
| Improve | solution selected, solution linked to root cause, pilot results, implementation plan |
| Control | control plan, sustainability check, post-improvement metric, handover documented |

**Three distinct things check these fields**, and conflating them is a
design error:

| Mechanism | Checks | Where |
|---|---|---|
| `PhaseInput` schema | Types and shape | `phases/{phase}/schema.py` |
| `DMAICGateValidator` | Presence and objective properties | Layer 2b |
| Phase rubric | Meaningful quality per criterion | Layer 2d |

A `root_cause_statement` reading "there are problems" satisfies the
schema and the presence check and fails the rubric. That gap is the
reason Layer 2d exists.

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
- **2.5.1** Upgrade `langgraph` 1.1.10 → **1.2.7**. Required for the
  subgraph `checkpoint_ns` fix (§3.1) **and** the native reliability
  primitives (§9.2). Both need ≥1.2.6.
- **2.5.2** Upgrade `langchain` → 1.3.11. Sweep for imports from
  `langgraph.prebuilt`; migrate to `langchain.agents`.
- **2.5.3** Repin adjacent packages after pip resolution.

### Step 3 — Tools and schemas
- **3.1** `knowledge/tool_args.py` — Pydantic arg schemas
- **3.2** `knowledge/fusion.py` — `reciprocal_rank_fusion`
- **3.3** `knowledge/tools.py` — the universal eight with multi-query + RRF
- **3.4** `knowledge/computation.py` — 18 computation tools, pure functions, unit tested
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
- **5.4** `middleware/state_injection.py` — `before_model` injection
- **5.5** Wire `SummarizationMiddleware`

### Step 6 — Phase subgraph migration (Define first)
- **6.1** Migrate Define: `nodes.py` (planner, executor, policy_advisory,
  revise), `gate.py` (gate_review_node, gate_apply_node), `graph.py`.
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
| Coach pattern | **`create_agent`** with four middlewares and a per-phase tool subset |
| Planner | Explicit node producing a structured plan; Level 1 planner is deterministic |
| Rubric grading | **Custom `DMAICGraderMiddleware`** on `create_agent`, not deepagents |
| HITL mechanism | **Graph-level `interrupt()`**, not `HumanInTheLoopMiddleware` |
| Gate flow | **Nine steps, two nodes, four validation layers** |
| Coherence and constraint checks | **Lightweight LLM**, not format checks |
| Mid-phase value conflicts | **Auto-flag, no threshold**, with re-approval cascade |
| Retrieval | **Three tools**, multi-query + RRF mandatory, metadata filters |
| `improve_case_index` | **Active** — yokoten via `rag_lookup_case_history` |
| Computation | **18 tools**, per-phase binding, pure functions |
| Context compression | `SummarizationMiddleware` + typed state fields |
| Compensation | **Native `error_handler=`**, no custom Saga framework |
| Fallback Level 3 | **Azure Cache for Redis** — new infrastructure |
| Deployment layer | **FastAPI** — LangGraph Server requires a commercial licence |
| Protocol layer | **None** — MCP architecturally excluded |
| Diagram generation | LLM emits JSON, frontend renders SVG from templates |
| Prompt management | Constants in `core/prompts.py` |

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

### 18.1 Amendment procedure

1. The decision is recorded in REFACTORING_AGENT_IMPROVE.md with its
   rationale
2. The rule lands in CLAUDE.md
3. The design lands here
4. Version number incremented, change log entry added
5. **If the change touches an index schema, §7 is updated in the same
   commit as the Azure AI Search change** (§7.7)

Architecture changes are separate commits from feature changes.
