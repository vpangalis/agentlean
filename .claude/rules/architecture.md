---
paths:
  - "agent-improve/backend/core/graph.py"
  - "agent-improve/backend/core/checkpointer.py"
  - "agent-improve/backend/core/store.py"
  - "agent-improve/backend/core/tracing.py"
  - "agent-improve/backend/phases/subgraph_common.py"
---
# §1 — Architecture principles

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

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

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §5, §6, §8, §9.*

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

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §9, §12, §13, §16.*

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

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §3 (terminology), §13, §17.*

### 1.4 — Async by Default

- All FastAPI endpoints are `async def`
- All graph invocations use `await graph.ainvoke(...)` or
  `graph.astream_events(...)`
- All LLM calls use `await llm.ainvoke(...)`
- All Azure SDK calls use the `aio` variants where available

Synchronous code is permitted only in pure functions with no I/O
(prompt building, state transformations, validation logic, all 20
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

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §33, §19.9.*

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

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §8, §10, Appendix B item 13.*

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

**The runtime stack is:** FastAPI, LangGraph ≥1.2.6, LangChain 1.x,
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

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §29.1, §29.2.*

