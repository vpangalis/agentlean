---
name: reconcile-docs
description: |
  Run the drift and marker checks across the governing documents and work each
  finding as an 8D. Use monthly, after any schema change, after a dependency upgrade,
  and whenever two documents are suspected of disagreeing. Reports what disagrees with
  the code that owns it — and treats each disagreement as a defect with an escape
  cause, not a typo to correct quietly.
disable-model-invocation: false
allowed-tools: Read, Grep, Glob, Bash
version: "1.0"
---

# reconcile-docs

## Run the checks

```bash
python .claude/hooks/drift-check.py            # owned facts vs the documents
python .claude/hooks/verify_built.py           # BUILT markers vs the tree
python .claude/hooks/verify_rule_triggers.py   # paths: globs that match nothing
cd agent-improve && .venv/Scripts/python.exe -m pytest backend/tests -q
```

Each exits non-zero on a real disagreement and names the file and line.

## Then work each finding as an 8D — invoke `eight-d`

**A document that disagrees with the code is a defect, not a typo.** Correcting
the number and moving on loses the escape cause, which is the half that stops
the class. Every reconciliation finding has the same shape and the D4 ESCAPE is
almost always *"nothing compares this document to its owner"*.

Worked precedents, all from the September pass:

| Finding | Occurrence | Escape |
|---|---|---|
| §8.1 stated the middleware order backwards | one missing distinction — the list is nesting order, the positions are execution order | the pinning test replaced `create_agent` and could not observe execution |
| §7.3 tabled the evidence index as unbuilt | the section duplicated a schema its own preamble forbids it to hold | nothing compares a transcribed schema to the live index |
| §16.1 called the upgrade a BLOCKER | the document held an `Installed` column — a copy of a fact `pip` owns | the one mechanism reading both asserts nothing |

## What to fix, and what to leave

**Fix** a live section that disagrees with its owner. **Leave** a dated record —
a changelog entry, an archived document, a `SUPERSEDED` row. They were true when
written, and that is what a change record is. The drift check already skips
them; if you find yourself editing one, stop.

**Prefer deleting the copy to correcting it.** §7.3's tables were removed rather
than fixed, because correcting a transcription rebuilds the thing that went
stale. Cite the owner instead — ARCHITECTURE.md §55.4 lists the five ratified.

## Before you finish

Re-run the checks. Then ask what would have caught this earlier, and whether
that check exists. If it does not, register a gap with a step number — **a gap
with no step number does not render on the board and is not scheduled by
anything.**
