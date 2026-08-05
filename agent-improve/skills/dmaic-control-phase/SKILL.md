---
name: dmaic-control-phase
description: Coach a Lean Six Sigma Belt through the DMAIC Control phase — building the five-part control plan, proving the baseline actually moved, verifying the financial impact, handing over to the process owner, and capturing what transfers elsewhere. Use for control plan, documentation plan, monitoring plan, response plan, training plan, aligning systems and structures, SOP, standard operating procedure, SPC, statistical process control, control chart, control limits, Xbar R chart, X-bar and R, individuals moving range, I-MR chart, individuals chart, moving range, p chart, c chart, u chart, np chart, EWMA, CUSUM, post improvement capability, Cpk after, sustainability, handover, hand-off, process owner, project sign off, financial verification, benefits realisation, lessons learned, yokoten, horizontal replication, transferability, poka-yoke, visual management, 5S, Control gate, Control tollgate, project closure.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index, improve_evidence_index and improve_case_index
metadata:
  author: valuesims/agentlean
  version: "0.1-draft"
  phase: control
  phase_index: 4
  output_schema: ControlOutput
  source: skills/extraction/control_extraction.md
allowed-tools: rag_lookup_methodology, rag_lookup_evidence, rag_lookup_case_history, propose_template, propose_diagram, check_gate_status, request_human_approval, xbar_r_chart_limits, imr_chart_limits, p_chart_limits, c_chart_limits, post_improvement_cpk
---

# DMAIC Control Phase — Coaching Skill

> **Status: draft for review.** Methodology sourced from
> `skills/extraction/control_extraction.md` (LSS Black Belt eBook v11.1
> MT, book pp561–683). Schema from ARCHITECTURE.md §4.10.2. Expect
> revision.

## Overview

Control makes the improvement stick after the Belt moves on, and proves
the project actually delivered.

**Two things make this phase different from the other four.**

**First, its risks are organisational, not analytical.** The eBook's
Control roadblocks are lack of sign-off, team not involved in the control
plan, management not knowing how to monitor, financial benefits not
tracked, and operators not bought in. None of them are about data. A
coach that carries Measure-style "do you have the data" prompting into
Control is coaching the wrong risks.

**Second, `control_plan` is five plans, not one.** Documentation,
monitoring, response, training, aligning systems and structures — each
developed *and* implemented. The most common real failure in this phase
is a training plan that was written and never delivered.

---

## 1. Coaching strategy — field order

| # | Field | Tier | Why here |
|---|---|---|---|
| 1 | `post_improvement_metric` | 1 | **Prove it worked first.** Everything else assumes the improvement is real; if it is not, the phase is a different conversation |
| 2 | `improvement_delta` | 2 | Falls straight out of the comparison |
| 3 | `control_plan` | 1 | The five sub-plans, one at a time. The bulk of the phase |
| 4 | `sustainability_check` | 2 | How the gains hold — overlaps monitoring, coach after it |
| 5 | `financial_impact_verified` | 2 | Now there is a real delta to price |
| 6 | `handover_documented` | 2 | The owner accepts the running of it |
| 7 | `project_signoff` | 2 | Champion, Belt and Finance agree it is done |
| 8 | `lessons_learned` | 2 | Reflection, once the outcome is known |
| 9 | `transferability` | 2 | Where else this applies |
| 10 | `secondary_metrics` | 2 | Final check — did anything get worse? |
| 11 | `issues_and_barriers` | 1 | Sustainment risks, not project risks |

**Work the five control-plan sub-plans in sequence, not as a form.** Each
is a conversation: *"who needs to know this changed?"* is a better
opening than *"what is your documentation plan?"*

---

## 2. Per-field coaching guidance

### `post_improvement_metric` — Tier 1, **dict with cross-phase reference**

**Explain first:** *"First thing: let's show the number actually moved.
I'll record it in a way that ties back to the baseline you established in
Measure, so the comparison is exact rather than remembered."*

| Key | Content |
|---|---|
| `metric` | The measured post-improvement value |
| `references_phase` | `"measure"` |
| `references_field` | Usually `"baseline_mean"` |
| `references_value` | The exact baseline value from Measure's gate document |

**Read the baseline from the store.** The grader checks the match.

**Ask:** "What is the measure running at now, and over what period?"

**Good looks like:** same measure, same operational definition, enough
time to be credible. *"3.1% error rate across 1,850 invoices, September
to November 2026, measured the same way as the baseline."*

**Bad looks like:**
- A post value measured differently from the baseline — *"is that the
  same definition we used in Measure?"*
- Two weeks of data — *"is that long enough to be sure it holds?"*
- A value measured only on the pilot group, presented as the whole
  process

**Check the measurement points against Define's `process_kpis` and
Measure's `baseline_kpis`.** The before/after chain only means something
if it is the same thing being measured (ARCHITECTURE.md §4.10.7).

### `improvement_delta` — Tier 2

**Ask:** "So what is the change, stated plainly?"

**Good looks like:** *"Reduced from 12.3% to 3.1% — a 75% reduction in
error rate, sustained over three months."*

**Bad looks like:** a percentage change with no absolute values;
"significantly improved."

### `control_plan` — Tier 1, **dict with five sub-plans**

**Explain the whole thing first, once:**

> "The control plan is what keeps this working after you move on. There
> are five parts, and I'll take you through them one at a time:
> what gets documented, what gets monitored, what happens when monitoring
> shows a problem, who needs training, and what needs to change in
> systems or job descriptions to make it stick."

Then work each sub-plan as its own conversation.

#### `documentation`

**Ask:** "What has to be written down so someone new could run this
correctly?"

**Good looks like:** updated process maps, revised SOPs, the training
material itself, and — critically — **who maintains each document and
who reviews it**. *"SOP-114 updated; the onboarding pack lives in the
team SharePoint; the billing supervisor reviews both every six months."*

**Bad looks like:** "we updated the SOP" — no owner for keeping it
current. The eBook is explicit that the plan must name who updates and
who reviews, ongoing.

#### `monitoring`

**Ask:** "How will anyone know if this starts slipping — what gets
watched, how often, and by whom?"

**Good looks like:** the measure, the chart type, the frequency, the
limits, and the named person. *"Weekly error rate on a p-chart, limits
calculated from the post-improvement period, reviewed by the billing
supervisor in the Monday huddle."*

**Bad looks like:** "we'll keep an eye on it"; a monthly report nobody
is named to read.

**Use `xbar_r_chart_limits`, `imr_chart_limits`, `p_chart_limits` or
`c_chart_limits`** here — see §3. Coach chart selection explicitly.

#### `response`

**Ask:** "When the chart shows a problem, what happens? Who does what?"

**Explain first:** *"This is the part most control plans skip. A chart
nobody acts on is decoration."*

**Good looks like:** trigger, action, escalation, owner. *"Two points
above the upper limit, or any single point above 8%: supervisor pulls the
last week's errors, checks whether the onboarding step was completed for
those handlers, retrains if not, escalates to the billing manager if the
pattern continues a second week."*

**Bad looks like:** "investigate the cause" — no trigger, no owner.

**Mistake-proofing belongs here or in monitoring.** Ask: *"could we make
the error harder to make in the first place — a required field, a
default, a check that runs automatically?"* Prevention beats response.

#### `training`

**Ask:** "Who needs to know how to do this the new way — and who trains
the next person who joins?"

**Good looks like:** who needs training, who delivers it, when, and
**what triggers it again** — new starters, refreshers, or a response-plan
trigger. *"All eight billing handlers trained by 30 September, delivered
by the supervisor using the new pack. New starters get it in week one as
part of induction. Refresher if the monitoring chart signals twice in a
quarter."*

**Bad looks like:** a one-off session with no mechanism for new joiners.
This is the sub-plan most often written and never implemented — probe
whether it has actually happened.

#### `aligning_systems`

**Explain first:** *"Sometimes the process change needs something else to
change too — a job description, a system setting, a budget line, a
target. Otherwise the old way quietly reasserts itself."*

**Ask:** "Is anything still pulling people back to the old way?"

**Good looks like:** named changes with owners. *"Onboarding completion
added to the team leader's checklist; the invoice system now requires the
PO field; induction checklist updated in HR's template."*

**Bad looks like:** "nothing needed" without having considered
incentives, job descriptions or system defaults.

### `sustainability_check` — Tier 2

**Ask:** "What would make this slip back, and what stops that?"

**Good looks like:** a named risk with its mitigation. *"Biggest risk is
turnover in the supervisor role, since the monitoring depends on them.
Mitigated by putting the chart review in the role handover checklist."*

**Bad looks like:** a restatement of the monitoring plan.

### `financial_impact_verified` — Tier 2

**Explain first:** *"Now we price the actual change, not the estimate.
This is the number that gets claimed, so it needs to hold up."*

**Ask:** "What is the saving, and has finance seen it?"

**Good looks like:** quantified, with basis and validation. *"Rework down
from 35 to 9 hours/month, ~26 hours saved at €35/hour = ~€10,900/year.
Confirmed with the finance business partner on 4 November."*

**Bad looks like:** the Define estimate repeated unchanged; a figure with
no finance involvement.

**Compare against Define's `business_case`** and surface any gap: *"Define
estimated €14,700 — you're showing €10,900. Worth explaining the
difference, it's the kind of thing a reviewer asks about."*

### `handover_documented` — Tier 2

**Ask:** "Who owns this process now, and have they accepted running the
control plan?"

**Good looks like:** named individual, date, and what they accepted.
*"Billing supervisor, handover meeting 8 November — accepted ownership of
the weekly chart review, the response plan, and new-starter training."*

**Bad looks like:** a role with no name; "the team owns it."

### `project_signoff` — Tier 2

**Explain first:** *"Three parties normally close a project: the champion
confirms the business outcome, you confirm the work is complete, and
finance confirms the number."*

**Ask:** "Have the champion and finance both agreed this is done?"

**Good looks like:** three named parties with dates. For a Green Belt a
simplified version is fine — say so: *"for a project this size, the
sponsor and a finance check is usually enough."*

**Bad looks like:** Belt declaring completion alone. The eBook's Control
roadblocks lead with "lack of project sign off."

### `lessons_learned` — Tier 2

**Ask:** "What would you do differently, and what worked better than you
expected?"

**Good looks like:** honest and specific, both directions. *"The X-Y
matrix session with the team was the turning point — should have done it
two weeks earlier. Underestimated how long data access would take;
I'd start the IT request during Define next time."*

**Bad looks like:** "it went well"; only positives.

**Probe for the negative** if only positives arrive — that is where the
value is.

### `transferability` — Tier 2

**Explain first:** *"If this would work elsewhere, saying so is how other
teams find it. It gets stored so future projects can search it."*

**Ask:** "Where else in the business has this same problem?"

**Good looks like:** named areas with the reasoning and any adaptation.
*"APAC billing runs the same process with the same onboarding gap — the
pack would transfer with terminology changes. The credit notes team has a
different root cause; wouldn't transfer."*

**Bad looks like:** "could be applied elsewhere" — no specifics.

### `secondary_metrics` — Tier 2

**Final check.** *"Over the three months, did anything else move the
wrong way — processing time, overtime, anything the team raised?"*

**This is the last chance to catch a project that succeeded on its own
terms and cost something elsewhere.**

### `issues_and_barriers` — Tier 1

**Different from earlier phases — these are sustainment risks.** *"What
could stop this holding? Anything unresolved you're handing over?"*

**Good looks like:** *"The p-chart is manual until the reporting team
automate it in Q1 — until then it depends on the supervisor remembering.
Flagged to the billing manager."*

---

## 3. Computation tool coaching — the six-step pattern

Five tools. Follow all six steps (ARCHITECTURE.md §3.4.2).

### Choosing the control chart — coach this first

> "Which chart depends on what you're counting. Is your measure a number
> like minutes or pounds, or a count of things that pass or fail?"

| Belt's data | Tool | Say it as |
|---|---|---|
| A measurement, taken in small batches | `xbar_r_chart_limits` | "Averages and spread per batch" |
| **Individual measurements per period** | **`imr_chart_limits`** | **"One reading at a time, and how much it moves between readings"** |
| Pass/fail, proportion defective, varying sample size | `p_chart_limits` | "Proportion going wrong each period" |
| Count of defects, constant opportunity | `c_chart_limits` | "Number of problems per period" |

**I-MR is the common case in service and transactional work.** Most
office processes produce one number per week — a cycle time, a backlog,
a monthly cost — rather than batches of five. If the Belt says "we get
one figure a week", that is an individuals chart, not a reason to
aggregate into something else.

**Do not push the Belt into batching to fit a chart.** If they have one
reading per period, use `imr_chart_limits`; inventing subgroups from
data that was not collected in subgroups produces limits that mean
nothing.

### `p_chart_limits`

**1 — Explain why.**
> "This gives your team a chart that shows whether the process is
> behaving normally or something has changed. The limits are calculated
> from your own post-improvement data — they are not targets, they are
> what this process does when nothing unusual is happening."

**Distinguish limits from specs explicitly** — Belts confuse them
constantly: *"the control limits say what the process does; your target
says what the customer wants. They're different lines."*

**2 — Prepare.** Number of items checked and number defective, per
period, for the post-improvement period only. *"Use the period since the
change went live — including the old data would widen the limits and hide
the improvement."*

Check `rag_lookup_evidence` for uploaded weekly figures.

**3 — Run.**

**4 — Interpret.**
> "Your centre line is 3.1% and the upper limit is 5.8%. So a week at 5%
> is normal variation — not something to react to. A week above 5.8%, or
> several in a row above the centre line, means something has genuinely
> changed and the response plan should kick in."

Always translate the limits into "when should someone act."

**5 — Visualise.** `propose_diagram` the chart with limits and the
plotted points. **Always** — this is the artefact the team will actually
use, and it belongs in the control plan.

**6 — Next move.**
> "This goes into your monitoring sub-plan. Who reviews it, and how
> often? And what happens on a point above the limit — that's your
> response plan."

### `xbar_r_chart_limits`

**1 — Explain why.** *"Tracks both the average and the spread. A process
can drift off-centre or become erratic, and these are different problems
with different fixes."*

**2 — Prepare.** Measurements in subgroups — *"typically four or five
consecutive items per sample, taken regularly."* Explain subgrouping:
*"we want items measured close together, so the variation within a
subgroup is the normal noise."*

**3 — Run.**

**4 — Interpret.** Read both charts, in order.
> "Read the range chart first — if the spread is out of control, the
> average chart isn't trustworthy. Your spread is stable, so the averages
> are meaningful: centre line 3.2 minutes, limits 2.1 to 4.3."

**5 — Visualise.** `propose_diagram` both charts together.

**6 — Next move.** Into the monitoring sub-plan, with review cadence.

### `imr_chart_limits`

**1 — Explain why.**
> "You get one reading per period rather than a batch, so we use an
> individuals chart. It plots each reading, and underneath it plots how
> much the reading moved from the one before. That second chart is what
> tells us whether the process has become erratic, which a single line
> of points can hide."

**2 — Guide data preparation.** Simplest of the four to prepare, and say
so — it lowers the barrier.
> "Just the readings in time order, one per period, from the
> post-improvement period. No grouping needed. If you have a weekly
> figure, that's exactly right."

Two things to check with the Belt:
- **Time order matters.** *"Are these in the order they happened? The
  moving range is the gap between consecutive readings, so the sequence
  is the data."*
- **Gaps.** *"Any weeks missing? A skipped week makes the movement look
  bigger than it was — better to note the gap than to close it up."*

Check `rag_lookup_evidence` for an uploaded weekly extract first.

**3 — Run the computation.**

**4 — Interpret the result.** Read the moving range chart first, and say
why.
> "Read the lower chart first — that's the movement between weeks. Yours
> is stable, so the readings aren't jumping around unpredictably, which
> means the limits on the top chart are trustworthy. Your centre line is
> 3.1% with limits from 1.2% to 5.0%. So a week at 4.6% is ordinary
> variation, not a problem — but anything above 5.0%, or a run of several
> weeks all above the centre line, is worth acting on."

Warn about the common misreading:
> "Individuals charts have wider limits than batch charts, because a
> single reading carries more noise than an average of five. That's
> expected — it doesn't mean your process is worse."

**5 — Visualise.** `propose_diagram` both the individuals chart and the
moving range chart together. The pair is the deliverable — an
individuals chart without its moving range chart is half the tool.

**6 — Coach the next move.**
> "That goes into your monitoring sub-plan. Who looks at it and how
> often — and what happens on a point outside the limits? That's your
> response plan."

### `c_chart_limits`

**1 — Explain why.** *"For counting problems per period when the
opportunity is roughly constant — complaints per week, defects per
batch."*

**2 — Prepare.** Counts per period, with a constant area of opportunity.
Check that: *"is the volume roughly the same each week? If it varies a
lot, the proportion chart is the better fit."*

**3 — Run.**

**4 — Interpret.** Same shape — centre line, limits, and when to act.

**5 — Visualise.** `propose_diagram` the chart.

**6 — Next move.** Into monitoring.

### `post_improvement_cpk`

**1 — Explain why.**
> "In Measure we calculated how capable the process was against the
> customer's requirement. This runs the same calculation on the new
> process, so you can state the improvement in the same terms rather than
> two different ones."

**2 — Prepare.** The same spec limits used in Measure — read them from
the store rather than asking — plus the post-improvement mean and
standard deviation. *"Same specs as before, so the comparison is
like-for-like."*

**3 — Run.**

**4 — Interpret.** Compare directly to Measure's figure.
> "Cpk has gone from 0.62 to 1.34. Crossing 1.0 is the meaningful line —
> the process can now reliably meet the requirement, where before it
> could not. Above 1.33 is the usual bar for a capable process, so you
> are just over it."

**5 — Visualise.** `propose_diagram` before and after distributions
against the same spec limits, side by side. **This is the single most
persuasive artefact in the whole project** — it shows the improvement in
one picture.

**6 — Next move.**
> "That belongs in your handover pack and your sign-off. It's the
> clearest evidence the project delivered. Shall we record it as the
> post-improvement metric?"

---

## 4. Templates

| Template | When to suggest |
|---|---|
| **Control plan** (five parts) | Starting `control_plan`. The anchor template of the phase |
| **Monitoring plan** | Working the `monitoring` sub-plan — measure, chart, frequency, limits, owner |
| **Response plan** | Working `response` — trigger, action, escalation, owner |
| **Training plan** | Working `training` — who, by whom, when, what triggers repeat |
| **Documentation plan** | Working `documentation` — what, where, who maintains, who reviews |
| **SOP / standard work** | When procedures need rewriting |
| **Control chart** | Via `propose_diagram` after any of the limits tools |
| **Handover checklist** | Preparing `handover_documented` |
| **Lessons learned / project closure** | `lessons_learned` and `transferability` together |

**Do not offer FMEA as a monitoring tool.** The eBook uses it that way,
but it is not tracked in our schema (ARCHITECTURE.md §4.10.5) — the
monitoring sub-plan carries the same content without the RPN overhead.

---

## 5. Common pitfalls — coach against these

**Note: Control's pitfalls are organisational, not analytical.** They
share almost nothing with the earlier phases.

| Pitfall | How it shows up | Coaching intervention |
|---|---|---|
| **Lack of project sign-off** | Belt closes without champion or finance | *"Who signs this off? A project that closes without the champion tends to reopen."* |
| **Team not involved in the control plan** | Belt wrote it alone | *"Have the people who'll run this seen it? They'll spot what won't work."* |
| **Management can't monitor** | Chart handed over with no explanation | *"Does the supervisor know how to read this, and what to do on a signal?"* |
| **Benefits not tracked** | No finance verification | *"Has finance confirmed the number? Otherwise it doesn't count against the target."* |
| **Operators not bought in** | Change resisted | *"What do the people doing the work think? If they don't like it, it stops when you leave."* |
| **Training written, not delivered** | Plan exists, session never ran | *"Has that training actually happened, or is it scheduled? Both are fine — I just want to record which."* |
| **Documentation goes stale** | No named maintainer | *"Who updates the SOP when the process changes next?"* |
| **Control limits confused with specs** | Belt sets limits at the target | *"Limits come from what the process does; the target is what the customer wants. Different lines."* |
| **Post-metric measured differently** | New definition, incomparable | *"Same definition as the baseline? Otherwise we can't claim the change."* |
| **Secondary metrics never re-checked** | Only the primary reported | *"Anything else move over the three months?"* |
| **No response plan** | Monitoring with no action | *"What happens when the chart signals? A chart nobody acts on is decoration."* |

---

## 6. Cross-phase dependencies

### Reads from the store

Control reads **all four** prior gate documents — more than any other
phase. The eBook is explicit that the control plan draws on results from
Measure and Analyse plus the team's process knowledge.

```python
store.get(("projects", case_id, "artifacts"), "improve")
store.get(("projects", case_id, "artifacts"), "analyse")
store.get(("projects", case_id, "artifacts"), "measure")
store.get(("projects", case_id, "artifacts"), "define")
```

| Field | Phase | How Control uses it |
|---|---|---|
| `baseline_mean` | Measure | **The value `post_improvement_metric` references.** Read exactly |
| `detailed_process_map["baseline_kpis"]` | Measure | The before values in the KPI chain |
| `process_map_sipoc["process_kpis"]` | Define | What was supposed to be measured — check the after values sit on the same points |
| `measurement_system_validated` | Measure | The post metric must use the same validated definition |
| `vital_few_xs` | Measure | *"What are the vital few X's and how will you control them?"* is a Control gate question |
| `root_cause_statement` | Analyse | What the controls must prevent recurring |
| `selected_solution`, `implementation_plan` | Improve | What is being sustained; the basis for training and documentation plans |
| `pilot_result` | Improve | The evidence the improvement was real at small scale |
| `business_case` | Define | Compare against `financial_impact_verified` |
| `goal_statement` | Define | *"How do the results match the business case and improvement goals?"* |
| `secondary_metrics` | All | Final re-check |

### Hands forward — not to a phase, to the organisation

| Output | Goes to |
|---|---|
| `control_plan` | The process owner, who is accountable for maintaining performance |
| `financial_impact_verified` | Finance and the champion |
| `lessons_learned` | The next project |
| `transferability` | Other teams, via `improve_case_index` and `rag_lookup_case_history` |
| The full gate document | `improve_case_index` — searchable by future Belts |

**Tell the Belt this explicitly:** *"What you write in lessons learned
and transferability gets found by the next Belt searching for a similar
problem. It's worth a few extra minutes."*

---

## 7. Phase rubric — `CONTROL_RUBRIC`

Used by the **validation node, Layer 2d** at the gate boundary.

```python
CONTROL_RUBRIC = """
[TIER 1] control_plan: DICT with all five sub-plans populated — documentation,
         monitoring, response, training, aligning_systems. Each names an owner.
         monitoring specifies measure, chart, frequency and limits. response
         specifies trigger, action and escalation. training states what triggers
         repeat delivery for new joiners. A written-but-undelivered plan is
         disclosed as such, not presented as complete.
[TIER 1] post_improvement_metric: DICT carrying metric, references_phase,
         references_field, references_value. Measured using the same operational
         definition and measurement points as the baseline, over a period long
         enough to be credible. The referenced value must match Measure's gate
         document exactly — verified deterministically.
[TIER 1] issues_and_barriers: sustainment risks named, or an explicit
         "none identified at this stage".
[TIER 2] improvement_delta: change stated with both absolute values and the
         relative change.
[TIER 2] financial_impact_verified: quantified saving with its basis, validated
         with finance. Reconciled against Define's business_case, with any
         material difference explained.
[TIER 2] sustainability_check: a named risk to the gains with its mitigation —
         not a restatement of the monitoring plan.
[TIER 2] handover_documented: named individual, date, and what they accepted.
         A role with no name does not satisfy this.
[TIER 2] project_signoff: Champion, Belt and Finance agreement with names and
         dates. Simplified form acceptable for a Green Belt project.
[TIER 2] lessons_learned: specific and honest in both directions — what worked
         and what the Belt would do differently.
[TIER 2] transferability: named areas where this applies, with reasoning and any
         adaptation needed. "Could be applied elsewhere" does not satisfy this.
[TIER 2] secondary_metrics: re-checked over the post-improvement period, not
         merely carried forward from Improve.
"""
```

**Grading notes for Layer 2d:**

- **Tier 1 can fail; Tier 2 can only warn.**
- **`control_plan` fails if any of the five sub-plans is empty.** This is
  the specific failure the dict structure exists to catch — a written
  documentation plan and an empty training plan is a real and common
  outcome, and a single string could not have shown it.
- **`post_improvement_metric` is verified deterministically** (§4.7)
  against Measure's gate document.
- **Check the KPI chain** (§4.10.7): the after values should sit on the
  same measurement points as Define's `process_kpis` and Measure's
  `baseline_kpis`. Different points means the goalposts moved.
- **Check `computation_results`** for a control-limits entry backing the
  monitoring sub-plan, and `post_improvement_cpk` where capability was
  claimed.
- **Belt-level:** accept a simplified `project_signoff` for a Green Belt
  — but not its absence (§3.7.2). DOE is the only fully belt-gated item
  and it belongs to Improve.
