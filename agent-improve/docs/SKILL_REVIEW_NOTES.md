# SKILL.md Review Notes — for batch correction

## Cross-cutting (all five skills)

### 1. Missing: COACHING_QUALITY_RUBRIC reference
Each skill documents the PHASE_RUBRIC but none mentions the COACHING_QUALITY_RUBRIC
that fires every turn via DMAICGraderMiddleware (Finding 18). Add a note in each
skill's rubric section: "The middleware rubric (COACHING_QUALITY_RUBRIC) checks
coaching behaviour every turn — do not accept vague inputs, do not invent data,
do not do the Belt's work. The PHASE_RUBRIC below checks the gate document once."

### 2. Missing: what to do when the Belt uploads a file
Only Define mentions this (process map upload → decompose to SIPOC). Measure,
Analyse, Improve, and Control should also address uploads — Belts upload data
spreadsheets, test results, existing process documentation. The coach should
check uploads via rag_lookup_evidence and reference them during coaching rather
than asking the Belt to re-state information that's already in an uploaded file.

### 3. CoachingResponse not referenced
None of the skills mention how field capture works — via structured_response
from CoachingResponse (Finding 23). The coach doesn't call record_field (removed).
Each skill should note: "When capturing a field, include it in your
fields_captured list with the field_name, value, and source."

### 15. CRITICAL — Show-first coaching principle (all five skills, every field)
The coach must LEAD by example, not ask and correct. For every field, before
asking the Belt to provide their answer, the coach shows a concrete example of
what a completed answer looks like — visually where possible.

This is the fundamental coaching approach:
1. Show a concrete example (visual/structured if applicable)
2. Explain why it works ("this works because it has X, Y, Z")
3. Invite the Belt to build theirs ("can you describe yours in the same shape?")

The Belt sees the target, understands the structure, and mirrors it. One turn
to a complete answer instead of three turns of ask-and-correct.

Apply to every per-field coaching section:

**String fields:** show a boxed text example before asking.
```
Coach: "Here's what a strong problem statement looks like:

  'Invoice error rate in EMEA billing has run at 12.3% since 
   January 2026, against a target of under 5%, causing 35 hours 
   of rework per month.'

  It has: what's wrong, where, how bad, since when, and what it
  costs. Now — describe your situation in the same shape."
```

**SIPOC dict fields:** show a completed SIPOC as a row-per-step table before asking.
Each row traces one process step end to end — supplier → input → step → output → customer.
Include process volume as context — the Belt needs to know scale from Define.
```
Coach: "Here's an example SIPOC for a similar process. Each row 
  follows one step from who supplies it to who receives the result:

  Process volume: ~2,000 invoices per month (~100/working day)

  ┌───────────┬──────────────┬──────────────┬──────────────┬───────────┐
  │ Supplier  │ Input        │ Process Step │ Output       │ Customer  │
  ├───────────┼──────────────┼──────────────┼──────────────┼───────────┤
  │ Sales     │ Purchase     │ 1. Receive   │ Logged PO    │ Billing   │
  │ team      │ order        │    PO        │              │ clerk     │
  ├───────────┼──────────────┼──────────────┼──────────────┼───────────┤
  │ CRM       │ Customer     │ 2. Validate  │ Verified     │ Billing   │
  │ system    │ master data  │    details   │ record       │ clerk     │
  ├───────────┼──────────────┼──────────────┼──────────────┼───────────┤
  │ Billing   │ Verified     │ 3. Create    │ Draft        │ Reviewer  │
  │ clerk     │ record + PO  │    invoice   │ invoice      │           │
  ├───────────┼──────────────┼──────────────┼──────────────┼───────────┤
  │ Reviewer  │ Draft        │ 4. Review    │ Approved     │ Customer  │
  │           │ invoice      │    & approve │ invoice      │           │
  ├───────────┼──────────────┼──────────────┼──────────────┼───────────┤
  │ System    │ Approved     │ 5. Send      │ Delivered    │ Customer, │
  │           │ invoice      │    invoice   │ invoice      │ Finance   │
  └───────────┴──────────────┴──────────────┴──────────────┴───────────┘
  KPIs: Error rate at step 4, cycle time steps 1-5

  See how each row traces the flow? The output of one step becomes 
  the input to the next. Now let's build yours — start with: roughly 
  how many [items] flow through your process per week or per month? 
  Then we'll map step 1: what's the first thing that happens, and 
  who triggers it?"
```

**Detailed process map (Measure phase):** when the Belt reaches Measure, the SIPOC
expands into a detailed map with value stream mapping data per step. Show this
example to the Belt:
```
Coach: "Now we add the operational detail to each step. For every 
  step in your SIPOC, I need to know: how long does it take, who 
  does it, and is it adding value for the customer?

  Here's what a completed row looks like:

  ┌──────────────┬───────┬───────┬───────┬──────────┬───────────┬──────┐
  │ Step         │ Min   │ Avg   │ Max   │ People   │ Value/    │ KPI  │
  │              │ time  │ time  │ time  │ assigned │ Waste     │ today│
  ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
  │ 1. Receive   │ 2min  │ 5min  │ 15min │ 1 clerk  │ Value     │ 100% │
  │    PO        │       │       │       │          │           │      │
  ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
  │ (wait)       │ 1hr   │ 4hr   │ 2days │ —        │ Waste     │ —    │
  ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
  │ 2. Validate  │ 3min  │ 8min  │ 30min │ 1 clerk  │ Value     │ 95%  │
  │    details   │       │       │       │          │           │ FTQ  │
  ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
  │ 3. Create    │ 5min  │ 12min │ 45min │ 1 clerk  │ Value     │ 88%  │
  │    invoice   │       │       │       │          │           │ FTQ  │
  ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
  │ (rework)     │ 10min │ 20min │ 1hr   │ 1 clerk  │ Waste     │ 12%  │
  │              │       │       │       │          │           │ rate │
  ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
  │ 4. Review    │ 2min  │ 5min  │ 20min │ 1 senior │ Necessary │ —    │
  │    & approve │       │       │       │          │ waste     │      │
  ├──────────────┼───────┼───────┼───────┼──────────┼───────────┼──────┤
  │ 5. Send      │ 1min  │ 1min  │ 2min  │ auto     │ Value     │ 100% │
  │    invoice   │       │       │       │          │           │      │
  └──────────────┴───────┴───────┴───────┴──────────┴───────────┴──────┘

  Total touch time: ~31 min avg  |  Total elapsed: ~2.5 days avg
  That gap is the hidden waste — mostly waiting between steps.

  Notice three things:
  - Waiting time is listed as its own row — it's usually where 
    the time goes
  - Rework is listed as its own row — it's the hidden factory
  - 'Necessary waste' means it doesn't add customer value but 
    you can't remove it (like the review step)

  Let's build yours step by step. Take your first SIPOC step 
  and tell me: how long does it take at minimum, on average, 
  and at worst?"
```

**Computation tool results:** educate FIRST, show what the output means, THEN run.
The coach must never assume the Belt knows what a calculation is or why it matters.
```
Coach: "Before we look at the numbers, let me explain what 
  process capability means. It answers one question: can your 
  process, as it runs today, consistently meet what the 
  customer needs?

  Imagine the customer accepts anything between 0 and 5 days 
  processing time. Your process averages 3 days but sometimes 
  takes 7. Capability measures that gap — are you reliably 
  inside the limits, or are you spilling over?

  The result is a number called Cpk:
  - Above 1.33: your process comfortably meets the requirement
  - Between 1.0 and 1.33: it meets it, but with little margin
  - Below 1.0: it can't reliably meet the requirement as it runs

  Let me calculate yours from the data you provided. The result 
  will look something like:

    Cpk = 0.82 — the process can't reliably meet the 
    requirement. The spread is too wide or the centre is off.

  Ready? Let me run it."
```

**EVERY computation tool coaching sequence must follow this pattern:**
1. Explain the concept in plain language with a real-world analogy
2. Explain why the Belt needs it right now in their project
3. Show what the result will look like and what the numbers mean
4. Run the tool
5. Interpret their specific result
6. Visualise
7. Coach the next move

This is seven steps, not six — step 1 (educate) was missing from Finding 25.
Update Finding 25's six-step pattern to seven steps across all skills.

**Cross-phase reference dicts:** show how the link will look.
```
Coach: "Your hypothesis will connect back to the Measure baseline 
  like this:

  Hypothesis: 'Inadequate onboarding causes error spike in 
               first 60 days'
  References: Measure baseline_mean = 12.3%

  That link is what proves your root cause addresses the actual 
  measured problem, not a different one."
```

**Use `propose_diagram` for visual examples wherever the field has spatial
structure:** SIPOC, process maps, fishbone, control charts, scatter plots.
A picture of a completed example teaches faster than prose description.

**This principle replaces the current "Good looks like" paragraphs.** Those
describe what good looks like to the SKILL.md reader (Claude Code, the
developer). Note 15 describes what good looks like to the BELT — shown
inside the coaching conversation as a concrete example, not described in
documentation they never see.

## Define-specific

### 4. process_map_sipoc — add validation checklist
The coaching guidance is strong but could use a concrete validation checklist
the coach runs through before accepting the SIPOC:
- Does each supplier connect to at least one input?
- Does each input enter at least one process step?
- Does each output reach a named customer?
- Are there steps with no KPI? (flag, don't block)
- Does the scope boundary fall on a step boundary?

### 5. calculate_expected_savings — mention Define's acknowledged_gaps
If business_case is Tier 2 and the Belt proceeds without it, the savings
calculation may not have happened. Note this in the cross-phase handoff —
Measure should check whether Define acknowledged this gap.

## Measure-specific

### 6. stability_assessment — add what "unstable" coaching looks like
The skill says check stability before capability, and the Cpk tool refuses
without it. But what does the coach DO when the process is unstable?
Add: "If unstable, coach the Belt to identify the special causes. Common
ones: new staff, equipment changes, seasonal volume. Once identified,
the Belt can either remove them and re-measure, or exclude those data
points with documented rationale."

### 7. vital_few_xs — add the "too many" coaching
The pitfalls table mentions "too many vital few" but the per-field coaching
doesn't explicitly say how many is right. Add: "Three to six is typical.
More than six means the prioritisation wasn't selective enough — go back
to the X-Y matrix scores."

## Analyse-specific

### 8. Test selection dialogue needs the data type decision tree
The skill opens with "is it a number or a category?" but should explicitly
map the decision tree:
- Comparing two groups, continuous data → t_test
- Comparing three or more groups → anova
- Comparing proportions/categories → chi_square_test
- Checking relationship between two continuous variables → pearson_correlation
- Predicting one variable from another → linear_regression
This is the most common coaching moment in Analyse — getting it wrong
invalidates everything downstream.

### 9. ruled_out_causes — emphasise this is positive evidence
The skill should stress: "rejected with rationale" means the Belt ran
a test or collected data showing this X is NOT the cause. "I don't think
it's that" is not rejection. The audit trail should show what was tested
and what the result was.

## Improve-specific

### 10. Three-option experiment justification — add examples per option
The dialogue presents three options but doesn't show what a good answer
looks like for each:
- Option 1 (full DOE): "Conducted a 2³ factorial — three factors at two
  levels, 8 runs randomised. Factor A (training hours) significant,
  factors B and C not significant."
- Option 2 (simplified): "Tested the new onboarding programme on one team
  for 4 weeks, compared error rates before and after. Error rate dropped
  from 12.3% to 4.1%."
- Option 3 (no experiment): "Root cause analysis conclusively showed
  training gap. The solution (structured onboarding) directly addresses
  it. Piloting is sufficient validation."

### 11. pilot_result — add practical AND statistical significance check
The Improve rubric requires both. The coaching should explicitly ask:
"Is the improvement statistically significant (the numbers prove it's
real, not noise)? AND is it practically significant (big enough to
matter to the business)?" — same two-gate pattern from Analyse.

## Control-specific

### 12. Chart selection — needs the I-MR addition
Pending the imr_chart_limits commit. Once that lands, the chart selection
dialogue should be:
- Multiple measurements per period, continuous → X-bar R
- Individual measurements per period, continuous → I-MR
- Pass/fail counts → p-chart
- Defect counts per unit → c-chart

### 13. control_plan five sub-plans — add "develop vs implement" check
The eBook has ten steps: five develop and five implement. The skill coaches
each sub-plan but should explicitly ask for both stages: "Have you written
the training plan? Good. Has the training actually happened?" A written
but undelivered plan is the most common Control failure.

### 14. post_improvement_metric — coach the comparison explicitly
The skill captures the metric and the cross-phase reference, but should
coach the Belt through the comparison: "Your baseline was 12.3%. You're
now at 3.1%. That's a 74.8% reduction. Does that match what the pilot
predicted?" The comparison is the proof the project worked.

## Cross-cutting — Session Flow

### 16. CRITICAL — Coaching session flow (all five skills)

Every SKILL.md must define the Belt's experience from phase entry to gate passage.
The same A→F flow applies to all five phases — only the fields and examples change.

**Step A — Phase opening (first turn).** Coach shows:
- Complete field list for the phase, split by Tier 1 (required) and Tier 2 (recommended)
- Plain-language description of each field (not field_name, the human name)
- Progress: "0 of N required complete"
- What comes first and why
- Use `propose_diagram` to render the checklist visually

**Step B — Phase resumption (returning Belt).** Coach shows:
- Same checklist with ✓/□ status per field
- What was completed last time
- What's next and why
- Current progress count
- Reads from PhaseState.artifacts to know what's captured

**Step C — Per-field coaching (Note 15 show-first pattern).** For each field:
1. Show concrete example of the completed field
2. Explain why it matters
3. Invite the Belt to build theirs
4. Coach iteratively until good enough
5. Capture in fields_captured when satisfied

**Step D — Field capture feedback.** After every successful capture:
- Echo back what was captured (the Belt confirms it's right)
- Show updated checklist with the new ✓
- Updated progress count
- Name the next field and transition: "Next: [field]. Let me show you..."

**Step E — Tier 1 complete, Tier 2 offered.** When all required fields are done:
- List remaining Tier 2 fields with plain-language descriptions
- Belt chooses which to complete and which to skip
- Skipped fields recorded in acknowledged_gaps
- Coach doesn't pressure — offers, explains value, respects the Belt's choice

**Step F — Gate ready.** When Belt is ready:
- Coach announces gate check
- Four-layer validation fires
- Belt sees gate review panel via interrupt

**The planner drives the sequence — the SKILL.md defines what's available.**
The planner reads artifacts to know what's captured, checks the SKILL.md field
order, and produces a coaching_plan for the next empty field. The coach follows
the plan and presents the field to the Belt using the show-first pattern.

**Progress visibility is non-negotiable.** The Belt must ALWAYS know:
- How many fields are done
- How many remain
- Which one they're working on now
- What comes next

This information comes from PhaseState.artifacts (what's captured) and the
SKILL.md field order (what the sequence is). The coach renders it as a visual
checklist via propose_diagram on every field transition.

### 17. CRITICAL — Live gate document preview (architecture + all five skills)

The Belt must always see the gate document building in real time. This is not
just a progress checklist (Note 16) — it is the actual readable document that
will be reviewed at the gate, presented at stakeholder meetings, and
downloaded as a project deliverable.

**What the Belt sees alongside the coaching conversation:**

A live-updating structured document that shows every field — populated fields
with their content, empty fields as placeholders. Example for Define mid-session:

```
┌─────────────────────────────────────────────────────────────┐
│ DMAIC Define — Gate Document (LIVE)                         │
│ Project: IMPR-2026-E9D  |  Belt: Vassilis  |  Phase: 1/5   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ PROBLEM STATEMENT                                           │
│ Invoice error rate in EMEA billing has run at 12.3% since   │
│ January 2026, against a target of under 5%, causing 35      │
│ hours of rework per month.                                  │
│                                                             │
│ PROCESS MAP (SIPOC)                                         │
│ ┌──────────┬───────────┬──────────┬──────────┬──────────┐   │
│ │Supplier  │Input      │Step      │Output    │Customer  │   │
│ ├──────────┼───────────┼──────────┼──────────┼──────────┤   │
│ │Sales     │Purchase   │1.Receive │Logged PO │Billing   │   │
│ │team      │order      │  PO      │          │clerk     │   │
│ ├──────────┼───────────┼──────────┼──────────┼──────────┤   │
│ │CRM       │Customer   │2.Validate│Verified  │Billing   │   │
│ │system    │data       │  details │record    │clerk     │   │
│ ├──────────┼───────────┼──────────┼──────────┼──────────┤   │
│ │Billing   │Verified   │3.Create  │Draft     │Reviewer  │   │
│ │clerk     │record     │  invoice │invoice   │          │   │
│ ├──────────┼───────────┼──────────┼──────────┼──────────┤   │
│ │Reviewer  │Draft      │4.Review  │Approved  │Customer  │   │
│ │          │invoice    │  approve │invoice   │          │   │
│ ├──────────┼───────────┼──────────┼──────────┼──────────┤   │
│ │System    │Approved   │5.Send    │Delivered │Customer, │   │
│ │          │invoice    │  invoice │invoice   │Finance   │   │
│ └──────────┴───────────┴──────────┴──────────┴──────────┘   │
│ KPIs: Error rate at step 4, cycle time steps 1-5            │
│                                                             │
│ PROJECT SCOPE                                               │
│ In: Invoice creation through dispatch, EMEA only            │
│ Out: Credit notes, APAC, upstream CRM data entry            │
│                                                             │
│ VOICE OF CUSTOMER                                           │
│ [not yet captured]                                          │
│                                                             │
│ GOAL STATEMENT                                              │
│ [not yet captured]                                          │
│                                                             │
│ ISSUES AND BARRIERS                                         │
│ [not yet captured]                                          │
│                                                             │
│ ─────────── Recommended ───────────                         │
│ Baseline Metric: 12.3% error rate, 4200 invoices Jan-Jun    │
│ Target Metric: [not yet captured]                           │
│ Business Case: [not yet captured]                           │
│ Secondary Metrics: [not yet captured]                       │
│ Team: [not yet captured]                                    │
│                                                             │
│ ──────────── Progress ─────────────                         │
│ Required: 3/6 complete  |  Recommended: 1/5 complete        │
│                                                             │
│ [Download as PDF]  [Download as Word]                       │
└─────────────────────────────────────────────────────────────┘
```

**Key requirements:**

1. **Always visible** — a separate tab or panel alongside the chat, not buried in a menu.
   The Belt glances at it to see what's done and what's coming. Already exists in the
   current Agent Improve UI as the last tab.

2. **Updates in real time** — when the coach captures a field via CoachingResponse
   fields_captured, the document updates immediately. The Belt sees the new content
   appear without refreshing.

3. **Readable as a document** — not a list of field names and values. Structured with
   headers, formatted content, visual elements (SIPOC as a table, not JSON). This is
   what gets shown to the sponsor.

4. **Downloadable** — PDF and/or Word format. The Belt downloads at any point, not
   just after the gate passes. Mid-phase downloads show [not yet captured] placeholders.
   Post-gate downloads show the approved gate document.

5. **Phase-specific formatting** — Define shows SIPOC as a table. Measure shows the
   detailed process map with timings. Analyse shows the hypothesis test results.
   Control shows the five sub-plans in sections. Each phase's document layout is
   defined in its SKILL.md.

6. **Computation results rendered** — when artifacts["computation_results"] contains
   tool outputs, they render inline: "Sigma level: 2.67" with the interpretation,
   not raw JSON.

7. **Citations shown** — sources the coach referenced appear as footnotes or a
   references section. The Belt and their sponsor can verify the methodology.

**Architecture impact:**

This connects to §77 (Frontend Feedback Requirements) Pattern 3 (show extracted
fields before gate review) and Pattern 4 (completeness progress bar). The live
gate document IS the implementation of both patterns — it shows fields and progress
simultaneously, in a document format the Belt can use outside the system.

The data source is PhaseState.artifacts — already checkpointed and updated on every
field capture. The frontend reads it and renders the document template for the
current phase. No new backend work — the data is already there.

**SKILL.md impact:** Each skill needs a "Document Layout" section defining how that
phase's gate document renders:
- Which fields get headers
- Which fields render as tables (SIPOC, detailed process map, control plan sub-plans)
- Which fields render inline (baseline_metric, goal_statement)
- Where computation results and citations appear
- The download format structure

## Summary

17 review notes. Notes 15, 16, and 17 together define the complete Belt experience:
- Note 15: the coach shows before asking (teaching method)
- Note 16: structured A→F session flow with progress (coaching sequence)
- Note 17: live gate document always visible, downloadable (deliverable visibility)

All can be applied as one Claude Code commit to the five SKILL.md files.
Note 17 also produces a requirement for §77 (frontend) and a "Document Layout"
section in each SKILL.md.

**Finding 25 update:** The computation tool coaching pattern changes from six
steps to seven. Step 1 becomes: educate the Belt on what the concept IS and
why it matters (plain language, real-world analogy). The old step 1 ("explain
why") assumed the Belt already understood the concept. Update in
STATE_DESIGN_RESOLUTION.md and all three governance documents.
