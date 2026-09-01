# Measure Phase-Review Closure + Computation-Tools Spec (Draft for Ratification)

*Drafted 2026-08-26, in the phase-review workstream (`CONTINUITY.md` §5).
Sources read live via OneDrive: `agent-improve/docs/CONTINUITY.md` v4.1,
`agent-improve/ARCHITECTURE.md` (local copy, §7, §30, §35, §39, §40, §41, §60.6,
§63.1–§63.7), `AGENTIC_ARCHITECTURE_REFERENCE.md` v1.7.2 §30, and
`agent-improve/skills/dmaic-measure-phase/SKILL.md` v0.2-draft. This is prose
for founder ratification — not an implementation prompt. Nothing here has been
written back to OneDrive (read-only through the connector); once ratified, an
intent brief goes to Claude Code.*

---

## Part A — Measure capture review, closed against the five-point bar

### 1. Field list — final

Confirmed final. `MeasureOutput` (§63.2, S-C28): 14 fields — 7 Tier 1, 3 Tier 2,
4 gate metadata. Matches `dmaic-measure-phase/SKILL.md` §2's ten coached
fields (gate metadata is assembled, not coached). No field additions,
removals, or type changes are needed. Coached order, with the tier inversion
already correctly designed (MSA before the baseline, methodology order over
tier order):

| # | Field | Tier | Type | Why here |
|---|---|---|---|---|
| 1 | `detailed_process_map` | 1 | `dict` (6 sub-fields) | Everything attaches to it |
| 2 | `data_collection_plan` | 1 | `str` | Flows from the map's measurement points |
| 3 | `measurement_system_validated` | 2 | `str` | **Offered here, before the baseline** — see §2 below |
| 4 | `stability_assessment` | 1 | `str` | Before capability — an unstable process has no single capability figure |
| 5 | `baseline_mean` | 1 | `str` | Only trustworthy once 3–4 are done |
| 6 | `baseline_sigma` | 2 | `str` | Falls out of the baseline and spec limits |
| 7 | `xy_matrix_summary` | 1 | `str` | Prioritise inputs using the map |
| 8 | `vital_few_xs` | 1 | `str` | The ranked result Analyse consumes |
| 9 | `secondary_metrics` | 2 | `str` | Carried from Define, re-checked |
| 10 | `issues_and_barriers` | 1 | `str` | Always last; ask once collection's been attempted |

### 2. The three files — one real disagreement, now resolved

**Rename, `baseline` → `baseline_metric` (ratified 2026-08-26, CONTINUITY §5).**
`schema.py`/SKILL.md-facing prose already anticipates the new name — the
SKILL.md's own §10 cross-phase-reads table already reads `baseline_metric`.
**`ARCHITECTURE.md` is the file that lags**: §39.1.2 (Define's field #5),
§39 (measurement-thread prose), §35's Define gate-required-fields row, and
§63.1 (S-C27 `DefineOutput`) all still say `baseline`. This is exactly the
"owed" item CONTINUITY names for Define's finalization — Measure's side of
it is already consistent and needs no separate edit once Define's rename
lands. **No new decision required here — flagging it closes the cross-check,
the fix itself is Define's, already scheped.**

**A real internal contradiction in `dmaic-measure-phase/SKILL.md`, not yet
flagged elsewhere.** §1 Sections A and E describe strict two-block coaching —
"Required (7)" then, only once all seven are done, "Tier 1 complete, Tier 2
offered" for the three recommended fields. But §2's field order interleaves
Tier 2 at position 3 (`measurement_system_validated`, before four Tier-1
fields) and position 6 (`baseline_sigma`, before three more) — and §2 says
outright "sequence follows methodology, not tier." The opening checklist and
closing "Tier 2 offered" framing describe a flow the field order doesn't
follow. A coach built from the SKILL.md as currently worded doesn't know
which section governs.

**Proposed resolution (ratify or amend):** the field-order table is correct —
methodology sequencing is the right call for Measure specifically because
`measurement_system_validated`'s whole point is gating trust in the data that
everything after it depends on. Section A's opening and Section E close
should stop implying two coaching blocks. Concretely:

- Section A's checklist keeps the Required/Recommended split for *display*
  (it's a legitimate gate-status view), but the closing line changes from
  "We start by expanding your Define map" to something that doesn't imply a
  strict block order — e.g. *"We'll work through these roughly in this order,
  and I'll flag the two recommended ones ([Measurement system check],
  [Sigma level]) when we get to them rather than saving them for the end."*
- Section E is repurposed from "offer the three Tier 2 fields now" to a
  **genuine final check on whatever the Belt actually deferred** — if the
  Belt already did `measurement_system_validated` at position 3 and
  `baseline_sigma` at position 6, Section E has nothing left to offer except
  `secondary_metrics` (position 9, already in the main walk) and should say
  so, rather than re-listing all three as if untouched. Section E becomes:
  *"list only the Tier 2 fields still absent from `artifacts` at this point,
  offer each once, record a decline as an `acknowledged_gaps` entry."*

This is the one change this review makes to the SKILL.md's substance; it's a
wording/flow fix, not a field or tier change, so it doesn't reopen the
five-point bar's item 1.

### 3. MSA coached-as-an-option — ratified framing

CONTINUITY §5: MSA stays Tier 2 (optional) but must be **actively offered and
explained**, never silently skipped. The SKILL.md's position-3 placement and
its coaching content (§3, `measurement_system_validated`) already do the
"explain, then ask" part correctly — the explanation is genuinely good
(scale/weighing analogy, %study-variation thresholds, "point at the
definition, not the people"). What was missing was the explicit **choice**:
nothing in the current text tells the Belt they *can* decline. Add one line
to the per-field block, after the existing "Ask":

> *"This one's optional, but I'd recommend it — if you'd rather skip it and
> come back later, that's fine too; just say so and we'll note it and move to
> the baseline."*

A decline routes to `acknowledged_gaps` immediately (not deferred to Section
E, which per §2 above now only sweeps whatever's still outstanding).

### 4. Define-recap opening — ratified requirement, not yet implemented

CONTINUITY §5: Measure's SKILL.md "opens with a DEFINE RECAP — show the Belt
the key Define parameters/decisions (problem, baseline_metric, target, SIPOC,
process KPIs), then a guideline of what to measure, showing all options."
**Section A as currently drafted does not do this** — it opens directly on
Measure's own checklist and only gestures at Define with one line ("Define
agreed what the problem is"). This is the one genuine gap against the
ratified ruling. Replacement opening (Section A):

> *"Welcome to Measure. Quick recap of what Define locked in, so we're
> building on the same picture:*
> *• Problem: {problem_statement}*
> *• Baseline: {baseline_metric}*
> *• Target: {target_metric} by {target_date}*
> *• Process (SIPOC): {process_map_sipoc — rendered as the table}, measuring
> {process_map_sipoc['process_kpis']}*
>
> *Now, what Measure actually does: we expand that SIPOC into a detailed
> process map, decide what to collect and how, check the measurement itself
> can be trusted, confirm the process is behaving consistently, establish a
> real baseline, and prioritise which inputs are most likely driving the
> problem. You don't need to do these in a fixed order in your head — I'll
> guide you — but here's the full menu so nothing's a surprise:*
> *[— required/recommended checklist, as currently written —]"*

This pulls the four named values from `store.get(("projects", case_id,
"artifacts"), "define")` — the same read the SKILL.md's own §10 already
specifies, just moved to fire once at phase open rather than only as
scattered per-field cross-checks.

### 5. Cross-phase reads — already named, confirmed consistent

SKILL.md §10 names both directions correctly (Define reads in, Analyse reads
out) and needs no change beyond the rename in §2 above. No new cross-phase
dependency surfaced by this review.

### 6. Mechanics — deferred to Part B, not a Measure-specific gap

Backbone mechanics (checkpointing, static routing) were verified once,
horizontally, for all five phases (CONTINUITY §5) — nothing Measure-specific
to re-check there. What *is* unverified is the eight computation tools' own
interfaces, which is a pre-existing platform-level gap (G-25, below), not
something this phase review introduces.

### Verdict

**Measure meets the five-point bar once the three wording changes in §§2–4
above are applied** (SKILL.md only — no schema or tier change). No founder
ruling is needed on the field set or tiers; the MSA-as-option and
Define-recap items are wording implementations of rulings already made. The
SKILL.md-vs-narrative contradiction in §2 is new information from this
review and is worth a one-line founder nod before Claude Code applies it,
since it touches coaching flow rather than pure prose.

### Measure's named computation requirements

Confirmed against `AGENTIC_ARCHITECTURE_REFERENCE.md` §30/§60.6 (root,
platform-canonical) and the SKILL.md's own §4 — the two already agree:

`calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`,
`calculate_yield_rty`, `calculate_ftq`, `calculate_grr`,
`calculate_sample_size_proportion`, `calculate_sample_size_mean` — **8
tools**, all Six Sigma statistics, all currently unspecified below the name
(SPEC-GAP G-25). Part B closes that gap for these 8 and the other 12.

**One boundary worth stating explicitly so it isn't rediscovered as a
"missing tool" later:** `stability_assessment` (Measure, Tier 1) is coached
as a **visual, qualitative** run-chart read — "plot it, tell me what you
see" — with no calculated control limits. Neither `xbar_r_chart_limits` nor
`imr_chart_limits` is bound to Measure (§30's Measure list has no
chart-limit tool), and Measure already sits at 15 of 16 tools, so adding one
would hit the ceiling and needs its own amendment. Formal control-chart math
(UCL/LCL) is Control-only, via `xbar_r_chart_limits` / `imr_chart_limits` /
`p_chart_limits` / `c_chart_limits`. This is consistent with the existing
worked example in the SKILL.md, which reads a run chart by eye ("ran between
10–14% except two weeks") rather than citing a calculated limit — so this is
a clarifying note, not a change.

---

## Part B — Computation-tools specification (new architecture section, resolves SPEC-GAP G-25)

**Container decision, applying CONTINUITY §5's ruling:** this is a standalone
subsystem spec, not embedded in any phase's section. Proposed home:
`agent-improve/ARCHITECTURE.md`, new **§69 "Spec — computation tools"**,
immediately following the existing `§63–§68` "Spec —" run (§63 DMAIC gate
documents, §64 reliability, §65 API/UI/evidence, §66 SPEC-GAP register, §67
EU AI Act, §68 DORA register) — new content is appended after §68 rather than
interleaved, so no existing section renumbers. Spec IDs continue the existing
sequence: **S-F37 through S-F56** (the document's S-F run currently ends at
S-F36; S-C currently ends at S-C37 and none of these need a class ID, since
every entry is a pure function). This closes out §60.6's **S-F24** group
entry (which stays, now pointing at these 20 as its detail) and resolves
**G-25** in the §66 register.

**Common conventions, stated once rather than 20 times (per §7 and §40's own
style):**

- **File:** `knowledge/computation.py`. **Procedure:** step 5.3.
- Every tool is a separate `@tool` with `args_schema=` from
  `knowledge/tool_args.py` (§31) — no mode-argument grouping (§30 B4).
- **Inputs**, below, are the *semantic* values the tool needs. Per §7, every
  captured field arrives as a `str`; each tool parses what it needs from the
  string(s) it's given and — per B3 — returns a clear reformatting request
  rather than raising or guessing when it can't.
- **Output shape**, below, lists the keys of the `result` sub-dict inside the
  `computation_results` entry (§7's shape: `{"tool", "inputs", "result",
  "turn", "phase"}`). **Every value in `result` is a string**, per the field
  typing law — a numeric like `cpk: 0.62` is stored as `"result":
  {"cpk": "0.62", ...}`.
- **Preconditions** are business/methodology preconditions (what must be true
  of the project state before the tool should be called) — not argument
  validation, which is ordinary parsing (B2/B3).
- **Trusted-source basis:** unlike LangGraph/LangChain patterns, these
  formulas are stable, decades-old Six Sigma / applied-statistics standards
  (AIAG MSA-4 for GR&R, Shewhart control-chart constant tables, standard
  hypothesis-test and OLS formulas, the 1.5σ long-term shift convention for
  sigma-level). They don't drift the way a package API does, so the Standing
  Reasoning Protocol's trusted-source check here is "matches the standard
  method, as taught in the ingested BB eBook (`rag_lookup_methodology`)" —
  cited per tool below — rather than a web-search-verified library call.

### B1. Define (1 tool)

| S-F | Tool | What it computes | Inputs | Output (`result` keys) | Preconditions |
|---|---|---|---|---|---|
| S-F37 | `calculate_expected_savings` | Projected annualised financial benefit of closing baseline→target gap | `baseline_value`, `target_value`, `unit_cost` (cost per defect/unit of the gap), `annual_volume` | `annual_savings`, `currency`, `calculation_note` (states the multiplication used, since a Belt must be able to defend it at the gate) | `baseline_metric` and `target_metric` captured (Define #5, #8); `business_case` gives the cost basis where the Belt has one — tool must accept an absent cost and return a reformatting request rather than inventing a unit cost |

### B2. Measure (8 tools)

| S-F | Tool | What it computes | Inputs | Output (`result` keys) | Preconditions |
|---|---|---|---|---|---|
| S-F38 | `calculate_sigma_level` | Defect rate → sigma level, long-term (1.5σ shift convention) | `defects`, `units`, `opportunities_per_unit` (or `dpmo` directly) | `sigma_level`, `dpmo`, `shift_assumption` (states "1.5σ long-term shift applied") | None beyond a parseable defect count |
| S-F39 | `calculate_cpk` | Process capability against one or two spec limits | `mean`, `std_dev`, `usl` (optional), `lsl` (optional) | `cpk`, `cp` (only if both limits given), `binding_limit` (which side is closer — the centring-vs-spread read) | **Hard: `stability_assessment` must read "stable"** (§63.2 B1) — a `calculate_cpk` call timestamped before a stable verdict is a grading flag (§35, §41), not just a style note |
| S-F40 | `calculate_dpmo` | Defects per million opportunities | `defects`, `units`, `opportunities_per_unit` | `dpmo` | None |
| S-F41 | `calculate_yield_rty` | Rolled throughput yield across process steps | `step_yields` (list) **or** `step_units_and_defects` (list of pairs) | `rty`, `simple_average_yield` (for contrast), `hidden_factory_gap` (the difference — the number that makes RTY's point) | `detailed_process_map` steps populated with at least 2 steps |
| S-F42 | `calculate_ftq` | First-time quality at one step | `units_processed`, `units_reworked_or_defective` | `ftq` | The step is identified in `detailed_process_map` |
| S-F43 | `calculate_grr` | Measurement system variation — Gage R&R (variable) or attribute agreement | `data_type` (`variable`/`attribute`); variable: `readings` (operators × parts × trials matrix); attribute: `agreement_matrix` (operator ratings per part per trial) | `pct_study_variation` (variable) or `pct_agreement` (attribute); `repeatability_pct`, `reproducibility_pct`; `verdict` (`acceptable` <10%, `marginal` 10–30%, `unacceptable` >30% — AIAG MSA-4 bands) | None — this precedes the baseline by design |
| S-F44 | `calculate_sample_size_proportion` | Required sample size to estimate a proportion within a margin | `expected_proportion`, `margin_of_error`, `confidence_level` (default 0.95) | `required_n` | None |
| S-F45 | `calculate_sample_size_mean` | Required sample size to detect a difference in a mean | `estimated_std_dev`, `detectable_difference`, `confidence_level` (default 0.95), `power` (default 0.80) | `required_n` | None |

### B3. Analyse (5 tools)

| S-F | Tool | What it computes | Inputs | Output (`result` keys) | Preconditions |
|---|---|---|---|---|---|
| S-F46 | `t_test` | Compares two sample means (Welch's by default; equal-variance if the Belt states it) | `sample1`, `sample2` (raw values or `{mean, std_dev, n}` summaries), `paired` (bool) | `t_statistic`, `degrees_of_freedom`, `p_value`, `significant` (`"yes"`/`"no"` at α=0.05) | One of `vital_few_xs` names the factor under test |
| S-F47 | `chi_square_test` | Association between two categorical variables | `contingency_table` (rows × columns of counts) | `chi_square_statistic`, `degrees_of_freedom`, `p_value`, `significant` | Categorical data for both variables; expected cell counts ≥5 (tool returns a reformatting/small-sample warning otherwise, per B3) |
| S-F48 | `anova` | Compares means across 3+ groups | `groups` (list of raw-value lists or summaries) | `f_statistic`, `df_between`, `df_within`, `p_value`, `significant` | At least 3 groups |
| S-F49 | `pearson_correlation` | Linear correlation strength, two continuous variables | `x_values`, `y_values` (paired) | `r`, `r_squared`, `p_value`, `strength_label` (negligible/weak/moderate/strong, standard |r| bands) | Paired continuous data, n ≥ 10 (methodology floor — smaller returns a warning, not a suppressed result) |
| S-F50 | `linear_regression` | Fits Y = a + bX (simple OLS) | `x_values`, `y_values` (paired) | `slope`, `intercept`, `r_squared`, `equation_string`, `p_value` | Same as `pearson_correlation`; typically run after it, on the same pair |

### B4. Improve (1 tool)

| S-F | Tool | What it computes | Inputs | Output (`result` keys) | Preconditions |
|---|---|---|---|---|---|
| S-F51 | `calculate_doe_main_effects` | Main effect of each factor from a factorial experiment | `factors` (names + the two levels each ran at), `design_matrix` (which level each factor was at, per run), `responses` (measured output per run) | `main_effects` (per-factor effect size), `ranked_factors` (largest effect first) | `experiment_justification` records that a DOE (not "simplified" or "none") was chosen (§63.4 B1) |

### B5. Control (5 tools)

| S-F | Tool | What it computes | Inputs | Output (`result` keys) | Preconditions |
|---|---|---|---|---|---|
| S-F52 | `xbar_r_chart_limits` | Control limits for subgrouped variable data | `subgroups` (list of equal-size value-lists) | `x_bar_bar` (centre line), `ucl_x`, `lcl_x`, `r_bar`, `ucl_r`, `lcl_r` | Subgroup size ≥ 2, constant across subgroups (standard A2/D3/D4 constants by subgroup size) |
| S-F53 | `imr_chart_limits` | Control limits for one measurement per period | `values` (single time series) | `x_bar` (centre line), `ucl_i`, `lcl_i`, `mr_bar`, `ucl_mr` | **The default choice** whenever data is one-per-period — do not coach the Belt into inventing subgroups to force `xbar_r_chart_limits` (§30 B7) |
| S-F54 | `p_chart_limits` | Control limits for proportion defective, variable subgroup size | `subgroups` (list of `{defectives, n}`) | `p_bar`, `ucl_note` (limits vary per subgroup by `n` — returns the formula plus the per-subgroup array, not one flat number) | Attribute (pass/fail) data |
| S-F55 | `c_chart_limits` | Control limits for defect counts per unit, constant opportunity | `counts` (defect count per unit/period) | `c_bar`, `ucl`, `lcl` | Constant area of opportunity across periods |
| S-F56 | `post_improvement_cpk` | Process capability on post-improvement data, compared to the baseline | `mean`, `std_dev`, `usl`/`lsl`, `baseline_cpk` (for the comparison) | `cpk`, `improvement_delta` (vs `baseline_cpk`), `meets_target` (`"yes"`/`"no"`) | Control's stability re-check passes first (same stability-before-capability rule as `calculate_cpk`, §41) — **same formula as `calculate_cpk`, kept as a separately-bound, separately-named tool per §30's per-phase-binding and no-mode-argument rules; the two MAY share a private helper, but are two `@tool`s** |

### Register update (for whoever applies this)

- §66 SPEC-GAP register: **G-25 → closeable** once §69 lands (currently 9
  closed / 35 open).
- §60.6 (S-F24, the existing 20-tool group entry): update its "Rebuild test"
  line from *"not met — the inventory is complete, the interfaces are
  absent"* to *"met — see §69"*, and point its Architecture reference at §69.
- No change to §30 (root reference) or the SKILL.md tool lists — names and
  per-phase binding were already correct; this only adds the interfaces
  underneath them.
