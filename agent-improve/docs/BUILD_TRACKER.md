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

<!--
⚠ THE ▶ CURSOR IS LOAD-BEARING AND MUST APPEAR EXACTLY ONCE.
`.claude/hooks/continuity_status.py` takes the FIRST row whose status cell
contains ▶ as "next", and regenerates CONTINUITY.md's status block from it.
It matches the character anywhere in the cell — including inside a
parenthetical. On 2026-09-08 a note reading "was marked ▶ next until the
audit …" left on step 7.1 made the block report "next 7.1" while Appendix D
and the session-start hook both said 6.9, which would have skipped three
steps. Say "the cursor" in prose; keep the character for the cursor itself.
-->

# Agent Improve — Refactor Build Tracker
# updated 2026-09-08 · build target: `agent-improve/ARCHITECTURE.md`

**Progress: 27 of 51 build steps done** (2.3–2.7, 3.1–3.5, 4.1–4.4, 5.1–5.4, 6.1–6.8 + 9.0 out-of-band). **Next: step 6.11 — 6.10 is BLOCKED. STAGE 6 IS NOT COMPLETE — the 2026-09-07 audit reopened it.**

> **This header line is hand-maintained and the table is not — keep them in step.** On 2026-09-08 it still read *"26 of 49 … Next: step 6.8"*, dated 2026-09-03, while the table below already showed 6.8 done and the cursor on 6.9. The machine path (Appendix D → session-start hook, and the ▶ cursor → `continuity_status.py`) was correct throughout; only the line a human reads was wrong. **A stale human line is the same defect class as a stale count** — see the 35-vs-49 note below.
Spine runs 2.3 → 11.2, one step = one commit. The spec is complete; this is the code.

> **The total moved from 35 to 49 on 2026-09-07, and both halves of that are worth stating.** *35 was never right* — it was a hand-count that had drifted five rows from Appendix D, which is the machine-readable table the session-start hook actually parses. **Appendix D is authoritative; this line is derived from it.** The other eight rows are new: the pre-Stage-7 coverage audit found eleven ratified ARCHITECTURE sections with no step at all, and eight of them needed one. See `DECISIONS.md` Part AM.
>
> **"Stage 6 complete" was wrong when 6.6 claimed it.** Three Stage-6 holes were open the whole time — `phase_context` unread (6.8), the five SKILL.md files not audited against §32's seven mandatory items (6.9), and §26's multi-hop node unbuilt (6.10). **The 6.9 description was itself wrong until 2026-09-08** — it said four files were missing; all five exist and load. See the row.

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
| 6.3 | Middleware positions 1–3 | §19 | ✅ done **trace-check verified** *(`before_agent` fired ONCE on a many-call turn — B1 proved. `missing_gate_fields` consolidated so the prompt and all five `validate.py` share ONE computation. **G-33 answered**: `load_skill` is middleware-registered, outside §30's totals. Review caught string concatenation where §21 requires content blocks — DECISIONS Part AH)* |
| 6.4 | Retry middleware 4–5 + factory hardcoded retry | §19 | ✅ done **grep-absence verified** *(`max_retries=0` PINNED on the constructor — the middleware is the only retry layer; two layers multiply 3×3=9, not add. **Recursion question answered by experiment: retries cost NO graph steps**, so 6.4 does not worsen WATCH 26 — DECISIONS Part AI)* |
| 6.5 | Middleware positions 6–8 | §19 | ✅ done *(**the stack is complete at eight.** Found §19 wrong three ways: `after_agent` executes in REVERSE, `after_agent` state does not propagate between hooks, and positions 4–5 are no longer unnested — position 1's wrap encloses them. G-15 answered: `HITLInterrupt` never defined. Position 6 ships INERT until 6.6 — WATCH 31. DECISIONS Part AJ)* |
| 6.6 | Prompts | §22 | ✅ done *(**WATCH 31 CLOSED** — proven live both ways: a real contradiction interrupts, an ordinary refinement does not. Done-when scoped to live v2 code; the two v1 families die with their consumers at 11.1 per Route A. **WATCH 26 did NOT close and moved off this step** — the cause is §26's unbuilt `RemainingSteps`, not the prompt. DECISIONS Part AK)* |
| 6.7 | **WATCH 26** — the hop cap becomes `RemainingSteps` + a hop count | §16, §26, S-F09 B1 | ✅ done *(**the defect was CLAUDE.md §3.7**, which carried `recursion_limit = 2*max_hops+1 = 11` — rejected by §16 — so the build followed the constitution into the wrong mechanism. Governance first and alone (2.2.32). **Both counters measured, not assumed**: `remaining_steps` DOES cross the subgraph boundary, but moves by 1 per executor turn however many hops it made, so it cannot cap hops — both guards built. `recursion_limit=11` was also short by one, which is why the symptom see-sawed. **Live re-run still owed — blocked on Azure 429s (AI2).** DECISIONS Part AL)* |
| 6.8 | **`phase_context` is read (WATCH 19)** | §6, §9, §19.1 | ✅ done **live-run verified** *(**WATCH 19 CLOSED.** Both breaks fixed: `write_case_record` at `POST /cases` + a lazy backfill on `/ask` and `/gate`, and both of §9's named readers wired — the planner prompt and `BeforeModelStateInjection`. Proved live: a real case created through the route landed 5 framing fields in the Store, and a Measure turn's injected block carried the case facts, the approved Define values and the 7 missing gate fields. The fallback is KEPT and made loud — WARNING + an in-block marker. DECISIONS Part AN)* *(was: declared, written by all five input mappers, **read by nothing**. §6 names its consumers as "planner; state injection" and neither touches it. **Invalidates every live measurement since 6.3** — the coach has been running on mapper-fallback prose. Two halves: the Store `case` writer W19 has owed since before 6.3, and the injection reader 6.3 never wired)* |
| 6.9 | SKILL.md conformance to §32's seven | §32, §43, §37 | ✅ done **live-run verified** *(**the step was the opposite file.** All five existed; the four "drafts" carried 7/7 of §32's items and **Define — recorded as the finished one — carried 4.5/7**. Written into Define: the A→F session flow with its `n of 12` count, §43.7 metric literacy, and Uploads + capture as real sections. 21.8K → 32.0K chars. Metric literacy landed in §39.1.7 too — v1.17 embeds coaching script, not flow or capture — and containment re-verified byte-exact. Version labels aligned and their meaning declared: Define 1.2, the four 1.1, "0.2-draft" false since v1.17. DECISIONS Part AO)* |
| 6.10 | `analyse_executor_node` — §26's multi-hop | §26, S-F09 | ⛔ **BLOCKED on G-05 and G-35** *(both need the Standing Reasoning Protocol, not a build session. Marked blocked 2026-09-08 so the queue does not stall on it — the upload path now sits behind it, and a cursor parked on an unresolvable precondition blocks everything after it. the half 6.7 did not build. `hop_results` / `synthesis_output` are declared and read by nothing, and S-F09 is their named writer. Blocked on G-05 and G-35)* |
| 6.11 | **The upload path (G-36)** | §29.1, §6, §10, §23.2, S-F35 | ☐ ▶ **next** *(**the twelfth unstepped section, and the largest.** §29.1 calls the evidence index the ONLY channel for external data; for the formats a Belt actually uploads it does nothing — csv/xlsx bucket as `other`, pdf/docx have no extractor while `is_supported()` says True, and `_index_upload` returns early on empty text. **`PhaseState.uploads` has no writer**, so every gate document already asserts §6's "this phase used no evidence". Deterministic parse first; evidence vs artefact split; unparseable is refused, never dropped. **Must land before Stage 7 completes.** DECISIONS Part AP)* |
| 6.12 | **Ask-binding: an upload answers a request** | §29.1, §32, §43, §50 | ☐ *(an upload binds to the coach's REQUEST, not its filename. The ask carries the expected shape from the SKILL.md worked examples; the file is validated against it and a mismatch is a coaching question, not an error. The ask is the identity, files are its versions — no naming convention, no inference. **This is what makes feeding an upload to a computation tool safe** rather than transcribing numbers out of chunks)* |
## Stage 7 — Validation and gates
| Step | What | Builds | Status |
|---|---|---|---|
| 7.0 | The evaluation suite | §52 | ☐ *(no `evals/` directory exists. Numbered before 7.1 on §52's own rule — the suite is load-bearing once the coach, tools and grader are wired, and **Stage 7 is the first stage that changes coaching behaviour**, so a suite built after it has no pre-change baseline. Baseline must be taken after 6.8)* |
| 7.1 | `DMAICGateValidator` + Layer 2b **(gate assembly ×4, G-28)** | §34, §40.1 | ☐ *(was the cursor until the 2026-09-07 audit put four steps in front of it)* |
| 7.2 | Layers 2c and 2d + `validation_stack` node | §34, the five rubrics | ☐ |
| 7.3 | The nine-step HITL gate | §33 | ☐ |
| 7.4 | Two tiers + the `warning` verdict | §35 | ☐ |
| 7.5 | Escalation | §38 | ☐ |
| 7.6 | The re-approval cascade **+ evidence supersession** | §37, §9.5 | ☐ *(**superseding evidence routes into this cascade, not a second mechanism** — founder ruling 2026-09-08; the trigger differs, the cascade is the same. Needs 6.11's parse and 6.12's ask-binding to detect it at all. §37's other half — the middleware landed at 6.5, the cascade it exists to trigger was never scheduled. §3.6's `error_handler=` rule names gate reopening as one of its two correctness-critical consumers)* |

## Stage 8 — Reliability
| Step | What | Builds | Status |
|---|---|---|---|
| 8.0 | **Turn telemetry and `@traceable`** | §51, §44 | ☐ *(**zero `@traceable` decorators exist in the backend**, and §51 requires one on every extractor, routing decision, direct Azure call and **all four validation layers** — none of the five `validate.py` files has one. The log line is 3 of 5 fields; `node_name` and `duration_ms` are absent. **Numbered before 8.1 because 8.2 cannot be done without it** — WATCH 28's ratified method resolves `run_timeout` by measurement, and nothing records the components today)* |
| 8.1 | Structured errors | §48 | ☐ |
| 8.2 | Per-node timeouts + compensating actions | §44, §45 | ☐ |
| 8.3 | Circuit breakers + fallback chain (levels 1,2,4) | §46 | ☐ |
| 8.6 | Context recovery (§44 Step 2) | §44, §45 | ☐ *(§44's pipeline is seven steps; six were scheduled and Step 2 — "save partial results, resume" — had no step. Native at LangGraph ≥1.2.6, which the venv already satisfies)* |
| 8.7 | `delete_blob` + upload lifecycle | §10, S-C08 | ☐ *(**WATCH 10 said "owed as its own step" and that step was never created.** Uploaded blobs are orphaned forever. A new SPEC-GAP is owed with it — S-C08 owns the path and no behaviour governs its deletion)* |
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
