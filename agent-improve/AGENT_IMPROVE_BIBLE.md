# Agent Improve — Architecture Reference
**AgentLean Platform · DMAIC Improvement Agent**
Version 1.0-draft · 2026-08-21
Status: **IN PROGRESS** — Parts I–II written. Parts III–XI pending.
Not yet cross-checked against live sources (Task 3B).

---

## About this document

This is the architecture reference for Agent Improve. It states the ratified
design directly: what the system is, how each part is shaped, and why the
non-obvious choices were made that way.

**It is written to be built against.** A reader should be able to implement
Agent Improve from this document without reconstructing anything from memory
or reading a second file. Where a concept has a definition, that definition
appears **once**, in one canonical section, and everything else
cross-references it.

**What this document is not.** It is not a learning register and not a review
log. The reasoning trail that produced these decisions — what a course taught,
what was corrected, which options were rejected and when — lives in
`docs/EDUCATIONAL.md` (the original chronological register),
`docs/REFACTORING_AGENT_IMPROVE.md` (the section-by-section review), and
`docs/REVIEW_DECISIONS.md` / `docs/DECISIONS.md` (the decision log). Those
remain the historical record. This document states conclusions.

**Rationale is kept where it is load-bearing.** "Narrative scaffolding
removed" does not mean "reasoning removed." Where a design choice is
non-obvious — static edges rather than `Command` routing, the Store rather
than shared state keys, two graders rather than one — the reasoning is stated
here, because an implementer who does not understand *why* will reimplement
the thing the rule exists to prevent.

### The two-document division

| Document | Answers | Binding? |
|---|---|---|
| `CLAUDE.md` | **What the rule is.** Quoted in every implementation prompt | **Yes** |
| `AGENT_IMPROVE_BIBLE.md` (this file) | **How the system is shaped, and why.** Component design, schemas, contracts, sequencing | **Yes** |

`ARCHITECTURE.md` was absorbed into this document. Where this file and
`CLAUDE.md` describe the same thing, `CLAUDE.md` states the rule and this file
states the design; neither restates the other's job.

### Section numbering and provenance

This document renumbers. Sections here do **not** correspond to the 87-section
numbering of `REFACTORING_AGENT_IMPROVE.md`, nor to `ARCHITECTURE.md`'s
numbering. Each section carries a **Supersedes** line naming its sources, and
**Appendix A** is the reverse index: old reference → new section.

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
| **Agent Improve** | DMAIC coaching (this document) | In refactor |
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
`error_handler=` and `RunControl.request_drain()` (Part IX) and the subgraph
`checkpoint_ns` fix (§16) all require ≥1.2.6 and are therefore **unavailable
today**. Resolving the correct upgrade target is Task 3B scope; the previously
documented 1.2.10 pin is already stale.

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

```python
class SupervisorState(TypedDict):
    messages:       Annotated[list[BaseMessage], operator.add]
    history:        Annotated[list[str], operator.add]
    case_id:        str
    phase_index:    int
    current_phase:  str
    gate_passed:    dict[str, bool]
    final_output:   Optional[dict]
```

**Seven fields. That is the entire schema.** An eighth requires an amendment.

### Field by field

| Field | Type | Written by | Read by |
|---|---|---|---|
| `messages` | `Annotated[list[BaseMessage], operator.add]` | Route on each Belt turn; subgraph returns | Input mappers (§9), seeding `PhaseState.messages` |
| `history` | `Annotated[list[str], operator.add]` | Every node, on entry | Debugging and trace reconstruction only |
| `case_id` | `str` | Once, at session start | Everything — it is also `thread_id` and the store namespace segment |
| `phase_index` | `int` | **Output mapper only** | UI progress, readability |
| `current_phase` | `str` | **Output mapper only** | Routing, state injection, index writes |
| `gate_passed` | `dict[str, bool]` | **Output mapper only**; re-approval cascade sets `False` (§37) | Supervisor routing — the thing Level 1 actually decides on |
| `final_output` | `Optional[dict]` | Control's output mapper, at the final gate | API response at project completion |

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

**Seventeen fields — three plumbing plus fourteen content.** A fifteenth
content field requires an amendment.

### Field by field

| Field | Type | Written by | Read by |
|---|---|---|---|
| `messages` | `Annotated[list, operator.add]` | Input mapper seeds it; the agent loop appends | The agent loop; `SummarizationMiddleware` (§19) |
| `history` | `Annotated[list[str], operator.add]` | Every node on entry | Debugging |
| `phase_context` | `str` | **Input mapper only**, composed from the Store | Planner; state injection (§19) |
| `coaching_plan` | `Optional[CoachingPlan]` | Planner node, overwritten each turn | Executor node |
| `field_index` | `int` | Planner node | Planner — which field within the phase |
| `draft` | `dict[str, Any]` | Executor node — this turn's extraction | Validation stack; `gate_review` |
| `artifacts` | `dict[str, Any]` | Executor (from `fields_captured`); `gate_apply` (Belt edits) | Planner, `check_gate_status()`, validation stack, gate assembly, state injection |
| `step_log` | `Annotated[list[dict], operator.add]` | Validation layers, grader `on_evaluation`, fallback chain | Audit trail; written into the gate document |
| `belt_edits` | `dict[str, Any]` | `gate_apply`, from the interrupt resume payload | `gate_apply` |
| `turn_count` | `int` | Executor node | Planner; `step_log` key construction (§11) |
| `final` | `dict[str, Any]` | `gate_apply_node` | Output mapper; crash recovery |
| `gate_attempts` | `int` | Validation stack increments; `gate_apply` resets to `0` | Validation stack; the escalation edge at `>= 3` |
| `validator_feedback` | `list[dict]` | Validation stack appends; `gate_apply` resets to `[]` | Coach, on retry |
| `citations` | `list[dict]` | Executor, from `CoachingResponse.citations` | Gate document assembly |
| `uploads` | `list[dict]` | Upload handler | Gate document assembly; evidence context |
| `hop_results` | `list[str]` | `analyse_executor_node` | The synthesis call; LangSmith state view |
| `synthesis_output` | `Optional[dict]` | `analyse_executor_node`, from the synthesis call | The coach call |

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

**It is a Pydantic model, produced via `with_structured_output`:**

```python
class CoachingPlan(BaseModel):
    focus_field:        str
    next_action:        str
    retrieval_strategy: Literal["single_hop", "multi_hop"]
    retrieval_hops:     list[str]     # template strings; empty for single_hop
```

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

```python
{"attempt": 1, "layer": "grader",
 "criteria_failed": ["root_cause_validation"],
 "feedback": "does not reference statistical evidence",
 "timestamp": "2026-08-03T11:04:19Z"}
```

The coach reads the full list on retry. **The shared cap of 3 is defensible
only because each attempt is better informed than the last** — a cap on
retries that carry no memory of the previous failure is just a cap on
repetition, and this field is what carries the memory.

### `citations` and `uploads` — the evidence trail

```python
citations = [{"source": "improve_knowledge_index", "page": 47,
              "content_summary": "GR&R acceptance thresholds", "turn": 5}]

uploads   = [{"evidence_index_id": "...", "filename": "defect_data_q2.xlsx",
              "phase": "measure", "uploaded_at": "2026-05-27T09:19:24+00:00",
              "summary": "baseline defect counts, Q2"}]
```

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

```python
causal_hypothesis = {
    "hypothesis":       "Inadequate onboarding causes error spike in first 60 days",
    "references_phase": "measure",
    "references_field": "baseline_mean",
    "references_value": "12.3%",
}
```

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

```python
class AzureBlobStore(BaseStore):
    def put(self, namespace: tuple[str, ...], key: str, value: dict) -> None: ...
    def get(self, namespace: tuple[str, ...], key: str) -> Item | None: ...
    def search(self, namespace: tuple[str, ...], *, query: str | None = None,
               filter: dict | None = None, limit: int = 10) -> list[Item]: ...
    def delete(self, namespace: tuple[str, ...], key: str) -> None: ...
```

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

```python
def build_phase_subgraph(phase: str, llm):
    tools = UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase]
    ...
    return builder.compile()          # NO checkpointer, NO store
```

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

```python
async def phase_executor(state: PhaseState) -> dict:
    ...
    return {"draft": {...}, "step_log": [{...}]}
```

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

```python
builder.add_edge(START,      "define")
builder.add_edge("define",   "measure")
builder.add_edge("measure",  "analyse")
builder.add_edge("analyse",  "improve")
builder.add_edge("improve",  "control")
builder.add_edge("control",  END)
```

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

### Level 1 routes on `gate_passed`

The supervisor's decision is a deterministic gate-check, not a reasoning step:

```python
def route_after_phase(state: SupervisorState) -> str:
    if state["gate_passed"].get(state["current_phase"]):
        return "next"
    return "escalate" if state["gate_attempts"] >= 3 else "retry"
```

### No subgraph imports another subgraph's nodes

Phases communicate through the Store (§9) and through the parent's edges.
A direct import creates a dependency the graph does not model.

---

## 16. `thread_id`, `checkpoint_ns`, and where persistence attaches

*Supersedes: REFACTORING §23, §44; ARCHITECTURE.md §3.1, §6.1.*
**Status: RATIFIED.**

### One `thread_id` per project

```python
await graph.ainvoke(
    state,
    config={
        "recursion_limit": 50,        # infrastructure backstop, NOT the hop cap
        "configurable": {"thread_id": case_id},
    },
)
```

**`thread_id` is the `case_id` value.** Never per phase, never concatenated —
`{case_id}-define` and similar are **BANNED**.

### The checkpointer and store go on the parent graph ONLY

```python
graph = builder.compile(checkpointer=checkpointer, store=store)   # parent
subgraph = phase_builder.compile()                                # NO args
```

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

```python
class CoachingPlan(BaseModel):
    focus_field:        str
    next_action:        str
    retrieval_strategy: Literal["single_hop", "multi_hop"]
    retrieval_hops:     list[str]     # template strings; empty for single_hop

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

```python
executor = create_agent(
    model=get_llm("coach", max_tokens=1500),
    tools=UNIVERSAL_TOOLS + COMPUTATION_TOOLS_BY_PHASE[phase],
    response_format=CoachingResponse,        # §20 — never a {Phase}Output
    middleware=[...],                        # §19 — all eight, in order
    prompt=PHASE_COACH_PROMPT[phase],
)
```

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

```python
middleware=[
    BeforeModelStateInjection(...),          # 1 · custom · before_agent
    DMAICSkillsMiddleware(...),              # 2 · custom · before_agent
    SummarizationMiddleware(...),            # 3 · core   · before_model
    ModelRetryMiddleware(retries=2),         # 4 · core   · wrap_model_call
    ToolRetryMiddleware(                     # 5 · core   · wrap_tool_call
        max_retries=2, on_failure="continue"),
    ContradictionDetectionMiddleware(...),   # 6 · custom · after_agent
    CoherenceMiddleware(...),                # 7 · custom · after_agent
    DMAICGraderMiddleware(...),              # 8 · custom · after_agent
]
```

**Five custom, three core.** All are built on the six `AgentMiddleware` hooks:
`before_agent`, `after_agent`, `before_model`, `after_model`,
`wrap_model_call`, `wrap_tool_call`.

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
`retries=2`, exponential backoff. Wraps each model call and silently retries
transient timeouts and rate limits.

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

Reads `CoachingResponse.fields_captured` after the executor runs and compares
each captured field against the Store-held gate-approved value for that phase.
**Any mismatch raises `HITLInterrupt`.**

```python
class ContradictionDetectionMiddleware(AgentMiddleware):
    def after_agent(self, state, runtime):
        for field in state["structured_response"].fields_captured:
            prior = store.get(
                ("projects", state["case_id"], "artifacts"),
                state["current_phase"],
            )
            if prior and field["field_name"] in prior:
                if prior[field["field_name"]] != field["value"]:
                    raise HITLInterrupt(
                        field=field["field_name"],
                        approved_value=prior[field["field_name"]],
                        proposed_value=field["value"],
                    )
```

**Deterministic dict comparison. No LLM call**, negligible latency. **No
tolerance threshold**, and none may be added — the reasoning is in §37.

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

```python
class CoachingResponse(BaseModel):
    """Structured extraction from each coaching turn."""
    message:         str                 # coaching text the Belt sees
    fields_captured: list[dict] = []     # [{field_name, value, source}]
    citations:       list[dict] = []     # sources referenced this turn
```

**`value` is `Any`, not `str`, and that is deliberate.** It must carry both
plain string fields and the three cross-phase reference dicts (§7). Typing it
`str` would make `causal_hypothesis`, `solution_linked_to_root_cause` and
`post_improvement_metric` uncapturable. **This is the one place `Any` is
correct**; the values *inside* those dicts are still strings.

### The executor node writes the response into state

```python
result = await executor.ainvoke(state)
resp = result["structured_response"]              # CoachingResponse

for f in resp.fields_captured:
    artifacts[f["field_name"]] = f["value"]       # str or dict
citations.extend(resp.citations)
```

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

*Parts I–IV end here. Parts V–XI to follow.*
