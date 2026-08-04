# Improve Phase — eBook Extraction

**Status:** raw extraction for review. **Not a SKILL.md.** Do not wire into
`DMAICSkillsMiddleware` until reviewed and signed off.

**Source:** `agent-improve/data/knowledge/5_BB_EB_MT_v11.1_PDF2_compressed (1).pdf`
— LSS Black Belt eBook v11.1 MT, © Open Source Six Sigma, LLC.

**Page convention:** `book pN / PDF pN+3`.

**eBook scope:** Improve Phase = book pp423–559 / PDF pp426–562. Modules: Welcome
to Improve (p423), Process Modeling Regression (p426), Advanced Process Modeling
(p445), Designing Experiments (p472), Experimental Methods (p487), Full Factorial
Experiments (p502), Fractional Factorial Experiments (p531), Wrap Up and Action
Items (p551), Quiz (p557).

> **Read this phase against the eBook's own caveat.** Improve is 137 pages
> overwhelmingly about Design of Experiments, and the eBook repeatedly says most
> projects will not need DOE. The methodology content and the expected practice
> diverge more here than in any other phase — which matters directly for how the
> coach should behave.

---

## 1. Required deliverables

Verbatim from **Improve Phase Action Items** (book p552 / PDF p555). Delivery
format: "each candidate will present in a **Power Point presentation at the
beginning of the Control Phase training**."

| # | Deliverable | eBook wording |
|---|---|---|
| 1 | Team Members | "Team Members (Team Meeting Attendance)" |
| 2 | Primary Metric | "Primary Metric" |
| 3 | Secondary Metric(s) | "Secondary Metric(s)" |
| 4 | Experiment Justification | "Experiment Justification" |
| 5 | Experiment Plan / Objective | "Experiment Plan / Objective" |
| 6 | Experiment Results | "Experiment Results" |
| 7 | Project Plan | "Project Plan" |
| 8 | Issues and Barriers | "Issues and Barriers" |

**Phase goal**, from *Improve Phase Overview—The Goal* (book p552 / PDF p555):

> - "Determine the **optimal levels of the variables** which are significantly
>   impacting your Primary Metric."
> - "Demonstrate a working knowledge of **modeling as a means of process
>   optimization**."

**The eBook's own warning about DOE**, same page:

> "Avoid getting into **analysis paralysis**, only use DOE's as necessary. **Most
> problems will NOT require the use of Designed Experiments** however to qualify
> as a Black Belt you at least need to have an understanding of DOE as described
> in this course."

And again at book p554 / PDF p557:

> "Over 80% of projects will realize their solutions in the Analyze Phase —
> Designed Experiments can be extremely effective when used properly. **It is
> imperative that a Designed Experiment is justified.** From an application and
> practical standpoint **if you can identify a solution by utilizing the strategy
> and tools within the Measure and Analyze Phases then do it. Do not force
> Designed Experiments.**"
>
> "Remember your sole objective in conducting a Lean Six Sigma project is to
> **find a solution to the problem**. You created a Problem Statement and an
> Objective Statement at the beginning of your project. However you can reach a
> solution that achieves the stated goals in the Objective Statement, then
> implement them and move on to another issue."

**"Experiment Justification" is a first-class deliverable** precisely because the
default answer is often "no experiment needed."

---

## 2. Recommended tools and techniques

| Tool | eBook location | Purpose |
|---|---|---|
| **Simple regression** | book p426+ / PDF p429+ | Process modeling |
| **Multiple regression (MLR)** | book p464 / PDF p467 | `Flight Regression MLR.mtw` |
| **Advanced process modeling** | book p445+ / PDF p448+ | Non-linear and multi-variable |
| **Fractional Factorial / screening designs** | book p531+ / PDF p534+ | "Used when the process or product knowledge is **low**… need to screen [factors] down to a more reasonable or workable level" |
| **Full Factorial** | book p502+ / PDF p505+ | "Used when it is necessary to fully understand the effects of **interactions** and when there are between **2 to 5** input variables" |
| **Response surface methods** | book p477 / PDF p480 | "(not typically applicable) … used to optimize a response typically when the response surface has significant curvature" |
| **Experimental methods** | book p487+ / PDF p490+ | Randomisation, replication, blocking |
| **Main effects analysis** | Improve modules | Factor effect magnitude |
| **Pilot / simulation** | book p554 / PDF p557 | "Simulate the New Process" → "Validate New Process" |
| **Catapult exercise** | book p479 / PDF p482 | `Catapult.mtw` — the standard DOE teaching exercise |

**Design selection rule** (book p477 / PDF p480):

| Situation | Design |
|---|---|
| Process/product knowledge **low**, long list of candidate factors | **Fractional Factorial** (screening) |
| Need to understand **interactions**, 2–5 input variables | **Full Factorial** |
| Response surface has **significant curvature** | Response surface methods *(not typically applicable)* |

> "DOE is **iterative** in nature and may require more than one experiment at
> times… If we have a very good understanding of our process maybe we will only
> need one experiment, if not we very well may need a series of experiments."

**Full factorial notation** (book p477 / PDF p480): `2^k`, where k is the number
of input variables (factors) and 2 is the number of levels.

---

## 3. Gate checklist criteria

Verbatim from **Improve Phase Questions** (book p555 / PDF p558):

- Are the potential X's **measurable and controllable** for an experiment?
- Are they **statistically and practically significant**?
- **How much of the problem have you explained with these X's?**
- **Have you clearly justified the need for conducting a Designed Experiment?**
- Are adequate resources available to complete the project?
- What next steps are you recommending?

**Planning for Action grid** (same page) — WHAT / WHO / WHEN / WHY / WHY NOT /
HOW across:

> A DOE to meet your problem solving strategy · Scheduling your experimental plan
> · Executing your planned DOE · Analysis of results from your DOE · **Obtain
> mathematical model to represent process** · **Planning the pilot validation for
> breakthrough** · **Present statistical promise to process owner** · Prepare for
> implementation of final model · **Schedule resources for implementation
> timeline** · **Conclude on expected financial benefits**

**The eBook frames this checklist as a bridge, not a wrap-up** (book p555 / PDF
p558):

> "we have developed a follow up process that involves **planning for action
> between the conclusion of this phase and the beginning of the Control Phase**.
> It is imperative you complete this to keep you on the proper path."

---

## 4. Templates

| Template | eBook location | Notes |
|---|---|---|
| **Improve Phase Checklist** | book p555 / PDF p558 | The six questions above |
| Planning for Action grid | book p555 / PDF p558 | WHAT/WHO/WHEN/WHY/WHY NOT/HOW matrix |
| DOE design matrix | book p477+ / PDF p480+ | `2^k` factor/level table |
| `Catapult.mtw` | book p479 / PDF p482 | DOE teaching dataset |
| `Panel Cleaning.mtw` | book p519 / PDF p522 | Full factorial exercise |
| `Discount.mtw` | book p454 / PDF p457 | Regression exercise |
| `Flight Regression MLR.mtw` | book p464 / PDF p467 | Multiple regression exercise |
| `RB Stats Correlation.mtw` | book p430, p440 / PDF p433, p443 | Correlation exercise |

**Improve has the fewest fill-in templates of the five phases.** Its artefacts
are experiment designs, models and results — generated, not filled in.

---

## 5. Common pitfalls

Verbatim from **Improve Phase - The Roadblocks** (book p553 / PDF p556):

- "Lack of data"
- "Data presented is the **best guess by functional managers**"
- "Team members do not have the time to collect data"
- "Process participants do not participate in the analysis planning"
- "Lack of access to the process"

*(Identical to Analyse's roadblock list — the eBook notes "Many will be similar
throughout your project.")*

**The pitfalls the eBook stresses in prose are more specific and more useful:**

- **Forcing a Designed Experiment.** "Do not force Designed Experiments" (book
  p554). The single most emphasised warning in the phase, stated three times.
- **Analysis paralysis.** "Avoid getting into analysis paralysis, only use DOE's
  as necessary" (book p552).
- **Not justifying the experiment.** A named deliverable *and* a gate question.
- **Continuing past a solution you already have.** "You can reach a solution that
  achieves the stated goals in the Objective Statement, then implement them and
  move on to another issue — there are plenty!" (book p554).
- **X's that are not controllable.** "Are the potential X's measurable and
  **controllable** for an experiment?" — a significant X you cannot set is not an
  experimental factor.
- **Statistical significance without practical significance.** Asked again here,
  as in Analyse.
- **Not quantifying explanatory power.** "How much of the problem have you
  explained with these X's?" — R² or equivalent, not just a list of significant
  factors.
- **Skipping process-owner engagement.** "Present statistical promise to process
  owner" is a Planning for Action row.

---

## 6. Cross-phase dependencies

**From Analyse:**

| Needs | Used for |
|---|---|
| **Root Cause** | The thing the solution must address |
| **Strategy to reduce the X's** | Direct input to solution selection |
| Vital few X's, reduced to a practical number | The candidate experimental factors |
| Hypothesis test results | Establishes which X's are significant before optimising them |
| Modeling results | Regression models carry forward into optimisation |
| Statistical + practical significance verdicts | Re-tested at the Improve gate |

**Improve's internal sequence** (book p554 / PDF p557):

```
Analysis Complete
  → Identify Few Vital X's
  → Experiment to Optimize Value of X's
  → Simulate the New Process
  → Validate New Process
  → Implement New Process
  → Ready for Control
```

**Note "Simulate" precedes "Validate" precedes "Implement".** The pilot is not
optional in the roadmap even when DOE is skipped — the eBook's Planning for
Action row is "Planning the **pilot validation** for breakthrough."

**What Improve hands to Control:**

| Handed forward | Consumed by |
|---|---|
| Implemented / validated new process | Control — the thing being sustained |
| Optimal levels of the vital X's | Control — "Finalize Key Input Variables (KPIV) to meet goal" |
| Mathematical model of the process | Control — monitoring thresholds |
| Experiment results | Control — evidence base |
| Expected financial benefits | Control — "Verify Financial Impact" |
| Implementation timeline and resources | Control — Training and Documentation Plans |

---

## 7. Cross-reference against `ImproveOutput`

Schema as ratified in **ARCHITECTURE.md §4.10.2**. (Version note: see
`define_extraction.md` §7.)

### Covered — eBook deliverable has a field

| eBook deliverable | `ImproveOutput` field | Tier |
|---|---|---|
| Solution / optimal levels chosen | `selected_solution` | 1 |
| Experiment Results / pilot validation | `pilot_result` | 1 |
| Link from solution back to root cause | `solution_linked_to_root_cause` (dict, cross-phase ref) | 2 |
| Implementation timeline, owner, resources | `implementation_plan` | 2 |
| DOE main effects output | `computation_results` (`calculate_doe_main_effects`) | — |
| Methodology sources | `citations` | — |
| Belt-uploaded experiment data | `uploads` | — |
| Tier 2 fields the Belt chose to proceed without | `acknowledged_gaps` | — |

**`pilot_result`'s rubric already requires "practical AND statistical
significance, not one standing in for the other"** (§13.4) — this matches the
eBook's gate question exactly and is the model Analyse should follow (see
Analyse A-1).

**`solution_linked_to_root_cause` is a strong fit**: the eBook's whole Improve
logic is that the solution optimises the X's Analyse proved significant, and the
cross-phase reference dict makes that link machine-checkable (§4.7).

### GAPS — eBook deliverable with no corresponding field

| # | eBook deliverable | eBook ref | Severity | Note |
|---|---|---|---|---|
| **I-1** | **Experiment Justification** | book p552, p555 | **HIGH** | A named deliverable *and* a gate question ("Have you clearly justified the need for conducting a Designed Experiment?"), and the eBook's most-repeated warning. No field. **Note the inversion:** the valuable answer is often "no DOE — the solution came from Analyse," and there is nowhere to record that reasoning either. ARCHITECTURE.md §3.7.2 makes DOE a BB-only Tier 2 rubric item, which handles *whether to recommend it* but not *whether the Belt justified their decision*. |
| **I-2** | **Experiment Plan / Objective** | book p552 | **HIGH** | Named deliverable, distinct from results. Design type, factors, levels, runs, randomisation, blocking. No field. |
| **I-3** | **"How much of the problem have you explained with these X's?"** | book p555 | **HIGH** | Explanatory power — R², or variance explained. A gate question with no field. This is the question that distinguishes a solution addressing the main driver from one addressing a marginal factor. |
| **I-4** | **X's measurable and controllable** | book p555 | **MEDIUM** | Gate question. A significant X that cannot be controlled is not actionable, and the project needs to know that before designing around it. |
| **I-5** | **Simulate / Validate before Implement** | book p554 | **MEDIUM** | Three distinct roadmap steps. `pilot_result` covers validation; simulation and the implement-confirmation are not separable in the schema. |
| **I-6** | **Present statistical promise to process owner** | book p555 | **MEDIUM** | Planning for Action row. Owner engagement again (cf. Analyse A-5, Control's handover). Three phases ask for process-owner involvement; only Control has a field. |
| **I-7** | **Conclude on expected financial benefits** | book p555 | **MEDIUM** | Planning for Action row. `financial_impact_verified` is on `ControlOutput` only — the *expected* benefit at Improve and the *verified* benefit at Control are different claims at different times, and comparing them is exactly what makes verification meaningful. |
| **I-8** | **Mathematical model of the process** | book p555 | **MEDIUM** | "Obtain mathematical model to represent process." Regression coefficients reach `computation_results`; the model as a deliverable does not. Control needs it for monitoring thresholds. |
| **I-9** | **Next steps recommended** | book p555 | **LOW** | "What next steps are you recommending?" Partially covered by `implementation_plan`. |
| **I-10** | **Secondary Metric(s)** | book p552 | **HIGH** | Cross-phase gap — see Define D-1. Especially sharp here: Improve changes the process, so secondary metrics are the mechanism for catching damage done elsewhere. |
| **I-11** | **Project Plan** | book p552 | **MEDIUM** | Cross-phase gap — see Define D-4. |
| **I-12** | **Issues and Barriers** | book p552 | **MEDIUM** | Cross-phase gap — see Define D-5. |

### Observations for review

- **I-1 is the phase's defining gap.** Three of eight named deliverables concern
  the experiment (justification, plan, results) and only results has a field.
  The eBook's dominant message — *justify the experiment, and usually conclude
  you don't need one* — has no representation in the schema at all.
- **The DOE tension has a coaching consequence worth deciding explicitly.** The
  eBook devotes 137 pages to DOE and then tells the Belt not to use it. §3.7.2
  suppresses DOE recommendations for Green Belts entirely. Neither position
  captures the eBook's actual stance, which is: *every* Belt should reach a
  reasoned decision about whether an experiment is warranted, and record it. A
  Green Belt who correctly concludes "no DOE needed" has done the right thing and
  should get credit for it.
- **I-7 is the other half of Control's `financial_impact_verified`.** Without an
  expected figure recorded at Improve, "verified" at Control has nothing to
  verify against. The same pattern the cross-phase reference dicts solve
  elsewhere (§4.7) would apply cleanly here.
- **Improve's schema fit is good on the solution axis, weak on the experiment
  axis.** `selected_solution`, `pilot_result` and
  `solution_linked_to_root_cause` cover "what did you do and did it work."
  Nothing covers "how did you decide what to try."
