# CLAUDE.md — Agent Improve
# Version 2.2.43 — September 2026
# 2026 LangChain/LangGraph standards. Authoritative. Never bypass.

DMAIC coaching agent: LangGraph phase subgraphs, LangChain `create_agent` with a
custom middleware coach stack, Azure OpenAI / AI Search / Blob. One of the three
AgentLean agents (Resolve · Improve · Flow). Mid-refactor from v1 to v2.2.

**These rules are the constitution.** Quote the rule numbers you are working
under at the top of every implementation prompt. If a rule blocks the request,
the rule wins. If a rule is wrong, amend it first, in its own commit — never
violate it silently.

**Violations of this constitution cost weeks of rework. We have proven this
twice with Agent Resolve and once with Agent Improve. There is no third time.**

## Where this is

```
C:\Users\mavep\OneDrive - Vassilis Pangalis Valuesims\_DEVELOPMENT\AgentLean\agent-improve
```

The repository root is one level up; `.claude/` sits **there**, not here, which
is why every `paths:` glob is written `agent-improve/...` (§0.2).

**It is recorded here and not in `CONTINUITY.md`** — that file is regenerated on
every commit and hand edits are overwritten. **The tree lives inside OneDrive,
and the mirror does not carry `.claude/`**: resolve through git, never a
directory listing (§0.32).

## Commands

```powershell
.venv\Scripts\Activate.ps1         # Windows venv — there is no bin/activate
pip install -r requirements.txt
pytest                             # must pass before any commit; the suite owns its count
mypy .                             # reports the WHOLE tree, v1 debt included — see below
./start.ps1                        # local run — SEE THE WARNING BELOW
```

**`./start.ps1` HARD-RESETS TO `origin/main` AND DISCARDS UNCOMMITTED WORK.** Its
own header says so. Commit or stash first; it is not a plain "run the app".

**`mypy .` is NOT the gate, and a clean run is not what you are aiming for.** It
type-checks the whole tree and reports the v1 debt with it. **The gate is a
RATCHET**: the commit hook runs mypy over the CHANGED files only and blocks
errors absent from `.claude/config/mypy-baseline.txt`. Read a bare `mypy .`
count as a measurement, never as a pass/fail — a first run showing dozens of
errors is the expected state, not a broken checkout.

**Use `agent-improve/.venv`, never the repo-root venv.** The root one is stale.
Probing the wrong one is what put a false dependency blocker into two governing
documents; `session-start-context.py` pins the right interpreter and prints the
resolved versions at session start.

## Layout

| Path | What it is |
|---|---|
| `backend/` | The agent — graph, nodes, middleware, state, tools, knowledge. **Owns the schema facts** |
| `ui/` | Belt-facing UI |
| `skills/` | **Agent Improve's own DMAIC content — product, not Claude Code skills.** Each phase directory holds its SKILL.md and its coaching script. Do not move into `.claude/` |
| `data/` `scripts/` `diagrams/` | Corpora, one-off tooling, generated diagrams |
| `docs/` | Reference. Never auto-loaded — read targeted |
| `.claude/rules/` | The numbered rules, loaded when you open matching files |

## Which document answers what

| Question | Document | Status |
|---|---|---|
| What is the rule? | this file + `.claude/rules/*.md` | **Binding** |
| How is Agent Improve shaped, and why? | `ARCHITECTURE.md` — the design, the §56 changelog, the gap register, the BUILT markers | **Binding — and the target of every architecture citation** |
| What do I build next, and how is it verified? | `docs/REFACTORING_PROCEDURE.md` — step specs, Appendix A traceability, Appendix D `Seq` ordering | **Binding** |
| How is the platform shaped across all three agents? | `../AGENTIC_ARCHITECTURE_REFERENCE.md` | **A FORWARD DOCUMENT.** To be authored FROM Agent Improve once Improve is proven. **Not a source of truth today** — do not cite it, and do not treat it as owing a back-port |
| Where did we leave off? | `docs/control-board.html` — **the only progress view** (founder, 2026-09-25); `docs/CONTINUITY.md` carries its headline | **Generated every commit from `tools/control_board/progress.py`. Never hand-edit** |
| Historical rulings | `docs/_archive/` | Closed. Rulings from 2026-09-10 onward live in ARCHITECTURE.md and in commit bodies |

**Architecture citations resolve to `ARCHITECTURE.md`.** Rule numbers of the form
§10.5 are the rules' own numbering, in this file and in `.claude/rules/`.

> **Resolving a pre-2026-08-22 `ARCHITECTURE.md §X` citation** — in a code
> comment, a SKILL.md or an older prompt. Before 2026-08-22 that path held the
> v2.2.16 design document with its own numbering, §1–§18. It now holds Agent
> Improve's architecture with §1–§56 numbering, so the same string means two
> different things depending on when it was written. The v2.2.16 original is at
> commit `8533879`; its §17 and §18 registers are at
> `docs/_archive/ARCHITECTURE_v2216_registers.md`.

> **A `§0.x` citation resolves in one of two places.** §0.2 and §0.24 are below.
> Anything else — §0.10, §0.13, §0.16, §0.17, §0.18, §0.20, §0.28–§0.31 are all
> still cited from the rule files — resolves in
> `docs/_archive/CLAUDE_md_S0_change_records.md`, where §0's 27 dated change
> records moved on 2026-09-13.

ARCHITECTURE.md is large: search for the section, read that region. **Never
`@`-import any document in this table** — imports load at launch and would put
the whole set in every session.

## How the rules work

The rules live in `.claude/rules/`, one file per domain, loaded when you open a
file the rule covers. **Rule numbers are unchanged from v2.2.37 and are
load-bearing** — `.claude/config/deprecated_patterns.yaml` cites them back to you
when the drift hook fires.

| Rule file | Covers | Loads on |
|---|---|---|
| `architecture.md` | §1 — the principles the rest rest on | `backend/core/graph.py`, `backend/core/checkpointer.py`, `backend/core/store.py`, `backend/core/tracing.py`, `backend/phases/subgraph_common.py` |
| `module-layout.md` | §2 — where classes may live | the 24 files §2 names |
| `graph.md` | §3 — graph, nodes, routing, reliability | `backend/core/graph.py`, `backend/phases/**` |
| `llm.md` | §4 — model calls, structured output, fallback | `backend/core/llm.py`, `backend/phases/**`, `backend/upload/**` |
| `tools.md` | §5 — universal and per-phase computation tools | `backend/knowledge/tools.py`, `backend/knowledge/computation.py`, `backend/knowledge/tool_args.py` |
| `prompts.md` | §6, §15 — prompt construction and size | `backend/core/prompts.py`, `skills/**` |
| `rag.md` | §7 — retrieval, index schemas, failure semantics | `backend/knowledge/**`, `scripts/ingest_knowledge.py` |
| `middleware.md` | §8 — the coach middleware stack and its order | `backend/middleware/**`, `backend/phases/nodes_common.py` |
| `gates.md` | §9 — four-layer validation, nine-step HITL, tiers | `backend/validation/**`, `backend/phases/gate_assembly.py`, `backend/phases/gate_registry.py`, `backend/phases/*/validate.py`, `backend/phases/*/schema.py` |
| `state.md` | §10 — state schemas, store, gate documents | `backend/core/state.py`, `backend/core/substate.py`, `backend/core/store.py`, `backend/storage/**`, `backend/phases/mappers_common.py`, `backend/phases/*/mappers.py` |
| `observability.md` | §11 — LangSmith tracing, structured logging | `backend/core/tracing.py`, `backend/core/logging_setup.py`, `backend/core/metrics.py` |
| `testing.md` | §12 — eval suite, regression threshold, errors | `backend/tests/**` |
| `ui.md` | §13 — team-facing language, citations, gate screen | `ui/**`, `backend/gateway/**` |

Paths are repo-root-relative — `.claude/` sits above `agent-improve/`, so a glob
of `backend/**` matches nothing and **fails silently: the rule simply never
loads.** Each rule file ends with its own **Never** list — the §14 bans that
belong to that domain, each landing in exactly one file.

## Facts have one owner

A count, a field name, a schema shape or a version pin is stated in exactly one
place and cited everywhere else. Restating an owned fact in prose creates a
second copy that can drift, and every contradiction found in the September audit
was of that kind.

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

`fact-ownership-guard.py` denies an edit that writes an owned value into prose.
Cite the owner instead.

### 0.2 — Rule numbers are load-bearing, across fourteen files

`.claude/config/deprecated_patterns.yaml` cites rule numbers in the messages the
drift hook feeds back when it denies a write. **Those citations must resolve.
Renumbering a cited rule requires updating the registry in the same commit.** A
hook that cites a non-existent rule is worse than no hook. The registry owns the
pattern-to-rule mapping; it is not restated here.

**A rule number now resolves in this file OR in one of thirteen files under
`.claude/rules/`**, and the invariant spans both. Moving a rule between files is
safe — the number travels with it and the citation still resolves. **Renumbering
is what breaks silently**, and there are now fourteen places for the break to
hide instead of one:

```bash
python .claude/hooks/verify_rule_citations.py
```

It reads the registry's `message:` fields — the text actually quoted back when a
write is denied — and resolves each citation in its own namespace: `CLAUDE.md §x`
against the root and the rule files, `Reference §x` against ARCHITECTURE.md,
`EDUCATIONAL §x` against the archived review. **A §-number in a YAML comment is
prose about history and is not checked**; a grep over the whole file reports it
as dangling and is the wrong tool here.

**This fired for real on 2026-09-13.** Retiring §18.1 left the registry citing a
rule that no longer existed; the sweep caught it in the same commit, which is
what this rule is for. Full procedure: ARCHITECTURE.md §56.

## Always — regardless of what you are touching

*Five. Every other ban from §14 lives in the rule file for the code it governs,
which is where it loads.*

- Never renumber a rule cited in `deprecated_patterns.yaml` without updating the
  registry in the same commit (§0.2)
- Never restate an owned fact in prose — cite its owner
- The git working tree at HEAD is the only source of truth. A claim about a
  file's content is made against that file at its repo path, read at the time of
  the claim — never a cached copy, a snapshot, a draft, a scratchpad, or a
  synced mirror (§0.32)
- Scratch lives outside the tree, is never committed, and is never evidence. If
  a scratch artifact matters it becomes a tracked file with a step number (§0.32)
- A new file in the tree needs a step number or a gap number (§0.32)

### 0.24 — PREFER FRAMEWORK PRIMITIVES — a standing RULE, not a change record

*Kept in the root with its number because it is constitutional — it governs
what may be BUILT — and because `deprecated_patterns.yaml` cites §0.24 three
times, in the denial messages for `pattern-9`, `pattern-10` and `pattern-11`.
Added 2026-08-31 at 2.2.30; the rest of §0 moved to `docs/_archive/` on
2026-09-13.*

> **Before hand-rolling retry, tracing/metrics, state persistence,
> checkpointing, or the agent loop, confirm LangChain / LangGraph / LangSmith
> does not already provide it. Reinventing a framework primitive is a
> violation.**

| If you are about to build… | Use instead | Specified in |
|---|---|---|
| A retry loop around a model call | **`ModelRetryMiddleware(max_retries=2)`** on `create_agent` — and `ToolRetryMiddleware` for tool calls; they are different middlewares, not synonyms | ARCHITECTURE.md **§19.4** · §8.7 |
| Tracing, metrics, or a callback layer for LLM calls | **LangSmith.** `LANGCHAIN_TRACING_V2=true`, plus **`@traceable`** on the plain Python functions between nodes — runnables and graph nodes are traced already | ARCHITECTURE.md **§51** · §11.2 |
| Saving or restoring graph/phase state | **The LangGraph checkpointer** (per `thread_id`), and **the store** for cross-phase artifacts. Both attach to the PARENT graph only | ARCHITECTURE.md **§16** · §1.7, §10.2 |
| An agent loop — model → tools → model | **`create_agent`**, with the eight-middleware stack | ARCHITECTURE.md **§18** · §4.4, §8.1 |

**Why this is a rule and not advice.** Three of the costliest corrections in
this file are the same mistake: code written against a remembered idea of a
library rather than the library. §0.10's `retries=` vs **`max_retries=`** sat
inside the canonical middleware block — the one an implementer copies verbatim
— from adoption until 2026-08-21. §0.13's `ContradictionDetectionMiddleware`
was adopted as a named pattern and could not do its job in three independent
ways. §0.16's `remaining_steps` was read off a schema that never declared it,
so a five-hop cap returned **10 forever** and never fired. **A hand-rolled
primitive is that failure with no upstream to correct it**: the framework's own
version gets fixed by its maintainers and covered by its tests, and yours does
not.

**This rule adds no new design.** It generalises four decisions already
ratified — §8.7 ("Hand-writing retry plumbing is BANNED"), §11.2 (`@traceable`
required), §1.7 (phased checkpointer/store) and §4.4 (`create_agent`) — into
the question to ask *before* writing, rather than four prohibitions discovered
after. **It restates no design**: every § cited above already says what this
rule says, and this rule is the single place that says it once.

**It is enforced, not just stated.** Three registry patterns block the write:
`pattern-9-hand-rolled-llm-retry`, `pattern-10-custom-llm-tracing`,
`pattern-11-manual-state-persistence` — the registry is the owner of that
mapping and carries it. They match a SHAPE
rather than a name, because the drift here is code that should never have been
written at all and so has no deprecated identifier to grep for. **Verified
2026-08-31: zero matches across all 57 files in `agent-improve/backend/`**, so
none of the three landed as a pre-existing violation.

> **The rule is "confirm", not "never build".** A framework gap is a real
> answer — `AzureBlobCheckpointSaver` exists because LangGraph ships no Azure
> Blob saver, and it is correct precisely because it **implements
> `BaseCheckpointSaver`** rather than replacing it. Supplying a backend to a
> framework primitive is using the primitive. Writing your own alongside it is
> the violation. When the check says "the framework does not have this",
> **record that finding** — `/verify-current-version` against the live package
> index, per §16.3, not against memory or a document.

### 0.32 — THE TREE AT HEAD IS THE ONLY SOURCE OF TRUTH

*Constitutional, and kept in the root for §0.24's reason: it governs what may be
CLAIMED and what may be COMMITTED, rather than one domain's code. Ratified
2026-09-13; the ruling is ARCHITECTURE.md §56.3.*

> **A claim about a file is made against that file, at its repo path, read at
> the time of the claim.** Not a copy read earlier in the session, not a draft
> of it, not a scratchpad summary of it, and not a mirror that syncs it.

**The mirror is the sharpest case, because this tree lives inside one.** A
synced copy can be complete, current-looking, and still not hold what git holds:
`.claude/` does not appear in the OneDrive mirror at all, so from a seat that
trusts the mirror the entire governance layer — every rule file, every hook,
every skill — reads as absent. **A source of truth you can be wrong about
without noticing is not one.** The test is a git command and never a directory
listing: a file is in the tree, or `git ls-files` does not name it.

**Clauses two and three are enforced, not merely stated.** Two rules of the
commit-msg guard refuse the commit; `.claude/hooks/commit-msg-refactor-guard.py`
owns the patterns and the resolution and its docstring carries both. One blocks
a staged scratch path **by name**. The other blocks a path new to the tree with
no step and no gap behind it — declared in the spine subject or in a `Step:` /
`Gap:` trailer, and resolved against Appendix D or §66's register, **both read
from the index**, so a gap registered in the same commit counts.

**Both are ratchets rather than walls**, on rule 3's argument: they read only
what is NEW to the tree, so paths already tracked stay visible and countable
instead of blocking every commit that touches one.

> **Neither rule can check clause one, and that is a limit, not an oversight.**
> A gate sees the index; it never sees a sentence. A claim sourced from a stale
> copy passes every hook in this repository and is caught only by the reader who
> resolves the citation — which is why §20.5.1 already requires the file, the
> line number, and the command behind a claim of absence. **G-57 carries the
> other half**: these two rules are demonstrated and untested, where the 8D rule
> carries a test suite written against exactly this failure mode — a message
> check that stops matching fails SILENTLY, by letting commits through.

## How to deliver work

- A decision or an explanation is a diagram or a table carrying the full detail —
  never prose threaded with section numbers (§19.1)
- Never render a bare number or a bare code in anything a human reads:
  "6.20 — the write paths", never "6.20" (§19.2)
- Every fix is an 8D, worked **before** the fix is proposed — defects,
  modifications and adaptations alike (§20)
- Every occurrence cause carries an escape cause: *"why did nothing detect this"*
  is a separate answer (§20.2)
- Every interim containment carries its removal condition (§20.2)
- An empty discipline is a finding, written `NONE — <reason>` (§20.2)
- A claim about what the code does quotes the lines it rests on, with file and
  line number; a claim of absence carries the command and its output (§20.5.1)

## §21 — The coaching move is decided in code

*Founder ruling 2026-09-25. Canonical: ARCHITECTURE.md v1.75 (§17, §19.1, §20,
§22, §32, §43). **Binds ALL phases and ALL agents** — the platform reference's
back-port is owed.*

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

> **The nine disciplines and the six the gate requires are the `eight-d` skill.**
> `.claude/skills/eight-d/` carries the D0–D8 table, the enforcement contract
> and the worked example. It loads when you invoke it, which is when you are
> working a defect — the rules above bind always and are seven lines; the
> reference is thirty and was carried in every session that never opened it.

## Versions

Pinned in `requirements.txt` — **that file is the owner; this section states only
the rule.**

**The floor is the rule; the pins are a snapshot.**

| Floor | Why it is a floor |
|---|---|
| `langgraph >= 1.2.6` | 1.2.6 (2026-06-18) carries *"nested subgraph inherits parent `checkpoint_ns` (regression in 1.2.3)"* — the fix the subgraph design depends on. Node-level `TimeoutPolicy` and `error_handler` need 1.2+ |
| `langchain-core >= 1.6.0` | Required by `langchain` 1.x as resolved |

`langchain-classic` retains legacy classes we do not use: **presence is not
permission.** `langgraph-prebuilt` is present as a transitive dependency — its
presence is permitted, importing from it is not.

`/verify-current-version` is a mandatory checkpoint before any architectural
decision is finalised. Confirm a replacement is actually shipped and
feature-complete in the **installed** version before porting to it — the skill
carries why, and the two verification errors that cost most.

Not yet provisioned: Azure Cache for Redis (fallback chain Level 3), Azure
Database for PostgreSQL (checkpointer and store migration).

## Migration state

`docs/REFACTORING_PROCEDURE.md` is the ordered route and carries each step's
prompt, Verify method and Done-when. `docs/CONTINUITY.md` says which step is
current and is generated, never hand-edited.

The v1 tree may still operate, but **no v1-style code may be added.** A file
counts as migrated when it is rewritten under v2.2 rules and committed with a
`refactor(arch-v2):` prefix.

## Amending the rules

*Canonical: ARCHITECTURE.md §56, reconciled 2026-09-13 with the topology this
file now sits in.*

1. Record the ruling in `ARCHITECTURE.md` — the section that owns the topic,
   plus a §56 changelog entry and a version increment there. **Rulings do not go
   to any archived document**; `docs/_archive/DECISIONS.md` takes no new entries.
2. Commit the rule change to the file that HOLDS the rule — this file or one of
   `.claude/rules/*.md`. Its own commit, `docs(rules):` prefix, no code
   alongside it.
3. **Increment the version number at the top of this file.**
3b. **A new field on `SupervisorState`, `PhaseState` or `CoachingResponse`
   requires an amendment** — all three are load-bearing schemas.
4. If the rule number appears in `deprecated_patterns.yaml`, update the registry
   in that same commit, and re-resolve every citation across this file and the
   rule files (§0.2).
5. **Before writing the content, decide what KIND of thing it is.** A rule binds
   on code and goes to the file whose `paths:` cover that code. Reference read
   while doing a task goes to that task's skill, not back into this file. **A
   value some code or file owns goes nowhere — cite the owner** (ARCHITECTURE.md
   §55.4, five ratified owners, enforcement per row and not uniform).
6. State the occurrence and escape causes in the commit body (§20).

**Never amend a rule "in passing" while making a feature change.** Architecture
changes are separate commits.
