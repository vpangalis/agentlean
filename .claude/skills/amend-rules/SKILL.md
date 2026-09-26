---
name: amend-rules
description: |
  How to amend a rule of Agent Improve (CLAUDE.md or .claude/rules/*.md): where the
  ruling goes, what the commit must carry, the version bump and the registry. Invoked
  by the founder when a rule changes, never by the model on its own.
disable-model-invocation: true
allowed-tools: Read, Grep, Glob, Bash, Edit
version: "1.0"
---
# Amending the rules

> Moved verbatim from `agent-improve/CLAUDE.md` v2.2.46 on 2026-09-26 (step 6.67).

- To amend a rule: the ruling goes to `ARCHITECTURE.md` (owning section, a §56 line, a
  version bump) — never to an archived document; the rule change to the file that holds
  it, alone, `docs(rules):`; bump this file's version; update the registry if the number
  is cited (§0.2); state the occurrence and escape causes in the commit body (§20). A new
  field on `SupervisorState`, `PhaseState` or `CoachingResponse` requires an amendment.
  An owned value goes nowhere — cite the owner. Never amend in passing.

Since 6.67 a rule that binds on code goes to the rule file whose `paths:` cover that
code (as §21 went to `.claude/rules/coaching-move.md`); CLAUDE.md holds only how to
work here. Check citations after any renumbering: `python .claude/hooks/verify_rule_citations.py`.
