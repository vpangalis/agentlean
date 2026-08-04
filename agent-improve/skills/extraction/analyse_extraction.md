# Analyse Phase — eBook Extraction

**Status:** raw extraction for review. **Not a SKILL.md.** Do not wire into
`DMAICSkillsMiddleware` until reviewed and signed off.

**Source:** `agent-improve/data/knowledge/5_BB_EB_MT_v11.1_PDF2_compressed (1).pdf`
— LSS Black Belt eBook v11.1 MT, © Open Source Six Sigma, LLC.

**Page convention:** `book pN / PDF pN+3`.

**Naming:** the eBook spells this phase **"Analyze"**. Our internal phase key is
`analyse` (ARCHITECTURE.md §7.3.1) and prose uses British spelling. eBook
quotations below preserve the source spelling.

**eBook scope:** Analyze Phase = book pp236–422 / PDF pp239–425. Modules: Welcome
to Analyze (p236), X Sifting (p239), Inferential Statistics (p266), Introduction
to Hypothesis Testing (p281), Hypothesis Testing Normal Data Part 1 (p296) and
Part 2 (p339), Hypothesis Testing Non-Normal Data Part 1 (p368) and Part 2
(p395), Wrap Up and Action Items (p414), Quiz (p420).

**This is the largest phase in the eBook — 187 pages, roughly 27% of the book.**
The page-density map confirms it: Analyse dominates every 50-page band from
PDF 251 to PDF 500.

---

## 1. Required deliverables

Verbatim from **Analyze Deliverables** (book p416 / PDF p419). Delivery format is
specified: "each candidate will present in a **Power Point presentation at the
beginning of the Improve Phase training**."

| # | Deliverable | eBook wording |
|---|---|---|
| 1 | Team Members | "Team Members (Team Meeting Attendance)" |
| 2 | Primary Metric | "Primary Metric" |
| 3 | Secondary Metric(s) | "Secondary Metric(s)" |
| 4 | Data Demographics | "Data Demographics" |
| 5 | Hypothesis Testing | "Hypothesis Testing (applicable tools)" |
| 6 | Modeling | "Modeling (applicable tools)" |
| 7 | Strategy to reduce the X's | "Strategy to reduce the X's" |
| 8 | Project Plan | "Project Plan" |
| 9 | Issues and Barriers | "Issues and Barriers" |

**Phase goal**, from *Analyze Phase Wrap Up Overview* (book p415 / PDF p418):

> "Locate the variables significantly impacting your Primary Metric. Then
> establish **Root Causes** for X variables using Inferential Statistical
> Analysis such as **Hypothesis Testing and Simple Modeling**."

**The double-significance rule.** The roadmap (book p417 / PDF p420) carries
**two** decision diamonds in series before a root cause is accepted:

```
Perform Statistical Tests
   → Statistically Significant?  N → back
   → Y
State Practical Conclusion
   → Practically Significant?    N → back
   → Y
   → Root Cause?                 N → back
   → Y → Update FMEA → Identify Root Cause → Ready for Improve and Control
```

**Statistical significance alone is not sufficient.** A result can clear the
p-value test and still fail the practical test, and the eBook routes it back.

**A striking claim about where solutions actually appear** (book p417 / PDF p420):

> "**Over 80% of projects will realize their solutions in the Analyze Phase** –
> then we must move to the Control Phase to assure we can sustain our
> improvements."

Repeated at book p554 / PDF p557 in the Improve wrap-up. This is the eBook's own
argument that Improve's DOE machinery is the exception, not the norm.

---

## 2. Recommended tools and techniques

| Tool | eBook location | Purpose |
|---|---|---|
| **X Sifting** | book p239+ / PDF p242+ | Determining the impact of process inputs |
| **Graphical analysis** | book p418 / PDF p421 | "Is existing data laid out graphically?" — first gate question |
| **Box Plots** | book p159+ / PDF p162+ | Distribution comparison across groups |
| **Inferential Statistics** | book p266+ / PDF p269+ | Basis for generalising from sample to process |
| **Hypothesis Testing — normal data** | book p296–367 / PDF p299–370 | Two parts; the bulk of the phase |
| **Hypothesis Testing — non-normal data** | book p368–413 / PDF p371–416 | Two parts |
| **ANOVA** | book p166+ / PDF p169+ | Means across 3+ groups |
| **Chi-Square** | book p293, p396 / PDF p296, p399 | Attribute / count data |
| **Correlation** | book p427+ / PDF p430+ | Relationship strength |
| **Simple regression / modeling** | book p424+ / PDF p427+ | "Simple Modeling" per the phase goal |
| **Non-parametric tests** | book p382+ / PDF p385+ | `Nonparametric.mtw` exercises |
| **Variance components** | book p391 / PDF p394 | `Var_Comp.mtw` |
| **FMEA (update)** | book p417, p418 | Roadmap step and gate question |
| **Fishbone** | book p88, p91+ / PDF p91, p94+ | Carried from Measure for root cause exploration |

**The eBook's stated analytical sequence** (book p417 / PDF p420):

1. Vital Few X's Identified *(from Measure)*
2. **State Practical Theories** of Vital Few X's impact on the problem
3. **Translate Practical Theories into Scientific Hypothesis**
4. Select Analysis Tools to Prove/Disprove Hypothesis
5. Collect Data
6. Perform Statistical Tests
7. State Practical Conclusion
8. Update FMEA
9. Identify Root Cause

**Step 3 is the discipline the phase is built on** — a practical theory is not
testable until it is translated into a formal hypothesis. ARCHITECTURE.md §3.7.2
lists "statistical problem statement" as a Black-Belt-only Tier 2 item; the
eBook's gate asks every Belt "What is the statement of Statistical Problem?"

**A note on sample size** (book p416 / PDF p419): "Sample size is dependent on
the type of data." Analyse inherits Measure's sample-size tooling.

---

## 3. Gate checklist criteria

Verbatim from **Analyze Questions** (book p418 / PDF p421). The eBook introduces
this checklist as "**a template that should be used with each project** to assure
you take the proper steps – remember, Six Sigma is very much about taking steps.
Lots of them and in the correct order."

**Define Performance Objectives — Graphical Analysis**
- Is existing data laid out graphically?
- Are there newly identified secondary metrics?
- Is the response discrete or continuous?
- Is it a Mean or a variance problem or both?

**Document Potential X's — Root Cause Exploration**
- Are there a reduced number of potential X's?
- Who participated in these activities?
- Are the number of likely X's reduced to a practical number for analysis?
- **What is the statement of Statistical Problem?**
- **Does the process owner buy into these Root Causes?**

**Analyze Sources of Variability — Statistical Tests**
- Are there completed Hypothesis Tests?
- **Is there an updated FMEA?**

**General Questions**
- Are there any issues or barriers preventing you from completing this phase?
- Do you have adequate resources to complete the project?

**Planning for Action grid** (same page) — WHAT / WHO / WHEN / WHY / WHY NOT /
HOW across:

> Qualitative screening of vital from controllable trivial X's · Qualitative
> screening for other factors · Quantitative screening of vital from controllable
> trivial X's · Ensure compliance to problem solving strategy · Quantify risk of
> meeting needs of customer, business and people · Predict risk of sustainability
> · Chart a plan to accomplish desired state of culture · Assess shift in process
> location · Minimise risk of process failure · Modeling Continuous or Non
> Continuous Output · Achieving breakthrough in Y with minimum efforts ·
> **Validate Financial Benefits**

---

## 4. Templates

| Template | eBook location | Notes |
|---|---|---|
| **Analyze Phase Checklist** | book p418 / PDF p421 | The eBook calls this "a template that should be used with each project" |
| Planning for Action grid | book p418 / PDF p421 | WHAT/WHO/WHEN/WHY/WHY NOT/HOW matrix |
| FMEA form (update) | book p670 / PDF p673 | Re-scored RPNs after root cause work |
| `HypoTestStud.mtw` / `Hypoteststud.mtw` | book p334, p381+ / PDF p337, p384+ | Hypothesis testing exercises |
| `Nonparametric.mtw` | book p382 / PDF p385 | Non-normal data exercises |
| `Var_Comp.mtw` | book p391 / PDF p394 | Variance components |
| `BBaptitude.mtw` | book p392 / PDF p395 | Exercise dataset |
| `Billy Bobs Pool.mtw` | book p317 / PDF p320 | Exercise dataset |
| `RB Stats Correlation.mtw` | book p430, p440 / PDF p433, p443 | Correlation exercises |

**Analyse is the phase with the fewest fill-in templates and the most datasets.**
Its artefacts are test results and conclusions rather than completed forms.

---

## 5. Common pitfalls

Verbatim from **Analyze Phase - The Roadblocks** (book p416 / PDF p419):

- "Lack of data"
- "Data presented is the **best guess by functional managers**"
- "Team members do not have the time to collect data"
- "**Process participants do not participate in the analysis planning**"
- "**Lack of access to the process**"

**Additional pitfalls implied by the text:**

- **Stopping at statistical significance.** The roadmap's second diamond —
  "Practically Significant?" — exists because a statistically significant result
  that moves nothing is not a root cause.
- **Skipping the translation step.** Going from practical theory straight to a
  test, without stating the scientific hypothesis, is the step the gate question
  "What is the statement of Statistical Problem?" is designed to catch.
- **Root causes the process owner does not accept.** "Does the process owner buy
  into these Root Causes?" is a gate question — a technically correct root cause
  the owner rejects will not survive Improve.
- **Not updating the FMEA.** Explicit roadmap step and gate question. The FMEA
  from Measure is stale once root causes are known.
- **Choosing the wrong test family.** "Is the response discrete or continuous?"
  and "Is it a Mean or a variance problem or both?" are asked *before* the test
  questions — the eBook is guarding against running a t-test on count data.
- **Too many X's to analyse.** Asked twice: "Are there a reduced number of
  potential X's?" and "Are the number of likely X's reduced to a practical number
  for analysis?"

---

## 6. Cross-phase dependencies

**From Measure:**

| Needs | Used for |
|---|---|
| **Vital Few X's** | The roadmap's stated entry condition — "Vital Few X's Identified" |
| Baseline / capability / sigma level | The reference the causal hypothesis links back to |
| FMEA | Updated during Analyse; "Is there an updated FMEA?" is a gate question |
| Detailed process map | Root cause exploration |
| MSA result | Precondition — hypothesis tests on unvalidated data are meaningless |
| Data demographics / basic statistics on Y | "Data Demographics" is an Analyse deliverable |
| Centering vs spread diagnosis | "Is it a Mean or a variance problem or both?" |
| Secondary metrics | "Are there newly identified secondary metrics?" |

**What Analyse hands to Improve and Control:**

| Handed forward | Consumed by |
|---|---|
| **Root Cause** | Improve — the thing the solution must be linked to |
| Strategy to reduce the X's | Improve — the input to solution selection |
| Hypothesis test results | Improve and Control — evidence base |
| Updated FMEA | Control — becomes the Monitoring Plan (book p670 / PDF p673) |
| Modeling results | Improve — regression models carry into process optimisation |

**The roadmap's exit is "Ready for Improve *and Control*"** (book p417 / PDF
p420) — not Improve alone. Consistent with the 80% claim: for most projects the
solution is already visible here and Improve's DOE work is optional.

---

## 7. Cross-reference against `AnalyseOutput`

Schema as ratified in **ARCHITECTURE.md §4.10.2**. (Version note: see
`define_extraction.md` §7.)

### Covered — eBook deliverable has a field

| eBook deliverable | `AnalyseOutput` field | Tier |
|---|---|---|
| Root Cause | `root_cause_statement` | 1 |
| Hypothesis Testing evidence | `root_cause_validation` | 1 |
| Link from root cause to baseline | `causal_hypothesis` (dict, cross-phase ref) | 2 |
| Alternatives rejected | `ruled_out_causes` | 2 |
| t-test / ANOVA / chi-square / correlation / regression output | `computation_results` (5 computation tools) | — |
| Methodology sources | `citations` | — |
| Belt-uploaded analysis data | `uploads` | — |
| Tier 2 fields the Belt chose to proceed without | `acknowledged_gaps` | — |

**`causal_hypothesis` is a genuinely good fit for this phase.** The eBook's
"Translate Practical Theories into Scientific Hypothesis" step and its insistence
on linking back to the Primary Metric are exactly what the cross-phase reference
dict (`references_phase` / `references_field` / `references_value`, §4.7)
encodes. This is the strongest schema-to-source alignment in the five phases.

### GAPS — eBook deliverable with no corresponding field

| # | eBook deliverable | eBook ref | Severity | Note |
|---|---|---|---|---|
| **A-1** | **Practical significance — separate from statistical** | book p417 | **HIGH** | The roadmap has **two** gates in series. `root_cause_validation` (Tier 1) covers "statistical or observational evidence"; nothing separately records that the Belt tested and confirmed *practical* significance. A statistically significant X that moves the Y by 0.1% passes our schema and fails the eBook's roadmap. Note Improve's rubric already requires "practical AND statistical significance" for `pilot_result` (§13.4) — Analyse should be symmetric. |
| **A-2** | **Statement of Statistical Problem** | book p418 | **HIGH** | Explicit gate question for **every** Belt in the eBook. ARCHITECTURE.md §13.1 has "statistical problem statement" as **BB-only, no field**, and places it in *Define*. The eBook asks it in *Analyse*, of everyone. Two divergences in one item: belt-level and phase placement. |
| **A-3** | **Strategy to reduce the X's** | book p416 | **HIGH** | Named deliverable and the direct input to Improve's solution selection. `root_cause_statement` says *what causes it*; the strategy says *what to do about it*. No field. |
| **A-4** | **Updated FMEA** | book p416, p417, p418 | **HIGH** | Roadmap step *and* gate question. §3.7.2 makes it BB-only Tier 2, conditional on an FMEA existing from Measure — which is itself unrecorded (see Measure M-4). The whole FMEA chain is unpersisted across three phases. |
| **A-5** | **Process owner buy-in on root causes** | book p418 | **HIGH** | "Does the process owner buy into these Root Causes?" A named gate question. `handover_documented` exists in Control but there is no owner-acceptance field at Analyse — and a root cause the owner rejects will not survive Improve. |
| **A-6** | **Data Demographics** | book p416 | **MEDIUM** | Named deliverable. Sample sizes, data sources, time periods, stratification. Partially reachable through `computation_results` inputs, but not asserted. |
| **A-7** | **Modeling (applicable tools)** | book p416 | **MEDIUM** | Named deliverable, distinct from hypothesis testing. Regression output lands in `computation_results` via `linear_regression` / `pearson_correlation`, so the *numbers* are reachable — the deliverable assertion is not. |
| **A-8** | **Discrete vs continuous response; mean vs variance problem** | book p418 | **MEDIUM** | Two gate questions that determine test selection. No field. Getting this wrong invalidates every downstream test. |
| **A-9** | **Reduction of potential X's to a practical number** | book p418 | **MEDIUM** | Asked twice at the gate. Continues the unrecorded vital-few-X's chain (Measure M-6). |
| **A-10** | **Secondary Metric(s)** | book p416 | **HIGH** | Cross-phase gap — see Define D-1. Analyse additionally asks "Are there **newly identified** secondary metrics?", so the set can grow here. |
| **A-11** | **Project Plan** | book p416 | **MEDIUM** | Cross-phase gap — see Define D-4. |
| **A-12** | **Issues and Barriers** | book p416 | **MEDIUM** | Cross-phase gap — see Define D-5. |
| **A-13** | **Validate Financial Benefits** | book p418 | **MEDIUM** | A Planning for Action row in Analyse, and again in Measure and Improve. We have `financial_impact_verified` only on `ControlOutput` — the eBook expects financial validation to be revisited at three earlier gates. |

### Observations for review

- **A-1 is the cleanest single fix in the whole extraction.** Adding a practical-
  significance field (or extending `root_cause_validation`'s rubric to require
  both) restores the eBook's two-diamond gate and makes Analyse symmetric with
  Improve's existing `pilot_result` requirement.
- **A-2 is a placement question, not just a coverage question.** We put
  "statistical problem statement" in Define as BB-only. The eBook asks it in
  Analyse, of every Belt, immediately before the hypothesis tests it governs.
  Worth deciding which is right rather than carrying both.
- **The FMEA chain (Measure M-4 → Analyse A-4 → Control's "updated FMEA"
  question) is unrecorded end to end.** Three phases each ask about it; no schema
  holds it.
- **This phase has the best schema fit of the five.** Four content fields against
  nine deliverables is a better ratio than Measure's, and `causal_hypothesis`
  captures the phase's central discipline precisely. Most gaps here are
  cross-phase (secondary metrics, project plan, issues) rather than Analyse-
  specific.
