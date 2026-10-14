# ADR-0084: Grader v2 — the evaluator judges the reply the Belt sees, on four criteria, and the coach revises once

Status: WITHDRAWN (founder, 2026-10-14: "grader stays middleware, log-only; findings reported per run; calibration after Define" — no v2 node, no revision loop, no T69 change; accepted earlier the same day)
Requirements: R1, R2, R3, R6 (the coaching moves); T69 (the call budget — see decision 7); DEF-015
Supersedes, when accepted: ADR-0081 decision 2's grader half (its log-only line stays until v2 passes);
the B2 rubric of 7e68b96 for the per-turn grader
Depends on: ADR-0080 (the 45 s deadline), ADR-0083 (the coherence call it reuses), graph.md §3.4
("reflection is a graph node reached via a conditional edge")

## Context

The grader is the architecture's evaluator (reflection) step. Measured against the founder's 40 labels it
fails: before B2, 52% false fails and 47% false passes; after B2's rubric, 60% / 27% on gpt-4o-mini and 0% /
67% on gpt-4o. The design's flaws, from the replays (report of 2026-10-14):

1. Nine to ten abstract criteria in one call, any fail = fail: 9 of the 13 good replies it failed, failed on
   one criterion only.
2. No context: no acceptance criteria, no confirmed values (B2 added the values and earlier messages; no
   criteria).
3. Criteria without definitions or examples; "reference methodology" meant whatever the model chose.
4. No "not applicable": a status of pass or fail only (`CriterionResult.status`), so a criterion that does
   not apply is failed or passed at random.
5. Verdict before reasoning (`status` is declared before `feedback`); no quoted evidence — 0 of 30 fail
   reasons quoted the reply before B2.
6. Per-criterion verdicts against whole-reply labels; nothing tells which criterion a label rests on.
7. No revision: a fail changes nothing (one grading, `GRADER_MAX_ITERATIONS` held).
8. Move filtering by keywords in the criterion text (`MOVE_EXCLUDES`), which silently changes when a
   criterion is reworded.
9. (Added) **It grades a reply the Belt never sees.** It runs on `after_agent`, inside the agent — before
   the executor's code writes the sample (G-170), removes repeats (G-171), answers a status question (G-172),
   rejects unsourced numbers (G-173), challenges a placeholder (G-174) and teaches the next element after a
   store (G-175). Replies written in code are not graded at all.
10. (Added) Its verdict, stored per criterion only, cannot be compared with the founder's whole-reply label
    without a rule for combining them; and temperature 0.1 still flipped 8 of 40 verdicts on replay.

## Decision

1. **Code checks first.** A1–A7 and G-168 stay in code and run before the grader; the grader judges only
   what code cannot.
2. **A graph node, after the executor** (graph.md §3.4): `grade` reads the composed reply the Belt would see
   — message and blocks, after every code check — and, on a fail, routes back to the executor once
   (a conditional edge), which re-runs the coach with the grader's quoted feedback as section 5. The
   revision is composed by the same code and graded once more; the better-graded reply is sent. Replies
   written in code skip the node.
3. **Four criteria (Define), each with a definition, one pass and one fail example from the labelled turns,
   and "not applicable" allowed:**
   - **C1 Teaches before asking** — on a teaching move, explains what the element is and why it matters
     (its purpose in DMAIC) before asking.
   - **C2 Challenges the right gap** — names an acceptance criterion the Belt actually left unmet, given their
     message and the confirmed values; never asks for what was already given; never lets a vague answer
     through.
   - **C3 Faithful to the Belt** — a read-back is complete and unchanged; nothing added the Belt didn't say;
     nothing they said ignored; no Confirm on an incomplete value.
   - **C4 One clear next step** — ends with one clear question or action; after a store, the next element;
     never re-confirms a stored value.
   - C7 (raw statistical output) is kept for Measure and Analyse; not applicable in Define.
   - The two lines of the old rubric outside C1–C4 become **code checks** (founder, 2026-10-14): no external
     URLs (DEF-019's link removal, now also a check), and on the phase's topic (the reply names the phase or
     one of its elements). A failed code check is a failed reply, as a failed criterion is.
4. **An explicit move → criteria table** replaces keyword filtering:

   | Move | C1 | C2 | C3 | C4 |
   |---|---|---|---|---|
   | teach | ✓ | n/a | ✓ (nothing added) | ✓ |
   | challenge | n/a | ✓ | ✓ | ✓ |
   | read_back | n/a | ✓ (no vague value let through — confirmed by the founder) | ✓ | ✓ |
   | store_and_advance | ✓ (judged on the next element's teaching — confirmed by the founder) | n/a | n/a | ✓ |
   | respond | n/a | n/a | ✓ | ✓ |
   | offer_park | n/a | n/a | n/a | ✓ |

5. **The grader's input:** the move; the element's acceptance criteria (`skills.acceptance_criteria`); the
   confirmed values; the Belt's message and earlier messages; the composed reply.
6. **Its output, per criterion and in this order:** `reasoning`, `evidence` (a sentence quoted from the
   reply, or empty), `verdict` (pass | fail | not_applicable). A fail without a quoted sentence is
   recorded as not checked, never as a fail. The reply passes when no applicable criterion fails.
7. **The call budget (founder, option a).** T69 allows a fifth model call only on a turn that revises:
   the coherence call ADR-0083 freed covers the revision, the fifth its grade. A revision never starts with
   less than 15 s before the 45 s deadline (ADR-0080's clock). A revision that fails again is sent and
   logged — never revised twice.
8. **Log-only until accepted:** the node grades and records (`step_log`, with the evidence); it routes back
   only in `enforce` mode. Accepted per criterion against the founder's labels: ≥ 90% repeatability on
   replay, ≤ 20% false fails, ≤ 20% false passes — measured on gpt-4o-mini and gpt-4o by replay before the
   model is chosen.
9. **A revision regenerates the reply text only** (founder): the coach is called once more with the
   grader's quoted feedback and no tools; nothing is stored again, no move is decided again, and the turn's
   model calls are counted with it. The revised reply names the one it replaces, and every reader of the
   conversation (the coach's next input, the reload, the route's answer) shows the revised one only.
10. **Tests for each** (founder): no tool runs in a revision, no second store, the call count, the 15 s
   floor, never revised twice.

## Consequences

- `DMAICGraderMiddleware` leaves the coach's middleware; the grading happens in the node. A new node type
  is an amendment (graph.md §3.3), made by this ADR when accepted.
- One grading call per turn in log-only mode (as today); up to two more on a failed turn in enforce mode.
- The founder's new labelling sheet (C1–C4 columns, 3122388) is the acceptance set.

## Rejected

- **Keeping the grader as `after_agent` middleware with the re-ask hook (ADR-0079's mechanism):** it would
  still grade a reply the Belt never sees (flaw 9).
- **One overall score:** a coach handed an aggregate has nothing to act on (§36).
