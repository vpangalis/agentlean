> **SUPERSEDED 2026-09-26 by the founder's R7** (`docs/requirements/define.md`): the Define rubric is `DEFINE_RUBRIC` in `backend/core/prompts.py`, graded by `backend/validation/rubric.py` — one criterion per element, pass/fail with a reason. Historical from here; never cite it as current.

# G-40 (F1) — a draft `DEFINE_RUBRIC` for Layer 2d

> **DRAFT — for founder ruling, not ratified.** This is an implementer's proposal of domain
> content that procedure step 7.2 says must be a founder decision (*"a rubric written by an
> implementer is a guess at what good coaching looks like"*). It is offered as a starting point to
> strike through, not as the rubric. Read at HEAD `44d111a`, 2026-09-25. Paths relative to `agent-improve/`.

## 1. Frame — what the rubric must fit

| Constraint | Source | Effect on this draft |
|---|---|---|
| The constant is `{PHASE}_RUBRIC` → `DEFINE_RUBRIC` in `core/prompts.py` | ARCH §22 (L2339) | Text block below, same bullet form as `COACHING_QUALITY_RUBRIC` (`core/prompts.py:1635`) |
| Grades the **gate document**, never the coach's process | ARCH §36 | No criterion about coaching behaviour — those are `COACHING_QUALITY_RUBRIC`'s |
| Ratified Define coverage: `problem_statement`, `voc_summary`, `business_case`, `project_scope`, `team`, `goal_statement` | ARCH §36 "ratified rubric coverage" (L3956–3972) | R01, R02, R03, R04, R07, R08 are **inside** ratified coverage; every other criterion is **an addition for the founder to accept or strike** (column "Cov.") |
| Every field must "pass the quality rubric" to open the gate | ARCH §39.1.2 Option A note | Coverage of all 12 + registry is proposed |
| **Define has no Tier 2** → every criterion is Tier 1; **no `warning`** is ever issued | ARCH §35; `phases/gate_registry.py:68–77` (`tier_2 = ()`); feature **DEF-045** (*"never issues a 'warning' verdict and acknowledged_gaps is always empty"*); `test_gate_documents.py::test_define_has_no_tier_2` | Status is `pass` or `fail` only. "Needs-work" is a **descriptor for the feedback**, not a third status (see §3, Q1) |
| Deterministic where no judgment is needed; lookups, not opinions | ARCH §62.9 S-F26 B2/B3/B4/B7, §36 | Column "Mode": **code** criteria run in `DMAICGateValidator.deterministic_verdicts` (G-23 draft, Q1) before the model call; **LLM** criteria go to the `grader` role at 0.1 |
| No retrieval while grading | S-F26 B6 | The rubric text carries the standard itself |
| Belt-level awareness | §35 | DOE is the only belt-gated item, and it is not a Define item → **no Define criterion varies by `belt_level`** |
| Layer 2b already blocks on presence and dict sub-keys | `gate_registry.py:298` `missing_gate_fields` | Rubric criteria never re-check bare presence; they start where 2b stops |

## 2. The twelve Define fields + registry (`backend/phases/define/schema.py`)

| # | Field | Type | Line | 2b sub-keys |
|---|---|---|---|---|
| 1 | `business_case` | `str` | 177 | — |
| 2 | `team` | `list[dict]` | 184 | `name, role, function` (`TEAM_MEMBER_KEYS`, :143) |
| 3 | `voc_summary` | `str` | 193 | — |
| 4 | `problem_statement` | `str` | 200 | — (composed from 5W2H, §39.1.3) |
| 5 | `baseline_estimate` | `str` | 208 | — |
| 6 | `project_scope` | `dict` | 216 | `in_scope, out_scope` (:140) |
| 7 | `goal_statement` | `str` | 223 | — |
| 8 | `target_value` | `str` | 231 | — |
| 9 | `target_date` | `str` (ISO) | 240 | — |
| 10 | `secondary_metrics` | `str` | 250 | — |
| 11 | `process_map_sipoc` | `dict` | 257 | six `SIPOC_KEYS` (:133) |
| 12 | `issues_and_barriers` | `str` | 265 | — |
| + | `metric_definitions` | `list[dict]` | 275 | `name, unit, meaning` (:123) |

Gate document = these 13 + `phase_metrics` + 4 gate-metadata fields = 18 keys (`DefineOutput`,
`schema.py:146`; D17). `phase_metrics` is derived at assembly (`define_phase_metrics`, :339) and is
not graded.

## 3. Output shape — consistent with the repo's verdict structures

Specified, not built — **S-C20** (ARCH §62.1, L9690–9696):
```python
class CriterionVerdict(BaseModel):
    criterion: str
    tier:      int                                     # 1 or 2
    status:    Literal["pass", "warning", "fail"]
    feedback:  str                                     # specific, per criterion
```
Built, for the **other** grader — `backend/validation/schemas.py:84`:
`class CriterionResult(BaseModel): criterion: str; status: Literal["pass", "fail"]; feedback: str = ""`
inside `CoachingGraderVerdict.criteria: list[CriterionResult]` (:108). **Not reused here**: §36 keeps
the two graders apart, and S-C20 carries `tier`.

**Proposed Define output (DRAFT):** `GraderVerdict(phase="define", verdicts=[CriterionVerdict, …])`
(G-11 shape proposed in the G-23 draft), one verdict per criterion id below, and:

| Descriptor | `CriterionVerdict.status` | `tier` | `feedback` |
|---|---|---|---|
| **pass** | `"pass"` | `1` | `""` |
| **needs-work** | `"fail"` | `1` | names the one concrete fix (*"state what is out of scope, not only what is in"*) |
| **fail** | `"fail"` | `1` | names what is missing or wrong and why it blocks |
| *(never)* | `"warning"` | — | unreachable for Define (DEF-045) |

`criterion` = `"DEF-R04 problem_statement"` — id + field, so the gate screen can attach the verdict
to a `review_rows` row (`gate_registry.py:178`).

## 4. The criteria (DRAFT)

Mode: **code** = deterministic in `deterministic_verdicts`; **LLM** = `grader` call; **mixed** = code
part first, model only if it passes. Tier = **1 (blocks)** for every row (Define, §35). Cov. = inside
§36's ratified Define coverage (✓) or an addition (+).

| Id | Field(s) → doc key | What is checked (LSS tollgate) | pass | needs-work | fail | Mode | Cov. |
|---|---|---|---|---|---|---|---|
| **DEF-R01** | `business_case` | Why this project, now: linked to a business goal; impact quantified (COPQ / savings) — [DSI], [SSI] "expected benefits" | Names the business objective it serves **and** a quantified impact (money, time or volume) | Linked to an objective, impact only qualitative | No business reason, or restates the problem | mixed: if a `calculate_expected_savings` entry exists in `computation_results`, the figure quoted must match it (S-F26 B3); rest LLM | ✓ |
| **DEF-R02** | `team` | Sponsor/champion present; process owner; SMEs — [DSI] "sponsored by a champion"; §39.1.4 roles | ≥1 **Sponsor/Champion**, 1 **Project Leader**, 1 **Process Owner**, each named | Sponsor and leader present, no process owner | No sponsor/champion | code (role match against §39.1.4's four role names, case-insensitive) | ✓ |
| **DEF-R03** | `voc_summary` | Customers identified; their needs stated; needs turned into measurable requirements (CTQ) — [DSI] VOC questions; [MoP] Q12 CTQs | Names the customer(s), their need in their terms, **and** a measurable requirement (CTQ) | Customers and needs, no measurable requirement | No customer named, or internal opinion only | LLM | ✓ |
| **DEF-R04** | `problem_statement` | Specific gap, measurable, located; **no cause, no solution, no blame** — [SSI] "Assign a Cause or Blame / Include a Solution" to avoid | What, where, when, how much (magnitude vs a requirement), who is affected; no cause, solution or blame | Measurable but missing where/when, or impact on the customer | Embeds a cause or a solution, or has no magnitude | LLM | ✓ |
| **DEF-R05** | `baseline_estimate` + `metric_definitions` | Measurable current state in a registered metric — [MoP] Q1 "Big Y" | Numeric value + unit; the metric is a registry `name` | Numeric, unit absent or not the registry unit | No number | code (numeric token; registry `name` match); LLM only for unit equivalence | + |
| **DEF-R06** | `metric_definitions` | The project's Y is defined once: name, unit, operational meaning | Each entry's `meaning` says how the metric is counted/measured | A `meaning` restates the name | *(2b already blocks absent keys)* — meaning contradicts the unit | mixed | + |
| **DEF-R07** | `project_scope` | Boundaries in and out — [SSI] "what is included and … what is not included" | `in_scope` gives process start/end; `out_scope` excludes something a reader might assume included | `out_scope` is trivial ("n/a", "everything else") | In and out overlap or contradict | mixed: code rejects `out_scope` ∈ {n/a, none, everything else}; rest LLM | ✓ |
| **DEF-R08** | `goal_statement` | SMART — [SSI] Specific, Measurable, Achievable, Relevant, Time-bound | All five present; same metric and direction as the problem; carries `target_value` and `target_date` | One SMART element weak (e.g. achievability not argued) | Not measurable or not time-bound, or a different metric from the problem | LLM | ✓ |
| **DEF-R09** | `target_value` + `baseline_estimate` | Comparable target, same metric/unit, moves the right way | Numeric, same unit as baseline, differs from it in the goal's direction | Direction not evident from the goal | Equals the baseline, or non-numeric | code (numeric, ≠ baseline, unit match); LLM for direction | + |
| **DEF-R10** | `target_date` | Time-bound plan — [SSI] milestones | ISO date, after the gate date | *(see Q3)* | Not ISO, or in the past | code | + |
| **DEF-R11** | `secondary_metrics` | Side-effect watch (what could get worse) | Names ≥1 metric plausibly harmed by improving the Y | Named but unrelated to the process | Restates the primary metric | LLM | + |
| **DEF-R12** | `process_map_sipoc` | High-level SIPOC — [DSI] SIPOC question | `process_steps` spans `in_scope`'s start→end in ~4–7 steps; `customers` agree with `voc_summary`; `process_metrics` names a registry metric | Steps too granular/too few, or customers differ from VOC | Steps cover only part of the scoped process (§41 partial map) | mixed: code checks `process_metrics` ↔ registry `name` (first link of S-F26 B7); rest LLM | + |
| **DEF-R13** | `issues_and_barriers` | Constraints and risks named — [MoP] Q11 | Specific blockers/risks, or the explicit "none identified at this stage" | Generic ("time", "resources") with no project detail | Restates `out_scope` or the problem | LLM | + |
| **DEF-R14** | cross-field | One Y end-to-end: problem, baseline, goal, target, registry, SIPOC metric are the same metric — §36's cross-field reason for 2d | All six name the same metric | Same metric, wording drifts | Two different Y's (the §36 "error rate vs cycle time" failure) | mixed: code checks registry `name` in baseline / target / SIPOC; LLM for problem & goal | + |

**Counts:** 14 criteria · 6 inside ratified coverage · 8 additions · code-only 2 (R02, R10) · mixed 7
(R01, R05, R06, R07, R09, R12, R14) · LLM-only 5 (R03, R04, R08, R11, R13).

**Tollgate items with no Define field — not graded, listed so the omission is a decision:** project
plan / milestones beyond `target_date`; stakeholder analysis ([MoP] Q9–10); team training ([DSI]);
Value Stream Map ([DSI]); sponsor **sign-off** (§39.1.4 says "approval required at the gate" — no field
records it). Adding any needs `/change-gate-schema`, outside G-40.

## 5. Draft constant text (for `core/prompts.py`; the LLM half only — code halves never reach the model)

```
- DEF-R05 baseline_estimate: the unit is the registry unit for that metric (equivalent, not identical text)
- DEF-R06 metric_definitions: each meaning says how the metric is counted, not a restated name
- DEF-R09 target_value: moves from the baseline in the direction the goal states
- DEF-R01 business_case: names the business objective served AND a quantified impact; fail if no business reason
- DEF-R03 voc_summary: names the customer, their need in their words, and a measurable requirement (CTQ)
- DEF-R04 problem_statement: states what, where, when, how much and who is affected; FAILS if it contains a cause, a solution or blame
- DEF-R07 project_scope: in_scope gives the process start and end; out_scope excludes something a reader would assume included
- DEF-R08 goal_statement: specific, measurable, achievable, relevant, time-bound; same metric and direction as the problem
- DEF-R11 secondary_metrics: names at least one metric that could get worse
- DEF-R12 process_map_sipoc: process_steps span the scoped process; customers agree with voc_summary
- DEF-R13 issues_and_barriers: specific blockers, or the explicit "none identified at this stage"
- DEF-R14 cross-field: problem, baseline, goal and target describe the same metric
Every criterion is Tier 1 in Define: status is "pass" or "fail", never "warning". Feedback names the one fix.
```

## 6. Open questions for the founder

| # | Question | Options | Recommendation (DRAFT) |
|---|---|---|---|
| **Q1** | "Needs-work" has no status in Define (no `warning`). What does it do? | A: maps to `fail` (blocks, costs one of 3 attempts, feedback names the fix). B: maps to `pass` + a coaching note outside the verdict. C: give Define a Tier 2 | **A** — the only option consistent with Option A and DEF-045. C reverses a 2026-08-26 ruling. Watch the cap: with 14 criteria, a strict grader can burn 3 attempts; calibrate on the eval set first |
| **Q2** | Scope: grade only §36's six ratified fields, or all 13 + cross-field? | A: 6 (R01–R04, R07, R08). B: all 14 | **B**, because §39.1.2 says every Define field "passes the quality rubric" and R14 is 2d's stated reason for existing (§36). Accept or strike each "+" row |
| **Q3** | Hard thresholds the tollgate literature does not fix: is a quantified business case **mandatory** (schema says "where the Belt has it", `schema.py` business_case description), and is there a maximum project length for `target_date`? | A: mandatory money + no max date. B: quantity of any kind + no max. C: add a 6-month max | **B** — any quantified impact; money is Measure's (`calculate_expected_savings` is optional in Define). No date maximum without a ruling |

## 7. Sources (fetched 2026-09-25; only these are cited)

| Tag | Source | Used for |
|---|---|---|
| [DSI] | Six Sigma Development Solutions, "Lean Six Sigma 'Define' Tollgate Review" — https://sixsigmadsi.com/six-sigma-define-tollgate-review/ | Champion sponsorship, SMEs, business case / savings estimates, VOC → "specific, measurable requirements", SIPOC, VSM |
| [MoP] | Master of Project, "Tollgate Checklist: 12 Questions to Complete Define Stage" — https://blog.masterofproject.com/tollgate-review-check-list/ | Big Y, problem/goal statement, scope, team, plan, stakeholders, constraints, CTQs |
| [SSI] | Six Sigma Institute, "Six Sigma DMAIC Problem Statement & Project Charter" — https://www.sixsigma-institute.org/Six_Sigma_DMAIC_Process_Define_Phase_Six_Sigma_Project_Charter.php | Charter elements; problem statement must not "Assign a Cause or Blame" or "Include a Solution"; SMART goal |

ASQ (asq.org/quality-resources/project-charter) and GoLeanSixSigma (goleansixsigma.com/tollgate-review/)
were attempted and returned HTTP 403 — **not cited**. The iSixSigma problem-statement page returned no
body text — **not cited**.
