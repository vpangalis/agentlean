# ADR-0085: An upload that covers the current element is read back on its upload turn, and "use the file" confirms it

Status: ACCEPTED (founder, 2026-10-13, G-169 option B; drafted by Claude Code from the ruling)
Requirements: W5 (uploads strengthen answers), R16 (where a stored value came from); DEF-169
Changes: ADR-0074 point 3 (a file's values reach the read-back and Confirm on the upload turn itself)
Depends on: ADR-0074 (the upload judged against the current element at interpretation), ADR-0066 (the
phase record), step 6.61 (the move decided in code; a read-back's value is pending until confirmed)

## Context

Scenario (e), live, 2026-10-13: the team list uploaded as a CSV; the upload turn named the file and said
it covers every criterion of the team element; the Belt answered "Please use the team exactly as listed in
project_team_ap_late_payments.csv." The planner's judgment read only that sentence — the file is not in its
input — and challenged; the Confirm after it had nothing pending. ADR-0074 point 3 says a file's values go
through the normal read-back and Confirm, but nothing carried them there: the coach sees the file's two- or
three-sentence summary, not its values, and a plain-text element stores the Belt's own words.

## Decision

1. The interpretation call (one per upload, at ingest — unchanged) also returns the element's answer as
   the file gives it: `ElementCheck.value`, the file's own words, every item it lists for the element;
   empty when the file does not answer it. A record without it reads as empty.
2. The upload turn of a file that **covers** the current element — checked against that element, every
   criterion `supported`, nothing missing, a value given — is a read-back, decided in code
   (`moves.decide`, `moves.covering_upload`): no judgment call; the answer so far is the file's value; the
   pending read-back carries the file's name. The file part of the reply stays written in code (ADR-0074
   point 2), and the coach reads the values back as on any read-back.
3. On that read-back, a Confirm click, a plain yes, or a message every part of which asks to use the file
   (or names it) or is a courtesy, and that changes nothing (`moves.uses_upload`), confirms it on the
   existing path: what a Confirm stores is computed as for any read-back (`moves.pending_store`). Any other
   content — "use the file but add Maria", "use the file except the sponsor", "use the file, sponsor is
   Jane" — is an answer, judged as one (founder, 2026-10-14).
4. The change log records the stored value's source as `upload` (R16, `FIELD_LOG_SOURCES`).
5. A file that does not cover the element is unchanged from ADR-0074: the file named, what it shows, what
   it lacks, and the ask.

## Consequences

- An upload turn that reads back makes one model call fewer (no judgment).
- The interpretation's output grows by the element's value; its call count does not.
- A value that is wrong in the file is read back to the Belt before anything is stored; nothing is stored
  without a Confirm (W5's acceptance).
- State schema version 9 (T88, ADR-0065): `migrate_v8_to_v9` is a no-op — a check written under 8 has no
  value and reads as not covering the element.
- Pilot item: scenario (e) is its live proof; DEF-169 reads failing until it passes live.

## Rejected

- **Option A — give the planner's judgment the file's interpretation**: the judgment would rule on a
  summary, not the values, and the plain-text store would still keep the Belt's sentence, not the file's.
- **Option C — parse the file in code per element**: works for a CSV team list only; every other element
  and file type would still need a model's reading.
