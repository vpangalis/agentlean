# REFACTORING_AGENT_IMPROVE.md — LangGraph & Multi-Agent Systems
## Agent Improve Refactor Specification and Learning Register

*Derived from EDUCATIONAL.md by applying every ratified decision in `REVIEW_DECISIONS.md`.*
*EDUCATIONAL.md remains untouched as the historical training register.*
*Last updated: July 2026 — 87 sections plus Terminology Reference and §52a.*

---

## Purpose

This document is the **architectural specification for the Agent Improve refactor**. It began as a chronological learning register (EDUCATIONAL.md) capturing concepts from development and coursework. Every section has since been reviewed against the ratified architecture, corrected where superseded, and cross-linked. Sections now fall into four kinds:

- **Ratified design** — the decision is locked and this section describes what gets built.
- **Confirmed aligned** — the section was already correct; only stale details were updated.
- **Knowledge-only** — valuable pedagogy retained deliberately, explicitly *not* a roadmap (all MCP sections, §57–§65, fall here per §39).
- **Historical record** — course assignments and evaluations preserved to document how the thinking arrived where it did.

Where a section records a pattern that has been superseded, the superseding decision is named inline rather than the old text being deleted — the reasoning chain is part of the value.

### How to read this document

| If you are… | Start at |
|---|---|
| New to the vocabulary | **Terminology Reference** (immediately below the Overview Architecture) |
| Implementing the refactor | §44 (blueprint), then §17/§18/§23 (state and subgraphs), then §39 (tools) |
| Wiring retrieval | §32, §33, §34, §37, §40, §71 |
| Wiring validation and gates | §2, §42, §48, §68, §69 |
| Wiring reliability | §49, §66, §67, §79 |
| Planning what comes after the refactor | §87 (Deferred Backlog) |

### Canonical names used throughout

Earlier drafts used placeholder names. The canonical names below are authoritative everywhere in this document:

| Canonical name | What it is |
|---|---|
| `rag_lookup_methodology(query, phase, top_k)` | Retrieval against `improve_knowledge_index`, filtered by `phase_relevance` (§37) |
| `rag_lookup_evidence(query, case_id, top_k)` | Retrieval against `improve_evidence_index`, filtered by `case_id` |
| `rag_lookup_case_history(query, top_k, exclude_current_case=True)` | Retrieval against `improve_case_index` for yokoten |
| `SupervisorState` | Parent orchestration state (§17) |
| `PhaseState` | Per-phase subgraph state, formerly `PlannerState` (§18) |
| `DMAICGraderMiddleware` | Custom rubric grader on `create_agent` (§42) |
| `DMAICGateValidator` | Deterministic field-presence checks (§48) |
| `DMAICSkillsMiddleware` | Custom progressive-disclosure skills middleware (§84) |
| `AzureBlobCheckpointSaver` / `AzureBlobStore` | Persistence during the refactor; `PostgresSaver` / `PostgresStore` post-refactor |
| `case_id` | **The** project identifier — state field, `thread_id`, store namespace segment, blob path, index field (§17) |
| `artifacts` | A phase's captured fields — `PhaseState` field, store namespace, gate document content (§17, §18) |

**Retired names — do not use, in prose or in v2 code:**

| Retired | Use instead | Note |
|---|---|---|
| `project_id` | `case_id` | Only the governance documents ever said `project_id`; code and indexes always said `case_id` (§17) |
| `captured_fields` | `artifacts` | Prose-only name from EDUCATIONAL.md (§17) |
| `phase_inputs` | `artifacts` | v1 code field name, replaced during the refactor (§17) |
| `feedback` (on `PhaseState`) | `belt_edits` or `validator_feedback` | Two different things — Belt corrections vs validation results (§18) |
| `gate_documents` (store namespace) | `artifacts` | Duplicated the same content under a second key (§52a) |

Where a retired name appears below, it is either a quotation of the
course lab, a description of v1 code, or a record of the rename itself.
None of those are usage.

---

## Document Navigation — Reference Guide Structure

*The sections below are grouped into eleven Parts plus an Appendix and appear in the file in this order. The grouping is by what a reader would look up, not by when the material was learned.*

***Section numbers are unchanged.** §1 is still §1, §42 is still §42, §52a is still §52a. Only each section's POSITION in the file has changed, so every `§N` cross-reference — in this document, in `CLAUDE.md`, and in `ARCHITECTURE.md` — continues to resolve. Because the numbers no longer run in file order, use this index or your editor's search rather than scrolling to locate a section.*

*Front matter — Purpose, this index, the Overview Architecture, and the Terminology Reference — stays at the top, ahead of Part 1.*

### Front matter
- **Terminology Reference** — node, subgraph, tool, planner, executor, supervisor, phase subagent, leaf tool; the two-level recursion table. *Read this first.*

### Part 1 — Foundations
*Core concepts a reader needs first.*

- §1 — LangGraph Persistent Checkpointing (`@traceable`, fail-fast validation, diagnostic patterns)
- §2 — Human-in-the-Loop (Interrupts) — the nine-step gate pattern
- §10 — Subagent State Management *(the EDUCATIONAL.md index called this "State Management Patterns")*
- §5 — Planner / Executor Model (two-level cascade, the nested cycle)
- §20 — Supervisor / Worker Architecture — recursive Planner-Executor pairs
- §23 — Modular Subgraph Architecture
- §11 — Recursive Planner / Executor — Every Level Plans *(the EDUCATIONAL.md index called this "Phase Planner and Phase Executor")*

### Part 2 — Agent Construction
*How the coach is built.*

- §82 — LangChain 1.0 ProviderStrategy — native structured output
- §80 — LangChain 1.0 AgentMiddleware — the six hooks foundation
- §81 — LangChain 1.0 Standard Content Blocks — typed model responses
- §42 — `DMAICGraderMiddleware` — self-evaluation and correction loop; subjective quality evaluation, temperature discipline
- §83 — Agent Skills Specification (SKILL.md standard)
- §84 — SkillsMiddleware in deepagents → the custom `DMAICSkillsMiddleware` *(also Part 8)*
- §36 — Short-Term and Long-Term Vector Memory (`SummarizationMiddleware`)
- §38 — Hybrid Memory Stack and Context Orchestration Layer — decomposed into three small additions

### Part 3 — Retrieval Architecture
*How knowledge is found.*

- §32 — **Multi-Query Retrieval** *(the section the EDUCATIONAL.md index mislabelled as §28)*
- §33 — RAG Fusion (RRF, canonical `rag_lookup_*` implementation)
- §34 — Multi-Hop Reasoning (5-hop cap via `RemainingSteps`)
- §71 — Multi-Hop Retrieval — Gap 17 formally CLOSED
- §35 — Query Voting and Weighted Fusion *(knowledge-only, comparative)*
- §37 — Memory Patterns in Agentic Systems (taxonomic scaffold)
- §40 — Metadata as a Signal — freshness, authority, context
- §41 — Target Retrieval Pipeline — system-level workflow

### Part 4 — Quality and Validation
*How output is checked.*

- §48 — Reflection Nodes vs Consensus Modeling + three-prompt separation + `DMAICGateValidator`
- §68 — Decision Validation Against Business Constraints (the four-layer stack)
- §69 — Validation Layer Placement — firing contexts, the transparency principle
- §29 — OutputFixingParser *(historical — superseded by §82)*
- §22 — Debate Agents and Consensus Voting *(v2.2, Analyse phase — deferred, §87 item 10)*

### Part 5 — Reliability and Failure Handling
- §79 — LangGraph 1.2 Native Reliability Primitives (per-node timeouts, error handlers, DeltaChannel)
- §49 — Saga-Based Transactions and Compensating Actions (**UPDATED by §79 — native `error_handler=`**)
- §66 — Circuit Breaker, Context Recovery, Safe Reopen — the six-step failure pipeline
- §67 — Self-Healing Fallback Chain — complete reference implementation
- §15 — Failure Patterns in Long-Running Agent Workflows *(historical context)*

*Correction: the EDUCATIONAL.md index listed "Section 20 — Fallback Chains" in this category. §20 is Supervisor / Worker Architecture (Part 1). Fallback-chain content lives in §66 and §67.*

### Part 6 — Orchestration and Data Flow
*How phases connect.*

- §17 — InsightForge Mapping — Refactor Specification; `SupervisorState` *(the EDUCATIONAL.md index called this "Recursive Orchestrator Pattern")*
- §18 — Lab Code — `PhaseState` Schema *(renamed from `PlannerState`)*
- §19 — Multi-Step Task Chaining — store-mediated handoff, Level 1 / Level 2 nested cycle
- §21 — State Passing Across Agent Nodes *(renamed from "Message Passing")*
- §70 — Inter-Stage Data Dependency — outputs become inputs
- §52 — MAJOR FINDING — Checkpointer + Store Architecture (the LangGraph 2026 memory split)
- **§52a — AzureBlobStore and Multi-Chain Persistence**

### Part 7 — Deployment and Infrastructure
- §55 — LangServe archived; **decision: stay on FastAPI**
- §72 — LangGraph Server — deployment option *(evaluation record; resolved by §55)*
- §73 — Langfuse — open-source LangSmith alternative *(knowledge for future)*
- §74 — Agent API Versioning *(knowledge for post-launch)*
- §75 — Evaluation Dataset Design and Regression Testing
- §76 — Docker containerisation
- §77 — AgentLean Frontend Feedback Requirements (six UI patterns)
- §78 — Menu-Driven Developer Orchestration (replaces destructive `start.ps1`)

### Part 8 — Governance and Anti-Drift
- §24 — Governance and Debugging — Production Readiness Framework *(the EDUCATIONAL.md index called this "Observer Agent Role"; the Observer Agent is discussed in §43 and deferred in §87)*
- §44 — Consolidated Architecture Diagnosis — Agent Resolve benchmark; **the refactor blueprint**
- §45 — Anti-Drift Governance Design — hooks, skills, staying current (Gap 27 CLOSED; `/verify-current-version` lives here, **not** in §27)
- §50 — CRITICAL VERSION CORRECTIONS *(the EDUCATIONAL.md index called this "Anti-Drift Mechanisms")*
- §53 — MAJOR FINDING — Built-In Middleware; `HumanInTheLoopMiddleware` bug warning, `Command(resume=...)`
- **§86 — Verified Claude Code Hook Mechanics** *(forward-referenced from §45)*
- §43 — Common Agent Roles and Responsibilities

### Part 9 — MCP Knowledge *(not implemented — pedagogical reference)*

**MCP is permanently out of scope for Agent Improve, Agent Resolve, and Agent Flow (§39).** These sections are retained as protocol pedagogy, not as a roadmap. Belts upload their own data; the `@tool` decorator handles all tool composition.

- §57 — Correction: MCP is agent-to-tool, not agent-to-agent
- §58 — Correction: two functional layers, not four
- §59 — MCP Server Implementation — FastMCP, transports, tool design
- §60 — Internal RAG tools vs MCP tools *(retained as **architectural reference** — the internal-tool boundary and the hybrid planner + reactive tool pattern confirm the ratified architecture)*
- §61 — MCP Resources — URI-addressable read-only data
- §62 — MCP Server Ecosystem — third-party servers
- §63 — **MCP evaluated for AgentLean and rejected**, with rationale
- §64 — MCP Production Architecture *(the structured error schema is preserved for Azure services; ratified in §66/§67)*
- §65 — MCP Caching *(cache-key/TTL/invalidation principles feed §67 Level 3 Redis cache)*
- §39 — **Knowledge Tools in Augmented Reasoning** — the MCP-out decision and the 20 computation tools. *Placed last in this Part because it is the section that closes it; §39 is a ratified design section, not MCP pedagogy, and Parts 2, 3, and 5 all depend on it.*

### Part 10 — Course History and Context
*Training record — not operational. Chronological entries kept for continuity.*

- §9 — Coursera / Edureka Multi-Agent Systems notes
- §14 — Course Curriculum Map
- §26 — Orion Intelligence — Graded Assignment Submission *(the EDUCATIONAL.md index called this "Skills and Hooks Governance Framework")*
- §31 — Course 2 Progress Notes
- §56 — Course 4 — stale deployment warning *(resolved by §55)*
- §54 — Correction to Section 42 — RubricMiddleware *(historical; incorporated into the §42 rewrite)*

### Part 11 — Reference
*Patterns, diagrams, taxonomies.*

- §3 — Time Travel Debugging & Snapshot Analysis
- §4 — DAG Execution vs LangGraph Cycles
- §6 — Multi-User Production Gaps *(post-launch scope — Gaps 9–12)*
- §7 — Full Dependency Chain
- §8 — Implementation Sequencing Decision *(rewritten — Option B selected)*
- §12 — From Execution Control to Task Delegation
- §13 — Complete Planner/Executor Flow — full diagram
- §16 — Architectural Debt Acknowledgement *(Option B decision recorded)*
- §25 — Architectural Gaps — Complete Register
- §27 — LCEL Pipelines — scope corrected to node-internal composition
- §28 — LCEL Primitives — `RunnableParallel`, `RunnableBranch`, pipe operator *(the EDUCATIONAL.md index wrongly listed §28 as "Multi-Query Retrieval"; that is §32)*
- §30 — Semantic Routing vs LLM-Assisted Routing
- §46 — Coordination Pattern Taxonomy (classification index)
- §47 — Opinion Aggregation Techniques *(Gap 28 deferred to §87)*
- §51 — InsightForge Analytics — structural reference implementation
- §85 — LangSmith 2026 Additions (Fleet, Sandboxes, Context Hub, Engine)

### Appendix
- **§87 — v2.2 Deferred Backlog** — every "defer" decision from the review, with its promotion trigger

### Index reconciliation notes

*Carried forward from the previous index. These record where the EDUCATIONAL.md index pointed at the wrong section, so the corrections are not lost in the rebuild.*

*The EDUCATIONAL.md index listed "Section 25 — Actor-Critic Pattern" with sub-items 25a and 25b. That was a mislabel: §25 is the Architectural Gaps Register, and 25a/25b were sub-entries inside Gap 25, never standalone sections. The content those entries pointed at lives here:*

- LangGraph 2026 memory architecture (Checkpointer + BaseStore split) → **§52** (Part 6)
- `create_agent` replacing `create_react_agent` → **§50** (Part 8), applied throughout §42/§48/§51
- Actor-Critic as a conceptual foundation → never written as a section; the closest ratified pattern is the grader/coach loop in **§42** and reflection in **§48**

*The EDUCATIONAL.md index also listed §39 among the MCP sections. §39 is "Knowledge Tools in Augmented Reasoning" — it is where the MCP-out decision and the 20 computation tools are recorded, and it closes Part 9 for that reason.*

---


## Overview Architecture — Agent Improve Refactor Target

*Graphical view of how all the concepts in this document connect for the Agent Improve refactor. Section numbers reference where each concept is documented in detail. This diagram reflects the ratified end-state: FastAPI (§55), no MCP (§39), one thread_id per project with LangGraph-managed `checkpoint_ns` (§23/§44), and the four-middleware coach stack (§84).*

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (Section 77)                              │
│  Six UI feedback patterns: spinner, status, extracted fields, completeness  │
│  score, LangSmith trace link, completion confirmation                       │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │ HTTP / SSE
┌──────────────────────────────────▼──────────────────────────────────────────┐
│              API LAYER — FastAPI  (DECIDED, Section 55; see 72)             │
│  LangServe archived; LangGraph Server needs a commercial licence.           │
│  FastAPI + LangGraph (MIT) + checkpointer is the self-hosted path.          │
│  Versioning (Section 74) becomes relevant after first production launch.    │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼──────────────────────────────────────────┐
│          LEVEL 1 — SUPERVISOR: Global Planner + Global Executor              │
│                        (Sections 5, 11, 17, 20, 44)                         │
│                                                                             │
│    Global Planner   — DETERMINISTIC gate-checker, not an LLM (Section 44)   │
│                       reads gate_passed → decides next unfinished phase   │
│    Global Executor  — routes via STATIC edges: define → measure → …         │
│    SupervisorState  — orchestration only (Section 17). No artifacts.        │
│    One thread_id per project, e.g. "IMPR-2026-FS1"                          │
└──────────────────────────────────┬──────────────────────────────────────────┘
                                   │
       ┌───────────────┬───────────┼───────────┬───────────┐
       │               │           │           │           │
┌──────▼─────┐ ┌──────▼─────┐ ┌───▼─────┐ ┌──▼──────┐ ┌───▼──────┐
│  DEFINE    │ │  MEASURE   │ │ ANALYSE │ │ IMPROVE │ │ CONTROL  │
│  Subgraph  │ │  Subgraph  │ │ Subgraph│ │Subgraph │ │ Subgraph │
│ (S. 23,44) │ │ (S. 23,44) │ │ (23,44) │ │ (23,44) │ │ (23,44)  │
└──────┬─────┘ └──────┬─────┘ └────┬────┘ └────┬────┘ └────┬─────┘
       │              │            │           │           │
       │   Each subgraph: own PhaseState (S.18), own auto-managed            │
       │   checkpoint_ns. NO per-subgraph checkpointer, NO per-subgraph      │
       │   thread_id (S.23/§44 correction).                                  │
       └──────────────┴────────────┴───────────┴───────────┘
                                   │
                    ┌──────────────▼──────────────┐
                    │  LEVEL 2 — Phase Subagent   │
                    │  ┌───────────────────────┐  │
                    │  │ Phase Planner (S.5,11)│  │
                    │  │ decides next action,  │  │
                    │  │ focus_field, and      │  │
                    │  │ retrieval_strategy    │  │
                    │  │ (single_hop|multi_hop │  │
                    │  │  — Section 71)        │  │
                    │  └──────────┬────────────┘  │
                    │             │               │
                    │  ┌──────────▼────────────┐  │
                    │  │ Phase Executor (S.11) │  │
                    │  │ create_agent + ReAct  │  │
                    │  │ bind_tools, ≤5 hops   │  │
                    │  │ RemainingSteps cap    │  │
                    │  │ (Section 34)          │  │
                    │  │                       │  │
                    │  │ Middleware stack S.84:│  │
                    │  │  DMAICSkillsMW  (83)  │  │
                    │  │  DMAICGraderMW  (42)  │  │
                    │  │  SummarizationMW(36)  │  │
                    │  │  before_model   (38)  │  │
                    │  └──────────┬────────────┘  │
                    │             │               │
                    │  ┌──────────▼────────────┐  │
                    │  │ Coherence Check (S.69)│  │
                    │  │ lightweight LLM,      │  │
                    │  │ every turn, silent    │  │
                    │  └──────────┬────────────┘  │
                    │             │               │
                    │  ┌──────────▼────────────┐  │
                    │  │ policy advisory (S.2, │  │
                    │  │ 38) — mid-phase       │  │
                    │  │ artifacts             │  │
                    │  │ contradiction check   │  │
                    │  └──────────┬────────────┘  │
                    │             │               │
                    │  ┌──────────▼────────────┐  │
                    │  │ At Gate Boundary —    │  │
                    │  │ four layers (S.68):   │  │
                    │  │ 2a Coherence   (69)   │  │
                    │  │ 2b Field presence(48) │  │
                    │  │ 2c Constraints  (68)  │  │
                    │  │ 2d Rubric grader(42)  │  │
                    │  │ then gate_review_node │  │
                    │  │ → interrupt() (S.2)   │  │
                    │  │ → gate_apply_node(44) │  │
                    │  └───────────────────────┘  │
                    └──────────────┬──────────────┘
                                   │
       ┌───────────────────────────┼───────────────────────────┐
       │                           │                           │
┌──────▼──────────┐   ┌────────────▼──────────┐   ┌───────────▼──────────┐
│  STATE LAYER    │   │  LEVEL 3 — LEAF TOOLS │   │  OBSERVABILITY       │
│                 │   │  (Sections 39, 60)    │   │                      │
│  Checkpointer   │   │                       │   │  LangSmith           │
│  (Sections 1,52)│   │  Universal 8:         │   │  (Sections 1, 73, 75)│
│  AzureBlob      │   │  CoachingResponse     │   │  @traceable on       │
│   CheckpointSvr │   │   rag_lookup_         │   │  custom functions    │
│   (refactor)    │   │     methodology       │   │  and all four        │
│  → PostgresSaver│   │   rag_lookup_evidence │   │  validation layers   │
│   (production)  │   │   rag_lookup_         │   │                      │
│                 │   │     case_history      │   │  Evaluation datasets │
│  BaseStore      │   │   propose_template    │   │  (Section 75)        │
│  (Sections 52,  │   │   propose_diagram     │   │  regression testing  │
│   52a)          │   │   check_gate_status   │   │                      │
│  AzureBlobStore │   │   request_human_      │   │  P50/P99 diagnostic  │
│   → PostgresStr │   │     approval          │   │  (Section 1)         │
│  cross-phase    │   │                       │   │                      │
│  artifacts      │   │  + 20 per-phase       │   │  Grader on_evaluation│
│                 │   │    computation tools  │   │  → step_log (S.42)   │
│  Typed Pydantic │   │    (Section 39)       │   │                      │
│  boundary       │   │                       │   │                      │
│  mappers (S.19, │   │  Multi-query + RRF    │   │                      │
│   23, 44)       │   │  inside each          │   │                      │
│                 │   │  rag_lookup_* tool    │   │                      │
│                 │   │  (Sections 32, 33)    │   │                      │
└─────────────────┘   └───────────────────────┘   └──────────────────────┘

RELIABILITY WRAPPING (Sections 49, 66, 67, 79) — applied to LLM + Azure calls:
  Per-node TimeoutPolicy(run_timeout=45) + node error_handler= for Saga
  compensation + Circuit Breaker (3 failures / 30s, 60s reset) +
  Exponential backoff (managed services) / Jittered backoff (shared resources) +
  Structured error schema (Section 64) +
  Fallback Chain: gpt-4o → gpt-4o-mini → Azure Redis Cache → degraded mode
```

### How the Numbered Concepts Connect

The refactor sequence is not arbitrary — dependencies flow through this diagram:

```
State foundations (S.1, 52, 52a) must exist before
  → subgraph structure (S.23, 44) can be wired, which enables
    → phase planner/executor pattern (S.5, 11) to have context, which enables
      → validation stack (S.48, 68, 69) to run at correct boundaries, which enables
        → HITL gates (S.2, 53) to actually pause execution, which enables
          → gate quality evaluation (S.42, 54) to fire only at the right moments,
             which enables
            → multi-hop retrieval (S.71) to serve coaching, not gates, which is
               served by internal @tool retrieval (S.32, 33, 39) — NOT MCP (S.39),
                → wrapped in failure handling (S.49, 66, 67, 79) for production
                   reliability, observed via
                  → LangSmith (S.1, 75) with @traceable on custom functions,
                     containerised per S.76, versioned per S.74 after launch.
```

Every arrow above represents a real technical dependency. Attempting to build later layers without earlier layers produces the exact fragility Section 44 diagnosed in the current Agent Improve.

---

## Terminology Reference

*New section, authored during the batch commit. Positioned before §1 deliberately: the rest of this document uses "agent," "subagent," "node," "subgraph," and "tool" heavily, and EDUCATIONAL.md used them inconsistently across §5, §11, §17, §18, §20, and §23. These are the authoritative definitions. Where a later section's wording differs, this section wins.*

### Structural primitives (from LangGraph)

| Term | Definition |
|---|---|
| **Node** | A Python function in a `StateGraph`. Reads state, does work, returns a state-update dict. The atomic unit of execution. |
| **Subgraph** | A compiled `StateGraph` embedded as a node in a parent graph. Has its own state schema and internal nodes; the parent sees only its input and output. |
| **Tool** | A Python function bound to an LLM via `bind_tools()`. **Not** a node — it is invoked from inside a node, by the LLM, at runtime. |
| **Middleware** | A LangChain 1.0 `AgentMiddleware` attached to a `create_agent` call via `middleware=[...]`. Wraps the agent loop through six hooks (§80). Not a node and not a tool. |

### "Harness" — the control plane around the model

**Definition: the harness is everything we engineer around the model — the graph, the state schemas, the tools, the middleware, the validation stack, the persistence layer. The model is the reasoning; the harness is the system.** Anthropic's framing is *agent = harness + model* (`anthropic.com/engineering/effective-harnesses-for-long-running-agents`, Nov 2025), and the point of the framing is that for a long-running task the harness is where the engineering effort goes, not the prompt.

This matters here because DMAIC coaching is a long-running agent task by that definition: it spans weeks, survives process restarts, and accumulates state a single context window cannot hold. Almost every ratified decision in this document is a harness decision — checkpointer and store (§1, §52), the four-layer validation stack (§68), context compression (§36), reliability primitives (§79) — and none of them is a prompt.

**The word has two live senses; do not conflate them:**

| Sense | Meaning | Where it appears |
|---|---|---|
| **Architectural (Anthropic)** | The whole control plane around the model — our entire LangGraph application | The Tier 1 sources in §45; this document's design decisions generally |
| **Library (LangChain)** | A specific agent-loop implementation. From the deepagents README: *"LangChain's `create_agent` is a minimal agent harness on top of \[LangGraph]. Deep Agents is a more opinionated harness on top of `create_agent`."* | §42, §84 — the `create_agent` vs `create_deep_agent` decision |

In the library sense we chose the *minimal* harness (`create_agent`) and built our own middleware on it (§4.4 of CLAUDE.md, §42, §84). In the architectural sense the harness is the thing this entire document specifies.

### Role labels applied to those primitives

| Role | What it is | Where it lives |
|---|---|---|
| **Planner** | A node whose responsibility is producing a structured plan — typically an LLM call with `with_structured_output`. | §5, §11, §20 |
| **Executor** | A node whose responsibility is consuming a plan and dispatching. At Level 1 it dispatches to subgraphs via edges; at Level 2 it dispatches to tools via the tool-calling loop. | §5, §11, §20 |
| **Supervisor** | The Level 1 pair — Global Planner + Global Executor — at the top of the hierarchy. | §17, §20, §44 |
| **Phase subagent** | A subgraph at Level 2: Define, Measure, Analyse, Improve, Control. Contains its own Planner and Executor nodes. | §18, §23 |
| **Leaf tool** | A tool bound to a Level 2 executor. Plain functions — never Planner-Executor pairs. | §39, §60 |

### The recursion is two-level, not infinite

| Level | Planner | Executor | Dispatches to | Mechanism |
|---|---|---|---|---|
| 1 | `global_planner` — **deterministic gate-checker**, not an LLM (§44) | `global_executor` (router) | Phase subgraphs | Static LangGraph edges |
| 2 | `phase_planner` (LLM) | `phase_executor` (LLM + `bind_tools`) | Leaf tools | Tool-calling loop inside the node |
| 3 | — | — | — | Tools are functions, not P-E pairs |

**Recursion rule:** at every non-leaf level the pattern is *Planner reasons, Executor dispatches*. An Executor's targets may themselves be Planner-Executor pairs — that is what makes the pattern recursive. Only at the leaf level do you find single-function tools.

### "Agent" — used carefully

The word carries two meanings in this document, and both appear:

- **LangChain classic sense** — an LLM with bound tools that decides which tool to call. In our code this is the Level 2 `phase_executor` node.
- **Multi-agent sense** — a named role (supervisor, subagent, worker). In our code, "phase subagent" means the Level 2 *subgraph as a whole*.

When §23's AgentLean Application paragraph says "subagent," it means **subgraph**.

### Things that are deliberately *not* levels in the hierarchy

A recurring source of confusion in EDUCATIONAL.md was treating composition tools as architectural levels. They are not:

- **LCEL** (`prompt | llm | parser`) is a composition tool used *inside* a single node (§27). It does not replace nodes or subgraphs, and it cannot express the executor's dynamic tool dispatch.
- **RRF and multi-query** live *inside* a `rag_lookup_*` tool (§32, §33). Not nodes, not wrapper classes around the retriever.
- **Middleware** wraps the agent loop (§80, §84). Not a node in the subgraph.
- **Rubric grading** is middleware on `create_agent` (§42), not a subgraph node.

### Terms cross-referenced to sections

| Concept | Mechanism documented in | Definition in |
|---|---|---|
| Node, subgraph, tool | §23 | this section |
| Planner-Executor pair, recursion | §5, §11, §20 | this section |
| Phase subagent, `PhaseState` | §17, §18, §23 | this section |
| Tool-calling coach agent | ARCHITECTURE.md §B2 *(external reference)* | this section |
| Middleware hooks | §80, §84 | this section |
| Harness | §42, §84 *(library sense)*; §45 Tier 1 sources *(architectural sense)* | this section |

---

### Visual Architecture Reference

*Four diagrams, placed after the definitions because they are illustrations of those definitions rather than a second vocabulary. Every box in them is one of the four **structural primitives** defined above — node, subgraph, tool, middleware — and nothing else. Diagram 4 exists specifically to settle the question "Agent" — used carefully leaves open: which of these boxes is an agent and which merely looks like one.*

*In the architectural sense of **harness**, all four diagrams together **are** the harness: the graph, the state schemas, the tools, the middleware, the validation stack, the persistence layer. The model appears in exactly two places across all four — inside `phase_planner` and inside `phase_executor`. Everything else on these pages is engineered control plane, which is the point of the framing.*

*The diagrams are committed as **images**, so they render in any markdown viewer with no extension and no live rendering step. The Mermaid source of each is a `.mmd` file in [`diagrams/`](diagrams/) and is the thing to edit — the `.png` and `.svg` beside it are build artifacts.*

*They were originally inline Mermaid code fences. Live-rendering them in the VS Code markdown preview proved unreliable in this document: the preview re-renders on every content update, and both Mermaid extensions tried would draw the diagrams and then blank them a moment later, leaving an empty gap. Static images remove the failure mode entirely.*

**To change a diagram:** edit the `.mmd`, then re-render both artifacts.

```bash
npm install @mermaid-js/mermaid-cli          # provides mmdc, bundles Chromium
cd agent-improve/diagrams
mmdc -i 01-overview.mmd -o 01-overview.png -b white -w 2000 -s 2
mmdc -i 01-overview.mmd -o 01-overview.svg -b white -w 1800
```

*`-b white` matters: several node labels rely on dark text, so a transparent background makes edge labels and subgraph titles unreadable in a dark-themed viewer.*

---

#### Diagram 1 — The whole system: one graph, five subgraphs, two persistence primitives

The top-level view. The **supervisor** is the Level 1 router from *The recursion is two-level, not infinite* — and it contains no LLM: phase sequencing is a deterministic gate-check plus static edges, so there is nothing to reason about. Each DMAIC phase is a **subgraph** (a compiled `StateGraph` embedded as a node in the parent; the parent sees only its input and output). Both persistence primitives attach to the parent graph **only** — subgraphs compile without either, and LangGraph routes their writes through the parent's saver under an auto-managed `checkpoint_ns`. The three Azure AI Search indexes sit below the graph because they are reached through **tools** invoked from inside a phase executor, never through a prepended context block (§7.1).

![Diagram 1 — supervisor router, five phase subgraphs joined by static edges, checkpointer and store on the parent graph only, three Azure AI Search indexes below](diagrams/01-overview.png)

*Source: [`diagrams/01-overview.mmd`](diagrams/01-overview.mmd) · [full-size SVG](diagrams/01-overview.svg). Edit the `.mmd` and re-render — never hand-edit the image.*

Two rules are visible in the shape rather than the labels. **Solid double arrows are static edges; dashed arrows are conditional edges** — and no node ever emits both, because mixing them means both paths execute silently (§1.2). And the persistence and index clusters hang off the *parent*, not off any phase — that placement is the architecture, not the drawing.

---

#### Diagram 2 — Inside a phase subgraph: a cycle, not a pipeline

Expanding one of the five phase subgraphs from Diagram 1. Every box here is a **node** — a Python function that reads state, does work, and returns a state-update dict. The two loops are the substance of this diagram: the planner and executor cycle many times per phase, once per field rather than once per phase, and the validation stack loops back to the executor on failure with accumulated per-layer feedback. Leaf **tools** do not appear as boxes at all — from the subgraph's point of view the executor is a single node, and what happens inside it is Diagram 3.

![Diagram 2 — inside a phase subgraph: planner, executor, four-layer validation, gate review interrupt, gate apply, and the two cycles](diagrams/02-phase-subgraph.png)

*Source: [`diagrams/02-phase-subgraph.mmd`](diagrams/02-phase-subgraph.mmd) · [full-size SVG](diagrams/02-phase-subgraph.svg). Edit the `.mmd` and re-render — never hand-edit the image.*

`Command` routing is legitimate **inside** a phase subgraph — this is the level where step order is genuinely data-dependent — and it is the only level where it is legitimate. Note also what the ordering buys: the grader loop in layer 2d runs *before* the interrupt, so the Belt is never shown work already known to be below standard, and the policy advisory runs *after* the Belt's edits, where it offers a second opinion rather than a veto (§9.1).

---

#### Diagram 3 — Inside the coach node: `create_agent`, eight middlewares, two tool tiers

Expanding the `phase_executor` box from Diagram 2. Everything here lives inside what the subgraph sees as one node. **Middleware** is an `AgentMiddleware` attached via `create_agent(middleware=...)` that wraps the agent loop through its hooks — it is not a node and not a tool. **Tools** are Python functions bound to the LLM, invoked from inside this node by the model at runtime — also not nodes. The diagram orders the middlewares by when their hooks fire, which is what matters at runtime; the declaration order in `middleware=[...]` is given in §8.1.

![Diagram 3 — the phase executor built with create_agent: the middleware layers and the two tool tiers](diagrams/03-coach-node.png)

*Source: [`diagrams/03-coach-node.mmd`](diagrams/03-coach-node.mmd) · [full-size SVG](diagrams/03-coach-node.svg). Edit the `.mmd` and re-render — never hand-edit the image.*

Two structural facts worth reading off the picture. **The tool count is bounded by construction, not by discipline** — per-phase binding keeps every coach between 9 and 16 tools, which is why no tool-selector middleware is needed. And **the grader is middleware, not a subgraph node** — it wraps the agent loop, so it is invisible both to the subgraph in Diagram 2 and to the Belt.

---

#### Diagram 4 — Agent role mapping: what is an agent, and what only looks like one

The word "agent" carries two senses in this document — the LangChain classic sense (an LLM with bound tools that decides which tool to call) and the multi-agent sense (a named role: supervisor, subagent, worker). This diagram applies both senses to every box in Diagrams 1–3 and labels each one explicitly. Read it as the answer to "so how many agents are in this system?" The answer is: **one per phase, and it is the executor node.**

![Diagram 4 — agent role mapping: phase_executor is the only actual agent](diagrams/04-agent-roles.png)

*Source: [`diagrams/04-agent-roles.mmd`](diagrams/04-agent-roles.mmd) · [full-size SVG](diagrams/04-agent-roles.svg). Edit the `.mmd` and re-render — never hand-edit the image.*

**Legend:** ✅ green, thick border — an agent in the LangChain classic sense: an LLM with bound tools that decides which tool to call. ❌ red — not an agent, whatever it is named. ◆ yellow, dashed border — a role label applied to a structural primitive, with no corresponding code object.

The same mapping in table form, since it is the distinction most often lost when this document is quoted in a prompt:

| Box | Primitive it actually is | Has an LLM? | Has bound tools? | Agent? |
|---|---|---|---|---|
| Supervisor router | Parent graph + static edges | No | No | **No** — deterministic router |
| Phase subgraph | Subgraph | — | — | **No** — "phase subagent" is a role label |
| `phase_planner` | Node | Yes | No | **No** — planner node |
| `phase_executor` | Node built with `create_agent` | Yes | Yes | **Yes** — the only one |
| Validation layer 2b | Plain function | No | No | **No** |
| Validation layers 2a / 2c | Node-internal LLM calls | Yes | No | **No** |
| Validation layer 2d | Middleware | Yes | No | **No** — middleware is not a node |
| `gate_review_node` | Node — `interrupt()` | No | No | **No** — interrupt point |
| `gate_apply_node` | Node | No | No | **No** — plain function |
| 7 universal tools | Tools | No | — | **No** |
| 20 computation tools | Tools — pure functions | No | — | **No** |

Five agents exist in Agent Improve: one `phase_executor` per DMAIC phase. Everything above them is routing, everything beside them is validation, and everything below them is functions.

---

# PART 1 — FOUNDATIONS

*Core concepts a reader needs before anything else: how state survives, how a human approves it, and how the planner/executor cascade nests.*

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
| `AzureBlobCheckpointSaver` | Custom `BaseCheckpointSaver` implementation, `core/checkpointer.py` | **Transitional — in use during the refactor.** Committed and unit tested at refactor steps 2.1–2.2, wired into `graph.compile()`. Works for single-developer development with no new infrastructure. |
| `PostgresSaver` | Production — first-class LangGraph support | **Post-refactor target.** Officially maintained, handles concurrency correctly, SQL-queryable for debugging, updated by the LangChain team on every LangGraph release. |

*The EDUCATIONAL.md version of this table said "Custom Blob Saver — ruled out, too much custom code." That was written before the saver existed. It now exists, is tested, and is the checkpointer the refactor runs on.*

**Phased checkpointer decision (ratified).** `AzureBlobCheckpointSaver` is custom code that we maintain, and it was never tested for concurrent access — Azure Blob has no row-level locking. `PostgresSaver` is the officially maintained, primary tested path. But adding PostgreSQL during the heaviest refactoring period adds infrastructure complexity for no development benefit. So:

| Stage | Checkpointer | Store (§52, §52a) |
|---|---|---|
| During the refactor | `AzureBlobCheckpointSaver` | `AzureBlobStore` |
| Post-refactor, pre-production | `PostgresSaver` | `PostgresStore` |

Migration is small: change the constructor and the connection string, then run the existing unit tests against PostgreSQL. Provision Azure Database for PostgreSQL (flexible server, ~€12–15/month) at that point. The `BaseCheckpointSaver` and `BaseStore` interfaces are identical regardless of backend, so nothing above the persistence layer changes. Tracked as §87 backlog item 13.

### Where This Stood, and Where It Stands Now
EDUCATIONAL.md recorded "no checkpointer is wired into `workflow.compile()`" as an open gap. **That gap is closed** — commits at refactor steps 2.1–2.2 wired `AzureBlobCheckpointSaver` into `graph.compile()`. The mitigation that used to carry the system (completeness-based re-extraction from full conversation history on every gate submission) is no longer load-bearing.

### Implementation
```python
# During the refactor — what is wired today
from core.checkpointer import AzureBlobCheckpointSaver

checkpointer = AzureBlobCheckpointSaver(blob_client)
graph = workflow.compile(checkpointer=checkpointer, store=store)

# Post-refactor, pre-production — the migration
from langgraph.checkpoint.postgres import PostgresSaver

checkpointer = PostgresSaver.from_conn_string(os.getenv("PG_CONN"))
graph = workflow.compile(checkpointer=checkpointer, store=store)
```

**Checkpointer placement rule (§23, §44 — web-verified):** the checkpointer goes on the **parent graph only**. Phase subgraphs are compiled *without* a checkpointer; LangGraph routes their writes through the parent's saver, distinguished by an auto-managed `checkpoint_ns`. One `thread_id` per project. Compiling a checkpointer onto a subgraph causes duplicate storage and state-persistence problems.

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
    return artifacts

@traceable
def validate_define_gate(state: DefineState) -> list[str]:
    """Run all four validation layers for Define gate."""
    failures = []
    # DMAICGateValidator calls here
    return failures

@traceable
def check_completeness(artifacts: dict, phase: str) -> float:
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
        │     inputs: {artifacts: {...}, phase: "define"}
        │     outputs: 0.75
        └── validate_define_gate (custom — NOW traced via @traceable)
              inputs: {state: {...}}
              outputs: ["how_goal missing timeline criterion"]
```

Without `@traceable`, the LangSmith trace shows the LangGraph nodes but the logic BETWEEN them is invisible — you cannot see what the extraction produced, what completeness score triggered the next coaching turn, or which validation criterion failed. With `@traceable`, the full execution path is inspectable.

**Add `@traceable` to every custom function that:**
- Extracts fields from LLM responses
- Validates gate criteria — **all four validation layers of §68** (coherence, field presence, constraint validation, rubric grading) are custom functions and none of them are traced by default
- Scores completeness
- Makes routing decisions outside of LangGraph node routing
- Calls an external Azure service directly (so its latency appears in traces)

*The EDUCATIONAL.md version of this list ended with "calls the MCP server." MCP is out of scope (§39); the corresponding requirement is to trace direct Azure OpenAI and Azure AI Search calls made outside a LangChain runnable.*

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

High P99 latency degrades the Belt's coaching experience. The trace for the slowest turns will show which combination of operations caused the outlier — typically multi-hop retrieval (Section 71) combined with a `DMAICGraderMiddleware` call on the same turn. The fix is either caching (Section 65's principles, applied to the Azure Redis Cache in Section 67 Level 3), a faster model for the grader (Section 42's temperature and model notes), or restructuring the validation stack to run cheapest-first (Sections 68 and 69).

These percentiles are also the input to Section 75's regression thresholds — a latency regression is a release blocker in the same way an accuracy regression is.

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
Act: cache it (Sections 65/67), reorder the validation
     layers (Sections 68/69), or use a faster model (Section 42)
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
graph.invoke(input, config={"configurable": {"thread_id": case_id}})
```

### The Full HITL Gate Pattern — Nine Steps

*This replaces the approve/reject binary that EDUCATIONAL.md described. Ratified across §42 (grader added as step 2), §48 and §68 (step 2 decomposed into four validation layers), §38 (mid-phase contradiction handling folded into step 6), and §44 (two-node implementation).*

Interrupts are not a binary approve/reject. The correct pattern is a nine-step sequence with **two distinct quality checks in it** — one on the AI's work before the Belt sees it, one on the Belt's edits before they commit.

| Step | What Happens | Quality check for |
|---|---|---|
| 1. Executor runs | Coach produces its response; extraction captures phase fields into the Task Plan | — |
| 2. **Validation stack runs** | Four layers, cheapest first (§68). Failures feed back to the coach with accumulated per-layer feedback; shared cap of 3 attempts. **The Belt does not see this loop.** | **AI's work** |
| 3. Interrupt fires | `gate_review_node` pauses the graph; Belt sees validated, grader-approved output | — |
| 4. Belt reviews | Belt checks AI-captured values for accuracy | — |
| 5. Belt edits *(optional)* | Belt corrects wrong fields directly in the Task Plan | — |
| 6. **Policy advisory** | Validates the Belt's edits against required-field policy, cross-phase consistency, and previously gate-approved values (§38 contradiction auto-flag). Surfaces structured feedback. **Non-blocking** — the Belt may act on it or override. | **Human's edits** |
| 7. Belt approves | Belt confirms the gate is ready — with or without acting on the advisory. **`gate_apply_node` assembles the gate document and writes it to both the store and `PhaseState.final`** (§18) | — |
| 8. Checkpoint saves | State committed to Azure Blob / PostgreSQL **only now** — never before the Belt approves | — |
| 9. Next task? | Supervisor reads `gate_passed`, routes to the next unfinished phase or next field | — |

**Step 2 in detail — the four validation layers (§68):**

| Sub-step | Layer | Mechanism | Model |
|---|---|---|---|
| 2a | Coherence | Is this a real, meaningful, conclusive statement? Catches gibberish, vague non-answers, self-contradiction, off-topic replies, and parroting the Belt's own words. | Lightweight LLM — `operational-model`, temp 0.1 |
| 2b | Field presence | Are all **Tier 1** fields for this phase populated? (`DMAICGateValidator`, §48) | Deterministic — no LLM |
| 2c | Constraint validation | Does the decision address budget / timeline / risk / measurement? (§68) | Lightweight LLM — `operational-model`, temp 0.1 |
| 2d | Quality rubric | Does the **gate document** meet DMAIC quality standards per criterion? Gate document grader using `PHASE_RUBRIC` (e.g. `ANALYSE_RUBRIC`, §42) | LLM grader — `operational-model`, temp 0.1 |

> **Step 2d is NOT `DMAICGraderMiddleware`.** An earlier revision of this table named it, and that was wrong. **Two graders exist, and they are complementary rather than redundant** (§42 Finding 18):
>
> | | `DMAICGraderMiddleware` | Step 2d |
> |---|---|---|
> | Where | Middleware, inside the executor | The `validation_stack` node |
> | When | **Every coaching turn**, via `after_agent` | **Once**, at the gate boundary |
> | Rubric | `COACHING_QUALITY_RUBRIC` | `PHASE_RUBRIC` — `DEFINE_RUBRIC`, `MEASURE_RUBRIC`, … |
> | Grades | The coach's **process** | The **gate document** |
> | Sees | One response at a time | The complete captured field set |
>
> By the time step 2d fires, the middleware grader has already done its job across every turn of the conversation. Step 2d checks what no per-turn grader can see: cross-field consistency and cross-phase linkage in the finished document.

Each layer fires only if the previous one passes. Layer 2b is the only deterministic layer — checking whether a key exists in a dict genuinely does not need an LLM. Layer 2a *was* specified as deterministic (length plus question-mark checks) and was upgraded on the grounds that "I can write garbage in and a length check will not detect it." At roughly 250 tokens per check on `gpt-4o-mini` fired 20–40 times per phase session, Layer 2a costs about $0.01–0.02 per phase — negligible against the quality it buys.

### Why the Advisory Is Non-Blocking

The Belt is the domain expert. The policy check offers a second opinion *before* the approval decision, not a veto *after* it. A blocking post-approval check would place the LLM above the human's judgment, which is wrong in a coaching context. The advisory fires inside the existing interrupt window — no additional round-trip.

Contrast this with the grader at step 2: the grader *does* block, because it is checking the AI's own output, and there is no reason to show a Belt work that the system already knows is below standard.

### The Advisory Also Fires Mid-Phase

Per §38, the policy advisory is not only a gate-boundary mechanism. It also runs before each coach response is returned to the Belt, comparing the Belt's most recent statements against the `artifacts` already committed in prior gate documents. If a numeric or categorical value differs from a previously approved one, the coach's response is suppressed and a HITL interrupt payload is emitted:

- **Payload contains:** field name, previously approved value with its approval timestamp and gate, the proposed new value, and two Belt-facing options.
- **Belt chooses:** *"Update the approved value"* → the affected phase's gate document becomes provisional and downstream phases need re-review; or *"Keep the approved value"* → the Belt clarifies they misspoke, no state change.

This is a structured diff over `artifacts` — no LLM call, negligible latency. There is deliberately **no tolerance threshold**: in production DMAIC, baseline means, sigma levels, and target metrics are taken seriously, and silent drift across weeks is exactly the failure mode a coaching system exists to prevent. "The delta was small enough" is not acceptable when downstream analysis depends on the value. Any change to a previously gate-approved value is treated as a mini-gate, not a silent overwrite. See §49 — the re-approval cascade must run the affected phase's compensating action to clean up stale values in external systems.

### Implementation — Two Nodes, Not One (§44)

Splitting collection from application keeps the interrupt boundary clean:

| Node | Responsibility |
|---|---|
| `gate_review_node` | Fires the `interrupt()`, presents validated fields to the Belt, and stops. Does nothing with the response. |
| `gate_apply_node` | Reads the Belt's response, applies corrections, runs the policy advisory, and `Command`s either to the next step or back to the grader. |

**Implementation note:** the policy advisory is a `validate_phase_gate` tool call from the coaching agent — a leaf tool bound to the executor, **not** a separate subgraph node. Confirm the tool name against ARCHITECTURE.md §5.1 when the governance docs are rewritten. Its v2.1 scope covers single-phase field completeness *and* cross-phase consistency (for example, Measure's Y matching Define's Y), since §38's contradiction detection requires the cross-phase comparison anyway.

**Do not use `HumanInTheLoopMiddleware` for this.** Per §53, its edit and reject paths have confirmed bugs in subgraph contexts — only approve is reliable. This nine-step pattern uses graph-level `interrupt()` plus `Command(resume=...)` and avoids the bug entirely.

### Where Interrupts Belong in Agent Improve

| Interrupt Point | Purpose |
|---|---|
| Gate evaluation | Belt reviews extracted fields before the phase advances |
| Field correction | Belt edits fields the AI captured incorrectly |
| Mid-phase value contradiction | Belt resolves a conflict with a previously approved value (§38) |
| Coach escalation | AI uncertain, or validation exhausted its 3 attempts — needs human confirmation (`request_human_approval`) |

### Where This Stood, and Where It Stands Now
EDUCATIONAL.md recorded the gap as "gate advancement is automatic after extraction; no human review step; Belt cannot correct AI-extracted fields before they are committed." The nine-step pattern above is the ratified closure of that gap. The prerequisite — a working checkpointer — is satisfied (§1).

### Dependency Chain
```
Checkpointer (AzureBlobCheckpointSaver now, PostgresSaver later)
  → interrupt() possible
    → nine-step gate pattern
      → validation stack (§68) gates what the Belt ever sees
```

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
    case_id: str
    current_phase: str
    messages: list
    # All phase fields in one flat object
    what: str                       # Define
    baseline_mean: str              # Measure — all captured fields are str (§17)
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
    case_id: str
    current_phase: str
    messages: list
    phase_result: dict          # what the subagent hands back

# Define subagent — private state
class DefineState(TypedDict):
    messages: list              # its own conversation slice
    what: str
    why: str
    how_goal: str
    coaching_plan: Optional[CoachingPlan]   # planner output — parent never sees this

# Measure subagent — private state
class MeasureState(TypedDict):
    messages: list
    baseline_mean: str                      # captured fields are str — §17
    baseline_std: str
    coaching_plan: Optional[CoachingPlan]   # ONE plan per planner turn — §18
```

Parent passes a slice **in**, subagent returns a slice **out**. Clean boundary. No cross-phase access possible.

> **`completeness_score` was removed from both sketches above.** Earlier
> revisions carried it as a stored `float`, annotated "computed, not captured —
> float is correct." The annotation defended the *type* and missed the
> question: **there is no stored completeness score in the ratified design at
> all** (§17, §77). Gate progress is derived on demand from `artifacts`, the
> same way `check_gate_status()` derives missing fields. A stored score is a
> second source of truth for gate readiness that can drift out of agreement
> with `DMAICGateValidator`; a derived one cannot. These sketches are
> illustrative of Pattern 2, not schema definitions — the canonical per-phase
> state is `PhaseState` (§18).

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
├── case_id
├── current_phase
├── messages (full conversation — parent owns this)
└── gate_status per phase
         │
         │ passes in: {messages, phase_fields}
         ↓
DefineSubgraphState (private)
├── messages (slice)
├── define_fields: {what, why, how_goal, ...}
└── coaching_plan  ← planner output, never exposed to parent
         │
         │ output mapper writes the gate document to the Store;
         │ returns to parent: orchestration values only (§44 Mechanism 3)
         ↑
MeasureSubgraphState (private)
├── messages (slice)
├── measure_fields: {baseline_mean, baseline_std, ...}
└── coaching_plan
```

*No `completeness_score` on either — gate readiness is derived, not stored
(see the note above). And the return to the parent carries orchestration
values only: the artifacts themselves go to the Store, not up to
`SupervisorState` (§44).*

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

Each subagent's state is checkpointed **under its own namespace**, not by its own checkpointer. One checkpointer sits on the parent graph; LangGraph assigns each subgraph an auto-managed `checkpoint_ns` within the project's single `thread_id` (§23, §44). This gives the isolation properties without the duplicate-storage problem that per-subgraph checkpointers cause:

- A crash mid-Define does not affect Measure's checkpointed state
- Time travel can replay a specific subagent's execution independently — subject to the side-effect caveat in §3
- Interrupt points can be declared per subagent, not just globally

Note what this isolation does **not** give you: subgraph state does not automatically propagate to the parent's visibility. Cross-phase artifacts therefore travel through the store (§52a), not through parent state — see §19, §21, §23, §70.

---

### Where This Stood, and Where It Stands Now
EDUCATIONAL.md recorded Agent Improve as using flat shared state (Pattern 1), with all phase fields in one object and no encapsulation. **The refactor targets Pattern 2**, ratified concretely in §17 (`SupervisorState`) and §18 (`PhaseState`). The three rules above map one-to-one onto that ratification:

| Rule here | Ratified as |
|---|---|
| Rule 1 — parent owns the conversation | `SupervisorState.messages` (§17) |
| Rule 2 — subagents own their phase fields | `PhaseState.artifacts`, `.draft`, `.feedback` (§18) |
| Rule 3 — typed schemas for communication | Boundary mappers (§19, §23, §44) |

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
    how_goal: str
    # "messages" field and its reducer come for free

# Option B — declare TypedDict directly, explicit reducer
class DefineState(TypedDict):
    messages: Annotated[list, add_messages]   # explicit, same reducer, same behavior
    what: str
    why: str
    how_goal: str
```

**The distinction is design intent, not behavior.** `MessagesState` inheritance is the right convenience when the state's dominant content genuinely IS conversational — a chat container with a few extras bolted on. Explicit `TypedDict` declaration is the better choice when the state's dominant content is structured working memory that happens to also need conversation history for context.

**For Agent Improve's phase substates specifically:** `DefineState`, `MeasureState`, `AnalyseState` etc. are fundamentally structured DMAIC field containers (`what`, `why`, `baseline_mean`, `completeness_score`) — the conversation history is one field among several, not the dominant shape. Option B (explicit `TypedDict`) is more consistent with this document's emphasis on typed Pydantic boundary contracts and explicit state design (Section 44), even though it costs one extra line versus inheriting `MessagesState`.

**Where `MessagesState` inheritance genuinely IS the right choice in Agent Improve:** the debate subgraph (Section 22). `DebateState`'s dominant content really is conversational exchange — advocate argument, skeptic argument — making it closer in shape to the lab's researcher/summarizer example than the phase-level states are. Note that the debate subgraph itself is deferred to v2.2 (§87 item 10), so this remains a design note rather than refactor scope.

**The rule:**
```
State is mostly conversation + a few extras    → MessagesState inheritance is fine
State is mostly structured fields + conversation → explicit TypedDict makes intent clearer
```

---

## 5. Planner / Executor Model

*For the vocabulary used in this section — node, subgraph, tool, planner, executor, phase subagent, leaf tool — see the **Terminology Reference** in the front matter. This section and §11, §17, §18, §20, §23 all describe the same architecture from different angles; the Terminology Reference is the authority when wording differs.*

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
# Phase Planner output (structured, via llm.with_structured_output — §82)
{
  "next_action": "ask_for_baseline_data",
  "rationale": "baseline_mean missing, process scope confirmed",
  "tools_needed": ["rag_lookup_methodology"],
  "retrieval_strategy": "single_hop",          # §71 — planner decides, not the executor
  "focus_field": "baseline_mean",
  "expected_fields": ["baseline_mean", "baseline_std"]
}
# Phase Executor then carries out exactly this action
```

`retrieval_strategy` is decided here, at plan time, rather than at retrieval time — see §71 for the planned (Analyse) versus emergent (all other phases) multi-hop distinction.

### The Nested Cycle — Same Cycle, Two Scopes

The two-level cascade above answers *who plans*. It does not by itself say what a plan-execute round looks like, and without that the phase executor collapses back into a monolithic coaching loop with branching hidden inside the prompt — the exact Gap 10 problem this section diagnoses. The missing piece: **Plan → Execute → Review → Revise (§19) happens at both levels, nested.**

**Level 1 — the phase chain:**

| Stage | What happens |
|---|---|
| Plan | Phase planner decides the coaching strategy for the phase — which fields to elicit, in what order, with which tools |
| Execute | Phase executor iterates through the strategy, running per-field cycles (Level 2) |
| Review | Gate interrupt — Belt reviews all captured fields for the phase |
| Revise | Belt edits, policy advisory fires, Belt approves; final gate document written |

**Level 2 — the per-field cycle, nested inside Level 1 Execute:**

| Stage | What happens |
|---|---|
| Plan | Within-turn planner decides the coaching action for the current field — elicit, teach, challenge, re-ask with different framing, offer a worked example |
| Execute | Coaching LLM runs; extraction runs; one field captured |
| Review | Fast completeness and coherence check on the captured field — **no interrupt** |
| Revise | If not clean, loop back to Level 2 Plan with the failure signal; otherwise increment `field_index` and move to the next field |

**How they interleave:**

```
Level 1  Plan ──────────────────────────────────────────► Review ─► Revise
              │                                          ▲ (interrupt)
              │  Execute                                 │
              ▼                                          │
        ┌───────────────────────────────────────────────┐│
        │ L2: Plan→Exec→Review→Revise   (field 1)       ││
        │ L2: Plan→Exec→Review→Revise   (field 1 retry) ││
        │ L2: Plan→Exec→Review→Revise   (field 2)       ││
        │ …                                             ││
        │ L2: Plan→Exec→Review→Revise   (field 6)       ├┘
        └───────────────────────────────────────────────┘
```

One Level 1 Execute contains many Level 2 iterations. Level 1 Review fires only once, when Level 2 has completed for every required field.

**Concrete example — Define phase, IMPR-2026-FS1.** Six required fields (`problem_statement`, `business_case`, `project_scope`, `goal_statement`, `baseline_metric`, `target_metric`). Level 2 fires roughly 6–10 times inside Level 1 Execute, since some fields need re-asks. The Level 1 Review interrupt fires only when all six are captured and the §68 validation stack has passed.

Making Level 2 explicit is what turns coaching from a monolithic prompt into an inspectable, per-field, structured process. See §19 for the chaining mechanics and §11 for the level-by-level tool view.

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
- **Global Planner is deterministic, not an LLM** (§44). It reads `gate_passed` and decides the next unfinished phase. Phase sequencing in DMAIC is fixed; there is nothing to reason about. Using an LLM here would be cost and latency for no decision.
- Phase Planner uses `operational-premium` (gpt-4o) — genuinely reasoning-heavy structured decision
- Phase Executor uses `operational-model` (gpt-4o-mini) for tool calls and extraction; intermediate multi-hop retrieval stays on `operational-model` with final synthesis on `operational-premium` (§34 model tiering)
- All planner outputs are structured via `with_structured_output` (§82), never prose parsed downstream
- Re-planning is triggered when the executor hits a dead end, missing data, or a validation-layer failure (§68)
- Executors are routing mechanisms — LangGraph nodes or router functions, not necessarily LLMs. The Planner/Executor split matters for cost, observability, and testing; fusing them loses the boundary (§20).

---

## 20. Supervisor / Worker Architecture — Implementation

*Source: Edureka course — Implementing a Supervisor Node and Worker Agents*

*For the vocabulary used here, see the **Terminology Reference**.*

### The Correction This Section Needed

As written from the course, this section presented a **flat two-level supervisor/worker model**: supervisors have no tools, workers perform a single well-defined function. That contradicts §5 (two-level cascade), §11 (phase planner *and* phase executor), and §17 (which names the pattern recursive). A flat model cannot express a phase-level agent that plans coaching strategy *and* has its own executor dispatching to leaf tools — and that is exactly what a DMAIC phase subagent is.

**The correct model: a Planner-Executor pair, applied recursively. Three levels for Agent Improve.**

| Level | Planner (reasons) | Executor (dispatches) | Leaf |
|---|---|---|---|
| 1 — Global | Global Planner: which phase, are gates passed, what is missing — **deterministic, not an LLM** (§44) | Global Executor: routes to the phase subgraph via a static edge | — |
| 2 — Phase | Phase Planner: coaching strategy, which field, which action, which retrieval strategy | Phase Executor: `create_agent` + `bind_tools`, dispatches to leaf tools per plan step | — |
| 3 — Leaf | — | — | extraction, `rag_lookup_*`, gate validator, coaching LLM, computation tools, policy advisory |

**Recursion rule:** at every non-leaf level the pattern is *(Planner reasons, Executor dispatches)*. The Executor's targets can themselves be Planner-Executor pairs. Only at the leaf level do you find single-function tools.

### Key Design Principles

*Restated for the recursive model:*

The pattern is a Planner-Executor pair applied recursively. At every non-leaf level, a Planner reasons and produces a structured plan; an Executor consumes that plan and dispatches to the next level. At the innermost level, workers are single-function tools. **The Planner and Executor are distinct components — never fused.** The Executor's targets can themselves be Planner-Executor pairs, which is what makes the pattern recursive.

**Implementation implications:**
- Level 2 Planners run on `operational-premium` (gpt-4o) — reasoning-heavy structured decisions. The Level 1 Planner runs on no model at all; it reads flags.
- Executors are routing mechanisms — LangGraph nodes or router functions, not necessarily LLMs. The Level 2 Executor is an exception: it is an LLM with bound tools, because tool selection genuinely is a decision.
- Leaf tools use `operational-model` (gpt-4o-mini) or are pure functions. All 20 computation tools (§39) are pure functions.
- The Planner/Executor split matters for cost, observability, and testing. Fusing them loses the boundary — you can no longer see what was decided separately from what was done.

### Universal Anti-Patterns — Apply at Every Level

- **Executors reasoning** — they dispatch, they do not decide
- **Planners dispatching directly to leaves** — they produce plans; the Executor at their level consumes them
- **Leaves influencing control flow** — leaves return results; the Executor at their level routes
- **Overlapping responsibilities between two Planners at the same level**
- **Unstructured or ambiguous plan objects** between a Planner and its Executor — plans are `with_structured_output` schemas (§82), never prose

*Correction record: an earlier draft of this decision proposed that "the phase subagent is simultaneously worker and supervisor." That framing was rejected — it collapses the Planner/Executor split that §5 already establishes correctly. The framing above preserves the split.*

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

### Scope of These Factory Functions

`make_supervisor_node` and `make_worker_node` are useful **as Level 1 primitives** — the Global Planner + Global Executor shape — and **as leaf-level worker wrappers**. They do **not** describe Level 2 phase subagents, which need the full Planner + Executor decomposition from §5 and §11.

For Level 2 structure, see §5 (the nested cycle), §11 (the three planning scopes), §19 (Level 1 vs Level 2 chaining), and §23 (the five-node subgraph).

One further caveat on `make_supervisor_node` as written: it uses an LLM to choose the next worker. For DMAIC phase sequencing that is the wrong mechanism — the order is fixed, so §44's static edges apply. The LLM-routing version of this factory is appropriate only where the next step genuinely can vary at runtime.

### State — Different at Each Level

```python
# Level 1 — the course's minimal pattern
class SupervisorState(MessagesState):
    next: str    # tracks which node executes next — the routing backbone
```

Agent Improve's actual state is richer at both levels, and deliberately different between them:

| Level | State | Contains |
|---|---|---|
| 1 | `SupervisorState` (§17) | `phase_index`, `current_phase`, `gate_passed` — orchestration only |
| 2 | `PhaseState` (§18) | `coaching_plan`, `field_index`, `draft`, `artifacts`, `step_log`, `belt_edits`, `validator_feedback`, `gate_attempts`, `citations`, `uploads` — phase-internal detail the parent never sees |

The level-by-level state distinction is the structural expression of the recursion. If both levels shared one state object, the encapsulation §10 argues for would not exist.

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

### Verified Against LangGraph Docs (2026-07)

The mechanism this section describes is the right one for Agent Improve. Four points confirmed against Tier 1 sources during the review:

- Subgraphs embedded in a parent graph **share the parent's `thread_id`**
- Each subgraph gets its **own auto-managed `checkpoint_ns`**
- LangGraph 1.2.6 fixed a regression where nested subgraphs were not inheriting the parent `checkpoint_ns` — which both confirms the intended pattern and sets our version floor
- *"When using subgraphs, only the parent graph should have a checkpointer, to avoid duplicate storage and state persistence issues"*
- *"When a subgraph updates state, the parent graph may not see the changes immediately… Use shared state via Store for data that needs to cross graph boundaries"*

### AgentLean Application

Each DMAIC phase subagent **is** a subgraph embedded as a node in the supervisor parent graph. *(Terminology note: "subagent" here means "subgraph" — see the Terminology Reference.)* The parent graph has one `thread_id` per project, e.g. `IMPR-2026-FS1`; each subgraph — Define, Measure, Analyse, Improve, Control — has its own auto-managed `checkpoint_ns`, which LangGraph handles.

The subgraph's internal state (`DefineState`, `MeasureState`, …) is the `PhaseState` schema from §18. The parent's `SupervisorState` (§17) never sees the subgraph's coaching turns, tool calls, or extraction attempts — only the structured output at exit.

Cross-phase artifacts do **not** flow through the parent's state. That is why §17 removed `captured_fields` from `SupervisorState`. They flow through the store (§52a), because LangGraph subgraph state does not automatically propagate to the parent's visibility.

**The Define subgraph is not a straight pipeline.** §23's `researcher → summarizer` example above shows the mechanism, but it is too simple to represent a DMAIC phase. The Define subgraph has five nodes — planner, executor, validation_stack, gate_review (interrupt), gate_apply — connected by **conditional edges** and **cycles**. The graph structure is fixed at compile time; routing is dynamic based on state. The planner fires many times per phase, not once: after each executor step, control returns to the planner to decide whether to keep coaching the current field, move to the next field, or trigger the gate.

```python
def build_phase_subgraph(phase: str, llm, tools_for_phase):
    graph = StateGraph(PhaseState)
    graph.add_node("planner",          make_phase_planner(phase, llm))
    graph.add_node("executor",         make_phase_executor(phase, llm, tools_for_phase))
    graph.add_node("validation_stack", make_validation_stack(phase, llm))
    graph.add_node("gate_review",      make_gate_review(phase))     # interrupt fires here
    graph.add_node("gate_apply",       make_gate_apply(phase))      # policy advisory + store write
    # … conditional edges and cycles; see §4 for the shape
    return graph.compile()        # NO checkpointer — the parent owns it
```

**Two node names were wrong in earlier revisions, and both mattered.**

| Earlier revision | Ratified | Why the earlier name was wrong |
|---|---|---|
| `policy_advisory` as node 3 | **`validation_stack`** | The four-layer stack (§68) was missing from the node list entirely. The policy advisory is not a node — it is logic inside `gate_apply` |
| `revise` as node 5 | **`gate_apply`** | Different name *and* larger scope. `gate_apply` runs the policy advisory (step 6 of §2), processes the Belt's approval (step 7), and writes the gate document to the store (§18) |

`gate_review` was correct and is unchanged. Revision is still a behaviour — the validation stack routes back to the planner with accumulated `validator_feedback` — but it is an edge, not a node.

**Leaf tools are not subgraph nodes.** `rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history`, `propose_template`, `propose_diagram`, `check_gate_status`, `request_human_approval`, and the phase-specific computation tools are passed to the executor through the `tools=` parameter of `create_agent` (§84 — never `bind_tools()` on a bare LLM, which would bypass the middleware stack). From the subgraph's perspective the executor is one node; from inside that node, multiple tools can fire per invocation — up to the 5-hop cap of §34.

**The validation stack and the policy advisory are NOT tools.**

- **The validation stack is a separate node.** It runs *after* the executor finishes, reached by an edge. Making it a tool would put the decision of whether to validate in the coach's hands, which is exactly backwards — the coach is the thing being validated.
- **The policy advisory is logic inside `gate_apply`.** It fires after the Belt reviews and edits, checking whether those edits break cross-phase consistency (§38). It cannot be a coach tool because at the moment it runs, the coach is no longer in the loop.

**`record_field` is also not in that list, and no longer exists as a tool.** Field capture happens through `response_format=CoachingResponse` on the executor — see §82.

### How This Section Aligns With the Rest

| Section | Relationship |
|---|---|
| §5 — two-level cascade | Subgraphs implement the phase-level boundary |
| §17 — `SupervisorState` | Parent state holds orchestration; subgraph state holds phase-internal detail |
| §18 — `PhaseState` | The subgraph's internal state schema, plus the boundary mappers |
| §20 — Planner-Executor recursion | Each subgraph internally contains a Planner-Executor pair |
| §52a — `AzureBlobStore` | The mechanism for artifacts crossing subgraph boundaries |

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
    Executor: rag_lookup_methodology + coaching LLM + CoachingResponse
```

*Terminology: this section's "Level 3 — Tool Executor" is the leaf level of the Terminology Reference's table. Leaf tools are functions, not Planner-Executor pairs; the recursion stops at Level 2.*

---

### Three Levels of Planning in Agent Improve

**Level 1 — Supervisor Planner**

Thinks about the **entire DMAIC project across weeks**:
- Which phase are we in?
- Is the current phase complete?
- Which subagent should execute this turn?
- Is the gate ready to pass?

Scope: weeks, across all five phases.

*Note on implementation (§44): "thinks" here is a description of scope, not of mechanism. The Level 1 planner is **deterministic logic reading `gate_passed`, not an LLM call.* DMAIC phase order is fixed, so there is no reasoning to do — the routing between phases uses static edges. LLM-based planning starts at Level 2.*

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
  Reads gate_passed (deterministic gate-check, no LLM — §44)
  "Analyse phase not yet approved"
  Decision: invoke Analyse subagent
       ↓
LEVEL 2 — ANALYSE PHASE PLANNER
  Reads analyse artifacts + last messages
  "Belt listed 3 causes, none validated yet"
  Decision: {
    next_action: "validate_causes",
    tools: ["rag_lookup_methodology", "chi_square_test"],
    retrieval_strategy: "multi_hop",        # Analyse defaults to planned multi-hop (§71)
    focus_field: "root_cause_statement"
  }
       ↓
LEVEL 3 — TOOL EXECUTOR (leaf tools bound via bind_tools)
  → rag_lookup_methodology: "how to validate root causes with hypothesis testing"
  → Coaching LLM: generates Black Belt response
  → CoachingResponse.fields_captured: root_cause_statement
       ↓
Results bubble back up:
  Extraction result → Phase Planner (field captured? yes/no)
  Phase result → Supervisor (completeness score, gate ready?)
  Supervisor → updates blob, sends response to Belt
```

---

### Across Multiple Weeks — Continuity

The supervisor's orchestration state and the phase artifacts persist across all sessions via the checkpointer (`AzureBlobCheckpointSaver` during the refactor, `PostgresSaver` post-refactor) plus the store (`AzureBlobStore` → `PostgresStore`) for cross-phase artifacts. Each session the supervisor resumes on the project's `thread_id` and picks up exactly where the project left off. The Belt never re-explains what they have done.

```
Week 1  Sessions 1-3   Define Subagent executes    → gate passed
Week 2  Sessions 4-6   Measure Subagent executes   → gate passed
Week 3  Session 7      Analyse Subagent executes   → 40% complete, saved
Week 3  Session 8      Analyse Subagent resumes    → NOT from scratch
Week 3  Session 9      Analyse gate passed         → Improve unlocked
```

Each session:
1. Supervisor resumes on the project `thread_id` → knows full project state instantly
2. Phase Planner reads the phase artifacts → knows exactly what is missing
3. Tool Executor runs coaching → captures incrementally
4. Checkpoint saves at gate approval → ready for next session

---

### Tools Live in Subagents — Not the Supervisor

The supervisor has no tools. It only routes.

*This diagram was an early sketch of what §39 later ratified as per-phase tool binding. Tool names below are the canonical ones. Every phase carries the same universal seven; the computation tools differ per phase. Note that "fishbone" is **not** a tool — it is a coaching template surfaced through `propose_template` / `propose_diagram`, not a computation call.*

```
Supervisor (routing only — no tools)

UNIVERSAL 8 — bound to every phase executor:
  rag_lookup_methodology · rag_lookup_evidence ·
  rag_lookup_case_history · propose_template · propose_diagram ·
  check_gate_status · request_human_approval

Define (9 tools)          Measure (16 tools)              Analyse (13 tools)
└── universal 7           └── universal 7                 └── universal 7
└── calculate_expected_   ├── calculate_sigma_level       ├── t_test
    savings               ├── calculate_cpk               ├── chi_square_test
                          ├── calculate_dpmo              ├── anova
                          ├── calculate_yield_rty         ├── pearson_correlation
                          ├── calculate_ftq               └── linear_regression
                          ├── calculate_grr
                          ├── calculate_sample_size_
                          │     proportion
                          └── calculate_sample_size_mean

Improve (8 tools)         Control (12 tools)
└── universal 7           └── universal 7
└── calculate_doe_main_   ├── xbar_r_chart_limits
    effects               ├── imr_chart_limits
                          ├── p_chart_limits
                          ├── c_chart_limits
                          └── post_improvement_cpk
```

The phase subgraph builder takes the phase as a parameter so it can select the correct computation-tool subset for `bind_tools()`. See §39 for the full rationale, including why no phase exceeds 16 tools.

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

| Capability | Before | After Refactor |
|---|---|---|
| Supervisor reasoning | Implicit routing in prompt | Deterministic gate-checker + static edges (§44) |
| Phase planning | Implicit in coaching prompt | Explicit phase planner node per subagent |
| Tool encapsulation | Mixed into one graph | Per-phase `bind_tools()` subset (§39) |
| Field accumulation | Re-extraction from full history | Incremental via `PhaseState.artifacts` (§18) |
| Mid-session recovery | Lost on restart | Checkpointer resumes automatically (§1) |
| Cross-session memory | Blob loaded on each request | Checkpoint history + store for artifacts (§52a) |
| Cross-phase handoff | String concatenation into the next prompt | `store.put` / `store.get` boundary mappers (§19, §70) |

---

### Where This Stood, and Where It Stands Now
No explicit planner nodes existed at either level; planning was implicit inside coaching prompts. The refactor introduces:
- A Level 1 supervisor gate-checker plus static phase edges
- A phase planner node inside each subagent (Level 2)
- A phase executor per subagent with its phase-appropriate tool subset (Level 3 leaves)

This is refactor scope, not deferred work — see §8 for the sequence. The hierarchical subgraph architecture (§23) is the scaffold.

---

# PART 2 — AGENT CONSTRUCTION

*How the coach itself is built: the LangChain 1.0 primitives, the middleware stack assembled on `create_agent`, and the memory policy that stack enforces.*

---

## 82. LangChain 1.0 ProviderStrategy — Native Structured Output

*Source: LangChain official reference (reference.langchain.com/python/langchain/agents/structured_output/ProviderStrategy), LangChain 1.1 December 2, 2025. Verified against docs.*

> **Status: foundation reference, and the mechanism behind a lot of this document.** Structured output is what makes §29's parse-then-validate layers obsolete, what every planner and grader and validator returns, and why no ratified code parses JSON out of prose.
>
> **Two forms, and the distinction matters:**
>
> | Context | Form |
> |---|---|
> | An agent built with `create_agent` | `response_format=ProviderStrategy(Schema)` — integrated into the model-tools loop, one round-trip |
> | A plain LLM call inside a tool or middleware | The builder-style structured-output call on the model |
>
> The second form appears throughout the ratified design — query variant generation inside `rag_lookup_*` (§32, §33, §37), grader verdicts inside `DMAICGraderMiddleware` (§42), constraint verdicts in §68 — because none of those are agents, and `response_format=` has nothing to attach to.
>
> **Confirm at implementation time** that the installed `langchain` version supports all four strategies (`ToolStrategy`, `ProviderStrategy`, `NativeStrategy`, `AutoStrategy`), and note that 1.2 can infer the choice automatically from the model profile.
>
> **What structured output does not do:** guarantee the *content* is true. It guarantees shape. See §29's anti-hallucination note — this is the single most important caveat in this section.

### What Changed

Previously, structured output from `create_agent` required an additional LLM call after the main loop — expensive and slow. LangChain 1.1 integrated structured output into the main model-tools loop.

Two strategies now available:

**`ToolStrategy`** — model uses tool calling to produce structured output (works across all providers)
**`ProviderStrategy`** — model uses provider-native structured output (OpenAI, Anthropic native JSON mode)

```python
from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy, ProviderStrategy
from pydantic import BaseModel

class CoachingResponse(BaseModel):
    """Structured extraction from each coaching turn — NOT the gate document."""
    message: str                        # coaching text the Belt sees
    fields_captured: list[dict] = []    # [{field_name: str, value: Any, source: str}]
    citations: list[dict] = []          # sources referenced this turn

# Option A — ToolStrategy (universal, works everywhere)
agent = create_agent(
    "gpt-4o",
    tools=[rag_lookup_methodology],
    response_format=ToolStrategy(CoachingResponse),
    system_prompt="Coach the Belt through the Define phase."
)

# Option B — ProviderStrategy (native, more efficient where supported)
agent = create_agent(
    "gpt-4o",
    tools=[rag_lookup_methodology],
    response_format=ProviderStrategy(CoachingResponse),
    system_prompt="Coach the Belt through the Define phase."
)
```

**These examples previously used `DefineOutput`, and that was the real
error in this section — not the use of `response_format` itself.**
`DefineOutput` is the complete Define gate document. The executor runs
once per **coaching turn**; the gate document is assembled once per
**phase**. Asking the coach to emit a full `DefineOutput` on every turn
requests eight fields it has not yet coached, five of which the Belt has
not been asked about. The per-turn schema is `CoachingResponse`.

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

The Define phase currently uses a separate `.with_structured_output(...)` call for extraction. `response_format` folds that into the agent's own loop:

```python
define_agent = create_agent(
    model="operational-premium",
    tools=UNIVERSAL_TOOLS + [calculate_expected_savings],   # §39 — 8 tools for Define
    response_format=CoachingResponse,                       # ProviderStrategy auto-selected
    middleware=[                                            # §84 — the ratified eight
        BeforeModelStateInjection(),                          # before_agent — FIRST
        DMAICSkillsMiddleware(skills_dir="agent-improve/skills"),
        SummarizationMiddleware(model="azure/operational-model",
                                trigger=("tokens", 100_000),
                                keep=("messages", 20)),
        ModelRetryMiddleware(max_retries=2),                  # wrap_model_call
        ToolRetryMiddleware(max_retries=2,                    # wrap_tool_call
                            on_failure="continue"),
        ContradictionDetectionMiddleware(store=store),        # after_agent — §38
        CoherenceMiddleware(model=coherence_llm),             # after_agent — L2a
        DMAICGraderMiddleware(model=grader_llm, max_iterations=3,
                              rubric=COACHING_QUALITY_RUBRIC, # §42 — NOT a phase rubric
                              on_evaluation=write_to_step_log),
    ],
    system_prompt=DEFINE_COACHING_PROMPT,
)
```

*Corrected again 2026-08-21 on two parameter names:* `ModelRetryMiddleware`
takes **`max_retries`**, not `retries` — `retries=` does not exist and raises
at construction — and `create_agent` takes **`system_prompt`**, not `prompt`,
which `create_react_agent` took. Both verified against the LangChain
reference; record in `docs/BIBLE_VERIFICATION_LOG.md` C-1 and C-2.

*Corrected from the original example on five counts:* `HumanInTheLoopMiddleware` is replaced by graph-level interrupts (§53 bugs, §2 pattern); deepagents' `RubricMiddleware` by the custom `DMAICGraderMiddleware` (§42 Option B); the tool list uses the canonical names and the per-phase subset (§39), now **8** rather than 9 since `record_field` was retired; `BeforeModelStateInjection` moved from **last to first** and its hook type corrected to `before_agent`; and the stack grew from four to **eight** as `ModelRetryMiddleware` (§80), `ToolRetryMiddleware`, `ContradictionDetectionMiddleware` and `CoherenceMiddleware` were ratified. The canonical stack is §84.

**Middleware order is execution order for hooks of the same kind.** The original listed `BeforeModelStateInjection` last, which placed the project's established facts *after* skills loading and summarisation had already shaped the prompt — the opposite of what §38's injection-timing argument requires. State injection must fire first.

#### How `response_format` behaves at runtime

**Verified against the official LangChain documentation, August 2026.** The structured response is returned in the `structured_response` key of the agent's final state. **The agent still calls tools normally during the ReAct loop, and still writes coaching prose into `messages`.** Only the terminal response carries the additional structure. Both exist simultaneously — reading one does not cost you the other.

```python
result = agent.invoke(state)

# What the Belt sees:
result["messages"][-1]
  → "Good — I've captured your baseline at 12.3%. How was that measured?"

# What the system reads:
result["structured_response"]
  → CoachingResponse(
        message="Good — I've captured your baseline at 12.3%…",
        fields_captured=[{"field_name": "baseline_metric",
                          "value": "12.3%", "source": "belt_stated"}],
        citations=[],
    )
```

The executor node then writes `fields_captured` into `artifacts` and appends `citations` to `state["citations"]` (§18).

#### `record_field` is retired — capture is structural, not a tool call

**`record_field` is removed from the universal tools. The universal eight become the universal seven:** `rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history`, `propose_template`, `propose_diagram`, `check_gate_status`, `request_human_approval`.

**Why this is a real improvement and not a rename.** A tool call is a decision the model may or may not make. A turn where the Belt states their baseline and the coach — mid-way through a multi-hop retrieval — never calls `record_field` loses that value silently, and nothing downstream knows a capture was missed. `fields_captured` is part of the response shape: the model cannot return a well-formed `CoachingResponse` without addressing it. Capture stops being an action the coach might forget and becomes a property of every response.

**Revised per-phase tool counts (§39):**

| Phase | Universal | Phase-specific | Total |
|---|---|---|---|
| Define | 7 | 1 — `calculate_expected_savings` | **8** |
| Measure | 7 | 8 computation tools | **15** |
| Analyse | 7 | 5 computation tools | **12** |
| Improve | 7 | 1 — `calculate_doe_main_effects` | **8** |
| Control | 7 | 5 computation tools | **12** |

Every phase drops by one, and Measure moves off the top edge of the 10–15 degradation range it previously sat on at 16.

#### Complete structured output mapping

| Node / Component | Built with | Output schema | Mechanism |
|---|---|---|---|
| Phase planner | Plain LLM call | `CoachingPlan` | `model.with_structured_output(CoachingPlan)` |
| **Phase executor (coach)** | **`create_agent` + tools** | **`CoachingResponse`** | **`response_format=CoachingResponse`** (ProviderStrategy auto-selected) |
| Validation Layer 1 (coherence) | Plain LLM call | `CoherenceResult` | `model.with_structured_output(...)` |
| Validation Layer 3 (constraints) | Plain LLM call | `ConstraintCheckResult` | `model.with_structured_output(...)` |
| Validation Layer 4 (gate grader) | Plain LLM call | `GraderVerdict` | `model.with_structured_output(...)` |
| `gate_review` | **No LLM** | Interrupt payload | `interrupt()` |
| `gate_apply` — policy advisory | Plain LLM call | `PolicyAdvisoryResult` | `model.with_structured_output(...)` |
| `DMAICGraderMiddleware` | Plain LLM call inside middleware | `CoachingGraderVerdict` | `model.with_structured_output(...)` |
| Inside `rag_lookup_*` | Plain LLM call | `QueryVariants` | `model.with_structured_output(...)` |
| Gate document assembly | **No LLM call** | `DefineOutput` … `ControlOutput` | `DefineOutput(**artifacts)` — Pydantic validation only |

**Three distinct mechanisms, and the distinction is what this section exists to fix:**

- **`response_format=CoachingResponse` on `create_agent`** — structured extraction on **every turn**, alongside normal coaching text, inside the agent's own loop.
- **`model.with_structured_output(Schema)`** — a plain LLM call wrapped for a **one-shot** structured response, inside tools, middleware, and non-agent nodes. There is no agent loop to attach `response_format` to in any of those places.
- **`DefineOutput(**artifacts)`** — Pydantic **validation at gate time, no LLM call at all**. The values were captured turn by turn; assembly only checks and packages them.

---

### The Five Canonical Gate Document Schemas

**One definition per phase, in `phases/{phase}/schema.py`.** Two conflicting `DefineOutput` definitions previously existed in this document — one here in §82 and one in §44 — neither matching the ratified fields, both using `float` against Finding 3. `MeasureOutput`, `AnalyseOutput`, `ImproveOutput` and `ControlOutput` were referenced repeatedly and defined nowhere.

**Every field is `str`** except the three cross-phase reference dicts (§17 Finding 5). **Every schema carries the same four gate-metadata fields.** Tier classification per §17 Finding 11.

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

**`citations` and `uploads` were the cross-check catch.** Both were added to `PhaseState` by Finding 8 and then omitted from the Output schemas — so the evidence trail reached state and stopped there, never arriving in the document that is supposed to record what the phase was grounded in. `computation_results` and `acknowledged_gaps` had the same shape of problem from the other direction: they are assembled *at gate time* from `artifacts` and the validation stack, not captured per turn by `CoachingResponse`, and nothing said where they came from.

### Gate Assembly — All Five Phases

Runs in `gate_apply` after Belt approval. **No LLM call.**

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

**One pattern across all five, and the access style encodes the tier:**

| Field kind | Access | If absent |
|---|---|---|
| Tier 1 | `artifacts["field"]` | **`KeyError`** — correct; Layer 2b should have blocked the gate |
| Tier 2 | `artifacts.get("field", "")` | Empty string — records that the Belt proceeded without it |
| Cross-phase dict | `artifacts.get("field", {})` | Empty dict |
| Gate metadata | Always the same four sources | `artifacts["computation_results"]`, `validation_stack.get_acknowledged_gaps()`, `state["citations"]`, `state["uploads"]` |

**Letting a Tier 1 `KeyError` propagate is deliberate.** It signals a bug in the validation stack — Layer 2b passed a gate missing a field it must block on. Defaulting Tier 1 to `""` instead would write a gate document with a silently empty required field into the store, and the next phase would build on it.

---

### Cross-Reference Impact on Existing Sections

| Existing Section | Update Applied |
|---|---|
| §44 (typed boundaries) | `ProviderStrategy` preferred for `DefineOutput`, `MeasureOutput`, etc. |
| §42 (grader) | Works with either strategy; the grader's own verdict uses the builder-style call, since middleware is not an agent |
| §29 (OutputFixingParser) | Obsolete — nothing left to fix when the provider guarantees the schema |
| §45 (drift registry) | `pattern-2` blocks the builder-style call; the rule needs scoping to agent calls when CLAUDE.md §4.6 is authored |

### Gap Register Note
No new gap number — an architectural refinement that reduces latency and cost for every gate transition without changing graph structure.

---

## 80. LangChain 1.0 AgentMiddleware — The Six Hooks Foundation

*Source: LangChain official reference (reference.langchain.com/python/langchain/agents/middleware/types/AgentMiddleware), LangChain 1.0 GA October 22, 2025, LangChain 1.1 December 2, 2025. Verified against docs and multiple independent 2026 sources.*

> **Status: foundation reference. Preserve as-is — no decision needed.** These six hooks are what the entire ratified middleware stack is built on, and five of the eight middlewares are custom, so this is not background reading. See §84 for the complete stack.

### Why This Section Exists

§42 documented the rubric grader and §48 introduced middleware conceptually. Neither documented the **six hooks that all middleware — built-in and custom — is built from**. Understanding these primitives is a prerequisite for writing `DMAICGraderMiddleware` (§42), `DMAICSkillsMiddleware` (§84), and the `before_model` state injection (§38).

**Which hook each ratified middleware uses:**

| Middleware | Hook | Section |
|---|---|---|
| `DMAICSkillsMiddleware` | `before_agent` (Level 1 registration), tool call for Level 2 | §83, §84 |
| `DMAICGraderMiddleware` | `after_agent` | §42 |
| `SummarizationMiddleware` | `before_model` | §36, §53 |
| `before_model` state injection | `before_model` | §38 |

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

**Agent Improve uses built-in middleware wherever possible** — `SummarizationMiddleware` is adopted as shipped (§36). Custom middleware is reserved for genuinely domain-specific logic: rubric grading against DMAIC phase criteria (§42), progressive disclosure of phase skills (§84), and structured project-state injection (§38).

Two built-ins are deliberately **not** used:
- **`HumanInTheLoopMiddleware`** — two confirmed bugs hit our exact use case; §2 uses graph-level `interrupt()` instead (§53).
- **`LLMToolSelectorMiddleware`** — per-phase tool binding (§39) already keeps every coach at 8–15 tools, inside the range where selection quality holds. Adding a selector LLM would spend a model call to solve a problem we solved structurally.

**`ModelRetryMiddleware` is ADOPTED** as the invisible-retry tier of §67's fallback chain, where retry is a mechanical concern rather than a coaching event. `max_retries=2`, exponential backoff, on `wrap_model_call`. **The keyword is `max_retries`, not `retries`** — corrected 2026-08-21 after verification against the LangChain reference; `retries=` does not exist on this class.

*This was previously recorded as "worth evaluating" with no decision attached.* The evaluation is short: without it we hand-write try/except, a sleep with backoff, and a counter increment around every model call — mechanical plumbing the built-in already provides, on a hook designed for exactly this. The rule "prefer built-in middleware wherever it exists" decides it.

**The distinction that matters, and the reason this is not a duplicate of §67:**

| | `ModelRetryMiddleware` | The fallback chain (§67) |
|---|---|---|
| Handles | Mechanical failure — the network flaked | Service-level failure |
| Action | Retry **the same call** | **Swap the model**: gpt-4o → gpt-4o-mini → cache → degraded |
| Visible to the Belt | Never | Degraded mode is |

Different tiers, different mechanisms. The middleware sits below the chain and absorbs the transient failures that never need to reach it.

---

### The Composition Order Rule

```python
# GENERIC LANGCHAIN ILLUSTRATION — not Agent Improve's stack.
# Agent Improve's ratified eight-middleware stack is in §84.
# HumanInTheLoopMiddleware appears here only to show ordering; it is BANNED
# for our gates (§53 — edit/reject are broken in subgraph contexts).
agent = create_agent(
    model="gpt-4o",
    tools=[...],
    middleware=[
        PIIMiddleware(),
        SummarizationMiddleware(),
        ModelRetryMiddleware(max_retries=2),
        HumanInTheLoopMiddleware(...),
        GateValidationMiddleware(...)
    ]
)
```

Middleware compose like nested wrappers. First in the list is the outermost layer. This ordering matters — PII redaction MUST fire before summarization sees the content, or PII leaks into summaries.

*`max_retries=2` throughout this document, including in illustrations —
`ModelRetryMiddleware` and `CoherenceMiddleware` each carry an independent
2-retry cap (§84), and an example showing 3 invites the number to be copied.
**The keyword itself was wrong throughout until 2026-08-21**: this document
wrote `retries=`, which does not exist on `ModelRetryMiddleware`. The same
reasoning applies to the keyword as to the number — an illustration is
copied.*

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

> **Status: foundation reference. Preserve as-is — no decision needed.** Typed content blocks are how LangGraph nodes communicate through messages, and reading `response.content_blocks` rather than string-parsing `response.content` is enforced by the drift-check registry (pattern-3). See §45.

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

## 42. DMAICGraderMiddleware — Self-Evaluation and Correction Loop

*Source: Anthropic Blog — "Introducing Rubrics: Build Agents that Evaluate and Correct Their Work", June 2, 2026*
*Authors: S. Seshadri, S. Runkle*

> **Ratified: Option B — a custom `DMAICGraderMiddleware` on `create_agent`, not deepagents' `RubricMiddleware`.** The pattern is adopted; the dependency is not. Rationale and the web verification behind it are below the pedagogy.

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

---

### Decision 1 — Option B: Custom Middleware on `create_agent`

**Web-verified 2026-07-30:**

- deepagents is **pre-1.0** (stable 0.6.10, alpha 0.7.0a7). From GitHub issue #4219 (24 June 2026): *"APIs may still evolve between minor versions."* Breaking changes were shipping weekly in the 0.7 alpha line.
- `RubricMiddleware` requires `create_deep_agent`, **not** `create_agent`. Confirmed across all Tier 1 documentation.
- `create_agent` exposes the same six middleware hooks (`before_agent`, `after_agent`, `before_model`, `after_model`, `wrap_model_call`, `wrap_tool_call`) that `RubricMiddleware` uses internally. Custom middleware on `create_agent` is the GA-stable equivalent.
- From the deepagents README: *"LangGraph is the graph runtime. LangChain's create_agent is a minimal agent harness on top of it. Deep Agents is a more opinionated harness on top of create_agent."* And: *"Use create_agent when you want a lighter harness without the bundled middleware."*
- Anthropic's own guidance: *"find the simplest solution possible, and only increase complexity when simpler approaches fall short."*

Sources: `reference.langchain.com/python/deepagents/middleware/rubric/RubricMiddleware`, `docs.langchain.com/oss/python/deepagents/rubric`, `github.com/langchain-ai/deepagents/issues/4219`, `github.com/langchain-ai/deepagents/releases`, `langchain.com/blog/introducing-rubrics-for-deepagents`, `anthropic.com/research/building-effective-agents`.

**Why Option B:**

| | Option A — adopt deepagents | Option B — custom middleware *(selected)* |
|---|---|---|
| Dependency risk | Pre-1.0, breaking changes shipping | None — `create_agent` hooks are GA |
| What comes along | Filesystem tools, sub-agent spawning, code interpreter, harness profiles — all unused, and some conflicting with our architecture | Nothing |
| Implementation cost | 2–3 days | 3–4 days |
| Migration path | — | When deepagents reaches 1.0, swap to the official `RubricMiddleware` — same hooks, near-drop-in |

The cost difference is roughly one day. Against an end-of-August production target, carrying a pre-1.0 dependency with weekly breaking changes is the larger risk. *If the timeline were end of Q4, this would flip to Option A — deepagents 1.0 would likely be out by then.*

### Decision 2 — Grader and Policy Advisory Are Both Kept

They are not redundant, because they check different actors' work at different moments:

| | Checks | Fires | Blocking? |
|---|---|---|---|
| `DMAICGraderMiddleware` | The **AI's** coaching, against COACHING_QUALITY_RUBRIC | Every turn, before the Belt sees anything | Yes — retries the coach, cap 3 |
| Policy advisory | The **Belt's** edits, against policy and prior gate values | Step 6, after the Belt edits | No — second opinion, Belt may override |

Two different actors producing output at two different moments. Each needs its own quality check. See §2 for the full nine-step sequence.

---

### Implementation Pattern

```python
# NOT THIS — RubricMiddleware requires create_deep_agent, which brings
# a pre-1.0 dependency and a large unused harness.
#
#   from deepagents import RubricMiddleware, create_deep_agent
#   gate_grader = RubricMiddleware(model=..., max_iterations=3)
#   coaching_agent = create_deep_agent(model=..., middleware=[gate_grader])

# THIS — custom middleware on the GA-stable create_agent
from langchain.agents import create_agent
from langchain.agents.middleware import AgentMiddleware, SummarizationMiddleware
from pydantic import BaseModel
from typing import Literal


class CriterionVerdict(BaseModel):
    criterion: str
    tier: int                                          # 1 or 2 — Decision 4
    status: Literal["pass", "warning", "fail"]         # "warning" — Decision 4
    feedback: str                                      # empty if status == "pass"


class GraderVerdict(BaseModel):
    result: Literal["satisfied", "needs_revision", "failed"]
    criteria: list[CriterionVerdict]
    explanation: str


class DMAICGraderMiddleware(AgentMiddleware):
    def __init__(self, model, max_iterations=3, on_evaluation=None):
        self.grader_llm = model.with_structured_output(GraderVerdict)
        self.max_iterations = max_iterations
        self.on_evaluation = on_evaluation
        self._iteration = 0

    def after_agent(self, state, runtime):
        rubric = state.get("rubric")
        if not rubric:
            return None                      # no rubric, no grading

        verdict = self.grader_llm.invoke(
            f"Evaluate the agent's output against this rubric:\n{rubric}\n\n"
            f"Belt level: {state['belt_level']}\n"      # Decision 5
            f"Transcript:\n{format_messages(state['messages'])}"
        )
        self._iteration += 1

        if self.on_evaluation:
            self.on_evaluation({"iteration": self._iteration, **verdict.dict()})

        # Only Tier 1 can fail. Tier 2 warns and does not block.
        failed = [c for c in verdict.criteria if c.status == "fail"]
        if not failed or self._iteration >= self.max_iterations:
            return None                      # pass through — warnings survive

        feedback = "\n".join(f"- {c.criterion}: {c.feedback}" for c in failed)
        # … inject as a HumanMessage and return control to the agent loop
```

**`warning` is what makes a gate passable with a known gap.** The loop
above re-enters only on `fail`, so a Tier 2 criterion the Belt has
chosen not to satisfy cannot trap the coach in a retry cycle it has no
way to exit — the Belt has already decided, and the gap is recorded in
the gate document instead (Decision 4).

> **This is a reference sketch, not production code.** The exact `after_agent` mechanics for retry signalling must match `create_agent`'s return-value contract. Verify against `reference.langchain.com/python/langchain/agents/middleware` before implementing.

The grader runs on `operational-model` (gpt-4o-mini) while the coach runs on `operational-premium` (gpt-4o) — cheap grading, quality coaching. That part of the original pattern was right and is preserved.

---

### Decision 3 — The Five DMAIC Phase Rubrics

*Stored as constants; the grader receives the phase-appropriate rubric based on `current_phase`. Rubrics can evolve from production experience without touching the grader mechanism.*

**Every criterion carries a tier.** Tier 1 blocks the gate at Layer 2b; Tier 2 produces a warning the Belt may proceed past with a recorded gap. See Decision 4 below for why, and ARCHITECTURE.md §13 for the consolidated table.

```python
DEFINE_RUBRIC = """
[TIER 1] problem_statement: measurable problem with baseline and target,
         consolidated into a single statement (the 5W2H sub-fields feed it)
[TIER 1] voc_summary: customer perspective — who is affected and how they judge it
[TIER 1] project_scope: explicit inclusions and exclusions with process boundaries
[TIER 1] goal_statement: SMART (Specific, Measurable, Achievable, Relevant, Time-bound)
[TIER 1] process_map_sipoc: DICT — suppliers, inputs, process_steps, outputs,
         customers, process_kpis. End-to-end, not a fragment
[TIER 1] issues_and_barriers: real project blockers — sponsor availability, data
         access, resource constraints. "None identified at this stage" is an
         acceptable answer; silence is not
[TIER 2] business_case: quantified business impact in COPQ terms — cost of poor
         quality, not a qualitative assertion of importance
[TIER 2] team: Belt, sponsor, and 2+ team members with named roles
[TIER 2] baseline_metric / target_metric: current and target values
[TIER 2] secondary_metrics: what could get worse if this improvement succeeds
"""

MEASURE_RUBRIC = """
[TIER 1] baseline_mean: current-state value with units, as the Belt stated it
[TIER 1] data_collection_plan: sample size, frequency, and responsible person named
[TIER 1] xy_matrix_summary: evidence that prioritisation of the X's was done
[TIER 1] vital_few_xs: the ranked X's carried into Analyse, and why
[TIER 1] detailed_process_map: DICT — steps, cycle_times, resources,
         value_vs_waste, measurement_points, baseline_kpis
[TIER 1] stability_assessment: checked BEFORE capability — an unstable process
         has special causes and its Cpk is not a capability figure
[TIER 1] issues_and_barriers: real project blockers
[TIER 2] baseline_sigma: calculated sigma level from the baseline data
[TIER 2] measurement_system_validated: GR&R or equivalent evidence provided
[TIER 2] secondary_metrics: what could get worse if this improvement succeeds
"""

ANALYSE_RUBRIC = """
[TIER 1] root_cause_statement: specific and actionable, not a category
[TIER 1] root_cause_validation: statistical or observational evidence, not opinion
[TIER 2] causal_hypothesis: DICT — carries references_phase / references_field /
         references_value linking to Measure's baseline. Verified deterministically.
[TIER 1] practical_significance: how much of the problem this root cause explains
         — the eBook's second gate, in series with statistical significance
[TIER 1] issues_and_barriers: real project blockers
[TIER 2] ruled_out_causes: alternatives considered and rejected, with rationale
[TIER 2] statistical_problem_statement: the formal hypothesis, all Belts
[TIER 2] process_owner_buyin: the owner accepts these root causes
[TIER 2] secondary_metrics: what could get worse if this improvement succeeds
"""

IMPROVE_RUBRIC = """
[TIER 1] selected_solution: criteria-based selection documented (impact, effort, risk)
[TIER 1] pilot_result: measurable improvement demonstrated with data — practical
         AND statistical significance, not one standing in for the other
[TIER 1] experiment_justification: DOE conducted / simplified experiment / none
         needed — all three valid, but the Belt must have decided
[TIER 1] issues_and_barriers: real project blockers
[TIER 2] solution_linked_to_root_cause: DICT — references Analyse's root_cause_statement
[TIER 2] implementation_plan: timeline, responsible person, resource requirements
[TIER 2] explanatory_power: how much of the problem the selected X's explain
[TIER 2] process_owner_buyin: the owner accepts this solution
[TIER 2] secondary_metrics: what could get worse if this improvement succeeds
[TIER 2 · BB ONLY] DOE
"""

CONTROL_RUBRIC = """
[TIER 1] control_plan: DICT — five sub-plans (documentation, monitoring, response,
         training, aligning_systems). The grader checks all five are populated
[TIER 1] issues_and_barriers: real project blockers
[TIER 1] post_improvement_metric: DICT — the measured post-improvement value, carrying
         references to Measure's baseline so the shift is verified, not asserted
[TIER 2] improvement_delta: the change from baseline, stated explicitly
[TIER 2] financial_impact_verified: quantified saving (book pp677–679)
[TIER 2] sustainability_check: process defined for maintaining the gains
[TIER 2] handover_documented: process owner accepted responsibility, named individual
[TIER 2] lessons_learned: what would be done differently — feeds the case index
[TIER 2] transferability: where else this applies — yokoten, feeds rag_lookup_case_history
[TIER 2] project_signoff: Champion + Belt + Finance agree the project is complete
[TIER 2] secondary_metrics: re-checked at close — "repeat same process for
         secondary metrics"
"""
```

These rubrics existed implicitly in the pre-refactor gate validation logic. Making them explicit and feeding them to a grader is the upgrade.

**Control gained three fields, and the reason is not completeness for its own sake.** A DMAIC project that cannot show the baseline moved has not demonstrated anything — it has documented an intention. The eBook (book pp677–679) requires verified financial impact for the same reason. `post_improvement_metric` is Tier 1 and carries the reference to Measure's baseline, so the grader verifies the shift by reading Measure's gate document rather than accepting the claim; `improvement_delta` and `financial_impact_verified` are Tier 2, because the improvement is real without them but the project is not finished.

**Three criteria are checked mechanically, not by judgment.** `causal_hypothesis`, `solution_linked_to_root_cause` and `post_improvement_metric` are dicts carrying `references_phase`, `references_field` and `references_value` (§17, ARCHITECTURE.md §4.7). The grader reads the referenced phase's gate document from the store and checks the named field holds the named value, failing with an exact message:

```
references baseline_mean = 12.3% but the Measure gate document
shows baseline_mean = 15%.
```

**Why deterministic rather than LLM reasoning for these three.** They are the highest-stakes checks in DMAIC — a broken link means the project was built on the wrong foundation, and nothing downstream surfaces it. LLM linkage checking fails exactly where it is needed: when the Belt's terminology shifts between phases ("high rework" in Analyse against "12.3% invoice error rate" in Measure), which is the common case, not the edge case.

**Criteria depending on a computation are checked the same way**, by scanning `artifacts["computation_results"]` for the relevant `tool` entry — `t_test` for a hypothesis test, `calculate_grr` for measurement system validation, `calculate_cpk` for capability (§17, ARCHITECTURE.md §4.8). Before that list existed, a Belt could run `t_test`, get p=0.001, and have the result vanish into the conversation with the grader unable to confirm the test was ever run.

---

### Decision 4 — Two Tiers, and a Third Verdict Status

**The problem this fixes is a contradiction, not a gap.** Layer 2b blocked on a required-field list. Layer 2d graded against a rubric. The two sets were not the same set — so a phase could pass the gate and then be failed by the grader on a criterion the gate had never asked for, with no defined resolution.

| Tier | Layer 2b (presence) | Layer 2d (grader) | The Belt's options |
|---|---|---|---|
| **Tier 1** | **Blocks** — gate cannot pass | May return `fail` | Must supply the field |
| **Tier 2** | Not checked | At worst `warning` | Add it now, or proceed with an acknowledged gap |

**`CriterionVerdict` gains a third status and a tier:**

```python
class CriterionVerdict(BaseModel):
    criterion: str
    tier:      int                                   # 1 or 2
    status:    Literal["pass", "warning", "fail"]
    feedback:  str
```

**A gate may pass with warnings; it may never pass with failures.** Only Tier 1 criteria can produce `fail`.

**A Tier 2 gap the Belt proceeds past is recorded, not dropped.** `gate_apply_node` writes it into the gate document:

```python
"acknowledged_gaps": ["baseline_sigma — Belt accepted gap"]
```

The next phase's planner reads that from the store and factors it in — a Measure phase that proceeded without `baseline_sigma` is something Analyse should know when it comes to validate a root cause against process capability.

**The argument for two tiers rather than one strict list, in the user's framing:** a rigid gate that blocks on every criterion teaches Belts to fill fields mechanically. That produces complete gate documents and worse projects, which is the opposite of what the gate is for. Tier 1 catches genuinely incomplete phases. Tier 2 coaches toward best practice while respecting the Belt's judgment about their own project — and the audit trail then shows conscious decisions rather than silent omissions, which is the more useful record for a quality system.

### Decision 5 — The Grader Is Belt-Level Aware

Coaching scope is **both** Green Belt and Black Belt, and the tier system is what lets one rubric serve both. The grader reads `belt_level` from the case record:

```
if belt_level == "Black Belt":
    flag DOE as a Tier 2 recommendation
if belt_level == "Green Belt":
    suppress it — do not recommend heavy methodology GB isn't trained for
```

| Item | Green Belt | Black Belt |
|---|---|---|
| DOE | Suppressed | Tier 2 |

**DOE is the only belt-gated item left.** Five others left this table across v2.2.11 and v2.2.12, and it is worth recording where each went:

| Item | Was | Now |
|---|---|---|
| X-Y matrix | BB-only Tier 2 rubric item | **`xy_matrix_summary`, Tier 1 field, all Belts** — it produces the vital few X's Analyse cannot start without |
| Statistical problem statement | BB-only, and placed in Define | **`statistical_problem_statement`, Tier 2 field, all Belts, in Analyse** — where the eBook asks it |
| FMEA / updated FMEA | BB-only Tier 2 | **Removed entirely.** Not tracked in any schema; §17 Finding 24 records the reasoning |
| Stability / special causes | Tier 2, strong warning, both levels | **`stability_assessment`, Tier 1 field, both levels.** Never suppressed for a GB — what changed is that it is no longer advisory |
| Three-party sign-off | Tier 2 rubric item, no field | **`project_signoff`, Tier 2 field on `ControlOutput`.** Still simplified for a GB in coaching, but now recorded |

DOE is a heavy methodology — in the user's words, "are heavy." Recommending it to a Green Belt produces either a badly designed experiment or a Belt who learns to ignore the grader, and both cost more than the omission. Note that `experiment_justification` (Tier 1, all Belts — §17 Finding 26) still requires a GB to *decide* about experimentation; what is suppressed is the recommendation to run a DOE, not the obligation to think about one.

**Stability is not suppressed for either level, and is no longer advisory.** `stability_assessment` is a Tier 1 field for both belt levels: a baseline computed across an unstable process is not a baseline, and that holds regardless of training.

Note the contrast with §36's decision to leave `belt_level` **off** as a retrieval filter on `improve_case_index`. Filtering what a Belt may *learn from* over-narrows — a Green Belt often benefits from a Black Belt case. Adjusting what the grader *asks of them* does not have that failure mode.

**Items from the MBB eBook covered without new fields:**

| eBook item | Covered by |
|---|---|
| COPQ | Strengthened `business_case` rubric wording |
| Financial verification | `financial_impact_verified` |
| Hypothesis test results | `artifacts["computation_results"]` |
| Handover | `handover_documented` |
| Process maps | **Superseded** — now `process_map_sipoc` (Define) and `detailed_process_map` (Measure), both Tier 1 fields (§17 Finding 26). `propose_diagram` still renders them |
| Short/long-term capability | `calculate_cpk`, results in `computation_results` |
| Practical + statistical significance | Strengthened `pilot_result` rubric wording |

---

### Decision 6 — Iteration Cap and Temperature Discipline

| Setting | Value | Why |
|---|---|---|
| Grader iteration cap | 3 | On `max_iterations_reached`, output passes through with a warning flag visible to the Belt. Matches §54 and deepagents defaults. |
| Grader temperature | 0.1 | The same gate document must receive the same verdict across runs — required for the regression testing in §75 |
| Coach temperature | 0.5–0.7 | Natural language variation improves the Belt's coaching experience |
| Extraction and field validators | 0.0–0.2 | Same consistency rationale as the grader |

### Decision 7 — `COACHING_QUALITY_RUBRIC` and the Computation Tool Coaching Pattern

**`DMAICGraderMiddleware`'s rubric is a single constant, shared across all five phases** — distinct from the five `PHASE_RUBRIC` constants Layer 2d uses (Decision 4, Finding 18). It grades the coach's *process*, not the gate document.

```python
COACHING_QUALITY_RUBRIC = """
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
"""
```

**The last three criteria are the coaching-behaviour ones, and they exist because of real gaps in what "coaching" was specified to mean.**

**Show before asking.** Describing what good looks like in a SKILL.md tells the *developer*; it does not tell the Belt. The coach shows a concrete completed example, explains why it works, then invites the Belt to build theirs in the same shape. One turn to a good answer instead of three turns of ask-and-correct.

**No external URLs.** A model asked about methodology will happily produce links from its training data — stale, unverifiable, and outside the grounding contract of §39. Methodology comes from `rag_lookup_methodology` and is woven into the coach's own voice, not pasted as a citation block the Belt has to chase.

**Educate before computing.** The original framing was: The problem, in the user's framing:

> "We need to ensure the phase_executor node not only guides the Belt but explains them how to prepare for `linear_regression` and how to collect the data… and interpret it and give it back to the Belt with visual and text explanation. **This is a critical part of the coach who does not only ask questions but assists the Belt in every aspect.**"

A coach that asks good questions and then returns `t_statistic: 4.23, p_value: 0.001` has not coached. The Belt has a number they cannot act on and cannot defend at a gate.

#### The seven-step pattern — every computation tool, every time

| # | Step | What the coach does |
|---|---|---|
| 1 | **Educate on the concept** | What this *is*, in plain language, with a real-world analogy — and what the output numbers will mean, before any are produced |
| 2 | **Explain why now** | Why the Belt needs this analysis at this point in their project |
| 3 | **Guide data preparation** | What format the tool needs; check what the Belt already uploaded via `rag_lookup_evidence` |
| 4 | **Run the computation** | Call the tool — the Belt sees the call happening |
| 5 | **Interpret their result** | Translate the statistical output into plain language |
| 6 | **Visualise** | Call `propose_diagram` to show it graphically, where applicable |
| 7 | **Coach the next move** | What this means for the project, and what happens next |

**Step 1 was added after the first SKILL.md review** and is the correction that matters most. The original pattern opened with "explain why", which quietly assumes the Belt already knows what a Cpk or a p-value *is*. Most do not — Agent Improve exists to serve teams with no Six Sigma qualification (§1 of ARCHITECTURE.md). A Belt told "this matters because it shows capability" and then handed `Cpk = 0.82` has learned nothing: they cannot judge whether 0.82 is good and cannot defend it at a gate.

Educating first also does the interpretation work in advance. By the time the number arrives the Belt already knows that above 1.33 is comfortable and below 1.0 is not, so step 5 confirms a frame they hold rather than introducing one alongside a result they are still trying to read.

**Steps 1, 5 and 7 are the coaching.** Steps 2, 3, 4 and 6 are mechanics that most implementations would get right by default; the three that carry the teaching are exactly the three a model under-serves when it is optimising for a correct answer.

**This applies to all 20 computation tools (§39), not only regression:**

| Phase | Tool | Step 1 — how the coach opens |
|---|---|---|
| Define | `calculate_expected_savings` | "Let's estimate the financial impact. If each rework costs €X and you have Y per month…" |
| Measure | `calculate_sigma_level` | "Your sigma level tells us how capable the process is. Let me calculate it from your defect data…" |
| Measure | `calculate_cpk` | "Cpk shows whether your process fits within the spec limits. You'll need USL, LSL, mean and standard deviation…" |
| Measure | `calculate_grr` | "Before we trust the data, we need to verify the measurement system. GR&R checks whether different people measuring the same thing get the same result…" |
| Analyse | `t_test` | "To prove the training gap is real, we'll compare error rates between the two groups statistically…" |
| Analyse | `linear_regression` | "Let's see how strongly training hours predict error rate. You'll need two columns of data…" |
| Control | `xbar_r_chart_limits` | "Control charts will monitor whether the improvement holds. I'll calculate the control limits from your post-improvement data…" |
| Control | `imr_chart_limits` | "You have one reading per period rather than batches, so we'll use an individuals chart — same idea, limits from the point-to-point movement…" |

**Why the rubric criterion rather than a prompt instruction.** A system-prompt line saying "explain your computations" is advisory and degrades over a long conversation. The middleware grader fires on **every turn** via `after_agent`, so a raw-output dump is caught and retried **before the Belt sees it** — the same argument that put coherence checking at Layer 1 rather than in a prompt (§68).

#### Consequence for SKILL.md authoring

**Each phase's SKILL.md must carry the seven-step sequence for every computation tool in that phase's `allowed-tools`** (§83, §84). At 20–40 lines of coaching guidance per tool, Measure's eight computation tools alone are 160–320 lines — **this is the most content-heavy part of each skill.**

The BB eBook extractions under `agent-improve/skills/extraction/` supply the methodology content; the skill shapes it into the seven-step conversation. That is the division of labour between the extraction files and the skills: extraction is *what the methodology says*, the skill is *how the coach says it*.

**Step 2 is where §60's data-collection coaching actually lives.** The eBook teaches what data a tool needs; the coach teaches the Belt to collect and structure it. Since `improve_evidence_index` is the only channel through which external data enters AgentLean (§39, §63), the quality of step 2 across the 20 tools is the quality of the system's grounding.

---

### Audit Trail Integration

The `on_evaluation` callback writes each grading iteration into `step_log` (§18). This gives the DMAIC audit trail full visibility into what the grader found, how many iterations ran, and what the final verdict was — **without leaking grader internals into the coach's messages or the Belt's view.**

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
- The grader can call tools to gather hard evidence before its verdict — this is where §48's `DMAICGateValidator` static methods fit, as a deterministic pre-filter
- Each criterion gets its own verdict — the agent knows exactly what to fix
- Agent outputs are probabilistic — the same prompt can succeed or fail across runs — a grader loop handles that variance systematically
- deepagents' implementation is in beta; ours is not a dependency

### Where the Grader Sits in the Gate Stack

The grader is **Layer 2d of four** (§68), not the whole of gate validation:

```
Step 2a  Coherence check        lightweight LLM, every turn      §69
Step 2b  Field presence         deterministic, DMAICGateValidator §48
Step 2c  Constraint validation  lightweight LLM                   §68
Step 2d  Quality rubric         gate document grader, PHASE_RUBRIC  this section
```

Cheapest first. Each layer fires only if the previous passes. The shared cap is 3 attempts across all four, with accumulated feedback — not three per layer.

### Where It Sits in the Middleware Stack

`DMAICGraderMiddleware` is **middleware on the `create_agent` call — not a subgraph node** (Terminology Reference). It is one of four (§84):

| Middleware | Source |
|---|---|
| `DMAICSkillsMiddleware` | Custom — §83, §84 |
| `DMAICGraderMiddleware` | Custom — this section |
| `SummarizationMiddleware` | LangChain core — §36 |
| `before_model` state injection | Custom — §38 |

### Gap Register
**Gap 23 — closes in the refactor** via Option B custom middleware. The original "deferred to post-completion refactor" no longer applies. The four-layer stack of §68 is the full implementation target for this gap.

*Cross-references: §2 (the nine-step HITL pattern the grader is step 2 of), §29 (superseded by the grader for quality evaluation), §48 (`DMAICGateValidator` as the deterministic layer, and the reflection/consensus distinction), §54 (corrections incorporated here), §68 (the complete four-layer stack), §75 (why grader temperature must be 0.1), §80 (the hooks this middleware uses), §84 (the full middleware stack).*

---

## 83. Agent Skills Specification — SKILL.md Standard

*Source: LangChain official docs (docs.langchain.com/oss/python/deepagents/skills), agentskills.io specification, LangChain Skills repository (github.com/langchain-ai/langchain-skills). Verified May-June 2026.*

> **Status: ratified. Each DMAIC phase becomes a skill following the agentskills.io SKILL.md standard.**
>
> ```
> agent-improve/skills/
>   dmaic-define-phase/SKILL.md
>   dmaic-measure-phase/SKILL.md
>   dmaic-analyse-phase/SKILL.md
>   dmaic-improve-phase/SKILL.md
>   dmaic-control-phase/SKILL.md
> ```
>
> **Each skill's `allowed-tools` lists that phase's computation tools plus the universal seven** — mirroring the per-phase binding of §39, so the skill and the tool binding cannot drift apart.
>
> **Storage backend: `FilesystemBackend`** — git-versioned alongside the code, which means skill changes are reviewable in the same PR as the code that depends on them. `ContextHubBackend` (LangSmith) is deferred to a multi-deployment stage.
>
> **Progressive disclosure, three levels:**
>
> | Level | When | What loads |
> |---|---|---|
> | 1 | Startup | Skill *descriptions* only — under 2K tokens for all five combined |
> | 2 | On demand | Full phase instructions, when the coach enters that phase |
> | 3 | On demand | Reference files, when explicitly needed |
>
> **Each skill contains:** phase coaching instructions, the phase rubric (§42), the phase-specific computation tools list (§39), and coaching strategy guidance.
>
> **Authored jointly, like the eval dataset (§75)** — these encode Black Belt domain judgment, not architecture. Drafted alongside the refactor rather than generated from it.

### What Changed

§26 introduced Skills conceptually as part of AgentLean's governance framework. Since then an **official Agent Skills specification** has emerged at agentskills.io, adopted by LangChain, Claude Code, Cursor, and other agent frameworks.

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

| Existing Section | Update Applied |
|---|---|
| §26 (course assignment record) | The governance framing there predates the formal spec; the spec is now authoritative |
| §45 (`/verify-current-version`) | Already implemented as a skill at `.claude/skills/verify-current-version/SKILL.md` — note this is a **Claude Code** skill for the development workflow, distinct from the five **runtime** DMAIC phase skills this section defines |
| §42 (system prompt bloat) | Solved by progressive disclosure — see §84 for the middleware |
| §39 (per-phase tools) | Each skill's `allowed-tools` mirrors the phase's tool subset |

### Gap Register Note
No new gap number — this section formalises the specification the five DMAIC phase skills follow. Note the two distinct kinds of skill in this project: **development-workflow skills** under `.claude/skills/` (Claude Code, §45) and **runtime coaching skills** under `agent-improve/skills/` (loaded by the coach, this section). Same file format, different consumers.

---

## 84. SkillsMiddleware in deepagents — Solving System Prompt Bloat

*Source: LangChain official reference (reference.langchain.com/python/deepagents), deepagents 0.6.10 May 2026. Verified against docs.*

> **Status: ratified — same Option B approach as §42. A custom `DMAICSkillsMiddleware` on `create_agent` hooks, not deepagents adoption.**
>
> The pattern is right and the problem is real. The dependency is the issue: deepagents is pre-1.0 with breaking changes shipping weekly (§42), and adopting it for skills would mean adopting it for everything — `create_deep_agent` is all-or-nothing.
>
> **Implementation:** read SKILL.md frontmatter at startup (Level 1), register `load_skill(name)` as a tool the coach can call (Level 2 on demand). Same progressive disclosure as §83, implemented as middleware on `create_agent`.
>
> **Migration path:** when deepagents reaches 1.0, migrate from the custom middleware to the official `SkillsMiddleware` — the same path as `DMAICGraderMiddleware` → `RubricMiddleware`. Both migrations happen together or not at all.

### The Complete Coach Middleware Stack — Ratified

**Eight middlewares**, all wired via `create_agent(middleware=[...])`. **The table order is the declaration order, which is the execution order for hooks of the same kind.**

| # | Middleware | Source | Purpose | Hook |
|---|---|---|---|---|
| 1 | `BeforeModelStateInjection` | **Custom** (§38) | Prepend structured project state at the top of the prompt | `before_agent` |
| 2 | `DMAICSkillsMiddleware` | **Custom** (§83, §84) | Progressive disclosure of phase coaching instructions | `before_agent` + a registered tool |
| 3 | `SummarizationMiddleware` | LangChain core (§36) | Context compression for long coaching sessions | `before_model` |
| 4 | `ModelRetryMiddleware` | LangChain core (§80) | Invisible retry on transient **model API** failures | `wrap_model_call` |
| 5 | `ToolRetryMiddleware` | LangChain core (§29) | Invisible retry on **tool execution** failures | `wrap_tool_call` |
| 6 | `ContradictionDetectionMiddleware` | **Custom** (§38) | Deterministic §38 check — captured field vs gate-approved value | `after_agent` |
| 7 | `CoherenceMiddleware` | **Custom** (§68, §69) | L2a coherence — real, conclusive, on-topic, not parroting | `after_agent` |
| 8 | `DMAICGraderMiddleware` | **Custom** (§42, §48) | Coaching **process** quality against `COACHING_QUALITY_RUBRIC` | `after_agent` |

Five custom, three core. The custom ones migrate to deepagents equivalents if and when it reaches 1.0 — a deliberate decision to carry a known, bounded amount of our own code rather than an unknown, unbounded amount of someone else's pre-1.0 churn.

**How the stack grew from four to eight, and why each addition is not redundant:**

| Added | Why it is not covered by something already in the stack |
|---|---|
| `ModelRetryMiddleware` (§80) | Nothing else retried a failed model call. Distinct from the §67 fallback chain, which *swaps the model* on service-level failure rather than retrying the same call |
| `ToolRetryMiddleware` | A failed Azure Search call is not a failed model call. `ModelRetryMiddleware` never sees it — different hook, different failure mode. `on_failure="continue"` returns a failure result the coach can react to instead of killing the graph |
| `ContradictionDetectionMiddleware` | §38's mid-phase contradiction check needed a home. It is deterministic dict comparison, no LLM call, and lives here rather than inside the executor node so it is a named, LangSmith-visible step and the executor stays responsible only for coaching |
| `CoherenceMiddleware` | L2a coherence was previously a criterion inside `COACHING_QUALITY_RUBRIC`. That conflated two different questions — "is this a real statement at all?" versus "is this good coaching?" — and paid for a full rubric grading call on responses already known to be incoherent |

**Ordering rules that bind.** `BeforeModelStateInjection` MUST be first: project
facts have to reach the top of the prompt before skills loading and
summarisation shape it. Its hook is **`before_agent`**, not `before_model` —
state injection belongs at agent-loop start, not before every individual model
call within a turn. Middlewares 6, 7 and 8 all fire `after_agent` and therefore
run in declaration order: contradiction check, then coherence, then grader.
**If `CoherenceMiddleware` fails and its retries exhaust, `DMAICGraderMiddleware`
is skipped for that turn** — deliberately, since grading an incoherent response
spends a model call to produce a meaningless score.

Positions 4 and 5 sit on `wrap_*` hooks and do not compete for a slot with
anything else; they are grouped together for readability, not for ordering.

**`DMAICGraderMiddleware` grades process quality only** — the seven-step
computation pattern, the show-first principle, citations, no external URLs.
Coherence is not one of its criteria; middleware 7 owns that.

**`DMAICGraderMiddleware` here grades coaching, not gate documents** (§42 Finding 18). Its rubric is `COACHING_QUALITY_RUBRIC`, shared across all five phases. The phase rubrics belong to Layer 4 of the validation stack, which is a node, not middleware.

### What Changed

§42's grader discussion identified system prompt bloat but did not resolve it. deepagents' `SkillsMiddleware` is the reference solution; the mechanism below is what `DMAICSkillsMiddleware` reimplements.

### How It Works — The deepagents Reference

```python
# REFERENCE ONLY — requires create_deep_agent and the deepagents dependency.
# The ratified implementation is a custom middleware on create_agent (above).
from deepagents import create_deep_agent
from deepagents.backends.filesystem import FilesystemBackend

agent = create_deep_agent(
    model="operational-premium",
    backend=FilesystemBackend(root_dir="./agent-improve/skills/"),
    skills=[
        "./agent-improve/skills/dmaic-define-phase/",
        "./agent-improve/skills/dmaic-measure-phase/",
        "./agent-improve/skills/dmaic-analyse-phase/",
        "./agent-improve/skills/dmaic-improve-phase/",
        "./agent-improve/skills/dmaic-control-phase/",
    ],
    tools=[...],
)
```

At startup, `SkillsMiddleware`:
1. Reads all SKILL.md frontmatter (Level 1 disclosure — descriptions only)
2. Adds a compact summary to the system prompt
3. Registers `load_skill(name)` as a tool the agent can call
4. When the agent calls `load_skill("dmaic-analyse-phase")`, the full instructions load into context (Level 2)

`DMAICSkillsMiddleware` does exactly these four things against `create_agent`'s hooks.

### Cross-Reference Impact

| Existing Section | Update Needed |
|---|---|
| Section 42 (RubricMiddleware) | Combine with SkillsMiddleware — RubricMiddleware evaluates gate quality, SkillsMiddleware provides phase context |
| Section 44 (architectural refactor) | Skills become the mechanism for phase-specific coaching context, not the graph structure |
| Section 83 (agentskills.io spec) | Implementation companion — this is HOW skills get loaded |

### Gap Register Note
No new gap number — SkillsMiddleware is the concrete implementation of Section 83's progressive disclosure pattern. Use `FilesystemBackend` during v2.1 refactor for git-versioned skills.

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

**improve_evidence_index (7 fields — was 5)**
| Field | Type | |
|---|---|---|
| id | Edm.String | |
| content | Edm.String | |
| content_vector | Collection(Edm.Single) — vector, 3072d | |
| metadata | Edm.String | |
| case_id | Edm.String | |
| **phase** | **Edm.String** | **NEW** — auto-set from `state["current_phase"]` at upload |
| **uploaded_at** | **Edm.String** | **NEW** — ISO 8601, server-side, never Belt-entered |

Case-specific uploaded documents. Per §39, this is the **only** channel through which real-world data enters AgentLean — there are no live system integrations. That elevates its architectural importance well beyond "uploaded files."

**Two fields were added to this index (ratified 2026-08-20), and both are set
by the system, never by the Belt.**

`uploaded_at` closes a gap this document previously recorded and worked around:
`rag_lookup_evidence` wanted `order_by=["uploaded_at desc"]`, the field did not
exist as a top-level sortable field, and the upload timestamp was buried inside
the non-sortable `metadata` JSON blob where `$orderby` cannot reach it. The
workaround on the table was to drop recency ordering entirely. As a top-level
`Edm.String` holding ISO 8601, it sorts lexicographically in the correct
chronological order, and the ordering clause becomes available.

`phase` closes a problem that had not been articulated at all: **two similar
documents uploaded at different phases were indistinguishable at retrieval
time.** A Belt uploads defect data in Measure and revised defect data in
Control; both match "defect data" and nothing in the index says which phase
each belongs to. Since `improve_evidence_index` is the sole channel for
external data, that ambiguity lands directly on the coaching answer.

`rag_lookup_evidence` gains an **optional** `phase` filter — **default
unfiltered**, so cross-phase evidence retrieval still works when the coach
genuinely needs it (a Control-phase Belt comparing against the Measure
baseline is the normal case, not the exception). Filtering by default would
have quietly broken exactly the comparison the field exists to enable.

Both fields are server-set: `phase` from `state["current_phase"]` at upload
time and `uploaded_at` from the server clock. Belt-entered values for either
would make them unreliable as filter and sort keys.

**Both require a reindex.** Batch this with the already-planned
`improve_case_index` `embedding` → `content_vector` standardisation so the
corpus is rebuilt once rather than twice.

**Consequential: `PhaseState.uploads` gains a specified shape.** The field
existed with its internal structure unstated; with `phase` and `uploaded_at`
now on the index, the state record mirrors it:

```python
uploads: list[dict]
# {"evidence_index_id": str,   # the row in improve_evidence_index
#  "filename":          str,
#  "phase":             str,   # matches the index field
#  "uploaded_at":       str,   # ISO 8601, matches the index field
#  "summary":           str}
```

`evidence_index_id` is what makes the gate document's evidence trail
traversable: a reviewer reading the approved document can follow it back to the
indexed chunk the coaching was grounded in.

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
| **phase_summary_analyse** | Edm.String — **RENAMED** from `phase_summary_analyse_phase` |
| phase_summary_improve | Edm.String |
| phase_summary_control | Edm.String |
| content_text | Edm.String |
| embedding | Collection(Edm.Single) — vector — **renaming to `content_vector`, see below** |

Live case data with per-phase summaries and vector embedding. This IS long-term vector memory for cross-case retrieval.

> **Ratified: `embedding` → `content_vector`. Not yet applied in Azure.**
> This index is the only one of the three whose vector field is not called
> `content_vector`, and the asymmetry has no justification beyond history —
> each tool knowing its own index's field name locally makes the asymmetry
> *safe*, not *good*. Standardising removes a permanent trap for anyone
> writing a fourth retrieval tool.
>
> **Until the re-index runs, `embedding` is still the live field name**, and
> code written against this index must use `embedding`. The change is a
> delete + recreate (the index holds 0 documents, so nothing is lost and no
> data migration is needed), and it should be batched with the
> `improve_evidence_index` `phase` / `uploaded_at` additions above so the
> corpus is rebuilt once. `rag_lookup_case_history` in `knowledge/tools.py`
> and ARCHITECTURE.md §7.3 change in the same commit as the Azure change —
> not before it.

> **Pre-commit priority action — field rename.** `phase_summary_analyse_phase` is renamed to `phase_summary_analyse` for consistency with `_define`, `_measure`, `_improve`, `_control`. This is a **breaking schema change**: update the `improve_case_index` schema in Azure AI Search, reindex existing case content (or rename the field on existing documents), and sweep the codebase for reads of the old name.
>
> The alternative — a `PHASE_SUMMARY_FIELD_MAP` mapping constant — was considered and rejected. Fixing the name at the source means no permanent workaround exists in the codebase, and future readers are never surprised by the inconsistency. Once the rename lands, the naive `phase_summary_{phase.lower()}` pattern is correct for all five phases; before it lands, that pattern fails on Analyse specifically.
>
> Deferred consideration: a schema audit across all three indexes for other similar naming inconsistencies.

---

### Revised Gap Assessment

With `improve_case_index` in place the picture is significantly better than assumed:

| Memory Type | What We Have | What Is Still Missing |
|---|---|---|
| Short-term | `messages[]` in state — current session | Summarisation when context window fills |
| Long-term methodology | `improve_knowledge_index` — eBook | Nothing — this is complete |
| Long-term case data | `improve_case_index` — per-phase summaries + vector | Nothing — this exists |
| Context management | No mechanism | Summarisation strategy for long sessions |

**Gap 20 — the diagnosis here is confirmed and acted on.** `improve_case_index` with its `embedding` field and five `phase_summary_*` fields *is* the long-term memory mechanism. The remaining question this section raised — whether it is queried during active coaching — is answered by §37's ratification of the `rag_lookup_case_history` tool. This section is the pedagogical foundation for that tool's existence.

The `phase_summary_*` fields are pre-computed per-phase summaries, which means the case-history tool can retrieve compact per-phase context rather than only raw content chunks. Its docstring says so explicitly, so the coach knows both modes are available:

```python
"""Semantic search across past Agent Improve cases. Retrieves either
raw content chunks (via the `embedding` field) or pre-computed per-phase
summaries (via phase_summary_define, phase_summary_measure, … on
improve_case_index)."""
```

**Gap 19 was real and is now closed by `SummarizationMiddleware`** — see below.

---

### Vector Field Name Asymmetry — Closes as a No-Op

The three indexes do not agree on their vector field name:
- `improve_knowledge_index` → `content_vector`
- `improve_evidence_index` → `content_vector`
- `improve_case_index` → `embedding`

This section originally flagged that as a hazard requiring runtime normalisation. **Under the ratified three-tool design it evaporates.** The concern presumed a *shared* retriever mapping field names across indexes. There is no shared retriever: each of the three `rag_lookup_*` tools is bound to exactly one index and knows that index's vector field name locally (§32, §33). No shared code hides the asymmetry, so nothing can fail silently on it.

Each tool's docstring names the vector field it uses. That is the whole mitigation.

---

### .env Hygiene — Operational, Not Architectural

Recorded as an operational note. No architectural change:
- The app loads `agent-improve/.env`; a root `.env` can silently shadow values depending on `load_dotenv()` search order
- Correct variable name is `AZURE_SEARCH_API_KEY`, **not** `AZURE_SEARCH_KEY`
- Audit and remove the root `.env` if it is redundant

This is a Claude Code housekeeping fix, not a governance-doc update. §1's fail-fast environment validation is the structural defence against the class of problem.

---

### Short-Term Memory — What It Actually Means at Runtime

**Where everything is stored — the v1 layout this section diagnoses:**
```
Azure Blob Storage                    ← v1. Retired names shown as they were.
└── case_id/state.json                  `captured_fields` → `artifacts` (§17);
    ├── messages[]           ← EVERY message ever sent, grows forever
    ├── captured_fields{}    ← structured extracted fields
    ├── current_phase        ← which phase we are in
    └── completeness_score   ← per phase; NOT carried into v2 — derived (§17, §77)

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

**Who triggers summarisation and when:** nothing did. Gap 19 was real. Below is what closes it.

### Short-Term Memory — Ratified: `SummarizationMiddleware` + Two Typed State Fields

This section originally proposed a custom `conversation_context` structured-JSON implementation with a hand-written `compress_messages` function. **That is retired** — it reinvents what LangChain now provides natively. But its underlying insight is correct and is preserved, applied in the right place.

**The mechanism — LangChain 1.0 built-in middleware.**

Web-verified: `SummarizationMiddleware` lives in the main `langchain` package and attaches via `middleware=[...]` on `create_agent`. Configuration parameters are `trigger`, `keep`, and `model`. Available since v1.0 GA (October 2025); v1.1 adds context-aware profiles per model.

From `docs.langchain.com/oss/python/langchain/middleware/built-in`: *"Automatically summarize conversation history when approaching token limits, preserving recent messages while compressing older context."*

Ratified configuration for Agent Improve:

```python
from langchain.agents.middleware import SummarizationMiddleware

SummarizationMiddleware(
    model="azure/operational-model",       # gpt-4o-mini for cost
    trigger=("tokens", 100_000),           # ~78% of gpt-4o's 128k window
    keep=("messages", 20),                 # preserve the last 20 turns raw
)
```

**The insight that survives — some project state belongs in typed fields, not in `messages[]`.**

The original section was right that prose summary is the wrong carrier for facts:

| | Prose summary | Typed state field |
|---|---|---|
| LLM reads facts | Parses natural language | Reads structured values directly |
| Consistency | Varies per read | Same every time |
| Hallucination risk | LLM interprets a summary | LLM reads exact values |
| Survives compression | No — it *is* the compression | Yes — never lived in `messages[]` |

The correct application is not a custom compression function. It is that **the facts were never in `messages[]` to begin with** — so compressing the conversation cannot lose them.

This section originally concluded differently. It proposed **two new typed fields on `SupervisorState`**, `key_decisions` and `open_items`, populated at gate boundaries, on the grounds that anything which must survive compression has to live in typed state. **Both were later removed as redundant (§17).** The premise was right and the conclusion did not follow from it:

| What must survive compression | Where it already lives | Outside `messages[]`? |
|---|---|---|
| A decision the Belt commits | `CoachingResponse.fields_captured` → `PhaseState.artifacts` → the store at gate approval | Yes, in all three |
| A captured field value | Same path | Yes |
| Which fields are still missing | Not stored at all — `check_gate_status()` computes it | N/A — derived |
| Whether a gate is ready | `DMAICGateValidator`, layer 2b of the validation stack (§68) | N/A — derived |

`key_decisions` would have held a second copy of facts that were durable already. `open_items` would have held a stored answer to a question the validation stack answers on demand — and a stored answer can contradict `DMAICGateValidator`, which is strictly worse than having no field at all.

**What §36 actually establishes, then, is a constraint rather than a schema:** durable facts must not live *only* in `messages[]`. `record_field`, `artifacts`, and the store already satisfy it. The `before_model` middleware (§38) prepends that structured project state early in the prompt each turn, deriving the missing-field list at injection time rather than reading a stored one.

**The principle connection:** prose summary is planning buried in a prompt. Typed state is explicit, inspectable, and durable. Same principle as planner/executor — make the reasoning explicit and structured rather than hidden in natural language. What changed is only *who implements the compression*: LangChain, not us.

**Web-verification citations:**
- `docs.langchain.com/oss/python/langchain/middleware/built-in` — `SummarizationMiddleware` behaviour
- `reference.langchain.com/python/langchain/agents/middleware/summarization/SummarizationMiddleware` — class reference
- `www.langchain.com/blog/langchain-langgraph-1dot0` — v1.0 GA release notes confirming the middleware pattern

*Cross-references: §17 (the two new `SupervisorState` fields), §33 (RRF in the retrieval tools), §37 (working memory in the memory taxonomy), §38 (`before_model` injection), §53 (built-in middleware confirmation), §84 (the complete four-middleware coach stack), Terminology Reference (middleware is neither a node nor a tool).*

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

> **How to read this section.** §38 was originally written as the case for a monolithic **Context Orchestration Layer** (Gap 22). Under LangChain 1.0 middleware, the ratified ReAct coach, and the policy advisory pattern, the concerns it identifies are real but are addressed by **three small additions rather than a new component**. This section documents that decomposition. The pedagogy — the briefing analogy, injection timing, the four trade-offs — is kept, because it explains *why* the three additions matter.

**The decomposition:**

| §38 concern | Treatment | Status |
|---|---|---|
| Memory selection | Handled by the ReAct loop + tool descriptions (ARCHITECTURE.md §3.2) | No action |
| Budget management | Handled by `SummarizationMiddleware` (§36) | No action |
| Memory prioritisation | System prompt engineering — a memory-hierarchy paragraph in the coach's system prompt | **In scope — Gap 22a** |
| Conflict resolution, gate-time | Policy advisory (§2) | No action |
| Conflict resolution, mid-phase | Extend the policy advisory to detect `captured_field` contradictions and fire a HITL interrupt | **In scope — Gap 22c** |
| Injection timing | Custom `before_model` middleware prepending structured project state early | **In scope — Gap 22b** |
| Self-correcting queries (reactive) | Multi-query + RRF is the proactive equivalent (§32, §33) | No action; §87 item 8 if ever needed |

Compound Gap 22 retires. Three small additions, each with a clear implementation surface. No monolithic new component.

### AgentLean Status Against Each Component

| Component | AgentLean | Status |
|---|---|---|
| Short-Term Memory | `messages[]` + `SummarizationMiddleware` | ✅ closed (§36) |
| Long-Term Memory | `improve_case_index` via `rag_lookup_case_history` | ✅ in scope (§32, §33) |
| External Knowledge | `improve_knowledge_index` via `rag_lookup_methodology` | ✅ in scope |
| Context Orchestration Layer | **Not built as a component** | Decomposed into 22a / 22b / 22c |

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
artifacts            → buried inside old messages
                            ↓
                       everything → LLM (no selection, no ordering, no budget)
```

---

### Agent Improve After Gap 22 Is Fixed

```
messages[]           → orchestrator: last 10 only
RAG chunks           → orchestrator: only score > 0.8, max 3 chunks
artifacts            → orchestrator: inject as structured JSON first
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

That briefing still gets prepared before every coaching turn — but it is the **emergent behaviour of middleware, the ReAct loop, and system prompt discipline working together**, not the output of a distinct component. `SummarizationMiddleware` keeps the history short, `before_model` puts the structured project state at the top, the coach's system prompt says which source outranks which, and the ReAct loop decides whether retrieval is needed at all. Four mechanisms, one briefing, no orchestrator class.

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

**Gap 22a — this is a system prompt paragraph, not a priority table in code.** The mechanism is prompt-level priority, not per-chunk metadata scoring. The coach's system prompt carries an explicit hierarchy:

```
MEMORY HIERARCHY — when sources disagree, weight them in this order:
  1. LSS Black Belt methodology (rag_lookup_methodology) — authoritative
  2. This project's confirmed captured fields — the Belt's own approved facts
  3. Past case history (rag_lookup_case_history) — patterns, not prescriptions
  4. Recent conversation — context, not evidence
Never present case history as methodology. Never let a recent remark
override a gate-approved value without flagging it.
```

The equivalent rule expressed as data, for reference:

```python
MEMORY_PRIORITY = {
    "external_knowledge": 1,   # highest — eBook is authoritative methodology
    "artifacts":          2,   # second — Belt's own confirmed facts
    "long_term_case":     3,   # third — past case patterns
    "recent_messages":    4,   # last — recent conversational context
}
```

*This also settles §40's "authority weighting between sources" idea: it needs no new work, because this paragraph already handles it. §40's framing of authority as a per-chunk metadata signal is misleading — the real mechanism is prompt-level priority.*

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
    # most recent Belt statement beats old artifacts
    "recent_message_vs_captured_field": "recent_message_wins",
    
    # artifacts beats long-term case memory
    "captured_field_vs_case_memory": "captured_field_wins",
    
    # eBook methodology beats case memory
    "external_knowledge_vs_case_memory": "external_knowledge_wins",
    
    # when uncertain — do not guess
    "unresolvable": "trigger_hitl_interrupt"
}
```

The last rule is the one that matters, and the ratified design goes further than "when uncertain."

---

### Mid-Phase `captured_field` Contradiction Handling — Gap 22c

**Ratified: auto-flag every contradiction. No tolerance threshold.**

In production DMAIC, numbers — baseline mean, sigma level, target metric — are taken very seriously. Silent drift across weeks is precisely the failure mode a coaching system exists to prevent. A HITL interrupt forces the human to take responsibility for the change. Threshold-based softening would drift in the wrong direction: *"the delta was small enough"* is not an acceptable justification when downstream analysis depends on the value.

This extends §2's principle rather than contradicting it: the policy advisory offers a second opinion *before* the approval decision, and approval is what commits state. **Any change to a previously gate-approved value is treated as a mini-gate, not a silent overwrite.**

**Mechanics:**

- Fires as policy-advisory logic inside `gate_apply`, and mid-phase before each coach response is returned to the Belt — not only at gate boundaries
- Compares the Belt's most recent statements (extracted this turn) against the `artifacts` already committed in prior gate documents
- If any numeric or categorical field value differs, the coach's response is **suppressed** and a HITL interrupt payload is emitted
- Payload contains: field name, previously approved value, its approval timestamp and gate, the proposed new value, and two Belt-facing options
- It is a structured diff over `artifacts` — **no LLM call**, negligible latency

**Belt's two options:**

| Option | Consequence |
|---|---|
| *"Update the approved value"* | The affected phase's gate document becomes provisional; downstream phases need re-review |
| *"Keep the approved value"* | The Belt clarifies they misspoke; no state change |

**The re-approval cascade.** If the Belt confirms the new value, the affected phase *and every downstream phase that depends on it* return to a provisional state and need re-review. This is deliberately heavier than a soft override. Silent invalidation of downstream analysis is not acceptable in a production quality system — a root cause validated against a baseline of 4.2 is not automatically valid against 3.8.

The cascade has a hard dependency on §49: when it fires, the affected phase's **compensating action must run** to clean up stale values already written to Azure Blob and `improve_case_index`. Saga and the re-approval cascade are interdependent, not independent features.

---

### The Three Additions That Replace Gap 22

```
Gap 22a — Memory prioritisation paragraph in the coach's system prompt
Gap 22b — before_model middleware for early structured state injection
Gap 22c — Policy advisory extension for mid-phase captured_field contradictions
```

All three are in refactor scope. Each has a clear, small implementation surface. Together they cover what the monolithic Context Orchestration Layer was proposed to do, without introducing a component that would itself need governing.

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
[artifacts JSON]              ← LLM reads project facts first
[RAG methodology chunks]      ← LLM reads methodology second
[Recent messages]
[Belt's current message]      ← LLM evaluates Belt's message
                                 through the lens of established facts

Late injection (conversation first):
[System prompt]
[Recent messages]
[Belt's current message]      ← LLM reads Belt's message first
[artifacts JSON]              ← project facts arrive after LLM
[RAG chunks]                     has already started reasoning
                                 → response may drift toward Belt's suggestion
                                    rather than project-grounded answer
```

**Injection timing rule for Agent Improve:**

| Inject Early | Inject Late or Drop |
|---|---|
| artifacts JSON | Old messages from week 1 |
| Current phase requirements | Low-scoring RAG chunks |
| Missing fields list | Tangential case history |
| High-scoring RAG chunks | Superseded values |
| System prompt | Conversational filler |

**Gap 22b — the mechanism is `before_model` middleware.** LangChain 1.0's `AgentMiddleware` exposes a `before_model` hook (§80) that runs immediately before each model call. A small custom middleware prepends the structured project state — captured fields, current phase requirements, and the missing fields computed by `check_gate_status()` — at the top of the prompt, ahead of the conversation. Every one of those is read or derived at injection time, so the prompt cannot disagree with the gate (§17). That is the whole of the injection-timing control, and it is one hook rather than a component.

Injecting everything in the order it happened to land in `messages[]`, which is what the pre-refactor code does, is what this replaces.

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

**Status: subsumed, not built.** The reactive form is redundant given the proactive one. Multi-query + RRF (§32, §33) generates 3–5 variants up front and fuses them, which covers the same failure mode without a confidence-threshold heuristic and without a second round-trip on the turns where it fires. Running variants always is also more predictable in latency than sometimes running one query and sometimes three.

Retained here as historical context. If retrieval evaluation ever shows that multi-query variants systematically miss even after RRF fusion, the reactive form becomes worth adding — recorded as §87 item 8.

**TAO loop connection (worth keeping):**
Self-correcting queries *is* the TAO loop applied to retrieval — Thought (need methodology) → Action (query) → Observe (low confidence) → Thought (restructure) → Action (reissue). The same pattern as ReAct, operating at the retrieval level rather than the tool-selection level. Multi-hop (§34, §71) is the form of that loop we do build: the coach's ReAct loop chains retrievals, capped at 5 hops.

### Gap Register

**Gap 22 is retired as a compound gap.** It is replaced by three entries, all in refactor scope:

| Gap | Description |
|---|---|
| 22a | Memory-prioritisation paragraph in the coach's system prompt |
| 22b | `before_model` middleware for early structured state injection |
| 22c | Policy advisory extension for mid-phase `captured_field` contradictions, with re-approval cascade |

*Cross-references: §2 (the HITL pattern 22c extends), §17 (`SupervisorState` schema), §32/§33 (multi-query + RRF as the proactive equivalent of self-correcting queries), §36 (`SummarizationMiddleware` for budget management), §37 (memory taxonomy), §40 (why authority weighting needs no new work), §49 (compensating actions the cascade depends on), §80 (the six middleware hooks), §84 (the complete middleware stack), §87 item 8.*

---

# PART 3 — RETRIEVAL ARCHITECTURE

*How knowledge is found: query expansion, fusion, multi-hop depth, and the metadata and pipeline design around them.*

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

### Applies to Every Phase, Not Just Analyse

Analyse is the most obvious case — concepts appear under multiple terminologies in the eBook:

```
"root cause analysis" also appears as:
  "cause and effect analysis"
  "fishbone diagram methodology"
  "5 Why technique"
  "Ishikawa diagram"
  "potential cause identification"
```

But every phase has vocabulary fan-out in the LSS Black Belt eBook:

| Phase | Same concept, different wording |
|---|---|
| Define | problem statement / voice of customer / opportunity statement |
| Measure | baseline metric / current state performance / as-is measurement |
| Analyse | root cause / fishbone / Ishikawa / 5 Why |
| Improve | improvement hypothesis / counter-measure / solution design |
| Control | control plan / sustainability / process governance |

The `phase` argument shapes the variant-generation prompt, so one tool serves all five phases uniformly.

### Where This Belongs in the Architecture

Multi-query is implemented **inside** the `rag_lookup_methodology` tool — one of the leaf tools bound to each phase executor (§23, Terminology Reference). It is **not** a separate node in the subgraph and **not** a wrapper class around the retriever. From the executor's perspective, `rag_lookup_methodology(query, phase, top_k)` returns documents; the multi-query behaviour is encapsulated inside the tool.

The same applies to the other two retrieval tools. All three are:

| Tool | Index | Filter | Vector field |
|---|---|---|---|
| `rag_lookup_methodology(query, phase, top_k)` | `improve_knowledge_index` | `phase_relevance` (§37) | `content_vector` |
| `rag_lookup_evidence(query, case_id, top_k, phase=None)` | `improve_evidence_index` | `case_id`; optional `phase` (§36) | `content_vector` |
| `rag_lookup_case_history(query, top_k, exclude_current_case=True)` | `improve_case_index` | `status eq 'completed'` (§40) | `embedding` → `content_vector` *(§36 — pending re-index)* |

Each tool is bound to exactly one index and knows that index's vector field name locally. There is no shared retriever hiding the `content_vector` / `embedding` asymmetry, so no runtime normalisation is needed (§36).

*The asymmetry is safe by construction, and is still being removed — see §36. "Safe" was the argument for not treating it as urgent, never an argument for keeping it.*

### Reference Implementation

**The canonical implementation lives in §33**, because RRF is included by default and the two cannot be shown separately without the code drifting. §33's `rag_lookup` is the version to build against; the §37 variant adds the `phase_relevance` filter clause for the methodology tool specifically.

Variant generation uses LangChain 1.x native structured output (§82). No manual JSON parsing, no `OutputFixingParser` (§29).

### What This Section Used to Recommend, and Why That Is Wrong Now

The original version recommended `MultiQueryRetriever.from_llm(...)` from `langchain.retrievers.multi_query`:

```python
# DEPRECATED — do not use
from langchain.retrievers.multi_query import MultiQueryRetriever

retriever = MultiQueryRetriever.from_llm(
    retriever=azure_search.as_retriever(),
    llm=get_llm(),
)
```

In LangChain 1.x this is invalid on two counts:

1. **The import moved.** LangChain 1.0 (October 2025) split the namespace — `MultiQueryRetriever` and everything else from `langchain.retrievers` moved to `langchain-classic`. The old import raises `ImportError`.
2. **The class is deprecated even in `langchain-classic`.**

Rather than depend on a deprecated class, implement the pattern inside the tool. The current LangChain 1.x idiom is to build patterns from `create_agent`, tool binding, structured output, and middleware — not from legacy wrapper classes.

Verification: `docs.langchain.com/oss/python/migrate/langchain-v1`; `reference.langchain.com/python/langchain-classic/retrievers/multi_query`. Web-verified July 2026.

### Interaction With Related Retrieval Patterns

- **§33 RAG Fusion** — reciprocal rank fusion over the merged multi-query results. Not optional: ratified as included by default.
- **§34 / §71 Multi-Hop** — sequential retrieval where each hop informs the next. Different concept, complementary. **Multi-query broadens; multi-hop deepens.** Composable — multi-query can run at each hop.
- **§35 Query Voting and Weighted Fusion** — the comparative background on *why* RRF was chosen over the alternatives.
- **§37** — the `phase_relevance` filter added to this tool.
- **§40** — the metadata filters and ordering added to the evidence and case-history tools.

### Gap Register
**Gap 15** — single-query formulation only, against an already-good hybrid retriever. A self-contained tool-level improvement, implemented inside the `rag_lookup_*` tools. **Included in refactor scope.** The earlier "defer to post-completion refactor" rationale is inverted now that the refactor is the active work and the change carries no architectural risk.

**Open item for implementation:** confirm how `azure_search_retriever` is exposed in the current codebase (module-level object versus factory) and adjust the reference implementation accordingly.

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

### Agent Improve Gap Assessment — Refactor Target State

| Step | RAG Fusion | Agent Improve after the refactor |
|---|---|---|
| Query expansion | LLM generates variants | ✅ 3–5 variants, phase-shaped prompt |
| Retrieval | Parallel per variant | ✅ hybrid BM25 + vector, one call per variant |
| Document aggregation | All sets collected | ✅ `ranked_lists` collected |
| Reciprocal Rank Fusion | Cross-result re-ranking | ✅ RRF, k=60 |
| Final context | Best-ranked docs | ✅ top-k after fusion |

### Empirical Override — Why RRF Is Included by Default

An earlier assessment deferred RRF on the grounds that "Azure AI Search already does sophisticated hybrid ranking internally," making RRF a diminishing-returns improvement. **That assessment is overridden by production evidence.**

Agent Resolve production experience shows Azure AI Search's ranking is unreliable for this corpus and use case: the retriever was not ranking properly, and with a single search query it was not even reliably returning the right matches. Agent Improve uses the same underlying technology — Azure AI Search hybrid over `improve_knowledge_index` — so the theoretical argument does not survive contact with the LSS Black Belt eBook corpus.

**Why RRF specifically helps this failure mode.** RRF operationalises *cross-variant consistency*. When several query variants all return the same document at moderate ranks, that document is more likely genuinely relevant than one appearing once at the top of a single variant. Native Azure AI Search ranking is single-query — it cannot perform this consistency check, because it does not know the variants exist. RRF is the layer that turns variant-level ranking signal into a corpus-level relevance signal.

RRF is about fifteen lines. It needs no LangChain class and no third-party dependency, and the algorithm is stable across framework versions.

### Canonical Reference Implementation

*This is the authoritative implementation for all three `rag_lookup_*` tools. §32's multi-query-only sketch is superseded by this version — one implementation, not two that can drift.*

```python
from langchain_core.tools import tool
from langchain_core.documents import Document
from pydantic import BaseModel


class QueryVariants(BaseModel):
    queries: list[str]


def reciprocal_rank_fusion(
    ranked_lists: list[list[Document]],
    k: int = 60,
) -> list[tuple[Document, float]]:
    """Standard RRF: score each doc as the sum of 1/(k+rank) across variant
    results. Documents ranked consistently across variants score higher than
    one-off hits."""
    scores: dict[str, float] = {}
    docs: dict[str, Document] = {}
    for ranked_list in ranked_lists:
        for rank, doc in enumerate(ranked_list, start=1):
            doc_id = doc.metadata["id"]
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            docs[doc_id] = doc
    return sorted(
        [(docs[doc_id], score) for doc_id, score in scores.items()],
        key=lambda pair: pair[1],
        reverse=True,
    )


@tool
def rag_lookup_methodology(query: str, phase: str, top_k: int = 10) -> list[Document]:
    """Multi-query RAG lookup with Reciprocal Rank Fusion against
    improve_knowledge_index (LSS Black Belt eBook). Filters by phase_relevance
    to scope results to the current DMAIC phase. Uses the content_vector field.
    Applies to all five DMAIC phases."""
    variants = llm.with_structured_output(QueryVariants).invoke(
        f"Generate 3-5 alternative phrasings for retrieving DMAIC {phase} "
        f"content on: {query}. Include synonyms, related terminology, and "
        f"phrasings a Black Belt would use in the LSS Black Belt eBook."
    )
    # Module-level cached vectorstore; the filter is a per-call argument.
    vs = get_knowledge_vectorstore()          # AzureSearch, search_type="hybrid"
    filters = (f"phase_relevance eq '{phase}' "
               f"or phase_relevance eq 'general'")
    ranked_lists = [
        vs.similarity_search(q, k=top_k, filters=filters)
        for q in variants.queries
    ]
    fused = reciprocal_rank_fusion(ranked_lists, k=60)
    return [doc for doc, _score in fused[:top_k]]
```

**The cross-phase filter value is `general`, not `all`.** The index was
inspected directly: 218 documents carry `phase_relevance = 'general'` and
**zero** carry `'all'`. The `OR` clause was therefore never satisfied, and
every methodology lookup silently returned a corpus narrowed to the current
phase — no error, no empty result, just quietly missing cross-phase content.
The earlier note here said "confirm the exact enumeration before
implementing"; that placeholder is now closed, and this is the confirmed
value. **`backend/knowledge/retriever.py` already had this right**
(`CROSS_PHASE_RELEVANCE = "general"`); only this document carried the bug.

**On `AzureSearch`, the filter is a per-call argument — and that is
correct.** An earlier revision of this section showed
`azure_search_retriever.invoke(q, search_kwargs={"filters": ...})` and was
then corrected to a per-call `AzureAISearchRetriever(filters=...)`
constructor. **Both were wrong, because neither is the class in use.**

`AzureAISearchRetriever` does take `filters` at construction, which is what
forces per-call instantiation when the filter is dynamic. But Agent Improve
uses `AzureSearch` (`langchain_community.vectorstores.azuresearch`), whose
`similarity_search(query, k=..., filters=...)` accepts the filter **at call
time**. That difference removes the whole problem: the vectorstore stays a
module-level `lru_cache`d singleton because the dynamic `phase` filter never
touches its construction.

**`AzureAISearchRetriever` is deliberately not adopted** — see §39 for the
mechanism decision. The `search_kwargs` collision recorded in `langchain`
issue #30482 is real, but it is an artifact of a class this codebase does
not use, and it should not be cited as a constraint on the code that exists.

**What *is* construction-time on `AzureSearch` is `fields=`**, and that one
genuinely binds: LangChain promotes a metadata key to a filterable top-level
field only when the key matches a name in `self.fields`, which defaults to
`[id, content, content_vector, metadata]` and never introspects the live
index. Declaring `fields=KNOWLEDGE_INDEX_FIELDS` is what keeps
`phase_relevance` filterable on write. Omit it and the value is silently
buried in the `metadata` JSON blob, unreachable by `$filter`, with no error
raised — which is how `phase_relevance` went unpopulated in the first place.

The same corrections apply to §37's implementation note, which carried
identical copies of the same bugs.

`rag_lookup_evidence` and `rag_lookup_case_history` follow the identical shape — same variant generation, same RRF — differing only in index, filter, and vector field. See §32's table and §40 for their metadata filters and ordering clauses. Metadata filters propagate through fusion cleanly: each variant query returns metadata-filtered results, and RRF combines them normally.

### Gap Register
**Gap 16 — RRF re-ranking. Included in refactor scope**, integrated with Gap 15 (multi-query) inside the `rag_lookup_*` tools. Empirical evidence from Agent Resolve retrieval quality overrode the earlier "diminishing returns" deferral.

*Cross-references: §32 (the parent tool that houses RRF), §35 (query voting and weighted fusion — why RRF won), §37 (`phase_relevance` filter), §40 (metadata filters on the other two tools), §71 (multi-hop composes with multi-query at each hop), §82 (structured output for variant generation), Terminology Reference (RRF lives inside a tool, not as a subgraph node or wrapper class).*

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

### Where Multi-Hop Lives — No New Infrastructure

Multi-hop is **not** a missing component. It is what the coach node already does when its ReAct tool-calling loop makes multiple `rag_lookup_methodology` or `rag_lookup_evidence` calls in a single Belt turn. The capability lives in the executor's tool-calling loop (ARCHITECTURE.md §3.2), not in a separate retrieval subsystem.

**It is also not dependent on multi-query.** The original "prerequisite: Gap 15" claim was wrong — multi-hop and multi-query are independent mechanisms. Better single-hop retrieval (multi-query + RRF) *reduces the need* for many hops, but neither requires the other.

### The Hop Cap — 5 Tool Calls per Belt Turn

Beyond five hops the LLM is usually lost or looping, and cutting it off is the correct behaviour.

**The cap is enforced with `RemainingSteps`, a LangGraph managed value read
inside the executor node — not with `recursion_limit`.**

```python
from langgraph.managed import RemainingSteps

def agent_node(state: PhaseState) -> dict:
    remaining = state.get("remaining_steps", 10)
    if remaining <= 2:
        # too close to the limit — synthesise from what we have
        return {"messages": [synthesise_partial(state)]}
    return run_agent_step(state)
```

**Why not `recursion_limit`.** An earlier revision of this section set
`recursion_limit = 2 * max_hops + 1 = 11` on the graph invocation and called
that the hop cap. In a flat graph the arithmetic holds. In our hierarchy —
supervisor → phase subgraph → executor — it fails in two opposite directions,
and which one you get depends on configuration:

| Failure mode | What happens | Evidence |
|---|---|---|
| Shared counter | Subgraphs draw on the parent's step budget. Supervisor and phase-routing steps consume from the same 11 before the executor's first tool call, so the executor gets **fewer** than 5 hops | LangGraph Discussion #1260 |
| Non-propagation | `recursion_limit` is not passed down to the subgraph at all, which reverts to the default of 25 — the cap is **absent** | deepagents Issue #1698 |

It is also a blunt instrument: it counts every node invocation
indiscriminately and terminates the graph with `GraphRecursionError` rather
than letting the coach close out gracefully.

`RemainingSteps` avoids all of this because it lives in graph state rather
than in config. It crosses the subgraph boundary intact, it counts only
executor steps, and — the part that matters to the Belt — it provides an
off-ramp: at `<= 2` the agent composes an answer from what it already has
instead of dying.

**`recursion_limit` stays, with a different job.** Set high on the supervisor
invocation as a backstop against genuine infinite loops:

```python
await graph.ainvoke(
    state,
    config={
        "recursion_limit": 50,        # infrastructure backstop, NOT the hop cap
        "configurable": {"thread_id": case_id},
    },
)
```

Two responsibilities, two mechanisms: `recursion_limit` catches bugs,
`RemainingSteps` enforces the Belt-facing hop budget.

**Error handling is still mandatory.** The coach node must catch
`GraphRecursionError` and return a partial answer rather than crash — now as a
belt-and-braces guard against bugs, since `RemainingSteps` should prevent the
cap from being reached in normal operation. A Belt mid-session should never
see a stack trace because the coach explored too broadly. Verified:
`docs.langchain.com/oss/python/langgraph/errors/GRAPH_RECURSION_LIMIT`.

### Cost Mitigations

Multi-hop multiplies LLM calls per turn, so five mitigations are ratified together:

| Mitigation | Effect |
|---|---|
| Cap the hops at 5 | Bounds worst-case cost per turn — via `RemainingSteps`, above |
| **Tier the model** — **DEFERRED, §87** | Intermediate hops on `operational-model` (gpt-4o-mini), final synthesis on `operational-premium` (gpt-4o). Substantial lever — gpt-4o-mini is roughly 15× cheaper — but **not implemented in v2.1**. See below. |
| Adaptive routing | Simple queries do not need multi-hop at all — the planner decides (§71) |
| Session-scoped caching | Repeat retrievals within a session hit the cache (§67 Level 3) |
| Better single-hop | Multi-query + RRF (§32, §33) reduces how many hops are needed in the first place |

**Model tiering is deferred to §87, and this is the trigger that promotes it.**
No standard `create_agent` mechanism exists for swapping models mid-loop — the
agent compiles with one model — so tiering requires a `RemainingSteps`-gated
swap inside a custom agent node. The other four mitigations give v2.1
sufficient cost control, and tiering before LangSmith shows *which* turns hit
the cap and at what cost is optimising without data. **Promotion trigger:
LangSmith shows repeated 5-hop cap hits on Analyse-phase turns.**

**Hitting the 5-hop cap in production is a signal**, not just a limit. It means either the coach's system prompt is encouraging too-broad exploration (prompt tuning), or the question genuinely warrants escalation to `operational-premium` for that turn (model tiering). Watch it in LangSmith — this is the same observation that promotes the deferred item above.

### Gap Register
**Gap 17 — CLOSED.** Multi-hop is available through the ReAct coach loop with a 5-hop cap. §71 adds the design layer: which phases, which query types, and the planned-versus-emergent distinction. Together, §34 and §71 close Gap 17 completely.

*In one sentence: multi-hop is what the coach node does when its ReAct loop makes several `rag_lookup_*` calls in one Belt turn, capped at 5 hops via `RemainingSteps`.*

*Cross-references: ARCHITECTURE.md §3.2 (coach as a ReAct agent); §32/§33 (better single-hop reduces the need for many hops); §71 (scoping, planner integration, and the formal Gap 17 closure).*

---

## 71. Multi-Hop Retrieval — Gap 17 Formally Closed

*Source: Edureka Course 4 Module 2, "Multi-Stage Knowledge Pipeline and Multi-Hop System Reasoning" demonstration, plus direct discussion on where multi-hop applies across Agent Improve's architecture.*

> **Status: Gap 17 CONFIRMED CLOSED.** §34 supplies the mechanism (the coach's ReAct loop, 5-hop cap via `RemainingSteps`, `recursion_limit` as a high backstop only, `GraphRecursionError` handling). This section supplies the design layer: which phases, which query types, and the distinction between planned and emergent multi-hop. Together they close Gap 17 completely.
>
> **Two approaches, phase-dependent:**
>
> - **Analyse — planned multi-hop.** The planner pre-decomposes the question into a typed `Plan` schema with exactly three hops *before any retrieval fires*. More structured, more predictable, fully inspectable in LangSmith — you can see each hop's question and its result. Correct for Analyse because root cause validation is inherently layered and inspectability matters in a quality system.
> - **All other phases — emergent multi-hop.** The coach naturally calls `rag_lookup_methodology` several times when it needs to, driven by its own reasoning. No structured hop plan. Correct where multi-hop is occasional (Measure for complex MSA questions, Improve for comparing approaches) — a structured planner is not justified for rare occurrences.
> - **Gate validation — no multi-hop, ever.** Retrieval is excluded from the four-layer stack (§68). The rubric already encodes the methodology standards; adding retrieval at gate time is redundant *and* adds latency at exactly the moment the Belt is waiting.

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

**Stage 2 — Executor (sequential, results written to `PhaseState`):**

```python
async def analyse_executor_node(state: PhaseState) -> dict:
    # Guard at node entry — the for-loop below runs entirely inside ONE node
    # invocation, so RemainingSteps does not decrement between hops (§34).
    if state.get("remaining_steps", 10) <= 2:
        return {"messages": [synthesise_partial(state)]}

    plan: Plan = planner.invoke(decomposition_prompt)
    local: dict[str, str] = {"entity": state.get("extracted_entity", "")}
    hop_results: list[str] = []

    for hop in sorted(plan.hops, key=lambda h: h.hop_number):
        result = rag_lookup_methodology(
            query=hop.hop_question.format(**local),   # templates filled from prior hops
            phase=state["current_phase"],
        )
        local[f"hop{hop.hop_number}_answer"] = result
        hop_results.append(result)

    synthesis = synthesis_llm.invoke(
        synthesis_prompt.format(**local, instruction=plan.synthesis_instruction)
    )
    return {
        "hop_results":      hop_results,              # §71-E — checkpointed, LangSmith-visible
        "synthesis_output": synthesis.model_dump(),   # §71-D — read by the coach call
    }
```

**Two corrections are in that block, and both were required before Step 3.1.**

**The `RemainingSteps` guard sits at node entry, not inside the loop.** For
emergent multi-hop the guard fires before each ReAct tool call; here the whole
three-hop sequence executes inside a single node invocation, and LangGraph
counts node transitions, not Python iterations — so `RemainingSteps` never
decrements between hops. The loop needs no internal guard because `Plan` bounds
it at exactly 3 hops, but without an entry guard the sequence can begin with
almost no budget left and consume it entirely before the agent can synthesise.

**Hop results go into `PhaseState`, not a local dict.** §71 claims planned
multi-hop is "fully inspectable in LangSmith." A local Python variable inside a
node is not: LangSmith traces node inputs and outputs and tool calls, not
interpreter locals. The claim only holds once `hop_results` is returned from
the node into state, where it is checkpointed and appears in the state diff.
`local` survives in the code above purely as the template-substitution scratch
space for the next hop's question.

**Stage 3 — Synthesis (a dedicated LLM call):**

Synthesis is its own call, and the coaching response is a further call after
it — **three LLM calls per Analyse multi-hop turn**, not two:

| # | Call | Temp | Produces | Belt-facing |
|---|---|---|---|---|
| 1 | Planner | 0.1 | `Plan` — 3 hops + `synthesis_instruction` | No |
| 2 | Synthesis | 0.1–0.2 | `SynthesisOutput` — evidence chain, key finding, confidence, caveats | **No** |
| 3 | Coach | 0.5–0.7 | The coaching response, reading `synthesis_output` from state | Yes |

```python
class SynthesisOutput(BaseModel):
    evidence_chain: str                          # assembled reasoning from hop results
    key_finding:    str                          # the conclusion the coach communicates
    confidence:     Literal["high", "medium", "low"]
    caveats:        list[str]                    # limitations in the hop chain
```

**Why synthesis is not folded into the coaching call.** Collapsing stages 2 and
3 would save a call, and it was considered and rejected. Synthesis is a quality
gate: assembling multi-hop evidence correctly is a different job from
translating it into coaching language, and each call is temperature-tuned for
its own job — deterministic evidence assembly at 0.1–0.2, natural coaching
voice at 0.5–0.7. One call cannot be both. Separating them also makes each
stage independently unit-testable, and puts the evidence chain in the trace
where a wrong coaching answer can be traced to either bad evidence or bad
translation. The three Azure AI Search calls (one per hop) are not LLM calls.

If LangSmith later shows multi-hop Analyse turns costing the Belt noticeable
wait time, that is the trigger for §34's deferred model tiering — planner and
synthesis on `operational-model`, coach on `operational-premium`.

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
Source: `artifacts` already on `PhaseState`.
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

When `retrieval_strategy == "single_hop"` the executor calls `rag_lookup_methodology` once. When `retrieval_strategy == "multi_hop"` it runs the three-hop chain. The Belt never sees the difference — they only see the coaching response, which is better grounded in the multi-hop case.

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

## 35. Query Voting and Weighted Fusion

*Source: Edureka Course 2 — Retrieval, Fusion Techniques, and Multi-Hop Reasoning*

> **Status: knowledge-only, comparative.** The implementation decision is settled in §33 — RRF, inside all three `rag_lookup_*` tools. This section exists so a reader understands *why* RRF was chosen over the alternatives, not to offer a choice. There is no design guidance and no gap here.

### What It Is
After running multiple queries against a retriever, the results need to be merged intelligently. Simple deduplication is not enough — documents need to be ranked by how relevant they are across all query results combined.

Three approaches appear in the literature. Two are described here for contrast; the third is what we build.

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

**Its weakness:** simple voting ignores *position* within each result set. A document ranked 50th in one variant scores exactly the same as one ranked 1st. For chunked retrieval, where position carries real information, that discards signal.

---

### Weighted Fusion
Assigns different weights to queries based on their quality, specificity, or source. More important queries influence the final ranking more than less important ones.

```python
# Example — original query weighted higher than generated alternatives
weights = {
    "original_query": 1.0,        # highest weight — direct user intent
    "generated_query_1": 0.7,     # alternative phrasing
    "generated_query_2": 0.7,     # alternative phrasing
    "domain_specific_query": 0.9  # high weight — domain knowledge
}

# Document score = sum of (rank_in_result_set * query_weight)
```

**Its weakness for Agent Improve specifically:** it presumes the Belt's original phrasing is more authoritative than the LLM-generated variants. For DMAIC coaching that is often exactly backwards. Belts phrase problems in plant vernacular; the generated variants translate that into methodology terminology — which is the language the LSS Black Belt eBook actually uses. Weighting the Belt's phrasing highest would systematically down-rank the better-matched queries.

Per-query weighting also introduces a hyperparameter that would need tuning against retrieval-quality metrics we do not have yet (§75).

---

### Reciprocal Rank Fusion (RRF) — What We Build
Rewards documents that consistently appear near the top of multiple result sets, while still respecting position.

```
RRF_score(doc) = sum over variants of  1 / (k + rank_in_that_variant)
# k = constant, typically 60, to dampen the influence of the very top ranks
```

A document ranked 1st in one variant and 3rd in another scores higher than a document ranked 1st in one variant and absent from the rest. This is the property neither simple voting (ignores position) nor weighted fusion (needs tuning) delivers.

**See §33 for the ratified implementation.** It lives inside `rag_lookup_methodology`, `rag_lookup_evidence`, and `rag_lookup_case_history`.

---

### Why Fusion Matters for DMAIC

*This is the genuinely valuable teaching in this section and it applies to whichever fusion method you pick.*

Different query phrasings surface different parts of the Black Belt eBook. A single root cause analysis question might be answered by three separate places in the corpus:

- The Analyse phase methodology chapter — surfaces on a query about "root cause"
- The fishbone diagram section — surfaces on a query about "cause and effect"
- The hypothesis testing chapter — surfaces on a query about "validating causes"

Without fusion, the coaching response is grounded in whichever chunk happened to rank highest for the one query that was used. With fusion, all three sections contribute — the coaching response is richer and more complete, and the Belt gets the methodology rather than a fragment of it.

---

### A Note on `EnsembleRetriever` and `MultiQueryRetriever`

Earlier versions of this section showed implementations built on `EnsembleRetriever` and `MultiQueryRetriever`. **Both classes moved to `langchain-classic` in the LangChain 1.0 namespace split** (web-verified, see §32) and are non-functional in the current codebase. They are omitted here rather than shown, because presenting them as guidance would mislead — and RRF is fifteen lines of plain Python that needs neither.

> **This supersedes a contrary claim in DECISIONS.md §E1**, which described
> `EnsembleRetriever` as "not deprecated, active in
> `langchain.retrievers.ensemble`, confirmed v0.3." That observation predates
> the 1.0 migration and was corrected on 2026-08-20 against the official
> LangChain v1 migration guide. E1's *architectural* conclusion was never in
> doubt and still stands on its own: `EnsembleRetriever` fuses results from
> **different retriever sources** (BM25 + vector), whereas our pattern is
> **same-index multi-query** — N phrasings against one index. It solves a
> different problem, so it would be the wrong class here even if it were
> importable. Two independent reasons, one conclusion: custom RRF.

---

### Gap Register
**No Gap 18.** The fusion gap for Agent Improve was closed by the RRF implementation in §33, formerly Gap 16. Gap 18 collapses into Gap 16; there is no separate entry.

### One Future Consideration (v2.2+)

Weighted fusion becomes plausibly useful in exactly one scenario: retrieval strategies drawing on *fundamentally different sources* — for example the BB eBook, case history, and an external best-practice database. There, weighting **per source** rather than per query variant could help balance authority levels. Not a refactor concern; recorded in §87 item 2 so it is not lost if a fourth retrieval source is ever added.

*Cross-references: §32 (multi-query, where fusion is applied), §33 (the canonical RRF implementation), §87 item 2, Terminology Reference (RRF lives inside tools, not as a node or wrapper class).*

---

## 37. Memory Patterns in Agentic Systems

*Source: Edureka Course 2 — Applied Agentic AI Pipelines with LangChain*

> **How to read this section: it is a taxonomic scaffold.** Each memory pattern below is mapped to where it lives in the ratified architecture. There is no standalone Gap Register at the end — one addition is in refactor scope, and five items are deferred to §87 with promotion triggers.

**The map, in one table:**

| Memory pattern | Where it lives | Status |
|---|---|---|
| Episodic | `improve_case_index` `phase_summary_*` fields, retrieved via `rag_lookup_case_history` | In refactor scope (§32, §33) |
| Semantic | `improve_knowledge_index` (LSS Black Belt eBook), retrieved via `rag_lookup_methodology` | In refactor scope |
| Working | `SummarizationMiddleware` + typed `PhaseState` fields (`artifacts`, `hop_results`, `synthesis_output`) | In refactor scope (§36) |
| **Procedural (static)** | System prompt, the five SKILL.md files via `DMAICSkillsMiddleware`, phase rubrics via `DMAICGraderMiddleware`, anti-hallucination guards | **In refactor scope (§83, §84, §42)** |
| **Procedural (dynamic)** | Per-Belt procedure store, updated from LangSmith trace analysis of gate outcomes | **Deferred, §87 item 5** |
| Retrieval control | One addition in scope (`phase_relevance` filter), three deferred | See below |

### Procedural Memory — the fifth type, and why it splits in two

Earlier revisions of this section listed four memory types and omitted
procedural memory entirely. LangMem (Tier 1) treats it as a first-class
category alongside semantic and episodic, and Agent Improve implements it —
it simply had no name here. Naming it exposes a distinction that matters
architecturally.

**Static procedural memory is the invariant DMAIC methodology.** The coaching
rules in the system prompt, the phase instructions in each SKILL.md, the
rubric criteria the grader applies, the anti-hallucination guards — these are
the same for every Belt, every project, every domain. **That is correct and
deliberate, not a limitation.** Methodology consistency is precisely the
guarantee a DMAIC coaching system exists to provide; a coach that quietly
varied gate criteria per Belt would be worthless as a quality system.

**Dynamic procedural memory is Belt-adaptive *delivery*.** It tracks how a
specific Belt learns best — how much scaffolding they need, whether worked
examples or challenge questions land better, which project-type emphasis
helps. It is stored per Belt, retrieved at session start, and updated from
gate outcomes.

The line between them is strict and load-bearing: **dynamic procedural memory
adapts how the methodology is delivered, never what the methodology
requires.** A Black Belt still needs `vital_few_xs`. The coach may open the
Analyse phase differently for a BB with ten projects behind them, but the
gate criteria do not move.

The mechanism is §87 item 5, which was previously framed as "LangSmith
trace-based coaching learning" — a general learning feature with no clear
shape. It is better understood as exactly this: LangSmith traces record which
coaching approaches preceded clean gate passages and which preceded repeated
loops, a background process outside the coaching loop extracts the pattern,
and the next session for that Belt loads the learned procedures alongside the
static SKILL.md rules — extending them, never overriding them.

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

Retrieved via `rag_lookup_case_history` — the yokoten tool ratified in §32/§33.

**Per-turn episodic entries — deferred (§87 item 3).** Only gate-level summaries are stored. Recording individual coaching decisions as retrievable memories would multiply case-index writes 30–50×, and gate-level granularity is sufficient for the coaching use case. Promotion trigger: coaching evaluation shows gate-level summaries lose actionable detail.

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
This was **Gap 19**, discussed at length in §36. It is closed by `SummarizationMiddleware` alone — the facts that must survive compression were never in `messages[]` to begin with.

**Ratified implementation:**
```
Recent messages (last 20)  → kept raw in messages[]        (keep=("messages", 20))
Older messages             → compressed by SummarizationMiddleware
                             at ~100k tokens               (trigger=("tokens", 100_000))
Captured fields            → CoachingResponse → PhaseState.artifacts → the store
                             at gate approval. Never in messages[], so
                             compression cannot touch them.
Missing fields, blockers   → not stored at all. Derived on demand from
                             check_gate_status() and the validation stack (§68).
```

**Mid-phase summary persistence to `improve_case_index` — deferred (§87 item 4).** `SummarizationMiddleware` keeps the compressed summary in `messages[]` for the current session, and gate-pass writes cover durability. Promotion trigger: Belts frequently resume in-flight cases weeks later and the coach needs historical mid-phase context.

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

**Deferred (§87 item 5) — LangSmith trace-based coaching learning.** Tool usage results and reasoning traces are not stored in a form the coaching agent can retrieve. LangSmith has the traces; making them retrievable is a substantial feature needing its own design phase, evaluation criteria, and data schema. This is a v2.2 priority workstream rather than something waiting on a signal.

---

### Memory Retrieval and Control Strategies

Uncontrolled retrieval introduces noise into model reasoning.

- Similarity thresholds ensure only sufficiently relevant memories are retrieved
- Metadata filters — time, user identity, task type — scope retrieval appropriately
- Episodic and semantic memories use separate retrieval strategies
- Retrieved memory volume carefully limited to fit context window constraints

**AgentLean mapping:**

| Control | Ratified treatment |
|---|---|
| Metadata filters | **In refactor scope** — `phase_relevance` on methodology (below); `case_id` on evidence; `status` + `created_at` on case history (§40) |
| Separate retrieval strategies | **Closed by construction** — three distinct tools, each bound to one index with its own filter, ordering, and vector field. The concern that "both indexes are queried the same way" cannot arise. |
| Similarity threshold | **Deferred, §87 item 6** — calibration requires retrieval-quality metrics not yet in place. Promotion trigger: the §75 evaluation dataset populated with representative queries and expected results. |
| Volume limiting | **Deferred, §87 item 7** — dynamic top-k based on remaining context requires middleware to expose context-remaining state cleanly. Promotion trigger: fixed top-k causes context-budget problems in production. |

**The one addition in refactor scope — `phase_relevance` filter.**

`improve_knowledge_index` carries a `phase_relevance` field specifically for filtering by DMAIC phase, and nothing was using it. Adding the filter clause improves retrieval precision immediately, at the cost of one constructor argument:

```python
vs = get_knowledge_vectorstore()          # module-level, lru_cache'd
filters = f"phase_relevance eq '{phase}' or phase_relevance eq 'general'"
ranked_lists = [
    vs.similarity_search(q, k=top_k, filters=filters)
    for q in variants.queries
]
```

**The cross-phase term is `general`, not `all`.** Cross-phase eBook content must
stay reachable from any phase, so filtering strictly to the current phase
over-narrows — but the value that does that is `'general'`. 218 documents in the
index carry it; **zero** carry `'all'`. The earlier `OR 'all'` clause was
never satisfied and narrowed the corpus silently, with no error raised.

**The filter is a per-call argument to `similarity_search`, and the
vectorstore stays module-level.** An earlier revision showed
`search_kwargs={"filters": ...}`; a later correction replaced it with a
per-call `AzureAISearchRetriever(filters=...)` constructor. Both described a
class this codebase does not use. `AzureSearch` takes `filters` at call time,
so the dynamic `phase` value never reaches construction and the `lru_cache`d
singleton is correct. Full reasoning: §33.

**What must be set at construction is `fields=`** — without it,
`phase_relevance` is silently demoted to the unfilterable `metadata` blob on
write, which is the original cause of this section's filter never working.

This is the same set of corrections applied to §33's canonical implementation;
both sections carried identical copies of the same bugs, and both are fixed.

**This filter is methodology-tool-only.** `rag_lookup_evidence` is already filtered by `case_id`, and `rag_lookup_case_history` is inherently cross-phase — neither has a phase-relevance equivalent. The full tool with the filter in place is in §33.

**Gap 21 — closed by the filter above, together with §40's metadata filters on the other two tools.**

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

The nine-step HITL gate (§2) directly addresses the human review governance requirement — the Belt approves what gets committed *before* it is stored, and step 8 makes that ordering explicit. Access controls and memory pruning are production-scale concerns for after the refactor (Gaps 9 and 12). Multi-tenant filtering on `rag_lookup_case_history` is §87 item 1 — not a blocker under the single-tenant assumption, but recorded so cross-tenant leakage cannot be introduced by accident later.

---

### Deferred Items From This Section

All five live in §87 with promotion triggers: per-turn episodic entries (item 3), mid-phase summary persistence (item 4), LangSmith trace-based coaching learning (item 5), similarity threshold calibration (item 6), and dynamic top-k (item 7).

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

*Note: this section originally framed authority as a metadata signal, which reads more cleanly than hardcoded priority rules. It is misleading, though — see Idea 2 below. The actual mechanism is prompt-level priority (§38), not per-chunk metadata scoring.*

---

> **This section splits three ways.** Idea 1 (static metadata filters and ordering) is in refactor scope. Idea 2 (authority weighting) needs no new work — §38 already covers it. Idea 3 (feedback adaptation) is deferred to §87 item 9 with specific caveats.

### Verified Metadata Schema

All seven metadata fields this section references were verified present against the live Azure AI Search indexes during the review:

| Index | Fields relevant to metadata signals |
|---|---|
| `improve_knowledge_index` | `id`, `content`, `content_vector` (3072d), `metadata`, **`source_file`**, **`phase_relevance`**, **`page_number`** (Int32) |
| `improve_evidence_index` | `id`, `content`, `content_vector` (3072d), `metadata`, **`case_id`**, **`phase`**, **`uploaded_at`** *(both added 2026-08-20 — §36)* |
| `improve_case_index` | `id`, `case_id`, `title`, **`belt_level`**, `leader`, `department`, `current_phase`, `rag_status`, **`status`**, **`created_at`**, `target_date`, **`days_in_phase`** (Int32), `phase_summary_define`, `phase_summary_measure`, **`phase_summary_analyse`** *(renamed — §36)*, `phase_summary_improve`, `phase_summary_control`, `content_text`, **`embedding`** |

Two schema facts settled here rather than rediscovered later:
- **Vector field asymmetry is real and harmless** — `content_vector` on knowledge and evidence, `embedding` on case. Each tool knows its own index's field name locally (§36). Not a blocker.
- **`phase_summary_analyse_phase` → `phase_summary_analyse`** — renamed at the source rather than papered over with a mapping constant. Breaking change; see §36 for scope.

**Documentation action:** the full schemas belong in ARCHITECTURE.md §7 as the canonical record, with CLAUDE.md §7 referencing rather than duplicating them — a single source prevents the two governance docs from drifting. This closes a real gap: decisions during the review kept discovering schema facts (vector field names, the field-name inconsistency, `case_id` filter capability, `days_in_phase` as Int32) that were nowhere documented. Confirm the vector dimension on `improve_case_index.embedding` when documenting — most likely 3072, consistent with `text-embedding-3-large` on the other two.

### What We Have But Did Not Use

| Index | Field | Signal Type | Treatment |
|---|---|---|---|
| knowledge | `phase_relevance` | Context | ✅ **Filter** — ratified §37 |
| knowledge | `source_file` | Authority | ✅ **Returned as metadata** for citation, not used as a filter |
| knowledge | `page_number` | Context | ✅ **Returned as metadata** for citation, not used as a filter |
| evidence | `case_id` | Context | ✅ **Filter** — already in the tool signature |
| case | `status` | Authority | ✅ **Filter** — `status eq 'completed'` |
| case | `created_at` | Freshness | ✅ **Order by** — `created_at desc` |
| case | `belt_level` | Context | ⚠️ **Optional parameter, off by default** — see below |
| case | `days_in_phase` | Context | Not used in retrieval |

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

### Idea 1 — Static Metadata Filters and Ordering. IN REFACTOR SCOPE.

Small, concrete, no infrastructure change. Filter and ordering clauses added to the three retrieval tools:

**`rag_lookup_methodology`** — the `phase_relevance` filter is already ratified in §37. No additional filters. `source_file` and `page_number` are useful as *returned* metadata for citation transparency ("this came from page 47 of the BB eBook"), not as filter criteria.

**`rag_lookup_evidence`** —
```python
filter="case_id eq '{case_id}'"       # always
filter += f" and phase eq '{phase}'"  # OPTIONAL — omitted by default
order_by=["uploaded_at desc"]         # the Belt's recent uploads rank first
```
The earlier "verify before implementing — `uploaded_at` may not exist" caveat
is closed: both `uploaded_at` and `phase` were added to
`improve_evidence_index` on 2026-08-20 as top-level fields (§36), so the
ordering clause is available and the phase filter is possible.

**The phase filter defaults to OFF, and that default is deliberate.** A
Control-phase Belt comparing post-improvement results against the Measure
baseline needs Measure-phase evidence; filtering to the current phase by
default would break the cross-phase comparison the field was added to support.
Pass `phase` only when the coach genuinely wants to scope to one phase's
uploads.

**`rag_lookup_case_history`** —
```python
filter="status eq 'completed'"        # completed cases are more authoritative
order_by=["created_at desc"]          # freshness matters for yokoten
```
`belt_level` filtering is deliberately **off by default** — over-narrowing risk, since a Green Belt often benefits from seeing Black Belt cases. Available as an optional parameter for scoped searches.

Metadata filters propagate through RRF cleanly: each variant query returns metadata-filtered results, and fusion combines them normally (§33).

### Idea 2 — Authority Weighting Between Sources. NO NEW WORK.

The §38 memory-hierarchy paragraph in the coach's system prompt already handles this: methodology > confirmed captured fields > case history > recent messages. §40's framing of authority as a metadata signal is misleading — the actual mechanism is prompt-level priority, not per-chunk metadata scoring. Nothing to build here.

---

### Metadata-Driven Ranking Strategies

**Relevance Scoring** — combines vector similarity and metadata to rank results. Not just semantic match but weighted combination of similarity + freshness + authority.

**Freshness Boosting** — prioritises newer more current information when applicable. Applied to `improve_case_index` via `created_at desc` ordering. Not applied to `improve_knowledge_index` — eBook methodology does not expire.

**Authority Weighting** — elevates results from trusted and thoroughly validated sources. eBook content ranks above case data. Completed cases rank above in-progress cases.

**Feedback Adaptation** — continuously improves ranking using user and system feedback loops. The only dynamic strategy — ranking changes based on accumulated evidence of what actually works.

---

### Idea 3 — Feedback Adaptation. DEFERRED TO §87 ITEM 9, WITH CAVEATS.

*The concept below is valid and worth keeping — a coaching system that learns from Belt outcomes is more valuable than static ranking. The sketched implementation has three real problems, documented after it so the eventual v2.2 design does not repeat them.*

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

**The sketched implementation — and why it does not survive scrutiny:**

```python
# SKETCH ONLY — NOT the v2.2 design. See the three problems below.
async def record_positive_feedback(phase_chunks: list, phase: str):
    for chunk in phase_chunks:
        await update_chunk_score(chunk.id, phase, delta=+0.1)

async def record_negative_feedback(correction: dict, chunks_used: list):
    for chunk in chunks_used:
        await update_chunk_score(chunk.id, correction["field"], delta=-0.1)
```

**Problem 1 — causal attribution.** Every chunk retrieved during a phase receives the same +0.1 credit for gate passage. But a Belt might pass *despite* unhelpful chunks; the chunks that actually helped might have been from turn 3 while turns 1, 5, and 8 retrieved noise. There is no turn-level attribution. Over 50 projects, useful chunks and noise chunks both accumulate scores, and the signal degrades toward "how often was this chunk retrieved."

**Problem 2 — selection bias and cold drift.** A chunk demoted enough to fall below top-k stops being retrieved, and therefore can never accumulate positive feedback again. Chunks disappear silently from the effective corpus with no mechanism for recovery.

**Problem 3 — infrastructure.** Azure AI Search does not natively support per-chunk boost adjustments. Implementing this needs an external score table (Cosmos DB or Blob) combined with vector similarity at query merge time. That is real infrastructure work, not the quick win the code sketch implies.

**A better v2.2 formulation** would use LangSmith trace analysis for *retrospective* attribution, or offline evaluation runs comparing retrieval variants — not real-time in-line score updates. That is a genuine research workstream with its own design phase, which is why it is deferred rather than scheduled.

**Promotion trigger (§87 item 9):** retrieval evaluation shows systematic misses that static ranking and metadata filters cannot fix, and a dedicated v2.2 research workstream is established.

*(The prerequisite noted in the original — that field corrections are only capturable once the Belt has a review step — is satisfied: §2's nine-step gate provides exactly that signal. The blocker was never HITL; it is attribution and infrastructure.)*

### Gap 21 — Closed

Gap 21 was originally scoped to the `phase_relevance` filter only, then broadened to cover all unused metadata signals. Its scope now resolves as:

| Item | Status |
|---|---|
| `phase_relevance` filter on knowledge index | ✅ In scope — §37 |
| `status eq 'completed'` filter on case index | ✅ In scope — Idea 1 |
| `created_at desc` ordering on case index | ✅ In scope — Idea 1 |
| `belt_level` filter | ✅ Optional parameter, off by default |
| `source_file` / `page_number` returned for citation | ✅ In scope — closes Gap 33 |
| Authority weighting | ✅ No new work — §38 |
| Feedback adaptation | ⏸ Deferred — §87 item 9 |

*Cross-references: §32/§33 (the tools these filters attach to), §36 (schema and the field rename), §37 (`phase_relevance` filter), §38 (memory hierarchy handles authority), §87 item 9.*

---

## 41. Target Retrieval Pipeline — System-Level Workflow

*Source: Edureka Course 2 — System-Level Workflow*

### The Six-Step Pipeline

| Step | What It Does | Ratified treatment |
|---|---|---|
| 01 User Query | User submits information request | ✅ Works |
| 02 Tool Invocation | Tools retrieve candidate documents | ✅ Three `rag_lookup_*` tools (§32) |
| 03 Query Refinement | Improve the query when results are weak | ✅ **Proactive form** — multi-query variant generation (§32). Reactive self-correction subsumed (§38). |
| 04 Metadata Filtering | Filter using context and authority signals | ✅ Per-tool filters (§37, §40) |
| 05 Ranking Engine | Rank by combined scores | ✅ RRF across variants (§33) |
| 06 Final Context Output | Top-ranked context to the reasoning layer | ✅ `before_model` injection + `SummarizationMiddleware` budget (§36, §38) |

Every step is accounted for. Note that steps 03–05 all live **inside a single tool call**, not as separate pipeline stages — see the Terminology Reference.

---

### The Complete Retrieval Pipeline for Agent Improve

```
Belt sends message (01)
        ↓
Phase planner decides retrieval_strategy (§71)
  single_hop → one tool call
  multi_hop  → three-hop chain, Analyse phase
        ↓
rag_lookup_* tool invoked (02)
        ↓
  ┌─── INSIDE THE TOOL ────────────────────────────────┐
  │                                                    │
  │ Variant generation (03)          ← §32             │
  │   3-5 alternative phrasings, phase-shaped prompt   │
  │        ↓                                           │
  │ Per-variant retrieval with metadata filters (04)   │
  │   methodology: phase_relevance eq phase OR 'general'│
  │   evidence:    case_id eq current_case,            │
  │                order_by uploaded_at desc     ← §36 │
  │   case:        status eq 'completed',              │
  │                order_by created_at desc      ← §40 │
  │        ↓                                           │
  │ Reciprocal Rank Fusion (05)      ← §33             │
  │   score = sum 1/(k + rank), k=60                   │
  │        ↓                                           │
  │ top_k returned, with source_file + page_number     │
  │ metadata for citation                              │
  └────────────────────────────────────────────────────┘
        ↓
Executor receives documents; may make further tool calls
  (multi-hop, capped at 5 — §34)
        ↓
Context assembly (06)
  before_model middleware prepends structured state    ← §38 Gap 22b
  SummarizationMiddleware bounds message history       ← §36
  memory-hierarchy paragraph orders authority          ← §38 Gap 22a
        ↓
LLM receives clean grounded context
        ↓
Coaching response → coherence check (§68 Layer 2a)
```

---

### Gap Mapping to Pipeline Steps

```
Step 03 Query Refinement    → Gap 15  (multi-query variants) — in scope
Step 04 Metadata Filtering  → Gap 21  (phase_relevance, case_id, status, freshness) — in scope
Step 05 Ranking Engine      → Gap 16  (RRF) — in scope
Step 06 Context Output      → Gap 22a/22b (prompt hierarchy + before_model) — in scope
                              Gap 19  (working memory compression) — closed by §36
```

This is the complete picture of what the retrieval layer becomes. All six steps are designed; none are deferred.

---

# PART 4 — QUALITY AND VALIDATION

*How output is checked before a Belt ever sees it, and where the human's own edits get a second opinion.*

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
    return Command(update={"validator_feedback": critique}, goto="planner")
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
| Where it appears in this document | §29 (superseded), §42 `DMAICGraderMiddleware`, §48 `DMAICGateValidator`, §68 four-layer stack | §22 (Debate — deferred to §87), §46, §47 (deferred to §87) |

*This distinction is the clearest statement in the document of when each pattern applies, and it is preserved verbatim for that reason. Everything in the ratified validation architecture is **reflection**. The only genuine consensus mechanism — the debate subgraph — is scoped to Analyse-phase root cause validation and deferred to v2.2.*

### Why Reflection Was the Correct Tool for Most of What Has Been Built

Reflection is the right tool for the large majority of what Agent Improve needs:
- "Is this extracted field complete?" → reflection (§68 Layer 2b, `DMAICGateValidator`)
- "Does this gate document satisfy the DMAIC rubric?" → reflection (§68 Layer 2d, `DMAICGraderMiddleware`)
- "Does this decision address the phase constraints?" → reflection (§68 Layer 2c)
- "Is this response coherent, or gibberish?" → reflection (§68 Layer 2a)
- "Is this JSON output malformed?" → no longer a question; native structured output makes it unrepresentable (§29, §82)

These are all single-conclusion quality checks. There was never a second legitimate opinion to reconcile — just a standard to meet or fail. Relying on reflection here was the correct instinct, not a gap to retroactively fix.

### Where Reflection Alone Is Structurally Insufficient

The specific failure mode reflection cannot catch: **when the LLM's single reasoning pass might be systematically biased or have a blind spot, and a self-check by the same kind of reasoning is unlikely to catch its own blind spot.**

Root cause identification is the clearest DMAIC example. If the coaching LLM proposes a root cause and then reflects on its own proposal, it is likely to find its own reasoning convincing — that is precisely what a blind spot is. Reflection cannot catch a blind spot it does not know it has. A genuinely independent skeptic position, generated separately and instructed to argue the opposite, has a structurally different chance of surfacing what a self-check would miss. This is why Section 22's debate subgraph is built as two separate agent calls (advocate, skeptic) rather than one agent reflecting twice.

### The Practical Rule Going Forward

```
Use reflection when:         the question is "did I do this correctly against a known standard"
                              → completeness, format, constraints, rubric satisfaction

Use consensus modeling when: the question is "could I be wrong in a way I wouldn't notice myself"
                              → root cause validation, high-stakes irreversible decisions
```

Both belong in Agent Improve, but not on the same timeline. Reflection is the default for the vast majority of quality checks — cheap, fast, sufficient — and all of it is in refactor scope. Consensus modeling is reserved for the small number of genuinely high-stakes, hard-to-self-detect decisions, and is deferred to v2.2 (§87 item 10) given its added latency and cost.

---

### The Two-Layer Validation Design — and How §68 Extends It to Four

This section originally ratified a **two-layer** design:

- **Layer 1 — `DMAICGateValidator`** (deterministic, rule-based, no LLM call). Static methods checking objective properties: does the problem statement contain a number? Does the scope mention exclusions? Does the goal have a time-bound keyword? Cheap, instant, deterministic.
- **Layer 2 — `DMAICGraderMiddleware`** (LLM-as-a-judge, subjective quality). Checks whether content is *meaningfully* correct, not merely structurally present. Is the problem statement a real measurable problem? Is the root cause grounded in evidence?

Layer 1 runs before Layer 2 — if the deterministic checks fail, no LLM grader call is made; fix the obvious issues first.

**§68 expands this to four layers**, and the two above become 2b and 2d:

```
Step 2a: Coherence check         lightweight LLM     §69
Step 2b: Field presence          deterministic       §48 DMAICGateValidator
Step 2c: Constraint validation   lightweight LLM     §68
Step 2d: Quality rubric          LLM grader          §42 PHASE_RUBRIC (not the middleware)
```

All four run inside the same pre-Belt window — before the interrupt fires at step 3 of §2's nine-step pattern. The iteration cap of 3 is **shared across all four layers**, with accumulated feedback, not three attempts per layer.

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
@traceable                                   # §1 — otherwise invisible in LangSmith
def validate_define_gate(state: PhaseState) -> list[str]:
    """Returns a list of failure messages. Empty list = Layer 2b passes."""
    failures = []
    fields = state["artifacts"]              # §18 — not captured_fields

    checks = [
        DMAICGateValidator.validate_problem_statement(fields.get("problem_statement", "")),
        DMAICGateValidator.validate_smart_goal(fields.get("goal_statement", "")),
        DMAICGateValidator.validate_scope(fields.get("project_scope", "")),
    ]

    for passed, message in checks:
        if not passed:
            failures.append(message)

    return failures
```

**These are Define-phase validators only.** Measure, Analyse, Improve, and Control each need their own deterministic validators — for example `validate_baseline_has_units`, `validate_root_cause_has_evidence_reference`, `validate_control_plan_has_owner`. Draft them during the governance-doc rewrite, alongside the phase rubrics in §42.

**Connection to the grader (§42, §54):** the grader does the same thing at a higher level — per-criterion evaluation returning targeted feedback. `DMAICGateValidator` is the deterministic, rule-based equivalent for properties that can be checked without LLM reasoning (numeric presence, word count, keyword presence). Use the validator for objective checks and the grader for subjective quality. Both produce the same output shape: per-criterion pass/fail with reasons — which is what lets §68 run them as consecutive layers with one shared feedback accumulator.

*Note that §42's Option B decision applies here too: the grader is a custom `DMAICGraderMiddleware` on `create_agent`, not deepagents' `RubricMiddleware`.*

---

### The Simulated LLM Caveat — Worth Recording

The course demo explicitly uses a fake LLM: *"This is not a real LLM call. It's a simulation so the demo always behaves consistently."* Attempt 1 is hardcoded to fail, attempt 2 to pass.

**What this means for production:** the two-attempt simulation does not demonstrate real LLM non-determinism. In production, attempt 2 can also fail, or can fix one criterion while introducing a new failure. The `max_iterations=3` cap (§42) handles this — always set a maximum to prevent infinite correction loops. On `max_iterations_reached`, output passes through with a warning flag visible to the Belt, who becomes the final arbiter (§69 Level 4).

*Cross-references: §2 (the nine-step gate this validation sits inside), §22 (debate — the consensus counterpart, deferred), §42 (`DMAICGraderMiddleware` as Layer 2d), §46 (coordination taxonomy — priority-based resolution now covered), §47 (opinion aggregation — deferred with §22), §68 (the four-layer stack), §69 (where each check fires and what the Belt sees).*

---

## 68. Decision Validation Against Business Constraints — Resilient Decision Agent Pattern

*Source: Edureka Course 4 Module 2, "Resilient Decision-Making Agent" demonstration transcript. Verified against current langchain_core documentation — same PromptTemplate caveat as Section 48 applies: use ChatPromptTemplate for gpt-4o/Azure OpenAI.*

### What Makes This Different From OutputFixingParser and RubricMiddleware

| Pattern | What It Validates | When It Applies |
|---|---|---|
| `OutputFixingParser` (§29) | Format correctness — is the JSON valid? | *Obsolete — native structured output* |
| `DMAICGraderMiddleware` (§42, §54) | Content quality — does it meet the rubric? | Gate document quality |
| `DMAICGateValidator` (§48) | Field completeness — are required fields present? | Gate field presence checks |
| **Decision validation (this section)** | **Business constraints — does the decision address budget / timeline / risk / measurement?** | **Before acting on a decision** |

Decision validation validates a **choice before it is acted upon**, not the quality of an artifact after it is produced.

---

### The Ratified Four-Layer Gate Validation Stack

*This section is where the two-layer design of §48 becomes four. It is the complete gate validation architecture.*

| Layer | What it checks | Mechanism | Model | When it fires |
|---|---|---|---|---|
| **1. Coherence** | Is this a real, meaningful, conclusive statement? Catches gibberish, vague non-answers, self-contradiction, off-topic replies, and parroting the Belt's own words back. | **Lightweight LLM check** | `operational-model` (gpt-4o-mini), temp 0.1 | **Every coaching turn** |
| **2. Field presence** | Are all **Tier 1** fields for this phase populated? | Deterministic — field existence on `PhaseState` | **No LLM** | Gate boundary only |
| **3. Constraint validation** | Does the decision address budget / timeline / risk / measurement? | **Lightweight LLM check** | `operational-model`, temp 0.1 | Gate boundary + mid-conversation for key decisions |
| **4. Quality rubric** | Does it meet DMAIC quality standards per criterion? **Tier 1 can fail; Tier 2 warns.** | `DMAICGraderMiddleware` (§42) | `operational-model`, temp 0.1 | Gate boundary only |

**Run cheapest first, most expensive last. Each layer fires only if the previous one passes.**

### The Two Tiers Resolve a Layer 2 / Layer 4 Contradiction

**As originally specified, Layers 2 and 4 could disagree with no defined resolution.** Layer 2 blocked on a required-field list; Layer 4 graded against a rubric; the two sets were not the same set. A phase could clear the gate at Layer 2 and then be failed by the grader on a criterion Layer 2 had never asked for — and nothing said which one won.

**Every rubric criterion now carries a tier** (§42 Decision 4):

- **Layer 2 checks Tier 1 only.** Missing Tier 1 field → gate blocked.
- **Layer 4 checks both tiers.** Tier 1 can return `fail`; Tier 2 can only return `warning`.
- **A gate passes with warnings. A gate never passes with failures.**

The grader's structured verdict gains `"warning"` alongside `"pass"` and `"fail"` to carry this, and a `tier` field so the caller can see which rule applied. A Tier 2 gap the Belt proceeds past is written into the gate document as an `acknowledged_gaps` entry rather than discarded, so the next phase's planner can see it.

**The counter and the accumulated feedback are state fields, not locals.** The shared cap of 3 is `PhaseState.gate_attempts`; the accumulated feedback that the retry loop below depends on is `PhaseState.validator_feedback` (§18). Both are checkpointed. Holding either in route scope is the v1 defect this stack exists to avoid — a cap that resets on every request is not a cap.

### Why Layer 1 Is an LLM, Not a Length Check

The original design had coherence as a deterministic check — word count plus a question-mark test:

```python
# ORIGINAL — deterministic coherence. NOT SUFFICIENT.
def check_coherence(decision: str) -> tuple[bool, str]:
    if len(decision.split()) < 10:
        return False, "Decision too brief — lacks detail"
    if "?" in decision:
        return False, "Decision is questioning — must be conclusive"
    return True, "Decision is coherent"
```

The objection that settled it: *"I can write garbage in and a length check will not detect it."*

That is correct, and it is decisive. Twelve words of fluent nonsense passes both tests. So does "there are some issues with the process" — a vague non-answer that is structurally perfect and informationally empty. So does a response that contradicts itself across two sentences, or one that restates the Belt's own words with no added value. **A format check cannot detect any of these**, and every one of them is a real failure mode in coaching dialogue.

**Cost:** Layer 1 fires every coaching turn — roughly 20–40 times per phase session. At ~250 tokens per check on `gpt-4o-mini`, that is about **$0.01–0.02 per phase session**. Negligible. The quality improvement justifies it comfortably.

**Layer 2 stays deterministic.** Checking whether a key exists in a dictionary genuinely does not need an LLM. It is the only deterministic layer in the stack.

### Layer 3 Implementation

```python
class ConstraintVerdict(BaseModel):
    constraint: str
    addressed: bool
    evidence: str            # which part of the decision addresses this constraint


class ConstraintCheckResult(BaseModel):
    all_satisfied: bool
    verdicts: list[ConstraintVerdict]


constraint_checker = operational_model.with_structured_output(ConstraintCheckResult)


@traceable                                    # §1 — otherwise invisible in LangSmith
def validate_constraints(
    decision: str,
    constraints: dict,
    phase: str,
) -> ConstraintCheckResult:
    return constraint_checker.invoke(
        f"Check whether this {phase} phase decision addresses each constraint.\n\n"
        f"Decision: {decision}\n\n"
        f"Constraints to check:\n"
        + "\n".join(f"- {k}: {v}" for k, v in constraints.items())
    )
```

Model: `operational-model` (gpt-4o-mini). Temperature 0.1, for consistent verdicts. Structured output per §82.

*The original keyword-matching version — `if "budget" not in decision.lower()` — fails the same way the deterministic coherence check does. A decision that thoroughly addresses cost without ever using the word "budget" would be rejected; one that says "budget is not a concern" would pass.*

**Value-dependent constraints — preserved and worth implementing.** Constraints can be conditional on other field values. The clearest example: the risk-mitigation check fires only when `risk_level == "low"`, because a low-risk project should explicitly say how it stays low-risk, whereas a high-risk project's decision inherently involves risk. This is more sophisticated than a flat constraint list and should be implemented for any constraint that is conditional on another field.

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

**In Agent Improve, `previous_feedback` is `PhaseState.validator_feedback`** — a list rather than a single value, appended to by every layer on every failed attempt, and read in full by the coach on retry:

```python
{"attempt": 1, "layer": "grader",
 "criteria_failed": ["root_cause_validation"],
 "feedback": "does not reference statistical evidence",
 "timestamp": "2026-08-03T11:04:19Z"}
```

Reset to `[]` when the gate passes. **The cap of 3 is only defensible because of this field.** Three attempts that each start from nothing is three chances at the same mistake; three attempts that each know what the previous two got wrong is a convergent loop, which is what the DMAIC example below demonstrates.

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

*Ratified per-phase constraint sets:*

```python
DEFINE_CONSTRAINTS = {
    "baseline": "must reference a measurable current state",
    "target": "must include a specific improvement target",
    "scope": "must define what is included and excluded",
    "timeline": "must reference a project timeline",
}

ANALYSE_CONSTRAINTS = {
    "root_cause": "must identify a specific, actionable root cause",
    "validation": "must reference how root cause was validated",
    # Value-dependent: the risk check fires only when risk_level == "low"
}

IMPROVE_CONSTRAINTS = {
    "budget": "improvement approach must address cost",
    "deadline": "implementation plan must reference timeline",
    "measurement": "must specify how improvement will be measured",
}

CONTROL_CONSTRAINTS = {
    "monitoring": "control plan must specify monitoring frequency",
    "sustainability": "must define process for maintaining gains",
    "handover": "must identify process owner accepting responsibility",
}
```

*Measure's constraints are covered by its rubric (§42) — `baseline_mean` with units, GR&R evidence, a data collection plan — rather than by a separate constraint set. Add one if production experience shows the rubric alone is insufficient.*

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

This is the connection between decision validation and §2's HITL gate — when the self-correction loop exhausts its attempts, the decision escalates to the Belt rather than the system deciding unilaterally. **The Belt is the final arbiter, not the agent.** See §69 Level 4.

---

### The Complete Validation Stack — Where It Sits in §2's Nine Steps

All four layers run inside **step 2** of the nine-step HITL pattern — before the interrupt fires at step 3, so the Belt is never shown output the system already knows is below standard:

```
Step 2a  Coherence check         lightweight LLM, EVERY turn         §69
Step 2b  Field presence          deterministic, DMAICGateValidator   §48
Step 2c  Constraint validation   lightweight LLM                     this section
Step 2d  Quality rubric          gate document grader, PHASE_RUBRIC   §42

Cheapest first, most expensive last. Each fires only if the previous passes.
Shared cap: 3 attempts across all four, with accumulated feedback.
```

Note that only **one** layer is deterministic (2b). The original stack had three of four deterministic; both coherence and constraint checking were upgraded to lightweight LLM calls for the reason given above — format checks cannot detect content failures.

*This supersedes §48's two-layer design, which becomes 2b and 2d.*

### Gap Register Note
No new gap number. **The four-layer stack is the complete implementation target for Gap 23.** Each attempt is logged to `step_log` as a dict (§18):

```python
{"layer": "constraint", "attempt": 2, "status": "failed",
 "reason": "does not address timeline", "decision_excerpt": "..."}
```

*Cross-references: §2 (all four layers fire in step 2), §18 (`step_log` dict format), §42 (Layer 4 grader), §48 (Layer 2 validator, and the two-layer design this expands), §69 (which failures the Belt sees and which they do not), §82 (structured output for Layer 3 verdicts).*

---

## 69. Validation Layer Placement — Where Each Check Fires Across Agent Improve

*Source: Direct discussion clarifying where Sections 48, 68's validation patterns apply — every subagent turn vs gate boundaries only.*

### The Question

Do the four validation layers (coherence, field presence, constraint, rubric) fire at gates only, or at every subagent turn?

**Answer: it depends on the layer. Cheapest layers fire everywhere. Most expensive layers fire only at gates.**

---

### Where Each Layer Fires

**Coherence check — every coaching turn, all subagents**

Every LLM output should be coherent before it reaches the Belt. Gibberish, a vague non-answer, a self-contradiction, or the Belt's own words parroted back is a generation failure regardless of phase or gate proximity. Cheapest check in the stack, always worth running.

```
Every coaching turn:
  LLM generates response
  → coherence check (lightweight LLM — §68 Layer 1)
  → FAIL: retry silently, Belt never sees it
  → PASS: send to Belt
```

*Per §68 this is a lightweight LLM call rather than the length-and-question-mark test originally proposed — a format check cannot detect the failures that actually occur.*

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

**Rubric / quality evaluation (`DMAICGraderMiddleware`) — gate boundary only**

The most expensive validation, and the one whose judgment is least useful mid-conversation — a phase in progress *should* fail its rubric. Only fires when the Belt is ready to close a phase and all cheaper checks have passed.

---

### Complete Validation Map

| Validation Layer | Every Turn | Key Decision Moments | Gate Boundary |
|---|---|---|---|
| Coherence check (2a) | ✅ always | ✅ always | ✅ always |
| Field presence (2b) | ❌ | ❌ | ✅ gate only |
| Constraint validation (2c) | ❌ | ✅ for key proposals | ✅ gate, full check |
| Quality rubric (2d) | ❌ | ❌ | ✅ gate only, last |
| **Mid-phase contradiction (§38)** | ✅ always | ✅ always | ✅ always |

**Run in order: cheapest first, most expensive last. Only invoke the next layer if the previous passes.**

*The last row is the §38 addition — the policy advisory's structured diff over previously approved values. It fires on every turn like coherence does, and costs nothing (no LLM call), but unlike coherence its failure is never silent: a contradiction with a gate-approved value always surfaces to the Belt.*

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

**The critical distinction — and the principle behind it:**

```
Coherence failures         → handled SILENTLY by the system
                              Belt never sees a failed coherence check
                              system self-heals invisibly

Everything else            → handled COLLABORATIVELY with the Belt
                              Belt receives the feedback
                              Belt participates in fixing it
                              Belt approves before advancing
```

> **Design principle: *"Coached improvement is key as silent is not transparent."***
>
> The default posture of the system is **transparency** — the Belt sees what is happening and participates in fixing it. Silent retry is the narrowly scoped exception, and it is justified only because visibility would harm the Belt's experience without giving them anything actionable: showing a Belt that the AI produced gibberish adds no value and erodes trust in the coach. They see the corrected response.
>
> Everything else — constraint failures, field completeness, quality rubric, value contradictions — is visible and collaborative. In particular, a constraint failure on a Belt's own proposal is **a teaching moment, not an error**. When a Belt says "the root cause is poor morale," the coach's job is to teach what makes a root cause actionable, not to silently reject and re-ask. That is core DMAIC pedagogy, and it is why constraint validation fires mid-conversation at all.

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

**Retry behaviour per level (ratified):**

| Level | Retry policy |
|---|---|
| 1 — Silent | Max **2** silent retries, then degraded mode ("I need a moment to reconnect…") |
| 2 — Coached | **No retry cap.** This is coaching dialogue, not a retry loop. The coach keeps working with the Belt until the proposal improves or the Belt signals gate readiness. |
| 3 — Validated | Max **3** attempts, with accumulated feedback across all four validation layers |
| 4 — Escalated | **No retry.** The Belt decides manually. |

Level 2 having no cap is deliberate and is the difference between a coaching system and a validation system. Capping it would mean the coach eventually gives up and accepts a weak root cause — which is precisely the outcome DMAIC discipline exists to prevent.

### Gap Register Note
No new gap number — this section maps the four-layer validation architecture (§48, §68) to its firing points and, more importantly, ratifies **what the Belt sees at each one**. Use the tables here directly when specifying node behaviour in ARCHITECTURE.md v2.2.

*Cross-references: §2 (the nine-step gate), §38 (mid-phase contradiction — the fifth check in the map), §42 (Layer 2d), §48 (Layer 2b), §66/§67 (degraded mode at Level 1), §68 (the four layers).*

---

## 29. OutputFixingParser — The Pre-1.0 Parse-Then-Validate Pattern

*Source: Edureka Course 2 — OutputFixingParser: Role and Workflow*

> **Status: historical. Do not build against this.** `OutputFixingParser` is not wrong for its era, but it is superseded by LangChain 1.x native structured output. Read this section for the *concerns* it identifies — format, schema, content — then read where each concern actually lives in the ratified architecture, below.
>
> **Web-verified 2026-07:**
> - `OutputFixingParser` moved to `langchain-classic` (compatibility path, v1.3.4)
> - Main `langchain` v1.x exposes native structured output strategies — `ToolStrategy`, `ProviderStrategy`, `NativeStrategy`, `AutoStrategy` — via `response_format=` on `create_agent` or the builder-style call on a plain model
> - GitHub issue #34098 (Nov 2025) is an *open feature request* asking for `OutputFixingParser` to come back to core, which confirms it is no longer on the recommended path
> - Sources: `python.langchain.com/api_reference/langchain/output_parsers/langchain.output_parsers.fix.OutputFixingParser`; `reference.langchain.com/python/langchain-classic/output_parsers`; GitHub issue #34098

### What It Is

Checks LLM output against a schema and **automatically fixes errors** to ensure the final result follows the required format. All correction logic is inside the parser — you write none of it.

### How It Works

```
LLM Output → Validate → Valid Output → Output
                ↓ Invalid
            Fix with LLM → Validate Again → Output
```

The parser calls the LLM a second time with a correction prompt if the first output fails validation. Then validates again before passing the result downstream.

### Reflection Node vs OutputFixingParser — Still a Useful Framing

| Approach | How it works | Where logic lives | Status |
|---|---|---|---|
| Reflection node | A separate LangGraph node re-invokes the LLM on bad output | Explicit in the graph — visible, controllable | **Current pattern for graph-visible retry** — §48 |
| Native structured output | Provider guarantees schema-conformant output at the API level | Enforced at the model call | **Current pattern for format and schema** — §82 |
| `OutputFixingParser` | Parser catches bad output, auto-fixes via a second LLM call | Hidden inside the parser | **Legacy** — `langchain-classic` |

**Reflection node advantages** (unchanged, and why §48 keeps it):
- Fully visible in the LangGraph trace
- You control retry logic, prompt, and fallback
- The fix attempt is a first-class graph event with its own checkpoint

For *invisible* retry — the kind that should not appear in the Belt's view or the graph topology — LangChain 1.x provides **`ToolRetryMiddleware`** (`wrap_tool_call` hook), which auto-retries failed tool calls with configurable backoff. Use it where a retry is a mechanical concern, and a reflection node where the retry is a coaching event.

> **The class is `ToolRetryMiddleware`, not `RetryMiddleware`.** An earlier
> revision of this section named a class that does not exist in LangChain 1.x.
> The mechanism is real and is already wired — it is position 5 of the
> eight-middleware stack (§84), configured
> `max_retries=2, on_failure="continue"`. `on_failure="continue"` is what keeps
> the coaching loop alive: when retries are exhausted the tool returns a failure
> result the coach can react to, rather than raising and killing the graph.
>
> It is a **different** middleware from `ModelRetryMiddleware`, which sits at
> position 4 on `wrap_model_call` and retries the *model* call on Azure OpenAI
> rate limits and transient 5xx. Tool execution failures and model API failures
> are different failure modes; neither middleware substitutes for the other,
> and both are distinct again from the fallback chain (§67), which swaps the
> model on service-level failure.

### What Happened to the "Three-Layer Defence"

The original model stacked three layers in a linear pipeline:

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

Under the ratified architecture only the third layer survives, and it does not live in a pipeline:

| Original layer | Status |
|---|---|
| `OutputFixingParser` | **Obsolete.** ProviderStrategy (§82) guarantees valid schema output at the API level — there is nothing left to fix. |
| Pydantic validation | **Subsumed.** The schema *is* the Pydantic model passed to the structured-output call. Same location, same mechanism. |
| Completeness check | **Still relevant.** A content-level concern. Lives as a bound tool or a conditional edge, not as a pipeline stage. |

### Where Each Concern Actually Lives

| Concern | Where it lives now |
|---|---|
| Format validation | `response_format=CoachingResponse` on the executor, via native structured output. No separate parser. |
| Schema validation | Same location, same mechanism — native to ProviderStrategy (§82) |
| Completeness | The `check_gate_status` tool invoked by the executor, **or** a conditional edge on the subgraph checking whether the required field count is met. Formalised as Layer 2b of the gate stack (§48, §68). |
| Content-level hallucination | **Not addressed by §29 at all.** See below. |
| Retry on failure | **Already wired, not a residual concern.** `ToolRetryMiddleware` (position 5, `wrap_tool_call`) for invisible tool retry and `ModelRetryMiddleware` (position 4, `wrap_model_call`) for model API retry — both in the §84 stack; the §48 reflection node for graph-visible retry; the shared 3-attempt cap across the four validation layers (§68) |

### Anti-Hallucination — Orthogonal, and Not Solved by Any of This

**Neither `OutputFixingParser` nor ProviderStrategy addresses content-level hallucination.** Structured output guarantees the *shape* of the answer, not its truth. A perfectly schema-valid `baseline_metric: 4.2` invented by the model is exactly as well-formed as a correct one.

Content-level defence requires three separate things, none of which are parsers:

1. **Explicit anti-hallucination guards in the executor's prompt** — the LLM must never invent field values from coaching templates. This is a standing requirement on all orchestrator prompts.
2. **Cross-checking extracted values against the raw conversation** — did the Belt actually say this?
3. **The policy advisory (§2) reviewing extracted values before Belt approval**, plus the coherence layer (§68 Layer 2a), which catches parroting and vague non-answers that a format check cannot.

No reader should come away from this section assuming structured output is sufficient defence against hallucinated content. It is not.

*Cross-references: §2 (policy advisory), §42 (`DMAICGraderMiddleware` — quality evaluation), §48 (reflection nodes, `DMAICGateValidator`), §51 (InsightForge self-correcting pipeline — same deprecated layer, same replacement), §68 (the four-layer stack this distributes into), §82 (ProviderStrategy), Terminology Reference (tools bound to an executor, not layers in a chain).*

---

## 22. Debate Agents and Consensus Voting

*Source: Edureka course — Debate Agents with Consensus Voting*

> **Scope: deferred to v2.2 — §87 item 10. NOT implemented in v2.1** *(confirmed 2026-08-19)*. The pattern is correct and the scoping is settled: an adversarial debate subgraph (advocate + skeptic + judge) for **root cause validation in the Analyse phase only**. It is deferred because it depends on the base coaching loop working in production first, and it adds 2–3 LLM calls per root-cause evaluation.
>
> **The promotion trigger is evidence, not a date.** Test the ordinary Analyse node in production first, then decide whether adversarial debate is needed: is the Analyse coach producing root causes that survive scrutiny, or root causes that need adversarial stress-testing? Building the debate subgraph before that question has a real answer risks solving a problem the base loop does not have — at a permanent cost of 2–3 LLM calls on every root-cause evaluation.
>
> **§47 (Opinion Aggregation) is blocked behind this section** and deferred with it — §87 item 11. Its input signals, `advocate_confidence` chief among them, are produced by the debate subgraph and do not exist until this is built. It cannot be ratified independently.
>
> Read this section alongside §48, which draws the distinction this pattern rests on: **reflection** is one perspective checking itself against a standard (`DMAICGraderMiddleware`, §42); **consensus modeling** is multiple genuinely independent perspectives that may legitimately disagree, being reconciled. Only root cause validation in Analyse is genuinely the second kind.
>
> `DebateState` is the one place in Agent Improve where inheriting `MessagesState` is the right call rather than an explicit `TypedDict` — its dominant content really is conversational exchange (§10).

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

# PART 5 — RELIABILITY AND FAILURE HANDLING

*What happens when a call times out, a service degrades, or a gate has to be reopened after downstream work already landed.*

---

## 79. LangGraph 1.2 Native Reliability Primitives — Per-Node Timeouts, Error Handlers, DeltaChannel

*Source: LangChain official changelog (docs.langchain.com/oss/python/releases/changelog), LangGraph 1.2 release May 11, 2026. Verified against docs and multiple independent 2026 sources.*

### What Changed

LangGraph 1.2 (May 11, 2026) added production-grade reliability primitives that are now **built into LangGraph itself** — no custom implementation needed. Several concepts previously documented as custom patterns in §49 and §66 are now framework-native.

> **Status: ratified. Three of four primitives adopted; requires LangGraph 1.2.6+ (upgrade target 1.2.10).**
>
> | Primitive | Decision |
> |---|---|
> | **Per-node timeouts** | **Adopt.** `TimeoutPolicy(run_timeout=45)` on every phase executor node. 45s is the wall-clock limit; the fallback chain fires before the Belt notices the delay. |
> | **Node-level error handlers** | **Adopt.** `error_handler=` carries the Saga compensating actions from §49. Every node with external writes gets one. |
> | **Graceful shutdown** | **Adopt.** `RunControl.request_drain()` for deployment rollouts — mid-coaching sessions save their checkpoint and resume later. Production-grade session preservation. |
> | **DeltaChannel** | **Deferred — §87 item 12.** Beta API, and not needed until coaching sessions exceed ~200 turns. Genuinely premature: no production evidence of need. |
>
> **Impact on other sections:** §49 rewrites to use native `error_handler=` instead of custom compensating nodes; §66 gains per-node timeouts as Step 0 of the failure pipeline; §67's chain is triggered by `NodeTimeoutError` before retries begin; §52 notes `DeltaChannel` as a future checkpoint-compression option.

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
            "partial_fields": state.get("artifacts", {}),
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
class SupervisorState(TypedDict):
    messages: Annotated[list, DeltaChannel(snapshot_frequency=50)]
    # every 50 steps, a full snapshot is written
    # steps in between store only deltas
```

**Deferred — §87 item 12.** Two reasons, and both matter: it is a **beta API** in a system that has just spent a whole review removing pre-1.0 dependencies, and there is no production evidence that checkpoint size is a problem yet. Promotion trigger: long-running DMAIC projects accumulate checkpoint-size problems in production, which in practice means sessions exceeding roughly 200 turns. The trade-off when it arrives: rebuild latency (small) against storage growth (significant over weeks).

---

### Cross-Reference Impact on Existing Sections

| Existing Section | Change Applied |
|---|---|
| §49 (Saga) | ✅ Rewritten to use `error_handler=` — pattern still valid, mechanism is now native |
| §66 (Failure pipeline) | ✅ Per-node timeouts added as Step 0, before retries fire |
| §67 (Fallback chain) | ✅ `NodeTimeoutError` triggers the chain — fallback fires on timeout, not only on exceptions |
| §52 / §52a (Checkpointer + Store) | ✅ `DeltaChannel` noted as a future optimisation, §87 item 12 |

### Gap Register Note
No new gap number — the §49 and §66 closures are **updated to native primitives**. This is the clearest case in the document of the anti-drift discipline paying for itself: three patterns that would have been hand-written are now framework-provided, and the only reason we know is that the version check happened before implementation rather than after.

**Version requirement: LangGraph ≥ 1.2.6.** The upgrade target is **1.2.10** (latest on PyPI as of August 2026) — 1.2.6+ is also required for the subgraph `checkpoint_ns` fix (§23). The codebase is currently pinned at 1.1.10, so this upgrade is a prerequisite for both this section and the subgraph architecture. During the upgrade, sweep for imports from `langgraph.prebuilt` — deprecated in 1.0 → 1.1, with functionality moved to `langchain.agents` (§50).

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

### Ratified Implementation — LangGraph 1.2 Native `error_handler=`

**No custom Saga orchestrator is built.** LangGraph 1.2 provides a node-level `error_handler=` parameter, which is the mechanical hook compensating logic attaches to (§79). Hand-rolling a saga coordinator on top of that would be redundant machinery.

```python
def define_error_recovery(error: NodeError, state: PhaseState) -> Command:
    """Compensating action for define_executor — undoes external writes."""
    delete_or_flag_stale_in_case_index(state["case_id"], "define")
    return Command(
        update={"extraction_error": str(error), "extraction_incomplete": True},
        goto="degraded_coaching_response",
    )


builder.add_node(
    "define_executor",
    define_executor_fn,
    error_handler=define_error_recovery,
    timeout=TimeoutPolicy(run_timeout=45),     # §79 — bounds the failure window
)
```

**Every phase executor node that writes to an external system — Blob, case index, evidence index — gets an `error_handler=` with the corresponding compensation logic.** Without it, a reopened gate leaves a stale, now-incorrect baseline value sitting silently in `improve_case_index`, corrupting the long-term memory that cross-case retrieval (§37) depends on.

### Connection to Gate Reopening — §38's Re-Approval Cascade

Saga and the mid-phase contradiction cascade are **interdependent, not independent**. When a Belt changes a gate-approved value and §38's re-approval cascade fires, the affected phase's compensating action must run to clean up stale values in external systems. A cascade that marks phases provisional but leaves the published values in place is worse than no cascade — the state and the index now disagree, silently.

### Status

**In refactor scope, not deferred.** This was originally listed as lower priority than Gaps 1–23. That ranking assumed the system would not be production-grade. It is being built to be production-grade, and correctness under gate reopening is a production requirement, not a refinement.

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
Define   → writes artifacts to store + case index    — error_handler required
Measure  → writes baseline + case index update       — error_handler required
Analyse  → writes root cause                          — error_handler required
Improve  → writes hypothesis + pilot results          — error_handler required
Control  → writes final control plan                  — error_handler required
```

Note the list no longer mentions "future MCP-connected systems" — there are none (§39). The external systems are Azure Blob, `improve_case_index`, and `improve_evidence_index`, and that set is closed by design.

### Gap Register
**Gap 29 — in refactor scope.** Compensating actions implemented via LangGraph 1.2 native `error_handler=` on every node with external side effects. Its prerequisite (confirming `error_handler=` mechanics in the current LangGraph version) is satisfied — see §79. Correctness under gate reopening (§2, §38) and time-travel debugging (§3) both depend on it.

*Cross-references: §3 (time travel does not undo side effects), §38 (the re-approval cascade this supports), §66 (where compensation sits in the six-step failure pipeline), §79 (the native primitive), §64 (structured error schema for what gets logged).*

---

## 66. Circuit Breaker, Context Recovery, and Safe Reopen — Completing the Failure Pipeline

*Source: Edureka Course 4 Module 2, "Retry Strategies, Back-off Techniques, and Failure Handling" transcript. Three concepts from the six-step failure pipeline not previously formally captured.*

> **Status: ratified. The six-step failure pipeline is the complete reliability architecture for the refactored Agent Improve — with a Step 0 added.**
>
> ```
> Step 0. Per-node timeout        TimeoutPolicy(run_timeout=45)     §79
> Step 1. Error classification    transient vs permanent            §64 schema
> Step 2. Context recovery        save partial results, resume
> Step 3. Circuit breaker         3 failures / 30s → OPEN, 60s reset
> Step 4. Safe reopen             one probe in HALF-OPEN
> Step 5. Graceful degradation    four-level fallback chain         §67
> Step 6. Smart fallbacks         alternative models, cache, degraded mode
> ```
>
> **Step 0 is new.** LangGraph 1.2's per-node `TimeoutPolicy` bounds the wall clock at 45 seconds, and `NodeTimeoutError` is what triggers the fallback chain — the timeout fires *before* the Belt notices the delay, rather than after retries have already burned the budget.
>
> **Backoff discipline (ratified):** jittered backoff for shared resources, because multiple subagents may retry simultaneously and lock-step retries create their own thundering herd; exponential backoff for managed services like Azure OpenAI, which rate-limit predictably.

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
    """Wraps any external call — Azure OpenAI, Azure AI Search, Azure Blob."""

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
                "artifacts": partial_results,
                "extraction_error": str(e),
                "extraction_incomplete": True,
                "last_successful_field": field
            }

    return {"artifacts": partial_results, "extraction_incomplete": False}
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

For AgentLean this matters specifically for **Azure OpenAI and Azure AI Search** — both are critical-path for coaching turns, and they are the two breakers §66 defines. A failed circuit probe should not silently succeed and immediately flood the recovering service with full traffic.

*An earlier revision named "the AgentLean MCP server" here. There is no such component — MCP is architecturally excluded (§39), not deferred.*

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
| Multiple agents sharing the same resource (Azure Cache for Redis) | Jittered | Randomises retry timing across agents, prevents synchronized storm |
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

Level 3: Azure Cache for Redis (session-scoped response cache)
         jittered_backoff      ← shared resource, multiple subagents may hit simultaneously
         ↓ if cache miss or unavailable

Level 4: Degraded mode         ← always succeeds, never a hard failure to the Belt
```

*Level 3 was originally "AgentLean MCP knowledge cache." Replaced by Azure Cache for Redis (§67) — the cache-key, TTL, and invalidation principles from §65 carry over; the transport does not.*

**Degraded mode for Agent Improve must never be a blank error.** The Belt is mid-project and needs continuity. The correct degraded response:

```python
def degraded_mode_response(state: PhaseState) -> str:
    phase    = state["phase_context"]
    captured = state["artifacts"]
    missing  = get_missing_fields(state)

    return (
        f"I'm experiencing a temporary connection issue. "
        f"Based on what we've captured so far in the {phase} phase "
        f"({len(captured)} of {len(captured) + len(missing)} fields complete), "
        f"I'd suggest we pause here and continue once the system recovers. "
        f"Your progress is saved and nothing has been lost."
    )
```

This is better than silence or a crash in every respect — the Belt knows what happened, knows their work is safe, and knows how to continue. **The message uses actual state rather than a generic error**, which maintains trust even during a degraded experience. That is the point worth carrying forward: degraded mode is still a coaching interaction, not an error page.

### Gap Register Note
No new gap number — jitter and per-level backoff selection are implementation details of the ratified fallback chain. The chain above is the architecture carry-forward for ARCHITECTURE.md v2.2's reliability section.

---

## 67. Self-Healing Fallback Chain — Complete Reference Implementation

*Source: Edureka Course 4 Module 2 self-healing demonstration, complete code across all screenshots. Confirms and extends Sections 51 and 66 with a single runnable reference.*

> **Status: ratified in full, including the cache tier.**
>
> **The four-level fallback chain:**
> ```
> Level 1: Azure OpenAI gpt-4o (operational-premium)
>          exponential_backoff — managed service
>          ↓ if rate-limited or unavailable
>
> Level 2: Azure OpenAI gpt-4o-mini (operational-model)
>          exponential_backoff — same managed tier
>          ↓ if also unavailable
>
> Level 3: Response cache (Azure Cache for Redis)
>          jittered_backoff — shared resource
>          ↓ if cache miss or unavailable
>
> Level 4: Degraded mode — always succeeds, never crashes
> ```
>
> **Level 3 cache infrastructure is IN REFACTOR SCOPE, not deferred.** The original §66/§67 referenced "the MCP knowledge cache from Section 65," which does not exist under §39. It is replaced by **Azure Cache for Redis**, storing recent retrieval results keyed by query hash + phase, and recent coaching responses for similar questions. **Session-scoped, not global** — different projects have different context, and a cached answer from another Belt's project is worse than no answer.
>
> **⚠️ New infrastructure component.** Azure Cache for Redis is not in the current `valuesims-*` / `agentlean-*` setup. Add it to the infrastructure provisioning plan before this level can be implemented.
>
> **Three-state circuit breaker, not two.** Use the §66 version. Agent Improve is a long-running service and must recover without a restart.

### Geographic Redundancy — the chain's single-region dependency (v2.2)

**The four-level chain above is the v2.1 implementation target and does not
change.** This subsection records a compliance limitation in it and the
ratified v2.2 replacement, so the constraint is not rediscovered at launch.

**The finding.** Levels 1, 2 and 3 are all provisioned in **Azure West Europe
(Frankfurt)**. They are three different services, but one region. A Frankfurt
regional outage does not degrade the chain a level at a time — it collapses
Levels 1–3 simultaneously and drops straight to Level 4 degraded mode, with no
intermediate recovery path. The chain reads as defence in depth and is, against
*service* failure; against *regional* failure it is a single point of failure
wearing four hats.

**Why this matters beyond availability.** DORA's ICT resilience obligations
require geographic redundancy for continuity of critical functions. A
single-region chain is non-compliant for any regulated-entity deployment, which
makes this a launch blocker for that market rather than a robustness
nice-to-have. EU AI Act data-governance provisions are also in scope, which is
why the secondary region must be inside the EU.

**Ratified v2.2 replacement — five levels, two regions:**

```
Level 1: Azure OpenAI gpt-4o      — West Europe (Frankfurt) — primary
         ↓ timeout / rate-limit / regional outage
Level 2: Azure OpenAI gpt-4o      — secondary EU region (Sweden Central candidate)
         ↓ if also unavailable
Level 3: Azure OpenAI gpt-4o-mini — secondary EU region
         ↓ if also unavailable
Level 4: Azure Cache for Redis    — session-scoped response cache
         ↓ cache miss or unavailable
Level 5: Degraded mode            — always succeeds, never crashes
```

The insertion is Level 2: the same model in a different region, before
accepting a quality drop to gpt-4o-mini. A regional outage should cost latency,
not coaching quality.

**Open decision for v2.2 — the secondary region.** Sweden Central is the
candidate: EU data residency satisfied, low latency from Frankfurt, Azure
OpenAI available. It needs quota provisioned in that region under the same
subscription. Once provisioned this is a connection-string change, not a model
or code change.

**TPM exhaustion and regional outage are different failures, and v2.1 already
handles the first correctly.** A 429 from Azure OpenAI is classified transient,
exponential backoff fires, and the chain activates as designed — that path is
sound and needs no amendment. What the amendment addresses is the case where
Frankfurt endpoints are unreachable outright, or where 429s persist past backoff
tolerance so that "wait and retry" has no regional escape hatch to fall back to.

**Deferred to §87 item 16**, promoted before production launch with real Belts.
Not a v2.1 blocker: the refactor establishes the coaching loop, middleware
stack, gate validation and chain structure against a single region, and adding
a second region mid-refactor buys nothing testable.

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
| AgentLean fit | Dev and testing only | **Ratified** — the FastAPI service is long-running |

**Use the three-state version from §66.** Agent Improve runs as a long-lived FastAPI service; a circuit that stays open until process restart would turn a 30-second Azure OpenAI blip into an outage lasting until someone notices and redeploys.

---

### The Structured Audit Log — The Genuinely New Addition

Every service attempt — success or failure — is appended to the log. **Ratified as dicts, not tuples** (§18, §68): self-documenting, inspectable, and consistent with every other `step_log` entry.

```python
# RATIFIED — dict entries
step_log.append({"service": "gpt-4o", "attempt": 2, "status": "failed",
                 "reason": "timeout after 45s", "timestamp": "..."})

step_log.append({"service": "gpt-4o-mini", "attempt": 1, "status": "success",
                 "timestamp": "..."})

step_log.append({"service": "degraded", "attempt": 1, "status": "fallback",
                 "timestamp": "..."})

# The course's tuple form — positional, opaque at the read site
self.log.append((name, attempt + 1, "failed", str(e)))
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
   → three-state (CLOSED/OPEN/HALF-OPEN) — ratified
   → 3 failures in 30s trips open; 60s reset timeout; one probe

3. Structured Fallback Chain (Sections 66, 67)
   → Level 0: per-node TimeoutPolicy(run_timeout=45)   ← §79, fires first
   → Level 1: gpt-4o primary
   → Level 2: gpt-4o-mini backup
   → Level 3: Azure Cache for Redis (session-scoped)
   → Level 4: degraded mode response (never a hard failure)

4. Audit Log (Sections 18, 64, 67)
   → every attempt logged as a DICT: service, attempt, status, reason, timestamp
   → written to step_log; shape from Section 64's error schema
   → enables post-hoc analysis of which service served each coaching turn
```

### Gap Register Note
No new gap number — this section completes the self-healing implementation reference. The audit-log pattern is adopted with dict entries (not tuples) and connected to `step_log` (§18).

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

**Two separate circuit breakers — LLM layer and retrieval layer:**

```python
# Circuit Breaker 1 — wraps Azure OpenAI calls
llm_circuit_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=60)
# 3 consecutive 503s → OPEN → stop trying the primary model
# coaching turn fails → trigger Level 2 fallback

# Circuit Breaker 2 — wraps Azure AI Search calls (the rag_lookup_* tools)
search_circuit_breaker = CircuitBreaker(failure_threshold=3, reset_timeout=60)
# 3 consecutive search failures → OPEN → skip knowledge retrieval
# coaching continues WITHOUT RAG grounding
# quality degradation, NOT availability failure — the Belt still gets a response
```

*The second breaker originally wrapped the AgentLean MCP server. There is none (§39); it wraps Azure AI Search, which is where retrieval actually happens.*

These are independent — a search outage does not affect LLM availability and must not trigger the LLM fallback chain:

```
Search Circuit Breaker OPEN:
  → coaching turn still happens
  → LLM reasons without eBook grounding
  → Belt gets a response, just less well-grounded
  → step_log entry: {"service": "azure-search", "status": "circuit_open",
                     "reason": "knowledge_retrieval_skipped"}
  → this is a QUALITY degradation, not a SYSTEM failure
  → the coach's system prompt must acknowledge the reduced grounding rather
    than presenting ungrounded methodology as if it were retrieved (§29)

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

| Failure Pattern | Agent Improve Risk | Ratified Mitigation |
|---|---|---|
| State drift | Belt's situation changes but old fields persist | Nine-step gate review + field correction (§2); mid-phase contradiction auto-flag with re-approval cascade (§38) |
| Context window overflow | Multi-week projects accumulate long histories | `SummarizationMiddleware` — trigger at 100k tokens, keep last 20 messages (§36); captured fields live in `artifacts` and the store, never in `messages[]`, so compression cannot reach them |
| Stale plan | Phase fields defined in Define may be wrong by Analyse | HITL edit loop (§2) plus the cross-phase consistency check in the policy advisory (§38) |
| Orphaned checkpoints | Checkpoint volume grows across a multi-week project | Not yet a problem at current session lengths. `DeltaChannel` (§79) is the compression mechanism, deferred to §87 item 12 until sessions exceed ~200 turns. |
| Partial task completion | Node fails after writing to Blob or an index, leaving external state inconsistent | Saga compensating actions via LangGraph's native `error_handler=` (§49, §79); per-node `TimeoutPolicy(run_timeout=45)` bounds how long a partial state can hang |
| Re-planning loops | Coach keeps asking the same questions | `RemainingSteps` caps tool calls per turn, with `GraphRecursionError` handling as a backstop (§34); shared cap of 3 attempts across the four validation layers (§68); Level 2 completeness check gates the field-index advance (§5) |

---

# PART 6 — ORCHESTRATION AND DATA FLOW

*How the five phases connect: the two state schemas, the store-mediated handoff between them, and the persistence split underneath.*

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

*For the vocabulary used here, see the **Terminology Reference**. This is the parent-level half of the state design; §18 is the phase-level half.*

**1. Typed State Schema — `SupervisorState`**

The original draft of this schema mixed orchestration state with cross-phase artifacts. Under the Checkpointer + BaseStore split (§52, §52a), artifacts move to the store and `SupervisorState` shrinks to **orchestration state only**. Field names are aligned with §18 so the two schemas read as a pair.

```python
class SupervisorState(TypedDict):
    messages:        Annotated[list[BaseMessage], operator.add]
    history:         Annotated[list[str], operator.add]    # node execution order
    case_id:         str                                    # canonical identifier
    phase_index:     int                                    # 0=Define … 4=Control
    current_phase:   str
    gate_passed:     dict[str, bool]                        # {"define": True, …}
    final_output:    Optional[dict]                         # set on Control gate approval
```

**What changed and why:**

| Original field | Fate | Reason |
|---|---|---|
| `captured_fields` | **Removed** — moved to the store | Cross-phase artifacts do not belong in parent state; subgraph state does not propagate to the parent anyway (§23). The name itself is also retired — see "One name for one concept" below |
| `gate_documents` | **Removed** — moved to the store | Same reason; also keeps parent state small enough to checkpoint cheaply. The store namespace of the same name was later retired too, as a duplicate of `artifacts` |
| `step_log` | **Removed** — moved to the store, and to `PhaseState` for in-phase entries | Append-only cross-phase audit trail; §18 owns the per-phase slice |
| `step_index` | **Renamed** → `phase_index` | Disambiguates from `field_index`, the field-level pointer in §18 |
| `dmaic_plan` | **Removed** — redundant | DMAIC order is fixed and lives in static edges (§44). The project's substantive plan is Define's gate document in the store, plus `improve_case_index` metadata |
| `project_context` | **Added, then removed** — redundant | Inherited from the course lab's `task: str` (§18). Had no writer anywhere, and its one reader ran before the phase that was meant to set it. Context is now composed at the boundary by each input mapper — see below |
| `project_id` | **Renamed** → `case_id` | Docs said `project_id`; all code and both Azure AI Search indexes said `case_id`. See below |
| — | **Added** `gate_passed` | Which phases are approved. This is what the deterministic Level 1 gate-checker actually routes on (§44), and it was referenced throughout this document long before it was declared here |
| `gate_passed` | **Retyped** `list[str]` → `dict[str, bool]` | `gate_passed["measure"]` is a direct lookup, and the re-approval cascade (§38) sets a phase back to `False` rather than removing it from a list — a removal that has to be conditional on the phase being present |
| `final_output` | **Retyped** `str` → `Optional[dict]` | The Control gate document is structured data, the same rule that made `PhaseState.final` a dict (§18) |

**Seven fields, and an eighth needs an amendment.** The pattern across
2.2.7, 2.2.8 and 2.2.9 is that parent state accumulates fields nobody
writes or nobody reads, and the check that catches them is cheap: for
every field, name the node that writes it and the node that reads it.

#### `case_id`, not `project_id` — documents move, code does not

**The identifier is `case_id` across the entire project**, and this was
never a design question. It was governance documents disagreeing with
everything else:

| Already said `case_id` | Said `project_id` |
|---|---|
| `improve_case_index.case_id`, `improve_evidence_index.case_id` (§60) | This document |
| `cases/case_{id}.json`, `registry.json`, `uploads/{case_id}/{file}` | CLAUDE.md |
| `CaseDocument`, `PhaseRecord`, `RegistryEntry` | ARCHITECTURE.md |
| Every `@tool` signature taking a case scope | |

One find-and-replace across three markdown files, against a migration of
the code, two live Azure AI Search indexes, and the blob layout. The
cost asymmetry decides it, and the docs were the ones that were wrong.

`case_id` is also the graph's `thread_id` and the store's namespace
segment — one identifier, one name, used by both persistence systems.

#### `current_phase` and `phase_index` — derived, and kept anyway

Both are computable from `gate_passed`, which by the test that removed
the four fields above makes them redundant. **They are kept as a
documented exemption**, and it is worth being explicit about why the
exemption is safe here and was not for `open_items`.

`state["current_phase"]` is read in dozens of places — every input
mapper, the state-injection middleware, every log line, the case index
writer. Deriving it at each site adds noise to code that is about
coaching. Both fields are scalar and cannot grow.

**The difference from the removed fields is the number of write sites.**
`current_phase`, `phase_index` and `gate_passed` are advanced together
by the output mapper at gate approval, and nowhere else — one write, all
three consistent by construction. `open_items` would have needed
refreshing after every field capture, every validation failure and every
Belt edit, which is many sites and therefore many chances to miss one.
Redundancy is not the failure mode; **redundancy plus a scattered write
surface** is.

#### One name for one concept — `artifacts`

Three names had been circulating for the same thing:

| Name | Where it came from | Status |
|---|---|---|
| `artifacts` | `PhaseState` field, store namespace, gate document content | **Canonical** |
| `captured_fields` | Prose in EDUCATIONAL.md and these documents | **Retired** — replace with `artifacts` in prose |
| `phase_inputs` | v1 code field name | **Retired** — replaced during the refactor |

`PhaseState.artifacts` holds the fields the Belt has produced in this
phase. The cost of three names is not aesthetic: a reader who meets all
three across a governance document reasonably concludes there are three
things, and then asks how they stay in sync.

**A later revision removed two more fields — `key_decisions` and `open_items` — that an earlier version of this section had added.** They were introduced by §36's context-compression decision, on reasoning that was sound but arrived at the wrong conclusion. The reasoning: `SummarizationMiddleware` compresses `messages[]`, so anything that must survive compression has to live in typed state. True. The error was assuming that required *new* fields.

It did not. A decision the Belt commits already arrives via `CoachingResponse.fields_captured`, is approved at a gate, and lands in `PhaseState.artifacts` and then the store — three locations, none of them `messages[]`. The compression guarantee was already satisfied. `key_decisions` added a parallel copy of facts that were durable anyway, and a parallel copy is a second source of truth that can disagree with the first.

`open_items` failed the same way against a different mechanism. Outstanding work is a *derived* property: `check_gate_status()` reports which required fields are unpopulated, and the four-layer validation stack (§68) is what surfaces blockers. A stored list is a second answer to "is this gate ready?" capable of contradicting `DMAICGateValidator`. A derived one is not capable of it.

**A later audit removed a fourth field — `project_context` — and it is the cleanest illustration of the rule.** The audit asked three questions of it: what is it, who reads it, who writes it.

It was `project_context: str`, and **no document anywhere states what goes in it.** The only characterisation was the schema comment, "never changes after Define."

**One reader:** `define_input_mapper`, which sets `phase_context` from it. That is the entire consumer list. The Level 1 gate-checker does not read it — there is no LLM at Level 1 to consume prose, and routing is `gate_passed` plus static edges (§44). Every other phase already built `phase_context` from the store: Measure reads Define's artifacts, and so on down the chain.

**No writer.** Not a node, not a mapper, not a middleware, in any document or any code path. `define_output_mapper` returns orchestration values only, by rule.

Those three answers do not compose. The field was declared to be written *after* Define and read *before* it, so as specified its single read would return an empty string every time. That contradiction survived several revisions because nothing in the design depended on the value — which is the tell.

Its provenance explains the rest. The AgentLean Field Mapping in §18 maps the course lab's `task: str` onto Agent Improve, and `project_context` is what `task` became. It is an **inherited field, not a designed one** — the same lineage as `step_index`, which was renamed rather than kept, and `dmaic_plan`, which was removed. In the lab, `task` is the one-line instruction a single-level planner decomposes. Agent Improve has no such instruction: the work is fixed by DMAIC, and the project's substance is the Belt's captured fields.

**What covers the use case.** `phase_context` is real and still exists on `PhaseState` — what changed is where it comes from. Each input mapper now composes it from the store: Define from the case record loaded at session start, every later phase from the prior phase's artifacts. The rule is uniform, and an input mapper's only dependency is `BaseStore`. Underneath, nothing was lost — the substance (problem, goal, scope, business case) is Define's gate document in the store, the framing (title, department, belt level, target date) is the case record and the `improve_case_index` row (§60), and `before_model` injection (§38) already places captured fields and prior gate documents at the top of every coach prompt. The v1 codebase had in fact been doing this all along: `VISION_EXTRACT_PROMPT` composes a literal "Project context:" block from title, department, phase and Define's `what` at the point of use, storing nothing.

**The general rule this leaves behind:** state carries what cannot be recomputed. Anything derivable from captured fields, gate documents, or the validation stack is derived at the moment it is needed, not stored and refreshed. `project_context` adds a corollary — **a field with no writer is not state, it is a comment** — and the check that catches it is cheap: for every field on a schema, name the node that writes it and the node that reads it. If either list is empty, or the two are ordered impossibly, the field is not carrying anything. See §68 for the validation stack, §52a for the store, and CLAUDE.md §10.1 for the binding form of the schema.

**2. Phase Routing — Static Edges, Not a Conditional Router**

The original specification used a conditional router keyed on `current_phase`. **§44 corrects this**: DMAIC phase order is fixed, so the transitions are static edges and the "planner" is a deterministic gate-checker.

```python
# Ratified — static edges between phase subgraphs
builder.add_edge("define",  "measure")
builder.add_edge("measure", "analyse")
builder.add_edge("analyse", "improve")
builder.add_edge("improve", "control")
builder.add_edge("control", END)
```

Apply the decision test from §44: *"Could this transition vary at runtime?"* → dynamic. *"Always exactly once, in this order?"* → static. DMAIC phase sequence is the second case. `Command`-based dynamic routing is reserved for **inside** phase subgraphs, where step order genuinely is data-dependent.

**Critical rule (§44):** never mix static edges and `Command` routing from the same node. Both paths execute, silently.

**3. Checkpointing**
```python
# During the refactor
from core.checkpointer import AzureBlobCheckpointSaver
checkpointer = AzureBlobCheckpointSaver(blob_client)

# Post-refactor, pre-production
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string(os.getenv("PG_CONN"))

# Parent graph ONLY — phase subgraphs compile without a checkpointer
graph = workflow.compile(checkpointer=checkpointer, store=store)
await graph.ainvoke(
    input,
    config={"recursion_limit": 50,                    # §34 — backstop, not the hop cap
            "configurable": {"thread_id": case_id}},  # one thread_id per case
)
```

*`InMemorySaver` appears nowhere in the ratified design — not even for development. It was in the original draft as the dev-tier option; the phased Blob → PostgreSQL decision (§1) replaces it.*

#### 3a. Disconnect policy — what a dropped client commits

**Scope note.** This is part of step 3, not a new step. Wiring `thread_id`
through `graph.ainvoke` is what makes checkpoints actually write; the moment
they do, a question arrives that did not exist while `routes.py` dispatched
nodes manually and nothing persisted: **when a Belt closes the tab
mid-coaching-turn, what has been committed?**

**The finding that forces the decision** (Ranjan Kumar, *"FastAPI + LangGraph:
What a Client Disconnect Commits"*, measured 2026-08-04): once checkpoints are
live, **the FastAPI handler's control-flow shape — not the checkpointer —
decides what survives a disconnect.** A handler that hands the graph run to a
bare `asyncio.create_task` keeps executing after the client is gone, and the
run checkpoints every node it completes. The Belt sees nothing; the checkpoint
says the turn happened.

**Ratified policy for Agent Improve: ABANDON, not COMPLETE.**

A silently-completed gate approval that the Belt never saw is unacceptable in
a system whose entire premise is that the Belt approves what gets committed
(§2, step 7). COMPLETE is defensible for idempotent background work; it is not
defensible for a nine-step HITL gate. If the Belt is gone, the turn stops.

**Five requirements, all part of step 3:**

| # | Requirement | Why |
|---|---|---|
| 1 | **Deliberate handler shape** — either inline `await` streaming, or an explicit ABANDON policy calling `t.cancel()` in `gen()`'s `finally`. Never a bare `asyncio.create_task` with no disconnect handling | This is the decision point. A handler that has not chosen has chosen COMPLETE by accident |
| 2 | **Deterministic `step_log` keys** — `f"{phase}:{turn_count}:{step_name}"`, never a raw timestamp as identity (§18) | An abandoned-then-retried turn re-executes the same logical step. Timestamp keys record that as two events and inflate the audit trail |
| 3 | **Azure Blob lease as the per-thread concurrency guard** | Two tabs open on one `case_id` means two writers on one `thread_id`. Postgres advisory locks are the natural mechanism and are not available until the §1 migration, so the lease carries it in the interim — and the Blob checkpointer's known lack of concurrency testing (§1) is exactly this exposure |
| 4 | **A reconciliation sweep for abandoned threads that excludes `interrupt()`-paused threads** | A thread paused at a gate is indistinguishable from an abandoned one by "no recent activity" alone. A sweep that misses this cleans up Belts who are simply thinking about their gate review overnight |
| 5 | **`thread_id` / `case_id` derived from the authenticated session, never client-supplied** | A client-supplied `thread_id` lets any caller resume any Belt's coaching session. `thread_id` is `case_id` (§17) and `case_id` is the tenancy boundary |

**`gate_apply_node`'s store write needs no change.** It is already idempotent
by key — `store.put(("projects", case_id, "artifacts"), phase, doc)` overwrites
rather than appends, so replaying it is safe. The exposure is in `step_log`
(requirement 2) and in concurrent writers (requirement 3), not here.

**4. Human-in-the-Loop**
```python
graph = workflow.compile(
    checkpointer=checkpointer,
    store=store,
    interrupt_before=["gate_review_node"],   # §44 two-node pattern
)
# FastAPI endpoints:
# GET  /gate/review   → returns validated fields for Belt review
# POST /gate/approve  → accepts corrections + approval,
#                       resumes with Command(resume=corrections)
```
See §2 for the nine steps this wiring implements.

**5. Supervisor / Worker Architecture**
```
Supervisor: no tools. Reads gate_passed deterministically, advances phase_index,
            routes to the next phase subgraph via a static edge.
Workers:    Define, Measure, Analyse, Improve, Control — each a subgraph with its
            own PhaseState (§18) and its own phase-specific tool subset (§39).
```
The relationship is not flat supervisor/worker — it is a Planner-Executor pair applied recursively (§20). See the Terminology Reference for the level table.

**6. Observability**
```python
# Time travel — subject to the side-effect caveat in §3
await graph.ainvoke(None, config={"configurable": {
    "thread_id": "IMPR-2026-E9D",
    "checkpoint_id": "before_gate_measure",
}})

# Snapshot inspection — orchestration state only
for state in graph.get_state_history(config):
    print(state.values["current_phase"], state.values["phase_index"])

# Cross-phase artifact inspection uses the store, NOT checkpoint history
store.get(("projects", case_id, "artifacts"), "define")
```
The original example printed `state.values["captured_fields"]`. That field no longer exists on `SupervisorState` — the phase's gate document is read from the store (§52a).

---

## 18. Lab Code — PhaseState Schema

*Source: Edureka course lab — Creating a Planner Node with a Structured Executor. **Renamed from `PlannerState` to `PhaseState`**: this is the state that runs *inside* a phase subgraph, and "PhaseState" says so. See the Terminology Reference.*

### Key Imports
```python
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt      # HITL primitives
from langchain_core.messages import BaseMessage
import operator
from typing import Annotated, Any
```

*The lab imported `InMemorySaver` here. Phase subgraphs compile **without** a checkpointer (§23, §44) — the parent's saver handles them via `checkpoint_ns` — so no checkpointer import belongs in a subgraph module.*

### Complete `PhaseState` Schema
```python
class PhaseState(TypedDict):
    # ── conversation plumbing (3) ─────────────────────────────────
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]  # node execution order
    phase_context:      str              # composed at the boundary — see below

    # ── the fourteen content fields ───────────────────────────────
    coaching_plan:      Optional[CoachingPlan]   # ONE plan per planner turn — §71-C
    field_index:        int              # current field within the phase
    draft:              dict[str, Any]   # extracted fields this turn
    artifacts:          dict[str, Any]   # accumulated fields for the phase
    step_log:           Annotated[list[dict[str, Any]], operator.add]
    belt_edits:         dict[str, Any]   # Belt corrections at the gate
    turn_count:         int              # coaching turns before the gate fires
    final:              dict[str, Any]   # approved gate document
    gate_attempts:      int              # validation retry counter, cap 3
    validator_feedback: list[dict]       # accumulated per-attempt feedback
    citations:          list[dict]       # sources the coach cited this phase
    uploads:            list[dict]       # files the Belt uploaded this phase
    hop_results:        list[str]        # ordered hop answers — [] outside planned multi-hop
    synthesis_output:   Optional[dict]   # SynthesisOutput — None for single-hop turns
```

**Seventeen fields — fourteen content fields plus three plumbing fields.**
The state design audit governed the original twelve; `messages`, `history`
and `phase_context` were not in its scope. `messages` is what `create_agent`
runs its loop on, `history` is the node execution trail, and
`phase_context` is composed at the boundary by the input mapper.

**`hop_results` and `synthesis_output` were added by the §71 compliance audit
(2026-08-11)**, and `coaching_plan` was retyped in the same pass. All three
are specified in §71: `hop_results` (§71-E) makes the planned multi-hop chain
visible in LangSmith and recoverable from a checkpoint, which a local Python
dict inside the node could not do; `synthesis_output` (§71-D) holds the
dedicated synthesis call's result so the coach call reads it from state rather
than from a local variable; `coaching_plan` (§71-C) moves from a plain dict to
the typed `CoachingPlan` Pydantic model produced via `with_structured_output`,
matching the typed-boundary discipline every other boundary in this
architecture follows (§82). `dict[str, Any]` is acceptable as an interim
annotation inside the `TypedDict`; the typed form is preferred.

**Both new fields are Analyse-shaped but not Analyse-restricted.** They are
`[]` and `None` on every single-hop turn in every phase — `CoachingPlan.
retrieval_strategy` may select `multi_hop` in any phase, so the fields are
declared once on `PhaseState` rather than on an Analyse-only variant.

**What changed from the lab's `PlannerState`:**

| Lab field | Ratified | Reason |
|---|---|---|
| `PlannerState` | `PhaseState` | Names what it actually is — the state inside a phase subgraph |
| `counter` | `turn_count` | The lab name says nothing; this counts coaching turns before the gate fires |
| `step_index` | `field_index` | Disambiguates from `phase_index` in `SupervisorState` (§17) — this one points at a field *within* a phase |
| `plan` | `coaching_plan`, retyped `list[dict]` → `dict[str, Any]` → **`Optional[CoachingPlan]`** | One plan per planner turn, overwritten each time. Retyped again by §71-C to a Pydantic model. See "Why the plan is a dict" below |
| `task: str` | `phase_context: str` | Same role, phase-scoped |
| `final_output` | `final`, retyped `str` → **`dict[str, Any]`** | The gate document is structured data. `final: str` contradicted the dict-not-str rule the same schema enforces on `draft` |
| — | **Added** `draft: dict[str, Any]` | Structured extraction result for the current turn. Typed, not a string — see §21 on why prose handoffs are the Gap 10 anti-pattern. |
| — | **Added** `feedback: dict[str, Any]`, later renamed **`belt_edits`** | Structured Belt corrections at the gate. Renamed once `validator_feedback` arrived — see below |
| — | **Added** `gate_attempts: int` | The retry counter for the four-layer stack (§68). Its absence reintroduced a v1 bug — see below |
| — | **Added** `validator_feedback: list[dict]` | Accumulated per-attempt validation feedback. This is what makes the shared cap of 3 defensible |
| — | **Added** `citations: list[dict]` | Sources the coach cited, for the gate document and §13's citation requirement |
| — | **Added** `uploads: list[dict]` | Files the Belt uploaded — the record of what external evidence the phase had (§39) |
| — | **Added** `hop_results: list[str]` | Ordered hop answers from the planned multi-hop chain. In a local dict they were invisible to LangSmith and lost on checkpoint restore (§71-E) |
| — | **Added** `synthesis_output: Optional[dict]` | The dedicated synthesis call's `SynthesisOutput`. The coach call reads it from state, not from a local variable (§71-D) |
| `artifacts`, `step_log` | Unchanged in name; `step_log` gains an append-only reducer | See below |

### `gate_attempts` — the field whose absence recreated a v1 bug

**`gate_attempts` was mandated in two places and declared in none.**
CLAUDE.md §1.7 and §3.5 both state it must be in checkpointed state and
never in route scope; the schema did not have it. A validation loop with
no counter cannot enforce a cap, which is precisely the v1 defect those
rules were written to prevent: v1 held the equivalent counter in route
scope, so every request rebuilt it at `0`, the cap never fired, and the
loop reported attempt 1 indefinitely.

**It is per phase, not per supervisor.** Each phase runs its own
validation loop with its own budget of 3. A supervisor-level counter
would let a difficult Measure phase consume the retries Analyse needs,
and the two phases have nothing to do with each other.

Incremented on each failed attempt, reset to `0` when the gate passes,
routes to escalation (§2) at `>= 3`.

### `validator_feedback` vs `belt_edits` — two kinds of feedback

The original `feedback` field carried "Belt corrections at the gate."
Then §68's accumulated-feedback requirement needed somewhere to live,
and the obvious move — reuse `feedback` — is wrong.

**They are different actors at different moments in the nine-step gate
(§2):**

| Field | Written at | By | Read by |
|---|---|---|---|
| `validator_feedback` | Step 2 | The four validation layers | The coach, on retry |
| `belt_edits` | Step 5 | The Belt | `gate_apply_node`, at step 6–7 |

Conflating them would have the coach reading the Belt's corrections as
validation failures — the Belt fixing a value would look to the coach
like the system rejecting it. `feedback` was renamed `belt_edits` so the
name says which of the two it is.

**Accumulation is the whole point of `validator_feedback`.** Each failed
attempt appends:

```python
{"attempt": 1, "layer": "grader",
 "criteria_failed": ["root_cause_validation"],
 "feedback": "does not reference statistical evidence",
 "timestamp": "2026-08-03T11:04:19Z"}
```

The coach reads the full list on retry; the list resets to `[]` when the
gate passes. §68's argument for the shared cap of 3 rests entirely on
each attempt being better informed than the last — a cap on retries that
carry no memory is just a cap on repetition, and this field is what
carries the memory.

### `citations` and `uploads` — what the gate document could not show

The coach cites BB eBook pages; the Belt uploads spreadsheets. Neither
was tracked, so the gate document could not answer what the phase was
grounded in — and §13 requires citation transparency down to
`source_file` and `page_number`.

```python
citations = [{"source": "improve_knowledge_index", "page": 47,
              "content_summary": "GR&R acceptance thresholds", "turn": 5}]

uploads   = [{"filename": "defect_data_q2.xlsx", "case_id": "IMPR-2026-E9D",
              "upload_turn": 3, "purpose": "baseline data"}]
```

`uploads` carries more weight than it looks. Per §39 and §63,
`improve_evidence_index` is the **only** channel through which external
data enters AgentLean — so the upload list is the complete record of
what real-world evidence the phase had to work with. A phase with an
empty `uploads` list reached its conclusions from the Belt's typed
statements alone, and a reviewer should be able to see that.

Both are written into the gate document at approval.

### Why the plan is a dict, not a list

`coaching_plan` appeared as `dict` in some places and `list[dict]` in
others. **It is a single `dict`, overwritten each time the planner
fires.**

```python
class CoachingPlan(BaseModel):
    focus_field:        str
    next_action:        str
    retrieval_strategy: Literal["single_hop", "multi_hop"]
    retrieval_hops:     list[str]    # template strings; empty for single_hop

phase_planner = llm.with_structured_output(CoachingPlan)
coaching_plan: CoachingPlan = phase_planner.invoke(planner_prompt)
```

**One plan, and it is typed** (§71-C). "Dict, not list" remains the rule —
what changed is that the single object is a validated Pydantic model rather
than a bare dict. A plain dict cannot be validated at planner-output time, and
`retrieval_strategy` in particular needs the `Literal` constraint: it selects
the executor's entire retrieval path, and a typo silently falls through to
single-hop. Consumers read `coaching_plan.retrieval_hops`, not
`coaching_plan["retrieval_hops"]`.

The list form implied an upfront queue of plans, and the subgraph is a
cycle (§5, §11): the planner fires many times per phase, and the Belt's
answers change what the next plan should be. A plan made at turn 1
cannot anticipate turn 4 — so a queued plan is either followed against
the evidence or discarded, and it is dead weight either way. The planner
reads current `artifacts` to know what is captured and what is next.
That is the queue, and it is derived rather than stored.

**The plan is transient; its consequences are durable.** Captured values
and tool output land in `artifacts`, sources in `citations`, the
planner's decision and rationale in `step_log`, the conversation in
`messages`, and the full LLM input/output in the LangSmith trace.
Nothing is lost when the next plan overwrites this one.

### Critical Design Insight: `artifacts` vs `step_log`
- `artifacts` = WHAT was captured (the results)
- `step_log` = HOW it was captured (the audit trail)

These are **separate fields**. The pre-refactor code mixed them — `captured_fields` held results with no separate record of how each field was captured. For DMAIC quality systems the separation matters: the Belt needs to show not just what the root cause was, but how it was determined.

`step_log` entries are **dicts, not tuples** (ratified in §68). Self-documenting and inspectable:

```python
{"layer": "constraint", "attempt": 2, "status": "failed",
 "reason": "does not address timeline", "decision_excerpt": "..."}

{"service": "gpt-4o", "attempt": 2, "status": "failed",
 "reason": "timeout after 45s", "timestamp": "..."}
```

Everything that needs an audit trail writes here: the four validation layers (§68), each grader iteration via the `on_evaluation` callback (§42), and every fallback-chain attempt (§67).

**Every entry carries a deterministic key, never a raw timestamp as its
identity:**

```python
step_key = f"{phase}:{turn_count}:{step_name}"     # "analyse:7:constraint_check"
```

A timestamp is still recorded as *data* — it is just not what identifies the
entry. The distinction matters once checkpoints are live: a turn that is
retried, resumed from a checkpoint, or replayed after a client disconnect
re-executes the same logical step, and a timestamp-keyed log records that as
two separate events. A deterministic key makes the write idempotent — the
replay overwrites its own earlier entry instead of duplicating it. Without
this, `step_log` inflates on every retry and the audit trail stops being
evidence of what happened. This is a hard requirement of the disconnect
policy in §17.

### Boundary Mapper Pattern

`SupervisorState` and `PhaseState` are different schemas, so something has to translate between them at the subgraph boundary. In EDUCATIONAL.md this was implicit. It is explicit here — two plain functions per phase:

```python
def define_input_mapper(
    parent: SupervisorState,
    store: BaseStore,
) -> PhaseState:
    """SupervisorState → DefineState. Context is composed from the store,
    never carried on parent state (§23 — subgraph state does not
    propagate). Define has no prior phase, so its source is the case
    record loaded at session start (§52a)."""
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


def define_output_mapper(
    child: PhaseState,
    parent: SupervisorState,
    store: BaseStore,
) -> dict[str, Any]:
    """DefineState → SupervisorState update. The gate document goes to the
    store; only orchestration-relevant values go back to the parent."""
    store.put(
        ("projects", parent["case_id"], "artifacts"),
        "define",
        child["final"],                 # the approved gate document
    )
    return {
        "current_phase": "measure",
        "phase_index":   1,
        "gate_passed":   {**parent["gate_passed"], "define": True},
    }
```

**The three orchestration values advance together, from this one site.**
That is what makes §17's derived-field exemption for `current_phase` and
`phase_index` safe — there is exactly one place they can go out of step
with `gate_passed`, and it is this function.

The rule the mappers enforce: **the parent never sees the subgraph's coaching turns, tool calls, or extraction attempts — only the structured output at exit.** See §19 for the concrete Define→Measure walkthrough and §23 for why the store rather than parent state carries the artifacts.

**Every input mapper composes `phase_context` from the store**, Define from the case record and every later phase from the prior phase's artifacts. That uniformity is the point: an input mapper's only dependency is `BaseStore`, so no parent-state field has to be kept current and no phase's context can go stale because a write was missed. An earlier revision made Define the exception by reading `parent["project_context"]` — the field §17 removed for having no writer.

The case record reaches the store once, at session start, from `cases/case_{id}.json` into `("projects", pid, "case")`. It is not re-read per phase entry, and the case blob remains the system of record. Mappers are pure translation functions; handing one a blob client would put untracked I/O inside the boundary.

### AgentLean Field Mapping

| Course Lab Field | Agent Improve Equivalent |
|---|---|
| `task: str` | **No equivalent.** It became `project_context` on `SupervisorState`, which §17 later removed as an inherited field with no writer. `phase_context` on `PhaseState` is composed at the boundary from the store — the lab's single fixed task has no counterpart in a five-phase methodology where the work is fixed and the substance is the Belt's captured fields |
| `plan: List[Dict]` | `coaching_plan: dict[str, Any]` — one plan per planner turn, not a queue |
| `step_index: int` | Split in two: `phase_index` on `SupervisorState`, `field_index` on `PhaseState` |
| `artifacts: Dict` | `artifacts` — written to the store inside the gate document at approval |
| `step_log: List` | `step_log` — dict entries, append-only reducer |
| `final_output: str` | `final: dict[str, Any]` — the approved gate document itself, not a description of it |
| `InMemorySaver` | Not used. Parent-only `AzureBlobCheckpointSaver` → `PostgresSaver` (§1) |
| *(not in the lab)* | Boundary mappers — the input/output translation above |
| *(not in the lab)* | `gate_attempts`, `validator_feedback` — the lab's loop had no cap and no accumulated feedback (§68) |
| *(not in the lab)* | `citations`, `uploads` — the lab had no retrieval and no external evidence channel |

### Where the gate document is written — the missing writer

**The store-mediated handoff had a reader and no writer.** §19 and §70
both describe the next phase's input mapper reading the prior phase's
artifacts out of the store, and §52a defines the namespace — but nothing
specified the write. It is `gate_apply_node`, at step 7 of §2's nine,
and it writes to **two** destinations:

```python
gate_document = {
    **child["artifacts"],                     # every captured field
    "computation_results": child["artifacts"].get("computation_results", []),
    "citations":           child["citations"],
    "uploads":             child["uploads"],
    "acknowledged_gaps":   acknowledged_gaps,  # Tier 2 gaps the Belt accepted (§42)
}

store.put(("projects", case_id, "artifacts"), phase_name, gate_document)
return {"final": gate_document, "gate_attempts": 0, "validator_feedback": []}
```

Physical path: `store/projects/IMPR-2026-E9D/artifacts/define.json`.

**Both writes are needed because the store write and the checkpoint
commit are separate operations.** A crash between them leaves state
saying the gate was not applied while the store says it was; `final`
holding the same dict makes the checkpoint self-sufficient for recovery.
That is also the concrete reason `final` had to stop being a `str`.

**The `gate_documents` store namespace is retired.** It held the same
content as `artifacts` under a second key, which turns "which is
authoritative?" into a live question with no answer. A phase's approved
artifacts and its gate document are one object.

---

## 19. Multi-Step Task Chaining

*Source: Edureka course — Building Multi-Step Task Chains demonstration*

### The Core Pattern
A single LangGraph task chain is defined **once** and reused. Each chain runs independently with its own execution history. The finalized output of Chain 1 is injected into Chain 2 as structured input.

### Single Chain Structure (4 nodes)

> **This is the course lab's chain, not Agent Improve's phase subgraph.** Read it for the interrupt mechanism only. Our five nodes are `planner → executor → validation_stack → gate_review → gate_apply` (§23) — there is no `Revise` node, and `state["feedback"]` was split into `belt_edits` and `validator_feedback` (§18).

```
Plan → Execute → Review (interrupt) → Revise → END
```

- **Plan node**: decomposes task into structured steps. Does NOT execute. Stores plan in state.
- **Execute node**: follows planner output, produces concise draft stored in `state["draft"]`
- **Review node**: pauses using `interrupt()`. Payload includes draft, allowed actions, decision hint. Stores human decision in `state["feedback"]` *(lab name — ours is `belt_edits`)*
- **Revise node**: if approved → draft becomes final immediately. If revision requested → regenerates using provided notes. Every chain ends with human-approved result.

### ChainState Schema — Source Lab Reference

*Kept verbatim as the course original. **Do not build against it** — `plan`, `draft`, `final`, and `feedback` are all `str`, which is a teaching simplification. The ratified equivalents are structured; see `PhaseState` in §18.*

```python
# SOURCE LAB REFERENCE ONLY — superseded by PhaseState (§18)
class ChainState(TypedDict):
    messages:  Annotated[Sequence[str], operator.add]  # append-only
    history:   Annotated[Sequence[str], operator.add]  # node execution order
    task:      str      # instruction for this chain
    plan:      str      # planner's decomposition
    draft:     str      # executor's first output
    final:     str      # approved or revised result
    feedback:  str      # human decision and notes
```

String-typed `draft` and `feedback` force downstream nodes to parse prose out of an upstream node's output. That is precisely the Gap 10 anti-pattern §5 and §21 diagnose. In `PhaseState` these are `dict[str, Any]`.

### Multi-Chain Orchestration — Store-Mediated, Not String-Interpolated

The lab chained by interpolating Chain 1's output into Chain 2's prompt string. For DMAIC that would mean Measure's coach re-reading Define's conclusions out of prose. The ratified mechanism is different:

```python
# ANTI-PATTERN — what the lab does
chain2_input = f"Based on this: {chain1_final}\nNow do: [new task]"

# RATIFIED — store-mediated boundary mapper
# Define's gate approval writes structured artifacts:
store.put(
    ("projects", case_id, "artifacts"),
    "define",
    {"problem_statement": "...", "baseline_metric": 4.2,
     "target_metric": 2.1, "project_scope": {...}},
)

# Measure's input mapper reads them:
define_artifacts = store.get(
    ("projects", case_id, "artifacts"), "define"
).value
```

**CORRECTION — one thread_id per project, not one per phase.**

An earlier draft of this section had each phase running on its own `thread_id` (`IMPR-2026-FS1-define`, `IMPR-2026-FS1-measure`). That is Pattern B — separate graph invocations. §23 describes Pattern A — subgraphs embedded in a parent supervisor graph — and LangGraph documentation (verified 2026-07) confirms Pattern A is the native mechanism for multi-phase orchestration. Per-subgraph `thread_id`s cause duplicate storage and state-persistence problems. The corrected model:

- **One `thread_id` per project**: `IMPR-2026-FS1`
- **Each phase is one subgraph embedded as a node** in the supervisor parent graph
- **LangGraph auto-namespaces each subgraph's checkpoints** via `checkpoint_ns` (a regression here was fixed in LangGraph 1.2.6 — subgraphs now inherit the parent `checkpoint_ns` correctly, which is why 1.2.6+ is the version floor)
- **The store mediates artifacts between subgraphs** — per LangChain docs: *"Use shared state via Store for data that needs to cross graph boundaries"*

*This was corrected three times during the review — first in §23, then here, then in §44. It is definitively settled.*

### Concrete Walkthrough — Define → Measure

```
1. Define subgraph runs. Level 2 cycles capture six fields into
   PhaseState.artifacts. Nothing is written outside the subgraph yet.

2. Define's gate: validation stack (§68) → interrupt → Belt reviews,
   edits, policy advisory fires, Belt approves.

3. Checkpoint saves. THEN define_output_mapper runs:
      store.put(("projects", "IMPR-2026-FS1", "artifacts"), "define",
                {"problem_statement": ..., "baseline_metric": 4.2, ...})
   and returns to the parent only:
      {"current_phase": "measure", "phase_index": 1,
       "gate_passed": ["define"]}

4. Static edge fires: define → measure.

5. measure_input_mapper runs:
      define_artifacts = store.get(
          ("projects", "IMPR-2026-FS1", "artifacts"), "define").value
      phase_context = build_measure_context(define_artifacts)
   Measure's PhaseState starts with structured knowledge of Define's
   problem statement and baseline metric — as typed values, not prose.

6. Measure's planner reads phase_context and Measure's own required
   fields, and plans its first coaching turn.
```

At no point does Measure parse Define's output out of a message. If Measure needs Define's baseline metric it reads a named field out of a structured gate document — as a string, which `calculate_sigma_level` parses at the point of use (§17) — and if that value later changes, §38's contradiction check fires.

*An earlier revision of this paragraph said Measure "reads a float." It does not, and no schema in this project has ever typed a baseline as a float. The prohibition being stated is on parsing a value out of an interpolated prompt, not on the value's type — and stating it as a typing guarantee was the drift §17's Finding 3 corrected.*

### Critical Rule — Resume Mechanics
```python
# Same graph instance + same thread_id MUST be used when resuming.
# This ensures LangGraph restores state correctly from checkpoint.
await graph.ainvoke(
    Command(resume=decision),
    config={"configurable": {"thread_id": case_id}},
)
```

### AgentLean Mapping

Each DMAIC phase **is a subgraph embedded in the supervisor parent graph** — not a separately invoked chain. One `thread_id` per project. Each subgraph has its own auto-managed `checkpoint_ns`. Cross-phase artifacts flow through the store, never through parent state and never through string concatenation. Each phase still runs Plan → Execute → Review → Revise, with Belt approval before its output becomes the next phase's input.

### Nested Plan / Execute / Review / Revise — Level 1 vs Level 2

The four-node chain above describes **Level 1**. Inside Level 1's Execute stage, the same four stages run again per field. This is the mechanism behind §5's nested cycle.

**Level 1 — phase chain:**

| Stage | What happens |
|---|---|
| Plan | Phase planner decides the coaching strategy for the phase — which fields to elicit, in what order, with which tools |
| Execute | Phase executor iterates through the strategy, running per-field cycles (Level 2) |
| Review | Gate interrupt — Belt reviews all captured fields for the phase |
| Revise | Belt edits, policy advisory fires, Belt approves; the final gate document is written |

**Level 2 — per-field cycle, nested inside Level 1 Execute:**

| Stage | What happens |
|---|---|
| Plan | Within-turn planner decides the coaching action for the current field — elicit, teach, challenge, re-ask with different framing, offer a worked example |
| Execute | Coaching LLM runs; extraction runs; one field captured into `draft` |
| Review | Fast completeness and coherence check on the captured field — **no interrupt** |
| Revise | If not clean, loop back to Level 2 Plan with the failure signal; otherwise merge `draft` into `artifacts`, increment `field_index`, move on |

**Concrete example — Define phase, IMPR-2026-FS1.** Six required fields (`problem_statement`, `business_case`, `project_scope`, `goal_statement`, `baseline_metric`, `target_metric`). Level 2 fires roughly 6–10 times inside Level 1 Execute, because some fields need re-asks. The Level 1 Review interrupt fires only once, when Level 2 has completed for all six and the §68 stack has passed.

**What this replaces in the current codebase:** the monolithic coaching loop where field capture, re-asking, and completeness checking are all fused inside a single prompt — the Gap 10 "planning implicit in prompts" problem §5 diagnoses.

---

## 21. State Passing Across Agent Nodes

*Source: Edureka course — Message Passing Across Agent Nodes demonstration. **Renamed**: despite the course's section name, the primary handoff channel in this pattern is a dedicated state field, not messages. Messages provide the audit trail. Downstream nodes read structured state and never parse prose from message history.*

### Sequential Pipeline Pattern (Generator → Reviewer → Refiner)
Three-stage pipeline where each agent builds on the previous one's work.

```python
class PipelineState(MessagesState):
    draft:    dict[str, Any]    # generator's structured output
    feedback: dict[str, Any]    # reviewer's structured critique
    final:    dict[str, Any]    # refiner's structured result
```

**Two corrections to the course version.** Its `draft: str` and `feedback: str` are the same teaching simplification as §19's `ChainState`; for Agent Improve these are structured, matching `PhaseState` (§18). And its comment `# final comes from messages` is worse than a simplification — it makes downstream consumers parse prose out of message history, which is exactly the Gap 10 anti-pattern. `final` is a structured field.

### Dual Storage Pattern
Each node writes results to TWO places:
1. A **dedicated state field** for the next node to access directly
2. The **messages list** as a named message for full audit traceability

```python
# Generator writes to both — structured state field + audit message
return {
    "draft": {"problem_statement": "...", "baseline_metric": 4.2},   # for the next node
    "messages": [
        AIMessage(
            content=json.dumps(draft, indent=2),   # or a human-readable summary
            name="generator",
        )
    ],
}

# Reviewer reads the structured field directly — never parses prose
reviewer_input = state.get("draft", {})
```

The principle is right and worth keeping: one channel for machines, one for humans and audit. The channels must not be swapped.

### Safe State Access Pattern
```python
# Always use .get() with a default — never assume the field exists
draft      = state.get("draft", {})
belt_edits = state.get("belt_edits", {})
```
Valid defensive coding regardless of the value type. No change needed here.

### AgentLean Application — Within-Chain vs Between-Chain

The dual-storage principle is correct but must be scoped carefully. It describes **within-chain** handoff, not **between-chain**.

**Within-chain handoff** — nodes inside a single phase subgraph passing structured results to each other. Inside the Define subgraph, the extraction node writes to both `state["draft"]` (structured, for the next node) and to messages (for audit). The gate-review node reads `state["draft"]`, not message history. This is the pattern above.

**Between-chain handoff** — Define → Measure, Measure → Analyse, and so on — uses a different mechanism: **the store, not a state field.** When Define's gate is approved, its artifacts are written via `store.put(("projects", case_id, "artifacts"), "define", {...})`, and Measure's input mapper reads them via `store.get(...)`. See §19 for the walkthrough and §52a for the store itself.

*The EDUCATIONAL.md version of this paragraph said Define writes its gate document to `captured_fields["define"]` for Measure to read directly. That contradicts §17 — `captured_fields` was removed from `SupervisorState` — and §23, which explains why: LangGraph subgraph state does not automatically propagate to the parent's visibility, so a parent state field is the wrong carrier for cross-phase data.*

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

`DefineOutput` as a typed Pydantic object (§18, §44) is not just a completion record — it is the structured input the Measure phase planner uses to scope its work correctly.

**The mechanism is the store, not a direct pass.** The Phase Orchestrator does not hand `define_output` into the Measure subgraph's initial state as a parameter. Define's `output_mapper` writes it via `store.put(("projects", case_id, "artifacts"), "define", {...})`, and Measure's `input_mapper` reads it via `store.get(...)` (§18, §19, §52a). The reason is §23's constraint: subgraph state does not propagate to the parent's visibility, so parent state is the wrong carrier for anything a later phase depends on.

The consequence is the same as this section describes, and that is the point: the Measure subgraph reads Define's scope and CTQs to know what to measure — it does not independently decide.

**This is why gate quality matters so much:** a weak Define gate produces compounding error across all downstream phases. A problem statement without a measurable baseline produces a Measure phase that cannot establish a valid sigma level. A sigma level without a valid baseline produces an Analyse phase that cannot validate root causes. The error propagates and amplifies. **Gate quality is not a bureaucratic checkpoint — it is a data integrity guarantee for every downstream phase.**

This is also why §38's re-approval cascade is as heavy as it is. If a Belt changes a gate-approved baseline mid-project, every downstream phase built on that value becomes provisional. Not because the process is bureaucratic, but because the chain above is real.

### Gap Register Note
No new gap number — this section supplies the argument for why gate quality validation (§68) is non-negotiable, and confirms the store-mediated handoff pattern (§52a). Use this reasoning when explaining to stakeholders why the four-layer stack is not overhead.

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
# During the refactor
from core.checkpointer import AzureBlobCheckpointSaver
from core.store import AzureBlobStore                    # §52a

checkpointer = AzureBlobCheckpointSaver(blob_client)      # short-term, thread-scoped
store        = AzureBlobStore(blob_client)                # long-term, cross-thread

# Post-refactor, pre-production — same interfaces, different backend
# from langgraph.checkpoint.postgres import PostgresSaver
# from langgraph.store.postgres import PostgresStore
# checkpointer = PostgresSaver.from_conn_string(PG_CONN)
# store        = PostgresStore.from_conn_string(PG_CONN)

graph = builder.compile(checkpointer=checkpointer, store=store)   # parent graph only


# Inside any node — the store is injected automatically when declared as a parameter
async def analyse_node(
    state: PhaseState,
    config: RunnableConfig,
    *,
    store: BaseStore,
) -> dict:
    case_id = config["configurable"]["thread_id"]

    # Read the prior phase's artifacts — the cross-boundary mechanism (§19, §23)
    measure_artifacts = store.get(
        ("projects", case_id, "artifacts"), "measure"
    ).value

    # Write this phase's artifacts at gate approval
    store.put(
        ("projects", case_id, "artifacts"),
        "analyse",
        {"root_cause": state["artifacts"]["root_cause_statement"],
         "outcome": "validated"},
    )
```

*The original example used `InMemoryStore` for dev and namespaced by domain (`("dmaic_cases", "call_centre", "complaint_rate")`). The ratified namespace convention is `("projects", case_id, <kind>)` — see §52a. Cross-**case** retrieval for yokoten goes through `rag_lookup_case_history` against `improve_case_index`, not through the store; the store carries cross-**phase** artifacts within one project.*

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

**Resolution: Option A, with the two roles separated.** `improve_case_index` stays as Azure AI Search and is reached through `rag_lookup_case_history` (§32, §33) — it needs hybrid BM25 + vector scoring and multi-query + RRF, neither of which `BaseStore.search` provides. The store is used for a different job: **cross-phase artifact handoff within one project** (§52a). Two mechanisms, two purposes, no overlap:

| | Carries | Scope | Mechanism |
|---|---|---|---|
| Store | Phase artifacts — Define's output for Measure to read | One project | `store.put` / `store.get`, namespace `("projects", case_id, "artifacts")` |
| `improve_case_index` | Completed case summaries for yokoten | All projects | `rag_lookup_case_history` — multi-query + RRF + metadata filters |

The framing that made this look like an either/or was treating "long-term memory" as one thing. It is two.

### Two Critical Operational Findings Not Previously Documented

**Finding 1 — `thread_id` has a hard length limit of 255 characters with `PostgresSaver`:**

> "When using PostgresSaver (or AsyncPostgresSaver), the thread_id is stored in a column with limited length. If your thread_id exceeds the column size, you will see a database error. Fix: Keep thread_id values under 255 characters."

**This concern dissolves under the corrected threading model.** It assumed the nested-subgraph `thread_id` concatenation that §44 originally proposed — `f"{case_id}-define-debate-{root_cause_id}"`. There is **one `thread_id` per project** (`IMPR-2026-FS1`); LangGraph manages per-subgraph namespacing itself via `checkpoint_ns` (§19, §23, §44). Nothing is concatenated, so nothing can overflow.

The limit remains worth knowing for the `PostgresSaver` migration, but it is no longer a design constraint. Gap 30 closes by construction.

**Finding 2 — confirmed documented LangGraph limitation: subgraph state updates do not automatically propagate to the parent:**

> "When a subgraph updates state, the parent graph may not see the changes immediately. This is because each subgraph manages its own checkpoint namespace. Fix: Use shared state via Store for data that needs to cross graph boundaries, or configure your subgraph to write to the parent checkpoint."

**This is the finding that determined the cross-phase handoff mechanism.** §44 originally described shared-key-name propagation as fully automatic. The official source confirms it is not always immediate, and explicitly names the **Store** as the fix for data crossing graph boundaries.

The ratified design follows that recommendation rather than testing around it: `captured_fields` and `gate_documents` were removed from `SupervisorState` (§17), and cross-phase artifacts travel through `AzureBlobStore` (§52a) via boundary mappers (§18). Shared key names remain fine for in-graph communication; they are not the carrier for anything a later phase depends on.

### Gap Register Update

**Gap 20 — resolved by separating two jobs.** `improve_case_index` stays for cross-**case** yokoten retrieval via `rag_lookup_case_history`; the Store carries cross-**phase** artifacts within one project. See the resolution above.

**Gap 30 — CLOSED by construction.** One `thread_id` per project; LangGraph manages `checkpoint_ns`. There is no concatenated `thread_id` to overflow the 255-character column.

**Gap 31 — CLOSED: confirmed real, and designed around.** Subgraph-to-parent propagation is documented as not-necessarily-immediate. Rather than integration-testing a shared-key approach and hoping, the design routes cross-boundary data through the Store, which is the officially recommended fix.

*Cross-references: §1 (checkpointer), §17/§18 (what moved out of parent state and where it went), §19/§23 (the boundary mechanism), §36 (memory taxonomy), §52a (the `AzureBlobStore` implementation), §79 (`DeltaChannel` as a future checkpoint-compression option, §87 item 12), §87 item 13 (the PostgreSQL migration).*

---

## 52a. AzureBlobStore and Multi-Chain Persistence

*New section, authored during the batch commit. Positioned immediately after §52 so the general finding and its Agent Improve application sit together.*

§52 establishes the Checkpointer + BaseStore split as a concept. Nothing in the original document applied it concretely to Agent Improve, which left the single most-referenced mechanism in the ratified architecture — "artifacts flow through the store" — undefined. This section defines it.

### Why a Store Is Required, Not Optional

Three independent findings converge on the same conclusion:

1. **§23 / §44** — LangGraph subgraph state does not automatically propagate to the parent's visibility. Officially documented, with the Store named as the fix.
2. **§17** — `captured_fields` and `gate_documents` were removed from `SupervisorState` to keep parent state to orchestration only. They had to go somewhere.
3. **§19 / §70** — Define's outputs are Measure's inputs. String-interpolating them into the next prompt is the Gap 10 anti-pattern.

Without a store, cross-phase handoff has no correct carrier.

### Interface

`AzureBlobStore` implements `langgraph.store.base.BaseStore`. The interface is four methods over tuple namespaces:

```python
from langgraph.store.base import BaseStore, Item


class AzureBlobStore(BaseStore):
    """BaseStore backed by Azure Blob Storage. Transitional — migrates to
    PostgresStore alongside the checkpointer (§1, §87 item 13)."""

    def put(self, namespace: tuple[str, ...], key: str, value: dict) -> None: ...
    def get(self, namespace: tuple[str, ...], key: str) -> Item | None: ...
    def search(self, namespace: tuple[str, ...], *, query: str | None = None,
               filter: dict | None = None, limit: int = 10) -> list[Item]: ...
    def delete(self, namespace: tuple[str, ...], key: str) -> None: ...
```

> **Correction: `BaseStore.search()` does support metadata filtering** via its
> `filter=` parameter. An earlier revision listed metadata filters among the
> things the store lacks, which overstated the case for keeping
> `improve_case_index` on Azure AI Search. The two capabilities the store
> genuinely does **not** provide are **hybrid BM25 + vector scoring** and
> **multi-query + RRF** — and those are the two the yokoten use case actually
> depends on, so Option A above still resolves the same way. The conclusion
> was right; one of the three reasons given for it was not.

**Verified against current LangGraph docs (2026-07 web check):**
- `BaseStore` interface is `put`, `get`, `search`, `delete`, over tuple namespaces
- `search()` accepts `filter=` for metadata filtering alongside `query=`
- The store is injected into nodes via `get_store()` or as a declared function argument
- LangChain docs explicitly recommend the Store for cross-subgraph data — which matches the Define → Measure boundary case exactly

### Namespace Convention

```
("projects", case_id, <kind>)
```

| Namespace | Keys | Contents |
|---|---|---|
| `("projects", case_id, "case")` | `"record"` | Case framing — title, department, belt level, leader, target date. Written once at session start from `cases/case_{id}.json` |
| `("projects", case_id, "artifacts")` | `"define"`, `"measure"`, … | **Each phase's approved gate document.** Written by `gate_apply_node` at gate approval (§18) |
| `("projects", case_id, "step_log")` | timestamped keys | Append-only cross-phase audit trail |

**Physical blob layout:**

```
store/projects/{case_id}/case/record.json
store/projects/{case_id}/artifacts/define.json
store/projects/{case_id}/artifacts/measure.json
store/projects/{case_id}/artifacts/analyse.json
store/projects/{case_id}/artifacts/improve.json
store/projects/{case_id}/artifacts/control.json
store/projects/{case_id}/step_log/{timestamp}.json

checkpoints/{case_id}/latest.json
checkpoints/{case_id}/history/{checkpoint_id}.json
```

`case_id` is the same value as the graph's `thread_id`. One identifier for the case, used by both persistence systems (§17).

**Each `artifacts/{phase}.json` holds the complete approved gate document:** every captured field as a string (§17), the cross-phase reference dicts where they apply, `computation_results`, `citations`, `uploads`, and `acknowledged_gaps` if the Belt proceeded past a Tier 2 warning (§42).

**A `gate_documents` namespace was specified and is now retired.** It held the same content as `artifacts` under a second key, which makes "which of these is authoritative?" a question the design could not answer — and a second copy that can drift is the failure mode §17 spent three amendments removing from parent state. A phase's approved artifacts and its gate document are one object.

The `case` namespace was added when §17 removed `project_context`. Define's input mapper needs *some* framing for `phase_context`, and every other phase gets its framing from the store already — so putting the case record there makes the rule uniform and keeps an input mapper's dependency list at `BaseStore` alone. It is a session-start copy, not a second system of record: `cases/case_{id}.json` stays authoritative, and the copy is never written mid-conversation.

### Compile-Time Wiring

```python
graph = builder.compile(checkpointer=checkpointer, store=store)   # parent graph ONLY
```

Phase subgraphs receive neither. They reach the store through the injected `store` parameter in their node signatures, and their checkpoints route through the parent's saver by `checkpoint_ns` (§23).

### Runtime Pattern — The DMAIC Phase Chain

```
Define subgraph runs → gate validated (§68) → Belt approves (§2)
        ↓
define_output_mapper:
    store.put(("projects", "IMPR-2026-FS1", "artifacts"), "define", {...})
        ↓
static edge: define → measure
        ↓
measure_input_mapper:
    store.get(("projects", "IMPR-2026-FS1", "artifacts"), "define")
        ↓
Measure's PhaseState starts with typed knowledge of Define's outputs
```

Repeated for Measure → Analyse → Improve → Control. See §18 for the mapper implementations and §19 for the full walkthrough.

### Ordering Constraint

**Implement `AzureBlobStore` after Step 6** — after `thread_id` is wired through `graph.ainvoke`. A store is meaningless without functional checkpoint persistence first: if the graph cannot resume, there is no second session for the stored artifacts to serve.

### Migration Path

`AzureBlobStore` → `PostgresStore` happens alongside the checkpointer migration (§87 item 13), against the same PostgreSQL instance. Because both sides of the split are defined by LangGraph interfaces rather than by our implementations, nothing above the persistence layer changes — the namespace convention, the mappers, and every `store.get` / `store.put` call site stay exactly as written.

### What the Store Is Not

- **Not the case index.** Cross-*case* retrieval for yokoten is `rag_lookup_case_history` against `improve_case_index` (§32, §33). The store carries cross-*phase* data within one project.
- **Not a checkpointer.** The checkpointer is automatic and thread-scoped; the store is explicit and cross-thread. Passing only a checkpointer is, per §52, the most common architecture mistake.
- **Not a conversation buffer.** `messages[]` compression is `SummarizationMiddleware` (§36).

*Cross-references: §1 (checkpointer, phased approach), §17 (what left `SupervisorState`), §18 (boundary mappers), §19 (Define → Measure walkthrough), §23 (why subgraph state cannot carry this), §52 (the split), §70 (inter-stage dependency), §87 item 13 (migration).*

---

# PART 7 — DEPLOYMENT AND INFRASTRUCTURE

*Serving, observing, versioning, evaluating, packaging, and driving the system — everything outside the graph itself.*

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

### DECISION — Stay on FastAPI

**Ratified. The deployment layer is FastAPI + LangGraph (MIT) + our own checkpointer.**

The decisive factor is licensing, not preference. LangGraph Server is the official LangServe replacement, but it requires `langgraph-api` under **Elastic License 2.0** — and even the self-hosted tier requires a commercial licence key. Web-verified this session across multiple Tier 1 and Tier 3 sources.

FastAPI + LangGraph + a custom checkpointer is the standard approach for self-hosted deployments without a commercial licence, and it is what Agent Improve already uses. The work is to fix `routes.py:238` (refactor Step 6 — wire `thread_id` through `graph.ainvoke`) and keep the custom plumbing.

| | FastAPI *(selected)* | LangGraph Server |
|---|---|---|
| Licence | MIT | Elastic License 2.0 — commercial key required even self-hosted |
| SSE streaming | Hand-wired, already working | Built in |
| HITL resume endpoints | Hand-wired (§2's two endpoints) | Built in |
| `thread_id` routing | Hand-wired in `routes.py` | Built in |
| Data residency | Stays in our Azure tenant | Depends on tier |
| Alignment | Matches the `valuesims-*` → `agentlean-*` Azure plan | New infrastructure relationship |

**LangGraph Studio remains useful for development** — `langgraph dev` locally gives the visual graph debugger without adopting LangGraph Server for production. Use it; do not deploy on it.

### What This Means Right Now

The question §55 raised is answered, and the answer propagates: §1 (checkpointer wiring), §12 (the two gate endpoints), §44 (the interrupt implementation), and §72 (which documents the fuller evaluation) all assume FastAPI. §72 is retained as the record of *why*.

---

## 72. LangGraph Server — Deployment Option for AgentLean

*Source: Verified against official LangChain documentation (docs.langchain.com/langsmith/deploy-standalone-server), LangGraph Platform GA announcement, and multiple current sources (March-May 2026).*

> **Decision made in §55: stay on FastAPI.** This section documents the evaluation that produced that decision, and is retained as the record of why.
>
> The deciding factor was licensing: LangGraph Server requires `langgraph-api` under **Elastic License 2.0**, and even the self-hosted tier needs a commercial licence key. FastAPI + LangGraph (MIT) + a custom checkpointer is the self-hosted path without one — and it is what Agent Improve already runs.
>
> **What we adopt anyway:** LangGraph Studio for local development debugging (`langgraph dev`). It is genuinely better than anything hand-built for inspecting graph execution, and using it locally carries no licensing obligation for the deployed service.

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

The LangGraph graph code itself does not change. `SupervisorState`, phase subgraphs, the Orchestrator, the checkpointer — all identical. The only thing that changes is the layer that exposes the graph to the outside world.

### Gap Register Note
No new gap number — this section documents LangGraph Server as an option that directly addresses Gap 2 (HITL) through built-in resume endpoints. Evaluate explicitly during the DMAIC redraw. Do not default to either option without consciously working through the decision framework above.

---

## 73. Langfuse — Open-Source LangSmith Alternative

*Source: Verified against multiple current independent sources, May-June 2026. Triggered by the course introducing Langfuse in Module 3.*

> **Status: knowledge for future enterprise conversations. No decision needed for the refactor — keep LangSmith**, which has been wired in since commit 1.1 and is mandatory per CLAUDE.md §1.8.
>
> **Three triggers that would make this worth revisiting:**
> 1. An enterprise customer asks about data residency for observability data
> 2. The team grows and per-seat LangSmith pricing becomes significant
> 3. AgentLean adds components outside the LangChain ecosystem
>
> One capability worth noting for later: Langfuse's **Code Evaluators** run programmatic checks against production traces without LLM cost. That connects directly to §68's Layer 2 (field presence) as a continuous production-monitoring option — the same deterministic check, run against live traffic rather than at the gate.

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

*Source: Edureka Course 4 Module 3, "Designing Versioned Agent Endpoints" transcript. LangServe-specific implementation replaced with FastAPI equivalents (§55). Concepts are framework-agnostic.*

> **Status: knowledge for post-launch. No decision needed for the refactor.** No production system exists yet — the refactor produces the first production-grade version, so there is nothing live to avoid breaking. Versioning becomes relevant *after* launch, when updates must not break Belts mid-project.
>
> Two things here are worth preserving until then: the **breaking-change definition table** for agent APIs (the observation that behaviour can change completely while the interface stays identical is specific to agents and easy to underestimate), and the **"add new fields as optional"** discipline.

### Why Versioning Matters for Agent APIs

Agent APIs are different from standard REST APIs in one critical way: **the interface can stay identical while the behaviour changes completely**. A model update, a prompt change, a graph restructure, or a new tool can all produce different outputs for the same input without changing a single endpoint signature. Downstream systems break silently.

Three specific risks for AgentLean:

```
Risk 1 — State schema change:
  v1 graph state has a flat captured_fields dict on the parent
  v2 SupervisorState holds orchestration only; the typed DefineOutput /
     MeasureOutput gate documents live in the Store, never on parent state
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
  ✗ State schema restructured (SupervisorState field names or types changed)
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
| State schema | Flat parent state | `SupervisorState` (orchestration only) + typed gate documents in the Store | ✅ Yes |
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

> **Status: ratified, with modified sequencing.**
>
> **Build the eval dataset *alongside* the refactor, not before it.** Establishing a quality baseline against the current system would produce a baseline of "bad" — it is not production-ready, and its coaching quality is not the thing we want to preserve. The eval suite becomes critical when the coaching agent, retrieval tools, and grader middleware are wired, because that is when output quality actually changes. Infrastructure steps (graph structure, state schemas, checkpointer) do not affect coaching quality and do not need eval coverage.
>
> **It is a joint exercise, not a generated artifact.** Claude proposes examples from the ratified architecture and DMAIC domain; the user reviews and corrects with Black Belt expertise. Coaching quality judgments are domain judgments — generating them unilaterally would produce a dataset that measures agreement with a model rather than correctness. Scheduled as a dedicated session, with output as JSON or Python ready for LangSmith's `create_dataset` API.
>
> **Minimum viable eval suite (ratified):**
>
> | Dimension | Ratified |
> |---|---|
> | Size | 20–30 examples across all five DMAIC phases (4–6 per phase) |
> | Categories | Realistic coaching turns · edge cases · tool-calling scenarios · failure/ambiguous cases · historical production data (once available) |
> | Metrics | Accuracy (field extraction) · relevance (coaching alignment) · reasoning quality (explanation depth) · tool usage (correct invocation) · safety (no invented methodology) |
> | Evaluator order | Deterministic field extraction ($0) → LLM-judge coaching relevance (~$0.01/example) → LLM-judge reasoning quality (~$0.02/example) |
> | Regression threshold | **Block release if any metric drops >10% from baseline** |
> | Run frequency | Every commit touching system prompts, graph structure, or model config |
> | Cost per run | ~$0.60 for 20 examples |
>
> **Rubrics and the eval dataset are complementary, not duplicative.** Rubrics (§42) define what "good" looks like *for the grader*, and run in production at every gate. The eval dataset tests whether the whole system — coach plus retrieval plus grader plus validation — produces good outcomes, and runs in CI/CD at every commit. Different consumers, different cadence, different failure modes caught.
>
> This is also why grader temperature is pinned at 0.1 (§42): a grader that returns different verdicts across runs makes regression thresholds meaningless.

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
| Tool usage | Are tools invoked appropriately? | Was `rag_lookup_methodology` called when needed? Was it called unnecessarily? |
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
   FastAPI — decided in Section 55
   NOT LangGraph Server (Elastic License 2.0, Section 72)
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
"Review captured Define fields"

  problem_statement:    Invoice error rate in EMEA billing at
                        12.3% since Jan 2026
  process_map_sipoc:    5 steps, Sales -> Finance  [renders as table]
  project_scope:        In: invoice creation -> dispatch, EMEA
                        Out: credit notes, APAC, upstream CRM
  voc_summary:          Collections need right-first-time
  goal_statement:       12.3% -> below 5% by 30 Sep 2026
  issues_and_barriers:  IT access via weekly extract

  [Edit fields] [Approve and advance to Measure ->]
```

This is the HITL review step from §2, made concrete in UI terms — specifically steps 4 and 5 of the nine-step gate. The Belt verifies accuracy before the gate commits, not after. Any field they correct is validated by the policy advisory at step 6, and if the corrected value contradicts one approved at an earlier gate, §38's contradiction check fires with its re-approval cascade.

> **This pattern is no longer a gate-time-only view.** It merges with
> Pattern 4 into the **live gate document** described below — the same
> fields, visible continuously rather than surfaced once at the gate.
> The field names above are the ratified `DefineOutput` schema (§17,
> ARCHITECTURE.md §4.10.2); an earlier revision of this example used the
> v1 `what` / `why` / `scope` / `how_goal` names, which no longer exist.

*The original text also attributed a "feedback adaptation signal" here to Gap 21. That was a mis-reference — feedback adaptation is §40's Idea 3, deferred to §87 item 9. Gap 21 is metadata filters, which are in refactor scope and unrelated to what happens when a Belt edits a field.*

---

### Pattern 4 — Completeness as Visual Signal

Progress is derived from `PhaseState.artifacts` against the phase's
Tier 1 / Tier 2 field list — not read from a stored score. Surface it
continuously, not only at the gate:

```
Required: [##########..]  5 of 6     Recommended: [####......]  2 of 5

  [x] problem_statement    - measurable problem confirmed
  [x] process_map_sipoc    - 5 steps, end to end
  [x] project_scope        - boundaries confirmed
  [x] voc_summary          - two customer groups
  [x] goal_statement       - SMART, dated
  [ ] issues_and_barriers  - not yet captured

  "One required field left before the gate can run."
```

Colour coding, on the **required** count:

```
all required complete  -> green  -> "Ready to review gate"
1-2 remaining          -> amber  -> "N required fields still needed"
3+ remaining           -> red    -> "Several required fields missing"
```

**Two counts, not one.** Tier 1 and Tier 2 get separate bars (§17
Finding 11). A Belt at 6/6 required and 0/5 recommended can pass the
gate; a single blended percentage would read as 55% and imply otherwise.

> **A stored `completeness_score` is not the mechanism.** The v1 field of
> that name went with the v1 flat parent state and does not exist on
> `SupervisorState`. Progress is derived on demand from
> `artifacts`, the same way `check_gate_status()` derives missing fields
> (ARCHITECTURE.md §4.1) — a stored score is a second source of truth
> that can disagree with the gate.

---

### Patterns 3 + 4 Merged — The Live Gate Document

**Patterns 3 and 4 are one component, not two.** Showing the Belt their
captured fields and showing them their progress are the same view at
different zoom levels, and splitting them across two moments produced the
wrong behaviour: fields visible only at the gate, progress visible only
as a number.

**The implementation is a single live document tab**, alongside the chat,
always visible. It already exists in the current Agent Improve UI as the
last tab.

| Requirement | Behaviour |
|---|---|
| **Always visible** | A tab or panel beside the conversation, not behind a menu. The Belt glances at it |
| **Updates in real time** | When the coach captures a field via `CoachingResponse.fields_captured` (§82), the document updates immediately — no refresh |
| **Reads as a document** | Headers, formatted content, tables. This is what gets shown to a sponsor, not a list of field names and values |
| **Downloadable at any point** | PDF and Word. Mid-phase downloads show `[not yet captured]` placeholders; post-gate downloads are the approved document |
| **Phase-specific formatting** | Define renders SIPOC as a table, Measure the process map with timings, Analyse the test results, Control the five sub-plans as sections |
| **Computation results rendered** | `artifacts["computation_results"]` renders inline with its interpretation — *"Sigma level: 2.6 — typical for an unimproved process"* — never raw JSON |
| **Citations shown** | `citations` render as a references section so the Belt and their sponsor can verify the methodology |

**The rendering format is defined per phase in the skills**, not here.
Each phase's SKILL.md carries a **Document Layout** section specifying
which fields get headers, which render as tables, which render inline,
where computation results and citations appear, and the download
structure:

| Phase | Skill — Document Layout section | Layout specifics |
|---|---|---|
| Define | `skills/dmaic-define-phase/SKILL.md` §8 | SIPOC as a row-per-step table with process volume; Tier 2 fields below a "Recommended" divider |
| Measure | `skills/dmaic-measure-phase/SKILL.md` §8 | Detailed process map as a table with touch-time vs elapsed-time totals; X-Y matrix as a table; vital few X's as a numbered list |
| Analyse | `skills/dmaic-analyse-phase/SKILL.md` §9 | `causal_hypothesis` as a callout box showing the cross-phase link; `ruled_out_causes` as a cause / test / result table |
| Improve | `skills/dmaic-improve-phase/SKILL.md` §8 | Pilot result with an explicit before / after / change line; implementation plan as a phased table |
| Control | `skills/dmaic-control-phase/SKILL.md` §8 | Before/after block leads the document; control plan as five named sub-sections each with a written / implemented status pair; sign-off as a three-party table |

**No new backend work.** The data source is `PhaseState.artifacts`,
already checkpointed and updated on every capture (§18). The frontend
reads it and renders the template for the current phase. What was missing
was the rendering spec, and that now lives in the skills.

**Why the spec belongs with the skills rather than here.** The layout is
a coaching artefact: it decides what the Belt sees while being coached
and what they hand to a sponsor. It changes whenever the field set
changes, and the field set is defined in the skill. Keeping the two
together means one file changes, not two.

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
- `PhaseState.artifacts` → **Patterns 3 + 4 merged** — the live gate
  document. Both the field content and the progress counts derive from
  this one source; there is no stored `completeness_score` (§17)
- `artifacts["computation_results"]` and `citations` → rendered inline in
  the same document
- `current_phase` and `gate_passed` → Patterns 2 and 6
- LangSmith run ID → Pattern 5
- Node execution events via SSE → Pattern 1

The frontend just needs to surface what the agent already knows. The one
thing it also needs is a **rendering spec per phase**, and that lives in
each SKILL.md's Document Layout section rather than here.

*An earlier revision of this list named `completeness_score` and
`captured_fields`. Neither exists: the score was never a stored field in
the ratified design, and `captured_fields` was renamed `artifacts`
(§17 Finding 15).*

### Gap Register Note
No new gap number — these are frontend design requirements, not architectural gaps in the agent. Record them as input to the AgentLean frontend design conversation when the UI is being built or redesigned. The agent architecture already produces every data point these patterns require.

---

## 78. Menu-Driven Developer Orchestration — A Pattern from the MCP Demo

*Source: Edureka Course 4 Module 1, "Orchestrating the Full MCP Workflow" (main.py demonstration). This is a small but genuinely useful pattern for AgentLean's development experience — not captured elsewhere in this document.*

### The Pattern

Rather than requiring developers to remember multiple commands (`docker up`, `python mcp_server.py`, `python client.py`, `curl` for health checks), wrap the full development lifecycle in a single command-line menu that guides the user through it:

> **Status: ratified. Build it as an early refactor task — roughly 30 minutes — replacing the destructive `start.ps1`.** Cheap, and it removes a real hazard on day one rather than at the end.

```
========================================
  AgentLean Development Menu
========================================
1. Check prerequisites (Python version, dependencies, credentials)
2. Start Agent Improve dev server (uvicorn on 8020)
3. Run evaluation suite (Section 75)
4. Check LangSmith connectivity
5. Run integration smoke test
6. Launch LangGraph Studio (langgraph dev — Section 72)
7. Exit
========================================
```

*Updated from the original: the "Start AgentLean MCP server" option is removed (§39), and the evaluation suite (§75) and LangGraph Studio (§72) options are added.*

### Why It Matters for AgentLean

Two specific pain points this solves:

**Pain point 1 — `start.ps1` is permanently destructive:** the current PowerShell startup script hard-resets to `origin/main` on every run. That is a data-loss hazard sitting in the daily workflow. A menu-driven orchestrator replaces it with explicit, opt-in actions and no destructive default.

**Pain point 2 — multiple terminals become confusing during three-agent development:** when Agent Resolve (8010) and Agent Improve (8020) both need to be running, a menu with clear "start X" options is far less error-prone than remembering which script lives where.

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

### The Key Insight — Infrastructure Layers Are Independently Testable

The course demo's point survives the MCP removal, restated for our stack: the layers fail independently and should be testable independently. Without `LANGCHAIN_API_KEY` the graph still runs, untraced. Without `AZURE_SEARCH_API_KEY` the coach still responds, ungrounded. Without `AZURE_OPENAI_KEY` nothing runs at all.

That ordering is exactly what §67's dual circuit breakers encode — a search outage is a *quality* degradation, an LLM outage is an *availability* failure. A menu that tests each layer separately makes diagnosing a failed coaching turn a matter of elimination rather than guesswork: retrieval layer (§33), Azure OpenAI layer (§67 exception mapping), or graph layer (§23, §44).

**`check_prerequisites()` should match the actual Agent Improve requirements** — the env var list above (`AZURE_OPENAI_KEY`, `AZURE_SEARCH_API_KEY`, `LANGCHAIN_API_KEY`) is correct, and note `AZURE_SEARCH_API_KEY` rather than `AZURE_SEARCH_KEY` (§36).

### Gap Register Note
No new gap number — a developer-experience pattern, ratified as an early refactor task. Replaces the destructive `start.ps1` with an explicit, opt-in orchestrator. Build it alongside the eval suite (§75).

---

# PART 8 — GOVERNANCE AND ANTI-DRIFT

*The three governance layers, the mechanisms that keep them from drifting apart, and the diagnosis that motivated the refactor.*

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
| Plan approval | Not applicable — DMAIC order is fixed (§44), so there is no plan to approve. The equivalent moment is the Belt approving Define's gate document, which is what scopes the project | Covered by the Define gate below |
| Gate evaluation | Belt reviews AI-extracted fields before the phase advances | `interrupt_before=["gate_review_node"]` (§44 two-node pattern) |
| Field correction | Belt corrects wrong values before they are committed | `Command(resume={"corrections": {...}})`, processed by `gate_apply_node` |
| Value contradiction | Belt resolves a conflict with a previously approved value | Interrupt payload emitted by the policy advisory` (§38) |

This risk-classification framework is the principled basis for interrupt placement, and it is what §2's nine-step pattern implements. Note that the four-layer validation stack (§68) is *not* an interrupt — it runs before the interrupt fires, so the Belt is never shown work the system already knows is below standard.

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

**Where each answer lives in the ratified architecture:**

| Question | Source |
|---|---|
| What happened | `PhaseState.artifacts` and `step_log` (§18); LangSmith node spans |
| Why | `coaching_plan` from the phase planner; grader verdicts written through `on_evaluation` into `step_log` (§42); the four validation-layer entries (§68) |
| Who approved it | Belt approval recorded at step 7 of the nine-step gate (§2), with reviewer ID and timestamp |
| When | Checkpoint timestamps (§1); `days_in_phase` and `created_at` on `improve_case_index` (§40) |

`@traceable` on every custom validation function (§1) is what makes parts 1 and 2 answerable without re-running the conversation.

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
`SupervisorState` (main) carries orchestration only — `case_id`, `phase_index`, `current_phase`, `gate_passed`, `final_output` (§17). Each phase has its own private substate (`PhaseState`, per-phase variants) for internal working memory, invisible to the main graph. This confirms and sharpens Section 10's Pattern 2 (Private Subagent State + Shared Parent State), with one correction: **what travels between phases does not travel on the parent state.** Phase outputs cross via the Store (§52a), not via per-phase output fields on `SupervisorState`. Fields named `define_output` / `measure_output` on the parent are the pattern this document previously showed and now retires — see "The Correct Implementation for Agent Improve" below.

---

### Architecture Target for Agent Improve — Confirmed and Sharpened

```
Main Graph (SupervisorState)          ── artifacts cross via the Store, not this state
  └── Orchestrator — deterministic gate-check on gate_passed + static edges
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

**The corrected architectural rule for the refactor:** the top-level `SupervisorState` orchestrator connecting the five phase subgraphs should very likely use simple static `add_edge` connections between them, since the phase sequence itself never varies. The recursive internal orchestrators *inside* each phase subgraph (the `understand → search → scope → validate` pattern) are where `Command`-based dynamic routing genuinely earns its complexity, because the step order there is authentically data-dependent.

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

The combined form is shown here as the general `Command` mechanism, **not** as Agent Improve's phase-sequencing pattern:
```python
def orchestrator(state: SupervisorState) -> Command:
    next_phase = decide_next_phase(state)
    return Command(
        update={"current_phase": next_phase},
        goto=f"{next_phase}_subgraph"
    )
```

> **This is not how Agent Improve sequences phases.** DMAIC order is fixed,
> so phase transitions are **static edges** — `add_edge("define", "measure")`
> — and `Command` routing is reserved for inside phase subgraphs where step
> order is genuinely data-dependent (§23, and the static-vs-dynamic criterion
> later in this section). Mixing static edges and `Command` from the same
> node executes both paths silently. Keep the snippet above as the mechanism
> reference; do not copy it into the supervisor.

**Nuance 2 — LLM-decided routing vs logic-decided routing**

The lab example uses an LLM call to decide the next worker. This is appropriate when the order genuinely depends on judgment about content (e.g. "researcher, then analyst, then writer" requires reasoning about what has been gathered so far within the team).

For Agent Improve's **main Orchestrator** routing between DMAIC phases, the decision is likely **deterministic, not LLM-based** — the next phase is simply the next phase in the DMAIC sequence once the current phase's gate has passed:

```python
def orchestrator(state: SupervisorState) -> Command:
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
    """Gate document for the Define phase. Canonical — see §82 for all five."""
    # Tier 1 — gate-required
    problem_statement: str
    project_scope: str
    goal_statement: str
    voc_summary: str
    # Tier 2 — rubric-recommended
    business_case: str
    team: str
    baseline_metric: str
    target_metric: str
    # Gate metadata
    computation_results: list[dict] = []
    acknowledged_gaps:   list[str]  = []
    citations:           list[dict] = []
    uploads:             list[dict] = []

# The orchestrator reads structured fields, never parses text
```

This directly resolves a risk in our current architecture — the orchestrator should never be parsing natural language output from a subgraph to decide what to do next. It reads validated typed fields.

> **This block previously carried a different, invented `DefineOutput`** — `ctqs: list[str]`, `confidence_score: float`, `gaps_identified: list[str]`. None of those are Define phase fields; the schema was written to illustrate the *mechanism* and was never reconciled with the actual phase. A second, also-wrong `DefineOutput` lived in §82 (`problem_statement`, `baseline_metric: float`, `scope`). Two definitions of the same class, neither matching the ratified fields, and both using `float` in contradiction of §17's Finding 3. **There is now one canonical definition per phase — all five are in §82** — and `MeasureOutput`, `AnalyseOutput`, `ImproveOutput` and `ControlOutput`, referenced throughout this document but never previously defined anywhere, are defined there too.

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

**Both are also in-graph only.** Neither carries data across a phase boundary in Agent Improve — that is Mechanism 3, the Store, added below after the case study.

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
# Parent — SupervisorState (§17), NOT DMAICState
class SupervisorState(TypedDict):
    messages:        Annotated[list[BaseMessage], operator.add]
    history:         Annotated[list[str], operator.add]
    case_id:         str
    phase_index:     int
    current_phase:   str
    gate_passed:     dict[str, bool]
    final_output:    Optional[dict]
    # NO define_output, NO measure_output — cross-phase artifacts never live here

class DefineState(TypedDict):
    messages: list
    understand_result: str       # PRIVATE — never crosses
    search_result: str           # PRIVATE — never crosses
    ctq_candidates: list         # PRIVATE — never crosses
    draft: DefineOutput          # written during the phase, not shared with parent

define_subgraph = build_define_subgraph(llm)
main_graph.add_node("define", define_subgraph)
main_graph.add_edge("define", "measure")             # static edge — fixed sequence

def define_output_mapper(state: DefineState, config) -> dict:
    case_id = config["configurable"]["thread_id"]
    store.put(("projects", case_id, "artifacts"), "define", state["draft"].model_dump())
    return {}

def measure_input_mapper(state, config) -> dict:
    case_id = config["configurable"]["thread_id"]
    define_artifacts = store.get(("projects", case_id, "artifacts"), "define").value
    return {"phase_context": build_context_from(define_artifacts)}
```

**This block replaces an earlier version that put `define_output` and
`measure_output` on the parent state and relied on shared key names to carry
them across the boundary.** That version contradicted CLAUDE.md §10.1
(`SupervisorState` is seven fields, orchestration only), §10.2 (cross-phase
data flows through the Store) and §1.2 (subgraph state updates are not
guaranteed to propagate to the parent). Because it was the block a reader
would copy as *the* reference implementation, it is corrected here rather
than annotated.

Everything inside `DefineState` stays genuinely private — which is what the
lab above failed to build. What leaves the phase leaves through the output
mapper, into the Store, under a namespace the next phase's input mapper
reads by name.

---

### Mechanism 3 — the Store (the one this section was missing)

Mechanisms 1 and 2 above are both **in-graph**: they move data between two
state schemas inside a single graph invocation. Neither survives a process
restart, and neither is what Agent Improve uses to cross a phase boundary.

| | Mechanism 1 — shared keys | Mechanism 2 — transformers | **Mechanism 3 — the Store** |
|---|---|---|---|
| Moves data | Parent ↔ child, same graph | Parent ↔ child, same graph | Phase → phase, across invocations |
| Durability | In-graph only | In-graph only | **Durable, checkpoint-independent** |
| Survives restart | No | No | **Yes** |
| Agent Improve uses it | Inside a subgraph | Inside a subgraph | **For every phase boundary** |

**The omission of Mechanism 3 from this section is how the drift happened.**
With only two in-graph mechanisms on the page, "shared key names" looked like
the natural answer to "how does Define's output reach Measure" — and the
reference implementation was written that way. The actual answer is the Store
(§52, §52a): `gate_apply_node` writes the approved gate document under
`("projects", case_id, "artifacts")`, and the next phase's input mapper reads
it. That write is also what makes the handoff survive the days or weeks
between one Belt session and the next, which no in-graph mechanism can do.

Mechanisms 1 and 2 remain correct for what they are — moving values between a
phase subgraph and its own internal nodes. They are simply not boundary
mechanisms.

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
| Task identifiers and execution status | `case_id`, `current_phase`, `gate_passed` in `SupervisorState` |
| Partial results and intermediate outputs | `DefineOutput`, `MeasureOutput` Pydantic models — held in the Store under `("projects", case_id, "artifacts")`, not on `SupervisorState` |
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

**Two-node pattern** for HITL gates — **ADOPTED**:
```
gate_review_node     → fires interrupt(), presents validated fields, collects decision
        ↓
gate_apply_node      → applies corrections, runs the policy advisory,
                       Commands to the next step or back to the grader
```

This is more precise than what §2 and §12 originally captured — the interrupt logic splits into collection and application as two distinct nodes, not one combined gate node. §2's nine-step pattern now uses this shape.

**Checkpointer — superseded.** This section originally said `InMemorySaver` for dev, `PostgresSaver` for production. The ratified position is the phased approach: `AzureBlobCheckpointSaver` during the refactor, `PostgresSaver` post-refactor, and `InMemorySaver` at no stage. See §1.

---

### Thread ID and Checkpoints in a Nested Orchestrator/Subagent Architecture

A precision not previously made explicit: in a distributed architecture where subagents have their own private state and internal orchestration, **does each subagent get its own checkpoint stream, separate from the main graph?**

**The relationship between the three concepts:**
```
State        = the data itself (what is in the clipboard right now)
Checkpoint   = a saved SNAPSHOT of that state at a specific point in time
Thread ID    = the LABEL that groups all checkpoints belonging to one conversation/project
```

> ### ⚠️ CORRECTION — The per-subgraph `thread_id` model below is WRONG
>
> This subsection originally concluded that each phase subgraph should be compiled with its own checkpointer and invoked under its own `thread_id` (`IMPR-2026-E9D-define`, `IMPR-2026-E9D-measure`). **That is incorrect**, and it is corrected against official documentation verified during the review.
>
> **What the documentation actually says:**
> - LangChain support docs: *"When using subgraphs, only the parent graph should have a checkpointer to avoid duplicate storage and state persistence issues."*
> - DeepWiki source analysis of langgraph: *"All checkpoints for both the parent and all subgraphs share the same thread_id but differ in checkpoint_ns."* And: *"When [checkpointer is] None, the subgraph checkpoint writes go through the same BaseCheckpointSaver as the parent, distinguished by checkpoint_ns."*
> - LangChain persistence docs: *"When a subgraph updates state, the parent graph may not see the changes immediately. This is because each subgraph manages its own checkpoint namespace. Fix: Use shared state via Store for data that needs to cross graph boundaries."*
>
> **The correct model:**
> ```
> One project thread_id:  "IMPR-2026-FS1"
> One checkpointer:       on the parent graph ONLY
> Auto checkpoint_ns:     LangGraph manages per-subgraph namespacing itself
> Store:                  cross-phase artifacts via AzureBlobStore (§52a)
> ```
>
> **The concern that motivated Option A is real and is satisfied anyway.** Subgraph-internal interrupts *do* need to persist across a server restart. They do — the parent's checkpointer handles them, namespaced by `checkpoint_ns`. Option A was solving a real problem with the wrong mechanism.
>
> *This was corrected three times during the review — in §23, then §19, now here. It is definitively settled.*

**The two options as originally framed** (retained so the reasoning is legible):

**Option A — subgraph compiled with its own checkpointer, own `thread_id`** ❌ WRONG
```python
# DO NOT DO THIS — causes duplicate storage and state persistence issues
define_subgraph = define_builder.compile(checkpointer=checkpointer)
# invoked with thread_id = "IMPR-2026-E9D-define" — a SEPARATE checkpoint stream
```

**Option B — subgraph mounted as a node inside the parent, no checkpointer of its own** ✅ CORRECT
```python
define_subgraph = define_builder.compile()               # no checkpointer
main_graph.add_node("define_subgraph", define_subgraph)
main_graph_compiled = main_graph.compile(
    checkpointer=checkpointer,                            # parent only
    store=store,
)
```

The original objection to Option B — *"the subgraph runs as one atomic unit; its internal steps are not individually checkpointed; a crash mid-subgraph requires re-running from the start"* — is **factually wrong**. LangGraph assigns the subgraph its own `checkpoint_ns` within the shared `thread_id`, and its internal supersteps *are* individually checkpointed under that namespace. There is no atomicity penalty and no lost interrupt state.

**The correct architecture:**
```
Main Graph
  thread_id:    "IMPR-2026-FS1"                 ← ONE, for the whole project
  checkpointer: AzureBlobCheckpointSaver        ← ONE, on the parent only
                (→ PostgresSaver post-refactor)
  store:        AzureBlobStore                  ← ONE, on the parent only
                (→ PostgresStore post-refactor)

  Define Subgraph      compiled WITHOUT a checkpointer
    checkpoint_ns:     auto-managed by LangGraph
    own internal HITL interrupts — fully recoverable via the parent's saver

  Measure Subgraph     compiled WITHOUT a checkpointer
    checkpoint_ns:     auto-managed by LangGraph
```

**Version floor:** LangGraph 1.2.6 fixed a regression where nested subgraphs were not inheriting the parent `checkpoint_ns` correctly. This mechanism requires 1.2.6+; the upgrade target is 1.2.10 (§79).

**The parent still only sees the validated final result:**
```
SupervisorState (parent, thread_id="IMPR-2026-FS1")
  current_phase, phase_index, gate_passed                 ← orchestration only

PhaseState (subgraph, checkpoint_ns auto-assigned)
  coaching_plan, field_index, draft, artifacts, step_log  ← private working memory,
                                                             never crosses the boundary

AzureBlobStore  ("projects", "IMPR-2026-FS1", "artifacts")
  "define": {...}                                          ← how artifacts actually reach
  "measure": {...}                                            the next phase
```

The boundary contract rule (typed Pydantic outputs only) still holds, and the subgraph's checkpoint history remains genuinely private. What changed is the *mechanism* for privacy — namespacing rather than separate threads — and the *carrier* for cross-phase data — the store rather than parent state.

**Summary:**
```
One project (Belt's case)   = one thread_id, full stop
Each phase subgraph         = its own AUTO-MANAGED checkpoint_ns — you do not name it
One checkpointer            = on the parent graph only; subgraphs compile without one
Parent state                = orchestration only; no artifacts, no gate documents
Cross-phase artifacts       = via the Store (§52a), not parent state, not shared keys
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

**This is the case for every DMAIC phase.** Each phase has failure modes, needs a quality gate (§42, §68), needs HITL (§2), and uses a different tool subset (§39). This settles the question of whether Agent Improve's phases should be prompt-sequenced or full subgraph nodes — unambiguously: full subgraph nodes.

Note the decision rule cuts the other way at the top level: phase *sequencing* is simple, reliable, and non-branching, so it uses static edges rather than a reasoning node. Same rule, opposite answer, because the question is different.

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
- `SessionStart` — inject current git state, refactor step, dependency versions
- **`PreToolUse`** — check every file write against the deprecated-pattern registry; `exit 2` blocks the write **before** it lands
- `Stop` — end-of-session compliance summary

**Critical implementation detail:** `exit code 2` is mandatory for blocking — `exit 1` is silently non-blocking, the most common implementation bug.

> **Correction:** this section originally specified `PostToolUse` for the write check. `PostToolUse` fires *after* the file is on disk and cannot block. The implemented hook uses **`PreToolUse`**, matched on `Write|Edit|MultiEdit`. See §86 for the verified mechanics of all four hook events.

**On MCP as a governance layer — removed.** The original version of this list included Context7, GitHub MCP, and Playwright MCP servers. Per §39, MCP is out of scope for AgentLean. Root cause #2 above (code generated from training memory rather than current documentation) is instead addressed by the `/verify-current-version` skill (§45, Gap 27 CLOSED), which fetches live version and changelog information at Layer 2.

**The mental model:** CLAUDE.md persuades, skills structure, hooks enforce. All three layers must coexist — none alone is sufficient.

---

### Correct Division of Labor — Tool Usage Going Forward

| Tool | Use For | Why |
|---|---|---|
| Claude.ai Chat (Desktop) | Architecture thinking, gap analysis, concept learning, building reference docs | Has cross-session memory about you and the project; no codebase access |
| Claude Code in VS Code | All implementation | Full codebase access, runs code and tests, reads CLAUDE.md, skills, and hooks |

**The anti-pattern to avoid:** using chat to draft implementation prompts that get copy-pasted into Claude Code. This recreates the original problem — design happens without codebase visibility, execution happens without the originating context.

**The bridge mechanism:** a short "session briefing" document (current gaps, target architecture reference) maintained in chat and pasted into Claude Code at the start of implementation sessions — until native cross-tool project memory exists. This EDUCATIONAL.md serves exactly this bridging function.

---

### Gap Register Addition

**Gap 25 — Version drift risk. CLOSED.** Implementation patterns throughout this document and in the original build used pre-1.0 LangGraph syntax (plain dict returns, externally wired `add_conditional_edges`, `set_entry_point()`). All are now in the deprecated-pattern registry the `PreToolUse` hook enforces, and `/verify-current-version` (§45) replaces the Context7-MCP idea for fetching live documentation.

**Gap 26 — No governance enforcement layers. CLOSED.** All three layers exist for Agent Improve as of commits 0.5.0–0.5.5: CLAUDE.md and ARCHITECTURE.md (Layer 1), `/verify-current-version` (Layer 2), and the `SessionStart` + `PreToolUse` hooks (Layer 3). See §45 for the implementation and §86 for the verified hook mechanics.

---

### Full Reconciliation of §44 Against the Ratified Architecture

*This section is the refactor blueprint, so every one of its claims was checked. The table records the verdict on each.*

| §44 claim | Verdict |
|---|---|
| Static edges for the DMAIC phase sequence | **Correct — ADOPTED.** The Global Planner is deterministic logic reading `gate_passed`, not an LLM call. `add_edge("define", "measure")` and so on. |
| `Command` routing inside phases | **Correct — ratified** |
| Per-subgraph `thread_id`s (Option A) | **WRONG — corrected** to one `thread_id` + auto `checkpoint_ns`. Web-verified against Tier 1 sources. |
| Shared key names (Mechanism 1) for boundary crossing | **Compatible.** Use alongside the store: shared keys for in-graph communication, store for durability and cross-case retrieval. |
| Explicit transformer functions (Mechanism 2) for boundary crossing | **Compatible.** The boundary mappers in §18 are the same concept. |
| Two-node HITL pattern (`review` → `apply_decision`) | **Refinement — ADOPTED.** More precise than §2's original framing. |
| `InMemorySaver` dev / `PostgresSaver` production | **Stale.** Superseded by the phased checkpointer decision (§1). |
| Typed Pydantic boundary outputs (`DefineOutput`, `MeasureOutput`) | **Correct — ratified** in §18 |
| Prompt sequencing vs real nodes decision test | **Correct.** Phases unambiguously need full subgraph nodes. |
| `Command(graph=Command.PARENT)` for subgraph-to-parent routing | **Correct — preserved** as reference |
| Send API for dynamic parallel worker creation | **Correct — preserved** as reference for the future debate subgraph (§22, v2.2) |
| Static vs dynamic routing criterion | **Correct — preserved.** *"Could this transition vary at runtime?"* = dynamic. *"Always exactly once in this order?"* = static. |
| Never mix static edges and `Command` from the same node | **Critical rule — preserved.** Both paths execute silently if mixed. |
| Root cause analysis (four reasons for the debt) | **Correct — preserved.** Still the foundational diagnosis. |
| Three governance layers | **Correct — implemented** (§45, Gap 27 CLOSED) |
| Division of labour (Claude.ai for architecture, Claude Code for implementation) | **Correct** |
| MCP references (Context7, GitHub, Playwright) | **Out of scope** per §39. Removed from the governance layers; retained as knowledge in §57–§65. |
| Course lab case study (the failed subgraph demo) | **Correct — valuable warning.** Preserved as documentation of what *not* to copy from the course. |

**Two adoptions from §44 into the ratified architecture:**

1. **Static edges between phase subgraphs.** This sharpens §5's Global Planner: it is not an LLM reasoner for phase sequencing, it is a deterministic gate-checker.
2. **Two-node HITL pattern.** §2's step 3 is `gate_review_node`; steps 5–7 are processed by `gate_apply_node`. Cleaner separation of collection from application.

---

### External Alignment — Anthropic's Planner / Generator / Evaluator (March 2026)

*Added August 2026, when the trusted-sources table was updated (§45). Source: `anthropic.com/engineering/harness-design-long-running-apps`, March 2026.*

> **Scope note on this source.** The March 2026 post is a **specific research
> write-up on long-running coding harnesses**, not a general restatement of
> Anthropic's agent architecture guidance. An earlier framing here described it
> as superseding the December 2024 "Building Effective Agents" post outright,
> which claims more for it than the post claims for itself. The comparison
> below still holds and is still worth recording — the convergence is real —
> but treat it as one well-evidenced study whose problem domain is adjacent to
> ours, not as a specification we are conforming to.

This blueprint was derived from the Agent Resolve diagnosis and the Edureka course material, not from Anthropic guidance. It is worth recording that Anthropic independently arrived at the same three-role decomposition for long-running agent applications, because convergence from a different starting point is stronger evidence than agreement would have been.

**The mapping is close to one-to-one:**

| Anthropic role (Mar 2026) | Our component | Documented in |
|---|---|---|
| **Planner** — decides what to do next; does not do the work | `phase_planner` — structured plan: focus field, next action, retrieval strategy | §5, §11, §44 |
| **Generator** — does the work; does not decide strategy | `phase_executor` — `create_agent` with the phase's tool subset | §5, §11, §42 |
| **Evaluator** — judges the output against a standard; separate model call | `DMAICGraderMiddleware` — per-criterion rubric verdict at temperature 0.1 | §42, §68 |

**What the post adds that we did not already have:**

- **Ablation discipline.** The three-agent architecture was tested *against a solo agent* rather than assumed better. We have not done this. Our Planner-Executor split is justified on inspectability and testability grounds (§5), which is a real argument, but it is not a measured one. **This is the natural first experiment for the §75 evaluation dataset** once it is populated: run the same coaching turns through a fused planner-executor and compare. If the split does not measurably help, we would at least know what we are paying for it.
- **The Evaluator is a separate call, not a self-check.** Our grader already satisfies this — it is middleware with its own model role and its own temperature (§42, §4.7 of CLAUDE.md). Worth noting because the tempting simplification, asking the executor to grade its own output, is the specific thing both sources rule out.

**Where the mapping stops.** The three roles map onto our **Level 2** only. At Level 1 there is no Planner in this sense: **phase sequencing is a deterministic gate-check on `gate_passed`, not a model call** (the first adoption above). DMAIC order is fixed by the methodology, so there is nothing to reason about — spending a model call to re-derive a constant would be cost without inspectability. Read the table as a Level 2 correspondence, not a whole-system one.

**No change to the ratified architecture follows from this note.** It is corroboration plus one open experiment (the ablation), recorded so the blueprint's provenance is honest: we did not design from this post, and we should not retrofit the claim that we did.

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
1. Fetch current LangGraph version and changelog from live documentation
2. Fetch current LangChain / LangSmith / deepagents / Anthropic / Langfuse equivalents
3. Compare against patterns about to be used in the upcoming decision
4. Output: "Confirmed current" or "WARNING: pattern X is deprecated as of version Y, use Z instead"
```

*The original design routed these lookups through Context7 MCP. MCP is out of scope (§39); the implemented skill fetches from the Tier 1 sources directly. The mechanism is unchanged — only the transport.*

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

### Mechanism 2 — Hook: PreToolUse Drift Detection in VS Code

A Hook is automatic and deterministic — it fires regardless of what Claude Code "decides" to do, closing the gap that Skills leave open (Skills can simply not be invoked).

**Correction (July 2026):** an earlier draft of this section documented this as a PostToolUse hook. Verification against current Claude Code hooks reference during the Step 0.5 scaffold build showed PostToolUse cannot block writes — it fires AFTER the tool call completes, meaning the file is already on disk when the hook runs, and exit code 2 only signals an error to Claude in the next turn. The correct event for pre-write blocking is PreToolUse matched on Write|Edit|MultiEdit. Exit code 2 there is fed back as a blocking error before the write happens. See Section 86 for the full verified hook mechanics.

```python
# .claude/hooks/pre-tool-use-drift-check.py
# Registered as PreToolUse matcher: Write|Edit|MultiEdit
# Fires BEFORE each file write; exit 2 blocks the write from happening

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

**Second critical implementation detail (learned during scaffold build):** deprecated-pattern regexes are stored in a YAML registry read by the hook at runtime. Patterns containing both single and double quotes (e.g. matching either 'next' or "next" in dict keys) must use doubled-embedded-quote encoding — `["\''] ` — not a bare embedded quote. A bare quote closes the YAML scalar early and produces a ParserError at load time. Because the hook fail-softs on load error (to avoid blocking all writes when the config is broken), a malformed pattern registry SILENTLY DISABLES all drift checks. Validate the YAML loads before assuming the hook is armed.

**Third critical implementation detail (learned on Windows):** hook scripts writing non-ASCII characters (── ✓ ⚠ — §) to stdout or stderr must call `sys.stdout.reconfigure("utf-8")` and `sys.stderr.reconfigure("utf-8")` before any output. Windows consoles with legacy code pages otherwise raise UnicodeEncodeError, which the hook's broad exception handler swallows — resulting in empty stderr fed back to Claude, so the block is registered but the pattern name and message are lost. Reconfigure at the top of every hook script.

**What this catches that the Skill above does not:** the Skill is checked before design decisions. The Hook is checked on every single file write, catching drift introduced during implementation even when the original design was correct — for example, Claude Code falling back to a familiar pre-1.0 pattern out of habit while writing code, even after the architecture was correctly designed with Command-based routing.

**Registry additions identified during this review.** The following deprecated patterns were confirmed during the section-by-section review and belong in the YAML registry alongside the existing entries:

| Pattern | Replacement | Source |
|---|---|---|
| `MultiQueryRetriever` | Multi-query inside the `rag_lookup_*` tools | §32 |
| `EnsembleRetriever` | RRF inside the `rag_lookup_*` tools | §33, §35 |
| `OutputFixingParser` | Native structured output | §29, §82 |
| `ConversationSummaryMemory` | `SummarizationMiddleware` | §36, §50, §52 |
| `ConversationEntityMemory` | Typed state fields + Store | §36, §50, §52 |
| `VectorStoreRetrieverMemory` | `rag_lookup_case_history` + Store | §36, §50, §52 |
| `create_react_agent` | `create_agent` from `langchain.agents` | §50 |
| `from langgraph.prebuilt import` | `langchain.agents` | §50 |

**A registry caveat worth stating explicitly:** the registry guards *code*. Architecture documentation legitimately shows superseded patterns side by side with their replacements — that is the whole point of a "what this used to recommend, and why that is wrong now" subsection. Markdown under `agent-improve/` is therefore path-excluded for patterns where documentation must be able to name the deprecated form. Adding a pattern without considering doc paths makes the governance docs unwritable.

---

### Mechanism 3 — SessionStart Hook: Inject Current Context Automatically

```python
# .claude/hooks/session-start-context.py
# Fires automatically when a new Claude Code session begins

def inject_session_context():
    git_state    = read_git_head_and_working_tree()
    refactor_step = read_last_completed_and_next_step()
    versions      = compare_installed_against_latest([
        "langgraph", "langchain", "langsmith", "deepagents",
    ])
    return format_session_context(git_state, refactor_step, versions)
```

The implemented hook injects git HEAD and working-tree state, the last completed and next refactor step, and an installed-versus-latest comparison for each tracked dependency. Every Claude Code session therefore starts aware of where the work stands and whether the environment has drifted — without relying on anyone remembering to check.

*The original sketch called `query_context7(...)` for the latest version. That is replaced by a direct PyPI lookup (§39 — no MCP).*

---

### Mechanism 4 — Staying Current as a Human: Targeted Forum Monitoring

This is the human-side complement to the automated hooks. The goal is not generic browsing but **targeted monitoring of the specific sources where LangGraph/LangChain changes are announced first**.

**Ratified source tiers — UPDATED August 2026.** This replaces the ad-hoc source list this section originally maintained. One table, used by both the human habit and the `/verify-current-version` skill, so the two cannot diverge.

**What changed, and why it is not cosmetic.** The December 2024 *Building Effective Agents* post was the primary Anthropic reference throughout this review. It is now 19 months old, and Anthropic has published 14 engineering posts since — several of which directly evolve or supersede its guidance. It moves to historical foundation; the 2025–2026 engineering posts become Tier 1. Reviewing against a superseded primary source is the same failure mode as coding against a superseded API, one layer up: §50 catches stale library patterns, and nothing was catching stale *architectural* sources.

**Tier 1 — Primary (current, authoritative; check before any architectural decision)**

| Source | Date | Topic | Why it matters |
|---|---|---|---|
| `anthropic.com/engineering/effective-harnesses-for-long-running-agents` | Nov 2025 | Harness concept, context reset, session bridging | Reframes agents as "harness + model" — the harness (control plane) is the engineering, not the prompt. Directly relevant: DMAIC coaching is a long-running agent task. Defined in the Terminology Reference. |
| `anthropic.com/engineering/harness-design-long-running-apps` | Mar 2026 | Planner/Generator/Evaluator, ablation discipline | Three-agent architecture tested against a solo agent. Maps to our Planner/Executor/Grader — see §44. **A specific research write-up on long-running coding harnesses**, not general architecture guidance — weigh it as strong evidence from an adjacent domain, not as a spec. |
| `anthropic.com/engineering/managed-agents` | Apr 2026 | Brain/hands separation, scaling | Separating planning from execution at the infrastructure level. Confirms the Planner-Executor cascade (§5, §11). |
| `anthropic.com/engineering/how-we-contain-claude` | Jul 2026 | Containment, blast radius, security boundaries | Newest post. Containment architecture for Claude products. Relevant to hook security (§45, §86). |
| `anthropic.com/engineering/effective-context-engineering-for-ai-agents` | Sep 2025 | Context-window management as a first-class discipline | Directly relevant to `SummarizationMiddleware` (§36) and progressive skill disclosure (§84). |
| `anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills` | Oct 2025 | Agent Skills, SKILL.md spec | The spec §83 and §84 are built against. |
| `anthropic.com/engineering/demystifying-evals-for-ai-agents` | Jan 2026 | Eval design for agents | Directly relevant to the §75 evaluation dataset. |
| `anthropic.com/engineering/writing-tools-for-agents` | Sep 2025 | Tool design principles | Relevant to the 20 computation tools and 3 retrieval tools (§39). |
| `docs.langchain.com`, `reference.langchain.com`, `python.langchain.com` | Ongoing | Official LangChain / LangGraph / deepagents docs | API patterns, middleware, `create_agent`, structured output |
| `github.com/langchain-ai/*` (repos, issues, releases, changelogs) | Ongoing | Source of truth for code, versions, breaking changes | Version verification, bug fixes, feature status |
| `pypi.org` | Ongoing | Package versions and dependency data | Definitive version and dependency data |

**Tier 2 — Official publications (announcements, strategic context)**

| Source | Content type |
|---|---|
| `langchain.com/blog` | LangChain team feature announcements and design rationale |
| `anthropic.com/news/*` | Product announcements, enterprise case studies |
| `resources.anthropic.com` | Whitepapers, trend reports (2026 Agentic Coding Trends Report) |
| `claude.com/blog/*` | Claude-specific product blog |

**Tier 3 — Informed practitioner (cross-checked, cited)**

| Source | Content type |
|---|---|
| `marsdevs.com/guides` | Practitioner guides with Tier 1 citations |
| `deepwiki.com/langchain-ai/*` | Community wiki with source references |
| `agentpatterns.ai` | Pattern vocabulary crosswalk across frameworks |

**Downgraded — historical context (no longer primary)**

| Source | Date | Status |
|---|---|---|
| `anthropic.com/engineering/building-effective-agents` | Dec 2024 | **Historical foundation, and still sound.** The most-cited post in the industry; its core advice — *"find the simplest solution possible"*, the principle behind §42's Option B — remains valid and is not superseded. What the 2025–2026 posts add is *newer specific material* — the harness framing, the Planner/Generator/Evaluator study, context-reset discipline, ablation method — which is why they are checked first. Age is the reason for the ordering, not a claim that this post has been refuted. |

**Excluded.** Stack Overflow, Reddit, Medium, Dev.to — unverified unless linking directly to Tier 1 content.

**Still referenced, outside the tiers.** These are cited elsewhere in this document and remain valid for their specific topic, but are not decision-time checks: `anthropic.com/engineering/multi-agent-research-system` (production multi-agent design; the cascading-behaviour-changes warning), `anthropic.com/engineering/advanced-tool-use` (programmatic tool calling), `anthropic.com/news/finance-agents` (structured domain agents — DMAIC coaching is structurally similar to financial auditing), and `docs.anthropic.com` (API docs, cookbooks, runnable examples).

**Verification discipline going forward.** Before any architectural decision, check the `anthropic.com/engineering` post index and the `pypi.org/project/langgraph` release history. **These two sources move fastest and have the most impact on our design.** Until the weekly-update skill exists, do a manual pass at the start of each Claude Code session and each claude.ai review session.

**The practical habit:** rather than browsing reactively, `/verify-current-version` pulls from these sources at decision time — turning passive monitoring into an active part of the architectural workflow rather than a separate habit to remember.

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
patterns                              PreToolUse hook blocks
                ↓                     deprecated pattern writes
Hand to Claude Code                            ↓
                                     Clean, current-syntax code
```

---

### Why All Four Mechanisms Are Necessary Together

This restates and sharpens the "all layers must coexist" principle from Section 44, now with concrete implementation:

- **Without the Skill** — architectural decisions get made on stale assumptions before any code is written
- **Without the PreToolUse Hook** — even a correct design can drift during implementation through habit or autocomplete suggesting old patterns
- **Without the SessionStart Hook** — every new session starts blind to whether the environment itself has drifted
- **Without human source monitoring** — the automated checks only catch drift against what is already documented; genuinely new patterns and emerging best practices appear in Tier 1 and Tier 2 sources before they reach a version changelog

### Gap Register Addition

**Gap 27 — CLOSED (July 2026, verified 2026-07-03).** Anti-drift mechanisms implemented as the Step 0.5 anti-drift scaffold, commits 0.5.0 through 0.5.5 (git range de875ba..9d065a0). Specifically: `/verify-current-version` skill at `.claude/skills/verify-current-version/SKILL.md` (commit b9aec22), PreToolUse deprecated-pattern hook at `.claude/hooks/pre-tool-use-drift-check.py` (commit ad5bbf9, registered in `.claude/settings.json` at commit 0ddcff9), SessionStart context-injection hook at `.claude/hooks/session-start-context.py` (commit 9ea3e2a). Human-side source monitoring embedded in the skill's source list. Verified operational by smoke test on 2026-07-03: the SessionStart hook injects git HEAD and refactor step into every session, and the PreToolUse hook blocks writes containing deprecated patterns with exit code 2.

The PostToolUse mechanism originally documented above is corrected to PreToolUse (see the Mechanism 2 correction).

### One Known Governance Contradiction

`pattern-2-with-structured-output` in the registry blocks the builder-style structured-output call and cites "CLAUDE.md §4.6" — **a rule that does not exist**. CLAUDE.md §4.3 currently *mandates* that same call. So the constitution requires a pattern the hook blocks, on the authority of a section that was never written.

The substance is resolvable: `response_format=` on `create_agent` (§82) is preferred **for agents**, but the ratified design also makes plain structured-output calls inside tools and middleware (§32, §33, §37, §42, §48, §68) where `response_format=` does not apply. The rule needs to distinguish those two cases.

**Action required at the CLAUDE.md v2.2 rewrite:** author the real §4.6, scope it to agent calls, and update the registry message to cite it. Until then the registry path-excludes `agent-improve/**/*.md` so architecture documentation can name both forms. See §86 for the full hook-mechanics reference this contradiction sits inside.

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
    → LangGraph checkpointer
      (AzureBlobCheckpointSaver during the refactor → PostgresSaver post-refactor, §1)
    → scoped by thread_id
    → plus SummarizationMiddleware for compression (§36)

Cross-session memory (replaces ConversationEntityMemory, VectorStoreRetrieverMemory):
    → LangGraph BaseStore
      (AzureBlobStore during the refactor → PostgresStore post-refactor, §52a)
    → scoped by project / entity namespace, NOT thread_id

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

**Gap 25 is now CONFIRMED, not hypothetical.** Two specific sub-findings, both since addressed:

- **Gap 25a — CLOSED.** `ConversationSummaryMemory`, `ConversationEntityMemory`, `VectorStoreRetrieverMemory` confirmed deprecated, scheduled for removal in LangChain 2.0. Replaced by the Checkpointer (session-scoped) + BaseStore (cross-session, cross-case) split — see §36, §52, §52a.
- **Gap 25b — CLOSED.** `create_react_agent` confirmed deprecated in LangGraph v1, replaced by `create_agent` from `langchain.agents`. Applied throughout §42, §48, and §51.

All three corrections in this section are addressed in the ratified architecture:

| Correction | Where it is resolved |
|---|---|
| Deprecated memory classes | §36 (`SummarizationMiddleware`), §52 and §52a (Checkpointer + Store split) |
| `create_react_agent` → `create_agent` | §42 (middleware architecture on `create_agent`), §48, §51 |
| "Verify before migrating" | §45 — the `/verify-current-version` skill, Gap 27 CLOSED |

Both patterns are now in the deprecated-pattern registry the PreToolUse hook enforces (§45), so this correction is mechanically enforced rather than remembered.

*The honest nuance recorded above — that `create_agent`'s message-history rewriting was reported as a regression, and that the deprecation message initially pointed at a function that did not yet exist — is exactly the failure mode `/verify-current-version` exists to catch. Keep it. It is the best worked example in this document of why the skill is a discipline checkpoint rather than background reading.*

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

**Resolution: Option A, because the tension dissolves.** §36's ratified design does not put facts into the summary at all. Facts live in typed fields that `messages[]` compression never touches:

- `artifacts` on `PhaseState` (§18), written to the store at gate approval (§52a)
- The `before_model` middleware prepends that structured state to every prompt (§38 Gap 22b)

So prose summarisation of *conversational* history is fine — that is what conversation is. The structured-versus-prose argument was never about the summary format; it was about facts not living in `messages[]` in the first place. With that fixed, `SummarizationMiddleware` can be used as shipped, with the ratified configuration:

```python
SummarizationMiddleware(
    model="azure/operational-model",       # gpt-4o-mini for cost
    trigger=("tokens", 100_000),           # ~78% of gpt-4o's 128k window
    keep=("messages", 20),                 # preserve the last 20 turns raw
)
```

*Note the parameter names: current LangChain uses `trigger` and `keep`; the `max_tokens_before_summary` / `messages_to_keep` form in the example above is the earlier API. Verify against the installed version.*

### Deep Agents' `SummarizationMiddleware` Variant — An Even Closer Match

A more specific finding: Deep Agents (LangChain's "batteries-included" harness, built on `create_agent`) ships a **wrapped version** of `SummarizationMiddleware` with capabilities directly relevant to Agent Improve's multi-week DMAIC sessions:

> "Backend offload of evicted history. Evicted messages are appended to /conversation_history/{thread_id}.md ... before the summary replaces them, and the summary embeds that path so the agent can re-open it via read_file ... LangChain drops evicted messages with no recovery path [in the base version]."

The base middleware permanently discards old messages once summarised; the Deep Agents variant offloads evicted history to a retrievable file.

**Not adopted, and the concern is already covered.** Adopting it would mean adopting deepagents, which §42 rejected on dependency-risk grounds. More importantly, the data-loss risk it addresses does not apply to us: nothing load-bearing lives only in `messages[]`. Artifacts go to the store (§52a), decisions and open items are typed state fields (§17), and every validation and fallback attempt is written to `step_log` (§18). The audit trail is built from those, not from raw conversation history.

Worth revisiting if deepagents reaches 1.0 and we migrate the custom middlewares (§84) anyway — at that point the offload comes for free.

### `HumanInTheLoopMiddleware` — Evaluated, and Deliberately Not Used

> **Do not use this middleware for Agent Improve's gates.** Read this subsection for the API and for the bug evidence; the ratified HITL mechanism is graph-level `interrupt()` plus `Command(resume=...)` (§2). The two confirmed bugs below hit exactly our use case — Belt field edits inside phase subgraphs — and only `approve` is reliable there. Building on graph primitives avoids the bug entirely, at the cost of a little more code.

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

**This finding decided the mechanism.** The architecture depends on each phase subgraph owning its own interrupt (§44: *"each phase subgraph owns its own interrupt (quality gate); the main orchestrator only routes based on results"*). Bug 2 says edit and reject are unreliable in exactly that position. Bug 1 says a Belt's correction can be silently re-overwritten by the agent re-attempting its original call — which in DMAIC terms means an approved value being replaced by the AI's rejected extraction, without anyone seeing it happen.

Neither is acceptable in a system whose entire value proposition is that the Belt is accountable for what gets saved. There were three options — wait for fixes, restrict interrupts to the top level and lose per-phase gates, or build on graph primitives — and the third is the only one that keeps the architecture intact. §2's nine-step pattern uses `interrupt()` + `Command(resume=...)` directly.

### Gap Register Updates

**Gap 19 — CLOSED.** `SummarizationMiddleware` used as shipped, with the §36 configuration. The structured-versus-prose tension resolved by keeping facts out of `messages[]` entirely rather than by changing the summary format.

**Gap 2 — CLOSED, by a different mechanism than this section proposed.** The approve / edit / reject model is right and is preserved in §2's nine-step pattern. The *implementation* is graph-level interrupts, not `HumanInTheLoopMiddleware`.

**Gap 32 — CLOSED: verified, and avoided.** Both bugs are confirmed and both hit our use cases. Rather than gate the architecture on upstream fixes, the ratified design does not depend on the buggy paths. Re-evaluate only if a future version fixes both *and* there is a reason to prefer middleware over graph primitives.

*Cross-references: §2 (the ratified nine-step HITL pattern), §36 (`SummarizationMiddleware` configuration), §42 (why deepagents is not adopted), §80 (the six hooks all of this is built on), §84 (the complete middleware stack).*

---

## 86. Verified Claude Code Hook Mechanics

*New section, authored during the batch commit. §45 forward-referenced "Section 86 for the full verified hook mechanics" and the section was never written — this closes that reference. Web-verified against `code.claude.com/docs/en/hooks` at authoring time, and cross-checked against the hooks actually running in this repository. **Written from live documentation, not from memory** — that discipline is the entire point of the anti-drift system §45 describes.*

### Why This Section Exists

§44 and §45 built a three-layer governance system whose bottom layer — hooks — is the only one *guaranteed* to fire. Constitution documents can be forgotten as context fills. Skills have to be invoked. Hooks fire on system events regardless of what the model decides.

That guarantee is only as good as the mechanics being right. §45 shipped a real bug on exactly this point: the drift check was designed as `PostToolUse`, which cannot block a write. Getting hook mechanics wrong produces a governance layer that *appears* to be enforcing and is not — the worst failure mode available, because it is silent and it inspires false confidence.

### The Events That Matter for AgentLean

Claude Code exposes a large hook surface. Five events carry the governance weight here:

| Event | When it fires | Can it block? | What exit code 2 does |
|---|---|---|---|
| `SessionStart` | New session, or resume | **No** | stderr is shown only |
| `UserPromptSubmit` | Before Claude processes a prompt | **Yes** | Blocks the prompt and erases it |
| `PreToolUse` | **Before** a tool call executes | **Yes** | **Blocks the tool call** |
| `PostToolUse` | **After** a tool succeeds | **No** — the tool already ran | stderr is shown |
| `Stop` | When Claude finishes responding | **Yes** | Prevents stopping; conversation continues |

### The Correction §45 Needed

**`PostToolUse` cannot block a write.** It fires *after* the tool call completes, which means the file is already on disk when the hook runs. Exit code 2 at that point signals an error to Claude for the next turn — useful for telling the model something went wrong, useless for preventing it.

**`PreToolUse` is the correct event for write-blocking**, matched on `Write|Edit|MultiEdit`. Exit code 2 there is fed back as a blocking error *before the write happens*.

```
PostToolUse:  tool runs → file on disk → hook fires → exit 2 → Claude told after the fact
PreToolUse:   hook fires → exit 2 → tool never runs → file never written
```

This distinction is the whole difference between a guarantee layer and an audit layer.

### Exit Code Semantics — The Three Cases

| Exit code | Meaning | What Claude sees |
|---|---|---|
| **0** | Success | stdout is parsed for JSON output fields |
| **2** | **Blocking error** | **stderr is fed to Claude; stdout JSON is ignored** |
| Anything else | Non-blocking error | stderr appears in the transcript; execution continues |

**Exit code 1 is silently non-blocking.** This is the most common implementation bug in hook scripts, and it is silent in the worst way: the script runs, prints its warning, and the write proceeds anyway. A hook that uses `exit 1` looks correct in every log and enforces nothing.

Note the asymmetry at exit 2: **stdout JSON is ignored**. A hook that wants to both block *and* return structured output must choose — either exit 2 with a stderr message, or exit 0 with `permissionDecision: "deny"` in its JSON.

### Configuration Structure

Hooks are registered in `settings.json` under the event name, with an optional `matcher`:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/session-start-context.py\"",
            "timeout": 30
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write|Edit|MultiEdit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"$CLAUDE_PROJECT_DIR/.claude/hooks/pre-tool-use-drift-check.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

*This is the AgentLean configuration as it actually runs, not an illustration.*

**Scope precedence**, from broadest to narrowest:

| Location | Applies to | Shared? |
|---|---|---|
| `~/.claude/settings.json` | All projects | No — local only |
| `.claude/settings.json` | One project | **Yes — committed, and the right place for governance hooks** |
| `.claude/settings.local.json` | One project | No — gitignored |

Governance hooks belong in `.claude/settings.json` precisely because they are committed. A constitution that exists only on one developer's machine is not a constitution.

**`$CLAUDE_PROJECT_DIR`** resolves to the project root, which is what makes the hook path work regardless of the working directory a session starts in.

**Matchers** filter which tool calls fire the hook. For tool events the matcher tests `tool_name`. Simple strings match exactly or as an alternation list (`Write|Edit|MultiEdit`); anything containing other characters is treated as an unanchored regex.

### JSON Input — What a Hook Receives on stdin

Every hook receives a JSON envelope. Common fields:

```json
{
  "session_id": "abc123",
  "transcript_path": "/path/to/transcript.jsonl",
  "cwd": "/current/working/dir",
  "permission_mode": "default",
  "hook_event_name": "PreToolUse"
}
```

Tool events add `tool_name`, `tool_input`, and `tool_use_id`. `SessionStart` adds `source` — one of `startup`, `resume`, `clear`, `compact`, or `fork`.

**The `tool_input` shape differs per tool, and the drift check has to handle all three:**

| Tool | Field holding the content to check |
|---|---|
| `Write` | `content` |
| `Edit` | `new_string` |
| `MultiEdit` | every `edits[].new_string`, concatenated |

Checking only `content` would let every `Edit` through unchecked — a hole that stays invisible until someone notices deprecated patterns landing via edits but not via writes.

### JSON Output — The Richer Alternative to Exit Codes

Exit codes are the simple path. A hook can instead exit 0 and print structured JSON on stdout:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Deprecated pattern: MultiQueryRetriever",
    "additionalContext": "Use multi-query inside rag_lookup_methodology (see §32)."
  }
}
```

`permissionDecision` accepts `allow`, `deny`, `ask`, or `defer`. `updatedInput` can rewrite the tool arguments before execution. `additionalContext` injects context Claude sees without blocking.

For `SessionStart`, `hookSpecificOutput.additionalContext` is the field that injects context into the session — which is what the AgentLean session-start hook uses to surface git state, refactor step, and dependency versions.

Universal fields available on any event include `continue: false` with a `stopReason`, plus `suppressOutput` and `systemMessage`.

### Three Implementation Lessons Learned Building These

*Learned during the Step 0.5 scaffold build. Each one produced a hook that appeared to work and did not.*

**1. A malformed pattern registry silently disables all checks.**

The deprecated-pattern regexes live in a YAML registry the hook reads at runtime. Patterns containing both single and double quotes — matching either form of quoting in a dict key — must use doubled-embedded-quote encoding, not a bare embedded quote. A bare quote closes the YAML scalar early and raises a `ParserError` at load time.

Because the hook **fail-softs on load error** — deliberately, so a broken config cannot wedge every write in the repository — a malformed registry disables all drift checking with no visible symptom. **Validate that the YAML loads before assuming the hook is armed.** The fail-soft is correct; the silence is the hazard.

**2. Non-ASCII output on Windows silently swallows the message.**

Hook scripts writing box-drawing characters, tick marks, warning signs, or the section symbol to stdout or stderr must reconfigure both streams to UTF-8 before any output. Windows consoles with legacy code pages otherwise raise `UnicodeEncodeError`, which the hook's broad exception handler swallows — producing empty stderr fed back to Claude. The block registers, but the pattern name and remediation message are lost, so the model sees "blocked" with no reason and cannot self-correct.

**3. Fail-soft everywhere, deliberately.**

Both AgentLean hooks exit 0 on any internal error: unparseable stdin, missing config, invalid regex, unexpected exception. A hook bug must never wedge the developer. The trade-off is lesson 1 — fail-soft means failures are quiet — which is why the smoke test below is not optional.

### Verifying a Hook Is Actually Armed

A hook that is registered, syntactically valid, and doing nothing looks identical to a working one, until the day it should have blocked something and didn't. Verify explicitly:

1. **Config loads** — parse the YAML registry standalone and confirm the expected pattern count
2. **Hook fires** — attempt a write containing a known deprecated pattern; confirm it is blocked
3. **Message survives** — confirm the blocked response names the pattern and its remediation, not just "blocked"
4. **Both tool shapes** — test via `Write` *and* via `Edit`, since they carry content in different fields

AgentLean's hooks were smoke tested on 2026-07-03 against these checks (§45, Gap 27 CLOSED).

### A Governance Rule the Hooks Themselves Taught Us

**The registry guards code. Architecture documentation is not code.**

This document deliberately shows superseded patterns beside their replacements — "what this used to recommend, and why that is wrong now" is a section shape that recurs throughout, and much of the value lives there. A pattern added to the registry without considering documentation paths makes the governance documents unwritable: the file explaining why a deprecated class is deprecated cannot be written if writing its name is blocked.

Hence the `path_exclusions` for `agent-improve/**/*.md` on patterns whose deprecated form documentation must be able to name.

### The Known Contradiction — CLAUDE.md §4.3 vs §4.6

**`pattern-2-with-structured-output` blocks the builder-style structured-output call and cites "CLAUDE.md §4.6" — a section that does not exist.** CLAUDE.md §4.3 currently *mandates* that same call. The constitution requires what the hook forbids, on the authority of a rule nobody wrote.

The substance is resolvable. §82 establishes that `response_format=ProviderStrategy(Schema)` is preferred **for agents built with `create_agent`**. But the ratified design also makes plain structured-output calls inside tools and middleware — query variant generation (§32, §33, §37), grader verdicts (§42), constraint verdicts (§68) — none of which are agents, and where `response_format=` has nothing to attach to. The rule needs to distinguish the two cases; the current pattern does not.

**Action at the CLAUDE.md v2.2 rewrite:** author the real §4.6, scope it to agent calls, correct §4.3, and update the registry message to cite it. Until then the markdown path exclusion above keeps the governance documents writable.

This is worth recording as more than a bug. A governance rule pointing at a non-existent authority is a specific failure mode of layered governance: the layers can drift from one another, and that drift is not visible from inside any single layer. `/verify-current-version` catches drift between our patterns and the *framework*. Nothing yet catches drift between the constitution and the hooks — the same class of problem §45 exists to solve, one level up.

*Cross-references: §44 (three governance layers), §45 (the four anti-drift mechanisms, Gap 27 closure), §82 (ProviderStrategy — the substance of the contradiction above), §83 (Agent Skills — the Layer 2 file format).*

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

### Mapping to Agent Improve — Ratified Status

| Role | Original assessment | Ratified state |
|---|---|---|
| Coordinator | "exists implicitly" | ✅ **Global Planner + Global Executor** (§5, §20) — deterministic gate-checker plus static edges |
| Decision | "MISSING" | ✅ **Partially closed, distributed by design.** Quality evaluation → `DMAICGraderMiddleware` (§42) and the four-layer stack (§68). Conflict resolution → mid-phase contradiction detection (§38). |
| Observer | "MISSING" | ⏸ **Deferred — §87 item 14.** Not a per-project coaching component. |
| Worker | "exists" | ✅ **Phase subagents** with their own Planner-Executor pairs (§5, §20, §23) |

The Decision Agent role turned out **not** to want to be an agent. Splitting it across middleware and a validation stack is better than a separate node: the grader fires where the AI's output is produced, the constraint check fires at the gate, and the conflict detector fires mid-turn. A single Decision Agent would have to be invoked at three different points anyway.

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

**Deferred — §87 item 14.** This is not a per-project coaching component, and it requires production traffic across multiple concurrent projects before its pattern analysis would produce anything meaningful. Building it against one or two demo projects would produce noise dressed as insight. Promotion trigger: multiple concurrent DMAIC projects in production generating enough traffic for pattern analysis.

---

### The Complete Target Architecture

```
Coordinator (Global Planner + Global Executor)          ← §5, §20 — in scope
  — deterministic gate-checker reading gate_passed
  — static edges between phase subgraphs

Decision responsibilities — DISTRIBUTED, not a separate agent  ← in scope
  — gate quality        → DMAICGraderMiddleware (§42), Layer 2d
  — constraint checks   → §68 Layer 2c
  — field presence      → DMAICGateValidator (§48), Layer 2b
  — coherence           → §69, Layer 2a, every turn
  — conflict resolution → mid-phase contradiction detection (§38)

Worker Agents (Phase Subagents)                          ← §23 — in scope
  — Define, Measure, Analyse, Improve, Control
  — each a subgraph with its own PhaseState and tool subset

Observer Agent                                           ← §87 item 14 — deferred
  — completion rates across all Belts
  — coaching quality drift
  — system health metrics
  — insights feeding back into eBook content
```

### Why This Matters
Without the decision responsibilities, nobody in the system evaluates whether a gate *should* pass beyond field presence. That is closed. Without an Observer, nobody tracks system-wide health and patterns across all Belts and projects — that remains open, deliberately, until there is enough traffic for the answer to mean anything.

### Gap Register
**Gap 24 — partially closed.** The Decision Agent role is implemented, distributed across the grader (§42), the four-layer validation stack (§68), and mid-phase conflict detection (§38). The Observer Agent role is deferred to §87 item 14.

---

# PART 9 — MCP KNOWLEDGE

*Not implemented — retained as protocol pedagogy. MCP is architecturally excluded from Agent Improve, Agent Resolve, and Agent Flow (§39); see the banner below and §63 for the evaluation and the rejection.*

---

---

# Sections 57–65 — MCP: Knowledge Only

> **MCP is permanently out of scope for Agent Improve, Agent Resolve, and Agent Flow (§39).** Not deferred. Not a roadmap item. Architecturally excluded.
>
> The nine sections that follow are retained deliberately, as protocol pedagogy. Understanding MCP is worth having — it is the standard for cross-organisation tool sharing, and the reasoning for excluding it only holds because of facts about *our* situation (one team, one stack, all Python, all LangChain 1.x) that could change for a different product.
>
> **What replaces MCP here:** the `@tool` decorator for tool composition (§39), three `rag_lookup_*` tools for retrieval (§32, §33), 20 per-phase computation tools (§39), and Python imports from shared modules for cross-agent tool sharing. Users upload their data via `improve_evidence_index`; the coach's job includes teaching them what to collect and how.
>
> **Three sections carry content that outlives the MCP framing** and are worth reading even though MCP is out:
> - **§60** — the internal-tool boundary and the hybrid planner + reactive tool pattern. Confirms the ratified architecture; retained as an architectural reference, not just MCP knowledge.
> - **§64** — the structured error schema. Applies to Azure OpenAI and Azure AI Search failures regardless of protocol; ratified in §66/§67.
> - **§65** — cache key design, TTL, and invalidation. Applies directly to the Azure Redis Cache at §67 Level 3.
>
> **§63** is rewritten: it was a planning document for an AgentLean MCP server; it is now the record of the evaluation and the rejection.

---

## 57. CORRECTION — Course Slide Mischaracterises MCP as "Agent-to-Agent" Protocol; It Is Agent-to-Tool/Data

*Source: Direct discussion, verified against the official MCP specification site, an arXiv survey paper, Anthropic's own framing, and multiple independent technical sources, all in agreement. This is a clear, confirmed correction to course material — not an ambiguous edge case.*

*Status: knowledge-only (§39). Kept as-is — a valuable correction to course material, and the distinction it draws (agent-to-tool, not agent-to-agent) is worth understanding regardless.*

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

*Status: knowledge-only (§39). Kept as-is — a valuable correction to course material.*

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

*Status: knowledge-only (§39). Retained in full because it is accurate and current — useful if Agent Flow or a future product ever needs to expose tools across an organisational boundary. Not built for Agent Improve.*

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

> **Status: architectural reference, not merely MCP knowledge.** This is the section in the MCP group that survives §39 intact. The internal-tool boundary it draws, and the hybrid planner-plus-reactive-tool pattern (Option C) it selects, are both ratified. Read it for the architecture; the MCP contrast is now purely illustrative, since there is no external side of the boundary to contrast with.
>
> **Tool names below have been updated to the canonical names:** `retrieve_methodology` → `rag_lookup_methodology`, `retrieve_similar_cases` → `rag_lookup_case_history`, and `rag_lookup_evidence` added (it did not appear in the original text).

### The Core Distinction

```
MCP Tool (external)     = exposed to OUTSIDE clients across a process/network boundary
                          any agent or system can discover and call it
                          e.g. "fetch live SAP process data", "query complaint rate API"

Internal @tool          = private to THIS agent's own reasoning loop
                          LLM can invoke it within its TAO cycle
                          stays inside the same process, never exposed externally
                          e.g. "rag_lookup_methodology when I need theoretical grounding"
```

All three indexes — `improve_knowledge_index`, `improve_evidence_index`, `improve_case_index` — are **private reasoning support** for the coaching LLM. None is exposed as an MCP endpoint. They are internal `@tool` functions the phase executor invokes within its own reasoning loop.

Under §39 this is no longer a *choice* between two boundaries. Everything is on the internal side. The distinction still matters as a design principle, though: it is why cross-agent tool sharing (Agent Improve reading Agent Resolve's indexes) happens through Python imports from shared modules rather than through a protocol.

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
LLM CALLS: rag_lookup_methodology(query="root cause validation
           techniques DMAIC Analyse phase", phase="analyse")
        ↓
Tool returns filtered, relevant eBook chunks
        ↓
LLM reasons with theoretical grounding
        ↓
Responds with methodology-backed coaching
```

---

### The Three Internal Retrieval Tools

*This section originally described two. The ratified set is three — `rag_lookup_evidence` was added because uploaded evidence is the only channel for real-world data (§39), and `rag_lookup_case_history` was ratified on yokoten grounds (§32). The sketches below show the tool boundary and docstring discipline; the **canonical implementations with multi-query and RRF are in §33**.*

```python
from langchain_core.tools import tool
from langchain_core.documents import Document


@tool
def rag_lookup_methodology(query: str, phase: str, top_k: int = 10) -> list[Document]:
    """Retrieve Six Sigma and DMAIC methodology from the LSS Black Belt
    knowledge base. Use when you need theoretical grounding for a coaching
    decision, root cause validation, or methodology guidance.
    Filters by phase_relevance; uses the content_vector field."""


@tool
def rag_lookup_evidence(query: str, case_id: str, top_k: int = 10) -> list[Document]:
    """Retrieve from the Belt's own uploaded documents for THIS case.
    Use when you need the project's actual data — measurements, process
    documentation, collected samples. This is the only channel through which
    real-world data enters the system. Filtered by case_id; uses content_vector."""


@tool
def rag_lookup_case_history(
    query: str,
    top_k: int = 10,
    exclude_current_case: bool = True,
) -> list[Document]:
    """Semantic search across past Agent Improve cases (all phases, all
    completed gates). Useful for yokoten — finding similar problems, root
    causes, or successful counter-measures from prior projects.
    Retrieves either raw content chunks (via the `embedding` field) or
    pre-computed per-phase summaries (phase_summary_define, _measure, …).
    Excludes the current case by default, since its artifacts are available
    directly via the store. Filters status eq 'completed'; orders by
    created_at desc.
    NOTE for future engineers: if Agent Improve ever serves multiple
    organisations, this tool must filter by tenant (§87 item 1)."""
```

**Docstrings are load-bearing.** They are how the LLM decides *which* of the three to call — the difference between "I need methodology," "I need this project's data," and "I need precedent from other projects" is carried entirely by these descriptions. This is the "memory selection" concern from §38, and it is why §38 concluded no separate selection component is needed.

**Metadata filters are built into the tool definitions** rather than passed by the caller (§40). The `phase` argument shapes both the `phase_relevance` filter and the variant-generation prompt; `status eq 'completed'` and `order_by created_at desc` are fixed inside `rag_lookup_case_history`. Correct filtering happens because the tool owns it, not because the LLM remembers to ask for it.

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
    {"tool": "rag_lookup_methodology", "query": "root cause validation techniques", "phase": "analyse"},
    {"tool": "rag_lookup_case_history", "query": "call centre complaint rate root cause"}
  ],
  "reactive_tools_available": ["rag_lookup_methodology", "rag_lookup_case_history"],
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
# Phase Executor — Analyse phase example (§39 per-phase binding)
UNIVERSAL_TOOLS = [
    record_field,
    rag_lookup_methodology,      # internal RAG — methodology grounding
    rag_lookup_evidence,         # internal RAG — this case's uploaded data
    rag_lookup_case_history,     # internal RAG — precedent, yokoten
    propose_template,
    propose_diagram,
    check_gate_status,
    request_human_approval,
]

ANALYSE_COMPUTATION_TOOLS = [
    t_test, chi_square_test, anova, pearson_correlation, linear_regression,
]

executor = create_agent(
    model=get_llm("operational-premium"),           # gpt-4o for reasoning
    tools=UNIVERSAL_TOOLS + ANALYSE_COMPUTATION_TOOLS,   # 13 for Analyse
    system_prompt=black_belt_coach_prompt,
    middleware=[                                    # §84
        DMAICSkillsMiddleware(...),
        DMAICGraderMiddleware(...),
        SummarizationMiddleware(...),
        BeforeModelStateInjection(...),
    ],
)
```

*Note that the executor does **not** take `checkpointer=` or `store=` — those go on the parent graph only (§23, §44). The store reaches nodes through injection.*

The executor's capabilities per turn:
1. Plan-driven retrieval, from the Phase Planner's `planned_retrievals`
2. Reactive retrieval, when the Belt's answer demands it — up to the 5-hop cap (§34)
3. Field capture via `CoachingResponse.fields_captured`
4. Phase-appropriate computation — 5 statistical tools for Analyse
5. Gate readiness check via `check_gate_status`

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

### Where the Boundary Ended Up

The original version of this subsection split tools into two columns — internal `@tool` for reasoning support, MCP for anything crossing a system boundary:

```
Internal @tool (private, same process):
  rag_lookup_methodology      ← reasoning support
  rag_lookup_case_history     ← reasoning support
  CoachingResponse            ← internal, structured output
  check_gate_status           ← internal scoring

MCP Tool (external, network-accessible):     ← THIS COLUMN IS EMPTY (§39)
  get_sap_process_data()
  fetch_live_complaint_rate()
  query_azure_devops_metrics()
```

**The right-hand column is empty by decision, not by omission.** Everything in it required a live system integration, and AgentLean has none: the Belt uploads their data and the coach teaches them what to collect. So all 27 tools are internal `@tool` functions (§39), and the "boundary" this section describes turns out to enclose the whole system.

The distinction is still worth understanding. It is what makes the §39 reasoning legible — MCP is the right answer when tools must cross an organisational boundary, and the reason it is wrong here is a fact about our situation, not about the protocol.

### Gap Register Update
**Gap 21 — resolved as described.** Filters live in the tool definitions rather than in a global retrieval pipeline. There is no residual unconditional-pipeline work, because the unconditional pipeline is removed entirely: retrieval is a tool call the LLM decides to make.

---

## 61. MCP Resources — URI-Addressable Read-Only Knowledge Layer

*Source: Edureka Course 4 Module 1, "Consuming MCP Resources" demonstration transcript, verified against official MCP specification primitives.*

> **Status: knowledge-only (§39).** The tool-versus-resource distinction is genuinely useful and worth understanding. Note that its most attractive application for AgentLean — URI-cited sources making every coaching response auditable (Gap 33) — is achieved without MCP: `rag_lookup_methodology` returns `source_file` and `page_number` as document metadata, which gives the same citation transparency ("this came from page 47 of the BB eBook") with no protocol layer. See §40.

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
The demo uses upfront bulk load (load everything before the conversation). For Agent Improve this is the wrong pattern — the eBook is large and not all chapters are relevant to every coaching turn. Loading everything upfront wastes context window space, directly conflicting with Gaps 19 and 22 (context window management, context orchestration layer). The on-demand retrieval pattern from Section 60 (`rag_lookup_methodology` as an internal tool the LLM calls when needed) remains the correct approach.

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
  rag_lookup_methodology("root cause validation")
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
- Similarity search (Section 60's `rag_lookup_methodology` tool) for broad queries when the right chapter is not known in advance
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
              - rag_lookup_methodology (internal RAG)
              - rag_lookup_case_history (internal RAG)
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

The practical implication as originally stated: **AgentLean's custom MCP server should be deliberately scoped to only what does not already exist in a maintained third-party server.**

### Gap Register
No new gap number. **The three-way split this section proposed — Azure MCP Server for infrastructure, a custom AgentLean MCP Server for DMAIC domain logic, internal `@tool` for reasoning support — collapses to its third branch under §39.** Everything is internal `@tool`. The build-versus-buy analysis is preserved as knowledge; it is a good worked example of how to scope an MCP surface if a future product needs one.

---

## 63. MCP Evaluated for AgentLean — and Rejected

*Source: Direct discussion, synthesising Sections 59–62, then reversed by the §39 ratification. This section was a planning document for an AgentLean MCP server. It is now the record of the evaluation and the decision not to build it.*

### The Decision

**No AgentLean MCP server will be built.** Not for Agent Improve, not for Agent Resolve, not for Agent Flow. This is an architectural exclusion, not a deferral — there is no promotion trigger and no §87 entry.

### Why

The `@tool` decorator does everything an MCP server would do here. As stated during ratification: *"the tool decorator does the same thing. The only difference is if I would be working for a large enterprise I would use MCP to share the tools to other agents."*

MCP earns its overhead when at least one of these is true:

| Condition | AgentLean |
|---|---|
| Multiple teams or organisations share tools across independent codebases | ✗ One team owns all three agents |
| Language-agnostic tool consumers exist (Python tool, Node.js agent) | ✗ All Python |
| Third-party tool ecosystems require a standardised interface | ✗ No third-party consumers |
| Enterprise tool registries with governance boundaries are needed | ✗ One repository, one constitution |

None apply. Cross-agent tool sharing — Agent Improve reading Agent Resolve's indexes — happens via Python imports from shared modules. That is simpler, faster, type-checked, and debuggable in one process.

**The second, independent reason:** the scope proposed below was built around exposing knowledge and case retrieval as network-accessible endpoints. Those are private reasoning support (§60), and exposing them would cross a boundary that should not be crossed. And the live-data tools that *would* have justified a protocol — SAP process data, live KPIs, external benchmarks — are excluded by the data architecture principle in §39: **users upload their data; the agent coaches them on what to collect and how.**

### What Replaces It

| Proposed MCP tool | Ratified replacement |
|---|---|
| `search_knowledge(query, phase)` | `rag_lookup_methodology(query, phase, top_k)` — internal `@tool`, multi-query + RRF (§32, §33) |
| `search_cases(query, ...)` | `rag_lookup_case_history(query, top_k, exclude_current_case)` — internal `@tool` |
| *(not proposed)* | `rag_lookup_evidence(query, case_id, top_k)` — the only channel for real-world data |
| Live external data tools | **Excluded.** Belt uploads to `improve_evidence_index`. |
| Computation exposed via MCP | 18 internal `@tool` computation functions, bound per phase (§39) |

### What Survives From the Original Plan

Three things in the design below are worth keeping, detached from the protocol:

1. **Tool docstrings as the selection mechanism.** The care taken over "use when reasoning about a complex coaching decision" carries directly into the `@tool` docstrings (§60).
2. **Read-only discipline.** Retrieval tools never write. Writes go through `CoachingResponse.fields_captured` and the gate flow, where the Belt approves them.
3. **Structured JSON returns rather than prose.** Ratified throughout (§21, §82).

---

### The Original Proposed Scope — Historical Record

*What follows was the plan. It is retained so the decision has a legible before-and-after, not as guidance.*

### The Proposed Scope

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
        │     rag_lookup_methodology()    ← wraps MCP search_knowledge call
        │     rag_lookup_case_history()  ← wraps MCP search_cases call
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

> **Status: MCP framing is knowledge-only (§39). One piece is ratified and used everywhere — the structured error schema.**
>
> ```python
> class AgentImproveError(BaseModel):
>     error_code: str              # "TIMEOUT", "RATE_LIMIT", "AUTH_FAILURE", …
>     severity: str                # "transient" | "permanent"
>     retry_recommendation: str    # "retry_after_backoff" | "do_not_retry" | "retry_after_delay"
>     affected_identifier: str     # which service failed
>     message: str                 # human-readable description
>     timestamp: datetime
> ```
>
> This schema applies to **every external service call** — Azure OpenAI, Azure AI Search, Azure Blob — not just MCP ones. It is consumed by the circuit breaker (§66), the fallback chain (§67), and the `step_log` audit trail (§18). `severity` is what lets the circuit breaker distinguish "retry this" from "stop trying"; `retry_recommendation` is what the fallback chain reads to decide between exponential and jittered backoff.
>
> Two further principles below survive the MCP framing and are worth reading: **stateless servers with LangGraph owning session continuity** (the same separation the Checkpointer + Store split makes, §52), and the **two-stage metadata-then-content retrieval pattern** (cheap descriptors first, full content only for what passes a relevance threshold — a good cost pattern independent of transport).

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

> **Status: MCP framing is knowledge-only (§39). The caching principles are ratified and applied to the Azure Redis Cache at §67 Level 3.**
>
> Three things here transfer directly and are worth reading for:
> - **Cache key design** — what actually distinguishes one cached retrieval from another. For us: query hash + phase, and session-scoped rather than global, because different projects have different context.
> - **TTL policy** — how long a cached answer stays trustworthy. Methodology retrieval is stable (the eBook does not change); case history and evidence are not.
> - **Invalidation** — what must evict a cached entry. A gate approval changes the project's artifacts, which changes what a retrieval *should* return.
>
> **What does not transfer:** tool-list caching. There is no `tools/list` round-trip to amortise, because tools are Python functions bound at graph-build time.
>
> §66/§67 originally referenced "the MCP knowledge cache from Section 65" as the Level 3 fallback. That is replaced by Azure Cache for Redis — a real infrastructure component that must be provisioned, and which is **in refactor scope** (§67).

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

## 39. Knowledge Tools in Augmented Reasoning

*Source: Edureka Course 2 — Role of Knowledge Tools in Augmented Reasoning*

### What Augmented Reasoning Means
The LLM's reasoning is augmented by external knowledge tools — accessing information beyond its training data to produce grounded, fact-aware outputs.

### The Four Capabilities

**Accesses external knowledge beyond the model's training data**
Why `improve_knowledge_index` exists. gpt-4o was not trained on the specific Black Belt eBook. Without RAG the model answers Six Sigma questions from generic training data — potentially wrong, outdated, and not aligned with our methodology. The knowledge index gives it access to authoritative specific content.

**Retrieves documents, databases, and real-time information**
We retrieve from the knowledge, evidence, and case indexes. We deliberately do **not** retrieve real-time process data — see Decision 1 below. The Belt uploads their data; the coach's job includes teaching them what to collect and how.

**Enables verification, search, and computation capabilities**
Search and verification we have. **Computation is added in the refactor** — 20 tools, distributed per phase. See Decision 2 below.

**Supports grounded and fact-aware reasoning outputs**
The anti-hallucination argument for RAG. Without it the coach invents methodology. With it the coach retrieves and cites actual Black Belt content — including `source_file` and `page_number` for citation transparency (§40). This is why the eBook index exists.

---

### Decision 1 — MCP Is Out of Scope. Permanently.

**Ratified: Agent Improve, Agent Resolve, and Agent Flow will never use MCP to connect to a live system.** This is not a deferral. It is an architectural exclusion.

> *"Agent Improve as well as Agent Resolve that we will refactor after will never use MCP to connect to a live system. Users must upload their data they collect and the agents are responsible to guide the user to what kind of data they should collect and how to collect it."*

> *"The tool decorator does the same thing. The only difference is if I would be working for a large enterprise I would use MCP to share the tools to other agents."*

That reasoning is architecturally sound. The `@tool` decorator handles single-team, single-stack tool composition natively. MCP adds protocol overhead that pays off only when:

- Multiple teams or organisations share tools across independent codebases
- Language-agnostic tool consumers exist (a Python tool, a Node.js agent)
- Third-party tool ecosystems require a standardised interface
- Enterprise tool registries with governance boundaries are needed

**None of these apply to AgentLean.** Same team owns all three agents, all Python, all LangChain 1.x. Cross-agent tool sharing — Agent Improve calling into Agent Resolve's search — happens via Python imports from shared modules, not via a protocol.

### What This Changes

| Area | Treatment |
|---|---|
| §57–§65 (nine MCP sections) | Retained as **pedagogical knowledge**, not roadmap. Same treatment as §35. §63 is rewritten as "MCP evaluated and rejected, with rationale." |
| Cross-agent tools (`search_resolve_*`) | Remain — but as `@tool` functions reading Agent Resolve's Azure AI Search indexes directly. Not MCP servers. |
| Stack description | FastAPI, LangGraph 1.2+, LangChain 1.x, Azure OpenAI, Azure AI Search, Azure Blob Storage. **No MCP.** |
| §87 backlog | MCP-dependent items (real-time SAP data, external verification benchmarks) are **removed, not deferred**. They are architecturally excluded. |

### The Data Architecture Principle This Establishes

**`improve_evidence_index` is not merely "case-specific uploaded documents." It is the *only* channel for external, real-world data in AgentLean.**

That elevates its architectural importance considerably. It means:

- Coaching content itself must include guidance on what data to upload and how to structure it — data-collection coaching is a first-class part of the methodology, not a workaround
- Belt data-collection discipline is what the platform's grounding depends on
- There is no fallback path where the system fetches a number the Belt failed to provide

Worth capturing as an explicit design principle in ARCHITECTURE.md §1.

### What We Augment With

```
In scope:
✅ Static methodology  (improve_knowledge_index  → rag_lookup_methodology)
✅ Uploaded evidence   (improve_evidence_index   → rag_lookup_evidence)
✅ Case history        (improve_case_index       → rag_lookup_case_history)
✅ Computation         (18 @tool functions, per-phase — Decision 2)

Architecturally excluded — not deferred:
✗ Real-time process data (SAP, live KPIs)       → Belt uploads it
✗ External verification (industry benchmarks)    → out of scope
```

### The Course 4 Connection — Reframed

Course 4 taught MCP, and that knowledge is worth having: the protocol, the host/client/server model, transports, resource URIs, caching. §57–§65 preserve it. What Course 4 is **not** is a roadmap for AgentLean. The knowledge-tool suite is completed by `@tool` functions and three retrieval tools, not by a protocol layer.

Two of Course 4's ideas do carry over, detached from MCP:
- The **structured error schema** (§64) applies to Azure OpenAI and Azure AI Search failures regardless of protocol
- The **caching principles** (§65) — cache key design, TTL, invalidation — apply directly to the Azure Redis Cache at §67 Level 3

---

### Decision 2 — 20 Computation Tools, Bound Per Phase

Each is a `@tool(args_schema=...)` function with a Pydantic argument schema. All are pure functions — no LLM call, deterministic, unit-testable.

### Per-Phase Distribution

| Phase | Universal tools | Phase-specific computation tools | Total |
|---|---|---|---|
| Define | 7 | `calculate_expected_savings` | **8** |
| Measure | 7 | `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean` | **15** |
| Analyse | 7 | `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression` | **12** |
| Improve | 7 | `calculate_doe_main_effects` | **8** |
| Control | 7 | `xbar_r_chart_limits`, `imr_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk` | **12** |

**The universal seven**, passed to every phase executor via `tools=`: `rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history`, `propose_template`, `propose_diagram`, `check_gate_status`, `request_human_approval`.

### Why Per-Phase Binding, Not Universal

| | Option A — bind all 27 to every phase | Option B — per-phase subset *(selected)* |
|---|---|---|
| Tools per coach | 26 everywhere | 9–16, never more than 16 |
| Selection quality | Degrades past ~10–15 tools per agent (2026 practitioner guidance) | Every coach stays in the tractable range |
| Reasoning burden | Every turn considers 26 options, most irrelevant | Only phase-appropriate options |

### Why Separate Tools, Not Parameterised Grouping

Grouping was considered — a single `calculate_sample_size(type, ...)` with a mode parameter — and rejected. Parameterisation moves the selection burden from the tool namespace into the argument space, and LLMs handle distinct named tools more reliably than mode arguments. Each canonical DMAIC calculation gets its own tool with a name that signals its purpose.

### Architectural Consequence — The Subgraph Builder Needs to Know Its Phase

Retrieval, templates, diagrams and gate status stay universal; computation tools do not. **The phase subgraph builder function therefore takes the phase as a parameter**, used to select the correct computation-tool subset for tool binding:

```python
def build_phase_subgraph(phase: str, llm):
    tools = UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    ...
```

A small change, called out explicitly because ARCHITECTURE.md §3.2 currently describes the coach as bound to a single fixed toolset.

*Cross-references: §11 (per-phase tool diagram), §23 (tools are bound to the executor node, not separate subgraph nodes), §36/§37/§38 (memory and retrieval), §57–§65 (MCP as knowledge), §60 (the internal-tool boundary, retained as architectural reference), §63 (the rejection documented), §83 (each phase skill's `allowed-tools` mirrors this distribution), Terminology Reference (leaf tools).*

---

# PART 10 — COURSE HISTORY AND CONTEXT

*Training record, not operational. Kept for continuity: these sections document how the thinking arrived where it did; none of them specifies architecture.*

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

### Two Points Since Superseded

This is a historical record of a graded submission, kept as documentation of where the architectural thinking started. Two of its points have since been overtaken:

| In the submission | Ratified since |
|---|---|
| `InMemorySaver` for dev, `PostgresSaver` for production | Phased checkpointer: `AzureBlobCheckpointSaver` during the refactor, `PostgresSaver` post-refactor. `InMemorySaver` is not used at any stage. (§1) |
| Flat supervisor / worker with no cross-agent awareness | Recursive Planner-Executor pair — a phase subagent plans *and* dispatches. Flat supervisor/worker cannot express it. (§5, §20) |

The four guarantees themselves hold, and each now maps to a specific ratified mechanism: checkpointing (§1), HITL interrupts (§2), time-travel debugging (§3, with the §49 side-effect caveat), and modular subgraphs (§23).

**Framing that distinguished the proposal:**
- "Right now human oversight means someone reviews outputs after they have already been acted on. That is not oversight, that is audit."
- "The architecture is the guarantee" — each of the four guarantees is delivered by a specific tested LangGraph capability, not an aspiration
- Node classification framework: consequence severity + reversibility as the principled basis for interrupt placement

### Grade and Feedback
No additional feedback received. All concepts correctly applied and present.

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

No new gap number — a **course-material reliability flag**, not an AgentLean architectural gap. Confidence downgraded from "verify when encountered" to "assume stale, substitute by default" given the syllabus-level confirmation above.

**Resolved by §55: FastAPI is the deployment layer. The LangServe substitution is complete.** Every deployment pattern from Course 4 is superseded by that decision; there is nothing left to substitute case by case. Note also that the course's MCP content, while protocol-accurate, is knowledge-only for AgentLean per §39 — so Module 3's deployment content is doubly out of scope: stale tooling for an architecture we are not building.

---

## 54. Correction to Section 42 — RubricMiddleware Exact Requirements and API

*Source: Verified directly against docs.langchain.com/oss/python/deepagents/rubric, current as of June 2026 (confirmed via direct documentation reference, and a blog post dated within the last week relative to current date — this is very recently shipped, actively evolving functionality).*

> **Status: incorporated into §42. This section is now a historical note.**
>
> Both corrections below are reflected in §42's ratified decision. The dependency point in Correction 1 is precisely what drove **Option B** — a custom `DMAICGraderMiddleware` on `create_agent` rather than deepagents' `RubricMiddleware`. The temperature discipline is ratified as §42 Decision 4. The `on_evaluation` callback pattern is adopted for the `step_log` audit trail.
>
> Read §42 for what gets built. Read this section for the evidence that led there.

Section 42 correctly captured the purpose and value but was imprecise on two points, now corrected:

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

**This is the decision point that §42 resolved.** Adopting `RubricMiddleware` would mean adopting `deepagents` as a dependency for every phase subagent needing rubric grading — and switching them all from `create_agent` to `create_deep_agent`. That is a far larger commitment than a single middleware import, and it lands a pre-1.0 package with weekly breaking changes in the core of the coaching loop.

**§42 chose Option B:** a custom `DMAICGraderMiddleware` implementing the same LLM-as-a-judge pattern on `create_agent`'s GA-stable hooks. Roughly one extra day of implementation, zero dependency risk, and a near-drop-in migration path when deepagents reaches 1.0.

**Correction 2 — state schema is more precise than Section 42 implied:**

> "Only rubric is part of the public I/O schema -- callers write a rubric and read the improved agent response back from messages. Everything else is bookkeeping: status, iteration count, accumulated evaluations, and rubric-attempt tracking are annotated with PrivateStateAttr so they are omitted from input/output schemas."

This confirms a clean boundary contract consistent with Section 44's typed-boundary-output principle: the rubric grading internals (iteration count, accumulated evaluations) stay private to the middleware's own state, never leaking into `PhaseState` or `SupervisorState`. Only the rubric string goes in, and the graded final response comes out via `messages`. Observability into the grading process (which Gap 23's audit-trail requirement needs) is available via a separate, explicit mechanism:

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

The `on_evaluation` callback is the precise mechanism for feeding grading decisions into §18's `step_log` — closing the question of how the grader's internal reasoning becomes part of the DMAIC audit trail without leaking into the coach's messages or the Belt's view.

**Adopted.** `DMAICGraderMiddleware` takes an `on_evaluation` callback with the same contract (§42). The private-state discipline is adopted too: iteration count, accumulated evaluations, and attempt tracking stay inside the middleware and never reach `PhaseState` or `SupervisorState`.

### Gap Register Update

**Gap 23 — closes via §42 Option B.** The dependency question this section raised is answered: no `deepagents` dependency, custom middleware on `create_agent`. What carries over from here into §42 is the temperature discipline (Decision 4), the `on_evaluation` audit-trail integration, and the private-state boundary.

*Cross-references: §18 (`step_log`), §42 (the ratified decision this section fed), §48 (the deterministic layer that runs before the grader), §68 (the four-layer stack), §75 (why grader temperature must be low).*

---

# PART 11 — REFERENCE

*Patterns, diagrams, taxonomies, and evaluation records looked up occasionally rather than read through.*

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

### What This Solved
Before the checkpointer landed there were no checkpoint IDs and no state history, so debugging extraction errors, gate routing bugs, and phase regressions required manual reproduction:

- Extraction hallucination debugging required re-running the full conversation
- Gate advancement bugs (e.g. `selectTab` vs `openWorkspace`) were hard to reproduce
- No before/after state comparison when a change introduced a regression

### Key Point
Resolved by wiring the checkpointer (§1) — no additional implementation needed. This holds for `AzureBlobCheckpointSaver` today and for `PostgresSaver` after migration; `get_state_history` is a `BaseCheckpointSaver` interface method, not a backend feature.

### Caveat — Time Travel Does Not Undo Side Effects

**Resuming from an earlier checkpoint rolls back graph state. It does not roll back writes already made to Azure Blob, `improve_case_index`, or `improve_evidence_index`.** For any node with external writes, time travel is only correct if the corresponding compensating action runs alongside the rollback. That compensating action is the Saga `error_handler=` from §49. Time-travel debugging and Saga support are interdependent, not independent features.

### Subgraph Note
Each phase subgraph's history is namespaced under its own auto-managed `checkpoint_ns` within the project's single `thread_id` (§23). `get_state_history` on the parent config walks the parent's supersteps; inspecting inside a phase requires the subgraph's namespaced config.

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

### Agent Improve Graph Shape — Before and After

The pre-refactor graph is **mostly DAG-like** — one linear pass per HTTP request:

```
START → load_state → route_message → generate_response → extract_fields → save_state → END
```

LangGraph's cycle capability was barely used. Each request triggered one clean pass, which is exactly why coaching strategy had nowhere to live except inside a single prompt (the Gap 10 problem §5 diagnoses).

**The refactored shape uses cycles at both levels.** Per §23, a phase subgraph is not a straight pipeline:

```
        ┌────────────────────────────────────────────┐
        │                                            │
   phase_planner → phase_executor → validation_stack ┤
        ↑                 │                          │
        │                 └── (tool-calling loop,    │
        │                      ≤5 hops, §34)         │
        └── gate_apply ← gate_review (interrupt) ────┘
```

The planner fires many times per phase, not once: after each executor step, control returns to the planner to decide whether to keep coaching the current field, move to the next field, or trigger the gate. That is a cycle, and it is why LangGraph rather than a DAG engine is the right runtime. Between phases the top level is deliberately acyclic — static edges, `define → measure → analyse → improve → control` (§44).

---

## 6. Multi-User Production Gaps

### Identity & Session Isolation
- No authentication layer currently
- No user namespacing on blobs
- Any `case_id` guess exposes another user's data
- Target: Azure AD B2C or Auth0 + blob path `/{user_id}/{case_id}/state.json`

### Concurrency & State Write Safety
- No locking on blob reads/writes
- Concurrent users on same project can cause write race → state corruption
- Target: ETag-based optimistic concurrency on blob writes

### Azure OpenAI Rate Limits
- No request queuing beyond LangChain defaults
- TPM limits hit fast under concurrent users
- Target: exponential backoff, request queuing, potentially multiple deployments

### Tagged Observability
- LangSmith traces untagged — no `user_id` / `case_id` context
- Errors visible only in local terminal
- Target: tagged traces, Azure Monitor, alerting on failed gates

---

## 7. Full Dependency Chain

*Corrected: the original chain started at "PostgreSQL (new Azure resource)". PostgreSQL is no longer the entry condition — `AzureBlobCheckpointSaver` satisfies the checkpointer dependency during the refactor, and the PostgreSQL migration is a later, independent step (§1, §87 item 13).*

```
Checkpointer wired into graph.compile()          ← AzureBlobCheckpointSaver (done)
    ↓
├── Human-in-the-loop interrupts (§2)
├── Time travel debugging (§3) ── requires Saga compensation (§49) to be correct
├── Snapshot analysis (§3)
└── Stateful planner/executor loops (§5, §11)
    ↓
Store wired into graph.compile()                 ← AzureBlobStore (§52a)
    ↓
└── Cross-phase artifact handoff (§19, §21, §23, §70)

    ── later, independently ──
PostgreSQL (Azure Database for PostgreSQL, ~€12–15/month flexible server)
    ↓
PostgresSaver + PostgresStore replace the Blob implementations
    (constructor + connection string change; same interfaces)
```

The ordering constraint that does still bind: **the store is meaningless without functional checkpoint persistence first.** Implement `AzureBlobStore` after `thread_id` is wired through `graph.ainvoke` (refactor Step 6), not before.

---

## 8. Implementation Sequencing Decision

*This section was rewritten. EDUCATIONAL.md described Option A — defer the refactor until all three AgentLean agents are feature-complete. **Option B was selected** (§16). The sequence below is the ratified one.*

### The Decision

Two options were on the table:

| | Option A — defer | Option B — refactor first *(selected)* |
|---|---|---|
| Sequence | Finish Improve and Control on the current foundation, then refactor everything | Refactor the foundation now, then build Improve and Control on top of it |
| Rework | Two more phases built the wrong way, then rewritten | None — each new phase is built correctly the first time |
| Risk | Architectural debt compounds across five phases | Refactor happens while only three phases exist to migrate |
| Infrastructure | PostgreSQL required up front | None — `AzureBlobCheckpointSaver` already works |

**Option B was selected.** The original deferral rationale rested on two premises that no longer hold: that checkpointing requires PostgreSQL (it does not — see §1), and that the blob-at-gate pattern is durable enough (it is not, for anything beyond single-user demo use). The cost of Option A is building Improve and Control twice.

### The Correct Sequence

```
Refactor the foundation
  ├── Checkpointer wired into graph.compile()            (§1)   ✔ steps 2.1–2.2
  ├── SupervisorState / PhaseState split                 (§17, §18)
  ├── Phase subgraphs with private state                 (§23)
  ├── AzureBlobStore for cross-phase artifacts           (§52a)
  ├── Explicit planner / executor nodes                  (§5, §11, §20)
  ├── Three rag_lookup_* tools with multi-query + RRF    (§32, §33)
  ├── 20 per-phase computation tools                     (§39)
  ├── Four-middleware coach stack                        (§84)
  ├── Four-layer gate validation + nine-step HITL        (§2, §68)
  └── Reliability: timeouts, error_handler, circuit
      breaker, fallback chain with cache                 (§49, §66, §67, §79)
    ↓
Build Improve phase        ← on the correct foundation from the start
    ↓
Build Control phase        ← on the correct foundation from the start
    ↓
Run IMPR-2026-E9D end-to-end clean
    ↓
Activate IMPR-2026-FS1 (financial services demo)
    ↓
Migrate PostgresSaver + PostgresStore                    (§87 item 13)
    ↓
Multi-user identity & isolation, tagged observability    (§6)
    ↓
Begin Agent Flow
```

Two workstreams run alongside the refactor rather than after it: the evaluation dataset (§75) and the five DMAIC phase skills (§83). Both are authored jointly rather than generated, because both encode Black Belt domain judgment.

See §16 for the debt acknowledgement this decision resolves.

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
Shown as stacked pages — a structured artifact the planner creates and the executor consumes task by task. Not buried in a prompt. **Agent Improve has no parent-level equivalent, deliberately.** DMAIC order is fixed rather than planned (§44), so a stored plan object would encode a constant. The first-class-object principle still applies one level down, at `coaching_plan` on `PhaseState` (§18), where the planner genuinely decides which field to work on next.

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
| Task Plan | `coaching_plan` on `PhaseState` — fields as tasks within a phase. No parent-level plan: DMAIC order is static (§44) |
| Executor | Phase Subagent (Levels 2 + 3) |
| Human-in-the-loop | Belt reviews extracted fields at gate |
| Edited | Belt corrects wrong AI-extracted field values |
| Approved? | Belt confirms phase gate ready |
| Checkpoint & State Update | `AzureBlobCheckpointSaver` during the refactor, `PostgresSaver` post-refactor (§1) |
| Next Task? | Next phase or next missing field in same phase |

---

### What This Changes in the Refactor Plan

The edit loop requires a FastAPI resume endpoint — not just a pause:

```python
# Pause — graph interrupts here automatically
graph.invoke(input, config={"configurable": {"thread_id": case_id}})

# Belt reviews extracted fields in UI
# Belt edits if needed — sends corrections back

# Resume — with corrected state
graph.invoke(
    Command(resume={"edited_fields": corrections}),
    config={"configurable": {"thread_id": case_id}}
)
# Checkpoint saves AFTER this resume, not before
```

Two endpoints needed in FastAPI:
- `GET /gate/review` — returns current extracted fields for Belt to review
- `POST /gate/approve` — accepts corrections + approval, resumes graph, triggers checkpoint

---

### Correction to the §2 Framing
This section was where the approve/reject binary first proved insufficient: the pattern is interrupt → review → optional edit → approve → checkpoint. The edit capability is what makes the system trustworthy for a DMAIC audit trail — the Belt is accountable for what gets saved, not the AI.

§2 now carries the full **nine-step** pattern, which adds two things this section did not yet have: the grader loop before the Belt ever sees the output (step 2, §42), and the policy advisory on the Belt's own edits (step 6, §38). The two-endpoint FastAPI shape above is still correct, and §44 refines the graph side of it into two nodes — `gate_review_node` fires the interrupt, `gate_apply_node` processes the response.

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
| Task Plan | `coaching_plan` on `PhaseState` — fields as individual tasks within a phase. No parent-level plan: DMAIC order is static (§44) |
| Executor | Phase Subagent (Levels 2 + 3) |
| Human-in-the-loop | Belt reviews AI-extracted fields at gate |
| Edited | Belt corrects wrong field values — loops back to Task Plan |
| Approved? | Belt confirms gate ready |
| Checkpoint & State Update | `AzureBlobCheckpointSaver` during the refactor, `PostgresSaver` post-refactor (§1) |
| Next Task? Yes | Next missing field or next phase |
| Next Task? No | All phases complete — final DMAIC report output |
| Output | Completed DMAIC project — gate documents, control plan |

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

**Option A — Complete first, full refactor after**
Finish Analyse, Improve, Control phases. Accept architectural debt. Full refactor during `agentlean-*` migration. Lower risk to timeline.

**Option B — Pause and refactor before building more phases**
Introduce checkpointer, private subagent states, explicit planner nodes before Improve and Control phases. Higher upfront cost but each new phase built correctly from the start.

### Decision

**Option B selected.** The refactor introduces the checkpointer, private subagent states, and explicit planner/executor nodes *before* the Improve and Control phases are built. Each new phase is built on the correct foundation from the start, so neither has to be written twice. See §8 for the updated sequence, and CLAUDE.md / ARCHITECTURE.md v2.2 for the full specification.

The debt table above is the scope of what Option B closes:

| Feature | Closed by |
|---|---|
| Checkpointer | §1 — `AzureBlobCheckpointSaver` wired at refactor steps 2.1–2.2 |
| Human-in-the-loop interrupts | §2 — nine-step gate pattern |
| Explicit planner nodes | §5, §11, §20 — Planner-Executor pairs at both levels |
| Private subagent state schemas | §17 `SupervisorState`, §18 `PhaseState`, §23 subgraphs |
| Tool encapsulation per subagent | §39 — per-phase `bind_tools()` subsets |
| Structured executor pattern | §5, §11 — `with_structured_output` plans, §82 |

---

## 25. Architectural Gaps — Complete Register (Final)

*Consolidated from all sessions, then reconciled against every ratified decision. The EDUCATIONAL.md version of this register had gaps 1–14 in one table and 15–33 orphaned below a prose block; they are one table here. **"Deferred To" is replaced by "Status"** — the Option B decision (§8, §16) means these are refactor scope, not post-completion work.*

| Gap | Description | Status | Where |
|---|---|---|---|
| 1 | No LangGraph checkpointer wired into `graph.compile()` | **CLOSED** — `AzureBlobCheckpointSaver` wired at refactor steps 2.1–2.2 | §1 |
| 2 | No human-in-the-loop interrupts at gate boundaries | **In refactor scope** — nine-step gate pattern | §2, §42, §68 |
| 3 | Flat shared state — no private subagent state schemas | **In refactor scope** — `SupervisorState` / `PhaseState` split | §10, §17, §18, §23 |
| 4 | No explicit planner nodes — planning implicit in prompts | **In refactor scope** — Planner-Executor pairs at both levels | §5, §11, §20 |
| 5 | No tool encapsulation per subagent | **In refactor scope** — per-phase `bind_tools()` subsets | §39 |
| 6 | No `step_log` audit trail — only captured results | **In refactor scope** — `step_log` with dict entries, append-only reducer | §18, §68 |
| 7 | No backward correction arcs — Analyse cannot send back to Define/Measure | **In refactor scope** — the §38 re-approval cascade is the mechanism: changing an approved value makes that phase and all downstream phases provisional | §38, §49 |
| 8 | No time travel debugging or snapshot analysis | **CLOSED by Gap 1**, with the caveat that it is only *correct* alongside Saga compensation | §3, §49 |
| 9 | No multi-user identity or session isolation | **Post-refactor** — after first production launch | §6 |
| 10 | No concurrency protection on blob writes | **Post-refactor** — resolved by the `PostgresSaver` migration, which has real row-level locking | §1, §87 item 13 |
| 11 | No Azure OpenAI rate limit handling | **In refactor scope** — circuit breaker + exponential backoff + four-level fallback chain | §66, §67 |
| 12 | No tagged observability (`user_id` / `case_id` in traces) | **Post-refactor**, alongside Gap 9 | §6 |
| 13 | No debate-based root cause validation | **Deferred to v2.2** — §87 item 10 | §22, §48 |
| 14 | No context window management for long sessions | **In refactor scope** — `SummarizationMiddleware` + typed state fields | §36 |
| 15 | Single-query RAG only — no multi-query retrieval | **In refactor scope** — multi-query inside the `rag_lookup_*` tools. *The earlier "wait for post-completion refactor" rationale is inverted now that the refactor is the active work.* | §32 |
| 16 | No RAG Fusion / Reciprocal Rank Fusion | **In refactor scope** — RRF in all three retrieval tools by default. The "diminishing returns" deferral was overridden by Agent Resolve production evidence. | §33 |
| 17 | Multi-hop retrieval | **CLOSED** — emergent via the ReAct coach (5-hop cap via `RemainingSteps`); planned three-hop pipeline in Analyse | §34, §71 |
| 18 | No query voting or weighted fusion | **CLOSED — collapsed into Gap 16.** RRF is the ratified fusion method; there is no separate Gap 18. | §35 |
| 19 | No short-term memory summarisation | **CLOSED by Gap 14** — `SummarizationMiddleware` | §36, §53 |
| 20 | Long-term vector memory in `improve_case_index` not queried during coaching | **In refactor scope** — `rag_lookup_case_history` tool (yokoten). Vector field asymmetry (`content_vector` vs `embedding`) closes as a no-op: each tool knows its own index's field name locally. | §36, §37 |
| 21 | Metadata signals not applied in RAG queries | **In refactor scope** — `phase_relevance` filter on methodology; `status` + `created_at` on case history; `case_id` on evidence | §37, §40 |
| 22 | No context orchestration layer | **RETIRED as a compound gap** — decomposed into three small additions: 22a memory-hierarchy paragraph in the coach prompt, 22b `before_model` middleware for early state injection, 22c policy-advisory extension for mid-phase contradictions. All three in refactor scope. | §38 |
| 23 | No rubric-based quality evaluation at gate boundaries | **In refactor scope** — the four-layer validation stack, with `DMAICGraderMiddleware` as layer 4 | §42, §48, §68 |
| 24 | No Decision Agent or Observer Agent roles | **Partially closed.** Decision Agent role is distributed across the grader (§42), the four-layer stack (§68), and mid-phase conflict detection (§38). **Observer Agent deferred** — §87 item 14. | §43 |
| 25 | Version drift — deprecated memory classes and `create_react_agent` | **CLOSED** — Checkpointer + BaseStore split replaces the memory classes; `create_agent` replaces `create_react_agent` throughout | §50, §52 |
| 26 | No governance enforcement layers (Skills, Hooks) | **CLOSED** — implemented, commits 0.5.0–0.5.5 | §45, §86 |
| 27 | No anti-drift mechanisms | **CLOSED** — `/verify-current-version` skill, PreToolUse deprecated-pattern hook, SessionStart version hook, forum monitoring. Smoke tested 2026-07-03. | §45, §86 |
| 28 | No opinion aggregation framework | **Deferred to v2.2** — §87 item 11; depends on the Gap 13 debate subgraph as a signal source. Note that its two named techniques are already ratified elsewhere: rank aggregation = RRF (§33), weighted aggregation = memory hierarchy (§38). | §47 |
| 29 | No Saga-based compensating actions | **In refactor scope** — LangGraph 1.2 native `error_handler=` on every node with external writes | §49, §79 |
| 30 | No `thread_id` length validation | **CLOSED by construction.** The concern assumed concatenated per-subgraph `thread_id`s (`case_id-phase-debate-rootcauseid`). There is one `thread_id` per project; LangGraph manages `checkpoint_ns` itself. Nothing to concatenate, nothing to overflow. | §19, §23, §44 |
| 31 | Subgraph-to-parent state propagation not verified immediate | **CLOSED — confirmed real, and designed around.** LangChain docs state the caveat explicitly and prescribe the fix: use the Store for data crossing graph boundaries. That is why artifacts go to `AzureBlobStore` rather than through shared state keys. | §23, §52a |
| 32 | `HumanInTheLoopMiddleware` edit/reject bugs | **CLOSED — verified, and avoided.** Both bugs confirmed; only approve is reliable in subgraph contexts. The nine-step pattern uses graph-level `interrupt()` + `Command(resume=...)`, not the middleware. | §2, §53 |
| 33 | No knowledge source traceability in coaching responses | **In refactor scope, by a different mechanism.** The original plan was URI-cited MCP Resources; MCP is out of scope (§39). `rag_lookup_methodology` returns `source_file` and `page_number` as metadata, which gives citation transparency ("this came from page 47 of the BB eBook") without a protocol layer. | §39, §40 |

### Root Cause of All Gaps
LangGraph was used as a **graph router and state passer** rather than as a full agent framework. The graph was compiled but its agent capabilities — checkpointing, interrupts, tool-calling agents, planner nodes — were never activated.

### What Was Built Correctly
- LangGraph graph compilation and routing
- Hierarchical subgraph scaffold
- SSE streaming
- Azure Blob state persistence at gate boundaries
- LangSmith tracing
- Black Belt coaching prompt quality (150–400 words mandatory, teach/template/ask)
- Completeness-based extraction with anti-hallucination guards
- RAG retrieval from `improve_knowledge_index`

### Resolution Decision
**Option B (§8, §16):** refactor the foundation first, then build Improve and Control on top of it. The register above is the scope of that refactor. Items marked "Deferred to v2.2" live in §87 with their promotion triggers; nothing else is deferred.

---

## 27. LCEL Pipelines — Why We Never Used Them

*Source: Edureka Course 2 — Applied Agentic AI Pipelines with LangChain*

> **Scope correction — read this before the rest of the section.** LCEL is used **inside individual nodes** for prompt construction, structured output, and deterministic post-processing. It does **not** replace the LangGraph node or subgraph structure. The phase executor in particular uses `bind_tools` for dynamic tool invocation, and that dispatch *cannot* be expressed as an LCEL chain, because the LLM decides at runtime which tool to call. See the Terminology Reference: LCEL is a composition tool, not a level in the hierarchy.
>
> This matters because §27 is one of the first sections a reader hits when trying to understand how AgentLean should compose LLM calls. Read uncorrected, it would lead someone to build the executor as one large LCEL chain — contradicting §17, §18, §23, and §82, and undoing the tool-calling coach agent pattern (ARCHITECTURE.md §B2).

### What We Do Now vs What Pipelines Give Us

**Current approach — manual chaining:**
```python
llm = get_llm()
prompt = build_prompt(state)
response = await llm.ainvoke(prompt)
extracted = extract_fields(response)
```

This observation is still true and still worth fixing. The fix is **not** "turn the whole thing into one chain." It is: move each step into the appropriate node in the subgraph, using LCEL inside those nodes for the deterministic parts and `bind_tools` for the dynamic parts.

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

**Inside individual nodes** — for prompt construction, structured output, and deterministic post-processing:

```python
# Inside the planner node — LCEL for prompt construction + structured output
planner_chain = (
    planner_prompt_template
    | llm.with_structured_output(CoachingPlanSchema)   # §82 ProviderStrategy
)
plan = await planner_chain.ainvoke({"state": state})

# Inside the gate_apply node's policy advisory — LCEL for validation
advisory_chain = (
    build_validation_prompt(state)
    | llm.with_structured_output(AdvisorySchema)
)
```

**What this replaces.** An earlier version of this section modelled the *entire* Measure phase executor as one linear chain:

```python
# ANTI-PATTERN — do not build this
measure_chain = (
    measure_prompt_template
    | get_llm()
    | StrOutputParser()
    | extraction_runnable
    | completeness_check_runnable
)
```

Three things are wrong with it under the ratified architecture:

1. **It encodes the pre-subagent monolith.** Extraction and completeness checking become fixed pipeline steps. In §17/§18/§23 the phase executor is a *node* inside a five-node subgraph, and extraction and completeness are *tools bound to that node* — invoked dynamically by the LLM, not chained deterministically via `|`.
2. **`StrOutputParser` is superseded.** LangChain 1.0's ProviderStrategy (§82) gives native structured output, eliminating the parse-then-validate step entirely (§29). Where the call is an agent rather than a plain LLM invocation, `response_format=ProviderStrategy(Schema)` on `create_agent` is the preferred form — see §82.
3. **`extraction_runnable` and `completeness_check_runnable` are retired as pipeline steps.** They are `response_format=CoachingResponse` and `check_gate_status` — tools, not runnables in an executor chain.

The benefits table above is real, but it applies to LCEL *at the right scope*: composability, streaming, `.abatch()`, per-step tracing, and `.with_fallbacks()` / `.with_retry()` all work fine inside a node.

*Cross-references: §17, §18, §23 (subgraph architecture); §29 and §82 (structured output supersedes parse-then-validate); §51 (LCEL primitives as node-internal composition); Terminology Reference.*

### The Two Levels — Pipelines vs Orchestrator

```
LangGraph (orchestrator)    = controls WHICH agents run and WHEN
                              manages state, routing, checkpointing, interrupts

LCEL Pipelines              = controls HOW each agent does its work internally
                              composes prompt → LLM → parser → extraction

LangChain                   = the materials both are built from
```

The orchestrator is the traffic controller. Pipelines are the engine inside each vehicle. Course 3 taught the blueprint. Course 2 teaches the plumbing. Course 4 teaches MCP — which AgentLean studied and then deliberately excluded (§39, §63); the tool layer is `@tool` functions, not a protocol.

This two-level framing is the correct one and is worth holding onto. The mistake the section originally made was applying it one level too high — treating the phase executor as "one vehicle with one engine," when the executor is itself a node whose tool dispatch is decided at runtime.

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

**Priority-based Resolution** — a ranking rule decides, not a vote. Maps to Memory Prioritization and Conflict Resolution (Section 38, Gap 22) — when `artifacts` conflicts with a recent message, priority rules decide, not a vote.

---

### Synchronization — Two Sub-Patterns

**Synchronous** — agents wait for each other before proceeding. RunnableParallel's synchronisation barrier (Section 28) — all branches complete before next stage runs.

**Asynchronous** — agents progress independently without waiting. What the Observer Agent (Gap 24) needs — monitoring system state in the background without blocking the main coaching flow.

---

### Complete Mapping to Agent Improve

```
Agent Improve Coordination Pattern
├── Control Flow
│   ├── Hierarchical    → Supervisor → Phase Subgraphs (§20, §23)          ✅ in refactor scope
│   ├── Sequential      → DMAIC phase order via STATIC edges (§44)         ✅ in refactor scope
│   ├── Parallel        → RunnableParallel inside nodes (§28)              ✅ in refactor scope
│   ├── Iterative       → Level 2 per-field cycle (§5, §19) + the
│   │                     4-layer gate loop, cap 3 (§68)                   ✅ in refactor scope
│   └── Peer-to-peer    → NOT USED — DMAIC requires strict hierarchy       ✅ correctly absent
│
├── Consensus
│   ├── Voting          → Debate agents for root cause validation (§22)    ⏸ deferred, §87 item 10
│   └── Priority-based  → Memory hierarchy in the coach prompt (§38 22a)   ✅ in refactor scope
│
└── Synchronization
    ├── Synchronous     → Parallel fan-out/fan-in inside phase nodes       ✅ in refactor scope
    └── Asynchronous    → Observer Agent background monitoring (§43)       ⏸ deferred, §87 item 14
```

*Two entries changed status materially during the review. **Priority-based resolution** was marked "not implemented"; §38's memory-hierarchy paragraph (Gap 22a) implements it, and it is the only consensus mechanism in refactor scope. **Iterative** was marked partial for want of a rubric; §42 supplies the rubric and §68 supplies the loop.*

---

### What This Taxonomy Adds

A single index against which every coordination decision in Agent Improve can be checked. Every coordination need falls into exactly one of these seven leaf categories. This is useful both as a completeness check (have we considered every pattern type) and as a vocabulary for discussing the architecture precisely with Claude Code during the refactor.

**Status summary:**
- In refactor scope: Hierarchical, Sequential, Parallel, Iterative, Priority-based, Synchronous (6/8)
- Correctly absent: Peer-to-peer (1/8)
- Deferred to v2.2: Voting (§87 item 10), Asynchronous / Observer (§87 item 14)

### Gap Register
No new gap number — this section is a classification index, not implementation. Use the table as the checklist when validating that the refactor design covers every required coordination pattern.

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

| Technique | Where It Already Appears | Status |
|---|---|---|
| Rank Aggregation | = Reciprocal Rank Fusion (§33) | ✅ In refactor scope |
| Weighted Aggregation | = memory-hierarchy paragraph in the coach's system prompt (§38, Gap 22a) | ✅ In refactor scope |

Same mechanisms, different application — Rank Aggregation merges search-result orderings, Weighted Aggregation ranks memory sources by authority. Both are ratified; neither needs anything from this section.

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
**Gap 28 — deferred to v2.2, §87 item 11.** Distinct from Gap 16 (rank aggregation over search results) and Gap 22a (weighted aggregation over memory sources); this is specifically about combining confidence and quality signals when assessing whether a coaching decision such as a proposed root cause is well-supported.

It is deferred because **its signal sources do not exist yet**. `advocate_confidence` in the example above comes from the debate subgraph (§22), which is itself deferred to §87 item 10. Building an aggregation framework over one or two available signals would be premature. Promotion trigger: the §22 debate subgraph is implemented and producing confidence scores.

*Note that two of the five techniques in this section are already in the ratified design under different names — see the table above. What remains genuinely new is only the decision-quality-signal application.*

---

## 51. InsightForge Analytics — Complete Production-Grade Reference Implementation

*Source: Edureka Course 2 graded assignment reference material (also appears as "StrategicConsult Analytics" — same architecture, different cover story). This is the most complete, end-to-end runnable code reference captured anywhere in this document — five layers, fully wired, with an explicit problem-to-solution mapping at each layer.*

> **Status: structural reference only. Do not implement from the code here.**
>
> The five-layer architecture, the separation of concerns, and the governance discipline are sound and directly applicable. Several of the specific classes are deprecated. This table maps each layer's deprecated pattern to its ratified replacement — read it before reading the code.
>
> | §51 Layer | Deprecated pattern | Ratified replacement |
> |---|---|---|
> | 1 — Workflow | `OutputFixingParser`, `parse_with_retry` | Native structured output (§82); `DMAICGraderMiddleware` (§42) |
> | 2 — Routing | `create_react_agent` | `create_agent` with per-phase tool binding (§39, §50) |
> | 3 — Transform | Scoring / ranking — **not deprecated** | Keep as-is |
> | 4 — Retrieval | `MultiQueryRetriever`, `BM25Retriever`, `ConversationSummaryMemory`, `ConversationEntityMemory`, `VectorStoreRetrieverMemory` | `rag_lookup_*` tools with multi-query + RRF (§32, §33); `SummarizationMiddleware` (§36); `AzureBlobStore` (§52a) |
> | 5 — Governance | Risk gate, metrics | Four-layer validation stack (§68), `DMAICGateValidator` (§48), evaluation metrics (§75) |
>
> **What is genuinely valuable here and appears nowhere else in this document:** the end-to-end assembly view, the risk-gate trigger conditions, the routing-strategy comparison table, the practitioner reflection on domain-varying confidence thresholds, and the governance metrics table. Those are called out where they appear.
>
> **This section produces no new architectural decisions.** It is a "how the pieces fit together" reference, not a source of implementation guidance.

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
Fallback score of 0 ensures malformed outputs sink to the bottom rather than crashing the ranker. The `reason` field makes scoring transparent and auditable — directly relevant to the per-criterion feedback discipline in §42.

*Layer 3 is **not deprecated**. The scoring and ranking pattern, and specifically the defensive fallback-to-zero, are worth keeping as written.*

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
**The conceptual pattern worth preserving despite the deprecated classes:** an adaptive classifier runs BEFORE retrieval — cheap intent analysis (keyword matching on temporal and domain markers) deciding which memory layers are worth querying, preventing expensive unnecessary searches.

This pattern survives the class-name deprecation intact. It is **not** ratified as a refactor addition — the ReAct loop already decides whether retrieval is needed, driven by tool descriptions — but it is worth recording as a v2.2 optimisation. If retrieval cost per turn becomes a concern, a lightweight classifier could be implemented either as guidance in the coach's system prompt or as a `wrap_tool_call` middleware hook (§80).

**Multi-query retrieval + RRF fusion — the right pattern, the wrong classes:**

*⚠️ `MultiQueryRetriever` and `BM25Retriever` both moved to `langchain-classic` in the LangChain 1.0 namespace split, and `MultiQueryRetriever` is deprecated even there (§32). The **RRF function below is correct and framework-independent** — it is essentially the ratified implementation in §33. Take the fusion function; leave the retriever classes.*
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
This is the concrete implementation of the self-correcting queries pattern. **Not adopted** — multi-query + RRF is the ratified proactive equivalent (§38). Two ideas inside it *are* adopted, though, and are worth extracting: **a retrieval miss is a logged event, not a silent failure**, and **max iterations reached triggers an explicit low-confidence flag plus human review** rather than degrading quietly. Both appear in the ratified design as `step_log` entries (§18) and the §69 Level 4 escalation.

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
**The risk gate's four trigger conditions** (LOW_CONFIDENCE, SENSITIVE_TOPIC, HIGH_RETRY_COUNT, RETRIEVAL_MISS) are a directly usable template — they sit precisely where the grader (§42) and the HITL gate (§2) intersect: output that fails routes to human review rather than auto-committing to the store or case index. HIGH_RETRY_COUNT maps to the shared 3-attempt cap across the four validation layers (§68), and its escalation path is §69 Level 4.

**The four metrics table above is directly applicable to §75's evaluation design.** Pipeline Success Rate, Retry Frequency, Retrieval Relevance, and Reasoning Accuracy are a sound production metric set; note especially that *Retry Frequency is a leading indicator* — it rises before success rate drops, which makes it the right thing to alert on.

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

**Direct relevance to Agent Improve:** the threshold-varies-by-domain problem recurs exactly when comparing confidence thresholds across DMAIC phases. Define-phase completeness and Analyse-phase root-cause-validation confidence are not comparable on the same numeric scale — the same finding as "market vs regulatory" above. **Any single global confidence threshold across all five phases should be treated with suspicion.** This is why §42's rubrics are per-phase rather than one shared rubric, and why §87 item 6 defers similarity-threshold calibration until there are retrieval-quality metrics to calibrate against.

*(The second reflection — markdown code fences around JSON — is largely obsolete. Native structured output means the model returns typed values rather than text that has to be parsed, so there is no fence to strip. The prompt-discipline half of the lesson still holds.)*

### Gap Register Note

No new gap number. This section is a **structural reference** — the assembly view, the risk gate, the routing comparison, the practitioner reflection, and the metrics table. It is **not** the implementation reference for the phase executor; §23 (subgraph structure), §39 (tools), §42 and §68 (validation), and §33 (retrieval) are. Read §51 to see how the pieces connect, then build from those sections.

---

## 85. LangSmith 2026 Additions — Fleet, Sandboxes, Context Hub, Engine

*Source: LangChain official announcements (Interrupt 2026 conference blog), LangSmith Fleet documentation (langchain.com/langsmith/fleet), multiple independent 2026 sources. Verified March-June 2026.*

### What Changed

> **Status: knowledge-only.** LangSmith remains wired for tracing and evaluation (§1, §75); none of the four additions below is adopted in the refactor. Each has a clear trigger recorded in place.

§1 and §75 documented LangSmith as it stood mid-2025 — primarily observability and evaluation. LangSmith has since expanded into a full agent engineering platform. This section documents the additions.

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

**What it is:** Versioned storage for the instructions and policies agents follow.

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

| Existing Section | Relationship |
|---|---|
| §1 (LangSmith basics) | SmithDB and Messages View are automatic upgrades — nothing to do |
| §83 (Agent Skills) | `ContextHubBackend` is the alternative to `FilesystemBackend`; deferred to the multi-deployment stage |
| §44, §45 (governance) | Fleet is the productised, enterprise form of the three-layer governance system. Code-level governance is sufficient at three agents and gives more control. |
| §75 (regression testing) | Engine is the proactive complement to §75's reactive testing — it finds failure patterns before you write tests for them |
| §76 (Docker) | Sandboxes are for testing, containers for deployment |
| §78 (developer menu) | Sandboxes could replace parts of the menu-driven testing pattern |

### Gap Register Note

No new gap number. **None of these is adopted in the refactor**, and each has a specific trigger:

| Addition | Adopt when |
|---|---|
| Fleet | AgentLean runs across multiple customer organisations needing cross-customer governance |
| Sandboxes | Useful sooner than the others — mock Azure endpoints for running the §75 eval suite without consuming production credentials |
| Context Hub | Skills are shared across multiple deployments (§83 storage-backend decision) |
| Engine | Production traffic is sufficient for patterns to emerge — roughly >1000 coaching turns per week |

*Note the recurring shape of these triggers: every one of them is "when there is more than one deployment or more than one customer." That is the same boundary that makes MCP unjustified (§39), the Observer Agent premature (§87 item 14), and multi-tenant filtering a v2.2 concern (§87 item 1). It is worth knowing that the single-tenant assumption is load-bearing in more places than it looks.*

---

# APPENDIX

*Every “defer” decision from the review, with its promotion trigger.*

---

## 87. v2.2 Deferred Backlog

*New section, authored during the batch commit. Deferred items evaporate without a tracking home, and per-section Gap Registers scatter the picture. This is the one consolidated place to look when planning v2.2.*

### What Belongs Here, and What Does Not

**This backlog tracks genuinely premature items:** beta APIs, research workstreams needing their own design phase, and capabilities with known unsolved problems.

**It does not track things needed for production that were lazily deferred.** That distinction was drawn explicitly during the review:

> *"For me, what we have is a deprecated and not production-ready Agent Improve that after my trainings we upgrade to the latest architecture of LangChain and LangGraph. After we complete this document we begin with the full-scale refactoring."*

The refactor is a full rebuild to production grade, not an incremental patch. Anything required for a production-grade system belongs **in scope**, not on a later list. Two items were moved *out* of this backlog during the review on exactly those grounds:

| Item | Was | Now |
|---|---|---|
| Saga / compensating actions (§49) | "defer to §87" | **IN SCOPE** — correctness under gate reopening is a production requirement |
| Cache infrastructure for Level 3 fallback (§67) | "defer to §87" | **IN SCOPE** — "full scale with cache infrastructure, we need to do this right" |

**Items architecturally excluded, not deferred.** MCP-dependent capabilities — real-time SAP data, external verification benchmarks, an AgentLean MCP server — are **not** in this backlog. They are excluded by §39. There is no promotion trigger because there is no path to promotion: the data channel is always uploaded documents via `improve_evidence_index`.

### The Backlog

| # | Source | Deferred capability | Why deferred | Promotion trigger |
|---|---|---|---|---|
| 1 | §32, case-history tool | Multi-tenant filtering on `improve_case_index` | ARCHITECTURE.md does not address multi-tenancy; single-tenant assumed | Agent Improve deployed to multiple organisations |
| 2 | §35 | Per-source weighting in RAG fusion | Only useful with fundamentally different retrieval sources; the current three tools query the same corpus type | A fourth retrieval source is introduced (e.g. an external best-practice database) |
| 3 | §37 | Per-turn episodic entries in `improve_case_index` | Would multiply case-index writes 30–50×; gate-level granularity is sufficient | Coaching evaluation shows gate-level summaries lose actionable detail |
| 4 | §37 | Mid-phase summary persistence to `improve_case_index` | `SummarizationMiddleware` keeps the compressed summary in `messages[]` for the current session; gate-pass covers durability | Belts frequently resume in-flight cases weeks later and the coach needs historical mid-phase context |
| 5 | §37 | LangSmith trace-based coaching learning | Substantial feature needing its own design phase, evaluation criteria, and data schema | **No signal needed — this is a v2.2 priority workstream** |
| 6 | §37 | Similarity-threshold calibration for retrieval | Requires retrieval-quality metrics that do not exist yet | The §75 evaluation dataset is populated with representative queries and expected results |
| 7 | §37 | Dynamic top-k based on remaining context | Requires middleware to expose context-remaining state cleanly | Fixed top-k causes context-budget problems in production |
| 8 | §38 | Reactive self-correcting query restructuring | Multi-query + RRF is the proactive equivalent (§32, §33); the reactive form is redundant unless the proactive one proves insufficient | Retrieval evaluation shows multi-query variants systematically missing even after RRF fusion |
| 9 | §40 | Feedback-driven chunk score adaptation | Three known problems: causal attribution (all chunks credited equally for gate passage regardless of contribution), cold drift (demoted chunks stop being retrieved and cannot recover), and infrastructure (Azure AI Search has no native per-chunk boost — an external score table is required). Likely needs LangSmith trace analysis for retrospective attribution, or offline evaluation runs, rather than real-time in-line adjustment. | Retrieval evaluation shows systematic misses that static ranking and metadata filters cannot fix, **and** a dedicated v2.2 research workstream is established |
| 10 | §22, §48 | Adversarial debate subgraph for root cause validation (Analyse phase) | Analyse-only feature; depends on the base coaching loop working in production first; adds 2–3 LLM calls per root-cause evaluation | Base coaching loop stable in production, with the Analyse coach producing root causes that need adversarial stress-testing |
| 11 | §47 | Opinion aggregation framework for combining decision-quality signals (Gap 28) | **Its signal sources do not exist yet** — `advocate_confidence` comes from the item 10 debate subgraph | The §22 debate subgraph is implemented and producing confidence scores |
| 12 | §79 | `DeltaChannel` for checkpoint compression | Beta API, and not needed until sessions exceed roughly 200 turns | Long-running DMAIC projects accumulate checkpoint-size problems in production |
| 13 | §1, §52a | Migrate `AzureBlobCheckpointSaver` + `AzureBlobStore` → `PostgresSaver` + `PostgresStore` | The Blob checkpointer works for single-developer refactoring; adding PostgreSQL during the heaviest refactoring period is unnecessary infrastructure complexity | **Post-refactor testing complete, before production launch with real Belts.** Provision Azure Database for PostgreSQL (~€12–15/month). Migration is small: change constructor and connection string, run existing tests against PostgreSQL. |
| 14 | §43 | Observer Agent — system-wide monitoring across all Belts and projects (completion rates, coaching quality drift, system health, pattern detection) | Not a per-project coaching component; requires production traffic across multiple projects to produce meaningful patterns | Multiple concurrent DMAIC projects in production generating enough traffic for pattern analysis |
| 15 | §37, §60, Finding 27 | **Multi-source knowledge index** — add `source_document` and `tenant_id` to `improve_knowledge_index`, priority-ordered retrieval filter in `rag_lookup_methodology`, and phase-classifier re-evaluation for non-BB-eBook documents | The refactor builds against the BB eBook as the single knowledge source. The architecture already supports more: the index needs two fields and the filter needs one additional clause. Adding it now complicates ingestion, retrieval and testing with no second document to test against | A customer supplies their own improvement methodology (internal BB guide, company process standards) that must sit alongside or ahead of the BB eBook |
| 16 | §67 / DORA | **Geographic redundancy** — a secondary Azure OpenAI deployment in a second EU region, promoting the fallback chain from four levels to five | Infrastructure provisioning (region selection, quota, connection-string management) deferred until the base refactor is stable. Not a v2.1 blocker | **Before production launch with real Belts.** DORA compliance requires it before any regulated-entity deployment |

#### Item 15 — Multi-source knowledge index, in more detail

**The problem it solves.** `improve_knowledge_index` currently has no source separation — every chunk looks the same. If a customer uploads their own improvement guide alongside the BB eBook, the coach cannot tell standard methodology from company-specific guidance, and conflicting advice from the two sources arrives with no attribution.

**Three issues, all of which need the same two fields:**

1. **No source separation** — chunks from different documents mix with no attribution
2. **Phase classifier tuned to the BB eBook** — the per-chunk keyword scoring of §7.1.2 was calibrated against one book's terminology; a different document may misclassify
3. **No tenant isolation** — Company A's methodology would be visible to Company B's Belts

**Schema addition:**

```
source_document: str    — "bb_ebook_v11.1" or "acme_corp_guide_v2"
tenant_id: str          — which company (multi-tenant isolation)
```

**Retrieval filter, priority-ordered:**

```python
# Default — BB eBook only
filter = f"phase_relevance eq '{phase}' and source_document eq 'bb_ebook_v11.1'"

# Customer with their own guide — theirs first, BB eBook as fallback
filter = (f"phase_relevance eq '{phase}' and "
          f"(source_document eq 'acme_corp_guide_v2' or "
          f" source_document eq 'bb_ebook_v11.1')")
```

**Ingestion changes** (`scripts/ingest_knowledge.py`): accept `source_document` and `tenant_id` parameters, and re-evaluate the phase classifier for non-BB documents whose terminology and structure differ.

**Coaching impact — and why it stays consistent with the rubric.** The coach weaves retrieved content into its own voice; it does not show the Belt citation blocks or external links (`COACHING_QUALITY_RUBRIC`, §42). With customer content available the coach can say *"your company's improvement guide recommends…"* and fall back to the BB eBook for topics the company guide does not cover. The attribution is in the coaching voice, not in a footnote the Belt has to chase.

**Note the overlap with item 1.** Multi-tenant filtering on `improve_case_index` and `tenant_id` here are the same problem on two indexes, and both fire on the same trigger — deployment to a second organisation. They should be planned together.

### Reading the Backlog

Three observations worth having in view when planning v2.2:

**Item 13 is not optional and not far away.** It is the only entry with a *scheduled* trigger rather than a conditional one — it happens before production launch, full stop. It sits in this list because of *sequencing*, not because it might never happen.

**Items 10 and 11 are a chain.** Opinion aggregation depends on the debate subgraph for its signals. Neither is worth starting without the other, and both depend on the base coaching loop being stable.

**Items 6, 7, and 9 all wait on the same thing: retrieval quality metrics.** None can be designed responsibly without the §75 evaluation dataset populated with representative queries. That makes §75 the highest-leverage unlock in this table — one deliverable moves three items from "cannot be designed" to "can be evaluated."

A fourth observation, carried from §85: several triggers reduce to *"when there is more than one deployment or more than one customer."* Items 1 and 14, plus every LangSmith platform addition in §85, sit behind that single boundary. The single-tenant assumption is load-bearing in more places than it appears.

### Adding to This Backlog

Each entry needs four things, and an entry missing any of them is not a deferral — it is a guess:

1. **Source section(s)** in this document
2. **Description** of the deferred capability
3. **Why it was deferred** from the refactor
4. **The prerequisite condition or signal** that would promote it

Point 4 is the one that decays first. "Later" is not a trigger. If nobody can state what would have to become true, the item is either in scope or out of scope, and pretending otherwise just moves the decision somewhere it will not be revisited.

*Cross-references: §25 (Gap Register — the in-scope counterpart to this list), §39 (what is excluded rather than deferred), §75 (the evaluation dataset that unlocks items 6, 7, and 9).*
