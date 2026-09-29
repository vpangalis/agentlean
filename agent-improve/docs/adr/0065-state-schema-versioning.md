# ADR-0065 — Checkpoints carry a state schema version; every state change ships a migration

Status: ACCEPTED (founder, 2026-09-29) · proposed 2026-09-28 · Requirement: T88

## Context
A DMAIC case runs for weeks or months. Its checkpoints and Store records are written by the release
that was live at the time. When `SupervisorState`, `PhaseState` or a `{Phase}Output` changes, an
older checkpoint may no longer load, or may load with missing fields. LangGraph persists state; it
does not migrate application schemas.

## Decision
1. A constant `STATE_SCHEMA_VERSION` (in `core/state.py`) is written into every checkpoint's
   metadata and every Store record.
2. Any change to a state class or phase record raises the version and adds a migration function
   `migrate_vN_to_vN+1` in `core/migrations.py`; loading a checkpoint or record with an older version
   runs the migrations in order before the graph uses it.
3. Each migration has a test that loads a saved fixture of the previous version.
4. A checkpoint with a newer version than the code refuses to load with a readable error.

## Consequences
Adding a state field costs one migration and one fixture; the generated §4.2 shows the version.

## Rejected
Discarding old checkpoints on upgrade (loses weeks of a Belt's work); lenient loading with defaults
(silent wrong data).
