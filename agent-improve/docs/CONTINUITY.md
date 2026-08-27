<!--
Document: agent-improve/docs/CONTINUITY.md
Version: 4.6 — 2026-08-27
Purpose: Session-start orientation. A new session reading ONLY this file should
         be able to orient fully and continue without losing a day.

MAINTENANCE RULE: when a version number, a step, or a document location
changes, update this file in the same commit. Verify claims against the files
themselves; do not carry a line forward because it was here before.

v4.6 delta (2026-08-27): IMPROVE phase review done — §39.4 landed with its
coaching script embedded, IMPROVE_RUBRIC gains both guards + DOE belt-gating,
Improve SKILL.md conformed (it existed; field order contradicted §39.4.2).
Define's §32 gap closed — calculate_expected_savings seven-step block added.
Only Control (§39.5) remains stubbed. ARCHITECTURE.md v1.18, CLAUDE.md 2.2.28.

v4.5 delta (2026-08-27): §39.2.10 / §39.3.10 now embed their coaching scripts;
all three phase sections are authoritative-during-refactor with byte-exact
SKILL.md generation. Doc-content only. ARCHITECTURE.md v1.17.

v4.4 delta (2026-08-27): ANALYSE phase review done — §39.3 landed (12
subsections), F-13 CLOSED via `references_metric_name` on the S-C32 shape,
Analyse SKILL.md rebuilt (it existed; its field order contradicted §39.3.2) and
ANALYSE_RUBRIC gains the two methodology guards. Analyse is now a ratified
exemplar alongside Define and Measure. §39.4/§39.5 still stubbed; F-14 still
open but its reference shape is now defined. ARCHITECTURE.md v1.16,
CLAUDE.md 2.2.27.

v4.3 delta (2026-08-26): Measure naming convention + structured metric registry
applied (7 renames; metric_definitions + phase_metrics; §39.2 written;
single-authority invariant enforced and unit-tested). ARCHITECTURE.md v1.15,
CLAUDE.md 2.2.26. ROOT REFERENCE NOT RENAMED and now diverges on field names —
expected per CLAUDE.md §0.12, owed at back-port once Improve settles.

v4.2 delta (2026-08-26): the `baseline` -> `baseline_metric` rename is APPLIED
and CLOSED (commit below). ARCHITECTURE.md v1.13, CLAUDE.md 2.2.25.

v4.1 delta (2026-08-26 PM session): Define FINALIZED to 12 required fields /
no tiers (supersedes v4.0's 15/8-Tier-1). WATCH 3 and WATCH 8 CLOSED
(CLAUDE.md 2.2.24, commit d1c7fa3). Procedure reconciled to today's out-of-band
commits. Phase-review workstream OPENED — Define done, Measure in progress.
Computation-tools decision recorded. OneDrive access for Claude Desktop recorded
in §0.
-->

# AgentLean — Session Continuity Guide
# Version 4.6 — 2026-08-27

> **Read this first, then stop reading it.** This file orients. The binding
> documents are named in §2 and they win on every point of detail.

---

## 0. Environment note for Claude Desktop — READ, stop relitigating this

**Claude Desktop has live read access to the OneDrive that holds this repo**
via the Microsoft 365 connector. It can find and READ any file under
`_DEVELOPMENT/AgentLean/…` — `ARCHITECTURE.md`, `CLAUDE.md`,
`REFACTORING_PROCEDURE.md`, this file, the phase source, anything. Use
`sharepoint_search` / `sharepoint_folder_search` to locate, then `read_resource`
on the returned URI to read. **Do NOT ask the user to paste files that are in
the repo — read them.** ARCHITECTURE.md is large; read it targeted (search for
the section, read the region) rather than whole.

**Write access is READ-ONLY through the connector** — `sharepoint_upload_file`
returns 403 (a permanent permission boundary, not transient). So Claude Desktop
**produces updated documents as files for the user to save**, and hands
**intent briefs** to Claude Code for anything touching the repo. It does not
write to OneDrive directly.

**Workflow split (unchanged):** Claude Desktop reasons, ratifies, and drafts
document amendments as prose. Claude Code (VS Code) executes ALL repo changes —
it has SessionStart context, the drift-check hook, and `/verify-current-version`.
Desktop does NOT generate implementation prompts; it hands Claude Code a short
intent brief pointing at the ratified doc.

---

## 1. What this project is

**AgentLean** is a three-agent platform for Lean Six Sigma practitioners:

| Agent | Purpose | Status | Port |
|---|---|---|---|
| **Agent Resolve** | Incident problem-solving (8D) | Production | 8010 |
| **Agent Improve** | DMAIC coaching | **In refactor — active work** | 8020 |
| **Agent Flow** | Flow / value-stream | Future, not started | 8030 |

**Agent Improve** coaches a Belt through Define → Measure → Analyse → Improve →
Control, capturing what they produce and holding a quality gate between phases
that the Belt explicitly approves. Long-running agentic system on LangGraph:
hierarchical subgraphs, a Planner/Executor pair per phase, eight middlewares in
a fixed order, a four-layer validation stack, and a nine-step human-in-the-loop
gate.

**Stack:** FastAPI · LangGraph ≥1.2.6 · LangChain 1.x · Azure OpenAI · Azure AI
Search · Azure Blob · Azure Cache for Redis *(not yet provisioned)*.
**MCP is architecturally excluded** for Improve — not deferred.

---

## 2. The document map

### Binding — three documents

| Document | Scope | Version |
|---|---|---|
| **`/AGENTIC_ARCHITECTURE_REFERENCE.md`** *(monorepo root)* | The platform architecture; binds all three agents | **1.7.2** |
| **`agent-improve/CLAUDE.md`** | The rules. Per agent | **2.2.24** |
| **`agent-improve/ARCHITECTURE.md`** | Agent Improve's own architecture; a 2026-08-22 copy of the reference, deliberately diverging | **1.10.x** |

**Where to edit what:** platform-wide → root reference · Improve-specific →
`agent-improve/ARCHITECTURE.md` · a rule → `CLAUDE.md`. The two architecture
files diverge intentionally; there is no sync check. `CLAUDE.md`'s `§` citations
point at the ROOT reference, not the local copy.

### The route

**`agent-improve/docs/REFACTORING_PROCEDURE.md`** — the ordered path from the v1
tree to the target. 38 steps, spine 2.3 → 11.2, one step = one commit, each
traces to a reference section and names one verification method. **Appendix D is
the machine-readable step index the session-start hook parses.**

### Today's ratified working docs (this session)

| Doc | What it is |
|---|---|
| `docs/DEFINE_AMENDMENT_2026-08-25.md` | The original Define spec (§39.1). Superseded on tier counts by the finalization; kept as history |
| `docs/DEFINE_FINALIZATION_2026-08-26.md` | **Authoritative Define spec: 12 required fields, no tiers (Option A)** |
| `docs/PROCEDURE_RECONCILIATION_2026-08-25.md` | The four edits reconciling the procedure to the out-of-band commits |

### Historical record — not binding, do not cite in rules

`docs/REFACTORING_AGENT_IMPROVE.md` (the review register, best source for *why*)
· `docs/EDUCATIONAL.md` (frozen) · `docs/DECISIONS.md` · `docs/REVIEW_DECISIONS.md`
· `docs/BIBLE_VERIFICATION_LOG.md`. The reference's **Appendix A** resolves old
`ARCHITECTURE.md §X` / `REFACTORING §X` citations.

---

## 3. What is DONE

### The document work — complete and signed off
Full architectural review; `CLAUDE.md` rewrite (now **2.2.24**); the reference
written and verified (Task 3 / 3B); absorption + citation sweep; the Refactoring
Procedure written; reference sign-off granted.

### The code refactor — one spine step done
**Step 2.3 — dependency upgrade. DONE** (`95926d6`): langgraph 1.2.11,
langchain 1.3.16, langchain-core 1.6.0, langchain-classic 1.0.8. pytest 6/6.
**The LangGraph gate on steps 4.1–4.4 and 8.2 is CLEARED.**

### This session's commits (2026-08-25 → 26)

| Commit | What landed |
|---|---|
| `73ba7fb` | G-01 + G-02 (Level 2 Command routing + Belt REJECT) |
| `871637f` | Knowledge-index rebuild → `improve_knowledge_index_v3` live |
| `4701a09` | Define schema/validator/skill + CoachingResponse presentational fields |
| `9d9e77c` | Procedure reconciliation (Step 9.0 recorded, 3.4 banner, WATCH 7 row) |
| `d69a52c` | Procedure/reconciliation stale-figure fixes |
| `d1c7fa3` | **WATCH 3 + WATCH 8 CLOSED** — CLAUDE.md → 2.2.24, §0.18 amendment (218→259; Define counts) |
| *(pending)* | Define FINALIZATION — 12 required / no tiers (see §5) |

### Knowledge index — live state
`improve_knowledge_index_v3` — 1,184 docs, BB eBook only, **259 `general`**,
LLM-classified at ingest (cheap model, temp 0.0). Bound by
`AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX` in `.env` (local swap; one-line rollback
to `improve_knowledge_index`, retained at 1,369). Contamination gone (8D no
longer surfaces on Analyse queries). `_v2` (keyword interim) supersede-able,
delete when `_v3` confirmed good.

---

## 4. Where the code actually stands

> **The codebase is still v1. One spine step of 38 is done (2.3).** No
> architectural code written yet. Next spine step: **2.4** — `set_entry_point`
> → `add_edge(START, …)`.

> **The checkpointer is WIRED but INERT** — zero checkpoints ever written;
> `routes.py` discards the compiled graph and dispatches by hand. Closed by
> step 4.2.

Measured `agent-improve/backend/`: 55 files (~7,900 lines), 11 flat graph nodes,
all sync `def`, 20 `response.content` sites, 6 LLM roles (target 11).
Not-yet-existing: `core/substate.py` · `core/store.py` · `middleware/` ·
`validation/` · `knowledge/{computation,tool_args,fusion}.py` ·
`core/reliability.py` · `core/diagrams.py` · `phases/{phase}/{graph,nodes,mappers}.py`.

---

## 5. The active workstream — PHASE REVIEWS, then the backbone, then build

**Decision (2026-08-26): phases are reviewed individually BEFORE the backbone is
finalized, because the phases define what fields the state/schemas must hold.**
Sequence: review each phase to a five-point bar → finalize backbone (state,
schemas, CoachingResponse) from the complete picture → build via the procedure
(horizontal order, resuming at 2.4).

**Five-point "refactor-ready" bar per phase** (freeze when met; no deeper
polishing — the discipline is "is this preventing a mis-build or just prettier?"):
1. Field list final (names, types, required-or-not, coaching order).
2. The three files agree (schema · validate · SKILL.md share one vocabulary).
3. Cross-phase reads named (what it reads from prior phases, by exact field name).
4. No internal contradiction (numbers/names identical everywhere they appear).
5. Mechanics trusted-source-verified.

**Backbone mechanics — VERIFIED (2026-08-26), once, horizontally.** Checked
against current LangGraph docs (updated <1 day prior) + source via DeepWiki:
checkpointer inheritance via `checkpoint_ns` (subgraph compiles with none,
inherits parent) ✓; static-discovery constraint (invoke in a node, never in a
tool) ✓ current; Pattern B (wrapper-node invoke) validated as avoiding the
per-thread-subgraph parallel-call limitation ✓; `thread_id`/`ainvoke` resume
contract ✓; "zero checkpoints written" explained (ainvoke+thread_id never
actually called). **Verdict: backbone mechanics SOUND.** The G-44 local repro is
still technically owed (WATCH 1) but is deferred to build (step 4.2) where the
code runs anyway.

### Phase-review status

| Phase | Status |
|---|---|
| **Define** | **DONE — being FINALIZED.** 12 required fields, NO tiers (Option A). See below |
| **Measure** | **IN PROGRESS.** Schema exists (§40, 14 fields). Rulings captured; capture-review nearly closed; computation-tools spec pending |
| Analyse / Improve / Control | Not started. Schemas exist in §40; need the ordered coaching + SKILL.md + tier decision |

### Define — FINALIZED (authoritative: `DEFINE_FINALIZATION_2026-08-26.md`)

**12 required fields, NO Tier 1/Tier 2 split. Option A — every field
gate-required; missing any → gate fails.** Order (= planner `field_index`):
`business_case, team, voc_summary, problem_statement, baseline_estimate,
project_scope, goal_statement, target_value, target_date, secondary_metrics,
process_map_sipoc, issues_and_barriers`.
- **`baseline_estimate`** (NOT `baseline` — too generic; reverses the earlier
  `baseline` rename). `target_value` and `baseline_estimate` are **discrete**
  fields, not folded into `goal_statement` — Control compares target-vs-actual
  and needs machine-readable values (the measurement thread).
- `target_date` = **planned** completion (PM parameter). Control captures the
  **actual** close date — `actual_close_date` to be ADDED to Control at its
  review (forward note).
- `problem_statement` composed from 5W2H coaching (coach elicits granularly,
  stores one SMART statement; anti-hallucination: assemble the Belt's words,
  invent nothing).
- `process_map_sipoc` = dict, 6 keys incl `process_metrics`; SIPOC is structured
  capture (no computation tool); shown-then-built column-by-column; visual via
  `propose_diagram` (G-30, open).
- Tiers REMAIN for the other four phases — decided at each review. Option A is
  Define-only, because Define has no genuinely-optional field; Measure does (MSA).

**Owed for Define — CLOSED 2026-08-26.** The finalization is applied to
ARCHITECTURE.md (§40/S-C27, §35, §39.1, all count mentions, gate-assembly sample)
at 12 required / no tiers; `schema.py`, `validate.py` and SKILL.md are aligned to
the 12-field list as one atomic unit (§56.1); and **the `baseline` →
`baseline_metric` rename is applied and closed** — the last outstanding half.
CLAUDE.md was amended separately and properly, via §0.18 and §0.19 (2.2.25), not
in a feature commit. `orchestrate.py` remains untouched — **WATCH 7 still open**,
still step 4.1.

> **The rename landed the wrong way first.** Commit `885defc` renamed
> `baseline_metric` → `baseline`, following `DEFINE_FINALIZATION_2026-08-26.md`,
> which states that direction. **§5 here is authoritative and reverses it**;
> `885defc` is superseded on this point only — its 12-required/no-tiers work
> stands. **`DEFINE_FINALIZATION_2026-08-26.md` still states the wrong
> direction** and is left as the dated record it is; if it is ever re-applied
> verbatim it will re-introduce the collision.

### Measure — rulings captured (2026-08-26), review continuing

- **Rename `baseline` → `baseline_metric` EVERYWHERE — APPLIED 2026-08-26.**
  (Define's field and Measure's read of it.) `baseline` collided with
  `baseline_mean` / `baseline_sigma` / `baseline_metrics`. Done across
  ARCHITECTURE.md (incl. §28.1's collision example, which was *precisely* this
  pair), CLAUDE.md §9.7, `phases/define/schema.py`, `skills/dmaic-define-phase/
  SKILL.md`, and the Analyse orchestrator's v2-target-name comment.
  **Measure's SKILL.md §10 already read `baseline_metric` and needed no change.**
  The three sibling fields are untouched — they are the collision, not casualties
  of it. Verified by a raw unfiltered `baseline` sweep: every survivor is
  either an amendment record describing the rename, or Measure's own `"baseline"`
  **section key** in `orchestrate.py`, which groups `baseline_period` /
  `_sample_size` / `_mean` / `_variation` / `_summary` and is not this field.
- **MSA (`measurement_system_validated`) stays optional (Tier 2)** — but the
  coach must actively OFFER and EXPLAIN it (heavy, not always needed) and let the
  Belt choose, not silently skip. Measure KEEPS tiers (unlike Define) because it
  has a genuinely-optional field.
- **Measure SKILL.md opens with a DEFINE RECAP** — show the Belt the key Define
  parameters/decisions (problem, baseline_estimate, target, SIPOC, process KPIs),
  then a guideline of what to measure, showing all options ("define exactly all
  options — what to measure and how").
- Cross-phase thread is well-designed (Measure reads Define's baseline as a
  named field; writes `detailed_process_map["baseline_metrics"]`; Analyse reads
  `vital_few_drivers` + `baseline_mean`).

### Computation-tools — the decision that governs Measure onward

**The RAG knowledge index teaches methodology; a SEPARATE computation-tool layer
CALCULATES actual outputs from Belt-uploaded data.** Distinct layers. Measure is
where computation becomes essential (baseline_mean, baseline_sigma, DPMO,
stability/control-chart, Cpk capability [only valid after stability — EARS B1],
MSA/GR&R). "How to measure" = "which computation tool runs."

**Ratified model:** the ARCHITECTURE holds the tool **specifications** (name,
what it computes, inputs, output shape → `computation_results`, preconditions,
phase). The **code** is written during refactoring (procedure step 5.3), by
Claude Code. So specifying ~20 tools is bounded spec work, not building an
engine now.

**Container decision (OPEN, next up):** the computation tools should be a
STANDALONE subsystem spec (reusable across all 5 phases — Pareto/Analyse,
Cpk/Measure, regression, control charts), NOT embedded inside Measure's section.
Each phase's review NAMES its required tools; the computation-tools spec section
DEFINES them. `EXCEL_SHEET_TOOL_MAP` (in `ingest_knowledge.py`, preserved at
`docs/EXCEL_TOOL_INVENTORY.md`) is the ~20-tool build-inventory. G-25 (tools) +
G-36 (upload endpoint) resolve here at the spec level. Data enters via
`improve_evidence_index`; tools are read-only `@tool` functions; seven-step
computation pattern §43; no fallback-fetch.

**Immediate next step:** finish Measure's capture review (fields, recap, MSA
coaching, the rename) which yields Measure's NAMED computation requirements →
then write the computation-tools spec section (all ~20, buildable accuracy).

---

## 6. Open items, gates and watches

### Gated — do not schedule work against these
- **`RunControl.request_drain()`** — UNCONFIRMED, may not exist (ref §45). Gates step 8.5 only.
- **Azure Cache for Redis** — not provisioned. Gates step 8.4 only.
- **Two Azure index schema changes** — RATIFIED, NOT APPLIED. `improve_evidence_index` gains `phase` + `uploaded_at`; `improve_case_index` `embedding` → `content_vector`. Batch — step 9.1. (Independent of the knowledge-index rebuild, which touched a different index.)

### SPEC-GAP register
**`ARCHITECTURE.md` §66 — 44 identified, 9 closed, 35 open. Group A empty**
(no founder rulings outstanding). G-38 closed 2026-08-26 (Define field order).
Pick the next gap from §66. Group D holds the computation layer (G-25, G-36).

### Watches (owed work, NOT §66 gaps — the register will not surface them)

- **WATCH 1 — §16 persistence repro owed.** Documentation-verified 2026-08-26
  (current LangGraph docs + source); a LOCAL repro against the pinned version is
  still owed. Deferred to step 4.2 where the code runs. Not a blocker.
- **WATCH 2 — two venvs / stale-blocker.** Hook reads the ROOT venv (1.1.10);
  `agent-improve/.venv` is 1.2.11. Confirm which is authoritative before editing
  any doc that states the blocker.
- **WATCH 5 — citations must say "PDF page", not "page".** `page_number` is the
  PDF index; printed number is piecewise-offset. Fix belongs in the (unbuilt)
  citation renderer.
- **WATCH 6 — PDF page 302 ships as `general`** (Azure content-filter false
  positive, permanent, not retried). Genuinely Analyse content; reachable
  everywhere via `general`.
- **WATCH 7 — v1 Define gate inert until `orchestrate.py` migrates.**
  `validate.py` reads v2 names; `orchestrate.py` still writes v1 (`what`/`where`/
  `scope_in`…). The rename landed ahead of its writer — NOT a defect, no shim
  (§17). Owed: migrate `orchestrate.py` AND the Define cross-phase briefs in
  analyse/improve/control at **step 3.4/4.1**. Do not switch readers first.
- **WATCH 9 — `CoachingResponse`'s four presentational fields render nowhere
  yet.** `explanation`/`example`/`prompt`/`progress` in the schema; UI half is
  the UI rebuild (step 10.2). The four Measure/Analyse/Improve/Control SKILL.md
  files must instruct the coach to populate them when written (only Define's does).
- **Hook wrinkle (owed decision):** the session-start hook skips only BLOCKED/
  GATED when picking "next", not `done`. Step 9.0 landed as `feat(knowledge):`
  (not `refactor(arch-v2): commit 9.0`), so it never appears in the git-log scan
  and can trap the "next" pointer once 8.3 lands. Two-line fix: add `done` to
  `_UNAVAILABLE_STATUSES` in `.claude/hooks/session-start-context.py`. Same trap
  applies to any future out-of-band step.

**CLOSED this session (were WATCH 3 + WATCH 8):** CLAUDE.md's stale "218
`general`" → 259 and Define "6 Tier 1 / 15-6-5-4" figures — corrected via the
§0.18 amendment, commit `d1c7fa3`, CLAUDE.md → 2.2.24. **CONTINUITY:335's old
WATCH-8 entry retired here.** WATCH 4 (drift-registry pattern-2 scope) — verify
whether still owed.

### Parallel workstreams — not steps, do not block the spine
- **Five SKILL.md files** — Define's written; Measure/Analyse/Improve/Control
  owed (must include the CoachingResponse-population instruction, WATCH 9).
- **Eval dataset (§52)** — becomes load-bearing once step 6.2 lands; the >10%
  regression threshold is asserted, not measured.

---

## 7. Session protocol

### Before starting
1. Read the session-start hook output (git state, last completed commit, next
   step, dependency drift).
2. Confirm the working tree is clean and pushed.
3. Open the procedure at the next step; check Precondition, run prompt, run
   Verify. **OR** — if in the phase-review workstream (§5) — resume there:
   finish Measure, then the computation-tools spec, then Analyse/Improve/Control.
4. If resolving a SPEC-GAP, follow the Standing Reasoning Protocol below.

### Hard rules
- **Never run `agent-improve/start.ps1`** — it `git reset --hard origin/main`.
  Start the server: `cd agent-improve; .\.venv\Scripts\Activate.ps1; uvicorn backend.app:app --host 127.0.0.1 --port 8020 --reload`
- **Never `git add -A`** — stage by name.
- **Every commit** ends with `Co-Authored-By: Claude <noreply@anthropic.com>`;
  bodies say what changed, where, and why.
- **Refactor commits:** `refactor(arch-v2): commit X.Y — <what changed>`.
- **`/verify-current-version` before any version/API decision** — the live
  package index is authoritative for what exists now, not any document.

> **Reference sweeps must use raw `grep -rn`** — agent-facing search tools
> filter by `.gitignore` and cannot see gitignored paths. Any "zero remaining
> references" conclusion ends with an unfiltered `grep -rn`.

### STANDING REASONING PROTOCOL — filling SPEC-GAPs
Every spec gap is resolved through this discipline, never a quick local patch:
1. **DETAIL** — the specific fix: exactly what field/function/signature changes.
2. **HOLISTIC** — trace through every SIPOC link it touches (peer runtime call
   edges only — ref §55.1 rule 3). List affected use cases; confirm the fix
   holds across all, not just the one that surfaced the gap.
3. **TRUSTED-SOURCE CHECK** — verify the pattern against current LangGraph/
   LangChain/LangSmith sources (and EU AI Act/DORA for compliance gaps). No
   pattern adopted on plausibility; confirmed or explicitly marked unverified.
4. **USE-CASE FORWARD-NOTE** — record which use case(s) the gap belongs to for
   the later sequence-diagram pass.

Resolving a gap MAY surface new gaps — expand the list when the trace demands.
No gap closes on DETAIL alone.

### The lesson this session keeps re-teaching
**A check that cannot fail is worse than no check, because it is recorded as
evidence.** When you write a verification, first prove it can fail.

---

## 8. Amendment procedure

| Change | Route |
|---|---|
| Platform architecture | Root reference §56 — decision in `DECISIONS.md`, section updated, version bumped, change log |
| A rule | `CLAUDE.md` §18 — plus a numbered `§0.x` change entry |
| Improve-specific architecture | `agent-improve/ARCHITECTURE.md` |
| A rule number cited in `deprecated_patterns.yaml` | Update the registry in the same commit (§55) |
| During Improve's refactor | Improve-specific decisions recorded in `agent-improve/ARCHITECTURE.md`; back-ported to the root reference once Improve settles |

**Never amend a rule in passing while making a feature change.**

---

## 9. Version log

| Version | Date | Change |
|---|---|---|
| **4.6** | 2026-08-27 | **IMPROVE phase review + Define §32 fix.** §39.4 written from the ratified appendix — twelve subsections, coaching script embedded at §39.4.10 per the §39.1.7 pattern. **Two movements**: choose (generate → select on explicit criteria) then prove (pilot → confirm); `selected_solution` at 1, link at 2, `experiment_justification` at 3, `pilot_result` at 4 — **you decide how hard to test after you know what you're choosing between**. `IMPROVE_RUBRIC` gains **two Tier-1 guards** (solution traces to the validated root cause by lookup; pilot before rollout, practical AND statistical) and **explicit DOE belt-gating** (all three answers valid; recommended BB, suppressed GB, asked of both). Improve `phase_metrics` = linkage-plus-pilot; `solution_linked_to_root_cause` now populates `references_metric_name`. `ImproveOutput` stays **14**. **Improve SKILL.md CONFORMED, not created** — it existed at 656 lines with a field order §39.4.2 rejects (it coached `experiment_justification` first). **Define §32 gap CLOSED**: `calculate_expected_savings` had no seven-step block; added to §39.1.7 and the Define SKILL.md after the `target_value` field. **Only Control (§39.5) remains stubbed**; F-14 is its open finding. ARCHITECTURE.md **v1.18**, CLAUDE.md **2.2.28** |
| **4.5** | 2026-08-27 | **§39.2.10 and §39.3.10 now embed their coaching script.** Both claimed §39.1.7's authoritative-during-refactor status while holding only a pointer — nothing for the SKILL.md to be generated from. Both now carry the full script in §39.1.7's format: preamble, phase opening, one block per field in §39.2.2/§39.3.2 order with Explain/Show/Ask/Confirm, one seven-step block per tool, metric literacy, gate-readiness closing; plus Analyse's two-movements framing, 5 Whys and test selection. **Content lifted, not rewritten** — 13/13 tool blocks already had seven steps and moved verbatim; 19/19 field blocks gained the four labelled parts. Fixed on the way in: Analyse's `causal_hypothesis` block showed the old three-key reference shape (now five, with `references_metric_name`), and §39.3.10's "SKILL.md does not exist yet" line. Both SKILL.md restructured to one contiguous `## 3. Coaching content` section and renumbered. **Byte-consistency verified for all three phases** by substring containment. Doc-content only — no schema, no code. ARCHITECTURE.md **v1.17** |
| **4.4** | 2026-08-27 | **ANALYSE phase review.** §39.3 written from the ratified draft — twelve subsections, the two-movements structure (generate qualitatively → validate quantitatively) and the ordering that enforces it: `causal_hypothesis` at 2, validation at 3, **`root_cause_statement` at 5 after it is proven**. **F-13 CLOSED** — `references_metric_name` added to all three cross-phase reference dicts (§63.6, S-C32); the grader resolves the `phase_metrics` entry by metric name rather than reading the bare scalar (§42, B1/B5). **Analyse `phase_metrics` = linkage form**, `"not addressed this phase"` where untouched. `AnalyseOutput` stays **14** — the key is inside the dict value, not a new field. §35 confirms 4 Tier 1 / 5 Tier 2 and `causal_hypothesis` as Tier 2. **`ANALYSE_RUBRIC` encodes two Tier-1 guards**: correlation≠causation, statistical≠practical significance. **Analyse SKILL.md REBUILT, not created** — it existed with a field order §39.3.2 rejects. Also fixed: §63.7 had been left below §63.9 by the v1.15 insert. **F-14 still open**, shape now defined. ARCHITECTURE.md **v1.16**, CLAUDE.md **2.2.27** |
| **4.3** | 2026-08-26 | **Measure naming convention + structured metric registry.** Seven identifiers renamed on the two-tier acronym rule (`baseline_metric`→`baseline_estimate`, `target_metric`→`target_value`, `process_kpis`→`process_metrics`, `baseline_kpis`→`baseline_metrics`, `vital_few_xs`→`vital_few_drivers`, `xy_matrix_summary`→`driver_priority_summary`, `post_improvement_metric`→`post_improvement_metrics`); `baseline_mean`/`baseline_sigma`/`post_improvement_cpk` and all 20 tool names untouched. **`metric_definitions` (Define registry) + `phase_metrics` (all five schemas)** — a fourth exception to the string law, traced by key equality on `name`. **§39.2 specifies Measure in full** (12 subsections, written as an index into the cross-cutting specs). **Single-authority invariant** — `phase_metrics` authoritative, scalars mirror the primary, enforced at `gate_apply` and unit-tested across all five phases (`core/metrics.py`, 22 tests). Counts 18/15/14/14/16; same-field-on-all-five now **three** fields. Metric literacy added (§43.7, §32) and applied to Measure's SKILL.md. Register 46/12/34. ARCHITECTURE.md **v1.15**, CLAUDE.md **2.2.26**. **Root reference deliberately not renamed — diverges until back-port** |
| **4.2** | 2026-08-26 | **`baseline` → `baseline_metric` applied and CLOSED** — founder ruling reversing `885defc`, which had renamed it the wrong direction on the authority of `DEFINE_FINALIZATION_2026-08-26.md`. §5 is authoritative. Renamed across ARCHITECTURE.md (**v1.13**), CLAUDE.md (**2.2.25**, via a proper §0.19 amendment), `phases/define/schema.py`, `skills/dmaic-define-phase/SKILL.md`, and the Analyse cross-phase-brief comment. `validate.py` needed no edit — it imports the field list rather than retyping it, which is why the atomic-unit rule earns its keep. **Siblings `baseline_mean` / `baseline_sigma` / `baseline_kpis` untouched** (27 / 8 / 15 occurrences intact) — they are the collision the rename resolves. Define's owed-item list is now empty; **WATCH 7 (`orchestrate.py`) remains open at step 4.1** |
| **4.1** | 2026-08-26 | **Define FINALIZED to 12 required / no tiers (Option A)** — supersedes v4.0's 15/8-Tier-1; `baseline`→`baseline_metric`; `target_metric`/`baseline_metric`/`target_date` kept discrete (measurement thread); `actual_close_date` forward-noted to Control. **WATCH 3 + WATCH 8 CLOSED** (CLAUDE.md 2.2.24, `d1c7fa3`). Procedure reconciled to the out-of-band commits (`9d9e77c`, `d69a52c`). **Phase-review workstream opened** (§5) with the five-point bar; **backbone mechanics VERIFIED** against current LangGraph. **Computation-tools model ratified** — architecture holds specs, code built at step 5.3; standalone-subsystem container recommended. Measure review in progress. **§0 added: OneDrive read access for Claude Desktop** recorded so it stops being relitigated each session |
| **4.0** | 2026-08-26 | Define fully specified; G-38 CLOSED. `DefineOutput` at 15 fields / 8 Tier 1 (SUPERSEDED by 4.1). §50.1 + §56.1; CoachingResponse gains four presentational fields. Watches 7, 8, 9 added |
| **3.9** | 2026-08-25 | LLM phase classification landed; `_v3` live (1,184 / 259 general); swap done |
| **3.8–3.7** | 2026-08-25 | Knowledge-index rebuild rulings and ingest |
| **3.6** | 2026-08-24 | G-01 + G-02 resolved; Group A empty |
| **3.5x** | 2026-08-24 | G-04 / G-44 chain resolved; watches for the §16 repro and two-venv blocker |
| **3.1–3.3** | 2026-08-24 | Standing Reasoning Protocol added; live gap list |
| **3.0** | 2026-08-22 | Rebuilt from live files |
| 2.8 | 2026-08-19 | Last version before the reference rewrite |

*A new session should be able to act on §4 and §5 without opening another file.*
