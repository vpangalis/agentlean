---
paths:
  - "agent-improve/backend/knowledge/tools.py"
  - "agent-improve/backend/knowledge/computation.py"
  - "agent-improve/backend/knowledge/tool_args.py"
---
# §5 — Tools

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## 5. TOOLS

Defined in `knowledge/tools.py` (universal) and
`knowledge/computation.py` (per-phase), with Pydantic arg schemas in
`knowledge/tool_args.py`.

### 5.1 — The universal eight

Passed to every phase executor via `tools=`:

```
rag_lookup_methodology(query: str, phase: str, top_k: int = 10) -> list[Document]
  improve_knowledge_index. Multi-query + RRF. Filters phase_relevance.

rag_lookup_evidence(query: str, case_id: str, top_k: int = 10) -> list[Document]
  improve_evidence_index. Multi-query + RRF. Filters case_id.

rag_lookup_case_history(query: str, top_k: int = 10,
                        exclude_current_case: bool = True) -> list[Document]
  improve_case_index. Multi-query + RRF. Yokoten — cross-case learning.

propose_template(template_type: str, fill_data: dict) -> str
  Fill-in template for the team. Types: problem_statement, sipoc,
  data_collection_plan, fishbone, etc.

propose_diagram(diagram_type: str, data: dict) -> dict
  Structured diagram JSON (NOT SVG). Types and schemas in
  core/diagrams.py. Frontend renders via SVG template library.

check_gate_status() -> dict
  Current phase gate readiness — which required fields are populated,
  which are missing.

request_human_approval(reason: str) -> str
  Triggers an interrupt awaiting human decision, beyond standard gate
  submission.

load_evidence_series(blob_path: str, column: str) -> dict
  A column's typed values plus n, mean, sigma, min, max — RE-PARSED from the
  case blob with step 6.11's parser. Retrieval finds WHICH file; this loads
  THE VALUES. Ratified 2026-09-09; built at step 6.12.
```

**`load_evidence_series` is universal rather than a computation tool, and that
is a classification rather than an exception.** §5.2's twenty are pure functions
with no I/O; this reads a blob. **The universal set is already where the
I/O-performing tools live** — all three `rag_lookup_*` call Azure AI Search,
this one calls Azure Blob. It stores no parsed values and re-parses instead,
because a second copy of the table is the drift the single-authority rule exists
to prevent.

**The superseded tool names are `search_improve_knowledge`,
`search_improve_cases` and `search_improve_evidence`** — the three `@tool`
functions in `knowledge/tools.py` today. No v2 code may reference them.

> **Corrected 2026-08-21.** This rule previously named `search_methodology`
> and `search_evidence`. **`search_methodology` exists nowhere in the
> codebase**, and **`search_evidence` is a live retriever function that §7.2
> requires to keep existing** — so this rule and §7.2 contradicted each other,
> and a grep for the retired names would have passed while every real one
> survived. **Verification depends on the literal strings**, which is why a
> wrong name here is not cosmetic.

**Two layers, and only the upper one is retired.** `knowledge/tools.py` is the
`@tool` layer the model calls; `knowledge/retriever.py` holds the
`search_knowledge` / `search_cases` / `search_evidence` functions those tools
call. **The tool layer is replaced by `rag_lookup_*`; the retriever layer keeps
its names** and its failure semantics (§7.2).

**Four further tools in `knowledge/tools.py` are neither retired nor bound** —
`search_resolve_cases`, `search_resolve_knowledge`, `search_resolve_evidence`,
`search_flow_vsm`. Read-only cross-agent tools, a distinct third category,
deliberately bound to no coach. Do not delete them and do not bind them:
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §29.4 states the three rules that bind first.

**`record_field` is RETIRED and may not be reintroduced.** Field capture
happens through `response_format=CoachingResponse` on the executor
(§4.6) — the coach emits `fields_captured` as structured output on every
turn, and the executor node writes each entry to `artifacts`. A tool
would make capture a decision the coach might skip; structured output
makes it part of every response by construction.

### 5.2 — Per-phase tool binding

**Tool sets are per phase, not universal.** Tool selection quality
degrades past roughly 10–15 tools per agent; per-phase binding keeps
every coach inside the tractable range.

| Phase | Universal | Computation tools | Total |
|---|---|---|---|
| Define | 8 | `calculate_expected_savings` | **9** |
| Measure | 8 | `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean` | **16** |
| Analyse | 8 | `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression` | **13** |
| Improve | 8 | `calculate_doe_main_effects` | **9** |
| Control | 8 | `xbar_r_chart_limits`, `imr_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk` | **13** |

**No phase exceeds 16 tools**, and **as of 2026-09-09 the maximum is 16
(Measure) — the ceiling exactly.** If a new tool would push a phase past
16, that is an amendment to `../AGENTIC_ARCHITECTURE_REFERENCE.md` (§56), not a routine addition.

> **⚠ REVISIT THE CEILING BEFORE A NINTH UNIVERSAL TOOL, NOT AFTER.**
> `load_evidence_series` took Measure from 15 to 16. **There is no margin left**,
> and the two universal tools still unbuilt — `check_gate_status` and
> `request_human_approval` — are already inside the eight and inside this count.
> A per-phase total that is legal only because nothing else has been added is a
> constraint with no margin, and **the margin is what usually gets discovered by
> exceeding it.**

**`imr_chart_limits` is the individuals / moving-range chart** and is
the right choice whenever the Belt has **one measurement per period**
rather than batches — the common case in service and transactional work.
Never coach a Belt into inventing subgroups to fit a batch chart;
subgroups that were not collected as subgroups produce meaningless
limits.

**Each of the 20 computation tools is a separate named tool.**
Parameterised grouping (one `calculate_sample_size(type, ...)` with a
mode argument) is BANNED — it moves the selection burden into the
argument space, and models handle distinct named tools more reliably
than mode arguments.

**All 20 are pure functions.** No LLM call, deterministic, unit-tested.

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
