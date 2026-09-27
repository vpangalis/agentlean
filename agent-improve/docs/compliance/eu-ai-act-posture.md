# EU AI Act compliance posture

> **Decision: [ADR-0055](../adr/0055-eu-ai-act-posture.md).** Moved verbatim from ARCHITECTURE.md v1.88 67 on 2026-09-27 (brief Part C2); its § numbers refer to the archived [v1.88](../_archive/ARCHITECTURE_v1.88_2026-09-27.md). Links re-pointed to this folder.

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
