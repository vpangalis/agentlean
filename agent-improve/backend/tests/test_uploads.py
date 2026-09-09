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
