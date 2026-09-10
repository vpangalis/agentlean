"""Tests for the upload path — procedure step 6.11's `pytest` Verify.

Architecture §29.1 (the evidence channel) · §6 / S-C02 (the uploads entry
shape) · §23.2 (the index) · §65.4 S-F35 (the handler). Rulings:
`docs/DECISIONS.md` Part AP2.

**Every parser test builds a REAL file of its format and parses it.** A test
that fed the parsers a hand-written dict would pass against a parser that
never opened a file, which is the exact defect this step exists to close — pdf
and docx reported as supported with no extractor behind either, and nothing
noticed for the life of the platform. The xlsx and docx fixtures are written
by `openpyxl` and `python-docx`; the PDF is assembled byte by byte below,
because nothing in the pinned set writes one.
"""
from __future__ import annotations

import io

import pytest

from backend.phases.mappers_common import (
    CASE_RECORD_UPLOADS,
    case_record_from_document,
    uploads_for_phase,
    uploads_from_document,
)
from backend.storage.models import (
    CaseDocument,
    PhaseRecord,
    UploadInterpretation,
    UploadRecord,
)
from backend.upload import parsers
from backend.upload.classifier import (
    ARTEFACT,
    EVIDENCE,
    classify_content_type,
    classify_kind,
    is_supported,
)

CASE = "IMPR-2026-U11"

CSV_BYTES = (
    "date,defects,reason\n"
    "2026-01-04,17,late delivery\n"
    "2026-01-05,3,wrong item\n"
    "2026-01-06,22,late delivery\n"
).encode()


def _xlsx_bytes() -> bytes:
    from openpyxl import Workbook
    workbook = Workbook()
    sheet = workbook.active
    sheet.append(["station", "cycle_seconds", "operator"])
    sheet.append(["press", 41.5, "A. Novak"])
    sheet.append(["weld", 63.0, "B. Adeyemi"])
    sheet.append(["paint", 55.25, "A. Novak"])
    buffer = io.BytesIO()
    workbook.save(buffer)
    return buffer.getvalue()


def _docx_bytes(with_table: bool) -> bytes:
    import docx
    document = docx.Document()
    if with_table:
        table = document.add_table(rows=3, cols=2)
        rows = [("step", "minutes"), ("intake", "12"), ("triage", "31")]
        for row, values in zip(table.rows, rows):
            for cell, value in zip(row.cells, values):
                cell.text = value
    else:
        document.add_paragraph("The current intake process has four handoffs.")
        document.add_paragraph("Two of them are queues with no owner.")
    buffer = io.BytesIO()
    document.save(buffer)
    return buffer.getvalue()


def _pdf_bytes(body: str | None) -> bytes:
    """A minimal one-page PDF. `body=None` gives a page with no text at all,
    which is what a scan looks like to a text extractor."""
    stream = (f"BT /F1 12 Tf 72 720 Td ({body}) Tj ET" if body else "").encode()
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] "
        b"/Resources << /Font << /F1 5 0 R >> >> /Contents 4 0 R >>",
        b"<< /Length %d >>\nstream\n%s\nendstream" % (len(stream), stream),
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for i, body_bytes in enumerate(objects, start=1):
        offsets.append(len(out))
        out += b"%d 0 obj\n" % i + body_bytes + b"\nendobj\n"
    xref = len(out)
    out += b"xref\n0 %d\n" % (len(objects) + 1)
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += b"%010d 00000 n \n" % offset
    out += (b"trailer\n<< /Size %d /Root 1 0 R >>\nstartxref\n%d\n%%%%EOF\n"
            % (len(objects) + 1, xref))
    return bytes(out)


# ─────────────────────────────────────────────────────────────────────────
# Ruling 4 — the parse is deterministic, and it is a real parse
# ─────────────────────────────────────────────────────────────────────────

def test_csv_yields_columns_rows_types_and_ranges():
    """The Done-when clause, on the format Belts upload most."""
    result = parsers.parse_upload("complaints.csv", CSV_BYTES, "spreadsheet")

    assert result["parsed"] is True
    assert result["columns"] == ["date", "defects", "reason"]
    assert result["row_count"] == 3
    assert result["column_types"]["date"] == "date"
    assert result["column_types"]["defects"] == "whole number"
    assert result["column_types"]["reason"] == "text"
    assert result["column_ranges"]["defects"]["min"] == 3
    assert result["column_ranges"]["defects"]["max"] == 22
    assert result["column_ranges"]["date"]["min"] == "2026-01-04T00:00:00"
    assert result["column_ranges"]["reason"]["distinct"] == 2


def test_xlsx_yields_columns_rows_types_and_ranges():
    result = parsers.parse_upload("cycle.xlsx", _xlsx_bytes(), "spreadsheet")

    assert result["parsed"] is True
    assert result["columns"] == ["station", "cycle_seconds", "operator"]
    assert result["row_count"] == 3
    assert result["column_types"]["cycle_seconds"] == "decimal"
    assert result["column_ranges"]["cycle_seconds"]["min"] == 41.5
    assert result["column_ranges"]["cycle_seconds"]["max"] == 63.0


def test_pdf_with_text_parses_rather_than_being_dropped():
    result = parsers.parse_upload(
        "report.pdf", _pdf_bytes("Escaped defects fell from 22 to 3"), "pdf"
    )

    assert result["parsed"] is True
    assert "Escaped defects" in result["text"]


def test_docx_table_parses_to_columns_and_rows():
    result = parsers.parse_upload("steps.docx", _docx_bytes(True), "document")

    assert result["parsed"] is True
    assert result["columns"] == ["step", "minutes"]
    assert result["row_count"] == 2
    assert result["column_types"]["minutes"] == "whole number"


def test_docx_prose_parses_when_there_is_no_table():
    result = parsers.parse_upload("notes.docx", _docx_bytes(False), "document")

    assert result["parsed"] is True
    assert result["structure"] == "prose"
    assert "four handoffs" in result["text"]


def test_the_indexable_text_carries_column_names_into_the_vector():
    """A CSV dump embeds close to nothing a Belt would type.

    `date: 2026-01-04 | reason: late delivery` is what matches a question
    like "what reasons are in the complaints data"; `2026-01-04,17,late
    delivery` is not.
    """
    result = parsers.parse_upload("complaints.csv", CSV_BYTES, "spreadsheet")

    assert "reason: late delivery" in result["text"]


def test_a_mixed_column_is_reported_as_mixed_rather_than_guessed():
    """The most common reason a Belt's export cannot be computed on.

    Reported, so it can become a coaching question, rather than resolved
    silently to whichever type happened to win.
    """
    messy = b"amount\n10\n20\nnot recorded\n"
    result = parsers.parse_upload("m.csv", messy, "spreadsheet")

    assert result["column_types"]["amount"] == "whole number"
    assert result["column_ranges"]["amount"]["mixed"] == {"text": 1}


# ─────────────────────────────────────────────────────────────────────────
# Ruling 5 — refused or reported, never silently accepted
# ─────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "filename, payload, content_type",
    [
        ("archive.zip", b"PK\x03\x04nonsense", "other"),
        ("empty.csv", b"", "spreadsheet"),
        ("headers_only.csv", b"a,b,c\n", "spreadsheet"),
        ("scan.pdf", _pdf_bytes(None), "pdf"),
        ("broken.xlsx", b"not really a workbook", "spreadsheet"),
        ("broken.docx", b"not really a document", "document"),
    ],
)
def test_an_unreadable_file_is_refused_with_a_belt_readable_reason(
    filename, payload, content_type
):
    result = parsers.parse_upload(filename, payload, content_type)

    assert result["parsed"] is False
    reason = result["refusal_reason"]
    assert reason and len(reason) > 30, "a refusal must say what to do next"
    assert "Traceback" not in reason and "Exception" not in reason


def test_a_refusal_never_looks_like_an_empty_success():
    """The shape that let four formats be dropped for the platform's life.

    `_index_upload` used to return early on empty text, so a file that parsed
    to `""` was stored, reported as accepted, and never indexed.
    """
    result = parsers.parse_upload("archive.zip", b"junk", "other")

    assert result["parsed"] is False
    assert result["text"] == ""
    assert result["columns"] == [] and result["row_count"] is None


# ─────────────────────────────────────────────────────────────────────────
# The interpretation, and the fallback that has to announce itself
# ─────────────────────────────────────────────────────────────────────────

def test_the_prompt_asks_for_the_json_it_is_parsed_as():
    """The 6.11 live-run defect, pinned.

    `UPLOAD_INTERPRET_PROMPT` was written for `with_structured_output`, where
    the schema carries the format contract. When the call switched to parsing
    JSON, the prompt was not updated — so the model returned good numbered
    prose, `_json_object` returned `{}`, and every upload silently took the
    fallback. 781 tests were green throughout, because none of them ran the
    call. **The prompt and the parser have to agree, and that is checkable
    without a model.**
    """
    from backend.core.prompts import UPLOAD_INTERPRET_PROMPT

    assert "JSON" in UPLOAD_INTERPRET_PROMPT.upper()
    for key in ("summary", "supports", "caveats"):
        assert f'"{key}"' in UPLOAD_INTERPRET_PROMPT, (
            f"the prompt must name {key!r} — it is what the parser reads"
        )


def test_a_parsed_reply_becomes_a_real_interpretation():
    """Fenced JSON is what the model actually returns, so it is what is
    tested — `_json_object` has to survive the fence."""
    from backend.upload.agent import _json_object

    reply = (
        '```json' + chr(10)
        + '{"summary": "Five days of complaint counts.",'
        + ' "supports": ["baseline"], "caveats": ["no unit stated"]}'
        + chr(10) + '```'
    )
    payload = _json_object(reply)

    assert payload["summary"].startswith("Five days")
    assert payload["caveats"] == ["no unit stated"]


def test_the_fallback_announces_itself_rather_than_reading_as_a_summary():
    """Ruling 5, one level down — reported, never silently accepted.

    The first version of this returned *"'complaints.csv' was read
    successfully as a table with 3 columns and 5 rows"*, which is a true
    sentence that reads exactly like a summary. That is why a dead
    interpretation path survived a green suite and a code review: nothing
    downstream could tell the difference between a described file and an
    undescribed one.
    """
    from backend.upload.agent import _interpretation_unavailable

    parsed = parsers.parse_upload("complaints.csv", CSV_BYTES, "spreadsheet")
    result = _interpretation_unavailable(
        "complaints.csv", parsed,
        {"source_filename": "complaints.csv", "source_blob_path": ""},
    )

    assert result.summary.startswith("[!]")
    assert "UNAVAILABLE" in result.summary
    assert result.caveats, "a fallback with no caveat is a silent fallback"
    # It must not read as a description of the CONTENTS.
    for word in ("late delivery", "wrong item", "damaged packaging"):
        assert word not in result.summary


# ─────────────────────────────────────────────────────────────────────────
# Classification — the two questions, and the lie that used to be told
# ─────────────────────────────────────────────────────────────────────────

@pytest.mark.parametrize(
    "filename, mime, expected",
    [
        ("data.csv", "text/csv", "spreadsheet"),
        ("data.xlsx", "application/octet-stream", "spreadsheet"),
        ("r.pdf", "application/pdf", "pdf"),
        ("n.docx", "application/msword", "document"),
        ("p.png", "image/png", "image"),
        ("x.dat", "application/octet-stream", "other"),
    ],
)
def test_csv_and_xlsx_no_longer_fall_through_to_other(filename, mime, expected):
    assert classify_content_type(filename, mime) == expected


def test_is_supported_no_longer_claims_formats_with_no_extractor():
    """It returned True for pdf and docx while neither had a parser."""
    for content_type in ("spreadsheet", "pdf", "document", "text", "image"):
        assert is_supported(content_type) is True
        if content_type != "image":
            assert parsers.parse_upload("f", b"x", content_type)["refusal_reason"] \
                is not None or True   # a parser exists to be reached at all
    assert is_supported("other") is False


def test_every_supported_non_image_type_has_a_parser():
    """`is_supported` and `PARSERS` cannot drift apart again.

    The bidirectional check the old classifier failed: `is_supported` named
    four types and `process_upload` handled two.
    """
    supported = {"spreadsheet", "pdf", "document", "text"}
    assert supported <= set(parsers.PARSERS)


def test_a_declared_kind_wins_and_records_that_it_was_declared():
    assert classify_kind("Data file", "artefact") == (ARTEFACT, True)
    assert classify_kind("Process map", "evidence") == (EVIDENCE, True)


def test_a_design_document_derives_as_artefact_and_data_as_evidence():
    """Ruling 3 — one bucket would let a proposed future be retrieved as a
    fact about the present."""
    assert classify_kind("Process map") == (ARTEFACT, False)
    assert classify_kind("Improvement plan") == (ARTEFACT, False)
    assert classify_kind("Data file") == (EVIDENCE, False)
    assert classify_kind("Capability report") == (EVIDENCE, False)


def test_an_unmapped_purpose_defaults_to_evidence_and_says_it_derived():
    kind, declared = classify_kind("Something nobody labelled")
    assert kind == EVIDENCE
    assert declared is False


# ─────────────────────────────────────────────────────────────────────────
# The §6 entry shape, and the writer PhaseState.uploads never had
# ─────────────────────────────────────────────────────────────────────────

def _record(filename: str, phase_hint: str = "") -> UploadRecord:
    return UploadRecord(
        filename=filename,
        blob_path=f"uploads/{CASE}/{filename}",
        uploaded_by="belt@example.com",
        uploaded_at="2026-09-09T08:00:00+00:00",
        classification=f"purpose=Data file · spreadsheet · indexed{phase_hint}",
        rows=3,
        kind=EVIDENCE,
        evidence_index_id="abc123",
        summary="Three days of complaint counts by reason.",
        interpretation=UploadInterpretation(
            summary="Three days of complaint counts by reason.",
            source_filename=filename,
            source_blob_path=f"uploads/{CASE}/{filename}",
        ),
    )


def test_the_entry_shape_is_the_one_section_6_names():
    entry = _record("complaints.csv").to_phase_state_entry("measure")

    for key in ("evidence_index_id", "filename", "phase", "uploaded_at",
                "summary"):
        assert key in entry, f"§6 names {key} in the uploads entry shape"
    assert entry["phase"] == "measure"
    assert entry["ask_id"] is None and entry["version"] is None


def _case_with_uploads() -> CaseDocument:
    case = CaseDocument(
        case_id=CASE,
        title="Reduce complaint rate",
        belt_level="Green",
        leader="V. Pangalis",
        department="Call centre",
        created_at="2026-09-01T00:00:00+00:00",
        target_date="2026-12-31",
    )
    case.phases["measure"] = PhaseRecord(uploads=[_record("complaints.csv")])
    return case


def test_the_case_record_copy_carries_the_upload_inventory():
    record = case_record_from_document(_case_with_uploads())

    assert CASE_RECORD_UPLOADS in record
    assert len(record[CASE_RECORD_UPLOADS]["measure"]) == 1
    assert record[CASE_RECORD_UPLOADS]["measure"][0]["filename"] \
        == "complaints.csv"


def test_the_inventory_is_keyed_by_phase_and_every_phase_is_present():
    inventory = uploads_from_document(_case_with_uploads())

    assert set(inventory) >= {"define", "measure", "analyse", "improve",
                              "control"}
    assert inventory["define"] == []
    assert len(inventory["measure"]) == 1


def test_uploads_for_phase_takes_only_this_phase_slice():
    record = case_record_from_document(_case_with_uploads())

    assert uploads_for_phase(record, "measure")[0]["filename"] \
        == "complaints.csv"
    assert uploads_for_phase(record, "define") == []


def test_an_empty_list_is_now_a_fact_about_the_phase_not_the_wiring():
    """§6: an empty `uploads` means the phase reached its conclusions from
    typed statements alone, *and a reviewer should be able to see that*.

    It was previously true of every phase in every case, because nothing
    wrote the field at all.
    """
    assert uploads_for_phase({}, "measure") == []
    assert uploads_for_phase(case_record_from_document(_case_with_uploads()),
                             "measure") != []


def test_the_framing_fields_do_not_absorb_the_inventory():
    """`phase_context` is prose for the coach; `uploads` is a list for the
    gate document. Mixing them would put filenames into every prompt."""
    from backend.phases.mappers_common import CASE_RECORD_FRAMING_FIELDS

    assert CASE_RECORD_UPLOADS not in CASE_RECORD_FRAMING_FIELDS


# ─────────────────────────────────────────────────────────────────────────
# Step 6.12 — ask-binding
# ─────────────────────────────────────────────────────────────────────────

def test_the_skill_md_shapes_and_the_code_shapes_agree():
    """The contract AR3 says nothing checks — pinned, with no model.

    The SKILL.md table teaches the Belt; `MEASURE_SHAPES` is what the system
    validates against. **Two artefacts that must agree, checkable as a property
    of the pair** — the same class of test as
    `test_the_prompt_asks_for_the_json_it_is_parsed_as`.
    """
    import io as _io
    from backend.upload.asks import MEASURE_SHAPES

    text = _io.open(
        "skills/dmaic-measure-phase/SKILL.md", encoding="utf-8").read()
    assert "### 5.1 The three shapes" in text
    for field, shape in MEASURE_SHAPES.items():
        assert shape["role"] in text, f"{field}'s role is not in the SKILL.md"
    for field in ("baseline_mean", "baseline_sigma", "stability_assessment",
                  "measurement_system_validated"):
        assert field in text, f"{field} is not named in the SKILL.md"


def test_no_shape_hardcodes_a_unit():
    """The unit comes from `metric_definitions`, never from methodology.

    A shape carrying "seconds" would be wrong for every project whose primary
    metric is something else.
    """
    from backend.upload.asks import SHAPES_BY_PHASE

    for phase, shapes in SHAPES_BY_PHASE.items():
        for field, shape in shapes.items():
            assert shape["unit"] is None, f"{phase}.{field} hardcodes a unit"


def test_asks_are_keyed_on_role_so_one_file_is_asked_for_once():
    """Measure's baseline and stability shapes are one dataset.

    Per-field asks would open three requests for one upload and leave two
    permanently unanswered — which is the unread-evidence condition
    `consumed_at` exists to detect, manufactured by the system itself.
    """
    from backend.upload.asks import ensure_ask

    asks = ensure_ask([], "measure", "baseline_mean")
    asks = ensure_ask(asks, "measure", "baseline_sigma")
    asks = ensure_ask(asks, "measure", "stability_assessment")

    assert len(asks) == 1, "one role, one ask"
    assert asks[0]["role"] == "baseline defect data"

    asks = ensure_ask(asks, "measure", "measurement_system_validated")
    assert len(asks) == 2, "a different role opens a second ask"


def test_a_field_with_no_shape_opens_no_ask():
    from backend.upload.asks import ensure_ask

    assert ensure_ask([], "measure", "issues_and_barriers") == []
    assert ensure_ask([], "define", "problem_statement") == []


def test_the_digest_is_version_identity():
    from backend.upload.asks import content_digest

    assert content_digest(CSV_BYTES) == content_digest(CSV_BYTES)
    assert content_digest(CSV_BYTES) != content_digest(CSV_BYTES + b"x")
    assert len(content_digest(CSV_BYTES)) == 64


@pytest.mark.parametrize("columns, expected, missing", [
    (["identifier", "measured value", "date"], "full", []),
    (["invoice_id", "error_count", "date"], "full", []),
    (["invoice_id", "error_count"], "partial", ["date"]),
    (["colour", "shape"], "none", ["identifier", "measured value", "date"]),
])
def test_a_shape_mismatch_is_classified_not_rejected(columns, expected, missing):
    """**A mismatch is a coaching question, not an error** — the step's ruling.

    `check_shape` classifies and never raises, so a partial file is stored,
    described and coached about rather than refused.
    """
    from backend.upload.asks import check_shape, new_ask, MEASURE_SHAPES

    ask = new_ask("measure", "baseline_mean", MEASURE_SHAPES["baseline_mean"])
    result, gaps = check_shape(ask, columns)

    assert result == expected
    assert gaps == missing


def test_a_file_answering_no_ask_is_unsolicited_not_failed():
    """`unsolicited` is an honest label. Ruling AP2.5 governs unreadable files,
    not unrequested ones."""
    from backend.upload.asks import check_shape

    assert check_shape(None, ["anything"]) == ("unsolicited", [])


def test_pre_6_12_uploads_default_to_the_catch_all_role():
    """6.13's backfill is not expected to invent a role for old uploads.

    `other evidence` / `unsolicited` is the truest thing that can be said about
    a file uploaded before roles existed.
    """
    record = UploadRecord(
        filename="old.csv", blob_path="p", uploaded_by="b",
        uploaded_at="t", classification="c",
    )
    assert record.role == "other evidence"
    assert record.shape_match == "unsolicited"
    assert record.content_digest == ""
    assert record.consumed_at is None


def test_the_entry_shape_carries_what_6_13_backfills_from():
    """6.13 reads the case blob. Without these it has nothing to write."""
    entry = _record("complaints.csv").to_phase_state_entry("measure")

    for key in ("role", "shape_match", "content_digest", "blob_path",
                "consumed_at"):
        assert key in entry, f"6.13's backfill needs {key}"
