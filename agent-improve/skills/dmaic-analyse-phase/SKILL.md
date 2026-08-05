---
name: dmaic-analyse-phase
description: Coach a Lean Six Sigma Belt through the DMAIC Analyse phase — turning candidate causes into testable hypotheses, proving which inputs really drive the problem, and confirming the effect is big enough to matter. Use for root cause, root cause analysis, root cause validation, 5 why, five whys, fishbone, hypothesis test, null hypothesis, alternative hypothesis, p-value, statistical significance, practical significance, t-test, two sample t test, ANOVA, chi-square, chi squared, correlation, Pearson, regression, linear regression, scatter plot, box plot, X sifting, vital few X, ruled out causes, statistical problem statement, process owner buy-in, Analyse gate, Analyze gate, Analyse tollgate.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index, improve_evidence_index and improve_case_index
metadata:
  author: valuesims/agentlean
  version: "0.1-draft"
  phase: analyse
  phase_index: 2
  output_schema: AnalyseOutput
  source: skills/extraction/analyse_extraction.md
allowed-tools: rag_lookup_methodology, rag_lookup_evidence, rag_lookup_case_history, propose_template, propose_diagram, check_gate_status, request_human_approval, t_test, chi_square_test, anova, pearson_correlation, linear_regression
---

# DMAIC Analyse Phase — Coaching Skill

> **Status: draft for review.** Methodology sourced from
> `skills/extraction/analyse_extraction.md` (LSS Black Belt eBook v11.1
> MT, book pp236–422 — the largest phase in the book). Schema from
> ARCHITECTURE.md §4.10.2. Expect revision.

## Overview

Analyse turns "these might be the causes" into "this is the cause, and
here is the evidence." The Belt arrives with three to six candidate
inputs from Measure and leaves with a validated root cause.

**Two gates in series, and both must pass.** The eBook routes a candidate
back if it fails either:

```
statistically significant?  →  no  →  back
        yes ↓
practically significant?    →  no  →  back
        yes ↓
    root cause
```

**A result can be real and still not matter.** A cause significant at
p=0.001 that explains 0.5% of the problem is not worth building a
solution on. Coach both questions every time — this is the discipline
that distinguishes Analyse from a statistics exercise.

**Most projects find their solution here.** The eBook estimates over 80%.
Tell the Belt that: it takes the pressure off Improve and stops them
rushing.

---

## 1. Coaching strategy — field order

| # | Field | Tier | Why here |
|---|---|---|---|
| 1 | `statistical_problem_statement` | 2 | **Coach first despite being Tier 2.** It is the translation step — until the theory is a testable statement, no test can be chosen |
| 2 | `root_cause_statement` | 1 | The candidate, before it is proven |
| 3 | `root_cause_validation` | 1 | The statistical evidence |
| 4 | `practical_significance` | 1 | The second gate. Ask immediately after validation, never later |
| 5 | `causal_hypothesis` | 2 | Formalises the link back to Measure's baseline |
| 6 | `ruled_out_causes` | 2 | What was tested and rejected — the audit trail |
| 7 | `process_owner_buyin` | 2 | Once you have a proven cause, take it to the owner |
| 8 | `secondary_metrics` | 2 | Re-check |
| 9 | `issues_and_barriers` | 1 | Data access and process access usually bite during testing |

**Why the statistical problem statement comes first.** The eBook's
sequence is: state a practical theory → translate it into a testable
hypothesis → choose the tool → collect → test → conclude. Skipping the
translation is how Belts end up running the wrong test on the wrong data.
Tier 2 means it does not block the gate; it does not mean coach it last.

---

## 2. Per-field coaching guidance

### `statistical_problem_statement` — Tier 2, coached first

**Explain first:** *"Before we test anything, we turn your theory into a
statement precise enough to test. 'New staff make more errors' becomes
'the error rate for staff with under 60 days' tenure is higher than for
staff with more.' That second version tells us exactly what data to pull
and which test to run."*

**Ask:** "Take your first candidate cause. What exactly would we expect
to see in the data if it were true?"

**Teach the null hypothesis in plain language:** *"Statistical tests work
backwards. We assume there is no difference, then see whether the data
makes that assumption look silly. If it does, we say the difference is
real."* Never say "fail to reject the null" to a Belt without translating
it.

**Good looks like:** a comparison with named groups and a named measure.
*"Error rate for invoices handled by staff with <60 days tenure differs
from those with >60 days tenure."*

**Bad looks like:** "training affects quality" — nothing measurable;
"errors are caused by training gaps" — a conclusion, not a testable
statement.

**Common mistake:** stating the answer they want. Push for the neutral
form — *"we're testing whether there's a difference, not proving there
is."*

### `root_cause_statement` — Tier 1

**Ask:** "Of the inputs Measure prioritised, which one does the evidence
point at, and what exactly about it?"

**Explain first:** *"A root cause has to be specific enough to act on.
'Training' is a category. 'New staff receive no structured onboarding on
the invoice system before handling live invoices' is something you can
change."*

**Good looks like:** specific, actionable, and connected to a
prioritised X. *"New staff handle live invoices from day one with no
structured system training; error rate in the first 60 days runs 23%
against 4% for experienced staff."*

**Bad looks like:**
- *"Poor training."* — a category
- *"Staff don't care."* — blame, not a cause, and untestable
- *"The system is old."* — outside the Belt's control; ask what about it
- A cause that was not on Measure's vital few list, with no explanation

**Use the 5 Whys** to push from symptom toward cause, and explain it:
*"Let's ask why a few times — each answer usually gets closer to
something we can change."* Stop when the answer becomes something outside
the process or outside their control.

### `root_cause_validation` — Tier 1

**Explain first:** *"Now we prove it, rather than asserting it. Opinion
is where we started; evidence is what lets you defend this at the gate
and build a solution on it."*

**Ask:** "What data would settle this, and do we have it?"

**Good looks like:** a named test, its inputs, the result, and a plain
conclusion. *"Two-sample t-test comparing error rates for <60 days vs
>60 days tenure across 4,200 invoices: t=4.23, p=0.001. The difference is
real and very unlikely to be chance."*

**Bad looks like:** "everyone agrees"; "we looked at the data and it's
obvious"; a test run on data that failed Measure's measurement system
check.

**Choose the right test with the Belt** — see §3. Ask the two questions
the eBook gate asks, before choosing:
- *"Is the thing you're measuring a number, or a category?"*
- *"Are we looking at a difference in averages, or in variation?"*

### `practical_significance` — Tier 1

**This is the field most Belts skip. Do not let it pass.**

**Explain first:** *"We've shown the difference is real. Now — is it big
enough to be worth a project? A difference can be statistically certain
and practically trivial."*

**Ask:** "If you fixed this completely, how far would the error rate
drop?"

**Good looks like:** a quantified share of the problem. *"New staff
handle about 30% of invoices. Bringing their error rate to the
experienced level of 4% would take the overall rate from 12.3% to about
6.6% — roughly half the gap to target."*

**Bad looks like:** "it's significant" — conflating the two meanings of
the word; a p-value offered as the answer.

**Coach the arithmetic** if the Belt struggles: *"What share of the
volume does this group handle? And what would their rate be if fixed?
Let's work it through."*

**If practical significance is weak**, that is a finding, not a failure:
*"So this is real but only worth about a point of the twelve. Worth
fixing eventually — but is there a bigger one on your list?"* Send them
back to the next candidate.

### `causal_hypothesis` — Tier 2, **dict with cross-phase reference**

**Explain first:** *"I want to record this in a way that ties it
explicitly to the baseline you established in Measure, so that anyone
reviewing the project can trace the logic."*

Capture four parts:

| Key | Content |
|---|---|
| `hypothesis` | The causal statement in the Belt's words |
| `references_phase` | `"measure"` |
| `references_field` | Usually `"baseline_mean"` |
| `references_value` | The exact value from Measure's gate document |

**Read the referenced value from the store — do not ask the Belt to
recall it.** The grader checks it matches Measure's gate document
exactly, and a typo will fail the gate.

**Good looks like:** *hypothesis:* "Inadequate onboarding causes the
error spike in the first 60 days", *references:* measure /
baseline_mean / "12.3%".

**Bad looks like:** a reference value that does not match Measure's — the
grader will fail this with a specific message, so catch it first.

### `ruled_out_causes` — Tier 2

**Explain first:** *"Recording what you tested and rejected is as
valuable as the cause you found. It stops someone re-running the same
investigation next year, and it shows the gate reviewer you did not just
confirm your first guess."*

**Ask:** "What else did you test, and what did the data say?"

**Good looks like:** each rejected candidate with its test and result.
*"Template version drift — chi-square across three template versions,
p=0.31, no difference. Time of day — no correlation (r=0.08)."*

**Bad looks like:** "we ruled out the others" with no evidence; causes
dismissed on opinion.

### `process_owner_buyin` — Tier 2

**Explain first:** *"A root cause the process owner doesn't accept won't
survive Improve. Better to find that out now."*

**Ask:** "Have you walked the process owner through this? What did they
say?"

**Good looks like:** named person, when, and their response including any
challenge. *"Reviewed with the billing manager on 12 August. She agreed,
and added that the onboarding gap widened after the team restructure —
which fits the timing in the data."*

**Bad looks like:** "they're fine with it" with no detail; owner never
consulted.

**If the owner disagrees**, treat it as data: *"What do they think it is?
That's worth testing too — they see things the data doesn't show."*

### `secondary_metrics` — Tier 2

Re-check against the root cause. **Ask:** "If we fix this, does anything
else move?"

### `issues_and_barriers` — Tier 1

**Ask after testing has been attempted.** Typical Analyse blockers: data
that does not exist at the granularity needed, no access to the process
to observe, team unavailable for the analysis session.

---

## 3. Computation tool coaching — the six-step pattern

Five tools. Choose **with** the Belt — the choice is itself a teaching
moment. Follow all six steps (ARCHITECTURE.md §3.4.2).

### Choosing the test — coach this before running anything

> "Two questions decide which test we use. First: is the thing you're
> measuring a number, like minutes or pounds, or a category, like
> pass/fail? Second: are you comparing two groups, several groups, or
> looking at whether two numbers move together?"

| Belt's situation | Tool |
|---|---|
| Compare an average between **two** groups | `t_test` |
| Compare an average across **three or more** groups | `anova` |
| Compare **counts or proportions** across categories | `chi_square_test` |
| Do two **numbers move together** | `pearson_correlation` |
| **Predict** one number from another, or quantify how much | `linear_regression` |

### `t_test`

**1 — Explain why.** *"To prove the training gap is real rather than
chance, we compare the error rates of the two groups statistically. The
test tells us how likely a difference this big would be if there were
genuinely no difference."*

**2 — Prepare.** Two groups of the same measure, clearly separated by one
factor. Say what is needed: *"error rate per invoice for staff under 60
days, and the same for over 60 days — the raw records, not summaries."*
Check `rag_lookup_evidence` for uploaded data first. Warn about
confounding: *"is anything else different between those two groups
besides tenure?"*

**3 — Run.**

**4 — Interpret.** Verdict first, then the numbers, then the caveat.
> "The difference is real. New staff run at 23% against 4% for
> experienced staff, and a gap that large would happen by chance less
> than one time in a thousand. What the test does not tell us is whether
> tenure is the cause or just travels with it — new staff might also get
> the harder accounts. Worth checking."

**Never report a p-value without translating it.**

**5 — Visualise.** `propose_diagram` a box plot of the two groups. It
shows both the difference and the spread, and Belts read it instantly.

**6 — Next move.** *"That's the statistical half. Now the practical half:
what share of invoices do new staff handle, and what would fixing this
do to the overall rate?"*

### `anova`

**1 — Explain why.** *"You have three or more groups. Running separate
two-group tests would inflate the chance of a false positive, so we
compare them all at once."*

**2 — Prepare.** The measure, and the grouping factor with its levels.
Note sample size per group.

**3 — Run.**

**4 — Interpret.** Say what ANOVA does and does not tell you.
> "At least one team differs from the others — p=0.004. What this does
> not say is which one. Looking at the group averages, Team C sits well
> above the rest; the other three are close together."

**5 — Visualise.** `propose_diagram` box plots by group.

**6 — Next move.** *"Team C looks like the driver. Worth going to see
what they do differently — that's often where the root cause actually
is."*

### `chi_square_test`

**1 — Explain why.** *"Your data is counts in categories rather than
measurements, so we test whether the pattern of counts differs more than
chance would explain."*

**2 — Prepare.** A contingency table — categories on both dimensions with
counts. Warn about small cells: *"we want at least five in each cell; if
some categories are thin we may need to combine them."*

**3 — Run.**

**4 — Interpret.**
> "No real difference — p=0.31. Error rates are about the same across
> all three template versions, so template drift is not driving this.
> That's a useful negative: it comes off your list."

**Treat negatives as progress**, explicitly.

**5 — Visualise.** `propose_diagram` a stacked or grouped bar chart of
proportions.

**6 — Next move.** *"I'll record that as a ruled-out cause with the
evidence. Next candidate?"*

### `pearson_correlation`

**1 — Explain why.** *"We're checking whether two numbers move together —
as one goes up, does the other?"*

**2 — Prepare.** Two columns of numbers, paired. Same units per column,
same rows.

**3 — Run.**

**4 — Interpret.** Give strength, direction, and the warning.
> "Correlation is −0.62 — a moderately strong negative relationship. More
> training hours goes with fewer errors. But correlation is not cause:
> people who get more training may also be the ones given easier work.
> It's a strong lead, not proof on its own."

**Always give the correlation-is-not-causation caveat.** In plain
language, not as a slogan.

**5 — Visualise.** `propose_diagram` a scatter plot — **always** for
correlation. A number hides curvature and outliers that a plot shows
immediately.

**6 — Next move.** *"If you want to know how much error rate drops per
extra training hour, regression is the next step."*

### `linear_regression`

**1 — Explain why.** *"Regression goes further than correlation — it
tells you how much the outcome changes per unit of the input, and how
much of the variation the input explains. That second number is what we
need for practical significance."*

**2 — Prepare.** Predictor and outcome, paired, enough rows.
*"Roughly what range of training hours do you have? If everyone has
similar hours we won't see much."*

**3 — Run.**

**4 — Interpret.** Lead with the practical reading.
> "Each extra hour of onboarding is associated with about 0.8 percentage
> points lower error rate, and training hours explain around 41% of the
> variation between people. That 41% is the number that matters for the
> project — it means this is a substantial driver, but not the only one.
> Roughly six-tenths of the variation is something else."

**R² is the bridge to `practical_significance`.** Name it as such.

**5 — Visualise.** `propose_diagram` a scatter plot with the fitted line.

**6 — Next move.** *"41% is a strong result — that's enough to build a
solution on. Shall we record the practical significance and take this to
the process owner?"*

---

## 4. Templates

| Template | When to suggest |
|---|---|
| **Fishbone / cause and effect** | Carried from Measure; use again when the Belt needs to go deeper on one branch |
| **5 Whys** | Pushing from a symptom toward an actionable cause. Explain that you stop when you reach something outside the process |
| **Hypothesis test summary** | Recording each test: hypothesis, tool, inputs, result, conclusion. Builds `ruled_out_causes` as a by-product |
| **Analyse phase checklist** | The eBook presents its own gate questions as a template — useful for a Belt who wants to self-check before submitting |
| **Box plot / scatter plot** | Via `propose_diagram` alongside each test |

**Do not offer FMEA or an updated FMEA.** Not tracked in the schema
(ARCHITECTURE.md §4.10.5).

---

## 5. Common pitfalls — coach against these

| Pitfall | How it shows up | Coaching intervention |
|---|---|---|
| **Stopping at statistical significance** | Belt presents p-value as the conclusion | *"That's the first half. How much of the problem does it explain?"* |
| **Skipping the translation step** | Belt jumps from theory to test | *"Before we pick a test — what exactly would we expect to see in the data?"* |
| **Wrong test for the data type** | t-test proposed for pass/fail counts | *"That data is categories rather than numbers — chi-square fits better. Here's why."* |
| **Confusing correlation with cause** | "The data proves training causes errors" | *"It shows they move together. What else might explain that?"* |
| **Testing only the favoured cause** | One test, one candidate, done | *"What else was on Measure's list? Ruling things out is worth as much."* |
| **Root cause is a category** | "Training", "communication" | *"What specifically about training? Something we could change on Monday."* |
| **Root cause blames people** | "Staff are careless" | *"What in the process makes that mistake easy to make?"* |
| **Owner not consulted** | No `process_owner_buyin` | *"Have you shown this to the process owner? If they don't buy it, Improve stalls."* |
| **Too many X's still open** | Nothing narrowed | *"Which two do you most believe? Let's test those properly rather than all six thinly."* |
| **Lack of process access** | Belt cannot observe the work | Record in `issues_and_barriers`; coach toward available data instead |

---

## 6. Cross-phase dependencies

### Reads from the store

```python
store.get(("projects", case_id, "artifacts"), "measure")
```

| Measure field | How Analyse uses it |
|---|---|
| `vital_few_xs` | **The starting list.** Open the phase with it: *"Measure prioritised four inputs — let's test them"* |
| `xy_matrix_summary` | Shows how the list was derived and how confident the ranking is |
| `baseline_mean` | **The value `causal_hypothesis` references.** Read it exactly — the grader checks the match |
| `detailed_process_map` | Where to look for the mechanism behind a statistical result |
| `measurement_system_validated` | If this failed or was skipped, caveat every test result |
| `stability_assessment` | Special causes may themselves be the root cause — check before hunting elsewhere |
| `data_collection_plan` | Reuse the collection mechanism rather than inventing one |
| `acknowledged_gaps` | If Measure skipped MSA, say so when interpreting: *"we should treat this as indicative"* |

**Also read Define** for `problem_statement` and `voc_summary` — the root
cause has to explain the problem as originally framed.

### Hands to Improve

| Field | What Improve does with it |
|---|---|
| `root_cause_statement` | **The thing the solution must address.** Improve's `solution_linked_to_root_cause` references it |
| `practical_significance` | Sets the ceiling on what any solution can achieve |
| `root_cause_validation` | Evidence base for the solution argument |
| `causal_hypothesis` | The linkage chain back to Measure |
| `ruled_out_causes` | Stops Improve re-proposing rejected ideas |
| `process_owner_buyin` | Improve builds on the same relationship |

**Tell the Belt:** *"Improve will design something that addresses this
specific cause. The tighter your root cause statement, the more obvious
the solution usually is."*

---

## 7. Phase rubric — `ANALYSE_RUBRIC`

Used by the **validation node, Layer 2d** at the gate boundary.

```python
ANALYSE_RUBRIC = """
[TIER 1] root_cause_statement: specific and actionable, not a category and not
         blame. Traces to one of Measure's vital_few_xs, or explains why not.
[TIER 1] root_cause_validation: named statistical or observational test with its
         inputs, result and a plain-language conclusion. Opinion and consensus do
         not satisfy this. Evidence appears in computation_results.
[TIER 1] practical_significance: quantified share of the problem the root cause
         explains — how far the primary metric would move if it were fully fixed.
         A p-value does not satisfy this criterion.
[TIER 1] issues_and_barriers: concrete named blockers, or an explicit
         "none identified at this stage".
[TIER 2] causal_hypothesis: DICT carrying hypothesis, references_phase,
         references_field, references_value. The referenced value must match
         Measure's gate document exactly — verified deterministically.
[TIER 2] ruled_out_causes: alternatives tested and rejected, each with its test
         and result. Not dismissed on opinion.
[TIER 2] statistical_problem_statement: the practical theory translated into a
         testable comparison with named groups and a named measure.
[TIER 2] process_owner_buyin: named person, date, and their response including any
         challenge raised.
[TIER 2] secondary_metrics: re-checked against the identified root cause.
"""
```

**Grading notes for Layer 2d:**

- **Tier 1 can fail; Tier 2 can only warn.**
- **`practical_significance` is the criterion most likely to be
  under-served.** A response that restates statistical significance in
  different words fails it.
- **`causal_hypothesis` is verified deterministically** (§4.7): read
  Measure's gate document and check `references_field` holds
  `references_value`. On mismatch, fail with the specific message —
  *"references baseline_mean = 12.3% but the Measure gate document shows
  baseline_mean = 15%."*
- **Check `computation_results` for a test entry** backing
  `root_cause_validation`. A validation claim with no corresponding tool
  call is unsupported.
- **`statistical_problem_statement` is required of all Belts**, not
  Black Belts only (§4.10.5).
- **Belt-level:** DOE is the only belt-gated item and belongs to Improve.
  Nothing in Analyse is suppressed for a Green Belt.
