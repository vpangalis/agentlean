# ARCHITECTURE.md — text moved out at step 6.66

This file holds text moved out of `agent-improve/ARCHITECTURE.md` at v1.77 by step 6.66, on the founder ruling of 2026-09-25 that a governing document holds only current binding text (the design as it is now, open items, and rules). Everything here is VERBATIM, grouped by the original section it came from and in original order: superseded text, dated incident narratives, completed-step prose, closed-gap discussion, reasoning that the rule sentence does not need, and the full §56 changelog entries (which the document now carries one line each). Each block is anchored `#L<n>`, where n is the line it started on in ARCHITECTURE.md at commit `5d29baa`. It is a dated record: nothing here binds, and where it disagrees with ARCHITECTURE.md, ARCHITECTURE.md wins.

---

## From: (document head)

<a id="L7"></a>
#### Original lines 7–71

> # 📋 Provenance — this file originated as a copy
>
> **Source:** [`../AGENTIC_ARCHITECTURE_REFERENCE.md`](../AGENTIC_ARCHITECTURE_REFERENCE.md),
> copied **2026-08-22** in the commit that created this file. The root's priorRebuilt and pushed (6f25c11). v2.8 → v3.0, written from the live files.

What v2.8 had wrong
Field	v2.8 said	Actual
CLAUDE.md version	2.2.14	2.2.18
Document map	ARCHITECTURE.md is "the design reference"	Reference renamed and moved to the monorepo root; that path now holds Improve's copy
Code migration	"Steps 2.5+ pending"	2.3 done, 2.4 next
REFACTORING	"the architectural bible"	Historical review register only
Structure	duplicate ## 4 heading	fixed
The corrected state summary
The document work is complete and signed off. Full review → CLAUDE.md v2.2.18 → the architecture reference (v1.3) → Task 3B verification (3 corrections, 2 now-stale, 4 enhancements, 15 confirmed) → absorption and citation sweeps → Task 4's procedure (v1.1) → the rename and split.

The codebase is still v1. One step of 38 is done. Step 2.3 upgraded dependencies (langgraph 1.1.10 → 1.2.11, langchain-core 1.3.3 → 1.6.0) and nothing else. Step 2.4 is next and not started. I put the measured facts in so the next session doesn't re-measure: 55 files / 7,924 lines, 11 flat graph nodes, zero async def route handlers, 20 content.strip() sites across 8 files, and zero checkpoints ever written despite the checkpointer being compiled in.

Three decision statuses I checked rather than trusted
G11 (REFACTORING restructure) — DONE. 11 # PART headings exist. My first check missed them because the headings are uppercase; had I not re-checked, I'd have written "pending" into the orientation file.
H1 (multi-query Option A) — substance appears absorbed into reference §23–§25, but I recorded it as "looks stale, confirm and close" rather than declaring it done. Absorbed-in-substance isn't the same as verified-closed, and this file shouldn't be where that distinction gets lost.
H2 (content_vector rename) — genuinely pending, equals procedure step 9.1.
Open items, separated by kind
Gated — request_drain (§45, unconfirmed, gates step 8.5 only), Redis (step 8.4 only), the two Azure schema changes (step 9.1). Each gates its own step and nothing else; that framing is deliberate so a gate can't stall the spine.

Watches — the langchain/langchain-core pin has zero margin (1.3.16 requires >=1.6.0 and 1.6.0 is latest), and LangGraph 1.2.7's release body repeats 1.2.6's checkpoint_ns fix verbatim.

Parallel — the five SKILL.md files (should lead step 6.6) and the eval dataset, whose >10% threshold is still an asserted number.

Future generalisation — scoped by the six annotated sections (§5, §6, §23, §30, §32, §35).

One thing I carried forward deliberately
The session protocol now includes the raw-grep -rn rule and the lesson underneath all three failures this session caught: a check that cannot fail is worse than no check, because it gets recorded as evidence. That belongs where a new session will read it before writing their first verification.

Verification: 9 of 10 automated claim checks passed against the live files; the tenth failed only because my harness invoked WSL bash rather than Git Bash — I confirmed that claim (55 files) directly afterward.
> commit was **`8533879`**.
>
> **This is Agent Improve's architecture document.** It began byte-identical to
> the platform reference at the monorepo root and **is expected to diverge**:
> the root gets generalised across Agent Improve, Agent Resolve and Agent Flow,
> while this file stays specific to Improve. **Divergence is the intent, not
> drift.**
>
> **There is deliberately no sync check.** The two files are only briefly
> identical, so a diff between them would fire constantly and mean nothing — and
> a check that always fails teaches you to ignore it.
>
> | If you are changing… | Edit |
> |---|---|
> | Platform architecture — binds on all three agents | `../AGENTIC_ARCHITECTURE_REFERENCE.md` |
> | Agent Improve specifically | **this file** |
> | A rule quoted in implementation prompts | `CLAUDE.md` |
>
> **`CLAUDE.md`'s `§` citations point at the root reference, not at this file**
> — one rule, mechanically checkable. See `CLAUDE.md` §0.12.
>
> **What was here before:** this path held the v2.2.16 design document, frozen
> as SUPERSEDED after being absorbed into the reference. Its two registers that
> lived nowhere else — §17 Decisions Resolved and §18 Change Log — were
> extracted to `docs/_archive/ARCHITECTURE_v2216_registers.md` before this copy replaced (archived to docs/_archive/; canonical: ARCHITECTURE.md Appendix F)
> it, and were **merged back into this file on 2026-09-01 as
> [Appendix F](#appendix-f--the-v2216-registers)**. The full prior file is at
> commit `8533879`.
>
> **Paths inside this document are written from the monorepo root**, inherited
> from the source. From here, `agent-improve/backend/...` means `backend/...`.

---

## From: 🗺 Where state lives — a MAP, not a definition

<a id="L77"></a>
#### Original lines 77–82

**Four places, and this table is not one of them.** It holds no field list of
its own and never will: it says where each thing is defined and sends you
there. **If this section ever restates §57.2 or §58.2, it is wrong** — a second
copy of a field list is the exact duplication that cost two days to remove on
2026-09-10, when four documents held overlapping answers and the guard checked
only that two of them had been touched, never that they agreed.

<a id="L91"></a>
#### Original lines 91–97

> **There are NO `{Phase}State` classes — ruled 2026-09-11, step 6.20.** This
> document named `DefineState`, `MeasureState`, `AnalyseState`, `ImproveState`
> and `ControlState` thirteen times and the tree contained none of them, with
> **G-19 open for two months** because their fields could never be enumerated.
> They are not built and will not be; §39.x.7 describes per-phase USE of the
> shared `PhaseState`, which is what those tables always actually contained.
> S-C03 carries the ruling.

<a id="L99"></a>
#### Original lines 99–102

**Adding a field to either class is a §56 amendment**, and the test it must
pass is the one §5 already sets: **name the node that writes it and the node
that reads it.** `project_context` failed exactly there — no writer at all, and
its only reader ran before the point it was supposed to be set.

---

## From: Agentic Architecture Reference

<a id="L112"></a>
#### Original lines 112–283

**v1.77 (2026-09-25)** — **§56 AMENDMENT. S-C04 TAKES THE SHAPE STEP 6.61 BUILT — THE PLAN IS CODE'S, THE PLANNER'S MODEL MAKES ONE JUDGMENT.** Carried by step 6.61, as v1.75 (B) required (CLAUDE.md, amending the rules, 3b). **(A) S-C04.** `CoachingPlan` is built by `phases/moves.decide`, never returned by a model: `next_action` is RETIRED; `status` (not taught / asked / answered / confirmed), `move` (teach / challenge / read_back / store_and_advance / respond), `judgment`, `answer`, `messages`, `pending`, `store`, `stored_field` and `statuses` are added, and `focus_field` becomes optional (`None` once every position is confirmed). The planner model's structured output is the new `SufficiencyJudgment {verdict: sufficient | insufficient | not_an_answer, reason}`, asked for ONLY when the Belt has answered — the opening, a field not yet taught and a plain yes cost no model call. `respond` is the move for a message that is not an answer (*"where do we stand?"*): the field's status does not change. **(B) WHERE THE STATUS AND PENDING LIVE — `PhaseState.field_status` (ruling R5, 2026-09-25, superseding the first draft's reply-borne status).** Four explicit statuses per field, checkpointed, every one starting `not taught`: not taught → asked → answered (the Belt's words held PENDING; awaiting confirmation = answered and read back) → confirmed (stored). The current field is the first not confirmed. **Only code changes a status, and only at turn end**; nothing is derived from the previous reply's record. The map rides out on the graph payload, is written to `PhaseRecord.field_status` by the same statement as the values, and seeds the next turn through the case record — the path `field_log` takes (S-C02, §58.2). The move record (field, move, status, judgment) still rides on the reply as `additional_kwargs["coaching_move"]`, beside last turn's quality feedback (`"quality_feedback"`), for section 5 and the audit; `core/conversation.py` round-trips both. `SupervisorState` and `CoachingResponse` gain no field; `CoachingResponse.fields_captured`'s DESCRIPTION now says it carries the read-back, pending until confirmed (S-C05 B7), and `draft` carries only what the turn stored. **(C) CONFIRMATION IS A RULE, NOT A MODEL.** A plain yes (`moves.is_confirmation`) stores the pending value; anything more is a correction and returns the field to answered (the ruling's clause). **(D) WHAT A YES STORES.** A plain-string answer given in one message stores the Belt's own words, even where the read-back reworded them; a structured field, a composed one (`problem_statement`) and an answer assembled from more than one message store the version read back — the one the Belt said yes to. A yes that cannot complete the position (a structure refused) is read back again, never advanced past. **(E) CONSEQUENCE, recorded and not resolved:** `retrieval_strategy` is the phase's §28 default and `retrieval_hops` stays empty, so S-C04's *"the planner may select multi_hop in any phase"* and §26's model-PLANNED hop chain have no author until a step gives them one. **(F) S-C11 B2's ORDER** (facts at the top of the prompt) is superseded by v1.75's six sections — rules first, state third; B2's channel rule (never `messages[]`) stands. **(G) FINDING — G-110:** a CONFIRMED field has no move that revises it — the Belt correcting an earlier field in a later turn is not modelled by the moves. (E) is registered as **G-111**. **(H) CONFIRM AND CHANGE (ruling R4).** Every read-back shows two buttons; a click sends `AskRequest.action` (`confirm` | `change`) and code sets the status whatever the text says — confirm stores the pending value, change returns the field to asked with the Belt's words kept, and its reply is written IN CODE with no model call — the Belt's exact current words, then "What would you like to change?" (founder ruling on 6.61's review: live, the model left the words out 3 of 3 runs). A typed plain yes is still a confirmation (C). **(I) THE GRADER GRADES THE MOVE (fix 3).** `middleware/grader.MOVE_EXCLUDES` names, per move, the rubric lines that move does not answer (a read-back is not failed for not challenging; a challenge is not failed for not citing methodology); the grader is told the move and graded on the rest, and section 5 carries only the failures that apply to this turn's move — so section 5 never contradicts section 4. The challenge exclusion is the challenge loop's cause, measured live (step 6.61's commit body). **(J) SECTIONS 2 AND 6 (fix 4).** Section 2 is the script's opening (first turn only) plus the CURRENT field's block — not the whole script, and the skill catalogue is no longer in the message; section 6 is one entry per coach turn, its reply text — no stubs, no structured-output dumps. **(K) THE FALLBACK IS CONTAINMENT.** A timeout or the runaway backstop gives the Belt the move's script question in code, never the backstop text; every use is logged at ERROR as a DEFECT and flagged `fallback` on the move record. Reasoning: step 6.61's commit body (§56.2).

**v1.76 (2026-09-25)** — **§56 RECORD. STEP 10.0 — §50.1's FOUR BLOCKS AND THE GRADER'S WARNING REACH THE BELT.** **(A) WHAT CHANGED IS THE TREE, NOT THE RULE.** §50.1 already required four blocks on screen and §19.8 a Belt-visible warning; neither left the backend (G-69, G-76, G-103). The executor now puts `explanation`, `example`, `prompt` and `progress` (`coaching_blocks`) and the grader's warning (`grader_warning`) on the reply message's `additional_kwargs` — the channel the SIPOC diagram already uses — because the route never holds the `CoachingResponse`, only the graph's messages; `AskResponse` declares them (defaulted, §4.8), the route projects them beside `answer`, `conversation_history` keeps them, and the UI draws one block per field in §50.1's order, the example set apart (B6), an empty block absent. **`message` stays the transcript entry.** **(B) THE WARNING'S WORDING** is the founder's, 2026-09-25: *"My quality check flagged this reply as weaker than it should be. If it doesn't help, tell me and I'll try again."* **(C) A PAGE RELOAD REDRAWS PAST TURNS** from `conversation_history`, blocks included (G-79, the chat half); the stored VISUAL is still drawn from the last send only — that half needs the UI's v2 field names and is 10.3's. **No schema of the three load-bearing ones changed** (`AskResponse` is the gateway envelope). Reasoning: step 10.0's commit body (§56.2).

**v1.75 (2026-09-25)** — **§56 AMENDMENT. THE COACHING MOVE IS DECIDED IN CODE — ALL PHASES, ALL AGENTS.** Founder ruling 2026-09-25. **The ruled text, verbatim:** *"The coaching move is decided in code, never by the model. For every field in every phase and every agent, code determines this turn's move from the field's status: not yet taught -> teach (explain, show, ask); answered, judged insufficient -> challenge (say what is missing); answered, judged sufficient -> read back (the Belt's own words, then ask 'is this right?'); confirmed by the Belt -> store and advance. An LLM is used only to judge whether an answer is sufficient, and to write the coach's words. A value is stored only after the Belt confirms it, in the Belt's words; a tidied version may be proposed in the read-back and is stored only if the Belt confirms it. The coach's input is assembled by code each turn in labelled sections, each with one job: coaching rules (how to behave), phase script (what to teach), state (facts), this turn's move (authoritative), last turn's quality feedback, and the conversation. The rules and scripts contain no move-sequencing instructions. Feedback to the coach is never presented as a message from the Belt. Basis: Anthropic, 'Effective context engineering for AI agents' (distinct sections, high-signal context, no brittle logic in prompts) and 'Building effective agents' (workflows for well-defined tasks; evaluator-optimizer)."* **(A) WHY — measured.** The coherence audits (`IMPR-2026-AD5`, `IMPR-2026-4E5`, the 10.0 proof `IMPR-2026-8D4`, 0 traces) found the move decided nowhere reliable: the Define script says *"Confirm, then move on"*, the coach rules say *"A coaching turn does ONE thing and then stops"*, and the planner's `next_action` reaches no channel the coach reads; the coach sometimes waited after a read-back, sometimes moved on, occasionally re-asked a field, and stored its own paraphrase before the Belt confirmed. **(B) SECTIONS AMENDED:** §17, S-C04 (§58.4), §19.1 and S-C11 (§61.2, B7), §20 and S-C05 (§58.5, B7), §22, §32, §43 — each carries a v1.75 note. **Schemas are NOT changed here**: `CoachingPlan` and `CoachingResponse` keep their fields until step **6.61** builds the change, and that step carries its own amendment for any field it adds (CLAUDE.md, amending the rules, 3b). **(C) OWNER:** step 6.61, first in Appendix F's `Order`; the four other phase scripts' move-sequencing text is step 6.62. **(D) BACK-PORT OWED:** the ruling binds all three agents, so `AgentLean/AGENTIC_ARCHITECTURE_REFERENCE.md` (the platform reference — its Planner/Executor levels and coaching method) owes the same amendment; it is NOT made here, and is recorded as owed. Reasoning: this commit's body (§56.2).

**v1.74 (2026-09-25)** — **§56 AMENDMENT. v1.73 (C)'s WRITTEN STEP IS THE POSITION AFTER THE TURN'S CAPTURE, WRITTEN ON EVERY TURN.** Founder ruling 2026-09-25. **(A) THE DEFECT.** v1.73 computed the written label from the turn-START artifacts, so on every capture turn it lagged one step — dry run 2 (IMPR-2026-134, turn 2): the Belt answered position 1, the model wrote *"Step 2 of 12"*, the executor overwrote it with *"Step 1 of 12"*. **(B) THE RULE.** The executor writes `define_progress` of the artifacts AFTER the capture merge into the reply's `progress` and the stored structured-response message, unconditionally; the turn-start label the coach was delivered is recorded beside it (`delivered_label`) with the model's own (`reply_progress`). No condition on the conversation's history. Reasoning: the fix's commit body (§56.2).

**v1.73 (2026-09-25)** — **§56 AMENDMENT. DEFINE'S "STEP n OF 12" IS COMPUTED, DELIVERED AND WRITTEN — NEVER COUNTED BY THE MODEL.** Founder ruling 2026-09-24, applied at step 6.57. **The ruled text:** *"Compute the Define position from DEFINE_FIELD_ORDER (12 positions; metric_definitions sits inside position 5, §39.1.9) and deliver it every turn, as v1.71 delivers the script. Keep the gate's 'missing (… of 13)' list separate and labelled as the gate list."* **(A) WHY.** Every coaching turn on 0E5 wrote *"Define · 13 of 13"* — the gate list's count, the only one the coach was given. **(B) ONE FUNCTION.** `define_progress(artifacts)` (`phases/define/schema.py`): the first position not complete, 1..12, position 5 complete only with `metric_definitions` as well. `BeforeModelStateInjection` delivers it at the top of the block; `field_index` is it minus one; step 10.3's bar calls it. **(C) DELIVERY WAS NOT ENOUGH, MEASURED** — with the step first in its input the model still wrote *"13 of 13"*, its own earlier replies carrying `of 13` 55 times. So the executor WRITES the computed label into the reply's `progress` and re-renders the stored structured-response message; the model's own value is recorded in `step_log` (node `define_position`: `reply_progress`, `reply_matches`). **(D) THE GATE LIST** is headed *"THE GATE LIST … (n of 13 gate fields; not the step count)"*. Reasoning: step 6.57's commit body (§56.2).

**v1.72 (2026-09-24)** — **§56 AMENDMENT. LAYER 2a JUDGES A REPLY AGAINST THE SCRIPT STEP IT PERFORMS, AND EVERY VERDICT IS RECORDED (G-96).** Founder ruling 2026-09-24, Option A. **The ruled text:** *"Coherence gets the current script step; reading back to confirm is allowed; 'parroting' = restatement with no confirmation question and nothing added; every 2a rejection records its reason in step_log."* **(A) WHY.** §19.7 asked *"is it parroting?"* and §43's ④ Confirm asks for a read-back — opposite demands on the same reply, and the judge was told neither which step the coach was on nor shown the question: `CoachingResponse.prompt`, where the confirmation question lives (§50.1), never reached it. On 2026-09-24 13:14 (`IMPR-2026-0E5`) it rejected a Confirm reply as parroting, degraded the turn, stood the grader down, and left no record why (capability row 13). **(B) THE STEP IS DERIVED, NOT ASKED.** A reply that captured a value is at that field's ④ Confirm; one that captured nothing is at the planner's focus field's ①–③. The judge is given the step, the field's numbered block from the phase's SKILL.md (all five number their fields), and the whole reply — `message`, `explanation`, `example`, `prompt`. **(C) RECORDED.** One `step_log` entry per turn, node `coherence`: the verdict, its reason, `degraded`, `grader_skipped`, and the step judged against. Reasoning and the measurements: the G-96 commit body (§56.2).

**v1.71 (2026-09-24)** — **§56 AMENDMENT. THE CURRENT PHASE'S SCRIPT IS DELIVERED ON EVERY MODEL CALL AND RECORDED — NEVER LEFT FOR THE COACH TO FETCH.** Founder-ratified 2026-09-24 (relay), applied at step 6.46 (option A). **The ratified text:** *"§19.2 / §32 / S-C12: For the phase being coached, level 2 (the phase's full SKILL.md) is placed in the system message on every model call by DMAICSkillsMiddleware, and each turn records the script's version and hash in step_log. load_skill stays registered for other phases' scripts and level-3 references, but the current phase's script is never left to the coach's choice. Rule: any content the product depends on is delivered and recorded, never left for the model to fetch. The system-prompt sentence 'load_skill IS A WHOLE TURN' is removed."* **(A) WHY.** Level 2 was reached only by the coach calling `load_skill`; it was called **zero times in the last 30 traced turns on IMPR-2026-0E5** (2026-09-15 .. 09-24), with the tool bound, offered, and the catalogue saying *"load first"* — while the system prompt called it *"a whole turn"*. A mechanism that waits for the model to choose cannot guarantee anything. **(B) THE COST.** 7,586 tokens per model call; the script sits in the system message, never in `messages[]`, so the conversation does not grow. **(C) WHAT IS RECORDED.** One `step_log` entry per turn, node `coaching_script`: script, version, sha256, `delivered`, `model_calls` — a turn coached without its method is distinguishable after the fact. **(D) §22 IS NOW ENFORCED AT CAPTURE**, because the worked examples arrive with the script: a captured value that reproduces one is refused and recorded (`fields_example_refused`). Reasoning: step 6.46's commit body (§56.2).

**v1.70 (2026-09-23)** — **§56 AMENDMENT. `CoachingResponse.fields_captured`'s DESCRIPTION CARRIES THE DECLARED SHAPE OF ALL NINE STRUCTURED COACHED FIELDS.** Founder ruling, applied as step A of the Define critical path with 6.48's enforcement half. **(A) WHAT CHANGED, AND WHAT DID NOT.** The description now names `team`, `metric_definitions`, `project_scope`, `process_map_sipoc`, `detailed_process_map`, `control_plan` and S-C32's three cross-phase reference dicts, each with its keys. **It is a DESCRIPTION, not a type change**: the ratified eight fields stay eight, `value` stays `Any`, and **a per-phase response schema stays ruled out — this is not one.** What changed is what the model is told, on the one channel it cannot miss. **(B) WHY THE CONTRACT AND NOT THE COACHING SCRIPT, MEASURED RATHER THAN ARGUED.** The shape was written into `skills/dmaic-define-phase/SKILL.md` first — correct content, right file, and **it did not reach the model.** SKILL.md loads at **level 2, on demand**, through the `load_skill` tool the coach must choose to call (§19.2, S-C12). **On four live turns, 2026-09-23, `load_skill` was called ZERO times and all four Define fields came back as prose.** **(C) A DECLARED SHAPE IS PART OF THE TYPE CONTRACT, NOT PART OF COACHING.** A contract that lives only in a document can be broken by editing that document, with nothing failing until a Belt reaches a gate — the failure class §55.2 exists for. **(D) FOUR REFERENCE KEYS, NOT THREE.** S-C32 carries `references_phase`, `references_field`, **`references_metric_name`** and `references_value`; the fourth names WHICH registry metric a link is about (F-13, closed 2026-08-26) and the shape is uniform across all three dicts. Checked against §63.6 before writing rather than recalled — the description would otherwise have taught the model a three-key shape the grader cannot resolve. **(E) ENFORCEMENT IS STILL AT CAPTURE** (step 6.48). This makes the contract REACHABLE; 6.48 makes it ENFORCED. Capability row 18 goes green on both, and neither does it alone. Reasoning: this commit body (§56.2).

**v1.69 (2026-09-23)** — **§56 AMENDMENT. FOUR CORRECTIONS THAT UNBLOCK THE DEFINE VERTICAL — the document half of the founder's procedure amendment. NO CODE AND NO SCHEMA CHANGE; every code change stays a step.** **(A) §39.1.9 GAINS DEFINE'S `phase_metrics` ENTRY, AND IT IS WHAT UNBLOCKS 6.20's SCORECARD HALF.** One entry per registry metric engaged, assembled deterministically in `gate_apply` immediately before the `{Phase}Output` is constructed — **no model call** — carrying `name` and `unit` verbatim from `metric_definitions`, `baseline_estimate` and `target_value` from the captured fields of the same names, and `source: "stated"`, because Define states rather than measures. **The single-authority invariant (§39.2.3, S-F28) then holds BY CONSTRUCTION**: the entry's values ARE the captured scalars, so the two cannot drift — which is the reason the assembly is deterministic rather than a convenience. A model asked to restate a number it was shown is a second author of that number. **6.20's scorecard half was never blocked on code; it was blocked on this shape never having been written down**, and this subsection states once what §63.1's type comment and §63.9's table row carried separately. **(B) THE `computation_results` SCAN IS VALIDATION STACK LAYER 2d, NOT "THE GRADER" — §7 AND §39.3.7 CORRECTED.** §36 forbids conflating the two graders and this is where the conflation entered: `DMAICGraderMiddleware` (§19.8) judges COACHING PROCESS QUALITY every turn, Layer 2d judges GATE CONTENT once at the gate, and the scan is Layer 2d's — §62.9 B3, *"scan `artifacts["computation_results"]` for the relevant tool entry rather than asking the model."* **Attributing it to the middleware put a gate check on the turn path**, which step 7.2 would have inherited. **THREE MORE SITES CARRY THE SAME WORDING AND ARE DELIBERATELY UNTOUCHED** — §39.2.7 (Measure), §39.4.7 (Improve) and §39.5.7 (Control) — because the ratified card named two and widening a ratified card is how a correction becomes a sweep nobody reviewed. **They are reported rather than fixed**, and they are the same defect. **(C) §37 NAMED A STOP MECHANISM ITS OWN RULING FORBIDS.** It specified that the middleware *"raises `HITLInterrupt`"*; **that class is DELIBERATELY NEVER DEFINED** — ruling v1.21(D), carried as G-15 since 2026-09-10 — because step 7.3 pauses with LangGraph's own `interrupt()`, which is resumable by construction, and an exception from `after_agent` is not. **Anything built to this text would have built the forbidden thing.** Left open as *"a naming problem"* in v1.21 and v1.22; closed here by naming what actually pauses. Placement is step 6.44's: a stop belongs in a node, detection stays in the coach's existing reply. **AND §37's SCOPE IS STATED FOR THE FIRST TIME: it governs contradiction of a GATE-COMMITTED value only.** A Belt revising an uncommitted field mid-phase is ordinary coaching, its record is `PhaseState.field_log` (§6, step 6.33), and conflating the two would make every ordinary revision an interrupt. That warning existed only inside a field description the coach reads, never in the section governing the behaviour. **(D) §63.9's CONTROL ROW AND §39.5.3 NAMED DIFFERENT KEYS FOR ONE SHAPE.** The row said `post_improvement_metrics, improvement_delta`; the worked example writes `actual` and `delta`. **Both names exist elsewhere in Control's schema as top-level captured fields**, which is what made the disagreement plausible in both directions rather than obviously wrong in one. **§39.5.3 wins because it carries the worked example**, and the row now points there rather than restating it. Reasoning: this commit body (§56.2).

**v1.68 (2026-09-21)** — **§56 AMENDMENT. `PhaseState` GAINS `field_log`, ITS TWENTY-THIRD FIELD, AND §6 GAINS THE RULE THAT `artifacts` IS SEEDED RATHER THAN BLANKED.** Founder ruling, ratified for step 6.33. **(A) THE FIELD.** `field_log` records WHEN each captured value changed and what it was before — one entry per change, keyed `{phase}:{turn}:{field}` per §11, the first capture of a field included with no `prior_value`. **A third thing that neither existing field can answer for**: `artifacts` holds only the current value because the merge overwrote the last one, and `step_log` is one entry per NODE per turn and never held a value at all. §7's argument for string-typed fields is that *"the Belt must be able to show what they stated"*; a Belt who revised a baseline on turn 9 after an upload contradicted it can show the figure and not the revision. **(B) THE CHANNEL CARRIES A REDUCER, AND THAT IS THE DECLARATION.** `merge_field_log` is attached in `core/substate.py`, so a node returning only this turn's entries cannot replace the history — the move `messages` and `step_log` already make, and the opposite of `artifacts`, which merges in its writer and depends on every writer remembering to. **A log is exactly the field where "every writer must remember" fails**, because the writer that forgets leaves no trace of what it dropped. **(C) IT IS NOT `operator.add`, AND §11 IS WHY.** §11 requires a deterministic key so *"the replay overwrites its own earlier entry instead of duplicating it"*. `operator.add` cannot honour that and does not honour it for `step_log` today — a replayed turn appends its entries twice. `merge_field_log` upserts on the key. **§11 states the rule; this is the first channel that enforces it**, and §11 now says so rather than leaving the two channels to be assumed alike. **(D) THE TURN NUMBER IS COUNTED IN THE CONVERSATION, NOT TAKEN FROM `turn_count`.** G-39 leaves that field's increment contract unstated and the measured behaviour is worse than ambiguous: the input mapper seeds it to `0` every invoke and `core/graph.py` reads it as the ENTRY MODE, so it is `0` on every coaching turn — which is why every `step_log` key reads `{phase}:0:{node}`. **A change log keyed on it would have each turn overwrite the one before, which is the defect 6.33 exists to end, reproduced inside the fix.** The Belt-message count accumulates across turns and is stable under a replay. **G-39 is routed around, NOT closed.** **(E) `artifacts` IS SEEDED FROM THE CASE RECORD — A NEW INVARIANT ON S-C02.** `new_phase_state` initialised it to `{}` on every turn from step 3.1, so the field §6 calls *"the accumulation"* could hold one turn's worth and was permanently identical to `draft`. **This is the defect step 6.11 fixed one field over**, on `uploads`, and its comment already carried the argument: the input mapper is the only thing that builds `PhaseState`, so a constant there is not a default but a ceiling. **(F) AN EMPTY CAPTURE IS REPORTED, NEVER SILENTLY DROPPED — B13.** The turn's log counted KEYS and the write filtered on VALUES, so *"captured 1 field(s)"* and *"nothing reached the gate document"* were both true of the same turn. Worse, an empty value in the merge DESTROYED the prior value in `artifacts` while the case-blob write discarded the same entry — two records of one field disagreeing, silently, in the direction that loses data. Both ends now split the capture through one function and name the fields they dropped. **(G) THE LOG PERSISTS IN `PhaseRecord.field_log`, NOT THE STORE'S `case` RECORD, AND §6's `asks` RULING DOES NOT EXTEND.** That ruling turns on who must read the thing BETWEEN turns: an ask is answered by an upload arriving on a route that cannot see the checkpoint. A field change has no such reader, and **a history persisted on a different schedule from the value it is a history OF can disagree with it** — which reads exactly like a change that never happened. It inherits §10's open per-turn case-blob write rather than adding one, and moves with `structured` when step 10.2 removes it. Reasoning: this commit body (§56.2).

**v1.67 (2026-09-20)** — **§56 RECORD. Two of step 6.20's three write paths land, and §39.x.7's contract statements are CONFIRMED UNCHANGED rather than assumed to be.** **(A) WHAT CHANGED IS THE TREE, NOT THIS DOCUMENT.** The executor now writes `artifacts["computation_results"]` in §7's five-key shape from the turn's computation-tool calls, and advances `field_index` through Define's ordered list. §39.x.7 already said both — *“`computation_results` — every tool run (§7 shape)”*, *“`field_index` walks the §39.x.2 list”* — so a claim that was true as a contract and false as a description of the tree is now true as both. **Nothing here needed correcting**, and this entry exists because rule 2b asks for that confirmation to be on the record rather than inferred from silence. **(B) THE BUILD STATUS IS NOT HERE AND MUST NOT COME BACK.** It is Appendix F's row, since 6.37. This document holds the contract; whether the tree meets it is the register's column. **(C) TWO CLAUSES OF 6.20 ARE HANDLED BY AMENDMENT ELSEWHERE AND ARE DELIBERATELY UNTOUCHED HERE** — `phase_metrics`, whose Define entry shape is being written into §39.1.9, and the grader clause, where §36's two graders must not be conflated and Layer 2d is the reader meant (step 7.2). **(D) A MISATTRIBUTION IS REPORTED AT ITS SOURCE.** `docs/REFACTORING_PROCEDURE.md` line 3457 attributes the `computation_results` scan to §35 and §41; **checked rather than repeated, both sections mention it zero times** — §35 is *Two tiers of field, and the `warning` verdict* and §41 is *Structured dict fields, and FMEA*. Left for the amendment that owns the step text. Reasoning: this commit body.

**v1.66 (2026-09-18)** — **§56 AMENDMENT. EVERY SECTION NOW OWNS A ROW OR DECLARES IT CANNOT, AND v1.26’S COMPLETENESS CLAIM IS CORRECTED.** Step 6.40, founder ruling. **(A) THE POPULATION WAS NEVER DEFINED.** §66’s header has always said the correspondence *“is checkable”*; in the section-to-row direction it was not, because nothing distinguished the sections carrying no annotation from the 17 that carried one — the 17 were simply the ones somebody had annotated. **(B) 198 → 11, MEASURED AT EACH STAGE.** 6.39’s 96 spec rows already covered their own sections (112). §16’s own convention — *“one marker per item, never one per section that mentions it”* — accounts for every sub-section whose ANCESTOR owns a row (78). **Four missing markers cost 40 sections**: §39.1 owned a row and §39.2–§39.5 did not, though all five are “complete specification” sections of the same kind (38). §43 gains seven rows and §56, §57, §67 and §68 are declared NOT-MARKABLE by category (11). **(C) THE FOUR PHASE SECTIONS ARE ⚠️ AND THE TREE RULED IT, NOT THE FOUNDER.** The ruling said ☐ NOT BUILT on the premise that step 3.4 left four phases outstanding, and instructed that the tree overrides. It does: **3.4 is ✅ built**, all five `{Phase}Output` classes exist as Pydantic models citing their spec entries, and all five validators exist — `validate_define` is `async def`, which is why a `^def ` sweep first reported it absent. **(D) §43 IS BUILT AND FAILING, NOT UNBUILT.** Its rules are grader criteria: `COACHING_QUALITY_RUBRIC` at `core/prompts.py:1510`, imported by `middleware/grader.py:53`. Five map to a criterion and are ⚠️; **§43.3 and §43.4 are ☐** — no SKILL.md carries the six-stage count, and `check_gate_status()` is absent from the tree, which is G-31. **(E) v1.26 IS CORRECTED IN PLACE RATHER THAN DELETED.** It claimed *“MARKER COVERAGE IS NOW COMPLETE”* and was accurate on the day: it walked **62 top-level sections** and **nothing re-ran it**. There are now 69, nine carry neither, and it never ranged over sub-sections at all. **§55.2’s own sentence, turned on a changelog entry — a claim nothing re-runs is a claim.** The cost of a completeness claim that aged silently is the evidence, so the entry stands with its correction attached. **(F) ELEVEN JUDGEMENTS REMAIN AND ARE PINNED.** `PENDING_CLASSIFICATION` carries §1, §4, §19, §19.9, §39, §50, §58, §63, §66, §69 and §69.1, ratcheted at 11 so a section that gains a row or a declaration must LEAVE the set rather than merely stop mattering. Reasoning: this commit body.

**v1.65 (2026-09-18)** — **§56 AMENDMENT. §26’s HOP CAP GOES FIVE → THREE, AND G-83 CLOSES.** Founder ruling, applied at step 6.35. **(A) THE DECLARED CAP NOW MATCHES THE MEASURED CEILING.** §25’s fusion makes one hop a MODEL CALL plus six searches plus RRF — **~9.5s measured** on G-63’s trace and on rid `ca6ba417` — so a fifth hop landed near 47.5s against the executor’s 40s budget (6.34). The turn died on the wall before the cap could fire and `_HOP_BUDGET_SPENT` was **unreachable code**. **(B) IT WAS DEAD THE DAY IT WAS WRITTEN**: fusion landed at step 5.2, the cap at 6.7 — the cap was built on top of a per-hop cost that already excluded it, and no check compared the two. **(C) NO CAPABILITY IS LOST.** Hops four and five could never be taken. What changes is that the limit is REACHABLE, so the coach composes from `_HOP_BUDGET_SPENT` instead of being cancelled mid-search. **(D) THE ARITHMETIC IS A TEST, NOT A COMMENT.** `MEASURED_HOP_SECONDS` and `HOP_BUDGET_COMPOSE_RESERVE` are declared beside the cap with their provenance, and `test_hop_cap.py` asserts a full-budget turn FITS the node budget, that five would NOT, and that four would not either — so the cap is the largest value that fits rather than a guess under it. **An unreachable cap is unfalsifiable, which is how five survived eleven steps**, and the existing cap tests could not catch it because they are budget-RELATIVE and pass at any value. **(E) PER-HOP COST IS DEFERRED ON A CONDITION.** Cutting fusion’s six queries per hop is the other lever; it **waits for step 9.0**, when the corpus is ingested and recall can first be measured. Cutting breadth before then would trade an unmeasured quality for a measured latency. Reasoning: this commit body (§56.2).

**v1.64 (2026-09-15)** — **§56 AMENDMENT × 2. S-C05’s four presentational fields become optional, and BUILD STATUS BEGINS LEAVING THIS DOCUMENT.** Founder ruling, applied at procedure step 6.31. **(A) S-C05: `default=""`, AND AN EMPTY FIELD IS A FINDING.** `explanation`, `example`, `prompt` and `progress` were REQUIRED `str` from 6.19, so **a model omitting `progress` failed the whole turn’s structured output** — a hard failure to the Belt, which §4.8 forbids in terms. 6.19’s own record flagged it: *“defaults would need a §56 amendment, so the ratified shape stands until ruled otherwise”*. It is now ruled. **Optional WITHOUT a finding would have been worse than required** — it trades a loud failure for a silent one, with the UI drawing four blocks, one of them blank, and nothing anywhere noticing. So `substate.py::presentational_gaps` names which came back empty and the executor logs it at WARNING. **Degraded, not broken** — the same shape as G-63’s refusal to dispatch. Whitespace counts as empty (B6). `message` is deliberately NOT among the four: a turn with no coaching text has nothing to append to `messages` and is a real failure. **(B) STATUS MOVES TO `REFACTORING_PROCEDURE.md` APPENDIX F; RATIONALE STAYS HERE.** The 69 `> **BUILT:**` markers each mix *why a thing is shaped this way* with *whether it exists today*, and **§58.5 held both versions of the same fact in ONE block** after 6.19 landed — *“✅ all 8 fields exist”* and *“the four … are NOT BUILT”*, three lines apart. That is the predictable outcome of storing a status inside a rationale, where the reader’s eye goes to the prose and the status rides along unmaintained. **Appendix F is now the single leading document for build status**: one row per step, seven columns, organised by layer, and an ANCHOR in every row — `mod::Symbol` with `{a,b}`, `=v`, `absent:`, `installed:` and `repo:` forms, **never a line number**. `verify_built.py` is the referee and fails CLOSED. **(C) THE MIGRATION IS ONE MARKER AT A TIME, BY JUDGEMENT.** §58.5 goes first, being the one that states both versions at once. **Not a script** — a marker’s prose must be read to know which half is status and which is rationale, and a regex that guessed would produce 69 edits nobody reviewed. **Until a marker is migrated it is mid-flight, not authoritative.** **(D) A FALSE PASS CAUGHT ON THE STEP’S OWN ROW.** The seeded anchor `absent: `.claude.hooks.verify_built::read_matrix`` names a module that can never import, so the `absent:` was **trivially true and would have stayed true after the symbol was built**. An `absent:` anchor is where an unfailable check hides — a positive anchor that cannot resolve fails loudly, a negative one goes quiet. Malformed module paths are now MALFORMED, never PASS. Reasoning: this commit body (§56.2).

**v1.63 (2026-09-15)** — **§56 RECORD. G-63’s OCCURRENCE CAUSE IS FIXED. ITS ESCAPE CAUSE IS NOT, AND STEP 6.21 IS NOT CLOSED.** **(A) THE FIX.** `_routed_column` returned a `"(not specified)"` placeholder whenever no open ask declared a column; `SHAPES_BY_PHASE["define"]` is `{}` by ruling AR-R2, so in Define that was **every** routed read, not an edge case. It now returns `None`, and `_dispatch_routed_read` takes the column from **two sources and a refusal**: the ask (unchanged, still authoritative), then the file’s own header via new `knowledge/tools.py::first_numeric_column`, and **if neither answers it does not dispatch at all** — a read that can only return `no_such_column` is worse than no read, because the span reports success either way. Declining leaves the upload manifest, which is the pre-6.21 behaviour: degraded, not broken (§4.8). `_COLUMN_UNDECLARED` is deleted. **NUMERIC rather than first**: on the trace’s own file the first column is `date`, which satisfies *“a column the file has”* and none of its purpose, since `load_evidence_series` returns n, mean and sigma. The helper lives in `knowledge/tools.py` because the download, the parse and `_numeric_columns` already do — a parse site in `nodes_common` would be a second answer to *“what columns does this file have”*, the single-authority drift §39.2 names. **948 pass** (941 + 7), mypy clean on both modules, `verify_built.py` 24 checks zero disagreements. **(B) THE ESCAPE CAUSE IS RECORDED, NOT FIXED.** D4 has two halves. The test half is closed — the `xfail(strict=True)` probe asserted on the CONSTANT `_routed_column` returned, testing the source rather than the contract, and seven tests now assert on the DISPATCHED CALL instead, which is what makes them channel-agnostic on 6.18’s precedent. **The telemetry half is open**: the span said `status: "success"` whether or not data loaded, and a routed read that reports its own outcome belongs with **step 8.0**. Carried on the record rather than quietly. **(C) STEP 6.21 REMAINS OPEN.** Its Done-when requires a `live-run` on `IMPR-2026-ED8` in which `load_evidence_series` is called on the named blob path and an upload is stamped `consumed_at`, plus the live halves of **6.7**, **6.12** and **6.13** in the same pass. **None of that evidence exists yet** — the founder is running the turn, and 6.21 closes on a follow-up commit that carries the result. **(D) WHAT IS STILL UNPROVEN.** Whether the coach would have searched anyway had the data loaded. The trace cannot separate it: the tool told the coach to *“Ask the Belt which of those holds the value you need”* and the coach searched instead. That is a second finding about the authority of a node-issued result, it has no evidence independent of this defect, and only the live turn can close it. Reasoning: this commit body (§56.2).

**v1.62 (2026-09-14)** — **§56 RECORD. Step 6.19 closes G-50; §39.1 gains its six missing subsections; G-63 names why the Define turn times out.** **(A) 6.19 — `CoachingResponse` GOES 4 FIELDS TO 8.** `explanation`, `example`, `prompt`, `progress` transcribed from S-C05, not designed here. §50.1's render contract is schema-backed rather than prompt-hoped. `verify_built.py`'s expectation moved 4 → 8 in the same commit as its own comment demanded; 20 test constructions updated; **941 pass**. **The four are REQUIRED `str`, matching the ratified entry** — and that is a founder-visible choice, because §4.8 says *never a hard failure to the Belt* and a model omitting `progress` now fails the turn's structured output rather than rendering an empty block. Defaults would need a §56 amendment, so the ratified shape stands until ruled otherwise. **(B) §39.1.9–39.1.14 APPENDED, 39.1.1–39.1.8 UNTOUCHED.** Define carried eight subsections against the twelve Measure, Analyse, Improve and Control each carry; the six missing were the metric registry, tools bound, conditions, state parameters, metric literacy and cross-phase reads. **Appended rather than interleaved because `§39.1.2` is cited from §56.1** and renumbering resolves a citation silently to the wrong subsection — Appendix D's `Zone`/`Impact` precedent. **Five of the six document what is already built** and cite the owner rather than restating it. **(C) THE 12-vs-13 GATE MISMATCH IS NOT A DEFECT, AND THE AUDIT THAT RAISED IT WAS WRONG.** `metric_definitions` is ratified (§63.8, S-C38), gate-required, and **coached inside position 5** — `SKILL.md` reads `[5 · baseline_estimate · required · also captures metric_definitions]` and *“this one field-ask fills two fields, and the Belt should not have to know that.”* The structure audit's *“the Belt can complete every coached field and still fail the gate”* is withdrawn. **What was true is that the spec never said so**, which §39.1.9 now fixes. **(D) G-63 — THE TIMEOUT'S CAUSE IS NAMED AND NO FIX IS PROPOSED.** Option C's transport works; its ARGUMENT does not. `_routed_column` reads a column off an ask shape Define does not populate, so every Define routed read dispatches `"(not specified)"` and the tool answers `no_such_column`. The coach then searches because it holds nothing. **The framing hypothesis is ruled out as the cause** — there was no result to frame — **and kept as a separate finding** with no independent evidence. **The escape cause is that the span said `status: "success"`**: nothing tells a routed read that loaded data from one that did not. Reasoning: this commit body.

**v1.61 (2026-09-14)** — **§56 RECORD. Housekeeping: G-60 gets a step, G-62 registers a founder ruling on §56.3, and the repository path lands in CLAUDE.md.** **(A) G-60 → STEP 6.29.** *Ruling first, engineering second* had no owner, no deadline and no consequence — the shape *live-run owed* had when four stacked up over six days. A step renders on the board and the cursor reaches it; a sentence does neither. **(B) G-62 → STEP 6.30, A FOUNDER RULING OVERRIDING §56.3.** A gate cannot judge whether a prose claim is true; **it can gate the shape**. A commit body asserting a code fact carries a git-resolvable reference — `path:line` or a sha — and correctness is never judged. **(C) THE WORKED EXAMPLE WAS CORRECTED BEFORE IT WAS WRITTEN DOWN.** The case offered was *“the executor times out at 45s while nothing in the repository enforces any timeout”*. **The timeout IS enforced**: `backend/phases/subgraph_common.py:73` sets `EXECUTOR_RUN_TIMEOUT = 45` and line 129 attaches `timeout=TimeoutPolicy(run_timeout=EXECUTOR_RUN_TIMEOUT)` to the executor node; `verify_built.py` re-runs it as *executor run timeout (§44) 45/45*. **What step 8.2 owns and has not built is the bounded REQUEST timeout** — the HTTP-level one `core/llm.py` names when it removes SDK retry — which is a different timeout at a different layer. **A step whose purpose is to gate unresolvable citations must not open with one**, so the register carries v1.31(C) instead: a claim about what rule 2b did, no reference, wrong, six weeks standing, `ef59aa8` in cost. **(D) THE LIMIT IS RECORDED WITH THE RULING.** It does not catch a citation that resolves and is wrong — §55.2 cited `build_board.py`'s four inputs accurately and drew a false conclusion, and a shape gate passes that unchanged. **(E) THE REPOSITORY PATH IS IN `CLAUDE.md`**, not `CONTINUITY.md`, which is regenerated every commit and overwrites hand edits. Reasoning: this commit body.

**v1.60 (2026-09-14)** — **§56 RECORD. The four loose ends the full-structure audit left unowned are registered: G-59, G-60, G-61, and the D7 coverage limit.** **(A) G-59 — THE OWNERSHIP CHECK MOVES TO THE COMMIT GATE, step 6.28.** Ratified at §55.5 and not built. The `PreToolUse` guard cannot cover Bash, widening its matcher yields a check that cannot fail, and static shell parsing cannot recover content from four of the six write mechanisms measured in one session. **(B) G-60 — SEARCH INDEX SCHEMAS HAVE NO REGISTERED OWNER**, the third of the three unregistered classes and the only one in no gap until now. Hardest of the three because its owner is a live Azure resource rather than a parseable file. Ruling first, engineering second. **(C) G-61 — FOUR DISMISSED HAZARDS GET OWNERS**: §23.3 and §23.2 to step 9.1, §15 to step 7.3, and **§56.3 RULED to stay untested with its reason** — a gate reads the index and cannot read a sentence, so claiming a step for it would claim coverage that cannot exist. **(D) ONE OF THE AUDIT'S OWN FINDINGS IS WITHDRAWN.** §19.6's *“every turn, by construction”* was counted as a dismissed hazard; it sits inside a record of three defects fixed on 2026-08-22 and describes the OLD behaviour. **A diagnosis read as a dismissal** — the list goes five to four, and the correction is recorded rather than quietly dropped. **(E) THE D7 COVERAGE LIMIT IS WRITTEN BESIDE THE CHECKS IT QUALIFIES**, in §56.0, so the audit result cannot be read as stronger than it is: 15 claims plus 24 checks plus one spot-check, not a line-by-line diff of thirteen files. **RULED: no sweep, no step** — G-55's ruling applied to the same shape, with the ratchet standing and a revisit at 11.2. **(F) G-59 WAS NAMED IN CONVERSATION BEFORE IT EXISTED.** The write-path work was discussed as *“G-59”* while no such row existed; that finding is §55.5 and needs no gap, and the number is now spent on the unbuilt half. Reasoning: this commit body.

**v1.59 (2026-09-14)** — **§56 AMENDMENT. THE COMMIT GATES GOVERN; THE THIRTEEN RULE FILES ARE ADVISORY CONTEXT. §55.5 ratified, and three places that implied the reverse are corrected.** **(A) MEASURED, NOT ASSUMED.** `.claude/logs/instructions-loaded.log` holds **six records across two days** of heavy editing — one `session_start` and five `path_glob_match`. Probed four ways on files under live globs: **Write no, Bash no, Edit no, Read yes** — the Read delivering both matching rule files in full. The Edit was NOT refused for lacking a prior read, so this is not `Read`-always-precedes-`Edit`. **Path-scoped rules are delivered on READ.** **(B) WHAT WAS WRONG.** §55's mechanism table listed the constitution under *Enforces* as *“the rules, quoted in every implementation prompt”*; §56.0.1 said a rule *“must load when that code is opened”*. **Opened is the word the measurement contradicts** — written is not opened. Both corrected, and the table now names the rule files alongside the root rather than leaving them implied. **(C) THIS IS NOT A DEFECT TO PATCH.** A rule that must hold whether or not anyone read it belongs in a gate; a rule that teaches or bounds a judgment belongs in a rule file and earns its place even when it loads late. **What stops is writing a rule file as though it were a control** — §55's own shape, a correct mechanism paired with a document claiming more for it than it does. **(D) RULE DELIVERY AT WRITE TIME IS AVAILABLE AND LANDS ONE STEP LATE.** A `PreToolUse` hook returning `hookSpecificOutput.additionalContext` **does** reach the model — probed with a throwaway hook registered in the gitignored `settings.local.json`, which took effect **without a session restart**. It arrives WITH the tool result, after the write it fired on, so it informs the correction and never prevents the edit. **Only `permissionDecision: deny` prevents.** The probe carried a log line written unconditionally, so a negative result could be told apart from a hook that never ran; the observed envelope carries eleven keys including `cwd`, `permission_mode` and `transcript_path`. **(E) THE BASH BYPASS IS REPORTED AND DELIBERATELY NOT FIXED** — both `PreToolUse` guards match `Write|Edit|MultiEdit` and read `content` / `new_string`, fields a Bash call does not carry. Widening the matcher without a shell-parsing path in `extract()` yields a guard that always passes: **a check that cannot fail, recorded as coverage**, which CONTINUITY §7 names as worse than no check. Reasoning: this commit body.

**v1.58 (2026-09-14)** — **§56 AMENDMENT. The board's cause is corrected: it was not an oversight and not a violated exclusion — it was a RATIFIED argument that was false on its face. Plus G-58, and the mutation-restore rule gets a number.** **(A) WHAT v1.57 AND `258d0dd`'s 8D GOT WRONG.** Both state the occurrence cause as *a derived artifact was placed on a source-of-truth list* — which reads as an oversight. **§55.2 ratified it deliberately**, named it *“the only watched path that is GENERATED rather than authored”*, and argued the hazard away: *“it carries no wall-clock date, and that is load-bearing … a guard that fires for nothing is one people route around.”* **The section identified the exact failure mode it was about to cause, attributed it to the wrong mechanism, and cleared the entry.** That is a worse cause than an oversight and a different one: **review did not miss this; review considered it and got the arithmetic wrong**, because `build_board.py` takes git log as one of four inputs and git log moves unconditionally. **(B) A CORRECTION TO THE CORRECTION, RECORDED RATHER THAN ACCEPTED.** The amendment was requested against *§42, the generated-file exclusion, ratified 2026-09-12*. **No such ratification exists.** §42 is *Cross-phase reference fields in practice*. The only exclusion naming `board.html` verbatim is `governed_exclusions` in `.claude/config/fact_owners.yaml`, added **2026-09-13** (v1.47(E)) and governing the **fact-ownership guard**, not rule 2b — two days AFTER the board joined 2b on 2026-09-11, so there was nothing to violate. The cause above is what the tree supports. **(C) v1.31 IS THE ESCAPE CAUSE, AND IT IS SHARPER THAN THE ONE RECORDED.** v1.31(C), dated the day the board was added: *“Rule 2b blocked the commit adding rule 6 … a watched path staged without this file is exactly what 2b exists to stop.”* **It was not — it was the board being regenerated.** The first false trigger fired immediately and was written into the changelog as the rule working. From inside the hook, *the board changed* and *the status changed* are the same observation. **(D) §55.2 IS CORRECTED, AND IT WAS WRONG FOR THREE COMMITS.** `258d0dd` removed the board from the guard and left §55.2 tabulating it, so the document said thirteen and the gate enforced twelve. **The fix for a drift created a fresh instance of the same drift**, which is the argument for (E). **(E) G-58 AND STEP 6.27 — ONE FACT, ONE OWNER, ENFORCED.** An equality test now asserts §55.2's fenced block and `STATUS_WATCHED` state the same set, normalising `middleware/**` against `middleware/` because they are one entry in two notations. Both mutation directions fail. **(F) THE MUTATION-RESTORE RULE IS NOW PROCEDURE §0.4, NOT A THIRD CHANGELOG ENTRY.** Never restore a mutation with `git checkout --`: it restores from HEAD, and while the fix is uncommitted — which is exactly when mutation proofs run — that reverts the fix and leaves every later mutation running against the old code. Copy a baseline OUTSIDE the tree and restore from that, and **read which test failed, never the count**, because a reverted fix also produces `1 failed`. **Three instances now**: v1.49(D), the `git checkout --` revert during `258d0dd`, and a third caught while proving 6.27 — a document mutation whose string did not match, which reported a clean pass until the file was checked for having actually changed. **(G) A TEST OF MINE WAS A FALSE-ALARM GENERATOR AND IS FIXED WITH IT.** `test_the_registers_are_read_from_the_INDEX_not_the_disk` compared byte counts between index and disk, which are equal only in a clean tree — so it went red on any working copy with an unstaged procedure edit. It now asserts the SOURCE. Same class as the defect this entry is about: a check that fires for a reason unrelated to what it checks. Reasoning: this commit body.

**v1.57 (2026-09-14)** — **§56 AMENDMENT. A WATCHED PATH MUST BE A SOURCE OF TRUTH, NEVER THE OUTPUT OF A GENERATOR. `docs/board.html` leaves rule 2b's watch list.** **(A) THE RULE FIRED ON EVERY COMMIT.** `build_board.py` regenerates the board during pre-commit from Appendix D, the BUILT markers, §66 and **git log** — and git log moves on every commit. Worse, the hook runs BEFORE the commit it is part of exists, so the board permanently **lags one commit** and spends each commit catching up with the previous one. Rule 2b therefore demanded an `ARCHITECTURE.md` edit on every commit, whether or not any architectural fact had changed. **(B) [CAUSE CORRECTED 1.58 — SEE BELOW; THIS ENTRY'S ORIGINAL (B) AND THE 8D IN `258d0dd`'s BODY STATE A SHALLOWER CAUSE THAN THE TREE SUPPORTS]** **THE ENTRY'S OWN COMMENT ARGUED THE OPPOSITE AND WAS WRONG WHEN WRITTEN**: *“It carries NO wall-clock date precisely so that it changes when, and only when, one of those four sources does.”* True as stated, and self-defeating — **git log IS one of those four sources, and it is the one that moves unconditionally.** Removing the date removed a clock and left a counter. **(C) WHAT IT COST IS ON THE RECORD.** `ef59aa8` — a `fix(ops)` commit touching only `start.ps1` — was blocked by 2b, and carries a §56 entry (v1.56) written for no reason except to satisfy the gate. That entry is left standing rather than rewritten: **it is the evidence**, and deleting the cost of a false trigger is how the next one goes unnoticed. **(D) THE WHOLE LIST WAS TESTED, NOT JUST THE OFFENDER.** All thirteen entries checked for derivation and for existence: **twelve are hand-written source, all present and tracked; one was derived.** Every generator in the repository was enumerated from the hooks rather than guessed — `build_board.py` writes `board.html` whole, and `pre-commit-continuity.py` splices blocks into `CONTINUITY.md` and `REFACTORING_PROCEDURE.md`; **neither of those two is watched, so the board was the only breach.** `gateway/routes.py` tripped a content scan for the word *generated* and is a false positive — it is a user-facing error string, and that is exactly why the invariant is pinned as DATA rather than inferred from file content. **(E) THE BOARD IS NOT LEFT UNGUARDED.** `verify_built.py` re-runs the counts behind it, which is the check appropriate to a projection: **a derived file is verified by REGENERATING it and comparing**, never by asking whether someone remembered to touch a different file in the same commit. **(F) BOTH DIRECTIONS DEMONSTRATED, AND THE SECOND IS THE ONE THAT MATTERS.** A code-only commit whose board regenerated now PASSES without `ARCHITECTURE.md`; `core/state.py`, `middleware/grader.py` and `gateway/routes.py` each still BLOCK without it, and pass with it. **(G) THREE TESTS, EACH PROVEN TO FAIL** — no watched path is a generator's output, every watched path exists, and the list still has at least ten entries so a correction cannot become a deletion. Re-adding the board fails the first; watching a nonexistent path fails the second; gutting the list fails the third. Reasoning: this commit body.

**v1.56 (2026-09-14)** — **§56 RECORD. `start.ps1` lost its path separators, and never set its own directory.** **(A) THE MANGLING WAS REAL, AND THE CHECK WAS THE POINT.** Line 10 read `..venvScriptsActivate.ps1` — **zero `0x5C` bytes**, verified by reading the file as bytes rather than through any layer that interprets a backslash. **The hypothesis tested first was that it was a rendering artefact**, and had the separators been present this would have been recorded as a false positive with nothing committed. Now `.\.venv\Scripts\Activate.ps1`, three separators confirmed in the bytes after the write. **(B) THE SECOND DEFECT IS INDEPENDENT AND WORSE.** The script set no working directory. `StaticFiles(directory="ui")` at `backend/app.py:65` is relative, so a wrong cwd starts the backend and serves no UI — **a silent failure that looks like success**. But the same script runs `git reset --hard origin/main`, which is equally relative: run from another repository's folder it would have hard-reset **that** repository. `Set-Location $PSScriptRoot` is therefore line 1 and not merely somewhere above uvicorn. **(C) THE ESCAPE IS THAT NOTHING READS THIS FILE.** Not Python, so rule 3's mypy pass does not see it; no test parses it; and it cannot be exercised by hand because it hard-resets the working tree. **A destructive script is the least tested file in a repository precisely because it is destructive.** **(D) A PARSE CHECK WOULD NOT HAVE CAUGHT IT**, which is recorded rather than glossed: `..venvScriptsActivate.ps1` parses cleanly as a command token naming a file that does not exist. Catching the mangling needs a resolve-the-path check, not a syntax check — noted here rather than built inside a fix commit. Verified not run: the script was parse-checked with `Parser::ParseFile` (0 errors) and never executed. Reasoning: this commit body.

**v1.55 (2026-09-13)** — **§56 RECORD. Step 6.26 — G-57 CLOSED. The two rules that guard the tree stop being demonstrated and start being re-run.** **(A) THE GAP.** Rules 7 and 8 landed with ten hand-run cases and nothing that re-ran them. **A demonstration proves a rule worked once**; `test_commit_guard_8d.py` already states why that is not enough — *a message check fails SILENTLY by letting commits through* — and the argument transfers to an index check without a word changed. **(B) IT TRANSFERS WITH TWO EXTRA FAILURE MODES.** A scratch pattern that stops matching reports nothing. And rule 8 resolves numbers by parsing two tables it does not own: **it is the fourth hook parsing Appendix D and the second parsing §66**, and both carry format warnings in their own headers because of the readers that came before. A regex that stops resolving after a reformat would let every new file through while reporting success. **Two assertions therefore go red on a REFORMAT rather than on a rule change**, which is a different job from the rest of the file. **(C) WHAT IS PINNED IS WHAT THE RULES RANGE OVER**, not only what they match — the ratchet, the rename into a scratch name, the index-versus-disk read, and resolution. The false-positive side is pinned too, with `scratchpad_tools.py` as the named case: the word is in the NAME and not in a directory segment, and a rule that blocked it would be routed around within a week. **(D) THE MUTATIONS ARE RECORDED WITH THEIR RESULTS**, because a suite nobody has seen fail is a suite nobody has tested. Emptying `SCRATCH_SEGMENTS`: **8 failed, 33 passed**. Pointing the Appendix D regex at `**Step X.Y**`, a shape the table does not use: **1 failed, 40 passed**. Dropping the filter from `AR` to `A`: **1 failed, 40 passed**. Each was restored from git rather than by hand, so the mutation could not survive its own proof. **(E) ONE ASSERTION GUARDS THE RATCHET'S REASON RATHER THAN ITS CODE.** The exemption for modified paths exists because two `.bak` archives are tracked deliberately under `docs/_archive/`; a test asserts those files still exist, so if they are ever removed the suite says that the stated reason for the exemption is gone. **A rule whose justification has silently expired is the shape §55 keeps finding.** **(F) WHAT IS DELIBERATELY NOT PINNED** is whether a file genuinely belongs to the step it declares. `Step: 2.3` on an unrelated file passes. The limit is in `check_step_or_gap`'s docstring and restated in the test file, so a green suite is not read as evidence the numbers are honest — the same discipline rule 6's suite carries about the correctness of an 8D answer. Register: 57 identified, nineteen closed, 38 open. Reasoning: this commit body.

**v1.54 (2026-09-13)** — **§56 RECORD. Step 6.25 — scratch leaves the tree, sorted by CONTENT rather than by folder.** **(A) THE CONDITION.** Two working folders sat untracked INSIDE the tree — `_Artifacts/` at the root and `agent-improve/_Claude_chat_Prompts/` — and `docs/_archive/response-to-audit-2026-08-19.md`, a tracked document, cited a file in each. **A citation from a tracked document to an untracked file resolves for whoever has the folder on disk and for nobody else**, which is §55.1's bidirectional rule failing in the direction nothing checks. §0.32 clause 2 names the remedy and this step applies it. **(B) THE IGNORE RULE THAT WAS MEANT TO COVER ONE OF THEM MATCHED NOTHING.** `.gitignore` carried `ARTIFACTS/`; the directory is `_Artifacts/`. **An ignore rule that matches nothing fails the same silent way a rule file's `paths:` glob does** — the failure recorded at v1.41(D), now found a second time in a different file. `agent-improve/.gitignore` did carry `_Artifacts/`, scoped to a directory where no such folder exists, which is why the typo survived: a correct-looking rule in the wrong place beside a wrong rule in the right place. Both are now matched, proven with `git check-ignore -v` rather than by reading the file. **(C) THE SORT IS BY CONTENT, AND THE FOLDER IS NOT THE UNIT.** Twelve files, two outcomes: the two a tracked document cites moved to `docs/_archive/` and are tracked; the eleven nothing cites moved OUTSIDE the tree and are kept, because clause 2 says outside and never says deleted. **(D) REDACTED ON THE WAY IN, BECAUSE THIS REPOSITORY IS PUBLIC.** Checked rather than assumed: an anonymous `GET api.github.com/repos/vpangalis/agentlean` returns 200. The handover's identifiers were then tested against what the tracked tree ALREADY contains, and three were new — a storage account name and two contact addresses — so those three are redacted and everything else is left as the historical record. **A file that was safe as working material is not automatically safe as a published one**, and the test is the difference, not a general feeling of sensitivity. **(E) THE PAT WAS ALREADY HANDLED AND THE FILE'S CLAIM ABOUT ITSELF WAS NOT.** The credential was redacted on 2026-08-20 while the file was untracked, so it never entered git history and tracking it now cannot put it there. But the file's own security note ended *“This file is untracked”* — **a claim about a file's own location, which tracking it falsifies** — and it is corrected in the same commit that moves it. §0.32's first clause makes that claim checkable for the first time. **The revocation item still stands**: redacting a token does not revoke it, and the archive document's instruction is left in force rather than quietly closed. **(F) STEP 6.26 IS REGISTERED WITH IT** — G-57's test suite, so the two rules that enforce §0.32 stop being demonstrated and start being re-run. Reasoning: this commit body.

**v1.53 (2026-09-13)** — **§56 AMENDMENT. §0.32 — THE TREE AT HEAD IS THE ONLY SOURCE OF TRUTH, and two of its three clauses are gated at the commit.** **(A) THE CLAIM CLAUSE.** A claim about a file's content is made against that file at its repo path, read at the time of the claim — never a cached copy, a snapshot, a draft, a scratchpad, or a synced mirror. **The mirror is the sharpest case and it is not hypothetical: this tree lives inside OneDrive, and `.claude/` does not appear in that mirror at all.** From a seat reading the mirror, the rule files, the hooks and the skills read as absent — a governance layer that looks machine-local while being tracked and pushed. **Checked rather than assumed before the rule was written**: `git ls-files .claude/` names 37 files, `git ls-remote origin main` returns the same commit as HEAD, and the only untracked paths under `.claude/` are `__pycache__/`, `logs/` and `settings.local.json`. **A source of truth you can be wrong about without noticing is not one**, so the test is a git command and never a directory listing. **(B) THE SCRATCH CLAUSE, GATED AS RULE 7.** Scratch lives outside the tree, is never committed, and is never evidence. The guard refuses a commit staging a path NEW to the tree whose NAME is scratch — a `scratch/` or `_drafts/` segment, a `.bak`/`.tmp`/`.old` suffix, an Office `~$` lock file, a OneDrive `conflicted copy`. **The pattern list is not hypothetical either**: `_Artifacts/` and `_Claude_chat_Prompts/` sit untracked in this tree today, and `.gitignore` already calls `ARTIFACTS/` “not part of the repo” while spelling it in a case the working directory does not use. **It reads the name, never the content** — a draft called `notes.md` passes, which is `check_8d`'s limit restated one rule along. **(C) THE NUMBER CLAUSE, GATED AS RULE 8.** A new file in the tree needs a step number or a gap number. A spine subject declares its own; any other type carries `Step:` or `Gap:` in the body, and the number must RESOLVE — Appendix D for a step, §66's register for a gap. **Both registers are read from the INDEX rather than from disk**, which is clause one applied to the guard's own reading: a commit that registers a gap and adds the file that gap schedules must pass, and only the index holds both halves. §66's own words carry the reason — *a gap without one does not render on the board and so is not scheduled by anything* — and a path with no number is that same condition one level down. **(D) BOTH ARE RATCHETS, NOT WALLS**, on rule 3's argument. They range over paths NEW to the tree and never over a modification, because two `.bak` archives are tracked deliberately under `docs/_archive/` and a rule reading every staged path would block every commit that touched one. **A guard people route around with `--no-verify` is worse than no guard.** Neither carries a soft opt-out, unlike rule 6's `8D: NOT A FIX`: that opt-out exists because trigger 2 fires on a MENTION and can be wrong about what a commit is, where these two fire on the index, which cannot. **(E) PROVEN TO FAIL, NOT ONLY TO PASS.** Staging `docs/scratch/notes.md` and `docs/PLAN.md.bak` gives exit 1 naming both paths AND the pattern that caught each. A new document with no trailer gives exit 1. `Step: 99.9` and `Gap: G-999` give exit 1 as unresolvable — **a number that resolves nowhere schedules nothing, so it is refused like none at all.** `Step: 6.22` and `Gap: G-52` pass. A spine subject passes both and is stopped by rule 5 instead, which is the correct handoff. **(F) CLAUSE ONE CANNOT BE GATED, AND THE RULE SAYS SO RATHER THAN IMPLYING COVERAGE.** A gate sees the index; it never sees a sentence. A claim sourced from a stale copy passes every hook in this repository and is caught only by the reader who resolves the citation, which is what §20.5.1 already requires. **G-57 is registered for the other half**: rules 7 and 8 are demonstrated and untested, where rule 6 carries a test suite because a message check that stops matching fails SILENTLY, by letting commits through — and that argument transfers to an index check without a word changed. **(G) THE RULE WAS EXERCISED ON ITSELF WHILE BEING WRITTEN.** A concurrent session landed two commits and a working-tree edit into this file mid-amendment; the version line read 1.49 when this entry was drafted and 1.51 when it was written. **The draft was discarded and the file re-read at its path**, which is clause one, and is the reason this entry is v{NEW}. **No rule was renumbered**, so `deprecated_patterns.yaml`'s citations still resolve and §0.2 holds. `/verify-current-version` returns nothing to check — this amendment introduces no framework API, the guard using stdlib `re`, `fnmatch` and `subprocess` over git plumbing — recorded per §16.3 rather than skipped. Reasoning: this commit body.

**v1.52 (2026-09-13)** — **§56 RECORD. The comment tail of v1.49's rename.** `backend/phases/nodes_common.py` and `backend/tests/test_executor.py` each name the stubbed middleware test in a comment; the rename to `test_the_declared_middleware_list_is_the_ratified_layering` reached them after `2e17f3f` was staged. Comments only — no code, no assertion, no behaviour. **Nothing this document states changed and that was checked rather than asserted**: `verify_built.py` reports 24 checks and zero disagreements, *middleware mounted* 8/8 among them. Rule 2b brought this file in because `nodes_common.py` is a watched path, which is the rule working as intended on a change that turned out to be harmless.

**v1.51 (2026-09-13)** — **§56 AMENDMENT. G-54's rule gains its corollary: introspection settles MEMBERSHIP, never ORDER or BEHAVIOUR.** **(A) THE CLAUSE.** `vars()` and `inspect.signature()` answer one kind of question — *is this name there, and what does it take*. They are silent about *what happens first*, *what happens when this raises*, and *how these compose*. **An entry claiming an ORDER is settled by a runtime test that exercises the path and observes what happened, not by a signature** — and **until such a test exists the entry is marked as resting on a page, not verified.** Marking it is a RESULT; leaving it looking verified because the classes exist is the C-3 failure with a different surface. **(B) E-2 IS THE WORKED EXAMPLE.** It claims retries decide first and `error_handler` runs only after they are exhausted. `RetryPolicy` exists and carries `max_attempts` — and none of that settles the claim. What would: a test that raises inside a node and counts attempts before the handler fires. E-2 is therefore the one entry in `BIBLE_VERIFICATION_LOG.md` still marked as resting on a page, and it says why. **(C) §19'S MIDDLEWARE ORDER IS THE SAME SHAPE, SETTLED THE OTHER WAY — WHICH IS WHY G-52 AND G-54 ARE ONE LESSON FROM TWO ENDS.** No amount of `vars()` could establish that `after_*` fires innermost-first. Until 2026-09-13 the only proof was a test that reversed the declared list and compared it with itself; `test_middleware_execution_order.py` now invokes the real compiled graph and observes 8 → 7 → 6. **G-54 is the case where the runtime test does not exist and the entry says so. G-52 is the case where it was owed and has been written.** **(D) WHERE THE CLAUSE LIVES.** The `verify-current-version` skill, beside the rule it bounds, because that is what a person reads while running the check; step 6.23's spec, because it bounds step 1 of that step's method; and E-2 itself, which names the clause it is the example for. Reasoning: this commit body.

**v1.50 (2026-09-13)** — **§56 RECORD. G-54 CLOSED — every entry in the verification log carries a `Source method` row, and every claim with an installed object has been re-run against it.** **(A) ALL NINE, NOT A SAMPLE.** C-1 `retries` absent / `max_retries` present; C-2 `prompt` absent / `system_prompt` present; C-3 withdrawn on `vars(AgentMiddleware)`; S-1 partly withdrawn, two of three reasons stand; S-2 installed 1.2.11 / 1.3.16 / 1.0.8; E-1 `set_node_defaults` present on `StateGraph`; E-3 `TimeoutPolicy` carries `run_timeout`, `idle_timeout`, `refresh_on` — and `refresh_on`, which the entry never mentioned and which is how `idle_timeout` learns progress happened. **(B) NO VERDICT MOVED, SO NOTHING PROPAGATED.** The two entries that were wrong — C-3 and S-1 — had already been caught and corrected; the remaining five were right, and are now grounded in the object rather than the page. **A pass that changes no conclusion is still the pass that lets you rely on them**, which is the difference between a verdict and a verdict you can cite. **(C) TWO ENTRIES ARE NOT SETTLED BY INTROSPECTION AND SAY SO.** **E-2** claims an ORDER — retries decide first, `error_handler` runs only after they are exhausted. Both classes exist and `RetryPolicy` carries `max_attempts`, but **an order is behaviour, not a signature**, and a runtime test that raises inside a node and counts attempts before the handler fires is what would settle it. Marked as the one entry whose verdict still rests on the page, rather than marked verified on the strength of the classes existing. **E-4** is about which posts an external index has published — there is no installed object, a page is the RIGHT source, and it is marked so a future pass does not hunt for one. **(D) S-2 IS SUPERSEDED A SECOND TIME, AND BETTER.** Since §55.4 this class of fact has an owner: `agent-improve/requirements.txt`. A verification-log entry recording pins is a copy; the pin lives in the manifest and the floor in the documents. The entry now says it should not be cited for a version again. **(E) THE `Source method` COLUMN IS THE COUNTERMEASURE, NOT THE RE-VERIFICATION.** Its two starting values are `introspection — <the expression>` and `documentation page — NOT RE-CHECKED`, and **the second is a finding rather than a placeholder** — an unverified entry can no longer look like a verified one. Reasoning: this commit body.

**v1.49 (2026-09-13)** — **§56 RECORD. G-52 CLOSED — the middleware stack's ordering is OBSERVED on a real graph at last, and the test that claimed to do it is renamed for what it actually checks.** **(A) THE NEW TEST.** `backend/tests/test_middleware_execution_order.py` builds the stack through the REAL `_build_executor()` and invokes the compiled agent, recording which hooks fire: `after_agent` **8 → 7 → 6** — contradiction, coherence, grader — and `before_agent` **1 → 2**. Both clauses on one run, because they are OPPOSITE and a test seeing only one could not tell the difference. **No network**: the defect is in the graph LangChain builds at construction time, so `GenericFakeChatModel` suffices, and G-53 means a live model is not reliably available anyway. A third assertion checks that hooks fired AT ALL — otherwise the first two would pass vacuously on empty lists, which is the G-52 shape reappearing inside its own fix. **(B) THE RENAME IS THE OTHER HALF.** `test_all_eight_positions_execute_in_the_ratified_order` observed no execution: `stub_coach` replaces `create_agent`, so it asserted `reversed(declared)` — the rule compared with itself. It is now `test_the_declared_middleware_list_is_the_ratified_layering`, which is a real and useful property. **The name was the part that lied**, and a name claiming more than the body delivers tells the next reader the ground is covered. Dated changelog entries keep the old name, because they record what the test was called when they were written. **(C) THE DONE-WHEN'S DEMONSTRATION DID NOT HOLD, AND THE STEP RECORDS WHY RATHER THAN SWAPPING IT QUIETLY.** It specified *"reversing positions 6 and 8 makes the new test fail while the stubbed one still passes"*. **Both fail** — the stubbed test asserts `reversed(declared)`, so reversing the declaration breaks it too, and the mutation separates nothing. What separates them is a mutation the DECLARED LIST cannot see: removing position 8's `after_agent` and `aafter_agent` while the class stays in `middleware=[...]` gives **stubbed 5 passed, new 2 failed**. **(D) THE FIRST ATTEMPT AT THAT MUTATION WAS ITSELF WRONG** — disabling only `after_agent` left `aafter_agent` overriding, the middleware still fired, and the new test passed. **A mutation that does not do what you think produces a green result that means nothing**, which is the same trap one layer down and is why the mutation is recorded with its verification. **(E) WHAT THE STUBBED TEST GENUINELY CANNOT CATCH** is LangChain changing its composition semantics: it asserts our BELIEF about reversal rather than verifying it. That cannot be demonstrated by editing this repository, which is why (C)'s mutation is the evidence offered instead. Reasoning: this commit body.

**v1.48 (2026-09-13)** — **§56 AMENDMENT. The amendment procedure is reconciled with the topology the September refactor produced, and §56 was stale about ITSELF in two places.** **(A) STEP 1 NAMED A DESTINATION THAT TAKES NO ENTRIES.** It routed every ruling to `docs/_archive/DECISIONS.md`, archived on 2026-09-10. **(B) STEP 4 DESCRIBED THIS FILE'S OWN STRUCTURE, WRONGLY.** It said *"this document has no change-log section, by design"* — while this document has carried one at its head since v1.0 and every amendment of the September pass was written into it. **A procedure that describes a file's structure is a copy of a fact the file owns, and it went stale exactly the way every other copy in this repository did.** Step 4 also required a numbered `§0.x` entry in `CLAUDE.md`; §0's change records moved to `docs/_archive/` at brief step 5 and the root carries a version line and nothing else. **(C) THE PROCEDURE NOW HAS SIX STEPS AND ACCOUNTS FOR WHAT EXISTS**: the ruling lands here with a §56 entry and a version increment; the rule change lands in the file that HOLDS the rule — the root or one of thirteen under `.claude/rules/`; the registry is updated in the same commit if it cites the number; **the enforcement column of §55.4 is CHECKED rather than assumed, because enforcement is not uniform across the five owners**; reference material is amended in the skill that holds it rather than added back to the root; and the body states occurrence and escape. **(D) §56.0 — WHAT CHANGED WHEN THE RULES STOPPED BEING ONE FILE.** A rule number now resolves in fourteen places. Moving a rule between files is safe, since the number travels with it; **renumbering is what breaks silently**, and there are fourteen places for the break to hide. Three checks stand behind the topology and each answers a different question — citations resolve, `paths:` globs match, owned facts agree. **(E) §56.0.1 — RULE, REFERENCE, OR OWNED FACT.** An amendment goes wrong most often by putting the right content in the wrong place, so the test is what KIND of thing it is: a rule binds on code and goes where that code's `paths:` reach; reference goes to the task's skill; **a value some file owns goes nowhere — cite the owner.** **(F) THE CHECK THIS SECTION PRESCRIBES WAS BUILT, AND ITS FIRST TWO CUTS WERE WRONG.** `verify_rule_citations.py` reads only `message:` fields, because a §-number in a YAML comment is prose about history — a whole-file grep called `§18.1` dangling when the comment beside it explains its retirement. And it resolves **three namespaces** against three corpora: `CLAUDE.md §x`, `Reference §x`, `EDUCATIONAL §x`. A checker that assumed one reported six false failures on its first run. **A prescribed command that cries wolf is worse than no command, because it is written into governance.** Proven to fail: renumbering a cited rule to `§8.99` gives exit 1 naming it. Reasoning: this commit body.

**v1.47 (2026-09-13)** — **§56 RECORD. The ownership guard reads the dependency-versions row at last, and G-56's Done-when passes on all four clauses.** **(A) THE GAP.** The guard built its symbol table only from `owner.get("symbols")`. `dependency-versions` declares no symbols — it declares `symbol_source: requirements`, because **the package names ARE the symbols** — so the guard read nothing for it and **a version pin written into a governing document went undetected.** That is the exact class that put a false BLOCKER into §16.1 and §53 and left it there three weeks. Found by testing step 6.24's Done-when clause by clause rather than by assuming a passing check passes. **(B) A FLOOR IS NOT A PIN, AND THAT DISTINCTION IS THE RULE.** §55.4 puts the floor in the documents deliberately — `langgraph >= 1.2.6` is a rule and belongs where rules live — and the pin in `requirements.txt`, which owns it. So `>= 1.2.6` PASSES and a bare `1.2.11` beside the same package name is denied. **(C) ONLY THE CURRENT PIN IS A RESTATEMENT.** `langgraph 1.1.10 → 1.2.11` records a migration and names a version that is no longer the pin; nothing can drift out of a fact about the past. A dated line is likewise a record — *"Introspected against `langgraph` 1.2.11 on 2026-09-12"* is EVIDENCE, the G-54 discipline working, and the date is looked for on the preceding line too because a record is a sentence and a sentence wraps. **(D) MEASURED BEFORE ENFORCED, WHICH IS NOW THE HABIT.** A 40-character proximity window reported **82** claims across four documents, nearly all step numbers sitting near a package name; adjacency of three characters plus the current-pin test brought that to **4, every one genuine** — and **four of them were written this week, by the session that built the guard.** All four are corrected to cite `requirements.txt` rather than restate it. **(E) `CONTINUITY.md` AND `board.html` ARE EXCLUDED.** Both are generated on every commit and never hand-edited, so guarding them would deny an edit nobody makes by hand and block the pre-commit hook that writes them. **(F) G-56 IS STILL OPEN** — its remaining condition is a ruling, not an engineering problem: gate tier splits and tool inventory. Reasoning: this commit body.

**v1.46 (2026-09-13)** — **§56 RECORD. The seven skills exist, and the root file loses the two references that were carried in every session and opened in almost none.** **(A) SEVEN SKILLS, ALL UNDER THE 500-LINE BUDGET** — `eight-d` 115, `verify-current-version` 239, `upgrade-langchain-stack` 89, `refactor-step-review` 77, `add-computation-tool` 71, `change-gate-schema` 68, `reconcile-docs` 58. Directory name is the command; every `name:` matches its directory and every description says WHEN to reach for it rather than what it contains, because a description that does not name the trigger is a skill nobody invokes. **(B) THE BRIEF WAS STALE ON TWO OF THEM.** It records `verify-current-version` and `refactor-step-review` as slash commands to be converted. `.claude/commands/` does not exist; `verify-current-version` was **already a skill** at 203 lines and was extended rather than converted, and `refactor-step-review` existed nowhere and was written. **(C) WHAT LEFT THE ROOT FILE.** §20.1's D0–D8 table and §20.4's enforcement contract moved to `eight-d`; §16.3's worked reason — the `create_agent` regression whose deprecation notice pointed at a function that did not yet exist — moved to `verify-current-version`. **The rules stay in the root and bind always; the references load when someone is actually working a defect or an upgrade.** Root: 296 → 270 lines. **(D) THE SKILLS CARRY THIS PROJECT'S OWN SCARS, NOT GENERIC ADVICE.** `add-computation-tool` leads with the 16-tool cap because Measure sits nearest it and the answer to a breach is a placement rather than a higher ceiling. `change-gate-schema` ends on `computation_results` and `phase_metrics` — read by all five gate assemblers and written by nothing — because that is what half-landing looks like here. `upgrade-langchain-stack` leads with the venv trap that produced a false blocker in two documents. `refactor-step-review` asks of any check offered as proof: *what edit makes this go red?* Reasoning: this commit body.

**v1.45 (2026-09-13)** — **§56 RECORD. Three more rows join §55.4's ownership table — middleware order, coaching content, banned patterns — and each was RECORDED rather than decided.** **(A) NOTHING HAD TO CHANGE, WHICH IS THE ARGUMENT.** The factory has owned the middleware order since step 6.5, `skills/` has owned the coaching scripts since step 8, and the registry has always owned its own entries. Ratifying them cost an afternoon where the first two rows cost a week — **because by the time the files made the answer obvious, there was nothing left to argue.** That is the case for ruling a row when the vertical work next touches it rather than in the abstract. **(B) ENFORCEMENT IS NOT UNIFORM AND THE TABLE NOW SAYS SO.** Dependency versions and schema fields are enforced by the guard and the drift check. **Middleware order** is enforced by `verify_built.py`'s *middleware mounted* check and by `test_all_eight_positions_execute_in_the_ratified_order` — both already running. **Banned patterns** by the rule-number resolution sweep, which caught §18.1 at step 7. **Coaching content** by CONTAINMENT in the drift check: a governed document carrying a verbatim run of a phase script has copied it, and nothing else would notice step 8 being undone. **(C) A PROSE-COUNT CHECK WAS BUILT FOR TWO ROWS AND THEN DELETED.** *middleware* and *pattern* appear **164 and 122 times** in two governed documents as ordinary English, and the matcher fired on `### 19.9 Middleware deliberately NOT used` — a heading number — and on *"step 6.3 shipped two middlewares"*, which is true. Both facts were already checked against the tree, so the second check would have added false positives to something that already passes. **A row can be owned without every claim about it being mechanically comparable.** Pretending otherwise is how a check gets switched off — the same lesson the drift check itself took three cuts to learn. **(D) THE CONTAINMENT CHECK IS PROVEN, NOT ASSERTED.** One line of `dmaic-define-phase/coaching_script.md` pasted back into this document takes the drift check to exit 2 naming the file and the phase; removing it returns exit 0. **(E) TWO ROWS REMAIN UNRULED BY DECISION, NOT BY OVERSIGHT** — gate tier splits and tool inventory. They are left for the vertical refactor to settle in the file. Reasoning: this commit body.

**v1.44 (2026-09-13)** — **§56 AMENDMENT. The ownership minimum is ratified at TWO rows, encoded as data, and enforced by two hooks — the countermeasure G-56 names.** **(A) TWO ROWS, NOT EIGHT.** §55.4 ratifies `requirements.txt` as the owner of every dependency pin and the floor, and the schema modules — `core/state.py`, `core/substate.py`, `phases/*/schema.py` — as the owner of state and output field names, counts and types. CLAUDE.md's *Facts have one owner* table lists eight classes; the other six are intent until ruled, and **a guard enforcing an unratified row is a guard nobody trusts.** **(B) THE REGISTRY STORES NO VALUES.** `.claude/config/fact_owners.yaml` names each owner and says HOW TO DERIVE its value; it holds not one count. A registry of owned values would be the ninth copy of every fact it governs — this section's own failure mode, rebuilt inside its countermeasure. Both hooks derive at check time, in the pinned venv, through one shared module so they cannot disagree. **(C) TWO HOOKS, TWO JOBS, AND THE DIVISION IS THE POINT.** `fact-ownership-guard.py` (PreToolUse) denies a NEW restatement; `drift-check.py` (Stop, and runnable in CI) catches an EXISTING one that has gone stale. The guard cannot reach backwards — every restatement written before today is still in the documents, agreeing with the code now and free to disagree later. **(D) THIS IS WHAT G-56 ASKED FOR.** `deprecated_patterns.yaml` excludes `agent-improve/**/*.md` correctly, because architecture markdown must be able to show a superseded form beside its replacement; the ownership guard matches OWNERSHIP rather than patterns, so it needs no exclusion and watches exactly the files the pattern registry cannot. **G-56 is NOT closed**: it names the governing documents being guarded by nothing, and two of eight fact classes are now guarded. Closing it needs the remaining six ruled. **(E) PENDING IS RATIFIED AS A FIRST-CLASS RESULT.** Where a declared owner does not exist — `validation/gate_validator.py`, which §2 designates and the 7.x gate work builds — the fact has no owner to cite, so both hooks report PENDING and allow. Registered now so the owner is live the day the file lands. **(F) THE DRIFT CHECK'S FIRST THREE CUTS WERE ALL CRY-WOLF, AND THAT IS RECORDED BECAUSE IT IS THE LESSON.** Cut one matched any number within 80 characters of an owned symbol: **200+ findings, every one false** — §58.2 beside `PhaseState`, step numbers, years. Cut two bound every count on a line to every symbol on it, a cross product that turned one changelog sentence into thirty-six findings. Cut three still flagged dated records and spec-vs-built pairs. The check now requires a number bound to a count noun, belonging to the NEAREST symbol within 60 characters, skipping dated records and `N of M fields` pairs: **15 claims checked, zero false positives, and a corrupted count still fails it.** A check that cries wolf gets switched off, which is the failure this registry exists to prevent — building it three times over was cheaper than shipping the first one. Reasoning: this commit body.

**v1.43 (2026-09-13)** — **§56 AMENDMENT. The five per-phase coaching scripts leave this document for the phase directories, and the byte-consistency check becomes FILE-to-FILE.** **(A) THE MOVE.** §39.1.7, §39.2.10, §39.3.10, §39.4.10 and §39.5.10 each carried their phase's opening script from `**[OPENING` to the end of the section. All five now live at `skills/dmaic-{phase}-phase/coaching_script.md`, beside the `SKILL.md` that ships them. **965,368 → 847,809 bytes, 117,559 removed, 12.2%.** Each section keeps its heading, its BUILT marker and its shape description, and cites the file. **(B) THE BRIEF'S "FORTY PERCENT" WAS WRONG BY A FACTOR OF THREE, AND THE NUMBER IS REPORTED RATHER THAN THE EXPECTATION MET.** It predicted *"roughly 555 KB expected; forty percent is coaching script"*. The five scripts are **12.3% of the original**; **all of §39 — every phase specification, not just the scripts — is 20.4%.** There is no extraction of coaching content that reaches 40%, so 555 KB was never reachable this way. The measurement that produced it was not re-run before it became a target. **(C) THE CHECK IS SIMPLER, WHICH WAS THE POINT.** It used to locate `#### 39.x.10` inside a 965 KB document, find `**[OPENING` within that section, slice to the next heading, and compare — three steps that could each break on an edit touching neither artifact. It now reads two files in one directory and asks whether one contains the other. **A person can reproduce it with `diff`.** Containment rather than equality is deliberate: SKILL.md wraps the script in §32's frontmatter and the middleware loads it whole. **(D) PROVEN TO FAIL, NOT JUST TO PASS.** One byte appended to `dmaic-analyse-phase/coaching_script.md` takes the check from 5 to 4 and the run to `1 marker(s) DISAGREE`. That demonstration is recorded because a check that has only ever been seen passing is the G-52 shape, and this pass has registered that defect twice already. **(E) FIVE BUILT MARKERS AND FIVE AUTHORITY NOTES CORRECTED IN THE SAME COMMIT.** Each marker claimed the script was *"byte-identical to this section"*, which the move makes false. Each Authority note said *"this section wins until the refactor completes; then authority flips to the code file and this reduces to a pointer"* — **that flip happened here**, and the notes now say so rather than continuing to anticipate it. Reasoning: this commit body.

**v1.42 (2026-09-13)** — **§56 AMENDMENT. The root CLAUDE.md is rebuilt from the live sources at 296 lines, the platform reference is reclassified as a FORWARD document, and two prose open items become numbered gaps.** **(A) ASSEMBLED, NOT SWAPPED.** The handover draft was 176 lines and stale — it carried `backend/**` globs that match nothing, a back-port framing this entry retires, and twelve bans that step 6 had already placed in rule files. The installed file is merged from the live 572 plus the draft's structure: 4,292 lines on 2026-09-12 to **296** today. **(B) `../AGENTIC_ARCHITECTURE_REFERENCE.md` IS A FORWARD DOCUMENT.** Founder ruling: it is to be authored FROM Agent Improve once Improve is proven. **It is not a source of truth today and it is not owed a back-port** — the earlier framing of *"stale, carries a back-port debt"* implied a repayment that was never the plan. Nothing cites it; §0.24's four *Specified in* citations were retargeted to this document in the same pass, and CLAUDE.md §0.12 — whose standing instruction was that *every* § citation points at the reference — is dropped. That instruction was the wiring behind the §8.1 ordering defect. **(C) CARRIED FORWARD AGAINST THE DRAFT:** §0.24 whole, with its number and its four-row table, because `deprecated_patterns.yaml` cites it three times in denial messages; §0.2's invariant sentence and number, without the registry table the registry owns; §18 step 3b, the schema-change gate; the version line, incremented to 2.2.38 per §18 step 3; §20.1's D0–D8 table and §20.4's enforcement table, both marked **moving to the `eight-d` skill at step 10**; the §0.x archive-resolution rule; *"violations cost weeks — proven twice, no third time"*; and the `langchain-core >= 1.6.0` floor beside the langgraph one. **(D) TWO OPEN ITEMS BECOME GAPS, BECAUSE PROSE IS NOT SCHEDULED.** **G-55** — the 1,128 parenthetical citations: **no sweep, the ratchet stands**, revisit when the platform reference is authored from Improve, carried at step 11.2. **G-56** — the live half of §18.1: `deprecated_patterns.yaml` excludes `agent-improve/**/*.md`, so no drift check sees the governing documents, and **every defect worked on 2026-09-12 and 2026-09-13 was in a document**. Step 6.24, a hook that reads ownership rather than patterns and therefore needs no exclusion. §18.1's other half was closed at step 5.2 on 2026-09-03 and the document never said so, which is why it read as owed for ten days. **(E) §0.2's INVARIANT FIRED ON THIS COMMIT AND WAS OBEYED.** Removing §18.1 left `deprecated_patterns.yaml` citing a rule that no longer exists; the registry comment was updated in the same commit, as §0.2 requires. **The check that caught it was the one this pass added at step 6** — re-resolving every registry citation against the root plus the rule files. **(F) THE FIVE COMMANDS VERIFIED, AND TWO WERE WRONG.** `.venv/bin/activate` does not exist — this is a Windows venv with `Scripts/Activate.ps1` only — and `./start.ps1` **hard-resets to `origin/main` and discards uncommitted work**, which the draft described as *"local run"*. Both corrected; the trailing instruction comment is deleted. **(G) THE THREE OVER-BUDGET RULE FILES GAIN NARROW GLOBS** rather than a split: `state.md` 589, `middleware.md` 522, `gates.md` 349, each now loading on the code it governs — editing a phase node loads neither state law nor middleware law. Reasoning: this commit body.

**v1.41 (2026-09-13)** — **§56 AMENDMENT. CLAUDE.md's §1–§15 become thirteen files under `.claude/rules/`, each loading only when a file it governs is opened.** **(A) THE ROOT FILE GOES 3,355 LINES TO 572.** With step 5's archive of §0's change records the two passes take it from 4,292 to 572 — under the 200-line target only after step 7 replaces what remains. §16, §18, §19 and §20 stay in the root because they govern the project rather than the code. **(B) RULE NUMBERS ARE UNCHANGED, AND THAT WAS CHECKED RATHER THAN INTENDED.** All ten rule numbers `deprecated_patterns.yaml` cites — §0.24, §1.4, §1.7, §3.6, §4.4, §4.5, §4.6, §8.7, §11.2, §18.1 — were re-resolved against the root plus the thirteen rule files after the move. §0.2's invariant holds by measurement. **(C) §14 IS DISTRIBUTED, NOT MOVED, AND THE ARITHMETIC IS ASSERTED IN THE EXTRACTOR.** Its **95** bans each land in exactly one place: 87 under the `## Never` heading of the rule file that owns their subject, 8 cross-cutting ones in the root's §1.1. Placement follows each ban's PRIMARY CITATION rather than §14's own six group headings, because the point of `paths:` is that a ban loads with the code it governs — which moved two bans out of the group they were filed under: one citing §10.1 to `state.md` and one citing §7.3 to `rag.md`, both mis-grouped under *LLM and tools*. **(D) THE GLOBS ARE REPO-ROOT-RELATIVE, WHICH IS A TRAP WORTH RECORDING.** `.claude/` sits at the repository root and the code sits under `agent-improve/`, so a glob of `backend/**` matches nothing. The first cut wrote exactly that and the matcher check caught it — every path is `agent-improve/backend/**`, matching `STATUS_WATCHED`'s existing convention. **A `paths:` glob that matches nothing fails silently: the rule simply never loads, and nothing reports it.** **(E) TARGETING VERIFIED BY MATCHING, NOT ASSUMED.** `agent-improve/ui/index.html` loads `ui.md` and nothing else; `backend/tests/**` loads `testing.md` alone; `backend/core/state.py` loads `state.md` + `module-layout.md`. §2's globs are the twenty-four files §2 itself names, extracted from its own text rather than written as `backend/**`. **(F) THREE FILES EXCEED THE 300-LINE BUDGET AND ARE REPORTED, NOT SPLIT** — `state.md` 586, `middleware.md` 521, `gates.md` 346. Splitting a ratified section is a ruling, not an extraction. **(G) §17 IS DROPPED.** `docs/REFACTORING_PROCEDURE.md` owns the build sequence; the second copy in CLAUDE.md was the one that went stale. Reasoning: this commit body.

**v1.40 (2026-09-13)** — **§56 AMENDMENT. §9 CONCEDED A REASON TO A PARAMETER THAT HAS NEVER EXISTED. The Azure AI Search ruling stands on TWO technical reasons, not one.** **(A) THE RULING IS UNCHANGED; ITS BASIS IS CORRECTED.** §9 recorded three reasons for keeping `improve_case_index` on Azure AI Search — the Store has no metadata filtering, no hybrid BM25 + vector scoring, no multi-query + RRF — then conceded two of them and concluded the decision *"now rests on one technical reason rather than three"*. **The hybrid concession followed entirely from `mode="hybrid"`, which does not exist.** **(B) READ FROM THE INSTALLED PACKAGE, NOT A PAGE.** `inspect.signature(BaseStore.search)` on `langgraph` 1.2.11 returns `['namespace_prefix', 'query', 'filter', 'limit', 'offset', 'refresh_ttl']` — six parameters. §9 named eight, of which **four do not exist** (`mode`, `similarity_threshold`, `vector_weight`, `distance_metric`) and one that is REQUIRED (`namespace_prefix`) was not among them. Checked past the base class because a concrete store could have widened it and none does: `InMemoryStore.search`/`.asearch` identical, `SearchOp` identical, `IndexConfig` exposes only `dims`/`embed`/`fields`, and **the string `hybrid` occurs nowhere in the installed package.** **(C) THE SCORECARD.** Metadata filtering — **CONCEDED**, `filter=` exists and does the job. Hybrid scoring — **STANDS**. Multi-query + RRF — **STANDS** (§25). §25 gains the tie-in, because §9's old text left it looking like the sole support for a live ruling; it is one of two. §25's own `MultiQueryRetriever` / `EnsembleRetriever` ban was re-verified by import in the same pass — `langchain.retrievers` raises `ModuleNotFoundError`, both classes present under `langchain_classic.retrievers`, and §18's rule holds that presence is not permission. **(D) THE DIRECTION OF THE ERROR IS THE PART TO KEEP.** C-3 made a document worse; S-1 made a sound ruling look **worse-supported than it was** and then flagged it for re-examination on that false basis. **An error that understates your own position is not a safe error** — it invites reopening a decision that was never in doubt, and it reads as diligence while doing it. **(E) S-1 IS CORRECTED IN PLACE UNDER G-54's RULE**, with a `Source method` row added — *"~~documentation page~~ → introspection — `inspect.signature(BaseStore.search)`, re-run 2026-09-13"* — which is the column step 6.23 will add to every entry. S-1 was named in G-54 as the one entry in that log pinned by nothing while a live ruling rested on it; that is how this was found, and it is the first of the four the step will work. Reasoning: this commit body.

**v1.39 (2026-09-12)** — **§56 RECORD. The §0-retirement dependency check: TWO OF §0's SUBSECTIONS ARE LIVE RULES, NOT CHANGE RECORDS, and one of them is cited by the drift hook.** **(A) THE CHECK, AND WHY IT WAS RUN BEFORE THE RETIREMENT AND NOT DURING IT.** CLAUDE.md §0 is scheduled for wholesale retirement to `docs/_archive/` — 1,112 lines, 26% of the file. Every `§0.x` citation from a live section (line > §0's end) was enumerated first: **§0.18 ×5, §0.28 ×4, §0.24 ×4, §0.20 ×3, §0.2 ×2, §0.17 ×2, §0.10 ×2, §0.29 / §0.30 / §0.31 ×1 each.** **(B) MOST ARE PROVENANCE AND MOVE NOTHING.** §0.17, §0.18, §0.20, §0.28–§0.31 are cited for the DATE a thing was ratified, while the live sections state the values themselves — §9.7 carries *"Thirteen gate-required, twelve coached"* in its own text and cites §0.18 only for *"Option A, ratified 2026-08-26"*. Retiring those rows costs a provenance pointer, not a fact, and no value needs moving. **(C) §0.2 AND §0.24 ARE DIFFERENT IN KIND AND MUST NOT BE RETIRED.** §0.24 says so in its own first line — *"Every other §0.x above is a dated 'What Changed' entry. **This one is a rule**, placed in §0 because it is constitutional"* — and §0.2 states the rule-numbers-are-load-bearing invariant plus the registry's citation table. **`.claude/config/deprecated_patterns.yaml` cites `§0.24` three times**, in the `permissionDecisionReason` messages `pattern-9-hand-rolled-llm-retry`, `pattern-10-custom-llm-tracing` and `pattern-11-manual-state-persistence` feed back to Claude. **Archiving §0.24 would therefore break §0.2's own invariant — *"these citations must resolve"* — using the one mechanism §0.2 exists to protect.** Four live sections cite §0.24 besides. **(D) THE RETIREMENT'S LINE RANGE IS WRONG AS WRITTEN** and is corrected here rather than discovered during the move: §0.2 is **CLAUDE.md lines 53–72** and §0.24 is **lines 756–810**, both inside the range marked for archiving, and both must be carried forward into the surviving file. §0.2 already has an owning step; **no step owns §0.24**, which is the finding rather than a footnote. **(E) §898 IS STRUCK FROM §0.5.** The per-phase-totals row cited *"§898's amendment of 2026-09-09"*; there is no §898 in any of the three documents and the string occurred exactly once across all of them — in that row. The amendment is real and is **§29.2, *"`load_evidence_series` joins the set — RATIFIED 2026-09-09"*** (tool spec §60.7 / S-F57). Struck in place rather than silently repointed, on C-3's precedent, because **a §-number is a literal string and nothing checks them** — which §30's own 2026-09-09 note says about itself, after two wrong citations in one section. **(F) §0'S INTERNAL CONTRADICTIONS ARE DELIBERATELY NOT REPAIRED**, per the ruling: the retired gate field names, Define's counts, and `PhaseState`'s *"20 + 1 managed, 21 declared"* at §0.17 against §10.1's twenty-two all stand, because repairing a section scheduled for deletion spends effort on text nobody will read again. Reasoning: this commit body.

**v1.38 (2026-09-12)** — **§56 AMENDMENT. THE DEPENDENCY UPGRADE IS NOT A BLOCKER AND HAS NOT BEEN SINCE STEP 2.3. The Installed/Latest tables are removed and replaced by floors plus a pointer to `requirements.txt`.** **(A) FIVE SITES CALLED IT BLOCKED, THREE WEEKS AFTER IT WAS DONE.** §53's table read `langgraph` **1.1.10** installed against a venv running **1.2.11**, and `langchain-core` 1.3.3 against an installed 1.6.0; §1 said *"the installed version is below it … unavailable today"*; §44 said the fallback chain's native primitives were *"unavailable at the currently installed 1.1.10"*; §45's drain question said the dependency was *"separate and also unmet"*; Appendix E listed it under **Blocked**. CLAUDE.md §16.1 carried the same table with **BLOCKER** in the first row. **§1's own status line recorded the upgrade** — *"Step 2.3 upgraded dependencies (langgraph 1.1.10 → 1.2.11, langchain-core 1.3.3 → 1.6.0)"* — so §1 contradicted itself inside one section, and four more sections agreed with the wrong half. **(B) THE TABLE WAS THE DEFECT, NOT THE NUMBERS IN IT.** An `Installed` column in a document is a copy of a fact `pip` owns. It can be right only between upgrades, and it goes wrong **silently at the moment the project improves** — the one event nobody re-reads a dependency table after. §53's header even said *"the targets are a snapshot — re-resolve at upgrade time"*, and it went stale in exactly the way it described. A snapshot that warns it is a snapshot is still a snapshot. **(C) WHAT REPLACES THEM: FLOORS, WHICH ARE RULES.** `langgraph >= 1.2.6`, attributable to one release note — 1.2.6 (2026-06-18), *"nested subgraph inherits parent `checkpoint_ns` (regression in 1.2.3)"* — and `langchain-core >= 1.6.0`. **A floor does not move; a pin is a fact.** The floors stay in the documents because a rule belongs in a rule file; every pin now lives only in `agent-improve/requirements.txt`, which already carried the floor rule in its own comments and was right throughout. **(D) `deepagents` STAYS EXCLUDED** — still pre-1.0, §18's exclusion stands, not installed. `langchain-classic` retains legacy classes we do not use; presence is not permission. `langgraph-prebuilt` is present transitively and that is not a violation — §4.4 bans the import, not the package. **(E) APPENDIX E's TWO BLOCKED ITEMS ARE STRUCK, NOT DELETED.** It is a dated snapshot and says so, but a `Blocked` heading over two things that are not blocked is the one staleness a dated header does not excuse. The second item is corrected with it: *"two Azure schema changes ratified and unapplied"* is now **one** — the evidence index's `phase` and `uploaded_at` landed at step 6.13 — and with one left there is nothing to batch it with. **(F) `session-start-context.py` IS NOT TOUCHED.** It pins the right interpreter and reports installed-versus-latest from the live environment, which is the correct place for that comparison: it reads, it does not assert. Reasoning: this commit body.

**v1.37 (2026-09-12)** — **§56 RECORD. CLAUDE.md §7.2 and §7.3 carried the evidence index as unbuilt for two days after §23.2's fields landed, and §7.3 was tabling a schema its own preamble forbids it to hold.** **(A) NOTHING IN THIS DOCUMENT CHANGES.** §23.2's seven fields were marked APPLIED at v1.20 and S-F15 B3 discharged there — *"`uploaded_at` exists now, and the tool still takes no `order_by` as a design choice rather than a schema constraint"*. §59.6's B3 row already reads DISCHARGED. CLAUDE.md was the stale copy, exactly as §8.1 was of §19. **(B) THE LIVE SHAPE, READ FROM AZURE RATHER THAN FROM A DOCUMENT** — 2026-09-12, `SearchIndexClient.get_index(name).fields`: `improve_evidence_index` **12 fields**, `phase` filterable, `uploaded_at` filterable AND sortable, plus §23.2's `role`, `kind`, `description`, `content_digest`, `shape_match`; `improve_knowledge_index` 7; `improve_case_index` 19, vector field still `embedding`. CLAUDE.md §7.3 had tabled seven for the evidence index and asserted *"`phase` and `uploaded_at` are ratified additions, not live fields"*. **(C) THE TABLES ARE REMOVED, NOT CORRECTED.** §7.3's own preamble says it *"does not duplicate the schema"* and then duplicated all three — so correcting the copy would have rebuilt the thing that went stale. It now cites §23 as owner, names the introspection that reads the live shape, and keeps only the facts a rule depends on: `improve_case_index`'s vector field is `embedding` and `rag_lookup_case_history` must use it; `phase` and `uploaded_at` are server-set; `phase`'s filter defaults OFF. **That rename is now the ONLY unapplied schema change of the three this subsection used to track.** **(D) A RULE WHOSE REASON EXPIRED IS NOT THE SAME RULE.** §7.2's `order_by` prohibition survived on its restated form after its basis was gone. The prohibition itself stands — `rag_lookup_evidence` still takes no `order_by` — but for a different and now-stated reason: §7.4's multi-query + RRF returns a FUSED rank, and an `$orderby` over it discards the fusion for recency, which is a different tool. Recency is answered by a filter on `uploaded_at`, never by sorting the fused set. **(E) THE SAME ASSERTION WAS IN CODE.** `backend/knowledge/tools.py`'s module docstring said *"`improve_evidence_index` has neither `uploaded_at` nor `phase` as a top-level field yet"* and named two unapplied changes where one remains. Corrected; rule 2b brought this file in on that path. `verify_built.py`: 24 checks, zero disagreements. **(F) LEFT DELIBERATELY:** CLAUDE.md §0's v2.2.15 row calling the two fields *"ratified, pending reindex"* is a DATED CHANGELOG ENTRY and was true when written; it is retired wholesale at the brief's step 5, not repaired here. Reasoning: this commit body.

**v1.36 (2026-09-12)** — **§56 RECORD. G-54 REGISTERED — the verification log's SOURCE METHOD, which is what produced C-3's wrong verdict, is the same method behind every other verdict in that file.** **(A) THE FAILURE WAS A METHOD, NOT A TYPO.** v1.35 withdrew C-3 for reading a MODULE's API page as a CLASS's member list. **Four of the log's five `Source` cells name a documentation page** — `reference.langchain.com` or `docs.langchain.com` — and not one names an introspection of the installed package. Correcting the one entry that was caught and leaving the method that produced it is the shape §55.1 exists to refuse. **(B) WHAT IS STILL EXPOSED, ENUMERATED.** C-1 (`retries=` / `max_retries=`) and C-2 (`prompt=` / `system_prompt=`) are pinned by `test_retry_kwargs_against_the_installed_classes` and `test_executor.py`'s signature assertions — **by accident of what those steps needed, not by anything the log did**. **S-1 is pinned by nothing and carries a live architectural decision**: it asserts `BaseStore.search()`'s parameter surface from two doc pages, and §9's ruling to keep `improve_case_index` on Azure AI Search already rests on the single reason that entry left standing. If that surface has moved again, §9 rests on less than it claims. **(C) THE COUNTERMEASURE IS A COLUMN, NOT A HABIT.** Step 6.23 adds a `Source method` cell to every entry, whose two starting values are `introspection — <the expression>` and `documentation page — NOT RE-CHECKED`; **the second is a finding rather than a placeholder**, so an unverified entry cannot look like a verified one. Re-verification records the expression verbatim — `inspect.signature()` for a parameter claim, `vars()` for a member list, `importlib.metadata.version()` for a version — and **never the page a second time**, that being what produced the error. Entries are corrected in place, on C-3's precedent. **(D) A MOVED VERDICT MUST BE FOLLOWED.** S-1's feeds §9 and §25; re-verifying it and leaving those sections citing the old conclusion would be the same failure one layer down, so it is in the step's Done-when. **Step 6.23**, Seq 569, OPS/SHARED. Appendix D goes 61 rows to 62. Reasoning: this commit body.

**v1.35 (2026-09-12)** — **§56 AMENDMENT. §19's hook surface is CORRECTED — the six named lifecycle hooks ARE the complete set — and the verification-log entry that made it wrong is withdrawn in place.** **(A) THE ORIGINAL WORDING WAS RIGHT AND A VERIFICATION PASS OVERWROTE IT.** This section read *"`AgentMiddleware` exposes more than six — the reference also lists `dynamic_prompt()`, `hook_config()` and `configure_trace_policy()`"*. Those three are **module-level** names in `langchain.agents.middleware` — two decorators and a process-wide trace-policy setter — and are not members of `AgentMiddleware` at all. `AgentMiddleware`'s hooks are `before_agent`, `before_model`, `after_model`, `after_agent`, `wrap_model_call` and `wrap_tool_call`, each with an `a`-prefixed async twin: twelve methods, six hooks, nothing else. **(B) VERIFIED BY `vars()`, NOT BY THE PAGE AGAIN.** `'dynamic_prompt' in vars(AgentMiddleware)` is `False` for all three against the installed 1.3.16; the public members are the twelve hook methods plus `name`, `state_schema`, `trace_policy`, `transformers`. **The failure mode is the reusable part: C-3's Source cell names a MODULE's API page and its Claim is about a CLASS's member list.** A page lists what a module exports; the verdict read that as what the class exposes, and stamped it CORRECTED. **A documentation page is evidence about an API; the installed object is the API.** **(C) C-3 IS AMENDED IN PLACE, NOT DELETED** — `docs/_archive/BIBLE_VERIFICATION_LOG.md`. A verification log that removes its own errors cannot be used to judge what its other verdicts are worth. Its propagation note is amended with it: the machinery carried the wrong verdict to CLAUDE.md §8.1 exactly as fast as it would have carried a right one, **so the check that a verdict is right cannot live downstream of it**. **(D) §19.1 AND §19.2 UNDERSTATED THEIR OWN HOOK SETS.** `vars()` shows `wrap_model_call` and `awrap_model_call` defined on both LEAF classes rather than inherited, against header lines reading *"Custom · `before_agent` · position 1"* and *"Custom · `before_agent` + a registered tool · position 2"*. §19.1's BUILT marker had named the enclosure since v1.22 while its own header did not — the fact was in the file and not where a reader of the spec would meet it. Both headers now name both hooks, and §19.1 states the division of labour: `before_agent` composes once per turn, `wrap_model_call` prepends and recomputes nothing. Propagated to CLAUDE.md §8.5, whose heading had read *"`before_model` state injection"* — naming a hook the class does not implement — and to §10.2's `project_context` row, a third site of the same wrong name. **(E) TWO GAPS REGISTERED, EACH WITH THE STEP IT NEEDS.** **G-52 — the stack's ordering test cannot observe order**: `test_all_eight_positions_execute_in_the_ratified_order` runs under `stub_coach`, which replaces `create_agent`, so it asserts `reversed(declared)` — the rule checked against itself. That is the escape cause for the whole §19/§8.1 split, and no existing step's Done-when covered it. **Step 6.22.** **G-53 — the premium deployment returns 429**, so no live run reaches a coached turn and the healthy path (coherence passing, the grader actually grading) is unobserved. A quota condition, not a defect, and EXTERNAL like §9.0 and §9.1. **Step 9.2.** Appendix D goes 59 rows to 61. Reasoning: this commit body.

**v1.34 (2026-09-12)** — **§56 RECORD, NOT AN AMENDMENT. The retired ordering sentence had two more sites, both in code, and neither is a separate defect.** **(A) SAME DEFECT, THIRD AND FOURTH SITE.** `backend/middleware/__init__.py`'s module docstring asserted *"Declaration order is execution order for hooks of the same kind, so the order in `create_agent(middleware=[...])` is binding, not cosmetic"*, and its `__all__` numbered contradiction 6, coherence 7, grader 8 against a declaration list that is the reverse — a reader of the package's own front door got the inversion §8.1 had. `backend/tests/test_middleware.py`'s module docstring repeated the sentence as one of the three things it exists to pin. Same occurrence cause and same escape cause as `8b10e8d`, whose body carries the 8D; this commit adds none of its own. **(B) THE `__all__` NUMBERING IS NOW GENERATED**, from the same AST parse of `_build_executor()` that §8.1's block comes from, and carries both numbers where they differ — `declared 6, executes 8` — because a single number is what let the two readings be confused. **(C) `verify_built.py` re-run: 24 checks, zero disagreements.** Rule 2b brought this file in because `backend/middleware/` is a watched path; no marker it carries moves, and §19 is untouched. **(D) OPEN, AND OWNED BY THE NEXT COMMIT:** `vars()` on positions 1 and 2 shows `wrap_model_call` and `awrap_model_call` defined on the LEAF classes, not inherited, so §19.1's *"Custom · `before_agent` · position 1"* and §19.2's *"Custom · `before_agent` + a registered tool · position 2"* both understate the hook set of the middleware they specify. §19.1's BUILT marker already names the enclosure; its header line does not. Reasoning: this commit body.

**v1.33 (2026-09-12)** — **§56 RECORD, NOT AN AMENDMENT. §19's ordering rule is unchanged; CLAUDE.md §8.1's copy of it is brought into line, two and a half months after §19 was corrected.** **(A) NOTHING IN THIS DOCUMENT CHANGES.** §19's *"Ordering rules that bind"* was corrected at v1.22 and is right. CLAUDE.md §8.1 restated the same rule and was not corrected with it, so the two documents disagreed about the declaration order of positions 6–8 from 2026-09-10 until today — and §8.1 is the copy a build step reads. **(B) THE GAP IS STRUCTURAL AND IS NAMED HERE BECAUSE IT RECURS.** §55.1 governs references between documents; nothing governs a document's *transcribed copy* of a fact another document owns. §8.1's block was typed, so the code moving at step 6.5 and §19 moving at v1.22 both left it behind in silence. §8.1 now cites §19 as owner and **generates its declaration block from `_build_executor()` by AST parse** rather than transcribing it. **(C) THE PINNING TEST CANNOT SEE EXECUTION ORDER, which is the escape cause and is registered as a gap rather than fixed here.** `test_all_eight_positions_execute_in_the_ratified_order` runs under the `stub_coach` fixture, which replaces `create_agent` itself; no graph is built, so it asserts `reversed(declared)` instead of observing what fires. The suite was green throughout the defect's life and could not have been otherwise. **(D) VERIFIED BY LIVE TURN, NOT BY THE SUITE.** Real `create_agent`, real LangGraph, real Azure OpenAI, hooks instrumented at class level so LangChain's `m.__class__.after_agent is not AgentMiddleware.after_agent` discrimination is unchanged: `before_agent` fires 1 → 2, `after_agent` fires 8 → 7 → 6 — contradiction, coherence, grader. Four consecutive runs. **(E) THE BUILT MARKERS ARE UNAFFECTED AND THAT WAS CHECKED, NOT ASSUMED.** `verify_built.py`: 24 checks, zero disagreements — including *middleware mounted* 8/8 and *retry caps* 2/continue. Rule 2b brought this file into the commit because the step board regenerated; the board's catch-up is to step 6.21, which landed at `a1a0a5d` without it. Reasoning: this commit body.

**v1.32 (2026-09-11)** — **§56 AMENDMENT. §17 CHANGES MEANING: the executor dispatches the planner's named call, and G-49 closes.** **FOUNDER RULING — option C**, of the four transports costed at step 6.21. **(A) THE EXECUTOR'S `Dispatches` CELL GAINS THE NODE-ISSUED CALL.** Where `coaching_plan` routes to an unread upload, `executor()` calls `load_evidence_series` on that blob path itself, before the model runs, and puts the result in front of the coach as a real tool exchange. **The planner's `Never dispatches` cell is untouched** — the planner still decides and still calls nothing; what changed is that its decision is now carried out rather than suggested. **(B) SCOPED TO ONE CASE, and the scope is the ruling.** One tool, one condition. Every other tool stays model-chosen, §24's *"no unconditional retrieval pipeline"* is untouched, and nothing here decides what to coach. **(C) WHY C AND NOT A OR B.** Step 6.18 established that the instruction was not being outranked, it was not arriving; A and B put prose in front of a model that had already issued 18 evidence searches against a file the plan named. C is the only one of the four whose guarantee does not depend on the model's ranking. D — forced tool choice — stays unverified against the installed library and was not taken. **(D) §26's HOP ACCOUNTING IS ANSWERED, which 6.21's spec left open: a node-issued read costs NO hop.** §3.7's budget counts `rag_lookup_*` calls and `load_evidence_series` is not one, so the accounting is the same as when the model issues it. A guarantee that spent a hop would compete with the retrieval the coach still needs. **(E) A CORRECTNESS FIX TRAVELS WITH IT.** `_unconsumed_for_open_ask` now takes the asks it must decide on: the planner decided before its own `update["asks"]` was applied and the executor reads after it, so under C the two could have disagreed about which upload was routed — the plan naming a file the node then did not read. Define carries no ask shapes, so the two agreed by accident; Measure would not have. **(F) THE EXECUTOR'S DOCSTRING CLAIMED THIS CONTRACT WAS "now fully true" THROUGHOUT.** It said so from step 6.2, while the coach was told neither the plan's `focus_field` nor its `next_action`. Corrected in the same commit: a docstring asserting a contract holds is the last place a reader looks for the news that it does not. **Verification owed and named:** the `live-run` halves of 6.7, 6.12 and 6.13. Reasoning: this commit body, per §56.2.

**v1.31 (2026-09-11)** — **§56 AMENDMENT. §55's mechanism table gains the one mechanism that actually blocks a commit, and that mechanism gains a sixth rule.** Founder ruling: every defect, modification or adaptation is worked as an 8D before any fix is proposed, and it is enforced at the commit rather than trusted — *convention decays; a gate does not*. **(A) RULE 6 EXISTS.** The commit-msg guard now requires **D2 IS, D2 IS-NOT, D4 OCCURRENCE, D4 ESCAPE, D5 FIX and D7 PREVENT** in the body of any commit that is a fix, on three triggers: the subject's type is `fix`; the subject names a registered defect (`G-49`, `F-15`, `WATCH 26`); or the body already carries a `D<n>` label, which is what stops a half-written 8D passing. **Trigger 2 carries the design**: this project's fixes land as spine commits, so G-49's own fix lands as `commit 6.21` and a type-only trigger would have exempted the most important fix commit in the backlog. The rule, the nine disciplines and G-49 worked end to end live at `agent-improve/CLAUDE.md` §20 — every fix is an 8D (v2.2.36, change record §0.30); 37 tests pin the gate, because a message check fails SILENTLY by letting commits through. **(B) §55's TABLE SAID THREE MECHANISMS AND OMITTED THE GUARD.** The constitution is read, the skill is invoked by choice, the drift hook warns before a write — **the commit-msg guard refuses**, and it had been refusing since 2026-08-31 while the section named *Anti-drift* did not list it. Same shape as the findings §55.1 records: a correct mechanism paired with a document that cannot see it. **(C) FOUND BY THE GUARD ITSELF.** Rule 2b blocked the commit adding rule 6 — `git commit --only` still lets the pre-commit hook stage `docs/board.html`, and a watched path staged without this file is exactly what 2b exists to stop. The omission surfaced because the mechanism it omitted did its job on its own amendment. **No rule was renumbered** and rule 2's number stays retired, so the guard's rules are 1, 2b, 3, 4, 5, 6 and `deprecated_patterns.yaml`'s citations still resolve. Reasoning: this commit body, per §56.2.

**v1.30 (2026-09-11)** — **§56 AMENDMENT. G-49 IS DIAGNOSED — the planner's routing decision has no transport into the model's request, and the fix is a step of its own.** Step 6.18, a diagnosis step, ends with a cause rather than a change. **(A) THE CAUSE IS LAYER 2 of the four the step listed: the plan does not reach the executor's context.** The planner rewrites `CoachingPlan.next_action` into an imperative naming a tool and a blob path and logs that it did; `executor()` then invokes the agent with `{"messages": prior}`, reads `coaching_plan` only for the logger and the `step_log`, passes a per-phase constant as `system_prompt`, and mounts the one state-holding middleware — `BeforeModelStateInjection` — which never mentions `coaching_plan`, `focus_field` or `next_action`. Measured at the boundary rather than argued: the imperative reaches **none** of the three channels the model reads — system prompt 7,770 chars, injected block 797 chars, messages 5 chars. **(B) THE OTHER THREE LAYERS ARE RULED OUT ON EVIDENCE.** Layer 1 — `load_evidence_series` has been in `UNIVERSAL_TOOLS` since step 6.12 and is bound in all five phases, pinned by a new test. Layer 3 — excluded by construction, a model cannot deprioritise what is not in its request. Layer 4 — present and not the cause: the upload manifest reaches the coach every turn with the file, its `NOT YET READ` state, its `blob_path` and the tool that opens it (2,893 composed chars on the failing run) and 18 evidence searches followed anyway, so ranking explains a preference and not a missing instruction. **(C) §19.1's GUARANTEE IS TWO-LEGGED, NOT THREE.** The manifest makes the coach AWARE and the planner's routing was meant to make it ACT; that second leg is decided, logged, and never delivered. This node's own comment calls the unread-upload route *"the only point in the loop that is not the model's discretion"* — and because the plan has no transport, it is entirely the model's discretion. **(D) THE FIX IS STEP 6.21, `GATED` on a founder ruling**, because all four candidate transports change a ratified section: the injected block (G-24, founder-owned), a turn-level message, a node-executed call (a real §17 amendment — *"the executor decides no strategy"* would become *"the executor executes the plan's named call"*), or forced tool choice (unverified against the installed library, §16.3). **Prompt wording is excluded as a fix by the diagnosis itself.** **(E) 6.9 COMES OFF G-49's BLOCKING LIST — it never belonged.** Its Verify is `pytest`, it has no live clause, and its Done-when is satisfied by the tree; the blocking claim narrows from four steps to three (6.7, 6.12, 6.13), which re-run on the first `live-run` after 6.21 lands and are re-reported to the founder if that has not happened by 2026-09-25. One correction to the audit that raised the 6.9 question: it recorded *"a test asserts the count and both instructions per file"* as satisfied when only the count was — all five SKILL.md files do carry both instructions and nothing asserted it, which is a missing guarantee over correct content. **No rule was renumbered and no schema changed**, so `deprecated_patterns.yaml`'s citations still resolve. Reasoning: this commit body, per §56.2.

**v1.29 (2026-09-11)** — **§56 AMENDMENT. A step's body heading may not carry a status token, and title drift is now a check.** Founder ruling. **(A) THE BOARD TYPES NO NAME**, so the two sources can disagree with each other and the board renders the disagreement faithfully. `verify_built.py` gains two checks: **step titles** (Appendix D's row against the step's own `## Step X.Y — ...` heading) and **typed names** (zero literal titles in the generator). **(B) SEVEN STEPS FAILED ON THE FIRST RUN.** 6.9 was semantic — its row read *"SKILL.md conformance to §32's seven"* and its section read *"The four missing SKILL.md files"*, two descriptions of different work; both now read *"the four missing SKILL.md files, and §32 conformance"*. 3.4's row said `schemas` and its heading did not; 6.4's said the factory retry was REMOVED and its heading only named it; 9.1's said `Azure`. **Four headings carried a STATUS TOKEN** — 8.4 `· **BLOCKED**`, 8.5 `**GATED**`, 9.0 `**DONE out-of-band**`, 9.1 `**EXTERNAL**` — **a second hand-maintained source for the one fact Appendix D's Status column exists to own**, and a heading and a cell that can disagree will. The rule is ratified in Appendix D. **(C) THE RULE IS NOT BYTE-EQUALITY.** A row is a SHORT FORM — *"Middleware 1–3"* against *"Middleware positions 1–3"* — so it may DROP words and may not INVENT them. That passes abbreviation and fails drift; demanding equality would have forced 58 edits that make the index worse. **(D) The per-phase panel is rebuilt** around what §55.3 actually says: one SHARED block naming every complete and every open item, open ordered by which closes soonest, then one line per phase for what differs. **Define reads 8 of 10 canonical subsections with SIX named as missing** — counted by TOPIC, not by subtraction, because its eight are not the same eight. **(E) Hover detail on 118 elements**, every line read from a source document at generation time and every bubble ending in the document and section it came from. Self-contained: no library, no network, ~20 lines of inline JS. Reasoning: this commit body (§56.2).

**v1.28 (2026-09-11)** — **§56 AMENDMENT. §63 and §69's aliases were CHECKED rather than assumed, and two of sixteen subsections turned out not to be covered.** Founder ruling, after §55.3's completeness view exposed both Parts as UNMEASURED against a note claiming their entries carried their own markers — which they did not. **(A) THIRTEEN OF SIXTEEN GENUINELY ALIAS.** §63.1–§63.5 (the five `{Phase}Output`), §63.7 (the three structured dicts) and §63.8 (`metric_definitions`) are covered by §40–§42; §69.1–§69.6 by §30 and §31. **(B) §63.6 IS NOT COVERED.** The three cross-phase reference dicts exist, and `references_phase` / `references_field` / `references_value` / `references_metric_name` appear only as INSTRUCTION — a field description and three SKILL.md files. **Nothing validates them**: `missing_structured()` states in its own docstring that Analyse and Improve return `[]`, and Control checks `control_plan` alone. **So the one thing that entry exists for cannot happen** — *"the grader verifies the link by LOOKUP rather than judgment"* is judgment again, and the gate passes either way. §42's ✅ would have covered it. **(C) §63.9 IS NOT COVERED.** `phase_metrics` is on all five schemas, is a coached field on NONE, and is written by nothing — `verify_built.py` reports `phase_metrics:W`. The keyed trail across five gate documents is five empty lists. §40's ✅ would have covered it. **(D) §69.7 GAINS A ✅ AND A CORRECTION**: the deliberate absence of a Measure chart-limit tool holds and is pinned by `test_measure_binds_no_chart_limit_tool` — **a deliberate absence is a buildable claim** — and the section's own arithmetic read *"15 of the 16-tool ceiling"* when Measure has been ON the ceiling at 16 since 2026-09-09. **(E) Both Part-level notes are corrected** to say where their entries are measured and which carry their own. UNMEASURED falls 4 → 2, and the two that remain — §43 and §28 — are unmarkable by nature. Reasoning: this commit body (§56.2).

**v1.27 (2026-09-11)** — **§56 AMENDMENT. §55.3 RATIFIES THE PHASE COMPLETENESS SET — the real denominator for "is this phase done".** Founder ruling. **(A) THE OLD FRACTION MEASURED THE WRONG THING.** The board showed each phase as a fraction of the three markers NAMED after it — *"Define 1/3"* — which is the sections named after a phase, not the sections a phase DEPENDS ON. §55.3 lists the **fifty-one items a phase traverses to run end to end with a visible gate**: the API surface and UI, orchestration and persistence, the subgraph, the coach, what it knows, what the Belt gives it, what it computes, validation and the gate, the gate document, reliability, observability, and the phase's own spec. **Define is 25 of 51**, not 1 of 3. **(B) NUMBERING VERIFIED BEFORE USE**, as the ruling required — the set was drawn against a v1.22 snapshot and this document is v1.26; all fifty cited sections still carry the titles named. **(C) SHARED vs PHASE, and a shared break is ONE break.** Fifty of the fifty-one rows are SHARED, which is the vertical-slice argument restated from the other side: **a phase is 98% shared machinery**, so the second slice inherits almost everything the first proves. **(D) UNMEASURED IS NOT A PASS**, and four rows come back UNMEASURED: §43 and §28 are unmarkable by nature, but **§63 and §69 were classified as spec containers *"whose entries carry their own markers"* and their entries carry NONE** — a false claim in the 2026-09-11 sweep, caught by this view on its first run, which is what a denominator is for. **(E) §39.x IS NOT EQUAL ACROSS PHASES.** Four phases carry twelve subsections; **Define carries eight, and not the same eight** — six of the twelve topics have no Define section at all. The phase being proven first has the least specified spec. Reasoning: this commit body (§56.2).

**v1.26 (2026-09-11)** — **§56 AMENDMENT. [CLAIM CORRECTED AT 6.40, 2026-09-18 — IT WAS TRUE OF A PASS AND WAS WRITTEN AS A PROPERTY OF THE DOCUMENT.]** The sentence read *“MARKER COVERAGE IS NOW COMPLETE: every ratified section ends in a marker or in an explicit reason it cannot carry one.”* **It was accurate on the day and nothing re-ran it.** The sweep walked **62 top-level sections**; there are now **69**, and of those **9 carry neither a register row nor a `NOT-MARKABLE` note** — §1, §4, §19, §39, §50, §58, §63, §66 and §69. **It also never ranged over sub-sections at all**, where the real population is: 277 numbered sections, of which assertion 7 found 112 undeclared before this step. **This is §55.2's own sentence turned on a changelog entry — a claim nothing re-runs is a claim** — and the entry is corrected rather than deleted because the cost of a completeness claim that aged silently is the evidence. The remaining 9 are the singles ruled individually at 6.40; assertion 7 is what stops this recurring. Founder ruling. **(A) THE SWEEP.** All 62 ratified top-level sections walked. **45 carry a `> **BUILT:**` marker** with a closing step or `no step owns this`; **17 carry a `> **NOT-MARKABLE:**` note** giving the reason — methodology or coaching content (§28, §43), a rule enforced elsewhere (§54, §56), or **marked at its canonical home** (§5→§57.2, §6→§58.2, §12→§15, §20→§58.5, §45→§44) and the eight spec-layer Parts whose entries carry their own. **Zero sections are in neither state**, which was the point: a section nobody classified is indistinguishable from one nobody built. Markers go 21 → 66. **(B) THE UNOWNED LIST, ENUMERATED FOR THE FIRST TIME.** Four markers are `☐ not built` with **no step that closes them**: §39.2.2, §39.3.2, §39.4.2 and §39.5.2 — the ordered field lists for Measure, Analyse, Improve and Control, which exist as tables here and in no runtime form. A fifth unowned item sits inside §39.5.7: **`SupervisorState.final_output` is never written**, so the project's terminal artifact does not exist. **(C) F-15 IS CHECKED AT LAST.** `verify_built.py` gains an `ast` pass asserting a writer AND a reader for every state field and every `artifacts` key — **one check for a pattern that recurred seven times**, each found by hand months apart. Nine fields are unpaired and each is accounted for; three are exempt **with declared reasons** (`history` diagnostic-only, `remaining_steps` engine-managed, `phase_index` read by the UI). The check took two cuts to get right and both failure modes are recorded in it: counting every dict literal called a READ a write, and counting only `return {...}` called two written fields unwritten. **(D) THE BOARD NAMES EVERY NUMBER.** No bare `§` or step reference renders anywhere — titles come from the headings, and a section with no usable heading is reported by `--check` (there are none). A generated legend gives the prefixes in plain words. Reasoning: this commit body (§56.2).

**v1.25 (2026-09-11)** — **§56 AMENDMENT. EIGHTEEN BUILT MARKERS ADDED — MAIN's three items and the five phases — so the board can show state PER PHASE rather than only per architectural block.** Founder ruling: *"If a fact is worth showing it is worth marking, and the board reads markers."* **(A) MAIN, all ✅ and expected to stay that way:** §57.2 (`SupervisorState` 7/7 exact), §58.2 (`PhaseState` 22/22 exact and in order), §15 (the supervisor graph compiles exactly as specified and is deliberately not yet the runtime — one line at 7.3). **(B) PER PHASE, fifteen markers over three facts each.** The **ordered field list** (§39.x.2): built for Define only — `DEFINE_FIELD_ORDER`, 12 fields — and **absent for the other four**, which expose tier SETS and no `*_FIELD_ORDER`, so the sequence those tables state has no runtime form. **⚠ No step owns those four**: 6.20 covers Define's and group C's slices do not create ordered lists. The **state contract** (§39.x.7): the captured fields land as specified in all four, and **three rows do not hold in any of them** — `artifacts["computation_results"]` and `artifacts["phase_metrics"]` are read by the gate-document assembler and written by nothing, and `field_index` never advances. Analyse additionally never populates `hop_results`/`synthesis_output` despite §39.3.7 saying *"populated here"* (6.10, blocked); Control never writes `SupervisorState.final_output`, and **no step owns that clause**. The **SKILL.md content** (§39.1.7, §39.x.10): ✅ all five, §32-conformant and byte-matching. **(C) DEFINE HAS NO STATE-PARAMETERS SECTION AND NOW SAYS SO** — 39.1.7 is its SKILL.md content, so the phase being proven first is the one phase with no state contract; 6.20 writes it. **(D) §39.x.2's four missing lists and Control's `final_output` are recorded as UNOWNED**, which is the finding rather than a footnote. **(E) The board leads with the four Seq BANDS, not with readiness lanes** — 11.1 and 11.2 had been sitting in READY beside 6.18, correct on readiness and misleading about what to do next. Band ranges and their descriptions are **data in Appendix D**, not constants in the generator. Reasoning: this commit body (§56.2).

**v1.24 (2026-09-11)** — **§56 AMENDMENT. The five `{Phase}State` variants are RULED NOT BUILT, a state MAP joins the head of this document, and Appendix D is re-sequenced around the Define vertical slice.** **(A) S-C03 IS INVERTED — IT NOW DECLARES AN ABSENCE.** It read *"`DefineState`, `MeasureState`, `AnalyseState`, `ImproveState` and `ControlState` extend `PhaseState` with phase-specific transient fields"*; the targeted state audit found **zero occurrences in `backend/` and no subclass of `PhaseState` anywhere**, against a spec naming them **thirteen times**. **They were never specifiable, which is the finding**: G-19 said so for two months — *"the phase-specific transient fields are never enumerated for any of the five"* — and a class whose fields nobody can name is not a design that was missed but one never made. S-C03 assigned them to **step 3.1**, DONE, whose Done-when never mentioned them, so **a completed step silently dropped a spec entry assigned to it**. §7 had already ruled against the concrete case (*"no per-phase typed destinations"*); the general ruling now matches. **§39.2.7–§39.5.7 become descriptions of per-phase USE of the shared 22-field `PhaseState`**, which is what those tables always contained — every row already read *"`artifacts` — holds the 10 captured fields…"*, usage and not declaration. Thirteen references removed; the survivors are explicit negations, kept so the names cannot quietly return. **G-19 CLOSED by ruling.** **(B) A STATE MAP AT THE HEAD OF THE DOCUMENT**, after the provenance block: four rows pointing at §57.2, §58.2 and §39.x.7, **holding no field list of its own** — a second copy of a field list is the duplication that cost two days on 2026-09-10, so the map says where, never what. **(C) THE WRITE PATHS ARE A STEP: 6.20.** `artifacts["computation_results"]` and `artifacts["phase_metrics"]` are read by all five gate-document assemblers and **written by nothing**; `field_index` is set to 0 and never advanced. **The grader scans `computation_results` to answer "was a hypothesis test run?"** — against an always-empty list its answer is always no, so a gate document records that a project did no analysis whatever it actually did. **(D) APPENDIX D GAINS `Seq` AND `Scope`.** `Seq` orders; the step number becomes a stable identifier. **The watermark is gone with it** — completion is per-row, so a step at any position is reachable once unblocked and **the numbering trap that cost a renumber on 2026-09-10 is removed rather than relocated**. `Scope` splits SHARED machinery from PHASE work: **25 of the 27 unlanded steps are SHARED**, which is the vertical-slice argument as a number. **(E) THE BOARD GAINS A HEALTH PANEL** — built / built-and-defective / not-started, counted from the markers, with G-numbers attributed **from §66's own refs column rather than from marker prose** (the first cut read the first `G-\d+` in the text and put G-15 against §19.6, a reference rather than a cause). Reasoning: this commit body (§56.2).

**v1.23 (2026-09-11)** — **§56 AMENDMENT. The three-way alignment audit: four BUILT markers were wrong, and the eleven checks guarding them all passed.** **(A) §49's MARKER CONTRADICTED ITSELF** — *"11 of 12 routes exist … this section's table names 8 of the 11 — six are in the tree and in no ratified table"*: **8 + 6 = 14 against 11 built routes**, and the `12` traced to nothing. The true split is **4 named, 7 unnamed, 5 table rows unbuilt**. **G-47 gains `POST /cases`** (six → seven), missed because the table's `GET /cases` row was read as covering the path rather than the verb — while **step 6.8's own Done-when opens *"`POST /cases` writes the case record to the Store"***. **(B) §33 SAID NOTHING PAUSES FOR A HUMAN, AND SOMETHING DOES.** `ContradictionDetectionMiddleware.after_agent` has called `langgraph.types.interrupt` since 6.5. The gate interrupt is genuinely unbuilt; the blanket claim was not, and it is load-bearing — §34, §49 and S-F01 all cite that absence. **A contradiction interrupt fires today with no built route able to resume it**, which is worse than not pausing; §19.6's *"nothing consumes the flag"* is corrected with it. **(C) G-50 REGISTERED — `CoachingResponse` IS BUILT AT 4 OF S-C05's 8 FIELDS.** §50.1's `explanation` / `example` / `prompt` / `progress` do not exist, so the render contract that section calls *"schema-backed, not prompt-hoped"* is prompt-hoped, and **all five SKILL.md files instruct the coach to populate fields the schema cannot receive** — **WATCH 9 is not closed by 6.9**, contrary to that step's body. The built class's docstring claims transcription from the entry defining eight: **S-C05's rebuild test, failed inside the file that cites it.** **(D) G-51 REGISTERED** — `storage/models.py` defines eleven models where S-C09 names six; the same shape as Part AP6 one level up, AP6 having checked the fields of one named model while nothing checked the model list. **(E) §30 GAINS A MARKER because FOUR figures for one quantity were in the tree**: ratified 9/16/13/9/13, step 5.4's Done-when at the superseded 8/15/12/8/12, the live bind at 7/14/11/7/11, and `test_computation.py`'s docstring at 6/13/10/6/10 — in the file recording WATCH 25 to prevent exactly this, under a test named `test_per_phase_totals_are_8_15_12_8_12` asserting 9/16/13/9/13. All four reconciled. **(F) `verify_built.py` GOES 11 → 21 CHECKS.** Every one of the eleven counted a POPULATION; none pinned a VALUE or a SET, which is why all eleven passed against four wrong markers. Added: the route SET, `CoachingResponse`'s fields, `SupervisorState`/`PhaseState` counts, the model count, §19.3's trigger/keep, §19.4/§19.5's retry caps, §26's three caps, §44's timeout, `interrupt()` call sites **parsed with `ast`** (its line-matching first cut returned 3 where the answer is 1), and **the LIVE per-phase tool bind — the figure none of the four captions was measuring**. **(G) `session-start-context.py` WAS THE LIVE INSTANCE OF WATCH 2**, probing `sys.executable` — the root venv — so every session opened reporting `langgraph 1.1.10 ⚠` against a project on **1.2.11**, contradicting step 2.3's Done-when at the top of every session. Now pinned to `agent-improve/.venv`, as `verify_built.py` always was. Reasoning: this commit body (§56.2).

**v1.22 (2026-09-10)** — **§56 AMENDMENT. §19's ordering rule is CORRECTED, `ARCHITECTURE_STATUS.md`'s tables become BUILT markers on the items they describe, and the counts behind them become a check that runs.** **(A) §19 "Ordering rules that bind" WAS BACKWARDS AND THE CODE HAS BEEN RIGHT SINCE 6.5.** It read *"Declaration order is execution order for hooks of the same kind"* and *"positions 6, 7 and 8 … run in declaration order: contradiction, then coherence, then grader"*. **Both sentences are false.** LangChain's documented middleware model is *sequential on the way in, reverse sequential on the way back* (`langchain.com/blog/agent-middleware`), measured at step 6.5 (ruling AJ1, 2026-09-07): **the declared list is NESTING order, outermost-first**; `before_*` fires outermost-first and `after_*` innermost-first. So positions 6–8 are **declared grader, coherence, contradiction** and **execute contradiction, coherence, grader** — which is what those position numbers have always meant. `test_all_eight_positions_execute_in_the_ratified_order` pins the built behaviour and `test_position_1_wrap_encloses_position_4_retry` pins the `wrap_*` case. **Rule 3 was corrected with it**: positions 4 and 5 have not been "independent of everything else" since 6.3, because position 1's `wrap_model_call` encloses position 4's retry — which is why the project-state block is composed once per turn rather than once per attempt. **Corrected before step 7.1 is built against it**, that being the next step to add to this stack. **(B) THE BUILT MARKERS MOVE ONTO THE SPECIFIED ITEMS.** `docs/ARCHITECTURE_STATUS.md` held eight Level-1 blocks and four Level-3 control-point tables that restated this document's own items with a built-marker attached — the same fact in two files, and the file that carried *"1 of 5 SKILL.md files written"* wrong from its first commit. **17 `> **BUILT:**` markers now sit under the items they describe** — §16, §19.1–§19.8, §26, §33, §34, §44, §46, §49, §51, §53 — in one vocabulary: ✅ built · ⚠️ built with a known defect · ☐ not built · ⛔ blocked, with the rule, the reason and the status on one line. §55.2 states the contract and carries the twelve watched paths. **(C) `.claude/hooks/verify_built.py` RE-RUNS THE COUNTS.** Eleven checks plus the five-phase script byte-match, against the pinned venv, reporting any marker that disagrees with the tree. **A marker nothing re-runs is a claim**, and the first cut of the script proved the point on itself: two probes shelled out to `grep`, returned empty under cmd.exe's quoting, and reported disagreements against a tree that was correct — the probes are now pure Python and shell-free. It also caught one real error, `PARSERS`' keys being `document/pdf/spreadsheet/text` rather than the file extensions the expectation guessed. **(D) Guard rule 2b repointed** to `ARCHITECTURE.md`; verified by probe that it blocks a watched-path commit without it and passes with it, BEFORE the archive move. `docs/` now holds `REFACTORING_PROCEDURE.md`, `CONTINUITY.md` and `_archive/`. **CARRIED FORWARD UNRESOLVED, per the ruling**: §21's role map versus the 11-role factory, and `HITLInterrupt`'s prose call sites in §19.6 and S-C15 (step 7.3's work).

**v1.21 (2026-09-10)** — **§56 AMENDMENT. Parts R–AU are classified and the four rules that existed only in `DECISIONS.md` land here; that file is archived.** **THE POINT OF THE PASS IS THE FOUR, NOT THE 28.** Parts A–Q each carry `landed in ARCHITECTURE.md §X`; Parts R–AU carry no landing pointer at all, so a rule stated there and nowhere else was a rule nothing could be checked against. Working through 28 Parts and ~120 subsections against this document: **4 LAND · 3 SUPERSEDED · 21 REASONING**, with 4 contradictions found and deliberately NOT resolved (below). **(A) AS2 → §58.2 S-C02's `asks` row: ASKS ARE KEYED ON `role`, NEVER ON FIELD.** Several coached fields draw on one dataset — `baseline_mean` and `baseline_sigma` are two reads of one file — so a per-field ask opens three requests for one upload and leaves two permanently unanswered, which is the unread-evidence condition `consumed_at` exists to detect. The row named `role` as a field of an ask and never said it was the key. **(B) AI1 → §21: THE FACTORY PASSES `max_retries=0`, EXPLICITLY.** Retry belongs to the middleware and nothing else; a factory that also retried would multiply against §19.4's cap of 2 and §19.7's cap of 2, turning a documented 2 into an undocumented 6 that no §34 counter can see. Written as an explicit zero because the SDK default is non-zero and omission yields silent retries that look like latency. **(C) AH4 → G-33: `load_skill` is MIDDLEWARE-REGISTERED and outside §30's totals** — and the row's own arithmetic was corrected, because it was false in the dangerous direction. It read *"if bound, Measure goes to 16 against a cap of 16"*, legal by a hair; with the universal eight it is **17 against 16**, illegal on the day it happens. The gap stays open: the answer is a placement, not a ceiling. **(D) AJ4 → G-15: `HITLInterrupt` is DELIBERATELY NEVER DEFINED.** Step 7.3 pauses with LangGraph's own `interrupt()`, resumable by construction; an exception from `after_agent` is not, and defining one would create a second pause mechanism competing with the framework primitive §0.24 requires preferring. Open as a naming problem — §19.6 and S-C15 still raise it in prose. **FOUR CONTRADICTIONS FOUND AND LEFT FOR A FOUNDER, per the ruling that a disagreement between spec and decision is a decision and not a typo** — the largest is **§19's "Ordering rules that bind"**, which states *"declaration order is execution order for hooks of the same kind"* and *"positions 6, 7 and 8 … run in declaration order: contradiction, then coherence, then grader"*. Part AJ1 measured the opposite on 2026-09-07 and the built stack implements it: the list is NESTING order, `after_*` fires innermost-first, and 6–8 are declared **grader, coherence, contradiction** to execute contradiction, coherence, grader. `test_all_eight_positions_execute_in_the_ratified_order` pins the built behaviour. **A build step checked against §19 today would produce the wrong declaration order.** Full list in the commit body. **No rule renumbered**, so `deprecated_patterns.yaml`'s citations still resolve and §0.2 is satisfied.

**v1.20 (2026-09-10)** — **§56 AMENDMENT. The evidence channel's decisions land here, and the version stops standing still.** **THE VERSION IS THE POINT OF THIS ENTRY AS MUCH AS THE CONTENT.** §56 step 3 requires an increment on every amendment, and this file read `Version 1.19.2 · 2026-09-01` across **six consecutive commits** — `c6566f4`, `bd0b4fe`, `29a744b`, `b90b9f2`, `bc34213` and `1714d75` — two of which are explicit §56 amendments (`PhaseState` gains `asks`; §23.2.1 gains its thirteenth row). Six in a row is where an oversight becomes the de facto rule, so it is corrected rather than continued. **(A) §23.2.1's MIGRATION SENTINEL is ratified here, not merely present.** `unclassified (pre-ask-binding)` · kind `evidence` · phase any, carried only by uploads predating step 6.12's ask-binding. Its row and its reasoning landed in the section at `1714d75` under §23.5 — *"an index schema change lands in this section first"* — but §56 steps 3 and 4 were not performed, so the rule was in the document and nowhere in its change record. **Why not `other evidence`**: §23.2.1 reads a rising count of `other` as the signal to extend the vocabulary, so backfilling legacy documents into that row would make the one signal the section relies on measure the migration instead of the corpus. `kind` is `evidence` on Part AQ4 finding 2's precedent — hiding a legacy document from evidence retrieval is the worse of the two available failures. **The premise was verified against the STORED BYTES, not a loaded model**: `role`, `shape_match` and `content_digest` are *absent keys* in the case blob's JSON on every pre-6.12 record, and a loaded `UploadRecord` manufactures `'other evidence'` for them as a Pydantic default — an audit run against models would have concluded no ruling was needed and written a fabricated role into a filterable field. **(B) G-49 REGISTERED — the executor does not call the tool its own planner names.** Group B; register count 48 → 49, open 33 → 34. Found at step 6.13 and **reproduced identically at `1714d75` on 6.12's code**, so it is neither step's defect. It blocks the `live-run` half of **6.7, 6.9, 6.12 and 6.13** — four steps whose remaining verification runs through a path that times out, and which until now were recorded as merely *owed*. Owed means not yet run; this is blocked, and the distinction is what makes it schedulable. **(C) F-15 REGISTERED — declared, and read by nothing, four times.** WATCH 19's shape promoted from incident to pattern: the Store's `case` namespace (closed 6.8), `PhaseState.uploads` (closed 6.11), §6's *"evidence context"* reader (closed 6.12), and `get_evidence_vectorstore()`, which is defined, correct and called by nothing. **The first three were each found while building something adjacent; none was found by a check**, and §55.1's bidirectional rule governs references between documents but nothing applies it between a declaration and its reader. **(D) §23.2's seven fields are marked APPLIED**, and §24's structured record with them — both were RATIFIED-NOT-YET-APPLIED and both landed at step 6.13 (`1396627`), with `azure-query` confirming each of the seven present and filterable on the live index. S-F15's behaviour **B3 is discharged**: `uploaded_at` exists now, and the tool still takes no `order_by` as a design choice rather than a schema constraint. **No rule was renumbered**, so `deprecated_patterns.yaml`'s citations still resolve and §0.2 is satisfied. Decision record: `docs/_archive/DECISIONS.md` Parts AT and AU — **the last entries that file will carry** (§56.2).

**v1.19.2 (2026-09-01)** — **G-21 CLOSED. Records a ratification already made; not a §56 amendment — no rule, schema, field or count of anything but the gap register changes.** `storage/blob.py`'s surface was designed and founder-approved at procedure step 3.5 (commit `025bde7`), but the register still carried G-21 as open and `docs/_archive/DECISIONS.md` held no record of it at all — the binding document asking for a decision that had been taken. **The resolution is that there is no class interface:** §54 and `CLAUDE.md` §2 hold this file to module-level functions ONLY, so three quarters of what G-21 asked for may not exist here. `ImproveBlobClient` was removed; **thirteen module-level names** replace it, tabled at S-C08. **B2's sequencing is answered** — `write_phase_gate` awaits the case blob *before* the registry, because the case document is the system of record and the registry is a projection of it. **Lifecycle:** one loop-keyed cached `azure.storage.blob.aio` client closed by `aclose()` on `app.py`'s shutdown hook, ruled on a measured **~470 ms per `/ask`** penalty for the per-operation alternative — of which client construction is 0.5 ms and the rest is TLS setup, which is why the procedure demanded a number. **`core/store.py` keeps the per-operation shape and is right to**, at a handful of writes per phase. **Deletion is explicitly NOT resolved and is a new gap** — nothing removes `uploads/{case_id}/{file}` (`CONTINUITY.md` WATCH 10). Register: **46 identified, 14 closed or resolved, 32 open** — 13→14, the 12/34 figure quoted when this was scoped having already been stale since G-27 closed at step 3.3. **S-C08's title still reads `ImproveBlobClient`**, a stale label on an entry whose subject is now a module; renaming a spec title is a §56 amendment and was deliberately not done here. Decision record: `docs/_archive/DECISIONS.md` Part Y.

**v1.19.1 (2026-09-01)** — **DOCS CONSOLIDATION. Not a §56 amendment — no rule, schema, field or count changes.** A patch-level entry because this file's content moved, not its meaning. **(A) Appendix F is new**: the v2.2.16 §17 Decisions-Resolved and §18 Change-Log registers, merged in from `docs/ARCHITECTURE_v2216_registers.md`. Those two registers **lived nowhere else** — Appendix A's §17 and §18 rows read "No section here" and routed out to that file, so the reference could not answer a pre-2026-08-22 citation from its own pages. Both rows now route to **Appendix F.1 / F.2** in this file, and the provenance note at the head of the document points there too. Heading levels demoted to appendix depth; **no register text altered**. **(B) §39.1.2 now states its own authority** for the Define Option A ruling — all 12 fields gate-required, no tiers — which `CONTINUITY.md` and `REFACTORING_PROCEDURE.md` had both attributed to `docs/DEFINE_FINALIZATION_2026-08-26.md`. **The ruling was merged; two of that file's field names deliberately were not.** It still writes field 5 as `baseline` and field 8 as `target_metric`, and both are superseded — `baseline` re-introduces the collision v1.13 reversed, and v1.15's metric-registry rename made the live names `baseline_estimate` and `target_value`. §39.1.2's table already carried the current names and is unchanged; the added note records the authority transfer and warns against re-applying the archived file verbatim. §63.1 needed no edit — it already cross-references §39.1.2 rather than restating the ruling, so authority resolves through one place. Both source files move to `docs/_archive/` in the following commit.

**v1.19 (2026-08-27)** — **§56 AMENDMENT. Control is fully specified at §39.5. THE FIVE-PHASE DMAIC SPECIFICATION IS COMPLETE.** §39.5 is the fifth and final per-phase HUB, twelve subsections with its coaching script embedded at §39.5.10. **There is no §39.6.** **Its two movements are confirm and lock:** measure the improved process and show the number moved against the same baseline on the same definition, then build the five-part control plan and hand the process over. **The bright line is delivery, not authorship** — a control plan written is not a control plan delivered, and the classic Control failure is a training plan authored and never run. **F-12 CLOSED:** `actual_close_date` is added to `ControlOutput` as **Tier 2**, taking it **16 → 17** fields and §35's Control row to **3 Tier 1 / 9 Tier 2**. It is the achieved completion date paired with Define's planned `target_date`, and it is Tier 2 for the same reason that target is a planning parameter: **a slipped date does not invalidate the improvement.** **F-14 CLOSED:** `phase_metrics` is **the authoritative store of all N comparisons**, one entry per registry metric carrying `baseline`, `target`, `actual`, `delta` and `met`; `post_improvement_metrics` stays the **primary** metric's Tier-1 deterministic link to Measure's `baseline_mean`, carrying `references_metric_name`. **The grader grades every entry, not only the primary** — a project that met its primary metric and silently missed a secondary one has not fully succeeded, and `phase_metrics` is the only place that shows. **The single-authority invariant now covers Control**, and its shape is the odd one: `post_improvement_metrics` is a reference **dict** whose value lives under `metric`, while the `phase_metrics` entry calls the same number `actual` — **two names for one number**, which is exactly the drift `core/metrics.py` exists to catch, so the mapping is written down rather than inferred and is unit-tested. **`CONTROL_RUBRIC` encodes three Tier-1 guards**: link back to the baseline (the only Tier-1 cross-phase reference in the system), the control plan complete **and** delivered with a named accepting owner, and stability before capability **again** before `post_improvement_cpk`. **The Control SKILL.md was restructured and conformed, not created** — it existed at 946 lines with a field order §39.5.2 reorders. **The measurement thread is now closed end to end** and traceable by one key across all five gate documents (§39.5.12). **What remains is build, not specification:** WATCH 7 (`orchestrate.py` still writes v1 names), **G-27** (boundary mappers) and **G-28** (gate assembly for the four phases beyond Define), and the root-reference back-port. Decision record: `docs/_archive/CLAUDE_CODE_PROMPT_control_39_5.md`. (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.5)

**v1.18 (2026-08-27)** — **§56 AMENDMENT. The Improve phase is fully specified at §39.4; Define's §32 tool-block gap is closed.** **§39.4 is the fourth ratified per-phase HUB**, twelve subsections to the §39.2/§39.3 template, with its coaching script **embedded at §39.4.10** in §39.1.7's format. **Its load-bearing content is the two movements** — *choose* (generate candidates, then select on explicit criteria, a decision matrix) and *prove* (pilot at limited scale, then confirm) — and the ordering that enforces them: `selected_solution` at **1**, the root-cause link at **2**, `experiment_justification` at **3**, `pilot_result` at **4**. **You decide how hard to test after you know what you are choosing between**, not before. **Two Tier-1 guards** in `IMPROVE_RUBRIC`: the solution must **trace to the validated root cause** (resolved by lookup, not judgment), and **pilot before rollout** — practical AND statistical, the same two-gate test as Analyse, with a trivial-effect pilot coached back. **DOE belt-gating is stated as a rubric criterion**: all three answers to `experiment_justification` are valid and none scores higher; DOE is recommended for Black Belts and suppressed for Green Belts, **but the question is asked of both**. **Improve's `phase_metrics` carries the linkage-plus-pilot form** — `{name, moved_by, pilot_effect, source}` — with `"not addressed this phase"` for untouched metrics (§39.4.3, §63.4), and **`solution_linked_to_root_cause` is the phase that now populates `references_metric_name`** on the uniform S-C32 shape. **No schema field-count change: `ImproveOutput` stays 14.** §35 confirms the **4 Tier 1 / 5 Tier 2** split. **The Improve SKILL.md was restructured and conformed, not created** — it existed at 656 lines, and its field order contradicted §39.4.2 (it coached `experiment_justification` first). **Separately, a §32 compliance gap is closed:** Define binds `calculate_expected_savings` (§30) but §39.1.7 carried **no seven-step block for it**, while §32 requires one for every bound computation tool. The block is added to §39.1.7 and to the Define SKILL.md at the matching position, after the `target_value` field — the tool needs both `baseline_estimate` and `target_value` to compute anything. **This is new ratified content, not a rename.** **Only §39.5 (Control) remains stubbed**; F-14 is the open finding it carries. Decision record: `docs/_archive/CLAUDE_CODE_PROMPT_improve_39_4.md`. (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.4)

**v1.17 (2026-08-27)** — **§56 AMENDMENT. §39.2.10 and §39.3.10 now carry their phase's coaching script, so the authority they claim is real.** **The defect was coherence, not content.** §39.1.7 (Define) embeds the full script and is authoritative-during-refactor, with its SKILL.md generated to match verbatim. §39.2.10 and §39.3.10 claimed **the same authority while holding only a pointer at the SKILL.md** — so the file that was supposed to be generated from them had nothing to be generated from, and "must match verbatim" had no referent. **Both now embed the script, formatted exactly as §39.1.7**: the authority and coaching-pattern preamble, the phase opening (Measure's Define-recap, Analyse's Measure-recap), one block per field in §39.2.2 / §39.3.2 order with **Explain / Show / Ask / Confirm**, one seven-step block per bound tool, the metric-literacy explanation, and the gate-readiness closing — plus, for Analyse, the two-movements framing, the 5-Whys sequence and the test-selection sequence. **Content was lifted, not rewritten** — all thirteen tool blocks already carried seven labelled steps and moved byte-for-byte. **What was conformed on the way in:** all nineteen field blocks gained the four labelled parts (they had **Show** and little else); Analyse's `causal_hypothesis` block still showed the three-key reference shape and now shows five, including `references_metric_name` (§63.6, added at the Analyse review); and §39.3.10's line claiming the SKILL.md **does not exist** is gone — it exists and was reordered at `43c4201`. **Deliberately NOT embedded**, because they are not coaching script and several have their own §39.x home: front matter, the A→F session flow, the field-order table, templates, uploads, capture instructions, the Document Layout, pitfalls, cross-phase tables and the phase rubrics. **Both SKILL.md files were restructured to match** — their coaching content is now one contiguous `## 3. Coaching content` section holding the identical body, with the remaining sections renumbered contiguously. **Verified by containment, not by eye:** each of the three embedded scripts is a byte-exact substring of its SKILL.md — the Define atomic-unit check, now run for all three phases. Decision record: this section pair.

**v1.16 (2026-08-27)** — **§56 AMENDMENT. The Analyse phase is fully specified at §39.3; F-13 CLOSED; the cross-phase reference shape gains `references_metric_name`.** **§39.3 is the third ratified per-phase HUB**, written to §39.2's template — twelve subsections indexing the cross-cutting specs and recording only Analyse specifics. **Its load-bearing content is the two movements**: generate candidate causes qualitatively (fishbone, 5 Whys, Pareto), then validate them quantitatively — and the ordering that enforces it. `causal_hypothesis` is coached at **2**, `root_cause_validation` at **3**, and **`root_cause_statement` at 5, after validation and ruling-out**. You state the cause once, once it is proven; the previous SKILL.md draft had it at position 2 as "the candidate, before it's proven", which invites a Belt to write a conclusion and then look for support. **F-13 is closed by `references_metric_name`** (§63.6, S-C32), added to **all three** cross-phase reference dicts for one uniform resolution path. **The grader now matches on it** against the referenced phase's `phase_metrics` `name` and reads the value from that entry — **never from the bare scalar**, which is only the primary metric's mirror (§39.2.3), so a link about the second metric would otherwise resolve against the first and compare two different things while looking verified (§42, S-C32 B1, B5). Analyse populates the key now; **Improve and Control carry it unpopulated until §39.4 and §39.5** — Control's is **F-14**, still open, but **its reference shape is now settled** and what remains is how N comparisons are presented and graded. **Analyse's `phase_metrics` carries the LINKAGE form** — `{name, explained_by, share_explained, source: "linkage"}` — with `"not addressed this phase"` for any registry metric the phase does not touch (§39.3.3, §63.3). **No schema field-count change: `AnalyseOutput` stays 14.** **§35 confirms Analyse's 4 Tier 1 / 5 Tier 2 split** and confirms **`causal_hypothesis` as Tier 2** — the substance is in the Tier-1 `root_cause_*` fields, and the traceability rides on `phase_metrics`, which is not skippable. **`ANALYSE_RUBRIC` encodes two methodology guards as Tier 1**: correlation is not causation (an association result needs a stated mechanism before it is a root cause) and statistical is not practical significance (a validated cause explaining a trivial share is coached back). **`skills/dmaic-analyse-phase/SKILL.md` was rebuilt, not created** — it existed and its field order contradicted §39.3.2. **Also corrected here: §63.7 had been left sitting after §63.9** by the v1.15 insertion, and is moved back above §63.8. **§39.4–§39.5 stay stubbed.** Decision record: `docs/_archive/analyse_section_39_3_draft.md`. (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.3)

**v1.15 (2026-08-26)** — **§56 AMENDMENT. The Measure naming convention, the structured metric registry, and Measure's full specification at §39.2.** Founder-ratified change set, applied in five steps. **(A) Seven identifiers renamed** on the two-tier acronym rule — spell out the cryptic and local, keep the industry-standard: `process_kpis`→`process_metrics`, `baseline_kpis`→`baseline_metrics`, `baseline_metric`→`baseline_estimate`, `target_metric`→`target_value`, `vital_few_xs`→`vital_few_drivers`, `xy_matrix_summary`→`driver_priority_summary`, `post_improvement_metric`→`post_improvement_metrics`. **`baseline_mean`, `baseline_sigma` and `post_improvement_cpk` survive untouched** — they are the lookalikes the rename had to route around, which is why it ran as seven word-boundary substitutions rather than one find-replace. **(B) All 20 computation-tool NAMES stay** — `Cpk`, `DPMO`, `GR&R`, `RTY`, `FTQ`, `DOE`, `I-MR`, `ANOVA` are the recognised terms — but every docstring now opens **plain concept first, then the standard term** (§69.1). **(C) The structured metric registry replaces the prose-string multi-criteria contract of v1.14.** `metric_definitions` (§63.8, S-C38) is Define's registry of `{name, unit, meaning}`; `phase_metrics` (§63.9, S-C39) is a per-phase placeholder **on all five schemas**. Both are a **narrow fourth exception to §7's string law**, same class and reason as the three cross-phase reference dicts: **the grader traces a metric by key equality on `name`**, which prose cannot support — "Error rate: 12.3%" and "error rate (%)" are one metric to a human and two to a matcher. Scalars inside stay strings. **(D) §40's same-field-on-all-five rule now binds THREE fields**, adding `phase_metrics`; counts rise to Define 18, Measure 15, Analyse 14, Improve 14, Control 16. **Define rises by two, not one** — it alone carries the registry. **Its 12-position coached walk is unchanged**: the registry is captured inside position 5, where the Belt names what they measure, so the walk stays at twelve while the gate requires thirteen. **(E) §39.2 specifies Measure in full** — twelve subsections, written as an INDEX into the cross-cutting specs rather than a restatement of them. It carries the **single-authority rule**: `phase_metrics` is authoritative, the scalars are the primary metric's mirror and MUST equal it, additional metrics live only in `phase_metrics`. **Enforced as a `gate_apply` assembly invariant that raises** (S-F28 B1–B5, `core/metrics.py`), because two stores holding one value drift invisibly — both reads succeed and the disagreement only surfaces a phase later. **(F) Metric literacy is a new coaching requirement** (§43.7, §32): the coach teaches the *metric* — what it is, why it matters here, how to read it — distinct from §43.1's education on the *statistic*. §50's gate-document rule regroups on `phase_metrics` `name` and adds `phase_metrics` to the narrative sources. Register: **46 identified, 12 closed or resolved, 34 open** — G-45 and G-46 registered and resolved in the same pass, so every reference in §39.2 resolves. **§39.3–§39.5 stay stubbed.** **The root `AGENTIC_ARCHITECTURE_REFERENCE.md` is deliberately NOT renamed** and temporarily diverges on field names — expected under §0.12, owed at back-port once Improve settles. Decision record: `docs/_archive/CLAUDE_CODE_PROMPT_measure_naming_registry.md`. (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.2)

**v1.14 (2026-08-26)** — **§56 AMENDMENT. A project may track N measurement criteria, and it costs ZERO schema change.** Founder ruling, phase-review workstream: **multiplicity lives inside the existing `str` fields**, exactly as `process_map_sipoc["process_kpis"]` and `detailed_process_map["baseline_kpis"]` already carry several KPIs each. `baseline_metric`, `target_metric`, `baseline_mean`, `baseline_sigma` and `stability_assessment` **all stay `str`** — no `phases/*/schema.py` is touched, and §7's typing law is not merely respected but is what makes the ruling work. **The contract is textual:** `baseline_metric = "Error rate: 12.3% (n=4,200). Cycle time: 2.6 days (n=340)."`, with `target_metric` naming the same criteria by the same names and units. **§69.1 gains one additive convention** — when more than one criterion is tracked, a tool call's `inputs` sub-dict carries a **`metric_name`** key naming which criterion the call is for. **No tool signature changes**; `metric_name` is simply absent on single-criterion projects, so all 20 entries at §69.2–§69.6 stand unaltered. **`MEASURE_RUBRIC` gains two Tier-1 checks** (`dmaic-measure-phase/SKILL.md` §11): the criteria named in `baseline_metric` must match `target_metric` by name and unit — **a name-match, not an LLM judgment** — and where several are named, stability and any Cpk verdict must be **per criterion**, so one blanket "stable" covering four metrics fails rather than passes. **§50 gains the gate-document parity rule**, which is cross-phase rather than Measure's alone: every phase renders `computation_results` inline, grouped by `metric_name`, each with its interpretation and its chart — and **the document's narrative comes from captured field text plus `computation_results`, never from `CoachingResponse`'s turn-level `explanation`/`example`/`prompt`/`progress`**, which are ephemeral coaching UI (§50.1, WATCH 9). Measure's SKILL.md §8 already did this; Define's is back-applied, and the other three inherit it when written. **Two forward-notes recorded, not built** — F-13 (Analyse's `causal_hypothesis` must name which criterion a root cause explains) and F-14 (Control's target-vs-actual becomes one comparison per criterion); both belong to their own phase reviews. Findings 12 → 14. Decision record: `docs/_archive/measure_multicriteria_and_intent_brief.md` Part 2. (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.2)

**v1.13 (2026-08-26)** — **§56 AMENDMENT. Define's field #5 is `baseline_metric`. Founder ruling; supersedes v1.12's rename, which went the wrong direction.** v1.12 renamed `baseline_metric` → `baseline` on the authority of `DEFINE_FINALIZATION_2026-08-26.md`; **`CONTINUITY.md` v4.1 §5 is authoritative and reverses it.** **The reason is collision, and it is a real one:** Measure carries `baseline_mean` and `baseline_sigma`, and `detailed_process_map` carries `baseline_kpis` — a bare `baseline` sitting among those three reads as a generic prefix rather than as Define's discrete current-state value, which is exactly the ambiguity the measurement thread cannot afford. **`baseline_metric` pairs with `target_metric`** and makes the Define-sets / Control-compares relationship legible at a glance. **Renamed here:** §35's Define row, §39.1.2 field #5 and the measurement-thread note, §39.1.7's coaching block, §63.1 (S-C27) and its B7, the S-F28 gate-assembly sample, §69's S-F37 precondition, and §28.1's collision example — which was, precisely, `baseline` vs `baseline_mean`. **Not renamed, deliberately:** the three sibling fields, and every English use of the word "baseline" (a rough baseline, a baseline Cpk, the Measure baseline). **§39's measurement-thread block needed no change** — it names `process_kpis`, `baseline_kpis` and `post_improvement_metric`, none of which is this field. v1.11's and v1.12's entries keep their original wording as dated records. Decision record: `docs/CONTINUITY.md` v4.1 §5. (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.1.2)

**v1.12 (2026-08-26)** — **§56 AMENDMENT. Define is FINALIZED at Option A — all 12 fields gate-required, no Tier 1 / Tier 2 split in Define.** Supersedes v1.11's 8/3 split for Define only; **the other four phases keep their tiers**, each decided at its own phase review. **This pass is a consistency finalization**: §39.1.2, §40, §35's per-phase table, §43.4's live-preview sample, §63.1 (S-C27) and §62.11 (S-F28) are reconciled to one answer, which also resolves the live §39.1-vs-§40 contradiction over whether `team` and `baseline` were gate-required. **`DefineOutput` is 16 fields — 12 required + 4 gate metadata**, up from 15: **`target_metric` is added** and `secondary_metrics`, `business_case` and `target_date` join the required set. **`baseline_metric` is renamed `baseline` throughout** — the last two references outside the schema (§28.1's middleware post-mortem, §33's structured-output caveat) now match the field the code declares. **`baseline`, `target_metric` and `target_date` stay discrete required fields and are NOT folded into `goal_statement`** — they are the machine-readable values Control extracts to compute target-vs-actual, mirroring the existing three-phase KPI thread (§39). **Gate assembly for Define is direct `artifacts[...]` access on all 12** — the Tier 2 `.get(..., "")` row never applies, and there is no `acknowledged_gaps` path for Define. **§39.1.7 gains two coaching blocks** (`target_metric`, `secondary_metrics`) and `target_date` gains a worked example, taking the coached sequence to 12; `skills/dmaic-define-phase/SKILL.md` and `phases/define/{schema,validate}.py` are rebuilt with it as one atomic unit (§56.1). **F-12 records the forward dependency**: Control needs an `actual_close_date` to pair with Define's planned `target_date`, to be formalized at Control's phase review. **WATCH 7 is unchanged** — `orchestrate.py` still writes the v1 names and the Define gate stays non-functional until procedure step 4.1; this pass is spec-plus-schema alignment, not the orchestrator migration. **WATCH 8 is unchanged** — `CLAUDE.md`'s "Define 6 Tier 1" becomes "Define 12 required" in its own §0.x amendment, deliberately not in this commit. Register: 44 identified, 9 closed or resolved, 35 open; findings 11 → 12. Decision record: `agent-improve/docs/_archive/DEFINE_FINALIZATION_2026-08-26.md`. (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.1.2)

**v1.11 (2026-08-26)** — **§56 AMENDMENT. The Define phase is fully specified at §39.1; G-38 CLOSED for Define; `CoachingResponse` gains four presentational fields.** **§39.1 is the ratified amendment's "new §41" renumbered** — §41 was already "Structured dict fields, and FMEA", RATIFIED and cited 23 times here, three times in `CLAUDE.md` §10.8 and once in Appendix A, and sections run 1–68 with no gaps. Placing Define at **§39.1** expands the §39 table row that describes it, breaks no citation, and reserves §39.2–§39.5 for the other four phases (founder ruling, 2026-08-25). **§39.1.2 is the ordered field list — ten coached fields — and that list IS the `field_index` sequence, which closes G-38** and makes S-F13's DP1 predicate implementable for Define; the other four phases stay blocked on G-27 and G-28, so the closure is per-phase by design and all seven inline G-38 markers now say so. **`DefineOutput` is 15 fields — 8 Tier 1, 3 Tier 2, 4 gate metadata**, up from 6 Tier 1: `team` and `baseline` join Tier 1, `project_scope` becomes a dict, `problem_statement` is composed from 5W2H coaching rather than stored granularly, and one `target_date` replaces the `target_date` / `estimated_completion_date` duplicate. **Founder ruling: `secondary_metrics` stays** — the amendment's ten-row table omitted it, but §40's two-fields-on-all-five rule was not retracted, and §39.1.2 is the *coached* list rather than the whole schema. **F-11 records that the built `DefinePhaseInput` had diverged from the v2 names**, so this rebuild is not later read as having introduced them — it retired them. **§50.1 defines the coach response structure** and **§56.1 adds the atomic-unit principle**: a phase's `schema.py`, `validate.py` and `SKILL.md` are one unit sharing one field vocabulary, and rebuilding one without the others is a §56-class violation — a mismatch does not fail loudly, it fails at the gate one phase later. **`CoachingResponse`'s four new fields carry a five-phase blast radius**, stated rather than discovered; the UI half is not built. Register: 44 identified, **9 closed or resolved, 35 open.** Pydantic and `response_format=` verified against live documentation 2026-08-26. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §W1.

**v1.10 (2026-08-24)** — **§56 AMENDMENT. G-01 and G-02 resolved together; `PhaseState` gains `rejection_feedback`, 20 author-populated + 1 managed.** **S-F13 is designed rather than marked**: DP1 — the **planner** owns the field/gate decision and the executor returns plainly, emitting no routing `Command` (§17); DP2 — `gate_attempts` increments **once at `validation_stack` entry**, and the three exits are pass → `gate_review`, fail under cap → planner with `validator_feedback`, fail at cap → escalation via `Command.PARENT`, **the only use of `Command.PARENT` in this architecture**; DP3 — `gate_review` interrupts, and `gate_apply` branches approve → `END` / **reject → planner carrying `rejection_feedback`**, with the Belt's reason **mandatory**. Every routing node returns `Command` exclusively, annotated `-> Command[Literal[...]]`, and no routing node has a static edge out (§15 C2). **`rejection_feedback` is a third actor at a third moment** and is never merged into `validator_feedback`. **Two dependencies are recorded rather than assumed:** DP1's predicate needs **G-38**, and the escalation node name needs **G-34** — both still open. §4's stale `PhaseState (17)` label corrected. Register: 44 identified, 8 closed or resolved, 36 open; **Group A is now empty.** Verified against current LangGraph documentation, 2026-08-24. §13's diagram was redrawn in the same commit to match — **§13's phase-subgraph diagram redrawn to agree with S-F13 DP1 and §17.** **The field-complete / more-fields decision moves from after the executor to the planner**, which is where §13's own prose already put it: the planner inspects `artifacts` and returns `Command(goto="executor")` or `Command(goto="validation_stack")`, and **the executor returns plainly, emitting no routing Command** — it decides no strategy (§17). Deciding in the executor would have fused the two roles while leaving the node names intact. The branch is relabelled from "conditional edge" to `Command` routing (§15). **`gate_apply` now shows two exits:** approve → `END`, and **reject → planner carrying `rejection_feedback`** (§33, G-02), drawn in the same left return channel as the validation stack's `validator_feedback` loop because they are the two ways control re-enters coaching. A routing summary states who returns a `Command` and who does not, and that the only static edges are `START → planner` and the parent's phase edges (§15 C2).

**v1.9.1 (2026-08-24)** — S-F09 guard sample synced to the G-04 resolution (direct access; the `.get(...,10)` artifact removed).

**v1.9 (2026-08-24)** — **W1 / G-04 resolved: `remaining_steps` is declared as a LangGraph managed value.** It was read off `PhaseState` in §26's entry guard and never declared — so `state.get("remaining_steps", 10)` returned **10 forever and the five-hop cap never fired.** `PhaseState` now declares `remaining_steps: RemainingSteps` (`from langgraph.managed import RemainingSteps`) in a new **engine-managed** category: **nineteen author-populated fields plus one engine-managed value, twenty declared.** The input mapper populates the nineteen and **SHALL NOT populate the managed one** — LangGraph's execution loop supplies it as `recursion_limit` − steps taken. **The 10 was a bug artifact and is gone; the five-hop business rule is unchanged and now actually fires.** Verified against the installed LangGraph 1.2.11 — import path, `Annotated[int, RemainingStepsManager]`, and `scratchpad.stop - scratchpad.step` read from source. Register: 44 identified, 6 closed or resolved, 38 open. Also in `CLAUDE.md` §10.1.

**v1.8 (2026-08-24)** — **G-44 resolved; §16 gains the wrapper-invoke rule.** The phase wrapper node's inner `await subgraph.ainvoke(child_state)` **does** persist `PhaseState` across Belt turns — LangGraph statically discovers a subgraph invoked directly inside a node function and namespaces its checkpoints under the parent saver via the inherited config. **Pattern B is not merely correct, it is forced**: `SupervisorState` and `PhaseState` share no keys, so `add_node(subgraph)` is unavailable. Two constraints now bind — call `ainvoke` directly with the inherited config and never pass a fresh one, and never relocate the invoke inside a tool, where LangGraph does not namespace it and persistence breaks silently (a constraint G-32 must respect). Verified against current LangChain subgraph documentation, 2026-08-24; **a local repro against the pinned LangGraph is still owed.** Register: 44 identified, 5 closed or resolved, 39 open. **G-04 is now the next live gap.**

**v1.7.1 (2026-08-24)** — **G-43 resolved as a FALSE ALARM; gap-register resolution, no architecture change.** Every `.invoke`/`.ainvoke` in this document is either the single parent-graph entry point or an LLM call — **no subgraph is invoked standalone**, so the per-invocation concern has no site to occur at. Checkpointer placement is the prescribed pattern, and the `checkpointer=True` clause whose absence raised the alarm **applies to independently-persisted subgraphs, which this architecture deliberately does not use — omitting it is correct.** What remains is the already-known **⚠ WIRED, INERT** checkpointer in the current code, already scheduled as the `thread_id`-through-`ainvoke` step (§16, §47, §53.1); G-43 folds into it and adds no new work. **The provenance pattern-check fired and then cleared on inspection — recorded as a true negative so the §R-series list is not inflated with a false fourth instance.** **G-44 registered in its place at HIGH severity**: G-43 verified the standalone-invoke and bare-node cases, and the **wrapper-internal `subgraph.ainvoke`** that S-F10's execution site prescribes is a third case it did not cover — open, and prior to it whether that wrapper pattern is the right approach at all. Register: 44 identified, 4 closed or resolved, 40 open. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §U1.

**v1.7 (2026-08-24)** — **§56 AMENDMENT. G-03 and G-42 resolved; `PhaseState` 17 → 19 fields.** Ruling A2: phase-internal code reads case identity and phase from its own `PhaseState`, injected by the input mapper at the boundary — `case_id` and `current_phase`, **copied down at phase entry, read-only inside the subgraph, never written back up.** The parent keeps its single writer; this is a boundary-time copy, not a second writer. Chosen over reading `case_id` from config and phase from a build constant, **because mixing sources is what made G-03 latent.** The same fix resolves **G-42**: the mapper's execution site is the parent's uniquely-named node function for that phase — the documented LangGraph pattern where parent and subgraph share no state keys — which adds no sixth node and carries a call-order namespace stability condition. **§56's `PhaseState` trigger is corrected in the same commit**: it now fires on any new field whatever its category, closing an enforcement hole in which a field could skip the gate on a category label. `§45`'s handler now reads `current_phase`, not `phase`. **G-43 registered, not resolved** — highest severity, marked INFERENCE. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §T1.

**v1.6.1 (2026-08-24)** — **§55.1 rule 3 narrowed to peer runtime call edges**, with the four excluded classes stated: edges into class entries, return paths, build-time relations, and nested sub-component references. Its first run (§66.8) reported 36 non-closures; re-run under the narrowed scope, 29 fall out of scope and 7 remain, of which 5 are real wiring defects — 86% of the original output was noise, which is how a check stops being read. The re-run was executed and its classification is tabled at §66.8, not asserted. §66.8's note now records the narrowing as the resolution of finding F-07. **A check-scope correction, not an architecture change**: no section content, schema, signature or gap moved, and this is deliberately not routed through §56. Also applied to `agent-improve/docs/_archive/SPEC_LAYER_GUIDE.md` §6 rule 3, which carried the same un-narrowed wording. (archived to docs/_archive/; canonical: ARCHITECTURE.md §57)

**v1.6 (2026-08-23)** — **The specification layer.** Two new Parts: **Part XII (§57–§66)** states the classes, functions and interfaces at the level the code could be rebuilt from, and **Part XIII (§67–§68)** carries the EU AI Act posture and the DORA-structured risk register. 73 spec entries; definitions relocated out of 28 architecture sections, which keep every word of their reasoning and gain a `**Specification:**` pointer. **§1–§56 do not renumber.** Five entries carry an AI-ACT flag and 12 carry `AI-ACT-REVIEW: uncertain`. **42 gaps are marked and none is filled** — that was the pass's binding constraint; §66 is the register, and §66.7 records ten findings that are inconsistencies rather than absences. §55.1 adds the five spec-layer governance rules; Appendix C gains a Tier 1 compliance block. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §S1, §S2.

**v1.5 (2026-08-22)** — **§15: `route_after_phase` deleted.** The section showed static phase edges *and* a conditional router returning labels wired to nothing, reading `gate_attempts` off `SupervisorState` where that field does not exist — a `KeyError` on the gate-failure path. A phase transition is either static or conditional; static is correct, because a subgraph reaches `END` only through `gate_apply` and so reaching `END` means the gate passed. Retry and escalation resolve inside the phase. **Level 2 routing untouched.** The deleted function was already prohibited by Appendix D.2 — see DECISIONS §R2 for that finding. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §R2.

**v1.4 (2026-08-22)** — **Contradiction detection redesigned** (§19.6, §20, §32, §37, §50). The middleware's mechanical dict comparison is deleted — it read a Store key `gate_apply` does not write until phase end, and matched field names where **38 of 41 content fields are unique to one phase**. Detection moves to the coach via SKILL.md instruction and a new `CoachingResponse.contradiction_flag`; **no LLM call is added anywhere**. The middleware keeps its position and hook and becomes a flag-reader. §56 gains `CoachingResponse` to its amendment-required list — that omission was an oversight. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §R1.

**v1.2 (2026-08-22)** — Renamed from `AGENT_IMPROVE_BIBLE.md` and moved to the
monorepo root. **The scope statement changed with it**: this is the platform
reference for Agent Improve, Agent Resolve and Agent Flow, not an
Improve-specific document. See *Scope* below. No architectural content changed
in this version — only the name, the location, the scope statement, and the
relative paths that the move invalidated.

**v1.1 (2026-08-21)** — §29.4 added via the §56 amendment procedure: cross-agent
tools named as a distinct third category, RATIFIED as present-but-not-bound,
with the three rules that bind before any may be bound to a coach. Resolves the
§29.1 / §29.2 tension. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §Q1.
Also in this version: Appendix D.1's retired retrieval-tool names corrected to
the strings actually in the codebase, and §53.1's checkpointer status corrected
from "done" to WIRED-but-INERT.

<a id="L285"></a>
#### Original lines 285–300

**Verification:** every API signature, parameter name, deprecation status,
version floor and cited source was checked against live documentation. Three
corrections, two now-stale items and four enhancements were applied to this
document as a result. Full log:
[`agent-improve/docs/_archive/BIBLE_VERIFICATION_LOG.md`](agent-improve/docs/_archive/BIBLE_VERIFICATION_LOG.md)
— that file keeps its original name because it is a dated record of a completed
pass; its subject is this document. (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

**Four claims remain unverified and are named in the log.**

> **One of them is stronger than "unverified."** `RunControl.request_drain()`
> (§45) is **UNCONFIRMED — MAY NOT EXIST**: it was not located in LangGraph
> releases 1.2.5–1.2.11 or in the reference. **No work may be scheduled against
> it until it is confirmed against a real release or the source**, and if it
> does not exist, §45 needs a real fallback drain design rather than a
> replacement citation. Full statement in §45.

---

## From: About this document

<a id="L382"></a>
#### Original lines 382–387 › The two-document division

`agent-improve/ARCHITECTURE.md` was absorbed into this document, and on
2026-08-22 that path was **replaced by a copy of this file** — Agent Improve's
own architecture document, expected to diverge from this one as this one is
generalised across the three agents. **It is no longer a superseded tombstone.** Where this file and a `CLAUDE.md` describe the same thing, the
`CLAUDE.md` states the rule and this file states the design; neither restates
the other's job.

---

## From: 1. What Agent Improve is

<a id="L489"></a>
#### Original lines 489–493 › The runtime stack

> **THIS PARAGRAPH READ *"the installed version is below it … unavailable
> today"* UNTIL 2026-09-12**, against a venv that had satisfied the floor since
> step 2.3 landed. §1 own status line two hundred lines above it recorded that
> upgrade — *"Step 2.3 upgraded dependencies (langgraph 1.1.10 → 1.2.11 …)"* —
> so the document contradicted itself inside one section.

---

## From: 6. `PhaseState` — per-phase subgraph state

<a id="L789"></a>
#### Original lines 789–793

**Twenty-three author-populated fields** (two identity, three plumbing, eighteen
content) **plus one engine-managed value — twenty-four declared.** The managed value
is **declared but NOT populated by the input mapper**; LangGraph's execution loop
supplies it. **Any new field requires an amendment**,
whatever category it is placed in (§56).

<a id="L1001"></a>
#### Original lines 1001–1001 › Per-phase variants

**there are no per-phase state classes** (ruling 2026-09-11, step 6.20); each phase uses the shared 24-field `PhaseState` and §39.x.7 describes its

---

## From: 7. Field typing law — every captured field is a string

<a id="L1084"></a>
#### Original lines 1084–1093 › Computation results

> **"THE GRADER" WAS WRONG HERE, AND §36 IS THE REASON IT MATTERS.** This
> sentence read *"the grader answers…"* until 2026-09-23. **There are two
> graders and §36 forbids conflating them**: `DMAICGraderMiddleware` (§19.8)
> judges COACHING PROCESS QUALITY on every turn, and Layer 2d of the validation
> stack judges GATE CONTENT once, at the gate. The scan is Layer 2d's — it is
> deterministic, it runs at the gate, and it reads a list rather than a model.
> **Attributing it to the middleware put a gate check on the turn path**, which
> is where the conflation entered and what step 7.2 would have inherited. Adding typed per-phase computation fields is a violation:
it multiplies schema surface for a question a scan already answers, and it puts
the same result in two places.

---

## From: 9. The Store — cross-phase artifacts and boundary mappers

<a id="L1230"></a>
#### Original lines 1230–1249

> **⚑ CORRECTED 2026-09-13. THE PARAGRAPH THIS REPLACES CONCEDED A REASON TO A
> PARAMETER THAT HAS NEVER EXISTED.** It read *"Beyond `query` and `filter` it
> supports `mode` (`text` | `vector` | `hybrid` | `auto`), `offset`,
> `similarity_threshold`, `vector_weight` and `distance_metric`"* and concluded
> the decision *"now rests on one technical reason rather than three"*. Four of
> those eight parameters do not exist, `namespace_prefix` — which is REQUIRED —
> was not among the eight, and the concession of hybrid scoring followed
> entirely from `mode="hybrid"`.
>
> **The direction of the error is worth keeping.** It did not weaken a
> conclusion that should have held; it made a sound ruling look
> worse-supported than it was, and then flagged itself for re-examination on
> that false basis. **An error that understates your own position is not a safe
> error** — it invites revisiting a decision that was never in doubt.
>
> Source: `BIBLE_VERIFICATION_LOG.md` S-1, whose method was two documentation
> pages. Same class as C-3 and the reason **G-54** is registered; S-1 was named
> there as the one entry pinned by nothing, which is how this was found. S-1's
> verdict is corrected in place at that entry, per G-54's rule, with the
> introspection recorded.

---

## From: 15. Routing — static edges and `Command`

<a id="L1744"></a>
#### Original lines 1744–1751 › Level 1 does not route — it advances

> **A `route_after_phase` function was deleted from this section on
> 2026-08-22.** It returned `"next"` / `"escalate"` / `"retry"` — labels wired
> to nothing — and read `state["gate_attempts"]` off `SupervisorState`, where
> that field does not exist, so it would have raised `KeyError` **on the
> gate-failure path specifically.** It was a fossil of an abandoned design in
> which the supervisor owned retry and escalation; that responsibility moved
> into the phase subgraph and the function was never removed. **Do not
> reinstate it.** Full record: `agent-improve/docs/_archive/DECISIONS.md` §R2.

---

## From: 17. The Planner / Executor contract

<a id="L1864"></a>
#### Original lines 1864–1902

> planner owns outright** (G-49 closed) · **closed by:** `[6.21]`
>
> Both nodes exist, the planner emits a structured plan, and a LangSmith trace
> shows the two spans in order. **Since step 6.21 the planner's routing decision
> is executed rather than suggested**: where the plan routes to an unread
> upload, `executor()` calls `load_evidence_series` on that blob path itself and
> puts the result in front of the coach as a tool exchange. The model is not
> asked. Everything else it calls remains its own choice, and §24's *"no
> unconditional retrieval pipeline"* is untouched.
>
> **WHAT G-49 WAS, kept because the shape recurs.** Handed *"call
> `load_evidence_series` on `uploads/IMPR-2026-ED8/complaints.csv`"* the
> executor issued 18 evidence searches, read no `uploads/` blob at all, and
> ended on the 45s node timeout. Diagnosed at step 6.18 as **layer 2 — the plan
> reached no channel the model reads**: the agent was invoked with `{"messages":
> prior}`, `coaching_plan` fed the logger and the `step_log` and nothing else,
> and the one state-holding middleware never mentioned it. **The routing
> decision this section assigns to the planner was advisory in practice** — not
> a degraded split, the split not existing where it mattered.
>
> **Why C and not a prompt.** 6.18 established that the instruction was not
> being outranked, it was not arriving; and options A and B would have put it in
> front of a model that had already shown it would rank a retrieval tool above
> it. C removes the decision from the model, which is the only form of the fix
> that does not depend on how the model feels about the instruction.
>
> **The `⚠️ built with a known defect` marker was added here on 2026-09-11 and
> its ABSENCE had been the finding.** G-49 was registered on 2026-09-10 and no
> section carried a marker for it, because the code was *built* — nothing was
> missing, it misbehaved — and `☐ not built` cannot express "built and wrong".
> The board's architecture view showed this block clean while four landed steps
> sat blocked on it.
>
> **VERIFICATION STATE, stated rather than implied.** `pytest` pins the
> dispatch — that the node calls the routed path, that nothing is dispatched
> without one, that `consumed_at` is stamped by the node-issued call, and that a
> failed read leaves the turn alive. **The `live-run` halves of 6.7, 6.12 and
> 6.13 are the verification this step owes** (step 6.18's re-schedule), and they
> are what turns "the tests say so" into "the product does it".

---

## From: 19. The middleware stack — eight, in order

<a id="L2019"></a>
#### Original lines 2019–2023

**THE SIX ARE THE COMPLETE SET, AND THIS SECTION SAID OTHERWISE FOR THREE
WEEKS.** `AgentMiddleware`'s lifecycle hooks are `before_agent`, `before_model`,
`after_model`, `after_agent`, `wrap_model_call` and `wrap_tool_call` — each with
an `a`-prefixed async twin, twelve methods for six hooks. A middleware extending
this stack has these and no others.

<a id="L2025"></a>
#### Original lines 2025–2044

> **CORRECTED 2026-09-12.** This section read *"`AgentMiddleware` exposes more
> than six — the reference also lists `dynamic_prompt()`, `hook_config()` and
> `configure_trace_policy()`"*, and called the original "the six hooks" wording
> an error. **The original was right.** Those three are module-level names in
> `langchain.agents.middleware` — two decorators and a process-wide trace-policy
> setter — and are not members of `AgentMiddleware` at all. Verified against the
> installed 1.3.16 by `vars()`, not by reading the reference page a second time:
> `'dynamic_prompt' in vars(AgentMiddleware)` is `False` for all three, and
> `sorted(n for n in vars(AgentMiddleware) if not n.startswith('_'))` returns
> the twelve hook methods plus `name`, `state_schema`, `trace_policy` and
> `transformers`.
>
> **The source of the error is the reason the rule exists.** The claim came from
> `BIBLE_VERIFICATION_LOG.md` C-3, a verification pass whose whole purpose was
> to check documented claims against live documentation — and it read a MODULE's
> API page as a CLASS's member list. A verification that reads the wrong surface
> produces a confident wrong answer and stamps it CORRECTED, which is harder to
> undo than the error it replaced. C-3 is amended in place rather than deleted;
> a verification log that hides its own errors is worse than one that carries
> them.

<a id="L2051"></a>
#### Original lines 2051–2059 › Ordering rules that bind

> **⚑ CORRECTED 2026-09-10 — §56 AMENDMENT. This section stated the rule
> backwards and the built stack has been right since step 6.5.** It read
> *"Declaration order is execution order for hooks of the same kind"* and
> *"positions 6, 7 and 8 … run in declaration order: contradiction, then
> coherence, then grader"*. **Both sentences are false**, measured at 6.5
> (ruling AJ1, 2026-09-07) against LangChain's documented middleware model —
> *sequential on the way in, reverse sequential on the way back*
> (`langchain.com/blog/agent-middleware`). **Corrected here before step 7.1 is
> built against it**, which is the first step that adds to this stack.

<a id="L2096"></a>
#### Original lines 2096–2101 › Ordering rules that bind

3. ~~**Positions 4 and 5 sit on `wrap_*` hooks** and compete for no slot with
   anything else.~~ **No longer true, and it is the same conflation.** That
   held before step 6.3; since 6.3 position 1 also wraps the model call, so it
   encloses position 4 — see rule 1. Position 5 (`wrap_tool_call`) is still
   independent: a failed retrieval is not a failed model call, and
   `ModelRetryMiddleware` never sees it (§19.5).

<a id="L2239"></a>
#### Original lines 2239–2243 › 19.4 `ModelRetryMiddleware` — API-level retry

**The parameter is `max_retries`, not `retries`.** Earlier revisions of this
design wrote `ModelRetryMiddleware(retries=2)` throughout — that keyword does
not exist and would raise at construction. Corrected against the reference
signature on 2026-08-21. The two retry middlewares share the same parameter
vocabulary, which is a good reason not to remember one and guess the other.

<a id="L2279"></a>
#### Original lines 2279–2302 › 19.6 `ContradictionDetectionMiddleware` — the mid-phase check

> ### The mechanical comparison this replaced could not work — DECISIONS §R1
>
> Until 2026-08-22 this middleware did deterministic dict comparison against
> the Store. **Three defects, each verified:**
>
> 1. **It read the wrong drawer.** It called `store.get(..., current_phase)`,
>    but `gate_apply_node` is the only writer and writes at phase *end*
>    (§33.2). **Mid-phase the key does not exist**, so it read nothing, every
>    turn, by construction.
> 2. **Field-name matching finds almost nothing.** Of 41 distinct content
>    fields across the five `{Phase}Output` schemas, **38 are unique to exactly
>    one phase** — `baseline_estimate` in Define, `baseline_mean` in Measure,
>    the
>    same quantity deliberately differently named. **93% cannot cross-phase
>    name-match at all.**
> 3. **The 3 shared names are all prose** — `issues_and_barriers`,
>    `secondary_metrics`, `process_owner_buyin` — where `!=` fires on any
>    rewording. False positives, not detections.
>
> **Repairing (1) leaves 3 prose fields out of 41.** Real contradictions arrive
> as natural-language prose referencing prior committed values under different
> field names, which needs semantic understanding. **Dict comparison cannot be
> repaired into that**, which is why this was a redesign and not a fix.


---

## From: 23. The three indexes

<a id="L2696"></a>
#### Original lines 2696–2699 › 23.1 `improve_knowledge_index` — methodology

*Figures re-synced 2026-08-25 against `improve_knowledge_index_v3`. They
previously read 218 of 1,369, measured against the superseded index; the
argument above depends on the count being real, so a stale figure here weakens
the point it is making.*

<a id="L2730"></a>
#### Original lines 2730–2736 › 23.2 `improve_evidence_index` — Belt-uploaded evidence

**All twelve fields are live as of 2026-09-10** (step 6.13). The prohibition this paragraph carried — *"the live
index is the first five fields and code must not reference the other seven"* —
is **discharged**, and `azure-query` confirmed each of the seven present and
filterable on `improve_evidence_index`, with a live `kind eq 'evidence'` filter
returning documents rather than zero. **Zero is what a filter on a
metadata-buried value returns**, so the count is the check, not the presence of
the field (§23.4).

<a id="L2828"></a>
#### Original lines 2828–2836 › Two Azure behaviours govern the migration

Both new fields **backfill from `metadata`** at reindex time — `uploaded_at`
from `metadata.timestamp`, `phase` from `metadata.upload_phase`. No new data
collection is needed; the values already exist in the wrong shape, buried in a
non-sortable JSON blob where `$orderby` and `$filter` cannot reach them.

Both are **server-set**: `phase` from `state["current_phase"]` at upload,
`uploaded_at` from the server clock. A Belt-entered value for either makes it
unreliable as a filter or sort key.


<a id="L2976"></a>
#### Original lines 2976–2993 › The internal phase key is `analyse`, never `analyse_phase`

`analyse_phase` was the anomaly in **four places at once**, all renamed
together:

| Was | Now |
|---|---|
| `backend/phases/analyse_phase/` | `backend/phases/analyse/` |
| `orchestrate_analyse_phase`, `validate_analyse_phase` | `orchestrate_analyse`, `validate_analyse` |
| Graph nodes `"orchestrate_analyse_phase"`, `"validate_analyse_phase"` | `"orchestrate_analyse"`, `"validate_analyse"` |
| The key `"analyse_phase"` in `PHASE_ORDER`, v1 `phase_inputs`, `EXTRACTION_MAP`, `ORCHESTRATOR_CONTEXT_MAP`, `GATE_CHECKS`, `PhaseSummaryRecord`, `CaseDocument.phases` | `"analyse"` |

**`AnalysePhaseInput` keeps its name** — `{Phase}PhaseInput` is the convention
all five phases follow, so it was never part of the inconsistency.

**Renaming the graph node names was safe only because no checkpoints existed.**
LangGraph checkpoints record node names; had any been present, the rename would
have orphaned them. This was verified before applying — the blob container held
no `checkpoints/` prefix.


---

## From: 24. The three `rag_lookup_*` tools

<a id="L3051"></a>
#### Original lines 3051–3064

*Corrected 2026-08-21. This section previously named `search_methodology` and
`search_evidence` as the retired pair. `search_methodology` exists nowhere, and
`search_evidence` is a live retriever function §27 depends on — so the rule
contradicted §27, and a grep for the named strings would have passed while every
real retired name survived. Verification depends on literal strings.*

*Corrected again 2026-09-09, and the repetition is the point. The structured-record
subsection below shipped citing §29.1 and §7.1 for rules that live in this section's
own "RAG via tool" subsection thirty-five lines further down — §7 is the field
typing law and §29.1 is "There is no MCP". **Second wrong citation in this
section, in a document whose §55.1 governance rule is that every reference must
resolve to what it names.** The 2026-08-21 note above ends "verification depends
on literal strings"; a §-number is a literal string, and nothing checks them.*


<a id="L3153"></a>
#### Original lines 3153–3158 › The retrieval mechanism

> **Task 3B note (2026-08-21).** The brief asked whether
> `AzureAISearchRetriever` offers anything `AzureSearch` does not, and whether
> that would justify revisiting. **No such advantage was found** in the current
> reference, so the decision stands unchanged. Recorded so the question is not
> re-opened without new evidence.


---

## From: 25. Multi-query and Reciprocal Rank Fusion

<a id="L3233"></a>
#### Original lines 3233–3251 › `MultiQueryRetriever` and `EnsembleRetriever` are BANNED

> **THIS SECTION IS ALSO THE SECOND OF §9'S TWO REASONS, AND SINCE 2026-09-13
> IT IS TWO REASONS THERE RATHER THAN ONE.** §9 records why
> `improve_case_index` stays on Azure AI Search: the Store has **no multi-query
> + RRF** — this section's mechanism — and **no hybrid BM25 + vector scoring.**
> Both were re-verified by introspection rather than from a documentation page:
> `inspect.signature(BaseStore.search)` returns
> `['namespace_prefix', 'query', 'filter', 'limit', 'offset', 'refresh_ttl']`
> on the pinned `langgraph`, and the string `hybrid` occurs nowhere in the
> installed package.
>
> **§9 previously conceded the hybrid reason to a `mode="hybrid"` parameter
> that has never existed**, leaving its decision looking as though it rested on
> this section alone. It does not. Corrected at §9 and at
> `BIBLE_VERIFICATION_LOG.md` S-1 (G-54).
>
> **Note what does NOT follow.** Azure AI Search doing hybrid retrieval is why
> the gap here is *one query formulation*, not *missing BM25* — that argument
> is about Azure and is untouched. What changed is the comparison against the
> Store, which does neither.

---

## From: 26. Multi-hop retrieval

<a id="L3287"></a>
#### Original lines 3287–3305 › The hop cap is `RemainingSteps`

> **✅ FIVE → THREE. §56 amendment v1.65, founder ruling 2026-09-18, closing
> G-83.** The declared cap now matches the ceiling that was always in force.
>
> **Five was never reachable.** §25's multi-query fusion makes a hop one MODEL
> CALL plus six searches plus RRF — measured **~9.5s** — so a fifth hop landed
> near 47.5s against the executor's 40s budget. The turn died on the wall
> before the cap could fire, and `_HOP_BUDGET_SPENT` was unreachable code.
> **It was dead the day it was written**: fusion landed at step 5.2 and this
> cap at 6.7.
>
> **THIS COSTS NO CAPABILITY.** Hops four and five could never be taken. What
> changes is that the limit is now REACHABLE — the coach receives
> `_HOP_BUDGET_SPENT` and composes, instead of being cancelled mid-search.
>
> **An unreachable cap is unfalsifiable, which is how five survived eleven
> steps** — and why the arithmetic is now a test
> (`test_hop_cap.py`) rather than a comment. `MEASURED_HOP_SECONDS` carries
> its provenance so the number can be revised rather than merely trusted.
>

---

## From: 29. The data channel and the universal eight

<a id="L3597"></a>
#### Original lines 3597–3603 › 29.3 `record_field` is RETIRED and may not be reintroduced

**A tool would make capture a decision the coach might skip; structured output
makes it part of every response by construction.** That is the whole argument,
and it is why `record_field` is not among the universal tools. *(The set became
eight on 2026-09-09 when `load_evidence_series` joined it — §29.2. This sentence
previously read "which is why the universal count is seven rather than eight",
counting `record_field` as the absent eighth; the eighth is now a different tool
and the argument here is unchanged.)*

---

## From: 30. Computation tools and per-phase binding

<a id="L3688"></a>
#### Original lines 3688–3705 › Tool sets are per phase, not universal

> built exactly as tabled; the per-phase TOTALS above are the ratified figure,
> not the live one.** `_executor_tools` binds `len(UNIVERSAL_TOOLS)` — **six**,
> because `check_gate_status` (7.1) and `request_human_approval` (7.5) are
> unbuilt — so what `create_agent` actually receives today is
> **7 / 14 / 11 / 7 / 11**. Both steps must return here.
>
> **⚠ FOUR DIFFERENT FIGURES FOR THIS ONE QUANTITY were in the tree on
> 2026-09-11**, which is why this marker states the live bind rather than only
> the ceiling: this table's ratified **9/16/13/9/13**; procedure step 5.4's
> Done-when at the superseded **8/15/12/8/12**; the live bind at
> **7/14/11/7/11**; and `test_computation.py`'s own docstring describing the
> live bind as **6/13/10/6/10**, stale by one since `load_evidence_series`
> landed at 6.12. The test asserting the ratified figure was named
> `test_per_phase_totals_are_8_15_12_8_12` while asserting 9/16/13/9/13.
> **This is the caption-outliving-its-list failure step 6.16 exists to end,
> found inside the test file that records WATCH 25 to prevent it.** All four
> are reconciled in that commit, and `verify_built.py` now pins the LIVE bind
> — the figure none of the four was measuring.

---

## From: 33. The nine-step HITL gate

<a id="L3875"></a>
#### Original lines 3875–3876

>
> **⛑ CORRECTED 2026-09-11 — this line read *"Nothing in the system currently pauses for a human"*, and one thing does.** `ContradictionDetectionMiddleware.after_agent` calls `langgraph.types.interrupt` at middleware position 6 and has since step 6.5 (§19.6). **The blanket claim was wrong for six steps and nothing re-read it**; it was found by the `ast` call-site probe added to `verify_built.py` on the same day, after the line-matching first cut of that probe returned 3 and the parse returned the true 1. **The distinction is not pedantic:** a contradiction interrupt fires today into a system with **no built route that can resume it** — §49's `/gate/approve` and `/gate/reject` are unbuilt — so the turn suspends and the Belt has no way forward. **That is a worse state than not pausing at all**, and it is invisible while the marker says nothing pauses. Step 7.3 owns the resume path; **the fact that something could already suspend is what made 7.3 urgent rather than merely next**. **⛑ RESOLVED THE SAME DAY, and this marker is true again for a different reason.** The founder ruled position 6 **GUARDED** until 7.3 (§19.6's marker carries the measurement): detection continues, enforcement is suspended, and one commented line restores it. So *"nothing pauses for a human"* is accurate today — **but it is now a decision with a tripwire test rather than an absence nobody had checked, and that difference is the whole point of the exercise.** **STEP 7.3 RESTORES BOTH INTERRUPTS** — `gate_review`'s, and position 6's commented line — in the same commit, and takes `verify_built.py`'s call-site count from 0 to 2

---

## From: 37. Mid-phase contradiction and the re-approval cascade

<a id="L4349"></a>
#### Original lines 4349–4370 › The check runs every turn, not only at gates

> ### ⛑ CORRECTED 2026-09-23 — THIS SECTION NAMED A STOP MECHANISM THAT WAS
> ### RULED NEVER TO EXIST
>
> It read *"`ContradictionDetectionMiddleware` (§19.6) reads the flag on
> `after_agent` and **raises `HITLInterrupt`**"*. **`HITLInterrupt` is
> DELIBERATELY NEVER DEFINED** — ruling v1.21(D), 2026-09-10, carried since as
> G-15: step 7.3 pauses with LangGraph's own `interrupt()`, which is resumable
> by construction, and **an exception raised from `after_agent` is not**.
> Defining one would create a second pause mechanism competing with the
> framework primitive §0.24 requires preferring.
>
> **So the section specified a mechanism whose own ruling forbids it**, and
> anything built to this text would have built the forbidden thing. The naming
> was left open as *"a naming problem"* in v1.21 and v1.22; it is closed here
> by naming what actually pauses.
>
> **THE PLACEMENT IS A SEPARATE QUESTION AND IT IS STEP 6.44's.** `interrupt()`
> cannot be raised from middleware and be resumable — **a stop belongs in a
> node**. Detection stays exactly where it is (the coach sets the flag in the
> reply it already writes, no extra model call); the planner routes on it; the
> stop lives in a node that writes nothing, so a resumed turn writes once
> rather than twice. This section states WHAT pauses; 6.44 builds WHERE.

---

## From: 39. The five phases

<a id="L4479"></a>
#### Original lines 4479–4483

| **Define** | A measurable problem, its scope, a SMART goal, the customer's voice, the team, a rough baseline, a target and a date, a SIPOC with KPIs | **12 required fields — no tiers** (§39.1) |
| **Measure** | A validated baseline, a data collection plan, a detailed process map, prioritised X's, a stability assessment | 7 Tier 1 fields |
| **Analyse** | A specific root cause, the evidence validating it, and how much of the problem it explains | 4 Tier 1 fields |
| **Improve** | A selected solution, a pilot result, and a stated position on experimentation | 4 Tier 1 fields |
| **Control** | A five-part control plan and the post-improvement measurement | 3 Tier 1 fields |

<a id="L4510"></a>
#### Original lines 4510–4517 › 39.1 Define phase, complete specification

> **Numbering note.** The ratifying amendment proposed this as a new §41. **§41
> was already taken** — "Structured dict fields, and FMEA", RATIFIED, cited 23
> times in this document, three times in `CLAUDE.md` §10.8, and mapped in
> Appendix A. Sections run 1–68 with no gaps, so there was no free two-level
> number in Part VIII. Placing Define at **§39.1** expands the very row of §39's
> table that describes it, costs no citation, and gives §39.2–§39.5 to the other
> four phases when they land (§39.1.8). Founder ruling, 2026-08-25.


<a id="L4555"></a>
#### Original lines 4555–4565 › 39.1.2 The ordered field list — the `field_index` sequence (closes G-38)

>
> **This subsection is the authoritative statement of that ruling, as of
> 2026-09-01.** It previously lived in `docs/_archive/DEFINE_FINALIZATION_2026-08-26.md`, (archived to docs/_archive/; canonical: ARCHITECTURE.md §39.1.2)
> which `CONTINUITY.md` and `REFACTORING_PROCEDURE.md` both called authoritative;
> that file is now at `docs/_archive/`. **The ruling was merged; two of its field
> names deliberately were not.** It still writes field 5 as `baseline` and field 8
> as `target_metric`, both superseded — `baseline` re-introduces the collision
> that founder ruling v1.13 reversed, and the v1.15 metric-registry rename made
> the current names `baseline_estimate` and `target_value` (§0.19, §0.20 in
> `CLAUDE.md`). **The table above carries the current names. Do not re-apply the
> archived file verbatim.**

<a id="L4651"></a>
#### Original lines 4651–4656 › 39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor)

> **Authority: THE FILES, not this section.** The flip this note
> anticipated happened on 2026-09-13 (brief step 8).
> `skills/dmaic-define-phase/coaching_script.md` is the script and
> `skills/dmaic-define-phase/SKILL.md` is what ships; **this section is
> the pointer it said it would reduce to.** On conflict the files win,
> and the check that keeps them agreeing compares the two files.

<a id="L4665"></a>
#### Original lines 4665–4670 › 39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor)

**The script itself is `skills/dmaic-define-phase/coaching_script.md`.**
It left this document on 2026-09-13 (brief step 8) and now sits beside
the `SKILL.md` it must match, in the phase directory that ships it.
`verify_built.py`'s *phase scripts byte-matching* check compares the two
FILES — a comparison a reader can run with `diff`, where the old one
required slicing a 965 KB document at a heading first.

<a id="L4674"></a>
#### Original lines 4674–4678 › 39.1.8 The other four phases

Measure, Analyse, Improve and Control follow **this exact section shape**, and
take §39.2–§39.5 as they land. **Measure is specified at §39.2** (2026-08-26);
Analyse, Improve and Control remain stubbed, their field lists blocked on
**G-27** (mappers) and **G-28** (gate assembly). **Define and Measure are the
ratified exemplars.**

<a id="L4696"></a>
#### Original lines 4696–4703 › 39.1.9 The metric registry and Define's placeholder

> **12 coached against 13 gate-required looks like a defect and is not.** It was
> raised as one by the 2026-09-14 structure audit — *"the Belt can complete every
> coached field and still fail the gate on one nobody asked for"* — and the tree
> disproves it: `SKILL.md` position 5 reads **`[5 · baseline_estimate · required ·
> also captures metric_definitions]`**, and says *"this one field-ask fills two
> fields, and the Belt should not have to know that."* **The finding was that the
> spec did not say so, which is what this subsection fixes.**


<a id="L4719"></a>
#### Original lines 4719–4722 › 39.1.9 The metric registry and Define's placeholder

**This subsection states ONCE what §63.1's type comment and §63.9's table row
have carried separately; neither is superseded.** Ratified 2026-09-23 with the
procedure amendment, and it is what unblocks step 6.20's scorecard half — which
was not blocked on code but on this shape never having been written down.

<a id="L4726"></a>
#### Original lines 4726–4730 › 39.1.10 Tools bound to Define

**Seven**, and the count is owned by the live bind, not by this list —
`COMPUTATION_TOOLS_BY_PHASE` in `knowledge/computation.py` plus
`UNIVERSAL_TOOLS`, re-run every commit by `verify_built.py`'s *LIVE per-phase
tool bind* check. Define is the lightest of the five by design: scoping is a
conversation, not a calculation.

<a id="L4742"></a>
#### Original lines 4742–4744 › 39.1.12 State parameters — Define's use of `PhaseState`

**There is no `DefineState`.** §39.x.7 describes per-phase USE of the shared
24-field `PhaseState` — **S-C03 carries that ruling**, and G-19 was closed by it
on 2026-09-11. Define reads `asks`, `uploads`, `artifacts`, `coaching_plan` and

<a id="L4766"></a>
#### Original lines 4766–4780 › 39.1.14 Cross-phase reads and writes

> ### ⚠ WHY 39.1.9–39.1.14 ARE APPENDED RATHER THAN INTERLEAVED
>
> The other four phases carry these topics at positions 3, 5, 6, 7, 8 and 11.
> **Inserting them in that order here would renumber 39.1.3–39.1.8, and
> `§39.1.2` is already cited from §56.1.** A renumbered citation resolves
> silently to the wrong subsection — §0.2's failure mode, in a document rather
> than a registry.
>
> **So reading order is not numbering order, deliberately**, on the precedent
> Appendix D set when `Zone` and `Impact` were *"appended rather than inserted
> deliberately"* because two readers matched on column position.
>
> **Five of these six document what is already built** and cite the owner rather
> than restating it — the spec was behind the tree, not ahead of it. **Only
> 39.1.11 names something unbuilt**, and it is owned by step 7.3.

<a id="L4821"></a>
#### Original lines 4821–4823 › 39.2.2 The ordered field list — the `field_index` sequence

`MeasureOutput` = these ten **+** `phase_metrics` (§39.2.3) **+** four
gate-metadata fields = **15** (was 14; §40's count rises by `phase_metrics`).
**7 Tier 1, 3 Tier 2** — Measure keeps both tiers, unlike Define (§35).

<a id="L4909"></a>
#### Original lines 4909–4914 › 39.2.5 Tools bound to Measure

view the executor is one node (§13). **Fifteen — the phase maximum**, under the
16 cap (§30).

- **The universal eight** (§29.2), on every phase: `rag_lookup_methodology`,
  `rag_lookup_evidence`, `rag_lookup_case_history`, `propose_template`,
  `propose_diagram`, `check_gate_status`, `request_human_approval`.

<a id="L4963"></a>
#### Original lines 4963–4963 › 39.2.7 State parameters — Measure's use of `PhaseState`

*Indexes §6 / §58.2 — **S-C02**; nothing re-defined.* **There is no `MeasureState`.** Measure uses the shared **24-field `PhaseState`**; this table is its USAGE — which Measure field each shared field carries, and who reads it:

<a id="L5012"></a>
#### Original lines 5012–5045 › 39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor)

> **Authority: THE FILES, not this section.** The flip this note
> anticipated happened on 2026-09-13 (brief step 8).
> `skills/dmaic-measure-phase/coaching_script.md` is the script and
> `skills/dmaic-measure-phase/SKILL.md` is what ships; **this section is
> the pointer it said it would reduce to.** On conflict the files win,
> and the check that keeps them agreeing compares the two files.

> **What lives here and what does not.** This section carries the **coaching
> script** — the opening, the metric-literacy explanation, one block per field
> in §39.2.2's order, one seven-step block per bound tool, and the closing. The
> SKILL.md additionally carries its front matter, the A→F session flow, the
> field-order table, templates, uploads, capture instructions, the Document
> Layout, pitfalls, cross-phase tables and `MEASURE_RUBRIC` — **those are not
> duplicated here**, and several have their own home in §39.2.2, §39.2.9 and
> §39.2.11.

> **Coaching pattern for every field:** ① **Explain** (plain language, why it
> matters) → ② **Show** (worked example, visually distinct, illustration only)
> → ③ **Ask** (invite the Belt's version) → ④ **Confirm** (reflect back, check,
> advance). Tone: warm, encouraging, never gatekeeping. Assume a capable but
> possibly non-expert Belt. Responses follow §50.1 structure — sectioned,
> scannable, never bulk prose.

> **Every computation tool follows the seven-step pattern** (§43.1), every time:
> ① educate on the concept → ② explain why now → ③ guide data preparation →
> ④ run → ⑤ interpret → ⑥ visualise → ⑦ coach the next move. **Step 1 is the one
> most often skipped and the one that matters most.**

**The script itself is `skills/dmaic-measure-phase/coaching_script.md`.**
It left this document on 2026-09-13 (brief step 8) and now sits beside
the `SKILL.md` it must match, in the phase directory that ships it.
`verify_built.py`'s *phase scripts byte-matching* check compares the two
FILES — a comparison a reader can run with `diff`, where the old one
required slicing a 965 KB document at a heading first.

<a id="L5066"></a>
#### Original lines 5066–5069 › 39.2.12 The other two phases

Improve and Control follow **this same section shape** and take §39.4–§39.5 at
their own reviews. Their field lists remain blocked on **G-27** (mappers) and
**G-28** (gate assembly). **Define, Measure and Analyse are the ratified
exemplars; the other two are stubbed.**

<a id="L5111"></a>
#### Original lines 5111–5112 › 39.3.2 The ordered field list — the `field_index` sequence

`AnalyseOutput` = these nine **+** `phase_metrics` (§39.3.3) **+** four
gate-metadata fields = **14**. 4 Tier 1, 5 Tier 2.

<a id="L5178"></a>
#### Original lines 5178–5179 › 39.3.5 Tools bound to Analyse

Passed to the executor via `tools=` on `create_agent` (§18). **Twelve** — under
the 16 cap (§30).

<a id="L5231"></a>
#### Original lines 5231–5231 › 39.3.7 State parameters — Analyse's use of `PhaseState`

*Indexes §6 / §58.2 — **S-C02**; nothing re-defined.* **There is no `AnalyseState`.** Analyse uses the shared **24-field `PhaseState`**; this table is its USAGE — which Analyse field each shared field carries, and who reads it — note this is the phase where multi-hop is real:

<a id="L5273"></a>
#### Original lines 5273–5306 › 39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor)

> **Authority: THE FILES, not this section.** The flip this note
> anticipated happened on 2026-09-13 (brief step 8).
> `skills/dmaic-analyse-phase/coaching_script.md` is the script and
> `skills/dmaic-analyse-phase/SKILL.md` is what ships; **this section is
> the pointer it said it would reduce to.** On conflict the files win,
> and the check that keeps them agreeing compares the two files.

> **What lives here and what does not.** This section carries the **coaching
> script** — the opening, the two-movements framing, the metric-literacy
> explanation, the 5-Whys sequence, one block per field in §39.3.2's order, the
> test-selection sequence, one seven-step block per bound tool, and the closing.
> The SKILL.md additionally carries its front matter, the A→F session flow, the
> field-order table, templates, uploads, capture instructions, the Document
> Layout, pitfalls, cross-phase tables and `ANALYSE_RUBRIC` — **those are not
> duplicated here**.

> **Coaching pattern for every field:** ① **Explain** (plain language, why it
> matters) → ② **Show** (worked example, visually distinct, illustration only)
> → ③ **Ask** (invite the Belt's version) → ④ **Confirm** (reflect back, check,
> advance). Tone: warm, encouraging, never gatekeeping. Assume a capable but
> possibly non-expert Belt. Responses follow §50.1 structure — sectioned,
> scannable, never bulk prose.

> **Every computation tool follows the seven-step pattern** (§43.1), every time:
> ① educate on the concept → ② explain why now → ③ guide data preparation →
> ④ run → ⑤ interpret → ⑥ visualise → ⑦ coach the next move. **Step 1 is the one
> most often skipped and the one that matters most.**

**The script itself is `skills/dmaic-analyse-phase/coaching_script.md`.**
It left this document on 2026-09-13 (brief step 8) and now sits beside
the `SKILL.md` it must match, in the phase directory that ships it.
`verify_built.py`'s *phase scripts byte-matching* check compares the two
FILES — a comparison a reader can run with `diff`, where the old one
required slicing a 965 KB document at a heading first.

<a id="L5328"></a>
#### Original lines 5328–5330 › 39.3.12 The other phase

Control follows this same section shape and takes §39.5 at its own review.
**Define, Measure, Analyse and Improve are now the ratified exemplars; only
Control remains stubbed.**

<a id="L5371"></a>
#### Original lines 5371–5372 › 39.4.2 The ordered field list — the `field_index` sequence

`ImproveOutput` = these nine **+** `phase_metrics` (§39.4.3) **+** four
gate-metadata fields = **14**. 4 Tier 1, 5 Tier 2.

<a id="L5413"></a>
#### Original lines 5413–5414 › 39.4.5 Tools bound to Improve

Passed to the executor via `tools=` on `create_agent` (§18). **Eight** — under the
16 cap (§30).

<a id="L5465"></a>
#### Original lines 5465–5465 › 39.4.7 State parameters — Improve's use of `PhaseState`

*Indexes §6 / §58.2 — **S-C02**; nothing re-defined.* **There is no `ImproveState`.** Improve uses the shared **24-field `PhaseState`**; this table is its USAGE — which Improve field each shared field carries, and who reads it:

<a id="L5505"></a>
#### Original lines 5505–5545 › 39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor)

**Authority is the FILES as of 2026-09-13 (brief step 8).** The script is
`skills/dmaic-improve-phase/coaching_script.md`; `skills/dmaic-improve-phase/SKILL.md`
is what ships and must contain it verbatim. This section describes the SHAPE
and no longer carries the content,  **embedded here in §39.1.7's format** — preamble, phase opening
(an Analyse-recap: show the Belt the `root_cause_statement` and
`practical_significance` they arrive with), one Explain/Show/Ask/Confirm block per
field in §39.4.2 order, the seven-step block for `calculate_doe_main_effects`, the
two-movements framing, the decision-matrix and pilot-plan coaching, metric
literacy (§39.4.8), gate-readiness closing. **Authoritative during the refactor.**

> **Verify first — do not assume.** Whether `skills/dmaic-improve-phase/SKILL.md`
> already exists must be checked by listing the directory, not by a search miss
> (the Analyse SKILL.md existed when a search suggested it did not, 43c4201). If it
> exists, **restructure and conform, do not overwrite** sound content; if not,
> write it from this section.

> **What lives here and what does not.** This section carries the **coaching
> script**. The SKILL.md additionally carries its front matter, the A→F session
> flow, the field-order table, templates, uploads, capture instructions, the
> Document Layout, pitfalls, cross-phase tables and `IMPROVE_RUBRIC` — **those
> are not duplicated here**, and several have their own home in §39.4.2, §39.4.9
> and §39.4.11.

> **Coaching pattern for every field:** ① **Explain** (plain language, why it
> matters) → ② **Show** (worked example, visually distinct, illustration only)
> → ③ **Ask** (invite the Belt's version) → ④ **Confirm** (reflect back, check,
> advance). Tone: warm, encouraging, never gatekeeping. Assume a capable but
> possibly non-expert Belt. Responses follow §50.1 structure — sectioned,
> scannable, never bulk prose.

> **Every computation tool follows the seven-step pattern** (§43.1), every time:
> ① educate on the concept → ② explain why now → ③ guide data preparation →
> ④ run → ⑤ interpret → ⑥ visualise → ⑦ coach the next move. **Step 1 is the one
> most often skipped and the one that matters most.**

**The script itself is `skills/dmaic-improve-phase/coaching_script.md`.**
It left this document on 2026-09-13 (brief step 8) and now sits beside
the `SKILL.md` it must match, in the phase directory that ships it.
`verify_built.py`'s *phase scripts byte-matching* check compares the two
FILES — a comparison a reader can run with `diff`, where the old one
required slicing a 965 KB document at a heading first.

<a id="L5612"></a>
#### Original lines 5612–5620 › 39.5.2 The ordered field list — the `field_index` sequence

`ControlOutput` = these twelve **+** `phase_metrics` (§39.5.3) **+** four
gate-metadata fields = **17** (was 16; `actual_close_date` is the added field).
**3 Tier 1, 9 Tier 2.**

> **F-12 recommendation:** `actual_close_date` is **Tier 2** — a slipped date does
> not invalidate the improvement (the same logic that makes Define's `target_date`
> a planning parameter, §39.1.2). It is the paired value Control captures against
> Define's planned `target_date`. §40 count rises 16 → 17; §35's Control row
> becomes 3 Tier 1 / 9 Tier 2.

<a id="L5671"></a>
#### Original lines 5671–5672 › 39.5.5 Tools bound to Control

Passed to the executor via `tools=` on `create_agent` (§18). **Twelve** — under the
16 cap (§30).

<a id="L5725"></a>
#### Original lines 5725–5725 › 39.5.7 State parameters — Control's use of `PhaseState`

*Indexes §6 / §58.2 — **S-C02**; nothing re-defined.* **There is no `ControlState`.** Control uses the shared **24-field `PhaseState`**; this table is its USAGE — which Control field each shared field carries, and who reads it:

<a id="L5768"></a>
#### Original lines 5768–5809 › 39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor)

**Authority is the FILES as of 2026-09-13 (brief step 8).** The script is
`skills/dmaic-control-phase/coaching_script.md`; `skills/dmaic-control-phase/SKILL.md`
is what ships and must contain it verbatim. This section describes the SHAPE
and no longer carries the content,  **embedded here in §39.1.7's format** — preamble, phase opening (an
Improve-recap: show the Belt the `selected_solution` and `pilot_result` they arrive
with, and the Define `target_value` they are closing against), one
Explain/Show/Ask/Confirm block per field in §39.5.2 order, the seven-step block for
each control-chart tool and `post_improvement_cpk`, the two-movements framing, the
five-part control-plan coaching, metric literacy (§39.5.8), and a **project-closure
closing** (not "advance to the next phase" — there is none). **Authoritative during
the refactor.**

> **Verify first — do not assume.** Whether `skills/dmaic-control-phase/SKILL.md`
> already exists must be checked by listing the directory, not by a search miss (the
> Analyse and Improve SKILL.md both existed when a search suggested otherwise). If it
> exists, **restructure and conform, do not overwrite** sound content; if not, write
> it from this section.

> **What lives here and what does not.** This section carries the **coaching
> script**. The SKILL.md additionally carries its front matter, the A→F session
> flow, the field-order table, templates, uploads, capture instructions, the
> Document Layout, pitfalls, cross-phase tables and `CONTROL_RUBRIC` — **those
> are not duplicated here**.

> **Coaching pattern for every field:** ① **Explain** (plain language, why it
> matters) → ② **Show** (worked example, visually distinct, illustration only)
> → ③ **Ask** (invite the Belt's version) → ④ **Confirm** (reflect back, check,
> advance). Tone: warm, encouraging, never gatekeeping. Assume a capable but
> possibly non-expert Belt. Responses follow §50.1 structure — sectioned,
> scannable, never bulk prose.

> **Every computation tool follows the seven-step pattern** (§43.1), every time:
> ① educate on the concept → ② explain why now → ③ guide data preparation →
> ④ run → ⑤ interpret → ⑥ visualise → ⑦ coach the next move. **Step 1 is the one
> most often skipped and the one that matters most.**

**The script itself is `skills/dmaic-control-phase/coaching_script.md`.**
It left this document on 2026-09-13 (brief step 8) and now sits beside
the `SKILL.md` it must match, in the phase directory that ships it.
`verify_built.py`'s *phase scripts byte-matching* check compares the two
FILES — a comparison a reader can run with `diff`, where the old one
required slicing a 965 KB document at a heading first.

---

## From: 40. The five `{Phase}Output` schemas

<a id="L5879"></a>
#### Original lines 5879–5884 › Field counts

**Every total rose by one for `phase_metrics`** (§63.9), which is now the third
field on all five schemas. **Define rose by two**: it also carries
`metric_definitions` (§63.8), the registry itself, which no other phase holds.
**Define's 12-position coached walk is unchanged** — the registry is captured
inside position 5's conversation, where the Belt names their metrics, rather
than at a thirteenth position (§39.1.2). Twelve coached, thirteen gate-required.

<a id="L5901"></a>
#### Original lines 5901–5904 › The four gate-metadata fields

**`citations` and `uploads` were on `PhaseState` but missing from the Output
schemas in an earlier revision** — the evidence trail reached state and then
stopped, never arriving in the document that records what the phase was
grounded in.

---

## From: 45. Timeouts and compensating actions

<a id="L6298"></a>
#### Original lines 6298–6298

**Status: RATIFIED — BLOCKED on the LangGraph upgrade.**

<a id="L6382"></a>
#### Original lines 6382–6385 › Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST**

> **This is the same failure mode as `ModelRetryMiddleware(retries=...)`**
> (§19.4) — a plausible API name, adopted once, never re-verified, sitting in a
> document implementers copy. That one was caught. This one is still open.
>

<a id="L6403"></a>
#### Original lines 6403–6408 › Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST**

**The dependency this sits behind is separate and IS met:** everything in this
section requires LangGraph ≥1.2.6, which step 2.3 satisfied (§53). **That
changes nothing about the question above** — `RunControl.request_drain()` is
gated on the API being shown to exist at all, not on a version, which is why the
two were stated separately.


---

## From: 49. API surface

<a id="L6639"></a>
#### Original lines 6639–6659 › Endpoints

> **SPEC-GAP (G-47): this table is still not what the tree serves.** Adding
> `/upload` closed one row of a wider drift, and registering the rest is how
> §55.1's bidirectional rule stays honest. **Seven routes exist in
> `gateway/routes.py` and in neither this table nor S-F34's copy of it** —
> `/health`, `/summarise`, `/context`, **`POST /cases`**, `POST /gate`,
> `/gate/review/{case}/{phase}` and `/files/{case}/{file}`. **`POST /cases` was
> added to this list on 2026-09-11**: the register said six and the tree served
> seven, because this table's `GET /cases` row was read as covering the path
> rather than the verb. **It is the sharpest omission of the seven after
> `POST /gate`** — step 6.8's own Done-when opens *"`POST /cases` writes the
> case record to the Store"*, so a ratified step names a route this section
> does not, which is precisely the direction §55.1's bidirectional rule exists
> to catch. **`POST /gate` is the sharpest of them**: this
> table ratifies `/gate/submit`, `/gate/approve` and `/gate/reject`, and the
> tree serves one route where the spec names three, so the disagreement is a
> shape, not an omission. `/ask/stream` is the reverse case and is NOT part of
> this gap — ratified, unbuilt, and owned by step 10.1. **Registered rather
> than fixed in passing**: which of the six are ratified, which are v1 residue
> due to die at 11.1, and whether `/gate` becomes three routes are founder
> questions, and §8's rule is that a table is not amended while making a
> feature change. Raised 2026-09-08 while scoping 6.11 — Part AP5.

---

## From: 50. UI and language rules

<a id="L6701"></a>
#### Original lines 6701–6709 › 50.1 Coach response structure

>
> The built `CoachingResponse` carries `message`, `fields_captured`, `citations`
> and `contradiction_flag` — see S-C05's marker. **Until step 6.19 declares
> them, this rule is stated and unenforced**, and the five SKILL.md files
> instruct the coach to populate four fields the response schema cannot
> receive — which is why **WATCH 9 is NOT closed by step 6.9**, contrary to
> that step's own body. **6.19 declares them; 10.2 renders them and cannot run
> first.**


<a id="L6724"></a>
#### Original lines 6724–6729 › 50.1 Coach response structure

> **UI note.** The *rendering* of these fields belongs to the UI rebuild — no
> production UI exists for Agent Improve yet. **This section defines the
> contract** (the schema carries the structure, §50 mandates it); the UI
> implements it when built. The schema half landed 2026-08-25; the UI half is
> tracked as a `CONTINUITY.md` watch.


<a id="L6813"></a>
#### Original lines 6813–6819 › The live gate document

> **This generalises what `dmaic-measure-phase/SKILL.md` §8 already specifies.**
> It is stated here rather than in one phase's skill because a rule that lives
> in the one file that already follows it cannot bind the four that do not.
> `dmaic-define-phase/SKILL.md` is back-applied; **Analyse, Improve and Control
> carry it when they are written.** It may be back-ported to the root
> `AGENTIC_ARCHITECTURE_REFERENCE.md` once Improve settles (§8).


---

## From: 53. Configuration, dependencies and deployment

<a id="L7017"></a>
#### Original lines 7017–7025 › Dependency floor

> **THIS SECTION CALLED THE UPGRADE A BLOCKER UNTIL 2026-09-12, THREE WEEKS
> AFTER STEP 2.3 PERFORMED IT.** It tabled `langgraph` **1.1.10** as installed
> against a venv running 1.2.11, and `langchain-core` 1.3.3 against an installed
> 1.6.0. **The table was the defect, not the numbers in it.** An `Installed`
> column in a document is a copy of a fact `pip` owns; it can be right only
> between upgrades, and it goes wrong silently at the moment the project
> improves. Replaced by floors, which are rules and do not move, and a pointer
> to the manifest, which is the fact.


<a id="L7124"></a>
#### Original lines 7124–7137 › 53.1 Migration sequence

**The phase schemas are rewritten in place** — `{Phase}PhaseInput` becomes
`{Phase}Output` in the same file. No parallel schema, no deprecation window, no
retirement step. There is no production consumer to protect, and the two models
are near-disjoint: of Define's **12 required fields, exactly two names match the
v1 schema** — `goal_statement` and `target_date`. The other ten are new names
for values v1 held under different ones (`how_much_baseline` → `baseline_estimate`,
`primary_metric` → `target_value`, `secondary_metric` → `secondary_metrics`,
`business_case_rationale` → `business_case`, `team_members` → `team`,
`scope_in`/`scope_out` → `project_scope`, `sipoc` → `process_map_sipoc`, the
seven granular 5W2H fields → one composed `problem_statement`), or values v1
never held at all (`voc_summary`, `issues_and_barriers`). Two conversions bind:
`team_members` from `list[TeamMember]` to `list[dict]` (§39.1.4), and `sipoc`
gains `process_metrics` as its sixth key (§41).


---

## From: 55. Anti-drift

<a id="L7205"></a>
#### Original lines 7205–7213

> **THE TABLE READ "THREE MECHANISMS" UNTIL 2026-09-11, AND THE ONE IT OMITTED
> IS THE ONLY ONE THAT BLOCKS ANYTHING.** The drift hook warns before a write;
> the skill is invoked by choice; the constitution is read. **The commit-msg
> guard refuses.** It has carried enforcing rules since 2026-08-31 and this
> section — the section named *Anti-drift* — did not list it, which is the same
> shape as the findings §55.1 records: a correct mechanism paired with a
> document that cannot see it. Found while adding rule 6, by rule 2b blocking
> the commit that added it.


<a id="L7301"></a>
#### Original lines 7301–7309 › 55.1 Spec-layer governance rules

> **Why this was narrowed rather than left as written.** The first run (§66.8)
> checked 58 edges and reported 36 non-closures. **Re-run under this narrowed
> scope, 29 fall out and 7 remain — of which 5 are real wiring defects.**
> Signal-to-noise moves from 5-in-36 to 5-in-7. **86% noise is how a check gets
> ignored**, and an ignored check is recorded as evidence while proving nothing.
> That is the R2 lesson arriving from the opposite direction to the three
> instances §55 already records: not a check that cannot fail, but a check that
> fails so often its failures stop being read. **Narrowing the scope is the
> resolution of finding F-07.**

<a id="L7328"></a>
#### Original lines 7328–7331 › 55.2 The BUILT markers, and the paths that oblige a re-check

**A `> **BUILT:**` line sits under the item it describes**, never in a parallel
table. `docs/_archive/ARCHITECTURE_STATUS.md` held that parallel table until 2026-09-10
and is archived; the same fact in two files is what this section exists to
prevent.

<a id="L7355"></a>
#### Original lines 7355–7362 › 55.2 The BUILT markers, and the paths that oblige a re-check

> **What was wrong.** `READY` rendered GREEN, the same family as `DONE`, so an
> unstarted step read as finished. ORANGE meant both *"building now"* (a
> position in the plan) and *"built and wrong"* (a quality of the code). RED
> meant both *"blocked"* and *"not built"*, when not-built is the ordinary
> state of scheduled work. **A lane state and a marker state may never share a
> colour**: one is where a thing sits in the plan, the other is whether it
> works, and a reader cannot hold both off one hue.
>

<a id="L7369"></a>
#### Original lines 7369–7408 › 55.2 The BUILT markers, and the paths that oblige a re-check

> **A MARKER NOTHING RE-RUNS IS A CLAIM.** `.claude/hooks/verify_built.py`
> re-runs the counting commands against the tree and reports any marker that
> disagrees. **Twenty checks plus the five-phase script byte-match**, against
> the pinned venv.
>
> **AND SINCE 2026-09-11 `pytest` RUNS THEM, which is the difference between a
> guard and a habit.** `backend/tests/test_built_markers.py` parametrises the
> table one test per check, so rule 4 of the commit-msg guard enforces all 21
> on every spine commit and a failure names **which marker went stale** rather
> than reporting that the hook exited non-zero. **Until then nothing invoked
> it**: no hook, no CI step, only a human remembering the command — which is
> this section's own failure mode applied to the thing guarding against it.
> *A check nobody runs and a check that passes look identical until you run
> it.*
>
> **The check COUNT is pinned separately**, because parametrising over a list
> means deleting a check deletes its test and the suite goes green — the
> cheapest possible answer to a red build. It may only move in a commit that
> means to move it.
>
> **Cost: ~2s, not ~49s.** `py()` skips its subprocess when the running
> interpreter is already the pinned venv, which it is under `pytest`, so the
> eleven probes stop paying a cold `langchain` import each. WATCH 2's rule is
> about WHICH interpreter answers, not about spawning one, and the subprocess
> path still applies to every other caller. **A check people wait 49s for is a
> check someone eventually skips.**
>
> **It ran eleven until 2026-09-11, and all eleven passed against four wrong
> markers.** §49's contradicted itself, §33's asserted an absence the tree
> disproved, §19.6's called a consumed flag inert, and S-C05 had no marker at
> all while the class was built at half its fields. **What the eleven had in
> common is the lesson: every one counted a POPULATION** — routes, tools,
> files — **and not one pinned a VALUE or a SET.** A count of eleven routes
> agrees with the tree whatever the routes are called and whichever of them
> the spec covers. The ten added that day pin sets, constants and field lists,
> and one of them — `interrupt()` call sites, parsed with `ast` — found the
> §33 defect on its first run. **The rule comes from the row it cost most on**: *"1 of 5 SKILL.md
> files written"* was copied from `CONTINUITY.md` on the day the status file was
> created and was wrong from its first commit, in the one place whose header
> promised *"verified against the tree, never from a document"*.

<a id="L7410"></a>
#### Original lines 7410–7427 › 55.2 The BUILT markers, and the paths that oblige a re-check

> ### ⛑ STATUS IS LEAVING THIS DOCUMENT — §56 amendment v1.64, step 6.31
>
> **`REFACTORING_PROCEDURE.md` Appendix F is the single leading document for
> build status.** A marker here keeps the *rationale* — why a thing is shaped
> the way it is — and Appendix F carries *whether it exists today*, one row per
> step, with a resolvable anchor in every row and `verify_built.py` as a
> fail-closed referee.
>
> **§58.5 is why.** After 6.19 landed, its marker read *“✅ all 8 fields
> exist”* and, three lines later, *“the four presentational fields … are NOT
> BUILT”*. **Both sentences, one block.** Not an editing slip — the predictable
> outcome of storing a STATUS inside a RATIONALE, where the eye goes to the
> prose and the status rides along unmaintained.
>
> **MIGRATION IS ONE MARKER AT A TIME, BY JUDGEMENT, AND IS NOT A SCRIPT.** A
> marker's prose has to be read to know which half is which. **A marker that
> still states a status is mid-migration, not authoritative** — and the four
> colours below keep their meanings unchanged for the ones that have not moved.

<a id="L7429"></a>
#### Original lines 7429–7431 › 55.2 The BUILT markers, and the paths that oblige a re-check

**Guard rule 2b requires the file carrying these markers staged whenever a
commit touches a path they tabulate.** Thirteen paths, deliberately narrow — a
guard that fired on every backend file would be routed around inside a week:

<a id="L7448"></a>
#### Original lines 7448–7481 › 55.2 The BUILT markers, and the paths that oblige a re-check

> ### ⛔ `board.html` WAS THE THIRTEENTH AND IS REMOVED, 2026-09-14
>
> **A WATCHED PATH MUST BE A SOURCE OF TRUTH, NEVER THE OUTPUT OF A
> GENERATOR.** That is the contract this list is now held to, and it is
> enforced — `test_no_watched_path_is_a_generators_output` fails if a
> generator's output is added back.
>
> **The entry was ratified here, not slipped in**, added 2026-09-11 with step
> 6.16 and argued for in this section: *"It carries no wall-clock date, and
> that is load-bearing — a byte changing for a reason unrelated to those four
> sources would force this file into the first commit of every day, and a
> guard that fires for nothing is one people route around."* **That paragraph
> identified the right risk and the wrong mechanism.** `build_board.py` takes
> **git log** as one of its four inputs, and git log moves on every commit —
> so the board changed on every commit regardless of any wall-clock date. The
> reasoning cleared a hazard it had already walked into.
>
> **The first false trigger was recorded the same day and read as the rule
> working.** v1.31(C): *"Rule 2b blocked the commit adding rule 6 … a watched
> path staged without this file is exactly what 2b exists to stop."* It was
> not — it was the board being regenerated. **From inside the hook, "the board
> changed" and "the status changed" are the same observation**, which is why
> six weeks passed before it was read as a false trigger.
>
> **Cost on the record:** `ef59aa8` — a `fix(ops)` commit touching only
> `start.ps1` — was blocked and carries a §56 entry (v1.56) written for no
> reason but to satisfy the gate. Left standing; deleting the cost of a false
> trigger is how the next one goes unnoticed. Fixed in `258d0dd`; the cause
> corrected in v1.58.
>
> **The board is not unguarded.** `verify_built.py` re-runs the counts behind
> it, which is the check a projection takes: **a derived file is verified by
> REGENERATING it and comparing**, never by asking whether someone remembered
> to touch a different file in the same commit.

<a id="L7489"></a>
#### Original lines 7489–7498 › 55.3 The phase completeness set — what one phase actually traverses

**Machine-readable: `.claude/hooks/build_board.py` renders the per-phase view
from this table.** Ratified 2026-09-11 by founder ruling, and checked against
this document's own section list before use — all fifty cited numbers still
carry the titles the ruling names.

**A phase running end to end with a visible gate traverses every row below.**
Until now the board showed each phase as a fraction of its THREE per-phase
markers, which read *"Define 1/3"* and meant almost nothing: it measured the
sections named after the phase, not the sections the phase depends on. **The
honest denominator is this table.**

<a id="L7569"></a>
#### Original lines 7569–7577 › 55.3 The phase completeness set — what one phase actually traverses

> **⚠ §39.x IS ONE ROW AND IT IS NOT EQUAL ACROSS THE PHASES.** Measure,
> Analyse, Improve and Control each carry **twelve** subsections; **Define
> carries eight**, and not the same eight — its numbering is a different shape.
> Six of the twelve topics have **no Define section at all**: the metric
> registry, tools bound to the phase, conditions, state parameters, metric
> literacy, and cross-phase reads. **The phase this project is proving first
> has the least specified spec**, which is worth knowing before its slice is
> called complete.


<a id="L7602"></a>
#### Original lines 7602–7609 › 55.4 Facts have one owner — the ratified minimum

> **THE LAST THREE WERE RECORDED, NOT DECIDED.** Each was already true in
> practice — the factory has owned the order since 6.5, `skills/` has owned the
> scripts since step 8, the registry has always owned its own entries. Writing
> them down cost nothing because nothing had to change, **which is the argument
> for ruling a row when the work touches it rather than in the abstract.** The
> first two rows were argued for a week; these three took an afternoon, and the
> difference is that by then the files made the answer obvious.


<a id="L7610"></a>
#### Original lines 7610–7619 › 55.4 Facts have one owner — the ratified minimum

> **ENFORCEMENT IS NOT UNIFORM, AND SAYING SO IS THE POINT.** A prose-count
> check was built for *middleware* and *banned patterns* and then **deleted**:
> those nouns appear 164 and 122 times in two governed documents as ordinary
> English, and the matcher fired on `### 19.9 Middleware deliberately NOT used`
> — a heading number — and on *"step 6.3 shipped two middlewares"*, which is
> true. Both facts were already checked against the tree elsewhere, so a second
> noisier check would have added false positives to something that already
> passes. **A row can be owned without every claim about it being mechanically
> comparable**, and pretending otherwise is how a check gets switched off.


<a id="L7657"></a>
#### Original lines 7657–7673 › 55.5 The commit gates govern. The rule files are advisory context.

**THE MEASUREMENT.** `.claude/logs/instructions-loaded.log` is written by the
`InstructionsLoaded` hook, which records every instruction file the CLI loads
and why. Across **two days of heavy editing it holds six records**: one
`session_start` for the root `CLAUDE.md`, and five `path_glob_match` — `ui.md`,
`middleware.md`, `testing.md`, `module-layout.md`, `rag.md`.

**Probed directly, four ways, on files under live globs:**

| Action | Tool | Rule text delivered? |
|---|---|---|
| Write a new file | `Write` | **No** |
| Append to a file | `Bash` | **No** |
| Edit a file, no prior read | `Edit` | **No** |
| Read that same file | `Read` | **Yes — both matching rule files, in full** |

The `Edit` was not refused for lacking a prior read, so this is not a case of
`Read` always preceding `Edit`. **Path-scoped rules are delivered on READ.**

---

## From: 56. Amendment procedure

<a id="L7728"></a>
#### Original lines 7728–7741

> **STEP 1 WAS WRONG IN TWO DIRECTIONS UNTIL 2026-09-13, AND BOTH WERE ABOUT
> THIS FILE.** It routed the ruling to `DECISIONS.md`, which has been archived
> since 2026-09-10 — so the procedure named a destination that takes no
> entries. And its step 4 said *"this document has no change-log section, by
> design"* while **this document has carried one at its head since v1.0** and
> every amendment in the September pass was written into it. A procedure that
> describes a file's structure is a copy of a fact the file owns, and it went
> stale the way every other copy in this repository did.
>
> The old step 4 also required a numbered `§0.x` change entry in `CLAUDE.md`.
> §0's change records moved to `docs/_archive/` at brief step 5; the root file
> carries the version line and nothing else. **The changelog for a rule change
> is this file's §56 entry and the commit body — there is no second place.**


<a id="L7767"></a>
#### Original lines 7767–7785 › 56.0 What changed about amending, when the rules stopped being one file

> ### ⚠ WHAT THESE THREE CHECKS DO NOT COVER — recorded 2026-09-14
>
> The full-structure audit reported *“no rule file contradicts the
> ARCHITECTURE.md section it derives from”*. **That result rests on these
> instruments and one spot-check, never on an exhaustive diff.** Measured the
> same day: `drift-check.py` reports **15 claims** checked; `verify_built.py`
> reports **24 checks**. Thirteen rule files carry far more assertions than 39.
>
> **So the finding means: the built instruments are green, and one manually
> chosen pair agreed** (`rag.md`'s 12 evidence-index fields against §23.2's 12
> tabulated rows). It does not mean the thirteen files were diffed against
> their sections line by line, and it must not be read as though it did.
>
> **RULED: NO EXHAUSTIVE SWEEP, AND NO STEP.** The same ruling G-55 already
> carries for the citation back-catalogue — a single pass is a diff across
> nearly every rule in the constitution for a gain that arrives anyway as
> rules are amended. **The ratchet stands**: a rule touched from here on is
> checked against its section as part of touching it. Revisit with G-55, at
> step 11.2, where the handover is marked.

<a id="L7867"></a>
#### Original lines 7867–7874 › What requires an amendment rather than a routine change

  `CoachingResponse`'s omission from this list until 2026-08-22 was an oversight
  (DECISIONS §R1)

  > **The `PhaseState` trigger previously read "a fifteenth content field," and
  > that was an enforcement hole**: a field could be added, declared
  > non-content, and skip the gate on a category label. Closed 2026-08-24 in the
  > amendment that added the two identity fields — which would themselves have
  > slipped through the old wording (DECISIONS §T1)

---

## From: Part XII — Specification

<a id="L7914"></a>
#### Original lines 7914–7919 › 56.2 The rule lands here; the reasoning lands in the commit

**`docs/_archive/DECISIONS.md` is CLOSED AND ARCHIVED** — frozen at Part AU, 2026-09-10. **It is where the historical reasoning for Parts A–AU sits**, and the only pointer to it in this document. No new entries. It held
the reasoning half for Parts A–AU. Its own *How to read this document* required
`Status / Landed in / Source` on every entry; that field appears **40 times in
Parts A–Q and zero times in Parts R–AU**, so the register had stopped recording
where its rules landed long before it was closed. **A decision whose rule never
reached this document is a decision nothing can be checked against.**

<a id="L7921"></a>
#### Original lines 7921–7926 › 56.2 The rule lands here; the reasoning lands in the commit

> **THE TEST FOR WHETHER SOMETHING IS A RULE:** would a build step be checked
> against it? Then it belongs here, in the section that owns the subject —
> never in a decision log, a tracker row or a status file. The 2026-09-10
> document collapse exists because four documents held overlapping answers and
> a guard rule checked only that two of them had been *touched*, never that
> they *agreed*.

<a id="L7954"></a>
#### Original lines 7954–7960 › 56.3 The tree at HEAD is the only source of truth

> **Row two is not the theoretical one.** While this very amendment was being
> written, a concurrent session landed four commits into
> this file: the version line read 1.49 when the entry was drafted and 1.52 when
> it was written — three increments by another seat. **A draft held in a session is a cached copy of a file that
> moved**, and the only thing that caught it was re-reading the path before the
> write. That is clause one, working, on the document that ratifies it.


---

## From: 57. The specification layer — how to read and write a spec entry

<a id="L8085"></a>
#### Original lines 8085–8088 › How gaps are marked

Every marker has a row in the **§66 gap register**, and every register row has
a marker. The conversion pass of 2026-08-23 identified 42 and filled none — that
was its binding constraint. **§66 carries the live count**; do not read one from
this paragraph.

<a id="L8216"></a>
#### Original lines 8216–8217 › 57.4 Entry index

**73 entries — 37 classes, 36 functions and nodes.** Five carry an AI-ACT flag;
twelve carry `AI-ACT-REVIEW: uncertain`. **§66 carries the live gap count.**

<a id="L8229"></a>
#### Original lines 8229–8229 › 57.4 Entry index

| **The gap register** | **§66** | 41 gaps |

---

## From: 58. Spec — graph management

<a id="L8408"></a>
#### Original lines 8408–8414 › 58.2 S-C02 · `PhaseState`

> **G-38 — CLOSED 2026-08-25 for Define.** `field_index` indexes into the
> ordered field list at **§39.1.2**, which is that phase's coached sequence.
> §13's "advance to the next field" now has an ordering source. **The other
> four phases take §39.2–§39.5 and remain blocked on G-27 and G-28** (§39.1.8),
> so `field_index` is well-defined for Define and undefined elsewhere until
> those land.


<a id="L8426"></a>
#### Original lines 8426–8426 › 58.3 S-C03 · Per-phase use of `PhaseState`

phases run on the single shared **24-field `PhaseState`** (S-C02). What varies

<a id="L8430"></a>
#### Original lines 8430–8451 › 58.3 S-C03 · Per-phase use of `PhaseState`

> ### ⛑ RULING 2026-09-11: the five variants are NOT built, and will not be
>
> This entry used to read *"`DefineState`, `MeasureState`, `AnalyseState`,
> `ImproveState` and `ControlState` extend `PhaseState` with phase-specific
> transient fields."* **They never existed.** The targeted state audit of
> 2026-09-11 found **zero occurrences in `backend/`** and no subclass of
> `PhaseState` anywhere, against a spec that named them thirteen times.
>
> **They were never specifiable, which is the real finding.** G-19 said so for
> two months: *"the phase-specific transient fields are never enumerated for
> any of the five."* **A class whose fields nobody could name is not a design
> that was missed; it is a design that was never made.** This entry assigned
> them to step **3.1**, which is DONE and whose Done-when never mentioned them
> — so a completed step silently dropped a spec entry assigned to it, and
> nothing noticed until something went looking.
>
> **§7 had already ruled against the one concrete case**: *"No new top-level
> `PhaseState` field, and no per-phase typed destinations"*, because typed
> per-phase destinations *"multiply schema surface for a question a scan
> already answers"*. The general ruling now matches the specific one.
>
> **G-19 is CLOSED by this ruling**, not by enumerating the fields.

<a id="L8462"></a>
#### Original lines 8462–8467 › 58.4 S-C04 · `CoachingPlan`

> **v1.75 (founder, 2026-09-25):** `next_action` as free text chosen by a model
> is superseded — the move is decided in code from the field's status (§17), and
> the planner's model judges only whether an answer is sufficient. **The class
> below is unchanged until step 6.61 builds it**, and 6.61 carries its own
> amendment for the shape it lands (CLAUDE.md, amending the rules, 3b).


<a id="L8538"></a>
#### Original lines 8538–8541 › 58.4 S-C04 · `CoachingPlan`

> **Was defined twice.** Until the 2026-08-23 conversion this class appeared in
> full in both §6 and §17 — a define-once violation that predates this Part.
> This entry is now its only definition.


<a id="L8547"></a>
#### Original lines 8547–8562 › 58.5 S-C05 · `CoachingResponse`

> — `message`, `fields_captured`, `citations`, `contradiction_flag`. **§50.1's
> four presentational fields — `explanation`, `example`, `prompt`, `progress`
> — are NOT BUILT** (**G-50**), so the render contract §50.1 calls
> *"schema-backed, not prompt-hoped"* is currently prompt-hoped: the one field
> the UI receives is `message`, which is the single free-text blob that section
> forbids. **Found 2026-09-11 by the three-way alignment audit; the rebuild
> test above is what it failed.** The built class's own docstring reads *"the
> four fields below are transcribed from that entry"* against an entry defining
> eight — a conformance claim made in the file that breaks it.
>
> **Closed by step 6.19, not by 10.2** — which was the first guess and was
> wrong. **10.2 RENDERS these fields; it cannot DECLARE them**, and it sits
> behind seven Stage-7 steps while 6.19 is `READY` now. The four are already
> ratified here, so 6.19 applies a ratified definition rather than amending
> one, on the RATIFIED-NOT-YET-APPLIED precedent §23.2 set


<a id="L8630"></a>
#### Original lines 8630–8635 › 58.5 S-C05 · `CoachingResponse`

  **The four §50.1 presentational fields were added 2026-08-25 under that
  procedure**, and the blast radius is stated rather than discovered: this
  schema is the coach output of **all five phases**, so every SKILL.md must
  instruct the coach to populate the four, and the response-rendering UI must
  draw them. **The UI half is not built** — §50.1 defines the contract, the UI
  rebuild implements it.

<a id="L8654"></a>
#### Original lines 8654–8666 › 58.5 S-C05 · `CoachingResponse`

> **WHY THE CONTRACT AND NOT THE COACHING SCRIPT.** The shape was written into
> `skills/dmaic-define-phase/SKILL.md` first. That is correct content in the
> right file and **it did not reach the model**: SKILL.md loads at **level 2,
> on demand**, through the `load_skill` tool the coach must choose to call
> (§19.2, S-C12). **Measured on four live turns, 2026-09-23: `load_skill` was
> called ZERO times and all four Define fields came back as prose.**
>
> **A field's declared shape is part of its TYPE CONTRACT, not part of
> coaching.** A contract that lives only in a document can be broken by editing
> that document, and nothing fails until a Belt reaches a gate — which is the
> failure class §55.2 exists for. This description is the structured-output
> contract the model receives on **every** turn, with nothing to fetch and
> nothing to choose.

<a id="L8794"></a>
#### Original lines 8794–8838 › 58.8 S-C08 · `ImproveBlobClient`

> ~~**SPEC-GAP (G-21):** the class interface — method names, signatures, return
> types, and how registry updates are sequenced against case writes — is stated
> nowhere — to be designed with founder.~~
>
> **RESOLVED 2026-09-01, procedure step 3.5.** Decision record:
> `docs/_archive/DECISIONS.md` Part Y. **There is no class interface, and that is the
> resolution** — §54 and `CLAUDE.md` §2 name this file among those holding
> module-level functions ONLY, so the gap as originally written asked for
> something that may not exist here. `ImproveBlobClient` was removed; the
> surface is fourteen module-level names — **thirteen until 2026-09-10**,
> when `download_bytes` joined them for S-F57's loader: `_download` decodes
> UTF-8 and would corrupt every binary format the parser handles (Part AS):
>
> | Kind | Names |
> |---|---|
> | sync | `case_path(case_id) -> str` · `storage_configured() -> bool` |
> | async | `load_case` · `save_case` · `create_case` · `write_phase_gate` · `append_turn` · `load_registry` · `save_registry` · `register_case` · `upload_file` · `aclose` |
> | const | `REGISTRY_BLOB_PATH` |
>
> **B2's sequencing is answered:** `write_phase_gate` awaits `save_case` first,
> then `_update_registry_entry` — the case blob is the system of record, so the
> registry must never point at a phase the case document does not yet show.
> Both are still two separate writes covered by the node's `error_handler`
> (§45).
>
> **`write_phase_gate` MERGES into the phase record and is SAFE TO PERFORM
> TWICE — step 6.42, 2026-09-23.** It replaced the whole `PhaseRecord` with five
> fields until then, which dropped `field_log` (§6), `analyst_output`, and —
> because the call site passed neither and the defaults were `[]` — the Belt's
> citations and uploads, **at the one moment a reviewer goes looking for them**.
> `citations` and `uploads` now default to `None`, meaning NOT SUPPLIED, which
> the `[]` default could not express. The approval stamp is written on the
> TRANSITION only, so two writes leave one record rather than one with a moving
> timestamp; `current_phase` is computed from the `phase` argument rather than
> the case's current value. **That is a framework requirement, not caution**:
> when step 7.3 moves this write behind `interrupt()`, *"the runtime restarts
> the entire node from the beginning"* and every resume re-runs it
> (`docs.langchain.com/oss/python/langgraph/interrupts`, verified 2026-09-23). **Lifecycle:** one cached `azure.storage.blob.aio` client, keyed on its
> event loop, closed by `aclose()` on `app.py`'s shutdown hook — ruled on a
> measurement, not a preference (Part Y).
>
> **What this does NOT resolve:** deletion. S-C08's *Paths owned* includes
> `uploads/{case_id}/{file}` and no behaviour governs removing one, so uploaded
> blobs are orphaned when their case record drops them (`CONTINUITY.md` §6,
> WATCH 10). That is a **new gap, not part of G-21**.

<a id="L8862"></a>
#### Original lines 8862–8866 › 58.9 S-C09 · `storage/models.py` — the record models

> **`UploadRecord` joined this list on 2026-09-08** (`DECISIONS.md` Part AP5).
> It has been in `storage/models.py` since before the refactor and is the
> element type of `PhaseRecord.uploads`; this entry named four models and not
> it.


<a id="L8899"></a>
#### Original lines 8899–8909 › 58.9 S-C09 · `storage/models.py` — the record models

> **Six of these thirteen fields were in the tree and in no document until
> 2026-09-09** (`DECISIONS.md` Part AP6). AP5 documented `ask_id` and `version`
> because it ratified them; `evidence_index_id`, `summary`, `kind`,
> `interpretation` and `refusal_reason` were added at 6.11 as things the
> Done-when *entailed* — §6's entry shape names `evidence_index_id` and
> `summary`, and neither existed on the record — and entailed additions are
> exactly the ones that reach a tree without reaching a spec. **`ask_id` and
> `version` are still RESERVED FOR 6.12**; the ask-binding fills them, on
> §23.2's RATIFIED-NOT-YET-APPLIED precedent, so that no upload written between
> the two steps lacks a place to record which ask it answered.


<a id="L9020"></a>
#### Original lines 9020–9024 › Behaviors (EARS)

> **Resolved — G-01, see S-F13.** The intra-phase edges this function wires are
> the Level 2 `Command` routing, designed 2026-08-24. **Its DP1 predicate reads
> the ordered field list**, which G-38 supplied for Define on 2026-08-25
> (§39.1.2). For the other four phases the predicate has no list yet, so this
> entry's rebuild test is met for Define and blocked elsewhere.

<a id="L9065"></a>
#### Original lines 9065–9067 › Behaviors (EARS)

> **G-38 — CLOSED 2026-08-25 for Define.** "Advance to the next field" walks
> the ordered list at §39.1.2. See S-C02.


<a id="L9423"></a>
#### Original lines 9423–9423 › SIPOC — at a glance

| **Process** | Reads the case record, composes `phase_context` as prose framing, and initialises all seventeen `PhaseState` fields |

<a id="L9555"></a>
#### Original lines 9555–9557 › Behaviors (EARS)

> **G-27 — CLOSED 2026-08-31, at procedure step 3.3.** All four pairs are
> built, alongside Define's, in `phases/{phase}/mappers.py`. The three open
> questions are ruled:

<a id="L9608"></a>
#### Original lines 9608–9614 › DP1 — the planner owns the field / gate decision

> **G-38 — CLOSED 2026-08-25 for Define.** DP1's structure was already settled;
> its predicate now has the list it evaluates against. "Field complete" and
> "more fields" read **§39.1.2**, Define's ordered coached sequence, so **DP1 is
> implementable for Define.** The other four phases take §39.2–§39.5 and are
> still blocked on G-27 and G-28 — DP1 is implementable per phase, in step with
> each phase's field list, not all at once.


---

## From: 59. Spec — knowledge and retrieval

<a id="L9806"></a>
#### Original lines 9806–9813 › 59.4 S-C19 · `QueryVariants`

> **~~SPEC-GAP (G-14)~~ — CLOSED 2026-09-03, procedure step 5.2.** All three
> undecided points are ruled, in `knowledge/fusion.py` and in §66.3's row:
> **one field `variants: list[str]`**; **the original query is NOT among them
> and is always searched as ranked list zero**; **count model-chosen, bounded
> 3–5 by the schema**. Resolved under CONTINUITY's Standing Reasoning Protocol
> as a Group C gap — a schema named but never defined — rather than as a
> founder ruling, which Group A is empty of. Record: `docs/_archive/DECISIONS.md`
> Part AC.

---

## From: 60. Spec — tools

<a id="L10283"></a>
#### Original lines 10283–10296 › Behaviors (EARS) — binding on all twenty

> **SPEC-GAP (G-25) — RESOLVED 2026-08-26 by §69.** *Retained as the record of
> what was missing, because §55.1 requires every register row to keep an inline
> marker. The three consequences below are the reason the gap mattered; §69.1
> answers (a) and (b), and (c) is answered per tool in §69.2–§69.6.*
>
> When raised: not one of the twenty had a signature, a parameter
> schema, or a return shape stated anywhere in this document. Three consequences
> follow, and each is its own design decision: (a) §31 requires every `@tool` to
> carry an `args_schema` from `knowledge/tool_args.py`, and none exists; (b) B3's
> "clear reformatting request to the Belt" has no defined shape — whether it is a
> raised error, a sentinel return, or a string the model reads changes how the
> coach handles it; (c) B6's `computation_results` entry shape is illustrated in
> §7 for `t_test` only. **The inventory above is complete and is not a gap; the
> interfaces are entirely absent** — to be designed with founder.

---

## From: 63. Spec — the DMAIC gate documents

<a id="L11331"></a>
#### Original lines 11331–11352 › 63.6 S-C32 · The three cross-phase reference dicts

> reference keys are validated by NOTHING** · **closes:** `[7.1]`
>
> `causal_hypothesis` (Analyse), `solution_linked_to_root_cause` (Improve) and
> `post_improvement_metrics` (Control) are all declared `dict`, and
> `references_phase` / `references_field` / `references_value` /
> `references_metric_name` appear in `analyse/schema.py`'s field description
> and in three SKILL.md files — **as instruction to the coach.** Nothing checks
> they arrived: `missing_structured()` says so in its own docstring — *"Analyse
> and Improve have no structured field and return `[]`"* — and Control's branch
> validates `control_plan` only.
>
> **So the one thing this entry exists for cannot happen.** Its purpose is that
> *"the grader can verify the link deterministically — it reads the referenced
> phase's gate document from the Store and checks the named field carries the
> named value. Without the reference keys, ‘does this solution address the
> validated root cause?’ is an opinion; with them it is a lookup."* **With the
> keys unvalidated it is an opinion again**, and the gate passes either way.
>
> **Found 2026-09-11 by checking the alias instead of assuming it.** This
> section was covered by §42's ✅ marker, which pins only that
> `post_improvement_metrics` is the sole Tier-1 cross-phase reference — true,
> and nothing to do with whether the keys are there.

<a id="L11387"></a>
#### Original lines 11387–11392 › 63.6 S-C32 · The three cross-phase reference dicts

**Populated by Analyse now.** `solution_linked_to_root_cause` (Improve) and
`post_improvement_metrics` (Control) **carry the key and leave it unpopulated
until their own reviews** — §39.4 and §39.5. Control's is **F-14**, still open:
its target-vs-actual becomes one comparison per metric, and this key is the
shape that comparison will resolve through. **The key exists on all three now
so the shape is settled once**, rather than three times in three reviews.

<a id="L11500"></a>
#### Original lines 11500–11515 › 63.9 S-C39 · `phase_metrics` — the per-phase placeholder

> and NOTHING WRITES IT** · **closes:** `[6.20]`
>
> `phase_metrics` is declared on every `{Phase}Output` and
> `test_gate_documents.py` pins that. **It is not a coached field on any phase**
> — it appears in no tier set — so the coach never captures it, and
> `verify_built.py`'s reader/writer pass reports it `phase_metrics:W`: read by
> all five gate-document assemblers, written by none.
>
> **So the keyed trail this entry exists for does not exist.** Its purpose is
> that a metric's *"whole journey is one keyed trail across the five gate
> documents"*; today every gate document carries an empty list where that trail
> should be. Step 6.20 writes it.
>
> **Found 2026-09-11 by checking the alias instead of assuming it.** §40's ✅
> marker covers the schemas and their field counts — both true — and says
> nothing about whether a declared field is ever populated.

<a id="L11545"></a>
#### Original lines 11545–11557 › 63.9 S-C39 · `phase_metrics` — the per-phase placeholder

> **⛑ CORRECTED 2026-09-23 — THIS ROW AND §39.5.3 NAMED DIFFERENT KEYS FOR ONE
> SHAPE.** The row read *"`post_improvement_metrics`, `improvement_delta`"*
> while §39.5.3's worked example writes `actual` and `delta`. **Two sites, one
> shape, and an implementer reading either alone would have built the other's
> entry wrong** — silently, because both names exist elsewhere in Control's
> schema as TOP-LEVEL captured fields (§39.5.4). That is what made the
> disagreement plausible in both directions rather than obviously wrong in one.
>
> **§39.5.3 wins because it carries the worked example** — a shape stated as a
> literal entry is harder to misread than one named in prose, and the
> single-authority invariant in that same subsection binds `actual` to
> `post_improvement_metrics`'s value by name. This row now points there rather
> than restating it, which is why it cannot drift again.

---

## From: 65. Spec — API, UI and evidence

<a id="L11957"></a>
#### Original lines 11957–11963 › Behaviors (EARS)

> **SPEC-GAP (G-36) — STILL OPEN, but no longer the naming half.** `POST /upload`
> joined this table on 2026-09-08 (Part AP5); **the sentence that stood here
> — "there is no upload endpoint in this table" — was true until then and is
> not now.** What remains open is the channel itself: §29.1 makes uploaded
> documents the only route by which external data enters AgentLean, and for the
> formats a Belt actually uploads the handler parses nothing. **Behaviour is
> step 6.11** — see S-F35.

<a id="L12007"></a>
#### Original lines 12007–12016 › Behaviors (EARS)

> **SPEC-GAP (G-36) — STILL OPEN; two of its three clauses have been answered.**
> As written this read: *"no upload endpoint exists in §49's endpoint table, no
> file owns this handler, and it appears in no procedure step."* `POST /upload`
> was added to §49 and to S-F34 on 2026-09-08 (Part AP5), and the handler now
> has procedure steps — **6.11 the upload path, 6.12 the ask-binding** (Part AP3).
> **The founder input the gap asked for has been given**: six rulings at Part AP2.
> **What is still open is the code.** §29.1's sole external channel does not parse
> csv, xlsx, pdf or docx; `PhaseState.uploads` has no writer; and until 6.11
> lands, the entire channel remains specified more thinly than §29.1's claim on
> it. **G-36 closes at 6.11, or is re-scoped there.**

---

## From: 66. The SPEC-GAP register — MOVED

<a id="L12061"></a>
#### Original lines 12061–12065

**The section number is kept rather than reclaimed.** 1,128 parenthetical
citations exist across the two binding documents and many of them are `§66`;
a number that silently pointed at nothing would break every one. §0.2's rule
against renumbering applies to a section that MOVES exactly as it applies to
one that is amended.

---

## From: Appendix A — Provenance index

<a id="L12435"></a>
#### Original lines 12435–12495 › A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference

| Old | New | Topic |
|---|---|---|
| §1 | §8, §10 | Checkpointing, persistence |
| §2 | §33, §38, §39 | HITL gates, escalation |
| §5 | §17 | Planner/Executor |
| §10 | §6 | Subagent state |
| §11 | §17 | Recursive planner/executor |
| §17 | §5 | `SupervisorState` |
| §18 | §6, §11, §40 | `PhaseState`, `step_log` |
| §19 | §9 | Multi-step chaining, boundary mappers |
| §20 | §17 | Supervisor/worker |
| §21 | §14 | Node contract, state passing |
| §22 | Appendix B item 10 | Debate agents — **deferred** |
| §23 | §12, §13, §16 | Subgraph architecture |
| §24 | §51, §55 | Governance and debugging |
| §25 | Appendix D | Gap register |
| §27, §28 | — | LCEL — **not used**, historical |
| §29 | §19.5, §21 | Retry middleware, structured output |
| §30 | §15 | Routing |
| §32, §33 | §24, §25 | Multi-query, RRF |
| §34 | §26 | Multi-hop mechanism |
| §35 | §25 | Query voting — RRF chosen |
| §36 | §23, §28 | Vector memory, index schemas |
| §37 | §23, §28 | Memory patterns |
| §38 | §22, §37 | Memory hierarchy, contradiction |
| §39 | §29, §30, §31 | Knowledge tools, MCP-out, computation tools |
| §40 | §22, §23 | Metadata signals |
| §41 | §24 | Retrieval pipeline |
| §42 | §36, §43 | Grader middleware, coaching method |
| §43 | Appendix B item 14 | Agent roles — Observer deferred |
| §44 | §9, §12, §15, §33 | Architecture diagnosis, boundary mechanisms |
| §45 | §55, Appendix C | Anti-drift, trusted sources |
| §46, §47 | Appendix B item 11 | Coordination, aggregation — **deferred** |
| §48 | §34, §36 | Reflection vs consensus |
| §49 | §45 | Saga → `error_handler=` |
| §50 | §18, §53 | Version corrections |
| §51 | §34 | InsightForge reference implementation |
| §52, §52a | §8, §9 | Checkpointer + Store |
| §53 | §19 | Built-in middleware |
| §55, §72 | §53 | LangServe, LangGraph Server |
| §56 | §53 | Stale deployment tooling |
| §57–§65 | §29.1 | **MCP — architecturally excluded** |
| §66, §67 | §44, §46 | Circuit breaker, fallback chain |
| §68, §69 | §34, §35 | Validation stack, layer placement |
| §70 | §9 | Inter-stage dependency |
| §71 | §26 | Multi-hop design layer |
| §73 | §51 | Langfuse — LangSmith retained |
| §74 | §53 | API versioning |
| §75 | §52 | Evaluation dataset |
| §76 | §53 | Docker |
| §77 | §50 | Frontend requirements |
| §78 | §53 | Developer orchestration menu |
| §79 | §44, §45 | LangGraph 1.2 reliability primitives |
| §80 | §19 | AgentMiddleware six hooks |
| §81 | §21 | Content blocks |
| §82 | §20, §21 | ProviderStrategy, structured output |
| §83, §84 | §32, §19.2 | Agent Skills, SkillsMiddleware |
| §85 | §51 | LangSmith 2026 additions |
| §86 | §55 | Hook mechanics |
| §87 | Appendix B | Deferred backlog |
| §3, §4, §6–§9, §12–§16, §26, §31, §54 | — | Course material and historical notes — **no section here**; retained in `agent-improve/docs/_archive/REFACTORING_AGENT_IMPROVE.md` |

<a id="L12499"></a>
#### Original lines 12499–12571 › A.2 `agent-improve/ARCHITECTURE.md` → this reference

`ARCHITECTURE.md` is **absorbed** by this document.

| Old | New |
|---|---|
| §0 | §2 |
| §1 | §1, §4 |
| §2 | §1, §50 |
| §3.1 | §12, §15, §16 |
| §3.2 | §13, §14 |
| §3.3 | §18, §21, §22 |
| §3.4 | §19 |
| §3.4.1 | §36 |
| §3.4.2 | §43 |
| §3.5 | §17 |
| §3.6 | §33 |
| §3.7 | §34 |
| §3.7.1 | §35 |
| §3.8 | §37 |
| §3.9 | §38 |
| §4.1 | §5 |
| §4.2 | §6 |
| §4.3 | §9 |
| §4.4 | §11 |
| §4.5 | §8 |
| §4.6 | §7 |
| §4.7 | §7, §42 |
| §4.8 | §7 |
| §4.9 | §5 |
| §4.10 | §20, §40 |
| §4.10.2, §4.10.3 | §40 |
| §4.10.5–§4.10.7 | §41 |
| §5 | §54 |
| §6.1, §6.2 | §8 |
| §6.3 | §9 |
| §6.4, §6.5 | §10 |
| §6.6 | §46 |
| §6.7 | §8 |
| §7.1–§7.3 | §23 |
| §7.4 | §24, §25 |
| §7.5 | §26 |
| §7.6 | §23.5 |
| §7.7 | §23.5 |
| §8.1 | §29, §31 |
| §8.2 | §30 |
| §8.3 | §25 |
| §8.4 | §32 |
| §9.1 | §44 |
| §9.2 | §45 |
| §9.3, §9.4 | §46 |
| §9.5 | §48 |
| §10 | §49 |
| §11 | §50 |
| §12 | §51 |
| §13 | §35, §39 |
| §13.6 | §35 |
| §14 | §52 |
| §15 | §53.1 |
| §16 | Appendix B, Appendix D.3 |
| §17 | **Appendix F.1** · Decisions-resolved register. Each entry's *conclusion* is stated in the section that owns the topic; the register itself is a historical artefact. Extracted 2026-08-22 to `docs/_archive/ARCHITECTURE_v2216_registers.md`, **merged into this file at Appendix F.1 on 2026-09-01** |
| §18 | **Appendix F.2** · Change log. This document states conclusions, not their history (§"About this document"), so the log is carried as an appendix rather than a section. Extracted 2026-08-22 to `docs/_archive/ARCHITECTURE_v2216_registers.md`, **merged into this file at Appendix F.2 on 2026-09-01** |
| §18.1 | §56 |

**Absorption completed 2026-08-21.** Nine items of `ARCHITECTURE.md` content
had no home here when the absorption was first declared and were written in
during this sweep: the one-way-door gate principle (→ §33), parallel-case
isolation (→ §16), ETag concurrency and the Blob-vs-alternatives rationale
(→ §8), the `analyse` rename scope table, the checkpoint / node-name warning
and the `improve_case_index` vector profile (→ §23.3), the conflict-resolution
panel and the LangSmith run id (→ §50), the three-mechanisms-check-these-fields
distinction (→ §35), cache invalidation policy (→ §46) and the structured log
field list (→ §51). **`agent-improve/ARCHITECTURE.md` was genuinely absorbed.** On 2026-08-22 that
path was reused for a copy of this document (see the two-document division
above); the absorbed v2.2.16 original is at commit `8533879`.

---

## From: Appendix C — Trusted sources

<a id="L12670"></a>
#### Original lines 12670–12686 › Index refresh — 2026-08-21

### Index refresh — 2026-08-21

**The `anthropic.com/engineering` index was re-read in full. Nothing has been
published after this list's August 2026 cutoff** — the newest dated post is
*"An update on recent Claude Code quality reports"* (Apr 23, 2026), with *"How
we contain Claude across products"* currently featured.

**Three posts inside the window were missing from this list and have been
added** (above). They were not new; they were simply never picked up when the
list was built. Two bear directly on §52's evaluation design, which is the
part of this architecture with the least production evidence behind it.

**Posts deliberately not added**, being product/model-specific rather than
architectural: *Claude Code auto mode* (Mar 25), *Eval awareness in Claude Opus
4.6's BrowseComp performance* (Mar 06), *Building a C compiler with parallel
Claudes* (Feb 05), *An update on recent Claude Code quality reports* (Apr 23).


---

## From: Appendix E — Current state

<a id="L12771"></a>
#### Original lines 12771–12818

**As of 2026-08-21.** This appendix is expected to go stale; it records where
the implementation stands relative to the design, so the gap is explicit rather
than discovered.

### What exists

| Component | Status |
|---|---|
| `core/checkpointer.py` — `AzureBlobCheckpointSaver` | **Implemented and compiled in — but INERT.** `thread_id` and `ainvoke` appear nowhere, so it has never written a checkpoint (§53.1) |
| `core/state.py` | v1 `ImproveGraphState` — **not** `SupervisorState` |
| `core/graph.py` | v1 flat graph, 11 nodes, `set_entry_point` |
| `knowledge/retriever.py` | v1, **but already carries the correct `phase_relevance` filter and `fields=` declaration** |
| `knowledge/tools.py` | v1 `search_*` names, no multi-query, no RRF |
| `phases/{phase}/schema.py` | v1 `{Phase}PhaseInput` |

### What does not exist yet

`core/substate.py` · `core/store.py` · `middleware/` · `validation/` ·
`knowledge/tool_args.py` · `knowledge/computation.py` · `knowledge/fusion.py` ·
`core/reliability.py` · `core/diagrams.py` · `phases/{phase}/mappers.py` ·
`phases/{phase}/graph.py`

### Known violations in current code

| Site | Rule |
|---|---|
| `gateway/routes.py` — `get_graph()` called, then nodes dispatched manually; **the compiled graph is built and discarded** | §49 |
| Phase nodes are sync `def`, called unawaited | §14 |
| `core/graph.py` — `set_entry_point` | §12 |
| `core/llm.py` — contains a class; role map diverges from §21 | §54, §21 |
| `gateway/routes.py:67` and `upload/agent.py:107` — parse `response.content` directly | §21 |

### Blocked

> **BOTH ENTRIES BELOW WERE CLEARED AFTER THIS APPENDIX DATE, and are struck
> rather than deleted.** The appendix is a dated snapshot and says so — but a
> heading reading `Blocked` over two things that are not is the one kind of
> staleness a dated header does not excuse.

~~**`langgraph` 1.1.10 < 1.2.6** blocks all of §45 and the §16 subgraph
namespacing (§53).~~ **CLEARED at step 2.3.** The venv satisfies the ≥1.2.6
floor; the pin lives in `requirements.txt` and not here.

~~**Two Azure schema changes are ratified and unapplied**~~ → **ONE.**
`improve_evidence_index` `phase` + `uploaded_at` **LANDED at step 6.13**
(2026-09-10, §23.2). What remains is `improve_case_index` `embedding` →
`content_vector` (§23) — and with one left there is nothing to batch it with.


---

## From: Appendix F — The v2.2.16 registers

<a id="L12824"></a>
#### Original lines 12824–12833

> **Merged into this file 2026-09-01** from
> `docs/_archive/ARCHITECTURE_v2216_registers.md`. Originally extracted 2026-08-22 from
> `agent-improve/ARCHITECTURE.md` at commit `8533879`, §17–§18.1, when that file
> was replaced by a copy of the platform reference — these two registers lived
> nowhere else, which is why they were extracted rather than left to git history.
>
> **Historical record. Not binding, not maintained.** Every decision below is
> stated as a *conclusion* in the section that owns its topic; this is the
> register of **when** each was resolved, not where it is defined. Appendix A's
> §17 and §18 rows route here.

<a id="L12837"></a>
#### Original lines 12837–12869 › F.1 Decisions Resolved (v2.2) — the former §17

| Decision | Resolution |
|---|---|
| Graph topology | Hierarchical subgraphs, **static edges between phases** |
| Threading | **One `thread_id` per project**, auto `checkpoint_ns` per subgraph |
| Checkpointer placement | **Parent graph only** — subgraphs compile without one |
| Checkpointer backend | **Phased** — Azure Blob → PostgreSQL before production |
| Cross-phase handoff | **Store-mediated boundary mappers**, not parent state |
| Coach pattern | **`create_agent`** with eight middlewares and a per-phase tool subset |
| Planner | Explicit node producing a structured plan; Level 1 planner is deterministic |
| Rubric grading | **Custom `DMAICGraderMiddleware`** on `create_agent`, not deepagents |
| HITL mechanism | **Graph-level `interrupt()`**, not `HumanInTheLoopMiddleware` |
| Gate flow | **Nine steps, two nodes, four validation layers** |
| Coherence and constraint checks | **Lightweight LLM**, not format checks |
| Mid-phase value conflicts | **Auto-flag, no threshold**, with re-approval cascade |
| Retrieval | **Three tools**, multi-query + RRF mandatory, metadata filters |
| `improve_case_index` | **Active** — yokoten via `rag_lookup_case_history` |
| Computation | **20 tools**, per-phase binding, pure functions |
| Context compression | `SummarizationMiddleware` + typed state fields |
| Compensation | **Native `error_handler=`**, no custom Saga framework |
| Fallback Level 3 | **Azure Cache for Redis** — new infrastructure |
| Deployment layer | **FastAPI** — LangGraph Server requires a commercial licence |
| Protocol layer | **None** — MCP architecturally excluded |
| Diagram generation | LLM emits JSON, frontend renders SVG from templates |
| Prompt management | Constants in `core/prompts.py` |
| Project identifier | **`case_id` everywhere** — documents match the code and the indexes (§4.1.1) |
| Name for a phase's captured fields | **`artifacts`** — `captured_fields` and `phase_inputs` retired (§4.9) |
| Captured field typing | **All `str`**; the 20 computation tools parse at the point of use (§4.6) |
| Cross-phase linkage | **Explicit reference dicts** on three fields — deterministic grader check, not LLM judgment (§4.7) |
| Computation tool output | **`artifacts["computation_results"]`** — one list per phase, not typed per-phase fields (§4.8) |
| Gate document write | **`gate_apply_node` writes both** the store and `PhaseState.final` (§3.6.1) |
| Gate-required fields | **Two tiers** — Tier 1 blocks, Tier 2 warns with an acknowledged gap (§3.7.1) |
| Grader verdict statuses | **`pass` / `warning` / `fail`**, belt-level aware (§3.7.1, §3.7.2) |
| `coaching_plan` shape | **Single transient `dict`**, overwritten per planner turn (§3.5) |

<a id="L12875"></a>
#### Original lines 12875–12912 › F.2 Change Log — the former §18

| Date | Version | Change |
|---|---|---|
| May 2026 | 0.1 | Initial scaffold |
| Jun 2026 | 0.2 | Define + Measure complete |
| Jun 2026 | 1.0 | Analyse + Improve + Control complete. v1 in production. |
| Jun 2026 | 2.0 | DRAFT — Path C architecture proposed |
| Jun 2026 | 2.1 | Path C ratified: hierarchical subgraphs, tool-calling coach, Azure Blob checkpointer, interrupt-based gates, SSE streaming, LangSmith mandatory. |
| Jun 2026 | 2.1.1 | §6.1.1 base64 envelope for checkpoint blobs (surfaced during commit 2.1). |
| Aug 2026 | **2.2** | **Ground-up rewrite aligning with the EDUCATIONAL.md review.** Static edges between phases; one `thread_id` with auto `checkpoint_ns`; checkpointer and store on the parent only; phased Blob → PostgreSQL; `AzureBlobStore` and store-mediated boundary mappers; six-node phase subgraph with conditional edges and cycles; `create_agent` with a four-middleware stack; three retrieval tools with multi-query + RRF; 18 per-phase computation tools; nine-step gate across two nodes; four-layer validation stack; mid-phase conflict detection with re-approval cascade; native `error_handler=` compensation; per-node timeouts; two three-state circuit breakers; four-level fallback chain with Redis cache; `recursion_limit=11` hop cap; **canonical index schemas in §7**; MCP architecturally excluded; FastAPI confirmed as the deployment layer. |
| Aug 2026 | **2.2.1** | **Index schema facts resolved against the live service (§7).** `improve_case_index.phase_summary_analyse_phase` renamed to `phase_summary_analyse` by delete + recreate (index empty, no reindex required) — Step 3.6 closed; writer-side phase-key alignment carried forward in §7.3. `improve_evidence_index` confirmed to have **no** `uploaded_at` field — the timestamp lives in the non-sortable `metadata` blob, so the `uploaded_at desc` ordering clause is dropped from §7.2 and `rag_lookup_evidence` takes no `order_by`. `improve_case_index.embedding` confirmed 3072d on profile `improve-vector-profile`. |

| Aug 2026 | **2.2.2** | **Internal phase key `analyse_phase` renamed to `analyse` across the codebase (§7.3.1)** — completes the schema rename in 2.2.1 on the writer side. Directory `phases/analyse_phase/` → `phases/analyse/`; `orchestrate_analyse_phase` / `validate_analyse_phase` and their graph node names lose the suffix; the key is now `analyse` in `PHASE_ORDER`, `phase_inputs`, `EXTRACTION_MAP`, `ORCHESTRATOR_CONTEXT_MAP`, `GATE_CHECKS`, `PhaseSummaryRecord`, and `CaseDocument.phases`. `AnalysePhaseInput` unchanged — it already matched convention. Node rename was free only because no checkpoints existed yet. |

| Aug 2026 | **2.2.3** | **Methodology retrieval fixed and its failure contract defined (§7.1, §7.1.1).** `search_knowledge` filtered on `phase`, a field that does not exist on `improve_knowledge_index`, so Azure rejected every phase-filtered query and a bare `except Exception` rendered it as "No relevant methodology content found" — phase-filtered retrieval had never returned a document. Filter corrected to `phase_relevance`; cross-phase value corrected from the non-existent `all` to `general` (218 docs), closing the §7.1 open item with the confirmed enumeration. Failures now raise `KnowledgeSearchError` carrying an `AgentImproveError` (§12.3, `core/errors.py` added), classified by Azure exception type with 4xx as permanent/do-not-retry. `step_log` wiring deferred to step 4.1 — the dict shape is already emitted. |

| Aug 2026 | **2.2.4** | **Failure contract extended to all three retrieval functions (§7.1.1).** `search_cases` and `search_evidence` carried the same bare `except Exception` → `[]` as `search_knowledge`, so a broken case or evidence query also read as "nothing found". Both now raise `KnowledgeSearchError` with the same classification. `RETRIEVAL_EXCEPTIONS` additionally covers `OpenAIError`, since the query-embedding call runs inside the same `try` and would otherwise escape raw; embedding failures carry an `EMBEDDING_` code prefix. Result materialisation moved inside the `try` (the pager is lazy), imports hoisted out of it, `case_id` OData-escaped, and the metadata-blob parse narrowed to `JSONDecodeError`/`TypeError` with a warning instead of a silent `pass`. Callers `search_improve_cases`, `search_improve_evidence`, and `_generate_sipoc_draft` updated to catch the typed exception. |

| Aug 2026 | **2.2.5** | **Ingestion contract fixed and documented (§7.1.2).** `ingest_knowledge.py` emitted `phase`, not a field on the index, so `phase_relevance` was never populated by the script. Fixing the key name alone proved insufficient: LangChain promotes metadata keys only against `self.fields`, which defaults to `[id, content, content_vector, metadata]` and never introspects the live index — so `get_knowledge_vectorstore()` now passes `fields=KNOWLEDGE_INDEX_FIELDS`. Both changes are required; either alone leaves the index unfilterable. Also: metadata reduced to the live four-key shape, `source_file` emitted as a stable label rather than a filename, chunking moved to per-page so `page_number` is a real page rather than a chunk index, and document keys made deterministic and passed via `ids=` so re-ingest upserts instead of duplicating. Phase mapping confirmed empirically as per-chunk keyword scoring, not chapter mapping, and documented with the evidence. |

| Aug 2026 | **2.2.6** | **LangGraph upgrade target moved 1.2.7 → 1.2.10 (§1, §2.5.1).** Verified against PyPI and the verbatim GitHub release bodies for 1.2.6–1.2.10 via `/verify-current-version`. The **floor is unchanged at ≥1.2.6** — the nested-subgraph `checkpoint_ns` inheritance fix (#8053, a regression introduced in 1.2.3) landed there and nothing since has touched it. Of the three intervening releases, 1.2.7, 1.2.8 and 1.2.9 are **entirely `DeltaChannel` fixes**, and `DeltaChannel` is not used (CLAUDE.md §3.6, backlog item 12) — so they are no-ops for us. 1.2.10 adds v3 `stream_events` return typing with native projections, and exposes `trace_policy` as a **new additive kwarg on `add_node`** alongside the existing `timeout=` and `error_handler=`; no existing signature changes, no deprecations, no breaking changes. **`trace_policy` is deliberately not adopted:** the same release contains both "drop tags from TracePolicy" (#8402) and "revert: delete TracePolicy" (#8403), so the API is unsettled. Per-node `TimeoutPolicy` and node-level `error_handler=` are unchanged across all four releases, so §9.2 needs no revision. No code change accompanies this amendment — the upgrade itself is still step 2.5.1, not yet executed. |

| Aug 2026 | **2.2.7** | **`dmaic_plan`, `key_decisions` and `open_items` removed from `SupervisorState` (§4.1, §4.3).** All three were redundant against mechanisms that already existed, and each was a second source of truth able to drift out of agreement with the first. `dmaic_plan` stored a plan that is not variable — DMAIC order is fixed in static edges (§3.2) — while the project's substantive plan is Define's gate document in the store plus `improve_case_index` metadata. `key_decisions` duplicated captured fields: a decision the Belt commits goes through `record_field`, is approved at a gate, and lands in `artifacts` and then the store, all outside `messages[]`, so the compression guarantee that motivated the field was already satisfied without it. `open_items` duplicated gate readiness, which `check_gate_status()` and the four-layer validation stack (§9) compute on demand — and a stored copy can contradict `DMAICGateValidator`, which a derived one cannot. `gate_passed` added to the schema block: it is what the supervisor routes on and was referenced throughout while never being declared. The Define output mapper no longer lifts `key_decisions`/`open_items` back onto the parent; it returns orchestration values only. Parent state is now `messages`, `history`, `project_id`, `project_context`, `phase_index`, `current_phase`, `gate_passed`, `final_output`. No code change accompanies this amendment — `core/state.py` is written at the `SupervisorState`/`PhaseState` split, which is still ahead in the sequence. |

| Aug 2026 | **2.2.8** | **`project_context` removed from `SupervisorState` (§4.1, §4.3, §6.3).** The fourth field to fail the same test as 2.2.7's three, and the clearest case of it: an audit found the field had **no writer anywhere** — no node, mapper or middleware set it in any document or any code path — while its schema comment claimed "set once after Define" and its only declared reader, `define_input_mapper`, runs *before* Define. No later phase read it either; §4.3 already routes Measure through Control's `phase_context` through the store. Its provenance is the Edureka lab's `task: str` (REFACTORING_AGENT_IMPROVE.md §18) — an inherited field, like the renamed `step_index` and the removed `dmaic_plan`, not a designed one. **What covers it instead:** each input mapper composes `phase_context` at the boundary — Define from the case record, later phases from the prior phase's artifacts — so the rule is now uniform and an input mapper's only dependency is `BaseStore`. The substance was never in this field to begin with: problem, goal, scope and business case are Define's gate document in the store, and title, department, belt level and target date are the case record and the `improve_case_index` row (§7.3). The `before_model` middleware (§8.5 in CLAUDE.md) already injects captured fields and prior gate documents into every coach prompt, so no planner loses context. **One addition:** a `("projects", pid, "case")` store namespace, written once at session start from `cases/case_{id}.json`, giving `define_input_mapper` a store-only source — the case blob (§6.4) stays the system of record. Parent state is now `messages`, `history`, `project_id`, `phase_index`, `current_phase`, `gate_passed`, `final_output`. **Code change:** `ANALYST_MEASURE_SUMMARY` and `ANALYST_ANALYSE_SUMMARY` deleted from `core/prompts.py` — unreferenced v1 remnants, and the `{project_context}` placeholder in the first was the field's only trace in code. `core/state.py` is unaffected; it is still written at the `SupervisorState`/`PhaseState` split. |

| Aug 2026 | **2.2.9** | **State design closed — all 15 findings from `STATE_DESIGN_RESOLUTION.md` applied (§3.6.1, §3.7.1, §3.7.2, §4, §6.3, §13).** The audit that produced 2.2.7 and 2.2.8 was run to completion across both schemas, the store, the rubrics and the validation stack. **Naming:** `project_id` → **`case_id`** everywhere (§4.1.1) — the code, both Azure AI Search indexes, the blob layout and the case models already said `case_id`, and only the governance documents disagreed; `artifacts` is now the single name for a phase's captured fields, retiring `captured_fields` from prose and `phase_inputs` from v1 references (§4.9). **`SupervisorState` is seven fields**, with `gate_passed` retyped `list[str]` → `dict[str, bool]` and `final_output` `str` → `Optional[dict]`; `current_phase` and `phase_index` are documented as derived-but-kept, with the supervisor owning consistency from a single write site (§4.1.2). **`PhaseState` gains four fields and loses one name**: `gate_attempts` (the counter whose absence reintroduced the v1 "attempts always reset to 0" bug — §4.2.1), `validator_feedback` (accumulated per-attempt feedback, without which the shared cap of 3 is retry-without-memory — §4.2.2), and `citations` / `uploads` (the evidence trail the gate document could not previously show — §4.2.3); `feedback` → `belt_edits`, splitting the Belt's gate corrections from the system's validation results; `final` `str` → `dict`; `coaching_plan` confirmed a single transient `dict`, not a list (§3.5). **Finding 2 — the missing writer:** `gate_apply_node` writes the approved gate document to **both** `store.put(("projects", case_id, "artifacts"), phase, …)` and `PhaseState.final`, and the store-mediated handoff had until now been specified with a reader and no writer (§3.6.1). The `gate_documents` store namespace is retired as a duplicate of `artifacts`, and the store prefix becomes `store/projects/{case_id}/{kind}/{key}.json`. **Typing:** all captured fields are `str`, parsed by the 18 computation tools at the point of use — §4.6 corrects the earlier claim that Measure reads Define's baseline as a typed float, which no schema in this project ever provided. Three cross-phase reference fields are the enumerated exception, carrying `references_phase` / `references_field` / `references_value` so the grader verifies linkage deterministically rather than by LLM judgment (§4.7). Computation-tool output lands in `artifacts["computation_results"]` as a list of typed dicts, giving the grader a mechanical answer to "was a hypothesis test actually run?" (§4.8). **Two-tier fields (§3.7.1):** Tier 1 blocks at Layer 2b, Tier 2 produces a grader warning the Belt may proceed past with a recorded `acknowledged_gaps` entry — which resolves the Layer 2b / Layer 2d contradiction where the grader could fail what the gate never required. `CriterionVerdict` gains `"warning"` alongside `"pass"` and `"fail"`, plus a `tier` field. The grader is belt-level aware: FMEA, DOE, X-Y matrix and statistical problem statements are flagged for Black Belt only and suppressed for Green Belt; stability / special-cause analysis warns strongly for both (§3.7.2). **New fields (§13):** `voc_summary` (Define, Tier 1), `problem_statement` consolidated (Define, Tier 1), `baseline_sigma` (Measure), `ruled_out_causes` (Analyse), `post_improvement_metric` / `improvement_delta` / `financial_impact_verified` / `handover_documented` / `lessons_learned` / `transferability` (Control) — a project that cannot show the baseline moved has not demonstrated anything. No code change accompanies this amendment; `core/state.py` and `core/substate.py` are written at Step 4.1. The dead `ANALYST_MEASURE_SUMMARY` / `ANALYST_ANALYSE_SUMMARY` templates were already removed in 2.2.8 and are confirmed absent. |

| Aug 2026 | **2.2.10** | **Findings 16–23 applied — the executor contract, node names and output schemas closed (§3.2.1, §3.3.2, §3.4, §3.4.1, §4.10, §8.1, §8.2, §13).** A second reading pass over the three documents after 2.2.9 found eight further inconsistencies, all of them between prose that had been ratified and code examples that predated it. **Node names (16):** the phase subgraph is `planner → executor → validation_stack → gate_review → gate_apply`. `policy_advisory` as node 3 was the serious error — it left the subgraph with **no node running the four-layer stack** — and `revise` as node 5 both misnamed and undersized `gate_apply`, which runs the policy advisory, processes approval, and writes the gate document. Revision is an edge back to the planner carrying `validator_feedback`, not a node. **Executor tool binding (17):** the gate validator and the policy advisory were listed among the executor's bound tools; neither is a tool. The validation stack is a node reached by an edge — as a tool the coach would decide whether to be validated, which is backwards — and the policy advisory is logic inside `gate_apply`, firing when the coach is no longer in the loop. **Two graders, two rubrics (18, 20):** `DMAICGraderMiddleware` grades the coach's **process** against a single shared `COACHING_QUALITY_RUBRIC` on **every turn**; validation Layer 2d grades the **gate document** against the phase's `PHASE_RUBRIC` **once**, at the boundary. They are complementary — the middleware prevents eight turns built on a weak foundation, Layer 2d catches cross-field and cross-phase contradictions no per-turn check can see. §3.7's step 2d had named the middleware, which was wrong. **Middleware (21, 19):** `ModelRetryMiddleware` adopted, taking the stack to **five**; it is the mechanical-retry tier (retry the same call) and does not overlap the fallback chain (swap the model). `BeforeModelStateInjection` moved from **last to first** — declaration order is execution order for `before_model` hooks, so listing it last placed project facts after skills loading and summarisation had already shaped the prompt, inverting the rule §8.5 exists to enforce. **Output schemas (22):** two conflicting `DefineOutput` definitions existed, neither matching the ratified fields and both using `float` against §4.6; `MeasureOutput`, `AnalyseOutput`, `ImproveOutput` and `ControlOutput` were referenced throughout and defined nowhere. All five are now canonical in §4.10 with per-phase gate assembly, and all five carry the same four gate-metadata fields — the cross-check found `citations` and `uploads` reaching `PhaseState` but never the gate document. **Structured output (23):** `response_format` on the executor is correct and is retained; the error was the schema. It carries **`CoachingResponse`** — a per-turn extraction of `message`, `fields_captured` and `citations` — not a complete gate document the coach cannot produce on turn one. `value: Any` in `fields_captured` is required so the three cross-phase reference dicts remain capturable. **`record_field` is retired**, taking the universal eight to **seven**: capture is now part of the response shape rather than a tool call the coach can omit mid-retrieval. Per-phase totals become Define 8, Measure 15, Analyse 12, Improve 8, Control 11 — Measure moves off the top edge of the 10–15 selection-quality range. **Integrity check run across all three documents:** field types, node names, canonical identifiers, both rubrics, store namespaces, tier classification, verdict statuses, tool counts, and the complete capture-to-store schema chain verified mechanically — every schema field assembled, every Tier 1 field coach-reachable, every Tier 2 field capturable or computable (§4.10.4). No code change accompanies this amendment. |

| Aug 2026 | **2.2.11** | **eBook extraction gaps closed — Findings 24 and 25 (§3.4.2, §4.10.5, §4.10.6, §13).** The five BB eBook extractions under `skills/extraction/` identified **57 deliverables with no corresponding field**. Six cross-cutting decisions close 25 of them; the rest are handled by SKILL.md coaching content or by mechanisms that already exist, and both sets are recorded in §4.10.5 so they are not re-litigated. **Two fields land on all five schemas:** `issues_and_barriers` (**Tier 1** — every real project has blockers, and a Belt reporting none has not looked; distinct from `acknowledged_gaps`, which is system-generated and records skipped Tier 2 fields) and `secondary_metrics` (Tier 2 — the field that catches a project which succeeded on its own terms and did damage elsewhere; a named eBook deliverable in every phase). **Measure gains two Tier 1 fields:** `xy_matrix_summary` and `vital_few_xs`, carrying the eBook's own labelled Measure→Analyse hand-off, which previously had no carrier at all — Analyse's entry condition was a list nothing recorded. **Analyse gains `practical_significance` (Tier 1)**, restoring the eBook's two-gates-in-series rule: a root cause significant at p=0.001 that explains 0.1% of the problem is not worth an Improve solution, and Improve's `pilot_result` rubric already demanded both. Analyse also gains `statistical_problem_statement` and `process_owner_buyin` (Tier 2); Improve gains `explanatory_power` and `process_owner_buyin` (Tier 2); Control gains `project_signoff` (Tier 2), which the gate had been asking for with no field able to answer. **`control_plan` becomes a `dict` of five sub-plans** — documentation, monitoring, response, training, aligning_systems (§4.10.6). A single string could not show that four were done and one was skipped, which is what the eBook's ten roadmap steps (five develop, five implement) exist to surface; four extraction gaps close with this one change. **FMEA is deliberately NOT added to any schema** (§4.10.5) — heavy manufacturing methodology built around severity × occurrence × detection scoring of physical failure modes, where the typical Agent Improve case is service or transactional DMAIC and `xy_matrix_summary` / `vital_few_xs` already do the prioritisation job. If a Black Belt performs one it lives in `uploads`. **Two tier/placement corrections:** the statistical problem statement moves from Define BB-only to **Analyse, all Belts**, where the eBook asks it; and the X-Y matrix stops being BB-only, becoming a Tier 1 field for everyone. DOE is now the only belt-gated item in §3.7.2. **Finding 25 — the six-step computation coaching pattern (§3.4.2):** explain why → guide data preparation → run → interpret → visualise → coach the next move, for all 18 computation tools, enforced by a new `COACHING_QUALITY_RUBRIC` criterion checked on every turn. A coach that returns `p_value: 0.001` with no interpretation has handed the Belt a number they cannot act on or defend at a gate. This is the most content-heavy part of each SKILL.md — Measure's eight computation tools alone are 160–320 lines. **Page citation corrected:** §13.5 and REFACTORING §42 cited "eBook p681" for verified financial impact; that page is the Control quiz cover and the material is at **book pp677–679**. **Field counts:** Define 14 · Measure 12 · Analyse 13 · Improve 12 · Control 15. No code change accompanies this amendment. |

| Aug 2026 | **2.2.12** | **Process maps, stability and experiment justification promoted to schema — Finding 26 (§4.10.7, §13).** Three of the nine gaps that v2.2.11 assigned to SKILL.md coaching content were reclassified as **Tier 1 fields**, on one argument: a coaching prompt produces a conversation, and a conversation cannot be read by the next phase's planner or checked by the grader. **`process_map_sipoc` (Define, Tier 1, dict)** — six sub-fields: suppliers, inputs, process_steps, outputs, customers, process_kpis. The failure this catches is the partial map: *“far too often Belts capture only segments of the process”*, which produces a project that cannot show improvement because the baseline never covered the whole thing — invisible at Define, expensive at Control. The coach validates end-to-end coverage, challenges fragments, checks consistency with `project_scope`, and decomposes an uploaded diagram into the structured form rather than accepting the image as the deliverable. **`detailed_process_map` (Measure, Tier 1, dict)** — six sub-fields: steps, cycle_times, resources, value_vs_waste, measurement_points, baseline_kpis. The coach checks it expands Define's SIPOC correctly and that measurement_points align with `data_collection_plan`. **These two close the before/after KPI chain**: Define's `process_kpis` names what is measured, Measure's `baseline_kpis` holds the before values, Control's `post_improvement_metric` holds the after — and the grader verifies the same measurement points carry different values, so a project whose Control metrics sit on steps Define never listed is caught. **`stability_assessment` (Measure, Tier 1)** — was a Tier 2 rubric criterion with no field and a strong warning; the warning was right and the tier was not. The eBook sequences stability as a precondition for capability (book p230), because a Cpk computed across special causes is an average of two different processes, not a capability figure. **`experiment_justification` (Improve, Tier 1)** — does not require an experiment, it requires a decision, stated as one of three: DOE conducted, simplified one-factor experiment, or none needed because the solution follows from root cause analysis. All three are valid; the failure it catches is drifting past the question, not skipping DOE — consistent with the eBook's own *“do not force Designed Experiments”* and its estimate that over 80% of projects find their solution in Analyse. The Improve SKILL.md carries a plain-language DOE explanation so a Belt without statistical training chooses rather than defaults. **Structured dicts go from one to three** (§4.10.4) — `control_plan`, `process_map_sipoc`, `detailed_process_map` — distinct from the three cross-phase reference dicts, and the grader checks every sub-field is populated. All three are Tier 1 and use bracket access in gate assembly; only the cross-phase reference keeps `.get(…, {})` for shape-guarding. **Six gaps remain deliberately field-free** and are listed in §4.10.5: stakeholder analysis, project plan, short/long-term capability, lean opportunities, benefits deferral date, Define-stage finance involvement. **Field counts:** Define 15 · Measure 14 · Analyse 13 · Improve 13 · Control 15. **Tier 1:** 6 · 7 · 4 · 4 · 3. Schema/assembly parity and the per-phase compatibility table verified mechanically in both documents. No code change accompanies this amendment. |

| Aug 2026 | **2.2.13** | **`imr_chart_limits` added to the Control phase (§8.2, §13.5).** Control's chart set covered batched measurements (`xbar_r_chart_limits`), proportions (`p_chart_limits`) and counts (`c_chart_limits`), but not the individuals / moving-range chart — which the eBook recommends for most **inputs** and for low-volume or long-cycle processes (book p631). That is the common case in service and transactional work: most office processes produce one figure per week, not batches of five. Without the tool the Control skill had to coach a workaround — aggregate into weekly totals and use a proportion chart — which is the wrong chart for the data and produces limits that do not mean what the Belt thinks. **Control goes from 11 tools to 12**; the maximum across phases is unchanged at 15 (Measure), so the §5.2 cap of 16 is untouched. **A pre-existing count error was found and corrected in the same pass:** every document has said "18 computation tools" since v2.2, while the §8.2 table has always enumerated **19** (1 + 8 + 5 + 1 + 4). With the new tool the correct figures are **20 computation tools and 27 total**. The table was always right and the prose was wrong; the figure had been restated across nine amendments without anyone re-deriving it. Per-phase totals are now **8 / 15 / 12 / 8 / 12**. No code change accompanies this amendment — `knowledge/computation.py` is written at Step 3.4. |

| Aug 2026 | **2.2.14** | **Computation coaching goes from six steps to seven; three new `COACHING_QUALITY_RUBRIC` criteria; §87 backlog item 15 (§3.4.1, §3.4.2, §87).** The first SKILL.md review produced 17 notes, three of which change the coaching approach rather than its content. **Seven-step computation pattern (§3.4.2).** Step 1 is now *educate on the concept* — what this **is**, in plain language, with a real-world analogy, and what the output numbers will mean, before any are produced. The original pattern opened with “explain why”, which assumes the Belt already knows what a Cpk or a p-value is; most do not, and Agent Improve exists to serve teams with no Six Sigma qualification (§1). A Belt told “this matters because it shows capability” and then handed `Cpk = 0.82` has learned nothing — they cannot judge whether 0.82 is good, and cannot defend it at a gate. Educating first also front-loads the interpretation: by the time the number arrives the Belt already holds the frame, so step 5 confirms rather than introduces. **Three rubric criteria added (§3.4.1).** *Show a concrete example of a completed answer before asking the Belt to produce theirs* — describing what good looks like in a SKILL.md tells the developer, not the Belt, and show-first reaches a good answer in one turn instead of three of ask-and-correct. *No external URLs from training data* — a model asked about methodology will produce stale, unverifiable links outside the grounding contract of §1.9; methodology comes from `rag_lookup_methodology`, woven into the coach's own voice. *Educate before computing*, replacing the narrower “explain the purpose before calling”. **§87 backlog item 15 — multi-source knowledge index (Finding 27).** `source_document` and `tenant_id` on `improve_knowledge_index`, a priority-ordered retrieval filter in `rag_lookup_methodology`, and phase-classifier re-evaluation for non-BB-eBook documents. Deferred because the refactor builds against one knowledge source and the change is incremental — two fields and one filter clause — with no second document to test against. Overlaps item 1 (multi-tenant filtering on `improve_case_index`); both fire on the same trigger and should be planned together. **All five SKILL.md files rewritten** to the show-first pattern, with an A→F session flow (opening → resumption → per-field → capture feedback → Tier 2 offered → gate ready), a per-phase Document Layout section defining how the live gate document renders, upload handling, `CoachingResponse` capture instructions, and the seven-step sequence for all 20 computation tools. No code change accompanies this amendment. |

| Aug 2026 | **2.2.15** | **Frontend Patterns 3 and 4 merge into the live gate document (§11.4, §11.6, new §11.7; REFACTORING §77).** Showing the Belt their captured fields (Pattern 3) and showing them their progress (Pattern 4) are the same view at different zoom levels, and splitting them across two moments produced the wrong behaviour: fields visible only at the gate, progress visible only as a number. They are now one component — a single live document tab beside the chat, always visible, updating the moment a field is captured via `CoachingResponse.fields_captured` (§4.10.1), readable as a document rather than a field list, and downloadable as PDF or Word at any point with `[not yet captured]` placeholders mid-phase. **The rendering spec lives in the skills, not here.** Each SKILL.md carries a Document Layout section defining which fields get headers, which render as tables, and where `computation_results` and `citations` appear; §11.7 and REFACTORING §77 cross-reference all five. The layout is a coaching artefact — it decides what the Belt sees while being coached and what they hand a sponsor — and it changes when the field set changes, so keeping it beside the coaching guidance means one file changes rather than two. **Two stale claims corrected in the same pass.** Progress is derived from `PhaseState.artifacts` against the phase's Tier 1 / Tier 2 field list; there is no stored `completeness_score`, and a stored one would be a second source of truth able to disagree with the gate (§4.1). Tier 1 and Tier 2 get **separate** counts — a Belt at 6/6 required and 0/5 recommended can pass the gate, where a single blended percentage would read 55% and imply otherwise. §77's Pattern 3 example and its data-mapping list still used the v1 `what` / `why` / `scope` / `how_goal` field names and `captured_fields`; both now use the ratified schema. **No code change and no CLAUDE.md change** — no rule moved, so CLAUDE.md stays at 2.2.14. The data these patterns need is already checkpointed in `PhaseState.artifacts` (§4.2); what was missing was the rendering spec. |

<a id="L12916"></a>
#### Original lines 12916–12924 › F.2.1 Amendment procedure — the former §18.1

1. The decision is recorded in REFACTORING_AGENT_IMPROVE.md with its
   rationale
2. The rule lands in CLAUDE.md
3. The design lands here
4. Version number incremented, change log entry added
5. **If the change touches an index schema, §7 is updated in the same
   commit as the Azure AI Search change** (§7.7)

Architecture changes are separate commits from feature changes.

