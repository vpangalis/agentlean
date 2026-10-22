# ADR-0108: The kept verdicts have their own PhaseState channel, not a copy in every reply's phase record

Status: SUPERSEDED by 0109 (founder and Desktop, 2026-10-22)
Requirements: R13; DEF-219 (G-220), DEF-224, DEF-098
Refines: ADR-0066 (unfinished phase work lives in the checkpoint only)

## Context

DEF-224 and DEF-098 keep the planner's verdict (`judged`), the gate rubric's per criterion (`gate`) and a value offered
from another answer (`offered`) inside each element's `field_status` entry. ADR-0066 puts the merged phase record on
every reply, so every reply carries them again. Measured 2026-10-21 (case IMPR-2026-LTSS4W): 178,967 of 1,257,229
bytes of the newest checkpoint's message payloads (14.2%), across 36 copies. Facts drafted for Desktop on 2026-10-21
(`agent-improve/Claude outputs/ADR_facts_P6_step_log_and_kept_verdicts.md`).

## Decision

1. Option (b): the kept verdicts move to a dedicated `PhaseState` channel — a dict with an upsert reducer — and are no
   longer inside every reply's phase record.
2. The newest checkpoint's message bytes per turn are measured before and after.

## Rejected

- Option (c), replacing older replies' copies by message id: rewriting old replies breaks the audit trail (R16, R19).
- Option (a), each reply carrying only what changed: recorded as the larger lever for DEF-219 and analysed there.
