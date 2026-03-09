# CLAUDE.md — CoSolve Hard Rules for Claude Code
# Version: 3.0 — 2026-03-09
# Changes from v2.0: LLM roles replace Azure deployment names in node code

READ THIS COMPLETELY BEFORE WRITING ANY CODE.
Every rule is non-negotiable. Violation = reject output, start again.

---

## BEFORE ANY CHANGE

1. Read ARCHITECTURE.md
2. Read REFERENCE.py
3. Read the file you are about to change
4. State what you will change and what you will NOT touch

---

## HARD RULES

### Nodes
- Nodes are module-level functions — NEVER classes
- One node per file. Filename = function name = graph node name
- Signature: `def node_name(state: IncidentGraphState) -> dict`
- Return a dict slice — only the keys this node produces
- NEVER return a Pydantic model from a node
- NEVER call `.model_dump()` in a node
- NEVER call `cast()` anywhere
- NEVER define a prompt string inside a node file — import from prompts.py
- Reflection nodes follow the exact same pattern — no base class, no inheritance

### LLM — ROLE NAMES ONLY
- NEVER pass an Azure deployment name directly to `get_llm()`
- NEVER write `get_llm("gpt-4o", ...)` or `get_llm("gpt-4o-mini", ...)` or `get_llm("operational-premium", ...)`
- ALWAYS use a logical role name: `get_llm("intent", ...)` or `get_llm("reasoning", ...)`
- Role-to-deployment mapping lives ONLY in config.py (`LLM_INTENT_DEPLOYMENT`, `LLM_REASONING_DEPLOYMENT`)
- Each node declares its own role and temperature explicitly

### State
- ONE state class: `IncidentGraphState` in `backend/state/__init__.py`
- NEVER create a new TypedDict, dataclass, or Pydantic output model for nodes
- Node outputs are plain dicts stored as state fields
- State NEVER crosses the wire to the UI

### Tools
- ALL retrieval is done through @tool functions in `backend/tools/__init__.py`
- NEVER call CaseSearchClient, EvidenceSearchClient, KnowledgeSearchClient directly from a node
- NEVER create a new search client class
- Tool docstrings are mandatory — they are what the LLM reads to decide which tool to use

### Prompts
- ALL prompts live in `backend/prompts.py` as module-level string constants
- NEVER define a prompt inline inside a node function
- Prompt content is NOT changed during refactor — only moved to prompts.py

### API Contract
- ONLY `CoSolveRequest` and `CoSolveResponse` cross the UI/backend wire
- `routes.py` is the only place that translates state ↔ envelope
- NEVER expose IncidentGraphState fields directly in an API response

### Files
- Do NOT create new files without explicit instruction
- Do NOT modify files outside the scope of the current phase
- Files marked STAYS UNTOUCHED in ARCHITECTURE.md are never modified
- Do NOT delete any code — mark deprecated code with `# DEPRECATED:` comment

### Classes
- Node files: no classes
- tools/__init__.py: no classes — only @tool functions and client singletons
- Permitted classes: `LLMProvider` in llm.py, Pydantic models in schemas.py,
  `IncidentGraphState` in state/__init__.py

### Minimum Footprint
- Smallest possible change that solves the problem
- Audit existing code before writing anything new

---

## 4 POST-CHANGE CHECKS (run after EVERY change)

1. `python -m py_compile <modified_file>` — must pass
2. No new standalone functions outside permitted locations
3. No new classes outside permitted locations
4. No Azure deployment name strings in any node file

---

## NO-GO LIST

- `cast()` anywhere in the codebase
- `.model_dump()` in any node file
- `__init__` in any node file
- `from backend.infra.* import` inside a node file
- `from backend.retrieval.hybrid_retriever import` inside a node file
- New Pydantic output models for nodes
- Azure deployment name strings inside node files (e.g. `"gpt-4o"`, `"operational-premium"`)
- `AzureChatOpenAI(...)` instantiated directly in a node
- Prompts defined inline inside node functions
