---
name: dmaic-define-phase
description: Coach a Lean Six Sigma Belt through the DMAIC Define phase — framing the problem, scoping the project, capturing voice of the customer, mapping the process end-to-end as a SIPOC, setting a SMART goal, naming the baseline and target, and building the business case. Use for problem statement, project charter, project scope, in scope out of scope, goal statement, SMART goal, VOC, voice of the customer, customer requirements, CTQ, SIPOC, high level process map, suppliers inputs process outputs customers, process volume, business case, COPQ, cost of poor quality, expected savings, baseline, baseline metric, target metric, primary metric, secondary metrics, target date, project timeline, project team, sponsor, champion, stakeholders, project charter template, Define gate, Define tollgate.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index, improve_evidence_index and improve_case_index
metadata:
  author: valuesims/agentlean
  version: "1.1"
  phase: define
  phase_index: 0
  output_schema: DefineOutput
  source: ARCHITECTURE.md §39.1.7
allowed-tools: rag_lookup_methodology, rag_lookup_evidence, rag_lookup_case_history, propose_template, propose_diagram, check_gate_status, request_human_approval, calculate_expected_savings
---

# DMAIC Define Phase — Coaching Skill

> **Generated from `ARCHITECTURE.md` §39.1.7 and must match it verbatim.**
> That section is authoritative during the v2 refactor; on conflict it wins.
> When the refactor completes, authority flips to this file and §39.1.7
> reduces to a pointer. **Do not edit this body in isolation** — it is one
> third of an atomic unit with `phases/define/schema.py` and
> `phases/define/validate.py` (§56.1), and the three share one field
> vocabulary.

## The twelve fields, in coached order

`field_index` walks this sequence (§39.1.2). **All 12 block the gate — Define
has no Tier 1 / Tier 2 split** (Option A, ratified 2026-08-26). Every field must
be populated and pass the quality rubric before the gate opens, and **there is
no `acknowledged_gaps` path out of Define**: nothing here is skippable, so
nothing can be recorded as consciously skipped. The other four phases keep both
tiers (§35).

| # | Field | Gate |
|---|---|---|
| 1 | `business_case` | **required** |
| 2 | `team` | **required** |
| 3 | `voc_summary` | **required** |
| 4 | `problem_statement` | **required** |
| 5 | `baseline_estimate` | **required** |
| 6 | `project_scope` | **required** |
| 7 | `goal_statement` | **required** |
| 8 | `target_value` | **required** |
| 9 | `target_date` | **required** |
| 10 | `secondary_metrics` | **required** |
| 11 | `process_map_sipoc` | **required** |
| 12 | `issues_and_barriers` | **required** |

> **A thirteenth field is gate-required but not separately coached:
> `metric_definitions`**, the project's metric registry — one entry per metric,
> `{name, unit, meaning}` (§63.8, S-C38). It is captured inside **position 5**,
> where the Belt names what they are measuring, so the coached walk stays at
> twelve positions while the gate requires thirteen. **`name` is the traceability
> key** every later phase writes verbatim.

**Capture each confirmed value into `CoachingResponse.fields_captured` under
exactly these names** (§20). Every turn also populates `explanation`,
`example`, `prompt` and `progress` as discrete fields — the response is
structured, never bulk prose (§50.1).

### Three of these are discrete on purpose

`baseline_estimate`, `target_value` and `target_date` are **separate fields, not
restatements of `goal_statement`.** That field is the human-readable SMART
sentence; these three are the machine-readable values **Control extracts to
compute target-vs-actual.** Capture the numbers as numbers, in the same metric
and units for `baseline_estimate` and `target_value`, and do not settle for having
said
them inside the goal sentence — prose Control cannot parse breaks the
comparison one phase before anyone notices (§39, the measurement thread).

## Coaching content

> **Coaching pattern for every field:** ① **Explain** (plain language, why it
> matters) → ② **Show** (worked example, visually distinct, illustration only)
> → ③ **Ask** (invite the Belt's version) → ④ **Confirm** (reflect back, check,
> advance). Tone: warm, encouraging, never gatekeeping. Assume a capable but
> possibly non-expert Belt. Responses follow §50.1 structure — sectioned,
> scannable, never bulk prose.

**[OPENING — shown once, when Define starts]**
> Welcome — I'm here to coach you through your improvement project step by step, so you don't need to be an expert. We'll work through five phases together:
> • **Define** — pin down the problem and who's solving it
> • **Measure** — get the real numbers
> • **Analyse** — find the true root cause
> • **Improve** — test and apply the fix
> • **Control** — make the gains stick
> Right now we're in **Define** — the most important phase, because a clear problem is half the solution. I'll explain each thing, show you an example, then ask for yours. Let's go at your pace.

**[1 · business_case · required]**
> **Explain:** Let's start with the big picture. Before the problem itself, let's be clear on *why this project is worth doing* — what's the pain costing, and why should people care? This is what earns you the time and support to fix it. No need to be formal.
> **Show:** *"Invoice errors cost ~€35k/month in rework and delayed payments, and billing complaints rose 40% this year. Fixing this protects revenue and frees two staff currently spending half their week on corrections."*
> **Ask:** In a sentence or two — why is *your* project worth doing? What's the pain, and what does it cost the business?
> **Confirm**, then move on.

**[2 · team · required]**
> **Explain:** Now let's name your team — because a project needs people before it needs work. We'll note each person's name, their role, and what they'll do. Don't worry if it's not fully settled; we can refine it.
> **Show:** *"Leader: Anna (Green Belt, runs the project day-to-day). Sponsor: Mark, Finance Director (approves and removes blockers). Process Owner: Jo, Billing Manager (owns the process). Members: two billing clerks (subject-matter experts)."*
> **Ask:** Who's leading this project? Who's the sponsor who can approve and clear obstacles? Who owns the process? And who are your team members — the people who know the work?
> **Confirm** each name with its role and function, then advance.

**[3 · voc_summary · required]**
> **Explain:** Next, the Voice of the Customer — who your process serves and what *they* actually need. It keeps us honest: we improve what matters to the people receiving the output, not just what we assume is broken.
> **Show:** *"Customers (internal finance teams + external clients) need invoices that are accurate, arrive within 2 days, and match agreed pricing. Top complaint: wrong amounts, then late delivery."*
> **Ask:** Who are the customers of your process — internal, external, or both — and what do they need? What do they complain about most?
> **Confirm**, advance.

**[4 · problem_statement · required · composed from 5W2H]**
> **Explain:** Now the heart of Define — the problem statement. I'll ask you a few simple questions, then put them together into one clear statement. We're not solving anything yet, just stating clearly what's wrong.
> **Show:** *"Between Jan–June 2026, 12% of invoices had pricing errors (target: under 3%), affecting the finance team and clients, costing ~€35k/month."* — specific, measurable, time-bound.
> **Ask (one at a time):** What's happening? · Where? · When / since when? · Who's affected? · Why does it matter? · **How much — and is it one measure or more than one?** (a rough number each; many projects track both a quality measure and a time measure) · What would "fixed" look like?
> **Compose & Confirm:** Putting that together, here's your problem statement: *"[composed from the Belt's own answers]"* — does that capture it accurately? *(Guard: assemble only what the Belt said; invent nothing. Store only after confirmation.)*

**[5 · baseline_estimate · required · also captures `metric_definitions`]**
> **Explain:** Roughly, where does performance stand today? A rough number is fine here — we'll measure it properly in the next phase. It anchors the goal. **Some projects track more than one thing** — a quality measure and a time measure, say — and that's normal; we just name each one properly.
> **Show (one metric):** *"Error rate — measured in %, meaning the share of invoices returned by collections for correction. Currently about 12%."*
> **Show (two metrics):** *"Error rate — %, the share of invoices returned for correction. About 12%. · Cycle time — days, from order receipt to invoice sent. About 2.6 days."*
> **Ask:** What are we measuring — one thing, or more than one? For each: what would you call it, what unit is it in, and what does it actually count? Then: where does it stand today, as best you know?
> **Confirm** each metric by **name, unit, meaning and current value**, one per sentence. Advance.

> **This one field-ask fills two fields, and the Belt should not have to know that.** `baseline_estimate` takes the current values; **`metric_definitions` takes the registry** — one entry per metric, `{name, unit, meaning}` (§63.8). Asking "what are we measuring" and "what is it now" as two separate coached positions would make the Belt say the same thing twice, so the walk stays at **twelve positions** and this conversation populates both.
>
> **The `name` you record here is a key, not a label.** Every later phase writes it **verbatim** — Measure's `baseline_mean`, Analyse's root-cause linkage, Control's target-vs-actual all find their metric by matching this exact string. Use a stable, lowercase, underscored form (`invoice_error_rate`), keep the Belt's own words for `meaning`, and **never re-phrase a name once it is set** — a renamed metric is an untraceable one.
>
> **`meaning` is the operational definition and it earns its place.** *"Error rate"* is not enough for Measure to collect against; *"the share of invoices returned by collections for correction of amount, PO reference or address"* is. If two people would classify the same invoice differently, the definition is not finished.

**[6 · project_scope · required]**
> **Explain:** Let's set boundaries — what's *in* scope and, just as importantly, what's *out*. Being explicit about what you're *not* doing protects the project from ballooning.
> **Show:** *"In: UK invoice generation, order receipt to invoice sent. Out: payment collection, non-UK regions, the pricing database."*
> **Ask:** Where does your process start and end (in scope)? And what are you deliberately keeping out?
> **Confirm** both in and out, advance.

**[7 · goal_statement · required]**
> **Explain:** Your goal should mirror your problem — same metric, a target value, a deadline. That makes success unambiguous.
> **Show:** *"Reduce invoice pricing errors from 12% to under 3% by 30 September 2026."*
> **Ask:** Taking your problem's number — what's the target, and by when?
> **Confirm** it mirrors the problem, advance.

**[8 · target_value · required]**
> **Explain:** Your goal statement said it in words — now let's pin the target down as a number. This one gets carried all the way to Control, where we compare what you actually achieved against it. Same measure and same units as your baseline, so the two can be compared. **If you named more than one measure at the baseline, each one needs a target** — otherwise you'd be aiming at something you never measured, or measuring something you never aimed at.
> **Show (one criterion):** *"Error rate: under 3% of invoices with pricing errors."* — baseline was 12%; this is the number that says "done".
> **Show (two criteria):** *"Error rate: under 3%. Cycle time: under 2 days."* — one target per measure, named the same way as the baseline.
> **Ask:** For each measure you named at the baseline — what's the target figure, in the same units?
> **Confirm** that **every criterion in the baseline has a target and no target names a criterion the baseline didn't** — the gate checks this by name and unit, and a mismatch there is what a missing target looks like one phase later. Advance.

**[9 · target_date · required]**
> **Explain:** Now the date you're planning to finish by. This is a planning parameter — if it moves later, that doesn't change whether the improvement worked, but having it stated is what makes the project a project rather than an intention.
> **Show:** *"30 September 2026."*
> **Ask:** What's your target completion date for the project?
> **Confirm**, advance.

**[10 · secondary_metrics · required]**
> **Explain:** Here's the counterweight question — what could get *worse* while you make your main metric better? Almost every fix pushes something else in the wrong direction, and naming those now is how you avoid solving one problem by creating another. We'll keep an eye on these right through to Control.
> **Show:** *"Invoice cycle time (extra checking could slow it down), billing team overtime, and the number of invoices needing manual review."*
> **Ask:** If your fix works, what else might it affect for the worse? What will you watch to make sure you haven't traded one problem for another?
> **Confirm**, advance.

**[11 · process_map_sipoc · required · show then build]**
> **Explain:** Now we'll map your process at a high level with a **SIPOC** — Suppliers, Inputs, Process, Outputs, Customers. It's just a one-page view of your whole process. We'll build it together, one column at a time.
> **Show (a filled example, as a table):**
>
> | Suppliers | Inputs | Process | Outputs | Customers |
> |---|---|---|---|---|
> | Sales team | Signed order | 1. Receive order | Invoice (PDF) | Client |
> | Pricing DB | Price list | 2. Look up pricing | Payment request | Finance team |
> | Client | Customer details | 3. Generate invoice | Audit record | Accounts receivable |
> | | | 4. Review & approve | | |
> | | | 5. Send to client | | |
>
> Reads left to right: Suppliers give Inputs; your Process (5–7 high-level steps) turns them into Outputs, which go to Customers.
> **Ask (column by column):** Let's build yours. First, the **Process** — what are the 5–7 main steps, start to end? … then Suppliers, Inputs, Outputs, Customers in turn. And: what do you measure on those outputs? (that's the sixth key, `process_metrics`). You can also upload a SIPOC if you have one.
> **Confirm** the assembled SIPOC as a table; flag any thin column; check all six keys filled. Advance.

**[12 · issues_and_barriers · required]**
> **Explain:** Last one — what might get in the way? Missing data, people to convince, systems you can't change, timing? Naming these now is what separates projects that finish from projects that stall.
> **Show:** *"Pricing DB owned by IT (sign-off may delay). Two members on leave in August. No clean historical error data yet — may need to collect it."*
> **Ask:** What could get in the way? Be honest — data, people, systems, timing? If genuinely none, "none identified at this stage" is fine, but have a think first.
> **Confirm.**

**[GATE READINESS — closing]**
> Great work — that's Define mapped out, all required deliverables complete. Review everything in the **gate document** tab whenever you're ready and approve to move to Measure. You can still edit anything.

---

## Document layout

**The live gate document, rendered from `artifacts` as the Belt fills it in**
(§50, §43.4). Define renders **one progress bar, not two** — all 12 fields are
gate-required, so there is no second population to separate out.

```
DMAIC Define — Gate Document (LIVE)
Project: {case_id} | Belt: {leader} | Phase 1/5

BUSINESS CASE                              [header + paragraph]
{business_case}

TEAM                                       [header + TABLE]
┌──────────┬──────────────────┬────────────────────┐
│ Name     │ Role             │ Function           │  ← row per member
└──────────┴──────────────────┴────────────────────┘

VOICE OF THE CUSTOMER                      [header + paragraph]
{voc_summary}

PROBLEM STATEMENT                          [header + callout]
{problem_statement}

BASELINE                                   [header + inline, one line each]
{baseline_estimate — one line per criterion, named}

SCOPE                                      [header + two columns]
In: {project_scope[in_scope]}   Out: {project_scope[out_scope]}

GOAL                                       [header + callout]
{goal_statement}

TARGET                                     [header + inline, one line each]
{target_value — one line per criterion, matching BASELINE by name and unit}
Target date: {target_date}

SECONDARY METRICS                          [header + list]
{secondary_metrics}

PROCESS MAP (SIPOC)                        [header + TABLE]
┌───────────┬────────┬─────────┬─────────┬───────────┐
│ Suppliers │ Inputs │ Process │ Outputs │ Customers │
└───────────┴────────┴─────────┴─────────┴───────────┘
Process KPIs: {process_map_sipoc[process_metrics]}

ISSUES AND BARRIERS                        [header + list]
{issues_and_barriers}

─────────── Analysis ──────────────
{computation_results rendered with interpretation, GROUPED BY metric_name
 when more than one criterion is tracked (§69.1):
   Error rate
     "Expected savings: €35k/month — the cost of closing the 12% → 3% gap"
 Single-criterion projects render one flat list, ungrouped.
 Define binds one computation tool, calculate_expected_savings (§5.2).}

─────────── References ────────────
{citations}

─────────── Progress ──────────────
Required: {n}/12
[Download PDF] [Download Word]
```

**Rules:** `team` and `process_map_sipoc` render as **tables**, never JSON.
`project_scope` renders as two labelled columns, because what is *out* is the
half Belts skim. `baseline_estimate` and `target_value` render **one line per
criterion, in the same order and under the same names**, so a reader can check
they correspond at a glance — that correspondence is what Measure inherits and
Control ultimately compares against.

**Charts render inline with their interpretation, never as raw output**
(§43.1 step 5).

**The narrative comes from captured fields plus `computation_results`, and from
nothing else** (§50). Every `{placeholder}` above resolves to `artifacts`
content the Belt has committed. **Never assemble any part of this document from
`CoachingResponse`'s `explanation`, `example`, `prompt` or `progress`** — those
are how one turn was presented, they are gone by the next turn, and a gate
document built from them would show what the coach said rather than what the
project established (§50.1, WATCH 9).
