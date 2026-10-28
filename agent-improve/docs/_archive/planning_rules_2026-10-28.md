# Planning rules as they stood before 2026-10-28

Archived when `.claude/rules/planning.md` was rewritten to its size budget to take the founder's ruling of
2026-10-28 (locked parts, test scope, Define closing by 7 November 2026). Each rule below is restated in place there;
what changed: "packages built on the same day share that day's run-through; they land together after it" became the
full suite once per wave and one push; "area tests while working; the full suite only in the hook" became the touched
modules' tests and a smoke set per commit. Verbatim, frontmatter dropped:

# Planning — process 2: the queue is computed

Brief Part F5 (founder, 2026-09-27); the rule is ADR-0058. Process 1 is the
`new-requirement` skill.

- The queue is recomputed on every commit (`tools/control_board/rank.py`, run by the
  pre-commit hook). Nobody writes an order of work by hand.
- Each report gives the new top of each lane's queue (`rank.py`).
- Never pick work outside the rank without a founder override (`priority_override`, with
  its reason, set only by the founder).
- When Claude Code finds that a requirement is wrong, missing or conflicting, it never edits
  business.md or platform.md: it reports it to Desktop as a proposed change; the
  founder rules; then process 1 runs (guard rule 20 refuses an edit without `Ruling:`).

## Prompt cycle (brief Part F9, 2026-09-28)

- Define's scope is frozen (founder, 2026-10-22): no new feature or requirement. A problem found is
  fixed in its feature; one needing a new feature goes on the post-Define list, unless it breaks a Must.
- Packages are fixed in the feature list (`package`); `rank.py` picks the next. They chain
  (2026-10-21): when a package's area tests pass, the next starts; stop only for a design
  decision, an accepted-ADR conflict or a failing live run. Packages built on the same day
  share that day's run-through; they land together after it — one push, one report.
- One commit per feature, or per shared code change; it lands only if every DEF it names and its
  dependencies pass.
- Questions are asked at the start, together, never mid-run.
- Before coding a package, list its assumptions (framework, ADRs, repo rules), each probed by a test
  or an ADR line; a failed one stops the package, reported before code. A package changing a model
  call times it live once (the live slice) before landing (founder, 2026-10-22).
- The day's one report lists what its live run found, each with its escape class; the count should fall.
- Area tests while working; the full suite only in the hook. Never rerun a passing suite.
