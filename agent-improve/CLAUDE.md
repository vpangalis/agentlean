# Agent Improve — CLAUDE.md Hard Rules
# Enforced in every Claude Code prompt. Never bypass these rules.

## Industry scope

Agent Improve is industry-agnostic — it serves any vertical including
manufacturing, railway, healthcare, finance & banking, telecom, and logistics.
The railway maintenance context is used only as a worked example.
No prompts, labels, or field names may assume a specific industry.
All examples in prompts must use generic placeholders or be drawn from
the case's own domain context loaded from blob at session start.

## Where classes are allowed (and only here)

Classes are permitted ONLY in these designated files:
- core/state.py         — ImproveGraphState(TypedDict, total=False) — ONE TypedDict only
- phases/{phase}/schema.py  — PhaseInput + nested models (Pydantic v2 BaseModel)
- storage/models.py     — CaseDocument, PhaseRecord, RegistryEntry etc (Pydantic v2)
- gateway/schemas.py    — API request/response envelopes (Pydantic v2)
- core/citations.py     — CitationRecord, CitationBundle (Pydantic v2)

All other files contain module-level functions ONLY. No classes anywhere else.
This includes: all node files, graph.py, llm.py, blob.py, retriever.py, escalate.py.

## Graph topology rules

The Agent Improve graph has exactly this node structure per phase:
  orchestrate_{phase} -> validate_{phase} -> (pass: next phase | fail: loop | escalate)
No new node types may be added without a design decision in the architecture chat.
The graph must remain: 10 phase nodes + 1 escalation node = 11 nodes total.

## Inherited from Agent Resolve

- Nodes are module-level functions: def node_name(state: ImproveGraphState) -> dict
- One node per file — file name = function name = graph node name
- Nodes return dict slices only — never Pydantic models, never full state
- Never instantiate AzureChatOpenAI directly — always use get_llm() factory
- Tools are @tool decorated functions in knowledge/tools.py — no classes

## Agent Improve specific

- ImproveGraphState is the only TypedDict — never create a second state class
- phases/{phase}/schema.py is the only place Pydantic PhaseInput models live
- core/citations.py is the only place CitationRecord is defined — never duplicated
- knowledge/tools.py is the only place @tool functions live
- storage/models.py is the only place CaseDocument and storage models live
- Every orchestrate_{phase}.py MUST call _reflect() before returning
- No node may import from another node's file — cross-phase data via state only
- All prompts live in core/prompts.py as constants — no prompt strings in node files
- escalate.py is the only escalation node — fires after GATE_MAX_ATTEMPTS failures

## UI and language rules

- No methodology jargon in any team-facing string — plain language always
- Technical terms appear only as small secondary grey labels in the capture panel
- Every AI data request must include a concrete example with column names
- Every AI suggestion using cross-agent data must include a visible source citation
- Citation format: agent_origin, index_name, document_id, relevance_summary

## No-Go list

- Never create a second TypedDict or state class
- Never put prompts inline in node files
- Never instantiate AzureChatOpenAI directly
- Never write to Agent Resolve indexes — read only via knowledge/tools.py
- Never duplicate the CitationRecord model
- Never use methodology jargon in team-facing strings
- Never add a new graph node type without architecture approval
- Never add classes outside the designated schema files listed above
