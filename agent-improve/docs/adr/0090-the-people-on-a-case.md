# ADR-0090: One person record for everyone on a case, kept in the case record and written on every team change; Define's team element refers to it

Status: ACCEPTED (founder, 2026-10-17, with rulings a–b; drafted by Claude Code from the founder's ruling of 2026-10-15 on R8b)
Requirements: R8b (amendment PROPOSED), R8, R8a, W17, R16; findings 2, 4, 29; G-216
Changes: ADR-0066 / T13 (the case blob is also written on a team change, as on an upload)
Depends on: ADR-0089 (location lists), ADR-0065 (T88)

## Context (verified 2026-10-16)

- The create form's "Project team" and Define's element 2 are two lists that know nothing of each other.
  - The form writes `CaseDocument.team` (name and role) once, at creation, and nothing reads it afterwards.
  - Element 2 lives in the checkpoint (name, role, function) and reaches the blob only at approval.
- The lead is a typed string (`leader`). On A99 the Gate showed two names for the lead.

## Decision

1. **One person record**: full name, company e-mail, role on the project, function, department, and location
   (country and site, as in ADR-0089).
   - Full name, role and location are required at case creation; **the e-mail is required only before the
     person signs in** (ruling a).
   - Location defaults to the case's own.
   - The case record holds `people: list[Person]`, and the lead is one of them (`role: project lead`).
2. **The people list is case-level data.** It is written to the case record at creation and on every
   change to the team, as uploads already are. ADR-0066 / T13 gain "a change of the people on the case"
   as a moment the blob may be written.
3. **Define's element 2 refers to the people by e-mail** and adds only the project fields R7 names (time
   on the project, training). The two lists can then no longer drift.
   - A new person named in element 2 is stored as a **proposed member**; element 2 can still be
     confirmed. The lead confirms proposed members in the team panel. A proposed member cannot sign in
     until confirmed with an e-mail (ruling b).
4. **One display name everywhere**: header, case list, sign-in window (W17), Define report section A, and
   the "who" of audit entries.
5. **With single sign-on (R8)**, name, e-mail, function and department come from the identity provider.
6. **Schema bump with a tested migration** (T88): `leader` becomes the lead's person record, with the e-mail missing.
   `team` entries become person records. The lead is asked to complete the missing details on the next
   open.

## Rejected

- **Name only**: no invites (R8a), no match with single sign-on.
- **Free-text location**: breaks W20's filters.
- **Keeping element 2 as a separate list**: the two drift (A99).
