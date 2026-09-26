<!--
  agent-improve/ARCHITECTURE.md
  ORIGINATED AS A COPY of ../AGENTIC_ARCHITECTURE_REFERENCE.md, 2026-08-22.
  Expected to diverge. No sync machinery by design.
-->

> **This is Agent Improve's architecture document.** It originated as a copy of
> `../AGENTIC_ARCHITECTURE_REFERENCE.md` (2026-08-22) and diverges from it by intent; there is
> deliberately no sync check between the two.
>
> | If you are changing… | Edit |
> |---|---|
> | Platform architecture — binds on all three agents | `../AGENTIC_ARCHITECTURE_REFERENCE.md` |
> | Agent Improve specifically | **this file** |
> | A rule quoted in implementation prompts | `CLAUDE.md` |
>
> **`CLAUDE.md`'s `§` citations point at the root reference, not at this file** — see `CLAUDE.md` §0.12.
> **Paths inside this document are written from the monorepo root.**
>
> **History moved out on 2026-09-25 (step 6.66)** — superseded text, dated incident narratives,
> completed-step prose, closed-gap discussion and the full changelog entries — is verbatim in
> [`docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md`](docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md),
> grouped by original section; each anchor `#L<n>` names the line the text started on.

---

## 🗺 Where state lives — a MAP, not a definition

**Four places, and this table is not one of them.** It holds no field list of
its own and never will: it says where each thing is defined and sends you
there. **If this section ever restates §57.2 or §58.2, it is wrong.**

| What | Defined in | Size | Holds |
|---|---|---|---|
| **`SupervisorState`** | **§57.2** (S-C01) | 7 fields | Orchestration. Spans the whole case, one per project |
| **`PhaseState`** | **§58.2** (S-C02) | 24 fields | One in-flight turn inside one phase subgraph |
| **Per-phase usage** | **§39.x.7** (S-C03) | — | Which `PhaseState` field carries what, per phase. **Reads and writes, NOT variant classes** |
| **Nothing else holds state** | — | — | Captured values go to `artifacts`; durable ones to the Store (§9); conversation to the checkpointer (§8) |

> **There are NO `{Phase}State` classes — ruled 2026-09-11, step 6.20.** They are
> not built and will not be; §39.x.7 describes per-phase USE of the shared
> `PhaseState`. S-C03 carries the ruling.

**Adding a field to either class is a §56 amendment**, and the test it must
pass is the one §5 already sets: **name the node that writes it and the node
that reads it.**

---

# Agentic Architecture Reference
**AgentLean Platform · the shared architecture for all three agents**
Version 1.84 · 2026-09-26
Status: **COMPLETE AND CROSS-CHECKED.** Parts I–XI and Appendices A–F written;
Task 3B verification pass completed 2026-08-21.

**Changelog (§56 step 1)** — one line per entry: version · date · what was ruled · where it lives now.
The full text of every entry through v1.77 is verbatim in
[`docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L112`](docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L112).

- v1.84 · 2026-09-26 · R7: Layer 2d for Define — `DEFINE_RUBRIC` (core/prompts.py), ONE criterion per element, Tier 1, pass/fail with a reason (the G-40 draft is archived); graded by `validation/rubric.grade_define`, deterministic half first, one `grader` call at 0.1 for judgment, a missing verdict failing closed; run by `validation_stack` after 2b, so a failing report never reaches the R6 pause. `CriterionVerdict` and `GraderVerdict` land in `validation/schemas.py` · §9.2, §9.7, §36
- v1.83 · 2026-09-26 · R6: the Define report is accepted through a graph-level pause — `gate_review` calls `interrupt()` once the gate has passed validation; `POST /gate` returns awaiting-acceptance and writes nothing; `POST /gate/decision` resumes with `Command(resume=...)` (approve: `gate_apply` assembles `final`, the route writes and advances, the Belt recorded as actor until R8; reject: the named elements re-open and the coach guides the Belt back in the same run). `AzureBlobCheckpointSaver.put_writes` persists pending writes — it was a no-op, which dropped the interrupt · §33, §49
- v1.82 · 2026-09-26 · R5: Define's gate is the DEFINE REPORT — seven sections assembled deterministically from confirmed values (`phases/define/report.define_report`), served as `GateReviewResponse.report` on `GET /gate/review` (Define only), drawn on the gate screen with the 5W2H and SIPOC diagrams; the v1-key Define gate document is retired from the screen · §49, §50
- v1.81 · 2026-09-26 · R6: every Define change is kept in phase state with its date — `field_log` already holds it (one entry per CONFIRMED change, timestamped, with the value it replaced, carried across turns by the case record); `substate.value_history` reads the first and the current confirmed value per field. No new state field · §10.1, §56 (2026-09-21)
- v1.80 · 2026-09-26 · R3 (docs/requirements/define.md): the validation layer every Belt answer passes before the coach model is the planner's one judgment, made against the element's ACCEPTANCE CRITERIA (`skills.acceptance_criteria`, from its SKILL.md block); `SufficiencyJudgment.failed_criterion` names the first one an insufficient answer fails, checked in code, and the challenge names it · §58 (S-C04)
- v1.79 · 2026-09-26 · Founder's Define requirements v2 (`docs/requirements/define.md`, R1–R7 — domain requirements live there, never here): Define has THIRTEEN elements — the benefits analysis at position 10 (R4); `critical_to_quality` captured inside position 3 and `problem_5w2h` inside position 4, as the registry is inside 5; `DefineOutput` 21 fields, 16 gate-required; every element's acceptance criteria are in its SKILL.md block · `phases/define/schema.py`, §39.1.9, §63.1
- v1.78 · 2026-09-25 · Founder ruling, the overnight run (step 6.66): documents hold current binding text only (REPLACE, DON'T APPEND; history to `docs/_archive/`; a size budget refuses growth); CLAUDE.md is rules and pointers; the 8D is asked only for a real defect (a fix, or a `Gap:` trailer); Define's plan is `docs/define_features.json`, status only from tests; the procedure is reference-only · CLAUDE.md §22 (a, h), rule 6 of the commit-msg guard
- v1.77 · 2026-09-25 · S-C04 takes step 6.61's shape: code builds `CoachingPlan` via `phases/moves.decide`; the planner's model makes one judgment · §58 (S-C04)
- v1.76 · 2026-09-25 · Record, step 10.0: §50.1's four coaching blocks and the grader's warning reach the Belt · §50.1, §19.8
- v1.75 · 2026-09-25 · The coaching move is decided in code from the field's status, never by the model — all phases, all agents · §43, §58 (S-C04)
- v1.74 · 2026-09-25 · Define's written step is the position AFTER the turn's capture, written on every turn · §39.1
- v1.73 · 2026-09-25 · Define's "Step n of 12" is computed from `DEFINE_FIELD_ORDER`, delivered and written — never counted by the model · §39.1
- v1.72 · 2026-09-24 · Layer 2a judges a reply against the script step it performs; every verdict recorded in `step_log` (G-96) · §34, §19
- v1.71 · 2026-09-24 · The current phase's full SKILL.md is delivered in the system message on every model call and recorded · §19.2, §32, S-C12
- v1.70 · 2026-09-23 · `fields_captured`'s description carries the declared shape of every structured coached field · §20, S-C05
- v1.69 · 2026-09-23 · Four Define-vertical corrections; §39.1.9 gains Define's `phase_metrics` entry, assembled in `gate_apply` · §39.1.9
- v1.68 · 2026-09-21 · `PhaseState` gains `field_log`; `artifacts` is seeded at phase entry rather than blanked · §6, §58.2 (S-C02)
- v1.67 · 2026-09-20 · Record: two of step 6.20's write paths land; §39.x.7's contracts confirmed unchanged · §39.x.7
- v1.66 · 2026-09-18 · Every section owns a register row or declares NOT-MARKABLE; v1.26's completeness claim corrected · §55.2
- v1.65 · 2026-09-18 · §26's hop cap goes five → three; G-83 closed · §26
- v1.64 · 2026-09-15 · S-C05's four presentational fields become optional (`default=""`); build status begins leaving this document · §20, S-C05, §55.2
- v1.63 · 2026-09-15 · Record: G-63's occurrence cause fixed (`_routed_column` returns `None`); its escape cause and step 6.21 stay open · §66 (G-63)
- v1.62 · 2026-09-14 · Record: step 6.19 closes G-50 (`CoachingResponse` gains its presentational fields); §39.1 gains six subsections · §20, §39.1
- v1.61 · 2026-09-14 · Record: G-60 gets step 6.29; G-62 registers a ruling on §56.3; the repository path lands in CLAUDE.md · §66, §56.3
- v1.60 · 2026-09-14 · Record: G-59, G-60, G-61 and the D7 coverage limit registered · §66
- v1.59 · 2026-09-14 · The commit gates govern; the thirteen rule files are advisory context · §55.5
- v1.58 · 2026-09-14 · The board's cause corrected (a ratified argument false on its face); G-58; the mutation-restore rule numbered · §55.2
- v1.57 · 2026-09-14 · A watched path must be a source of truth, never a generator's output; `docs/board.html` leaves rule 2b · §55.2
- v1.56 · 2026-09-14 · Record: `start.ps1` lost its path separators and never set its own directory · record only
- v1.55 · 2026-09-13 · Record, step 6.26: G-57 closed — the tree-guard rules are re-run by tests · §56.3
- v1.54 · 2026-09-13 · Record, step 6.25: scratch leaves the tree, sorted by content rather than folder · §56.3
- v1.53 · 2026-09-13 · CLAUDE.md §0.32: the tree at HEAD is the only source of truth; two of three clauses gated at the commit · §56.3
- v1.52 · 2026-09-13 · Record: the comment tail of v1.49's rename; nothing in this document changed · record only
- v1.51 · 2026-09-13 · G-54's corollary: introspection settles MEMBERSHIP, never ORDER or BEHAVIOUR · §19, verification log
- v1.50 · 2026-09-13 · Record: G-54 closed — every verification-log entry carries a `Source method` row · verification log
- v1.49 · 2026-09-13 · Record: G-52 closed — the middleware ordering is observed on a real graph · §19
- v1.48 · 2026-09-13 · The amendment procedure reconciled with the post-refactor topology · §56
- v1.47 · 2026-09-13 · Record: the ownership guard reads the dependency-versions row; G-56's Done-when passes · §55.4
- v1.46 · 2026-09-13 · Record: the seven skills exist; the root file loses two always-loaded references · §56.0.1
- v1.45 · 2026-09-13 · Record: §55.4 gains middleware order, coaching content and banned patterns as owned facts · §55.4
- v1.44 · 2026-09-13 · The ownership minimum ratified at two rows, encoded as data, enforced by two hooks · §55.4
- v1.43 · 2026-09-13 · The per-phase coaching scripts move to `skills/dmaic-{phase}-phase/coaching_script.md`; the byte check becomes file-to-file · §32, §39.x
- v1.42 · 2026-09-13 · Root CLAUDE.md rebuilt; the platform reference reclassified as a forward document; two open items become gaps · §66
- v1.41 · 2026-09-13 · CLAUDE.md §1–§15 become thirteen path-scoped files under `.claude/rules/` · §55.5, §56.0
- v1.40 · 2026-09-13 · §9's Azure AI Search ruling stands on two technical reasons, not three · §9
- v1.39 · 2026-09-12 · Record: two of CLAUDE.md §0's subsections are live rules, not change records · CLAUDE.md
- v1.38 · 2026-09-12 · The dependency upgrade is not a blocker; installed/latest tables replaced by floors plus `requirements.txt` · §1, §53
- v1.37 · 2026-09-12 · Record: CLAUDE.md §7.2/§7.3 brought into line with §23.2's evidence-index fields · §23.2
- v1.36 · 2026-09-12 · Record: G-54 registered — the verification log's source method · §66 (G-54)
- v1.35 · 2026-09-12 · §19's hook surface corrected: the six named lifecycle hooks are the complete set · §19
- v1.34 · 2026-09-12 · Record: the retired ordering sentence's two code sites corrected · §19
- v1.33 · 2026-09-12 · Record: CLAUDE.md §8.1 brought into line with §19's ordering rule · §19
- v1.32 · 2026-09-11 · §17: the executor dispatches the planner's named call; G-49 closed (option C) · §17
- v1.31 · 2026-09-11 · §55's mechanism table gains the commit-msg guard, and the guard gains rule 6 (the 8D) · §55
- v1.30 · 2026-09-11 · G-49 diagnosed: the planner's routing decision had no transport into the model's request · §17
- v1.29 · 2026-09-11 · A step's body heading carries no status token; title drift becomes a check · §55
- v1.28 · 2026-09-11 · §63 and §69's aliases checked; two of sixteen subsections were not covered · §55.3
- v1.27 · 2026-09-11 · §55.3 ratifies the phase completeness set · §55.3
- v1.26 · 2026-09-11 · Marker coverage claimed complete (claim corrected at step 6.40) · §55.2
- v1.25 · 2026-09-11 · BUILT markers added for MAIN's items and the five phases · §55.2
- v1.24 · 2026-09-11 · The `{Phase}State` variants ruled not built; the state map joins the head; Appendix D re-sequenced · state map, S-C03
- v1.23 · 2026-09-11 · Three-way alignment audit: four BUILT markers were wrong · §55.2
- v1.22 · 2026-09-10 · §19's ordering rule corrected; `ARCHITECTURE_STATUS.md` tables become BUILT markers and a check · §19, §55.2
- v1.21 · 2026-09-10 · `DECISIONS.md` Parts R–AU classified; four rules land here; that file archived · §56.2
- v1.20 · 2026-09-10 · The evidence channel's decisions land here; the version increments on every amendment · §23.2, §29, §56
- v1.19.2 · 2026-09-01 · G-21 closed: the `storage/blob.py` surface ratification recorded · §66
- v1.19.1 · 2026-09-01 · Docs consolidation: Appendix F merges the v2.2.16 registers · Appendix F
- v1.19 · 2026-08-27 · Control fully specified; the five-phase DMAIC specification is complete · §39.5
- v1.18 · 2026-08-27 · Improve fully specified; Define's §32 tool-block gap closed · §39.4
- v1.17 · 2026-08-27 · §39.2.10 and §39.3.10 carry their phase's coaching script · §39.x.10
- v1.16 · 2026-08-27 · Analyse fully specified; F-13 closed; the cross-phase reference gains `references_metric_name` · §39.3, §42
- v1.15 · 2026-08-26 · Measure naming convention, the structured metric registry, and Measure's full specification · §39.2
- v1.14 · 2026-08-26 · A project may track N measurement criteria at zero schema change · §39.2
- v1.13 · 2026-08-26 · Define's field #5 is `baseline_metric`; reverses v1.12's rename · §39.1
- v1.12 · 2026-08-26 · Define finalized at Option A: every Define field gate-required, no tier split · §39.1.2, §35
- v1.11 · 2026-08-26 · Define fully specified; G-38 closed for Define; `CoachingResponse` gains four presentational fields · §39.1, §20
- v1.10 · 2026-08-24 · G-01 and G-02 resolved; `PhaseState` gains `rejection_feedback` · §6, S-F13
- v1.9.1 · 2026-08-24 · S-F09's guard sample synced to the G-04 resolution · S-F09
- v1.9 · 2026-08-24 · G-04: `remaining_steps` declared as a LangGraph managed value · §6, §26
- v1.8 · 2026-08-24 · G-44 resolved; §16 gains the wrapper-invoke rule · §16
- v1.7.1 · 2026-08-24 · G-43 resolved as a false alarm · §66
- v1.7 · 2026-08-24 · G-03 and G-42 resolved; `case_id` and `current_phase` copied down into `PhaseState` at phase entry · §6
- v1.6.1 · 2026-08-24 · §55.1 rule 3 narrowed to peer runtime call edges · §55.1
- v1.6 · 2026-08-23 · The specification layer: Part XII (§57–§66) and Part XIII (§67–§68) · Parts XII–XIII
- v1.5 · 2026-08-22 · §15: `route_after_phase` deleted; phase transitions are static · §15
- v1.4 · 2026-08-22 · Contradiction detection moves to the coach via `contradiction_flag` · §19.6, §20, §37
- v1.2 · 2026-08-22 · Renamed from `AGENT_IMPROVE_BIBLE.md`; scope becomes the platform · About this document
- v1.1 · 2026-08-21 · §29.4: cross-agent tools ratified as present-but-not-bound · §29.4


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

> **Two things follow, and both bind.**
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
`agent-improve/docs/_archive/EDUCATIONAL.md` (the original chronological register),
`agent-improve/docs/_archive/REFACTORING_AGENT_IMPROVE.md` (the section-by-section
review), and `agent-improve/docs/REVIEW_DECISIONS.md` /
`agent-improve/docs/_archive/DECISIONS.md` (the decision log). Those remain the
historical record, and they live under `agent-improve/` because that is where
the work was done — not because their conclusions are Improve-specific. This
document states conclusions. (archived to docs/_archive/; canonical: REVIEW_DECISIONS.md)

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

> **NOT-MARKABLE:** a statement of purpose. **Nothing to anchor**: it says what Agent Improve IS, which no symbol in the tree can confirm or refute.

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

**The LangGraph floor is ≥1.2.6 and it is MET.** Step 2.3 upgraded the venv to
a `langgraph` above the floor (`requirements.txt` owns the pin), so per-node
`TimeoutPolicy`, `error_handler=` (Part IX) and
the subgraph `checkpoint_ns` fix (§16) are all available. **The floor is the
rule; the pin is not stated here.** `agent-improve/requirements.txt` carries the
resolved versions, and it is the only place that does — a version written into a
document is stale the day something upgrades.


**Graceful shutdown is a separate and weaker claim.** The mechanism named for
it, `RunControl.request_drain()`, is **UNCONFIRMED — MAY NOT EXIST** (§45). It
is not gated on the version upgrade; it is gated on the API being shown to
exist at all.

---

## 2. How to read this document

> **NOT-MARKABLE:** reading instructions.

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

> **NOT-MARKABLE:** terminology.

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

> **NOT-MARKABLE:** a summary of facts that own rows elsewhere. **It MENTIONS, it does not OWN** — every box in the diagram is specified somewhere that carries the row, and duplicating the claim here is how two copies drift.

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
        │  each phase subgraph — PhaseState (20 + 1 managed), no checkpointer
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

> **NOT-MARKABLE:** specified here, **marked at its canonical home §57.2 (S-C01)**, which carries the rebuild test. One marker per item, never one per section that mentions it.

*Supersedes: REFACTORING §17; ARCHITECTURE.md §4.1; DECISIONS §A1.*
**Status: RATIFIED.** File: `core/state.py`.

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

> **NOT-MARKABLE:** specified here, **marked at §58.2 (S-C02)**, which carries the rebuild test and the field census.

*Supersedes: REFACTORING §18; ARCHITECTURE.md §4.2; DECISIONS §A2.*
**Status: RATIFIED.** File: `core/substate.py`.

**Specification:** the canonical schema and its field table are **§58.2 — S-C02**.
This section keeps the reasoning.

**The field census is §58.2 (S-C02); the owner is `core/substate.py`.** The
engine-managed value is **declared but NOT populated by the input mapper**;
LangGraph's execution loop supplies it. **Any new field requires an amendment**,
whatever category it is placed in (§56).

### `asks` — §56 AMENDMENT, ratified 2026-09-09

**`asks` is the coach's recorded requests for data**, each carrying the expected
shape — columns, units, period — drawn from the SKILL.md worked examples the
coach already shows (§32, §43). Created during a coaching turn; read by the
upload route when a file arrives, by the planner when it routes, and by the
upload manifest. Built at step 6.12. `DECISIONS.md` Part AR.

**An ask is the logical identity of a document; files are its versions.** That is
ruling AP2.2, and this field is where the binding is recorded **when the coach
asks** rather than reconstructed afterwards from a filename — which the same
ruling forbids.

**`artifacts["asks"]` was considered and rejected, and §10.6's precedent is why
the question arose.** That precedent put `computation_results` inside `artifacts`
explicitly to avoid a new top-level field. It does not extend here, for three
reasons:

| | |
|---|---|
| **Whose record it is** | `artifacts` holds **the Belt's captured values**. An ask is a **system** record — the coach's own request. The precedent turns on that distinction, not on convenience |
| **What reads `artifacts`** | Gate assembly and `missing_gate_fields` both walk it. An `asks` key would appear in every gate document and would have to be excluded by name from the completeness computation |
| **§7's string law** | Every value in `artifacts` is a string, with **four** ratified exceptions. A structured `asks` list would need a **fifth** — so the "no amendment" route costs an amendment to §7 instead, and a weaker one, because it widens a typing law rather than declaring a field |

**`PhaseRecord.asks` in the case blob was also rejected, and §10 is the reason.**
The case record is *"written on case create, on gate pass, on file upload —
**never mid-conversation**"*, and §10's own subsection removes the v1 pattern of
writing it per turn. **An ask is born in a coaching turn**, and there is no
sanctioned write moment between that turn and the upload that answers it
moments later. Recording asks there would reinstate exactly the per-turn write
§10 deleted.

### `field_log` — §56 AMENDMENT, ratified 2026-09-21

**`field_log` is when each captured value changed, and what it was before.**
One entry per change — `field`, `value`, `prior_value`, `turn`, `timestamp`
and the Belt's stated `reason` where one was given — keyed `{phase}:{turn}:{field}`
per §11. **`reason` is declared and nothing populates it: G-89**, whose fix is
one clause on S-C05's `fields_captured` description and is owned by the
procedure amendment, not by the step that declared the column. **The first capture of a field is an entry too**, carrying no
`prior_value`. Built at step 6.33 alongside the capture path it logs.

**It is a THIRD thing and neither of the other two can answer for it.**

| | Holds | Cannot say |
|---|---|---|
| `artifacts` | WHAT is captured — the current value of each field | what the field said before, because the merge overwrote it |
| `step_log` | HOW a TURN went — one entry per node, per turn | which field moved, or from what to what; it never held the value |
| `field_log` | WHEN each value changed, from what, and why | — |

**For a quality system this is not bookkeeping.** §7's whole argument for
string-typed fields is that *"the Belt must be able to show what they stated,
not what the system parsed out of it"* — and a Belt who revised a baseline on
turn 9 after an upload contradicted their estimate can show the figure and not
the revision. The gate document records the last state of a value; this records
its history.

**The channel carries a reducer, and that is the declaration.** `merge_field_log`
is attached in `core/substate.py`, so a node that returns only this turn's
entries cannot replace the history — the same move `messages` and `step_log`
make with `operator.add`, and the opposite of `artifacts`, which merges in its
writer and depends on every writer remembering to. **A log is exactly the field
where "every writer must remember" fails**, because the writer that forgets
leaves no trace of what it dropped.

**The reducer is NOT `operator.add`, and §11 is the reason.** §11 requires a
deterministic key so that *"the replay overwrites its own earlier entry instead
of duplicating it"*. `operator.add` cannot honour that — it appends whatever it
is given, so a resumed or replayed turn logs the same change twice and the log
inflates on every retry until it stops being evidence. `merge_field_log` upserts
on the key. **§11 states that rule for `step_log` and `operator.add` does not
deliver it there; it is delivered here.**

**The turn number is counted in the conversation, not taken from `turn_count`.**
G-39 records that `turn_count`'s increment contract is unstated, and the
measured behaviour is worse than ambiguous: the input mapper seeds it to `0` on
every invoke and `core/graph.py` reads it as the ENTRY MODE, so it is `0` on
every coaching turn — which is why every `step_log` key of every turn reads
`{phase}:0:{node}`. A change log keyed on it would have each turn overwrite the
one before, **which is the defect step 6.33 exists to end, reproduced inside the
fix.** The Belt-message count is what accumulates across turns and is stable
under a replay, so it is what the key uses. **G-39 is not closed by this** — it
is routed around, and `turn_count` remains ambiguous for everything else.

**`artifacts["field_log"]` was considered and rejected, on §6's own `asks`
reasoning**: `artifacts` holds the Belt's captured values, gate assembly and
`missing_gate_fields` walk it, and a log key would appear in every gate document
and need excluding by name from the completeness computation. §7's string law
would need a fifth exception besides.

**It persists in `PhaseRecord.field_log` — the case blob — and NOT in the
Store's `case` record, which is where `asks` went for the same-shaped
question.** §6's `asks` ruling turns on who must read the thing BETWEEN turns:
an ask is answered by an upload arriving moments later on a route that cannot
see the checkpoint, and no case-blob write moment exists between them. A field
change has no such reader. It is written from the same turn's product, by the
same statement, as `structured` — and **a history persisted on a different
schedule from the value it is a history OF can disagree with it**, which reads
exactly like a change that never happened. It therefore inherits §10's open
per-turn-write violation rather than adding one, and moves with `structured`
when step 10.2 removes it.

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

**there are no per-phase state classes** (ruling 2026-09-11, step 6.20); each phase uses the shared `PhaseState` and §39.x.7 describes its
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
| `post_improvement_metrics` | Control | Result → Measure baseline |

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
**Validation stack Layer 2d** answers "was a hypothesis test run?" by scanning
that list for `"tool": "t_test"` — **§62.9 B3: *"scan `artifacts["computation_results"]`
for the relevant tool entry rather than asking the model."***

> **The scan is Layer 2d's, not the grader's (§36).** `DMAICGraderMiddleware`
> (§19.8) judges coaching process quality on every turn; Layer 2d judges gate
> content once, at the gate, deterministically, by reading this list.
> Adding typed per-phase computation fields is a violation:
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

> **`BaseStore.search()`'s real surface, read from the installed package.**
> Six parameters, and that is all there is:
>
> ```python
> >>> import inspect
> >>> from langgraph.store.base import BaseStore
> >>> [p for p in inspect.signature(BaseStore.search).parameters if p != "self"]
> ['namespace_prefix', 'query', 'filter', 'limit', 'offset', 'refresh_ttl']
> ```
>
> Introspected against `langgraph` 1.2.11 on 2026-09-12. Checked past the base
> class, because a concrete store could have widened it and none does:
> `InMemoryStore.search` and `.asearch` carry the identical six, `SearchOp`
> declares the same six, `IndexConfig` exposes only `dims`, `embed`, `fields`,
> and **the string `hybrid` does not occur anywhere in the installed package.**
>
> **TWO of the three reasons for keeping `improve_case_index` on Azure AI
> Search stand; one is genuinely conceded.** The old argument was that the
> Store provides neither metadata filtering, nor hybrid BM25 + vector scoring,
> nor multi-query + RRF.
>
> | Reason | Status |
> |---|---|
> | Metadata filtering | **CONCEDED** — `filter=` exists and does the job |
> | Hybrid BM25 + vector scoring | **STANDS** — there is no `mode` parameter, on any store, at any version installed here |
> | Multi-query + RRF | **STANDS** — §25, the mechanism Agent Resolve production experience showed this corpus needs |
>
> **The decision rests on two technical reasons plus migration cost.**
> Re-examine if the Store's search surface grows — but note that it has not
> grown in the direction this section once recorded, and the thing to re-run is
> the introspection above, not a documentation page.


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

> **AND `step_log`'s OWN REDUCER DOES NOT DELIVER IT.** The key above is
> deterministic; the channel reduces with `operator.add`, which appends. So a
> replayed turn writes its entries a second time under the same keys, and the
> idempotence this subsection requires is available to a reader who de-duplicates
> and to nobody else. **`field_log` (§6, step 6.33) is the first channel where
> the key is enforced by the reducer** — `merge_field_log` upserts on it, so a
> re-run of a turn replaces its own entry. Recorded here because the rule lives
> here: closing the gap for `step_log` is not step 6.33's, and the two channels
> must not be assumed to behave alike because they share this paragraph.

---

# Part III — The Graph

*The graph is the orchestrator. Nothing outside it dispatches work.*

---

## 12. Topology

> **NOT-MARKABLE:** topology overview. **The buildable claim is §15's**, which marks the supervisor graph and the fact that it is not yet the runtime.

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
   START
     │
     ▼
  ┌──────────────────────────────────┐          ┌────────────────┐
  │            planner               │─────────▶│    executor    │
  │  reads artifacts; produces the   │  Command │  create_agent  │
  │  CoachingPlan; owns the ONLY     │  (goto=  │  ReAct, ≤3 hops│
  │  field / gate routing decision   │ executor)│  RemainingSteps│
  │                                  │          │  7 universal + │
  │   · field incomplete → executor  │◀─────────│  phase comp.   │
  │   · more fields      → executor  │  plain   │                │
  │     (field_index++)              │  return  │  decides NO    │
  │   · all captured     → val. stack│  §17     │  strategy — §17│
  └────────────────┬─────────────────┘          └────────────────┘
                   │
       Command(goto="validation_stack") — §15 · S-F13 DP1
                   │
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
  │                     │ Command(resume=…)
  │                     ▼
  │            ┌──────────────────┐
  │            │   gate_apply     │
  │            │ · apply edits    │
  │            │ · policy advisory│
  │            │ · assemble doc   │
  │            │ · store.put()    │
  │            │ · final = doc    │
  │            └───┬──────────┬───┘
  │        reject  │          │  approve
  ├────────────────┘          ▼
  │                          END   (parent's static edge advances the phase)
  │
  └──▶ back to planner — TWO Command returns, both carrying feedback:
          validation fail → validator_feedback   (§34, shared cap 3)
          Belt reject     → rejection_feedback   (§33, G-02)

   Routing summary — who returns a Command, and who does not
     · planner          Command(goto="executor" | "validation_stack").
                        The single field / gate decision point — S-F13 DP1
     · executor         plain return to the planner. Emits NO routing
                        Command; it decides no strategy (§17)
     · validation_stack Command: pass → gate_review · fail → planner
                        · gate_attempts ≥ 3 → escalation (§38)
     · gate_apply       Command: approve → END · reject → planner
     · static edges     START → planner, and the parent's phase edges.
                        Nothing else. A node never mixes a Command with a
                        static edge — both paths execute, silently (§15 C2)
```

### The subgraph is a cycle, not a pipeline

**The planner fires many times per phase, not once.** After each executor step,
control returns to the planner to decide whether to keep coaching the current
field, advance to the next, or trigger the gate. That cycle is why LangGraph
rather than a DAG engine is the runtime — a DAG cannot express "go back and try
this field again with what you just learned."

**The planner is the single field/gate decision point, and the executor returns
plainly.** The executor reads `coaching_plan`, coaches, and hands control back
without choosing where control goes — it decides no strategy, which is the whole
content of the Planner/Executor split (§17). The planner then inspects
`artifacts` and returns `Command(goto="executor")` to keep coaching or
`Command(goto="validation_stack")` once every field is captured (S-F13 DP1).
**Putting that decision in the executor would fuse the two roles** while leaving
the node names intact — the failure §17 exists to prevent, and the harder one to
see because the diagram would still show two boxes.

**The cycle is built from `Command` routing, not from conditional edges.** The
target is part of the node's own return value; there is no anonymous edge
function deciding for it (§15). That distinction is load-bearing rather than
terminological: **a node may not mix a `Command` with a static edge, because
both paths would execute, silently** (§15 C2). The only static edges in a phase
are `START → planner` and the parent's phase-to-phase edges.

**Control returns to the planner from two places downstream, and both carry
feedback.** The validation stack returns `validator_feedback` on a failed
attempt (§34, shared cap of 3); `gate_apply` returns `rejection_feedback` when
the Belt rejects (§33). They are drawn as parallel loops because they *are*
parallel — the two ways a phase re-enters coaching after having left it.

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

The universal eight (§29) and the phase's computation tools are passed to the
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

> **`route_after_phase` is deleted and must not be reinstated** — the supervisor
> owns no retry or escalation (DECISIONS §R2).

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

### The wrapper node must invoke the subgraph directly (G-44)

Each phase runs inside the parent's uniquely-named node function, which calls
`input_mapper` → `await subgraph.ainvoke(child_state)` → `output_mapper`
(§58.19, the different-schemas mapping pattern). That inner invoke persists
`PhaseState` across Belt turns **only because it is called directly inside a
node function**: LangGraph statically discovers a subgraph invoked inside a
node and routes its checkpoint writes through the parent's saver under an
auto-managed `checkpoint_ns`, carried by the inherited runtime config
(`thread_id` = `case_id`).

Two constraints bind, and both are load-bearing:
- The wrapper SHALL call `await subgraph.ainvoke(child_state)` directly and
  SHALL NOT pass a fresh `config` — the inherited config carries `thread_id`
  and `checkpoint_ns` down.
- The invoke SHALL NOT be relocated inside a tool function or any other
  indirection. LangGraph does not namespace a subgraph invoked inside a tool
  (the subagents pattern); persistence silently breaks there. This is the one
  constraint G-32 must respect if `request_human_approval` ever wraps an invoke.

Verified against current LangChain subgraph documentation, 2026-08-24: a
subgraph invoked inside a node is discoverable and its state persists; invoked
inside a tool it is not. **Still owed:** a local repro against the pinned
LangGraph (parent node calls `subgraph.ainvoke`; assert
`get_state(subgraphs=True)` shows the child checkpoint under a non-empty
`checkpoint_ns`) — documented, not yet demonstrated.

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

Which one you get depends on configuration. Neither reliably yields the cap, and
both terminate the graph with `GraphRecursionError` rather than letting the
coach close out gracefully.

---

# Part IV — The Coaching Agent

*Everything in this Part runs inside one node — the `executor` of §13.*

---

## 17. The Planner / Executor contract

*Supersedes: REFACTORING §5, §11, §20; ARCHITECTURE.md §3.5; CLAUDE.md §1.3.*
**Status: RATIFIED.**

> **v1.75 — THE COACHING MOVE IS DECIDED IN CODE (founder, 2026-09-25; all
> phases, all agents).** The move for this turn is no longer the planner
> model's choice and never the coach's: **code** derives it from the field's
> status — not yet taught → **teach** (explain, show, ask); answered and judged
> insufficient → **challenge** (say what is missing); answered and judged
> sufficient → **read back** (the Belt's own words, then *"is this right?"*);
> confirmed by the Belt → **store and advance**. **The planner's LLM call is
> reduced to ONE judgment — is this answer sufficient, with a reason**; the coach
> model writes the words for the move code chose. Built at step 6.61.

> **Since step 6.21 the planner's routing decision is executed rather than
> suggested**: where the plan routes to an unread upload, `executor()` calls
> `load_evidence_series` on that blob path itself and puts the result in front
> of the coach as a tool exchange. The model is not asked. Everything else it
> calls remains its own choice, and §24's *"no unconditional retrieval
> pipeline"* is untouched. **Still owed:** the `live-run` halves of 6.7, 6.12
> and 6.13.

> **v1.77 — HOW THE MOVE RUNS (step 6.61).** Relocated here from the v1.77
> changelog entry, whose full text is archived (`#L112`).
>
> - **Status lives in `PhaseState.field_status`** (ruling R5): not taught →
>   asked → answered (the Belt's words held PENDING) → confirmed (stored). Only
>   code changes a status, and only at turn end; the current field is the first
>   not confirmed.
> - **Confirmation is a rule, not a model** (`moves.is_confirmation`): a plain
>   yes stores the pending value; anything more is a correction and returns the
>   field to answered.
> - **What a yes stores:** a plain-string answer given in one message stores the
>   Belt's own words; a structured field, a composed one (`problem_statement`)
>   and an answer assembled from more than one message store the version read
>   back. A yes that cannot complete the position is read back again, never
>   advanced past.
> - **Confirm and Change (ruling R4):** every read-back shows two buttons;
>   `AskRequest.action` (`confirm` | `change`) sets the status in code whatever
>   the text says. Change returns the field to asked with the Belt's words kept,
>   and its reply is written in code, with no model call — the Belt's exact
>   current words, then "What would you like to change?".
> - **The grader grades the move:** `middleware/grader.MOVE_EXCLUDES` names, per
>   move, the rubric lines that move does not answer; section 5 carries only the
>   failures that apply to this turn's move.
> - **Sections 2 and 6:** section 2 is the script's opening (first turn only)
>   plus the CURRENT field's block; section 6 is one entry per coach turn, its
>   reply text.
> - **The fallback is containment:** a timeout or the runaway backstop gives the
>   Belt the move's script question in code, logged at ERROR as a DEFECT and
>   flagged `fallback` on the move record.
> - The move record rides on the reply as `additional_kwargs["coaching_move"]`,
>   beside `"quality_feedback"`; `core/conversation.py` round-trips both. S-C11
>   B2's facts-at-the-top order is superseded by v1.75's six sections; B2's
>   channel rule (never `messages[]`) stands.
> - **Open — G-110:** a CONFIRMED field has no move that revises it. **Open —
>   G-111:** `retrieval_strategy` is the phase default and `retrieval_hops` stays
>   empty, so §26's model-planned hop chain has no author until a step gives it
>   one.

Each phase subgraph contains a **Planner-Executor pair**, not a single coaching
node.

| | `phase_planner` | `phase_executor` |
|---|---|---|
| Produces | A structured `CoachingPlan` | The coaching response + extraction |
| Decides | **Strategy** — which field, which action, which retrieval mode | **Nothing about strategy** |
| Dispatches | **Never** dispatches to tools | Dispatches to leaf tools via the tool-calling loop — **and, since step 6.21, executes the planner's own named call**: when the plan routes to an unread upload the NODE calls `load_evidence_series` on that blob path before the model runs, so the model is never offered that decision. Scoped to that one case; every other tool stays model-chosen |
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

> **SPEC-GAP (G-48): the builder-style call above is permitted here and blocked
> in `backend/upload/**`, and the two calls are the same shape.** §4.6 scopes
> this form to a plain model invocation inside a tool, middleware or validator,
> plus this planner — and `deprecated_patterns.yaml`'s `pattern-2` excludes
> exactly those paths by name. **The upload interpretation (§29.1, step 6.11) is
> also a plain model invocation for a typed result**, with no agent and no
> model-tools loop for `response_format=` to attach to, and it is on none of the
> listed paths, so the hook blocks it and the call parses JSON by hand instead.
> **That is not a style difference and it has already cost a defect** — a schema
> binding cannot drift out of contract with its own parser, a hand-written one
> can, and did (Part AP6). **Registered rather than fixed**: §8 forbids amending
> a rule in passing during a feature change, and the ruling waits on what
> `9fce8fc` recorded when it scoped `pattern-2`.

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

> **NOT-MARKABLE:** a parent whose CHILDREN own the facts. §16's convention — *“one marker per item, never one per section that mentions it”* — and a row here would be a second claim over the same ground. Eight of its nine children own rows.

*Supersedes: REFACTORING §80, §84; ARCHITECTURE.md §3.4; DECISIONS §B3, §M2, §M3.*
**Status: RATIFIED.** **This is the canonical definition. Everything else cross-references it.**

**Specification:** the five custom middlewares are **§61 — S-C10 to S-C15**. The stack, its
order and its ordering rules stay here; the three core middlewares are used
as shipped and keep their configuration in §19.3–§19.5.

**Five custom, three core.** All are built on `AgentMiddleware` hooks.

**The six are the complete set.** `AgentMiddleware`'s lifecycle hooks are
`before_agent`, `before_model`, `after_model`, `after_agent`, `wrap_model_call`
and `wrap_tool_call` — each with an `a`-prefixed async twin, twelve methods for
six hooks. A middleware extending this stack has these and no others.


**Prefer built-in middleware wherever it exists.** Custom middleware is
reserved for genuinely domain-specific logic.

### Ordering rules that bind


**THE DECLARED LIST IS NESTING ORDER, OUTERMOST-FIRST. THE POSITION NUMBERS ARE
EXECUTION ORDER. For `after_*` hooks the two are OPPOSITE.**

| Hook kind | Fires | Relative to the list |
|---|---|---|
| `before_*` | on the way **in** | outermost-first — **same** as declaration order |
| `after_*` | on the way **out** | innermost-first — **the reverse** of declaration order |
| `wrap_*` | around the call it wraps | an earlier declaration **encloses** a later one |

Measured, not inferred:

```
declared:      1st, 2nd, 3rd
before_agent:  1st, 2nd, 3rd      <- outermost first, going in
after_agent:   3rd, 2nd, 1st      <- innermost first, coming out
```

1. **`BeforeModelStateInjection` MUST be first.** Project facts have to reach
   the top of the prompt before skills loading and summarisation shape it.
   Declared first means **outermost**, so this is also the rule that makes its
   `wrap_model_call` enclose position 4's retry — the project-state block is
   composed and prepended **once**, and a retry re-sends the built request
   rather than rebuilding it per attempt. Pinned by
   `test_position_1_wrap_encloses_position_4_retry`.
2. **Positions 6, 7 and 8 all fire `after_agent`, so they EXECUTE in the
   reverse of how they are declared.** They are **declared grader, coherence,
   contradiction** and therefore **execute contradiction, coherence, grader** —
   which is what the position numbers 6, 7, 8 mean. Pinned by
   `test_the_declared_middleware_list_is_the_ratified_layering`, which asserts what
   executes rather than what is listed.
   - **Grader outermost** — a final quality verdict should be the last thing to
     touch the answer on its way out.
   - **Contradiction innermost** — it should be first to see the coach's raw
     output, and able to interrupt before anything else spends effort on it.
   - **Coherence between them**, so it can stand the grader down.
3. **Position 5 (`wrap_tool_call`) is independent**: a failed retrieval is not
   a failed model call, and `ModelRetryMiddleware` never sees it (§19.5).
   Position 1 also wraps the model call and encloses position 4 — rule 1.
4. **If `CoherenceMiddleware` exhausts its retries, `DMAICGraderMiddleware` is
   skipped for that turn** — deliberately. Grading a response already known to
   be incoherent spends a model call to produce a meaningless score. **This is
   why coherence must sit inside the grader**: the skip travels outward on the
   way out, which only works if the grader has not run yet.

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


> **v1.75 — THE COACH'S INPUT IS LABELLED SECTIONS, ONE JOB EACH (founder,
> 2026-09-25).** Assembled by code every turn, in this order: **coaching rules**
> (how to behave) · **phase script** (what to teach) · **state** (facts) · **this
> turn's move** (authoritative — the section says so) · **last turn's quality
> feedback** · **the conversation**. Delivered through this middleware's existing
> `wrap_model_call` — no new model call. **Feedback to the coach is never
> presented as a message from the Belt.** Built at step 6.61.

**Custom · `before_agent` + `wrap_model_call` · position 1.** Prepends structured project state at
the **top** of the prompt, ahead of the conversation: this phase's `artifacts`,
prior phases' gate documents from the Store, current phase requirements, and
the missing fields reported by `check_gate_status()`.

**The COMPOSING hook is `before_agent`, not `before_model`.** State injection
belongs at agent-loop start, once per turn. `before_model` fires before every
individual model call within a turn, which would re-compose the same project
facts repeatedly and waste context.

**Two hooks, and the division of labour is the design.** `before_agent`
composes the block once; `wrap_model_call` prepends the composed block to each
request and recomputes nothing — *"a pure read of what `before_agent` composed,
or the once-per-turn guarantee would be decorative"*. Both are defined on this
class rather than inherited, which is why the header names both: checked by
`'wrap_model_call' in vars(BeforeModelStateInjection)`, which is `True`.

**Missing fields are computed at injection time, never read from a stored
list.** The middleware derives them the same way the gate does, so the prompt
and `DMAICGateValidator` cannot disagree.

**For Define the block opens with the Belt's step, computed (v1.73).**
*WHERE THE BELT IS — Define · Step n of 13 — <field>*, from `define_progress`,
above everything else; the missing-field list is headed as **the gate list**
(*n of 16 gate fields; not the step count*). The executor writes the same
label into the reply's `progress`; the coach never counts it.

**Why the top of the prompt.** Models weight earlier content more heavily.
Injecting project facts *after* the Belt's message lets the response drift
toward the Belt's framing rather than the project's established state.
**Injecting in `messages[]` append order is a violation** — there is no "just
add it to the history" option.

### 19.2 `DMAICSkillsMiddleware` — progressive disclosure


**Custom · `before_agent` + `wrap_model_call` + a registered tool · position 2.** Full treatment in
§32; the stack-level facts are:

| Level | When | What loads |
|---|---|---|
| 1 | Startup | Skill descriptions only — **under 2K tokens for all five combined** |
| 2 | **Every model call**, for the phase being coached (v1.71) | That phase's full SKILL.md, in the system message; version and hash recorded in `step_log` |
| 3 | On demand | Reference files, when explicitly needed |

**For the phase being coached, level 2 is placed in the system message on every model call by `DMAICSkillsMiddleware`, and each turn records the script's version and hash in `step_log` (v1.71).** `load_skill(name)` stays registered for other phases' scripts and level-3 references, but the current phase's script is never left to the coach's choice. **Rule: any content the product depends on is delivered and recorded, never left for the model to fetch.**
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

**The parameter is `max_retries`, not `retries`** — `retries=` does not exist
and would raise at construction. The two retry middlewares share the same
parameter vocabulary.

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

**Parroting is judged against the script step the reply performs (v1.72,
G-96).** The judge is told the step — ④ **Confirm** for a field the reply
captured, ①–③ Explain, Show and Ask for the focus field otherwise — with that
field's block from the phase's SKILL.md, and it reads the whole reply,
`prompt` included. **Reading the Belt's words back to confirm them is allowed;
parroting is a restatement with no confirmation question and nothing added.**
Every verdict — a rejection with its reason — is recorded in `step_log`
(node `coherence`), so a turn the grader stood down on says why.

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

> **STATUS, 2026-09-24 — step 6.52 B2. What is built, recorded so §19.7 and
> §19.8 are not silently false; the rule change is a DRAFTED amendment in that
> commit's body, not applied.** Coherence and the grader each make **one call
> per reply**. Their "retries" re-sent the SAME text to a temperature-0.1 judge
> — no rewrite happened between them (trace `01a0d215…`: three grader calls,
> identical inputs). Until step 6.53 asks the coach to rewrite on a FAIL (gated
> on G-83), coherence rejects once and degrades the turn, and the grader grades
> once and passes a FAIL through with its warning. `max_iterations=3` and the
> two coherence retries are held for 6.53. **Each grading now reaches
> `step_log`** (`layer: "coaching_grader"`), as §19.8 says it does.

### 19.9 Middleware deliberately NOT used

> **NOT-MARKABLE:** a deliberate absence — what was considered and rejected. **A middleware that is not used has nothing to build**, and recording the decision is the point of the section.

| Middleware | Why not |
|---|---|
| `HumanInTheLoopMiddleware` | **Two confirmed bugs hit our exact use case.** Edited tool-call args can be silently re-overwritten by the agent re-attempting the original call; and edit/reject are broken in subgraph contexts, where only approve is reliable. Both would silently discard a Belt's correction. Use graph-level `interrupt()` (§33) |
| `LLMToolSelectorMiddleware` | Per-phase binding (§30) already keeps every coach at 8–15 tools. A selector LLM spends a model call solving a problem already solved structurally |
| deepagents `RubricMiddleware` / `SkillsMiddleware` | Pre-1.0 dependency (§18) |

---

## 20. `CoachingResponse` — the per-turn schema

> **NOT-MARKABLE:** specified here, **marked at §58.5 (S-C05)** — which records that `CoachingResponse` is built at four of its eight fields (G-50).

*Supersedes: REFACTORING §82; ARCHITECTURE.md §4.10; CLAUDE.md §10.7; DECISIONS §B4.*
**Status: RATIFIED.**

> **v1.75 — A VALUE IS STORED ONLY AFTER THE BELT CONFIRMS IT (founder,
> 2026-09-25).** What the coach returns in `fields_captured` is **pending** until
> the Belt confirms the read-back; the stored value is **the Belt's own words**,
> or a tidied version proposed in the read-back **and confirmed by the Belt**.
> The capture contract (`CAPTURE_CONTRACT`, S-C05's `fields_captured`, the Define
> script's *"Capture each confirmed value"*) moves under this rule at step 6.61.

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

**It gained four presentational fields on 2026-08-25** — `explanation`,
`example`, `prompt`, `progress` — under that procedure, so that §50.1's
response structure is **carried by the schema rather than hoped for from the
prompt.** `message` is retained as the transcript entry appended to `messages`;
the four are the render contract. **This is a five-phase change**, not a Define
one: every phase's coach output uses this schema.

**Structured output guarantees the flag's shape and its presence — never the
correctness of the coach's judgment in setting it.** A schema-valid
`contradiction_flag` describing a contradiction that is not one is exactly as
well-formed as a correct one. This is the same limit stated below for captured
values, and it is why §50's all-gate-fields tab is the documented human
backstop rather than a convenience.

**`value` is `Any`, not `str`, and that is deliberate.** It must carry both
plain string fields and the three cross-phase reference dicts (§7). Typing it
`str` would make `causal_hypothesis`, `solution_linked_to_root_cause` and
`post_improvement_metrics` uncapturable. **This is the one place `Any` is
correct**; the values *inside* those dicts are still strings.

### The executor node writes the response into state

**Specification:** the write-into-state behaviour is **§57.3 — S-F04**.

### The executor's `response_format` is `CoachingResponse`, never a phase Output

**The executor runs once per coaching turn; the gate document is assembled once
per phase.** Asking the coach to emit a complete `DefineOutput` every turn
requests fields it has not yet coached — the model then either refuses or
invents them, and the second failure mode is worse. See §40.

### What structured output does NOT give you

**Truth.** It guarantees shape. A schema-valid `baseline_estimate: 4.2` invented
by the model is exactly as well-formed as a correct one. Content-level defence
is the anti-hallucination guards (§22), validation Layer 2a (§34) and the
policy advisory (§33) — **not this mechanism.** No reader should come away
believing structured output is a defence against hallucinated content.

---

## 21. LLM roles, temperature, and the factory


*Supersedes: REFACTORING §34-D, §42; ARCHITECTURE.md §3.3; CLAUDE.md §4.1, §4.2, §4.7.*
**Status: RATIFIED.** File: `core/llm.py`.

> **THE FACTORY PASSES `max_retries=0`, EXPLICITLY, AND THE ZERO IS THE RULE**
> (ruling AI1, step 6.4; landed here 2026-09-10). **Retry belongs to the
> middleware and to nothing else.** `ModelRetryMiddleware` owns transient API
> failures (§19.4, cap 2) and `CoherenceMiddleware` owns response-quality
> failures (§19.7, cap 2); a factory that also retried would multiply against
> both, turning a documented cap of 2 into an undocumented 6 that no §34 counter
> can see.
>
> **It is written as an explicit `0`, never omitted.** The SDK default is
> non-zero, so leaving the parameter out yields silent retries that look like
> latency. **The trade is deliberate**: the SDK's `Retry-After` awareness goes
> with it, and the middleware's exponential backoff with jitter replaces it — a
> slightly worse backoff in exchange for one countable retry path.

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

> **v1.75 (founder, 2026-09-25):** the coaching rules say **how to behave** and
> contain **no move-sequencing** — no *"one move, then stop"*, no *"confirm and
> advance"*. The move is decided in code (§17) and delivered as its own section
> (§19.1).

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
**Canonical home for all index schemas.**

Three Azure AI Search indexes, one per retrieval tool. **Each tool is bound to
exactly one index and knows that index's field names locally** — there is no
shared retriever, which is what keeps the differences between them from hiding
in shared code.

### 23.1 `improve_knowledge_index` — methodology

LSS Black Belt eBook content. Static, identical for every project and every
Belt, never updated at runtime.

**The live index is `improve_knowledge_index_v3` as of 2026-08-25.** The
`AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX` environment variable is what binds it,
and `improve_knowledge_index` — the superseded index — is retained intact as
the rollback target. The schema below is identical across both; only the
corpus and its `phase_relevance` tags changed.

**The corpus is the BB eBook alone — 1,184 documents.** `problem_solving_8D`
(169 documents) and `LSS_tools_suite` (75) were removed: 8D is Agent Resolve's
methodology and was retrievable during DMAIC coaching, and the tool sheets were
thin duplicates of eBook content whose example-number rows acted as retrieval
attractors. One tier-1 methodology voice, because the MEMORY HIERARCHY
arbitrates *between* tiers and cannot arbitrate within one.

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

**259 of 1,184 documents carry `'general'`. Zero carry `'all'`.** **The silent
failure is the dangerous one**, and it is why this value is stated here rather
than left to be confirmed at implementation time.


**`phase_relevance` is assigned by an LLM call per chunk, not by keyword
counting.** The keyword scorer it replaced classified on vocabulary rather than
subject — it tagged the Control-phase wrap-up page `improve` because that page
lists "Improvement Selected / Develop Training Plan", and tagged the
introduction to hypothesis testing `measure` because the passage is dense with
measurement words while teaching an Analyse technique. The two classifiers
agree on 52% of chunks. `ingest_knowledge.py` owns this.

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
| `phase` | String | **APPLIED 2026-09-10, step 6.13.** Optional filter, default OFF |
| `uploaded_at` | String | **APPLIED 2026-09-10, step 6.13.** Order by, ISO 8601 |
| `role` | String | **APPLIED 2026-09-10, step 6.13.** **Filter + searchable.** The document's function in the project. With `case_id` this is the document's **logical identity**. Drawn from the ratified vocabulary at §23.2.1 |
| `kind` | String | **APPLIED 2026-09-10, step 6.13.** **Filter.** `evidence` or `artefact`. **Derived from `role`, never declared separately.** Retrieval filters to `evidence` by default |
| `description` | String | **APPLIED 2026-09-10, step 6.13.** **Searchable + retrievable.** The interpretation's summary — a **projection** of `UploadRecord.summary`, written once at index time |
| `content_digest` | String | **APPLIED 2026-09-10, step 6.13.** **Filter.** SHA-256 of the uploaded bytes. **Version identity** — the same bytes re-uploaded are not a new version |
| `shape_match` | String | **APPLIED 2026-09-10, step 6.13.** **Filter.** `full`, `partial`, `none` or `unsolicited` — whether the file matched the ask's expected shape. Paired with `missing_columns` in `metadata` |

**All twelve fields are live** (step 6.13). **Zero is what a filter on a
metadata-buried value returns**, so the count is the check, not the presence of
the field (§23.4).

**All seven ratified-not-yet-applied fields are server-set.** `phase` from
`state["current_phase"]` at upload, `uploaded_at` from the server clock, `role`
from the ask when the upload was solicited and from the Belt's declared purpose
when it was not, `kind` from `role`, `description` from the interpretation,
`content_digest` from the bytes, `shape_match` from the check against the ask.
**A Belt-entered value for any of them makes it unreliable as a filter or a sort
key**, which is the rule this section already applied to the first two.

**`description` is a PROJECTION and is declared as one.** The system of record
for the summary is the case blob (§10). The index copy exists because it must be
*searchable*, which the blob cannot serve. **A change to the summary requires
re-indexing that document — never an in-place edit of the index copy.** This
follows `phase_summary_{phase}` in `improve_case_index` (§23.3).

**The structural profile is deliberately NOT indexed.** Columns, types, ranges
and row count stay on `UploadRecord` in the case blob. Copying them into the
index would create a second source of truth for one fact — the drift §39.2's
single-authority rule exists to prevent — and would repeat per chunk. **The
index carries the pointer; the blob carries the data.**

#### Supersession deletes; it does not flag

**When a document is superseded, its chunks are DELETED from the index.** The
index holds only current versions and needs no `is_current` flag. History is not
lost: the case blob is the system of record (§10) and retains every version,
which is where a superseded file belongs.

An `is_current` boolean was drafted and dropped. **The reason is a use-case
count, not a cost.** Of four moments that could need it — a Belt asking for
their current data, §37's cascade reopening a gate, a gate document citing its
source, and a Belt asking what the earlier version said — **only the last needs
the flag**, and surfacing superseded evidence to a coach is arguably wrong
behaviour rather than a feature. *(An earlier argument that the write path
offers no partial update was withdrawn as false — `DECISIONS.md` Part AQ.)*

Two consequences bind:

- **Supersession is scoped to `(case_id, role)`.** A Control-phase measurement
  does not supersede the Measure baseline, because they are different roles.
  Only a correction of the same document supersedes.
- **Citations anchor on `blob_path` + `content_digest`, never on the index id.**
  An index id disappears when its document is superseded, and a gate document
  citing one would break. This is what lets §37 / step 7.6's cascade detect that
  an approved gate rested on a file that has since changed (§6, S-C02).

#### Two Azure behaviours govern the migration

*Verified against Microsoft Learn, "Update or rebuild an index in Azure AI
Search", 2026-09-09.*

**1 — All seven additions are ADDITIVE, so no drop-and-rebuild is required.**
"Add a new field" is on that page's *updates with no rebuild* list, and
**"when you update an index schema to include a new field, existing documents in
the index are given a null value for that field."** Only changing an EXISTING
field forces a rebuild — a rename, a data-type change, or a change to
`searchable` / `filterable` / `sortable` / `facetable`. **Nothing here changes an
existing field**, so the schema add is cheap and reversible in a way the original
"batched reindex" framing assumed it was not.

**2 — `mergeOrUpload` DROPS `content_vector` when that field is declared
`stored: false`, and reports success.** The same page: *"A side effect of setting
`stored` to false is that vectors are dropped on a reindexing operation.
Providing the vector in the documents payload prevents this from happening."*
**A write that succeeds and silently destroys retrievability is a §23.4-class
trap** — the same shape as the `fields=` failure below, and it belongs recorded
beside it.

**The rule is CONDITIONAL ON THE DECLARATION, and on this index the trap is not
armed.** Measured against the live index on **2026-09-09**:

| | `improve_evidence_index.content_vector` |
|---|---|
| `stored` | **`true`** |
| `retrievable` | **`false`** |
| dimensions · profile | 3072 · `default` |

**Under `stored: true` a partial update may omit the vector safely — and it
should.** The field is **not retrievable**, so a writer cannot read the existing
vector back to carry it; supplying it would mean **re-embedding every document
touched**. Mandating that unconditionally would impose exactly the cost
`stored: true` exists to avoid, on a backfill whose whole point is that it does
not need to re-embed.

> **If `stored` is ever declared `false` on this index, every partial write path
> must be revisited BEFORE that change lands.** `stored` is a field attribute, so
> it can only change at a rebuild (behaviour 1 above) and cannot drift silently.
> **But a 3072-dimension vector is exactly where someone reaches for that
> optimisation**, and taking it at a rebuild would arm this trap for every later
> partial write — silently, and with each write reporting success.

**`phase` closes a problem that was never articulated:** two similar documents
uploaded at different phases were indistinguishable at retrieval time. A Belt's
Measure-phase defect data and their Control-phase defect data both match
"defect data" with nothing to tell them apart — and since this index is the
sole external channel, that ambiguity lands directly on the coaching answer.

**Its filter defaults OFF, deliberately.** Cross-phase evidence retrieval is
the *normal* case — a Control Belt comparing against the Measure baseline —
so filtering to the current phase by default would break the comparison the
field exists to enable.

### 23.2.1 The `role` vocabulary — ratified, not invented per phase

**`role` is only a reliable filter if it is drawn from a fixed list.** Free text
drifts — "cycle times", "cycle time data", "cycle_times" — and **every drift is
a retrieval miss that looks like an empty result rather than an error**, which is
the failure class §27 exists to make impossible elsewhere.

**`kind` is a property of the row, not a separately declarable field.** A Belt or
an ask names the `role`; nothing names the `kind`. An inconsistent pair is
therefore unrepresentable rather than merely discouraged.

| `role` | `kind` | Typical phase |
|---|---|---|
| `as-is process map` | evidence | Define · Measure |
| `voice-of-customer data` | evidence | Define |
| `baseline defect data` | evidence | Measure |
| `cycle time data` | evidence | Measure · Analyse |
| `capability study data` | evidence | Measure · Control |
| `root cause analysis` | artefact | Analyse |
| `fmea worksheet` | artefact | Analyse · Improve |
| `to-be process map` | artefact | Improve |
| `improvement proposal` | artefact | Improve |
| `control plan draft` | artefact | Control |
| `other evidence` | evidence | any |
| `other artefact` | artefact | any |
| `unclassified (pre-ask-binding)` | evidence | any |

**"Process map" is why the pairing exists.** An **as-is** map describes the world
and is evidence; a **to-be** map is what the team designed and is an artefact.
The 6.11 live run classified `purpose=Process map` as `artefact`, which would
filter the current-state description out of evidence retrieval by default —
removing exactly the document a Measure or Analyse coach needs most. The
vocabulary distinguishes the two at the point of declaration.

**The two `other` rows are deliberate.** A Belt with a document that fits nothing
must still be able to upload it, and **forcing a wrong role is worse than an
honest catch-all**. A rising count of `other` is the signal that the vocabulary
needs extending.

#### `unclassified (pre-ask-binding)` is a MIGRATION SENTINEL, not a thirteenth role

**Ratified 2026-09-10**, when step 6.13's implementation audit found the ratified
Done-when unsatisfiable as written. It marks a document uploaded **before step
6.12 gave an upload an ask to answer**, and nothing else may carry it.

**The premise was verified against the stored bytes, not against a loaded
model.** `role`, `shape_match` and `content_digest` are **absent keys** in the
case blob's JSON on every pre-6.12 upload record. The `other evidence` and
`unsolicited` that appear when such a record is loaded are **Pydantic defaults
manufactured at load time** — read them as evidence of a stored value and the
migration writes a fabricated role into a filterable field. There is nothing in
the tree from which a real role can be derived for these documents.

**It is distinct from `other evidence` on purpose, and the reason is the signal
above.** `other evidence` is a Belt's honest *"this fits nothing"*, and this
section reads a rising count of it as the trigger to extend the vocabulary.
Backfilling legacy documents into that row would raise the count without a Belt
having chosen it once, and **the only signal this section relies on would then be
measuring the migration** rather than the corpus.

**Its `kind` is `evidence`, following Part AQ4 finding 2** — of the two available
failures, hiding a legacy document from evidence retrieval is the worse. **No
document may be given this role after 6.13's backfill.** A new upload has either
an ask or a declared purpose, and both yield a real role; a sentinel appearing on
a post-6.13 upload is a defect in the write path, not a classification.

> **Extending this vocabulary is a GOVERNANCE EVENT, not a code change.** A new
> row is a §56 amendment to this section, because `role` is a filter value that
> retrieval, supersession scoping and §6's uploads entry all read. Adding one in
> code produces a value no query filters on and no reviewer can see.

---

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

### `rag_lookup_evidence` returns a structured record, not rendered text

**APPLIED 2026-09-10, step 6.13**, with §23.2's five new fields, which three of
these keys read. `DECISIONS.md` Part AQ. `knowledge/tools.py::_evidence_record`
builds it; `test_evidence_index.py` pins that every key §24 names is present.

**The MECHANISM is unchanged.** Retrieval is a tool call the model decides to
make, never a prepended system message — *"RAG via tool, never via prepended
system message"* below, including its prohibition on an unconditional retrieval
pipeline. Both stand. **Only the shape of what comes back changes.** One record
per hit:

```
role · kind · description · phase · uploaded_at · shape_match
blob_path · content_digest · excerpt
```

**Two reasons, each sufficient on its own.**

**The coach has to CHOOSE a file, and choosing needs attributes rather than
prose.** *"Which of these three is the current cycle-time data"* is a question
about fields — `role`, `uploaded_at`, `shape_match` — not about similarity.
Rendered text forces the model to re-derive from prose what the index already
knows as values.

**§50's citations are built from `source`, `page` and `content_summary`**, and a
coach can only cite those accurately if it received them as values. Returning
prose and asking the model to reconstruct the citation from it is the
transcription anti-pattern §22 exists to prevent, performed on the platform's own
retrieval layer.

**`blob_path` and `content_digest` are in the record for §6's citation anchor**
— they are what a citation stores so that §37 / step 7.6 can detect that an
approved gate rested on a file that has since been replaced. A record that
omitted them would leave that cascade with nothing to compare.

**This applies to `rag_lookup_evidence` ONLY.** `rag_lookup_methodology` and
`rag_lookup_case_history` keep their current return shape, and the asymmetry is
deliberate rather than an oversight: **the evidence index is the only one whose
documents have identity, versions and supersession.** `(case_id, role)` is a
logical identity, `content_digest` a version identity, and a superseded document
is deleted (§23.2) — so *"which of these three is the current cycle-time data"*
is a question about fields. The BB eBook has no versions a Belt chooses between,
and a past case is retrieved for its pattern rather than selected as an object.
**Choosing between hits is a question about fields only where the hits are
distinguishable objects**, and only this index makes them so.

> **OPEN QUESTION — §50's citation argument reaches further than this change
> does.** §23.1 declares `source_file` and `page_number` on
> `improve_knowledge_index` as *"Returned for citation"*, so the second reason
> above — that a coach can only cite accurately what it received as values —
> applies to `rag_lookup_methodology` as well. **It is recorded here and not
> folded in**: changing that tool's return shape touches step 5.2's landed work
> and the coach prompts that consume it, which is a change with its own blast
> radius and deserves to be argued on its own rather than carried by an evidence
> amendment. The asymmetry above is the *design* reason for the split; this is
> the part of it that is unfinished.

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
are not importable from `langchain` in the current version. Re-verified by
import against the installed packages, 2026-09-13 — `langchain.retrievers`
raises `ModuleNotFoundError`, and both classes are present under
`langchain_classic.retrievers`. §18's rule applies: presence in
`langchain-classic` is not permission.

`EnsembleRetriever` would be the wrong class even if it were importable: it
fuses results from **different retriever sources** (BM25 + vector, say),
whereas our pattern is **same-index multi-query** — N phrasings against one
index. No standard LangChain 1.x class covers that pattern, and the LangChain
rag-fusion template used a custom implementation for the same reason.

**Two independent reasons, one conclusion.** Custom RRF is correct, stable and
dependency-free.

> **This section is also the second of §9's two reasons** for keeping
> `improve_case_index` on Azure AI Search: the Store has no multi-query + RRF,
> and no hybrid BM25 + vector scoring (§9 carries the introspection).

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
reads is declared as a managed value — **S-C02**.

**Three hops per Belt turn.** Beyond three the model is usually lost or
looping, and cutting it off is correct behaviour.

> **Three, not five** (v1.65, closing G-83). A hop is one model call plus six
> searches plus RRF — measured ~9.5s — so the cap must be reachable inside the
> executor's budget; the arithmetic is a test (`test_hop_cap.py`), and
> `MEASURED_HOP_SECONDS` carries its provenance.
>
> **PER-HOP COST IS DEFERRED, ON A CONDITION RATHER THAN AS AN OPEN
> QUESTION.** Fusion runs six queries per hop; cutting that is the other way
> to make more hops fit. **It waits for step 9.0**, when the knowledge corpus
> is ingested — **the first moment recall can be measured.** Cutting query
> breadth before there is a corpus to measure recall against would trade an
> unmeasured quality for a measured latency, which is the trade §52's
> regression thresholds exist to prevent.

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

> **NOT-MARKABLE:** **a map of mechanisms specified elsewhere** — Appendix A of the procedure ruled exactly that on 2026-09-07 when it found eleven ratified sections with no step. Working memory is `PhaseState`, durable memory is the Store, retrieval is §23–§25; each is marked where it is built. There is no artefact called *the memory taxonomy*.

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
A Black Belt still needs `vital_few_drivers`. The coach may open Analyse differently
for a BB with ten projects behind them, but the gate criteria do not move.

The mechanism is Appendix B item 5 — LangSmith traces record which coaching
approaches preceded clean gate passages and which preceded repeated loops; a
background process outside the coaching loop extracts the pattern; the next
session loads the learned procedures alongside the static rules, **extending
them, never overriding them.**

---

# Part VI — Tools

---

## 29. The data channel and the universal eight


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

### 29.2 The universal eight

Passed to **every** phase executor via `tools=`:

**Specification:** the three retrieval tools are **§59.5–§59.7 — S-F14 to S-F16**; the four
remaining universal tools are **§60.1–§60.4 — S-F19 to S-F22**;
`load_evidence_series` is **§60.7 — S-F57**.

#### `load_evidence_series` joins the set — RATIFIED 2026-09-09

**`load_evidence_series(blob_path, column)` returns a column's typed values plus
`n`, `mean`, `sigma`, `min` and `max`, re-parsed from the case blob** with the
deterministic parser built at step 6.11. It is built at **step 6.12**;
`DECISIONS.md` Part AR.

**It is a CLASSIFICATION, not an exception, and the reasoning is what makes that
true.** §30 defines a computation tool as a **pure function with no I/O** — all
twenty are, deliberately, because that is what makes them unit-testable without
a network. `load_evidence_series` reads a blob. **It therefore cannot be a
computation tool**, and the universal set is not a residual category it falls
into by elimination: **the universal set is already where the I/O-performing
tools live.** All three `rag_lookup_*` tools call Azure AI Search; this one
calls Azure Blob. It sits with them because it does what they do.

**Why a loader exists at all, rather than retrieval returning the numbers.**
Similarity search is the wrong mechanism for loading data — you do not fetch
five hundred rows by vector similarity. **Retrieval finds WHICH file; a
deterministic fetch loads THE VALUES.** The split is the point (§24).

**It re-parses the blob and reads no stored values.** `UploadRecord.rows` is a
row *count*; the parsed values themselves are stored nowhere, and stay that way.
Storing a second copy of the table would be the drift §39.2's single-authority
rule exists to prevent. Re-parsing costs milliseconds and keeps one source of
truth.

**The twenty computation tools are NOT touched.** They take scalar strings
(Part AD1), and the loader hands them exactly that. One new tool, zero changes
to twenty.

**`propose_diagram` returns structured JSON, not SVG.** The model describes
what to draw; the frontend owns how it looks. A model emitting SVG produces
markup that drifts from the design system and cannot be restyled.

### 29.3 `record_field` is RETIRED and may not be reintroduced

Field capture happens through `response_format=CoachingResponse` on the
executor (§20) — the coach emits `fields_captured` as structured output on
**every** turn, and the executor node writes each entry to `artifacts`.

**A tool would make capture a decision the coach might skip; structured output
makes it part of every response by construction.** That is the whole argument,
and it is why `record_field` is not among the universal tools.

### 29.4 Cross-agent tools — a third category, present but NOT BOUND

*Ratified 2026-08-21 via §56. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §Q1.*

**There are three tool categories in this system, not two:**

| Category | Where | Bound to |
|---|---|---|
| **The universal eight** (§29.2) | `knowledge/tools.py` | **Every** phase executor |
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
functions*; §29.2 defines the universal eight, which these are not among. Read
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
> 3. **They must return citations the way the universal eight do** (§50). They
>    return `str` with an inline source prefix, not structured citation
>    metadata, so nothing downstream can surface `source_file` / `page_number`.

**Never write to Agent Resolve indexes** (§23.5). Read-only is not a default
that may be relaxed.

---

## 30. Computation tools and per-phase binding

*Supersedes: REFACTORING §39; ARCHITECTURE.md §8.2; CLAUDE.md §5.2; DECISIONS §B7.*
**Status: RATIFIED.** File: `knowledge/computation.py`.

### Tool sets are per phase, not universal

**Tool selection quality degrades past roughly 10–15 tools per agent.**
Per-phase binding keeps every coach inside the tractable range.

| Phase | Universal | Computation tools | Total |
|---|---|---|---|
| **Define** | 8 | `calculate_expected_savings` | **9** |
| **Measure** | 8 | `calculate_sigma_level`, `calculate_cpk`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq`, `calculate_grr`, `calculate_sample_size_proportion`, `calculate_sample_size_mean` | **16** |
| **Analyse** | 8 | `t_test`, `chi_square_test`, `anova`, `pearson_correlation`, `linear_regression` | **13** |
| **Improve** | 8 | `calculate_doe_main_effects` | **9** |
| **Control** | 8 | `xbar_r_chart_limits`, `imr_chart_limits`, `p_chart_limits`, `c_chart_limits`, `post_improvement_cpk` | **13** |

**20 computation tools total.** 1 + 8 + 5 + 1 + 5 = 20.

> **The per-phase TOTALS above are the ratified figure, not the live one.**
> `_executor_tools` binds `len(UNIVERSAL_TOOLS)`, and `check_gate_status` (7.1)
> and `request_human_approval` (7.5) are unbuilt, so the live bind is lower by
> two until both land. `verify_built.py` pins the LIVE bind; the figure is
> stated there, not here.

**No phase exceeds 16 tools**, and **as of 2026-09-09 the maximum is 16
(Measure) — the ceiling exactly.** A new tool that would push a phase past 16
requires an amendment, not a routine addition.

> **⚠ THE CEILING MUST BE REVISITED BEFORE A NINTH UNIVERSAL TOOL IS ADDED, NOT
> AFTER.** `load_evidence_series` took Measure from 15 to 16 (§29.2, Part AR).
> There is now **no margin**: a ninth universal tool breaks the rule for Measure
> on the day it is added, and the two universal tools still unbuilt —
> `check_gate_status` (7.1) and `request_human_approval` (7.5) — are already
> inside the eight and inside this count.
>
> **A per-phase total that is legal only because nothing else has been added is
> a constraint with no margin, and the margin is what usually gets discovered by
> exceeding it.** The question to settle first is whether 16 is still the right
> ceiling given per-phase binding, not whether one more tool can be squeezed
> under it.

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

> **v1.75 (founder, 2026-09-25):** a SKILL.md says **what to teach** — the
> explanation, the worked example, the question, the read-back wording, per field
> — and contains **no move-sequencing** (*"then advance"*, *"confirm and move
> on"*). Which of those a turn uses is decided in code (§17). Define at step 6.61;
> the other four at step 6.62.

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
| 2 | **Every model call**, for the phase being coached (v1.71) | That phase's full SKILL.md, in the system message; version and hash recorded in `step_log` |
| 3 | On demand | Reference files, when explicitly needed |

**For the phase being coached, level 2 is placed in the system message on every model call by `DMAICSkillsMiddleware`, and each turn records the script's version and hash in `step_log` (v1.71).** `load_skill(name)` stays registered for other phases' scripts and level-3 references, but the current phase's script is never left to the coach's choice. **Rule: any content the product depends on is delivered and recorded, never left for the model to fetch.**

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
- **Metric-literacy explanations** (§43.7) — for each metric in play, what it
  is, why it matters in this phase, and how to read a good or bad value.
  **Distinct from the seven-step education on the statistic**: one teaches
  the Belt their own measure, the other teaches the tool
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

> **Today nothing pauses for a human**: position 6's interrupt is GUARDED until
> step 7.3 (§19.6). **Step 7.3 restores both interrupts** — `gate_review`'s and
> position 6's commented line — in the same commit.

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

**`/gate/reject` is now specified.** `gate_apply` branches on the Belt's
decision: **approve → assemble, write, `END`** (the parent's static edge
advances the phase); **reject → `Command(goto="planner")` carrying
`rejection_feedback`**, which returns the phase to coaching with the Belt's
stated reason in hand. **The Belt must supply a reason** — a rejection with no
reason gives the coach nothing to change, and the next turn would repeat the
one just refused. Full routing: **S-F13 DP3**; the field: **S-C02**.

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
| **2a** Coherence | Real, meaningful, conclusive? Catches gibberish, vague non-answers, self-contradiction, off-topic, parroting the Belt — a restatement with no confirmation question and nothing added, judged against the script step (v1.72) | Lightweight LLM | `coherence`, 0.1 | **Every turn** | **`CoherenceMiddleware`** (§19.7) |
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

### Gate-required fields by phase

| Phase | Gate-required fields | Count |
|---|---|---|
| **Define** | **All 12 — no tier split (Option A).** `business_case`, `team` (**list[dict]**), `voc_summary`, `problem_statement`, `baseline_estimate`, `project_scope` (**dict**), `goal_statement`, `target_value`, `target_date`, `secondary_metrics`, `process_map_sipoc` (**dict**), `issues_and_barriers` | **12** |
| **Measure** | `baseline_mean`, `data_collection_plan`, `driver_priority_summary`, `vital_few_drivers`, `detailed_process_map` (**dict**), `stability_assessment`, `issues_and_barriers` | **7** |
| **Analyse** | `root_cause_statement`, `root_cause_validation`, `practical_significance`, `issues_and_barriers` | **4** |
| **Improve** | `selected_solution`, `pilot_result`, `experiment_justification`, `issues_and_barriers` | **4** |
| **Control** | `control_plan` (**dict**, 5 sub-plans), `post_improvement_metrics`, `issues_and_barriers` | **3** |

> **Control's 3 Tier 1 / 9 Tier 2 split was confirmed at its phase review**
> (2026-08-27, §39.5), the ninth Tier 2 being `actual_close_date` (F-12). It is
> **the smallest Tier 1 set and the largest Tier 2 set**, and that is
> deliberate: Control is rich in best-practice closure steps a Belt should be
> coached toward but not gated on. **The three that block are the three that
> prove the project happened** — the result linked to the baseline, the control
> plan, and the sustainment risks.

> **Improve's 4 Tier 1 / 5 Tier 2 split was confirmed at its phase review**
> (2026-08-27, §39.4). **`solution_linked_to_root_cause` stays Tier 2** — but
> note the asymmetry the rubric encodes: the **dict** is Tier 2, while the
> **traceability it records is Tier 1**. A missing dict is weak documentation;
> a solution aimed at a different problem is a wasted phase.

> **Analyse's 4 Tier 1 / 5 Tier 2 split was confirmed at its phase review**
> (2026-08-26, §39.3). **`causal_hypothesis` stays Tier 2** and that is the
> considered answer rather than an oversight: the substance of the phase is
> carried by the Tier-1 `root_cause_statement`, `root_cause_validation` and
> `practical_significance`, and an Analyse phase without an explicit hypothesis
> dict is weaker but not void. **The traceability it provides rides on
> `phase_metrics` instead**, which is not skippable (§63.9).

> **Define is the one phase with no Tier 2** (founder ruling, Option A, ratified
> 2026-08-26). Every Define field blocks the gate, so `DEFINE_REQUIRED_FOR_GATE`
> **is** the whole coached list and there is no `acknowledged_gaps` path out of
> Define. **The other four phases retain both tiers**, each settled at its own
> phase review (§39.2–§39.5); Measure additionally keeps an optional path for
> MSA. The rows above are those four phases' **Tier 1** sets and Define's
> **complete** set — do not read the Define row as a tier.

**`issues_and_barriers` is gate-required in every phase.** Every real project has
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
| X-Y matrix | **`driver_priority_summary`, Tier 1, all Belts** — it produces the vital few X's that Analyse cannot start without |
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
`post_improvement_metrics` are cross-phase reference dicts (§7). **The grader
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
Control (`control_plan`, `sustainability_check`, `post_improvement_metrics`,
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
- The flag is read after the turn and **the graph PAUSES with LangGraph's own
  `interrupt()`**; the coach's response is suppressed and the interrupt payload
  goes to the Belt
- Payload: the contradicted field, its approved value and approving phase, the
  proposed value, the Belt's own words, and the two Belt-facing options below

> **What pauses is LangGraph's own `interrupt()`, raised in a node.**
> `HITLInterrupt` is DELIBERATELY NEVER DEFINED (G-15, ruling v1.21(D)): an
> exception raised from `after_agent` is not resumable. **The placement is step
> 6.44's**: detection stays in the coach's reply (no extra model call), the
> planner routes on the flag, and the stop lives in a node that writes nothing.

### §37 governs a GATE-COMMITTED value only

**A correction to an uncommitted field WITHIN a phase is not a §37 event.**
The Belt raising a baseline from "about 12%" to "12.4%" on turn 9 of Define,
before any gate has approved either, is **ordinary coaching** — it is the
system working, not a contradiction to stop the turn for. §37 fires only where
the Belt materially contradicts a value **an earlier phase's gate already
approved**, which is why the payload carries an `approved_phase` at all.

**The record of an in-phase correction is `PhaseState.field_log`** (§6, step
6.33): what the field said before, what it says now, on which turn, and the
Belt's stated reason where given. **Two different events, two different
records, and conflating them would make every ordinary revision an interrupt** —
which is the failure mode §20's *"leave null for prose rephrasing, and for any
refinement of a current-phase value that has not been committed yet"* already
warns the coach against. Stated here because that warning lived only in a field
description the coach reads, and not in the section that governs the behaviour.

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

> **NOT-MARKABLE:** a parent whose CHILDREN own the facts. §16's convention — *“one marker per item, never one per section that mentions it”* — and a row here would be a second claim over the same ground. **All FIVE direct children own rows** since 6.40 — §39.1 through §39.5, one per phase. (An earlier count of *20 of 67* was wrong in kind: it counted grandchildren, which have their own canonical homes.)

*Supersedes: REFACTORING §2; ARCHITECTURE.md §13.*
**Status: RATIFIED.**

| Phase | What the Belt produces | Gate blocks on |
|---|---|---|
| **Define** | A measurable problem, its scope, a SMART goal, the customer's voice, the team, a rough baseline, a target and a date, a SIPOC with KPIs | **Every field — no tiers** (§39.1) |
| **Measure** | A validated baseline, a data collection plan, a detailed process map, prioritised X's, a stability assessment | Its Tier 1 set (§35) |
| **Analyse** | A specific root cause, the evidence validating it, and how much of the problem it explains | Its Tier 1 set (§35) |
| **Improve** | A selected solution, a pilot result, and a stated position on experimentation | Its Tier 1 set (§35) |
| **Control** | A five-part control plan and the post-improvement measurement | Its Tier 1 set (§35) |

**Phase order is fixed and enforced by static edges** (§15). There is no
skipping and no reordering.

### The measurement thread that runs across three phases

Three fields carry one measurement chain, and **the grader verifies the same
measurement points carry different values** at each end:

```
Define    process_map_sipoc["process_metrics"]      — WHAT is measured
Measure   detailed_process_map["baseline_metrics"]  — the BEFORE values
Control   post_improvement_metrics                  — the AFTER values
```

**This is the spine of a DMAIC project.** A project that cannot show
before-and-after on the same measurement point has not demonstrated
improvement, whatever else its gate documents contain.

### 39.1 Define phase, complete specification


*Supersedes: the built `DefinePhaseInput` (F-11).*
**Status: RATIFIED 2026-08-25.** Files: `phases/define/schema.py`,
`phases/define/validate.py`, `skills/dmaic-define-phase/SKILL.md`.

#### 39.1.1 Purpose

Define is the **contract phase**. It turns a vague concern into a specific,
scoped, measurable project with an assigned team, **before any data work
begins.** At completion the Belt holds a charter-quality description: the
problem, who owns it, what is in and out of scope, the target, and the process
at a high level.

#### 39.1.2 The ordered field list — the `field_index` sequence (closes G-38)


**This is the order the planner walks.** `field_index` indexes into this list;
S-F13's DP1 predicate ("is the current field complete?") reads it. Before this
list existed, `field_index` indexed into nothing (G-38).

| # | Field (`artifacts` key) | Type | Gate | Notes |
|---|---|---|---|---|
| 1 | `business_case` | `str` | **required** | Strategic rationale — why invest; the quantified impact (COPQ) where the Belt has it |
| 2 | `team` | `list[dict]` | **required** | Each entry `{name, role, function}`. Roles per §39.1.4 |
| 3 | `voc_summary` | `str` | **required** | Who the customers are, and what they need |
| 4 | `problem_statement` | `str` | **required** | ONE SMART statement, **composed from 5W2H coaching** (§39.1.3). The 5W2H are NOT separate stored fields |
| 5 | `baseline_estimate` | `str` | **required** | **Discrete** current-state value — Control compares against it. Rough in Define; the rigorous baseline is Measure's job. Founder ruling: stays in Define |
| 6 | `project_scope` | `dict` | **required** | `{in_scope: str, out_scope: str}` — both explicit |
| 7 | `goal_statement` | `str` | **required** | The SMART sentence — human-readable prose that mirrors the problem |
| 8 | `target_value` | `str` | **required** | **Discrete** target value — Control compares achieved-vs-target. **Not redundant with `goal_statement`:** that is prose, this is the comparable value |
| 9 | `target_date` | `str` (ISO) | **required** | The **planned** completion date — a project-management parameter, which may slip without affecting the improvement logic. **Single date field** — `estimated_completion_date` is retired as a duplicate. Distinct from Control's actual close date (F-12) |
| 10 | `secondary_metrics` | `str` | **required** | What could get worse — the side-effect watch. One of the two fields §40 requires on all five schemas |
| 11 | `process_map_sipoc` | `dict` | **required** | Six keys: `suppliers`, `inputs`, `process_steps`, `outputs`, `customers`, `process_metrics`. Fewer than six filled is the partial-map failure (§41) |
| 12 | `issues_and_barriers` | `str` | **required** | Always last. "none identified at this stage" is a valid conscious answer |

> **Define uses Option A — all fields gate-required, no tiers. Ratified
> 2026-08-26.** `DEFINE_REQUIRED_FOR_GATE` is all 12; the gate blocks until
> every one is populated and passes the quality rubric, and **there is no
> `acknowledged_gaps` path for Define** because no field is skippable. This
> supersedes the 8/3 split of 2026-08-25 **for Define only** — the other four
> phases keep Tier 1 / Tier 2, each decided at its own phase review (§35,
> §39.1.8).
>
> The archived `docs/_archive/DEFINE_FINALIZATION_2026-08-26.md` still carries
> superseded names (`baseline`, `target_metric`). **The table above carries the
> current names. Do not re-apply the archived file verbatim.**

> **The measurement thread — do NOT "simplify" these away.** `baseline_estimate`,
> `target_value` and `target_date` are discrete fields **on purpose**, not
> redundant restatements of `goal_statement`. Define sets `baseline_estimate` (the
> start)
> and `target_value` (the goal value); **Control captures the achieved value
> and computes target-vs-actual.** If those numbers lived only inside
> `goal_statement` prose, Control could not extract and compare them. This
> mirrors the existing three-phase KPI thread —
> `process_map_sipoc["process_metrics"]` → `detailed_process_map["baseline_metrics"]`
> → `post_improvement_metrics` (§39, S-C27 B7). `target_date` is the same pattern
> for schedule rather than performance.

> **This list is the COACHED sequence and, for Define, also the complete
> required set.** `DefineOutput` is these 12 **plus** the four gate-metadata
> fields, which are assembled rather than coached — **16 fields in total: 12
> required, 4 gate metadata** (§40, §63.1). Unlike the other four phases, no
> Define field sits outside the coached walk: `secondary_metrics`, which the
> 2026-08-25 amendment's ten-row table had omitted and which §40 requires on all
> five schemas, is now coached at position 10 rather than assembled silently.

> **Reconciliation — supersedes the built v1 `DefinePhaseInput` (F-11).** v1 used
> granular 5W2H fields (`what` / `where` / `when` / `who_affected` /
> `why_it_matters` / `how_much_baseline` / `how_goal`), `scope_in` / `scope_out`,
> and **both** `target_date` and `estimated_completion_date`. All are
> **RETIRED.** v2 stores `problem_statement` (composed), `project_scope` (dict),
> one `target_date`. **The 5W2H survive as the coaching METHOD (§39.1.3), never
> as stored fields.** This was a documentation-versus-code divergence, resolved
> in favour of the v2 architecture names; `schema.py` is rebuilt to match.

#### 39.1.3 The composed-problem-statement rule (binding)

The coach elicits the problem through 5W2H sub-questions — what, where, when,
who is affected, why it matters, how much, and what "fixed" looks like — as
**conversational prompts, not fields.** The coach then **composes the Belt's
answers into one SMART `problem_statement`** and reflects it back for
confirmation. **Only the confirmed composed statement becomes
`artifacts["problem_statement"]`.**

**Anti-hallucination guard (§22).** Composition is *assembly of the Belt's own
words into SMART form*, never authorship. **The coach must not add facts,
numbers, or details the Belt did not provide**, and the Belt confirms accuracy
before storage. A composed statement carrying an invented number is exactly as
well-formed as a correct one — the guard is the only thing between them.

#### 39.1.4 The `team` structure

`team: list[dict]`, each entry `{name: str, role: str, function: str}`. Roles
follow standard Lean Six Sigma structure:

| Role | Who |
|---|---|
| **Project Leader** | The Belt driving day-to-day — Black Belt for complex or cross-functional work, Green Belt for departmental |
| **Sponsor / Champion** | Secures resources and removes barriers. **Approval required at the gate** |
| **Process Owner** | Owns the process being changed |
| **Team Members** | Subject-matter experts who work within the process |

**Coached early — position 2 — because the people must exist before the work.**
RACI framing is encouraged, not enforced.

#### 39.1.5 SIPOC handling

`process_map_sipoc` is a **dict, not free text** (six keys). **No computation
tool** — this is structured capture, and there is nothing to calculate.

The coach **shows a filled SIPOC example first, then builds the Belt's
column-by-column** — guided capture into the dict — offering an upload option.
Visual rendering routes through `propose_diagram` (**G-30, open**). A SIPOC
missing any of the six keys is the partial-map failure §41 describes.

#### 39.1.6 Gate, storage, progress view

- **All 12 fields block** the gate (Option A, §39.1.2). Define has no Tier 2,
  so the "warn only" path of §35 has no Define members and `acknowledged_gaps`
  is always empty for this phase.
- The **live gate document** renders from `artifacts` (§50) — the secondary tab
  where the Belt sees progress, what is done and what is missing. **Define shows
  one progress bar, not two**: the separate Tier-1 / Tier-2 bars of §50 apply to
  the four phases that have both tiers.
- Written **once** to `store/projects/{case_id}/artifacts/define.json` by
  `gate_apply` (§9, §33).

#### 39.1.7 The SKILL.md content (AUTHORITATIVE during the refactor)


> **Authority: THE FILES, not this section.**
> `skills/dmaic-define-phase/coaching_script.md` is the script and
> `skills/dmaic-define-phase/SKILL.md` is what ships; on conflict the files win,
> and the check that keeps them agreeing compares the two files.

> **Coaching pattern for every field:** ① **Explain** (plain language, why it
> matters) → ② **Show** (worked example, visually distinct, illustration only)
> → ③ **Ask** (invite the Belt's version) → ④ **Confirm** (reflect back, check,
> advance). Tone: warm, encouraging, never gatekeeping. Assume a capable but
> possibly non-expert Belt. Responses follow §50.1 structure — sectioned,
> scannable, never bulk prose.

**The script itself is `skills/dmaic-define-phase/coaching_script.md`**, beside
the `SKILL.md` it must match. `verify_built.py`'s *phase scripts byte-matching*
check compares the two FILES.

#### 39.1.8 The other four phases

Measure, Analyse, Improve and Control follow **this exact section shape**, at
§39.2–§39.5.

---

#### 39.1.9 The metric registry and Define's placeholder

**Define WRITES the registry; every later phase echoes it.** `metric_definitions`
is the project's canonical metric set — **§63.8, S-C38 owns its shape**, and this
subsection does not restate it.

**It is gate-required and it is NOT a coached position of its own**, which is the
distinction this subsection exists to record. The Belt names their metrics inside
**position 5's** conversation (`baseline_estimate`), because *"what are we
measuring, in what units"* and *"what is it at today"* are one exchange, not two.
The CTQs (inside position 3) and the 5W2H answers (inside position 4) are captured
the same way (v1.79). `field_index` indexes `DEFINE_FIELD_ORDER`; only the gate list
is longer. The owner of both lists and their lengths is `phases/define/schema.py`
(`DEFINE_REQUIRED_FIELDS`, `DEFINE_REQUIRED_FOR_GATE_FIELDS`, `_CAPTURED_INSIDE`).

**Define writes one `phase_metrics` entry per registry metric it engaged**,
assembled deterministically in `gate_apply` immediately before the
`{Phase}Output` is constructed — **no model call**. Each entry carries five
keys: `name` and `unit` taken verbatim from `metric_definitions`;
`baseline_estimate` and `target_value` taken from the captured fields of the
same names; and `source: "stated"`, because **Define states rather than
measures**. A phase engaging no metric writes `"none this phase"` (§63.9 B2).

**The single-authority invariant (§39.2.3, S-F28) then holds BY CONSTRUCTION** —
the entry's values ARE the captured scalars, so the two cannot drift. That is
the whole reason the assembly is deterministic and sited at `gate_apply`: a
model asked to restate a number it was shown is a second author of that number,
and §39.2.3 exists because two authors of one figure is how a gate document
comes to disagree with the field it was built from.

**This subsection states ONCE what §63.1's type comment and §63.9's table row
carry separately; neither is superseded.**

#### 39.1.10 Tools bound to Define

**The count is owned by the live bind, not by this list** —
`COMPUTATION_TOOLS_BY_PHASE` in `knowledge/computation.py` plus
`UNIVERSAL_TOOLS`, re-run every commit by `verify_built.py`'s *LIVE per-phase
tool bind* check. Define is the lightest of the five by design: scoping is a
conversation, not a calculation.

#### 39.1.11 Conditions — routing and the gate

**Define's subgraph is the canonical five nodes** (§13), with no phase-specific
routing condition. The planner cycles to the executor until it routes to the
gate; the validation stack returns to the planner with `validator_feedback` on a
failure, sharing the cap of 3 (§34).


#### 39.1.12 State parameters — Define's use of `PhaseState`

**There is no `DefineState`.** §39.x.7 describes per-phase USE of the shared
`PhaseState` — **S-C03 carries that ruling**. Define reads `asks`, `uploads`, `artifacts`, `coaching_plan` and
`field_index`; it writes `artifacts` through `fields_captured` (S-C05). Field
names, counts and types are owned by `core/substate.py` and are not restated
here.

#### 39.1.13 Metric literacy — what each metric means

**Define's SKILL.md carries the METRIC LITERACY block**, as all five do —
`verify_built.py` re-runs the count. Its Define-specific content is the
distinction the Belt meets first: a **baseline** is what the process does today
and a **target** is what it must do, expressed in the same unit, with
`metric_definitions` naming that unit once for the whole project (§39.1.9).

#### 39.1.14 Cross-phase reads and writes

**Define is the origin of the measurement thread.** It writes and nothing
upstream reads it; Measure, Analyse, Improve and Control all read what it
commits. The mechanism is the Store, never parent state (§10.2) — the
cross-phase reference fields are §42's, and `baseline_estimate` /
`target_value` are the two Control compares against when the thread closes
(§39.5).

> **39.1.9–39.1.14 are appended rather than interleaved, deliberately**:
> inserting them in the other phases' order would renumber the cited
> 39.1.3–39.1.8, and a renumbered citation resolves silently to the wrong
> subsection. Reading order is not numbering order.

### 39.2 Measure phase, complete specification

*Per-phase HUB: indexes the cross-cutting specs (state §6/§58.2, graph/routing
§13–16, gate §33–38, tiers §35, tools §30/§69, dicts §41, gate doc §50) and
records only what is Measure-specific. Define-once holds — nothing here
re-defines a mechanism that lives in a concern Part.*

**Status: RATIFIED 2026-08-26.** Files: `phases/measure/schema.py`,
`phases/measure/validate.py`, `skills/dmaic-measure-phase/SKILL.md`.

#### 39.2.1 Purpose

Measure establishes what is actually happening and proves the numbers can be
trusted before anyone acts on them. It opens on Define's contract, expands the
high-level SIPOC into an operational process map, decides what to collect and
how, validates the measurement itself, confirms the process is stable, and only
then fixes a baseline — leaving the Belt with a trustworthy baseline and the
vital few drivers Analyse will test.

#### 39.2.2 The ordered field list — the `field_index` sequence


The order the planner walks (`field_index` indexes into it). Coached in
**methodology order, not tier order** — the inversion at 3–4 is deliberate
(§39.2.6). Schema: **§63.2 — S-C28** (canonical home).

| # | Field (`artifacts` key) | Type | Tier | Note |
|---|---|---|---|---|
| 1 | `detailed_process_map` | `dict` | 1 | Six sub-fields (§41). Everything attaches to it |
| 2 | `data_collection_plan` | `str` | 1 | Flows from the map's measurement points |
| 3 | `measurement_system_validated` | `str` | 2 | MSA. **Offered before the baseline** (§39.2.6) |
| 4 | `stability_assessment` | `str` | 1 | Run-chart read. **Before capability** (§39.2.6) |
| 5 | `baseline_mean` | `str` | 1 | The measured central value; supersedes Define's `baseline_estimate` |
| 6 | `baseline_sigma` | `str` | 2 | Spread / sigma level |
| 7 | `driver_priority_summary` | `str` | 1 | Scored prioritisation of candidate drivers |
| 8 | `vital_few_drivers` | `str` | 1 | Ranked shortlist Analyse consumes |
| 9 | `secondary_metrics` | `str` | 2 | Carried from Define, re-checked |
| 10 | `issues_and_barriers` | `str` | 1 | Ask once collection has been attempted |

`MeasureOutput` = these ten **+** `phase_metrics` (§39.2.3) **+** the four
gate-metadata fields (§40). Measure keeps both tiers, unlike Define (§35).

#### 39.2.3 The metric registry and Measure's placeholder

**The registry is Define's** (`metric_definitions`, §39.1, **§63.8 — S-C38**):
the canonical set of project metrics, each `{name, unit, meaning}`. `name` is
the traceability key, identical in every phase.

**Measure's placeholder is `phase_metrics`** (**§63.9 — S-C39**) — a
`list[dict]`, one entry per registry metric this phase measured:

```python
phase_metrics = [
    {"name": "invoice_error_rate", "unit": "%",
     "baseline_mean": "12.3%", "baseline_sigma": "2.6 sigma",
     "stability": "stable (2 special causes excluded)", "source": "measured"},
    {"name": "invoice_cycle_time", "unit": "days",
     "baseline_mean": "2.6 days", "baseline_sigma": "—", "stability": "stable",
     "source": "measured"},
]
```

Structured registry (founder ruling 2026-08-26): a narrow, justified **fourth
exception** to §7's string law, same class and reason as the three cross-phase
reference dicts — the grader traces a metric across phases by **key equality on
`name`**, not by reading prose. Scalar values inside stay strings.
`detailed_process_map["baseline_metrics"]` captures the before-values in the
map, per step; `phase_metrics` is the phase-level roll-up the next phase reads.
Multi-criteria falls out: one entry per metric, tools run once per entry
(`name` in `computation_results.inputs`, §69.1). Scan `phase_metrics` across the
five gate documents and a metric's whole journey is one keyed trail.

> #### The single-authority rule — binding on all five phases
>
> **`phase_metrics` is the authoritative per-metric store.** The scalar fields
> — Measure's `baseline_mean` and `baseline_sigma`, Define's `baseline_estimate`
> and `target_value`, Control's `post_improvement_metrics` — are **the primary
> metric's mirror**. They are kept because the gate document reads far better
> with a named scalar than with an index into a list, and because Control's
> target-vs-actual comparison was specified against them before the registry
> existed.
>
> **They MUST equal that metric's `phase_metrics` entry.** **Additional metrics
> live only in `phase_metrics`** and have no scalar to mirror.
>
> **Enforced as a `gate_apply` assembly invariant** (§40.1, **S-F28**), not as a
> convention: `assert_single_authority(phase, artifacts)` runs before the
> `{Phase}Output` is constructed, and a mismatch **raises**. By assembly time
> every value has been captured, validated and Belt-approved, so two stores
> disagreeing about one number is a code defect rather than an incomplete
> phase — the class §40.1 already says must surface loudly rather than default
> quietly. Implementation: `core/metrics.py`.
>
> **Two stores holding one value is how they drift**, and the drift is invisible
> at the moment it happens: both reads succeed, both look authoritative, and the
> disagreement only surfaces one phase later when Control compares against
> whichever it happened to read. The mirror is the cheap change; the check is
> what makes the mirror safe.
>
> **Analyse and Improve mirror nothing** — they act on drivers rather than
> outcome values, so their entries record which metric a cause or solution
> targets, and the invariant is vacuously satisfied (§63.9).

#### 39.2.4 SIPOC → the detailed process map

*Parallel to Define's §39.1.5 SIPOC handling.* Measure does not build a SIPOC —
it **expands Define's** into an operational map. `detailed_process_map` is a
`dict`, six sub-fields (§41, **S-C33**): `steps`, `cycle_times`, `resources`,
`value_vs_waste`, `measurement_points`, `baseline_metrics`. **No computation
tool** — structured capture, nothing to calculate.

- **Reads** Define's `process_map_sipoc` first and opens the phase on it
  (§39.2.11). The detailed map must **decompose that same SIPOC**, not describe
  a different process, and must **stay inside `project_scope`** — the grader
  flags a map that adds steps Define scoped out (§41).
- **Show then build:** a completed example first, then the Belt's own,
  step-by-step (never all six sub-fields at once). Waiting and rework are their
  own rows — that is where the hidden time and the hidden factory live.
- **`baseline_metrics` connects to Define's `process_metrics`** — the same
  measurement points, now carrying before-values (the measurement thread, §39).
- Visual rendering routes through `propose_diagram` (§29); a partial map missing
  any sub-field is the failure §41 describes.

#### 39.2.5 Tools bound to Measure

Passed to the executor via `tools=` on `create_agent` (§18); from the subgraph's
view the executor is one node (§13). The count is owned by the live bind
(§39.1.10), under the 16 cap (§30).

- **The universal eight** (§29.2), on every phase.
- **Eight computation tools** (§30 binding; specified §69, **S-F38–S-F45**),
  standard statistical names kept (two-tier acronym rule), with
  plain-concept-then-standard-term docstrings (§69.1):

| Job | Tools | Serves |
|---|---|---|
| Size the sample | `calculate_sample_size_proportion`, `calculate_sample_size_mean` | `data_collection_plan` |
| Trust the gauge | `calculate_grr` | `measurement_system_validated` (lock 1) |
| Characterise the baseline | `calculate_sigma_level`, `calculate_dpmo`, `calculate_yield_rty`, `calculate_ftq` | `baseline_mean` / `baseline_sigma` |
| Prove capability | `calculate_cpk` | capability (lock 2, after stability) |

Each runs under the seven-step pattern (§43.1). The SKILL.md `allowed-tools`
MUST match this exact subset (§32) — skill/tool drift produces a coach that
promises a tool it was not given.

#### 39.2.6 Conditions — sequence locks, routing, and the gate

**Two methodology sequence locks** (coaching-order conditions; a number produced
out of order looks authoritative while being wrong):

1. **Validate before you trust** — `measurement_system_validated`
   (`calculate_grr`) is coached at position 3, **before** the baseline at 5.
   Enforced by coaching order plus the rubric. A baseline off an unvalidated
   gauge measures the people, not the process.
2. **Stability before capability** — `stability_assessment` (4) is established
   **before** `calculate_cpk` may run. Enforced as a **tool precondition** —
   `stability == "stable"` (§69, S-F39; §63.2 B1) — not merely a convention.

**Routing conditions** — Measure's subgraph is the five-node cycle (§13), routed
by `Command`, not conditional edges (§15). Nothing Measure-specific in the
topology; the conditions that fire:

| Where | Condition | Goes to |
|---|---|---|
| `planner` (S-F13 DP1) | current field incomplete, or more fields remain | `executor` (`field_index++`) |
| `planner` | all 10 captured | `validation_stack` |
| `validation_stack` | 2b presence of the **7 Tier 1** + 2d `MEASURE_RUBRIC` pass | `gate_review` |
| `validation_stack` | fail | `planner` (+ `validator_feedback`); `gate_attempts ≥ 3` → escalation (§38) |
| `gate_apply` | Belt approve / reject | `END` / `planner` (+ `rejection_feedback`) |

**Gate-pass condition:** the 7 Tier 1 fields present and the rubric clears; the 3
Tier 2 fields warn only, a skip recorded in `acknowledged_gaps` (§35). Each phase
runs its own validation loop with its own budget of 3 (`gate_attempts` is per
phase, §6).

#### 39.2.7 State parameters — Measure's use of `PhaseState`


*Indexes §6 / §58.2 — **S-C02**; nothing re-defined.* **There is no `MeasureState`.** Measure uses the shared `PhaseState`; this table is its USAGE — which Measure field each shared field carries, and who reads it:

| `PhaseState` field | In Measure |
|---|---|
| `artifacts` | holds the 10 captured fields **+ `phase_metrics` + `computation_results`**; the planner reads it to derive what is next (there is no queue) |
| `field_index` | walks the §39.2.2 list (0–9); distinct from `phase_index` (§6) |
| `gate_attempts` | Measure's own retry counter, cap 3 → escalation; reset on pass |
| `validator_feedback` | accumulates across the ≤3 validation retries; the coach reads the full list |
| `citations` / `uploads` | the evidence trail — Measure is the heaviest upload phase (error logs, time studies, GR&R sheets); both land in the gate document |
| `computation_results` | every tool run (§7 shape); the grader scans it for tool evidence, not prose |
| `hop_results` / `synthesis_output` | declared but `[]` / `None` on Measure's typically single-hop turns (multi-hop is mainly Analyse, §26) — present because `CoachingPlan.retrieval_strategy` may select `multi_hop` in any phase |
| `draft` / `belt_edits` / `final` | `dict`, never `str` (§6); `final` is the assembled gate document |

Any new Measure state field requires an amendment (§6, §56).

#### 39.2.8 Metric literacy — what each metric means

New requirement (§32, §43.7), Measure instance. The coach teaches **two distinct
things**, and must not conflate them:

- **The metric** (the business measure — `invoice_error_rate`): what it is, why
  it matters in Measure, and how to read a good baseline. Fires when the metric
  is first measured, echoing its Define `meaning`. *"Error rate is the share of
  invoices sent back for correction — your primary problem metric. A baseline
  worth trusting is a stable, validated number with its sample and period
  stated."*
- **The statistic** (`mean`, `sigma`, `Cpk`, `DPMO`, `RTY`, `FTQ`, `Gage R&R`):
  the seven-step **educate** step (§43.1 step 1) — what the number means before
  it is produced.

Plain language (§50); surfaced through `CoachingResponse.explanation` (§50.1).

#### 39.2.9 Gate, storage, progress view

- **Seven Tier 1 fields block** the gate (§35). Three Tier 2 warn only.
- **The live gate document** (§50) renders `detailed_process_map` and
  `driver_priority_summary` as tables, `vital_few_drivers` as a numbered list,
  and `computation_results` inline with interpretation and charts (via
  `propose_diagram`), **grouped by `phase_metrics` `name`** when several metrics
  run. Narrative assembles from captured field text + `computation_results` +
  `phase_metrics` — **never** from `CoachingResponse` turn fields (§50, WATCH 9).
- **Two progress bars**, Tier 1 and Tier 2 (Measure has both tiers — unlike
  Define's single bar).
- Written **once** to `store/projects/{case_id}/artifacts/measure.json` by
  `gate_apply` (§9, §33), after the single-authority invariant clears (§39.2.3).

#### 39.2.10 The SKILL.md content (AUTHORITATIVE during the refactor)


> **Authority: THE FILES, not this section.**
> `skills/dmaic-measure-phase/coaching_script.md` is the script and
> `skills/dmaic-measure-phase/SKILL.md` is what ships; on conflict the files win.
> `verify_built.py`'s *phase scripts byte-matching* check compares the two files.
> The per-field coaching pattern is §39.1.7's; the seven-step tool pattern is §43.1.

#### 39.2.11 Cross-phase reads and writes

**Reads from Define** (`store.get(("projects", case_id, "artifacts"), "define")`):
`metric_definitions` (the registry), `process_map_sipoc["process_metrics"]`,
`baseline_estimate` (the anchor; flag drift into `baseline_mean`), `target_value`,
`project_scope` (bounds the map), `problem_statement` (re-test), `voc_summary`
(spec limits for `calculate_cpk`), `secondary_metrics`, `issues_and_barriers`.

**Writes:** `detailed_process_map["baseline_metrics"]`, `phase_metrics`,
`baseline_mean`, `baseline_sigma`, `driver_priority_summary`,
`vital_few_drivers`.

**Hands to Analyse:** `vital_few_drivers` (the starting list),
`driver_priority_summary` (how it was derived), `baseline_mean` and
`phase_metrics` (the values `causal_hypothesis` references),
`measurement_system_validated` and `stability_assessment` (preconditions).

#### 39.2.12 The other two phases

Improve and Control follow **this same section shape**, at §39.4–§39.5.

---

### 39.3 Analyse phase, complete specification

*Per-phase HUB: indexes the cross-cutting specs (state §6/§58.2, graph/routing
§13–16, gate §33–38, tiers §35, tools §30/§69, multi-hop §26, cross-phase refs
§7/§42, gate doc §50) and records only what is Analyse-specific. Define-once
holds — nothing here re-defines a mechanism that lives in a concern Part.*

**Status: RATIFIED 2026-08-26.** Files: `phases/analyse/schema.py`,
`phases/analyse/validate.py`, `skills/dmaic-analyse-phase/SKILL.md`.

#### 39.3.1 Purpose

Analyse takes the vital few drivers Measure prioritised and finds — and proves —
which of them actually cause the problem. It has two distinct movements:
**generate** candidate root causes (qualitative — fishbone, 5 Whys, Pareto), then
**validate** them against the data (hypothesis tests, ANOVA, regression). It ends
with a specific, evidence-backed root cause and an honest statement of how much
of the problem that cause explains — the input Improve needs before it designs a
fix.

#### 39.3.2 The ordered field list — the `field_index` sequence


Coached in **methodology order** — frame, generate, validate, confirm, quantify,
socialise. Schema: **§63.3 — S-C29** (canonical home).

| # | Field (`artifacts` key) | Type | Tier | Note |
|---|---|---|---|---|
| 1 | `statistical_problem_statement` | `str` | 2 | Translate the practical problem into a testable statistical question. All Belts, in Analyse — not Define |
| 2 | `causal_hypothesis` | `dict` | 2 | Candidate cause(s), generated (fishbone/5-Whys), linked to the metric being explained (§39.3.3) |
| 3 | `root_cause_validation` | `str` | 1 | Statistical or observational evidence the cause is real |
| 4 | `ruled_out_causes` | `str` | 2 | Alternatives tested and rejected, with rationale |
| 5 | `root_cause_statement` | `str` | 1 | The confirmed, specific, actionable root cause |
| 6 | `practical_significance` | `str` | 1 | How much of the problem it explains — the eBook's second gate |
| 7 | `process_owner_buyin` | `str` | 2 | The owner accepts the root cause |
| 8 | `secondary_metrics` | `str` | 2 | Carried from Measure, re-checked |
| 9 | `issues_and_barriers` | `str` | 1 | Always last |

`AnalyseOutput` = these nine **+** `phase_metrics` (§39.3.3) **+** the four
gate-metadata fields (§40).

**Note the generate-before-validate ordering** (2 before 3). A hypothesis is
generated qualitatively, then tested. `root_cause_statement` (5) lands *after*
validation (3) and ruling-out (4) — you state the cause once, once it is proven,
not as an opening guess refined in place.

#### 39.3.3 The metric registry and Analyse's placeholder (linkage form — closes F-13)

Analyse holds no *measured* metric value — Measure did that. Its `phase_metrics`
entry records the **linkage**: which root cause explains which registry metric.

```
phase_metrics = [
  {name: "invoice_error_rate", explained_by: "root cause: onboarding gap in first 60 days",
   share_explained: "≈70% (practical_significance)", source: "linkage"},
  {name: "invoice_cycle_time", explained_by: "not addressed this phase", source: "linkage"}
]
```

A metric Analyse does not address writes `"not addressed this phase"`, never a
silent absence. This keeps the keyed trail unbroken through a phase that acts on
drivers rather than outcome values.

**`causal_hypothesis` names the metric it explains.** Its reference dict
(§63.6 / S-C32) gains `references_metric_name` so a multi-metric project links a
hypothesis to a *specific* Y, not just "the baseline":

```
causal_hypothesis = {
    "hypothesis":          "Inadequate onboarding causes the error spike in first 60 days",
    "references_phase":    "measure",
    "references_field":    "baseline_mean",
    "references_metric_name": "invoice_error_rate",   # NEW — which metric
    "references_value":    "12.3%",
}
```

The grader resolves the link by lookup against Measure's gate document (§42),
now matching on `references_metric_name` against the `phase_metrics` key, not on
a bare scalar. `causal_hypothesis` stays **Tier 2** (the substance is in the
Tier-1 `root_cause_*` fields); the linkage traceability itself rides on
`phase_metrics`, which is not skippable.

#### 39.3.4 Two movements — generate, then validate

*Analyse's methodology core (parallel to Measure's §39.2.4 SIPOC handling).*

**Movement 1 — generate (qualitative).** From Measure's `vital_few_drivers`, the
coach helps the Belt generate candidate causes: a **fishbone** (`propose_template`
/ `propose_diagram`) to structure them by category, **5 Whys** (a coaching
sequence, not a tool) to drill past symptoms, **Pareto** (`propose_diagram`) to
focus. Output: `causal_hypothesis`. No computation tool — this is structured
thinking, nothing to calculate.

**Movement 2 — validate (quantitative).** Each surviving hypothesis is tested
against the data with the computation tools (§39.3.5). Output: `root_cause_
validation`, `ruled_out_causes`, and — only once proven — `root_cause_statement`.

**The bright line between them is the load-bearing teaching of the phase.** A
cause that feels obvious on a fishbone is a hypothesis, not a finding, until the
data backs it. Skipping movement 2 is how a Belt ships their first guess as a
root cause.

#### 39.3.5 Tools bound to Analyse

Passed to the executor via `tools=` on `create_agent` (§18). The count is owned
by the live bind (§39.1.10), under the 16 cap (§30).

- **The universal eight** (§29.2), on every phase — including `propose_template`
  and `propose_diagram`, which carry the **generation** tools here: fishbone,
  Pareto, scatter plot, box plot. 5 Whys is a SKILL.md coaching sequence, not a
  registered tool.
- **Five computation tools** (§30 binding; specified §69), standard statistical
  names kept, plain-concept-then-standard-term docstrings:

| Job | Tools | Use |
|---|---|---|
| Compare groups | `t_test`, `anova` | Does the driver shift the outcome between groups? |
| Association, categorical | `chi_square_test` | Are two categorical factors related? |
| Association, continuous | `pearson_correlation` | Do two continuous variables move together? |
| Explain / predict | `linear_regression` | How much of the outcome does the driver explain? |

No `calculate_doe_main_effects` — DOE belongs to Improve (§30). Each tool runs
under the seven-step pattern (§43.1). SKILL.md `allowed-tools` MUST match this
exact subset (§32).

#### 39.3.6 Conditions — methodology guards, routing, and the gate

**Two methodology guards** (Analyse's equivalent of Measure's sequence locks):

1. **Correlation is not causation.** When `pearson_correlation` or
   `linear_regression` shows association, the coach requires a plausible
   **mechanism** before it is written as a root cause. Association is evidence
   toward a hypothesis, never the confirmation itself — enforced by the rubric.
2. **Statistical ≠ practical significance.** A result may be statistically
   significant (`p < 0.05`) and explain a trivial share of the problem. The gate
   requires **`practical_significance`** (Tier 1) alongside validation — the
   eBook's second gate. A validated cause explaining too little is coached back,
   not carried to Improve.

**Routing conditions** — the five-node cycle (§13), `Command`-routed (§15). The
Analyse-specific one:

| Where | Condition | Goes to |
|---|---|---|
| `planner` (S-F13 DP1) | current field incomplete, or more fields remain | `executor` (`field_index++`) |
| `planner` | may select `retrieval_strategy = multi_hop` (§26) — Analyse is the phase this exists for | `executor` |
| `planner` | all 9 captured | `validation_stack` |
| `validation_stack` | 2b presence of the **4 Tier 1** + 2d `ANALYSE_RUBRIC` pass | `gate_review` |
| `validation_stack` | fail | `planner` (+ `validator_feedback`); `gate_attempts ≥ 3` → escalation (§38) |
| `gate_apply` | Belt approve / reject | `END` / `planner` (+ `rejection_feedback`) |

**Gate-pass condition:** the 4 Tier 1 fields present and `ANALYSE_RUBRIC` clears;
the 5 Tier 2 fields warn only, a skip recorded in `acknowledged_gaps` (§35).

#### 39.3.7 State parameters — Analyse's use of `PhaseState`


*Indexes §6 / §58.2 — **S-C02**; nothing re-defined.* **There is no `AnalyseState`.** Analyse uses the shared `PhaseState`; this table is its USAGE — which Analyse field each shared field carries, and who reads it — note this is the phase where multi-hop is real:

| PhaseState field | In Analyse |
|---|---|
| `artifacts` | the 9 captured fields + `phase_metrics` + `computation_results` |
| `field_index` | walks the §39.3.2 list (0–8) |
| `hop_results` / `synthesis_output` | **populated here** — Analyse's planned multi-hop retrieval chain (§26); the dedicated synthesis call's output lives in state, not a node local, so it is traced and survives resume |
| `computation_results` | every hypothesis test run; **validation stack Layer 2d** scans it for `t_test` / `anova` / `chi_square_test` evidence, not prose (§62.9 B3 — **not `DMAICGraderMiddleware`**; §36 forbids conflating the two graders, and this row is where that conflation entered) |
| `gate_attempts` | Analyse's own retry counter, cap 3 |
| `citations` / `uploads` | evidence trail; Analyse leans on `rag_lookup_case_history` (precedent from other projects) more than any phase |

#### 39.3.8 Metric literacy — what each metric and statistic means

New requirement (§32, §43.7), Analyse instance. The coach teaches, in plain
language (§50), for each thing in play:

- **The metric** — echo its Define `meaning`; frame what "explaining" it means
  ("we're finding what drives the 12.3% error rate, and how much of it").
- **The statistic** — the seven-step *educate* step (§43.1 step 1) for
  `p-value`, `t-statistic`, `R²`, `correlation coefficient`. *"A p-value is the
  chance you'd see this result if the driver made no difference — small means
  the effect is probably real. R² is the share of the variation this driver
  explains — that's your practical significance."*

Never a raw dump — `t = 4.23, p = 0.001` without the plain-language read is a
rubric failure (§43.1).

#### 39.3.9 Gate, storage, progress view

- **Four Tier 1 fields block** the gate (§35). Five Tier 2 warn only.
- **The live gate document** (§50) renders the fishbone / Pareto / scatter via
  `propose_diagram` inline, and `computation_results` (each test) with its
  interpretation, grouped by `phase_metrics` `name`. Narrative from captured
  field text + `computation_results` + `phase_metrics` — never `CoachingResponse`
  turn fields (§50, WATCH 9).
- **Two progress bars**, Tier 1 and Tier 2.
- Written **once** to `store/projects/{case_id}/artifacts/analyse.json` by
  `gate_apply` (§9, §33).

#### 39.3.10 The SKILL.md content (AUTHORITATIVE during the refactor)


> **Authority: THE FILES, not this section.**
> `skills/dmaic-analyse-phase/coaching_script.md` is the script and
> `skills/dmaic-analyse-phase/SKILL.md` is what ships; on conflict the files win.
> `verify_built.py`'s *phase scripts byte-matching* check compares the two files.
> The per-field coaching pattern is §39.1.7's; the seven-step tool pattern is §43.1.

#### 39.3.11 Cross-phase reads and writes

**Reads from Measure** (`store.get(("projects", case_id, "artifacts"), "measure")`):
`vital_few_drivers` (**the starting list — Analyse tests exactly these**),
`driver_priority_summary` (how they were ranked), `baseline_mean` and
`phase_metrics` (the values `causal_hypothesis` references),
`measurement_system_validated` and `stability_assessment` (preconditions — tests
on unvalidated or unstable data are meaningless), `data_collection_plan` (reuse
its definitions). Also reads Define's `metric_definitions` (the registry).

**Writes**: the 9 content fields, `phase_metrics` (the linkage), and
`causal_hypothesis` (with `references_metric_name`).

**Hands to Improve**: `root_cause_statement` (**what the solution must address**),
`practical_significance` (the size of the prize), `causal_hypothesis` and
`phase_metrics` (the metric linkage Improve's `solution_linked_to_root_cause`
extends).

#### 39.3.12 The other phase

Control follows this same section shape, at §39.5.

---

### 39.4 Improve phase, complete specification

*Per-phase HUB: indexes the cross-cutting specs (state §6/§58.2, graph/routing
§13–16, gate §33–38, tiers §35, tools §30/§69, dicts §41, cross-phase refs
§7/§42, gate doc §50) and records only what is Improve-specific. Define-once
holds — nothing here re-defines a mechanism that lives in a concern Part.*

**Status: RATIFIED 2026-08-27.** Files: `phases/improve/schema.py`,
`phases/improve/validate.py`, `skills/dmaic-improve-phase/SKILL.md`.

#### 39.4.1 Purpose

Improve designs, tests and proves the fix. It generates solutions that target the
validated root cause, selects the best on explicit criteria, decides what level of
experiment the choice needs, and — the discipline that defines the phase —
**pilots on a limited scale before full rollout**, proving the improvement is real
before the organisation commits to it. It ends with a selected, piloted,
evidence-backed solution and a plan to implement it.

#### 39.4.2 The ordered field list — the `field_index` sequence


Coached in **methodology order** — generate & select, justify, pilot, prove, plan,
socialise. Schema: **§63.4 — S-C30** (canonical home).

| # | Field (`artifacts` key) | Type | Tier | Note |
|---|---|---|---|---|
| 1 | `selected_solution` | `str` | 1 | Candidates generated (brainstorm), then the best selected on explicit criteria (decision matrix) |
| 2 | `solution_linked_to_root_cause` | `dict` | 2 | Cross-phase ref → Analyse `root_cause_statement`; names the metric (§39.4.3) |
| 3 | `experiment_justification` | `str` | 1 | DOE / simplified / none — **and why**. All three valid; the failure is drifting past the question (§41) |
| 4 | `pilot_result` | `str` | 1 | Piloted on a limited scale; practical **and** statistical significance |
| 5 | `explanatory_power` | `str` | 2 | R² / variance the solution explains |
| 6 | `implementation_plan` | `str` | 2 | Timeline, owner, resources for full rollout |
| 7 | `process_owner_buyin` | `str` | 2 | The owner accepts the solution |
| 8 | `secondary_metrics` | `str` | 2 | Carried from Analyse, re-checked against the pilot |
| 9 | `issues_and_barriers` | `str` | 1 | Always last |

`ImproveOutput` = these nine **+** `phase_metrics` (§39.4.3) **+** the four
gate-metadata fields (§40).

#### 39.4.3 The metric registry and Improve's placeholder (linkage form)

Improve's `phase_metrics` entry records which registry metric the selected
solution is expected to move, and what the pilot achieved on it:

```
phase_metrics = [
  {name: "invoice_error_rate", moved_by: "selected solution: onboarding checklist",
   pilot_effect: "12.3% → 4.1% in the pilot cell", source: "pilot"},
  {name: "invoice_cycle_time", moved_by: "not addressed this phase", source: "linkage"}
]
```

`"not addressed this phase"` for any registry metric the solution does not target.
**`solution_linked_to_root_cause` names the metric** via `references_metric_name`
(the uniform S-C32 shape, added 43c4201) — so a multi-metric project links the
solution to the specific Y its root cause explained. The grader resolves the link
by lookup against Analyse's gate document (§42).

#### 39.4.4 Two movements — generate-and-select, then pilot-and-prove

*Improve's methodology core (parallel to Analyse's §39.3.4).*

**Movement 1 — choose (generate, then select).** From Analyse's
`root_cause_statement`, the coach helps the Belt **generate** candidate solutions
(brainstorming, poka-yoke / mistake-proofing, `propose_template`) and then
**select** on explicit criteria — a **decision / selection matrix**
(`propose_template`) scoring options against impact, cost, effort and risk. Output:
`selected_solution`, `solution_linked_to_root_cause`. A solution chosen without
visible criteria is the failure this movement prevents.

**Movement 2 — prove (pilot, then confirm).** The chosen solution is **piloted on a
limited scale** and its effect measured. Output: `pilot_result`,
`explanatory_power`. The bright line: **a solution is a proposal until the pilot
data backs it.** Rolling out unpiloted is the failure movement 2 exists to prevent
— especially when the change is costly or hard to reverse.

#### 39.4.5 Tools bound to Improve

Passed to the executor via `tools=` on `create_agent` (§18). The count is owned
by the live bind (§39.1.10), under the 16 cap (§30).

- **The universal eight** (§29.2) — `propose_template` / `propose_diagram` carry
  the **generation and selection** tools here: brainstorming, the decision /
  selection matrix, mistake-proofing aids. FMEA is **supported if a Black Belt
  raises it** (result → `uploads`), never suggested unprompted, and is not a
  schema field (§41).
- **One computation tool** (§30 binding; specified §69), standard name kept:

| Job | Tool | Use |
|---|---|---|
| Test factor effects | `calculate_doe_main_effects` | Which factors, at which settings, move the outcome — when a designed experiment is run |

Run under the seven-step pattern (§43.1). SKILL.md `allowed-tools` MUST equal this
subset (§32).

#### 39.4.6 Conditions — methodology guards, DOE belt-gating, routing, gate

**Two methodology guards** (Improve's sequence locks):

1. **The solution must trace to the validated root cause.** `solution_linked_to_
   root_cause` references Analyse's `root_cause_statement` by lookup (§42). A
   solution that does not address the proven root cause is solving the wrong
   problem — the rubric requires the link.
2. **Pilot before full rollout.** `pilot_result` (Tier 1) gates on evidence from a
   limited-scale trial showing **practical AND statistical** significance — the
   same two-gate test as Analyse (§39.3.6). A pilot that is statistically
   significant but trivial in effect is coached back, not passed.

**DOE is belt-gated** (§35, S-C30 B1/B2): `experiment_justification` accepts three
valid answers — DOE conducted, a simplified one-factor experiment, or none needed
because the fix follows directly from the root cause. **All three pass**; the
failure is drifting past the question. DOE is **recommended for Black Belts,
suppressed for Green Belts.**

**Routing conditions** — the five-node cycle (§13), `Command`-routed (§15):

| Where | Condition | Goes to |
|---|---|---|
| `planner` (S-F13 DP1) | current field incomplete, or more fields remain | `executor` (`field_index++`) |
| `planner` | all 9 captured | `validation_stack` |
| `validation_stack` | 2b presence of the **4 Tier 1** + 2d `IMPROVE_RUBRIC` pass | `gate_review` |
| `validation_stack` | fail | `planner` (+ `validator_feedback`); `gate_attempts ≥ 3` → escalation (§38) |
| `gate_apply` | Belt approve / reject | `END` / `planner` (+ `rejection_feedback`) |

**Gate-pass condition:** the 4 Tier 1 fields present and `IMPROVE_RUBRIC` clears;
the 5 Tier 2 fields warn only, a skip recorded in `acknowledged_gaps` (§35).

#### 39.4.7 State parameters — Improve's use of `PhaseState`


*Indexes §6 / §58.2 — **S-C02**; nothing re-defined.* **There is no `ImproveState`.** Improve uses the shared `PhaseState`; this table is its USAGE — which Improve field each shared field carries, and who reads it:

| PhaseState field | In Improve |
|---|---|
| `artifacts` | the 9 captured fields + `phase_metrics` + `computation_results` |
| `field_index` | walks the §39.4.2 list (0–8) |
| `computation_results` | the DOE run, if any; the grader scans for `calculate_doe_main_effects` evidence behind an experiment claim, not prose |
| `uploads` | pilot data and any FMEA a Black Belt contributes land here (§29.1) |
| `gate_attempts` | Improve's own retry counter, cap 3 |
| `hop_results` / `synthesis_output` | `[]` / `None` on Improve's typically single-hop turns |

#### 39.4.8 Metric literacy — what each metric and statistic means

New requirement (§32/§43.7), Improve instance. The coach teaches, in plain
language (§50):

- **The metric** — echo its Define `meaning`; frame the pilot as moving it
  ("the pilot cut the error rate from 12.3% to 4.1% — here's whether that holds").
- **The statistic** — the seven-step *educate* step (§43.1 step 1) for a DOE
  **main effect** and **R²** (`explanatory_power`). *"A main effect is how much the
  outcome moves when you change one factor from its low to its high setting — the
  bigger it is, the more that factor matters."*

Never a raw dump (§43.1).

#### 39.4.9 Gate, storage, progress view

- **Four Tier 1 fields block** the gate (§35). Five Tier 2 warn only.
- **The live gate document** (§50) renders the decision / selection matrix as a
  table, the pilot before/after and any DOE effects as charts via
  `propose_diagram`, and `computation_results` with interpretation, grouped by
  `phase_metrics` `name`. Narrative from captured field text + `computation_results`
  + `phase_metrics` — never `CoachingResponse` turn fields (§50, WATCH 9).
- **Two progress bars**, Tier 1 and Tier 2.
- Written **once** to `store/projects/{case_id}/artifacts/improve.json` by
  `gate_apply` (§9, §33).

#### 39.4.10 The SKILL.md content (AUTHORITATIVE during the refactor)


> **Authority: THE FILES, not this section.**
> `skills/dmaic-improve-phase/coaching_script.md` is the script and
> `skills/dmaic-improve-phase/SKILL.md` is what ships and must contain it
> verbatim; on conflict the files win. `verify_built.py`'s *phase scripts
> byte-matching* check compares the two files. The per-field coaching pattern is
> §39.1.7's; the seven-step tool pattern is §43.1.

#### 39.4.11 Cross-phase reads and writes

**Reads from Analyse** (`store.get(("projects", case_id, "artifacts"), "analyse")`):
`root_cause_statement` (**what the solution must address**), `practical_significance`
(the size of the prize), `causal_hypothesis` and `phase_metrics` (the metric
linkage `solution_linked_to_root_cause` extends), `ruled_out_causes` (do not
re-propose a rejected cause's fix). Also reads Define's `metric_definitions` and
`target_value` (the pilot is measured against it).

**Writes**: the 9 content fields, `phase_metrics` (solution → metric, with pilot
effect), and `solution_linked_to_root_cause` (with `references_metric_name`).

**Hands to Control**: `selected_solution` (**what is now in place to hold**),
`pilot_result` and `implementation_plan` (the proven effect and how it was rolled
out), `phase_metrics` (which metrics moved, for Control's post-improvement
comparison).

#### 39.4.12 The last phase

Control takes §39.5, ratified at its own review on 2026-08-27. **All five phases
— Define, Measure, Analyse, Improve and Control — are now ratified. There is no
§39.6.**

---

### 39.5 Control phase, complete specification

*Per-phase HUB: indexes the cross-cutting specs (state §6/§58.2, graph/routing
§13–16, gate §33–38, tiers §35, tools §30/§69, dicts §41, cross-phase refs
§7/§42, gate doc §50) and records only what is Control-specific. Define-once
holds — nothing here re-defines a mechanism that lives in a concern Part.*

**Status: RATIFIED 2026-08-27.** Files: `phases/control/schema.py`,
`phases/control/validate.py`, `skills/dmaic-control-phase/SKILL.md`.

#### 39.5.1 Purpose

Control makes the gain stick. It confirms the improvement actually held against the
baseline and the target, builds the five-part control plan that keeps the process
from regressing, verifies the financial impact, and hands a monitored, documented,
owned process to the business before the project closes. It is where the
measurement thread that began in Define is finally closed: before → after, on the
same measure.

#### 39.5.2 The ordered field list — the `field_index` sequence


Coached in **methodology order** — confirm it held, lock it in, verify, hand over,
close. Schema: **§63.5 — S-C31**.

| # | Field (`artifacts` key) | Type | Tier | Note |
|---|---|---|---|---|
| 1 | `post_improvement_metrics` | `dict` | 1 | The AFTER values; cross-phase ref → Measure `baseline_mean`. **The only Tier-1 cross-phase reference** (§42) |
| 2 | `improvement_delta` | `str` | 2 | The change from baseline, per metric |
| 3 | `control_plan` | `dict` | 1 | **Five sub-plans** — documentation, monitoring, response, training, aligning_systems (§41) |
| 4 | `financial_impact_verified` | `str` | 2 | Realised saving — the actual against Define's `calculate_expected_savings` estimate |
| 5 | `sustainability_check` | `str` | 2 | How the gains are maintained after the project |
| 6 | `handover_documented` | `str` | 2 | Named process owner accepting ongoing ownership |
| 7 | `actual_close_date` | `str` (ISO) | 2 | **NEW (F-12)** — the achieved completion date, paired with Define's `target_date` |
| 8 | `lessons_learned` | `str` | 2 | Feeds the case index (§23.3) |
| 9 | `transferability` | `str` | 2 | Yokoten — feeds `rag_lookup_case_history` (§24) |
| 10 | `project_signoff` | `str` | 2 | Champion + Belt + Finance |
| 11 | `secondary_metrics` | `str` | 2 | Final re-check |
| 12 | `issues_and_barriers` | `str` | 1 | Always last |

`ControlOutput` = these twelve **+** `phase_metrics` (§39.5.3) **+** the four
gate-metadata fields (§40).

> **`actual_close_date` is Tier 2 (F-12)** — a slipped date does not invalidate
> the improvement (the same logic that makes Define's `target_date` a planning
> parameter, §39.1.2). It is the paired value Control captures against Define's
> planned `target_date`.

#### 39.5.3 The metric registry, the comparison, and single authority (closes F-14)

Control closes the measurement thread. Its `phase_metrics` entry carries the full
per-metric comparison — the AFTER value against the Define target and the Measure
baseline:

```
phase_metrics = [
  {name: "invoice_error_rate", baseline: "12.3%", target: "<3%",
   actual: "2.8%", delta: "-9.5pp", met: "yes", source: "after"},
  {name: "invoice_cycle_time", baseline: "2.6 days", target: "<1.5 days",
   actual: "1.4 days", delta: "-1.2 days", met: "yes", source: "after"}
]
```

**F-14 recommendation — how N comparisons present and grade:**
- **`phase_metrics` is the authoritative store of all N comparisons**, one entry
  per registry metric, each carrying `baseline` (from Measure), `target` (from
  Define `target_value`), `actual`, `delta`, `met`. This is where a multi-metric
  project shows every Y closed.
- **`post_improvement_metrics` (Tier 1, dict) is the primary metric's deterministic
  link** back to Measure's `baseline_mean`, carrying `references_metric_name` (the
  uniform S-C32 shape, 43c4201). It is the gate-blocking link (§42, B2).
- **Single-authority invariant** (as Measure, §39.2.3): the primary metric's
  `phase_metrics` `actual` **equals** `post_improvement_metrics`'s value — a
  mismatch is a wiring defect. Additional metrics live only in `phase_metrics`.
- **The grader grades every entry**, not just the primary: a project that met its
  primary metric but silently missed a secondary criterion has not fully
  succeeded, and `phase_metrics` is where that shows.

#### 39.5.4 Two movements — confirm it held, then lock it in

*Control's methodology core (parallel to §39.3.4 / §39.4.4).*

**Movement 1 — confirm (did it hold?).** Measure the improved process and compare:
`post_improvement_metrics` against the Measure baseline, `phase_metrics` against the
Define target. Re-check **stability before capability** (§39.5.6) before running
`post_improvement_cpk`. Output: `post_improvement_metrics`, `improvement_delta`, the
per-metric comparison. **A Control phase that cannot show before→after on the same
measure has demonstrated nothing** (§42, B2) — this is the thread closing.

**Movement 2 — lock (make it stick).** Build the five-part `control_plan` and hand
the process over. The bright line: **a control plan written is not a control plan
delivered.** The most common real Control failure is a training plan authored but
never run (§41, B1) — so the grader checks all five sub-plans are populated, and
`handover_documented` names an owner who has actually accepted.

#### 39.5.5 Tools bound to Control

Passed to the executor via `tools=` on `create_agent` (§18). The count is owned
by the live bind (§39.1.10), under the 16 cap (§30).

- **The universal eight** (§29.2) — `propose_template` carries the control-plan,
  SOP and reaction-plan templates; `propose_diagram` renders the control charts.
- **Five computation tools** (§30 binding; specified §69), standard SPC names kept:

| Job | Tools | Use |
|---|---|---|
| Variable control limits, subgroups | `xbar_r_chart_limits` | Monitoring plan, batched measurements |
| Variable control limits, one-per-period | `imr_chart_limits` | **The default for service/transactional data** (§30) — do not invent subgroups |
| Attribute limits, proportion | `p_chart_limits` | Defect-rate monitoring |
| Attribute limits, counts | `c_chart_limits` | Defect-count monitoring |
| Capability held | `post_improvement_cpk` | The improved process's capability — **after** a fresh stability check |

Run under the seven-step pattern (§43.1). SKILL.md `allowed-tools` MUST equal this
subset (§32). The chosen chart type feeds the `monitoring` sub-plan of `control_plan`.

#### 39.5.6 Conditions — guards, routing, gate

**Three methodology guards** (Control's sequence locks):

1. **Link back to the baseline (Tier 1).** `post_improvement_metrics` references
   Measure's `baseline_mean` by lookup (§42, B2) — the only Tier-1 cross-phase
   reference in the system, because a result that cannot be tied to the baseline
   proves nothing.
2. **The control plan must be complete AND delivered.** All five sub-plans
   populated (§41, B1); `handover_documented` names an owner who accepted — a plan
   on paper that no one runs is the phase's classic failure.
3. **Stability before capability, again.** `post_improvement_cpk` runs only after a
   fresh stability check on the improved process — the same lock as Measure's
   `calculate_cpk` (§39.2.6). A capability figure on an unstable new process is as
   meaningless here as it was at baseline.

**Routing conditions** — the five-node cycle (§13), `Command`-routed (§15). Control
is the terminal phase: on gate pass, `gate_apply` populates
`SupervisorState.final_output` through Control's output mapper (§5, S-C31 B3), and
the supervisor's static edge runs to `END` — there is no next phase.

| Where | Condition | Goes to |
|---|---|---|
| `planner` (S-F13 DP1) | current field incomplete, or more remain | `executor` (`field_index++`) |
| `planner` | all 12 captured | `validation_stack` |
| `validation_stack` | 2b presence of the **3 Tier 1** + 2d `CONTROL_RUBRIC` pass | `gate_review` |
| `validation_stack` | fail | `planner` (+ `validator_feedback`); `gate_attempts ≥ 3` → escalation (§38) |
| `gate_apply` | Belt approve | populate `final_output` → `END` (project complete) |
| `gate_apply` | Belt reject | `planner` (+ `rejection_feedback`) |

**Gate-pass condition:** the 3 Tier 1 fields present and `CONTROL_RUBRIC` clears;
the 9 Tier 2 fields warn only, a skip recorded in `acknowledged_gaps` (§35).

#### 39.5.7 State parameters — Control's use of `PhaseState`


*Indexes §6 / §58.2 — **S-C02**; nothing re-defined.* **There is no `ControlState`.** Control uses the shared `PhaseState`; this table is its USAGE — which Control field each shared field carries, and who reads it:

| PhaseState field | In Control |
|---|---|
| `artifacts` | the 12 captured fields + `phase_metrics` + `computation_results` |
| `field_index` | walks the §39.5.2 list (0–11) |
| `computation_results` | the control-chart limits and `post_improvement_cpk` run; the grader scans for the chart-type evidence behind the monitoring sub-plan |
| `final` / `final_output` | on gate pass, Control's mapper writes `SupervisorState.final_output` — the project's terminal artifact (§5, B3) |
| `gate_attempts` | Control's own retry counter, cap 3 |
| `uploads` | post-improvement data, signed control plan, sign-off record |

#### 39.5.8 Metric literacy — what each metric and statistic means

New requirement (§32/§43.7), Control instance. The coach teaches, in plain
language (§50):

- **The metric** — echo its Define `meaning`; frame the closure ("your error rate
  started at 12.3%, you targeted under 3%, and it's now 2.8% — here's how we keep
  it there").
- **The statistic** — the seven-step *educate* step (§43.1 step 1) for **control
  limits** and the improved **Cpk**. *"Control limits are the voice of the process —
  the range it naturally runs in. A point outside them is a signal to act, not
  noise to ignore. That's what your monitoring plan watches for."*

Never a raw dump (§43.1).

#### 39.5.9 Gate, storage, progress view

- **Three Tier 1 fields block** the gate (§35) — the smallest Tier 1 set. Nine
  Tier 2 warn only — the largest Tier 2 set, because Control is rich in
  best-practice closure steps the Belt should be coached toward but not gated on.
- **The live gate document** (§50) renders the before→after comparison per
  `phase_metrics` `name`, the control charts via `propose_diagram`, the five-part
  `control_plan` as a table, and `computation_results` with interpretation.
  Narrative from captured field text + `computation_results` + `phase_metrics` —
  never `CoachingResponse` turn fields (§50, WATCH 9).
- **Two progress bars**, Tier 1 and Tier 2.
- Written **once** to `store/projects/{case_id}/artifacts/control.json` by
  `gate_apply` (§9, §33); this write **also** finalises the project (§5).

#### 39.5.10 The SKILL.md content (AUTHORITATIVE during the refactor)


> **Authority: THE FILES, not this section.**
> `skills/dmaic-control-phase/coaching_script.md` is the script and
> `skills/dmaic-control-phase/SKILL.md` is what ships and must contain it
> verbatim; on conflict the files win. `verify_built.py`'s *phase scripts
> byte-matching* check compares the two files. The per-field coaching pattern is
> §39.1.7's; the seven-step tool pattern is §43.1. Control's script closes the
> project (there is no next phase).

#### 39.5.11 Cross-phase reads and writes — the thread closes here

**Reads across the whole project:**
- **Define**: `metric_definitions` (registry), `target_value` (**what actual is
  compared to**), `target_date` (paired with `actual_close_date`),
  `calculate_expected_savings` result (the estimate `financial_impact_verified`
  confirms).
- **Measure**: `baseline_mean` and `phase_metrics` (**what `post_improvement_metrics`
  references** — the before values), `stability_assessment` (the method to re-run).
- **Improve**: `selected_solution` (**what is now in place to hold**),
  `implementation_plan`, `pilot_result` (the expected effect the actual confirms).

**Writes**: the 12 content fields, `phase_metrics` (the closing comparison),
`post_improvement_metrics` (with `references_metric_name`), and — on gate pass —
`SupervisorState.final_output` (§5).

#### 39.5.12 The measurement thread, closed

Control is the last phase; there is no §39.6. The thread that opened in Define is
now closed end to end, and it is traceable by one key across all five gate
documents:

```
Define    metric_definitions + target_value        — the metric named, the target set
Measure   phase_metrics.baseline_mean               — the before value, measured
Analyse   phase_metrics (root cause explaining it)  — why it was where it was
Improve   phase_metrics.pilot_effect                — the fix, proven in pilot
Control   phase_metrics.actual vs target            — the after value, the gain locked
```

**Define, Measure, Analyse, Improve and Control are all ratified. The five-phase
DMAIC specification is complete.**

---


## 40. The five `{Phase}Output` schemas


*Supersedes: REFACTORING §18, §82; ARCHITECTURE.md §4.10.2, §4.10.3; CLAUDE.md §10.7.*
**Status: RATIFIED.** File: `phases/{phase}/schema.py`. **Canonical home.**

**Every field is `str`** except the cross-phase reference dicts and the three
structured dicts (§41). **Every schema carries the same four gate-metadata
fields.**

**Specification:** the five schemas are **§63.1–§63.5 — S-C27 to S-C31**. The field counts,
gate-metadata sourcing and cross-schema rules below stay here.

**A schema is not the same list as the coaching order.** §39.1.2 gives Define's
**coached** sequence — the thirteen elements the planner walks by `field_index`.
`DefineOutput` is those **plus** the fields captured inside a position, the
registry's `phase_metrics` and the four gate-metadata fields, which are assembled
rather than coached (count: `DefineOutput.model_fields`). **Reading a phase's coached
list as its schema drops the cross-schema invariants**, which is exactly what
the two-fields-on-all-five rule exists to prevent — and it is why Define now
coaches `secondary_metrics` explicitly (position 10) rather than assembling it
behind the Belt's back.

### Field counts

| Phase | Total | Gate-required | Tier 2 | `phase_metrics` | Gate metadata |
|---|---|---|---|---|---|
| Define | **18** | **13 — all of them, incl. `metric_definitions`** | **— (no Tier 2)** | 1 | 4 |
| Measure | **15** | 7 | 3 | 1 | 4 |
| Analyse | **14** | 4 | 5 | 1 | 4 |
| Improve | **14** | 4 | 5 | 1 | 4 |
| Control | **17** | 3 | 9 | 1 | 4 |

**`phase_metrics` is on all five schemas; Define also carries
`metric_definitions`** (§63.8), the registry itself, which no other phase holds.
**Define's 12-position coached walk is unaffected** — the registry is captured
inside position 5's conversation, where the Belt names their metrics (§39.1.9).

**Define's column reads differently on purpose.** Under Option A (§39.1.2) every
Define field is gate-required, so its "gate-required" count is its whole content
set rather than a tier within it. The other four rows are **Tier 1** counts.

### The four gate-metadata fields

On all five schemas, always from the same four sources:

| Field | Source |
|---|---|
| `computation_results` | `artifacts["computation_results"]` (§7) |
| `acknowledged_gaps` | `validation_stack.get_acknowledged_gaps()` (§35) |
| `citations` | `PhaseState.citations` (§6) |
| `uploads` | `PhaseState.uploads` (§6) |


### Three fields are on all five schemas

`issues_and_barriers`, `secondary_metrics` and **`phase_metrics`** — the third
added by the metric-registry ruling of 2026-08-26 (§63.9, S-C39), because a
metric is only traceable end to end if **every** phase records what it did with
it, including the phases that did nothing.

`issues_and_barriers` is gate-required everywhere; `secondary_metrics` is Tier 2
in the four tiered phases and **gate-required in Define** (§39.1.2);
`phase_metrics` is present on all five and carries `"none this phase"` rather
than an empty list where the phase engaged no metric (§63.9 B2). **Adding a
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

> **Define has no Tier 2 row.** Under Option A all 12 of its fields are
> gate-required, so `DefineOutput` assembly is **direct `artifacts["field"]`
> access throughout** and the `.get(..., "")` pattern never applies to it
> (§39.1.2, S-F28). The tiered access pattern above governs the other four
> phases.

**Gate assembly must reference every field in the schema.** A field in the
schema that assembly never sets is a field that silently never reaches the
Store.

---

## 41. Structured dict fields, and FMEA


*Supersedes: REFACTORING §68; ARCHITECTURE.md §4.10.5–§4.10.7; CLAUDE.md §10.8; DECISIONS §C5, §C6.*
**Status: RATIFIED.**

> **The metric registry is a fourth, narrow exception to §7's string law**
> (founder ruling 2026-08-26). `metric_definitions` (§63.8) and `phase_metrics`
> (§63.9) are `list[dict]` for **the same reason and in the same class** as the
> three cross-phase reference dicts: the grader traces a metric across phases by
> **key equality on `name`**, which prose cannot support. **Scalar values inside
> both stay strings** — the exception is the container, never the typing law.

**Three gate-required fields are structured dicts**, distinct from the three
cross-phase reference dicts of §7:

| Field | Phase | Sub-fields |
|---|---|---|
| `process_map_sipoc` | Define | `suppliers`, `inputs`, `process_steps`, `outputs`, `customers`, **`process_metrics`** |
| `detailed_process_map` | Measure | `steps`, `cycle_times`, `resources`, `value_vs_waste`, `measurement_points`, **`baseline_metrics`** |
| `control_plan` | Control | `documentation`, `monitoring`, `response`, `training`, `aligning_systems` |

### The grader checks every sub-field is populated

**A `process_map_sipoc` with four of six keys filled is the partial-map failure
the field exists to catch.** A Belt who maps steps 3–5 of a seven-step process
produces a project that cannot show improvement, because the baseline never
covered the whole thing.

**`process_metrics` and `baseline_metrics` are the two sub-fields that carry the
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
service or transactional DMAIC, where `driver_priority_summary` and `vital_few_drivers`
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

| Field | Phase | Tier | References | `references_metric_name` |
|---|---|---|---|---|
| `causal_hypothesis` | Analyse | 2 | Measure's `baseline_mean`, for a named metric | **Yes — §39.3** |
| `solution_linked_to_root_cause` | Improve | 2 | Analyse's `root_cause_statement`, for a named metric | **Yes — §39.4** |
| `post_improvement_metrics` | Control | **1** | Measure's `baseline_mean`, for the primary metric | **Yes — §39.5** |

**Only `post_improvement_metrics` is Tier 1**, and that asymmetry is
deliberate: a Control phase that cannot link its result back to the Measure
baseline has not demonstrated improvement at all, whereas an Analyse phase
without an explicit hypothesis link is weaker but not void.

**The grader verifies each link by lookup, not judgment** (§36) — it reads the
referenced phase's gate document from the Store and checks the named field
carries the named value.

**The lookup matches on `references_metric_name`, not on the bare scalar**
(2026-08-26, closing F-13). It resolves the referenced phase's `phase_metrics`
entry whose `name` equals `references_metric_name`, and reads the value from
**that entry**. **Reading the scalar directly is wrong on any multi-metric
project**: `baseline_mean` is only the *primary* metric's mirror (§39.2.3), so a
link about the second metric would silently resolve against the first and
compare two different things while looking verified. A reference that does not
name its metric fails the lookup rather than falling back (S-C32 B5).

---

## 43. The coaching method

> **NOT-MARKABLE:** **coaching method — methodology content, not code.** What a good coaching turn does is taught through the SKILL.md files (§32, marked per phase) and the prompts (§22). A probe can check that a file exists and matches its section; it cannot check that the method is sound.

*Supersedes: REFACTORING §42; ARCHITECTURE.md §3.4.2; CLAUDE.md §0.8, §8.2; DECISIONS §D1–§D5.*
**Status: RATIFIED.** Enforced by `COACHING_QUALITY_RUBRIC` every turn (§36).

> **v1.75 — ① Explain → ② Show → ③ Ask → ④ Confirm ARE MOVES CHOSEN BY CODE
> (founder, 2026-09-25).** Not yet taught → teach (①–③); answered, insufficient →
> challenge; answered, sufficient → read back and ask *"is this right?"* (④);
> confirmed → store and advance. **The model writes the words for the move; it
> does not choose the move.** Every step touching coaching behaviour carries a
> repeated-run consistency test in its Done-when (6.61's D7).

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

**Define's count is COMPUTED (v1.73)** — `define_progress`, thirteen positions
(v1.79), three fields captured inside positions 3, 4 and 5 — delivered in the prompt and written
into the reply's `progress` by the executor — the position AFTER the turn's
capture, on every turn (v1.74). The model states it; it never counts it.

| Stage | What happens |
|---|---|
| **A** | Orientation — context setting, phase purpose |
| **B** | Mandatory gate-required fields, one by one, show-first |
| **C** | Computation tools, seven-step pattern |
| **D** | Cross-phase references where applicable |
| **E** | Tier 2 fields — advisory, the Belt decides. **Empty for Define**, which has no Tier 2 (§39.1.2) |
| **F** | Gate readiness check (`check_gate_status()`) and submission |

### 43.4 The live gate document preview

**The coach shows the Belt the gate document as it fills in**, using
`check_gate_status()` output — what is captured, what is missing, and what the
final document will look like:

```
📋 Your Define Report (5 of 13 elements complete)

✅ Business Case: "Invoice errors cost ~€35k/month in rework..."
✅ Team: [4 members — Leader, Sponsor, Process Owner, 2 SMEs]
✅ VOC Summary: "Customer complaints focus on..."
✅ Problem Statement: "Invoice error rate at 12.3% causes..."
✅ Baseline: "12.3% of invoices contain pricing errors"
⬜ Project Scope: [not yet captured]
⬜ Goal Statement: [not yet captured]
⬜ Target Metric: [not yet captured]
⬜ Target Date: [not yet captured]
⬜ Secondary Metrics: [not yet captured]
⬜ Process Map (SIPOC): [not yet captured]
⬜ Issues & Barriers: [not yet captured]

We're on Step 6 of 13. Let's capture Project Scope next.
```

**Define shows one list, not two.** All 13 of its elements are gate-required
(§39.1.2), so there is no "optional" section to render and nothing the Belt can
consciously skip. The four tiered phases render their Tier 2 fields separately.

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

### 43.7 Metric literacy — the metric, and the statistic

**The coach teaches two different things and must not conflate them.** §43.1's
seven-step pattern educates on **the statistic** — what a Cpk or a p-value is,
before one is produced. **Metric literacy is the other half**: what the
project's own measure *is*, why it matters in this phase, and how to read a good
or bad value.

**For each metric in play** (`metric_definitions`, §63.8), the coach states:

| | |
|---|---|
| **What it is** | The operational definition, echoing the registry's `meaning` in plain language — not the metric's name restated |
| **Why it matters here** | What this phase does with it, and what a bad value would cost the project |
| **How to read it** | What a good value looks like and what a poor one implies — so the Belt can judge their own number rather than waiting to be told |

**Fires when the metric is first engaged in a phase**, not once per project: the
same metric means something different in Measure (is this baseline trustworthy?)
and in Control (did it move, and will it stay moved?).

> **This is why `meaning` is in the registry.** A metric named
> `invoice_error_rate` with no operational definition cannot be explained, cannot
> be collected against consistently, and cannot be re-read by a later phase
> without guessing. **The coach reads `meaning`; it does not invent one** — that
> would be authoring the Belt's definition, which §22 forbids.

**Required in every phase's SKILL.md** (§32). Applied in full to
`dmaic-measure-phase/SKILL.md`; the other four inherit it at their reviews.

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

**LangGraph ≥1.2.6 required, and MET** — steps 0 and 2 are native primitives at
that version, and the venv has satisfied the floor since step 2.3 (§1). The
pinned version lives in `requirements.txt`.

---

## 45. Timeouts and compensating actions

> **NOT-MARKABLE:** specified here, **marked at §44**, which records that only Step 0 (`TimeoutPolicy(run_timeout=45)`) is built and steps 1–6 are step 8.2.

*Supersedes: REFACTORING §49, §79; ARCHITECTURE.md §9.2; CLAUDE.md §3.6.*
**Status: RATIFIED.** The LangGraph floor these primitives need is met (§1).

### Per-node timeouts — required on every phase executor node

**Specification:** the registration is behaviour B3 of **§58.11 — S-F02**; the handler is
**§64.3 — S-F29**.

**`TimeoutPolicy` also accepts `idle_timeout`**, refreshed by progress signals,
alongside the wall-clock `run_timeout`. A bare number or `timedelta` is
accepted as a hard cap that is *not* refreshed. `run_timeout=45` is the
ratified value; `idle_timeout` is available if a long legitimate tool call ever
needs distinguishing from a hang.

> **STATUS, 2026-09-24 — step 6.52 B1, G-92. What is built, recorded so this
> section is not silently false; the rule that would bind it is a DRAFTED
> amendment in that commit's body, not applied.** The wall is still
> `run_timeout=45`. Beneath it, the executor's own soft budget
> (`EXECUTOR_SOFT_BUDGET`, 40 s, step 6.34) is now measured from **node
> entry** — the moment the wall starts — rather than from `agent.ainvoke`, and
> the three `rag_lookup_*` tools run their synchronous searches in worker
> threads, together, so they cannot hold the event loop that both timers need.
> Before this, two live turns on 2026-09-24 reached the wall and the Belt got a
> 500 (traces `01a0d215…`, `01a0d28e…`).

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
> Recorded in `agent-improve/docs/_archive/BIBLE_VERIFICATION_LOG.md` under *Not verified*. (archived to docs/_archive/; canonical: CLAUDE.md §0.10)

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
| `POST /gate` | Triggers the validation stack; for Define, the gate interrupt (§33.1, v1.83) |
| `POST /gate/decision` | Resumes from the interrupt — `decision: approve \| reject`, the element(s) and reason of a rejection (R6, v1.83) |
| `GET /cases`, `GET /cases/{id}` | Case records |
| `GET /registry` | Case registry |
| `POST /upload` | Belt evidence and artefacts — the only channel through which external data enters the system (§29.1). **Ratified 2026-09-08 (`DECISIONS.md` Part AP5): the route already existed and this table did not name it.** Parse, evidence/artefact routing and refusal behaviour are step 6.11 |

> **SPEC-GAP (G-47): this table is not what the tree serves.** Seven routes
> exist in `gateway/routes.py` and in neither this table nor S-F34's copy of it
> — `/health`, `/summarise`, `/context`, `POST /cases`,
> `/gate/review/{case}/{phase}` and `/files/{case}/{file}`. **v1.83 settles the gate's
> shape**: submission stays `POST /gate`, and ONE resume route carries the decision
> rather than two (`/gate/approve`, `/gate/reject` retired from this table). `/ask/stream`
> is NOT part of this gap — ratified, unbuilt, owned by step 10.1. Which of the
> seven are ratified, which are v1 residue due to die at 11.1, and whether `/gate`
> becomes three routes are founder questions.

**All of them invoke the same compiled graph object.**

### Envelopes are Pydantic v2

Request and response schemas live in `gateway/schemas.py` (§54).

---

## 50. UI and language rules

> **NOT-MARKABLE:** a parent whose CHILDREN own the facts. §16's convention — *“one marker per item, never one per section that mentions it”* — and a row here would be a second claim over the same ground. Its one child owns a row.

*Supersedes: REFACTORING §77; ARCHITECTURE.md §11; CLAUDE.md §13.*
**Status: RATIFIED.**

### 50.1 Coach response structure

*Validated against conversational-UX practice, 2026-08-25: dense LLM prose is a
named failure mode; structured, scannable, card-based responses are the
standard.*

**Coach responses are structured, never bulk prose.** Every coaching turn
presents as visually distinct sections, not a paragraph block:

> **v1.76 — BUILT at step 10.0.** The four blocks travel on the reply message's
> `additional_kwargs` (`coaching_blocks`), are declared on `AskResponse`, kept in
> `conversation_history`, and drawn by the UI's `renderTurn` in this order;
> the grader's warning travels the same way (`grader_warning`).

| Block | Carries |
|---|---|
| **Explanation** | What this deliverable is — 2–3 short lines |
| **Example** | The worked example, its own distinct block, **marked as illustration** |
| **Your turn** | The request to the Belt, distinct as the call to action |
| **Progress** | Where they are — "Define · field 4 of 10" — always visible |

**Reliability rule — schema-backed, not prompt-hoped.** `CoachingResponse`
carries these as **discrete presentational fields** (`explanation`, `example`,
`prompt`, `progress`), not one free-text blob (§20, S-C05).

**Prose one turn
and structure the next erodes trust**, and a prompt asking for structure
produces exactly that inconsistency; a schema field cannot be skipped. The UI
renders one block per field and never parses prose to find the boundaries.

**The example block is marked as illustration, every time.** A Belt who mistakes
the worked example for a finding about their own project carries that error
into the gate document, and the coach's own example is the most plausible-
looking wrong answer available to them.

**No jargon in the visible structure** (the rule below); technical terms appear
only as small grey secondary labels. **On mobile:** shorter sections, larger tap
targets.

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
percentage would read as 55% and imply otherwise. **Define is the exception and
renders a single bar** — all 12 of its fields are gate-required, so there is no
second population to separate out (§39.1.2).

**Every phase's live gate document renders `computation_results` inline**,
**grouped by `phase_metrics` `name`** when more than one metric is tracked
(§63.9) — the same key the tool call carried in `computation_results.inputs`
(§69.1), so a result and the metric it belongs to are joined by key rather than
by proximity. Each entry is shown **with its interpretation rather than raw
numbers** (§43.1 step 5) and with its chart via `propose_diagram` where one
applies. **This is a document-layout requirement on every phase's SKILL.md, not
an optional enhancement of any one phase's.**

**The document's narrative is assembled from captured field text, plus
`computation_results`, plus `phase_metrics`** (§40's gate-metadata sourcing) —
**never from `CoachingResponse`'s turn-level `explanation`, `example`, `prompt`
or `progress` fields** (§50.1, WATCH 9), which are ephemeral coaching UI. The
distinction is the whole point: `artifacts` is what the Belt committed and can
defend at a gate; those four fields are how one turn was presented and are gone
the moment the next turn renders. **A gate document assembled from presentation
fields would show what the coach said rather than what the project established.**

**The mirrored scalars are what the document shows for the primary metric**
(§39.2.3) — `baseline_mean` reads better in a quality record than
`phase_metrics[0]["baseline_mean"]`. **Additional metrics render from
`phase_metrics` alone**, since only the primary has a scalar. That the two agree
is guaranteed at assembly, not assumed by the renderer (S-F28 B2).

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

> **STATUS, 2026-09-24 — step 8.0's EXECUTOR SLICE, pulled forward by founder
> ruling ahead of its precondition 7.6.** `@traceable` spans now cover the
> executor's setup (`_build_executor`, the dispatched read, the prior-document
> read, `get_llm`), the knowledge lookups (variant call, each query in its thread,
> the RRF merge) and every direct Azure AI Search and embeddings call in
> `retriever.py`, each recording its HTTP attempts, statuses, 429s and backoff.
> **Still untraced, as this section requires:** the five `validate.py` files and
> field extraction. Recorded so the section is not read as met; no rule changed.

> **STATUS, 2026-09-24 — gap G-95. Spans are CHILD-ONLY; tests never trace.**
> The executor slice's spans now record only inside an already-traced run
> (`child_span` / `child_trace` in `core/tracing.py`); a span with no enclosing
> run is the bare call, not a root trace. The test suite never traces. Before
> this, standalone spans and test runs exhausted LangSmith's monthly trace quota
> and every trace since is refused (429) until the quota is restored — so
> *"every Define turn leaves a trace"* is currently unmet. Recorded, no rule
> changed.

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

**THE FLOOR IS THE RULE. THE PINS ARE NOT STATED HERE** —
`agent-improve/requirements.txt` carries every resolved version and is the only
place that does.

| Floor | Why it is a floor and not a preference |
|---|---|
| `langgraph >= 1.2.6` | **1.2.6 (2026-06-18) carries *"nested subgraph inherits parent `checkpoint_ns` (regression in 1.2.3)"*** — the fix §16 depends on. Node-level `TimeoutPolicy` and `error_handler` (§45) require 1.2+. Attributable to one release note, which is what makes it a floor rather than a preference |
| `langchain-core >= 1.6.0` | Required by `langchain` 1.x as resolved. The jump from the pre-2.3 venv was three minors and was that upgrade main risk |
| `deepagents` — EXCLUDED | **Still pre-1.0** — §18 exclusion stands, and it is not installed |

**`langchain-classic` retains legacy classes we do NOT use — presence is not
permission.**

**Do not upgrade to a version written in a document — re-resolve against live
PyPI** (`/verify-current-version`). That rule is the reason the floors above
name no current version at all.

**During the upgrade, sweep for imports from `langgraph.prebuilt`** —
deprecated, functionality moved to `langchain.agents` (§18). `langgraph-prebuilt`
is present as a transitive dependency and that is not a violation: CLAUDE.md §4.4
bans IMPORTING from it, not its presence.

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

**Until migration is complete the v1 architecture may still operate, but no
v1-style code may be ADDED.** A file is "migrated" when it is rewritten under
these rules and committed with a `refactor(arch-v2):` prefix.

---

# Part XI — Governance

---

## 54. Where code is allowed to live

> **NOT-MARKABLE:** **a placement rule, enforced elsewhere.** Where a class may live is checked by CLAUDE.md §2 at review time and by the commit-msg guard's mypy pass, not by a count. Marking it would claim a probe this file does not have.

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

Four mechanisms, layered:

| Layer | Mechanism | Enforces |
|---|---|---|
| **Constitution** | `{agent}/CLAUDE.md` + `.claude/rules/*.md` | **ADVISORY CONTEXT, not enforcement** (§55.5). The root loads at session start; the thirteen rule files load on READ of a matching path and were measured silent on Write, Edit and Bash. **Per agent** — see *Scope* |
| **Skills** | `.claude/skills/verify-current-version` | Version currency at decision time |
| **Hooks** | `.claude/hooks/pre-tool-use-drift-check.py` + `deprecated_patterns.yaml` | Deprecated patterns blocked before they land |
| **Gates** | `.githooks/commit-msg` → `.claude/hooks/commit-msg-refactor-guard.py` | **Six rules at the commit itself: 1, 2b, 3, 4, 5, 6.** Subject format; the BUILT-marker document staged with a watched path; mypy against the pinned venv; pytest; CONTINUITY.md current; and **rule 6 — a fix commit's body answers D2 IS, D2 IS-NOT, D4 OCCURRENCE, D4 ESCAPE, D5 FIX and D7 PREVENT** (`agent-improve/CLAUDE.md` §20 — every fix is an 8D) |

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

*Added 2026-08-23 with Part XII. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §S1.*

**Five rules, each stated with what would catch a violation of it.** A rule
whose enforcement is "nothing" says so, rather than being assumed covered —
that is the R2 discipline, and three separate findings in this project have now
been a correct rule paired with a check that could not see what it governed.

| # | Rule | What catches a violation |
|---|---|---|
| **1** | **Spec-before-code.** A code change requires its spec entry to be updated first | A code change whose spec entry's last-modified timestamp predates it. **Checkable in git; no automation exists yet** |
| **2** | **Flag-is-canonical, register-is-derived.** The DORA register never leads the per-entry AI-ACT flags; when they disagree the flag wins and the row is regenerated | Bidirectional: every register Risk ID must trace to a flagged entry, and every flagged entry must appear in the register. Grep on Risk ID |
| **3** | **SIPOC Supplier/Customer cross-check.** On a **peer runtime call edge**, the callee's Suppliers must list the caller and the caller's Customers must list the callee. **Scope is narrowed — see the note below this table** | Grep by entry name across Part XII, over peer runtime call edges only. **A non-closure is a defect only on such an edge**; the four excluded classes are not findings |
| **4** | **Define-once.** A class or function defined in Part XII must not have its schema or signature restated in an architecture section — those sections carry a `**Specification:**` pointer and keep their reasoning | A definition appearing in two section ranges. Grep for the class or function name followed by a definition token |
| **5** | **Selective flagging.** AI-ACT flags appear only on high-risk-surface entries — coaching output, gate approval, anything that could feed a competence, employment or certification decision | A flag on a pure utility, or a missing flag on a coaching, gate or assessment entry, is a review finding. **Judgment, not automation** — where classification is unclear the entry carries `AI-ACT-REVIEW: uncertain` rather than a guess |

> ### Rule 3's scope — narrowed 2026-08-24
>
> **The cross-check applies ONLY to peer node-to-node call edges** — one node or
> function invoking another at runtime. It **excludes**:
>
> | Excluded | Why it is not a caller relation |
> |---|---|
> | **Edges into class/schema entries** | A class is not a caller. `CoachingResponse` is passed, not invoked |
> | **Return paths** | The reverse of an edge already counted. The API surface invoking the graph is one edge, not two |
> | **Build-time / compile-time relations** | Graph wiring at construction is not a runtime call. `build_phase_subgraph` registering nodes is not calling them |
> | **Nested sub-component references** | A middleware hook inside a node, or a layer inside `validation_stack`, is not a separate caller |
>
> **A non-closure is a defect ONLY on a peer runtime call edge.** Everything
> else is out of scope and is not a finding.
>
>
> **Narrowing the scope is the resolution of finding F-07**: an 86%-noise check
> is a check whose failures stop being read.

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

### 55.2 The BUILT markers, and the paths that oblige a re-check

**Every numbered section owns a register row or declares `> **NOT-MARKABLE:**`
with its reason** (v1.66, step 6.40); a sub-section whose ANCESTOR owns a row is
covered by it. `verify_built.py` assertion 7 checks this. **A status marker sits
under the item it describes, never in a parallel table.**

| Marker | Means | Renders |
|---|---|---|
| ✅ built | exists and works as specified | **green** |
| ⚠️ built with a known defect | exists, and the defect is named on the same line | **amber** |
| ☐ not built | with the step that builds it | **grey** |
| ⛔ blocked | with what unblocks it | **red** |

> **ONE MEANING PER COLOUR, ACROSS THE WHOLE BOARD.** Ratified 2026-09-11 by
> founder ruling. The `Renders` column is not decoration — it is the half of
> the vocabulary a reader actually perceives first, and it was wrong in three
> places before anyone wrote it down:
>
> | Colour | Means | Where |
> |---|---|---|
> | green | exists and works | `DONE` lane · ✅ built |
> | blue | can start now | `READY` lane |
> | orange | in progress | `BUILDING NOW` — the cursor |
> | amber | live, and wrong | ⚠️ built with a known defect |
> | red | cannot proceed | `BLOCKED` lane · ⛔ |
> | grey | scheduled, not started | `QUEUED` lane · ☐ not built |
> | dashed | unmeasured | no marker exists — **not a pass** |
>
> **A pointer is not a state.** The board's `closes:` chip names the step that
> fills a hole; it used to take that step's LANE colour, which put green beside
> a `☐ not built` marker. It is neutral.
>
> **A G-NUMBER ON THE BOARD CARRIES ITS NAME** — CLAUDE.md §19.2, founder ruling 2026-09-11. Not `G-49` but **G-49 — the executor does not call the tool its own planner names**. The name is the first clause of that gap's own §66 row, **read at generation time and never typed**, so it cannot drift from the register. A bare code is legible only to a reader already holding the register it indexes, and the founder reading a finding is not holding it.

> **A MARKER NOTHING RE-RUNS IS A CLAIM.** `.claude/hooks/verify_built.py`
> re-runs the counting commands against the tree, against the pinned venv, and
> reports any marker that disagrees. **`pytest` runs it**:
> `backend/tests/test_built_markers.py` parametrises the table one test per
> check, so rule 4 of the commit-msg guard enforces every check on every spine
> commit and a failure names **which marker went stale**.
>
> **The check COUNT is pinned separately**, because parametrising over a list
> means deleting a check deletes its test and the suite goes green. It may only
> move in a commit that means to move it. **A check pins a VALUE or a SET, not
> only a POPULATION** — a count agrees with the tree whatever the items are.

> **Build status lives in `REFACTORING_PROCEDURE.md` Appendix F** (§56 amendment
> v1.64, step 6.31) — one row per step, a resolvable anchor in every row, and
> `verify_built.py` as a fail-closed referee. A marker here keeps the
> *rationale*; Appendix F carries *whether it exists today*. Migration is one
> marker at a time, by judgement; **a marker that still states a status is
> mid-migration, not authoritative.**

**Guard rule 2b requires the file carrying these markers staged whenever a
commit touches a path they tabulate.** Deliberately narrow — a guard that fired
on every backend file would be routed around inside a week:

```
agent-improve/backend/core/graph.py              supervisor topology, backstop
agent-improve/backend/core/state.py              SupervisorState
agent-improve/backend/core/substate.py           PhaseState, caps
agent-improve/backend/core/checkpointer.py       checkpoints
agent-improve/backend/core/store.py              Store namespaces
agent-improve/backend/middleware/**              §19's eight positions
agent-improve/backend/phases/subgraph_common.py  nodes, TimeoutPolicy
agent-improve/backend/phases/nodes_common.py     planner, executor, caps, guards
agent-improve/backend/knowledge/tools.py         the universal eight
agent-improve/backend/knowledge/computation.py   the twenty
agent-improve/backend/gateway/routes.py          §49's API surface
agent-improve/backend/storage/blob.py            system of record
```

> **A WATCHED PATH MUST BE A SOURCE OF TRUTH, NEVER THE OUTPUT OF A
> GENERATOR** (`docs/board.html` left this list on 2026-09-14; v1.57, v1.58).
> Enforced by `test_no_watched_path_is_a_generators_output`. **A derived file
> is verified by REGENERATING it and comparing** (`verify_built.py`), never by
> asking whether someone touched a different file in the same commit.

**Rule 2b binds on EVERY commit**, not only spine commits: a middleware swap
lands as a `fix(` as easily as a `refactor(`, and scoping it to the spine would
exempt exactly the commits nobody reviews against the plan.

### 55.3 The phase completeness set — what one phase actually traverses

**Machine-readable: `.claude/hooks/build_board.py` renders the per-phase view
from this table.** **A phase running end to end with a visible gate traverses
every row below** — the honest denominator for "is this phase done", not the
sections named after the phase.

| Group | Section | Scope | Measured at |
|---|---|---|---|
| In and out | `§49` | SHARED | — |
| In and out | `§50` | SHARED | — |
| In and out | `§53` | SHARED | — |
| Orchestration and persistence | `§5` | SHARED | `§57.2` |
| Orchestration and persistence | `§12` | SHARED | `§15` |
| Orchestration and persistence | `§15` | SHARED | — |
| Orchestration and persistence | `§16` | SHARED | — |
| Orchestration and persistence | `§8` | SHARED | — |
| Orchestration and persistence | `§9` | SHARED | — |
| Orchestration and persistence | `§10` | SHARED | — |
| Orchestration and persistence | `§11` | SHARED | — |
| The phase subgraph | `§13` | SHARED | — |
| The phase subgraph | `§14` | SHARED | — |
| The phase subgraph | `§6` | SHARED | `§58.2` |
| The phase subgraph | `§7` | SHARED | — |
| The coach | `§17` | SHARED | — |
| The coach | `§18` | SHARED | — |
| The coach | `§19` | SHARED | — |
| The coach | `§20` | SHARED | `§58.5` |
| The coach | `§21` | SHARED | — |
| The coach | `§22` | SHARED | — |
| What the coach knows | `§32` | SHARED | — |
| What the coach knows | `§43` | SHARED | — |
| What the coach knows | `§23` | SHARED | — |
| What the coach knows | `§24` | SHARED | — |
| What the coach knows | `§25` | SHARED | — |
| What the coach knows | `§26` | SHARED | — |
| What the coach knows | `§27` | SHARED | — |
| What the coach knows | `§28` | SHARED | — |
| What the Belt gives it | `§29` | SHARED | — |
| What the coach computes | `§30` | SHARED | — |
| What the coach computes | `§31` | SHARED | — |
| What the coach computes | `§69` | SHARED | — |
| Validation and the gate | `§34` | SHARED | — |
| Validation and the gate | `§35` | SHARED | — |
| Validation and the gate | `§36` | SHARED | — |
| Validation and the gate | `§33` | SHARED | — |
| Validation and the gate | `§37` | SHARED | — |
| Validation and the gate | `§38` | SHARED | — |
| The gate document | `§40` | SHARED | — |
| The gate document | `§41` | SHARED | — |
| The gate document | `§42` | SHARED | — |
| The gate document | `§63` | SHARED | — |
| Reliability | `§44` | SHARED | — |
| Reliability | `§45` | SHARED | `§44` |
| Reliability | `§46` | SHARED | — |
| Reliability | `§47` | SHARED | — |
| Reliability | `§48` | SHARED | — |
| Observability | `§51` | SHARED | — |
| Observability | `§52` | SHARED | — |
| The phase's own spec | `§39.x` | PHASE | — |

**`Scope`.** `SHARED` is machinery every phase runs; `PHASE` is per-phase. **A
SHARED item that is broken is broken for all five phases and is ONE defect,
not five** — it appears in every phase's row because every phase traverses it,
labelled so the count is not mistaken for five separate problems.

**`Measured at`** names the section carrying the marker where an item is
specified in one place and marked in another — §5's class is marked at §57.2,
§20's at §58.5. **Without it those rows would read UNMEASURED, which would be
false**: the item is measured, just not here.

**An item with no marker anywhere is UNMEASURED, and UNMEASURED is not a
pass.** A blank cell and a green cell look identical at a glance and mean
opposite things; the view renders them differently and the fraction counts
only what is actually built.

**The spec layer (§57–§65) is not listed separately.** Each S-C / S-F entry is
attributed to the section it specifies, so `S-C05` counts under §20 and
`S-F01` under §15. Listing the spec layer as its own group would count the
same obligation twice — once as the architecture and once as its spec.

### 55.4 Facts have one owner — the ratified minimum

**Status: RATIFIED 2026-09-13.** Founder ruling. Encoded as data at
`.claude/config/fact_owners.yaml`, read by `fact-ownership-guard.py` and
`drift-check.py`.

**FIVE ROWS OF EIGHT.** The table CLAUDE.md carries under *Facts have one owner*
lists eight classes of fact; **these five are ratified.** The rest are a
statement of intent until each is ruled, and a guard enforcing an unratified row
is a guard nobody trusts.

| Class of fact | Owner | How it is enforced |
|---|---|---|
| **Dependency versions** — every pin, and the floor | `agent-improve/requirements.txt` | guard + drift check |
| **State and output field names, counts and types** | the schema modules: `core/state.py`, `core/substate.py`, `phases/*/schema.py` | guard + drift check |
| **Middleware order** | the agent factory `_build_executor()`, and `test_the_declared_middleware_list_is_the_ratified_layering` | `verify_built.py` *middleware mounted*, and the test |
| **Coaching content** | the phase directories under `skills/` | drift check, by **containment** |
| **Banned patterns** | `.claude/config/deprecated_patterns.yaml` | the rule-number resolution sweep |

**Coaching content is enforced by CONTAINMENT, not by a count.** A governed
document carrying a verbatim run of a phase script has copied it. That check
exists because step 8 moved those scripts out of this document, and nothing
else would notice them coming back.

**The rule is CITE, NOT RESTATE.** A governing document naming one of these
values in prose creates a second copy that can drift; the September audit found
that every contradiction it turned up was of that shape. Naming the owner is
always permitted — *"`PhaseState`'s field count (`backend/core/substate.py`)"* —
and so is quoting a value **with** its owner cited on the same line, which is
what makes a correction readable.

> **THE VALUES ARE NOT WRITTEN HERE, AND THAT IS THE POINT.** This section names
> owners and no counts. `fact_owners.yaml` likewise declares *how to derive* each
> value and stores none. A registry of owned values would be the ninth copy of
> every fact it governs — the failure mode this section exists to end, rebuilt
> inside its own countermeasure.

**PENDING IS NOT A VIOLATION.** Where a declared owner does not exist yet —
`phases/*/schema.py` for a phase not built, a pin for a package not added — the
fact has no owner to cite and the guard reports **PENDING** rather than denying.
A check that goes red on correct behaviour gets switched off, which is the
lesson `verify_rule_triggers.py` learned on its first run against §2's
designation of `core/reliability.py`.

**CODE IS NOT A GOVERNING DOCUMENT.** A field count in a docstring or a comment
sits beside the definition it describes and moves with it; that is a use of the
owner, not a copy of it. The guard fires on `CLAUDE.md`, `ARCHITECTURE.md`,
`.claude/rules/**` and `docs/**` — and never on `docs/_archive/**`, which records
what was true when written.

### 55.5 The commit gates govern. The rule files are advisory context.

**Ratified 2026-09-14, on measurement rather than on design intent.** This
section exists because §55's own table implied the reverse, and three other
places in this document were written as though a rule file were a control.

**Measured 2026-09-14** — `.claude/logs/instructions-loaded.log`, plus direct
probes on files under live globs (`Write`, `Bash` append, `Edit` with no prior
read: no rule text delivered; `Read`: both matching rule files, in full).
**Path-scoped rules are delivered on READ.**

**WHAT FOLLOWS, AND WHAT DOES NOT.**

| | |
|---|---|
| **Governs** | The commit gates. `.githooks/commit-msg` → the guard's rules, and `.githooks/pre-commit`. They read the index and refuse. They cannot be unloaded, forgotten, or missed |
| **Advises** | The root `CLAUDE.md` at session start, and a rule file when a matching path is READ |
| **Does not reach the write path at all** | The thirteen rule files, during Write, Edit, and Bash-mediated edits |

**This is not a defect to patch and it is not a reason to distrust the rule
files.** It is a statement of what each layer can carry. A rule that must hold
regardless of whether anyone read it belongs in a gate; a rule that teaches,
explains, or bounds a judgment belongs in a rule file and is worth having even
when it loads late. **What must stop is writing a rule file as though it were a
control** — the §55 shape of a correct mechanism paired with a document that
claims more for it than it does.

> **Rule delivery at write time IS available, and it lands one step late.**
> Probed 2026-09-14: a `PreToolUse` hook returning
> `hookSpecificOutput.additionalContext` **does** reach the model, surfaced as
> *"PreToolUse:Write hook additional context"*. But it arrives **with the tool
> result** — after the write it fired on. So it can inform the next action and
> the correction, never prevent the edit. **Only `permissionDecision: deny`
> prevents**, which is what `fact-ownership-guard.py` already uses. Any design
> that moves rule text onto the write path has to choose between those two, and
> the choice is not a detail.

## 56. Amendment procedure

> **NOT-MARKABLE:** **governance procedure.** How this document is amended has no built form; §56.2's split (rule here, reasoning in the commit) is followed or it is not, and the commit-msg guard is what notices.

*Supersedes: CLAUDE.md §18.*
**Status: RATIFIED.** Reconciled 2026-09-13 against the topology the September
refactor produced — thirteen rule files, five ratified owners, seven skills.

This document and an agent's `CLAUDE.md` are amended only via:

1. **The ruling is recorded HERE** — in the section that owns the topic, **plus
   a `§56` changelog entry at the head of this file and an increment to the
   version line.** Rulings do not go to `docs/_archive/DECISIONS.md`; that file
   was archived on 2026-09-10 and takes no new entries.
2. **The rule change is committed to the file that HOLDS the rule** — the root
   `CLAUDE.md` or one of `.claude/rules/*.md`. Its own commit, `docs(rules):`
   prefix, no code alongside it.
3. **If the rule number is cited in `deprecated_patterns.yaml`, the registry is
   updated in the same commit** (§55, and CLAUDE.md §0.2).
4. **If the change touches a ratified owner (§55.4), the enforcement column is
   checked** — not assumed. Enforcement is not uniform across the five rows.
5. **If the material is REFERENCE rather than rule, it is amended in the skill
   that holds it**, not added back to the root.
6. **The commit body states the occurrence and the escape causes** (CLAUDE.md
   §20). An amendment is a fix to a rule, and rule 6 of the commit-msg guard
   applies on its own trigger.

### 56.0 What changed about amending, when the rules stopped being one file

> **NOT-MARKABLE:** the procedure for amending rules. **A rule about how rules change has nothing in the tree to be checked against** — its subject is this document, not the code.

**A rule number used to resolve in one document.** It now resolves in the root
`CLAUDE.md` **or** in one of thirteen files under `.claude/rules/`, and the
registry's citations must still resolve across both. That is the whole of
§0.2's invariant restated for the topology that exists:

```bash
python .claude/hooks/verify_rule_citations.py
```

**Three namespaces, not one.** The registry's messages cite `CLAUDE.md §x` for a
rule, `Reference §x` for a section of this document, and `EDUCATIONAL §x` for the
archived design review — and each resolves against a different corpus. A checker
that assumed one reported **six false failures on its first run**, every one an
`EDUCATIONAL` citation. Only `message:` fields are read: a §-number in a YAML
comment is prose about history, not text the hook quotes back.

**Renumbering is the dangerous edit, and it is more dangerous now than it was.**
A rule moved between files keeps its number and the citation still resolves; a
rule RENUMBERED breaks every citation silently, and there are now fourteen
places for it to hide instead of one.

> **What these three checks do not cover:** they are instruments plus
> spot-checks, never an exhaustive diff of the rule files against their
> sections. **RULED: NO EXHAUSTIVE SWEEP, AND NO STEP** (as G-55 for the citation
> back-catalogue). **The ratchet stands**: a rule touched from here on is checked
> against its section as part of touching it. Revisit with G-55, at step 11.2.

**Three checks stand behind this and each answers a different question:**

| Check | Answers |
|---|---|
| the rule-number sweep above | does every cited number still resolve? |
| `verify_rule_triggers.py` | does every `paths:` glob still match a real file? |
| `drift-check.py` | does every owned fact still agree with its owner? |

**A `paths:` glob that matches nothing fails silently** — the rule simply never
loads. That is not a hypothetical: thirteen rule files shipped at brief step 6
with globs rooted at `backend/**` when `.claude/` sits above `agent-improve/`,
and every one matched zero files.

### 56.0.1 Rule, reference, and owned fact — three destinations

> **NOT-MARKABLE:** the procedure for amending rules. **A rule about how rules change has nothing in the tree to be checked against** — its subject is this document, not the code.

An amendment goes wrong most often by putting the right content in the wrong
place, so the test is **what kind of thing is it**:

| It is… | It goes to | Because |
|---|---|---|
| a RULE that binds on code | the root, or the rule file whose `paths:` cover that code | it loads when that code is **READ** — not when it is written (§55.5) |
| REFERENCE read while doing a task | the skill for that task | it loads on invocation, not in every session |
| a VALUE some code or file owns | nowhere — **cite the owner** (§55.4) | a second copy is a copy that can drift |

**The third row is the one that keeps being got wrong.** Every contradiction the
September audit found was a document restating a value it did not own —
`PhaseState`'s field count, the evidence index's schema, the dependency pins,
the middleware order. `fact-ownership-guard.py` now denies the write; §55.4
names the five owners and how each is enforced.

### 56.1 A phase is one atomic unit — schema, validator, skill

> **NOT-MARKABLE:** the procedure for amending rules. **A rule about how rules change has nothing in the tree to be checked against** — its subject is this document, not the code.

**A phase's `schema.py`, `validate.py` and `SKILL.md` are ONE unit sharing one
field vocabulary. They are always rebuilt together, never independently.**

| File | Owns |
|---|---|
| `schema.py` (`{Phase}Output`) | The field **names, types, shape** |
| `validate.py` | Which of those fields are **gate-required** — gate-blocking (§35). For Define that is all 12 (§39.1.2) |
| `SKILL.md` | Coaches **those exact field names, in the planner's `field_index` order** (§39.1.2) |

**They share field names by construction.** If the SKILL coaches
`problem_statement`, the schema declares `problem_statement` and the validator
knows its tier.

**A mismatch does not fail loudly — it fails at the gate, one phase later.**
Capture writes `artifacts["problem_statement"]` while `{Phase}Output(**artifacts)`
has no such field, so assembly raises on a Belt who has done nothing wrong, at
the moment they approve. **Rebuilding one of the three without the others is a
§56-class violation**, not a tidiness preference.

**The capture path this protects**, end to end:

| # | Step |
|---|---|
| 1 | The coach's model call uses `response_format=CoachingResponse` (§20) |
| 2 | Captured values arrive in `fields_captured` — **shape guaranteed by the schema, truth NOT** (§40) |
| 3 | The executor **node** — not the LLM — writes them into `PhaseState.artifacts[field]` |
| 4 | They live in `artifacts` in flight, checkpointed each turn. The **planner reads `artifacts`** to know what is captured and which `field_index` is next (§6) |
| 5 | At the gate, `gate_apply` builds `{Phase}Output(**artifacts)` — Pydantic, **no LLM** — and writes it **once** to `projects/{case_id}/artifacts/{phase}.json` (§9, §33) |

**Middleware never captures.** `BeforeModelStateInjection` (`before_agent`)
injects prior `artifacts` into context *before* the call;
`ContradictionDetectionMiddleware` (`after_agent`) reads the coach's
`contradiction_flag` *after* it. **Both read; neither writes captured fields.**
A middleware that wrote to `artifacts` would put a second writer on the field
the planner reads to decide what to coach next.

**Never amend a rule "in passing" while making a feature change.**
Architecture changes are separate commits.

### What requires an amendment rather than a routine change

- An eighth `SupervisorState` field (§5), **any new field on `PhaseState`
  (§6) whatever category it is placed in**, or **any new field on
  `CoachingResponse` (§20)** — all three are load-bearing schemas.
- A new graph node type in a phase subgraph (§13)
- A new middleware, or any change to stack order (§19)
- A new LLM role (§21)
- A tool that pushes a phase past 16 (§30)
- Any index schema change (§23.5)
- **Rebuilding a phase's `schema.py`, `validate.py` or `SKILL.md` without
  the other two** (§56.1) — they are one unit and one field vocabulary
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

### 56.2 The rule lands here; the reasoning lands in the commit

> **NOT-MARKABLE:** the procedure for amending rules. **A rule about how rules change has nothing in the tree to be checked against** — its subject is this document, not the code.

**Founder ruling 2026-09-10.** Every amendment has two halves and they go to
different places:

| | Goes to | Why there |
|---|---|---|
| **The RULE** — what is now true, and what a build step is checked against | **This document**, as a §56 amendment with a version bump | Permanent, indexed, and the thing §55.1's cross-check can resolve |
| **The REASONING** — what was decided, what was rejected, what an audit found, what was deliberately left unfixed | **The commit message body** | Already required, already permanent, and tied to the diff it explains |

**A commit body is never re-read except when investigating that commit, and
that is the correct cost.** The moment you want the reasoning is the moment you
are already looking at the diff.

**`docs/_archive/DECISIONS.md` is CLOSED AND ARCHIVED** — frozen at Part AU,
2026-09-10. It is where the historical reasoning for Parts A–AU sits, and it
takes no new entries.

> **THE TEST FOR WHETHER SOMETHING IS A RULE:** would a build step be checked
> against it? Then it belongs here, in the section that owns the subject —
> never in a decision log, a tracker row or a status file.

### 56.3 The tree at HEAD is the only source of truth

> **NOT-MARKABLE:** the procedure for amending rules. **A rule about how rules change has nothing in the tree to be checked against** — its subject is this document, not the code.

**Ratified 2026-09-13.** The rule is `CLAUDE.md` §0.32 and binds always; this
section is the ruling behind it, and the reason it sits in §56 rather than in a
domain rule file. **An amendment procedure presumes a shared object to amend.**
§56.0.1 routes content by KIND — rule, reference, or owned fact — and every one
of those routes ends at a path. If two readers can disagree about what is at a
path, the routing decides nothing.

| The claim is made against | Verdict |
|---|---|
| the file at its repo path, read now | **The only admissible source** |
| a copy read earlier in the same session | Stale by construction — the file can move underneath it |
| a draft, a scratchpad, an artifact directory | Never evidence: no history, so nothing settles a disagreement |
| a synced mirror of the tree | **The most dangerous, because it looks complete** |

**The mirror row is why this is ruled rather than assumed.** This repository
lives inside OneDrive, and `.claude/` does not appear in that mirror — so the
rule files, the hooks and the skills read as absent from a seat that trusts it,
while `git ls-files` names them and `git ls-remote` confirms them on the remote.
That is the §55 failure shape one level up: **a correct artifact paired with a
view that cannot see it.** The countermeasure is not a better mirror. It is that
a claim resolves through git, or is not made.

**Two of the three clauses are gated at the commit** — §0.32 says what the guard
refuses, and `commit-msg-refactor-guard.py` owns the patterns and the
resolution. **The claim clause is NOT gated, and is not claimed to be.** A gate
reads the index; it cannot read a sentence. §20.5.1 already carries the
discipline that catches it — a claim about code quotes its lines with file and
number, a claim of absence carries the command and its output — and **G-57
carries the rest**: two enforcing rules with demonstrations and no test suite.

## 57. The specification layer — how to read and write a spec entry

> **NOT-MARKABLE:** reading instructions for the specification layer — how to write an entry, and two calibrated samples of one. **The entries it teaches you to read carry the rows**; teaching is not a second claim.

*Supersedes: none — new Part, ratified 2026-08-23. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §S1.*
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

Every marker has a row in the **§66 gap register** (now `docs/REFACTORING_PROCEDURE.md`
Appendix G), and every register row has a marker. **§66 carries the live count.**

### 57.1 The two calibrated samples

> **NOT-MARKABLE:** reading instructions for the specification layer — how to write an entry, and two calibrated samples of one. **The entries it teaches you to read carry the rows**; teaching is not a second claim.

**These two entries are the approved standard, transcribed verbatim from
`agent-improve/docs/_archive/SPEC_SAMPLES.md`.** Every other entry in this Part is built
to match one of them. They are also the canonical entries for their subjects —
`SupervisorState` is **S-C01** and `phase_executor` is **S-F04**; §58 points
here rather than restating them. (archived to docs/_archive/; canonical: ARCHITECTURE.md §57.1)

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

> **NOT-MARKABLE:** reading instructions for the specification layer — how to write an entry, and two calibrated samples of one. **The entries it teaches you to read carry the rows**; teaching is not a second claim.

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

> **NOT-MARKABLE:** reading instructions for the specification layer — how to write an entry, and two calibrated samples of one. **The entries it teaches you to read carry the rows**; teaching is not a second claim.

**§66 carries the live gap count, and the register carries the entry census**;
neither is restated here.

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
| **The gap register** | **§66** | the live count is in the register |

---

## 58. Spec — graph management

> **NOT-MARKABLE:** a parent whose CHILDREN own the facts. §16's convention — *“one marker per item, never one per section that mentions it”* — and a row here would be a second claim over the same ground. All 22 children own rows — the spec entries themselves.

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
from langgraph.managed import RemainingSteps
from backend.core.substate import merge_field_log   # declared in this module

class PhaseState(TypedDict):
    # ── identity, copied down by the input mapper (2) ────
    case_id:            str
    current_phase:      str

    # ── conversation plumbing (3) ───────────────────────────────
    messages:           Annotated[list[BaseMessage], operator.add]
    history:            Annotated[list[str], operator.add]
    phase_context:      str

    # ── content fields (18) ─────────────────────────────────────
    coaching_plan:      Optional[CoachingPlan]
    field_index:        int
    draft:              dict[str, Any]
    artifacts:          dict[str, Any]
    step_log:           Annotated[list[dict[str, Any]], operator.add]
    field_log:          Annotated[list[dict[str, Any]], merge_field_log]
    field_status:       dict[str, dict[str, Any]]   # v1.77 — ruling R5
    belt_edits:         dict[str, Any]
    turn_count:         int
    final:              dict[str, Any]
    gate_attempts:      int
    validator_feedback: list[dict]
    rejection_feedback: list[dict]
    citations:          list[dict]
    uploads:            list[dict]
    asks:               list[dict]
    hop_results:        list[str]
    synthesis_output:   Optional[dict]

    # ── engine-managed (1) ──────────────────────────
    remaining_steps:    RemainingSteps
```
**Twenty-three author-populated fields** (two identity, three plumbing, eighteen
content) **plus one engine-managed value — twenty-four declared.** The managed value
is **declared but NOT populated by the input mapper**; LangGraph's execution loop
supplies it. **Any new
field requires a §56 amendment, whatever category it is placed in.**

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `case_id` | `str` | The project identifier, **copied down from `SupervisorState.case_id`** at phase entry. Identical to the graph's `thread_id` and the first Store namespace segment. The single source of case identity for everything inside the subgraph | none | **input mapper only**, at the boundary | `gate_apply_node`'s Store write (S-F07); `phase_error_recovery` (S-F29) |
| `current_phase` | `str` | Which DMAIC phase this subgraph is executing, **copied down from `SupervisorState.current_phase`** at phase entry. The single source of phase identity inside the subgraph | none | **input mapper only**, at the boundary | `analyse_executor_node` (S-F09); `phase_error_recovery` (S-F29); `gate_apply_node`'s Store key (S-F07) |
| `messages` | `Annotated[list[BaseMessage], operator.add]` | The Belt↔coach conversation for this phase. Append-only; the only thing prose summarisation is allowed to compress (§19.3) | `operator.add` | input mapper seeds it; the agent loop appends | the agent loop; `SummarizationMiddleware` (§19.3) |
| `history` | `Annotated[list[str], operator.add]` | Breadcrumbs, one per node entry. Diagnostic only | `operator.add` | every node, on entry | debugging |
| `phase_context` | `str` | The framing this phase was entered with, composed at the boundary from the Store — the case record for Define, the prior phase's gate document for the rest. Never carried on parent state | none | **input mapper only** | planner; state injection (§19.1) |
| `coaching_plan` | `Optional[CoachingPlan]` | The strategy for the current turn — which field, which action, which retrieval mode. Transient: overwritten every time the planner fires, never queued | none (whole-object replace) | planner node | executor node |
| `field_index` | `int` | Which field within the phase is being coached | none | planner node | planner |
| `draft` | `dict[str, Any]` | This turn's extraction, before validation. Structured, never prose | none | executor node | validation stack; `gate_review` |
| `artifacts` | `dict[str, Any]` | Everything captured in this phase so far, keyed by field name. Values are strings, except the three cross-phase reference dicts and the three structured dicts (§7, §41). Also holds `computation_results` | none (merge by the writer) | executor, from `CoachingResponse.fields_captured`; `gate_apply`, applying Belt edits | planner, `check_gate_status()`, validation stack, gate assembly, state injection, the live gate document (§50) |
| `step_log` | `Annotated[list[dict], operator.add]` | The audit trail — HOW each thing was captured, as opposed to WHAT (§11). Dicts only; tuples are banned. Keyed deterministically | `operator.add` | validation layers, grader `on_evaluation`, the fallback chain | audit trail; written into the gate document |
| `field_log` | `Annotated[list[dict], merge_field_log]` | **WHEN each captured value changed, and what it was before** — §56 amendment, ratified 2026-09-21, built at step 6.33. One entry per change: `key`, `field`, `phase`, `turn`, `value`, `prior_value`, `timestamp`, `reason`. The first capture of a field is an entry, with `prior_value: None`; a re-statement of the value already held is not. **`turn` is the Belt-message count, not `turn_count`** — G-39 leaves that field's contract unstated and it is `0` on every coaching turn, so a key built on it would collide across turns | **`merge_field_log`** — upserts on `key`, so a replayed turn replaces its own entry (§11). The one channel whose reducer is not `operator.add`, and the only one where §11's deterministic key is enforced rather than merely recorded | executor node, from the same split the `artifacts` merge uses | the gate document's provenance; a reviewer asking what a value said before; `gateway/routes.py`, persisting it to `PhaseRecord.field_log` |
| `field_status` | `dict[str, dict]` | **Where each field stands — STORED, never derived** (v1.77, ruling R5, 2026-09-25). One entry per field: `status` — `not taught` → `asked` → `answered` → `confirmed` — plus `answer` and `messages` (the Belt's words so far) and, while `answered`, `pending` (the read-back awaiting confirmation and what a yes stores). Every field starts `not taught`; a field stored before 6.61 with no entry reads as `confirmed`. **Only code changes a status, at turn end** | none — replaced whole each turn | executor node, from `phases/moves.decide`'s after-change map | the planner (the current field is the first not confirmed); state injection (section 3); `gateway/routes.py`, persisting it to `PhaseRecord.field_status`; the input mapper, seeding it from the case record |
| `belt_edits` | `dict[str, Any]` | The Belt's corrections made at gate step 5. A different thing from `validator_feedback`, and must stay separate | none | `gate_apply`, from the interrupt resume payload | `gate_apply` |
| `turn_count` | `int` | How many coaching turns this phase has taken. Load-bearing: it is a component of the deterministic `step_log` key (§11) | none | executor node | planner; `step_log` key construction |
| `final` | `dict[str, Any]` | The approved gate document. A `dict` and never a `str`, so a resumed graph can read what was approved without re-reading the Store | none | `gate_apply_node` | output mapper; crash recovery |
| `gate_attempts` | `int` | The shared retry counter for the four-layer validation stack. Per phase, in the checkpoint — never in route scope | none | validation stack increments; `gate_apply` resets to `0` | validation stack; the escalation edge at `>= 3` |
| `validator_feedback` | `list[dict]` | Accumulated per-attempt validation failures, each recording attempt, layer, criteria failed and specific feedback. What makes the shared cap of 3 defensible | none (append by the writer) | validation stack appends; `gate_apply` resets to `[]` | the coach, on retry |
| `rejection_feedback` | `list[dict]` | The Belt's per-reject reasons at the gate — the stated reason plus the rejected edits as context. Read on the re-coaching turn so the coach addresses what the Belt actually objected to | none (append by the writer) | `gate_apply`, on a Belt reject; reset to `[]` by `gate_apply` when the gate passes | the planner (S-F03), on the re-coaching turn |
| `citations` | `list[dict]` | Sources the coach cited this phase — `source`, `page`, `content_summary`, `turn`, plus **`blob_path` and `content_digest`** (**RATIFIED 2026-09-09 — NOT YET APPLIED**; Part AQ). The first four identify a passage; **none identifies the FILE underneath**, so a citation could not tell that its source had been replaced and §37 / step 7.6's cascade had nothing to compare. The anchor turns supersession from something the system records into something it can detect | none (append by the writer) | executor, from `CoachingResponse.citations` | gate document assembly |
| `uploads` | `list[dict]` | Files the Belt uploaded this phase — `evidence_index_id`, `filename`, `phase`, `uploaded_at`, `summary`, **`role`**, **`shape_match`**, **`content_digest`**, `blob_path`, **`consumed_at`** (**RATIFIED 2026-09-09 — NOT YET APPLIED**; set when a citation or a load references the document. **`None` at a gate on an upload bound to an open ask means the Belt supplied evidence and the coaching proceeded without it** — undetectable without the field, which is why it is specified here rather than at Stage 7; Part AQ), plus `ask_id` and `version` — **both RESERVED FOR STEP 6.12**: declared at 6.11, written `None`, filled by the ask-binding (Part AP5). An empty list means the phase reached its conclusions from typed statements alone | none (append by the writer) | the upload handler — **see G-36** | gate document assembly; evidence context |
| `asks` | `list[dict]` | **The coach's recorded requests for data** — `ask_id`, `role` (§23.2.1's vocabulary), `expected_shape` (columns, units, period, from the SKILL.md worked examples), `phase`, `asked_at`, `status`. **RATIFIED 2026-09-09 — built at step 6.12** (§56 amendment; Part AR). An ask is the **logical identity** of a document and files are its versions (ruling AP2.2), so the binding is recorded when the coach asks rather than inferred from a filename afterwards. **A system record, not a captured value** — which is why it is here and not in `artifacts` (§6) | none (append by the writer) | the executor, when the coach requests data | the upload route, resolving an arriving file; the planner (S-F13), routing on an unconsumed ask; `BeforeModelStateInjection` (S-C11), for the manifest |
| `hop_results` | `list[str]` | Ordered answers from a planned multi-hop chain. `[]` on every single-hop turn. State rather than a node local, so LangSmith can see it and a resume does not lose it | none | `analyse_executor_node` | the synthesis call; the LangSmith state view |
| `synthesis_output` | `Optional[dict]` | The dedicated synthesis call's `SynthesisOutput`, dumped. `None` on single-hop turns | none | `analyse_executor_node` | the coach call |
| `remaining_steps` | `RemainingSteps` (managed) | Live per-turn hop budget, = `recursion_limit` − steps taken. Read by the executor entry guard; the graceful off-ramp that keeps a Belt from ever seeing `GraphRecursionError` | none (engine-managed) | LangGraph execution loop, **not user code** | `analyse_executor_node` entry guard (S-F09) |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | a phase subgraph is entered | populate the **twenty-three author-populated fields** from the input mapper; no field SHALL be left undeclared. **`remaining_steps` is the one declared field the mapper SHALL NOT populate** — it is engine-managed, `NotRequired` in intent, and LangGraph's execution loop supplies it | §9 |
| B2 | the planner fires | replace `coaching_plan` entirely; it SHALL NOT be appended to or queued | §6 |
| B3 | a validation layer fails | increment `gate_attempts` by one and append one entry to `validator_feedback` | §34 |
| B4 | the gate passes | reset `gate_attempts` to `0` and `validator_feedback` to `[]`, and only `gate_apply` SHALL do so | §33.2 |
| B5 | a turn is single-hop | leave `hop_results` as `[]` and `synthesis_output` as `None` | §26 |
| B6 | any node writes `draft`, `belt_edits` or `final` | write a `dict`; a `str` SHALL never be assigned to any of the three | §6 |
| B7 | `coaching_plan` is read | read it by attribute (`coaching_plan.retrieval_hops`), never by subscript | §6 |
| B8 | a phase subgraph is entered | copy `case_id` and `current_phase` down from the parent `SupervisorState`, and take them from **no other source** — not config, not a build-time constant | §5, §9 |
| B9 | any node inside the subgraph runs | treat `case_id` and `current_phase` as **read-only**; no node SHALL return either key in its state-update dict | §5 |
| B10 | a Belt rejects at the gate | `gate_apply` SHALL append one entry to `rejection_feedback` and route to the planner; it SHALL NOT merge that entry into `validator_feedback` | §33, S-F13 |
| B11 | a coaching turn captures a field whose value differs from the one `artifacts` holds | append one `field_log` entry keyed `{phase}:{turn}:{field}`, carrying the new value, the prior value (`None` on a first capture) and the timestamp. A capture that re-states the value already held SHALL NOT produce an entry | §6, §11 |
| B12 | a node returns `field_log` | return THIS TURN's entries only; the channel's reducer SHALL fold them onto what is already held, and no node SHALL assign the whole log | §6 |
| B13 | a capture arrives with an empty value — `None`, `[]`, `{}`, or a blank or whitespace string | REPORT it by field name and leave the prior value standing; it SHALL NOT enter `artifacts`, SHALL NOT be written to the case record, and SHALL NOT produce a `field_log` entry. **The log that counts captures and the write that stores them must agree** (step 6.33, G-78) | §6, §7 |

**Invariants:**
- `validator_feedback` (what the system said about the AI's output at step 2)
  and `belt_edits` (what the Belt corrected at step 5) are **two actors at two
  moments** and MUST NOT be merged.
- `rejection_feedback` (why the Belt rejected at step 7) is a **third actor at a
  third moment** and MUST stay separate from both, for the same reason. Merging
  it into `validator_feedback` would have the coach read a Belt's rejection as a
  validation failure — the exact conflation the `feedback` field was split to
  end.
- `artifacts` (WHAT was captured), `step_log` (HOW a turn went) and `field_log`
  (WHEN a value changed, and from what) are **three** fields and MUST stay
  separate. Each answers a question the other two cannot.
- `artifacts` MUST be SEEDED at phase entry from the case record, never
  initialised to `{}`. A constant there is not a default but a ceiling: the
  input mapper is the only thing that builds `PhaseState`, so a blank
  accumulator means nothing captured can survive into a second turn (step 6.33,
  G-78 — the defect step 6.11 fixed one field over, on `uploads`).
- `gate_attempts` MUST be in the checkpoint. Holding it in route scope is the
  specific defect this placement fixes (§6).
- Every captured value in `artifacts` is a `str`, except the three cross-phase
  reference dicts (S-C32) and the three structured dicts (S-C33).

**The copy-down invariant — `case_id` and `current_phase`:**

> **Both fields are COPIED DOWN from the parent by the input mapper at phase
> entry. They are READ-ONLY within the subgraph and are never written back up.**
> `SupervisorState.current_phase` remains authoritative and keeps its single
> writer, the output mapper (§5). **This is a boundary-time copy, not a second
> writer, and it does not violate the single-writer rule** — the parent field
> and the child field are two fields on two schemas, and the child's is derived
> from the parent's exactly once, at entry.
>
> **Why copied rather than read from elsewhere.** Phase-internal code takes case
> identity and phase from its own state, and from nothing else. Reading
> `case_id` from config while taking phase from a build-time constant is what
> made G-03 latent: three functions read three different notional sources, none
> of which was declared, and nothing could see the disagreement.
>
> **What catches a violation** (§55.1 rule 5): **grep every node's return dict
> for `case_id` or `current_phase` as a key. Any hit is a violation.** Node
> returns are dict literals (§14), so the keys are greppable at their write
> sites.

**Failure modes:**
- A missing key in `artifacts` at gate-required assembly is **correct behaviour**
  — Layer 2b should have blocked the gate, so the `KeyError` must surface
  (§40.1).
- `coaching_plan` is `None` before the planner's first turn; readers MUST treat
  `None` as "no plan yet," not as an error.

> **SPEC-GAP (G-05):** `extracted_entity` is read off this state by
> `analyse_executor_node` (§26). It is not a declared field and no writer is
> named anywhere — to be designed with founder.

> **SPEC-GAP (G-06):** `extraction_error` and `extraction_incomplete` are
> written into this state by `phase_error_recovery`'s `Command(update=...)`
> (§45). Neither is a declared field — to be designed with founder.

> **SPEC-GAP (G-39):** `turn_count`'s increment contract — when it advances, by
> whom, and by how much — is unstated. It is load-bearing in §11's
> deterministic `step_log` key, so an ambiguous contract produces either
> duplicate or colliding audit entries — to be designed with founder.

### 58.3 S-C03 · Per-phase use of `PhaseState`

**Architecture:** §6 · **File:** `core/substate.py` · **Procedure:** step 6.20
*Rebuild test: there is nothing to rebuild — this entry declares an absence.*

**Purpose:** **To record that there are NO per-phase state classes.** All five
phases run on the single shared `PhaseState` (S-C02). What varies
by phase is which fields carry what, and that is §39.x.7 — usage, not
declaration.

> **RULING 2026-09-11: the five variants are NOT built, and will not be.** They
> were never specifiable — no phase's transient fields were ever enumerated
> (G-19, closed by this ruling) — and §7 had already ruled out per-phase typed
> destinations.

**A phase needing state that `PhaseState` does not carry is a §56 amendment to
S-C02**, adding a field every phase declares — the same rule as any other new
field. It is not licence to reintroduce a variant class.

### 58.4 S-C04 · `CoachingPlan`

**Architecture:** §6, §17 · **File:** `core/substate.py` · **Procedure:** step 6.1
*Rebuild test: reconstructable from this entry alone.*

**Purpose:** The planner's structured output — one plan per planner turn,
carried on `PhaseState.coaching_plan` and consumed by the executor. It is a
Pydantic model rather than a dict specifically so `retrieval_strategy` can
carry a `Literal` constraint: that field selects the executor's entire
retrieval path, and a typo would fall through silently to single-hop.

> **v1.77 (step 6.61):** the class below is the shape 6.61 built. The plan is
> BUILT BY CODE (`phases/moves.decide`); the planner model's only output is
> `SufficiencyJudgment`, and only when the Belt has answered.

**Definition:**
```python
class SufficiencyJudgment(BaseModel):      # the planner MODEL's one output
    verdict: Literal["sufficient", "insufficient", "not_an_answer"]
    reason:  str
    failed_criterion: Optional[str] = None   # R3 (v1.80): the element's criterion id an insufficient answer fails

class CoachingPlan(BaseModel):             # built in code, never by a model
    focus_field:        Optional[str]      # None once every position is confirmed
    status:             Literal["not taught", "asked", "answered", "confirmed"]
    move:               Literal["teach", "challenge", "read_back",
                                "store_and_advance", "respond"]
    judgment:           Optional[SufficiencyJudgment] = None
    answer:             str = ""           # the Belt's words for the field so far
    messages:           int = 0            # how many Belt messages `answer` spans
    pending:            Optional[dict] = None   # the read-back awaiting a yes
    store:              dict[str, Any] = {}     # what the Belt confirmed THIS turn
    stored_field:       Optional[str] = None
    statuses:           dict[str, str] = {}     # every position's status, AFTER this turn
    field_status:       dict[str, dict] = {}    # the after-change map the executor stores
    retrieval_strategy: Literal["single_hop", "multi_hop"] = "single_hop"
    retrieval_hops:     list[str] = []     # empty since 6.61 — no model writes them
```

**Produced by** `phases/nodes_common._plan_turn`, which calls
`phases/moves.decide`; the judgment is the builder-style structured-output call
on the `planner`-role model at temperature 0.1 — a plain model invocation, not
an agent, so `response_format=` does not apply (§21).

**Fields:**

| Field | Type | Meaning | Reducer | Writer | Readers |
|---|---|---|---|---|---|
| `focus_field` | `Optional[str]` | The field this turn's reply works on — for a store-and-advance, the NEXT field, which the same reply teaches. The executor may not choose a different one | none | planner node (code) | executor node (S-F04 B1); state injection (section 4) |
| `status` | `Literal[...]` | The focus field's status BEFORE this turn — not taught / asked / answered / confirmed, read from `PhaseState.field_status` (R5), never from a reply | none | planner node (code) | state injection |
| `move` | `Literal[...]` | THIS TURN'S MOVE, decided in code from the status (§17 v1.75). Replaces `next_action` | none | planner node (code) | executor node; state injection (section 4, authoritative) |
| `judgment` | `Optional[SufficiencyJudgment]` | The planner model's one judgment, `None` when none was needed | none | planner model | state injection; `step_log` |
| `answer` · `messages` | `str` · `int` | The Belt's own words for the field so far, and how many messages they span | none | planner node (code) | executor (the move record) |
| `pending` | `Optional[dict]` | The read-back awaiting the Belt's confirmation — NOTHING in it is stored | none | planner node (code); executor adds what a yes stores | state injection (section 3); the next turn, via the move record |
| `store` · `stored_field` | `dict` · `Optional[str]` | What the Belt confirmed THIS turn — the only values written to `artifacts` | none | planner node (code) | executor node |
| `statuses` · `field_status` | `dict[str, str]` · `dict[str, dict]` | Every position's status AFTER this turn's change, and the full map the executor stores — so section 3 and section 4 always agree (fix 2) | none | planner node (code) | state injection (section 3); executor node |
| `retrieval_strategy` | `Literal["single_hop", "multi_hop"]` | Which retrieval path the executor takes — the phase's §28 default since 6.61 (v1.77 (E)) | none | planner node (code) | executor node; `analyse_executor_node` |
| `retrieval_hops` | `list[str]` | Hop question templates for a planned multi-hop turn — empty since 6.61: no model writes them | none | planner node | `analyse_executor_node` |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the planner produces a plan | produce it through structured output, never by parsing JSON from raw model text | §21 |
| B2 | `retrieval_strategy` is `"single_hop"` | leave `retrieval_hops` empty | §17 |
| B3 | a new plan is produced | overwrite the previous one entirely; plans SHALL NOT accumulate | §6 |
| B4 | a plan is produced | derive `status` and `move` in code from the field's status; a model SHALL NOT choose the move (v1.77) | §17 v1.75 |
| B5 | the focus field is answered and the Belt's reply is not a plain yes | ask the `planner`-role model for ONE `SufficiencyJudgment`; in every other case make no model call (v1.77) | §17 v1.75 |

**Invariants:**
- The plan is transient; its consequences are durable. Captured values land in
  `artifacts`, sources in `citations`, the rationale in `step_log`, the
  exchange in the LangSmith trace. Nothing is lost when the next plan overwrites
  this one.
- Read by attribute, never by subscript.

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
    message:            str                 # transcript entry, appended to messages
    explanation:        str                 # §50.1 — what this deliverable is
    example:            str                 # §50.1 — the worked example block
    prompt:             str                 # §50.1 — the request to the Belt
    progress:           str                 # §50.1 — e.g. "Define · 4 of 10"
    fields_captured:    list[dict] = []     # [{field_name, value, source}]
    citations:          list[dict] = []     # sources referenced this turn
    contradiction_flag: Optional[dict] = None   # §37 — set only on a material
                                                # contradiction of a committed value
```

**`message` and the four presentational fields are not duplicates, and the
split is the point.** `message` is the **transcript** entry — it is what gets
appended to `messages` and what summarisation later compresses (§19.3).
`explanation` / `example` / `prompt` / `progress` are the **render contract**:
the UI draws one block per field, every turn, without parsing prose. Collapsing
them back into one field is what §50.1 exists to prevent; dropping `message`
would leave the conversation history with nothing to append.

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
| `message` | `str` | The turn's text as a transcript entry, appended to `messages` | none | the executor's model call | `messages`; `SummarizationMiddleware` (§19.3) |
| `explanation` | `str` | Plain-language "what this deliverable is", 2–3 short lines | none | the executor's model call | the UI, as its own block (§50.1) |
| `example` | `str` | The worked example, marked as illustration | none | the executor's model call | the UI, as its own visually distinct block (§50.1) |
| `prompt` | `str` | The request to the Belt — the call to action | none | the executor's model call | the UI, as the CTA block (§50.1) |
| `progress` | `str` | Position indicator, e.g. "Define · 4 of 10" | none | the executor's model call | the UI, always visible (§50.1) |
| `fields_captured` | `list[dict]` | Values the Belt supplied this turn. `value` is `Any`, deliberately: it must carry both plain strings and the three cross-phase reference dicts. **Its DESCRIPTION carries the declared shape of all NINE structured coached fields** — §56 amendment, 2026-09-23; see below | none | the executor's model call | the executor node, which writes each entry to `artifacts` |
| `citations` | `list[dict]` | Sources referenced this turn | none | the executor's model call | the executor node, which extends `PhaseState.citations` |
| `contradiction_flag` | `Optional[dict]` | Set only where the Belt materially contradicts a gate-committed value. `None` otherwise, which is the overwhelmingly common case | none | the executor's model call | `ContradictionDetectionMiddleware` (S-C10) |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | every coaching turn | be produced by the executor's `response_format=`, with no additional model call anywhere in the path | §20 |
| B2 | the Belt materially contradicts a gate-committed numeric or categorical value | set `contradiction_flag` with all five keys | §37 |
| B3 | the Belt rephrases prose, or refines a not-yet-committed current-phase value | leave `contradiction_flag` as `None` | §37 |
| B4 | a captured value is one of the three cross-phase reference fields | carry it as a `dict` in `value`, not a string | §7 |
| B5 | every coaching turn | populate `explanation`, `example`, `prompt` and `progress` as discrete fields — never one prose blob split by the UI | §50.1 |
| B7 | a value is returned in `fields_captured` | hold it as PENDING until the Belt confirms the read-back; store only the Belt's words or the tidied version the Belt confirmed (v1.75; built at 6.61) | §20 |
| B6 | a field has no meaningful worked example | still return `example`, saying so plainly, rather than folding the absence into `explanation` — the UI renders a block per field and an empty one is a layout break | §50.1 |

**Invariants:**
- **Adding a field to this schema requires a §56 amendment.** It is
  load-bearing in the same way `SupervisorState` and `PhaseState` are.
  **The four §50.1 presentational fields are optional (`default=""`, v1.64)** —
  a model omitting one must not fail the turn's structured output — **and an
  empty one is a finding**: `substate.py::presentational_gaps` names which came
  back empty and the executor logs it at WARNING. Whitespace counts as empty.
  `message` is deliberately not among them: a turn with no coaching text is a
  real failure.
- **Shape is guaranteed; content is not.** The four presentational fields are
  LLM-produced text and carry the same truth caveat as `fields_captured` (§40).
  A schema-valid `example` that misleads is exactly as well-formed as a good
  one.
- `value` is `Any` and this is the one place `Any` is correct. The values
  *inside* the reference dicts are still strings.
- Structured output guarantees the flag's shape and presence, never the
  correctness of the coach's judgment in setting it. §50's all-gate-fields tab
  is the documented human backstop.

> ### ⛑ `fields_captured`'s DESCRIPTION CARRIES THE DECLARED SHAPE
> ### §56 AMENDMENT, ratified 2026-09-23
>
> **Nine coached fields across the five phases are objects rather than
> strings** — §7's enumerated exceptions, S-C32's three cross-phase reference
> dicts and S-C33's three structured dicts, plus `team`, `metric_definitions`
> and `project_scope`. The description now names each with its keys.
>
> **The declared shape is part of the field's TYPE CONTRACT, not coaching.**
> This description is the structured-output contract the model receives on
> **every** turn, with nothing to fetch and nothing to choose.
>
> **IT IS A DESCRIPTION, NOT A TYPE CHANGE.** The ratified eight fields stay
> eight; `value` stays `Any`; **a per-phase response schema stays ruled out**
> and this is not one. What changed is what the model is told, on the one
> channel it cannot miss.
>
> **Enforcement is still at capture** (step 6.48): a value that is not the
> declared shape is refused and not stored, so this description makes the
> contract *reachable* rather than making it *enforced*. The two halves are
> what turn capability row 18 green, and neither does it alone.

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

**Architecture:** §10 · **File:** `storage/blob.py` · **Procedure:** step 3.5

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

> **SPEC-GAP (G-21) — RESOLVED 2026-09-01, procedure step 3.5: there is no class
> interface, and that is the resolution.** §54 and `CLAUDE.md` §2 name this file
> among those holding module-level functions ONLY; `ImproveBlobClient` was
> removed. The surface is fourteen module-level names (`download_bytes` joined
> them for S-F57's loader, because `_download` decodes UTF-8):
>
> | Kind | Names |
> |---|---|
> | sync | `case_path(case_id) -> str` · `storage_configured() -> bool` |
> | async | `load_case` · `save_case` · `create_case` · `write_phase_gate` · `append_turn` · `load_registry` · `save_registry` · `register_case` · `upload_file` · `aclose` |
> | const | `REGISTRY_BLOB_PATH` |
>
> **B2's sequencing:** `write_phase_gate` awaits `save_case` first, then
> `_update_registry_entry` — the registry must never point at a phase the case
> document does not yet show. Both are two separate writes covered by the node's
> `error_handler` (§45).
>
> **`write_phase_gate` MERGES into the phase record and is SAFE TO PERFORM
> TWICE** (step 6.42). `citations` and `uploads` default to `None`, meaning NOT
> SUPPLIED; the approval stamp is written on the TRANSITION only; `current_phase`
> is computed from the `phase` argument. **That is a framework requirement**:
> when step 7.3 moves this write behind `interrupt()`, every resume re-runs the
> node. **Lifecycle:** one cached `azure.storage.blob.aio` client, keyed on its
> event loop, closed by `aclose()` on `app.py`'s shutdown hook (Part Y).
>
> **Open, and not part of G-21:** deletion. No behaviour governs removing an
> uploaded blob, so blobs are orphaned when their case record drops them
> (WATCH 10).

### 58.9 S-C09 · `storage/models.py` — the record models

**Architecture:** §10, §23.3 · **File:** `storage/models.py` · **Procedure:** [tbd]

**Purpose:** The Pydantic models for the system of record: `CaseDocument`,
`PhaseRecord`, `RegistryEntry`, `PhaseSummaryRecord` (which feeds the five
`phase_summary_{phase}` fields of `improve_case_index`, §23.3), and
`UploadRecord`.

> **SPEC-GAP (G-51): `storage/models.py` defines ELEVEN models and this entry
> names six.** Unnamed: **`AnalystOutputRecord`, `CaseRegistry`, `ChartRecord`,
> `CitationRecord`, `TeamMemberRecord`.** Found 2026-09-11 by the three-way
> alignment audit, and it is the **same shape as Part AP6** — which found six
> `UploadRecord` FIELDS in the tree and in no document — one level up: AP6
> checked the fields of one named model and nothing checked the model list
> itself. `CaseRegistry` is the sharpest: `storage/blob.py`'s `load_registry` /
> `save_registry` return it, and `GET /registry` serves it, so a route this
> section's sibling §49 ratifies returns a model this section does not name.
> **Registered rather than fixed in passing** — which of the five are v1
> residue due to die at 11.1 and which are load-bearing is a founder question,
> and §8's rule is that a table is not amended while making a feature change.

**`UploadRecord` — the case-blob half of §6's uploads entry shape.** The §6 shape
a gate document reads is `evidence_index_id`, `filename`, `phase`,
`uploaded_at`, `summary` plus the two reserved fields; `phase` is the key this
record is stored under rather than a field on it, and the rest are here.
`to_phase_state_entry(phase)` is the single place the two shapes are reconciled.

| Field | Type | Meaning |
|---|---|---|
| `filename` | `str` | As uploaded. **Not an identity** — ruling AP2.2 forbids inferring anything from it |
| `blob_path` | `str` | `uploads/{case_id}/{filename}` |
| `uploaded_by` | `str` | Who uploaded it |
| `uploaded_at` | `str` | ISO 8601, server clock (§23.2) |
| `classification` | `str` | `purpose=<p> · <content_type> · <indexed\|pending>` |
| `rows` | `Optional[int]` | Row count from the deterministic parse. **Declared since before the refactor and written by nothing until 6.11** (Part AP1) |
| `role` | `str` | The document's function, from §23.2.1's vocabulary. **With `case_id` this is the LOGICAL IDENTITY** — supersession resolves on `(case_id, role)`, never on filename (ruling AP2.2). From the ask when solicited; from the Belt's declared purpose when not. **Built at 6.12** |
| `shape_match` | `str` | `full` \| `partial` \| `none` \| `unsolicited` — whether the file matched the ask's expected shape. **A mismatch is a coaching question, not a rejection**, so this records the answer and never blocks. **Built at 6.12** |
| `content_digest` | `str` | SHA-256 of the uploaded bytes — **VERSION IDENTITY**. The same bytes re-uploaded are not a new version; a different digest under the same role supersedes. **Built at 6.12** |
| `kind` | `str` | `evidence` \| `artefact` — **the destination, not the format** (ruling AP2.3). Evidence goes to `improve_evidence_index`; an artefact is what the team designed and does not, because one bucket would let a proposed future be retrieved later as a fact about the present |
| `evidence_index_id` | `Optional[str]` | The index document id. **`None` for every artefact, and for evidence whose indexing failed** — §6 names it as what makes the evidence trail traversable |
| `summary` | `str` | The interpretation's summary, lifted to the top level because §6's entry shape names `summary` and a gate document reads that shape |
| `interpretation` | `Optional[UploadInterpretation]` | The one model call the parse is allowed (ruling AP2.4), with its source citation (ruling AP2.6) |
| `refusal_reason` | `Optional[str]` | Belt-readable. The route refuses before persisting, so this is the belt-and-braces record for any later path that chooses to keep a refused upload |
| `consumed_at` | `Optional[str]` | **APPLIED at step 6.12** (was *"RATIFIED — NOT YET APPLIED"*; corrected 2026-09-11 — the field is on the model and `phases/nodes_common.py` stamps it). ISO 8601, set when a `load_evidence_series` call or a citation references this document. `None` means nothing has read it. Mirrors the §6 uploads entry (S-C02) |
| `ask_id` | `Optional[str]` | **RESERVED FOR STEP 6.12**, written `None` at 6.11 |
| `version` | `Optional[int]` | **RESERVED FOR STEP 6.12**, written `None` at 6.11 |

**`UploadInterpretation` is a nested model of it** — `summary`, `supports`,
`caveats`, `source_filename`, `source_blob_path`. The two source fields are
ruling AP2.6: §50's traceability binds on computed figures, not only
quotations, so a baseline derived from an uploaded extract must be followable
back to the file it came from.

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
  `RemainingSteps` inside the executor (§26), declared as an engine-managed
  value on `PhaseState` — S-C02.

### 58.11 S-F02 · `build_phase_subgraph(phase, llm)`

**Architecture:** §12, §13 · **File:** `phases/{phase}/graph.py` · **Procedure:** steps 4.1, 4.4
*Rebuild test: met for Define — the routing is designed (S-F13) and its DP1
predicate reads §39.1.2. Blocked for the other four phases until their field
lists land (G-27, G-28).*

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
| B4 | selecting tools | bind the universal eight plus that phase's computation subset, never more than 16 in total | §30 |

> **Resolved — G-01, see S-F13.** The intra-phase edges this function wires are
> the Level 2 `Command` routing; its DP1 predicate reads each phase's ordered
> field list (§39.x.2).

> **SPEC-GAP (G-33):** if `load_skill(name)` is a registered tool bound to the
> executor (§19.2, §32), it is an eighth universal tool and every phase count in
> §30 moves against the 16 cap. `UNIVERSAL_TOOLS` therefore has an undetermined
> membership — see S-F23.

### 58.12 S-F03 · `phase_planner` node

**Architecture:** §13, §17 · **File:** `phases/{phase}/nodes.py` · **Procedure:** step 6.1
*Rebuild test: met for Define (field order at §39.1.2); blocked for the other
four phases until their field lists land.*

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

> **Resolved — G-01 DP1, see S-F13.** The planner returns
> `Command(goto="executor")` to keep coaching and
> `Command(goto="validation_stack")` once every field is captured. **It owns
> this decision; the executor returns plainly** (§17). The *predicate* —
> "field complete", "more fields" — is evaluated against §39.1.2's ordered list
> (G-38, closed for Define 2026-08-25).

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
*Rebuild test: blocked on G-08 and G-34.*

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

> **Resolved — G-01 DP2, see S-F13.** Pass → `Command(goto="gate_review")`;
> fail under cap → `Command(goto="planner")` with `validator_feedback`; at the
> cap → escalation via `Command.PARENT`. **`gate_attempts` increments once, at
> entry** — a partially-run stack still costs an attempt. The escalation target
> name depends on G-34 (open).

### 58.15 S-F06 · `gate_review_node`

**Architecture:** §13, §33.1 · **File:** `phases/{phase}/nodes.py` · **Procedure:** step 7.3
*Rebuild test: blocked on G-18.*

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

> **Resolved — G-02, see S-F13 DP3.** This node interrupts and stops; it routes
> nothing. The Belt's decision is acted on by `gate_apply`: approve → `END`,
> **reject → planner carrying `rejection_feedback`**, with the reason mandatory.
> **The `/gate/reject` payload that must carry it depends on G-18** (open).

### 58.16 S-F07 · `gate_apply_node`

**Architecture:** §13, §33.1, §33.2, §40.1 · **File:** `phases/{phase}/nodes.py` · **Procedure:** step 7.3
*Rebuild test: blocked on G-08 and G-28.*

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
| **Input** | The resume payload → `PhaseState.belt_edits`; `PhaseState.artifacts`, `citations`, `uploads`; `acknowledged_gaps` (see G-08); `PhaseState.case_id` and `PhaseState.current_phase`, copied down at entry (S-C02) |
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

> **SPEC-GAP (G-28):** §40.1 shows gate assembly for `DefineOutput` only. The
> four remaining assemblies are unwritten, and §40 requires that assembly
> reference every field in the schema — see S-F28.

> **Resolved — G-02, see S-F13 DP3.** On reject this node returns
> `Command(goto="planner", update={"rejection_feedback": [...]})` — a new
> coaching turn carrying the Belt's stated reason, never merged into
> `validator_feedback` (S-C02 B10).

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
*Rebuild test: blocked on G-05 and G-35.*

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
    if state["remaining_steps"] <= 2:
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
| **Input** | `remaining_steps` (**declared, engine-managed — S-C02**), `extracted_entity` (**undeclared — G-05**), `PhaseState.current_phase` (declared, copied down at entry — S-C02), `coaching_plan.retrieval_hops` |
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
    """SupervisorState → PhaseState, for Define. Context is composed from the store,
    never carried on parent state. Define has no prior phase, so its source
    is the case record loaded at session start (§10)."""
    case = store.get(("projects", parent["case_id"], "case"), "record").value
    return {
        "case_id":            parent["case_id"],        # copied down — S-C02
        "current_phase":      parent["current_phase"],  # copied down — S-C02
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

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | The supervisor graph (S-F01), on entry to the Define subgraph |
| **Input** | `SupervisorState.messages`, `SupervisorState.case_id`; Store key `("projects", case_id, "case")/"record"` |
| **Process** | Reads the case record, composes `phase_context` as prose framing, and initialises every declared `PhaseState` field |
| **Output** | A complete `PhaseState` |
| **Customer** | `phase_planner` (S-F03), which reads `phase_context`; every node of the Define subgraph, which reads the initialised fields |

> **Resolved — see §16 (G-44).** The wrapper must invoke the subgraph directly
> with inherited config; never behind a tool.

#### Execution site — where a boundary mapper actually runs

**A mapper runs inside the parent's node function for that phase, not inside
the subgraph.** The parent registers one uniquely-named node per phase; that
node function calls the input mapper, invokes the compiled subgraph, and calls
the output mapper on the way back.

**This is the documented LangGraph pattern for the case at hand** — verified
against the current subgraph reference, 2026-08-24: when a parent graph and a
subgraph have different state schemas, the subgraph is invoked **inside a node
function**, which transforms parent state into subgraph state before invoking
and transforms the result back afterwards. `SupervisorState` and `PhaseState`
share no keys, so this is exactly that case.

**It does not add a sixth node.** §13's five-node rule governs the *subgraph*;
the mapper runs one level up, in the parent.

> **Stability condition, and it binds.** Checkpoint namespaces for
> subgraphs invoked inside node functions are assigned **by call order**, and
> reordering calls can mix up which subgraph loads which state. The documented
> remedy is to give each subgraph its own uniquely-named parent node — which
> the five phase nodes already satisfy, and which is now a reason they must
> stay uniquely named rather than an accident of readability.
>
> **The escalation edge is the one place order is not fixed** (§12, §38): it is
> reached by a conditional edge from inside a phase rather than by the static
> DMAIC sequence. It needs its own stable node name for the same reason, and
> that is one more thing G-34 must settle.

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | invoked | depend on `BaseStore` alone; it SHALL NOT be handed a blob client, and SHALL NOT read context off parent state | §9 |
| B2 | invoked | populate all nineteen fields explicitly | §6 |
| B3 | composing `phase_context` | compose it here, at the boundary; context SHALL NOT be carried on `SupervisorState` | §5, §9 |
| B4 | invoked | copy `case_id` and `current_phase` down from the parent, as their **only** writer | §5, S-C02 |

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
    """PhaseState → SupervisorState update, from Define. The gate document goes to the
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
| B4 | returning to the parent | **NOT return `case_id` or `current_phase`.** Both were copied down at entry and are read-only in the subgraph; returning either would create the second writer the copy-down invariant exists to prevent | S-C02 |

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
| B5 | an input mapper is invoked | copy `case_id` and `current_phase` down from the parent, as their only writer | S-C02 |
| B6 | an output mapper is invoked | NOT return `case_id` or `current_phase` upward | S-C02 |

**Execution site:** identical to S-F10 — inside the parent's uniquely-named node
function for that phase, invoking the compiled subgraph between the two mappers.
The stability condition stated at S-F10 applies to all five.

> **Phase-context rulings** (G-27 closed at procedure step 3.3; all four pairs
> are built in `phases/{phase}/mappers.py`):
>
> | Question | Ruling |
> |---|---|
> | Which fields | The prior phase's **Tier-1 (gate-required) fields** per §35 / CLAUDE.md §9.7, **plus `phase_metrics`**, **plus `acknowledged_gaps`** |
> | In what form | `field: value` lines, one per field. A field the prior phase did not capture renders as "not captured" rather than being omitted — a planner that cannot tell *absent* from *never asked* will not ask |
> | `acknowledged_gaps` | **Included.** It is the record of what was CONSCIOUSLY skipped, and without it a deliberate Tier-2 decision is indistinguishable from an oversight — the distinction §35's two tiers exist to preserve |
>
> **Tier 2 is excluded**, deliberately: a Belt may proceed without a Tier-2
> field, so carrying one forward invites the next planner to treat a permitted
> absence as a finding.
>
> The ruling lives in code as one named constant per phase,
> `PHASE_CONTEXT_FIELDS`, so a later amendment changes a list rather than
> control flow.

### 58.22 S-F13 · Level 2 `Command` routing

**Architecture:** §13, §15 · **File:** `phases/{phase}/graph.py` · **Procedure:** steps 4.1, 4.4
*Rebuild test: met.*

**Purpose:** The intra-phase routing that makes the subgraph a cycle. §15 states
the rule — `Command` inside phase subgraphs, static edges between phases — and
this entry is the design that rule was waiting for.

**Every routing node returns a `Command` exclusively**, annotated
`-> Command[Literal[...]]` so the reachable targets are visible to the type
checker and to LangGraph's graph construction. **No routing node has a static
edge out of it** (§15 C2). The only static edges in a phase are
`START → planner` and the parent's phase-to-phase edges.

**Verified against current LangGraph documentation, 2026-08-24.**

#### DP1 — the planner owns the field / gate decision

**The executor returns plainly and emits no routing `Command`.** It consumes
`coaching_plan`, coaches, and hands control back; it decides no strategy, which
is the whole content of the Planner/Executor split (§17).

**The planner then inspects `artifacts` and returns:**

| Condition | Return |
|---|---|
| Field incomplete — keep coaching it | `Command(goto="executor")` |
| Field complete, more fields remain | `Command(goto="executor")`, with `field_index++` |
| All fields captured | `Command(goto="validation_stack")` |

> **Deciding this in the executor would fuse the two roles while leaving the
> node names intact** — the failure §17 exists to prevent, and the harder one to
> see, because the diagram would still show two boxes.

#### DP2 — the validation stack's three exits

**`gate_attempts` increments ONCE, at `validation_stack` entry** — before any
layer runs. A partially-run stack still costs one attempt, which is the
conservative reading: a stack that failed at 2b consumed a gate passage just as
a stack that failed at 2d did.

| Condition | Return |
|---|---|
| All layers pass | `Command(goto="gate_review")` |
| Fail, `gate_attempts < 3` | `Command(goto="planner", update={"validator_feedback": [...]})` |
| Fail, `gate_attempts >= 3` | `Command(goto="<escalation>", graph=Command.PARENT)` |

**The escalation exit is the only place `Command.PARENT` is used in this
architecture.** Escalation is a parent-level subgraph (§12, §38), so the hop
crosses the graph boundary; every other `Command` here is intra-subgraph.

> **SPEC-GAP (G-34):** the escalation subgraph still has no node list, no state
> schema and no exit contract, so `"<escalation>"` above is a placeholder for a
> node name G-34 must fix — to be designed with founder.

#### DP3 — the gate exits

**`gate_review` fires `interrupt()` and stops.** It routes nothing; the graph
resumes into `gate_apply` with the Belt's decision.

| Belt decision | `gate_apply` does |
|---|---|
| **Approve** | Applies edits, runs the policy advisory, assembles and writes the gate document, then `END` — the parent's static edge advances the phase |
| **Reject** | `Command(goto="planner", update={"rejection_feedback": [...]})` |

**Reject loops back for another coaching turn, carrying the Belt's stated
reason.** The reason is mandatory: a rejection with no reason gives the coach
nothing to change, and the next turn would reproduce the one just refused.
`rejection_feedback` is a `PhaseState` field (S-C02) and is **never merged into
`validator_feedback`** — the system rejecting the AI's work and the Belt
rejecting the document are two actors at two moments (§6).

> **SPEC-GAP (G-18):** the `/gate/reject` request envelope must carry that
> mandatory reason, and no envelope is defined for any endpoint — to be designed
> with founder.

#### What is settled and binds

| # | Constraint | Ref |
|---|---|---|
| C1 | `Command` inside phase subgraphs only; phase transitions are static edges | §15 |
| C2 | A node SHALL NOT mix a static edge and a `Command` — both paths execute, silently | §15 |
| C3 | `gate_attempts` lives on `PhaseState`, never in route scope | §6, §15 |
| C4 | Retry and escalation resolve inside the phase, never above it | §15 |
| C5 | A subgraph reaches `END` only through `gate_apply` **on approve**, so reaching `END` means the gate passed | §15 |

---

## 59. Spec — knowledge and retrieval

> **NOT-MARKABLE:** **a spec-layer container.** Its entries (S-C / S-F) carry their own markers where they have a built form; marking the Part as well would be the parallel table §55.2 exists to prevent.

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

> **SCHEMA GAP — `Hop` carries no index or tool field** (recorded 2026-09-08).
> `hop_number` and `hop_question` are all a hop has, and S-F09's reference
> implementation hardcodes `rag_lookup_methodology`, so **a planned hop can only
> target `improve_knowledge_index`.** §26 does not forbid the other two — its
> opening defines multi-hop over `rag_lookup_*`, and its three-query-type table
> excludes non-retrieval question types rather than enumerating permitted
> indexes. **This is a limit of the schema, not a rule**, and it is recorded
> here so the table is not read as a whitelist. Revisit after the upload path
> (procedure step 6.11) makes evidence worth hopping against.

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

> **`QueryVariants` (G-14 closed, step 5.2):** one field `variants: list[str]`;
> **the original query is NOT among them and is always searched as ranked list
> zero**; the count is model-chosen, bounded 3–5 by the schema
> (`knowledge/fusion.py`).

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
| B3 | ~~called before the batched reindex lands~~ | ~~take no `order_by` argument; `uploaded_at` does not exist on the live index~~ **DISCHARGED 2026-09-10 at step 6.13** — `uploaded_at` is live, filterable and sortable. The tool still takes no `order_by`, now as a design choice rather than a schema constraint: B4 forbids presenting a re-sorted `top_k` as recency ordering, and §24's structured record carries `uploaded_at` as a VALUE so the coach can choose on it without the tool ranking on it | §23.2 |
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

> **NOT-MARKABLE:** **a spec-layer container.** Its entries (S-C / S-F) carry their own markers where they have a built form; marking the Part as well would be the parallel table §55.2 exists to prevent.

*Supersedes: none — new. Definitions relocated from §29.2, §30.*
**Status: RATIFIED as a structure; most entries carry gaps.**

**The tool inventory and the per-phase binding table stay in §30.** They are a
binding inventory rather than a signature set, and §30 is where an amendment
against the 16-tool cap is evaluated. The entries below specify the tools
themselves.

**Three categories exist, and only two are bound:** the universal eight
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
> `load_skill(name)` tool," and it appears in **neither the universal eight
> (§29.2) nor any phase's tool count (§30).** If it is bound to the executor it
> is an eighth universal tool, and every per-phase total in §30 moves — Measure
> from 15 to 16, against a hard cap of 16, which would then also constrain
> §29.4's cross-agent binding question. If it is not bound to the executor,
> then how the coach calls it is unstated. Its signature and return shape are
> undefined either way — to be designed with founder.

### 60.6 S-F24 · The 20 computation tools

**Architecture:** §30, §7, §43.1, **§69** · **File:** `knowledge/computation.py` · **Procedure:** step 5.3
*Rebuild test: **met — see §69**, which states each tool's inputs, `result` keys
and preconditions as S-F37–S-F56. This entry remains the group entry: the
inventory below and the EARS behaviors bind on all twenty.*

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

> **SPEC-GAP (G-25) — RESOLVED 2026-08-26 by §69**, which specifies all twenty:
> §69.1 answers the `args_schema` and reformatting-request shape, and
> §69.2–§69.6 give each tool's `computation_results` entry.

### 60.7 S-F57 · `load_evidence_series(blob_path, column)`

**Architecture:** §29.2, §24, §30 · **File:** `knowledge/tools.py` · **Procedure:** step 6.12
*Rebuild test: not met — ratified 2026-09-09, built at 6.12. `DECISIONS.md` Part AR.*

**Purpose:** The eighth universal tool, and the one that gets a Belt's numbers
into a computation without the coach retyping them. **Retrieval finds WHICH
file; this loads THE VALUES.** It takes a `blob_path` — obtained from
`PhaseState.uploads` or from `rag_lookup_evidence`'s record (§24) — and one
column name, and returns that column's typed values with `n`, `mean`, `sigma`,
`min` and `max`.

**It re-parses the blob with step 6.11's deterministic parser.** It reads no
stored values: `UploadRecord.rows` is a row *count*, and the parsed table is
stored nowhere, deliberately. **Storing a second copy would be the drift
§39.2's single-authority rule exists to prevent**, and re-parsing costs
milliseconds against a file the platform already holds.

**Why it is universal rather than a computation tool.** §30's twenty are pure
functions with no I/O, which is what makes them unit-testable without a network.
This one reads a blob. **The universal set is where the I/O-performing tools
already live** — all three `rag_lookup_*` tools call Azure AI Search, this one
calls Azure Blob — so the placement is a classification, not an exception
carved for it.

#### SIPOC — at a glance

| | |
|---|---|
| **Supplier** | `PhaseState.uploads` (§6) for the `blob_path`; `rag_lookup_evidence` (S-F15) where the coach found the file by search; `storage/blob.py` for the bytes |
| **Input** | `blob_path: str`, `column: str` |
| **Process** | Fetch the blob → parse with `upload/parsers.py` → select the named column → compute `n` / `mean` / `sigma` / `min` / `max` over its typed values |
| **Output** | The column's typed values plus the five summary scalars, as **strings** (§7's typing law, Part AD1) |
| **Customer** | The twenty computation tools (S-F24), which take scalar strings and are **not modified**; `consumed_at` on the upload record and the §6 entry |

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the tool is called | re-parse the blob at `blob_path`; it SHALL NOT read a stored copy of the parsed values, and no such copy SHALL be created | §39.2 |
| B2 | the named column is absent | return a Belt-readable reformatting request naming the columns that ARE present, never a bare failure | §27, ruling AP2.5 |
| B3 | values are returned | return them as strings, so the twenty computation tools consume them unchanged | §7, AD1 |
| B4 | a load succeeds | set `consumed_at` on that upload's record and its §6 entry — the write that makes an unread upload detectable at the gate. **The EXECUTOR NODE performs it, not the tool** (ruling AR-R4, 2026-09-10): a `@tool` receives only its arguments and cannot reach `PhaseState`, so the node inspects the turn's tool calls afterwards. The behaviour is the system's; the placement is the node's | S-C02, S-C09 |
| B5 | the column is mixed-typed | carry the parse's own `mixed` report rather than silently coercing; a mixed column is a coaching question | step 6.11 |

**Invariants:**
- **The twenty computation tools are not touched by this entry.** One new tool,
  zero changes to twenty.
- **This tool never writes to `improve_evidence_index`.** It reads a blob and
  returns values; the index is §23.2's concern and step 6.13's.

---

---

## 61. Spec — the coaching agent's middleware

> **NOT-MARKABLE:** **a spec-layer container.** Its entries (S-C / S-F) carry their own markers where they have a built form; marking the Part as well would be the parallel table §55.2 exists to prevent.

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
| B6 | composing for Define | open the block with the Belt's step from `define_progress` — *Step n of 13*, computed, never counted by the model — and head the missing-field list as the gate list (v1.73) | §43.3, §39.1.9 |
| B7 | composing any turn | deliver labelled sections, one job each — coaching rules, phase script, state, **this turn's move (authoritative)**, last turn's quality feedback, the conversation — and never present feedback as a message from the Belt (v1.75; built at 6.61) | §17, §19.1 |

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
| 2 | **Every model call**, for the phase being coached (v1.71) | That phase's full SKILL.md, in the system message; version and hash recorded in `step_log` |
| 3 | On demand | Reference files, when explicitly needed |

**Storage backend: `FilesystemBackend`** — git-versioned alongside the code, so
a skill change is reviewable in the same PR as the code depending on it.
`ContextHubBackend` is deferred to the multi-deployment stage.

#### Behaviors (EARS)

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the system starts | load descriptions only, under 2K tokens for all five combined | §32 |
| B2 | a model call is made while coaching a phase | place that phase's full SKILL.md in the system message, and record the script's version and hash in `step_log` once per turn (v1.71) | §19.2 |
| B2a | the coach calls `load_skill(name)` for ANOTHER phase, or a level-3 reference | return it — the current phase's script never depends on this call (v1.71) | §19.2 |
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
| B6 | the check is made | give the judge the script step the reply performs — ④ Confirm for a captured field, ①–③ for the focus field — with that field's SKILL.md block and the whole reply, `prompt` included; a read-back that asks the Belt to confirm is NOT parroting (v1.72, G-96) | §19.7, §43 |
| B6a | the check returns | record the verdict in `step_log` under node `coherence` — a rejection with its reason, `degraded` and `grader_skipped` (v1.72, G-96) | §19.7 |

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

> **NOT-MARKABLE:** **a spec-layer container.** Its entries (S-C / S-F) carry their own markers where they have a built form; marking the Part as well would be the parallel table §55.2 exists to prevent.

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

**The gate-required lists it checks** are §35's, per phase: **Define 12 (all
required — no tiers, Option A §39.1.2)**, Measure 7, Analyse 4, Improve 4,
Control 3. For the four tiered phases those are Tier 1 counts; for Define it is
the whole field set.

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
| B2 | grading `causal_hypothesis`, `solution_linked_to_root_cause` or `post_improvement_metrics` | verify the link **by lookup, not judgment** — read the referenced phase's gate document from the Store and check the named field carries the named value | §36, §42 |
| B3 | grading a criterion that depends on a computation | scan `artifacts["computation_results"]` for the relevant `tool` entry rather than asking the model | §36 |
| B4 | grading a structured dict field | check **every** sub-field is populated — a `process_map_sipoc` with four of six keys filled is the partial-map failure the field exists to catch | §41 |
| B5 | `belt_level` is Green Belt | suppress DOE as a recommendation; when it is Black Belt, flag DOE as a Tier 2 recommendation | §35 |
| B6 | grading | never retrieve; the rubric already encodes the methodology standards, and retrieval adds latency at the moment the Belt is waiting | §26 |
| B7 | grading the measurement thread | verify that `process_map_sipoc["process_metrics"]`, `detailed_process_map["baseline_metrics"]` and `post_improvement_metrics` name the same measurement points and carry **different values** | §39 |

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

**Two invariants run BEFORE the document is constructed, and both raise:**

1. **Field coverage** — assembly must reference **every** field in the schema
   (§40). A field assembly never sets is a field that silently never reaches the
   Store, and the omission is invisible until a later phase reads nothing.
2. **Metric single authority** (§39.2.3) —
   `assert_single_authority(phase, artifacts)` from `core/metrics.py`. The
   primary metric's `phase_metrics` entry and the mirrored scalars **must be
   equal**: Define's `baseline_estimate` / `target_value`, Measure's
   `baseline_mean` / `baseline_sigma`, Control's `post_improvement_metrics`.
   **Analyse and Improve mirror nothing** and satisfy it vacuously — they record
   which metric a cause or solution targets, not its value.

> **Both raise rather than warn, and at this point that is right.** Layer 2b,
> the constraint check and the rubric have all run; the Belt has approved. A
> mismatch here is therefore **a code defect, not an incomplete phase** — two
> stores disagreeing about one number, where writing either one makes the
> disagreement permanent. This is the same reasoning that makes a `KeyError` on
> a gate-required field correct rather than something to defend against.

**Definition — Define, the one worked example.** Under Option A (§39.1.2) all
12 Define fields are gate-required, so **every one is a direct `artifacts[...]`
access** in coached order — none defaults through `.get()`:
```python
assert_single_authority("define", artifacts)   # §39.2.3 — raises on drift

gate_document = DefineOutput(
    # All 12 gate-required (§39.1.2) — direct access throughout.
    business_case=artifacts["business_case"],
    team=artifacts["team"],
    voc_summary=artifacts["voc_summary"],
    problem_statement=artifacts["problem_statement"],
    baseline_estimate=artifacts["baseline_estimate"],
    project_scope=artifacts["project_scope"],
    goal_statement=artifacts["goal_statement"],
    target_value=artifacts["target_value"],
    target_date=artifacts["target_date"],
    secondary_metrics=artifacts["secondary_metrics"],
    process_map_sipoc=artifacts["process_map_sipoc"],
    issues_and_barriers=artifacts["issues_and_barriers"],
    # The metric registry — gate-required, captured inside position 5 (§63.8)
    metric_definitions=artifacts["metric_definitions"],
    # On all five schemas (§63.9); "none this phase" rather than an empty list
    phase_metrics=artifacts.get("phase_metrics", []),
    # Gate metadata — the same four on all five schemas (§40)
    computation_results=artifacts.get("computation_results", []),
    acknowledged_gaps=acknowledged_gaps,   # always [] for Define — nothing is skippable
    citations=state["citations"],
    uploads=state["uploads"],
)
```

**The access pattern encodes the tier, and the difference is deliberate:**

| Tier | Access | Why |
|---|---|---|
| Tier 1 / gate-required | `artifacts["field"]` | **A `KeyError` here is correct** — Layer 2b should have blocked the gate, so reaching assembly without the field is a bug that must surface loudly |
| Tier 2 | `artifacts.get("field", "")` | An empty value **records that the Belt proceeded without it** |
| Cross-phase dicts | `artifacts.get("field", {})` | Same, with the right empty type |

> **The Tier 2 row does not apply to Define.** It has no Tier 2 fields, which is
> why the worked example above reads every gate-required field directly — the
> coached elements plus the fields captured inside a position, which are
> gate-required and therefore read the same way (§63.8). **`phase_metrics` is the one `.get()` in Define's
> assembly**, and it is not a Tier 2 access: it defaults to `[]` because a phase
> may legitimately engage no metric, in which case §63.9 B2 requires
> `"none this phase"` to be written into it rather than the field being absent. The row governs the other four phases, whose assemblies are
> **G-28 — still unwritten**.

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | assembly runs for any of the five phases | call `assert_single_authority(phase, artifacts)` **before** constructing the `{Phase}Output`, and raise on any defect | §39.2.3 |
| B2 | the primary metric's `phase_metrics` entry disagrees with a mirrored scalar | raise — `phase_metrics` is authoritative and the scalar is its mirror, so a difference means one of the two is already wrong | §39.2.3, §63.9 |
| B3 | a phase carries mirrored scalars but `phase_metrics` names no metric | raise — the value cannot be traced to a registry metric, which is the failure the registry exists to prevent | §63.8 |
| B4 | `phase_metrics` holds `"none this phase"` | treat the invariant as satisfied — that is a conscious answer, not a broken mirror | §63.9 B2 |
| B5 | the phase is Analyse or Improve | satisfy the invariant vacuously; those phases record linkage, not values | §63.9 |
| B6 | a field exists on the schema | be referenced by assembly, so nothing reaches the Store unset | §40 |

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

> **NOT-MARKABLE:** a parent whose CHILDREN own the facts. §16's convention — *“one marker per item, never one per section that mentions it”* — and a row here would be a second claim over the same ground. All 9 children own rows.

> **NOT-MARKABLE at Part level · its entries are measured at §40, §41 and §42.** **⛑ Corrected 2026-09-11.** This note read *"its entries carry their own markers where they have a built form"* and **they carried none** — a claim that looked fine in a list of sections and failed the moment §55.3's completeness view counted it. **§63.6 and §63.9 carry their OWN markers** — checked 2026-09-11, and both turned out NOT to be covered: the cross-phase reference keys are validated by nothing, and `phase_metrics` is written by nothing. Under the alias both would have rendered green.

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

**Purpose:** Define's gate document, rendered as the Define report (R5). **21 fields
— 16 required, `phase_metrics`, 4 gate metadata** (v1.79; the owner is
`DefineOutput.model_fields`). No Tier 1 / Tier 2 split: every field blocks the gate. **The declaration order below is
the coached order** of §39.1.2 — with no tiers to group by, the two lists are
one.

```python
class DefineOutput(BaseModel):
    """Gate document for the Define phase. All 16 content fields gate-required."""
    business_case:        str         # strategic rationale / quantified impact (COPQ)
    team:                 list[dict]  # [{name, role, function}] — §39.1.4
    voc_summary:          str         # who the customers are, what they need
    problem_statement:    str         # ONE SMART statement, composed — §39.1.3
    baseline_estimate:      str         # DISCRETE current-state value — Control compares
    project_scope:        dict        # {in_scope, out_scope} — both explicit
    goal_statement:       str         # the SMART sentence, human-readable prose
    target_value:        str         # DISCRETE target value — Control compares
    target_date:          str         # ISO; the PLANNED completion date (PM parameter)
    benefits_analysis:    dict        # {cost_of_gap, impact_type, realisation_schedule, finance_contact} — R4
    secondary_metrics:    str         # what could get worse — on all five (§40)
    process_map_sipoc:    dict        # SIPOC + KPIs, 6 sub-fields (§41)
    issues_and_barriers:  str         # Belt-stated blockers
    # Captured inside positions 3 and 4 (R4, R5)
    critical_to_quality:  list[dict]  # [{customer, need, requirement}] — the CTQs
    problem_5w2h:         dict        # {what, where, when, who, why, how, how_much}
    # The metric registry — Define owns it (§63.8, S-C38); the FIRST entry is the primary
    metric_definitions:   list[dict]  # [{name, unit, meaning}] — the traceability keys
    # On all five schemas (§40, §63.9, S-C39)
    phase_metrics:        list[dict]  # [{name, unit, baseline_estimate, target_value, source}]
    # Gate metadata (unchanged)
    computation_results:  list[dict] = []
    acknowledged_gaps:    list[str]  = []   # stays in schema; always empty for Define
    citations:            list[dict] = []
    uploads:              list[dict] = []
```

**Three fields are not `str`, and each is deliberate** (§7's typing law admits
exactly the structured dicts and the cross-phase reference dicts):
`process_map_sipoc` and `project_scope` are dicts because a coaching
conversation produces prose no planner can read and no grader can check;
`team` is `list[dict]` because a project has N people and each carries three
attributes.

**`baseline_estimate`, `target_value` and `target_date` are discrete fields,
not duplicates of `goal_statement`.** `goal_statement` is the human-readable SMART
sentence; these three are the **machine-readable values Control extracts** to
compute target-vs-actual. Folding them into the prose would leave Control with
nothing to compare (§39.1.2, the measurement thread). `acknowledged_gaps` stays
on the schema for cross-schema uniformity (§40) but is **always empty for
Define** — no field is skippable, so nothing can be acknowledged as skipped.

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the gate is evaluated | block on **every required field** — Define has no Tier 2 and no `acknowledged_gaps` path, so a missing field can never be waived (Option A) | §35, §39.1.2 |
| B2 | `process_map_sipoc` is graded | require all six sub-fields, `process_metrics` among them | §41 |
| B3 | `process_metrics` is set | carry WHAT is measured — the first link of the three-phase measurement thread | §39 |
| B4 | `project_scope` is graded | require **both** `in_scope` and `out_scope` — what the project is *not* doing is what protects it from ballooning | §39.1.2 |
| B5 | `problem_statement` is captured | store only the composed statement the Belt has confirmed, assembled from the Belt's own words with nothing invented | §39.1.3, §22 |
| B6 | the coach elicits 5W2H | treat them as conversational prompts, never as stored fields | §39.1.3 |
| B7 | `baseline_estimate` and `target_value` are captured | store them as **discrete values**, never folded into `goal_statement` prose — Control extracts both to compute target-vs-actual, and prose it cannot parse breaks that comparison | §39, §39.1.2 |
| B8 | `target_date` is captured | treat it as the **planned** completion date, a project-management parameter that may slip without invalidating the improvement. **Control's `actual_close_date` is the paired value** and is not yet specified — F-12 | §39.1.2, §66.7 |

### 63.2 S-C28 · `MeasureOutput`

**Architecture:** §40 · **File:** `phases/measure/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Measure's gate document. **15** fields — 7 Tier 1, 3 Tier 2, 4 gate
metadata. The largest Tier 1 set of the five.

```python
class MeasureOutput(BaseModel):
    """Gate document for the Measure phase."""
    # Tier 1
    baseline_mean:                str    # value with units, as the Belt stated it
    data_collection_plan:         str    # sample size, frequency, responsible person
    driver_priority_summary:            str    # evidence that prioritisation happened
    vital_few_drivers:                 str    # the ranked result Analyse consumes
    detailed_process_map:         dict   # expanded map, 6 sub-fields (§41)
    stability_assessment:         str    # checked BEFORE capability (§41)
    issues_and_barriers:          str
    # Tier 2
    baseline_sigma:               str    # calculated sigma level
    measurement_system_validated: str    # GR&R or equivalent evidence
    secondary_metrics:            str
    # On all five schemas (§40, §63.9, S-C39)
    phase_metrics:                list[dict]  # one entry per registry metric
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
| B2 | `detailed_process_map` is graded | require all six sub-fields, `baseline_metrics` among them | §41 |
| B3 | `baseline_metrics` is set | carry the BEFORE values of the measurement thread | §39 |
| B4 | `vital_few_drivers` is set | be the ranked result Analyse consumes; Analyse cannot start without it, which is why `driver_priority_summary` is Tier 1 for all Belts | §35 |

### 63.3 S-C29 · `AnalyseOutput`

**Architecture:** §40 · **File:** `phases/analyse/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Analyse's gate document. **14** fields — 4 Tier 1, 5 Tier 2, 4 gate
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
    # On all five schemas (§40, §63.9, S-C39)
    phase_metrics:                list[dict]  # one entry per registry metric
    # Gate metadata
    computation_results:  list[dict] = []
    acknowledged_gaps:    list[str]  = []
    citations:            list[dict] = []
    uploads:              list[dict] = []
```

> **Analyse's `phase_metrics` carries the LINKAGE form, not values** (§39.3.3).
> Analyse holds no measured metric value — Measure did that. Each entry records
> which root cause explains which registry metric:
>
> ```python
> phase_metrics = [
>     {"name": "invoice_error_rate",
>      "explained_by": "root cause: onboarding gap in first 60 days",
>      "share_explained": "≈70% (practical_significance)", "source": "linkage"},
>     {"name": "invoice_cycle_time",
>      "explained_by": "not addressed this phase", "source": "linkage"},
> ]
> ```
>
> **A registry metric this phase does not touch writes `"not addressed this
> phase"`** — populated-or-explicit, never silently absent (§40, §63.9 B2). That
> is what keeps the keyed trail unbroken through a phase that acts on drivers
> rather than outcome values.

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | `causal_hypothesis` is graded | verify its reference keys against Measure's gate document by lookup, not judgment | §36, §42 |
| B2 | `statistical_problem_statement` is coached | require it of all Belts, in Analyse and not Define — it is no longer belt-gated | §35 |
| B3 | the phase is graded | treat `practical_significance` as Tier 1 — the eBook's second gate, "how much of the problem does this explain" | §35 |

### 63.4 S-C30 · `ImproveOutput`

**Architecture:** §40 · **File:** `phases/improve/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Improve's gate document. **14** fields — 4 Tier 1, 5 Tier 2, 4 gate
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
    # On all five schemas (§40, §63.9, S-C39)
    phase_metrics:                list[dict]  # one entry per registry metric
    # Gate metadata
    computation_results:  list[dict] = []
    acknowledged_gaps:    list[str]  = []
    citations:            list[dict] = []
    uploads:              list[dict] = []
```

> **Improve's `phase_metrics` carries the LINKAGE-PLUS-PILOT form** (§39.4.3).
> Each entry records which registry metric the selected solution is expected to
> move, and what the pilot achieved on it:
>
> ```python
> phase_metrics = [
>     {"name": "invoice_error_rate",
>      "moved_by": "selected solution: onboarding checklist",
>      "pilot_effect": "12.3% → 4.1% in the pilot cell", "source": "pilot"},
>     {"name": "invoice_cycle_time",
>      "moved_by": "not addressed this phase", "source": "linkage"},
> ]
> ```
>
> **A registry metric the solution does not target writes `"not addressed this
> phase"`** — populated-or-explicit, never silently absent (§40, §63.9 B2).
> **`solution_linked_to_root_cause` names the metric** via
> `references_metric_name` (§63.6, S-C32), so a multi-metric project links the
> solution to the specific Y its root cause explained; the grader resolves the
> link by lookup against Analyse's gate document (§42).

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | `experiment_justification` is graded | accept any of three answers — DOE conducted, simplified one-factor experiment, or no experiment needed because the solution follows from root cause analysis. **All three are valid**; the failure it catches is drifting past the question, not skipping DOE | §41 |
| B2 | `belt_level` is Green Belt | not recommend DOE | §35 |
| B3 | `solution_linked_to_root_cause` is graded | verify its reference keys against Analyse's gate document by lookup | §36, §42 |

### 63.5 S-C31 · `ControlOutput`

**Architecture:** §40 · **File:** `phases/control/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Control's gate document. **17** fields — 3 Tier 1, 9 Tier 2, 4 gate
metadata. The smallest Tier 1 set and the largest Tier 2 set. (Was 16:
`actual_close_date` is added at the 2026-08-27 review, closing **F-12**.)

```python
class ControlOutput(BaseModel):
    """Gate document for the Control phase."""
    # Tier 1
    control_plan:              dict   # FIVE sub-plans — §41
    post_improvement_metrics:   dict   # cross-phase ref → Measure baseline (§7)
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
    actual_close_date:         str    # ISO — achieved date, pairs with Define's
                                      # planned target_date (F-12)
    # On all five schemas (§40, §63.9, S-C39)
    phase_metrics:                list[dict]  # one entry per registry metric
    # Gate metadata
    computation_results:  list[dict] = []
    acknowledged_gaps:    list[str]  = []
    citations:            list[dict] = []
    uploads:              list[dict] = []
```

> **Control's `phase_metrics` carries the COMPARISON form** (§39.5.3) and is
> **the authoritative store of all N comparisons** — one entry per registry
> metric, each closing the thread:
>
> ```python
> phase_metrics = [
>     {"name": "invoice_error_rate", "baseline": "12.3%", "target": "<3%",
>      "actual": "2.8%", "delta": "-9.5pp", "met": "yes", "source": "after"},
>     {"name": "invoice_cycle_time", "baseline": "2.6 days", "target": "<1.5 days",
>      "actual": "1.4 days", "delta": "-1.2 days", "met": "yes", "source": "after"},
> ]
> ```
>
> **`post_improvement_metrics` is the PRIMARY metric's link, not the store.** It
> is Tier 1 and carries `references_metric_name`, and it is what the gate blocks
> on (§42 B2). **Single-authority invariant** (§39.2.3, `core/metrics.py`): the
> primary metric's `phase_metrics` **`actual`** equals
> `post_improvement_metrics`'s **`metric`** value — two names for one number, so
> a mismatch raises at assembly. **Additional metrics live only in
> `phase_metrics`.**
>
> **The grader grades every entry, not only the primary.** A project that met its
> primary metric but silently missed a secondary criterion has not fully
> succeeded, and `phase_metrics` is the only place that shows.

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | `control_plan` is graded | require all five sub-plans populated. A single string cannot show that four were done and one was skipped, and **a Training Plan written but never delivered is the most common real Control failure** | §41 |
| B2 | `post_improvement_metrics` is graded | verify by lookup against Measure's `baseline_mean`. **It is the only cross-phase reference field that is Tier 1** — a Control phase that cannot link its result back to the baseline has not demonstrated improvement at all | §42 |
| B3 | Control's gate passes | populate `SupervisorState.final_output` through Control's output mapper | §5 |
| B4 | `actual_close_date` is captured | record the **achieved** completion date, paired with Define's **planned** `target_date`. **Tier 2 — a slipped date does not invalidate the improvement**, the same reasoning that makes Define's target a planning parameter | §39.1.2, F-12 |
| B5 | `phase_metrics` is graded | grade **every** entry, not only the primary — a project that met its primary metric and missed a secondary one has not fully succeeded | §39.5.3 |
| B4 | `lessons_learned` and `transferability` are set | feed the case index and cross-case retrieval respectively | §23.3, §24 |

### 63.6 S-C32 · The three cross-phase reference dicts

> **The reference keys are validated by NOTHING yet — closed by step 7.1.**
> They reach the coach as instruction (`analyse/schema.py`'s field description,
> three SKILL.md files); `missing_structured()` checks none of them, so the
> deterministic lookup this entry exists for cannot happen and the gate passes
> either way.

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
    "hypothesis":             "Inadequate onboarding causes error spike in first 60 days",
    "references_phase":       "measure",
    "references_field":       "baseline_mean",
    "references_metric_name": "invoice_error_rate",   # which metric — §63.8
    "references_value":       "12.3%",
}
```

**Four reference keys, not three.** `references_metric_name` names **which
registry metric** the link is about (§63.8), and the shape is **uniform across
all three dicts** so the grader has one resolution path rather than three.

> **Why it was added (F-13, closed 2026-08-26).** With one metric, "references
> Measure's `baseline_mean`" is unambiguous. With two, `baseline_mean` is the
> *primary* metric's mirror (§39.2.3) and the others live only in
> `phase_metrics` — so a hypothesis referencing a bare scalar resolves to
> whichever metric happens to be primary, and *"explains 60% of the problem"*
> stops having a single referent. **The key turns a positional guess into a
> lookup.**

**`references_metric_name` is on all three dicts**, so the resolution shape is
settled once rather than three times.

**The three:**

| Field | Phase | Tier | References | `references_metric_name` populated? |
|---|---|---|---|---|
| `causal_hypothesis` | Analyse | 2 | Measure's `baseline_mean`, for a named metric | **Yes — §39.3** |
| `solution_linked_to_root_cause` | Improve | 2 | Analyse's `root_cause_statement`, for a named metric | **Yes — §39.4** |
| `post_improvement_metrics` | Control | **1** | Measure's `baseline_mean`, for the primary metric | **Yes — §39.5** |

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | one of the three is graded | resolve `references_phase` / `references_field` / `references_metric_name` / `references_value` against the Store by lookup, never by model judgment. **Match `references_metric_name` against the referenced phase's `phase_metrics` `name`** and read the value from that entry — **not from the bare scalar**, which is only the primary metric's mirror (§39.2.3) | §36, §42, §63.9 |
| B5 | `references_metric_name` is absent or names no registry metric | fail the lookup rather than falling back to the scalar — a link that cannot say which metric it is about is not a verified link | §63.8 |
| B2 | one of the three is captured | carry it through `CoachingResponse.fields_captured` with `value` as a `dict` — which is why `value` is typed `Any` | §20 |
| B3 | values inside the dict are written | write them as strings | §7 |
| B4 | assembly reaches one of the three | access it as `artifacts.get("field", {})` — the correct empty type | §40.1 |

**Invariant:** only `post_improvement_metrics` is Tier 1, and the asymmetry is
deliberate — an Analyse phase without an explicit hypothesis link is weaker but
not void, whereas a Control phase that cannot link back to the baseline has
demonstrated nothing.

### 63.7 S-C33 · The three structured dict fields

**Architecture:** §41, §39 · **File:** `phases/{phase}/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** Three gate-required fields are structured dicts, **distinct from the three
cross-phase reference dicts.** They are dicts rather than prose because a
coaching conversation produces text no downstream planner can read and no grader
can check.

| Field | Phase | Sub-fields |
|---|---|---|
| `process_map_sipoc` | Define | `suppliers`, `inputs`, `process_steps`, `outputs`, `customers`, **`process_metrics`** |
| `detailed_process_map` | Measure | `steps`, `cycle_times`, `resources`, `value_vs_waste`, `measurement_points`, **`baseline_metrics`** |
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
| B3 | the measurement thread is verified | read `process_metrics` (WHAT), `baseline_metrics` (BEFORE) and `post_improvement_metrics` (AFTER), and confirm the same measurement points carry different values | §39 |

**Invariant — FMEA has no field in any schema, and none may be added.** Not
`fmea_summary`, not `updated_fmea`, not an FMEA sub-key anywhere. If a Black
Belt performs one it lives in `uploads` as an attached document; the schema does
not track it, the grader does not ask for it, and no gate blocks on it (§41).

---

### 63.8 S-C38 · `metric_definitions` — the project metric registry

**Architecture:** §39.1, §40 · **File:** `phases/define/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** **The canonical set of metrics the project is traced by.** Define
owns it; every later phase refers to its entries rather than re-naming them.

```python
metric_definitions: list[dict] = [
    {"name": "invoice_error_rate", "unit": "%",
     "meaning": "share of invoices returned by collections for correction"},
    {"name": "invoice_cycle_time", "unit": "days",
     "meaning": "order receipt to invoice sent"},
]
```

| Key | Holds |
|---|---|
| `name` | **The traceability key.** A stable identifier, written **identically in every phase** — this is what the grader matches on |
| `unit` | The unit the value is expressed in, so a target can be compared to a baseline without guessing |
| `meaning` | What the metric actually counts, in the Belt's own words. The operational definition a later phase re-reads rather than re-deriving |

> **`name` is a key, not prose, and that is the whole point.** The grader traces
> a metric across the five gate documents by **key equality on `name`** — not by
> reading a sentence and hoping two phases phrased it the same way. **This is
> what a prose-string contract could not deliver**: "Error rate: 12.3%" in
> Define and "error rate (%)" in Measure are the same metric to a human and two
> different metrics to a matcher.

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | the Belt names a metric | record it once, here, with all three keys populated | §39.1 |
| B2 | any later phase refers to a metric | use the registry `name` **verbatim** — never a variant, never a re-phrasing | §40 |
| B3 | the gate is evaluated | require at least one entry, every entry carrying `name`, `unit` and `meaning` | §35 |
| B4 | a value is written inside an entry | keep it a **string** — the dict is the exception to §7, its scalars are not | §7 |

### 63.9 S-C39 · `phase_metrics` — the per-phase placeholder

> **`phase_metrics` is declared on every `{Phase}Output` and written by nothing
> until step 6.20's write path lands** — it is in no tier set, the coach never
> captures it, and `verify_built.py`'s reader/writer pass reports it
> `phase_metrics:W`.

**Architecture:** §40 · **File:** `phases/{phase}/schema.py` · **Procedure:** step 3.4
*Rebuild test: met.*

**Purpose:** **What one phase produced for each registry metric it engaged.**
On **all five** schemas, in the same shape, so a metric's whole journey is one
keyed trail across the five gate documents.

```python
# Measure
phase_metrics = [
    {"name": "invoice_error_rate", "unit": "%", "baseline_mean": "12.3%",
     "baseline_sigma": "2.6 sigma", "stability": "stable", "source": "measured"},
]
```

| Phase | What its entries record |
|---|---|
| **Define** | The stated starting point and target — `baseline_estimate`, `target_value`, `source: "stated"` |
| **Measure** | The measured state — `baseline_mean`, `baseline_sigma`, `stability`, `source: "measured"` |
| **Analyse** | **Linkage, not values** — which registry metric each validated root cause explains |
| **Improve** | **Linkage, not values** — which registry metric each selected solution targets |
| **Control** | The achieved state and the comparison — `actual`, `delta`, against `baseline` and `target`, with `met` and `source: "after"` (**§39.5.3's worked example is the shape**) |

**`name` MUST equal a `metric_definitions` name** (S-C38 B2). The remaining keys
are whatever state that phase produced, and differ by phase — Analyse and
Improve act on drivers rather than outcome values, so their entries carry the
link rather than a number.

> **§39.5.3's worked example is the Control shape** (`actual`, `delta`) — not
> the top-level captured fields `post_improvement_metrics` / `improvement_delta`.
> The single-authority invariant there binds `actual` to
> `post_improvement_metrics`'s value by name.

> **A phase touching no metric writes `"none this phase"` — never a silent gap.**
> An empty list is ambiguous: it reads the same whether the phase engaged no
> metric or simply forgot to record one, and the second is the failure worth
> catching. This is the same reasoning that makes `issues_and_barriers` accept
> "none identified at this stage" but not silence (§35).

**Behaviors (EARS):**

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | a phase writes an entry | set `name` to a registry `name` **verbatim**, so key equality holds | §63.8 |
| B2 | a phase engages no metric | write `"none this phase"` rather than leaving the list empty | §40 |
| B3 | a tool runs on a multi-metric project | carry the metric's `name` in `computation_results.inputs`, so the result is attributable (§69.1) | §69 |
| B4 | the live gate document renders | group `computation_results` by `phase_metrics` `name` when more than one metric is tracked | §50 |
| B5 | a scalar is written inside an entry | keep it a **string** — the dict is the exception to §7, its scalars are not | §7 |

## 64. Spec — reliability

> **NOT-MARKABLE:** **a spec-layer container.** Its entries (S-C / S-F) carry their own markers where they have a built form; marking the Part as well would be the parallel table §55.2 exists to prevent.

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
*Rebuild test: not met — blocked on G-06 and G-35.*

**Purpose:** The node-level error handler required on every node with external
writes. It **undoes the external write** and routes to a degraded response.

**Definition:**
```python
def phase_error_recovery(error: NodeError, state: PhaseState) -> Command:
    delete_or_flag_stale_in_case_index(state["case_id"], state["current_phase"])
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
| **Input** | `NodeError`; `PhaseState` — including `case_id` and `current_phase`, both declared and copied down at entry (S-C02) |
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

> **SPEC-GAP (G-06):** it writes `extraction_error` and
> `extraction_incomplete`, and `PhaseState` declares neither — see S-C02.

> **DESIGN NOTE — S-F29 / G-35, an input to step 8.2, NOT a ratification.**
> Recorded 2026-09-02. **It closes no gap and changes no rule:** G-35 stays
> open, and §45's mandate is untouched.
>
> §45's choice stands: compensation via LangGraph's native `error_handler=`
> (`delete_or_flag_stale_in_case_index` undoes the stale `improve_case_index`
> write); hand-rolled sagas remain banned. **Complementing it**, per LangGraph's
> durable-execution guidance a node re-runs on resume/retry, so an
> un-encapsulated external write is repeated. Prefer making the
> `improve_case_index` write **idempotent** — an upsert keyed on `case_id`, so a
> replay overwrites the same entry rather than orphaning a second — and
> **encapsulating** it in a task/dedicated node so a completed write loads from
> the checkpoint instead of re-executing.
>
> **Effect:** an idempotent write shrinks what `phase_error_recovery` must undo,
> leaving the compensating action to cover only the genuinely non-idempotent
> residue (e.g. a partially-written multi-document batch) rather than every
> retry. So at step 8.2: **(a)** make the index write idempotent and
> encapsulated first, then **(b)** scope `delete_or_flag_stale_in_case_index` to
> the remainder.
>
> Source: LangGraph durable execution —
> `docs.langchain.com/oss/python/langgraph/durable-execution`. *(Substance
> verified 2026-09-02 against that page and its source markdown at
> `langchain-ai/langgraph` `docs/docs/concepts/durable_execution.md`: wrap
> side-effecting operations in tasks/nodes so a resumed workflow retrieves
> their results from the persistence layer rather than repeating them, and make
> those effects idempotent. The same page is explicit that **durable execution
> does not by itself make a non-idempotent side effect safe** — which is the
> reason (a) precedes (b) rather than replacing it.)*

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
> call site — `(case_id, current_phase)`, renamed from `phase` in the 2026-08-24
> amendment so it matches the field it is passed — and **the name itself
> contains an unresolved
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

> **NOT-MARKABLE:** **a spec-layer container.** Its entries (S-C / S-F) carry their own markers where they have a built form; marking the Part as well would be the parallel table §55.2 exists to prevent.

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
*Rebuild test: not met — blocked on G-18 and G-36.*

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
| `POST /upload` | Belt evidence and artefacts — §29.1's sole external channel. **Added 2026-09-08 (Part AP5)**; behaviour specified at step 6.11 |

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

> **SPEC-GAP (G-36) — STILL OPEN** — see S-F35.

> **SPEC-GAP (G-18):** no envelope is defined for any endpoint — see S-C37.

> **Resolved — G-02, see S-F13 DP3.** `POST /gate/reject` resumes the graph;
> `gate_apply` routes back to the planner with `rejection_feedback`. **Its
> request envelope must carry a mandatory reason — that depends on G-18**
> (open).

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

> **SPEC-GAP (G-36) — STILL OPEN; two of its three clauses are answered.**
> `POST /upload` is in §49 and S-F34, the handler has procedure steps (6.11 the
> upload path, 6.12 the ask-binding), and the founder input was given (Part AP2).
> **What is still open is the code.** G-36 closes at 6.11, or is re-scoped there.

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

## 66. The SPEC-GAP register — MOVED

> **NOT-MARKABLE:** a deliberate absence — the pointer left where the register used to be. **The register moved to Appendix G at 6.37** and the number is kept so the §66 citations still resolve; a pointer asserts nothing buildable.

**The register moved to `docs/REFACTORING_PROCEDURE.md`, Appendix G, at step
6.37.** `ARCHITECTURE.md` holds the architecture and nothing else: no gap
register, no BUILT markers, no status. Founder ruling 2026-09-18.

**The section number is kept rather than reclaimed**, so the `§66` citations
across the binding documents still resolve (§0.2's no-renumbering rule).

## 67. EU AI Act compliance posture

> **NOT-MARKABLE:** compliance posture. **A legal obligation is not a buildable claim** — an obligation is met by evidence and by process, and neither is a symbol in this tree. Where a finding IS actionable it is carried as a gap, which is what §67.4 records.

*Supersedes: none — new. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §S2.*
**Status: SCAFFOLD. The classification question is UNRESOLVED and requires qualified legal advice.**

### 67.1 The deadlines are now fixed

> **NOT-MARKABLE:** compliance posture. **A legal obligation is not a buildable claim** — an obligation is met by evidence and by process, and neither is a symbol in this tree. Where a finding IS actionable it is carried as a gap, which is what §67.4 records.

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

> **NOT-MARKABLE:** compliance posture. **A legal obligation is not a buildable claim** — an obligation is met by evidence and by process, and neither is a symbol in this tree. Where a finding IS actionable it is carried as a gap, which is what §67.4 records.

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

> **NOT-MARKABLE:** compliance posture. **A legal obligation is not a buildable claim** — an obligation is met by evidence and by process, and neither is a symbol in this tree. Where a finding IS actionable it is carried as a gap, which is what §67.4 records.

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

> **NOT-MARKABLE:** compliance posture. **A legal obligation is not a buildable claim** — an obligation is met by evidence and by process, and neither is a symbol in this tree. Where a finding IS actionable it is carried as a gap, which is what §67.4 records.

**§46.1 states that the v2.1 single-region fallback chain is non-compliant for
any regulated-entity deployment** under DORA's ICT resilience obligations, and
that EU AI Act data-governance provisions are why the secondary region must be
inside the EU. It is Appendix B item 16, and it gates a production launch.

**It is carried into the register at §68 rather than restated here.**

### 67.5 Compliance-source discipline

> **NOT-MARKABLE:** compliance posture. **A legal obligation is not a buildable claim** — an obligation is met by evidence and by process, and neither is a symbol in this tree. Where a finding IS actionable it is carried as a gap, which is what §67.4 records.

**The EU AI Act and DORA are in active implementation with shifting guidance.**

- **Any compliance claim must cite a current-dated source.**
- **If availability cannot be verified, mark it "unverified — requires legal
  validation" rather than asserting it.**
- **This is not legal advice.** The classification question of §67.2 needs
  qualified counsel.

Sources are in Appendix C, under *Tier 1 — compliance*.

---

## 68. The DORA-structured compliance risk register

> **NOT-MARKABLE:** a risk register. **A risk is a statement about what could happen, not about what exists**, so it has no built/not-built state to assert. The mitigations that ARE built carry their own rows.

*Supersedes: none — new. Decision record: `agent-improve/docs/_archive/DECISIONS.md` §S2.*
**Status: SCAFFOLD, populated from the five AI-ACT flags placed 2026-08-23.**

### 68.1 Why DORA structure

> **NOT-MARKABLE:** a risk register. **A risk is a statement about what could happen, not about what exists**, so it has no built/not-built state to assert. The mitigations that ARE built carry their own rows.

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

> **NOT-MARKABLE:** a risk register. **A risk is a statement about what could happen, not about what exists**, so it has no built/not-built state to assert. The mitigations that ARE built carry their own rows.

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

> **NOT-MARKABLE:** a risk register. **A risk is a statement about what could happen, not about what exists**, so it has no built/not-built state to assert. The mitigations that ARE built carry their own rows.

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

> **NOT-MARKABLE:** a risk register. **A risk is a statement about what could happen, not about what exists**, so it has no built/not-built state to assert. The mitigations that ARE built carry their own rows.

**Carried from §46.1, not newly asserted:**

| Risk ID | Item | Status |
|---|---|---|
| **R-INFRA-01** | The v2.1 fallback chain is single-region — Levels 1, 2 and 3 are all in Azure West Europe. A Frankfurt outage collapses three levels simultaneously rather than degrading one at a time. **DORA's ICT resilience obligations require geographic redundancy for continuity of critical functions, which makes this non-compliant for any regulated-entity deployment** — a launch blocker for that market, and EU AI Act data-governance provisions are why the secondary region must be inside the EU | Ratified v2.2 replacement designed (§46.1); **Appendix B item 16**; promotion trigger is *before production launch with real Belts* |

**This row has no AI-ACT flag behind it and is not derived from one.** It is a
DORA-side entry, recorded here because the register is the artifact handed to a
prospect and a bank will ask this question first. It is marked as such so the
flag-is-canonical rule is not read as broken by its presence.

## 69. Spec — computation tools

> **NOT-MARKABLE:** a parent whose CHILDREN own the facts. §16's convention — *“one marker per item, never one per section that mentions it”* — and a row here would be a second claim over the same ground. Six of its seven children own rows, and §69.1 — the seventh — owns one as of this step.

> **NOT-MARKABLE at Part level · its entries are measured at §30 and §31.** **⛑ Corrected 2026-09-11.** This note read *"its entries carry their own markers where they have a built form"* and **they carried none** — a claim that looked fine in a list of sections and failed the moment §55.3's completeness view counted it. **§69.7 carries its OWN marker** — a deliberately absent tool is a buildable claim, and it is the one section here that makes one.

*Supersedes: the inventory-only treatment of the twenty tools at §60.6 (S-F24).*
**Status: RATIFIED 2026-08-26.** File: `knowledge/computation.py`. **Canonical
home for the interfaces.** Source: `docs/_archive/measure_review_and_computation_spec_draft.md`
Part B, ratified in the Measure phase-review workstream. (archived to docs/_archive/; canonical: ARCHITECTURE.md §69)

**This section resolves SPEC-GAP G-25.** Until it landed, not one of the twenty
tools had a signature, a parameter schema, or a return shape stated anywhere —
§60.6 held a complete *inventory* and no *interfaces*, which is why its rebuild
test read "not met". §60.6 stays as the group entry and the EARS behaviors
binding on all twenty; **this section is the detail underneath it.**

**Why a standalone section rather than five per-phase ones.** The twenty are one
subsystem in one file, sharing one set of conventions and one typing law. Split
across §39.1–§39.5 they would be five partial lists with the conventions restated
five times, and the cross-phase pairs that must agree — `calculate_cpk` and
`post_improvement_cpk` — would sit in different sections with nothing forcing
them to be read together. **Appended after §68 so that no existing section
renumbers** (§55.1); the appendices follow it unchanged.

**Spec IDs run S-F37 → S-F56**, continuing the document's existing sequence,
which ended at S-F36. **None of the twenty takes an `S-C` id**: every entry is a
pure function, not a class, so the S-C run is untouched at S-C37.

### 69.1 Common conventions — stated once, binding on all twenty

Per §7's and §40's own style, the repeated header fields are stated here rather
than twenty times below. **Read every entry in §69.2–§69.6 as carrying these.**

| Field | Value for all twenty |
|---|---|
| **Architecture** | §30 (per-phase binding), §7 (typing law), §43.1 (seven-step coaching pattern), §60.6 (EARS B1–B7) |
| **File** | `knowledge/computation.py` |
| **Args schema** | `knowledge/tool_args.py` (§31) — every tool is a separate `@tool` with its own `args_schema=` |
| **Procedure** | step 5.3 |
| **Rebuild test** | *met — see the per-tool rows below* |

- **No mode-argument grouping.** Each row below is a separately named `@tool`.
  Collapsing several into one function behind a `mode=` argument is **BANNED**
  (§30, §60.6 B4). This is why `post_improvement_cpk` is its own entry despite
  sharing `calculate_cpk`'s formula.
- **Inputs are the *semantic* values the tool needs.** Per §7 every captured
  field arrives as a `str`; each tool parses what it needs at the point of use
  and — per §60.6 B3 — **returns a clear reformatting request rather than
  raising or guessing** when it cannot.
- **Output shape lists the keys of the `result` sub-dict** inside the
  `computation_results` entry, whose full shape is §7's
  `{"tool", "inputs", "result", "turn", "phase"}`. **Every value in `result` is
  a string**, per the typing law — a numeric like `cpk: 0.62` is stored as
  `"result": {"cpk": "0.62", …}`.
- **Docstring opening — plain concept first, then the standard term.** All
  twenty tool NAMES stay as they are: `Cpk`, `DPMO`, `GR&R`, `RTY`, `FTQ`,
  `DOE`, `I-MR` and `ANOVA` are the recognised terms and a Belt will meet them
  in every textbook and every audit. **What changes is the first line the coach
  reads.** Each docstring opens with the plain concept, then the standard term
  in parentheses, then plain-language substance —
  `"""Process capability (Cpk) — can the process meet spec as it runs today…"""`.
  The **What it computes** column in §69.2–§69.6 **is** that opening line: it is
  what `knowledge/computation.py` is built from at step 5.3. A Belt who has to
  already know the acronym to find out what the tool does is a Belt the tool
  will not reach.
- **Preconditions are business and methodology preconditions** — what must be
  true of the *project state* before the tool should be called. They are **not**
  argument validation, which is ordinary parsing (§60.6 B2, B3).
- **`metric_name` — when the project tracks more than one criterion.** A project
  may carry several measurement criteria (error rate *and* cycle time), and
  §39.1.2's `baseline_estimate` / `target_value` express that **inside the
  string**, not as extra fields. When more than one is tracked, **the `inputs`
  sub-dict of each `computation_results` entry carries a `metric_name` key**
  naming which criterion that call was for — so four `calculate_cpk` results are
  four attributable numbers rather than four indistinguishable ones.

> **This is additive and changes no tool signature.** Not one of the twenty
> entries at §69.2–§69.6 is altered by it: `metric_name` is a key in the
> **recorded `inputs`**, which §7 already defines as part of the
> `computation_results` shape — it is not a new parameter, and no `args_schema`
> in `knowledge/tool_args.py` gains a field. **Single-criterion projects are
> unaffected**, and `metric_name` is simply absent there; a reader should not
> infer that it became mandatory. **Why a key rather than a schema change:** the
> alternative was making these fields lists, which would have rewritten five
> `{Phase}Output` schemas, §7's typing law and every gate assembly, to express
> something the KPI sub-fields already express in text. §50 renders
> `computation_results` grouped by this key, and `MEASURE_RUBRIC` is what checks
> the criteria actually agree end to end.

> **Trusted-source basis — and why it differs from the rest of this document.**
> Unlike LangGraph and LangChain patterns, these formulas are stable,
> decades-old standards: AIAG MSA-4 for GR&R, Shewhart control-chart constant
> tables, the standard hypothesis-test and OLS formulas, and the 1.5σ
> long-term-shift convention for sigma level. **They do not drift the way a
> package API does.** The Standing Reasoning Protocol's trusted-source check
> here is therefore *"matches the standard method as taught in the ingested BB
> eBook"* (`rag_lookup_methodology`), **not** a web-search-verified library
> call. Applying the package-version check to a Shewhart constant table would
> be a category error.

### 69.2 S-F37 · Define — 1 tool

| S-F | Tool | What it computes | Inputs | Output (`result` keys) | Preconditions |
|---|---|---|---|---|---|
| **S-F37** | `calculate_expected_savings` | **Expected savings** — what closing the baseline→target gap is worth over a year, in money | `baseline_value`, `target_value`, `unit_cost` (cost per defect or per unit of the gap), `annual_volume` | `annual_savings`, `currency`, `calculation_note` — **states the multiplication used**, because a Belt must be able to defend the number at the gate | `baseline_estimate` and `target_value` captured (§39.1.2 fields #5 and #8); `business_case` supplies the cost basis where the Belt has one. **The tool must accept an absent cost and return a reformatting request rather than inventing a unit cost** |

### 69.3 S-F38–S-F45 · Measure — 8 tools

| S-F | Tool | What it computes | Inputs | Output (`result` keys) | Preconditions |
|---|---|---|---|---|---|
| **S-F38** | `calculate_sigma_level` | **Defect rate on a common scale (sigma level)** — how good the process is, expressed so any process compares to any other. Long-term, 1.5σ shift convention | `defects`, `units`, `opportunities_per_unit` — **or** `dpmo` directly | `sigma_level`, `dpmo`, `shift_assumption` (states "1.5σ long-term shift applied") | None beyond a parseable defect count |
| **S-F39** | `calculate_cpk` | **Process capability (Cpk)** — can the process meet spec as it runs today, given both where it sits and how much it varies | `mean`, `std_dev`, `usl` (optional), `lsl` (optional) | `cpk`, `cp` (**only if both limits given**), `binding_limit` — which side is closer, the centring-vs-spread read | **Hard: `stability_assessment` must read "stable"** (§63.2 B1). A `calculate_cpk` call timestamped before a stable verdict is **a grading flag** (§35, §41), not a style note — capability computed across an unstable process is not capability |
| **S-F40** | `calculate_dpmo` | **Defect rate per million chances (DPMO)** — defects scaled so processes of different volume and complexity compare fairly | `defects`, `units`, `opportunities_per_unit` | `dpmo` | None |
| **S-F41** | `calculate_yield_rty` | **End-to-end yield (RTY, rolled throughput yield)** — the share of work that clears every step first time, with no rework anywhere | `step_yields` (list) **or** `step_units_and_defects` (list of pairs) | `rty`, `simple_average_yield` (for contrast), `hidden_factory_gap` — the difference, and **the number that makes RTY's point** | `detailed_process_map` steps populated, **at least 2 steps** |
| **S-F42** | `calculate_ftq` | **First-time quality at one step (FTQ)** — the share that step gets right without rework | `units_processed`, `units_reworked_or_defective` | `ftq` | The step is identified in `detailed_process_map` |
| **S-F43** | `calculate_grr` | **Measurement trust (Gage R&R)** — how much of the variation you can see is the process, and how much is the measuring | `data_type` (`variable` / `attribute`); **variable:** `readings` (operators × parts × trials matrix); **attribute:** `agreement_matrix` (operator ratings per part per trial) | `pct_study_variation` (variable) **or** `pct_agreement` (attribute); `repeatability_pct`, `reproducibility_pct`; `verdict` — `acceptable` <10%, `marginal` 10–30%, `unacceptable` >30% (**AIAG MSA-4 bands**) | **None — this precedes the baseline by design.** It is the tool behind `measurement_system_validated`, coached before `baseline_mean` |
| **S-F44** | `calculate_sample_size_proportion` | **How many to sample, for a percentage** — the count needed to pin a proportion within a stated margin | `expected_proportion`, `margin_of_error`, `confidence_level` (default `0.95`) | `required_n` | None |
| **S-F45** | `calculate_sample_size_mean` | **How many to sample, for an average** — the count needed to detect a difference of a stated size | `estimated_std_dev`, `detectable_difference`, `confidence_level` (default `0.95`), `power` (default `0.80`) | `required_n` | None |

### 69.4 S-F46–S-F50 · Analyse — 5 tools

| S-F | Tool | What it computes | Inputs | Output (`result` keys) | Preconditions |
|---|---|---|---|---|---|
| **S-F46** | `t_test` | **Is the gap between two averages real? (t-test)** — **Welch's by default**, equal-variance only if the Belt states it | `sample1`, `sample2` (raw values **or** `{mean, std_dev, n}` summaries), `paired` (bool) | `t_statistic`, `degrees_of_freedom`, `p_value`, `significant` (`"yes"`/`"no"` at α=0.05) | One of `vital_few_drivers` names the factor under test |
| **S-F47** | `chi_square_test` | **Are two categories related? (chi-square test)** — association between two categorical variables | `contingency_table` (rows × columns of counts) | `chi_square_statistic`, `degrees_of_freedom`, `p_value`, `significant` | Categorical data for both variables; **expected cell counts ≥ 5** — below that the tool returns a reformatting / small-sample warning (§60.6 B3) |
| **S-F48** | `anova` | **Do three or more groups differ? (ANOVA, analysis of variance)** | `groups` (list of raw-value lists or summaries) | `f_statistic`, `df_between`, `df_within`, `p_value`, `significant` | At least 3 groups |
| **S-F49** | `pearson_correlation` | **Do two numbers move together? (Pearson correlation)** — strength and direction, not cause | `x_values`, `y_values` (paired) | `r`, `r_squared`, `p_value`, `strength_label` — negligible / weak / moderate / strong, standard \|r\| bands | Paired continuous data, **n ≥ 10** (methodology floor). Below it the tool **returns a warning, not a suppressed result** — the Belt decides |
| **S-F50** | `linear_regression` | **How much does Y change when X changes? (simple linear regression, OLS)** — fits Y = a + bX | `x_values`, `y_values` (paired) | `slope`, `intercept`, `r_squared`, `equation_string`, `p_value` | Same as `pearson_correlation`; **typically run after it, on the same pair** |

### 69.5 S-F51 · Improve — 1 tool

| S-F | Tool | What it computes | Inputs | Output (`result` keys) | Preconditions |
|---|---|---|---|---|---|
| **S-F51** | `calculate_doe_main_effects` | **Which factor actually mattered? (DOE main effects)** — the effect of each factor from a designed experiment | `factors` (names plus the two levels each ran at), `design_matrix` (which level each factor was at, per run), `responses` (measured output per run) | `main_effects` (per-factor effect size), `ranked_factors` (largest effect first) | `experiment_justification` records that a **DOE** was chosen — not "simplified", not "none" (§63.4 B1) |

### 69.6 S-F52–S-F56 · Control — 5 tools

| S-F | Tool | What it computes | Inputs | Output (`result` keys) | Preconditions |
|---|---|---|---|---|---|
| **S-F52** | `xbar_r_chart_limits` | **Control limits for batched measurements (X̄-R chart)** — the lines that separate normal variation from a real signal | `subgroups` (list of equal-size value-lists) | `x_bar_bar` (centre line), `ucl_x`, `lcl_x`, `r_bar`, `ucl_r`, `lcl_r` | Subgroup size **≥ 2 and constant** across subgroups (standard A2 / D3 / D4 constants by subgroup size) |
| **S-F53** | `imr_chart_limits` | **Control limits for one-at-a-time measurements (I-MR, individuals and moving range)** | `values` (single time series) | `x_bar` (centre line), `ucl_i`, `lcl_i`, `mr_bar`, `ucl_mr` | **The default choice whenever data is one-per-period.** A Belt SHALL NOT be coached into inventing subgroups to force `xbar_r_chart_limits` (§30, §60.6 B7) |
| **S-F54** | `p_chart_limits` | **Control limits for a pass/fail rate (p-chart)** — for when the batch size changes between periods | `subgroups` (list of `{defectives, n}`) | `p_bar`, `ucl_note` — **limits vary per subgroup by `n`**, so it returns the formula plus the per-subgroup array, never one flat number | Attribute (pass/fail) data |
| **S-F55** | `c_chart_limits` | **Control limits for defect counts (c-chart)** — for when the area of opportunity is constant | `counts` (defect count per unit or period) | `c_bar`, `ucl`, `lcl` | **Constant area of opportunity** across periods |
| **S-F56** | `post_improvement_cpk` | **Capability after the fix (post-improvement Cpk)** — the same capability figure on the new data, set against the baseline | `mean`, `std_dev`, `usl` / `lsl`, `baseline_cpk` (for the comparison) | `cpk`, `improvement_delta` (vs `baseline_cpk`), `meets_target` (`"yes"`/`"no"`) | Control's stability re-check passes first — **the same stability-before-capability rule as `calculate_cpk`** (§41) |

> **Why `post_improvement_cpk` is a separate tool from `calculate_cpk`.** Same
> formula, two entries — deliberately. §30 binds tools per phase and §60.6 B4
> bans mode-argument grouping, so a single `calculate_cpk(mode="post")` is not
> available. **The two MAY share a private helper; they are two `@tool`s.** The
> difference is not the arithmetic but the contract: `post_improvement_cpk`
> additionally takes `baseline_cpk` and returns `improvement_delta`, which is
> the number Control's `post_improvement_metrics` is graded against (§63.5 B2).

### 69.7 The Measure control-chart boundary — a tool that is deliberately absent

> `xbar_r_chart_limits` nor `imr_chart_limits` is bound to Measure, asserted by
> `test_measure_binds_no_chart_limit_tool`. **A deliberate absence is a
> buildable claim**, and this is the one section in §69 that carries one ·
> **closes:** `[none]`

**`stability_assessment` (Measure, gate-required) is coached as a visual,
qualitative run-chart read** — *"plot it, tell me what you see"* — **with no
calculated control limits.** Neither `xbar_r_chart_limits` nor `imr_chart_limits`
is bound to Measure: §30's Measure list contains no chart-limit tool, and
Measure already sits at **16 of the 16-tool ceiling** — ON it, not under it —
so adding one would BREACH the cap, not approach it, and needs its own
amendment. *(Corrected 2026-09-11: this read "15 of the 16", true until
`load_evidence_series` made the universal set eight on 2026-09-09 and took
Measure to 16. The same caption drift this document keeps finding.)*

**Formal control-chart mathematics is Control-only** — S-F52 through S-F55.

**This is stated here so it is not rediscovered later as a "missing tool".** It
is consistent with the worked example in `dmaic-measure-phase/SKILL.md`, which
reads a run chart by eye ("ran between 10–14% except two weeks") rather than
citing a calculated limit. **A clarifying note, not a change** — nothing about
the inventory or the bindings moves.

---

# Appendices

---

## Appendix A — Provenance index

**Old reference → this document.** Use this to resolve any `§X` citation in
`agent-improve/CLAUDE.md`, `agent-improve/docs/_archive/DECISIONS.md`, `agent-improve/docs/REVIEW_DECISIONS.md`, the SKILL.md
files, or code comments.

### A.1 `REFACTORING_AGENT_IMPROVE.md` → this reference

Moved to [docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12435](docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12435) on 2026-09-25 (step 6.66).

### A.2 `agent-improve/ARCHITECTURE.md` → this reference

Moved to [docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12499](docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12499) on 2026-09-25 (step 6.66). The absorbed v2.2.16 original is at commit `8533879`.

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

**A dated snapshot of 2026-08-21, now stale.** Moved to
[docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12771](docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12771)
on 2026-09-25 (step 6.66). Build status lives in `docs/REFACTORING_PROCEDURE.md`
Appendix F.
---


## Appendix F — The v2.2.16 registers

**Historical record of the v2.2.16 design document's §17–§18.1; not binding, not
maintained.** Every decision in it is stated as a conclusion in the section that
owns its topic.

### F.1 Decisions Resolved (v2.2) — the former §17

Moved to [docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12837](docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12837) on 2026-09-25 (step 6.66).

---

### F.2 Change Log — the former §18

Moved to [docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12875](docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12875) on 2026-09-25 (step 6.66).

#### F.2.1 Amendment procedure — the former §18.1

Moved to [docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12916](docs/_archive/ARCHITECTURE_slimmed_2026-09-25.md#L12916) on 2026-09-25 (step 6.66). §56 is the current amendment procedure.

---

*End of document.*
