# ARCHITECTURE.md AMENDMENT — Define phase, fully specified

**Status: RATIFIED 2026-08-25.**
**Scope: new §41 (Define phase) · new §50.x (response structure) · updates to §20/S-C05, §35, §40, §56, §66.**
**Basis for rebuilding `phases/define/{schema.py, validate.py}` and `skills/dmaic-define-phase/SKILL.md` as one atomic set, plus the shared `CoachingResponse` schema.**

---

## PART A — The atomic-unit principle (new §56 governance rule)

**A phase's `schema.py`, `validate.py`, and `SKILL.md` are ONE atomic unit sharing one field vocabulary. They are always rebuilt together, never independently.**

- `schema.py` (`{Phase}Output`) — the field **names, types, shape**.
- `validate.py` (`DMAICGateValidator`) — which of those fields are **Tier 1** (gate-blocking).
- `SKILL.md` — coaches those **exact field names in the planner's `field_index` order** (§G-38).

They share field names by construction. If SKILL coaches `problem_statement`, schema declares `problem_statement`, validator knows its tier. A mismatch means capture writes `artifacts["problem_statement"]` while `{Phase}Output(**artifacts)` has no such field — gate assembly fails. **Rebuilding one without the others is a §56-class violation.**

**Capture path (how a coached field reaches storage):**
1. Coach LLM call uses `response_format=CoachingResponse`.
2. Captured values arrive in `CoachingResponse.fields_captured` — **shape guaranteed by the schema, truth NOT** (§40).
3. The executor NODE (not the LLM) writes them into `PhaseState.artifacts[field]`.
4. Lives in `artifacts` in-flight, checkpointed each turn (Azure Blob). The planner READS `artifacts` to know what is captured and what `field_index` is next (§6).
5. At the gate, `gate_apply` builds `{Phase}Output(**artifacts)` (Pydantic, no LLM) and writes it ONCE to the Store: `projects/{case_id}/artifacts/{phase}.json` (§9, §33).

**Middleware never captures.** `BeforeModelStateInjection` (`before_agent`) injects prior `artifacts` into context before the call; `ContradictionDetectionMiddleware` (`after_agent`) reads the coach's `contradiction_flag` after. Both READ; neither writes captured fields.

---

## PART B — §41 Define phase, complete specification (new section)

### §41.1 Purpose

Define is the **contract phase**. It turns a vague concern into a specific, scoped, measurable project with an assigned team, before any data work begins. At completion the Belt holds a charter-quality description: the problem, who owns it, what is in/out of scope, the target, and the process at a high level.

### §41.2 The ordered field list — THIS IS the `field_index` sequence the planner walks (closes G-38)

| # | Field (`artifacts` key) | Type | Tier | Notes |
|---|---|---|---|---|
| 1 | `business_case` | `str` | 2 | Strategic rationale — why invest. |
| 2 | `team` | `list[dict]` | 1 | Each entry `{name, role, function}`. Roles per §41.4. |
| 3 | `voc_summary` | `str` | 1 | Who the customers are + what they need. |
| 4 | `problem_statement` | `str` | 1 | ONE SMART statement, **composed from 5W2H coaching** (§41.3). The 5W2H are NOT separate stored fields. |
| 5 | `baseline` | `str` | 1 | Rough baseline stated in Define (rigorous baseline is Measure's job). Founder ruling: stays in Define. |
| 6 | `project_scope` | `dict` | 1 | `{in_scope: str, out_scope: str}` — both explicit. |
| 7 | `goal_statement` | `str` | 1 | SMART, mirrors the problem; carries the target value + date. |
| 8 | `target_date` | `str` (ISO) | 2 | Project completion target. **Single date field** — `estimated_completion_date` is retired (duplicate). |
| 9 | `process_map_sipoc` | `dict` | 1 | Six keys: `suppliers, inputs, process_steps, outputs, customers, process_kpis`. Fewer than six filled = partial-map failure (§41). |
| 10 | `issues_and_barriers` | `str` | 1 | Always last, always Tier 1. "none identified at this stage" is a valid conscious answer. |

**Tier 1 (8):** `team`, `voc_summary`, `problem_statement`, `baseline`, `project_scope`, `goal_statement`, `process_map_sipoc`, `issues_and_barriers`.
**Tier 2 (2):** `business_case`, `target_date`.

> **Reconciliation note — supersedes the built v1 `DefinePhaseInput`.** v1 used granular 5W2H fields (`what/where/when/who_affected/why_it_matters/how_much_baseline/how_goal`), `scope_in`/`scope_out`, and both `target_date` + `estimated_completion_date`. These are **RETIRED.** v2 stores `problem_statement` (composed), `project_scope` (dict), one `target_date`. **The 5W2H survive as the coaching METHOD (§41.3), not as stored fields.** This is a documentation-vs-code divergence resolved in favour of the v2 architecture names; `schema.py` is rebuilt to match. §35's Define Tier-1 list is updated accordingly.

### §41.3 The composed-problem-statement rule (binding)

The coach elicits the problem through 5W2H sub-questions — what / where / when / who affected / why it matters / how much / goal — as **conversational prompts, not fields.** The coach then **composes the Belt's answers into one SMART `problem_statement`** and reflects it back for confirmation. Only the confirmed composed statement becomes `artifacts["problem_statement"]`.

**Anti-hallucination guard (§22):** composition is *assembly of the Belt's own words into SMART form*, never authorship. The coach must not add facts, numbers, or details the Belt did not provide. The Belt confirms accuracy before storage.

### §41.4 The `team` structure (validated against trusted LSS sources, 2026-08-25)

`team: list[dict]`, each `{name: str, role: str, function: str}`. Roles follow standard Lean Six Sigma structure:

- **Project Leader** — the Belt driving day-to-day (Black Belt for complex/cross-functional; Green Belt for departmental).
- **Sponsor / Champion** — secures resources, removes barriers; **approval required at the gate.**
- **Process Owner** — owns the process being changed.
- **Team Members** — subject-matter experts who work within the process.

Coached early (position 2) because the people must exist before the work. RACI framing encouraged, not enforced.

### §41.5 SIPOC handling

`process_map_sipoc` is a **dict, not free text** (six keys). **No computation tool** — structured capture, nothing to calculate. The coach **shows a filled SIPOC example first, then builds the Belt's column-by-column** (guided capture into the dict), offering an upload option. Visual rendering routes through `propose_diagram` (G-30, open). A SIPOC missing any of the six keys is the partial-map failure (§41).

### §41.6 Gate, storage, progress view

- Tier-1 fields block the gate; Tier-2 warn only (§34).
- The **live gate document** renders from `artifacts` (§50) — the secondary tab where the Belt sees progress, with **separate Tier-1 / Tier-2 progress bars**, what is done and what is missing.
- Written once to `store/projects/{case_id}/artifacts/define.json` by `gate_apply` (§9).

### §41.7 The inline SKILL.md content (AUTHORITATIVE during refactor)

> **Authority:** this content is authoritative during the v2 refactor. `skills/dmaic-define-phase/SKILL.md` is generated from it and must match verbatim. On conflict, this section wins until the refactor completes; then authority flips to the code file and this reduces to a pointer.

> **Coaching pattern for every field:** ① Explain (plain, why it matters) → ② Show (worked example, visually distinct, illustration only) → ③ Ask (invite the Belt's version) → ④ Confirm (reflect back, check, advance). Tone: warm, encouraging, never gatekeeping. Assume a capable but possibly non-expert Belt. Responses follow §50.x structure — sectioned, scannable, never bulk prose.

**[OPENING — shown once, when Define starts]**
> Welcome — I'm here to coach you through your improvement project step by step, so you don't need to be an expert. We'll work through five phases together:
> • **Define** — pin down the problem and who's solving it
> • **Measure** — get the real numbers
> • **Analyse** — find the true root cause
> • **Improve** — test and apply the fix
> • **Control** — make the gains stick
> Right now we're in **Define** — the most important phase, because a clear problem is half the solution. I'll explain each thing, show you an example, then ask for yours. Let's go at your pace.

**[1 · business_case · Tier 2]**
> **Explain:** Let's start with the big picture. Before the problem itself, let's be clear on *why this project is worth doing* — what's the pain costing, and why should people care? This is what earns you the time and support to fix it. No need to be formal.
> **Show:** *"Invoice errors cost ~€35k/month in rework and delayed payments, and billing complaints rose 40% this year. Fixing this protects revenue and frees two staff currently spending half their week on corrections."*
> **Ask:** In a sentence or two — why is *your* project worth doing? What's the pain, and what does it cost the business?
> **Confirm**, then move on.

**[2 · team · Tier 1]**
> **Explain:** Now let's name your team — because a project needs people before it needs work. We'll note each person's name, their role, and what they'll do. Don't worry if it's not fully settled; we can refine it.
> **Show:** *"Leader: Anna (Green Belt, runs the project day-to-day). Sponsor: Mark, Finance Director (approves and removes blockers). Process Owner: Jo, Billing Manager (owns the process). Members: two billing clerks (subject-matter experts)."*
> **Ask:** Who's leading this project? Who's the sponsor who can approve and clear obstacles? Who owns the process? And who are your team members — the people who know the work?
> **Confirm** each name with its role and function, then advance.

**[3 · voc_summary · Tier 1]**
> **Explain:** Next, the Voice of the Customer — who your process serves and what *they* actually need. It keeps us honest: we improve what matters to the people receiving the output, not just what we assume is broken.
> **Show:** *"Customers (internal finance teams + external clients) need invoices that are accurate, arrive within 2 days, and match agreed pricing. Top complaint: wrong amounts, then late delivery."*
> **Ask:** Who are the customers of your process — internal, external, or both — and what do they need? What do they complain about most?
> **Confirm**, advance.

**[4 · problem_statement · Tier 1 · composed from 5W2H]**
> **Explain:** Now the heart of Define — the problem statement. I'll ask you a few simple questions, then put them together into one clear statement. We're not solving anything yet, just stating clearly what's wrong.
> **Show:** *"Between Jan–June 2026, 12% of invoices had pricing errors (target: under 3%), affecting the finance team and clients, costing ~€35k/month."* — specific, measurable, time-bound.
> **Ask (one at a time):** What's happening? · Where? · When / since when? · Who's affected? · Why does it matter? · How much (roughly, a number if you have one)? · What would "fixed" look like?
> **Compose & Confirm:** Putting that together, here's your problem statement: *"[composed from the Belt's own answers]"* — does that capture it accurately? *(Guard: assemble only what the Belt said; invent nothing. Store only after confirmation.)*

**[5 · baseline · Tier 1]**
> **Explain:** Roughly, where does performance stand today? A rough number is fine here — we'll measure it properly in the next phase. It anchors the goal.
> **Show:** *"Currently about 12% of invoices contain errors."*
> **Ask:** What's the current level of the problem, as best you know it right now?
> **Confirm**, advance.

**[6 · project_scope · Tier 1]**
> **Explain:** Let's set boundaries — what's *in* scope and, just as importantly, what's *out*. Being explicit about what you're *not* doing protects the project from ballooning.
> **Show:** *"In: UK invoice generation, order receipt to invoice sent. Out: payment collection, non-UK regions, the pricing database."*
> **Ask:** Where does your process start and end (in scope)? And what are you deliberately keeping out?
> **Confirm** both in and out, advance.

**[7 · goal_statement · Tier 1]**
> **Explain:** Your goal should mirror your problem — same metric, a target value, a deadline. That makes success unambiguous.
> **Show:** *"Reduce invoice pricing errors from 12% to under 3% by 30 September 2026."*
> **Ask:** Taking your problem's number — what's the target, and by when?
> **Confirm** it mirrors the problem, advance.

**[8 · target_date · Tier 2]**
> **Explain:** Roughly when do you expect the whole project to wrap up?
> **Ask:** What's your target completion date for the project?
> **Confirm**, advance.

**[9 · process_map_sipoc · Tier 1 · show then build]**
> **Explain:** Now we'll map your process at a high level with a **SIPOC** — Suppliers, Inputs, Process, Outputs, Customers. It's just a one-page view of your whole process. We'll build it together, one column at a time.
> **Show (a filled example, as a table):**
>
> | Suppliers | Inputs | Process | Outputs | Customers |
> |---|---|---|---|---|
> | Sales team | Signed order | 1. Receive order | Invoice (PDF) | Client |
> | Pricing DB | Price list | 2. Look up pricing | Payment request | Finance team |
> | Client | Customer details | 3. Generate invoice | Audit record | Accounts receivable |
> | | | 4. Review & approve | | |
> | | | 5. Send to client | | |
>
> Reads left to right: Suppliers give Inputs; your Process (5–7 high-level steps) turns them into Outputs, which go to Customers.
> **Ask (column by column):** Let's build yours. First, the **Process** — what are the 5–7 main steps, start to end? … then Suppliers, Inputs, Outputs, Customers in turn. And: what do you measure on those outputs? (that's the sixth key, `process_kpis`). You can also upload a SIPOC if you have one.
> **Confirm** the assembled SIPOC as a table; flag any thin column; check all six keys filled. Advance.

**[10 · issues_and_barriers · Tier 1]**
> **Explain:** Last one — what might get in the way? Missing data, people to convince, systems you can't change, timing? Naming these now is what separates projects that finish from projects that stall.
> **Show:** *"Pricing DB owned by IT (sign-off may delay). Two members on leave in August. No clean historical error data yet — may need to collect it."*
> **Ask:** What could get in the way? Be honest — data, people, systems, timing? If genuinely none, "none identified at this stage" is fine, but have a think first.
> **Confirm.**

**[GATE READINESS — closing]**
> Great work — that's Define mapped out, all required deliverables complete. Review everything in the **gate document** tab whenever you're ready and approve to move to Measure. You can still edit anything.

### §41.8 The other four phases

Measure, Analyse, Improve, Control follow this exact section shape. Their field lists depend on **G-27** (mappers) and **G-28** (gate assembly), still open. Define is the ratified exemplar; the other four are stubbed pending those gaps.

---

## PART C — §50.x Coach response structure (new §50 subsection)

*Validated against conversational-UX best practice (2026-08-25): dense LLM prose is a named UX failure mode; structured, scannable, card-based responses are the standard.*

**Coach responses are structured, never bulk prose.** Every coaching turn presents as visually distinct sections, not a paragraph block:

- **Explanation** — what this deliverable is (2–3 short lines).
- **Example** — the worked example, its own visually distinct block, marked as illustration.
- **Your turn** — the request to the Belt, distinct as the call-to-action.
- **Progress** — where they are (e.g. "Define · field 4 of 10"), always visible.

**Reliability rule — schema-backed, not prompt-hoped.** `CoachingResponse` carries the coach's visible message as **discrete presentational fields** (`explanation`, `example`, `prompt`, `progress`), not one free-text blob, so the UI renders each block consistently every turn. Prose-one-turn / structure-the-next erodes trust; consistency is a UX requirement.

**No jargon in the visible structure** (existing §50 rule); technical terms only as small grey secondary labels. **Mobile:** shorter sections, larger tap targets.

> **UI note:** the *rendering* of these fields is part of the UI rebuild (no production UI exists yet for Agent Improve). This section defines the CONTRACT (schema carries structure, §50 mandates it); the UI implements it when built.

---

## PART D — §20 / S-C05 `CoachingResponse` amendment (§56 — shared across all phases)

`CoachingResponse` gains four presentational fields, per §50.x:

- `explanation: str` — the plain-language "what this is."
- `example: str` — the worked example block.
- `prompt: str` — the request to the Belt (the call-to-action).
- `progress: str` — position indicator (e.g. "Define · 4 of 10").

Existing fields (`fields_captured`, `contradiction_flag`, and the rest of S-C05) unchanged. **This is a §56 amendment affecting ALL FIVE phases' coach output and the response-rendering UI** — larger blast radius than the Define-only change; called out as such. Shape guaranteed by schema; content correctness is not (§40) — the presentational fields are still LLM-produced text and subject to the same truth caveat.

---

## PART E — Register / cross-reference updates

- **G-38 → CLOSED (§66.6).** The ordered per-phase field list exists (§41.2); `field_index` walks it; DP1's predicate (G-01) is now implementable. Resolution note: the v1-code divergence (§41.2 note) reconciled toward v2 names.
- **§35** — update the Define Tier-1 list/count to §41.2 (team added; problem consolidated to one field; baseline included).
- **§40 / S-C05** — `DefineOutput` field names updated to §41.2; `CoachingResponse` gains the four §50.x fields.
- **New finding (F-11):** built `DefinePhaseInput` diverged from v2 names (granular 5W2H, dual date fields); resolved by this rebuild — recorded so the rebuild is not later read as having introduced the names.
- **§56** — add the atomic-unit principle (Part A) as a governance rule.
- **New design item (CONTINUITY watch):** the `CoachingResponse` presentational-fields UI rendering belongs to the UI rebuild — schema/contract defined here, UI implements later.

---

## INTENT HAND-OFF FOR CLAUDE CODE (not a code prompt — Claude Code implements)

Apply this amendment to ARCHITECTURE.md first (new §41, new §50.x, updates to §20/S-C05, §35, §40, §56, §66). Then, in the SAME commit, rebuild the Define atomic unit to match §41 exactly:

- `phases/define/schema.py` — `DefineOutput` with the §41.2 fields/types; RETIRE the granular 5W2H `DefinePhaseInput`.
- `phases/define/validate.py` — `DEFINE_REQUIRED_FOR_GATE` = the §41.2 Tier-1 fields (the 8).
- `skills/dmaic-define-phase/SKILL.md` — verbatim from §41.7.
- `CoachingResponse` (S-C05) — add `explanation`, `example`, `prompt`, `progress` per §50.x / Part D (shared schema — note the all-phase blast radius).

Verify: the three Define files share field names exactly; capture round-trips (`CoachingResponse.fields_captured` → `artifacts` → `DefineOutput(**artifacts)`); G-38 closed in §66; §35/§40 counts reconciled. The UI rendering of §50.x fields is NOT in this commit (UI rebuild). Cite CLAUDE.md rule numbers per constraint. Stage by name. Co-Authored-By: Claude.
