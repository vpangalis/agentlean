# CLAUDE CODE PROMPT — Control phase review (§39.5) — the final phase

*Self-contained. Paste this whole file into Claude Code. Founder-ratified
2026-08-27, AgentLean / Agent Improve phase-review workstream. Renames,
`phase_metrics`, and the S-C32 `references_metric_name` key are already global
(commits through 36e7b8a) — DO NOT re-sweep or re-plumb. Apply as one change set.
This completes the five-phase DMAIC specification.*

Two ratified decisions carried in this prompt:
- **F-12:** add `actual_close_date` to Control as **Tier 2** (ControlOutput 16 → 17).
- **F-14:** `phase_metrics` is the authoritative store of all N per-metric
  comparisons; `post_improvement_metrics` is the primary metric's Tier-1 link;
  single-authority invariant (primary `phase_metrics.actual` == `post_improvement_metrics` value).

---

## STEP 1 — Write §39.5 (Control)

Replace the §39.5 stub in `ARCHITECTURE.md` with **APPENDIX 1** verbatim (an INDEX
referencing the cross-cutting specs — do not copy those mechanisms in). Update
§39.4.12 so Control is now ratified and the five-phase set is complete. There is no
§39.6.

## STEP 2 — Schema change: add `actual_close_date` (F-12)

Add `actual_close_date: str` (ISO) to `ControlOutput` (schema + §63.5), **Tier 2**.
`ControlOutput` 16 → 17. Update §40's count table (Control 16 → 17) and §35's Control
row (3 Tier 1 / 9 Tier 2). It is the achieved completion date, paired with Define's
planned `target_date` (a slipped date does not invalidate the improvement — the same
logic as §39.1.2). Update `CLAUDE.md` §9.7/§10.7 counts.

## STEP 3 — `phase_metrics` comparison form + single authority (F-14)

Specify (in §39.5.3 as written, and as a note on `ControlOutput` §63.5) that
Control's `phase_metrics` carries one entry per registry metric with
`{name, baseline, target, actual, delta, met, source: "after"}` — the authoritative
store of all N comparisons. `post_improvement_metrics` (Tier 1, dict) remains the
**primary** metric's deterministic cross-phase link to Measure's `baseline_mean`,
carrying `references_metric_name`. Enforce the **single-authority invariant** (as
Measure, §39.2.3, via `assert_single_authority` / `core/metrics.py`): the primary
metric's `phase_metrics.actual` equals `post_improvement_metrics`'s value — a
mismatch raises. The grader grades **every** `phase_metrics` entry, not only the
primary. Extend the existing single-authority test to Control.

## STEP 4 — Write / conform the Control SKILL.md

**Check first by LISTING the skills directory — do not trust a search miss** (the
Analyse and Improve SKILL.md both existed when a search suggested otherwise). If
`skills/dmaic-control-phase/SKILL.md` exists, **restructure and conform** its sound
content to §39.5; if not, write it from §39.5. Either way it must be
**byte-consistent with the coaching script embedded in §39.5.10** (§39.1.7 embed
pattern): preamble, Improve-recap opening, one Explain/Show/Ask/Confirm block per
field in §39.5.2 order, the seven-step block for each control-chart tool and
`post_improvement_cpk`, the two-movements framing, the five-part control-plan
coaching, metric literacy, and a **project-closure closing** (there is no next
phase). `allowed-tools` MUST equal §39.5.5's **12** (7 universal + `xbar_r_chart_limits`,
`imr_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk`) by set
comparison. Populate the four `CoachingResponse` presentational fields (WATCH 9) and
carry the §32 contradiction-check instruction.

## STEP 5 — `CONTROL_RUBRIC` (Layer 2d)

Write the gate rubric, parallel to the other four. Tier 1 fails / Tier 2 warns.
Encode the three guards: **link back to baseline** (`post_improvement_metrics`
verified by lookup, §42, B2 — the only Tier-1 cross-phase ref); **control plan
complete AND delivered** (all five sub-plans populated, `handover_documented` names
an accepting owner — §41, B1); **stability before capability again**
(`post_improvement_cpk` only after a fresh stability check). Grade every
`phase_metrics` comparison, not just the primary.

## STEP 6 — Register, amendment records, closure

- §66 register: mark **F-12 and F-14 resolved**; note the five-phase reviews complete.
- §35: confirm Control's **3 Tier 1 / 9 Tier 2** split ratified at this review.
- Amendment records: `ARCHITECTURE.md` version bump + changelog; `CLAUDE.md` §0.x
  (the `actual_close_date` field and count changes); CONTINUITY update — **all five
  phases ratified, the DMAIC phase-review workstream complete**; note what remains
  (WATCH 7 orchestrate.py, G-27/G-28 mappers & gate assembly, root-reference
  back-port) as the path from ratified spec to built code.

## VERIFY AND REPORT

1. §39.5 present, twelve subsections, no dangling references; no §39.6.
2. `ControlOutput` is **17** (`actual_close_date` added, Tier 2); §40 / §35 / §9.7 /
   §10.7 counts updated and agreeing.
3. `post_improvement_metrics` carries `references_metric_name`; the grader matches on
   it; the single-authority invariant is enforced for Control and unit-tested.
4. Control SKILL.md byte-consistent with §39.5.10, `allowed-tools` == 12;
   `CONTROL_RUBRIC` present with all three guards.
5. All five atomic units green (Define / Measure / Analyse / Improve / Control).
6. Commit body: §39.5 landed, `actual_close_date` added, F-12 + F-14 closed, Control
   SKILL.md + `CONTROL_RUBRIC` written/conformed, **five-phase DMAIC spec complete**.

---
---

# APPENDIX 1 — §39.5 verbatim (write into ARCHITECTURE.md, replacing the stub)

> **F-12** — add `actual_close_date` (§39.5.2); **F-14** — how Control presents and
> grades N per-metric comparisons (§39.5.3). Recommendations below; both need a nod.

---

## 39.5.1 Purpose

Control makes the gain stick. It confirms the improvement actually held against the
baseline and the target, builds the five-part control plan that keeps the process
from regressing, verifies the financial impact, and hands a monitored, documented,
owned process to the business before the project closes. It is where the
measurement thread that began in Define is finally closed: before → after, on the
same measure.

## 39.5.2 The ordered field list — the `field_index` sequence

Coached in **methodology order** — confirm it held, lock it in, verify, hand over,
close. Schema: **§63.5 — S-C31**.

| # | Field (`artifacts` key) | Type | Tier | Note |
|---|---|---|---|---|
| 1 | `post_improvement_metrics` | `dict` | 1 | The AFTER values; cross-phase ref → Measure `baseline_mean`. **The only Tier-1 cross-phase reference** (§42) |
| 2 | `improvement_delta` | `str` | 2 | The change from baseline, per metric |
| 3 | `control_plan` | `dict` | 1 | **Five sub-plans** — documentation, monitoring, response, training, aligning_systems (§41) |
| 4 | `financial_impact_verified` | `str` | 2 | Realised saving — the actual against Define's `calculate_expected_savings` estimate |
| 5 | `sustainability_check` | `str` | 2 | How the gains are maintained after the project |
| 6 | `handover_documented` | `str` | 2 | Named process owner accepting ongoing ownership |
| 7 | `actual_close_date` | `str` (ISO) | 2 | **NEW (F-12)** — the achieved completion date, paired with Define's `target_date` |
| 8 | `lessons_learned` | `str` | 2 | Feeds the case index (§23.3) |
| 9 | `transferability` | `str` | 2 | Yokoten — feeds `rag_lookup_case_history` (§24) |
| 10 | `project_signoff` | `str` | 2 | Champion + Belt + Finance |
| 11 | `secondary_metrics` | `str` | 2 | Final re-check |
| 12 | `issues_and_barriers` | `str` | 1 | Always last |

`ControlOutput` = these twelve **+** `phase_metrics` (§39.5.3) **+** four
gate-metadata fields = **17** (was 16; `actual_close_date` is the added field).
**3 Tier 1, 9 Tier 2.**

> **F-12 recommendation:** `actual_close_date` is **Tier 2** — a slipped date does
> not invalidate the improvement (the same logic that makes Define's `target_date`
> a planning parameter, §39.1.2). It is the paired value Control captures against
> Define's planned `target_date`. §40 count rises 16 → 17; §35's Control row
> becomes 3 Tier 1 / 9 Tier 2.

## 39.5.3 The metric registry, the comparison, and single authority (closes F-14)

Control closes the measurement thread. Its `phase_metrics` entry carries the full
per-metric comparison — the AFTER value against the Define target and the Measure
baseline:

```
phase_metrics = [
  {name: "invoice_error_rate", baseline: "12.3%", target: "<3%",
   actual: "2.8%", delta: "-9.5pp", met: "yes", source: "after"},
  {name: "invoice_cycle_time", baseline: "2.6 days", target: "<1.5 days",
   actual: "1.4 days", delta: "-1.2 days", met: "yes", source: "after"}
]
```

**F-14 recommendation — how N comparisons present and grade:**
- **`phase_metrics` is the authoritative store of all N comparisons**, one entry
  per registry metric, each carrying `baseline` (from Measure), `target` (from
  Define `target_value`), `actual`, `delta`, `met`. This is where a multi-metric
  project shows every Y closed.
- **`post_improvement_metrics` (Tier 1, dict) is the primary metric's deterministic
  link** back to Measure's `baseline_mean`, carrying `references_metric_name` (the
  uniform S-C32 shape, 43c4201). It is the gate-blocking link (§42, B2).
- **Single-authority invariant** (as Measure, §39.2.3): the primary metric's
  `phase_metrics` `actual` **equals** `post_improvement_metrics`'s value — a
  mismatch is a wiring defect. Additional metrics live only in `phase_metrics`.
- **The grader grades every entry**, not just the primary: a project that met its
  primary metric but silently missed a secondary criterion has not fully
  succeeded, and `phase_metrics` is where that shows.

## 39.5.4 Two movements — confirm it held, then lock it in

*Control's methodology core (parallel to §39.3.4 / §39.4.4).*

**Movement 1 — confirm (did it hold?).** Measure the improved process and compare:
`post_improvement_metrics` against the Measure baseline, `phase_metrics` against the
Define target. Re-check **stability before capability** (§39.5.6) before running
`post_improvement_cpk`. Output: `post_improvement_metrics`, `improvement_delta`, the
per-metric comparison. **A Control phase that cannot show before→after on the same
measure has demonstrated nothing** (§42, B2) — this is the thread closing.

**Movement 2 — lock (make it stick).** Build the five-part `control_plan` and hand
the process over. The bright line: **a control plan written is not a control plan
delivered.** The most common real Control failure is a training plan authored but
never run (§41, B1) — so the grader checks all five sub-plans are populated, and
`handover_documented` names an owner who has actually accepted.

## 39.5.5 Tools bound to Control

Passed to the executor via `tools=` on `create_agent` (§18). **Twelve** — under the
16 cap (§30).

- **The universal seven** (§29.2) — `propose_template` carries the control-plan,
  SOP and reaction-plan templates; `propose_diagram` renders the control charts.
- **Five computation tools** (§30 binding; specified §69), standard SPC names kept:

| Job | Tools | Use |
|---|---|---|
| Variable control limits, subgroups | `xbar_r_chart_limits` | Monitoring plan, batched measurements |
| Variable control limits, one-per-period | `imr_chart_limits` | **The default for service/transactional data** (§30) — do not invent subgroups |
| Attribute limits, proportion | `p_chart_limits` | Defect-rate monitoring |
| Attribute limits, counts | `c_chart_limits` | Defect-count monitoring |
| Capability held | `post_improvement_cpk` | The improved process's capability — **after** a fresh stability check |

Run under the seven-step pattern (§43.1). SKILL.md `allowed-tools` MUST equal this
subset (§32). The chosen chart type feeds the `monitoring` sub-plan of `control_plan`.

## 39.5.6 Conditions — guards, routing, gate

**Three methodology guards** (Control's sequence locks):

1. **Link back to the baseline (Tier 1).** `post_improvement_metrics` references
   Measure's `baseline_mean` by lookup (§42, B2) — the only Tier-1 cross-phase
   reference in the system, because a result that cannot be tied to the baseline
   proves nothing.
2. **The control plan must be complete AND delivered.** All five sub-plans
   populated (§41, B1); `handover_documented` names an owner who accepted — a plan
   on paper that no one runs is the phase's classic failure.
3. **Stability before capability, again.** `post_improvement_cpk` runs only after a
   fresh stability check on the improved process — the same lock as Measure's
   `calculate_cpk` (§39.2.6). A capability figure on an unstable new process is as
   meaningless here as it was at baseline.

**Routing conditions** — the five-node cycle (§13), `Command`-routed (§15). Control
is the terminal phase: on gate pass, `gate_apply` populates
`SupervisorState.final_output` through Control's output mapper (§5, S-C31 B3), and
the supervisor's static edge runs to `END` — there is no next phase.

| Where | Condition | Goes to |
|---|---|---|
| `planner` (S-F13 DP1) | current field incomplete, or more remain | `executor` (`field_index++`) |
| `planner` | all 12 captured | `validation_stack` |
| `validation_stack` | 2b presence of the **3 Tier 1** + 2d `CONTROL_RUBRIC` pass | `gate_review` |
| `validation_stack` | fail | `planner` (+ `validator_feedback`); `gate_attempts ≥ 3` → escalation (§38) |
| `gate_apply` | Belt approve | populate `final_output` → `END` (project complete) |
| `gate_apply` | Belt reject | `planner` (+ `rejection_feedback`) |

**Gate-pass condition:** the 3 Tier 1 fields present and `CONTROL_RUBRIC` clears;
the 9 Tier 2 fields warn only, a skip recorded in `acknowledged_gaps` (§35).

## 39.5.7 State parameters (`ControlState`)

*Indexes §6 / §58.2 — S-C02.* `ControlState` extends `PhaseState`:

| PhaseState field | In Control |
|---|---|
| `artifacts` | the 12 captured fields + `phase_metrics` + `computation_results` |
| `field_index` | walks the §39.5.2 list (0–11) |
| `computation_results` | the control-chart limits and `post_improvement_cpk` run; the grader scans for the chart-type evidence behind the monitoring sub-plan |
| `final` / `final_output` | on gate pass, Control's mapper writes `SupervisorState.final_output` — the project's terminal artifact (§5, B3) |
| `gate_attempts` | Control's own retry counter, cap 3 |
| `uploads` | post-improvement data, signed control plan, sign-off record |

## 39.5.8 Metric literacy — what each metric and statistic means

New requirement (§32/§43.7), Control instance. The coach teaches, in plain
language (§50):

- **The metric** — echo its Define `meaning`; frame the closure ("your error rate
  started at 12.3%, you targeted under 3%, and it's now 2.8% — here's how we keep
  it there").
- **The statistic** — the seven-step *educate* step (§43.1 step 1) for **control
  limits** and the improved **Cpk**. *"Control limits are the voice of the process —
  the range it naturally runs in. A point outside them is a signal to act, not
  noise to ignore. That's what your monitoring plan watches for."*

Never a raw dump (§43.1).

## 39.5.9 Gate, storage, progress view

- **Three Tier 1 fields block** the gate (§35) — the smallest Tier 1 set. Nine
  Tier 2 warn only — the largest Tier 2 set, because Control is rich in
  best-practice closure steps the Belt should be coached toward but not gated on.
- **The live gate document** (§50) renders the before→after comparison per
  `phase_metrics` `name`, the control charts via `propose_diagram`, the five-part
  `control_plan` as a table, and `computation_results` with interpretation.
  Narrative from captured field text + `computation_results` + `phase_metrics` —
  never `CoachingResponse` turn fields (§50, WATCH 9).
- **Two progress bars**, Tier 1 and Tier 2.
- Written **once** to `store/projects/{case_id}/artifacts/control.json` by
  `gate_apply` (§9, §33); this write **also** finalises the project (§5).

## 39.5.10 The SKILL.md content

`skills/dmaic-control-phase/SKILL.md` is generated from this section and must match
verbatim, **embedded here in §39.1.7's format** — preamble, phase opening (an
Improve-recap: show the Belt the `selected_solution` and `pilot_result` they arrive
with, and the Define `target_value` they are closing against), one
Explain/Show/Ask/Confirm block per field in §39.5.2 order, the seven-step block for
each control-chart tool and `post_improvement_cpk`, the two-movements framing, the
five-part control-plan coaching, metric literacy (§39.5.8), and a **project-closure
closing** (not "advance to the next phase" — there is none). **Authoritative during
the refactor.**

> **Verify first — do not assume.** Whether `skills/dmaic-control-phase/SKILL.md`
> already exists must be checked by listing the directory, not by a search miss (the
> Analyse and Improve SKILL.md both existed when a search suggested otherwise). If it
> exists, **restructure and conform, do not overwrite** sound content; if not, write
> it from this section.

## 39.5.11 Cross-phase reads and writes — the thread closes here

**Reads across the whole project:**
- **Define**: `metric_definitions` (registry), `target_value` (**what actual is
  compared to**), `target_date` (paired with `actual_close_date`),
  `calculate_expected_savings` result (the estimate `financial_impact_verified`
  confirms).
- **Measure**: `baseline_mean` and `phase_metrics` (**what `post_improvement_metrics`
  references** — the before values), `stability_assessment` (the method to re-run).
- **Improve**: `selected_solution` (**what is now in place to hold**),
  `implementation_plan`, `pilot_result` (the expected effect the actual confirms).

**Writes**: the 12 content fields, `phase_metrics` (the closing comparison),
`post_improvement_metrics` (with `references_metric_name`), and — on gate pass —
`SupervisorState.final_output` (§5).

## 39.5.12 The measurement thread, closed

Control is the last phase; there is no §39.6. The thread that opened in Define is
now closed end to end, and it is traceable by one key across all five gate
documents:

```
Define    metric_definitions + target_value        — the metric named, the target set
Measure   phase_metrics.baseline_mean               — the before value, measured
Analyse   phase_metrics (root cause explaining it)  — why it was where it was
Improve   phase_metrics.pilot_effect                — the fix, proven in pilot
Control   phase_metrics.actual vs target            — the after value, the gain locked
```

**Define, Measure, Analyse, Improve and Control are all ratified. The five-phase
DMAIC specification is complete.**
