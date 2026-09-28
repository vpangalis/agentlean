# Brief for Claude Code — requirements and architecture restructure

From Desktop, founder-ratified 2026-09-27. Inputs are in `agent-improve/docs/founder-inputs/`:
`business.md`, `ARCHITECTURE.md` (v2.0 draft), and this brief. 0 live model calls. One commit
per part, following CLAUDE.md's commit conventions; report each part with its evidence and end
with the timing line.

## The model this brief puts in place

| Layer | File | Holds |
|---|---|---|
| What must be true (founder) | `docs/requirements/business.md` | Business requirements (R, C, W, M ids) |
| | `docs/requirements/platform.md` | Technical requirements (T ids), each with its proof test |
| What to build next | `docs/define_features.json` | Features, each citing one requirement id; new `priority` field |
| Defects | `docs/defects.json` | Each closed by a feature |
| How it is built | `ARCHITECTURE.md` | Design only (contract below) |
| Why | `docs/adr/` | Decisions |
| Method | `skills/` | DMAIC content |
| Compliance | `docs/compliance/` | EU AI Act posture, DORA register |
| How to work | `CLAUDE.md`, `.claude/` | Rules |
| History | git, `docs/_archive/` | Everything retired |

**ARCHITECTURE.md contract.** It contains: overview with key decisions linked to ADRs; context,
container and graph diagrams; the coaching turn, checkpoints and persistence, and human-in-the-loop
as runtime views; components and interfaces (code layout, nodes, middleware with hooks, conditions
and failure behaviour, models, retrieval, tools, skills, validation, API, UI); data models as a
generated block with every declared field; error-handling design; testing strategy; glossary.
It never contains requirements, build status, plans, changelog, history, rejected designs, method
content, compliance registers, rationale (ADRs hold it) or repo rules. It changes in the same
commit as the code it describes.

---

## Part A — Requirements

**A1. business.md.** Copy `docs/founder-inputs/business.md` to `docs/requirements/business.md`.
Delete `define.md`, `workspace.md`, `measure.md` (git keeps them). R1–R7 keep their ids, so
existing features still resolve; W6 (cited by DEF-074) is now in business.md. Point the
requirement-id checker (and anything reading `docs/requirements/*.md`) at business.md and
platform.md. Remove the draft W6 you added to workspace.md.

**A2. platform.md — edit in place:**
1. Delete the "R8 / R9" section. Add one line under the title: "R8 moved to business.md; R9 is
   retired into T71 and T72."
2. Delete the table "Proposed features for the requirements with no proof" (features belong in
   the feature list — see A4).
3. Amend **T40**: "Every Define turn leaves a LangSmith trace **in development and test**."
4. Retire **T41** ("production refuses to start without LangSmith"): mark it RETIRED, replaced
   by T77. Production does not send traces outside the intranet.
5. Change the header status from PROPOSED to: T1–T68 ACCEPTED 2026-09-27 (except T41 retired);
   T69–T70 ACCEPTED; T71–T84 PROPOSED — awaiting founder.
6. Append:

| Id | Requirement | Proof |
|---|---|---|
| T69 | An ordinary coaching turn makes at most 4 model calls, retries included; the count is recorded per turn in `step_log` | none |
| T70 | Node time limits, retries and compensation use LangGraph's per-node `timeout=`, `retry_policy=` and `error_handler=`; no hand-written budget or retry loop | none |
| T71 | The Belt's message is screened before any model reads it — fixed rules, then Azure Prompt Shields — in a node at the front of the parent graph; a blocked turn answers with guidance, stores nothing, and records the verdict in `step_log` | none |
| T72 | Upload text is screened for hidden instructions before any model reads it, and is always passed to a model as labelled data, never as instruction | none |
| T73 | A coach reply never contains the system prompt, another case's data or an external link | none |
| T74 | Every tool is classified read-only, internal write or external effect; an external-effect tool needs human approval; credentials stay in code | none |
| T75 | The evaluation set contains prompt-attack cases; a regression blocks release | none |
| T76 | In production nothing connects to the public internet; every service is reached over a private endpoint; start-up verifies it | none |
| T77 | In production, traces and feedback stay inside the intranet (the decision trail, T84, replaces LangSmith there) | none |
| T78 | The UI loads no font, script or style from outside the product | none |
| T79 | Every request is authorised against the case team before the graph runs | none |
| T80 | Each field-log entry carries value, time, person, reason and source, and the log is append-only | none |
| T81 | The as-is process and its performance are stored structured in Define's record and read by later phases through the Store | none |
| T82 | Turn progress is streamed with LangGraph's `custom` stream mode | none |
| T83 | Reply feedback is stored against the turn's trace (T84 record in production) | none |
| T84 | `step_log` and the field log form the decision trail: append-only, kept for the life of the case, served read-only by a route, never leaving the intranet | none |

**A3.** `docs/requirements/inventory.md` stays, headed "As-is audit (2026-09-26) — not a
requirement". Its Q-list is reviewed by Desktop in a later round.

**A4. Features and priority.** Add a `priority` field (1 now, 2 next, 3 later) to every feature
and to the checker. Create a feature (lane, test stub that fails "not written yet", requirement
id) for each ACCEPTED business requirement not yet covered, and for each ACCEPTED T-requirement
whose proof is `none`. Do not create features for PROPOSED or DRAFT ids. Initial priorities:

| Priority | Requirements / features | Why |
|---|---|---|
| 1 | G-112 / DEF-060 (fold DEF-073 into DEF-060, link G-112 to it), DEF-040, DEF-005, R14, R7 number-with-unit, R13 hard limit (T24, T70), W9, W6 / G-113, W8, W10 | A Belt can finish Define without getting stuck, losing work or seeing wrong data |
| 2 | R16 / T80, C3, R17, R18, C1, C2, R5 report layout, W2, W3, W11, W12, R12 run-through gate, T69 | Define is complete and readable |
| 3 | Everything else accepted | — |

---

## Part B — Verify the ARCHITECTURE.md draft against the code

Before anything replaces the current file, check the draft and correct it where the code differs.
Report every correction with file and line.

1. Every path and symbol in the draft exists (run `tools/control_board/citations.py` over it).
2. The route list in §3.9, from `gateway/routes.py`.
3. The hook `ContradictionDetectionMiddleware` actually uses, against T55's test; state it in §3.3.
4. The declared order of the eight middleware in `_build_executor` (§3.3).
5. What `gate_review`'s interrupt payload holds for phases other than Define (§2.6).
6. Where `CoachingResponse` is declared; whether `core/diagrams.py` exists; what
   `core/citations.py` holds (§3.1, §4.3).
7. Whether the Analyse multi-hop pipeline exists in code. If not, nothing about it goes in the draft.
8. Whether `ui/index.html` loads anything from outside the product (§3.10; a finding for T78).
9. §4 is replaced by the generator's output in Part D; do not hand-edit it.

---

## Part C — Replace ARCHITECTURE.md and move the old content

1. Move the current file to `docs/_archive/ARCHITECTURE_v1.86_2026-09-27.md`. Place the corrected
   draft at `agent-improve/ARCHITECTURE.md`.
2. Move §67 and §68 verbatim to `docs/compliance/eu-ai-act-posture.md` and
   `docs/compliance/dora-risk-register.md`, each headed with its ADR (0055, 0056).
3. Move Appendix C to `.claude/rules/trusted-sources.md` and add: Kiro specs, arc42, C4 model,
   OWASP GenAI LLM Top 10, Microsoft HAX guidelines, Azure Prompt Shields, EU AI Act Articles 12
   and 50.
4. Check, do not move, and report gaps: every banned pattern in old Appendix D is enforced by
   `deprecated_patterns.yaml`; every rationale in old Parts II–XI is present in an ADR (ADRs are
   never edited — list what is missing); every method statement in old §39 and §43 is present in
   the matching SKILL.md; every Appendix B deferred item (list them; Desktop decides where they go).
5. Move `docs/architecture-sort.md` to `docs/_archive/` (its job is done).
6. Update everything that points into the old file: `docs/section-index.md` (regenerate for v2),
   CLAUDE.md's three-layer table (requirement file names), `harness-progress.md`, the CONTINUITY
   generator's version line, the size budget (base = v2's size).
7. **Rule 2b** required a changelog line in ARCHITECTURE.md when `checkpointer.py` or `routes.py`
   changed; v2 has no changelog. Founder ruling: retire rule 2b and replace it with — a commit that
   changes a file named in ARCHITECTURE.md §3 must either change ARCHITECTURE.md or carry the trailer
   `Design: unchanged`. Register the replacement with its rule number (rule 14 applies: this is a
   replacement, not a weakening).

---

## Part D — Activate the generated data models

The two Part G commits (constants module; generator, pre-commit step, guard check) must already be
in. Now that v2 carries the markers:
1. Run the generator; commit the regenerated §4.
2. Report the diff between the draft's §4 (transcribed from the old spec entries) and the
   generated §4: every field, type and default that differed.
3. Show the guard refusing a hand-edited §4.

---

## Part E — Plan and control board

**E1. The plan.** Add a section "Plan" to `docs/harness-progress.md` (replace, don't append). It
holds only what the feature list cannot: milestones and ordering rules. Priorities stay in the
feature list.

| Milestone | Done when | Features |
|---|---|---|
| M1 — Define without dead ends | every priority-1 feature passes, and a run-through reaches an approved Define report | priority 1 |
| M2 — Define complete and readable | every priority-2 feature passes, and R12 (at most 40 turns, no turn over 45 s) passes on the run-through | priority 2 |
| M3 — Define hardened | every accepted Define-scope requirement has a passing feature | priority 3 |

Ordering rule for "next feature" in each lane: lowest priority number first, then dependencies
(`depends_on`), then id.

**E2. The control board** (`tools/control_board/build_control_board.py`, regenerated every commit)
gains, after the headline:
1. **Milestones** — M1, M2, M3 with passing / total.
2. **Waiting for the founder** — every requirement marked PROPOSED or DRAFT in business.md and
   platform.md, and every row of business.md's "Open decisions" table.
3. **Requirement coverage** — one row per requirement id in business.md and platform.md: status,
   number of features, number passing. Flag in red: an ACCEPTED or RATIFIED id with no feature;
   a feature citing an id that does not exist.
4. **By priority** — features grouped 1 / 2 / 3 with pass or fail.
5. **Open defects** — each open entry in `docs/defects.json` with its feature and lane.
6. The existing sections stay: by lane, next failing feature per lane (now using the E1 order),
   burn-up (target line: the M1 date once the founder sets one), last commits with timing.

**E3. Guard.** The requirement checker refuses a feature citing an unknown id (already true) and
warns — does not refuse — on an accepted id with no feature; the warning appears on the board.

---

## Report

| Part | Commit | Evidence |
|---|---|---|
| A | … | checker passes; features created with priorities; counts from the checker, not typed |
| B | … | each correction to the draft, with code file and line |
| C | … | archive path; moved files; gap lists from C4 |
| D | … | the §4 diff; the refusal |
| E | … | the board's new sections, and the coverage count of accepted ids without a feature |

Timing line at the end.
