---
paths:
  - "agent-improve/docs/define_features.json"
  - "agent-improve/docs/requirements/**"
  - "agent-improve/docs/defects.json"
  - "agent-improve/tools/control_board/**"
---
# Planning — process 2: the queue is computed

Brief Part F5 (founder, 2026-09-27); the rule is ADR-0058. Process 1 is the
`new-requirement` skill.

- The queue is recomputed on every commit (`tools/control_board/rank.py`, run by the
  pre-commit hook). Nobody writes an order of work by hand.
- After a feature passes, a defect is registered, a run-through is recorded or a requirement
  changes, report the new top of each lane's queue (`python tools/control_board/rank.py`).
- Never pick work outside the rank without a founder override (`priority_override`, with
  its reason, set only by the founder).
- When Claude Code finds that a requirement is wrong, missing or conflicting, it never edits
  business.md or platform.md: it reports the finding to Desktop as a proposed change; the
  founder rules; then process 1 runs (guard rule 20 refuses an edit without `Ruling:`).

## Prompt cycle time — effective 2026-09-28 (brief Part F9)

- One work package per prompt per lane: the lane's next package from `rank.py` (its
  top-ranked failing feature plus the same-area features after it, up to 5 effort points).
- One commit per feature, or several features in one commit when they share their code
  change; a commit may name several DEF ids and lands only if all of them and their
  dependencies pass.
- Questions are asked at the start, together, never mid-run.
- A time box of 60 minutes: when it is reached, finish the current commit, report where it
  stands and what is left of the package, and stop.
- Area tests while working; the full suite only in the hook. Never rerun a passing suite.
- Every prompt is recorded in `.claude/logs/prompts.jsonl` at its end
  (`.claude/hooks/prompt_record.py`); the report's timing line summarises that record.
