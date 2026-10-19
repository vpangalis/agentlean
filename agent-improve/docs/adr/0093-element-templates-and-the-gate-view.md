# ADR-0093: Element templates and the Gate view — each element read back and shown in the Gate as its criteria, one row each, with the value and its source; drawn in code

Status: ACCEPTED (founder, 2026-10-19, with option (b) for free-text elements and the verbatim-span safeguard; drafted
by Claude Code 2026-10-16, revised 2026-10-19)
Requirements: R5 "The Define report", R6 "Formal acceptance, human in the loop", R7 "Acceptance criteria and gate
rubric", C1, C5, W3, W4, R16 "Audit trail per element"; findings 17–19, 28, 30, 32–36, 41, 43, 46, 48, 51, 58, 60, 64,
72, 73; G-195, G-197, G-198 (sections A–G), G-199, G-200; stage 2 item 9 "Structured read-back card"
Mockups: docs/founder-inputs/readback_card_mockup.html, docs/founder-inputs/gate_view_mockup.html (approved 2026-10-15)
Depends on: ADR-0088 "Element values parsed and checked in code" (one parser per kind, required parts), ADR-0070
(visuals drawn in code), T47 (one judgment call per answer), ADR-0077 "Calculations run in code, never by the coach"

## Context

- A read-back is the coach's restatement of the answer. On IMPR-2026-A99 three barriers were read back and one was
  stored (finding 73); the benefits read-back echoed the Belt's text with a calculation line under it
  (readback_card_mockup.html, "Today").
- The Gate repeats the Belt's text, has two numbering schemes, crossed CTQ rows, raw JSON history and the goal under
  three names (findings 18, 32–36, 41, 43, 48, 51, 72).
- What exists in code today: each element's acceptance criteria in the Define script (one bullet per criterion, with
  an id); `parse.missing_parts` (ADR-0088) for the required parts of the team, the CTQs, the 5W2H and the target date;
  the parsers for lists, metrics, dates, durations and the SIPOC; the calculations and their formula line (ADR-0077).

## Decision

1. **A template per element, in code** (`phases/define/templates.py`, C5): the element's criteria as rows, in the
   script's order, each with its id, its label, whether it is required, and where its value comes from in the stored
   value. The criteria are the script's own (R7); the template adds no criterion and no wording to any prompt.
2. **The read-back is a criteria card, drawn in code from the exact pending value a Confirm will store**
   (readback_card_mockup.html):
   - the header "Element n of 13 · name" and "k of m criteria met";
   - one row per criterion: ✓ or ○, the value that will go into the Gate, and its source — "your answer", "from your
     file" (the upload the value came from), or "calculated" with its formula (ADR-0077);
   - groups where the element has them (hard and soft benefits);
   - what is missing, in plain words, with one ask;
   - **Confirm disabled until every required criterion is met** (enforced on the server too: a Confirm with a required
     criterion open is refused in plain words and stores nothing); Change always available.
   The coach's prose never stands in for the value; the coach's words come above the card, unchanged.
3. **After a Confirm**, a separate green strip — "✓ Element n · name confirmed — the Gate document is updated (section
   X)" — and the next element as its own card.
4. **The Gate shows the same rows** (gate_view_mockup.html): the summary strip and the 13-element strip; sections A–G
   (R5's seven); each element its own card with "Element n · name", a status chip and a History link, its rows drawn
   by the same template and the same code as the card; display names, never ids; no raw JSON; "Still to confirm" at
   the end with element numbers.
5. **Where a row's value comes from:**
   - structured elements (team, CTQs, 5W2H, scope in/out, primary metric, baseline, target, target date, benefits
     fields, secondary metrics, SIPOC and its performance, issues as a list) — from the stored structure and the
     ADR-0088 parsers, in code;
   - free-text elements (business case What / Where / Since when / Size / Cost; the problem statement's parts) —
     **option (b), ruled 2026-10-19:** the existing judgment call (T47: still one call) returns the quoted span per
     criterion as a field of its structured output (`criterion_spans`), as ADR-0077 does for calculation inputs.
     **Safeguard:** code checks each span is a verbatim substring of the Belt's answer; a span that is not — or a
     criterion with none — shows the whole answer once, marked "in your answer".
6. **No prompt rule and no script change.** Structure and layout are code. The one model-facing addition is the
   description of the new structured-output field (option (b)); its bytes are reported. The script is unchanged.
7. **State:** the pending value and the stored value keep their shape (ADR-0088). The rows are computed, never stored.
   The spans travel with the pending value and are kept on the confirmed element's status, so the Gate shows the
   same rows: a schema bump with a tested migration (T88) — a record without spans reads as having none (the whole
   answer, once).

## Build order

1. The templates and the row builder (pure functions), with a test per element against the A99 values.
2. The read-back card in the UI, Confirm disabled while a required criterion is open, the server refusing such a
   Confirm; the green strip.
3. The Gate's element cards from the same rows; sections A–G; "Still to confirm".

## Rejected

- **A free-text report** (today's state).
- **A coach-written report text**: C1 builds the report only from confirmed values.
- **A second model call** for the breakdown: T47 allows one judgment.
- **Storing the rows**: they are a view of the stored value; storing them would give two copies that can disagree.
