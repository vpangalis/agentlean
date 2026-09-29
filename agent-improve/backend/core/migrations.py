"""State schema versions and their migrations — ADR-0065 (ACCEPTED, founder 2026-09-29), T88.

A DMAIC case runs for weeks. Its checkpoints and Store records were written by the release that
was live then, and LangGraph persists state without migrating an application's schema. So:

    STATE_SCHEMA_VERSION  (core/state.py) is written into every checkpoint's metadata (by
                          `AzureBlobCheckpointSaver.put`) and into every Store record (by
                          `AzureBlobStore`), under `VERSION_KEY`.
    on load               an older version runs `MIGRATIONS` in order before the graph sees it;
                          a NEWER version than the code refuses to load with a readable error
                          (`StateSchemaVersionError`) — nothing is changed or guessed.
    a missing version     is version 1: everything written before versioning existed.

Each migration is a module-level function `migrate_vN_to_vN+1(values) -> values` over a flat
mapping — a checkpoint's `channel_values`, a pending write's `{channel: value}`, or a Store
record — and returns a NEW mapping; it never deletes a value it cannot convert (ADR-0071 point
5). Each has a test that loads a saved fixture of the version before it
(`backend/tests/fixtures/state_schema/`).
"""
from __future__ import annotations

from typing import Any, Callable, Mapping

from backend.core.errors import StateSchemaVersionError
from backend.core.state import STATE_SCHEMA_VERSION

#: Where the version is written: a checkpoint's metadata key, and a Store record's own key.
VERSION_KEY = "state_schema_version"
#: The version of anything written before versioning existed.
UNVERSIONED = 1

Migration = Callable[[Mapping[str, Any]], dict[str, Any]]

#: {N: migrate_vN_to_vN+1}. Adding a state change raises STATE_SCHEMA_VERSION by one and adds
#: its function here, with its fixture test.
MIGRATIONS: dict[int, Migration] = {}


def current() -> int:
    """This release's version (read at call time, so a test can stand in a later release)."""
    return STATE_SCHEMA_VERSION


def version_of(carrier: Mapping[str, Any] | None) -> int:
    """The version a checkpoint's metadata or a Store record carries; 1 when it carries none."""
    raw = (carrier or {}).get(VERSION_KEY)
    try:
        return int(raw) if raw is not None else UNVERSIONED
    except (TypeError, ValueError):
        raise StateSchemaVersionError(
            f"The saved state carries an unreadable schema version ({raw!r}); it was not loaded "
            "and nothing was changed.", found=None, supported=current()) from None


def check_loadable(found: int, what: str) -> None:
    """Refuse state written by a newer release, readably (ADR-0065 point 4)."""
    if found > current():
        raise StateSchemaVersionError(
            f"This {what} was saved by a newer release of Agent Improve (state schema version "
            f"{found}); this release reads up to version {current()}. Open the case with "
            "the newer release — nothing was loaded and nothing was changed.",
            found=found, supported=current())


def migrate(values: Mapping[str, Any], found: int, what: str = "saved state") -> dict[str, Any]:
    """`values` brought from version `found` to STATE_SCHEMA_VERSION, the migrations in order."""
    check_loadable(found, what)
    out = dict(values)
    for n in range(found, current()):
        step = MIGRATIONS.get(n)
        if step is None:
            raise StateSchemaVersionError(
                f"No migration from state schema version {n} to {n + 1}; the {what} was not loaded.",
                found=found, supported=current())
        out = step(out)
    return out


def stamp_metadata(metadata: Mapping[str, Any]) -> dict[str, Any]:
    """A checkpoint's metadata with this release's version written into it."""
    return {**dict(metadata or {}), VERSION_KEY: current()}


def stamp_record(value: Mapping[str, Any]) -> dict[str, Any]:
    """A Store record as written: the value with this release's version beside its keys."""
    return {**dict(value), VERSION_KEY: current()}


def read_record(stored: Mapping[str, Any]) -> dict[str, Any]:
    """A Store record as read: refused if newer, migrated if older, the version key removed so
    every reader sees the value exactly as it was put."""
    found = version_of(stored)
    value = {k: v for k, v in stored.items() if k != VERSION_KEY}
    return migrate(value, found, "Store record")


def migrate_case(data: Mapping[str, Any], found: int) -> dict[str, Any]:
    """A case blob (`storage/models.CaseDocument`, as JSON) brought to this release: each phase
    record's captured values and field statuses run through the migrations as one state-shaped
    mapping (`{"artifacts", "field_status"}`), exactly as a checkpoint's channels do."""
    check_loadable(found, "case record")
    out = dict(data)
    phases: dict[str, Any] = {}
    for name, record in (data.get("phases") or {}).items():
        rec = dict(record or {})
        moved = migrate({"artifacts": dict(rec.get("structured") or {}),
                         "field_status": dict(rec.get("field_status") or {})}, found, "case record")
        if rec.get("structured") is not None:
            rec["structured"] = moved["artifacts"]
        rec["field_status"] = moved["field_status"]
        phases[name] = rec
    out["phases"] = phases
    out[VERSION_KEY] = current()
    return out


__all__ = ["current", "migrate_case", "VERSION_KEY", "UNVERSIONED", "MIGRATIONS", "version_of", "check_loadable", "migrate",
           "stamp_metadata", "stamp_record", "read_record"]
