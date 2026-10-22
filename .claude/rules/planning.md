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
- Each report gives the new top of each lane's queue (`python tools/control_board/rank.py`).
- Never pick work outside the rank without a founder override (`priority_override`, with
  its reason, set only by the founder).
- When Claude Code finds that a requirement is wrong, missing or conflicting, it never edits
  business.md or platform.md: it reports the finding to Desktop as a proposed change; the
  founder rules; then process 1 runs (guard rule 20 refuses an edit without `Ruling:`).

## Prompt cycle (brief Part F9, 2026-09-28)

- Define's scope is frozen (founder, 2026-10-22): no new feature or requirement. A problem found is a
  defect fixed in its feature; one needing a new feature is reported on a post-Define list, not
  built, unless it breaks a Must.

- Packages are fixed in the feature list (`package`); `rank.py` picks the next. They chain
  (founder, 2026-10-21): when a package's area tests pass, the next starts; stop only for a design
  decision, a conflict with an accepted ADR or a failing live run. Packages built on the same day
  share that day's run-through; they land together after it — one push, one report.
- One commit per feature, or one for features sharing a code change; it lands only if every
  DEF it names and their dependencies pass.
- Questions are asked at the start, together, never mid-run.
- Before coding a package, list its assumptions (framework, accepted ADRs, repo rules), each probed
  by a test or a cited ADR line; a failed one stops the package, reported before code.
- The day's one report lists what its live run found, each with its escape class; the count should fall.
- Area tests while working; the full suite only in the hook. Never rerun a passing suite.
