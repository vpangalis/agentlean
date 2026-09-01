# CLAUDE CODE HANDOFF — wrap the spec, update the docs, take orchestrate.py

*2026-08-27. The five-phase DMAIC specification is complete (caf86da). This handoff
does two things: (A) records the milestone in the key docs so a fresh session
orients correctly, and (B) executes the first real refactor step, `orchestrate.py`
(WATCH 7). Part A is doc-content; Part B is code and follows the procedure
discipline. Do them as two commits.*

---

## PART A — record the milestone (doc-content, one commit)

**A1. Commit the state doc.** Add `agent-improve/docs/PRE_REFACTOR_STATE.md` (saved
under docs). It is the functional pre-build assessment — inventory, retrospective,
readiness. Not binding; a snapshot. Leave it as written.

**A2. Update `CONTINUITY.md` — it is stale in one place.** §9 version log is
correct (v4.7 records Control complete), but **§5's phase-review status table still
reads "Measure IN PROGRESS / Analyse-Improve-Control Not started"** — false now.
- §5 status table → all five phases **DONE / ratified**.
- §5 "immediate next step" → no longer "finish Measure"; it is **the build**: the
  phase-review workstream is complete, the phase specs (§39.1–39.5) are ratified
  inputs, resume the procedure at **step 2.4**, first real step `orchestrate.py`
  (WATCH 7, Part B below).
- §5 heading still reads "PHASE REVIEWS, then the backbone, then build" — the phase
  reviews are done; note the pivot.
- Add a **v4.8** version-log entry: five-phase spec complete; `PRE_REFACTOR_STATE.md`
  added; build phase opened; `orchestrate.py` migrated (if Part B lands in the same
  push, record it; else note it as the immediate next step).

**A3. Update `REFACTORING_PROCEDURE.md`.** The procedure was written before the
phase specs were ratified. Add a **status banner** near the top: the five DMAIC
phase specs (§39.1–39.5), the five gate schemas (§63.1–63.5), the 20-tool spec
(§69), the five rubrics, and the metric registry are now **ratified inputs** — the
per-phase steps (notably **3.4** mappers/schemas, **4.1** orchestrate/gate wiring,
**5.3** computation tools) build against them rather than against open questions.
Confirm the resume point is **step 2.4** and that no step's precondition still names
a now-closed spec gap (F-12/F-13/F-14, G-25 are closed; G-27/G-28 remain build
gaps). Do not renumber steps — annotate.

---

## PART B — orchestrate.py, the first refactor step (code, its own commit)

*This is WATCH 7, procedure step 4.1. Follow the step discipline: precondition,
change, verify. This is the first step that touches architectural behaviour, so
treat it as the rehearsal of the build cadence.*

**The problem (WATCH 7):** `validate.py` reads the v2 Define field names;
`orchestrate.py` still **writes** v1 granular names (`what` / `where` / `when` /
`who_affected` / `scope_in` / `scope_out` / `how_much_baseline` / `how_goal` /
`target_date` + `estimated_completion_date`). The Define gate is inert until the
writer is migrated — the rename landed ahead of its writer (NOT a defect, no shim,
§17).

**The change:** migrate `orchestrate.py`'s Define capture/write to the ratified v2
Define schema (§39.1.2 / §63.1 / `phases/define/schema.py`):
`business_case`, `team` (list[dict]), `voc_summary`, `problem_statement` (composed
from 5W2H — the 5W2H are coaching prompts, not stored fields, §39.1.3),
`baseline_estimate`, `project_scope` (dict `{in_scope, out_scope}`),
`goal_statement`, `target_value`, `target_date` (single field — `estimated_
completion_date` is retired), `secondary_metrics`, `process_map_sipoc` (dict, 6
keys incl `process_metrics`), `issues_and_barriers`, plus `metric_definitions` and
`phase_metrics`. Migrate the **Define cross-phase briefs read in analyse / improve /
control** to the same v2 names in the same commit.

**Rules:** do **not** switch readers first (§17 — no shim, the writer moves to meet
the reader). Stage by name, never `git add -A`. Raw `grep -rn` sweep to confirm no
v1 Define field name (`what`/`where`/`scope_in`/`estimated_completion_date`…)
survives as a live write. `refactor(arch-v2): commit 4.1 — orchestrate.py Define
writer → v2 names` (or the procedure's exact step id).

**Verify:** the Define gate is no longer inert — `orchestrate.py` writes exactly the
field names `validate.py` reads and `DefineOutput` declares (set-compare the written
keys against `DefineOutput.model_fields`, the same technique that caught the S-F28
assembly gap); the Define atomic unit (schema · validate · SKILL.md) is still green;
the raw sweep shows zero v1 Define field names as live writes; tests pass. Report
the survivor list and the key set-comparison.

---

## Order and reporting

Part A first (records reality even if Part B pauses), then Part B. If Part B raises
anything the paper spec didn't anticipate — the first code to exercise the Define
write path may — stop and report it rather than patching past it; that is exactly
the kind of thing the build is expected to surface (PRE_REFACTOR_STATE §6). Report
both commits and stop.
