# Lessons

Founder-curated. An entry is added only when the founder rules a lesson; Claude Code never adds one on its own.

Each entry: date · what happened · the lesson · where it is enforced (or "not yet enforced").

---

**2026-10-20** · Live model tests cost about €3 a day · Test live every day, but small: replay recorded answers up to
the changed element and run only that live; one full run-through per day · `.claude/rules/planning.md` (once that
rule is committed)

**(from an earlier session)** · With AI, testing the code is the easy part and runs automatically. The use cases must
be tested too: the model's answers to the Belt's questions, and the reasoning behind each decision. LangSmith
evaluation is the normal tool but comes later; until then this means deliberate time spent reviewing answers and
reasoning. The agent must also be able to report how a decision was made (EU AI Act) · enforced in part by the testing
ADR (use-case tiers) once committed; the decision report is not yet enforced
