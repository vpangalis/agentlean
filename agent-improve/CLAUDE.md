# CLAUDE.md — Agent Improve
# Version 2.2.38 — September 2026
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

## Commands

```powershell
.venv\Scripts\Activate.ps1         # Windows venv — there is no bin/activate
pip install -r requirements.txt
pytest                             # 893 tests; must pass before any commit
mypy .                             # mypy.ini; the commit hook gates on this
./start.ps1                        # local run — SEE THE WARNING BELOW
```

**`./start.ps1` HARD-RESETS TO `origin/main` AND DISCARDS UNCOMMITTED WORK.** Its
own header says so. Commit or stash first; it is not a plain "run the app".

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
| Where did we leave off? | `docs/CONTINUITY.md`, `docs/board.html` | **Generated every commit. Never hand-edit** |
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

### 0.2 — Rule numbers are load-bearing

`.claude/config/deprecated_patterns.yaml` cites rule numbers in the messages the
drift hook feeds back. **Those citations must resolve. Renumbering a cited rule
requires updating the registry in the same commit.** A hook that cites a
non-existent rule is worse than no hook. The registry owns the pattern-to-rule
mapping; it is not restated here.

## Always — regardless of what you are touching

*Only two. Every other ban from §14 lives in the rule file for the code it
governs, which is where it loads.*

- Never renumber a rule cited in `deprecated_patterns.yaml` without updating the
  registry in the same commit (§0.2)
- Never restate an owned fact in prose — cite its owner

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

### 20.1 — The nine disciplines

> **MOVES TO THE `eight-d` SKILL AT STEP 10.** This table and §20.4's below are
> the reference a person reads while working a defect, which is what a skill is
> for — loaded on invocation rather than carried in every session. They stay
> here until that skill exists, because the gate in §20.4 is live now.

| | Discipline | What it answers |
|---|---|---|
| **D0** | **prepare** | Is there a reproduction that is not a story — the request, the case, the build, re-runnable |
| **D1** | **team** | Who is working it, and who rules on what |
| **D2** | **describe, with IS / IS-NOT** | What happens, where, since when, how you know — **and the nearest thing it is NOT**, which is what bounds it |
| **D3** | **interim containment, WITH its removal condition** | What protects the Belt while the real fix is built, and what retires it |
| **D4** | **root cause, in TWO parts** | **Occurrence** — why it happened. **Escape** — why nothing detected it |
| **D5** | **chosen permanent fix** | Which change, and why that one rather than the others costed |
| **D6** | **verification** | What proves the fix works — and what would have failed before it |
| **D7** | **prevention of recurrence** | What stops the **class**, not this instance. Usually a check, a schema, or a gate |
| **D8** | **closure conditions** | What has to be true to call it closed — here, the step's Done-when |

### 20.4 — Enforced at the commit, as rule 6

`.claude/hooks/commit-msg-refactor-guard.py` blocks a fix commit whose body does
not answer the six.

| | |
|---|---|
| **Required labels** | `D2 IS:` · `D2 IS-NOT:` · `D4 OCCURRENCE:` · `D4 ESCAPE:` · `D5 FIX:` · `D7 PREVENT:` — each starting a line, each followed by a colon |
| **Why these six and not all nine** | D6 is the step's `Verify` and guard rules 3 and 4 already run it; D8 is its Done-when; D0 and D1 are process the commit does not need to carry |
| **What counts as a fix** | the subject's type is `fix` or `hotfix`; **or** the subject names a registered defect (`G-49`, `F-15`, `WATCH 26`); **or** the body already carries a `D<n>` label |
| **Declining on the record** | `8D: NOT A FIX — <why>` — valid only for the middle trigger. It cannot exempt a `fix(` subject or a body that already carries D-labels |
| **What it checks** | that each discipline is ANSWERED, never that the answer is right. An empty one passes as `NONE — <reason>`; bare `NONE` does not |

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
decision is finalised, not background reading. Confirm a replacement is actually
shipped and feature-complete in the **installed** version before porting to it
(§16.3).

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

1. Record the ruling in `ARCHITECTURE.md` — the section that owns the topic, plus
   its §56 changelog entry. Rulings do not go to any archived document.
2. Commit the rule change to this file or the owning rule file — its own commit,
   `docs(rules):` prefix, no code alongside it.
3. **Increment the version number at the top of this file.**
3b. **A new field on `SupervisorState`, `PhaseState` or `CoachingResponse`
   requires an amendment** — all three are load-bearing schemas (§10.1, §10.7).
4. If the rule number appears in `deprecated_patterns.yaml`, update the registry
   in that same commit (§0.2).
5. State the occurrence and escape causes in the commit body (§20).

**Never amend a rule "in passing" while making a feature change.** Architecture
changes are separate commits.
