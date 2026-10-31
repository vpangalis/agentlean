# Contract h — index set and structure (RULED 31 Oct 2026 by the founder)

Part of the single-loop refactoring rulebook (REFACTORING_PLAN_single_loop_parallel_2026-10-31.md, stage 0). Builds on the evidence-channel amendment (EVIDENCE_CHANNEL_AMENDMENT_draft.md: role, kind, description, content_digest, shape_match; finding vs loading; structured retrieval results) and on ADR D10 (Azure AI Search, optimised).
Founder rulings 31 Oct: all agents use the same shared indexes; agent-specific indexes are dedicated; naming agentlean_<index> (shared) and agentlean_<agent>_<index> (dedicated); existing indexes hold test data only and are rebuilt BEFORE the refactoring starts; general and customer knowledge are separate indexes.

## 1. Naming and versions
- Shared: `agentlean_<index>`; dedicated: `agentlean_<agent>_<index>` (Azure: lowercase, letters/digits/dashes/underscores, starts with letter or digit, no consecutive `_`/`-`).
- Physical index carries a version: `<name>_v1`; agents and tools use only the alias `<name>`. Rebuild = build `_v2`, switch alias, delete `_v1`.

## 2. The five indexes

| Alias | Kind | Holds |
|---|---|---|
| `agentlean_knowledge` | Shared, general (shipped with AgentLean, curated, licensed) | Methodology, KPI definitions, industry patterns, examples |
| `agentlean_customer_knowledge` | Shared, customer-owned | The customer's own documents (procedures, process descriptions) |
| `agentlean_case_memory` | Shared | Summaries of closed cases / phases from all agents |
| `agentlean_metrics` | Shared | Search copy of the metric registry ("is this the same metric?") |
| `agentlean_improve_case_files` | Dedicated to Agent Improve | Text from files uploaded to Improve cases (the evidence channel) |

Why general and customer knowledge are separate: physical isolation of customer data (no filter to forget), deletion per customer by dropping/emptying one index, the general index ships as a product to every installation, licensed vs customer-owned content kept apart, relevance statistics not skewed by mixing, each with its own fields. Cost: the look-up tool queries both when a question needs both and merges by semantic-ranker score.

## 3. Tree structure (both knowledge indexes; case files use the same tree fields)
document → section → chunk. Each record has `level`, `parent_id`, `path` (e.g. "Black Belt manual > Measure > MSA > Gage R&R"), `position`. A chunk hit lets the look-up tool fetch its section summary or neighbouring chunks (small-to-big) instead of returning an isolated fragment.

## 4. Fields — `agentlean_knowledge` and `agentlean_customer_knowledge`

| Group | Field | Type | Attributes |
|---|---|---|---|
| Identity | `id` | string | key |
| | `document_id`, `version`, `content_digest` | string | filter |
| Tree | `level` (document / section / chunk) | string | filter |
| | `parent_id`, `path`, `position` | string / string / int | filter (path searchable) |
| Text | `content` | string | searchable |
| | `chunk_summary`, `context_line` | string | searchable, retrievable |
| | `section_summary`, `document_summary` | string | retrievable |
| Vectors | `content_vector`, `summary_vector` | vector | searchable (hybrid) |
| Type of information | `info_type` (definition / procedure / example / formula / checklist / benchmark / pattern / case) | string | filter, facet |
| DMAIC position | `phase`, `element`, `tool` | string | filter |
| Industry and process | `industry`, `process_path`, `kpi_ids` | string / string / collection | filter |
| Provenance | `source`, `licence`, `owner`, `approved_by`, `language` | string | filter, retrievable |

Customer index additionally: `source_system`, `confidentiality`.
Only records with `approved_by` set are returned to the coach.

## 5. `agentlean_improve_case_files` (evidence channel, as ratified, plus tree fields)
`id` · `content` · `content_vector` · `case_id` · `phase` · `uploaded_at` · `role` · `kind` (evidence / artefact, derived from role) · `description` (summary) · `content_digest` · `shape_match` · `blob_path` · `level` · `parent_id` · `path`. All server-set. Supersession deletes the old chunks; citations anchor on `blob_path` + `content_digest`. Retrieval filters to `kind eq 'evidence'` by default inside the tool.

## 6. `agentlean_case_memory`
`id` · `agent` · `case_id` · `phase` · `title` · `summary` · `summary_vector` · `industry` · `process_path` · `site_id` · `metric_ids` · `baseline` · `result` · `closed_at` · `owner`.

## 7. `agentlean_metrics`
`metric_id` (key) · `name` · `definition` · `other_names` · `unit` · `direction` · `industry` · `process_path` · `status` · `definition_vector`.

## 8. What search returns (all look-up tools)
Structured records, not prose: `info_type` · `path` · `summary` · excerpt · `source` · `licence` · handle (`id` / `blob_path`). Finding is search; loading numbers from data files is a deterministic fetch by handle (evidence-channel amendment D), never similarity search.

## 9. Search behaviour (ADR D10)
Every look-up: hybrid (keyword + vector) with the semantic ranker; always scoped (index + filters for phase / element / info_type / industry / process / owner); context line indexed with each chunk (contextual retrieval).

## 10. Rebuild (before the refactoring starts)
1. Export today's index definitions as reference.
2. Delete the old test indexes (founder authorisation 31 Oct: test data only), including those of the Agent Resolve prototype.
3. Create the five `_v1` indexes with aliases and the fields above.
4. Ingest: the Black Belt manual and the tools spreadsheet (agent-improve/data) into `agentlean_knowledge` with tree, summaries, context lines, info types, phase/element/tool tags; fresh test cases into case files and case memory. One-time model cost for summaries allowed outside the €1/day test cap.
5. 20-question retrieval test as the search baseline, recorded.
6. Look-up tools point at the aliases only.

Out of scope for this run: curated industry content (APQC and others) — structure only; loading after licences and founder material.
