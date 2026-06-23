# Agent Improve — Architecture & Design Document
**Agentlean Platform · DMAIC Improvement Agent**
Version 2.1.1 · June 2026
Status: v2.1 architecture defined · migration not yet started

---

## 1. Overview

Agent Improve is the second agent in the Agentlean platform. It guides
cross-functional teams through structured DMAIC (Define, Measure,
Analyse, Improve, Control) Lean Six Sigma improvement projects.

**Core principle**: Agent Improve must work for a team with no Six
Sigma qualification. The AI guides every step in plain language. No
methodology jargon reaches the user unless they ask.

**Architectural principle (v2.1)**: One state, one runtime, one source
of truth. The LangGraph compiled graph IS the orchestrator. Routes are
thin transport. Persistence is Blob via two distinct concerns.

| Property | Value |
|---|---|
| Backend port | 8020 |
| Repo | `vpangalis/agentlean` → `agent-improve/` |
| Stack | Python 3.11 · FastAPI · LangGraph 0.2+ · Azure OpenAI · Azure AI Search · Azure Blob |
| LangChain Version | 0.3+ (tool-calling, structured output, async) |
| Persistence | Azure Blob — checkpoints + case records (separate paths) |
| Tracing | LangSmith (mandatory) |

---

## 2. Design Principles

### 2.1 Plain language first
The AI translates Six Sigma into plain English. Technical terms are
hidden until explicitly requested.

### 2.2 Every data request comes with a collection guide
When the coach asks for data it explains what, how, and shows a
concrete example.

### 2.3 Source citation is mandatory and transparent
Every AI suggestion carries: `agent_origin`, `index_name`,
`document_id`, `relevance_summary`.

### 2.4 Phase gates are one-way doors
Once a gate passes and the phase record commits to the case blob,
that phase is locked.

### 2.5 Multiple parallel cases from day one
Each case has its own `IMPR-YYYY-NNN` id, its own checkpoint thread,
its own case blob, its own state.

### 2.6 The graph is the orchestrator (v2.1 NEW)
Routes do not orchestrate. Routes invoke the compiled graph. All
dispatch, conditional logic, gating, and escalation live inside the
graph.

---

## 3. Agent Architecture

### 3.1 Hierarchical subgraph composition

```
supervisor_graph
├── phase_router            (1 node — routes by current_phase)
├── define_subgraph         (5 nodes)
├── measure_subgraph        (5 nodes)
├── analyse_subgraph        (5 nodes)
├── improve_subgraph        (5 nodes)
├── control_subgraph        (5 nodes)
└── escalation_subgraph     (1 node)
```

Each phase subgraph has the canonical 5-node structure:

```
retrieve_node     → coach_node → reflect_node? → validate_node → gate_interrupt
                                       ↑                              │
                                       └──────────loop───────────────┘
```

The `reflect_node?` indicates a conditional edge — reflection runs
only when triggered by content rules.

### 3.2 Inside coach_node — tool-calling agent

The coach LLM is bound to seven universal tools (CLAUDE.md §5).
The LLM decides which tools to call. Tool calls:

- `record_field(field_name, value)` — writes to phase_inputs
- `search_methodology(query, top_k)` — RAG against knowledge index
- `search_evidence(query, top_k)` — RAG against case evidence
- `propose_template(template_type, fill_data)` — coaching template
- `propose_diagram(diagram_type, data)` — diagram JSON for UI
- `check_gate_status()` — gate readiness check
- `request_human_approval(reason)` — out-of-band interrupt

The coach is a true ReAct agent within the constrained scope of a
single phase node.

### 3.3 Reflection — conditional node

`reflect_node` is reached via a conditional edge from `coach_node`.
Routing rule:

```python
def should_reflect(state):
    last_response = state["chat_history"][-1]["content"]
    if len(last_response) > 800:
        return "reflect"
    if contains_numeric_commitment(last_response):
        return "reflect"
    if state.get("force_reflect"):
        return "reflect"
    return "validate"
```

Turning reflection on/off requires no code change — just a routing
edit.

### 3.4 Escalation — its own subgraph

`escalation_subgraph` is entered when any phase's `validate_node`
sees `gate_attempts >= GATE_MAX_ATTEMPTS`. The subgraph:

1. Calls escalation LLM to produce a structured "stuck" report
2. Sets `escalated=True` in checkpointed state
3. Routes to END (graph terminates this turn)

The frontend reads `escalated` and renders the escalation banner.

### 3.5 Interrupt-based gates

`gate_interrupt` is a node that calls LangGraph `interrupt()`. The
graph pauses with `validate_node`'s output as the interrupt payload.

Frontend flow:
1. User clicks **Submit Gate** → `POST /gate/submit`
2. Backend resumes graph from coach checkpoint, runs through
   `validate_node` → `gate_interrupt`
3. Interrupt fires with payload `{passed: bool, checks: [...]}`
4. Response returned to frontend
5. If passed, frontend immediately calls `POST /gate/approve`
6. Backend resumes from interrupt with approval, graph advances
   phase, persists to case blob, returns

User experience: instant. Architecture: properly interrupt-based.

---

## 4. State Model

### 4.1 ImproveGraphState (supervisor level)

`core/state.py` — TypedDict (total=False)

| Field | Type | Purpose |
|---|---|---|
| case_id | str | The case in flight |
| current_phase | str | define / measure / analyse / improve / control |
| current_user | str | Active team member |
| phase_inputs | dict | Per-phase structured field captures |
| chat_history | list[dict] | role, content, timestamp, tool_calls |
| gate_attempts | int | Per-phase counter, persisted via checkpoint |
| escalated | bool | Set by escalation subgraph |
| citations | list[dict] | Per-session citation accumulator |
| uploaded_files | list[dict] | name, classification, phase, blob path |
| case_metadata | dict | title, belt_level, leader, team |
| pending_interrupt | dict \| None | Active interrupt payload if any |

### 4.2 Phase substates (subgraph level)

`core/substate.py` — one TypedDict per phase, inheriting from
`ImproveGraphState`. Each adds phase-specific transient fields
(e.g. `define.sipoc_draft`, `analyse.fishbone_in_progress`).

### 4.3 Persistence boundary

- **Checkpointed (graph-managed)**: full state above, every node
  transition
- **Persisted to case blob (lifecycle-managed)**: on gate pass —
  `phase_inputs[phase]` → `case.phases[phase].structured`;
  `chat_history` slice for that phase → `case.phases[phase].conversation`

---

## 5. Folder Structure (v2.1 target)

```
agent-improve/
backend/
  app.py                          FastAPI app, lifespan management
  core/
    state.py                      ImproveGraphState
    substate.py                   Per-phase substates (NEW)
    graph.py                      Supervisor graph compilation
    llm.py                        get_llm() factory
    checkpointer.py               AzureBlobCheckpointSaver (NEW)
    config.py                     Settings
    prompts.py                    All prompt constants
    citations.py                  Citation models
    diagrams.py                   Diagram type schemas (NEW)
    tracing.py                    LangSmith integration (NEW)
  phases/
    define/
      graph.py                    Subgraph compilation
      nodes.py                    retrieve, coach, reflect, validate
      gate.py                     gate_interrupt node
      schema.py                   DefinePhaseInput
    measure/  (same shape)
    analyse_phase/  (same shape)
    improve/  (same shape)
    control/  (same shape)
  knowledge/
    retriever.py                  AzureSearch clients
    tools.py                      Universal coach tools
    tool_args.py                  Pydantic arg schemas (NEW)
  storage/
    blob.py                       Case blob CRUD (lifecycle only)
    models.py                     CaseDocument, PhaseRecord, etc
  gateway/
    routes.py                     Thin transport: invoke graph
    schemas.py                    API envelopes
    sse.py                        SSE streaming (NEW)
  escalate.py                     Escalation subgraph
  upload/
    agent.py
    classifier.py
ui/
  index.html
CLAUDE.md
ARCHITECTURE.md
requirements.txt
```

Major v1 → v2.1 changes:
- Each phase grows from 4 files to 4 files but with different content
- `core/checkpointer.py`, `core/diagrams.py`, `core/tracing.py`,
  `core/substate.py`, `knowledge/tool_args.py`, `gateway/sse.py` are
  new
- `phases/{phase}/orchestrate.py` and `validate.py` are deleted —
  replaced by `nodes.py` and `gate.py`
- `phases/{phase}/analyse.py` (the 2-line vestigial stub) is deleted

---

## 6. Storage

### 6.1 Two concerns, one Azure Storage account

**Concern A — Checkpoints (in-flight)**
- Container: `agent-improve-cases` (existing)
- Prefix: `checkpoints/{case_id}/`
- Files: `latest.json` (active) + `history/{checkpoint_id}.json`
- Owner: `core/checkpointer.py` → `AzureBlobCheckpointSaver`
- Lifecycle: written by graph after every node, read on resume

**Concern B — Case records (durable)**
- Container: `agent-improve-cases` (existing)
- Prefix: `cases/`
- Files: `case_{id}.json` (full case), `registry.json` (index)
- Owner: `storage/blob.py` → `ImproveBlobClient`
- Lifecycle: written on create, gate pass, upload — not per turn

### 6.1.1 On-blob format

Each checkpoint blob (both `latest.json` and
`history/{id}.json`) is a JSON document with this envelope:

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
`JsonPlusSerializer.dumps_typed()` (LangGraph
`langgraph-checkpoint` 4.x) returns binary msgpack rather
than utf-8 text. Wrapping the bytes in base64 keeps the
blob a valid JSON document while preserving exact
round-trip semantics.

### 6.2 Why blob and not Cosmos / Tables / SQLite

- Already provisioned, already secured, already monitored
- Single Azure SDK dependency (no new service to deploy)
- Append-only checkpoint history → simple time-travel debugging
- LangGraph `BaseCheckpointSaver` interface lets us swap to Cosmos
  later if scale requires, with no other code changes

### 6.3 Concurrency

Checkpoint writes use blob ETag conditional writes. Concurrent turns
on the same case are detected and the second turn retries. Case
blob writes are non-concurrent (gate pass is rare, single-user).

---

## 7. Azure AI Search Indexes (unchanged from v1)

### Active
| Index | Content | Used by |
|---|---|---|
| `improve_knowledge_index` | DMAIC methodology, BB content | `search_methodology` tool |
| `improve_evidence_index` | Uploaded case evidence | `search_evidence` tool |

### Cross-agent read-only (Agent Resolve, future)
| Index | Tool |
|---|---|
| `case_index_v3` | `search_resolve_cases` |
| `knowledge_index_v2` | `search_resolve_knowledge` |
| `evidence_index_v1` | `search_resolve_evidence` |

### Out of scope for refactor
| Index | Status |
|---|---|
| `improve_case_index` | Indexed on gate pass, queried on demand (existing) |
| `vsm_index` etc | Agent Flow, not built |

---

## 8. API Surface (v2.1)

| Endpoint | Method | Purpose |
|---|---|---|
| `/health` | GET | Liveness |
| `/cases` | POST | Create case |
| `/cases/{id}` | GET | Full case document |
| `/registry` | GET | Case list |
| `/ask` | POST | Non-streaming turn (legacy clients) |
| `/ask/stream` | POST | SSE streaming turn (primary) |
| `/gate/submit` | POST | Submit current phase for review |
| `/gate/approve` | POST | Resume from gate interrupt with approval |
| `/gate/reject` | POST | Resume from gate interrupt with rejection |
| `/upload` | POST | File upload to evidence |
| `/files/{case_id}/{file_id}` | DELETE | Remove uploaded file |
| `/context` | POST | Re-entry greeting (preserved for now) |
| `/summarise` | POST | Session summary (preserved for now) |

All endpoints are `async def`. All return Pydantic models from
`gateway/schemas.py`.

---

## 9. UI Architecture (unchanged structurally; some integration changes)

The UI structure (4 screens, 5 tabs per phase) is preserved. Two
integration changes:

### 9.1 Streaming chat (`/ask/stream`)
The AI Guide tab connects to `/ask/stream` via EventSource and renders
tokens as they arrive. Replaces the current 16-22s wait.

### 9.2 Gate interrupt flow
The Gate tab's Submit button calls `/gate/submit`, then immediately
`/gate/approve` (or `/gate/reject` if validation failed). The
interrupt payload drives the gate result panel.

UI files (`index.html`) split into modules is a separate roadmap
item; for now the file stays monolithic.

---

## 10. Tracing and Observability

### 10.1 LangSmith integration

`core/tracing.py` initialises tracing at app startup:
- Sets `LANGCHAIN_TRACING_V2=true`
- Sets `LANGCHAIN_API_KEY` from settings
- Sets `LANGCHAIN_PROJECT=agentlean-improve` (configurable)

If LangSmith credentials are missing in production, app fails
startup with a clear error.

### 10.2 What's traced

- Every `graph.ainvoke` call → top-level trace
- Every node → child span with input/output state slices
- Every LLM call → token cost, latency, model name
- Every tool call → args, result, duration
- Every retrieval → query, top-k, scores

### 10.3 Logs

Structured logs via `logging.Logger`. Every request gets a
`request_id` (UUID4), propagated to all child operations. Logs
include `request_id`, `case_id`, `phase`, `node_name`, `duration_ms`.

---

## 11. Phase Gate Requirements (mostly preserved from v1)

| Phase | Required for gate (3-4 fields each, see schema) |
|---|---|
| Define | problem statement, primary metric, target, process owner, SIPOC |
| Measure | metric confirmed, data collection plan, baseline data, sigma |
| Analyse | ≥3 causes, vital few, cause verified, root cause statement |
| Improve | selected solution, pilot result, improvement confirmed |
| Control | control plan, monitoring method, sustainability confirmed |

Detailed schemas in `phases/{phase}/schema.py`. Gate validators
in `phases/{phase}/nodes.py` (validate_node).

---

## 12. Out of Scope (v2.1 refactor)

- Agent Flow build-out
- Cosmos DB migration (Blob suffices)
- Tool-calling for cross-agent search (`search_resolve_*` stays as a
  no-op tool until Agent Resolve integration is wired)
- LangChain Hub for prompts (deferred indefinitely)
- Mobile UI

---

## 13. Decisions Resolved (v2.1)

| Decision | Resolution |
|---|---|
| Graph topology | Hierarchical subgraphs (Option A2) |
| Coach pattern | Tool-calling agent inside explicit node (Option B2) |
| Checkpointer backend | Azure Blob via custom `BaseCheckpointSaver` |
| Gate flow | Interrupt-based, triggered on user Submit (Q4c) |
| Streaming | SSE via `/ask/stream` (Q5a) |
| Tools per phase | Universal toolset, ~7 tools (Q1a) |
| Diagram generation | LLM emits JSON, frontend renders SVG from templates (Q2b) |
| Prompt management | Constants in `core/prompts.py` (no Hub migration) |

---

## 14. Out-of-band Roadmap Items (for future versions)

These are explicit decisions to DEFER, not silent gaps:

- LangChain Hub prompt versioning
- Cosmos DB checkpointer (swap when scale needs it)
- Tool-calling for cross-agent search
- Saga pattern for case-vs-registry atomicity
- index.html modularisation
- Human-in-the-loop interrupts beyond gate (sponsor approvals etc)
- Cost & latency dashboards

---

## 15. Migration Sequence — v1 → v2.1

The refactor proceeds in this strict order. Each step is one commit
with prefix `refactor(arch-v2):`. Each step must compile, tests pass,
existing demo case (IMPR-2026-E9D) loads, before next step begins.

### Step 0 — Foundation
**Commit 0.1**: Save CLAUDE.md v2.1 + ARCHITECTURE.md v2.1 to repo.
No code changes. Establishes the constitution.

### Step 1 — Tracing first (so we can debug the rest)
**Commit 1.1**: `core/tracing.py` — initialise LangSmith at startup.
Wire `LANGCHAIN_TRACING_V2=true`. Update `.env.example`. App fails
startup in production if credentials missing.

**Commit 1.2**: Add `request_id` middleware. Structured logging.

### Step 2 — Checkpointer
**Commit 2.1**: `core/checkpointer.py` — `AzureBlobCheckpointSaver`
implementing `BaseCheckpointSaver`. Write/read/list to blob via
`checkpoints/{case_id}/` paths. Unit tests with mock blob client.

**Commit 2.2**: Wire checkpointer into graph compilation. Graph
still uses v1 node structure for now — only persistence changes.

### Step 3 — Universal toolset
**Commit 3.1**: `knowledge/tool_args.py` — Pydantic arg schemas for
all 7 tools.

**Commit 3.2**: `knowledge/tools.py` — define all 7 tools with
`@tool(args_schema=...)`. `record_field`, `search_methodology`,
`search_evidence`, `propose_template`, `propose_diagram`,
`check_gate_status`, `request_human_approval`.

**Commit 3.3**: `core/diagrams.py` — diagram type schemas (Pydantic
models for fishbone, SIPOC, pareto, impact-effort, control chart).

### Step 4 — Phase subgraph migration (one phase at a time, Define first)
**Commit 4.1**: `core/substate.py` — DefineSubState, MeasureSubState,
AnalyseSubState, ImproveSubState, ControlSubState.

**Commit 4.2**: Migrate Define phase
- New `phases/define/nodes.py` (retrieve, coach, reflect, validate)
- New `phases/define/gate.py` (gate_interrupt)
- New `phases/define/graph.py` (subgraph compilation)
- Delete old `phases/define/orchestrate.py`, `validate.py`,
  `analyse.py`
- New `DEFINE_COACH_PROMPT`, `DEFINE_REFLECT_PROMPT` in prompts.py
- Delete `ORCHESTRATOR_DEFINE_CONTEXT`, `EXTRACTION_DEFINE`

**Commits 4.3 → 4.6**: Same migration for Measure, Analyse, Improve,
Control. One commit per phase, each independently verifiable.

### Step 5 — Supervisor and routing
**Commit 5.1**: New `core/graph.py` — supervisor graph composing
phase subgraphs + escalation subgraph. Replaces v1 graph.py
entirely.

**Commit 5.2**: New `escalate.py` — escalation subgraph (was a
single node, now a subgraph of 1-2 nodes for trace clarity).

### Step 6 — Routes refactor (the big simplification)
**Commit 6.1**: Rewrite `gateway/routes.py`. Each endpoint becomes
a few lines: load case meta, invoke graph, format response. All v1
manual orchestration is deleted.

**Commit 6.2**: New `/ask/stream` SSE endpoint. New `gateway/sse.py`
for the SSE plumbing.

**Commit 6.3**: New `/gate/submit`, `/gate/approve`, `/gate/reject`
endpoints replacing the v1 `/gate`.

### Step 7 — UI integration
**Commit 7.1**: AI Guide tab — connect to `/ask/stream`. Render
streaming tokens. (Tests against the working backend from step 6.)

**Commit 7.2**: Gate tab — submit/approve flow against new endpoints.

**Commit 7.3**: Diagram rendering — frontend SVG templates that
consume diagram JSON from `propose_diagram` tool results. One
template per diagram type.

### Step 8 — Cleanup
**Commit 8.1**: Delete all v1 code that hasn't already been removed.
Verify no dead imports.

**Commit 8.2**: Update CLAUDE.md migration section to mark v1 → v2.1
complete.

### Step 9 — End-to-end validation
**Commit 9.1**: Run IMPR-2026-E9D end-to-end on v2.1. Confirm all
phases work with the new architecture. Document any deltas in
behaviour.

**Commit 9.2**: Create financial services demo case
(IMPR-2026-FS1). Run end-to-end as the showcase.

---

## 16. Change Log

| Date | Version | Change |
|---|---|---|
| May 2026 | 0.1 | Initial scaffold |
| Jun 2026 | 0.2 | Define + Measure complete |
| Jun 2026 | 1.0 | Analyse + Improve + Control complete. v1 architecture in production. |
| Jun 2026 | 2.0 | DRAFT — Path C architecture proposed |
| Jun 2026 | 2.1 | Path C ratified: hierarchical subgraphs, tool-calling coach, Azure Blob checkpointer, interrupt-based gates, SSE streaming, LangSmith mandatory. |
| Jun 2026 | 2.1.1 | ARCHITECTURE.md amendment: §6.1.1 documents the base64 envelope for checkpoint blobs (deviation from initial spec, surfaced during commit 2.1 implementation). |
