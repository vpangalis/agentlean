# ADR-0105: A personal one-time code opens a case; the thread comes from the session

Status: ACCEPTED (founder and Desktop, 2026-10-21 evening; drafted by Claude Code from the ruling)
Requirements: R8a (amended 2026-10-01), T12; DEF-103, DEF-116
Refines: ADR-0091 "Basic access check by registered e-mail" (decision 7: one-time codes stay before customers)
Depends on: ADR-0090 "The people on a case" (decision 2: the people are written on a team change)

## Context

Without single sign-on, R8a's pilot amendment admits each team member through a personal invite: a one-time code,
single-use, expiring after 72 hours, every sign-in recorded. ADR-0091's e-mail sign-in is "a basic check, not
security". The facts were drafted for Desktop on 2026-10-21 (`agent-improve/Claude outputs/ADR_facts_P5_one_time_codes.md`).

## Decision

1. **Issuer**: the project lead only, for one confirmed member. A re-issue voids the earlier code.
2. **Code**: 8 characters from a 31-character alphabet without 0, O, 1, I or L. Shown once, to the lead, at issue.
3. **Expiry**: 72 hours from issue (R8a).
4. **Storage**: only an HMAC-SHA256 of the code under `SESSION_SECRET`, in the case record's person entry (written on a
   team change, ADR-0090 decision 2). Never stored in plain text.
5. **Attempts**: 5 wrong tries void the code. Constant-time comparison. Every issue, sign-in and refusal is recorded
   in the access trail.
6. **After use**: the code is spent at the first successful sign-in; the session cookie lasts 7 days; a new device
   needs a new code from the lead.
7. **thread_id** (DEF-116, T12): taken from the session's case. A request whose body names another case is refused
   (403).
8. **`SESSION_SECRET` is required outside `GUARD_MODE=development`**: start fails without it. E-mail-only sign-in stays
   allowed in development and demos only (R8a).
