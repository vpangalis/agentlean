# CLAUDE.md — Agent Improve
# Version 2.2.45 — September 2026
# Rules and pointers only. The why and the history: docs/_archive/CLAUDE_md_v2.2.44_2026-09-25.md

DMAIC coaching agent (LangGraph phase subgraphs, `create_agent` with a middleware coach
stack, Azure OpenAI / AI Search / Blob), mid-refactor v1 → v2.2. **These rules are the
constitution.** Quote the rule numbers you work under; if a rule is wrong, amend it
first, in its own commit — never violate it silently.

## Where and how to run

- `.claude/` sits one level up, so every `paths:` glob is `agent-improve/...` (§0.2). The
  OneDrive mirror does not carry `.claude/` — resolve through git (§0.32).
- **Use `agent-improve/.venv` only** (the repo-root venv is stale). `mypy .` is a
  measurement; the gate is rule 3's ratchet against `.claude/config/mypy-baseline.txt`.
- **`./start.ps1` HARD-RESETS TO `origin/main`, discarding uncommitted work — never run it.**

## Which document answers what

| Question | Document | Status |
|---|---|---|
| What is the rule? | this file + `.claude/rules/*.md` | **Binding** |
| How is Agent Improve shaped? | `ARCHITECTURE.md` — the design, §56 changelog, gap register, BUILT markers | **Binding** — target of every architecture citation |
| What do I build next, and is it done? | `docs/define_features.json` + `docs/test-results.json`; `docs/harness-progress.md` | **The plan** (step 6.66). Status comes only from tests |
| Step specs, Appendix D/F/G/H | `docs/REFACTORING_PROCEDURE.md` | **Reference only** — its tables still drive the board |
| Where did we leave off? | `docs/control-board.html`; `docs/CONTINUITY.md` | Generated every commit. Never hand-edit |
| Platform across all three agents | `../AGENTIC_ARCHITECTURE_REFERENCE.md` | Forward document — do not cite |

- Architecture citations resolve to `ARCHITECTURE.md` (before 2026-08-22 that path was
  the v2.2.16 document, commit `8533879`); §0.x other than §0.2/§0.24/§0.32 resolves in
  `docs/_archive/CLAUDE_md_S0_change_records.md`. **Never `@`-import these documents**;
  find the section in `docs/section-index.md` and read only its lines.
- Rule files (load by `paths:`; each ends with its **Never** list, the §14 bans): architecture §1 · module-layout §2
  · graph §3 · llm §4 · tools §5 · prompts §6, §15 · rag §7 · middleware §8 · gates §9 · state §10 · observability §11 · testing §12 · ui §13.

## Facts have one owner — cite it; `fact-ownership-guard.py` denies a restatement

| Class of fact | Owner |
|---|---|
| State schemas — names, counts, types | the state module |
| Gate document schemas, tier splits | the outputs module |
| Middleware stack and execution order | the agent factory and its ordering test |
| Tool inventory and per-phase binding | the tool registry |
| Search index schemas, and whether a field is live | the index definition, confirmed by query |
| Dependency versions | `requirements.txt` |
| Coaching script content | the phase directory under `skills/` |
| Banned patterns | `.claude/config/deprecated_patterns.yaml` |

### 0.2 — Rule numbers are load-bearing, across fourteen files

**Citations in `deprecated_patterns.yaml` must resolve; renumbering a cited rule
requires updating the registry in the same commit.** Moving a rule between files is
safe. Check: `python .claude/hooks/verify_rule_citations.py`.

## Always — regardless of what you are touching

- Never renumber a rule cited in `deprecated_patterns.yaml` without updating the
  registry in the same commit (§0.2)
- Never restate an owned fact in prose — cite its owner
- The git working tree at HEAD is the only source of truth. A claim about a file's
  content is made against that file at its repo path, read at the time of the claim —
  never a cached copy, a snapshot, a draft, a scratchpad, or a synced mirror (§0.32)
- Scratch lives outside the tree, is never committed, and is never evidence. If a
  scratch artifact matters it becomes a tracked file with a step number (§0.32)
- A new file in the tree needs a step number or a gap number (§0.32)

### 0.24 — PREFER FRAMEWORK PRIMITIVES — a standing RULE

> **Before hand-rolling retry, tracing/metrics, state persistence, checkpointing, or
> the agent loop, confirm LangChain / LangGraph / LangSmith does not already provide
> it. Reinventing a framework primitive is a violation.**

| If you are about to build… | Use instead | Specified in |
|---|---|---|
| A retry loop around a model call | **`ModelRetryMiddleware(max_retries=2)`**; `ToolRetryMiddleware` for tool calls | ARCHITECTURE.md §19.4 · §8.7 |
| Tracing, metrics, or an LLM callback layer | **LangSmith**, plus **`@traceable`** on plain functions between nodes | ARCHITECTURE.md §51 · §11.2 |
| Saving or restoring graph/phase state | **The checkpointer** (per `thread_id`) and **the store**, on the PARENT graph only | ARCHITECTURE.md §16 · §1.7, §10.2 |
| An agent loop — model → tools → model | **`create_agent`** with the middleware stack | ARCHITECTURE.md §18 · §4.4, §8.1 |

**Confirm, not never build**: implementing `BaseCheckpointSaver` is using the primitive.
Record a framework gap via `/verify-current-version`, never memory.

### 0.32 — THE TREE AT HEAD IS THE ONLY SOURCE OF TRUTH
> **A claim about a file is made against that file, at its repo path, read at the time
> of the claim.** Not a copy read earlier, a draft, a scratchpad summary, or a mirror.
> The test is a git command, never a directory listing.

## How to deliver work

- A decision or an explanation is a diagram or a table carrying the full detail —
  never prose threaded with section numbers (§19.1)
- Never render a bare number or code in anything a human reads: "6.20 — the write
  paths", never "6.20" (§19.2)
- Every **real defect** — a fix of wrong behaviour, or a `Gap:` trailer — is an 8D worked
  before the fix (§20; the `eight-d` skill). Each occurrence cause carries an escape cause,
  each containment its removal condition; an empty discipline is `NONE — <reason>` (§20.2)
- A claim about what the code does quotes the lines, with file and line number; a claim
  of absence carries the command and its output (§20.5.1)

## §21 — The coaching move is decided in code (founder 2026-09-25; ARCHITECTURE.md v1.75; binds all phases and agents)

- **Code decides this turn's move from the field's status — never a model.** Not
  yet taught → teach (explain, show, ask); answered, insufficient → challenge
  (say what is missing); answered, sufficient → read back (the Belt's own words,
  then *"is this right?"*); confirmed by the Belt → store and advance.
- **A model is used only to judge whether an answer is sufficient, and to write
  the coach's words.**
- **A value is stored only after the Belt confirms it, in the Belt's words.** A
  tidied version may be proposed in the read-back and is stored only if the Belt
  confirms it.
- **The coach's input is assembled by code each turn in labelled sections, one
  job each:** coaching rules (how to behave) · phase script (what to teach) ·
  state (facts) · this turn's move (authoritative) · last turn's quality
  feedback · the conversation.
- **Coaching rules and phase scripts contain no move-sequencing** — no *"then
  advance"*, no *"confirm and move on"*, no *"one move, then stop"*.
- **Feedback to the coach is never presented as a message from the Belt.**
- **Every step that touches coaching behaviour carries a repeated-run
  consistency test in its Done-when** — the same turn, run five times, makes the
  same move.

## §22 — Speed without losing quality (founder 2026-09-25, 6.65/6.66: keep every check; remove only repeats)

- **(a) Tests.** The full suite runs **once per commit**, in the pre-commit hook, in
  parallel. **The pre-flight runs before every commit attempt** (`.claude/hooks/preflight.py`,
  fired by a PreToolUse hook on `git commit`). While working, run area tests serial
  (`-n 0`). Never run the full suite by hand.
- **(b) Reading.** Never read `ARCHITECTURE.md` or the procedure whole. **(c) Paperwork.**
  An 8D only for a real defect; the step card and its Done-when are the record.
- **(d) Live model runs.** 3 per situation while building; 5 only in a final proof;
  diagnosis calls count toward any cap. **(e) Stops.** Only when the Belt's experience
  changes or a founder decision is needed. **(f) Reports.** One table plus decisions.
- **(g) Timing.** `.claude/logs/timing.jsonl`; one `prompt` record per prompt, each
  category VERIFIED or ASSUMED; every report ends with it as one line.
- **(h) REPLACE, DON'T APPEND.** A governing document holds the current state: change a
  statement in place; history goes to `docs/_archive/`. Rule 12 of the commit guard
  refuses growth past `.claude/config/size-budget.json`.

## Versions, migration, amending the rules

- `requirements.txt` owns the pins; **the floor is the rule**: `langgraph >= 1.2.6`,
  `langchain-core >= 1.6.0`. Presence of `langchain-classic` / `langgraph-prebuilt` is
  not permission to import them. `/verify-current-version` against the **installed** version.
- No v1-style code may be added; a file is migrated when rewritten under v2.2 rules and
  committed as `refactor(arch-v2):`.
- To amend a rule: the ruling goes to `ARCHITECTURE.md` (owning section, a §56 line, a
  version bump); the rule change to the file that holds it, alone, `docs(rules):`; bump
  this file's version; update the registry if the number is cited (§0.2). A new field on
  `SupervisorState`, `PhaseState` or `CoachingResponse` requires an amendment. An owned
  value goes nowhere — cite the owner. Never amend in passing.
