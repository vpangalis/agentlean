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
