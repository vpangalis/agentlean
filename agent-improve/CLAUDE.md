# Agent Improve — CLAUDE.md
# Version 2.2.10 — August 2026
# 2026 LangChain/LangGraph standards. Authoritative. Never bypass.

---

## 0. CONSTITUTION — Read Before Any Change

These rules are the constitution. Every Claude Code prompt must quote
the relevant rule numbers at the top of the prompt. If a rule blocks
a request, the rule wins. If a rule is wrong, propose an amendment
to this file FIRST in a separate commit — never violate it silently.

Violations of this constitution cost weeks of rework. We have proven
this twice with Agent Resolve and once with Agent Improve. There is
no third time.

### 0.1 — What v2.2 Is

v2.2 is a **ground-up rewrite**, not a patch. It aligns this file with
every decision ratified in the EDUCATIONAL.md architectural review.
The output of that review is `REFACTORING_AGENT_IMPROVE.md`, which is
the **rationale document**: when a rule here is unclear or looks wrong,
read the section it cites before proposing an amendment.

Division of responsibility across the three documents:

| Document | Answers |
|---|---|
| CLAUDE.md (this file) | **What the rule is.** Binding. Quoted in prompts. |
| ARCHITECTURE.md | **How the system is shaped.** Component design, sequencing. |
| REFACTORING_AGENT_IMPROVE.md | **Why the rule exists.** Evidence, alternatives, decisions. |

### 0.2 — Rule Numbers Are Load-Bearing

`.claude/config/deprecated_patterns.yaml` cites rule numbers in the
messages the drift hook feeds back to Claude. These citations must
resolve:

| Registry pattern | Cites |
|---|---|
| `pattern-2-with-structured-output` | §4.6 |
| `pattern-3-response-content-parsing` | §4.5 |
| `pattern-4-custom-saga` | §3.6 |
| `pattern-8-bind-tools-in-phase-executor` | §4.4 |

**Renumbering any of these rules requires updating the registry in the
same commit.** A hook that cites a non-existent rule is worse than no
hook — see REFACTORING_AGENT_IMPROVE.md §86.

### 0.3 — What Changed From v2.1

| Area | v2.1 | v2.2 |
|---|---|---|
| Gate approval | Interrupt → approve | **Nine-step HITL** (§9.1) |
| Gate validation | Field presence | **Four-layer stack** (§9.2) |
| Retrieval tools | 2 (`search_methodology`, `search_evidence`) | **3 `rag_lookup_*`** (§7.2) |
| Tool binding | 7 universal tools, same for all phases | **7 universal + 18 per-phase computation** (§5) |
| Coach construction | `bind_tools` on the coach LLM | **`create_agent` + five middlewares** (§4.4, §8) |
| Structured output | `with_structured_output` mandated everywhere | **Scoped by call type** (§4.6) |
| Cross-phase data | Parent state | **Store** (§10.2) |
| Persistence | Azure Blob only | **Phased Blob → PostgreSQL** (§1.7) |
| MCP | In the stack description | **Architecturally excluded** (§1.9) |
| Index schemas | Partial, in prose | **Canonical in ARCHITECTURE.md §7**; rule-bearing facts in §7.3 |

### 0.4 — What Changed in 2.2.9 — the state design closed

All 15 findings from the state design audit landed in one commit. The
rules that bind, and where they live:

| Area | v2.2.8 | v2.2.9 |
|---|---|---|
| Identifier | `project_id` in docs, `case_id` in code | **`case_id` everywhere** (§10.5) |
| Name for captured fields | `artifacts` / `captured_fields` / `phase_inputs` | **`artifacts` only** (§10.5) |
| `SupervisorState` | 7 fields, `gate_passed: list[str]` | 7 fields, **`gate_passed: dict[str, bool]`**, `final_output: Optional[dict]` (§10.1) |
| `PhaseState` | 11 fields, `feedback`, `final: str` | **15 fields** — adds `gate_attempts`, `validator_feedback`, `citations`, `uploads`; `feedback` → **`belt_edits`**; `final: dict` (§10.1) |
| `coaching_plan` | `list[dict]` in some places | **single `dict`**, transient (§10.1) |
| Gate document write | Unspecified | **`gate_apply_node` writes store + `PhaseState.final`** (§9.6) |
| Captured field typing | Prose promised typed floats | **All `str`**, three cross-phase reference dicts excepted (§10.6) |
| Computation results | Nowhere | **`artifacts["computation_results"]`** (§10.6) |
| Gate-required fields | One flat list, contradicting the rubric | **Two tiers**; grader verdict gains `"warning"` (§9.7) |

### 0.5 — What Changed in 2.2.10 — the executor contract closed

| Area | v2.2.9 | v2.2.10 |
|---|---|---|
| Subgraph nodes | `policy_advisory`, `revise` | **`validation_stack`, `gate_apply`** (§3.3) |
| Validation stack | Listed as an executor tool | **A node**, reached by an edge (§3.3) |
| Policy advisory | Listed as an executor tool | **Logic inside `gate_apply`** (§3.3) |
| Graders | One, conflated | **Two** — `COACHING_QUALITY_RUBRIC` every turn, `PHASE_RUBRIC` at the gate (§8.2) |
| Middleware | Four | **Five** — `ModelRetryMiddleware` added (§8.7) |
| Middleware order | State injection last | **State injection first** (§8.1) |
| Executor `response_format` | `ProviderStrategy(PhaseOutput)` | **`CoachingResponse`** (§4.6, §10.7) |
| Field capture | `record_field` tool | **`CoachingResponse.fields_captured`** (§5.1) |
| Universal tools | 8 | **7** (§5.1) |
| Per-phase totals | 9 / 16 / 13 / 9 / 12 | **8 / 15 / 12 / 8 / 11** (§5.2) |
| Gate document schemas | Undefined, or two conflicting | **Five canonical `{Phase}Output`** (§10.7) |

---

## 1. ARCHITECTURE PRINCIPLES

### 1.1 — One State Per Level, One Runtime, One Source of Truth

- **One state per level.** Two state schemas, and only two:
  - `SupervisorState` — parent orchestration state (§10.1)
  - `PhaseState` — per-phase subgraph state (§10.1)

  No parallel state in routes, no per-request manual dicts, no shadow
  state in the UI. `SupervisorState` holds orchestration **only** —
  it does not hold captured fields or gate documents.

- **One runtime.** The compiled LangGraph supervisor is the
  orchestrator. Nothing in `gateway/routes.py` may dispatch nodes
  manually. If a route does anything beyond `await graph.ainvoke(...)`
  (or `astream_events(...)`) plus envelope marshalling, it is a
  violation.

- **Two persistence systems, not one.** The checkpointer and the store
  are distinct LangGraph primitives serving different lifecycles
  (§1.7, §10). Passing only a checkpointer is the most common
  architecture mistake.

*Rationale: REFACTORING_AGENT_IMPROVE.md §17, §18, §52.*

### 1.2 — Hierarchical Subgraphs, One Thread, Auto Namespacing

```
supervisor_graph                    thread_id = case_id, e.g. "IMPR-2026-FS1"
├── define_subgraph                 checkpoint_ns auto-managed by LangGraph
├── measure_subgraph
├── analyse_subgraph
├── improve_subgraph
├── control_subgraph
└── escalation_subgraph
```

**Binding rules:**

- **One `thread_id` per project.** Never per phase, never concatenated
  (`{case_id}-define` and similar are BANNED).
- **The checkpointer and store go on the parent graph ONLY.** Phase
  subgraphs compile without either. LangGraph routes their writes
  through the parent's saver, distinguished by an auto-managed
  `checkpoint_ns`.
- **Phase transitions use static edges**, not a routing LLM and not
  `Command`. DMAIC order is fixed:
  `define → measure → analyse → improve → control → END`.
- **`Command` routing is for inside phase subgraphs only**, where step
  order is genuinely data-dependent.
- **Never mix static edges and `Command` from the same node.** Both
  paths execute, silently.
- **No subgraph imports from another subgraph's nodes.**
- **Cross-phase data flows through the store, never through parent
  state** (§10.2). Subgraph state updates are not guaranteed to
  propagate to the parent immediately — this is documented LangGraph
  behaviour, and the store is the documented fix.

*Rationale: REFACTORING_AGENT_IMPROVE.md §19, §23, §44, §52a.*

### 1.3 — Tool-Calling Coach, Explicit Planner

Each phase subgraph contains a **Planner-Executor pair** (§3.3), not a
single coaching node:

- **`phase_planner`** produces a structured plan — which field to
  focus on, which action to take, which retrieval strategy to use.
  Never dispatches directly to tools.
- **`phase_executor`** consumes that plan and dispatches to leaf
  tools. Never decides strategy.

The Planner and Executor are distinct nodes and are **never fused**.
Fusing them loses the boundary that makes coaching inspectable and
costs the ability to test either half.

Extraction is structured output on the executor
(`response_format=CoachingResponse`, §4.6), not a separate node and no
longer a tool call.

**Level 1 (supervisor) has no LLM planner.** Phase sequencing is a
deterministic gate-check on `gate_passed` plus static edges. There
is nothing to reason about, so nothing reasons.

*Rationale: REFACTORING_AGENT_IMPROVE.md §5, §11, §20, §23, plus the
Terminology Reference.*

### 1.4 — Async by Default

- All FastAPI endpoints are `async def`
- All graph invocations use `await graph.ainvoke(...)` or
  `graph.astream_events(...)`
- All LLM calls use `await llm.ainvoke(...)`
- All Azure SDK calls use the `aio` variants where available

Synchronous code is permitted only in pure functions with no I/O
(prompt building, state transformations, validation logic, all 18
computation tools).

**Per-node timeouts require async nodes** (§3.6) — this is a hard
LangGraph constraint, not a preference.

### 1.5 — Streaming Responses

Coach responses stream to the UI via Server-Sent Events on
`/ask/stream`. The frontend renders tokens as they arrive. The
non-streaming `/ask` endpoint remains for clients that cannot use
SSE but is not used by the standard UI.

### 1.6 — Interrupt-Based Gates — Nine Steps, Two Nodes

Gate approval is a nine-step sequence with two distinct quality
checks in it, implemented across two nodes. The full sequence is
§9.1; the binding structural rules are:

- The interrupt fires in `gate_review_node`, which presents validated
  fields and stops.
- The Belt's response is processed by `gate_apply_node`, which applies
  corrections, runs the policy advisory, and routes onward.
- **The checkpoint commits only after Belt approval.** Never before.
- **Use graph-level `interrupt()` + `Command(resume=...)`.**
  `HumanInTheLoopMiddleware` is BANNED for gates (§8.6).

*Rationale: REFACTORING_AGENT_IMPROVE.md §2, §44, §53.*

### 1.7 — Phased Persistence — Blob Now, PostgreSQL Before Production

| Stage | Checkpointer | Store |
|---|---|---|
| During the refactor | `AzureBlobCheckpointSaver` | `AzureBlobStore` |
| Post-refactor, pre-production | `PostgresSaver` | `PostgresStore` |

**`InMemorySaver` is not used at any stage**, including development.

`AzureBlobCheckpointSaver` lives at `core/checkpointer.py` and
implements `BaseCheckpointSaver`. `AzureBlobStore` lives at
`core/store.py` and implements `BaseStore`.

**Blob layout for checkpoints:**
```
checkpoints/{case_id}/
  latest.json                    — most recent checkpoint (fast resume)
  history/{checkpoint_id}.json   — historical checkpoints for time-travel
```

**Critical constraints:**
- One blob write per checkpoint (no per-key writes)
- Atomic via blob ETag conditional writes to handle concurrent turns
- `gate_attempts` MUST be in the checkpointed state, never in route
  scope — this is what fixes the v1 "attempts always reset to 0" bug.
  It lives on `PhaseState` (§10.1), per phase, because each phase runs
  its own validation loop with its own cap

**Migration is a constructor and connection-string change.** Both
sides of the split are defined by LangGraph interfaces, so nothing
above the persistence layer changes. Provision Azure Database for
PostgreSQL (flexible server) when the trigger fires; run the existing
unit tests against PostgreSQL before switching.

**Known limitation of the Blob implementation:** it was not tested
for concurrent access, and Azure Blob has no row-level locking. This
is acceptable for single-developer refactoring and is not acceptable
for production. Do not defend it past the migration trigger.

*Rationale: REFACTORING_AGENT_IMPROVE.md §1, §52a, §87 item 13.*

### 1.8 — LangSmith Tracing Mandatory

- `LANGCHAIN_TRACING_V2=true` is required in all environments
- Every LLM call must be traced
- Every tool call must be traced
- Every graph node must be a traceable span
- **Every custom validation function carries `@traceable`** (§11.2)
- Token cost and latency are logged per node

Dead tracing config (the v1 state) is a CRITICAL violation.

### 1.9 — No MCP. Uploaded Data Is the Only External Channel

**Agent Improve, Agent Resolve, and Agent Flow will never use MCP to
connect to a live system.** This is an architectural exclusion, not a
deferral. There is no promotion trigger.

**The runtime stack is:** FastAPI, LangGraph 1.2.10+, LangChain 1.x,
Azure OpenAI, Azure AI Search, Azure Blob Storage, Azure Cache for
Redis. No MCP.

**The data architecture principle this establishes:**

> `improve_evidence_index` is not merely "case-specific uploaded
> documents." It is the **only** channel through which external,
> real-world data enters AgentLean.

Three consequences that bind on implementation:

1. Coaching content must include guidance on **what data to upload and
   how to structure it**. Data-collection coaching is a first-class
   part of the methodology, not a workaround.
2. Belt data-collection discipline is what the platform's grounding
   depends on.
3. **There is no fallback path where the system fetches a number the
   Belt failed to provide.** Do not build one.

**Cross-agent tool sharing** (Agent Improve reading Agent Resolve's
indexes) happens via Python imports from shared modules, not via a
protocol. Those remain `@tool` functions, read-only.

*Rationale: REFACTORING_AGENT_IMPROVE.md §39, §60, §63.*

---

## 2. WHERE CLASSES ARE ALLOWED

Classes are permitted ONLY in these files.

### State and schemas
- `core/state.py` — `SupervisorState` (TypedDict) — ONE only
- `core/substate.py` — `PhaseState` and per-phase variants
- `phases/{phase}/schema.py` — `PhaseInput` and nested models (Pydantic v2)
- `storage/models.py` — `CaseDocument`, `PhaseRecord`, `RegistryEntry`
- `gateway/schemas.py` — API request/response envelopes (Pydantic v2)
- `core/citations.py` — `CitationRecord`, `CitationBundle`

### Tool and validation schemas
- `knowledge/tool_args.py` — Pydantic schemas for `@tool` `args_schema=`
- `validation/schemas.py` — `CriterionVerdict`, `GraderVerdict`,
  `ConstraintVerdict`, `ConstraintCheckResult`
- `core/errors.py` — `AgentImproveError` (§12.3)

### Persistence
- `core/checkpointer.py` — `AzureBlobCheckpointSaver(BaseCheckpointSaver)`
- `core/store.py` — `AzureBlobStore(BaseStore)`

### Middleware
- `middleware/grader.py` — `DMAICGraderMiddleware(AgentMiddleware)`
- `middleware/skills.py` — `DMAICSkillsMiddleware(AgentMiddleware)`
- `middleware/state_injection.py` — `before_model` injection middleware

### Reliability
- `core/reliability.py` — `CircuitBreaker`

All other files contain module-level functions ONLY. Especially:
- Graph builder files (`core/graph.py`, `phases/{phase}/graph.py`)
- LLM factory (`core/llm.py`)
- All node files (`phases/{phase}/nodes.py`)
- Blob client (`storage/blob.py`)
- Retriever (`knowledge/retriever.py`)
- Tool definitions (`knowledge/tools.py`, `knowledge/computation.py`)
- Boundary mappers (`phases/{phase}/mappers.py`)
- Escalation (`escalate.py`)
- Routes (`gateway/routes.py`)

**`DMAICGateValidator` is the one permitted exception to "no classes
elsewhere":** it lives in `validation/gate_validator.py` as a
namespace of `@staticmethod` deterministic checks, holding no state.

---

## 3. GRAPH AND NODE RULES

### 3.1 — Graph structure

- One supervisor graph in `core/graph.py`
- One subgraph per phase in `phases/{phase}/graph.py`
- One escalation subgraph in `escalate.py`
- The supervisor compiles all subgraphs into a hierarchical compiled graph
- The compiled graph is the ONLY runtime path. `/ask`, `/ask/stream`,
  and `/gate/*` all invoke the same compiled graph object.
- **Entry is declared with `add_edge(START, ...)`.** The
  `set_entry_point` form is superseded.

The phase subgraph builder takes the phase as a parameter, because it
must select that phase's computation-tool subset (§5.2):

```python
def build_phase_subgraph(phase: str, llm):
    tools = UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    ...
    return builder.compile()          # NO checkpointer, NO store
```

### 3.2 — Node contract

Nodes are module-level async functions:

```python
async def phase_executor(state: PhaseState) -> dict:
    ...
    return {"draft": {...}, "step_log": [{...}]}
```

- File name and function name are aligned (one file per subgraph may
  contain multiple nodes)
- Nodes return `dict` slices only — never Pydantic, never full state
- Nodes are async (no sync nodes — §1.4)
- **Plans and drafts crossing nodes are structured**, never prose
  parsed downstream (§4.6)

### 3.3 — Per-phase subgraph nodes (the canonical structure)

Each phase subgraph contains exactly these nodes:

```
planner            — structured plan: focus_field, next_action,
                     retrieval_strategy, tools_needed
executor           — create_agent with the phase's tool subset
validation_stack   — the four layers (§9.2), shared cap of 3
gate_review        — interrupt() — presents validated fields, stops
gate_apply         — policy advisory, applies corrections, assembles
                     and writes the gate document (§9.6), routes on
```

**Five nodes. `policy_advisory` and `revise` are BANNED as node
names.** Both appeared in earlier revisions:

| Retired | Ratified | Why |
|---|---|---|
| `policy_advisory` | `validation_stack` | The four-layer stack was missing from the node list entirely. The policy advisory is logic inside `gate_apply`, not a node |
| `revise` | `gate_apply` | Revision is an **edge** — the validation stack routes back to the planner with `validator_feedback`. `gate_apply` does advisory + approval + store write |

**The subgraph is a cycle, not a pipeline.** The planner fires many
times per phase, not once: after each executor step, control returns
to the planner to decide whether to continue on the current field,
advance to the next, or trigger the gate.

**Leaf tools are NOT subgraph nodes.** The universal seven (§5.1) and
the phase's computation tools are passed to the executor via `tools=`
on `create_agent`. From the subgraph's perspective the executor is one
node.

**The validation stack and the policy advisory are NOT tools, and
adding either to a tool list is a violation.**

| Component | What it is |
|---|---|
| Validation stack | A **node**, reached by an edge after the executor finishes. As a tool, the coach would decide whether to be validated — backwards |
| Policy advisory | **Logic inside `gate_apply`**. It runs after the Belt edits, when the coach is no longer in the loop |

NEW node types may not be added to a subgraph without an
ARCHITECTURE.md amendment.

### 3.4 — Reflection is a node, not a private function

`_reflect()` inside orchestrate files (the v1 pattern) is BANNED.

Reflection is a graph node reached via a conditional edge. The edge
decides whether reflection is needed based on response length, risk
keywords (numbers, commitments, dates), and phase-specific rules.

For **invisible** retry — mechanical, not a coaching event — use
`RetryMiddleware` rather than a reflection node.

### 3.5 — Escalation lives and runs

`escalate.py` defines the escalation subgraph. It is reachable via
conditional edge when the validation stack exhausts its shared cap of
3 attempts (§9.2), and via the `request_human_approval` tool.

`gate_attempts` is persisted in the checkpointed state, never in route
scope.

### 3.6 — Reliability primitives are native, not hand-written

**Custom Saga orchestrators and hand-written compensating-action
frameworks are BANNED.** LangGraph 1.2 provides the mechanism.

**Per-node timeouts — required on every phase executor node:**

```python
builder.add_node(
    "phase_executor",
    phase_executor_fn,
    timeout=TimeoutPolicy(run_timeout=45),
    error_handler=phase_error_recovery,
)
```

`run_timeout=45` is the wall-clock limit. `NodeTimeoutError` triggers
the fallback chain (§4.8) before the Belt notices the delay.

**Node-level error handlers — required on every node with external
writes.** Every node that writes to Azure Blob, `improve_case_index`,
or `improve_evidence_index` gets an `error_handler=` that undoes the
external write and routes to a degraded response:

```python
def phase_error_recovery(error: NodeError, state: PhaseState) -> Command:
    delete_or_flag_stale_in_case_index(state["case_id"], state["phase"])
    return Command(
        update={"extraction_error": str(error), "extraction_incomplete": True},
        goto="degraded_coaching_response",
    )
```

**Two dependencies on this rule, both correctness-critical:**
- **Gate reopening** (§9.5) — when the re-approval cascade fires, the
  affected phase's handler must run, or state and index disagree
  silently.
- **Time-travel debugging** — resuming from an earlier checkpoint
  rolls back state, **not** external writes. Time travel is only
  correct for nodes that have a handler.

**Graceful shutdown:** use `RunControl.request_drain()` for deployment
rollouts. Mid-coaching sessions save their checkpoint and resume.

**`DeltaChannel` is NOT used.** Beta API; deferred until sessions
exceed ~200 turns.

*Rationale: REFACTORING_AGENT_IMPROVE.md §3, §49, §79.*

### 3.7 — Multi-hop is capped at five tool calls per Belt turn

LangGraph counts steps, not hops. Each hop is two steps (LLM node →
tool node) plus one final synthesis step:

```
recursion_limit = 2 * max_hops + 1 = 11
```

```python
await graph.ainvoke(
    state,
    config={"recursion_limit": 11,
            "configurable": {"thread_id": case_id}},
)
```

**`GraphRecursionError` MUST be caught in the coach node** and turned
into a partial answer for the Belt. A Belt mid-session never sees a
stack trace because the coach explored too broadly.

Hitting the cap is a **monitoring signal**, not just a limit — it
means either the system prompt encourages too-broad exploration, or
the question warrants `operational-premium` for that turn.

*Rationale: REFACTORING_AGENT_IMPROVE.md §34, §71.*

---

## 4. LLM RULES

### 4.1 — Factory only

Never instantiate `AzureChatOpenAI` directly. Always use:

```python
from core.llm import get_llm
llm = get_llm("coach", max_tokens=1500)
```

### 4.2 — Roles

Defined in `core/llm.py`. Two deployment tiers, addressed by role:

| Role | Deployment | Purpose |
|---|---|---|
| `coach` | `operational-premium` (gpt-4o) | Coaching content, max_tokens=1500 |
| `planner` | `operational-premium` (gpt-4o) | Phase planner structured decisions |
| `synthesis` | `operational-premium` (gpt-4o) | Final multi-hop synthesis |
| `reasoning` | `operational-model` (gpt-4o-mini) | Default reasoning, intermediate hops |
| `extraction` | `operational-model` (gpt-4o-mini) | Field extraction |
| `coherence` | `operational-model` (gpt-4o-mini) | Layer 1 coherence check (§9.2) |
| `constraint` | `operational-model` (gpt-4o-mini) | Layer 3 constraint check (§9.2) |
| `grader` | `operational-model` (gpt-4o-mini) | Layer 4 rubric grading (§8.2) |
| `summarizer` | `operational-model` (gpt-4o-mini) | Context compression (§8.4) |
| `intent` | `operational-model` (gpt-4o-mini) | Short classification |
| `vision` | `operational-premium` (gpt-4o) | Multimodal upload analysis |

**Model tiering is a cost rule, not a style preference.** Intermediate
multi-hop retrieval runs on `operational-model`; only final synthesis
runs on `operational-premium`. gpt-4o-mini is roughly 15× cheaper.

New roles require an ARCHITECTURE.md amendment.

### 4.3 — Never parse JSON from raw LLM text

Structured output is the only path from a model to a typed value. The
mechanism is §4.6; this rule is the prohibition.

### 4.4 — Agent construction — `create_agent`, with middleware

**Phase executors are built with `create_agent`.** Binding tools
directly onto a bare LLM inside a phase executor is a violation: it
bypasses the middleware stack (§8), which carries grading, skills,
compression, and state injection.

```python
executor = create_agent(
    model=get_llm("coach"),
    tools=UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase],
    response_format=ProviderStrategy(PhaseOutput),
    middleware=[...],                       # §8.1 — all four, in order
    prompt=PHASE_COACH_PROMPT[phase],
)
```

**`create_react_agent` is superseded** by `create_agent` from
`langchain.agents`. Nothing may import it, and nothing may import from
the `langgraph.prebuilt` namespace.

**deepagents is NOT a dependency.** `create_deep_agent`,
`RubricMiddleware`, and `SkillsMiddleware` from that package are all
BANNED while it remains pre-1.0. Our equivalents are custom middleware
on `create_agent` (§8.2, §8.3). Revisit at deepagents 1.0; migrate all
three custom middlewares together or not at all.

*Rationale: REFACTORING_AGENT_IMPROVE.md §42, §50, §84.*

### 4.5 — Read typed content blocks, never string-index the content

Model responses carry typed content blocks. Read
`response.content_blocks`. String-indexing or substring-parsing the
raw content field is a violation — it breaks the moment a provider
returns a multi-part response.

*Rationale: REFACTORING_AGENT_IMPROVE.md §81.*

### 4.6 — Structured output — scoped by call type

**This rule replaces v2.1 §4.3, which mandated one mechanism
everywhere. There are two mechanisms, and the choice is determined by
what is being called — not by preference.**

| The call is… | Use | Example |
|---|---|---|
| An agent built with `create_agent` | `response_format=Schema` (ProviderStrategy auto-selected) | Phase executor → `CoachingResponse` |
| A plain model invocation inside a tool, middleware, or validator | The builder-style structured-output call on the model | Query variants, grader verdict, constraint verdict |
| Assembling a gate document from already-captured fields | **No LLM call** — Pydantic construction | `DefineOutput(**artifacts)` at `gate_apply` |

**Why the first two exist separately:** `response_format=` attaches to
an agent's model-tools loop. A tool generating query variants, a
middleware grading a transcript, and a validator returning
per-constraint verdicts are not agents — there is no loop to attach to.

Prefer `ProviderStrategy` over `ToolStrategy` where the provider
supports native JSON mode. LangChain 1.2 can infer the choice from the
model profile.

**Complete mapping — every structured output in the system:**

| Component | Built with | Schema | Mechanism |
|---|---|---|---|
| Phase planner | Plain LLM call | `CoachingPlan` | `with_structured_output` |
| **Phase executor (coach)** | **`create_agent` + tools** | **`CoachingResponse`** | **`response_format=`** |
| Validation Layer 2a (coherence) | Plain LLM call | `CoherenceResult` | `with_structured_output` |
| Validation Layer 2c (constraints) | Plain LLM call | `ConstraintCheckResult` | `with_structured_output` |
| Validation Layer 2d (gate grader) | Plain LLM call | `GraderVerdict` | `with_structured_output` |
| `gate_review` | **No LLM** | Interrupt payload | `interrupt()` |
| `gate_apply` — policy advisory | Plain LLM call | `PolicyAdvisoryResult` | `with_structured_output` |
| `DMAICGraderMiddleware` | Plain LLM call in middleware | `CoachingGraderVerdict` | `with_structured_output` |
| Inside `rag_lookup_*` | Plain LLM call | `QueryVariants` | `with_structured_output` |
| Gate document assembly | **No LLM** | `DefineOutput` … `ControlOutput` | `Schema(**artifacts)` |

**The executor's `response_format` is `CoachingResponse`, never a phase
Output schema.** The executor runs once per coaching turn; the gate
document is assembled once per phase. Asking the coach to emit a
complete `DefineOutput` every turn requests fields it has not yet
coached. See §10.7.

**The structured response and the coaching text coexist.** The agent
still calls tools normally through the ReAct loop and still writes
coaching prose into `messages`; only the terminal response is
additionally structured, and it arrives in `result["structured_response"]`.
Reading one does not cost you the other.

**What structured output does NOT give you:** truth. It guarantees
shape. A schema-valid `baseline_metric: 4.2` invented by the model is
exactly as well-formed as a correct one. Content-level defence is
§6.4, §9.2 Layer 1, and §9.4 — not this rule.

*Rationale: REFACTORING_AGENT_IMPROVE.md §29, §82, §86.*

### 4.7 — Temperature discipline

| Component | Temperature | Why |
|---|---|---|
| Coach responses | 0.5–0.7 | Natural variation improves the Belt's experience |
| Grader (§8.2) | 0.1 | Same gate document must get the same verdict across runs |
| Coherence check (Layer 1) | 0.1 | Consistent verdicts |
| Constraint check (Layer 3) | 0.1 | Consistent verdicts |
| Extraction, field validators | 0.0–0.2 | Same rationale |

**The grader's temperature is a hard requirement, not a tuning knob.**
A grader that returns different verdicts across runs makes the
regression thresholds in §12 meaningless.

### 4.8 — Fallback chain and circuit breakers

**Four levels, always terminating in success:**

```
Level 0: TimeoutPolicy(run_timeout=45)         — fires first (§3.6)
Level 1: gpt-4o    (operational-premium)       exponential backoff
Level 2: gpt-4o-mini (operational-model)       exponential backoff
Level 3: Azure Cache for Redis, session-scoped jittered backoff
Level 4: Degraded mode — never a hard failure to the Belt
```

**Backoff rule:** exponential for managed services (Azure OpenAI, which
rate-limits predictably); jittered for shared resources (the cache,
which several subagents may hit simultaneously).

**Circuit breakers — three-state, two instances:**

| Breaker | Wraps | On OPEN |
|---|---|---|
| LLM | Azure OpenAI calls | Coaching turn cannot happen — fall to Level 2, then degraded |
| Search | Azure AI Search calls | Coaching **continues** without RAG grounding — quality degradation, not availability failure |

Threshold 3 failures in 30s trips open; 60s reset timeout; one probe
request in HALF-OPEN before resuming. **Two-state (CLOSED/OPEN)
breakers are not permitted** — this is a long-running service and must
recover without a restart.

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

**HTTP 400 (token limit exceeded) is NOT a fallback case.** It is a
context-management failure — do not retry the same request against a
smaller model. Fix the context (§8.4).

**Every attempt is logged to `step_log` as a dict** (§10.3).

*Rationale: REFACTORING_AGENT_IMPROVE.md §64, §66, §67.*

---

## 5. TOOLS

Defined in `knowledge/tools.py` (universal) and
`knowledge/computation.py` (per-phase), with Pydantic arg schemas in
`knowledge/tool_args.py`.

### 5.1 — The universal seven

Passed to every phase executor via `tools=`:

```
rag_lookup_methodology(query: str, phase: str, top_k: int = 10) -> list[Document]
  improve_knowledge_index. Multi-query + RRF. Filters phase_relevance.

rag_lookup_evidence(query: str, case_id: str, top_k: int = 10) -> list[Document]
  improve_evidence_index. Multi-query + RRF. Filters case_id.

rag_lookup_case_history(query: str, top_k: int = 10,
                        exclude_current_case: bool = True) -> list[Document]
  improve_case_index. Multi-query + RRF. Yokoten — cross-case learning.

propose_template(template_type: str, fill_data: dict) -> str
  Fill-in template for the team. Types: problem_statement, sipoc,
  data_collection_plan, fishbone, etc.

propose_diagram(diagram_type: str, data: dict) -> dict
  Structured diagram JSON (NOT SVG). Types and schemas in
  core/diagrams.py. Frontend renders via SVG template library.

check_gate_status() -> dict
  Current phase gate readiness — which required fields are populated,
  which are missing.

request_human_approval(reason: str) -> str
  Triggers an interrupt awaiting human decision, beyond standard gate
  submission.
```

`search_methodology` and `search_evidence` are **renamed and
superseded**. No code may reference the old names.

**`record_field` is RETIRED and may not be reintroduced.** Field capture
happens through `response_format=CoachingResponse` on the executor
(§4.6) — the coach emits `fields_captured` as structured output on every
turn, and the executor node writes each entry to `artifacts`. A tool
would make capture a decision the coach might skip; structured output
makes it part of every response by construction.

### 5.2 — Per-phase tool binding

**Tool sets are per phase, not universal.** Tool selection quality
degrades past roughly 10–15 tools per agent; per-phase binding keeps
every coach inside the tractable range.

| Phase | Universal | Computation tools | Total |
|---|---|---|---|
| Define | 7 | `calculate_expected_savings` | **8** |
| Measure | 7 | `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean` | **15** |
| Analyse | 7 | `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression` | **12** |
| Improve | 7 | `calculate_doe_main_effects` | **8** |
| Control | 7 | `xbar_r_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk` | **11** |

**No phase exceeds 16 tools**, and after `record_field` was retired the
actual maximum is 15 (Measure). If a new tool would push a phase past
16, that is an ARCHITECTURE.md amendment, not a routine addition.

**Each of the 18 computation tools is a separate named tool.**
Parameterised grouping (one `calculate_sample_size(type, ...)` with a
mode argument) is BANNED — it moves the selection burden into the
argument space, and models handle distinct named tools more reliably
than mode arguments.

**All 18 are pure functions.** No LLM call, deterministic, unit-tested.

Tool decisions are the LLM's, not the graph's.

### 5.3 — Tool args via Pydantic schemas

Every `@tool` uses `args_schema=` with a Pydantic model from
`knowledge/tool_args.py`. No tools with raw signature inference.

### 5.4 — Docstrings are load-bearing

The tool docstring is how the model chooses between the three
retrieval tools. It is interface, not commentary.

Every retrieval tool docstring MUST state:
- **When to use it** — "I need methodology" vs "I need this project's
  data" vs "I need precedent from other projects"
- **Which index** it queries
- **Which vector field** it uses (`content_vector` or `embedding`)
- **Which filters** are applied

`rag_lookup_case_history`'s docstring must additionally carry the
multi-tenancy note for future engineers: if Agent Improve ever serves
multiple organisations, this tool must filter by tenant.

*Rationale: REFACTORING_AGENT_IMPROVE.md §32, §39, §60.*

---

## 6. PROMPTS

### 6.1 — Constants in `core/prompts.py`

All prompts live as constants in `core/prompts.py`. Prompt strings are
never inline in node files.

### 6.2 — Prompt naming

- `{PHASE}_COACH_PROMPT` — phase executor system prompt
- `{PHASE}_PLANNER_PROMPT` — phase planner prompt
- `{PHASE}_RUBRIC` — grader rubric constant (§8.2)
- `{PHASE}_CONSTRAINTS` — constraint set (§9.2)

The v1 `ORCHESTRATOR_{PHASE}_CONTEXT` and `EXTRACTION_{PHASE}`
patterns are deleted. Extraction is a tool call.

**`KNOWLEDGE_INJECTION_TEMPLATE` is deleted.** RAG results arrive as
tool results, not as a prepended system message (§7.1).

### 6.3 — The memory hierarchy paragraph is mandatory

Every coach system prompt carries an explicit source hierarchy. This
is the ratified mechanism for memory prioritisation — **prompt-level
priority, not per-chunk metadata scoring**:

```
MEMORY HIERARCHY — when sources disagree, weight them in this order:
  1. LSS Black Belt methodology (rag_lookup_methodology) — authoritative
  2. This project's confirmed captured fields — the Belt's own approved facts
  3. Past case history (rag_lookup_case_history) — patterns, not prescriptions
  4. Recent conversation — context, not evidence
Never present case history as methodology. Never let a recent remark
override a gate-approved value without flagging it.
```

### 6.4 — Anti-hallucination guards are mandatory

Every coach and extraction prompt carries explicit anti-hallucination
guards. **The LLM must never invent field values from coaching
templates.** A template showing `baseline_mean: 4.2` as an example is
not data.

Structured output does not satisfy this rule (§4.6). Content-level
defence requires all three of:
1. Explicit prompt guards
2. Cross-checking extracted values against the raw conversation
3. The policy advisory reviewing extracted values before Belt approval

*Rationale: REFACTORING_AGENT_IMPROVE.md §29, §38, §40.*

---

## 7. RAG AND INDEXES

### 7.1 — RAG via tool, never via prepended system message

The v1 pattern (`build_knowledge_context()` injected as a
SystemMessage) is DELETED. Retrieval is a tool call the model decides
to make.

This makes RAG accountable in the trace, lets the model control when
to retrieve, and removes the always-on retrieval cost.

**There is no unconditional retrieval pipeline.** If you find one,
it is a violation.

### 7.2 — Three retrieval tools, one index each

| Tool | Index | Filter | Ordering | Vector field |
|---|---|---|---|---|
| `rag_lookup_methodology` | `improve_knowledge_index` | `phase_relevance eq '{phase}' or phase_relevance eq 'general'` | — | `content_vector` |
| `rag_lookup_evidence` | `improve_evidence_index` | `case_id` | — *(no ordering — see below)* | `content_vector` |
| `rag_lookup_case_history` | `improve_case_index` | `status eq 'completed'` | `created_at desc` | `embedding` |

**Each tool is bound to exactly one index and knows that index's
vector field name locally.** There is no shared retriever. This is why
the `content_vector` / `embedding` asymmetry is safe: no shared code
can hide it, so nothing can fail silently on it.

**`belt_level` filtering is OFF by default** on case history —
over-narrowing risk, since a Green Belt often benefits from Black Belt
cases. Available as an optional parameter.

`source_file` and `page_number` are **returned as metadata for
citation transparency**, never used as filters.

**The methodology filter field is `phase_relevance`, and its cross-phase
value is `general` — never `phase`, never `all`.** Both were wrong in
earlier revisions; `phase` does not exist on the index (Azure rejects the
whole query) and no document carries `all` (218 carry `general`). One
fails loudly, the other silently returns a narrowed corpus.

**A metadata key becomes a filterable field only if it is named after one
AND the vectorstore declares it.** LangChain's `AzureSearch` promotes a
metadata key to a top-level field only when the key matches a name in
`self.fields` — and `self.fields` defaults to
`[id, content, content_vector, metadata]`, never the live schema. So
writing methodology requires both the correct key name *and*
`fields=KNOWLEDGE_INDEX_FIELDS` on the vectorstore. Either alone leaves
the value buried in the `metadata` JSON blob, unreachable by `$filter`,
with no error raised. This is how `phase_relevance` went unpopulated.
`ingest_knowledge.py` owns this contract; full detail in
ARCHITECTURE.md §7.1.2.

**Retrieval failure is never an empty result.** All three retrieval
functions — `search_knowledge`, `search_cases`, `search_evidence` — return
`[]` only when the search ran and matched nothing; when they fail they
raise `KnowledgeSearchError`. **Never wrap a retrieval call in a bare
`except Exception` that returns `[]`** — that is what hid the `phase`
filter bug, by reporting a broken index as a silent corpus. Catch
`retriever.RETRIEVAL_EXCEPTIONS` and classify via `_fail()`.

Three rules that fall out of it, each of which has already bitten:
- **`RETRIEVAL_EXCEPTIONS` spans two services.** Azure AI Search *and* the
  Azure OpenAI query embedding, which runs inside the same `try`.
- **A 4xx is `permanent` / `do_not_retry`**, not transient — it is our
  malformed query, and retrying fails identically.
- **Materialise results inside the `try`** — `SearchClient.search()` is
  lazy and the HTTP call fires on iteration.

Full rationale: ARCHITECTURE.md §7.1.1.

**`rag_lookup_evidence` takes no `order_by` argument.** Verified
against the live index (Aug 2026): `improve_evidence_index` has **no
`uploaded_at` field**. The upload timestamp exists only inside the
non-sortable `metadata` JSON blob, which `$orderby` cannot reach, so
recency ranking is unavailable on this index as shaped. Adding it is a
schema change under ARCHITECTURE.md §7.7 — not a tool change. Never
re-sort the returned `top_k` client-side and present it as recency
ordering: that reorders only what was already retrieved.

### 7.3 — Index schemas — field names that bind on code

**The canonical full schemas live in ARCHITECTURE.md §7**, with types,
vector dimensions, filter and ordering clauses, and the schema-change
procedure. This subsection carries only the facts a *rule* depends on.
It does not duplicate the schema, and it is not the place to record a
schema change — that lands in ARCHITECTURE.md §7 first, in the same
commit as the Azure AI Search change.

**`improve_knowledge_index`** — LSS Black Belt eBook, static
```
id                String
content           String
content_vector    SingleCollection (3072d)
metadata          String
source_file       String
phase_relevance   String
page_number       Int32
```

**`improve_evidence_index`** — Belt-uploaded documents, per case.
*The only channel for external data (§1.9).*
```
id                String
content           String
content_vector    SingleCollection (3072d)
metadata          String
case_id           String
```

**`improve_case_index`** — live case records, cross-case memory
```
id                      String
case_id                 String
title                   String
belt_level              String
leader                  String
department              String
current_phase           String
rag_status              String
status                  String
created_at              String
target_date             String
days_in_phase           Int32
phase_summary_define    String
phase_summary_measure   String
phase_summary_analyse   String   ← renamed from phase_summary_analyse_phase
phase_summary_improve   String
phase_summary_control   String
content_text            String
embedding               SingleCollection (3072d)
```

**Breaking schema change — LANDED Aug 2026.**
`phase_summary_analyse_phase` was renamed to `phase_summary_analyse` in
Azure AI Search by delete + recreate (the index held 0 documents, so
nothing was lost and no reindex was needed). The pattern
`phase_summary_{phase.lower()}` is now correct for all five phases. A
mapping constant was considered and rejected: fix the name at the
source so no permanent workaround exists.

**The internal phase key is `analyse`, never `analyse_phase`.** The
key was renamed across the codebase in the same change, so
`f"phase_summary_{phase}"` is correct for all five phases with no
mapping constant anywhere. This binds on: `PHASE_ORDER` and every
`phase_order` list, v1 `phase_inputs` keys, `EXTRACTION_MAP`,
`ORCHESTRATOR_CONTEXT_MAP`, `GATE_CHECKS`, `PhaseSummaryRecord`,
`CaseDocument.phases`, the graph node names, and the module path
`backend.phases.analyse`. `AnalysePhaseInput` keeps its name —
`{Phase}PhaseInput` is the convention all five phases follow. Full
scope: ARCHITECTURE.md §7.3.1.

**Never write to Agent Resolve indexes.** Read only, via tools.

### 7.4 — Multi-query + RRF is mandatory, not optional

All three retrieval tools generate 3–5 query variants and fuse the
results with Reciprocal Rank Fusion, k=60.

This is not a nice-to-have. Agent Resolve production experience showed
Azure AI Search ranking unreliable for this corpus — with a single
query it was not reliably returning the right matches. RRF
operationalises cross-variant consistency, which single-query native
ranking cannot do because it does not know the variants exist.

RRF is about fifteen lines and needs no LangChain class. `MultiQueryRetriever`
and `EnsembleRetriever` are BANNED — both moved to `langchain-classic`
in the 1.0 namespace split, and the former is deprecated even there.

Variant generation uses structured output (§4.6), never manual JSON
parsing.

### 7.5 — Multi-hop policy per phase

The **phase planner** decides retrieval strategy at plan time, not the
executor at retrieval time. `coaching_plan` carries a
`retrieval_strategy` field.

| Phase | Default | Multi-hop when |
|---|---|---|
| Define | Single-hop | Never — scoping questions are direct |
| Measure | Single-hop | Complex measurement system validation (GR&R) |
| **Analyse** | **Multi-hop, planned (3 hops)** | Almost always — root cause validation is layered |
| Improve | Single-hop | Belt is comparing competing approaches |
| Control | Single-hop | Never — documentation questions are direct |
| **Gate validation** | **No retrieval** | **Never** |

**Gate validation never retrieves.** The rubric already encodes the
methodology standards; retrieval there is redundant and adds latency
at exactly the moment the Belt is waiting.

Multi-query and multi-hop compose: multi-query broadens within a hop,
multi-hop deepens across hops.

*Rationale: REFACTORING_AGENT_IMPROVE.md §32, §33, §34, §36, §37, §40, §71.*

---

## 8. MIDDLEWARE STACK

### 8.1 — Five middlewares, all on `create_agent`

```python
middleware=[
    BeforeModelStateInjection(...),    # §8.5 — custom        · before_model
    DMAICSkillsMiddleware(...),        # §8.3 — custom        · before_agent
    SummarizationMiddleware(...),      # §8.4 — LangChain core · before_model
    ModelRetryMiddleware(retries=2),   # §8.7 — LangChain core · wrap_model_call
    DMAICGraderMiddleware(...),        # §8.2 — custom        · after_agent
]
```

Three are custom, two are core. All are built on the six
`AgentMiddleware` hooks (`before_agent`, `after_agent`,
`before_model`, `after_model`, `wrap_model_call`, `wrap_tool_call`).

**Declaration order is execution order for hooks of the same kind, so
this order is binding.** `BeforeModelStateInjection` MUST be first —
project facts have to reach the top of the prompt before skills loading
and summarisation shape it. Listing it last, as an earlier revision did,
defeats the ordering rule §8.5 exists to enforce.

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
```

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
post_improvement_metric, improvement_delta, financial_impact_verified,
handover_documented, lessons_learned, transferability). Each criterion
carries its tier (§9.7). Full text in REFACTORING_AGENT_IMPROVE.md §42;
the tier table is ARCHITECTURE.md §13.

**Three criteria are verified deterministically, not by judgment.**
`causal_hypothesis`, `solution_linked_to_root_cause` and
`post_improvement_metric` are cross-phase reference dicts (§10.6); the
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

### 8.5 — `before_model` state injection — injection timing

**Custom.** Prepends structured project state at the **top** of the
prompt, ahead of the conversation: captured fields (this phase's
`artifacts` plus prior phases' gate documents from the store), current
phase requirements, and the missing fields reported by
`check_gate_status()`.

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

**LangChain core, used as shipped, ADOPTED.** `retries=2` with
exponential backoff, on the `wrap_model_call` hook. It wraps each model
call and silently retries transient timeouts and rate limits.

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

*Rationale: REFACTORING_AGENT_IMPROVE.md §36, §42, §53, §80, §83, §84.*

---

## 9. VALIDATION AND GATES

### 9.1 — The nine-step HITL gate pattern

| Step | What happens | Quality check for |
|---|---|---|
| 1. Executor runs | Coach produces its response; extraction captures fields | — |
| 2. **Validation stack** | Four layers, cheapest first (§9.2). Failures feed back with accumulated per-layer feedback. **The Belt does not see this loop.** | **AI's work** |
| 3. Interrupt fires | `gate_review_node` pauses; Belt sees validated output | — |
| 4. Belt reviews | Belt checks AI-captured values for accuracy | — |
| 5. Belt edits *(optional)* | Belt corrects wrong fields | — |
| 6. **Policy advisory** | Validates the Belt's edits against required-field policy, cross-phase consistency, and previously approved values (§9.4). **Non-blocking.** | **Human's edits** |
| 7. Belt approves | Belt confirms the gate is ready; the gate document is assembled and written to the store **and** `PhaseState.final` (§9.6) | — |
| 8. Checkpoint saves | State committed **only now** | — |
| 9. Next task | Supervisor reads `gate_passed`, routes onward | — |

**Two quality checks, two actors, two moments.** The grader blocks
(step 2) because it checks the AI's own output and there is no reason
to show the Belt work already known to be below standard. The advisory
does **not** block (step 6) because the Belt is the domain expert — it
offers a second opinion before the decision, not a veto after it.

### 9.2 — The four-layer validation stack

All four run inside step 2, before the interrupt.

| Layer | Checks | Mechanism | Model | Fires |
|---|---|---|---|---|
| **2a. Coherence** | Real, meaningful, conclusive? Catches gibberish, vague non-answers, self-contradiction, off-topic replies, parroting the Belt's own words | Lightweight LLM | `coherence`, temp 0.1 | **Every coaching turn** |
| **2b. Field presence** | All **Tier 1** fields for this phase populated? (`DMAICGateValidator`) | **Deterministic** | No LLM | Gate boundary only |
| **2c. Constraint** | Addresses budget / timeline / risk / measurement? | Lightweight LLM | `constraint`, temp 0.1 | Gate boundary + mid-conversation for key decisions |
| **2d. Quality rubric** | Does the **gate document** meet DMAIC standards per criterion? **Tier 1 fails, Tier 2 warns.** Uses `PHASE_RUBRIC` — *not* `DMAICGraderMiddleware`, which is a different grader (§8.2) | LLM grader | `grader`, temp 0.1 | Gate boundary only |

**Run cheapest first. Each layer fires only if the previous passes.**

**The counter is `PhaseState.gate_attempts` and the accumulated feedback
is `PhaseState.validator_feedback`** (§10.1). Neither may live in route
scope, and neither may be per layer.

**Layer 2b is the only deterministic layer.** Coherence and constraint
checks are LLM calls because format checks cannot detect content
failures — a length check does not detect fluent nonsense, and a
keyword check rejects a decision that addresses cost without using the
word "budget." Layer 2a costs roughly $0.01–0.02 per phase session at
20–40 turns; this is settled and is not to be re-optimised into a
regex.

**The iteration cap is 3, SHARED across all four layers**, with
accumulated feedback. Not three per layer. Feedback is specific:
*"your previous answer did not address timeline or risk mitigation"*,
never *"try again."*

**Per-phase constraint sets** are constants in `core/prompts.py`:
`DEFINE_CONSTRAINTS`, `ANALYSE_CONSTRAINTS`, `IMPROVE_CONSTRAINTS`,
`CONTROL_CONSTRAINTS`. Measure is covered by its rubric.

**Value-dependent constraints are supported and required** where a
constraint is conditional on another field — e.g. the risk-mitigation
check fires only when `risk_level == "low"`, because a low-risk
project should say how it stays low-risk, whereas a high-risk
project's decision inherently involves risk.

Every attempt at every layer is logged to `step_log` as a dict (§10.3).

### 9.3 — Where each check fires, and what the Belt sees

| Layer | Every turn | Key decision moments | Gate boundary |
|---|---|---|---|
| 2a Coherence | ✅ | ✅ | ✅ |
| 2b Field presence | ❌ | ❌ | ✅ |
| 2c Constraint | ❌ | ✅ | ✅ full check |
| 2d Quality rubric | ❌ | ❌ | ✅ last |
| Mid-phase contradiction (§9.4) | ✅ | ✅ | ✅ |

**The self-healing hierarchy — and the transparency principle:**

| Level | Trigger | Behaviour | Belt sees | Retry |
|---|---|---|---|---|
| 1 — Silent | Coherence failure mid-turn | System retries internally | **Invisible** | Max 2, then degraded mode |
| 2 — Coached | Constraint failure on a Belt proposal | Coach teaches toward a better formulation | Transparent, collaborative | **No cap** — this is dialogue, not a loop |
| 3 — Validated | Full four-layer check at the gate | Belt sees pass/fail, corrects, approves | Transparent, Belt approves | Max 3, accumulated feedback |
| 4 — Escalated | Attempts exhausted | System defers with unresolved constraints named | Transparent, Belt is arbiter | None |

> **Design principle: coached improvement is key, because silent is
> not transparent.**
>
> The default posture is transparency. **Silent retry is the narrowly
> scoped exception — coherence only** — justified because showing a
> Belt that the AI produced gibberish adds no value and erodes trust.
> Everything else is visible and collaborative.
>
> Level 2 having no retry cap is deliberate. Capping it would mean the
> coach eventually accepts a weak root cause, which is exactly the
> outcome DMAIC discipline exists to prevent. A constraint failure on
> a Belt's proposal is **a teaching moment, not an error**.

### 9.4 — Mid-phase conflict detection — auto-flag, no threshold

The policy advisory does **not** only run at gate boundaries. It runs
**before each coach response is returned to the Belt**.

**Mechanics:**
- Compares the Belt's most recent statements against the `artifacts`
  already committed in prior gate documents
- **If any numeric or categorical value differs, the coach's response
  is suppressed and a HITL interrupt payload is emitted**
- Payload: field name, previously approved value, its approval
  timestamp and gate, the proposed new value, two Belt-facing options
- Structured diff — **no LLM call**, negligible latency

**Belt's two options:**

| Option | Consequence |
|---|---|
| Update the approved value | The affected phase's gate document becomes provisional; downstream phases need re-review |
| Keep the approved value | The Belt clarifies they misspoke; no state change |

**There is NO tolerance threshold, and none may be added.** In
production DMAIC, baseline means, sigma levels, and target metrics are
taken seriously; silent drift across weeks is exactly the failure mode
a coaching system exists to prevent. *"The delta was small enough"* is
not acceptable when downstream analysis depends on the value.

**Any change to a previously gate-approved value is a mini-gate, never
a silent overwrite.**

### 9.5 — The re-approval cascade

If the Belt confirms a new value, the affected phase **and every
downstream phase that depends on it** return to a provisional state
and require re-review.

This is deliberately heavier than a soft override. A root cause
validated against a baseline of 4.2 is not automatically valid against
3.8. Silent invalidation of downstream analysis is not acceptable.

**The cascade has a hard dependency on §3.6.** When it fires, the
affected phase's `error_handler` compensating logic MUST run to clean
up stale values already written to Azure Blob and `improve_case_index`.
A cascade that marks phases provisional but leaves published values in
place is worse than no cascade — state and index then disagree,
silently.

### 9.6 — `gate_apply_node` writes the gate document TWICE

**This is the write the whole store-mediated handoff depends on.** Every
cross-phase read in §10.2 assumes the previous phase's gate document is
in the store. `gate_apply_node` is what puts it there.

After Belt approval, at step 7, `gate_apply_node` writes to **both**:

```python
# 1. The store — what the next phase's input mapper reads
store.put(("projects", case_id, "artifacts"), phase_name, gate_document)

# 2. PhaseState — so the checkpoint is self-sufficient for crash recovery
return {"final": gate_document, "gate_attempts": 0, "validator_feedback": []}
```

**Both writes are required.** The store write and the checkpoint commit
are separate operations; a crash between them would leave state saying
the gate was not applied while the store says it was. `final` holding
the same dict means the resumed graph can see what was approved without
re-reading the store — which is why `final` is a `dict` and not a `str`.

**Store path:** `store/projects/{case_id}/artifacts/{phase}.json`

**The gate document contains, and nothing may be omitted from it:**

| Part | Source |
|---|---|
| All captured fields (strings — §10.6) | `artifacts` |
| The three cross-phase reference dicts, where they apply | `artifacts` |
| `computation_results` | `artifacts["computation_results"]` |
| `citations` | `PhaseState.citations` |
| `uploads` | `PhaseState.uploads` |
| `acknowledged_gaps` | Tier 2 fields the Belt chose to proceed without (§9.7) |

**`gate_attempts` and `validator_feedback` reset here, and only here.**
The retry budget is per gate passage.

### 9.7 — Two tiers of field; the grader gains a `warning` verdict

**Layer 2b and Layer 2d must not be able to contradict each other.**
Before this rule, the gate blocked on a required-field list while the
grader graded against a rubric covering a different set — so a phase
could pass the gate and then be failed by the grader on a criterion the
gate never asked for.

**Every rubric criterion is classified into one of two tiers.**

| Tier | Layer 2b | Layer 2d | Belt |
|---|---|---|---|
| **Tier 1 — gate-required** | **Blocks** | Can `fail` | Must supply it |
| **Tier 2 — rubric-recommended** | Not checked | At worst `warning` | Add it, or proceed with an acknowledged gap |

**Tier 1, by phase:**

| Phase | Tier 1 |
|---|---|
| Define | `problem_statement`, `voc_summary`, `project_scope`, `goal_statement` |
| Measure | `baseline_mean`, `data_collection_plan` |
| Analyse | `root_cause_statement`, `root_cause_validation` |
| Improve | `selected_solution`, `pilot_result` |
| Control | `control_plan`, `post_improvement_metric` |

**Everything else in the rubric is Tier 2** — `baseline_sigma`,
`ruled_out_causes`, `handover_documented`, `financial_impact_verified`,
`implementation_plan`, `lessons_learned`, `transferability`, and the
rest.

**The grader's verdict has three statuses, not two:**

```python
class CriterionVerdict(BaseModel):
    criterion: str
    tier:      int                                     # 1 or 2
    status:    Literal["pass", "warning", "fail"]
    feedback:  str                                     # specific, per criterion
```

**A gate MAY pass with warnings. A gate may NEVER pass with failures.**
Only Tier 1 criteria may produce `fail`.

**A Tier 2 gap the Belt proceeds past MUST be recorded**, never silently
dropped:

```python
"acknowledged_gaps": ["baseline_sigma — Belt accepted gap"]
```

The next phase's planner reads it from the store and factors it into the
coaching plan.

**Why two tiers.** A gate that blocks on every criterion teaches Belts
to fill fields mechanically — complete gate documents, worse projects.
Tier 1 catches genuinely incomplete phases; Tier 2 coaches toward best
practice while leaving the judgment with the Belt, who knows the
project. The audit trail then records conscious decisions rather than
silent omissions.

**The grader is belt-level aware.** It reads `belt_level` from the case
record:

```
if belt_level == "Black Belt":
    flag FMEA, DOE, X-Y matrix, statistical problem statement as Tier 2
if belt_level == "Green Belt":
    suppress these — do not recommend heavy methodology GB isn't trained for
```

**Stability / special-cause analysis is NOT suppressed for either
level** — a baseline computed across an unstable process is not a
baseline. It is Tier 2 with a strong warning for both.

*Rationale: REFACTORING_AGENT_IMPROVE.md §2, §38, §42, §48, §49, §68, §69.*

---

## 10. STATE AND STORAGE

### 10.1 — Two state schemas

**`SupervisorState`** — orchestration only:

```python
class SupervisorState(TypedDict):
    messages:        Annotated[list[BaseMessage], operator.add]
    history:         Annotated[list[str], operator.add]
    case_id:         str                                  # canonical id — §10.5
    phase_index:     int                                  # 0=Define … 4=Control
    current_phase:   str
    gate_passed:     dict[str, bool]                      # {"define": True, …}
    final_output:    Optional[dict]                       # set at the Control gate
```

**Seven fields. That is the entire schema.** An eighth requires an
ARCHITECTURE.md amendment (§18).

**`gate_passed` is a `dict[str, bool]`, not a `list[str]`.**
`gate_passed["measure"]` is a direct lookup, and the re-approval cascade
(§9.5) sets a phase back to `False` rather than removing it from a list.

**`final_output` is `Optional[dict]`, never `str`** — same rule as
`PhaseState.final` (§10.1, §10.6).

**Artifacts and gate documents are NOT on `SupervisorState`.** They live
in the store (§10.2). Adding them back is a violation.

**`dmaic_plan`, `key_decisions`, `open_items` and `project_context` are
NOT on `SupervisorState` either.** All four were removed as redundant —
each duplicated something an existing mechanism already carries:

| Removed field | What covers it instead |
|---|---|
| `dmaic_plan` | DMAIC order is fixed and static (§1.2), so there is no plan to store. The project's actual plan is Define's gate document in the store plus `improve_case_index` metadata |
| `key_decisions` | Decisions the Belt commits are captured fields, arriving via `CoachingResponse.fields_captured` and approved at a gate. A decision that is not worth a field is not worth replaying into every prompt |
| `open_items` | Outstanding work is derived, not stored: `check_gate_status()` reports which required fields are unpopulated, and the four-layer validation stack (§9.2) is what surfaces blockers |
| `project_context` | Composed at the boundary by each input mapper (§10.2). Define reads the case record from the store; every later phase reads the prior phase's artifacts. The substance is Define's gate document; the framing is the case record and the `improve_case_index` row (§7.3). `before_model` injection (§8.5) already puts both in front of every coach |

Deriving these on demand is what keeps them correct. A stored
`open_items` list is a second source of truth for gate readiness that
can disagree with `DMAICGateValidator`; a derived one cannot. Adding
any of the four back is a violation.

**`project_context` had no writer at all.** Its comment said "set once
after Define," yet nothing set it, and its only reader —
`define_input_mapper` — runs before Define. Every later phase already
built `phase_context` from the store. **Context is composed at the
boundary, never carried on parent state.**

**`current_phase` and `phase_index` are derived from `gate_passed` and
kept anyway** — a documented exemption for readability, not an
oversight. They are read in dozens of places, and they are written in
exactly one: the output mapper at gate approval (§10.2). **Nothing else
may write them**, and the supervisor is responsible for keeping them
consistent with `gate_passed`. Full rationale: ARCHITECTURE.md §4.1.2.

**`PhaseState`** — per-phase subgraph state:

```python
class PhaseState(TypedDict):
    # conversation plumbing
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]
    phase_context:      str                # composed at the boundary — §10.2

    # the twelve content fields
    coaching_plan:      dict[str, Any]     # ONE plan per planner turn
    field_index:        int                # field within the phase
    draft:              dict[str, Any]     # this turn's extraction
    artifacts:          dict[str, Any]     # accumulated for the phase
    step_log:           Annotated[list[dict[str, Any]], operator.add]
    belt_edits:         dict[str, Any]     # Belt corrections at the gate
    turn_count:         int
    final:              dict[str, Any]     # approved gate document — §9.6
    gate_attempts:      int                # retry counter, cap 3
    validator_feedback: list[dict]         # accumulated per-attempt feedback
    citations:          list[dict]         # sources cited this phase
    uploads:            list[dict]         # files the Belt uploaded this phase
```

**`draft`, `belt_edits` and `final` are `dict`, never `str`.**
String-typed handoffs force downstream nodes to parse prose, which is
the anti-pattern this architecture exists to remove.

**`coaching_plan` is a single `dict`, never `list[dict]`.** One plan per
planner turn, overwritten each time the planner fires. There is no
upfront queue — the planner reads `artifacts` to know what is captured
and what is next, and a plan made at turn 1 cannot anticipate turn 4.

**`gate_attempts` MUST be on `PhaseState` and in the checkpoint.** It is
the shared counter for the four-layer stack (§9.2): incremented per
failed attempt, reset to 0 when the gate passes, escalating at 3.
Holding it in route scope is what produced the v1 "attempts always reset
to 0" bug — it is per phase, because each phase runs its own loop with
its own cap (§1.7, §3.5).

**`validator_feedback` and `belt_edits` are different things and must
stay separate.** `validator_feedback` is what the system's validation
layers said about the AI's output at step 2; `belt_edits` is what the
Belt corrected at step 5. Two actors, two moments (§9.1). The single
`feedback` field they replace conflated them, which would have had the
coach reading the Belt's corrections as validation failures.

**`validator_feedback` is what makes the shared cap of 3 defensible.**
Each entry records attempt, layer, criteria failed, and specific
feedback; the coach reads the full list on retry. Reset to `[]` when the
gate passes. A cap on retries that carry no memory of the previous
failure is just a cap on repetition.

**`citations` and `uploads` are the evidence trail.** Both are written
into the gate document (§9.6) — the coach cites BB eBook sources and the
Belt uploads files, and without these the gate document cannot show what
the phase was grounded in.

**Naming discipline:** `phase_index` (which phase) and `field_index`
(which field within a phase) are distinct. Never reuse `step_index`.

**Use explicit `TypedDict`, not `MessagesState` inheritance**, for
phase states — their dominant content is structured fields, not
conversation. `MessagesState` inheritance is appropriate only for the
debate subgraph, which is not in scope.

### 10.2 — The store — cross-phase artifacts

**Namespace convention:**
```
("projects", case_id, <kind>)
```

| Namespace | Keys | Contents |
|---|---|---|
| `("projects", case_id, "case")` | `"record"` | Case framing — title, department, belt level, leader, target date. Written once at session start from `cases/case_{id}.json`, never mid-conversation |
| `("projects", case_id, "artifacts")` | `"define"`, `"measure"`, … | **Each phase's approved gate document** — written by `gate_apply_node` (§9.6) |
| `("projects", case_id, "step_log")` | timestamped | Append-only cross-phase audit trail |

**Blob prefix:** `store/projects/{case_id}/{kind}/{key}.json`

`case_id` is the same value as the graph's `thread_id` (§10.5).

**The `gate_documents` namespace is retired.** A phase's approved
artifacts and its gate document are the same object; two keys holding
the same content is a question about which is authoritative with no
answer. Reintroducing it is a violation.

**Cross-phase handoff uses boundary mappers**, in
`phases/{phase}/mappers.py`:
- The output mapper writes artifacts to the store at gate approval and
  returns **only orchestration-relevant values** to the parent
- The input mapper reads the prior phase's artifacts from the store

**Every input mapper composes `phase_context` from the store** — Define
from the case record, later phases from the prior phase's artifacts. An
input mapper's only dependency is `BaseStore`. Reading context off
parent state, or handing a mapper a blob client, is a violation: the
first creates a parent field to keep in sync, the second puts untracked
I/O in a translation function.

**The `case` namespace is not a second system of record.**
`cases/case_{id}.json` (§10.4) stays authoritative.

**String-interpolating a previous phase's output into the next
phase's prompt is BANNED.** Measure reads Define's baseline metric as a
named field out of a structured gate document, not out of prose. The
field's *value* is a string (§10.6) — the prohibition is on parsing a
value out of an interpolated prompt, not on the value's type.

**The store is not the case index.** Cross-*case* retrieval for yokoten
is `rag_lookup_case_history` (§7.2). The store carries cross-*phase*
data within one project. Two mechanisms, two purposes.

**Ordering constraint:** implement the store **after** `thread_id` is
wired through `graph.ainvoke`. A store is meaningless without working
checkpoint persistence.

### 10.3 — `step_log` — dicts, never tuples

Every audit entry is a dict with named keys. Tuples are BANNED — field
names make the log self-documenting and queryable.

```python
{"layer": "constraint", "attempt": 2, "status": "failed",
 "reason": "does not address timeline", "decision_excerpt": "..."}

{"service": "gpt-4o", "attempt": 2, "status": "failed",
 "reason": "timeout after 45s", "timestamp": "..."}
```

Everything requiring an audit trail writes here: the four validation
layers (§9.2), each grader iteration via `on_evaluation` (§8.2), and
every fallback attempt (§4.8).

**`artifacts` and `step_log` are separate fields and must stay
separate.** `artifacts` is WHAT was captured; `step_log` is HOW. For a
DMAIC quality system the Belt must be able to show not just what the
root cause was, but how it was determined.

### 10.4 — Azure Blob — two distinct concerns

**Concern 1: Checkpoints (in-flight graph state)**
- Path: `checkpoints/{case_id}/latest.json` + `history/{id}.json`
- Written by `AzureBlobCheckpointSaver` after every graph node
- Owner: `core/checkpointer.py`

**Concern 2: Case records (system of record)**
- Path: `cases/case_{id}.json`, `registry.json`, `uploads/{case_id}/{file}`
- Written on case create, on gate pass, on file upload — **never
  mid-conversation**
- Owner: `storage/blob.py` via `ImproveBlobClient`

Same Azure Storage account, separate concerns, separate code paths.

**The case blob is NOT updated per turn.** The v1 pattern of
overwriting `case_{id}.json` on every `/ask` is REMOVED. Conversation
history lives in the checkpoint until gate pass.

**Case-vs-registry atomicity:** gate-pass case blob write and registry
update remain two separate writes. Both are covered by the node's
`error_handler` (§3.6).

### 10.5 — Naming: `case_id` and `artifacts` are the only names

**The project identifier is `case_id`. Everywhere.** State field, store
namespace segment, `thread_id`, blob path, log field, index field,
prose. **`project_id` is retired and may not be reintroduced.**

This was never a design question — it was documents disagreeing with
code. `improve_case_index.case_id`, `improve_evidence_index.case_id`
(§7.3), `cases/case_{id}.json`, `uploads/{case_id}/{file}` and every
storage model already said `case_id`.

**A phase's captured fields are `artifacts`. Everywhere.**

| Retired name | Was | Rule |
|---|---|---|
| `captured_fields` | Prose name in these documents | Never use in prose — say `artifacts` |
| `phase_inputs` | v1 code field name | Never add to v2 code; replaced during the refactor |

`PhaseState.artifacts` holds the fields the Belt has produced in this
phase. Three names for one concept is how a reader ends up believing
there are three things.

### 10.6 — Every captured field is a string

**All captured fields are `str`.** No phase schema declares a typed
numeric. **Computation tools parse at the point of use** — each of the
18 (§5.2) extracts what it needs from the string it is given and returns
a clear reformatting request to the Belt when it cannot.

```python
baseline_mean = "12.3% invoice error rate, measured over Q2 2026"
```

**The gate document shows the Belt's exact words.** That is a
requirement of a quality system: the Belt must be able to show what they
stated, not what the system parsed out of it.

> **This corrects the previous §10.2, which claimed "Measure reads
> Define's baseline metric as a typed float."** No baseline field has
> ever been typed as a float in any schema in this project. The prose
> promised a guarantee the schemas did not provide.

**The one exception — three cross-phase reference fields are `dict`:**
`causal_hypothesis` (Analyse), `solution_linked_to_root_cause`
(Improve), `post_improvement_metric` (Control). Each carries the Belt's
content plus `references_phase`, `references_field` and
`references_value`, so the grader verifies the link by reading the
referenced phase's gate document from the store — deterministic, no LLM
judgment in the linkage check. The values inside the dict are still
strings. Design detail: ARCHITECTURE.md §4.7.

**Computation tool output goes in `artifacts["computation_results"]`**
as a list of typed dicts, all values strings. No new top-level
`PhaseState` field, and no per-phase typed destinations — the grader
answers "was a hypothesis test run?" by scanning that list for
`"tool": "t_test"`. Adding typed per-phase computation fields is a
violation (ARCHITECTURE.md §4.8).

### 10.7 — `CoachingResponse` in, `{Phase}Output` out

**Two schemas, two moments. Never substitute one for the other.**

| | `CoachingResponse` | `{Phase}Output` |
|---|---|---|
| Fires | **Every coaching turn** | **Once**, at `gate_apply` |
| Produced by | The executor, via `response_format=` | Pydantic construction — no LLM |
| Holds | This turn's extraction | The complete gate document |

**`CoachingResponse` — the per-turn schema:**

```python
class CoachingResponse(BaseModel):
    """Structured extraction from each coaching turn."""
    message: str                        # coaching text the Belt sees
    fields_captured: list[dict] = []    # [{field_name: str, value: Any, source: str}]
    citations: list[dict] = []          # sources referenced this turn
```

**`value` is `Any`, not `str`, and that is deliberate** — it must carry
both plain string fields and the three cross-phase reference dicts
(§10.6). Typing it `str` would make `causal_hypothesis`,
`solution_linked_to_root_cause` and `post_improvement_metric`
uncapturable. This is the one place `Any` is correct; the *values inside*
those dicts are still strings.

**The executor node writes the response into state:**

```python
result = await executor.ainvoke(state)
resp = result["structured_response"]              # CoachingResponse

for f in resp.fields_captured:
    artifacts[f["field_name"]] = f["value"]       # str or dict
citations.extend(resp.citations)
```

**`{Phase}Output` schemas are canonical** — `DefineOutput`,
`MeasureOutput`, `AnalyseOutput`, `ImproveOutput`, `ControlOutput`, in
`phases/{phase}/schema.py`. Full definitions and per-phase gate assembly
are in ARCHITECTURE.md §4.10. The binding rules:

- **Every field is `str`** except the three cross-phase reference dicts
  (§10.6)
- **Every schema carries the same four gate-metadata fields** —
  `computation_results`, `acknowledged_gaps`, `citations`, `uploads`
- **Tier 1 fields are assembled with `artifacts["field"]`** — a
  `KeyError` here is correct, because Layer 2b should have blocked the
  gate
- **Tier 2 fields use `artifacts.get("field", "")`**, cross-phase dicts
  `artifacts.get("field", {})` — an empty value records that the Belt
  proceeded without it (§9.7)
- **Gate assembly must reference every field in the schema.** A field in
  the schema that assembly never sets is a field that silently never
  reaches the store

*Rationale: REFACTORING_AGENT_IMPROVE.md §17, §18, §19, §21, §52, §52a, §68, §70, §82.*

---

## 11. TRACING AND OBSERVABILITY

### 11.1 — LangSmith required

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=agentlean-improve
```

Production environments without LangSmith fail startup with a clear
error (§11.4).

### 11.2 — `@traceable` on every custom function

LangSmith traces LangChain runnables and LangGraph nodes
automatically. It does **not** trace plain Python functions. Without
`@traceable`, the logic *between* nodes is invisible and a gate failure
surfaces as a 500 with no indication of which layer failed.

`@traceable` is REQUIRED on every function that:
- Extracts fields from LLM responses
- **Validates gate criteria — all four layers of §9.2**
- Scores completeness
- Makes routing decisions outside LangGraph node routing
- Calls an external Azure service directly, outside a LangChain runnable

### 11.3 — What gets traced

- Every graph invocation (full graph as parent span)
- Every node execution (child span per node)
- Every LLM call (prompt, response, token counts, cost)
- Every tool call (arguments and result)
- Every retrieval (query and top-k results)
- Every validation layer (§11.2)

**P50/P99 latency is a coaching quality signal**, not just an ops
metric. High P99 degrades the Belt's experience. The usual outlier is
multi-hop retrieval combined with a grader call on the same turn; the
fixes in order of preference are caching (§4.8 Level 3), a faster
grader model, and reordering the validation stack cheapest-first
(already mandated in §9.2).

### 11.4 — Fail-fast environment validation

Validate all required credentials at startup, before the first request:

```
AZURE_OPENAI_KEY        — coaching LLM
AZURE_SEARCH_API_KEY    — retrieval        (NOT "AZURE_SEARCH_KEY")
LANGCHAIN_API_KEY       — observability
```

Missing credentials exit 1 with a clear message. This integrates with
Docker health checks — a container failing startup receives no traffic.

**`.env` hygiene:** the app loads `agent-improve/.env`. A root `.env`
can silently shadow values depending on `load_dotenv()` search order —
audit and remove it if redundant.

### 11.5 — Logs

Structured logs via `logging`. Every request gets a `request_id`. Every
node logs entry, exit, and the state-slice keys it returned.

---

## 12. EVALUATION AND REGRESSION TESTING

### 12.1 — The eval suite is built alongside the refactor

Not before it. Establishing a baseline against the current system
would produce a baseline of "bad." The suite becomes load-bearing when
the coach, retrieval tools, and grader are wired — that is when output
quality changes. Infrastructure steps (graph structure, state schemas,
checkpointer) do not affect coaching quality.

**The dataset is authored jointly, not generated.** Coaching quality
judgments are domain judgments; a generated dataset measures agreement
with a model rather than correctness.

### 12.2 — Minimum viable suite

| Dimension | Requirement |
|---|---|
| Size | 20–30 examples, 4–6 per DMAIC phase |
| Categories | Realistic coaching turns · edge cases · tool-calling scenarios · failure/ambiguous cases · historical production data |
| Metrics | Accuracy (field extraction) · relevance · reasoning quality · tool usage · safety (no invented methodology) |
| Evaluator order | Deterministic ($0) → LLM-judge relevance (~$0.01) → LLM-judge reasoning (~$0.02) |
| **Regression threshold** | **Block release if any metric drops >10% from baseline** |
| Run frequency | Every commit touching system prompts, graph structure, or model config |

**Rubrics and the eval dataset are complementary, not duplicative.**
Rubrics (§8.2) define what good looks like *for the grader*, in
production, at every gate. The eval dataset tests whether the whole
system produces good outcomes, in CI, at every commit.

### 12.3 — Structured errors

All external service failures use one schema, in `core/errors.py`:

```python
class AgentImproveError(BaseModel):
    error_code: str              # "TIMEOUT", "RATE_LIMIT", "AUTH_FAILURE", …
    severity: str                # "transient" | "permanent"
    retry_recommendation: str    # "retry_after_backoff" | "do_not_retry" | …
    affected_identifier: str
    message: str
    timestamp: datetime
```

`severity` is what lets the circuit breaker distinguish "retry" from
"stop trying"; `retry_recommendation` is what the fallback chain reads
to choose backoff strategy (§4.8).

---

## 13. UI AND LANGUAGE RULES

- No methodology jargon in any team-facing string — plain language always
- Technical terms appear only as small secondary grey labels
- Every AI data request must include a concrete example with column names
- Every AI suggestion using cross-agent data must include a visible
  source citation
- Citation format: `agent_origin`, `index_name`, `document_id`,
  `relevance_summary`
- **Retrieval citations surface `source_file` and `page_number`**
  (§7.2) — "this came from page 47 of the BB eBook"
- **Spinner messages are contextual, never generic** — "Retrieving
  methodology…", "Validating your root cause…", not "Loading…"
- **The gate review screen shows extracted fields before approval**,
  editable, with an explicit approve action (§9.1 steps 4–7)

---

## 14. NO-GO LIST

**State and persistence**
- Never add artifacts or gate documents to `SupervisorState` — seven
  fields, and an eighth needs an amendment (§10.1)
- Never add `dmaic_plan`, `key_decisions`, `open_items` or
  `project_context` to `SupervisorState` — all four were removed as
  redundant (§10.1)
- Never write `project_id` — the identifier is `case_id` everywhere
  (§10.5)
- Never write `captured_fields` in prose or `phase_inputs` in v2 code —
  the name is `artifacts` (§10.5)
- Never reintroduce the `gate_documents` store namespace — the gate
  document lives under `artifacts` (§10.2)
- Never type a captured field as a numeric — all captured fields are
  `str`, and the computation tools parse at the point of use (§10.6)
- Never add typed per-phase destinations for computation results — they
  go in `artifacts["computation_results"]` (§10.6)
- Never hold `gate_attempts` in route scope — it is on `PhaseState` and
  in the checkpoint, or the v1 reset bug returns (§10.1, §1.7)
- Never merge `validator_feedback` and `belt_edits` — system validation
  and Belt corrections are different actors at different moments (§10.1)
- Never write `current_phase` or `phase_index` outside the output mapper
  — they are derived values kept for readability, and one write site is
  what keeps them honest (§10.1)
- Never store a derived list of missing fields or blockers — derive them
  from `check_gate_status()` and the validation stack at the moment they
  are needed (§9.2, §10.1)
- Never carry phase context on parent state — every input mapper
  composes `phase_context` from the store (§10.2)
- Never create a per-phase or concatenated `thread_id`
- Never compile a checkpointer or store onto a phase subgraph
- Never use `InMemorySaver`
- Never write to the case blob mid-conversation
- Never write checkpoints to the case blob path
- Never pass cross-phase data through parent state or string interpolation
- Never log to `step_log` as tuples
- Never reintroduce `analyse_phase` as a phase key — the key is
  `analyse`, matching the index field and the other four phases (§7.3)

**Graph**
- Never mix static edges and `Command` routing from the same node
- Never use `set_entry_point` — use `add_edge(START, ...)`
- Never add a graph node type without an ARCHITECTURE.md amendment
- Never dispatch nodes manually in routes
- Never call `_reflect()` as a private function — reflection is a node
- Never fuse the planner and executor
- Never write a node with external writes and no `error_handler`
- Never hand-write a Saga orchestrator or compensating-action framework

**LLM and tools**
- Never instantiate `AzureChatOpenAI` directly — use `get_llm()`
- Never bind tools directly onto a bare LLM in a phase executor — use
  `create_agent` (§4.4)
- Never use `create_react_agent`, or import from `langgraph.prebuilt`
- Never add deepagents as a dependency while it is pre-1.0
- Never parse JSON from raw LLM text
- Never string-index the raw content field — read `content_blocks`
- Never exceed 16 tools on a phase executor
- Never parameterise the computation tools into mode-argument groups
- Never reference `search_methodology` or `search_evidence`
- Never use `MultiQueryRetriever`, `EnsembleRetriever`, or
  `OutputFixingParser`
- Never use the deprecated `Conversation*Memory` or
  `VectorStoreRetrieverMemory` classes

**Validation and gates**
- Never let a gate pass with a Tier 1 failure; never let a Tier 2 gap
  block a gate (§9.7)
- Never drop a Tier 2 gap the Belt proceeded past — it goes in
  `acknowledged_gaps` in the gate document (§9.6, §9.7)
- Never recommend FMEA, DOE, X-Y matrix or a statistical problem
  statement to a Green Belt (§9.7)
- Never approve a gate without writing the gate document to **both** the
  store and `PhaseState.final` (§9.6)
- Never let the Belt see the grader loop
- Never add a tolerance threshold to mid-phase conflict detection
- Never cap Level 2 coached improvement with a retry limit
- Never make the policy advisory blocking
- Never commit a checkpoint before Belt approval
- Never use `HumanInTheLoopMiddleware` for gates
- Never run retrieval during gate validation
- Never downgrade the coherence or constraint checks to format checks

**Retrieval and data**
- Never build an unconditional retrieval pipeline
- Never catch bare `Exception` around a retrieval call and return `[]` —
  retrieval failure must be distinguishable from no matches (§7.1.1)
- Never let a coach-facing failure message read as an absence of content
  ("no cases found" when the search never ran) (§7.1.1)
- Never filter methodology on `phase`; the field is `phase_relevance` and
  its cross-phase value is `general`, not `all` (§7.2)
- Never write to an index through LangChain without declaring the real
  schema via `fields=` — unmatched metadata keys are silently demoted to
  the JSON blob and become unfilterable (§7.1.2)
- Never call `add_texts` without explicit `ids=` — LangChain assigns a
  random UUID key, so re-ingestion duplicates the corpus (§7.1.2)
- Never write to Agent Resolve indexes — read only, via tools
- Never add an MCP server, client, or dependency
- Never build a fallback path that fetches data the Belt did not upload

**Prompts and governance**
- Never put prompts inline in node files
- Never omit the memory hierarchy paragraph from a coach prompt
- Never omit anti-hallucination guards from a coach or extraction prompt
- Never add classes outside the designated files in §2
- Never duplicate `CitationRecord`
- Never disable LangSmith tracing
- Never use methodology jargon in team-facing strings
- Never renumber a rule cited in `deprecated_patterns.yaml` without
  updating the registry in the same commit (§0.2)

---

## 15. PROMPT SIZE MANAGEMENT

When a UI change touches more than 3 functions or adds more than ~150
lines of new code, split into multiple focused prompts. Never include
more than 2 full function replacements per prompt for `index.html`.

---

## 16. VERSION TARGETS AND DEPENDENCIES

### 16.1 — Pinned targets

| Package | Current | Target | Why |
|---|---|---|---|
| `langgraph` | 1.1.10 | **1.2.10** | Subgraph `checkpoint_ns` fix (§1.2) **and** native reliability primitives (§3.6). Both require ≥1.2.6; 1.2.10 is latest. |
| `langchain` | 1.2.13 | 1.3.11 | Optional but recommended; backward compatible per the 1.0 stability commitment |
| `langchain-classic` | 1.0.3 | 1.0.3 | Keep pinned. Retains legacy classes we do **not** use — presence is not permission. |

Adjacent packages (`langchain-core`, `langchain-openai`,
`langchain-community`, `langchain-text-splitters`, `langsmith`,
`langfuse`) — let pip resolve during the upgrade, then repin.

**During the upgrade, sweep for imports from `langgraph.prebuilt`** —
deprecated in 1.0 → 1.1, functionality moved to `langchain.agents`.

### 16.2 — New infrastructure required

| Component | For | Status |
|---|---|---|
| Azure Cache for Redis | Fallback chain Level 3 (§4.8) | **Not yet provisioned** — add to the provisioning plan |
| Azure Database for PostgreSQL | `PostgresSaver` + `PostgresStore` (§1.7) | Provision before production launch |

### 16.3 — Verify before migrating

`/verify-current-version` is a **mandatory checkpoint before any
architectural decision is finalised**, not background reading. It
exists because a deprecation notice is not sufficient guidance: during
this review, `create_agent` was found to have a reported regression
relative to `create_react_agent`, and the deprecation message pointed
at a function that did not yet exist in the package at the time.

Confirm a replacement is **actually shipped and feature-complete in
the installed version** before porting to it.

---

## 17. MIGRATION AND SEQUENCING

This document describes the **target** architecture.

**Option B is the ratified sequence:** refactor the foundation first,
then build Improve and Control on top of it. Building two more phases
on the current foundation and rewriting them later was rejected.

```
Refactor the foundation
  ├── Checkpointer wired into graph.compile()          ✔ steps 2.1–2.2
  ├── SupervisorState / PhaseState split               §10.1
  ├── Phase subgraphs with private state               §1.2, §3.3
  ├── AzureBlobStore for cross-phase artifacts         §10.2
  ├── Explicit planner / executor nodes                §1.3, §3.3
  ├── Three rag_lookup_* tools, multi-query + RRF      §7
  ├── 18 per-phase computation tools                   §5.2
  ├── Four-middleware coach stack                      §8
  ├── Four-layer validation + nine-step HITL           §9
  └── Reliability: timeouts, error_handler, breaker,
      fallback chain with cache                        §3.6, §4.8
    ↓
Build Improve phase       ← on the correct foundation from the start
    ↓
Build Control phase
    ↓
Run IMPR-2026-E9D end-to-end clean
    ↓
Activate IMPR-2026-FS1
    ↓
Migrate PostgresSaver + PostgresStore                  §1.7
    ↓
Multi-user identity, isolation, tagged observability
```

Two workstreams run **alongside** the refactor, not after it: the
evaluation dataset (§12) and the five DMAIC phase skills (§8.3). Both
encode Black Belt domain judgment.

Until migration is complete the v1 architecture may still operate, but
**no v1-style code may be ADDED**. A file is "migrated" when it is
rewritten under v2.2 rules and committed with a `refactor(arch-v2):`
prefix.

---

## 18. AMENDMENT PROCEDURE

This file is amended only via:

1. A new architectural decision documented in ARCHITECTURE.md
2. A commit to CLAUDE.md updating the relevant rule
3. Increment to the version number at the top
4. Change entry in ARCHITECTURE.md change log
5. **If a rule number cited in `deprecated_patterns.yaml` changes, the
   registry is updated in the same commit** (§0.2)

Never amend a rule "in passing" while making a feature change.
Architecture changes are separate commits.

### 18.1 — Known open item for the next amendment

**§4.6 replaces v2.1's §4.3 and resolves a live contradiction.** The
drift registry's `pattern-2` message cites "CLAUDE.md §4.6" — a rule
that did not exist until this version, while v2.1 §4.3 mandated the
pattern the hook blocked.

Now that §4.6 exists and is scoped, the registry entry should be
updated to reflect the scoping: the builder-style call is correct
inside tools, middleware, and validators, and only agent construction
should prefer `response_format=`. Until that update lands,
`agent-improve/**/*.md` remains path-excluded so the governance
documents stay writable.

*Rationale: REFACTORING_AGENT_IMPROVE.md §86.*
