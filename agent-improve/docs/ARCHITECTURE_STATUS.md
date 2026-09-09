<!--
Document: agent-improve/docs/ARCHITECTURE_STATUS.md
Created: 2026-09-08 (step 6.8's governance commit)
Purpose: The REPO-SIDE SOURCE for the board's architecture panel. What exists in
         the tree, drawn as containers and control points rather than as steps.
         BUILD_TRACKER.md answers "how far along the spine are we"; this answers
         "what is actually wired, and where are the holes".
Rule:    Verified against the tree, never from memory or from a document. Every
         figure here was read out of the code on the date in the header.
Guard:   `.claude/hooks/commit-msg-refactor-guard.py` rule 2 requires this file
         to be staged by any commit touching a WATCHED PATH (listed at the end).
Legend:  ✅ built · ⚠️ built with a known defect · ☐ not built · ⛔ blocked
-->

# Agent Improve — Architecture Status

# verified against the tree 2026-09-08 · at commit 6.9
# every count below is reproduced by a command in «Re-running the counts»

**This is what exists, not what is specified.** `ARCHITECTURE.md` is the build
target; `BUILD_TRACKER.md` is the spine's progress; this is the standing answer
to *"is that thing actually wired?"* — the question the coverage audit had to
reconstruct by hand because nothing recorded it.

**⚠️ means built and defective, which is the row that costs measurements.** A
`☐` is honest — nobody is relying on it. A `⚠️` looks finished from every angle
except the one that matters, and `phase_context` cost six steps of live
measurements by sitting in that state unrecorded.

---

## Level 1 — the eight blocks

| # | Block | Built / total | The parts |
|---|---|---|---|
| **1** | **API surface** — §49 | **11 / 12** | ✅ `/health` `/summarise` `/context` `/cases` `/ask` `/gate` `/gate/review/{case}/{phase}` `/upload` `/files/{case}/{file}` `/registry` `/cases/{case}` · ☐ `/ask/stream` SSE (step 10.1) |
| **2** | **Supervisor graph** — §12, §15 | **6 / 6 nodes** ⚠️ | ✅ five phase nodes + `escalate`, seven static edges, checkpointer and store attached · ⚠️ **it is the target topology, not the runtime** — `get_graph()` still returns the one-turn parent (WATCH 23); the swap is Stage 7's `interrupt()` |
| **3** | **Phase subgraphs** — §13 | **5 / 5 phases · 5 / 5 nodes** | ✅ one parameterised builder, all five phases wired: `planner` `executor` `validation_stack` `gate_review` `gate_apply` · ✅ `PhaseState`, no checkpointer of its own (§16) · ✅ ten boundary mappers |
| **4** | **The coaching agent** — §17, §18, §26 | **2 / 3 nodes** | ✅ `planner` (structured `CoachingPlan`, temp 0.1) · ✅ `executor` (`create_agent`, `response_format=CoachingResponse`) · ☐ `analyse_executor_node` — §26's planned multi-hop (step 6.10; `hop_results` / `synthesis_output` have no writer) |
| **5** | **Middleware stack** — §19 | **8 / 8 mounted** ⚠️ | all eight construct and fire; two carry defects — see the control-point table |
| **6** | **Tools and knowledge** — §23–§32 | **25 / 27 tools · 3 / 3 indexes** | ✅ 3 `rag_lookup_*` + `propose_template` + `propose_diagram` · ☐ `check_gate_status` (7.1) ☐ `request_human_approval` (7.5) — WATCH 25 · ✅ 20 computation tools, bound 1/8/5/1/5 per phase · ✅ `load_skill` via middleware 2 · ✅ **5 of 5 SKILL.md files exist, load, and carry all seven of §32's mandatory items** — Define's A→F flow, Uploads and §43.7 metric literacy landed at 6.9. All five byte-match their §39.x.10 section |
| **7** | **Validation, gates and escalation** — §33–§38 | **1.5 / 9** | ⚠️ Layer 2b delegates to the v1 `validate_{phase}` and **all five gates are inert** · ✅ Layer 2a is `CoherenceMiddleware` · ☐ Layers 2c, 2d ☐ nine-step HITL ☐ two tiers + `warning` ☐ escalation logic ☐ §37 re-approval cascade (7.6) |
| **8** | **Persistence and cross-cutting** — §8–§10, §44–§48, §51–§52 | **3 / 3 persistence · 1 / 10 cross-cutting** | ✅ checkpointer (Azure Blob, per `case_id`) ✅ Store (cross-phase artifacts) ✅ case blob (system of record) · ✅ §44 Step 0 only · ☐ §44 Steps 1–6 ☐ §46 circuit breaker + fallback chain ☐ §48 structured errors (the schema exists, nothing raises it) ☐ **§51 tracing — zero `@traceable` in the backend** ☐ §52 evaluation — no suite ⛔ §46 L3 cache (Redis) |

**Block 8 is the one that compounds.** With no tracing, every investigation
needs a hand-built harness, and WATCH 28's ratified *"set the limits from
measured data"* cannot run at all. That is why §51 is numbered **8.0**, ahead of
the step that consumes it.

---

### Re-running the counts

**Every number in this document is produced by one of these commands.** The
header promises *"verified against the tree, never from a document"*, and until
2026-09-08 that promise was broken by the row it mattered most on: *"1 of 5
SKILL.md files written"* was copied from `CONTINUITY.md` on the day this file
was created and was wrong from its first commit. **A re-runnable row is
verified. A bare number is a claim** — and a claim ages without saying so.

Run from the repo root. The Python ones `cd agent-improve` first and use that project's venv — the repo-root `.venv` is a different, older interpreter (WATCH 2), so `python` alone gives the wrong answer or none.

```sh
# Block 1 — API surface (11)
grep -cE '^@router\.(get|post|delete|put)' agent-improve/backend/gateway/routes.py

# Block 3 — phase subgraph nodes (5)
grep -c 'builder.add_node' agent-improve/backend/phases/subgraph_common.py

# Block 5 — middleware mounted (8)
#   7 constructor calls + `coherence`, which is built above the list and
#   passed by name so position 8 can hold a reference to it.
grep -c 'Middleware(\|^            coherence,' agent-improve/backend/phases/nodes_common.py

# Block 6 — universal tools BUILT, of 7 ratified (5)
(cd agent-improve && ./.venv/Scripts/python -c 'from backend.knowledge.tools import UNIVERSAL_TOOLS as U; print(len(U))')

# Block 6 — distinct computation tools (20), and the per-phase split (1/8/5/1/5)
(cd agent-improve && ./.venv/Scripts/python -c 'from backend.knowledge.computation import COMPUTATION_TOOLS_BY_PHASE as C; print(len({t.name for p in C for t in C[p]}))')
(cd agent-improve && ./.venv/Scripts/python -c 'from backend.knowledge.computation import COMPUTATION_TOOLS_BY_PHASE as C
from backend.phases.mappers_common import PHASE_ORDER as P
print("/".join(str(len(C[p])) for p in P))')

# Block 6 — SKILL.md files that EXIST (5)
ls agent-improve/skills/*/SKILL.md | wc -l

# Block 6 — SKILL.md files carrying §32's metric-literacy item (5)
#   The item Define lacked until 6.9, and the cheapest single proxy for
#   §32 conformance. It is a proxy, not a proof — see the note below.
grep -l 'METRIC LITERACY' agent-improve/skills/*/SKILL.md | wc -l

# Block 6 — each phase script byte-matches its §39.x.10 section (5 of 5)
(cd agent-improve && ./.venv/Scripts/python - <<'EOF'
import io, re
arch = io.open('ARCHITECTURE.md', encoding='utf-8').read()
SEC = {'define':'39.1.7','measure':'39.2.10','analyse':'39.3.10',
       'improve':'39.4.10','control':'39.5.10'}
for ph, sec in SEC.items():
    i = arch.index(f'#### {sec}')
    j = arch.index('\n#### ', i + 1)
    m = re.search(r'\*\*\[OPENING', arch[i:j])
    script = arch[i:j][m.start():].rstrip('\n')
    skill = io.open(f'skills/dmaic-{ph}-phase/SKILL.md', encoding='utf-8').read()
    print(f'{ph:8s} {script in skill}')
EOF
)

# Block 8 — @traceable decorators in the backend, excluding tests (0)
grep -rl '@traceable' agent-improve/backend --include=*.py | grep -v tests | wc -l
```

> **The `METRIC LITERACY` grep is a proxy and is labelled as one.** It answers
> "does this file carry the one §32 item Define was missing", not "does it carry
> all seven". **A grep is exactly how the wrong count was produced twice** — the
> 6.9 scoping audit scored Define 3.5/7 on a keyword pass, then 4.5/7 on a
> second, because the file carries all seven of `calculate_expected_savings`'s
> steps without ever using the phrase "seven-step". The full check is reading
> the file against §32's list; this line is the cheap regression signal, not a
> replacement for it. `DECISIONS.md` Part AO.

---

## Level 3 — the control points

**Every place the system can stop, retry, cap, interrupt or checkpoint.** This
is the table the coverage audit needed and had to rebuild by grep.

### Middleware — declaration order is nesting order; 6–8 execute in reverse

| # | Middleware | Hook(s) | Status |
|---|---|---|---|
| 1 | `BeforeModelStateInjection` | `before_agent` composes · `wrap_model_call` prepends | ✅ **as of 6.8 it injects `phase_context`.** Was ⚠️ from 6.3 to 6.8 — composed the block without it |
| 2 | `DMAICSkillsMiddleware` | `before_agent` + registers the `load_skill` tool | ✅ mounted and working; **all five SKILL.md files exist, load and are §32-conformant** as of 6.9. This table carried "1 of 5" from its first commit until 2026-09-08 — copied from a document, which is what the counts block above now prevents |
| 3 | `SummarizationMiddleware` | `before_model` | ✅ LangChain core, as shipped · trigger 100k tokens, keep 20 |
| 4 | `ModelRetryMiddleware` | `wrap_model_call` | ✅ `max_retries=2` → three attempts. The only model-retry layer; the factory's own is pinned to 0 |
| 5 | `ToolRetryMiddleware` | `wrap_tool_call` | ✅ `max_retries=2`, `on_failure="continue"` — a failed retrieval does not kill the turn. **Costs no graph steps** (measured at 6.4) |
| 6 | `ContradictionDetectionMiddleware` | `after_agent` — **executes first** | ⚠️ detects and sets `contradiction_flag`; **the §37 re-approval cascade it exists to trigger is unbuilt** (step 7.6) |
| 7 | `CoherenceMiddleware` | `after_agent` — executes second | ✅ validation Layer 2a. Can stand the grader down |
| 8 | `DMAICGraderMiddleware` | `after_agent` — executes third | ✅ coaching-quality grading, per turn |

> **The list is declared grader → coherence → contradiction and executes the
> other way.** `before_*` hooks fire outermost-first, `after_*` innermost-first,
> from one list. For 1–5 declaration and execution coincide; for 6–8 they
> invert, which is why the numbering above is EXECUTION order and the
> declaration is its mirror. `test_all_eight_positions_execute_in_the_ratified_order`
> asserts what executes, not what is listed.

### Interrupts

| Point | Status |
|---|---|
| `interrupt()` at `gate_review` — §33 | ☐ **not built.** The node exists and passes through; Stage 7.3 raises it |
| `request_human_approval` tool — S-F22 | ☐ not built (step 7.5) |

**Nothing in the system currently pauses for a human.** Three consequences ride
on that and are recorded rather than rediscovered: `gate_attempts` cannot
accumulate across turns (WATCH 18), the supervisor graph is not the runtime
(WATCH 23), and §47's reconciliation sweep cannot be written yet (WATCH 13).

### Checkpoints

| Point | Status |
|---|---|
| `AzureBlobCheckpointSaver` on the parent graph, keyed by `case_id` | ✅ live since 4.2 |
| Phase subgraphs — no checkpointer of their own; `checkpoint_ns` assigned by the engine | ✅ §16, deliberate |
| ETag / `ConcurrentTurnError` on `latest.json` | ⚠️ optimistic, not the specified lease. **A concurrent turn is LOST, never interleaved**, and a failed write orphans a history blob (WATCH 15 — out of scope, post-refactor) |
| Store — `("projects", {case}, "artifacts")` | ✅ written by the boundary mappers |
| Store — `("projects", {case}, "case")` | ✅ **as of 6.8.** Had no writer at all from 3.3 to 6.8 (WATCH 19) |

### Caps

| Cap | Value | Status |
|---|---|---|
| Retrieval hops per Belt turn — §3.7 | **5**, counted in per-turn copies of the `rag_lookup_*` tools | ✅ 6.7 |
| `remaining_steps` floor — §26, S-F09 B1 | **2** — below it the coach is built with no retrieval tools | ✅ 6.7 |
| `recursion_limit` backstop — §16 | **50** | ✅ a backstop, **not** the hop cap. It was 11 and standing in for the cap from 6.2 to 6.7 (WATCH 26) |
| Model / tool retries — §19.4, §19.5 | **2** each (three attempts) | ✅ |
| Gate attempts — §34 | **3** (`GATE_MAX_ATTEMPTS`) | ⚠️ **cannot fire.** With no `interrupt()` the subgraph reruns from the mapper each turn, so every submission reports attempt 1 (WATCH 18) |
| Summarization trigger | 100k tokens / keep 20 | ✅ |

### Guards

| Guard | Status |
|---|---|
| `TimeoutPolicy(run_timeout=45)` on the executor node — §44 Step 0 | ✅ the only piece of §44 that exists. Observed firing live |
| `GraphRecursionError` caught in the executor | ✅ belt-and-braces since 6.7; the Belt gets a partial answer, never a stack trace |
| `phase_context` fallback — Define's labelled prose | ✅ **loud since 6.8** — WARNING log plus a marker inside the injected block. Silent from 3.3 to 6.8 |
| `PriorGateDocumentMissing` — an ordering fault raises, never defaults | ✅ |
| `error_handler=` / `phase_error_recovery` on nodes with external writes — §3.6 | ☐ **not built.** WATCH 16, owed at 8.2, blocked on G-35 and G-06 |
| Circuit breaker (3 fails / 30s → OPEN) — §46 | ☐ not built (8.3) |
| Fallback chain — §4.8, §46 | ☐ not built (8.3) |
| Fail-fast env validation at startup — §53 | ✅ |

---

## Corrections against the published Architecture Board (2026-09-07)

Recorded here because the panel is regenerated from this file, so a correction
that lives only in chat gets rebuilt wrong next time.

1. **"25 of 35 steps" — both figures are wrong.** Appendix D is authoritative
   and now reads **28 of 51**. The 35 was an unreconciled hand-count already
   five rows adrift before the audit added eight steps.
2. **"§26 multi-hop + the step guard" under NONE OF THIS EXISTS YET — half
   wrong.** The step guard shipped at 6.7: the five-hop cap, the
   `remaining_steps` off-ramp and the backstop are all live. Only
   `analyse_executor_node` is unbuilt.
3. **"§44 failure pipeline · 7 steps" under NONE OF THIS EXISTS YET — Step 0
   exists.** `TimeoutPolicy(run_timeout=45)` is on the executor node and was
   observed firing. Six of seven are missing, not seven.
4. **"none of the gate exists yet" — overstated.** All three gate nodes exist
   and run; `validation_stack` carries Layer 2b against the v1 validator, and
   Layer 2a is live as `CoherenceMiddleware`. What does not exist is the
   `interrupt()`, Layers 2c/2d, and everything that makes a gate *decide*.
5. **"MIDDLEWARE — 8, IN NESTING ORDER" then numbering 6 contradiction, 7
   coherence, 8 grader — the header contradicts the list.** That numbering is
   EXECUTION order; nesting order is its mirror for 6–8. The caption underneath
   explains the inversion, so only the header is wrong.
6. **"PERSISTENCE — THREE LAYERS, ALL BUILT" — true of the layers, not of the
   Store's contents.** The `case` namespace had no writer until 6.8, which is
   the defect the board's own amber input-mapper note was describing from the
   other end.

**Right, and worth keeping:** the amber-versus-outline distinction, the
`phase_context` call-out, the SKILL.md count, the §37 cascade note, and the
observation that §51 compounds. Items 1 and 2 above are now stale in the
board's favour — both were fixed after it was published.

---

## Watched paths — what obliges an update to this file

Guard rule 2 requires this file staged when a commit touches any of:

```
agent-improve/backend/core/graph.py            supervisor topology, backstop
agent-improve/backend/core/state.py            SupervisorState
agent-improve/backend/core/substate.py         PhaseState, caps
agent-improve/backend/core/checkpointer.py     checkpoints
agent-improve/backend/core/store.py            Store namespaces
agent-improve/backend/middleware/**            the middleware table
agent-improve/backend/phases/subgraph_common.py  nodes, TimeoutPolicy
agent-improve/backend/phases/nodes_common.py   planner, executor, caps, guards
agent-improve/backend/knowledge/tools.py       the universal seven
agent-improve/backend/knowledge/computation.py the twenty
agent-improve/backend/gateway/routes.py        the API surface
agent-improve/backend/storage/blob.py          system of record
```

**The list is deliberately narrow.** A guard that fired on every backend file
would be routed around within a week; these are the twelve paths whose contents
are literally tabulated above, so a change to one of them makes a row here
false.
