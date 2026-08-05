---
name: dmaic-measure-phase
description: Coach a Lean Six Sigma Belt through the DMAIC Measure phase — building a detailed process map with timings and waste, validating the measurement system, checking process stability before capability, establishing the baseline, and prioritising the vital few X's. Use for detailed process map, cycle time, value added, non value added, waste, VSM, measurement points, data collection plan, sample size, sampling, operational definition, measurement system analysis, MSA, gage R&R, gauge R and R, attribute agreement, repeatability, reproducibility, baseline, baseline mean, sigma level, DPMO, process capability, Cp, Cpk, yield, RTY, FTQ, stability, special causes, control chart, run chart, fishbone, Ishikawa, cause and effect, X-Y matrix, vital few, trivial many, Measure gate, Measure tollgate.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index, improve_evidence_index and improve_case_index
metadata:
  author: valuesims/agentlean
  version: "0.1-draft"
  phase: measure
  phase_index: 1
  output_schema: MeasureOutput
  source: skills/extraction/measure_extraction.md
allowed-tools: rag_lookup_methodology, rag_lookup_evidence, rag_lookup_case_history, propose_template, propose_diagram, check_gate_status, request_human_approval, calculate_sigma_level, calculate_cpk, calculate_dpmo, calculate_yield_rty, calculate_ftq, calculate_grr, calculate_sample_size_proportion, calculate_sample_size_mean
---

# DMAIC Measure Phase — Coaching Skill

> **Status: draft for review.** Methodology sourced from
> `skills/extraction/measure_extraction.md` (LSS Black Belt eBook v11.1
> MT, book pp86–235). Schema from ARCHITECTURE.md §4.10.2. Expect
> revision.

## Overview

Measure establishes what is actually happening, and proves the numbers
can be trusted before anyone acts on them. The Belt leaves this phase
with a validated baseline and a shortlist of the inputs most likely to
be driving the problem.

**This is the most tool-heavy phase — eight computation tools.** Every
one of them is a teaching moment, not a calculation. A Belt handed a Cpk
of 0.8 with no explanation has a number they cannot act on.

**Order matters more here than anywhere else.** Two sequences are
non-negotiable and you should say why out loud:

1. **Validate the measurement system before trusting any data.**
2. **Check stability before calculating capability.**

---

## 1. Coaching strategy — field order

| # | Field | Tier | Why here |
|---|---|---|---|
| 1 | `detailed_process_map` | 1 | Everything else attaches to it — measurement points, cycle times, the X's. Build it first |
| 2 | `data_collection_plan` | 1 | Flows straight out of the map's measurement points |
| 3 | `measurement_system_validated` | 2 | **Coach before the baseline.** A baseline from an unvalidated gauge is not a baseline |
| 4 | `stability_assessment` | 1 | **Coach before capability.** An unstable process has no single capability figure |
| 5 | `baseline_mean` | 1 | Only now is the number trustworthy |
| 6 | `baseline_sigma` | 2 | Falls out of the baseline and the spec limits |
| 7 | `xy_matrix_summary` | 1 | Prioritise the inputs, using the map |
| 8 | `vital_few_xs` | 1 | The ranked result — this is what Analyse starts from |
| 9 | `secondary_metrics` | 2 | Carry forward from Define, re-check |
| 10 | `issues_and_barriers` | 1 | Data access problems usually surface during collection — ask once they have tried |

**Note the tier inversion at steps 3–4.** `measurement_system_validated`
is Tier 2 but coached *before* the Tier 1 `baseline_mean`, because
sequence follows methodology, not tier. Tier decides what blocks the
gate; it does not decide teaching order.

---

## 2. Per-field coaching guidance

### `detailed_process_map` — Tier 1, **dict with six sub-fields**

**Explain first:** "In Define you mapped the process at a high level.
Now we go a level deeper — how long each step takes, who does it, which
steps actually add value, and where we can measure. This is what tells
us where the problem lives."

Read Define's `process_map_sipoc` from the store first and **open with
it**: *"Your Define map had five steps — let's expand each one."*

| Sub-field | Ask |
|---|---|
| `steps` | "Break each of your Define steps into what actually happens. Include the rework loops and the waiting." |
| `cycle_times` | "How long does each step take? Actual time, and waiting time between steps." |
| `resources` | "Who does each step, and what system or equipment do they use?" |
| `value_vs_waste` | "For each step — would the customer pay for this? If not, is it necessary anyway, or is it waste?" |
| `measurement_points` | "Where could we capture data on each step? What already gets recorded?" |
| `baseline_kpis` | "What is each step running at today?" |

**Teach value vs waste in plain language:** *"Value-adding means it
changes the thing into what the customer wants. Checking, moving,
waiting, fixing and re-entering are usually waste — necessary sometimes,
but waste. Most processes are 90%+ waste by time, so do not be alarmed."*

**Good looks like:** every Define step expanded, cycle times including
waiting, waste steps identified with a reason, measurement points that
match what the data collection plan will actually use, and a current KPI
per step.

**Bad looks like:**
- Cycle times for the work but not the waiting — waiting is usually where
  the time goes
- `value_vs_waste` marking everything as value-adding
- `measurement_points` that describe data nobody currently collects,
  with no plan to start
- `baseline_kpis` that do not connect to Define's `process_kpis`

**Check the expansion:** does the detailed map decompose Define's SIPOC,
or is it a different process? If steps have appeared that were outside
Define's scope, one of the two is wrong — surface it now.

**Offer `propose_diagram`** to render the map with timings once
populated. A visual makes the bottleneck obvious in a way a table does
not.

### `data_collection_plan` — Tier 1

**Ask:** "What are we going to collect, how much, how often, and who is
going to do it?"

**Explain first:** "The plan matters because bad data collection is
almost impossible to fix afterwards. Getting it right once beats
collecting twice."

**Teach operational definitions:** *"Before anyone collects anything,
everyone has to agree what counts. If two people would classify the same
invoice differently, the data will not mean anything. So — what exactly
counts as an error?"*

**Good looks like:** what is being measured with an agreed definition,
sample size with a basis, frequency, the person responsible, and where
the data will be stored.

**Bad looks like:** "we'll pull the error report" — no definition, no
sample basis, nobody named.

**Use `calculate_sample_size_proportion` or
`calculate_sample_size_mean`** here — see §3.

### `measurement_system_validated` — Tier 2, coached early

**Explain first, this one always needs it:** *"Before we trust any of
this data, we should check the measuring itself. If two people looking at
the same invoice disagree about whether it is an error, then the error
rate is measuring the people, not the process."*

**Ask:** "Who decides whether something counts as a defect, and would two
of them agree?"

**Good looks like:** a GR&R or attribute agreement study with a result
and a judgement — *"three reviewers, 30 invoices, 87% agreement; we
tightened the definition of 'address error' and re-ran at 96%."*

**Bad looks like:** "the system counts them automatically" with no check
that the system's rule matches the operational definition.

**Use `calculate_grr`** — see §3.

**If the measurement system fails:** do not proceed to the baseline. Coach
the fix — tighten definitions, retrain, re-run. This is the eBook's
"Repeatable & Reproducible? N" loop and it exists because a baseline from
a bad gauge is worse than no baseline.

### `stability_assessment` — Tier 1

**Explain first:** *"Before we work out how capable the process is, we
check whether it is behaving consistently. If last month was 4% and this
month is 20%, there is no single 'current level' to improve from —
something changed, and we need to know what."*

**Ask:** "Plotted over time, does the measure sit in a steady band, or
are there spikes and shifts?"

**Good looks like:** a time-ordered plot, a statement about stability,
and — if unstable — named special causes. *"Weekly error rate ran 10–14%
except weeks 12 and 13, which hit 24%. Both were during the system
migration. Excluding those, the process is stable."*

**Bad looks like:** a single average with no time dimension; instability
noticed and ignored.

**If unstable, coach the branch explicitly:**
> "Two options. Either we find and remove the special cause, or we
> exclude those periods and baseline the stable part — but we have to say
> which we did and why. What happened in those two weeks?"

**Coaching order is the point of this field.** Stability first, then
capability. Say it out loud: *"I want to check stability before we
calculate capability, because a capability number from an unstable
process is an average of two different processes."*

### `baseline_mean` — Tier 1

**Ask:** "So what is the current level, now we trust the data?"

**Good looks like:** a value with units, a sample size and a period.
*"12.3% invoice error rate, 4,200 invoices, Jan–Jun 2026, stable
excluding the migration weeks."*

**Bad looks like:** a value with no period; a value that contradicts
Define's `baseline_metric` without explanation.

**If it differs from Define's figure — flag it, do not smooth it over.**
The mid-phase contradiction check will catch it anyway. Say: *"Define had
12%, you have 12.3% — is that a refinement, or did something change?"*

### `baseline_sigma` — Tier 2

**Explain first:** *"Sigma level is a way of expressing how often the
process produces something acceptable, on a scale that lets you compare
very different processes. It is a translation of your error rate, not new
information."*

**Use `calculate_sigma_level`** — see §3. `calculate_dpmo`,
`calculate_yield_rty` and `calculate_ftq` support the same conversation.

### `xy_matrix_summary` — Tier 1

**Explain first:** *"We have a long list of things that might be causing
this. Rather than investigating all of them, we score which ones most
affect the outputs the customer cares about, and take the top few
forward. That's the whole idea — separate the few that matter from the
many that don't."*

**Sequence to coach:**
1. Brainstorm causes — a **fishbone** helps here (`propose_template`)
2. Sort them: which can you control, which are procedures, which are
   noise you cannot influence
3. Score the controllable ones against the outputs, weighted by how much
   each output matters to the customer
4. Rank

**Good looks like:** a described scoring basis, who took part, and a
ranked output. *"Team of five scored 14 causes against three outputs
weighted by customer priority. Top four: data entry rework, template
version drift, missing PO numbers, approval delays."*

**Bad looks like:** a ranking with no method; the Belt's own opinion
presented as a matrix; process participants not involved — a named eBook
roadblock.

**Push on participation:** *"Who was in the room? The people who do the
work usually know which of these actually bite."*

### `vital_few_xs` — Tier 1

**Ask:** "Which of these are you taking into Analyse, and why those?"

**Explain first:** *"Analyse is where we prove which of these actually
drives the problem. We can only test a few properly, so this choice
shapes the rest of the project."*

**Good looks like:** three to six named inputs with the reason each made
the cut. *"Data entry rework (highest score, fully in our control),
template version drift (medium score, cheap to test), missing PO numbers
(high customer impact)."*

**Bad looks like:** ten X's — nothing has been prioritised; one X — the
Belt has pre-decided the answer; X's the Belt cannot measure or control.

**This is what Analyse starts from.** Tell the Belt that: *"Analyse will
take exactly this list and test each one against your baseline data."*

### `secondary_metrics` — Tier 2

Carry forward from Define and re-check. **Ask:** "Now you have seen the
process in detail, is there anything else that could suffer if we push on
the error rate?"

### `issues_and_barriers` — Tier 1

**Ask once data collection has been attempted** — that is when the real
blockers appear.

**Good looks like:** *"The weekly extract only goes back 90 days, so we
cannot baseline a full year. Two of the five reviewers are on leave until
May, which slows the agreement study."*

---

## 3. Computation tool coaching — the six-step pattern

Eight tools. **This section is the bulk of the skill.** Every tool
follows explain → prepare → run → interpret → visualise → next move
(ARCHITECTURE.md §3.4.2). Never return raw output.

**Choosing between the two sample-size tools.** Ask what the Belt is
counting: *"is the thing you're measuring a pass/fail — right or wrong —
or a number like minutes or pounds?"* Pass/fail goes to
`calculate_sample_size_proportion`; measurements go to
`calculate_sample_size_mean`.

### `calculate_sample_size_proportion`

**1 — Explain why.** *"Before collecting, let's work out how many you
need to check. Too few and we cannot tell a real difference from noise;
too many and you have wasted your team's time."*

**2 — Prepare.** Roughly what error rate the Belt expects, how precise
they need to be, and the confidence level — say 95% is standard and why:
*"it means if we repeated this sampling twenty times, nineteen would land
within that margin."*

*"If you're not sure of the current rate, an estimate is fine — 'roughly
one in ten' is enough to size it."*

**3 — Run.**

**4 — Interpret.**
> "You need about 340 invoices to be confident within ±3%. At your volume
> that's roughly three weeks of sampling, or you can pull it from history
> if the last three months are representative."

Always translate N into effort — days of sampling, not just a number.

**5 — Visualise.** Usually unnecessary for a single N. If the Belt is
weighing precision against effort, `propose_diagram` a short table of N
against margin of error.

**6 — Next move.** *"Does three weeks work with your timeline? If not we
can accept a wider margin — tell me what precision the decision actually
needs."*

### `calculate_sample_size_mean`

**1 — Explain why.** *"Same question, but for a measurement rather than a
pass/fail — how many readings do we need before the average means
something."*

**2 — Prepare.** An estimate of the spread (standard deviation) and the
difference worth detecting. Coach the second one — Belts find it hard:
*"how big a change would actually matter to you? If a two-minute
improvement is worth having but thirty seconds isn't, that's your
number."*

If the Belt has no spread estimate, suggest a small pilot sample:
*"take twenty readings first, and we'll size the real sample from
those."*

**3 — Run.**

**4 — Interpret.**
> "About 65 readings to detect a two-minute difference reliably. That's
> a fortnight at your current volume."

**5 — Visualise.** As above — usually unnecessary for a single N.

**6 — Next move.** *"Who's going to capture these, and does the timing
fit your plan?"*

### `calculate_grr`

**1 — Explain why.** *"This checks whether your measurement system is
trustworthy. It separates the variation that comes from the process from
the variation that comes from measuring it. If measurement noise is a big
share, the data cannot support the decisions we want to make."*

**2 — Prepare.** Explain the study design in plain terms: *"Take about 10
items that cover the normal range. Have 2 or 3 people assess each one,
twice, without seeing their earlier answer or each other's. That gives us
30 to 60 measurements."*

Check `rag_lookup_evidence` — the Belt may have uploaded the study
already.

**3 — Run.**

**4 — Interpret.** Give the verdict before the numbers.
> "Your measurement system is acceptable. Measurement accounts for about
> 17% of the total variation, which is inside the usual acceptable band —
> most of what you are seeing is real process variation, which is what we
> want. Repeatability was slightly worse than reproducibility, meaning
> the same person assessing twice varied a little more than different
> people did — usually a sign the definition is fine but the task is
> fiddly."

For attribute data, interpret agreement percentage the same way — and
where agreement is poor, point at the operational definition, not the
people.

**5 — Visualise.** `propose_diagram` a components-of-variation
breakdown — it makes "measurement vs process" immediate.

**6 — Next move.** *"Good — we can trust the baseline now. If it had come
out the other way, the fix is usually tightening the definition rather
than retraining."*

### `calculate_sigma_level`

**1 — Explain why.** *"Sigma level puts your performance on a common
scale, so you can compare this process to others and see how much room
there is. It's a translation of your defect rate."*

**2 — Prepare.** Number of defects, number of units, and opportunities
per unit. Explain opportunities: *"how many distinct ways can one invoice
be wrong? If there are five fields that can each be wrong, that's five
opportunities."*

**3 — Run.**

**4 — Interpret.**
> "That's about 2.6 sigma. For context, most business processes without
> deliberate improvement sit between 2 and 3, and 4 sigma is where things
> feel reliably good. So there is real headroom here — this is not a
> process that has been squeezed dry."

Never present a sigma level without a reference point.

**5 — Visualise.** `propose_diagram` a simple scale showing where they
sit and where the target would be.

**6 — Next move.** *"Worth noting for the charter. What matters more for
the project is which inputs drive it, which is what we do next."*

### `calculate_dpmo`

**1 — Explain why.** *"Defects per million opportunities — a way of
comparing processes with very different volumes on the same footing."*

**2 — Prepare.** Same inputs as sigma level.

**3 — Run.**

**4 — Interpret.** Translate to something human: *"About 25,000 defects
per million opportunities. Put another way, roughly one in forty
opportunities goes wrong."*

**5 — Visualise.** Usually unnecessary alongside sigma level; skip rather
than duplicate.

**6 — Next move.** Connect to the baseline record.

### `calculate_yield_rty`

**1 — Explain why.** *"Rolled throughput yield asks: what proportion get
all the way through without needing fixing anywhere? It's usually much
worse than the final pass rate, because rework hides in the middle."*

**2 — Prepare.** The yield at each step — from the detailed process map's
`baseline_kpis` if it is populated.

**3 — Run.**

**4 — Interpret.** This one usually surprises people; say so.
> "Each step looks fine on its own — 95% or better. But multiply them and
> only 74% get through clean first time. That gap is your hidden factory:
> the quarter of work that gets touched twice."

**5 — Visualise.** `propose_diagram` a step-by-step yield waterfall. This
is one of the highest-value visuals in Measure.

**6 — Next move.** *"The steps with the worst individual yield are strong
candidates for the X-Y matrix. Shall we take those forward?"*

### `calculate_ftq`

**1 — Explain why.** *"First time quality — what share is right first
time at a given step, before any rework."*

**2 — Prepare.** Units processed and units needing rework at the step.

**3 — Run.**

**4 — Interpret.** Tie to the step in the map.

**5 — Visualise.** Combine with the RTY waterfall rather than a separate
chart.

**6 — Next move.** Feed into the X-Y matrix.

### `calculate_cpk`

**1 — Explain why.** *"Capability compares your process spread to what
the customer will accept. It answers 'can this process meet the
requirement as it currently runs?' — separately from whether it is
centred correctly."*

**⚠ Do not run this before `stability_assessment`.** If stability has not
been established, say so and go back: *"Let's check stability first —
a capability figure from an unstable process is an average of two
different processes."*

**2 — Prepare.** Upper and lower spec limits (from VOC where possible),
the mean, and the standard deviation. If the Belt only has one spec
limit, say that is fine and common.

**3 — Run.**

**4 — Interpret.** Answer the centring-vs-spread question explicitly —
the eBook gate asks it.
> "Cpk is 0.62. Below 1.0 means the process cannot reliably meet the
> requirement as it stands. Comparing Cp and Cpk tells us why: your spread
> alone would nearly fit, but the average sits off-centre toward the upper
> limit. So this is more a centring problem than a variation problem —
> which usually points at different fixes."

Also address short-term vs long-term if the data supports it.

**5 — Visualise.** `propose_diagram` the distribution against the spec
limits. This is the single most persuasive visual in Measure.

**6 — Next move.** *"Centring problems often trace to a setting or a
default. Worth adding to your list of candidate causes."*

---

## 4. Templates

| Template | When to suggest |
|---|---|
| **Detailed process map** | Starting `detailed_process_map`. Render with `propose_diagram` once populated |
| **Fishbone / cause and effect** | Before the X-Y matrix, to generate the candidate causes. Explain the categories in plain language — people, method, machine, material, measurement, environment |
| **X-Y matrix** | Scoring causes against weighted outputs |
| **Data collection plan** | Working `data_collection_plan` — what, definition, who, when, sample size, where stored |
| **Operational definition sheet** | When two people might classify the same item differently |
| **GR&R study sheet** | Setting up the measurement study — parts, operators, replicates |
| **Run chart / control chart** | For `stability_assessment`. Render via `propose_diagram` |

**Do not offer FMEA.** It is not tracked in the schema and is heavy
manufacturing methodology (ARCHITECTURE.md §4.10.5). If a Black Belt
raises it, support it and note the result lands in `uploads` — but never
suggest it unprompted.

---

## 5. Common pitfalls — coach against these

| Pitfall | How it shows up | Coaching intervention |
|---|---|---|
| **Capability before stability** | Belt asks for Cpk early | *"Let's plot it over time first — otherwise the number averages two different processes."* |
| **Trusting an unvalidated gauge** | Baseline offered with no MSA | *"Would two people classify the same one the same way? Let's check before we lock the baseline."* |
| **Mapping the ideal process** | No rework loops, no waiting | *"That's the designed flow. Where does it actually go wrong?"* |
| **Cycle times exclude waiting** | Step times sum to far less than end-to-end time | *"The steps add to 40 minutes but it takes 3 days. Where does the time go?"* |
| **Process participants not involved** | X-Y matrix scored by the Belt alone | *"Who else scored these? The people doing the work usually rank them differently."* |
| **Best-guess data from managers** | Numbers with no source | *"Is that from a system or an estimate? Either is workable — we just record which."* |
| **Too many vital few** | Ten X's carried forward | *"We can test three or four properly. Which would you bet on?"* |
| **Problem statement drift ignored** | Definition has quietly changed | *"This sounds different from Define. Should we update the problem statement?"* |
| **Only one of short/long-term capability** | Single Cpk reported | *"Is that from one period or across several? They often differ, and the gap is informative."* |
| **Team has no time to collect** | Collection keeps slipping | Record it in `issues_and_barriers` and coach a smaller sample rather than none |

---

## 6. Cross-phase dependencies

### Reads from the store

```python
store.get(("projects", case_id, "artifacts"), "define")
```

| Define field | How Measure uses it |
|---|---|
| `process_map_sipoc` | **Expanded into `detailed_process_map`.** Open the phase with it |
| `process_map_sipoc["process_kpis"]` | Basis for `baseline_kpis` |
| `baseline_metric` | Starting point for `baseline_mean`; flag any discrepancy |
| `project_scope` | Bounds the detailed map |
| `problem_statement` | Re-test — has it changed? |
| `voc_summary` | Source of the spec limits used in capability |
| `secondary_metrics` | Carry forward and re-check |
| `issues_and_barriers` | Factor into data collection coaching — *"you mentioned IT access was slow, so let's plan the extract early"* |
| `acknowledged_gaps` | If Define skipped `business_case`, do not assume a cost figure exists |

### Hands to Analyse

| Field | What Analyse does with it |
|---|---|
| `vital_few_xs` | **The starting list.** Analyse tests exactly these |
| `xy_matrix_summary` | Shows how the list was derived; the grader checks prioritisation happened |
| `baseline_mean` | The reference `causal_hypothesis` links back to |
| `detailed_process_map` | Root cause exploration |
| `measurement_system_validated` | Precondition — hypothesis tests on unvalidated data are meaningless |
| `stability_assessment` | Special causes may themselves be the root cause |
| `data_collection_plan` | Analyse reuses the collection mechanism |

**Tell the Belt:** *"Analyse will take these three or four inputs and
test each against your baseline data to prove which ones really drive
the problem."*

---

## 7. Phase rubric — `MEASURE_RUBRIC`

Used by the **validation node, Layer 2d** at the gate boundary.

```python
MEASURE_RUBRIC = """
[TIER 1] detailed_process_map: all six sub-fields populated — steps, cycle_times,
         resources, value_vs_waste, measurement_points, baseline_kpis. Expands
         Define's SIPOC rather than describing a different process. Cycle times
         include waiting, not only touch time. measurement_points align with
         data_collection_plan.
[TIER 1] data_collection_plan: what is measured with an agreed operational
         definition, sample size with a stated basis, frequency, named responsible
         person, and where data is stored.
[TIER 1] stability_assessment: process plotted over time with an explicit
         stability verdict. If unstable, special causes named and either removed
         or excluded with a stated rationale. Established BEFORE capability.
[TIER 1] baseline_mean: value with units, sample size and period. Consistent with
         Define's baseline_metric, or the difference explained.
[TIER 1] xy_matrix_summary: scoring basis described, participants named, ranked
         output produced. Not the Belt's unaided opinion.
[TIER 1] vital_few_xs: 3-6 named inputs carried to Analyse, each with the reason
         it made the cut. Measurable and controllable.
[TIER 1] issues_and_barriers: concrete named blockers, or an explicit
         "none identified at this stage".
[TIER 2] baseline_sigma: calculated from the baseline data, presented with a
         reference point rather than as a bare number.
[TIER 2] measurement_system_validated: GR&R or attribute agreement evidence with
         a result and a judgement. If it failed, the remedy and re-run are shown.
[TIER 2] secondary_metrics: carried from Define and re-checked against the
         detailed process map.
"""
```

**Grading notes for Layer 2d:**

- **Tier 1 can fail; Tier 2 can only warn.**
- **`detailed_process_map` fails if any of the six sub-fields is empty**,
  and should fail if it does not decompose Define's `process_map_sipoc`.
- **Check the stability-before-capability sequence.** If
  `computation_results` contains a `calculate_cpk` entry at an earlier
  turn than the stability work, flag it — the number may be
  meaningless.
- **Check `computation_results` for evidence**, not just prose:
  `calculate_grr` for `measurement_system_validated`,
  `calculate_sigma_level` for `baseline_sigma`.
- **Belt-level:** do not flag FMEA or X-Y-matrix depth as a Black Belt
  expectation — the X-Y matrix is now required of all Belts as a field,
  and FMEA is not tracked at all (§3.7.2, §4.10.5). DOE is the only
  belt-gated item, and it belongs to Improve.
