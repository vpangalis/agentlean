# ADR-0109: The kept verdicts ride only on the reply whose turn changed them

Status: ACCEPTED (founder and Desktop, 2026-10-22; drafted by Claude Code from the ruling)
Requirements: R13; DEF-219 (G-220), DEF-224, DEF-098
Supersedes: ADR-0108
Refines: ADR-0066 (unfinished phase work lives in the checkpoint only)

## Context

ADR-0108 moved the kept verdicts (`judged`, `gate`, `offered`) into a dedicated `PhaseState` channel. The
probe before building found that `PhaseState` is rebuilt every turn (`backend/phases/mappers_common.py`,
the input mapper; a fresh `checkpoint_ns` per parent turn): such a channel would be empty at each turn's
start and the verdicts would be lost. Today they reach the next turn inside `field_status`, on every reply's
phase record — 178,967 of 1,257,229 bytes (14.2%) of the newest checkpoint's message payloads, 36 copies
(case IMPR-2026-LTSS4W, 2026-10-21). Findings: `agent-improve/Claude outputs/FINDINGS_P6_ADR-0107_0108_assumptions.md`.

## Decision

1. Option (b2): the kept verdicts ride only on the reply whose turn changed them.
2. The input mapper reads the latest reply carrying them.
3. The newest checkpoint's message bytes are measured before and after.

## Rejected

- ADR-0108's `PhaseState` channel: it does not outlive the turn.
- A `SupervisorState` channel (b1): an eighth parent field needs an amendment (state.md §10.1).
- A Store namespace (b3): against ADR-0066.
- Rewriting older replies (ADR-0108's option (c)): breaks the audit trail (R16, R19).
