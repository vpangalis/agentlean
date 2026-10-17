# ADR-0098: A fourth index: industry practice

Status: ACCEPTED (founder, 2026-10-17; drafted by Desktop, 2026-10-17). Scheduled after Define — no build now.
Requirements: R22 (Practice intelligence for Analyse and Improve)
Extends: ADR-0030 "Three search indexes with separate purposes"
Vocabulary: [practice_index_vocabulary.md](practice_index_vocabulary.md)

## Context

The knowledge index is methodology only (the BB manual) and is deliberately one voice. Analyse and Improve need industry practice, which differs by industry and process and must never be mixed with method text.

## Decision

1. A separate index, `improve_practice_index_v1`, searched by its own lookup. The methodology index is renamed only at its next rebuild (v4), not now.
2. Fields per chunk: `content`, `context_summary`, `vector`; `scope` (cross_industry · industry_specific); `industries` (list, `*` = all); `process_area` (fixed list); `process_step` (free text); `content_type` (fixed list); `dmaic_phase` (list); `jurisdiction`; `source`, `version`, `url`, `section`; `licence` (open · prototype_only · licensed · client_private); `tenant` (empty = shared, else the customer).
3. Filters at query time: `tenant` empty or the current customer; `industries` contains the customer's industry or `*`; `process_area` from the case. Industry-specific content ranks above cross-industry.
4. The customer's industry is one configuration value per deployment (C5); the case's process area comes from the department or area chosen at case creation (pick-list with the W20 rework). The Belt is asked nothing new.
5. Chunking along process steps, not fixed lengths. Context summaries per chunk follow ADR-0060: adopted if the eval shows a gain. Process cards (the founder's own process summaries) come later, linked by `process_area`.

## Rejected

Adding practice to the methodology index (mixes voices); one global shared index without tenant (leaks customer content); embedding without fields (cannot separate banking risk from rail risk).
