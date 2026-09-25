---
paths:
  - "agent-improve/backend/knowledge/tools.py"
  - "agent-improve/backend/knowledge/computation.py"
  - "agent-improve/backend/knowledge/tool_args.py"
---
# §5 — Tools

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

## 5. TOOLS

Defined in `knowledge/tools.py` (universal) and
`knowledge/computation.py` (per-phase), with Pydantic arg schemas in
`knowledge/tool_args.py`.

### 5.1 — The universal eight

Passed to every phase executor via `tools=`; signatures are in
`knowledge/tools.py` (`UNIVERSAL_TOOLS`):
- `rag_lookup_methodology`, `rag_lookup_evidence`, `rag_lookup_case_history` —
  one index each, multi-query + RRF (§7.2, §7.4)
- `propose_template` — fill-in template for the team
- `propose_diagram` — structured diagram JSON, **NOT SVG** (types in
  `core/diagrams.py`)
- `check_gate_status` — which required fields are populated / missing
- `request_human_approval` — interrupt for a human decision beyond the gate
- `load_evidence_series` — a column's typed values plus summary stats,
  **re-parsed from the case blob** (it stores no parsed values). Universal,
  not a computation tool: the universal set is where the I/O tools live.

**The superseded tool names are `search_improve_knowledge`,
`search_improve_cases` and `search_improve_evidence`.** No v2 code may
reference them.

**Two layers, and only the upper one is retired.** `knowledge/tools.py` is the
`@tool` layer the model calls; `knowledge/retriever.py` holds the
`search_knowledge` / `search_cases` / `search_evidence` functions those tools
call. **The tool layer is replaced by `rag_lookup_*`; the retriever layer keeps
its names** and its failure semantics (§7.2).

**The cross-agent tools** (`search_resolve_*`, `search_flow_vsm`) are neither
retired nor bound — see the Never list and
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §29.4.

**`record_field` is RETIRED and may not be reintroduced.** Field capture
happens through `response_format=CoachingResponse` on the executor
(§4.6).

### 5.2 — Per-phase tool binding

**Tool sets are per phase, not universal.** The per-phase partition is
owned by `COMPUTATION_TOOLS_BY_PHASE` in `knowledge/computation.py`; each
executor gets `UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]`. Read the
sets and totals there.

**No phase exceeds 16 tools.** Measure is at the ceiling with no margin; a
new tool that would push a phase past 16 is an amendment to
`../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56), not a routine addition —
revisit the ceiling before a ninth universal tool, not after.

**`imr_chart_limits` is the right chart whenever the Belt has one
measurement per period.** Never coach a Belt into inventing subgroups to fit
a batch chart.

**Each computation tool is a separate named tool.** Parameterised grouping
(one `calculate_sample_size(type, ...)` with a mode argument) is BANNED.

**All computation tools are pure functions.** No LLM call, deterministic,
unit-tested.

Tool decisions are the LLM's, not the graph's.

### 5.3 — Tool args via Pydantic schemas

Every `@tool` uses `args_schema=` with a Pydantic model from
`knowledge/tool_args.py`. No tools with raw signature inference.

### 5.4 — Docstrings are load-bearing

The tool docstring is how the model chooses between the three
retrieval tools. It is interface, not commentary.

Every retrieval tool docstring MUST state:
- **When to use it** — "I need methodology" vs "I need this project's
  data" vs "I need precedent from other projects"
- **Which index** it queries
- **Which vector field** it uses (`content_vector`, or `embedding` on
  `improve_case_index` until the §7.3 rename lands)
- **Which filters** are applied, and which are optional and default off

`rag_lookup_case_history`'s docstring must additionally carry the
multi-tenancy note for future engineers: if Agent Improve ever serves
multiple organisations, this tool must filter by tenant.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §29, §30, §31.*


## Never

*§14's bans that belong to this file — 6 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never add deepagents as a dependency while it is pre-1.0
- Never exceed 16 tools on a phase executor
- Never parameterise the computation tools into mode-argument groups
- Never delete or bind the four cross-agent tools (`search_resolve_*`,
  `search_flow_vsm`) — present, unbound, and binding one is an amendment
  (`../AGENTIC_ARCHITECTURE_REFERENCE.md` §29.4)
- Never use `MultiQueryRetriever`, `EnsembleRetriever`, or
  `OutputFixingParser`
- Never use the deprecated `Conversation*Memory` or
  `VectorStoreRetrieverMemory` classes
