"""Step 6.13 — the evidence index migration. The `pytest` half of its Verify.

Architecture §23.2 (the seven fields) · §23.2.1 (the `role` vocabulary and its
migration sentinel) · §23.4 (the write-path trap) · §24 (the structured
record). Rulings: `docs/_archive/DECISIONS.md` Part AT.

**No network.** Every Azure boundary is a fake, so what these assert is the
code that runs in production rather than a copy of it.

THE ONE THAT MATTERS MOST is `test_the_sentinel_turns_on_an_ABSENT_KEY_not_a_
falsy_value`. `role`, `shape_match` and `content_digest` are absent keys on
every pre-6.12 upload record; loading such a record through `UploadRecord`
manufactures `'other evidence'` and `'unsolicited'` as Pydantic defaults. A
migration that read the model instead of the stored JSON would write a
fabricated role into a filterable field **and report success** — §23.4's
failure class arriving through the model layer. The distinction is invisible
at every layer above the raw dict, so it is pinned here.
"""
from __future__ import annotations

import json
from typing import Any

import pytest

from backend.knowledge import retriever, tools
from backend.knowledge.retriever import (
    EVIDENCE_INDEX_FIELDS,
    EVIDENCE_KIND_DEFAULT,
    EVIDENCE_SELECT,
)

# The seven §23.2 applies at this step.
THE_SEVEN = ("phase", "uploaded_at", "role", "kind",
             "description", "content_digest", "shape_match")

SENTINEL = "unclassified (pre-ask-binding)"


class FakeSearchClient:
    """Records the kwargs it was called with, returns canned rows."""

    def __init__(self, rows: list[dict]):
        self.rows = rows
        self.calls: list[dict] = []

    def search(self, **kwargs: Any):
        self.calls.append(kwargs)
        return list(self.rows)


class FakeEmbeddings:
    def embed_query(self, text: str) -> list[float]:
        return [0.1, 0.2, 0.3]


def evidence_row(**over: Any) -> dict:
    row = {
        "id": "doc1", "content": "cycle time by station", "case_id": "C1",
        "metadata": json.dumps({"filename": "cycle_times.xlsx",
                                "blob_path": "uploads/C1/cycle_times.xlsx",
                                "upload_phase": "measure",
                                "timestamp": "2026-09-09T10:23:21+00:00"}),
        "phase": "measure", "uploaded_at": "2026-09-09T10:23:21+00:00",
        "role": "cycle time data", "kind": "evidence",
        "description": "Cycle times for four stations.",
        "content_digest": "db1b5285b6a1", "shape_match": "full",
    }
    row.update(over)
    return row


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    monkeypatch.setattr(retriever, "get_embeddings", lambda: FakeEmbeddings())


# ── §23.4: the fields declaration ──────────────────────────────────────────

def test_EVIDENCE_INDEX_FIELDS_declares_all_seven():
    """§23.4 — a metadata key reaches a filterable field only if declared.

    The list guards `get_evidence_vectorstore`, which nothing currently calls
    (Part AT). It is asserted anyway: a dead function revived without this
    list fails **silently**, and the silence is the failure mode.
    """
    declared = {f.name for f in EVIDENCE_INDEX_FIELDS}
    assert set(THE_SEVEN) <= declared
    # The original five must not have been dropped on the way in.
    assert {"id", "content", "content_vector", "metadata", "case_id"} <= declared


def test_the_projection_selects_every_field_the_record_reads():
    """A field missing from `select` comes back ABSENT, not empty — so §24's
    record would render `unknown` for a value the index actually holds."""
    for name in THE_SEVEN:
        assert name in EVIDENCE_SELECT, f"{name} would never reach the record"


# ── sub-step 4: the default kind filter ────────────────────────────────────

def test_search_evidence_filters_to_evidence_by_default(monkeypatch):
    fake = FakeSearchClient([evidence_row()])
    monkeypatch.setattr(retriever, "SearchClient", lambda **kw: fake)

    retriever.search_evidence("cycle time", case_id="C1")

    odata = fake.calls[0]["filter"]
    assert "case_id eq 'C1'" in odata
    assert "kind eq 'evidence'" in odata


def test_an_artefact_does_not_surface_on_an_unfiltered_evidence_query(monkeypatch):
    """Part AP2 ruling 3's second binding condition — **a test, not an
    observation**, which is how 6.13's Done-when words it.

    A to-be process map is what the team DESIGNED. One bucket would let a
    proposed future be retrieved later as a fact about the present.
    """
    fake = FakeSearchClient([])
    monkeypatch.setattr(retriever, "SearchClient", lambda **kw: fake)

    retriever.search_evidence("what is the to-be process", case_id="C1")

    # The artefact never reaches the client: the filter excludes it at Azure.
    assert "kind eq 'evidence'" in fake.calls[0]["filter"]
    assert EVIDENCE_KIND_DEFAULT == "evidence"


def test_searching_both_kinds_is_explicit_and_visible_at_the_call_site(monkeypatch):
    fake = FakeSearchClient([evidence_row()])
    monkeypatch.setattr(retriever, "SearchClient", lambda **kw: fake)

    retriever.search_evidence("anything", case_id="C1", kind=None)

    assert "kind eq" not in fake.calls[0]["filter"]


def test_the_case_filter_survives_an_odata_quote_in_either_argument(monkeypatch):
    fake = FakeSearchClient([])
    monkeypatch.setattr(retriever, "SearchClient", lambda **kw: fake)

    retriever.search_evidence("q", case_id="O'Brien", kind="o'ther")

    odata = fake.calls[0]["filter"]
    assert "case_id eq 'O''Brien'" in odata
    assert "kind eq 'o''ther'" in odata


# ── §24: the structured record ─────────────────────────────────────────────

def test_the_record_carries_every_field_24_names():
    """§24: role · kind · description · phase · uploaded_at · shape_match,
    then blob_path · content_digest, then the excerpt."""
    row = dict(evidence_row(), blob_path="uploads/C1/cycle_times.xlsx",
               filename="cycle_times.xlsx")
    record = tools._evidence_record(row)

    for key in ("role:", "kind:", "description:", "phase:", "uploaded_at:",
                "shape_match:", "blob_path:", "content_digest:", "excerpt:"):
        assert key in record, f"§24 names {key} and the record omits it"


def test_the_record_returns_values_not_rendered_prose():
    """The reason §24 gives: choosing a file is a question about FIELDS.

    *"Which of these three is the current cycle-time data"* is answered by
    `role`, `uploaded_at` and `shape_match` — not by similarity, and not by
    re-deriving from prose what the index already holds as values.
    """
    record = tools._evidence_record(dict(evidence_row(),
                                         blob_path="uploads/C1/f.xlsx"))
    assert "cycle time data" in record
    assert "2026-09-09T10:23:21+00:00" in record
    assert "db1b5285b6a1" in record          # the citation anchor, §6


def test_a_missing_value_reads_unknown_rather_than_vanishing():
    """A missing LINE reads as 'this file has no role'. It means 'this
    document predates the field'."""
    record = tools._evidence_record({"id": "d", "content": "x"})
    assert "role: unknown" in record


# ── Part AT1: the sentinel turns on an ABSENT KEY ──────────────────────────

def test_the_sentinel_turns_on_an_ABSENT_KEY_not_a_falsy_value():
    """**The single most important assertion in this file.**

    `role_of` must answer the sentinel when the key is absent and the stored
    value when it is present. Reading a loaded `UploadRecord` instead would
    answer `'other evidence'` for both — a fabricated role written into a
    filterable field, recorded as migrated (Part AT1).
    """
    from scripts.backfill_evidence_index import role_of

    assert role_of({"filename": "x.csv"}) == SENTINEL          # absent
    assert role_of({"role": "cycle time data"}) == "cycle time data"
    assert role_of({"role": ""}) == SENTINEL                   # present, empty


def test_the_sentinel_is_not_other_evidence():
    """§23.2.1 reads a rising count of `other` as the signal to extend the
    vocabulary. Backfilling into that row would make the signal measure the
    migration instead of the corpus."""
    from backend.upload.asks import SENTINEL_ROLE

    assert SENTINEL_ROLE != "other evidence"
    assert SENTINEL_ROLE == SENTINEL


def test_the_sentinel_row_exists_in_the_ratified_vocabulary():
    """The AR3 class of check — the code and the document that ratifies it
    must agree, with no model and no network.

    §23.2.1 says extending this vocabulary is a GOVERNANCE EVENT. A sentinel
    that existed only in code would be a value no query filters on and no
    reviewer can see, which is precisely what that rule forbids.
    """
    from pathlib import Path

    from backend.upload.asks import SENTINEL_KIND, SENTINEL_ROLE

    arch = (Path(__file__).resolve().parents[2] / "ARCHITECTURE.md").read_text(
        encoding="utf-8")
    row = f"| `{SENTINEL_ROLE}` | {SENTINEL_KIND} | any |"
    assert row in arch, f"§23.2.1 has no row reading {row!r}"


# ── Part AT3: the supersession sweep ───────────────────────────────────────

def test_every_version_but_the_newest_of_one_blob_path_is_swept():
    """`storage/blob.py` writes with `overwrite=True`, so one `blob_path`
    uploaded twice leaves the LATER bytes and both index documents. A digest
    for the earlier one could only be the later one's — the newer version's
    identity written onto the older chunk."""
    from scripts.backfill_evidence_index import mark_superseded

    records = [
        {"case_id": "C1", "phase": "define",
         "raw": {"blob_path": "uploads/C1/a.csv", "uploaded_at": "08:09",
                 "evidence_index_id": "old"}},
        {"case_id": "C1", "phase": "define",
         "raw": {"blob_path": "uploads/C1/a.csv", "uploaded_at": "10:23",
                 "evidence_index_id": "new"}},
    ]
    assert mark_superseded(records) == {"old"}


def test_a_single_version_is_never_swept():
    from scripts.backfill_evidence_index import mark_superseded

    records = [
        {"case_id": "C1", "phase": "define",
         "raw": {"blob_path": "uploads/C1/a.csv", "uploaded_at": "08:09",
                 "evidence_index_id": "only"}},
    ]
    assert mark_superseded(records) == set()


def test_two_cases_uploading_the_same_filename_do_not_supersede_each_other():
    """Supersession is scoped to the case, like everything else in §23.2 —
    evidence SHALL NOT leak across cases (S-F15 B1)."""
    from scripts.backfill_evidence_index import mark_superseded

    records = [
        {"case_id": "C1", "phase": "define",
         "raw": {"blob_path": "uploads/C1/a.csv", "uploaded_at": "08:09",
                 "evidence_index_id": "c1"}},
        {"case_id": "C2", "phase": "define",
         "raw": {"blob_path": "uploads/C2/a.csv", "uploaded_at": "10:23",
                 "evidence_index_id": "c2"}},
    ]
    assert mark_superseded(records) == set()


# ── sub-step 2: the write path ─────────────────────────────────────────────

def test_index_upload_writes_all_seven_as_TOP_LEVEL_fields(monkeypatch):
    """§23.4 is the whole point: a value in the `metadata` JSON blob is
    unreachable by `$filter`, **with no error raised**. That is how
    `phase_relevance` went unpopulated, and each of the seven is two changes
    rather than one — the key name AND the declaration."""
    import asyncio

    import azure.search.documents.aio as aio

    from backend.gateway import routes

    captured: dict = {}

    class FakeAioClient:
        def __init__(self, **kw): ...
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def upload_documents(self, docs):
            captured["doc"] = docs[0]

    class FakeEmb:
        async def aembed_query(self, text): return [0.1, 0.2]

    monkeypatch.setattr(aio, "SearchClient", FakeAioClient)
    monkeypatch.setattr(
        "backend.knowledge.retriever.get_embeddings", lambda: FakeEmb())

    record = {
        "filename": "cycle_times.xlsx", "timestamp": "2026-09-10T09:00:00+00:00",
        "extracted_text": "station,seconds", "phase": "measure",
        "kind": "evidence", "summary": "Cycle times for four stations.",
        "content_type": "spreadsheet", "blob_path": "uploads/C1/cycle_times.xlsx",
    }
    asyncio.run(routes._index_upload(
        "C1", record,
        role="cycle time data", shape_match="full", content_digest="abc123",
    ))

    doc = captured["doc"]
    for name in THE_SEVEN:
        assert name in doc, f"{name} is not a top-level field — §23.4"
    assert doc["role"] == "cycle time data"
    assert doc["kind"] == "evidence"
    assert doc["shape_match"] == "full"
    assert doc["content_digest"] == "abc123"
    assert doc["phase"] == "measure"
    assert doc["description"] == "Cycle times for four stations."


def test_the_description_is_a_projection_of_the_records_summary(monkeypatch):
    """§23.2 declares `description` a PROJECTION. The case blob is the system
    of record; a change to the summary means re-indexing the document, never
    an in-place edit of the index copy."""
    import asyncio

    import azure.search.documents.aio as aio

    from backend.gateway import routes

    captured: dict = {}

    class FakeAioClient:
        def __init__(self, **kw): ...
        async def __aenter__(self): return self
        async def __aexit__(self, *a): return False
        async def upload_documents(self, docs): captured["doc"] = docs[0]

    class FakeEmb:
        async def aembed_query(self, text): return [0.1]

    monkeypatch.setattr(aio, "SearchClient", FakeAioClient)
    monkeypatch.setattr(
        "backend.knowledge.retriever.get_embeddings", lambda: FakeEmb())

    asyncio.run(routes._index_upload(
        "C1",
        {"filename": "f.csv", "timestamp": "t", "extracted_text": "x",
         "summary": "THE INTERPRETATION'S SUMMARY", "kind": "evidence"},
        role="other evidence", shape_match="unsolicited", content_digest="d",
    ))

    assert captured["doc"]["description"] == "THE INTERPRETATION'S SUMMARY"
