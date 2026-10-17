"""A basic access check — ADR-0091 "Basic access check by registered e-mail" (ACCEPTED 2026-10-17, rulings a–c).

Stated plainly: a basic check, not security (decision 7). E-mail as identity is accepted for the pilot by name;
one-time invites and single sign-on stay required before customers (ruling a).

- **Who may enter.** A person on the case (ADR-0090) who is a confirmed member with an e-mail
  (`people.may_sign_in`) signs in with that e-mail — exact, capital letters ignored.
- **The session.** One cookie per case (`improve_session_<case_id>`, HTTP-only, SameSite=Lax), bound to the case
  id and the person's e-mail and signed by the server (HMAC-SHA256, stdlib). A person on two cases signs in to
  each; the lead on a second device signs in with their own e-mail (ruling c).
- **When it applies (ruling b).** A case asks for sign-in once every confirmed member has an e-mail — the lead has
  completed them. Until then it opens as today, and the typed name is the person.
- **Every sign-in and every refusal** is recorded in the decision trail with who and when (decision 5).
Module-level functions only (rule §2).
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import secrets
import time
from datetime import datetime, timezone
from typing import Any, Optional

from fastapi import HTTPException, Request, Response

from backend.storage import people as people_mod

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


def required(case: Any) -> bool:
    """Ruling b: a case asks for sign-in once every confirmed member (the lead too) has an e-mail."""
    members = [p for p in case.people if p.status == "member"]
    return bool(members) and all(p.email.strip() for p in members)


def lead_name(case: Any) -> str:
    head = people_mod.lead(case.people)
    return head.full_name if head is not None else case.leader


def _trail(case_id: str, status: str, email: str, where: str, why: str = "") -> None:
    """Decision 5: every sign-in and every refusal, with who and when — in the decision trail."""
    at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        from backend.core.store import get_store
        get_store().put(("projects", case_id, "step_log"), f"access:{int(time.time() * 1000)}:{secrets.token_hex(3)}",
                        {"layer": "access", "status": status, "email": email, "route": where, "why": why, "at": at})
    except Exception as exc:  # noqa: BLE001 — the trail must not decide the request
        logger.error("access: the %s of %s could not be recorded: %s", status, email or "someone", exc)


def person(http: Optional[Request], case: Any, where: str) -> Optional[Any]:
    """Decision 3: the person a request is from. None when the case does not ask for sign-in yet (it opens as
    today). A request without a valid session for the case is refused (401) in W17's words and changes nothing."""
    if not required(case):
        return None
    value = http.cookies.get(cookie_name(case.case_id)) if http is not None else None
    email = read_token(value, case.case_id) if value else None
    who = people_mod.find(case.people, email) if email else None
    if who is not None and people_mod.may_sign_in(who):
        return who
    _trail(case.case_id, "refused", email or "", where, "no valid session" if not email else "not a member")
    raise HTTPException(401, SIGN_IN_NEEDED.format(lead=lead_name(case)))


def sign_in(case: Any, email: str, response: Response) -> Any:
    """Decision 2: a sign-in by the company e-mail the lead registered — exact, capital letters ignored. Sets the
    case's session cookie and returns the person; refuses in W17's words otherwise."""
    lead = lead_name(case)
    who = people_mod.find(case.people, email) if "@" in email else None
    if who is None:
        _trail(case.case_id, "refused", email.strip(), "sign-in", "not on the team")
        raise HTTPException(403, NOT_ON_THE_TEAM.format(lead=lead))
    if not people_mod.may_sign_in(who):
        _trail(case.case_id, "refused", email.strip(), "sign-in", "proposed member")
        raise HTTPException(403, NOT_YET_CONFIRMED.format(name=who.full_name, lead=lead))
    set_session(response, case.case_id, who.email)
    _trail(case.case_id, "signed_in", who.email, "sign-in")
    return who


def set_session(response: Response, case_id: str, email: str) -> None:
    """The case's session cookie: HTTP-only, so no script on the page reads it; SameSite=Lax."""
    response.set_cookie(cookie_name(case_id), token(case_id, email), max_age=SESSION_SECONDS,
                        httponly=True, samesite="lax", path="/")


__all__ = ["cookie_name", "token", "read_token", "required", "lead_name", "person", "sign_in", "set_session",
           "SIGN_IN_NEEDED", "NOT_ON_THE_TEAM", "NOT_YET_CONFIRMED"]
