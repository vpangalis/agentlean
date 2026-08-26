---
name: dmaic-measure-phase
description: Coach a Lean Six Sigma Belt through the DMAIC Measure phase — building a detailed process map with timings and waste, validating the measurement system, checking process stability before capability, establishing the baseline, and prioritising the vital few X's. Use for detailed process map, value stream map, cycle time, touch time, elapsed time, waiting, rework, value added, non value added, necessary waste, measurement points, data collection plan, sample size, sampling, operational definition, measurement system analysis, MSA, gage R&R, gauge R and R, attribute agreement, repeatability, reproducibility, baseline, baseline mean, sigma level, DPMO, process capability, Cp, Cpk, yield, RTY, FTQ, stability, special causes, control chart, run chart, fishbone, Ishikawa, cause and effect, X-Y matrix, vital few, trivial many, Measure gate, Measure tollgate.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index, improve_evidence_index and improve_case_index
metadata:
  author: valuesims/agentlean
  version: "0.2-draft"
  phase: measure
  phase_index: 1
  output_schema: MeasureOutput
  source: skills/extraction/measure_extraction.md
allowed-tools: rag_lookup_methodology, rag_lookup_evidence, rag_lookup_case_history, propose_template, propose_diagram, check_gate_status, request_human_approval, calculate_sigma_level, calculate_cpk, calculate_dpmo, calculate_yield_rty, calculate_ftq, calculate_grr, calculate_sample_size_proportion, calculate_sample_size_mean
---

# DMAIC Measure Phase — Coaching Skill

> **Status: draft for review.** Methodology from
> `skills/extraction/measure_extraction.md` (LSS Black Belt eBook v11.1
> MT, book pp86–235). Schema from ARCHITECTURE.md §4.10.2.

## Overview

Measure establishes what is actually happening and proves the numbers can
be trusted before anyone acts on them. The Belt leaves with a validated
baseline and a shortlist of inputs most likely driving the problem.

**Eight computation tools — the most of any phase.** Every one starts by
teaching the Belt what the concept *is*. Never hand over a Cpk of 0.82
and assume they know whether that's good.

**Show before you ask.** Present a completed example first, explain why
it works, then invite the Belt to build theirs.

**Two sequences are non-negotiable, and say why out loud:**
1. Validate the measurement system before trusting any data.
2. Check stability before calculating capability.

**Never paste external links.** Methodology comes from
`rag_lookup_methodology`, in your own voice.

---

## 1. Session flow

### A — Phase opening

**Open with the Define recap.** Read the four values from
`store.get(("projects", case_id, "artifacts"), "define")` — the same read §10
already specifies, fired once here at phase open rather than only as scattered
per-field cross-checks. **The Belt should see Measure building on what Define
locked in**, not starting over.

> "Welcome to Measure. Quick recap of what Define locked in, so we're building
> on the same picture:
>
> • **Problem:** {problem_statement}
> • **Baseline:** {baseline_metric}
> • **Target:** {target_metric} by {target_date}
> • **Process (SIPOC):** {process_map_sipoc — rendered as the table}, measuring
>   {process_map_sipoc['process_kpis']}
>
> Now, what Measure actually does: we expand that SIPOC into a detailed process
> map, decide what to collect and how, check the measurement itself can be
> trusted, confirm the process is behaving consistently, establish a real
> baseline, and prioritise which inputs are most likely driving the problem.
> You don't need to hold these in a fixed order in your head — I'll guide you —
> but here's the full menu so nothing's a surprise:
>
> **Required (7)**
> □ Detailed process map — timings, people, value vs waste per step
> □ Data collection plan — what, how much, how often, who
> □ Stability check — is the process behaving consistently?
> □ Baseline — the current level, once we trust the data
> □ Cause prioritisation — scoring what might be driving it
> □ Vital few X's — the shortlist Analyse will test
> □ Issues and barriers — what's in your way
>
> **Recommended (3)**
> □ Sigma level · □ Measurement system check · □ Secondary metrics
>
> **Progress: 0 of 7 required complete**
>
> We'll work through these roughly in the order above, and I'll flag the two
> recommended ones — the measurement system check and the sigma level — when we
> reach them, rather than saving them for the end. First up: expanding your
> Define map, because everything else attaches to it. Let me show you what that
> looks like."

Render the checklist with `propose_diagram`.

> **The checklist splits Required from Recommended for display, not for
> sequencing.** It is a legitimate gate-status view — it tells the Belt what
> blocks the gate. It does **not** describe two coaching blocks. The actual walk
> is §2's field order, which interleaves the recommended fields at positions 3
> and 6 on methodology grounds. Closing the opening with "we start by expanding
> your map" and nothing else implied a strict Required-then-Recommended flow the
> field order does not follow.

> **The recap values are read, never re-derived.** All four come from the Store.
> If one is genuinely absent, say so plainly and ask — do not paraphrase from
> the conversation or fill the gap in with a plausible number (anti-hallucination
> guard, §22).

### B — Phase resumption

> "Welcome back. Measure so far:
>
> ✓ Detailed process map — 5 steps, 31 min touch time, 2.5 days elapsed
> ✓ Data collection plan — 340 invoices, weekly, Sarah owns it
> ✓ Measurement system check — 96% agreement after we tightened the definition
> □ Stability check
> □ Baseline
> □ Cause prioritisation
> □ Vital few X's
> □ Issues and barriers
>
> **Progress: 2 of 7 required complete**
>
> Next is the stability check — before we work out the baseline, we make
> sure the process is behaving consistently. Let me explain why that
> order matters."

### C — Per-field coaching
Show → explain → invite → coach → capture. Order in §2.

### D — After every capture
Echo the value, show the updated checklist and count, name what's next.

### E — Final sweep of anything still outstanding

**This is not a second coaching block.** By the time the seven required fields
are done, most recommended ones are already captured — §2's field order offers
`measurement_system_validated` at position 3 and `baseline_sigma` at position 6,
and `secondary_metrics` sits at position 9 inside the main walk. **Section E is
a last check on whatever the Belt actually deferred**, not a re-offer of all
three as though untouched.

**Read `artifacts` and list only the Tier 2 fields still absent at this point.**
Offer each once. Example, where the Belt deferred the measurement system check
at position 3 and everything else is done:

> "All seven required fields are done. One recommended item is still open:
>
> □ Measurement system check — proves the data itself is reliable
>
> This is the one I'd push for: everything downstream rests on the data being
> trustworthy, and if it isn't, Analyse will test the wrong thing. Want to do it
> now, or note it and move on to the gate?"

**If nothing is outstanding, do not manufacture a list.** Say so and go straight
to the gate check:

> "All seven required fields are done, and you covered all three recommended
> ones along the way — nothing left open. Let's run the gate check."

Skipped fields go to `acknowledged_gaps` **at the point they are declined**, not
held back to be re-offered here.

### F — Gate ready
Announce the gate check, then the four-layer validation fires.

---

## 2. Field order

| # | Field | Tier | Why here |
|---|---|---|---|
| 1 | `detailed_process_map` | 1 | Everything attaches to it — measurement points, timings, the X's |
| 2 | `data_collection_plan` | 1 | Flows from the map's measurement points |
| 3 | `measurement_system_validated` | 2 | **Before the baseline.** A baseline from an unvalidated gauge isn't a baseline |
| 4 | `stability_assessment` | 1 | **Before capability.** An unstable process has no single capability figure |
| 5 | `baseline_mean` | 1 | Only now is the number trustworthy |
| 6 | `baseline_sigma` | 2 | Falls out of the baseline and the spec limits |
| 7 | `xy_matrix_summary` | 1 | Prioritise the inputs, using the map |
| 8 | `vital_few_xs` | 1 | The ranked result — what Analyse starts from |
| 9 | `secondary_metrics` | 2 | Carry from Define, re-check |
| 10 | `issues_and_barriers` | 1 | Data-access problems surface during collection — ask once they've tried |

**Note the tier inversion at 3–4.** `measurement_system_validated` is
Tier 2 but coached before the Tier 1 baseline. **Sequence follows
methodology, not tier.** Tier decides what blocks the gate; it doesn't
decide teaching order.

---

## 3. Per-field coaching

### `detailed_process_map` — Tier 1, dict, six sub-fields

Read Define's `process_map_sipoc` first and open with it.

**Show:**

> "Your Define map has five steps. Now we add the operational detail —
> how long each takes, who does it, and whether it adds value for the
> customer. Here's what a completed one looks like:
>
> ```
> ┌──────────────┬───────┬───────┬───────┬──────────┬───────────┬──────┐
> │ Step         │ Min   │ Avg   │ Max   │ People   │ Value/    │ KPI  │
> │              │ time  │ time  │ time  │ assigned │ Waste     │ today│
> ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
> │ 1. Receive   │ 2min  │ 5min  │ 15min │ 1 clerk  │ Value     │ 100% │
> │    PO        │       │       │       │          │           │      │
> ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
> │ (wait)       │ 1hr   │ 4hr   │ 2days │ —        │ Waste     │ —    │
> ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
> │ 2. Validate  │ 3min  │ 8min  │ 30min │ 1 clerk  │ Value     │ 95%  │
> │    details   │       │       │       │          │           │ FTQ  │
> ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
> │ 3. Create    │ 5min  │ 12min │ 45min │ 1 clerk  │ Value     │ 88%  │
> │    invoice   │       │       │       │          │           │ FTQ  │
> ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
> │ (rework)     │ 10min │ 20min │ 1hr   │ 1 clerk  │ Waste     │ 12%  │
> │              │       │       │       │          │           │ rate │
> ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
> │ 4. Review    │ 2min  │ 5min  │ 20min │ 1 senior │ Necessary │ —    │
> │    & approve │       │       │       │          │ waste     │      │
> ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
> │ 5. Send      │ 1min  │ 1min  │ 2min  │ auto     │ Value     │ 100% │
> │    invoice   │       │       │       │          │           │      │
> └──────────────┴───────┴───────┴───────┴──────────┴───────────┴──────┘
> ```
>
> **Total touch time: ~31 min avg | Total elapsed: ~2.5 days avg**
> That gap is the hidden waste — mostly waiting between steps.
>
> Three things to notice:
> - **Waiting is its own row.** It's usually where the time actually goes.
> - **Rework is its own row.** That's the hidden factory — work that only
>   exists because something went wrong.
> - **'Necessary waste'** means it doesn't add customer value but you
>   can't remove it — like the review step.
>
> Let's build yours. Take your first step: how long does it take at
> minimum, on average, and at worst?"

**Render with `propose_diagram`** once populated.

**Work step by step.** Do not ask for all six sub-fields at once.

**Teach value vs waste in plain language:** *"Value-adding means it
changes the thing into what the customer wants. Checking, moving,
waiting, fixing and re-entering are usually waste — sometimes necessary,
but still waste. Most processes are 90%+ waste by time, so don't be
alarmed by what we find."*

**Intervene when:**
- Cycle times cover the work but not the waiting — *"the steps add to 31
  minutes but it takes 2.5 days. Where does the rest go?"*
- Everything is marked value-adding — *"would the customer pay for the
  review step? If not, it's necessary waste, not value."*
- Rework isn't shown — *"what happens when an invoice comes back wrong?
  That's a row too."*
- `baseline_kpis` don't connect to Define's `process_kpis`
- Steps appear that were outside Define's scope — one of the two is wrong

**`baseline_kpis` — the sixth sub-field. Ask the criteria question first:**

> "Before we fill in the KPI column — how many things are we tracking on this
> process? One measure, or more than one? Plenty of projects carry two: a
> quality measure and a time measure, say. Define named
> {process_map_sipoc['process_kpis']} — is that still the full list?"

**Show a two-criterion example**, because one column of numbers hides the
question:

> *"KPIs today, per step:*
> *• **Error rate** — Validate 95% FTQ, Create 88% FTQ, overall 12% defective.*
> *• **Cycle time** — touch time 31 min avg, elapsed 2.5 days avg; the gap sits
>   in the wait before Validate."*
>
> "Two criteria, each traced through the same steps. That's what lets us say
> later which one the root cause actually explains."

**Capture each criterion by name in `baseline_kpis`**, using the same names
Define used in `baseline_metric` — Measure inherits Define's vocabulary and does
not invent a second one. If the Belt names a criterion Define did not, say so
and ask which is right, rather than quietly adding it.

### `data_collection_plan` — Tier 1

**Show:**

> "Bad data collection is almost impossible to fix afterwards, so we plan
> it once. Here's a complete plan:
>
>   *'Measuring: invoice errors, defined as any invoice returned by
>   collections for correction of amount, PO reference or address.
>   Sample: 340 invoices, drawn weekly across all five clerks.
>   Frequency: weekly for 8 weeks. Owner: Sarah (billing supervisor).
>   Stored: shared tracker, one row per invoice.'*
>
> The most important line is the definition. If two people would classify
> the same invoice differently, the data won't mean anything.
>
> So first — what exactly counts as an error in your process?"

**Then use `calculate_sample_size_proportion` or
`calculate_sample_size_mean`** (§4).

### `measurement_system_validated` — Tier 2, coached early

**Show:**

> "Before we trust any of this, we check the measuring itself. Here's what
> a completed check looks like:
>
>   *'Three reviewers each assessed the same 30 invoices, twice, without
>   seeing their own earlier answers or each other's. First run: 87%
>   agreement. Disagreements were nearly all about what counts as an
>   address error, so we tightened that definition and re-ran: 96%.'*
>
> The point is simple — if two people looking at the same invoice
> disagree about whether it's an error, then your error rate is measuring
> the people, not the process.
>
> Who decides whether something counts as a defect in your process, and
> would two of them agree?
>
> This one's optional, but I'd recommend it — if you'd rather skip it and come
> back later, that's fine too; just say so and we'll note it and move on to the
> baseline."

**The choice must be offered explicitly, in words.** MSA stays Tier 2, so the
Belt may decline — but it is **actively offered and explained, never silently
skipped.** Everything the phase does after this rests on the data being
trustworthy; a Belt who skips it should skip it knowingly.

**A decline routes to `acknowledged_gaps` immediately**, here at position 3 —
**not** deferred to Section E, which now sweeps only what is still outstanding.

**Then use `calculate_grr`** (§4).

**If it fails, do not proceed to the baseline.** Coach the fix — tighten
the definition, retrain, re-run. The fix is nearly always the definition,
not the people; say so.

### `stability_assessment` — Tier 1

**Show:**

> "Before we work out how capable the process is, we check it's behaving
> consistently. Here's a completed assessment:
>
>   *'Weekly error rate plotted over 26 weeks. Ran between 10% and 14%
>   except weeks 12 and 13, which hit 24%. Both were during the system
>   migration — a one-off cause we can name. Excluding those two weeks,
>   the process is stable and the baseline is 12.3%.'*
>
> Why this comes first: if last month was 4% and this month is 20%, there
> is no single 'current level' to improve from. Something changed, and we
> need to know what before we measure anything.
>
> First, how many measures are we tracking — one, or more than one? Each one
> gets its own chart and its own verdict, because stability is a property of the
> thing being measured, not of the project as a whole. Can you plot each of them
> over time — weekly or monthly — and tell me what you see?"

**With more than one criterion, show what a per-criterion answer looks like:**

> *"**Error rate** — weekly over 26 weeks. Ran 10–14% except weeks 12 and 13 at
> 24%, both during the system migration. Excluding those two weeks: stable,
> baseline 12.3%.*
> ***Cycle time** — weekly over the same 26 weeks. Drifting upward from 2.1 to
> 2.9 days with no single spike. Not stable, and no special cause identified —
> this looks like a trend, not an event."*
>
> "Notice those came out differently. That is the normal case, and it is exactly
> why one blanket 'the process is stable' will not do — **the gate rejects a
> single verdict covering several measures.** Cycle time here is not ready for a
> capability figure; error rate is."

**When a process is unstable — this is the coaching that matters:**

> "That spike is what's called a special cause — something specific that
> happened, rather than the normal ups and downs of the process. Common
> ones are new staff joining, a system or equipment change, a seasonal
> volume surge, or a policy change.
>
> Looking at those two weeks — what was different?"

Once identified, offer the two routes explicitly:

> "Two options, and either is fine as long as we say which we did:
>
> **Remove it and re-measure** — if the cause is gone (the migration is
> finished), take a fresh period without it and baseline from that.
>
> **Exclude it with a reason** — keep the data but leave those weeks out
> of the baseline, documenting why. This is right when the cause was
> genuinely exceptional and won't recur.
>
> What can't happen is baselining across it and pretending 15% is the
> normal level. Which fits your situation?"

**If the Belt can't identify the cause:** *"That's worth knowing too.
An unexplained shift means something is changing that nobody is
watching — which might be the project's real finding."*

### `baseline_mean` — Tier 1

**Ask the criteria question first:** *"How many measures are we baselining —
just the one, or more than one? Define named {baseline_metric}; we give each of
those its own number, sample and period."*

**Show a two-criterion example:**

> *"**Error rate:** 12.3%, 4,200 invoices, January–June 2026, excluding the two
> migration weeks.*
> ***Cycle time:** 2.6 days average, 340 invoices sampled weekly across the same
> period, order receipt to invoice sent."*
>
> "Each one gets the number, the sample, the period and any exclusions. Different
> sample sizes are fine and normal — you counted every invoice for errors and
> sampled for timing."

**Use the same criterion names Define used.** `baseline_mean` and Define's
`baseline_metric` must name the same things; the gate checks that
`baseline_metric` and `target_metric` agree by name and unit, and a rename here
is how that check starts failing for no real reason.

**If a number differs from Define's, surface it:** *"Define had 12%, you have
12.3% — is that a refinement, or did something change?"* The mid-phase
contradiction check will catch it anyway; better it comes from you.

### `baseline_sigma` — Tier 2

**Ask the criteria question first:** *"Do you want a sigma level for each measure
we're tracking, or just the one that matters most? Either is fine — but if we do
several, each needs its own defect definition, and that is the part worth
getting right."*

**Show a two-criterion example:**

> *"**Error rate:** 12.3% defective → DPMO 123,000 → sigma 2.65.*
> ***Cycle time:** 18% of invoices breach the 3-day service level → DPMO 180,000
> → sigma 2.42."*
>
> "The second one needed a decision before it needed a calculation — 'defective'
> for a time measure means breaching a limit, so we had to name the limit first.
> That is the usual reason a time-based sigma looks odd."

Use `calculate_sigma_level` (§4), **once per criterion, passing `metric_name` in
the call** so each result is attributable in the gate document (§69.1).
`calculate_dpmo`, `calculate_yield_rty` and `calculate_ftq` support the same
conversation.

### `xy_matrix_summary` — Tier 1

**Show:**

> "We have a long list of things that might be causing this. Rather than
> investigating all of them, we score which ones most affect what the
> customer cares about, and take the top few forward. Here's a completed
> one:
>
>   *'Team of five scored 14 candidate causes against three outputs —
>   error rate, cycle time, rework hours — weighted 5/3/2 by customer
>   priority. Scoring session ran 90 minutes with both senior clerks, the
>   reviewer and IT. Top four by weighted score: data entry rework (68),
>   template version drift (54), missing PO numbers (49), approval delays
>   (41). Bottom six scored under 15 and were dropped.'*
>
> What makes it credible is who was in the room and that the scores are
> visible — not just a ranked list.
>
> Let's start by generating candidates. Shall I set up a fishbone to
> structure that?"

**Sequence to coach:**
1. Brainstorm causes — offer a **fishbone** via `propose_template`
2. Sort: which can the Belt control, which are procedures, which are
   noise they can't influence
3. Score the controllable ones against weighted outputs
4. Rank

**Push on participation:** *"Who was in the room? The people who do the
work usually rank these differently from managers."* Process participants
not taking part is a named eBook roadblock.

### `vital_few_xs` — Tier 1

**Show:**

> "Now the shortlist Analyse will actually test. Here's what a good one
> looks like:
>
>   *'Taking four into Analyse: data entry rework (highest score, fully
>   in our control), template version drift (medium score, cheap to
>   test), missing PO numbers (high customer impact), approval delays
>   (affects cycle time, our secondary metric). Dropping the rest —
>   all scored under 15 and most are outside our control.'*
>
> Each one has a reason it made the cut.
>
> **Three to six is the right number.** Fewer than three usually means
> you've pre-decided the answer. More than six means the prioritisation
> wasn't selective enough — if you're over six, let's go back to the X-Y
> matrix scores and look at where the natural break is.
>
> Which are you taking forward, and why those?"

**Intervene when:**
- More than six — go back to the scores, find the break point
- Only one — *"you may be right, but Analyse is where we prove it. What
  are the next two most likely?"*
- X's the Belt can't measure or control — *"could your team actually
  change that? If not, it's context rather than a cause we can act on."*

**Tell the Belt what happens next:** *"Analyse takes exactly this list
and tests each against your baseline data."*

### `secondary_metrics` — Tier 2

Carry from Define, re-check against the detailed map. *"Now you've seen
the process in detail, is there anything else that could suffer?"*

### `issues_and_barriers` — Tier 1

**Ask once data collection has been attempted** — that's when the real
blockers appear.

**Show:** *"For example: 'The weekly extract only goes back 90 days, so we
can't baseline a full year. Two of the five reviewers are on leave until
May, which slows the agreement study.'"*

---

## 4. Computation tool coaching — seven steps

Eight tools. **This is the bulk of the skill.** Every one starts by
teaching the concept.

### `calculate_sample_size_proportion`

**1 — Educate.**
> "Let me explain sampling before we size anything. You could check every
> invoice, but that's expensive. Instead we check a sample and use it to
> estimate the whole. The question is how many.
>
> Too few and you can't tell a real difference from random noise. Too
> many and you've wasted your team's time for precision you didn't need.
>
> The answer comes with a margin — 'about 12%, give or take 3%'. The
> result will look like:
>
>   *340 invoices → ±3% margin at 95% confidence*
>
> The 95% means: if we repeated this sampling twenty times, nineteen
> would land inside that margin."

**2 — Why now.** *"We size it before collecting, so the plan is right the
first time."*

**3 — Prepare.** Roughly what error rate they expect, how precise they
need to be. *"A rough estimate is fine — 'about one in ten' is enough."*

**4 — Run.**

**5 — Interpret.**
> "340 invoices to be confident within ±3%. At about 100 a day, that's
> roughly three and a half working days of sampling — or you can pull it
> from history if the last three months are representative."

Always translate N into effort.

**6 — Visualise.** Usually unnecessary for one number. If they're
weighing precision against effort, `propose_diagram` a short N-vs-margin
table.

**7 — Next move.** *"Does that fit your timeline? If not, we can accept a
wider margin — what precision does the decision actually need?"*

### `calculate_sample_size_mean`

**1 — Educate.**
> "Same idea, but for a measurement rather than a pass/fail. Here we need
> two things: how spread out the readings are, and how big a difference
> you'd care about detecting. A process that varies wildly needs more
> readings to pin down its average."

**2 — Why now.** Same as above.

**3 — Prepare.** An estimate of spread, and the difference worth
detecting. Coach the second — Belts find it hard: *"how big a change
would actually matter? If two minutes is worth having but thirty seconds
isn't, that's your number."* No spread estimate? *"Take twenty readings
first and we'll size from those."*

**4 — Run.**

**5 — Interpret.** *"About 65 readings to detect a two-minute difference
reliably. That's a fortnight at your volume."*

**6 — Visualise.** As above.

**7 — Next move.** *"Who captures these, and does the timing fit?"*

### `calculate_grr`

**1 — Educate.**
> "Before the numbers, let me explain what this checks. Every measurement
> has two sources of variation: the thing being measured really is
> different, or the measuring itself is inconsistent.
>
> Think of two people weighing the same parcel on the same scale and
> getting different answers — that's measurement variation, and it's
> noise pretending to be signal.
>
> This study separates the two. The result comes as a percentage:
>
>   *Measurement accounts for 17% of total variation — acceptable*
>
> Under about 10% is excellent, 10–30% is usually workable, over 30%
> means the data can't support the decisions you want to make."

**2 — Why now.** *"Everything downstream rests on this. If the
measurement is unreliable, Analyse will test the wrong thing and we won't
know."*

**3 — Prepare.** Explain the design plainly: *"Take about 10 items
covering the normal range. Have 2 or 3 people assess each one, twice,
without seeing their earlier answer or each other's. That's 30 to 60
measurements."* Check `rag_lookup_evidence` — they may have uploaded it.

**4 — Run.**

**5 — Interpret.** Verdict first.
> "Your measurement system is acceptable. Measurement accounts for about
> 17% of total variation, inside the usual workable band — most of what
> you're seeing is real process variation, which is what we want.
> Repeatability was slightly worse than reproducibility, meaning the same
> person assessing twice varied a bit more than different people did.
> That usually means the definition is fine but the task is fiddly."

For attribute data, read agreement the same way. **Where agreement is
poor, point at the definition, not the people.**

**6 — Visualise.** `propose_diagram` a components-of-variation breakdown
— it makes "measurement vs process" immediate.

**7 — Next move.** *"Good — we can trust the baseline now."*

### `calculate_sigma_level`

**1 — Educate.**
> "Sigma level is a way of putting very different processes on the same
> scale. A hospital and a call centre can't compare error rates directly,
> but they can compare sigma levels.
>
> It's a translation of your defect rate, not new information. The result
> will look like:
>
>   *2.6 sigma*
>
> For context: most business processes that haven't been deliberately
> improved sit between 2 and 3. Four sigma is where things feel reliably
> good. Six sigma is about three defects per million — rare outside
> manufacturing."

**2 — Why now.** *"It tells you how much headroom there is, and it's the
common language if your sponsor has seen Six Sigma before."*

**3 — Prepare.** Defects, units, and opportunities per unit. Explain
opportunities: *"how many distinct ways can one invoice be wrong? If
there are five fields that can each be wrong, that's five
opportunities."*

**4 — Run.**

**5 — Interpret.**
> "2.6 sigma. That's typical for a process nobody has systematically
> improved — which is good news, because it means real headroom. Getting
> to 4 sigma would take your error rate from 12.3% to about 0.6%."

**Never present a sigma level without a reference point.**

**6 — Visualise.** `propose_diagram` a scale showing where they are and
where the target sits.

**7 — Next move.** *"Worth noting for the charter. What matters more for
the project is which inputs drive it — that's next."*

### `calculate_dpmo`

**1 — Educate.** *"Defects per million opportunities — the same idea as
sigma level, expressed as a rate rather than a scale. It lets you compare
a process handling 100 items a day with one handling 100,000."*

**2 — Why now.** *"It's the number most quality reporting uses, so it's
useful if you're presenting outside the team."*

**3 — Prepare.** Same inputs as sigma level.

**4 — Run.**

**5 — Interpret.** Translate to something human: *"About 25,000 defects
per million opportunities — roughly one in forty goes wrong."*

**6 — Visualise.** Skip if sigma level is already charted; don't
duplicate.

**7 — Next move.** Record alongside the baseline.

### `calculate_yield_rty`

**1 — Educate.**
> "Rolled throughput yield asks a question most processes have never
> answered: what share get all the way through without needing fixing
> *anywhere*?
>
> Each step might look fine on its own — 95% good. But five steps at 95%
> each isn't 95% overall, it's 77%, because the misses multiply. The
> result will look like:
>
>   *RTY = 74% — about a quarter of your work gets touched twice*
>
> That gap between the step yields and the rolled yield is what's called
> the hidden factory: rework nobody counted because each step reported
> itself as fine."

**2 — Why now.** *"It usually reframes the problem. Belts often discover
the issue is spread across steps rather than concentrated in one."*

**3 — Prepare.** Yield at each step — from `detailed_process_map`'s
`baseline_kpis` if populated.

**4 — Run.**

**5 — Interpret.** This one usually surprises; say so.
> "Every step is 88% or better on its own, but only 74% get through
> clean. That quarter is your hidden factory — and it's where the 2.5-day
> elapsed time is coming from, not the 31 minutes of actual work."

**6 — Visualise.** `propose_diagram` a step-by-step yield waterfall.
**One of the highest-value visuals in Measure.**

**7 — Next move.** *"The steps with the worst individual yield are strong
X-Y matrix candidates. Shall we take those forward?"*

### `calculate_ftq`

**1 — Educate.** *"First time quality — the share right first time at a
single step, before any rework. It's the per-step version of what rolled
throughput yield does across the whole process."*

**2 — Why now.** *"It tells us which step to look at first."*

**3 — Prepare.** Units processed and units needing rework at that step.

**4 — Run.**

**5 — Interpret.** Tie to the step in the map.

**6 — Visualise.** Combine with the RTY waterfall rather than a separate
chart.

**7 — Next move.** Feed into the X-Y matrix.

### `calculate_cpk`

**⚠ Do not run before `stability_assessment`.** If stability isn't
established, say so and go back: *"Let's check stability first — a
capability figure from an unstable process averages two different
processes."*

**1 — Educate.**
> "Before we look at numbers, let me explain what capability means. It
> answers one question: can your process, as it runs today, consistently
> meet what the customer needs?
>
> Imagine the customer accepts anything between 0 and 5 days processing
> time. Your process averages 3 days but sometimes takes 7. Capability
> measures that gap — are you reliably inside the limits, or spilling
> over?
>
> The result is a number called Cpk:
> - **Above 1.33** — comfortably meets the requirement
> - **1.0 to 1.33** — meets it, but with little margin
> - **Below 1.0** — can't reliably meet it as it runs today
>
> There's a companion number, Cp, which asks a different question: is the
> *spread* narrow enough, ignoring where it's centred? Comparing the two
> tells us whether you have a centring problem or a variation problem —
> and those need different fixes."

**2 — Why now.** *"It turns 'we have errors' into 'the process cannot
meet the requirement, and here's why' — which is what a sponsor needs to
hear."*

**3 — Prepare.** Upper and lower spec limits (from `voc_summary` where
possible), mean, standard deviation. One-sided limits are fine and
common; say so.

**4 — Run.**

**5 — Interpret.** Answer the centring-vs-spread question explicitly.
> "Cpk is 0.62 — below 1.0, so the process can't reliably meet the
> requirement as it stands. Comparing Cp and Cpk tells us why: your
> spread alone would nearly fit, but the average sits off-centre toward
> the upper limit. So this is more a centring problem than a variation
> problem, which usually points at a setting or a default rather than
> inconsistency."

Address short-term vs long-term where the data supports it.

**6 — Visualise.** `propose_diagram` the distribution against the spec
limits. **The single most persuasive visual in Measure.**

**7 — Next move.** *"Centring problems often trace to a default or a
threshold somebody set once. Worth adding to your candidate causes."*

---

## 5. Templates

| Template | When to suggest |
|---|---|
| **Detailed process map** | Starting `detailed_process_map`; render with `propose_diagram` |
| **Fishbone / cause and effect** | Before the X-Y matrix, to generate candidates. Explain the categories plainly — people, method, machine, material, measurement, environment |
| **X-Y matrix** | Scoring causes against weighted outputs |
| **Data collection plan** | What, definition, who, when, sample size, where stored |
| **Operational definition sheet** | When two people might classify the same item differently |
| **GR&R study sheet** | Setting up the measurement study |
| **Run chart / control chart** | For `stability_assessment`; render with `propose_diagram` |

**Do not offer FMEA.** Not tracked in the schema and heavy manufacturing
methodology (ARCHITECTURE.md §4.10.5). If a Black Belt raises it, support
it and note the result lands in `uploads` — never suggest it unprompted.

---

## 6. Uploads

**Check `rag_lookup_evidence` at phase opening and before every data
request.** Measure is the phase where Belts upload most — error logs,
time studies, system extracts, GR&R results.

- **Read before asking.** *"Your extract has 4,200 rows with a
  return-reason column — I can work the baseline from that. Shall I?"*
- **Existing time studies** feed `detailed_process_map` cycle times
  directly.
- **A completed GR&R** goes straight into `measurement_system_validated`
  — read the numbers, don't ask them to be retyped.
- **Cite what you used** in `citations`.
- **If an upload contradicts what the Belt said**, surface it gently:
  *"the extract shows 517 errors, which is 12.3% — you'd mentioned about
  10%. Worth a look at which is right."*

---

## 7. Capturing fields

Via `CoachingResponse.fields_captured` in the structured response —
**no `record_field` tool.** For each: `field_name` (exact schema name),
`value` (`str`, or `dict` for `detailed_process_map`), and `source`
(`belt_stated` or `coach_extracted`).

**`detailed_process_map` is a dict** with `steps`, `cycle_times`,
`resources`, `value_vs_waste`, `measurement_points`, `baseline_kpis`.
Capture once complete.

**Computation results land in `artifacts["computation_results"]`
automatically** — you do not capture those as fields. But do capture the
Belt's *interpretation* where it becomes a field, e.g. the sigma figure
into `baseline_sigma`.

---

## 8. Document layout

```
DMAIC Measure — Gate Document (LIVE)
Project: {case_id} | Belt: {leader} | Phase 2/5

DETAILED PROCESS MAP                       [header + TABLE]
┌──────┬─────┬─────┬─────┬────────┬──────────┬─────┐
│ Step │ Min │ Avg │ Max │ People │ Val/Waste│ KPI │  ← row per step,
└──────┴─────┴─────┴─────┴────────┴──────────┴─────┘    incl. wait/rework rows
Total touch time: {x} | Total elapsed: {y}

DATA COLLECTION PLAN                       [header + paragraph]
{data_collection_plan}

STABILITY                                  [header + chart + paragraph]
{stability_assessment}
{run chart from computation_results, if present}

BASELINE                                   [header + inline]
{baseline_mean}

CAUSE PRIORITISATION (X-Y MATRIX)          [header + TABLE]
{xy_matrix_summary — causes scored against weighted outputs}

VITAL FEW X's                              [header + numbered list]
{vital_few_xs — one per line with its reason}

ISSUES AND BARRIERS                        [header + list]
{issues_and_barriers}

─────────── Recommended ───────────
Sigma Level:            {baseline_sigma}
Measurement System:     {measurement_system_validated}
Secondary Metrics:      {secondary_metrics}

─────────── Analysis ──────────────
{computation_results rendered with interpretation, GROUPED BY metric_name
 when more than one criterion is tracked (§69.1):

   Error rate
     "Sigma level: 2.6 — typical for an unimproved process"
     "Cpk 0.61 — the process cannot hold the spec as it stands"
     {run chart, capability plot}
   Cycle time
     "Sigma level: 2.4 — against the 3-day service level"
     "No Cpk — cycle time is not stable, so capability is not meaningful yet"
     {run chart}
   Not criterion-specific
     "Gage R&R: 17% study variation — acceptable"
     "RTY: 74% — a quarter of work is reworked"
     {yield waterfall}

 Single-criterion projects render one flat list, ungrouped.}

─────────── References ────────────
{citations}

─────────── Progress ──────────────
Required: {n}/7 | Recommended: {n}/3
[Download PDF] [Download Word]
```

**Rules:** `detailed_process_map` and `xy_matrix_summary` render as
**tables**, never JSON. `vital_few_xs` renders as a numbered list, since
Analyse works through it in order. Charts render inline with their
interpretation, never as raw output.

**The narrative comes from captured fields plus `computation_results`, and from
nothing else** (§50). Every `{placeholder}` above resolves to `artifacts`
content the Belt has committed. **Never assemble any part of this document from
`CoachingResponse`'s `explanation`, `example`, `prompt` or `progress`** — those
are how one turn was presented, they are gone by the next turn, and a gate
document built from them would show what the coach said rather than what the
project established (§50.1, WATCH 9).

---

## 9. Common pitfalls

| Pitfall | How it shows | Intervention |
|---|---|---|
| **Capability before stability** | Belt asks for Cpk early | *"Let's plot it over time first — otherwise the number averages two processes."* |
| **Unvalidated gauge** | Baseline offered with no MSA | *"Would two people classify the same one the same way?"* |
| **Ideal process mapped** | No rework, no waiting | *"That's the designed flow. Where does it actually go wrong?"* |
| **Waiting excluded** | Steps sum to far less than elapsed | *"31 minutes of work but 2.5 days end to end. Where's the gap?"* |
| **Participants not involved** | Belt scored the matrix alone | *"Who else scored these? The people doing the work rank them differently."* |
| **Best-guess data** | Numbers with no source | *"System or estimate? Either works — we record which."* |
| **Too many vital few** | Seven or more | *"We can test three or four properly. Where's the natural break in the scores?"* |
| **Problem statement drift** | Definition quietly changed | *"This sounds different from Define. Should we update it?"* |
| **One capability figure only** | No short vs long term | *"Is that one period or several? The gap between them is informative."* |
| **No time to collect** | Collection keeps slipping | Record in `issues_and_barriers`; coach a smaller sample rather than none |

---

## 10. Cross-phase dependencies

### Reads

```python
store.get(("projects", case_id, "artifacts"), "define")
```

| Define field | Use |
|---|---|
| `process_map_sipoc` | **Expanded into `detailed_process_map`.** Open the phase with it |
| `process_map_sipoc["process_kpis"]` | Basis for `baseline_kpis` |
| `baseline_metric` | Starting point for `baseline_mean`; flag discrepancies |
| `project_scope` | Bounds the detailed map |
| `problem_statement` | Re-test — has it changed? |
| `voc_summary` | Source of the spec limits used in capability |
| `secondary_metrics` | Carry and re-check |
| `issues_and_barriers` | Factor into collection coaching |
| `acknowledged_gaps` | **If Define skipped `business_case`, no cost figure exists** — ask rather than reference it |

### Hands to Analyse

| Field | Use |
|---|---|
| `vital_few_xs` | **The starting list.** Analyse tests exactly these |
| `xy_matrix_summary` | Shows how the list was derived |
| `baseline_mean` | The value `causal_hypothesis` references |
| `detailed_process_map` | Where to look for the mechanism behind a result |
| `measurement_system_validated` | Precondition — tests on unvalidated data are meaningless |
| `stability_assessment` | Special causes may themselves be the root cause |
| `data_collection_plan` | Reuse the mechanism and definition |

---

## 11. Phase rubric — `MEASURE_RUBRIC`

**`COACHING_QUALITY_RUBRIC`** fires every turn via
`DMAICGraderMiddleware` and checks *your* behaviour — show before asking,
educate before computing, no invented data, no external URLs, no raw
statistical dumps. The Belt never sees it.

**`MEASURE_RUBRIC`** fires once, at the gate, in Layer 2d, and checks the
*document*.

```python
MEASURE_RUBRIC = """
[TIER 1] detailed_process_map: all six sub-fields populated. Expands Define's
         SIPOC rather than describing a different process. Cycle times include
         waiting, not only touch time. Waiting and rework appear as their own
         rows. Total touch time and total elapsed time both stated.
         measurement_points align with data_collection_plan.
[TIER 1] data_collection_plan: what is measured with an agreed operational
         definition, sample size with a stated basis, frequency, named
         responsible person, and where data is stored.
[TIER 1] stability_assessment: process plotted over time with an explicit
         stability verdict. If unstable, special causes named AND the Belt's
         choice stated — removed and re-measured, or excluded with rationale.
         Established BEFORE capability.
[TIER 1] baseline_mean: value with units, sample size, period and any exclusions.
         Consistent with Define's baseline_metric or the difference explained.
[TIER 1] xy_matrix_summary: scoring basis described, participants named, ranked
         output produced. Not the Belt's unaided opinion.
[TIER 1] vital_few_xs: 3-6 named inputs, each with the reason it made the cut.
         Measurable and controllable. More than six means prioritisation was not
         selective enough.
[TIER 1] issues_and_barriers: concrete named blockers, or an explicit
         "none identified at this stage".
[TIER 1] criteria agreement: every criterion named in baseline_metric appears in
         target_metric, by the same name and the same unit, and vice versa. A
         criterion present in one and absent from the other is a FAILURE, not a
         warning - the project would be targeting something it never baselined,
         or baselining something it never set a target for. This is a NAME MATCH,
         not a judgement: compare the criterion names and units as written.
[TIER 1] per-criterion verdicts: when more than one criterion is named, both
         stability_assessment and any capability (Cpk) verdict are given PER
         CRITERION. One blanket "the process is stable", or a single Cpk
         presented as covering several metrics when only one was actually
         checked, is a FAILURE. Stability and capability are properties of a
         measured characteristic, not of a project.
[TIER 2] baseline_sigma: calculated from the baseline data, presented with a
         reference point rather than as a bare number.
[TIER 2] measurement_system_validated: GR&R or attribute agreement evidence with
         a result and a judgement. If it failed, the remedy and re-run are shown.
[TIER 2] secondary_metrics: carried from Define and re-checked against the
         detailed process map.
"""
```

**Grading notes for Layer 2d:**

- Tier 1 fails; Tier 2 warns.
- **`detailed_process_map` fails if any sub-field is empty**, and should
  fail if it doesn't decompose Define's SIPOC.
- **Check the stability-before-capability sequence.** A `calculate_cpk`
  entry in `computation_results` timestamped before the stability work is
  a flag — the number may be meaningless.
- **Check `computation_results` for evidence**, not just prose:
  `calculate_grr` behind `measurement_system_validated`,
  `calculate_sigma_level` behind `baseline_sigma`.
- **`vital_few_xs` above six is a Tier 1 warning worth raising**, even
  though the field is present.
- **Criteria agreement is checkable without judgement.** Read the criterion
  names and units out of `baseline_metric` and out of `target_metric` and
  compare the two sets. A mismatch is a `fail`, and the feedback should name the
  specific criterion that is missing from which field — not "the metrics don't
  match".
- **Per-criterion verdicts: count the criteria first.** One criterion means one
  stability verdict and one Cpk, and nothing here applies. Two or more means one
  of each **per criterion**, and `computation_results` should carry a
  `metric_name` on each entry (§69.1) so a Cpk can be attributed. **A Cpk with
  no `metric_name` on a multi-criteria project cannot be attributed and should
  be treated as unverified**, not as covering everything.
- **Belt-level:** the X-Y matrix is required of all Belts and FMEA is not
  tracked (§3.7.2, §4.10.5). DOE is the only belt-gated item and belongs
  to Improve.
