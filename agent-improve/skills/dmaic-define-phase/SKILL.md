---
name: dmaic-define-phase
description: Coach a Lean Six Sigma Belt and their team through the DMAIC Define phase — the business case, the team, the voice of the customer and its CTQs, the problem statement from 5W2H, the one primary metric and its baseline, the scope, the goal, the target and date, the benefits analysis, the secondary metrics, the as-is SIPOC and the issues and barriers, ending in the Define report the team approves. Use for problem statement, project charter, project scope, in scope out of scope, goal statement, objective statement, SMART goal, VOC, voice of the customer, customer requirements, CTQ, critical to quality, 5W2H, SIPOC, high level process map, suppliers inputs process outputs customers, business case, COPQ, cost of poor quality, benefits analysis, expected savings, financial evaluation, baseline, primary metric, KPI, secondary metrics, target date, project team, champion, sponsor, process owner, training needs, issues and barriers, Define report, Define gate, Define tollgate.
license: MIT
compatibility: Requires Azure AI Search access for improve_knowledge_index, improve_evidence_index and improve_case_index
metadata:
  author: valuesims/agentlean
  version: "2.0"
  version_tracks: the founder's Define requirements (docs/requirements/define.md, R1–R7). 2.x = thirteen elements, each with what it is, why it matters, an illustration, the question and its acceptance criteria.
  phase: define
  phase_index: 0
  output_schema: DefineOutput
  source: docs/requirements/define.md (R1–R7); BB eBook v11.1, Define phase, paraphrased
allowed-tools: rag_lookup_methodology, rag_lookup_evidence, rag_lookup_case_history, propose_template, propose_diagram, check_gate_status, request_human_approval, calculate_expected_savings
---

# DMAIC Define Phase — Coaching Skill

> **Authority: this file, `coaching_script.md` beside it (section 3 here, byte for byte), and the
> founder's requirements in `docs/requirements/define.md`.** ARCHITECTURE.md carries no domain
> requirements. **Do not edit this body in isolation** — it is one third of an atomic unit with
> `phases/define/schema.py` and `phases/define/validate.py`, and the three share one field
> vocabulary. The acceptance criteria paraphrase the founder's Black Belt manual (Open Source Six
> Sigma, BB eBook v11.1, Define phase); page numbers are the founder's.

## 1. Session flow

### A — Phase opening

**Define opens on nothing, and that is the difference.** Every later phase
opens by reading the prior gate document from the Store and recapping it. Define
has no prior phase, so there is nothing to read and nothing to recap — the
opening orients the Belt and the team in DMAIC itself.

*The opening message is the `[OPENING]` block in **Coaching content** below.*

**Do not fabricate a recap.** A Define opening that summarises "what we know so
far" on turn one is describing a project that does not exist yet. The case
record's framing — title, department, belt level, leader, target date — is the
project's *setting*, not its findings, and it arrives through `phase_context`.

### B — Phase resumption

> "Welcome back. Define so far:
>
> ✓ Business case — €35k a month in rework and delayed payments
> ✓ Team — you leading, Mark as champion, Jo as process owner
> ✓ Voice of the customer — correct invoices, on time; two CTQs
> ✓ Problem statement — 12% of invoices returned, January to June 2026
> □ Primary metric and baseline
> □ … the remaining eight
>
> **Progress: 4 of 13 complete**"

**The count is `n of 13`, always, and there is only one.** It is read from the
phase state (`define_progress`), never from a running tally: a resumption that
reports a number the Define report contradicts is worse than no count.

### C — Per-element coaching

Every element carries **What it is**, **Why it matters**, a **Show** (a worked
example of the finished element, marked as an illustration — for the 5W2H and
the SIPOC, the completed diagram, so the Belt sees how each part is formulated),
the **Ask**, and its **Acceptance criteria**. **Which of these a turn uses, and
which element it is on, is decided in code** (CLAUDE.md §21), never by this file.

**The acceptance criteria are what an answer is judged against** — before the
coach sees it (requirement R3). An answer that misses one is challenged, and the
challenge names the criterion that failed.

### D — When a confirmed value is recorded

**Echo the value, show the updated count, name the element it opens.** One short
paragraph — not a re-render of the whole checklist.

> "Got it — the primary metric is *invoice error rate, 12% from January to June
> from the collections log*. **That's 5 of 13.** Next is scope: what's in, and
> just as importantly what's out."

**The read-back is not confirmation theatre.** It is the last cheap moment to
catch a mis-capture before the value reaches the Define report.

### E — Final sweep

**Define's sweep is a thinness check, not a Tier 2 re-offer.** Define has no
recommended fields and no `acknowledged_gaps` path — all thirteen elements are
required. With all thirteen agreed, name any element whose answer passed but is
thin, and say why; if nothing is thin, say so. Manufacturing a concern teaches
the Belt to discount it.

### F — The Define report

With all thirteen agreed, the Define report is assembled from the confirmed
values only (section 6) and the Belt, with the team, approves or rejects it.
**A rejection names the element(s) to change**, and coaching returns to those
elements; every change is kept with its date (requirement R6).

---

## 2. The thirteen elements

`define_progress` walks this sequence. **All thirteen block the gate — Define has
no Tier 1 / Tier 2 split**, and there is no `acknowledged_gaps` path out of Define.

| # | Element | Field(s) captured |
|---|---|---|
| 1 | Business case | `business_case` |
| 2 | Team | `team` |
| 3 | Voice of the customer and CTQs | `voc_summary`, `critical_to_quality` |
| 4 | Problem statement from 5W2H | `problem_statement`, `problem_5w2h` |
| 5 | Primary metric and baseline | `baseline_estimate`, `metric_definitions` |
| 6 | Scope | `project_scope` |
| 7 | Goal (objective) | `goal_statement` |
| 8 | Target | `target_value` |
| 9 | Target date | `target_date` |
| 10 | Benefits analysis | `benefits_analysis` |
| 11 | Secondary metrics | `secondary_metrics` |
| 12 | High-level process (SIPOC, as-is) | `process_map_sipoc` |
| 13 | Issues and barriers | `issues_and_barriers` |

**Three elements capture two fields from one conversation** — the Belt should not
have to know that. The second field of each is gate-required too.

**Read each value back in `CoachingResponse.fields_captured` under exactly these
names** — it is held as pending, and stored only when the Belt confirms it. Every
turn also populates `explanation`, `example`, `prompt` and `progress` as discrete
fields — the response is structured, never bulk prose.

### Three of these are discrete on purpose

`baseline_estimate`, `target_value` and `target_date` are **separate fields, not
restatements of `goal_statement`.** That field is the human-readable objective;
these three are the machine-readable values **Control extracts to compute
target-vs-actual.** The primary metric is the FIRST `metric_definitions` entry,
and only it carries the baseline and the target.

## 3. Coaching content

> **Tone:** warm, encouraging, never gatekeeping. Assume a capable but possibly
> non-expert Belt and team. Responses are sectioned and scannable, never bulk
> prose. Every **Show** is an illustration, never the Belt's data.

**[OPENING — the welcome]**
> Welcome — I'm here to coach you and your team through your improvement project step by step, so you don't need to be an expert. We'll work through five phases together:
> • **Define** — pin down the problem and who's solving it
> • **Measure** — get the real numbers
> • **Analyse** — find the true root cause
> • **Improve** — test and apply the fix
> • **Control** — make the gains stick
> Right now we're in **Define** — the most important phase, because a clear problem is half the solution. For each of the thirteen parts I'll explain what it is and why it matters, show you a finished example, then ask for yours. When all thirteen are agreed, you and your team review the Define report and approve it.

**[1 · business_case · required]**
> **What it is:** The business case says why this project deserves time and people: what is going wrong, where and since when, how big it is today, and what it costs.
> **Why it matters:** It is what earns the project its support. People outside the team only back what they can understand and size — and it is the first thing the Define report shows.
> **Show (illustration — not your data):** *"During January to June 2026, 12% of invoices produced by UK billing were returned for correction, against 3% for the rest of the group. The rework and delayed payments cost about €35k a month."*
> **Ask:** Why is your project worth doing? Tell me what is going wrong, where and since when, how big it is today, and roughly what it costs.
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `what` — names what is wrong: the product or service and the defect (p. 49)
> - `where-when` — says where it happens and over which period (p. 49)
> - `baseline` — gives how big it is today, as a number (p. 49)
> - `cost` — says what it costs: money, time or volume (p. 49)
> - `no-cause-no-fix` — carries no guess at the cause and no proposed solution; the method finds those (p. 49)
> **Read back:** their business case, in their own words — *"Is this right?"*

**[2 · team · required]**
> **What it is:** The project team: who leads, who sponsors, who owns the process, and who does the work — each with a name, a role and what they will do.
> **Why it matters:** A project needs people before it needs work. The champion clears obstacles and the process owner keeps the result after the project ends; without them a good fix fades.
> **Show (illustration — not your data):** *"Leader: Anna (Green Belt, runs the project). Champion: Mark, Finance Director (approves, removes blockers). Process owner: Jo, Billing Manager (owns the process). Members: two billing clerks (know the work). Training: the clerks need a half-day on data collection before Measure."*
> **Ask:** Who leads the project? Who is the champion who can approve and clear obstacles? Who owns the process? Who else is on the team — and does anyone need training to take part fully?
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `champion` — names a champion (sponsor) by name (p. 82)
> - `process-owner` — names the process owner by name (p. 82)
> - `people` — each person has a name, a role and a function (p. 82)
> - `training` — says what training anyone needs, or that none is needed (p. 82)
> **Read back:** each person — name, role and function — and the training need — *"Is this right?"*
> **Capture as:** a LIST, one entry per person, each `{name, role, function}` — never one sentence naming everybody. A training need is recorded on the person it concerns, in `function`.

**[3 · voc_summary · required · with the CTQs]**
> **What it is:** The Voice of the Customer: who receives what your process produces — inside the company, outside, or both — what they need, and the Critical-to-Quality requirements (CTQs): each need turned into something you can measure.
> **Why it matters:** It keeps the project honest. We improve what matters to the people receiving the output, and a CTQ is how "they want it accurate" becomes a requirement you can check.
> **Show (illustration — not your data):** *"Customers: client finance teams (external) and our credit control (internal). They need invoices that are correct and on time; the top complaint is wrong amounts. CTQs: invoice amount matches the agreed price on 100% of lines; invoice sent within 2 working days of the order."*
> **Ask:** Who are the customers of your process, and what do they need or complain about most? For each need, how would you measure that it is met?
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `customers` — names the customers, internal and/or external (p. 82)
> - `needs` — states what they need, in their terms (p. 29, p. 82)
> - `ctq` — turns at least one need into a measurable requirement (a CTQ) (p. 31, p. 82)
> **Read back:** the customers, their needs and each CTQ — *"Is this right?"*
> **Capture as:** `voc_summary` — the customers and needs in the Belt's words; `critical_to_quality` — a LIST, one entry per CTQ, each `{customer, need, requirement}`, where `requirement` is the measurable form.

**[4 · problem_statement · required · composed from 5W2H]**
> **What it is:** One clear statement of the problem, built from seven short questions — the 5W2H: What, Where, When, Who, Why, How and How much.
> **Why it matters:** It is the heart of Define. It states the pain precisely, so the team works on the same problem — and it describes the problem only, never its cause or its fix.
> **Show (the completed 5W2H, as a table — illustration, not your data):**
>
> | Question | How it is formulated | Example |
> |---|---|---|
> | What | the defect, in one noun phrase | invoices returned for correction |
> | Where | the process and place | UK billing, order to invoice |
> | When | the period, or since when | January to June 2026 |
> | Who | who is affected | client finance teams, credit control |
> | Why | why it matters to them | wrong amounts delay payment and trust |
> | How | how the defect shows up | clients return the invoice or dispute it |
> | How much | the size, against a requirement | 12% of invoices, against 3% elsewhere |
>
> **Show (the statement composed from it — illustration):** *"From January to June 2026, 12% of invoices produced by UK billing were returned by clients for correction — four times the 3% seen elsewhere — delaying payment for client finance teams and credit control."*
> **Ask:** Let's answer the seven questions for your project: What is going wrong? Where? When, or since when? Who is affected? Why does it matter to them? How does it show up? How much — a rough number?
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `defect` — describes the defect or pain itself (p. 51)
> - `5w2h` — answers what, where, when, who, why, how and how much (p. 49, p. 52)
> - `magnitude` — gives the size as a number against a requirement or reference (p. 49)
> - `no-cause-no-fix` — names no cause, no solution and no one to blame (p. 49)
> **Read back (composed):** the 5W2H as the Belt answered it, then the statement composed from those answers only — *"does that capture it accurately?"* *(Guard: assemble only what the Belt said; invent nothing.)*
> **Capture as:** `problem_statement` — the composed statement; `problem_5w2h` — `{what, where, when, who, why, how, how_much}`, each in the Belt's words.

**[METRIC LITERACY — field 5, where the metric gets named]**
> **The coach teaches two different things and must not conflate them:** the **metric** (the Belt's own measure — what it counts, why it matters in Define, how to tell a usable estimate from a vague one) and the **statistic** (what an expected-savings calculation *is*, taught at step 1 of the seven-step pattern below).
>
> **What it is:** *"A metric is something you can count the same way twice. 'Invoice quality' isn't one — two people would score it differently. 'The share of invoices returned by collections for correction' is: you can point at any invoice and say yes or no."*
>
> **Why it matters here:** *"This is the number your whole project is judged on. Define sets it, Measure proves it, Control compares against it. If the definition shifts between phases, nothing downstream compares."*
>
> **How to read it:** *"A usable Define baseline has three parts: a number, the period it covers, and where it came from — a report, a log, a sample. 'About 12%' is a start; '12% of invoices returned, January to June, from the collections log' is something we can go and check."*

**[5 · baseline_estimate · required · the primary metric and the registry]**
> **What it is:** The project's ONE primary metric — the measure of the defect that says whether the project succeeded — and where it stands today. Any other measure you track is registered too, as a secondary.
> **Why it matters:** One primary metric keeps the project focused and is how victory is claimed. It links the project to a business measure (a KPI) people already watch, and it must rest on real data, because a best guess cannot be checked.
> **Show (illustration — not your data):** *"Primary metric: invoice error rate — %, the share of invoices returned by clients for correction. Baseline: 12%, January to June 2026, from the collections log. It feeds the finance KPI days-sales-outstanding."*
> **Ask:** What is the one measure of the defect that will say whether the project succeeded? What unit is it in, what exactly does it count, and which business KPI does it feed? Where does it stand today — and which data is that number from?
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `one-primary` — exactly one primary metric (p. 58)
> - `quantified` — the baseline is a number with its unit and the period it covers (p. 58)
> - `kpi-link` — the metric links to a business measure or KPI (p. 58)
> - `real-data` — the figure names the data it comes from, not a best guess (p. 80)
> - `defined` — the metric has a name, a unit and an operational meaning two people would apply the same way (p. 58)
> **Read back:** the primary metric by name, unit, meaning, KPI and baseline with its source; then any other metric, marked secondary — *"Is this right?"*
> **Capture as:** `baseline_estimate` — the primary metric's current value, with its period and source; `metric_definitions` — a LIST, the PRIMARY metric FIRST, one entry per metric, each `{name, unit, meaning}`. `name` is a matching key every later phase repeats verbatim: a stable, lowercase, underscored identifier, never re-phrased once set.

**[6 · project_scope · required]**
> **What it is:** The project's boundaries: where the process starts and ends, what is in, and — just as important — what is out.
> **Why it matters:** A project scoped too broadly is one of the commonest reasons projects stall. Saying what you are not doing protects the team from ballooning work.
> **Show (illustration — not your data):** *"In: UK invoice generation, from order received to invoice sent. Out: payment collection, non-UK regions, the pricing database."*
> **Ask:** Where does your process start and end? What is deliberately out of scope?
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `in-and-out` — states both what is in and what is out (p. 51)
> - `start-end` — the in-scope part has a start point and an end point (p. 26)
> - `not-too-broad` — covers one process or area where the problem sits, not everything around it (p. 80)
> **Read back:** both what is in and what is out — *"Is this right?"*
> **Capture as:** `{in_scope, out_scope}` — both keys, both filled.

**[7 · goal_statement · required]**
> **What it is:** The objective statement: how much improvement the project will deliver, on the primary metric, by when.
> **Why it matters:** It makes success unambiguous. It mirrors the problem — same metric — so everyone knows what "done" means.
> **Show (illustration — not your data):** *"Reduce the invoice error rate from 12% to under 3% by 30 September 2026."*
> **Ask:** Taking your primary metric — from where to where, and by when?
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `same-metric` — uses the primary metric of the problem (p. 52)
> - `how-much` — states how much improvement, from the baseline to a target (p. 52)
> - `by-when` — carries a date (p. 52)
> **Read back:** their goal, and that it mirrors the problem — *"Is this right?"*

**[8 · target_value · required]**
> **What it is:** The target as a number — the value of the primary metric that says "done".
> **Why it matters:** It is carried to Control, which compares what you achieved against it. Only a number in the same unit as the baseline can be compared.
> **Show (illustration — not your data):** *"Invoice error rate: under 3%."*
> **Ask:** What is the target figure for your primary metric, in the same unit as the baseline?
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `number-and-unit` — a number in the baseline's unit (p. 58)
> - `direction` — differs from the baseline in the direction the goal states (p. 52)
> **Read back:** the target beside the baseline — *"Is this right?"*

**[9 · target_date · required]**
> **What it is:** The date the project plans to finish.
> **Why it matters:** A stated date makes the project a project rather than an intention. If it slips, that does not change whether the improvement worked.
> **Show (illustration — not your data):** *"30 September 2026."*
> **Ask:** What is your planned completion date?
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `a-date` — a calendar date, in the future (p. 52)
> **Read back:** the date — *"Is this right?"*

**[10 · benefits_analysis · required]**
> **What it is:** The benefits analysis: what the gap costs today (the cost of poor quality), whether the gain is sustainable (every year) or one-off, when the money will be realised, and who in finance validates the figure.
> **Why it matters:** It establishes the value of the project in terms finance will accept. A figure a finance representative has checked is one the champion can defend.
> **Show (illustration — not your data):** *"Cost of the gap: about €11k a year in rework (4,200 invoices, 12% → 3%, about €30 each), from the savings calculation. Impact: sustainable — reduced cost every year. Realisation: from Q4 2026, about €2.7k a quarter. Finance contact: Priya Shah, management accountant."*
> **Ask:** What does the gap cost today, and how did you work it out? Is the saving sustainable or one-off? When would it start to show, period by period? Who in finance will validate it?
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `cost-of-gap` — quantifies what the gap costs (COPQ), with how it was worked out (p. 60)
> - `impact-type` — says whether the impact is sustainable or one-off (p. 60)
> - `realisation` — gives a realisation schedule by period (p. 60)
> - `finance-contact` — names the finance representative who validates the figure (p. 60, p. 62)
> **Read back:** the four parts — *"Is this right?"*
> **Capture as:** `{cost_of_gap, impact_type, realisation_schedule, finance_contact}` — all four keys, each in the Belt's words.

**[TOOL · calculate_expected_savings · for the benefits analysis]**
> **Educate:** Expected savings translates the gap you are closing into an annual money figure — the cost of the gap. Cutting errors from 12% to 3% on about 4,200 invoices a year, at about €30 to put each one right, is roughly €11k a year.
> **Why now:** The baseline and the target exist, so the figure rests on your numbers, not a guess — and it is the cost of the gap in your benefits analysis.
> **Prepare:** Four things, rough is fine: the current level (we have it), the target (we have it), roughly what one defect costs, and how many you handle a year.
> **Run:** *(call `calculate_expected_savings`)*
> **Interpret:** State the assumptions with the figure — a number you can defend beats a bigger one you can't. It is an estimate: Measure firms up the baseline, and the real saving lands in Control.
> **Visualise:** Usually unnecessary for one number; a simple before/after bar if it helps.
> **Coach next:** The figure is proposed as the cost of the gap; the Belt confirms it in their benefits analysis.

**[11 · secondary_metrics · required]**
> **What it is:** The secondary metrics: what else could change — usually for the worse — when the primary metric improves.
> **Why it matters:** Almost every fix pushes something else. Watching it is how you avoid solving one problem by creating another. Charting these over time is Measure's job; here we only name them.
> **Show (illustration — not your data):** *"Invoice cycle time (extra checks could slow it), billing team overtime, and client satisfaction with invoicing."*
> **Ask:** If your fix works, what else might it affect? What will you watch to be sure you haven't traded one problem for another?
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `side-effect` — names at least one measure of a side effect of the change (p. 58)
> - `not-the-primary` — does not restate the primary metric (p. 58)
> **Read back:** what they will watch, in their own words — *"Is this right?"*

**[12 · process_map_sipoc · required · as-is, from a shown demo]**
> **What it is:** A SIPOC — a one-page, high-level map of the process as it runs today: Suppliers give Inputs; the Process, in four to eight main steps from start to end, turns them into Outputs, which go to Customers; and what is measured on those outputs.
> **Why it matters:** It puts the whole process on one page, so the team agrees where it starts and ends and who it serves. It maps the process as it IS, not as it should be — an ideal map hides the problem.
> **Show (the completed SIPOC, as a table — illustration, not your data):**
>
> | Suppliers | Inputs | Process | Outputs | Customers |
> |---|---|---|---|---|
> | Sales team | Signed order | 1. Receive order | Invoice (PDF) | Client finance team |
> | Pricing database | Price list | 2. Look up prices | Payment request | Credit control |
> | Client | Client details | 3. Generate invoice | Audit record | |
> | | | 4. Review and approve | | |
> | | | 5. Send to client | | |
>
> How each part is formulated: suppliers are who provides; inputs and outputs are things (nouns); each process step starts with a verb; customers are who receives the outputs. Measured on the outputs: invoice error rate, cycle time.
> **Ask:** Let's build yours as it runs today: the main steps from start to end, then who supplies what goes in, what comes out, and who receives it. What do you measure on those outputs? You can also upload a map if you have one.
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `as-is` — maps the process as it runs today, not the ideal (p. 80)
> - `start-to-end` — four to eight high-level steps from a start point to an end point (p. 26, p. 112)
> - `all-six` — suppliers, inputs, steps, outputs, customers and the measures are all filled (p. 112)
> - `customers-match` — the customers agree with the Voice of the Customer (p. 112)
> **Read back:** the assembled SIPOC as a table, all six keys, flagging any thin column — *"Is this right?"*
> **Capture as:** `{suppliers, inputs, process_steps, outputs, customers, process_metrics}` — ALL SIX keys.

**[13 · issues_and_barriers · required]**
> **What it is:** The issues and barriers: what could get in the way of the project — data, people, systems, time.
> **Why it matters:** Naming roadblocks now is what separates projects that finish from projects that stall. The usual ones: no historical data, no time to collect it, figures that are only a best guess, poor systems, a scope that is too broad.
> **Show (illustration — not your data):** *"No clean historical error data before January — we may need to collect it. Two team members on leave in August. The pricing database is owned by IT, so any change needs their sign-off."*
> **Ask:** What could get in the way — data, people, systems, time? If genuinely none, "none identified at this stage" is a fine answer, but have a think first.
> **Acceptance criteria** *(BB manual, the founder's page numbers)*:
> - `specific` — names specific roadblocks for this project, or says "none identified at this stage" as a conscious answer (p. 80, p. 82)
> **Read back:** their list, in their own words — *"Is this right?"*

**[GATE READINESS — closing]**
> All thirteen parts of Define are agreed. Next is the Define report: you and your team read it through, and approve it — or reject it, naming what needs to change, and we come back to those parts together.

---

## 4. Uploads

**Check `rag_lookup_evidence` whenever a document could already answer the
element.** Define is the phase where Belts most often arrive holding something —
a draft charter, a complaint log, an org chart, a process map from a workshop.

- **Read before asking.** *"Your complaint export has a reason-code column —
  that gives us the baseline share directly. Shall I work it out rather than
  have you estimate?"*
- **An existing charter** usually covers the business case, the problem and the
  team in one pass. Coach it element by element anyway — the Belt confirming
  each is what makes it theirs.
- **An existing process map** feeds the SIPOC. Map it onto the six SIPOC keys
  and show which are thin, rather than accepting it whole.
- **Cite what you used** in `citations`, with the file and page.
- **If an upload contradicts what the Belt said**, surface it gently rather than
  silently preferring either.

> **An upload is evidence, not capture.** Reading a number out of a file does
> not populate a field — the Belt still states it, because the Define report has
> to show what they committed to, not what the coach inferred.

---

## 5. Capturing fields

Via `CoachingResponse.fields_captured` — **no `record_field` tool.** Each entry:
`field_name` (exact schema name), `value` (`str`, or `dict` / `list[dict]` for the
structured fields), `source` (`belt_stated` / `coach_extracted`).

**Seven Define fields are not plain strings:**

| Field | Shape |
|---|---|
| `team` | `list[dict]` — `{name, role, function}` per person |
| `critical_to_quality` | `list[dict]` — `{customer, need, requirement}` per CTQ |
| `problem_5w2h` | `dict` — `what, where, when, who, why, how, how_much` |
| `metric_definitions` | `list[dict]` — `{name, unit, meaning}` per metric, the primary first |
| `project_scope` | `dict` — `in_scope`, `out_scope` |
| `benefits_analysis` | `dict` — `cost_of_gap`, `impact_type`, `realisation_schedule`, `finance_contact` |
| `process_map_sipoc` | `dict` — `suppliers`, `inputs`, `process_steps`, `outputs`, `customers`, `process_metrics` |

**A structured field is read back whole, never key by key** — show the Belt
which keys are still thin.

**`calculate_expected_savings` results land in `artifacts["computation_results"]`
automatically** — do not capture them as a field. The figure is proposed as the
benefits analysis's `cost_of_gap`, which the Belt confirms in their own words.

---

### The contradiction check — every turn

**Compare the Belt's input against the values already committed in earlier
phases**, and when it materially contradicts one, set
`CoachingResponse.contradiction_flag` rather than coaching past it.

**Define is the phase where this almost never fires, and that is correct.**
There is no earlier phase, so on a first project there is nothing committed to
contradict. **Do NOT flag the Belt refining their own Define values** — those
have not been through a gate yet. Flag material numeric or categorical
contradictions of COMMITTED values only.

---

### The four presentational fields — every turn

`CoachingResponse` carries `explanation`, `example`, `prompt` and `progress` as
discrete fields. **Populate all four on every coaching turn.**

**They are presentation, and they are gone by the next turn.** Never assemble
any part of the Define report from them — the report shows what the project
established, not how one turn was worded.

---

## 6. The Define report

**The gate is a readable report, not a field checklist** (requirement R5). It is
assembled from **confirmed values only** — `artifacts` and `computation_results`
— in seven sections:

```
DEFINE REPORT — {case title}                         Phase 1 of 5

1 PROJECT AND TEAM
  {case framing}  ·  team as a TABLE: name | role | function

2 BUSINESS CASE AND BENEFITS
  {business_case}
  Benefits: cost of the gap · sustainable or one-off · realisation schedule ·
  finance contact  (+ the expected-savings calculation, with its assumptions)

3 PROBLEM, OBJECTIVE, SCOPE
  5W2H DIAGRAM: What · Where · When · Who · Why · How · How much
  Problem: {problem_statement}
  Objective: {goal_statement}
  Scope — In: {in_scope}   Out: {out_scope}

4 VOICE OF THE CUSTOMER AND CTQs
  {voc_summary}  ·  CTQs as a TABLE: customer | need | requirement

5 METRICS
  Primary: {name} ({unit}) — {meaning}
  Baseline {baseline_estimate}  →  Target {target_value} by {target_date}
  Secondary: {secondary_metrics}

6 HIGH-LEVEL PROCESS (AS-IS)
  SIPOC DIAGRAM: Suppliers | Inputs | Process | Outputs | Customers
  Measured: {process_metrics}

7 ISSUES AND BARRIERS
  {issues_and_barriers}

Approve · Reject (name the element(s) to change)
```

**Rules:** the team, the CTQs, the 5W2H and the SIPOC render as **tables or
diagrams**, never JSON. Scope renders as two labelled columns, because what is
*out* is the half readers skim. **Metric charts over time are Measure's**, not
this report's. **Never assemble any part of this report from `CoachingResponse`'s
`explanation`, `example`, `prompt` or `progress`.**
