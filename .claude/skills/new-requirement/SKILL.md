---
name: new-requirement
description: |
  Process 1 — run whenever the founder rules a new or changed requirement (business.md
  or platform.md). Carries the four steps in order: the entry with MoSCoW and Design,
  committed with a Ruling trailer; the ADR as Desktop gives it; the features with
  their failing tests, lane, depends_on, effort and proposed belt_impact and
  rework_risk; the re-rank and the report. Use when a prompt says "the founder ruled",
  "accepted", "amend T..", "add R..". Guard rules 18-20 refuse every shortcut.
disable-model-invocation: false
allowed-tools: Read, Grep, Glob, Bash, Edit, Write
version: "1.0"
---

# New or changed requirement — process 1

Brief Part F5 (founder, 2026-09-27); the order of work it feeds is ADR-0058. Every
requirement, whoever proposes it, runs this procedure:
**requirement → design decision (ADR if needed) → features → rank → build → ARCHITECTURE.md.**

Claude Code runs it only on a founder ruling. When Claude Code itself finds a requirement
wrong, missing or conflicting, it does NOT edit the file: it reports the finding to Desktop
as a proposed change (`.claude/rules/planning.md`).

## 1. The entry — one commit, with the ruling

- Business requirement (R, C, W, M ids): `agent-improve/docs/requirements/business.md`,
  heading line `**Rnn Title** · STATUS date · MoSCoW: … · Design: …`.
- Technical requirement (T ids): `agent-improve/docs/requirements/platform.md`, a table row
  `| Tnn | requirement | MoSCoW | Design | Proof |` (Proof is a test node id, or `none`).
- `MoSCoW:` — `Must | Should | Could | Won't-now` as ruled, or `?` until the founder ratifies it.
- `Design:` — `ADR-nnnn` when the change needs one (`.claude/rules/adr.md`), else `none`.
- An amendment changes the text in place; an id is permanent; a retired id stays, marked RETIRED.
- The commit carries `Ruling: <date> <what the founder ruled>` (guard rule 20).

## 2. The ADR, when `Design:` names one

- Place the ADR exactly as Desktop gives it: `agent-improve/docs/adr/NNNN-short-slug.md`,
  status PROPOSED or ACCEPTED as ruled. Never write or reword the decision yourself.
- The pre-commit hook regenerates the index in `docs/adr/README.md`.
- An ACCEPTED ADR is never edited; a changed decision is a new ADR that supersedes it (rule 21).

## 3. The features — in the SAME commit as an ACCEPTED requirement

Every RATIFIED or ACCEPTED requirement (a T id with proof `none`) has at least one feature
in `agent-improve/docs/define_features.json`; guard rule 18 refuses the commit otherwise.
For each feature:

| Field | Value |
|---|---|
| `id` | the next free `DEF-nnn` |
| `requirement` | the id |
| `test` | a failing stub in `backend/tests/test_define_e2e.py` (`_not_written(fid)`, which fails "not written yet"), or the real test |
| `lane` | A coaching · B gate · C screen and inputs · integrator |
| `depends_on` | from the code: the features whose behaviour it builds on |
| `effort` | S, M or L, from the code |
| `belt_impact` | proposed: dead_end · wrong_data · data_loss · degraded · none |
| `rework_risk` | proposed: high if it changes state, persistence, the gate or a schema; else low |
| `priority_override` | `null` — founder only |
| `phase`, `stage`, `layer` | where it sits on the board's value stream |

A feature whose requirement names a PROPOSED ADR can be added, but it cannot land until
the ADR is ACCEPTED (guard rule 19).

## 4. Re-rank and report

The pre-commit hook re-ranks (`tools/control_board/rank.py`). Report, as tables:
the requirement (id, text, MoSCoW, Design); the features (id, lane, effort, proposed
belt_impact and rework_risk, rank and its reason); the new top of each lane's queue
(`python tools/control_board/rank.py`).
