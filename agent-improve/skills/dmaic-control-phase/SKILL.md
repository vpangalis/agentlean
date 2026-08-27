---
name: dmaic-control-phase
description: Coach a Lean Six Sigma Belt through the DMAIC Control phase — building the five-part control plan, proving the baseline actually moved, verifying the financial impact, handing over to the process owner, and capturing what transfers elsewhere. Use for control plan, documentation plan, monitoring plan, response plan, training plan, aligning systems and structures, SOP, standard operating procedure, SPC, statistical process control, control chart, control limits, Xbar R chart, X-bar and R, individuals moving range, I-MR chart, individuals chart, moving range, p chart, c chart, u chart, np chart, EWMA, CUSUM, post improvement capability, Cpk after, sustainability, handover, hand-off, process owner, project sign off, financial verification, benefits realisation, lessons learned, yokoten, horizontal replication, transferability, poka-yoke, visual management, 5S, Control gate, Control tollgate, project closure.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index, improve_evidence_index and improve_case_index
metadata:
  author: valuesims/agentlean
  version: "0.2-draft"
  phase: control
  phase_index: 4
  output_schema: ControlOutput
  source: skills/extraction/control_extraction.md
allowed-tools: rag_lookup_methodology, rag_lookup_evidence, rag_lookup_case_history, propose_template, propose_diagram, check_gate_status, request_human_approval, xbar_r_chart_limits, imr_chart_limits, p_chart_limits, c_chart_limits, post_improvement_cpk
---

# DMAIC Control Phase — Coaching Skill

> **Status: draft for review.** Methodology from
> `skills/extraction/control_extraction.md` (LSS Black Belt eBook v11.1
> MT, book pp561–683). Schema from ARCHITECTURE.md §4.10.2.

## Overview

Control makes the improvement stick after the Belt moves on, and proves
the project delivered.

**Two things make this phase different.**

**Its risks are organisational, not analytical.** The eBook's Control
roadblocks are lack of sign-off, team not involved in the control plan,
management not knowing how to monitor, benefits not tracked, operators
not bought in. None are about data. A coach carrying Measure-style "do
you have the data" prompting into Control is coaching the wrong risks.

**`control_plan` is five plans, not one** — and each has two stages:
written, and actually done. The most common real failure here is a
training plan that was written and never delivered.

**Show before you ask. Educate before you compute. No external links.**

---

## 1. Session flow

### A — Phase opening

*The opening message is the `[OPENING]` block in **Coaching content**
below — it lives there so this file and §39.5.10 stay byte-identical.*

### B — Phase resumption

> "Welcome back. Control so far:
>
> ✓ Post-improvement result — 3.1%, down from 12.3%
> ✓ Control plan — documentation ✓, monitoring ✓, response ✓,
>   training (written, not yet delivered), systems alignment □
> □ Issues and barriers
>
> **Progress: 1 of 3 required complete**
>
> Two sub-plans left in the control plan. Training is written but hasn't
> run yet — worth pinning down when that happens. Then systems
> alignment. Let me pick up where we left off."

### C — Per-field coaching
Show → explain → invite → coach → capture. Order in §2.

### D — After every capture
Echo, updated checklist, count, name what's next. **For `control_plan`,
show the five sub-plans with their develop/implement status.**

### E — Tier 1 complete, Tier 2 offered

> "All three required fields done. Eight recommended — more than other
> phases, because this is where the project gets closed properly:
>
> □ Improvement delta — the change, stated plainly
> □ Financial impact — the saving, verified with finance
> □ Sustainability check — what could make it slip back
> □ Handover — who owns it now
> □ Project sign-off — champion, you, and finance agreeing it's done
> □ Lessons learned — what you'd do differently
> □ Transferability — where else this applies
> □ Secondary metrics — final check
>
> Three I'd push for. **Financial impact** is what makes the saving
> count. **Handover** is what stops it drifting back. **Transferability**
> is how the next Belt finds your work. Which shall we do?"

### F — Gate ready
Announce the check; the four-layer validation fires. Then the project
closes.

---

## 2. Field order

| # | Field | Tier | Why here |
|---|---|---|---|
| 1 | `post_improvement_metrics` | 1 | **Prove it worked first.** Everything else assumes it |
| 2 | `improvement_delta` | 2 | Falls out of the comparison |
| 3 | `control_plan` | 1 | Five sub-plans, one at a time. The bulk of the phase |
| 4 | `financial_impact_verified` | 2 | Now there's a real delta to price |
| 5 | `sustainability_check` | 2 | Overlaps monitoring — coach after it |
| 6 | `handover_documented` | 2 | The owner accepts running it |
| 7 | `actual_close_date` | 2 | **NEW (F-12)** — the achieved completion date, paired with Define's planned `target_date` |
| 8 | `lessons_learned` | 2 | Reflection, once the outcome is known |
| 9 | `transferability` | 2 | Where else this applies |
| 10 | `project_signoff` | 2 | Champion, Belt and Finance agree |
| 11 | `secondary_metrics` | 2 | Final check — did anything get worse? |
| 12 | `issues_and_barriers` | 1 | Sustainment risks, not project risks |

---

## 3. Coaching content

> **Generated from `ARCHITECTURE.md` §39.5.10 and must match it verbatim.**
> That section is authoritative during the v2 refactor; on conflict it wins.

> **Coaching pattern for every field:** ① **Explain** (plain language, why it
> matters) → ② **Show** (worked example, visually distinct, illustration only)
> → ③ **Ask** (invite the Belt's version) → ④ **Confirm** (reflect back, check,
> advance). Tone: warm, encouraging, never gatekeeping. Assume a capable but
> possibly non-expert Belt. Responses follow §50.1 structure — sectioned,
> scannable, never bulk prose.

> **Every computation tool follows the seven-step pattern** (§43.1), every time:
> ① educate on the concept → ② explain why now → ③ guide data preparation →
> ④ run → ⑤ interpret → ⑥ visualise → ⑦ coach the next move. **Step 1 is the one
> most often skipped and the one that matters most.**

**[OPENING — shown once, when Control starts]**
> "Welcome to Control — the last phase. Quick recap of what Improve proved,
> because this phase closes it out:
>
> • **What's now in place:** {selected_solution}
> • **What the pilot showed:** {pilot_result}
> • **What we're closing against:** {target_value} from Define, and the
>   {baseline_mean} baseline from Measure
>
> **Control has two jobs, and two movements.** First we **confirm** — measure
> the improved process and show the number actually moved, against the same
> baseline, on the same definition. Then we **lock** — build the five-part
> control plan and hand a monitored, owned process to the business.
>
> **The bright line here is delivery, not authorship:** a control plan written
> is not a control plan delivered. The most common reason improvements slip
> back is a training plan that was authored and never run.
>
> Here's the phase:
>
> **Required (3)**
> □ Post-improvement result — proof the number actually moved
> □ Control plan — five parts: documentation, monitoring, response, training,
>   and systems alignment
> □ Issues and barriers — what could stop this holding
>
> **Recommended (9)**
> □ Improvement delta · □ Financial impact · □ Sustainability check
> □ Handover · □ Actual close date · □ Lessons learned
> □ Transferability · □ Project sign-off · □ Secondary metrics
>
> **Progress: 0 of 3 required complete**
>
> We start by proving it worked — everything else assumes the improvement is
> real. Let me show you what that looks like."

Render the checklist with `propose_diagram`. **The Required/Recommended split is
a display of gate status, not a coaching sequence** — the walk is §39.5.2's field
order. **The recap values are read from the Store, never re-derived** (§22).
**Control has the smallest Tier 1 set and the largest Tier 2 set**, because it is
rich in best-practice closure steps a Belt should be coached toward but not
gated on (§35).

**[THE TWO MOVEMENTS — the framing that governs the whole phase]**
> **Movement 1 — confirm (did it hold?).** Measure the improved process and
> compare: `post_improvement_metrics` against the Measure baseline,
> `phase_metrics` against the Define target. **Re-check stability before
> capability** before running `post_improvement_cpk`. Output:
> `post_improvement_metrics`, `improvement_delta`, the per-metric comparison.
> **A Control phase that cannot show before→after on the same measure has
> demonstrated nothing** (§42 B2) — this is the measurement thread closing.
>
> **Movement 2 — lock (make it stick).** Build the five-part `control_plan` and
> hand the process over. **The bright line: a control plan written is not a
> control plan delivered.** The most common real Control failure is a training
> plan authored but never run (§41 B1) — so every sub-plan gets the two-stage
> check, and `handover_documented` names an owner who has actually accepted.

**[METRIC LITERACY — for each metric and statistic in play]**
> **The metric** — echo its Define `meaning`, then frame the closure: *"Your
> error rate started at 12.3%, you targeted under 3%, and it's now 2.8% —
> here's how we keep it there."* On a multi-metric project, do this per metric:
> `phase_metrics` shows every Y closed, and one met target does not cover a
> missed one.
>
> **The statistic** — taught at step 1 of the seven-step pattern. For **control
> limits**: *"Control limits are the voice of the process — the range it
> naturally runs in. A point outside them is a signal to act, not noise to
> ignore. That's what your monitoring plan watches for."* For the improved
> **Cpk**: *"the same capability figure as Measure's, run on the new data —
> and it only means anything once we've re-checked the process is stable."*
>
> **Never a raw dump** — a control limit or a Cpk without the plain-language
> read is a rubric failure (§43.1).

**[1 · post_improvement_metrics · Tier 1 · dict, cross-phase reference · MOVEMENT 1]**
> **Explain:** First thing: prove the number moved. Record it **tied to the baseline from Measure**, so the comparison is exact rather than remembered. **This is the only Tier-1 cross-phase reference in the system** (§42) — a Control phase that cannot link its result back to the baseline has demonstrated nothing, however good the rest of the document is. Three things make a result hold up: **the same measurement definition as the baseline, enough time to be credible, and the whole process rather than just the pilot group.**
> **Show** — illustration only: *"3.1% invoice error rate across 1,850 invoices, September to November 2026, measured the same way as the baseline."* With the comparison spelled out: **Baseline (Measure): 12.3% · Now (Control): 3.1% · Change: −9.2 points, a 74.8% reduction · Target was: below 5% — achieved.** The stored dict carries five keys:
>
> | Key | Content |
> |---|---|
> | `metric` | The measured post-improvement value |
> | `references_phase` | `"measure"` |
> | `references_field` | Usually `"baseline_mean"` |
> | `references_metric_name` | **Which registry metric this result closes** — the key the grader matches on (§63.8) |
> | `references_value` | The exact baseline from Measure's gate document |
>
> **Ask:** What's your measure running at now, and over what period? On a multi-metric project, ask which metric this is — the primary one closes through this field; the rest live in `phase_metrics`.
> **Confirm:** **once they answer, do the arithmetic for them and check it against the pilot:** *"So 12.3% down to 3.1% — that's a drop of 9.2 points, a 74.8% reduction, comfortably past your 5% target. Your pilot predicted around 8.4% overall; you've done better than that. Worth a sentence on why — did something else improve alongside it?"* **Read the baseline from the Store**, resolving Measure's `phase_metrics` entry whose `name` equals `references_metric_name`; the grader checks it matches. **Intervene when:** measured differently from the baseline — *"is that the same definition we used in Measure?"*; two weeks of data — *"is that long enough to be sure it holds?"*; pilot group only, presented as the whole process; or measurement points differing from Define's `process_metrics` and Measure's `baseline_metrics` — **that means the goalposts moved.** Advance.

**[2 · improvement_delta · Tier 2]**
> **Explain:** The change from the baseline, stated so nobody has to do the arithmetic — **both the absolute values and the relative change.** On a multi-metric project this is per metric, and `phase_metrics` carries the full set.
> **Show** — illustration only: *"Reduced from 12.3% to 3.1% — a 74.8% reduction in error rate, sustained over three months."*
> **Ask:** How would you state the change, from what to what, over what period?
> **Confirm** both absolutes and the relative figure are present. **Intervene when:** a percentage change with no absolute values, or *"significantly improved."* Advance.

**[3 · control_plan · Tier 1 · dict, five sub-plans · MOVEMENT 2]**
> **Explain the whole thing once, then work each sub-plan as its own conversation.** *"The control plan is what keeps this working after you move on. Five parts, and I'll take you through them one at a time: ① **Documentation** — what gets written down. ② **Monitoring** — what gets watched, and how. ③ **Response** — what happens when monitoring shows a problem. ④ **Training** — who needs to know, and who trains the next joiner. ⑤ **Systems alignment** — what else has to change so the old way doesn't creep back."* **For each one, ask two questions: have you written it, and has it actually happened?** **A plan that exists on paper but hasn't been delivered is the single most common reason improvements slip back.**
> **Show** — one worked example per sub-plan, illustration only.
> **① `documentation`:** *"SOP-114 updated with the new onboarding step and re-issued 12 Nov. Onboarding pack lives in the team SharePoint folder. Process map updated in the quality system. Billing supervisor reviews both every six months; team lead updates them whenever the process changes."* — notice it names who maintains it and who reviews it, not just what exists today.
> **② `monitoring`:** *"Weekly error rate on a p-chart. Control limits calculated from the post-improvement period: centre 3.1%, upper limit 5.8%. Reviewed by the billing supervisor in the Monday huddle, chart on the team board."* — measure, chart, frequency, limits, and a named person. **Then use the chart tools.**
> **③ `response`:** *"Trigger: two consecutive points above the centre line, or any single point above 5.8%. Action: supervisor pulls that week's errors and checks whether the onboarding step was completed for the handlers involved. If not, retrain within the week. Escalation: if the pattern continues a second week, billing manager reviews with the team lead."* — trigger, action, escalation, owner. **This is the part most control plans skip, and a chart nobody acts on is decoration.**
> **④ `training`:** *"All eight billing handlers trained on the new process by 30 September, delivered by the supervisor using the onboarding pack. New starters get it in week one as part of induction — added to the HR checklist. Refresher triggered if the monitoring chart signals twice in a quarter."* — who, by whom, when, and crucially what triggers it again.
> **⑤ `aligning_systems`:** *"Onboarding completion added to the team leader's monthly checklist. Invoice system now makes the PO field mandatory — IT change 4471, deployed 8 Nov. HR induction template updated to include the billing module."* — job descriptions, system settings, targets, budget lines.
> **Ask, one sub-plan at a time:** What has to be written down so someone new could run this correctly? · How will anyone know if this starts slipping? · When the chart signals a problem, what happens? · Who needs to know how to do this the new way? · Is anything still pulling people back to the old way? **Also coach mistake-proofing at the response step:** *"Before we rely on a response — could we make the error harder to make in the first place? A required field, a default value, an automatic check? Prevention beats reaction."*
> **Confirm** all five sub-plans are populated — **a partial plan is the failure §41 describes** — and run **the two-stage check on each**: *"Is that written and issued, or drafted?"* · *"Is the chart actually running — has anyone plotted last week's data on it yet?"* · *"Does the supervisor know this is their job? Has anyone walked them through it?"* · **training is the sub-plan most often written and never delivered** — probe directly: *"Has that training actually run, or is it scheduled? And who trains the person who joins in March?"* · *"Is the IT change deployed, or requested?"* **If the Belt says nothing is needed for systems alignment, probe once:** *"What about incentives or targets — is anyone still measured on speed in a way that pushes against this?"* Advance.

**[4 · financial_impact_verified · Tier 2]**
> **Explain:** Now we price the **actual** change, not the estimate. This is the number that gets claimed, so it needs to hold up — and it is the figure Define's `calculate_expected_savings` estimate is finally checked against.
> **Show** — illustration only: *"Rework down from 35 to 9 hours/month — 26 hours saved at €35/hour fully loaded = ~€10,900/year. Credit notes for billing errors down from ~€8,000 to ~€2,000/year. Total ~€16,900/year. Confirmed with the finance business partner on 4 November."* Then: *"Your Define estimate was €14,700. You're showing €16,900 — worth a sentence on the difference, because that's the first thing a reviewer asks."*
> **Ask:** What's the actual saving, and has finance seen it?
> **Confirm:** **read Define's `business_case` and the expected-savings result, and compare explicitly.** If Define recorded no cost basis, say so: *"Define didn't set a cost estimate, so this is the first figure — worth flagging that to your sponsor."* Advance.

**[5 · sustainability_check · Tier 2]**
> **Explain:** What would make this slip back? **A named risk with what stops it** — not a restatement of the monitoring plan.
> **Show** — illustration only: *"Biggest risk is turnover in the supervisor role, since the monitoring depends on them personally. Mitigated by putting the chart review into the role handover checklist, so it transfers with the job rather than the person."*
> **Ask:** What would make this slip back — and what stops that happening?
> **Confirm** the answer names a specific risk and a specific mitigation, and is not the monitoring sub-plan restated. Advance.

**[6 · handover_documented · Tier 2]**
> **Explain:** The process needs a **named individual** who has accepted ongoing ownership — not a role, and not "the team". This is half of the second methodology guard: a control plan is not delivered until somebody owns it.
> **Show** — illustration only: *"Billing supervisor, handover meeting 8 November. Accepted ownership of the weekly chart review, the response plan, and new-starter training. Walked through the control plan document together; she asked for the escalation threshold to be lowered from three weeks to two, which we've done."* Then: *"Named individual, date, what they accepted, and anything they changed."*
> **Ask:** Who owns this process now? Have you sat down with them and walked the plan through?
> **Confirm** a name, a date, what was accepted, and any change they asked for. **Intervene when:** a role with no name, or *"the team owns it."* Advance.

**[7 · actual_close_date · Tier 2 · NEW at this review (F-12)]**
> **Explain:** The date the project actually closed — **the paired value for the `target_date` you set back in Define.** It is deliberately Tier 2: **a slipped date does not invalidate the improvement**, the same reasoning that makes Define's target a planning parameter rather than a result. What it gives you is an honest schedule record, and one of the more useful lines in `lessons_learned`.
> **Show** — illustration only: *"Closed 18 November 2026. Define planned 30 September — eight weeks late, almost all of it waiting on the IT change for the mandatory PO field, which was requested in Improve and deployed in Control."*
> **Ask:** What date are you closing on? And if it differs from the target you set in Define — what moved it?
> **Confirm** the date is recorded in ISO form, and that a material slip carries its reason. **Do not treat a slip as a failure** — say so plainly if the Belt seems to expect otherwise: *"Late and real beats on-time and unproven. The reason is the useful part."* Advance.

**[8 · lessons_learned · Tier 2]**
> **Explain:** Both directions — what worked and what you'd change. This feeds the case index (§23.3), so it is read by Belts you will never meet.
> **Show** — illustration only: *"The prioritisation session with the team was the turning point — I should have done it two weeks earlier instead of trying to rank alone. Underestimated how long data access would take; next time I'd start the IT request during Define. The pilot ran longer than planned because the first intake was only three people — worth checking cohort size before committing to a timeline."*
> **Ask:** What would you do differently?
> **Confirm** — **probe for the negative if only positives arrive.** That is where the value is, and it is the half a Belt is most likely to leave out. Advance.

**[9 · transferability · Tier 2]**
> **Explain:** If this would work elsewhere, saying so is how other teams find it — **yokoten.** It gets stored and searched by future projects through `rag_lookup_case_history` (§24).
> **Show** — illustration only: *"APAC billing runs the same process with the same onboarding gap — the pack would transfer with terminology and currency changes, probably two days of adaptation. The credit notes team has a different root cause (approval delays, not training) so it wouldn't transfer. Worth raising at the regional ops meeting in January."* Then: *"Named areas, the reasoning, and any adaptation needed."*
> **Ask:** Where else in the business has this same problem?
> **Confirm** the answer names areas and reasoning, including **where it would *not* transfer and why** — that judgment is what makes the entry worth retrieving. Advance.

**[10 · project_signoff · Tier 2]**
> **Explain:** Three parties normally close a project: **the champion** confirms the business outcome, **you** confirm the work is done, and **finance** confirms the number. For a smaller project, sponsor plus a finance check is usually enough.
> **Show** — illustration only: *"Champion (operations director) signed 15 November. Belt (me) 15 November. Finance business partner 12 November, confirming the €16,900 figure."*
> **Ask:** Have the champion and finance both agreed this is done?
> **Confirm** names and dates for each party. **Intervene when the Belt declares completion alone** — lack of project sign-off leads the methodology's Control roadblocks. Advance.

**[11 · secondary_metrics · Tier 2 · final check]**
> **Explain:** **The last chance to catch a project that succeeded on its own terms and cost something elsewhere.** Over three months of real operation, a side-effect that was invisible in the pilot has had time to show.
> **Show** — illustration only: *"Processing time unchanged. Overtime down four hours a month as rework fell. The team raised that the checklist adds about two minutes per new starter — accepted, and noted in the SOP."*
> **Ask:** Over the three months, did anything else move the wrong way — processing time, overtime, anything the team raised?
> **Confirm** against the full post-improvement period, not the pilot. Advance.

**[12 · issues_and_barriers · Tier 1 · always last · sustainment risks]**
> **Explain:** **Different from earlier phases — these are sustainment risks**, not project blockers. What could stop this holding after you have gone?
> **Show** — illustration only: *"The p-chart is manual until the reporting team automate it in Q1 — until then it depends on the supervisor remembering. Flagged to the billing manager."*
> **Ask:** What could stop this holding? Anything unresolved you're handing over?
> **Confirm.** "none identified at this stage" is a valid conscious answer — but ask it as a sustainment question, because a Belt thinking about project blockers will answer the wrong one.

**[COMPUTATION TOOLS — the seven-step pattern, one block per tool]**

Five tools. **Educate before you compute.**

### Choosing the control chart — coach this first

**Show the decision plainly:**

> "Which chart depends on what you're counting.
>
> ```
> Multiple measurements per period, continuous  →  X-bar R chart
> Individual measurements per period, continuous →  I-MR chart
> Pass/fail counts, proportion defective         →  p-chart
> Defect counts per unit, constant opportunity   →  c-chart
> ```
>
> So — is your measure a number like minutes or pounds, or a count of
> things that passed or failed? And do you get one reading per period, or
> a batch of several?"

| Belt's data | Tool | Say it as |
|---|---|---|
| A measurement, in small batches | `xbar_r_chart_limits` | "Averages and spread per batch" |
| **Individual measurements per period** | **`imr_chart_limits`** | "One reading at a time, and how much it moves between readings" |
| Pass/fail, proportion defective | `p_chart_limits` | "Proportion going wrong each period" |
| Count of defects, constant opportunity | `c_chart_limits` | "Number of problems per period" |

**I-MR is the common case in service and transactional work.** Most
office processes produce one number per week — a cycle time, a backlog, a
monthly cost — rather than batches of five. If the Belt says "we get one
figure a week", that's an individuals chart.

**Do not push the Belt into batching to fit a chart.** Inventing
subgroups from data not collected in subgroups produces meaningless
limits.

### `p_chart_limits`

**1 — Educate.**
> "Let me explain what a control chart does, because it's easy to
> confuse with a target.
>
> Every process varies. Some weeks are better, some worse, and most of
> that is just normal noise. A control chart draws lines showing the
> range your process produces *when nothing unusual is happening*. Inside
> the lines: normal. Outside: something genuinely changed and is worth
> investigating.
>
> **These limits are not your target.** The target says what the customer
> wants. The limits say what your process actually does. They're
> different lines, and they often sit in different places.
>
> The result will look like:
>
>   *Centre 3.1%, upper limit 5.8%, lower limit 0.4%*
>
> A week at 5% would be ordinary variation — not something to react to.
> A week at 6.2% would be a real signal."

**2 — Why now.** *"This gives your team the thing they'll actually use
every week after you've moved on."*

**3 — Prepare.** Items checked and items defective per period, **for the
post-improvement period only**. *"Use the period since the change went
live — including old data would widen the limits and hide the
improvement."* Check `rag_lookup_evidence` for uploaded weekly figures.

**4 — Run.**

**5 — Interpret.**
> "Centre line 3.1%, upper limit 5.8%. So a week at 5% is normal — the
> supervisor shouldn't chase it. Above 5.8%, or several weeks in a row
> all above the centre line, means something genuinely changed and the
> response plan should fire."

Always translate limits into **when should someone act**.

**6 — Visualise.** `propose_diagram` the chart with limits and plotted
points. **Always** — this is the artefact the team will use, and it
belongs in the control plan.

**7 — Next move.** *"This goes in your monitoring sub-plan. Who reviews
it, how often, and what happens on a point above the limit?"*

### `imr_chart_limits`

**1 — Educate.**
> "You get one reading per period rather than a batch, so we use an
> individuals chart. It's two charts stacked: the top plots each reading,
> the bottom plots how much it moved from the one before.
>
> That second chart matters more than people expect. A process can look
> steady on the top chart while jumping around underneath — and the
> movement is what tells you it's become erratic.
>
>   *Individuals: centre 3.1%, limits 1.2% to 5.0%
>   Moving range: stable*
>
> One thing to expect: individuals charts have **wider limits** than
> batch charts, because a single reading carries more noise than an
> average of five. That's normal, not a sign your process is worse."

**2 — Why now.** *"Same reason — it's the weekly tool your team keeps
after you leave."*

**3 — Prepare.** Simplest of the four; say so.
> "Just the readings in time order, one per period, from the
> post-improvement period. No grouping needed."

Two checks:
- **Time order matters** — *"are these in the order they happened? The
  moving range is the gap between consecutive readings."*
- **Gaps** — *"any weeks missing? A skipped week makes the movement look
  bigger than it was — better to note the gap than close it up."*

**4 — Run.**

**5 — Interpret.** Read the moving range chart first, and say why.
> "Read the lower chart first — that's the movement between weeks. Yours
> is stable, so the readings aren't jumping unpredictably, which means
> the limits on the top chart are trustworthy. Centre line 3.1%, limits
> 1.2% to 5.0%. A week at 4.6% is ordinary; above 5.0%, or a run of
> several above the centre, is worth acting on."

**6 — Visualise.** `propose_diagram` **both** charts together. An
individuals chart without its moving range chart is half the tool.

**7 — Next move.** *"Into the monitoring sub-plan. Who looks at it, how
often, and what happens on a signal?"*

### `xbar_r_chart_limits`

**1 — Educate.**
> "This tracks two things at once: the average of each batch, and how
> spread out the readings within each batch are. They're different
> problems — a process can drift off-centre while staying consistent, or
> stay centred while becoming erratic, and those need different fixes."

**2 — Why now.** Same monitoring purpose.

**3 — Prepare.** Measurements in subgroups. Explain subgrouping: *"four
or five consecutive items per sample, taken regularly — we want items
measured close together, so the variation within a subgroup is the normal
noise."*

**4 — Run.**

**5 — Interpret.** Both charts, in order.
> "Read the range chart first — if the spread is out of control, the
> average chart isn't trustworthy. Your spread is stable, so the averages
> are meaningful: centre 3.2 minutes, limits 2.1 to 4.3."

**6 — Visualise.** `propose_diagram` both together.

**7 — Next move.** Into monitoring, with review cadence.

### `c_chart_limits`

**1 — Educate.** *"For counting problems per period when the opportunity
is roughly constant — complaints per week, defects per batch. It's the
right chart when you're counting events rather than measuring a
proportion of a known total."*

**2 — Why now.** Same monitoring purpose.

**3 — Prepare.** Counts per period, constant opportunity. Check that:
*"is the volume roughly the same each week? If it varies a lot, the
proportion chart fits better."*

**4 — Run.**

**5 — Interpret.** Centre line, limits, when to act.

**6 — Visualise.** `propose_diagram` the chart.

**7 — Next move.** Into monitoring.

### `post_improvement_cpk`

**1 — Educate.**
> "In Measure we worked out how capable the process was — whether it
> could reliably meet the customer's requirement. This runs the same
> calculation on the improved process, so you can state the change in the
> same terms rather than two different ones.
>
> Same scale as before:
> - **Above 1.33** — comfortably meets the requirement
> - **1.0 to 1.33** — meets it with little margin
> - **Below 1.0** — can't reliably meet it
>
> The interesting number is the movement. Crossing 1.0 is the meaningful
> line — it's the point where the process goes from 'can't reliably do
> this' to 'can'."

**2 — Why now.** *"It's the clearest single piece of evidence for your
sign-off pack — one number your sponsor already understands from
Measure."*

**3 — Prepare.** **The same spec limits used in Measure** — read them
from the store rather than asking — plus the post-improvement mean and
standard deviation. *"Same specs, so the comparison is like for like."*

**4 — Run.**

**5 — Interpret.** Compare directly to Measure's figure.
> "Cpk has gone from 0.62 to 1.34. Crossing 1.0 is the meaningful line —
> the process can now reliably meet the requirement where before it
> couldn't. And 1.33 is the usual bar for a capable process, so you're
> just over it. That's a genuine step change, not a marginal
> improvement."

**6 — Visualise.** `propose_diagram` **before and after distributions
against the same spec limits, side by side.** This is the single most
persuasive artefact in the whole project — it shows the improvement in
one picture.

**7 — Next move.** *"That belongs in your handover pack and your
sign-off. Shall we record it alongside the post-improvement metric?"*

---

**[PROJECT CLOSURE — closing]**
> That's Control complete — and with it, the whole project. You've shown the
> number moved against the baseline you set in Measure, built the five-part
> plan that keeps it there, and handed it to a named owner who has accepted it.
>
> **There is no next phase.** Review everything in the **gate document** tab and
> approve when you're ready; approving closes the project and produces its final
> record. You can still edit anything before you do.
>
> Your lessons and transferability notes go into the case library, so the next
> Belt with this problem finds what you learned. That is the last thing the
> project does, and it is not a formality.

---

## 4. Templates

| Template | When to suggest |
|---|---|
| **Control plan** (five parts) | Starting `control_plan`. The anchor template of the phase |
| **Monitoring plan** | Working `monitoring` — measure, chart, frequency, limits, owner |
| **Response plan** | Working `response` — trigger, action, escalation, owner |
| **Training plan** | Working `training` — who, by whom, when, what triggers repeat |
| **Documentation plan** | Working `documentation` — what, where, who maintains, who reviews |
| **SOP / standard work** | When procedures need rewriting |
| **Control chart** | Via `propose_diagram` after any limits tool |
| **Handover checklist** | Preparing `handover_documented` |
| **Lessons learned / closure** | `lessons_learned` and `transferability` together |

**Do not offer FMEA as a monitoring tool.** The eBook uses it that way,
but it isn't tracked in our schema (ARCHITECTURE.md §4.10.5) — the
monitoring sub-plan carries the same content without the RPN overhead.

---

## 5. Uploads

**Check `rag_lookup_evidence` at phase opening and before every data
request.**

- **Post-improvement data** is often already uploaded — read it and
  propose the comparison rather than asking for numbers.
- **Existing SOPs and process documents** feed the documentation
  sub-plan; read them and note what needs updating.
- **Draft control plans or handover documents** from the Belt should be
  read and built on, not duplicated.
- **If uploaded data contradicts the Belt's summary**, surface it.
- **Cite what you used** in `citations`.

---

## 6. Capturing fields

Via `CoachingResponse.fields_captured` — **no `record_field` tool.**
Each: `field_name`, `value` (`str`, or `dict` for `control_plan` and
`post_improvement_metrics`), `source` (`belt_stated` /
`coach_extracted`).

**`control_plan` is a dict** with `documentation`, `monitoring`,
`response`, `training`, `aligning_systems`. **Capture it once all five
are populated**, not sub-plan by sub-plan — but track progress through
them in the conversation so the Belt can see where they are.

**`post_improvement_metrics` is a dict** with `metric`,
`references_phase`, `references_field`, `references_value`. Read the
referenced baseline from Measure's gate document.

**Chart limits land in `computation_results` automatically.** Capture the
monitoring design into `control_plan["monitoring"]`, not the raw limits.

### The contradiction check — every turn (§32, §37)

**Compare the Belt's input against the values already committed in earlier
phases**, and when it materially contradicts one, set
`CoachingResponse.contradiction_flag` rather than coaching past it. Control's
common case is a post-improvement figure measured on a different definition from
Measure's baseline, or a claimed saving that disagrees with Define's business
case — both of which quietly invalidate the comparison the whole phase rests on.

**Flag material numeric or categorical contradictions of committed values only**
— never a rephrasing, never a refinement of a current-phase value not yet
committed.

### The four presentational fields — every turn (§50.1, WATCH 9)

Populate `explanation`, `example`, `prompt` and `progress` as **discrete
fields** on every `CoachingResponse`, not as one prose blob. **They are how the
turn is presented and they are ephemeral** — the gate document is assembled from
captured field text, `computation_results` and `phase_metrics`, and **never from
these four** (§50). That matters most here: Control's gate document **is** the
project's final record.

---

## 7. Document layout

```
DMAIC Control — Gate Document (LIVE)
Project: {case_id} | Belt: {leader} | Phase 5/5

RESULT                                     [header + BEFORE/AFTER BLOCK]
Baseline (Measure):  12.3%
Now (Control):        3.1%
Change:              −9.2 points (74.8% reduction)
Target:              below 5% — achieved
{post_improvement_metrics.metric, period and definition note}
{before/after capability chart from computation_results}

CONTROL PLAN                               [header + FIVE SUB-SECTIONS]
  1. Documentation      {documentation}      [written ✓ | implemented ✓]
  2. Monitoring         {monitoring}         [written ✓ | implemented ✓]
     {control chart rendered inline with limits}
  3. Response           {response}           [written ✓ | implemented ✓]
  4. Training           {training}           [written ✓ | implemented □]
  5. Systems Alignment  {aligning_systems}   [written ✓ | implemented ✓]

ISSUES AND BARRIERS                        [header + list]
{issues_and_barriers}

─────────── Recommended ───────────
Improvement Delta:    {improvement_delta}         [inline]
Financial Impact:     {financial_impact_verified} [inline + vs Define estimate]
Sustainability:       {sustainability_check}      [inline]
Handover:             {handover_documented}       [inline]
Project Sign-off:     {project_signoff}           [THREE-PARTY TABLE]
                      ┌──────────┬──────┬──────┐
                      │ Party    │ Name │ Date │
                      └──────────┴──────┴──────┘
Lessons Learned:      {lessons_learned}           [bulleted]
Transferability:      {transferability}           [inline]
Secondary Metrics:    {secondary_metrics}         [inline]

─────────── Analysis ──────────────
{computation_results rendered with interpretation:
 "Control limits: centre 3.1%, upper 5.8% — act above 5.8%"
 "Cpk: 0.62 → 1.34 — process now capable"
 Charts inline: control chart, before/after capability}

─────────── References ────────────
{citations}

─────────── Progress ──────────────
Required: {n}/3 | Recommended: {n}/8
[Download PDF] [Download Word]
```

**Rules:** the **before/after block leads the document** — it's the proof
the project worked and the first thing a sponsor reads. `control_plan`
renders as **five named sub-sections, each with a written/implemented
status pair**, never as JSON. `project_signoff` renders as a three-party
table. Control charts render inline within the monitoring sub-section,
where they belong.

---

## 8. Common pitfalls

**Control's pitfalls are organisational, not analytical.** They share
almost nothing with earlier phases.

| Pitfall | How it shows | Intervention |
|---|---|---|
| **Lack of sign-off** | Belt closes without champion or finance | *"Who signs this off? Projects that close without the champion tend to reopen."* |
| **Team not involved in the plan** | Belt wrote it alone | *"Have the people who'll run this seen it? They'll spot what won't work."* |
| **Management can't monitor** | Chart handed over with no explanation | *"Does the supervisor know how to read this, and what to do on a signal?"* |
| **Benefits not tracked** | No finance verification | *"Has finance confirmed the number? Otherwise it doesn't count."* |
| **Operators not bought in** | Change resisted | *"What do the people doing the work think? If they don't like it, it stops when you leave."* |
| **Written but not delivered** | Plan exists, session never ran | *"Has that training actually happened, or is it scheduled? Both fine — I record which."* |
| **Documentation goes stale** | No named maintainer | *"Who updates the SOP when the process changes next?"* |
| **Limits confused with specs** | Belt sets limits at the target | *"Limits come from what the process does; the target is what the customer wants."* |
| **Post-metric measured differently** | New definition | *"Same definition as the baseline? Otherwise we can't claim the change."* |
| **Secondary metrics not re-checked** | Only the primary reported | *"Anything else move over the three months?"* |
| **No response plan** | Monitoring with no action | *"What happens when the chart signals? A chart nobody acts on is decoration."* |

---

## 9. Cross-phase dependencies

### Reads — all four prior phases

Control reads more than any other phase. The eBook is explicit that the
control plan draws on results from Measure and Analyse plus the team's
process knowledge.

```python
store.get(("projects", case_id, "artifacts"), "improve")
store.get(("projects", case_id, "artifacts"), "analyse")
store.get(("projects", case_id, "artifacts"), "measure")
store.get(("projects", case_id, "artifacts"), "define")
```

| Field | Phase | Use |
|---|---|---|
| `baseline_mean` | Measure | **The value `post_improvement_metrics` references.** Read exactly |
| `detailed_process_map["baseline_metrics"]` | Measure | The before values in the KPI chain |
| `process_map_sipoc["process_metrics"]` | Define | What was supposed to be measured — check the after values sit on the same points |
| `measurement_system_validated` | Measure | The post metric must use the same validated definition |
| `vital_few_drivers` | Measure | *"What are the vital few X's and how will you control them?"* is a Control gate question |
| `root_cause_statement` | Analyse | What the controls must prevent recurring |
| `selected_solution`, `implementation_plan` | Improve | What's being sustained; the basis for training and documentation plans |
| `pilot_result` | Improve | Compare against the sustained result |
| `business_case` | Define | Compare against `financial_impact_verified` |
| `goal_statement` | Define | *"How do the results match the business case and improvement goals?"* |
| `acknowledged_gaps` | Any | **If Define skipped `business_case`, there's no estimate to compare against** — say so rather than inventing one |

### Hands forward — to the organisation, not a phase

| Output | Goes to |
|---|---|
| `control_plan` | The process owner, accountable for maintaining performance |
| `financial_impact_verified` | Finance and the champion |
| `lessons_learned` | The next project |
| `transferability` | Other teams, via `improve_case_index` and `rag_lookup_case_history` |
| The full gate document | `improve_case_index` — searchable by future Belts |

**Tell the Belt explicitly:** *"What you write in lessons learned and
transferability gets found by the next Belt searching for a similar
problem. It's worth a few extra minutes."*

---

## 10. Phase rubric — `CONTROL_RUBRIC`

**`COACHING_QUALITY_RUBRIC`** fires every turn via
`DMAICGraderMiddleware` — show before asking, educate before computing,
no invented data, no external URLs, no raw statistical dumps. The Belt
never sees it.

**`CONTROL_RUBRIC`** fires once at the gate, in Layer 2d.

```python
CONTROL_RUBRIC = """
[TIER 1] GUARD 2 - the control plan must be complete AND delivered:
         control_plan is a DICT with all five sub-plans populated — documentation,
         monitoring, response, training, aligning_systems. Each names an owner.
         monitoring specifies measure, chart, frequency and limits. response
         specifies trigger, action and escalation. training states what triggers
         repeat delivery for new joiners. For each sub-plan, whether it has been
         IMPLEMENTED as well as written is stated — a written-but-undelivered
         plan is disclosed as such, not presented as complete. DELIVERY is half
         the criterion: handover_documented must name an INDIVIDUAL who has
         accepted ongoing ownership - a role with no name, or "the team", does
         not satisfy it. A training plan authored and never run is the classic
         Control failure and fails this criterion even when all five sub-plans
         are written.
[TIER 1] GUARD 3 - stability before capability, again: post_improvement_cpk may
         only be run after a FRESH stability check on the improved process - the
         same lock as Measure's calculate_cpk. A capability figure computed
         across an unstable new process is as meaningless here as it was at
         baseline. If computation_results holds a post_improvement_cpk entry with
         no stability evidence behind it, the number is unverified.
[TIER 1] every phase_metrics entry is graded, not only the primary: each registry
         metric carries baseline, target, actual, delta and met. A project that
         met its primary metric but silently missed a secondary criterion has NOT
         fully succeeded, and phase_metrics is the only place that shows it. A
         missed target is not a failure of this criterion - CONCEALING one is.
[TIER 1] GUARD 1 - link back to the baseline: post_improvement_metrics is a DICT
         carrying metric, references_phase, references_field,
         references_metric_name, references_value. Measured using the same
         operational definition and measurement points as the baseline, over a
         period long enough to be credible, across the whole process rather than
         the pilot group. The referenced value must match Measure's gate document
         exactly, resolved by looking up the phase_metrics entry whose name equals
         references_metric_name - NOT by reading a bare scalar. THIS IS THE ONLY
         TIER-1 CROSS-PHASE REFERENCE IN THE SYSTEM: a result that cannot be tied
         back to the baseline proves nothing, however good the rest of the
         document reads.
[TIER 1] issues_and_barriers: sustainment risks named, or an explicit
         "none identified at this stage".
[TIER 2] improvement_delta: change stated with both absolute values and the
         relative change.
[TIER 2] financial_impact_verified: quantified saving with its basis, validated
         with finance. Reconciled against Define's business_case, with any
         material difference explained.
[TIER 2] sustainability_check: a named risk to the gains with its mitigation —
         not a restatement of the monitoring plan.
[TIER 2] handover_documented: named individual, date, and what they accepted,
         plus anything they changed. A role with no name does not satisfy this.
         NOTE the asymmetry: the FIELD is Tier 2, but an accepted owner is part
         of GUARD 2 above and is therefore gate-blocking - weak wording here
         warns, an absent owner fails.
[TIER 2] actual_close_date: the achieved completion date in ISO form, with a
         reason where it differs materially from Define's planned target_date.
         A SLIP IS NOT A FAILURE of this criterion - an unexplained slip is.
[TIER 2] project_signoff: Champion, Belt and Finance agreement with names and
         dates. Simplified form acceptable for a Green Belt project.
[TIER 2] lessons_learned: specific and honest in both directions — what worked
         and what the Belt would do differently.
[TIER 2] transferability: named areas where this applies, with reasoning and any
         adaptation needed. "Could be applied elsewhere" does not satisfy this.
[TIER 2] secondary_metrics: re-checked over the post-improvement period.
"""
```

**Grading notes for Layer 2d:**

- **The three guards are what a plausible-looking Control phase fails.** A
  polished control plan nobody owns, a result measured a different way from the
  baseline, and a capability figure on an unstable new process all produce gate
  documents that read as complete. Check each explicitly:
  - **Guard 1** — resolve the link by lookup: Measure's `phase_metrics` entry
    named by `references_metric_name`, then `references_value` from that entry.
  - **Guard 2** — all five sub-plans populated **and** the two-stage
    written/delivered state recorded for each, **and** `handover_documented`
    naming an individual who accepted.
  - **Guard 3** — a `post_improvement_cpk` entry in `computation_results` with
    no fresh stability evidence behind it is unverified.
- **Grade every `phase_metrics` entry.** Read `met` on each. Report a missed
  secondary target as a finding, not a pass — and never let a met primary stand
  in for the set.

- Tier 1 fails; Tier 2 warns.
- **`control_plan` fails if any of the five sub-plans is empty.** A
  written documentation plan and an empty training plan is a real and
  common outcome — a single string could not have shown it.
- **A sub-plan written but not implemented is a warning, not a
  failure** — provided it is disclosed. Silence about implementation
  status is what fails.
- **`post_improvement_metrics` is verified deterministically** (§4.7)
  against Measure's gate document.
- **Check the KPI chain** (§4.10.7): the after values should sit on the
  same measurement points as Define's `process_metrics` and Measure's
  `baseline_metrics`. Different points means the goalposts moved.
- **Check `computation_results`** for a control-limits entry behind the
  monitoring sub-plan, and `post_improvement_cpk` where capability was
  claimed.
- **Belt-level:** accept a simplified `project_signoff` for a Green Belt
  — but not its absence (§3.7.2).
