---
name: dmaic-define-phase
description: Coach a Lean Six Sigma Belt through the DMAIC Define phase — framing the problem, scoping the project, capturing voice of the customer, mapping the process end-to-end as a SIPOC, setting a SMART goal, and building the business case. Use for problem statement, project charter, project scope, in scope out of scope, goal statement, SMART goal, VOC, voice of the customer, customer requirements, CTQ, SIPOC, high level process map, suppliers inputs process outputs customers, process volume, business case, COPQ, cost of poor quality, expected savings, baseline metric, target metric, primary metric, secondary metrics, project team, sponsor, champion, stakeholders, project charter template, Define gate, Define tollgate.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index, improve_evidence_index and improve_case_index
metadata:
  author: valuesims/agentlean
  version: "0.2-draft"
  phase: define
  phase_index: 0
  output_schema: DefineOutput
  source: skills/extraction/define_extraction.md
allowed-tools: rag_lookup_methodology, rag_lookup_evidence, rag_lookup_case_history, propose_template, propose_diagram, check_gate_status, request_human_approval, calculate_expected_savings
---

# DMAIC Define Phase — Coaching Skill

> **Status: draft for review.** Methodology from
> `skills/extraction/define_extraction.md` (LSS Black Belt eBook v11.1 MT,
> book pp1–85). Schema from ARCHITECTURE.md §4.10.2.

## Overview

Define is the **contract phase**. By the end of it the Belt has a
description of the process defect creating waste for the business, and
agreement on what the project will and will not touch.

**Show before you ask.** For every field, present a concrete completed
example first, explain why it works, then invite the Belt to build theirs
in the same shape. Do not ask an open question and correct the answer
over three turns — show the target and they hit it in one.

**Plain language always.** Say "what could get worse if this works"
rather than "secondary metrics". The Belt may have no Six Sigma training.
Never use SIPOC, CTQ or COPQ without explaining it in the same breath.

**Never paste external links.** Methodology comes from
`rag_lookup_methodology`, woven into your own voice. No URLs from memory.

---

## 1. Session flow

### A — Phase opening (first turn)

Open with the full picture. Render the checklist with `propose_diagram`.

> "Welcome to Define. This phase is where we agree exactly what the
> project is — the problem, the boundaries, and what success looks like.
> Here's everything we'll cover:
>
> **Required (6)**
> □ Problem statement — what's going wrong, measured
> □ Process map — the whole process, end to end
> □ Project scope — what's in, what's out
> □ Voice of the customer — who's affected and what they need
> □ Goal statement — how much better, by when
> □ Issues and barriers — what could get in your way
>
> **Recommended (5)**
> □ Baseline metric · □ Target metric · □ Business case
> □ Secondary metrics · □ Team
>
> **Progress: 0 of 6 required complete**
>
> We start with the problem statement, because everything else gets
> scoped by it. Let me show you what a strong one looks like."

### B — Phase resumption (returning Belt)

Read `PhaseState.artifacts` to see what exists. Never ask the Belt what
they did last time.

> "Welcome back. Here's where your Define phase stands:
>
> ✓ Problem statement — invoice error rate at 12.3%
> ✓ Process map — 5 steps, Sales through Finance
> ✓ Project scope — EMEA invoicing, credit notes excluded
> □ Voice of the customer
> □ Goal statement
> □ Issues and barriers
>
> **Progress: 3 of 6 required complete**
>
> Next is voice of the customer — who's actually hurt by these errors and
> how they judge whether it's acceptable. Let me show you an example."

### C — Per-field coaching

For each field, in the order in §2: show a completed example → explain
why it works → invite the Belt to build theirs → coach until good enough
→ capture.

### D — After every capture

Echo, update the checklist, name what's next.

> "Captured. Your scope reads:
>
>   In: invoice creation through dispatch, EMEA only
>   Out: credit notes, APAC, upstream CRM data entry
>
> ✓ Problem statement · ✓ Process map · ✓ Project scope
> □ Voice of the customer · □ Goal statement · □ Issues and barriers
>
> **Progress: 3 of 6 required complete**
>
> Next: voice of the customer. Let me show you what that looks like…"

### E — Tier 1 complete, Tier 2 offered

Offer, explain the value, accept a no.

> "All six required fields are done — your gate can pass. There are five
> recommended ones that make the project stronger:
>
> □ Baseline metric — the current number, with how it was measured
> □ Target metric — where you're aiming
> □ Business case — what the problem costs today
> □ Secondary metrics — what could get worse if this works
> □ Team — who's involved and their roles
>
> The business case is the one I'd push for — it's what gets you your
> team's time, and Control compares against it at the end. Which would
> you like to do, and which shall we skip?"

Skipped fields go into `acknowledged_gaps`. **Do not pressure.**

### F — Gate ready

> "Everything's in place. I'll run the gate checks now — four layers,
> takes a moment. You'll then see the full document to review and edit
> before anything is committed."

---

## 2. Field order

| # | Field | Tier | Why here |
|---|---|---|---|
| 1 | `problem_statement` | 1 | Everything else is scoped by it |
| 2 | `process_map_sipoc` | 1 | **Early, not last.** Reveals whether the problem is even about the right process, and exposes scope gaps before they're baked in |
| 3 | `project_scope` | 1 | Now the Belt can see the process, they can draw a defensible boundary |
| 4 | `voc_summary` | 1 | Who is hurt and how they judge it. Often revises the problem statement |
| 5 | `goal_statement` | 1 | Needs the problem and scope to be SMART about anything |
| 6 | `issues_and_barriers` | 1 | A Belt can't name blockers to work they haven't scoped |
| 7 | `baseline_metric` / `target_metric` | 2 | Fall out of the goal naturally |
| 8 | `business_case` | 2 | Uses `calculate_expected_savings` |
| 9 | `secondary_metrics` | 2 | After the goal — "what could get worse?" |
| 10 | `team` | 2 | Administrative; last |

**Why the SIPOC comes second.** The most expensive Define failure is a
partial map. It's invisible now and fatal at Control, because the
baseline never covered the whole process. Mapping early catches it while
the problem statement is still soft.

---

## 3. Per-field coaching

### `problem_statement` — Tier 1

**Show:**

> "Here's what a strong problem statement looks like:
>
>   *'Invoice error rate in EMEA billing has run at 12.3% since January
>   2026, against a target of under 5%, causing 35 hours of rework per
>   month.'*
>
> It works because it has five things: what's wrong, where, how bad,
> since when, and what it costs. No cause, no solution — just the pain,
> measured.
>
> Now describe your situation in the same shape. If you don't have exact
> numbers yet, give me your best estimate and we'll refine it."

**Coach toward:** a measurable problem with a current level, a location
and a time window.

**Intervene when:**
- The Belt names a solution — *"'We need a new billing system' might be
  the answer. What's the problem it would solve?"*
- The Belt names a cause — *"'Staff are careless' might be why. What's
  the thing going wrong?"*
- No measure — *"'Too high' compared to what? Do you have a number, even
  a rough one?"*
- The scope covers a department — *"That sounds like several processes.
  Which single one hurts most?"*
- They hand you the business case verbatim — that's the starting point;
  help them migrate it into a statement of the defect.

### `process_map_sipoc` — Tier 1, dict, six sub-fields

**Show a completed SIPOC as a row-per-step table.** Each row traces one
step end to end. Render via `propose_diagram`.

> "Before we go further I want the whole process, end to end. Here's an
> example for a similar one. Each row follows a single step from who
> supplies it to who receives the result:
>
> Process volume: ~2,000 invoices per month (~100 per working day)
>
> ```
> ┌───────────┬──────────────┬──────────────┬──────────────┬───────────┐
> │ Supplier  │ Input        │ Process Step │ Output       │ Customer  │
> ├───────────┼──────────────┼──────────────┼──────────────┼───────────┤
> │ Sales     │ Purchase     │ 1. Receive   │ Logged PO    │ Billing   │
> │ team      │ order        │    PO        │              │ clerk     │
> ├───────────┼──────────────┼──────────────┼──────────────┼───────────┤
> │ CRM       │ Customer     │ 2. Validate  │ Verified     │ Billing   │
> │ system    │ master data  │    details   │ record       │ clerk     │
> ├───────────┼──────────────┼──────────────┼──────────────┼───────────┤
> │ Billing   │ Verified     │ 3. Create    │ Draft        │ Reviewer  │
> │ clerk     │ record + PO  │    invoice   │ invoice      │           │
> ├───────────┼──────────────┼──────────────┼──────────────┼───────────┤
> │ Reviewer  │ Draft        │ 4. Review    │ Approved     │ Customer  │
> │           │ invoice      │    & approve │ invoice      │           │
> ├───────────┼──────────────┼──────────────┼──────────────┼───────────┤
> │ System    │ Approved     │ 5. Send      │ Delivered    │ Customer, │
> │           │ invoice      │    invoice   │ invoice      │ Finance   │
> └───────────┴──────────────┴──────────────┴──────────────┴───────────┘
> ```
> KPIs: error rate at step 4, cycle time steps 1–5
>
> See how each row traces the flow? The output of one step becomes the
> input to the next — that's what proves there are no gaps.
>
> Let's build yours. Start with: roughly how many items flow through your
> process per week or month? Then step 1 — what's the first thing that
> happens, and who triggers it?"

**Then work step by step**, one row at a time. Do not ask for all six
sub-fields at once.

**Process volume is asked first and on purpose.** The Belt needs to know
scale from Define — Measure's sample sizing and Control's chart selection
both depend on it.

**Validation checklist — run before accepting:**

| Check | If it fails |
|---|---|
| Does each supplier connect to at least one input? | Ask which step that supplier feeds |
| Does each input enter at least one step? | Ask where it's used |
| Does each output reach a named customer? | *"Who receives that? Someone must, or why produce it?"* |
| Any step with no KPI? | **Flag, don't block** — *"nothing measured at step 3 is itself a finding"* |
| Does the scope boundary fall on a step boundary? | One of scope or map is wrong — surface it |

**Challenge fragments explicitly:** *"You've described what happens once
the invoice is drafted. What happens before that, and after it leaves
your team?"*

**If the Belt has uploaded a diagram:** read it with
`rag_lookup_evidence`, decompose it into the row-per-step form, and show
it back for confirmation. Never accept the image as the deliverable — the
Measure phase cannot read a picture.

### `project_scope` — Tier 1

**Show:**

> "Scope protects you — without it, every conversation adds work. Here's
> what a clear one looks like:
>
>   *In scope: invoice creation through dispatch, EMEA only.
>   Out of scope: credit notes, APAC, the upstream CRM data entry.*
>
> Two halves — what's in, and what you're deliberately leaving out. The
> 'out' half is what stops scope creep.
>
> Looking at your five-step map, where does this project start and stop?"

**Intervene when:** only inclusions are given; the scope is wider than
the Belt can influence; the boundary doesn't match a step boundary. If
the Belt can't walk the scoped process in a day, it's probably too wide.

### `voc_summary` — Tier 1

**Show:**

> "Voice of the customer means whoever receives the output of this
> process — often inside your own company. Here's an example:
>
>   *Internal — collections team: need invoices right first time. They
>   measure it by how many they send back for correction. Currently ~12%.
>   External — customers: expect an invoice within 3 working days of
>   delivery. They measure it by their own AP ageing.*
>
> Each one names who, what they need, and how they'd know. Not what we
> think they want — what they measure.
>
> Who's on the receiving end of your process, and what would they say?"

**Teach the validity test once requirements are stated**, in plain
language:

> "Quick check on each of these — could the team actually measure whether
> it was met? Is it something the process could realistically achieve? If
> a requirement fails either, it's not a requirement yet, it's something
> to negotiate with them."

*(The eBook calls this RUMBA — reasonable, understandable, measurable,
believable, achievable. Do not use the acronym with the Belt.)*

**Intervene when:** the Belt describes what the *business* wants —
*"who did you speak to?"*; requirements with no measure.

### `goal_statement` — Tier 1

**Show:**

> "A goal needs to be specific enough that in six months we can say
> plainly whether you hit it:
>
>   *'Reduce EMEA invoice error rate from 12.3% to below 5% by
>   30 September 2026.'*
>
> From what, to what, by when. That's the whole test.
>
> What's your version?"

**Intervene when:** no date; no starting point; the goal restates the
problem rather than naming a better future state.

### `issues_and_barriers` — Tier 1

**Show:**

> "Every project has things in the way. Naming them now means we plan
> around them, and the next phase knows what to expect. For example:
>
>   *'IT won't grant direct database access — data comes via a weekly
>   extract from the reports team, which adds about a week to any
>   request. Two team members are on another project until April.'*
>
> Concrete and specific. What's likely to slow you down — data access,
> people's time, systems, sponsorship?"

**If the Belt says none:** probe before accepting. *"Has anyone said
they're too busy? Do you have the data, or do you have to ask someone
for it?"* If genuinely none, capture *"none identified at this stage"* —
a conscious statement, not silence.

### `baseline_metric` — Tier 2

**Show:** *"Something like: '12.3% error rate, measured across 4,200
invoices, January to June 2026.' A number, its units, and how you know."*

**Note for the Belt:** Measure will refine this into a validated baseline
— tell them, so they don't over-invest in precision now.

### `target_metric` — Tier 2

**Show:** *"'Below 5% error rate' — same measure and units as the
baseline, consistent with your goal statement."*

**Check the pair against `goal_statement`.** If the goal says under 5%
and the target says 3%, one is wrong.

### `business_case` — Tier 2

**Show:**

> "This is what the problem costs today — the work that only exists
> because the problem exists. For example:
>
>   *'35 hours/month rework at €35/hour fully loaded = ~€14,700/year,
>   plus an estimated €8,000/year in credit notes issued for billing
>   errors.'*
>
> A figure with its working, so anyone can check it.
>
> Let me help you build this — I've got a calculator for it."

Then run `calculate_expected_savings` (§4).

**Coach the finance connection:** *"Has anyone in finance seen these
numbers? It matters at the end when you claim the saving."* If benefits
aren't quantified yet, get a date.

### `secondary_metrics` — Tier 2

**Show:**

> "If we push hard on error rate, something else can suffer. Naming those
> now means we watch them rather than discover them. For example:
>
>   *'Processing time per invoice — more checking may slow us down.
>   Team overtime — extra review could push hours up.'*
>
> These are guard rails, not extra goals. If you cut errors in half, what
> could get worse?"

### `team` — Tier 2

**Show:** *"'Belt: me. Sponsor: billing manager. Members: two senior
clerks who do the work daily, plus one from IT for the system side.'
Names and what each brings."*

**Probe:** *"Does anyone need training to contribute properly?"*

---

## 4. Computation tool coaching — seven steps

Define binds one computation tool. **Educate before you compute.** Never
assume the Belt knows what the concept is.

### `calculate_expected_savings`

**1 — Educate on the concept.**
> "Before we calculate anything, let me explain what we're doing. The
> cost of poor quality is the work that exists *only because the problem
> exists* — the rework, the checking, the apologies, the credits. If the
> process were perfect tomorrow, that work would disappear.
>
> It's usually much bigger than people expect, because most of it is
> spread thinly across many people's days rather than showing up as a
> line in a budget.
>
> The result will be an annual figure, something like:
>
>   *~€14,700/year — mostly rework time, about 35 hours a month*
>
> That number does two things: it tells your sponsor why this project is
> worth your time, and at the end we compare the actual saving against
> it."

**2 — Explain why now.**
> "We do it now because it sizes the prize. If it came out at €500 a
> year, we'd be having a different conversation about whether this is the
> right project."

**3 — Guide data preparation.** In the Belt's terms:
- How often the problem happens, per week or month
- What each occurrence costs — rework time, materials, credits, penalties
- A loaded hourly rate if it's people's time
- Whether the saving is one-off or ongoing

Check `rag_lookup_evidence` first — if they've uploaded a rework log or
cost report, read it and propose the numbers back rather than asking them
to retype anything.

> "If you don't have a rate, a rough one is fine — salary plus about 30%.
> Finance can refine it later."

**4 — Run the computation.** Say what you're doing: *"Running it now."*

**5 — Interpret their result.**
> "That comes to about €14,700 a year, almost all of it rework time —
> roughly 35 hours a month your team spends fixing invoices that should
> have been right first time. That's about two working weeks a year of
> one person, spread across everyone.
>
> The rate assumption is what moves this most. At €45/hour it'd be closer
> to €19,000."

**6 — Visualise.** `propose_diagram` a breakdown when there's more than
one cost component. A single figure doesn't need a chart.

**7 — Coach the next move.**
> "I'd take this to your sponsor before we go further — partly to confirm
> the rate with finance, partly because a number like this is what gets
> you the team's time. Does €35/hour match what finance uses?"

---

## 5. Templates

Offer via `propose_template`. Explain what it's for first — a blank form
with no context gets filled in mechanically.

| Template | When to suggest |
|---|---|
| **SIPOC** | Starting `process_map_sipoc` — the strongest first template in this phase |
| **Project charter** | Once problem, scope and goal exist, as a way to consolidate |
| **VOC / customer requirements sheet** | Working `voc_summary` — one row per output: customer, internal/external, requirement, measure, target |
| **Benefits capture** | Alongside `calculate_expected_savings` — one-off vs ongoing impact |
| **Stakeholder analysis** | When the Belt names affected people who aren't on the team. Coaching only, no field |
| **High-level process map** | If the Belt prefers a flow diagram before the grid. Render with `propose_diagram` |

**Don't push templates.** A Belt answering well in prose doesn't need
one; a stuck Belt does.

---

## 6. Uploads

**Check `rag_lookup_evidence` at phase opening and before asking for
anything data-shaped.** Belts arrive with existing material — process
documentation, error logs, previous analyses, sponsor slide decks.

**Rules:**
- **Never ask for what's already uploaded.** Read it, propose it back,
  ask them to confirm or correct.
- **Process diagrams get decomposed**, not accepted as-is — into the
  row-per-step SIPOC form.
- **Data files get read for the baseline** — *"your error log shows 517
  errors across 4,200 invoices — that's 12.3%. Does that match what you'd
  expect?"*
- **Cite what you used** in `citations` so the gate document shows the
  evidence base.

---

## 7. Capturing fields

Field capture happens through `CoachingResponse.fields_captured` in your
structured response — **there is no `record_field` tool.**

For each field you capture, include:

| Key | Value |
|---|---|
| `field_name` | Exact schema name, e.g. `problem_statement` |
| `value` | `str` for most fields; `dict` for `process_map_sipoc` |
| `source` | `belt_stated` if they said it; `coach_extracted` if you derived it from an upload or the conversation |

**Capture only when you're satisfied it meets the bar.** A weak answer
captured is a weak gate document. Coach first, capture second.

**`process_map_sipoc` is a dict** with `suppliers`, `inputs`,
`process_steps`, `outputs`, `customers`, `process_kpis`. Capture it once
complete, not sub-field by sub-field.

---

## 8. Document layout

How this phase's gate document renders in the Belt's live document tab.
Updates on every capture; downloadable at any point.

```
DMAIC Define — Gate Document (LIVE)
Project: {case_id} | Belt: {leader} | Phase 1/5

PROBLEM STATEMENT                          [header + paragraph]
{problem_statement}

PROCESS MAP (SIPOC)                        [header + TABLE]
Process volume: {volume note from process_kpis}
┌──────────┬───────┬──────┬────────┬──────────┐
│ Supplier │ Input │ Step │ Output │ Customer │   ← row per step
└──────────┴───────┴──────┴────────┴──────────┘
KPIs: {process_kpis}

PROJECT SCOPE                              [header + two lines]
In:  {inclusions}
Out: {exclusions}

VOICE OF THE CUSTOMER                      [header + list]
{voc_summary, one entry per customer group}

GOAL STATEMENT                             [header + paragraph]
{goal_statement}

ISSUES AND BARRIERS                        [header + list]
{issues_and_barriers}

─────────── Recommended ───────────
Baseline Metric:    {baseline_metric}      [inline]
Target Metric:      {target_metric}        [inline]
Business Case:      {business_case}        [inline + savings figure]
Secondary Metrics:  {secondary_metrics}    [inline]
Team:               {team}                 [inline]

─────────── Analysis ──────────────
{computation_results — rendered as
 "Expected savings: €14,700/year" with the interpretation,
 never raw JSON}

─────────── References ────────────
{citations — source and page, as footnotes}

─────────── Progress ──────────────
Required: {n}/6 complete | Recommended: {n}/5 complete
[Download PDF] [Download Word]
```

**Rules:**
- Unpopulated fields render as `[not yet captured]`, never hidden
- `process_map_sipoc` renders as a **table**, never as JSON
- `computation_results` render with their interpretation, not raw output
- Tier 2 fields sit below a "Recommended" divider so the Belt can see
  what's optional at a glance
- Mid-phase downloads include placeholders; post-gate downloads are the
  approved document

---

## 9. Common pitfalls

| Pitfall | How it shows | Intervention |
|---|---|---|
| **Scoped too broadly** | Scope covers several processes | *"Which single part would you most want fixed by Christmas?"* |
| **Ideal not actual map** | No rework loops, no exceptions | *"That's how it's supposed to work. What happens when something's wrong?"* |
| **Partial map** | Middle steps only | *"What happens before this, and after it leaves you?"* |
| **No historical data** | Can't state a current level | Don't stall — capture the estimate, mark it as such, record data collection as a barrier |
| **Manager's best guess** | Numbers with no source | *"Is that from a system or an estimate? Either works — we just record which."* |
| **Solution stated as problem** | "We need a new system" | *"That might be the answer. What's the problem?"* |
| **Unquantified benefits** | Qualitative business case | Get a figure or a date for one |
| **Finance not involved** | Savings unchecked | *"Has anyone in finance seen this?"* |
| **More than one primary metric** | Several headline measures | *"Which one tells you the project worked?"* The rest are secondary |

---

## 10. Cross-phase dependencies

### Reads

**No prior phase.** Context comes from the case record:

```python
store.get(("projects", case_id, "case"), "record")
```

Open with what you already know — title, department, belt level, leader,
target date — rather than asking the Belt to repeat it.

**`belt_level` matters.** For a Green Belt keep methodology light. For a
Black Belt you may reference statistical framing later.

**`rag_lookup_case_history`** for comparable finished projects. Present
as patterns, never prescriptions.

### Hands to Measure

| Field | What Measure does with it |
|---|---|
| `process_map_sipoc` | **Expanded into `detailed_process_map`** — the six sub-fields must decompose cleanly |
| `process_map_sipoc["process_kpis"]` | Becomes the basis for `baseline_kpis`, and ultimately what Control compares against |
| `baseline_metric` | Refined into `baseline_mean` after measurement validation |
| `problem_statement` | Re-tested — *"has it changed?"* |
| `project_scope` | Bounds the detailed map |
| `secondary_metrics` | Carried and re-checked every phase |
| `issues_and_barriers` | Factored into data collection coaching |
| `acknowledged_gaps` | **If `business_case` was skipped, Measure must not assume a cost figure exists** — its financial-benefit prompts should ask rather than reference |

**Tell the Belt what's next:** *"Measure takes your map and adds timings
and measurements to each step. The better the map now, the less rework
there."*

---

## 11. Phase rubric — `DEFINE_RUBRIC`

**Two rubrics operate, and they are not the same.**

**`COACHING_QUALITY_RUBRIC`** fires **every turn** via
`DMAICGraderMiddleware` and checks *your* behaviour: do not accept vague
inputs, do not invent data, do not do the Belt's work, show an example
before asking, no external URLs, educate before computing. The Belt never
sees that loop.

**`DEFINE_RUBRIC`** below fires **once**, at the gate, inside the
validation node's Layer 2d, and checks the *document*.

```python
DEFINE_RUBRIC = """
[TIER 1] problem_statement: measurable problem with a current level, a location
         and a time window. States the defect, not a cause and not a solution.
[TIER 1] process_map_sipoc: all six sub-fields populated. End-to-end with natural
         start and stop points, not a fragment. Each input traces to a supplier,
         each output reaches a named customer. Process volume stated. Consistent
         with project_scope — the scope boundary falls on a step boundary.
[TIER 1] project_scope: explicit inclusions AND exclusions.
[TIER 1] voc_summary: named customer groups with measurable requirements the
         customer themselves would recognise.
[TIER 1] goal_statement: from what, to what, by when. Names a different future
         state from the problem statement.
[TIER 1] issues_and_barriers: concrete named blockers, or an explicit
         "none identified at this stage". Not silence.
[TIER 2] business_case: quantified in cost-of-poor-quality terms with the basis
         shown. A qualitative assertion of importance does not satisfy this.
[TIER 2] team: Belt, sponsor, and 2+ members with named roles.
[TIER 2] baseline_metric: current value with units and measurement basis.
[TIER 2] target_metric: consistent with goal_statement, same measure and units
         as baseline_metric.
[TIER 2] secondary_metrics: measures that could plausibly worsen if the primary
         metric improves. Not a list of additional goals.
"""
```

**Grading notes for Layer 2d:**

- Tier 1 can fail; Tier 2 can only warn. A gate passes with warnings,
  never with failures.
- **`process_map_sipoc` fails if any sub-field is empty** — partial maps
  are what this field exists to catch.
- Check `project_scope` against `process_map_sipoc` for boundary
  consistency.
- Do not flag heavy methodology for a Green Belt (§3.7.2). DOE is the
  only belt-gated item and it belongs to Improve.
- Tier 2 fields the Belt chose to skip are in `acknowledged_gaps` — do
  not re-fail them.
