"""The people on a case — ADR-0090 "The people on a case" (ACCEPTED 2026-10-17, rulings a–b).

One `PersonRecord` per person, held on the case record (`CaseDocument.people`) and written on every change to
the team, as uploads are (ADR-0066 / T13 gain this moment). The lead is the person whose role is
`PROJECT_LEAD`; their full name is the one display name everywhere (decision 4).

Define's element 2 (the team) keeps the Belt's rows. When it is confirmed, each row is matched to a person on
the case; a name not on the case becomes a **proposed** member — element 2 is still confirmed — and the lead
confirms proposed members in the team panel, with an e-mail. A proposed member cannot sign in (ruling b).
Pure functions: the routes load and save.
"""
from __future__ import annotations

import re
from typing import Any, Iterable, Optional

from backend.storage.models import PROJECT_LEAD, PersonLocation, PersonRecord


def _norm(text: Any) -> str:
    return re.sub(r"\s+", " ", str(text or "")).strip().lower()


def lead(people: Iterable[PersonRecord]) -> Optional[PersonRecord]:
    """The project lead — the person whose role is PROJECT_LEAD."""
    return next((p for p in people if _norm(p.role) == PROJECT_LEAD), None)


def find(people: Iterable[PersonRecord], who: str) -> Optional[PersonRecord]:
    """The person `who` names: by e-mail (capital letters ignored) or by full name (spacing and case ignored)."""
    w = _norm(who)
    if not w:
        return None
    return next((p for p in people if (p.email and _norm(p.email) == w) or _norm(p.full_name) == w), None)


def _named(people: list[PersonRecord], name: str) -> bool:
    """Element 2 names this person already on the case: the full name, or a shorter form whose words begin
    exactly one person's full name ("Priya" for "Priya Shah") — never a guess between two."""
    if find(people, name) is not None:
        return True
    words = _norm(name).split()
    starts = [p for p in people if _norm(p.full_name).split()[:len(words)] == words]
    return len(starts) == 1


def reconcile_team(people: list[PersonRecord], rows: Any, by: str, at: str) -> tuple[list[PersonRecord], list[str]]:
    """Element 2 confirmed (ADR-0090 decision 3, ruling b): every person its rows name who is not on the case
    is added as a proposed member, with the role and function the Belt gave. Nobody on the case is changed.
    Returns the people and the names added."""
    out = list(people)
    added: list[str] = []
    for row in rows if isinstance(rows, list) else []:
        if not isinstance(row, dict):
            continue
        name = str(row.get("name") or "").strip()
        if not name or _named(out, name) or (row.get("email") and find(out, str(row["email"]))):
            continue
        out.append(PersonRecord(full_name=name, role=str(row.get("role") or ""),
                                function=str(row.get("function") or ""), status="proposed",
                                added_by=by, added_at=at))
        added.append(name)
    return out, added


def confirm(people: list[PersonRecord], who: str, email: str) -> list[PersonRecord]:
    """The lead confirms a proposed member (ruling b): only with an e-mail, which no one else on the case has."""
    person = find(people, who)
    if person is None:
        raise LookupError(who)
    mail = email.strip()
    if not re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", mail):
        raise ValueError("an e-mail address is needed to confirm a member")
    if any(p is not person and _norm(p.email) == _norm(mail) for p in people):
        raise ValueError(f"{mail} is already on this case")
    return [p.model_copy(update={"status": "member", "email": mail}) if p is person else p for p in people]


def complete(people: list[PersonRecord], who: str, details: dict[str, Any]) -> list[PersonRecord]:
    """The lead completes a person's details: e-mail, role, function, department, location. The lead's role
    stays the lead's; an e-mail stays unique on the case."""
    person = find(people, who)
    if person is None:
        raise LookupError(who)
    update: dict[str, Any] = {k: str(v).strip() for k, v in details.items()
                              if k in ("full_name", "email", "role", "function", "department") and v is not None}
    if "location" in details and isinstance(details["location"], dict):
        update["location"] = PersonLocation(**{k: str(details["location"].get(k) or "") for k in ("country", "site")})
    if person is lead(people):
        update.pop("role", None)
    elif _norm(update.get("role", "")) == PROJECT_LEAD:
        # DEF-104 (R8b): a role is assigned, never the lead's — the case has one lead; handing it over is R8c.
        raise ValueError("the case has one project lead — the lead role is handed over, not assigned")
    mail = update.get("email")
    if mail and any(p is not person and _norm(p.email) == _norm(mail) for p in people):
        raise ValueError(f"{mail} is already on this case")
    if not str(update.get("full_name", person.full_name)).strip():
        raise ValueError("a person needs a full name")
    return [p.model_copy(update=update) if p is person else p for p in people]


def add(people: list[PersonRecord], person: PersonRecord) -> list[PersonRecord]:
    """The lead adds a member: a full name and a role at least; never a second lead, never a name or e-mail
    already on the case."""
    if not person.full_name.strip() or not person.role.strip():
        raise ValueError("a person needs a full name and a role")
    if _norm(person.role) == PROJECT_LEAD:
        raise ValueError("the case has one project lead")
    if find(people, person.full_name) or (person.email and find(people, person.email)):
        raise ValueError(f"{person.full_name} is already on this case")
    return [*people, person]


def remove(people: list[PersonRecord], who: str) -> list[PersonRecord]:
    """DEF-104 (R8b): the lead removes a member. Never the lead: the case keeps one lead, and handing the role
    over is R8c's."""
    person = find(people, who)
    if person is None:
        raise LookupError(who)
    if person is lead(people):
        raise ValueError("the project lead cannot be removed — the lead role is handed over first")
    return [p for p in people if p is not person]


#: DEF-105 (R8c): the role the old lead keeps on the team after handing the lead over.
FORMER_LEAD_ROLE = "Team member"


def hand_over(people: list[PersonRecord], to: str) -> list[PersonRecord]:
    """DEF-105 (R8c, founder ruling 2026-10-21): the lead hands the role to another registered member — a confirmed
    member of the case; the old lead stays on the team as a team member. One lead, always."""
    current, new = lead(people), find(people, to)
    if new is None:
        raise LookupError(to)
    if new is current:
        raise ValueError(f"{new.full_name} is already the project lead")
    if new.status != "member":
        raise ValueError(f"{new.full_name} is a proposed member — the lead confirms them first")
    return [p.model_copy(update={"role": PROJECT_LEAD}) if p is new else
            p.model_copy(update={"role": FORMER_LEAD_ROLE}) if p is current else p for p in people]


def set_code(people: list[PersonRecord], who: str, digest: str, at: str) -> list[PersonRecord]:
    """ADR-0105 decisions 1 and 4: a code issued for one confirmed member with an e-mail — only its digest kept; a
    re-issue replaces (voids) the earlier one and resets the attempts."""
    person = find(people, who)
    if person is None:
        raise LookupError(who)
    if not may_sign_in(person):
        raise ValueError(f"{person.full_name} is not a confirmed member with an e-mail — the lead confirms them first")
    return [p.model_copy(update={"code_hash": digest, "code_issued_at": at, "code_attempts": 0}) if p is person else p
            for p in people]


def code_used(people: list[PersonRecord], who: str, outcome: str, limit: int) -> list[PersonRecord]:
    """ADR-0105 decisions 5 and 6: after a sign-in attempt with a code — spent on "ok"; one more failure on "wrong",
    the code voided at `limit`; voided when expired."""
    def after(p: PersonRecord) -> PersonRecord:
        if outcome in ("ok", "expired"):
            return p.model_copy(update={"code_hash": "", "code_issued_at": "", "code_attempts": 0})
        if outcome == "wrong":
            tries = p.code_attempts + 1
            return p.model_copy(update={"code_attempts": tries, **({"code_hash": ""} if tries >= limit else {})})
        return p
    person = find(people, who)
    return [after(p) if p is person else p for p in people]


def may_sign_in(person: Optional[PersonRecord]) -> bool:
    """Ruling b: a person signs in only as a member with an e-mail — a proposed member cannot."""
    return person is not None and person.status == "member" and bool(person.email.strip())


__all__ = ["lead", "find", "reconcile_team", "confirm", "complete", "add", "may_sign_in"]
