"""Operational scripts — a package so their pure helpers can be tested.

**Added at step 6.13**, when `backend/tests/test_evidence_index.py` became the
first test to import a script. Without this file mypy resolves the same path
under two module names (`backfill_evidence_index` and
`scripts.backfill_evidence_index`) and refuses to check either.

Every module here is still runnable as `python scripts/<name>.py` — each puts
the repository root on `sys.path` itself.
"""
