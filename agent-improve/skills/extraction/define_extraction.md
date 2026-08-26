# Define Phase — eBook Extraction

**Status:** raw extraction for review. **Not a SKILL.md.** Do not wire into
`DMAICSkillsMiddleware` until reviewed and signed off.

**Source:** `agent-improve/data/knowledge/5_BB_EB_MT_v11.1_PDF2_compressed (1).pdf`
— LSS Black Belt eBook v11.1 MT, © Open Source Six Sigma, LLC. 700 PDF pages.

**Page convention:** `book p78 / PDF p81`. The book's printed numbers run three
behind the PDF's (book p1 = PDF p4). Citations give both because
`improve_knowledge_index.page_number` is populated from the **PDF** index
(ARCHITECTURE.md §7.1.2), while a Belt reading the eBook sees the printed number.

**eBook scope:** Define Phase = book pp1–85 / PDF pp4–88. Modules: Understanding
Six Sigma (p1), Six Sigma Fundamentals (p22), Selecting Projects (p42), Elements
of Waste (p64), Wrap Up and Action Items (p77), Quiz (p83).

---

## 1. Required deliverables

The eBook's own list, verbatim from **Define Action Items** (book p78 / PDF p81).
The Belt presents these to their mentor and Champion at phase close.

| # | Deliverable | eBook wording |
|---|---|---|
| 1 | Charter Benefits Analysis | "Charter Benefits Analysis" |
| 2 | Team Members | "Team Members" |
| 3 | Process Map — high level | "Process Map – high level" |
| 4 | Primary Metric | "Primary Metric" |
| 5 | Secondary Metric(s) | "Secondary Metric(s)" |
| 6 | Lean Opportunities | "Lean Opportunities" |
| 7 | Stakeholder Analysis | "Stakeholder Analysis" |
| 8 | Project Plan | "Project Plan" |
| 9 | Issues and Barriers | "Issues and Barriers" |

**The Project Charter is the container deliverable.** Its components, from
*Project Charter — Definitions* (book p50 / PDF p53):

- **Problem Statement** — "Articulates the pain of the defect or error in the process."
- **Objective Statement** — "States how much of an improvement is desired from the project."
- **Scope** — "Articulates the boundaries of the project."
- **Primary Metric** — "The actual measure of the defect or error in the process."
- **Secondary Metric(s)** — "Measures of potential consequences (+ / -) as a result of changes in the process."
- **Charts** — "Graphical displays of the Primary and Secondary Metrics over a period of time."
- Standard project information: project / Belt / Process Owner names, start and
  desired end date, division or business unit, supporting Master Black Belt
  (mentor), team members.

**Phase goal**, from *Define Phase Overview—The Goal* (book p78 / PDF p81):

> "Identify a process to improve and develop a specific Lean Six Sigma project…
> Define is the **contract phase** of the project. We are determining exactly what
> we intend to work on and estimating the impact to the business. At the
> completion of the Define Phase you should have a **description of the process
> defect that is creating waste for the business**."

**Two rules on metrics** (book p57 / PDF p60):

- "**Only one Primary Metric per project.**" It "serves as the indicator of
  project success" and "links to the KPI or Primary Business measure."
- Secondary metrics "measure positive & negative consequences" and "can have
  multiple."

**The charter is expected to change.** "By the time the Measure Phase is wrapping
up the Project Charter should be in its final form" (book p50 / PDF p53). Define
does not freeze the metric — Measure does.

---

## 2. Recommended tools and techniques

| Tool | eBook location | Purpose |
|---|---|---|
| **Project Charter** | book p50 / PDF p53 | The contract document; expands the Business Case |
| **SIPOC** | book p104+ / PDF p107+ | Supplier-Input-Process-Output-Customer; "especially useful after you have been able to construct either a Level 1 or Level 2 Map" |
| **Level 1 Macro Process Map** | book p106 / PDF p109 | High-level process map — the Define-phase deliverable |
| **Pareto analysis** | book p52+ / PDF p55+ | "Determine Appropriate Project Focus (Pareto, Project Desirability)" |
| **Project Desirability** | book p9, p80 / PDF p12, p83 | Project selection scoring |
| **COPQ estimation** | book p9, p31+ / PDF p12, p34+ | "Estimate COPQ" is an explicit roadmap step |
| **Stakeholder Analysis** | book p10, p78 / PDF p13, p81 | Named Define deliverable |
| **Voice of the Customer (VOC)** | book p112 / PDF p115 | Customer requirements per output |
| **RUMBA** | book p112 / PDF p115 | VOC requirement validity test — see below |
| **Elements of Waste** | book p64+ / PDF p67+ | "Lean Opportunities" deliverable |
| **Value Stream Map** | book p66+ / PDF p69+ | Lean opportunity identification |
| **Financial Evaluation** | book p59 / PDF p62 | Impact / Allocations / Forecast |
| **Time Series Plots** | book p58 / PDF p61 | "Typically utilize Time Series Plots" for metric charts |

**RUMBA — the VOC validity test** (book p112 / PDF p115). A customer requirement
must be **R**easonable, **U**nderstandable, **M**easurable, **B**elievable and
**A**chievable. "If a requirement cannot meet all of these characteristics then
it is not a valid requirement, hence the word negotiation."

**Financial Evaluation components** (book p59 / PDF p62):
- **Impact** — Sustainable vs One-off
- **Allocations** — cost codes / accounting system
- **Forecast** — cash flow, realization schedule

> "A financial representative of the firm should establish guidelines on how
> savings will be calculated… Typically a financial representative is responsible
> for evaluating the financial impact of the project. The Belt works in
> coordination to facilitate the proper information."

---

## 3. Gate checklist criteria

Verbatim from **Define Questions** (book p81 / PDF p84). The eBook's own gate
checklist, organised in two steps plus general questions.

### Step One — Project Selection, Project Definition and Stakeholder Identification

**Project Charter**
- What is the problem statement? Objective?
- Is the business case developed?
- What is the primary metric?
- What are the secondary metrics?
- Why did you choose these?
- What are the benefits?
- Have the benefits been quantified? If not, when will this be done? **Date: ______**
- Who is the customer (internal/external)?
- Has the COPQ been identified?
- **Has the controller's office been involved in these calculations?**
- Who are the members on your team?
- Does anyone require additional training to be fully effective on the team?

**Voice of the Customer (VOC) and SIPOC defined**
- Voice of the customer identified?
- Key issues with stakeholders identified?
- VOC requirements identified?
- Business Case data gathered, verified and displayed?

### Step Two — Process Exploration

**Processes Defined and High Level Process Map**
- Are the critical processes defined and decision points identified?
- Are all the key attributes of the process defined?
- Do you have a high level process map?
- Who was involved in its development?

### General Questions
- Are there any issues/barriers that prevent you from completing this phase?
- Do you have adequate resources to complete the project?
- Have you completed your initial Define report out presentation?

---

## 4. Templates

| Template | eBook location | Notes |
|---|---|---|
| `Define Templates.xls` | book p49 / PDF p52 | The phase's template workbook |
| `Project Charter Template.xls` | book p58 / PDF p61 | Charter + built-in metric graphing |
| Benefits Capture — Calculation Template | book p59 / PDF p62 | Impact / cost codes / forecast grid |
| Customer requirements sheet (VOC) | book p112 / PDF p115 | Process name, operational definition, each output Y, customer name, internal/external, metric, LSL / target / USL |
| SIPOC form | book p104+ / PDF p107+ | Supplier, Input, Process, Output, Customer, plus an optional requirements section |
| X-Y Diagram template | book p119 / PDF p122 | Introduced in Define-phase material, used in Measure |

**The charter template is not mandatory.** "It is acceptable to not use this
template but in any case ensure you are regularly measuring the critical
metrics" (book p58 / PDF p61).

**The customer requirements sheet is where an operational definition is
required:** "a short paragraph which states why the process exists, what it does
and what its value proposition is. Always take sufficient time to write this such
that anyone who reads it will be able to understand the process."

---

## 5. Common pitfalls

Verbatim from **Define Phase — The Roadblocks** (book p79 / PDF p82):

- "No historical data exists to support the project."
- "Team members do not have the time to collect data."
- "Data presented is the **best guess by functional managers**."
- "Data is communicated from poor systems."
- "**The project is scoped too broadly.**"
- "**The team creates the ideal Process Map rather than the *as is* Process Map.**"

**Additional pitfalls implied by the text:**

- **Treating the Business Case as a finished Problem Statement.** "First the
  Business Case will serve as the Problem Statement, as the Belt learns more
  about the process" (book p51 / PDF p54) — it is a starting point, not the
  deliverable.
- **More than one Primary Metric.** Explicitly ruled out (book p57 / PDF p60).
- **Unquantified benefits.** The gate checklist demands a *date* if they are not
  yet quantified — deferral is allowed, silence is not.
- **Skipping the controller's office.** A named gate question, not a nicety.
- **Accepting a VOC requirement that fails RUMBA** instead of negotiating it.

---

## 6. Cross-phase dependencies

**Define is the first phase — it consumes no prior phase output.** Its inputs
come from outside DMAIC, from the Champion / Process Owner swim lane of the
DMAIC Roadmap (book p80 / PDF p83):

| Input | Source |
|---|---|
| Business Case Selected | Champion / Process Owner |
| Notify Belts and Stakeholders | Champion / Process Owner |
| Identify Problem Area | Champion / Process Owner |

**Define's sequence** (book p80 / PDF p83): Create High-Level Process Map →
Determine Appropriate Project Focus (Pareto, Project Desirability) → Define &
Charter Project (Problem Statement, Objective, Primary Metric, Secondary Metric)
→ Estimate COPQ → Recommend Project Focus → **Approved Project Focus?** → if N,
loop back to project focus; if Y, Create Team → Charter Team → **Ready for
Measure**.

**What Define hands to Measure:**

| Handed forward | Consumed by |
|---|---|
| Primary Metric definition | Measure — becomes `baseline_mean` after MSA and capability work |
| Secondary Metrics | Measure — carried through every subsequent phase deliverable list |
| High-level (Level 1) process map | Measure — the base for the Level 2 / Level 3 detailed map |
| Problem Statement | Measure — "Has the Problem Statement changed?" is a Measure gate question |
| COPQ estimate | Measure — "Have you identified more COPQ?" is a Measure gate question |
| Scope | Measure — bounds the detailed process map |
| Team | All phases — "Team Members (Team Meeting Attendance)" recurs in every later deliverable list |

**There is an explicit approval gate before the team is even formed.** The
roadmap loops on "Approved Project Focus? N" back to project focus selection.

---

## 7. Cross-reference against `DefineOutput`

Schema as ratified in **ARCHITECTURE.md §4.10.2** and REFACTORING §82.

> **Version note.** The request cited ARCHITECTURE.md **v2.2.9**; the five
> `{Phase}Output` schemas were actually introduced in **v2.2.10** (commit
> `203cc15`). v2.2.9 had no canonical output schemas to cross-reference. This
> section is checked against v2.2.10, which is the current ratified state.

### Covered — eBook deliverable has a field

| eBook deliverable | `DefineOutput` field | Tier |
|---|---|---|
| Problem Statement | `problem_statement` | 1 |
| Scope | `project_scope` | 1 |
| Objective Statement | `goal_statement` | 1 |
| VOC | `voc_summary` | 1 |
| Business Case / COPQ | `business_case` | 2 |
| Team Members | `team` | 2 |
| Primary Metric (current state) | `baseline_estimate` | 2 |
| Objective target value | `target_value` | 2 |
| Pareto / project desirability output | `computation_results` (via `calculate_expected_savings`) | — |
| VOC + methodology sources | `citations` | — |
| Belt-uploaded data | `uploads` | — |

### GAPS — eBook deliverable with no corresponding field

| # | eBook deliverable | eBook ref | Severity | Note |
|---|---|---|---|---|
| **D-1** | **Secondary Metric(s)** | book p78, p57 | **HIGH** | A named deliverable in **all five** phase deliverable lists. `DefineOutput` has `baseline_estimate` and `target_value` but nothing for secondary metrics. The eBook is explicit that these catch the negative consequences of improving the primary metric — the field that would surface a project that fixed cycle time by wrecking quality. |
| **D-2** | **High-level Process Map** | book p78, p106 | **HIGH** | A named deliverable and a Step Two gate question ("Do you have a high level process map?"). `propose_diagram` can render one, but nothing persists it in the gate document. Handed forward to Measure as the base for the Level 2 map. |
| **D-3** | **Stakeholder Analysis** | book p78, p10 | **MEDIUM** | Named deliverable; gate asks "Key issues with stakeholders identified?" Distinct from `team` — stakeholders are affected parties, not team members. |
| **D-4** | **Project Plan** | book p78 | **MEDIUM** | Named deliverable in all five phases. Improve has `implementation_plan`; Define has no plan field. |
| **D-5** | **Issues and Barriers** | book p78 | **MEDIUM** | Named deliverable in all five phases, and a General gate question in all five. Closest existing mechanism is `acknowledged_gaps`, which records *skipped Tier 2 fields* — not project blockers. Note ARCHITECTURE.md §4.1 deliberately removed `open_items` from `SupervisorState` as derivable; this is different — it is Belt-stated, not derived. |
| **D-6** | **Lean Opportunities** | book p78, p64 | **MEDIUM** | Named deliverable. Elements of Waste / Value Stream analysis output. No field. |
| **D-7** | **Charter Benefits Analysis** — quantified, with a date if deferred | book p78, p81 | **MEDIUM** | `business_case` (Tier 2) partially covers this, but the gate asks specifically "Have the benefits been quantified? If not, when will this be done? **Date:____**" — a deferral date has nowhere to live. |
| **D-8** | **Finance/controller sign-off** | book p81 | **MEDIUM** | "Has the controller's office been involved in these calculations?" is a Define gate question. ARCHITECTURE.md §3.7.2 has three-party sign-off as a **Control** Tier 2 rubric item; the eBook asks for financial involvement at **Define** too. |
| **D-9** | **Metric charts over time** | book p58 | **LOW** | "Displays Primary and Secondary Metrics over time… updated regularly throughout the life of the project." Time-series data, not a scalar. `propose_diagram` renders; nothing persists. |
| **D-10** | **Process operational definition** | book p112 | **LOW** | Required by the VOC sheet — "why the process exists, what it does, what its value proposition is." Could fold into `project_scope`, but is a distinct artefact in the eBook. |
| **D-11** | **Project / Belt / Process Owner / MBB names, dates, business unit** | book p50 | **NONE — covered elsewhere** | Charter's "standard project information." Lives in the case record (`("projects", case_id, "case")`, ARCHITECTURE.md §6.3) and `improve_case_index`. **Not a schema gap** — recorded here so review does not re-flag it. |

### Observations for review

- **D-1, D-4 and D-5 are not Define-specific.** Secondary Metrics, Project Plan
  and Issues and Barriers appear in the deliverable list of **every** phase. If
  they are adopted they belong in all five Output schemas, or on `PhaseState` as
  cross-phase fields — a structural decision, not five independent ones.
- **D-2 and D-9 are both "a diagram the Belt produced."** `propose_diagram`
  returns structured JSON (CLAUDE.md §5.1) but the gate document has no field to
  hold it. This is a general gap in the artefact model, not a Define gap: the
  same issue recurs for Measure's detailed process map and fishbone.
- **Tier placement question.** The eBook's own gate checklist puts VOC, business
  case and COPQ at the same level of obligation as the problem statement. Our
  §3.7.1 makes `business_case` Tier 2. That is a defensible coaching choice
  (§3.7.1's rationale about mechanical field-filling) but it *is* a divergence
  from the source, and reviewers should confirm it is intended.
