# Brief for Claude Code: answers to your guard-scope report, housekeeping, then the M1 loop

From Desktop, founder-ratified 2026-09-28. Input: this file in `docs/founder-inputs/`.
Requirement changes carry
`Ruling: 2026-09-28 founder — T71 amended (blocked turn removed from state), M1 loop per BRIEF_m1_loop.md`.

## Answers to your report

| Your point | Founder ruling |
|---|---|
| T71's "stores nothing" is not met | Use the framework: the input guard returns `RemoveMessage` for the blocked Belt message and its reply, so the conversation state no longer holds them. `add_messages` supports this without a custom reducer or schema change (https://docs.langchain.com/oss/python/langgraph/add-memory, "delete messages"). If the channel does not use `add_messages`, stop and report; that would need an ADR. Keep `without_blocked` only as a read-side filter for cases written before the change. Amend T71 as in Part 1d. |
| The persona attack passes the fixed rules | Add narrow phrase rules for persona or role takeover, such as "you are now … without rules" or "pretend to be the grader / validator / system". Each must pass the 60 benign cases; a teammate called Dan must still pass. Prompt Shields remains the main defence. |
| Prompt Shields block mode; Content Safety not provisioned | Founder actions in the Azure portal, not yours. Keep `GUARD_MODE=development` for local runs and run-throughs, and say so in each report. |
| The coach says "recorded" when nothing was stored | A defect. Register it as G-117 (Part 1e) and build it in the first loop package. |
| DEF-029 blocks element 5 | The first loop package. |
| Full suite run by hand; 106 minutes | Noted. The loop below replaces the 60-minute box with checkpoints. |

## Part 0: Controls inventory (read-only, no commit)

List every hook, guard rule, slash command, skill, generator and test routine under `.claude/`,
`tools/`, `scripts/` and the test infrastructure in `backend/tests/`. For each one give:

- what it enforces or produces;
- how often it refused or caught something (from git log, `prompts.jsonl` and `defects.json`);
- its time per commit;
- whether it is specific to Agent Improve or generic.

Report it as one table and change nothing. Desktop uses it for the starter kit before the Agent Resolve refactoring.

## Part 1: Housekeeping (one commit per item)

a. **Unused lane copies.** Run `git worktree list`. For each lane worktree (lane-a-coaching,
   lane-b-gate, lane-c-screen-inputs, lane-integrator) and each copy under `.claude/worktrees/`,
   check for uncommitted changes and for unpushed or unmerged commits. Remove only the clean ones
   with `git worktree remove`, and report any that are not clean without touching them. Delete no
   branch that holds unmerged work.

b. **Control board labels.**
   - M1: "M1 — must work for one Belt to finish Define".
   - M2: "M2 — the other must-haves".
   - M3: "M3 — should- and could-haves".
   - Show the M1 count (passing of total) under each stage column.
   - Rename stage 2 to "Works through the 13 elements".
   - Show the latest run-through as "element n of 13 reached".

c. **ARCHITECTURE.md room.** It is at 41,629 of 42,024 characters. Free at least 3,000 characters by
   moving out text that is not design (status, rationale that belongs in an ADR, history) or by
   tightening. Change no design content. Measure the size before and after.

d. **T71 and the blocked turn.**
   - Replace T71 with this text: "Before any model call, every Belt message is checked for attempts
     to change the coach's rules (overriding instructions, fake system or assistant turns, persona
     role-play, encoded instructions) and against the limits of T93. A blocked turn answers with the
     guard's fixed guidance plus the current element and its sample, and records the threat, rule and
     signed-in person in `step_log`. The blocked message and its reply are removed from the
     conversation state, so no later model call and no reload sees them. Earlier checkpoints in the
     case's history keep them as security evidence under the case's access rules. No model is used
     to build the reply."
   - Build the `RemoveMessage` step and the narrow persona rules.
   - Test routine, from now on: every block test sends a follow-up turn and checks the next model
     input and the reload. That is the escape cause of the leak you found.

e. **Register G-117.** "The coach tells the Belt a value is recorded when nothing was stored."
   Evidence: the IMPR-2026-83B run, turns 12–13. Belt impact `wrong_data`, tier 1. Link it to a
   feature. The fix direction: any sentence telling the Belt a value was stored is produced in code
   from the storage result, like the read-back, never by the coach model.

## Part 2: The M1 loop

**Rule 1: requirements are frozen.** Add no requirement and no ADR during the loop. The one
exception is a defect found by a run-through: register it as a defect with a feature and carry on.
If the fix needs a design change, stop (stop condition 2).

**How a package is chosen.** Take the top-ranked package across all lanes: at most 5 effort points,
one lane per package, never above a dependency. **The first package is fixed:** DEF-029 (the metric
definitions are proposed, so the baseline can be stored) and G-117.

**Each package:**
1. Build.
2. Run the end-to-end tests.
3. Commit (the hooks run the suite; don't run it by hand).
4. Run the scripted run-through live (`scripts/define_runthrough.py`, `GUARD_MODE=development`).
5. Add one line to the loop log in `prompts.jsonl`, and to the final report table below: the
   package, its features, the run-through's element reached, the turns, the model calls, the longest
   turn and the minutes taken.

**Stop conditions.** Stop at a clean commit and report when any of these happens:

| # | Condition |
|---|---|
| 1 | A founder decision is needed: a requirement is unclear or conflicting |
| 2 | A fix needs a design change, which means a new ADR (the design gate) |
| 3 | The run-through regresses: it reaches an earlier element than after the previous package, or a turn exceeds 45 s |
| 4 | A feature fails three attempts. Register it as a defect with an 8D (occurrence and escape cause) and stop |
| 5 | 4 hours of loop time have passed (checkpoint) |
| 6 | The live-call budget is spent: 1,500 model calls for this run |
| 7 | **M1 is reached:** every tier-1 feature passes, and the run-through reaches an approved Define with the next turn in Measure |

When condition 7 is met, also record the Part E evidence still owed: submission, approval and the
next turn entering Measure.

## Report

| Part | Commit(s) | Evidence |
|---|---|---|
| 0 | none | the controls table |
| 1a–1e | … | worktrees removed or reported; board labels; ARCHITECTURE.md size before and after; T71, `RemoveMessage`, persona rules, follow-up-turn tests; G-117 |

Loop log, one row per package:

| # | Package (features) | Run-through: element reached, approved? | Turns | Model calls | Longest turn | Minutes | Commit |
|---|---|---|---|---|---|---|---|

Finish with the stop condition that ended the run, the M1 count (n of 42), the total live calls,
and a timing line.
