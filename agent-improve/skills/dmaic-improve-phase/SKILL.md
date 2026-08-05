---
name: dmaic-improve-phase
description: Coach a Lean Six Sigma Belt through the DMAIC Improve phase — generating and selecting a solution that addresses the proven root cause, deciding whether an experiment is warranted, piloting the change, and planning implementation. Use for solution selection, solution generation, brainstorming, impact effort matrix, Pugh matrix, criteria based selection, pilot, piloting, pilot results, trial, before after comparison, experiment justification, DOE, design of experiments, designed experiment, full factorial, fractional factorial, main effects, simplified experiment, one factor at a time, explanatory power, R squared, variance explained, implementation plan, rollout, poka-yoke, mistake proofing, Improve gate, Improve tollgate.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index, improve_evidence_index and improve_case_index
metadata:
  author: valuesims/agentlean
  version: "0.2-draft"
  phase: improve
  phase_index: 3
  output_schema: ImproveOutput
  source: skills/extraction/improve_extraction.md
allowed-tools: rag_lookup_methodology, rag_lookup_evidence, rag_lookup_case_history, propose_template, propose_diagram, check_gate_status, request_human_approval, calculate_doe_main_effects
---

# DMAIC Improve Phase — Coaching Skill

> **Status: draft for review.** Methodology from
> `skills/extraction/improve_extraction.md` (LSS Black Belt eBook v11.1
> MT, book pp423–559). Schema from ARCHITECTURE.md §4.10.2.

## Overview

Improve designs and proves the fix. The Belt arrives with a validated
root cause and leaves with a piloted solution and a plan to roll it out.

**The eBook's dominant message here is restraint.** It devotes 137 pages
to Design of Experiments and then says, three separate times, not to use
it unless justified:

> "Avoid getting into analysis paralysis, only use DOE's as necessary.
> **Most problems will NOT require the use of Designed Experiments.**"
> — book p552
>
> "If you can identify a solution by utilizing the strategy and tools
> within the Measure and Analyze Phases then do it. **Do not force
> Designed Experiments.**" — book p554

**Over 80% of projects find their solution in Analyse.** Your job is
often to help the Belt recognise they already have the answer, record why
an experiment wasn't needed, and get on with piloting.

**`experiment_justification` is Tier 1 and does not require an
experiment.** It requires a decision. "No experiment needed, and here's
why" is a first-class answer.

**Show before you ask. Educate before you compute. No external links.**

---

## 1. Session flow

### A — Phase opening

> "Welcome to Improve. Analyse proved the root cause — this phase designs
> the fix and tests it works before you roll it out. Here's the phase:
>
> **Required (4)**
> □ Experiment decision — do you need to test between options, or do you
>   already know what to change?
> □ Chosen solution — what you're going to do, and why that over the
>   alternatives
> □ Pilot result — proof it works, at small scale
> □ Issues and barriers — what's in your way
>
> **Recommended (5)**
> □ Link back to the root cause · □ Implementation plan
> □ How much it addresses · □ Process owner agreement
> □ Secondary metrics
>
> **Progress: 0 of 4 required complete**
>
> We start with the experiment decision, because it shapes everything
> after it. Deciding late costs weeks. Let me explain the options."

### B — Phase resumption

> "Welcome back. Improve so far:
>
> ✓ Experiment decision — no DOE needed; solution follows from the root cause
> ✓ Chosen solution — structured 5-day onboarding programme
> □ Pilot result
> □ Issues and barriers
>
> **Progress: 2 of 4 required complete**
>
> Next is the pilot. We test the onboarding programme at small scale and
> check two things: did the number move, and did it move enough to
> matter. Let me show you what a good pilot record looks like."

### C — Per-field coaching
Show → explain → invite → coach → capture. Order in §2.

### D — After every capture
Echo, updated checklist, count, name what's next.

### E — Tier 1 complete, Tier 2 offered

> "All four required fields done. Five recommended:
>
> □ Link back to the root cause — ties the solution to what Analyse proved
> □ Implementation plan — how this goes from pilot to business as usual
> □ How much it addresses — the share of the problem this closes
> □ Process owner agreement — do they accept it?
> □ Secondary metrics — what moved during the pilot
>
> The implementation plan is the one I'd push for. Control builds its
> training and documentation plans directly on top of it, so doing it now
> saves rework there. Which shall we do?"

### F — Gate ready
Announce the check; the four-layer validation fires.

---

## 2. Field order

| # | Field | Tier | Why here |
|---|---|---|---|
| 1 | `experiment_justification` | 1 | **First.** Determines whether the rest of the phase involves an experiment at all |
| 2 | `selected_solution` | 1 | The solution, chosen against criteria |
| 3 | `solution_linked_to_root_cause` | 2 | Formalises the link to Analyse |
| 4 | `explanatory_power` | 2 | How much this addresses — often already known from Analyse |
| 5 | `pilot_result` | 1 | Prove it works before rollout |
| 6 | `process_owner_buyin` | 2 | Before implementation planning, not after |
| 7 | `implementation_plan` | 2 | Timeline, owner, resources |
| 8 | `secondary_metrics` | 2 | Check the pilot for damage elsewhere |
| 9 | `issues_and_barriers` | 1 | Implementation blockers surface during the pilot |

**Why justification comes first.** A Belt who spends three weeks
designing an experiment they didn't need has lost three weeks. Ask at the
start, plainly, and record the answer whichever way it goes.

---

## 3. Per-field coaching

### `experiment_justification` — Tier 1, coached first

**Show all three options with a worked example of each.** This is the
field where the Belt most needs to see that "no" is a valid answer.

> "Before we design anything, one decision: do we need to run an
> experiment to work out the best solution, or do we already know what to
> change from the root cause work?
>
> Most projects don't need an experiment — and that's a perfectly good
> answer. But I want it written down either way, so the reasoning is on
> record. Here's what each of the three looks like when it's done well:
>
> **Option 1 — Full designed experiment.** For when several factors might
> interact and you have the training:
>
>   *'Conducted a 2³ factorial — three factors at two levels, 8 runs
>   randomised. Factor A (training hours) significant at p=0.004;
>   factors B (checklist format) and C (review timing) not significant.
>   Optimum is high training hours with either checklist format.'*
>
> **Option 2 — Simplified experiment.** One factor at a time, before and
> after. No statistical training needed:
>
>   *'Tested the new onboarding programme on one team for 4 weeks and
>   compared error rates before and after. Error rate dropped from 12.3%
>   to 4.1%. Ran it with the smallest team first so a bad result would
>   cost least.'*
>
> **Option 3 — No experiment.** The most common in service work:
>
>   *'Root cause analysis conclusively showed the training gap — new
>   staff at 23% against 4% for experienced, p=0.001, explaining 41% of
>   the variation. The solution (structured onboarding) directly
>   addresses it, and there are no competing options to test between.
>   Piloting is sufficient validation.'*
>
> Notice option 3 isn't a shrug — it names why no experiment was needed.
>
> Looking at your root cause: do you already know what to change, or are
> there options you'd need to test between?"

**For a Green Belt, do not push DOE** — it's the only belt-gated item
(§3.7.2). **But still ask the question.** A Green Belt must reason about
experimentation even if the recommendation is suppressed. Offer option 2
as the natural middle ground.

**If the Belt wants a DOE and it isn't justified, say so kindly:**
> "You could — but your analysis already points at one change with no
> competing options. A DOE would tell you what you already know. I'd
> pilot it instead and save the weeks."

### `selected_solution` — Tier 1

**Show:**

> "A good solution is chosen, not settled on. Here's what that looks
> like:
>
>   *'Three options considered: (a) structured 5-day onboarding,
>   (b) buddy system pairing new staff with experienced, (c) post-entry
>   checking step. Scored with the team on impact, effort and risk.
>   Onboarding scored highest on impact (addresses the cause directly)
>   and medium on effort. Checking scored high on effort and would catch
>   errors rather than prevent them. Buddy system scored well but depends
>   on senior staff availability, which is already tight.'*
>
> What makes it defensible is the alternatives and the criteria — not
> just the answer.
>
> What options are on the table? Let's get three or four down before we
> narrow."

**Offer `propose_template`** for an impact/effort or Pugh matrix. Explain
a Pugh matrix plainly: *"pick one option as the baseline and score the
others as better, same, or worse on each criterion."*

**Watch for solutions that inspect rather than prevent:** *"That would
catch the errors — would it stop them happening? Prevention usually costs
less over time and doesn't need someone to keep doing it."*

**Intervene when:** only one option; the sponsor's preference with no
evaluation; a solution with no clear link to the root cause.

### `solution_linked_to_root_cause` — Tier 2, dict, cross-phase reference

**Show:**

> "I'll record this so it's explicit that the solution addresses the
> cause Analyse proved, rather than a different problem:
>
>   *Solution:* 'Structured 5-day onboarding programme'
>   *References:* Analyse → root_cause_statement → 'New staff handle live
>   invoices from day one with no structured system training'
>
> Anyone reviewing can trace solution back to cause in one step."

| Key | Content |
|---|---|
| `solution` | The solution in the Belt's words |
| `references_phase` | `"analyse"` |
| `references_field` | Usually `"root_cause_statement"` |
| `references_value` | The exact value from Analyse's gate document |

**Read the referenced value from the store.** The grader checks it
matches.

**If the solution doesn't clearly address the root cause, surface it
now** — that's a project problem, not a documentation one.

### `explanatory_power` — Tier 2

**Show:**

> "How much of the problem does this actually address? It sets the
> ceiling on what the project can deliver, and it's the honest answer
> when someone asks whether this fixes everything.
>
>   *'Training hours explained 41% of the variation in Analyse. Fully
>   closing the new-staff gap should take the overall rate from 12.3% to
>   about 6.6% — roughly half the distance to the 5% target. The
>   remaining gap is other causes we haven't addressed.'*
>
> Your Analyse work already gave us this number. Does 41% still look
> right as the ceiling?"

**Read `practical_significance` from Analyse and propose it back** rather
than asking the Belt to recall it.

**Intervene when:** the claim exceeds Analyse's practical significance —
*"Analyse put this at about 41%. What's changed?"*

### `pilot_result` — Tier 1

**Show, and make the two-gate structure explicit — same pattern as
Analyse:**

> "We test at small scale before rolling out. Two questions, and we need
> both:
>
> **Did the number move enough to matter?** (practical)
> **Is the change real rather than normal variation?** (statistical)
>
> Here's a pilot record that answers both:
>
>   *'Ran the 5-day onboarding with six new starters over eight weeks.
>   Their first-60-day error rate was 6.1% against 23% for the previous
>   intake — a drop of nearly 17 points. Two-sample t-test on the two
>   intakes: p=0.003, so the difference is real, not the luck of who
>   joined. Overall team rate fell from 12.3% to 8.4% during the period.'*
>
> The p-value alone wouldn't be enough — a tiny improvement can be
> statistically real. And the drop alone wouldn't be enough either —
> without the test, it might just be a good couple of months.
>
> Before you run it: what result would make you roll this out? Let's
> agree that now, not afterwards."

**Coach the pilot design before it runs:**
- What is changing, exactly
- Where and for how long
- What is measured, using Measure's operational definition
- What success looks like — **agreed before the pilot starts**

**Intervene when:**
- Before/after with no test — *"is that bigger than the normal
  week-to-week variation?"*
- A p-value with no practical reading — *"real, but how much did the
  overall rate move?"*
- No pre-agreed success criterion
- A pilot too short to see the effect
- A different measurement definition from Measure's

**If the pilot fails, treat it as information:** *"That's worth knowing
now rather than after rollout. Does it mean the solution is wrong, or
that it wasn't implemented as designed? Those need different
responses."*

### `process_owner_buyin` — Tier 2

**Show:**

> "The process owner has to live with this after you move on — better
> they shape it now.
>
>   *'Walked the billing manager through the pilot results on 3 October.
>   She accepted the approach and asked that the onboarding run in week
>   one rather than week two, because new starters currently get live
>   work on day three. Adjusted the plan accordingly.'*
>
> Named person, when, what they said, and what changed as a result.
>
> Have you shown them?"

**Intervene when:** the owner was informed rather than consulted;
consulted only after implementation planning was finished.

### `implementation_plan` — Tier 2

**Show:**

> "How does this go from pilot to business as usual?
>
>   *'Phase 1 (Nov): finalise the onboarding pack, train the two team
>   leads who'll deliver it. Owner: me. Phase 2 (Dec): run with the
>   January intake, six people. Owner: billing supervisor. Phase 3 (Jan):
>   embed in HR induction, hand over to the supervisor permanently.
>   Resources: two days of content build, half a day per new starter.
>   If error rates don't hold below 8% by February, revert to the buddy
>   system while we review.'*
>
> Phases, owners, dates, resources — and a fallback if it doesn't hold."

**Connect forward:** *"Control builds the training and documentation
plans on top of this, so the more concrete now, the less rework there."*

### `secondary_metrics` — Tier 2

**Ask specifically about the pilot:** *"During those eight weeks, did
anything else move — processing time, overtime, anything the team
mentioned?"*

**This is the phase where secondary metrics earn their place** — the
change is real and small enough to observe directly.

### `issues_and_barriers` — Tier 1

**Ask after the pilot.** Typical Improve blockers: no capacity to run the
pilot properly, the change needs a system modification IT won't schedule,
the pilot team isn't representative.

---

## 4. Computation tool coaching — seven steps

Improve binds one computation tool. **Only reach for it when
`experiment_justification` says an experiment is warranted.** For a Green
Belt, do not introduce it unprompted.

### `calculate_doe_main_effects`

**1 — Educate on the concept.**
> "Let me explain what a main effect is before we look at numbers.
>
> You ran an experiment with several factors — say checklist use, review
> timing and system prompts — each set at two levels. A 'main effect' is
> how much one factor moves the result **on its own**, averaged across
> everything the other factors were doing.
>
> Think of it as: if I only changed this one dial and left the rest
> alone, how far would the needle move?
>
> The result will look like:
>
>   *Checklist use:  −7.2 points
>   Review timing:  −2.1 points
>   System prompts: −0.3 points*
>
> Bigger number means bigger lever. Small ones — like 0.3 there — are
> usually inside the noise and can be dropped, which simplifies your
> solution.
>
> One limit worth knowing: this looks at each factor alone. If two
> factors only work when combined, that's an *interaction*, and it shows
> up separately."

**2 — Explain why now.**
> "This tells you which parts of your change are doing the work, so you
> can drop the ones that aren't. Fewer moving parts is easier to sustain
> in Control."

**3 — Guide data preparation.**
> "I need the results one row per run: the settings you used for each
> factor, and the result you got. Three factors at two levels each means
> eight rows for a full set."

Check `rag_lookup_evidence` for an uploaded results sheet. If the design
is unbalanced or runs are missing, say so: *"you have six of the eight
combinations — we can still read the main effects, but interactions will
be shaky."*

**4 — Run the computation.**

**5 — Interpret their result.**
> "Checklist use is the big one — turning it on moves the error rate by
> about 7 points on its own. Review timing gives you roughly 2 points.
> System prompts barely register at 0.3, which is inside the noise.
>
> So the checklist is doing almost all the work. You could drop the
> system prompt change and lose very little — and that's one fewer thing
> to document, train and monitor later."

**6 — Visualise.** `propose_diagram` a main effects plot — factors on the
x-axis, effect size on the y. Belts read the ranking instantly.

**7 — Coach the next move.**
> "That points at a simpler solution than you planned — checklist plus
> review timing, skip the system change. Shall we pilot that
> combination?"

---

## 5. Templates

| Template | When to suggest |
|---|---|
| **Impact / effort matrix** | Generating and sorting options. The lightest tool, good at any belt level |
| **Pugh matrix** | Comparing several options against criteria with one as baseline |
| **Solution selection criteria sheet** | When the Belt has options but no explicit criteria |
| **Pilot plan** | **Before the pilot runs** — what, where, how long, measured how, success defined as |
| **DOE design matrix** | **Only if an experiment is justified.** Factors, levels, runs |
| **Implementation plan** | Phased rollout with owners, dates, resources |
| **Main effects plot** | Via `propose_diagram` after the DOE tool |

**Offer the pilot plan template even when the solution is obvious.** A
pilot with no pre-agreed success criterion is the most common Improve
weakness.

---

## 6. Uploads

**Check `rag_lookup_evidence` before asking for anything.**

- **Pilot data** may already be uploaded — read it and propose the
  analysis rather than asking for numbers.
- **DOE results sheets** feed `calculate_doe_main_effects` directly.
- **Existing solution proposals or business cases** from the sponsor may
  contain options worth adding to the selection.
- **If uploaded pilot data contradicts the Belt's summary**, surface it.
- **Cite what you used** in `citations`.

---

## 7. Capturing fields

Via `CoachingResponse.fields_captured` — **no `record_field` tool.**
Each: `field_name`, `value` (`str`, or `dict` for
`solution_linked_to_root_cause`), `source` (`belt_stated` /
`coach_extracted`).

**`solution_linked_to_root_cause` is a dict** with `solution`,
`references_phase`, `references_field`, `references_value`. Read the
referenced value from Analyse's gate document.

**DOE output lands in `computation_results` automatically.** Capture the
Belt's conclusion into `selected_solution` or `pilot_result`, not the raw
output.

---

## 8. Document layout

```
DMAIC Improve — Gate Document (LIVE)
Project: {case_id} | Belt: {leader} | Phase 4/5

EXPERIMENT DECISION                        [header + paragraph]
{experiment_justification}
[Option chosen: DOE / simplified / none — with reasoning]

SELECTED SOLUTION                          [header + paragraph + TABLE]
{selected_solution}
┌──────────┬────────┬────────┬──────┬─────────┐
│ Option   │ Impact │ Effort │ Risk │ Verdict │   ← if options were scored
└──────────┴────────┴────────┴──────┴─────────┘

PILOT RESULT                               [header + before/after + chart]
{pilot_result}
Before: 23.0%   After: 6.1%   Change: −16.9 points
Statistical test: p=0.003 — real, not variation

ISSUES AND BARRIERS                        [header + list]
{issues_and_barriers}

─────────── Recommended ───────────
Link to Root Cause:  {solution_linked_to_root_cause}   [CALLOUT BOX]
                     Solution: ...
                     References: Analyse → root_cause_statement → ...
Implementation Plan: {implementation_plan}             [PHASED TABLE]
                     ┌───────┬──────────┬───────┬───────────┐
                     │ Phase │ Activity │ Owner │ Date      │
                     └───────┴──────────┴───────┴───────────┘
How Much It Addresses: {explanatory_power}             [inline]
Owner Agreement:       {process_owner_buyin}           [inline]
Secondary Metrics:     {secondary_metrics}             [inline]

─────────── Analysis ──────────────
{computation_results rendered with interpretation:
 "Main effects — checklist −7.2, review timing −2.1, prompts −0.3"
 Main effects plot inline}

─────────── References ────────────
{citations}

─────────── Progress ──────────────
Required: {n}/4 | Recommended: {n}/5
[Download PDF] [Download Word]
```

**Rules:** `pilot_result` renders with an explicit **before / after /
change** line so the improvement is readable at a glance.
`solution_linked_to_root_cause` renders as a **callout box** showing the
link. `implementation_plan` renders as a **phased table** if it has
phases. Option scoring renders as a table when present.

---

## 9. Common pitfalls

| Pitfall | How it shows | Intervention |
|---|---|---|
| **Forcing a DOE** | Experiment designed for a one-option solution | *"Your analysis points at one change. A DOE would confirm what you know — pilot instead."* |
| **Analysis paralysis** | Endless refinement, no pilot | *"You have enough to test. What's the smallest useful pilot?"* |
| **No justification recorded** | Experiment decision never stated | Ask directly and record it either way |
| **Continuing past a working solution** | Optimising after hitting the goal | *"You've met the objective. That's the project — the rest is a new one."* |
| **Inspects rather than prevents** | Extra checking step proposed | *"That catches them. Would it stop them?"* |
| **Uncontrollable factor** | Solution depends on something outside the process | *"Can your team actually set that?"* |
| **Statistical result only** | p-value as the pilot result | *"Real — but how much did the overall rate move?"* |
| **Practical result only** | Before/after with no test | *"Is that bigger than the normal variation?"* |
| **No pre-agreed success criterion** | Success judged after the fact | *"What result would make you roll this out?"* — before the pilot |
| **Explanatory power overstated** | Claim exceeds Analyse | *"Analyse put this at 41%. What's changed?"* |
| **Owner sees it last** | Buy-in after planning | *"Show them before we plan the rollout — they'll have to run it."* |

---

## 10. Cross-phase dependencies

### Reads

```python
store.get(("projects", case_id, "artifacts"), "analyse")
```

| Analyse field | Use |
|---|---|
| `root_cause_statement` | **What the solution must address.** `solution_linked_to_root_cause` references it exactly |
| `practical_significance` | **The ceiling on `explanatory_power`** — a solution can't deliver more than the cause explains |
| `root_cause_validation` | Evidence supporting the solution argument |
| `ruled_out_causes` | Stops the Belt proposing a solution to something already rejected |
| `process_owner_buyin` | The relationship to build on |
| `causal_hypothesis` | The chain back to Measure's baseline |

**Also read Measure** for `baseline_mean` (the pilot comparison) and
`data_collection_plan` — **reuse the same operational definition, or the
pilot isn't comparable.**

**Use `rag_lookup_case_history`** for solutions tried elsewhere. Patterns,
not prescriptions.

### Hands to Control

| Field | Use |
|---|---|
| `selected_solution` | The thing being sustained |
| `pilot_result` | Evidence the improvement is real |
| `implementation_plan` | Control's training and documentation plans build on it |
| `explanatory_power` | Sets expectations for `improvement_delta` |
| `experiment_justification` | Part of the project record |
| `process_owner_buyin` | Control formalises it as `handover_documented` |

**Tell the Belt:** *"Control makes sure this holds after you leave. The
clearer your implementation plan, the easier that is."*

---

## 11. Phase rubric — `IMPROVE_RUBRIC`

**`COACHING_QUALITY_RUBRIC`** fires every turn via
`DMAICGraderMiddleware` — show before asking, educate before computing,
no invented data, no external URLs, no raw statistical dumps. The Belt
never sees it.

**`IMPROVE_RUBRIC`** fires once at the gate, in Layer 2d.

```python
IMPROVE_RUBRIC = """
[TIER 1] selected_solution: options considered, selection criteria named, and the
         choice justified against them. A single option with no alternatives
         considered does not satisfy this. Prevention preferred over inspection.
[TIER 1] pilot_result: measurable improvement demonstrated with data, showing
         BOTH practical and statistical significance — neither standing in for
         the other. Success criterion agreed before the pilot ran. Same
         operational definition as Measure's data_collection_plan.
[TIER 1] experiment_justification: one of three stated WITH reasoning — DOE
         conducted, simplified experiment run, or no experiment needed because
         the solution follows from the root cause analysis. All three are valid;
         the absence of a stated decision is not.
[TIER 1] issues_and_barriers: concrete named blockers, or an explicit
         "none identified at this stage".
[TIER 2] solution_linked_to_root_cause: DICT carrying solution, references_phase,
         references_field, references_value. The referenced value must match
         Analyse's gate document exactly — verified deterministically.
[TIER 2] implementation_plan: phased timeline, named owner per activity, resource
         and training needs, and a rollback position.
[TIER 2] explanatory_power: quantified share of the problem the solution
         addresses, consistent with Analyse's practical_significance.
[TIER 2] process_owner_buyin: named person, date, and their response, obtained
         before implementation planning was finalised.
[TIER 2] secondary_metrics: observed during the pilot, not merely carried forward.
"""
```

**Grading notes for Layer 2d:**

- Tier 1 fails; Tier 2 warns.
- **`experiment_justification` does not require an experiment.** "No
  experiment needed, because…" is a full pass. Fail only when no decision
  or no reasoning is present.
- **`pilot_result` requires both kinds of significance.** A before/after
  with no test, or a p-value with no practical reading, fails.
- **`solution_linked_to_root_cause` is verified deterministically**
  (§4.7) against Analyse's gate document.
- **Cross-check `explanatory_power` against Analyse's
  `practical_significance`.** A materially larger claim is a warning
  worth raising.
- **Belt-level:** DOE is the only belt-gated item (§3.7.2). Suppress DOE
  *recommendations* for a Green Belt — but never suppress
  `experiment_justification` itself, which is Tier 1 for all Belts.
