# ADR-0076: The third failed gate attempt escalates to the project lead; the case stays open

Status: ACCEPTED (founder, 2026-10-01; drafted by Claude Code from the ruling)
Requirements: T65 (the third failed gate attempt escalates), R6, R7; DEF-137, DEF-046
Depends on: ADR-0039 (one shared cap of three — escalation was "still a stub"), ADR-0066 (unfinished work
in the checkpoint), ADR-0072 (parking an element)
Defect: G-150 (the attempt count reset every turn)

## Context

ADR-0039 counts failed gate attempts against one shared cap of three and says the third escalates, but
not to whom or what happens next. In the code the validation stack computes `escalated` and routes to
`gate_review` regardless; the v1 `escalate.py` writes a model-generated report into `chat_history`, a
field v2 does not have; and `gate_attempts` is seeded 0 by the input mapper every turn, so the count
cannot reach three across separate submissions (G-150).

Three readings were put to the founder: hold for the lead with the case open; lock gate submission until
a person clears it; notify by e-mail (needs a mail service and a secret).

## Decision

1. **The count persists.** The phase record (ADR-0066) carries `gate_attempts`; the next turn is seeded
   from it. A passed gate resets it to 0 (ADR-0039).
2. **On the third failed submission the report is held for the project lead.** The validation stack
   marks the phase escalated (with the failed criteria named) instead of looping silently; the Belt is
   told, in code and in plain words, that the report has gone to the project lead with what failed.
3. **The case stays open.** Coaching continues; the Belt or the lead can still change the named elements
   through coaching and submit again. Escalation does not lock anything.
4. **It is visible.** The registry entry and the dashboard show the case as escalated, with the date and
   the failed criteria, until a submission passes.
5. **No model call, no new service.** The message is written in code from the failed criteria; no
   e-mail is sent (that would need a mail service and its secret — not ruled).

## Consequences

- T65 and ADR-0039's stub are closed; the v1 `escalate.py` is not used by this path.
- The phase record gains `gate_attempts` and `escalated`: a state change under ADR-0065 (schema version
  raised, a no-op migration — a record without them reads 0 and not escalated).
- The parent graph's `escalate` node stays unreached by this path (the case does not leave the phase).

## Rejected

- **Lock gate submission until a person clears it.** Stops the team working on what the lead would ask
  them to fix anyway.
- **Notify by e-mail.** Needs a mail service and a secret from the founder; not ruled now.

## Verification

- Route test: three failed submissions across separate POST /gate calls → the third is escalated: the
  Belt is told, the report names the failed criteria, the registry shows escalated; coaching continues;
  a later passing submission clears it and resets the count.
