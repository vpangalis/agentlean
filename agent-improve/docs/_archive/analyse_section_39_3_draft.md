# §39.3 — Analyse phase, complete specification (DRAFT for ratification)

*Drafted 2026-08-26 to the §39.2 (Measure) template, in the new naming
convention and the structured metric registry. For `agent-improve/
ARCHITECTURE.md` Part VIII, replacing the §39.3 stub. Per-phase HUB: indexes the
cross-cutting specs (state §6/§58.2, graph/routing §13–16, gate §33–38, tiers
§35, tools §30/§69, multi-hop §26, cross-phase refs §7/§42, gate doc §50) and
records only what is Analyse-specific. Define-once holds.*

*Grounded against current LSS practice: iSixSigma / sixsigmastudyguide Analyze
phase, 6sigma.us DMAIC tools, Lean6Sigma Hub root-cause techniques (2026).*

---

## 39.3.1 Purpose

Analyse takes the vital few drivers Measure prioritised and finds — and proves —
which of them actually cause the problem. It has two distinct movements:
**generate** candidate root causes (qualitative — fishbone, 5 Whys, Pareto), then
**validate** them against the data (hypothesis tests, ANOVA, regression). It ends
with a specific, evidence-backed root cause and an honest statement of how much
of the problem that cause explains — the input Improve needs before it designs a
fix.

## 39.3.2 The ordered field list — the `field_index` sequence

Coached in **methodology order** — frame, generate, validate, confirm, quantify,
socialise. Schema: **§63.3 — S-C29** (canonical home).

| # | Field (`artifacts` key) | Type | Tier | Note |
|---|---|---|---|---|
| 1 | `statistical_problem_statement` | `str` | 2 | Translate the practical problem into a testable statistical question. All Belts, in Analyse — not Define |
| 2 | `causal_hypothesis` | `dict` | 2 | Candidate cause(s), generated (fishbone/5-Whys), linked to the metric being explained (§39.3.3) |
| 3 | `root_cause_validation` | `str` | 1 | Statistical or observational evidence the cause is real |
| 4 | `ruled_out_causes` | `str` | 2 | Alternatives tested and rejected, with rationale |
| 5 | `root_cause_statement` | `str` | 1 | The confirmed, specific, actionable root cause |
| 6 | `practical_significance` | `str` | 1 | How much of the problem it explains — the eBook's second gate |
| 7 | `process_owner_buyin` | `str` | 2 | The owner accepts the root cause |
| 8 | `secondary_metrics` | `str` | 2 | Carried from Measure, re-checked |
| 9 | `issues_and_barriers` | `str` | 1 | Always last |

`AnalyseOutput` = these nine **+** `phase_metrics` (§39.3.3) **+** four
gate-metadata fields = **14**. 4 Tier 1, 5 Tier 2.

**Note the generate-before-validate ordering** (2 before 3). A hypothesis is
generated qualitatively, then tested. `root_cause_statement` (5) lands *after*
validation (3) and ruling-out (4) — you state the cause once, once it is proven,
not as an opening guess refined in place.

## 39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13)

Analyse holds no *measured* metric value — Measure did that. Its `phase_metrics`
entry records the **linkage**: which root cause explains which registry metric.

```
phase_metrics = [
  {name: "invoice_error_rate", explained_by: "root cause: onboarding gap in first 60 days",
   share_explained: "≈70% (practical_significance)", source: "linkage"},
  {name: "invoice_cycle_time", explained_by: "not addressed this phase", source: "linkage"}
]
```

A metric Analyse does not address writes `"not addressed this phase"`, never a
silent absence. This keeps the keyed trail unbroken through a phase that acts on
drivers rather than outcome values.

**`causal_hypothesis` names the metric it explains.** Its reference dict
(§63.6 / S-C32) gains `references_metric_name` so a multi-metric project links a
hypothesis to a *specific* Y, not just "the baseline":

```
causal_hypothesis = {
    "hypothesis":          "Inadequate onboarding causes the error spike in first 60 days",
    "references_phase":    "measure",
    "references_field":    "baseline_mean",
    "references_metric_name": "invoice_error_rate",   # NEW — which metric
    "references_value":    "12.3%",
}
```

The grader resolves the link by lookup against Measure's gate document (§42),
now matching on `references_metric_name` against the `phase_metrics` key, not on
a bare scalar. `causal_hypothesis` stays **Tier 2** (the substance is in the
Tier-1 `root_cause_*` fields); the linkage traceability itself rides on
`phase_metrics`, which is not skippable.

## 39.3.4 Two movements — generate, then validate

*Analyse's methodology core (parallel to Measure's §39.2.4 SIPOC handling).*

**Movement 1 — generate (qualitative).** From Measure's `vital_few_drivers`, the
coach helps the Belt generate candidate causes: a **fishbone** (`propose_template`
/ `propose_diagram`) to structure them by category, **5 Whys** (a coaching
sequence, not a tool) to drill past symptoms, **Pareto** (`propose_diagram`) to
focus. Output: `causal_hypothesis`. No computation tool — this is structured
thinking, nothing to calculate.

**Movement 2 — validate (quantitative).** Each surviving hypothesis is tested
against the data with the computation tools (§39.3.5). Output: `root_cause_
validation`, `ruled_out_causes`, and — only once proven — `root_cause_statement`.

**The bright line between them is the load-bearing teaching of the phase.** A
cause that feels obvious on a fishbone is a hypothesis, not a finding, until the
data backs it. Skipping movement 2 is how a Belt ships their first guess as a
root cause.

## 39.3.5 Tools bound to Analyse

Passed to the executor via `tools=` on `create_agent` (§18). **Twelve** — under
the 16 cap (§30).

- **The universal seven** (§29.2), on every phase — including `propose_template`
  and `propose_diagram`, which carry the **generation** tools here: fishbone,
  Pareto, scatter plot, box plot. 5 Whys is a SKILL.md coaching sequence, not a
  registered tool.
- **Five computation tools** (§30 binding; specified §69), standard statistical
  names kept, plain-concept-then-standard-term docstrings:

| Job | Tools | Use |
|---|---|---|
| Compare groups | `t_test`, `anova` | Does the driver shift the outcome between groups? |
| Association, categorical | `chi_square_test` | Are two categorical factors related? |
| Association, continuous | `pearson_correlation` | Do two continuous variables move together? |
| Explain / predict | `linear_regression` | How much of the outcome does the driver explain? |

No `calculate_doe_main_effects` — DOE belongs to Improve (§30). Each tool runs
under the seven-step pattern (§43.1). SKILL.md `allowed-tools` MUST match this
exact subset (§32).

## 39.3.6 Conditions — methodology guards, routing, and the gate

**Two methodology guards** (Analyse's equivalent of Measure's sequence locks):

1. **Correlation is not causation.** When `pearson_correlation` or
   `linear_regression` shows association, the coach requires a plausible
   **mechanism** before it is written as a root cause. Association is evidence
   toward a hypothesis, never the confirmation itself — enforced by the rubric.
2. **Statistical ≠ practical significance.** A result may be statistically
   significant (`p < 0.05`) and explain a trivial share of the problem. The gate
   requires **`practical_significance`** (Tier 1) alongside validation — the
   eBook's second gate. A validated cause explaining too little is coached back,
   not carried to Improve.

**Routing conditions** — the five-node cycle (§13), `Command`-routed (§15). The
Analyse-specific one:

| Where | Condition | Goes to |
|---|---|---|
| `planner` (S-F13 DP1) | current field incomplete, or more fields remain | `executor` (`field_index++`) |
| `planner` | may select `retrieval_strategy = multi_hop` (§26) — Analyse is the phase this exists for | `executor` |
| `planner` | all 9 captured | `validation_stack` |
| `validation_stack` | 2b presence of the **4 Tier 1** + 2d `ANALYSE_RUBRIC` pass | `gate_review` |
| `validation_stack` | fail | `planner` (+ `validator_feedback`); `gate_attempts ≥ 3` → escalation (§38) |
| `gate_apply` | Belt approve / reject | `END` / `planner` (+ `rejection_feedback`) |

**Gate-pass condition:** the 4 Tier 1 fields present and `ANALYSE_RUBRIC` clears;
the 5 Tier 2 fields warn only, a skip recorded in `acknowledged_gaps` (§35).

## 39.3.7 State parameters (`AnalyseState`)

*Indexes §6 / §58.2 — S-C02.* `AnalyseState` extends `PhaseState`. The
Analyse-specific reads/writes — note this is the phase where multi-hop is real:

| PhaseState field | In Analyse |
|---|---|
| `artifacts` | the 9 captured fields + `phase_metrics` + `computation_results` |
| `field_index` | walks the §39.3.2 list (0–8) |
| `hop_results` / `synthesis_output` | **populated here** — Analyse's planned multi-hop retrieval chain (§26); the dedicated synthesis call's output lives in state, not a node local, so it is traced and survives resume |
| `computation_results` | every hypothesis test run; the grader scans it for `t_test` / `anova` / `chi_square_test` evidence, not prose |
| `gate_attempts` | Analyse's own retry counter, cap 3 |
| `citations` / `uploads` | evidence trail; Analyse leans on `rag_lookup_case_history` (precedent from other projects) more than any phase |

## 39.3.8 Metric literacy — what each metric and statistic means

New requirement (amendment §4), Analyse instance. The coach teaches, in plain
language (§50), for each thing in play:

- **The metric** — echo its Define `meaning`; frame what "explaining" it means
  ("we're finding what drives the 12.3% error rate, and how much of it").
- **The statistic** — the seven-step *educate* step (§43.1 step 1) for
  `p-value`, `t-statistic`, `R²`, `correlation coefficient`. *"A p-value is the
  chance you'd see this result if the driver made no difference — small means
  the effect is probably real. R² is the share of the variation this driver
  explains — that's your practical significance."*

Never a raw dump — `t = 4.23, p = 0.001` without the plain-language read is a
rubric failure (§43.1).

## 39.3.9 Gate, storage, progress view

- **Four Tier 1 fields block** the gate (§35). Five Tier 2 warn only.
- **The live gate document** (§50) renders the fishbone / Pareto / scatter via
  `propose_diagram` inline, and `computation_results` (each test) with its
  interpretation, grouped by `phase_metrics` `name`. Narrative from captured
  field text + `computation_results` + `phase_metrics` — never `CoachingResponse`
  turn fields (§50, WATCH 9).
- **Two progress bars**, Tier 1 and Tier 2.
- Written **once** to `store/projects/{case_id}/artifacts/analyse.json` by
  `gate_apply` (§9, §33).

## 39.3.10 The SKILL.md content

`skills/dmaic-analyse-phase/SKILL.md` is generated from this section and must
match. **Authoritative during the refactor.** It carries the A→F session flow, a
Measure-recap opening (show the Belt the `vital_few_drivers` and `baseline_mean`
they arrive with), the two-movements structure, the seven-step sequence per
computation tool, the 5-Whys coaching sequence, a worked example per field, the
metric-literacy explanations (§39.3.8), the Document Layout, and the
contradiction-check instruction (§32). **This SKILL.md does not exist yet** — it
is written from this section.

## 39.3.11 Cross-phase reads and writes

**Reads from Measure** (`store.get(("projects", case_id, "artifacts"), "measure")`):
`vital_few_drivers` (**the starting list — Analyse tests exactly these**),
`driver_priority_summary` (how they were ranked), `baseline_mean` and
`phase_metrics` (the values `causal_hypothesis` references),
`measurement_system_validated` and `stability_assessment` (preconditions — tests
on unvalidated or unstable data are meaningless), `data_collection_plan` (reuse
its definitions). Also reads Define's `metric_definitions` (the registry).

**Writes**: the 9 content fields, `phase_metrics` (the linkage), and
`causal_hypothesis` (with `references_metric_name`).

**Hands to Improve**: `root_cause_statement` (**what the solution must address**),
`practical_significance` (the size of the prize), `causal_hypothesis` and
`phase_metrics` (the metric linkage Improve's `solution_linked_to_root_cause`
extends).

## 39.3.12 The other two phases

Improve and Control follow this same section shape and take §39.4–§39.5 at their
own reviews. **Analyse, Define and Measure are now the ratified exemplars;
Improve and Control remain stubbed.**
