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
# updated 2026-09-03 · build target: `agent-improve/ARCHITECTURE.md`

**Progress: 21 of 35 build steps done** (2.3, 2.4, 2.5, 2.6, 2.7, 3.1, 3.2, 3.3, 3.4, 3.5, 4.1, 4.2, 4.3, 4.4, 5.1, 5.2, 5.3, 5.4, 6.1, 6.2 + 9.0 out-of-band). **Next: step 6.3.** **WATCH 7 is CLOSED** — the v2 field writer exists.
Spine runs 2.3 → 11.2, one step = one commit. The spec is complete; this is the code.

**Blocked / not-yet-schedulable:** 8.4 (Redis not provisioned), 8.5 (`request_drain`
unconfirmed), 9.1 (external reindex). Everything else is open once its precondition step lands.

---

## Stage 2 — Foundation hygiene
| Step | What | Builds (agent-improve/ARCHITECTURE.md) | Status |
|---|---|---|---|
| 2.3 | Dependency upgrade (LangGraph 1.2.11 etc.) | §53, §16 | ✅ done (`95926d6`) |
| 2.4 | `set_entry_point` → `add_edge(START, …)` | §12 | ✅ done |
| 2.5 | Async conversion (all nodes `async def`) | §14, §49 | ✅ done |
| 2.6 | `response.content` → `content_blocks` (20 sites) | §21 | ✅ done |
| 2.7 | LLM factory: class → functions, 6 → 11 roles | §21, §54 | ✅ done |

## Stage 3 — State and persistence
| Step | What | Builds | Status |
|---|---|---|---|
| 3.1 | `SupervisorState` + `PhaseState` | §5, §6, §7 | ✅ done |
| 3.2 | `AzureBlobStore` | §9, §10 | ✅ done |
| 3.3 | Boundary mappers **(G-27 CLOSED)** | §9 | ✅ done |
| 3.4 | `{Phase}Output` schemas + validators + UI **(gate assembly, G-28)** | §7, §40, §41, §63 | ✅ done |
| 3.5 | `storage/blob.py` — class → functions, sync → aio **(S-C08)** | §54, §10, §49 | ✅ done |

## Stage 4 — The graph
| Step | What | Builds | Status |
|---|---|---|---|
| 4.1 | The Define phase subgraph | §12, §13, §14, §39.1 | ✅ done |
| 4.2 | `thread_id` through `graph.ainvoke` + disconnect policy | §16, §47, §49 | ✅ done **+ azure-query VERIFIED** *(first live checkpoints ever. §47: 3 in, 2 deferred — WATCH 13, 14. Fixed `checkpoint_ns` in the blob layout — Z3 — and the ABANDON policy, which did not work as first shipped and was caught by the live check — Z8. Verified on `IMPR-2026-0CB`; E9D is complete — WATCH 22)* |
| 4.3 | The supervisor graph | §12, §15, §38 | ✅ done *(five phase nodes + `escalate`, seven static edges, **no Level-1 conditional edge** — the escalation edge is inside the phase via `Command.PARENT`, DECISIONS Part AA. Target topology, **not yet the runtime** — WATCH 23)* |
| 4.4 | The remaining four phase subgraphs | §12, §13, §39.2–39.5 | ✅ done *(**WATCH 17 CLOSED** — all five from one parameterised builder, `subgraph_common` + `nodes_common`. Caught the cross-phase brief going empty — DECISIONS Part AB3)* |

## Stage 5 — Retrieval and tools
| Step | What | Builds | Status |
|---|---|---|---|
| 5.1 | Retrieval failure semantics | §27 | ✅ done *(the classifier was already right; the gap was `build_knowledge_context` returning `None` for both a break and a no-match — the path all five orchestrators take every turn)* |
| 5.2 | Three `rag_lookup_*` tools + multi-query + RRF | §24, §25 | ✅ done **live-run verified** *(**G-14 CLOSED**. Found that `search_knowledge` projected four index fields that do not exist, so §50 citations were unbuildable — DECISIONS Part AC3)* |
| 5.3 | **The 20 computation tools** | §69 (S-F37–S-F56) | ✅ done *(20 named tools, 20 distinct `args_schema`s, 67 known-answer tests — 8 mutations of the code all caught. Scalar inputs are `str` + `_num()`, not `float` — DECISIONS Part AD1)* |
| 5.4 | Per-phase tool binding | §30 | ✅ done *(**Stage 5 complete.** `COMPUTATION_TOOLS_BY_PHASE` is the partition and `COMPUTATION_TOOLS` now derives from it — one source, no drift point. Totals 8/15/12/8/12, ceiling 16, seven new tests all mutation-checked — DECISIONS Part AE)* |

## Stage 6 — The coaching agent
| Step | What | Builds | Status |
|---|---|---|---|
| 6.1 | Planner / Executor split | §17 | ✅ done **trace-check verified** *(the real planner: `CoachingPlan` via `with_structured_output`, `planner` role @0.1, executor-bound path only. Needed a governance commit first — `9fce8fc` scoped pattern-2. **G-01 stays open**; DP1 was not invented. Found `validation_stack` reading the routing verb off `next_action` — DECISIONS Part AF)* |
| 6.2 | `create_agent` executor + `CoachingResponse` | §18, §20 | ✅ done **live-run verified** *(**WATCH 7 CLOSED** — `fields_captured` → `artifacts` → `validate_define` went 13/13 missing → 0, `passed=True`. Built `propose_template`/`propose_diagram` owed from 5.2 (+`core/diagrams.py`); two universal tools still owed to 7.1/7.5 — **WATCH 25**. Live-run found §3.7's coach cap could never fire — DECISIONS Part AG)* |
| 6.3 | Middleware positions 1–3 | §19 | ▶ **next** |
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

## Drift defences on the spine (2026-08-31)

A `refactor(arch-v2)` commit is blocked by `.githooks/commit-msg` unless all five
hold. Activate per clone with `git config core.hooksPath .githooks`.

| # | Rule |
|---|---|
| 1 | Subject is exactly `refactor(arch-v2): commit X.Y — <what changed>` |
| 2 | **This file** is staged in the same commit |
| 3 | **mypy** over the changed Python, against the pinned `.venv` (LangGraph 1.2.11) — new errors block; pre-existing ones are baselined in `.claude/config/mypy-baseline.txt` |
| 4 | **pytest** green |
| 5 | **`CONTINUITY.md`** is staged AND its CURRENT BUILD STATUS block is current |

Fail-closed; every refusal prints `git commit --no-verify`. The baseline is DEBT
— it should only ever shrink. Never widen it to silence a new error.

**Rule 5 is normally satisfied for you.** `.githooks/pre-commit` regenerates
CONTINUITY.md's status block from this file, `CLAUDE.md`, `ARCHITECTURE.md` and
the git spine, then stages it — so the orientation document cannot lag the
checklist. That writer is fail-SOFT (a hook that writes must never wedge a
commit); rule 5 behind it is fail-CLOSED, and catches the cases where it did
not run: `core.hooksPath` unset in a fresh clone, a `--no-verify` retry leaving
a stale block staged, or a hand-edited block.

## Deferred (not blockers, tracked)
- Root-reference back-port (`AGENTIC_ARCHITECTURE_REFERENCE.md`) — after Improve settles.
- Two Azure index schema changes — batched at 9.1.
- Eval dataset (§52) — load-bearing once 6.2 lands.
