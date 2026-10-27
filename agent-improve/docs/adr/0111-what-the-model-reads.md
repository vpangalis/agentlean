# ADR-0111: What the model reads

Status: ACCEPTED (founder ruling 2026-10-27; placed by Claude Code from the ruling's text)
Requirements: founder rulings 2026-10-24 (wave 2, B8) and 2026-10-27 (items 1, 3, 5 and 10)
Facts: `agent-improve/Claude outputs/ADR_facts_0111_what_the_model_reads.md`

## Context

Six model roles read inputs built in different places (`state_injection`, `prompts.py` format strings,
`nodes_common`, the grader, the rubric); some parts are cut silently; the coach's tool description is 1,200 tokens
on every call; `cached_tokens` was 0; the gate judge reads the whole document as JSON (G-263); the grader reads
code-written lines as the coach's claims (G-254).

## Decision

**D1 One declared input per call.** Each role (coach, planner judgment, grader, gate judge, query variants,
extraction/vision) has a named, ordered list of parts, each with one owner module. The table lives in this ADR
(below); `ARCHITECTURE.md` §3.4 carries one line pointing here.

**D2 Order:** static parts first (rules, fixed phase text, tool schema), then per-element (the current element's
script block), then per-turn (case state, feedback), the task last (the move / the Belt's message). The static
prefix must be byte-identical across turns of a phase: a test compares it between two turns. First establish why
`cached_tokens` is 0 (measure; do not assume), then fix at the cause.

**D3** Cuts stay only as caps on whole parts; every cut says so in the text ("[cut at N characters]"). No cut
inside a structured value.

**D4** The `CoachingResponse` docstring shrinks to its purpose (about 150 tokens); field meanings stay on the Field
descriptions; nothing moves into the rules section. The coach's prompt may not grow.

**D5** The grader reads what the coach read: its sources come from the same composer, with the same display names
and tags; code-written lines are tagged as given (ruling 3).

**D6** The gate judge reads, per criterion, only the fields in `rubric.READS`, as tagged text (ruling 1).

**D7** Tokens per call by role stay recorded in every run-through; the coach ratchet (item 10) enforces the size.

### The declared inputs (D1), in D2's order

Paths are under `agent-improve/backend/`. "Static" is the same on every call of the role in a phase; "per element"
changes when the element in focus changes; "per turn" changes every turn; "task" is what this call is asked.

| Role (`core/llm.py`) | Call | # | Part | Kind | Owner |
|---|---|---|---|---|---|
| `coach` | `phases/nodes_common.py::_build_executor` (`create_agent`) | 1 | The tools the turn type offers, and the structured reply `CoachingResponse` | static per turn type | `middleware/turn_tools.py` (which tools); `core/substate.py::coaching_response_model` (the reply) |
| | | 2 | Section 1, the coaching rules | static | `core/prompts.py::PHASE_COACH_PROMPT`, headed by `middleware/state_injection.py` |
| | | 3 | Section 2, the phase script: the current element's block; then the opening on the phase's first turn, or the closing block once every element is confirmed | per element, then per turn | `middleware/skills.py::script_section` (from `skills/dmaic-{phase}-phase/SKILL.md`) |
| | | 4 | Section 3, the state: the case's values, tagged under display names | per turn | `middleware/state_injection.py::_compose` (`value_tag`) |
| | | 5 | Section 4, last turn's quality feedback | per turn | `middleware/state_injection.py::_compose_feedback` |
| | | 6 | Section 5, this turn's move | task | `middleware/state_injection.py::_compose_move` (`core/prompts.py` move texts) |
| | | 7 | Section 6, the conversation's label; then the conversation, the Belt's latest message last | task | `middleware/state_injection.py`; `SummarizationMiddleware` |
| `planner` | `phases/nodes_common.py::_judgment_prompt` (the one judgment) | 1 | The structured verdict `SufficiencyJudgment` | static | `core/substate.py` |
| | | 2 | What is judged and the three verdicts | static | `core/prompts.py::PLANNER_JUDGMENT_PROMPT` |
| | | 3 | The field, and what the element needs: what it is, its question, its acceptance criteria | per element | `middleware/skills.py::field_needs` |
| | | 4 | This project's framing; the read-back note | per turn | `phases/nodes_common.py::_judgment_prompt` |
| | | 5 | The Belt's earlier messages for the field | per turn | `phases/nodes_common.py::_judgment_prompt` |
| | | 6 | The Belt's latest message; the calculation inputs asked | task | `phases/nodes_common.py::_judgment_prompt`; `phases/calculations.py::missing_inputs` |
| `grader` | `middleware/grader.py::_grade` (the coaching grader) | 1 | The structured verdict `CoachingGraderVerdict` | static | `validation/schemas.py` |
| | | 2 | How a turn is graded and how a verdict is returned | static | `middleware/grader.py` (the prompt) |
| | | 3 | The method for this element: the coach's section 2 | per element | `middleware/skills.py::script_section` |
| | | 4 | The case so far: the coach's section 3 values, tagged | per turn | `middleware/state_injection.py` (`value_tag`) |
| | | 5 | What the Belt has given for the element, and the answer awaiting Confirm, as the coach had them | per turn | `middleware/state_injection.py` (the same composer) |
| | | 6 | The move and its criteria; the Belt's message; the coach's reply, its code-written lines and the script's example tagged as given and not graded | task | `middleware/grader.py` (`core/prompts.py::COACHING_QUALITY_RUBRIC`) |
| `gate_judge` | `validation/rubric.py::grade_define` (layer 2d) | 1 | The structured verdict `GraderVerdict` | static | `validation/schemas.py` |
| | | 2 | How the document is graded and how a verdict is returned | static | `core/prompts.py::GATE_GRADER_PROMPT` |
| | | 3 | The criteria to judge, each with its element's acceptance criteria and what is left to the model | per submission | `validation/rubric.py` |
| | | 4 | The document by criterion: only the fields in `rubric.READS`, tagged under display names, and the calculation line | task | `validation/rubric.py::_document_by_criterion` (`state_injection.value_tag`) |
| `query_variants` | `knowledge/fusion.py` (a lookup's variants) | 1 | The structured `QueryVariants` | static | `knowledge/fusion.py` |
| | | 2 | How to rephrase | static | `core/prompts.py::VARIANT_PROMPT` |
| | | 3 | The lookup's question | task | `knowledge/fusion.py` |
| `extraction` / `vision` | `upload/agent.py` (the upload interpretation, ADR-0104; the image read) | 1 | The structured interpretation | static | `upload/agent.py` |
| | | 2 | How to read an upload | static | `core/prompts.py::UPLOAD_INTERPRET_SYSTEM`, `VISION_EXTRACT_PROMPT` |
| | | 3 | The case's title and phase; the parsed file, screened, capped and said so | task | `upload/agent.py` |

## Consequences

No new graph nodes, no new model calls; the grader stays middleware; ADR-0110 (code is the enforcer) unchanged.

## Rejected

The ruling records no rejected alternative.
