# Agent Improve — CLAUDE.md
# Version 2.1 — June 2026
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

---

## 1. ARCHITECTURE PRINCIPLES

### 1.1 — One State, One Runtime, One Source of Truth

- **One state**: `ImproveGraphState` (TypedDict) is the only mutable
  state object at the supervisor level. No parallel state in routes,
  no per-request manual dicts, no shadow state in the UI.
- **One runtime**: The compiled LangGraph supervisor is the orchestrator.
  Nothing in `gateway/routes.py` may dispatch nodes manually. If a
  route does anything beyond `await graph.ainvoke(...)` (or
  `astream_events(...)`) plus envelope marshalling, it is a violation.
- **One source of truth**: Azure Blob is the only persistence layer.
  Two distinct uses, both in Blob:
  - **Checkpoints**: `checkpoints/{case_id}/{checkpoint_id}.json` —
    in-flight graph state (see §1.7 and §8)
  - **Case records**: `cases/case_{id}.json` — completed-phase
    records, registry, files

### 1.2 — Hierarchical Subgraphs (A2)

The graph is hierarchical:

```
supervisor_graph
├── phase_router            (decides which subgraph to enter)
├── define_subgraph         (retrieve, coach, reflect?, validate, gate_interrupt)
├── measure_subgraph
├── analyse_subgraph
├── improve_subgraph
├── control_subgraph
└── escalation_subgraph
```

Each phase subgraph has its own internal state schema that inherits
from `ImproveGraphState`. Subgraphs may have any number of internal
nodes — the 11-node total cap of v1 is removed.

No subgraph imports from another subgraph's nodes. Cross-phase data
flows through the parent state only.

### 1.3 — Tool-Calling Coach (B2)

Inside each phase subgraph, the `coach_node` is a tool-calling agent.
The LLM has access to universal tools (see §5) and decides when to
call them. There is no separate `extract` step — extraction is a
tool call (`record_field`) the LLM makes as part of its response.

The graph structure is still explicit (subgraph nodes are not
collapsed into one giant agent). The agent pattern lives **inside**
the coach node. This is hybrid: deterministic graph flow, modern
tool-calling within nodes.

### 1.4 — Async by Default

- All FastAPI endpoints are `async def`
- All graph invocations use `await graph.ainvoke(...)` or
  `graph.astream_events(...)`
- All LLM calls use `await llm.ainvoke(...)`
- All Azure SDK calls use the `aio` variants where available

Synchronous code is permitted only in pure functions with no I/O
(prompt building, state transformations, validation logic).

### 1.5 — Streaming Responses (Q5a)

Coach responses stream to the UI via Server-Sent Events on
`/ask/stream`. The frontend renders tokens as they arrive. The
non-streaming `/ask` endpoint remains for clients that cannot use
SSE but is not used by the standard UI.

### 1.6 — Interrupt-Based Gate Approval (Q4c)

Gate submission uses LangGraph `interrupt()`:

1. User completes work products in coach loop
2. User clicks "Submit Gate" → frontend calls `/gate/submit`
3. Graph runs `validate_node`, then `interrupt()` pauses awaiting
   human confirmation
4. Frontend immediately calls `/gate/approve` (or `/gate/reject`)
5. Graph resumes, advances phase, returns

The interrupt is functionally instant on Submit. We use the
interrupt API for graph correctness; the UX feels like a normal
submit/response.

### 1.7 — Azure Blob Checkpointer

In-flight conversation state persists via a custom
`AzureBlobCheckpointSaver` implementing LangGraph's
`BaseCheckpointSaver` interface. Lives at
`core/checkpointer.py`.

**Blob layout for checkpoints**:
```
checkpoints/{case_id}/
  latest.json              — most recent checkpoint (for fast resume)
  history/{checkpoint_id}.json  — historical checkpoints for time-travel
```

**Critical constraints**:
- One blob write per checkpoint (no per-key writes)
- Atomic via blob ETag conditional writes to handle concurrent turns
- `gate_attempts` MUST be in the checkpointed state, never in route
  scope — this is what fixes the v1 "attempts always reset to 0" bug

The case blob (`cases/case_{id}.json`) is NOT touched mid-conversation.
It is the system of record for completed phases only (see §8).
Checkpointer and case blob are separate concerns serving different
lifecycles, both happening to live in the same Azure Storage account.

### 1.8 — LangSmith Tracing Mandatory

- `LANGCHAIN_TRACING_V2=true` is required in all environments
- Every LLM call must be traced
- Every tool call must be traced
- Every graph node must be a traceable span
- Token cost and latency are logged per node

Dead tracing config (the v1 state) is a CRITICAL violation.

---

## 2. WHERE CLASSES ARE ALLOWED

Classes are permitted ONLY in these files. The list expands the v1
list to reflect modern needs.

### State and schemas
- `core/state.py` — `ImproveGraphState` (TypedDict, total=False) — ONE only
- `core/substate.py` — Per-phase subgraph state TypedDicts (NEW)
- `phases/{phase}/schema.py` — `PhaseInput` and nested models (Pydantic v2)
- `storage/models.py` — `CaseDocument`, `PhaseRecord`, `RegistryEntry`
- `gateway/schemas.py` — API request/response envelopes (Pydantic v2)
- `core/citations.py` — `CitationRecord`, `CitationBundle`

### Modern additions
- `knowledge/tool_args.py` — Pydantic schemas for `@tool` `args_schema` (NEW)
- `core/checkpointer.py` — `AzureBlobCheckpointSaver(BaseCheckpointSaver)` (NEW)

All other files contain module-level functions ONLY. Especially:
- Graph builder files (`core/graph.py`, `phases/{phase}/graph.py`)
- LLM factory (`core/llm.py`)
- All node files (`phases/{phase}/nodes.py`)
- Blob client (`storage/blob.py`)
- Retriever (`knowledge/retriever.py`)
- Tool definitions (`knowledge/tools.py`)
- Escalation (`escalate.py`)
- Routes (`gateway/routes.py`)

---

## 3. GRAPH AND NODE RULES

### 3.1 — Graph structure

- One supervisor graph in `core/graph.py`
- One subgraph per phase in `phases/{phase}/graph.py`
- One escalation subgraph in `escalate.py`
- Supervisor compiles all subgraphs into a hierarchical compiled graph
- The compiled graph is the ONLY runtime path. `/ask`, `/ask/stream`,
  `/gate/*` all invoke the same compiled graph object.

### 3.2 — Node contract

Nodes are module-level async functions:

```python
async def coach_node(state: DefineSubState) -> dict:
    ...
    return {"chat_history": [...], "phase_inputs": {...}}
```

- File name and function name are aligned (one file per subgraph
  may contain multiple nodes — modern grouping pattern)
- Nodes return `dict` slices only — never Pydantic, never full state
- Nodes are async (no sync nodes — async-by-default rule)

### 3.3 — Per-phase subgraph nodes (the canonical structure)

Each phase subgraph contains exactly these nodes:

```
retrieve_node     — RAG injection (knowledge index)
coach_node        — tool-calling LLM with universal tools
reflect_node      — optional, conditional edge decides whether to run
validate_node     — gate readiness check
gate_interrupt    — interrupt() for human approval
```

NEW node types may not be added to a subgraph without an
ARCHITECTURE.md amendment.

### 3.4 — Reflection is a node, not a private function

`_reflect()` inside orchestrate files (the v1 pattern) is BANNED.

Reflection is a graph node (`reflect_node`) reached via a conditional
edge from `coach_node`. The edge decides whether reflection is needed
based on:
- Response length > threshold
- Detected risk keywords (numbers, commitments, dates)
- Phase-specific rules

This lets us turn reflection on/off via routing without commenting
out code anywhere.

### 3.5 — Escalation lives and runs

`escalate.py` defines the escalation subgraph. It is reachable via
conditional edge from any phase's `validate_node` when
`gate_attempts >= GATE_MAX_ATTEMPTS`.

`gate_attempts` is persisted in the checkpointed state, never in
route scope. The v1 bug where attempts reset to 0 every request is
fixed by construction in this architecture (the checkpointer holds
it across turns).

---

## 4. LLM RULES

### 4.1 — Factory only

Never instantiate `AzureChatOpenAI` directly. Always use:

```python
from core.llm import get_llm
llm = get_llm("coach", temperature=0.4, max_tokens=1500)
```

### 4.2 — Roles

Defined in `core/llm.py`. Current set:
- `intent` — short classification (gpt-4o-mini)
- `reasoning` — default reasoning (gpt-4o-mini)
- `coach` — coaching content (gpt-4o, max_tokens=1500)
- `extraction` — structured output (gpt-4o-mini, temp=0.0)
- `reflection` — response review (gpt-4o-mini, temp=0.0)
- `vision` — multimodal upload analysis (gpt-4o)

New roles require ARCHITECTURE.md amendment.

### 4.3 — Structured output via `with_structured_output`

When binding a Pydantic model, use:

```python
llm = get_llm("extraction").with_structured_output(MeasurePhaseInput)
```

Never parse JSON from raw text in node code. The structured output
binding is the only path.

### 4.4 — Fallbacks for production reliability

Coach calls use fallback chains:

```python
primary = get_llm("coach")
fallback = get_llm("reasoning", max_tokens=1500)
llm = primary.with_fallbacks([fallback])
```

---

## 5. TOOLS — UNIVERSAL TOOLSET (Q1a)

All coach nodes share the same toolset. Defined in `knowledge/tools.py`
with Pydantic arg schemas in `knowledge/tool_args.py`.

### 5.1 — Canonical tools

```
record_field(field_name: str, value: Any) -> str
  Writes a field to phase_inputs. Field must exist in current
  phase schema; otherwise tool errors.

search_methodology(query: str, top_k: int = 4) -> list[dict]
  Searches improve_knowledge_index. Returns BB methodology chunks.

search_evidence(query: str, top_k: int = 4) -> list[dict]
  Searches case-specific evidence index (uploaded files).

propose_template(template_type: str, fill_data: dict) -> str
  Generates a fill-in template for the team to complete.
  Types: problem_statement, sipoc, data_collection_plan, fishbone, etc.

propose_diagram(diagram_type: str, data: dict) -> dict
  Returns structured diagram JSON (NOT SVG). Diagram types and
  schemas defined in core/diagrams.py. Frontend renders via SVG
  template library. This is the Q2b decision.

check_gate_status() -> dict
  Returns current phase gate readiness — which required fields are
  populated, which are missing.

request_human_approval(reason: str) -> str
  Triggers an interrupt awaiting human decision. Used in interrupt
  flows beyond standard gate submission (e.g. sensitive decisions).
```

### 5.2 — Tool binding

The coach LLM in each phase is bound to all 7 tools via
`llm.bind_tools([...])`. Tool decisions are the LLM's, not the
graph's.

### 5.3 — Tool args via Pydantic schemas

Every `@tool` uses `args_schema=` with a Pydantic model from
`knowledge/tool_args.py`. No tools with raw signature inference.

---

## 6. PROMPTS

### 6.1 — Constants in `core/prompts.py`

All prompts live as constants in `core/prompts.py`. Prompt strings
are never inline in node files.

### 6.2 — Prompt naming

- `{PHASE}_COACH_PROMPT` — coach node system prompt
- `{PHASE}_REFLECT_PROMPT` — reflect node prompt
- `KNOWLEDGE_INJECTION_TEMPLATE` — wraps RAG results when injected

The old `ORCHESTRATOR_{PHASE}_CONTEXT` and `EXTRACTION_{PHASE}`
patterns are deleted. Extraction is via tool call now, not a
separate prompt.

---

## 7. RAG

### 7.1 — RAG via tool, not via prepended system message

The v1 pattern (`build_knowledge_context()` injected as a SystemMessage)
is DELETED. RAG is invoked by the LLM via `search_methodology` tool
when it decides retrieval is needed.

This makes RAG accountable in the trace, lets the LLM control when
to retrieve, and removes the always-on retrieval cost.

### 7.2 — Knowledge index

`improve_knowledge_index` — DMAIC methodology, BB content. Fields:
`content`, `content_vector`, `metadata`, `source_file`, `phase_relevance`.
Hybrid search via `AzureSearch` with LangChain defaults.

### 7.3 — Evidence index

`improve_evidence_index` — case-specific uploaded documents.
Filtered by `case_id`. Available via `search_evidence` tool.

---

## 8. STORAGE

### 8.1 — All persistence in Azure Blob, two distinct concerns

**Concern 1: Checkpoints (in-flight graph state)**
- Path: `checkpoints/{case_id}/latest.json` + `checkpoints/{case_id}/history/{id}.json`
- Written: by `AzureBlobCheckpointSaver` after every graph node
- Read: by graph on resume, by debugger for time-travel
- Owner: `core/checkpointer.py`

**Concern 2: Case records (system of record)**
- Path: `cases/case_{id}.json`, `registry.json`, `uploads/{case_id}/{file}`
- Written: on case create, on gate pass, on file upload — never mid-conversation
- Read: by `/cases/{id}` endpoint, by gate document UI, by registry
- Owner: `storage/blob.py` via `ImproveBlobClient`

Same Azure Storage account, separate concerns, separate code paths.

### 8.2 — What does NOT get written mid-conversation

The case blob is NOT updated per turn. The v1 pattern of overwriting
`case_{id}.json` on every `/ask` is REMOVED. Conversation history
lives in the checkpoint until gate pass; on gate pass, the relevant
slice is committed to the case blob.

### 8.3 — Case-vs-registry atomicity

Gate-pass case blob write and registry update remain two separate
writes. Acceptable risk for now. Roadmap: wrap in a saga pattern
when scale requires.

---

## 9. TRACING AND OBSERVABILITY

### 9.1 — LangSmith required

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=agentlean-improve
```

Production environments without LangSmith fail startup with a
clear error.

### 9.2 — What gets traced

- Every graph invocation (full graph as parent span)
- Every node execution (child span per node)
- Every LLM call (with prompt, response, token counts, cost)
- Every tool call (with arguments and result)
- Every retrieval (with query and top-k results)

### 9.3 — Logs

Structured logs via `logging`. Every request gets a `request_id`.
Every node logs entry, exit, and any state-slice keys it returned.

---

## 10. UI AND LANGUAGE RULES (preserved from v1)

- No methodology jargon in any team-facing string — plain language always
- Technical terms appear only as small secondary grey labels
- Every AI data request must include a concrete example with column names
- Every AI suggestion using cross-agent data must include a visible
  source citation
- Citation format: agent_origin, index_name, document_id, relevance_summary

---

## 11. NO-GO LIST (updated)

- Never instantiate `AzureChatOpenAI` directly
- Never create a second `TypedDict` for state at the same level (subgraph
  substates inheriting are permitted)
- Never put prompts inline in node files
- Never write to Agent Resolve indexes — read only via tools
- Never duplicate `CitationRecord`
- Never add a graph node type without ARCHITECTURE.md amendment
- Never add classes outside the designated files in §2
- Never dispatch nodes manually in routes — always via the compiled graph
- Never call `_reflect()` as a private function — reflection is a node
- Never bypass `get_llm()` factory
- Never parse JSON from raw LLM text — use `with_structured_output`
- Never write to the case blob mid-conversation — only at lifecycle events
- Never write checkpoints to the case blob path — separate paths only
- Never disable LangSmith tracing
- Never use methodology jargon in team-facing strings

---

## 12. PROMPT SIZE MANAGEMENT (preserved from v1)

When a UI change touches more than 3 functions or adds more than ~150
lines of new code, split into multiple focused prompts. Never include
more than 2 full function replacements per prompt for `index.html`.

---

## 13. MIGRATION FROM v1 ARCHITECTURE

This document describes the **target** architecture (Path C end-state).

The migration follows ARCHITECTURE.md §15 — a defined sequence of
refactor commits. Until migration is complete, the v1 architecture
may still operate, but no v1-style code may be ADDED. All new code
must conform to v2 rules.

A file is "migrated" when it is rewritten under v2 rules and committed
with a `refactor(arch-v2):` prefix.

---

## 14. AMENDMENT PROCEDURE

This file is amended only via:

1. A new architectural decision documented in ARCHITECTURE.md
2. A commit to CLAUDE.md updating the relevant rule
3. Increment to the version number at the top
4. Change entry in ARCHITECTURE.md change log

Never amend a rule "in passing" while making a feature change.
Architecture changes are separate commits.
