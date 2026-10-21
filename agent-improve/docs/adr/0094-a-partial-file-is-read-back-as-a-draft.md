# ADR-0094: An upload that covers an element only partly is read back as a draft with its gaps; a message pointing at the file is never judged as a typed answer; an upload starts its own turn

Status: ACCEPTED (founder, 2026-10-21, Desktop reviewed; drafted by Claude Code 2026-10-16 from the founder's build items 10 and 11)
Requirements: W5, R14; findings 22, 25, 26; G-206, G-209, G-210
Supersedes: ADR-0085 point 5 (a file that does not cover the element only names what it lacks)
Depends on: ADR-0074, ADR-0085, ADR-0088 (the required parts), ADR-0093 (the read-back card)

## Decision

1. **An upload in the chat starts the upload turn itself**: the route runs the same turn a follow-up
   message would. There is no browser-written "Let me process it". A failure gets the W10 card.
   - Scenario (e) and its test upload without a follow-up message.
2. **A file that gives the element's value only partly is read back as a DRAFT**. The interpretation's
   `value` (ADR-0085) is given whatever the coverage.
   - The read-back card shows the value as a table, with each missing required part (ADR-0088 decision 6)
     marked.
   - The ask: "Add what is missing or correct anything, then Confirm."
   - Confirm stays disabled while a required part is open. The Belt completes it in a message, and the table
     updates.
3. **A message that points at the uploaded file** ("our team is in the attached file", "use the file") is
   read by `moves.uses_upload`'s rule, never judged as a typed answer.
4. **The layout**:
   - the file's name and what it covers, as a header line;
   - the table;
   - the missing items as a list;
   - the ask.

## Rejected

- **Leaving partial files to be retyped**: finding 25.
