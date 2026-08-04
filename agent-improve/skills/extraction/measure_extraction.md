# Measure Phase — eBook Extraction

**Status:** raw extraction for review. **Not a SKILL.md.** Do not wire into
`DMAICSkillsMiddleware` until reviewed and signed off.

**Source:** `agent-improve/data/knowledge/5_BB_EB_MT_v11.1_PDF2_compressed (1).pdf`
— LSS Black Belt eBook v11.1 MT, © Open Source Six Sigma, LLC.

**Page convention:** `book pN / PDF pN+3`. See `define_extraction.md` §Page
convention for why both are given.

**eBook scope:** Measure Phase = book pp86–235 / PDF pp89–238. Modules: Welcome
to Measure (p86), Process Discovery (p89), Six Sigma Statistics (p138),
Measurement System Analysis (p171), Process Capability (p206), Wrap Up and Action
Items (p227), Quiz (p233).

---

## 1. Required deliverables

Verbatim from **Measure Phase Deliverables** (book p229 / PDF p232). The eBook
specifies the delivery format: "each candidate should present in a **Power Point
presentation to their mentor and project Champion**."

| # | Deliverable | eBook wording |
|---|---|---|
| 1 | Team Members | "Team Members (Team Meeting Attendance)" |
| 2 | Primary Metric | "Primary Metric" |
| 3 | Secondary Metric(s) | "Secondary Metric(s)" |
| 4 | Process Map — detailed | "Process Map – detailed" |
| 5 | FMEA | "FMEA" |
| 6 | X-Y Matrix | "X-Y Matrix" |
| 7 | Basic Statistics on Y | "Basic Statistics on Y" |
| 8 | MSA | "MSA" |
| 9 | Stability graphs | "Stability graphs" |
| 10 | Capability Analysis | "Capability Analysis" |
| 11 | Project Plan | "Project Plan" |
| 12 | Issues and Barriers | "Issues and Barriers" |

**Phase goal**, from *Measure Phase Overview - The Goal* (book p228 / PDF p231):

> - "Define, explore and classify X variables using a variety of tools —
>   Detailed Process Mapping, Fishbone Diagrams, X-Y Matrixes, FMEA."
> - "Acquire a working knowledge of Basic Statistics to use as a communication
>   tool and a basis for inference."
> - "Perform Measurement Capability studies on output variables."
> - "**Evaluate stability of process and estimate starting point Capability.**"

**Note the ordering the eBook enforces:** stability is assessed *before*
capability. The roadmap (book p230 / PDF p233) runs Assess Stability
(Statistical Control) → Assess Capability (Problem with Centering/Spread) →
Estimate Process Sigma Level.

**MSA is a hard gate inside the phase.** The roadmap carries a decision diamond
— "**Repeatable & Reproducible?**" — with an N branch looping to "Implement
Changes to Make System Acceptable" before the phase can proceed.

---

## 2. Recommended tools and techniques

| Tool | eBook location | Purpose |
|---|---|---|
| **Level 2 / Level 3 Process Map (PFM)** | book p106–110 / PDF p109–113 | The detailed "as is" map |
| **SIPOC** | book p104+ / PDF p107+ | Performed between Level 2 and Level 3 mapping |
| **Fishbone / Ishikawa** | book p88, p91+ / PDF p91, p94+ | "Identify All Process X's Causing Problems (Fishbone, Process Map)" |
| **X-Y Matrix** | book p119 / PDF p122 | "Isolate the vital few X's from the trivial many X's" |
| **FMEA** | book p116+ / PDF p119+ | Risk prioritisation via RPN |
| **RPN** | book p119+ / PDF p122+ | Severity × Occurrence × Detection |
| **Basic / descriptive statistics** | book p138+ / PDF p141+ | Mean, median, variance, standard deviation |
| **Box Plots** | book p159+ / PDF p162+ | Distribution and outlier view |
| **Gage R&R (variable)** | book p173+ / PDF p176+ | Repeatability and reproducibility |
| **Attribute Agreement Analysis** | book p201–203 / PDF p204–206 | MSA for attribute data |
| **Process Capability — Cp, Cpk** | book p206+ / PDF p209+ | Short- and long-term capability |
| **Z-score → Cp/Cpk conversion** | book p222 / PDF p225 | Attribute capability route |
| **Control charts (stability)** | book p215+ / PDF p218+ | "Voice of the Process" stability assessment |
| **Operational definitions** | book p112 / PDF p115 | Required before data collection |
| **Sampling** | Measure statistics module | Sample size and strategy |

**X-Y Matrix, purpose and inputs** (book p119 / PDF p122):

> "Breakthrough requires dealing primarily with **controllable X's** impacting the
> Y. Use the controllable X's from the **Fishbone analysis** to include in the X-Y
> Matrix. The goal is to isolate the **vital few X's from the trivial many X's**.
> Procedures and Noise X's will be used in the **FMEA** at the end of this module."

So the eBook's chain is explicit: **Fishbone → classify X's → controllable X's go
to the X-Y Matrix; procedure and noise X's go to the FMEA.**

**Gage R&R output to read** (book p196 / PDF p199) — MINITAB session window:
`%Contribution`, `%Study Var (%SV)`, `%Tolerance (SV/Toler)`, `Number of
Distinct Categories`, and the two-way ANOVA table with Repeatability and
Reproducibility variance components. The worked example shows Total Gage R&R
2.91 %Contribution, 17.05 %Study Var, 8 distinct categories, judged "acceptable."

**Attribute Capability steps** (book p222 / PDF p225): Select Output for
Improvement → Verify Customer Requirements → Validate Specification Limits →
Collect Sample Data → **Calculate DPU** → Find Z-Score → Convert Z-Score to Cp &
Cpk.

---

## 3. Gate checklist criteria

Verbatim from **Measure Questions** (book p231 / PDF p234), grouped as the eBook
groups them.

**Identify Critical X's and potential failure modes (process)**
- Is the *as is* Process Map created?
- Are the decision points identified?
- Where are the data collection points?
- Is there an analysis of the measurement system?
- Where did you get the data?

**Identify Critical X's and potential failure modes (prioritisation)**
- Is there a completed X-Y Matrix?
- Who participated in these activities?
- Is there a completed FMEA?
- **Has the Problem Statement changed?**
- **Have you identified more COPQ?**

**Stability Assessment**
- Is the Voice of the Process stable?
- If not, have the Special Causes been acknowledged?
- Can the good signals be incorporated into the process?
- Can the bad signals be removed from the process?
- How stable can you make the process?

**Capability Assessment**
- **What is the short-term and long-term Capability of the process?**
- What is the problem; one of centering, spread or some combination?

**General Questions**
- Are there any issues or barriers preventing you from completing this phase?
- Do you have adequate resources to complete the project?

**Planning for Action grid** (same page) — a WHAT / WHO / WHEN / WHY / WHY NOT /
HOW matrix the Belt completes across these rows:

> Identify the complexity of the process · Focus on the problem solving process ·
> Define Characteristics of Data · **Validate Financial Benefits** · Balance and
> Focus Resources · Establish potential relationships between variables ·
> Quantify risk of meeting critical needs of Customer, Business and People ·
> Predict the Risk of sustainability · Chart a plan to accomplish the desired
> state of the culture · **What is your defect?** · **When does your defect
> occur?** · **How is your defect measured?** · **What is your project financial
> goal (target & time) to reach it?** · What is your Primary metric? · What are
> your Secondary metrics? · Define the appropriate elements of waste

---

## 4. Templates

| Template | eBook location | Notes |
|---|---|---|
| X-Y Diagram / X-Y Matrix template | book p119 / PDF p122 | "You should have a copy of this template" |
| FMEA form | book p670 / PDF p673 (blank grid) | Columns: Process Function (Step) · Potential Failure Modes · Potential Failure Effects (Y's) · SEV · Class · Potential Causes of Failure (X's) · OCC · Current Process Controls · DET · **RPN** · Recommend Actions · Responsible Person & Target Date · Taken Actions · SEV · OCC · DET · RPN |
| Level 1 PFM worksheet | book p106 / PDF p109 | Named step in the mapping sequence |
| Customer / supplier requirements sheet | book p112 / PDF p115 | Carried from Define; supplier version is "a similar form" |
| `Measure Data Sets.mpj` | book p96, p147 / PDF p99, p150 | MINITAB exercise project |
| `Graphing Data.mtw`, `Surfaceflaws.mtw`, `Camshaft.mtw` | book pp96–220 | MINITAB exercise datasets |

**The FMEA form is re-used in Control** as the Monitoring Plan (book p670 / PDF
p673) — "Provides the means to keep the document current — reassessing RPNs as
the process changes."

---

## 5. Common pitfalls

Verbatim from **Measure Phase - The Roadblocks** (book p229 / PDF p232):

- "Team members do not have the time to collect data."
- "Data presented is the **best guess by functional managers**."
- "**Process participants do not participate in the creation of the X-Y Matrix,
  FMEA and Process Map.**"

**Additional pitfalls implied by the text:**

- **Assessing capability on an unstable process.** The roadmap sequences
  stability before capability; the gate asks "Is the Voice of the Process
  stable?" before the capability questions. A Cpk from an out-of-control process
  is not a capability estimate.
- **Proceeding on an unacceptable measurement system.** The roadmap's
  "Repeatable & Reproducible? N" branch loops back rather than continuing —
  measuring with a bad gauge produces a baseline that is not real.
- **Reporting only one of short-term and long-term capability.** The gate asks
  for both.
- **Not diagnosing centering vs spread.** "What is the problem; one of centering,
  spread or some combination?" — the answer changes what Improve does.
- **Letting the Problem Statement drift silently.** "Has the Problem Statement
  changed?" is an explicit gate question, which implies change is *expected* and
  must be declared.
- **Mapping the ideal rather than the *as is* process** — carried over from
  Define's roadblock list and re-asked here as "Is the *as is* Process Map
  created?"

---

## 6. Cross-phase dependencies

**From Define:**

| Needs | Used for |
|---|---|
| Primary Metric | Becomes the Y under measurement; baseline is established against it |
| Secondary Metrics | Carried into the deliverable list and the Planning for Action grid |
| High-level (Level 1) process map | Base for the Level 2 / Level 3 detailed map |
| Problem Statement | Re-tested — "Has the Problem Statement changed?" |
| COPQ estimate | Re-tested — "Have you identified more COPQ?" |
| Scope | Bounds the Level 2 map — "From your Macro Process Map select the area that represents your problem" (book p110 / PDF p113) |
| Customer requirements / VOC | Feeds "Verify Customer Requirements" and "Validate Specification Limits" in the capability steps |

**Measure's internal sequence** (book p230 / PDF p233): Detailed Problem
Statement Determined → Assess Measurement System → **Repeatable & Reproducible?**
(N → Implement Changes to Make System Acceptable, loop) → Detailed Process
Mapping → Identify All Process X's Causing Problems (Fishbone, Process Map) →
Select the Vital Few X's Causing Problems (X-Y Matrix, FMEA) → Assess Stability →
Assess Capability → Estimate Process Sigma Level → **Review Progress with
Champion** → Ready for Analyze.

**What Measure hands to Analyse:**

| Handed forward | Consumed by |
|---|---|
| Vital few X's (from X-Y Matrix + FMEA) | Analyse — "Vital Few X's Identified" is Analyse's entry condition |
| Baseline capability / sigma level | Analyse — the reference the causal hypothesis links back to |
| Detailed process map | Analyse — root cause exploration |
| FMEA | Analyse — "Is there an updated FMEA?" is an Analyse gate question |
| MSA result | Analyse — validated data is the precondition for hypothesis testing |
| Stability assessment / special causes | Analyse and Control |

**A named checkpoint sits inside the phase:** "Review Progress with Champion"
appears on the roadmap before "Ready for Analyze" — the eBook expects a
mid-phase Champion touchpoint, not only an end-of-phase gate.

---

## 7. Cross-reference against `MeasureOutput`

Schema as ratified in **ARCHITECTURE.md §4.10.2**. (See the version note in
`define_extraction.md` §7 — schemas landed in v2.2.10, not v2.2.9.)

`MeasureOutput` is the **smallest** of the five schemas: 2 Tier 1 + 2 Tier 2 + 4
gate-metadata fields, against **12** named eBook deliverables.

### Covered — eBook deliverable has a field

| eBook deliverable | `MeasureOutput` field | Tier |
|---|---|---|
| Basic Statistics on Y / baseline | `baseline_mean` | 1 |
| Data collection points and plan | `data_collection_plan` | 1 |
| Process Sigma Level | `baseline_sigma` | 2 |
| MSA | `measurement_system_validated` | 2 |
| Gage R&R, Cp/Cpk, DPMO, sample size outputs | `computation_results` (8 computation tools) | — |
| eBook page citations | `citations` | — |
| Belt-uploaded measurement data | `uploads` | — |
| Tier 2 fields the Belt chose to proceed without | `acknowledged_gaps` | — |

### GAPS — eBook deliverable with no corresponding field

| # | eBook deliverable | eBook ref | Severity | Note |
|---|---|---|---|---|
| **M-1** | **Capability Analysis — short-term AND long-term** | book p229, p231 | **HIGH** | `baseline_sigma` holds one value. The gate explicitly asks for **both** short-term and long-term capability, and ARCHITECTURE.md §3.7.2 lists "Short/long-term capability" as covered by `calculate_cpk` into `computation_results`. That works for the *number* but leaves no field asserting the Belt addressed both. |
| **M-2** | **Stability graphs / stability assessment** | book p229, p231 | **HIGH** | A named deliverable and five gate questions. ARCHITECTURE.md §13.2 lists stability as a **Tier 2 rubric criterion with no field** and a strong warning for both belt levels. The eBook treats it as a hard sequencing precondition for capability, not an advisory. **The strongest candidate for promotion to a real field.** |
| **M-3** | **X-Y Matrix** | book p229, p119 | **HIGH** | Named deliverable, explicit gate question ("Is there a completed X-Y Matrix?"), and the mechanism that produces the vital few X's Analyse depends on. Currently **BB-only Tier 2 rubric, no field** (§3.7.2). The eBook does not mark it BB-only. |
| **M-4** | **FMEA** | book p229, p231 | **HIGH** | Same as M-3 — named deliverable, gate question, currently BB-only Tier 2 with no field. Analyse then asks "Is there an **updated** FMEA?", which is unanswerable if the original was never recorded. |
| **M-5** | **Detailed Process Map** | book p229, p231 | **HIGH** | Named deliverable and first gate question. Same artefact-persistence gap as Define's D-2. |
| **M-6** | **Vital few X's** | book p230 | **HIGH** | The roadmap's stated output of Measure and Analyse's stated input. No field in either schema. `root_cause_statement` in Analyse is downstream of this, not the same thing. |
| **M-7** | **Secondary Metric(s)** | book p229 | **HIGH** | Same cross-phase gap as Define D-1. |
| **M-8** | **Special causes acknowledged** | book p231 | **MEDIUM** | "If not, have the Special Causes been acknowledged?" — a conditional deliverable that fires exactly when the process is unstable, i.e. when it matters most. |
| **M-9** | **Centering vs spread diagnosis** | book p231 | **MEDIUM** | "What is the problem; one of centering, spread or some combination?" Directly determines Improve's approach. No field. |
| **M-10** | **Project Plan** | book p229 | **MEDIUM** | Cross-phase gap — see Define D-4. |
| **M-11** | **Issues and Barriers** | book p229 | **MEDIUM** | Cross-phase gap — see Define D-5. |
| **M-12** | **Problem Statement change declaration** | book p231 | **MEDIUM** | "Has the Problem Statement changed?" Our mid-phase contradiction detection (§3.8) catches a *silent* change to an approved value and forces a mini-gate — arguably a **stronger** mechanism than a field. Flagged so review can confirm §3.8 is accepted as the answer. |
| **M-13** | **Additional COPQ identified** | book p231 | **MEDIUM** | "Have you identified more COPQ?" — an increase discovered in Measure has nowhere to go; `business_case` is on `DefineOutput` and already gate-approved. |
| **M-14** | **Operational definitions** | book p112 | **LOW** | Precondition for valid data collection. Could fold into `data_collection_plan`. |
| **M-15** | **Number of Distinct Categories / %Study Var** | book p196 | **LOW** | The specific MSA acceptance numbers. Reachable via `calculate_grr` → `computation_results`. **Probably not a gap** — recorded for completeness. |

### Observations for review

- **Measure has the widest deliverable-to-field gap of the five phases.** Twelve
  named deliverables against four content fields. Define has eight fields for
  nine deliverables; Measure has four for twelve.
- **M-2, M-3 and M-4 are the same decision.** Stability, X-Y Matrix and FMEA are
  all currently Tier 2 *rubric criteria with no field* (§13.2), yet all three are
  named eBook deliverables with dedicated gate questions, and two of them
  (X-Y Matrix, FMEA) produce the input Analyse cannot start without.
- **§3.7.2 marks FMEA and X-Y Matrix Black-Belt-only; the eBook does not.**
  This is a deliberate coaching divergence (heavy methodology for a Green Belt),
  and the reasoning in §3.7.2 is sound — but it means a Green Belt project can
  pass Measure with no documented prioritisation of X's at all. Worth an explicit
  decision on what a GB does *instead*, rather than nothing.
- **M-6 may be the most consequential gap in the whole extraction.** "Vital Few
  X's Identified" is the labelled hand-off between Measure and Analyse on the
  eBook's own roadmap, and neither schema records it.
