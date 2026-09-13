# Agent Improve — CLAUDE.md
# Version 2.2.37 — September 2026
# 2026 LangChain/LangGraph standards. Authoritative. Never bypass.

---

## 0. CONSTITUTION — Read Before Any Change

These rules are the constitution. Every Claude Code prompt must quote
the relevant rule numbers at the top of the prompt. If a rule blocks
a request, the rule wins. If a rule is wrong, propose an amendment
to this file FIRST in a separate commit — never violate it silently.

Violations of this constitution cost weeks of rework. We have proven
this twice with Agent Resolve and once with Agent Improve. There is
no third time.

> **§0'S CHANGE RECORDS ARE ARCHIVED.** The dated *What Changed in 2.2.x*
> subsections moved verbatim to `docs/_archive/CLAUDE_md_S0_change_records.md`
> on 2026-09-13 — 27 subsections, 954 lines. **The four that remain are not
> change records**: §0.1 and §0.12 carry the document tables and the citation
> conventions, §0.2 and §0.24 are rules. **Their numbers are unchanged and the
> gaps in the sequence are deliberate** — §0.2 applies to itself, and
> `.claude/config/deprecated_patterns.yaml` cites §0.24 three times.
>
> **HOW A `§0.x` CITATION RESOLVES.** If it is not one of the four above,
> it resolves in the archive file — one rule rather than twenty rewritten
> citations, and the reason none of them was rewritten. Ten live sections
> cite §0.10, §0.17, §0.18, §0.20 and §0.28–§0.31 for the DATE a thing was
> ratified, never for a value: §9.7 carries *"Thirteen gate-required,
> twelve coached"* in its own text and cites §0.18 only for *"Option A,
> ratified 2026-08-26"*. **Checked before the move, not after** —
> ARCHITECTURE.md v1.39.

### 0.1 — What v2.2 Is

v2.2 is a **ground-up rewrite**, not a patch. It aligns this file with
every decision ratified in the EDUCATIONAL.md architectural review. (archived to docs/_archive/; canonical: REVIEW_DECISIONS.md)

**Three binding documents.** The **v2.2.16 `ARCHITECTURE.md`** was absorbed
into `../AGENTIC_ARCHITECTURE_REFERENCE.md`; on 2026-08-22 that path was reused
for **a copy of the reference** — Agent Improve's own architecture document
(§0.12). **Every `§`-citation in this file points at the root reference**,
never at the local copy.

| Document | Answers | Binding? |
|---|---|---|
| `CLAUDE.md` (this file) | **What the rule is.** Quoted at the top of every implementation prompt | **Yes** |
| `../AGENTIC_ARCHITECTURE_REFERENCE.md` | **How the platform is shaped, and why.** All three agents | **Yes** |
| `ARCHITECTURE.md` | **How Agent Improve specifically is shaped.** Began as a copy of the reference, expected to diverge (§0.12) | **Yes** |

**The historical record is not binding and is not cited by rules here.**
`docs/_archive/REFACTORING_AGENT_IMPROVE.md` (the section-by-section review),
`docs/_archive/EDUCATIONAL.md`, `docs/_archive/DECISIONS.md` and `docs/REVIEW_DECISIONS.md`
hold the reasoning trail — what was considered, rejected and when. Each
Reference section carries a **Supersedes** line naming its sources, so the
chain back to that trail is one hop from any rule. (archived to docs/_archive/; canonical: REVIEW_DECISIONS.md)

> **Disambiguation — `ARCHITECTURE.md §X` means two different things now.**
> Before 2026-08-22 it meant the **v2.2.16** design document's own numbering
> (§1–§18). Since then that path holds a copy of the reference and uses the
> **reference's** numbering (§1–§56).
>
> **To resolve a pre-2026-08-22 `ARCHITECTURE.md §X` or `REFACTORING §X`
> citation** — in code comments, SKILL.md files or an older prompt — **use the
> reference's Appendix A**, which maps the v2.2.16 numbering to the current one.
> The v2.2.16 original is at commit `8533879`; its §17 and §18 registers are at
> `docs/_archive/ARCHITECTURE_v2216_registers.md`. (archived to docs/_archive/; canonical: ARCHITECTURE.md Appendix F)

### 0.2 — Rule Numbers Are Load-Bearing

`.claude/config/deprecated_patterns.yaml` cites rule numbers in the
messages the drift hook feeds back to Claude. These citations must
resolve:

| Registry pattern | Cites |
|---|---|
| `pattern-2-with-structured-output` | §4.6 |
| `pattern-3-response-content-parsing` | §4.5 |
| `pattern-4-custom-saga` | §3.6 |
| `pattern-8-bind-tools-in-phase-executor` | §4.4 |
| `pattern-9-hand-rolled-llm-retry` | §8.7, §0.24 |
| `pattern-10-custom-llm-tracing` | §11.2, §0.24 |
| `pattern-11-manual-state-persistence` | §1.7, §10.2, §0.24 |

**Renumbering any of these rules requires updating the registry in the
same commit.** A hook that cites a non-existent rule is worse than no
hook — see `../AGENTIC_ARCHITECTURE_REFERENCE.md` §55.

### 0.12 — Two architecture documents, and which one a rule cites

**Since 2026-08-22 there are two**, and they are not duplicates of each other
for long:

| File | Scope | Edited when |
|---|---|---|
| `../AGENTIC_ARCHITECTURE_REFERENCE.md` | **Platform.** Binds on Agent Improve, Agent Resolve and Agent Flow | The change applies to more than one agent |
| `ARCHITECTURE.md` | **Agent Improve's own architecture.** Originated 2026-08-22 as a copy of the reference at commit `8533879` | The change is Improve-specific |

**They begin identical and are expected to diverge** — the reference gets
generalised across the three agents while the local copy stays specific to
Improve. **That divergence is the intent, not drift**, which is why there is
deliberately no sync check between them: two files that are only briefly
identical would make such a check fire constantly and mean nothing.

> **Every `§` citation in this file points at the root reference, never at the
> local copy.** One rule, and a mechanically checkable one — a single grep
> confirms it. The alternative was routing each citation by whether its subject
> is platform or Improve-specific; measured against the actual citations that
> would have moved only 4 of 48 sections, in exchange for a rule no script can
> verify and 48 individual judgment calls on a boundary that is clean
> structurally and blurry in content.
>
> **The platform / Improve boundary is real but does not follow file paths.**
> Part VIII of the reference is the DMAIC domain and is Improve's alone;
> Parts I–VII and IX–XI are platform. Several platform sections nonetheless
> carry Improve-specific instantiation — §30's twenty tools are Six Sigma
> statistics, §23's schemas are the `improve_*` indexes. Those sections are
> annotated in the reference itself rather than sorted by which file cites them.

**The v2.2.16 design document that used to live at `ARCHITECTURE.md`** was
absorbed into the reference. Its two registers that existed nowhere else —
§17 Decisions Resolved and §18 Change Log — are at
`docs/_archive/ARCHITECTURE_v2216_registers.md`; the full original is at commit
`8533879`. (archived to docs/_archive/; canonical: ARCHITECTURE.md Appendix F)

### 0.24 — PREFER FRAMEWORK PRIMITIVES — a standing RULE, not a change record

*Every other §0.x above is a dated "What Changed" entry. **This one is a rule**,
placed in §0 because it is constitutional: it governs what may be BUILT, not
what was decided on a particular day. Added 2026-08-31 at 2.2.30.*

> **Before hand-rolling retry, tracing/metrics, state persistence,
> checkpointing, or the agent loop, confirm LangChain / LangGraph / LangSmith
> does not already provide it. Reinventing a framework primitive is a
> violation.**

| If you are about to build… | Use instead | Specified in |
|---|---|---|
| A retry loop around a model call | **`ModelRetryMiddleware(max_retries=2)`** on `create_agent` — and `ToolRetryMiddleware` for tool calls; they are different middlewares, not synonyms | Reference **§19.4** · §8.7 |
| Tracing, metrics, or a callback layer for LLM calls | **LangSmith.** `LANGCHAIN_TRACING_V2=true`, plus **`@traceable`** on the plain Python functions between nodes — runnables and graph nodes are traced already | Reference **§51** · §11.2 |
| Saving or restoring graph/phase state | **The LangGraph checkpointer** (per `thread_id`), and **the store** for cross-phase artifacts. Both attach to the PARENT graph only | Reference **§16** · §1.7, §10.2 |
| An agent loop — model → tools → model | **`create_agent`**, with the eight-middleware stack | Reference **§18** · §4.4, §8.1 |

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
after. **It is therefore not a §56 reference amendment**: no section of
`../AGENTIC_ARCHITECTURE_REFERENCE.md` changes, and every § cited above already
says what this rule says.

**It is enforced, not just stated.** Three registry patterns block the write:
`pattern-9-hand-rolled-llm-retry`, `pattern-10-custom-llm-tracing`,
`pattern-11-manual-state-persistence` — see §0.2's table. They match a SHAPE
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

## 1. THE RULES ARE IN `.claude/rules/`

> **Moved 2026-09-13, verbatim, brief step 6.** §1–§15 are thirteen files
> under `.claude/rules/`, each with `paths:` frontmatter so it loads only
> when a file it governs is opened. **Rule numbers are unchanged** —
> `.claude/config/deprecated_patterns.yaml` cites them and §0.2 makes that
> binding, so `§8.7` still means §8.7 wherever it is written.

| Was | Now | Loads when you open |
|---|---|---|
| §1 | `.claude/rules/architecture.md` | `agent-improve/backend/core/graph.py`, `agent-improve/backend/core/checkpointer.py`, `agent-improve/backend/core/store.py`, `agent-improve/backend/core/tracing.py`, `agent-improve/backend/phases/subgraph_common.py` |
| §2 | `.claude/rules/module-layout.md` | `agent-improve/backend/core/checkpointer.py`, `agent-improve/backend/core/citations.py`, `agent-improve/backend/core/errors.py`, `agent-improve/backend/core/graph.py`, `agent-improve/backend/core/llm.py`, `agent-improve/backend/core/reliability.py`, `agent-improve/backend/core/state.py`, `agent-improve/backend/core/store.py`, `agent-improve/backend/core/substate.py`, `agent-improve/backend/gateway/routes.py`, `agent-improve/backend/gateway/schemas.py`, `agent-improve/backend/knowledge/computation.py`, `agent-improve/backend/knowledge/retriever.py`, `agent-improve/backend/knowledge/tool_args.py`, `agent-improve/backend/knowledge/tools.py`, `agent-improve/backend/middleware/coherence.py`, `agent-improve/backend/middleware/contradiction.py`, `agent-improve/backend/middleware/grader.py`, `agent-improve/backend/middleware/skills.py`, `agent-improve/backend/middleware/state_injection.py`, `agent-improve/backend/storage/blob.py`, `agent-improve/backend/storage/models.py`, `agent-improve/backend/validation/gate_validator.py`, `agent-improve/backend/validation/schemas.py` |
| §3 | `.claude/rules/graph.md` | `agent-improve/backend/core/graph.py`, `agent-improve/backend/phases/**` |
| §4 | `.claude/rules/llm.md` | `agent-improve/backend/core/llm.py`, `agent-improve/backend/phases/**`, `agent-improve/backend/upload/**` |
| §5 | `.claude/rules/tools.md` | `agent-improve/backend/knowledge/tools.py`, `agent-improve/backend/knowledge/computation.py`, `agent-improve/backend/knowledge/tool_args.py` |
| §6 and §15 | `.claude/rules/prompts.md` | `agent-improve/backend/core/prompts.py`, `agent-improve/skills/**` |
| §7 | `.claude/rules/rag.md` | `agent-improve/backend/knowledge/**`, `agent-improve/scripts/ingest_knowledge.py` |
| §8 | `.claude/rules/middleware.md` | `agent-improve/backend/middleware/**` |
| §9 | `.claude/rules/gates.md` | `agent-improve/backend/validation/**`, `agent-improve/backend/phases/**` |
| §10 | `.claude/rules/state.md` | `agent-improve/backend/core/state.py`, `agent-improve/backend/core/substate.py`, `agent-improve/backend/storage/**` |
| §11 | `.claude/rules/observability.md` | `agent-improve/backend/core/tracing.py`, `agent-improve/backend/core/logging_setup.py`, `agent-improve/backend/core/metrics.py` |
| §12 | `.claude/rules/testing.md` | `agent-improve/backend/tests/**` |
| §13 | `.claude/rules/ui.md` | `agent-improve/ui/**`, `agent-improve/backend/gateway/**` |

**§14 is distributed, not moved.** Its 95 bans each land in exactly one
place: 87 under the `## Never` heading of the rule file that owns their
subject, and the 8 cross-cutting ones below. A ban now loads with the code
it governs.

**§17 is dropped.** `docs/REFACTORING_PROCEDURE.md` owns the sequence, and
a second copy of it here was the thing that went stale.

### 1.1 — Never, everywhere

*§14's cross-cutting bans. These bind on every file and belong to no
single rule file, which is why they stayed here.*

- Never renumber a rule cited in `deprecated_patterns.yaml` without
  updating the registry in the same commit (§0.2)
- Never deliver a decision or an explanation as prose threaded with
  section numbers — it is a diagram or a table carrying the full detail
  (§19.1 — a decision or an explanation is delivered as a visual)
- Never render a bare number or a bare code in anything a human reads —
  "6.20 — the write paths", never "6.20" (§19.2 — never a bare number,
  never a bare code)
- Never propose a fix before the 8D is worked — a defect, a
  modification and an adaptation are all worked first (§20 — every fix
  is an 8D)
- Never give an occurrence cause without an escape cause — "why did
  nothing detect this" is a separate answer (§20.2 — three clauses carry
  the weight)
- Never put an interim containment in place without its removal
  condition (§20.2 — three clauses carry the weight)
- Never omit an empty discipline — it is a finding, and it is written
  `NONE — <reason>` (§20.2 — three clauses carry the weight)
- Never make a claim about what the code does without quoting the lines
  it rests on, with file and line number — and never state an absence
  without the command and its output (§20.5.1 — a claim about code
  carries the code)

---

## 16. VERSION TARGETS AND DEPENDENCIES

### 16.1 — The floor, and where the pins live

**THIS FILE STATES NO VERSION NUMBER FOR A DEPENDENCY.**
`agent-improve/requirements.txt` carries every resolved pin and is the only
place that does. **Read it; do not read this section for it.**

| Floor | Attribution |
|---|---|
| `langgraph >= 1.2.6` | LangGraph 1.2.6 (2026-06-18) carries *"nested subgraph inherits parent `checkpoint_ns` (regression in 1.2.3)"* — the fix §1.2 depends on, and the native reliability primitives §3.6 needs |
| `langchain-core >= 1.6.0` | Required by `langchain` 1.x as resolved |

**A floor is a rule and does not move. A pin is a fact `pip` owns.** The floor
is stated here because a rule belongs in a rule file; the pin is not, because a
version transcribed into a document is stale the day the project upgrades.

> **THIS SECTION CALLED THE UPGRADE A BLOCKER UNTIL 2026-09-12 — three weeks
> after step 2.3 performed it.** It tabled `langgraph` 1.1.10 and
> `langchain-core` 1.3.3 as *Installed* against a venv running 1.2.11 and 1.6.0,
> under the heading `Pinned targets`. The table even warned that *"the targets
> are a snapshot — re-resolve at upgrade time"* and then went stale in exactly
> the way it described. **A snapshot that warns it is a snapshot is still a
> snapshot.** Owner: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §53.

**Do not upgrade to a version written in a document — re-resolve against live
PyPI** (§16.3). Let pip resolve the adjacent packages during an upgrade, then
repin in `requirements.txt`.

**During the upgrade, sweep for imports from `langgraph.prebuilt`** —
deprecated in 1.0 → 1.1, functionality moved to `langchain.agents`. Its presence
as a transitive dependency is not a violation: §4.4 bans the import, not the
package.

### 16.2 — New infrastructure required

| Component | For | Status |
|---|---|---|
| Azure Cache for Redis | Fallback chain Level 3 (§4.8) | **Not yet provisioned** — add to the provisioning plan |
| Azure Database for PostgreSQL | `PostgresSaver` + `PostgresStore` (§1.7) | Provision before production launch |

### 16.3 — Verify before migrating

`/verify-current-version` is a **mandatory checkpoint before any
architectural decision is finalised**, not background reading. It
exists because a deprecation notice is not sufficient guidance: during
this review, `create_agent` was found to have a reported regression
relative to `create_react_agent`, and the deprecation message pointed
at a function that did not yet exist in the package at the time.

Confirm a replacement is **actually shipped and feature-complete in
the installed version** before porting to it.

---

## 18. AMENDMENT PROCEDURE

This file is amended only via:

1. A new architectural decision recorded in `docs/_archive/DECISIONS.md` and stated in
   the `../AGENTIC_ARCHITECTURE_REFERENCE.md` section that owns the topic
2. A commit to CLAUDE.md updating the relevant rule
3. Increment to the version number at the top
3b. **A new field on `SupervisorState`, `PhaseState` or `CoachingResponse`
   requires an amendment** — all three are load-bearing schemas (§10.1, §10.7)
4. **A numbered `§0.x` change entry in this file**, saying what changed and
   why. The reference's own change log lives in `docs/_archive/DECISIONS.md` plus a
   one-line version note at its head — it has no change-log section, by design
   (`../AGENTIC_ARCHITECTURE_REFERENCE.md` §56 step 4)
5. **If a rule number cited in `deprecated_patterns.yaml` changes, the
   registry is updated in the same commit** (§0.2)

Never amend a rule "in passing" while making a feature change.
Architecture changes are separate commits.

### 18.1 — Known open item for the next amendment

**§4.6 replaces v2.1's §4.3 and resolves a live contradiction.** The
drift registry's `pattern-2` message cites "CLAUDE.md §4.6" — a rule
that did not exist until this version, while v2.1 §4.3 mandated the
pattern the hook blocked.

Now that §4.6 exists and is scoped, the registry entry should be
updated to reflect the scoping: the builder-style call is correct
inside tools, middleware, and validators, and only agent construction
should prefer `response_format=`. Until that update lands,
`agent-improve/**/*.md` remains path-excluded so the governance
documents stay writable.

*Design: `../AGENTIC_ARCHITECTURE_REFERENCE.md` §55, §56.*

---

## 19. HOW FINDINGS REACH THE FOUNDER

**FOUNDER RULING 2026-09-11.** Two rules. They bind **every output a human
reads** — the board, an audit's findings, a step report, a brief, a review
reply, an answer in chat.

### 19.1 — A decision or an explanation is delivered as a VISUAL

**If an output asks the founder to DECIDE, or exists to EXPLAIN, it is a
diagram or a table carrying the full detail** — never prose threaded with
section numbers.

| An output whose job is | Takes this shape | Not this |
|---|---|---|
| **A decision** — choose one, approve or reject, rule on a split | **A table**: one row per option, one column per thing that differs, the cost of each in its own cell | paragraphs describing the options one after another |
| **Explaining a flow or a structure** — how a mechanism works, where a value is written, what a guard checks | **A diagram** | a walk-through the reader has to hold in their head to compare |
| **Explaining a set of facts** — what an audit found, which sites disagree, what is missing | **A table**: one row per fact, the site and the verdict in cells | a numbered prose list |
| **Status** | **the board** — `agent-improve/docs/board.html`, generated (§0.28 — the document set collapses to two) | a prose paragraph restating what the board already shows |
| **Explaining a DEFECT** — what broke, why, and why nothing caught it | **the 8D table**, nine rows, empty disciplines shown empty (§20.5 — every defect report is delivered in this structure) | a narrative that hides which discipline went unanswered |

**"Carrying the full detail" is the load-bearing half of the rule.** A summary
table sitting on top of three pages of prose does not satisfy it — the visual
IS the finding, not an index to it. **If a fact matters, it is a cell.** A fact
that will not fit in a cell has not been reduced yet, and reducing it is the
work, not the reader's job.

### 19.2 — Never a bare number, never a bare code

**Every number and every code carries the name of what it points at, in the
same breath, every time it appears** — not once at the top and bare thereafter.

| Never write | Always write |
|---|---|
| `6.20` | **6.20 — the write paths** |
| `§39.1.7` | **§39.1.7 — Define's state contract** |
| `G-49` | **G-49 — the executor ignores the tool its planner names** |
| "the guard's rule 5" | **rule 5 — CONTINUITY.md is staged and its status block matches regeneration** |
| "18/15/14/14/17 fields" | **the gate schemas — Define 18 fields, Measure 15, Analyse 14, Improve 14, Control 17** |

**This already held for the board**, where every number carries its subject and
one colour means one thing (§0.28 — the document set collapses to two). **It
now holds for reports, briefs, findings and replies.**

A bare number is legible only to a reader already holding the register it
indexes. The founder reading a finding is not holding that register — being
sent the finding is the whole point.

### 19.3 — Why this is a RULE and not a style note

**The largest cost of this refactor has not been code. It has been findings the
founder could not read, and therefore could not act on.**

A correct finding that does not reach a decision has not been delivered, and it
costs more than a wrong one: a wrong finding gets corrected, an unreadable one
gets filed. This paragraph exists so the rule is enforced on that ground and
not on taste — §19.1 and §19.2 are not about how writing looks.

### 19.4 — Where the rule bites, and the open item

| Output | Bound? |
|---|---|
| An audit's findings, a step report, a brief, a review reply, an answer in chat | **Yes** — the rule was written for exactly these |
| `agent-improve/docs/board.html` — the board | **Yes**, and already conformant since step 6.16 — the board is generated, not written |
| A commit body — the decision record since the 2026-09-10 ruling (§0.28 — the document set collapses to two) | **Yes** — a human reads it, while investigating the diff it explains |
| A NEW or AMENDED rule in this file or in `ARCHITECTURE.md` | **Yes** — a rule written from 2026-09-11 names what its own citations point at |
| The 1,128 parenthetical `(§x)` citations ALREADY standing in those two files | **Ratchet, not sweep** — each is named when its rule is next amended. Open item below |

> **OPEN ITEM — for the founder, one call to make.** The ruling says *any output
> a human reads*, and both binding documents are read by a human. Between them
> they carry **1,128** parenthetical `(§x)` cross-references — 310 in this file,
> 818 in `ARCHITECTURE.md`. Naming all of them in one pass is a diff across
> nearly every rule in the constitution, so **this amendment binds them forward
> only**: every rule touched from 2026-09-11 names its citations, and the
> back-catalogue stands as it is. **If the sweep is wanted instead it is its own
> step and its own commit** — say so and it happens. Nothing else in §19 is
> scoped, narrowed, or deferred.

*Founder ruling 2026-09-11. Reason: §19.3 — why this is a rule and not a style
note. Change record: §0.29 — a finding is delivered as a visual.*

---

## 20. EVERY FIX IS AN 8D

**FOUNDER RULING 2026-09-11.** Every **defect, modification or adaptation** is
worked as an 8D **before any fix is proposed**. Not features — defects and
changes.

**The 8D is the work, not the write-up.** It is what is done first; the commit
body is where it lands, because the commit body is already the decision record
(§0.28 — the document set collapses to two). **And it is enforced at the commit,
not trusted** — rule 6 of `.claude/hooks/commit-msg-refactor-guard.py`
(§20.4 — enforced at the commit, as rule 6). Convention decays; a gate does not.

### 20.1 — The nine disciplines

| | Discipline | What it answers |
|---|---|---|
| **D0** | **prepare** | Is there a reproduction that is not a story — the request, the case, the build, re-runnable after a change? |
| **D1** | **team** | Who is working it, and who rules on what. One person plus the founder, here — and which session holds which file, when more than one is live |
| **D2** | **describe, with IS / IS-NOT** | What happens, where, since when, how you know — **and the nearest thing this is NOT.** IS-NOT is the half that bounds the defect; without it every adjacent system is a suspect |
| **D3** | **interim containment, WITH its removal condition** | What protects the Belt while the real fix is built, **and the condition on which it comes out again** |
| **D4** | **root cause, in TWO parts** | **Occurrence** — why it happened. **Escape** — why nothing detected it. Two answers, never one |
| **D5** | **chosen permanent fix** | Which change, and why that one rather than the others costed |
| **D6** | **verification** | What proves the fix works — and what would have failed before it |
| **D7** | **prevention of recurrence** | What stops the **class**, not this instance. Usually a check, a schema, or a rule — rarely a prompt |
| **D8** | **closure conditions** | What has to be true to call it closed. In this project that is the step's Done-when |

### 20.2 — Three clauses carry the weight

**D4 IS NOT COMPLETE WITH ONLY AN OCCURRENCE CAUSE.** *"Why did nothing detect
this"* is a separate answer and is usually the expensive one. An occurrence
cause alone repairs the instance and leaves the blind spot, so the same class
returns by the same route. G-49's occurrence cause is one line — the plan is not
in the request. **Its escape cause is the finding**: every executor test stubs
`create_agent` and asserts the kwargs, so nothing in 849 tests ever looked at
what the model RECEIVES, and the upload manifest shipped at step 6.12 with no
test at all.

**D3 RECORDS ITS OWN REMOVAL CONDITION, OR IT BECOMES PERMANENT.** A containment
with no exit is a workaround with a long life. **The `interrupt()` guard is the
working example**: `test_ContradictionDetectionMiddleware_does_not_call_interrupt`
contains position 6 until the real gate exists, and its removal is **clause 1 of
step 7.3's Done-when** — written where the fix lands, not where the guard sits.

**AN EMPTY DISCIPLINE IS A FINDING AND SAYS SO. IT IS NEVER OMITTED.** Write
**`NONE — <why it is empty>`**. An omitted discipline reads as forgotten; an
empty one with its reason reads as measured. **D3 and D7 are empty for G-49, and
that is the most useful thing the structure produced** — it says in two lines
that the product is unprotected today and that nothing yet stops a second
instance, which no amount of correct D4 would have surfaced.

### 20.3 — The worked example: G-49, empty disciplines included

| | G-49 — the executor ignores the tool its planner names |
|---|---|
| **D0** | `POST /ask` on `IMPR-2026-ED8`, *"what does our to-be process look like"*, re-runnable; reproduced on `09960df` at 45.141s against 2026-09-10's 45.157s on `1714d75` |
| **D1** | This session and the founder; the board and verifier files were held by a second live session at the time (§19.4 — where the rule bites, and the open item) |
| **D2 IS** | A Define turn with an unread upload issues 18 evidence searches across 3 multi-query calls, fetches no `uploads/` blob, and ends on the 45s node timeout. The planner routes correctly and names the tool and the blob path |
| **D2 IS-NOT** | **Not the hop cap** — §3.7's budget fired correctly. **Not retrieval quality** — the searches returned documents. **Not a binding failure** — `load_evidence_series` is bound in all five phases. **Not §26's off-ramp** — the turn had budget to spend |
| **D3** | **NONE — and that is the finding.** Nothing protects the Belt today: the same question still times out. The only quick containment available was raising the node timeout, which would convert a visible failure into a slow one and pin the symptom the step forbids pinning. Recorded as unprotected rather than papered over |
| **D4 OCCURRENCE** | The plan has no transport into the model's request. `executor()` invokes the agent with `{"messages": prior}`; `coaching_plan` is read for the logger and the `step_log` and nothing else; the system prompt is a per-phase constant; the one state-holding middleware never mentions the plan |
| **D4 ESCAPE** | **No test asserted what the model RECEIVES.** Every executor test stubs `create_agent` and asserts its kwargs, so the composition path never ran under test; and the manifest that the coach does receive landed at step 6.12 with no assertion anywhere in the suite |
| **D5** | **NOT CHOSEN — the founder's ruling.** Four transports are costed at step 6.21 — the plan reaches the model, two of which amend §17. Prompt wording is excluded by the diagnosis itself |
| **D6** | `live-run` **then** `pytest`, in that order: a test written before the cause was known would have pinned the 45s timeout. `test_the_planners_instruction_reaches_the_model` is `xfail(strict=True)`, so the suite goes red the day the transport lands without the marker coming out |
| **D7** | **NONE — nothing here stops the class.** The class is *a decision that is recorded and never delivered*, and the only real prevention is structural — a rule that a node's routing output must reach the consumer it was written for. That is a §17 or §26 amendment and belongs to 6.21, not here |
| **D8** | Step 6.21's Done-when: the strict marker removed, the ruled transport applied and its section amended, a `live-run` in which the named blob is read and an upload is stamped `consumed_at`, and the live halves of 6.7, 6.12 and 6.13 run in the same pass |

### 20.4 — Enforced at the commit, as rule 6

**`.claude/hooks/commit-msg-refactor-guard.py` blocks a fix commit whose body
does not answer five of the nine.** The rules are 1, 2b, 3, 4, 5 and now **6**.

| | |
|---|---|
| **Required labels** | `D2 IS:` · `D2 IS-NOT:` · `D4 OCCURRENCE:` · `D4 ESCAPE:` · `D5 FIX:` · `D7 PREVENT:` |
| **Why these and not all nine** | D6 is the step's `Verify` and rules 3 and 4 already run it; D8 is its Done-when; D1 is one person here; D0 is preparation. **These five are the ones nothing else can see** |
| **What counts as a fix** | the subject's type is `fix` or `hotfix`; **or** the subject names a registered defect — `G-49`, `F-15`, `WATCH 26`; **or** the body already carries any `D<n>` label, which stops a half-written 8D from passing |
| **Missing or empty** | fails. `NONE` **plus a reason** passes; bare `NONE` does not — the reason is the finding |
| **Too short to be an answer** | fails at under 20 characters. `tbd`, `see above` and `n/a` are what a decaying convention produces and they pass a presence check |
| **The one opt-out** | `8D: NOT A FIX — <why>` clears the **defect-code** trigger only. It cannot exempt a `fix(` subject, and it cannot exempt a body carrying D-labels: **a commit that calls itself a fix does not get to opt out of being one.** It stays on the record, where `--no-verify` leaves nothing |
| **What the gate cannot check** | whether an answer is RIGHT. A plausible `D4 ESCAPE` naming the wrong blind spot passes, and the last label in a body absorbs the text after it, so `D7 PREVENT` is usually satisfied by whatever follows. **The gate raises the floor; it does not do the thinking** — and `test_commit_guard_8d.py` pins the gate itself, because a gate with no test is a convention wearing a gate's clothes |

### 20.5 — Every defect report is delivered in this structure

**A report on a defect — to the founder, in chat, in a brief, in a review reply
— is delivered as the 8D**, with the empty disciplines shown empty. This is
§19.1 — a decision or an explanation is delivered as a visual applied to the one
shape that recurs most: a table of nine rows, each discipline named, `NONE` and
its reason where a discipline is empty.

**The reason is the same as §19.3 — why this is a rule and not a style note.** A
defect report in prose invites the reader to reconstruct which question was
answered and which was skipped. The nine rows make an unanswered discipline
visible at a glance, which is exactly what a narrative hides — and D4's missing
half is the thing most worth seeing.

#### 20.5.1 — A claim about code carries the code

**FOUNDER RULING 2026-09-11.** **Any claim about what the code does carries the
lines it rests on, quoted, with file and line number. Not a description of
them.**

| Not this | This |
|---|---|
| *"the executor invokes the agent with `{"messages": prior}`"* | the same claim, **plus the lines**: |

```python
# agent-improve/backend/phases/nodes_common.py:1024-1028
    prior = list(state.get("messages") or [])
    hit_cap = False
    try:
        result = await agent.ainvoke(
            {"messages": prior},
```

**Three to six lines is the normal size.** A claim needing more than about ten
is more than one claim, and splits.

**AN ABSENCE CLAIM CARRIES THE COMMAND AND ITS OUTPUT**, because there are no
lines to quote — and absence claims are usually the load-bearing half of a
diagnosis. *"`BeforeModelStateInjection` never mentions the plan"* is delivered
as the search that shows it:

```
$ grep -n "coaching_plan\|focus_field\|next_action" backend/middleware/state_injection.py
(no matches)
```

#### 20.5.2 — Why, and what it cost to learn

**The reason, recorded so it is not read as a formatting preference.** Claude
Desktop can locate any source file in this repository and **read none of them**
— the file reader refuses `.py` as `application/octet-stream`. **So a code claim
in a report is unverifiable at review unless the report carries its own
evidence.** The reviewer's only options are to take it on trust or to go and
open the file by hand, and the first is what actually happens. **Quoting four
lines costs nothing and converts a relayed claim into a checkable one.**

> **THIS RULE CAUGHT TWO WRONG CITATIONS IN THE REPORT THAT PROMPTED IT.**
> Step 6.18's G-49 report cited `nodes_common.py:1035` for the agent invocation
> — **it is line 1028**, and 1035 is the `recursion_limit` argument four lines
> below it. The same report cited `:995` for `plan = state.get("coaching_plan")`
> — **it is line 990**. Both numbers pointed at plausible neighbouring code in
> the right function, which is exactly why neither looked wrong.
>
> **The diagnosis those citations supported was correct.** The claims held; the
> pointers did not. **That is the failure mode this rule exists for** — a line
> number is the one part of a code claim that carries no evidence of its own
> truth, and a reader who cannot open the file cannot tell a right one from a
> wrong one. Quoting the lines would have failed loudly at writing time, because
> the quote and the claim would not have matched.

*Founder rulings 2026-09-11. Change records: §0.30 — 8D is the structure for
every fix, and §0.31 — a claim about code carries the code. Gate: rule 6 of the
commit-msg guard.*
