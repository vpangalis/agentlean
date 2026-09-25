---
paths:
  - "agent-improve/backend/knowledge/**"
  - "agent-improve/scripts/ingest_knowledge.py"
---
# §7 — RAG and indexes

> Never renumber — `deprecated_patterns.yaml` cites these (§0.2). History/rationale: `docs/_archive/rules_rationale_2026-09-25.md`.

## 7. RAG AND INDEXES

### 7.1 — RAG via tool, never via prepended system message

Retrieval is a tool call the model decides to make. The v1
`build_knowledge_context()` SystemMessage injection is DELETED.

**There is no unconditional retrieval pipeline.** If you find one,
it is a violation.

### 7.2 — Three retrieval tools, one index each

| Tool | Index | Filter | Ordering | Vector field |
|---|---|---|---|---|
| `rag_lookup_methodology` | `improve_knowledge_index` | `phase_relevance eq '{phase}' or phase_relevance eq 'general'` | — | `content_vector` |
| `rag_lookup_evidence` | `improve_evidence_index` | `case_id`; `kind` (default `evidence`); optional `phase` (default OFF) | **none — by ruling, not by schema** | `content_vector` |
| `rag_lookup_case_history` | `improve_case_index` | `status eq 'completed'` | `created_at desc` | `embedding` † |

† `improve_case_index`'s vector field **is still named `embedding`** — the
rename is ratified and not yet applied (§7.3). **Write code against the live
schema, not the target schema.**

**Each tool is bound to exactly one index and knows that index's
vector field name locally.** There is no shared retriever.

**`belt_level` filtering is OFF by default** on case history; available as
an optional parameter.

`source_file` and `page_number` are **returned as metadata for
citation transparency**, never used as filters.

**The methodology filter field is `phase_relevance`, and its cross-phase
value is `general` — never `phase`, never `all`.**

**A metadata key becomes a filterable field only if it is named after one
AND the vectorstore declares it** — LangChain's `AzureSearch` needs
`fields=KNOWLEDGE_INDEX_FIELDS`; otherwise the value is buried in the
`metadata` JSON blob, unreachable by `$filter`, with no error raised.
`ingest_knowledge.py` owns this contract
(`../AGENTIC_ARCHITECTURE_REFERENCE.md` §23.4).

**Retrieval failure is never an empty result.** `search_knowledge`,
`search_cases` and `search_evidence` return `[]` only when the search ran and
matched nothing; on failure they raise `KnowledgeSearchError`. **Never wrap a
retrieval call in a bare `except Exception` that returns `[]`.** Catch
`retriever.RETRIEVAL_EXCEPTIONS` and classify via `_fail()`:
- **`RETRIEVAL_EXCEPTIONS` spans two services** — Azure AI Search *and* the
  Azure OpenAI query embedding, which runs inside the same `try`.
- **A 4xx is `permanent` / `do_not_retry`**, not transient.
- **Materialise results inside the `try`** — `SearchClient.search()` is
  lazy and the HTTP call fires on iteration.

Rationale: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §27.

**`rag_lookup_evidence` takes no `order_by` argument — a DESIGN CHOICE, not a
schema constraint** (ARCHITECTURE.md v1.20 (D) owns this). An `$orderby`
would discard the RRF fusion (§7.4); recency is served by a filter on
`uploaded_at`, not a sort of the fused set. Never re-sort the returned
`top_k` client-side and present it as recency ordering.

### 7.3 — Index schemas — field names that bind on code

**The canonical schemas live in `../AGENTIC_ARCHITECTURE_REFERENCE.md` §23**;
a schema change lands there first, in the same commit as the Azure AI Search
change (§23.5). **Do not tabulate schemas here — read the live definition**
(`SearchIndexClient.get_index(name).fields`).

**`improve_case_index`'s vector field is `embedding`, not `content_vector`.**
It is the only index where this is true, and **`rag_lookup_case_history`
must use the live name** until the ratified rename lands.

**`phase` and `uploaded_at` are SERVER-SET** — `phase` from
`state["current_phase"]` at upload, `uploaded_at` from the server clock.
Never Belt-entered.

**`phase`'s filter defaults OFF** — comparing across phases is the normal
case.

**The internal phase key is `analyse`, never `analyse_phase`**, so
`f"phase_summary_{phase}"` is correct for all five phases with no mapping
constant anywhere. `AnalysePhaseInput` keeps its name. Scope:
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §23.3.

**Never write to Agent Resolve indexes.** Read only, via tools.

### 7.4 — Multi-query + RRF is mandatory, not optional

All three retrieval tools generate 3–5 query variants and fuse the
results with Reciprocal Rank Fusion, k=60.

RRF needs no LangChain class. `MultiQueryRetriever` and `EnsembleRetriever`
are BANNED.

Variant generation uses structured output (§4.6), never manual JSON
parsing.

### 7.5 — Multi-hop policy per phase

The **phase planner** decides retrieval strategy at plan time, not the
executor at retrieval time. `coaching_plan` carries a
`retrieval_strategy` field.

| Phase | Default | Multi-hop when |
|---|---|---|
| Define | Single-hop | Never — scoping questions are direct |
| Measure | Single-hop | Complex measurement system validation (GR&R) |
| **Analyse** | **Multi-hop, planned (3 hops)** | Almost always — root cause validation is layered |
| Improve | Single-hop | Belt is comparing competing approaches |
| Control | Single-hop | Never — documentation questions are direct |
| **Gate validation** | **No retrieval** | **Never** |

**Gate validation never retrieves.**

Multi-query broadens within a hop; multi-hop deepens across hops.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §23, §24, §25, §26, §28.*


## Never

*§14's bans that belong to this file — 11 of 95, each landing in exactly one rule file. Verbatim, with their citations.*

- Never reference the retired **tool** names `search_improve_knowledge`,
  `search_improve_cases` or `search_improve_evidence` in v2 code — the tools
  are `rag_lookup_*` (§5.1). **The retriever functions `search_knowledge`,
  `search_cases` and `search_evidence` are NOT retired** and must keep their
  names and failure semantics (§7.2)
- Never write code against the ratified-but-unapplied index fields
  (`phase`, `uploaded_at`, `content_vector` on `improve_case_index`) — use
  the live schema until the reindex lands (§7.3)
- Never build an unconditional retrieval pipeline
- Never catch bare `Exception` around a retrieval call and return `[]` —
  retrieval failure must be distinguishable from no matches (§7.1.1)
- Never let a coach-facing failure message read as an absence of content
  ("no cases found" when the search never ran) (§7.1.1)
- Never filter methodology on `phase`; the field is `phase_relevance` and
  its cross-phase value is `general`, not `all` (§7.2)
- Never write to an index through LangChain without declaring the real
  schema via `fields=` — unmatched metadata keys are silently demoted to
  the JSON blob and become unfilterable (§7.1.2)
- Never call `add_texts` without explicit `ids=` — LangChain assigns a
  random UUID key, so re-ingestion duplicates the corpus (§7.1.2)
- Never write to Agent Resolve indexes — read only, via tools
- Never add an MCP server, client, or dependency
- Never build a fallback path that fetches data the Belt did not upload
