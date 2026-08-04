# Control Phase — eBook Extraction

**Status:** raw extraction for review. **Not a SKILL.md.** Do not wire into
`DMAICSkillsMiddleware` until reviewed and signed off.

**Source:** `agent-improve/data/knowledge/5_BB_EB_MT_v11.1_PDF2_compressed (1).pdf`
— LSS Black Belt eBook v11.1 MT, © Open Source Six Sigma, LLC.

**Page convention:** `book pN / PDF pN+3`.

**eBook scope:** Control Phase = book pp561–683 / PDF pp564–686. Modules: Welcome
to Control (p561), Advanced Experiments (p564), Advanced Capability (p574), Lean
Controls (p588), Defect Controls (p603), Statistical Process Control (p615), Six
Sigma Control Plans (p655), Wrap Up and Action Items (p675), Quiz (p681).

> **Governance-doc cross-check.** ARCHITECTURE.md §13.5 and REFACTORING §42 cite
> "eBook p681" for verified financial impact. Book p681 / PDF p684 is the Control
> **Quiz** cover page; the financial-impact material is at book pp677–679 / PDF
> pp680–682, in the Control wrap-up. The citation points at the right *phase and
> section* but the page number is off by a few. Worth correcting when these
> extractions are reviewed.

---

## 1. Required deliverables

Control's wrap-up does **not** present a bulleted "Deliverables" list in the
format the other four phases use. Its deliverables are the **five Control Plan
elements** plus the roadmap steps.

**The five elements of a Control Plan** (book p664 / PDF p667):

> "The **5 elements** of a Control Plan include the **documentation, monitoring,
> response, training and aligning systems and structures**."

| # | Element | eBook detail |
|---|---|---|
| 1 | **Documentation Plan** | Updated process maps/flowcharts, SOPs, FMEA; training manuals; monitoring plan; response plan; job descriptions |
| 2 | **Monitoring Plan** | FMEA-based; check lists/matrices; visual management; SPC charts |
| 3 | **Response Plan** | What to do when monitoring shows degradation; FMEA-driven |
| 4 | **Training Plan** | Who, by whom, when, and what triggers ongoing training |
| 5 | **Aligning Systems & Structures** | Job descriptions, performance management objectives |

Plus, on the same diagram: **Verified Financial Impact**, and —

> "**Process owners are accountable to maintain new level of process
> performance.**"

**Phase goal**, from *Control Phase Overview—The Goal* (book p676 / PDF p679):

> - "Assess the **final Process Capability**."
> - "Revisit Lean with an eye for **sustaining** the project."
> - "Evaluate methods for **Defect Prevention**."
> - "Explore various methods to **monitor process using SPC**."
> - "**Implement a Control Plan.**"

**Organisational change expectations**, same page — including one that maps
directly onto our yokoten tooling:

> "Accept responsibility · Monitoring · Responding · Managing · Embracing change &
> continuous learning · Sharing best practices · **Potential for horizontal
> replication or expansion of results**"

**The Control Plan draws on everything before it** (book p664 / PDF p667):

> "The team develops the Control Plan by utilizing all available information
> from: Results from the Measure and Analyze Phases · Lessons learned from
> similar products and processes · Team's knowledge of the process · Design FMEAs
> · Design reviews · Defect Prevention Methods selected"

---

## 2. Recommended tools and techniques

| Tool | eBook location | Purpose |
|---|---|---|
| **Advanced Capability** | book p574+ / PDF p577+ | Final capability assessment |
| **Lean Controls** | book p588+ / PDF p591+ | Vision of Lean, Lean Tool Highlights, Project Sustained Success |
| **5S** | book p65+, p73+ / PDF p68+, p76+ | "5S is necessary for Visual Management" |
| **Kaizen** | book p598+ / PDF p601+ | Continuous improvement events |
| **Kanban** | book p599+ / PDF p602+ | Pull signalling |
| **Standard Work** | book p597 / PDF p600 | Process standardisation |
| **Defect Controls** | book p603+ / PDF p606+ | Tolerances, Process Automation, Poka-Yoke |
| **Poka-Yoke / Mistake Proofing** | book p604+, p609+ / PDF p607+, p612+ | Eliminate or rigidly define human intervention |
| **Realistic Tolerance / Six Sigma Design** | book p604 / PDF p607 | Tolerance setting |
| **Process Automation or Interruption** | book p604 / PDF p607 | Defect prevention by design |
| **SPC** | book p615+ / PDF p618+ | Ongoing monitoring |
| **Xbar & R / Xbar & S charts** | book p631 / PDF p634 | Variable data, subgroups |
| **Individuals & Moving Range (I-MR)** | book p631 / PDF p634 | Low volume, costly sampling; "Used for SPC on most **inputs**" |
| **Pre-Control** | book p631 / PDF p634 | "Set-up is critical, or cost of setup scrap is high. Use for **outputs**" |
| **EWMA** | book p631 / PDF p634 | Small shifts, autocorrelated output |
| **CUSUM** | book p631 / PDF p634 | As EWMA, where past data matters as much as present |
| **P / C / U / NP charts** | book p578+ / PDF p581+ | Attribute data — "The P Chart is the most common type" |
| **FMEA (as Monitoring Plan)** | book p670 / PDF p673 | Re-scored RPNs as the process changes |
| **Visual Management** | book p670 / PDF p673 | Red/yellow/green signals, empty-bin triggers, audible alerts |
| **Check lists / matrices** | book p670 / PDF p673 | Key items, decision criteria, decision road map |

**Control chart selection rules** (book p631 / PDF p634), verbatim:

| Chart | When you need it |
|---|---|
| **Xbar & R or Xbar & S** | "Production is higher volume; allows process Mean and variability to be viewed and assessed together; more sampling than with Individuals Chart (I) and Moving Range Charts (MR) but when subgroups are desired. Outliers can cause issues with Range (R) charts so Standard Deviation charts (S) used instead if concerned." |
| **Individuals & Moving Range** | "Production is low volume or cycle time to build product is long or homogeneous sample represents entire product (batch etc.); sampling and testing is costly so subgroups are not desired. Control limits are wider than Xbar Charts. **Used for SPC on most inputs.**" |
| **Pre-Control** | "Set-up is critical, or cost of setup scrap is high. **Use for outputs.**" |
| **EWMA** | "Small shift needs to be detected often because of autocorrelation of the output results. Used only for individuals or averages of Outputs. Infrequently used because of calculation complexity." |
| **CUSUM** | "Same reasons as EWMA except the past data is as important as present data." |

**Solution selection at Control** (book p656, p658 / PDF p659, p661) — the eBook
expects a final selection pass among defect-reduction options, scored on:

- **Cost:** initial (training, materials, resources, capital) and on-going
  (future training, inspection, monitoring, material)
- **Time:** technical (minimum build/implement time), political (competing
  priorities), cultural (time to gain stakeholder support)

---

## 3. Gate checklist criteria

Verbatim from **Control Questions** (book p678 / PDF p681), in the eBook's four
steps.

**Step One: Process Enhancement And Control Results**
- **How do the results of the improvement(s) match the requirements of the
  business case and improvement goals?**
- What are the vital few X's?
- How will you control or redesign these X's?
- Is there a process Control Plan in place?
- **Has the Control Plan been handed off to the process owner?**

**Step Two: Capability Analysis for X and Y — Process Capability**
- How are you monitoring the Y's?

**Step Three: Standardization And Continuous Improvement**
- How are you going to ensure this problem does not return?
- **Is the learning transferable across the business?**
- **What is the action plan for spreading the best practice?**
- Is there a project documentation file?
- How is this referenced in process procedures and product drawings?
- What is the mechanism to ensure this is not reinvented in the future?

**Step Four: Document what you have learned**
- Is there an updated FMEA?
- Is the Control Plan fully documented and implemented?
- **What are the financial implications?**
- Are there any spin-off projects?
- **What lessons have you learned?**

**General Questions**
- Are there any issues/barriers preventing the completion of the project?
- **Do the Champion, the Belt and Finance all agree this project is complete?**

**Planning for Action grid** (book p679 / PDF p682) — the longest of the five:

> Test validation plan for a specific time · **Calculate benefits for
> breakthrough** · Implement change across project team · Process map of improved
> process · **Finalize Key Input Variables (KPIV) to meet goal** · Prioritize
> risks of output failure · **Control plan for output** · **Control plan for
> inputs** · Chart a plan to accomplish the desired state of the culture ·
> **Mistake proofing plan for inputs or outputs** · Implementation plan for
> effective procedures · **Knowledge transfer between Belt, PO and team members**
> · **Knowledge sharing between businesses and divisions** · Lean project control
> plan · Establish continuous or attribute metrics for Cpk · **Identify actual
> versus apparent Cpk** · Finalize problem solving strategy · **Complete RPN
> assessment with revised frequency and controls** · **Show improvement in RPN
> through action items** · **Repeat same process for secondary metrics**

---

## 4. Templates

| Template | eBook location | Notes |
|---|---|---|
| **Control Plan** (5 elements) | book p664+ / PDF p667+ | Documentation · Monitoring · Response · Training · Aligning Systems & Structures |
| **FMEA form** (as Monitoring Plan) | book p670 / PDF p673 | Full column set incl. revised SEV/OCC/DET/RPN after actions |
| Training Plan structure | book p665 / PDF p668 | Who requires training · who delivers · when · what triggers ongoing training |
| Documentation Plan structure | book p667 / PDF p670 | Process docs (maps, SOPs, FMEA) + control plan docs + responsibility assignment |
| Control Phase Checklist | book p678 / PDF p681 | The four-step question set |
| Planning for Action grid | book p679 / PDF p682 | 20-row WHAT/WHO/WHEN/WHY/WHY NOT/HOW matrix |
| Control chart selection table | book p631 / PDF p634 | Variable and attribute chart decision guide |
| `pchart.mtw`, `c-u Chart.mtw`, `Overfill.mtw`, `Cycletime_bankers.mtw` | book pp578–582 / PDF pp581–585 | SPC exercises |
| `Ascent.mtw`, `Paycheck2.mtw`, `Holediameter.mtw` | book p571, p644, p648 | Capability and SPC exercises |

**Documentation Plan responsibility split** (book p667 / PDF p670) — the Belt's
obligations at hand-off are explicit:

- Belt ensures all documents are current at hand off
- Belt ensures there is a process to modify documentation as the process changes
- Belt ensures there is a process to review documentation on a regular basis
- The plan must name who maintains and who reviews documentation **ongoing**

---

## 5. Common pitfalls

Verbatim from **Control Phase—The Roadblocks** (book p677 / PDF p680). **Note
this list is entirely different from the other four phases** — it is about
organisational sustainment, not data collection:

- "**Lack of project sign off**"
- "**Team members are not involved in Control Plan design**"
- "**Management does not have knowledge on monitoring and reacting needs**"
- "**Financial benefits are not tracked and integrated into business**"
- "**Lack of buy in of process operators or staff**"

**Additional pitfalls implied by the text:**

- **Handing off a Control Plan the owner has not accepted.** "Has the Control
  Plan been handed off to the process owner?" and "Process owners are accountable
  to maintain new level of process performance."
- **Documentation that goes stale.** The Documentation Plan must name who updates
  and who reviews, ongoing — not just who wrote it.
- **Confusing actual and apparent Cpk.** "Identify actual versus apparent Cpk" is
  a Planning for Action row.
- **Wrong control chart for the data.** The selection table exists because I-MR,
  Xbar-R, P and EWMA are not interchangeable; I-MR is for most *inputs*,
  Pre-Control for *outputs*.
- **Not closing the RPN loop.** "Complete RPN assessment with revised frequency
  and controls" and "Show improvement in RPN through action items" — the FMEA
  must demonstrate risk *reduction*, not merely be updated.
- **Forgetting secondary metrics at close.** "Repeat same process for secondary
  metrics."
- **Declaring completion without three-party agreement.** "Do the Champion, the
  Belt and Finance all agree this project is complete?"
- **Losing the learning.** Four separate Step Three questions guard against the
  improvement being reinvented later.

---

## 6. Cross-phase dependencies

**From Improve:**

| Needs | Used for |
|---|---|
| Implemented / validated new process | The thing being sustained |
| Optimal levels of vital X's | "Finalize Key Input Variables (KPIV) to meet goal" |
| Mathematical model | Monitoring thresholds |
| Experiment results | Evidence base |
| Expected financial benefits | Compared against verified actuals |

**From all earlier phases** (book p664 / PDF p667) — the Control Plan explicitly
consumes "Results from the Measure and Analyze Phases," Design FMEAs, design
reviews, and the defect-prevention methods selected.

| Needs | From | Used for |
|---|---|---|
| Business case and improvement goals | Define | "How do the results of the improvement(s) match the requirements of the business case and improvement goals?" |
| Baseline capability / sigma | Measure | The comparison for final capability |
| FMEA | Measure → Analyse | Becomes the Monitoring Plan; RPNs re-scored |
| Vital few X's | Measure → Analyse | "What are the vital few X's? How will you control or redesign these X's?" |
| Secondary metrics | Define onward | "Repeat same process for secondary metrics" |
| Process maps | Define → Measure | "Process map of improved process" |

**Control's internal sequence** (book p678 / PDF p681):

```
Improvement Selected
  → Develop Training Plan       → Implement Training Plan
  → Develop Documentation Plan  → Implement Documentation Plan
  → Develop Monitoring Plan     → Implement Monitoring Plan
  → Develop Response Plan       → Implement Response Plan
  → Develop Plan to Align Systems and Structures → Align Systems and Structures
  → Verify Financial Impact
  → Go to Next Project
```

**Every one of the five plans is develop-then-implement.** A written plan is half
a deliverable in this phase.

**What Control hands forward** — not to a next phase, but to the organisation:

| Handed forward | To |
|---|---|
| Control Plan | Process owner (accountable for maintaining performance) |
| Verified financial impact | Finance / Champion |
| Lessons learned | The next project |
| Transferable learning / best practice action plan | Other businesses and divisions (yokoten) |
| Spin-off projects | The project pipeline |

---

## 7. Cross-reference against `ControlOutput`

Schema as ratified in **ARCHITECTURE.md §4.10.2**. (Version note: see
`define_extraction.md` §7.)

`ControlOutput` is the **largest** of the five schemas — 2 Tier 1 + 6 Tier 2 + 4
gate-metadata fields — and has the best coverage of eBook content.

### Covered — eBook deliverable has a field

| eBook deliverable | `ControlOutput` field | Tier |
|---|---|---|
| Control Plan | `control_plan` | 1 |
| Final capability / post-improvement measure, linked to baseline | `post_improvement_metric` (dict, cross-phase ref) | 1 |
| Improvement vs baseline | `improvement_delta` | 2 |
| Financial implications | `financial_impact_verified` | 2 |
| "How are you going to ensure this problem does not return?" | `sustainability_check` | 2 |
| Hand-off to process owner | `handover_documented` | 2 |
| "What lessons have you learned?" | `lessons_learned` | 2 |
| "Is the learning transferable across the business?" | `transferability` | 2 |
| Control chart limits, post-improvement Cpk | `computation_results` (4 computation tools) | — |
| Methodology sources | `citations` | — |
| Belt-uploaded control data | `uploads` | — |
| Tier 2 fields the Belt chose to proceed without | `acknowledged_gaps` | — |

**This is the strongest alignment of the five phases.** `lessons_learned` and
`transferability` (added per Finding 12) map directly onto the eBook's Step Three
and Step Four questions and onto its "horizontal replication" language.

### GAPS — eBook deliverable with no corresponding field

| # | eBook deliverable | eBook ref | Severity | Note |
|---|---|---|---|---|
| **C-1** | **The Control Plan's five elements, separately** | book p664 | **HIGH** | `control_plan` is one `str`. The eBook defines the Control Plan as **five distinct plans** — Documentation, Monitoring, Response, Training, Aligning Systems & Structures — each with its own content and its own develop-then-implement step. A single string cannot show that four of five were done and one was skipped, which is exactly what the roadmap's ten steps are designed to surface. **The single most consequential gap in this phase.** |
| **C-2** | **Develop vs Implement, per plan** | book p678 | **HIGH** | Ten roadmap steps, five develop / five implement. A written-but-unimplemented Training Plan is a common real failure and is invisible to the schema. |
| **C-3** | **Three-party sign-off** | book p678 | **HIGH** | "Do the Champion, the Belt and Finance all agree this project is complete?" — a General gate question, i.e. asked of every Belt. §3.7.2 has it as Tier 2, "full for BB, simplified for GB", **with no field**. `handover_documented` covers the process owner only, not Champion and Finance. |
| **C-4** | **Updated FMEA with RPN improvement demonstrated** | book p678, p679 | **HIGH** | Three separate asks: "Is there an updated FMEA?", "Complete RPN assessment with revised frequency and controls", "**Show improvement in RPN through action items**". The last is a *quantitative before/after* claim with no field. Completes the unrecorded FMEA chain (Measure M-4, Analyse A-4). |
| **C-5** | **Monitoring method for the Y's** | book p678 | **MEDIUM** | "How are you monitoring the Y's?" — which chart, what frequency, what limits. Chart limits reach `computation_results`; the monitoring design does not. Arguably inside `control_plan`, but see C-1. |
| **C-6** | **Vital few X's and how they will be controlled** | book p678 | **HIGH** | "What are the vital few X's? How will you control or redesign these X's?" Terminal instance of the unrecorded vital-few-X's chain (Measure M-6, Analyse A-9) — three phases ask, none record. |
| **C-7** | **Action plan for spreading best practice** | book p678 | **MEDIUM** | `transferability` records *whether* it transfers; the eBook separately asks for the **action plan** for spreading it. Feeds `rag_lookup_case_history` / yokoten. |
| **C-8** | **Project documentation file / procedure references** | book p678 | **MEDIUM** | "Is there a project documentation file?", "How is this referenced in process procedures and product drawings?", "What is the mechanism to ensure this is not reinvented in the future?" — three questions about durable documentation location. |
| **C-9** | **Spin-off projects** | book p678 | **MEDIUM** | "Are there any spin-off projects?" A named gate question and a real pipeline input. No field. |
| **C-10** | **Match to business case and improvement goals** | book p678 | **MEDIUM** | Step One's **first** question. `post_improvement_metric` links to Measure's baseline (§4.7); this asks for the link to **Define's** business case and goal statement. A second cross-phase reference — to `DefineOutput.goal_statement` / `business_case` — would close it with existing machinery. |
| **C-11** | **Actual vs apparent Cpk** | book p679 | **MEDIUM** | "Identify actual versus apparent Cpk." A specific analytical distinction with no field; `post_improvement_cpk` produces a number but not the comparison. |
| **C-12** | **Secondary metrics repeated at close** | book p679 | **HIGH** | "Repeat same process for secondary metrics." Terminal instance of the cross-phase secondary-metrics gap (Define D-1). A project that improved the primary metric and degraded a secondary one closes clean under our schema. |
| **C-13** | **Cost and time considerations for solution selection** | book p658 | **MEDIUM** | Initial vs on-going cost; technical, political and cultural time constraints. No field. |
| **C-14** | **Issues and Barriers** | book p678 | **MEDIUM** | Cross-phase gap — see Define D-5. |
| **C-15** | **Mistake proofing / poka-yoke plan** | book p679 | **MEDIUM** | "Mistake proofing plan for inputs or outputs" — a Planning for Action row and a whole eBook module (Defect Controls, 13 pages). Arguably inside `control_plan`; see C-1. |

### Observations for review

- **C-1 is the phase's structural gap.** Four of the fifteen gaps here (C-2, C-5,
  C-15, and part of C-8) dissolve if `control_plan` becomes structured — either
  five sub-fields or a dict with a develop/implement status per element. This is
  the single highest-value change identified in the whole extraction.
- **C-6 and C-12 close chains that run the full length of DMAIC.** Vital few X's
  are requested in Measure, Analyse and Control; secondary metrics in all five.
  Neither is recorded anywhere. These are not Control gaps — Control is just
  where the consequence lands.
- **C-3 raises a belt-level question.** §3.7.2 treats three-party sign-off as
  BB-full / GB-simplified. The eBook asks it as a **General** question of every
  Belt, and its Roadblocks list leads with "Lack of project sign off." Worth
  confirming that a simplified GB version still requires *some* recorded
  agreement rather than none.
- **Control's roadblocks are organisational, not analytical**, and unlike the
  other four phases they share almost nothing with the earlier lists. A coach
  that carries Measure-style "lack of data" prompting into Control will be
  coaching the wrong risks.
- **The `improve_case_index` connection is explicit in the source.**
  "Potential for horizontal replication or expansion of results" and "Knowledge
  sharing between businesses and divisions" are the eBook's own words for what
  `rag_lookup_case_history` exists to serve — good confirmation that the yokoten
  tooling is methodologically grounded, not an invention.
