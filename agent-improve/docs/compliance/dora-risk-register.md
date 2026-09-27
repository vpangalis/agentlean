# DORA-structured compliance risk register

> **Decision: [ADR-0056](../adr/0056-dora-risk-register.md).** Moved verbatim from ARCHITECTURE.md v1.88 68 on 2026-09-27 (brief Part C2); its § numbers refer to the archived [v1.88](../_archive/ARCHITECTURE_v1.88_2026-09-27.md). Links re-pointed to this folder.

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
