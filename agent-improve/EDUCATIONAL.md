# EDUCATIONAL.md — LangGraph & Multi-Agent Systems
## AgentLean Learning Register

*Captured from active learning sessions. To be committed to `vpangalis/agentlean` repo root.*
*Last updated: June 2026*

---

## Purpose

This document records concepts learned during development and coursework that are **not yet implemented** in AgentLean but will be needed during the post-completion refactor and production migration. It serves as a bridge between learning and implementation.

---

## Document Navigation — Topic Groups

*This index groups the existing sections by theme without moving them. Section numbers remain unchanged so all cross-references in the document continue to work. Use this index to find related content across the document.*

### A. Foundations — State, Persistence, Interrupts
- Section 1 — LangGraph Persistent Checkpointing (`@traceable`, fail-fast validation, diagnostic patterns added)
- Section 2 — Human-in-the-Loop (Interrupts)
- Section 10 — State Management Patterns
- Section 44 — Architectural Diagnosis and Refactor Blueprint
- Section 52 — Checkpointer + BaseStore Split (LangGraph 2026 memory architecture)
- Section 53 — HumanInTheLoopMiddleware, Command(resume=...)
- Section 79 — **LangGraph 1.2 Native Reliability Primitives** (per-node timeouts, error handlers, DeltaChannel)
- Section 81 — **LangChain 1.0 Standard Content Blocks** (typed model responses)

### B. Orchestration and Multi-Agent Patterns
- Section 5 — Planner/Executor Pattern
- Section 11 — Phase Planner and Phase Executor
- Section 17 — Recursive Orchestrator Pattern
- Section 22 — Debate Agents and Consensus Voting
- Section 43 — Coordinator / Worker / Decision Agent Roles
- Section 44 — Full architecture refactor blueprint
- Section 70 — Inter-Stage Data Dependency (outputs become inputs)
- Section 80 — **LangChain 1.0 AgentMiddleware Six Hooks Foundation**
- Section 82 — **LangChain 1.0 ProviderStrategy** (native structured output)
- Section 84 — **SkillsMiddleware** (solves system prompt bloat)

### C. Reasoning, Reflection, and Correction
- Section 28 — Multi-Query Retrieval (parallel variants)
- Section 29 — OutputFixingParser (format correction)
- Section 42 — RubricMiddleware (subjective quality evaluation, temperature discipline)
- Section 48 — Reflection Nodes + Three-Prompt Separation + DMAICGateValidator
- Section 51 — InsightForge Self-Correcting Pipeline (`parse_with_retry`)
- Section 54 — RubricMiddleware June 2026 documentation confirmation
- Section 68 — Decision Validation Against Business Constraints
- Section 69 — Validation Layer Placement Across Agent Improve
- Section 71 — Multi-Hop Retrieval (Gap 17 CLOSED)

### D. Reliability, Recovery, and Failure Handling
- Section 20 — Fallback Chains
- Section 49 — Saga Pattern and Compensating Actions (**UPDATED by Section 79 — now use native `error_handler=`**)
- Section 64 — MCP Production Architecture (structured errors, circuit breaker foundations)
- Section 66 — Circuit Breaker, Context Recovery, Safe Reopen, Six-Step Failure Pipeline
- Section 67 — Complete Self-Healing Reference Implementation + Agent Improve Exception Mapping
- Section 79 — **LangGraph 1.2 Native Reliability Primitives** (also Category A)

### E. MCP — Model Context Protocol
- Section 39, 57–63 — MCP fundamentals, transport, host/client/server model, AgentLean MCP scope
- Section 60 — Internal @tool vs MCP tools (boundary rules)
- Section 61 — MCP Resources
- Section 62 — Third-Party MCP Servers (Microsoft Azure MCP Server)
- Section 63 — AgentLean MCP Server Design and Scope
- Section 64 — Production MCP Architecture Principles + 2026-07-28 spec verification
- Section 65 — MCP Caching (tool list + result caching, in-process → Redis progression)

### F. Deployment, Versioning, and Infrastructure
- Section 55 — LangServe Archived, LangGraph Server Replacement
- Section 56 — Course Stale Deployment Warning
- Section 72 — LangGraph Server Deployment Option for AgentLean
- Section 73 — Langfuse (open-source LangSmith alternative)
- Section 74 — API Versioning (framework-agnostic patterns for v2.1 refactor)
- Section 75 — Evaluation Dataset Design and Regression Testing
- Section 76 — Docker Containerisation for AgentLean
- Section 85 — **LangSmith 2026 Additions** (Fleet, Sandboxes, Context Hub, Engine)

### G. Frontend and User Experience
- Section 77 — AgentLean Frontend Feedback Requirements (six UI patterns)

### H. Governance, Skills, Hooks, and Anti-Drift
- Section 24 — Observer Agent Role
- Section 26 — Skills and Hooks Governance Framework (**UPDATED by Section 83 — now follows agentskills.io spec**)
- Section 27 — Gap 27 (`/verify-current-version` skill)
- Section 45 — Three-Layer Governance System
- Section 50 — Anti-Drift Mechanisms
- Section 78 — Menu-Driven Developer Orchestration (replaces destructive `start.ps1`)
- Section 83 — **Agent Skills Specification** (SKILL.md standard)
- Section 84 — **SkillsMiddleware** (also Category B)

### I. Course-Specific Concepts (Framework-Agnostic Foundations)
- Section 25 — Actor-Critic Pattern (RL conceptual foundation, not directly implemented)
- Section 25a — LangGraph 2026 Memory Architecture (Checkpointer + BaseStore split)
- Section 25b — `create_agent` replacing `create_react_agent`

---

## Overview Architecture — Agent Improve v2.1 Target

*Graphical view of how all the concepts in this document connect for the Agent Improve v2.1 refactor. Section numbers reference where each concept is documented in detail.*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Section 77)                              │
│  Six UI feedback patterns: spinner, status, extracted fields, completeness  │
│  score, LangSmith trace link, completion confirmation                       │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ HTTP / SSE
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                    API LAYER — Choice for v2.1 (Section 72)                 │
│  Option A: FastAPI (current, custom control, data stays in Azure)           │
│  Option B: LangGraph Server (built-in HITL, thread mgmt, Studio)            │
│  Versioning: /v1 (current) + /v2 (refactored) parallel (Section 74)         │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│                  ORCHESTRATOR — Recursive Pattern (Section 17, 44)          │
│                                                                             │
│    Reads gate_passed[] → routes to next unfinished phase                    │
│    Delegates via LangGraph Command (Section 44)                             │
│    NEVER does the work itself — only routes and inspects state              │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
       ┌───────────────┬───────────┼───────────┬───────────┐
       │               │           │           │           │
┌──────▼─────┐ ┌──────▼─────┐ ┌───▼─────┐ ┌──▼──────┐ ┌───▼──────┐
│  DEFINE    │ │  MEASURE   │ │ ANALYSE │ │ IMPROVE │ │ CONTROL  │
│  Subgraph  │ │  Subgraph  │ │ Subgraph│ │Subgraph │ │ Subgraph │
│(Section 44)│ │(Section 44)│ │  (44)   │ │  (44)   │ │  (44)    │
└──────┬─────┘ └──────┬─────┘ └────┬────┘ └────┬────┘ └────┬─────┘
       │              │            │           │           │
       └──────────────┴────────────┴───────────┴───────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │   Each Phase Subgraph:      │
                    │  ┌───────────────────────┐  │
                    │  │ Phase Planner (S. 11) │  │
                    │  │ decides next action + │  │
                    │  │ retrieval_strategy    │  │
                    │  └──────────┬────────────┘  │
                    │             │               │
                    │  ┌──────────▼────────────┐  │
                    │  │ Phase Executor (S.11) │  │
                    │  │ TAO loop with tools   │  │
                    │  │ (create_agent S.25b)  │  │
                    │  └──────────┬────────────┘  │
                    │             │               │
                    │  ┌──────────▼────────────┐  │
                    │  │ Coherence Check (S.69)│  │
                    │  │ every turn, silent    │  │
                    │  └──────────┬────────────┘  │
                    │             │               │
                    │  ┌──────────▼────────────┐  │
                    │  │ At Gate Boundary:     │  │
                    │  │ 1. Field Presence(48) │  │
                    │  │ 2. Constraint Val(68) │  │
                    │  │ 3. Rubric Grader (42) │  │
                    │  │ 4. HITL Review (53)   │  │
                    │  └───────────────────────┘  │
                    └──────────────┬──────────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │                           │                           │
┌──────▼──────────┐   ┌────────────▼──────────┐   ┌───────────▼──────────┐
│  STATE LAYER    │   │   TOOL LAYER          │   │  OBSERVABILITY       │
│                 │   │                       │   │                      │
│  Checkpointer   │   │  Internal @tool       │   │  LangSmith           │
│  (Section 1,52) │   │  (Section 60)         │   │  (Section 1, 73, 75) │
│  PostgresSaver  │   │  extract_fields,      │   │  @traceable on       │
│                 │   │  validate_gate,       │   │  custom functions    │
│  BaseStore      │   │  check_completeness   │   │                      │
│  (Section 52)   │   │                       │   │  Evaluation datasets │
│  cross-session  │   │  MCP Client → Server  │   │  (Section 75)        │
│  memory         │   │  (Section 63, 64, 65) │   │  regression testing  │
│                 │   │  search_knowledge     │   │                      │
│  Typed Pydantic │   │  search_cases         │   │  P50/P99 diagnostic  │
│  boundaries     │   │  (result caching)     │   │  (Section 1)         │
│  (Section 44)   │   │                       │   │                      │
└─────────────────┘   └───────────────────────┘   └──────────────────────┘

RELIABILITY WRAPPING (Sections 66, 67) — Applied to LLM + MCP layers:
  Circuit Breaker + Exponential/Jittered Backoff + Structured Error Schema +
  Fallback Chain (gpt-4o → gpt-4o-mini → cached → degraded)
```

### How the Numbered Concepts Connect

The refactor sequence is not arbitrary — dependencies flow through this diagram:

```
State foundations (S.1, 52) must exist before
  → subgraph structure (S.44) can be wired, which enables
    → phase planner/executor pattern (S.11) to have context, which enables
      → validation stack (S.48, 68, 69) to run at correct boundaries, which enables
        → HITL gates (S.2, 53) to actually pause execution, which enables
          → gate quality evaluation (S.42, 54) to fire only at right moments, which enables
            → multi-hop retrieval (S.71) to serve coaching not gates, which requires
              → MCP server (S.63, 64, 65) for knowledge access, wrapped in
                → failure handling (S.66, 67) for production reliability, observed via
                  → LangSmith (S.1, 75) with @traceable on custom functions,
                     versioned per S.74, deployed per S.72/76.
```

Every arrow above represents a real technical dependency. Attempting to build later layers without earlier layers produces the exact fragility Section 44 diagnosed in the current Agent Improve.

---

## 1. LangGraph Persistent Checkpointing

### What It Is
LangGraph's built-in mechanism to save graph state after every node execution. Managed entirely by LangGraph — not something you build yourself.

### How It Works
```python
# One-line wire-in at graph compilation
graph = workflow.compile(checkpointer=checkpointer)

# LangGraph automatically:
# - saves state after every node
# - resumes on same thread_id
# - handles crash recovery
```

### Storage Backend Options

| Backend | Use Case | Status |
|---|---|---|
| `SqliteSaver` | Local dev only — file wiped on Azure restart | Not viable for deployment |
| `PostgresSaver` | Production — first-class LangGraph support | Target for agentlean-* migration |
| Custom Blob Saver | Must implement `BaseCheckpointSaver` yourself | Ruled out — too much custom code |

### Current Gap in AgentLean
No checkpointer is wired into `workflow.compile()`. State persists only at gate boundaries via Azure Blob write. Mid-conversation state is lost on server restart.

### Current Mitigation
Completeness-based re-extraction from full conversation history on every gate submission acts as a natural mitigation within a session.

### Implementation When Ready
```python
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(os.getenv("PG_CONN"))
graph = workflow.compile(checkpointer=checkpointer)
```

---

### Fail-Fast Environment Validation — Production Pattern

*Source: Edureka Course 4 Module 3 end-to-end demo, generalised for AgentLean.*

Validate all required credentials at application startup — before the first request arrives. Silent credential failures corrupt first requests without a clear error message.

```python
# agent-improve/backend/app.py — startup validation
import sys

def validate_environment():
    required = {
        "AZURE_OPENAI_KEY": "Azure OpenAI — coaching LLM unavailable",
        "AZURE_SEARCH_API_KEY": "Azure AI Search — knowledge retrieval unavailable",
        "LANGCHAIN_API_KEY": "LangSmith — observability disabled",
    }
    missing = []
    for key, description in required.items():
        if not os.getenv(key):
            missing.append(f"  {key}: {description}")

    if missing:
        print("STARTUP FAILED — missing required environment variables:")
        print("\n".join(missing))
        print("Check agent-improve/.env — see .env.example for required keys")
        sys.exit(1)   # halt immediately, do not serve requests

validate_environment()   # call at module level, before app starts
```

This replaces the current pattern where missing credentials surface as cryptic Azure SDK errors mid-request. The fail-fast exit code 1 also integrates cleanly with Docker health checks and container orchestration — a container that fails startup will not receive traffic.

---

### `@traceable` Decorator — Making Custom Functions Visible in LangSmith

*Source: Edureka Course 4 Module 3 end-to-end demo.*

LangSmith automatically traces LangChain runnables and LangGraph nodes. It does NOT automatically trace plain Python functions — even if they contain important logic like field extraction, gate validation, and completeness checking.

The `@traceable` decorator makes any custom function appear in LangSmith traces without changing the function logic:

```python
from langsmith import traceable

@traceable   # ← now visible in LangSmith traces
def extract_define_fields(llm_response: str, state: dict) -> dict:
    """Extract DMAIC Define phase fields from Belt's coaching response."""
    # extraction logic here
    return captured_fields

@traceable
def validate_define_gate(state: DefineState) -> list[str]:
    """Run all four validation layers for Define gate."""
    failures = []
    # DMAICGateValidator calls here
    return failures

@traceable
def check_completeness(captured_fields: dict, phase: str) -> float:
    """Score completeness of captured fields for current phase."""
    # completeness scoring here
    return score
```

**What appears in LangSmith after adding `@traceable`:**
```
Coaching turn trace:
  └── define_subgraph
        ├── coaching_node (LangGraph — already traced)
        ├── extract_define_fields (custom — NOW traced via @traceable)
        │     inputs: {llm_response: "...", state: {...}}
        │     outputs: {what: "...", why: "...", ...}
        │     latency: 45ms
        ├── check_completeness (custom — NOW traced via @traceable)
        │     inputs: {captured_fields: {...}, phase: "define"}
        │     outputs: 0.75
        └── validate_define_gate (custom — NOW traced via @traceable)
              inputs: {state: {...}}
              outputs: ["how_goal missing timeline criterion"]
```

Without `@traceable`, the LangSmith trace shows the LangGraph nodes but the logic BETWEEN them is invisible — you cannot see what the extraction produced, what completeness score triggered the next coaching turn, or which validation criterion failed. With `@traceable`, the full execution path is inspectable.

**Add `@traceable` to every custom function that:**
- Extracts fields from LLM responses
- Validates gate criteria
- Scores completeness
- Makes routing decisions outside of LangGraph node routing
- Calls the MCP server (so MCP tool latency appears in traces)

---

### LangSmith Diagnostic Patterns — What to Look For in Production

*Source: Edureka Course 4 Module 3 LangSmith observability demo.*

**Trace tree for pinpointing failures:**

Without `@traceable`, a gate validation failure surfaces as a 500 error at the API level with no indication of which layer failed. With it:

```
Coaching turn trace:
  ├── coaching_node          → PASS  1.2s
  ├── extract_define_fields  → PASS  0.3s
  ├── check_completeness     → PASS  0.1s
  └── validate_define_gate   → FAIL  ← failure is here, not anywhere else
        error: "how_goal missing timeline criterion"
        input: {how_goal: "Reduce complaint rate by 50%"}
```

The trace answers: was it the coaching LLM, the extraction, the completeness check, or the gate validator? One click, immediate answer.

**P50/P99 latency as a coaching quality signal:**

LangSmith's project overview aggregates latency percentiles across all traces:

```
P50 coaching turn latency: 1.8s   → acceptable, most turns are fast
P99 coaching turn latency: 12s    → flag — what causes the worst 1% of turns?
```

High P99 latency degrades the Belt's coaching experience. The trace for the slowest turns will show which combination of operations caused the outlier — typically multi-hop retrieval (Section 71) combined with a RubricMiddleware grader call on the same turn. The fix is either caching (Section 65), a faster model for the grader (Section 42's temperature note), or restructuring the validation stack to run cheapest-first (Section 69).

**The diagnostic workflow:**
```
P99 latency spike detected in LangSmith project overview
        ↓
Filter traces by latency > 8s
        ↓
Open the slowest trace — expand each node
        ↓
Identify which node consumed the most time
        ↓
Act: cache it (Section 65), reorder it (Section 69),
     or use a faster model (Section 42)
```

---

## 2. Human-in-the-Loop (Interrupts)

### What It Is
LangGraph pauses graph execution at declared points, persists state, and waits for explicit human approval before resuming. Requires checkpointing as a prerequisite.

### How It Works
```python
# Declare interrupt points at compile time
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["gate_evaluate"]
)

# Graph pauses here — resumes only when called again with same thread_id
graph.invoke(input, config={"configurable": {"thread_id": project_id}})
```

### Where Interrupts Belong in Agent Improve

| Interrupt Point | Purpose |
|---|---|
| Gate evaluation | Belt reviews extracted fields before phase advances |
| Field correction | Belt edits fields the AI captured incorrectly |
| Coach escalation | AI uncertain — needs human confirmation before proceeding |

### Current Gap
Gate advancement is automatic after extraction. No human review step between extraction and phase advancement. Belt cannot correct AI-extracted fields before they are committed.

### Dependency Chain
```
PostgreSQL → Checkpointer → Interrupts possible
```

---

## 3. Time Travel Debugging & Snapshot Analysis

### What It Is
LangGraph allows replaying a graph execution from any previous checkpoint and inspecting state at any node during a past run.

### How It Works
```python
# Replay from a specific checkpoint
graph.invoke(None, config={
    "configurable": {
        "thread_id": "IMPR-2026-E9D",
        "checkpoint_id": "step_3"
    }
})

# Inspect state history
state_history = graph.get_state_history(config)
```

### Current Gap
No checkpoint IDs exist. No state history is stored. Debugging extraction errors, gate routing bugs, and phase regressions requires manual reproduction.

### Practical Pain Points Without It
- Extraction hallucination debugging requires re-running the full conversation
- Gate advancement bugs (e.g. `selectTab` vs `openWorkspace`) are hard to reproduce
- No before/after state comparison when a change introduces a regression

### Key Point
Resolved automatically when PostgreSQL checkpointer is wired in. No additional implementation needed beyond Gap 1.

---

## 4. DAG Execution vs LangGraph Cycles

### What a DAG Is
**Directed Acyclic Graph** — nodes connected by directed edges with no cycles.

```
    A
   / \
  B   C     ← B and C run in parallel
   \ /
    D        ← D runs after both complete
```

Used in: Airflow, Spark, build systems, data pipelines.

### How LangGraph Extends DAGs
LangGraph allows **cycles** — nodes can loop back, enabling agent reasoning patterns:

```
A → B → C ──┐
    ↑        │   ← agent loops: think → act → observe → think
    └────────┘
```

### Agent Improve Graph Shape
Currently **mostly DAG-like** — one linear pass per HTTP request:

```
START → load_state → route_message → generate_response → extract_fields → save_state → END
```

LangGraph's cycle capability is not yet heavily used. Each request triggers one clean pass.

---

## 5. Planner / Executor Model

### What It Is
A multi-agent pattern separating reasoning (planner) from action (executor). The planner never executes; the executor never plans.

```
User Request
     ↓
  PLANNER          ← reasons, produces structured plan (gpt-4o class LLM)
     ↓
  [Step 1]
  [Step 2]
  [Step 3]
     ↓
  EXECUTOR         ← carries out each step (tool calls, RAG, extraction)
     ↓
  Result
```

### Planner Output (Structured)
```python
{
    "plan": [
        "Retrieve baseline defect rate data",
        "Calculate process sigma level",
        "Identify top 3 root causes from Fishbone",
        "Validate causes against data",
        "Recommend improvement hypothesis"
    ]
}
```

### Current Gap in Agent Improve
Single-agent pattern — planning and execution are **implicit** inside the coaching LLM prompt. No explicit planner node exists.

### How It Maps to AgentLean Architecture
The pattern maps naturally onto the Path C hierarchical subgraph design:

| Current | With Planner/Executor |
|---|---|
| Supervisor routes phases | Supervisor becomes PLANNER |
| Phase subgraphs run coaching | Phase subgraphs become EXECUTORS |
| Coaching strategy implicit in prompt | Coaching strategy explicit and inspectable |

### Two-Level Cascade Architecture

Planners and executors exist at **each level** of the hierarchy — not just globally.

**Level 1 — Global**
```
Global Planner    → decides which phase subagent to invoke
                    (What phase? What fields missing? Which subagent?)
Global Executor   → the chosen phase subagent
```

**Level 2 — Phase**
```
Phase Planner     → decides what to do within this phase turn
                    (Ask for data? Run extraction? Trigger gate check?)
Phase Executor    → runs tool calls, RAG, LLM coaching, extraction
```

**Full cascade:**
```
User Message
     ↓
GLOBAL PLANNER (Supervisor)
  - What phase are we in?
  - What fields are missing?
  - What is the coaching strategy for this turn?
  - Which subagent should execute?
     ↓
PHASE SUBAGENT
     ↓
  Phase Planner   → structured decision: what action this turn
     ↓
  Phase Executor  → RAG lookup, coaching LLM, extraction, gate check
     ↓
Response to user
```

### What Changes in the Refactor

**Now — planning is implicit inside the prompt:**
```
"You are a Black Belt coach. The user said X.
 Fields missing: Y. Continue the conversation."
```
The LLM figures out what to do. No structured plan. Coaching strategy invisible.

**After refactor — planning is explicit:**
```python
# Phase Planner output (structured JSON)
{
  "next_action": "ask_for_baseline_data",
  "rationale": "baseline_mean missing, process scope confirmed",
  "tools_needed": ["rag_lookup", "extraction"],
  "expected_fields": ["baseline_mean", "baseline_std"]
}
# Phase Executor then carries out exactly this action
```

### Why This Is Powerful for DMAIC Specifically
DMAIC phases have **known structure** — the planner always knows exactly which fields are required, which are captured, and what a Black Belt would logically ask next. That domain knowledge moves from a long buried prompt into an inspectable reasoning step. Coaching quality improves, hallucination risk decreases.

### Mapping Current Architecture → Refactored

| Current | Refactored |
|---|---|
| Supervisor node (routes phases) | Global Planner |
| Phase subgraph entry | Global Executor + Phase Planner |
| Coaching node inside phase | Phase Executor |
| Extraction node | Phase Executor tool |
| Gate check node | Phase Executor tool |

The **architecture is already the right shape** — Path C hierarchical subgraphs provide the scaffold. The refactor makes planning logic explicit rather than implicit.

### Implementation Notes
- Global Planner uses `operational-premium` (gpt-4o) — reasoning-heavy
- Phase Planner uses `operational-premium` (gpt-4o) — structured decision
- Phase Executor uses `operational-model` (gpt-4o-mini) — tool calls, extraction
- All planner outputs structured JSON, not prose
- Re-planning triggered when executor hits a dead end or missing data

---

## 6. Multi-User Production Gaps

### Identity & Session Isolation
- No authentication layer currently
- No user namespacing on blobs
- Any `project_id` guess exposes another user's data
- Target: Azure AD B2C or Auth0 + blob path `/{user_id}/{project_id}/state.json`

### Concurrency & State Write Safety
- No locking on blob reads/writes
- Concurrent users on same project can cause write race → state corruption
- Target: ETag-based optimistic concurrency on blob writes

### Azure OpenAI Rate Limits
- No request queuing beyond LangChain defaults
- TPM limits hit fast under concurrent users
- Target: exponential backoff, request queuing, potentially multiple deployments

### Tagged Observability
- LangSmith traces untagged — no `user_id` / `project_id` context
- Errors visible only in local terminal
- Target: tagged traces, Azure Monitor, alerting on failed gates

---

## 7. Full Dependency Chain

```
PostgreSQL (new Azure resource, ~€15/month smallest tier)
    ↓
Checkpointer wired into workflow.compile()
    ↓
├── Human-in-the-loop interrupts
├── Time travel debugging
├── Snapshot analysis
└── Enables stateful planner/executor loops
```

---

## 8. Implementation Sequencing Decision

### Rationale for Deferral
All items in this document are deferred until after all three AgentLean agents are complete:

- Checkpointing and interrupts require PostgreSQL — not justified before the product is feature-complete
- Current blob-at-gate pattern is durable enough for single-user demo use
- Adding these now extends timeline with infrastructure work before core DMAIC value is proven

### The Correct Sequence
```
Complete Analyse v2.1
    ↓
Build Improve phase
    ↓
Build Control phase
    ↓
Run IMPR-2026-E9D end-to-end clean
    ↓
Activate IMPR-2026-FS1 (financial services demo)
    ↓
Begin Agent Flow
    ↓
All three agents complete
    ↓
valuesims-* → agentlean-* migration
+ PostgreSQL
+ Checkpointer (PostgresSaver)
+ Human-in-the-loop interrupts
+ Time travel debugging
+ Planner/executor refactor
+ Multi-user identity & isolation
+ Tagged observability
```

---

## 9. Coursera / Edureka Multi-Agent Systems — Notes

*Section to be expanded as course progresses.*

### Topics Covered
- [x] Planner/Executor model — see Section 5
- [x] Two-level cascade (global + phase level) — see Section 5
- [x] Human oversight through middleware — link logged, content pending login

### Topics to Add as Covered
- [ ] ReAct pattern (Reason + Act)
- [ ] Tool calling agents
- [ ] Memory types (short-term, long-term, episodic, semantic)
- [ ] Agent communication patterns
- [ ] Supervisor / worker hierarchies
- [ ] Reflection and self-critique agents

### Course Links
- Human Oversight Through Middleware: https://www.coursera.org/learn/multi-agent-systems-with-langgraph/supplement/zVa2L/human-oversight-through-middleware
  *(Coursera login required — paste content here when reviewing)*

---

## 10. Subagent State Management

### The Core Problem
When a parent graph and child subgraphs coexist, three questions must be answered explicitly:
- What does the parent (supervisor) know?
- What does each subagent know?
- How do they share information without corrupting each other?

---

### Three Patterns LangGraph Supports

**Pattern 1 — Shared Global State**

Every node and every subagent reads and writes the same flat state object.

```python
class AgentImproveState(TypedDict):
    project_id: str
    current_phase: str
    messages: list
    # All phase fields in one flat object
    what: str                       # Define
    baseline_mean: float            # Measure
    root_cause_statement: str       # Analyse
    improvement_hypothesis: str     # Improve
    control_plan: str               # Control
```

*What AgentLean has now — essentially this.*

Pros: Simple, everything visible everywhere.
Cons: Subagents can accidentally overwrite each other's fields. No encapsulation. Silent cross-phase corruption possible.

---

**Pattern 2 — Private Subagent State + Shared Parent State** ← Target for AgentLean

Parent has its own state. Each subagent has its own private state. They communicate through explicit typed input/output schemas.

```python
# Parent state — only what the supervisor needs
class SupervisorState(TypedDict):
    project_id: str
    current_phase: str
    messages: list
    phase_result: dict          # what the subagent hands back

# Define subagent — private state
class DefineState(TypedDict):
    messages: list              # its own conversation slice
    what: str
    why: str
    how_goal: str
    coaching_plan: dict         # planner output — parent never sees this
    completeness_score: float

# Measure subagent — private state
class MeasureState(TypedDict):
    messages: list
    baseline_mean: float
    baseline_std: float
    coaching_plan: dict
    completeness_score: float
```

Parent passes a slice **in**, subagent returns a slice **out**. Clean boundary. No cross-phase access possible.

---

**Pattern 3 — State Handoff via Channels**

LangGraph's most sophisticated pattern. Parent and subagents communicate through typed channels with reducers that control how values are merged.

```python
# Reducer controls HOW values combine on write
def merge_phase_fields(existing, new):
    return {**existing, **new} if new else existing

class AgentImproveState(TypedDict):
    messages: Annotated[list, add_messages]        # append-only, never overwrite
    phase_fields: Annotated[dict, merge_phase_fields]  # merge, not overwrite
```

---

### The Right Architecture for Agent Improve

**Pattern 2** maps directly onto the two-level cascade:

```
SupervisorState (parent)
├── project_id
├── current_phase
├── messages (full conversation — parent owns this)
└── gate_status per phase
         │
         │ passes in: {messages, phase_fields}
         ↓
DefineSubgraphState (private)
├── messages (slice)
├── define_fields: {what, why, how_goal, ...}
├── coaching_plan  ← planner output, never exposed to parent
└── completeness_score
         │
         │ returns to parent: {define_fields, completeness_score, gate_ready}
         ↑
MeasureSubgraphState (private)
├── messages (slice)
├── measure_fields: {baseline_mean, baseline_std, ...}
├── coaching_plan
└── completeness_score
```

---

### Three Rules for AgentLean State Management

**Rule 1 — Parent owns the conversation.**
Full `messages` list lives in `SupervisorState`. Subagents receive a copy, never write back directly. Parent appends the subagent response after it returns.

**Rule 2 — Subagents own their phase fields.**
`DefineState` owns Define fields. `MeasureState` owns Measure fields. No cross-phase field access ever. This makes the field name discipline bugs we have already hit (`what` vs `problem_statement`, `baseline_mean` vs `baseline_value`) structurally impossible rather than just unlikely.

**Rule 3 — Communication through explicit typed schemas.**
What goes in and what comes out is a declared typed schema. The planner's `coaching_plan` is internal to the subagent — the parent never sees it. The parent only receives what it needs to route next.

---

### The Anti-Pattern to Avoid

```python
# DANGEROUS — flat global state, anyone writes anywhere
state["root_cause_statement"] = "..."   # Analyse writing — fine
state["baseline_mean"] = 4.2            # Define node doing this by mistake — silent corruption
```

With flat shared state and no encapsulation, a bug in one subagent corrupts another phase's data silently. Private subagent state with typed schemas makes this class of bug impossible.

---

### Relationship to Checkpointing

Each subagent state is checkpointed **independently** when PostgreSQL checkpointer is wired in. This means:

- A crash mid-Define does not affect Measure's checkpointed state
- Time travel can replay a specific subagent's execution independently
- Interrupt points can be declared per subagent, not just globally

---

### Current Gap in AgentLean
Agent Improve uses a flat shared state (Pattern 1). All phase fields coexist in one object. No encapsulation between phases. Refactor to Pattern 2 is part of the post-completion architecture work alongside checkpointing and planner/executor introduction.

---

### MessagesState Inheritance vs Explicit TypedDict — When Each Applies

*Source: Edureka Course 2 lab — Building a Multi-Agent Subgraph Workflow*

LangGraph provides a built-in convenience base class for conversational state:
```python
from langgraph.graph import MessagesState

class MessagesState(TypedDict):
    messages: Annotated[list, add_messages]
```

Course labs commonly declare subgraph states this way:
```python
class SubgraphState(MessagesState):
    summary: str
```

**The two options are functionally identical — same reducer, same behavior:**
```python
# Option A — inherit MessagesState
class DefineState(MessagesState):
    what: str
    why: str
    completeness_score: float
    # "messages" field and its reducer come for free

# Option B — declare TypedDict directly, explicit reducer
class DefineState(TypedDict):
    messages: Annotated[list, add_messages]   # explicit, same reducer, same behavior
    what: str
    why: str
    completeness_score: float
```

**The distinction is design intent, not behavior.** `MessagesState` inheritance is the right convenience when the state's dominant content genuinely IS conversational — a chat container with a few extras bolted on. Explicit `TypedDict` declaration is the better choice when the state's dominant content is structured working memory that happens to also need conversation history for context.

**For Agent Improve's phase substates specifically:** `DefineState`, `MeasureState`, `AnalyseState` etc. are fundamentally structured DMAIC field containers (`what`, `why`, `baseline_mean`, `completeness_score`) — the conversation history is one field among several, not the dominant shape. Option B (explicit `TypedDict`) is more consistent with this document's emphasis on typed Pydantic boundary contracts and explicit state design (Section 44), even though it costs one extra line versus inheriting `MessagesState`.

**Where `MessagesState` inheritance genuinely IS the right choice in Agent Improve:** the debate subgraph (Section 22). `DebateState`'s dominant content really is conversational exchange — advocate argument, skeptic argument — making it closer in shape to the lab's researcher/summarizer example than the phase-level states are.

**The rule:**
```
State is mostly conversation + a few extras    → MessagesState inheritance is fine
State is mostly structured fields + conversation → explicit TypedDict makes intent clearer
```

---

*This document should be committed to the repo root alongside CLAUDE.md and ARCHITECTURE.md.*
*Commit prefix: `docs(education):` per v2.1 commit discipline.*

---

## 11. Recursive Planner / Executor — Every Level Plans

### The Core Insight
The planner/executor pattern is **recursive**. Every level of the hierarchy has its own planner and its own executor. The supervisor's executor IS the subagent. The subagent IS itself a planner/executor pair. The subagent's executor IS the tools.

```
SUPERVISOR
  Planner: "We are in Analyse. Root cause missing. Invoke Analyse subagent."
  Executor: Analyse Subagent
       │
       ↓
  ANALYSE SUBAGENT
    Planner: "Root cause missing. Belt confirmed 3 causes. Ask to validate with data."
    Executor: RAG tool + Coaching LLM + Extraction tool
```

---

### Three Levels of Planning in Agent Improve

**Level 1 — Supervisor Planner**

Thinks about the **entire DMAIC project across weeks**:
- Which phase are we in?
- Is the current phase complete?
- Which subagent should execute this turn?
- Is the gate ready to pass?

Scope: weeks, across all five phases.

---

**Level 2 — Phase Planner (inside each subagent)**

Thinks about **one phase, one conversation turn**:
- Which fields are still missing in this phase?
- What did the Belt say last turn?
- What is the most logical next coaching question?
- Do I need RAG, extraction, or both this turn?

Scope: minutes, within one phase.

---

**Level 3 — Tool Executor**

Does not think — just executes what the Phase Planner decided:
- Call RAG with query X
- Call coaching LLM with prompt Y
- Run extraction on Belt's last message
- Check completeness score

Scope: milliseconds, one tool call at a time.

---

### The Full Flow — One Belt Message

```
Belt sends message
       ↓
LEVEL 1 — SUPERVISOR PLANNER
  Reads full dmaic_plan + captured_fields
  "Analyse phase, root_cause_statement missing"
  Decision: invoke Analyse subagent
       ↓
LEVEL 2 — ANALYSE PHASE PLANNER
  Reads analyse_fields + last messages
  "Belt listed 3 causes, none validated yet"
  Decision: {
    next_action: "validate_causes",
    tools: ["rag_lookup", "coaching_llm", "extraction"],
    focus_field: "root_cause_statement"
  }
       ↓
LEVEL 3 — TOOL EXECUTOR
  → RAG: "how to validate root causes with hypothesis testing"
  → Coaching LLM: generates Black Belt response
  → Extraction: tries to capture root_cause_statement
       ↓
Results bubble back up:
  Extraction result → Phase Planner (field captured? yes/no)
  Phase result → Supervisor (completeness score, gate ready?)
  Supervisor → updates blob, sends response to Belt
```

---

### Across Multiple Weeks — Continuity

The supervisor's dmaic_plan and captured_fields persist across all sessions via blob (now) and checkpointer (future). Each session the supervisor loads state and picks up exactly where the project left off. The belt never re-explains what they have done.

```
Week 1  Sessions 1-3   Define Subagent executes    → gate passed
Week 2  Sessions 4-6   Measure Subagent executes   → gate passed
Week 3  Session 7      Analyse Subagent executes   → 40% complete, saved
Week 3  Session 8      Analyse Subagent resumes    → NOT from scratch
Week 3  Session 9      Analyse gate passed         → Improve unlocked
```

Each session:
1. Supervisor loads blob → knows full project state instantly
2. Phase Planner reads captured fields → knows exactly what is missing
3. Tool Executor runs coaching → captures incrementally
4. Supervisor saves updated state → ready for next session

---

### Tools Live in Subagents — Not the Supervisor

The supervisor has no tools. It only reasons and routes.

```
Supervisor (Planner only — no tools)

Define Subagent          Measure Subagent         Analyse Subagent
├── RAG tool             ├── RAG tool             ├── RAG tool
├── extraction tool      ├── extraction tool      ├── extraction tool
├── gate check tool      ├── sigma calc tool      ├── fishbone tool
└── coaching LLM         ├── gate check tool      ├── gate check tool
                         └── coaching LLM         └── coaching LLM

Improve Subagent         Control Subagent
├── RAG tool             ├── RAG tool
├── hypothesis tool      ├── control plan tool
├── extraction tool      ├── extraction tool
├── gate check tool      ├── gate check tool
└── coaching LLM         └── coaching LLM
```

---

### The Consulting Firm Analogy

| Role | Agent Improve Equivalent | Thinks About |
|---|---|---|
| Engagement Partner | Supervisor Planner | Full project across weeks |
| Phase Lead | Phase Planner | This week's deliverable |
| Analyst | Tool Executor | This specific task right now |

The Partner does not write the report. The Analyst does not decide what the report covers. Each level plans at its own scope and delegates execution downward.

---

### What We Have Now vs After Refactor

| Capability | Now | After Refactor |
|---|---|---|
| Supervisor reasoning | Implicit routing in prompt | Explicit planner node reading dmaic_plan |
| Phase planning | Implicit in coaching prompt | Explicit phase planner node per subagent |
| Tool encapsulation | Mixed into one graph | Encapsulated per subagent |
| Field accumulation | Re-extraction from full history | Incremental per session via state |
| Mid-session recovery | Lost on restart | Checkpointer resumes automatically |
| Cross-session memory | Blob loaded on each request | Same + richer checkpoint history |

---

### Current Gap in AgentLean
No explicit planner nodes exist at either level. Planning is implicit inside coaching prompts. The refactor introduces:
- A supervisor planner node (Level 1)
- A phase planner node inside each subagent (Level 2)
- Tool executor nodes per subagent (Level 3)

All deferred to post-completion refactor. The Path C hierarchical subgraph architecture is already the correct scaffold for this pattern.

---

## 12. From Execution Control to Task Delegation (Edureka Course — Slide)

*Source: Edureka / Veranda Multi-Agent Systems with LangGraph course*

### The Diagram

```
User Objectives
       ↓
Planner Node          ← creates the plan
       ↓
Task Plan             ← structured artifact (stacked pages — not implicit in prompt)
       ↓    ↑ Edited
Executor              ← executes one task at a time
       ↓
Human-in-the-loop?    ← interrupt point
       ↓ no                ↓ yes
       ↓            Approved?
       ↓                ↓ yes
       ↓         Checkpoint & State Update   ← state saved HERE, not before
       ↓                ↓
       └──────► Next Task?   ← loop: next phase or next field
```

---

### Three Key Insights From This Slide

**1. Task Plan is a first-class object.**
Shown as stacked pages — a structured artifact the planner creates and the executor consumes task by task. Not buried in a prompt. In Agent Improve this maps to `dmaic_plan` with phase fields as individual tasks.

**2. Human-in-the-loop sits between Executor and Checkpoint.**
The human reviews AFTER the executor runs but BEFORE state is saved. The Belt reviews what was captured before it is committed. This is the correct gate pattern — currently we save at gate boundary without a human review step.

**3. The human can EDIT the Task Plan — not just approve/reject.**
The "Edited" arrow returns to the Task Plan, not just a binary approve/reject. The Belt can correct AI-extracted fields directly before the executor runs again. This is richer than a simple interrupt.

---

### The Edit Loop — What It Means for Agent Improve

Current pattern (no interrupt):
```
Executor extracts root_cause_statement = "agent error rate"  ← possibly wrong
Blob saved immediately
Belt has no review step
```

With interrupt + edit loop:
```
Executor extracts root_cause_statement = "agent error rate"
       ↓
Human-in-the-loop INTERRUPT
Belt reviews: "that is wrong"
Belt edits Task Plan: root_cause_statement = "agent training gaps"
       ↓
Approved? Yes
       ↓
Checkpoint & State Update   ← correct value saved
       ↓
Next Task?
```

The edit loop makes AI extraction errors **recoverable before they become permanent record**.

---

### Updated Human-in-the-Loop Pattern (Replaces Section 2)

Section 2 described interrupts as approve/reject only. This slide shows the full pattern:

| Step | What Happens |
|---|---|
| Executor runs | Coaching LLM + extraction captures fields |
| Interrupt fires | Graph pauses, Belt sees extracted fields |
| Belt reviews | Checks AI-captured values for accuracy |
| Belt edits (optional) | Corrects wrong fields directly in Task Plan |
| Belt approves | Confirms gate ready |
| Checkpoint saves | State committed to PostgreSQL only now |
| Next Task? | Supervisor routes to next phase or next field |

---

### Mapping to Agent Improve Architecture

| Diagram Element | Agent Improve Equivalent |
|---|---|
| User Objectives | Belt's DMAIC project goal |
| Planner Node | Supervisor Planner (Level 1) |
| Task Plan | `dmaic_plan` with phase fields as tasks |
| Executor | Phase Subagent (Levels 2 + 3) |
| Human-in-the-loop | Belt reviews extracted fields at gate |
| Edited | Belt corrects wrong AI-extracted field values |
| Approved? | Belt confirms phase gate ready |
| Checkpoint & State Update | PostgreSQL checkpointer (currently: blob at gate) |
| Next Task? | Next phase or next missing field in same phase |

---

### What This Changes in the Refactor Plan

The edit loop requires a FastAPI resume endpoint — not just a pause:

```python
# Pause — graph interrupts here automatically
graph.invoke(input, config={"configurable": {"thread_id": project_id}})

# Belt reviews extracted fields in UI
# Belt edits if needed — sends corrections back

# Resume — with corrected state
graph.invoke(
    Command(resume={"edited_fields": corrections}),
    config={"configurable": {"thread_id": project_id}}
)
# Checkpoint saves AFTER this resume, not before
```

Two endpoints needed in FastAPI:
- `GET /gate/review` — returns current extracted fields for Belt to review
- `POST /gate/approve` — accepts corrections + approval, resumes graph, triggers checkpoint

---

### Current Gap Update
Section 2 (Human-in-the-Loop) understated the pattern. It is not just interrupt → approve. It is interrupt → review → optional edit → approve → checkpoint. The edit capability is what makes the system trustworthy for a DMAIC audit trail — the Belt is accountable for what gets saved, not the AI.

---

## 13. Complete Planner/Executor Flow — Full Diagram (Edureka Course)

*Source: Edureka / Veranda — Multi-Agent Systems with LangGraph, Multi-Step Task Planning and Execution module*

### The Complete Flow

```
User Objectives
       ↓
Planner Node
       ↓
Task Plan ◄──────────── Edited (human correction loops back here)
       ↓
Executor ──────────────► Human-in-the-loop
                                ↓ Approved? Yes
                         Checkpoint & State Update
                                ↓
                           Next Task?
                          ↙         ↘
                        Yes          No
                         ↓            ↓
                   (loop back       Output
                   to Executor)   (final result)
```

### What the Full Diagram Adds vs Previous Screenshot

The right side was cut off before. The complete flow adds:

- **Next Task? → No → Output** — explicit loop termination. When all tasks are complete the system produces final output, not just another loop. In Agent Improve this Output is the completed gate document / phase summary.
- **Next Task? → Yes → loops back to Executor** — confirmed the cycle pattern. The executor runs tasks one at a time, not all at once.
- The Human-in-the-loop sits on the path FROM Executor TO Checkpoint — human reviews before state is ever saved, not after.

### Mapping to Agent Improve — Complete

| Diagram Element | Agent Improve Equivalent |
|---|---|
| User Objectives | Belt's DMAIC project goal |
| Planner Node | Supervisor Planner (Level 1) |
| Task Plan | `dmaic_plan` — phase fields as individual tasks |
| Executor | Phase Subagent (Levels 2 + 3) |
| Human-in-the-loop | Belt reviews AI-extracted fields at gate |
| Edited | Belt corrects wrong field values — loops back to Task Plan |
| Approved? | Belt confirms gate ready |
| Checkpoint & State Update | PostgreSQL checkpointer (currently: blob at gate boundary) |
| Next Task? Yes | Next missing field or next phase |
| Next Task? No | All phases complete — final DMAIC report output |
| Output | Completed DMAIC project — gate documents, control plan |

---

## 14. Course Curriculum Map — What Is Coming

*Captured from course left panel — Multi-Agent Systems with LangGraph*

### Completed Modules (green ticks at time of capture)

- ✅ Resuming from Checkpoints (6 min)
- ✅ Demonstration: Performing Branch Analysis with Snapshots I (5 min)
- ✅ Demonstration: Performing Branch Analysis with Snapshots II (5 min)
- ✅ Failure Patterns in Long-Running Agent Workflows (15 min reading)
- ✅ Practice Assignment: Debugging Pipelines and Time-Travel Analysis (Grade: 100%)
- ✅ Planner & Executor Task Model (6 min) ← current position

### Upcoming Modules — High Priority for AgentLean

- ⬜ Demonstration: Creating a Planner Node with a Structured Executor I (7 min)
- ⬜ Demonstration: Creating a Planner Node with a Structured Executor II (7 min)

These two demonstrations are directly applicable to Agent Improve. Screenshots and notes should be captured and added here.

---

## 15. Failure Patterns in Long-Running Agent Workflows

*Source: Edureka course — 15 min reading, completed*

### Why This Is Critical for Agent Improve

Agent Improve is explicitly a long-running agent workflow — a DMAIC project spans weeks with multiple sessions. This module directly addresses the failure modes we will encounter.

### Content to Be Added

*Paste or screenshot the reading content here for capture.*

Common failure patterns in long-running agent workflows typically include:

- **State drift** — accumulated state diverges from reality over many sessions
- **Context window overflow** — conversation history grows too large for the LLM context
- **Stale plan** — planner made assumptions early that are no longer valid
- **Orphaned checkpoints** — checkpoints accumulate without cleanup strategy
- **Partial task completion** — executor completes some subtasks but fails mid-plan, leaving state inconsistent
- **Re-planning loops** — planner keeps re-planning without making progress

### AgentLean Relevance

| Failure Pattern | Agent Improve Risk | Current Mitigation |
|---|---|---|
| State drift | Belt's situation changes but old fields persist | Gate review + field correction (to be built) |
| Context window overflow | Multi-week projects accumulate long histories | Summarisation strategy needed |
| Stale plan | Phase fields defined in Define may be wrong by Analyse | Human-in-the-loop edit loop |
| Orphaned checkpoints | N/A until PostgreSQL checkpointer added | Deferred |
| Partial task completion | Server crash mid-phase loses turn | Blob-at-gate mitigation currently |
| Re-planning loops | Coach keeps asking same questions | Completeness score guards against this |

---

## 16. Architectural Debt Acknowledgement

### What Was Built vs What Should Have Been Built

When Agent Improve was created with the instruction to use LangGraph's latest technology, the following features were available but not implemented:

| Feature | Available | Implemented | Impact |
|---|---|---|---|
| Checkpointer | ✅ | ❌ | No mid-session recovery, no time travel |
| Human-in-the-loop interrupts | ✅ | ❌ | Gate advancement automatic, no Belt review |
| Explicit planner nodes | ✅ | ❌ | Planning implicit in prompts |
| Private subagent state schemas | ✅ | ❌ | Flat shared state, cross-phase corruption risk |
| Tool encapsulation per subagent | ✅ | ❌ | Tools mixed into one graph |
| Structured executor pattern | ✅ | ❌ | Executor implicit in coaching node |

### What Was Built Well
- LangGraph graph compilation and routing
- Hierarchical subgraph scaffold (Path C)
- SSE streaming
- Azure Blob state persistence at gate boundaries
- LangSmith tracing
- Black Belt coaching prompt quality
- Completeness-based extraction with anti-hallucination guards

### Root Cause
LangGraph was used as a **graph router and state passer** rather than as a full **agent framework**. The graph was compiled but its agent capabilities — checkpointing, interrupts, tool-calling agents, planner nodes — were never activated.

### Resolution Options

**Option A — Complete first, full refactor after (current plan)**
Finish Analyse, Improve, Control phases. Accept architectural debt. Full refactor during `agentlean-*` migration. Lower risk to timeline.

**Option B — Pause and refactor before building more phases**
Introduce checkpointer, private subagent states, explicit planner nodes before Improve and Control phases. Higher upfront cost but each new phase built correctly from the start.

Decision deferred to Vassilis. Both are defensible with full awareness of the tradeoffs.

---

## 17. InsightForge Mapping — Refactor Specification

*Source: Edureka course final project scenario*

The InsightForge scenario describes exactly Agent Improve's current architecture as the **problem to solve**. Every challenge maps directly to our gaps.

### Challenge Mapping

| InsightForge Problem | Agent Improve Equivalent | Our Status |
|---|---|---|
| Loses intermediate context during multi-step tasks | Mid-phase state lost on server restart | ❌ Gap 1 |
| Failures require restarting entire workflow | No checkpointer — full restart needed | ❌ Gap 1 |
| No structured execution flow | Planning implicit in prompts | ❌ Gap 10 |
| Critical responses without human review | Gate auto-advances after extraction | ❌ Gap 8 |
| Multiple specialist agents not coordinated | Flat single graph, no subagent separation | ❌ Gap 10 |

### Required Architecture (Direct Specification for Refactor)

**1. Typed State Schema**
```python
class SupervisorState(TypedDict):
    messages:        Annotated[Sequence[str], operator.add]   # append-only
    history:         Annotated[Sequence[str], operator.add]   # node execution order
    project_id:      str
    dmaic_plan:      List[Dict[str, Any]]                     # explicit plan object
    step_index:      int                                       # current phase index
    current_phase:   str
    captured_fields: Dict[str, Any]                           # artifacts — extracted values
    step_log:        List[Dict[str, Any]]                     # audit trail per step
    gate_documents:  Dict[str, str]                           # completed gate doc per phase
    final_output:    str                                       # full DMAIC report
```

**2. Conditional Router**
```python
def supervisor_router(state: SupervisorState) -> str:
    phase = state["current_phase"]
    routes = {"define": "define_subagent", "measure": "measure_subagent",
              "analyse": "analyse_subagent", "improve": "improve_subagent",
              "control": "control_subagent"}
    return routes.get(phase, END)
```

**3. Checkpointing**
```python
# Dev: InMemorySaver (zero infrastructure)
from langgraph.checkpoint.memory import InMemorySaver
checkpointer = InMemorySaver()

# Production: PostgresSaver
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(os.getenv("PG_CONN"))

graph = workflow.compile(checkpointer=checkpointer)
graph.invoke(input, config={"configurable": {"thread_id": project_id}})
```

**4. Human-in-the-Loop**
```python
graph = workflow.compile(
    checkpointer=checkpointer,
    interrupt_before=["gate_checkpoint"]
)
# FastAPI endpoints:
# GET  /gate/review   → returns extracted fields for Belt review
# POST /gate/approve  → accepts corrections + approval, resumes with Command(resume=corrections)
```

**5. Supervisor/Worker Architecture**
```
Supervisor: no tools, reads dmaic_plan, routes to phase subagents, updates step_index
Workers: Define, Measure, Analyse, Improve, Control — each with private state + phase tools
```

**6. Observability**
```python
# Time travel
graph.invoke(None, config={"configurable": {"thread_id": "IMPR-2026-E9D", "checkpoint_id": "before_gate_measure"}})
# Snapshot inspection
for state in graph.get_state_history(config):
    print(state.values["captured_fields"])
```

---

## 18. Lab Code — Imports and PlannerState Schema

*Source: Edureka course lab — Creating a Planner Node with a Structured Executor*

### Key Imports
```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt      # HITL primitives
from langgraph.checkpoint.memory import InMemorySaver  # dev checkpointer
import operator
from typing import Annotated, Sequence
```

### Complete PlannerState Schema
```python
class PlannerState(TypedDict):
    messages:     Annotated[Sequence[str], operator.add]  # append-only
    history:      Annotated[Sequence[str], operator.add]  # node execution order
    counter:      int
    task:         str                    # original user objective — never changes
    plan:         List[Dict[str, Any]]   # structured task list — first-class object
    step_index:   int                    # which task executor is currently on
    artifacts:    Dict[str, Any]         # results captured per step
    step_log:     List[Dict[str, Any]]   # audit trail — HOW each step was captured
    final_output: str                    # populated when step_index >= len(plan)
```

### Critical Design Insight: artifacts vs step_log
- `artifacts` = WHAT was captured (the results)
- `step_log` = HOW it was captured (the audit trail)

These are **separate fields**. In Agent Improve we currently mix these — `captured_fields` holds results but there is no separate audit log of how each field was captured. For DMAIC quality systems the separation matters — the Belt needs to show not just what the root cause was but how it was determined.

### AgentLean Field Mapping

| Course Lab Field | Agent Improve Equivalent |
|---|---|
| `task: str` | `project_description` from Define phase |
| `plan: List[Dict]` | `dmaic_plan` with phase fields as tasks |
| `step_index: int` | `current_phase` + `current_field_index` |
| `artifacts: Dict` | `captured_fields` |
| `step_log: List` | Currently missing — needs adding |
| `final_output: str` | Completed gate document / DMAIC report |
| `InMemorySaver` | Use now for dev; replace with `PostgresSaver` at production |

---

## 19. Multi-Step Task Chaining

*Source: Edureka course — Building Multi-Step Task Chains demonstration*

### The Core Pattern
A single LangGraph task chain is defined **once** and reused. Each chain runs independently with its own execution history. The finalized output of Chain 1 is injected into Chain 2 as structured input.

### Single Chain Structure (4 nodes)
```
Plan → Execute → Review (interrupt) → Revise → END
```

- **Plan node**: decomposes task into structured steps. Does NOT execute. Stores plan in state.
- **Execute node**: follows planner output, produces concise draft stored in `state["draft"]`
- **Review node**: pauses using `interrupt()`. Payload includes draft, allowed actions, decision hint. Stores human decision in `state["feedback"]`
- **Revise node**: if approved → draft becomes final immediately. If revision requested → regenerates using provided notes. Every chain ends with human-approved result.

### ChainState Schema
```python
class ChainState(TypedDict):
    messages:  Annotated[Sequence[str], operator.add]  # append-only
    history:   Annotated[Sequence[str], operator.add]  # node execution order
    task:      str      # instruction for this chain
    plan:      str      # planner's decomposition
    draft:     str      # executor's first output
    final:     str      # approved or revised result
    feedback:  str      # human decision and notes
```

### Multi-Chain Orchestration
```python
# Chain 1 runs fully — human approves
chain1_final = chain1_state["final"]

# Chain 2 receives Chain 1's output as structured input
chain2_input = f"Based on this: {chain1_final}\nNow do: [new task]"
chain2_state = run_chain(graph, chain2_input, thread_id="chain2")
```

Chain 2 does not start from scratch — it transforms and extends Chain 1's result.

### Critical Rule — Resume Mechanics
```python
# Same graph instance + same thread_id MUST be used when resuming
# This ensures LangGraph restores state correctly from checkpoint
graph.invoke(Command(resume=decision), config={"configurable": {"thread_id": thread_id}})
```

### AgentLean Mapping
Each DMAIC phase IS a chain. The output of Define feeds Measure. The output of Measure feeds Analyse. Each phase runs through Plan → Execute → Review → Revise with human approval before its output becomes the next phase's input.

---

## 20. Supervisor / Worker Architecture — Implementation

*Source: Edureka course — Implementing a Supervisor Node and Worker Agents*

### Key Design Principles

**Supervisor responsibilities:**
- Interprets overall task objective
- Decomposes complex tasks into manageable units
- Selects appropriate worker agents for execution
- Evaluates intermediate results and determines next steps
- Has NO tools — only routes

**Worker agent design principles:**
- Performs a single, well-defined function
- Operates with constrained prompts and tools
- Produces structured and consistent outputs
- Avoids direct control over global state or routing

### Supervisor Implementation Pattern
```python
def make_supervisor_node(llm, workers: list[str]):
    system_prompt = """You are a supervisor. Route tasks in this order: {workers}, then FINISH.
    Return ONLY the next worker name or FINISH."""
    
    def supervisor_node(state):
        messages = [SystemMessage(system_prompt)] + state["messages"]
        response = llm.invoke(messages)
        choice = response.content.strip().upper()
        
        # Graceful degradation — never crash on invalid choice
        if choice not in workers + ["FINISH"]:
            choice = workers[0]  # default to first worker
            
        if choice == "FINISH":
            return Command(goto=END)
        return Command(goto=choice)
    
    return supervisor_node
```

### Worker Implementation Pattern
```python
def make_worker_node(llm, name: str, role_prompt: str):
    def worker_node(state):
        messages = [SystemMessage(role_prompt)] + state["messages"]
        response = llm.invoke(messages)
        # Label messages with worker name for traceability
        return {
            "messages": [HumanMessage(content=response.content, name=name)],
            "history": [name]
        }
    return worker_node
```

### State for Supervisor/Worker
```python
class SupervisorState(MessagesState):
    next: str    # tracks which node executes next — the routing backbone
```

### Anti-Patterns to Avoid
- Assigning complex reasoning to workers (workers execute, supervisor reasons)
- Workers with overlapping responsibilities
- Workers influencing control flow directly
- Unstructured or ambiguous messages between agents

---

## 21. Message Passing Across Agent Nodes

*Source: Edureka course — Message Passing Across Agent Nodes demonstration*

### Sequential Pipeline Pattern (Generator → Reviewer → Refiner)
Three-stage pipeline where each agent builds on the previous one's work.

```python
class PipelineState(MessagesState):
    draft:    str    # generator's initial output
    feedback: str    # reviewer's critique
    # final comes from messages
```

### Dual Storage Pattern
Each node writes results to TWO places:
1. A **dedicated state field** for the next agent to access directly
2. The **messages list** as a named message for full audit traceability

```python
# Generator writes to both
return {
    "draft": draft_content,                                    # for reviewer
    "messages": [HumanMessage(content=draft_content, name="generator")]  # for audit
}

# Reviewer reads draft field directly — not from messages
reviewer_input = state.get("draft", "")
```

### Safe State Access Pattern
```python
# Always use .get() for safe access — never assume field exists
draft = state.get("draft", "")
feedback = state.get("feedback", "")
```

### AgentLean Application
This is the pattern for phase-to-phase handoff. Define writes its gate document to both `captured_fields["define"]` (for Measure to access directly) and to messages (for audit trail). Measure reads from `captured_fields["define"]`, not from message history.

---

## 22. Debate Agents and Consensus Voting

*Source: Edureka course — Debate Agents with Consensus Voting*

### When to Use Debate-Based Reasoning
- Complex, ambiguous, or high-stakes decisions
- When single-agent reasoning is insufficient
- When bias detection is important
- When transparency in decision-making is required

### Debate Agent Pattern
```python
class DebateState(MessagesState):
    votes: List[str]    # yes/no votes from each agent

def make_debate_agent(llm, name: str, stance: str):
    def agent_node(state):
        topic = state["messages"][-1].content
        system = f"You are {name}. Stance: {stance}. End response with YES or NO."
        response = llm.invoke([SystemMessage(system), HumanMessage(topic)])
        vote = "YES" if "YES" in response.content.upper() else "NO"
        return {
            "messages": [HumanMessage(content=response.content, name=name)],
            "votes": [vote]
        }
    return agent_node
```

### Judge Node (Consensus)
```python
def judge_node(state):
    votes = state["votes"]
    yes_count = votes.count("YES")
    no_count = votes.count("NO")
    decision = "APPROVED" if yes_count > no_count else "REJECTED"
    summary = f"Votes: YES={yes_count}, NO={no_count}. Decision: {decision}"
    return {"messages": [HumanMessage(content=summary, name="judge")]}
```

### Debate Framework Variants

*Source: Edureka Course 2 — Debate Frameworks in AI Systems*

The four variants are not separate mechanisms — three are content styles, one is the structural scaffold they all run on:

```
Adversarial Debate     → agents argue OPPOSING positions, deep critique
Society of Minds       → agents bring DIFFERENT EXPERTISE, not opposition
Collaborative Debate   → agents REFINE together, minimal conflict
Turn-based Protocol    → the STRUCTURE governing how any of the above takes turns
```

Turn-based Protocol is always present — it is the mechanical scaffolding. Adversarial, Society of Minds, or Collaborative is the content choice for what happens during each turn.

**Choosing the right variant per use case:**
- Root cause validation (Analyse phase) → **Adversarial** — high-stakes decision, want someone actively poking holes in the conclusion
- Improvement hypothesis evaluation (Improve phase) → **Society of Minds** — distinct expertise (cost, timeline, feasibility) rather than opposition

---

### Physical Implementation — Adversarial Debate for Root Cause Validation

A concrete, fully wired implementation for the candidate use case: validating a proposed root cause in the Analyse phase before the Belt commits to it. Built as a subgraph mounted inside the Analyse phase subgraph, following the nested-subgraph pattern from Section 44.

**Debate State — private, never crosses to AnalyseState until a verdict is reached:**
```python
class DebateState(TypedDict):
    proposed_root_cause: str
    supporting_evidence: dict          # data the Belt provided
    advocate_argument: str
    skeptic_argument: str
    round_count: int
    verdict: str                        # "supported" | "rejected" | "needs_more_data"
```

**The two opposing nodes:**
```python
def advocate_node(state: DebateState) -> Command:
    prompt = f"""
    You are arguing FOR this root cause: {state['proposed_root_cause']}
    Evidence available: {state['supporting_evidence']}
    Previous skeptic argument (if any): {state.get('skeptic_argument', 'none yet')}
    Make the strongest case that this root cause IS correctly identified.
    """
    response = llm.invoke(prompt)
    return Command(update={"advocate_argument": response.content}, goto="skeptic")

def skeptic_node(state: DebateState) -> Command:
    prompt = f"""
    You are arguing AGAINST this root cause: {state['proposed_root_cause']}
    Evidence available: {state['supporting_evidence']}
    Advocate's argument: {state['advocate_argument']}
    Identify weaknesses, alternative explanations, or insufficient evidence.
    """
    response = llm.invoke(prompt)
    return Command(
        update={"skeptic_argument": response.content, "round_count": state["round_count"] + 1},
        goto="judge"
    )
```

### Five Consensus Strategies — How a Debate's Verdict Gets Decided

*Source: Edureka Course 2 — Consensus Strategies in Multi-agent Systems*

The debate (Adversarial Debate above) generates the raw material — opposing arguments. Consensus strategy is the separate question of *how that material becomes a final verdict*. Five distinct mechanisms:

| Strategy | Mechanism | Cost | Fit for Root Cause Debate |
|---|---|---|---|
| Judge/Mediator | One dedicated agent evaluates both sides, decides | Lowest — single extra LLM call | Baseline — what was originally implemented |
| Voting Based | Multiple independent agents each cast a vote, majority wins | Highest — N independent LLM calls | Overkill for a 2-role debate; better suited to genuinely independent multi-agent panels |
| Confidence-Based Agents | Each agent reports a confidence score; verdict weights by confidence | Low — confidence reported alongside existing argument | Strong fit — connects to Section 38's Memory Prioritization weighting principle |
| Iterative Refinement | Agents revise their position in light of the other's argument across rounds, converging rather than repeating | Medium — multiple rounds | Strong fit — our judge's CONTINUE branch was a primitive version of this |
| Hybrid Approach | Combines multiple strategies | Varies | **Recommended for Agent Improve** — Confidence + Iteration + Judge |

**Why Hybrid, not pure Voting, for the root cause use case:** Voting needs multiple genuinely independent agents to be meaningful. A Belt's root cause debate naturally only has two opposing roles (advocate, skeptic) plus a deciding judge — adding 5 independent voters would be expensive overkill for this specific decision. The hybrid of Confidence + Iteration + Judge gives a defensible verdict without that cost, and is the correct upgrade to the implementation below.

---

### Upgraded Implementation — Hybrid Consensus (Confidence + Iteration + Judge)

**State with confidence fields added:**
```python
class DebateState(TypedDict):
    proposed_root_cause: str
    supporting_evidence: dict
    advocate_argument: str
    advocate_confidence: float       # NEW — confidence-based strategy
    skeptic_argument: str
    skeptic_confidence: float        # NEW — confidence-based strategy
    round_count: int
    verdict: str
```

**Advocate node now reports confidence alongside its argument:**
```python
def advocate_node(state: DebateState) -> Command:
    response = llm.invoke(f"""
    You are arguing FOR this root cause: {state['proposed_root_cause']}
    Evidence available: {state['supporting_evidence']}
    Previous skeptic argument (if any): {state.get('skeptic_argument', 'none yet')}
    Make the strongest case that this root cause IS correctly identified.
    Also rate your confidence in this argument from 0.0 to 1.0.
    Return JSON: {{"argument": "...", "confidence": 0.0}}
    """)
    parsed = parse_json(response.content)
    return Command(
        update={"advocate_argument": parsed["argument"], "advocate_confidence": parsed["confidence"]},
        goto="skeptic"
    )
```
(The skeptic node follows the same pattern, reporting `skeptic_confidence`.)

**Iterative refinement — round 2+ revises position in light of the rebuttal, rather than repeating:**
```python
def advocate_node_round2(state: DebateState) -> Command:
    response = llm.invoke(f"""
    Your original argument: {state['advocate_argument']}
    The skeptic's rebuttal: {state['skeptic_argument']}
    Revise your position — concede points that are valid,
    strengthen points that survive the rebuttal.
    Return JSON: {{"argument": "...", "confidence": 0.0}}
    """)
    # genuinely updates position based on rebuttal — not just escalating the same claim
```

**Judge node — now short-circuits on a decisive confidence gap before spending another full round:**
```python
def judge_node(state: DebateState) -> Command:
    gap = abs(state["advocate_confidence"] - state["skeptic_confidence"])
    
    if gap > 0.3:
        # confidence gap is decisive — no need for further rounds
        verdict = "SUPPORTED" if state["advocate_confidence"] > state["skeptic_confidence"] else "REJECTED"
        return Command(update={"verdict": verdict}, goto=END)
    
    if state["round_count"] >= 2:
        return Command(update={"verdict": "NEEDS_MORE_DATA"}, goto=END)
    
    return Command(goto="advocate")   # iterative refinement round — genuine revision, not repetition
```

This is a meaningful upgrade over the original Judge/Mediator-only version: it now uses Confidence-Based weighting to avoid unnecessary rounds when one side is clearly stronger, and genuine Iterative Refinement (not mere repetition) when the rounds do continue.

**Wiring the subgraph:**
```python
debate_builder = StateGraph(DebateState)
debate_builder.add_node("advocate", advocate_node)
debate_builder.add_node("skeptic", skeptic_node)
debate_builder.add_node("judge", judge_node)
debate_builder.add_edge(START, "advocate")
debate_subgraph = debate_builder.compile(checkpointer=checkpointer)
```

Following the nested checkpoint rule established above — this gets its **own thread_id** (e.g. `f"{case_id}-define-debate-{root_cause_id}"`) since it may need its own HITL interrupt if the verdict comes back `NEEDS_MORE_DATA` and the Belt needs to be asked for additional evidence mid-debate.

**Mounting inside the Analyse phase orchestrator:**
```python
def analyse_orchestrator(state: AnalyseState) -> Command:
    if state.get("proposed_root_cause") and not state.get("root_cause_validated"):
        return Command(goto="debate_subgraph")
    # ... other routing logic
```

The Analyse phase's internal orchestrator (the recursive pattern from Section 44) routes into the debate subgraph specifically when a root cause is proposed but not yet validated.

**What crosses back to AnalyseState — only the validated result, never the raw transcript:**
```python
class RootCauseValidation(BaseModel):
    root_cause: str
    verdict: str
    confidence: float
    key_concern: str | None   # if REJECTED or NEEDS_MORE_DATA, the main reason
```

Same Pydantic boundary-contract rule as everything else in Section 44 — the Analyse orchestrator reads this typed object, never parses the raw advocate/skeptic transcript.

**Why the engineering cost is justified specifically here:** root cause validation is the single highest-leverage decision point in the entire DMAIC project — every subsequent phase (Improve, Control) builds on whatever root cause gets confirmed here. A wrong root cause silently accepted by a single coaching LLM call is far more costly than the extra latency of a two-round adversarial debate before committing to it. This is not a pattern to apply everywhere — reserve it for the highest-stakes decision points in the workflow.

---

## 23. Modular Subgraph Architecture

*Source: Edureka course — Modular Subgraph Architectures and Subgraph Communication*

### Evolution: Monolith → Modular
```
Monolithic graph          → tightly coupled, fragile as complexity grows
    ↓
Decomposition             → self-contained subgraphs, each responsible for one function
    ↓
Clear interfaces          → typed input/output schemas
    ↓
Modular graph             → scalable, independently evolvable, easier to reason about
```

### Composable Subgraph Characteristics
- Self-contained unit with clear boundaries
- Encapsulates internal logic — external components interact only through defined interfaces
- Maintains its own internal state
- Supports independent versioning and deployment
- Built-in error handling
- **Same subgraph reusable across multiple workflows without duplicating logic**

### Subgraph Implementation Pattern
```python
# Subgraph has its own isolated state
class SubgraphState(MessagesState):
    summary: str    # internal field — parent never sees this

# Build subgraph independently
def build_subgraph(llm):
    graph = StateGraph(SubgraphState)
    graph.add_node("researcher", researcher_node)
    graph.add_node("summarizer", summarizer_node)
    graph.add_edge(START, "researcher")
    graph.add_edge("researcher", "summarizer")
    graph.add_edge("summarizer", END)
    return graph.compile()    # compiled = reusable component

# Parent embeds subgraph as a single node
subgraph = build_subgraph(llm)
parent_graph.add_node("research_team", subgraph)  # entire subgraph = one node
```

### Communication Between Parent and Subgraph
- Pass **summarized inputs** — not full message histories
- Return **structured results** — not raw agent outputs
- Maintain **internal state isolation** where possible
- Use shared state **selectively and intentionally**

### Naming Convention for Traceability
Prefix subgraph messages with `sub_` to distinguish from parent graph messages:
```python
HumanMessage(content=response, name="sub_researcher")  # inside subgraph
HumanMessage(content=response, name="parent_finalizer") # parent graph
```

### AgentLean Application
Each DMAIC phase subagent IS a subgraph. Define subgraph, Measure subgraph, etc. Each has its own private state (`DefineState`, `MeasureState`). The parent (Supervisor) embeds each as a single node. The subgraph's internal planner, executor, RAG calls, and extraction logic are invisible to the parent — the parent only sees the typed output it receives back.

---

## 24. Governance and Debugging — Production Readiness Framework

*Source: Edureka course — Role Play: Governing and Debugging a High-Risk Agent Workflow*

### Node Risk Classification Framework
Before placing HITL checkpoints, classify every node on two axes:
- **Consequence severity** — how bad if this output is wrong?
- **Reversibility** — can this action be undone?

Nodes that score high on either get `interrupt_before`.

### Three Mandatory Gate Points for Agent Improve

| Gate | Why | LangGraph Implementation |
|---|---|---|
| Plan approval | Human reviews dmaic_plan before any coaching fires | `interrupt_before=["start_coaching"]` |
| Gate evaluation | Belt reviews AI-extracted fields before phase advances | `interrupt_before=["gate_checkpoint"]` |
| Field correction | Belt corrects wrong values before they are committed | `Command(resume={"corrections": {...}})` |

### What the Human Reviewer Sees at Each Gate
- Structured snapshot pulled directly from state — no reformatting, no summarization
- Exactly what the agent produced
- Approval logged back into state with timestamp and reviewer ID
- Reviewer never asked to interpret raw LLM output

### Production Readiness Checklist

| Concern | Solution |
|---|---|
| Autonomous decision without checkpoint | `interrupt_before` on all high-consequence nodes |
| Mid-execution crash, no recovery | Checkpointer — resume from last valid checkpoint |
| Outputs nobody could audit | `step_log` in state + LangSmith traces |
| Non-deterministic behavior across runs | LangSmith run comparison — diff traces side by side |
| Failed segment debugging | Load checkpoint before failure, patch state, re-execute forward only |

### The Four-Part End-to-End Audit Answer
For any completed run, the system must be able to answer:
1. **What happened** — state envelope at every node
2. **Why** — node execution log + planner decision record
3. **Who approved it** — reviewer ID + timestamp in state
4. **When** — checkpoint timestamps

---

## 25. Architectural Gaps — Complete Register (Final)

*Consolidated from all sessions*

| Gap | Description | Prerequisite | Deferred To |
|---|---|---|---|
| 1 | No LangGraph checkpointer wired into `workflow.compile()` | PostgreSQL | Post-completion refactor |
| 2 | No human-in-the-loop interrupts at gate boundaries | Gap 1 | Post-completion refactor |
| 3 | Flat shared state — no private subagent state schemas | None | Post-completion refactor |
| 4 | No explicit planner nodes — planning implicit in prompts | None | Post-completion refactor |
| 5 | No tool encapsulation per subagent | Gap 3 | Post-completion refactor |
| 6 | No `step_log` audit trail — only `captured_fields` results | None | Post-completion refactor |
| 7 | No backward correction arcs — Analyse cannot send back to Define/Measure | Gap 1 | Post-completion refactor |
| 8 | No time travel debugging or snapshot analysis | Gap 1 | Automatic when Gap 1 resolved |
| 9 | No multi-user identity or session isolation | PostgreSQL | agentlean-* migration |
| 10 | No concurrency protection on blob writes | None | agentlean-* migration |
| 11 | No Azure OpenAI rate limit handling | None | agentlean-* migration |
| 12 | No tagged observability (user_id / project_id in traces) | None | agentlean-* migration |
| 13 | No debate-based root cause validation | Gaps 3,4,5 | Future enhancement |
| 14 | No context window management for long sessions | None | Post-completion refactor |

### Root Cause of All Gaps
LangGraph was used as a **graph router and state passer** rather than as a full agent framework. The graph was compiled but its agent capabilities were never activated.

### What Was Built Correctly
- LangGraph graph compilation and routing
- Hierarchical subgraph scaffold (Path C architecture)
- SSE streaming
- Azure Blob state persistence at gate boundaries
- LangSmith tracing
- Black Belt coaching prompt quality (150-400 word mandatory, teach/template/ask)
- Completeness-based extraction with anti-hallucination guards
- RAG retrieval from `improve_knowledge_index`

| 15 | Single-query RAG only — no multi-query retrieval on `improve_knowledge_index` | None | Post-completion refactor |
| 16 | No RAG Fusion or Reciprocal Rank Fusion — Azure AI Search default ranking only | Gap 15 | Post-completion refactor — evaluate after Gap 15 |
| 17 | CLOSED — Multi-hop retrieval fully designed in Section 71. Analyse phase primary target. Gate validation explicitly excluded. Implement via retrieval_strategy field in Phase Planner coaching_plan output. | Gap 15 | Implement during Phase Executor refactor |
| 18 | No query voting or weighted fusion — no cross-query result merging or re-ranking | Gap 15 | Post-completion refactor |
| 19 | No short-term memory summarisation — context window grows unbounded across long DMAIC sessions | None | Post-completion refactor |
| 20 | REVISED — improve_case_index with vector embedding and per-phase summaries exists. Remaining question: whether queried during active coaching turns. Vector field name asymmetry (content_vector vs embedding) must be resolved. | None | Audit during refactor |
| 21 | Metadata signals not applied in RAG queries — phase_relevance, status, created_at, belt_level all unused despite being indexed. Pure vector similarity only. | None | Quick win — filter additions only, no new infrastructure, do before refactor |
| 22 | No context orchestration layer — all memory sources injected without selection, ordering, or budget management | Gaps 19, 21 | Post-completion refactor |
| 23 | No rubric-based quality evaluation at gate boundaries — current gate check is binary (field present/absent), not qualitative | Gap 2 | Post-completion refactor |
| 24 | No Decision Agent or Observer Agent roles — only Coordinator and Worker roles exist and are not cleanly separated | Gaps 22, 23 | Post-completion refactor |
| 25 | CONFIRMED (was hypothetical) — Version drift verified against live docs June 2026. 25a: ConversationSummaryMemory/ConversationEntityMemory/VectorStoreRetrieverMemory deprecated, removal scheduled LangChain 2.0 — replace with Checkpointer+BaseStore split. 25b: create_react_agent deprecated in LangGraph v1, replaced by create_agent from langchain.agents — verify actually shipped before migrating. | None | HIGHEST PRIORITY — verify before Step 3.1 resumes, see Section 50 |
| 26 | No governance enforcement layers (Skills, Hooks) for Agent Improve — only CLAUDE.md/ARCHITECTURE.md (suggestion layer) exists | None | Recommend before Step 3.1 — PostToolUse hook + SessionStart hook |
| 27 | No anti-drift mechanisms — no /verify-current-version skill, no PostToolUse deprecated-pattern hook, no SessionStart version hook, no forum monitoring habit | Gap 25, 26 | Implement alongside Gap 25 fix, before Step 3.1 resumes |
| 28 | No opinion aggregation framework for combining decision quality signals — distinct from rank aggregation (Gap 16) and memory weighting (Gap 22) | Gaps 16, 22, debate subgraph (Section 22) | Lower priority — refinement after Gaps 22, 23 are in place |
| 29 | No Saga-based compensating actions for nodes with external side effects — gate reopening or time-travel debugging can leave improve_case_index/blob out of sync with rolled-back state | Gap 25 | Address before Gap 8 (time-travel) is used in production against systems with side effects |
| 30 | No thread_id length validation — PostgresSaver has a confirmed 255-character column limit; nested subgraph thread_id concatenation (case_id-phase-debate-rootcauseid) could exceed it on long descriptive identifiers | Gap 25 | Low effort — validate/use UUIDs for generated thread_id components, fix alongside Gap 25 |
| 31 | Subgraph-to-parent state propagation not verified immediate — officially documented LangGraph caveat that subgraph updates may not appear in parent state right away; Section 44 Mechanism 1 (shared key names) needs integration testing under actual installed version, not assumed | None | Integration-test before relying on DefineOutput-style boundary contracts; use Store if propagation lag confirmed |
| 32 | HumanInTheLoopMiddleware edit/reject behaviour not verified against installed versions — two confirmed open bugs: (a) edited tool-call args can be silently re-overwritten by agent re-attempting original call, (b) edit/reject confirmed broken in subagent/subgraph contexts, only approve reliable | None | CRITICAL — verify before Gap 2 considered resolved; outcome determines interrupt placement strategy (Orchestrator vs Phase Subgraph level) |
| 33 | No knowledge source traceability in coaching responses — coaching LLM draws on retrieved chunks with no record of which specific eBook sections grounded a decision; URI-cited MCP Resources would make every coaching response auditable | None | Implement alongside MCP server build for Agent Improve; directly relevant to DMAIC audit requirements |

### Resolution Decision
Complete all five DMAIC phases demo-ready with IMPR-2026-E9D first. Then execute the full refactor introducing all gaps above in dependency order starting with PostgreSQL + checkpointer.

---

## 26. Orion Intelligence — Graded Assignment Submission

*Source: Edureka course — Designing a Stateful, Multi-Agent Workflow System with LangGraph*
*Graded Assignment — Due Jun 29, 2026 — Submitted on time*

### Assignment Brief
Design a production-grade stateful multi-agent workflow system using LangGraph addressing:
- Workflow reliability and state management
- Governance, debugging, and human oversight
- Multi-agent coordination and scalability

### Submitted Proposal (847 words)

**Core argument:** State is the foundation of everything. Get state right and fault tolerance, debugging, and multi-agent coordination all follow naturally.

**Four guarantees delivered by the design:**
1. No execution progress is ever lost — checkpointing
2. No critical decision executes without a named human approving it — HITL interrupts
3. No failure is impossible to inspect and replay — time-travel debugging
4. No workflow logic needs to be duplicated — modular subgraphs

**Key concepts demonstrated:**
- Typed state with `TypedDict` and reducer patterns (`operator.add` for append-only, last-write-wins for scalars)
- `PostgresSaver` for production checkpointing, `InMemorySaver` for dev — single line swap at compile time
- Node risk classification on consequence severity + reversibility before placing interrupt gates
- Supervisor/Worker with no cross-agent awareness — workers focused, testable, reusable
- Debate agents with judge node for high-stakes decisions requiring multiple perspectives
- Compiled subgraphs as reusable components with typed input/output contracts

**Framing that distinguished the proposal:**
- "Right now human oversight means someone reviews outputs after they have already been acted on. That is not oversight, that is audit."
- "The architecture is the guarantee" — each of the four guarantees is delivered by a specific tested LangGraph capability, not an aspiration
- Node classification framework: consequence severity + reversibility as the principled basis for interrupt placement

### Grade and Feedback
No additional feedback received. All concepts correctly applied and present.

---

## 27. LCEL Pipelines — Why We Never Used Them

*Source: Edureka Course 2 — Applied Agentic AI Pipelines with LangChain*

### What We Do Now vs What Pipelines Give Us

**Current approach — manual chaining:**
```python
llm = get_llm()
prompt = build_prompt(state)
response = await llm.ainvoke(prompt)
extracted = extract_fields(response)
```

**LCEL pipeline approach — declarative composition:**
```python
chain = prompt_template | llm | output_parser | extraction_step
response = await chain.ainvoke({"input": state})
```

### Why Pipelines Matter for AgentLean

| Benefit | Current Gap | Pipeline Fix |
|---|---|---|
| Composability | Each step tightly coupled | Swap any step independently |
| Streaming | Manually wired SSE | Built into every chain automatically |
| Batch processing | Sequential only | `.abatch()` runs multiple inputs in parallel |
| Observability | One blob in LangSmith | Each step traced as separate span |
| Error handling | Ad-hoc retry logic | `.with_fallbacks()` and `.with_retry()` built in |

### Where Pipelines Belong in AgentLean

Inside **Phase Executor nodes** — the tool encapsulation gap:

```python
# Measure phase executor as an LCEL chain
measure_chain = (
    measure_prompt_template
    | get_llm()
    | StrOutputParser()
    | extraction_runnable
    | completeness_check_runnable
)
```

Each phase gets its own chain. The supervisor invokes the chain, not a series of manual calls. The node becomes thin — the chain is testable independently.

### The Two Levels — Pipelines vs Orchestrator

```
LangGraph (orchestrator)    = controls WHICH agents run and WHEN
                              manages state, routing, checkpointing, interrupts

LCEL Pipelines              = controls HOW each agent does its work internally
                              composes prompt → LLM → parser → extraction

LangChain                   = the materials both are built from
```

The orchestrator is the traffic controller. Pipelines are the engine inside each vehicle. Course 3 taught the blueprint. Course 2 teaches the plumbing. Course 4 teaches how to connect to the outside world (MCP).

---

## 28. LCEL Primitives — RunnableParallel, RunnableBranch, Pipe Operator

*Source: Edureka Course 2 — RunnableSequence for Data Enrichment demonstration*

### RunnableParallel — Fan-Out / Fan-In

Runs multiple Runnables **simultaneously** on the same input. Returns a dictionary of all results. **All branches must complete before the next pipe stage executes** — synchronisation barrier.

```python
parallel_stage = RunnableParallel(
    ticket=RunnableLambda(lambda d: d["ticket"]),
    urgency=RunnableLambda(lambda d: d["urgency"]),
    original=RunnablePassthrough(),     # passes input through unchanged
)
```

```
Input: d = {"ticket": "...", "urgency": "high", ...}
              ↓
    ┌─────────────────────────────┐
    │       RunnableParallel      │
    ├──────────┬──────────┬───────┤
  ticket    urgency   original
  (runs)    (runs)    (runs)      ← all three simultaneously
    └──────────┴──────────┴───────┘
              ↓ ALL must complete
Output: {"ticket": "...", "urgency": "high", "original": d}
```

**Key behaviours:**
- Performance: if each branch takes 1 second, total = ~1 second not ~3 seconds
- Guarantee: downstream always receives complete dictionary — never partial
- Failure: if any branch fails, whole parallel stage fails — no silent partial results

**`RunnablePassthrough`** — passes input through unchanged. Used to carry the full original input forward so later pipeline stages still have access to everything.

**AgentLean application:**
```python
analyse_parallel = RunnableParallel(
    rag_result=rag_lookup_runnable,       # hits Azure AI Search
    extracted=extraction_runnable,         # hits extraction LLM
    completeness=completeness_runnable,    # runs completeness scorer
    original=RunnablePassthrough(),
)
# coaching_node only fires when ALL THREE complete
workflow = analyse_parallel | coaching_node
```

Currently these run sequentially in manual code. Parallelising reduces latency since all three hit different services.

---

### RunnableBranch — Conditional Routing

Evaluates conditions in order. Executes **exactly one** branch — the first condition that returns True. Last argument with no condition is the default fallback.

```python
def is_high(data: dict) -> bool:
    return data["urgency"].lower() == "high"

def is_medium(data: dict) -> bool:
    return data["urgency"].lower() == "medium"

ticket_router = RunnableBranch(
    (is_high, high_branch),       # condition, branch
    (is_medium, medium_branch),   # condition, branch
    low_branch,                    # default — no condition
)
```

```
Input arrives
     ↓
is_high? → Yes → high_branch executes → done
     ↓ No
is_medium? → Yes → medium_branch executes → done
     ↓ No
low_branch executes (default) → done
```

**AgentLean application:**
RunnableBranch is the LCEL equivalent of LangGraph conditional routing — but operating **inside a single node** rather than at the graph level.

| Level | Tool | Used For |
|---|---|---|
| Graph routing | LangGraph conditional edges | Which phase subagent to invoke |
| Node-level routing | RunnableBranch | Which processing path within a node |

Inside the Analyse executor, RunnableBranch could route between "ask for more data" vs "proceed to validation" vs "trigger gate check" based on completeness score — without needing a new graph node for each path.

---

### The Pipe Operator `|` — Full Workflow Assembly

Chains Runnables declaratively. Output of left side becomes input of right side.

```python
# Overall shape:
# user_input → collect_inputs → parallel_stage → ticket_router
workflow = collector_runnable | parallel_stage | ticket_router
```

**Compare:**
```python
# Manual — what AgentLean does now
result1 = await step1.ainvoke(input)
result2 = await step2.ainvoke(result1)
result3 = await step3.ainvoke(result2)

# LCEL — declarative, composable, auto-streaming
workflow = step1 | step2 | step3
result = await workflow.ainvoke(input)
```

Same outcome. LCEL version is testable at each step, streams automatically, traces each step independently in LangSmith.

---

### RunnableLambda

Wraps any Python function into a Runnable so it can participate in a pipeline chain.

```python
collector_runnable = RunnableLambda(collect_inputs)
```

---

## 29. OutputFixingParser

*Source: Edureka Course 2 — OutputFixingParser: Role and Workflow*

### What It Is

Checks LLM output against a schema and **automatically fixes errors** to ensure the final result follows the required format. All correction logic is inside the parser — you write none of it.

### How It Works

```
LLM Output → Validate → Valid Output → Output
                ↓ Invalid
            Fix with LLM → Validate Again → Output
```

The parser calls the LLM a second time with a correction prompt if the first output fails validation. Then validates again before passing the result downstream.

### Comparison to What AgentLean Uses

| Approach | How it works | Where logic lives |
|---|---|---|
| Reflection node | Separate LangGraph node re-invokes LLM on bad output | Explicit in graph — visible, controllable |
| Pydantic structured output | LLM instructed to return JSON matching schema | Enforced at prompt level |
| OutputFixingParser | Parser catches bad output, auto-fixes via second LLM call | Hidden inside parser — automatic |

### Tradeoffs

**OutputFixingParser advantages:**
- Zero boilerplate — no extra graph node needed
- Works inside any LCEL chain automatically
- Cleaner graph topology

**Reflection node advantages:**
- Fully visible in LangGraph trace
- You control retry logic, prompt, and fallback
- Fix attempt is a first-class graph event with its own checkpoint

### Three-Layer Defence for Agent Improve Extraction

```
LLM coaching response
        ↓
OutputFixingParser    ← catches malformed JSON, auto-fixes
        ↓
Pydantic validation   ← enforces schema correctness
        ↓
Completeness check    ← catches missing or hallucinated fields
        ↓
state["captured_fields"]
```

Three layers instead of one. Directly addresses the extraction hallucination gap documented in Gap 6.

---

## 30. Semantic Routing vs LLM-Assisted Routing

*Source: Edureka Course 2*

### Semantic Routing

Uses **embedding similarity** to decide which branch. No LLM call for the routing decision.

```python
routes = {
    "billing":   "payment invoice charge refund subscription",
    "technical": "error crash bug connection timeout",
    "general":   "hours location contact information"
}
# Input embedded → cosine similarity against route embeddings → highest score wins
```

### LLM-Assisted Routing

Uses an **LLM call** to reason about the input and decide the route.

```python
routing_prompt = """
Classify this ticket into exactly one category: BILLING, TECHNICAL, or GENERAL.
Ticket: {input}
Return only the category name.
"""
# LLM response → parsed → branch executes
```

### Comparison

| Factor | Semantic Routing | LLM-Assisted Routing |
|---|---|---|
| Speed | Fast — vector math only | Slower — LLM call |
| Cost | Cheap | More expensive |
| Determinism | Deterministic | Non-deterministic |
| Handles ambiguity | Poorly | Well |
| Handles complex intent | Poorly | Well |
| Explainability | Low — similarity score only | High — LLM can explain decision |

### When to Use Which

**Semantic routing:** clearly distinct categories, high volume, predictable input language, speed and cost priority.

**LLM-assisted routing:** ambiguous or multi-intent input, categories require reasoning, correctness over speed, lower volume.

### AgentLean Application

DMAIC phase routing requires **LLM-assisted routing** — not semantic routing. The routing decision depends on completeness scores and field states, not semantic similarity of user input. The supervisor planner needs to reason about what is missing and what phase is appropriate, not just match keywords.

---

## 31. Course 2 Progress Notes

*Edureka — Applied Agentic AI Pipelines with LangChain*

### Topics Covered So Far
- [x] RunnableSequence for data enrichment
- [x] RunnableParallel — fan-out/fan-in pattern
- [x] RunnablePassthrough
- [x] RunnableBranch — conditional routing
- [x] Pipe operator `|` — workflow assembly
- [x] RunnableLambda
- [x] OutputFixingParser
- [x] Semantic routing vs LLM-assisted routing

### Topics To Capture As Covered
- [ ] Adaptive memory architectures
- [ ] Multi-query retrieval patterns
- [ ] Error handling and output correction in pipelines
- [ ] Context window management for long sessions
- [ ] ReAct pattern implementation details (if new patterns shown)

---

*Next: Course 4 — Developing MCP-Powered Agentic AI Systems*
*All content captured. Commit to repo when both courses complete.*

---

## 32. Multi-Query Retrieval

*Source: Edureka Course 2 — Retrieval, Fusion Techniques, and Multi-Hop Reasoning*

### What It Is
Enhances document retrieval by generating multiple alternative versions of a single user query. Expands search coverage, improves diversity, and overcomes the limitations of single-query retrieval.

### The Problem It Solves
A single query often misses relevant documents because the wording does not match how content was indexed.

```
Single query: "agent error rate"
Misses: "representative performance", "call handling quality", "AHT metrics"

Multi-query generates alternatives:
  "agent error rate reduction techniques"
  "call center representative performance issues"  
  "AHT and quality metrics improvement"
  "contact center coaching methodology"
→ All run in parallel → results merged and deduplicated → richer document set
```

### Three Steps
1. **LLM-based Query Generation** — LLM rewrites original query into multiple alternative phrasings capturing different angles
2. **Parallel Retrieval** — all alternative queries hit the retriever simultaneously (RunnableParallel applied to RAG)
3. **Union and Deduplication** — all result sets merged, duplicates removed

### What Agent Improve Actually Uses
Azure AI Search with `improve_knowledge_index` already implements **hybrid retrieval** — combining:
- **BM25** — keyword-based lexical search
- **Vector search** — semantic embedding similarity

This is more sophisticated than a pure vector retriever. BM25 handles exact terminology matches while vector search handles semantic similarity. The vocabulary mismatch problem is already partially addressed.

### The Actual Gap
Not "missing BM25" — we have that. The gap is sending **one query** to an already good hybrid retriever when multiple alternative query formulations would return broader concept coverage.

```
Hybrid BM25 + Vector (what we have)
→ Good at matching terminology used
→ Still limited to ONE query formulation
→ Misses concepts the Belt did not explicitly mention

Multi-query on top of hybrid (what we could add)
→ LLM generates alternative phrasings
→ Each hits the same hybrid retriever
→ Broader concept coverage beyond what Belt explicitly stated
```

### Most Affected Phase
Analyse phase — where concepts appear under multiple terminologies in the eBook:
```
"root cause analysis" also appears as:
  "cause and effect analysis"
  "fishbone diagram methodology" 
  "5 Why technique"
  "Ishikawa diagram"
  "potential cause identification"
```
Single query catches some. Multi-query catches all.

### Implementation — On Top of Existing Hybrid Retriever
```python
from langchain.retrievers.multi_query import MultiQueryRetriever

retriever = MultiQueryRetriever.from_llm(
    retriever=azure_search.as_retriever(),  # existing hybrid retriever
    llm=get_llm()
)
```

### Gap Register
**Gap 15** — single query formulation only. The hybrid BM25+vector retriever is already correct. Adding multi-query is an **incremental improvement**, not a fundamental fix. Lower priority than Gaps 1-14. Deferred to post-completion refactor.

---

## 33. RAG Fusion

*Source: Edureka Course 2 — Retrieval, Fusion Techniques, and Multi-Hop Reasoning*

### What It Is
Fusion techniques combine results from multiple query searches to create a single more accurate and relevant ranked list of documents.

### The 5-Step RAG Fusion Workflow

```
1. Query Expansion       → LLM generates multiple query variants from original
2. Vector Retrieval      → each variant hits vector store in parallel
3. Document Aggregation  → all result sets collected together
4. Reciprocal Rank Fusion → documents re-ranked by cross-result consistency
5. Final Context for LLM → best-ranked documents sent as context
```

### The Key Differentiator — Reciprocal Rank Fusion (RRF)

What makes RAG Fusion different from plain multi-query retrieval is the re-ranking step:

```
Document appears in 1 result set only    → low rank
Document appears in 3 result sets        → high rank — consistently relevant
Document appears in all 4 result sets    → top rank — definitively relevant
```

Documents relevant across multiple different query phrasings are more likely to be genuinely relevant than documents matching only one specific phrasing.

### Agent Improve Gap Assessment

| Step | RAG Fusion | Agent Improve |
|---|---|---|
| Query expansion | ✅ LLM generates variants | ❌ single query only |
| Retrieval | ✅ parallel per variant | ✅ hybrid BM25 + vector already |
| Document aggregation | ✅ all sets collected | ❌ one result set |
| Reciprocal Rank Fusion | ✅ cross-result re-ranking | ❌ Azure AI Search default ranking |
| Final context | ✅ best ranked docs | ✅ top-k by default score |

### Priority Assessment
Azure AI Search already does sophisticated hybrid ranking internally. RRF on top of a hybrid retriever is a diminishing returns improvement.

RAG improvement priority order:
1. Multi-query (Gap 15) — moderate gain, low effort
2. RAG Fusion (Gap 16) — marginal gain on top of hybrid, higher effort

### Gap Register
Added as **Gap 16** — RAG Fusion not implemented. Lower priority than Gap 15. Deferred to post-completion refactor. Evaluate after Gap 15 is implemented to determine if additional gain justifies the effort.

---

## 34. Multi-Hop Reasoning

*Source: Edureka Course 2 — Retrieval, Fusion Techniques, and Multi-Hop Reasoning*

### What It Is
The ability of an AI system to answer complex multi-step questions by retrieving information across multiple sources and logically connecting them. Each retrieval hop depends on the result of the previous hop.

### Single-Hop vs Multi-Hop

**Single-hop (what Agent Improve does now):**
```
Question → one RAG query → retrieve chunks → LLM answers
Works when the answer lives in one place.
```

**Multi-hop (what we are missing):**
```
Complex question
        ↓
Hop 1: retrieve first piece of information
        ↓ (result informs next query)
Hop 2: retrieve second piece based on Hop 1 result
        ↓ (result informs next query)
Hop 3: retrieve third piece based on Hop 2 result
        ↓
LLM connects all hops → answers the question
```

### Four Capabilities

- **Handles complex queries needing multiple steps** — builds context progressively rather than answering in one shot
- **Fixes basic RAG that fails on multi-chunk answers** — when the answer is spread across multiple document sections that need logical connection
- **Allows calculations, comparisons, and date logic** — reasoning across data retrieved from multiple places
- **Bridges retrieval to final task completion** — retrieved information is a stepping stone, not the final answer

### Why Critical for Agent Improve

DMAIC coaching questions are inherently multi-hop:

```
Belt: "We have sigma 2.1, root cause is agent training gaps, 
       constraint is 6 weeks — what improvement approach?"

Hop 1: what does sigma 2.1 mean for process capability
Hop 2: what approaches address training-related root causes
Hop 3: what can realistically be implemented in 6 weeks
Hop 4: intersection of above → the actual recommendation
```

Current single-hop RAG retrieves something relevant but cannot chain these retrievals. The LLM fills gaps from training data — exactly where hallucination risk comes from.

### Connection to TAO Loop
```
TAO Loop        = multi-hop reasoning applied to agent actions
Multi-hop RAG   = TAO Loop applied specifically to retrieval

Each hop:
THOUGHT:  "I need more specific info based on what I just retrieved"
ACTION:   retrieve next relevant chunk
OBSERVE:  got new information
THOUGHT:  "Now I can retrieve the next piece"
```

### Gap Register
Added as **Gap 17** — no multi-hop reasoning. Single retrieval step only. Complex DMAIC questions that require chaining multiple knowledge pieces are answered from LLM training data rather than grounded retrieval. This is a significant quality gap for the Analyse and Improve phases specifically. Depends on multi-query infrastructure (Gap 15) as a prerequisite. Deferred to post-completion refactor.

---

## 35. Query Voting and Weighted Fusion

*Source: Edureka Course 2 — Retrieval, Fusion Techniques, and Multi-Hop Reasoning*

### What It Is
After running multiple queries against a retriever, the results need to be merged intelligently. Simple deduplication is not enough — documents need to be ranked by how relevant they are across all query results combined.

Two approaches:

---

### Simple Voting Fusion
Each document gets one vote for every query result set it appears in. Documents are ranked by vote count.

```
Query 1 results: [Doc A, Doc B, Doc C]
Query 2 results: [Doc B, Doc D, Doc E]
Query 3 results: [Doc A, Doc B, Doc F]

Votes:
  Doc A → 2 votes
  Doc B → 3 votes  ← top ranked, appeared in all three
  Doc C → 1 vote
  Doc D → 1 vote
  Doc E → 1 vote
  Doc F → 1 vote

Final ranked list: Doc B, Doc A, then remainder
```

Documents consistently retrieved across multiple query phrasings are demonstrably more relevant than documents that only match one specific phrasing.

---

### Weighted Fusion
Assigns different weights to queries based on their quality, specificity, or source. More important queries influence the final ranking more than less important ones.

```python
# Example — original query weighted higher than generated alternatives
weights = {
    "original_query": 1.0,      # highest weight — direct user intent
    "generated_query_1": 0.7,   # alternative phrasing
    "generated_query_2": 0.7,   # alternative phrasing
    "domain_specific_query": 0.9  # high weight — domain knowledge
}

# Document score = sum of (rank_in_result_set * query_weight)
```

---

### Reciprocal Rank Fusion (RRF) — The Production Standard
The most robust fusion approach. Rewards documents that consistently appear at the top of multiple result sets.

```python
# RRF formula
RRF_score(doc) = sum(1 / (k + rank_in_result_set_i))
# k = constant (typically 60) to dampen the impact of top ranks
```

A document ranked 1st in one result and 3rd in another scores higher than a document ranked 1st in one result and not appearing in others.

---

### What Agent Improve Uses Today
None of the above. Azure AI Search returns a single ranked result set from a single query. There is no cross-query fusion of any kind.

```
Current:  one query → Azure AI Search → ranked results by hybrid score → top-k to LLM
Missing:  multiple queries → multiple result sets → fusion → re-ranked combined list → top-k to LLM
```

---

### Why Simple Voting and Weighted Fusion Are Critical

For DMAIC specifically, different query phrasings surface different parts of the Black Belt eBook. A root cause analysis question might be answered by:
- The Analyse phase methodology chapter (surfaces on query about "root cause")
- The fishbone diagram section (surfaces on query about "cause and effect")
- The hypothesis testing chapter (surfaces on query about "validating causes")

Without fusion, the coaching response is grounded in whichever chunk happened to rank highest for the single query used. With fusion, all three relevant sections contribute to the context — the coaching response is richer and more complete.

---

### Implementation

```python
from langchain.retrievers import EnsembleRetriever

# Combine multiple retrievers with weights
ensemble_retriever = EnsembleRetriever(
    retrievers=[bm25_retriever, vector_retriever],
    weights=[0.4, 0.6]
)

# Or implement RRF manually after MultiQueryRetriever
from langchain.retrievers.multi_query import MultiQueryRetriever
# MultiQueryRetriever + custom RRF re-ranking function
```

---

### Gap Register
Added as **Gap 18** — no query voting or weighted fusion across multiple query results. Agent Improve relies entirely on Azure AI Search's internal ranking from a single query. Simple voting and weighted fusion are the minimum viable improvement; RRF is the production standard. Prerequisite: Gap 15 (multi-query must be in place before fusion makes sense). Deferred to post-completion refactor.

---

## 36. Short-Term and Long-Term Vector Memory

*Source: Edureka Course 2 — Applied Agentic AI Pipelines with LangChain*

### What It Is
Vector memory organised into two layers to balance immediacy and durability — mirroring human working memory and long-term recall.

### Short-Term Vector Memory
- Stores recent interactions and task-specific context
- Ensures smooth continuity within active conversations
- Frequently updated — may be overwritten, summarized, or discarded as tasks progress
- Lives for the duration of a session or task

### Long-Term Vector Memory
- Stores durable knowledge: historical conversations, learned facts, preferences, domain expertise
- Persists across sessions
- Important short-term information can be **promoted** into long-term storage to prevent loss

---

### What Agent Improve Actually Has — Verified Index Schemas

**improve_knowledge_index (7 fields)**
| Field | Type |
|---|---|
| id | Edm.String |
| content | Edm.String |
| content_vector | Collection(Edm.Single) — vector |
| metadata | Edm.String |
| source_file | Edm.String |
| phase_relevance | Edm.String |
| page_number | Edm.Int32 |

Static Black Belt eBook content. Same for every project, every Belt. Never updated at runtime.

**improve_case_index (19 fields)**
| Field | Type |
|---|---|
| id, case_id, title | Edm.String |
| belt_level, leader, department | Edm.String |
| current_phase, rag_status, status | Edm.String |
| created_at, target_date | Edm.String |
| days_in_phase | Edm.Int32 |
| phase_summary_define | Edm.String |
| phase_summary_measure | Edm.String |
| phase_summary_analyse_phase | Edm.String |
| phase_summary_improve | Edm.String |
| phase_summary_control | Edm.String |
| content_text | Edm.String |
| embedding | Collection(Edm.Single) — vector |

Live case data with per-phase summaries and vector embedding. This IS long-term vector memory for cross-case retrieval.

---

### Revised Gap Assessment

With `improve_case_index` in place the picture is significantly better than assumed:

| Memory Type | What We Have | What Is Still Missing |
|---|---|---|
| Short-term | `messages[]` in state — current session | Summarisation when context window fills |
| Long-term methodology | `improve_knowledge_index` — eBook | Nothing — this is complete |
| Long-term case data | `improve_case_index` — per-phase summaries + vector | Nothing — this exists |
| Context management | No mechanism | Summarisation strategy for long sessions |

**Gap 20 is largely resolved** — `improve_case_index` with `embedding` field provides semantic retrieval across cases. The five `phase_summary_*` fields enable per-phase cross-case pattern retrieval.

**Gap 19 remains valid** — context window management for long `messages[]` histories is still missing regardless of what indexes exist. As a DMAIC project progresses across 30+ conversation turns, the context window grows unbounded.

---

### Critical Technical Note — Vector Field Name Asymmetry

The two indexes use different vector field names:
- `improve_knowledge_index` → `content_vector`
- `improve_case_index` → `embedding`

Any shared retriever or tool must map these explicitly. If normalisation is not handled, a shared RAG tool will fail silently on one index. This should be addressed during the refactor when tools are encapsulated per subagent.

---

### .env File Issue — Two Files, One Correct
- App loads `agent-improve/.env`
- Root `.env` exists and can silently shadow values depending on `load_dotenv()` search order
- Correct env var is `AZURE_SEARCH_API_KEY` not `AZURE_SEARCH_KEY`
- Root `.env` should be audited — remove if redundant to prevent silent shadowing

---

### Short-Term Memory — What It Actually Means at Runtime

**Where everything is stored:**
```
Azure Blob Storage
└── case_id/state.json
    ├── messages[]           ← EVERY message ever sent, grows forever
    ├── captured_fields{}    ← structured extracted fields
    ├── current_phase        ← which phase we are in
    └── completeness_score   ← per phase

Azure AI Search
├── improve_knowledge_index  ← eBook, static, never changes
└── improve_case_index       ← case summaries per phase, vector embedded

RAM (lives only during one HTTP request)
└── LangGraph state object   ← loaded from blob, used, saved back to blob
```

**The problem — messages[] grows forever:**
```
Request 1:  messages[] = [m1, m2]        → saved to blob
Request 2:  messages[] = [m1..m4]        → saved to blob
Request 30: messages[] = [m1..m60]       → saved to blob
Request 60: messages[] = [m1..m120]      → blob growing
                          ALL sent to Azure OpenAI every request
                          gpt-4o limit = 128k tokens
                          when hit → oldest messages silently dropped
                          Belt said something important in session 2
                          by session 40 the LLM cannot see it anymore
```

**Who triggers summarisation and when — currently nobody:**
No trigger exists. No summarisation happens. Gap 19 is real.

### Short-Term Memory — Revised Implementation: Structured JSON Not Prose Summary

**Why prose summary is wrong:**
- Forces LLM to parse natural language to extract facts — introduces interpretation variance
- Duplicates information already in `captured_fields` in a worse format
- Inconsistent — LLM may read the same summary differently each time

**Why structured JSON is correct:**
- LLM reads exact values directly — no interpretation needed
- Same format as blob state — no translation layer
- Aligns with typed state schema principle from planner/executor pattern
- Compact — JSON is more token-efficient than prose paragraphs

**What the structured context looks like:**
```python
conversation_context = {
    "project_summary": {
        "phases_completed": ["define", "measure"],
        "current_phase": "analyse",
        "key_decisions": [
            "scope limited to billing calls only",
            "measurement system validated via GR&R"
        ]
    },
    "captured_fields": {
        "what": "Complaint rate exceeding 8.3%",
        "baseline_mean": 4.2,
        "baseline_sigma": 2.1,
        "root_cause_statement": None
    },
    "open_items": ["root_cause_statement", "contributing_factors"]
}
```

**What the LLM receives each turn:**
```python
system_prompt = f"""
You are a Black Belt coach.

PROJECT STATE:
{json.dumps(conversation_context, indent=2)}

RECENT CONVERSATION:
{format_recent_messages(state["messages"][-10:])}

Continue coaching based on the above.
"""
```

Structured JSON for facts. Raw messages only for the most recent conversational thread. Clean separation.

**Revised implementation:**
```python
async def compress_messages(state):
    
    # build structured context from existing state — no LLM call needed
    structured_context = {
        "phases_completed": get_completed_phases(state),
        "captured_fields": state["captured_fields"],
        "key_decisions": extract_key_decisions(state["messages"][:-10]),
        "open_items": get_missing_fields(state)
    }
    
    # keep only last 10 messages as raw conversation
    recent_messages = state["messages"][-10:]
    
    return {
        **state,
        "conversation_context": structured_context,  # new typed state field
        "messages": recent_messages                   # trimmed
    }
```

`conversation_context` is a new typed field in the state schema. The gate node builds it from existing state — no extra LLM call required.

**Comparison:**

| Approach | Prose Summary | Structured JSON |
|---|---|---|
| LLM reads facts | Parses natural language | Reads structured data directly |
| Consistency | Varies per read | Same every time |
| Duplication | Duplicates captured_fields | References captured_fields directly |
| Token efficiency | Long paragraph | Compact JSON |
| Hallucination risk | LLM interprets summary | LLM reads exact values |
| Alignment with blob | Different format | Same format as blob state |

**The principle connection:**
Prose summary = planning buried in a prompt. Structured JSON context = explicit typed inspectable state. Same principle as planner/executor — make the reasoning explicit and structured rather than hidden in natural language.

---

## 37. Memory Patterns in Agentic Systems

*Source: Edureka Course 2 — Applied Agentic AI Pipelines with LangChain*

---

### Episodic Memory Pattern

Captures specific experiences or events as distinct memory entries.

- Stores records of past conversations, decisions made, and outcomes of previous actions with contextual metadata
- Allows the system to recall what happened previously, under what conditions, and with what results
- Supports personalisation by enabling responses that reference prior interactions
- Especially useful for conversational assistants that must adapt behaviour over time
- Enables experience-driven reasoning and continuity across interactions

**AgentLean mapping:**
`improve_case_index` with `phase_summary_*` fields IS episodic memory. Each completed DMAIC phase is a distinct experience entry — what happened, what was decided, what the outcome was. The Belt's history across sessions is episodic memory.

**What is still missing:** per-turn episodic entries. Currently only gate-level summaries are stored. Individual coaching decisions and their outcomes are not recorded as retrievable memories.

---

### Semantic Memory Pattern

Stores generalised knowledge rather than individual events.

- Includes facts, definitions, procedures, policies, and conceptual knowledge that remain relevant over long periods
- Acts as a stable knowledge base supporting consistent and grounded responses
- Typically shared across users or agents — not tied to a single interaction history
- In RAG systems, semantic memory plays the central role in factual grounding

**AgentLean mapping:**
`improve_knowledge_index` IS semantic memory. The Black Belt eBook — methodology, tools, techniques — is generalised knowledge shared across all Belts, all projects, all industries. It never changes based on individual interactions.

**We have this fully implemented.** No gap here.

---

### Working Memory and Context Management

LLMs have limited context windows — memory management is essential.

- Recent interactions kept directly in prompt context for immediate conversational continuity
- Older or less relevant information summarised to reduce context size while preserving meaning
- Summaries stored as vector embeddings for future retrieval when needed
- Balances focus on present task with long-term recall capability

**AgentLean mapping:**
This is **Gap 19** — exactly what was discussed in Section 36. `messages[]` in state grows unbounded. No summarisation trigger exists. No vector embedding of compressed summaries.

**Implementation target:**
```
Recent messages (last 20)  → kept in full in messages[]
Older messages             → summarised at gate boundary
Summaries                  → stored in improve_case_index as vector embeddings
                             retrievable in future sessions
```

---

### Vector Memory in Agent-Based Systems

Enables agents to learn and improve over time.

- Agents store tool usage results, reasoning traces, feedback, and environmental observations as retrievable memories
- Stored experiences allow recognition of patterns in past successes and failures
- Memory-driven learning helps avoid repeating mistakes and refine planning strategies
- Transforms agents from reactive responders into adaptive, experience-aware systems

**AgentLean mapping:**
This is the future state of `improve_case_index`. Today it stores structured summaries. The full vision is:
- Storing which coaching questions worked for specific problem types
- Storing which root causes were validated vs rejected and why
- Storing which improvement approaches succeeded in which industry contexts
- Enabling the coach to say "in similar situations this approach worked" grounded in real cases

**Current gap:** tool usage results and reasoning traces are not stored. Only phase summaries and captured fields. LangSmith has the traces but they are not retrievable by the coaching agent.

---

### Memory Retrieval and Control Strategies

Uncontrolled retrieval introduces noise into model reasoning.

- Similarity thresholds ensure only sufficiently relevant memories are retrieved
- Metadata filters — time, user identity, task type — scope retrieval appropriately
- Episodic and semantic memories use separate retrieval strategies
- Retrieved memory volume carefully limited to fit context window constraints

**AgentLean mapping:**

| Control | Current State | Gap |
|---|---|---|
| Similarity threshold | Azure AI Search default scoring | No explicit threshold configured |
| Metadata filters | `phase_relevance` field in knowledge index | Not used in current RAG queries |
| Separate retrieval strategies | Both indexes queried same way | Should differ — eBook vs case data |
| Volume limiting | top-k results | Basic — no dynamic sizing based on context remaining |

The `phase_relevance` field in `improve_knowledge_index` exists specifically to filter by DMAIC phase but is not currently used in RAG queries. This is a quick win — filtering by current phase before semantic search would immediately improve retrieval precision.

**Gap 21 — `phase_relevance` filter not applied in RAG queries despite field existing in index.**

---

### Governance and Memory Hygiene

Persistent memory introduces quality, privacy, and compliance considerations.

- Outdated or low-quality memories must be pruned to prevent system behaviour degradation
- Sensitive user-specific information must be isolated through access controls
- Critical memories may require validation or human review before long-term storage
- Audit logs track what information is stored, retrieved, and used

**AgentLean mapping:**

| Governance Concern | Current State | Gap |
|---|---|---|
| Memory pruning | No pruning mechanism | Old case data accumulates without quality control |
| Access controls | No user isolation | Any case_id accessible to any request |
| Human review before storage | Gate auto-writes to blob | HITL interrupt (Gap 2) would fix this |
| Audit logs | LangSmith traces | Not linked to memory operations specifically |

The HITL interrupt (Gap 2) directly addresses the human review governance requirement — Belt approves what gets committed before it is stored. The other governance gaps are production-scale concerns deferred to the `agentlean-*` migration.

---

### Gap Register Additions
- **Gap 21** — `phase_relevance` metadata filter exists in `improve_knowledge_index` but is not applied in RAG queries. Quick win — one line filter addition. Low effort, immediate precision improvement.

---

## 38. Hybrid Memory Stack and Context Orchestration Layer

*Source: Edureka Course 2 — Applied Agentic AI Pipelines with LangChain*

### The Four Components of a Hybrid Memory Stack

| Component | What It Stores | When Used |
|---|---|---|
| Short-Term Memory | Recent conversation state and immediate inputs | During active interactions and turn-by-turn reasoning |
| Long-Term Memory | Persistent user, task, and domain knowledge | When historical context or personalisation is required |
| External Knowledge Sources | Documents, vector databases, tools, APIs | When factual, domain, or real-time data is needed |
| Context Orchestration Layer | Memory selection rules and injection logic | Continuously, to control relevance and timing |

### AgentLean Status Against Each Component

| Component | AgentLean | Status |
|---|---|---|
| Short-Term Memory | messages[] in state | ✅ exists, Gap 19 to fix |
| Long-Term Memory | improve_case_index | ✅ exists |
| External Knowledge | improve_knowledge_index | ✅ exists |
| Context Orchestration Layer | Nothing | ❌ completely missing — Gap 22 |

---

### What the Context Orchestration Layer Is

A **gatekeeper and budget manager** that sits between ALL memory sources and the LLM. Every LLM call goes through it. It decides what gets injected, in what order, and how much.

**Correct flow:**
```
Short-Term Memory (messages[])
Long-Term Memory (improve_case_index)         → ALL feed INTO → Context Orchestration Layer → LLM
External Knowledge (improve_knowledge_index)
```

It does NOT sit in sequence after the memory sources. It controls all of them simultaneously.

---

### What the Orchestrator Decides Before Every LLM Call

```
Context Orchestration Layer asks:

From Short-Term:   which recent messages are relevant?
                   how many fit in the remaining budget?

From Long-Term:    are there past case summaries relevant to this turn?
                   inject only if relevant, only what fits

From External:     which RAG chunks scored above threshold?
                   inject only top scoring, only what fits

Budget check:      total tokens across all three sources < limit?
                   if over → cut least relevant first
                        ↓
                   Final assembled context → LLM → Response
```

---

### Agent Improve Today — No Orchestration

```
messages[]           → all of them, always
RAG chunks           → top-k, always, no threshold check
captured_fields      → buried inside old messages
                            ↓
                       everything → LLM (no selection, no ordering, no budget)
```

---

### Agent Improve After Gap 22 Is Fixed

```
messages[]           → orchestrator: last 10 only
RAG chunks           → orchestrator: only score > 0.8, max 3 chunks
captured_fields      → orchestrator: inject as structured JSON first
phase context        → orchestrator: only current phase fields prominent
                            ↓
                       selected + ordered + budget-managed → LLM
```

---

### Implementation Pattern

```python
async def build_context(state, retrieved_docs):
    
    budget = CONTEXT_WINDOW_LIMIT
    context_parts = []
    
    # 1. System prompt — always first, non-negotiable
    context_parts.append(system_prompt)
    budget -= token_count(system_prompt)
    
    # 2. Structured project state — always included (Gap 19 fix)
    project_state = build_structured_context(state)
    context_parts.append(project_state)
    budget -= token_count(project_state)
    
    # 3. Retrieved RAG chunks — only if relevant enough
    for chunk in retrieved_docs:
        if chunk.score > RELEVANCE_THRESHOLD and budget > 500:
            context_parts.append(chunk.content)
            budget -= token_count(chunk.content)
    
    # 4. Recent messages — fill remaining budget
    recent = fit_messages_to_budget(state["messages"], budget)
    context_parts.append(recent)
    
    return build_prompt(context_parts)
```

---

### The Briefing Document Analogy

You do not walk into a meeting and hand someone 300 pages of everything that ever happened. You prepare a one-page briefing with exactly what they need to know right now.

The Context Orchestration Layer prepares that briefing for the LLM before every single coaching turn.

---

### The Five Components of Unified Memory Coordination

From the course slide — the Context Orchestration Layer internally manages five concerns:

| # | Component | What It Does |
|---|---|---|
| 01 | Short-Term Memory | Maintains immediate conversational continuity |
| 02 | Long-Term Memory | Stores user preferences and historical knowledge |
| 03 | External Memory | Provides factual or real-time information |
| 04 | Memory Prioritization | Ranks memory layers based on relevance |
| 05 | Conflict Resolution | Resolves inconsistencies across memory sources |

Items 01-03 are the memory sources. Items 04-05 are what the orchestration layer does with them.

---

### Memory Prioritization

When all three memory sources return content for the same turn, the orchestrator decides which takes priority — injected first, given more tokens, wins when budget is tight.

```python
# Priority rules for Agent Improve
MEMORY_PRIORITY = {
    "external_knowledge": 1,   # highest — eBook is authoritative methodology
    "captured_fields":    2,   # second — Belt's own confirmed facts
    "long_term_case":     3,   # third — past case patterns
    "recent_messages":    4,   # last — recent conversational context
}
```

Example — Belt asks "what statistical test should I use to validate my root cause?":
```
Short-term:      "Belt mentioned chi-square in session 3"
Long-term:       "In a similar case, hypothesis testing was used"
External:        "Black Belt eBook recommends ANOVA for this scenario"

Without prioritization: LLM sees all three and picks arbitrarily
With prioritization:    External knowledge (rank 1) injected first
                        LLM grounds response in methodology first
                        then considers case history and Belt's prior mention
```

---

### Conflict Resolution

When two memory sources say contradictory things, the orchestrator applies defined rules rather than letting the LLM decide.

**The real risk for Agent Improve:**
```
Week 1: Belt confirms baseline_mean = 4.2  → captured at Define gate
Week 3: Belt says "I recalculated, actually 3.8"
Week 4: Belt says "manager wants 4.0 for reporting"

Three different values across memory sources.
Without conflict resolution: coach gives inconsistent answers across turns
With conflict resolution:    defined rule applied every time
```

**Conflict resolution rules:**
```python
CONFLICT_RULES = {
    # most recent Belt statement beats old captured_fields
    "recent_message_vs_captured_field": "recent_message_wins",
    
    # captured_fields beats long-term case memory
    "captured_field_vs_case_memory": "captured_field_wins",
    
    # eBook methodology beats case memory
    "external_knowledge_vs_case_memory": "external_knowledge_wins",
    
    # when uncertain — do not guess
    "unresolvable": "trigger_hitl_interrupt"
}
```

The last rule is critical — some conflicts cannot be resolved algorithmically. A Belt changing a gate-confirmed baseline value mid-phase should trigger a HITL interrupt before the new value overwrites the confirmed one. This connects directly to Gap 2 (HITL interrupts) and Gap 8 (field correction).

---

### Updated Gap 22 — Full Scope

Gap 22 is not just context injection. It contains four sub-components:

```
Gap 22 — Context Orchestration Layer
├── Memory selection      — what to include from each source
├── Budget management     — how many tokens each source gets
├── Memory Prioritization — which source wins when space is tight
└── Conflict Resolution   — which value wins when sources disagree
                            unresolvable conflicts → HITL interrupt
```

None of these four exist in Agent Improve today. All four are required for a production-grade coaching system where the Belt's data evolves across weeks and phases.

### Design Trade-offs and Implementation Considerations

*From course slide — four trade-offs every context orchestration layer must manage*

**1. Context Depth**
Balance relevance against token and latency limits. More context = better reasoning but higher cost and slower response. The orchestrator must decide how deep to go per memory source per turn.

**2. Retrieval Cost**
More memory layers increase accuracy but raise compute cost. Querying short-term + long-term + external on every single turn is expensive. The orchestrator should skip layers that are unlikely to be relevant for the current turn type.

**3. Injection Timing**
Early vs late context injection impacts reasoning quality. This is the least obvious trade-off.

LLMs read prompts top to bottom. What appears **earlier** gets more attention and anchors reasoning more strongly. What appears **late** gets less weight.

```
Early injection (authoritative facts first):
[System prompt]
[captured_fields JSON]        ← LLM reads project facts first
[RAG methodology chunks]      ← LLM reads methodology second
[Recent messages]
[Belt's current message]      ← LLM evaluates Belt's message
                                 through the lens of established facts

Late injection (conversation first):
[System prompt]
[Recent messages]
[Belt's current message]      ← LLM reads Belt's message first
[captured_fields JSON]        ← project facts arrive after LLM
[RAG chunks]                     has already started reasoning
                                 → response may drift toward Belt's suggestion
                                    rather than project-grounded answer
```

**Injection timing rule for Agent Improve:**

| Inject Early | Inject Late or Drop |
|---|---|
| captured_fields JSON | Old messages from week 1 |
| Current phase requirements | Low-scoring RAG chunks |
| Missing fields list | Tangential case history |
| High-scoring RAG chunks | Superseded values |
| System prompt | Conversational filler |

Today Agent Improve injects everything in the order it was appended to `messages[]`. There is no deliberate ordering. The Context Orchestration Layer (Gap 22) is what gives control over injection timing.

**4. System Complexity**
Greater flexibility requires stronger orchestration logic. Every rule added to the orchestrator is a decision point that must be maintained. The orchestration layer itself must be simple enough to reason about or it becomes a source of bugs rather than a solution.

### Self-Correcting Queries — Sub-Component of Gap 22

*Source: Edureka Course 2 — Self-correcting Queries Overview*

When a RAG query returns poor results, instead of silently passing bad context to the LLM, the system detects low confidence and automatically restructures and reissues the query.

```
Query issued → retriever returns low confidence results
                        ↓
              self-correction detects: low confidence signal
                        ↓
              restructures query with better terms
                        ↓
              reissues to retriever
                        ↓
              better results → LLM receives better context
```

**What Agent Improve does today:**
One query sent to Azure AI Search. Whatever comes back is used regardless of score quality. Poor retrieval = poor coaching context = weaker response — silently, no indication anything went wrong.

**Implementation pattern:**
```python
async def rag_with_self_correction(query: str, state: dict):
    results = await search(query)
    
    if max_score(results) < CONFIDENCE_THRESHOLD:
        better_query = await restructure_query_chain.ainvoke({
            "original_query": query,
            "poor_results": results,
            "phase": state["current_phase"]
        })
        results = await search(better_query)
    
    return results
```

**Connection to existing gaps:**
- Gap 15 — multi-query addresses this proactively by generating alternatives upfront
- Gap 17 — multi-hop includes adaptive re-querying based on hop results
- Gap 22 — context orchestration layer detects low confidence and triggers self-correction

Self-correcting queries is the reactive complement to multi-query's proactive approach. Run one query first, self-correct only when results are poor. More efficient than always running multiple queries.

**TAO loop connection:**
Self-correcting queries IS the TAO loop applied to retrieval — Thought (need methodology) → Action (query) → Observe (low confidence) → Thought (restructure) → Action (reissue). The same pattern as ReAct but operating at the retrieval level rather than the tool selection level.

```
Gap 19  working memory compression      ↘
Gap 21  phase_relevance filter           → feed into → Gap 22 context orchestration
Gaps 15-18  retrieval improvements      ↗
Gap 2   HITL interrupts                 ← triggered by conflict resolution
```

Gap 22 is the layer that makes all other memory and retrieval improvements work together coherently. Without it, fixing the individual gaps still results in uncontrolled context injection.

### Gap Register
**Gap 22** — no context orchestration layer. Missing all four sub-components: memory selection, budget management, memory prioritization, and conflict resolution. Unresolvable conflicts currently have no escalation path — they reach the LLM as contradictory context. Deferred to post-completion refactor. Depends on Gaps 19 and 21 being resolved first.

---

## 39. Knowledge Tools in Augmented Reasoning

*Source: Edureka Course 2 — Role of Knowledge Tools in Augmented Reasoning*

### What Augmented Reasoning Means
The LLM's reasoning is augmented by external knowledge tools — accessing information beyond its training data to produce grounded, fact-aware outputs.

### The Four Capabilities

**Accesses external knowledge beyond the model's training data**
Why `improve_knowledge_index` exists. gpt-4o was not trained on the specific Black Belt eBook. Without RAG the model answers Six Sigma questions from generic training data — potentially wrong, outdated, and not aligned with our methodology. The knowledge index gives it access to authoritative specific content.

**Retrieves documents, databases, and real-time information**
We retrieve from the eBook index and case index. What we do not retrieve is real-time process data — current complaint rates, live KPIs, SAP data. The Belt manually provides these numbers. This is the MCP gap — Course 4 addresses it.

**Enables verification, search, and computation capabilities**
Verification and search we have. Computation we do not. A SigmaCalculator tool would be a computation capability — the agent calculates sigma level from raw data rather than asking the Belt to calculate it themselves.

**Supports grounded and fact-aware reasoning outputs**
The anti-hallucination argument for RAG. Without it the coach invents methodology. With it the coach retrieves and cites actual Black Belt content. This is why the eBook index exists.

### What We Augment With Today vs What Is Missing

```
Today:
✅ Static methodology (improve_knowledge_index)
✅ Case history (improve_case_index)

Missing:
❌ Real-time process data (SAP, live KPIs)      → MCP — Course 4
❌ Computation tools (sigma calc, Cp/Cpk)        → local @tool decorated functions
❌ External verification (industry benchmarks)   → MCP — Course 4
```

### The Course 4 Connection
This slide is the motivation for MCP. The knowledge tools described — databases, real-time information, computation — are exactly what MCP servers expose. The eBook RAG is the foundation. MCP is what makes the knowledge tool suite complete.

A truly augmented DMAIC coach would:
- Pull live complaint rate data from SAP rather than asking the Belt
- Calculate sigma level from raw data rather than relying on Belt's calculation
- Verify improvement results against live KPIs rather than accepting reported numbers
- Reference industry benchmarks for context rather than relying on Belt's judgment alone

---

## 40. Metadata as a Signal: Freshness, Authority, and Context

*Source: Edureka Course 2 — Metadata as a Signal: Context, Freshness, and Authority*

### The Three Metadata Signals

**Freshness Signals** — how recent is this information? Should older content rank lower when relevance scores are similar?

**Authority and Trust Signals** — how authoritative is the source? Should verified expert content rank higher than general content?

**Metadata Intelligence** — using all available metadata fields together for smarter retrieval, not just vector similarity.

---

### AgentLean Mapping

**Freshness:**
```
improve_knowledge_index  → static eBook, never changes
                            freshness irrelevant — methodology does not expire

improve_case_index       → created_at and target_date fields exist
                            freshness IS relevant
                            recent case > 3-year-old case for current coaching
```

**Authority:**
```
improve_knowledge_index  → Black Belt eBook — highest authority
                            verified Six Sigma methodology
                            always ranks above case data when they conflict

improve_case_index       → real project data — medium authority
                            valuable for patterns, not prescriptive
                            should not override eBook methodology
```

This encodes the memory prioritization rules from Gap 22 as metadata signals rather than hardcoded priority rules — cleaner and more maintainable.

---

### What We Have But Do Not Use

Every metadata field indexed in both indexes is currently unused in retrieval queries. Pure vector similarity only.

| Index | Field | Signal Type | Used |
|---|---|---|---|
| knowledge | `phase_relevance` | Context | ❌ Gap 21 |
| knowledge | `source_file` | Authority | ❌ Not used |
| knowledge | `page_number` | Context | ❌ Not used |
| case | `created_at` | Freshness | ❌ Not used |
| case | `belt_level` | Context | ❌ Not used |
| case | `status` | Freshness/Authority | ❌ Not used |
| case | `days_in_phase` | Context | ❌ Not used |

---

### The Practical Impact

**Current retrieval from improve_case_index:**
- Cases from any phase
- Cases from any year
- Cases regardless of completion status
- Cases from any industry

**With metadata signals:**
- Cases where phase summary matches current phase
- Cases from last 2 years (freshness)
- Cases where status = completed (authority — completed more reliable than in-progress)
- Cases matching Belt level and industry (context)

Same index. Same embedding. Dramatically better retrieval quality from metadata we already have.

---

### Implementation — Quick Win

```python
# Current — pure vector only
results = search_client.search(
    search_text=query,
    vector_queries=[vector_query]
)

# With metadata signals — no new infrastructure needed
results = search_client.search(
    search_text=query,
    vector_queries=[vector_query],
    filter=f"phase_relevance eq '{current_phase}' 
             and status eq 'completed'",
    order_by=["created_at desc"]   # freshness signal
)
```

---

### Metadata-Driven Ranking Strategies

**Relevance Scoring** — combines vector similarity and metadata to rank results. Not just semantic match but weighted combination of similarity + freshness + authority.

**Freshness Boosting** — prioritises newer more current information when applicable. Applied to `improve_case_index` via `created_at desc` ordering. Not applied to `improve_knowledge_index` — eBook methodology does not expire.

**Authority Weighting** — elevates results from trusted and thoroughly validated sources. eBook content ranks above case data. Completed cases rank above in-progress cases.

**Feedback Adaptation** — continuously improves ranking using user and system feedback loops. The only dynamic strategy — ranking changes based on accumulated evidence of what actually works.

---

### Feedback Adaptation — Detailed

Unlike the other three strategies which are static rules set once, feedback adaptation makes the ranking system learn and improve over time.

**Two types of feedback loops:**

*Explicit feedback — user directly signals:*
- Belt clicks helpful / not helpful on a response
- Belt edits an AI-extracted field → signal that coaching missed something
- Belt submits gate successfully → positive signal for all chunks used that phase

*Implicit feedback — system infers from behaviour:*
- Belt spends 3 sessions on same topic → chunks used were insufficient
- Belt advances phase quickly → chunks used were effective
- Belt asks same question differently → current retrieval not finding right content

**AgentLean — two natural signals already being generated and ignored:**

```
Signal 1 — Gate passage (positive):
When Belt passes a gate, all RAG chunks retrieved during that phase
contributed to a successful outcome.
→ boost these chunks for similar future queries

Signal 2 — Field correction via HITL (negative):
When Belt corrects an AI-extracted field, the chunks that grounded
that extraction produced a wrong answer.
→ demote these chunks for similar future queries
```

**Implementation pattern:**
```python
# After gate passage — implicit positive feedback
async def record_positive_feedback(phase_chunks: list, phase: str):
    for chunk in phase_chunks:
        await update_chunk_score(chunk.id, phase, delta=+0.1)

# After Belt correction — implicit negative feedback
async def record_negative_feedback(correction: dict, chunks_used: list):
    for chunk in chunks_used:
        await update_chunk_score(chunk.id, correction["field"], delta=-0.1)
```

**Long-term value:**
After 50 DMAIC projects:
- Chunks that consistently help Belts pass gates rank higher
- Chunks that consistently produce wrong extractions rank lower
- System has learned from real coaching outcomes not just semantic similarity

This is how Agent Improve evolves from a static RAG system to a genuinely improving coaching system. The gate passage signal and the HITL correction signal are both already being generated — they just need to be captured and fed back into ranking.

**Note:** Feedback adaptation depends on HITL interrupts (Gap 2) being implemented first — field corrections are only capturable if the Belt has a review step before values are committed.

### Gap 21 Updated Scope

Gap 21 was originally scoped to `phase_relevance` filter only. It now encompasses all unused metadata signals and ranking strategies:

- `phase_relevance` filter on knowledge index
- `status = completed` filter on case index
- `created_at desc` ordering for freshness on case index
- `belt_level` and industry context filters on case index
- Authority weighting — eBook ranks above case data
- Feedback adaptation — gate passage and HITL corrections as ranking signals

Static metadata filters are quick wins requiring only filter additions. Feedback adaptation requires Gap 2 (HITL interrupts) as a prerequisite.

---

## 41. Target Retrieval Pipeline — System-Level Workflow

*Source: Edureka Course 2 — System-Level Workflow*

### The Six-Step Pipeline

| Step | What It Does | Agent Improve Today |
|---|---|---|
| 01 User Query | User submits information request | ✅ Works |
| 02 Tool Invocation | External tools retrieve candidate documents | ✅ Partial — Azure AI Search queried |
| 03 Query Refinement | Self-correcting logic improves query if results weak | ❌ Gap 22 — not implemented |
| 04 Metadata Filtering | Filter using context and authority signals | ❌ Gap 21 — all metadata unused |
| 05 Ranking Engine | Rank by semantic + metadata scores combined | ❌ Pure vector only |
| 06 Final Context Output | Top-ranked context passed to reasoning layer | ⚠️ Partial — top-k passed, no orchestration |

Steps 03, 04, and 05 are currently skipped entirely. We go directly from 02 to 06.

---

### The Complete Target Retrieval Pipeline for Agent Improve

```
Belt sends message (01)
        ↓
RAG query issued to Azure AI Search (02)
        ↓
Confidence check — results weak? (03)          ← Gap 22 sub-component
  Yes → restructure query, reissue
  No  → continue
        ↓
Metadata filters applied (04)                  ← Gap 21
  phase_relevance = current phase
  status = completed
  created_at desc (freshness)
        ↓
Ranking engine combines (05)                   ← Gap 21 + Gap 16
  vector similarity score
  + freshness boost
  + authority weight (eBook > case data)
  + feedback adaptation score
        ↓
Context Orchestration Layer assembles (06)     ← Gap 22
  structured JSON facts first (injection timing)
  top-ranked chunks within token budget
  recent messages last
        ↓
LLM receives clean grounded context
        ↓
Coaching response
```

---

### Gap Mapping to Pipeline Steps

```
Step 03 Query Refinement    → Gap 22 (self-correcting queries sub-component)
Step 04 Metadata Filtering  → Gap 21 (phase_relevance, status, freshness, authority)
Step 05 Ranking Engine      → Gap 21 (metadata-driven ranking)
                              Gap 16 (RAG Fusion / RRF)
                              Gap 15 (multi-query as input to ranking)
Step 06 Context Output      → Gap 22 (context orchestration layer)
                              Gap 19 (working memory compression)
```

This is the complete picture of what the retrieval layer should become. All six steps exist and are understood. Steps 03-05 need to be built. Step 06 needs the context orchestration layer added.

---

## 42. RubricMiddleware — Self-Evaluation and Correction Loop

*Source: Anthropic Blog — "Introducing Rubrics: Build Agents that Evaluate and Correct Their Work", June 2, 2026*
*Authors: S. Seshadri, S. Runkle*

### What It Is
A self-evaluation and correction loop built into the agent. A rubric defines what "done" looks like. A separate grader sub-agent evaluates output against the rubric. If anything fails, per-criterion feedback is injected back and the agent retries.

```
Agent produces output
        ↓
Grader sub-agent evaluates against rubric
        ↓
All criteria satisfied? → done
        ↓ No
Grader returns per-criterion targeted feedback:
"criterion 3 failed: root_cause_statement too vague,
 does not specify measurable impact"
        ↓
Agent receives specific feedback, retries
        ↓
Repeat until satisfied OR max_iterations hit
```

Loop terminates on: satisfied, max_iterations_reached, failed, or grader_error.

---

### How It Differs From What Agent Improve Has

| What We Have | RubricMiddleware |
|---|---|
| OutputFixingParser — fixes malformed JSON | Evaluates semantic quality not just format |
| Completeness checker — field present or absent | Checks if field meets quality criteria |
| Reflection node — generic retry | Per-criterion targeted feedback |
| Manual extraction guards | Automated grader loop |

The critical difference: **per-criterion targeted feedback**. Not "try again" — "root_cause_statement fails criterion 3 because it does not specify measurable impact." Agent fixes exactly that on the next attempt.

---

### Implementation Pattern

```python
from deepagents import RubricMiddleware, create_deep_agent

# Grader sub-agent — smaller cheaper model
gate_grader = RubricMiddleware(
    model="claude-haiku-4-5",       # cheaper model for grading
    system_prompt="You are a Black Belt gate reviewer. Grade each field against DMAIC standards.",
    tools=[validate_smart_goal, check_measurability],
    max_iterations=3
)

# Phase executor — main coaching model
coaching_agent = create_deep_agent(
    model="azure/gpt-4o",           # premium model for coaching
    system_prompt="You are a Black Belt coach...",
    middleware=[gate_grader]
)
```

Grader uses cheaper model. Main agent uses premium model. Cost-efficient and quality-controlled.

---

### What the Rubric Looks Like for Agent Improve

DMAIC gate documents have clear done criteria. Currently checked for presence only — not quality.

```python
define_rubric = """
- what field describes a measurable problem statement with baseline and target
- why field explains the business impact in quantifiable terms
- scope field clearly defines process boundaries with explicit inclusions and exclusions
- team field lists Belt, sponsor, and at least two team members with roles
- how_goal field is a SMART goal statement (Specific, Measurable, Achievable, Relevant, Time-bound)
"""

measure_rubric = """
- baseline_mean is a numeric value with units specified
- baseline_sigma is calculated correctly from the data provided
- measurement_system_validated confirms GR&R or equivalent was performed
- data_collection_plan specifies sample size, frequency, and responsible person
"""
```

These rubrics exist implicitly in our current gate validation logic. Making them explicit and feeding to a grader sub-agent is the upgrade.

---

### Connection to Existing Patterns

```
Planner    → defines the rubric (what done looks like)
Executor   → coaching agent produces output
Evaluator  → grader sub-agent checks against rubric  ← new role
TAO loop   → think → act → observe (grader feedback) → correct
```

This is OutputFixingParser (Section 29) operating at semantic quality level rather than just format level. Same loop concept, higher-level evaluation.

---

### Why This Is Important for DMAIC Specifically

A Black Belt gate document is not just complete when fields are present — it is complete when fields meet quality standards. A `root_cause_statement` that says "there are problems" passes the completeness check but fails the DMAIC quality standard. RubricMiddleware catches this before the gate is passed and the Belt moves to the next phase with a weak foundation.

---

### Key Points From the Blog Post
- Most effective for tasks with clear verifiable success criteria — gate documents qualify exactly
- Grader can call tools to gather hard evidence before verdict — `validate_smart_goal` tool could check SMART criteria programmatically
- Each criterion gets its own verdict — agent knows exactly what to fix
- Agent outputs are probabilistic — same prompt can succeed or fail across runs — RubricMiddleware handles this variance systematically
- Currently in beta — API may change

### Gap Register
**Gap 23** — no rubric-based quality evaluation at gate boundaries. Current gate check is binary: field present or absent. RubricMiddleware would add per-criterion quality evaluation with targeted correction feedback. Grader sub-agent pattern uses cheaper model (Haiku) for evaluation, preserving cost efficiency. Depends on Gate 2 (HITL) being in place so Belt can review grader feedback before gate is committed. Deferred to post-completion refactor.

---

## 43. Common Agent Roles and Responsibilities

*Source: Edureka Course 2 — Common Agent Roles and Responsibilities*

### The Four Roles

| Role | Responsibility |
|---|---|
| Coordinator Agents | Manage global goals and conflict resolution |
| Decision Agents | Evaluate outcomes and guide strategy |
| Observer Agents | Track system state and performance |
| Worker Agents | Handle computation and data processing |

### Mapping to Agent Improve

```
Coordinator → Supervisor              ✅ exists (implicitly — Gap 4 planning in prompts)
Decision    → MISSING                 ❌ no distinct role
Observer    → MISSING                 ❌ no distinct role
Worker      → Phase Subagents         ✅ exists (Define, Measure, Analyse, Improve, Control)
```

Two of four roles exist, and even those are not cleanly separated from each other.

---

### Decision Agent — What It Would Do

Distinct from the Supervisor. The Supervisor routes ("which phase next"). A Decision Agent evaluates outcomes and guides strategy.

```
Supervisor:      "We are in Analyse, root cause missing, route to Analyse subagent"
Decision Agent:  "The root cause extracted does not meet quality criteria,
                  recommend re-coaching before gate"
```

This is exactly what RubricMiddleware's grader sub-agent does (Gap 23) and exactly what conflict resolution logic needs (Gap 22). Currently this reasoning is either absent or buried inside the coaching prompt itself rather than being a distinct evaluative role.

---

### Observer Agent — What It Would Do

Tracks system state and performance across the WHOLE SYSTEM, not within one project. Distinct from anything currently implemented.

```
Observer Agent would track:
- Average time spent per DMAIC phase across all Belts
- Which phases most commonly require re-coaching
- System health: API latency, checkpoint failures, extraction error rates
- Drift detection: is coaching quality degrading over time
- Patterns feeding back into eBook content improvement
```

Connects to production governance and observability gaps already documented — but as a dedicated agent role rather than just LangSmith dashboards. The Observer Agent would actively use system-wide telemetry to inform decisions, not just passively log it.

---

### The Complete Target Architecture

```
Coordinator Agent (Supervisor)
  — routes between phases
  — manages the dmaic_plan

Decision Agent (NEW — Gap 24)
  — evaluates gate quality via rubric (Gap 23)
  — decides if coaching should continue or gate should pass
  — resolves conflicts between memory sources (Gap 22)

Worker Agents (Phase Subagents)
  — Define, Measure, Analyse, Improve, Control
  — execute coaching, extraction, calculations

Observer Agent (NEW — Gap 24)
  — tracks completion rates across all Belts
  — flags coaching quality drift
  — monitors system health metrics
  — feeds insights back to improve eBook content over time
```

### Why This Matters
Without Decision and Observer roles, no one in the system evaluates whether a gate SHOULD pass beyond field presence, and no one tracks system-wide health and patterns across all Belts and projects. Both gaps compound the existing quality and governance concerns already documented.

### Gap Register
**Gap 24** — no Decision Agent or Observer Agent roles. Coordinator and Worker roles exist but blended; Decision and Observer roles entirely absent. Decision Agent role would be implemented via RubricMiddleware (Gap 23) and conflict resolution (Gap 22). Observer Agent role is a new system-wide monitoring capability not yet scoped in detail. Deferred to post-completion refactor.

---

## 44. Consolidated Architecture Diagnosis — Agent Resolve Benchmark

*Source: Consolidated chat sessions, verified against LangGraph 1.2.6 (June 2026)*
*This section supersedes outdated terminology in earlier sections where noted*

### CRITICAL CORRECTION — LangGraph Version

Earlier sections of this document assumed LangGraph patterns without version verification. Confirmed current state:

- **Latest version: 1.2.6** — not 1.0. Actively shipping minor releases since the October 2025 stable milestone
- Fully backward compatible, no breaking changes
- New in 1.2.x: per-node timeouts, node-level `error_handler=` (returns Command for recovery/Saga patterns), `DeltaChannel` (cheaper checkpointing for long threads), streaming API v3
- `langgraph.prebuilt` deprecated → moved to `langchain.agents`

**The Edureka course (Sections 1-43 of this document) teaches pre-1.0 patterns:**
- Plain dict returns instead of `Command`
- `add_conditional_edges` wired externally instead of `Command`-based routing
- Manual history tracking in state
- `set_entry_point()` instead of `add_edge(START, ...)`

The concepts taught (interrupts, multi-stage approval, separation of concerns between review/decision nodes) remain sound. Only the syntax needs translating to `Command`-based 1.2.x style. This does not invalidate Sections 1-43 — it means implementation should use current syntax.

---

### Core Concepts Clarified — Precise Definitions

**Nodes vs States**
A node is a worker — a function that executes. A state is a clipboard — data passed between nodes. Nodes never run without state; state never runs on its own.

**Main Graph vs Subgraph**
The main graph is the top-level pipeline. A subgraph is a complete LangGraph mounted as a single node inside the parent — this is structural encapsulation, not intelligence. (Confirms Section 23's modular subgraph content.)

**Agent vs Subagent vs Orchestrator**
All three are just nodes with an LLM inside. The difference is role, not technology:
- **Orchestrator** — knows the full picture, decides what runs next, never does the work itself
- **Subagent** — knows only its narrow task, executes, knows nothing about other phases

This maps directly to the Planner → Executor pattern already documented in Sections 5, 11, 17.

**Main State vs Substate**
`DMAICState` (main) only carries what needs to travel between phases (`define_output`, `measure_output`, etc). Each phase has its own private substate (`DefineState`, `MeasureState`) for internal working memory — invisible to the main graph. This confirms and sharpens Section 10's Pattern 2 (Private Subagent State + Shared Parent State).

---

### Architecture Target for Agent Improve — Confirmed and Sharpened

```
Main Graph (DMAICState)
  └── Orchestrator Agent — reads full state, decides next phase via Command
        ├── Define Subgraph (DefineState)
        │     └── internal orchestrator + step-subagents
        │         (understand, search, scope, CTQs, validate)
        ├── Measure Subgraph (MeasureState)
        ├── Analyze Subgraph (AnalyzeState)
        ├── Improve Subgraph (ImproveState)
        └── Control Subgraph (ControlState)
```

**Critical addition not previously captured:** this pattern RECURSES. Each subgraph can have its own internal orchestrator deciding step order dynamically — not just the main graph. This is a deeper recursion than Section 11's three-level cascade (Supervisor → Phase Planner → Tool Executor). The recursion is: Main Orchestrator → Phase Orchestrator → Step-level subagents within that phase.

---

### Command Object — Replaces add_conditional_edges

This is the single most important syntax update from this section.

```python
# OLD (pre-1.0 pattern — what Edureka course teaches)
def router(state):
    if state["score"] > 0.8:
        return "next_node"
    return "retry_node"

graph.add_conditional_edges("current_node", router)

# NEW (1.2.x Command pattern)
def current_node(state) -> Command:
    result = do_work(state)
    if result.score > 0.8:
        return Command(update={"output": result}, goto="next_node")
    return Command(update={"output": result}, goto="retry_node")
```

A node returns `Command(update={...}, goto="next_node")` — combining state update and routing decision in one place. Eliminates separate routing functions entirely.

`Command(graph=Command.PARENT)` lets a subgraph node route directly into the parent graph — critical for the recursive orchestrator pattern above.

**Edges are still required for:**
- Parallel fan-out/fan-in (LangGraph needs to know dependencies at compile time to run nodes concurrently)
- The `ends=[]` declaration on Command-based nodes (compiler validation, not routing logic)

`Send` API — for dynamically creating a variable number of parallel workers when the count isn't known at design time. Confirmed by current LangChain documentation as the orchestrator-worker pattern's core mechanism: "The Send API lets you dynamically create worker nodes and send them specific inputs. Each worker has its own state, and all worker outputs are written to a shared state key that is accessible to the orchestrator graph" (docs.langchain.com/oss/python/langgraph/workflows-agents). Used specifically when "subtasks cannot be predefined the way they can with parallelization" — e.g. an unknown number of debate-subgraph instances, one per candidate root cause, where the candidate count is not known at design time.

---

### CORRECTION — Static Edges vs Dynamic Command Routing Is Situational, Not a Universal 2026 Standard

*Verified against current official documentation (docs.langchain.com/oss/python/langgraph/graph-api) and production guidance, June 2026, in response to a direct challenge during discussion*

An earlier version of this section implicitly favored `Command`-based dynamic routing as the general-purpose mechanism. This was imprecise. The current official documentation states the decision criterion explicitly:

> "For each node, choose one routing mechanism: use normal edges for static routing, or use conditional edges / Command for dynamic routing."

**The decision test:** could the number of times this transition fires, or whether it fires at all, vary at runtime?
```
Transition ALWAYS happens exactly once, in this exact order
        → static edge (add_edge) — correct, current, recommended

Transition MIGHT vary — skip, repeat, branch differently
based on what was just discovered
        → conditional edges / Command — correct, current, recommended
```

**A hard correctness rule, not a style preference, confirmed by official docs:**

> "Do not mix normal edges and dynamic routing from the same node, because both paths can execute and make graph behavior harder to reason about... if node_a returns Command(goto="my_other_node") and you also have graph.add_edge("node_a", "node_b"), both node_b and my_other_node will run."

A node must use either a static edge OR `Command`-based routing — never both. Mixing them silently executes both destinations, which is almost never the intended behavior. This rule was not previously stated in this section and must be respected throughout the v2.1 refactor.

**The three named production multi-agent patterns confirmed current for 2026** (Reactify Solutions, production guidance, dated within the last month relative to current date):

> "Supervisor. A router node owns the conversation and dispatches to specialist worker nodes. Workers return to the supervisor. This is our default. Easy to reason about, easy to extend, and the routing logic lives in one place."

This confirms the Hierarchical/Supervisor pattern already chosen for Agent Improve (Sections 44, 46) is the current recommended default for 2026 production systems — not an outdated choice. The open question was never "Supervisor or not" but "should the Supervisor's routing be static or dynamic," which the criterion above answers precisely.

---

### Applying the Criterion Correctly to Agent Improve — A Necessary Correction

```
Main DMAIC phase sequence:
Define → Measure → Analyse → Improve → Control

Does this transition EVER vary?
NO — DMAIC phase order is fixed by definition,
     every project, every Belt, every industry.
     It always runs exactly once, in this exact order.

→ STATIC EDGES (add_edge) are the correct, current,
  recommended choice for the MAIN phase sequence —
  NOT Command-based dynamic routing as earlier framing implied.
```

```
Internal step-subagents WITHIN a single phase (e.g. inside Define):
understand → search → scope → validate

Does this transition EVER vary?
YES — scope sometimes needs revisiting after validate fails,
      search sometimes needs to run twice, the Belt's actual
      answers determine the real path through these steps.

→ COMMAND-BASED DYNAMIC ROUTING is correct here —
  exactly as originally documented in this section.
```

**The corrected architectural rule for the refactor:** the top-level `DMAICState` orchestrator connecting the five phase subgraphs should very likely use simple static `add_edge` connections between them, since the phase sequence itself never varies. The recursive internal orchestrators *inside* each phase subgraph (the `understand → search → scope → validate` pattern) are where `Command`-based dynamic routing genuinely earns its complexity, because the step order there is authentically data-dependent.

This resolves the original design question raised during discussion: a "subgraph orchestrator deciding what to trigger dynamically" is the correct instinct — specifically for the *internal* recursion inside each phase, not necessarily for the fixed top-level DMAIC sequence, which the official documentation's own decision criterion places squarely in static-edge territory.

### Command Pattern — Confirmed in Lab Code

*Source: Edureka Course 2 lab — Supervisor node with Command-based routing*

```python
from langgraph.types import Command

class State(MessagesState):
    next: str    # routing decision field

def make_supervisor_node(llm, members: List[str]):
    system_prompt = (
        "You are a supervisor managing a team of workers.\n"
        f"Workers: {members}\n\n"
        "STRICT RULES:\n"
        "- You MUST choose exactly one of the following options:\n"
        f"  {members + ['FINISH']}\n"
        "- Start with researcher.\n"
        "- Then analyst.\n"
        "- Then writer.\n"
        "- Choose FINISH ONLY after writer has responded.\n"
        "Return ONLY ONE WORD from the allowed options."
    )

    def supervisor(state: State) -> Command:
        messages = [SystemMessage(content=system_prompt), *state["messages"]]
        response = llm.invoke(messages)

        choice = response.content.strip().upper()

        # Fallback safety — confirms Section 20's graceful degradation pattern
        if choice not in {m.upper() for m in members} | {"FINISH"}:
            choice = "RESEARCHER"

        if choice == "FINISH":
            return Command(goto=END)

        return Command(goto=choice.lower())

    return supervisor
```

This confirms the Command pattern in actual running code and confirms the fallback safety principle from Section 20 survives the syntax migration from pre-1.0 to 1.2.x.

---

### Two Nuances to Apply Correctly in Agent Improve

**Nuance 1 — `goto=` alone vs `update={}` + `goto=` together**

This lab example only routes — it does not change state:
```python
return Command(goto=choice.lower())          # routing only, no state write
```

Section 44's general pattern combines both:
```python
return Command(update={"output": result}, goto="next_node")   # routing + state write
```

For Agent Improve's main Orchestrator, **both are needed together** — it must route to the next phase AND update `current_phase` in `DMAICState`:
```python
def orchestrator(state: DMAICState) -> Command:
    next_phase = decide_next_phase(state)
    return Command(
        update={"current_phase": next_phase},
        goto=f"{next_phase}_subgraph"
    )
```

**Nuance 2 — LLM-decided routing vs logic-decided routing**

The lab example uses an LLM call to decide the next worker. This is appropriate when the order genuinely depends on judgment about content (e.g. "researcher, then analyst, then writer" requires reasoning about what has been gathered so far within the team).

For Agent Improve's **main Orchestrator** routing between DMAIC phases, the decision is likely **deterministic, not LLM-based** — the next phase is simply the next phase in the DMAIC sequence once the current phase's gate has passed:

```python
def orchestrator(state: DMAICState) -> Command:
    # logic-based, NO LLM call needed for phase sequencing
    next_phase = determine_next_phase(state)  # reads gate_passed flags
    return Command(
        update={"current_phase": next_phase},
        goto=f"{next_phase}_subgraph"
    )
```

LLM-based routing is more appropriate for the **internal step-subagents within a phase** (Section 44's recursive pattern) — e.g. deciding whether to call `understand`, `search`, `scope`, or `validate` next within the Define subgraph, where the right next step genuinely depends on reasoning about what has been captured so far. Reserve LLM-based routing for genuine judgment calls; use deterministic logic for fixed sequences like DMAIC's phase order.

---

### State Boundary Contracts — New Concept

Subgraphs only sync shared key names automatically, or use explicit input/output transformer functions.

**Critical rule:** outputs crossing the subgraph boundary should be typed Pydantic objects — not raw LLM text.

```python
class DefineOutput(BaseModel):
    ctqs: list[str]
    confidence_score: float
    gaps_identified: list[str]

# The orchestrator reads structured fields, never parses text
```

This directly resolves a risk in our current architecture — the orchestrator should never be parsing natural language output from a subgraph to decide what to do next. It reads validated typed fields.

---

### How the State Boundary Actually Works Mechanically — Resolving a Common Confusion

*Source: Direct discussion, prompted by a course lab that failed to correctly demonstrate this mechanism*

A natural point of confusion: subagents have their own private state, yet the main state must somehow get updated by what happens inside them. LangGraph provides exactly two mechanisms for this, both already named in this section but worth making fully concrete.

**Mechanism 1 — Shared Key Names (automatic, simplest case)**

If the parent state and child state both declare a field with the SAME name, LangGraph automatically copies that value across the boundary in both directions.

```python
class ParentState(TypedDict):
    messages: list              # SAME key name as child
    research_summary: str       # SAME key name as child — this IS the boundary

class ChildState(TypedDict):
    messages: list              # SAME key name as parent
    research_summary: str       # SAME key name as parent
    raw_search_results: list    # PRIVATE to child — parent never sees this
```

```
Parent invokes child subgraph as a node
        ↓
LangGraph automatically copies messages + research_summary INTO child state
        ↓
Child subgraph runs internally
        ↓
Child writes a value into research_summary
        ↓
LangGraph automatically copies research_summary BACK OUT into parent state
        ↓
raw_search_results NEVER crosses — it was never a shared key name
```

Fields not named identically in both schemas simply never leave the child's private scope. This is the actual mechanism behind "internal execution isolated from the parent graph."

**Mechanism 2 — Explicit Transformer Functions (when names differ or transformation is needed)**

```python
def transform_input_to_child(parent_state: ParentState) -> ChildState:
    return {"research_question": parent_state["topic"]}   # explicit field rename

def transform_output_to_parent(child_state: ChildState) -> dict:
    return {"research_summary": child_state["final_summary"]}  # explicit field rename
```

This is the mechanism this section already specifies for Agent Improve's boundary outputs being typed Pydantic objects (`DefineOutput`) rather than raw shared dict keys — DMAIC's needs are precise enough to warrant explicit, validated transformation rather than implicit name-matching.

**The critical precondition both mechanisms share:** they each require TWO DISTINCT state classes to exist. Mechanism 1 needs two classes that share some key names. Mechanism 2 needs two classes with a function translating between them.

---

### Case Study — A Course Lab That Failed to Implement This Correctly

*Edureka Course 2, "Building a Multi-Agent Subgraph Workflow" lab — analysed and found not to demonstrate the architecture it claims to teach*

The lab's narration correctly states the principle: "a parent graph that invokes a two-agent subgraph as a single node." However, inspecting the actual three files (`subgraph.py`, `parent_graph.py`, `main.py`) reveals:

```
subgraph.py     → declares SubgraphState(MessagesState)
parent_graph.py → declares the SAME SubgraphState(MessagesState), copy-pasted verbatim
main.py         → only ever imports and calls parent_graph — never imports subgraph.py
```

**Evidence this is an unintentional artifact, not a deliberate teaching technique:** `main.py` contains the comment `# Build graph using the function that ACTUALLY exists` directly above `app = parent_graph.build_subgraph(llm)`. This phrasing is the signature of a developer leaving a note after hitting a bug during refactoring — not language a deliberately-designed lesson would contain.

**Why this proves no real parent/child boundary exists in this lab:** with only one state class declared and reused verbatim, there is structurally nothing for either Mechanism 1 or Mechanism 2 to operate on — there is no boundary to cross, because there was only ever one side. `subgraph.py` is effectively dead code; what actually runs is a single flat graph with two nodes (researcher, summarizer) inside `parent_graph.py` alone — exactly the "monolithic graph" anti-pattern this document warns against, dressed across two files to resemble composition without the defining feature (a genuine state boundary) that would make it real.

**The verdict:** the lab's conceptual narration is sound and consistent with this document's principles. Its executed code does not demonstrate them. Do not use this lab's files as a reference implementation for Agent Improve's subgraph composition — use the principle below instead.

---

### The Correct Implementation for Agent Improve

```python
# Parent — DMAICState
class DMAICState(TypedDict):
    case_id: str
    current_phase: str
    define_output: DefineOutput | None      # shared key name = "define_output"
    measure_output: MeasureOutput | None

# Child — DefineState, genuinely separate class with private internal working memory
class DefineState(TypedDict):
    messages: list
    understand_result: str       # PRIVATE — never crosses
    search_result: str           # PRIVATE — never crosses
    ctq_candidates: list         # PRIVATE — never crosses
    define_output: DefineOutput  # SHARED key name — this crosses automatically

# main_orchestrator.py
define_subgraph = build_define_subgraph(llm)        # genuinely separate compiled graph
main_graph.add_node("define", define_subgraph)       # mounted as ONE node
main_graph.add_edge("define", "measure")             # static edge — fixed DMAIC sequence
```

Because `define_output` is named identically in both `DMAICState` and `DefineState`, it crosses the boundary automatically once the Define subgraph completes. Everything else inside `DefineState` stays genuinely private — exactly as the conceptual model describes, and exactly what the lab above failed to actually build.

---

### Cross-Reference — Connection to API/JSON Interface Design Principles

The state boundary contract above is the same discipline taught generically in API design, applied specifically to LangGraph's internal communication mechanism.

```
JSON API interface (general pattern)        Supervisor-Worker state passing (LangGraph)
─────────────────────────────────          ──────────────────────────────────────────
Request body = structured JSON              State object = structured TypedDict
Response body = structured JSON             Command(update={...}) = structured write
No free text in the contract                No conversational text in the contract
Caller and callee agree on a schema         Orchestrator and Worker agree on State schema
```

**Mapping the common communication elements precisely:**

| Generic Element | Agent Improve Equivalent |
|---|---|
| Task identifiers and execution status | `case_id`, `current_phase`, `gate_passed` in `DMAICState` |
| Partial results and intermediate outputs | `DefineOutput`, `MeasureOutput` Pydantic models |
| Metadata — confidence scores, error flags | `confidence_score`, `gaps_identified`, retry counters the Orchestrator reads to decide advance/retry/compensate/escalate |

**The critical mechanical distinction from typical API/microservice architecture:**

```
Direct API call pattern (NOT what LangGraph does):
Worker A → calls → Worker B directly with a request

Shared state pattern (what LangGraph actually does):
Worker A → writes to State → Orchestrator reads State → routes to → Worker B
                                                                       ↓
                                                          Worker B reads State
```

Agents do not call each other directly like API endpoints calling each other. They write to a shared state object; the next agent reads from that same object. **The state object itself is the API contract** — not a direct function call between agents.

This is exactly why Section 44's rule on typed Pydantic boundary outputs matters — a subagent returning prose instead of structured fields is the equivalent of an API returning unstructured text instead of JSON. The orchestrator would have to parse natural language to figure out what happened, which is fragile and unauditable — precisely the failure mode this slide's discipline prevents.

---

### Interrupts — Sharpened Implementation Pattern

`interrupt(payload)` pauses execution and saves state via the checkpointer; resumed via `Command(resume={...})` against the same `thread_id`.

**New architectural rule:** each phase subgraph owns its own interrupt (quality gate); the main orchestrator only routes based on results — it does not own the interrupt itself.

**Two-node pattern** for HITL gates:
```
review_node          → collects human decision
        ↓
apply_decision_node  → interprets decision, Commands to next step
```

This is more precise than what was captured in Section 2 and Section 12 — the interrupt logic is split into collection and application as two distinct nodes, not one combined gate node.

**Checkpointers confirmed:** `InMemorySaver` for dev, `PostgresSaver` for production on Azure — exactly as documented in Section 1, now confirmed current as of 1.2.6.

---

### Thread ID and Checkpoints in a Nested Orchestrator/Subagent Architecture

A precision not previously made explicit: in a distributed architecture where subagents have their own private state and internal orchestration, **does each subagent get its own checkpoint stream, separate from the main graph?**

**The relationship between the three concepts:**
```
State        = the data itself (what is in the clipboard right now)
Checkpoint   = a saved SNAPSHOT of that state at a specific point in time
Thread ID    = the LABEL that groups all checkpoints belonging to one conversation/project
```

**Two architectural options with different consequences:**

**Option A — Subgraph compiled with its own checkpointer, invoked under its own thread_id**
```python
define_subgraph = define_builder.compile(checkpointer=checkpointer)
# invoked with thread_id = "IMPR-2026-E9D-define" — a SEPARATE checkpoint stream
```
The subgraph's internal steps (understand → search → scope → CTQs → validate) are each individually checkpointed. Mid-phase crash recovery resumes exactly where the internal steps left off. HITL interrupts inside the subgraph persist correctly across a server restart.

**Option B — Subgraph mounted as a node inside the parent, no checkpointer of its own**
```python
define_subgraph = define_builder.compile()  # no checkpointer
main_graph.add_node("define_subgraph", define_subgraph)
main_graph_compiled = main_graph.compile(checkpointer=checkpointer)  # only on parent
```
The subgraph runs to completion as one atomic unit from the parent's perspective. Only the parent's checkpoint before entering and after exiting the subgraph captures state — the subgraph's internal steps are not individually checkpointed. A crash mid-subgraph requires re-running the entire subgraph from its start.

**Which is correct for Agent Improve — Option A is required, not optional**

This document already established that **each phase subgraph owns its own interrupt** (quality gate) earlier in this section. That requirement forces Option A: if the Define subgraph needs its own HITL interrupt — e.g. pausing mid-Define to confirm a CTQ with the Belt — that paused state must persist independently. With Option B, a server restart while a Define-internal interrupt is paused would lose that state entirely, since the parent checkpoint only captures pre- and post-subgraph snapshots, not what happens during.

**The correct architecture:**
```
Main Graph
  thread_id: "IMPR-2026-E9D"
  checkpointer: PostgresSaver (one shared instance)

  Define Subgraph
    thread_id: "IMPR-2026-E9D-define"      ← own thread, SAME checkpointer instance
    own internal HITL interrupts, fully recoverable

  Measure Subgraph
    thread_id: "IMPR-2026-E9D-measure"     ← own thread, SAME checkpointer instance
```

**Critical clarification:** a different checkpointer *object* per subgraph is not required — one `PostgresSaver` instance can be shared across the entire application. What separates the checkpoint streams is the **thread_id** used for each subgraph's invocation, not a different storage backend.

**The parent still only sees the validated final result, not the subgraph's internal checkpoint history:**
```
DMAICState (main, thread_id="IMPR-2026-E9D")
  define_output: DefineOutput(...)        ← only the validated final result lands here

DefineState (subgraph, thread_id="IMPR-2026-E9D-define")
  understand_result: ...
  search_result: ...
  scope_result: ...                       ← internal working memory, never crosses the boundary
  ctq_candidates: ...
```

This reaffirms the state boundary contract rule above (typed Pydantic outputs only crossing the boundary) while clarifying that the subgraph's full checkpoint history remains genuinely private — not just its live state, but its entire recoverable past.

**Summary:**
```
One project (Belt's case)      = one PARENT thread_id
Each phase subgraph            = its OWN child thread_id (e.g. f"{case_id}-define")
Same checkpointer instance     = shared across parent and all subgraphs
Parent state                   = only sees validated structured outputs from each subgraph
Subgraph state                 = has its own full checkpoint history, invisible to the parent
```

---

### Decision Rule — Prompt Sequencing vs Real Nodes

New decision framework not previously captured:

**Use prompt-only sequencing** for simple, reliable, non-branching steps.

**Use real nodes** (with their own Command routing) when steps:
- Can fail independently
- Need quality gates
- Need HITL
- Use different tools

**This is the case for every DMAIC phase.** Each phase has failure modes, needs a quality gate (Gap 23 RubricMiddleware), needs HITL (Gap 2), and uses different tools per phase. This settles the question of whether Agent Improve's phases should be prompt-sequenced or full subgraph nodes — the answer is unambiguously: full subgraph nodes, confirming the Path C architecture choice already made.

---

### Honest Architectural Diagnosis — Agent Resolve Case Study

**What Agent Resolve actually is today:**
A flat LangGraph StateGraph — five nodes at the same level, each a bare LLM call wrapped in the 5-phase methodology prompt text, not enforced architecture. No subgraph topology, no tool-calling coach agents, no T-A-O loop, no confidence scoring, no audit trail, no structured output validation, no retry/compensation logic.

**This is the same diagnosis pattern as Agent Improve's gaps documented throughout this entire EDUCATIONAL.md.** Both agents share the identical root architectural debt.

**What Agent Resolve needs to become (v2.1 target):**
Supervisor graph + 5 compiled phase subgraphs, each containing a ReAct coach node (tool-calling agent) with an internal T-A-O loop, a confidence gate, and an audit entry — with the Supervisor reading scores across phases to decide whether to advance, retry, compensate, or escalate.

---

### Root Cause Analysis — Why the Gap Formed

Four root causes identified, applicable to both Agent Resolve and Agent Improve:

1. **AI assistance solved each immediate question in isolation** rather than proactively flagging architectural standards across sessions
2. **Code was generated from training memory, not current framework documentation** — producing patterns that may already be deprecated (exactly the version gap identified above — pre-1.0 patterns persisting after 1.2.6 became current)
3. **Repeated refactors improved a flat system locally** without ever benchmarking against full LangGraph capability
4. **No persistent, enforced constitution travelled with the codebase** across many fragmented chat sessions

This root cause analysis explains precisely why CLAUDE.md and ARCHITECTURE.md exist as governance documents — and why this EDUCATIONAL.md itself is necessary as a third governance layer.

---

### Governance System to Prevent Recurrence — Three Enforcement Layers

This is new and significant — a layered defense system against the architectural debt pattern.

**Layer 1 — CLAUDE.md (the constitution) — a suggestion layer**
Encodes non-negotiable rules ("every phase = compiled subgraph," "no bare LLM calls," "Supervisor never calls the LLM directly"). Claude reads it at session start but can forget it as context fills — not a guarantee.

**Layer 2 — Skills (manually triggered procedures) — a checklist layer**
`/fetch-docs`, `/implement-subgraph`, `/architectural-review` — invoked as explicit commands, forcing the reading step to be atomic rather than assumed. Still relies on being triggered.

**Layer 3 — Hooks (automatic, deterministic enforcement) — a guarantee layer**
Fire on system events regardless of what the model decides:
- `SessionStart` — inject current gap count/version context
- `PostToolUse` — grep-check every file write for violations, `exit 2` blocks the write
- `Stop` — end-of-session compliance summary
- `PreToolUse` — protect critical files

**Critical implementation detail:** `exit code 2` is mandatory for blocking — `exit 1` is silently non-blocking, the most common implementation bug.

**Plus MCP servers:**
- **Context7** — fetches current LangGraph/LangChain docs at call time — solves training-data staleness (directly solves root cause #2 above)
- **GitHub MCP** — PRs, issues
- **Playwright** — integration tests

**The mental model:** CLAUDE.md persuades, skills structure, hooks enforce, MCP supplies live capability. All four layers must coexist — none alone is sufficient.

---

### Correct Division of Labor — Tool Usage Going Forward

| Tool | Use For | Why |
|---|---|---|
| Claude.ai Chat (Desktop) | Architecture thinking, gap analysis, concept learning, building reference docs | Has cross-session memory about you and the project; no codebase access |
| Claude Code in VS Code | All implementation | Full codebase access, runs code/tests, reads CLAUDE.md/skills/hooks, connects to Context7 + GitHub via MCP |

**The anti-pattern to avoid:** using chat to draft implementation prompts that get copy-pasted into Claude Code. This recreates the original problem — design happens without codebase visibility, execution happens without the originating context.

**The bridge mechanism:** a short "session briefing" document (current gaps, target architecture reference) maintained in chat and pasted into Claude Code at the start of implementation sessions — until native cross-tool project memory exists. This EDUCATIONAL.md serves exactly this bridging function.

---

### Gap Register Addition

**Gap 25 — Version drift risk.** Implementation patterns referenced throughout this document and in the original Agent Improve build may use pre-1.0 LangGraph syntax (plain dict returns, externally wired `add_conditional_edges`, `set_entry_point()`). Must be verified against current 1.2.6 API before refactor implementation begins. Context7 MCP should be used during refactor to fetch live documentation rather than relying on training data patterns. This is the single highest-priority gap to resolve before Step 3.1 resumes, since it affects the syntax of every other gap's implementation.

**Gap 26 — No governance enforcement layers for Agent Improve.** CLAUDE.md and ARCHITECTURE.md exist (Layer 1 — suggestion layer) but Skills (Layer 2) and Hooks (Layer 3) do not exist for Agent Improve specifically. Without Layers 2 and 3, architectural drift identified in this very document could recur. Recommend implementing hooks before resuming Step 3.1: a `PostToolUse` hook checking for bare LLM calls outside subgraph nodes, and a `SessionStart` hook injecting current gap count from this EDUCATIONAL.md.

---

## 45. Anti-Drift Governance Design — Hooks, Skills, and Staying Current

*Source: Direct discussion, building on Section 44's governance layers*

### The Maturity Shift

A turning point in this learning process: moving from "learn the concepts" to "design the system that prevents the concepts from going stale." This section captures the mechanisms needed to keep both Vassilis's knowledge and the codebase from drifting as LangGraph/LangChain continue shipping releases.

Three distinct problems, three distinct mechanisms:

```
Problem 1: Vassilis's own knowledge goes stale
           → solved by: deliberate version-check habit + targeted forum monitoring

Problem 2: Architectural decisions made on outdated assumptions
           → solved by: a Skill that forces a live-docs check before any
             architectural decision is finalized

Problem 3: Claude Code drifts from current syntax while implementing
           → solved by: a Hook that blocks code using deprecated patterns
```

---

### Mechanism 1 — Skill: Pre-Architecture-Decision Version Check

A Skill is manually triggered but forces an atomic, non-skippable step. Before any architectural decision is finalized (not just before writing code — before deciding the approach), this Skill runs.

```
/verify-current-version

Triggers:
1. Query Context7 MCP for current LangGraph version and changelog
2. Query Context7 MCP for current LangChain version and changelog
3. Compare against patterns about to be used in the upcoming decision
4. Output: "Confirmed current" or "WARNING: pattern X is deprecated as of version Y, use Z instead"
```

**Where this slots into the workflow:**
```
Idea for architectural change
        ↓
/verify-current-version  ← MANDATORY skill, cannot be skipped
        ↓
Confirmed current → proceed to design
Deprecated pattern flagged → redesign with current pattern first
```

This directly prevents the root cause #2 identified in Section 44 — code generated from training memory rather than current documentation.

---

### Mechanism 2 — Hook: PostToolUse Drift Detection in VS Code

A Hook is automatic and deterministic — it fires regardless of what Claude Code "decides" to do, closing the gap that Skills leave open (Skills can simply not be invoked).

```python
# .claude/hooks/post-tool-use-drift-check.py
# Fires after every file write in Claude Code

DEPRECATED_PATTERNS = {
    r"add_conditional_edges\(": "Use Command(goto=...) pattern instead (LangGraph 1.2.x)",
    r"set_entry_point\(": "Use add_edge(START, ...) instead",
    r"from langgraph\.prebuilt import": "Moved to langchain.agents in 1.2.x",
    r"return\s*\{[\"']next[\"']:": "Plain dict routing deprecated — return Command(goto=...) instead",
}

def check_file_for_drift(file_path: str, content: str) -> int:
    violations = []
    for pattern, message in DEPRECATED_PATTERNS.items():
        if re.search(pattern, content):
            violations.append(f"{file_path}: {message}")
    
    if violations:
        print("\n".join(violations))
        return 2  # MANDATORY exit code 2 to block the write
    return 0
```

**Critical implementation detail (from Section 44):** exit code 2 is mandatory for blocking. Exit code 1 is silently non-blocking — the most common implementation bug. This hook must use exit 2.

**What this catches that the Skill above does not:** the Skill is checked before design decisions. The Hook is checked on every single file write, catching drift introduced during implementation even when the original design was correct — for example, Claude Code falling back to a familiar pre-1.0 pattern out of habit while writing code, even after the architecture was correctly designed with Command-based routing.

---

### Mechanism 3 — SessionStart Hook: Inject Current Context Automatically

```python
# .claude/hooks/session-start-context.py
# Fires automatically when a new Claude Code session begins

def inject_session_context():
    gap_count = count_open_gaps("EDUCATIONAL.md")
    current_langgraph_version = check_installed_version("langgraph")
    latest_langgraph_version = query_context7("langgraph", "latest")
    
    context = f"""
    SESSION CONTEXT (auto-injected):
    - Open architectural gaps: {gap_count} (see agent-improve/EDUCATIONAL.md)
    - Installed LangGraph: {current_langgraph_version}
    - Latest available: {latest_langgraph_version}
    - {"⚠️ VERSION MISMATCH — review before implementing" if current_langgraph_version != latest_langgraph_version else "✅ Version current"}
    """
    return context
```

This ensures every Claude Code session starts with awareness of both the gap register and the current version state — without relying on Claude Code "remembering" to check.

---

### Mechanism 4 — Staying Current as a Human: Targeted Forum Monitoring

This is the human-side complement to the automated hooks. The goal is not generic browsing but **targeted monitoring of the specific sources where LangGraph/LangChain changes are announced first**.

**Highest-signal sources, ranked by directness:**

| Source | Why It Matters | Frequency to Check |
|---|---|---|
| LangChain official blog (blog.langchain.dev) | First-party announcements, breaking changes explained by the team | Weekly |
| LangGraph GitHub releases page | Raw changelog, exact version diffs, often before blog posts | Weekly |
| LangChain Discord — #langgraph channel | Practitioners discussing issues in real time, often surfaces problems before they hit docs | As needed when debugging |
| Anthropic engineering blog | Where RubricMiddleware-type announcements appear (Section 42) | Bi-weekly |
| r/LangChain (Reddit) | Lower signal but surfaces community pain points and workarounds | Monthly |
| Hacker News — search "LangGraph" | Surfaces significant architectural shifts that get broader discussion | Monthly |

**The practical habit:** rather than browsing all of these reactively, the same `/verify-current-version` Skill from Mechanism 1 could be extended to also pull recent items from the LangChain blog and GitHub releases — turning passive monitoring into an active part of the architectural decision workflow rather than a separate habit to remember.

---

### The Complete Anti-Drift System

```
HUMAN SIDE                          SYSTEM SIDE
─────────────                       ───────────
Weekly: check LangChain blog        SessionStart hook:
        + GitHub releases             auto-injects version state
                ↓                              ↓
Before architecture decision:       Before any decision:
/verify-current-version skill         confirms pattern is current
                ↓                              ↓
Design with confirmed-current       During implementation:
patterns                              PostToolUse hook blocks
                ↓                     deprecated pattern writes
Hand to Claude Code                            ↓
                                     Clean, current-syntax code
```

---

### Why All Four Mechanisms Are Necessary Together

This restates and sharpens the "all four layers must coexist" principle from Section 44, now with concrete implementation:

- **Without the Skill** — architectural decisions get made on stale assumptions before any code is written
- **Without the PostToolUse Hook** — even a correct design can drift during implementation through habit or autocomplete suggesting old patterns
- **Without the SessionStart Hook** — every new session starts blind to whether the environment itself has drifted
- **Without human forum monitoring** — the automated checks only catch drift against what Context7 already knows; genuinely new patterns and emerging best practices are first seen by humans in community discussion before they are formally documented

### Gap Register Addition

**Gap 27 — No anti-drift mechanisms implemented.** Specifically: no `/verify-current-version` skill exists, no `PostToolUse` deprecated-pattern hook exists, no `SessionStart` version-injection hook exists, no deliberate forum/changelog monitoring habit established. This gap is meta — it is the mechanism that prevents Gap 25 (version drift) from recurring after it is fixed once. Should be implemented alongside or immediately after Gap 25 resolution, before Step 3.1 resumes.

---

## 46. Coordination Pattern Taxonomy

*Source: Edureka Course 2 — Coordination Patterns in Distributed Systems*

### The Three Branches

```
Coordination Patterns
├── Control Flow      → HOW work is structured and sequenced
├── Consensus         → HOW agreement is reached when multiple agents weigh in
└── Synchronization   → WHEN agents wait for each other vs proceed independently
```

---

### Control Flow — Five Sub-Patterns

**Hierarchical** — a coordinator directs subordinates. Maps to Orchestrator/Subagent pattern (Section 44).

**Peer-to-peer** — agents coordinate directly, no central authority. Not used in Agent Improve — DMAIC has strict sequential dependency, peer coordination does not fit.

**Sequential** — one step finishes before next starts. Exactly DMAIC: Define → Measure → Analyse → Improve → Control. Cannot skip ahead.

**Parallel** — independent steps run simultaneously. Where `RunnableParallel` (Section 28) applies — e.g. RAG lookup and field extraction running concurrently within a phase.

**Iterative** — steps repeat until a condition is met. Exactly the HITL gate loop — coaching continues iteratively until gate criteria (Gap 23 RubricMiddleware) are satisfied.

---

### Consensus — Two Sub-Patterns

**Voting Mechanisms** — multiple agents vote, majority wins. Maps to Debate Agents (Section 22).

**Priority-based Resolution** — a ranking rule decides, not a vote. Maps to Memory Prioritization and Conflict Resolution (Section 38, Gap 22) — when `captured_fields` conflicts with a recent message, priority rules decide, not a vote.

---

### Synchronization — Two Sub-Patterns

**Synchronous** — agents wait for each other before proceeding. RunnableParallel's synchronisation barrier (Section 28) — all branches complete before next stage runs.

**Asynchronous** — agents progress independently without waiting. What the Observer Agent (Gap 24) needs — monitoring system state in the background without blocking the main coaching flow.

---

### Complete Mapping to Agent Improve

```
Agent Improve Coordination Pattern
├── Control Flow
│   ├── Hierarchical    → Main Orchestrator → Phase Subagents              ✅ designed (Section 44)
│   ├── Sequential      → DMAIC phase order                                ✅ implemented
│   ├── Parallel        → RunnableParallel within phase node               ⚠️ designed, not implemented
│   ├── Iterative       → HITL coaching loop until gate rubric satisfied   ⚠️ partial — no rubric yet (Gap 23)
│   └── Peer-to-peer    → NOT USED — DMAIC requires strict hierarchy       ✅ correctly absent
│
├── Consensus
│   ├── Voting          → Debate agents for root cause validation          ❌ not implemented
│   └── Priority-based  → Memory conflict resolution (Gap 22)              ❌ not implemented
│
└── Synchronization
    ├── Synchronous     → Parallel fan-out/fan-in within phase nodes       ⚠️ designed, not implemented
    └── Asynchronous    → Observer Agent background monitoring (Gap 24)    ❌ not implemented
```

---

### What This Taxonomy Adds

A single index against which every coordination decision in Agent Improve can be checked. Every coordination need falls into exactly one of these seven leaf categories. This is useful both as a completeness check (have we considered every pattern type) and as a vocabulary for discussing the architecture precisely with Claude Code during the refactor.

**Status summary:**
- Fully implemented: Hierarchical, Sequential (2/7)
- Correctly absent: Peer-to-peer (1/7)
- Designed but not implemented: Parallel, Synchronous (2/7)
- Partial: Iterative (1/7)
- Not yet addressed: Voting, Priority-based (2/7)

### Gap Register
No new gap number — this section indexes existing Gaps 22, 23, 24 and Section 28 against the formal coordination pattern taxonomy rather than introducing new scope. Use this table as the checklist when validating the v2.1 refactor design covers all required coordination patterns.

---

## 47. Opinion Aggregation Techniques

*Source: Edureka Course 2 — Opinion Aggregation Techniques*

### Distinct From Consensus Strategies (Section 22)

```
Consensus Strategies   → HOW agents reach AGREEMENT
                          (2-3 distinct positions to resolve — e.g. advocate vs skeptic)

Opinion Aggregation    → HOW to COMBINE many inputs into one number/output
                          (N similar-type values to merge — e.g. multiple confidence scores)
```

### The Five Techniques

**Simple Averaging** — merges inputs assuming equal contribution. Every input counts the same; take the mean.

**Weighted Aggregation** — assigns higher weight to more reliable inputs. Same averaging idea, but some inputs count more based on a trust/reliability factor.

**Rank Aggregation** — combines ranked outputs into a final order. Not averaging values — merging orderings. This is the same mechanism as Reciprocal Rank Fusion (Section 33, Gap 16) — multiple retrievers each rank documents, RRF merges those rankings into one final order.

**Outlier Filtering** — removes extreme or noisy inputs before combining the rest. A cleanup step that runs BEFORE the other four techniques, not an alternative to them.

**Ensemble Methods** — learns optimal weights for higher accuracy. Weighted Aggregation's smarter cousin — the system learns weights from historical performance data rather than weights being manually set.

---

### Already Covered Elsewhere, Now Correctly Named

| Technique | Where It Already Appears |
|---|---|
| Rank Aggregation | = Reciprocal Rank Fusion, Section 33, Gap 16 |
| Weighted Aggregation | = MEMORY_PRIORITY weighting, Section 38, Gap 22 |

Same mechanisms, different application — Rank Aggregation merges search result orderings, Weighted Aggregation in Section 38 ranks memory sources by authority.

---

### New Application — Decision Quality Signal Aggregation

The genuinely new fit for Agent Improve: combining multiple numeric confidence/quality signals when assessing whether a root cause is well-supported.

```python
signals = {
    "data_correlation_score": 0.82,      # statistical correlation with the defect
    "advocate_confidence": 0.75,          # from the debate subgraph (Section 22)
    "ebook_methodology_match": 0.90,      # match against known Six Sigma patterns
    "belt_certainty": 0.60,               # how confident the Belt sounded
}
```

**Simple Averaging:**
```python
overall_score = sum(signals.values()) / len(signals)   # 0.7675, all signals equal
```

**Weighted Aggregation** — methodology match and data correlation count more than the Belt's subjective certainty:
```python
weights = {
    "data_correlation_score": 0.35,
    "advocate_confidence": 0.20,
    "ebook_methodology_match": 0.30,
    "belt_certainty": 0.15,
}
overall_score = sum(signals[k] * weights[k] for k in signals)
```

**Outlier Filtering applied first** — if `belt_certainty` were 0.05 while everything else clusters around 0.8, that is likely noise unrelated to root cause quality and could be excluded before averaging rather than dragging the combined score down.

**Ensemble Methods** — over many completed DMAIC projects (`improve_case_index`, Section 36), learn which signals actually correlated with gates that did NOT later get reopened or corrected, and adjust weights automatically rather than hand-picking them.

---

### Gap Register
**Gap 28** — no opinion aggregation framework for combining decision quality signals. Distinct from Gap 16 (rank aggregation applied to search results) and Gap 22 (weighted aggregation applied to memory sources) — this gap is specifically about combining confidence/quality signals when assessing whether a coaching decision (e.g. a proposed root cause) is well-supported. Depends on the debate subgraph (Section 22) existing as one of its signal sources. Lower priority than Gaps 1-25 — a refinement once the debate subgraph and rubric evaluation (Gap 23) are already in place.

---

## 48. Reflection Nodes vs Consensus Modeling — Resolving the Ambiguity

*Source: Direct discussion — clarifying a pattern used throughout the document*

This document has used both reflection-style self-checking (Section 29 OutputFixingParser, Gap 23 RubricMiddleware) and consensus-style multi-perspective resolution (Section 22 Debate, Section 46, Section 47) without ever stating explicitly when each applies. This section resolves that.

### These Are Not the Same Pattern at Different Maturity Levels

A common assumption to correct: reflection is not simply an earlier or less sophisticated version of consensus modeling. They solve genuinely different problems.

```
Reflection Node           = ONE perspective checking itself against a STANDARD
Consensus Modeling        = MULTIPLE genuinely independent perspectives
                             that may legitimately disagree, being RECONCILED
```

### Reflection Node — What It Actually Checks

```python
def reflection_node(state):
    original_output = state["draft_output"]
    critique = llm.invoke(f"""
    Review this output: {original_output}
    Does it meet the required standard? What is wrong, if anything?
    """)
    if critique.is_satisfactory:
        return Command(goto=END)
    return Command(update={"feedback": critique}, goto="revise")
```

Checks output against a standard — completeness, format, a rubric. Only one "side" exists: the producer and a critic grading against criteria. There is no disagreement being modeled because there is nothing to disagree *about* — only a standard to meet or fail.

### Consensus Modeling — What It Actually Checks

```
Advocate: "I believe this root cause IS supported"
Skeptic:  "I believe this root cause is NOT supported"
                ↓
   These are two genuinely different conclusions
   that need to be RECONCILED, not corrected against a standard
```

A reflection node has no equivalent of "the critic disagrees with the original conclusion" — only "the critic finds the conclusion deficient against a standard."

### Side-by-Side Comparison

| | Reflection Node | Consensus Modeling |
|---|---|---|
| Number of independent viewpoints | One (self-check) | Multiple (genuinely different) |
| What it answers | "Does this meet the standard?" | "Which of these conflicting views is right?" |
| Failure mode it catches | Sloppiness, hallucination, incompleteness | Bias, blind spots a single reasoning path would miss |
| Output if it fails | Revise and retry | Reconcile, weight, or escalate |
| Where it appears in this document | Section 29 (OutputFixingParser), Gap 23 (RubricMiddleware) | Section 22 (Debate), Section 46, Section 47 |

### Why Reflection Was the Correct Tool for Most of What Has Been Built

Reflection is the right tool for the large majority of what Agent Improve needs:
- "Is this extracted field complete?" → reflection
- "Does this gate document satisfy the DMAIC rubric?" → reflection (Gap 23)
- "Is this JSON output malformed?" → reflection (Section 29)

These are all single-conclusion quality checks. There was never a second legitimate opinion to reconcile — just a standard to meet or fail. Relying on reflection here was the correct instinct, not a gap to retroactively fix.

### Where Reflection Alone Is Structurally Insufficient

The specific failure mode reflection cannot catch: **when the LLM's single reasoning pass might be systematically biased or have a blind spot, and a self-check by the same kind of reasoning is unlikely to catch its own blind spot.**

Root cause identification is the clearest DMAIC example. If the coaching LLM proposes a root cause and then reflects on its own proposal, it is likely to find its own reasoning convincing — that is precisely what a blind spot is. Reflection cannot catch a blind spot it does not know it has. A genuinely independent skeptic position, generated separately and instructed to argue the opposite, has a structurally different chance of surfacing what a self-check would miss. This is why Section 22's debate subgraph is built as two separate agent calls (advocate, skeptic) rather than one agent reflecting twice.

### The Practical Rule Going Forward

```
Use reflection when:         the question is "did I do this correctly against a known standard"
                              → completeness, format, rubric satisfaction (Gap 23)

Use consensus modeling when: the question is "could I be wrong in a way I wouldn't notice myself"
                              → root cause validation, high-stakes irreversible decisions
```

Both belong in Agent Improve simultaneously. Reflection remains the default for the vast majority of quality checks — cheap, fast, sufficient. Consensus modeling is reserved for the small number of genuinely high-stakes, hard-to-self-detect decisions, given the added latency and cost shown in Section 22's hybrid implementation.

### The Three-Prompt Separation Pattern — Made Explicit

*Source: Edureka Course 4 Module 2 demonstration, verified against current langchain_core documentation June 2026.*

A refinement not previously explicit in this section: generation, validation, and correction are **three separate prompt calls**, not one combined self-review. This is the correct production pattern:

```
Generation Prompt  → produce the initial draft
                     inputs: task + constraints
                     returns: first attempt (may fail)

Validation Prompt  → check the draft against rules
                     inputs: output + constraints
                     returns: PASS:constraint or FAIL:constraint - reason
                     MUST be machine-readable format, not prose
                     so the correction prompt can parse it reliably

Correction Prompt  → fix exactly what failed
                     inputs: original_output + validation_feedback + task
                     "here is what failed and why — fix it now"
                     targeted feedback, not generic "try again"
```

**Important prompt-template correction from the course demo:**

The course uses `PromptTemplate` from `langchain_core.prompts`. This is current and not deprecated. However for Agent Improve using `gpt-4o` via `ChatOpenAI` (Azure OpenAI), the correct class is `ChatPromptTemplate` — `PromptTemplate` targets plain-text completion models, `ChatPromptTemplate` targets modern chat models:

```python
# What the course demo uses — valid but for completion-style models
from langchain_core.prompts import PromptTemplate

# What Agent Improve should use — for gpt-4o / ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

validation_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a strict DMAIC gate reviewer. Check each constraint exactly."),
    ("human",
     "Gate document:\n{output}\n\n"
     "Constraints:\n{constraints}\n\n"
     "For each constraint return exactly:\n"
     "PASS: <constraint> or FAIL: <constraint> - <reason>\n"
     "Machine-readable format only. No prose.")
])
```

---

### The ConstraintValidator Pattern — Typed, Composable Gate Validation

The course demo introduces a `ConstraintValidator` class with static methods — each validator returns `tuple[bool, str]` (pass/fail + reason). This is directly applicable to Agent Improve's DMAIC gate validation and more explicit than the OutputFixingParser approach:

```python
class DMAICGateValidator:
    """Typed gate field validators for Agent Improve.
    Each method returns (passed: bool, message: str).
    Composable — run as many or as few as needed per phase."""

    @staticmethod
    def validate_smart_goal(goal: str) -> tuple[bool, str]:
        checks = {
            "measurable": any(c.isdigit() for c in goal),
            "time_bound": any(t in goal.lower()
                for t in ["by", "within", "before", "q1", "q2", "q3", "q4"]),
            "specific": len(goal.split()) >= 10
        }
        failed = [k for k, v in checks.items() if not v]
        if failed:
            return False, f"SMART goal missing: {', '.join(failed)}"
        return True, "SMART goal valid"

    @staticmethod
    def validate_problem_statement(statement: str) -> tuple[bool, str]:
        has_baseline = any(c.isdigit() for c in statement)
        has_process = len(statement.split()) >= 8
        if not has_baseline:
            return False, "Problem statement missing baseline metric"
        if not has_process:
            return False, "Problem statement too vague — add process context"
        return True, "Problem statement valid"

    @staticmethod
    def validate_scope(scope: str) -> tuple[bool, str]:
        has_inclusion = "include" in scope.lower() or len(scope.split()) >= 5
        has_exclusion = "exclude" in scope.lower() or "not include" in scope.lower()
        if not has_inclusion:
            return False, "Scope missing inclusion boundary"
        if not has_exclusion:
            return False, "Scope missing exclusion boundary"
        return True, "Scope valid"
```

**Running all validators and collecting failures:**
```python
def validate_define_gate(state: DefineState) -> list[str]:
    """Returns list of failure messages. Empty list = gate passes."""
    failures = []
    fields = state["captured_fields"]

    checks = [
        DMAICGateValidator.validate_problem_statement(fields.get("what", "")),
        DMAICGateValidator.validate_smart_goal(fields.get("how_goal", "")),
        DMAICGateValidator.validate_scope(fields.get("scope", "")),
    ]

    for passed, message in checks:
        if not passed:
            failures.append(message)

    return failures
```

**Connection to RubricMiddleware (Section 42/54):** RubricMiddleware's grader sub-agent does the same thing at a higher level — per-criterion evaluation returning targeted feedback. The `ConstraintValidator` pattern is the deterministic, rule-based equivalent for fields that can be validated without LLM reasoning (numeric presence, word count, keyword presence). Use `ConstraintValidator` for objective checks, `RubricMiddleware` for subjective quality evaluation. Both produce the same output shape: per-criterion pass/fail with reasons.

---

### The Simulated LLM Caveat — Worth Recording

The course demo explicitly uses a fake LLM: *"This is not a real LLM call. It's a simulation so the demo always behaves consistently."* Attempt 1 is hardcoded to fail, attempt 2 to pass.

**What this means for production:** the two-attempt simulation does not demonstrate real LLM non-determinism. In production, attempt 2 can also fail, or can fix one criterion while introducing a new failure. The `max_iterations` cap (Section 42/54's `RubricMiddleware(max_iterations=3)`) handles this — always set a maximum to prevent infinite correction loops.

---

## 49. Saga-Based Transactions and Compensating Actions

*Source: Term first appeared in Section 23 (microservice design patterns) but was never explained. Resolved here.*

### Why Normal Transactions Don't Work in a Multi-Step Agentic Workflow

A single database transaction guarantees all-or-nothing rollback within that database. But a multi-step agentic workflow's steps often have real-world side effects outside any single database — calling an external API, sending a notification, writing to a different system. There is no database transaction that spans "call SAP" and "send an email" and "update an index" together.

### The Saga Solution — Compensating Actions

Each step that has a side effect also defines its own specific undo action (a compensating action). If a later step fails, the saga runs the compensating actions for everything that already succeeded, in reverse order.

```
Step 1: Reserve inventory        → succeeds
Step 2: Charge payment           → succeeds
Step 3: Schedule shipment        → FAILS

Saga response — run compensations in reverse:
Compensate Step 2: Refund payment
Compensate Step 1: Release inventory reservation

End result: system back to a consistent state, even though
            no single database transaction covered all three steps
```

### Connection to Already-Documented Architecture

This is the precise mechanism behind the phrase in Section 44: *"the Supervisor reads confidence_scores and routes via conditional edges to advance, retry, compensate, or escalate."* "Compensate" specifically means running a Saga-style compensating action when a later phase fails and an earlier phase's effects need partial undoing.

Also connects to **Gap 25's** confirmed `error_handler=` feature in LangGraph 1.2.x — the mechanical hook where compensating logic attaches to a node.

### Concrete Agent Improve Example

```python
def measure_node(state: MeasureState) -> Command:
    # side effect: writes baseline to improve_case_index
    write_to_case_index(state["case_id"], "baseline_mean", calculated_value)
    return Command(update={"baseline_mean": calculated_value}, goto="gate_check")

def measure_compensate(state: MeasureState):
    # the Saga compensating action for the step above
    # if Measure gate later needs to reopen, this undoes the published value
    delete_or_flag_stale_in_case_index(state["case_id"], "baseline_mean")
```

Without this, a reopened gate leaves a stale, now-incorrect baseline value silently sitting in `improve_case_index` — corrupting the long-term memory that Gap 20's cross-case retrieval depends on.

### Connection to Time-Travel Debugging — A Subtle but Important Interaction

A checkpoint records *state*, not external side effects. Resuming from an earlier checkpoint via time-travel debugging (Section 5) does not automatically undo a side effect that happened after that checkpoint.

```
Checkpoint 4 (before Measure gate)
        ↓
Measure runs → writes to improve_case_index → checkpoint 5 created
        ↓
[Time-travel back to checkpoint 4 to try again]
        ↓
PROBLEM: the write to improve_case_index from the first attempt
         is still there — checkpointing rolled back STATE,
         not the EXTERNAL SIDE EFFECT
        ↓
SOLUTION: a Saga compensating action must run alongside the
          time-travel rollback to undo the external write
```

This means Gap 8 (time-travel debugging) and a future Saga implementation are not independent — a correct time-travel implementation for any node with external side effects requires its compensating action to run as part of the rollback, not just the state restoration.

### Which Nodes Are Candidates

Every node that writes to an external system is a candidate for needing a compensating action — none currently have one:

```
Define   → writes captured_fields to blob           — needs compensation if reopened
Measure  → writes baseline + case index update       — needs compensation if reopened
Analyse  → writes root cause + debate verdict         — needs compensation if reopened
Improve  → writes hypothesis                          — needs compensation if reopened
Control  → writes final control plan                 — needs compensation if reopened
```

### Gap Register
**Gap 29** — no Saga-based compensating actions exist for any node with external side effects (writes to `improve_case_index`, Azure Blob, future MCP-connected systems). This becomes a correctness issue specifically when combined with gate reopening (HITL corrections, Gap 2) or time-travel debugging (Gap 8) — both can leave external systems out of sync with rolled-back graph state without compensation logic. Depends on Gap 25 (confirm `error_handler=` mechanics in current LangGraph version) before implementation. Lower priority than Gaps 1-23, but should be addressed before Gap 8 (time-travel) is used in production against systems with external side effects.

---

## 50. CRITICAL VERSION CORRECTIONS — Verified Against Live Documentation, June 2026

*Source: Direct verification against docs.langchain.com, LangChain Forum, and GitHub issues, triggered by reconciling Course 2/3 notes against the document. This section takes priority over any conflicting code pattern elsewhere in this document, including Sections 27-41 and the InsightForge reference in Section 51.*

This is the single most consequential finding from this reconciliation pass. Two API families used throughout the Edureka Course 2 lab code (and reproduced in good faith in Sections 27-41 and the project assignments) are **confirmed deprecated** as of LangChain/LangGraph v1.x, which is current as of June 2026. This is Gap 25 made concrete — not a hypothetical risk, but an active one already present in this document.

### Correction 1 — All Classic `ConversationXMemory` Classes Are Deprecated

```
DEPRECATED (do not use, scheduled for removal in LangChain 2.0):
  ConversationBufferMemory
  ConversationBufferWindowMemory
  ConversationSummaryMemory
  ConversationEntityMemory
  VectorStoreRetrieverMemory
  ConversationChain
```

**Confirmed by multiple independent sources, including official LangChain reference docs:** *"In LangChain 1.x, these classic memory classes and ConversationChain are deprecated and scheduled for removal in LangChain 2.0. For new LangChain agents, prefer create_agent with LangGraph checkpointing for short-term memory and LangGraph stores for long-term memory."*

**This directly affects the "Composite Memory System" code reproduced from the course notes** (three-layer memory using `VectorStoreRetrieverMemory`, `ConversationSummaryMemory`, `ConversationEntityMemory` — see Section 51 for the original reference). That code pattern is built entirely on deprecated classes and should NOT be implemented in Agent Improve as written, despite being current in the Edureka lab.

**The correct 2026 replacement, confirmed by official LangChain v1 migration guidance:**

```
Within-session memory (replaces ConversationBufferMemory, ConversationSummaryMemory):
    → LangGraph checkpointer (InMemorySaver dev / PostgresSaver production)
    → scoped by thread_id

Cross-session memory (replaces ConversationEntityMemory, VectorStoreRetrieverMemory):
    → LangGraph BaseStore
    → scoped by user_id or entity namespace, NOT thread_id

For semantic/procedural memory with LLM-driven extraction:
    → LangMem SDK (LangGraph-native, newer, confirmed "less battle-tested" per sources — evaluate before production use)

For temporal knowledge graph memory (event sequencing, "what happened when"):
    → Zep / ZepCloudMemory (third-party, confirmed production-stable)
```

**The critical architectural distinction, confirmed directly from official sources and essential to get right:**

> "A checkpointer manages conversation history within a single session, scoped by thread_id. A store manages facts that persist across all sessions, scoped by user or entity namespace. A new thread_id (new session) clears checkpointer context but never touches the store... passing only a checkpointer is the most common architecture mistake."

This is a precise, important refinement to everything this document has said about checkpointing (Section 1) and Agent Improve's "short-term vs long-term" memory discussion (Sections 36-38). **Checkpointer and Store are two distinct LangGraph primitives, not one mechanism wearing two names.** Section 36's `improve_case_index` (cross-case, cross-project memory) maps conceptually to what a `BaseStore` is meant to formalize — and the nested-subgraph thread_id discussion in Section 44 maps precisely to what a checkpointer governs. This document's own architecture already intuited the correct separation; it now has the correct LangGraph-native vocabulary and primitive for it.

### Correction 2 — `create_react_agent` Is Deprecated, Replaced by `create_agent`

```
DEPRECATED in LangGraph v1 (confirmed in official LangGraph v1 migration guide):
  from langgraph.prebuilt import create_react_agent

CURRENT REPLACEMENT:
  from langchain.agents import create_agent
```

**Confirmed directly from the official LangGraph v1 migration guide:** *"LangGraph v1 deprecates the create_react_agent prebuilt. Use LangChain's create_agent, which runs on LangGraph and adds a flexible middleware system."*

**This directly affects the ReAct Agent code in Section 51 / InsightForge Analytics reference**, which uses `create_react_agent` from `langgraph.prebuilt` throughout. That pattern should be treated as **conceptually correct but syntactically superseded** — exactly the same category of issue already documented for `add_conditional_edges` vs `Command` in Section 44.

**An important nuance worth recording honestly:** the migration is not entirely clean. A LangChain Forum thread and a GitHub issue (both dated within the last several months relative to the current date) confirm that `create_agent`'s message-history-rewriting flexibility is reported as a regression relative to `create_react_agent` for at least one real use case, and that LangChain's own deprecation message initially pointed to a function (`create_agent` inside `langchain.agents`) that didn't yet exist in the package at the time of complaint. **This is exactly the kind of edge case Gap 27's anti-drift mechanism (the `/verify-current-version` skill) exists to catch before committing to a migration** — confirm `create_agent` is fully available and feature-complete in the installed `langchain` version before porting any `create_react_agent` code, rather than assuming the deprecation notice alone is sufficient guidance.

**Also relevant — RubricMiddleware's "middleware system" framing (Section 42) is now confirmed connected to this exact migration**, not a separate or unrelated capability: *"create_agent, which runs on LangGraph and adds a flexible middleware system."* RubricMiddleware is one specific middleware built on the same underlying `create_agent` foundation that this correction identifies as the current standard. This strengthens, rather than weakens, the case for Gap 23 — the path to RubricMiddleware and the path off deprecated `create_react_agent` are the same migration, not two separate efforts.

### What This Means for the Refactor Sequence

This is now the most urgent, concrete instance of **Gap 25** found in this document to date. Before Step 3.1 resumes, or before any of the InsightForge-style code in Section 51 is used as a reference for implementation:

1. Verify the exact installed versions of `langchain`, `langgraph`, and `langgraph-checkpoint` in `agent-improve/.venv` against current PyPI releases
2. Confirm `create_agent` is present and feature-complete in the installed `langchain` version (not just announced — actually shipped, per the GitHub issue above)
3. Replace any future use of `ConversationSummaryMemory`/`ConversationEntityMemory`/`VectorStoreRetrieverMemory` patterns with the Checkpointer + BaseStore split described above
4. Treat all `create_react_agent`-based code in Section 51 as a conceptual reference only — re-author against `create_agent` before implementation

### Gap Register Update

**Gap 25 is now CONFIRMED, not hypothetical.** Add the following specific, actionable sub-findings:

- **Gap 25a** — `ConversationSummaryMemory`, `ConversationEntityMemory`, `VectorStoreRetrieverMemory` confirmed deprecated, scheduled for removal in LangChain 2.0. Any future composite-memory implementation for Agent Improve must use LangGraph Checkpointer (session-scoped) + BaseStore (cross-session/cross-case-scoped) instead.
- **Gap 25b** — `create_react_agent` confirmed deprecated in LangGraph v1, replaced by `create_agent` from `langchain.agents`. All ReAct-pattern code intended for Agent Improve's tool-calling subagents must target `create_agent`, verified actually present in the installed package version first.

---

## 51. InsightForge Analytics — Complete Production-Grade Reference Implementation

*Source: Edureka Course 2 graded assignment reference material (also appears as "StrategicConsult Analytics" — same architecture, different cover story). This is the most complete, end-to-end runnable code reference captured anywhere in this document — five layers, fully wired, with an explicit problem-to-solution mapping at each layer.*

**⚠️ READ SECTION 50 FIRST.** Two patterns in this reference (`ConversationSummaryMemory`/`ConversationEntityMemory` in Layer 4, and any future `create_react_agent` usage) are confirmed deprecated as of LangChain/LangGraph v1.x. This section is preserved as a **conceptual and structural reference** — the five-layer architecture, the separation of concerns, and the governance discipline are sound and directly applicable to Agent Improve. The specific deprecated class names must be substituted per Section 50 before any implementation.

### The Five-Layer Architecture

```
① Workflow          structures + heals       RunnableSequence · RunnableBranch · RunnableParallel · OutputFixingParser
        ↓
② Routing           decides + verifies       Semantic tool routing · ReAct loop · verifyResult · Fallback chain
        ↓
③ Transform         cleans both boundaries   TransformChain · Normalize · Score · Rank · Dual validation
        ↓
④ Retrieval         grounds in knowledge     Composite memory · Multi-query · RRF · Self-correcting pipeline
        ↓
⑤ Governance        measures + audits        4 metrics · Trace log · Risk gate · Human review queue
```

This is the same five concerns already scattered across Sections 27-41 of this document, but here assembled as one coherent, runnable system rather than five separate topic explanations — valuable specifically because it shows how the pieces actually connect end to end.

---

### Layer 1 — Workflow Design & Reliability

**RunnableSequence — linear pipeline:**
```python
from langchain_core.runnables import RunnableLambda, RunnableSequence
from langchain_google_genai import ChatGoogleGenerativeAI

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.2)

def normalize_input(data: dict) -> dict:
    query = data.get("query", "").strip().lower()
    if not query:
        raise ValueError("Query cannot be empty")
    return {"query": query, "metadata": data.get("metadata", {})}

def enrich_context(data: dict) -> dict:
    catalog = {"market trends": {"sector": "technology", "year": 2024}}
    enriched = catalog.get(data["query"], {"sector": "general", "year": 2024})
    return {**data, "context": enriched}

def build_prompt(data: dict) -> str:
    return (
        f"Research Query: {data['query']}\n"
        f"Sector: {data['context']['sector']}\n"
        f"Year: {data['context']['year']}\n"
        "Provide a concise strategic intelligence summary."
    )

def call_llm(prompt: str) -> str:
    return llm.invoke(prompt).content

pipeline = (
    RunnableLambda(normalize_input)
    | RunnableLambda(enrich_context)
    | RunnableLambda(build_prompt)
    | RunnableLambda(call_llm)
)
result = pipeline.invoke({"query": "market trends"})
```
Normalize first so the LLM never receives dirty data. Single `.invoke()` runs the full chain.

**RunnableBranch — conditional routing:**
```python
from langchain_core.runnables import RunnableBranch, RunnableLambda

def is_market_analysis(data: dict) -> bool:
    return "market" in data.get("query", "").lower()

def is_competitive_intel(data: dict) -> bool:
    return "competitor" in data.get("query", "").lower()

router = RunnableBranch(
    (is_market_analysis, RunnableLambda(handle_market)),
    (is_competitive_intel, RunnableLambda(handle_competitive)),
    RunnableLambda(handle_general)   # default — no condition needed
)
```
Conditions evaluated in order — first match wins. Only one path executes per request.

**RunnableParallel — simultaneous execution:**
```python
from langchain_core.runnables import RunnableParallel, RunnableLambda

parallel_retrieval = RunnableParallel({
    "docs": RunnableLambda(retrieve_research_docs),
    "metrics": RunnableLambda(fetch_market_metrics),
    "entities": RunnableLambda(query_entity_database),
})

def merge_and_reason(results: dict) -> str:
    context = f"Documents: {results['docs']}\nMetrics: {results['metrics']}\nEntities: {results['entities']}"
    return llm.invoke(f"Synthesize this research context:\n{context}").content

pipeline = parallel_retrieval | RunnableLambda(merge_and_reason)
```
Total time = slowest single task, not the sum. Results arrive as a keyed dictionary.

**OutputFixingParser + retry logic — self-healing:**
```python
from langchain.output_parsers import OutputFixingParser
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
import time

class ResearchOutput(BaseModel):
    summary: str = Field(description="Executive summary of findings")
    key_points: list[str] = Field(description="Top 3 insights")
    confidence: float = Field(description="Confidence score 0.0-1.0")

base_parser = PydanticOutputParser(pydantic_object=ResearchOutput)
fixing_parser = OutputFixingParser.from_llm(parser=base_parser, llm=llm)

def parse_with_retry(raw_output: str, max_retries: int = 3) -> ResearchOutput:
    for attempt in range(max_retries):
        try:
            return fixing_parser.parse(raw_output)
        except Exception as e:
            wait = 2 ** attempt   # 1s, 2s, 4s backoff
            print(f"Parse failed (attempt {attempt+1}): {e}. Retrying in {wait}s...")
            time.sleep(wait)
    raise RuntimeError("Pipeline stabilization failed after max retries")
```
The pipeline never crashes on a formatting error. Retry with exponential backoff handles transient failures.

**Layer 1 — problems solved:** multi-step pipelines breaking · JSON inconsistency · no automated correction · no retry mechanism.

---

### Layer 2 — Intelligent Tool Routing & Reasoning

**Tool definitions with semantic routing — docstrings ARE the routing signal:**
```python
from langchain_core.tools import tool

@tool
def vector_store_lookup(query: str) -> str:
    """Search research documents by semantic similarity. Use for: knowledge retrieval, finding reports, policy documents, research papers."""
    return f"[Vector Store] Found 5 relevant chunks for: {query}"

@tool
def market_data_api(query: str) -> str:
    """Fetch real-time market metrics, growth rates, and sector data. Use for: market size, revenue figures, growth trends, financial metrics."""
    return f"[Market API] Growth: 12%, Size: $4.2B, Trend: upward for {query}"

@tool
def general_research(query: str) -> str:
    """General research fallback using parametric knowledge. Use when: no specific tool matches, or as fallback when other tools fail."""
    return llm.invoke(f"Answer this research question: {query}").content

tools = [vector_store_lookup, market_data_api, competitor_database, sentiment_analyzer, general_research]
```

**ReAct agent — Thought/Action/Observation loop, with `verifyResult`:**

⚠️ The reference code below uses `create_react_agent` from `langgraph.prebuilt`. Per Section 50, this is **deprecated** — use `create_agent` from `langchain.agents` instead. Structure shown for conceptual reference.

```python
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor, create_react_agent   # ⚠️ DEPRECATED — see Section 50

react_prompt = PromptTemplate.from_template("""
You are an intelligent research agent. Use tools to gather evidence. Verify each result before using it. Always think step by step.
Available tools: {tools}
Tool names: {tool_names}
Format:
Thought: [what you know and what you need]
Action: [tool_name]
Action Input: [input to the tool]
Observation: [tool result]
... (repeat Thought/Action/Observation as needed)
Thought: I now have sufficient evidence
Final Answer: [structured research conclusion]
Question: {input}
{agent_scratchpad}
""")

def verify_result(observation: str, min_length: int = 10) -> bool:
    if not observation or len(observation.strip()) < min_length:
        print("verifyResult: observation too short or empty — flagging")
        return False
    if "error" in observation.lower():
        print("verifyResult: error detected in observation")
        return False
    return True

agent = create_react_agent(llm=llm, tools=tools, prompt=react_prompt)   # ⚠️ use create_agent instead
executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True,
    max_iterations=6,                 # max hops before graceful exit
    handle_parsing_errors=True        # OutputFixingParser integration
)

def run_with_fallback(query: str) -> str:
    try:
        return executor.invoke({"input": query})["output"]
    except Exception as e:
        print(f"Primary agent failed: {e}. Using fallback.")
        return general_research.invoke(query)   # parametric fallback
```
The ReAct loop is self-correcting — each observation updates the next thought. `verifyResult` catches bad tool outputs at the boundary. `max_iterations` prevents infinite loops. Fallback wrapper ensures graceful degradation, never a hard pipeline halt.

**Layer 2 — problems solved:** fixed tool sequences · pipeline halts on tool failure · no reasoning verification · complex multi-hop queries failing mid-execution.

---

### Layer 3 — Data Transformation & Post-Processing

**TransformChain — five-step text normalization, each function single-concern:**
```python
from langchain.chains import TransformChain
import re

def strip_whitespace(text: str) -> str: return text.strip()
def to_lowercase(text: str) -> str: return text.lower()
def collapse_spaces(text: str) -> str: return re.sub(r'\s+', ' ', text)
def remove_special_chars(text: str) -> str: return re.sub(r'[^\w\s\-.,?!]', '', text)
def normalize_numbers(text: str) -> str: return re.sub(r'\d+', '#', text)   # anonymization

def run_normalization_pipeline(inputs: dict) -> dict:
    text = inputs["text"]
    for step in [strip_whitespace, to_lowercase, collapse_spaces, remove_special_chars, normalize_numbers]:
        text = step(text)
    return {"normalized_text": text}

normalize_chain = TransformChain(
    input_variables=["text"], output_variables=["normalized_text"],
    transform=run_normalization_pipeline
)
```

**Scoring + ranking processor — analysts see highest-impact findings first:**
```python
from dataclasses import dataclass
import re

@dataclass
class IdeaScore:
    idea: str
    score: float
    reason: str

def parse_score_and_reason(text: str) -> tuple[float, str]:
    score_match = re.search(r'Score:\s*([\d.]+)', text)
    reason_match = re.search(r'Reason:\s*(.+)', text, re.DOTALL)
    score = float(score_match.group(1)) if score_match else 0.0   # fallback = 0 → sinks, never crashes
    reason = reason_match.group(1).strip() if reason_match else "No reason provided"
    return score, reason

def score_and_rank(findings: list[str]) -> list[IdeaScore]:
    scored = []
    for idea in findings:
        raw = scoring_chain.invoke({"idea": idea}).content
        score, reason = parse_score_and_reason(raw)
        scored.append(IdeaScore(idea=idea, score=score, reason=reason))
    return sorted(scored, key=lambda x: x.score, reverse=True)   # descending — highest impact first
```
Fallback score of 0 ensures malformed outputs sink to the bottom rather than crashing the ranker. The `reason` field makes scoring transparent and auditable — directly relevant to Gap 23's rubric-feedback discipline.

**Layer 3 — problems solved:** raw outputs not consumable · no structured validation · no scoring or prioritisation of findings.

---

### Layer 4 — Retrieval, Memory & Knowledge Pipelines

⚠️ **The composite memory code below uses deprecated classes. See Section 50 for the required replacement (Checkpointer + BaseStore split) before implementing anything from this subsection.** Preserved here for the conceptual three-layer pattern only.

```python
# ⚠️ DEPRECATED CLASSES — conceptual reference only, see Section 50
from langchain.memory import VectorStoreRetrieverMemory, ConversationSummaryMemory, ConversationEntityMemory

episodic_memory = VectorStoreRetrieverMemory(retriever=vectorstore.as_retriever(search_kwargs={"k": 3}), memory_key="episodic_context")
semantic_memory = ConversationSummaryMemory(llm=llm, memory_key="semantic_context", return_messages=True)
working_memory = ConversationEntityMemory(llm=llm, memory_key="entity_context")

def adaptive_memory_router(query: str, prior_confidence: float = 1.0) -> dict:
    context = {}
    if any(m in query.lower() for m in ["earlier", "previously", "last session", "before"]):
        context.update(episodic_memory.load_memory_variables({"prompt": query}))
    if any(m in query.lower() for m in ["market", "report", "analysis", "trend"]):
        context.update(semantic_memory.load_memory_variables({"input": query}))
    context.update(working_memory.load_memory_variables({"input": query}))   # always loaded
    if prior_confidence < 0.5:   # low confidence → widen the net
        context.update(episodic_memory.load_memory_variables({"prompt": query}))
        context.update(semantic_memory.load_memory_variables({"input": query}))
    return context
```
**The conceptual pattern worth preserving despite the deprecated classes:** an adaptive classifier runs BEFORE retrieval — cheap intent analysis (keyword matching on temporal/domain markers) that decides which memory layers are worth querying, preventing expensive unnecessary searches. This pattern survives the class-name deprecation entirely intact — it should be re-implemented against Checkpointer/BaseStore rather than discarded.

**Multi-query retrieval + RRF fusion (current, not deprecated):**
```python
from langchain.retrievers import MultiQueryRetriever
from langchain_community.retrievers import BM25Retriever
from collections import defaultdict

dense_retriever = vectorstore.as_retriever(search_kwargs={"k": 3})
bm25_retriever = BM25Retriever.from_documents(docs)
multi_query_retriever = MultiQueryRetriever.from_llm(retriever=dense_retriever, llm=llm)

def reciprocal_rank_fusion(ranked_lists: list[list], k: int = 60) -> list:
    scores = defaultdict(float)
    for ranked_list in ranked_lists:
        for rank, doc in enumerate(ranked_list, start=1):
            scores[doc.page_content] += 1.0 / (k + rank)
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)

def hybrid_retrieve(query: str) -> list:
    dense_results = multi_query_retriever.get_relevant_documents(query)
    bm25_results = bm25_retriever.get_relevant_documents(query)
    return reciprocal_rank_fusion([dense_results, bm25_results])
```
This is the concrete, runnable implementation of RRF that Section 33/16 described conceptually. `score = Σ 1/(60 + rank)`, summed across all lists a document appears in — rank position is stable across incomparable scoring scales (dense similarity vs. BM25 keyword score cannot be compared directly, but rank position can).

**Self-correcting pipeline — adaptive re-query with full trace log:**
```python
from datetime import datetime

def self_correcting_pipeline(query: str, confidence_threshold: float = 0.6, max_iterations: int = 3) -> dict:
    trace_log = []
    current_query = query
    for iteration in range(max_iterations):
        results = hybrid_retrieve(current_query)
        top_score = results[0][1] if results else 0.0
        review = {
            "timestamp": datetime.now().isoformat(), "iteration": iteration + 1,
            "query": current_query, "chunks": len(results), "top_score": round(top_score, 4),
            "decision": "PASS" if top_score >= confidence_threshold else "RETRY"
        }
        trace_log.append(review)
        if top_score >= confidence_threshold:
            context = "\n".join([r[0] for r in results[:3]])
            answer = llm.invoke(f"Answer using this context:\n{context}\n\nQuestion: {query}").content
            return {"answer": answer, "trace_log": trace_log, "status": "OK"}
        current_query = llm.invoke(f"Rephrase this query more broadly for better retrieval: {current_query}").content.strip()
    trace_log.append({"decision": "FALLBACK", "reason": "max iterations reached"})
    return {"answer": "Low confidence result — flagged for human review", "trace_log": trace_log, "status": "LOW_CONFIDENCE"}
```
This is the concrete, runnable implementation of the self-correcting queries pattern described conceptually in Section 32. A retrieval miss is a logged event, not a silent failure. Max iterations reached → automatic low-confidence flag + human review trigger, directly feeding Layer 5's risk gate below.

**Layer 4 — problems solved:** single-query retrieval missing context · sessions not reusing prior findings · no adaptive memory system · no re-query mechanism for weak results.

---

### Layer 5 — Optimisation, Safety & Governance

**Four pipeline metrics — confirmed from official sources as the production standard set:**

| Metric | Definition | Target | Behaviour |
|---|---|---|---|
| Pipeline Success Rate | % completing end-to-end without error or manual intervention | > 95% | Drops when retry budget exhausts |
| Retry Frequency | How often OutputFixingParser/self-correction fires per 100 requests | < 5% | Leading indicator — rises BEFORE success rate drops |
| Retrieval Relevance | Precision@K — top-K chunks actually relevant to the answer | P@5 > 0.80 | Drops when embeddings drift |
| Reasoning Accuracy | % of answers correct against ground-truth test set, including multi-hop | > 90% | Driven by retrieval quality |

```python
from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class PipelineMetrics:
    total_requests: int = 0
    successful: int = 0
    retry_count: int = 0
    retrieval_scores: list = field(default_factory=list)
    accuracy_scores: list = field(default_factory=list)
    flagged_for_review: int = 0

    @property
    def success_rate(self) -> float: return self.successful / max(self.total_requests, 1)
    @property
    def retry_frequency(self) -> float: return self.retry_count / max(self.total_requests, 1)
    @property
    def avg_retrieval_relevance(self) -> float: return sum(self.retrieval_scores) / max(len(self.retrieval_scores), 1)
    @property
    def avg_reasoning_accuracy(self) -> float: return sum(self.accuracy_scores) / max(len(self.accuracy_scores), 1)

metrics = PipelineMetrics()

def risk_gate(answer: str, confidence: float, retry_count: int, retrieval_miss: bool, sensitive_topic: bool = False) -> dict:
    flags = []
    if confidence < 0.6: flags.append("LOW_CONFIDENCE")
    if sensitive_topic: flags.append("SENSITIVE_TOPIC")
    if retry_count > 2: flags.append("HIGH_RETRY_COUNT")
    if retrieval_miss: flags.append("RETRIEVAL_MISS")
    if flags:
        metrics.flagged_for_review += 1
        return {"status": "REVIEW_REQUIRED", "flags": flags, "answer": answer}
    metrics.successful += 1
    return {"status": "AUTO_DELIVERED", "flags": [], "answer": answer}
```
**The risk gate's four trigger conditions** (LOW_CONFIDENCE, SENSITIVE_TOPIC, HIGH_RETRY_COUNT, RETRIEVAL_MISS) are a directly usable template for an Agent Improve gate-quality risk gate — sitting precisely where Gap 23 (RubricMiddleware) and Gap 2 (HITL interrupts) intersect: outputs that fail this gate route to human review rather than auto-committing to the blob/case-index.

**Layer 5 — problems solved:** no measurement framework · no explainability · no oversight for high-risk outputs.

---

### Routing Strategy Comparison Table — New, Not Previously Captured

This table is a genuinely new addition not covered elsewhere in this document — a precise comparison of all six routing strategies with explicit limitations, useful as a decision reference when choosing how the Phase Planner (Section 11) should route within a phase:

| Strategy | How It Works | Best For | Limitation |
|---|---|---|---|
| Static | Fixed rules — query type X always routes to tool Y | Known, stable patterns with no variation | Brittle — breaks when phrasing changes |
| Dynamic | Runtime decisions based on load, urgency, resource availability | High-throughput systems with variable load | Requires real-time system state awareness |
| Semantic | Embeds query, matches to tool descriptions by vector similarity | Varied phrasing and intent | Requires embedding model and tool description quality |
| LLM-Assisted | The model reads the query and selects the best tool from a catalog | Complex, ambiguous queries needing nuanced judgment | Adds latency and token cost per decision |
| Hybrid | Combines fixed rules + LLM reasoning | Production systems needing both speed and flexibility | More complex to configure and debug |
| Multi-Path | Executes several tools simultaneously when one is insufficient | Complex queries requiring multiple data sources | Higher resource usage — must deduplicate results |

This refines Section 30's binary semantic-vs-LLM framing into a full six-option decision space. For Agent Improve, the **Hybrid** row is the most likely fit for the Phase Planner's tool selection — fixed rules for well-known field-extraction needs, LLM reasoning reserved for genuinely ambiguous coaching judgment calls (consistent with the static-vs-dynamic edges decision criterion already established in Section 44).

### Written Reflection Excerpt — Real Implementation Wisdom Worth Preserving

From the assignment's accompanying reflection (StrategicConsult Analytics variant), worth recording verbatim in substance as practitioner-level insight not found in the lecture content itself:

*"The most technically challenging component was the self-correcting knowledge pipeline. The initial design used a fixed similarity threshold, but retrieval scores vary significantly by query domain — a threshold appropriate for market analysis queries was too strict for regulatory queries. The solution was to implement query relaxation on retry: when the threshold isn't met, the LLM rephrases the query more broadly, rather than simply re-running the same query against the same index."*

*"Early testing showed that even when explicitly instructed to return raw JSON, the LLM occasionally wraps output in markdown code fences. The fix was two-fold: include 'no markdown, no code fences' in the prompt, and fall back to OutputFixingParser when the base parser fails. This combination reduced parsing failures by over 90% in testing."*

**Direct relevance to Agent Improve:** the threshold-varies-by-domain problem will recur exactly when comparing confidence thresholds across DMAIC phases — Define-phase completeness checks and Analyse-phase root-cause-validation confidence are not directly comparable on the same numeric scale, mirroring the "market vs regulatory" finding above. Any single global confidence threshold across all five phases (a tempting simplification) should be treated with the same suspicion this reflection raises.

### Gap Register Note

This section does not introduce a new gap number. It consolidates and makes concrete several gaps already numbered (15, 16, 23, 29, 30 conceptually via Section 30's expansion) with a single coherent, runnable reference architecture. Use this section as the primary implementation reference for Agent Improve's Phase Executor nodes, subject to the Section 50 deprecation corrections.

---

## 52. MAJOR FINDING — Official Checkpointer + Store Architecture Supersedes Custom Memory Design

*Source: Verified directly against docs.langchain.com/oss/python/langgraph/persistence (official LangChain documentation, current as of June 2026) and corroborated by five independent technical sources. This is the single highest-value finding from this audit pass — it reveals that LangGraph already provides, as a first-class built-in primitive, the exact two-tier memory architecture this document spent Sections 36-38 designing from first principles.*

### The Official Architecture, Stated Plainly

> "LangGraph provides two complementary persistence systems: Checkpointers persist a thread's graph state as checkpoints. Use them for short-term, thread-scoped memory, including conversation continuity, human-in-the-loop workflows, time travel, and fault tolerance. Stores persist application-defined data outside the graph state. Use them for long-term, cross-thread memory, including user preferences, facts, and shared knowledge. Most applications can use both: a checkpointer tracks the current thread, and a store tracks durable information across threads."

This is not a third-party pattern or a best-practice suggestion — it is a core, named LangGraph subsystem (`langgraph.store`) with the same first-class status as the checkpointer subsystem already documented extensively in Section 1.

### The Asymmetry That Was Not Previously Captured

> "The checkpointer is invisible to the developer and end user. LangGraph handles it automatically when you compile with checkpointer=. The Store requires explicit read/write in your node functions. That asymmetry, automatic vs coded, is deliberate: conversation history is structural while long-term memory is a product decision and full of complexity."

This single sentence resolves something this document never made explicit: **Section 19's working-memory compression (Gap 19) is partially the wrong framing.** The checkpointer already handles message-history persistence automatically — what Agent Improve actually needs is not "make checkpointing smarter," it is **explicit Store reads/writes for the cross-case knowledge currently living in `improve_case_index`**, which is a genuine application-design decision requiring code, exactly as this source describes.

### Corrected Architecture for Agent Improve

```python
from langgraph.store.memory import InMemoryStore       # dev
from langgraph.store.postgres import PostgresStore      # production
from langgraph.checkpoint.postgres import PostgresSaver # production

checkpointer = PostgresSaver.from_conn_string(PG_CONN)   # short-term, thread-scoped
store = PostgresStore.from_conn_string(PG_CONN)          # long-term, cross-thread

graph = builder.compile(checkpointer=checkpointer, store=store)

# Inside any node — store is injected automatically when declared as a parameter
def analyse_node(state: AnalyseState, config: RunnableConfig, *, store: BaseStore) -> dict:
    case_id = config["configurable"]["case_id"]

    # Long-term cross-case retrieval — replaces ad-hoc improve_case_index queries
    namespace = ("dmaic_cases", "call_centre", "complaint_rate")
    similar_cases = store.search(namespace, query=state["root_cause_candidate"])

    # Write this case's outcome for FUTURE cases to retrieve
    store.put(namespace, case_id, {
        "root_cause": state["root_cause_candidate"],
        "phase_summary": state["phase_summary_analyse"],
        "outcome": "validated"
    })
```

### What This Means for `improve_case_index` Specifically

`improve_case_index` (Section 36, the Azure AI Search index with `phase_summary_*` fields and an `embedding` vector field) is functionally **a hand-built, Azure-AI-Search-backed approximation of what `PostgresStore` provides natively** with semantic search support built in (`InMemoryStore` and `PostgresStore` both support an `index=` parameter for embedding-based search, per the official source above). This raises a genuine architectural question worth deciding deliberately rather than defaulting:

```
Option A — Keep improve_case_index as-is (Azure AI Search)
  + Already built, already has hybrid BM25+vector (Section 32)
  + No migration work
  − Not LangGraph-native; requires custom glue code at every read/write site
  − Does not benefit from BaseStore's namespace/TTL/batch features for free

Option B — Migrate cross-case memory to PostgresStore
  + LangGraph-native — `store` parameter auto-injected into any node, no glue code
  + Same Postgres instance already planned for the checkpointer (Section 1) — no new infra
  + Gets TTL-based expiration and namespace hierarchy for free (see below)
  − Loses Azure AI Search's BM25 hybrid scoring unless reimplemented
  − Migration effort for existing case data
```

**Recommendation for the gap register:** this is not a "must fix" gap — `improve_case_index` is functioning RAG infrastructure, not broken. But it should be evaluated explicitly during the refactor rather than left as an unexamined assumption, specifically because Option B removes an entire category of custom integration code (every place the codebase currently does manual Azure AI Search client calls becomes a simple `store.search()` / `store.put()` call with automatic checkpointer-grade reliability guarantees).

### Two Critical Operational Findings Not Previously Documented

**Finding 1 — `thread_id` has a hard length limit of 255 characters with `PostgresSaver`:**

> "When using PostgresSaver (or AsyncPostgresSaver), the thread_id is stored in a column with limited length. If your thread_id exceeds the column size, you will see a database error. Fix: Keep thread_id values under 255 characters."

This is directly relevant to the nested-subgraph thread_id naming convention already established in Section 44 and used throughout Section 22's debate subgraph example: `f"{case_id}-define-debate-{root_cause_id}"`. If `case_id` follows a pattern like `IMPR-2026-E9D` and `root_cause_id` is a long descriptive slug rather than a short UUID, deeply nested thread_id concatenation across Define → Analyse → Debate → multiple rounds could plausibly approach this limit in a long-lived project. **Recommendation: use short UUIDs or hashes for any generated sub-thread_id component, not descriptive strings, and validate length defensively before any `PostgresSaver` write.**

**Finding 2 — confirmed documented LangGraph limitation: subgraph state updates do not automatically propagate to the parent:**

> "When a subgraph updates state, the parent graph may not see the changes immediately. This is because each subgraph manages its own checkpoint namespace. Fix: Use shared state via Store for data that needs to cross graph boundaries, or configure your subgraph to write to the parent checkpoint."

This is a **direct, material refinement to Section 44's state boundary contract mechanics** (Mechanism 1 — Shared Key Names). The document previously described shared-key-name propagation as fully automatic; this official source confirms there are documented cases where it is not immediate, and explicitly recommends the **Store** as the correct fix for cross-boundary data — not just shared key names or transformer functions. This should be treated as a required verification step during implementation: test that `DefineOutput` genuinely appears in `DMAICState` immediately after the Define subgraph node returns, under the actual installed LangGraph version, rather than assuming Section 44's description is sufficient without an integration test.

### Gap Register Update

**Gap 20 is REVISED a second time.** The first revision (Section 36) confirmed `improve_case_index` already provides cross-case memory. This second revision adds: the LangGraph-native equivalent (`BaseStore`/`PostgresStore`) exists and should be evaluated as a structural replacement or complement, not assumed unnecessary just because a working alternative already exists.

**New: Gap 30** — `thread_id` length validation. No current safeguard against generated nested thread_id strings exceeding the 255-character PostgresSaver column limit. Low effort, should be fixed alongside Gap 25's checkpointer work.

**New: Gap 31** — subgraph-to-parent state propagation is not verified to be immediate under the actual installed LangGraph version; Section 44's Mechanism 1 (shared key names) should be integration-tested, not assumed, before being relied upon for `DefineOutput`-style boundary contracts. If propagation lag is confirmed, the official-recommended fix is routing cross-boundary data through `Store` rather than shared state keys.

---

## 53. MAJOR FINDING — Built-In Middleware Replaces Most of Gaps 2, 19, and Part of 23

*Source: Verified against docs.langchain.com/oss/python/langchain/middleware/overview, the official LangChain "How Middleware Lets You Customize Your Agent Harness" blog post, and the official Human-in-the-Loop documentation. All confirmed current for LangChain 1.0+ / LangGraph 1.2.6, June 2026.*

This is the second major architectural finding from this audit, and it is genuinely consequential: **LangChain 1.0 ships official, production-supported middleware that implements a working-memory-compression solution (Gap 19) and a human-in-the-loop approval mechanism (most of Gap 2) as drop-in components, requiring no custom node design.** This significantly de-risks and simplifies two of the highest-priority gaps in the register.

### `SummarizationMiddleware` — A Production Answer to Gap 19

```python
from langchain.agents import create_agent
from langchain.agents.middleware import SummarizationMiddleware

agent = create_agent(
    model="azure-openai:gpt-4o",
    tools=[...],
    middleware=[
        SummarizationMiddleware(
            model="azure-openai:gpt-4o-mini",   # cheaper model for summarisation, confirmed pattern
            max_tokens_before_summary=400,        # trigger threshold
            messages_to_keep=5                    # always preserved in full, untouched
        )
    ]
)
```

**Confirmed mechanics, directly from the official source:** *"LangChain's builtin SummarizationMiddleware implements the before_model hook. To avoid context overflow, if message history exceeds a certain token threshold, its contents are summarized before being passed to the model."*

**This is structurally identical to the structured-JSON compression design this document arrived at independently in Section 36** (the revised approach replacing prose summary with structured JSON, agreed during direct discussion) — but Gap 19's custom `compress_messages()` function and `needs_compression()` trigger logic are **no longer necessary to hand-write**. The middleware provides the trigger condition, the summarisation call, and the message-list replacement automatically.

**One important divergence to flag honestly:** the official `SummarizationMiddleware` summarises into **prose**, not the structured JSON context object this document specifically argued for in Section 36 (*"Why prose summary is wrong... LLM reads exact values directly... aligns with typed state schema principle"*). This is a genuine design tension worth resolving deliberately rather than defaulting to the built-in behaviour:

```
Option A — Use SummarizationMiddleware as-is
  + Zero custom code, officially maintained, handles edge cases (token counting, model selection)
  − Summarises to prose, re-introducing the exact problem Section 36 argued against

Option B — Keep Section 36's structured JSON approach as a custom before_model hook
  + Preserves the typed-state-schema discipline already established throughout this document
  − Re-implements logic the middleware already provides for free

Option C — Hybrid: use SummarizationMiddleware's trigger/threshold mechanics,
            but override its summarisation call to emit structured JSON instead of prose
  + Gets the maintained trigger logic AND the structured output discipline
  − Requires subclassing or wrapping AgentMiddleware — moderate custom work
```

**Recommendation:** Option C deserves serious consideration during implementation — middleware is explicitly designed to be subclassed (*"Builders can also subclass the AgentMiddleware class to write your own for anything bespoke to your business"*), and `captured_fields` is already structured. A custom middleware that triggers on the same token threshold but writes a `conversation_context` JSON object (per Section 36) rather than a prose paragraph would deliver both benefits.

### Deep Agents' `SummarizationMiddleware` Variant — An Even Closer Match

A more specific finding: Deep Agents (LangChain's "batteries-included" harness, built on `create_agent`) ships a **wrapped version** of `SummarizationMiddleware` with capabilities directly relevant to Agent Improve's multi-week DMAIC sessions:

> "Backend offload of evicted history. Evicted messages are appended to /conversation_history/{thread_id}.md ... before the summary replaces them, and the summary embeds that path so the agent can re-open it via read_file ... LangChain drops evicted messages with no recovery path [in the base version]."

This directly resolves a gap in the base `SummarizationMiddleware` that would otherwise apply to Agent Improve: **the base middleware permanently discards old messages once summarised — exactly the data-loss risk this document worried about in Section 36's original (pre-correction) framing.** Deep Agents' variant offloads evicted history to a retrievable file rather than discarding it, which is a closer match to the audit-trail discipline already established throughout this document (Section 24's "every boundary is traced" principle, Section 44's structured output requirements).

### `HumanInTheLoopMiddleware` — Resolves Most of Gap 2

```python
from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware
from langgraph.checkpoint.memory import InMemorySaver

agent = create_agent(
    model="azure-openai:gpt-4o",
    tools=[capture_gate_fields, advance_phase],
    middleware=[
        HumanInTheLoopMiddleware(
            interrupt_on={
                "advance_phase": {"allowed_decisions": ["approve", "edit", "reject"]},
                "capture_gate_fields": False   # no HITL needed for this tool
            }
        )
    ],
    checkpointer=InMemorySaver()   # confirmed mandatory — without it, paused state is lost
)
```

**Confirmed resume mechanics, exact current API (verified against official docs and multiple corroborating sources):**

```python
from langgraph.types import Command

result = agent.invoke(
    {"messages": [{"role": "user", "content": "..."}]},
    config={"configurable": {"thread_id": case_id}},
    version="v2"
)

if result.interrupts:
    interrupt_value = result.interrupts[0].value
    action_requests = interrupt_value["action_requests"]
    review_configs = interrupt_value["review_configs"]

    decisions = [
        {"type": "approve"},
        {"type": "edit", "editedAction": {"name": "advance_phase", "args": {...corrected_fields...}}},
        {"type": "reject", "message": "Root cause not validated, sending back to coaching"}
    ]

    result = agent.invoke(
        Command(resume={"decisions": decisions}),
        config={"configurable": {"thread_id": case_id}},
        version="v2"
    )
```

**This is a direct, more mature implementation of exactly the gate-review pattern this document designed independently in Section 2 and Section 12** (the "Edit" loop, the GET/POST `/gate/review` and `/gate/approve` endpoints). The official `decisions` array with `approve`/`edit`/`reject` types, applied per-action in order, is functionally identical to what was designed from first principles — confirming that design was sound — but it is now backed by an officially maintained middleware rather than custom interrupt-handling code.

### Two Confirmed Open Bugs Worth Flagging Before Relying on This in Production

**Bug 1 — `edit` decisions can cause the agent to re-attempt the original (un-edited) tool call:**

> "When an agent's tool call is interrupted by the HumanInTheLoopMiddleware and the human operator chooses the edit decision, the middleware successfully executes the edited tool call. However, in the subsequent step, the agent re-evaluates its state... and generates a new AiMessage that attempts to execute the original, un-edited tool call... forcing the user to reject the very action they thought their edit had already replaced."

This is a confirmed open GitHub issue (langchain-ai/langchain #33787) on a recent `langchain` version (1.0.3). **Direct relevance to Agent Improve:** this is precisely the scenario where a Belt corrects an AI-extracted field value (Section 38's conflict resolution discussion, Gap 21's feedback-adaptation signal). If this bug is still present in the version actually installed in `agent-improve/.venv`, a Belt's correction could be silently re-overwritten by the agent re-attempting its original (wrong) extraction on the next turn. **This must be verified against the installed version before relying on `edit` decisions for gate field corrections.**

**Bug 2 — `edit`/`reject` modes confirmed broken specifically in subagent contexts, only `approve` works correctly:**

> "When using create_deep_agent with subagents and interrupt_on configuration, the interrupt/resume mechanism only works correctly for approve mode. The edit and reject modes fail to work as expected."

This is a confirmed open GitHub issue (langchain-ai/deepagents #554), and it is **directly and severely relevant to Agent Improve's nested-subgraph architecture** (Section 44's recursive Orchestrator → Phase Subgraph → Step-Subagent pattern, Section 22's debate subgraph). If a HITL interrupt fires *inside* a phase subgraph (e.g. the Define subgraph's internal `validate` step needing Belt confirmation) rather than at the top-level Orchestrator, this bug suggests `edit` and `reject` decisions may not propagate correctly through the subgraph boundary — only blanket `approve` is confirmed reliable in that nested context as of the version tested in that issue.

**This is a critical verification item, not just a footnote.** Given Section 44's entire architecture depends on each phase subgraph owning its own interrupt (stated explicitly: *"each phase subgraph owns its own interrupt (quality gate); the main orchestrator only routes based on results"*), this bug — if still present in the installed version — could mean the Belt's "edit" and "reject" capability at sub-orchestrator-level gates does not work as designed, with only "approve" being reliable. This single finding could materially change the gate placement strategy (favouring top-level Orchestrator-level interrupts over nested subgraph-level interrupts until the bug is confirmed fixed).

### Gap Register Updates

**Gap 19 — SIGNIFICANTLY DE-RISKED.** `SummarizationMiddleware` (or a custom subclass per Option C above) provides the trigger/compression mechanics without hand-built logic. Reduce implementation estimate accordingly; the design decision is now "which variant" rather than "build from scratch."

**Gap 2 — SIGNIFICANTLY DE-RISKED, with a critical caveat.** `HumanInTheLoopMiddleware` provides the approve/edit/reject mechanism this document designed independently. However, **Bug 1 and Bug 2 above must be verified against the actual installed package versions before this gap is considered resolved** — both bugs directly threaten the specific use cases Agent Improve needs (field correction via edit, nested subgraph-level interrupts).

**New: Gap 32** — Verify `HumanInTheLoopMiddleware` edit/reject behaviour against the actual installed `langchain`/`langgraph` versions in `agent-improve/.venv`, specifically: (a) whether edited tool-call arguments persist correctly without the agent re-attempting the original call, and (b) whether edit/reject decisions function correctly when the interrupt originates inside a subgraph rather than the top-level graph. This verification should happen before Gap 2's HITL implementation is considered de-risked, and its outcome should directly inform whether interrupts are placed at the Orchestrator level, the Phase Subgraph level, or both.

---

## 54. Correction to Section 42 — RubricMiddleware Exact Requirements and API

*Source: Verified directly against docs.langchain.com/oss/python/deepagents/rubric, current as of June 2026 (confirmed via direct documentation reference, and a blog post dated within the last week relative to current date — this is very recently shipped, actively evolving functionality).*

Section 42 correctly captured RubricMiddleware's purpose and value but was imprecise on two points, now corrected:

**Correction 1 — package requirement is explicit and versioned:**
> "RubricMiddleware requires deepagents>=0.6.5. It is in beta; the API may change in the future."

This is a `deepagents` package feature specifically, not a general `langchain.agents` middleware. It must be attached via `create_deep_agent`, not the plainer `create_agent` used elsewhere in this document's corrected patterns (Section 50, 53):

```python
from deepagents import RubricMiddleware, create_deep_agent   # NOT langchain.agents.create_agent
from langgraph.checkpoint.memory import InMemorySaver

agent = create_deep_agent(
    model="google_genai:gemini-3.5-flash",   # confirmed: any provider works
    middleware=[
        RubricMiddleware(
            model="anthropic:claude-haiku-4-5",
            max_iterations=3,
        ),
    ],
    checkpointer=InMemorySaver(),
)
```

**Temperature discipline — evaluation nodes vs coaching nodes:**

```python
# Coaching node — moderate temperature, natural language variation is acceptable
coaching_agent = create_deep_agent(
    model="azure-openai:gpt-4o",
    model_kwargs={"temperature": 0.7},   # some variation is natural and good
    ...
)

# RubricMiddleware grader — low temperature, consistency is critical
RubricMiddleware(
    model="anthropic:claude-haiku-4-5",
    model_kwargs={"temperature": 0.1},   # repeatable, structured evaluation output
    max_iterations=3,
)
```

Evaluation and grading nodes must produce consistent, repeatable structured outputs — the same gate document should receive the same verdict across runs. High temperature introduces variance that makes regression testing (Section 75) unreliable. Low temperature (0.0–0.2) for all graders, validators, and field extractors. Moderate temperature (0.5–0.7) for coaching responses where natural language variation improves the Belt's experience.

**Implication for Agent Improve:** if Gap 23 (rubric-based gate evaluation) is to use the official `RubricMiddleware` rather than a hand-built equivalent, the phase subgraphs built as `create_agent`-based agents (per Section 50/53's corrected patterns) would need to be `create_deep_agent`-based instead specifically to access this middleware — or a custom reflection node should be hand-built using the same LLM-as-a-judge pattern without the `deepagents` dependency. This is a real architectural decision point not previously surfaced: **adopting RubricMiddleware means adopting the `deepagents` package as a dependency for at least the phase subagents that need rubric grading**, which is a larger commitment than a single middleware import.

**Correction 2 — state schema is more precise than Section 42 implied:**

> "Only rubric is part of the public I/O schema -- callers write a rubric and read the improved agent response back from messages. Everything else is bookkeeping: status, iteration count, accumulated evaluations, and rubric-attempt tracking are annotated with PrivateStateAttr so they are omitted from input/output schemas."

This confirms a clean boundary contract consistent with Section 44's typed-boundary-output principle: the rubric grading internals (iteration count, accumulated evaluations) stay private to the middleware's own state, never leaking into `DMAICState`. Only the rubric string goes in, and the graded final response comes out via `messages`. Observability into the grading process (which Gap 23's audit-trail requirement needs) is available via a separate, explicit mechanism:

```python
from deepagents.middleware.rubric import RubricEvaluation

def log_evaluation(ev: RubricEvaluation) -> None:
    print(f"iteration {ev['iteration']}: {ev['result']} — {ev['explanation']}")
    # write this to step_log (Section 18's audit trail field) for DMAIC compliance

agent = create_deep_agent(
    model="...",
    middleware=[RubricMiddleware(model="...", on_evaluation=log_evaluation)],
    checkpointer=InMemorySaver(),
)
```

The `on_evaluation` callback is the precise mechanism for feeding rubric-grading decisions into Section 18's `step_log` field — closing a gap that was previously unaddressed in how RubricMiddleware's internal reasoning would become part of the DMAIC audit trail.

### Gap Register Update

**Gap 23 refined, not changed in priority.** Implementing via official `RubricMiddleware` requires the `deepagents` package and `create_deep_agent` specifically (`deepagents>=0.6.5`), not plain `create_agent`. This is a dependency decision that should be made explicitly and early, since it affects which agent-construction pattern every phase subagent uses, not just the ones needing rubric grading. The `on_evaluation` callback is the integration point for Gap 23's audit-trail requirement (Section 18, `step_log`).

---

## 55. LangServe — Archived, Superseded by LangGraph Platform / LangSmith Deployment

*Source: Verified against GitHub (langchain-ai/langserve), the official deprecation notice, and the LangGraph Platform GA announcement. Triggered by encountering "LangServe" mentioned in the Course 4 (MCP) introduction without prior context in this document.*

### What It Was

LangServe was LangChain's original deployment tool — it wrapped a LangChain `Runnable` or chain in a FastAPI server automatically, generating `/invoke`, `/batch`, and `/stream` REST endpoints with zero boilerplate, plus a built-in client and a Swagger/OpenAPI playground.

```python
# What LangServe did — now archived, do not use for new work
from langserve import add_routes
from fastapi import FastAPI

app = FastAPI()
add_routes(app, my_runnable, path="/agent")
# Automatically creates POST /agent/invoke, /agent/batch, /agent/stream
```

### Current Status — Confirmed Archived

> "This repository was archived by the owner on May 5, 2026. It is now read-only."

This is recent — roughly two months before the current date. The official deprecation notice, present in the README before archival:

> "We recommend using LangGraph Platform rather than LangServe for new projects... We will continue to accept bug fixes for LangServe from the community; however, we will not be accepting new feature contributions."

A second source (March 2026) confirms the deprecation was already settled industry knowledge before the archival: *"LangServe has been deprecated, so LangGraph Platform is now the recommended path for deployment and hosting."*

### What Replaced It

**LangGraph Platform**, subsequently **renamed to "LangSmith Deployment"** as of October 2025 (confirmed: *"Note: As of October 2025, LangGraph Platform has been re-named to 'LangSmith Deployment'"*). This is a more significant successor than a simple rename suggests — it is not a like-for-like replacement of LangServe's thin FastAPI wrapper, but a full deployment and management platform:

> "In contrast to LangServe, LangGraph Platform provides comprehensive, out-of-the-box support for persistence, memory, double-texting handling, human-in-the-loop workflows, cron job scheduling, webhooks, high-load management, advanced streaming, support for long-running tasks, background task processing, and much more."

**Component breakdown, confirmed from official source:**
- **LangGraph Server** — provides an Assistants API for graphs built with LangGraph
- **LangGraph Studio** — a dedicated IDE for real-time visualisation, debugging, and interaction (web app or macOS desktop app) — explicitly described as superseding LangServe's playground
- **SDK** — Python and JavaScript/TypeScript clients for programmatic interaction
- **RemoteGraph** — LangServe's `RemoteRunnable` equivalent, lets you interact with a remote graph as if it were local

**Deployment tiers confirmed available:** Cloud (SaaS, fastest to start, fully managed from within LangSmith), Hybrid, Self-hosted, and Standalone Container — giving a real choice for an enterprise context like AgentLean where data residency or Azure-hosted infrastructure may be a constraint.

### Direct Relevance to Agent Improve

This document has, until now, said nothing about how Agent Improve's compiled graphs are actually exposed as an API to the frontend — Section 1 onward has focused entirely on the graph/state/checkpoint architecture, implicitly assuming a hand-built FastAPI layer (consistent with the existing `agent-improve` codebase, which uses FastAPI directly per the project's CLAUDE.md and `routes.py` references throughout earlier sections of this document).

**This raises a genuine question worth deciding deliberately during the DMAIC redraw, not by default:**

```
Current AgentLean approach (confirmed from earlier sections):
  FastAPI hand-built routes → graph.ainvoke() → response
  Custom SSE streaming wiring
  Custom checkpoint thread_id management in routes.py

LangGraph Platform / LangSmith Deployment alternative:
  LangGraph Server provides the Assistants API automatically
  Built-in streaming, HITL, persistence, background tasks — no custom wiring
  LangGraph Studio gives a debugging UI superior to anything hand-built
```

**Honest assessment, not a recommendation to switch:** AgentLean already has a working FastAPI layer, and a wholesale migration to LangGraph Platform/LangSmith Deployment would be a significant infrastructure decision with real costs (vendor relationship with LangSmith's hosted tiers, or self-hosting the platform components, versus the Azure-native FastAPI approach already in place and already aligned with the `valuesims-*` → `agentlean-*` Azure migration plan). This is **not** something to default into — it should be weighed explicitly as an option during the DMAIC redraw, specifically around the question of whether hand-rolling SSE streaming, HITL resume endpoints (Section 53's `decisions` array), and checkpoint thread_id routing in custom FastAPI code is worth the control it preserves, versus adopting LangGraph Server's built-in equivalents and gaining LangGraph Studio's debugging capability for free.

### What This Means Right Now

No gap number assigned — this is **flagged for explicit discussion during the DMAIC redraw**, not an architectural gap in the sense of something broken or missing. The two real options (continue hand-building on FastAPI, or adopt LangGraph Platform/LangSmith Deployment) both have legitimate justifications, and the choice has downstream consequences for Sections 1, 12, 44, and 53's HITL/checkpoint implementation details that should be made once, deliberately, rather than discovered mid-implementation.

---

## 56. Course 4 (MCP) — Confirmed Stale Deployment Tooling, Caution Flagged for Module 3

*Source: Direct course transcript, Course 4 introduction, cross-referenced against Section 55's verified findings.*

### What the Course States

The course's tools section explicitly names five tools for the full course:

> "MCP forms the foundation for agent communication and orchestration. Python is used to implement agent logic, tools and workflows. LangServe allows you to expose agents as scalable APIs. LangSmith provides observability into prompts, tools, latency and failures. And Docker enables consistent packaging and deployment across environments."

### The Direct Conflict With Section 55

This explicitly names **LangServe** as the tool for exposing agents as APIs — precisely the tool confirmed archived by its own maintainers in May 2026 (Section 55), roughly two months before the current date, with an official recommendation in place since at least 2024 to use LangGraph Platform / LangSmith Deployment instead.

**This is no longer a minor syntax-currency issue (like Section 50's `create_react_agent`) — it is a course recommending students build their Module 3 production deployment architecture on a tool that:**
1. Receives no new feature contributions (true even before archival)
2. Is now fully archived and read-only
3. Has an actively maintained, more capable official replacement that has existed in some form since before this course was likely recorded

### Important Update — Full Syllabus Confirms This Is Not Just an Intro Script Issue

The complete course syllabus (not just the spoken introduction) lists LangServe as an explicit, graded learning outcome:

> "Deploy agents as production APIs using LangServe"

and names it as a core technology for the **entire course**, not just Module 3:

> "Technologies Used in this Course: ... Model Context Protocol (MCP), Python, LangServe, LangSmith, Structured schemas and URI-based resource design."

This removes the earlier hedge in this section — it is no longer plausible that only the intro voiceover is stale while the lab code has been quietly updated. **LangServe is baked into the curriculum's stated learning objectives and module structure**, specifically:

> "All demonstrations are fully guided and designed to reflect real production agent systems, without requiring specialized infrastructure."

Combined with the explicit Module 3 lesson title **"Production Agent APIs and Execution Visibility"** and **"End-to-End Application Deployment"**, this strongly suggests the actual demonstration code in Module 3 — and possibly Module 1's MCP server demos, since MCP servers are commonly exposed via a web framework for testing — will use `langserve.add_routes()` or equivalent, genuinely archived code.

**Revised guidance: treat any deployment-pattern code shown in this course (API exposure, server wrapping, "production-ready" framing) as needing direct substitution with the LangGraph Server / LangSmith Deployment pattern from Section 55, by default, rather than waiting to see if it turns out to be current.** The earlier "it might have been patched" benefit of the doubt no longer applies given the syllabus-level confirmation.

### What Remains Trustworthy vs What Needs Independent Verification

Confirming the pattern already established across this document — the issue is consistently in **specific named tools and library versions**, not in conceptual architecture:

| Course Element | Trust Level | Basis |
|---|---|---|
| MCP — foundation for agent communication | ✅ Trust, verify specifics as encountered | Genuinely current; MCP itself is an active, evolving standard, not deprecated |
| Python for agent logic | ✅ Trust | Not a versioned claim |
| Deep Agents, RubricMiddleware (Module 2 topic) | ✅ Likely current | Confirmed independently in Section 53/54 against live docs, shipped within days of current date |
| **LangServe for API exposure** | ❌ **Confirmed stale** | Archived May 2026, Section 55 |
| LangSmith for observability | ✅ Likely current | LangSmith itself remains actively developed and renamed/expanded (Section 55: LangGraph Platform → LangSmith Deployment), though the course's specific *usage pattern* should still be checked against current LangSmith docs when reached |
| Docker for packaging | ✅ Trust | Not a versioned LangChain-ecosystem claim |

### What This Means Going Into Module 3 Specifically — and a New Risk in Module 1

**Treat all of Module 3's deployment content as presumptively using archived LangServe patterns**, not just "possibly stale." When Module 3 content arrives, the specific things to flag for direct substitution rather than verification-in-doubt:

- Any `from langserve import ...` code shown — substitute with the LangGraph Server / LangSmith Deployment equivalent from Section 55
- Any reference to a "LangServe playground" — superseded by LangGraph Studio
- Any API exposure pattern (`add_routes`, etc.) — replace with `create_agent`/`create_deep_agent`'s native deployment path or hand-built FastAPI, per Section 55's two real options

**New risk surfaced by the full syllabus, not previously flagged:** Module 1's MCP server demonstrations may also use LangServe to expose the MCP server for testing/demo purposes, since the syllabus lists LangServe as a technology for "this course" broadly, not scoped only to Module 3. **When Module 1's downloadable demo code arrives, check its imports immediately before treating any server-exposure pattern shown there as current** — do not assume MCP server fundamentals (Lesson 1's architecture/communication model, Lesson 2's tool/resource schemas) are affected, since those are protocol-level and framework-agnostic, but the specific *runnable demo wiring* used to stand up and test those servers may not be.

### Gap Register Note

No new gap number — this remains a **course-material reliability flag**, not an AgentLean architectural gap. Confidence downgraded from "verify when encountered" to "assume stale, substitute by default" given the syllabus-level confirmation above.

---

## 57. CORRECTION — Course Slide Mischaracterises MCP as "Agent-to-Agent" Protocol; It Is Agent-to-Tool/Data

*Source: Direct discussion, verified against the official MCP specification site, an arXiv survey paper, Anthropic's own framing, and multiple independent technical sources, all in agreement. This is a clear, confirmed correction to course material — not an ambiguous edge case.*

### What the Course Slide Said

A course slide titled "What is Model Context Protocol?" listed as point 01:

> "Standard protocol for context exchange between agents"

### Why This Is Wrong, Confirmed Across Sources

This is a genuine mischaracterisation, not a simplification. Every authoritative source checked draws the same sharp distinction, using nearly identical language independently:

> "MCP is about connecting a single AI agent to its tools, data, and external systems. A2A is about enabling multiple AI agents to talk to each other — even if they come from different companies or use different frameworks... They solve different problems."

> "MCP (Model Context Protocol) is a structured way to let AI agents access tools, APIs, or external resources. Agent-to-Agent (A2A) communication, by contrast, is how agents collaborate with each other to accomplish tasks. MCP and A2A are not competing standards, they're complementary building blocks."

> "MCP standardizes how AI systems interact with external data and tools. Think of it as establishing the equivalent of USB-C for AI."

**The official MCP specification itself** (2025-03-26, confirmed) defines it precisely:

> "An open protocol for integration between LLM applications and external data sources and tools."

There is no mention of inter-agent communication in the formal definition. Agent-to-agent communication is a **separate, distinct protocol** — Google's **A2A (Agent-to-Agent)** — explicitly designed to solve the different problem the course slide incorrectly attributes to MCP.

### Confirmation This Maps Directly to Your Instinct

Your stated understanding — *"agents interchange info at the main state level"* — is precisely correct and is exactly what Sections 44 and 50–52 of this document already establish as the architecture for Agent Improve:

```
How agents ACTUALLY exchange information in LangGraph (confirmed, Sections 44/52):
  Agent A → writes to shared State / Checkpointer / Store → Agent B reads from same State/Store
  This is NOT MCP. This is LangGraph's own state-passing mechanism.

What MCP ACTUALLY does (confirmed, this section):
  Agent → MCP Client → MCP Server → external tool/database/API → result returns to Agent
  This is agent-to-TOOL, not agent-to-agent.
```

The slide conflated two entirely separate concerns: **how agents talk to each other** (LangGraph state/Store, or a separate protocol like A2A) versus **how a single agent talks to external tools and data** (MCP). These are genuinely different problems with genuinely different protocols, not two framings of the same thing.

### The Correct Five Points, Rewritten

| # | Course Slide Said | Should Say |
|---|---|---|
| 01 | "Standard protocol for context exchange between agents" | Standard protocol for an agent to access external tools, data, and resources |
| 02 | "Defines how models share data, goals, and memory" | Defines how a model discovers and invokes tool capabilities, and accesses resources, through structured schemas |
| 03 | "Ensures consistent understanding across multiple systems" | ✅ Roughly accurate — ensures a consistent interface regardless of which underlying system/database/API is behind the MCP server |
| 04 | "Enables collaboration and interoperability in reasoning" | Enables interoperability between agents and the tools/data sources they each independently need — not collaboration between agents |
| 05 | "Core to building multi-agent, context-aware systems" | Core to building tool-aware, data-connected agent systems (singular or multi-agent — but the protocol itself addresses the tool/data layer, not the agent-coordination layer) |

### Where Genuine Nuance Exists — Not Everything in the Original Framing Is Baseless

One source confirms the slide's error is understandable as a **directional misstatement of where the field is heading**, not pure fabrication:

> "The current MCP specification focuses on 'Host-to-Server' communication. The next frontier is 'Agent-to-Agent' communication."

So agent-to-agent communication via something MCP-adjacent is a stated **future direction** for the protocol's evolution — but it is explicitly **not** what current MCP does, and conflating the roadmap aspiration with the present specification is exactly the kind of imprecision this document has flagged repeatedly (Sections 50, 53, 55, 56).

**Also confirmed: the MCP specification is under genuinely active, fast revision right now** — a release candidate for spec version 2026-07-28 was published roughly five weeks before your current date, with the final specification due July 28, 2026 (just weeks away). That release candidate reportedly deprecates several existing MCP primitives (Roots, Sampling, Logging) and introduces new ones (a stateless protocol core, Extensions, Tasks, MCP Apps). **This means anything taught in this course about specific MCP primitives should be treated as a snapshot of a moving target, and re-verified against the 2026-07-28 specification once it finalises**, separate from the agent-to-agent/agent-to-tool conceptual correction above.

### Why This Matters for Agent Improve Specifically

This correction directly sharpens the architecture this document has been building toward for the DMAIC redraw:

```
Agent Improve's Orchestrator ↔ Phase Subgraphs
  → communicate via LangGraph State, Checkpointer, Store (Section 52)
  → NOT via MCP — MCP is not the right tool for this layer

Phase Subgraphs ↔ External tools/data
  (SAP process data, live KPIs, eBook knowledge index, case index — Section 39's "missing real-time data" gap)
  → THIS is where MCP belongs
  → an MCP server exposing SAP/KPI access would let any phase subagent
    query real-time data through a standardised tool interface,
    rather than each phase subagent needing custom integration code per data source
```

This is a precise, useful clarification of where MCP slots into the architecture we'll redraw — confirming the placement already implied in Section 39 and Section 51 ("knowledge tools" as external to the agent-to-agent reasoning layer) but now stated with full confidence rather than as an inference.

### Gap Register Note

No new gap number — this is a **conceptual correction to course material**, recorded here because it directly informs where MCP will be placed in the DMAIC redraw. Your instinct that "agents interchange info at the main state level" was correct and should be treated as the settled understanding going forward, not revisited as uncertain.

---

## 58. CORRECTION — Course Slide's "Core Functional Layers of MCP" Does Not Match the Official Specification

*Source: Verified directly against modelcontextprotocol.io/docs/learn/architecture (the official MCP specification site), plus seven independent corroborating technical sources, all in close agreement with each other and with the official spec. This is the second confirmed material error from this same course module, following Section 57.*

### What the Course Slide Presented

Four "core functional layers": Context Schema (standardized structure for shared information), Synchronization Engine (maintains consistent shared state across components), Access APIs (controlled retrieval of agent or memory data), Security Layer (manages access, tokens, and encryption).

### What the Official Specification Actually Defines

From `modelcontextprotocol.io` directly:

> "Data layer: Defines the JSON-RPC based protocol for client-server communication, including lifecycle management, and core primitives, such as tools, resources, prompts and notifications. Transport layer: Defines the communication mechanisms and channels that enable data exchange between clients and servers, including transport-specific connection establishment, message framing, and authorization. Conceptually the data layer is the inner layer, while the transport layer is the outer layer."

**MCP officially has exactly TWO layers, not four:**

```
Data Layer (inner)        — WHAT is communicated and WHAT IT MEANS
  ├── Lifecycle management (initialize → capability negotiation → ready)
  ├── Tools          — executable functions agents can invoke
  ├── Resources      — read-only data, URI-addressed
  ├── Prompts        — reusable prompt templates
  └── Notifications  — server-pushed events without a request

Transport Layer (outer)   — HOW messages physically move
  ├── STDIO  — local, in-process, fast
  └── HTTP/SSE or WebSocket — remote, distributed
```

### Architecture Components — Also Confirmed, Also Different From the Slide

Independent of the layer model, every source confirms the same three-role component architecture, none of which match the slide's four boxes:

> "MCP architecture consists of a Host, Client and a Server. MCP host manages multiple Client instances, authentication, policies and context aggregation. MCP Clients are created by the host and maintain the Server connection and routes messages... MCP Servers operate independently... and expose external systems for data access."

```
Host    — the LLM application itself (e.g. your agent)
Client  — lives inside the Host, maintains a strict 1:1 connection to one Server
Server  — external, independent process exposing Tools/Resources/Prompts
```

A Host can run multiple Clients to talk to multiple Servers simultaneously — this is the **multi-server discovery** Module 1 Lesson 3 is named after, and it is architecturally sound regardless of the slide's layer-naming error.

### Mapping the Slide's Four Boxes Onto What They Actually Are

This is worth doing precisely, because the slide isn't entirely fabricated — it's mislabeling real concepts using non-standard terminology:

| Slide's Term | What It's Actually Describing | Correct MCP Terminology |
|---|---|---|
| "Context Schema" | The structured format for data exchange | Roughly maps to **Resources** + the JSON-RPC message schema (Data Layer) |
| "Synchronization Engine" | Keeping state consistent | **Not an MCP concept at all.** This is what a LangGraph Checkpointer/Store does (Section 52), or what the host-side client's "state management" function does per one source: *"State management: Maintaining conversational history and user context across multiple interactions"* — that's a Client/Host responsibility, not a distinct MCP "layer" |
| "Access APIs" | Controlled data retrieval | Roughly maps to **Resources** (read-only, URI-addressed) combined with the Security/authorization concerns of the Transport Layer |
| "Security Layer" | Tokens, encryption, access control | ✅ Reasonably accurate — authorization is explicitly part of the Transport Layer per the official spec, though it's a sub-component, not a peer-level "layer" alongside the others |

**The most significant error: "Synchronization Engine" is not an MCP concept.** This appears to be the same conflation flagged in Section 57 — bleeding LangGraph's own state-management responsibility (or general distributed-systems thinking) into a slide nominally about MCP specifically. The official spec has no primitive or layer by this name or function.

### Why This Pattern Keeps Appearing — Worth Naming Directly

This is now the **second** instance in two consecutive slides (Section 57, this section) where the course material:
1. Takes a real, important AI-systems concept (state synchronization, agent-to-agent context exchange)
2. Incorrectly attributes it to MCP specifically
3. When MCP does not, in fact, address that concern — something else in the stack does (LangGraph's Checkpointer/Store for synchronization; A2A for agent-to-agent)

**The likely root cause, worth noting honestly:** MCP is presented in many secondary sources and course materials as a generic "AI systems glue" concept rather than the precisely scoped protocol it actually is. Marketing and course framing for MCP tends toward maximalist claims ("the backbone of agentic AI," "core to multi-agent systems") that go beyond what the formal specification actually commits to. This is consistent with one source's own framing: *"MCP doesn't replace APIs for other purposes... they solve different problems."* The discipline going forward should be: **whenever a course slide attributes a general distributed-systems capability to MCP specifically, check it against `modelcontextprotocol.io` directly before recording it as fact.**

### What This Means for the DMAIC Redraw

This sharpens, rather than changes, the placement already established in Section 57:

```
Synchronization between Orchestrator and Phase Subgraphs
  → LangGraph Checkpointer + Store (Section 52)
  → NOT MCP — confirmed now, with no remaining ambiguity

Access to external tools/data (SAP, eBook index, case index, live KPIs)
  → MCP Server, exposing Tools and Resources
  → Security/authorization handled at MCP's Transport Layer

Within the MCP Server itself, if Agent Improve builds one:
  → Tools: e.g. "fetch_sap_complaint_rate", "calculate_sigma_level"
  → Resources: e.g. URI-addressed access to specific case documents or eBook sections
  → Prompts: optionally, reusable coaching-prompt templates exposed for discovery
```

### Gap Register Note

No new gap number — second course-material correction in the same module, recorded for the same reason as Section 57: to ensure the DMAIC redraw uses the verified two-layer (Data/Transport) and three-component (Host/Client/Server) MCP model, not the course slide's four-box model, when MCP is incorporated into Agent Improve's architecture.

---

## 59. MCP Server Implementation — FastMCP, Transports, and Tool Design

*Source: Edureka Course 4 Module 1 demonstration transcript, verified against FastMCP official documentation (gofastmcp.com), PyPI, and multiple independent current sources (April-May 2026). This is the first MCP section with genuinely current, non-deprecated content.*

### FastMCP Is the Confirmed Current Standard

FastMCP is the correct, current framework for building MCP servers in Python. Confirmed figures as of the search date:
- 4 million+ daily downloads (March 2026)
- 70%+ of Python MCP servers use FastMCP
- FastMCP 1.0 was incorporated into the official MCP Python SDK in 2024; the actively maintained standalone project continues under Prefect
- Current version: FastMCP 3.2.4 (MCP 1.27.0 underlying spec, May 2026)

The course's choice of FastMCP for teaching MCP server development is fully current and correct — this is one of the few areas in this course where the tools are genuinely up to date.

---

### The Core Pattern — Confirmed Correct

```python
from fastmcp import FastMCP

mcp = FastMCP("weather")  # Server name becomes its identity for clients

# @mcp.tool decorator registers the function as a discoverable, invocable tool
# No manual route definitions, no JSON handlers, no HTTP wiring needed
@mcp.tool
def get_weather(city: str) -> str:
    """Get weather for a city. Provide city name."""   # docstring = tool description
    city = city.lower()                                 # normalize input — reliability pattern
    if city in weather_data:
        return f"Temperature: {weather_data[city]['temp']}"
    return f"City not found. Available: {list(weather_data.keys())}"   # graceful failure

@mcp.tool
def list_cities() -> list:
    """List all supported cities."""   # discovery tool alongside action tool
    return list(weather_data.keys())

if __name__ == "__main__":
    mcp.run()   # transport determined by argument or default
```

Three things the course correctly highlights that are worth preserving:

**1. The docstring IS the tool description the LLM reads.** Quality docstrings directly affect how accurately an agent selects and calls the tool. This is the same principle as Section 20's "tool docstrings are the routing signal" — confirmed again here at the MCP layer.

**2. Graceful failure with guidance is essential.** When a tool fails, it should tell the caller what went wrong AND what valid options exist — especially important when an AI agent (not a human) will be calling the tool and has no other way to recover. `return f"City not found. Available: {list(weather_data.keys())}"` is the right pattern.

**3. Provide discovery tools alongside action tools.** `list_cities()` with no input parameters, alongside `get_weather()` as the action tool. This lets an agent explore what the server supports at runtime without needing prior knowledge — essential for the multi-server discovery pattern in Module 1 Lesson 3.

---

### The Two Transports — STDIO and HTTP

The course correctly teaches both. The core insight: **the same server code runs on either transport — only `mcp.run()` changes.**

**STDIO — local, process-based:**
```python
if __name__ == "__main__":
    mcp.run()          # default = STDIO
    # OR explicitly:
    mcp.run(transport="stdio")
```
- Client spawns the server as a subprocess, one process per client session
- Communicates via stdin/stdout — no network port, no URL
- Ideal for: local tools, CLI utilities, Claude Desktop integrations, quick dev testing
- The client controls the server's lifetime — when the client disconnects, the process ends

**HTTP — remote, long-lived service:**
```python
if __name__ == "__main__":
    mcp.run(transport="http", port=8000)
    # Server binds to a port, stays alive, accepts multiple clients
    # Available at: http://localhost:8000/mcp/
```
- Server starts once, binds to a port, stays alive indefinitely
- Multiple clients can connect simultaneously (unlike STDIO's one-process-per-client)
- Ideal for: shared team servers, production deployments, remote data sources

---

### CRITICAL TRANSPORT CORRECTION — SSE Is Superseded

**The course was likely built when SSE (Server-Sent Events) was the HTTP transport standard.** This changed in the November 2025 MCP spec update. If the course's lab code uses `transport="sse"` anywhere, that is the outdated pattern.

```python
# OUTDATED (pre-November 2025) — do not use for new work
mcp.run(transport="sse", port=8000)

# CURRENT (November 2025 MCP spec onward) — Streamable HTTP
mcp.run(transport="http", port=8000)   # "http" invokes Streamable HTTP automatically
```

**Why Streamable HTTP replaced SSE:** SSE was one-directional (server pushes to client only). Streamable HTTP provides full bidirectional communication, handles all MCP operations including streaming responses, and is the production standard for remote MCP as of the 2026 spec. It also works better with enterprise WAF inspection.

**Practical rule:** whenever any tutorial or course code shows `transport="sse"`, substitute `transport="http"`. The FastMCP API handles the Streamable HTTP protocol internally — you just change the string.

---

### Transport Selection Decision Table — For Agent Improve

| Scenario | Transport | Reasoning |
|---|---|---|
| Local dev — testing a single MCP tool function | STDIO | Zero setup, fastest feedback loop |
| Agent Improve calling `improve_knowledge_index` during coaching | STDIO (same machine) or HTTP (if index server is remote) | Depends on where Azure AI Search client runs relative to the agent process |
| AgentLean MCP server for SAP/live KPI data | HTTP (Streamable) | Needs to be reachable by all three agents and potentially from Azure cloud |
| AgentLean MCP server for eBook RAG tools | HTTP (Streamable) | Shared across Define/Measure/Analyse/Improve/Control phases |
| Local compute tools (SigmaCalculator, FishboneBuilder) | STDIO | Phase subagent spawns them as subprocess tools, no network needed |

---

### Three-Primitive Reminder — What an MCP Server Exposes

Confirmed from the official spec and every source checked:

```python
@mcp.tool      # Functions the agent can CALL (actions, calculations, API calls)
@mcp.resource  # Data the agent can READ, URI-addressed ("config://...", "data://...")
@mcp.prompt    # Reusable prompt templates the agent can request
```

All three decorators work identically in FastMCP — same pattern as `@mcp.tool`, just different semantic purpose. For Agent Improve's MCP server:
- `@mcp.tool` → `get_process_data(case_id)`, `calculate_sigma(data)`, `fetch_complaint_rate(period)`
- `@mcp.resource` → `"ebook://chapter/analyse-phase"`, `"case://IMPR-2026-E9D/measure-summary"`
- `@mcp.prompt` → optional coaching prompt templates the orchestrator can request

### Gap Register Note
No new gap number — this section confirms that the MCP server implementation pattern the DMAIC redraw will use (FastMCP, `@mcp.tool` decorator, Streamable HTTP for remote servers, STDIO for local tools) is fully current and correct. One transport substitution to remember: wherever the course shows `transport="sse"`, replace with `transport="http"` in any Agent Improve implementation.

---

## 60. Internal RAG Tools vs MCP Tools — The Knowledge Retrieval Architecture Decision

*Source: Direct discussion during Course 4 Module 1, resolving a genuine architectural gap not previously captured explicitly.*

### The Core Distinction

```
MCP Tool (external)     = exposed to OUTSIDE clients across a process/network boundary
                          any agent or system can discover and call it
                          e.g. "fetch live SAP process data", "query complaint rate API"

Internal @tool          = private to THIS agent's own reasoning loop
                          LLM can invoke it within its TAO cycle
                          stays inside the same process, never exposed externally
                          e.g. "retrieve_methodology when I need theoretical grounding"
```

The eBook knowledge index (`improve_knowledge_index`) and case index (`improve_case_index`) are **private reasoning support** for the coaching LLM. They should NOT be exposed as MCP endpoints — they are internal `@tool` decorated functions the phase executor invokes within its own reasoning loop.

---

### What Agent Improve Currently Does — The Gap

Retrieval is **automatic and unconditional** — it fires on every turn regardless of whether it is needed. The LLM has no agency over when or what to retrieve.

```
Belt sends message → retrieve() fires unconditionally → chunks injected → LLM responds
```

Problems:
- Same retrieval every turn regardless of actual need
- No phase filter applied (Gap 21 — `phase_relevance` field unused)
- LLM passively receives whatever the pipeline returns
- Single retrieval step — no retry if first result is insufficient
- No distinction between "I need methodology grounding" vs "I need precedent from a past case"

---

### What Internal Tools Give Instead

The LLM **reasons about when it needs knowledge** — the TAO loop applied to retrieval:

```
Belt says: "I think the root cause is agent training gaps"
        ↓
LLM THINKS: "I need to validate this against Six Sigma root cause
             validation standards before asking the Belt to confirm"
        ↓
LLM CALLS: retrieve_methodology(query="root cause validation
           techniques DMAIC Analyse phase", phase="analyse")
        ↓
Tool returns filtered, relevant eBook chunks
        ↓
LLM reasons with theoretical grounding
        ↓
Responds with methodology-backed coaching
```

---

### The Two Internal Tools

```python
from langchain_core.tools import tool

@tool
def retrieve_methodology(query: str, phase: str = None) -> str:
    """Retrieve Six Sigma and DMAIC methodology from the Black Belt
    knowledge base. Use when you need theoretical grounding for a
    coaching decision, root cause validation, or methodology guidance.
    Specify phase to filter results (define/measure/analyse/improve/control)."""

    filters = f"phase_relevance eq '{phase}'" if phase else None
    results = search_client.search(
        search_text=query,
        filter=filters,
        top=3
    )
    return "\n\n".join([r["content"] for r in results])

@tool
def retrieve_similar_cases(query: str, current_phase: str) -> str:
    """Retrieve similar completed DMAIC cases from the case index.
    Use when you need to ground a coaching recommendation in real
    precedent rather than theory alone. Only returns completed cases."""

    results = case_search_client.search(
        search_text=query,
        filter=f"status eq 'completed'",
        order_by=["created_at desc"],
        top=2
    )
    return "\n\n".join([r["content"] for r in results])
```

**Note:** both tools also resolve Gap 21 (metadata filters unused) naturally — the LLM passes `phase` context when it calls `retrieve_methodology`, and the `status eq 'completed'` and `order_by` filters are built into the tool definition. Correct filtering happens because the LLM has agency over the call, not despite it lacking agency.

---

### Option C — Hybrid Planner + Reactive Tool (Confirmed Best for DMAIC)

Three options were considered:

**Option A — Tool available, LLM decides reactively (pure ReAct)**
Simpler, flexible, works well for unpredictable questions. But no audit trail of which retrieval decisions were planned vs reactive — a concern for DMAIC's quality governance requirements.

**Option B — Phase Planner explicitly plans all retrieval steps**
Fully auditable, predictable, fits Section 44's explicit-planner discipline. But too rigid — DMAIC coaching conversations are genuinely unpredictable, and forcing the planner to anticipate every retrieval need upfront produces brittle over-specified plans.

**Option C — Hybrid (selected):** Planner plans routine/predictable retrievals; tool available for ad-hoc reasoning needs that emerge mid-conversation.

```
Phase Planner output example (structured JSON — Section 17):
{
  "next_action": "coach_root_cause_validation",
  "planned_retrievals": [
    {"tool": "retrieve_methodology", "query": "root cause validation techniques", "phase": "analyse"},
    {"tool": "retrieve_similar_cases", "query": "call centre complaint rate root cause"}
  ],
  "reactive_tools_available": ["retrieve_methodology", "retrieve_similar_cases"],
  "focus_field": "root_cause_statement"
}
```

**Why C is the right fit for DMAIC specifically:**

DMAIC has known structure — the planner *can* anticipate that an Analyse phase coaching turn will likely need methodology retrieval before asking the Belt to confirm a root cause. That is plannable. But the Belt's actual answer might surface something unexpected — an unusual process constraint, a domain-specific term — that the planner could not have anticipated, and the tool needs to be available reactively for the executor to reach for it in that moment.

```
Planned retrievals     → Predictable, high-confidence needs
                          "we are entering root cause validation — retrieve methodology"
                          Appear in step_log as planned actions (Section 18 audit trail)

Reactive tool calls    → Emergent, unpredictable needs
                          "Belt mentioned something I need to ground in methodology"
                          Also logged in step_log but tagged as reactive
                          Both remain fully auditable — the distinction is planning origin
```

---

### How This Changes the Phase Executor Architecture

```python
# Phase Executor — Analyse phase example
phase_tools = [
    retrieve_methodology,       # internal RAG — methodology grounding
    retrieve_similar_cases,     # internal RAG — precedent grounding
    extract_analyse_fields,     # extraction
    check_completeness,         # completeness scoring
    # debate_subgraph_tool,     # future — root cause debate (Section 22)
]

executor = create_agent(
    model=get_llm("operational-premium"),   # gpt-4o for reasoning
    tools=phase_tools,
    system_prompt=black_belt_coach_prompt,
    checkpointer=checkpointer,
    store=store
)
```

The executor now has **four distinct capabilities** available in its TAO loop per turn:
1. Plan-driven methodology retrieval (from Phase Planner's `planned_retrievals`)
2. Reactive methodology retrieval (when the Belt's answer demands it)
3. Field extraction (after the coaching response)
4. Completeness check (feeds back to planner)

---

### Comparison Table — Current vs Target

| Aspect | Current | Target (Option C) |
|---|---|---|
| When retrieval fires | Every turn, unconditional | Planned + reactive, LLM-decided |
| Query formulation | Fixed pipeline query | LLM formulates the specific query needed |
| Phase filter | Never applied (Gap 21) | Applied by the tool definition + LLM passes phase |
| Number of retrieval hops | One | Multiple if first result insufficient (TAO loop) |
| Methodology vs precedent | Combined in one index query | Two distinct tools for two distinct needs |
| Audit trail | No retrieval decision record | step_log captures planned vs reactive retrievals |
| Gap 21 resolution | Requires explicit filter addition | Resolved naturally — LLM passes phase context |

---

### What Stays as MCP (For Reference — Section 57 Confirmed This Boundary)

```
Internal @tool (private, same process):
  retrieve_methodology        ← reasoning support, never external
  retrieve_similar_cases      ← reasoning support, never external
  extract_analyse_fields      ← internal computation
  check_completeness          ← internal scoring

MCP Tool (external, network-accessible):
  get_sap_process_data()      ← crosses a system boundary
  fetch_live_complaint_rate() ← real-time external data
  query_azure_devops_metrics()← external system
```

The eBook and case index retrieval stays internal. Only tools that cross a real system boundary (SAP, live KPIs, external APIs) belong on the MCP layer.

### Gap Register Update
**Gap 21 is now further resolved.** The internal tool pattern naturally applies `phase_relevance` and `status` filters as part of the tool definition rather than requiring a global filter change to the retrieval pipeline. The residual Gap 21 work (updating the unconditional pipeline for any remaining non-tool-based retrievals) is smaller than originally scoped.

---

## 61. MCP Resources — URI-Addressable Read-Only Knowledge Layer

*Source: Edureka Course 4 Module 1, "Consuming MCP Resources" demonstration transcript, verified against official MCP specification primitives.*

### The Core Distinction — Confirmed Correct From the Course

> "Resources are not tools. Tools do actions, resources return data."

```
MCP Tool      → agent CALLS it, something HAPPENS
                bidirectional — input in, result out
                e.g. calculate_sigma(), fetch_sap_data()

MCP Resource  → agent READS it, nothing changes in the world
                read-only — URI in, content out
                e.g. ebook://chapter/analyse-phase
```

---

### URI Addressing — The Defining Feature

Every resource has an **address** that communicates meaning:

```
library://catalog                    → full library index
library://book/001                   → one specific book
library://authors/sara-chin          → one specific author
file://documents/user-guide.txt      → one specific document
```

This enables **navigation** — following URI patterns to explore a knowledge structure, not just calling individual functions. The agent can follow references: fetch a root cause chapter → reference the fishbone tool → cross-reference similar cases.

---

### Three Access Patterns

**1. Direct fetch by known URI:**
```python
content = await client.read_resource("ebook://dmaic/analyse/root-cause-analysis")
```

**2. Discovery — explore what exists:**
```python
all_resources = await client.get_resources("ebook")
# Returns list of all URIs the server exposes
# Agent can discover structure without prior knowledge
```

**3. Bulk load for LLM context (upfront strategy):**
```python
context = ""
for uri in all_resource_uris:
    resource = await client.read_resource(uri)
    context += f"URI: {uri}\n{resource.content}\n\n"
# Pass entire context to LLM as background knowledge
```

**Upfront vs On-Demand — which fits Agent Improve:**
The demo uses upfront bulk load (load everything before the conversation). For Agent Improve this is the wrong pattern — the eBook is large and not all chapters are relevant to every coaching turn. Loading everything upfront wastes context window space, directly conflicting with Gaps 19 and 22 (context window management, context orchestration layer). The on-demand retrieval pattern from Section 60 (`retrieve_methodology` as an internal tool the LLM calls when needed) remains the correct approach.

---

### Tools vs Resources — The Exact Boundary for Agent Improve

```
MCP Tool (action, bidirectional):
  get_sap_complaint_rate(period)      → calls SAP, returns live data
  calculate_sigma(defects, opps)      → computation, returns result
  fetch_azure_devops_metrics(case_id) → external API call

MCP Resource (read-only, URI-addressed):
  "ebook://dmaic/analyse/root-cause-analysis"  → eBook chapter content
  "ebook://tools/fishbone-diagram"             → fishbone methodology
  "ebook://tools/5-why"                        → 5 Why methodology
  "case://completed/call-centre/complaint-rate" → similar past cases summary
  "template://coaching/measure"                → coaching prompt template
```

The eBook content and case documents are Resources — static knowledge the agent navigates. SAP data and live KPIs are Tools — actions that cross real system boundaries.

---

### How This Evolves Agent Improve's Knowledge Architecture

**Current state:** `improve_knowledge_index` queried via Azure AI Search vector similarity. The agent submits a query string, gets back the most similar chunks. This is a tool-pattern (action with input/output), not a resource-pattern.

**What Resources add:** specific knowledge assets become addressable — the agent can navigate the knowledge structure rather than just running a similarity query and hoping the right chunks surface.

```
Current (similarity query):
  retrieve_methodology("root cause validation")
  → Azure AI Search returns top-k similar chunks
  → agent uses whatever came back

Future (URI-addressed resource):
  read_resource("ebook://dmaic/analyse/root-cause-analysis")
  → returns the specific chapter reliably, every time
  → agent can then follow:
    read_resource("ebook://tools/fishbone-diagram")
    read_resource("ebook://tools/5-why")
  → navigating a knowledge structure, not just sampling from it
```

**Both patterns can coexist in Agent Improve:**
- Similarity search (Section 60's `retrieve_methodology` tool) for broad queries when the right chapter is not known in advance
- URI-addressed resource access for specific, known methodology references when the agent knows exactly what it needs

---

### Traceability — Why the URI Pattern Matters for DMAIC Specifically

The `ai_client.py` demo instructs the LLM to cite which URIs were used in its answer. This is directly relevant to DMAIC's audit requirements:

```
Current coaching response:
  "According to Six Sigma methodology, root causes should be validated
   with hypothesis testing..."
  → no traceability — where did this come from?

With URI-cited resources:
  "Based on ebook://dmaic/analyse/root-cause-analysis and
   ebook://tools/hypothesis-testing, root causes should be validated..."
  → full traceability — auditable, defensible, citable in a gate document
```

This closes a gap not previously formally numbered: **coaching responses are not currently traceable to specific source knowledge**. The URI citation pattern from Resource-based retrieval would make every coaching decision auditable back to its specific eBook reference — important for a quality system where a Belt's sponsor may question the methodology basis for a decision.

### Gap Register
**Gap 33 — No knowledge source traceability in coaching responses.** Currently the coaching LLM draws on retrieved chunks with no record of which specific sections of the Black Belt eBook grounded a coaching decision. URI-addressed MCP Resources with explicit citation instructions (as demonstrated in `ai_client.py`) would make every coaching response auditable back to its specific source. Lower priority than structural gaps 1-32, but directly relevant to DMAIC's quality system audit requirements. Implement alongside the MCP server build for Agent Improve.

---

## 62. MCP Server Ecosystem — Build Your Own vs Connect to Existing Servers

*Source: Verified against Microsoft Learn official Azure MCP Server documentation (learn.microsoft.com/azure/developer/azure-mcp-server, updated June 23, 2026), the official Microsoft MCP GitHub repository (github.com/microsoft/mcp), and multiple corroborating sources. This is one of the most directly relevant sections for AgentLean's actual production architecture.*

### The Two Relationships With MCP Servers — Confirmed

Your understanding is precisely correct. There are two fundamentally different relationships:

**Type 1 — You build your own MCP server**
You write server code using FastMCP (Section 59), define `@mcp.tool` and `@mcp.resource` decorators, and deploy it for your own domain-specific tools and data. This is what Module 1 has been teaching.

**Type 2 — You connect to existing third-party MCP servers**
These already exist, are maintained by their providers, and expose their capabilities through the MCP standard. Your agent just connects as a client — no server code to write.

```python
# Connect to Microsoft's Azure MCP Server — no server code needed
from mcp import ClientSession, StdioServerParameters

# Azure MCP Server available as a package
# pip install azure-mcp
# Exposes 40+ Azure service tools automatically
```

---

### What Actually Exists — Confirmed Third-Party MCP Servers

**Microsoft's Official Azure MCP Server** — implements the Model Context Protocol, making it compatible with MCP clients such as GitHub Copilot agent mode, the OpenAI Agents SDK, and Semantic Kernel. Supercharges agents with Azure context across 40+ different Azure services. Confirmed generally available.

The official Microsoft MCP GitHub repository contains multiple distinct servers including: All Azure MCP tools in a single server; a Model Context Protocol server for Microsoft Foundry providing tools for models, knowledge, evaluation; Azure Resource Graph tools; Azure DevOps tools; Azure Kubernetes Service tools; Microsoft Sentinel data exploration tools; SQL database tools (connecting to any SQL database from on-premises to Azure to Microsoft Fabric); Microsoft Teams management via Graph API; and a Microsoft 365 Agents Toolkit MCP Server.

**Security model confirmed:** uses Azure user credentials or managed identity; access secured through Azure Role-Based Access Control (RBAC). Tools that handle sensitive data require user consent before execution through a security mechanism called elicitation.

---

### Why This Is Directly Relevant to AgentLean

This changes the architecture picture significantly. AgentLean does not need to build custom MCP server integrations for the Azure services it already uses — **Microsoft has already built those servers**.

```
What was previously assumed for AgentLean (before this finding):
  "Build a custom MCP server for Azure Blob Storage access"
  "Build a custom MCP server for Azure AI Search"
  "Build a custom MCP server for Azure DevOps"

What is actually available today (confirmed):
  Azure MCP Server → already exposes Azure Blob Storage, Azure AI Search,
                     Azure DevOps, and 40+ other Azure services as MCP tools
                     Connect with your Entra ID credentials, use immediately
```

---

### The AgentLean MCP Architecture — Revised

With confirmed third-party server availability, the correct architecture is:

```
AgentLean Agent (MCP Client)
        ↓ connects to
        ├── Azure MCP Server (Microsoft-built, already exists)
        │     Tools available immediately:
        │     - Azure Blob Storage (case documents, state blobs)
        │     - Azure AI Search (improve_knowledge_index, improve_case_index)
        │     - Azure DevOps (future — linking DMAIC cases to work items)
        │     - Azure Resource Graph (monitoring, infrastructure)
        │
        ├── AgentLean Custom MCP Server (you build this)
        │     Domain-specific tools NOT in Azure's server:
        │     - calculate_sigma(defects, opportunities)
        │     - fetch_complaint_rate(case_id, period)
        │     - validate_smart_goal(goal_statement)
        │     - get_process_baseline(case_id)
        │
        └── Internal @tool functions (NOT MCP — Section 60)
              Private to agent's reasoning loop:
              - retrieve_methodology (internal RAG)
              - retrieve_similar_cases (internal RAG)
              - extract_fields, check_completeness
```

**The key insight:** the boundary between "use Azure MCP Server" vs "build your own" is:
- **Azure infrastructure tools** → use Microsoft's Azure MCP Server
- **DMAIC domain logic** → build your own AgentLean MCP Server
- **Internal reasoning support** → internal `@tool` functions, not MCP at all (Section 60)

---

### Security Consideration — Confirmed Important for Production

MCP clients can invoke operations based on the user's Azure RBAC permissions. Autonomous or misconfigured clients may perform destructive actions. You should review and apply least-privilege RBAC roles and implement safeguards before deployment.

This is a real production concern for AgentLean: when an AI agent connects to Azure MCP Server with Azure RBAC credentials, it could theoretically call destructive operations (delete a blob, modify a resource) if not properly scoped. **The Agent Improve phase subagents should connect to Azure MCP Server with read-only RBAC roles** for data retrieval use cases (reading `improve_knowledge_index`, reading case blobs) — write operations should remain in the application layer with explicit human approval gates (Section 53's HITL, Gap 2), not exposed through an autonomous MCP tool call.

---

### The Broader Third-Party MCP Server Ecosystem

Beyond Microsoft, the broader MCP server ecosystem is large and growing. Connecting to any of these requires only writing a client — no server code. Relevant examples for future AgentLean consideration:

| Provider | MCP Server | Relevance to AgentLean |
|---|---|---|
| Microsoft | Azure MCP Server | Direct — all Azure infrastructure |
| Microsoft | Azure DevOps MCP | Future — link DMAIC cases to work items |
| Microsoft | Microsoft 365 / Teams | Future — multi-user notifications for Belt gate reviews |
| Generic | SQL Database MCP | Future — connect to on-premise process databases |
| Generic | Sentinel MCP | Future — security/compliance monitoring |

The practical implication: **AgentLean's custom MCP server should be deliberately scoped to only what does not already exist in a maintained third-party server** — avoid duplicating what Microsoft has already built and maintains.

### Gap Register
No new gap number — this section resolves and refines an existing open question from Sections 39 and 60. The MCP architecture for AgentLean is now more precisely defined: Azure MCP Server handles Azure infrastructure access, a custom AgentLean MCP Server handles DMAIC domain logic, and internal `@tool` functions handle private reasoning support. This distinction should be used directly in the DMAIC redraw.

---

## 63. AgentLean MCP Server — Scope and Design Decision

*Source: Direct discussion, synthesising Sections 59-62. This section captures the confirmed architectural decision for what the AgentLean MCP server actually is and does.*

### The Confirmed Scope

A single AgentLean MCP server exposes two categories of tools — both are read operations against existing indexes, returning structured JSON the LLM uses when reasoning:

**Category 1 — Knowledge retrieval (improve_knowledge_index)**
When a phase subagent is reasoning about a complex coaching question and needs theoretical grounding from the Black Belt eBook:

```python
@mcp.tool
def search_knowledge(query: str, phase: str = None) -> dict:
    """Search the Black Belt knowledge base for DMAIC methodology,
    Six Sigma tools, and coaching guidance. Use when reasoning about
    a complex coaching decision or validating a methodology approach.
    Filter by phase (define/measure/analyse/improve/control) for precision."""

    filter_expr = f"phase_relevance eq '{phase}'" if phase else None
    results = knowledge_search_client.search(
        search_text=query,
        filter=filter_expr,
        top=3
    )
    return {
        "results": [
            {
                "content": r["content"],
                "source": r["source_file"],
                "page": r["page_number"],
                "phase_relevance": r["phase_relevance"]
            }
            for r in results
        ],
        "query_used": query,
        "phase_filter": phase
    }
```

**Category 2 — Case reference retrieval (improve_case_index)**
When a phase subagent needs to reference similar completed cases to ground a coaching recommendation in real precedent:

```python
@mcp.tool
def search_cases(query: str, current_phase: str) -> dict:
    """Search completed DMAIC cases for similar problems, root causes,
    and improvement approaches. Use when grounding a coaching recommendation
    in real-world precedent rather than theory alone."""

    results = case_search_client.search(
        search_text=query,
        filter="status eq 'completed'",
        order_by=["created_at desc"],
        top=2
    )
    return {
        "cases": [
            {
                "case_id": r["case_id"],
                "phase_summary": r.get(f"phase_summary_{current_phase}_phase", ""),
                "belt_level": r["belt_level"],
                "department": r["department"]
            }
            for r in results
        ],
        "query_used": query
    }
```

---

### Why the Return Type Is Structured JSON — Not a String

Both tools return **structured JSON dicts**, not raw text strings. This is deliberate and aligns with Section 44's typed-boundary-contract principle:

```
Current approach (string return):
  return "\n\n".join([r["content"] for r in results])
  → LLM gets a blob of text with no structure
  → Cannot reliably distinguish content from metadata

Better approach (structured JSON return):
  return {"results": [{"content": ..., "source": ..., "page": ...}]}
  → LLM sees structured data with clear field names
  → Source traceability is automatic (Gap 33) — "source" field always present
  → Phase filter applied and returned so LLM knows what was used
  → Directly auditable — step_log can record exactly what was retrieved
```

---

### The Server Itself — Minimal, STDIO Transport for Local Use

For Agent Resolve and Agent Improve running locally alongside the FastAPI server, STDIO transport is correct — no network hop needed, client spawns the server as a subprocess:

```python
from fastmcp import FastMCP
from azure.search.documents import SearchClient
from azure.core.credentials import AzureKeyCredential

mcp = FastMCP("agentlean-knowledge")

knowledge_search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name="improve_knowledge_index",
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

case_search_client = SearchClient(
    endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
    index_name="improve_case_index",
    credential=AzureKeyCredential(os.getenv("AZURE_SEARCH_API_KEY"))
)

@mcp.tool
def search_knowledge(query: str, phase: str = None) -> dict:
    """..."""
    # implementation above

@mcp.tool
def search_cases(query: str, current_phase: str) -> dict:
    """..."""
    # implementation above

if __name__ == "__main__":
    mcp.run()  # STDIO — agent spawns this as a subprocess
```

---

### How All Three Agents Use This

The same MCP server serves all three AgentLean agents — each connects as a client:

```
Agent Resolve (8D)
  → search_knowledge(query="containment actions immediate response", phase=None)
  → search_cases(query="manufacturing defect rate 8D", current_phase="d3")

Agent Improve (DMAIC)
  → search_knowledge(query="root cause validation hypothesis testing", phase="analyse")
  → search_cases(query="call centre complaint rate sigma improvement", current_phase="analyse")

Agent Flow (VSM) — future
  → search_knowledge(query="value stream mapping waste identification", phase=None)
  → search_cases(query="process flow takt time improvement", current_phase=None)
```

One server, three clients, zero duplication of the Azure AI Search integration code.

---

### What Stays Outside the MCP Server

The MCP server is deliberately minimal — read-only retrieval only. Everything else stays where it is:

```
In the MCP server:
  search_knowledge()     ← read from improve_knowledge_index
  search_cases()         ← read from improve_case_index

NOT in the MCP server (stays in application layer):
  State management       ← LangGraph Checkpointer + Store (Section 52)
  Field extraction       ← internal @tool decorated functions (Section 60)
  Gate logic             ← phase subgraph nodes
  Blob state read/write  ← direct Azure SDK (until migrated to LangGraph Store)
  Domain calculations    ← SigmaCalculator, FishboneBuilder as local @tools
  Agent-to-agent routing ← LangGraph State, never MCP (Section 57)
```

---

### The Full AgentLean Tool Architecture — Confirmed

```
AgentLean Phase Executor (e.g. Analyse Subagent)
        │
        ├── Internal @tool functions (private, same process)
        │     retrieve_methodology()    ← wraps MCP search_knowledge call
        │     retrieve_similar_cases()  ← wraps MCP search_cases call
        │     extract_fields()          ← local computation
        │     check_completeness()      ← local computation
        │
        └── MCP Client → AgentLean MCP Server
                              │
                              ├── search_knowledge() → improve_knowledge_index
                              └── search_cases()     → improve_case_index
```

The internal `@tool` functions from Section 60 are thin wrappers around the MCP tools — they add phase context, handle the TAO loop retry logic, and format the result for the coaching prompt. The MCP server handles only the raw Azure AI Search calls and JSON formatting.

### Gap Register
No new gap number. This section resolves the architectural open question from Sections 39, 60, and 62 by defining the exact scope of the AgentLean MCP server. Ready to implement after the DMAIC redraw establishes the full graph structure this server will serve.

---

## 64. MCP-Based Agent Architecture — Production Design Principles

*Source: Edureka Course 4 practice assessment review summary, July 2026. This is the most production-mature MCP architecture document in the course — several concepts here are sharper and more specific than anything in Sections 57-63 and should take precedence where they conflict or extend those sections.*

### 1. Core Value Proposition — N×M to N+M

> "MCP replaces N×M direct integrations (N agents × M services) with N+M — agents learn one protocol, servers handle translation to underlying services."

For AgentLean specifically:

```
Without MCP (current state):
  Agent Resolve  × (knowledge_index + case_index + blob) = 3 integrations
  Agent Improve  × (knowledge_index + case_index + blob) = 3 integrations
  Agent Flow     × (knowledge_index + case_index + blob) = 3 integrations
  Total: 9 separate integration code paths to maintain

With MCP:
  3 agents + 1 MCP server = 4 things to maintain
  Each agent learns one protocol once
  The MCP server handles all Azure AI Search integration
```

A central registry is not required at runtime — the supervisor maintains persistent connections established at startup and routes from an in-memory tool registry.

---

### 2. Three-Layer Topology — Confirmed and Sharpened

| Layer | Component | Responsibility |
|---|---|---|
| 1 | LangGraph Supervisor | Context-driven routing, tool registry, failure handling |
| 2 | Phase Subgraphs | Compiled StateGraphs, reasoning logic, MCP invocation |
| 3 | MCP Servers | **Stateless** domain servers, tool execution, resource serving |

**Critical principle confirmed and now made explicit:**
> "MCP servers are stateless. AgentState in LangGraph owns session continuity. Servers receive a request, return a response, done."

This resolves a potential confusion from earlier sections — MCP servers do NOT hold any session state between calls. Every tool call is independent. The LangGraph Checkpointer + Store (Section 52) owns everything that needs to persist. This is a clean separation that must be respected in implementation.

---

### 3. Server Naming Convention — Hierarchical Dot-Notation

**New, not previously in this document.** Use hierarchical dot-notation namespacing per domain:

```
retrieval-server.hybridSearch
retrieval-server.getMetadata
audit-server.logDecision
methodology-server.getPhaseInstructions
document-server.getPreview
```

**Why this matters:** disambiguates tool origin when the supervisor reasons over a unified registry spanning multiple servers. Prevents collision when two servers expose similarly named tools.

Applied to AgentLean:

```
knowledge-server.searchMethodology
knowledge-server.getMetadata
case-server.searchSimilarCases
case-server.getPhaseDetail
audit-server.logGateDecision
audit-server.logCoachingTurn
```

---

### 4. Tool vs Resource Distinction — Sharpened With Invocation Pattern

| Primitive | Invoked By | Pattern | Use Case |
|---|---|---|---|
| Tools | Model (during reasoning) | `tools/call` | Actions, computations, writes |
| Resources | Host/supervisor (before reasoning) | `resources/read` + URI | Context injection, document retrieval |

**New precision not previously captured:** Resources are invoked by the **host/supervisor before reasoning begins** — not by the LLM mid-reasoning. This is architecturally different from Section 61's framing.

```
Correct pattern:
  Supervisor/Phase Planner → reads resources BEFORE handing to LLM
  LLM → calls tools MID-REASONING when it needs to act or retrieve

Incorrect pattern:
  LLM calls resources mid-reasoning (that's what tools are for)
```

Resources are URI-addressed and stateless — multiple subgraphs can retrieve the same resource independently without conflict. No coordination overhead between agents.

---

### 5. Two-Stage Retrieval Pattern — New, Critical for Agent Improve

**Design contract: No tool or resource returns more than 2–4K tokens.**

This is a hard production rule, not a guideline. It directly addresses Gap 22's context window management concern.

**Stage 1 — Metadata scan:**
```python
# Call: knowledge-server.getMetadata
# Returns: URI, title, type, 2-3 sentence preview per candidate
# Cost: few hundred tokens regardless of candidate volume
# Action: subgraph scores relevance against descriptors

metadata_results = await mcp_client.call_tool(
    "knowledge-server.getMetadata",
    {"query": "root cause validation", "phase": "analyse"}
)
# Returns lightweight previews, not full content
# Subgraph decides which URIs pass the relevance threshold
```

**Stage 2 — Targeted fetch:**
```python
# Only fetch URIs that passed Stage 1 relevance scoring
# Server enforces token cap, chunks if necessary
for uri in relevant_uris:
    content = await mcp_client.read_resource(uri)
    # Only relevant content enters context window
```

**Multi-agent differentiation:** Each phase subgraph issues its own Stage 1 query with parameters reflecting its specific reasoning need. Define phase needs broad coverage; Analyse phase needs precise depth. **Relevance scoring is subgraph-local — no coordination overhead between agents.**

**Critical implementation note:**
> "Preview quality determines retrieval effectiveness. Poor previews cause relevant documents to fail the threshold. Preview generation is a first-class server implementation concern."

This means the MCP server's metadata generation for Stage 1 is as important as the retrieval itself. Invest in preview quality before optimising Stage 2.

---

### 6. Structured Error Schema — Shared Infrastructure

**New, not previously captured.** Error handling is shared infrastructure, not per-team convention.

```python
class MCPError(BaseModel):
    error_code: str          # MCP standard code
    message: str             # Human-readable description
    error_class: str         # "transient" | "permanent"
    affected_identifier: str # Tool or resource URI that failed
    retry_recommendation: str # "immediate" | "backoff" | "do-not-retry"
    fallback_hint: str | None # Optional alternative tool/resource
    data: dict | None        # Opaque payload for logs ONLY
                             # NEVER used for routing decisions
```

**Critical enforcement rule:**
> "The data payload field is where inconsistency accumulates over time. Keep it opaque to the supervisor. Routing logic stays clean; diagnostic richness stays in logs."

All AgentLean MCP servers import the same shared error library. Deviation fails at integration validation, not in production. This is exactly the typed-boundary-contract discipline from Section 44, applied to error responses.

---

### 7. Failure Isolation and Recovery — Three-Tier Response

**Isolation guarantee:** Server failures do not cascade. A retrieval server outage does not affect the audit server.

**Three-tier failure response:**
```
1. Detection     → structured error returned immediately on failed tool call
                   no timeout cascade

2. Classification → supervisor determines: critical-path or non-critical?

3. Response:
   Critical path  → failover to secondary server instance
                    MUST be pre-connected (warm), not spun up on demand
   Non-critical   → queue for retry, workflow continues unblocked
   (e.g. audit logging)
```

**Registry soft-invalidation:** Repeated failures from a server pause routing to it until health check confirms recovery. No manual intervention for transient outages.

**Deployment constraint:**
> "For time-sensitive workflows, failover servers must be warm (active-active), not cold (active-passive)."

For AgentLean during coaching sessions (a Belt is waiting), the knowledge retrieval server is critical-path. A cold failover would cause unacceptable latency. Warm standby is required for production.

---

### 8. What MCP Solves vs What It Does Not — Definitively Stated

> "What MCP solves: Integration-boundary context loss — inconsistent interfaces and missing data at agent handoff points."

> "What MCP does not solve: Context loss from poor AgentState design. These are separate problems requiring separate solutions."

This is the cleanest single statement of the MCP/LangGraph boundary in this entire document. Print it on the wall for the refactor:

```
MCP handles:     integration boundaries
LangGraph handles: reasoning continuity

Do not conflate the two layers.
```

---

### 9. Implementation Prerequisites — Before Any MCP Server Goes to Production

From the assessment's implementation commitments — these must be completed before implementation begins:

- [ ] Server naming convention specification (dot-notation, Section 64.3 above)
- [ ] Fallback routing logic specification
- [ ] Pilot scope definition (prevent scope creep)
- [ ] Error schema shared library and validation gate (Section 64.6 above)
- [ ] Preview generation quality standard for retrieval server (Section 64.5 above)

---

### 10. Key Design Principles — Carry Forward Into DMAIC Redraw

These eleven principles are the production-grade summary of everything learned in Sections 57-64:

1. **Stateless servers, stateful orchestrator** — MCP servers own no session state; LangGraph AgentState does
2. **Token budget is a contract** — 2–4K per tool/resource response, enforced server-side
3. **Naming is a first-class concern** — hierarchical namespacing before any server goes to production
4. **Error schema is shared infrastructure** — not a per-team convention
5. **Preview quality determines retrieval quality** — invest in Stage 1 before optimising Stage 2
6. **Failover servers must be warm** — cold standby is insufficient for critical-path tools
7. **MCP handles integration boundaries; LangGraph handles reasoning continuity** — don't conflate
8. **Resources before reasoning, tools during reasoning** — host/supervisor reads resources, LLM calls tools
9. **No tool or resource returns more than 2–4K tokens** — hard contract, enforced server-side
10. **Two-stage retrieval** — metadata scan first, targeted fetch only for what passes threshold
11. **N+M not N×M** — one protocol per agent, one integration per service

### Gap Register
No new gap number — this section establishes the production architecture principles that all existing MCP-related gaps (Sections 59-63) should be evaluated against. The two-stage retrieval pattern (Section 64.5) is a direct, practical answer to Gap 22's context window management concern and should be implemented as part of that gap's resolution. The 2026-07-28 spec finding means all AgentLean MCP implementation should wait for or target that spec — see Section 64.11 verification note.

### 11. Verification Against Current 2026 Standards

*Verified against seven independent sources, April-May 2026. Added after the original section was captured.*

**Confirmed correct:**
- N×M to N+M value proposition — confirmed verbatim across all sources
- Three-layer topology — confirmed as accurate application of Host/Client/Server model
- MCP servers are stateless — confirmed and now **stronger**: the 2026-07-28 release candidate makes statelessness a formal protocol-level guarantee, enabling plain round-robin load balancing without sticky sessions
- Tool vs Resource conceptual distinction — confirmed; tools have side effects, resources are read-only
- Structured error handling as shared infrastructure — confirmed as production best practice
- "MCP handles integration boundaries, LangGraph handles reasoning continuity" — confirmed as correct framing

**Requires precision correction:**

**Dot-notation naming (Section 64.3):** Not an official MCP standard — a sound AgentLean design convention, not a protocol requirement. Apply it internally but do not represent it as an MCP specification.

**Resources invoked "before reasoning" (Section 64.4):** Oversimplification. The protocol does not restrict when resources can be read — clients can read resources at any point during a session. The "host reads resources before handing to LLM" is a valid design pattern for context pre-loading, not a protocol rule.

**2–4K token budget (Section 64.5):** Not an MCP protocol requirement — a sound context-window management design decision for AgentLean. Enforce it as an internal contract, not a spec compliance requirement.

**Critical new finding — 2026-07-28 spec ships within weeks:**

The MCP 2026-07-28 release candidate is published and the final specification ships July 28, 2026 — within weeks of your current date. It contains breaking changes:
- Stateless protocol core (headline change — servers no longer need sticky sessions)
- Deprecation of Roots and Sampling primitives
- New Extensions framework, Tasks, and MCP Apps
- OAuth/OIDC hardening — MCP servers are OAuth Resource Servers consuming tokens from existing identity providers (Azure Entra ID), not issuing their own tokens

**Practical implication for AgentLean:** any AgentLean MCP server implementation should target the 2026-07-28 spec rather than the current 2025-11-25 spec. Building against 2025-11-25 now means an immediate migration within weeks of shipping. Wait for the July 28 final spec before writing production MCP server code — or at minimum, build with the release candidate draft in hand. This is exactly the verification Gap 27's `/verify-current-version` skill was designed to catch.

*Verified against seven independent sources, April-May 2026. Added after the original section was captured.*

**Confirmed correct:**
- N×M to N+M value proposition — confirmed verbatim across all sources
- Three-layer topology — confirmed as accurate application of Host/Client/Server model
- MCP servers are stateless — confirmed and now **stronger**: the 2026-07-28 release candidate makes statelessness a formal protocol-level guarantee, enabling plain round-robin load balancing without sticky sessions
- Tool vs Resource conceptual distinction — confirmed; tools have side effects, resources are read-only
- Structured error handling as shared infrastructure — confirmed as production best practice
- "MCP handles integration boundaries, LangGraph handles reasoning continuity" — confirmed as correct framing

**Requires precision correction:**

**Dot-notation naming (Section 64.3):** Not an official MCP standard — a sound AgentLean design convention, not a protocol requirement. Apply it internally but do not represent it as an MCP specification.

**Resources invoked "before reasoning" (Section 64.4):** Oversimplification. The protocol does not restrict when resources can be read — clients can read resources at any point during a session. The "host reads resources before handing to LLM" is a valid design pattern for context pre-loading, not a protocol rule. The LLM can also trigger resource reads mid-reasoning via tools.

**2–4K token budget (Section 64.5):** Not an MCP protocol requirement — a sound context-window management design decision for AgentLean. Enforce it as an internal contract, not as a spec compliance requirement.

**Critical new finding — 2026-07-28 spec ships within weeks:**

The MCP 2026-07-28 release candidate is published and the final specification ships July 28, 2026 — within weeks of your current date. It contains breaking changes:
- Stateless protocol core (headline change — servers no longer need sticky sessions)
- Deprecation of Roots and Sampling primitives
- New Extensions framework, Tasks, and MCP Apps
- OAuth/OIDC hardening — MCP servers are OAuth Resource Servers consuming tokens from existing identity providers (Azure Entra ID), not issuing their own tokens

**Practical implication for AgentLean:** any AgentLean MCP server implementation should target the 2026-07-28 spec rather than the current 2025-11-25 spec. Building against 2025-11-25 now means an immediate migration within weeks of shipping. Wait for the July 28 final spec before writing production MCP server code — or at minimum, build with the release candidate draft in hand. This is exactly the verification Gap 27's `/verify-current-version` skill was designed to catch.

---

## 65. MCP Server Caching — Tool List Caching and Result Caching

*Source: Verified against OpenAI Agents SDK documentation, production MCP deployment guides, and multiple current sources (February-April 2026). Directly answers the question: "is there memory on the MCP server when multiple agents ask the same questions?"*

### The Direct Answer

The MCP server itself has **no built-in memory between calls** — it is stateless by design (Section 64's confirmed principle). However two distinct caching mechanisms solve exactly this problem, at different layers:

---

### Layer 1 — Tool List Caching (Client-Side)

Every time an agent starts a new session, by default it sends a `tools/list` request to the MCP server to discover available tools. For a stable tool list this is wasteful — the tools never change, yet every query triggers a round trip.

```python
# Without caching — tools/list fires on every query (wasteful)
server = MCPServerStreamableHttp(
    name="agentlean-knowledge",
    params={"url": "http://localhost:8001/mcp"},
)

# With caching — tools/list fires ONCE, reused for all subsequent queries
server = MCPServerStreamableHttp(
    name="agentlean-knowledge",
    params={"url": "http://localhost:8001/mcp"},
    cache_tools_list=True,          # ← single parameter change
    max_retry_attempts=3,
    retry_backoff_seconds_base=2,
)
```

**Only the tool metadata is cached** (names, schemas, descriptions) — not the results of calling them. The tool logic still runs live on the server every time it is called. Invalidate with `server.invalidate_tools_cache()` if tool definitions change.

**Rule:** enable `cache_tools_list=True` for any stable MCP server. Disable only if tool definitions change frequently during a session (rare in practice).

---

### Layer 2 — Tool Result Caching (Server-Side, Directly Answers Your Question)

When multiple agents call the same tool with the same arguments — e.g. Agent Resolve and Agent Improve both call `search_knowledge(query="root cause analysis", phase="analyse")` within the same time window — without caching, both trigger a full Azure AI Search query. With result caching, the second call returns a stored result in milliseconds.

```python
from fastmcp import FastMCP
import hashlib
import json
from datetime import datetime, timedelta

mcp = FastMCP("agentlean-knowledge")

# Simple in-process cache — suitable for single-server STDIO deployment
_result_cache: dict = {}
CACHE_TTL_MINUTES = 30  # knowledge index content is stable

def _cache_key(tool_name: str, args: dict) -> str:
    return hashlib.md5(
        f"{tool_name}:{json.dumps(args, sort_keys=True)}".encode()
    ).hexdigest()

@mcp.tool
def search_knowledge(query: str, phase: str = None) -> dict:
    """Search the Black Belt knowledge base..."""
    key = _cache_key("search_knowledge", {"query": query, "phase": phase})
    
    # Check cache first
    if key in _result_cache:
        entry = _result_cache[key]
        if datetime.now() < entry["expires"]:
            return {**entry["result"], "cache_hit": True}
    
    # Cache miss — run the actual Azure AI Search query
    results = knowledge_search_client.search(
        search_text=query,
        filter=f"phase_relevance eq '{phase}'" if phase else None,
        top=3
    )
    
    result = {
        "results": [{"content": r["content"], "source": r["source_file"]} for r in results],
        "query_used": query,
        "cache_hit": False
    }
    
    # Store in cache with TTL
    _result_cache[key] = {
        "result": result,
        "expires": datetime.now() + timedelta(minutes=CACHE_TTL_MINUTES)
    }
    return result
```

**Cache only reads, never writes** — this is the confirmed rule from production deployments. Tools that write data (future SAP write-back tools, audit log tools) must never be cached since caching would suppress side effects.

---

### Three Caching Strategies by Infrastructure Stage

| Stage | Strategy | When to Use |
|---|---|---|
| Dev / STDIO single agent | In-process dict (above) | Zero infrastructure, works immediately |
| Production single server | File-based or in-process with TTL | Persistent across tool call restarts |
| Production multi-agent shared server | **Redis** | Multiple agents, multiple server instances, shared state |

Redis is the confirmed production standard for multi-agent scenarios: handles TTL expiration natively, supports atomic operations, scales horizontally, and prevents duplicate work across agents sharing the same MCP server.

```python
import redis
import json

redis_client = redis.Redis(host="localhost", port=6379, decode_responses=True)

@mcp.tool
def search_knowledge(query: str, phase: str = None) -> dict:
    """Search the Black Belt knowledge base..."""
    key = f"agentlean:knowledge:{hashlib.md5(f'{query}:{phase}'.encode()).hexdigest()}"
    
    cached = redis_client.get(key)
    if cached:
        return {**json.loads(cached), "cache_hit": True}
    
    result = run_azure_search(query, phase)
    redis_client.setex(key, 1800, json.dumps(result))  # 30 min TTL
    return {**result, "cache_hit": False}
```

---

### The Token Cost Context — Why This Matters

A production MCP deployment with five servers and 58 tools consumes over 55,000 tokens before the first user message. For Azure OpenAI (GPT-4o), uncached repeated queries across Agent Resolve and Agent Improve during the same time window compound cost quickly. Result caching of stable knowledge index queries can reduce response times by 80-95% for repetitive tool calls, and proportionally reduces Azure OpenAI token costs for any system prompt content that is re-sent with each turn.

---

### TTL Guidance for AgentLean's Two Tools

| Tool | Recommended TTL | Reasoning |
|---|---|---|
| `search_knowledge` | 24 hours | eBook content is static, never changes at runtime |
| `search_cases` | 30 minutes | Case index can receive new completed cases; shorter TTL keeps results fresh |

---

### What to Cache vs What Never to Cache

```
Cache reads:
  ✅ search_knowledge — static eBook content
  ✅ search_cases — semi-static case summaries
  ✅ getMetadata — Stage 1 retrieval previews (Section 64.5)

Never cache writes (future tools):
  ❌ log_gate_decision — side effect must fire every time
  ❌ update_case_status — write operation, caching suppresses the write
  ❌ Any tool that sends a notification or triggers an action
```

### Gap Register Note
No new gap number — this section provides the implementation pattern for tool result caching, which belongs in the AgentLean MCP server build alongside Section 63's tool definitions. The Redis pattern applies once all three agents are deployed and share a single HTTP MCP server. In-process dict caching is appropriate for the current STDIO single-agent development phase.

### Architecture Carry-Forward — Required for ARCHITECTURE_v2_DRAFT.md

When the architecture draft is written, the MCP Server layer must include the following as a non-functional requirement (not a graph node or state concern):

```
AgentLean MCP Server — Caching Requirements:

Client-side:
  cache_tools_list=True on all MCP server connections
  (prevents repeated tools/list round trips per session)

Server-side result caching:
  search_knowledge  → 24h TTL  (eBook content is static)
  search_cases      → 30min TTL (case index receives new entries)
  Any future write tool → never cached

Cache backend progression:
  Dev / STDIO single agent  → in-process dict with TTL
  Production / HTTP shared  → Redis (shared across all three agents)

Rule: cache reads, never writes
```

This is infrastructure specification, not graph architecture — it belongs in the MCP Server section of the architecture document, not in the LangGraph graph design section.

### No New Gap Number
This section does not introduce new scope — it resolves an ambiguity in how Gaps 22 and 23 relate to each other and clarifies that both reflection (Gap 23, RubricMiddleware) and consensus (Gap 22, debate subgraph) are required architectures, applied to different categories of decision, not competing alternatives to choose between. The three-prompt separation and ConstraintValidator pattern added above are the concrete implementation building blocks for Gap 23's gate quality evaluation.

---

## 66. Circuit Breaker, Context Recovery, and Safe Reopen — Completing the Failure Pipeline

*Source: Edureka Course 4 Module 2, "Retry Strategies, Back-off Techniques, and Failure Handling" transcript. Three concepts from the six-step failure pipeline not previously formally captured.*

### What Was Already in This Document

| Concept | Where Captured |
|---|---|
| Retry strategies + exponential backoff | Sections 51, 64, 65 |
| Error classification (transient/permanent) | Section 64 structured error schema |
| Graceful degradation + smart fallbacks | Sections 20, 51 |
| Human escalation | Section 53, Gap 2 |
| Validation checkpoints | Sections 42/54, 48 |
| Context preservation (checkpointing) | Sections 1, 44 |
| Compensating actions for rollback | Section 49 (Saga) |

---

### Three Concepts Not Previously Named

**1. Circuit Breaker — formally named**

Section 64 described this as "registry soft-invalidation: repeated failures from a server pause routing to it until health check confirms recovery." That is a circuit breaker. The formal definition:

```
CLOSED (normal)    → requests flow through normally
        ↓ failure threshold exceeded (e.g. 3 failures in 30 seconds)
OPEN (tripped)     → all requests to this component fail immediately
                     no retry attempts, no waiting
                     preserves system stability
        ↓ after reset timeout (e.g. 60 seconds)
HALF-OPEN (probe)  → one trial request allowed through
        ↓ succeeds?
CLOSED             → normal operation resumes
        ↓ fails?
OPEN               → stays open, reset timer restarts
```

For AgentLean, the circuit breaker applies at two levels:

```python
class CircuitBreaker:
    """Wraps any callable — MCP server call, Azure AI Search query, LLM call."""

    def __init__(self, failure_threshold=3, reset_timeout=60):
        self.failures = 0
        self.threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.state = "CLOSED"   # CLOSED | OPEN | HALF_OPEN
        self.last_failure_time = None

    def call(self, func, *args, **kwargs):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.reset_timeout:
                self.state = "HALF_OPEN"   # allow one probe
            else:
                raise CircuitOpenError("Circuit open — failing fast")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception as e:
            self._on_failure()
            raise

    def _on_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def _on_failure(self):
        self.failures += 1
        self.last_failure_time = time.time()
        if self.failures >= self.threshold:
            self.state = "OPEN"
```

Section 64's MCP error schema already has the connection point: `retry_recommendation: do-not-retry` is the signal to trip the circuit breaker rather than retrying. The circuit breaker is what acts on that signal at the infrastructure level.

---

**2. Context Recovery — preserve partial results mid-failure**

This is distinct from both checkpointing (automatic state snapshots between nodes) and Saga (undoing completed steps). Context recovery specifically means: *if an operation fails partway through, save whatever was successfully completed before raising the error*.

```python
async def extract_define_fields(state: DefineState, llm) -> dict:
    """Extract all five Define gate fields.
    Context recovery: save partial results if extraction fails mid-way."""

    partial_results = {}

    fields_to_extract = ["what", "why", "scope", "team", "how_goal"]

    for field in fields_to_extract:
        try:
            value = await extract_single_field(field, state, llm)
            partial_results[field] = value

        except Exception as e:
            # Context recovery — save what we have before failing
            await save_partial_to_blob(state["case_id"], partial_results)

            # Return partial state rather than losing everything
            return {
                "captured_fields": partial_results,
                "extraction_error": str(e),
                "extraction_incomplete": True,
                "last_successful_field": field
            }

    return {"captured_fields": partial_results, "extraction_incomplete": False}
```

Without context recovery, a failure on field 4 of 5 loses the first three extractions. With it, the next attempt resumes from where it failed rather than starting from scratch. This connects directly to the LangGraph checkpointer — partial state written to blob here will be picked up on resume.

---

**3. Safe Reopen — cautious resumption after circuit breaker trips**

When a circuit breaker moves from OPEN to HALF-OPEN, it allows exactly one probe request before deciding to reopen fully. This must be explicit:

```python
# Safe reopen — not "resume full traffic immediately"
# One probe request → success → reopen
# One probe request → failure → stay open, reset timer

if circuit_breaker.state == "HALF_OPEN":
    try:
        result = mcp_client.call_tool("search_knowledge", probe_query)
        circuit_breaker._on_success()   # fully reopen
        log_event("circuit_breaker_recovered", tool="search_knowledge")
    except Exception:
        circuit_breaker._on_failure()   # stay open
        log_event("circuit_breaker_probe_failed", tool="search_knowledge")
        raise CircuitOpenError("Probe failed — circuit remains open")
```

For AgentLean this matters specifically for the AgentLean MCP server and Azure AI Search — both are critical-path for coaching turns. A failed circuit probe should not silently succeed and immediately flood the recovering service with full traffic.

---

### The Complete Six-Step Failure Pipeline — Now Fully Captured

```
Step 1 — Error Classification
  transient | permanent
  Section 64 structured error schema

Step 2 — Context Recovery              ← new in this section
  save partial results before failing
  connect to LangGraph checkpointer for resume

Step 3 — Circuit Breaker               ← formally named in this section
  CLOSED → OPEN → HALF-OPEN → CLOSED
  Section 64's soft-invalidation now formally named

Step 4 — Safe Reopen                   ← new in this section
  one probe request before full traffic resumes

Step 5 — Graceful Degradation
  Section 20 fallback chains
  Section 51 run_with_fallback()

Step 6 — Smart Fallbacks
  alternative tools, models, or responses
  Section 20 Level 1 → Level 2 → Level 3 degradation
```

### The Complete Six-Step Failure Pipeline — Now Fully Captured

```
Step 1 — Error Classification
  transient | permanent
  Section 64 structured error schema

Step 2 — Context Recovery              ← new in this section
  save partial results before failing
  connect to LangGraph checkpointer for resume

Step 3 — Circuit Breaker               ← formally named in this section
  CLOSED → OPEN → HALF-OPEN → CLOSED
  Section 64's soft-invalidation now formally named

Step 4 — Safe Reopen                   ← new in this section
  one probe request before full traffic resumes

Step 5 — Graceful Degradation
  Section 20 fallback chains
  Section 51 run_with_fallback()

Step 6 — Smart Fallbacks
  alternative tools, models, or responses
  Section 20 Level 1 → Level 2 → Level 3 degradation
```

---

### Jitter and Per-Level Backoff Strategy Selection

*Source: Edureka Course 4 Module 2 self-healing demo code, verified against production retry pattern guidance.*

**Jitter** is a genuinely new addition to what was previously captured in Section 51's plain exponential backoff. It adds randomness to the retry delay to prevent the **thundering herd problem** — when multiple agents retry at exactly the same intervals, they all hit the recovering service simultaneously, which can prevent recovery rather than enabling it.

```python
def exponential_backoff(attempt: int, base: float = 1.0) -> float:
    return base * (2 ** attempt)   # 1s, 2s, 4s, 8s — predictable, synchronized

def jittered_backoff(attempt: int, base: float = 1.0) -> float:
    delay = base * (2 ** attempt)
    return delay + random.uniform(0, delay * 0.1)   # adds 0-10% random spread
    # multiple agents retrying at different moments — load distributed
```

**When to use which:**

| Scenario | Strategy | Reasoning |
|---|---|---|
| Single agent retrying a managed service (Azure OpenAI) | Exponential | Predictable intervals, no thundering herd risk |
| Multiple agents sharing the same resource (MCP server, cache) | Jittered | Randomises retry timing across agents, prevents synchronized storm |
| Local model or local cache | Jittered | Multiple phase subagraphs may fall back simultaneously |

The **per-level backoff strategy selection** is the design principle: the choice of backoff strategy depends on whether multiple agents could be retrying the same resource at the same time. A managed cloud service with its own load balancing can absorb synchronized retries; a shared local resource cannot.

---

### AgentLean-Specific Fallback Chain — Architecture Carry-Forward

```python
# Applied to Agent Improve's coaching turn failure handling

Level 1: Azure OpenAI gpt-4o (operational-premium deployment)
         exponential_backoff   ← managed service, predictable retries
         ↓ if rate-limited or unavailable

Level 2: Azure OpenAI gpt-4o-mini (operational-model deployment)
         exponential_backoff   ← same managed tier, same reasoning
         ↓ if also unavailable

Level 3: AgentLean MCP knowledge cache (cached response from Section 65)
         jittered_backoff      ← shared cache, multiple subagents may hit simultaneously
         ↓ if cache miss or unavailable

Level 4: Degraded mode         ← always succeeds, never a hard failure to the Belt
```

**Degraded mode for Agent Improve must never be a blank error.** The Belt is mid-project and needs continuity. The correct degraded response:

```python
def degraded_mode_response(state: AgentImproveState) -> str:
    phase = state["current_phase"]
    captured = state["captured_fields"]
    missing = get_missing_fields(state)

    return (
        f"I'm experiencing a temporary connection issue with my knowledge base. "
        f"Based on what we've captured so far in the {phase} phase "
        f"({len(captured)} of {len(captured) + len(missing)} fields complete), "
        f"I'd suggest we pause here and continue once the system recovers. "
        f"Your progress is saved and nothing has been lost."
    )
```

This is better than silence or a crash in every respect — the Belt knows what happened, knows their work is safe, and knows how to continue. The message uses actual state (`current_phase`, `captured_fields`) rather than a generic error, which maintains trust even during a degraded experience.

### Gap Register Note
No new gap number — jitter and per-level backoff selection are implementation refinements to the fallback chain already documented in Sections 20 and 51. The AgentLean-specific fallback chain above should be used as the architecture carry-forward for the ARCHITECTURE_v2_DRAFT.md reliability section.

---

## 67. Self-Healing Fallback Chain — Complete Reference Implementation

*Source: Edureka Course 4 Module 2 self-healing demonstration, complete code across all screenshots. Confirms and extends Sections 20, 51, and 66 with a single runnable reference.*

### What This Adds Beyond Section 66

Section 66 described the circuit breaker pattern conceptually and showed the state machine (CLOSED/OPEN/HALF-OPEN). This demo shows a **simplified two-state circuit breaker** (CLOSED/OPEN only — no HALF-OPEN probe) combined with a **structured audit log** across the entire fallback chain. Both are worth capturing precisely.

---

### The Simplified Circuit Breaker — Two States

The course demo uses CLOSED/OPEN without HALF-OPEN. This is a valid simplified implementation for cases where automatic recovery testing is not needed — the circuit stays open until manually reset or the process restarts:

```python
class CircuitBreaker:
    def __init__(self, threshold: int = 3):
        self.threshold = threshold
        self.failures = 0
        self.state = "CLOSED"   # CLOSED | OPEN (no HALF-OPEN in this implementation)

    def call(self, func, *args):
        if self.state == "OPEN":
            raise Exception("Circuit OPEN - Service blocked")

        try:
            result = func(*args)
            self.failures = 0   # reset on ANY success
            return result
        except Exception as e:
            self.failures += 1
            if self.failures >= self.threshold:
                self.state = "OPEN"
                print(f"Circuit OPEN after {self.failures} failures")
            raise e
```

**Two-state vs three-state trade-off:**

| | Two-State (CLOSED/OPEN) | Three-State (+ HALF-OPEN) |
|---|---|---|
| Complexity | Simple | Moderate |
| Auto-recovery | No — stays open until restart | Yes — probes for recovery |
| Use case | Short-lived processes, dev/test | Long-running production services |
| AgentLean fit | Dev and testing phase | Production MCP server |

For Agent Improve in production, the **three-state version from Section 66 is correct** — a long-running service must be able to recover without a restart. The two-state version is appropriate during development and testing.

---

### The Structured Audit Log — The Genuinely New Addition

Every service attempt — success or failure — appends to `self.log` as a tuple:

```python
# On success:
self.log.append((name, attempt+1, "success", None))

# On failure:
self.log.append((name, attempt+1, "failed", str(e)))

# On degraded mode:
self.log.append(("Degraded", 1, "fallback", None))
```

At the end of execution, the full log is printed:

```python
for service, attempt, status, reason in chain.log:
    print(f"Service : {service}")
    print(f"Attempt : {attempt}")
    print(f"Status  : {status}")
    if reason:
        print(f"Reason  : {reason}")
```

**Why this matters for Agent Improve:** this is exactly the `step_log` audit trail from Section 18, applied specifically to fallback chain execution. Every fallback decision becomes auditable — you can see which service was tried, which attempt it was, whether it succeeded, and why it failed if not. For a DMAIC quality system where coaching decisions need to be traceable, knowing that the Analyse phase coaching response came from the backup model rather than the primary model on attempt 2 is important context.

**Direct connection to Section 64's error schema:**

```python
# The log tuple maps exactly to Section 64's structured error schema
self.log.append((
    name,           # affected_identifier — which service
    attempt+1,      # attempt number
    "failed",       # status
    str(e)          # message — human-readable reason
))
```

---

### The `_try_service` Pattern — Retry Loop With Per-Attempt Logging

```python
def _try_service(self, service, query, name, backoff_fn, retries=None) -> str:
    retries = retries or self.max_retries

    for attempt in range(retries):
        try:
            result = service.call(query)
            self.log.append((name, attempt+1, "success", None))
            return result

        except Exception as e:
            self.log.append((name, attempt+1, "failed", str(e)))
            if attempt < retries - 1:
                wait = backoff_fn(attempt)
                time.sleep(wait)

    return None   # all attempts exhausted for this service → trigger next fallback level
```

**The `retries=None` defaulting to `self.max_retries`** allows per-level retry override — Level 3 (local model) passes `retries=1` explicitly, meaning it only tries once before going to degraded mode. This is a clean pattern: most fallback levels inherit the global retry count, but you can tighten it for the final tier.

---

### The `random.seed(1)` in `main()` — Teaching Artifact, Not Production Pattern

```python
random.seed(1)
```

This makes the demo deterministic — the same "random" failures occur every run. It is a teaching tool to produce consistent output in the video. **Never use `random.seed()` in production** — it defeats the purpose of probabilistic failure simulation and removes the randomness that jitter depends on.

---

### Complete Architecture Carry-Forward for Section 66

The four components now fully documented across Sections 66 and 67:

```
AgentLean Self-Healing Stack:

1. Jittered/Exponential Backoff (Section 66)
   → exponential for managed services
   → jittered for shared/local resources

2. Circuit Breaker (Sections 66, 67)
   → two-state (CLOSED/OPEN) for dev
   → three-state (+ HALF-OPEN) for production

3. Structured Fallback Chain (Sections 20, 66, 67)
   → Level 1: gpt-4o primary
   → Level 2: gpt-4o-mini backup
   → Level 3: cached MCP response
   → Level 4: degraded mode response (never a hard failure)

4. Audit Log (Sections 18, 64, 67)
   → every attempt logged: service, attempt#, status, reason
   → connects to step_log and Section 64 error schema
   → enables post-hoc analysis of which service served each coaching turn
```

### Gap Register Note
No new gap number — this section completes the self-healing implementation reference for Sections 20, 66. The audit log pattern (`self.log` appending per-attempt tuples) should be adopted in Agent Improve's fallback implementation and connected to the existing `step_log` field already in the state schema.

---

### Agent Improve Specific Implementation — Real Failure Conditions and Dual Circuit Breakers

*The demo uses artificial `fail_rate`. This section maps the pattern to Agent Improve's actual failure conditions and architecture.*

**Real failure conditions — not simulated:**

```python
import openai

# What actually triggers fallback in Agent Improve:
# HTTP 429  — Azure OpenAI rate limit hit
# HTTP 503  — Azure OpenAI service unavailable
# Timeout   — request takes > 30s, connection drops
# HTTP 400  — token limit exceeded (context overflow) — NOT a fallback case
# HTTP 404  — wrong deployment name in config
```

**The real implementation:**

```python
def call_llm_with_fallback(messages: list, state: dict) -> str:

    # Level 1 — Primary: gpt-4o operational-premium
    try:
        response = primary_client.chat.completions.create(
            model="operational-premium",
            messages=messages,
            timeout=30
        )
        log_attempt("operational-premium", 1, "success", None)
        return response.choices[0].message.content

    except openai.BadRequestError as e:
        if "context_length_exceeded" in str(e):
            # NOT a fallback case — switching models won't help
            # gpt-4o-mini has SMALLER context window
            # correct fix: compress context (Gap 19)
            messages = compress_messages(messages)
            # retry same model with compressed context
            return retry_with_compressed_context(messages, state)
        raise   # unexpected BadRequestError — do not mask

    except openai.RateLimitError:
        log_attempt("operational-premium", 1, "failed", "rate_limit")
        time.sleep(exponential_backoff(attempt=0))

    except openai.APIStatusError as e:
        if e.status_code == 503:
            log_attempt("operational-premium", 1, "failed", "service_unavailable")
        else:
            raise   # unexpected status — do not mask

    except openai.APITimeoutError:
        log_attempt("operational-premium", 1, "failed", "timeout")

    # Level 2 — Backup: gpt-4o-mini operational-model
    try:
        response = backup_client.chat.completions.create(
            model="operational-model",
            messages=messages,
            timeout=20
        )
        log_attempt("operational-model", 1, "success", None)
        return response.choices[0].message.content

    except (openai.RateLimitError, openai.APIStatusError, openai.APITimeoutError) as e:
        log_attempt("operational-model", 1, "failed", str(e))

    # Level 3 — Cached MCP response
    cached = get_cached_coaching_response(messages)
    if cached:
        log_attempt("mcp-cache", 1, "success", "cache_hit")
        return cached

    # Level 4 — Degraded mode (never a hard failure to the Belt)
    log_attempt("degraded", 1, "fallback", None)
    return degraded_mode_response(state)
```

**Critical distinction — context overflow is NOT a fallback case:**

```
HTTP 429 / 503 / Timeout  → infrastructure failure
                             gpt-4o-mini is a valid fallback
                             same prompt, smaller/different model

HTTP 400 context_length_exceeded → prompt engineering failure
                             gpt-4o-mini would ALSO fail (smaller window)
                             correct fix: compress messages[] first (Gap 19)
                             then retry the SAME model
```

This is the most common implementation mistake when applying the self-healing pattern to LLM systems — treating context overflow as a model failure rather than a context management failure.

---

**Two separate circuit breakers — LLM layer and MCP layer:**

```python
# Circuit Breaker 1 — wraps Azure OpenAI calls
llm_circuit_breaker = CircuitBreaker(threshold=3)
# 3 consecutive 503s → OPEN → stop trying primary model
# coaching turn fails → trigger Level 2 fallback

# Circuit Breaker 2 — wraps AgentLean MCP server calls
mcp_circuit_breaker = CircuitBreaker(threshold=3)
# 3 consecutive MCP failures → OPEN → skip knowledge retrieval
# coaching continues WITHOUT RAG grounding
# quality degradation, NOT availability failure — Belt still gets a response
```

These are independent — an MCP server outage does not affect LLM availability and should not trigger the LLM fallback chain:

```
MCP Circuit Breaker OPEN:
  → coaching turn still happens
  → LLM uses training knowledge instead of eBook index
  → Belt gets a response, just less well-grounded
  → log_attempt("mcp-server", attempt, "circuit_open", "knowledge_retrieval_skipped")
  → this is a QUALITY degradation, not a SYSTEM failure

LLM Circuit Breaker OPEN:
  → coaching turn cannot happen at all
  → must fall through to backup model or degraded mode
  → this is a SYSTEM degradation
```

**Exception type to fallback action mapping — the complete reference:**

| Exception | HTTP Code | Cause | Action |
|---|---|---|---|
| `openai.RateLimitError` | 429 | Token quota exceeded | Backoff + try Level 2 |
| `openai.APIStatusError` (503) | 503 | Azure OpenAI unavailable | Try Level 2 |
| `openai.APITimeoutError` | — | Request took too long | Try Level 2 |
| `openai.BadRequestError` (context) | 400 | Context window overflow | Compress + retry same model |
| `openai.AuthenticationError` | 401 | Wrong API key | Raise — do not retry |
| `openai.NotFoundError` | 404 | Wrong deployment name | Raise — do not retry |
| MCP `ConnectionError` | — | MCP server unreachable | Skip RAG, continue coaching |
| MCP `TimeoutError` | — | MCP server slow | Skip RAG, use cache |

The last two columns (Raise — do not retry) are as important as the fallback cases. Authentication and configuration errors will not resolve with retries — masking them with a fallback produces confusing behaviour that is hard to debug. Let them propagate immediately.

---

## 68. Decision Validation Against Business Constraints — Resilient Decision Agent Pattern

*Source: Edureka Course 4 Module 2, "Resilient Decision-Making Agent" demonstration transcript. Verified against current langchain_core documentation — same PromptTemplate caveat as Section 48 applies: use ChatPromptTemplate for gpt-4o/Azure OpenAI.*

### What Makes This Different From OutputFixingParser and RubricMiddleware

| Pattern | What It Validates | When It Applies |
|---|---|---|
| OutputFixingParser (Section 29) | Format correctness — is the JSON valid? | Output parsing failures |
| RubricMiddleware (Section 42/54) | Content quality — does it meet the rubric? | Gate document quality |
| DMAICGateValidator (Section 48) | Field completeness — are required fields present? | Gate field presence checks |
| **Decision Validation (this section)** | **Business constraints — does the decision address budget/timeline/risk?** | **Before acting on a decision** |

Decision validation validates a **choice before it is acted upon**, not the quality of an artifact after it is produced.

---

### Two Distinct Validation Layers

**Layer 1 — Constraint Validation:** does the decision address the business constraints that matter?

```python
def validate_constraints(decision: str, constraints: dict) -> tuple[bool, str]:
    issues = []

    if "budget" in constraints:
        if "budget" not in decision.lower():
            issues.append("Decision does not address budget")

    if "deadline" in constraints:
        if not any(w in decision.lower() for w in ["time", "deadline", "by", "within"]):
            issues.append("Decision does not address deadline")

    if constraints.get("risk_level") == "low":
        if "risk" not in decision.lower():
            issues.append("Decision does not address risk mitigation")

    if issues:
        return False, " | ".join(issues)
    return True, "All constraints satisfied"
```

**Layer 2 — Coherence Validation:** is this a real, conclusive decision?

```python
def check_coherence(decision: str) -> tuple[bool, str]:
    if len(decision.split()) < 10:
        return False, "Decision too brief — lacks detail"
    if "?" in decision:
        return False, "Decision is questioning — must be conclusive"
    return True, "Decision is coherent"
```

Both layers must pass. Coherence is checked first — a one-word answer that passes constraint checks is still not a valid decision.

---

### Retry With Accumulated Feedback — The Core Improvement Over Simple Retry

```python
def decide(situation: str, options: list, constraints: dict) -> str:
    previous_feedback = None

    for attempt in range(1, max_attempts + 1):

        # Each attempt receives WHY the previous failed
        decision = generate_decision(
            situation=situation,
            options=options,
            previous_feedback=previous_feedback   # ← accumulated context
        )

        coherent, coherence_msg = check_coherence(decision)
        if not coherent:
            previous_feedback = coherence_msg
            log_failure(attempt, decision, coherence_msg)
            continue

        valid, constraint_msg = validate_constraints(decision, constraints)
        if valid:
            log_success(attempt, decision)
            return decision

        previous_feedback = constraint_msg   # ← carries forward to next attempt
        log_failure(attempt, decision, constraint_msg)

    # All attempts exhausted — escalate to Belt
    log_fallback()
    return fallback_decision(situation, options)
```

`previous_feedback` is what makes this genuinely self-improving. Each generation call receives the specific failure reason from the previous attempt — not a generic "try again" but "your previous answer did not address timeline or risk mitigation, fix those specifically."

---

### Two Implementation Refinements From the Lab Code

**Refinement 1 — Pass `attempt` number to the generation function:**

```python
decision = self._generate_decision(situation, options, attempt)
```

The generation function knows which attempt it is on. This allows it to increase specificity and detail on later attempts — attempt 1 might produce a broad decision, attempt 3 knows two previous attempts failed and should be more precise and comprehensive. Without passing `attempt`, the generator produces the same kind of output regardless of how many times it has already failed.

**Refinement 2 — Dict-based audit log, not tuple:**

```python
# Tuple format (Section 67 — compact but opaque)
self.log.append((name, attempt+1, "success", None))

# Dict format (this section — self-documenting, easier to inspect)
self.decision_log.append({
    "attempt": attempt,
    "status": "success",
    "decision": decision
})
self.decision_log.append({
    "attempt": attempt,
    "status": "failed",
    "reason": feedback
})
```

Dict format with named keys is better for anything that will be inspected, exported to `step_log`, or queried later — field names make the log self-documenting without needing to remember which position holds which value.

**Use dict format for Agent Improve's `step_log`** — it connects directly to Section 18's audit trail requirement and Section 64's structured error schema, both of which use named fields.

---

### Value-Dependent Constraint Pattern — Worth Preserving

From Image 3, the risk constraint check is conditional on the constraint's own value:

```python
if "risk_level" in constraints:
    if constraints["risk_level"] == "low" and "risk" not in decision.lower():
        issues.append("Does not address risk mitigation")
```

Only enforces the risk keyword when `risk_level == "low"`. A high risk tolerance does not require explicit risk mention. This is a **value-dependent constraint** — the rule adapts based on context.

For Agent Improve this maps directly: the Control phase gate only requires explicit risk mitigation documentation if the improvement approach has `risk_level == "high"`. The constraint check is not static — it adapts to the project's actual risk profile. This is more sophisticated than the flat keyword checks and worth implementing for any constraint that is conditional on another field's value.

---

### Mapping to Agent Improve DMAIC Gate Decisions

The constraint set maps directly to DMAIC gate criteria:

**Define gate constraints:**
```python
define_constraints = {
    "baseline": "decision must reference a measurable current state",
    "target": "decision must include a specific improvement target",
    "scope": "decision must define what is included and excluded",
    "timeline": "decision must reference a project timeline"
}
```

**Analyse gate constraints:**
```python
analyse_constraints = {
    "root_cause": "decision must identify a specific, actionable root cause",
    "validation": "decision must reference how root cause was validated",
    "risk_level": "low"   # triggers risk mitigation check
}
```

**Improve gate constraints:**
```python
improve_constraints = {
    "budget": "improvement approach must address cost",
    "deadline": "implementation plan must reference timeline",
    "measurement": "must specify how improvement will be measured"
}
```

---

### Retry With Feedback — DMAIC Example

```
Attempt 1:
  Decision: "Reduce complaint rate"
  Coherence: FAIL — too brief (3 words)
  Feedback: "Decision too brief — lacks detail"

Attempt 2:
  Decision: "Implement agent training programme to reduce complaint rate"
  Coherence: PASS
  Constraints: FAIL — "does not address timeline or measurement method"
  Feedback: "does not address timeline or measurement method"

Attempt 3:
  Decision: "Implement structured agent training programme by Q3 2026
             to reduce complaint rate by 50%, measured weekly via CRM dashboard"
  Coherence: PASS
  Constraints: PASS — all satisfied
  → Gate approved
```

Each attempt is demonstrably better because the feedback is specific and accumulated. Attempt 3 addresses exactly what Attempt 2 missed.

---

### Fallback Decision — Gate-Level HITL Escalation

When all attempts fail, the system does NOT block the Belt or crash. It escalates to human judgment:

```python
def fallback_decision(situation: str, options: list) -> str:
    return (
        f"After {max_attempts} attempts, I was unable to generate a decision "
        f"that satisfies all gate constraints for: {situation}. "
        f"Options considered: {', '.join(options)}. "
        f"Please review the constraints manually and confirm your decision "
        f"before advancing to the next DMAIC phase. "
        f"Your progress is saved — nothing has been lost."
    )
```

This is the connection between decision validation and Gap 2 (HITL interrupts) — when the agent's self-correction loop exhausts its attempts, the decision escalates to the Belt rather than the system deciding unilaterally. The Belt is the final arbiter, not the agent.

---

### The Complete Validation Stack for Agent Improve Gates

All four validation layers now documented, each with a distinct role:

```
Gate validation sequence:

1. Coherence check (Section 68)
   Is this a real, conclusive statement? (not too short, not a question)
   → fast, deterministic, no LLM call

2. Field presence check (Section 48 DMAICGateValidator)
   Are all required fields populated?
   → fast, deterministic, no LLM call

3. Constraint validation (Section 68)
   Does the decision address budget / timeline / risk / measurement?
   → fast, deterministic, no LLM call

4. Quality evaluation (Section 42/54 RubricMiddleware)
   Does it meet DMAIC quality standards per criterion?
   → LLM grader call — most expensive, run last

Run in this order: cheapest first, most expensive last.
Only invoke the next layer if the previous passes.
```

### Gap Register Note
No new gap number — this section completes the gate validation architecture. The four-layer validation stack (coherence → field presence → constraint → quality rubric) is the complete implementation target for Gap 23's rubric-based gate evaluation. Run cheapest first, most expensive last.

---

## 69. Validation Layer Placement — Where Each Check Fires Across Agent Improve

*Source: Direct discussion clarifying where Sections 48, 68's validation patterns apply — every subagent turn vs gate boundaries only.*

### The Question

Do the four validation layers (coherence, field presence, constraint, rubric) fire at gates only, or at every subagent turn?

**Answer: it depends on the layer. Cheapest layers fire everywhere. Most expensive layers fire only at gates.**

---

### Where Each Layer Fires

**Coherence check — every coaching turn, all subagents**

Every LLM output should be coherent before it reaches the Belt. A response that is three words long or ends with a question mark is a generation failure regardless of phase or gate proximity. Cheapest check, always worth running.

```
Every coaching turn:
  LLM generates response
  → coherence check (too brief? contains "?"?)
  → FAIL: retry silently, Belt never sees it
  → PASS: send to Belt
```

**Field presence check — gate boundary only**

Fields are expected to be missing throughout a coaching conversation — the Belt provides information progressively. Checking completeness mid-conversation produces false alarms. Only meaningful when the Belt signals readiness to advance.

```
Gate boundary only:
  Belt: "I think we're ready to move on"
  → field presence check: all required fields populated?
  → FAIL: coaching continues, missing fields prompted
  → PASS: proceed to constraint check
```

**Constraint validation — gate boundary + one mid-conversation exception**

Gate-boundary logic applies for full constraint validation. Exception: when the Belt proposes a key decision mid-conversation (root cause, improvement hypothesis), the relevant constraint can be checked immediately — before it solidifies and reaches the gate as a problem.

```
Mid-conversation (specific subagents only):
  Belt proposes: "I think the root cause is poor morale"
  → constraint check: is this actionable and measurable?
  → FAIL: coach toward a more specific statement immediately
  → before it ever reaches the gate

Gate boundary:
  → full constraint validation across all fields
```

**Rubric / quality evaluation (RubricMiddleware) — gate boundary only**

Requires an LLM call — most expensive validation. Running it on every coaching turn triples cost and latency with no benefit. Only fires when the Belt is ready to close a phase AND all cheaper checks have already passed.

---

### Complete Validation Map

| Validation Layer | Every Turn | Key Decision Moments | Gate Boundary |
|---|---|---|---|
| Coherence check | ✅ always | ✅ always | ✅ always |
| Field presence | ❌ | ❌ | ✅ gate only |
| Constraint validation | ❌ | ✅ for key proposals | ✅ gate full check |
| Rubric / RubricMiddleware | ❌ | ❌ | ✅ gate only, last |

**Run in order: cheapest first, most expensive last. Only invoke the next layer if the previous passes.**

---

### Retry and Fallback Behaviour Per Context

**Every coaching turn — silent system retry:**
```
Coherence fails → retry same subagent immediately
                  Belt never sees the failed attempt
Max 2 retries → degraded mode response (Section 66)
                  Belt sees: "I need a moment to reconnect..."
```

**Key decision moments — collaborative improvement:**
```
Constraint fails → coach the Belt toward a better formulation
                   Belt participates in improving their own output
                   Not a silent retry — feedback is explicit and educational
```

**Gate boundary — full decision validation loop:**
```
Any layer fails → retry with accumulated feedback (Section 68)
Max 3 attempts → HITL escalation to Belt (Section 68 fallback)
                  "After 3 attempts, please review these constraints manually"
                  Belt is the final arbiter, not the agent
```

**The critical distinction:**

```
Mid-conversation failures  → handled SILENTLY by the system
                              Belt never sees a failed coherence check
                              system self-heals invisibly

Gate failures              → handled COLLABORATIVELY with the Belt
                              Belt receives the feedback
                              Belt participates in fixing it
                              Belt approves before advancing
```

---

### The Self-Healing Pattern Hierarchy

```
Level 1 — Silent self-healing (invisible to Belt):
  Coherence failure mid-turn
  → system retries internally
  → Belt receives only the corrected response

Level 2 — Coached self-healing (Belt participates):
  Constraint failure on a key proposal
  → agent coaches Belt toward a compliant formulation
  → Belt learns what makes a good root cause / goal statement

Level 3 — Validated gate progression (Belt approves):
  Full four-layer validation at gate boundary
  → Belt sees exactly what passed and what failed
  → Belt corrects and resubmits
  → Belt explicitly approves before phase advances

Level 4 — HITL escalation (system defers to Belt):
  Max attempts exhausted at gate
  → agent provides conservative fallback with named unresolved constraints
  → Belt manually reviews and decides
  → nothing advances without Belt confirmation
```

This hierarchy ensures the Belt is never surprised — they only see failures at the level where their input is genuinely needed to resolve them.

### Gap Register Note
No new gap number — this section maps the existing validation architecture (Sections 48, 68) to the correct firing points across Agent Improve's subagent structure. Use this table directly in the DMAIC redraw to specify which validation behaviour belongs in which node type.

---

## 70. Inter-Stage Data Dependency — Outputs Become Inputs

*Source: Edureka Course 4 Module 2, "Planner → Executor → Validator Workflow" demonstration. Adds one concrete refinement to Section 11's Planner/Executor pattern.*

In a multi-stage planner/executor workflow, outputs from earlier stages are not just recorded — they become the explicit inputs to later stages. The executor manages this flow deliberately:

```python
class Executor:
    def execute(self, plan: dict, product_data: dict) -> list:
        results = []

        # Stage 1 — output captured for downstream use
        stage1_output = self.market_analysis_agent.run(product_data)
        selected_segment = stage1_output["selected_segment"]   # ← stored explicitly
        results.append(stage1_output)

        # Stage 3 — receives Stage 1's output as its input
        stage3_output = self.marketing_agent.run(
            target_segment=selected_segment   # ← Stage 1 output passed forward
        )
        results.append(stage3_output)

        return results
```

### Why This Matters for Agent Improve Specifically

Each DMAIC phase is not independent — it depends on validated structured outputs from the previous phase:

```
DefineOutput (ctqs, scope, team, problem_statement)
        ↓ becomes input to
MeasureState  (baseline calculated against Define's scope)
        ↓ becomes input to
AnalyseState  (root cause analysis within Measure's baseline)
        ↓ becomes input to
ImproveState  (solution designed for Analyse's root cause)
        ↓ becomes input to
ControlState  (monitoring plan for Improve's solution)
```

`DefineOutput` as a typed Pydantic object (Section 44) is not just a completion record — it is the structured input the Measure phase planner uses to scope its work correctly. The Phase Orchestrator explicitly passes `define_output` into the Measure subgraph's initial state. The Measure subgraph reads `define_output.scope` and `define_output.ctqs` to know what to measure — it does not independently decide.

**This is why gate quality (Gap 23) matters so much:** a weak Define gate produces a compounding error across all downstream phases. A problem statement without a measurable baseline produces a Measure phase that cannot establish a valid sigma level. A sigma level without a valid baseline produces an Analyse phase that cannot validate root causes. The error propagates and amplifies through each stage. Gate quality is not a bureaucratic checkpoint — it is a data integrity guarantee for every downstream phase.

### Gap Register Note
No new gap number — this section reinforces Gap 23's importance with the inter-stage dependency argument. Use this reasoning when explaining to stakeholders why gate quality validation is non-negotiable, not optional.

---

## 71. Multi-Hop Retrieval — Gap 17 Formally Closed

*Source: Edureka Course 4 Module 2, "Multi-Stage Knowledge Pipeline and Multi-Hop System Reasoning" demonstration, plus direct discussion on where multi-hop applies across Agent Improve's architecture.*

### What Multi-Hop Retrieval Is

A single user query decomposed into sequential dependent reasoning hops where the answer to each hop becomes the input to the next:

```
Query: "What is the release year of the latest album by the artist who sang Blinding Lights?"

Hop 1: "Which artist sang Blinding Lights?"           → "The Weeknd"
Hop 2: "What is The Weeknd's latest album?"           → "Dawn FM"  (uses Hop 1)
Hop 3: "What year was Dawn FM released?"              → "2022"     (uses Hop 2)

Synthesis: "The release year of Dawn FM, The Weeknd's latest album, is 2022."
```

This is fundamentally different from parallel retrieval (Section 28) where all queries are independent. Each hop narrows the search space using the previous hop's answer.

---

### The Three-Stage Pipeline Architecture

**Stage 1 — Planner (LLM with structured output):**

```python
class Hop(BaseModel):
    hop_number: int        # 1, 2, or 3
    hop_question: str      # sub-question for this hop

class Plan(BaseModel):
    reasoning: str                  # overall approach
    hops: list[Hop]                 # exactly 3 dependent hops
    synthesis_instruction: str      # how to combine hop answers

# Planner forced to return typed Pydantic output
planner = llm.with_structured_output(Plan)
plan = planner.invoke(decomposition_prompt)
```

The planner prompt enforces: Hop 2 depends on Hop 1, Hop 3 depends on Hop 2. Same typed-boundary-contract discipline as Section 44 — structured output, never raw text.

**Stage 2 — Executor (sequential with shared state):**

```python
state = {"entity": extracted_entity}   # starts with extracted input

for hop in sorted(plan.hops, key=lambda h: h.hop_number):
    result = retrieve_methodology(
        query=hop.hop_question.format(**state),   # templates filled from state
        phase=current_phase
    )
    state[f"hop{hop.hop_number}_answer"] = result   # stored for next hop
```

The `state` dict carries intermediate answers — identical role to LangGraph's state object. Each hop's answer template references previous hop results: `"how is {hop1_answer} applied to {root_cause_candidate}"`.

**Stage 3 — Synthesis (LLM call):**

All hop answers combined into one coherent coaching response using the `synthesis_instruction` from the Plan object.

---

### The Three Query Types in Agent Improve — Where Multi-Hop Belongs

**Type 1 — Methodology retrieval (multi-hop applies)**
Agent needs knowledge to GROUND its coaching response.
Source: `improve_knowledge_index` (eBook).
```
Example: "how do I validate this root cause methodologically?"
→ multi-hop retrieval from knowledge index
→ Hop 1: what tools exist → Hop 2: which applies here → Hop 3: specific parameters
```

**Type 2 — Belt's conversational answers (multi-hop does NOT apply)**
Belt is answering the agent's coaching questions.
Source: Belt's own input, captured into state fields.
```
Example: Belt says "our baseline complaint rate is 8.3%"
→ field extraction and validation (Sections 48, 68, 69)
→ NOT retrieval — no index involved
```

**Type 3 — Gate quality evaluation (multi-hop does NOT apply)**
Checking whether captured fields meet DMAIC standards.
Source: `captured_fields` already in `DMAICState`.
```
Example: "does this problem statement have a measurable baseline?"
→ DMAICGateValidator + RubricMiddleware (Sections 48, 68)
→ NOT retrieval — evaluating what is already in state
```

---

### Why Multi-Hop Does NOT Belong at Gate Validation

This was raised specifically and deserves a precise answer.

**The gate validation pipeline is a structured check, not a reasoning problem:**
```
Coherence → Field presence → Constraint check → RubricMiddleware
ALL deterministic or single LLM call with pre-defined rubric
NO retrieval at any stage
```

RubricMiddleware's grader already has the rubric definition — the SMART criteria, the field quality standards, the DMAIC requirements. Adding multi-hop retrieval on top of a grader that already has the criteria would be redundant. The rubric IS the methodology standard, encoded explicitly. If the rubric is incomplete, the fix is to improve the rubric, not add retrieval at validation time.

**Latency argument:** gate validation already involves a RubricMiddleware grader LLM call. Adding 3 sequential search queries before or during that call adds significant latency at exactly the moment the Belt is waiting for a gate decision.

**The correct design:** multi-hop retrieval improves the coaching that helps the Belt write better gate content. It serves the coaching turn BEFORE the content reaches the gate, not the validation AT the gate.

```
Multi-hop retrieval:
  Coaching turn → helps Belt produce better goal statement
  → methodology-grounded advice on what makes a SMART goal

Gate validation:
  Rubric check → confirms the goal statement already meets the standard
  → deterministic, no retrieval needed
```

---

### Phase-by-Phase Multi-Hop Decision Table

| Phase | Default | Multi-Hop Trigger | Rationale |
|---|---|---|---|
| Define | Single-hop | Never | Scoping questions are direct and answerable |
| Measure | Single-hop | Complex measurement system validation questions | Most questions are direct; GR&R methodology is the exception |
| **Analyse** | **Multi-hop** | Almost always | Root cause validation is inherently layered — method → application → threshold |
| Improve | Single-hop | When Belt compares competing approaches | Simple implementation questions need no chaining |
| Control | Single-hop | Never | Documentation questions are specific and direct |
| **Gate validation** | **No retrieval** | **Never** | Rubric already encodes the standards; retrieval is redundant |

---

### How the Phase Planner Decides Retrieval Strategy

The Phase Planner (Section 11) decides at plan time, not at retrieval time:

```python
coaching_plan = {
    "next_action": "coach_root_cause_validation",
    "retrieval_strategy": "multi_hop",    # ← planner decides
    "retrieval_hops": [
        "what tools validate root cause in DMAIC analyse phase",
        "how is {hop1_answer} applied to {root_cause_candidate}",
        "what threshold applies for {hop2_answer} in a call centre context"
    ],
    "focus_field": "root_cause_statement"
}
```

When `retrieval_strategy == "single_hop"` the executor calls `retrieve_methodology` once. When `retrieval_strategy == "multi_hop"` it runs the three-hop chain. The Belt never sees the difference — they only see the coaching response, which is better grounded in the multi-hop case.

---

### Connection to Existing Gaps

**Gap 17 — FORMALLY CLOSED.** Multi-hop retrieval is now fully defined:
- What it is (sequential dependent hops)
- Where it applies (Type 1 methodology retrieval, Analyse phase primarily)
- Where it does NOT apply (Type 2 Belt answers, Type 3 gate validation)
- How the Phase Planner triggers it (retrieval_strategy field in coaching_plan)
- The implementation pattern (Pydantic Plan schema, state dict for intermediate results)

**Gap 15 (multi-query retrieval) relationship:** multi-query generates parallel variants of the same query to overcome vocabulary mismatch. Multi-hop generates sequential dependent queries where answers chain. Both can be used together: multi-query at each hop to improve recall, then chain the best result from each hop to the next.

### Gap Register Update
**Gap 17 — CLOSED.** Multi-hop retrieval fully designed and scoped. Analyse phase is the primary implementation target. Gate validation explicitly excluded. Implement as a retrieval_strategy option in the Phase Planner's coaching_plan output, resolved at execution time by the Phase Executor's tool-calling loop.

---

## 72. LangGraph Server — Deployment Option for AgentLean

*Source: Verified against official LangChain documentation (docs.langchain.com/langsmith/deploy-standalone-server), LangGraph Platform GA announcement, and multiple current sources (March-May 2026). This section documents LangGraph Server as an OPTION to evaluate during the DMAIC redraw — not a decision already made.*

### What LangGraph Server Is

The confirmed direct replacement for LangServe (archived May 2026). Where LangServe exposed generic LangChain runnables as APIs, LangGraph Server is purpose-built for stateful, long-running, multi-agent LangGraph graphs.

```
LangServe (archived) → replaced by → LangGraph Server (current)
Same problem: expose your agent as a production API
Better solution: stateful, HITL-aware, checkpointer-integrated
```

---

### How It Works — Three Files, No Custom Routes

**Step 1 — `langgraph.json` in project root (replaces routes.py):**

```json
{
  "dependencies": ["."],
  "graphs": {
    "agent_improve": "./agent-improve/backend/graph.py:graph",
    "agent_resolve": "./agent-resolve/backend/graph.py:graph"
  },
  "env": ".env"
}
```

LangGraph Server reads this, finds your compiled graphs, auto-generates all endpoints.

**Step 2 — Local development:**
```bash
langgraph dev
# Server at http://localhost:2024
# LangGraph Studio connects automatically — visual graph debugger
```

**Step 3 — Production deployment:**
```bash
langgraph build    # creates Docker image
langgraph deploy   # cloud deployment (March 2026, supersedes langgraph up)
# OR
langgraph up       # self-hosted Docker Compose flow
```

**What you get automatically — no code to write:**
```
POST /agent_improve/invoke              ← replaces /chat endpoint
POST /agent_improve/stream              ← SSE streaming built in
POST /agent_improve/threads             ← thread_id management built in
POST /agent_improve/threads/{id}/runs   ← resume a paused HITL thread
GET  /agent_improve/threads/{id}/state  ← inspect current state
```

---

### The Four Deployment Options — Confirmed Current

| Option | What It Is | AgentLean Fit |
|---|---|---|
| Cloud SaaS | Fully managed, hosted by LangChain | ❌ Data goes through LangChain servers — residency concern |
| Hybrid (BYOC) | LangChain manages platform, data in your Azure VPC | ⚠️ Enterprise plan only, contact sales |
| Self-Hosted | Run entirely in your Azure infrastructure | ✅ Best fit — data stays in Azure, full control |
| Developer (free) | Self-hosted, up to 100k nodes/month free | ✅ Good for dev and testing phase |

**Self-hosted infrastructure requirements:**
```
PostgreSQL  → already planned (Section 52's PostgresSaver)
Redis       → NEW — required for SSE streaming pub/sub
Docker      → for packaging and deployment
LangSmith API key → for tracing (already have this)
License key → LANGGRAPH_CLOUD_LICENSE_KEY (required for self-hosted)
```

Redis is the only genuinely new infrastructure dependency.

---

### The Honest Comparison — FastAPI vs LangGraph Server

| Concern | Current FastAPI | LangGraph Server (self-hosted) |
|---|---|---|
| Already built | ✅ working today | ❌ migration required |
| HITL resume (Gap 2) | ❌ needs custom implementation | ✅ built in |
| Thread management | ❌ your code in routes.py | ✅ built in |
| SSE streaming | ❌ your custom implementation | ✅ built in |
| LangGraph Studio | ❌ not available | ✅ visual graph debugger |
| Data residency | ✅ your Azure tenant | ✅ self-hosted stays in Azure |
| Redis dependency | ✅ not needed | ❌ new requirement |
| License key | ✅ not needed | ❌ required |
| Custom endpoint control | ✅ full control | ❌ standardised endpoints only |
| Migration effort | ✅ none | ❌ replace routes.py with langgraph.json |

---

### The HITL Argument — The Strongest Case for Switching

The most compelling reason to consider LangGraph Server specifically for AgentLean is **Gap 2** — HITL interrupts and resume. Building a correct, reliable HITL resume mechanism in custom FastAPI is non-trivial work. LangGraph Server provides it automatically:

```
POST /agent_improve/threads/{thread_id}/runs
body: {"command": {"resume": {"decisions": [...]}}}
```

This is the exact `Command(resume=...)` pattern from Section 53 — built by the people who designed the interrupt mechanism, already tested at scale. The alternative is implementing Gap 2 from scratch in `routes.py` and debugging edge cases in custom HITL logic.

---

### The Decision Framework for the DMAIC Redraw

This is not a decision to default into. It is a deliberate architectural choice with real trade-offs. Evaluate during the DMAIC redraw against these specific questions:

```
Question 1: How complex is Gap 2 (HITL) to implement in FastAPI?
  → If high complexity: LangGraph Server's built-in HITL is a strong argument
  → If manageable: FastAPI's advantages outweigh the migration cost

Question 2: Is LangGraph Studio worth the Redis + license overhead?
  → During development of all three agents: probably yes
  → For a production system already working: probably not

Question 3: Are all three agents completing the refactor at the same time?
  → If yes: migrate all three together with one langgraph.json
  → If no: keep FastAPI for the working agents, decide when all are complete
    (this aligns with the existing Azure migration plan — all three agents
     migrate infrastructure together)

Question 4: Does the license key create a vendor dependency concern?
  → For enterprise customers: evaluate carefully
  → For AgentLean's own use: less critical
```

---

### What Does Not Change Regardless of Choice

LangSmith observability stays regardless — it is independent of the API layer. Whether you keep FastAPI or adopt LangGraph Server, every coaching turn is traced, every node execution is logged, and LangSmith evaluation datasets work identically.

The LangGraph graph code itself does not change. `DMAICState`, phase subgraphs, the Orchestrator, the checkpointer — all identical. The only thing that changes is the layer that exposes the graph to the outside world.

### Gap Register Note
No new gap number — this section documents LangGraph Server as an option that directly addresses Gap 2 (HITL) through built-in resume endpoints. Evaluate explicitly during the DMAIC redraw. Do not default to either option without consciously working through the decision framework above.

---

## 73. Langfuse — Open-Source LangSmith Alternative

*Source: Verified against multiple current independent sources, May-June 2026. Triggered by the course introducing Langfuse in Module 3.*

### What It Is

Langfuse is an open-source LLM observability platform that does the same job as LangSmith — tracing, evaluation, prompt management, cost monitoring, and debugging — but built with a different philosophy: open-source, self-hostable, and framework-agnostic.

**Key facts confirmed current:**
- MIT licensed — free to self-host with unlimited usage
- Acquired by ClickHouse in January 2026 (ClickHouse is the database that already powered Langfuse's backend)
- 26 million monthly SDK installs as of early 2026
- Added Agent Graphs in November 2025 — visualises multi-step agent execution flow
- Added full-text search in May 2026 (ClickHouse-backed, sub-500ms)
- MCP server expanded in May 2026 — agents in Claude Code, Cursor, or OpenAI Codex can query Langfuse data programmatically

---

### Langfuse vs LangSmith — The Precise Comparison

Both cover the same core capabilities: tracing, evaluation, dataset management, prompt versioning, cost monitoring. The difference is deployment model and ecosystem tie-in.

| Concern | LangSmith | Langfuse |
|---|---|---|
| Open source | ❌ closed source | ✅ MIT licensed |
| Self-hosting | ❌ managed only (or complex) | ✅ free, unlimited, no license |
| Framework tie-in | LangChain/LangGraph native | Framework-agnostic (works with any stack) |
| LangGraph integration | ✅ automatic, zero config | ✅ native support, manual setup |
| LangGraph Studio | ✅ included | ❌ not included |
| Data sovereignty | Data goes to LangChain servers | ✅ data stays in your infrastructure |
| Pricing (self-hosted) | ❌ not available | ✅ free |
| Pricing (cloud) | $39/seat/month + trace volume | Free tier 50k obs/month, Pro ~$59/month |
| Agent graph visualisation | ✅ LangGraph Studio | ✅ Agent Graphs (inferred from traces) |
| ISO 27001 certification | ❌ | ✅ |
| ClickHouse SQL access | ❌ | ✅ self-hosted — raw SQL over all trace data |

**The one-sentence decision rule confirmed across multiple sources:**
> "We must keep data on our own infrastructure" → Langfuse.
> "We are all-in on LangChain and want zero-config tracing" → LangSmith.

---

### For AgentLean Specifically

This is worth thinking through precisely rather than defaulting.

**Arguments for staying with LangSmith (already wired in since commit 1.1):**
- Zero additional setup — already working
- LangGraph integration is automatic via environment variables
- LangGraph Studio is only available through LangSmith
- The team behind LangGraph builds and maintains LangSmith
- If using LangGraph Server (Section 72), LangSmith integration is seamless

**Arguments for considering Langfuse:**
- Data sovereignty — DMAIC project data (process metrics, root causes, improvement hypotheses) is sensitive; enterprise customers may require it to stay entirely within their infrastructure
- Self-hosted Langfuse is free — no per-seat cost as the team grows
- Framework-agnostic — if AgentLean ever runs models outside the LangChain ecosystem, Langfuse traces them equally
- ISO 27001 certification — relevant for enterprise sales conversations
- ClickHouse acquisition gives it serious data infrastructure backing

**The honest recommendation:**

Keep LangSmith for now — it is already wired in, it is the right tool for a LangGraph-native system, and the zero-config integration is genuinely valuable during the refactor. Revisit the decision when:
1. The first enterprise customer asks about data residency for their observability data
2. The team grows to a point where per-seat LangSmith pricing becomes significant
3. AgentLean adds components outside the LangChain ecosystem

At that point, Langfuse self-hosted is the natural upgrade path. The two tools are compatible with the same instrumentation patterns — migration is not a rewrite.

---

### One Genuinely New Capability — Code Evaluators

Langfuse's Code Evaluators can verify tool arguments against a schema programmatically — not just LLM-as-judge. For Agent Improve's field extraction nodes, this means you could write a code evaluator that checks whether an extracted `baseline_mean` is numeric and within a plausible range, running automatically against every production trace without LLM cost.

This is more precise than LLM-as-judge for objective field validation and connects directly to Gap 23's quality evaluation architecture. LangSmith's equivalent is more LLM-evaluation-centric.

### Gap Register Note
No new gap number — Langfuse is an observability option to evaluate at the enterprise deployment stage, not an architectural gap in Agent Improve's current design. LangSmith remains the correct choice for the v2.1 refactor phase. Document this section for the enterprise deployment conversation.

---

## 74. Agent API Versioning — Framework-Agnostic Concepts for AgentLean

*Source: Edureka Course 4 Module 3, "Designing Versioned Agent Endpoints" transcript. LangServe-specific implementation replaced with FastAPI and LangGraph Server equivalents. Concepts are framework-agnostic and directly applicable to the v2.1 refactor.*

### Why Versioning Matters for Agent APIs

Agent APIs are different from standard REST APIs in one critical way: **the interface can stay identical while the behaviour changes completely**. A model update, a prompt change, a graph restructure, or a new tool can all produce different outputs for the same input without changing a single endpoint signature. Downstream systems break silently.

Three specific risks for AgentLean:

```
Risk 1 — State schema change:
  v1 DMAICState has flat captured_fields dict
  v2 DMAICState has typed DefineOutput, MeasureOutput boundaries
  Same /chat endpoint, completely different state structure
  Frontend calling v1 expectations gets v2 responses → silent breakage

Risk 2 — HITL gate responses added:
  v1 coaching turns return {response: "..."}
  v2 gate turns return {response: "...", interrupt: true, gate_data: {...}}
  Frontend not expecting interrupt field → silent breakage

Risk 3 — Behaviour change without interface change:
  v1 uses flat LLM call for coaching
  v2 uses Phase Planner → Phase Executor with structured coaching_plan
  Same request format, meaningfully different response quality and structure
```

---

### The Five Versioning Patterns — Framework-Agnostic

These apply to any HTTP API layer — FastAPI, LangGraph Server, or anything else:

**URI-based (simplest, most visible):**
```python
# FastAPI — most explicit, easiest to route and document
@router.post("/v1/chat")   # current Agent Improve (pre-refactor)
async def chat_v1(): ...

@router.post("/v2/chat")   # Agent Improve v2.1 (post-refactor)
async def chat_v2(): ...
```

**Graph-mapped (most relevant for LangGraph):**
```python
# Different compiled graph per version — same endpoint logic, different graph
graphs = {
    "v1": build_graph_v1(checkpointer),   # current flat graph
    "v2": build_graph_v2(checkpointer),   # refactored subgraph hierarchy
}

@router.post("/{version}/chat")
async def chat(version: str, request: ChatRequest):
    graph = graphs.get(version)
    if not graph:
        raise HTTPException(404, f"Version {version} not found")
    return await graph.ainvoke(request.dict())
```

**LangGraph Server equivalent (langgraph.json):**
```json
{
  "graphs": {
    "agent_improve_v1": "./graph_v1.py:graph",
    "agent_improve_v2": "./graph_v2.py:graph"
  }
}
```
LangGraph Server auto-generates `/agent_improve_v1/invoke` and `/agent_improve_v2/invoke` — versioning falls out of the graph naming convention.

---

### What Constitutes a Breaking Change for Agent Improve

Define this explicitly before the v2.1 refactor begins. Any change in this list requires a version bump:

```
Breaking changes (require /v2 endpoint):
  ✗ State schema restructured (DMAICState field names or types changed)
  ✗ Response format changed (new required fields added to response)
  ✗ HITL interrupt responses introduced (new interrupt: true field)
  ✗ thread_id management changed (if moving to LangGraph Server)
  ✗ SSE streaming behaviour changed

Non-breaking changes (can ship to existing /v1 endpoint):
  ✓ Prompt quality improved (same interface, better output)
  ✓ New optional response fields added (clients ignore unknown fields)
  ✓ Internal graph restructure with same input/output contract
  ✓ Model upgraded (gpt-4o → gpt-4o-next) with same behaviour contract
  ✓ Bug fixes that preserve the existing interface
```

---

### Minimum Versioning Plan for the v2.1 Refactor

```
Step 1 — Before refactor begins:
  Document the current v1 API contract:
  - Request schema
  - Response schema
  - SSE event format
  - Error response format

Step 2 — Ship v2 alongside v1 (not replacing it):
  /v1/chat → current Agent Improve (unchanged, still serving existing frontend)
  /v2/chat → refactored Agent Improve v2.1

Step 3 — Parallel running period:
  Both versions run simultaneously
  Frontend migrates to v2 at its own pace
  Monitor v1 usage — when zero, deprecate

Step 4 — Deprecate v1 with timeline:
  Add Deprecation header to v1 responses:
  "Deprecation: 2026-10-01, Sunset: 2026-12-01"
  Document breaking changes between v1 and v2

Step 5 — Remove v1 after sunset date
```

---

### Compatibility Rules — Four Practices

**1. Define breaking changes before making any change** (table above)

**2. Preserve input/output schemas wherever possible**
Add new fields as optional — never remove or rename existing fields in a minor version. Clients must be able to ignore unknown fields safely.

**3. Deprecate gradually with documented timelines**
Never remove a version without a minimum 90-day notice. Add `Deprecation` and `Sunset` headers to responses from deprecated endpoints so clients can detect it programmatically.

**4. Add new features through optional fields**
New HITL gate response fields should be optional in the initial v2 release, becoming required only in v3. This gives existing v2 clients time to adopt.

---

### What Changes Between Agent Improve v1 and v2

Documenting this now, before the refactor, is the versioning discipline in practice:

| Component | v1 (current) | v2 (post-refactor) | Breaking? |
|---|---|---|---|
| State schema | Flat DMAICState | Typed DefineOutput etc. crossing subgraph boundaries | ✅ Yes |
| Routing | Manual in routes.py | Command-based in graph | ❌ No (internal) |
| HITL | Not implemented | Gate interrupt + resume | ✅ Yes (new response field) |
| Streaming | Custom SSE | Custom SSE or LangGraph Server SSE | ✅ Yes if switching |
| thread_id | Your code | Built-in (if LangGraph Server) or your code | ✅ Yes if switching |
| Checkpointer | Azure Blob (current) | PostgresSaver (target) | ❌ No (internal) |

### Gap Register Note
No new gap number — versioning is an operational discipline for the v2.1 refactor, not an architectural gap. The breaking change table above should be reviewed and confirmed during the DMAIC redraw before the refactor begins, so Claude Code knows exactly what constitutes a version boundary.

---

## 75. Evaluation Dataset Design and Regression Testing for Agent Improve

*Source: Edureka Course 4 Module 3, "Evaluation Dataset Design and Regression Testing" transcript, verified against LangSmith evaluation documentation and multiple current sources (May-June 2026). This fills a genuine gap in this document — evaluation was mentioned in passing but never formally designed.*

### Why Traditional Testing Fails for Agent Systems

Traditional tests check "does the code run." Agent evals check "is the output good." For the same input, multiple responses may be acceptable. Reasoning paths evolve across runs and versions, making fixed test expectations unreliable.

```
Traditional test:
  assert response == "The baseline sigma is 2.1"   ← brittle, breaks on any rephrasing

Agent eval:
  evaluator(response): "Does this response correctly identify
                        the baseline sigma and explain its significance?"
  → PASS or FAIL based on semantic correctness, not exact string match
```

The key insight confirmed from production experience: *"You changed a system prompt. It looks better on the three examples you tried. You ship it. Tuesday morning, support tickets spike. The agent is now hallucinating policy details on a class of queries you didn't test."* This is not a testing problem — it is an evaluation problem.

---

### The Two Types of Evaluation — Both Required

**Offline evaluation (before deployment):**
Runs against curated datasets during development. Acts as unit tests for the LLM application. Catches regressions before they reach production. Costs approximately $0.50 per run for a reasonable dataset size.

**Online evaluation (after deployment):**
Scores real-world production traffic in real-time. Detects quality drift that offline evals cannot catch — the distribution of real Belt questions is never fully represented in any curated dataset.

Both are needed. Offline catches known regressions. Online catches unknown drift.

---

### Evaluation Dataset Design for Agent Improve

**What the dataset should contain — five categories:**

```
Category 1 — Realistic coaching turns (core coverage):
  Real coaching exchanges across all five DMAIC phases
  Include Belt questions that are clear, ambiguous, and incomplete
  At least 10-15 examples per phase minimum

Category 2 — Edge cases (stress testing):
  Belt provides contradictory information
  Belt tries to skip a phase
  Belt's answer is in a non-English phrase mixed into English
  Belt provides a number in the wrong unit (percentage vs decimal)

Category 3 — Tool-calling scenarios:
  Turns where multi-hop retrieval should fire (Section 71)
  Turns where methodology grounding is needed
  Verify: did the agent call the right tools? In the right order?

Category 4 — Failure cases and ambiguous examples:
  Belt gives a vague non-answer to a direct field question
  Belt proposes a root cause that is too vague to be actionable
  Belt's SMART goal is missing the time-bound criterion
  Expected: agent detects and coaches toward correction

Category 5 — Historical production data (once available):
  Real IMPR-2026-E9D coaching exchanges
  Real gate submissions and their validation outcomes
  Ground the dataset in how Belts actually behave
```

---

### Success Metrics for Agent Improve Evals

Five metrics mapped to Agent Improve's specific needs:

| Metric | What It Checks | Agent Improve Specific |
|---|---|---|
| Accuracy | Does the agent produce the correct result? | Field extraction correctness — did `baseline_mean` extract the right number? |
| Relevance | Does the response align with the Belt's intent? | Does the coaching address what the Belt actually asked? |
| Reasoning quality | Does the agent explain decisions logically? | Does the agent explain WHY a root cause fails validation, not just that it does? |
| Tool usage | Are tools invoked appropriately? | Was `retrieve_methodology` called when needed? Was it called unnecessarily? |
| Safety | Are outputs compliant and responsible? | Does the agent ever invent methodology that contradicts the Black Belt eBook? |

---

### The LangSmith Evaluation Pipeline — Confirmed Current

```python
from langsmith import Client
from langsmith.evaluation import evaluate, LangChainStringEvaluator

client = Client()

# Step 1 — Create dataset (once, then grow it)
dataset = client.create_dataset(
    "agent_improve_coaching_evals",
    description="DMAIC coaching quality evaluation dataset"
)

# Step 2 — Add examples
client.create_examples(
    inputs=[
        {"phase": "analyse", "belt_message": "I think the root cause is poor morale"},
        {"phase": "define", "belt_message": "We want to reduce complaints"},
    ],
    outputs=[
        {"expected_behaviour": "Agent asks for evidence and suggests validation method"},
        {"expected_behaviour": "Agent asks for a measurable baseline and target"},
    ],
    dataset_id=dataset.id
)

# Step 3 — Define evaluator
def coaching_quality_evaluator(run, example):
    response = run.outputs["response"]
    expected = example.outputs["expected_behaviour"]

    # LLM-as-judge: did the agent do what it should have done?
    score = llm_judge(
        response=response,
        expected=expected,
        criteria="Did the agent coach appropriately given the expected behaviour?"
    )
    return {"key": "coaching_quality", "score": score}

# Step 4 — Run evaluation
results = evaluate(
    agent_improve_graph,
    data=dataset.id,
    evaluators=[coaching_quality_evaluator],
    experiment_prefix="v2.1-refactor"
)
```

---

### Regression Detection — Block Releases on Quality Drop

The most critical production pattern confirmed from real deployments:

```python
# In CI/CD pipeline — runs on every PR that touches prompts, graph, or model config
def check_for_regressions(current_experiment, baseline_experiment, threshold=0.10):
    """Block release if any evaluator's pass rate drops more than 10%."""

    for metric in ["coaching_quality", "field_extraction_accuracy", "tool_usage"]:
        baseline_score = get_experiment_score(baseline_experiment, metric)
        current_score = get_experiment_score(current_experiment, metric)

        drop = baseline_score - current_score
        if drop > threshold:
            raise RegressionError(
                f"REGRESSION DETECTED: {metric} dropped {drop:.1%} "
                f"(from {baseline_score:.1%} to {current_score:.1%}). "
                f"Release blocked."
            )
```

This is the evaluation equivalent of Gap 27's PostToolUse hook — automated enforcement that catches quality regressions at the PR level rather than discovering them from Belt complaints in production.

---

### The Minimum Eval Suite for the v2.1 Refactor

Before the refactor begins, establish a baseline. After each implementation step, run the suite and confirm no regression. This is the quality safety net for the entire refactor.

```
Minimum viable eval suite for Agent Improve v2.1:

Dataset:
  20 examples across all five DMAIC phases (4 per phase)
  Including: 10 clear cases, 5 edge cases, 5 field extraction validation cases

Evaluators (in order of cost):
  1. Field extraction accuracy  — deterministic, $0 (exact match on extracted fields)
  2. Coaching relevance         — LLM-as-judge, low cost (~$0.01 per example)
  3. Reasoning quality          — LLM-as-judge, moderate cost (~$0.02 per example)

Total cost per run: ~$0.60 for 20 examples
Recommended frequency: every commit that touches system prompts, graph structure, or model config

Regression threshold: block release if any metric drops > 10% from baseline
```

---

### Connection to the Refactor Sequence

The eval suite should be built **before** Step 3.1 resumes — not after. The refactor will change graph structure, prompts, and state schema simultaneously. Without a pre-refactor baseline, you cannot distinguish "this regression was introduced in Step 3.1" from "this regression was introduced in Step 4.2." A baseline established now makes every subsequent commit auditable.

```
Correct sequence:
  1. Build minimum eval suite → establish v1 baseline
  2. Begin v2.1 refactor (Step 3.1 onward)
  3. Run eval suite after each step
  4. Any regression → fix before proceeding to next step
  5. v2.1 complete → final eval run confirms quality maintained or improved
```

### Gap Register
No new gap number — evaluation dataset design and regression testing are operational requirements for the v2.1 refactor, not architectural gaps in Agent Improve's design. The minimum eval suite above should be built as the first task before resuming Step 3.1. This is the most important operational addition from Module 3.

---

## 76. Docker — Containerisation for AgentLean

*Source: Direct explanation triggered by Edureka Course 4 Module 3 containerisation content. Framework-agnostic concepts preserved; LangServe references replaced with AgentLean's actual FastAPI setup.*

### What Docker Is

Docker packages your application and everything it needs to run — Python version, library versions, OS configuration — into a single portable unit called a **container**. The same container runs identically on your laptop, a production Azure VM, or Azure Container Apps.

The problem it solves:
```
Without Docker:
  "It works on my machine" — different Python versions, different library versions
  across environments cause silent breakage

With Docker:
  One container = one guaranteed environment
  Build once, run anywhere, always identical
```

---

### The Three Core Concepts

**Image** — the blueprint (read-only template describing what is in the container)

**Container** — a running instance of an image. Multiple containers can run from the same image simultaneously and independently.

**Dockerfile** — the recipe that builds the image:

```dockerfile
# Agent Improve Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY agent-improve/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY agent-improve/ .

# Credentials NEVER baked into the image — injected at runtime
# AZURE_OPENAI_KEY, AZURE_SEARCH_API_KEY, LANGCHAIN_API_KEY
# from Azure Key Vault or container environment settings

EXPOSE 8020

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8020"]
```

---

### AgentLean's Four-Container Production Architecture

When all three agents are complete:

```
Agent Resolve container      (port 8010)  ← independent, isolated
Agent Improve container      (port 8020)  ← independent, isolated
Agent Flow container         (port 8030)  ← independent, isolated
AgentLean MCP Server container (port 8001) ← shared by all three agents
```

**Container isolation benefits:**
- If Agent Improve crashes, Agent Resolve keeps running — separate processes
- Update Agent Improve v2.1 by swapping its container — Resolve and Flow unaffected
- Roll back by switching back to the previous container image
- Each agent's dependencies are isolated — no library version conflicts between agents

---

### Three AgentLean-Specific Docker Rules

**Rule 1 — Never bake credentials into the image:**
```dockerfile
# WRONG — credential in image layer, visible to anyone with the image
ENV AZURE_OPENAI_KEY="sk-..."

# CORRECT — injected at runtime from Azure Key Vault or container env settings
# docker run -e AZURE_OPENAI_KEY=$KEY agent-improve
# or via Azure Container Apps secrets management
```

**Rule 2 — One container per agent:**
Agent Resolve, Agent Improve, and Agent Flow each get their own container. Separate containers = separate scaling, separate deployments, separate crash isolation.

**Rule 3 — MCP server as a separate container:**
The AgentLean MCP Server (Section 63) runs as its own container, not bundled with any agent. All three agent containers connect to it. This enables the MCP server to be updated independently and scaled separately from the agents.

---

### The Critical STDIO → HTTP Transport Shift

This is the one architectural change Docker forces on AgentLean's MCP design, already flagged in Section 59 but now explicit:

```
Development (same machine, no containers):
  Agent process → STDIO → MCP server subprocess
  Works because they share the same OS process namespace

Production (separate Docker containers):
  Agent container → CANNOT use STDIO → different container, different host
  Must use HTTP (Streamable HTTP transport)
  Agent container → HTTP port 8001 → MCP server container
```

```python
# Development (Section 59's STDIO pattern)
mcp.run()   # default STDIO

# Production (after containerisation)
mcp.run(transport="http", host="0.0.0.0", port=8001)
```

The agent's MCP client configuration changes accordingly:

```python
# Development
mcp_client = MCPClient(transport="stdio", command=["python", "mcp_server.py"])

# Production
mcp_client = MCPClient(transport="http", url="http://agentlean-mcp:8001/mcp")
```

The `agentlean-mcp` hostname resolves within Docker's internal network to the MCP server container. No external internet exposure needed — container-to-container communication stays internal.

---

### Docker vs Kubernetes — When You Need Each

```
Docker alone (AgentLean current scale):
  A handful of concurrent DMAIC projects
  Manual container management acceptable
  One instance of each agent container

Kubernetes (AgentLean at scale):
  Many concurrent Belts across multiple organisations
  Automatic horizontal scaling (5 Agent Improve instances under load)
  Automatic restart of crashed containers
  Traffic routing and load balancing
  Health checks and self-healing
  Not needed now — relevant when AgentLean has significant concurrent usage
```

---

### The Deployment Workflow — LangServe References Replaced

The course described this workflow using LangServe. The correct workflow for AgentLean:

```
1. Agent development
   LangGraph graph + FastAPI routes (or langgraph.json if using LangGraph Server)

2. Service wrapping
   FastAPI (current) or LangGraph Server (Section 72 option)
   NOT LangServe (archived May 2026, Section 55)

3. Dockerfile creation
   As shown above — python:3.11-slim base, requirements, code, port, CMD

4. Environment setup
   .env stays on disk, never in image
   Azure Key Vault for production secrets
   Container environment variables for non-secret config

5. Local validation
   docker build -t agent-improve .
   docker run -p 8020:8020 --env-file .env agent-improve
   Confirm /health endpoint responds before pushing to production

6. Production deployment
   Azure Container Apps (simplest for AgentLean's current scale)
   or Docker Compose for all four containers together
   or Kubernetes when scale demands it
```

### Gap Register Note
No new gap number — containerisation is an operational deployment concern, not an architectural gap in Agent Improve's design. The STDIO → HTTP transport shift is the only architectural consequence, and it was already flagged in Section 59's transport decision table. The four-container architecture above should be used as the production deployment reference in ARCHITECTURE_v2_DRAFT.md.

---

## 77. AgentLean Frontend Feedback Requirements

*Source: Edureka Course 4 Module 3, "Streamlit Interface for AI Resume Screening" demonstration. Domain-specific content removed — six framework-agnostic UI feedback patterns extracted and mapped to AgentLean's coaching interface.*

These are frontend requirements that emerge directly from the agent architecture. They should inform the design of AgentLean's coaching interface regardless of which frontend technology is used.

---

### Pattern 1 — Immediate Spinner With Context

When the Belt sends a message, show feedback immediately with context — not just a generic loading indicator:

```
Generic (bad):    "Loading..."
Contextual (good): "Coaching in progress — retrieving methodology..."
                   "Validating your root cause against Six Sigma standards..."
                   "Checking gate completeness..."
```

The message tells the Belt what the system is doing, setting appropriate expectations for latency. A multi-hop retrieval turn (Section 71) takes longer than a simple coaching response — the spinner message can reflect which operation is running.

---

### Pattern 2 — Connection Status Before First Interaction

The Belt should see system health before sending their first message:

```
Status panel (shown on session load):
  ✅ Azure OpenAI — connected
  ✅ Knowledge base — ready
  ✅ Case index — ready
  📋 Session: IMPR-2026-E9D
  📊 Phase: Analyse (3 of 5)
  🔢 Fields captured: 11 of 14
```

A Belt who opens the coaching interface and immediately sees "Azure OpenAI — disconnected" knows to wait before starting. Without this, the first coaching turn fails with a confusing error and the Belt does not know why.

---

### Pattern 3 — Extracted Fields Transparency Before Gate Review

Before asking the Belt to approve a gate, show them what was extracted in a readable, expandable section:

```
Expandable: "Review captured Define fields"
  ┌─────────────────────────────────────────────┐
  │ what:     Complaint rate exceeding 8.3%     │
  │           in billing calls                  │
  │ why:      Customer satisfaction impacting   │
  │           NPS score and retention           │
  │ scope:    Billing call centre, Mon-Fri 9-17 │
  │ team:     Vassilis (BB), Maria (Sponsor),   │
  │           3 team members                    │
  │ how_goal: Reduce rate by 50% by Q3 2026     │
  └─────────────────────────────────────────────┘
  [Edit fields] [Approve and advance to Measure →]
```

This is the HITL review step from Gap 2, made concrete in UI terms. The Belt verifies accuracy before the gate commits — not after. Any field they correct triggers Section 38's conflict resolution and Gap 21's feedback adaptation signal.

---

### Pattern 4 — Completeness Score as Visual Signal

`completeness_score` already exists in `DMAICState`. Surface it visually at the gate review step:

```
Completeness: ████████░░  80%

  ✅ what — problem statement confirmed
  ✅ why — business impact confirmed
  ✅ scope — process boundary confirmed
  ✅ team — Belt and sponsor confirmed
  ⚠️  how_goal — SMART goal needs timeline

  "One field still needs attention before advancing."
```

Color coding:
```
> 90%  → green  → "Ready to review gate"
60-90% → amber  → "N fields still needed"
< 60%  → red    → "Several key fields missing"
```

The Belt gets an instant read before reading the detailed field list. The visual score also sets the right expectation — 80% means "almost there," not "failed."

---

### Pattern 5 — Direct LangSmith Trace Link

Provide a direct link from the coaching interface to the LangSmith trace for the current session:

```
[View session trace in LangSmith →]
```

For enterprise customers this provides audit transparency — the sponsor can review exactly what coaching decisions were made and why. For development and debugging, one click from the Belt's conversation to the full execution trace eliminates the need to manually search LangSmith for the right trace.

Implementation: each coaching turn generates a LangSmith run URL. Store it in state or return it in the API response alongside the coaching text.

---

### Pattern 6 — Gate Completion Confirmation With Next Steps

After a gate passes, show a clear confirmation with what happens next:

```
✅ Define phase complete

Your problem statement, scope, team, and goal have been confirmed
and saved to your project record.

Next: Measure phase
  We will establish your process baseline and validate your
  measurement system before identifying root causes.

[Begin Measure phase →]

📊 Progress saved | 🔍 View trace | ⬇️ Download Define summary
```

The Belt always knows:
- What just happened (gate passed, what was committed)
- What comes next (next phase and what it involves)
- That their work is saved
- How to access the audit trail

Never leave the Belt on a blank screen after a significant event.

---

### Implementation Note

These six patterns are frontend requirements — they define what the coaching interface must show, not how it is technically built. They apply equally to the current AgentLean website frontend, a Streamlit prototype, or any future mobile interface.

The agent architecture already produces all the data these patterns need:
- `completeness_score` → Pattern 4
- `captured_fields` → Pattern 3
- `current_phase` and `gate_passed` → Patterns 2 and 6
- LangSmith run ID → Pattern 5
- Node execution events via SSE → Pattern 1

The frontend just needs to surface what the agent already knows.

### Gap Register Note
No new gap number — these are frontend design requirements, not architectural gaps in the agent. Record them as input to the AgentLean frontend design conversation when the UI is being built or redesigned. The agent architecture already produces every data point these patterns require.

---

## 78. Menu-Driven Developer Orchestration — A Pattern from the MCP Demo

*Source: Edureka Course 4 Module 1, "Orchestrating the Full MCP Workflow" (main.py demonstration). This is a small but genuinely useful pattern for AgentLean's development experience — not captured elsewhere in this document.*

### The Pattern

Rather than requiring developers to remember multiple commands (`docker up`, `python mcp_server.py`, `python client.py`, `curl` for health checks), wrap the full development lifecycle in a single command-line menu that guides the user through it:

```
========================================
  AgentLean Development Menu
========================================
1. Check prerequisites (Python version, dependencies, credentials)
2. Start Agent Improve dev server (uvicorn on 8020)
3. Start AgentLean MCP server (STDIO or HTTP)
4. Run evaluation suite (Section 75)
5. Check LangSmith connectivity
6. Run integration smoke test
7. Exit
========================================
```

### Why It Matters for AgentLean

Two specific pain points this solves:

**Pain point 1 — `start.ps1` was permanently destructive:** the current PowerShell startup script hard-resets to `origin/main` on every run (documented in Vassilis's memory). A menu-driven orchestrator replaces it with explicit, opt-in actions — no accidental destructive operations.

**Pain point 2 — Multiple terminals become confusing during three-agent development:** when Agent Resolve (8010), Agent Improve (8020), and the MCP server all need to be running, a menu with clear "start X" options is far less error-prone than remembering which script is where.

### The Prerequisite Validation Layer — Directly Useful

The demo's `check_prerequisites()` function is the pattern that maps directly onto Section 1's fail-fast validation:

```python
def check_prerequisites() -> bool:
    """Verify Python version, packages, files, and credentials before doing work."""

    issues = []

    # Python version
    if sys.version_info < (3, 11):
        issues.append(f"Python 3.11+ required, found {sys.version}")

    # Required packages
    required_packages = ["langgraph", "langchain", "azure-search-documents", "openai"]
    for pkg in required_packages:
        try:
            __import__(pkg.replace("-", "_"))
        except ImportError:
            issues.append(f"Missing package: {pkg}")

    # Required files
    required_files = [
        "agent-improve/backend/graph.py",
        "agent-improve/backend/app.py",
        "agent-improve/.env",
    ]
    for f in required_files:
        if not os.path.exists(f):
            issues.append(f"Missing file: {f}")

    # Credentials (fail-fast pattern from Section 1)
    required_env = ["AZURE_OPENAI_KEY", "AZURE_SEARCH_API_KEY", "LANGCHAIN_API_KEY"]
    for key in required_env:
        if not os.getenv(key):
            issues.append(f"Missing environment variable: {key}")

    if issues:
        print("PREREQUISITES FAILED:")
        for issue in issues:
            print(f"  ✗ {issue}")
        return False

    print("All prerequisites verified ✓")
    return True
```

### The Key Insight — MCP Infrastructure and AI Readiness Are Decoupled

The course demo makes one specific point that is worth preserving: even without `LANGCHAIN_API_KEY` (LangSmith), the MCP server itself can run and be tested with direct tool calls. Even without `AZURE_OPENAI_KEY`, the MCP server responds to `search_knowledge` calls (they will fail Azure Search auth, but the MCP layer works).

This separation is useful for debugging: if a coaching turn fails, you can isolate whether the failure is at the MCP layer (Section 63), the Azure OpenAI layer (Section 67 exception mapping), or the LangGraph layer (Section 44 subgraph routing). A menu-driven orchestrator that lets you test each layer independently accelerates that diagnosis.

### Gap Register Note
No new gap number — this is a developer experience pattern that should be adopted as part of the pre-refactor tooling setup. Replaces the destructive `start.ps1` with an explicit, opt-in orchestrator. Suggest building this alongside the eval suite from Section 75, before Step 3.1 of the refactor resumes.

---

## 79. LangGraph 1.2 Native Reliability Primitives — Per-Node Timeouts, Error Handlers, DeltaChannel

*Source: LangChain official changelog (docs.langchain.com/oss/python/releases/changelog), LangGraph 1.2 release May 11, 2026. Verified against docs and multiple independent 2026 sources.*

### What Changed

LangGraph 1.2 (May 11, 2026) added three production-grade reliability primitives that are now **built into LangGraph itself** — no custom implementation needed. Several concepts previously documented as custom patterns in Sections 49 and 66 are now framework-native.

---

### 1. Per-Node Timeouts — `add_node(timeout=)`

```python
from langgraph.graph import StateGraph
from langgraph.types import TimeoutPolicy

builder.add_node(
    "phase_executor",
    phase_executor_fn,
    timeout=TimeoutPolicy(
        run_timeout=30,    # Hard wall-clock limit per attempt
        idle_timeout=10,   # Resets on progress
    )
)
```

**Semantics:**
- When limit fires, LangGraph raises `NodeTimeoutError`
- Writes from that attempt are cleared
- Hands off to the retry policy
- **Async nodes only** — this is a hard constraint

**Applied to Agent Improve:** every phase executor node should have a `run_timeout` set. A coaching turn that takes >60 seconds is degraded experience regardless of eventual success. Setting `run_timeout=45` means the fallback chain (Section 67) fires before the Belt notices the delay.

---

### 2. Node-Level Error Handlers — `add_node(error_handler=)`

```python
from langgraph.graph import StateGraph
from langgraph.types import Command, NodeError

def define_error_recovery(error: NodeError, state: DefineState) -> Command:
    """Called after all retries exhausted for define_executor."""
    return Command(
        update={
            "extraction_error": str(error),
            "extraction_incomplete": True,
            "partial_fields": state.get("captured_fields", {}),
        },
        goto="degraded_coaching_response"
    )

builder.add_node(
    "define_executor",
    define_executor_fn,
    error_handler=define_error_recovery
)
```

**Semantics:**
- Receives typed `NodeError` after all retries exhausted
- Returns `Command` to update state and route to a different node
- **Purpose-built for Saga/compensation patterns**

**This directly changes Section 49's Saga implementation.** Section 49 documented Saga as a custom pattern. LangGraph 1.2 provides native support — the compensating action IS the `error_handler`, and the routing to it is automatic. Rewrite Section 49's pattern to use `error_handler=` rather than custom compensating nodes.

---

### 3. Graceful Shutdown — `RunControl.request_drain()`

```python
from langgraph.types import RunControl

# From another thread — e.g. Ctrl+C handler, deployment shutdown
control = RunControl(config)
control.request_drain()
# Current run raises GraphDrained after current superstep completes
# Checkpoint is saved — resumable with the same config later
```

**Semantics:**
- Stop in-flight run cooperatively after current superstep
- Save resumable checkpoint
- Run raises `GraphDrained`
- Can be resumed with the same config

**Applied to Agent Improve:** during deployment rollouts or `Ctrl+C` shutdowns, mid-coaching sessions are not lost. The Belt returns and the coaching resumes from exactly where the drain happened. This is production-grade session preservation that would otherwise require custom code.

---

### 4. DeltaChannel (beta) — Checkpoint Overhead Reduction

**Problem it solves:** as DMAIC projects grow across many sessions, checkpoint size grows because each checkpoint re-serializes the full accumulated state. For a 6-week DMAIC project with hundreds of coaching turns, this becomes significant.

**How it works:** `DeltaChannel` stores only the incremental delta at each step rather than re-serializing the full accumulated value. Configurable `snapshot_frequency` bounds rebuild latency.

```python
from langgraph.channels import DeltaChannel

# In state definition
class DMAICState(TypedDict):
    messages: Annotated[list, DeltaChannel(snapshot_frequency=50)]
    # every 50 steps, a full snapshot is written
    # steps in between store only deltas
```

**When to enable for AgentLean:**
- Not needed during v2.1 refactor initial rollout
- Enable when a real DMAIC project accumulates >200 coaching turns
- The trade-off: rebuild latency (small) vs storage growth (significant over weeks)

---

### Cross-Reference Impact on Existing Sections

| Existing Section | Change Required |
|---|---|
| Section 49 (Saga) | Rewrite implementation to use `error_handler=` — pattern still valid, mechanism is now native |
| Section 66 (Failure pipeline) | Add per-node timeouts as Step 0 (before retries fire) |
| Section 67 (Fallback chain) | Wrap top-level LLM calls in `TimeoutPolicy` — fallback fires on timeout, not just exceptions |
| Section 52 (Checkpointer + BaseStore) | Add DeltaChannel note as future optimization for long-lived DMAIC projects |

### Gap Register Note
No new gap number — Sections 49 and 66 gap closures are UPDATED. LangGraph 1.2 provides native primitives that replace custom Saga and timeout patterns. Rewrite implementation approach during v2.1 refactor. Requires LangGraph >= 1.2.6 (verified current pinned version).

---

## 80. LangChain 1.0 AgentMiddleware — The Six Hooks Foundation

*Source: LangChain official reference (reference.langchain.com/python/langchain/agents/middleware/types/AgentMiddleware), LangChain 1.0 GA October 22, 2025, LangChain 1.1 December 2, 2025. Verified against docs and multiple independent 2026 sources.*

### Why This Section Exists

Section 42 documented RubricMiddleware and Section 48 introduced middleware conceptually. Neither section documented the **six hooks that all middleware — built-in AND custom — is built from**. Understanding these primitives is essential before the v2.1 refactor writes any custom middleware for Agent Improve.

---

### The Six Middleware Hooks

The core agent loop calls a model, lets it choose tools, and finishes when no more tools are called. Middleware exposes hooks before and after each of those steps:

| Hook | When It Fires | Typical Use |
|---|---|---|
| `before_agent` | Once on invocation | Load memory, validate input, connect resources |
| `before_model` | Before each model call | Trim history, redact PII, inject context |
| `wrap_model_call` | Wraps whole model call | Caching, retries, dynamic model swap |
| `wrap_tool_call` | Wraps tool execution | Inject context, intercept results, gate tools |
| `after_model` | After model responds, before tools run | HITL approval, output validation |
| `after_agent` | Once at completion | Persist results, cleanup, audit |

Multiple middleware compose with **first defined = outermost layer**.

---

### Implementation Patterns

**Pattern A — Decorator-based (simple, stateless):**
```python
from langchain.agents.middleware import before_model, after_model

@before_model
def log_before_model(state, runtime):
    print(f"[LOG] About to call model with {len(state['messages'])} messages")
    return None

@after_model
def log_after_model(state, runtime):
    print(f"[LOG] Model returned: {state['messages'][-1].content[:100]}")
    return None
```

**Pattern B — Class-based (stateful, complex):**
```python
from langchain.agents.middleware import AgentMiddleware

class GateValidationMiddleware(AgentMiddleware):
    """Custom middleware for Agent Improve gate validation."""

    def __init__(self, gate_rubric: dict):
        self.gate_rubric = gate_rubric
        self.failure_count = 0

    def before_model(self, state, runtime):
        return {"context_note": "Gate review imminent"}

    def after_model(self, state, runtime):
        if self._detects_gate_readiness(state):
            return {"gate_check_pending": True}
        return None
```

**Pattern C — `wrap_model_call` (retry, fallback, model swap):**
```python
from langchain.agents.middleware import wrap_model_call

@wrap_model_call
def azure_fallback_wrapper(request, handler):
    """Retry with backup model on primary failure."""
    try:
        return handler(request)
    except (RateLimitError, APIStatusError):
        request.model = "operational-model"
        return handler(request)
```

---

### Built-in Middleware Available Out-of-the-Box

These are provided by LangChain — no custom implementation needed:

| Middleware | Hook Used | Purpose |
|---|---|---|
| `SummarizationMiddleware` | `before_model` | Context overflow — summarize when approaching token limits |
| `HumanInTheLoopMiddleware` | `after_model` | Interrupt tool calls for human approval (Section 53) |
| `PIIMiddleware` | `before_model`, `after_model` | Mask/redact/hash PII in inputs/outputs/tool results |
| `ModelRetryMiddleware` | `wrap_model_call` | Retry with configurable exponential backoff (added in 1.1) |
| `LLMToolSelectorMiddleware` | `wrap_model_call` | Dynamically narrow tool list — fast LLM picks which tools to bind |

**Agent Improve should use built-in middleware wherever possible** — do not reimplement what LangChain already provides. Custom middleware should be reserved for genuinely domain-specific logic (DMAIC gate detection, phase transition rules).

---

### The Composition Order Rule

```python
agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[
        PIIMiddleware(),
        SummarizationMiddleware(),
        ModelRetryMiddleware(retries=3),
        HumanInTheLoopMiddleware(...),
        GateValidationMiddleware(...)
    ]
)
```

Middleware compose like nested wrappers. First in the list is the outermost layer. This ordering matters — PII redaction MUST fire before summarization sees the content, or PII leaks into summaries.

---

### Cross-Reference Impact on Existing Sections

| Existing Section | Update Needed |
|---|---|
| Section 42 (RubricMiddleware) | Note that RubricMiddleware is one of many — it uses `after_model` hook internally |
| Section 48 (three-prompt separation) | The three prompts can now be implemented as three middleware layers rather than three explicit prompt calls |
| Section 53 (HumanInTheLoopMiddleware) | Confirmed built-in — no custom implementation needed |
| Section 66 (failure handling) | `ModelRetryMiddleware` replaces custom retry code |

### Gap Register Note
No new gap number — this section provides the foundation understanding required to correctly implement Sections 42, 48, and 53 during the v2.1 refactor. Read this before writing any custom middleware. Prefer built-in middleware; only write custom when domain-specific.

---

## 81. LangChain 1.0 Standard Content Blocks — Typed Model Responses

*Source: LangChain official docs (docs.langchain.com/oss/python/releases/langchain-v1), LangChain 1.0 GA October 22, 2025. Verified against docs and multiple independent 2026 sources.*

### What Changed

Before LangChain 1.0, `response.content` was a single opaque string. Parsing reasoning traces, citations, tool calls, and text out of it required provider-specific string parsing that broke when switching models.

LangChain 1.0 introduced `response.content_blocks` — a **provider-agnostic typed list** that works consistently across OpenAI, Anthropic, Google, and other providers.

---

### The Content Block Types

```python
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-sonnet-4-6")
response = model.invoke("Analyse this DMAIC case")

for block in response.content_blocks:
    if block["type"] == "text":
        print(f"Response: {block['text']}")

    elif block["type"] == "reasoning":
        print(f"Reasoning: {block['reasoning']}")

    elif block["type"] == "tool_call":
        print(f"Tool: {block['name']}({block['args']})")

    elif block["type"] == "citation":
        print(f"Cited: {block['url']} at chars {block['start_index']}-{block['end_index']}")
```

---

### Why This Matters for Agent Improve

**Two specific advantages** directly relevant to the v2.1 refactor:

**1. Reasoning traces become first-class data.**
When Agent Improve coaches on a complex root cause validation (Section 71's multi-hop pattern), the model's reasoning is now inspectable. This can be:
- Logged to LangSmith automatically via `@traceable`
- Stored in `step_log` for audit trails
- Analysed later for coaching quality patterns

Before LangChain 1.0, extracting reasoning required parsing model-specific string formats. Now it's a typed field.

**2. Citations for methodology retrieval.**
When Agent Improve's coaching response is grounded in the Black Belt eBook (Section 63's `search_knowledge`), the model can now return citations as typed blocks. This closes Gap 33 (knowledge source traceability in coaching responses) — cited sources appear as structured data, not embedded in prose that must be regex-parsed.

```python
# Belt asks: "How do I validate this root cause?"
# Agent Improve returns:
{
  "text": "Validate the root cause using hypothesis testing...",
  "citations": [
    {"url": "black_belt_ebook.pdf", "page": 47, "start_index": 12, "end_index": 89}
  ],
  "reasoning": "The Belt provided a root cause that requires statistical validation..."
}
```

---

### Backward Compatibility

`response.content` still works — it's now derived from `content_blocks`. Existing code that reads `response.content` as a string continues to function. **New code should read `content_blocks`** to get typed access.

---

### Cross-Reference Impact on Existing Sections

| Existing Section | Update Needed |
|---|---|
| Section 44 (typed Pydantic boundaries) | Extend to LLM response boundary — no more parsing `response.content` strings |
| Section 71 (multi-hop retrieval) | Store reasoning traces per hop for auditability |
| Gap 33 (knowledge source traceability) | CLOSED via citation content blocks — implement during v2.1 refactor |

### Gap Register Update
**Gap 33 — CLOSED.** Knowledge source traceability now provided by LangChain 1.0 typed citation content blocks. Implement citation reading in Phase Executor nodes during v2.1 refactor.

---

## 82. LangChain 1.0 ProviderStrategy — Native Structured Output

*Source: LangChain official reference (reference.langchain.com/python/langchain/agents/structured_output/ProviderStrategy), LangChain 1.1 December 2, 2025. Verified against docs.*

### What Changed

Previously, structured output from `create_agent` required an additional LLM call after the main loop — expensive and slow. LangChain 1.1 integrated structured output into the main model-tools loop.

Two strategies now available:

**`ToolStrategy`** — model uses tool calling to produce structured output (works across all providers)
**`ProviderStrategy`** — model uses provider-native structured output (OpenAI, Anthropic native JSON mode)

```python
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
from pydantic import BaseModel

class DefineOutput(BaseModel):
    problem_statement: str
    baseline_metric: float
    scope: str

# Option A — ToolStrategy (universal, works everywhere)
agent = create_agent(
    "gpt-4o",
    tools=[retrieve_methodology, extract_fields],
    response_format=ToolStrategy(DefineOutput),
    prompt="Coach the Belt through the Define phase."
)

# Option B — ProviderStrategy (native, more efficient where supported)
agent = create_agent(
    "gpt-4o",
    tools=[retrieve_methodology, extract_fields],
    response_format=ProviderStrategy(DefineOutput),
    prompt="Coach the Belt through the Define phase."
)
```

**ProviderStrategy advantages:**
- Native structured output — model returns JSON directly, no extra call
- Latency reduction — one round-trip instead of two
- Cost reduction — no additional LLM invocation
- **Inferred from model profiles in LangChain 1.2** — can be applied automatically when model supports it

**When to use which:**
- `ProviderStrategy` when using OpenAI, Anthropic, or other providers with native JSON mode
- `ToolStrategy` when using models without native JSON mode
- LangChain 1.2 can infer the choice automatically via `.profile` attribute

---

### Applied to Agent Improve

The Define phase currently uses `.with_structured_output(DefineOutput)` which creates a separate LLM call. Switching to `ProviderStrategy` during v2.1 refactor:

```python
define_agent = create_agent(
    "operational-premium",
    tools=[
        retrieve_methodology,
        search_similar_cases,
        extract_define_fields
    ],
    response_format=ProviderStrategy(DefineOutput),
    middleware=[
        HumanInTheLoopMiddleware(interrupt_on={"advance_to_measure": True}),
        RubricMiddleware(rubric=define_gate_rubric, max_iterations=3),
    ],
    prompt=DEFINE_COACHING_PROMPT
)
```

Every phase subagent gets typed output with no additional LLM cost.

---

### Cross-Reference Impact on Existing Sections

| Existing Section | Update Needed |
|---|---|
| Section 44 (typed boundaries) | Prefer `ProviderStrategy` over `.with_structured_output()` for `DefineOutput`, `MeasureOutput`, etc. |
| Section 42 (RubricMiddleware) | RubricMiddleware works with both strategies |

### Gap Register Note
No new gap number — architectural refinement for the v2.1 refactor. Reduces latency and cost for every gate transition without changing the graph structure.

---

## 83. Agent Skills Specification — SKILL.md Standard

*Source: LangChain official docs (docs.langchain.com/oss/python/deepagents/skills), agentskills.io specification, LangChain Skills repository (github.com/langchain-ai/langchain-skills). Verified May-June 2026.*

### What Changed

Section 26 introduced Skills conceptually as part of AgentLean's governance framework. Since Section 26 was written, an **official Agent Skills specification** has emerged at agentskills.io, adopted by LangChain, Claude Code, Cursor, and other agent frameworks.

This section documents the current standard so AgentLean skills conform to it and remain portable across tools.

---

### The SKILL.md Standard

Each skill is a directory containing a `SKILL.md` file:

```yaml
---
name: dmaic-define-phase
description: Use this skill when coaching a Black Belt through the DMAIC Define phase. Fetch problem statement templates, scope definition patterns, and SMART goal validation criteria.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index
metadata:
  author: valuesims/agentlean
  version: "1.0"
allowed-tools: search_knowledge, search_cases, extract_fields
---

# DMAIC Define Phase Coaching Skill

## Overview
This skill guides coaching for the Define phase of DMAIC projects.

## Instructions

### 1. Assess Belt's current input

### 2. Retrieve methodology grounding
Use search_knowledge with phase="define"

### 3. Validate against SMART criteria
```

**Frontmatter fields:**
- `name` — required, kebab-case identifier
- `description` — required, keyword-rich for LLM routing (see below)
- `license` — recommended (MIT for open sharing)
- `compatibility` — free-text environmental requirements
- `metadata` — arbitrary structured metadata
- `allowed-tools` — comma-separated tool names the skill uses

---

### The Description Field — Most Critical Text in the System

The `description` field is what the LLM sees at startup to decide when to load the skill. It should be:

**Keyword-rich** — mention every scenario, phrasing, and context where the skill triggers
**Specific** — mention exact trigger phrases like "coaching", "Define phase", "problem statement"
**Slightly pushy** — overstate when to use the skill so the LLM errs on the side of using it

Poor description → wrong skill selected → wrong coaching. This is the single most important thing to get right when creating skills.

---

### Three Storage Backends

deepagents supports three backends for skill storage:

| Backend | Storage | Use Case |
|---|---|---|
| `StateBackend` | LangGraph agent state for current thread | Ephemeral, per-session |
| `StoreBackend` | LangGraph store for durable cross-thread | Persistent skills across sessions |
| `FilesystemBackend` | Disk under configurable `root_dir` | Standard for development, git-versioned |
| `ContextHubBackend` | LangSmith Hub agent repo | Version history via Hub commits |

For AgentLean during v2.1 refactor: **`FilesystemBackend` under `agent-improve/skills/`**. This keeps skills git-versioned alongside the code and works with Claude Code's SKILL.md discovery.

---

### The Progressive Disclosure Pattern

Skills solve context bloat via progressive disclosure:

```
Level 1 — Startup (always loaded):
  Skill descriptions only (frontmatter)
  Small — under 2K tokens for 20 skills
  Model sees: "I have skills for A, B, C..."

Level 2 — Skill loaded on demand:
  Full SKILL.md instructions
  Loaded when the agent decides the skill applies

Level 3 — Reference files loaded on demand:
  Additional files referenced by the SKILL.md
  Loaded only when explicitly needed
```

**Applied to Agent Improve:** each of the five DMAIC phases becomes a skill. Startup loads 5 descriptions. When the Belt is in the Analyse phase, only the Analyse skill's full instructions load. This dramatically reduces context bloat vs current pattern of stuffing all phase methodology into system prompt.

---

### Cross-Reference Impact on Existing Sections

| Existing Section | Update Needed |
|---|---|
| Section 26 (Skills/Hooks governance) | Framework confirmed — now follows agentskills.io spec |
| Section 27 (`/verify-current-version`) | Should be implemented as a skill following this spec |
| Section 42 (system prompt bloat) | Skills solve this — implement during v2.1 refactor |

### Gap Register Note
No new gap number — this section formalises the specification that Section 26's governance framework should follow. Section 26 was conceptually correct but predates the formal spec. Skills should be authored in this format from v2.1 onward.

---

## 84. SkillsMiddleware in deepagents — Solving System Prompt Bloat

*Source: LangChain official reference (reference.langchain.com/python/deepagents), deepagents 0.6.10 May 2026. Verified against docs.*

### What Changed

Section 42's RubricMiddleware discussion mentioned system prompt bloat as a problem but did not resolve it. deepagents' `SkillsMiddleware` (part of the Deep Agents harness) is the direct solution.

### How It Works

```python
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend

agent = create_deep_agent(
    model="operational-premium",
    backend=FilesystemBackend(root_dir="./agent-improve/skills/"),
    skills=[
        "./agent-improve/skills/dmaic-define/",
        "./agent-improve/skills/dmaic-measure/",
        "./agent-improve/skills/dmaic-analyse/",
        "./agent-improve/skills/dmaic-improve/",
        "./agent-improve/skills/dmaic-control/",
    ],
    tools=[search_knowledge, search_cases, extract_fields],
    middleware=[
        HumanInTheLoopMiddleware(interrupt_on={"advance_phase": True}),
        RubricMiddleware(),
    ]
)
```

At startup, `SkillsMiddleware`:
1. Reads all SKILL.md frontmatter (Level 1 disclosure — descriptions only)
2. Adds a compact summary to the system prompt
3. Registers `load_skill(name)` as a tool the agent can call
4. When agent calls `load_skill("dmaic-analyse")`, the full instructions load into context (Level 2)

### Cross-Reference Impact

| Existing Section | Update Needed |
|---|---|
| Section 42 (RubricMiddleware) | Combine with SkillsMiddleware — RubricMiddleware evaluates gate quality, SkillsMiddleware provides phase context |
| Section 44 (architectural refactor) | Skills become the mechanism for phase-specific coaching context, not the graph structure |
| Section 83 (agentskills.io spec) | Implementation companion — this is HOW skills get loaded |

### Gap Register Note
No new gap number — SkillsMiddleware is the concrete implementation of Section 83's progressive disclosure pattern. Use `FilesystemBackend` during v2.1 refactor for git-versioned skills.

---

## 85. LangSmith 2026 Additions — Fleet, Sandboxes, Context Hub, Engine

*Source: LangChain official announcements (Interrupt 2026 conference blog), LangSmith Fleet documentation (langchain.com/langsmith/fleet), multiple independent 2026 sources. Verified March-June 2026.*

### What Changed

Section 1 and Section 75 documented LangSmith as it stood mid-2025 — primarily observability and evaluation. LangSmith has significantly expanded into a full agent engineering platform. This section documents the additions.

---

### 1. LangSmith Fleet (March 2026 — formerly Agent Builder)

**What it is:** No-code agent builder plus enterprise fleet management for organizations running many agents in production.

**Fleet's four capabilities:**
- **Identity and permissions** — role-based access control (viewers, editors, deployers, administrators)
- **Skills-as-service** — skills attachable to any agent in the fleet (open-source Skills ecosystem)
- **Fleet-level observability** — organizational views: which agents have highest error rates, which teams consume most tokens
- **Sharing mechanisms** — cross-team agent reuse without JSON export/import

**Relevance to AgentLean:**

**Not directly needed during v2.1 refactor** — Fleet is enterprise-scale multi-agent management. AgentLean has three agents (Resolve, Improve, Flow). Fleet becomes relevant when:
- Multiple customer organizations run AgentLean instances
- Cross-customer governance (permissions, cost tracking) is needed
- Skills are shared across customer deployments

**Honest assessment:** Fleet is a productized version of what your CLAUDE.md governance framework does at the code level. When AgentLean scales to multi-customer, revisit — until then, code-level governance is sufficient and gives more control.

---

### 2. LangSmith Sandboxes (Public Beta, June 2026)

**What it is:** Secure code execution environments for agents. Snapshots, cheap forks via copy-on-write, blueprints for reusable base environments.

**Key features:**
- **Snapshots and forks** — capture sandbox state, fork parallel sandboxes with copy-on-write
- **Blueprints** — refreshable base environments with warmed caches
- **Pause when inactive** — idle sandboxes pause automatically, no charge for unused resources
- **Auth Proxy** — inject credentials at network layer, secrets never enter runtime
- **Sandbox CLI** — manage sandboxes, build snapshots, tunnel TCP

**Relevance to AgentLean:**

Directly useful during the v2.1 refactor for **testing Agent Improve without hitting production Azure**. Set up a sandbox with a mock Azure OpenAI endpoint and mock Azure AI Search, run the eval suite from Section 75 against it, verify no production credentials are consumed during development testing.

Complements Section 76's Docker containerisation — Sandboxes are for testing, containers are for deployment.

---

### 3. Context Hub (June 2026)

**What it is:** Versioned storage for the instructions and policies agents follow. Direct answer to Section 27's `/verify-current-version` concern.

**Key features:**
- Every write is a Hub commit (git-like version history)
- LangSmith-native durability
- No separate LangGraph store needed
- Integrates with `ContextHubBackend` for skill storage

**Relevance to AgentLean:**

For the **living reference document** you plan to build in Cowork, Context Hub is the productized version of what you were considering assembling yourself. When we build the living reference document, Context Hub becomes the storage backend option.

For v2.1 refactor: not needed yet. Skills remain in `FilesystemBackend` under git. Context Hub becomes relevant when AgentLean skills are shared across multiple deployments.

---

### 4. LangSmith Engine (Public Beta, June 2026)

**What it is:** Automated failure pattern detection. Clusters production failures into prioritized issues, finds root cause in traces + code, proposes fixes for review.

**How it works:**
- Reads production traces from LangSmith
- Identifies recurring failure patterns
- Correlates trace patterns with code and prompt changes
- Proposes fixes as PRs

**Relevance to AgentLean:**

**Directly complements Section 75's regression testing.** Section 75 documented reactive regression testing (run evals on every PR). Engine is proactive — it finds failure patterns in production traces before you write tests for them.

Enable Engine once AgentLean has enough production traffic that patterns emerge (>1000 coaching turns/week). For the v2.1 refactor phase, standard LangSmith tracing is sufficient.

---

### 5. Messages View + LLM Gateway + SmithDB

**Messages View:** Multi-turn traces rendered readably at a glance. Fixes the "wall of JSON" problem for long conversations. Automatic — no code changes needed.

**LLM Gateway:** Enforces spend limits and redacts PII **before requests leave your environment**. Alternative to per-call middleware for organizational controls.

**SmithDB:** Purpose-built database backing core LangSmith workloads. Up to 15x faster on core queries. Automatic — no code changes needed.

---

### Cross-Reference Impact on Existing Sections

| Existing Section | Update Needed |
|---|---|
| Section 1 (LangSmith basics) | Note SmithDB, Messages View as automatic upgrades |
| Section 27 (`/verify-current-version` skill) | Context Hub is the productized version — evaluate at multi-deployment stage |
| Section 44 (governance framework) | Fleet is enterprise version — code-level governance sufficient for AgentLean current scale |
| Section 75 (regression testing) | Engine complements — proactive vs reactive |
| Section 76 (Docker) | Sandboxes complement — testing vs deployment |
| Section 78 (developer orchestration) | Sandboxes can replace parts of the menu-driven testing pattern |

### Gap Register Note
No new gap number — LangSmith additions documented for awareness. None are required for v2.1 refactor. Fleet becomes relevant at multi-customer scale; Sandboxes useful during refactor for isolated testing; Context Hub relevant when building the living reference document; Engine when production traffic emerges.
