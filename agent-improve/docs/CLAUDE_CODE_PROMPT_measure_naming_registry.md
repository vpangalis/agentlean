# CLAUDE CODE PROMPT — Measure naming convention + structured metric registry + §39.2

*Self-contained. Paste this whole file into Claude Code. It needs no other
document. Founder-ratified 2026-08-26, AgentLean / Agent Improve phase-review
workstream. Workflow: you (Claude Code) execute the repo changes; verify with the
raw-grep discipline. Apply as ONE change set in the order below.*

**Supersession:** this STRUCTURED registry replaces the earlier Option-1
multi-criteria approach (metric names buried in prose strings). If that was
applied, reconcile toward this; if not, do not apply it. The §50 gate-document
paragraph (Step F) is still wanted.

---

## STEP A — Rename identifiers (repo-wide)

Two-tier acronym rule: spell out cryptic/local names, keep industry-standard
statistical terms. These are DISTINCT source strings — **no blind find-replace**
of `metric` / `baseline` / `kpi`. Do a raw `grep -rn` sweep (unfiltered — it must
see gitignored paths) and report the survivor list.

| Old | New |
|---|---|
| `process_kpis` (key in `process_map_sipoc`) | `process_metrics` |
| `baseline_kpis` (key in `detailed_process_map`) | `baseline_metrics` |
| `baseline_metric` (Define field) | `baseline_estimate` |
| `target_metric` (Define field) | `target_value` |
| `vital_few_xs` (Measure → Analyse) | `vital_few_drivers` |
| `xy_matrix_summary` (Measure) | `driver_priority_summary` |
| `post_improvement_metric` (Control) | `post_improvement_metrics` |

**MUST survive intact (do not touch):** `baseline_mean`, `baseline_sigma`,
`post_improvement_cpk`. Known sites: `ARCHITECTURE.md` §35, §39, §39.1, §40, §41,
§63.1–63.5, §69; `CLAUDE.md` §9.7, §10.8; `phases/*/schema.py`, `validate.py`,
and the Define cross-phase briefs read in analyse/improve/control. Sweep for
completeness — do not treat this list as exhaustive.

## STEP B — Computation-tool docstrings (NO renames)

All 20 computation-tool names STAY (`Cpk`, `DPMO`, `GR&R`, `RTY`, `FTQ`, `DOE`,
`I-MR`, `ANOVA` are the recognised terms). Only change: open each tool's
docstring with the plain concept then the standard term, e.g.
`"""Process capability (Cpk) — can the process meet spec as it runs today…"""`.

## STEP C — Structured metric registry + per-phase placeholder

**C1. `metric_definitions` — Define owns the registry.** Add to `DefineOutput`
(schema + §63.1) and the Define SKILL.md: a `list[dict]`, one entry per project
metric — `{name, unit, meaning}`. `name` is the stable traceability key, written
identically in every phase. This is the canonical "which metrics exist."

**C2. `phase_metrics` — uniform placeholder on ALL FIVE phase Outputs**
(schemas + §63.1–63.5). A `list[dict]`, one entry per registry metric the phase
engages, recording the state that phase produced. Measure example:

```
phase_metrics = [
  {name: "invoice_error_rate", unit: "%", baseline_mean: "12.3%",
   baseline_sigma: "2.6 sigma", stability: "stable", source: "measured"}
]
```

For Analyse / Improve (which act on drivers, not outcome values) the entry
records the linkage — which metric the cause / solution targets. A phase touching
no metric writes `"none this phase"`, never a silent gap. `metric_definitions`
and `phase_metrics` are a narrow FOURTH exception to §7's string law (same class
and reason as the three cross-phase reference dicts): the grader traces a metric
across phases by KEY EQUALITY on `name`. Scalar values inside stay strings.

## STEP D — Spec entries + counts (so §39.2's references resolve)

- New spec entry for `metric_definitions` — a registry/class entry in the §63
  (or §58) spec range, next free `S-C` id, with a field table and the
  key-equality invariant.
- Add `phase_metrics` to each of the five schema spec entries (§63.1–63.5).
  State that the §40 "same field on all five schemas" rule now binds THREE
  fields: `issues_and_barriers`, `secondary_metrics`, `phase_metrics`.
- §40 field-count tables: +1 per phase (Measure 14→15, and each of the others).
  Update the two-fields → three-fields note.
- §66 SPEC-GAP register: log `metric_definitions` and `phase_metrics` as
  resolved (they were dangling references until these entries existed); update
  the closed/open counts.

## STEP E — Write Measure §39.2 + update the §39 thread prose

- Replace the §39.2 stub in `ARCHITECTURE.md` with the full section in
  **APPENDIX 1** below (verbatim; it is an INDEX that references the cross-cutting
  specs and states only Measure specifics — do not copy those mechanisms in).
- Update §39's measurement-thread prose to the new names:
  `process_metrics` (planned) → `baseline_metrics` (before) →
  `post_improvement_metrics` (after).
- Leave §39.3–39.5 (Analyse / Improve / Control) as stubs — same treatment at
  their own reviews.

## STEP F — SKILL.md metric-literacy + gate-document parity

- **Metric-literacy requirement** into §32 (SKILL.md required content) and §43
  (coaching method): for each metric in play, the coach explains what the metric
  IS, why it matters in the phase, and how to read a good/bad value — distinct
  from the seven-step tool education. Apply it in full to
  `skills/dmaic-measure-phase/SKILL.md` now; the other four SKILL.md inherit at
  their reviews.
- **§50 gate-document paragraph** — add to §50 "The live gate document": every
  phase's live gate document renders `computation_results` inline, grouped by
  `phase_metrics` `name` when more than one metric is tracked, each with its
  interpretation (not raw numbers — §43.1 step 5) and its chart via
  `propose_diagram`; the narrative assembles from captured field text +
  `computation_results` + `phase_metrics`, NEVER from `CoachingResponse`
  turn-level fields (`explanation`/`example`/`prompt`/`progress`, §50.1, WATCH 9).
  Requirement on every phase's SKILL.md; back-apply the layout section to
  Define's SKILL.md.

## VERIFY AND REPORT

1. Raw `grep -rn` shows no stale identifier from Step A; `baseline_mean` /
   `baseline_sigma` / `post_improvement_cpk` intact.
2. No `phases/*/schema.py` value field changed type EXCEPT the two new structured
   additions (`metric_definitions`, `phase_metrics`).
3. §40 counts reconcile with the five schema entries (each +1).
4. Every field, tool, state field and condition named in §39.2 resolves to an
   existing spec entry — no dangling reference (this is the gap-catch).
5. `metric_definitions` and `phase_metrics` each have a spec entry; §66 counts
   updated.
6. Commit body: what changed, where, why. Note the `885defc`-era naming fully
   superseded and the Option-1 multi-criteria approach replaced by the structured
   registry.

---
---

# APPENDIX 1 — §39.2 verbatim (write this into ARCHITECTURE.md, replacing the stub)

## 39.2 Measure phase, complete specification

*Per-phase HUB: indexes the cross-cutting specs (state §6/§58.2, graph/routing
§13–16, gate §33–38, tiers §35, tools §30/§69, dicts §41, gate doc §50) and
records only what is Measure-specific. Define-once holds — nothing here
re-defines a mechanism that lives in a concern Part.*

### 39.2.1 Purpose

Measure establishes what is actually happening and proves the numbers can be
trusted before anyone acts on them. It opens on Define's contract, expands the
high-level SIPOC into an operational process map, decides what to collect and
how, validates the measurement itself, confirms the process is stable, and only
then fixes a baseline — leaving the Belt with a trustworthy baseline and the
vital few drivers Analyse will test.

### 39.2.2 The ordered field list — the `field_index` sequence

The order the planner walks (`field_index` indexes into it). Coached in
**methodology order, not tier order** — the inversion at 3–4 is deliberate
(§39.2.6). Schema: **§63.2 — S-C28** (canonical home).

| # | Field (`artifacts` key) | Type | Tier | Note |
|---|---|---|---|---|
| 1 | `detailed_process_map` | `dict` | 1 | Six sub-fields (§41). Everything attaches to it |
| 2 | `data_collection_plan` | `str` | 1 | Flows from the map's measurement points |
| 3 | `measurement_system_validated` | `str` | 2 | MSA. **Offered before the baseline** (§39.2.6) |
| 4 | `stability_assessment` | `str` | 1 | Run-chart read. **Before capability** (§39.2.6) |
| 5 | `baseline_mean` | `str` | 1 | The measured central value; supersedes Define's `baseline_estimate` |
| 6 | `baseline_sigma` | `str` | 2 | Spread / sigma level |
| 7 | `driver_priority_summary` | `str` | 1 | *(was `xy_matrix_summary`)* — scored prioritisation of candidate drivers |
| 8 | `vital_few_drivers` | `str` | 1 | *(was `vital_few_xs`)* — ranked shortlist Analyse consumes |
| 9 | `secondary_metrics` | `str` | 2 | Carried from Define, re-checked |
| 10 | `issues_and_barriers` | `str` | 1 | Ask once collection has been attempted |

`MeasureOutput` = these ten **+** `phase_metrics` (§39.2.3) **+** four
gate-metadata fields = **15** (was 14; §40's count rises by `phase_metrics`).
7 Tier 1, 3 Tier 2.

### 39.2.3 The metric registry and Measure's placeholder (structured)

**The registry is Define's** (`metric_definitions`, §39.1): the canonical set of
project metrics, each `{name, unit, meaning}`. `name` is the traceability key,
identical in every phase.

**Measure's placeholder is `phase_metrics`** — a `list[dict]`, one entry per
registry metric this phase measured:

```
phase_metrics = [
  {name: "invoice_error_rate", unit: "%",
   baseline_mean: "12.3%", baseline_sigma: "2.6 sigma",
   stability: "stable (2 special causes excluded)", source: "measured"},
  {name: "invoice_cycle_time", unit: "days",
   baseline_mean: "2.6 days", baseline_sigma: "—", stability: "stable",
   source: "measured"}
]
```

Structured registry (founder ruling 2026-08-26): a narrow, justified fourth
exception to §7's string law, same class and reason as the three cross-phase
reference dicts — the grader traces a metric across phases by **key equality on
`name`**, not by reading prose. Scalar values inside stay strings.
`detailed_process_map["baseline_metrics"]` *(was `baseline_kpis`)* captures the
before-values in the map, per step; `phase_metrics` is the phase-level roll-up
the next phase reads. Multi-criteria falls out: one entry per metric, tools run
once per entry (`name` in `computation_results.inputs`, §69). Scan `phase_metrics`
across the five gate documents and a metric's whole journey is one keyed trail.

### 39.2.4 SIPOC → the detailed process map (Measure's structured-capture handling)

*Parallel to Define's §39.1.5 SIPOC handling.* Measure does not build a SIPOC —
it **expands Define's** into an operational map. `detailed_process_map` is a
`dict`, six sub-fields (§41, S-C33): `steps`, `cycle_times`, `resources`,
`value_vs_waste`, `measurement_points`, `baseline_metrics`. **No computation
tool** — structured capture, nothing to calculate.

- **Reads** Define's `process_map_sipoc` first and opens the phase on it
  (§39.2.11). The detailed map must **decompose that same SIPOC**, not describe a
  different process, and must **stay inside `project_scope`** — the grader flags a
  map that adds steps Define scoped out (§41).
- **Show then build:** a completed example first, then the Belt's own,
  step-by-step (never all six sub-fields at once). Waiting and rework are their
  own rows — that is where the hidden time and the hidden factory live.
- **`baseline_metrics` connects to Define's `process_metrics`** — the same
  measurement points, now carrying before-values (the measurement thread, §39).
- Visual rendering routes through `propose_diagram` (§29); a partial map missing
  any sub-field is the failure §41 describes.

### 39.2.5 Tools bound to Measure

Passed to the executor via `tools=` on `create_agent` (§18); from the subgraph's
view the executor is one node (§13). **Fifteen — the phase maximum**, under the
16 cap (§30).

- **The universal seven** (§29.2), on every phase: `rag_lookup_methodology`,
  `rag_lookup_evidence`, `rag_lookup_case_history`, `propose_template`,
  `propose_diagram`, `check_gate_status`, `request_human_approval`.
- **Eight computation tools** (§30 binding; specified §69, S-F38–S-F45),
  standard statistical names kept (two-tier acronym rule), plain-concept-then-
  standard-term docstrings:

| Job | Tools | Serves |
|---|---|---|
| Size the sample | `calculate_sample_size_proportion`, `calculate_sample_size_mean` | `data_collection_plan` |
| Trust the gauge | `calculate_grr` | `measurement_system_validated` (lock 1) |
| Characterise the baseline | `calculate_sigma_level`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq` | `baseline_mean` / `baseline_sigma` |
| Prove capability | `calculate_cpk` | capability (lock 2, after stability) |

Each runs under the seven-step pattern (§43.1). The SKILL.md `allowed-tools`
MUST match this exact subset (§32) — skill/tool drift produces a coach that
promises a tool it was not given.

### 39.2.6 Conditions — sequence locks, routing, and the gate

**Two methodology sequence locks** (coaching-order conditions; a number produced
out of order looks authoritative while being wrong):

1. **Validate before you trust** — `measurement_system_validated` (`calculate_grr`)
   is coached at position 3, **before** the baseline at 5. Enforced by coaching
   order + the rubric. A baseline off an unvalidated gauge measures the people.
2. **Stability before capability** — `stability_assessment` (4) is established
   **before** `calculate_cpk` may run. Enforced as a **tool precondition** — the
   tool's precondition is `stability == "stable"` (§69, S-C28 B1) — not merely a
   convention.

**Routing conditions** — Measure's subgraph is the five-node cycle (§13), routed
by `Command`, not conditional edges (§15). Nothing Measure-specific in the
topology; the conditions that fire:

| Where | Condition | Goes to |
|---|---|---|
| `planner` (S-F13 DP1) | current field incomplete, or more fields remain | `executor` (`field_index++`) |
| `planner` | all 10 captured | `validation_stack` |
| `validation_stack` | 2b presence of the **7 Tier 1** + 2d `MEASURE_RUBRIC` pass | `gate_review` |
| `validation_stack` | fail | `planner` (+ `validator_feedback`); `gate_attempts ≥ 3` → escalation (§38) |
| `gate_apply` | Belt approve / reject | `END` / `planner` (+ `rejection_feedback`) |

**Gate-pass condition:** the 7 Tier 1 fields present and the rubric clears; the 3
Tier 2 fields warn only, a skip recorded in `acknowledged_gaps` (§35). Each phase
runs its own validation loop with its own budget of 3 (`gate_attempts` is per
phase, §6).

### 39.2.7 State parameters (`MeasureState`)

*Indexes §6 / §58.2 — S-C02; nothing re-defined.* `MeasureState` extends
`PhaseState` — explicit `TypedDict`, not `MessagesState` (§6). All 21 declared
`PhaseState` fields apply; the Measure-specific reads/writes:

| PhaseState field | In Measure |
|---|---|
| `artifacts` | holds the 10 captured fields **+ `phase_metrics` + `computation_results`**; the planner reads it to derive what is next (there is no queue) |
| `field_index` | walks the §39.2.2 list (0–9); distinct from `phase_index` (§6) |
| `gate_attempts` | Measure's own retry counter, cap 3 → escalation; reset on pass |
| `validator_feedback` | accumulates across the ≤3 validation retries; the coach reads the full list |
| `citations` / `uploads` | the evidence trail — Measure is the heaviest upload phase (error logs, time studies, GR&R sheets); both land in the gate document |
| `computation_results` | every tool run (§7 shape); the grader scans it for tool evidence, not prose |
| `hop_results` / `synthesis_output` | declared but `[]`/`None` on Measure's typically single-hop turns (multi-hop is mainly Analyse, §26) — present because `CoachingPlan.retrieval_strategy` may select `multi_hop` in any phase |
| `draft` / `belt_edits` / `final` | `dict`, never `str` (§6); `final` is the assembled gate document |

Any new Measure state field requires an amendment (§6, §56).

### 39.2.8 Metric literacy — what each metric means (coaching requirement)

New requirement (amendment §4), Measure instance. The coach teaches **two
distinct things**, and must not conflate them:

- **The metric** (the business KPI — `invoice_error_rate`): what it is, why it
  matters in Measure, how to read a good baseline. Fires when the metric is
  first measured, echoing its Define `meaning`. *"Error rate is the share of
  invoices sent back for correction — your primary problem metric. A baseline
  worth trusting is a stable, validated number with its sample and period
  stated."*
- **The statistic** (`mean`, `sigma`, `Cpk`, `DPMO`, `RTY`, `FTQ`, `Gage R&R`):
  the seven-step *educate* step (§43.1 step 1) — what the number means before it
  is produced.

Plain language (§50); surfaced through `CoachingResponse.explanation` (§50.1).

### 39.2.9 Gate, storage, progress view

- **Seven Tier 1 fields block** the gate (§35). Three Tier 2 warn only.
- **The live gate document** (§50) renders `detailed_process_map` and
  `driver_priority_summary` as tables, `vital_few_drivers` as a numbered list,
  and `computation_results` inline with interpretation and charts (via
  `propose_diagram`), grouped by `phase_metrics` `name` when several metrics run.
  Narrative assembles from captured field text + `computation_results` +
  `phase_metrics` — never from `CoachingResponse` turn fields (§50, WATCH 9).
- **Two progress bars**, Tier 1 and Tier 2 (Measure has both tiers — unlike
  Define's single bar).
- Written **once** to `store/projects/{case_id}/artifacts/measure.json` by
  `gate_apply` (§9, §33).

### 39.2.10 The SKILL.md content

`skills/dmaic-measure-phase/SKILL.md` is generated from this section and must
match. **Authoritative during the refactor** (as §39.1.7 for Define): on
conflict this section wins until the refactor completes, then authority flips to
the code file. The SKILL.md carries the A→F session flow, the Define-recap
opening, the seven-step sequence per tool, a worked example per field, the
metric-literacy explanations (§39.2.8), the Document Layout, and the
contradiction-check instruction (§32).

### 39.2.11 Cross-phase reads and writes

**Reads from Define** (`store.get(("projects", case_id, "artifacts"), "define")`):
`metric_definitions` (registry), `process_map_sipoc["process_metrics"]`,
`baseline_estimate` (anchor; flag drift into `baseline_mean`), `target_value`,
`project_scope` (bounds the map), `problem_statement` (re-test), `voc_summary`
(spec limits for `calculate_cpk`), `secondary_metrics`, `issues_and_barriers`.

**Writes**: `detailed_process_map["baseline_metrics"]`, `phase_metrics`,
`baseline_mean`, `baseline_sigma`, `driver_priority_summary`, `vital_few_drivers`.

**Hands to Analyse**: `vital_few_drivers` (the starting list),
`driver_priority_summary` (how it was derived), `baseline_mean` and
`phase_metrics` (the values `causal_hypothesis` references),
`measurement_system_validated` and `stability_assessment` (preconditions).
