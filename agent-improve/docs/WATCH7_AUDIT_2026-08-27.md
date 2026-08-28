<!--
Document: agent-improve/docs/WATCH7_AUDIT_2026-08-27.md
Created: 2026-08-27
Purpose: Records why procedure step "4.1 / WATCH 7 — migrate orchestrate.py's
         Define writer to the v2 §39.1 names" was STOPPED rather than executed,
         with the evidence, and states the three routes forward. A founder
         ruling is owed on the route. NOT binding — binding detail lives in
         ARCHITECTURE.md / CLAUDE.md / CONTINUITY.md / REFACTORING_PROCEDURE.md.
-->

# WATCH 7 — audit, and why the step was stopped
# 2026-08-27 · after commit `7dd473f` (Part A)

The handoff `CLAUDE_CODE_HANDOFF_wrap_and_orchestrate.md` scoped Part B as:
*"migrate `orchestrate.py`'s Define capture/write to the ratified v2 Define
schema"*, plus the Define cross-phase briefs in analyse / improve / control, as
one commit — **and instructed: if Part B raises anything the paper spec didn't
anticipate, stop and report rather than patch past it.**

It does. **Five things, each independently sufficient to stop the step.** No
code was changed.

---

## 0. The verification the handoff asked for — run first, and it fails loudly

The handoff's own verify method was a set-comparison of the written keys
against `DefineOutput.model_fields`. Run before any change, so it is a check
that demonstrably *can* fail (§5's standing lesson) — it does:

```
WRITTEN by the v1 path   : 26      # EXTRACTION_DEFINE's JSON keys + "sipoc"
DECLARED by DefineOutput : 18
READ by validate.py      : 13      # DEFINE_REQUIRED_FOR_GATE_FIELDS
```

| Set | Count | Members |
|---|---|---|
| **Intersection** — names that already agree | **2** | `goal_statement`, `target_date` |
| **Written but not declared** — dead writes | **24** | `belt_level`, `business_case_rationale`, `current_cost`, `estimated_completion_date`, `expected_saving`, `hard_benefits`, `how_goal`, `how_much_baseline`, `primary_metric`, `primary_metric_unit`, `process_owner`, `project_milestones`, `scope_in`, `scope_out`, `secondary_metric`, `sipoc`, `soft_benefits`, `sponsor`, `team_members`, `what`, `when`, `where`, `who_affected`, `why_it_matters` |
| **Declared but never written** — the gate cannot see them | **16** | `acknowledged_gaps`, `baseline_estimate`, `business_case`, `citations`, `computation_results`, `issues_and_barriers`, `metric_definitions`, `phase_metrics`, `problem_statement`, `process_map_sipoc`, `project_scope`, `secondary_metrics`, `target_value`, `team`, `uploads`, `voc_summary` |
| **Gate verdict** — required fields the v1 path can never supply | **11 of 13** | `baseline_estimate`, `business_case`, `issues_and_barriers`, `metric_definitions`, `problem_statement`, `process_map_sipoc`, `project_scope`, `secondary_metrics`, `target_value`, `team`, `voc_summary` |

The intersection of **2** matches `validate.py`'s own docstring — *"of the 12
required names, exactly two match v1"* — so WATCH 7's diagnosis was correct.
**What was wrong was its estimated size, not its content.**

`DefineOutput` is **18** fields, but `phases/define/schema.py`'s class docstring
still says *"Gate document for the Define phase — 16 fields."* — stale since the
registry landed (`metric_definitions` + `phase_metrics`, v1.15). A one-line code
fix, deliberately not made here: this audit changed no code.

---

## 1. The writer is not `orchestrate.py`

The step assumes the v1 field names are authored in
`phases/define/orchestrate.py`. They are not. They are authored in an **LLM
extraction prompt**:

- [`core/prompts.py:724`](../backend/core/prompts.py#L724) — `EXTRACTION_DEFINE`
  declares a 26-key JSON object (`what`, `where`, `when`, `who_affected`,
  `why_it_matters`, `how_much_baseline`, `how_goal`, `scope_in`, `scope_out`,
  `business_case_rationale`, …) and 15 per-field extraction rules keyed by those
  names.
- [`define/orchestrate.py:53-55`](../backend/phases/define/orchestrate.py#L53) —
  merges **whatever keys come back, unfiltered**:
  `for key, value in extracted.items(): … define_inputs[key] = value`.
  Define is the one phase with no `VALID_*_KEYS` filter.

So `orchestrate.py` is a **pass-through**, not the writer. Migrating "the
writer" means rewriting `EXTRACTION_DEFINE` — a file the paper spec for this
step never names, and one Appendix B marks **Rewrite** at a later stage.

---

## 2. Four readers stand on the v1 names, beyond the three cross-phase briefs

The step names three readers (the Define briefs in analyse / improve /
control). Raw `grep -rn` finds four more. Migrating the writer breaks all of
them the moment it lands.

| Reader | Sites | What breaks |
|---|---|---|
| [`ui/index.html`](../ui/index.html) | **78 lines** | `DEFINE_GATE_FIELDS` (22 field rows, L657-681), the gate checklist (L3118-3132), five work-product key lists (L1177-1182, L4248-4332, L4889-4918, L5698-5788), the readiness chips (L6020-6043), the 5W2H mindmap (L6374-6387), the charter panel (L6965). **Renders blank panels with no error** — step 3.4 names this exact failure |
| [`measure/orchestrate.py:105-116`](../backend/phases/measure/orchestrate.py#L105) · [`measure/validate.py:46-54`](../backend/phases/measure/validate.py#L46) | 6 | Seeds `primary_metric_confirmed` / `secondary_metric_confirmed` from Define's `primary_metric` / `primary_metric_unit` / `secondary_metric`. **Silently stops seeding** — the Measure gate then blocks on values the Belt already gave in Define |
| [`gateway/routes.py:433`](../backend/gateway/routes.py#L433) | 1 | `"what": define_structured.get("what", "")` into the upload context |
| [`upload/agent.py:89`](../backend/upload/agent.py#L89) | 1 | `case_meta.get("what", …)` — consumes routes.py:433 |

Backend readers, by exact accessor, 25 sites:

```
gateway/routes.py:433                    define_structured.get("what", "")
phases/analyse/orchestrate.py:329-331    define.get('what'|'primary_metric'|'how_goal')
phases/control/orchestrate.py:320-322    define.get('what'|'primary_metric'|'how_goal')
phases/improve/orchestrate.py:318-320    define.get('what'|'primary_metric'|'how_goal')
phases/measure/orchestrate.py:105,106,116  define_structured.get('primary_metric'|'primary_metric_unit'|'secondary_metric')
phases/measure/validate.py:46,47,54        define_inputs.get('primary_metric'|'primary_metric_unit'|'secondary_metric')
phases/define/orchestrate.py:61,133,303-306,477,541-543
```

plus four hardcoded v1 key **lists** inside `define/orchestrate.py` —
`_problem_statement_complete` (L386-392), `_detect_section_completion`
(L411-433), `_build_state_summary` (L450-468), `_build_5w2h_visualisation`
(L528-534).

---

## 3. Three of the moves are not renames

A rename is a substitution. These are shape changes, and each needs a design
decision that is not in the paper spec:

**(a) `primary_metric` + `primary_metric_unit` → `metric_definitions` —
scalar to registry.** v2 has no scalar metric field. The registry is
`list[dict]` of `{name, unit, meaning}` and `meaning` has **no v1 source at
all**. Measure's seeding cannot be renamed; it must be rewritten as a registry
lookup, and something must decide which entry is primary.

**(b) The 5W2H fields have NO v2 home.** §39.1.3 and
[`schema.py:145-151`](../backend/phases/define/schema.py#L145): *"The 5W2H are
coaching prompts, never stored fields."* `what` / `where` / `when` /
`who_affected` / `why_it_matters` / `how_much_baseline` / `how_goal` are
composed into one `problem_statement` and **discarded**. So there is nothing to
rename them to, and four consumers lose their data source outright: the 5W2H
mindmap (backend `_build_5w2h_visualisation` + UI L6374-6387),
`_problem_statement_complete`, `_detect_section_completion`'s problem section,
and `_build_state_summary`'s work product 1. Whether the mindmap survives the
migration — and if so, on what — is a **product decision**, not a mechanical
one. Note `_generate_sipoc_draft` also *gates* on `["what","where",
"who_affected"]` (L272), so SIPOC generation stops firing entirely.

**(c) `sipoc` (5 keys) → `process_map_sipoc` (6).** `SIPOC_KEYS` requires
`process_metrics` and `validate.py:_missing_structured` fails the gate on any
absent key. But `SIPOC_DRAFT_PROMPT` states *"A SIPOC has exactly five keys"*
and *"No extra keys"*; `_extract_sipoc_from_text` validates five;
`orchestrate.py:85-88` **strips to exactly those five before storing**. So a
pure rename produces a `process_map_sipoc` that fails the six-key check **every
time** — the gate would still never open. `process_metrics` has to be captured
or generated, which is new coaching, not a rename.

*(A fourth, smaller: v1 `team_members` is `{name, role}`
(`prompts.py:806`); v2 `team` is `{name, role, function}`. The third key has no
v1 source.)*

---

## 4. `orchestrate.py` is marked DELETE, not REWRITE

- **`REFACTORING_PROCEDURE.md` Appendix B** — *Disposition of the 55 backend
  files*: **Delete** — `phases/{phase}/orchestrate.py` × 5. Not in the
  **Rewrite** row.
- **Step 11.1** — *"Delete … the five `orchestrate.py` files"*.
- [`define/validate.py:33-36`](../backend/phases/define/validate.py#L33) — *"The
  v2 writer is the executor node, which captures through
  `CoachingResponse.fields_captured` into `artifacts` (§56.1); `orchestrate.py`
  is v1 and is deleted at procedure step 11.1."*

The ratified architecture never migrates this file. It replaces it. Rewriting
a file scheduled for deletion, in order to keep a v1 path alive, is the
investment CLAUDE.md §17 exists to prevent.

**A related inconsistency, noted not fixed:** §0.2's gate table says WATCH 7
clears when *"4.1 lands (… executor stops delegating to v1 `orchestrate_define`)"*,
but **step 4.1's own prompt says the executor *does* delegate to
`orchestrate_define`** at that step. So WATCH 7 does not in fact clear at 4.1
as the procedure currently reads — it clears when the executor gains its own
capture path, at **6.2** (`create_agent` with `response_format=CoachingResponse`).

---

## 5. The step cannot be verified without a browser

Step 3.4 rules: *"Coupled in the same commit, per ruling: … the `ui/index.html`
field names that render them. Leaving the UI reading fields that no longer
exist — even briefly — produces a workspace that renders blank panels with no
error."* Its verify method is **`manual-UI`** — the one method that needs
Vassilis in a browser. The handoff's proposed verification (raw grep +
set-compare + pytest) cannot cover 78 UI sites; the test suite has no UI test.

---

## Consequence

**The Define gate stays inert until the v2 capture path exists** — executor
node → `CoachingResponse.fields_captured` → `artifacts` — which is the
4.1 / 6.1 / 6.2 run, not a step before it. This does not block anything: no
case is running the Define gate today, and steps 2.4 → 3.3 are all unblocked.

**The immediate next step is procedure step 2.4**, as `REFACTORING_PROCEDURE.md`
Appendix D and the session-start hook both already say.

---

## The three routes — a founder ruling is owed

**Do not pick one by default.** All three are coherent; they differ in what
they spend and what they risk.

### Route A — carry v1 unchanged to 11.1, and delete it *(recommended)*
Change nothing now. The v1 path keeps working end-to-end as it does today; the
Define gate stays inert; the v2 capture path arrives with the executor at
6.1/6.2 and `orchestrate.py` + `EXTRACTION_DEFINE`'s Define block are deleted
at 11.1.
- **Cost:** the Define gate is inert for the length of the build. WATCH 7 stays
  open, re-pointed at 6.2 rather than 4.1.
- **Risk:** low. It is what Appendix B, step 11.1 and `validate.py`'s docstring
  all already say happens.
- **Why recommended:** it spends nothing on a file marked for deletion, and it
  is the only route that does not put a `manual-UI` commit in front of the
  foundation steps that everything else depends on.

### Route B — full v1→v2 cutover now, as one large commit
Rewrite `EXTRACTION_DEFINE`, `orchestrate.py`, all 78 UI sites, Measure's
seeding, `routes.py`, `upload/agent.py` and the three cross-phase briefs
together — effectively executing step 3.4's Define portion *including* the UI
half that is outstanding for all five phases.
- **Cost:** large, and it is really step 3.4 + the UI coupling, not step 4.1.
  Needs design rulings on 5W2H retention, `process_metrics` capture, and
  `meaning` in the registry.
- **Risk:** high. `manual-UI` verify; touches the one file (`ui/index.html`,
  7,172 lines) that has no test coverage; done out of horizontal order, ahead
  of 2.4–3.3.
- **When it is right:** if a working Define gate is needed for a demo before
  the foundation lands.

### Route C — bring the executor forward
Reorder the procedure so 6.1/6.2 (planner/executor with `CoachingResponse`)
run before the remaining Stage 2–3 steps, so the v2 writer exists sooner and v1
is retired earlier.
- **Cost:** a procedure reordering, which is a §56-class amendment.
- **Risk:** medium-high. 6.2 depends on middleware, tool binding and
  `PhaseState` — the reorder pulls most of Stages 3–5 with it, which is why the
  procedure ordered it this way.

---

## What this audit changed

**Nothing in the code.** `git diff` over `*.py`, `*.html` is empty. Test suite
**30 passed**, unchanged.

Recorded in `CONTINUITY.md` v4.8 (§5's next-step, §6's WATCH 7 entry) and in
`REFACTORING_PROCEDURE.md`'s status banner, both at commit `7dd473f`. §0.2's
WATCH 7 gate row and step 3.4's consequence note are **left as written**, per
the annotate-don't-rewrite rule, and read against the banner.
