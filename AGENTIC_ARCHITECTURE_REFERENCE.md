# Agentic Architecture Reference
**AgentLean Platform · the shared architecture for all three agents**
Version 1.6 · 2026-08-23
Status: **COMPLETE AND CROSS-CHECKED.** Parts I–XI and Appendices A–E written;
Task 3B verification pass completed 2026-08-21.

**v1.6 (2026-08-23)** — **The specification layer.** Two new Parts: **Part XII (§57–§66)** states the classes, functions and interfaces at the level the code could be rebuilt from, and **Part XIII (§67–§68)** carries the EU AI Act posture and the DORA-structured risk register. 73 spec entries; definitions relocated out of 28 architecture sections, which keep every word of their reasoning and gain a `**Specification:**` pointer. **§1–§56 do not renumber.** Five entries carry an AI-ACT flag and 12 carry `AI-ACT-REVIEW: uncertain`. **42 gaps are marked and none is filled** — that was the pass's binding constraint; §66 is the register, and §66.7 records ten findings that are inconsistencies rather than absences. §55.1 adds the five spec-layer governance rules; Appendix C gains a Tier 1 compliance block. Decision record: `agent-improve/docs/DECISIONS.md` §S1, §S2.

**v1.5 (2026-08-22)** — **§15: `route_after_phase` deleted.** The section showed static phase edges *and* a conditional router returning labels wired to nothing, reading `gate_attempts` off `SupervisorState` where that field does not exist — a `KeyError` on the gate-failure path. A phase transition is either static or conditional; static is correct, because a subgraph reaches `END` only through `gate_apply` and so reaching `END` means the gate passed. Retry and escalation resolve inside the phase. **Level 2 routing untouched.** The deleted function was already prohibited by Appendix D.2 — see DECISIONS §R2 for that finding. Decision record: `agent-improve/docs/DECISIONS.md` §R2.

**v1.4 (2026-08-22)** — **Contradiction detection redesigned** (§19.6, §20, §32, §37, §50). The middleware's mechanical dict comparison is deleted — it read a Store key `gate_apply` does not write until phase end, and matched field names where **38 of 41 content fields are unique to one phase**. Detection moves to the coach via SKILL.md instruction and a new `CoachingResponse.contradiction_flag`; **no LLM call is added anywhere**. The middleware keeps its position and hook and becomes a flag-reader. §56 gains `CoachingResponse` to its amendment-required list — that omission was an oversight. Decision record: `agent-improve/docs/DECISIONS.md` §R1.

**v1.3 (2026-08-22)** — Six sections that carry platform mechanism with Agent Improve instantiation now say so inline: §5, §6, §23, §30, §32, §35. **This pre-labels the seams for when this document is generalised** across Resolve and Flow — the Part VIII boundary is clean structurally but blurry in content, and these six are where it is blurriest. No content changed.

**v1.2 (2026-08-22)** — Renamed from `AGENT_IMPROVE_BIBLE.md` and moved to the
monorepo root. **The scope statement changed with it**: this is the platform
reference for Agent Improve, Agent Resolve and Agent Flow, not an
Improve-specific document. See *Scope* below. No architectural content changed
in this version — only the name, the location, the scope statement, and the
relative paths that the move invalidated.

**v1.1 (2026-08-21)** — §29.4 added via the §56 amendment procedure: cross-agent
tools named as a distinct third category, RATIFIED as present-but-not-bound,
with the three rules that bind before any may be bound to a coach. Resolves the
§29.1 / §29.2 tension. Decision record: `agent-improve/docs/DECISIONS.md` §Q1.
Also in this version: Appendix D.1's retired retrieval-tool names corrected to
the strings actually in the codebase, and §53.1's checkpointer status corrected
from "done" to WIRED-but-INERT.

**Verification:** every API signature, parameter name, deprecation status,
version floor and cited source was checked against live documentation. Three
corrections, two now-stale items and four enhancements were applied to this
document as a result. Full log:
[`agent-improve/docs/BIBLE_VERIFICATION_LOG.md`](agent-improve/docs/BIBLE_VERIFICATION_LOG.md)
— that file keeps its original name because it is a dated record of a completed
pass; its subject is this document.

**Four claims remain unverified and are named in the log.**

> **One of them is stronger than "unverified."** `RunControl.request_drain()`
> (§45) is **UNCONFIRMED — MAY NOT EXIST**: it was not located in LangGraph
> releases 1.2.5–1.2.11 or in the reference. **No work may be scheduled against
> it until it is confirmed against a real release or the source**, and if it
> does not exist, §45 needs a real fallback drain design rather than a
> replacement citation. Full statement in §45.

---

## About this document

This is the **agentic architecture reference for the AgentLean platform**. It
states the ratified design directly: what the system is, how each part is
shaped, and why the non-obvious choices were made that way.

### Scope — three agents, one architecture

**This document governs all three AgentLean agents**, not Agent Improve alone:

| Agent | Purpose | Status |
|---|---|---|
| **Agent Resolve** | Incident problem-solving | Production |
| **Agent Improve** | DMAIC coaching | In refactor — the first agent built to this reference |
| **Agent Flow** | Flow / value-stream | Future |

**Parts I–VII and IX–XI are platform architecture** — state and persistence,
graph topology, the coaching agent and its middleware, retrieval, tools,
validation and gates, reliability, operations, governance. They are
methodology-agnostic and bind on every agent.

**Part VIII is the DMAIC domain** and is Agent Improve's alone. Its own header
says so: *"Parts II–VII describe a coaching harness that is largely
methodology-agnostic. This Part is where DMAIC itself enters the schema."* When
Agent Resolve or Agent Flow are built to this reference, each brings its own
domain part; Part VIII is the worked example of what such a part contains, not
a constraint on the others.

> **Six sections are annotated inline** where a platform mechanism carries an
Improve-specific instantiation — §5, §6, §23, §30, §32, §35. Look for the
**Scope:** note under the status line. They are the seams to cut along when
this document is generalised.

**Two things follow, and both bind.**
>
> **Worked examples are Agent Improve's because it is the agent being built.**
> Where a section illustrates a rule with `improve_case_index`, `PhaseState`, or
> a Belt at a gate, the *rule* is platform-level and the *illustration* is
> Improve's. Do not read an example as scoping the rule to one agent.
>
> **File paths are relative to the agent's own root**, not to this document.
> `core/store.py` means `agent-improve/backend/core/store.py` for Improve and
> the equivalent under `agent-resolve/` for Resolve. Paths that are genuinely
> repo-root-relative — `.claude/hooks/`, `.claude/config/` — are written from
> the root and marked as such.

**It is written to be built against.** A reader should be able to implement an
agent from this document without reconstructing anything from memory or reading
a second file. Where a concept has a definition, that definition appears
**once**, in one canonical section, and everything else cross-references it.

**What this document is not.** It is not a learning register and not a review
log. The reasoning trail that produced these decisions — what a course taught,
what was corrected, which options were rejected and when — lives in
`agent-improve/docs/EDUCATIONAL.md` (the original chronological register),
`agent-improve/docs/REFACTORING_AGENT_IMPROVE.md` (the section-by-section
review), and `agent-improve/docs/REVIEW_DECISIONS.md` /
`agent-improve/docs/DECISIONS.md` (the decision log). Those remain the
historical record, and they live under `agent-improve/` because that is where
the work was done — not because their conclusions are Improve-specific. This
document states conclusions.

**Rationale is kept where it is load-bearing.** "Narrative scaffolding
removed" does not mean "reasoning removed." Where a design choice is
non-obvious — static edges rather than `Command` routing, the Store rather
than shared state keys, two graders rather than one — the reasoning is stated
here, because an implementer who does not understand *why* will reimplement
the thing the rule exists to prevent.

### The two-document division

| Document | Answers | Binding? |
|---|---|---|
| `agent-improve/CLAUDE.md` | **What the rule is.** Quoted in every implementation prompt | **Yes** |
| `AGENTIC_ARCHITECTURE_REFERENCE.md` (this file) | **How the system is shaped, and why.** Component design, schemas, contracts, sequencing | **Yes** |

**The asymmetry is deliberate and reflects the scope split above.** This
reference sits at the monorepo root because it is platform-level. `CLAUDE.md`
sits under `agent-improve/` because a constitution is per-agent — it quotes
rule numbers into that agent's implementation prompts, and its drift registry
guards that agent's code. **When Agent Resolve is built to this reference it
gets its own `CLAUDE.md`, not a share of Improve's.**

`agent-improve/ARCHITECTURE.md` was absorbed into this document, and on
2026-08-22 that path was **replaced by a copy of this file** — Agent Improve's
own architecture document, expected to diverge from this one as this one is
generalised across the three agents. **It is no longer a superseded tombstone.** Where this file and a `CLAUDE.md` describe the same thing, the
`CLAUDE.md` states the rule and this file states the design; neither restates
the other's job.

### Section numbering and provenance

This document renumbers. Sections here do **not** correspond to the 87-section
numbering of `REFACTORING_AGENT_IMPROVE.md`, nor to `ARCHITECTURE.md`'s
numbering. Each section carries a **Supersedes** line naming its sources, and
**Appendix A** is the reverse index: old reference → new section.

> **Path convention in `Supersedes` lines.** They name source documents
> unqualified — `REFACTORING_AGENT_IMPROVE.md`, `ARCHITECTURE.md`, `CLAUDE.md`,
> `DECISIONS`. **All of those live under `agent-improve/`**, where the work was
> done; they were written when this document sat beside them. Left unqualified
> rather than rewritten ~50 times, because they are provenance records pointing
> into one agent's history, not live cross-references. **Live cross-references
> elsewhere in this document are fully qualified from the repo root.**

### Reading conventions

| Marker | Meaning |
|---|---|
| **RATIFIED** | Settled. Implement as written |
| **RATIFIED — NOT YET APPLIED** | The decision is final; the live system does not reflect it yet. **Write code against current reality, not the target** |
| **DEFERRED** | Out of scope for v2.1, with a named promotion trigger. Appendix B |
| **UNVERIFIED** | Stated on reasoning that has not been tested against production evidence. Flagged deliberately |
| **BANNED** | Actively prohibited. Reintroducing it is a violation, not a preference |

---

# Part I — Orientation

---

## 1. What Agent Improve is

*Supersedes: REFACTORING §Purpose, §Overview Architecture; ARCHITECTURE.md §1.*

Agent Improve is a **DMAIC coaching agent for Lean Six Sigma practitioners**.
It coaches a Belt through the five phases of an improvement project — Define,
Measure, Analyse, Improve, Control — capturing what they produce at each phase
and holding a quality gate between phases that the Belt must explicitly
approve.

It is one of three agents on the AgentLean platform:

| Agent | Purpose | Status |
|---|---|---|
| **Agent Resolve** | Incident problem-solving | Production |
| **Agent Improve** | DMAIC coaching — **the agent this section describes**, and the first built to this reference | In refactor |
| **Agent Flow** | Flow / value-stream | Future |

### What makes it architecturally distinctive

**It is a long-running agent, not a chat session.** A DMAIC project runs for
weeks. The Belt closes their laptop mid-Measure and returns nine days later.
State must survive process restarts, and the accumulated conversation exceeds
any single context window. Almost every decision in this document follows from
that one fact — the checkpointer and store (Part II), context compression
(§19), the disconnect policy (§47) are all consequences of duration.

**It coaches; it does not do the work.** The Belt writes their own problem
statement. The system's job is to teach, challenge weak inputs, show worked
examples, and refuse to accept "poor morale" as a validated root cause. A
coach that fills in the Belt's fields produces complete gate documents and
worse projects — which is why the quality machinery (Part VII) is as large as
it is.

**It is a quality system, so the audit trail is a product requirement.** A
Belt must be able to show not just what their root cause was, but how it was
determined — what evidence, which methodology, what the system checked and
when. This is why `artifacts` and `step_log` are separate fields (§11), why
`citations` and `uploads` are tracked per phase (§6), and why grading verdicts
are per-criterion rather than a score.

**Uploaded data is the only external channel.** There are no live system
integrations, and there will not be. The full statement of that decision and
what follows from it is §29.1.

### The runtime stack

```
FastAPI                     API layer, SSE streaming
LangGraph  ≥1.2.6           graph runtime, checkpointing, interrupts
LangChain  1.x              create_agent, middleware, structured output
Azure OpenAI                gpt-4o (premium) / gpt-4o-mini (operational)
Azure AI Search             three indexes — methodology, evidence, case history
Azure Blob Storage          checkpoints, store, case records, uploads
Azure Cache for Redis       fallback chain level 3   [NOT YET PROVISIONED]
```

**MCP is not in this stack and is not deferred** — see §29.1.

**The LangGraph floor is ≥1.2.6, and the installed version is below it.**
As of 2026-08-21 the venv has `langgraph 1.1.10`. Per-node `TimeoutPolicy`,
`error_handler=` (Part IX) and the subgraph `checkpoint_ns` fix (§16) all
require ≥1.2.6 and are therefore **unavailable today**. Verified upgrade targets
are in §53; the previously documented 1.2.10 pin was already stale and has been
corrected.

**Graceful shutdown is a separate and weaker claim.** The mechanism named for
it, `RunControl.request_drain()`, is **UNCONFIRMED — MAY NOT EXIST** (§45). It
is not gated on the version upgrade; it is gated on the API being shown to
exist at all.

---

## 2. How to read this document

*Supersedes: REFACTORING §Document Navigation; ARCHITECTURE.md §0.*

### By what you are trying to do

| You want to… | Start at |
|---|---|
| Understand the shape before anything else | §3 Terminology, then §4 |
| Implement or change state | Part II — §5, §6, §7 |
| Implement or change the graph | Part III |
| Work on the coach, prompts, or middleware | Part IV |
| Work on retrieval or the indexes | Part V |
| Add or change a tool | Part VI |
| Work on gates, validation, or grading | Part VII |
| Work on phase content or gate documents | Part VIII |
| Work on failure handling | Part IX |
| Work on the API, UI, tracing, or evals | Part X |
| Understand why a rule exists | The **Supersedes** line, then the named source |
| Find where an old §-number went | **Appendix A** |

### Canonical ownership

To keep this document from drifting against itself, each of these facts has
exactly one home. Everything else cross-references it.

| Fact | Canonical home |
|---|---|
| `SupervisorState` | §5 |
| `PhaseState` | §6 |
| Field typing law | §7 |
| Store namespaces | §9 |
| Graph topology | §12 |
| The middleware stack | §19 |
| Azure AI Search index schemas | §23 |
| The `rag_lookup_*` tools | §24 |
| Tool inventory and per-phase binding | §30 |
| The four-layer validation stack | §34 |
| The five `{Phase}Output` schemas | §40 |
| **Class and function specifications** | **Part XII** |
| **The SPEC-GAP register** | **§66** |
| **Compliance posture and the risk register** | **Part XIII** |
| Deferred items and promotion triggers | Appendix B |
| Retired names and banned patterns | Appendix D |

**If you find the same fact stated twice with different content, the canonical
section wins and the other is a bug.** Report it rather than picking one.

---

## 3. Terminology

*Supersedes: REFACTORING §Terminology Reference.*

The words "agent," "subagent," "node," "subgraph," and "tool" are used
heavily and were used inconsistently in the source material. **These are the
authoritative definitions. Where any other wording differs, this section
wins.**

### Structural primitives

There are four, they come from LangGraph and LangChain, and every box in every
diagram in this document is one of them.

| Term | Definition |
|---|---|
| **Node** | A Python function in a `StateGraph`. Reads state, does work, returns a state-update dict. The atomic unit of execution |
| **Subgraph** | A compiled `StateGraph` embedded as a node in a parent graph. Has its own state schema and internal nodes; the parent sees only its input and output |
| **Tool** | A Python function bound to an LLM and invoked *by the model* at runtime, from inside a node. **Not a node** |
| **Middleware** | A LangChain `AgentMiddleware` attached to `create_agent` via `middleware=[...]`. Wraps the agent loop through six hooks. **Not a node and not a tool** |

**The distinction that matters most in practice: a tool is chosen by the
model; a node is reached by an edge.** This is why the validation stack is a
node and not a tool (§34) — as a tool, the coach would decide whether to be
validated, which is backwards.

### Role labels

Roles describe *responsibility*; they are not new primitives.

| Role | What it is |
|---|---|
| **Planner** | A node whose job is producing a structured plan. Never dispatches to tools |
| **Executor** | A node whose job is consuming a plan and dispatching. Never decides strategy |
| **Supervisor** | The Level 1 pair at the top of the hierarchy |
| **Phase subagent** | A Level 2 subgraph — Define, Measure, Analyse, Improve, Control |
| **Leaf tool** | A tool bound to a Level 2 executor. A plain function, never a Planner-Executor pair |

### The recursion is two levels, not infinite

| Level | Planner | Executor | Dispatches to | Mechanism |
|---|---|---|---|---|
| **1** | **Deterministic gate-check — not an LLM** | Router | Phase subgraphs | Static edges |
| **2** | `phase_planner` (LLM) | `phase_executor` (LLM + tools) | Leaf tools | Tool-calling loop inside the node |
| **3** | — | — | — | Tools are functions, not pairs |

**Level 1 has no LLM planner, and this is deliberate.** DMAIC order is fixed:
Define → Measure → Analyse → Improve → Control. There is nothing to reason
about, so nothing reasons. The Level 1 "planner" is a gate-check on
`gate_passed` plus static edges (§15).

**Recursion rule:** at every non-leaf level, *Planner reasons, Executor
dispatches*. An Executor's targets may themselves be Planner-Executor pairs —
that is what makes the pattern recursive. Only at the leaf do you find single
functions.

### "Harness" — two senses, do not conflate

**The harness is everything engineered around the model** — the graph, the
state schemas, the tools, the middleware, the validation stack, the
persistence layer. The model is the reasoning; the harness is the system.

| Sense | Meaning |
|---|---|
| **Architectural** | The whole control plane around the model — the entire application. This is the sense used throughout this document |
| **Library** | A specific agent-loop implementation. `create_agent` is described by LangChain as "a minimal agent harness"; deepagents as "a more opinionated harness on top of `create_agent`" |

In the library sense we chose the *minimal* harness and built our own
middleware on it (§18, §19). In the architectural sense, the harness is what
this entire document specifies.

### "Agent" — used carefully

Two meanings, both live:

- **LangChain sense** — an LLM with bound tools that decides which to call. In
  our code that is the Level 2 `phase_executor` node.
- **Multi-agent sense** — a named role. "Phase subagent" means the Level 2
  *subgraph as a whole*.

Where a source document says "subagent," read **subgraph**.

### Things that are deliberately not levels

Composition mechanisms are not architectural levels, and treating them as such
was a recurring error in the source material:

| Not a level | What it actually is |
|---|---|
| Middleware | A wrapper around the agent loop (§19) |
| Multi-query / RRF | Logic *inside* a retrieval tool (§25) |
| Multi-hop | The executor's tool-calling loop iterating (§26) |
| The validation stack | One node reached by an edge (§34) |
| The policy advisory | Logic inside `gate_apply` (§33) |

---

## 4. Architecture at a glance

*Supersedes: REFACTORING §Overview Architecture, Diagrams 1–4; ARCHITECTURE.md §1, §3.1.*

```
                          FastAPI  (/ask, /ask/stream, /gate/*)
                                        │
                                        ▼
              ┌──────────────────────────────────────────────┐
              │  supervisor_graph        SupervisorState (7)  │
              │  thread_id = case_id                          │
              │  checkpointer + store attach HERE only        │
              └──────────────────────────────────────────────┘
                    │ static edges — fixed DMAIC order
        ┌───────────┼───────────┬───────────┬───────────┐
        ▼           ▼           ▼           ▼           ▼
     define →   measure →   analyse →   improve →   control → END
        │
        │  each phase subgraph — PhaseState (17), no checkpointer
        ▼
   ┌───────────────────────────────────────────────────────┐
   │  planner ──► executor ──► validation_stack            │
   │     ▲            │              │                     │
   │     └────────────┴──────────────┘  retry, cap 3       │
   │                                 │                     │
   │                                 ▼                     │
   │                          gate_review  ── interrupt()  │
   │                                 │                     │
   │                                 ▼                     │
   │                          gate_apply ──► store write   │
   └───────────────────────────────────────────────────────┘

   Inside executor:  create_agent
                     + 8 middleware
                     + 7 universal tools + this phase's computation tools

   Persistence:      checkpointer → in-flight graph state (automatic)
                     store        → cross-phase artifacts (explicit)
                     case blob    → system of record (gate-pass only)
```

### The five things that shape everything else

1. **Two state schemas, two levels** — `SupervisorState` for orchestration,
   `PhaseState` inside each phase. Nothing else (§5, §6).
2. **Cross-phase data moves through the Store, never through parent state.**
   Subgraph state updates are not guaranteed to propagate to the parent; the
   Store is the documented fix (§9).
3. **One `thread_id` per project**, checkpointer on the parent only, subgraph
   namespacing auto-managed (§16).
4. **The coach is `create_agent` with eight middlewares**, never a bare LLM
   with bound tools (§18, §19).
5. **The gate is a nine-step human-in-the-loop sequence** with two distinct
   quality checks, and the checkpoint commits only after the Belt approves
   (§33).

---

# Part II — State and Persistence

*This Part is the foundation: every later Part reads or writes what is defined
here. It is deliberately first.*

---

## 5. `SupervisorState` — orchestration only

*Supersedes: REFACTORING §17; ARCHITECTURE.md §4.1; DECISIONS §A1.*
**Status: RATIFIED.** File: `core/state.py`.
> **Scope:** the mechanism is platform; the instantiation below is Agent Improve's — the two-level state split and the seven-field ceiling bind on every agent; the field *names* are Improve's


**Specification:** the canonical schema and its field table are **§57.2 — S-C01**.
This section keeps the reasoning.

**Seven fields. That is the entire schema.** An eighth requires an amendment.

### `gate_passed` is a dict, not a list

`gate_passed["measure"]` is a direct lookup, and the re-approval cascade (§37)
sets a phase back to `False` rather than removing it from a list — a removal
that would have to be conditional on the phase being present. The dict form
makes both operations total.

### `current_phase` and `phase_index` are derived, and kept anyway

Both are computable from `gate_passed`. They are stored regardless, as a
**documented exemption for readability** — they are read in dozens of places
and computing them at each site would be worse.

**The exemption is safe only because they have exactly one writer.** The
output mapper at gate approval writes all three orchestration values together
(§9). **Nothing else may write them.** A second write site is what turns a
derived field into a second source of truth that can disagree with the thing
it was derived from.

### Four fields were removed as redundant, and may not return

| Removed | What covers it instead |
|---|---|
| `dmaic_plan` | DMAIC order is fixed and static (§15) — there is no plan to store. The project's actual plan is Define's gate document in the Store |
| `key_decisions` | A decision the Belt commits is a captured field, arriving via `CoachingResponse.fields_captured` and approved at a gate. A decision not worth a field is not worth replaying into every prompt |
| `open_items` | Outstanding work is **derived**: `check_gate_status()` reports unpopulated required fields, and the validation stack surfaces blockers |
| `project_context` | Composed at the boundary by each input mapper (§9) |

**Deriving these is what keeps them correct.** A stored `open_items` list is a
second source of truth for gate readiness that can disagree with
`DMAICGateValidator`; a derived one cannot.

`project_context` deserves its own note, because it failed in an instructive
way: **it had no writer at all.** Its comment said "set once after Define,"
yet nothing set it, and its only reader — `define_input_mapper` — runs *before*
Define. The check that catches this class of field is cheap and worth applying
to any proposed eighth field: **name the node that writes it and the node that
reads it.** If either answer is vague, the field is wrong.

### Artifacts are not here

**Captured fields and gate documents are NOT on `SupervisorState`.** They live
in the Store (§9). Adding them back is a violation — see §9 for why this is
structural rather than stylistic.

---

## 6. `PhaseState` — per-phase subgraph state

*Supersedes: REFACTORING §18; ARCHITECTURE.md §4.2; DECISIONS §A2.*
**Status: RATIFIED.** File: `core/substate.py`.
> **Scope:** the mechanism is platform; the instantiation below is Agent Improve's — one private state per subgraph, typed, checkpointed, is platform; `belt_edits`, `gate_attempts` and the DMAIC-facing names are Improve's


**Specification:** the canonical schema and its field table are **§58.2 — S-C02**.
This section keeps the reasoning.

**Seventeen fields — three plumbing plus fourteen content.** A fifteenth
content field requires an amendment.

### `draft`, `belt_edits` and `final` are `dict`, never `str`

String-typed handoffs force downstream nodes to parse prose out of an upstream
node's output. That is the anti-pattern this architecture exists to remove, and
`final` in particular is a structured gate document by construction (§33).

### `coaching_plan` is one typed plan, not a queue

**One plan per planner turn, overwritten each time the planner fires.** There
is no upfront queue: the subgraph is a *cycle*, the planner fires many times
per phase, and a plan made at turn 1 cannot anticipate turn 4. The planner
reads `artifacts` to know what is captured and what is next — that is the
queue, derived rather than stored.

**Specification:** `CoachingPlan` is defined once, at **§58.4 — S-C04**. It is a Pydantic
model produced by the builder-style structured-output call on the model.

A plain dict cannot be validated at planner-output time, and
`retrieval_strategy` needs its `Literal` constraint specifically: it selects
the executor's entire retrieval path, and a typo would fall through silently to
single-hop. Read `coaching_plan.retrieval_hops`, never
`coaching_plan["retrieval_hops"]`. `dict[str, Any]` is acceptable as an
interim annotation inside the `TypedDict`; typed is preferred.

**The plan is transient; its consequences are durable.** Captured values land
in `artifacts`, sources in `citations`, the planner's rationale in `step_log`,
the conversation in `messages`, and the full LLM exchange in the LangSmith
trace. Nothing is lost when the next plan overwrites this one.

### `gate_attempts` — the field whose absence recreated a production bug

It is the shared retry counter for the four-layer validation stack (§34):
incremented per failed attempt, reset to `0` when the gate passes, routing to
escalation at `>= 3`.

**It must be on `PhaseState` and therefore in the checkpoint.** v1 held the
equivalent counter in route scope, so every request rebuilt it at `0`, the cap
never fired, and the loop reported attempt 1 indefinitely. Holding it in route
scope is not a style question — it is the specific defect this placement fixes.

**It is per phase, not per supervisor.** Each phase runs its own validation
loop with its own budget of 3. A supervisor-level counter would let a difficult
Measure phase consume the retries Analyse needs, and the two have nothing to do
with each other.

### `validator_feedback` and `belt_edits` are different, and must stay separate

| Field | Written at | By | Read by |
|---|---|---|---|
| `validator_feedback` | Step 2 of the gate | The four validation layers | The coach, on retry |
| `belt_edits` | Step 5 of the gate | The Belt | `gate_apply_node`, at steps 6–7 |

**Two actors, two moments** (§33). A single `feedback` field conflating them
would have the coach reading the Belt's corrections as validation failures —
the Belt fixing a value would look to the coach like the system rejecting it.

**Accumulation is the entire point of `validator_feedback`.** Each failed
attempt appends:

**Specification:** the entry shape is in **§58.2 — S-C02**.

The coach reads the full list on retry. **The shared cap of 3 is defensible
only because each attempt is better informed than the last** — a cap on
retries that carry no memory of the previous failure is just a cap on
repetition, and this field is what carries the memory.

### `citations` and `uploads` — the evidence trail

**Specification:** both entry shapes are in **§58.2 — S-C02**.

Both are written into the gate document (§33). Without them the document
cannot show what the phase was grounded in, and §50 requires citation
transparency down to `source_file` and `page_number`.

**`uploads` carries more weight than it looks.** Because
`improve_evidence_index` is the only channel through which external data
enters the system (§29.1), the upload list *is* the complete record of what
real-world evidence the phase had. **A phase with an empty `uploads` list
reached its conclusions from the Belt's typed statements alone, and a reviewer
should be able to see that.**

`evidence_index_id` is what makes the trail traversable: a reviewer reading the
approved gate document can follow it back to the indexed chunk.

### `hop_results` and `synthesis_output` must be state, not node locals

Both carry the Analyse planned multi-hop chain (§26).

**A local Python variable inside a node is not inspectable.** LangSmith traces
node inputs, node outputs and tool calls — not interpreter locals. Hop results
held in a local dict are invisible in the trace *and* lost on checkpoint
restore, which makes the claim "planned multi-hop is fully inspectable" false.
Returned into state they appear in the state diff per node invocation and
survive a resume.

`synthesis_output` holds the dedicated synthesis call's `SynthesisOutput` so
the coach call reads it from state rather than from a local variable.

**Both are `[]` / `None` on every single-hop turn in every phase.** They are
declared on `PhaseState` rather than an Analyse-only variant because
`CoachingPlan.retrieval_strategy` may select `multi_hop` in any phase.

### Per-phase variants

`DefineState`, `MeasureState`, … extend `PhaseState` with phase-specific
transient fields. **All use explicit `TypedDict`, not `MessagesState`
inheritance** — their dominant content is structured fields, not conversation.
`MessagesState` inheritance is appropriate only where the dominant content
genuinely is conversational exchange, which in this architecture is the
deferred debate subgraph (Appendix B, item 10) and nothing else.

### Naming discipline

`phase_index` (which phase) and `field_index` (which field within a phase) are
distinct and must not be conflated. **Never reintroduce `step_index`** — the
ambiguity between the two is exactly what the rename removed.

---

## 7. Field typing law — every captured field is a string

*Supersedes: REFACTORING §10.6-equivalent; ARCHITECTURE.md §4.6, §4.7, §4.8; DECISIONS §A5, §A6.*
**Status: RATIFIED.**

**All captured fields are `str`.** No phase schema declares a typed numeric.

```python
baseline_mean = "12.3% invoice error rate, measured over Q2 2026"
```

**Computation tools parse at the point of use.** Each of the 20 (§30) extracts
what it needs from the string it is given, and returns a clear reformatting
request to the Belt when it cannot.

### Why strings

**The gate document shows the Belt's exact words.** That is a requirement of a
quality system: the Belt must be able to show what they stated, not what the
system parsed out of it. A stored `12.3` has already discarded "invoice error
rate," "measured over Q2 2026," and the Belt's own framing — and those are the
parts a reviewer needs.

The alternative designs were considered and rejected: a typed numeric loses the
context, and a triple of (raw, value, unit) triples the schema size for roughly
25 numeric fields across DMAIC — schema explosion in exchange for parsing that
each tool has to do anyway.

### The one exception — three cross-phase reference dicts

| Field | Phase | Links |
|---|---|---|
| `causal_hypothesis` | Analyse | Root cause → Measure baseline |
| `solution_linked_to_root_cause` | Improve | Solution → Analyse root cause |
| `post_improvement_metric` | Control | Result → Measure baseline |

Each carries the Belt's content plus three reference keys:

**Specification:** the canonical shape of all three is **§63.6 — S-C32**.

**The dict exists so the grader can verify the link deterministically.** It
reads the referenced phase's gate document from the Store and checks the named
field carries the named value — no LLM judgment in the linkage check. Without
the reference keys, "does this solution address the validated root cause?" is
an opinion; with them it is a lookup.

**The values inside the dict are still strings.**

### Computation results

**Computation tool output goes in `artifacts["computation_results"]`** as a
list of typed dicts, all values strings:

```python
artifacts["computation_results"] = [
    {"tool": "t_test",
     "inputs":  {"sample1": "new_staff_errors", "sample2": "experienced_staff_errors"},
     "result":  {"t_statistic": "4.23", "p_value": "0.001", "significant": "yes"},
     "turn": 7, "phase": "analyse"}
]
```

**No new top-level `PhaseState` field, and no per-phase typed destinations.**
The grader answers "was a hypothesis test run?" by scanning that list for
`"tool": "t_test"`. Adding typed per-phase computation fields is a violation:
it multiplies schema surface for a question a scan already answers, and it puts
the same result in two places.

---

## 8. The checkpointer / store split

*Supersedes: REFACTORING §1, §52, §52a; ARCHITECTURE.md §6.1, §6.2.*
**Status: RATIFIED.**

**Two persistence systems, not one.** They are distinct LangGraph primitives
serving different lifecycles, and **passing only a checkpointer is the single
most common architecture mistake** in LangGraph applications.

| | Checkpointer | Store |
|---|---|---|
| Scope | Thread-scoped — one project | Cross-thread, cross-phase |
| Lifecycle | **Automatic** — LangGraph writes after every node | **Explicit** — nodes call `put` / `get` |
| Carries | In-flight graph state | Durable cross-phase artifacts |
| Injected | `graph.compile(checkpointer=...)` | `graph.compile(store=...)` + node parameter |

**The asymmetry is deliberate:** conversation history is structural, so
LangGraph manages it; long-term memory is a product decision, so we write the
code.

**Both attach to the parent graph ONLY.** Phase subgraphs compile with
neither (§16).

### Phased backend

| Stage | Checkpointer | Store |
|---|---|---|
| During the refactor | `AzureBlobCheckpointSaver` | `AzureBlobStore` |
| Post-refactor, pre-production | `PostgresSaver` | `PostgresStore` |

**`InMemorySaver` is not used at any stage, including development.**

**Migration is a constructor and connection-string change.** Both sides are
defined by LangGraph interfaces, so nothing above the persistence layer
changes. Run the existing unit tests against PostgreSQL before switching.
Tracked as Appendix B item 13.

**Known limitation, stated plainly:** the Blob checkpointer was **not tested
for concurrent access**, and Azure Blob has no row-level locking. This is
acceptable for single-developer refactoring and is **not** acceptable for
production. Do not defend it past the migration trigger. The interim guard is
the Blob lease in §47.

### Concurrency and atomicity

**One blob write per checkpoint** — never per key — and **atomic via blob ETag
conditional writes**: concurrent turns on the same case are detected, and the
second writer retries rather than overwriting. This is a *mitigation*, not a
solution; it is what the `PostgresSaver` migration replaces properly.

**Gate-pass case blob write and registry update remain two separate writes**,
both covered by the node's `error_handler` (Part IX). That handler is the
ratified answer to what v2.1.1 carried as "Saga pattern for case-vs-registry
atomicity — deferred"; there is no Saga framework to write (§45).

### Why Blob, and not Cosmos / Tables / SQLite

The question was asked and settled; it is recorded so it is not re-opened
without new constraints.

- **Already provisioned, secured and monitored** — no new service to operate
- **A single Azure SDK dependency**, shared with case records and uploads (§10)
- **Append-only checkpoint history**, which makes time-travel debugging a blob
  listing rather than a query
- **`BaseCheckpointSaver` / `BaseStore` are the real portability layer** — the
  PostgreSQL migration is a constructor change either way, so picking the
  cheaper backend first costs nothing later

Note what is *not* on that list: concurrency. Blob was chosen despite it, with
the limitation above stated rather than designed around.

### On-blob checkpoint format

```json
{
  "checkpoint_type": "msgpack",
  "checkpoint_data": "<base64-encoded msgpack bytes>",
  "metadata_type":   "msgpack",
  "metadata_data":   "<base64-encoded msgpack bytes>",
  "checkpoint_id":   "<id>",
  "parent_checkpoint_id": "<id|null>"
}
```

The base64 wrapping is **required**, not decorative:
`JsonPlusSerializer.dumps_typed()` (`langgraph-checkpoint` 4.x) returns binary
msgpack rather than utf-8 text. Wrapping in base64 keeps the blob a valid JSON
document while preserving exact round-trip semantics. This is a real deviation
from the original spec, discovered during implementation.

---

## 9. The Store — cross-phase artifacts and boundary mappers

*Supersedes: REFACTORING §19, §44 (Mechanism 3), §52a; ARCHITECTURE.md §4.3, §6.3; DECISIONS §A7, §O1.*
**Status: RATIFIED.** File: `core/store.py`.

**Specification:** **§58.6 — S-C06**.

> **`BaseStore.search()` is more capable than earlier revisions of this design
> assumed** (verified 2026-08-21). Beyond `query` and `filter` it supports
> `mode` (`text` | `vector` | `hybrid` | `auto`), `offset`,
> `similarity_threshold`, `vector_weight` and `distance_metric`.
>
> **This weakens one of the three reasons previously given for keeping
> `improve_case_index` on Azure AI Search.** The old argument was that the
> Store provides neither metadata filtering, nor hybrid BM25 + vector scoring,
> nor multi-query + RRF. The first was already corrected — `filter=` exists —
> and `mode="hybrid"` now undercuts the second.
>
> **The conclusion still holds, on the remaining reason plus migration cost:**
> the Store has no multi-query + RRF (§25), which is the mechanism Agent
> Resolve production experience showed this corpus needs, and moving a live
> index is work with no user-visible payoff. **But the decision now rests on
> one technical reason rather than three, and should be re-examined if the
> Store's search surface keeps growing.** Flagged rather than quietly left to
> look better-supported than it is.

### Namespace convention

```
("projects", case_id, <kind>)
```

| Namespace | Keys | Contents |
|---|---|---|
| `("projects", case_id, "case")` | `"record"` | Case framing — title, department, belt level, leader, target date. Written **once** at session start, never mid-conversation |
| `("projects", case_id, "artifacts")` | `"define"`, `"measure"`, … | **Each phase's approved gate document**, written by `gate_apply_node` (§33) |
| `("projects", case_id, "step_log")` | timestamped | Append-only cross-phase audit trail |

**Blob prefix:** `store/projects/{case_id}/{kind}/{key}.json`
`case_id` is the same value as the graph's `thread_id` (§16).

**The `gate_documents` namespace is retired.** A phase's approved artifacts and
its gate document are the same object; two keys holding the same content poses
a question about which is authoritative that has no answer. Reintroducing it is
a violation.

**The `case` namespace is a session-start copy, not a second system of
record.** `cases/case_{id}.json` (§10) stays authoritative. The store holds the
framing fields so that mappers depend on `BaseStore` alone.

### Why cross-phase data cannot travel on parent state

This is the decision most likely to be reimplemented wrongly, so the reasoning
is stated rather than assumed.

**Subgraph state updates are not guaranteed to propagate to the parent
immediately.** Each subgraph manages its own checkpoint namespace, and this is
documented LangGraph behaviour, not a bug. The documented fix is shared state
via the Store.

There is a second, independent reason: **a DMAIC project spans weeks.** Define
completes in one session; Measure reads Define's output in a session nine days
later, after a process restart. In-graph mechanisms — shared state keys,
transformer functions — move data *within one graph invocation*. They cannot
carry a value across a gap where the process itself ended.

**Three boundary mechanisms exist, and only one crosses a phase boundary:**

| | Shared key names | Transformer functions | **The Store** |
|---|---|---|---|
| Moves data | Parent ↔ child, same graph | Parent ↔ child, same graph | **Phase → phase, across invocations** |
| Survives restart | No | No | **Yes** |
| Used for | Inside a subgraph | Inside a subgraph | **Every phase boundary** |

Shared keys and transformers remain correct for what they are — moving values
between a phase subgraph and its own internal nodes. **They are simply not
boundary mechanisms**, and a reference implementation that used shared key
names to carry `define_output` to the parent was the specific error this
section exists to prevent.

### Boundary mappers

Two plain functions per phase, in `phases/{phase}/mappers.py`.

**Specification:** both mappers are defined at **§58.19 — S-F10** and **§58.20 — S-F11**;
the four remaining pairs are **§58.21 — S-F12**.

**The three orchestration values advance together, from this one site.** That
single write point is what makes the derived-field exemption in §5 safe.

**Every input mapper composes `phase_context` from the Store.** Define reads
the case record; Measure, Analyse, Improve and Control read the prior phase's
artifacts. **The rule is uniform, and the uniformity is what makes it safe:**
an input mapper's only dependency is `BaseStore`, so there is no parent-state
field to keep current and no phase whose context goes stale because a write was
missed.

**An input mapper's only dependency is `BaseStore`.** Reading context off
parent state creates a parent field to keep in sync; handing a mapper a blob
client puts untracked I/O in a translation function. Both are violations.

### Two prohibitions that follow

**String-interpolating a previous phase's output into the next phase's prompt
is BANNED.** Measure reads Define's baseline metric as a named field out of a
structured gate document, not out of prose. Note the field's *value* is a
string (§7) — the prohibition is on parsing a value out of an interpolated
prompt, not on the value's type.

**The Store is not the case index.** Cross-*case* retrieval for yokoten is
`rag_lookup_case_history` against `improve_case_index` (§24). The Store carries
cross-*phase* data within one project. Two mechanisms, two purposes, no
overlap.

### Ordering constraint

**Implement the Store after `thread_id` is wired through `graph.ainvoke`.** A
store is meaningless without working checkpoint persistence — if the graph
cannot resume, there is no second session for stored artifacts to serve.

---

## 10. Azure Blob — two distinct concerns

*Supersedes: REFACTORING §1; ARCHITECTURE.md §6.2, §6.4, §6.5.*
**Status: RATIFIED.**

Same storage account, two separate concerns, two separate code paths.

**Concern 1 — checkpoints (in-flight graph state)**
- Path: `checkpoints/{case_id}/latest.json` + `history/{checkpoint_id}.json`
- Written by `AzureBlobCheckpointSaver` after every graph node
- Owner: `core/checkpointer.py`

**Concern 2 — case records (system of record)**
- Path: `cases/case_{id}.json`, `registry.json`, `uploads/{case_id}/{file}`
- Written on case create, on gate pass, on file upload — **never
  mid-conversation**
- Owner: `storage/blob.py` via `ImproveBlobClient`

### Complete physical layout

```
Azure Blob container: agent-improve-cases

store/projects/{case_id}/case/record.json
store/projects/{case_id}/artifacts/define.json
store/projects/{case_id}/artifacts/measure.json
store/projects/{case_id}/artifacts/analyse.json
store/projects/{case_id}/artifacts/improve.json
store/projects/{case_id}/artifacts/control.json
store/projects/{case_id}/step_log/{timestamp}.json

checkpoints/{case_id}/latest.json
checkpoints/{case_id}/history/{checkpoint_id}.json

cases/case_{case_id}.json                    ← system of record
registry.json
uploads/{case_id}/{file}
```

Each `artifacts/{phase}.json` holds the complete approved gate document for
that phase: captured fields as strings (§7), the cross-phase reference dicts
where they apply (§7), `computation_results`, `citations`, `uploads`, and
`acknowledged_gaps` (§35).

### The case blob is not updated per turn

**The v1 pattern of overwriting `case_{id}.json` on every `/ask` is REMOVED.**
Conversation history lives in the checkpoint until gate pass. Writing the
system of record on every conversational turn conflates in-flight state with
committed state — and the checkpoint already does the first job better.

**Case-vs-registry atomicity:** the gate-pass case blob write and the registry
update remain two separate writes. Both are covered by the node's
`error_handler` (Part IX).

---

## 11. `step_log` — the audit trail

*Supersedes: REFACTORING §18 (step_log); ARCHITECTURE.md §4.4.*
**Status: RATIFIED.**

Every audit entry is a **dict with named keys. Tuples are BANNED** — field
names make the log self-documenting and queryable.

```python
{"layer": "constraint", "attempt": 2, "status": "failed",
 "reason": "does not address timeline", "decision_excerpt": "..."}

{"service": "gpt-4o", "attempt": 2, "status": "failed",
 "reason": "timeout after 45s", "timestamp": "..."}
```

**Everything requiring an audit trail writes here:** the four validation layers
(§34), each grader iteration via `on_evaluation` (§36), and every fallback
attempt (Part IX).

### `artifacts` and `step_log` are separate fields and stay separate

- **`artifacts` = WHAT was captured** — the results
- **`step_log` = HOW it was captured** — the audit trail

For a DMAIC quality system the Belt must be able to show not just what the root
cause was, but how it was determined. v1 mixed them: `captured_fields` held
results with no separate record of how each was captured, which meant the
"how" existed only in conversation prose.

### Entries carry deterministic keys, never a raw timestamp as identity

```python
step_key = f"{phase}:{turn_count}:{step_name}"     # "analyse:7:constraint_check"
```

A timestamp is still recorded as *data* — it is just not what identifies the
entry.

**This matters once checkpoints are live.** A turn that is retried, resumed
from a checkpoint, or replayed after a client disconnect re-executes the same
logical step. A timestamp-keyed log records that as two separate events; a
deterministic key makes the write idempotent, so the replay overwrites its own
earlier entry instead of duplicating it. Without this, `step_log` inflates on
every retry and stops being evidence of what happened.

This is a hard requirement of the disconnect policy (§47).

---

# Part III — The Graph

*The graph is the orchestrator. Nothing outside it dispatches work.*

---

## 12. Topology

*Supersedes: REFACTORING §23, §44; ARCHITECTURE.md §3.1.*
**Status: RATIFIED.** Files: `core/graph.py`, `phases/{phase}/graph.py`, `escalate.py`.

```
supervisor_graph                    thread_id = case_id, e.g. "IMPR-2026-FS1"
├── define_subgraph                 checkpoint_ns auto-managed by LangGraph
├── measure_subgraph
├── analyse_subgraph
├── improve_subgraph
├── control_subgraph
└── escalation_subgraph             reached by conditional edge
```

- One supervisor graph in `core/graph.py`
- One subgraph per phase in `phases/{phase}/graph.py`
- One escalation subgraph in `escalate.py`
- The supervisor compiles all subgraphs into a hierarchical compiled graph

**The compiled graph is the ONLY runtime path.** `/ask`, `/ask/stream` and
`/gate/*` all invoke the same compiled graph object. A route that does anything
beyond `await graph.ainvoke(...)` / `astream_events(...)` plus envelope
marshalling is a violation (§49).

**Entry is declared with `add_edge(START, ...)`.** `set_entry_point` is
superseded and must not be used.

### The subgraph builder takes the phase as a parameter

It must, because it selects that phase's computation-tool subset (§30):

**Specification:** **§58.11 — S-F02**.

**The `compile()` call takes neither checkpointer nor store.** That is not an
omission — see §16.

---

## 13. The phase subgraph — five nodes

*Supersedes: REFACTORING §23; ARCHITECTURE.md §3.2, §3.3.1; DECISIONS §B1.*
**Status: RATIFIED.**

Each phase subgraph contains **exactly five nodes**.

| Node | Responsibility |
|---|---|
| `planner` | Produces a structured `CoachingPlan` — focus field, next action, retrieval strategy (§17) |
| `executor` | `create_agent` with this phase's tool subset; runs the coaching turn (§18) |
| `validation_stack` | The four layers, shared cap of 3 (§34) |
| `gate_review` | `interrupt()` — presents validated fields to the Belt and stops (§33) |
| `gate_apply` | Applies Belt edits, runs the policy advisory, assembles and writes the gate document, routes on (§33) |

```
                     ┌──────────────────────────────────────────────┐
                     │                                              │
                     ▼                                              │
              ┌──────────────┐                                      │
   START ────▶│   planner    │◀─────────────────────────┐           │
              └──────┬───────┘                          │           │
                     │ coaching_plan (typed — §17)      │           │
                     ▼                                  │           │
              ┌──────────────┐                          │           │
              │   executor   │  create_agent            │           │
              │              │  ReAct loop, ≤5 hops     │           │
              │  ┌────────┐  │  capped by RemainingSteps│ not clean │
              │  │ tools  │  │  7 universal +           │           │
              │  │  8–15  │  │  phase computation       │           │
              │  └────────┘  │                          │           │
              └──────┬───────┘                          │           │
                     │ draft (dict)                     │           │
                     │                                  │           │
        ┌────────────┴─────────────┐                    │           │
        │ conditional edge         │                    │           │
        │                          │                    │           │
   field complete? ── no ──────────┴────────────────────┘           │
        │ yes                                                       │
        │ more fields? ── yes ── field_index++ ─────────────────────┘
        │ all captured
        ▼
  ┌─────────────────────┐
  │ validation_stack    │  §34 — layers 2b/2c/2d, cheapest first
  │  2b field presence  │  shared cap: 3 attempts (gate_attempts)
  │  2c constraints     │  Layer 2a is middleware, not here — §34
  │  2d PHASE_RUBRIC    │
  └──────────┬──────────┘
     fail    │    pass
  ┌──────────┘          ▼
  │            ┌──────────────────┐
  │            │   gate_review    │  interrupt() — Belt sees fields
  │            └────────┬─────────┘
  │                     │ Command(resume=...)
  └──▶ back to planner  ▼
       (validator_ ┌──────────────────┐
        feedback)  │   gate_apply     │
                   │ · apply edits    │
                   │ · policy advisory│
                   │ · assemble doc   │
                   │ · store.put()    │
                   │ · final = doc    │
                   └────────┬─────────┘
                            ▼
                           END   (parent's static edge advances the phase)
```

### The subgraph is a cycle, not a pipeline

**The planner fires many times per phase, not once.** After each executor step,
control returns to the planner to decide whether to keep coaching the current
field, advance to the next, or trigger the gate. That cycle is why LangGraph
rather than a DAG engine is the runtime — a DAG cannot express "go back and try
this field again with what you just learned."

### Two node names are BANNED

| Retired | Ratified | Why |
|---|---|---|
| `policy_advisory` | — | The policy advisory is **logic inside `gate_apply`**, not a node. It runs after the Belt edits, when the coach is no longer in the loop |
| `revise` | — | Revision is an **edge**. The validation stack routes back to the planner carrying `validator_feedback` |

**The mid-phase contradiction check is also not a node.** Earlier revisions
drew it as a sixth box between the executor and the validation stack. It is
`ContradictionDetectionMiddleware` on the `after_agent` hook (§19) — it polices
the executor's own output, so it does not belong to the thing it polices, and
as middleware it is a named, LangSmith-visible step.

### Leaf tools are NOT subgraph nodes

The universal seven (§29) and the phase's computation tools are passed to the
executor via `tools=` on `create_agent`. **From the subgraph's perspective the
executor is one node.** The tool-calling loop happens inside it.

### The validation stack and the policy advisory are NOT tools

| Component | What it is | Why not a tool |
|---|---|---|
| Validation stack | A **node**, reached by an edge | As a tool, the coach would decide whether to be validated — backwards |
| Policy advisory | **Logic inside `gate_apply`** | It runs after the coach's turn is over |

**Adding either to a tool list is a violation.**

**New node types may not be added to a subgraph without an amendment.**

---

## 14. Node contract

*Supersedes: REFACTORING §21; ARCHITECTURE.md §3.2.*
**Status: RATIFIED.**

Nodes are **module-level async functions**:

**Specification:** `phase_executor` itself is the calibrated function sample at
**§57.3 — S-F04**. The contract below is cross-cutting and stays here.

| Rule | Detail |
|---|---|
| **Async** | Every node is `async def`. **Per-node timeouts require async nodes** — a hard LangGraph constraint, not a preference (Part IX) |
| **Returns dict slices** | Never a Pydantic model, never full state |
| **Structured handoffs** | Plans and drafts crossing nodes are structured, never prose parsed downstream |
| **Naming** | File name and function name align. One file may hold several nodes of the same subgraph |
| **No classes** | Node files contain module-level functions only |

**Synchronous code is permitted only in pure functions with no I/O** — prompt
building, state transformations, validation logic, and all 20 computation
tools (§30).

### Reflection is a node, not a private function

`_reflect()` inside orchestrate files is **BANNED**. Reflection is a graph node
reached via a conditional edge; the edge decides whether it is needed based on
response length, risk keywords (numbers, commitments, dates), and
phase-specific rules.

**For *invisible* retry — mechanical, not a coaching event — use the retry
middleware instead** (§19). A retry that the Belt should never see does not
belong in the graph topology.

---

## 15. Routing — static edges and `Command`

*Supersedes: REFACTORING §44; ARCHITECTURE.md §3.1.*
**Status: RATIFIED.**

### The decision test

> *"Could this transition vary at runtime?"* → **dynamic**, use `Command`.
> *"Always exactly once, in this order?"* → **static**, use `add_edge`.

**Phase transitions are static.** DMAIC order is fixed:

**Specification:** the supervisor wiring is **§58.10 — S-F01**; the undesigned Level 2
routing is **§58.22 — S-F13**.

There is nothing to reason about, so nothing reasons. An LLM call to choose the
next phase would be cost and latency purchasing no decision. **The v2.1
`phase_router` node is deleted.**

**`Command` routing is for inside phase subgraphs only**, where step order
genuinely is data-dependent — which field to coach next, whether to retry,
whether to trigger the gate.

### Never mix static edges and `Command` from the same node

**Both paths execute, silently.** This is the failure mode that makes the rule
absolute rather than stylistic: there is no error, no warning, and the symptom
appears far from the cause.

### Level 1 does not route — it advances

**The supervisor makes no decision at a phase boundary.** The six `add_edge`
calls above are the complete Level 1 wiring; there is no conditional edge, no
router function, and nothing for the supervisor to branch on.

**Why that is safe, rather than a simplification that ignores gate failure:**

> **A phase subgraph reaches `END` only through `gate_apply`, and `gate_apply`
> runs only after Belt approval** (§33). **Reaching `END` therefore *means* the
> gate passed.** A failing gate never arrives at the supervisor — it loops back
> to the planner inside the subgraph, or exits sideways to escalation (§13).

**Retry and escalation are resolved inside the phase**, never above it:

| Concern | Where it lives |
|---|---|
| Retry after a failed validation layer | §13's conditional edge — `validation_stack` → fail → back to the planner with `validator_feedback` |
| The attempt counter | `PhaseState.gate_attempts`, incremented by the validation stack, reset by `gate_apply` (§6, §35) |
| Escalation at `>= 3` | A conditional edge **from inside the phase** to the escalation subgraph (§38), which defers to the Belt and **never returns to the supervisor** |

**`gate_attempts` is read only inside the phase. It is not on
`SupervisorState`** (§5, seven fields) **and must not be added to it.** Holding
it in route scope is a banned pattern (Appendix D.2).

> **A `route_after_phase` function was deleted from this section on
> 2026-08-22.** It returned `"next"` / `"escalate"` / `"retry"` — labels wired
> to nothing — and read `state["gate_attempts"]` off `SupervisorState`, where
> that field does not exist, so it would have raised `KeyError` **on the
> gate-failure path specifically.** It was a fossil of an abandoned design in
> which the supervisor owned retry and escalation; that responsibility moved
> into the phase subgraph and the function was never removed. **Do not
> reinstate it.** Full record: `agent-improve/docs/DECISIONS.md` §R2.

### No subgraph imports another subgraph's nodes

Phases communicate through the Store (§9) and through the parent's edges.
A direct import creates a dependency the graph does not model.

---

## 16. `thread_id`, `checkpoint_ns`, and where persistence attaches

*Supersedes: REFACTORING §23, §44; ARCHITECTURE.md §3.1, §6.1.*
**Status: RATIFIED.**

### One `thread_id` per project

**Specification:** **§58.10 — S-F01**.

**`thread_id` is the `case_id` value.** Never per phase, never concatenated —
`{case_id}-define` and similar are **BANNED**.

**Multiple parallel cases are supported from day one, and this is what makes
that work.** Each case carries its own `IMPR-YYYY-NNN` identifier, and that one
value is simultaneously its checkpoint thread, its store namespace segment
(§9), its case blob path (§10) and its `case_id` index field (§23) — so two
Belts on two projects share no state at any layer without a single
multi-tenancy mechanism being written. What is *not* yet solved is two writers
on **one** `case_id`; that is the concurrency exposure named in §8 and guarded
in §47.

### The checkpointer and store go on the parent graph ONLY

**Specification:** **§58.10 — S-F01** and **§58.11 — S-F02**.

**Phase subgraphs compile with neither.** LangGraph routes their writes through
the parent's saver, distinguished by an **auto-managed `checkpoint_ns`**. Each
subgraph gets its own namespace within the shared thread.

**Why per-subgraph `thread_id` is wrong**, since this was attempted three times
in the source material before being settled: it causes duplicate storage and
state-persistence problems. Interrupts inside subgraphs work correctly through
the parent's checkpointer, namespaced by `checkpoint_ns` — there is no problem
that a second thread id solves.

### `recursion_limit` is a backstop, not the hop cap

**Set it high (50) on the supervisor invocation** to catch genuine infinite
loops. It does **not** control the per-turn hop budget — that is
`RemainingSteps`, read inside the executor node (§26).

The reason matters, because `recursion_limit=11` was previously ratified as the
hop cap and fails in two opposite directions in a hierarchy:

| Failure mode | What happens |
|---|---|
| Shared counter | Subgraphs draw on the parent's step budget; supervisor and routing steps consume it before the executor's first tool call, so the executor gets **fewer** than 5 hops |
| Non-propagation | `recursion_limit` is not passed to the subgraph at all, which reverts to its default of 25 — the cap is **absent** |

Which one you get depends on configuration. Neither reliably yields 5 hops, and
both terminate the graph with `GraphRecursionError` rather than letting the
coach close out gracefully.

---

# Part IV — The Coaching Agent

*Everything in this Part runs inside one node — the `executor` of §13.*

---

## 17. The Planner / Executor contract

*Supersedes: REFACTORING §5, §11, §20; ARCHITECTURE.md §3.5; CLAUDE.md §1.3.*
**Status: RATIFIED.**

Each phase subgraph contains a **Planner-Executor pair**, not a single coaching
node.

| | `phase_planner` | `phase_executor` |
|---|---|---|
| Produces | A structured `CoachingPlan` | The coaching response + extraction |
| Decides | **Strategy** — which field, which action, which retrieval mode | **Nothing about strategy** |
| Dispatches | **Never** dispatches to tools | Dispatches to leaf tools via the tool-calling loop |
| Model | `planner` role, temp 0.1 | `coach` role, temp 0.5–0.7 |

**The two are distinct nodes and are never fused.** Fusing them loses the
boundary that makes coaching inspectable and costs the ability to test either
half — a planner that can be unit-tested against "given these artifacts, which
field is next?" is worth the extra node.

### `CoachingPlan`

**Specification:** **§58.4 — S-C04**. The invocation form is kept here because it is what
makes "the planner decides at plan time" concrete.

```python
phase_planner = llm.with_structured_output(CoachingPlan)
coaching_plan: CoachingPlan = phase_planner.invoke(planner_prompt)
```

Full field semantics and the "one plan, not a queue" rule are in §6.

**The planner decides retrieval strategy at plan time, not the executor at
retrieval time.** This is what makes multi-hop *planned* rather than emergent
in Analyse (§26), and it is why `retrieval_strategy` lives on the plan rather
than being inferred inside a tool.

### Extraction is structured output, not a node and not a tool

Field capture happens through `response_format=CoachingResponse` on the
executor (§20). It is not a separate extraction node and **`record_field` is
retired** (§29).

---

## 18. Building the executor — `create_agent`

*Supersedes: REFACTORING §42, §50, §84; ARCHITECTURE.md §3.3; CLAUDE.md §4.4.*
**Status: RATIFIED.**

**Specification:** the executor node is the calibrated function sample at **§57.3 — S-F04**.

**The parameter is `system_prompt=`, not `prompt=`.** `create_react_agent`
took `prompt`; `create_agent` renamed it. Verified against the
`create_agent` reference signature, 2026-08-21.

### Binding tools directly onto a bare model is a violation

**It bypasses the middleware stack**, which carries grading, skills loading,
context compression, state injection, retry, and the coherence and
contradiction checks. A phase executor that attaches its tools straight to the
model object — rather than passing them to `create_agent(tools=...)` — silently
loses all eight.

### `create_react_agent` is superseded

Nothing may import `create_react_agent`, and **nothing may import from the
`langgraph.prebuilt` namespace** — deprecated in 1.0 → 1.1, functionality moved
to `langchain.agents`.

### deepagents is not a dependency

`create_deep_agent`, `RubricMiddleware` and `SkillsMiddleware` from that package
are **BANNED while it remains pre-1.0**. Our equivalents are custom middleware
on `create_agent` (§19).

The reasoning is a dependency-risk judgment, not a quality one: deepagents ships
breaking changes between minor versions, and adoption is all-or-nothing —
`create_deep_agent` replaces `create_agent` rather than extending it. Carrying a
bounded amount of our own code is preferable to an unbounded amount of someone
else's pre-1.0 churn. **Revisit at deepagents 1.0, and migrate all custom
middleware together or not at all.**

### The structured response and the coaching text coexist

The agent still calls tools normally through the ReAct loop and still writes
coaching prose into `messages`. Only the **terminal** response is additionally
structured, and it arrives in `result["structured_response"]`. Reading one does
not cost you the other.

---

## 19. The middleware stack — eight, in order

*Supersedes: REFACTORING §80, §84; ARCHITECTURE.md §3.4; DECISIONS §B3, §M2, §M3.*
**Status: RATIFIED.** **This is the canonical definition. Everything else cross-references it.**

**Specification:** the five custom middlewares are **§61 — S-C10 to S-C15**. The stack, its
order and its ordering rules stay here; the three core middlewares are used
as shipped and keep their configuration in §19.3–§19.5.

**Five custom, three core.** All are built on `AgentMiddleware` hooks. The six
this architecture uses are `before_agent`, `after_agent`, `before_model`,
`after_model`, `wrap_model_call` and `wrap_tool_call`.

**`AgentMiddleware` exposes more than six.** The reference also lists
`dynamic_prompt()`, `hook_config()` and `configure_trace_policy()`. Earlier
revisions of this design described "the six hooks" as though that were the
complete set; it is the set *we use*, not the set that exists. Nothing in the
stack below depends on the difference, but a reader extending the stack should
check the reference rather than this list.

**Prefer built-in middleware wherever it exists.** Custom middleware is
reserved for genuinely domain-specific logic.

### Ordering rules that bind

**Declaration order is execution order for hooks of the same kind.**

1. **`BeforeModelStateInjection` MUST be first.** Project facts have to reach
   the top of the prompt before skills loading and summarisation shape it.
2. **Positions 6, 7 and 8 all fire `after_agent`** and therefore run in
   declaration order: contradiction, then coherence, then grader.
3. **Positions 4 and 5 sit on `wrap_*` hooks** and compete for no slot with
   anything else. They are adjacent for readability, not ordering.
4. **If `CoherenceMiddleware` exhausts its retries, `DMAICGraderMiddleware` is
   skipped for that turn** — deliberately. Grading a response already known to
   be incoherent spends a model call to produce a meaningless score.

### Three independent retry caps

| Cap | Counts | Where |
|---|---|---|
| `ModelRetryMiddleware` — 2 | Transient Azure OpenAI API failures | §19.4 |
| `CoherenceMiddleware` — 2 | Response-quality failures | §19.7 |
| Validation stack — 3, shared across layers | Gate-boundary validation failures | §34 |

**They must not be merged.** Three different failure modes, three counters, no
shared state. An API timeout and an incoherent response are not the same event
and must not consume the same budget.

### 19.1 `BeforeModelStateInjection` — injection timing

**Custom · `before_agent` · position 1.** Prepends structured project state at
the **top** of the prompt, ahead of the conversation: this phase's `artifacts`,
prior phases' gate documents from the Store, current phase requirements, and
the missing fields reported by `check_gate_status()`.

**The hook is `before_agent`, not `before_model`.** State injection belongs at
agent-loop start, once per turn. `before_model` fires before every individual
model call within a turn, which re-injects the same project facts repeatedly
and wastes context.

**Missing fields are computed at injection time, never read from a stored
list.** The middleware derives them the same way the gate does, so the prompt
and `DMAICGateValidator` cannot disagree.

**Why the top of the prompt.** Models weight earlier content more heavily.
Injecting project facts *after* the Belt's message lets the response drift
toward the Belt's framing rather than the project's established state.
**Injecting in `messages[]` append order is a violation** — there is no "just
add it to the history" option.

### 19.2 `DMAICSkillsMiddleware` — progressive disclosure

**Custom · `before_agent` + a registered tool · position 2.** Full treatment in
§32; the stack-level facts are:

| Level | When | What loads |
|---|---|---|
| 1 | Startup | Skill descriptions only — **under 2K tokens for all five combined** |
| 2 | On demand | Full phase instructions, when the coach enters that phase |
| 3 | On demand | Reference files, when explicitly needed |

Level 2 is reached by the coach calling a registered `load_skill(name)` tool.
Storage backend is `FilesystemBackend` — git-versioned alongside the code, so a
skill change is reviewable in the same PR as the code depending on it.

### 19.3 `SummarizationMiddleware` — context compression

**LangChain core, used as shipped · `before_model` · position 3.**

```python
SummarizationMiddleware(
    model="azure/operational-model",       # gpt-4o-mini for cost
    trigger=("tokens", 100_000),           # ~78% of gpt-4o's 128k window
    keep=("messages", 20),                 # preserve the last 20 turns raw
)
```

**Custom compression functions are BANNED.** Do not hand-write
`compress_messages()` or a `conversation_context` builder — this middleware
provides the trigger, the summarisation call and the message-list replacement.

**The policy that makes prose summarisation safe: facts do not live in
`messages[]`.** Anything that must survive compression lives in typed state.

| Lives in | What |
|---|---|
| `SupervisorState` | `current_phase`, `phase_index`, `gate_passed` — orchestration only |
| `PhaseState` | `artifacts`, `draft`, `belt_edits`, `step_log`, `citations`, `uploads`, `validator_feedback`, `final` |
| Store | Cross-phase gate documents (§9) |

**Summarising *conversation* into prose is correct** — that is what conversation
is. **Summarising *facts* into prose is the failure this policy prevents.**

Decisions survive compression as captured fields, not as a decision list: a
committed decision arrives via `CoachingResponse.fields_captured`, is approved
at a gate, and lands in `artifacts` and then the Store — all three outside
`messages[]`. That is why no `key_decisions` field is needed (§5).

**Deprecated memory classes are BANNED:** `ConversationBufferMemory`,
`ConversationBufferWindowMemory`, `ConversationSummaryMemory`,
`ConversationEntityMemory`, `VectorStoreRetrieverMemory`, `ConversationChain`.
The replacement is checkpointer (thread-scoped) + Store (cross-thread) + this
middleware.

### 19.4 `ModelRetryMiddleware` — API-level retry

**LangChain core, used as shipped · `wrap_model_call` · position 4.**

```python
ModelRetryMiddleware(
    max_retries=2,              # NOT `retries=` — verified 2026-08-21
    retry_on=default_retry_on,
    on_failure="continue",
    backoff_factor=2.0,
    initial_delay=1.0,
    max_delay=60.0,
    jitter=True,
)
```

Wraps each model call and silently retries transient timeouts and rate limits.

**The parameter is `max_retries`, not `retries`.** Earlier revisions of this
design wrote `ModelRetryMiddleware(retries=2)` throughout — that keyword does
not exist and would raise at construction. Corrected against the reference
signature on 2026-08-21. The two retry middlewares share the same parameter
vocabulary, which is a good reason not to remember one and guess the other.

**Hand-writing retry plumbing is BANNED** — no try/except/sleep/counter loops
around an LLM call. This middleware provides the wrap, the backoff and the
attempt counter.

### 19.5 `ToolRetryMiddleware` — tool-level retry

**LangChain core, used as shipped · `wrap_tool_call` · position 5.**
`max_retries=2`, `on_failure="continue"`, exponential backoff with jitter.

**The class is `ToolRetryMiddleware`.** `RetryMiddleware` does not exist in
LangChain 1.x — never write it.

**`on_failure="continue"` is what keeps the coaching loop alive.** When retries
exhaust, the tool returns a failure result the coach can read and work around,
rather than raising and killing the graph mid-session.

### 19.6 `ContradictionDetectionMiddleware` — the mid-phase check

**Custom · `after_agent` · position 6.** Implements the mid-phase conflict
detection of §37.

**It reads a flag. It does not detect anything itself.**

**Specification:** **§61.1 — S-C10**.

**No Store read. No LLM call. No field-name matching.** Detection is performed
by the coach, in the model call that already runs every turn, and arrives as
`CoachingResponse.contradiction_flag` (§20). This middleware's whole job is to
turn that flag into an interrupt.

**No tolerance threshold**, and none may be added — the reasoning is in §37.

> ### The mechanical comparison this replaced could not work — DECISIONS §R1
>
> Until 2026-08-22 this middleware did deterministic dict comparison against
> the Store. **Three defects, each verified:**
>
> 1. **It read the wrong drawer.** It called `store.get(..., current_phase)`,
>    but `gate_apply_node` is the only writer and writes at phase *end*
>    (§33.2). **Mid-phase the key does not exist**, so it read nothing, every
>    turn, by construction.
> 2. **Field-name matching finds almost nothing.** Of 41 distinct content
>    fields across the five `{Phase}Output` schemas, **38 are unique to exactly
>    one phase** — `baseline_metric` in Define, `baseline_mean` in Measure, the
>    same quantity deliberately differently named. **93% cannot cross-phase
>    name-match at all.**
> 3. **The 3 shared names are all prose** — `issues_and_barriers`,
>    `secondary_metrics`, `process_owner_buyin` — where `!=` fires on any
>    rewording. False positives, not detections.
>
> **Repairing (1) leaves 3 prose fields out of 41.** Real contradictions arrive
> as natural-language prose referencing prior committed values under different
> field names, which needs semantic understanding. **Dict comparison cannot be
> repaired into that**, which is why this was a redesign and not a fix.

**Why middleware rather than logic inside the executor node:** the check
polices the executor's own output, so it does not belong to the thing it
polices. As middleware it is a named, LangSmith-visible step
(`ContradictionDetectionMiddleware.after_agent`), and the executor node stays
responsible only for coaching.

### 19.7 `CoherenceMiddleware` — validation Layer 2a

**Custom · `after_agent` · position 7, immediately before the grader.**

One LLM call — `coherence` role, temperature 0.1. Checks: is this a real,
conclusive statement? Is it parroting the Belt's own words back? Is it on-topic
for the current phase?

**Layer 2a fires every coaching turn**, which is why it is middleware and not
part of the `validation_stack` node — that node runs once, at the gate. Layers
2b–2d live there; 2a lives here. One conceptual stack, two mechanisms (§34).

**On failure: Level 1 silent retry, max 2.** The Belt never sees a failed
coherence response. On the third failure the turn degrades (Part IX) and
`DMAICGraderMiddleware` is skipped.

**Coherence is NOT a `COACHING_QUALITY_RUBRIC` criterion.** It moved out of the
rubric when this middleware was added. Any rubric entry for coherence is stale.

**Why it was separated from the grader:** running it inside
`DMAICGraderMiddleware` conflated two different questions — *"is this a real
statement at all?"* versus *"is this good coaching?"* — and paid for a full
rubric grading call on responses already known to be incoherent. Catching
incoherence at a cheaper gate is both faster and cleaner.

### 19.8 `DMAICGraderMiddleware` — coaching process quality

**Custom · `after_agent` · position 8.** Grades the **coach's process** against
`COACHING_QUALITY_RUBRIC` — one rubric, shared across all five phases.

Full treatment, including the rubric text and the two-grader distinction, is
**§36**. The stack-level facts:

- Model: `grader` role, temperature 0.1 (§21)
- `max_iterations=3`; on `max_iterations_reached` the output passes through
  **with a warning flag visible to the Belt**
- Verdict is **per criterion, not overall**
- `on_evaluation` writes each grading iteration to `step_log` (§11)
- Grader internals — iteration count, accumulated evaluations, attempt
  tracking — stay **private to the middleware** and never reach `PhaseState`
  or `SupervisorState`
- **The Belt does not see the grader loop.** It runs at step 2 of the gate,
  before the interrupt (§33)

### 19.9 Middleware deliberately NOT used

| Middleware | Why not |
|---|---|
| `HumanInTheLoopMiddleware` | **Two confirmed bugs hit our exact use case.** Edited tool-call args can be silently re-overwritten by the agent re-attempting the original call; and edit/reject are broken in subgraph contexts, where only approve is reliable. Both would silently discard a Belt's correction. Use graph-level `interrupt()` (§33) |
| `LLMToolSelectorMiddleware` | Per-phase binding (§30) already keeps every coach at 8–15 tools. A selector LLM spends a model call solving a problem already solved structurally |
| deepagents `RubricMiddleware` / `SkillsMiddleware` | Pre-1.0 dependency (§18) |

---

## 20. `CoachingResponse` — the per-turn schema

*Supersedes: REFACTORING §82; ARCHITECTURE.md §4.10; CLAUDE.md §10.7; DECISIONS §B4.*
**Status: RATIFIED.**

**Two schemas, two moments. Never substitute one for the other.**

| | `CoachingResponse` | `{Phase}Output` |
|---|---|---|
| Fires | **Every coaching turn** | **Once**, at `gate_apply` |
| Produced by | The executor, via `response_format=` | Pydantic construction — **no LLM** |
| Holds | This turn's extraction | The complete gate document |

**Specification:** the canonical schema, including the five `contradiction_flag` keys, is
**§58.5 — S-C05**.

**It is produced by this same `response_format` call — there is no additional
LLM call anywhere in the contradiction path** (§19.6, DECISIONS §R1). The coach
compares the Belt's input against the prior committed values already in its
context, injected by `BeforeModelStateInjection` at `before_agent` (§19.1).
**Each SKILL.md carries the instruction that governs when to set it** (§32).

**Adding a field to `CoachingResponse` requires an amendment** (§56) — it is
load-bearing in the same way `SupervisorState` and `PhaseState` are.

**Structured output guarantees the flag's shape and its presence — never the
correctness of the coach's judgment in setting it.** A schema-valid
`contradiction_flag` describing a contradiction that is not one is exactly as
well-formed as a correct one. This is the same limit stated below for captured
values, and it is why §50's all-gate-fields tab is the documented human
backstop rather than a convenience.

**`value` is `Any`, not `str`, and that is deliberate.** It must carry both
plain string fields and the three cross-phase reference dicts (§7). Typing it
`str` would make `causal_hypothesis`, `solution_linked_to_root_cause` and
`post_improvement_metric` uncapturable. **This is the one place `Any` is
correct**; the values *inside* those dicts are still strings.

### The executor node writes the response into state

**Specification:** the write-into-state behaviour is **§57.3 — S-F04**.

### The executor's `response_format` is `CoachingResponse`, never a phase Output

**The executor runs once per coaching turn; the gate document is assembled once
per phase.** Asking the coach to emit a complete `DefineOutput` every turn
requests fields it has not yet coached — the model then either refuses or
invents them, and the second failure mode is worse. See §40.

### What structured output does NOT give you

**Truth.** It guarantees shape. A schema-valid `baseline_metric: 4.2` invented
by the model is exactly as well-formed as a correct one. Content-level defence
is the anti-hallucination guards (§22), validation Layer 2a (§34) and the
policy advisory (§33) — **not this mechanism.** No reader should come away
believing structured output is a defence against hallucinated content.

---

## 21. LLM roles, temperature, and the factory

*Supersedes: REFACTORING §34-D, §42; ARCHITECTURE.md §3.3; CLAUDE.md §4.1, §4.2, §4.7.*
**Status: RATIFIED.** File: `core/llm.py`.

### Factory only

```python
from core.llm import get_llm
llm = get_llm("coach", max_tokens=1500)
```

**Never instantiate `AzureChatOpenAI` directly.**

### Roles

Two deployment tiers, addressed by role. **Model tiering is a cost rule, not a
style preference** — gpt-4o-mini is roughly 15× cheaper.

| Role | Deployment | Purpose |
|---|---|---|
| `coach` | `operational-premium` (gpt-4o) | Coaching content, `max_tokens=1500` |
| `planner` | `operational-premium` | Phase planner structured decisions |
| `synthesis` | `operational-premium` | Multi-hop synthesis (§26) |
| `reasoning` | `operational-model` (gpt-4o-mini) | Default reasoning, intermediate hops |
| `extraction` | `operational-model` | Field extraction |
| `coherence` | `operational-model` | Layer 2a (§19.7) |
| `constraint` | `operational-model` | Layer 2c (§34) |
| `grader` | `operational-model` | Rubric grading (§36) |
| `summarizer` | `operational-model` | Context compression (§19.3) |
| `intent` | `operational-model` | Short classification |
| `vision` | `operational-premium` | Multimodal upload analysis |

**New roles require an amendment.**

### Temperature

| Component | Temperature | Why |
|---|---|---|
| Coach responses | 0.5–0.7 | Natural variation improves the Belt's experience |
| Synthesis (§26) | 0.1–0.2 | Reproducible evidence assembly |
| Grader | **0.1** | Same gate document must get the same verdict across runs |
| Coherence (2a) | 0.1 | Consistent verdicts |
| Constraint (2c) | 0.1 | Consistent verdicts |
| Planner | 0.1 | Deterministic decomposition |
| Extraction, field validators | 0.0–0.2 | Same rationale |

**The grader's temperature is a hard requirement, not a tuning knob.** A grader
returning different verdicts across runs makes the regression thresholds in §52
meaningless — you cannot detect a 10% quality drop against a baseline that
moves on its own.

### Structured output — scoped by call type

**There are two mechanisms and the choice is determined by what is being
called, not by preference.**

| The call is… | Use |
|---|---|
| An agent built with `create_agent` | `response_format=Schema` |
| A plain model invocation inside a tool, middleware or validator | The builder-style structured-output call on the model |
| Assembling a gate document from already-captured fields | **No LLM call** — Pydantic construction |

**Why the first two exist separately:** `response_format=` attaches to an
agent's model-tools loop. A tool generating query variants, a middleware
grading a transcript, and a validator returning per-constraint verdicts are not
agents — there is no loop to attach to.

Prefer `ProviderStrategy` over `ToolStrategy` where the provider supports
native JSON mode.

**Complete mapping — every structured output in the system:**

| Component | Schema | Mechanism |
|---|---|---|
| Phase planner | `CoachingPlan` | builder-style |
| **Phase executor** | **`CoachingResponse`** | **`response_format=`** |
| Layer 2a coherence | `CoherenceResult` | builder-style |
| Layer 2c constraints | `ConstraintCheckResult` | builder-style |
| Layer 2d gate grader | `GraderVerdict` | builder-style |
| `gate_review` | Interrupt payload | **No LLM** — `interrupt()` |
| `gate_apply` policy advisory | `PolicyAdvisoryResult` | builder-style |
| `DMAICGraderMiddleware` | `CoachingGraderVerdict` | builder-style |
| Multi-hop synthesis | `SynthesisOutput` | builder-style |
| Inside `rag_lookup_*` | `QueryVariants` | builder-style |
| Gate document assembly | `DefineOutput` … `ControlOutput` | **No LLM** — `Schema(**artifacts)` |

**Never parse JSON from raw LLM text.** Structured output is the only path from
a model to a typed value.

**Read typed content blocks, never string-index the content.** Model responses
carry typed content blocks; read `response.content_blocks`. String-indexing or
substring-parsing the raw content field breaks the moment a provider returns a
multi-part response.

---

## 22. Prompts

*Supersedes: REFACTORING §38, §40; ARCHITECTURE.md §3.3; CLAUDE.md §6.*
**Status: RATIFIED.** File: `core/prompts.py`.

**All prompts live as constants in `core/prompts.py`.** Prompt strings are
never inline in node files.

| Constant | Purpose |
|---|---|
| `{PHASE}_COACH_PROMPT` | Phase executor system prompt |
| `{PHASE}_PLANNER_PROMPT` | Phase planner prompt |
| `{PHASE}_RUBRIC` | Gate grader rubric (§36) |
| `{PHASE}_CONSTRAINTS` | Constraint set (§34) |
| `COACHING_QUALITY_RUBRIC` | The single shared coaching rubric (§36) |

**Retired patterns:** `ORCHESTRATOR_{PHASE}_CONTEXT`, `EXTRACTION_{PHASE}`, and
`KNOWLEDGE_INJECTION_TEMPLATE`. The last is deleted specifically because RAG
results arrive as **tool results**, not as a prepended system message (§24).

### The memory hierarchy paragraph is mandatory

Every coach system prompt carries an explicit source hierarchy. **This is the
ratified mechanism for memory prioritisation — prompt-level priority, not
per-chunk metadata scoring:**

```
MEMORY HIERARCHY — when sources disagree, weight them in this order:
  1. LSS Black Belt methodology (rag_lookup_methodology) — authoritative
  2. This project's confirmed captured fields — the Belt's own approved facts
  3. Past case history (rag_lookup_case_history) — patterns, not prescriptions
  4. Recent conversation — context, not evidence
Never present case history as methodology. Never let a recent remark
override a gate-approved value without flagging it.
```

The ordering carries real weight: **case history is patterns, not
prescriptions.** Another project's solution is evidence that something worked
somewhere, not methodology, and a coach that presents it as methodology teaches
the Belt to copy rather than to reason.

### Anti-hallucination guards are mandatory

Every coach and extraction prompt carries explicit anti-hallucination guards.
**The LLM must never invent field values from coaching templates.** A template
showing `baseline_mean: 4.2` as an example is not data — and this is a real
failure mode, because show-first coaching (§43) puts worked examples directly
in front of the model on every turn.

**Structured output does not satisfy this rule** (§20). Content-level defence
requires all three of:

1. Explicit prompt guards
2. Cross-checking extracted values against the raw conversation
3. The policy advisory reviewing extracted values before Belt approval (§33)

---

# Part V — Knowledge and Retrieval

---

## 23. The three indexes

*Supersedes: REFACTORING §36, §40; ARCHITECTURE.md §7.1–§7.3; CLAUDE.md §7.3.*
**Status: RATIFIED, with two pending schema changes marked below.**
> **Scope:** the mechanism is platform; the instantiation below is Agent Improve's — the three-index split — methodology, evidence, case history — is platform; the `improve_*` names, schemas and field lists are Improve's. Agent Resolve's equivalents are `knowledge_index_v2`, `evidence_index_v1`, `case_index_v3`

**Canonical home for all index schemas.**

Three Azure AI Search indexes, one per retrieval tool. **Each tool is bound to
exactly one index and knows that index's field names locally** — there is no
shared retriever, which is what keeps the differences between them from hiding
in shared code.

### 23.1 `improve_knowledge_index` — methodology

LSS Black Belt eBook content. Static, identical for every project and every
Belt, never updated at runtime.

| Field | Type | Role |
|---|---|---|
| `id` | String | Key |
| `content` | String | Chunk text |
| `content_vector` | SingleCollection (3072d) | Vector field |
| `metadata` | String | JSON blob |
| `source_file` | String | Returned for citation |
| `phase_relevance` | String | **Filter** |
| `page_number` | Int32 | Returned for citation |

**Filter:** `phase_relevance eq '{phase}' or phase_relevance eq 'general'`

**The cross-phase value is `general` — never `all`, never `phase`.** All three
have been wrong in some revision, and the failure modes differ:

| Wrong value | What happens |
|---|---|
| `phase` as the *field* name | The field does not exist; **Azure rejects the whole query** — fails loudly |
| `'all'` as the cross-phase value | No document carries it; the `OR` clause is never satisfied and the corpus is **silently narrowed** to the current phase |

218 documents carry `'general'`. Zero carry `'all'`. **The silent failure is
the dangerous one**, and it is why this value is stated here rather than left
to be confirmed at implementation time.

### 23.2 `improve_evidence_index` — Belt-uploaded evidence

Case-specific documents. **This is the only channel through which external
data enters the system** (§29.1), which makes it architecturally more important
than "uploaded files" suggests.

| Field | Type | Role |
|---|---|---|
| `id` | String | Key |
| `content` | String | Chunk text |
| `content_vector` | SingleCollection (3072d) | Vector field |
| `metadata` | String | JSON blob |
| `case_id` | String | **Filter** — scopes to the current case |
| `phase` | String | **RATIFIED — NOT YET APPLIED.** Optional filter, default OFF |
| `uploaded_at` | String | **RATIFIED — NOT YET APPLIED.** Order by, ISO 8601 |

**Until the reindex runs, the live index is the first five fields and code must
not reference `phase` or `uploaded_at`.**

Both new fields **backfill from `metadata`** at reindex time — `uploaded_at`
from `metadata.timestamp`, `phase` from `metadata.upload_phase`. No new data
collection is needed; the values already exist in the wrong shape, buried in a
non-sortable JSON blob where `$orderby` and `$filter` cannot reach them.

Both are **server-set**: `phase` from `state["current_phase"]` at upload,
`uploaded_at` from the server clock. A Belt-entered value for either makes it
unreliable as a filter or sort key.

**`phase` closes a problem that was never articulated:** two similar documents
uploaded at different phases were indistinguishable at retrieval time. A Belt's
Measure-phase defect data and their Control-phase defect data both match
"defect data" with nothing to tell them apart — and since this index is the
sole external channel, that ambiguity lands directly on the coaching answer.

**Its filter defaults OFF, deliberately.** Cross-phase evidence retrieval is
the *normal* case — a Control Belt comparing against the Measure baseline —
so filtering to the current phase by default would break the comparison the
field exists to enable.

### 23.3 `improve_case_index` — case records (cross-case memory)

Live case data with per-phase summaries. This is the long-term cross-case
memory mechanism.

| Field | Type | Role |
|---|---|---|
| `id` | String | Key |
| `case_id` | String | Case identifier |
| `title` | String | Case title |
| `belt_level` | String | **Optional filter, OFF by default** |
| `leader` | String | Project leader |
| `department` | String | Owning department |
| `current_phase` | String | Phase in flight |
| `rag_status` | String | Red / Amber / Green |
| `status` | String | **Filter** — `status eq 'completed'` |
| `created_at` | String | **Order by** — `created_at desc` |
| `target_date` | String | Planned completion |
| `days_in_phase` | Int32 | Duration metric |
| `phase_summary_define` | String | Pre-computed summary |
| `phase_summary_measure` | String | Pre-computed summary |
| `phase_summary_analyse` | String | Pre-computed summary |
| `phase_summary_improve` | String | Pre-computed summary |
| `phase_summary_control` | String | Pre-computed summary |
| `content_text` | String | Concatenated case text |
| `embedding` | SingleCollection (3072d) | Vector field — **renaming, see below** |

**`embedding` → `content_vector` is RATIFIED — NOT YET APPLIED.** This is the
only index whose vector field is not `content_vector`, and the difference is
historical rather than deliberate. Delete + recreate (the index holds 0
documents, so no data migration), **batched with the §23.2 additions** so the
corpus rebuilds once. **Until it lands, `embedding` is the live name.**

**The vector-field asymmetry is safe by construction, and is still being
removed.** Each tool knows its own index's field name locally, so no shared
code can hide the difference and fail silently on it. "Safe" was the reason not
to rush the rename — never a reason to keep it.

**Vector configuration, confirmed against the live index (Aug 2026):**
`embedding` is **3072-dimensional**, consistent with `text-embedding-3-large`
and with `content_vector` on the other two indexes. HNSW profile
`improve-vector-profile`, cosine metric, `m=4`, `efConstruction=400`,
`efSearch=500`.

**The profile name differs from the other two indexes**, which use `default`.
Safe by construction — each tool addresses its own index (§24) — but **worth
normalising during the `content_vector` reindex**, since the index is being
deleted and recreated anyway and the opportunity does not recur cheaply.

### The internal phase key is `analyse`, never `analyse_phase`

`f"phase_summary_{phase}"` is correct for all five phases with **no mapping
constant anywhere**. A mapping constant was considered and rejected: fixing the
name at the source means no permanent workaround exists.

`analyse_phase` was the anomaly in **four places at once**, all renamed
together:

| Was | Now |
|---|---|
| `backend/phases/analyse_phase/` | `backend/phases/analyse/` |
| `orchestrate_analyse_phase`, `validate_analyse_phase` | `orchestrate_analyse`, `validate_analyse` |
| Graph nodes `"orchestrate_analyse_phase"`, `"validate_analyse_phase"` | `"orchestrate_analyse"`, `"validate_analyse"` |
| The key `"analyse_phase"` in `PHASE_ORDER`, v1 `phase_inputs`, `EXTRACTION_MAP`, `ORCHESTRATOR_CONTEXT_MAP`, `GATE_CHECKS`, `PhaseSummaryRecord`, `CaseDocument.phases` | `"analyse"` |

**`AnalysePhaseInput` keeps its name** — `{Phase}PhaseInput` is the convention
all five phases follow, so it was never part of the inconsistency.

**Renaming the graph node names was safe only because no checkpoints existed.**
LangGraph checkpoints record node names; had any been present, the rename would
have orphaned them. This was verified before applying — the blob container held
no `checkpoints/` prefix.

> **Any future rename of a graph node name must re-check this, and the window
> in which it is free is closing.** The checkpointer is being wired in during
> this same refactor (§8). Once real checkpoints exist, a node rename is a
> migration, not an edit.

### 23.4 The write-path trap that made `phase_relevance` unfilterable

**A metadata key becomes a filterable field only if it is named after one AND
the vectorstore declares it.**

LangChain's `AzureSearch` promotes a metadata key to a top-level field only
when the key matches a name in `self.fields`:

```python
additional_fields = {k: v for k, v in metadata.items()
                     if k in [x.name for x in self.fields]}
```

`self.fields` **defaults to `[id, content, content_vector, metadata]` and never
introspects the live index.** So writing methodology requires both the correct
key name *and* `fields=KNOWLEDGE_INDEX_FIELDS` on the vectorstore. Either alone
leaves the value buried in the `metadata` JSON blob, unreachable by `$filter`,
**with no error raised.**

**This is how `phase_relevance` went unpopulated.** `ingest_knowledge.py` owns
this contract.

**Never call `add_texts` without explicit `ids=`** — LangChain assigns a random
UUID key, so re-ingestion duplicates the corpus rather than replacing it.

### 23.5 Schema change procedure

An index schema change lands in **this section first**, in the same commit as
the Azure AI Search change. Never record a schema change only in code.

**Never write to Agent Resolve indexes.** Read-only, via tools.

---

## 24. The three `rag_lookup_*` tools

*Supersedes: REFACTORING §32, §33, §37; ARCHITECTURE.md §7.4; CLAUDE.md §7.2; DECISIONS §E1, §E4.*
**Status: RATIFIED.** File: `knowledge/tools.py`.

**Specification:** the three tools are **§59.5 — S-F14**, **§59.6 — S-F15** and
**§59.7 — S-F16**, each carrying its index, filter and vector field.

**The three superseded tool names are `search_improve_knowledge`,
`search_improve_cases` and `search_improve_evidence`.** No v2 code may
reference them.

**Only the tool layer is retired.** `knowledge/retriever.py`'s
`search_knowledge` / `search_cases` / `search_evidence` functions are what the
`rag_lookup_*` tools call, and they **keep their names** along with the failure
semantics of §27.

*Corrected 2026-08-21. This section previously named `search_methodology` and
`search_evidence` as the retired pair. `search_methodology` exists nowhere, and
`search_evidence` is a live retriever function §27 depends on — so the rule
contradicted §27, and a grep for the named strings would have passed while every
real retired name survived. Verification depends on literal strings.*

### RAG via tool, never via prepended system message

**The v1 pattern — `build_knowledge_context()` injected as a `SystemMessage` —
is DELETED.** Retrieval is a tool call the model decides to make.

Three things follow, and each is a reason on its own:
- RAG becomes **accountable in the trace** — you can see what was retrieved and when
- The model **controls when to retrieve**, rather than paying for it every turn
- The **always-on retrieval cost disappears**

**There is no unconditional retrieval pipeline. If you find one, it is a
violation.**

### The retrieval mechanism

**`AzureSearch` (`langchain_community.vectorstores.azuresearch`), with the
filter passed at call time:**

```python
vs = get_knowledge_vectorstore()          # module-level, @lru_cache(maxsize=1)
filters = f"phase_relevance eq '{phase}' or phase_relevance eq 'general'"
docs = vs.similarity_search(query, k=k, filters=filters)
```

**`AzureAISearchRetriever` is deliberately NOT adopted.** It takes `filters` at
*construction*, which would force per-call instantiation once the filter is
dynamic. `AzureSearch` takes it at *call time*, so the dynamic `phase` value
never reaches construction and the cached module-level singleton is correct.
Adopting a different retrieval class would be a migration, not a bug fix.

> **Task 3B note (2026-08-21).** The brief asked whether
> `AzureAISearchRetriever` offers anything `AzureSearch` does not, and whether
> that would justify revisiting. **No such advantage was found** in the current
> reference, so the decision stands unchanged. Recorded so the question is not
> re-opened without new evidence.

**`improve_case_index` additionally uses a raw `SearchClient`**, because
`AzureSearch` resolves its content and vector field names from process-global
settings that default to `content` / `content_vector`, while that index uses
`content_text` / `embedding`.

**What genuinely must be set at construction is `fields=`** — see §23.4. That
is the real constructor-time constraint on this stack.

### `belt_level` filtering is OFF by default

Over-narrowing risk: **a Green Belt often benefits from seeing a Black Belt
case.** Available as an optional parameter for scoped searches. Note the
contrast with the *grader*, which does suppress Black-Belt-only recommendations
for a Green Belt (§35) — adjusting what the grader asks of a Belt does not have
the same failure mode as restricting what they may learn from.

### `source_file` and `page_number` are returned, never filtered

They exist for **citation transparency** — "this came from page 47 of the BB
eBook" (§50). Using them as filters is a category error.

---

## 25. Multi-query and Reciprocal Rank Fusion

*Supersedes: REFACTORING §32, §33, §35; ARCHITECTURE.md §7.4; DECISIONS §E1.*
**Status: RATIFIED.**

**All three retrieval tools generate 3–5 query variants and fuse the results
with Reciprocal Rank Fusion, k=60. This is mandatory, not optional.**

### Why it is mandatory

Azure AI Search already does **hybrid retrieval** — BM25 keyword matching plus
vector similarity — so the gap is not "missing BM25." The gap is sending **one
query formulation** to an already-good hybrid retriever, which misses concepts
the Belt did not explicitly name.

**Agent Resolve production experience settled it.** With a single query, Azure
AI Search ranking was not reliably returning the right matches for this corpus.
RRF operationalises **cross-variant consistency** — a document ranked well by
several different phrasings is more likely relevant than one ranked well by
one. Native single-query ranking cannot do this, because it does not know the
other variants exist.

An earlier "diminishing returns, defer it" position was overridden by that
evidence.

### The implementation

**Specification:** **§59.8 — S-F17**.

**Roughly fifteen lines, no LangChain class, no third-party dependency, stable
across framework versions.** It lives in `knowledge/fusion.py`.

### `MultiQueryRetriever` and `EnsembleRetriever` are BANNED

**Both moved to `langchain_classic` in the LangChain 1.0 namespace split** and
are not importable from `langchain` in the current version.

`EnsembleRetriever` would be the wrong class even if it were importable: it
fuses results from **different retriever sources** (BM25 + vector, say),
whereas our pattern is **same-index multi-query** — N phrasings against one
index. No standard LangChain 1.x class covers that pattern, and the LangChain
rag-fusion template used a custom implementation for the same reason.

**Two independent reasons, one conclusion.** Custom RRF is correct, stable and
dependency-free.

### Encapsulation

Variant generation and fusion happen **inside** the tool. The agent sees a
clean `rag_lookup_*(query, ...)` interface and never manages either. Complexity
belongs inside the tool, not exposed to the model.

**Variant generation uses structured output** (`QueryVariants`, §21), never
manual JSON parsing.

---

## 26. Multi-hop retrieval

*Supersedes: REFACTORING §34, §71; ARCHITECTURE.md §7.5; DECISIONS §F6, §F7.*
**Status: RATIFIED.**

**Multi-hop is what the executor's ReAct loop does when it makes several
`rag_lookup_*` calls in one Belt turn.** It is not a separate subsystem and
needs no new infrastructure.

**Multi-hop and multi-query are independent and compose.** Multi-query
*broadens* within a hop; multi-hop *deepens* across hops. Neither requires the
other — better single-hop retrieval reduces how many hops are needed, but does
not replace them.

### The hop cap is `RemainingSteps`

**Specification:** the guard is behaviour B1 of **§58.18 — S-F09**. Note the state field it
reads is undeclared — **SPEC-GAP G-04**.

**Five hops per Belt turn.** Beyond five the model is usually lost or looping,
and cutting it off is correct behaviour.

**`RemainingSteps` rather than `recursion_limit`** — the reasoning, and the two
ways `recursion_limit` fails in a hierarchy, are in §16. The property that
matters here: `RemainingSteps` lives in graph state, so it crosses the subgraph
boundary intact, counts only executor steps, and **provides a graceful
off-ramp** — the agent composes an answer from what it has rather than dying.

**`GraphRecursionError` must still be caught in the coach node** and turned
into a partial answer. It is now a belt-and-braces guard against bugs rather
than the primary mechanism. **A Belt mid-session never sees a stack trace
because the coach explored too broadly.**

**Hitting the cap is a monitoring signal, not just a limit.** It means either
the system prompt encourages too-broad exploration, or the question warrants
premium-tier treatment for that turn. Watch it in LangSmith — it is also the
promotion trigger for the deferred model-tiering item (Appendix B).

### Per-phase policy

**The planner decides retrieval strategy at plan time** (§17), and
`coaching_plan.retrieval_strategy` carries it.

| Phase | Default | Multi-hop when |
|---|---|---|
| Define | Single-hop | **Never** — scoping questions are direct |
| Measure | Single-hop | Complex measurement-system validation (GR&R) |
| **Analyse** | **Multi-hop, planned (3 hops)** | **Almost always** — root cause validation is layered |
| Improve | Single-hop | The Belt is comparing competing approaches |
| Control | Single-hop | **Never** — documentation questions are direct |
| **Gate validation** | **No retrieval** | **Never** |

**Gate validation never retrieves.** The rubric already encodes the methodology
standards, so retrieval there is redundant *and* adds latency at exactly the
moment the Belt is waiting for a decision. If the rubric is incomplete, the fix
is to improve the rubric.

### Planned multi-hop — the Analyse pipeline

Three query types exist, and only the first is a retrieval problem:

| Type | Source | Multi-hop? |
|---|---|---|
| Methodology retrieval | `improve_knowledge_index` | **Yes** |
| The Belt's conversational answers | The Belt | No — field extraction, no index |
| Gate quality evaluation | `artifacts` already in state | No — never |

**Stage 1 — Planner:**

**Specification:** **§59.1 — S-C16** and **§59.2 — S-C17**.

**Stage 2 — Executor**, with the guard at node entry:

**Specification:** **§58.18 — S-F09**.

**The loop needs no internal guard** because `Plan` bounds it at exactly 3
hops. **The entry guard exists** because without it the 3-hop sequence can
begin with almost no budget left and consume it before the agent can
synthesise.

**Stage 3 — Synthesis is a dedicated call.** Three LLM calls per Analyse
multi-hop turn:

| # | Call | Temp | Produces | Belt-facing |
|---|---|---|---|---|
| 1 | Planner | 0.1 | `Plan` — 3 hops + `synthesis_instruction` | No |
| 2 | Synthesis | 0.1–0.2 | `SynthesisOutput` | **No** |
| 3 | Coach | 0.5–0.7 | The coaching response | Yes |

**Specification:** **§59.3 — S-C18**.

**Why synthesis is not folded into the coaching call.** Collapsing stages 2 and
3 saves a call and was rejected. Synthesis is a quality gate: assembling
multi-hop evidence correctly is a different job from translating it into
coaching language, and **each call is temperature-tuned for its own job** —
deterministic evidence assembly at 0.1–0.2, natural coaching voice at 0.5–0.7.
One call cannot be both. Separating them also makes each stage independently
unit-testable and puts the evidence chain in the trace, so a wrong coaching
answer can be traced to *either* bad evidence *or* bad translation.

The three Azure AI Search calls (one per hop) are not LLM calls.

### **UNVERIFIED** — planned multi-hop is Analyse-only

The planned pipeline is implemented **only** in `analyse_executor_node`. Every
other phase uses the standard ReAct path. **The assumption that reactive tool
calling is sufficient for non-Analyse turns has not been tested.**

A Define Belt asking whether their problem statement is well-scoped against
similar projects, or a Control Belt asking why Cpk remains borderline, could
equally benefit from structured multi-hop plus synthesis. Note
`CoachingPlan.retrieval_strategy` is **not** restricted to Analyse — the
planner may set `multi_hop` in any phase.

**Validate during the eval dataset phase (§52):** if non-Analyse turns show 3+
sequential tool calls with lower coaching quality than Analyse multi-hop turns,
extend the mechanism.

---

## 27. Retrieval failure semantics

*Supersedes: ARCHITECTURE.md §7.1.1; CLAUDE.md §7.2; DECISIONS §E5.*
**Status: RATIFIED.**

**Retrieval failure is never an empty result.**

All three retrieval functions return `[]` **only** when the search ran and
matched nothing. When they fail, they raise `KnowledgeSearchError`.

### Never wrap a retrieval call in a bare `except Exception` returning `[]`

**That is what hid the `phase` filter bug** — it reported a broken index as a
silent empty corpus for an extended period. The coach then told Belts the
methodology had nothing on their topic, which was false and unfalsifiable from
the outside.

Catch `retriever.RETRIEVAL_EXCEPTIONS` and classify via `_fail()`.

### Three rules that each have already bitten

1. **`RETRIEVAL_EXCEPTIONS` spans two services** — Azure AI Search *and* the
   Azure OpenAI query embedding, which runs inside the same `try`.
2. **A 4xx is `permanent` / `do_not_retry`**, not transient. It is our
   malformed query; retrying fails identically.
3. **Materialise results inside the `try`.** `SearchClient.search()` is lazy
   and the HTTP call fires on iteration — a `try` that returns the iterator
   catches nothing.

### The coach-facing message must not read as absence

A retrieval failure message tells the coach explicitly that this is a failure,
not an empty corpus:

> "Methodology search is unavailable right now (`{error_code}`). This is a
> retrieval failure, not an absence of guidance — do not tell the team the
> methodology has nothing on this. Answer from your own DMAIC knowledge, say
> the reference lookup failed, and avoid citing sources you could not
> retrieve."

**Never let a coach-facing failure message read as an absence of content** —
"no cases found" when the search never ran is worse than an error, because the
Belt acts on it.

---

## 28. Memory taxonomy

*Supersedes: REFACTORING §37; DECISIONS §K1.*
**Status: RATIFIED.**

Five memory types. The first four are v2.1 scope; the fifth splits.

| Type | What it stores | Implementation | Status |
|---|---|---|---|
| **Episodic** | Per-case history — coaching turns, decisions, gate outcomes | `step_log`, `improve_case_index`, `SummarizationMiddleware` | v2.1 |
| **Semantic** | Domain knowledge — DMAIC methodology, tools, templates | `improve_knowledge_index`, `rag_lookup_methodology` | v2.1 |
| **Working** | In-flight turn state | `PhaseState` fields — `artifacts`, `hop_results`, `synthesis_output` | v2.1 |
| **Retrieval control** | Which memory to query, when, how | `CoachingPlan.retrieval_strategy`, `rag_lookup_*` routing | v2.1 |
| **Procedural (static)** | How to execute DMAIC coaching — invariant rules | System prompt, SKILL.md via `DMAICSkillsMiddleware`, phase rubrics, anti-hallucination guards | **v2.1** |
| **Procedural (dynamic)** | How to *adapt* coaching delivery per Belt | Per-Belt procedure store, updated from LangSmith trace analysis | **DEFERRED** |

### The static/dynamic split is the part that matters

**Static procedural memory is the invariant DMAIC methodology** — the same
coaching rules for every Belt, every project, every domain. **This is correct
and deliberate, not a limitation.** Methodology consistency is precisely the
guarantee a DMAIC coaching system exists to provide; a coach that quietly
varied gate criteria per Belt would be worthless as a quality system.

**Dynamic procedural memory is Belt-adaptive *delivery*.** How much scaffolding
this Belt needs, whether worked examples or challenge questions land better,
which project-type emphasis helps.

**The line between them is strict and load-bearing: dynamic procedural memory
adapts how the methodology is delivered, never what the methodology requires.**
A Black Belt still needs `vital_few_xs`. The coach may open Analyse differently
for a BB with ten projects behind them, but the gate criteria do not move.

The mechanism is Appendix B item 5 — LangSmith traces record which coaching
approaches preceded clean gate passages and which preceded repeated loops; a
background process outside the coaching loop extracts the pattern; the next
session loads the learned procedures alongside the static rules, **extending
them, never overriding them.**

---

# Part VI — Tools

---

## 29. The data channel and the universal seven

*Supersedes: REFACTORING §39, §60, §63; ARCHITECTURE.md §8.1; CLAUDE.md §1.9, §5.1; DECISIONS §B5, §B6.*
**Status: RATIFIED.**

### 29.1 There is no MCP — the data-channel decision

**Agent Improve, Agent Resolve and Agent Flow will never use MCP to connect to
a live system. This is an architectural exclusion, not a deferral. There is no
promotion trigger, because there is no path to promotion.**

This is stated first in this Part because it determines what the tool
inventory *can* be. Every tool below is either a retrieval tool against our own
indexes, a pure function, or a UI-facing proposal — and that is a closed set by
design, not by current limitation.

**The principle it establishes:**

> `improve_evidence_index` is not merely "case-specific uploaded documents."
> It is the **only** channel through which external, real-world data enters
> AgentLean.

**Three consequences bind on implementation:**

1. **Coaching content must include guidance on what data to upload and how to
   structure it.** Data-collection coaching is a first-class part of the
   methodology, not a workaround for a missing integration. This is why the
   seven-step computation pattern (§43) has "guide data preparation" as an
   explicit step.
2. **Belt data-collection discipline is what the platform's grounding depends
   on.** A phase with an empty `uploads` list reached its conclusions from
   typed statements alone (§6).
3. **There is no fallback path where the system fetches a number the Belt
   failed to provide. Do not build one.**

**Cross-agent tool sharing** — Agent Improve reading Agent Resolve's indexes —
happens via **Python imports from shared modules, not via a protocol.** Those
remain `@tool` functions, read-only.

**Never add an MCP server, client, or dependency.**

### 29.2 The universal seven

Passed to **every** phase executor via `tools=`:

**Specification:** the three retrieval tools are **§59.5–§59.7 — S-F14 to S-F16**; the four
remaining universal tools are **§60.1–§60.4 — S-F19 to S-F22**.

**`propose_diagram` returns structured JSON, not SVG.** The model describes
what to draw; the frontend owns how it looks. A model emitting SVG produces
markup that drifts from the design system and cannot be restyled.

### 29.3 `record_field` is RETIRED and may not be reintroduced

Field capture happens through `response_format=CoachingResponse` on the
executor (§20) — the coach emits `fields_captured` as structured output on
**every** turn, and the executor node writes each entry to `artifacts`.

**A tool would make capture a decision the coach might skip; structured output
makes it part of every response by construction.** That is the whole argument,
and it is why the universal count is seven rather than eight.

### 29.4 Cross-agent tools — a third category, present but NOT BOUND

*Ratified 2026-08-21 via §56. Decision record: `agent-improve/docs/DECISIONS.md` §Q1.*

**There are three tool categories in this system, not two:**

| Category | Where | Bound to |
|---|---|---|
| **The universal seven** (§29.2) | `knowledge/tools.py` | **Every** phase executor |
| **Computation tools** (§30) | `knowledge/computation.py` | Per phase, 1–8 of them |
| **Cross-agent tools** (this section) | `knowledge/tools.py` | **Nothing. Deliberately** |

**The four:**

```
search_resolve_cases(query)      → Agent Resolve  case_index_v3
search_resolve_knowledge(query)  → Agent Resolve  knowledge_index_v2
search_resolve_evidence(query)   → Agent Resolve  evidence_index_v1
search_flow_vsm(query)           → Agent Flow     vsm_index   [STUB]
```

**This section exists because §29.1 and §29.2 were in tension.** §29.1
sanctions cross-agent sharing via Python imports and says those *remain `@tool`
functions*; §29.2 defines the universal seven, which these are not among. Read
together the four were simultaneously permitted and unaccounted for. Neither
section was wrong — the category was missing.

**Current disposition: RATIFIED — PRESENT, NOT BOUND.** No coach receives any
of them. Verified 2026-08-21: nothing outside `tools.py` imports from it and
`bind_tools` appears nowhere. They are **reserved for cross-agent scenarios
that do not exist yet** — Agent Resolve integration is not built and Agent Flow
has no indexes, which is why `search_flow_vsm` returns a fixed
*"not yet available"* string unconditionally.

**Why they are kept rather than deleted:** the three `search_resolve_*` tools
are working read-paths into a production system, verified read-only. They cost
nothing while unbound, and deleting them would mean rebuilding and re-verifying
later.

**Why they are not bound now:** §30's selection-quality ceiling. Measure is at
15 tools against a hard cap of 16; three more would put it at 18. And there is
no evidence cross-agent retrieval improves DMAIC coaching — producing that
evidence needs the §52 eval dataset.

> **Three rules bind before any of them may be bound to a coach.** They are
> recorded now, while the question is cheap, rather than when someone wants the
> capability.
>
> 1. **Binding one is an amendment (§56), not a routine change** — it moves a
>    phase's tool count against §30's cap.
> 2. **They must first comply with §27.** All four currently catch bare
>    `Exception` and return a prose string, which makes retrieval failure
>    indistinguishable from no matches. That is tolerable **only** because they
>    are unreachable; it becomes a live violation the moment one is bound.
> 3. **They must return citations the way the universal seven do** (§50). They
>    return `str` with an inline source prefix, not structured citation
>    metadata, so nothing downstream can surface `source_file` / `page_number`.

**Never write to Agent Resolve indexes** (§23.5). Read-only is not a default
that may be relaxed.

---

## 30. Computation tools and per-phase binding

*Supersedes: REFACTORING §39; ARCHITECTURE.md §8.2; CLAUDE.md §5.2; DECISIONS §B7.*
**Status: RATIFIED.** File: `knowledge/computation.py`.
> **Scope:** the mechanism is platform; the instantiation below is Agent Improve's — per-phase binding and the 16-tool ceiling are platform; **all twenty tools are Six Sigma statistics** and belong to Improve alone


### Tool sets are per phase, not universal

**Tool selection quality degrades past roughly 10–15 tools per agent.**
Per-phase binding keeps every coach inside the tractable range.

| Phase | Universal | Computation tools | Total |
|---|---|---|---|
| **Define** | 7 | `calculate_expected_savings` | **8** |
| **Measure** | 7 | `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean` | **15** |
| **Analyse** | 7 | `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression` | **12** |
| **Improve** | 7 | `calculate_doe_main_effects` | **8** |
| **Control** | 7 | `xbar_r_chart_limits`, `imr_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk` | **12** |

**20 computation tools total.** 1 + 8 + 5 + 1 + 5 = 20.

**No phase exceeds 16 tools**, and the actual maximum is 15 (Measure). A new
tool that would push a phase past 16 requires an amendment, not a routine
addition.

### Each of the 20 is a separate named tool

**Parameterised grouping is BANNED** — one `calculate_sample_size(type, ...)`
with a mode argument moves the selection burden into the argument space, and
models handle distinct named tools more reliably than mode arguments.

### All 20 are pure functions

No LLM call, deterministic, unit-tested. They are the one place synchronous
code is unambiguously correct (§14).

**They parse their inputs at the point of use** (§7) — each extracts what it
needs from the string it is given and returns a clear reformatting request to
the Belt when it cannot.

### `imr_chart_limits` — the choice that is usually wrong by default

**The individuals / moving-range chart is the right choice whenever the Belt
has one measurement per period** rather than batches — which is the common case
in service and transactional work.

**Never coach a Belt into inventing subgroups to fit a batch chart.** Subgroups
that were not collected as subgroups produce meaningless control limits, and
the resulting chart looks authoritative while being wrong.

### Tool decisions are the model's, not the graph's

The graph does not pre-select which computation tool runs. The coach chooses,
under the seven-step pattern (§43) and the rubric that enforces it.

---

## 31. Tool arg schemas and docstrings

*Supersedes: REFACTORING §32, §39; ARCHITECTURE.md §8.1; CLAUDE.md §5.3, §5.4.*
**Status: RATIFIED.** File: `knowledge/tool_args.py`.

### Every `@tool` uses `args_schema=`

A Pydantic model from `knowledge/tool_args.py`. **No tools with raw signature
inference** — inferred schemas produce vague parameter descriptions, and the
parameter description is what the model reads when deciding how to call.

### Docstrings are interface, not commentary

**The tool docstring is how the model chooses between the three retrieval
tools.** It is load-bearing.

Every retrieval tool docstring MUST state:

- **When to use it** — "I need methodology" vs "I need this project's data" vs
  "I need precedent from other projects"
- **Which index** it queries
- **Which vector field** it uses
- **Which filters** are applied, and which are optional and default off

**`rag_lookup_case_history`'s docstring must additionally carry the
multi-tenancy note** for future engineers: if Agent Improve ever serves
multiple organisations, this tool must filter by tenant. It is recorded in the
docstring rather than only in this document because the docstring is what
someone editing the tool will read (Appendix B item 1).

---

## 32. Phase skills — SKILL.md

*Supersedes: REFACTORING §83, §84; ARCHITECTURE.md §8.4; CLAUDE.md §8.3.*
**Status: RATIFIED.** Loaded by `DMAICSkillsMiddleware` (§19.2).
> **Scope:** the mechanism is platform; the instantiation below is Agent Improve's — progressive disclosure, `FilesystemBackend`, and `allowed-tools` matching the phase subset are platform; the five skills being *DMAIC phases* is Improve's


Five phase skills under `agent-improve/skills/`, following the agentskills.io
SKILL.md standard:

```
dmaic-define-phase/SKILL.md
dmaic-measure-phase/SKILL.md
dmaic-analyse-phase/SKILL.md
dmaic-improve-phase/SKILL.md
dmaic-control-phase/SKILL.md
```

### Each skill's `allowed-tools` MUST match that phase's subset in §30

**Skill and tool binding must not drift apart.** A skill describing a tool the
executor was not given produces a coach that promises something it cannot do.

### Progressive disclosure — three levels

| Level | When | What loads |
|---|---|---|
| 1 | Startup | Skill **descriptions only** — under 2K tokens for all five combined |
| 2 | On demand | Full phase instructions, when the coach enters that phase |
| 3 | On demand | Reference files, when explicitly needed |

Level 2 is reached by the coach calling a registered `load_skill(name)` tool.

### Storage backend: `FilesystemBackend`

Git-versioned alongside the code, **so a skill change is reviewable in the same
PR as the code that depends on it.** `ContextHubBackend` is deferred to the
multi-deployment stage.

### Each SKILL.md must carry

- The **seven-step sequence** for every computation tool in its phase's
  `allowed-tools` (§43)
- A **worked example per field** for show-first coaching (§43)
- An **A→F session flow** with a visible progress count
- A **Document Layout** section showing the Belt what the gate document will
  look like when complete
- Upload handling and `CoachingResponse` capture instructions
- **The contradiction-check instruction** (§37, DECISIONS §R1) — every turn,
  compare the Belt's input against the prior committed values already in
  context and set `contradiction_flag` (§20) on a material contradiction.
  **Flag only material numeric or categorical contradictions of
  gate-committed values. Never prose rephrasing, and never refinement of a
  not-yet-committed current-phase value** — that constraint is what keeps
  false positives down, and it lives in the instruction because there is no
  threshold to tune (§37)

### Two distinct kinds of skill exist in this repository

**They must not be confused:**

| Kind | Location | Consumed by |
|---|---|---|
| **Development-workflow skills** | `.claude/skills/` | Claude Code — e.g. `/verify-current-version` |
| **Runtime coaching skills** | `agent-improve/skills/` | The coach, at runtime |

---

# Part VII — Validation and Gates

*This is the quality machinery. It is large because the system's entire value
proposition is that a gate document it approved is worth trusting.*

---

## 33. The nine-step HITL gate

*Supersedes: REFACTORING §2, §44, §53; ARCHITECTURE.md §3.6; CLAUDE.md §9.1, §9.6.*
**Status: RATIFIED.**

| Step | What happens | Quality check for |
|---|---|---|
| 1. Executor runs | Coach produces its response; extraction captures fields | — |
| 2. **Validation stack** | Four layers, cheapest first (§34). Failures feed back with accumulated per-layer feedback. **The Belt does not see this loop** | **The AI's work** |
| 3. Interrupt fires | `gate_review_node` pauses; the Belt sees validated output | — |
| 4. Belt reviews | Belt checks AI-captured values for accuracy | — |
| 5. Belt edits *(optional)* | Belt corrects wrong fields → `belt_edits` | — |
| 6. **Policy advisory** | Validates the Belt's edits against required-field policy, cross-phase consistency and previously approved values. **Non-blocking** | **The human's edits** |
| 7. Belt approves | Gate document assembled and written to the Store **and** `PhaseState.final` (§33.2) | — |
| 8. Checkpoint saves | State committed **only now** | — |
| 9. Next phase | Supervisor reads `gate_passed`, static edge advances | — |

### Two quality checks, two actors, two moments

**The grader blocks at step 2; the advisory does not block at step 6.** That
asymmetry is deliberate and is the core of the design:

- **Step 2 checks the AI's own output.** There is no reason to show the Belt
  work already known to be below standard.
- **Step 6 checks the Belt's edits.** The Belt is the domain expert. The
  advisory offers a **second opinion before the decision, not a veto after
  it.**

A system that blocked the Belt's own corrections would be asserting that its
judgment outranks theirs on their own project. It does not.

### Gates are one-way doors, with exactly one defined exception

**Once a gate passes and the phase record commits, that phase is locked.** The
supervisor advances on a static edge (§15) and there is no "go back a phase"
control anywhere in the API or the UI.

**The only way back is the re-approval cascade (§37)**, and it is deliberately
heavy: it makes the affected phase and every downstream phase provisional, and
it runs compensating actions against Azure Blob and `improve_case_index` (Part
IX). That weight is the point — a cheap reverse gate is a gate the Belt learns
to walk through twice.

### Implementation: graph-level `interrupt()`

**`HumanInTheLoopMiddleware` is BANNED for gates** (§19.9). Use graph-level
`interrupt()` + `Command(resume=...)`.

### 33.1 The two-node split

| Node | Responsibility |
|---|---|
| `gate_review_node` | Fires the interrupt, presents validated fields, **stops** |
| `gate_apply_node` | Reads the Belt's response, applies corrections, runs the policy advisory, assembles and writes the document, routes onward |

**Collection and application are separated** because they happen either side of
a process boundary — the interrupt may be resumed hours or days later, in a
different process. A single node spanning that boundary would have to be
re-entrant in a way neither half needs to be.

**Frontend sequence:**

1. Belt clicks **Submit Gate** → `POST /gate/submit`
2. Backend resumes the graph; validation stack runs; `gate_review_node`
   interrupts with the validated field payload
3. Payload returned and rendered for review
4. Belt edits if needed, then `POST /gate/approve` (or `/gate/reject`)
5. Backend resumes from the interrupt; `gate_apply_node` runs the advisory,
   applies edits, writes artifacts to the Store, commits the checkpoint, and
   the parent's static edge advances the phase

### 33.2 `gate_apply_node` writes the gate document TWICE

**This is the write the entire store-mediated handoff depends on.** Every
cross-phase read in §9 assumes the previous phase's gate document is in the
Store; this is what puts it there.

**Specification:** **§58.16 — S-F07**, behaviours B1 and B5.

**Both writes are required.** The Store write and the checkpoint commit are
separate operations; **a crash between them would leave state saying the gate
was not applied while the Store says it was.** `final` holding the same dict
means the resumed graph can see what was approved without re-reading the Store
— which is why `final` is a `dict` and not a `str` (§6).

**Store path:** `store/projects/{case_id}/artifacts/{phase}.json`

**The gate document contains, and nothing may be omitted:**

| Part | Source |
|---|---|
| All captured fields (strings — §7) | `artifacts` |
| The cross-phase reference dicts, where they apply | `artifacts` |
| `computation_results` | `artifacts["computation_results"]` |
| `citations` | `PhaseState.citations` |
| `uploads` | `PhaseState.uploads` |
| `acknowledged_gaps` | Tier 2 fields the Belt chose to proceed without (§35) |

**`gate_attempts` and `validator_feedback` reset here, and only here.** The
retry budget is per gate passage.

### 33.3 The checkpoint commits only after Belt approval

Never before. This is what makes the Belt's approval meaningful rather than
ceremonial — before step 7, nothing about the phase is committed, so a Belt who
rejects loses nothing but the turn.

---

## 34. The four-layer validation stack

*Supersedes: REFACTORING §48, §68, §69; ARCHITECTURE.md §3.7; CLAUDE.md §9.2, §9.3.*
**Status: RATIFIED.** **Canonical home.**

All four run inside step 2, before the interrupt.

| Layer | Checks | Mechanism | Model | Fires | Implemented by |
|---|---|---|---|---|---|
| **2a** Coherence | Real, meaningful, conclusive? Catches gibberish, vague non-answers, self-contradiction, off-topic, parroting the Belt | Lightweight LLM | `coherence`, 0.1 | **Every turn** | **`CoherenceMiddleware`** (§19.7) |
| **2b** Field presence | All **Tier 1** fields populated? `DMAICGateValidator` static methods | **Deterministic** | None | Gate only | `validation_stack` node |
| **2c** Constraints | Addresses budget / timeline / risk / measurement? | Lightweight LLM | `constraint`, 0.1 | Gate + key mid-conversation decisions | `validation_stack` node |
| **2d** Quality rubric | Does the **gate document** meet DMAIC standards per criterion? **Tier 1 fails, Tier 2 warns.** Uses `PHASE_RUBRIC` | LLM grader | `grader`, 0.1 | Gate only | `validation_stack` node |

### Layer 2a is middleware; layers 2b–2d are the node

**Not a cosmetic distinction.** Layer 2a fires **every coaching turn**, which a
gate-boundary node cannot do. Layers 2b–2d fire once, at the gate, and cannot
sensibly run per turn — field presence is meaningless before the phase is
finished. **One conceptual stack, two mechanisms.** Do not try to move 2a into
the node or 2b–2d into middleware.

### Layer 2d is NOT `DMAICGraderMiddleware`

Two graders exist and confusing them is a violation — the full distinction is
**§36**. In one line: Layer 2d grades the **gate document** against
`PHASE_RUBRIC` at the boundary; `DMAICGraderMiddleware` grades the **coach's
process** against `COACHING_QUALITY_RUBRIC` every turn.

### Run cheapest first

Each layer fires only if the previous passes. Layer 2b is deterministic and
free; there is no reason to spend a grader call on a document missing a Tier 1
field.

### The counter and the feedback

**`PhaseState.gate_attempts`** is the counter; **`PhaseState.validator_feedback`**
is the accumulated feedback (§6). **Neither may live in route scope, and
neither may be per layer.**

**The iteration cap is 3, SHARED across all four layers**, with accumulated
feedback. Not three per layer. Feedback is specific — *"your previous answer
did not address timeline or risk mitigation"* — never *"try again."*

### Layer 2b is the only deterministic layer, deliberately

**Coherence and constraint checks are LLM calls because format checks cannot
detect content failures.** A length check does not detect fluent nonsense. A
keyword check rejects a decision that addresses cost without using the word
"budget."

Layer 2a costs roughly **$0.01–0.02 per phase session** at 20–40 turns. **This
is settled and is not to be re-optimised into a regex.**

### Per-phase constraint sets

Constants in `core/prompts.py`: `DEFINE_CONSTRAINTS`, `ANALYSE_CONSTRAINTS`,
`IMPROVE_CONSTRAINTS`, `CONTROL_CONSTRAINTS`. Measure is covered by its rubric.

**Value-dependent constraints are supported and required** where a constraint
is conditional on another field — the risk-mitigation check fires only when
`risk_level == "low"`, because a low-risk project should say how it *stays*
low-risk, whereas a high-risk project's decision inherently involves risk.

**Every attempt at every layer is logged to `step_log` as a dict** (§11).

### 34.1 Where each check fires

| Layer | Every turn | Key decision moments | Gate boundary |
|---|---|---|---|
| 2a Coherence | ✅ | ✅ | ✅ |
| 2b Field presence | ❌ | ❌ | ✅ |
| 2c Constraint | ❌ | ✅ | ✅ full check |
| 2d Quality rubric | ❌ | ❌ | ✅ last |
| Mid-phase contradiction (§37) | ✅ | ✅ | ✅ |

### 34.2 The self-healing hierarchy and the transparency principle

| Level | Trigger | Behaviour | Belt sees | Retry |
|---|---|---|---|---|
| **1 — Silent** | Coherence failure mid-turn | System retries internally | **Invisible** | Max 2, then degraded |
| **2 — Coached** | Constraint failure on a Belt proposal | Coach teaches toward a better formulation | Transparent, collaborative | **No cap** |
| **3 — Validated** | Full four-layer check at the gate | Belt sees pass/fail, corrects, approves | Transparent, Belt approves | Max 3, accumulated |
| **4 — Escalated** | Attempts exhausted | System defers with unresolved constraints named | Transparent, Belt is arbiter | None |

> **Design principle: coached improvement is key, because silent is not
> transparent.**
>
> The default posture is transparency. **Silent retry is the narrowly scoped
> exception — coherence only** — justified because showing a Belt that the AI
> produced gibberish adds no value and erodes trust. They see the corrected
> response. Everything else is visible and collaborative.
>
> **Level 2 having no retry cap is deliberate.** Capping it would mean the
> coach eventually accepts a weak root cause, which is exactly the outcome
> DMAIC discipline exists to prevent. A constraint failure on a Belt's
> proposal is **a teaching moment, not an error.**

**Never downgrade the coherence or constraint checks to format checks.**

---

## 35. Two tiers of field, and the `warning` verdict

*Supersedes: REFACTORING §42, §68; ARCHITECTURE.md §3.7.1; CLAUDE.md §9.7; DECISIONS §C1, §C2.*
**Status: RATIFIED.**
> **Scope:** the mechanism is platform; the instantiation below is Agent Improve's — the two-tier split, the `warning` verdict and the acknowledged-gap record are platform; the Tier 1 field lists are DMAIC fields and are Improve's

### The problem this solves

**Layer 2b and Layer 2d must not be able to contradict each other.** Before
this rule the gate blocked on a required-field list while the grader graded
against a rubric covering a different set — so a phase could pass the gate and
then be failed by the grader on a criterion the gate never asked for. A
contradiction with no defined resolution.

**Every rubric criterion is now classified into one of two tiers.**

| Tier | Layer 2b | Layer 2d | Belt's options |
|---|---|---|---|
| **Tier 1 — gate-required** | **Blocks** | Can `fail` | Must supply it |
| **Tier 2 — rubric-recommended** | Not checked | At worst `warning` | Add it, or proceed with an acknowledged gap |

### Three distinct things check these fields, and conflating them is a design error

| Mechanism | Checks | Where |
|---|---|---|
| The `{Phase}Output` schema (§40) | **Types and shape** | `phases/{phase}/schema.py` |
| `DMAICGateValidator` | **Presence of Tier 1 fields** | Layer 2b (§34) |
| `PHASE_RUBRIC` | **Meaningful quality per criterion, both tiers** | Layer 2d (§34) |

**A `root_cause_statement` reading "there are problems" satisfies the schema
and satisfies the presence check, and fails the rubric.** That gap is the
entire reason Layer 2d exists — the first two mechanisms cannot see content,
only shape and presence.

**The tiers are what keep 2b and 2d from contradicting each other.** 2b blocks
only on Tier 1; 2d can `fail` only on Tier 1 and can `warning` on either. There
is no longer a criterion the grader can fail that the gate never asked for.

### Tier 1 by phase

| Phase | Tier 1 fields | Count |
|---|---|---|
| **Define** | `problem_statement`, `voc_summary`, `project_scope`, `goal_statement`, `process_map_sipoc` (**dict**), `issues_and_barriers` | **6** |
| **Measure** | `baseline_mean`, `data_collection_plan`, `xy_matrix_summary`, `vital_few_xs`, `detailed_process_map` (**dict**), `stability_assessment`, `issues_and_barriers` | **7** |
| **Analyse** | `root_cause_statement`, `root_cause_validation`, `practical_significance`, `issues_and_barriers` | **4** |
| **Improve** | `selected_solution`, `pilot_result`, `experiment_justification`, `issues_and_barriers` | **4** |
| **Control** | `control_plan` (**dict**, 5 sub-plans), `post_improvement_metric`, `issues_and_barriers` | **3** |

**`issues_and_barriers` is Tier 1 in every phase.** Every real project has
blockers; a Belt reporting none has not looked. If there genuinely are none,
the Belt writes "none identified at this stage" — **a conscious statement, not
a silent skip.**

**It is NOT the same field as `acknowledged_gaps`.** `issues_and_barriers` is
Belt-stated real-world blockers; `acknowledged_gaps` is system-generated and
records skipped Tier 2 *fields*. **Merging them is a violation.**

### The grader's verdict has three statuses

**Specification:** **§62.1 — S-C20**.

**A gate MAY pass with warnings. A gate may NEVER pass with failures.** Only
Tier 1 criteria may produce `fail`.

**A Tier 2 gap the Belt proceeds past MUST be recorded**, never silently
dropped:

```python
"acknowledged_gaps": ["baseline_sigma — Belt accepted gap"]
```

The next phase's planner reads it from the Store and factors it into the
coaching plan.

### Why two tiers

**A gate that blocks on every criterion teaches Belts to fill fields
mechanically — complete gate documents, worse projects.** Tier 1 catches
genuinely incomplete phases; Tier 2 coaches toward best practice while leaving
the judgment with the Belt, who knows the project. **The audit trail then
records conscious decisions rather than silent omissions.**

### The grader is belt-level aware

It reads `belt_level` from the case record:

```
if belt_level == "Black Belt":  flag DOE as a Tier 2 recommendation
if belt_level == "Green Belt":  suppress it
```

**DOE is the only belt-gated item left.** Three others left this list:

| Item | Now |
|---|---|
| X-Y matrix | **`xy_matrix_summary`, Tier 1, all Belts** — it produces the vital few X's that Analyse cannot start without |
| Statistical problem statement | **`statistical_problem_statement`, Tier 2, all Belts, in Analyse** — not Define |
| FMEA | **Not tracked in any schema** — §41 |

**Stability is no longer belt-gated or advisory.** It is
`stability_assessment`, **Tier 1 for both belt levels** — a baseline computed
across an unstable process is not a baseline, so it blocks the gate rather than
warning about it (§41).

---

## 36. Two graders — and why they are not redundant

*Supersedes: REFACTORING §42; ARCHITECTURE.md §3.4.1; CLAUDE.md §8.2; DECISIONS §B2.*
**Status: RATIFIED.**

**THERE ARE TWO GRADERS IN THIS ARCHITECTURE. Confusing them is a violation.**

| | `DMAICGraderMiddleware` | Validation stack Layer 2d |
|---|---|---|
| **Where** | Middleware, inside the executor (§19.8) | The `validation_stack` node (§34) |
| **When** | **Every coaching turn** (`after_agent`) | **Once**, at the gate boundary |
| **Rubric** | **`COACHING_QUALITY_RUBRIC`** — one, shared | **`PHASE_RUBRIC`** — five, one per phase |
| **Grades** | The coach's **process** | The **gate document** |
| **Sees** | One response | The complete field set |

**Never point `DMAICGraderMiddleware` at a phase rubric, and never point Layer
2d at `COACHING_QUALITY_RUBRIC`.**

### Why both exist

**The middleware catches coaching-process failures in real time.** A coach that
accepts "poor morale" as a root cause is corrected *before the Belt sees the
response*, preventing eight further turns built on a weak foundation.

**The validation node catches document-product failures a per-turn check cannot
see.** Four Analyse fields can each look sound in isolation while the root
cause discusses "error rate" and the baseline it references is "cycle time."
**Cross-field and cross-phase consistency is only visible once the document is
complete.**

Different failure modes, different visibility windows. Neither substitutes.

### `COACHING_QUALITY_RUBRIC`

A single constant in `core/prompts.py`, identical for all five phases:

```
- Coach must not accept vague or unmeasurable statements as captured fields
- Coach must not invent data, metrics, or values the Belt didn't provide
- Coach must not do the Belt's work (writing their problem statement for them)
- Coach must stay on the current phase's topic
- Coach must challenge weak inputs with specific follow-up questions
- Coach must reference methodology when guiding (not just opinion)
- Coach must show a concrete example of a completed answer before asking
  the Belt to produce theirs
- Coach must not provide external URLs from training data. When referencing
  methodology, retrieve via rag_lookup_methodology and weave the content into
  natural coaching voice
- Coach must not dump raw statistical output without explanation. When calling
  a computation tool, the coach must educate the Belt on the concept first,
  explain why it matters for their project, then run the tool
```

**Coherence is NOT in this rubric.** It moved to `CoherenceMiddleware` (§19.7).
Any rubric entry for coherence is stale.

### Mechanism, both graders

- Model: `grader` role, temperature **0.1** (§21)
- `max_iterations=3`. On `max_iterations_reached`, output passes through **with
  a warning flag visible to the Belt**
- Verdict is **per criterion, not overall** (§35)
- Feedback injected back to the coach is **per criterion and specific** — never
  "try again"
- **Layer 2d is belt-level aware** (§35)

### Three criteria are verified deterministically, not by judgment

`causal_hypothesis`, `solution_linked_to_root_cause` and
`post_improvement_metric` are cross-phase reference dicts (§7). **The grader
reads the referenced phase's gate document from the Store and checks the named
field carries the named value** — a lookup, not an opinion.

Criteria depending on a computation are checked the same way, by scanning
`artifacts["computation_results"]` for the relevant `tool` entry.

### The ratified rubric coverage

Define (`problem_statement`, `voc_summary`, `business_case`, `project_scope`,
`team`, `goal_statement`) · Measure (`baseline_mean`, `baseline_sigma`,
`measurement_system_validated`, `data_collection_plan`, stability) · Analyse
(`root_cause_statement`, `root_cause_validation`, `causal_hypothesis`,
`ruled_out_causes`) · Improve (`selected_solution`,
`solution_linked_to_root_cause`, `pilot_result`, `implementation_plan`) ·
Control (`control_plan`, `sustainability_check`, `post_improvement_metric`,
`improvement_delta`, `financial_impact_verified`, `handover_documented`,
`lessons_learned`, `transferability`). Each criterion carries its tier (§35).

**Rubrics evolve from production experience without changing the grader
mechanism** — that separation is the point.

---

## 37. Mid-phase contradiction and the re-approval cascade

*Supersedes: REFACTORING §38; ARCHITECTURE.md §3.8; CLAUDE.md §9.4, §9.5.*
**Status: RATIFIED.** Implemented by `ContradictionDetectionMiddleware` (§19.6).

### The check runs every turn, not only at gates

**Mechanics — semantic detection by the coach, as of DECISIONS §R1:**

- **The coach compares** the Belt's input against the prior committed values
  already in its context (injected at `before_agent`, §19.1). The instruction
  governing this lives in each SKILL.md (§32)
- On a **material** contradiction of a gate-committed value it sets
  `CoachingResponse.contradiction_flag` (§20) — **in the response call that
  already runs every turn. No additional LLM call**
- `ContradictionDetectionMiddleware` (§19.6) reads the flag on `after_agent`
  and **raises `HITLInterrupt`**; the coach's response is suppressed and the
  interrupt payload goes to the Belt
- Payload: the contradicted field, its approved value and approving phase, the
  proposed value, the Belt's own words, and the two Belt-facing options below

**The check still runs every turn** — the coach runs every turn, so moving
detection into it changes the mechanism, not the cadence.

> **Detection is best-effort semantic, not deterministic**, and that is an
> honest downgrade from what the previous mechanism *claimed*. It detected
> nothing while looking deterministic (§19.6). **§50's always-referenceable
> all-gate-fields tab is the acknowledged human backstop** for contradictions
> the coach's judgment misses.

**The Belt's two options:**

| Option | Consequence |
|---|---|
| **Update** the approved value | The affected phase's gate document becomes provisional; downstream phases need re-review |
| **Keep** the approved value | The Belt clarifies they misspoke; no state change |

### There is NO tolerance threshold, and none may be added

**In production DMAIC, baseline means, sigma levels and target metrics are
taken seriously.** Silent drift across weeks is exactly the failure mode a
coaching system exists to prevent.

***"The delta was small enough"* is not acceptable when downstream analysis
depends on the value.** A root cause validated against a baseline of 4.2 is not
automatically valid against 3.8, and the difference between those two numbers
is precisely the kind of thing a threshold would swallow.

**Any change to a previously gate-approved value is a mini-gate, never a silent
overwrite.**

### The re-approval cascade

If the Belt confirms a new value, **the affected phase and every downstream
phase that depends on it** return to provisional state and require re-review.

This is deliberately heavier than a soft override. **Silent invalidation of
downstream analysis is not acceptable.**

### The cascade has a hard dependency on compensating actions

**When it fires, the affected phase's `error_handler` compensating logic MUST
run** to clean up stale values already written to Azure Blob and
`improve_case_index` (Part IX).

**A cascade that marks phases provisional but leaves published values in place
is worse than no cascade** — state and index then disagree, silently, and the
system reports a phase as needing review while continuing to serve its old
conclusions.

---

## 38. Escalation

*Supersedes: REFACTORING §2; ARCHITECTURE.md §3.9; CLAUDE.md §3.5.*
**Status: RATIFIED.** File: `escalate.py`.

The escalation subgraph is reachable two ways:

1. **Conditional edge** when the validation stack exhausts its shared cap of 3
2. **The `request_human_approval` tool** (§29.2), when the coach judges a
   decision beyond its remit

**`gate_attempts` is persisted in checkpointed state, never in route scope**
(§6) — escalation triggers on a counter that survives the request boundary, or
it does not trigger at all.

**At escalation the system defers with unresolved constraints named** (§34.2
Level 4). It does not silently accept, and it does not silently block: the Belt
becomes the arbiter with the specific failures in front of them.

---

# Part VIII — The DMAIC Domain

*Parts II–VII describe a coaching harness that is largely methodology-agnostic.
This Part is where DMAIC itself enters the schema.*

---

## 39. The five phases

*Supersedes: REFACTORING §2; ARCHITECTURE.md §13.*
**Status: RATIFIED.**

| Phase | What the Belt produces | Gate blocks on |
|---|---|---|
| **Define** | A measurable problem, its scope, a SMART goal, the customer's voice, a SIPOC with KPIs | 6 Tier 1 fields |
| **Measure** | A validated baseline, a data collection plan, a detailed process map, prioritised X's, a stability assessment | 7 Tier 1 fields |
| **Analyse** | A specific root cause, the evidence validating it, and how much of the problem it explains | 4 Tier 1 fields |
| **Improve** | A selected solution, a pilot result, and a stated position on experimentation | 4 Tier 1 fields |
| **Control** | A five-part control plan and the post-improvement measurement | 3 Tier 1 fields |

**Phase order is fixed and enforced by static edges** (§15). There is no
skipping and no reordering.

### The measurement thread that runs across three phases

Three fields carry one measurement chain, and **the grader verifies the same
measurement points carry different values** at each end:

```
Define    process_map_sipoc["process_kpis"]      — WHAT is measured
Measure   detailed_process_map["baseline_kpis"]  — the BEFORE values
Control   post_improvement_metric                — the AFTER values
```

**This is the spine of a DMAIC project.** A project that cannot show
before-and-after on the same measurement point has not demonstrated
improvement, whatever else its gate documents contain.

---

## 40. The five `{Phase}Output` schemas

*Supersedes: REFACTORING §18, §82; ARCHITECTURE.md §4.10.2, §4.10.3; CLAUDE.md §10.7.*
**Status: RATIFIED.** File: `phases/{phase}/schema.py`. **Canonical home.**

**Every field is `str`** except the cross-phase reference dicts and the three
structured dicts (§41). **Every schema carries the same four gate-metadata
fields.**

**Specification:** the five schemas are **§63.1–§63.5 — S-C27 to S-C31**. The field counts,
gate-metadata sourcing and cross-schema rules below stay here.

### Field counts

| Phase | Total | Tier 1 | Tier 2 | Gate metadata |
|---|---|---|---|---|
| Define | **15** | 6 | 5 | 4 |
| Measure | **14** | 7 | 3 | 4 |
| Analyse | **13** | 4 | 5 | 4 |
| Improve | **13** | 4 | 5 | 4 |
| Control | **15** | 3 | 8 | 4 |

### The four gate-metadata fields

On all five schemas, always from the same four sources:

| Field | Source |
|---|---|
| `computation_results` | `artifacts["computation_results"]` (§7) |
| `acknowledged_gaps` | `validation_stack.get_acknowledged_gaps()` (§35) |
| `citations` | `PhaseState.citations` (§6) |
| `uploads` | `PhaseState.uploads` (§6) |

**`citations` and `uploads` were on `PhaseState` but missing from the Output
schemas in an earlier revision** — the evidence trail reached state and then
stopped, never arriving in the document that records what the phase was
grounded in.

### Two fields are on all five schemas

`issues_and_barriers` (Tier 1) and `secondary_metrics` (Tier 2). **Adding a
field to one phase without considering the other four is how the cross-phase
gaps arose in the first place.**

### 40.1 Gate assembly

Runs in `gate_apply` after Belt approval. **No LLM call** — Pydantic validation
over values already captured.

**Specification:** **§62.11 — S-F28**. Only Define's assembly was ever written —
**SPEC-GAP G-28**.

**The access pattern encodes the tier, and the difference is deliberate:**

| Tier | Access | Why |
|---|---|---|
| **Tier 1** | `artifacts["field"]` | **A `KeyError` here is correct** — Layer 2b should have blocked the gate, so reaching assembly without the field is a bug that must surface loudly |
| **Tier 2** | `artifacts.get("field", "")` | An empty value **records that the Belt proceeded without it** (§35) |
| Cross-phase dicts | `artifacts.get("field", {})` | Same, with the right empty type |

**Gate assembly must reference every field in the schema.** A field in the
schema that assembly never sets is a field that silently never reaches the
Store.

---

## 41. Structured dict fields, and FMEA

*Supersedes: REFACTORING §68; ARCHITECTURE.md §4.10.5–§4.10.7; CLAUDE.md §10.8; DECISIONS §C5, §C6.*
**Status: RATIFIED.**

**Three Tier 1 fields are structured dicts**, distinct from the three
cross-phase reference dicts of §7:

| Field | Phase | Sub-fields |
|---|---|---|
| `process_map_sipoc` | Define | `suppliers`, `inputs`, `process_steps`, `outputs`, `customers`, **`process_kpis`** |
| `detailed_process_map` | Measure | `steps`, `cycle_times`, `resources`, `value_vs_waste`, `measurement_points`, **`baseline_kpis`** |
| `control_plan` | Control | `documentation`, `monitoring`, `response`, `training`, `aligning_systems` |

### The grader checks every sub-field is populated

**A `process_map_sipoc` with four of six keys filled is the partial-map failure
the field exists to catch.** A Belt who maps steps 3–5 of a seven-step process
produces a project that cannot show improvement, because the baseline never
covered the whole thing.

**`process_kpis` and `baseline_kpis` are the two sub-fields that carry the
measurement thread** (§39). They are the reason these are dicts rather than
prose: a coaching conversation produces text no downstream planner can read and
no grader can check.

### `control_plan` is `dict`, never `str`

**Specification:** all three structured dicts are **§63.7 — S-C33**.

**Tier 1 — the gate requires the dict, and the grader checks all five
sub-plans.** A single string cannot show that four were done and one was
skipped, and **a Training Plan written but never delivered is the most common
real Control failure.**

### `stability_assessment` is checked BEFORE capability

**An unstable process has special causes, so a baseline Cpk computed across
them is an average of two different processes, not a capability figure.**

Coaching order: **stability → special causes if unstable → capability.** This
is why the field is Tier 1 rather than advisory — a capability number computed
in the wrong order is worse than no number, because it looks authoritative.

### `experiment_justification` is Tier 1 and does not require an experiment

It requires a **decision**, stated as one of three:

1. DOE conducted
2. Simplified one-factor experiment
3. **No experiment needed** because the solution follows from root cause
   analysis

**All three are valid.** The failure it catches is **drifting past the
question**, not skipping DOE.

### FMEA has no field in any schema, and none may be added

Not `fmea_summary`, not `updated_fmea`, not an FMEA sub-key anywhere.

**FMEA is heavy manufacturing methodology** built around severity × occurrence
× detection scoring of physical failure modes. Agent Improve's typical case is
service or transactional DMAIC, where `xy_matrix_summary` and `vital_few_xs`
already do the prioritisation job without the RPN overhead.

**Requiring an FMEA would push every Belt through a heavy artefact to satisfy a
field** — precisely the mechanical field-filling that §35's two tiers exist to
prevent.

**If a Black Belt performs one, it lives in `uploads`** as an attached
document, and the BB SKILL.md may present it as an available technique. The
schema does not track it, the grader does not ask for it, and no gate blocks on
it.

---

## 42. Cross-phase reference fields in practice

*Supersedes: ARCHITECTURE.md §4.7; CLAUDE.md §10.6.*
**Status: RATIFIED.** Schema defined in §7; this is how the three are used.

| Field | Phase | Tier | References |
|---|---|---|---|
| `causal_hypothesis` | Analyse | 2 | Measure's `baseline_mean` |
| `solution_linked_to_root_cause` | Improve | 2 | Analyse's `root_cause_statement` |
| `post_improvement_metric` | Control | **1** | Measure's `baseline_mean` |

**Only `post_improvement_metric` is Tier 1**, and that asymmetry is
deliberate: a Control phase that cannot link its result back to the Measure
baseline has not demonstrated improvement at all, whereas an Analyse phase
without an explicit hypothesis link is weaker but not void.

**The grader verifies each link by lookup, not judgment** (§36) — it reads the
referenced phase's gate document from the Store and checks the named field
carries the named value.

---

## 43. The coaching method

*Supersedes: REFACTORING §42; ARCHITECTURE.md §3.4.2; CLAUDE.md §0.8, §8.2; DECISIONS §D1–§D5.*
**Status: RATIFIED.** Enforced by `COACHING_QUALITY_RUBRIC` every turn (§36).

**This is where the system's teaching behaviour is specified.** It is
enforcement, not aspiration: every rule below is a rubric criterion checked on
every coaching turn.

### 43.1 The seven-step computation pattern

**Every computation tool, every time.** The coach follows this sequence
whenever it calls one of the 20 (§30):

| # | Step |
|---|---|
| **1** | **Educate on the concept** — what this *is*, plain language, a real-world analogy, and what the output numbers will mean |
| 2 | **Explain why now** — why the Belt needs it at this point in their project |
| 3 | **Guide data preparation** — what format is needed; check uploads via `rag_lookup_evidence` |
| 4 | **Run the computation** — call the tool |
| 5 | **Interpret their result** — plain language, no jargon (§50) |
| 6 | **Visualise** — `propose_diagram` where applicable |
| 7 | **Coach the next move** — what it means for the project |

**Step 1 is mandatory and is the one most often skipped.** Never assume the
Belt knows what a Cpk, a p-value or a control limit *is*. Teach the concept and
say what the numbers will mean **before** producing any.

**Returning a p-value with no concept and no interpretation is a rubric
failure, not a style preference.** A Belt handed `t_statistic: 4.23,
p_value: 0.001` has a number they cannot act on and cannot defend at a gate.
Because the grader fires **every turn**, the dump is caught before the Belt
sees it.

**Every SKILL.md carries the seven-step sequence for each computation tool in
its phase's `allowed-tools`** (§32).

### 43.2 Show before asking

**For every field**, the coach:

1. **Shows a concrete example** of a completed answer
2. **Explains why it works** — what makes it good
3. **Invites the Belt to build theirs** in the same shape

**Never ask "what is your baseline metric?" before showing what a good baseline
metric looks like.** A Belt who does not know the target shape produces a weak
answer, and the coach then spends turns correcting what it could have prevented
in one.

Each SKILL.md carries a worked example per field. Example, Define:

```
Let me show you a completed SIPOC before you build yours:

Suppliers → Inputs → Process Steps → Outputs → Customers
HR system, Managers → Employee records, Role requirements →
  1. Receive request, 2. Screen candidates, 3. Interview,
  4. Select, 5. Contract, 6. Start date set →
Hired employee, Onboarding pack → Hiring manager, New employee

Key KPIs: Time-to-hire (days), offer acceptance rate (%)

Notice the KPIs are in the SIPOC itself — that's what makes it
DMAIC-useful rather than just a process map.

Now build yours for [project name].
```

**This interacts with §22's anti-hallucination guards and the interaction is
load-bearing.** Show-first puts worked examples with plausible numbers directly
in front of the model on every turn. The guards exist precisely because of
this: **a template showing `baseline_mean: 4.2` is not data**, and the coach
must never capture it as though the Belt said it.

### 43.3 The A→F session flow

Each SKILL.md structures coaching as a six-stage flow **with a visible progress
count the Belt can see at any time**:

```
"We're working through the Measure phase — Step 3 of 6."
```

| Stage | What happens |
|---|---|
| **A** | Orientation — context setting, phase purpose |
| **B** | Mandatory Tier 1 fields, one by one, show-first |
| **C** | Computation tools, seven-step pattern |
| **D** | Cross-phase references where applicable |
| **E** | Tier 2 fields — advisory, the Belt decides |
| **F** | Gate readiness check (`check_gate_status()`) and submission |

### 43.4 The live gate document preview

**The coach shows the Belt the gate document as it fills in**, using
`check_gate_status()` output — what is captured, what is missing, and what the
final document will look like:

```
📋 Your Define Gate Document (4 of 6 required fields complete)

✅ Problem Statement: "Invoice error rate at 12.3% causes..."
✅ VOC Summary: "Customer complaints focus on..."
⬜ Project Scope: [not yet captured]
✅ Goal Statement: "Reduce invoice error rate from 12.3% to <3%..."
✅ Process Map (SIPOC): [complete — 6/6 sub-fields]
⬜ Issues & Barriers: [not yet captured]

Tier 2 fields: Business Case ✅  Team ✅  Charter ⬜ (optional)

We're on Step 5 of 6. Let's capture Project Scope next.
```

**The Belt should always know what they are building toward.** Each SKILL.md
carries a Document Layout section for its phase.

### 43.5 No external URLs

**The coach must not provide external URLs from training data.** When
referencing methodology it retrieves via `rag_lookup_methodology` and **weaves
the content into its own coaching voice**.

Two reasons, and the second is the stronger: a URL from training data may be
dead, moved, or wrong; and a coach that hands out links is outsourcing the
teaching it exists to do.

### 43.6 What the coach must not do

From `COACHING_QUALITY_RUBRIC` (§36), the prohibitions:

- **Not accept vague or unmeasurable statements** as captured fields
- **Not invent data, metrics or values** the Belt did not provide
- **Not do the Belt's work** — writing their problem statement for them
- **Not stray off the current phase's topic**
- **Not accept weak inputs unchallenged** — challenge with specific follow-up
  questions

**"Not doing the Belt's work" is the one most easily rationalised away.** A
coach that writes a good problem statement produces a good gate document and a
Belt who cannot write the next one. The gate document is not the product; the
Belt's capability is.

---

# Part IX — Reliability

---

## 44. The failure pipeline

*Supersedes: REFACTORING §66, §79; ARCHITECTURE.md §9.1.*
**Status: RATIFIED.**

Seven steps, of which Step 0 is the newest and fires first:

| Step | Mechanism |
|---|---|
| **0** | **Per-node timeout** — `TimeoutPolicy(run_timeout=45)` (§45) |
| 1 | Error classification — transient vs permanent (§48) |
| 2 | Context recovery — save partial results, resume |
| 3 | Circuit breaker — 3 failures / 30s → OPEN, 60s reset (§46) |
| 4 | Safe reopen — one probe in HALF-OPEN (§46) |
| 5 | Graceful degradation — the fallback chain (§46) |
| 6 | Smart fallbacks — alternative models, cache, degraded mode (§46) |

**Step 0 matters because of its position.** The timeout bounds the wall clock
at 45 seconds and `NodeTimeoutError` is what *triggers* the chain — so fallback
fires **before the Belt notices the delay**, rather than after retries have
already burned the budget.

**LangGraph ≥1.2.6 required.** Steps 0 and 2 are native primitives at that
version and are unavailable at the currently installed 1.1.10 (§1).

---

## 45. Timeouts and compensating actions

*Supersedes: REFACTORING §49, §79; ARCHITECTURE.md §9.2; CLAUDE.md §3.6.*
**Status: RATIFIED — BLOCKED on the LangGraph upgrade.**

### Per-node timeouts — required on every phase executor node

**Specification:** the registration is behaviour B3 of **§58.11 — S-F02**; the handler is
**§64.3 — S-F29**.

**`TimeoutPolicy` also accepts `idle_timeout`**, refreshed by progress signals,
alongside the wall-clock `run_timeout`. A bare number or `timedelta` is
accepted as a hard cap that is *not* refreshed. `run_timeout=45` is the
ratified value; `idle_timeout` is available if a long legitimate tool call ever
needs distinguishing from a hang.

**Prefer `set_node_defaults` over repeating the policy on every node.**
LangGraph provides graph-wide defaults for `retry_policy`, `error_handler`,
`timeout` and `cache_policy`, which is a better fit for a rule phrased as
"required on **every** phase executor node" than copying the arguments five
times.

**Two constraints on defaults, both from the reference:** `cache_policy` and
`error_handler` defaults apply to **regular nodes only** — caching an error
handler's result is unsafe, and **a handler must never catch itself.**

### Composition order — retries run BEFORE the handler

**When a node attempt raises any exception — including `NodeTimeoutError` from
a timeout — the retry policy decides whether to retry, and the error handler
runs only after retries are exhausted.**

This matters for reading §44's pipeline correctly: Step 0's timeout does not
jump straight to compensation. It raises, the retry policy sees it first, and
only a fully-exhausted node reaches `error_handler` and the fallback chain.

### Node-level error handlers — required on every node with external writes

Every node that writes to Azure Blob, `improve_case_index` or
`improve_evidence_index` gets an `error_handler=` that **undoes the external
write** and routes to a degraded response:

**Specification:** **§64.3 — S-F29**. It reads and writes four undeclared state fields —
**SPEC-GAP G-03** and **G-06** — and routes to an undefined node,
**SPEC-GAP G-35**.

### Hand-written Saga orchestrators are BANNED

**LangGraph provides the mechanism.** Custom Saga classes and hand-written
compensating-action frameworks were the pre-1.2 workaround; `error_handler=` is
the native replacement.

### Two dependencies on this rule, both correctness-critical

1. **The re-approval cascade** (§37). When it fires, the affected phase's
   handler must run, **or state and index disagree silently.**
2. **Time-travel debugging.** Resuming from an earlier checkpoint rolls back
   **state, not external writes.** Time travel is only correct for nodes that
   have a handler — without one, you rewind the graph and leave the blob and
   the index holding values from a future that no longer exists.

### Graceful shutdown — **UNCONFIRMED — MAY NOT EXIST**

**The requirement is real and ratified.** A deployment rollout must not kill
mid-coaching sessions: they save their checkpoint and resume. **The named
mechanism is not.**

> ### ⛔ `RunControl.request_drain()` is UNCONFIRMED. Schedule no work against it.
>
> **This API was not located.** It is absent from LangGraph releases 1.2.5
> through 1.2.11 and was not found in the reference during the 2026-08-21
> verification pass. Either it predates 1.2.5, it is named differently, or **it
> does not exist.** It entered this architecture as a recommendation and was
> carried forward on citation alone; **it has never been checked against a
> release or against source.**
>
> **This is the same failure mode as `ModelRetryMiddleware(retries=...)`**
> (§19.4) — a plausible API name, adopted once, never re-verified, sitting in a
> document implementers copy. That one was caught. This one is still open.
>
> **Binding, until it is confirmed against a real release or the LangGraph
> source:**
>
> - **No implementation task may be scheduled against `request_drain()`.** Not
>   in Task 4, not in the §53.1 migration sequence, not in a Step 8 reliability
>   ticket. A task that names it is a task that may be unbuildable.
> - **The citation is not a design.** If the API does not exist, §45 needs a
>   **real fallback drain design** — the obvious candidates being a readiness
>   probe that fails while in-flight turns complete, or a shutdown hook that
>   stops accepting new `ainvoke` calls and awaits the current node — not a
>   replacement citation.
> - **Confirmation means one of:** the symbol found in the installed package,
>   or in the LangGraph source at a named version, or in the API reference with
>   a version stamp. A blog post or a model's recollection is not confirmation.
>
> Recorded in `agent-improve/docs/BIBLE_VERIFICATION_LOG.md` under *Not verified*.

**The dependency this sits behind is separate and also unmet:** everything in
this section requires LangGraph ≥1.2.6, and the venv has 1.1.10 (§53). Fixing
the version does not resolve the question above.

### `DeltaChannel` is NOT used

Beta API, and there is no production evidence that checkpoint size is a problem
yet. Deferred (Appendix B item 12) until sessions exceed roughly 200 turns.

---

## 46. The fallback chain and circuit breakers

*Supersedes: REFACTORING §66, §67; ARCHITECTURE.md §9.3, §9.4; CLAUDE.md §4.8; DECISIONS §N1.*
**Status: RATIFIED for v2.1; a v2.2 replacement is ratified and deferred.**

### The v2.1 four-level chain

```
Level 0: TimeoutPolicy(run_timeout=45)         — fires first (§45)
Level 1: gpt-4o    (operational-premium)       exponential backoff
Level 2: gpt-4o-mini (operational-model)       exponential backoff
Level 3: Azure Cache for Redis, session-scoped jittered backoff
Level 4: Degraded mode — never a hard failure to the Belt
```

**It always terminates in success.** Level 4 is not an error path; it is a
response.

### Backoff strategy is chosen per level, not globally

| Scenario | Strategy | Why |
|---|---|---|
| Managed service (Azure OpenAI) | **Exponential** | Predictable rate limiting, no thundering-herd risk |
| Shared resource (the cache) | **Jittered** | Several subgraphs may fall back simultaneously; randomising prevents a synchronised storm |

### Level 3 cache

**Azure Cache for Redis**, storing recent retrieval results keyed by query hash
+ phase, and recent coaching responses for similar questions.

**Session-scoped, not global.** Different projects have different context, and
**a cached answer from another Belt's project is worse than no answer.**

**Invalidation follows the volatility of the source, not one global TTL:**

| Source | Volatility | Consequence |
|---|---|---|
| Methodology (`improve_knowledge_index`) | **Static** — the BB eBook does not change | Cache freely, long TTL |
| Evidence (`improve_evidence_index`) | Changes on every Belt upload | Invalidate on upload |
| Case history (`improve_case_index`) | Changes as other cases progress | Short TTL |
| This project's artifacts | Changes at every gate | **A gate approval must invalidate the affected entries** |

**⚠️ Not yet provisioned** (§1).

### Circuit breakers — three-state, two instances

| Breaker | Wraps | On OPEN |
|---|---|---|
| **LLM** | Azure OpenAI calls | Coaching turn cannot happen — fall to Level 2, then degraded |
| **Search** | Azure AI Search calls | Coaching **continues** without RAG grounding — quality degradation, not availability failure |

**The asymmetry is the point.** A search outage should degrade grounding, not
stop the session.

Threshold: 3 failures in 30s trips OPEN; 60s reset; **one probe request in
HALF-OPEN** before resuming.

**Two-state (CLOSED/OPEN) breakers are not permitted.** This is a long-running
service and must recover without a restart.

### Degraded mode uses actual state, never a generic error

**Specification:** **§64.4 — S-F30**.

**Degraded mode is still a coaching interaction, not an error page.** The Belt
knows what happened, knows their work is safe, and knows how to continue.

### HTTP 400 is NOT a fallback case

**Token limit exceeded is a context-management failure.** Do not retry the same
request against a smaller model — the request is too big, and a smaller model
has a smaller window. Fix the context (§19.3).

**Every attempt is logged to `step_log` as a dict** (§11).

### 46.1 Geographic redundancy — **DEFERRED**

**The v2.1 chain has a single-region dependency.** Levels 1, 2 and 3 are all
provisioned in **Azure West Europe (Frankfurt)**. They are three different
services but one region. A Frankfurt outage does not degrade the chain a level
at a time — **it collapses Levels 1–3 simultaneously** and drops straight to
degraded mode.

The chain reads as defence in depth, and against *service* failure it is.
Against *regional* failure it is a single point of failure wearing four hats.

**This is a compliance matter, not only robustness.** DORA's ICT resilience
obligations require geographic redundancy for continuity of critical functions,
which makes a single-region chain **non-compliant for any regulated-entity
deployment** — a launch blocker for that market. EU AI Act data-governance
provisions are why the secondary region must be inside the EU.

**Ratified v2.2 replacement — five levels, two regions:**

```
Level 1: Azure OpenAI gpt-4o      — West Europe (Frankfurt) — primary
Level 2: Azure OpenAI gpt-4o      — secondary EU region (Sweden Central candidate)
Level 3: Azure OpenAI gpt-4o-mini — secondary EU region
Level 4: Azure Cache for Redis    — session-scoped response cache
Level 5: Degraded mode            — always succeeds
```

**The insertion is Level 2:** the same model in a different region, *before*
accepting a quality drop to gpt-4o-mini. **A regional outage should cost
latency, not coaching quality.**

**TPM exhaustion and regional outage are different failures, and v2.1 handles
the first correctly** — a 429 is classified transient, backoff fires, the chain
activates. The amendment addresses Frankfurt being unreachable outright, or
429s persisting past backoff tolerance with no regional escape hatch.

**Appendix B item 16.** Promotion: before production launch with real Belts.

---

## 47. Disconnect policy — what a dropped client commits

*Supersedes: DECISIONS §O3. New scope, ratified 2026-08-20.*
**Status: RATIFIED.** Part of the `thread_id` wiring step (§53.1), not a separate step.

**The question does not exist until checkpoints actually write.** While routes
dispatched nodes manually and nothing persisted, a dropped connection lost a
turn. Once `thread_id` reaches `graph.ainvoke`, it commits one.

**The finding:** once checkpoints are live, **the FastAPI handler's
control-flow shape — not the checkpointer — decides what survives a client
disconnect.** A handler that hands the graph run to a bare
`asyncio.create_task` keeps executing after the client is gone, and the run
checkpoints every node it completes. **The Belt sees nothing; the checkpoint
says the turn happened.**

### Ratified policy: ABANDON, not COMPLETE

**A silently-completed gate approval the Belt never saw is unacceptable** in a
system whose entire premise is that the Belt approves what gets committed (§33
step 7). COMPLETE is defensible for idempotent background work; **it is not
defensible for a nine-step HITL gate.** If the Belt is gone, the turn stops.

### Five requirements

| # | Requirement | Why |
|---|---|---|
| **1** | **Deliberate handler shape** — inline `await` streaming, or an explicit ABANDON policy calling `t.cancel()` in `gen()`'s `finally`. Never a bare `asyncio.create_task` with no disconnect handling | **A handler that has not chosen has chosen COMPLETE by accident** |
| **2** | **Deterministic `step_log` keys** — `f"{phase}:{turn_count}:{step_name}"`, never a raw timestamp as identity (§11) | An abandoned-then-retried turn re-executes the same logical step; timestamp keys record it as two events |
| **3** | **Azure Blob lease as the per-thread concurrency guard** | Two tabs on one `case_id` means two writers on one `thread_id`. Postgres advisory locks are the natural mechanism and are unavailable until the §8 migration; this is also exactly the exposure the untested-concurrency limitation names |
| **4** | **A reconciliation sweep for abandoned threads that EXCLUDES `interrupt()`-paused threads** | A thread paused at a gate is indistinguishable from an abandoned one by "no recent activity" alone. A sweep that misses this cleans up Belts who are simply thinking about their gate review overnight |
| **5** | **`thread_id` / `case_id` derived from the authenticated session, never client-supplied** | A client-supplied `thread_id` lets any caller resume any Belt's session. `thread_id` is `case_id` and `case_id` is the tenancy boundary |

**`gate_apply_node`'s Store write needs no change.** It is already idempotent
by key — `store.put(...)` overwrites rather than appends, so replaying it is
safe. **The exposure is in `step_log` (requirement 2) and concurrent writers
(requirement 3), not there.**

---

## 48. Structured errors

*Supersedes: REFACTORING §64; ARCHITECTURE.md §9.5; CLAUDE.md §12.3.*
**Status: RATIFIED.** File: `core/errors.py`.

All external service failures use one schema:

**Specification:** **§64.1 — S-C34**.

**Two fields are read by machinery, not humans:**

- **`severity`** is what lets the circuit breaker distinguish "retry" from
  "stop trying"
- **`retry_recommendation`** is what the fallback chain reads to choose its
  backoff strategy (§46)

A free-text error message cannot drive either decision, which is why this is a
schema rather than a logging convention.

**A 4xx from retrieval is `permanent` / `do_not_retry`** (§27) — it is our
malformed query, and retrying fails identically.

---

# Part X — Operations

---

## 49. API surface

*Supersedes: ARCHITECTURE.md §10; CLAUDE.md §1.1, §1.4, §1.5.*
**Status: RATIFIED.** File: `gateway/routes.py`.

### One runtime

**The compiled graph is the only runtime path.** A route that does anything
beyond `await graph.ainvoke(...)` / `astream_events(...)` plus envelope
marshalling is a violation.

**Nothing in `gateway/routes.py` may dispatch nodes manually.** This is the
rule the v1 codebase most conspicuously breaks, and it is why the checkpointer
wired at Step 2.1 does not yet take effect (§53).

### Async by default

- All FastAPI endpoints are `async def`
- All graph invocations use `await graph.ainvoke(...)` or
  `graph.astream_events(...)`
- All LLM calls use `await llm.ainvoke(...)`
- All Azure SDK calls use the `aio` variants where available

### Endpoints

| Endpoint | Purpose |
|---|---|
| `POST /ask` | Non-streaming coaching turn — retained for clients that cannot use SSE |
| `POST /ask/stream` | **The standard path.** Server-Sent Events; the frontend renders tokens as they arrive |
| `POST /gate/submit` | Triggers the validation stack and the gate interrupt (§33.1) |
| `POST /gate/approve` | Resumes from the interrupt with approval |
| `POST /gate/reject` | Resumes from the interrupt with rejection |
| `GET /cases`, `GET /cases/{id}` | Case records |
| `GET /registry` | Case registry |

**All of them invoke the same compiled graph object.**

### Envelopes are Pydantic v2

Request and response schemas live in `gateway/schemas.py` (§54).

---

## 50. UI and language rules

*Supersedes: REFACTORING §77; ARCHITECTURE.md §11; CLAUDE.md §13.*
**Status: RATIFIED.**

### Plain language always

- **No methodology jargon in any team-facing string.** Technical terms appear
  only as small secondary grey labels
- **Every AI data request includes a concrete example with column names**
- Every AI suggestion using cross-agent data carries a **visible source
  citation**

**Jargon is the failure mode a coaching product is most prone to**, because the
methodology has a rich vocabulary and using it feels like expertise. To a Belt
who does not yet have the vocabulary, it reads as gatekeeping.

### Citations

Format: `agent_origin`, `index_name`, `document_id`, `relevance_summary`.

**Retrieval citations surface `source_file` and `page_number`** (§23) — "this
came from page 47 of the BB eBook." That specificity is what makes a citation
checkable rather than decorative.

### Contextual feedback

**Spinner messages are contextual, never generic:**

```
Generic (bad):     "Loading…"
Contextual (good): "Retrieving methodology…"
                   "Validating your root cause…"
                   "Checking gate completeness…"
```

A multi-hop Analyse turn (§26) takes measurably longer than a simple coaching
response; the message sets the expectation.

### Connection status before the first interaction

The Belt sees system health before sending their first message. **A Belt who
opens the interface and immediately sees "Azure OpenAI — disconnected" knows to
wait.** Without it, the first coaching turn fails with a confusing error and
they do not know why.

### The gate review screen

**Shows extracted fields before approval**, editable, with an explicit approve
action (§33 steps 4–7). This is the UI surface of the entire HITL design — if
it renders fields the Belt cannot edit, step 5 does not exist.

### The live gate document

Rendered from `PhaseState.artifacts` (§43.4). **Both the field content and the
progress counts derive from that one source; there is no stored
`completeness_score`** (§5).

**Tier 1 and Tier 2 get separate progress bars, not one blended count.** A Belt
at 6/6 required and 0/5 recommended **can pass the gate**; a single blended
percentage would read as 55% and imply otherwise.

**The LangSmith run id is surfaced for support escalation** (§51) — a Belt
reporting a bad turn can name the exact trace.

### The all-gate-fields tab is the contradiction backstop

**Every gate field, every phase, open and closed, always referenceable.** Not
only the current phase and not only the incomplete fields.

**This is a deliberate second layer, not a convenience.** Contradiction
detection is best-effort semantic judgment by the coach (§37, §19.6,
DECISIONS §R1), and judgment misses. **A Belt who can see every committed
value at any moment can catch what the coach did not** — which is why this tab
is architecture rather than UI polish, and why it must stay reachable from any
phase rather than being scoped to the phase in flight.

### The conflict resolution panel

**The UI surface of §37.** When contradiction detection fires, the Belt sees
the field name, the previously approved value **with its approval timestamp and
gate**, the proposed new value, and the two options.

**Choosing "update" must surface which downstream phases become provisional
*before* the Belt confirms**, not after. The re-approval cascade is deliberately
heavy (§33); a Belt who discovers its cost only once it has fired was not given
the choice the design intends them to have.

---

## 51. Tracing and observability

*Supersedes: REFACTORING §45; ARCHITECTURE.md §12; CLAUDE.md §11.*
**Status: RATIFIED.**

### LangSmith is mandatory

```env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=...
LANGCHAIN_PROJECT=agentlean-improve
```

**Production environments without LangSmith fail startup with a clear error.**
Dead tracing config — the v1 state — is a CRITICAL violation.

### `@traceable` on every custom function

**LangSmith traces LangChain runnables and LangGraph nodes automatically. It
does NOT trace plain Python functions.** Without `@traceable`, the logic
*between* nodes is invisible and a gate failure surfaces as a 500 with no
indication of which layer failed.

REQUIRED on every function that:

- Extracts fields from LLM responses
- **Validates gate criteria — all four layers of §34**
- Scores completeness
- Makes routing decisions outside LangGraph node routing
- Calls an external Azure service directly, outside a LangChain runnable

### What gets traced

Every graph invocation (parent span) · every node (child span) · every LLM call
(prompt, response, token counts, cost) · every tool call (arguments, result) ·
every retrieval (query, top-k results) · every validation layer.

### P50/P99 latency is a coaching quality signal

**Not just an ops metric.** High P99 degrades the Belt's experience directly.
The usual outlier is **multi-hop retrieval combined with a grader call on the
same turn**; fixes in order of preference: caching (§46 Level 3), a faster
grader model, and reordering the validation stack cheapest-first (already
mandated, §34).

### Logs

Structured logs via `logging`. Every node logs entry, exit, and the state-slice
keys it returned.

**Every request gets a UUID4 `request_id`, propagated to child operations**, and
every log line carries `request_id`, `case_id`, `phase`, `node_name` and
`duration_ms`. Those five fields are what make a log searchable by the thing the
Belt can actually name — their case — rather than only by timestamp.

---

## 52. Evaluation and regression testing

*Supersedes: REFACTORING §75; ARCHITECTURE.md §14; CLAUDE.md §12.*
**Status: RATIFIED, sequencing deliberate.**

### Built alongside the refactor, not before it

**Establishing a baseline against the current system would produce a baseline
of "bad."** The suite becomes load-bearing when the coach, retrieval tools and
grader are wired — that is when output quality changes. Infrastructure steps
(graph structure, state schemas, checkpointer) do not affect coaching quality
and do not need eval coverage.

### The dataset is authored jointly, not generated

**Coaching quality judgments are domain judgments.** A generated dataset
measures agreement with a model rather than correctness. Claude proposes
examples from the ratified architecture and DMAIC domain; the Belt-expert
reviews and corrects.

### Minimum viable suite

| Dimension | Requirement |
|---|---|
| Size | 20–30 examples, 4–6 per DMAIC phase |
| Categories | Realistic coaching turns · edge cases · tool-calling scenarios · failure/ambiguous cases · historical production data |
| Metrics | Accuracy (field extraction) · relevance · reasoning quality · tool usage · safety (no invented methodology) |
| Evaluator order | Deterministic ($0) → LLM-judge relevance (~$0.01) → LLM-judge reasoning (~$0.02) |
| **Regression threshold** | **Block release if any metric drops >10% from baseline** |
| Run frequency | Every commit touching system prompts, graph structure, or model config |
| Cost per run | ~$0.60 for 20 examples |

**Output format:** JSON or Python ready for LangSmith's `create_dataset` API.

### Rubrics and the eval dataset are complementary, not duplicative

| | Rubrics (§36) | Eval dataset |
|---|---|---|
| Define | What good looks like **for the grader** | Whether the **whole system** produces good outcomes |
| Run | In production, every gate | In CI, every commit |
| Catch | Per-turn and per-document quality | Regressions across releases |

**This is also why grader temperature is pinned at 0.1** (§21): a grader
returning different verdicts across runs makes these thresholds meaningless.

### Two open validation questions this suite answers

1. **Whether planned multi-hop should extend beyond Analyse** (§26,
   **UNVERIFIED**)
2. **Whether the retrieval similarity threshold needs calibration** (Appendix B
   item 6)

---

## 53. Configuration, dependencies and deployment

*Supersedes: REFACTORING §72, §74, §76; ARCHITECTURE.md §15; CLAUDE.md §11.4, §16.*
**Status: RATIFIED.**

### Fail-fast environment validation

Validate all required credentials at startup, **before the first request**:

```
AZURE_OPENAI_KEY        — coaching LLM
AZURE_SEARCH_API_KEY    — retrieval        (NOT "AZURE_SEARCH_KEY")
LANGCHAIN_API_KEY       — observability
```

Missing credentials **exit 1 with a clear message**. This integrates with
Docker health checks — a container failing startup receives no traffic.

**`.env` hygiene:** the app loads `agent-improve/.env`. A root `.env` can
silently shadow values depending on `load_dotenv()` search order — audit and
remove it if redundant.

### Dependency floor

**All versions below verified against PyPI on 2026-08-21.**

| Package | Installed | Latest | Note |
|---|---|---|---|
| `langgraph` | **1.1.10** | **1.2.11** | **BLOCKER** — floor is **≥1.2.6** |
| `langchain` | 1.2.13 | **1.3.16** | Pins `langgraph>=1.2.11,<1.3.0` |
| `langchain-core` | 1.3.3 | — | `langchain` 1.3.16 requires **≥1.6.0** — a larger jump than the installed version suggests |
| `langchain-openai` | 1.1.11 | — | let pip resolve |
| `langchain-community` | 0.4.1 | — | supplies `AzureSearch` (§24) |
| `langsmith` | 0.7.3 | — | |
| `langchain-classic` | 1.0.3 | **1.0.8** | Retains legacy classes we do **not** use — **presence is not permission** |
| `deepagents` | not installed | 0.4.11 stable | **Still pre-1.0** — §18's exclusion stands |

**The ≥1.2.6 floor is precisely attributable.** LangGraph **1.2.6**
(2026-06-18) carries *"nested subgraph inherits parent `checkpoint_ns`
(regression in 1.2.3)"* — the fix §16 depends on. Node-level `TimeoutPolicy`
and `error_handler` (§45) require 1.2+.

**Upgrading `langchain` resolves `langgraph` for you.** `langchain` 1.3.16
requires `langgraph>=1.2.11`, so a single upgrade satisfies the floor with
margin. **Watch `langchain-core`:** installed 1.3.3 against a required ≥1.6.0
is a three-minor jump, and is the most likely source of surprises in the
upgrade.

**Do not upgrade to a stale pin.** The previously documented 1.2.10 / 1.3.11
targets were already superseded when written. Re-resolve against live PyPI at
upgrade time.

**During the upgrade, sweep for imports from `langgraph.prebuilt`** —
deprecated, functionality moved to `langchain.agents` (§18).

### `/verify-current-version` is a mandatory checkpoint

**Not background reading.** It exists because a deprecation notice is not
sufficient guidance: during this review, `create_agent` was found to have a
reported regression relative to `create_react_agent`, and the deprecation
message pointed at a function **that did not yet exist in the installed
package**.

**Confirm a replacement is actually shipped and feature-complete in the
installed version before porting to it.**

### Infrastructure not yet provisioned

| Component | For | Status |
|---|---|---|
| Azure Cache for Redis | Fallback chain Level 3 (§46) | **Not provisioned** |
| Azure Database for PostgreSQL | `PostgresSaver` + `PostgresStore` (§8) | Provision before production launch |
| Secondary EU region | Geographic redundancy (§46.1) | Deferred, Appendix B item 16 |

### Deployment layer: FastAPI, not LangGraph Server

**LangGraph Server was evaluated and rejected on licensing.** It requires
`langgraph-api` under Elastic License 2.0, and even the self-hosted tier needs
a commercial licence key. FastAPI + LangGraph (MIT) + a custom checkpointer is
the self-hosted path without one — and it is what the system already runs.

**LangGraph Studio is adopted anyway** for local development debugging
(`langgraph dev`). It is better than anything hand-built for inspecting graph
execution, and using it locally carries no licensing obligation for the
deployed service.

### 53.1 Migration sequence

**This document describes the target.** The ordered procedure for reaching it
from the current codebase is a separate document (the Refactoring Procedure).
The binding constraints on any such sequence:

**Option B is the ratified shape:** refactor the foundation first, then build
Improve and Control on top of it. Building two more phases on the current
foundation and rewriting them later was rejected.

```
Refactor the foundation
  ├── Checkpointer wired into graph.compile()          ⚠ WIRED, INERT
  ├── SupervisorState / PhaseState split               §5, §6
  ├── thread_id through graph.ainvoke + disconnect policy   §16, §47
  ├── Phase subgraphs with private state               §12, §13
  ├── AzureBlobStore for cross-phase artifacts         §9
  ├── Explicit planner / executor nodes                §17
  ├── Three rag_lookup_* tools, multi-query + RRF      §24, §25
  ├── 20 per-phase computation tools                   §30
  ├── Eight-middleware coach stack                     §19
  ├── Four-layer validation + nine-step HITL           §33, §34
  └── Reliability: timeouts, error_handler, breaker,
      fallback chain with cache                        §45, §46
    ↓
Build Improve phase   ← on the correct foundation from the start
    ↓
Build Control phase
    ↓
Run one case end-to-end clean
    ↓
Migrate PostgresSaver + PostgresStore                  §8
    ↓
Multi-user identity, isolation, tagged observability
```

**⚠ The checkpointer is WIRED but INERT, and the distinction matters for
sequencing.** `core/graph.py` does call
`builder.compile(checkpointer=get_checkpointer())` — that part of step 2.2 is
genuinely done. But **`thread_id` appears nowhere, `ainvoke` appears nowhere,
and the compiled graph is discarded**: `gateway/routes.py` calls `get_graph()`
and then dispatches phase nodes manually (§49, Appendix E). A checkpointer that
is never invoked through the graph writes nothing.

**Zero checkpoints have ever been written.** Reading this line as "✔ done", as
earlier revisions did, invites the next reader to build on persistence that
does not exist yet.

**It is closed by the `thread_id` wiring step, not before**, and that same step
carries the five Handler-Shaped Durability requirements of §47 — which is why
§47 says it is part of that step rather than a separate one. Until it lands:
time-travel debugging is unavailable, `gate_attempts` cannot survive a request
boundary, and graph node names are still free to rename (§23.3).

**Two workstreams run alongside, not after:** the evaluation dataset (§52) and
the five SKILL.md files (§32). Both encode Black Belt domain judgment and both
inform the design as it lands.

**The phase schemas are rewritten in place** — `{Phase}PhaseInput` becomes
`{Phase}Output` in the same file. No parallel schema, no deprecation window, no
retirement step. There is no production consumer to protect, and the two models
are near-disjoint: of Define's six Tier 1 fields, exactly one name matches the
v1 schema. Two conversions bind: `team_members` from `list[TeamMember]` to a
string (§7), and `sipoc` gains `process_kpis` as its sixth key (§41).

**Until migration is complete the v1 architecture may still operate, but no
v1-style code may be ADDED.** A file is "migrated" when it is rewritten under
these rules and committed with a `refactor(arch-v2):` prefix.

---

# Part XI — Governance

---

## 54. Where code is allowed to live

*Supersedes: CLAUDE.md §2; ARCHITECTURE.md §5.*
**Status: RATIFIED.**

### Classes are permitted ONLY in these files

| Area | Files |
|---|---|
| **State and schemas** | `core/state.py` (`SupervisorState`, one only) · `core/substate.py` (`PhaseState` + variants) · `phases/{phase}/schema.py` · `storage/models.py` · `gateway/schemas.py` · `core/citations.py` |
| **Tool and validation schemas** | `knowledge/tool_args.py` · `validation/schemas.py` · `core/errors.py` |
| **Persistence** | `core/checkpointer.py` · `core/store.py` |
| **Middleware** | `middleware/grader.py` · `middleware/skills.py` · `middleware/state_injection.py` · `middleware/contradiction.py` · `middleware/coherence.py` |
| **Reliability** | `core/reliability.py` (`CircuitBreaker`) |

**All other files contain module-level functions ONLY.** Especially: graph
builders, the LLM factory, all node files, the blob client, the retriever, tool
definitions, boundary mappers, escalation, and routes.

**`DMAICGateValidator` is the one permitted exception** — it lives in
`validation/gate_validator.py` as a namespace of `@staticmethod` deterministic
checks, holding no state.

### Target folder structure

```
backend/
  core/       state · substate · store · checkpointer · llm · graph
              prompts · errors · reliability · citations · diagrams · tracing
  middleware/ grader · skills · state_injection · contradiction · coherence
  validation/ gate_validator · schemas · coherence · constraints
  knowledge/  tools · computation · tool_args · retriever · fusion
  phases/{phase}/  graph · nodes · schema · mappers
  storage/    blob · models
  gateway/    routes · schemas
  escalate.py
skills/       dmaic-{phase}-phase/SKILL.md
```

---

## 55. Anti-drift

*Supersedes: REFACTORING §45, §50, §86; CLAUDE.md §0.2, §16.3.*
**Status: RATIFIED.**

Three mechanisms, layered:

| Layer | Mechanism | Enforces |
|---|---|---|
| **Constitution** | `{agent}/CLAUDE.md` | The rules, quoted in every implementation prompt. **Per agent** — see *Scope* |
| **Skills** | `.claude/skills/verify-current-version` | Version currency at decision time |
| **Hooks** | `.claude/hooks/pre-tool-use-drift-check.py` + `deprecated_patterns.yaml` | Deprecated patterns blocked before they land |

### Rule numbers are load-bearing

`deprecated_patterns.yaml` cites `agent-improve/CLAUDE.md` rule numbers in the messages it
feeds back. **Those citations must resolve.**

| Registry pattern | Cites |
|---|---|
| `pattern-2-with-structured-output` | CLAUDE.md §4.6 |
| `pattern-3-response-content-parsing` | CLAUDE.md §4.5 |
| `pattern-4-custom-saga` | CLAUDE.md §3.6 |
| `pattern-8-bind-tools-in-phase-executor` | CLAUDE.md §4.4 |

**Renumbering any cited rule requires updating the registry in the same
commit.** A hook that cites a non-existent rule is worse than no hook.

### The registry guards code, not documentation

`agent-improve/*.md` and `agent-improve/**/*.md` are excluded on patterns 2–8.
**Governance documents must be able to name a deprecated construct in order to
prohibit it** — a registry that blocks the sentence stating a rule prevents the
documentation of that rule.

**The registry file itself is exempt from the check**, because several of its
`message:` fields necessarily quote the literals they ban. Without the
exemption the governance file could not be edited by normal tooling at all.

### Verification discipline

**Before any architectural decision:** check the `anthropic.com/engineering`
post index and the `pypi.org/project/langgraph` release history. **These move
fastest and have the most impact.**

### Reference sweeps must use raw `grep -rn`, never a gitignore-filtered tool

**Agent-facing search tools filter by `.gitignore` by design.** That makes them
fast and usually right — and structurally unable to see anything gitignored.

**A rename sweep run through a filtered tool reports clean while stale
references survive** in `.claude/settings.local.json`, in `*.bak` files, in
untracked working directories, in anything the ignore rules cover. This
happened: the 2026-08-22 rename sweep reported zero stale references, and a raw
`grep -rn` over the same tree immediately found one the filtered tool could not
reach.

**The rule:** any sweep whose conclusion is *"zero remaining references"* runs
`grep -rn <pattern> .` — unfiltered — as its final check. A filtered tool is
fine for locating things; it is **not** evidence of absence.

**This is the same failure class as the two the verification pass caught**: a
`grep-absence` check written against retired names that never existed, and a
step lookup that rendered a parse failure identically to success. **A check that
cannot fail is worse than no check, because it is recorded as evidence.**

---

### 55.1 Spec-layer governance rules

*Added 2026-08-23 with Part XII. Decision record: `agent-improve/docs/DECISIONS.md` §S1.*

**Five rules, each stated with what would catch a violation of it.** A rule
whose enforcement is "nothing" says so, rather than being assumed covered —
that is the R2 discipline, and three separate findings in this project have now
been a correct rule paired with a check that could not see what it governed.

| # | Rule | What catches a violation |
|---|---|---|
| **1** | **Spec-before-code.** A code change requires its spec entry to be updated first | A code change whose spec entry's last-modified timestamp predates it. **Checkable in git; no automation exists yet** |
| **2** | **Flag-is-canonical, register-is-derived.** The DORA register never leads the per-entry AI-ACT flags; when they disagree the flag wins and the row is regenerated | Bidirectional: every register Risk ID must trace to a flagged entry, and every flagged entry must appear in the register. Grep on Risk ID |
| **3** | **SIPOC Supplier/Customer cross-check.** For every function or node, its Customers must list it as a Supplier, and its Suppliers must list it as a Customer | Grep by entry name across Part XII. **See §66.7 F-07 — the rule ranges over peer node-to-node edges only; nested sub-components and return paths are excluded, or it produces noise** |
| **4** | **Define-once.** A class or function defined in Part XII must not have its schema or signature restated in an architecture section — those sections carry a `**Specification:**` pointer and keep their reasoning | A definition appearing in two section ranges. Grep for the class or function name followed by a definition token |
| **5** | **Selective flagging.** AI-ACT flags appear only on high-risk-surface entries — coaching output, gate approval, anything that could feed a competence, employment or certification decision | A flag on a pure utility, or a missing flag on a coaching, gate or assessment entry, is a review finding. **Judgment, not automation** — where classification is unclear the entry carries `AI-ACT-REVIEW: uncertain` rather than a guess |

**For any new rule added here: state what would catch a violation of it. If the
answer is "nothing," say so in the rule** rather than assuming coverage. A rule
with no enforcement is a rule that rots.

> **The registry cannot currently see this document, and that is finding F-01.**
> `.claude/config/deprecated_patterns.yaml` excludes `agent-improve/*.md` and
> `agent-improve/**/*.md` from patterns 2–8. **This file moved to the monorepo
> root in v1.2 and the exclusion was never updated** — so the platform
> governance document is guarded as if it were code, while the registry's own
> header names it among the documents that must be able to name a deprecated
> construct in order to prohibit it. Recorded, not fixed: a registry change is
> its own audit-trailed commit (§0.2 of `agent-improve/CLAUDE.md`).

---

## 56. Amendment procedure

*Supersedes: CLAUDE.md §18.*
**Status: RATIFIED.**

This document and an agent's `CLAUDE.md` are amended only via:

1. A new architectural decision, recorded in `agent-improve/docs/DECISIONS.md`
2. A commit updating the relevant section here and/or the rule in that agent's `CLAUDE.md`
3. Increment to the version number at the top
4. **The change log goes in `agent-improve/docs/DECISIONS.md` — in the same entry as step 1 —
   plus a one-line version note at the head of this document. This document has
   no change-log section, by design** (see *About this document*: it states
   conclusions, not their history). An agent's `CLAUDE.md` is the exception: it carries its
   own numbered `§0.x` change entries, and an amendment touching a rule there
   adds one.
5. **If a rule number cited in `deprecated_patterns.yaml` changes, the registry
   is updated in the same commit** (§55)

*Step 4 previously read only "a change-log entry", against a document that
deliberately has no change log — leaving the amender to invent a destination.
Corrected 2026-08-21.*

**Never amend a rule "in passing" while making a feature change.**
Architecture changes are separate commits.

### What requires an amendment rather than a routine change

- An eighth `SupervisorState` field (§5), a fifteenth `PhaseState` content
  field (§6), or **any new field on `CoachingResponse` (§20)** — all three are
  load-bearing schemas. `CoachingResponse`'s omission from this list until
  2026-08-22 was an oversight (DECISIONS §R1)
- A new graph node type in a phase subgraph (§13)
- A new middleware, or any change to stack order (§19)
- A new LLM role (§21)
- A tool that pushes a phase past 16 (§30)
- Any index schema change (§23.5)
- A change to the tier of any gate field (§35)
- **A change to any spec entry's schema or signature (Part XII)** — the
  spec is master and the code follows it (§55.1 rule 1)

---

# Part XII — Specification

*Parts I–XI state the architecture: what the system is, how it is shaped, and
why. This Part states the **design** — the classes, functions and interfaces
themselves, at the level where the code could be rebuilt from them. The two
layers are separated because they change at different rates: switching Azure
Blob to Azure Files changes the spec and leaves the architecture untouched.*

---

## 57. The specification layer — how to read and write a spec entry

*Supersedes: none — new Part, ratified 2026-08-23. Decision record: `agent-improve/docs/DECISIONS.md` §S1.*
**Status: RATIFIED.** **Canonical home for the entry template and the two calibrated samples.**

### Why this Part exists

This document is an *architecture* — it explains shape and reasoning. It was
not a *specification*: it did not define classes and functions to the level
where code could be rebuilt from it without inventing the missing pieces. Two
seams traced during the 2026-08-22 wiring review — the contradiction middleware
(DECISIONS §R1) and `route_after_phase` (DECISIONS §R2) — proved the gap was
real and produced exactly the endless-debugging failure this project exists to
avoid.

**The fix is the missing middle layer of Spec-Driven Development:**

| SDD layer | AgentLean artifact |
|---|---|
| Requirements — what / why | Parts I–XI of this document |
| **Design — how: classes, functions, interfaces** | **This Part** |
| Tasks — ordered implementation | `agent-improve/docs/REFACTORING_PROCEDURE.md` |

**It lives inside this document, not beside it.** A separate spec file
re-creates the drift the SSOT non-overlapping rule was written to eliminate.

### The five structural rules

1. **One document.** The spec layer is a Part of this file, never a separate
   one.
2. **Define once, reference everywhere.** Each class and function is defined
   canonically here. Architecture sections keep their *reasoning* and stop
   *redefining* — they carry a `**Specification:**` pointer instead.
3. **Layers separated by volatility.** Architecture (why — stable) precedes
   spec (how — the interfaces).
4. **Rebuild test = the completeness bar.** A subsystem's spec is complete when
   its code could be rebuilt from the spec alone, without reading the old code.
   If it cannot, there is a gap, and the gap is marked (§66) rather than
   guessed at.
5. **Spec-before-code, always.** When something changes, the spec is updated
   first. Enforced as a governance rule with a stated check (§55.1).

### Entry identity and traceability

**Every entry carries a stable ID** — `S-C##` for a class, `S-F##` for a
function or node. Tests, reviews and DORA register rows cite the ID, so a
future section renumber costs nothing.

**Every entry carries the three-way trace** required by the SDD structure:

```
**Architecture:** §N · **File:** path · **Procedure:** step X.Y
```

architecture § ↔ spec entry ↔ procedure step, all three linked, so none can
silently drift from the others.

### The entry template — three layers

A **class** entry uses Purpose, definition, field table, EARS behaviors,
invariants and failure modes. A **function or node** entry uses all three
layers below.

**Layer 1 — SIPOC at a glance.** Six rows answering, without reading code or a
sequence diagram: who triggers this, what it reads, what it does, what it
produces, who consumes it.

| Cell | Content |
|---|---|
| **Supplier** | Who calls it / what upstream node or event triggers it. Many callers → a list, each naming caller and why. **A list longer than five or six is a design smell**: the function likely does too much and should be split |
| **Input** | Parameters, state fields read, Store keys read, tools bound |
| **Process** | What it does — summary; the EARS table gives the detail |
| **Output** | Return dict slice, state fields written, Store keys written, interrupts raised, structured-response fields set |
| **Customer** | Who consumes the output / what downstream node reads it |

> **Supplier and Customer are cross-checkable, and that is the point.** If A's
> Customer is B, then B's Supplier list must include A. A mismatch is a wiring
> bug, grep-able by function name. **This is a verification surface, not
> documentation** — it would have caught `route_after_phase` mechanically: its
> Input read `gate_attempts` from `SupervisorState`, and `SupervisorState` has
> no such field (§5, DECISIONS §R2).

**Layer 2 — Behaviors, in EARS form, as a table.** EARS (Easy Approach to
Requirements Syntax) forces testable, unambiguous phrasing:

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | … | … | §.. |

- `#` gives each behavior a stable ID, so a test, a review or a DORA row can
  cite "executor B4" precisely.
- `Ref` traces each behavior to the architecture section that justifies it —
  checkable against source.

**Layer 3 — the ⚠ AI-ACT flag, selectively.** Only on functions and nodes that
touch a high-risk surface: coaching output, gate approval, or anything that
could feed a competence, employment or certification decision. **Most entries
carry no flag** — orchestration, state and utility functions are not flagged,
and a flag on a pure utility is a review finding (§55.1). Where classification
is genuinely unclear the entry carries `AI-ACT-REVIEW: uncertain` rather than a
guess in either direction.

The flag states the high-risk surface, gives an obligation→mechanism table, and
names the DORA register row it feeds (§68).

### How gaps are marked

**Where a definition is missing, or too thin to meet the rebuild test, the
entry carries a labelled placeholder and nothing is invented:**

```
> **SPEC-GAP (G-nn):** <what is missing> — to be designed with founder.
```

Every marker has a row in the **§66 gap register**, and every register row has
a marker. Forty-one gaps were identified in the 2026-08-23 conversion pass and
none were filled by it — that was the pass's binding constraint.

### 57.1 The two calibrated samples

**These two entries are the approved standard, transcribed verbatim from
`agent-improve/docs/SPEC_SAMPLES.md`.** Every other entry in this Part is built
to match one of them. They are also the canonical entries for their subjects —
`SupervisorState` is **S-C01** and `phase_executor` is **S-F04**; §58 points
here rather than restating them.

> **The only alteration made in transcription is the heading level** of each
> sample's own title line, demoted from `##` to `####` so the two do not appear
> as document sections. Every other character is as approved. In particular the
> `[tbd]` procedure references and the section citations inside them are
> reproduced as written; two of those citations look wrong and are recorded as
> findings in §66, not corrected here.

### 57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 `SupervisorState`

#### SPEC — `SupervisorState`

**Canonical definition. File: `core/state.py`. Referenced by architecture §5 (rationale), procedure step [tbd].**
*Rebuild test: `core/state.py`'s `SupervisorState` must be reconstructable from this entry alone.*

**Purpose:** The orchestration-level (Level 1) graph state. Carries only what the supervisor needs to route between phases and assemble the final result. It deliberately holds no captured fields, no gate documents, and no phase-internal working data — those live in `PhaseState` (§6) and the Store (§9). It is a `TypedDict`, not a Pydantic model, because it is consumed by `create_agent`-based nodes, which do not support Pydantic state.

**Definition:**
```python
class SupervisorState(TypedDict):
    messages:      Annotated[list[BaseMessage], operator.add]
    history:       Annotated[list[str], operator.add]
    case_id:       str
    phase_index:   int
    current_phase: str
    gate_passed:   dict[str, bool]
    final_output:  Optional[dict]
```
**Exactly seven fields. Adding an eighth requires a §56 amendment.**

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `messages` | `Annotated[list[BaseMessage], operator.add]` | The Belt↔system conversation at the orchestration level. Append-only. | `operator.add` (appended, never replaced) | each Belt turn; subgraph return | input mappers (§9), seeding `PhaseState.messages` |
| `history` | `Annotated[list[str], operator.add]` | Human-readable trace breadcrumbs, one appended per node entry. Diagnostic only — no control logic reads it. | `operator.add` | every node, on entry | trace reconstruction / debugging only |
| `case_id` | `str` | Stable project identifier. Also serves as the LangGraph `thread_id` and the first Store namespace segment. Set once, never mutated. | none (last-write-wins, but only written once) | session start | everything; identity across checkpointer + Store |
| `phase_index` | `int` | Zero-based index of the current phase in the fixed DMAIC order `[define, measure, analyse, improve, control]`. Derived from `gate_passed`; stored for readability. | none | **output mapper only** | UI progress display, readability |
| `current_phase` | `str` | Name of the phase currently executing; one of the five DMAIC phase names. Derived from `phase_index`; stored for readability. | none | **output mapper only** | routing, state injection (§9), index writes |
| `gate_passed` | `dict[str, bool]` | Maps each phase name to whether its gate has been approved. Absence of a key means "not yet reached." The authoritative signal the supervisor routes on. | none (whole-dict replace by the single writer) | **output mapper only**; re-approval cascade sets a phase `False` (§37) | supervisor advancement logic |
| `final_output` | `Optional[dict]` | The assembled final deliverable, written only when Control's gate passes. `None` until then. | none | Control's output mapper, at the final gate | API response at project completion |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | a node begins execution | append one human-readable entry to `history` | §14 |
| B2 | the output mapper runs at gate approval | write `phase_index`, `current_phase`, and `gate_passed` together in a single update; no other node SHALL write any of these three | §9 |
| B3 | a reader queries `gate_passed` for a phase name not present as a key | treat the result as "gate not passed" (absent key ≡ `False`), never as an error | §37 |
| B4 | Control's gate is approved | populate `final_output`; UNTIL that point `final_output` SHALL remain `None` | §9 |
| B5 | the re-approval cascade fires for a phase | set that phase's `gate_passed` entry to `False` rather than deleting the key | §37 |

**Invariants:**
- `phase_index` and `current_phase` are derived from `gate_passed` and MUST have exactly one writer (the output mapper). A second writer is prohibited — it converts a derived field into a competing source of truth.
- Captured fields, gate documents, and phase-internal working data MUST NOT appear on this schema (they belong to `PhaseState`/§6 and the Store/§9).
- Any proposed new field MUST name its writing node and its reading node; if either is unclear, the field is rejected (the `project_context` failure — a field with no writer whose only reader ran before it would have been written).

**Failure modes:**
- A `KeyError` on `gate_passed[phase]` is a **contract violation in the reader**, not an expected path — readers MUST use absence-tolerant access (`.get(phase, False)`), per B3.
- Reading `final_output` before Control's gate returns `None`; callers MUST handle `None` as "project not yet complete," not as an error.

### 57.3 SAMPLE 2 — FUNCTION/NODE TEMPLATE — S-F04 `phase_executor` (the coach node)

#### SPEC — `phase_executor` (the coach node)

**Canonical definition. File: `phases/{phase}/nodes.py` (one per phase). References: architecture §14 (node contract), §17 (planner/executor split), §18. Procedure step [tbd].**
*Rebuild test: the phase executor node must be reconstructable from this entry alone.*

**Purpose:** The Level 2 coaching node. Runs one coaching turn: takes the planner's strategy (`CoachingPlan`), coaches the Belt on the chosen field via an LLM with the phase's bound tools, and returns a structured `CoachingResponse` (the Belt-facing message plus captured field values). It decides *nothing* about strategy — that is the planner's job; it executes the plan.

##### SIPOC — at a glance

| | |
|---|---|
| **Supplier** (who triggers it) | `phase_planner` (§17) — control returns to the planner after each executor turn, and the planner routes back here via `Command(goto="executor")` when more coaching on the current/next field is needed |
| **Input** (what it reads) | `PhaseState.coaching_plan` (the strategy for this turn), `PhaseState.messages` (conversation), `PhaseState.artifacts` (fields captured so far), `PhaseState.phase_context` (prior-phase committed values, loaded by `before_agent`); the phase's bound tool subset (§30) via `tools=` |
| **Process** (what it does) | Runs `create_agent` with eight middlewares (§19); coaches on `coaching_plan.focus_field`; may call leaf tools in its tool loop; produces a structured `CoachingResponse`; the skill prompt directs it to flag cross-phase contradictions (§37) |
| **Output** (what it produces) | Returns a dict slice: `{"draft": {...}, "artifacts": {...merged...}, "step_log": [{...}], "messages": [...]}` — plus, in `CoachingResponse`, `contradiction_flag` (read by `ContradictionDetectionMiddleware`, §19.6) |
| **Customer** (who consumes it) | `ContradictionDetectionMiddleware` (reads `contradiction_flag`, may raise interrupt); then control returns to `phase_planner`, which decides next field / trigger gate / retry |

##### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | coach only on `coaching_plan.focus_field`; never select a different field (field selection is the planner's responsibility) | §17 |
| B2 | producing its response | return a structured `CoachingResponse` via `response_format`, never free prose parsed downstream | §14 |
| B3 | Belt input materially contradicts a prior-phase gate-approved value present in `phase_context` | populate `contradiction_flag` in the response (read by §19.6) | §37 |
| B4 | capturing one or more field values | return them in `artifacts`; never invent values not supplied by the Belt or a tool | §18 |
| B5 | a tool call in the executor loop fails | surface the failure per §27; never fabricate a substitute result | §27 |
| B6 | the executor runs | append a `step_log` entry keyed deterministically `{phase}:{turn}:{step}` | §47 |

##### ⚠ AI-ACT — high-risk surface

**This node produces coaching output that could influence a Belt's assessment or project outcome. If Agent Improve is deployed where its output feeds an employment, certification, or competence decision, this is an Annex III (employment) high-risk function (deadline 2 Dec 2027).**

| Obligation | How this node addresses it |
|---|---|
| Art. 13 (transparency) | Output is clearly AI-generated coaching; the Belt is informed they are interacting with an AI coach (UI contract, §50) |
| Art. 14 (human oversight) | The Belt is always in the loop; coaching is advisory, and no field is committed without the Belt's gate approval (§13, gate_review interrupt) |
| Art. 15 (accuracy/robustness) | Anti-hallucination guard (no invented values); four-layer validation (§35) before any gate commit; contradiction detection (§37) |
| Art. 12 (record-keeping) | Every turn logged to `step_log` and LangSmith (§51); deterministic keys ensure a complete, non-duplicated audit trail |

*Feeds DORA register row **R-EXEC-01**.*

##### DORA register row (R-EXEC-01)

| Risk ID | Function | Risk Description | AI Act Art. | Likelihood | Impact | Current Mitigation | Residual Risk | Owner | Customer Negotiation |
|---|---|---|---|---|---|---|---|---|---|
| R-EXEC-01 | `phase_executor` (coach) | AI coaching output could influence a Belt's competence/employment assessment without adequate oversight, or could assert an unverified fact | 13, 14, 15, 12 | Med | High | HITL gate approval (§13); anti-hallucination guard; 4-layer validation (§35); full audit log (§51) | Low–Med — residual depends on whether customer uses gate outputs in formal evaluation | [Provider] | *open — depends on deployment context; customer confirms whether coaching feeds formal assessment* |

### 57.4 Entry index

**73 entries — 37 classes, 36 functions and nodes.** Five carry an AI-ACT flag;
twelve carry `AI-ACT-REVIEW: uncertain`; forty-one gaps are marked and none are
filled.

| Subsystem | Section | Entries |
|---|---|---|
| Graph management — state, persistence, nodes, routing, mappers | §58 | S-C01–S-C09, S-F01–S-F13 |
| Knowledge and retrieval | §59 | S-C16–S-C19, S-F14–S-F18 |
| Tools | §60 | S-F19–S-F24 |
| The coaching agent — middleware | §61 | S-C10–S-C15 |
| Validation and gates | §62 | S-C20–S-C26, S-F25–S-F28 |
| The DMAIC gate documents | §63 | S-C27–S-C33 |
| Reliability | §64 | S-C34–S-C35, S-F29–S-F33 |
| API, UI and evidence | §65 | S-C36–S-C37, S-F34–S-F36 |
| **The gap register** | **§66** | 41 gaps |

---

## 58. Spec — graph management

*Supersedes: none — new. Definitions relocated from §5, §6, §9, §12, §13, §14, §15, §16, §17, §20.*
**Status: RATIFIED as a structure; individual entries carry their own gaps.**

**This is the spine, and it is specified first** because every other subsystem
reads or writes what is defined here.

### 58.1 S-C01 · `SupervisorState`

**Defined in §57.2** as the calibrated class sample. Architecture rationale: §5.

### 58.2 S-C02 · `PhaseState`

**Architecture:** §6 · **File:** `core/substate.py` · **Procedure:** step 3.1
*Rebuild test: `core/substate.py`'s `PhaseState` must be reconstructable from this entry alone.*

**Purpose:** The Level 2 per-phase subgraph state. Private to one phase
subgraph, checkpointed through the parent's saver under an auto-managed
`checkpoint_ns` (§16). It holds the phase's working data — the plan in flight,
what has been captured, the audit trail, the retry budget — and it is where
every value that must survive context compression lives (§19.3).

**Definition:**
```python
class PhaseState(TypedDict):
    # ── conversation plumbing (3) ───────────────────────────────
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]
    phase_context:      str

    # ── content fields (14) ─────────────────────────────────────
    coaching_plan:      Optional[CoachingPlan]
    field_index:        int
    draft:              dict[str, Any]
    artifacts:          dict[str, Any]
    step_log:           Annotated[list[dict[str, Any]], operator.add]
    belt_edits:         dict[str, Any]
    turn_count:         int
    final:              dict[str, Any]
    gate_attempts:      int
    validator_feedback: list[dict]
    citations:          list[dict]
    uploads:            list[dict]
    hop_results:        list[str]
    synthesis_output:   Optional[dict]
```
**Seventeen fields — three plumbing plus fourteen content. A fifteenth content
field requires a §56 amendment.**

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `messages` | `Annotated[list[BaseMessage], operator.add]` | The Belt↔coach conversation for this phase. Append-only; the only thing prose summarisation is allowed to compress (§19.3) | `operator.add` | input mapper seeds it; the agent loop appends | the agent loop; `SummarizationMiddleware` (§19.3) |
| `history` | `Annotated[list[str], operator.add]` | Breadcrumbs, one per node entry. Diagnostic only | `operator.add` | every node, on entry | debugging |
| `phase_context` | `str` | The framing this phase was entered with, composed at the boundary from the Store — the case record for Define, the prior phase's gate document for the rest. Never carried on parent state | none | **input mapper only** | planner; state injection (§19.1) |
| `coaching_plan` | `Optional[CoachingPlan]` | The strategy for the current turn — which field, which action, which retrieval mode. Transient: overwritten every time the planner fires, never queued | none (whole-object replace) | planner node | executor node |
| `field_index` | `int` | Which field within the phase is being coached | none | planner node | planner |
| `draft` | `dict[str, Any]` | This turn's extraction, before validation. Structured, never prose | none | executor node | validation stack; `gate_review` |
| `artifacts` | `dict[str, Any]` | Everything captured in this phase so far, keyed by field name. Values are strings, except the three cross-phase reference dicts and the three structured dicts (§7, §41). Also holds `computation_results` | none (merge by the writer) | executor, from `CoachingResponse.fields_captured`; `gate_apply`, applying Belt edits | planner, `check_gate_status()`, validation stack, gate assembly, state injection, the live gate document (§50) |
| `step_log` | `Annotated[list[dict], operator.add]` | The audit trail — HOW each thing was captured, as opposed to WHAT (§11). Dicts only; tuples are banned. Keyed deterministically | `operator.add` | validation layers, grader `on_evaluation`, the fallback chain | audit trail; written into the gate document |
| `belt_edits` | `dict[str, Any]` | The Belt's corrections made at gate step 5. A different thing from `validator_feedback`, and must stay separate | none | `gate_apply`, from the interrupt resume payload | `gate_apply` |
| `turn_count` | `int` | How many coaching turns this phase has taken. Load-bearing: it is a component of the deterministic `step_log` key (§11) | none | executor node | planner; `step_log` key construction |
| `final` | `dict[str, Any]` | The approved gate document. A `dict` and never a `str`, so a resumed graph can read what was approved without re-reading the Store | none | `gate_apply_node` | output mapper; crash recovery |
| `gate_attempts` | `int` | The shared retry counter for the four-layer validation stack. Per phase, in the checkpoint — never in route scope | none | validation stack increments; `gate_apply` resets to `0` | validation stack; the escalation edge at `>= 3` |
| `validator_feedback` | `list[dict]` | Accumulated per-attempt validation failures, each recording attempt, layer, criteria failed and specific feedback. What makes the shared cap of 3 defensible | none (append by the writer) | validation stack appends; `gate_apply` resets to `[]` | the coach, on retry |
| `citations` | `list[dict]` | Sources the coach cited this phase — `source`, `page`, `content_summary`, `turn` | none (append by the writer) | executor, from `CoachingResponse.citations` | gate document assembly |
| `uploads` | `list[dict]` | Files the Belt uploaded this phase — `evidence_index_id`, `filename`, `phase`, `uploaded_at`, `summary`. An empty list means the phase reached its conclusions from typed statements alone | none (append by the writer) | the upload handler — **see G-36** | gate document assembly; evidence context |
| `hop_results` | `list[str]` | Ordered answers from a planned multi-hop chain. `[]` on every single-hop turn. State rather than a node local, so LangSmith can see it and a resume does not lose it | none | `analyse_executor_node` | the synthesis call; the LangSmith state view |
| `synthesis_output` | `Optional[dict]` | The dedicated synthesis call's `SynthesisOutput`, dumped. `None` on single-hop turns | none | `analyse_executor_node` | the coach call |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | a phase subgraph is entered | populate every one of the seventeen fields from the input mapper; no field SHALL be left undeclared | §9 |
| B2 | the planner fires | replace `coaching_plan` entirely; it SHALL NOT be appended to or queued | §6 |
| B3 | a validation layer fails | increment `gate_attempts` by one and append one entry to `validator_feedback` | §34 |
| B4 | the gate passes | reset `gate_attempts` to `0` and `validator_feedback` to `[]`, and only `gate_apply` SHALL do so | §33.2 |
| B5 | a turn is single-hop | leave `hop_results` as `[]` and `synthesis_output` as `None` | §26 |
| B6 | any node writes `draft`, `belt_edits` or `final` | write a `dict`; a `str` SHALL never be assigned to any of the three | §6 |
| B7 | `coaching_plan` is read | read it by attribute (`coaching_plan.retrieval_hops`), never by subscript | §6 |

**Invariants:**
- `validator_feedback` (what the system said about the AI's output at step 2)
  and `belt_edits` (what the Belt corrected at step 5) are **two actors at two
  moments** and MUST NOT be merged.
- `artifacts` (WHAT was captured) and `step_log` (HOW) MUST stay separate
  fields.
- `gate_attempts` MUST be in the checkpoint. Holding it in route scope is the
  specific defect this placement fixes (§6).
- Every captured value in `artifacts` is a `str`, except the three cross-phase
  reference dicts (S-C32) and the three structured dicts (S-C33).

**Failure modes:**
- A missing key in `artifacts` at Tier 1 gate assembly is **correct behaviour**
  — Layer 2b should have blocked the gate, so the `KeyError` must surface
  (§40.1).
- `coaching_plan` is `None` before the planner's first turn; readers MUST treat
  `None` as "no plan yet," not as an error.

> **SPEC-GAP (G-03):** `PhaseState` declares no `case_id` and no phase
> identifier, and at least three specified functions read one or both off it —
> `phase_error_recovery` reads `state["case_id"]` and `state["phase"]` (§45),
> `analyse_executor_node` reads `state["current_phase"]` (§26), and
> `gate_apply_node`'s Store write needs `case_id` (§33.2). Whether these become
> declared fields (a §56 amendment against the fourteen-content-field ceiling),
> arrive through `phase_context`, or are passed by config, is undesigned — to
> be designed with founder.

> **SPEC-GAP (G-04):** `remaining_steps` is read off this state twice (§26) and
> is not a declared field. `RemainingSteps` is a LangGraph managed value that
> must be declared on the state schema to be populated; undeclared,
> `state.get("remaining_steps", 10)` returns 10 on every call and **the
> five-hop cap never fires** — to be designed with founder.

> **SPEC-GAP (G-05):** `extracted_entity` is read off this state by
> `analyse_executor_node` (§26). It is not a declared field and no writer is
> named anywhere — to be designed with founder.

> **SPEC-GAP (G-06):** `extraction_error` and `extraction_incomplete` are
> written into this state by `phase_error_recovery`'s `Command(update=...)`
> (§45). Neither is a declared field — to be designed with founder.

> **SPEC-GAP (G-38):** `field_index` is defined as "which field within the
> phase," and the ordered per-phase field list it indexes into is stated
> nowhere. §13's "advance to the next field" depends on that ordering — to be
> designed with founder.

> **SPEC-GAP (G-39):** `turn_count`'s increment contract — when it advances, by
> whom, and by how much — is unstated. It is load-bearing in §11's
> deterministic `step_log` key, so an ambiguous contract produces either
> duplicate or colliding audit entries — to be designed with founder.

### 58.3 S-C03 · Per-phase `PhaseState` variants

**Architecture:** §6 · **File:** `core/substate.py` · **Procedure:** step 3.1

**Purpose:** `DefineState`, `MeasureState`, `AnalyseState`, `ImproveState` and
`ControlState` extend `PhaseState` with phase-specific transient fields. All
use explicit `TypedDict`; `MessagesState` inheritance is not used, because the
dominant content is structured fields rather than conversation.

> **SPEC-GAP (G-19):** the phase-specific transient fields are never
> enumerated for any of the five. Their existence also interacts with §6's
> fourteen-content-field ceiling and §56's amendment rule — whether a variant's
> extra field counts against that ceiling is undecided — to be designed with
> founder.

### 58.4 S-C04 · `CoachingPlan`

**Architecture:** §6, §17 · **File:** `core/substate.py` · **Procedure:** step 6.1
*Rebuild test: reconstructable from this entry alone.*

**Purpose:** The planner's structured output — one plan per planner turn,
carried on `PhaseState.coaching_plan` and consumed by the executor. It is a
Pydantic model rather than a dict specifically so `retrieval_strategy` can
carry a `Literal` constraint: that field selects the executor's entire
retrieval path, and a typo would fall through silently to single-hop.

**Definition:**
```python
class CoachingPlan(BaseModel):
    focus_field:        str
    next_action:        str
    retrieval_strategy: Literal["single_hop", "multi_hop"]
    retrieval_hops:     list[str]     # template strings; empty for single_hop
```

**Produced by** the builder-style structured-output call on the `planner`-role
model at temperature 0.1 — a plain model invocation, not an agent, so
`response_format=` does not apply (§21). The invocation form is shown in §17.

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `focus_field` | `str` | The single field this turn coaches on. The executor may not choose a different one | none | planner node | executor node (S-F04 B1) |
| `next_action` | `str` | What the coach should do with that field this turn — ask, challenge, show an example, run a computation | none | planner node | executor node |
| `retrieval_strategy` | `Literal["single_hop", "multi_hop"]` | Which retrieval path the executor takes. Not restricted to Analyse — the planner may select `multi_hop` in any phase | none | planner node | executor node; `analyse_executor_node` |
| `retrieval_hops` | `list[str]` | Hop question templates, in order, for a planned multi-hop turn. Empty for single-hop | none | planner node | `analyse_executor_node` |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the planner produces a plan | produce it through structured output, never by parsing JSON from raw model text | §21 |
| B2 | `retrieval_strategy` is `"single_hop"` | leave `retrieval_hops` empty | §17 |
| B3 | a new plan is produced | overwrite the previous one entirely; plans SHALL NOT accumulate | §6 |

**Invariants:**
- The plan is transient; its consequences are durable. Captured values land in
  `artifacts`, sources in `citations`, the rationale in `step_log`, the
  exchange in the LangSmith trace. Nothing is lost when the next plan overwrites
  this one.
- Read by attribute, never by subscript.

> **Was defined twice.** Until the 2026-08-23 conversion this class appeared in
> full in both §6 and §17 — a define-once violation that predates this Part.
> This entry is now its only definition.

### 58.5 S-C05 · `CoachingResponse`

**Architecture:** §20 · **File:** `phases/{phase}/schema.py` or `core/substate.py` · **Procedure:** step 6.2
*Rebuild test: reconstructable from this entry alone.*

**Purpose:** The per-turn structured output of the executor, produced via
`response_format=` on `create_agent`. It carries the Belt-facing coaching text,
the fields captured this turn, the sources cited, and — only on a material
contradiction — the contradiction flag. It fires every coaching turn, and is
never substituted for a `{Phase}Output`, which fires once per phase.

**Definition:**
```python
class CoachingResponse(BaseModel):
    """Structured extraction from each coaching turn."""
    message:            str                 # coaching text the Belt sees
    fields_captured:    list[dict] = []     # [{field_name, value, source}]
    citations:          list[dict] = []     # sources referenced this turn
    contradiction_flag: Optional[dict] = None   # §37 — set only on a material
                                                # contradiction of a committed value
```

`contradiction_flag` carries five keys when set:

```python
{"prior_field":    str,   # the committed field being contradicted
 "approved_value": str,   # what was gate-approved
 "approved_phase": str,   # which phase committed it
 "proposed_value": str,   # what the Belt is now asserting
 "belt_input":     str}   # the Belt's own words, for the interrupt payload
```

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `message` | `str` | The coaching text rendered to the Belt | none | the executor's model call | the UI; appended to `messages` |
| `fields_captured` | `list[dict]` | Values the Belt supplied this turn. `value` is `Any`, deliberately: it must carry both plain strings and the three cross-phase reference dicts | none | the executor's model call | the executor node, which writes each entry to `artifacts` |
| `citations` | `list[dict]` | Sources referenced this turn | none | the executor's model call | the executor node, which extends `PhaseState.citations` |
| `contradiction_flag` | `Optional[dict]` | Set only where the Belt materially contradicts a gate-committed value. `None` otherwise, which is the overwhelmingly common case | none | the executor's model call | `ContradictionDetectionMiddleware` (S-C10) |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | every coaching turn | be produced by the executor's `response_format=`, with no additional model call anywhere in the path | §20 |
| B2 | the Belt materially contradicts a gate-committed numeric or categorical value | set `contradiction_flag` with all five keys | §37 |
| B3 | the Belt rephrases prose, or refines a not-yet-committed current-phase value | leave `contradiction_flag` as `None` | §37 |
| B4 | a captured value is one of the three cross-phase reference fields | carry it as a `dict` in `value`, not a string | §7 |

**Invariants:**
- **Adding a field to this schema requires a §56 amendment.** It is
  load-bearing in the same way `SupervisorState` and `PhaseState` are.
- `value` is `Any` and this is the one place `Any` is correct. The values
  *inside* the reference dicts are still strings.
- Structured output guarantees the flag's shape and presence, never the
  correctness of the coach's judgment in setting it. §50's all-gate-fields tab
  is the documented human backstop.

### 58.6 S-C06 · `AzureBlobStore`

**Architecture:** §9 · **File:** `core/store.py` · **Procedure:** step 3.2
*Rebuild test: reconstructable from this entry alone.*

**Purpose:** The `BaseStore` implementation that carries cross-phase artifacts.
Explicit — nodes call `put`/`get` — as opposed to the checkpointer, which
LangGraph drives automatically. It is the only mechanism that moves a value
across a phase boundary, because it is the only one that survives the process
ending between two sessions nine days apart.

**Definition:**
```python
class AzureBlobStore(BaseStore):
    def put(self, namespace: tuple[str, ...], key: str, value: dict) -> None: ...
    def get(self, namespace: tuple[str, ...], key: str) -> Item | None: ...
    def search(self, namespace: tuple[str, ...], *, query: str | None = None,
               filter: dict | None = None, limit: int = 10) -> list[Item]: ...
    def delete(self, namespace: tuple[str, ...], key: str) -> None: ...
```

**Namespaces:**

| Namespace | Keys | Contents | Written by |
|---|---|---|---|
| `("projects", case_id, "case")` | `"record"` | Case framing — title, department, belt level, leader, target date | once, at session start |
| `("projects", case_id, "artifacts")` | `"define"` … `"control"` | Each phase's approved gate document | `gate_apply_node` (S-F07) |
| `("projects", case_id, "step_log")` | timestamped | Append-only cross-phase audit trail | validation and grading paths |

**Blob prefix:** `store/projects/{case_id}/{kind}/{key}.json`

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | `put` is called with an existing key | overwrite rather than append, so a replayed write is idempotent | §47 |
| B2 | `get` is called for a key not yet written | return `None`, never raise | §9 |
| B3 | it is compiled into a graph | attach to the parent graph only; a phase subgraph SHALL compile with no store | §16 |

**Invariants:**
- The `gate_documents` namespace is retired and MUST NOT be reintroduced. A
  phase's approved artifacts and its gate document are the same object.
- The `case` namespace is a session-start copy, not a second system of record;
  `cases/case_{id}.json` stays authoritative (§10).
- The Store carries cross-*phase* data within one project. Cross-*case*
  retrieval is `rag_lookup_case_history` (S-F16). Two mechanisms, no overlap.

**Failure modes:**
- A `get` returning `None` where a prior phase's gate document was expected
  means the prior gate never applied — that is a real ordering fault, not a
  missing-data condition, and callers MUST NOT paper over it with a default.

### 58.7 S-C07 · `AzureBlobCheckpointSaver`

**Architecture:** §8, §10 · **File:** `core/checkpointer.py` · **Procedure:** step 4.2

**Purpose:** The `BaseCheckpointSaver` implementation that persists in-flight
graph state. Thread-scoped, written automatically by LangGraph after every
node, and attached to the parent graph only.

**On-blob format** (this part *is* specified, and the base64 wrapping is
required rather than decorative — `JsonPlusSerializer.dumps_typed()` returns
binary msgpack, not utf-8 text):

```json
{
  "checkpoint_type": "msgpack",
  "checkpoint_data": "<base64-encoded msgpack bytes>",
  "metadata_type":   "msgpack",
  "metadata_data":   "<base64-encoded msgpack bytes>",
  "checkpoint_id":   "<id>",
  "parent_checkpoint_id": "<id|null>"
}
```

**Paths:** `checkpoints/{case_id}/latest.json` and
`checkpoints/{case_id}/history/{checkpoint_id}.json`

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | a checkpoint is written | perform exactly one blob write, never one per key | §8 |
| B2 | two turns on one `case_id` write concurrently | use a blob ETag conditional write so the second writer retries rather than overwriting | §8 |
| B3 | it is compiled into a graph | attach to the parent graph only | §16 |

> **SPEC-GAP (G-20):** the `BaseCheckpointSaver` method set this class
> implements — the put / put-writes / get-tuple / list surface and their async
> variants — is stated nowhere, nor is which of them the Blob backend supports.
> The on-blob format above is complete; the interface is not — to be designed
> with founder.

**Known limitation, carried forward, not designed around:** the Blob
checkpointer was not tested for concurrent access and Azure Blob has no
row-level locking. Acceptable for single-developer refactoring, not for
production. The interim guard is the Blob lease of §47; the resolution is the
`PostgresSaver` migration (Appendix B item 13).

### 58.8 S-C08 · `ImproveBlobClient`

**Architecture:** §10 · **File:** `storage/blob.py` · **Procedure:** [tbd]

**Purpose:** Owner of the second Blob concern — case records as the system of
record, distinct from checkpoints. Writes on case create, on gate pass and on
file upload, and **never mid-conversation.**

**Paths owned:** `cases/case_{id}.json`, `registry.json`,
`uploads/{case_id}/{file}`

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | a coaching turn completes | NOT write the case blob; conversation history lives in the checkpoint until gate pass | §10 |
| B2 | a gate passes | write the case blob and update the registry — two separate writes, both covered by the node's `error_handler` | §10, §45 |

> **SPEC-GAP (G-21):** the class interface — method names, signatures, return
> types, and how registry updates are sequenced against case writes — is stated
> nowhere — to be designed with founder.

### 58.9 S-C09 · `storage/models.py` — the record models

**Architecture:** §10, §23.3 · **File:** `storage/models.py` · **Procedure:** [tbd]

**Purpose:** The Pydantic models for the system of record: `CaseDocument`,
`PhaseRecord`, `RegistryEntry`, and `PhaseSummaryRecord` (which feeds the five
`phase_summary_{phase}` fields of `improve_case_index`, §23.3).

> **SPEC-GAP (G-17):** all four are named — in `CLAUDE.md` §2's permitted-class
> list, in §23.3's rename scope table — and none is defined anywhere. Their
> relationship to the `{Phase}Output` gate documents (S-C27–S-C31) is also
> unstated: whether `PhaseRecord` wraps a gate document or duplicates its
> fields determines whether there are two sources of truth — to be designed
> with founder.

---

### 58.10 S-F01 · The supervisor graph — static edges

**Architecture:** §12, §15, §16 · **File:** `core/graph.py` · **Procedure:** step 4.3
*Rebuild test: `core/graph.py`'s supervisor wiring must be reconstructable from this entry alone.*

**Purpose:** Level 1. Compiles the five phase subgraphs plus escalation into one
hierarchical graph, attaches the checkpointer and store, and advances through
the fixed DMAIC order. **It makes no routing decision** — there is nothing to
reason about, so nothing reasons.

**Definition:**
```python
builder.add_edge(START,      "define")
builder.add_edge("define",   "measure")
builder.add_edge("measure",  "analyse")
builder.add_edge("analyse",  "improve")
builder.add_edge("improve",  "control")
builder.add_edge("control",  END)

graph = builder.compile(checkpointer=checkpointer, store=store)   # parent only
```

Invoked with one thread per project:

```python
await graph.ainvoke(
    state,
    config={
        "recursion_limit": 50,        # infrastructure backstop, NOT the hop cap
        "configurable": {"thread_id": case_id},
    },
)
```

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The API surface (S-F34) — `/ask`, `/ask/stream` and `/gate/*` all invoke this one compiled graph object |
| **Input** | `SupervisorState`; `config.configurable.thread_id` = `case_id`; `recursion_limit=50` |
| **Process** | Runs the phase subgraph for `current_phase`; on its `END`, follows the static edge to the next phase |
| **Output** | Updated `SupervisorState`; `final_output` at Control's gate |
| **Customer** | The API surface (S-F34), which marshals the envelope; `define_input_mapper` (S-F10) and the four remaining input mappers (S-F12) |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the graph is built | declare entry with `add_edge(START, ...)`; the superseded entry-point form SHALL NOT be used | §12 |
| B2 | a phase subgraph reaches `END` | advance on the static edge without evaluating any condition — reaching `END` already means the gate passed | §15 |
| B3 | the graph is compiled | attach checkpointer and store here and nowhere else; each phase subgraph compiles with neither | §16 |
| B4 | a run is configured | pass `thread_id = case_id`, never a per-phase or concatenated value | §16 |
| B5 | any node in the parent is defined | NOT mix a static edge and a `Command` from it — both paths would execute, silently | §15 |

**Invariants:**
- There is no conditional edge, no router function, and nothing for the
  supervisor to branch on. `route_after_phase` was deleted on 2026-08-22 and
  MUST NOT be reinstated (§15, DECISIONS §R2).
- `gate_attempts` is read only inside a phase and MUST NOT be added to
  `SupervisorState`.
- `recursion_limit=50` is an infrastructure backstop. The per-turn hop budget is
  `RemainingSteps` inside the executor (§26) — see G-04.

### 58.11 S-F02 · `build_phase_subgraph(phase, llm)`

**Architecture:** §12, §13 · **File:** `phases/{phase}/graph.py` · **Procedure:** steps 4.1, 4.4
*Rebuild test: blocked on G-01.*

**Purpose:** Builds one phase subgraph. It takes the phase as a parameter
because it must select that phase's computation-tool subset (§30).

**Definition:**
```python
def build_phase_subgraph(phase: str, llm):
    tools = UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    ...
    return builder.compile()          # NO checkpointer, NO store
```

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The supervisor graph (S-F01), once per phase at startup |
| **Input** | `phase` (one of the five DMAIC names); an LLM factory handle; `UNIVERSAL_TOOLS` (S-F14–S-F22); `COMPUTATION_TOOLS_BY_PHASE[phase]` (S-F24) |
| **Process** | Registers the five nodes of §13, wires the intra-phase edges, applies `TimeoutPolicy` and `error_handler` per §45, and compiles |
| **Output** | A compiled `StateGraph` over `PhaseState`, with neither checkpointer nor store |
| **Customer** | The supervisor graph (S-F01), which embeds it as a node |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | compiling | pass neither checkpointer nor store; writes route through the parent's saver under an auto-managed `checkpoint_ns` | §16 |
| B2 | registering nodes | register exactly the five of §13; a sixth requires a §56 amendment | §13 |
| B3 | registering the executor node | apply `timeout=TimeoutPolicy(run_timeout=45)` and `error_handler=phase_error_recovery` | §45 |
| B4 | selecting tools | bind the universal seven plus that phase's computation subset, never more than 16 in total | §30 |

> **SPEC-GAP (G-01):** the intra-phase edges this function wires are the Level 2
> `Command` routing, which does not exist — see S-F13. Until it lands, this
> entry cannot pass the rebuild test.

> **SPEC-GAP (G-33):** if `load_skill(name)` is a registered tool bound to the
> executor (§19.2, §32), it is an eighth universal tool and every phase count in
> §30 moves against the 16 cap. `UNIVERSAL_TOOLS` therefore has an undetermined
> membership — see S-F23.

### 58.12 S-F03 · `phase_planner` node

**Architecture:** §13, §17 · **File:** `phases/{phase}/nodes.py` · **Procedure:** step 6.1
*Rebuild test: blocked on G-01 and G-38.*

**Purpose:** Decides strategy and nothing else. Produces one `CoachingPlan` per
turn — which field to focus on, what action to take, which retrieval mode — and
never dispatches to a tool. It fires many times per phase: the subgraph is a
cycle, not a pipeline.

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `START` of the phase subgraph, on entry; `phase_executor` (S-F04), after every coaching turn; the `validation_stack` node (S-F05) on a failed gate attempt, carrying `validator_feedback` |
| **Input** | `PhaseState.artifacts` (what is captured), `PhaseState.field_index`, `PhaseState.phase_context`, `PhaseState.validator_feedback`, `PhaseState.turn_count`; `{PHASE}_PLANNER_PROMPT` (§22) |
| **Process** | One plain model call at `planner` role, temperature 0.1, through the builder-style structured-output call producing `CoachingPlan`. Reads `artifacts` to derive what is next — the queue is derived, never stored |
| **Output** | `{"coaching_plan": CoachingPlan, "field_index": int, "step_log": [...]}` |
| **Customer** | `phase_executor` (S-F04), which consumes `coaching_plan`; `analyse_executor_node` (S-F09) when `retrieval_strategy == "multi_hop"` |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | produce exactly one `CoachingPlan` and overwrite any previous one | §6 |
| B2 | invoked | never dispatch to a tool; tool dispatch is the executor's responsibility alone | §17 |
| B3 | deciding retrieval mode | set `retrieval_strategy` at plan time, so multi-hop is planned rather than emergent | §17 |
| B4 | re-entered after a validation failure | read the full accumulated `validator_feedback` list, not only the latest entry | §6 |
| B5 | a prior phase recorded `acknowledged_gaps` | read them from the Store and factor them into the plan | §35 |

**No AI-ACT flag.** The planner selects what is coached; it asserts nothing
about the Belt and produces no assessment. Pure orchestration.

> **SPEC-GAP (G-38):** "advance to the next field" has no defined ordering
> source — see S-C02.

> **SPEC-GAP (G-01):** whether the planner returns `Command(goto="executor")`
> versus `Command(goto="validation_stack")` on field-complete is decision point
> 1 of the Level 2 routing gap — see S-F13.

### 58.13 S-F04 · `phase_executor` node

**Defined in §57.3** as the calibrated function sample. Architecture rationale:
§13, §17, §18, §20. **Procedure:** step 6.2. **Carries an AI-ACT flag and feeds
DORA row `R-EXEC-01`.**

> **SPEC-GAP (G-07):** `ContradictionDetectionMiddleware` reads
> `state["structured_response"]` (§19.6). Whether middleware observes
> `PhaseState` or `create_agent`'s own internal agent state is stated nowhere,
> so this entry's Output cell cannot say where `contradiction_flag` is
> published — to be designed with founder.

### 58.14 S-F05 · `validation_stack` node

**Architecture:** §13, §34 · **File:** `phases/{phase}/nodes.py` · **Procedure:** step 7.2
*Rebuild test: blocked on G-01 and G-08.*

**Purpose:** The gate-boundary quality node. Runs layers 2b, 2c and 2d in that
order — cheapest first, each firing only if the previous passes — against the
complete field set, and owns the shared retry budget of three. Layer 2a is not
here: it fires every turn and lives in `CoherenceMiddleware` (S-C13).

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `phase_planner` (S-F03), when all of the phase's fields are captured and the gate is triggered |
| **Input** | `PhaseState.artifacts` (the complete field set), `PhaseState.draft`, `PhaseState.gate_attempts`, `PhaseState.validator_feedback`; `{PHASE}_CONSTRAINTS` and `PHASE_RUBRIC` (§22); `belt_level` from the case record in the Store |
| **Process** | Layer 2b — `DMAICGateValidator` Tier 1 presence, deterministic (S-C26); Layer 2c — constraint check, `constraint` role at 0.1 (S-F25); Layer 2d — `PHASE_RUBRIC` grading of the gate document, `grader` role at 0.1 (S-F26). Every attempt at every layer is logged to `step_log` |
| **Output** | On pass: routes to `gate_review`. On fail: `{"gate_attempts": n+1, "validator_feedback": [...], "step_log": [...]}` and routes back to the planner. At `gate_attempts >= 3`: routes to the escalation subgraph |
| **Customer** | `gate_review_node` (S-F06) on pass; `phase_planner` (S-F03) on fail; the escalation subgraph (S-F08) at three attempts |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | run 2b, then 2c, then 2d, and run each only if the previous passed | §34 |
| B2 | any layer fails | increment `gate_attempts` once for the attempt — not once per layer — and append specific per-criterion feedback to `validator_feedback` | §34 |
| B3 | `gate_attempts` reaches 3 | route to escalation rather than retrying again | §34, §38 |
| B4 | a Tier 1 criterion fails at Layer 2d | block the gate; a Tier 2 criterion SHALL at worst produce `warning` | §35 |
| B5 | running any layer | perform no retrieval; the rubric already encodes the methodology standards | §26 |
| B6 | a Belt proceeds past a Tier 2 gap | record it in `acknowledged_gaps` rather than dropping it | §35 |
| B7 | any attempt at any layer completes | write one `step_log` dict recording layer, attempt, status and reason | §11 |

#### ⚠ AI-ACT — high-risk surface

**This node produces the pass/fail assessment of a Belt's completed phase. Where
Agent Improve is deployed into a formal evaluation, that assessment is the
artifact the evaluation would rest on — an Annex III (employment) high-risk
function (deadline 2 Dec 2027).**

| Obligation | How this node addresses it |
|---|---|
| Art. 14 (human oversight) | Its verdict does not commit anything — it gates the interrupt at which the Belt reviews, edits and approves (§33) |
| Art. 15 (accuracy/robustness) | Layer 2b is deterministic; 2c and 2d run at temperature 0.1 so the same document gets the same verdict across runs; verdicts are per criterion, never a score |
| Art. 12 (record-keeping) | Every attempt at every layer written to `step_log` with layer, attempt, status and reason |
| Art. 13 (transparency) | The Belt sees the pass/fail and the specific criteria, not a number; `max_iterations_reached` passes through with a warning flag visible to them |

*Feeds DORA register row **R-VALSTACK-01**, which aggregates behaviors B1–B4
and B7 and Layer 2d (S-F26).*

> **SPEC-GAP (G-08):** §40 names `validation_stack.get_acknowledged_gaps()` as
> the source of the gate document's `acknowledged_gaps`. That is attribute
> access on a node, and §14 requires nodes to be module-level async functions.
> Where acknowledged gaps are produced, where they are held between this node
> and gate assembly, and what shape they take, is undesigned — to be designed
> with founder.

> **SPEC-GAP (G-01):** this node's three exits — pass, fail, escalate — are
> decision point 2 of the Level 2 routing gap, including its ownership of the
> `gate_attempts` increment — see S-F13.

### 58.15 S-F06 · `gate_review_node`

**Architecture:** §13, §33.1 · **File:** `phases/{phase}/nodes.py` · **Procedure:** step 7.3
*Rebuild test: blocked on G-02 and G-18.*

**Purpose:** Fires the interrupt. Presents the validated fields to the Belt and
**stops.** It applies nothing and decides nothing — collection and application
are separated because they happen either side of a process boundary that may be
hours or days wide.

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The `validation_stack` node (S-F05), on pass |
| **Input** | `PhaseState.artifacts` and `PhaseState.draft` — the validated field set |
| **Process** | Builds the interrupt payload and calls graph-level `interrupt()`. **No LLM call.** `HumanInTheLoopMiddleware` is banned here (§19.9) |
| **Output** | An interrupt payload rendered by the gate review screen (§50); execution stops |
| **Customer** | The API surface (S-F34), which returns the payload from `POST /gate/submit`; then `gate_apply_node` (S-F07) when the graph resumes |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | call graph-level `interrupt()` and stop; it SHALL NOT apply edits or write any field | §33.1 |
| B2 | building the payload | present every validated field in an editable form, with an explicit approve action | §50 |
| B3 | invoked | commit no checkpoint — the checkpoint commits only after Belt approval at step 8 | §33.3 |

#### ⚠ AI-ACT — high-risk surface

**This is the human-oversight surface. Article 14 is implemented here or
nowhere:** if this screen renders fields the Belt cannot edit, gate step 5 does
not exist and the oversight claim made everywhere else in this document is
false.

| Obligation | How this node addresses it |
|---|---|
| Art. 14 (human oversight) | The Belt reviews every AI-captured value before anything commits, may edit any of them, and must explicitly approve |
| Art. 13 (transparency) | Values are shown as AI-extracted and attributable to a turn; the LangSmith run id is surfaced for escalation (§50) |
| Art. 12 (record-keeping) | The interrupt payload and the resume payload are both traced |

*Feeds DORA register row **R-GATEREV-01**.*

> **SPEC-GAP (G-18):** the interrupt payload has no schema. §49 states envelopes
> are Pydantic v2 and defines none, and this payload crosses the API boundary to
> the gate review screen — to be designed with founder.

> **SPEC-GAP (G-02):** `POST /gate/reject` exists in §49 and in §33.1's frontend
> sequence, and what a rejection does — re-coach, or apply-with-edits — is
> stated nowhere. It is a coaching-philosophy ruling, not a transcription — to
> be designed with founder.

### 58.16 S-F07 · `gate_apply_node`

**Architecture:** §13, §33.1, §33.2, §40.1 · **File:** `phases/{phase}/nodes.py` · **Procedure:** step 7.3
*Rebuild test: blocked on G-02, G-03, G-08 and G-28.*

**Purpose:** The commit. Applies the Belt's edits, runs the non-blocking policy
advisory, assembles the `{Phase}Output` gate document, and **writes it twice** —
to the Store and to `PhaseState.final`. This is the write the entire
store-mediated handoff depends on.

**Definition:**
```python
# 1. The Store — what the next phase's input mapper reads
store.put(("projects", case_id, "artifacts"), phase_name, gate_document)

# 2. PhaseState — so the checkpoint is self-sufficient for crash recovery
return {"final": gate_document, "gate_attempts": 0, "validator_feedback": []}
```

**Store path:** `store/projects/{case_id}/artifacts/{phase}.json`

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `gate_review_node` (S-F06), when the graph resumes from the interrupt with `Command(resume=...)` |
| **Input** | The resume payload → `PhaseState.belt_edits`; `PhaseState.artifacts`, `citations`, `uploads`; `acknowledged_gaps` (see G-08); `case_id` and the phase name (see G-03) |
| **Process** | Applies Belt edits into `artifacts`; runs the policy advisory (S-F27, non-blocking); assembles the `{Phase}Output` by Pydantic construction with **no LLM call** (S-F28); writes the Store; returns `final` |
| **Output** | Store key `("projects", case_id, "artifacts")/{phase}`; `{"final": dict, "gate_attempts": 0, "validator_feedback": []}`; then the subgraph reaches `END` |
| **Customer** | `define_output_mapper` (S-F11) and the four remaining output mappers (S-F12), which read `final`; the next phase's input mapper, which reads the Store key; crash recovery, which reads `final` |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the Belt approves | write the gate document to **both** the Store and `PhaseState.final`; one write alone is a violation | §33.2 |
| B2 | assembling the document | use Pydantic construction over already-captured values, with no LLM call | §40.1 |
| B3 | assembling a Tier 1 field | access `artifacts["field"]` directly, so a missing field raises — Layer 2b should have blocked the gate | §40.1 |
| B4 | assembling a Tier 2 field | access `artifacts.get("field", "")`, so an empty value records that the Belt proceeded without it | §40.1 |
| B5 | the gate passes | reset `gate_attempts` to `0` and `validator_feedback` to `[]`, and no other node SHALL reset either | §33.2 |
| B6 | running the policy advisory | never block on its result — it is a second opinion before the decision, not a veto after it | §33 |
| B7 | it writes externally | do so under an `error_handler` that can undo the write | §45 |
| B8 | assembling the document | include captured fields, reference dicts, `computation_results`, `citations`, `uploads` and `acknowledged_gaps`; nothing may be omitted | §33.2 |

#### ⚠ AI-ACT — high-risk surface

**This node commits the assessed record.** Everything downstream — the next
phase's coaching, the case index, any evaluation a customer builds on top —
reads what this node writes.

| Obligation | How this node addresses it |
|---|---|
| Art. 14 (human oversight) | It runs only after explicit Belt approval; the checkpoint commits only here (§33.3) |
| Art. 12 (record-keeping) | The document carries `citations`, `uploads`, `computation_results` and `acknowledged_gaps`, so a reviewer can see what the phase was grounded in and what it consciously skipped |
| Art. 10 (data governance) | `uploads` records the complete set of external evidence; an empty list is itself a visible finding (§6) |
| Art. 15 (accuracy/robustness) | Tier 1 access raises rather than silently defaulting; the policy advisory reviews the Belt's edits before commit |

*Feeds DORA register row **R-GATEAPPLY-01**.*

> **SPEC-GAP (G-03):** the Store write needs `case_id` and the phase name, and
> `PhaseState` declares neither — see S-C02.

> **SPEC-GAP (G-28):** §40.1 shows gate assembly for `DefineOutput` only. The
> four remaining assemblies are unwritten, and §40 requires that assembly
> reference every field in the schema — see S-F28.

> **SPEC-GAP (G-02):** what this node does on a Belt rejection is unstated — to
> be designed with founder.

### 58.17 S-F08 · The escalation subgraph

**Architecture:** §38 · **File:** `escalate.py` · **Procedure:** step 7.5
*Rebuild test: not met — the entry is a stub around a gap.*

**Purpose:** Where the system defers to the Belt as arbiter, with the unresolved
constraints named. It does not silently accept and it does not silently block.

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The `validation_stack` node (S-F05) by conditional edge, when `gate_attempts` reaches 3; the `request_human_approval` tool (S-F22), when the coach judges a decision beyond its remit |
| **Input** | `PhaseState.validator_feedback` — the specific failures to put in front of the Belt. Further inputs undetermined (G-34) |
| **Process** | Undetermined (G-34) |
| **Output** | Undetermined (G-34) |
| **Customer** | **Undetermined.** §15 states escalation "never returns to the supervisor," which leaves how the run terminates unstated (G-34) |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | reached | name the unresolved constraints explicitly rather than reporting a generic failure | §34.2 |
| B2 | reached | make the Belt the arbiter; the system SHALL neither accept nor block on its own | §34.2 |
| B3 | evaluating its trigger | read `gate_attempts` from checkpointed state, never from route scope | §38 |

**`AI-ACT-REVIEW: uncertain.`** This is an oversight mechanism (Art. 14) rather
than an assessment producer, which argues against a flag; but it is also the
terminal path for a Belt whose phase could not pass, and what it records about
that may matter under Art. 12. Classification deferred rather than guessed.

> **SPEC-GAP (G-34):** the escalation subgraph has no node list, no state
> schema and no exit contract. §15's "never returns to the supervisor" and
> §12's "reached by conditional edge" cannot both be satisfied without stating
> what terminates the run — to be designed with founder.

### 58.18 S-F09 · `analyse_executor_node`

**Architecture:** §26 · **File:** `phases/analyse/nodes.py` · **Procedure:** step 6.2
*Rebuild test: blocked on G-03, G-04, G-05 and G-35.*

**Purpose:** The planned multi-hop variant of the executor, implemented for
Analyse. Runs a three-hop dependent retrieval chain inside **one** node
invocation, then a dedicated synthesis call, then hands the synthesis to the
coach call.

**Definition:**
```python
async def analyse_executor_node(state: PhaseState) -> dict:
    # The for-loop below runs inside ONE node invocation, so RemainingSteps
    # does NOT decrement between hops — LangGraph counts node transitions,
    # not Python iterations. Hence a guard at entry, not inside the loop.
    if state.get("remaining_steps", 10) <= 2:
        return {"messages": [synthesise_partial(state)]}

    plan: Plan = planner.invoke(decomposition_prompt)
    local: dict[str, str] = {"entity": state.get("extracted_entity", "")}
    hop_results: list[str] = []

    for hop in sorted(plan.hops, key=lambda h: h.hop_number):
        result = rag_lookup_methodology(
            query=hop.hop_question.format(**local),
            phase=state["current_phase"],
        )
        local[f"hop{hop.hop_number}_answer"] = result
        hop_results.append(result)

    synthesis = synthesis_llm.invoke(
        synthesis_prompt.format(**local, instruction=plan.synthesis_instruction)
    )
    return {
        "hop_results":      hop_results,              # §6 — checkpointed, visible
        "synthesis_output": synthesis.model_dump(),   # read by the coach call
    }
```

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `phase_planner` (S-F03), when `coaching_plan.retrieval_strategy == "multi_hop"` |
| **Input** | `remaining_steps` (**undeclared — G-04**), `extracted_entity` (**undeclared — G-05**), `current_phase` (**undeclared on `PhaseState` — G-03**), `coaching_plan.retrieval_hops` |
| **Process** | Entry guard; decomposition call producing `Plan` (S-C17); three `rag_lookup_methodology` calls, each templating the prior hop's answer; one synthesis call at temperature 0.1–0.2 producing `SynthesisOutput` (S-C18) |
| **Output** | `{"hop_results": list[str], "synthesis_output": dict}` |
| **Customer** | The coach call inside `phase_executor` (S-F04), which reads `synthesis_output` from state rather than a local; the LangSmith state view |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | entered with two or fewer remaining steps | synthesise from what it has and return, rather than beginning a hop chain it cannot finish | §26 |
| B2 | running the hop loop | need no internal guard — `Plan` bounds it at exactly three hops | §26 |
| B3 | synthesising | use a dedicated call at temperature 0.1–0.2, separate from the coaching call at 0.5–0.7 | §26 |
| B4 | returning | write `hop_results` and `synthesis_output` into state, never leave them in node locals | §6 |
| B5 | the recursion limit is nevertheless hit | catch `GraphRecursionError` in the coach node and turn it into a partial answer; a Belt SHALL never see a stack trace | §26 |

**UNVERIFIED, carried forward:** the planned pipeline is implemented only here.
Whether reactive tool calling is sufficient for non-Analyse turns has not been
tested, and `CoachingPlan.retrieval_strategy` is deliberately not restricted to
Analyse. Validate during the §52 eval work.

> **SPEC-GAP (G-35):** `synthesise_partial(state)` is called twice — here and
> in §26's `agent_node` illustration — and is defined nowhere — to be designed
> with founder.

### 58.19 S-F10 · `define_input_mapper`

**Architecture:** §9 · **File:** `phases/define/mappers.py` · **Procedure:** step 3.3
*Rebuild test: met.*

**Purpose:** Translates `SupervisorState` into a fully-populated `PhaseState`
for Define, composing `phase_context` from the case record in the Store. Define
has no prior phase, so its source is the record loaded at session start.

**Definition:**
```python
def define_input_mapper(parent: SupervisorState, store: BaseStore) -> PhaseState:
    """SupervisorState → DefineState. Context is composed from the store,
    never carried on parent state. Define has no prior phase, so its source
    is the case record loaded at session start (§10)."""
    case = store.get(("projects", parent["case_id"], "case"), "record").value
    return {
        "messages":           parent["messages"],
        "history":            [],
        "phase_context": (
            f"{case['title']} — {case['department']}. "
            f"{case['belt_level']} belt, led by {case['leader']}, "
            f"target {case['target_date']}."
        ),
        "coaching_plan":      None,
        "field_index":        0,
        "draft":              {},
        "artifacts":          {},
        "step_log":           [],
        "belt_edits":         {},
        "turn_count":         0,
        "final":              {},
        "gate_attempts":      0,
        "validator_feedback": [],
        "citations":          [],
        "uploads":            [],
        "hop_results":        [],
        "synthesis_output":   None,
    }
```

> **SPEC-GAP (G-42):** **the boundary mappers have no execution site.** §9
> defines them as "two plain functions per phase"; §13 states a phase subgraph
> contains **exactly five nodes**, none of which is a mapper, and forbids a
> sixth without a §56 amendment; §12 embeds each subgraph as a node of the
> parent. Whether a mapper runs inside the subgraph, inside the parent's node
> wrapper, or somewhere else is stated nowhere — and every phase boundary
> depends on it. **Surfaced by the Supplier/Customer cross-check** (§66.2) — to
> be designed with founder.

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The supervisor graph (S-F01), on entry to the Define subgraph |
| **Input** | `SupervisorState.messages`, `SupervisorState.case_id`; Store key `("projects", case_id, "case")/"record"` |
| **Process** | Reads the case record, composes `phase_context` as prose framing, and initialises all seventeen `PhaseState` fields |
| **Output** | A complete `PhaseState` |
| **Customer** | `phase_planner` (S-F03), which reads `phase_context`; every node of the Define subgraph, which reads the initialised fields |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | depend on `BaseStore` alone; it SHALL NOT be handed a blob client, and SHALL NOT read context off parent state | §9 |
| B2 | invoked | populate all seventeen fields explicitly | §6 |
| B3 | composing `phase_context` | compose it here, at the boundary; context SHALL NOT be carried on `SupervisorState` | §5, §9 |

### 58.20 S-F11 · `define_output_mapper`

**Architecture:** §9 · **File:** `phases/define/mappers.py` · **Procedure:** step 3.3
*Rebuild test: met.*

**Purpose:** Translates the finished `PhaseState` into a `SupervisorState`
update. The gate document goes to the Store; **only orchestration-relevant
values return to the parent.** This is the single site at which the three
derived orchestration values advance together — the thing that makes §5's
derived-field exemption safe.

**Definition:**
```python
def define_output_mapper(child: PhaseState, parent: SupervisorState,
                         store: BaseStore) -> dict[str, Any]:
    """DefineState → SupervisorState update. The gate document goes to the
    store; only orchestration-relevant values return to the parent."""
    store.put(
        ("projects", parent["case_id"], "artifacts"),
        "define",
        child["final"],                      # the approved gate document (§33)
    )
    return {
        "current_phase": "measure",
        "phase_index":   1,
        "gate_passed":   {**parent["gate_passed"], "define": True},
    }
```

> **SPEC-GAP (G-42):** this function has no stated execution site — see
> **§58.19 — S-F10** and §66.2.

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `gate_apply_node` (S-F07) — the Define subgraph reaches `END` only through it, so arriving here means the gate passed |
| **Input** | `PhaseState.final` (the approved gate document); `SupervisorState.case_id` and `gate_passed` |
| **Process** | Writes the gate document to the Store, then returns the three orchestration values as one update |
| **Output** | Store key `("projects", case_id, "artifacts")/"define"`; `{"current_phase", "phase_index", "gate_passed"}` |
| **Customer** | The supervisor graph (S-F01), which applies the update to `SupervisorState`; the Measure input mapper (S-F12), which reads the Store key |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | write `current_phase`, `phase_index` and `gate_passed` together in one update, as the only site that writes any of them | §5, §9 |
| B2 | updating `gate_passed` | set the phase's key to `True` by merge, never replace the dict wholesale | §5 |
| B3 | returning to the parent | return orchestration values only; artifacts and gate documents SHALL NOT travel on parent state | §5, §9 |

**Note on the duplicated Store write.** `gate_apply_node` (S-F07 B1) already
wrote this document to the same Store key. The second write is idempotent by key
(§47), so the duplication is safe — but **which of the two is the authoritative
writer is not stated in either section.** Recorded as a finding in §66; not
resolved here.

### 58.21 S-F12 · The Measure, Analyse, Improve and Control mapper pairs

**Architecture:** §9 · **File:** `phases/{phase}/mappers.py` · **Procedure:** step 3.3

**Purpose:** Same contract as S-F10 and S-F11, with one difference: their
`phase_context` is composed from the **prior phase's gate document** in the
Store rather than from the case record.

> **SPEC-GAP (G-42):** this function has no stated execution site — see
> **§58.19 — S-F10** and §66.2.

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | Input mappers: the supervisor graph (S-F01) on entry to the phase. Output mappers: `gate_apply_node` (S-F07), on reaching `END` |
| **Input** | Input mappers: `SupervisorState.messages` and `case_id`; the prior phase's Store key under `("projects", case_id, "artifacts")`. Output mappers: `PhaseState.final` |
| **Process** | Undetermined per phase (G-27) — the contract below binds, the composition does not exist |
| **Output** | Input mappers: a complete `PhaseState`. Output mappers: a Store write plus the three orchestration values |
| **Customer** | Input mappers: `phase_planner` (S-F03) and the rest of that phase's subgraph. Output mappers: the supervisor graph (S-F01) and the next phase's input mapper |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | an input mapper is invoked | compose `phase_context` from the Store — the prior phase's artifacts — and depend on `BaseStore` alone | §9 |
| B2 | an input mapper is invoked | populate all seventeen `PhaseState` fields | §6 |
| B3 | an output mapper is invoked | write the gate document to the Store and return only the three orchestration values | §9 |
| B4 | reading a prior phase's value | read it as a named field out of the structured gate document; string-interpolating a previous phase's output into the next phase's prompt is BANNED | §9 |

> **SPEC-GAP (G-27):** none of the four pairs is written. §9 gives Define's pair
> in full and asserts the rest exist. What each phase's `phase_context`
> contains — which fields of the prior gate document, in what form, and whether
> `acknowledged_gaps` is included — is undesigned, and it determines what every
> planner after Define can see — to be designed with founder.

### 58.22 S-F13 · Level 2 `Command` routing

**Architecture:** §13, §15 · **File:** `phases/{phase}/graph.py` · **Procedure:** steps 4.1, 4.4
*Rebuild test: not met. This entry is a gap marker.*

**Purpose:** The intra-phase routing that makes the subgraph a cycle. §13 draws
it, §15 states the rule that `Command` routing is for inside phase subgraphs
only — and **no `Command(goto=...)` routing code exists anywhere in this
document.**

**What is settled and binds on whatever design lands:**

| # | Constraint | Ref |
|---|---|---|
| C1 | `Command` is used inside phase subgraphs only; phase transitions are static edges | §15 |
| C2 | A node SHALL NOT mix a static edge and a `Command` — both paths execute, silently | §15 |
| C3 | `gate_attempts` lives on `PhaseState`, never in route scope | §6, §15 |
| C4 | Retry and escalation resolve inside the phase, never above it | §15 |
| C5 | A subgraph reaches `END` only through `gate_apply`, so reaching `END` means the gate passed | §15 |

> **SPEC-GAP (G-01): Level 2 `Command` routing — to be designed with founder.**
> This is a genuine design task, not a transcription. Three decision points:
>
> 1. **Planner exit.** Whether `phase_planner` returns
>    `Command(goto="executor")` or `Command(goto="validation_stack")` on
>    field-complete, and what "field-complete" is evaluated against given that
>    the per-phase field ordering is itself undefined (G-38).
> 2. **Validation stack exit.** `Command` on pass to `gate_review`; at `>= 3` to
>    escalation; otherwise back to the planner carrying `validator_feedback`.
>    This node owns the `gate_attempts` increment, and where exactly it
>    increments determines whether a partially-run stack consumes an attempt.
> 3. **Gate exit.** `gate_review` (interrupt) to `gate_apply`, **and what a Belt
>    REJECT does** — re-coach, or apply-with-edits. **This one needs a founder
>    ruling** (G-02); it is a coaching-philosophy call, not an engineering one.

---

## 59. Spec — knowledge and retrieval

*Supersedes: none — new. Definitions relocated from §24, §25, §26, §27.*
**Status: RATIFIED as a structure; individual entries carry their own gaps.**

**Index schemas are not here.** The three Azure AI Search schemas stay in §23,
which §2 names their canonical home and which §23.5 makes the mandatory landing
site for any schema change. They are data-store schemas rather than code
classes or function signatures, so the define-once rule does not reach them.
The entries below reference §23 and do not restate it.

### 59.1 S-C16 · `Hop`

**Architecture:** §26 · **File:** `knowledge/` or `phases/analyse/` · **Procedure:** step 5.2
*Rebuild test: reconstructable from this entry alone.*

**Purpose:** One step of a planned multi-hop retrieval chain. `hop_question` may
template a prior hop's answer, which is what makes the chain *dependent* rather
than three parallel searches.

**Definition:**
```python
class Hop(BaseModel):
    hop_number:   int          # 1, 2 or 3
    hop_question: str          # sub-question, may template prior answers
```

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `hop_number` | `int` | Position in the chain, 1–3. The executor sorts on it, so ordering is explicit rather than list-order-dependent | none | the decomposition call | `analyse_executor_node` (S-F09) |
| `hop_question` | `str` | The sub-question, as a format template. Placeholders resolve against `entity` and `hop{n}_answer` | none | the decomposition call | `analyse_executor_node` |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | hops are executed | sort by `hop_number`, never rely on list order | §26 |
| B2 | a `hop_question` templates a prior answer | resolve it from the accumulated local map, not from state | §26 |

### 59.2 S-C17 · `Plan` — the hop decomposition plan

**Architecture:** §26 · **File:** `knowledge/` or `phases/analyse/` · **Procedure:** step 5.2
*Rebuild test: reconstructable from this entry alone.*

**Purpose:** The decomposition call's output. **It is what bounds the hop
loop** — exactly three hops — which is why `analyse_executor_node` needs no
guard inside its loop, only at entry.

**Definition:**
```python
class Plan(BaseModel):
    reasoning:             str
    hops:                  list[Hop]     # exactly 3 dependent hops
    synthesis_instruction: str
```

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `reasoning` | `str` | Why the question decomposes this way. Traced, not shown to the Belt | none | the decomposition call | LangSmith; review |
| `hops` | `list[Hop]` | Exactly three dependent hops | none | the decomposition call | `analyse_executor_node` (S-F09) |
| `synthesis_instruction` | `str` | How the synthesis call should assemble the three answers | none | the decomposition call | the synthesis call |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | a plan is produced | contain exactly three hops, which is the loop's bound | §26 |
| B2 | a plan is produced | be produced at `planner` role, temperature 0.1, and never be shown to the Belt | §26 |

**Note.** This class and `CoachingPlan` (S-C04) are different things with
similar names: `CoachingPlan` is the per-turn coaching strategy on
`PhaseState`; `Plan` is the retrieval decomposition inside one multi-hop
executor invocation. Neither is stored where the other is read.

### 59.3 S-C18 · `SynthesisOutput`

**Architecture:** §26 · **File:** `knowledge/` or `phases/analyse/` · **Procedure:** step 5.2
*Rebuild test: reconstructable from this entry alone.*

**Purpose:** The dedicated synthesis call's structured output, dumped into
`PhaseState.synthesis_output` so the coach call reads it from state rather than
a local variable. Synthesis is separate from coaching because assembling
evidence correctly and translating it into coaching language are different
jobs, tuned at different temperatures.

**Definition:**
```python
class SynthesisOutput(BaseModel):
    evidence_chain: str                          # assembled reasoning
    key_finding:    str                          # what the coach communicates
    confidence:     Literal["high", "medium", "low"]
    caveats:        list[str]                    # limits of the hop chain
```

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `evidence_chain` | `str` | The assembled reasoning across the three hops. In the trace, so a wrong coaching answer can be attributed to bad evidence rather than bad translation | none | the synthesis call | the coach call; LangSmith |
| `key_finding` | `str` | The one thing the coach communicates | none | the synthesis call | the coach call |
| `confidence` | `Literal["high","medium","low"]` | How well the chain supports the finding | none | the synthesis call | the coach call |
| `caveats` | `list[str]` | What the hop chain could not establish | none | the synthesis call | the coach call |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | synthesis runs | run as its own call at temperature 0.1–0.2, never folded into the coaching call | §26 |
| B2 | it is produced | be written to `PhaseState.synthesis_output`, never held in a node local | §6 |
| B3 | `confidence` is `"low"` or `caveats` is non-empty | make the coach communicate the limitation rather than presenting the finding as settled | §26, §43 |

### 59.4 S-C19 · `QueryVariants`

**Architecture:** §21, §25 · **File:** `knowledge/tool_args.py` or `knowledge/fusion.py` · **Procedure:** step 5.2

**Purpose:** The structured output of the variant-generation call inside every
`rag_lookup_*` tool. Three to five rephrasings of the Belt's query, fused by RRF.

**What is stated:** it is produced by structured output, never manual JSON
parsing (§25), and it carries 3–5 variants.

> **SPEC-GAP (G-14):** the schema is named in §21's mapping table and in §25 and
> is defined nowhere — field names, whether the original query is included among
> the variants, and whether the variant count is fixed or model-chosen are all
> unstated — to be designed with founder.

---

### 59.5 S-F14 · `rag_lookup_methodology`

**Architecture:** §24, §29.2, §25 · **File:** `knowledge/tools.py` · **Procedure:** step 5.2
*Rebuild test: blocked on G-14 and G-26.*

**Purpose:** Retrieves LSS Black Belt methodology from `improve_knowledge_index`.
The authoritative source in the memory hierarchy (§22) and the only tool the
planned multi-hop chain calls.

**Signature:**
```
rag_lookup_methodology(query: str, phase: str, top_k: int = 10) -> list[Document]
```

| | |
|---|---|
| Index | `improve_knowledge_index` (§23.1) |
| Filter | `phase_relevance eq '{phase}' or phase_relevance eq 'general'` |
| Vector field | `content_vector` |
| Retrieval | Multi-query 3–5 variants + RRF, k=60 (S-F17) |

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `phase_executor` (S-F04), by model choice inside the tool loop; `analyse_executor_node` (S-F09), called directly once per hop |
| **Input** | `query`, `phase`, `top_k`; the module-level cached vectorstore |
| **Process** | Generates 3–5 query variants via structured output (S-C19); runs each against the index with the filter applied at call time; fuses with RRF; returns the top results |
| **Output** | `list[Document]`, each carrying `source_file` and `page_number` for citation |
| **Customer** | The coach, which weaves the content into its own voice; `PhaseState.citations`, via `CoachingResponse.citations` |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | called | filter on `phase_relevance`, and use `'general'` as the cross-phase value — never `'all'`, never the field name `phase` | §23.1 |
| B2 | called | generate 3–5 variants and fuse with RRF; a single-query lookup is a violation | §25 |
| B3 | the search fails | raise `KnowledgeSearchError`; it SHALL NOT return `[]`, which means "ran and matched nothing" | §27 |
| B4 | returning results | carry `source_file` and `page_number` as metadata for citation, and never use them as filters | §24 |
| B5 | gate validation is running | not be called at all — gate validation never retrieves | §26 |

**`AI-ACT-REVIEW: uncertain.`** It grounds coaching content in methodology
(Art. 15 accuracy) and §27 records a real past failure in which retrieval
breakage read to the Belt as an absence of guidance. Whether that makes it a
high-risk surface in its own right, or a mitigation belonging to
`phase_executor`'s flag, is deferred rather than guessed.

### 59.6 S-F15 · `rag_lookup_evidence`

**Architecture:** §24, §29.2 · **File:** `knowledge/tools.py` · **Procedure:** step 5.2
*Rebuild test: blocked on G-14 and G-26.*

**Purpose:** Retrieves the Belt's own uploaded documents for this case. **This is
the only channel through which external, real-world data enters AgentLean**
(§29.1), which makes it architecturally more important than "uploaded files"
suggests.

**Signature:**
```
rag_lookup_evidence(query: str, case_id: str, top_k: int = 10,
                    phase: str | None = None) -> list[Document]
```

| | |
|---|---|
| Index | `improve_evidence_index` (§23.2) |
| Filter | `case_id`; optional `phase`, default OFF |
| Vector field | `content_vector` |
| Retrieval | Multi-query + RRF (S-F17) |

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `phase_executor` (S-F04), by model choice — notably at step 3 of the seven-step computation pattern, "guide data preparation" (§43.1) |
| **Input** | `query`, `case_id`, `top_k`, optional `phase` |
| **Process** | Multi-query + RRF against the case-scoped evidence index |
| **Output** | `list[Document]` scoped to this case |
| **Customer** | The coach, for grounding a computation or a claim in the Belt's own data |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | called | filter on `case_id` always; evidence SHALL NOT leak across cases | §23.2 |
| B2 | called without an explicit `phase` | leave the phase filter OFF — cross-phase evidence retrieval is the normal case | §23.2 |
| B3 | called before the batched reindex lands | take no `order_by` argument; `uploaded_at` does not exist on the live index | §23.2 |
| B4 | results are returned | never re-sort the returned `top_k` client-side and present it as recency ordering | §24 |
| B5 | the search fails | raise `KnowledgeSearchError`, never return `[]` | §27 |

**`AI-ACT-REVIEW: uncertain.`** This tool reads Belt-supplied operational
documents, which is squarely Art. 10 (data governance) territory, and the
`case_id` filter is the only tenancy boundary in the retrieval path.
Classification deferred.

### 59.7 S-F16 · `rag_lookup_case_history`

**Architecture:** §24, §29.2 · **File:** `knowledge/tools.py` · **Procedure:** step 5.2
*Rebuild test: blocked on G-14 and G-26.*

**Purpose:** Yokoten — cross-case learning. Retrieves completed cases from
`improve_case_index` so a Belt can see what worked elsewhere. **Case history is
patterns, not prescriptions** (§22), and a coach that presents it as methodology
teaches the Belt to copy rather than reason.

**Signature:**
```
rag_lookup_case_history(query: str, top_k: int = 10,
                        exclude_current_case: bool = True) -> list[Document]
```

| | |
|---|---|
| Index | `improve_case_index` (§23.3) |
| Filter | `status eq 'completed'`; `belt_level` optional, OFF by default |
| Ordering | `created_at desc` |
| Vector field | `embedding` — **the live name**; renaming to `content_vector` is ratified and not yet applied (§23.3) |

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `phase_executor` (S-F04), by model choice |
| **Input** | `query`, `top_k`, `exclude_current_case`; a raw `SearchClient` rather than the shared vectorstore, because this index uses `content_text` / `embedding` |
| **Process** | Multi-query + RRF against completed cases |
| **Output** | `list[Document]` from other cases |
| **Customer** | The coach, which must present the result as precedent rather than as methodology |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | called | use the vector field name this index actually has, locally, rather than a shared constant | §23.3, §24 |
| B2 | called without an explicit `belt_level` | leave that filter OFF — a Green Belt often benefits from a Black Belt case | §24 |
| B3 | results reach the coach | be weighted below methodology and below this project's own approved fields | §22 |
| B4 | the search fails | raise `KnowledgeSearchError`, never return `[]` | §27 |

**`AI-ACT-REVIEW: uncertain.`** It surfaces other Belts' project data to this
Belt. There is no tenancy filter today — multi-tenant filtering is Appendix B
item 1, and §31 requires the docstring to carry that warning for future
engineers. Art. 10 relevance is real; classification deferred.

### 59.8 S-F17 · `reciprocal_rank_fusion`

**Architecture:** §25 · **File:** `knowledge/fusion.py` · **Procedure:** step 5.2
*Rebuild test: met.*

**Purpose:** Fuses the ranked result lists of several query variants into one
ordering. It operationalises **cross-variant consistency** — a document ranked
well by several different phrasings is more likely relevant than one ranked well
by a single phrasing — which native single-query ranking cannot do, because it
does not know the other variants exist.

**Definition:**
```python
def reciprocal_rank_fusion(ranked_lists, k: int = 60):
    scores, docs = {}, {}
    for ranked in ranked_lists:
        for rank, doc in enumerate(ranked):
            doc_id = doc.metadata["id"]
            scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (k + rank)
            docs[doc_id] = doc
    return sorted(
        [(docs[i], s) for i, s in scores.items()],
        key=lambda pair: pair[1],
        reverse=True,
    )
```

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | All three `rag_lookup_*` tools (S-F14, S-F15, S-F16), internally |
| **Input** | `ranked_lists` — one ranked list per query variant; `k=60` |
| **Process** | Sums `1/(k + rank)` per document across lists, then sorts descending |
| **Output** | `list[tuple[Document, float]]`, highest fused score first |
| **Customer** | The calling `rag_lookup_*` tool, which returns the top slice to the model |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | fusing | use `k=60` | §25 |
| B2 | a document appears in several variant lists | accumulate its score across all of them | §25 |
| B3 | fusion is needed | use this function; `MultiQueryRetriever` and `EnsembleRetriever` are BANNED | §25 |

**Invariants:**
- Variant generation and fusion happen **inside** the tool. The model sees a
  clean `rag_lookup_*(query, ...)` interface and never manages either.
- Roughly fifteen lines, no LangChain class, no third-party dependency, stable
  across framework versions. That is a deliberate property, not an accident.

### 59.9 S-F18 · The retriever layer — `search_knowledge`, `search_cases`, `search_evidence`

**Architecture:** §27 · **File:** `knowledge/retriever.py` · **Procedure:** step 5.1
*Rebuild test: not met — semantics are fully specified, the interface is not.*

**Purpose:** The functions the three `rag_lookup_*` tools call. **The tool layer
was renamed to `rag_lookup_*`; this retriever layer keeps its names** and its
failure semantics.

**What is fully specified — the failure contract:**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the search runs and matches nothing | return `[]` | §27 |
| B2 | the search fails | raise `KnowledgeSearchError`; a bare `except Exception` returning `[]` is BANNED | §27 |
| B3 | catching | catch `retriever.RETRIEVAL_EXCEPTIONS` and classify via `_fail()` | §27 |
| B4 | classifying a 4xx | classify it `permanent` / `do_not_retry` — it is our malformed query, and retrying fails identically | §27, §48 |
| B5 | executing a search | materialise results inside the `try`; the search call is lazy and the HTTP request fires on iteration, so a `try` that returns the iterator catches nothing | §27 |
| B6 | reporting failure to the coach | say explicitly that this is a retrieval failure and not an absence of guidance | §27 |

**The coach-facing failure message, as ratified:**

> "Methodology search is unavailable right now (`{error_code}`). This is a
> retrieval failure, not an absence of guidance — do not tell the team the
> methodology has nothing on this. Answer from your own DMAIC knowledge, say
> the reference lookup failed, and avoid citing sources you could not
> retrieve."

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The three `rag_lookup_*` tools (S-F14, S-F15, S-F16) |
| **Input** | Undetermined (G-26) — the query and index-specific parameters |
| **Process** | Executes the Azure AI Search call plus the Azure OpenAI query embedding, both inside one `try` |
| **Output** | `list[Document]`, or raises `KnowledgeSearchError` |
| **Customer** | The calling `rag_lookup_*` tool, which fuses and returns |

> **SPEC-GAP (G-26):** the three signatures, the membership of
> `RETRIEVAL_EXCEPTIONS` — stated only as "spans two services" — and the
> `_fail()` contract, including what it returns and how it maps an exception to
> `AgentImproveError`'s `severity` and `retry_recommendation`, are all
> undefined — to be designed with founder.

---

## 60. Spec — tools

*Supersedes: none — new. Definitions relocated from §29.2, §30.*
**Status: RATIFIED as a structure; most entries carry gaps.**

**The tool inventory and the per-phase binding table stay in §30.** They are a
binding inventory rather than a signature set, and §30 is where an amendment
against the 16-tool cap is evaluated. The entries below specify the tools
themselves.

**Three categories exist, and only two are bound:** the universal seven
(§29.2), the computation tools (§30), and the four cross-agent tools of §29.4,
which are **present and deliberately bound to nothing.** The cross-agent four
get no spec entry in this pass: they are unreachable by construction, and §29.4
already states the three rules that must be satisfied before any may be bound.

### 60.1 S-F19 · `propose_template`

**Architecture:** §29.2 · **File:** `knowledge/tools.py` · **Procedure:** step 5.2
*Rebuild test: not met.*

**Purpose:** Produces a fill-in template for the team — a scaffold the Belt
completes, consistent with show-before-asking (§43.2).

**Signature:**
```
propose_template(template_type: str, fill_data: dict) -> str
```

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `phase_executor` (S-F04), by model choice |
| **Input** | `template_type`; `fill_data` |
| **Process** | Undetermined (G-29) |
| **Output** | A template string for the Belt |
| **Customer** | The coach, which presents it; the Belt, who completes it |

**No AI-ACT flag.** It emits a scaffold, asserts nothing about the Belt, and
captures no value.

> **SPEC-GAP (G-29):** the template types are given as "problem_statement,
> sipoc, data_collection_plan, fishbone, etc." — an open list, which is not a
> specification — and there is no `fill_data` schema for any type. Its
> relationship to the per-field worked examples each SKILL.md carries (§32,
> §43.2) is also unstated: whether a template and a worked example are the same
> artifact from two directions determines whether this tool duplicates skill
> content — to be designed with founder.

### 60.2 S-F20 · `propose_diagram`

**Architecture:** §29.2 · **File:** `knowledge/tools.py` · **Procedure:** step 5.2
*Rebuild test: not met.*

**Purpose:** Produces structured diagram JSON for the frontend to render. **The
model describes what to draw; the frontend owns how it looks** — a model
emitting SVG produces markup that drifts from the design system and cannot be
restyled.

**Signature:**
```
propose_diagram(diagram_type: str, data: dict) -> dict
```

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `phase_executor` (S-F04), by model choice — notably at step 6 of the seven-step computation pattern, "visualise" (§43.1) |
| **Input** | `diagram_type`; `data` |
| **Process** | Undetermined (G-30) |
| **Output** | Structured diagram JSON, never SVG |
| **Customer** | The frontend's SVG template library |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | called | return structured JSON; it SHALL NOT return SVG or any other markup | §29.2 |

**No AI-ACT flag.** Presentation only.

> **SPEC-GAP (G-30):** §29.2 states the diagram types and schemas live in
> `core/diagrams.py`. **That file does not exist** (Appendix E), and no diagram
> type or schema is stated anywhere in this document. The frontend contract this
> tool writes against is therefore entirely undefined — to be designed with
> founder.

### 60.3 S-F21 · `check_gate_status`

**Architecture:** §29.2, §19.1, §35 · **File:** `knowledge/tools.py` · **Procedure:** step 7.1
*Rebuild test: not met.*

**Purpose:** Reports current-phase gate readiness — which Tier 1 fields are
populated and which are missing. **Derived at call time, never read from a
stored list**, which is what keeps it from disagreeing with
`DMAICGateValidator`.

**Signature:**
```
check_gate_status() -> dict
```

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `phase_executor` (S-F04), by model choice — stage F of the A→F session flow (§43.3); `BeforeModelStateInjection` (S-C11), which computes missing fields the same way |
| **Input** | The current phase and `PhaseState.artifacts` — **by an unstated route, since the signature takes no arguments (G-31)** |
| **Process** | Compares populated `artifacts` keys against that phase's Tier 1 list (§35) |
| **Output** | A dict of readiness — shape undetermined (G-31) |
| **Customer** | The coach, for the live gate document preview (§43.4); the UI's Tier 1 / Tier 2 progress bars (§50) |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | called | derive readiness from `artifacts` at call time; it SHALL NOT read a stored list of missing fields or blockers | §5, §19.1 |
| B2 | called | derive it the same way Layer 2b does, so the prompt and `DMAICGateValidator` cannot disagree | §19.1 |
| B3 | its output reaches the UI | drive Tier 1 and Tier 2 progress separately, never one blended percentage | §50 |

**No AI-ACT flag.** Pure derivation over already-captured values; it asserts
nothing and captures nothing.

> **SPEC-GAP (G-31):** the return shape is unspecified, and **the signature
> takes no arguments while the function must know the current phase and read
> `artifacts`** — so how it reaches either is undefined. As a bound `@tool` it
> also needs an `args_schema` (§31), which a zero-argument signature does not
> obviously admit — to be designed with founder.

### 60.4 S-F22 · `request_human_approval`

**Architecture:** §29.2, §38 · **File:** `knowledge/tools.py` · **Procedure:** step 7.5
*Rebuild test: not met.*

**Purpose:** Lets the coach escalate a decision it judges beyond its remit,
outside the standard gate sequence. One of the two entry points to the
escalation subgraph.

**Signature:**
```
request_human_approval(reason: str) -> str
```

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `phase_executor` (S-F04), by model choice |
| **Input** | `reason` |
| **Process** | Triggers an interrupt awaiting a human decision (G-32) |
| **Output** | Undetermined (G-32) |
| **Customer** | The escalation subgraph (S-F08); the Belt |

**`AI-ACT-REVIEW: uncertain.`** It is an oversight escape hatch (Art. 14),
which argues for a flag; it is also a thin trigger with no judgment of its own,
which argues against. Deferred with S-F08.

> **SPEC-GAP (G-32):** how a *tool* raises a graph-level `interrupt()` from
> inside the executor's tool loop is unspecified — and it matters, because §19.9
> bans `HumanInTheLoopMiddleware` precisely on the ground that edit and reject
> are unreliable in subgraph contexts. What the tool returns to the model after
> the interrupt resumes, and how this path differs from the
> `gate_attempts >= 3` path into the same subgraph, are also undefined — to be
> designed with founder.

### 60.5 S-F23 · `load_skill(name)`

**Architecture:** §19.2, §32 · **File:** `middleware/skills.py` · **Procedure:** step 6.3
*Rebuild test: not met.*

**Purpose:** Level 2 of progressive disclosure — the coach calls it to load the
full phase instructions when it enters a phase.

> **SPEC-GAP (G-33):** this is described in both §19.2 and §32 as "a registered
> `load_skill(name)` tool," and it appears in **neither the universal seven
> (§29.2) nor any phase's tool count (§30).** If it is bound to the executor it
> is an eighth universal tool, and every per-phase total in §30 moves — Measure
> from 15 to 16, against a hard cap of 16, which would then also constrain
> §29.4's cross-agent binding question. If it is not bound to the executor,
> then how the coach calls it is unstated. Its signature and return shape are
> undefined either way — to be designed with founder.

### 60.6 S-F24 · The 20 computation tools

**Architecture:** §30, §7, §43.1 · **File:** `knowledge/computation.py` · **Procedure:** step 5.3
*Rebuild test: not met — the inventory is complete, the interfaces are absent.*

**Purpose:** Deterministic Six Sigma statistics. **All 20 are pure functions** —
no LLM call, unit-tested — and they are the one place synchronous code is
unambiguously correct (§14).

**The complete inventory, by phase:**

| Phase | Computation tools | Count |
|---|---|---|
| Define | `calculate_expected_savings` | 1 |
| Measure | `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean` | 8 |
| Analyse | `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression` | 5 |
| Improve | `calculate_doe_main_effects` | 1 |
| Control | `xbar_r_chart_limits`, `imr_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk` | 5 |

**1 + 8 + 5 + 1 + 5 = 20.**

#### Behaviors (EARS) — binding on all twenty

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | any of them is called | be a pure function — deterministic, no LLM call, no I/O | §30 |
| B2 | receiving a captured field | parse what it needs out of the string at the point of use, since every captured field is a `str` | §7 |
| B3 | unable to parse its input | return a clear reformatting request to the Belt rather than raising or guessing | §7 |
| B4 | one is defined | be a separate named tool; parameterised grouping behind a mode argument is BANNED | §30 |
| B5 | any of them is called by the coach | be called under the seven-step pattern — educate, explain why now, guide data prep, run, interpret, visualise, coach the next move | §43.1 |
| B6 | it produces a result | have that result written to `artifacts["computation_results"]` as a typed dict with string values, never to a typed per-phase field | §7 |
| B7 | the Belt has one measurement per period | make `imr_chart_limits` the correct choice; a Belt SHALL NOT be coached into inventing subgroups to fit a batch chart | §30 |

**No AI-ACT flag.** These are deterministic pure functions. Their *outputs*
reach the gate document, and the risk that carries is held by
`phase_executor`'s flag (`R-EXEC-01`, behaviors B4 and B5) and by
`gate_apply_node`'s (`R-GATEAPPLY-01`), where the interpretation and the commit
happen.

> **SPEC-GAP (G-25):** not one of the twenty has a signature, a parameter
> schema, or a return shape stated anywhere in this document. Three consequences
> follow, and each is its own design decision: (a) §31 requires every `@tool` to
> carry an `args_schema` from `knowledge/tool_args.py`, and none exists; (b) B3's
> "clear reformatting request to the Belt" has no defined shape — whether it is a
> raised error, a sentinel return, or a string the model reads changes how the
> coach handles it; (c) B6's `computation_results` entry shape is illustrated in
> §7 for `t_test` only. **The inventory above is complete and is not a gap; the
> interfaces are entirely absent** — to be designed with founder.

---

## 61. Spec — the coaching agent's middleware

*Supersedes: none — new. Definitions relocated from §19.*
**Status: RATIFIED as a structure; four of five custom middlewares carry a constructor gap.**

**The stack, its order and its ordering rules stay in §19**, which is their
canonical home and which §56 makes amendment-bearing. The entries below specify
the five custom classes. The three core middlewares — `SummarizationMiddleware`,
`ModelRetryMiddleware`, `ToolRetryMiddleware` — are used as shipped and get no
spec entry: their interfaces belong to LangChain, and §19.3–§19.5 already record
the exact configuration and the verified parameter names.

**Middleware gets class entries only.** Each hook's behaviour is expressed as
EARS behaviours on the class; a separate function entry per hook would duplicate
the SIPOC cells.

### 61.1 S-C10 · `ContradictionDetectionMiddleware`

**Architecture:** §19.6, §37 · **File:** `middleware/contradiction.py` · **Procedure:** step 6.5
*Rebuild test: blocked on G-07 and G-15.*

**Purpose:** Position 6, `after_agent`. **It reads a flag; it does not detect
anything itself.** Detection is semantic and performed by the coach, in the
response call that already runs every turn (DECISIONS §R1). This middleware's
whole job is turning that flag into an interrupt.

**Definition:**
```python
class ContradictionDetectionMiddleware(AgentMiddleware):
    def after_agent(self, state, runtime):
        flag = state["structured_response"].contradiction_flag
        if flag:
            raise HITLInterrupt(**flag)
```

**No Store read. No LLM call. No field-name matching. No tolerance threshold**,
and none may be added.

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the agent finishes a turn | read `contradiction_flag` off the structured response | §19.6 |
| B2 | the flag is set | raise `HITLInterrupt` with the flag's five keys, suppressing the coach's response | §37 |
| B3 | the flag is `None` | do nothing and let positions 7 and 8 run | §19.6 |
| B4 | at any time | make no Store read, no LLM call, and no field-name comparison | §19.6 |
| B5 | at any time | apply no tolerance threshold — any material change to a gate-approved value is a mini-gate, never a silent overwrite | §37 |

#### ⚠ AI-ACT — high-risk surface

**This middleware suppresses coaching output and is the entry point to the
re-approval cascade** — the mechanism that makes an already-approved assessment
provisional. It is the only component that can retroactively unsettle a
committed record.

| Obligation | How this middleware addresses it |
|---|---|
| Art. 14 (human oversight) | It does not resolve the contradiction. It stops and hands the Belt two explicit options — update, or keep — with the approved value, its approving phase and their own words in front of them (§37, §50) |
| Art. 15 (accuracy/robustness) | No tolerance threshold: silent drift across weeks is the failure a coaching system exists to prevent |
| Art. 12 (record-keeping) | The interrupt payload records the contradicted field, both values and the approving phase |
| Art. 13 (transparency) | **Partially. Detection is best-effort semantic and can miss**, which is an honest downgrade from what the previous mechanism claimed. §50's always-referenceable all-gate-fields tab is the documented human backstop, not a convenience |

*Feeds DORA register row **R-CONTRA-01**.*

**Why middleware rather than logic inside the executor node:** the check polices
the executor's own output, so it does not belong to the thing it polices. As
middleware it is a named, LangSmith-visible step, and the executor node stays
responsible only for coaching.

> **SPEC-GAP (G-07):** `state["structured_response"]` — whether middleware
> observes `PhaseState` or `create_agent`'s internal agent state — is unstated,
> so this entry cannot declare where it reads from.

> **SPEC-GAP (G-15):** `HITLInterrupt` is raised here and is defined nowhere. It
> is not confirmed to be a LangGraph symbol, and §19.9 bans
> `HumanInTheLoopMiddleware`, so it is not that package's exception either.
> Whether raising an exception from `after_agent` produces a resumable
> graph-level interrupt at all is unverified — to be designed with founder.

### 61.2 S-C11 · `BeforeModelStateInjection`

**Architecture:** §19.1 · **File:** `middleware/state_injection.py` · **Procedure:** step 6.3
*Rebuild test: blocked on G-24.*

**Purpose:** Position 1, `before_agent`. Prepends structured project state at the
**top** of the prompt, ahead of the conversation, so the response is anchored to
the project's established state rather than drifting toward the Belt's framing.

**What it injects:** this phase's `artifacts`; prior phases' gate documents from
the Store; the current phase's requirements; and the missing fields reported by
`check_gate_status()` (S-F21).

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | an agent turn begins | fire on `before_agent`, once per turn — **never `before_model`**, which fires before every model call within a turn and re-injects the same facts repeatedly | §19.1 |
| B2 | injecting | place project facts at the top of the prompt; appending them in `messages[]` order is a violation | §19.1 |
| B3 | computing missing fields | derive them at injection time the same way the gate does; it SHALL NOT read a stored list | §19.1 |
| B4 | the stack is declared | be first, so project facts reach the prompt before skills loading and summarisation shape it | §19 |
| B5 | injecting prior-phase values | inject them from the Store, which is what makes the coach's semantic contradiction check possible at all | §37 |

**No AI-ACT flag.** It moves already-committed values into the prompt and
asserts nothing of its own. Its correctness is nonetheless load-bearing for
`R-EXEC-01` behavior B3 and for `R-CONTRA-01`: **if this middleware does not
inject prior committed values, the coach has nothing to compare against and
contradiction detection silently detects nothing** — the same failure shape as
the mechanism it replaced.

> **SPEC-GAP (G-24):** §19 writes this class as `BeforeModelStateInjection(...)`.
> Its constructor arguments, the exact composition of the injected block, and
> its token budget are unstated — to be designed with founder.

> **Naming finding.** The class is named `BeforeModelStateInjection` and its hook
> is `before_agent`. The name therefore says the thing the architecture
> explicitly corrects three separate times (§8.5-equivalent, §19, §19.1, and the
> `CLAUDE.md` no-go list). Recorded in §66 as a finding; renaming is not in this
> pass's scope.

### 61.3 S-C12 · `DMAICSkillsMiddleware`

**Architecture:** §19.2, §32 · **File:** `middleware/skills.py` · **Procedure:** step 6.3
*Rebuild test: blocked on G-24 and G-33.*

**Purpose:** Position 2, `before_agent`, plus a registered tool. Implements
three-level progressive disclosure over the five phase SKILL.md files, so all
five descriptions cost under 2K tokens at startup and full instructions load
only for the phase in flight.

| Level | When | What loads |
|---|---|---|
| 1 | Startup | Skill descriptions only — under 2K tokens for all five combined |
| 2 | On demand | Full phase instructions, when the coach enters that phase |
| 3 | On demand | Reference files, when explicitly needed |

**Storage backend: `FilesystemBackend`** — git-versioned alongside the code, so
a skill change is reviewable in the same PR as the code depending on it.
`ContextHubBackend` is deferred to the multi-deployment stage.

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the system starts | load descriptions only, under 2K tokens for all five combined | §32 |
| B2 | the coach calls `load_skill(name)` | load that phase's full instructions | §19.2 |
| B3 | a skill is loaded | have its `allowed-tools` match that phase's tool subset in §30 exactly | §32 |
| B4 | it is constructed | use `FilesystemBackend` | §32 |

**No AI-ACT flag.** It loads instruction content and asserts nothing. Note that
**the contradiction-check instruction lives in the SKILL.md content it loads**
(§32), so its correctness is load-bearing for `R-CONTRA-01` in the same way
S-C11's is.

> **SPEC-GAP (G-24):** constructor arguments are unstated — `DMAICSkillsMiddleware(...)`.

> **SPEC-GAP (G-33):** whether `load_skill` is bound as an eighth universal tool
> is undetermined — see S-F23.

### 61.4 S-C13 · `CoherenceMiddleware`

**Architecture:** §19.7, §34 · **File:** `middleware/coherence.py` · **Procedure:** step 6.5
*Rebuild test: blocked on G-23-adjacent schema gap G-09 and on G-24.*

**Purpose:** Position 7, `after_agent`, immediately before the grader.
**Validation Layer 2a.** One LLM call at `coherence` role, temperature 0.1: is
this a real, conclusive statement? Is it parroting the Belt's own words back? Is
it on-topic for this phase?

**Layer 2a fires every coaching turn**, which is why it is middleware rather
than part of the `validation_stack` node — that node runs once, at the gate.
Layers 2b–2d live there; 2a lives here. One conceptual stack, two mechanisms.

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the agent finishes a turn | run one coherence check at `coherence` role, temperature 0.1 | §19.7 |
| B2 | the check fails | retry silently, at most twice — the Belt never sees a failed coherence response | §19.7, §34.2 |
| B3 | retries are exhausted | degrade the turn and **skip `DMAICGraderMiddleware`** — grading a response already known to be incoherent spends a model call for a meaningless score | §19 |
| B4 | its retry budget is counted | count it separately from `ModelRetryMiddleware`'s two and the validation stack's three; the three caps SHALL NOT be merged | §19 |
| B5 | a rubric is being maintained | contain no coherence criterion — coherence moved out of `COACHING_QUALITY_RUBRIC` when this middleware was added, and any such entry is stale | §36 |

**`AI-ACT-REVIEW: uncertain.`** Its silent retry is the one narrowly-scoped
exception to the transparency principle (§34.2), justified because showing a
Belt that the AI produced gibberish adds no value. That is a deliberate,
reasoned opacity — but it *is* opacity, and whether Art. 13 requires it to be
surfaced is a judgment this pass does not make.

> **SPEC-GAP (G-09):** its structured output `CoherenceResult` is named in §21
> and defined nowhere — see S-C23.

> **SPEC-GAP (G-24):** constructor arguments are unstated — `CoherenceMiddleware(...)`.

### 61.5 S-C14 · `DMAICGraderMiddleware`

**Architecture:** §19.8, §36 · **File:** `middleware/grader.py` · **Procedure:** step 6.5
*Rebuild test: blocked on G-12 and G-24.*

**Purpose:** Position 8, `after_agent`. Grades the **coach's process** against
`COACHING_QUALITY_RUBRIC` — one rubric, shared across all five phases — every
coaching turn. **It is not Layer 2d**, which grades the gate *document* against
`PHASE_RUBRIC` once per phase. Confusing the two is a violation.

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the agent finishes a turn | grade against `COACHING_QUALITY_RUBRIC`, never against a phase rubric | §36 |
| B2 | grading | run at `grader` role, temperature 0.1, so the same input gets the same verdict across runs | §21 |
| B3 | grading | return a verdict per criterion, never an overall score | §35 |
| B4 | feeding back to the coach | make the feedback per criterion and specific — never "try again" | §36 |
| B5 | `max_iterations=3` is reached | pass the output through **with a warning flag visible to the Belt** | §19.8 |
| B6 | each grading iteration completes | write it to `step_log` via the `on_evaluation` callback | §11 |
| B7 | at any time | keep iteration count, accumulated evaluations and attempt tracking **private to the middleware**; none SHALL reach `PhaseState` or `SupervisorState` | §19.8 |
| B8 | the Belt is present | not show them the grader loop; it runs at step 2 of the gate, before the interrupt | §33 |
| B9 | the coach calls a computation tool without educating on the concept first | fail that criterion — returning a p-value with no concept and no interpretation is a rubric failure, not a style preference | §43.1 |

**`AI-ACT-REVIEW: uncertain.`** It grades the *coach*, not the Belt, which
argues against a flag. But it can suppress or alter what the Belt receives, and
its `max_iterations_reached` warning is Belt-visible — so it shapes the
coaching record under Art. 13 and Art. 15. Deferred rather than guessed.

> **SPEC-GAP (G-12):** its structured output `CoachingGraderVerdict` is named in
> §21 and defined nowhere — see S-C22.

> **SPEC-GAP (G-24):** constructor arguments are unstated —
> `DMAICGraderMiddleware(...)`, including how `max_iterations` and
> `on_evaluation` are passed.

### 61.6 S-C15 · `HITLInterrupt`

**Architecture:** §19.6, §37 · **File:** `core/errors.py` (presumed) · **Procedure:** step 6.5

**Purpose:** The exception `ContradictionDetectionMiddleware` raises to convert
a contradiction flag into a Belt-facing interrupt carrying the five-key payload.

> **SPEC-GAP (G-15):** it is raised in §19.6 as `HITLInterrupt(**flag)` and
> defined nowhere. It is not confirmed to be a LangGraph symbol; it is not from
> `HumanInTheLoopMiddleware`, which §19.9 bans. Whether an exception raised from
> `after_agent` yields a resumable graph-level interrupt — as opposed to
> propagating out of the node and hitting `error_handler` (§45) — is unverified,
> and the answer determines whether the contradiction path works at all — to be
> designed with founder.

---

## 62. Spec — validation and gates

*Supersedes: none — new. Definitions relocated from §34, §35, §40.1.*
**Status: RATIFIED as a structure; six of eleven entries are gap stubs.**

**The four-layer table, the tier tables and the nine-step gate stay where they
are** — §33, §34 and §35 are their canonical homes and none of them is a class
or a signature. The entries below specify the schemas and the callables.

**The `validation_stack` node itself is S-F05, in §58**, with the five phase
subgraph nodes it belongs to.

### 62.1 S-C20 · `CriterionVerdict`

**Architecture:** §35 · **File:** `validation/schemas.py` · **Procedure:** step 7.4
*Rebuild test: reconstructable from this entry alone.*

**Purpose:** One grader verdict about one criterion. **Per criterion, never an
overall score** — a score cannot tell a Belt which of eight things to fix, and
a blended number would let a Tier 2 shortfall drag a passing gate below a
threshold.

**Definition:**
```python
class CriterionVerdict(BaseModel):
    criterion: str
    tier:      int                                     # 1 or 2
    status:    Literal["pass", "warning", "fail"]
    feedback:  str                                     # specific, per criterion
```

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `criterion` | `str` | The rubric criterion this verdict is about | none | Layer 2d (S-F26); `DMAICGraderMiddleware` (S-C14) | the coach on retry; the gate review screen |
| `tier` | `int` | 1 or 2, per §35. Determines whether `fail` is even permitted | none | the grader | gate pass/fail logic |
| `status` | `Literal["pass","warning","fail"]` | Three statuses, not two. **Only a Tier 1 criterion may produce `fail`** | none | the grader | gate pass/fail logic; the UI |
| `feedback` | `str` | Specific and actionable. "Your previous answer did not address timeline or risk mitigation," never "try again" | none | the grader | the coach on retry; the Belt |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | a Tier 2 criterion is graded | produce at worst `warning`; `fail` SHALL be unreachable for Tier 2 | §35 |
| B2 | any verdict carries `fail` | block the gate; a gate MAY pass with warnings and MAY NEVER pass with failures | §35 |
| B3 | a Belt proceeds past a Tier 2 `warning` | have that recorded in `acknowledged_gaps`, never silently dropped | §35 |
| B4 | `feedback` is written | be specific to the criterion | §36 |

**Invariants:**
- The tier is what keeps Layer 2b and Layer 2d from contradicting each other.
  2b blocks only on Tier 1; 2d can `fail` only on Tier 1. There is no longer a
  criterion the grader can fail that the gate never asked for.
- **A change to any field's tier requires a §56 amendment.**

### 62.2 S-C21 · `GraderVerdict`

**Architecture:** §21, §35 · **File:** `validation/schemas.py` · **Procedure:** step 7.2

**Purpose:** Layer 2d's structured output — the gate document's grading, as a
collection of per-criterion verdicts.

**What is stated:** it carries a `list[CriterionVerdict]` (§35), it is produced
by a builder-style structured-output call at `grader` role and temperature 0.1
(§21), and it is belt-level aware — it reads `belt_level` from the case record
and suppresses Black-Belt-only recommendations for a Green Belt (§35).

> **SPEC-GAP (G-11):** beyond "carries a `list[CriterionVerdict]`" the schema is
> undefined. Whether it also carries an overall gate decision, the phase name,
> the attempt number, or the acknowledged-gap list is unstated — and the
> acknowledged-gap question is the same one G-08 raises from the other side — to
> be designed with founder.

### 62.3 S-C22 · `CoachingGraderVerdict`

**Architecture:** §21, §36 · **File:** `validation/schemas.py` · **Procedure:** step 6.5

**Purpose:** `DMAICGraderMiddleware`'s structured output — the coaching-process
grading, every turn, against `COACHING_QUALITY_RUBRIC`.

> **SPEC-GAP (G-12):** named in §21's mapping table, defined nowhere. Whether it
> reuses `CriterionVerdict` — the two graders share the "per criterion, never
> overall" rule (§36) but grade different subjects against different rubrics —
> or needs its own per-criterion type, is undecided, and the answer determines
> whether `tier` is meaningful for coaching criteria at all — to be designed
> with founder.

### 62.4 S-C23 · `CoherenceResult`

**Architecture:** §21, §19.7, §34 · **File:** `validation/schemas.py` or `validation/coherence.py` · **Procedure:** step 6.5

**Purpose:** Layer 2a's structured output — whether the coach's response is a
real, conclusive, on-topic statement that is not parroting the Belt.

> **SPEC-GAP (G-09):** named in §21's mapping table, defined nowhere. The three
> questions it answers are stated in §19.7; whether it returns one verdict or
> three, and what drives the retry decision of S-C13 B2, is unstated — to be
> designed with founder.

### 62.5 S-C24 · `ConstraintCheckResult` / `ConstraintVerdict`

**Architecture:** §21, §34 · **File:** `validation/schemas.py` · **Procedure:** step 7.2

**Purpose:** Layer 2c's structured output — whether a decision addresses budget,
timeline, risk and measurement.

> **SPEC-GAP (G-10):** named in §21's mapping table as `ConstraintCheckResult`
> and defined nowhere. **There is also a naming split:** `CLAUDE.md` §2 lists
> **both** `ConstraintVerdict` and `ConstraintCheckResult` in
> `validation/schemas.py`, and this document names only the second. Whether
> those are two types — a per-constraint verdict inside a result envelope,
> mirroring `CriterionVerdict` inside `GraderVerdict` — or one type under two
> names, is unresolved — to be designed with founder.

### 62.6 S-C25 · `PolicyAdvisoryResult`

**Architecture:** §21, §33 · **File:** `validation/schemas.py` · **Procedure:** step 7.3

**Purpose:** The policy advisory's structured output at gate step 6 — a second
opinion on the Belt's own edits, **non-blocking by design.**

> **SPEC-GAP (G-13):** named in §21's mapping table, defined nowhere. What it
> reports, and how a non-blocking result is surfaced to the Belt without
> reading as a rejection of their correction, are both undefined — and the
> second is the design question, since §33 rests the whole asymmetry on the
> advisory not overriding the Belt's judgment — to be designed with founder.

### 62.7 S-C26 · `DMAICGateValidator`

**Architecture:** §34, §35, §54 · **File:** `validation/gate_validator.py` · **Procedure:** step 7.1
*Rebuild test: not met.*

**Purpose:** Layer 2b — deterministic Tier 1 field-presence checking. **The one
permitted exception to "no classes outside §54's files"**: a namespace of
`@staticmethod` deterministic checks, holding no state.

**What is stated:**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | check presence of that phase's Tier 1 fields, deterministically, with no LLM call | §34 |
| B2 | invoked | check Tier 1 only; Tier 2 fields SHALL NOT be checked here | §35 |
| B3 | invoked | run first in the stack, because it is free and there is no reason to spend a grader call on a document missing a Tier 1 field | §34 |
| B4 | it and `check_gate_status()` both compute missing fields | produce the same answer, derived the same way, so the prompt and the gate cannot disagree | §19.1 |
| B5 | it holds anything | hold no state | §54 |

**The Tier 1 lists it checks** are §35's, per phase: Define 6, Measure 7,
Analyse 4, Improve 4, Control 3.

**`AI-ACT-REVIEW: uncertain.`** It participates in the gate decision, which
argues for a flag; it is deterministic and holds no judgment, which makes it a
mitigation under Art. 15 rather than a risk surface. Deferred rather than
guessed.

> **SPEC-GAP (G-23):** the static method names, their signatures and their
> return shapes are stated nowhere. Whether it returns a boolean, a list of
> missing field names, or a structured result that Layer 2d then consumes is
> undefined — and B4 makes that shape shared with `check_gate_status()` (G-31),
> so the two must be designed together — to be designed with founder.

---

### 62.8 S-F25 · Layer 2c — the constraint check

**Architecture:** §34 · **File:** `validation/constraints.py` · **Procedure:** step 7.2
*Rebuild test: blocked on G-10.*

**Purpose:** Asks whether a decision addresses budget, timeline, risk and
measurement. **An LLM call and not a format check**, deliberately: a keyword
check rejects a decision that addresses cost without using the word "budget."

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The `validation_stack` node (S-F05), after Layer 2b passes; also mid-conversation at key decision moments (§34.1) |
| **Input** | The decision text; the phase's constraint set — `DEFINE_CONSTRAINTS`, `ANALYSE_CONSTRAINTS`, `IMPROVE_CONSTRAINTS`, `CONTROL_CONSTRAINTS` (§22). **Measure has none — it is covered by its rubric** |
| **Process** | One plain model call at `constraint` role, temperature 0.1, producing `ConstraintCheckResult` (S-C24) |
| **Output** | Per-constraint verdicts; a `step_log` entry |
| **Customer** | The `validation_stack` node, which proceeds to Layer 2d or fails the attempt; the coach, which teaches toward a better formulation (Level 2, uncapped) |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | run as an LLM call at temperature 0.1; it SHALL NOT be downgraded to a regex or a keyword check | §34 |
| B2 | a constraint is conditional on another field's value | evaluate it conditionally — the risk-mitigation check fires only when `risk_level == "low"`, because a low-risk project should say how it *stays* low-risk | §34 |
| B3 | it fails on a Belt's proposal mid-conversation | be handled as Level 2 coached improvement, which has **no retry cap** — capping it would mean the coach eventually accepts a weak root cause | §34.2 |
| B4 | it runs | write a `step_log` entry recording layer, attempt, status and reason | §11 |

**`AI-ACT-REVIEW: uncertain.`** It judges the quality of the Belt's own stated
decision, which is closer to assessing the person than any other validation
layer. Whether that makes it a distinct high-risk surface or part of
`R-VALSTACK-01` is deferred.

> **SPEC-GAP (G-10):** its output schema is undefined — see S-C24.

### 62.9 S-F26 · Layer 2d — the gate grader

**Architecture:** §34, §35, §36 · **File:** `validation/` · **Procedure:** step 7.2
*Rebuild test: blocked on G-11 and G-40.*

**Purpose:** Grades the **gate document** against that phase's `PHASE_RUBRIC`,
once, at the gate boundary. It catches document-product failures a per-turn
check cannot see: four Analyse fields can each look sound in isolation while the
root cause discusses "error rate" and the baseline it references is "cycle
time." **Cross-field and cross-phase consistency is only visible once the
document is complete.**

**It is NOT `DMAICGraderMiddleware`** (S-C14), which grades the coach's process
against `COACHING_QUALITY_RUBRIC` every turn.

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The `validation_stack` node (S-F05), after Layer 2c passes — last, because it is the most expensive |
| **Input** | The complete `artifacts` field set; that phase's `PHASE_RUBRIC` (§22, §36); `belt_level` from the case record; prior phases' gate documents from the Store, for the three deterministic linkage checks |
| **Process** | One plain model call at `grader` role, temperature 0.1, producing `GraderVerdict` (S-C21) — **plus deterministic lookups for the criteria that do not need judgment** |
| **Output** | A verdict per criterion, each carrying its tier; `step_log` entries |
| **Customer** | The `validation_stack` node, which passes to `gate_review` or fails the attempt with accumulated feedback |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | grade against `PHASE_RUBRIC`, never against `COACHING_QUALITY_RUBRIC` | §36 |
| B2 | grading `causal_hypothesis`, `solution_linked_to_root_cause` or `post_improvement_metric` | verify the link **by lookup, not judgment** — read the referenced phase's gate document from the Store and check the named field carries the named value | §36, §42 |
| B3 | grading a criterion that depends on a computation | scan `artifacts["computation_results"]` for the relevant `tool` entry rather than asking the model | §36 |
| B4 | grading a structured dict field | check **every** sub-field is populated — a `process_map_sipoc` with four of six keys filled is the partial-map failure the field exists to catch | §41 |
| B5 | `belt_level` is Green Belt | suppress DOE as a recommendation; when it is Black Belt, flag DOE as a Tier 2 recommendation | §35 |
| B6 | grading | never retrieve; the rubric already encodes the methodology standards, and retrieval adds latency at the moment the Belt is waiting | §26 |
| B7 | grading the measurement thread | verify that `process_map_sipoc["process_kpis"]`, `detailed_process_map["baseline_kpis"]` and `post_improvement_metric` name the same measurement points and carry **different values** | §39 |

**Covered by the AI-ACT flag on `validation_stack` (S-F05) and DORA row
`R-VALSTACK-01`.** This is the component that produces the assessment; it is
flagged there rather than separately, because the node is what acts on the
verdict.

> **SPEC-GAP (G-11):** its output schema `GraderVerdict` is undefined — see
> S-C21.

> **SPEC-GAP (G-40):** the five `PHASE_RUBRIC` constants have coverage lists
> (§36) and no text. This function cannot be built without them — see §64.

### 62.10 S-F27 · The policy advisory

**Architecture:** §33 step 6, §22, §9.4-equivalent · **File:** logic inside `gate_apply` · **Procedure:** step 7.3
*Rebuild test: not met.*

**Purpose:** Gate step 6. Validates the **Belt's edits** against required-field
policy, cross-phase consistency and previously approved values. **Non-blocking,
and that is the core of the design:** the grader blocks at step 2 because it
checks the AI's own output; the advisory does not block at step 6 because the
Belt is the domain expert. A system that blocked the Belt's own corrections
would be asserting that its judgment outranks theirs on their own project.

**It is not a node.** It is logic inside `gate_apply_node` (S-F07), and
`policy_advisory` is a BANNED node name (§13).

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `gate_apply_node` (S-F07), after applying Belt edits and before assembling the document |
| **Input** | `PhaseState.belt_edits`; `PhaseState.artifacts`; prior phases' gate documents from the Store |
| **Process** | One plain model call producing `PolicyAdvisoryResult` (S-C25) |
| **Output** | An advisory result — presentation undetermined (G-13) |
| **Customer** | The Belt, as a second opinion before they confirm |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | it produces a finding | never block; it is a second opinion before the decision, not a veto after it | §33 |
| B2 | it runs | run after the Belt's edits, when the coach is no longer in the loop | §13 |
| B3 | it reviews extracted values | be one of the three required content-level defences against hallucinated values, alongside prompt guards and cross-checking against the raw conversation | §22 |

**`AI-ACT-REVIEW: uncertain.`** It reviews a human's corrections and reports on
them, which is an oversight-support mechanism (Art. 14) rather than an
assessment. But it is the last check before commit and §22 names it as one of
three anti-hallucination defences, which is Art. 15 territory. Deferred.

> **SPEC-GAP (G-13):** its output schema, and how a non-blocking advisory is
> surfaced without reading as a rejection of the Belt's correction, are both
> undefined — see S-C25.

### 62.11 S-F28 · Gate document assembly

**Architecture:** §40.1 · **File:** `phases/{phase}/nodes.py`, inside `gate_apply` · **Procedure:** step 3.4
*Rebuild test: met for Define; not met for the other four.*

**Purpose:** Constructs the `{Phase}Output` from already-captured values. **No
LLM call** — Pydantic validation over `artifacts`.

**Definition — Define, the one worked example:**
```python
gate_document = DefineOutput(
    problem_statement=artifacts["problem_statement"],      # Tier 1 — direct
    project_scope=artifacts["project_scope"],
    goal_statement=artifacts["goal_statement"],
    voc_summary=artifacts["voc_summary"],
    process_map_sipoc=artifacts["process_map_sipoc"],
    issues_and_barriers=artifacts["issues_and_barriers"],
    business_case=artifacts.get("business_case", ""),      # Tier 2 — .get()
    team=artifacts.get("team", ""),
    baseline_metric=artifacts.get("baseline_metric", ""),
    target_metric=artifacts.get("target_metric", ""),
    secondary_metrics=artifacts.get("secondary_metrics", ""),
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=acknowledged_gaps,
    citations=state["citations"],
    uploads=state["uploads"],
)
```

**The access pattern encodes the tier, and the difference is deliberate:**

| Tier | Access | Why |
|---|---|---|
| Tier 1 | `artifacts["field"]` | **A `KeyError` here is correct** — Layer 2b should have blocked the gate, so reaching assembly without the field is a bug that must surface loudly |
| Tier 2 | `artifacts.get("field", "")` | An empty value **records that the Belt proceeded without it** |
| Cross-phase dicts | `artifacts.get("field", {})` | Same, with the right empty type |

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `gate_apply_node` (S-F07), after the policy advisory |
| **Input** | `artifacts`; `acknowledged_gaps` (see G-08); `PhaseState.citations`; `PhaseState.uploads` |
| **Process** | Pydantic construction of the phase's `{Phase}Output` |
| **Output** | The gate document `dict`, written to the Store and to `PhaseState.final` |
| **Customer** | `gate_apply_node` (S-F07), which performs both writes |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | assembling | make no LLM call | §21, §40.1 |
| B2 | assembling | **reference every field in the schema** — a field that assembly never sets is a field that silently never reaches the Store | §40.1 |
| B3 | assembling the four gate-metadata fields | source them from `artifacts["computation_results"]`, the acknowledged-gap source, `PhaseState.citations` and `PhaseState.uploads` respectively | §40 |

> **SPEC-GAP (G-28):** §40.1 shows assembly for `DefineOutput` only. Measure,
> Analyse, Improve and Control are unwritten — 55 field assignments in total,
> each of which must select the correct tier access pattern, and B2 makes an
> omission silent — to be designed with founder.

> **SPEC-GAP (G-08):** `acknowledged_gaps` is sourced from
> `validation_stack.get_acknowledged_gaps()`, which cannot exist as written —
> see S-F05.

---

## 63. Spec — the DMAIC gate documents

*Supersedes: none — new. Definitions relocated from §40, §41, §7.*
**Status: RATIFIED. This subsystem's entries are complete — no gaps.**

**Part VIII is Agent Improve's domain Part**, and these five schemas are the
most Improve-specific artifacts in the document. **§40 remains the canonical
home for the field-count tables, the gate-metadata sourcing table and the
two-fields-on-all-five rule**; the schemas themselves are here.

**The typing law stays in §7** and binds on every field below: every captured
field is a `str`, except the three cross-phase reference dicts (S-C32) and the
three structured dicts (S-C33).

### 63.1 S-C27 · `DefineOutput`

**Architecture:** §40 · **File:** `phases/define/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Define's gate document. 15 fields — 6 Tier 1, 5 Tier 2, 4 gate
metadata.

```python
class DefineOutput(BaseModel):
    """Gate document for the Define phase."""
    # Tier 1 — gate-required
    problem_statement:    str      # measurable problem, baseline and target
    project_scope:        str      # explicit inclusions and exclusions
    goal_statement:       str      # SMART
    voc_summary:          str      # voice of customer
    process_map_sipoc:    dict     # SIPOC + KPIs, 6 sub-fields (§41)
    issues_and_barriers:  str      # Belt-stated blockers
    # Tier 2 — rubric-recommended
    business_case:        str      # quantified business impact (COPQ)
    team:                 str      # Belt, sponsor, 2+ members with roles
    baseline_metric:      str      # current measured state
    target_metric:        str      # target value
    secondary_metrics:    str      # what could get worse
    # Gate metadata
    computation_results:  list[dict] = []
    acknowledged_gaps:    list[str]  = []
    citations:            list[dict] = []
    uploads:              list[dict] = []
```

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the gate is evaluated | block on all six Tier 1 fields | §35 |
| B2 | `process_map_sipoc` is graded | require all six sub-fields, `process_kpis` among them | §41 |
| B3 | `process_kpis` is set | carry WHAT is measured — the first link of the three-phase measurement thread | §39 |

### 63.2 S-C28 · `MeasureOutput`

**Architecture:** §40 · **File:** `phases/measure/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Measure's gate document. 14 fields — 7 Tier 1, 3 Tier 2, 4 gate
metadata. The largest Tier 1 set of the five.

```python
class MeasureOutput(BaseModel):
    """Gate document for the Measure phase."""
    # Tier 1
    baseline_mean:                str    # value with units, as the Belt stated it
    data_collection_plan:         str    # sample size, frequency, responsible person
    xy_matrix_summary:            str    # evidence that prioritisation happened
    vital_few_xs:                 str    # the ranked result Analyse consumes
    detailed_process_map:         dict   # expanded map, 6 sub-fields (§41)
    stability_assessment:         str    # checked BEFORE capability (§41)
    issues_and_barriers:          str
    # Tier 2
    baseline_sigma:               str    # calculated sigma level
    measurement_system_validated: str    # GR&R or equivalent evidence
    secondary_metrics:            str
    # Gate metadata
    computation_results:  list[dict] = []
    acknowledged_gaps:    list[str]  = []
    citations:            list[dict] = []
    uploads:              list[dict] = []
```

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | capability is being assessed | require `stability_assessment` first — a baseline Cpk computed across an unstable process averages two different processes and looks authoritative while being wrong | §41 |
| B2 | `detailed_process_map` is graded | require all six sub-fields, `baseline_kpis` among them | §41 |
| B3 | `baseline_kpis` is set | carry the BEFORE values of the measurement thread | §39 |
| B4 | `vital_few_xs` is set | be the ranked result Analyse consumes; Analyse cannot start without it, which is why `xy_matrix_summary` is Tier 1 for all Belts | §35 |

### 63.3 S-C29 · `AnalyseOutput`

**Architecture:** §40 · **File:** `phases/analyse/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Analyse's gate document. 13 fields — 4 Tier 1, 5 Tier 2, 4 gate
metadata.

```python
class AnalyseOutput(BaseModel):
    """Gate document for the Analyse phase."""
    # Tier 1
    root_cause_statement:          str   # specific and actionable
    root_cause_validation:         str   # statistical or observational evidence
    practical_significance:        str   # how much of the problem it explains
    issues_and_barriers:           str
    # Tier 2
    causal_hypothesis:             dict  # cross-phase ref → Measure baseline (§7)
    ruled_out_causes:              str   # alternatives rejected, with rationale
    statistical_problem_statement: str   # all Belts, in Analyse — not Define
    process_owner_buyin:           str   # owner accepts the root causes
    secondary_metrics:             str
    # Gate metadata
    computation_results:  list[dict] = []
    acknowledged_gaps:    list[str]  = []
    citations:            list[dict] = []
    uploads:              list[dict] = []
```

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | `causal_hypothesis` is graded | verify its reference keys against Measure's gate document by lookup, not judgment | §36, §42 |
| B2 | `statistical_problem_statement` is coached | require it of all Belts, in Analyse and not Define — it is no longer belt-gated | §35 |
| B3 | the phase is graded | treat `practical_significance` as Tier 1 — the eBook's second gate, "how much of the problem does this explain" | §35 |

### 63.4 S-C30 · `ImproveOutput`

**Architecture:** §40 · **File:** `phases/improve/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Improve's gate document. 13 fields — 4 Tier 1, 5 Tier 2, 4 gate
metadata.

```python
class ImproveOutput(BaseModel):
    """Gate document for the Improve phase."""
    # Tier 1
    selected_solution:             str   # criteria-based selection documented
    pilot_result:                  str   # practical AND statistical significance
    experiment_justification:      str   # DOE / simplified / none — and why (§41)
    issues_and_barriers:           str
    # Tier 2
    solution_linked_to_root_cause: dict  # cross-phase ref → Analyse root cause (§7)
    implementation_plan:           str   # timeline, owner, resources
    explanatory_power:             str   # R² / variance explained
    process_owner_buyin:           str   # owner accepts the solution
    secondary_metrics:             str
    # Gate metadata
    computation_results:  list[dict] = []
    acknowledged_gaps:    list[str]  = []
    citations:            list[dict] = []
    uploads:              list[dict] = []
```

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | `experiment_justification` is graded | accept any of three answers — DOE conducted, simplified one-factor experiment, or no experiment needed because the solution follows from root cause analysis. **All three are valid**; the failure it catches is drifting past the question, not skipping DOE | §41 |
| B2 | `belt_level` is Green Belt | not recommend DOE | §35 |
| B3 | `solution_linked_to_root_cause` is graded | verify its reference keys against Analyse's gate document by lookup | §36, §42 |

### 63.5 S-C31 · `ControlOutput`

**Architecture:** §40 · **File:** `phases/control/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Control's gate document. 15 fields — 3 Tier 1, 8 Tier 2, 4 gate
metadata. The smallest Tier 1 set and the largest Tier 2 set.

```python
class ControlOutput(BaseModel):
    """Gate document for the Control phase."""
    # Tier 1
    control_plan:              dict   # FIVE sub-plans — §41
    post_improvement_metric:   dict   # cross-phase ref → Measure baseline (§7)
    issues_and_barriers:       str
    # Tier 2
    improvement_delta:         str    # change from baseline
    financial_impact_verified: str    # quantified saving
    sustainability_check:      str    # process for maintaining the gains
    handover_documented:       str    # named process owner accepting
    lessons_learned:           str    # feeds the case index
    transferability:           str    # yokoten — feeds rag_lookup_case_history
    project_signoff:           str    # Champion + Belt + Finance
    secondary_metrics:         str
    # Gate metadata
    computation_results:  list[dict] = []
    acknowledged_gaps:    list[str]  = []
    citations:            list[dict] = []
    uploads:              list[dict] = []
```

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | `control_plan` is graded | require all five sub-plans populated. A single string cannot show that four were done and one was skipped, and **a Training Plan written but never delivered is the most common real Control failure** | §41 |
| B2 | `post_improvement_metric` is graded | verify by lookup against Measure's `baseline_mean`. **It is the only cross-phase reference field that is Tier 1** — a Control phase that cannot link its result back to the baseline has not demonstrated improvement at all | §42 |
| B3 | Control's gate passes | populate `SupervisorState.final_output` through Control's output mapper | §5 |
| B4 | `lessons_learned` and `transferability` are set | feed the case index and cross-case retrieval respectively | §23.3, §24 |

### 63.6 S-C32 · The three cross-phase reference dicts

**Architecture:** §7, §42 · **File:** `phases/{phase}/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** The one exception to the every-captured-field-is-a-string law.
Each carries the Belt's content plus three reference keys, **so the grader can
verify the link deterministically** — it reads the referenced phase's gate
document from the Store and checks the named field carries the named value.
Without the reference keys, "does this solution address the validated root
cause?" is an opinion; with them it is a lookup.

**Shape:**
```python
causal_hypothesis = {
    "hypothesis":       "Inadequate onboarding causes error spike in first 60 days",
    "references_phase": "measure",
    "references_field": "baseline_mean",
    "references_value": "12.3%",
}
```

**The three:**

| Field | Phase | Tier | References |
|---|---|---|---|
| `causal_hypothesis` | Analyse | 2 | Measure's `baseline_mean` |
| `solution_linked_to_root_cause` | Improve | 2 | Analyse's `root_cause_statement` |
| `post_improvement_metric` | Control | **1** | Measure's `baseline_mean` |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | one of the three is graded | resolve `references_phase` / `references_field` / `references_value` against the Store by lookup, never by model judgment | §36, §42 |
| B2 | one of the three is captured | carry it through `CoachingResponse.fields_captured` with `value` as a `dict` — which is why `value` is typed `Any` | §20 |
| B3 | values inside the dict are written | write them as strings | §7 |
| B4 | assembly reaches one of the three | access it as `artifacts.get("field", {})` — the correct empty type | §40.1 |

**Invariant:** only `post_improvement_metric` is Tier 1, and the asymmetry is
deliberate — an Analyse phase without an explicit hypothesis link is weaker but
not void, whereas a Control phase that cannot link back to the baseline has
demonstrated nothing.

### 63.7 S-C33 · The three structured dict fields

**Architecture:** §41, §39 · **File:** `phases/{phase}/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Three Tier 1 fields are structured dicts, **distinct from the three
cross-phase reference dicts.** They are dicts rather than prose because a
coaching conversation produces text no downstream planner can read and no grader
can check.

| Field | Phase | Sub-fields |
|---|---|---|
| `process_map_sipoc` | Define | `suppliers`, `inputs`, `process_steps`, `outputs`, `customers`, **`process_kpis`** |
| `detailed_process_map` | Measure | `steps`, `cycle_times`, `resources`, `value_vs_waste`, `measurement_points`, **`baseline_kpis`** |
| `control_plan` | Control | `documentation`, `monitoring`, `response`, `training`, `aligning_systems` |

**`control_plan`, fully specified:**
```python
control_plan: dict = {
    "documentation":    str,   # updated process maps, SOPs, training manuals
    "monitoring":       str,   # what charts, what frequency, what limits, who checks
    "response":         str,   # what happens when monitoring signals a problem
    "training":         str,   # who needs training, in what format, verified how
    "aligning_systems": str,   # HR, IT, budget changes needed to sustain
}
```

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | any of the three is graded | check **every** sub-field is populated; a partial map is the failure these fields exist to catch | §41 |
| B2 | any of the three is typed | be `dict`, never `str` | §41 |
| B3 | the measurement thread is verified | read `process_kpis` (WHAT), `baseline_kpis` (BEFORE) and `post_improvement_metric` (AFTER), and confirm the same measurement points carry different values | §39 |

**Invariant — FMEA has no field in any schema, and none may be added.** Not
`fmea_summary`, not `updated_fmea`, not an FMEA sub-key anywhere. If a Black
Belt performs one it lives in `uploads` as an attached document; the schema does
not track it, the grader does not ask for it, and no gate blocks on it (§41).

---

## 64. Spec — reliability

*Supersedes: none — new. Definitions relocated from §45, §46, §48.*
**Status: RATIFIED as a structure. Everything in this subsystem is BLOCKED on the LangGraph upgrade (§53).**

**The failure pipeline, the fallback chain, the breaker thresholds and the
`request_drain()` warning stay in §44, §45 and §46.** The entries below specify
the callables and the two classes.

### 64.1 S-C34 · `AgentImproveError`

**Architecture:** §48 · **File:** `core/errors.py` · **Procedure:** step 8.1
*Rebuild test: met.*

**Purpose:** The single schema for every external service failure. **Two of its
fields are read by machinery rather than humans**, which is why this is a schema
and not a logging convention: a free-text error message cannot drive a circuit
breaker's retry decision or a fallback chain's backoff choice.

**Definition:**
```python
class AgentImproveError(BaseModel):
    error_code:           str        # "TIMEOUT", "RATE_LIMIT", "AUTH_FAILURE", …
    severity:             str        # "transient" | "permanent"
    retry_recommendation: str        # "retry_after_backoff" | "do_not_retry" | …
    affected_identifier:  str
    message:              str
    timestamp:            datetime
```

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `error_code` | `str` | A stable machine token for the failure class | none | any external-call boundary | logs; the coach-facing failure message (§27) |
| `severity` | `str` | `"transient"` or `"permanent"`. **Read by the circuit breaker** to distinguish "retry" from "stop trying" | none | the classifier, e.g. `_fail()` (S-F18) | `CircuitBreaker` (S-C35) |
| `retry_recommendation` | `str` | **Read by the fallback chain** to choose its backoff strategy | none | the classifier | the fallback chain (§46) |
| `affected_identifier` | `str` | What the failure was about — a `case_id`, an index name, a deployment name | none | the raising site | logs; support escalation |
| `message` | `str` | Human-readable detail. Not read by machinery | none | the raising site | logs; humans |
| `timestamp` | `datetime` | When it happened | none | the raising site | logs |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | any external service call fails | be represented by this schema, not by a bare exception or a log line | §48 |
| B2 | a 4xx is returned from retrieval | be classified `permanent` / `do_not_retry` — it is our malformed query, and retrying fails identically | §27, §48 |
| B3 | an HTTP 400 token-limit error occurs | **not** be treated as a fallback case; it is a context-management failure, and a smaller model has a smaller window | §46 |
| B4 | any attempt is made | be logged to `step_log` as a dict | §11 |

### 64.2 S-C35 · `CircuitBreaker`

**Architecture:** §46, §54 · **File:** `core/reliability.py` · **Procedure:** step 8.3
*Rebuild test: not met.*

**Purpose:** Three-state breaker, two instances. **Two-state (CLOSED/OPEN)
breakers are not permitted** — this is a long-running service and must recover
without a restart.

| Instance | Wraps | On OPEN |
|---|---|---|
| LLM | Azure OpenAI calls | The coaching turn cannot happen — fall to Level 2, then degraded |
| Search | Azure AI Search calls | Coaching **continues** without RAG grounding — quality degradation, not availability failure |

**The asymmetry is the point.** A search outage should degrade grounding, not
stop the session.

**Thresholds, as ratified:** 3 failures in 30 seconds trips OPEN; 60-second
reset; **one probe request in HALF-OPEN** before resuming.

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | 3 failures occur within 30 seconds | trip OPEN | §46 |
| B2 | 60 seconds elapse in OPEN | move to HALF-OPEN and allow exactly one probe request | §46 |
| B3 | it classifies a failure | read `AgentImproveError.severity` rather than inspecting an exception type | §48 |
| B4 | the Search breaker is OPEN | let coaching continue ungrounded; it SHALL NOT stop the session | §46 |
| B5 | it is implemented | have three states; a two-state breaker is a violation | §46 |

> **SPEC-GAP (G-22):** the class interface is stated nowhere — how a call is
> wrapped, whether it is a decorator, a context manager or an explicit
> `call()`, how the two instances are constructed and held, and how state is
> shared across concurrent turns on one process. The thresholds and the state
> machine above are complete; the interface is absent — to be designed with
> founder.

---

### 64.3 S-F29 · `phase_error_recovery`

**Architecture:** §45 · **File:** `phases/{phase}/nodes.py` or `core/reliability.py` · **Procedure:** step 8.2
*Rebuild test: not met — blocked on G-03, G-06, G-32-adjacent G-35.*

**Purpose:** The node-level error handler required on every node with external
writes. It **undoes the external write** and routes to a degraded response.

**Definition:**
```python
def phase_error_recovery(error: NodeError, state: PhaseState) -> Command:
    delete_or_flag_stale_in_case_index(state["case_id"], state["phase"])
    return Command(
        update={"extraction_error": str(error), "extraction_incomplete": True},
        goto="degraded_coaching_response",
    )
```

**Registered as:**
```python
builder.add_node(
    "phase_executor",
    phase_executor_fn,
    timeout=TimeoutPolicy(run_timeout=45),
    error_handler=phase_error_recovery,
)
```

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The LangGraph runtime, when a node attempt raises **and the retry policy is exhausted** — retries run before the handler |
| **Input** | `NodeError`; `PhaseState` — including `case_id` and `phase`, **neither of which is a declared field (G-03)** |
| **Process** | Runs the compensating action against `improve_case_index`, then routes to a degraded response |
| **Output** | A `Command` carrying `extraction_error` and `extraction_incomplete` (**neither declared — G-06**) and `goto="degraded_coaching_response"` (**not one of §13's five nodes — G-35**) |
| **Customer** | The `degraded_coaching_response` node (S-F33) |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | any node with external writes is registered | carry an `error_handler=`; a node that writes to Azure Blob, `improve_case_index` or `improve_evidence_index` without one is a violation | §45 |
| B2 | it runs | undo the external write, not merely record the failure | §45 |
| B3 | the re-approval cascade fires | run for the affected phase, **or state and index disagree silently** | §37, §45 |
| B4 | time-travel debugging resumes from an earlier checkpoint | be what makes that correct — resuming rolls back state, not external writes | §45 |
| B5 | it is set as a graph-wide default | apply to regular nodes only; a handler SHALL never catch itself, and `cache_policy` is likewise excluded | §45 |
| B6 | the policy is applied to many nodes | prefer `set_node_defaults` over repeating the arguments on every node | §45 |

**Hand-written Saga orchestrators and compensating-action frameworks are
BANNED.** LangGraph provides the mechanism; `error_handler=` is the native
replacement for the pre-1.2 workaround.

> **SPEC-GAP (G-03):** it reads `state["case_id"]` and `state["phase"]`, and
> `PhaseState` declares neither — see S-C02.

> **SPEC-GAP (G-06):** it writes `extraction_error` and
> `extraction_incomplete`, and `PhaseState` declares neither — see S-C02.

### 64.4 S-F30 · `degraded_mode_response`

**Architecture:** §46 · **File:** `core/reliability.py` · **Procedure:** step 8.3
*Rebuild test: met in shape; the field counts it reads depend on G-31.*

**Purpose:** Level 4 of the fallback chain — the level that always succeeds.
**Degraded mode is still a coaching interaction, not an error page.** The Belt
knows what happened, knows their work is safe, and knows how to continue.

**Definition:**
```python
def degraded_mode_response(state: PhaseState) -> str:
    return (
        f"I'm experiencing a temporary connection issue. "
        f"Based on what we've captured so far in the {phase} phase "
        f"({n_captured} of {n_total} fields complete), "
        f"I'd suggest we pause here and continue once the system recovers. "
        f"Your progress is saved and nothing has been lost."
    )
```

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The fallback chain, at Level 4, after the model tiers and the cache have all failed; the LLM circuit breaker (S-C35) on OPEN |
| **Input** | `PhaseState` — the phase name and the captured/total field counts |
| **Process** | Composes a coaching-voiced message from actual state |
| **Output** | A string for the Belt |
| **Customer** | The Belt, via the API surface (S-F34) |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | it fires | use actual state — the phase and real field counts — never a generic error message | §46 |
| B2 | the chain reaches Level 4 | always succeed; Level 4 is a response, not an error path | §46 |
| B3 | it fires | tell the Belt their progress is saved | §46 |

**`AI-ACT-REVIEW: uncertain.`** It is Belt-facing content produced under
failure, which is Art. 13 territory — it must not misrepresent system state.
Whether that makes it a high-risk surface or ordinary UX is deferred.

**Note.** The function signature takes `state`, and the body references `phase`,
`n_captured` and `n_total` as bare names. Whether they are derived inside the
function or passed in is not shown; and `n_captured` / `n_total` are the same
counts `check_gate_status()` produces (G-31), so the two should be designed
together. Recorded as a finding in §66.

### 64.5 S-F31 · `synthesise_partial`

**Architecture:** §26 · **File:** `phases/analyse/` or `knowledge/` · **Procedure:** step 5.2

**Purpose:** The graceful off-ramp when the hop budget is nearly exhausted —
the agent composes an answer from what it has rather than dying. It is the
property that makes `RemainingSteps` preferable to `recursion_limit`, both of
which otherwise terminate the graph with `GraphRecursionError`.

**Called at two sites**, both in §26: the `agent_node` guard illustration and
`analyse_executor_node`'s entry guard (S-F09 B1).

> **SPEC-GAP (G-35):** defined nowhere. Its signature, what it returns — §26
> wraps it in `{"messages": [...]}`, implying a message object rather than a
> string — and whether it makes a model call or assembles deterministically are
> all unstated. Whether it also sets `hop_results` and `synthesis_output`
> matters, because S-F09 B4 requires both to reach state — to be designed with
> founder.

### 64.6 S-F32 · `delete_or_flag_stale_in_case_index`

**Architecture:** §45, §37 · **File:** `storage/` or `knowledge/` · **Procedure:** step 8.2

**Purpose:** The compensating action. Cleans up values already published to
`improve_case_index` when a node fails after writing externally, and when the
re-approval cascade makes a phase provisional.

**Why it is correctness-critical, twice over:** a cascade that marks phases
provisional but leaves published values in place is **worse than no cascade** —
state and index then disagree silently, and the system reports a phase as
needing review while continuing to serve its old conclusions. And time-travel
debugging is only correct for nodes that have a handler, because resuming rolls
back state and not external writes.

> **SPEC-GAP (G-35):** defined nowhere. Its signature is visible from the one
> call site — `(case_id, phase)` — and **the name itself contains an unresolved
> choice**: delete, or flag stale? The two produce different index states and
> different `rag_lookup_case_history` results, since that tool filters
> `status eq 'completed'` and a flagged-stale record's status is undefined. What
> it does to the five `phase_summary_{phase}` fields is also unstated — to be
> designed with founder.

### 64.7 S-F33 · `degraded_coaching_response` node

**Architecture:** §45 · **File:** `phases/{phase}/nodes.py` · **Procedure:** step 8.2

**Purpose:** The `goto=` target of `phase_error_recovery` (S-F29). Presents the
degraded response to the Belt after a node has failed and its external write has
been undone.

> **SPEC-GAP (G-35):** it is named only as a `goto=` string in §45's handler and
> is defined nowhere. **It is also not one of the five nodes §13 permits in a
> phase subgraph, and §13 requires a §56 amendment to add a sixth** — so either
> it is a sixth node needing an amendment, or the handler routes somewhere that
> does not exist. Its relationship to `degraded_mode_response` (S-F30), which
> returns a string rather than being a node, is likewise unstated — to be
> designed with founder.

---

## 65. Spec — API, UI and evidence

*Supersedes: none — new. Definitions relocated from §49.*
**Status: RATIFIED as a structure; every entry in this subsystem carries a gap.**

**The endpoint table, the UI language rules and the citation format stay in §49
and §50.** They are an inventory and a set of rules, not signatures.

### 65.1 S-C36 · `CitationRecord` and `CitationBundle`

**Architecture:** §50 · **File:** `core/citations.py` · **Procedure:** [tbd]

**Purpose:** The citation types. **Citation transparency is a product
requirement, not decoration** — "this came from page 47 of the BB eBook" is what
makes a citation checkable.

**What is stated:** the citation format is `agent_origin`, `index_name`,
`document_id`, `relevance_summary` (§50); retrieval citations must additionally
surface `source_file` and `page_number` (§23, §50); and `PhaseState.citations`
entries carry `source`, `page`, `content_summary` and `turn` (§6).

> **SPEC-GAP (G-16):** neither class is defined. `CitationRecord` appears in
> this document only inside Appendix D.2's ban on **duplicating** it, and in
> `CLAUDE.md` §2's permitted-class list; `CitationBundle` appears only in the
> latter. **Three different citation shapes are stated in three places** — §50's
> four fields, §6's four different fields, and §23's two more — and whether
> those are one type, a record plus a bundle, or three unreconciled shapes is
> undecided — to be designed with founder.

### 65.2 S-C37 · The API envelopes

**Architecture:** §49 · **File:** `gateway/schemas.py` · **Procedure:** step 10.1

**Purpose:** Pydantic v2 request and response envelopes for every endpoint.

**What is stated:** they are Pydantic v2 and they live in `gateway/schemas.py`
(§49, §54). A route may do nothing beyond invoking the graph plus **envelope
marshalling** — so the envelope is the entire permitted surface of the API
layer, which makes its absence load-bearing rather than cosmetic.

> **SPEC-GAP (G-18):** not one envelope is defined, for any of the seven
> endpoints. The gate interrupt payload (S-F06) and the `Command(resume=...)`
> approval payload cross this boundary and have no schema either, and the SSE
> event shape for `/ask/stream` is unstated — to be designed with founder.

---

### 65.3 S-F34 · The API surface

**Architecture:** §49 · **File:** `gateway/routes.py` · **Procedure:** steps 10.1, 4.2
*Rebuild test: not met — blocked on G-18, G-36 and G-02.*

**Purpose:** The only entry point. **The compiled graph is the only runtime
path**, and a route that does anything beyond invoking it plus envelope
marshalling is a violation — the rule the v1 codebase most conspicuously breaks.

**Endpoints:**

| Endpoint | Purpose |
|---|---|
| `POST /ask` | Non-streaming coaching turn — retained for clients that cannot use SSE |
| `POST /ask/stream` | **The standard path.** Server-Sent Events; the frontend renders tokens as they arrive |
| `POST /gate/submit` | Triggers the validation stack and the gate interrupt (§33.1) |
| `POST /gate/approve` | Resumes from the interrupt with approval |
| `POST /gate/reject` | Resumes from the interrupt with rejection — **behaviour undefined (G-02)** |
| `GET /cases`, `GET /cases/{id}` | Case records |
| `GET /registry` | Case registry |

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The frontend; the Belt |
| **Input** | Request envelopes (**undefined — G-18**); the authenticated session, from which `case_id` is derived |
| **Process** | Marshals the envelope, invokes the compiled graph, marshals the response. Nothing else |
| **Output** | Response envelopes; an SSE token stream on `/ask/stream`; the interrupt payload on `/gate/submit` |
| **Customer** | The supervisor graph (S-F01), which every endpoint invokes; the frontend |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | any endpoint is called | invoke the same compiled graph object; **manual node dispatch in a route is a violation** | §49 |
| B2 | any endpoint is defined | be `async def`; all graph invocations await the async form | §49 |
| B3 | a run is configured | derive `thread_id` / `case_id` **from the authenticated session, never from client input** — a client-supplied `thread_id` lets any caller resume any Belt's session | §47 |
| B4 | a client disconnects mid-run | **ABANDON, not COMPLETE.** A silently-completed gate approval the Belt never saw is unacceptable in a system whose premise is that the Belt approves what commits | §47 |
| B5 | the handler is written | use inline `await` streaming, or an explicit abandon policy cancelling the task in `finally`. **A bare background task with no disconnect handling has chosen COMPLETE by accident** | §47 |
| B6 | two tabs write one `case_id` | be guarded by the Azure Blob lease, until the PostgreSQL migration provides advisory locks | §47 |
| B7 | a reconciliation sweep runs for abandoned threads | **exclude interrupt-paused threads** — a thread paused at a gate looks identical to an abandoned one by inactivity alone, and a sweep that misses this cleans up Belts who are thinking about their gate review overnight | §47 |

> **SPEC-GAP (G-36):** **there is no upload endpoint in this table**, and
> §29.1 makes uploaded documents the only channel through which external data
> enters AgentLean — see S-F35.

> **SPEC-GAP (G-18):** no envelope is defined for any endpoint — see S-C37.

> **SPEC-GAP (G-02):** `POST /gate/reject` has no defined behaviour — see S-F13
> decision point 3.

### 65.4 S-F35 · The upload handler

**Architecture:** §6, §10, §23.2, §29.1 · **File:** unassigned · **Procedure:** [tbd]
*Rebuild test: not met.*

**Purpose:** Ingests a Belt's uploaded document into `improve_evidence_index`,
writes the file to Blob, and appends to `PhaseState.uploads`. **This is the only
path by which external, real-world data enters the platform** (§29.1), which
makes it architecturally more significant than its absence from the endpoint
table suggests.

**What is stated across the document:**

| Fact | Source |
|---|---|
| It is the writer of `PhaseState.uploads` | §6 field table |
| `uploads` entries carry `evidence_index_id`, `filename`, `phase`, `uploaded_at`, `summary` | §6 |
| Blob path `uploads/{case_id}/{file}`, owned by `ImproveBlobClient` | §10 |
| Case blob written on file upload — never mid-conversation | §10 |
| Index fields `phase` and `uploaded_at` are **server-set** — `phase` from `state["current_phase"]` at upload, `uploaded_at` from the server clock | §23.2 |
| Both are ratified and **not yet applied**; the live index has neither | §23.2 |
| A `vision` LLM role exists for multimodal upload analysis | §21 |
| Evidence cache entries invalidate on upload | §46 |
| Each SKILL.md carries upload-handling instructions | §32 |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | a file is uploaded | set `phase` from server state and `uploaded_at` from the server clock; a Belt-entered value for either makes it unreliable as a filter or sort key | §23.2 |
| B2 | a file is uploaded | append to `PhaseState.uploads` with `evidence_index_id`, so a reviewer reading the approved gate document can follow the trail back to the indexed chunk | §6 |
| B3 | a file is uploaded | invalidate the affected evidence cache entries | §46 |
| B4 | it writes to the index | write with explicit ids and with `fields=` declaring the real schema, or the metadata is silently demoted to an unfilterable JSON blob | §23.4 |
| B5 | a phase completes with no uploads | leave `uploads` empty and let that stand as a visible finding — the phase reached its conclusions from typed statements alone | §6 |

> **SPEC-GAP (G-36):** **no upload endpoint exists in §49's endpoint table**, no
> file owns this handler, and it appears in no procedure step. It is named only
> as a writer in §6's field table. Given §29.1, the entire external-data channel
> of the platform is currently specified as one cell in a field table — to be
> designed with founder.

### 65.5 S-F36 · The `improve_case_index` write path

**Architecture:** §23.3, §37, §45 · **File:** unassigned · **Procedure:** [tbd]
*Rebuild test: not met.*

**Purpose:** Publishes live case records — including the five
`phase_summary_{phase}` fields — into `improve_case_index`, which is the
cross-case memory `rag_lookup_case_history` reads.

**What is stated:**

| Fact | Source |
|---|---|
| The full index schema, 18 fields | §23.3 |
| `f"phase_summary_{phase}"` is correct for all five phases, with no mapping constant | §23.3 |
| A compensating action must clean up stale values in it (S-F32) | §37, §45 |
| The re-approval cascade depends on that cleanup, or state and index disagree silently | §37 |
| `rag_lookup_case_history` filters `status eq 'completed'` and orders by `created_at desc` | §24 |
| `lessons_learned` and `transferability` from `ControlOutput` feed it | §40 |
| Never write to Agent Resolve indexes — read-only, via tools | §23.5 |

**`AI-ACT-REVIEW: uncertain.`** It publishes one Belt's project record into a
corpus other Belts retrieve from. That is a data-governance surface (Art. 10),
and there is no tenancy filter today — multi-tenant filtering is Appendix B
item 1. Classification deferred rather than guessed.

> **SPEC-GAP (G-37):** **nothing writes this index.** §23.3 defines the schema,
> §37 and §45 require compensating cleanup of it, `rag_lookup_case_history`
> reads it — and no function, node, or procedure step is named as its writer.
> When a record is created, when the phase summaries are computed and by what,
> when `status` becomes `completed`, and how `days_in_phase` and `rag_status`
> are maintained are all unspecified — to be designed with founder.

---

## 66. The SPEC-GAP register

*Supersedes: none — new. Decision record: `agent-improve/docs/DECISIONS.md` §S1.*
**Status: OPEN — this is a working register, not a ratified statement.**

**Every gap marked inline in Part XII has a row here, and every row here has an
inline marker.** That bidirectional correspondence is checkable and is one of
the §55.1 governance rules.

**42 gaps identified. One is closed. 41 are open, and none was filled by the
conversion pass** — that was the pass's binding constraint. Filling them is the
work that follows, in the order the founder chooses.

### 66.1 Group A — founder ruling required

| # | Gap | Marked at |
|---|---|---|
| **G-01** | **Level 2 (subgraph-internal) `Command` routing.** §13 draws the branching, §15 states the rule, and no `Command(goto=…)` exists anywhere. Three decision points: planner exit; validation-stack exit and its ownership of the `gate_attempts` increment; gate exit including REJECT | S-F13, S-F02, S-F03, S-F05 |
| **G-02** | **What a Belt REJECT does.** `POST /gate/reject` is in §49's endpoint table and in §33.1's frontend sequence; its behaviour — re-coach, or apply-with-edits — is stated nowhere. A coaching-philosophy ruling | S-F06, S-F07, S-F13, S-F34 |

### 66.2 Group B — cross-check defects

**The same defect class as `route_after_phase` (DECISIONS §R2): specified code
reading state a schema does not declare.** Each fix is a design choice, and
adding a `PhaseState` field is a §56 amendment.

| # | Gap | Marked at |
|---|---|---|
| **G-03** | `PhaseState` declares no `case_id` and no phase identifier, yet `phase_error_recovery` reads `state["case_id"]` and `state["phase"]` (§45), `analyse_executor_node` reads `state["current_phase"]` (§26), and `gate_apply_node`'s Store write needs `case_id` (§33.2) | S-C02, S-F07, S-F09, S-F29 |
| **G-04** | `remaining_steps` is read off `PhaseState` twice (§26) and is not declared. `RemainingSteps` must be declared on the state schema to be populated; undeclared, the `.get(..., 10)` default returns 10 forever and **the five-hop cap never fires** | S-C02, S-F09 |
| **G-05** | `extracted_entity` is read off `PhaseState` (§26); undeclared, and no writer is named anywhere | S-C02, S-F09 |
| **G-06** | `extraction_error` and `extraction_incomplete` are written into `PhaseState` by `phase_error_recovery` (§45); neither is declared | S-C02, S-F29 |
| **G-07** | `state["structured_response"]` is read by `ContradictionDetectionMiddleware` (§19.6). Whether middleware observes `PhaseState` or `create_agent`'s internal agent state is unstated | S-F04, S-C10 |
| **G-08** | `validation_stack.get_acknowledged_gaps()` (§40) is attribute access on a node, and §14 requires nodes to be module-level async functions. Where acknowledged gaps are produced and how they reach assembly is unspecified | S-F05, S-F07, S-F28 |
| **G-42** | **NEW — surfaced by the Supplier/Customer cross-check.** **The boundary mappers have no execution site.** §9 defines them as "two plain functions per phase"; §13 states a phase subgraph contains **exactly five nodes**, none of which is a mapper, and forbids a sixth without a §56 amendment; §12 embeds each subgraph as a node of the parent. Whether a mapper runs inside the subgraph, inside the parent's node wrapper, or somewhere else is stated nowhere — and every phase boundary depends on it | S-F10, S-F11, S-F12 |

### 66.3 Group C — schemas named but never defined

| # | Gap | Marked at |
|---|---|---|
| **G-09** | `CoherenceResult` | S-C23, S-C13 |
| **G-10** | `ConstraintCheckResult`, plus the `ConstraintVerdict` / `ConstraintCheckResult` naming split between `CLAUDE.md` §2 and reference §21 | S-C24, S-F25 |
| **G-11** | `GraderVerdict` — only "carries a `list[CriterionVerdict]`" is stated | S-C21, S-F26 |
| **G-12** | `CoachingGraderVerdict` | S-C22, S-C14 |
| **G-13** | `PolicyAdvisoryResult`, and how a non-blocking advisory is surfaced without reading as a rejection of the Belt's correction | S-C25, S-F27 |
| **G-14** | `QueryVariants` | S-C19 |
| **G-15** | `HITLInterrupt` — and whether an exception raised from `after_agent` yields a resumable graph-level interrupt at all | S-C15, S-C10 |
| **G-16** | `CitationRecord` / `CitationBundle` — and the three different citation shapes stated in §50, §6 and §23 | S-C36 |
| **G-17** | `CaseDocument` · `PhaseRecord` · `RegistryEntry` · `PhaseSummaryRecord`, and whether `PhaseRecord` duplicates the gate document | S-C09 |
| **G-18** | All `gateway/schemas.py` envelopes, for all seven endpoints, plus the gate interrupt and resume payloads and the SSE event shape | S-C37, S-F06, S-F34 |
| **G-19** | Per-phase `PhaseState` variants — the transient fields are never enumerated, and whether they count against §6's ceiling is undecided | S-C03 |

### 66.4 Group D — described in prose, no interface

| # | Gap | Marked at |
|---|---|---|
| **G-20** | `AzureBlobCheckpointSaver` — the on-blob format is complete; the `BaseCheckpointSaver` method set is absent | S-C07 |
| **G-21** | `ImproveBlobClient` | S-C08 |
| **G-22** | `CircuitBreaker` — thresholds and state machine complete, interface absent | S-C35 |
| **G-23** | `DMAICGateValidator` — static method names, signatures and return shapes; must be designed with G-31 | S-C26 |
| **G-24** | Constructor arguments for all four remaining custom middlewares — `(...)` is literal in §19 in every case | S-C11, S-C12, S-C13, S-C14 |
| **G-25** | **The 20 computation tools** — no signature, no `args_schema`, no return shape for any of them; and no defined shape for §7's required "reformatting request" | S-F24 |
| **G-26** | Retriever-layer signatures, `RETRIEVAL_EXCEPTIONS` membership, and the `_fail()` contract | S-F18 |
| **G-27** | Boundary mappers for Measure, Analyse, Improve and Control — including what each `phase_context` contains | S-F12 |
| **G-28** | Gate assembly for Measure, Analyse, Improve and Control — 55 field assignments, each selecting a tier access pattern, and an omission is silent | S-F28, S-F07 |
| **G-29** | `propose_template` — an open "etc." type list and no `fill_data` schema | S-F19 |
| **G-30** | `propose_diagram` — types and schemas are said to live in `core/diagrams.py`, **which does not exist** | S-F20 |
| **G-31** | `check_gate_status()` — return shape unspecified, and a zero-argument signature that must nonetheless know the phase and read `artifacts` | S-F21 |
| **G-32** | `request_human_approval` — how a tool raises a graph-level interrupt from inside the executor's tool loop | S-F22 |
| **G-33** | `load_skill(name)` — in neither the universal seven nor any phase count; if bound, Measure goes to 16 against a cap of 16 | S-F23, S-F02, S-C12 |
| **G-34** | The escalation subgraph — no node list, no state schema, no exit contract | S-F08 |
| **G-35** | `synthesise_partial()`, `delete_or_flag_stale_in_case_index()` (delete **or** flag stale — the name carries the undecided choice), and the `degraded_coaching_response` node, which is not one of §13's permitted five | S-F31, S-F32, S-F33, S-F09, S-F29 |
| **G-36** | **No upload endpoint exists**, no file owns the upload handler, and §29.1 makes uploads the only channel through which external data enters the platform | S-F35, S-F34 |
| **G-37** | **Nothing writes `improve_case_index`** — the schema is defined, cleanup of it is required, and no writer is named | S-F36 |

### 66.5 Group E — content the build sequence defers

| # | Gap | Marked at |
|---|---|---|
| **G-38** | `field_index` has no ordering source — the per-phase field list it indexes into is stated nowhere, and §13's "advance to the next field" depends on it | S-C02, S-F03 |
| **G-39** | `turn_count`'s increment contract, load-bearing in §11's deterministic `step_log` key | S-C02 |
| **G-40** | Prompt constants — `{PHASE}_COACH_PROMPT`, `{PHASE}_PLANNER_PROMPT`, five `PHASE_RUBRIC`s and four `{PHASE}_CONSTRAINTS` sets are named with coverage lists and no text. Only `COACHING_QUALITY_RUBRIC` is written out | S-F26 |

### 66.6 Closed

| # | Gap | Resolution |
|---|---|---|
| **G-41** | The two calibrated samples' verbatim text was in no file in the repository — `SPEC_LAYER_GUIDE.md` §7 gave their skeletons and deferred the full text to the 2026-08-23 conversation | **CLOSED 2026-08-23.** The approved verbatim text was supplied at `agent-improve/docs/SPEC_SAMPLES.md` and transcribed into §57.2 and §57.3 |

### 66.7 Findings — recorded, not gaps

**A gap is something missing. A finding is something present and wrong, or
present and inconsistent.** These were surfaced by the conversion pass and the
Supplier/Customer cross-check, whose first run is recorded at §66.8. **None
was fixed by the pass**; each needs a
§56-routed decision of its own.

| # | Finding |
|---|---|
| **F-01** | **The drift registry cannot see this document.** `.claude/config/deprecated_patterns.yaml` excludes `agent-improve/*.md` and `agent-improve/**/*.md` from patterns 2–8. **This file moved to the monorepo root in v1.2 and the exclusion was never updated**, so the platform governance document is now guarded as if it were code — while the registry's own header names `AGENTIC_ARCHITECTURE_REFERENCE.md` among the documents that must be able to name a deprecated construct in order to prohibit it. **Fourth instance of the pattern §55 names:** a correct rule paired with a check that cannot see what it governs |
| **F-02** | **§33 step 9 still reads "Supervisor reads `gate_passed`, static edge advances."** v2.2.20 of `CLAUDE.md` deliberately tightened its equivalent step to "the parent's static edge advances," on the ground that "routes onward" was the last phrasing from which the deleted `route_after_phase` design could be re-derived. **The reference's own step 9 was not tightened with it**, so the two binding documents now differ on the sentence that DECISIONS §R2 exists to police |
| **F-03** | **The calibrated `phase_executor` sample cites "(§35)" for the four-layer validation stack, twice** — once in its Art. 15 row and once in its DORA row. §34 is the four-layer stack; §35 is the two-tier field rule. Transcribed verbatim and not corrected, because the sample is the approved standard |
| **F-04** | **The calibrated `phase_executor` sample's Supplier cell names only `phase_planner`.** `analyse_executor_node` (S-F09) produces `synthesis_output` that the coach call reads, which makes it a second supplier on multi-hop turns. Not corrected — verbatim |
| **F-05** | **Middleware is invisible to the Supplier/Customer cross-check.** Per the approved judgment call, the five custom middlewares are class entries without SIPOC tables — yet `phase_executor`'s Customer cell names `ContradictionDetectionMiddleware` as its first consumer. The cross-check cannot close on that edge. Either middleware needs SIPOC cells, or the rule needs to state that it ranges over nodes and functions only |
| **F-06** | **The 20 computation tools are likewise invisible**, for the same reason: S-F24 is one entry with behaviors and no SIPOC. They are named in `phase_executor`'s Input cell via `tools=` and nowhere else in the cross-check |
| **F-07** | **The cross-check rule does not model two structures it meets constantly.** *Request/response pairs*: the API surface both triggers the graph and consumes its output, so each is the other's Supplier and Customer, and a strict reading reports a mismatch. *Nesting*: Layers 2c and 2d, gate assembly, the policy advisory, RRF and the retriever layer are sub-components of their own callers, so their Supplier and Customer are the same entry. Both are correct designs that the rule as written flags. **Recommendation: state the rule as ranging over peer node-to-node edges, and exclude nested sub-components and return paths explicitly** — otherwise it produces noise that trains people to ignore it, which is the §55 failure mode |
| **F-08** | **The gate document is written to the same Store key twice** — by `gate_apply_node` (§33.2) and again by the phase's output mapper (§9). The write is idempotent by key so nothing breaks, but **neither section names which is authoritative**, and a future change to one will not obviously require a change to the other |
| **F-09** | **`BeforeModelStateInjection` is named after the hook it must not use.** Its hook is `before_agent`; §19, §19.1 and `CLAUDE.md`'s no-go list each correct the `before_model` reading separately. The class name reproduces the error every time it is read |
| **F-10** | **`degraded_mode_response` reads counts that `check_gate_status()` produces** (§46 body vs §29.2), and both are unspecified (G-31). They should be designed together, or the Belt sees two different completion counts |

### 66.8 The Supplier/Customer cross-check — first run, 2026-08-23

**Run mechanically over all 73 entries as the conversion landed.** 28 entries
carry a SIPOC table; 58 directed edges were checked in both directions;
**36 did not close.**

**Four are substantive, and three of those confirm a gap this document already
names.** The cross-check found them without being told to look:

| Edge | What it means |
|---|---|
| S-F05 names S-F03 as Supplier; **S-F03's Customers are S-F04 and S-F09 only** | **G-01, decision point 1, detected mechanically.** The validation stack says the planner triggers it and the planner does not say it routes there — because that routing does not exist |
| S-F10 and S-F12 name S-F03 as Customer; **S-F03's Suppliers do not include either** | **G-42, detected mechanically.** A mapper cannot be named as a supplier of the planner because it has no stated execution site |
| S-F11 names S-F12 as Customer; **S-F12's Suppliers are S-F01 and S-F07** | **F-08, with evidence.** Both `gate_apply_node` and the output mapper claim the Store write the next input mapper reads. Two writers, no stated owner |
| S-F09 names S-F04 as Customer; **the sample's Supplier cell names only `phase_planner`** | **F-04.** The multi-hop path feeds the coach call and is not accounted for. Not corrected — the sample is verbatim |

**The remaining 32 are structural, and they are the rule's problem rather than
the architecture's.** They fall into four classes, each already recorded above:

| Class | Count | Finding |
|---|---|---|
| The calibrated sample names its neighbours in prose (`phase_planner`) rather than by entry ID, so the parser cannot match them | 11 | F-04 |
| Nested sub-components — Layers 2c and 2d inside the validation stack, gate assembly and the policy advisory inside `gate_apply`, RRF and the retriever layer inside the `rag_lookup_*` tools | 12 | F-07 |
| Request/response and build-time/run-time pairs — the API surface both triggers the graph and consumes its output; the supervisor graph both builds subgraphs and runs them | 6 | F-07 |
| Edges pointing at class entries and gap stubs, which carry no SIPOC table | 3 | F-05, F-06 |

> **The conclusion is about the rule, not the result.** A check that reports 36
> failures of which 4 matter will be ignored by its third run. **§55.1 rule 3
> must be narrowed to peer node-to-node edges before it is automated** —
> excluding return paths, nested sub-components, build-time relations, and
> edges terminating at a class entry — or it becomes the fourth instance of the
> pattern §55 names: a check whose output nobody reads.

---

---

# Part XIII — Compliance and Risk

*The EU AI Act and DORA obligations this architecture is designed to satisfy,
and the register that aggregates them. **This Part is scaffolding placed
2026-08-23**: the posture is stated, the obligations are mapped to mechanisms
that already exist, and the classification question is left open because it is a
legal determination.*

---

## 67. EU AI Act compliance posture

*Supersedes: none — new. Decision record: `agent-improve/docs/DECISIONS.md` §S2.*
**Status: SCAFFOLD. The classification question is UNRESOLVED and requires qualified legal advice.**

### 67.1 The deadlines are now fixed

**Verified as of 2026-08-23.** The Digital Omnibus is enacted law — Regulation
(EU) 2026/1744, in force 27 July 2026 — and the high-risk deadlines are
**fixed and unconditional**:

| Date | Scope |
|---|---|
| **2 December 2027** | Standalone Annex III systems — **includes employment** |
| 2 August 2028 | High-risk AI embedded in regulated products (Annex I) |

Transparency (Art. 50), GPAI and prohibited-practices duties are **already in
force** and were not delayed.

### 67.2 The classification question — open, and not answered here

**Agent Improve MAY be Annex III high-risk via the employment category.** It
coaches professionals and produces assessments that *could* feed competence or
advancement decisions.

**Whether it crosses the line depends on deployment, not on the code:**

| Deployment | Likely classification |
|---|---|
| Gate outputs feed a formal evaluation of the Belt | **Likely high-risk** |
| A private learning aid with no institutional consequence | **Likely not** |

**This is a legal determination requiring qualified advice before December
2027. It is not made in this document, and no reader should treat this section
as legal advice.**

> **The architecture is designed defensively so that if the answer is
> high-risk, no retrofit is needed.** That is the whole reason this Part is
> scaffolded now rather than after the classification is settled — the eight
> obligations below map to mechanisms that already exist, and the cost of
> having built them anyway is small compared to the cost of discovering in 2027
> that human oversight was never architectural.

### 67.3 The eight core provider obligations

**Agent Improve already has much of the skeleton.** Each row names the existing
mechanism, not an aspiration:

| Article | Obligation | Existing mechanism |
|---|---|---|
| **9** | Risk management across the lifecycle | The DORA register (§68) is this, made operational |
| **10** | Data governance | Azure index schemas (§23); evidence provenance and the single-channel rule (§29.1); `uploads` as the complete external-evidence record (§6) |
| **11** | Technical documentation | This document, and Part XII in particular — the spec layer *is* the technical documentation obligation |
| **12** | Record-keeping and logging | `step_log` with deterministic keys (§11, §47); LangSmith tracing (§51); `citations` and `uploads` in every gate document (§33.2) |
| **13** | Transparency to users | The UI contract — the Belt is informed they interact with an AI coach; contextual feedback; the LangSmith run id surfaced for escalation (§50) |
| **14** | Human oversight | The nine-step HITL gate — **no field is committed without Belt approval** (§33); the gate review screen is editable (§50); the checkpoint commits only after approval (§33.3) |
| **15** | Accuracy and robustness | The four-layer validation stack (§34); the two-tier field rule (§35); anti-hallucination guards (§22); contradiction detection (§37); grader temperature pinned at 0.1 (§21) |
| **43** | Conformity assessment | Downstream — it needs all of the above demonstrable, which is what the register in §68 is for |

### 67.4 One compliance finding is already recorded in this document

**§46.1 states that the v2.1 single-region fallback chain is non-compliant for
any regulated-entity deployment** under DORA's ICT resilience obligations, and
that EU AI Act data-governance provisions are why the secondary region must be
inside the EU. It is Appendix B item 16, and it gates a production launch.

**It is carried into the register at §68 rather than restated here.**

### 67.5 Compliance-source discipline

**The EU AI Act and DORA are in active implementation with shifting guidance.**

- **Any compliance claim must cite a current-dated source.**
- **If availability cannot be verified, mark it "unverified — requires legal
  validation" rather than asserting it.**
- **This is not legal advice.** The classification question of §67.2 needs
  qualified counsel.

Sources are in Appendix C, under *Tier 1 — compliance*.

---

## 68. The DORA-structured compliance risk register

*Supersedes: none — new. Decision record: `agent-improve/docs/DECISIONS.md` §S2.*
**Status: SCAFFOLD, populated from the five AI-ACT flags placed 2026-08-23.**

### 68.1 Why DORA structure

**DORA — Regulation (EU) 2022/2554 — applies directly to financial customers**,
who must track a third-party AI vendor as ICT risk. Its register structure is
also the *universal* risk-register shape every industry uses: a manufacturer
reads the same table as their own risk register.

**So one DORA-structured table is cross-industry by construction** — legible to
a bank as DORA, and to a factory as a risk register. That is the reason for the
choice, and it is worth stating because the alternative reading is that a DMAIC
coaching product has acquired a financial-services artifact for no reason.

**The `Customer Negotiation` column is deliberately open.** The register is the
artifact handed to a prospect: *here are our AI's high-risk functions, here is
how each is already mitigated, here is the residual risk to discuss.*

### 68.2 The register

**The flag is canonical; the register is derived.** When they disagree, the
flag wins and the row is regenerated (§55.1). Each row cites the function and
the behavior IDs it aggregates, so row-to-flag correspondence is checkable by
Risk ID.

| Risk ID | Function | Risk Description | AI Act Art. | Likelihood | Impact | Current Mitigation | Residual Risk | Owner | Customer Negotiation |
|---|---|---|---|---|---|---|---|---|---|
| **R-EXEC-01** | `phase_executor` (coach) — S-F04, behaviors B1–B6 | AI coaching output could influence a Belt's competence/employment assessment without adequate oversight, or could assert an unverified fact | 13, 14, 15, 12 | Med | High | HITL gate approval (§13); anti-hallucination guard; 4-layer validation (§35); full audit log (§51) | Low–Med — residual depends on whether customer uses gate outputs in formal evaluation | [Provider] | *open — depends on deployment context; customer confirms whether coaching feeds formal assessment* |
| **R-VALSTACK-01** | `validation_stack` — S-F05, behaviors B1–B4, B7; Layer 2d — S-F26, behaviors B1–B7 | The pass/fail assessment of a Belt's completed phase is produced here. Where a customer deploys it into a formal evaluation, that verdict is the artifact the evaluation rests on. An LLM grader could fail a sound document, or pass a weak one | 14, 15, 12, 13 | Med | High | Verdict is per criterion, never a score (§35); Tier 2 can never `fail`; temperature pinned at 0.1 so verdicts are reproducible (§21); three linkage criteria verified by deterministic lookup, not judgment (§36); every attempt logged (§11); the verdict gates a Belt-editable interrupt rather than committing anything | **Med** — the grader's judgment is not appealable inside the system; the Belt's recourse is the retry loop and then escalation | [Provider] | *open — customer confirms whether a gate verdict is recorded against the individual or only against the project* |
| **R-GATEREV-01** | `gate_review_node` — S-F06, behaviors B1–B3 | This is the human-oversight surface. **If it renders fields the Belt cannot edit, gate step 5 does not exist** and the Art. 14 claim made throughout this architecture is false | 14, 13, 12 | Low | **High** | Graph-level `interrupt()` rather than `HumanInTheLoopMiddleware`, whose edit/reject bugs would silently discard a Belt's correction (§19.9); every validated field editable with an explicit approve action (§50); no checkpoint commits before approval (§33.3) | Low — provided the UI contract holds; **this is the row where a UI regression becomes a compliance regression** | [Provider] | *open — customer may require evidence that the review screen is editable in the deployed build* |
| **R-GATEAPPLY-01** | `gate_apply_node` — S-F07, behaviors B1–B8 | Commits the assessed record. Everything downstream reads what it writes, including any customer evaluation built on top. A partial or incorrect commit propagates silently | 14, 12, 10, 15 | Low | High | Runs only after explicit Belt approval (§33); writes to both Store and state so a crash cannot desynchronise them (§33.2); the document carries `citations`, `uploads`, `computation_results` and `acknowledged_gaps`, so what the phase was grounded in and what it consciously skipped are both visible; Tier 1 access raises rather than silently defaulting (§40.1) | Low–Med — **the compensating-action dependency (§45) is BLOCKED on the LangGraph upgrade**, so an external-write failure is currently uncompensated | [Provider] | *open — customer may require the audit trail as a deliverable* |
| **R-CONTRA-01** | `ContradictionDetectionMiddleware` — S-C10, behaviors B1–B5 | The only component that can retroactively unsettle a committed record, via the re-approval cascade. **Detection is best-effort semantic judgment by the coach and can miss**, so a Belt's contradiction of a gate-approved value may go unflagged and downstream analysis may continue against a superseded number | 14, 15, 12, 13 | **Med–High** | Med | No tolerance threshold, so any material change is a mini-gate rather than a silent overwrite (§37); the Belt is given two explicit options with the approved value, its approving phase and their own words (§50); **§50's always-referenceable all-gate-fields tab is the acknowledged human backstop**, which is architecture rather than UI polish | **Med — stated honestly.** The previous mechanism detected nothing while appearing deterministic (DECISIONS §R1); this one is weaker in claim and stronger in fact, and the backstop is a human reading a tab | [Provider] | *open — customer should be told detection is best-effort and the tab is the control* |

### 68.3 Pending classification — not register rows

**Twelve entries carry `AI-ACT-REVIEW: uncertain`.** They are held here rather
than in the register above, because §55.1's rule is bidirectional — every row
traces to a flag, and every flag appears in the register — and putting
unresolved classifications in it would break the check in both directions.

| Entry | Why classification is genuinely unclear |
|---|---|
| `rag_lookup_methodology` (S-F14) | Grounds coaching in methodology (Art. 15); §27 records a real failure in which retrieval breakage read to the Belt as an absence of guidance |
| `rag_lookup_evidence` (S-F15) | Reads Belt-supplied operational documents; the `case_id` filter is the only tenancy boundary in the retrieval path (Art. 10) |
| `rag_lookup_case_history` (S-F16) | Surfaces other Belts' project data with no tenancy filter today (Art. 10; Appendix B item 1) |
| `CoherenceMiddleware` (S-C13) | Its silent retry is the one scoped exception to the transparency principle — reasoned opacity, but opacity (Art. 13) |
| `DMAICGraderMiddleware` (S-C14) | Grades the coach rather than the Belt, but can suppress or alter what the Belt receives, and its warning flag is Belt-visible |
| `DMAICGateValidator` (S-C26) | Participates in the gate decision, but deterministically and without judgment — arguably a mitigation rather than a risk surface |
| Layer 2c constraint check (S-F25) | Judges the quality of the Belt's own stated decision — closer to assessing the person than any other layer |
| The policy advisory (S-F27) | Reviews a human's corrections; oversight support, but also the last check before commit and one of three anti-hallucination defences |
| The escalation subgraph (S-F08) | An oversight mechanism, and also the terminal path for a Belt whose phase could not pass |
| `request_human_approval` (S-F22) | An oversight escape hatch with no judgment of its own |
| `degraded_mode_response` (S-F30) | Belt-facing content produced under failure; must not misrepresent system state (Art. 13) |
| The `improve_case_index` write path (S-F36) | Publishes one Belt's project record into a corpus other Belts retrieve from, with no tenancy filter (Art. 10) |

### 68.4 The infrastructure risk already on record

**Carried from §46.1, not newly asserted:**

| Risk ID | Item | Status |
|---|---|---|
| **R-INFRA-01** | The v2.1 fallback chain is single-region — Levels 1, 2 and 3 are all in Azure West Europe. A Frankfurt outage collapses three levels simultaneously rather than degrading one at a time. **DORA's ICT resilience obligations require geographic redundancy for continuity of critical functions, which makes this non-compliant for any regulated-entity deployment** — a launch blocker for that market, and EU AI Act data-governance provisions are why the secondary region must be inside the EU | Ratified v2.2 replacement designed (§46.1); **Appendix B item 16**; promotion trigger is *before production launch with real Belts* |

**This row has no AI-ACT flag behind it and is not derived from one.** It is a
DORA-side entry, recorded here because the register is the artifact handed to a
prospect and a bank will ask this question first. It is marked as such so the
flag-is-canonical rule is not read as broken by its presence.

---

# Appendices

---

## Appendix A — Provenance index

**Old reference → this document.** Use this to resolve any `§X` citation in
`agent-improve/CLAUDE.md`, `agent-improve/docs/DECISIONS.md`, `agent-improve/docs/REVIEW_DECISIONS.md`, the SKILL.md
files, or code comments.

### A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference

| Old | New | Topic |
|---|---|---|
| §1 | §8, §10 | Checkpointing, persistence |
| §2 | §33, §38, §39 | HITL gates, escalation |
| §5 | §17 | Planner/Executor |
| §10 | §6 | Subagent state |
| §11 | §17 | Recursive planner/executor |
| §17 | §5 | `SupervisorState` |
| §18 | §6, §11, §40 | `PhaseState`, `step_log` |
| §19 | §9 | Multi-step chaining, boundary mappers |
| §20 | §17 | Supervisor/worker |
| §21 | §14 | Node contract, state passing |
| §22 | Appendix B item 10 | Debate agents — **deferred** |
| §23 | §12, §13, §16 | Subgraph architecture |
| §24 | §51, §55 | Governance and debugging |
| §25 | Appendix D | Gap register |
| §27, §28 | — | LCEL — **not used**, historical |
| §29 | §19.5, §21 | Retry middleware, structured output |
| §30 | §15 | Routing |
| §32, §33 | §24, §25 | Multi-query, RRF |
| §34 | §26 | Multi-hop mechanism |
| §35 | §25 | Query voting — RRF chosen |
| §36 | §23, §28 | Vector memory, index schemas |
| §37 | §23, §28 | Memory patterns |
| §38 | §22, §37 | Memory hierarchy, contradiction |
| §39 | §29, §30, §31 | Knowledge tools, MCP-out, computation tools |
| §40 | §22, §23 | Metadata signals |
| §41 | §24 | Retrieval pipeline |
| §42 | §36, §43 | Grader middleware, coaching method |
| §43 | Appendix B item 14 | Agent roles — Observer deferred |
| §44 | §9, §12, §15, §33 | Architecture diagnosis, boundary mechanisms |
| §45 | §55, Appendix C | Anti-drift, trusted sources |
| §46, §47 | Appendix B item 11 | Coordination, aggregation — **deferred** |
| §48 | §34, §36 | Reflection vs consensus |
| §49 | §45 | Saga → `error_handler=` |
| §50 | §18, §53 | Version corrections |
| §51 | §34 | InsightForge reference implementation |
| §52, §52a | §8, §9 | Checkpointer + Store |
| §53 | §19 | Built-in middleware |
| §55, §72 | §53 | LangServe, LangGraph Server |
| §56 | §53 | Stale deployment tooling |
| §57–§65 | §29.1 | **MCP — architecturally excluded** |
| §66, §67 | §44, §46 | Circuit breaker, fallback chain |
| §68, §69 | §34, §35 | Validation stack, layer placement |
| §70 | §9 | Inter-stage dependency |
| §71 | §26 | Multi-hop design layer |
| §73 | §51 | Langfuse — LangSmith retained |
| §74 | §53 | API versioning |
| §75 | §52 | Evaluation dataset |
| §76 | §53 | Docker |
| §77 | §50 | Frontend requirements |
| §78 | §53 | Developer orchestration menu |
| §79 | §44, §45 | LangGraph 1.2 reliability primitives |
| §80 | §19 | AgentMiddleware six hooks |
| §81 | §21 | Content blocks |
| §82 | §20, §21 | ProviderStrategy, structured output |
| §83, §84 | §32, §19.2 | Agent Skills, SkillsMiddleware |
| §85 | §51 | LangSmith 2026 additions |
| §86 | §55 | Hook mechanics |
| §87 | Appendix B | Deferred backlog |
| §3, §4, §6–§9, §12–§16, §26, §31, §54 | — | Course material and historical notes — **no section here**; retained in `agent-improve/docs/REFACTORING_AGENT_IMPROVE.md` |

### A.2 `agent-improve/ARCHITECTURE.md` → this reference

`ARCHITECTURE.md` is **absorbed** by this document.

| Old | New |
|---|---|
| §0 | §2 |
| §1 | §1, §4 |
| §2 | §1, §50 |
| §3.1 | §12, §15, §16 |
| §3.2 | §13, §14 |
| §3.3 | §18, §21, §22 |
| §3.4 | §19 |
| §3.4.1 | §36 |
| §3.4.2 | §43 |
| §3.5 | §17 |
| §3.6 | §33 |
| §3.7 | §34 |
| §3.7.1 | §35 |
| §3.8 | §37 |
| §3.9 | §38 |
| §4.1 | §5 |
| §4.2 | §6 |
| §4.3 | §9 |
| §4.4 | §11 |
| §4.5 | §8 |
| §4.6 | §7 |
| §4.7 | §7, §42 |
| §4.8 | §7 |
| §4.9 | §5 |
| §4.10 | §20, §40 |
| §4.10.2, §4.10.3 | §40 |
| §4.10.5–§4.10.7 | §41 |
| §5 | §54 |
| §6.1, §6.2 | §8 |
| §6.3 | §9 |
| §6.4, §6.5 | §10 |
| §6.6 | §46 |
| §6.7 | §8 |
| §7.1–§7.3 | §23 |
| §7.4 | §24, §25 |
| §7.5 | §26 |
| §7.6 | §23.5 |
| §7.7 | §23.5 |
| §8.1 | §29, §31 |
| §8.2 | §30 |
| §8.3 | §25 |
| §8.4 | §32 |
| §9.1 | §44 |
| §9.2 | §45 |
| §9.3, §9.4 | §46 |
| §9.5 | §48 |
| §10 | §49 |
| §11 | §50 |
| §12 | §51 |
| §13 | §35, §39 |
| §13.6 | §35 |
| §14 | §52 |
| §15 | §53.1 |
| §16 | Appendix B, Appendix D.3 |
| §17 | — · Decisions-resolved register. **No section here**: each entry's *conclusion* is stated in the section that owns the topic, and the register itself is a historical artefact. **Extracted 2026-08-22 to `agent-improve/docs/ARCHITECTURE_v2216_registers.md`** |
| §18 | — · Change log. **No section here**, by design — this document states conclusions, not their history (§"About this document"). **Extracted 2026-08-22 to `agent-improve/docs/ARCHITECTURE_v2216_registers.md`** |
| §18.1 | §56 |

**Absorption completed 2026-08-21.** Nine items of `ARCHITECTURE.md` content
had no home here when the absorption was first declared and were written in
during this sweep: the one-way-door gate principle (→ §33), parallel-case
isolation (→ §16), ETag concurrency and the Blob-vs-alternatives rationale
(→ §8), the `analyse` rename scope table, the checkpoint / node-name warning
and the `improve_case_index` vector profile (→ §23.3), the conflict-resolution
panel and the LangSmith run id (→ §50), the three-mechanisms-check-these-fields
distinction (→ §35), cache invalidation policy (→ §46) and the structured log
field list (→ §51). **`agent-improve/ARCHITECTURE.md` was genuinely absorbed.** On 2026-08-22 that
path was reused for a copy of this document (see the two-document division
above); the absorbed v2.2.16 original is at commit `8533879`.

---

## Appendix B — Deferred backlog

*Supersedes: REFACTORING §87.*

**Every item has a promotion trigger. An item with no trigger is not deferred —
it is excluded** (see Appendix D).

| # | Source | Capability | Promotion trigger |
|---|---|---|---|
| 1 | §24 | Multi-tenant filtering on `improve_case_index` | Agent Improve deployed to multiple organisations |
| 2 | §25 | Per-source weighting in RAG fusion | A fourth retrieval source is introduced |
| 3 | §28 | Per-turn episodic entries in the case index | Gate-level summaries shown to lose actionable detail |
| 4 | §28 | Mid-phase summary persistence | Belts frequently resume in-flight cases weeks later |
| 5 | §28 | **Dynamic procedural memory** — per-Belt coaching adaptation from LangSmith trace analysis | **No signal needed — v2.2 priority workstream** |
| 6 | §24 | Similarity-threshold calibration | The §52 eval dataset is populated |
| 7 | §24 | Dynamic top-k based on remaining context | Fixed top-k causes context-budget problems |
| 8 | §25 | Reactive self-correcting query restructuring | Multi-query + RRF shown insufficient |
| 9 | §23 | Feedback-driven chunk score adaptation | Systematic misses static ranking cannot fix, **and** a dedicated research workstream exists |
| 10 | §36 | Adversarial debate subgraph for root cause validation (Analyse only) | **Base coaching loop stable in production and the Analyse coach producing root causes that need adversarial stress-testing** |
| 11 | §36 | Opinion aggregation framework | Item 10 implemented and producing confidence scores |
| 12 | §45 | `DeltaChannel` for checkpoint compression | Sessions exceed ~200 turns |
| 13 | §8 | **Migrate to `PostgresSaver` + `PostgresStore`** | **Post-refactor testing complete, before production launch** |
| 14 | §51 | Observer Agent — system-wide monitoring across all Belts | Multiple concurrent projects generating enough traffic |
| 15 | §23 | Multi-source knowledge index — `source_document`, `tenant_id` | A customer supplies their own methodology alongside the BB eBook |
| 16 | §46.1 | **Geographic redundancy — secondary EU region** | **Before production launch with real Belts; DORA compliance requires it** |
| — | §26 | Model tiering per hop (gpt-4o-mini intermediate / gpt-4o final) | LangSmith shows repeated 5-hop cap hits on Analyse turns |

**Items 13 and 16 are the two that gate a production launch.**

---

## Appendix C — Trusted sources

*Supersedes: REFACTORING §45.*

**Ordered. Check Tier 1 before any architectural decision.**

### Tier 1 — current, authoritative

| Source | Date | Topic |
|---|---|---|
| `anthropic.com/engineering/effective-harnesses-for-long-running-agents` | Nov 2025 | Harness concept, context reset, session bridging |
| `anthropic.com/engineering/harness-design-long-running-apps` | Mar 2026 | Planner/Generator/Evaluator. **A specific research write-up on long-running coding harnesses** — strong evidence from an adjacent domain, not a specification |
| `anthropic.com/engineering/managed-agents` | Apr 2026 | Brain/hands separation, scaling |
| `anthropic.com/engineering/how-we-contain-claude` | Jul 2026 | Containment, blast radius |
| `anthropic.com/engineering/effective-context-engineering-for-ai-agents` | Sep 2025 | Context-window management — §19.3 |
| `anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills` | Oct 2025 | SKILL.md spec — §32 |
| `anthropic.com/engineering/demystifying-evals-for-ai-agents` | Jan 2026 | Eval design — §52 |
| `anthropic.com/engineering/writing-tools-for-agents` | Sep 2025 | Tool design — §29, §30 |
| `anthropic.com/engineering/designing-ai-resistant-technical-evaluations` | Jan 21, 2026 | Eval design that resists gaming — **added 2026-08-21**, bears on §52 |
| `anthropic.com/engineering/quantifying-infrastructure-noise-in-agentic-coding-evals` | Feb 05, 2026 | Separating real regressions from infrastructure noise — **added 2026-08-21**, bears on §52's >10% threshold |
| `anthropic.com/engineering/advanced-tool-use` | Nov 24, 2025 | Advanced tool use on the Claude Developer Platform — **added 2026-08-21**, bears on §29, §30, §31 |
| `docs.langchain.com`, `reference.langchain.com` | Ongoing | LangChain / LangGraph API surface |
| `github.com/langchain-ai/*` | Ongoing | Versions, breaking changes, open issues |
| `langchain-ai.github.io/langmem` | Ongoing | Memory taxonomy — §28 |
| `pypi.org` | Ongoing | Package versions |

### Tier 1 — compliance

*Added 2026-08-23 with Part XIII.*

| Source | Topic |
|---|---|
| `https://artificialintelligenceact.eu/implementation-timeline/` | EU AI Act implementation timeline — the deadlines in §67.1 |
| `https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai` | EU AI Act, European Commission — the regulatory framework |
| `https://ai-act-service-desk.ec.europa.eu` | EU AI Act Service Desk — guidance and classification questions |
| EUR-Lex, Regulation (EU) 2022/2554 | DORA regulation text — the register structure of §68 |
| GitHub Spec Kit; AWS Kiro (`kiro.dev/docs/specs`) | Spec-Driven Development method references — the basis for Part XII's structure |

> **Compliance-source discipline.** The EU AI Act and DORA are in **active
> implementation with shifting guidance**. Any compliance claim must cite a
> current-dated source; **if availability cannot be verified, mark it
> "unverified — requires legal validation" rather than asserting it.** Nothing
> in Part XIII is legal advice, and the classification question of §67.2 needs
> qualified counsel.

### Tier 2 — official announcements

`langchain.com/blog` · `anthropic.com/news/*` · `claude.com/blog/*`

### Tier 3 — informed practitioner, cross-check before citing

`marsdevs.com/guides` · `deepwiki.com/langchain-ai/*` · `agentpatterns.ai`

### Downgraded — historical

`anthropic.com/engineering/building-effective-agents` (Dec 2024). **Still
sound** — its core advice, *"find the simplest solution possible,"* is the
principle behind §18's custom-middleware decision. Ordered lower because newer
specific material exists, **not because it was refuted.**

### Excluded

Stack Overflow, Reddit, Medium, Dev.to — unless linking directly to Tier 1.

### Index refresh — 2026-08-21

**The `anthropic.com/engineering` index was re-read in full. Nothing has been
published after this list's August 2026 cutoff** — the newest dated post is
*"An update on recent Claude Code quality reports"* (Apr 23, 2026), with *"How
we contain Claude across products"* currently featured.

**Three posts inside the window were missing from this list and have been
added** (above). They were not new; they were simply never picked up when the
list was built. Two bear directly on §52's evaluation design, which is the
part of this architecture with the least production evidence behind it.

**Posts deliberately not added**, being product/model-specific rather than
architectural: *Claude Code auto mode* (Mar 25), *Eval awareness in Claude Opus
4.6's BrowseComp performance* (Mar 06), *Building a C compiler with parallel
Claudes* (Feb 05), *An update on recent Claude Code quality reports* (Apr 23).

---

## Appendix D — Retired names, banned patterns, and exclusions

### D.1 Retired names — never reintroduce

> **These strings are load-bearing.** `grep-absence` verification in the
> Refactoring Procedure checks for them literally, so a wrong name here produces
> a check that passes while the real pattern survives. The retrieval-tool row
> was wrong on exactly this until 2026-08-21.

| Retired | Use instead | §ction |
|---|---|---|
| `project_id` | `case_id` | §5 |
| `captured_fields` (prose), `phase_inputs` (v1 code) | `artifacts` | §6 |
| `project_context`, `dmaic_plan`, `key_decisions`, `open_items` | Derived or store-mediated | §5 |
| `gate_documents` store namespace | `artifacts` | §9 |
| `step_index` | `phase_index` / `field_index` | §6 |
| `analyse_phase` as a phase key | `analyse` | §23.3 |
| `completeness_score` | Derived from `artifacts` | §5, §50 |
| `record_field` tool | `CoachingResponse.fields_captured` | §29.3 |
| `search_improve_knowledge`, `search_improve_cases`, `search_improve_evidence` — the **tool** layer only | `rag_lookup_*` | §24 |
| `policy_advisory`, `revise` as node names | Logic in `gate_apply`; an edge | §13 |
| `RetryMiddleware` | `ModelRetryMiddleware` / `ToolRetryMiddleware` | §19.5 |
| `phase_router` node | Static edges | §15 |
| `ORCHESTRATOR_{PHASE}_CONTEXT`, `EXTRACTION_{PHASE}`, `KNOWLEDGE_INJECTION_TEMPLATE` | — | §22 |

### D.2 Banned patterns

**State and persistence** — artifacts on `SupervisorState` · numeric captured
fields · typed per-phase computation destinations · `gate_attempts` in route
scope · merging `validator_feedback` and `belt_edits` · merging
`issues_and_barriers` and `acknowledged_gaps` · `str`-typed `control_plan`,
`process_map_sipoc` or `detailed_process_map` · per-phase or concatenated
`thread_id` · checkpointer or store on a subgraph · `InMemorySaver` · case blob
written mid-conversation · cross-phase data through parent state or string
interpolation · tuples in `step_log`

**Graph** — mixing static edges and `Command` from one node · `set_entry_point`
· manual node dispatch in routes · `_reflect()` as a private function · fusing
planner and executor · a node with external writes and no `error_handler` ·
hand-written Saga orchestrators

**LLM and tools** — direct `AzureChatOpenAI` instantiation · binding tools onto
a bare model in a phase executor · `create_react_agent` · imports from
`langgraph.prebuilt` · deepagents while pre-1.0 · parsing JSON from raw LLM text
· string-indexing raw content · more than 16 tools on a phase executor ·
parameterised computation-tool grouping · `MultiQueryRetriever` ·
`EnsembleRetriever` · `OutputFixingParser` · deprecated `Conversation*Memory`
classes

**Validation and gates** — a gate passing with a Tier 1 failure · a Tier 2 gap
blocking a gate · dropping an acknowledged gap · recommending DOE to a Green
Belt · raw computation output without concept and interpretation · approving a
gate without both writes · showing the Belt the grader loop · a tolerance
threshold on contradiction detection · capping Level 2 coached improvement ·
making the policy advisory blocking · committing a checkpoint before approval ·
`HumanInTheLoopMiddleware` for gates · retrieval during gate validation

**Retrieval** — unconditional retrieval pipelines · bare `except Exception`
returning `[]` · a failure message that reads as absence · filtering methodology
on `phase` or `'all'` · writing to an index without `fields=` · `add_texts`
without `ids=` · writing to Agent Resolve indexes · any MCP dependency · a
fallback path fetching data the Belt did not upload

**Prompts and governance** — inline prompts in node files · omitting the memory
hierarchy or anti-hallucination guards · classes outside §54's files ·
duplicating `CitationRecord` · disabling LangSmith · methodology jargon in
team-facing strings · renumbering a rule cited in `deprecated_patterns.yaml`
without updating the registry

### D.3 Architecturally excluded — not deferred

**MCP-dependent capabilities** — real-time system data, external verification
benchmarks, an AgentLean MCP server. **There is no promotion trigger because
there is no path to promotion**: the data channel is always uploaded documents
(§29.1).

**FMEA as a tracked schema field** (§41).

---

## Appendix E — Current state

**As of 2026-08-21.** This appendix is expected to go stale; it records where
the implementation stands relative to the design, so the gap is explicit rather
than discovered.

### What exists

| Component | Status |
|---|---|
| `core/checkpointer.py` — `AzureBlobCheckpointSaver` | **Implemented and compiled in — but INERT.** `thread_id` and `ainvoke` appear nowhere, so it has never written a checkpoint (§53.1) |
| `core/state.py` | v1 `ImproveGraphState` — **not** `SupervisorState` |
| `core/graph.py` | v1 flat graph, 11 nodes, `set_entry_point` |
| `knowledge/retriever.py` | v1, **but already carries the correct `phase_relevance` filter and `fields=` declaration** |
| `knowledge/tools.py` | v1 `search_*` names, no multi-query, no RRF |
| `phases/{phase}/schema.py` | v1 `{Phase}PhaseInput` |

### What does not exist yet

`core/substate.py` · `core/store.py` · `middleware/` · `validation/` ·
`knowledge/tool_args.py` · `knowledge/computation.py` · `knowledge/fusion.py` ·
`core/reliability.py` · `core/diagrams.py` · `phases/{phase}/mappers.py` ·
`phases/{phase}/graph.py`

### Known violations in current code

| Site | Rule |
|---|---|
| `gateway/routes.py` — `get_graph()` called, then nodes dispatched manually; **the compiled graph is built and discarded** | §49 |
| Phase nodes are sync `def`, called unawaited | §14 |
| `core/graph.py` — `set_entry_point` | §12 |
| `core/llm.py` — contains a class; role map diverges from §21 | §54, §21 |
| `gateway/routes.py:67` and `upload/agent.py:107` — parse `response.content` directly | §21 |

### Blocked

**`langgraph` 1.1.10 < 1.2.6** blocks all of §45 and the §16 subgraph
namespacing (§53).

**Two Azure schema changes are ratified and unapplied** — `improve_evidence_index`
`phase` + `uploaded_at`, and `improve_case_index` `embedding` →
`content_vector` (§23). **Batch them.**

---

*End of document.*
