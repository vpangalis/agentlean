"""A basic access check — ADR-0091 "Basic access check by registered e-mail" (rulings a–c).

Stated plainly: a basic check, not security (decision 7). E-mail as identity is accepted for the pilot by name;
one-time invites and single sign-on stay required before customers (ruling a).

- **Who may enter.** A person on the case (ADR-0090) who is a confirmed member with an e-mail
  (`people.may_sign_in`) signs in with that e-mail — exact, capital letters ignored.
- **The session.** One cookie per case (`improve_session_<case_id>`, HTTP-only, SameSite=Lax), bound to the case
  id and the person's e-mail and signed by the server (HMAC-SHA256, stdlib). A person on two cases signs in to
  each; the lead on a second device signs in with their own e-mail (ruling c).
- **When it applies (ruling b).** A case asks for sign-in once every confirmed member has an e-mail — the lead has
  completed them. Until then it opens without sign-in, and the typed name is the person.
- **Every sign-in and every refusal** is recorded in the decision trail with who and when (decision 5).
Module-level functions only (CLAUDE.md).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import datetime
from typing import Any, Optional

from fastapi import HTTPException, Request, Response

from backend.storage import people as people_mod
from backend.core.clock import utc_now

logger = logging.getLogger(__name__)

#: The cookie's name: one per case, so sessions are per case (ruling c).
COOKIE_PREFIX = "improve_session_"
#: A session lasts a working week, then the person signs in again.
SESSION_SECONDS = 7 * 24 * 3600

#: W17's wording, in code. {lead} is the lead's one display name (ADR-0090 decision 4).
SIGN_IN_NEEDED = ("Only team members added by the project lead can open this project. Project lead: {lead}. "
                  "Enter your company e-mail as the project lead registered it.")
NOT_ON_THE_TEAM = "That e-mail is not on the team. Not on the team? Ask {lead} to add you."
NOT_YET_CONFIRMED = ("{name} is on the team as a proposed member; {lead} confirms you with your e-mail before you "
                     "can sign in. Ask {lead} to confirm you.")

_SECRET: Optional[bytes] = None


def _secret() -> bytes:
    """The signing key: `SESSION_SECRET` from the environment; without one, a key for this process only (every
    session ends at a restart) — logged once."""
    global _SECRET
    if _SECRET is None:
        from backend.core.config import settings
        configured = str(getattr(settings, "SESSION_SECRET", "") or "")
        if configured:
            _SECRET = configured.encode("utf-8")
        else:
            _SECRET = secrets.token_bytes(32)
            logger.warning("SESSION_SECRET is not set — sessions are signed with a key for this process only; "
                           "they end when the server restarts (ADR-0091)")
    return _SECRET


def cookie_name(case_id: str) -> str:
    return COOKIE_PREFIX + "".join(ch for ch in case_id if ch.isalnum() or ch in "-_")


def _sign(body: bytes) -> str:
    return hmac.new(_secret(), body, hashlib.sha256).hexdigest()


def token(case_id: str, email: str, now: Optional[float] = None) -> str:
    """A session for one case and one person: the case id, the e-mail and when, signed."""
    body = json.dumps({"c": case_id, "e": email.strip().lower(), "t": int(now if now is not None else time.time())},
                      separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(body).decode("ascii").rstrip("=") + "." + _sign(body)


def read_token(value: str, case_id: str, now: Optional[float] = None) -> Optional[str]:
    """The e-mail a valid session for `case_id` carries — None for anything else: a bad signature, another case,
    an expired session."""
    try:
        part, sig = value.rsplit(".", 1)
        body = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
    except (ValueError, TypeError):
        return None
    if not hmac.compare_digest(_sign(body), sig):
        return None
    try:
        data = json.loads(body)
    except ValueError:
        return None
    if data.get("c") != case_id or (now if now is not None else time.time()) - int(data.get("t") or 0) > SESSION_SECONDS:
        return None
    return str(data.get("e") or "") or None


#: ADR-0105 decision 2: a one-time code is 8 characters from this 31-character alphabet — no 0, O, 1, I or L.
CODE_ALPHABET = "23456789ABCDEFGHJKMNPQRSTUVWXYZ"
CODE_LENGTH = 8
#: Decision 3: a code expires 72 hours from issue (R8a). Decision 5: 5 wrong tries void it.
CODE_HOURS = 72
CODE_ATTEMPTS = 5
OTHER_CASE = "This session is for another case. Sign in to {case} to work on it."
CODE_NEEDED = "Enter the one-time code {lead} gave you, with your company e-mail."
CODE_REFUSED = "That code is not valid. Ask {lead} for a new one."


def new_code() -> str:
    """Decision 2: a fresh code, shown once to the lead and never stored."""
    return "".join(secrets.choice(CODE_ALPHABET) for _ in range(CODE_LENGTH))


def code_digest(case_id: str, email: str, code: str) -> str:
    """Decision 4: what is stored — the HMAC-SHA256 of the code under SESSION_SECRET, bound to the case and person."""
    body = f"{case_id}:{email.strip().lower()}:{code.strip().upper()}".encode("utf-8")
    return hmac.new(_secret(), body, hashlib.sha256).hexdigest()


def check_code(case_id: str, person: Any, code: str, now: Optional[float] = None) -> str:
    """Decisions 3 and 5: "ok", or why not — "none" (no code open), "expired", "wrong". Constant-time comparison."""
    if not person.code_hash:
        return "none"
    try:
        issued = datetime.fromisoformat(person.code_issued_at).timestamp()
    except ValueError:
        return "expired"
    if (now if now is not None else time.time()) - issued > CODE_HOURS * 3600:
        return "expired"
    return "ok" if hmac.compare_digest(code_digest(case_id, person.email, code), person.code_hash) else "wrong"


def development() -> bool:
    """R8a / decision 8: e-mail-only sign-in is allowed in development and demos only."""
    from backend.core.config import settings
    return str(getattr(settings, "GUARD_MODE", "strict")).strip().lower() == "development"


def session_case(value: str) -> Optional[str]:
    """The case a validly SIGNED session names (expired or not) — None when the signature does not hold."""
    try:
        part, sig = value.rsplit(".", 1)
        body = base64.urlsafe_b64decode(part + "=" * (-len(part) % 4))
        if not hmac.compare_digest(_sign(body), sig):
            return None
        return str(json.loads(body).get("c") or "") or None
    except (ValueError, TypeError):
        return None


def required(case: Any) -> bool:
    """Ruling b: a case asks for sign-in once every confirmed member (the lead too) has an e-mail."""
    members = [p for p in case.people if p.status == "member"]
    return bool(members) and all(p.email.strip() for p in members)


def lead_name(case: Any) -> str:
    head = people_mod.lead(case.people)
    return head.full_name if head is not None else case.leader


def _trail(case_id: str, status: str, email: str, where: str, why: str = "") -> None:
    """Decision 5: every sign-in and every refusal, with who and when — in the decision trail."""
    at = utc_now().isoformat(timespec="seconds")
    try:
        from backend.core.store import get_store
        get_store().put(("projects", case_id, "step_log"), f"access:{int(time.time() * 1000)}:{secrets.token_hex(3)}",
                        {"layer": "access", "status": status, "email": email, "route": where, "why": why, "at": at})
    except Exception as exc:  # noqa: BLE001 — the trail must not decide the request
        logger.error("access: the %s of %s could not be recorded: %s", status, email or "someone", exc)


def person(http: Optional[Request], case: Any, where: str) -> Optional[Any]:
    """Decision 3: the person a request is from. None when the case does not ask for sign-in yet (it opens
    without sign-in). A request without a valid session for the case is refused (401) in W17's words and changes nothing."""
    value = http.cookies.get(cookie_name(case.case_id)) if http is not None else None
    other = session_case(value) if value else None
    if other is not None and other != case.case_id:
        # ADR-0105 decision 7 (DEF-116, T12): the thread is the session's case — a request naming another is refused.
        _trail(case.case_id, "refused", "", where, f"a session for {other}")
        raise HTTPException(403, OTHER_CASE.format(case=case.case_id))
    if not required(case):
        return None
    email = read_token(value, case.case_id) if value else None
    who = people_mod.find(case.people, email) if email else None
    if who is not None and people_mod.may_sign_in(who):
        return who
    _trail(case.case_id, "refused", email or "", where, "no valid session" if not email else "not a member")
    raise HTTPException(401, SIGN_IN_NEEDED.format(lead=lead_name(case)))


def sign_in(case: Any, email: str, response: Response, code: str = "") -> tuple[Any, str]:
    """ADR-0091 decision 2 and ADR-0105: a sign-in by the company e-mail the lead registered, with the person's
    one-time code — e-mail alone only in development and demos (decision 8). Returns (the person, the code's
    outcome: "ok" | "wrong" | "expired" | "none" | "" for no code checked); sets the session only on success. The
    caller writes the code's spending or its failed attempt to the case record (a team change, ADR-0090)."""
    lead = lead_name(case)
    who = people_mod.find(case.people, email) if "@" in email else None
    if who is None:
        _trail(case.case_id, "refused", email.strip(), "sign-in", "not on the team")
        raise HTTPException(403, NOT_ON_THE_TEAM.format(lead=lead))
    if not people_mod.may_sign_in(who):
        _trail(case.case_id, "refused", email.strip(), "sign-in", "proposed member")
        raise HTTPException(403, NOT_YET_CONFIRMED.format(name=who.full_name, lead=lead))
    outcome = ""
    if code.strip() or not development():
        outcome = check_code(case.case_id, who, code) if code.strip() else "none"
        if outcome != "ok":
            _trail(case.case_id, "refused", who.email, "sign-in", f"code {outcome}")
            return who, outcome
    set_session(response, case.case_id, who.email)
    _trail(case.case_id, "signed_in", who.email, "sign-in", "one-time code" if outcome == "ok" else "e-mail (development)")
    return who, outcome or "ok"


def set_session(response: Response, case_id: str, email: str) -> None:
    """The case's session cookie: HTTP-only, so no script on the page reads it; SameSite=Lax."""
    response.set_cookie(cookie_name(case_id), token(case_id, email), max_age=SESSION_SECONDS,
                        httponly=True, samesite="lax", path="/")


__all__ = ["cookie_name", "token", "read_token", "required", "lead_name", "person", "sign_in", "set_session",
           "SIGN_IN_NEEDED", "NOT_ON_THE_TEAM", "NOT_YET_CONFIRMED"]
