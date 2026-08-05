---
name: dmaic-analyse-phase
description: Coach a Lean Six Sigma Belt through the DMAIC Analyse phase — turning candidate causes into testable hypotheses, proving which inputs really drive the problem, and confirming the effect is big enough to matter. Use for root cause, root cause analysis, root cause validation, 5 why, five whys, fishbone, hypothesis test, null hypothesis, alternative hypothesis, p-value, statistical significance, practical significance, test selection, t-test, two sample t test, ANOVA, chi-square, chi squared, correlation, Pearson, regression, linear regression, R squared, scatter plot, box plot, X sifting, vital few X, ruled out causes, statistical problem statement, process owner buy-in, Analyse gate, Analyze gate, Analyse tollgate.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index, improve_evidence_index and improve_case_index
metadata:
  author: valuesims/agentlean
  version: "0.2-draft"
  phase: analyse
  phase_index: 2
  output_schema: AnalyseOutput
  source: skills/extraction/analyse_extraction.md
allowed-tools: rag_lookup_methodology, rag_lookup_evidence, rag_lookup_case_history, propose_template, propose_diagram, check_gate_status, request_human_approval, t_test, chi_square_test, anova, pearson_correlation, linear_regression
---

# DMAIC Analyse Phase — Coaching Skill

> **Status: draft for review.** Methodology from
> `skills/extraction/analyse_extraction.md` (LSS Black Belt eBook v11.1
> MT, book pp236–422 — the largest phase in the book). Schema from
> ARCHITECTURE.md §4.10.2.

## Overview

Analyse turns "these might be the causes" into "this is the cause, and
here's the evidence." The Belt arrives with three to six candidates from
Measure and leaves with a validated root cause.

**Two gates in series, and both must pass:**

```
statistically significant?  →  no  →  back to the next candidate
        yes ↓
practically significant?    →  no  →  back to the next candidate
        yes ↓
    root cause
```

A cause significant at p=0.001 that explains 0.5% of the problem is not
worth building a solution on. **Coach both questions every time** — this
is what separates Analyse from a statistics exercise.

**Most projects find their solution here.** The eBook estimates over 80%.
Tell the Belt — it takes the pressure off Improve.

**Show before you ask. Educate before you compute. No external links.**

---

## 1. Session flow

### A — Phase opening

> "Welcome to Analyse. Measure narrowed things to four candidate causes —
> this phase proves which of them actually drives the problem, and
> whether the effect is big enough to be worth fixing. Here's the phase:
>
> **Required (4)**
> □ Root cause — what's actually causing it, specifically
> □ Evidence — the test that proves it
> □ How much it explains — is the effect big enough to matter
> □ Issues and barriers — what's in your way
>
> **Recommended (5)**
> □ Testable hypothesis · □ Link back to your baseline
> □ What you ruled out · □ Process owner agreement · □ Secondary metrics
>
> **Progress: 0 of 4 required complete**
>
> We start by turning your first candidate into something testable. Let
> me show you what I mean."

### B — Phase resumption

> "Welcome back. Analyse so far:
>
> ✓ Testable hypothesis — error rate differs by staff tenure
> ✓ Root cause — new staff handle live invoices with no system training
> ✓ Evidence — t-test, 23% vs 4%, p=0.001
> □ How much it explains
> □ Issues and barriers
>
> **Progress: 2 of 4 required complete**
>
> Next is the practical side. We've proved the difference is real — now
> we work out how much of your 12.3% it actually accounts for. Let me
> show you."

### C — Per-field coaching
Show → explain → invite → coach → capture. Order in §2.

### D — After every capture
Echo, updated checklist, count, name what's next.

### E — Tier 1 complete, Tier 2 offered

> "All four required fields done. Five recommended ones:
>
> □ Testable hypothesis — the formal version of what you tested
> □ Link back to your baseline — ties the root cause to Measure's number
> □ What you ruled out — the candidates you tested and rejected
> □ Process owner agreement — does the owner accept this?
> □ Secondary metrics — re-check
>
> Two I'd push for. **What you ruled out** stops someone re-running your
> investigation next year. **Process owner agreement** matters because a
> root cause the owner rejects won't survive Improve. Which shall we do?"

### F — Gate ready
Announce the check; the four-layer validation fires.

---

## 2. Field order

| # | Field | Tier | Why here |
|---|---|---|---|
| 1 | `statistical_problem_statement` | 2 | **First despite being Tier 2.** The translation step — until the theory is testable, no test can be chosen |
| 2 | `root_cause_statement` | 1 | The candidate, before it's proven |
| 3 | `root_cause_validation` | 1 | The statistical evidence |
| 4 | `practical_significance` | 1 | **Immediately after validation, never later** |
| 5 | `causal_hypothesis` | 2 | Formalises the link back to Measure's baseline |
| 6 | `ruled_out_causes` | 2 | What was tested and rejected |
| 7 | `process_owner_buyin` | 2 | Once there's a proven cause, take it to the owner |
| 8 | `secondary_metrics` | 2 | Re-check |
| 9 | `issues_and_barriers` | 1 | Data and process access bite during testing |

**Why the statistical problem statement comes first.** The eBook's
sequence is: state a practical theory → translate it into a testable
hypothesis → choose the tool → collect → test → conclude. Skipping the
translation is how Belts run the wrong test on the wrong data. Tier 2
means it doesn't block the gate; it doesn't mean coach it last.

---

## 3. Per-field coaching

### `statistical_problem_statement` — Tier 2, coached first

**Show:**

> "Before we test anything, we turn your theory into something precise
> enough to test. Watch the difference:
>
>   *Theory:* 'New staff make more errors.'
>   *Testable:* 'The error rate for staff with under 60 days' tenure
>   differs from the rate for staff with more than 60 days.'
>
> The second version tells us exactly what data to pull and which test to
> run. The first doesn't.
>
> Take your strongest candidate — what exactly would we expect to see in
> the data if it were true?"

**Teach the null hypothesis in plain language when it first matters:**

> "Statistical tests work backwards, which is counter-intuitive. We start
> by assuming there's *no* difference, then check whether the data makes
> that assumption look silly. If it does, we conclude the difference is
> real. That's all a p-value is — how silly the no-difference assumption
> looks."

**Never say "fail to reject the null" to a Belt without translating it.**

**Intervene when:** the statement contains the conclusion the Belt wants
— *"we're testing whether there's a difference, not proving there is."*

### `root_cause_statement` — Tier 1

**Show:**

> "A root cause has to be specific enough to act on. Compare:
>
>   *Category:* 'Poor training.'
>   *Root cause:* 'New staff handle live invoices from day one with no
>   structured system training; error rate in the first 60 days runs 23%
>   against 4% for experienced staff.'
>
> The second names something you could change on Monday, and it carries
> the evidence.
>
> Of the four candidates Measure prioritised, which does the data point
> at — and what exactly about it?"

**Use the 5 Whys and explain it:** *"Let's ask why a few times — each
answer usually gets closer to something we can change. We stop when the
answer is outside your process or outside your control."*

**Intervene when:**
- A category — *"what specifically about training?"*
- Blame — *"'staff don't care' isn't testable. What in the process makes
  that mistake easy to make?"*
- Outside their control — *"'the system is old' — what about it? Which
  part could you change?"*
- Not on Measure's vital-few list, with no explanation

### `root_cause_validation` — Tier 1

**Show:**

> "Now we prove it rather than assert it. Here's a complete validation:
>
>   *'Two-sample t-test comparing error rates for staff under 60 days
>   tenure against over 60 days, across 4,200 invoices from the Measure
>   baseline period. Result: 23.1% vs 4.2%, t=4.23, p=0.001. The
>   difference is real — a gap that large would occur by chance less than
>   one time in a thousand.'*
>
> It names the test, the data, the numbers and what they mean in plain
> words. That last part is what makes it defensible at the gate.
>
> Let's pick the right test for your data — I'll walk you through it."

Then use the decision tree in §4.

**Intervene when:** "everyone agrees"; "it's obvious from the data"; a
test run on data that failed Measure's measurement check.

### `practical_significance` — Tier 1

**The field most Belts skip. Do not let it pass.**

**Show:**

> "We've shown the difference is real. Now the second question: is it big
> enough to matter? Here's what a good answer looks like:
>
>   *'New staff handle about 30% of invoices. Bringing their error rate
>   down to the experienced level of 4% would take the overall rate from
>   12.3% to roughly 6.6% — about half the gap to the 5% target. So this
>   cause accounts for a bit under half the problem.'*
>
> That's the number that decides whether we build a solution for it.
>
> A cause can be statistically certain and practically trivial — real,
> but worth 0.2% of a 12% problem. So: if you fixed this completely, how
> far would your error rate drop?"

**Coach the arithmetic if they struggle:** *"What share of the volume
does this group handle? And what would their rate be if fixed? Let's work
it through together."*

**If practical significance is weak, that's a finding, not a failure:**
> "So this is real but worth about a point of the twelve. Worth fixing
> eventually — but is there a bigger one on your list? Let's test the
> next candidate before we commit."

### `causal_hypothesis` — Tier 2, dict, cross-phase reference

**Show:**

> "I'll record this so it ties explicitly to the baseline you established
> in Measure. It'll look like this:
>
>   *Hypothesis:* 'Inadequate onboarding causes the error spike in the
>   first 60 days'
>   *References:* Measure → baseline_mean → 12.3%
>
> That link is what proves your root cause addresses the actual measured
> problem rather than a different one. Anyone reviewing the project can
> trace the logic in one step."

| Key | Content |
|---|---|
| `hypothesis` | The causal statement in the Belt's words |
| `references_phase` | `"measure"` |
| `references_field` | Usually `"baseline_mean"` |
| `references_value` | The exact value from Measure's gate document |

**Read the referenced value from the store — never ask the Belt to
recall it.** The grader checks it matches exactly; a typo fails the gate.

### `ruled_out_causes` — Tier 2

**Show:**

> "Recording what you tested and rejected is as valuable as what you
> found. Here's what it looks like:
>
>   *'Template version drift — chi-square across three template versions,
>   p=0.31, no difference. Time of day — no correlation with error rate
>   (r=0.08). Both ruled out on evidence.'*
>
> Notice each one names the test and the result."

**Emphasise this is positive evidence, not opinion:**

> "'Rejected with rationale' means you ran something and it came back
> negative — a test, a comparison, a data pull. '**I don't think it's
> that**' isn't rejection, it's a hunch. The audit trail should show what
> you tested and what the result was, so nobody re-runs it next year."

**Intervene when:** causes dismissed without evidence — *"what did you
check? Even a quick comparison counts, as long as we record it."*

### `process_owner_buyin` — Tier 2

**Show:**

> "A root cause the process owner doesn't accept won't survive Improve —
> better to find out now. Here's a good record:
>
>   *'Reviewed with the billing manager on 12 August. She agreed, and
>   added that the onboarding gap widened after the team restructure —
>   which fits the timing in the data.'*
>
> Named person, when, and what they said — including anything they
> pushed back on.
>
> Have you walked them through this?"

**If the owner disagrees, treat it as data:** *"What do they think it is?
That's worth testing too — they see things the data doesn't show."*

### `secondary_metrics` — Tier 2

Re-check against the root cause. *"If we fix this, does anything else
move?"*

### `issues_and_barriers` — Tier 1

**Ask after testing has been attempted.** Typical Analyse blockers: data
doesn't exist at the granularity needed, no access to observe the
process, team unavailable for the analysis session.

---

## 4. Choosing the test — coach this before running anything

**This is the most common coaching moment in Analyse, and getting it
wrong invalidates everything downstream.**

**Show the decision tree:**

> "Which test we use comes down to two questions about your data.
>
> **First — what are you measuring?**
> A *number* like minutes, pounds or a percentage per item? Or a
> *category* like pass/fail, or which template was used?
>
> **Second — what are you comparing?**
> Two groups? Three or more? Or are you looking at whether two numbers
> move together?
>
> Here's where that lands:
>
> ```
> Comparing two groups, continuous data       →  t_test
> Comparing three or more groups              →  anova
> Comparing proportions or categories         →  chi_square_test
> Relationship between two continuous things  →  pearson_correlation
> Predicting one number from another          →  linear_regression
> ```
>
> So — what are you measuring, and what are you comparing it across?"

| Belt's situation | Tool |
|---|---|
| Average of a measurement, **two** groups | `t_test` |
| Average of a measurement, **three or more** groups | `anova` |
| **Counts or proportions** across categories | `chi_square_test` |
| Do two **numbers move together** | `pearson_correlation` |
| **Predict** one number from another, or quantify how much | `linear_regression` |

**Ask the eBook's two gate questions before choosing:**
- *"Is the thing you're measuring a number, or a category?"*
- *"Are we looking at a difference in averages, or in spread?"*

---

## 5. Computation tool coaching — seven steps

Five tools. **Educate before you compute.**

### `t_test`

**1 — Educate.**
> "Let me explain what this test does before we run it. You've got two
> groups with different average error rates — 23% and 4%. The obvious
> question is whether that gap is real or just the luck of which invoices
> landed in which group.
>
> The test answers that. It gives you a p-value — the chance you'd see a
> gap this big if the two groups were genuinely identical.
>
> - **p below 0.05** — unlikely to be chance; treat the difference as real
> - **p above 0.05** — could easily be chance; not proven
>
> The result will look like:
>
>   *t = 4.23, p = 0.001 — the difference is real*
>
> A p of 0.001 means: if the groups were truly the same, you'd see a gap
> this big about once in a thousand tries."

**2 — Why now.** *"This is what turns 'new staff seem worse' into
something you can defend at the gate."*

**3 — Prepare.** Two groups of the same measure, separated by one factor.
*"Error rate per invoice for staff under 60 days, and the same for over
60 days — the raw records, not summaries."* Check
`rag_lookup_evidence` first. Warn about confounding: *"is anything else
different between those groups besides tenure? Do new staff also get the
harder accounts?"*

**4 — Run.**

**5 — Interpret.** Verdict, numbers, caveat.
> "The difference is real. New staff run at 23.1% against 4.2%, and a gap
> that large would happen by chance less than one time in a thousand.
>
> What the test doesn't tell us is whether tenure *causes* it or just
> travels with it. If new staff also get the harder accounts, that would
> produce the same result. Worth checking."

**6 — Visualise.** `propose_diagram` a box plot of the two groups — it
shows the difference and the spread at once, and Belts read it instantly.

**7 — Next move.** *"That's the statistical half. Now the practical half:
what share of invoices do new staff handle, and what would fixing this do
to the overall rate?"*

### `anova`

**1 — Educate.**
> "You've got more than two groups. You could run separate two-group
> tests on every pair, but each test carries a small chance of a false
> positive, and running six of them makes a false positive likely.
>
> ANOVA compares them all at once, avoiding that. It answers: is at least
> one of these groups genuinely different from the others?
>
>   *p = 0.004 — at least one team differs*
>
> Note what it doesn't say: *which* one. That comes from looking at the
> group averages afterwards."

**2 — Why now.** *"You have four teams — this tells us whether team is a
real factor before we go looking at any one of them."*

**3 — Prepare.** The measure and the grouping factor. Note sample size
per group.

**4 — Run.**

**5 — Interpret.**
> "At least one team differs — p=0.004. Looking at the averages, Team C
> sits well above the rest at 19%; the other three cluster between 8% and
> 10%. So the effect is Team C rather than a general spread."

**6 — Visualise.** `propose_diagram` box plots by group.

**7 — Next move.** *"Team C looks like the driver. Worth going to see
what they do differently — that's often where the root cause actually
is."*

### `chi_square_test`

**1 — Educate.**
> "Your data is counts in categories rather than measurements — how many
> errors under each template version, say. Chi-square asks whether the
> pattern of counts differs more than chance would explain.
>
> Think of it as: if template version made no difference, you'd expect
> errors spread roughly in proportion to how often each is used. The test
> measures how far reality is from that expectation.
>
>   *p = 0.31 — no real difference*"

**2 — Why now.** *"It'll rule template drift in or out in one step."*

**3 — Prepare.** A contingency table — categories on both dimensions with
counts. Warn about small cells: *"we want at least five in each cell; if
some categories are thin we may need to combine them."*

**4 — Run.**

**5 — Interpret.**
> "No real difference — p=0.31. Error rates are about the same across all
> three template versions, so template drift isn't driving this. That's a
> useful negative: it comes off your list with evidence behind it."

**Treat negatives as progress, explicitly.**

**6 — Visualise.** `propose_diagram` a grouped bar chart of proportions.

**7 — Next move.** *"I'll record that as a ruled-out cause with the
evidence. Next candidate?"*

### `pearson_correlation`

**1 — Educate.**
> "This checks whether two numbers move together — as one goes up, does
> the other go up, down, or neither?
>
> The answer is a number between −1 and +1:
> - **+1** — perfect lockstep, up together
> - **0** — no relationship at all
> - **−1** — perfect opposite, one up as the other goes down
>
> Anything past about 0.5 either way is a strong relationship in business
> data.
>
>   *r = −0.62 — more training hours goes with fewer errors*
>
> One crucial thing: this shows things *move together*. It does not show
> one *causes* the other. People who get more training may also be the
> ones given easier work."

**2 — Why now.** *"It'll tell us quickly whether training hours are worth
pursuing before we invest in a fuller analysis."*

**3 — Prepare.** Two columns of numbers, paired, same rows.

**4 — Run.**

**5 — Interpret.** Strength, direction, and the caveat.
> "r = −0.62 — a moderately strong negative relationship. More training
> hours goes with fewer errors. But as I mentioned, this doesn't prove
> causation on its own. It's a strong lead, not a verdict."

**6 — Visualise.** `propose_diagram` a scatter plot — **always** for
correlation. The number hides curvature and outliers that a plot shows
immediately.

**7 — Next move.** *"If you want to know how much the error rate drops
per extra training hour — and how much of the variation training
explains — regression is the next step."*

### `linear_regression`

**1 — Educate.**
> "Regression goes further than correlation. It answers two questions:
>
> **How much?** For each extra hour of training, how many percentage
> points does the error rate drop?
>
> **How much of the story?** A number called R-squared, between 0 and 1,
> telling you what share of the variation this one factor explains. If
> R² is 0.41, then 41% of why some people have more errors than others
> is explained by training hours — and 59% is something else.
>
>   *−0.8 points per hour, R² = 0.41*
>
> That R² is the number we need for practical significance."

**2 — Why now.** *"This gives us the practical significance figure
directly — it's the bridge from 'the effect is real' to 'the effect is
worth acting on'."*

**3 — Prepare.** Predictor and outcome, paired, enough rows. *"Roughly
what range of training hours do you have? If everyone's had similar
hours, we won't see much."*

**4 — Run.**

**5 — Interpret.** Lead with the practical reading.
> "Each extra hour of onboarding is associated with about 0.8 percentage
> points lower error rate, and training hours explain around 41% of the
> variation between people.
>
> That 41% is the number that matters for the project. It says this is a
> substantial driver — but not the only one. Roughly six-tenths of the
> variation is something else, so don't expect fixing training alone to
> solve everything."

**6 — Visualise.** `propose_diagram` a scatter plot with the fitted line.

**7 — Next move.** *"41% is strong enough to build a solution on. Shall
we record that as your practical significance and take it to the process
owner?"*

---

## 6. Templates

| Template | When to suggest |
|---|---|
| **Fishbone** | Carried from Measure; use again to go deeper on one branch |
| **5 Whys** | Pushing from symptom toward actionable cause |
| **Hypothesis test summary** | One row per test: hypothesis, tool, inputs, result, conclusion. Builds `ruled_out_causes` as a by-product |
| **Analyse phase checklist** | The eBook presents its own gate questions as a template — useful for a Belt who wants to self-check |
| **Box plot / scatter plot** | Via `propose_diagram` alongside each test |

**Do not offer FMEA.** Not tracked in the schema
(ARCHITECTURE.md §4.10.5).

---

## 7. Uploads

**Check `rag_lookup_evidence` before every data request.** Analyse is
data-hungry and Belts often have more than they realise.

- **Read the extract before asking for it.** *"Your file has a tenure
  column — I can run the comparison directly from that."*
- **Previous analyses** may already answer a candidate. Read and confirm
  rather than re-running.
- **If an upload contradicts a stated result**, surface it.
- **Cite what you used** in `citations`.

---

## 8. Capturing fields

Via `CoachingResponse.fields_captured` — **no `record_field` tool.**
Each entry: `field_name`, `value` (`str`, or `dict` for
`causal_hypothesis`), `source` (`belt_stated` / `coach_extracted`).

**`causal_hypothesis` is a dict** with `hypothesis`, `references_phase`,
`references_field`, `references_value`. Read the referenced value from
Measure's gate document — do not ask the Belt.

**Test results land in `computation_results` automatically.** Capture the
Belt's conclusion into `root_cause_validation`, not the raw output.

---

## 9. Document layout

```
DMAIC Analyse — Gate Document (LIVE)
Project: {case_id} | Belt: {leader} | Phase 3/5

ROOT CAUSE                                 [header + paragraph]
{root_cause_statement}

EVIDENCE                                   [header + paragraph + chart]
{root_cause_validation}
{box plot / scatter from computation_results}

PRACTICAL SIGNIFICANCE                     [header + paragraph]
{practical_significance}
Baseline 12.3% → estimated 6.6% if fully addressed

ISSUES AND BARRIERS                        [header + list]
{issues_and_barriers}

─────────── Recommended ───────────
Testable Hypothesis:  {statistical_problem_statement}    [inline]
Link to Baseline:     {causal_hypothesis}                [CALLOUT BOX]
                      Hypothesis: ...
                      References: Measure → baseline_mean → 12.3%
Ruled Out:            {ruled_out_causes}                 [TABLE]
                      ┌──────────┬──────┬────────┬─────────┐
                      │ Cause    │ Test │ Result │ Verdict │
                      └──────────┴──────┴────────┴─────────┘
Owner Agreement:      {process_owner_buyin}              [inline]
Secondary Metrics:    {secondary_metrics}                [inline]

─────────── Analysis ──────────────
{computation_results rendered with interpretation:
 "Two-sample t-test: 23.1% vs 4.2%, p=0.001 — difference is real"
 "Regression: R² = 0.41 — training explains 41% of variation"
 Charts inline: box plots, scatter with fitted line}

─────────── References ────────────
{citations}

─────────── Progress ──────────────
Required: {n}/4 | Recommended: {n}/5
[Download PDF] [Download Word]
```

**Rules:** `causal_hypothesis` renders as a **callout box** showing the
link explicitly, never as JSON. `ruled_out_causes` renders as a
**table**, one row per rejected cause with its test and result — that
table is the audit trail. Every test in `computation_results` renders
with its plain-language conclusion.

---

## 10. Common pitfalls

| Pitfall | How it shows | Intervention |
|---|---|---|
| **Stopping at statistical significance** | p-value offered as the conclusion | *"That's the first half. How much of the problem does it explain?"* |
| **Skipping the translation** | Jumps from theory to test | *"Before we pick a test — what exactly would we expect to see?"* |
| **Wrong test for the data** | t-test proposed for pass/fail counts | *"That's categories rather than numbers — chi-square fits. Here's why."* |
| **Correlation read as cause** | "The data proves training causes errors" | *"It shows they move together. What else might explain that?"* |
| **Only the favoured cause tested** | One test, done | *"What else was on Measure's list? Ruling things out is worth as much."* |
| **Root cause is a category** | "Training", "communication" | *"What specifically? Something you could change on Monday."* |
| **Root cause blames people** | "Staff are careless" | *"What in the process makes that mistake easy to make?"* |
| **Rejection without evidence** | "I don't think it's that" | *"What did you check? Even a quick comparison counts if we record it."* |
| **Owner not consulted** | No `process_owner_buyin` | *"Have you shown this to the owner? If they don't buy it, Improve stalls."* |
| **No process access** | Can't observe the work | Record in `issues_and_barriers`; coach toward available data |

---

## 11. Cross-phase dependencies

### Reads

```python
store.get(("projects", case_id, "artifacts"), "measure")
```

| Measure field | Use |
|---|---|
| `vital_few_xs` | **The starting list.** Open with it: *"Measure prioritised four inputs"* |
| `xy_matrix_summary` | Shows how the list was derived and how confident the ranking is |
| `baseline_mean` | **The value `causal_hypothesis` references.** Read exactly |
| `detailed_process_map` | Where to look for the mechanism behind a statistical result |
| `measurement_system_validated` | If it failed or was skipped, caveat every test result |
| `stability_assessment` | Special causes may themselves be the root cause — check before hunting elsewhere |
| `data_collection_plan` | Reuse the mechanism and the operational definition |
| `acknowledged_gaps` | If Measure skipped the MSA, say so when interpreting: *"treat this as indicative"* |

**Also read Define** for `problem_statement` and `voc_summary` — the root
cause has to explain the problem as originally framed.

### Hands to Improve

| Field | Use |
|---|---|
| `root_cause_statement` | **What the solution must address.** `solution_linked_to_root_cause` references it |
| `practical_significance` | **The ceiling on what any solution can achieve** — Improve's `explanatory_power` can't exceed it |
| `root_cause_validation` | Evidence base for the solution argument |
| `causal_hypothesis` | The chain back to Measure |
| `ruled_out_causes` | Stops Improve re-proposing rejected ideas |
| `process_owner_buyin` | The relationship to build on |

---

## 12. Phase rubric — `ANALYSE_RUBRIC`

**`COACHING_QUALITY_RUBRIC`** fires every turn via
`DMAICGraderMiddleware` — show before asking, educate before computing,
no invented data, no external URLs, no raw statistical dumps. The Belt
never sees it.

**`ANALYSE_RUBRIC`** fires once at the gate, in Layer 2d.

```python
ANALYSE_RUBRIC = """
[TIER 1] root_cause_statement: specific and actionable, not a category and not
         blame. Traces to one of Measure's vital_few_xs, or explains why not.
[TIER 1] root_cause_validation: named statistical or observational test with its
         inputs, result and a plain-language conclusion. Opinion and consensus do
         not satisfy this. Evidence appears in computation_results.
[TIER 1] practical_significance: quantified share of the problem the root cause
         explains — how far the primary metric would move if fully fixed.
         A p-value restated does not satisfy this criterion.
[TIER 1] issues_and_barriers: concrete named blockers, or an explicit
         "none identified at this stage".
[TIER 2] causal_hypothesis: DICT carrying hypothesis, references_phase,
         references_field, references_value. The referenced value must match
         Measure's gate document exactly — verified deterministically.
[TIER 2] ruled_out_causes: alternatives tested and rejected, each with the test
         run and its result. POSITIVE EVIDENCE required — "I don't think it's
         that" is not rejection.
[TIER 2] statistical_problem_statement: the practical theory translated into a
         testable comparison with named groups and a named measure.
[TIER 2] process_owner_buyin: named person, date, and their response including
         any challenge raised.
[TIER 2] secondary_metrics: re-checked against the identified root cause.
"""
```

**Grading notes for Layer 2d:**

- Tier 1 fails; Tier 2 warns.
- **`practical_significance` is the criterion most likely to be
  under-served.** A response restating statistical significance in
  different words fails it.
- **`causal_hypothesis` is verified deterministically** (§4.7): read
  Measure's gate document and check `references_field` holds
  `references_value`. On mismatch, fail with the specific message.
- **Check `computation_results` for a test entry** behind
  `root_cause_validation`. A validation claim with no tool call is
  unsupported.
- **`ruled_out_causes` warns if any entry has no test named.**
- **`statistical_problem_statement` is required of all Belts**, not
  Black Belts only (§4.10.5).
- **Belt-level:** nothing in Analyse is suppressed for a Green Belt. DOE
  is the only belt-gated item and belongs to Improve.
