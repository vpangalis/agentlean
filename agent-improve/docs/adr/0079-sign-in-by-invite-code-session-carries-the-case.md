# ADR-0079: Sign-in by a personal invite code; the session carries the case and the person

Status: ACCEPTED (founder, 2026-10-12; drafted by Claude Code from the rulings of 2026-10-01 and 2026-10-12)
Refines: ADR-0024 (the thread id is the case id — its consequence "once R8 lands, the id must come from an
authenticated session")
Requirements: R8a (access without single sign-on, amended 2026-10-01), R8b (the project lead), T12 (`thread_id`
from an authenticated session), W17 (the sign-in window); DEF-103, DEF-104, DEF-114, DEF-116
Depends on: ADR-0066 (case-blob writes only at creation, upload and approval; T13), ADR-0065 (Store records
carry the schema version)
Later: DEF-102 (Microsoft Entra ID, R8) replaces the session's source; nothing else changes.

## Context

Today a request names its case and its person in the body (`case_id`, `user`), so anyone who knows a case id can
read and write it as anyone. R8a (amended 2026-10-01): without single sign-on, only the people the project lead
registered can open the case, each through a personal invite — for the pilot a one-time code the lead hands over
in person; single-use, expiring after 72 hours; every sign-in records who and when; e-mail delivery later, as an
adapter. R8b: the creator is the project lead and alone manages the team. T12: `thread_id` comes from an
authenticated session, never from the request body.

## Decision

1. **The creator is the project lead.** `POST /cases` makes the creator the lead and signs them in to the new
   case: the response sets their session.
2. **The roster lives in the Store**, `("projects", case_id, "roster")`: the lead and each member `{member_id,
   name, role, added_by, added_at}`. It is written at creation and on every change; the case blob is not
   written mid-case (ADR-0066). Only the lead adds or removes a member or changes a role; anyone else gets 403.
3. **The invite code.** The lead asks for a code for one member; the code (eight characters from an alphabet
   without look-alike letters) is shown to the lead once and stored only as its SHA-256 in
   `("projects", case_id, "invites")` with who issued it, for whom, when, and when it expires (72 hours). A new
   code for the same member voids the old one. A code signs in once.
4. **Sign-in.** `POST /session` with the case and the code: a valid, unused, unexpired code is marked used and
   opens a session for its member. Every sign-in — and every refused attempt, without the code — is recorded in
   `("projects", case_id, "sign_ins")`: who, when, how. A removed member's code and sessions stop working.
5. **The session.** A random 32-byte token in an HttpOnly cookie (SameSite=Strict; Secure outside development);
   the Store keeps only its SHA-256, in `("sessions",)`, with the case, the member and the expiry (14 days from
   sign-in). No signing secret is needed. The person must still be on the roster at each request.
6. **Every case route takes the case and the person from the session** (T12): the graph's `thread_id` is the
   session's case id, and the acting person is the session's member. A case id in the body or path that differs
   from the session's is refused (403); `user` in a body is not read for identity. Without a session: 401.
   Open without a session: `POST /cases`, `POST /session`, the sign-in window's facts
   (`GET /cases/{id}/sign-in`: title and project lead), `GET /registry` (the case list) and `/health`.
7. **Development and demos only** (R8a): with `SIGN_IN_MODE=development` set explicitly, a registered name
   signs in without a code, recorded as such. Production refuses that mode at start-up.
8. **The sign-in window** (W17) says what it is, who may enter and what to do otherwise, and names the lead;
   an unknown name or a wrong code is refused with the same guidance.
9. **Entra ID later** (DEF-102) becomes the session's source; the routes read identity from the one session
   dependency, so nothing else changes.

## Consequences

- One FastAPI dependency gives every case route its session; the routes stop reading `user` and `case_id`
  from bodies for identity.
- The page signs in, keeps no token in script (the cookie is HttpOnly) and shows the lead's team controls.
- The run-through signs in as the creator by creating its case.
- Store records carry the schema version (ADR-0065) as all Store records do.

## Rejected

- **A signed cookie** (stateless): it needs a signing secret to be provisioned and cannot be revoked when the
  lead removes a member before it expires.
- **The roster in the case blob**: ADR-0066 allows no case-blob write mid-case.
- **Codes kept in clear**: a Store reader could sign in as anyone; only the hash is kept.

## Verification

- Route tests: the creator is the lead; a non-lead's team change is refused; a code signs in once, expires
  after 72 hours, and a removed member cannot sign in; each sign-in is recorded.
- Route test: a request whose body names another case or another person acts on the session's case as the
  session's person, or is refused; without a session the case routes answer 401.
- Page test: the sign-in window names the lead and refuses an unknown name with the same guidance.
