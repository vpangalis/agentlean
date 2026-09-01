<!--
Review document: agent-improve/docs/RESTRUCTURE_PLAN.md
Normalised: UTF-8 without BOM, LF line endings
Purpose: tracked review artefact for cross-session architectural reference
Added in: f44e5c7
-->

# REFACTORING_AGENT_IMPROVE.md — Restructuring Plan

## What this is

The current REFACTORING_AGENT_IMPROVE.md has correct, ratified content but is ordered
chronologically (the order topics were learned during training). This plan reorders
the same content into a logical reference guide structure grouped by what a reader
would look up, not when it was written.

## Rules

- NO content changes. Only reordering.
- Every section moves intact — heading, body, code blocks, cross-references.
- All `§N` cross-references in the body must still resolve after reordering.
  The section NUMBERS stay the same (§1 is still §1, §42 is still §42) — only
  their POSITION in the file changes. This avoids a cascading renumber that
  would break CLAUDE.md and ARCHITECTURE.md references.
- The Document Navigation topic index at the top must be rebuilt to reflect
  the new Part structure.
- The Overview Architecture block stays at the top, before Part 1.
- The Terminology Reference stays at the top, before §1.

## Target structure

```
FRONT MATTER (keep as-is)
  Title, Purpose, Document Navigation (rebuild index), Overview Architecture,
  Terminology Reference

PART 1 — FOUNDATIONS (core concepts a reader needs first)
  §1   LangGraph Persistent Checkpointing
  §2   Human-in-the-Loop (nine-step gate pattern)
  §10  Subagent State Management
  §5   Planner / Executor Model
  §20  Supervisor / Worker Architecture
  §23  Modular Subgraph Architecture
  §11  Recursive Planner / Executor — Every Level Plans

PART 2 — AGENT CONSTRUCTION (how the coach is built)
  §82  LangChain 1.0 ProviderStrategy — Native Structured Output
  §80  LangChain 1.0 AgentMiddleware — The Six Hooks Foundation
  §81  LangChain 1.0 Standard Content Blocks
  §42  DMAICGraderMiddleware — Self-Evaluation and Correction Loop
  §83  Agent Skills Specification — SKILL.md Standard
  §84  SkillsMiddleware in deepagents
  §36  Short-Term and Long-Term Vector Memory (SummarizationMiddleware)
  §38  Hybrid Memory Stack and Context Orchestration Layer (decomposed)

PART 3 — RETRIEVAL ARCHITECTURE (how knowledge is found)
  §32  Multi-Query Retrieval
  §33  RAG Fusion
  §34  Multi-Hop Reasoning
  §71  Multi-Hop Retrieval — Gap 17 Formally Closed
  §35  Query Voting and Weighted Fusion (knowledge-only)
  §37  Memory Patterns in Agentic Systems (taxonomic scaffold)
  §40  Metadata as a Signal: Freshness, Authority, and Context
  §41  Target Retrieval Pipeline — System-Level Workflow

PART 4 — QUALITY AND VALIDATION (how output is checked)
  §48  Reflection Nodes vs Consensus Modeling
  §68  Decision Validation Against Business Constraints (four-layer stack)
  §69  Validation Layer Placement (firing contexts, transparency principle)
  §29  OutputFixingParser (historical — superseded by §82)
  §22  Debate Agents and Consensus Voting (v2.2 — Analyse phase)

PART 5 — RELIABILITY AND FAILURE HANDLING
  §79  LangGraph 1.2 Native Reliability Primitives
  §49  Saga-Based Transactions and Compensating Actions
  §66  Circuit Breaker, Context Recovery, Safe Reopen
  §67  Self-Healing Fallback Chain
  §15  Failure Patterns in Long-Running Agent Workflows (historical context)

PART 6 — ORCHESTRATION AND DATA FLOW (how phases connect)
  §17  InsightForge Mapping — Refactor Specification (SupervisorState)
  §18  Lab Code — PhaseState Schema
  §19  Multi-Step Task Chaining (store-mediated handoff)
  §21  State Passing Across Agent Nodes
  §70  Inter-Stage Data Dependency — Outputs Become Inputs
  §52  MAJOR FINDING — Checkpointer + Store Architecture
  §52a AzureBlobStore and Multi-Chain Persistence

PART 7 — DEPLOYMENT AND INFRASTRUCTURE
  §55  LangServe Archived / FastAPI Decision
  §72  LangGraph Server Evaluation
  §73  Langfuse — Open-Source LangSmith Alternative
  §74  Agent API Versioning
  §75  Evaluation Dataset Design and Regression Testing
  §76  Docker Containerisation
  §77  AgentLean Frontend Feedback Requirements
  §78  Menu-Driven Developer Orchestration

PART 8 — GOVERNANCE AND ANTI-DRIFT
  §24  Governance and Debugging — Production Readiness Framework
  §44  Consolidated Architecture Diagnosis — Agent Resolve Benchmark
  §45  Anti-Drift Governance Design
  §50  CRITICAL VERSION CORRECTIONS
  §53  MAJOR FINDING — Built-In Middleware
  §86  Verified Claude Code Hook Mechanics
  §43  Common Agent Roles and Responsibilities

PART 9 — MCP KNOWLEDGE (not implemented — pedagogical reference)
  §57  CORRECTION — MCP is Agent-to-Tool, Not Agent-to-Agent
  §58  CORRECTION — MCP Functional Layers
  §59  MCP Server Implementation — FastMCP
  §60  Internal RAG Tools vs MCP Tools
  §61  MCP Resources
  §62  MCP Server Ecosystem
  §63  MCP Evaluated for AgentLean — and Rejected
  §64  MCP-Based Agent Architecture — Production Design Principles
  §65  MCP Server Caching
  §39  Knowledge Tools in Augmented Reasoning

PART 10 — COURSE HISTORY AND CONTEXT (training record — not operational)
  §9   Coursera / Edureka Multi-Agent Systems Notes
  §14  Course Curriculum Map
  §26  Orion Intelligence — Graded Assignment Submission
  §31  Course 2 Progress Notes
  §56  Course 4 — Stale Deployment Warning
  §54  Correction to Section 42 — RubricMiddleware (historical)

PART 11 — REFERENCE (patterns, diagrams, taxonomies)
  §3   Time Travel Debugging & Snapshot Analysis
  §4   DAG Execution vs LangGraph Cycles
  §6   Multi-User Production Gaps
  §7   Full Dependency Chain
  §8   Implementation Sequencing Decision
  §12  From Execution Control to Task Delegation (Edureka Slide)
  §13  Complete Planner/Executor Flow Diagram
  §16  Architectural Debt Acknowledgement
  §25  Architectural Gaps — Complete Register
  §27  LCEL Pipelines — Why We Never Used Them
  §28  LCEL Primitives — RunnableParallel, RunnableBranch, Pipe Operator
  §30  Semantic Routing vs LLM-Assisted Routing
  §46  Coordination Pattern Taxonomy
  §47  Opinion Aggregation Techniques
  §51  InsightForge Analytics — Reference Implementation
  §85  LangSmith 2026 Additions

APPENDIX
  §87  v2.2 Deferred Backlog
```

## Verification after restructuring

1. Every `## N.` heading in the file must appear exactly once
2. Every `§N` reference in the body must point to a heading that exists
3. The Document Navigation index must list every section in its new Part
4. No content was added, removed, or modified — only moved
5. `wc -l` should be within ±5 lines of the original (Part headers added)
6. Code blocks must be intact (balanced ``` fences)
