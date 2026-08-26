# REFACTORING_PROCEDURE.md — Reconciliation

**Date: 2026-08-25**
**Purpose: bring the ratified procedure in line with two commits that landed out of its original sequence — `871637f` (knowledge-index rebuild) and `4701a09` (Define schema/validator/skill). No step is rewritten. Three steps are annotated, one out-of-band step is recorded, and the position note is updated.**

**Direction confirmed: HORIZONTAL.** The refactor resumes the procedure's own foundation-first order (next spine step = 2.4), not a phase-by-phase vertical build. Today's Define work is absorbed, not extended.

---

## Edit 1 — Record the knowledge-index rebuild as a completed out-of-band step

**Add to Part 8 (Stage 9), before Step 9.1:**

> ### Step 9.0 — Knowledge-index rebuild · **DONE out-of-band (commit `871637f`, 2026-08-25)**
>
> | | |
> |---|---|
> | **Reference §** | §23 · §23.1 (corpus, classification) |
> | **Touches** | `improve_knowledge_index` → `improve_knowledge_index_v3` · `scripts/ingest_knowledge.py` |
> | **Verify** | `azure-query` — DONE |
>
> **Not in the original spine; executed ahead of sequence and recorded here for continuity.** Rebuilt the methodology corpus: BB eBook only (8D removed as cross-framework contamination; tools-suite sheets removed as thin/redundant); pdfplumber extraction fixing cid/footer/%-bullet garble; **LLM phase classification at ingest** (operational-model, temp 0.0, six-label closed set) replacing keyword `detect_phase`; text-embedding-3-large / 3072d preserved; per-page 1200/150 chunking preserved.
>
> **Live state:** `improve_knowledge_index_v3` (1,184 docs, 259 `general`) is LIVE via `.env` (local only — reversible one-line rollback to `improve_knowledge_index`, kept intact). §23.1 doc counts re-synced in the commit.
>
> **Interaction with Step 9.1:** this rebuild touched `improve_knowledge_index` only. Step 9.1's reindex targets `improve_evidence_index` and `improve_case_index` — **different indexes, still outstanding.** 9.1 is unaffected and unchanged.
>
> **Residual (WATCH register):** CLAUDE.md §7.2 still states "218 carry `general`" — now 259 — pending a §0.x rule amendment (WATCH 3/8).
>
> **Updates Step 5.1's premise:** 5.1 says "retriever.py already carries the correct phase_relevance filter." Still true, but the *tags it filters on* are now LLM-generated, not keyword. The retriever code is unchanged; the corpus underneath it is rebuilt.

---

## Edit 2 — Annotate Step 3.4 as partially executed for Define, ahead of sequence

**Add this banner at the top of Step 3.4:**

> ⚠ **PARTIALLY EXECUTED AHEAD OF SEQUENCE — Define only (commit `4701a09`, 2026-08-25).** Read before running this step.
>
> The Define portion of this step's schema+validator work was done early, via the ratified Define amendment (`docs/DEFINE_AMENDMENT_2026-08-25.md` → ARCHITECTURE.md §39.1).
>
> **Already done for Define:**
> - `phases/define/schema.py` — `DefineOutput` (15 fields: 8 Tier 1, 3 Tier 2, 4 gate metadata) rebuilt; granular 5W2H `DefinePhaseInput` retired.
> - `phases/define/validate.py` — `DEFINE_REQUIRED_FOR_GATE` = the 8 Tier-1 fields.
> - `skills/dmaic-define-phase/SKILL.md` — written, generated verbatim from §39.1.7.
> - `CoachingResponse` (S-C05) — gained 4 presentational fields (`explanation`, `example`, `prompt`, `progress`), shared across all five phases.
>
> **STILL OUTSTANDING for this step (do NOT skip):**
> - The **other four phases'** schema+validator rebuilds — Measure, Analyse, Improve, Control. This step's "all five in one step, deliberately" rule (§14 cross-phase) is **not yet satisfied** — only Define is done. The four must be completed together.
> - The **`ui/index.html` field-rename** coupling — NOT done for any phase. The UI still references v1 field names.
> - **Count correction:** this step's prose says "Define has six Tier 1 fields" and "exactly one v1 name survives (`goal_statement`)." Both are superseded by §39.1 — Define is **8 Tier 1**, and more than one field was reconciled. §39.1 is authoritative; this step's inline counts are pre-amendment.
>
> **Consequence — WATCH 7 (Edit 3):** doing Define's schema early, without its subgraph (Step 4.1), left `phases/define/orchestrate.py` still writing v1 field names while the validator reads v2 names — so **the Define gate cannot currently pass.** Expected given out-of-sequence execution; resolves at Step 4.1 per the procedure's own order.

---

## Edit 3 — Record WATCH 7 as a known, accepted interim

**Add this row to the §0.2 Standing gates table:**

> | **WATCH 7 — Define gate non-functional** | Define phase end-to-end runs | Step **4.1** lands (Define subgraph; executor stops delegating to v1 `orchestrate_define`, which still writes v1 names). Accepted interim, not a bug — a consequence of running 3.4's Define portion (commit `4701a09`) ahead of 4.1. `validate.py` reads v2 names; `orchestrate.py` writes v1 names; gate reads all Tier-1 fields missing. **Do not add a v1→v2 shim** (CLAUDE.md §17) — the migration happens naturally when 4.1 replaces the orchestrator's role. Cross-phase Define briefs in analyse/improve/control stay on v1 names until then, deliberately. |

---

## Edit 4 — Update the current-position note

**In §0.3, add:**

> **As of 2026-08-25:** Step 2.3 done. **Out-of-band:** Step 9.0 (index rebuild, `871637f`) done; Step 3.4 partially done for Define (`4701a09`) with four phases + UI outstanding. **Next spine step: 2.4** — the procedure's horizontal order resumes here. Do not jump ahead to more phase work until 2.4–3.3 foundation is complete; then 3.4 finishes all five phases together.

**In Appendix D (status table):**
- `Commit 3.4` → status **`partial (Define only; 4 phases + UI outstanding)`**
- Add row `Commit 9.0` · Knowledge-index rebuild · **`done`**

---

## Notes for whoever applies this

- No step is rewritten. These are annotations, one new record (9.0), one gate row, and a status update.
- After the edit, confirm the session-start hook still parses Appendix D's fixed `| **Commit X.Y** | <title> | <status> |` format (CLAUDE.md §0.2) — the new 9.0 row and the 3.4 status change must not break it.
- The horizontal decision means the immediate next build step is **2.4**, not more Define work.
