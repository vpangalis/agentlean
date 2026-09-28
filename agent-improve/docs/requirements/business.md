# Business requirements — Agent Improve

> **Founder-owned.** Changed only by founder ruling. What the Belt, the team, the Champion and the
> customer need — never how it is built (that is `ARCHITECTURE.md`) and never a technical quality
> (that is `platform.md`). Every feature in the feature list cites one id from this file or from
> `platform.md`; the computed rank (ADR-0058) decides the order of work. Ids are permanent: a
> retired requirement keeps its id and is marked RETIRED; moving a requirement between parts never
> changes its id.
>
> Replaces `define.md`, `workspace.md` and `measure.md`. R8 moves here from `platform.md`;
> R9 moves to `platform.md` as a technical requirement.
>
> Domain source: the founder's LSS Black Belt manual (Open Source Six Sigma, BB eBook v11.1) —
> paraphrased, never copied; page numbers are the founder's (printed folio + 1).

**Status** — RATIFIED (founder ruling, dated) · ACCEPTED (founder accepted in review, final read of
this file pending) · PROPOSED (drafted, awaiting the founder) · DRAFT (recorded, not cited by any feature) · TO WRITE (the section exists, its
content comes from that phase's review).
**Fields on every heading line** — `MoSCoW: Must | Should | Could | Won't-now` (`?` until the
founder ratifies it) and `Design: ADR-nnnn | none` (the decision behind it, `docs/adr/`).
**Scope** — every RATIFIED and ACCEPTED requirement is in scope now (founder, 2026-09-27); there is
no release split. DRAFT and TO WRITE are out of scope until ratified.

## How this file is organised, and how it grows

| Part | Holds | Grows how |
|---|---|---|
| 1 Every phase | Rules that bind all five phases: how the coach behaves, how every phase report looks, what is carried from phase to phase, the audit trail | A rule found in one phase that is true for all moves here |
| 2 The phases | One section per phase, each filled in the **same seven headings** (below) | Each phase is written in its own review — Define is written; Measure is started; Analyse, Improve and Control are TO WRITE |
| 3 The workspace | Screens and interaction common to all phases | New screen behaviour |
| 4 The record | What counts as the official result | — |
| 5 Access and roles | Who may see, change and approve | — |

**The seven headings every phase section fills** — so no phase is written from scratch:

| Heading | Answers |
|---|---|
| a Purpose | What this phase delivers and why the project needs it |
| b Elements | What the coach works through, each with acceptance criteria and manual pages |
| c Coaching specifics | What this phase adds to the Part 1 coaching rules (demos, calculations, data requests) |
| d The phase report | Its sections, which visuals each carries, what each summary explains (applies C1–C2) |
| e The gate | The rubric the report must pass, and who approves |
| f Carried forward | Which approved values the later phases read, and for what (applies C6) |
| g Done when | The measurable finish line for the phase (Define's is R12) |

## Open decisions in this file

| # | Question | Proposal |
|---|---|---|
| 1 | W4 prerequisites: is the proposed set right? | Benefits analysis after business case; objective and scope after problem statement; secondary metrics after primary metric; process performance (R17) after the SIPOC steps; all else free |
| 2 | R8c: may the project lead hand the lead role to another team member? | Yes — the current lead hands over; the handover is recorded (R16) |
| 3 | R10 document formats | Word, PDF and images (images only once the vision read has a test); no Visio |
| 4 | R12 cost ceiling per completed Define | Set after the first measured run-through, at 1.5× the measured cost |
| 5 | M1 open questions | Excel and CSV (the parsers exist); size and first KPIs decided with the Measure review |
| 6 | R17: is the performance data per step right? | Per step: average, minimum and maximum duration with unit, how often it runs per period, the problems the team sees there and who said so; for the whole process: end-to-end lead time and runs per period |

---

# Part 1 — Every phase

**R1 Team copilot** · RATIFIED 2026-09-26 · MoSCoW: Must · Design: ADR-0001
Guide the Belt and team through the method; not a recommendation chat.

**C1 Every phase report is a business document** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0008
The report at each gate reads like a business document that the Belt, the team, a Champion, a
manager or an external reviewer understands without knowing the tool or the method's jargon. It is
laid out in visual sections, each with a heading, a short plain-language summary of what the section
shows and what it means for the project, and the key fields presented with a one-line explanation of
what each field is. The report is built only from confirmed values.

**C2 Show it as a picture where the data allows** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
Wherever a section's information can be shown graphically — a process, a baseline against a target,
a breakdown of costs or causes, a timeline — the report shows it as a labelled diagram or chart with
a sentence explaining how to read it, next to the table or text that carries the same values. A
diagram never carries a value the text does not.

**C3 Every request is explained, with a sample** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0001
Every time the coach asks the Belt or team for new information it explains, in plain words, what is
being asked and why it matters, and shows a sample answer. Once enough of the case is confirmed, the
sample is built from the case's own context so it is relevant; before that it comes from the phase's
worked example. Every sample is clearly marked: *"Sample only — to show the form of a good answer.
Do not copy it; answer for your own process."* A sample is never stored as the Belt's answer.

**C4 Suggested next steps** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
Under each coach reply the screen offers two or three suggested next steps, computed from what is
still missing in the phase (for example "Give the average time of step 3 — Check invoice" or "Work on
the benefits analysis next"). Choosing one starts it; the Belt can always type freely instead. The
suggestions are derived from the phase state in code — they never contradict the element the coach
is working on (W4) and cost no extra model call.

**C5 Runs inside the intranet** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: none
In production Agent Improve is not allowed outside the customer's intranet: it reaches only services
inside it, and nothing on the public internet. Everything the screens need —
layouts, report templates, fonts, diagram drawing — ships with the product. Each phase report has a
predefined template in the repository: its sections, their order, the visuals in each and the
explanatory text around them; the coach fills the template, it never invents the layout. The coach
never offers a link to an external website.

**C6 What is carried from phase to phase** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0019
Every approved value a later phase needs is stored in its structure, not as prose, and is available
to that phase's coach. In particular the as-is process and its performance (R17) captured in Define
are the baseline Measure verifies with data and Improve compares the to-be process against, step by
step, so the coach can reason about the difference.

**R13 Turn time** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0043
Hard limit: no turn exceeds 45 s; a turn that would, answers with what it has and says so.
Goals: 15 s at P50 and 30 s at P95 — measured and reported on every run-through, not blocking
until production launch.

**R14 No dead end** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: none
If an element cannot be completed after three attempts, the coach offers to park it and move on.
A parked element stays open in the progress view and blocks approval only if it is required
(Tier 1). Every turn ends with an action the Belt can take.

**R15 One answer, several elements** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: ADR-0002
When a Belt's answer contains values for other unconfirmed elements, the coach reads them back for
confirmation instead of asking for them again later. Nothing is stored before confirmation.

**R16 Audit trail per element** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0020
Every element value keeps its full history. Each version records the value, when it was created or
changed, who did it, the reason (for a change), and where it came from — typed by the Belt, read
from an upload, or proposed by the coach and confirmed. Nothing is overwritten. The report shows
the current value; the history is viewable per element. "Who" is the signed-in person (R8, R8a).

**R19 The decision trail** · PROPOSED 2026-09-27 · MoSCoW: Should · Design: ADR-0020
Every case keeps a readable trail of how the coach reached each result: for each turn, what the
coach decided to do and why (the element's status and, for a judgment, the criterion it passed or
failed), which sources it used (file and page), the validation verdict per criterion, the skill
version in force, and every change with who made it and why (R16); for each gate, the submission,
the verdict per criterion, and the approval or rejection with who and when. The trail shows the
decisions and their stated reasons, not the model's internal reasoning. It stays inside the
intranet (C5), is never edited, and is kept for the life of the case.

**R20 The coach can't be turned against its rules** · ACCEPTED 2026-09-28 · MoSCoW: Must · Design: ADR-0067
Nothing a team member types and nothing in an uploaded file can change how the coach behaves,
what it stores or how a gate is judged. A message or file that tries is not processed: whoever
sent it is told in plain words why it was blocked and how to phrase it instead, using the element
they are working on and its sample answer. Every block is recorded in the decision trail with who
and when (R19), where the project lead can see it. Ordinary project language is never refused.

---

# Part 2 — The phases

## 2.1 Define

**a Purpose.** Agree what problem the project solves, why it is worth solving, how success is
measured and how the process runs today — so that Measure starts from a shared, approved baseline.

**b Elements**

**R4 Thirteen elements** · RATIFIED 2026-09-26 · MoSCoW: Must · Design: ADR-0004
The current 12 + BENEFITS ANALYSIS (cost of the gap / COPQ, sustainable vs one-off impact,
realisation schedule, finance contact; manual p. 60–63). VOC includes the CTQs (p. 82).
The element list and field names are owned by `backend/phases/define/schema.py` — never restated.

**R7 Acceptance criteria and gate rubric** · RATIFIED 2026-09-26, amended ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0010
From the manual: business case = what, where, when, baseline size, cost, no cause or solution
speculation (p. 49); exactly ONE primary metric, quantified, linked to a KPI (p. 58); secondary
metrics capture side effects (p. 58); scope not too broad, map as-is not ideal (p. 80); team names
champion and process owner, and training needs (p. 82); real data, not best guesses (p. 80).
Metric charts over time belong to Measure (p. 51). *Amendments:* baseline and target are stored as a
number with a unit, and an unparseable value is asked again; the problem statement names the
process step(s) where the problem shows (R18).

**R17 The as-is process with its performance** · ACCEPTED 2026-09-27 · open decision 6 · MoSCoW: Must · Design: none
The high-level process element captures not only the SIPOC and its steps but how the process
performs today. For each step: average, minimum and maximum duration with a unit; how often it runs
per period; and where the team sees the key problems, in the Belt's and team's own words, with who
said it. For the whole process: end-to-end lead time and runs per period. Values may be estimates in
Define, marked as such; Measure replaces them with measured data. All of it is stored in its
structure (C6), not as prose. The element count stays thirteen — this extends the process element.

**R18 The problem is located in the process** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: none
The problem statement and the process map are linked: the problem statement names the step(s) where
the problem shows, and those steps carry the matching problem notes (R17). The coach checks the link
both ways — a problem that points at no step, or a step with problems that the problem statement
ignores, is raised with the Belt before either element is confirmed. The Define skill instructs the
coach to obtain this information actively; it is not left to the Belt to volunteer.

**R10 As-is process document → SIPOC** · DRAFT 2026-09-26 · open decision 3 · MoSCoW: Won't-now · Design: none
As a Belt, I want to upload our as-is process description and have the coach turn it into a SIPOC
draft, so that the high-level process map builds on what we already have.
Acceptance: the coach proposes a SIPOC from the document, checks it for completeness and asks for
missing parts; it recommends adding the performance data of R17; the Belt confirms or edits the
SIPOC before it is stored; the confirmed SIPOC appears in the Define report (R5).

**c Coaching specifics**

**R2 Teach before asking** · RATIFIED 2026-09-26, amended ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0001
For every Define element the coach explains what it is and why it matters, and shows a worked
example of the finished result (C3 applies to every request). *Amendment:* 5W2H keeps its live mind map
(it works today). SIPOC is shown both as a table and as a
process diagram (the steps in order, with suppliers and inputs on one side and outputs and customers
on the other), so the team can confirm the flow visually.

**R3 Validation before the coach** · RATIFIED 2026-09-26, amended ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0007
Every Belt answer passes a validation layer BEFORE it reaches the coach model, checking it is
reasonable against the element's acceptance criteria; insufficient → challenge, naming the failed
criterion. *Amendment:* at most one judgment call per substantive answer, none for any other turn.

**d The phase report**

**R5 The Define report** · RATIFIED 2026-09-26, amended ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0008
The gate is a readable DEFINE REPORT, not a field checklist, built as C1–C2 require:

| Section | Visual (C2) | The summary explains |
|---|---|---|
| 1 Project and team | Team table with roles; lead and Champion named | Who owns the project and who decides |
| 2 Business case and benefits | Cost of the gap and expected benefit, with a realisation timeline | Why the project is worth doing, in money and time |
| 3 Problem, objective, scope | 5W2H mind map; in / out of scope side by side | What exactly is wrong, what success is, what is excluded |
| 4 VOC and CTQs | Table from customer need to CTQ | What the customer requires, in measurable terms |
| 5 Metrics | Baseline → target chart for the primary metric; secondaries listed | How success is measured and how far there is to go |
| 6 High-level process | SIPOC table and process diagram, with step times and frequency (R17) and the problem steps highlighted (R18) | How the process runs today and where it hurts |
| 7 Issues and barriers | List with owner | What could stop the project |

**e The gate**

**R6 Formal acceptance, human in the loop** · RATIFIED 2026-09-26, amended ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0037
The Belt (with the team) reviews the report and approves or rejects it through a graph-level pause.
On rejection the coach guides the Belt back to the element(s) to change. Every change is kept with
its full history (R16). *Amendment:* the report names the project lead and the Champion; until
single sign-on (R8) the approval is recorded against the signed-in project lead, on behalf of the
team. Changes are made through coaching, never by editing fields on the report screen — so every
change passes R3. The rubric is R7.

**f Carried forward.** Metrics with baseline and target (Measure verifies the baseline); the as-is
process and its performance (Measure measures it, Improve compares the to-be against it — C6); the
benefits estimate (Control verifies realised savings against it).

**g Done when**

**R12 Define is done** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: none
A fresh case with a prepared Belt (the scripted run-through persona) reaches an approved Define
report in at most 40 Belt turns, with no turn over 45 s and no element left unreachable.
`scripts/define_runthrough.py` is the acceptance test and records turns, model calls, time and cost.
Cost ceiling: open decision 4.

## 2.2 Measure · started

**M1 Data upload with guidance** · DRAFT 2026-09-26 · open decision 5 · MoSCoW: Won't-now · Design: none
As a Belt, I want the coach to show me, with a sample, how to conduct a measurement and how to shape
my data file, so that it can recognise my data and calculate the KPIs correctly.
Acceptance: before asking for data, the coach shows a demo file and explains each column (name,
unit, meaning); after upload it states what it believes each column means and asks the Belt to
confirm before any calculation; results name the columns they came from.

Headings a–g: TO WRITE in the Measure review. Known inputs: the Define baseline and as-is performance
(C6); the measurement-system-before-baseline and stability-before-capability rules (inventory Q74).

## 2.3 Analyse · TO WRITE
## 2.4 Improve · TO WRITE
Known input: the to-be process is compared with Define's as-is process and performance, step by step
(C6).
## 2.5 Control · TO WRITE
Known input: realised savings are verified against Define's benefits estimate (C6).

---

# Part 3 — The workspace

**W1 Overview page — explain the method** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
As a Belt or team member, I want an overview page that explains what Agent Improve is, the DMAIC
method and each section of the workspace, with a tab per phase describing what the phase is for and
what it must deliver, so that the team understands the journey before starting.
Acceptance: each phase tab shows the phase's purpose and its required deliverables; the text is
read from a "Team overview" section of that phase's skill file, served by the backend — no overview
text is typed in the UI. English only. The texts are changed only by the founder, in the repo; the
app offers no editing.

**W2 Project status — where the project stands** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
As a Belt, I want the overview page to show the project's current phase, the days from case creation
to today, the target date and days remaining, days spent in each phase, and what is open or waiting
for approval, so that the team always knows where it stands.
Acceptance: every figure is computed once, by the backend, from the case record and phase state;
the overview, the navigation, the case list and the progress bar show the same figures from that one
computation. Open elements are counted against the phase's element list.

**W3 Coaching page welcome — summary so far** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
As a Belt, I want the coaching page to greet me by name and summarise what has been achieved so far,
so that I can resume without re-reading history.
Acceptance: the summary is assembled in code, without a model call, from confirmed values in the
phase state only; it lists confirmed elements with their current values and the open elements. It
replaces the browser-built recap, the stubbed welcome banner and the `/context` route, which are
removed.

**W4 Choose what to work on next** · ACCEPTED 2026-09-27 · open decision 1 · MoSCoW: Should · Design: none
As a Belt, I want to either pick any unconfirmed element whose prerequisites are confirmed, or
accept the coach's recommended next element, so that the team can work in the order that suits its
information.
Acceptance: the list shows only unconfirmed elements, and marks those whose prerequisites are open as
not yet available, naming the prerequisite; the recommended element is the one the planner will
actually work on (never a different one — G-107); progress reads "n of N confirmed", not a step
position. Prerequisites are declared per element in the phase skill.
Needs a decision record amending "the coaching move is decided in code": the element becomes a
planner input; the move stays decided in code.

**W5 Uploads strengthen answers** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0030
As a Belt, I want to upload documents on the coaching page, so that the coach can use them to help
me give better, more complete answers.
Acceptance: a file attached in the chat or the files panel appears in the case files panel; the coach
reads it, checks it against the current element's acceptance criteria and asks for what is missing,
naming the file (and page, where it has pages) it read; nothing from an upload is stored until the
Belt confirms it. Uploads on the create form are out of scope until R10 is ratified.

**W6 One case number** · ACCEPTED 2026-09-27 · defect G-113 · MoSCoW: Must · Design: ADR-0024
The case number is assigned only by the server when the case is created. The create form shows no
number before creation ("assigned when the case is created"); after creation, the number returned by
the server is the one shown on the form, in the workspace header, in the case list and in search. The
browser never generates a case number.
Proof: an end-to-end test creates a case through the form and finds the same number in the header,
the list and a search.

**W7 Removing a file** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
Deleting an uploaded file removes it from storage and from the search index; the audit log keeps its
name, digest, date and who removed it.

**W8 Say it is an AI, and what it cannot do** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0055
Every coaching screen carries a standing label: "AI coach — it can be wrong; you confirm every
value." The overview page (W1) states what the coach does and does not do.
Basis: EU AI Act Art. 50 (applies since 2 August 2026); Microsoft HAX guidelines 1–2.

**W9 Correct anything, anytime** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0042
Every confirmed element has a "change" action in the progress view that starts coaching on that
element. The Confirm and Change buttons under a read-back are still there after a reload.
Basis: HAX guidelines 9, 16.

**W10 Failures stay readable** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: ADR-0047
A failed or timed-out turn stays on screen and says what happened, what was saved, and offers a
retry; it shows a reference id the Belt can quote when reporting it.
Basis: HAX guideline 9.

**W11 Nothing typed is lost** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: none
A message typed but not sent survives a reload. Every sent turn and every confirmation survives a
reload or a restart. A Belt returning after weeks finds the case exactly as left.
Basis: HAX guideline 12.

**W12 Show progress while waiting** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
While a turn runs, the screen says what is happening in plain words ("checking your answer against
the criteria", "looking up the method") instead of a generic "thinking" indicator; the reply may
appear as it is written.

**W13 Why, and from where** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
A reply that draws on the manual or an upload shows the file and page it used.
Basis: HAX guideline 11.

**W14 Feedback on a reply** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
Every coach reply offers thumbs up / down and an optional comment; the feedback is stored against
that reply's trace and feeds evaluation.
Basis: HAX guideline 15.

**W15 Team presence** · ACCEPTED 2026-09-27 · MoSCoW: Could · Design: none
Each message shows who wrote it. A second person opening a case while someone is working on it is
told who is working on it.

**W16 Connection status** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
Before the first message the screen shows whether the service is reachable and ready.

**W17 The sign-in window explains itself** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: none
When someone opens a case, the sign-in window says what it is, who may enter, and what to do if they
cannot. It names the project lead. Example wording:

> **Sign in to IMPR-2026-0E5 — "Reduce invoice errors"**
> Only team members added by the project lead can open this project.
> Project lead: **Maria Huber**
> Enter your name as the project lead registered it.
> Not on the team? Ask Maria Huber to add you.

A name that is not on the team is refused with the same guidance, never with a bare error.

**W18 "Why this?" on every reply** · PROPOSED 2026-09-27 · MoSCoW: Should · Design: ADR-0020
Each coach reply has a "Why this?" link. It opens a short panel, in plain words: what the coach
did this turn and why, the criterion it checked and the result, the sources it used, and whether
the grader raised a warning. Read from the decision trail (R19).

**W19 Decision trail tab** · PROPOSED 2026-09-27 · MoSCoW: Should · Design: ADR-0020
A tab shows the case's decision trail as a timeline, filterable by phase, element and person, for
the Belt, the team, the Champion or an auditor. Each gate's entries are grouped under it. It can be
printed like a phase report (R11).

---

# Part 4 — The record

**R11 The record and its print view** · ACCEPTED 2026-09-27 · MoSCoW: Should · Design: ADR-0038
The approved phase output stored by Agent Improve is the record; the system generates no documents.
An approved phase report can be printed from the browser (a print layout of the same screen), headed
with the case number, phase, approval date and "Copy — the record is in Agent Improve". Nothing is
printed before approval. Supersedes the founder ruling "Agent Improve does not export documents"
(archived decisions, AG5) for reports; the two coaching tools it scoped are unaffected.

---

# Part 5 — Access and roles

**R8 Sign-in through single sign-on** · RATIFIED 2026-09-26, amended ACCEPTED 2026-09-27 · MoSCoW: Should · Design: none
The user is identified by the customer's single sign-on — Microsoft Entra ID first, other providers
(OIDC / SAML) when a customer needs them. The user is taken from the identity provider, never typed;
Agent Improve stores no passwords. A case is visible only to its team; roles project lead, team
member, Champion. The project lead adds team members by their company identity (e-mail).

**R8a Access without single sign-on** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: none
Where single sign-on is not available, only the people the project lead registered on the team can
open the case (W17). Entering a registered name is allowed in development and demos only; before any
customer data is used, each team member enters through a personal invite (a link or one-time code
sent to their e-mail).

**R8b The project lead** · ACCEPTED 2026-09-27 · MoSCoW: Must · Design: none
The person who creates a case is its project lead. Only the project lead adds or removes team members
and assigns their roles. The lead is shown on the create form ("You will be the project lead"), in the
workspace header, in the case list and in the sign-in window (W17).

**R8c Handing over the lead** · ACCEPTED 2026-09-27 · open decision 2 · MoSCoW: Should · Design: none
The project lead can hand the role to another team member; the handover is recorded in the audit
trail (R16).

---

## Not yet reviewed

The requirement-like statements in `docs/requirements/inventory.md` §4 (Q01–Q94) are reviewed in a
later round; each lands here, in `platform.md`, or is dropped. Until then no feature cites them.
