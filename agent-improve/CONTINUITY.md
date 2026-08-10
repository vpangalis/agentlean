<!--
Continuity document for cross-session architectural conversations.
Paste the contents of this file into the first message of any new
Claude Desktop chat to restore context.

Last commit: 8dfe1a8
Last updated: 2026-08-10
Maintained by: Claude Code as part of normal refactor commits.
-->

# Agent Improve — Continuity

## 1. Where we are

**HEAD:** `8dfe1a8` on `main`, level with `origin/main`.

**Refactor step:** highest committed is **Step 2.2** (`199e784`, checkpointer
wired into graph compile). §15 marks **Step 2.5 — dependency upgrade** as next.
Step 3.6 (index schema rename) landed early, out of sequence.

**Recent commits:**
- `8dfe1a8` docs: stamp the review documents with their adding commit
- `f44e5c7` docs: move review documents into agent-improve/reviews/
- `110eef6` docs(arch-v2): Patterns 3+4 merge into the live gate document (v2.2.15)

**Immediately next:** recent work has been design, not code — docs went
2.2.8 → 2.2.15, five phase skills authored. Code resumes at Step 2.5
(langgraph → 1.2.10, langchain → 1.3.11), then Step 3.1, **which is blocked**
(§3). Doc versions: ARCHITECTURE.md v2.2.15 · CLAUDE.md v2.2.14 (behind by
design — 2.2.15 changed no rule).

## 2. What's ratified

- **State design v2.2.9–v2.2.12** — 24 findings across `SupervisorState`,
  `PhaseState`, store, naming, tiers. 2026-08-03/05 ·
  `reviews/STATE_DESIGN_RESOLUTION.md`
- **`case_id` and `artifacts` are canonical** — `project_id`,
  `captured_fields`, `phase_inputs` retired. 2026-08-03 · Findings 10, 15
- **All captured fields are `str`**; 20 computation tools parse at point of use.
  Three cross-phase reference dicts are the exception. 2026-08-03 · Findings 3, 5
- **Two-tier gate fields** — Tier 1 blocks, Tier 2 warns with an acknowledged
  gap; grader verdict gains `"warning"`. 2026-08-03 · Finding 11
- **`gate_apply` writes the gate document twice** — store and `PhaseState.final`;
  closed a reader-with-no-writer gap. 2026-08-04 · Finding 2
- **Executor contract** — five nodes (`planner`, `executor`, `validation_stack`,
  `gate_review`, `gate_apply`); `response_format=CoachingResponse`;
  `record_field` retired, universal tools 8 → 7. 2026-08-04 · Findings 16–23
- **Two graders, two rubrics** — `COACHING_QUALITY_RUBRIC` every turn (middleware),
  `PHASE_RUBRIC` once at the gate. 2026-08-04 · Finding 18
- **Five middleware, declaration order = execution order**, state injection
  first; `ModelRetryMiddleware` adopted. 2026-08-04 · Findings 19, 21
- **eBook gaps closed** — `issues_and_barriers`/`secondary_metrics` on all five
  schemas; process maps, stability, experiment justification promoted to Tier 1.
  **FMEA deliberately not tracked.** 2026-08-05 · Findings 24, 26
- **Seven-step computation coaching** (step 1 educates before any number) and
  **show-first coaching** (example before asking; no external URLs).
  2026-08-05 · Finding 25, `SKILL_REVIEW_NOTES.md` 15–17
- **Multi-query: Option A, per-tool Search clients.**
  2026-08-10 · **pending governance-doc amendment**
- **`improve_case_index` vector field standardised `embedding` → `content_vector`.**
  2026-08-10 · **pending doc amendment + re-index** — see §3, §4

## 3. What's open

- **Step 3.1 blocked.** It writes `tool_args.py` for "all 7 tools", but the
  canonical seven don't exist in code — today's `tools.py` is a different,
  unbound set. Reconcile the toolset first. Audit 2026-07-03, Delta 1c/1d, D3.5
- **`improve_case_index` re-index before Step 3.0/3.3** — `embedding` →
  `content_vector`. Azure can't rename a field: delete + recreate, as done for
  `phase_summary_analyse`.
- **v2.2 constitution rewrite was blocked on 6 items** (§79–§84). All six have
  since landed in v2.2.x — **confirm the audit is stale here rather than assume.**
- **Dependency drift** — `langgraph` not installed; `langchain` 1.2.13 vs 1.3.11;
  `langsmith` 0.7.3 vs 0.10.17. Step 2.5 resolves.
- **Five SKILL.md files are drafts**, not wired into `DMAICSkillsMiddleware`.
- **`_Artifacts/` untracked**, not in `.gitignore` — deferred housekeeping.

## 4. What's stale — don't ground a conversation in these

- **ARCHITECTURE.md §7.4 says the `content_vector`/`embedding` asymmetry is
  "safe by construction."** Today's standardisation decision reverses this.
  §7.3 and §7.4 need rewriting before Step 3.3.
- **REFACTORING_AGENT_IMPROVE.md §10 (≈lines 915–1061)** shows
  `completeness_score: float` on illustrative `DefineState`/`MeasureState`
  sketches. Ratified `PhaseState` has no stored score — progress derives from
  `artifacts`. Flagged out of scope in `110eef6`.
- **`core/llm.py` contains a class** — CLAUDE.md §2 violation. Audit D3.1
- **`core/llm.py` role map diverges from CLAUDE.md §4.2.** Audit D3.2
- **`upload/agent.py:107` parses raw `response.content`** — CLAUDE.md §4.5
  violation. **No §15 step covers this file**, so it survives as-is unless
  deliberately scheduled. Audit D3.4
- **Deprecated LangGraph primitive in the compiled graph** (D3.3); gate
  mechanism contradicts the constitution (D3.6); tools without `args_schema`
  (D3.5). All expected — the code is a coherent **end-of-Step-2 v1 system**.
- **§36's field-name asymmetry warning becomes historical** once
  `content_vector` standardisation lands.

**Sources:** `reviews/` (REVIEW_DECISIONS, STATE_DESIGN_RESOLUTION,
RESTRUCTURE_PLAN) · `_Artifacts/audit-2026-07-03.md` · `ARCHITECTURE.md` §15
