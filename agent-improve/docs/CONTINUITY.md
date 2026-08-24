<!--
Document: agent-improve/docs/CONTINUITY.md
Version: 3.0 — 2026-08-22
Purpose: Session-start orientation. A new session reading ONLY this file should
         be able to orient fully and continue without losing a day.

REBUILT 2026-08-22 from the live files, not from the previous text. v2.8 had
drifted on the CLAUDE.md version, the document map, the code-migration step,
and the status of several decisions. A stale orientation file is worse than
none — it is read first and trusted.

MAINTENANCE RULE: when a version number, a step, or a document location
changes, update this file in the same commit. Verify claims against the files
themselves; do not carry a line forward because it was here before.
-->

# AgentLean — Session Continuity Guide
# Version 3.5 — 2026-08-24

> **Read this first, then stop reading it.** This file orients. The binding
> documents are named in §2 and they win on every point of detail.

---

## 1. What this project is

**AgentLean** is a three-agent platform for Lean Six Sigma practitioners:

| Agent | Purpose | Status | Port |
|---|---|---|---|
| **Agent Resolve** | Incident problem-solving | Production | 8010 |
| **Agent Improve** | DMAIC coaching | **In refactor — active work** | 8020 |
| **Agent Flow** | Flow / value-stream | Future, not started | 8030 |

**Agent Improve** coaches a Belt through Define → Measure → Analyse → Improve →
Control, capturing what they produce and holding a quality gate between phases
that the Belt explicitly approves. It is a long-running agentic system on
LangGraph: hierarchical subgraphs, a Planner/Executor pair per phase, eight
middlewares in a fixed order, a four-layer validation stack, and a nine-step
human-in-the-loop gate.

**Stack:** FastAPI · LangGraph ≥1.2.6 · LangChain 1.x · Azure OpenAI · Azure AI
Search · Azure Blob · Azure Cache for Redis *(not yet provisioned)*.
**MCP is architecturally excluded** — not deferred, no promotion trigger.

---

## 2. The document map — rebuilt 2026-08-22

**The structure changed materially this session.** The platform reference moved
to the monorepo root and was renamed; `agent-improve/ARCHITECTURE.md` was
reused for a copy of it.

### Binding — three documents

| Document | Scope | Version |
|---|---|---|
| **`/AGENTIC_ARCHITECTURE_REFERENCE.md`** *(monorepo root)* | **The platform architecture.** Binds on all three agents. Formerly `agent-improve/AGENT_IMPROVE_BIBLE.md`, formerly "the Bible" | **1.3** |
| **`agent-improve/CLAUDE.md`** | **The rules.** Quoted at the top of every implementation prompt. **Per agent** — Resolve will get its own | **2.2.18** |
| **`agent-improve/ARCHITECTURE.md`** | **Agent Improve's own architecture.** Originated 2026-08-22 as a copy of the reference; **expected to diverge** | 1.2 + provenance header |

**Where to edit what:** platform-wide → the root reference · Improve-specific →
`agent-improve/ARCHITECTURE.md` · a rule → `CLAUDE.md`.

> **The two architecture files are already diverging and that is intentional.**
> The root gets generalised across three agents; the copy stays Improve's.
> **There is deliberately no sync check** — they are only briefly identical, so
> a diff would fire constantly and mean nothing. They differed by 35 lines
> within one commit of the copy being made.

> **`CLAUDE.md`'s 48 `§` citations all point at the ROOT reference**, never at
> the local copy. One rule, checkable with a single grep. See `CLAUDE.md` §0.12.

### The route

**`agent-improve/docs/REFACTORING_PROCEDURE.md` (v1.1)** — the ordered path
from the v1 tree to the reference's target. 38 steps, spine 2.3 → 11.2, one
step = one commit, every step traces to a reference section and names one
verification method. **Appendix D is the machine-readable step index the
session-start hook parses.**

### Historical record — not binding, do not cite in rules

| Document | What it is |
|---|---|
| `docs/REFACTORING_AGENT_IMPROVE.md` | **The historical review register.** 87 sections, 11 PARTs. Was the design authority; superseded by the reference. Still the best source for *why* a decision was made |
| `docs/EDUCATIONAL.md` | Original chronological learning register, 505KB. Frozen. **Do not edit, do not cite as current** |
| `docs/DECISIONS.md` (v1.4) · `docs/REVIEW_DECISIONS.md` | The decision logs — rationale, rejected options, sources |
| `docs/BIBLE_VERIFICATION_LOG.md` | Task 3B verification record, 2026-08-21. Keeps its name and its "Bible" wording deliberately — renaming a dated log falsifies it |
| `docs/ARCHITECTURE_v2216_registers.md` | **§17 Decisions Resolved and §18 Change Log** from the old v2.2.16 `ARCHITECTURE.md`, extracted 2026-08-22 before the copy replaced that file |
| `docs/SKILL_REVIEW_NOTES.md` · `docs/STATE_DESIGN_RESOLUTION.md` · `docs/RESTRUCTURE_PLAN.md` · `docs/status-79-84-2026-08-10.md` | Audit trail |

**To resolve an old `ARCHITECTURE.md §X` or `REFACTORING §X` citation:** the
reference's **Appendix A** maps both. Note the ambiguity — `ARCHITECTURE.md §X`
meant the v2.2.16 numbering (§1–§18) before 2026-08-22 and the reference's
numbering (§1–§56) after.

---

## 3. What is DONE

### The document work — complete and signed off

1. **Full architectural review** of all 85 original sections against LangChain
   1.x, LangGraph 1.2+ and Anthropic's current engineering posts →
   `REFACTORING_AGENT_IMPROVE.md` (87 sections, 11 PARTs).
2. **`CLAUDE.md` ground-up rewrite** v2.1 → v2.2.x, now **2.2.18**.
3. **The architecture reference written** (Task 3) — Parts I–XI, Appendices A–E.
4. **Task 3B verification pass** — every API signature, parameter name,
   deprecation status, version floor and cited source checked against live
   documentation. **3 corrections, 2 now-stale, 4 enhancements, 15 confirmed.**
   Log: `docs/BIBLE_VERIFICATION_LOG.md`.
5. **`ARCHITECTURE.md` absorption + `CLAUDE.md` citation sweep** — every
   citation re-pointed, nine absorption gaps closed.
6. **Task 4 — the Refactoring Procedure** written, with the session-start hook
   re-pointed at it.
7. **Rename and split** — the reference moved to the root and renamed;
   `agent-improve/ARCHITECTURE.md` became Improve's copy.
8. **Reference sign-off granted.** The procedure is executable.

### The three API corrections worth remembering

They shaped how verification is now done, so they are recorded here rather than
only in the log.

| Finding | What was wrong |
|---|---|
| **C-1** | `ModelRetryMiddleware(retries=2)` — **the keyword is `max_retries`**; `retries=` raises at construction. It sat in the canonical middleware stack from adoption until 2026-08-21 |
| **C-2** | `create_agent(prompt=...)` — **the parameter is `system_prompt`**. `create_react_agent` took `prompt`; `create_agent` renamed it |
| **C-3** | "the six `AgentMiddleware` hooks" stated as a closed set. They are the six *we use*; `dynamic_prompt()`, `hook_config()` and `configure_trace_policy()` also exist |

**No live-code exposure** — none of those three appear in `backend/` yet. Every
occurrence was documentation, which is why they survived: nothing executed them.

### The code refactor — one step done

**Step 2.3 — dependency upgrade. DONE 2026-08-21** (`95926d6`).

| Package | Was | Now |
|---|---|---|
| `langgraph` | 1.1.10 | **1.2.11** |
| `langchain` | 1.2.13 | **1.3.16** |
| `langchain-core` | 1.3.3 | **1.6.0** |
| `langchain-classic` | 1.0.3 | **1.0.8** |

Verified by `import-check`: floor ≥1.2.6 met, `pytest` 6/6 green, app imports,
graph compiles, `pip check` clean. **The LangGraph gate on steps 4.1–4.4 and
8.2 is CLEARED.**

---

## 4. Where the code actually stands

> ### The codebase is still v1. One step of 38 is done.
>
> Step 2.3 changed dependencies only. **No architectural code has been written
> yet.**

**Next: step 2.4 — `set_entry_point` → `add_edge(START, …)`.** Not started. A
one-line change in `backend/core/graph.py`, verified by `grep-absence`. The
session-start hook reports `last completed 2.3 | next 2.4`.

**Measured state of `agent-improve/backend/` as of 2026-08-22:**

| Fact | Value |
|---|---|
| Python files | 55 (~7,900 lines) |
| Graph | 11 flat nodes, one `set_entry_point` (step 2.4) |
| Phase nodes | All sync `def` (step 2.5) |
| Route handlers | **Zero `async def`** in `gateway/routes.py` (step 2.5) |
| `response.content.strip()` | **20 sites across 8 files** (step 2.6) |
| LLM roles | 6 in `_ROLE_MAP`, target 11; `LLMProvider` is a banned class (step 2.7) |
| **Checkpoints ever written** | **0** |

> **The checkpointer is WIRED but INERT.** `core/graph.py` compiles with a
> checkpointer, but `thread_id` and `ainvoke` appear nowhere and
> `gateway/routes.py` discards the compiled graph and dispatches nodes by hand.
> **Closed by step 4.2**, which also carries the five §47 Handler-Shaped
> Durability requirements.

**What does not exist yet:** `core/substate.py` · `core/store.py` ·
`middleware/` · `validation/` · `knowledge/{computation,tool_args,fusion}.py` ·
`core/reliability.py` · `core/diagrams.py` · `phases/{phase}/{graph,nodes,mappers}.py`.

---

## 5. Open items, gates and watches

### Gated — do not schedule work against these

| Item | Status |
|---|---|
| **`RunControl.request_drain()`** | **UNCONFIRMED — MAY NOT EXIST** (reference §45). Not found in LangGraph releases 1.2.5–1.2.11 or the reference; independently confirmed absent from every release body. **Gates step 8.5 only.** If it does not exist, §45 needs a real fallback drain design, not a replacement citation |
| **Azure Cache for Redis** | Not provisioned. Gates step 8.4 only — the chain degrades Level 2 → Level 4 meanwhile, which is correct behaviour |
| **Two Azure index schema changes** | RATIFIED, NOT APPLIED. `improve_evidence_index` gains `phase` + `uploaded_at`; `improve_case_index` `embedding` → `content_vector`. **Batch them — step 9.1.** Write code against the live schema until then |

### Live high-severity SPEC-GAPs — read before gap work

**The register is reference §66; these two are the ones with weight on them
right now.** Both are resolved under the Standing Reasoning Protocol (§6), and
both need a trusted-source check before any design is chosen.

**None right now.** The G-43 → G-44 → G-04 chain that ran through 2026-08-24 is
closed end to end: `PhaseState` persists across Belt turns via the direct
wrapper invoke, and `remaining_steps` is declared so the hop cap fires.

**The register is `ARCHITECTURE.md` §66 — 44 identified, 6 closed or resolved,
38 open.** Pick the next gap from there rather than from this file; nothing
open is currently carrying the severity those three did.

> **Two things are owed and are not gaps**, so they will not surface from §66:
> a **local repro** of the §16 persistence claim (documented, not demonstrated),
> and the **G-01 Level 2 `Command` routing** design, which is the largest open
> item and gates the phase subgraph's wiring.

### Watches

**The `langchain` / `langchain-core` pin has zero margin.** `langchain` 1.3.16
requires `langchain-core>=1.6.0`, and 1.6.0 *is* the current latest — exactly
aligned, not comfortably apart. The next `langchain` release may force a
`langchain-core` move in the same step.

**LangGraph 1.2.7's release body repeats 1.2.6's `checkpoint_ns` fix text
verbatim.** The ≥1.2.6 floor attribution holds, but the fix appears to have
been applied twice — worth knowing if subgraph namespacing misbehaves at 4.1.

### Parallel workstreams — not steps, do not block the spine

| Workstream | Notes |
|---|---|
| **Five SKILL.md files** | Should lead step 6.6 — the coach prompts reference skill content. Drafts exist, not wired into `DMAICSkillsMiddleware` |
| **Eval dataset (§52)** | Becomes load-bearing once step 6.2 lands. **The >10% regression threshold is currently an asserted number** — two Anthropic engineering posts added to Appendix C bear on it, one specifically on separating real regressions from infrastructure noise. Read both before finalising §52 |

### The future root-generalisation task

**The reference is written as one agent's architecture and declared
platform-level.** Part VIII is the DMAIC domain and is Improve's alone; Parts
I–VII and IX–XI are platform. **Six sections carry platform mechanism with
Improve instantiation and are annotated inline** — §5, §6, §23, §30, §32, §35.
Look for the **Scope:** note under the status line. **Those annotations mark the
scope of the generalisation task** when Resolve or Flow are built to this
reference. §30 is the sharpest case: the binding rules are platform, all twenty
tools are Six Sigma.

### Decision-log items still marked pending

Checked against the files 2026-08-22:

| Item | Real status |
|---|---|
| **DECISIONS H2** — `improve_case_index` `content_vector` rename | **Genuinely pending.** Equals procedure step 9.1 |
| **DECISIONS H1** — multi-query Option A description | **Substance appears absorbed** into reference §23–§25 (per-tool `SearchClient`, no shared retriever, the "asymmetry" language corrected). **The PENDING marker looks stale — confirm and close rather than assuming** |
| **DECISIONS G11** — `REFACTORING_AGENT_IMPROVE.md` restructure | **DONE.** The 11 `# PART` headings are present. The marker is stale |
| Reference **Appendix B** deferred backlog | 16 items, each with a promotion trigger. **Items 13 (PostgreSQL) and 16 (geographic redundancy) gate a production launch** |

---

## 6. Session protocol

### Before starting

1. **Read the session-start hook output** — it reports git state, the last
   completed `refactor(arch-v2)` commit, the next step, and dependency drift.
2. **Confirm the working tree is clean and pushed.**
3. **Open the procedure at the next step.** Check its **Precondition**, run its
   prompt, run its **Verify** method.
4. **If the session's work is resolving a SPEC-GAP** (root reference §66),
   read the **Standing Reasoning Protocol** below before touching anything.
   No gap is closed on the local fix alone.

### Hard rules

- **Never run `agent-improve/start.ps1`.** It does `git reset --hard
  origin/main` and destroys unpushed commits. Start the server manually:
  `cd agent-improve; .\.venv\Scripts\Activate.ps1; uvicorn backend.app:app --host 127.0.0.1 --port 8020 --reload`
- **Never `git add -A`** — stage by name.
- **Every commit** ends with the `Co-Authored-By: Claude Opus 5 (1M context)`
  trailer, and commit bodies are descriptive: what changed, at which named
  sites, and why.
- **Refactor commits use the fixed subject format** the hook parses:
  `refactor(arch-v2): commit X.Y — <what changed>`
- **`/verify-current-version` before any version or API decision.** The
  reference is authoritative for architecture; **the live package index is
  authoritative for what version exists now.** No step trusts a version written
  in any document, including the reference's own snapshot.

> ### Reference sweeps must use raw `grep -rn`
>
> **Agent-facing search tools filter by `.gitignore` and are structurally
> unable to see gitignored paths.** The 2026-08-22 rename sweep reported zero
> stale references through a filtered tool while a raw `grep -rn` immediately
> found one it could not reach. **Any sweep concluding "zero remaining
> references" ends with an unfiltered `grep -rn`.** A filtered tool locates;
> it is not evidence of absence. Recorded as reference §55.

### STANDING REASONING PROTOCOL — filling SPEC-GAPs

**This governs every SPEC-GAP resolution** (root reference §66). It is
process governance, not architecture — it is amended here and in
`docs/SPEC_LAYER_GUIDE.md` §6.1, not through reference §56.

*Reproduced verbatim as approved 2026-08-24. The only alteration is the
title line, lifted into a heading; no word is changed.*

Every spec gap is resolved through this discipline, never a quick local patch:

1. DETAIL — the specific fix: exactly what field/function/signature changes.
2. HOLISTIC — trace it through every SIPOC link it touches. Each SIPOC entry is
   a use-case skeleton (Supplier→Input→Process→Output→Customer), so a change to
   one function's Input/Output ripples to every Supplier and Customer connected
   to it. List the affected use cases; confirm the fix holds across ALL of them,
   not just the one that surfaced the gap.
3. TRUSTED-SOURCE CHECK — verify the chosen pattern against current
   LangGraph/LangChain/LangSmith sources (and EU AI Act/DORA for
   compliance-touching gaps). No pattern is adopted on plausibility; it is
   confirmed against a current source or explicitly marked unverified. (R2
   lesson: a plausible API that doesn't exist is a demonstrated failure mode.)
4. USE-CASE FORWARD-NOTE — SIPOCs are the basis for the sequence diagrams / use
   cases to be built later. Each resolved gap records which use case(s) it
   belongs to, so the later sequence-diagram pass has the material ready.

Resolving a gap MAY surface new gaps — the holistic trace can reveal a further
function that mishandles the same field. The gap list is not fixed; expand it
when the trace demands. No gap is closed on DETAIL alone; steps 2–4 are
mandatory.

> **Step 2's scope is narrowed, and the narrowing matters.** The SIPOC
> cross-check applies **only to peer runtime call edges** — one node or function
> invoking another. Edges into class entries, return paths, build-time graph
> wiring and nested sub-components are **out of scope and are not findings**.
> Its first run reported 36 non-closures of which only 5 were real wiring
> defects — 29 of the 36 fall outside the narrowed scope. Tracing against the
> un-narrowed rule spends the trace's attention on noise. Scope definition:
> root reference **§55.1 rule 3**. The run that forced it: **§66.8**.

### The lesson this session keeps re-teaching

**A check that cannot fail is worse than no check, because it is recorded as
evidence.** Three instances, all caught: a `grep-absence` written against
retired names that never existed; a step lookup that rendered a parse failure
identically to success; and a reference sweep run through a tool that could not
see part of the tree. **When you write a verification, first prove it can
fail.**

---

## 7. Amendment procedure

| Change | Route |
|---|---|
| **Platform architecture** | Root reference §56 — decision in `docs/DECISIONS.md`, section updated, version bumped, change log in DECISIONS + a one-line note at the reference head |
| **A rule** | `CLAUDE.md` §18 — plus a numbered `§0.x` change entry in that file |
| **Improve-specific architecture** | `agent-improve/ARCHITECTURE.md` |
| **A rule number cited in `deprecated_patterns.yaml`** | **Update the registry in the same commit** (§55) |
| **During Improve's refactor** | Improve-specific architectural decisions are recorded in `agent-improve/ARCHITECTURE.md`, not `DECISIONS.md`. Platform-level decisions are captured there too **for now** and back-ported to the root reference (§56) once Improve is settled. Deliberate, temporary divergence from the root-first procedure above. |

**Never amend a rule in passing while making a feature change.** Architecture
changes are separate commits.

---

## 8. Version log

| Version | Date | Change |
|---|---|---|
| **3.5** | 2026-08-24 | **G-04 resolved** — `remaining_steps` declared as a LangGraph managed value on `PhaseState`; the hop cap now fires (the `.get(..., 10)` default had masked it). `ARCHITECTURE.md` S-C02/§26/§66 and `CLAUDE.md` §10.1 amended; register 6 closed / 38 open. Field count now "19 author-populated + 1 managed" |
| **3.4** | 2026-08-24 | **G-44 resolved** — the phase wrapper's inner `subgraph.ainvoke` persists `PhaseState` when called directly inside the node with inherited config; breaks only if moved inside a tool. ARCHITECTURE.md §16 gains the rule; §66 register G-44 → Closed (5 resolved / 39 open). Process note added to §7. **G-04 is now the next live gap.** Local repro of the persistence claim still owed |
| **3.3** | 2026-08-24 | **Live high-severity gap list added** (§5) — G-44 and G-04, with the ordering argument between them. Added when G-43 was resolved as a false alarm and its narrower successor G-44 registered |
| **3.2** | 2026-08-24 | **SIPOC cross-check scope note added** to the Standing Reasoning Protocol — step 2's holistic trace applies to peer runtime call edges only. Mirrors the narrowing of reference §55.1 rule 3. Process governance, not a §56 amendment |
| **3.1** | 2026-08-24 | **Standing Reasoning Protocol added** (§6) — the discipline every SPEC-GAP resolution follows: detail, holistic SIPOC trace, trusted-source check, use-case forward-note. Also in `docs/SPEC_LAYER_GUIDE.md` §6.1. Process governance, not a §56 amendment |
| **3.0** | 2026-08-22 | **Rebuilt from the live files.** v2.8 had drifted on the CLAUDE.md version (said 2.2.14, actual 2.2.18), the entire document map (the reference moved to root and was renamed; `ARCHITECTURE.md` became a copy), the code-migration step (said 2.5+ pending; actual 2.3 done / 2.4 next), and three decision statuses. Duplicate `## 4` heading fixed |
| 2.8 | 2026-08-19 | Last version before the reference rewrite |

*A new session should be able to act on §4 and §5 without opening another file.*
