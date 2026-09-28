# ADR-0060 — Contextual retrieval and reranking, adopted only on eval evidence

Status: ACCEPTED (founder, 2026-09-28 — adoption stays conditional on the eval result) · Requirement: T85 · Depends on: T86 (eval set)

## Context
Anthropic's Contextual Retrieval work reports fewer failed retrievals when each chunk carries a
short explanation of where it sits in its document before it is embedded and keyword-indexed
(35% with contextual embeddings, 49% with contextual BM25 as well, 67% with reranking), and that
passing the top 20 chunks beat the top 10 or 5. Our indexes embed raw chunks; the coach receives
the top 10 after multi-query fusion; there is no reranker.

## Decision
1. Build a candidate knowledge index (`improve_knowledge_index_v4`) at ingest: for each chunk, one
   model call writes a short context from the whole source section; the context is prepended to
   `content` before embedding and indexing.
2. Add Azure AI Search's semantic ranker over the fused candidates (availability in the customer's
   tier and private networking to be confirmed).
3. Compare v3 and v4 on the T86 eval set (retrieval hit rate, then coaching quality) at top-10
   and top-20. Switch the environment variable to v4 only if v4 wins; v3 stays the rollback.
4. The evidence index follows only if the knowledge index shows a gain, because it adds a model
   call per uploaded chunk.

## Consequences
One-off ingest cost; no change to the tools' interfaces; the retired-name guard gets v3 only once
v4 is live.

## Rejected
Switching without measurement; reranking with a second model call per turn (latency against R13).
