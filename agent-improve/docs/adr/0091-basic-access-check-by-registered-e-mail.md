# ADR-0091: A basic access check — sign-in by a registered e-mail, a per-case session the server checks on every request, approval by the session's person

Status: ACCEPTED (founder, 2026-10-17, with rulings a–c; drafted by Claude Code from the founder's build item 3)
Requirements: W17, R8a, R6, R19 (PROPOSED); finding 5; G-217
Depends on: ADR-0090 (the people on a case)

## Context (verified 2026-10-15)

- The browser asks for a name with `prompt()` and accepts anything. An empty answer becomes "Leader".
- Opening or joining a case checks nothing on the server.
- Approval compares a typed name with `case.leader` letter for letter. "VP" against "Vassilis" is a dead
  end, and anyone typing the lead's name can approve.

## Decision

1. The creator becomes the project lead from the details on the create form (ADR-0090), and is not asked
   again on this browser.
2. Anyone else signs in with the company e-mail the lead registered: an exact match, not case-sensitive.
   - The window says what it is and who may enter, and names the lead.
   - An unregistered e-mail gets W17's guidance: "Not on the team? Ask <lead> to add you."
3. A sign-in issues a session for that case and person: an HTTP-only cookie bound to the case id and the
   person's e-mail, signed by the server.
   - Every route that reads or changes the case checks it. A request without a valid session for the case
     is refused (401) and changes nothing.
4. Approval checks the session's person (the lead), never a typed name.
5. Every sign-in and every refusal is recorded with who and when (the decision trail).
6. No silent fallback name: the browser's `||'Leader'` default goes.
7. Stated plainly as a basic check, not security. One-time invite codes (R8a's pilot amendment) and single
   sign-on (R8) stay before customers. E-mail as identity is accepted for the pilot by name (ruling a).
8. **Existing cases open as today until the lead has completed the e-mails** (ruling b): a case whose people
   carry no e-mail yet asks no one to sign in; once the lead has completed them, decisions 2–4 apply.
9. **The lead on a second device signs in with their own e-mail**, like anyone else; **sessions are per
   case** — a person on two cases signs in to each (ruling c).

## Rejected

- **A check in the pop-up only**: skipped by calling the API directly.
- **Sign-in by name**: names are ambiguous ("Vassilis", "Vassilis P", "VP").
