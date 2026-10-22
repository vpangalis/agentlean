# ADR-0107: step_log upserts on its key — a replayed step leaves one entry

Status: ACCEPTED (founder and Desktop, 2026-10-21 night; drafted by Claude Code from the ruling)
Requirements: T21; DEF-119
Refines: ADR-0020 (the audit trail)

## Context

`PhaseState.step_log` is `Annotated[list[dict], operator.add]`: every node return appends, so a node re-run — a
retry, a resume after an interrupt (LangGraph re-runs the node from its start), a restart — appends its entries again.
`field_log` solved the same problem with `merge_field_log`, an upsert on its deterministic key. Every entry `_step`
writes already carries a key (`step_key(phase, turn, node)`). Facts drafted for Desktop on 2026-10-21
(`agent-improve/Claude outputs/ADR_facts_P6_step_log_and_kept_verdicts.md`).

## Decision

1. `step_log`'s reducer becomes an upsert on its key (`merge_step_log`, like `merge_field_log`).
2. The later entry replaces the earlier.
3. Entries repeated by design — the grader's iterations, the fallback attempts — carry their attempt in the key.
4. Every entry must carry a key: a test fails on a keyless entry.
5. The stored shape is unchanged (a list of dicts), so there is no schema bump; a replay test proves an old
   checkpoint replays the same.

## Notes

Note (founder, 2026-10-22): with Desktop, option (a) of the probe (`agent-improve/Claude outputs/FINDINGS_P6_ADR-0107_0108_assumptions.md`) — a rejection run writes planner, validation_stack, gate_review and gate_apply twice under one key; the pass after a rejection is a repeat by design (decision 3) and carries `:r1`, `:r2` … in its key, counted from `len(rejection_feedback)`.
