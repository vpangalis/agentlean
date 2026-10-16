# ADR-0088: Element values are parsed and checked in code by one parser per kind — lists, durations, dates — and an element's required parts are checked before its read-back and its Confirm

Status: ACCEPTED (founder, 2026-10-16, with corrections a–e; drafted by Claude Code from the founder's Define test
findings 31, 36–39, 49, 66, 69–71, 77–80 and build items 12, 14, 25)
Requirements: R4 (thirteen elements), R5 (the report), R7 (rubric DEF-R09), R17 (step performance), C1; T88
Refines: ADR-0071 (MetricValues parsed in code — durations join them), ADR-0086 (its note on dates, by a founder
note), ADR-0078 (step durations)
Depends on: ADR-0065 (T88: state schema version and migrations), step 6.61 (a read-back's value is pending)

## Context (verified on case IMPR-2026-A99, 2026-10-15)

- Lists. Issues and barriers and the secondary metrics are stored as the Belt typed them. The report splits
  issues with its own rule (`report._issues`: new lines and ";"), which ignores the Belt's (1) (2) (3). That
  gave "2 issues" from 3, then "1 issue" after the correction. The secondary metrics are not split at all,
  and the Belt's own label "Secondary metrics:" is shown under the report's label.
- CTQs. The coach's structured capture crossed every customer with every need: 4 rows from the Belt's 2
  CTQs. Nothing in code compares the rows with what the Belt wrote.
- A read-back lost a value on screen. G-117's store-claim filter (`_without_store_claims`) removes every
  sentence containing "recorded", "stored", "saved" or "logged". It removed the Belt's first CTQ ("…within 5
  working days of being logged…") from the read-back the Belt was asked to confirm. The stored value was
  complete.
- Durations. "2 working days" is stored with unit `working`, and "same day" with no number. The report then
  shows "2 working (1 days to 6 days)" and "End-to-end lead time: 8 working". Nothing checks that
  min ≤ average ≤ max, and nothing compares the steps with the stated lead time.
- 5W2H. The first Confirm stored six answers and `steps`, with no `how`. The Belt had answered the screen's
  "How goal — what does the target look like", a label from the old 5-section model. The skill asks "How
  does it show up?", and the coach, rightly, kept a goal out of the problem, so the seventh answer had no
  slot. `moves.store_missing` checks that `problem_5w2h` is present, not its seven parts, so the Confirm
  stored it. The mind map then printed "Confirmed — 7 / 7" because the element was confirmed, whatever was
  stored.
- Dates. Three readers disagree. A8's goal parser stores "31.03.2027" as written (ADR-0086 note). The rubric's
  DEF-R09 reader knows ISO, "31 March 2027" and "31/03/2027", but not "31.03.2027". The report has a third.
  Three gate submits failed on DEF-R09 alone (15:53, 15:56 and 15:58 UTC); the third escalated the case.

## Decision

1. **One list parser** (`define/parse.list_items`) for every list-shaped element (CTQs, secondary metrics,
   issues and barriers; the team's and the SIPOC's rows already arrive structured):
   - It honours the Belt's numbering — (1), 1., 1), a), "-", "•" — and splits only there, never inside an
     item at a ";", a "," or "and".
   - With no numbering it splits at line breaks, and otherwise keeps one item.
   - A leading label equal to the element's name ("Issues and barriers:") is dropped.
   - "None identified" (or "none identified at this stage") is one item — a conscious answer (correction a).
   - The read-back and the report use it. The stored value stays the Belt's text: the structured breakdown
     is item 9's ADR.
2. **CTQ rows as the Belt stated them.** After the capture, code collapses rows with the same need and
   requirement into one row with their customers joined. A row the Belt did not state can then no longer
   be produced by the cross product. Rows still at odds with the CTQs the Belt listed (by the list parser)
   are shown in the read-back as a question, before Confirm.
3. **The store-claim filter never edits the Belt's values.** A sentence counts as a store claim only with
   a system or first-person subject ("I have stored", "it has been recorded", "is now saved"). List items and
   quoted values are never removed. After stage 2 (the read-back card renders the stored value, item 9) no text
   filter runs on the read-back at all (correction e).
4. **One duration parser** (`define/parse.duration_value`, extended):
   - Units: minutes, hours, working days, calendar days, weeks and months, each with its plural and common
     abbreviations; "same day" reads as 0 days, and a range "1–6 days" as min and max.
   - A step's "2 days" with no kind of day is stored as days and asked in the read-back: "working or calendar
     days?". Working and calendar days are never mixed silently.
   - Code checks min ≤ average ≤ max.
   - The step averages are compared with the stated end-to-end lead time. A gap of more than 25 % is shown in
     the read-back as a question ("the steps add up to 5 days, you said 12 — waiting time between steps?"),
     never as an error.
5. **One date parser** (`define/parse.calendar_date`) for A8 (ADR-0086), element 9 and rubric DEF-R09:
   - It reads ISO, 31.03.2027, 31/03/2027, "31 March 2027", "March 31, 2027", "March 2027" (the month's last
     day) and "Q1 2027" (the quarter's last day).
   - It stores ISO (`2027-03-31`).
   - The read-back shows the Belt's form and the unambiguous one: "31.03.2027 = 31 March 2027".
   - DEF-R09 reads the stored ISO date, and checks that it is in the future — after the date of the gate,
     as R7 states it (correction b). The rubric's and the report's own readers are removed.
6. **An element's required parts are checked in code** (`moves.store_missing`, extended per element) before
   any read-back and before any Confirm — only the parts R7 states (correction c):
   - the problem statement: the seven 5W2H answers (DEF-R04, the element's `5w2h` criterion);
   - the team: a champion and a process owner named, and training stated per member or as none needed
     (DEF-R02) — no other column is required;
   - the VOC: customers, their needs, and at least one CTQ as a measurable requirement (DEF-R03);
   - the SIPOC: its six columns, as today (DEF-R12).

   A missing part is asked for (G-163's path) and never stored. The mind map's badge counts what is
   stored, never a fixed "7 / 7".
7. **One definition of the seventh 5W2H question**, the skill's: "How does it show up / how is it
   detected?" (key `how`). The mind map labels it "HOW IT SHOWS UP". The screen's legacy "How goal" texts go,
   and the composed problem statement carries no goal (R7, `no-cause-no-fix`).
8. **State schema 10** (T88), bumped now, one bump for every stored-data change of stage 1 (correction d),
   with one migration:
   - `target_date` read by the date parser into ISO, where it parses;
   - durations re-read: unit `working` becomes `working days`, "same day" becomes 0 days;
   - CTQ rows collapsed as in 2.

   Later stages (items 1, 2, 7, 9) take their own bump.

## Tests

- Lists: three numbered barriers with a ";" inside one, two numbered secondary metrics with their label,
  items with "," and "and" — each read back and in the report with the right count and no label.
- CTQs: a VOC with two CTQs and two customers reads back and stores 2 rows.
- The store-claim filter: a CTQ containing "logged" survives the read-back; "I have recorded your answer"
  is still removed.
- Durations: "2 working days", "same day", "1–6 days", "15 min" read as noted; min > max is asked; a 25 %
  gap is asked; nothing is mixed.
- Dates: "31.03.2027", "31 March 2027", "March 2027" and "Q1 2027" store ISO. The e2e test: a goal with
  "31.03.2027" passes DEF-R09 at the gate.
- Completeness: a 5W2H with six answers is asked for the seventh and not read back for a Confirm. The e2e
  test: all seven read back and stored, and the badge counts the stored values.
- The migration: a v9 record with "31.03.2027", unit `working` and crossed CTQ rows loads as v10, converted.

## Consequences

- The read-back still restates the value in the coach's words. Item 9 (the read-back rendered from the
  exact pending value) builds on this ADR's parsers.
- The report's per-element structure (item 17's Gate rework) uses the same parsers.

## Rejected

- **A model call to split lists or read dates**: code decides them (ADR-0071's rule), and T47 allows one
  judgment per turn.
- **Storing lists as structured values now**: that is item 9's structured breakdown, decided with the
  element templates.
