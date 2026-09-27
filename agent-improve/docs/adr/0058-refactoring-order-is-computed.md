# ADR-0058 — The order of work is computed from evidence, not written as a list

Status: ACCEPTED (founder, 2026-09-27) · Replaces: the `Order` column of the archived procedure

## Context

The archived procedure held the plan as a hand-written ordered list. It went stale within a day
(CONTINUITY, 2026-09-14: two of four "next" items had already landed). A priority typed into the
feature list would fail the same way: nothing explains it and nothing re-ranks it when a
requirement, defect or measurement arrives.

## Decision

The rank of every failing feature is computed on every commit from recorded inputs:

| Input | Where | Set by |
|---|---|---|
| `moscow` (Must, Should, Could, Won't-now) | each requirement in business.md / platform.md | founder |
| `belt_impact` (dead_end, wrong_data, data_loss, degraded, none) | feature | Desktop proposes, founder reviews |
| `rework_risk` (high if it changes state, persistence, the gate or a schema) | feature | Desktop proposes |
| `effort` (S, M, L) | feature | Claude Code |
| `depends_on` | feature | Claude Code |
| unblocks (features depending on it, transitively) | computed | tool |
| `priority_override` + reason | feature | founder only |

Rule, in order:
1. Tier 1: `belt_impact` is dead_end, wrong_data or data_loss **and** the requirement is Must.
2. Otherwise tier by MoSCoW: Must 2, Should 3, Could 4; Won't-now is not ranked.
3. Within a tier: score = (belt impact + rework risk + unblocks) ÷ effort (weighted shortest job first).
4. A feature never ranks above a feature it depends on.
5. An override wins and its reason is shown.

Each lane takes its top-ranked failing feature. Milestones M1–M3 (harness-progress.md, "Plan")
group the tiers and are accepted on run-through evidence.

## Where it is enforced

| Piece | Where |
|---|---|
| Ranking | `tools/control_board/rank.py`, run by the pre-commit hook |
| Board | ranked queue per lane with each rank's reason |
| Session start | CLAUDE.md: "take the top-ranked failing feature in your lane" |
| New requirement | `.claude/skills/new-requirement/SKILL.md` (process 1) |
| Re-planning triggers | `.claude/rules/planning.md` (process 2) |
| Guard | a commit adding an accepted requirement adds at least one feature citing it |

## Consequences

- The plan cannot go stale: it is recomputed from the feature list, test results and requirements.
- The founder's judgement is explicit (MoSCoW, overrides with reasons) and visible on the board.
- Estimates can be wrong; a wrong effort estimate shifts order only inside a tier, never tier 1.
