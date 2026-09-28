# Brief for Claude Code — Part F: the procedures, enforced by the repo

From Desktop, 2026-09-27. Run after Parts A–E are reported and reviewed. Inputs:
`docs/founder-inputs/ADR-0057-input-guard-node.md`, `docs/founder-inputs/ADR-0058-refactoring-order-is-computed.md`.
0 live model calls. One commit per step below unless a step says otherwise; report each with its
evidence and end with the timing line.

Goal: every new or changed requirement, whoever proposes it, runs the same procedure —
requirement → design decision (ADR if needed) → features → rank → build → ARCHITECTURE.md — and the
repo refuses any shortcut.

## F1. ADRs

1. Place ADR-0058 in `docs/adr/` as ACCEPTED (founder, 2026-09-27). Place ADR-0057 as PROPOSED
   (awaits the founder's ruling on T71 and on fail-closed).
2. Write `docs/adr/README.md`: the five parts (Status, Context, Decision, Consequences, Rejected),
   the lifecycle PROPOSED → ACCEPTED → SUPERSEDED, "never edited, only superseded", and the index
   of all ADRs with status.
3. Write `.claude/rules/adr.md` (`paths:` requirements, ARCHITECTURE.md, backend/): an ADR is
   required when a change touches a state field or schema, the graph (nodes, edges, routing),
   middleware, persistence (checkpointer, Store, Blob, indexes), an external service, the security
   boundary or a banned pattern, or when there is a real choice between alternatives.

## F2. Requirement fields

Every requirement entry in business.md and platform.md gains two fields, on its heading line:
`MoSCoW: Must | Should | Could | Won't-now` and `Design: ADR-nnnn | none`.
Fill `Design:` from the existing ADRs where one applies (list your mapping in the report).
Leave `MoSCoW:` as `?` everywhere — Desktop proposes the values, the founder ratifies them.
The requirement checker refuses an entry missing either field (a `?` MoSCoW is allowed until
ratified, and is shown on the board under "Waiting for the founder").

## F3. Feature fields and the computed rank (ADR-0058)

1. Add to every feature: `belt_impact` (dead_end | wrong_data | data_loss | degraded | none),
   `rework_risk` (high | low), `effort` (S | M | L), `priority_override` (null, or
   `{rank_tier, reason}`, founder only). Fill `effort` and `depends_on` from the code; propose
   `belt_impact` and `rework_risk` and list them in the report for Desktop's review.
2. Remove the typed `priority` field added in Part A; its values become the first proposal for
   `belt_impact` (priority 1 → the Belt-blocking values).
3. Scales used by the score (tunable only by a founder ruling): belt impact dead_end / wrong_data /
   data_loss = 3, degraded = 1, none = 0; rework risk high = 2, low = 0; unblocks = number of
   failing features that depend on it, directly or transitively; effort S = 1, M = 2, L = 3.
4. `tools/control_board/rank.py`, run by the pre-commit hook: tier 1 = Belt-blocking impact and
   Must; else MoSCoW tiers; within a tier score = (impact + rework risk + unblocks) ÷ effort;
   never above a dependency; override wins. Rank and reason are computed, never stored.
5. The board's "Next failing feature per lane" and "By priority" use the rank and show each rank's
   reason. Milestones M1–M3 map to tiers.
6. CLAUDE.md session start: replace "take the next failing feature in your lane" with "take the
   top-ranked failing feature in your lane". Replace text; do not grow the file.

## F4. Guards

| Rule | Refuses |
|---|---|
| Coverage (upgrade Part E's warning) | a commit that leaves an ACCEPTED or RATIFIED requirement with no feature citing it |
| Design gate | landing a feature whose requirement says `Design: ADR-nnnn` while that ADR is not ACCEPTED |
| Founder ownership | any change to `docs/requirements/business.md` or `platform.md` without a trailer `Ruling: <date> <what the founder ruled>` |
| ADR immutability | a change to an ACCEPTED ADR other than setting its status to SUPERSEDED with the superseding number |
| Design drift (from Part C) | a change to a file named in ARCHITECTURE.md §3 without an ARCHITECTURE.md change or `Design: unchanged` |

Register each with its rule number. Prove each: one refused commit, then the passing one.

## F5. The two procedures as instructions

1. `.claude/skills/new-requirement/SKILL.md` — process 1, run whenever the founder rules a new or
   changed requirement:
   1. add or change the entry (with `MoSCoW:` and `Design:`), commit with `Ruling:`;
   2. if `Design: ADR-nnnn`, add the ADR as given by Desktop (PROPOSED or ACCEPTED as ruled);
   3. add features: requirement id, failing test stub, lane, `depends_on`, `effort`,
      proposed `belt_impact` and `rework_risk`;
   4. let the hook re-rank; report the requirement, the features and the new top of each lane's queue.
2. `.claude/rules/planning.md` — process 2: the queue is recomputed on every commit; after a
   feature passes, a defect is registered, a run-through is recorded or a requirement changes,
   report the new top of each queue; never pick work outside the rank without a founder override.
3. When Claude Code itself finds that a requirement is wrong, missing or conflicting, it does not
   edit the requirement file: it reports the finding to Desktop as a proposed change (the founder
   rules, then process 1 runs).

## F6. Wiring check

A component that exists but is not wired has been the most repeated failure of this refactor
(declared-but-unwired has recurred at least seven times; G-112 is the latest: the output mappers
had no production caller). Add `tools/architecture/wiring.py`, run by the pre-commit hook, reading
source with `ast`:
1. Every node, middleware, mapper, tool and route named in ARCHITECTURE.md §3 has a production
   caller (reached from `core/graph.py`, `_build_executor` or a route), not only a test caller.
2. Every route that changes case state reaches the compiled graph or a named storage function.
3. Every feature test is end-to-end: it drives the compiled graph (or the API) with only the model
   replaced; a feature test that calls a node or mapper directly is flagged.
Findings appear on the board (F7, "Wiring health"). The check warns in this part; after the
founder reviews the first findings, it becomes a refusal.

## F7. The control board — a value-stream picture, updated on every commit

Same file (`docs/control-board.html`), same generator, run by the pre-commit hook after `rank.py`
and `wiring.py`. Inputs: every `docs/*_features.json` (Define today; Measure and later phases add
their own file), `test-results.json`, `defects.json`, business.md, platform.md, `docs/adr/`, the
latest run-through record, the wiring findings, git log. Nothing on it is typed by hand. **No long
lists**: the page is pictures, with at most three short lists.

1. **New feature fields**: `phase` (define | measure | …), `stage` (where in the Belt's journey,
   below) and `layer` (screen | api | coaching | gate | persistence | platform). Fill them for every
   feature and list the mapping in the report for Desktop's review.
2. **Status of a feature** (derived, never stored): **green** = its test passes; **amber** = its
   test is written (no longer the "not yet written" stub) and fails, or it is its lane's current
   top-ranked feature; **grey** = open (stub, not started). A red outline marks tier-1 items.
3. **Layout, top to bottom:**

| # | Block | Form |
|---|---|---|
| 1 | Phase tabs | Define now; one tab per phase as its feature file appears |
| 2 | **Define complete** | one large percentage (passing ÷ all ranked features of the phase), with three bars under it for M1, M2, M3 |
| 3 | **Belt journey** | the run-through as a strip of the six stages — Open case · Coached through the elements · Report · Approve · Record written · Next phase opens — with the 13 Define elements as small squares inside stage 2; filled up to where the latest run-through got; a sparkline of the last run-throughs underneath |
| 4 | **Value stream** | a grid: columns = the six stages, rows = the six layers; every feature is a small coloured tile in its cell (green / amber / grey), tooltip = id, description, rank reason; each column shows its own % complete at the bottom |
| 5 | **Now per lane** | one line per lane: the amber feature being worked and the next one (list 1) |
| 6 | **Waiting for you** | PROPOSED requirements and ADRs, `MoSCoW: ?`, open decisions (list 2) |
| 7 | **Health strip** | four small counters: open defects · wiring findings · accepted requirements without a feature · type-error record; each opens a short list on click (list 3) |
| 8 | Burn-up | passing features over time, per milestone |
| 9 | Last commits | as today, collapsed by default |

4. **Pointer detail**: hovering any tile, stage, bar or counter shows a tooltip; clicking opens a
   side panel with everything behind it — for a feature: id, description, requirement (with its
   MoSCoW and ADR), lane, stage, layer, test path, status and since when, rank and its reason,
   depends_on and what it unblocks, the last commit touching it, any linked defect.
5. Match the layout of `docs/founder-inputs/control-board-mockup.html` (example data only; the real
   board fills it from the inputs above).
6. Remove the current "by clause", "by lane" and "next failing feature" tables; blocks 4 and 5
   replace them.
7. For a later phase, the same page gains a tab: that phase's stages replace the journey strip,
   the layers stay the same.

## F8. New requirements from the trusted-source check (founder ruling 2026-09-27)

Run through `/new-requirement` once F5 exists — this is its first real use.

1. platform.md, with `Ruling: 2026-09-27 founder accepted T85–T87 and the T69/T34 amendments`:
   - amend **T69**: "… enforced with `ModelCallLimitMiddleware`; calls outside the agent are counted
     in `step_log` against the same budget" — `Design: ADR-0059`
   - amend **T34**: "… model fallback with `ModelFallbackMiddleware`; the degraded answer after the
     last model stays in code" — `Design: ADR-0059`
   - add **T85** Contextual retrieval: chunks carry a short context before embedding and keyword
     indexing, and a semantic reranker orders the fused candidates; a new index goes live only when
     the eval set shows it retrieves better at top-10 or top-20 — `Design: ADR-0060`
   - add **T86** Offline eval set: 20–50 Define tasks from real failures, graded by code, then the
     rubric model, with a human sample; pass^3 reported; run before a release and on changes to
     prompts, skills, graph or model settings — `Design: ADR-0061`
   - add **T87** Personal data: e-mail, phone, account and card numbers in uploads and tool results
     are masked before a model sees them; person names are kept; each masking is logged by type
     and count — `Design: ADR-0062`
2. Place ADR-0059 to ADR-0062 from `docs/founder-inputs/adr/` in `docs/adr/` as PROPOSED; the
   founder's ratification follows in the report review. Also record in ADR-0059 why the hop budget
   stays custom.
3. Add features for each (T86 before T85: `depends_on`), with the new fields. They land only when
   their ADR is ACCEPTED (F4 design gate).
4. Part B finding to confirm and report: does ingest already add chunk context or use a reranker?
   Does the evidence lookup use top-10?

## F9. Prompt cycle time — measured, bounded, on the board

1. **Record every prompt** in `.claude/logs/prompts.jsonl` at its end: start, end, feature(s) or
   part, commits, time in tests, time in hooks, time waiting for the founder (questions asked),
   time lost to refused commits and reruns, live model calls. The existing timing line becomes a
   summary of this record.
2. **Work packages.** `rank.py` also forms each lane's next **work package**: start from the lane's
   top-ranked failing feature, then add the next-ranked features of the same lane that touch the
   same code area (same `layer` and `stage`, or the same module in their sources) or that depend
   on a feature already in the package, until the package reaches 5 effort points (S = 1, M = 2,
   L = 3). A feature of another area is never pulled in ahead of its rank; it starts the next
   package. The board shows "Next package" per lane, with its features and effort total.
3. **Rules** in `.claude/rules/planning.md`, **effective from 2026-09-28** (this brief itself runs as
   one long prompt, by founder decision):
   - one work package per prompt per lane;
   - one commit per feature, or several features in one commit when they share their code change;
     a commit may name several DEF ids and lands only if all of them and their dependencies pass;
   - questions are asked at the start, together, not mid-run;
   - a time box of 60 minutes: when it is reached, finish the current commit, report where it
     stands and what is left of the package, and stop;
   - area tests while working, the full suite only in the hook (unchanged); no reruns of a passing
     suite.
4. **Board block "Prompt flow"** (after "Now per lane"): the last 15 prompts as stacked bars —
   building (green), tests and hooks (blue), waiting for the founder (grey), rework after a refusal
   (red) — with the median cycle time against the 60-minute line. Pointer detail per bar: the
   prompt's subject, commits and features.

## Report

| Step | Commit | Evidence |
|---|---|---|
| F1 | … | ADR files and index |
| F2 | … | `Design:` mapping per requirement; checker refusal shown |
| F3 | … | proposed `belt_impact` / `rework_risk` per feature for review; the ranked queue per lane |
| F4 | … | one refused and one passing commit per rule |
| F5 | … | skill and rule files |
| F6 | … | the first wiring findings, listed for Desktop |
| F9 | … | the prompt record for this run and the new board block |
| F8 | … | the platform.md diff, ADRs placed, features created with their ranks |
| F7 | … | the stage and layer mapping per feature; the new board rendered (screenshot) |

Timing line at the end.
