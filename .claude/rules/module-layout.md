---
paths:
  - "agent-improve/backend/core/checkpointer.py"
  - "agent-improve/backend/core/citations.py"
  - "agent-improve/backend/core/errors.py"
  - "agent-improve/backend/core/graph.py"
  - "agent-improve/backend/core/llm.py"
  - "agent-improve/backend/core/reliability.py"
  - "agent-improve/backend/core/state.py"
  - "agent-improve/backend/core/store.py"
  - "agent-improve/backend/core/substate.py"
  - "agent-improve/backend/gateway/routes.py"
  - "agent-improve/backend/gateway/schemas.py"
  - "agent-improve/backend/knowledge/computation.py"
  - "agent-improve/backend/knowledge/retriever.py"
  - "agent-improve/backend/knowledge/tool_args.py"
  - "agent-improve/backend/knowledge/tools.py"
  - "agent-improve/backend/middleware/coherence.py"
  - "agent-improve/backend/middleware/contradiction.py"
  - "agent-improve/backend/middleware/grader.py"
  - "agent-improve/backend/middleware/skills.py"
  - "agent-improve/backend/middleware/state_injection.py"
  - "agent-improve/backend/storage/blob.py"
  - "agent-improve/backend/storage/models.py"
  - "agent-improve/backend/validation/gate_validator.py"
  - "agent-improve/backend/validation/schemas.py"
---
# §2 — Where classes are allowed

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

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
- `middleware/state_injection.py` — `BeforeModelStateInjection(AgentMiddleware)`, `before_agent` hook
- `middleware/contradiction.py` — `ContradictionDetectionMiddleware(AgentMiddleware)` (§8.8)
- `middleware/coherence.py` — `CoherenceMiddleware(AgentMiddleware)` (§8.9)

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


## Never

*§14's bans that belong to this file — 1 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never add classes outside the designated files in §2
