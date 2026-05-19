# Agent Improve — CLAUDE.md Hard Rules
# Enforced in every Claude Code prompt. Never bypass these rules.

## Inherited from Agent Resolve

- Nodes are module-level functions: `def node_name(state: ImproveGraphState) -> dict`
- One node per file — file name = function name = graph node name
- Nodes return dict slices only — never Pydantic models, never full state
- Never instantiate AzureChatOpenAI directly — always use `get_llm()` factory
- Tools are `@tool` decorated functions in `knowledge/tools.py` — no classes

## Agent Improve specific

- `ImproveGraphState` is the only TypedDict — never create a second state class
- `phases/{phase}/schema.py` is the only place Pydantic PhaseInput models live
- `core/citations.py` is the only place `Source` / `CitationRecord` is defined — never duplicated
- `knowledge/tools.py` is the only place `@tool` functions live — all search tools in one file
- `storage/models.py` is the only place `CaseDocument` and storage models live
- Every `orchestrate_{phase}.py` MUST call `_reflect()` before returning — no exceptions
- No node may import from another node's file — cross-phase data travels through state only
- All prompts live in `core/prompts.py` as constants — no prompt strings inside node files
- `escalate.py` is the only escalation node — fires after GATE_MAX_ATTEMPTS consecutive failures

## UI and language rules

- No methodology jargon in any team-facing string — plain language always
- Technical terms appear only as small secondary grey labels in the capture panel
- Every AI data request must include a concrete example with column names and sample values
- Every AI suggestion using cross-agent data must include a visible source citation
- Citation format: agent_origin, index_name, document_id, relevance_summary

## No-Go list

- Never create a second TypedDict or state class
- Never put prompts inline in node files
- Never instantiate AzureChatOpenAI directly
- Never write to Agent Resolve indexes — read only via knowledge/tools.py
- Never duplicate the Source/CitationRecord model
- Never use methodology jargon in team-facing strings
