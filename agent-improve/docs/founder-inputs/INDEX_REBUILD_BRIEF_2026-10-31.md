# Index rebuild brief (founder-approved 31 Oct 2026) — first step of the single-loop refactoring

Spec: CONTRACT_H_index_structure_2026-10-31.md (same folder, ruled 31 Oct). Contract h is the specification; do not redesign it. Write gaps as questions and continue with the rest.
Context: the old node design is frozen (baseline ff508e7). The indexes are rebuilt BEFORE the Agent Improve refactoring starts. Inputs: docs/SINGLE_LOOP_INVENTORY_2026-10-30.md (AI Search section: one service, nine indexes, two retired Improve knowledge indexes, empty case index, Resolve search tools probably on a wrong vector field name).

## Steps
1. Export: every index definition (schema, vector config, semantic config) plus its document count to agent-improve/docs/refactor/index-export-2026-10-31/.
2. Delete: all old test indexes, including the Agent Resolve prototype's (founder authorisation 31 Oct: test data only). Only after step 1 succeeded. List deleted names with document counts.
3. Create: the five `_v1` indexes with the fields of contract h §4–7; hybrid search + semantic ranker; the embedding model already in use (check its dimensions against the current deployment). Aliases point at `_v1` — verify alias support on our tier and API version in current Microsoft docs and cite the URL; if unavailable, one config module maps alias → physical name and all look-up code reads it.
4. Ingest: the Black Belt manual and the tools spreadsheet from agent-improve/data into `agentlean_knowledge` with the document → section → chunk tree, chunk / section / document summaries, a context line per chunk, `info_type` and phase / element / tool tags, provenance with `approved_by` = founder. Synthetic test cases only (tests/fixtures) into `agentlean_improve_case_files` and `agentlean_case_memory`. No customer material, ever. `agentlean_customer_knowledge` and `agentlean_metrics`: created, empty. Estimate the one-time summary cost first: run if under €5 (outside the €1/day test cap), otherwise stop at this step and report the estimate.
5. Baseline: 20 retrieval questions across the DMAIC phases and info types, each with its expected `path`; run hybrid + semantic ranker; record hit@3 and hit@5 in docs/refactor/retrieval-baseline-2026-10-31.md.
6. Repoint: every look-up in code uses the aliases only; grep proof that no old or physical index names remain; run T1. The frozen old design changes only by this name change.

## Rules
No force push, no `git reset --hard`, no `start.ps1`. Keys stay in .env. Effort High is enough; most of the time is waiting on Azure and model calls.

## Report
Deleted and created indexes with counts; ingestion cost; baseline table; grep proof; lines added/removed; open gaps as questions. Report goes to Desktop for refactor-step-review before the founder walks anything.

## After this step
Desktop drafts contracts a–g from the inventory; the independent reviewer approves them; then one kickoff prompt starts the autonomous parallel run (REFACTORING_PLAN_single_loop_parallel_2026-10-31.md).
