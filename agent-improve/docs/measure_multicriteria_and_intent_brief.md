# Measure — Multi-Criteria Analysis + Claude Code Intent Brief

*2026-08-26, continuing the phase-review workstream. Part 1 is the intent
brief for the already-approved Measure-review + computation-tools draft
(`claude/MEASURE_REVIEW_AND_COMPUTATION_SPEC_DRAFT.md`). Part 2 is new
reasoning: multiple measurement criteria in Define/Measure, per your request.
Part 2 is NOT yet ratified — it's presented with a recommendation, for your
call before it goes to Claude Code.*

---

## Part 1 — Intent brief for Claude Code (push the approved draft)

*Per the project's workflow split, this is intent, not a diff. Claude Code
has repo access, the drift-check hook, and `/verify-current-version` — it
resolves the exact edit locations and writes the actual changes.*

**Target file:** `agent-improve/ARCHITECTURE.md`. **Source:** the project doc
`claude/MEASURE_REVIEW_AND_COMPUTATION_SPEC_DRAFT.md` (already written,
Parts A and B), ratified 2026-08-26.

**What to apply:**

1. **New §69, "Spec — computation tools."** Append after the existing §68
   (DORA register) — don't renumber anything. Content is Part B of the
   source doc verbatim: 20 tool entries, spec IDs S-F37–S-F56, common
   conventions preamble, the Control/Measure stability-tool boundary note.
2. **§60.6 (S-F24)** — update its "Rebuild test" line from *"not met — the
   inventory is complete, the interfaces are absent"* to *"met — see §69"*,
   and add a pointer from its Architecture reference to §69.
3. **§66, the SPEC-GAP register** — mark **G-25 closed**, citing §69. Update
   the register's closed/open counts (currently 9 closed / 35 open → 10/34).
4. **`agent-improve/skills/dmaic-measure-phase/SKILL.md`** — three wording
   changes, all in Part A of the source doc: (a) Section A's opening,
   replaced with the Define-recap version (pulls `problem_statement`,
   `baseline_metric`, `target_metric`+`target_date`, `process_map_sipoc`
   from `store.get(("projects", case_id, "artifacts"), "define")`); (b) one
   added line in the `measurement_system_validated` coaching block, giving
   the Belt an explicit decline option; (c) Section E rewritten to sweep
   only fields still absent from `artifacts`, not re-offer all three Tier 2
   fields unconditionally.
5. **Do NOT touch** the `baseline`→`baseline_metric` rename here — that's
   Define's item, already scheduled separately, and Measure's own files
   already use the new name.

**Verification:** rebuild test on §69 — could `knowledge/computation.py` be
written from it without reading old code, for at least 2–3 of the 20 tools
picked at random. SKILL.md changes: re-run the SKILL.md against its own
Section 2 field order to confirm the Section A/E contradiction is gone.

**Hold for Part 2 below** — do not start on it until you confirm which
option.

---

## Part 2 — Multiple measurement criteria (new architecture question)

### What you're pointing at

Right now, Define's problem/goal side of the "measurement thread" — the
three fields that carry one comparable value from Define through Measure to
Control — is single-valued:

```
Define    baseline_metric, target_metric        — ONE metric, discrete
Measure   baseline_mean, baseline_sigma          — characterises THAT one metric
Control   post-improvement result, compared to target_metric
```

That's a different thread from the one that's **already** multi-valued —
`process_map_sipoc["process_kpis"]` → `detailed_process_map["baseline_kpis"]`
→ Control's after-values, which the existing worked example already shows
carrying more than one KPI as prose ("Time-to-hire (days), offer acceptance
rate (%)"). **The gap you're naming is real, but it's narrower than "the
whole architecture assumes one metric"** — the KPI-thread side already
doesn't. The discrete `baseline_metric`/`target_metric` pair is the one place
singularity is actually baked in, because it's what Control uses for an
unambiguous machine-checkable target-vs-actual comparison (§39.1.2's stated
reason for keeping it discrete rather than folding it into prose).

### The holistic trace (Standing Reasoning Protocol, steps 1–2)

Tracing "Define can name several criteria" through every SIPOC link it
touches:

| Phase / field | Today | What changes |
|---|---|---|
| Define `baseline_metric` / `target_metric` | One value each | Must name and pair **N** criteria, each with a baseline and a target |
| Define `problem_statement` / `goal_statement` | Prose, assumed single-metric | Prose can already mention several; no field change, but the 5W2H "how much" question needs to invite "one or more" |
| Measure `baseline_mean` | One value | Must characterise **each** named criterion |
| Measure `baseline_sigma`, `stability_assessment` | One value/verdict each | Same — per criterion. **Stability especially**: one metric can be stable while another isn't, and capability can't be claimed for the unstable one even if the other's fine |
| Measure computation tools (`calculate_cpk`, `calculate_sigma_level`, etc., §69) | Called once per phase | **No signature change** — each is already single-metric-scoped (one mean/std_dev in, one result out). They get called **once per criterion**, landing as separate `computation_results` entries |
| `xy_matrix_summary` / `vital_few_xs` | Prioritises input X's | **Not affected.** This is the input side (what's driving the problem); your ask is about the output/Y side (what's being measured as the problem). Worth keeping these conceptually separate — it's an easy conflation |
| Analyse `causal_hypothesis` (cross-phase ref dict, §63.6) | References "the Measure baseline" | If Measure now characterises N criteria, the reference needs to say **which one** the root cause explains. Forward-note only — Analyse's own review hasn't started |
| Control post-improvement comparison | One target-vs-actual | Needs one comparison **per criterion**, not one overall verdict. Forward-note only — Control's own review hasn't started |

### Two ways to build it — a real fork, needs your call

**Option 1 — extend the string contract (recommended).** Keep
`baseline_metric`, `target_metric`, `baseline_mean`, `baseline_sigma`,
`stability_assessment` as plain `str` fields — no schema change, no new type.
Coach and grade them to a documented multi-criterion sub-structure inside the
string, exactly the pattern `process_kpis`/`baseline_kpis` already uses
successfully:

```
baseline_metric: "Error rate: 12.3% (n=4,200, Q1–Q2 2026).
                  Cycle time: 2.6 days (n=340, weekly sample)."
target_metric:   "Error rate: under 3% by 30 Sep 2026.
                  Cycle time: under 1.5 days by 30 Sep 2026."
```

Add one new grading rule to `DMAICGateValidator`/`PHASE_RUBRIC` (Layer 2b/2d,
§34–36): **the named criteria in `baseline_metric` must exactly match those
in `target_metric`**, same names, same units — a criterion appearing in one
but not the other is a gate failure, checkable by name-matching, not
judgment. Add one new convention to `computation_results` (§69's common
conventions): when a project tracks more than one criterion, each tool's
`inputs` sub-dict carries a `metric_name` key naming which criterion that
call is for — this is additive to the existing shape, doesn't touch any of
the 20 tool signatures, and means single-criterion projects (the common case)
are entirely unaffected.

*Why recommended:* it's exactly the escape valve §7 already built and
already validated in production use (the KPI thread) — "the alternative
designs were considered and rejected: a typed numeric loses context, and a
[structured] triple triples the schema" is §7's own stated reasoning, and it
applies here without modification. Zero schema/class changes; only
coaching-instruction and rubric changes, in Measure's SKILL.md, Define's
SKILL.md, and the two rubrics.

**Option 2 — a new structured field.** Replace `baseline_metric`/
`target_metric` with a list-of-dicts field (`measurement_criteria: list[dict]`
with keys `name`, `baseline_value`, `target_value`, `unit`), joining the
three existing structured dicts as a fourth exception to §7's typing law.
More machine-checkable (the grader iterates a list instead of parsing prose),
but it's a genuine schema change touching `DefineOutput`, `MeasureOutput`,
every downstream reader, §7's exception list, and §40's field-count tables —
and it reopens a law the document treats as hard-won and deliberately narrow.

**Recommendation: Option 1.** It resolves your requirement without touching
a single Pydantic schema, is consistent with how the architecture already
handles the one place multiplicity already exists, and keeps the "every
field is `str`" law intact rather than opening a fourth exception for a
problem the string contract already solves. Option 2 is worth it only if you
independently want machine-iterable criteria for something Option 1 can't
do (e.g., a UI that lets the Belt add/remove criteria as discrete rows rather
than editing prose) — that's a product decision, not an architecture
necessity.

### If you confirm Option 1 — the concrete deltas (Measure-scoped; this
review's job)

- `dmaic-measure-phase/SKILL.md` §2 field order: no field changes, but the
  per-field coaching blocks for `baseline_mean`, `baseline_sigma`,
  `stability_assessment`, and the `detailed_process_map` sub-field
  `baseline_kpis`, all get a rewritten "Ask" step that opens with *"How many
  things are we tracking here — just the one, or is there more than one
  criterion that together define this problem?"* and a worked example showing
  two criteria, not one.
- `MEASURE_RUBRIC` (§36/§39.1's counterpart for Measure): add the
  criteria-name-matching check described above, plus: **stability and
  capability verdicts must be given per criterion when more than one is
  named** — a blanket "stable" covering two metrics where only one was
  actually checked is the exact failure mode Tier-1 gating exists to catch.
- `§69`'s common-conventions preamble (already drafted, not yet pushed) gets
  the one addition above (`metric_name` in `inputs`) before Claude Code
  applies it — small enough to fold into Part 1's push rather than a second
  pass, if you confirm Option 1 now.
- Cross-phase reads (SKILL.md §10): no structural change — Analyse reading
  "Measure's baseline" still works, it just needs to say *which* baseline
  when Measure names more than one class. That instruction belongs in
  Analyse's own SKILL.md, at Analyse's review (forward-note, recorded here
  so it isn't lost).

### The gate-document parity ask — correcting one premise, then a proposal

You framed this as "Measure must match Define's gate-document richness."
**Checking that against what's actually written: it's the other way round.**
Define's SKILL.md content in `ARCHITECTURE.md` §39.1.7 ends at the closing
gate-readiness message — no document-layout section. Measure's SKILL.md
(§8, already drafted) is the one that already specifies a full rendered
document — a table per section, computation results shown "with
interpretation," charts inline via `propose_diagram`, a references block,
progress counts. **Measure is already ahead here, not behind.** Two things
are true at once: your instinct that this should be a *cross-phase*
requirement, not one skill author's choice, is right — but it needs to be
elevated from "one SKILL.md's convention" to an architecture rule (§50),
and then back-applied to Define (and forward-applied to Analyse/Improve/
Control at their reviews), rather than treated as something Measure needs to
catch up on.

**Proposed addition to §50 ("The live gate document"):** *"Every phase's
live gate document renders `computation_results` inline, grouped by
`metric_name` when more than one criterion is tracked, each entry shown with
its interpretation (not raw numbers — §43.1 step 5) and its chart via
`propose_diagram` where one applies. This is a document-layout requirement on
every phase's SKILL.md, not an optional enhancement of any one phase's."*
Worth noting precisely what does and doesn't feed this: the document's
narrative comes from the **captured field text** (the Belt's confirmed
values) plus **`computation_results`**, per §40's existing gate-metadata
sourcing rule — not from `CoachingResponse`'s turn-level `explanation`/
`example`/`prompt` fields (§50.1, WATCH 9), which are ephemeral coaching UI
and never assembled into the gate document. Keeping that boundary explicit
matters: it's what stops "why did we conclude this" turning into
re-parsing chat history at gate time.

This is a small, clean amendment (one new paragraph in §50) that generalizes
something already proven in Measure's draft, rather than a new mechanism —
worth folding into the same Claude Code push once you confirm it, alongside
Option 1 above.

### What this review is NOT deciding today

Analyse's `causal_hypothesis` reference-key shape, Control's per-criterion
target-vs-actual mechanics, and Define's own SKILL.md rewrite for
multi-criterion elicitation are all **forward-noted, not resolved** — each
belongs to that phase's own review, per the phase-review-before-backbone
sequencing you set in CONTINUITY §5. Recording them here now is what stops
them being rediscovered as surprises later.

---

## What I need from you to keep moving

1. **Part 1** — ready to push as-is; say so and I'll hand Claude Code the
   brief above (or you paste it directly).
2. **Part 2** — confirm Option 1 (recommended) or Option 2 for multi-criteria
   handling. Once confirmed, the Measure-scoped deltas above are ready to
   fold into the same push, and Measure's five-point bar closes for real —
   right now it's closed *for the single-criterion case only*.
3. The §50 gate-document-parity paragraph — confirm the wording above, or
   amend it, and it rides along in the same push.
