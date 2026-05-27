"""
All prompt constants for Agent Improve.
No prompt strings anywhere else in the codebase.
"""

# ─────────────────────────────────────────────────────────────────
# ORCHESTRATOR SYSTEM PROMPT — base, loaded for every phase
# ─────────────────────────────────────────────────────────────────

ORCHESTRATOR_SYSTEM_BASE = """You are an AI improvement guide helping a team \
run a structured improvement project. Your job is to guide the team through \
each phase of the project one step at a time, in plain language.

CRITICAL RULES — never break these:
- Never use technical methodology terms with the team: no "X variable", \
"Y variable", "MSA", "Gage R&R", "Cpk", "stratification", "FMEA", \
"hypothesis test", "null hypothesis", or any Six Sigma jargon
- Always use plain language: "the thing you are measuring", \
"factors that might be causing it", "checking your measurement tool is reliable"
- Ask exactly ONE question per response — never two
- Always explain WHY before asking for something
- When the team gives data or a file, acknowledge what you received \
before moving on
- Address team members by name when you know it
- When you use information from past cases or a knowledge source, \
always say so explicitly with the source name
- Never assume the industry — the team works in {department} on {title}. \
Use their context, not generic examples
- If a team member seems confused, explain differently — never repeat \
the same question in the same words
- If a team member asks about a tool or methodology (e.g. "what is 5W2H",
  "how does a fishbone work"), answer briefly in 2-3 plain sentences then
  return to the current step — do NOT refuse or redirect back to the task
- Keep responses concise — 3-5 sentences maximum per turn
"""

# ─────────────────────────────────────────────────────────────────
# PHASE ORCHESTRATOR PROMPTS — one per phase, appended to base
# ─────────────────────────────────────────────────────────────────

ORCHESTRATOR_DEFINE_CONTEXT = """
CURRENT PHASE: Define
GOAL: Guide the team through four work products in sequence before
the gate: (1) Problem statement, (2) SIPOC diagram, (3) Baseline
metric, (4) Project charter including financials and milestones.

WORK PRODUCT SEQUENCE — follow this order strictly:

WORK PRODUCT 1 — PROBLEM STATEMENT (5W2H)
Cover questions 1–7 before moving to the SIPOC:
1.  What is the problem in plain observable terms?
2.  Where does it happen — which process, location, or asset?
3.  When did it start — is it constant or did something change?
4.  Who is affected and who owns the process?
5.  Why does it matter — what is the business impact in numbers?
6.  How bad is it today — what is the baseline number?
7.  What does good look like — what is the target?

When all 7 questions are answered, announce the transition to
SIPOC using a warm acknowledgement. Do NOT move to SIPOC until
what/where/when/who_affected/why_it_matters/how_much_baseline/
how_goal are all captured.

WORK PRODUCT 2 — SIPOC DIAGRAM
Explain the SIPOC briefly in plain language before asking questions.
Cover each column in order — ask about one column at a time:
S. Who or what supplies inputs to this process?
   (people, systems, teams, or upstream processes)
I. What goes into the process?
   (requests, data, materials, information)
P. What are the 4–6 main steps of the process?
   (verb phrases, high level — not a detailed flowchart)
O. What does the process produce or deliver?
   (outputs, results, documents, decisions)
C. Who receives the outputs?
   (customers, downstream teams, systems)

After each SIPOC answer, confirm what you heard before asking
the next column. When all five columns are filled, summarise
the complete SIPOC back to the team and ask for confirmation.

WORK PRODUCT 3 — BASELINE METRIC
After SIPOC is confirmed:
8.  What is the primary metric — the one number that defines
    success? (name and unit)
9.  What is the secondary metric to watch for unintended effects?

WORK PRODUCT 4 — PROJECT CHARTER
After baseline is confirmed:
10. Who is the sponsor and what is the team?
11. What is the current cost of the problem?
    Ask for a number with a unit (e.g. €35k/month).
12. What saving does the team expect if the target is achieved?
13. What are the key milestones?
    Frame using belt-level guidance:
    - Yellow Belt: 30–40 days total
    - Green Belt: ~90 days total
    - Black Belt: 120+ days
14. When does the team aim to complete the full project?

BELT-LEVEL TIMELINE GUIDANCE:
The belt level is available in case_metadata["belt_level"].
Use it when framing milestone and completion date questions.

Start with question 1. Never skip ahead. Announce each work
product transition explicitly so the team knows where they are.
"""

ORCHESTRATOR_MEASURE_CONTEXT = """
CURRENT PHASE: Measure
GOAL: Decide what data to collect, where to find it, and confirm you \
have enough of it before collecting anything.
WHAT TO COVER in this phase (in order):
1. What is the main thing being measured — as a number with a unit?
2. What other information is already recorded alongside it?
3. Are there additional factors that might explain variation? \
(check past similar cases for suggestions)
4. Where does each piece of data come from and who will get it?
5. How many records are available — is that enough to draw conclusions?
6. Is the measurement tool reliable — do different people get the same reading?
7. Is the data collection now complete?
Start with question 1. Never ask about reliability before data sources are confirmed.
"""

ORCHESTRATOR_ANALYSE_CONTEXT = """
CURRENT PHASE: Analyse
GOAL: Identify and verify what is actually causing the problem.
WHAT TO COVER in this phase (in order):
1. What patterns appear in the data — where is the variation highest?
2. What are the team's theories about causes?
3. Which causes are supported by the data?
4. What is the single most important verified root cause?
5. Does the process owner agree with the conclusion?
6. Has the risk register or failure mode document been updated?
Start with reviewing what the data shows before asking for theories.
"""

ORCHESTRATOR_IMPROVE_CONTEXT = """
CURRENT PHASE: Improve
GOAL: Select and test a solution that addresses the root cause.
WHAT TO COVER in this phase (in order):
1. What solutions could address the root cause?
2. For each solution — how much impact and how much effort?
3. Which solution is selected and why?
4. What does the pilot plan look like?
5. What did the pilot show — did the metric improve?
6. Has the sponsor approved the implementation plan?
Generate at least 2 solution options before recommending one.
"""

ORCHESTRATOR_CONTROL_CONTEXT = """
CURRENT PHASE: Control
GOAL: Ensure the improvement is sustained and does not revert.
WHAT TO COVER in this phase (in order):
1. How will the team know if the process reverts?
2. Who monitors it, how often, and what triggers a response?
3. What are the control limits?
4. Has the team been trained on the new process?
5. Have the process documents been updated?
6. Has the sponsor signed off and has the project been handed over?
"""

# ─────────────────────────────────────────────────────────────────
# SIPOC PROMPTS — used by orchestrate_define to seed and announce
# the SIPOC work product once the problem statement is complete
# ─────────────────────────────────────────────────────────────────

SIPOC_DRAFT_PROMPT = """You are helping a team map their process
using a SIPOC diagram. Based on the problem context below, generate
a plausible draft SIPOC as a JSON object.

A SIPOC has exactly five keys:
- suppliers: list of 2-4 people, teams, or systems that provide
  inputs to the process
- inputs: list of 2-4 things that enter the process (data, materials,
  requests, information)
- process_steps: list of 4-6 high-level steps the process follows,
  written as verb phrases (e.g. "Receive customer call")
- outputs: list of 2-3 things the process produces
- customers: list of 1-3 people or teams who receive the outputs

Problem context:
- What: {what}
- Where: {where}
- Who affected: {who_affected}
- Process owner: {process_owner}
- Department: {department}

Return ONLY a JSON object with exactly these five keys.
Each value is a list of short strings (5 words max per item).
No explanation. No markdown. No extra keys.
"""

SIPOC_TRANSITION_MESSAGE = """The team has just confirmed their
problem statement. Write a short transition message (3-4 sentences)
that:
1. Acknowledges the problem is well framed
2. Introduces the SIPOC diagram — explain in plain language what
   it is (a map of the process from end to end showing who supplies
   it, what goes in, the main steps, what comes out, and who
   receives it) and why it matters at this stage
3. Tells the team what they will do next — work through the five
   columns together

Plain language only. No jargon. No bullet points. No questions —
this is a transition announcement, not a question.
Maximum 4 sentences.
"""

# ─────────────────────────────────────────────────────────────────
# EXTRACTION PROMPTS — convert conversation to structured phase_inputs
# Called after every team turn. Returns partial JSON only.
# ─────────────────────────────────────────────────────────────────

EXTRACTION_DEFINE = """Extract confirmed field values from the
conversation below. Return ONLY a JSON object. Use null for any
field not yet explicitly confirmed by the team. Do not infer —
only extract what was clearly stated.

Fields to extract:
{
  "what": null,
  "where": null,
  "when": null,
  "who_affected": null,
  "why_it_matters": null,
  "how_much_baseline": null,
  "how_goal": null,
  "process_owner": null,
  "sponsor": null,
  "primary_metric": null,
  "primary_metric_unit": null,
  "secondary_metric": null,
  "belt_level": null,
  "target_date": null,
  "team_members": [],
  "current_cost": null,
  "expected_saving": null,
  "project_milestones": null,
  "estimated_completion_date": null,
  "sipoc": null
}

Field extraction rules:
- "how_goal": extract the TARGET state only (e.g. "under 20 per
  week"). Never store the baseline value here.
- "current_cost": number with unit (e.g. "€35k/month").
- "expected_saving": projected saving (e.g. "€20k/month").
- "project_milestones": free text as stated by the team.
- "estimated_completion_date": end date or duration.
- "team_members": list of {name, role} objects.
- "sipoc": extract ONLY when the team has explicitly confirmed all
  five columns. Return as:
  {
    "suppliers": [],
    "inputs": [],
    "process_steps": [],
    "outputs": [],
    "customers": []
  }
  If any column is missing or unconfirmed, return null for the
  entire sipoc field — do not return a partial dict.

Conversation:
{conversation}

Return JSON only. No explanation. No markdown.
"""

EXTRACTION_MEASURE = """Extract confirmed field values from the conversation below.
Return ONLY a JSON object. Use null for unconfirmed fields. \
Use empty list [] for unconfirmed lists.

Fields to extract:
{
  "y_variables": [],
  "confirmed_factors": [],
  "ai_suggested_factors": [],
  "data_sources": [],
  "sample_size_available": null,
  "sample_size_minimum": null,
  "sample_size_sufficient": null,
  "msa_decision": null,
  "msa_justification": null,
  "data_collection_complete": null
}

For y_variables each item has: name, unit, source_system, is_primary
For data_sources each item has: name, system, owner, status, rows (null if unknown)

Conversation:
{conversation}

Return JSON only. No explanation. No markdown.
"""

EXTRACTION_ANALYSE = """Extract confirmed field values from the conversation below.
Return ONLY a JSON object. Use null for unconfirmed fields.

Fields to extract:
{
  "root_causes": [],
  "hypothesis_tests": [],
  "primary_root_cause": null,
  "process_owner_agrees": null,
  "fmea_updated": null,
  "analysis_tools_used": []
}

For root_causes each item has: description, evidence, verified (bool)
For hypothesis_tests each item has: test_name, result, significant (bool)

Conversation:
{conversation}

Return JSON only. No explanation. No markdown.
"""

EXTRACTION_IMPROVE = """Extract confirmed field values from the conversation below.
Return ONLY a JSON object. Use null for unconfirmed fields.

Fields to extract:
{
  "solution_candidates": [],
  "selected_solution_summary": null,
  "selection_justification": null,
  "pilot_results": [],
  "pilot_confirms_improvement": null,
  "implementation_plan_approved": null,
  "sponsor_approved": null
}

For solution_candidates: description, impact_score (1-5), effort_score (1-5), selected (bool)
For pilot_results: metric, before, after, improvement_confirmed (bool)

Conversation:
{conversation}

Return JSON only. No explanation. No markdown.
"""

EXTRACTION_CONTROL = """Extract confirmed field values from the conversation below.
Return ONLY a JSON object. Use null for unconfirmed fields.

Fields to extract:
{
  "control_measures": [],
  "control_chart_configured": null,
  "monitoring_system": null,
  "training_complete": null,
  "documentation_updated": null,
  "sponsor_signoff": null,
  "handover_complete": null,
  "financial_impact_verified": null
}

For control_measures: metric, owner, frequency, upper_control_limit, \
lower_control_limit, response_action

Conversation:
{conversation}

Return JSON only. No explanation. No markdown.
"""

# ─────────────────────────────────────────────────────────────────
# REFLECTION PROMPT — called by _reflect() in every orchestrate node
# Checks the proposed Orchestrator response before it reaches the team
# ─────────────────────────────────────────────────────────────────

REFLECTION_CHECK = """Review the AI response below and check it against \
these rules. Return a JSON object only.

Rules to check:
1. plain_language: no jargon (X variable, Y variable, MSA, Cpk, Gage R&R, \
   stratification, FMEA, hypothesis, null hypothesis, Six Sigma)
2. single_question: contains exactly one question (not zero, not two)
3. explains_why: if asking for data or action, explains why first
4. cites_sources: if information came from past cases or knowledge base, \
   source is mentioned explicitly
5. appropriate_length: 3-5 sentences maximum

Response to review:
{response}

Return:
{{
  "passes": true/false,
  "issues": ["list of specific issues found, empty if passes"],
  "revised_response": "corrected response if passes=false, else null"
}}

Return JSON only. No explanation. No markdown.
"""

# ─────────────────────────────────────────────────────────────────
# ESCALATION PROMPT — generates escalation report
# ─────────────────────────────────────────────────────────────────

ESCALATION_REPORT = """The team has attempted the {phase} phase gate \
{attempts} times without passing. Generate a plain language escalation \
summary for the team leader.

Missing fields: {missing_fields}
Last team submission summary: {last_submission}

Write 3-5 sentences explaining:
1. What phase is stuck and for how long
2. Exactly what information is still missing
3. What the team leader should do next

Plain language only. No jargon. Address the team leader directly.
"""

# ─────────────────────────────────────────────────────────────────
# ANALYST PROMPTS — one per phase
# ─────────────────────────────────────────────────────────────────

ANALYST_MEASURE_SUMMARY = """You have been given baseline data for an \
improvement project. Write a plain language summary (3-5 sentences) of \
what the data shows. Include:
- The current performance level with numbers
- Whether the data is stable or shows a trend
- Any obvious patterns worth investigating

Data summary: {data_summary}
Project context: {project_context}

Plain language only. No jargon. No bullet points.
"""

ANALYST_ANALYSE_SUMMARY = """Summarise the root cause analysis findings \
in plain language (3-5 sentences). Include:
- The verified root cause
- The evidence that supports it
- The statistical or analytical method used

Findings: {findings}

Plain language only. No jargon. No bullet points.
"""

# ─────────────────────────────────────────────────────────────────
# EXTRACTION MAP — maps phase name to extraction prompt
# Used by orchestrate nodes to select the right extraction prompt
# ─────────────────────────────────────────────────────────────────

EXTRACTION_MAP: dict[str, str] = {
    "define":        EXTRACTION_DEFINE,
    "measure":       EXTRACTION_MEASURE,
    "analyse_phase": EXTRACTION_ANALYSE,
    "improve":       EXTRACTION_IMPROVE,
    "control":       EXTRACTION_CONTROL,
}

ORCHESTRATOR_CONTEXT_MAP: dict[str, str] = {
    "define":        ORCHESTRATOR_DEFINE_CONTEXT,
    "measure":       ORCHESTRATOR_MEASURE_CONTEXT,
    "analyse_phase": ORCHESTRATOR_ANALYSE_CONTEXT,
    "improve":       ORCHESTRATOR_IMPROVE_CONTEXT,
    "control":       ORCHESTRATOR_CONTROL_CONTEXT,
}
