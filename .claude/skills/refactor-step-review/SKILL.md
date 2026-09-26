---
name: refactor-step-review
description: |
  Review a Claude Code report, a proposed approach, or a finished step against the
  ratified architecture, the rejected designs, and the installed framework — before
  it is accepted. Use when a session reports a step complete, when a proposal cites
  a section number, or when a report asserts what the code does. Checks that every
  citation resolves, that no claim about code arrives without the code, and that a
  rejected design is not being re-proposed under a new name.
disable-model-invocation: false
allowed-tools: Read, Grep, Glob, Bash
version: "1.0"
---

# refactor-step-review

Review against three things, in this order. The first is cheapest and catches
the most.

## 1 — Do the citations resolve?

A §-number is a literal string and **nothing checks them by default**. Two wrong
citations shipped inside §30 alone, in a document whose §55.1 rule is that every
reference resolves to what it names.

```bash
# every §x.y a report cites, against the root file and the rule files
grep -oE '§[0-9]+(\.[0-9]+)*' <report> | sort -u
grep -nE '^#+ (0\.)?[0-9]+' agent-improve/CLAUDE.md .claude/rules/*.md
```

Then the registry, which is the one that bites:

```bash
python .claude/hooks/preflight.py            # drift, types, tests of what changed (verify_built.py retired at 6.67)
python .claude/hooks/verify_rule_triggers.py  # every paths: glob matches something
python .claude/hooks/drift-check.py           # owned facts vs the documents
```

## 2 — Does a claim about code carry the code?

CLAUDE.md, "Reports" (§20.5 until 6.67) — a claim about what the code does quotes the lines it rests on,
with file and line number; **a claim of ABSENCE carries the command and its
output.** A report saying "no test asserts this" without the grep is not a
finding, it is a belief.

**Check the check.** A test that has only ever been seen passing is not evidence
it can fail. `test_the_declared_middleware_list_is_the_ratified_layering` encoded
the right rule for months under a fixture that replaced `create_agent`, so it
asserted `reversed(declared)` and could not fail — registered as **G-52**. Ask
of any check offered as proof: *what edit makes this go red?*

## 3 — Is a rejected design being re-proposed?

ARCHITECTURE.md records what was considered and refused, and a rejected design
returns under a new name. Search the register and the changelog before accepting:

```bash
grep -n "RULED\|rejected\|NOT chosen\|deliberately NOT" agent-improve/ARCHITECTURE.md
```

Known standing refusals: no MCP (§29.1); no `deepagents` while pre-1.0; no
`create_react_agent`; no hand-rolled retry, tracing, checkpointing or agent loop
(§0.24); no `MultiQueryRetriever` / `EnsembleRetriever`; no per-phase state
classes.

## What to report

Findings as a table, never prose threaded with section numbers (§19.1), and
never a bare code — `G-52 — the ordering test cannot observe order`, not `G-52`
(§19.2). If the step is a fix, its body answers the six 8D labels or the commit
is blocked; invoke `eight-d`.

## The failure this skill is for

A correct finding that does not reach a decision has not been delivered. A wrong
finding gets corrected; an unreadable one gets filed.
