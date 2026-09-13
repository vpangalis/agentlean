---
paths:
  - "agent-improve/backend/knowledge/**"
  - "agent-improve/scripts/ingest_knowledge.py"
---
# §7 — RAG and indexes

> **Moved verbatim from `agent-improve/CLAUDE.md` on 2026-09-13** (brief step 6).
> Rule numbers are unchanged — `.claude/config/deprecated_patterns.yaml`
> cites them and §0.2 makes that binding. Canonical reasoning stays in
> `agent-improve/ARCHITECTURE.md`.

## 7. RAG AND INDEXES

### 7.1 — RAG via tool, never via prepended system message

The v1 pattern (`build_knowledge_context()` injected as a
SystemMessage) is DELETED. Retrieval is a tool call the model decides
to make.

This makes RAG accountable in the trace, lets the model control when
to retrieve, and removes the always-on retrieval cost.

**There is no unconditional retrieval pipeline.** If you find one,
it is a violation.

### 7.2 — Three retrieval tools, one index each

| Tool | Index | Filter | Ordering | Vector field |
|---|---|---|---|---|
| `rag_lookup_methodology` | `improve_knowledge_index` | `phase_relevance eq '{phase}' or phase_relevance eq 'general'` | — | `content_vector` |
| `rag_lookup_evidence` | `improve_evidence_index` | `case_id`; `kind` (default `evidence`); optional `phase` (default OFF) | **none — by ruling, not by schema** | `content_vector` |
| `rag_lookup_case_history` | `improve_case_index` | `status eq 'completed'` | `created_at desc` | `embedding` † |

† `improve_case_index`'s vector field **is still named `embedding`** — that
rename is ratified and not yet applied, and it is now the only one left
(§7.3). **Write code against the live schema, not the target schema.**

> **The evidence index's half of this footnote is DISCHARGED.** It read
> *"`improve_evidence_index` has no `phase` or `uploaded_at`"*. It has both,
> and has had since step 6.13 landed §23.2's seven fields (`1396627`,
> 2026-09-10). Live definition read from Azure on 2026-09-12: **12 fields**,
> `phase` filterable, `uploaded_at` filterable **and sortable**.

**Each tool is bound to exactly one index and knows that index's
vector field name locally.** There is no shared retriever. This is why
the `content_vector` / `embedding` asymmetry is safe: no shared code
can hide it, so nothing can fail silently on it.

**`belt_level` filtering is OFF by default** on case history —
over-narrowing risk, since a Green Belt often benefits from Black Belt
cases. Available as an optional parameter.

`source_file` and `page_number` are **returned as metadata for
citation transparency**, never used as filters.

**The methodology filter field is `phase_relevance`, and its cross-phase
value is `general` — never `phase`, never `all`.** Both were wrong in
earlier revisions; `phase` does not exist on the index (Azure rejects the
whole query) and no document carries `all` (259 carry `general`). One
fails loudly, the other silently returns a narrowed corpus.

**A metadata key becomes a filterable field only if it is named after one
AND the vectorstore declares it.** LangChain's `AzureSearch` promotes a
metadata key to a top-level field only when the key matches a name in
`self.fields` — and `self.fields` defaults to
`[id, content, content_vector, metadata]`, never the live schema. So
writing methodology requires both the correct key name *and*
`fields=KNOWLEDGE_INDEX_FIELDS` on the vectorstore. Either alone leaves
the value buried in the `metadata` JSON blob, unreachable by `$filter`,
with no error raised. This is how `phase_relevance` went unpopulated.
`ingest_knowledge.py` owns this contract; full detail in
`../AGENTIC_ARCHITECTURE_REFERENCE.md` §23.4.

**Retrieval failure is never an empty result.** All three retrieval
functions — `search_knowledge`, `search_cases`, `search_evidence` — return
`[]` only when the search ran and matched nothing; when they fail they
raise `KnowledgeSearchError`. **Never wrap a retrieval call in a bare
`except Exception` that returns `[]`** — that is what hid the `phase`
filter bug, by reporting a broken index as a silent corpus. Catch
`retriever.RETRIEVAL_EXCEPTIONS` and classify via `_fail()`.

Three rules that fall out of it, each of which has already bitten:
- **`RETRIEVAL_EXCEPTIONS` spans two services.** Azure AI Search *and* the
  Azure OpenAI query embedding, which runs inside the same `try`.
- **A 4xx is `permanent` / `do_not_retry`**, not transient — it is our
  malformed query, and retrying fails identically.
- **Materialise results inside the `try`** — `SearchClient.search()` is
  lazy and the HTTP call fires on iteration.

Full rationale: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §27.

**`rag_lookup_evidence` takes no `order_by` argument — and that is now a
DESIGN CHOICE, not a schema constraint.** The distinction is the whole of this
paragraph, because the rule reads the same either way and means something
different.

This prohibition was justified by *"a tool cannot sort on a field the index does
not have"*. **That justification expired on 2026-09-10** and the rule outlived
it by two days: `uploaded_at` is live, filterable and sortable. Ruled at
ARCHITECTURE.md v1.20 (D) — *"`uploaded_at` exists now, and the tool still takes
no `order_by` as a design choice rather than a schema constraint"* — which is
the owner of this fact; S-F15 B3 is discharged there.

**What keeps it out of the signature is §7.4.** Retrieval here is multi-query +
RRF, and a fused rank is what the tool returns; an `$orderby` applied to that
discards the fusion and returns recency, which is a different tool. Wanting
recency is a real requirement and the answer to it is a filter on `uploaded_at`,
not a sort of the fused set.

**A rule whose reason has expired is not the same rule.** It survived here on
its restated form after its basis was gone, which is exactly what a citation
would have prevented.

Never re-sort the returned `top_k` client-side and present it as recency
ordering: that reorders only what was already retrieved, which is a different
result — and it stays wrong after the reindex too.

### 7.3 — Index schemas — field names that bind on code

**The canonical full schemas live in `../AGENTIC_ARCHITECTURE_REFERENCE.md` §23**, with types,
vector dimensions, filter and ordering clauses, and the schema-change
procedure. This subsection carries only the facts a *rule* depends on.
It does not duplicate the schema, and it is not the place to record a
schema change — that lands in `../AGENTIC_ARCHITECTURE_REFERENCE.md` §23 first, in the same
commit as the Azure AI Search change (§23.5).

> **THIS SUBSECTION SAID THAT AND THEN TABLED ALL THREE SCHEMAS ANYWAY,
> AND THE COPY WENT STALE.** It carried `phase ← RATIFIED, pending reindex`
> and `uploaded_at ← RATIFIED, pending reindex` and asserted *"`phase` and
> `uploaded_at` are ratified additions, not live fields"*. **Both have been
> live since step 6.13 landed §23.2's seven fields** (`1396627`, 2026-09-10).
> The tables are removed rather than corrected: a schema transcribed into a
> second document is a schema that will disagree with the index again, and
> the rule this subsection states about itself is the one it broke.
>
> **Read the live definition, do not read this file for it.** Three indexes,
> introspected 2026-09-12 against the pinned venv:
>
> ```python
> from azure.search.documents.indexes import SearchIndexClient
> [f.name for f in client.get_index(name).fields]
> ```
>
> | Index | Live fields | Notes |
> |---|---|---|
> | `improve_knowledge_index` | 7 | as §23 specifies |
> | `improve_evidence_index` | **12** | §23.2's seven APPLIED; `uploaded_at` filterable **and sortable** |
> | `improve_case_index` | 19 | vector field still `embedding` — see below |

**The facts a rule depends on**, and nothing else:

**`improve_case_index`'s vector field is `embedding`, not `content_vector`.**
It is the only index where this is true, the difference is historical rather
than deliberate, and **`rag_lookup_case_history` must use the live name**. The
rename to `content_vector` is ratified and still pending — delete + recreate,
0 documents, no data loss. **This is the last unapplied schema change of the
three this subsection used to track.** The per-tool local knowledge of vector
field names (§7.2) is what makes the asymmetry safe in the meantime — that was
the reason not to rush it, never a reason to keep it.

**`phase` and `uploaded_at` are SERVER-SET.** `phase` from
`state["current_phase"]` at upload, `uploaded_at` from the server clock. A
Belt-entered value for either makes it unreliable as a filter or a sort key,
which is the whole reason they were promoted out of `metadata`.

**`phase`'s filter defaults OFF.** It exists because two similar documents
uploaded at different phases were otherwise indistinguishable at retrieval
time — but a Control-phase Belt comparing against the Measure baseline is the
normal case, and filtering by default would break it.

**Breaking schema change — LANDED Aug 2026.**
`phase_summary_analyse_phase` was renamed to `phase_summary_analyse` in
Azure AI Search by delete + recreate (the index held 0 documents, so
nothing was lost and no reindex was needed). The pattern
`phase_summary_{phase.lower()}` is now correct for all five phases. A
mapping constant was considered and rejected: fix the name at the
source so no permanent workaround exists.

**The internal phase key is `analyse`, never `analyse_phase`.** The
key was renamed across the codebase in the same change, so
`f"phase_summary_{phase}"` is correct for all five phases with no
mapping constant anywhere. This binds on: `PHASE_ORDER` and every
`phase_order` list, v1 `phase_inputs` keys, `EXTRACTION_MAP`,
`ORCHESTRATOR_CONTEXT_MAP`, `GATE_CHECKS`, `PhaseSummaryRecord`,
`CaseDocument.phases`, the graph node names, and the module path
`backend.phases.analyse`. `AnalysePhaseInput` keeps its name —
`{Phase}PhaseInput` is the convention all five phases follow. Full
scope: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §23.3.

**Never write to Agent Resolve indexes.** Read only, via tools.

### 7.4 — Multi-query + RRF is mandatory, not optional

All three retrieval tools generate 3–5 query variants and fuse the
results with Reciprocal Rank Fusion, k=60.

This is not a nice-to-have. Agent Resolve production experience showed
Azure AI Search ranking unreliable for this corpus — with a single
query it was not reliably returning the right matches. RRF
operationalises cross-variant consistency, which single-query native
ranking cannot do because it does not know the variants exist.

RRF is about fifteen lines and needs no LangChain class. `MultiQueryRetriever`
and `EnsembleRetriever` are BANNED — both moved to `langchain-classic`
in the 1.0 namespace split, and the former is deprecated even there.

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

**Gate validation never retrieves.** The rubric already encodes the
methodology standards; retrieval there is redundant and adds latency
at exactly the moment the Belt is waiting.

Multi-query and multi-hop compose: multi-query broadens within a hop,
multi-hop deepens across hops.

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
