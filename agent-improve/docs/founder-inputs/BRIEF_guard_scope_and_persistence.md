# Brief for Claude Code — answers to your topology report: guard scope, unfinished work in the checkpoint, live run

From Desktop, founder-ratified 2026-09-28. One long run by founder decision; one commit per part.
Inputs in `docs/founder-inputs/`: this brief, `adr/ADR-0066-unfinished-work-lives-in-the-checkpoint.md`,
`adr/ADR-0067-input-guard-scope-and-modes.md`. Requirement changes carry
`Ruling: 2026-09-28 founder — guard scope (R20, T71–T72 amended, T91–T94), ADR-0066, ADR-0067 per BRIEF_guard_scope_and_persistence.md`.
0 live model calls except Part E, which the founder approves.

## Answers to your report

| Your point | Founder ruling |
|---|---|
| DEF-117: where unfinished work lives | The checkpoint, ADR-0066 |
| T71 and T72 "accepted by interpretation" | Not ratified as they stood. They are replaced by the amended text below. From now on a requirement's status changes only by a ruling that names it |
| Content Safety not configured | Kept, with safeguards: ADR-0067 point 5, T94 |
| DEF-060 and DEF-062 blocked by rule 11 | Accepted; the lane A package is the next brief |
| The two dropped fixed rules | Right call; now written into ADR-0067 as out of scope |
| diagrams/01-overview.mmd and docs/_archive/ARCHITECTURE_DIAGRAMS.html | Revert both. ARCHITECTURE_DIAGRAMS is no longer maintained; ARCHITECTURE.md carries its own diagrams. If ARCHITECTURE.md does not reference `diagrams/*.mmd`, move that folder to `docs/_archive/`, and make sure no guard or generator expects it |

## Part A — Records

1. Place ADR-0066 and ADR-0067 (ACCEPTED) in `docs/adr/`, update the index; ADR-0067 refines
   ADR-0057 (link both ways in the index only; ADR-0057's file is not edited).
2. business.md, Part 1 — add:
   **R20 The coach can't be turned against its rules** · ACCEPTED 2026-09-28 · MoSCoW: Must · Design: ADR-0067
   Nothing a team member types and nothing in an uploaded file can change how the coach behaves,
   what it stores or how a gate is judged. A message or file that tries is not processed: whoever
   sent it is told in plain words why it was blocked and how to phrase it instead, using the element
   they are working on and its sample answer. Every block is recorded in the decision trail with who
   and when (R19), where the project lead can see it. Ordinary project language is never refused.
3. platform.md — replace T71 and T72, add T91–T94 (all ACCEPTED 2026-09-28, Design ADR-0067):

| Id | Requirement | MoSCoW |
|---|---|---|
| T71 | Before any model call, every Belt message is checked for attempts to change the coach's rules (overriding instructions, fake system or assistant turns, persona role-play, encoded instructions) and against the limits of T93. A blocked turn answers with the guard's fixed guidance plus the current element and its sample, stores nothing, and records the threat, rule and signed-in person in `step_log`. No model is used to build the reply | Must |
| T72 | Before an upload is indexed or read by any model, its whole text is checked, in chunks of at most 10,000 characters, for instructions addressed to the AI, including text hidden by formatting, comments, hidden cells or sheets, or metadata. A flagged file stays in the case, marked as not used by the coach, and the Belt is told which file and why. All upload text and Belt answers reach every model (coach, planner, validator, grader) inside a labelled data block, never as instruction | Must |
| T91 | The guard refuses no ordinary project language: the evaluation set holds at least 50 benign Belt messages (Lean vocabulary, German, names, pasted tables, questions about other projects); none may be blocked, and a regression blocks release (with T75) | Must |
| T92 | A model call refused by Azure's content filter (`content_filter`) is never retried and never sent to the fallback model; the Belt gets a guidance reply, not an error; the refusal is recorded in `step_log`. Prompt Shields is enabled in block mode in the Azure OpenAI deployment's filter | Must |
| T93 | Limits: a message at most 10,000 characters; an upload above 5 MB is accepted with a notice to remove content the coach doesn't need; an upload above 25 MB is refused with the same advice; at most 10 turns per minute per person. Over a limit the Belt is told the limit and the typed text stays in the box | Should |
| T94 | The guard runs strict unless development mode is set explicitly; a production start without Content Safety configured refuses to run; in development a skipped Prompt Shields check is recorded as skipped in `step_log` | Must |

4. Features per requirement (propose the inputs; the rank computes the order). DEF-117 now cites
   ADR-0066.

## Part B — ADR-0066: unfinished work in the checkpoint (DEF-117)

1. `/ask` stops writing the case blob. The blob is written at creation, upload, and approval (once).
2. The reload and any progress screen read the thread state through the compiled graph (with
   subgraph state); no route reads unfinished work from the blob. The registry and case list keep
   reading case metadata from the blob.
3. Extend the retention rule: no checkpoint of an open case is deleted (T17 widened).
4. Tests as listed in ADR-0066's Verification section: no blob write on `/ask`, reload through the
   API shows every confirmed value and the conversation, approval writes the blob once, and the 10
   development cases still reload. T13 gets its proof test.
5. ARCHITECTURE.md §2.5 (Checkpoints and persistence): correct the case blob row in place.

## Part C — ADR-0067: guard scope, replies, limits, modes

1. Guard message catalogue, one fixed text per threat (A, B, D, the Azure refusal), wording in the
   ADR. The reply adds the current element and its C3 sample from the phase SKILL.md. No model call.
2. Upload screening in chunks of 10,000 characters; flagged file kept and marked not used; the Belt
   is told which file.
3. Labelled data blocks for Belt answers and upload text in the planner, validator and grader
   prompts too, not only the coach's.
4. Limits of T93 (length, 5 MB notice, 25 MB refusal, 10 turns a minute per person), each with its
   message; the typed text stays in the box.
5. `content_filter` refusals: non-retryable in both retry middlewares and in the fallback; guidance
   reply; `step_log`. Document the deployment setting (Prompt Shields, block mode) in the
   deployment configuration; if it can't be set from code, list it as a founder action.
6. Modes: strict default, development only when set explicitly, production start refuses without
   Content Safety, `shield: skipped` in `step_log`.
7. Eval set: add at least 50 benign cases (T91) and the attack cases for T71 and T72 (with T75).
   Fake Content Safety client for tests; no live calls.
8. ARCHITECTURE.md in place: §1 decisions row (ADR-0057 plus ADR-0067), §3.2 node table (input
   guard: scope, reply, modes), the upload pipeline, §3.9 API (the limit responses). Measure the size
   first. You are in the warning band, so trim or move text before adding; report the figure.

## Part D — Clean-up

Revert the two outside edits and archive `diagrams/` as ruled above. Update the board and
`prompts.jsonl`.

## Part E — Live run (founder-approved live model calls)

Once Parts B and C are merged: one fresh case through the API with the real model. At least three
Define turns, one confirmation, a reload that shows everything, one blocked message (Threat A)
answering with the fixed reply, then Define submitted and approved, and the next turn entering
Measure. Report the model-call count per turn, the latencies against the 45-second limit (R13), the
trace ids, and anything that differs from the fake-client tests. Content Safety is not provisioned,
so this runs in explicit development mode; say so in the report.

## Report

| Part | Commit(s) | Evidence |
|---|---|---|
| A | … | ADRs placed; R20, T71–T72, T91–T94 committed; features |
| B | … | the tests of ADR-0066; §2.5 row |
| C | … | guard replies, uploads, labelled data, limits, refusals, modes, eval cases; ARCHITECTURE.md sections and size |
| D | … | reverts, archive, board |
| E | … | live run results |

Stop and ask only if a founder decision is missing. Timing line at the end. The next brief is the
lane A package (presence check, gate document, the thirteen captures, the 8D on DEF-077).
