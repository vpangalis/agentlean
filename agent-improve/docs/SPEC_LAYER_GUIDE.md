# Specification Layer — Governing Document

**Purpose:** defines the specification layer to be added to
`AGENTIC_ARCHITECTURE_REFERENCE.md`, the format every spec entry follows, the
compliance/risk layer (EU AI Act + DORA register), the new trusted sources, and
the governance rules that keep all of it from drifting.

**This document is BOTH the build instruction for Claude Code AND the
continuity anchor for a new chat.** Read this first to understand where the
work stands and what the target structure is.

---

## 1. Why this exists (the decision and its grounding)

The reference document is an *architecture* — it explains shape and reasoning.
It is not a *specification* — it does not define classes and functions to the
level where code could be rebuilt from it without inventing the missing pieces.
Two seams traced during the 2026-08-22 wiring review (the contradiction
middleware; `route_after_phase`) proved the gap is real and produces exactly
the "endless debugging" failure the founder wants to avoid.

The fix is **Spec-Driven Development (SDD)** — verified against 2026 industry
practice (GitHub Spec Kit, AWS Kiro, the spec-as-source literature). SDD's
three-layer structure is the current professional standard, and AgentLean
already has two of the three layers:

| SDD layer | AgentLean artifact |
|---|---|
| Requirements (what / why) | `AGENTIC_ARCHITECTURE_REFERENCE.md` — architecture + reasoning |
| **Design (how — classes, functions, interfaces)** | **THE GAP — the spec layer this document defines** |
| Tasks (ordered implementation) | `REFACTORING_PROCEDURE.md` — the 38-step procedure |

The spec layer is the missing middle. It goes **inside the reference document**
as a new Part (one document, no separate spec file — separate files re-create
the drift we spent the effort eliminating; SSOT non-overlapping rule).

---

## 2. Structural rules (grounded in SDD/SSOT best practice)

1. **One document.** The spec layer is a new Part of
   `AGENTIC_ARCHITECTURE_REFERENCE.md`, not a separate file.
2. **Define once, reference everywhere.** Each class/function is defined
   canonically in the spec Part. Architecture sections (§5, §6, §14, …) keep
   their *reasoning* but stop *redefining* — they point at the spec entry.
   (Write-through-cache model: the spec is master; architecture prose
   references it.)
3. **Layers separated by volatility.** Architecture (why — stable) and spec
   (how — the interfaces) are distinct, because they change at different rates.
   Switching Azure Blob → Azure Files changes the spec, not the architecture.
4. **Rebuild test = completeness bar.** A subsystem's spec is complete when
   Claude Code could rebuild that subsystem's code from the spec alone,
   without reading the old code. If it can't, there's a gap.
5. **Spec-before-code, always.** When something changes, the spec is updated
   first, then the code. This is an enforced governance rule (see §6), because
   a spec that lags code rots into a useless historical artifact — the exact
   failure SDD exists to prevent.
6. **Full traceability.** architecture § ↔ spec entry ↔ procedure step, all
   three linked, so none can silently drift from the others.

---

## 3. The spec entry template (CALIBRATED — two approved samples in §7)

Every spec entry has up to three layers. A **class** entry uses SIPOC-style
field tables + behaviors + invariants. A **function/node** entry uses all
three below.

### Layer 1 — SIPOC at a glance (orientation)

A six-row table answering, without reading code or a sequence diagram: who
triggers this, what it reads, what it does, what it produces, who consumes it.

| Cell | Content |
|---|---|
| **Supplier** | Who calls it / what upstream node or event triggers it. Many callers → a list, each naming caller + why. A list longer than ~5-6 is a design smell: the function likely does too much and should be split. |
| **Input** | Parameters, state fields read, store keys read, tools bound |
| **Process** | What it does (summary; EARS gives the detail) |
| **Output** | Return dict slice, state fields written, store keys written, interrupts raised, structured-response fields set |
| **Customer** | Who consumes the output / what downstream node reads it |

**Supplier/Customer are cross-checkable:** if A's Customer is B, B's Supplier
list must include A. A mismatch is a wiring bug, grep-able by function name.
This is a verification surface — it would have caught `route_after_phase`
mechanically (its Input "reads gate_attempts from SupervisorState" vs.
SupervisorState having no such field).

### Layer 2 — Behaviors (EARS), as a table

EARS = Easy Approach to Requirements Syntax (Rolls-Royce). Forces testable,
unambiguous phrasing. Table form for scannability:

| # | WHEN (trigger) | THE SYSTEM SHALL (behavior) | Ref |
|---|---|---|---|
| B1 | … | … | §.. |

- `#` gives each behavior a stable ID (B1, B2…) so tests, reviews, and the DORA
  register can cite "executor B4" precisely.
- `Ref` traces each behavior to the architectural section that justifies it —
  checkable against source.

### Layer 3 — ⚠ AI-ACT flag (SELECTIVE — high-risk surfaces only)

Only on functions/nodes that touch a high-risk surface: coaching output, gate
approval, anything that could feed a competence/employment/certification
decision. **Most entries carry NO flag** — pure orchestration/state/utility
functions are not flagged. Selective flagging keeps the compliance layer honest
rather than box-ticking noise.

Format: a short statement of the high-risk surface + an obligation→mechanism
table (which EU AI Act Article, how this node addresses it) + a pointer to the
DORA register row it feeds.

---

## 4. Compliance & Risk layer (new dedicated Part)

### 4.1 EU AI Act compliance posture

**Verified state (as of 2026-08-23):** the Digital Omnibus is enacted law
(Regulation (EU) 2026/1744, in force 27 July 2026). High-risk deadlines are
now FIXED and unconditional:
- **2 December 2027** — standalone Annex III systems (includes **employment**)
- 2 August 2028 — high-risk AI embedded in regulated products (Annex I)

Transparency (Art. 50), GPAI, and prohibited-practices duties are already in
force and were not delayed.

**Classification question (for the founder / legal counsel, not resolved here):**
Agent Improve MAY be Annex III high-risk via the **employment** category — it
coaches professionals and produces assessments that *could* feed competence or
advancement decisions. Whether it crosses the line depends on **deployment**:
if gate outputs feed a formal evaluation → likely high-risk; if a private
learning aid with no institutional consequence → likely not. This is a legal
determination requiring qualified advice before Dec 2027. **The architecture is
designed defensively so that IF high-risk, no retrofit is needed.**

**The eight core provider obligations (Art. 9–15, 43)** and how Agent Improve
already maps to them — Agent Improve has much of the skeleton already:

| Article | Obligation | Existing mechanism |
|---|---|---|
| 9 | Risk management (lifecycle) | The DORA register (§4.2) is this, made operational |
| 10 | Data governance | Azure indexes, evidence provenance (§23) |
| 11 | Technical documentation | This reference document + spec layer |
| 12 | Record-keeping / logging | `step_log`, LangSmith tracing (§51), deterministic keys (§47) |
| 13 | Transparency to users | UI contract — Belt informed they interact with an AI coach (§50) |
| 14 | Human oversight | HITL gates — no field committed without Belt approval (§13) |
| 15 | Accuracy / robustness | 4-layer validation (§35), anti-hallucination, contradiction detection (§37) |
| 43 | Conformity assessment | Downstream — needs the above demonstrable |

### 4.2 DORA-structured compliance risk register

**Why DORA structure:** DORA (Regulation (EU) 2022/2554) applies directly to
financial customers (e.g. demo case IMPR-2026-FS1), who track a third-party AI
vendor as ICT risk. Its register structure is also the *universal* risk-register
shape every industry uses — a manufacturer reads the same table as their risk
register. So one DORA-structured table is **cross-industry by construction**:
legible to a bank as DORA, to a factory as a risk register.

**The register aggregates every AI-ACT flag** into one negotiable table:

| Risk ID | Function | Risk Description | AI Act Art. | Likelihood | Impact | Current Mitigation | Residual Risk | Owner | Customer Negotiation |
|---|---|---|---|---|---|---|---|---|---|

- One row per flagged function. `Risk ID` (e.g. `R-EXEC-01`) is stable.
- The **Customer Negotiation** column is deliberately open — the register is the
  artifact handed to a prospect: "here are our AI's high-risk functions, here's
  how each is already mitigated, here's the residual risk to discuss."
- **The register is DERIVED from the per-section flags; the flag is canonical.**
  When they disagree, the flag wins and the register row is regenerated. Same
  write-through-cache discipline. Each row cites the function + behavior IDs it
  aggregates, so row ↔ flag correspondence is checkable by Risk ID.

---

## 5. New trusted sources (add to reference §55 / Appendix C, Tier 1 for compliance)

- EU AI Act (official): `https://artificialintelligenceact.eu/implementation-timeline/`
- EU AI Act (Commission): `https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai`
- EU AI Act Service Desk: `https://ai-act-service-desk.ec.europa.eu`
- DORA (regulation text): EUR-Lex Regulation (EU) 2022/2554
- SDD method references (for the spec approach itself): GitHub Spec Kit, AWS Kiro docs (kiro.dev/docs/specs)

**Compliance-source discipline:** EU AI Act and DORA are in active
implementation with shifting guidance. Any compliance claim must cite a
current-dated source; if availability can't be verified, mark it
"unverified — requires legal validation" rather than asserting it. (This is not
legal advice; the classification question needs qualified counsel.)

---

## 6. Governance rules (enforced, per the R2 "rules need checkable enforcement" lesson)

1. **Spec-before-code.** Code changes require the spec entry to be updated
   first. Checkable: a code change whose spec entry's last-modified predates it
   is a violation.
2. **Flag-is-canonical, register-is-derived.** The DORA register never leads the
   per-section AI-ACT flags. Checkable: every register Risk ID must trace to a
   flagged function; every flagged function must appear in the register.
3. **SIPOC Supplier/Customer cross-check.** For every function, its Customers
   must list it as a Supplier and vice versa. Checkable by grep on function name.
4. **Define-once.** A class or function name defined in the spec Part must not
   be *re*-defined (schema/signature) in any architecture section — those
   reference it. Checkable: a definition appearing in two section ranges is a
   violation.
5. **Selective flagging.** AI-ACT flags appear only on high-risk-surface
   functions. A flag on a pure utility, or a missing flag on a
   coaching/gate/assessment function, is a review finding.

For any NEW rule added later: state what would catch a violation of it in prose;
if the answer is "nothing," say so in the rule rather than assuming coverage
(the R2 discipline — a rule with no enforcement is a rule that rots).

---

## 7. The two calibrated reference samples

These are APPROVED and define the standard. Every spec entry is built to match.

### 7.1 CLASS sample — `SupervisorState`

*(full entry — Purpose, definition, field table with type/meaning/reducer/
writer/readers, EARS behaviors, invariants, failure modes. See the conversation
of 2026-08-23 for the full text; reproduce it as the class template.)*

Key template features a class entry must have:
- Purpose (one paragraph: role in the system)
- The `TypedDict`/model definition
- Field table: Field | Type | Meaning | Reducer | Writer | Readers
  (Meaning must say what the thing IS, not restate the name)
- Behaviors (EARS table) — including the absent-key/None-handling contracts
- Invariants (single-writer rules, what must not appear here)
- Failure modes (what a KeyError/None means and how readers must handle it)

### 7.2 FUNCTION sample — `phase_executor` (the coach node)

The full three-layer entry:
- **SIPOC at a glance** — Supplier: phase_planner; Input: coaching_plan,
  messages, artifacts, phase_context, bound tools; Process: create_agent + 8
  middlewares, coach on focus_field, produce CoachingResponse; Output: dict
  slice {draft, artifacts, step_log, messages} + contradiction_flag; Customer:
  ContradictionDetectionMiddleware then phase_planner.
- **Behaviors (EARS table)** — B1 coach only on focus_field; B2 structured
  CoachingResponse not prose; B3 populate contradiction_flag on prior-phase
  contradiction; B4 no invented field values; B5 surface tool failure per §27;
  B6 deterministic step_log key.
- **⚠ AI-ACT flag** — high-risk (employment/Annex III if deployed into
  assessment); obligation→mechanism table for Art. 12/13/14/15; feeds DORA row
  R-EXEC-01.
- **DORA row R-EXEC-01** in the register.

*(Full text of both samples is in the 2026-08-23 conversation and should be
transcribed verbatim as the reference examples in the spec Part's preamble.)*

---

## 8. Build sequence (subsystem by subsystem, each rebuild-tested before next)

The spec layer is built one subsystem at a time, verified, then the next. Order
by dependency:

1. **Graph management** (FIRST — the spine; we're already in it via the routing
   gap): SupervisorState, PhaseState, the five nodes (planner, executor,
   validation_stack, gate_review, gate_apply), the Level 2 Command routing (the
   OPEN gap — §13 draws it, §15 states the rule, but no routing code exists;
   this must be designed, not just transcribed), static-edge supervisor wiring,
   thread_id/checkpoint_ns.
2. RAG management (indexes, rag_lookup_* functions, multi-query/RRF, multi-hop)
3. UI management (the UI contract, the all-gate-fields tab, the API surface)
4. Skills (the five SKILL.md, three-level loading, the contradiction-check
   instruction)
5. System prompts (per phase, per node)

Each subsystem: draft spec entries to the template → founder reviews → rebuild
test → Claude Code applies into the reference's new spec Part + strips
now-redundant definitions from architecture sections (pointing them at the spec)
→ commit → next subsystem.

**Compliance layer is woven in as we go** — each subsystem's high-risk functions
get flagged and added to the DORA register during that subsystem's pass, not as
a separate later sweep.

---

## 9. Open item carried into the graph subsystem

**Level 2 (subgraph-internal) routing is unspecified in code.** §13 draws the
branching (field→field, →gate, retry→planner, ≥3→escalation); §15 states
"Command routing inside subgraphs"; but no actual `Command(goto=...)` routing
code exists anywhere. This is a genuine design task (not transcription) and is
the first substantive thing the graph subsystem spec must resolve. The three
decision points to specify:
1. Planner returns `Command(goto="executor")` vs `Command(goto="validation_stack")` on field-complete.
2. validation_stack returns `Command`: pass→gate_review, ≥3→escalation, else→planner (with feedback); it owns gate_attempts increment.
3. gate_review (interrupt) → gate_apply, and what a Belt REJECT does (the coaching-philosophy call — re-coach vs apply-with-edits). **This one needs a founder ruling.**
