---
paths:
  - "agent-improve/backend/core/graph.py"
  - "agent-improve/backend/core/checkpointer.py"
  - "agent-improve/backend/core/store.py"
  - "agent-improve/backend/core/tracing.py"
  - "agent-improve/backend/phases/subgraph_common.py"
---
# §1 — Architecture principles

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

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
  (§1.7, §10).

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §5, §6, §8, §9.*

### 1.2 — Hierarchical Subgraphs, One Thread, Auto Namespacing

- **One `thread_id` per project, equal to `case_id`.** Never per phase, never
  concatenated (`{case_id}-define` and similar are BANNED).
- **The checkpointer and store go on the parent graph ONLY.** Phase
  subgraphs compile without either; `checkpoint_ns` is auto-managed.
- **Phase transitions use static edges**, not a routing LLM and not
  `Command`. DMAIC order is fixed:
  `define → measure → analyse → improve → control → END`.
- **`Command` routing is for inside phase subgraphs only**, where step
  order is genuinely data-dependent.
- **Never mix static edges and `Command` from the same node.** Both
  paths execute, silently.
- **No subgraph imports from another subgraph's nodes.**
- **Cross-phase data flows through the store, never through parent
  state** (§10.2).

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

Extraction is structured output on the executor
(`response_format=CoachingResponse`, §4.6), not a separate node and no
longer a tool call.

**Level 1 (supervisor) has no LLM planner.** Phase sequencing is a
deterministic gate-check on `gate_passed` plus static edges.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §3 (terminology), §13, §17.*

### 1.4 — Async by Default

- All FastAPI endpoints are `async def`
- All graph invocations use `await graph.ainvoke(...)` or
  `graph.astream_events(...)`
- All LLM calls use `await llm.ainvoke(...)`
- All Azure SDK calls use the `aio` variants where available

Synchronous code is permitted only in pure functions with no I/O
(prompt building, state transformations, validation logic, the
computation tools).

**Per-node timeouts require async nodes** (§3.6) — this is a hard
LangGraph constraint, not a preference.

### 1.5 — Streaming Responses

Coach responses stream to the UI via Server-Sent Events on
`/ask/stream`. The non-streaming `/ask` endpoint is not used by the
standard UI.

### 1.6 — Interrupt-Based Gates — Nine Steps, Two Nodes

The full sequence is §9.1; the binding structural rules are:

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

`AzureBlobCheckpointSaver` (`core/checkpointer.py`) implements
`BaseCheckpointSaver`; `AzureBlobStore` (`core/store.py`) implements
`BaseStore`. Blob layout: §10.4.

**Critical constraints:**
- One blob write per checkpoint (no per-key writes)
- Atomic via blob ETag conditional writes to handle concurrent turns
- `gate_attempts` in the checkpointed state (§10.1)

**Migration is a constructor and connection-string change**; run the
existing unit tests against PostgreSQL before switching.

**The Blob implementation is not safe for concurrent access** (no row-level
locking). Do not defend it past the migration trigger.

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
connect to a live system.** An architectural exclusion, not a deferral.

**`improve_evidence_index` is the only channel through which external,
real-world data enters AgentLean.** Consequences:

1. Coaching content must include guidance on **what data to upload and
   how to structure it**.
2. **There is no fallback path where the system fetches a number the
   Belt failed to provide.** Do not build one.

**Cross-agent tool sharing** (Agent Improve reading Agent Resolve's
indexes) happens via Python imports from shared modules, not via a
protocol. Those remain `@tool` functions, read-only.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §29.1, §29.2.*

