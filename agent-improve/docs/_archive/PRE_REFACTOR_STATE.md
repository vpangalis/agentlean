<!--
Document: agent-improve/docs/PRE_REFACTOR_STATE.md
Created: 2026-08-27
Purpose: Functional assessment of where Agent Improve stands the moment the
         five-phase DMAIC specification was completed, before the code refactor
         begins. Retrospective + inventory + readiness. Not a binding document —
         a snapshot for deciding whether to start the build. Binding detail lives
         in ARCHITECTURE.md / CLAUDE.md / CONTINUITY.md / REFACTORING_PROCEDURE.md.
-->

# Agent Improve — State of Play before the Refactor
# 2026-08-27 · ARCHITECTURE.md v1.19 · CLAUDE.md 2.2.29 · CONTINUITY v4.7

Purpose: one honest read of where we are before the first line of refactor code.
Functional, not decorative.

---

## 1. The one-line status

**The specification is complete. The code is not started.** All five DMAIC phases
are ratified in `ARCHITECTURE.md`; the backend is still the v1 tree (one of 38
procedure steps done — the dependency upgrade). We are at the seam between
"designed" and "built."

---

## 2. What is RATIFIED (the specification)

Complete and internally consistent as of `caf86da`:

- **Five per-phase hubs — §39.1 to §39.5.** Each carries: ordered field list
  (`field_index`), tier split, SIPOC/generation handling, bound tools, methodology
  guards, routing/gate conditions, per-phase state parameters, metric literacy,
  gate-document layout, embedded coaching script, cross-phase reads/writes.
- **Five gate-document schemas — §63.1 to §63.5.** Field counts: Define 18 /
  Measure 15 / Analyse 14 / Improve 14 / Control 17. Tier splits ratified per
  phase at each review.
- **The 20 computation tools — §69 (S-F37 to S-F56).** Named, with inputs, output
  shape, preconditions, phase binding. Spec only; code is built at procedure 5.3.
- **Five Layer-2d rubrics** — MEASURE / ANALYSE / IMPROVE / CONTROL (+ Define's
  gate). Each encodes its phase's methodology guards as Tier-1 checks.
- **Naming convention** — two-tier acronym rule; seven identifiers renamed;
  the 20 tool names and the statistics kept. Applied repo-wide.
- **Structured metric registry** — `metric_definitions` (Define) + `phase_metrics`
  (all five schemas). A fourth exception to the string law, traced by key equality
  on `name`. Single-authority invariant enforced in `core/metrics.py`, unit-tested
  across all five phases.
- **Metric literacy** (§32/§43.7) — every phase teaches what the metric and the
  statistic mean, not only how the tool runs.
- **Embedded coaching scripts** — §39.1.7 / .2.10 / .3.10 / .4.10 / .5.10 hold the
  full scripts; each is byte-consistent with its SKILL.md (the atomic-unit check).
- **The measurement thread, closed** — one key traceable across all five gate
  documents: Define target → Measure baseline → Analyse root cause → Improve pilot
  → Control actual.

**Confidence:** high on internal consistency (every §39.x reference resolves; five
atomic units green; 30 tests pass). Methodology grounded against current LSS
sources at each review. The specs meet the five-point "prevents a mis-build" bar.

---

## 3. What is BUILT (the code) — the honest part

**The backend is still v1.** From CONTINUITY §4: 55 files, ~7,900 lines, 11 flat
graph nodes, all sync `def`, `routes.py` dispatches by hand and discards the
compiled graph, the checkpointer is wired but inert (zero checkpoints ever
written). Six LLM roles against a target of 11.

**Done: one spine step of 38.** Step 2.3 — the dependency upgrade (LangGraph
1.2.11 etc., `95926d6`). The LangGraph gate on steps 4.1–4.4 and 8.2 is cleared.

**Not yet existing** (per CONTINUITY §4): `core/substate.py`, `core/store.py`,
`middleware/`, `validation/`, `knowledge/{computation,tool_args,fusion}.py`,
`core/reliability.py`, `core/diagrams.py`, `phases/{phase}/{graph,nodes,mappers}.py`.

So: the map is finished; the territory is untouched. `core/metrics.py` and the
five schemas exist because the phase reviews wrote and tested them, but the graph,
the nodes, the middleware and the tool implementations do not.

---

## 4. Retrospective — how the spec got finished this session

The arc (2026-08-26 → 27): entered with Define finalized and Measure mid-review;
left with all five phases ratified.

1. **Measure review** — closed its capture review, wrote the computation-tools
   spec (§69), MSA-as-option, Define-recap opening.
2. **Naming convention** — grounded in the LSS `Y=f(x)` vocabulary and general
   schema-naming practice; landed as a two-tier acronym rule after a trusted-source
   check corrected an initial "spell out everything" instinct.
3. **Structured metric registry** — `metric_definitions` + `phase_metrics`, the
   single-authority invariant. Resolved the "same value in two places" drift risk.
4. **Analyse → Improve → Control** — each reviewed to the Measure template, each
   surfacing and correcting a latent defect in its pre-existing SKILL.md (wrong
   field order in all three; a stale reference shape in Analyse's).
5. **Coaching scripts embedded** — §39.x.N made authoritative-in-fact, not just
   in claim, with byte-consistency checks.
6. **Define §32 gap closed** — `calculate_expected_savings` seven-step block.

**What worked, worth keeping for the build:**
- Draft-and-ratify in Desktop, execute in Claude Code, one commit per step, each
  with a raw-grep / atomic-unit / test verification.
- **Check by listing, not by searching** — three phase SKILL.md files "did not
  exist" on a search and existed on an `ls`. Assume nothing; verify against the
  filesystem.
- **A check that cannot fail is worse than no check.** Every verification proved it
  could fail first (the single-authority tests, the atomic-unit substring checks).
- The registry's key-equality traceability caught real bugs mid-run (the Analyse
  `causal_hypothesis` shape the grader would have rejected).

---

## 5. What REMAINS — the build backlog

### The path from spec to code (Claude Code territory)
- **WATCH 7 — `orchestrate.py`.** Still writes v1 Define field names
  (`what`/`where`/`scope_in`…); `validate.py` reads v2. The v1 Define gate is inert
  until this migrates. Procedure **step 3.4 / 4.1**. Owed with it: the Define
  cross-phase briefs in analyse/improve/control. Do not switch readers first (§17).
  **This is the natural first build step.**
- **G-27 — boundary mappers.** `phases/{phase}/mappers.py` — input/output mappers
  per phase. Blocks the per-phase field wiring.
- **G-28 — gate assembly for the four phases beyond Define.** Only Define's
  assembly was written; Measure/Analyse/Improve/Control need theirs (the spec is
  ratified; the code is not).
- **Root-reference back-port.** `AGENTIC_ARCHITECTURE_REFERENCE.md` deliberately
  not renamed; diverges on field names until Improve settles. Back-port then.

### Open watches (not §66 gaps)
- WATCH 1 (§16 persistence local repro — deferred to build step 4.2).
- WATCH 2 (two venvs — confirm which is authoritative before trusting a blocker).
- WATCH 5 (citations must say "PDF page" — belongs in the unbuilt renderer).
- WATCH 6 (PDF page 302 ships as `general` — reachable, not a blocker).
- WATCH 9 (the four `CoachingResponse` presentational fields render nowhere yet —
  UI half is step 10.2; all five SKILL.md now instruct populating them).
- Hook wrinkle — session-start hook doesn't skip `done`; two-line fix owed.

### Gated — do not schedule against these
- `RunControl.request_drain()` unconfirmed (gates 8.5 only).
- Azure Cache for Redis not provisioned (gates 8.4 only).
- Two Azure index schema changes ratified-not-applied (batch, step 9.1).

### The SPEC-GAP register
§66: was 46 identified / 12 closed / 34 open at v4.3; F-12/F-13/F-14 closed since.
Group A empty (no founder rulings outstanding). Group D (computation layer, G-25/
G-36) resolved at spec level. Next gaps are build-side (G-27, G-28).

---

## 6. Readiness assessment — can the refactor start?

**Yes, for the spine.** The phase-review workstream existed precisely so the
schemas and state fields were settled before the backbone was built — that is now
done. The backbone mechanics were verified against current LangGraph (CONTINUITY
§5). The build resumes at **procedure step 2.4** (`set_entry_point` →
`add_edge(START, …)`), with the phase specs (§39.1–39.5) as ratified inputs to the
per-phase steps (3.4, 4.1, 5.3).

**Recommended first move:** WATCH 7 / `orchestrate.py` — it is the smallest,
most-contained real refactor step (migrate the Define writer to v2 names, so the
Define gate stops being inert), it unblocks the Define path end-to-end, and it is a
good rehearsal of the build cadence before the larger structural steps (nodes,
middleware, mappers).

**Honest caveats before committing to the build:**
- The specs are verified for *consistency*, not yet for *runtime* — the first time
  code actually runs the graph (step 4.2) is where the deferred repros (WATCH 1)
  and the "zero checkpoints written" question get settled. Expect the first
  structural steps to surface things the paper review could not.
- The root-reference divergence is a known, tracked debt — fine to carry, but it
  must be paid at back-port or the two architecture files drift permanently.
- Two venvs (WATCH 2) should be resolved before the first build step, so the drift
  hook reads the authoritative one.

---

## 7. One-screen inventory

| Thing | State |
|---|---|
| DMAIC phase specs (§39.1–39.5) | ✅ ratified, all five |
| Gate schemas (§63.1–63.5) | ✅ 18/15/14/14/17 |
| Computation-tool specs (§69) | ✅ 20 named; code at 5.3 |
| Rubrics (Layer 2d) | ✅ five |
| Metric registry + single-authority | ✅ spec + `core/metrics.py` + tests |
| Coaching scripts (embedded + SKILL.md) | ✅ five, byte-consistent |
| Backbone mechanics | ✅ verified vs LangGraph (paper) |
| Backend code (nodes/middleware/graph) | ❌ still v1 |
| `orchestrate.py` (WATCH 7) | ❌ writes v1 names — first build step |
| Mappers (G-27) / gate assembly ×4 (G-28) | ❌ not built |
| Root-reference back-port | ⏸ deferred to post-settle |
| Redis / Azure index changes / request_drain | ⏸ gated |

*Spec: done. Code: at the starting line.*
