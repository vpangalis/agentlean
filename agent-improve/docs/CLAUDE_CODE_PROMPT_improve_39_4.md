# CLAUDE CODE PROMPT — Improve phase review (§39.4) + Define tool-block fix

*Self-contained. Paste this whole file into Claude Code. Founder-ratified
2026-08-27, AgentLean / Agent Improve phase-review workstream. Renames,
`phase_metrics`, and the S-C32 `references_metric_name` key are already global
(commits through cec4e38) — DO NOT re-sweep or re-plumb. Apply as one change set;
split the Define fix into its own commit if you prefer.*

---

## STEP 1 — Write §39.4 (Improve)

Replace the §39.4 stub in `ARCHITECTURE.md` with the section in **APPENDIX 1**
below (verbatim; it is an INDEX referencing the cross-cutting specs — do not copy
those mechanisms in). Update §39.3.12's "the other two phases" language so Improve
is now a ratified exemplar and only Control remains stubbed. Leave §39.5 stubbed.

## STEP 2 — Improve `phase_metrics` + `solution_linked_to_root_cause`

Specify (in §39.4.3 as written, and as a note on the `ImproveOutput` spec §63.4)
that Improve's `phase_metrics` carries the linkage-plus-pilot form —
`{name, moved_by, pilot_effect, source}` — with `"not addressed this phase"` for
untouched metrics. Populate `references_metric_name` in
`solution_linked_to_root_cause` (the uniform S-C32 shape already carries the key
since 43c4201 — Improve is the phase that now fills it). No schema field-count
change (Improve stays 14).

## STEP 3 — Write / conform the Improve SKILL.md

**Check first by LISTING the skills directory — do not trust a search miss**
(the Analyse SKILL.md existed when a search suggested otherwise). If
`skills/dmaic-improve-phase/SKILL.md` exists, **restructure and conform** its sound
content to §39.4; if not, write it from §39.4. Either way it must, per the
embed pattern (§39.1.7) now used by all reviewed phases, be **byte-consistent with
the coaching script embedded in §39.4.10**: preamble, Analyse-recap opening, one
Explain/Show/Ask/Confirm block per field in §39.4.2 order, the seven-step block for
`calculate_doe_main_effects`, the two-movements framing, decision-matrix and
pilot-plan coaching, metric literacy, gate-readiness. `allowed-tools` MUST equal
§39.4.5's **8** (7 universal + `calculate_doe_main_effects`), by set comparison.
Populate the four `CoachingResponse` presentational fields (WATCH 9).

## STEP 4 — `IMPROVE_RUBRIC` (Layer 2d)

Write the gate rubric, parallel to `MEASURE_RUBRIC` / `ANALYSE_RUBRIC`. Tier 1
fails / Tier 2 warns. Encode both guards: **solution traces to the validated root
cause** (`solution_linked_to_root_cause` verified by lookup, §42) and
**pilot-before-rollout** (`pilot_result` Tier 1, practical AND statistical — a
trivial-effect pilot is coached back). Encode DOE belt-gating: three valid answers
to `experiment_justification`, DOE recommended for Black Belts only (§35, S-C30
B1/B2). Check `computation_results` for `calculate_doe_main_effects` evidence behind
any experiment claim, not prose.

## STEP 5 — Define §32 fix: add the `calculate_expected_savings` seven-step block

Define binds `calculate_expected_savings` (§30) but §39.1.7 carries no seven-step
block for it — a §32 violation (every bound computation tool needs one). Insert the
block in **APPENDIX 2** into §39.1.7 **after the `target_value` field block** (the
tool needs `baseline_estimate` and `target_value`), and into
`skills/dmaic-define-phase/SKILL.md` at the matching position so the byte-consistency
check still holds. This is new ratified content, not a rename — note it as such.

## STEP 6 — Tiers, register, amendment records

- §35: confirm Improve's **4 Tier 1 / 5 Tier 2** split ratified at this review.
- §66 register: note §39.4 landed; F-14 (Control per-metric) still the open one.
- Amendment records (closing the set): `ARCHITECTURE.md` version bump + changelog;
  `CLAUDE.md` §0.x if any rule text changed (the Define tool block touches §32
  compliance — record it); CONTINUITY update — Improve now a ratified exemplar,
  §39.4 landed, Define §32 gap closed, only Control (§39.5) remains.

## VERIFY AND REPORT

1. §39.4 present, twelve subsections; every field / tool / state field / condition
   it names resolves to an existing spec entry — no dangling reference.
2. `ImproveOutput` still 14; `solution_linked_to_root_cause` carries
   `references_metric_name`; the grader matches on it.
3. Improve SKILL.md exists, byte-consistent with §39.4.10's embedded script,
   `allowed-tools` == 8 by set comparison; `IMPROVE_RUBRIC` present with both
   guards + DOE belt-gating.
4. Define's `calculate_expected_savings` block present in §39.1.7 AND its SKILL.md,
   byte-consistent; Define now has a seven-step block for its one bound tool.
5. Define / Measure / Analyse atomic units still green; §35 / §40 / §9.7 / §10.7
   counts unchanged and agreeing.
6. Commit body: §39.4 landed, Improve SKILL.md + `IMPROVE_RUBRIC` written/conformed,
   Define §32 gap closed with the `calculate_expected_savings` block.

---
---

# APPENDIX 1 — §39.4 verbatim (write into ARCHITECTURE.md, replacing the stub)

## 39.4.1 Purpose

Improve designs, tests and proves the fix. It generates solutions that target the
validated root cause, selects the best on explicit criteria, decides what level of
experiment the choice needs, and — the discipline that defines the phase —
**pilots on a limited scale before full rollout**, proving the improvement is real
before the organisation commits to it. It ends with a selected, piloted,
evidence-backed solution and a plan to implement it.

## 39.4.2 The ordered field list — the `field_index` sequence

Coached in **methodology order** — generate & select, justify, pilot, prove, plan,
socialise. Schema: **§63.4 — S-C30** (canonical home).

| # | Field (`artifacts` key) | Type | Tier | Note |
|---|---|---|---|---|
| 1 | `selected_solution` | `str` | 1 | Candidates generated (brainstorm), then the best selected on explicit criteria (decision matrix) |
| 2 | `solution_linked_to_root_cause` | `dict` | 2 | Cross-phase ref → Analyse `root_cause_statement`; names the metric (§39.4.3) |
| 3 | `experiment_justification` | `str` | 1 | DOE / simplified / none — **and why**. All three valid; the failure is drifting past the question (§41) |
| 4 | `pilot_result` | `str` | 1 | Piloted on a limited scale; practical **and** statistical significance |
| 5 | `explanatory_power` | `str` | 2 | R² / variance the solution explains |
| 6 | `implementation_plan` | `str` | 2 | Timeline, owner, resources for full rollout |
| 7 | `process_owner_buyin` | `str` | 2 | The owner accepts the solution |
| 8 | `secondary_metrics` | `str` | 2 | Carried from Analyse, re-checked against the pilot |
| 9 | `issues_and_barriers` | `str` | 1 | Always last |

`ImproveOutput` = these nine **+** `phase_metrics` (§39.4.3) **+** four
gate-metadata fields = **14**. 4 Tier 1, 5 Tier 2.

## 39.4.3 The metric registry and Improve's placeholder (linkage form)

Improve's `phase_metrics` entry records which registry metric the selected
solution is expected to move, and what the pilot achieved on it:

```
phase_metrics = [
  {name: "invoice_error_rate", moved_by: "selected solution: onboarding checklist",
   pilot_effect: "12.3% → 4.1% in the pilot cell", source: "pilot"},
  {name: "invoice_cycle_time", moved_by: "not addressed this phase", source: "linkage"}
]
```

`"not addressed this phase"` for any registry metric the solution does not target.
**`solution_linked_to_root_cause` names the metric** via `references_metric_name`
(the uniform S-C32 shape, added 43c4201) — so a multi-metric project links the
solution to the specific Y its root cause explained. The grader resolves the link
by lookup against Analyse's gate document (§42).

## 39.4.4 Two movements — generate-and-select, then pilot-and-prove

*Improve's methodology core (parallel to Analyse's §39.3.4).*

**Movement 1 — choose (generate, then select).** From Analyse's
`root_cause_statement`, the coach helps the Belt **generate** candidate solutions
(brainstorming, poka-yoke / mistake-proofing, `propose_template`) and then
**select** on explicit criteria — a **decision / selection matrix**
(`propose_template`) scoring options against impact, cost, effort and risk. Output:
`selected_solution`, `solution_linked_to_root_cause`. A solution chosen without
visible criteria is the failure this movement prevents.

**Movement 2 — prove (pilot, then confirm).** The chosen solution is **piloted on a
limited scale** and its effect measured. Output: `pilot_result`,
`explanatory_power`. The bright line: **a solution is a proposal until the pilot
data backs it.** Rolling out unpiloted is the failure movement 2 exists to prevent
— especially when the change is costly or hard to reverse.

## 39.4.5 Tools bound to Improve

Passed to the executor via `tools=` on `create_agent` (§18). **Eight** — under the
16 cap (§30).

- **The universal seven** (§29.2) — `propose_template` / `propose_diagram` carry
  the **generation and selection** tools here: brainstorming, the decision /
  selection matrix, mistake-proofing aids. FMEA is **supported if a Black Belt
  raises it** (result → `uploads`), never suggested unprompted, and is not a
  schema field (§41).
- **One computation tool** (§30 binding; specified §69), standard name kept:

| Job | Tool | Use |
|---|---|---|
| Test factor effects | `calculate_doe_main_effects` | Which factors, at which settings, move the outcome — when a designed experiment is run |

Run under the seven-step pattern (§43.1). SKILL.md `allowed-tools` MUST equal this
subset (§32).

## 39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate

**Two methodology guards** (Improve's sequence locks):

1. **The solution must trace to the validated root cause.** `solution_linked_to_
   root_cause` references Analyse's `root_cause_statement` by lookup (§42). A
   solution that does not address the proven root cause is solving the wrong
   problem — the rubric requires the link.
2. **Pilot before full rollout.** `pilot_result` (Tier 1) gates on evidence from a
   limited-scale trial showing **practical AND statistical** significance — the
   same two-gate test as Analyse (§39.3.6). A pilot that is statistically
   significant but trivial in effect is coached back, not passed.

**DOE is belt-gated** (§35, S-C30 B1/B2): `experiment_justification` accepts three
valid answers — DOE conducted, a simplified one-factor experiment, or none needed
because the fix follows directly from the root cause. **All three pass**; the
failure is drifting past the question. DOE is **recommended for Black Belts,
suppressed for Green Belts.**

**Routing conditions** — the five-node cycle (§13), `Command`-routed (§15):

| Where | Condition | Goes to |
|---|---|---|
| `planner` (S-F13 DP1) | current field incomplete, or more fields remain | `executor` (`field_index++`) |
| `planner` | all 9 captured | `validation_stack` |
| `validation_stack` | 2b presence of the **4 Tier 1** + 2d `IMPROVE_RUBRIC` pass | `gate_review` |
| `validation_stack` | fail | `planner` (+ `validator_feedback`); `gate_attempts ≥ 3` → escalation (§38) |
| `gate_apply` | Belt approve / reject | `END` / `planner` (+ `rejection_feedback`) |

**Gate-pass condition:** the 4 Tier 1 fields present and `IMPROVE_RUBRIC` clears;
the 5 Tier 2 fields warn only, a skip recorded in `acknowledged_gaps` (§35).

## 39.4.7 State parameters (`ImproveState`)

*Indexes §6 / §58.2 — S-C02.* `ImproveState` extends `PhaseState`:

| PhaseState field | In Improve |
|---|---|
| `artifacts` | the 9 captured fields + `phase_metrics` + `computation_results` |
| `field_index` | walks the §39.4.2 list (0–8) |
| `computation_results` | the DOE run, if any; the grader scans for `calculate_doe_main_effects` evidence behind an experiment claim, not prose |
| `uploads` | pilot data and any FMEA a Black Belt contributes land here (§29.1) |
| `gate_attempts` | Improve's own retry counter, cap 3 |
| `hop_results` / `synthesis_output` | `[]` / `None` on Improve's typically single-hop turns |

## 39.4.8 Metric literacy — what each metric and statistic means

New requirement (§32/§43.7), Improve instance. The coach teaches, in plain
language (§50):

- **The metric** — echo its Define `meaning`; frame the pilot as moving it
  ("the pilot cut the error rate from 12.3% to 4.1% — here's whether that holds").
- **The statistic** — the seven-step *educate* step (§43.1 step 1) for a DOE
  **main effect** and **R²** (`explanatory_power`). *"A main effect is how much the
  outcome moves when you change one factor from its low to its high setting — the
  bigger it is, the more that factor matters."*

Never a raw dump (§43.1).

## 39.4.9 Gate, storage, progress view

- **Four Tier 1 fields block** the gate (§35). Five Tier 2 warn only.
- **The live gate document** (§50) renders the decision / selection matrix as a
  table, the pilot before/after and any DOE effects as charts via
  `propose_diagram`, and `computation_results` with interpretation, grouped by
  `phase_metrics` `name`. Narrative from captured field text + `computation_results`
  + `phase_metrics` — never `CoachingResponse` turn fields (§50, WATCH 9).
- **Two progress bars**, Tier 1 and Tier 2.
- Written **once** to `store/projects/{case_id}/artifacts/improve.json` by
  `gate_apply` (§9, §33).

## 39.4.10 The SKILL.md content

`skills/dmaic-improve-phase/SKILL.md` is generated from this section and must
match verbatim, **embedded here in §39.1.7's format** — preamble, phase opening
(an Analyse-recap: show the Belt the `root_cause_statement` and
`practical_significance` they arrive with), one Explain/Show/Ask/Confirm block per
field in §39.4.2 order, the seven-step block for `calculate_doe_main_effects`, the
two-movements framing, the decision-matrix and pilot-plan coaching, metric
literacy (§39.4.8), gate-readiness closing. **Authoritative during the refactor.**

> **Verify first — do not assume.** Whether `skills/dmaic-improve-phase/SKILL.md`
> already exists must be checked by listing the directory, not by a search miss
> (the Analyse SKILL.md existed when a search suggested it did not, 43c4201). If it
> exists, **restructure and conform, do not overwrite** sound content; if not,
> write it from this section.

## 39.4.11 Cross-phase reads and writes

**Reads from Analyse** (`store.get(("projects", case_id, "artifacts"), "analyse")`):
`root_cause_statement` (**what the solution must address**), `practical_significance`
(the size of the prize), `causal_hypothesis` and `phase_metrics` (the metric
linkage `solution_linked_to_root_cause` extends), `ruled_out_causes` (do not
re-propose a rejected cause's fix). Also reads Define's `metric_definitions` and
`target_value` (the pilot is measured against it).

**Writes**: the 9 content fields, `phase_metrics` (solution → metric, with pilot
effect), and `solution_linked_to_root_cause` (with `references_metric_name`).

**Hands to Control**: `selected_solution` (**what is now in place to hold**),
`pilot_result` and `implementation_plan` (the proven effect and how it was rolled
out), `phase_metrics` (which metrics moved, for Control's post-improvement
comparison).

## 39.4.12 The other phase

Control follows this same section shape and takes §39.5 at its own review.
**Define, Measure, Analyse and Improve are the ratified exemplars; Control remains
stubbed.**

---
---

# APPENDIX 2 — the Define `calculate_expected_savings` block (insert into §39.1.7 after the `target_value` block, and into the Define SKILL.md at the matching position)

**[TOOL · calculate_expected_savings · after target is set]**
> **Educate:** Now that we know where you are and where you're aiming, we can put a rough money figure on the prize. Expected savings translates the gap you're closing into an annual number — it's what earns the project its backing. Cutting errors from 12% to 3% on ~4,200 invoices a year, at about €30 to put each one right, is roughly €11k a year — before the knock-on effects.
> **Why now:** We do this once the baseline and target exist, so the figure rests on your numbers, not a guess — and it feeds straight back into your business case.
> **Prepare:** Four things, rough is fine: current level (we have it), target (we have it), roughly what one error costs, and how many you handle a year.
> **Run:** *(call `calculate_expected_savings`)*
> **Interpret:** About €11k a year, on €30 per error and 4,200 invoices. State those assumptions when you present it — a figure you can defend beats a bigger one you can't.
> **Visualise:** Usually unnecessary for one number; a simple before/after bar if it helps the case.
> **Coach next:** That anchors your business case. It's an estimate — Measure firms up the baseline, and the real saving lands in Control. Shall I fold it into your business-case summary?
