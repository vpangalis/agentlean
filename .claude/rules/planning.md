---
paths:
  - "agent-improve/docs/define_features.json"
  - "agent-improve/docs/requirements/**"
  - "agent-improve/docs/defects.json"
  - "agent-improve/tools/control_board/**"
---
# Planning

The queue is computed (ADR-0058): `rank.py` on every commit; each report gives each lane's new top. History:
`agent-improve/docs/_archive/planning_rules_2026-10-28.md`.

- Never pick work outside the rank without a founder override (`priority_override`, with
  its reason, set only by the founder).
- When Claude Code finds that a requirement is wrong, missing or conflicting, it never edits
  business.md or platform.md: it reports it to Desktop as a proposed change; the
  founder rules; then process 1 runs (guard rule 20 refuses an edit without `Ruling:`).
- Define's scope is frozen: a problem is fixed in its feature; a new feature goes post-Define unless a Must breaks.
- Packages chain by rank; stop only for a design decision, an ADR conflict or a failing live run. One commit per
  feature or shared change, landing only when every DEF it names passes.
- Questions are asked at the start, together, never mid-run.
- List assumptions before coding, each probed by a test or an ADR line. A changed model call is timed live once.
- Locked (founder 2026-10-28): the welcome; an upload's own turn and draft read-back; VOC/CTQ rows; the problem
  statement, 5W2H map; goal, target, date; how-to answers; secondary metrics split; Gate layout A–G; R-F. Changed
  only for a blocker, with the founder's OK; their tests stay, no live calls.
- Tests: per commit the touched modules' and a smoke set; the full suite once per wave, then one push (no
  `start.ps1` while unpushed); live slices only for changed elements. Never rerun a passing suite. A wave report
  gives the time saved and what its live run found.
- Define closes by 7 Nov 2026. After the founder's final walk: only blockers, lost or wrong data and false passes;
  layout and wording go post-Define.
