---
name: change-gate-schema
description: |
  Add, rename or retype a field on a phase output or on PhaseState. Use BEFORE
  touching a schema module — the change fans out to the gate document assembler, the
  cross-phase reference keys, the coached field order, the phase SKILL.md, the rubric
  and the tests, and every one of those is a place it can half-land. Carries the full
  fan-out and the amendment the change requires.
disable-model-invocation: false
allowed-tools: Read, Grep, Glob, Bash, Edit
version: "1.0"
---

# change-gate-schema

**A schema field is never one edit.** ARCHITECTURE.md §55.4 makes the schema
modules the owner of field names, counts and types — so the module changes
first, and everything else cites it.

## Before anything: is this an amendment?

**Yes, always, for a new field.** CLAUDE.md's *Amending the rules* step 3b: a new
field on `SupervisorState`, `PhaseState` or `CoachingResponse` requires an
amendment — record the ruling in ARCHITECTURE.md with a §56 changelog entry and
a version bump, in its own commit, before the code.

## The fan-out — check every row

| Where | What to change | How to find it |
|---|---|---|
| the schema module | the field itself: `core/state.py`, `core/substate.py`, or `phases/<phase>/schema.py` | the owner; change it first |
| the coached order | `DEFINE_FIELD_ORDER` and its siblings, which `field_index` walks | `grep -rn "_FIELD_ORDER" backend/` |
| gate assembly | the assembler reads named keys off `artifacts` | `backend/phases/gate_assembly.py` |
| validation | the per-phase validator asserts presence and tier | `backend/phases/<phase>/validate.py` |
| tier split | gate-required versus coached; Define is the one phase with no Tier 2 | `.claude/rules/gates.md` |
| cross-phase reads | a later phase reading this field by key | `grep -rn "the_field_name" backend/phases/` |
| the phase SKILL.md | a coached field needs its Explain/Show/Ask/Confirm block | `skills/dmaic-<phase>-phase/` |
| the coaching script | and its byte-identical twin | `skills/dmaic-<phase>-phase/coaching_script.md` |
| the rubric | a gate-required field usually earns a criterion | `grep -rn "PHASE_RUBRIC" backend/` |
| tests | schema, validator, gate document, and the count checks | `backend/tests/` |

## Typing law — read this before choosing a type

**Every captured field is a string or a dict. Never a numeric.** The computation
tools parse at the point of use. A float field is the defect §10.6 exists to
prevent, and `test_gate_documents.py` pins both the dict fields and their Tier-1
placement.

## After the change

```bash
python .claude/hooks/drift-check.py
python .claude/hooks/verify_built.py
cd agent-improve && .venv/Scripts/python.exe -m pytest backend/tests -q
```

**The drift check is the one that catches a half-landed change.** If a governing
document stated the old count, it now disagrees with the module and says so with
a file and a line.

## What half-landing looks like

`artifacts["computation_results"]` and `artifacts["phase_metrics"]` are read by
all five gate assemblers and **written by nothing**; `field_index` is set to 0
and never advanced. Each was a field that landed in the schema and not in the
path that fills it. The grader scans `computation_results` to answer whether a
hypothesis test was run — against an always-empty list the answer is always no,
so a gate document records that a project did no analysis whatever it did.
