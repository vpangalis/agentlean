# Feature inputs — for Desktop's review

Snapshot of `docs/define_features.json` on 2026-09-28 (founder, housekeeping item 6): every feature's
rank inputs and board placement as Claude Code proposed them in brief Parts F3, F7 and F8. Nothing
here is ratified; the feature list stays the only source — a change is made there, never here.

Scales (ADR-0058): belt_impact dead_end / wrong_data / data_loss = 3 (Belt-blocking), degraded = 1,
none = 0 · rework_risk high = 2 (it changes state, persistence, the gate or a schema), low = 0 ·
effort S = 1, M = 2, L = 3. Stage: where in the Belt's journey; layer: screen, api, coaching, gate,
persistence, platform.

| Feature | Lane | Requirement | belt_impact | rework_risk | effort | stage | layer | depends_on | Description |
|---|---|---|---|---|---|---|---|---|---|
| DEF-001 | integrator | R1 | degraded | low | M | open_case | api | — | A Belt creates a new case and it opens in Define: POST /cases returns an id, the case list shows it, and GE… |
| DEF-002 | integrator | R1 | degraded | low | M | coached | api | DEF-001 | One Belt message to POST /ask runs the compiled graph once and returns a coached reply inside the 45 s wall… |
| DEF-003 | integrator | R1 | degraded | high | M | coached | persistence | DEF-002 | Every node of a Define turn leaves a checkpoint, so a crash loses at most one node's work. |
| DEF-004 | integrator | R1 | none | low | S | coached | platform | DEF-002 | Tracing is a switch: with tracing off, a Define run sends zero LangSmith runs. (The traced half — a traced … |
| DEF-005 | A | R2 | dead_end | low | M | coached | coaching | DEF-002 | On a field not yet taught, the coach TEACHES: an explanation, a worked example shown before the question, a… |
| DEF-006 | A | R1 | degraded | low | S | coached | coaching | DEF-005 | Every coaching turn tells the Belt where they are — 'Define · Step n of 13' — computed by define_progress, … |
| DEF-007 | A | R3 | degraded | low | M | coached | coaching | DEF-005 | A sufficient answer is READ BACK in the Belt's own words with 'is this right?', and held pending — nothing … |
| DEF-008 | A | R6 | degraded | high | M | coached | coaching | DEF-007 | Clicking Confirm under a read-back stores the pending value in the Belt's words and advances to the next fi… |
| DEF-009 | A | R3 | degraded | low | M | coached | coaching | DEF-007 | A typed plain yes confirms like the button; a yes carrying 'but/actually/change…' is treated as a correctio… |
| DEF-010 | A | R6 | degraded | low | M | coached | coaching | DEF-007 | Clicking Change under a read-back asks what to change and shows the Belt's current words; the field returns… |
| DEF-011 | A | R3 | degraded | low | M | coached | coaching | DEF-005 | A weak answer is CHALLENGED — the coach says what is missing and never writes the Belt's answer for them; t… |
| DEF-012 | A | R1 | degraded | low | M | coached | coaching | DEF-005 | A Belt message that is not an answer ('where do we stand?') is answered, the field is asked again, and its … |
| DEF-013 | A | R1 | degraded | low | M | coached | coaching | DEF-005 | The coherence judge rules on the Belt's words, not the coach's: a reply that quotes the script is not degra… |
| DEF-014 | A | R1 | degraded | low | M | coached | coaching | DEF-013 | When coherence rejects a reply, the coach is asked again inside the turn (a new model call), within the lat… |
| DEF-015 | A | R1 | degraded | low | M | coached | coaching | DEF-002 | Every coaching turn is graded by the coaching rubric, the grader sees all four blocks (not only 'message'),… |
| DEF-016 | A | R4 | degraded | low | M | coached | coaching | DEF-034 | The savings calculation is TAUGHT before its number is given, and '23%', '23' and '0.23' give the same savi… |
| DEF-017 | A | R4 | degraded | high | M | coached | coaching | DEF-016 | A calculation the coach ran is recorded in computation_results with its five keys and appears in the gate d… |
| DEF-018 | A | R2 | degraded | low | M | coached | coaching | DEF-030 | When the Belt's metric first comes up, the coach explains what it means, why Define cares and how to read i… |
| DEF-019 | A | R2 | degraded | low | S | coached | coaching | DEF-005 | The coach teaches in its own voice and never hands the Belt a URL. |
| DEF-020 | A | R1 | degraded | low | M | coached | coaching | DEF-041 | At any point the Belt can ask what is done and what is missing, and the coach shows the captured and missin… |
| DEF-021 | A | R6 | degraded | high | M | coached | persistence | DEF-039 | When the Belt corrects a stored value, their stated reason is kept with the change in field_log.reason. |
| DEF-022 | A | R6 | degraded | high | M | coached | persistence | DEF-008 | A Belt can revise a field they already confirmed while a later field is current, and the revision is judged… |
| DEF-023 | A | R2 | none | low | S | coached | coaching | DEF-005 | The coach does not fetch the Define script it already has in its system message (no load_skill call on a De… |
| DEF-024 | A | R3 | degraded | low | L | coached | coaching | DEF-005, DEF-007, DEF-011 | The same coaching situation run five times makes the same move every time (repeated-run consistency). Measu… |
| DEF-025 | A | R4 | degraded | low | S | coached | coaching | DEF-008 | Field 1 of 13 — The business case is captured verbatim in the Belt's words after Confirm. |
| DEF-026 | A | R4 | degraded | high | M | coached | coaching | DEF-025 | Field 2 of 13 — The team is captured as a list of people each with name, role and function — never as prose. |
| DEF-027 | A | R4 | degraded | low | S | coached | coaching | DEF-026 | Field 3 of 13 — The voice-of-the-customer summary is captured after Confirm. |
| DEF-028 | A | R4 | degraded | high | M | coached | coaching | DEF-027 | Field 4 of 13 — The problem statement is composed from the Belt's 5W2H answers, read back, and stored only … |
| DEF-029 | A | R4 | degraded | high | M | coached | coaching | DEF-028 | Field 5 of 13 — Position 5 captures the baseline AND the metric registry in one exchange; the baseline is s… |
| DEF-030 | A | R4 | degraded | low | M | coached | coaching | DEF-029 | Field 6 of 13 — The scope is captured with both halves explicit — what is in and what is out. |
| DEF-031 | A | R4 | degraded | low | S | coached | coaching | DEF-030 | Field 7 of 13 — The SMART goal sentence is captured after Confirm. |
| DEF-032 | A | R4 | degraded | high | M | coached | coaching | DEF-031 | Field 8 of 13 — The target is stored as a number with the same unit as the baseline, parseable by Control. |
| DEF-033 | A | R4 | degraded | low | S | coached | coaching | DEF-032 | Field 9 of 13 — The planned completion date is captured as an ISO date. |
| DEF-034 | A | R4 | degraded | low | S | coached | coaching | DEF-033 | Field 11 of 13 — The secondary metrics (what could get worse) are captured after Confirm. |
| DEF-035 | A | R4 | degraded | high | M | coached | coaching | DEF-034 | Field 12 of 13 — The SIPOC is built column by column after a filled example and captured with all six keys;… |
| DEF-036 | A | R4 | degraded | low | S | coached | coaching | DEF-035 | Field 13 of 13 — Issues and barriers are captured last; 'none identified at this stage' is accepted as a co… |
| DEF-037 | A | R6 | degraded | high | M | coached | persistence | DEF-025, DEF-026 | A confirmed value survives every later turn — the business case is still there when the SIPOC is captured. |
| DEF-038 | A | R6 | degraded | high | M | coached | persistence | DEF-026, DEF-030, DEF-035 | Captured values keep their declared type end to end: team, scope, SIPOC and the registry are stored structu… |
| DEF-039 | A | R6 | degraded | high | M | coached | persistence | DEF-037 | Every change to a stored value is kept in field_log, dated, with the prior value readable. |
| DEF-040 | B | R6 | wrong_data | high | L | coached | gate | DEF-047 | When the Belt contradicts a value an earlier gate approved, the turn stops in a node that writes nothing, t… |
| DEF-041 | B | R5 | degraded | high | M | report | gate | DEF-036 | Once all thirteen elements are confirmed, GET /gate/review returns the complete Define gate document (Defin… |
| DEF-042 | B | R5 | degraded | high | M | report | gate | DEF-041, DEF-029, DEF-032 | The gate document's phase_metrics entry mirrors the confirmed baseline and target, derived at assembly with… |
| DEF-043 | B | R5 | degraded | high | M | report | gate | DEF-041 | Layer 2b refuses a gate submission missing any of the sixteen gate-required fields and names what is missin… |
| DEF-044 | B | R7 | degraded | high | M | report | gate | DEF-043 | At the gate, constraints (2c) and the Define rubric (2d) grade the document and can send it back to coachin… |
| DEF-045 | B | R7 | degraded | high | S | report | gate | DEF-044 | Define's gate has no Tier 2: it never issues a 'warning' verdict and acknowledged_gaps is always empty. |
| DEF-046 | B | R7 | degraded | high | M | report | gate | DEF-044 | After three failed gate attempts the case is escalated to a person instead of looping. |
| DEF-047 | B | R6 | degraded | high | M | approve | gate | DEF-043 | Submitting the Define gate PAUSES the run at gate_review (graph-level interrupt) once it has passed validat… |
| DEF-048 | B | R6 | degraded | high | M | approve | gate | DEF-047 | A case paused at the gate survives a server restart and resumes where it stopped. |
| DEF-049 | B | R6 | degraded | high | M | approve | gate | DEF-047 | The Belt approves the reviewed Define report (POST /gate/decision, decision=approve); the approval reaches … |
| DEF-050 | B | R6 | degraded | high | M | approve | gate | DEF-047 | The Belt can reject the Define report naming the element(s) to change and a mandatory reason; those element… |
| DEF-051 | B | R6 | degraded | high | M | approve | gate | DEF-047 | At the paused gate the Belt may edit a field; a non-blocking policy advisory checks the edit, and the edite… |
| DEF-052 | C | R2 | degraded | low | M | coached | screen | DEF-005 | The workspace shows the coach's four blocks — explanation, example, prompt, and progress — plus the grader'… |
| DEF-053 | C | R1 | degraded | low | S | coached | screen | DEF-006 | The progress bar reads 'n of 13' from define_progress and moves turn by turn; the suggested next step alway… |
| DEF-054 | C | R6 | degraded | low | M | coached | screen | DEF-008, DEF-010 | Under a read-back the screen shows Confirm and Change; a click sends action=confirm/change on /ask and the … |
| DEF-055 | C | R1 | degraded | low | S | coached | screen | DEF-002 | A failed turn tells the Belt what happened in words, stays on screen, and never renders an error as an empt… |
| DEF-056 | C | R1 | degraded | low | M | coached | api | DEF-001 | The Belt can upload evidence to a Define case; the file lands, is indexed once, and carries an interpretati… |
| DEF-057 | C | R1 | degraded | low | M | coached | coaching | DEF-056 | The coach can read a document the Belt uploaded and quote a line from it (e.g. from an uploaded process map). |
| DEF-058 | C | R5 | degraded | low | M | report | screen | DEF-049 | The gate screen shows the live gate document (one progress bar for Define), and the approve/reject controls… |
| DEF-059 | C | R1 | degraded | low | M | coached | screen | DEF-002 | The coach's reply appears as it is written (server-sent events), and a dropped client abandons the turn. |
| DEF-060 | B | T23 | data_loss | high | L | record_written | persistence | DEF-049 | On approval the Define record is written once: the store (projects/{case}/artifacts/define.json), PhaseStat… |
| DEF-061 | B | R6 | degraded | high | M | record_written | persistence | DEF-060 | The gate write keeps the Belt's change log, citations and uploads. |
| DEF-062 | B | R6 | degraded | high | M | next_phase | gate | DEF-060 | After approval the case advances to Measure, and Measure starts from the approved Define record without Pri… |
| DEF-063 | integrator | R1 | degraded | low | L | approve | api | DEF-036, DEF-041, DEF-047, DEF-049 | A scripted Belt goes through all thirteen elements on a fresh case — good, weak and corrected answers, Conf… |
| DEF-064 | integrator | R1 | degraded | low | L | next_phase | api | DEF-063, DEF-056, DEF-060, DEF-062 | Define end to end: on ONE fresh case carrying an upload, every Define capability row's own check is green a… |
| DEF-065 | A | R2 | degraded | low | M | coached | coaching | — | For every Define element the coach's script explains what it is and why it matters, shows a worked example … |
| DEF-066 | A | R3 | degraded | low | M | coached | coaching | DEF-065 | Every Belt answer is judged against the element's acceptance criteria BEFORE the coach model is called; an … |
| DEF-067 | A | R4 | degraded | low | M | coached | coaching | DEF-065 | Define has thirteen elements: the benefits analysis (cost of the gap, sustainable or one-off, realisation s… |
| DEF-068 | B | R5 | degraded | high | M | report | gate | DEF-067 | The Define gate is a seven-section report assembled from confirmed values only: a value appears in it after… |
| DEF-069 | C | R5 | degraded | low | M | report | screen | DEF-068 | The gate screen draws the Define report: the seven sections, the 5W2H and SIPOC diagrams, one primary metri… |
| DEF-070 | A | R6 | degraded | high | M | coached | persistence | — | Per element, phase state keeps the first confirmed value and the current value, each with its date; the his… |
| DEF-071 | C | R6 | degraded | low | M | approve | screen | DEF-069 | Under a paused Define report the screen offers Approve, or Reject naming the elements and a reason; before … |
| DEF-072 | B | R7 | degraded | high | M | report | gate | DEF-068 | At the gate the Define rubric grades the report, one criterion per element from the manual, pass or fail wi… |
| DEF-074 | C | W6 | wrong_data | low | S | open_case | screen | — | G-113: the create form shows no case id until the server has assigned one; the number a Belt sees is always… |
| DEF-075 | A | R14 | dead_end | low | M | coached | coaching | DEF-011 | No dead end: after three failed attempts at an element the coach offers to park it; a parked element stays … |
| DEF-076 | A | R7 | wrong_data | high | M | coached | coaching | DEF-029 | R7 amendment: baseline and target are stored as a number with a unit; an unparseable value is asked again. |
| DEF-077 | A | R13 | dead_end | low | M | coached | platform | — | R13 hard limit: no turn exceeds 45 s; a turn that would answers with what it has and says so (T24's proof). |
| DEF-078 | A | T70 | dead_end | high | L | coached | platform | — | Node time limits, retries and compensation use LangGraph's per-node timeout=, retry_policy= and error_handl… |
| DEF-079 | C | W9 | dead_end | low | M | coached | screen | DEF-054 | Every confirmed element has a change action in the progress view that starts coaching on it; the Confirm an… |
| DEF-080 | C | W8 | wrong_data | low | S | open_case | screen | — | Every coaching screen carries the standing label 'AI coach — it can be wrong; you confirm every value'; the… |
| DEF-081 | C | W10 | dead_end | low | M | coached | screen | DEF-055 | A failed or timed-out turn stays on screen, says what happened and what was saved, offers a retry and shows… |
| DEF-082 | A | R16 | degraded | high | L | coached | persistence | DEF-039 | Every element value keeps its full history: value, when, who, the reason for a change, and its source (type… |
| DEF-083 | A | C3 | degraded | low | L | coached | coaching | — | Every request explains what is asked and why, with a sample marked 'Sample only — …'; built from the case's… |
| DEF-084 | A | R17 | degraded | high | L | coached | coaching | DEF-035 | The high-level process element captures per-step duration (avg/min/max with unit), frequency and problem no… |
| DEF-085 | A | R18 | degraded | high | M | coached | coaching | DEF-028, DEF-084 | The problem statement names the step(s) where the problem shows; the coach checks the link both ways before… |
| DEF-086 | C | C1 | degraded | low | L | report | screen | DEF-069 | Each phase report is laid out in visual sections, each with a heading, a plain-language summary and key fie… |
| DEF-087 | C | C2 | degraded | low | L | report | screen | DEF-086 | Where a section's data allows, the report shows a labelled diagram or chart with a sentence on how to read … |
| DEF-088 | C | R5 | degraded | low | M | report | screen | — | R5 amendment: the Define report's seven sections carry the visuals of R5's table (team table, cost and bene… |
| DEF-089 | C | W2 | degraded | low | M | coached | screen | — | Project status (phase, days since creation, target date and days remaining, days per phase, open and awaiti… |
| DEF-090 | C | W3 | degraded | low | M | coached | screen | — | The coaching page greets the Belt by name and summarises confirmed and open elements, assembled in code wit… |
| DEF-091 | C | W11 | degraded | low | M | coached | screen | — | A typed unsent message survives a reload; every sent turn and confirmation survives a reload or restart. |
| DEF-092 | C | W12 | degraded | low | S | coached | screen | — | While a turn runs the screen says what is happening in plain words, never a generic 'thinking'. |
| DEF-093 | integrator | R12 | degraded | low | L | approve | api | DEF-064 | A fresh case with the scripted persona reaches an approved Define report in at most 40 Belt turns, no turn … |
| DEF-094 | A | T69 | degraded | low | M | coached | platform | DEF-002 | An ordinary coaching turn makes at most 4 model calls, retries included; the count is recorded per turn in … |
| DEF-095 | C | C4 | degraded | low | M | coached | screen | — | Under each reply the screen offers two or three next steps computed in code from what is missing; they neve… |
| DEF-096 | integrator | C5 | degraded | low | L | open_case | platform | — | In production the product reaches only intranet services; screens, templates, fonts and diagram drawing shi… |
| DEF-097 | B | C6 | degraded | high | L | next_phase | persistence | — | Every approved value a later phase needs is stored in its structure and available to that phase's coach; De… |
| DEF-098 | A | R15 | degraded | low | M | coached | coaching | DEF-007 | When an answer carries values for other unconfirmed elements, the coach reads them back for confirmation; n… |
| DEF-099 | C | R2 | degraded | low | M | coached | screen | — | R2 amendment: SIPOC is shown both as a table and as a process diagram; 5W2H keeps its live mind map. |
| DEF-100 | B | R6 | degraded | high | M | approve | gate | DEF-049 | R6 amendment: the report names the project lead and the Champion; approval is recorded against the signed-i… |
| DEF-101 | C | R11 | degraded | low | M | record_written | screen | DEF-060 | An approved phase report can be printed from the browser, headed with case number, phase, approval date and… |
| DEF-102 | integrator | R8 | degraded | high | L | open_case | api | — | The user is identified by the customer's single sign-on (Entra ID first); a case is visible only to its tea… |
| DEF-103 | integrator | R8a | degraded | high | L | open_case | api | — | Without single sign-on only the team members the lead registered can open the case; a personal invite befor… |
| DEF-104 | C | R8b | degraded | high | M | open_case | api | — | The creator of a case is its project lead; only the lead adds or removes members and assigns roles; the lea… |
| DEF-105 | integrator | R8c | degraded | high | M | open_case | api | DEF-104 | The project lead can hand the role to another team member; the handover is recorded in the audit trail. |
| DEF-106 | C | W1 | degraded | low | M | open_case | screen | — | The overview page explains the method and each phase from a 'Team overview' section of that phase's skill f… |
| DEF-107 | A | W4 | degraded | low | L | coached | coaching | DEF-006 | The Belt picks any unconfirmed element whose prerequisites are confirmed, or accepts the recommended one th… |
| DEF-108 | C | W5 | degraded | low | M | coached | api | DEF-056 | A file attached in chat or the files panel appears in the case files; the coach reads it against the curren… |
| DEF-109 | C | W7 | degraded | low | M | coached | api | DEF-056 | Deleting an uploaded file removes it from storage and the search index; the audit log keeps its name, diges… |
| DEF-110 | C | W13 | degraded | low | S | coached | screen | DEF-057 | A reply that draws on the manual or an upload shows the file and page it used. |
| DEF-111 | C | W14 | degraded | low | M | coached | screen | — | Every reply offers thumbs up/down and an optional comment, stored against the reply's trace. |
| DEF-112 | C | W15 | degraded | low | M | coached | screen | — | Each message shows who wrote it; a second person opening a case in use is told who is working on it. |
| DEF-113 | C | W16 | degraded | low | S | open_case | screen | — | Before the first message the screen shows whether the service is reachable and ready. |
| DEF-114 | C | W17 | degraded | low | M | open_case | screen | — | The sign-in window says what it is, who may enter and what to do otherwise, and names the project lead; an … |
| DEF-115 | B | T11 | degraded | high | M | coached | persistence | — | Exactly one writer per `thread_id` at a time (a Blob lease) |
| DEF-116 | integrator | T12 | degraded | high | M | open_case | api | DEF-102 | `thread_id` comes from an authenticated session, never from the request body (with R8) |
| DEF-117 | B | T13 | degraded | high | M | record_written | persistence | — | The case blob is never written mid-conversation, only at gate approval |
| DEF-118 | B | T17 | degraded | high | S | approve | persistence | — | The retention sweep never removes a paused thread |
| DEF-119 | A | T21 | none | high | M | coached | persistence | — | A replayed step leaves one `step_log` entry (today the channel appends — see the drift list) |
| DEF-120 | integrator | T22 | degraded | high | M | coached | persistence | — | Re-ingesting a document leaves one copy per chunk (ids passed on add) |
| DEF-121 | integrator | T28 | none | low | M | coached | platform | — | Turn latency P50 and P99 are recorded per phase |
| DEF-122 | B | T29 | degraded | high | M | coached | platform | — | Every node with an external write has an `error_handler` that undoes it and routes to a degraded answer |
| DEF-123 | A | T34 | degraded | low | L | coached | platform | — | A model failure falls through levels 1–4; degraded mode names the phase and the captured count and says pro… |
| DEF-124 | A | T35 | degraded | low | L | coached | platform | — | Two three-state circuit breakers: 3 failures in 30 s open, 60 s reset, one half-open probe |
| DEF-125 | A | T36 | degraded | low | S | coached | platform | — | A token-limit 400 is never retried on a smaller model |
| DEF-126 | integrator | T37 | degraded | low | M | coached | persistence | — | A deployment rollout ends no coaching session: in-flight turns checkpoint and resume |
| DEF-127 | B | T38 | none | low | M | coached | platform | — | Retries are exhausted before a node's error handler runs |
| DEF-128 | integrator | T42 | none | low | M | coached | platform | — | Validation and extraction steps are traced spans |
| DEF-129 | integrator | T43 | none | low | M | coached | platform | — | Every log line carries `request_id`, case id and phase |
| DEF-130 | integrator | T50 | none | low | M | coached | platform | — | A drop of more than 10% in any eval metric blocks release |
| DEF-131 | B | T56 | none | low | S | report | gate | — | Gate validation makes no retrieval calls |
| DEF-132 | A | T57 | degraded | low | M | coached | coaching | — | A capability tool refuses until a stability check has passed |
| DEF-133 | A | T58 | degraded | low | S | coached | coaching | — | Knowledge lookups always include the `general` methodology |
| DEF-134 | C | T59 | degraded | low | S | coached | api | — | An upload's `phase` and `uploaded_at` are set by the server |
| DEF-135 | A | T60 | degraded | low | M | coached | persistence | — | Evidence series are re-parsed at use and never stored in state |
| DEF-136 | A | T61 | none | low | S | coached | platform | — | Each skill description stays under 2,000 tokens |
| DEF-137 | B | T65 | degraded | high | M | report | gate | — | The third failed gate attempt escalates |
| DEF-138 | B | T66 | degraded | high | M | report | gate | — | A Tier 2 criterion can never fail a gate |
| DEF-139 | integrator | T67 | none | low | S | open_case | platform | — | Start-up exits with status 1 when a required credential is missing |
| DEF-140 | integrator | T68 | none | low | L | coached | platform | — | A second-region fallback exists before launch (deferred) |
| DEF-141 | C | C5 | degraded | low | S | open_case | screen | — | G-114: the screens load no font, script or style from outside the product — the Tabler icon font ships with… |
| DEF-142 | integrator | T86 | none | low | L | coached | platform | — | T86: an offline eval set of 20–50 Define tasks from real failures lives in evals/define/, is graded by code… |
| DEF-143 | A | T85 | degraded | high | L | coached | coaching | DEF-142 | T85: knowledge chunks carry a short context before embedding and keyword indexing, a semantic reranker orde… |
| DEF-144 | C | T87 | none | high | M | coached | platform | — | T87: e-mail, phone, account and card numbers in uploads and tool results are masked before a model sees the… |
