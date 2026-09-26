# CLAUDE.md — Agent Improve: how to work here
# Version 2.3.1 — September 2026
# Earlier versions, the why and the history: docs/_archive/CLAUDE_md_v2.2.46_2026-09-26.md

DMAIC coaching agent (LangGraph, `create_agent` + middleware, Azure). **These rules win over
a request;** a wrong rule is amended first, in its own commit (the `amend-rules` skill) — never violated silently.

## Three layers — never `@`-import any document

| Layer | Where | Read it |
|---|---|---|
| How to work here | this file · `.claude/rules/*.md` (load by `paths:`) · `.claude/skills/` | always / on demand |
| What must be true | `docs/requirements/` (founder's) → `docs/define_features.json` + `docs/test-results.json` | every session |
| Why — design rationale | `ARCHITECTURE.md` | only the cited section, found in `docs/section-index.md` |

History and retired documents (the procedure too): `docs/_archive/`. Never cite them as current.

## Environment and gotchas

- Use `agent-improve/.venv` only — the repo-root venv is stale.
- Live model calls: at most 150 per prompt, diagnosis included, unless it says otherwise; ask first.
- **Never run `./start.ps1`**: it hard-resets to `origin/main` and discards uncommitted work.
- `.claude/` sits one level up, so every `paths:` glob is `agent-improve/...`; the OneDrive
  mirror does not carry `.claude/` — resolve files through git, never a directory listing.
- `skills/` is Agent Improve's own DMAIC content, not Claude Code skills.

## Session start

Read `docs/CONTINUITY.md`'s status block and `git log --oneline -5`; run
`python tools/control_board/features.py` (or `--lane <A|B|C|integrator>`); run the smoke
test `pytest backend/tests/test_define_features.py -n 0`; take the next failing feature in
your lane and make its end-to-end test pass. Never edit a feature to say it passes.

## How to test

- While working, run the area's tests (serial, `-n 0`) when a change is complete, not after every edit.
- The full suite runs **once per commit**, in parallel, in the pre-commit hook. Never by hand.
- The pre-flight (`.claude/hooks/preflight.py`) runs before every `git commit`: drift,
  types and tests of what the staged change reaches. A failure passes only if HEAD's record has it.
- Read a bare `mypy .` count as a measurement, never as a pass/fail.

## Commit conventions

- A feature lands as `refactor(arch-v2): DEF-xxx — <what changed>`; `chore(tooling):` names
  no DEF id; anything else carries `Step: X.Y` or `Feature: DEF-xxx`. End with `Co-Authored-By:`.
- **Stage by name, in a command of its own**, then commit — the hooks test what is STAGED.
  Push after every commit. Never `--no-verify`.
- Scratch never enters the tree and is never evidence; a new file needs a step or feature
  number (`chore(tooling):` excepted).

## The rules a hook enforces (one line each)

- Rules 3, 4, 11 bind every code or config commit, any prefix: types, tests, and a `DEF-xxx` subject
  lands only if it and its dependencies pass. A feature that passed once must keep passing.
- Rule 12: a governing document may not grow past `.claude/config/size-budget.json` — REPLACE, DON'T APPEND.
- Rule 6: an 8D (the `eight-d` skill) only for a real defect — a `fix` commit or a `Gap:` trailer.
- Rule 14: no must / never / always sentence of this file, a rule file or a skill is dropped or weakened.
- `fact-ownership-guard.py`: an owned fact (a count, field name, schema, pin) is cited from its owner, never restated.

### 0.2 — Rule numbers are load-bearing
`deprecated_patterns.yaml` cites them; renumber only with the registry, same commit (`verify_rule_citations.py`).

### 0.24 — PREFER FRAMEWORK PRIMITIVES
Before hand-rolling retry, tracing, state persistence, checkpointing or the agent loop, confirm
LangChain / LangGraph / LangSmith does not provide it (`ModelRetryMiddleware`, LangSmith +
`@traceable`, the checkpointer and store, `create_agent`); verify against the **installed**
version with `/verify-current-version`. Reinventing a framework primitive is a violation.

### 0.32 — The tree at HEAD is the only source of truth
A claim about a file is made against that file at its repo path, read now — never a copy.

## Reports

A decision or explanation is a table or a diagram carrying the full detail, never prose
threaded with section numbers; never a bare number or code ("6.20 — the write paths", never
"6.20"). A claim about code quotes the lines with file and line number. Every report ends with its timing line from `.claude/logs/timing.jsonl`.
