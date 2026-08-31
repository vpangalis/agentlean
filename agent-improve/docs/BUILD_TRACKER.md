<!--
Document: agent-improve/docs/BUILD_TRACKER.md
Created: 2026-08-27
Purpose: The one-screen "where are we in the refactor" checklist. A human-readable
         companion to REFACTORING_PROCEDURE.md's Appendix D (the machine-readable
         step index the session-start hook parses). Update the status column in
         the same commit as each step. Authoritative build target for every step:
         agent-improve/ARCHITECTURE.md (founder ruling 2026-08-27).
Legend:  ✅ done · ▶ next · ☐ to do · ⛔ blocked · ⏸ gated/external
-->

# Agent Improve — Refactor Build Tracker
# updated 2026-08-31 · build target: `agent-improve/ARCHITECTURE.md`

**Progress: 3 of 34 build steps done** (2.3, 2.4 + 9.0 out-of-band). **Next: step 2.5.**
Spine runs 2.3 → 11.2, one step = one commit. The spec is complete; this is the code.

**Blocked / not-yet-schedulable:** 8.4 (Redis not provisioned), 8.5 (`request_drain`
unconfirmed), 9.1 (external reindex). Everything else is open once its precondition step lands.

---

## Stage 2 — Foundation hygiene
| Step | What | Builds (agent-improve/ARCHITECTURE.md) | Status |
|---|---|---|---|
| 2.3 | Dependency upgrade (LangGraph 1.2.11 etc.) | §53, §16 | ✅ done (`95926d6`) |
| 2.4 | `set_entry_point` → `add_edge(START, …)` | §12 | ✅ done |
| 2.5 | Async conversion (all nodes `async def`) | §14, §49 | ▶ **next** |
| 2.6 | `response.content` → `content_blocks` (20 sites) | §21 | ☐ |
| 2.7 | LLM factory: class → functions, 6 → 11 roles | §21, §54 | ☐ |

## Stage 3 — State and persistence
| Step | What | Builds | Status |
|---|---|---|---|
| 3.1 | `SupervisorState` + `PhaseState` | §5, §6, §7 | ☐ |
| 3.2 | `AzureBlobStore` | §9, §10 | ☐ |
| 3.3 | Boundary mappers **(closes G-27)** | §9 | ☐ |
| 3.4 | `{Phase}Output` schemas + validators + UI **(gate assembly, G-28)** | §7, §40, §41, §63 | ☐ |

## Stage 4 — The graph
| Step | What | Builds | Status |
|---|---|---|---|
| 4.1 | The Define phase subgraph | §12, §13, §14, §39.1 | ☐ |
| 4.2 | `thread_id` through `graph.ainvoke` + disconnect policy | §16, §47, §49 | ☐ *(first live checkpoints — settles WATCH 1)* |
| 4.3 | The supervisor graph | §12, §15 | ☐ |
| 4.4 | The remaining four phase subgraphs | §12, §13, §39.2–39.5 | ☐ |

## Stage 5 — Retrieval and tools
| Step | What | Builds | Status |
|---|---|---|---|
| 5.1 | Retrieval failure semantics | §27 | ☐ *(partly done — `knowledge/retriever.py`)* |
| 5.2 | Three `rag_lookup_*` tools + multi-query + RRF | §24, §25 | ☐ |
| 5.3 | **The 20 computation tools** | §69 (S-F37–S-F56) | ☐ |
| 5.4 | Per-phase tool binding | §30 | ☐ |

## Stage 6 — The coaching agent
| Step | What | Builds | Status |
|---|---|---|---|
| 6.1 | Planner / Executor split | §17 | ☐ |
| 6.2 | `create_agent` executor + `CoachingResponse` | §18, §20 | ☐ **← clears WATCH 7** (the v2 Define writer starts here) |
| 6.3 | Middleware positions 1–3 | §19 | ☐ |
| 6.4 | Retry middleware 4–5 + factory hardcoded retry | §19 | ☐ |
| 6.5 | Middleware positions 6–8 | §19 | ☐ |
| 6.6 | Prompts | §22 | ☐ |

## Stage 7 — Validation and gates
| Step | What | Builds | Status |
|---|---|---|---|
| 7.1 | `DMAICGateValidator` + Layer 2b **(gate assembly ×4, G-28)** | §34, §40.1 | ☐ |
| 7.2 | Layers 2c and 2d + `validation_stack` node | §34, the five rubrics | ☐ |
| 7.3 | The nine-step HITL gate | §33 | ☐ |
| 7.4 | Two tiers + the `warning` verdict | §35 | ☐ |
| 7.5 | Escalation | §38 | ☐ |

## Stage 8 — Reliability
| Step | What | Builds | Status |
|---|---|---|---|
| 8.1 | Structured errors | §48 | ☐ |
| 8.2 | Per-node timeouts + compensating actions | §44, §45 | ☐ |
| 8.3 | Circuit breakers + fallback chain (levels 1,2,4) | §46 | ☐ |
| 8.4 | Level 3 response cache | §46 | ⛔ Redis not provisioned |
| 8.5 | Graceful shutdown | §45 | ⏸ `request_drain` unconfirmed |

## Stage 9 — Azure schema changes
| Step | What | Builds | Status |
|---|---|---|---|
| 9.0 | Knowledge-index rebuild | §23 | ✅ done out-of-band (`871637f`) |
| 9.1 | The batched reindex (evidence + case indexes) | §23 | ⏸ external |

## Stage 10 — API and UI
| Step | What | Builds | Status |
|---|---|---|---|
| 10.1 | `/ask/stream` SSE | §49 | ☐ |
| 10.2 | Live gate document + conflict panel + tier bars **(closes WATCH 9 UI half)** | §50 | ☐ |

## Stage 11 — Cleanup and governance
| Step | What | Builds | Status |
|---|---|---|---|
| 11.1 | Delete v1 (every retired name → zero grep hits) | §54 | ☐ *(the v1 Define vocabulary dies here — 10.2 must land first)* |
| 11.2 | Governance close-out | §55, §56 | ☐ |

---

## Owed rulings / open questions blocking specific steps
- ~~**WATCH 7 route**~~ — **RULED 2026-08-28: Route A** (`DECISIONS.md` Part X).
  The v1 Define capture path (`EXTRACTION_DEFINE`, `orchestrate.py`, **78** UI sites
  — measured, the "~30" here was an estimate) is **carried unchanged, never
  migrated**, and deleted at **11.1**. The Define gate is **accepted as inert** until
  the executor's capture path lands at **6.2** — not 4.1, whose own prompt still
  delegates to `orchestrate_define`. **Nothing is owed and nothing blocks Stage 4.**
  **The v1 Define field names in the tree are the ruled-correct state, not drift —
  do not "fix" them.**
- **WATCH 2** — resolve the two-venv split so the drift hook reads `agent-improve/.venv`
  (1.2.11, authoritative), not the root (1.1.10, stale). Do before 2.4.
- **Procedure framing** — `REFACTORING_PROCEDURE.md`'s "About this document" still names
  the ROOT reference as the design target; per the 2026-08-27 ruling it should cite
  `agent-improve/ARCHITECTURE.md`. Annotate.

## Deferred (not blockers, tracked)
- Root-reference back-port (`AGENTIC_ARCHITECTURE_REFERENCE.md`) — after Improve settles.
- Two Azure index schema changes — batched at 9.1.
- Eval dataset (§52) — load-bearing once 6.2 lands.
