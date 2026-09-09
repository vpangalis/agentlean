"""Deterministic extraction for the four formats a Belt actually uploads.

Architecture: **§29.1** (the evidence channel), **§23.2** (the index),
**§65.4 S-F35** (the upload handler). Procedure step **6.11**. Rulings:
`docs/DECISIONS.md` Part AP2.

RULING 4 — PARSE IS DETERMINISTIC FIRST
    Columns, row count, types and ranges come from the file. **Only meaning
    costs a model call, once, at ingest.** Nothing in this module calls an
    LLM, imports one, or knows one exists. A premium model must never be
    spent being told a spreadsheet has fourteen columns, and the facts this
    module returns are the ones the interpretation call is *given* rather
    than asked to invent.

RULING 5 — REFUSED OR REPORTED, NEVER SILENTLY ACCEPTED
    Every function here returns a dict carrying `parsed: bool`. A file this
    module cannot read comes back `parsed=False` with a Belt-readable
    `refusal_reason`, and the route turns that into a 422 the Belt can act on.
    **It never returns an empty success.** Before this step, four formats were
    accepted and dropped and two of them reported as supported — a Belt could
    upload a spreadsheet, see it stored, and have it be invisible to the coach
    and absent from the index, with no error anywhere (Part AP1).

NO CLASSES (`CLAUDE.md` §2)
    `backend/upload/` is not on §2's permitted-class list, so everything here
    is a module-level function returning a plain dict. The refusal path is a
    dict field rather than an exception for the same reason — and because a
    refusal is an ordinary, expected outcome of this module, not an error.
"""
from __future__ import annotations

import csv
import io
import logging
import re
from datetime import date, datetime
from typing import Any

logger = logging.getLogger(__name__)

#: Rows read for type and range inference. The whole file is counted, but only
#: this many are typed — a 200k-row export should not cost 200k date parses to
#: answer "is this column a date". The sample is the HEAD, deliberately: a
#: Belt's export is ordered, and a trailing totals row is exactly the value
#: that should not define the column's type.
TYPE_SAMPLE_ROWS = 500

#: Distinct values kept for a text column, so `column_ranges` can show a Belt
#: what is actually in it without carrying the whole column.
MAX_DISTINCT_SAMPLE = 12

#: Characters of extracted text handed onward for indexing and interpretation.
#: Well above a coaching turn's need and well below an embedding call's limit.
MAX_TEXT_CHARS = 20_000

#: Types that share one range. See `_column_profile` for why `percentage` is
#: not among them.
NUMERIC_TYPES = frozenset({"whole number", "decimal"})

_INT_RE = re.compile(r"^[+-]?\d+$")
_DEC_RE = re.compile(r"^[+-]?(\d+\.\d*|\.\d+|\d+)$")
_PCT_RE = re.compile(r"^[+-]?\d+(\.\d+)?\s*%$")

_DATE_FORMATS = (
    "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%d-%m-%Y",
    "%Y/%m/%d", "%d %b %Y", "%d %B %Y", "%Y-%m-%d %H:%M:%S",
)


def refusal(reason: str) -> dict[str, Any]:
    """The one shape a Belt-readable refusal takes (ruling 5).

    Written as a helper rather than repeated so that every refusal in this
    module is the same shape — a caller checks `parsed` and nothing else.
    """
    return {
        "parsed": False,
        "refusal_reason": reason,
        "structure": None,
        "columns": [],
        "row_count": None,
        "column_types": {},
        "column_ranges": {},
        "text": "",
    }


def _parsed(
    structure: str,
    text: str,
    columns: list[str] | None = None,
    row_count: int | None = None,
    column_types: dict[str, str] | None = None,
    column_ranges: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """The success shape. Mirrors `refusal()` key for key, on purpose."""
    return {
        "parsed": True,
        "refusal_reason": None,
        "structure": structure,
        "columns": columns or [],
        "row_count": row_count,
        "column_types": column_types or {},
        "column_ranges": column_ranges or {},
        "text": text[:MAX_TEXT_CHARS],
    }


# ─────────────────────────────────────────────────────────────────────────
# Type and range inference — the deterministic half of "what is in this file"
# ─────────────────────────────────────────────────────────────────────────

def _coerce(value: Any) -> tuple[str, Any]:
    """Classify one cell into (type_label, comparable_value).

    Type labels are Belt-readable on purpose: they appear in the coaching
    turn that asks about the file, and `CLAUDE.md`'s plain-language rule
    applies to anything the Belt can see.
    """
    if value is None:
        return "empty", None
    if isinstance(value, bool):
        return "true/false", value
    if isinstance(value, (datetime, date)):
        return "date", value
    if isinstance(value, int):
        return "whole number", value
    if isinstance(value, float):
        return "decimal", value

    text = str(value).strip()
    if not text:
        return "empty", None
    if _INT_RE.match(text):
        return "whole number", int(text)
    if _PCT_RE.match(text):
        return "percentage", float(text.rstrip("% ").strip())
    if _DEC_RE.match(text) and "." in text:
        return "decimal", float(text)
    for fmt in _DATE_FORMATS:
        try:
            return "date", datetime.strptime(text, fmt)
        except ValueError:
            continue
    return "text", text


def _column_profile(values: list[Any]) -> tuple[str, dict[str, Any]]:
    """One column's type and range, from its sampled values.

    **The type is the dominant non-empty type, and the range is reported only
    when the column is uniform.** A column that is 90% dates and 10% free text
    is reported as `date` with a `mixed` note rather than silently as either —
    a mixed column is the single most common reason a Belt's export cannot be
    computed on, and it is worth a coaching question rather than a guess.
    """
    counts: dict[str, int] = {}
    typed: dict[str, list[Any]] = {}
    for raw in values:
        label, comparable = _coerce(raw)
        counts[label] = counts.get(label, 0) + 1
        if label != "empty":
            typed.setdefault(label, []).append(comparable)

    non_empty = {k: v for k, v in counts.items() if k != "empty"}
    if not non_empty:
        return "empty", {"empty": len(values)}

    dominant = max(non_empty, key=lambda k: non_empty[k])

    # **`whole number` and `decimal` are ONE column, not two.** Excel stores
    # 63.0 as 63, so a column of 41.5 / 63.0 / 55.25 comes back as two
    # decimals and one integer — and treating those as different types put
    # the largest value outside the reported range and into `mixed`. A
    # min/max that silently excludes the round numbers is worse than no
    # min/max: it is wrong in the direction of looking right. `percentage`
    # is deliberately NOT in the family — "50%" beside "0.5" is a real
    # ambiguity about units and is worth surfacing.
    family = {dominant}
    if dominant in NUMERIC_TYPES:
        family = {t for t in non_empty if t in NUMERIC_TYPES}
        # Label by the widest member present, not the most frequent: a column
        # holding any decimal is a decimal column for anything that computes
        # on it, whatever the majority looks like.
        dominant = "decimal" if "decimal" in family else dominant

    sample = [v for t in family for v in typed[t]]
    profile: dict[str, Any] = {
        "count": len(values),
        "empty": counts.get("empty", 0),
    }
    outside = {k: v for k, v in non_empty.items() if k not in family}
    if outside:
        profile["mixed"] = outside

    if dominant in NUMERIC_TYPES or dominant == "percentage":
        profile["min"] = min(sample)
        profile["max"] = max(sample)
    elif dominant == "date":
        profile["min"] = min(sample).isoformat()
        profile["max"] = max(sample).isoformat()
    else:
        distinct = list(dict.fromkeys(str(v) for v in sample))
        profile["distinct"] = len(distinct)
        profile["examples"] = distinct[:MAX_DISTINCT_SAMPLE]

    return dominant, profile


def _profile_table(
    header: list[str], rows: list[list[Any]]
) -> tuple[dict[str, str], dict[str, Any]]:
    """Types and ranges for every column of a parsed table."""
    types: dict[str, str] = {}
    ranges: dict[str, Any] = {}
    for i, name in enumerate(header):
        column = [r[i] if i < len(r) else None for r in rows[:TYPE_SAMPLE_ROWS]]
        types[name], ranges[name] = _column_profile(column)
    return types, ranges


def _table_text(header: list[str], rows: list[list[Any]], limit: int = 200) -> str:
    """Indexable text for a table.

    **A table is rendered as labelled lines, not as a CSV dump.** The index is
    searched by embedding similarity, and `2026-01-04,17,late delivery` embeds
    close to nothing a Belt would type; `date: 2026-01-04 | count: 17 | reason:
    late delivery` carries the column names into the vector, which is what a
    question like "what reasons are in the complaints data" actually matches.
    """
    lines = [" | ".join(str(h) for h in header)]
    for row in rows[:limit]:
        lines.append(
            " | ".join(
                f"{header[i]}: {row[i]}"
                for i in range(min(len(header), len(row)))
                if row[i] is not None and str(row[i]).strip()
            )
        )
    return "\n".join(lines)


# ─────────────────────────────────────────────────────────────────────────
# Per-format parsers
# ─────────────────────────────────────────────────────────────────────────

def parse_csv(file_bytes: bytes) -> dict[str, Any]:
    """CSV, with the delimiter sniffed and the encoding tried in order."""
    text = ""
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = file_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    if not text.strip():
        return refusal(
            "This CSV appears to be empty, or is saved in a text encoding we "
            "could not read. Re-saving it as UTF-8 CSV from your spreadsheet "
            "tool usually fixes it."
        )

    sample = text[:8192]
    try:
        dialect: Any = csv.Sniffer().sniff(sample, delimiters=",;\t|")
    except csv.Error:
        dialect = csv.excel

    reader = csv.reader(io.StringIO(text), dialect)
    all_rows = [r for r in reader if any(str(c).strip() for c in r)]
    if not all_rows:
        return refusal("This CSV has no rows with any content in them.")

    header = [str(h).strip() or f"column {i + 1}"
              for i, h in enumerate(all_rows[0])]
    rows = all_rows[1:]
    if not rows:
        return refusal(
            "This CSV has a header row and no data rows, so there is nothing "
            "to measure yet."
        )

    types, ranges = _profile_table(header, rows)
    return _parsed("table", _table_text(header, rows),
                   header, len(rows), types, ranges)


def parse_xlsx(file_bytes: bytes) -> dict[str, Any]:
    """XLSX, first worksheet with content.

    `read_only=True` and `data_only=True`: the second is load-bearing — without
    it a formula cell yields `=SUM(B2:B57)` as a string, which types as `text`
    and makes a numeric column unreadable.
    """
    try:
        from openpyxl import load_workbook
        workbook = load_workbook(
            io.BytesIO(file_bytes), read_only=True, data_only=True
        )
    except Exception as exc:  # noqa: BLE001 — any openpyxl failure is a refusal
        logger.info("xlsx parse failed: %s", exc)
        return refusal(
            "We could not open this spreadsheet. If it is an older .xls file, "
            "re-saving it as .xlsx will let us read it."
        )

    try:
        for sheet in workbook.worksheets:
            all_rows = [
                list(r) for r in sheet.iter_rows(values_only=True)
                if r is not None and any(
                    c is not None and str(c).strip() for c in r
                )
            ]
            if len(all_rows) < 2:
                continue
            header = [
                str(h).strip() if h is not None and str(h).strip()
                else f"column {i + 1}"
                for i, h in enumerate(all_rows[0])
            ]
            rows = all_rows[1:]
            types, ranges = _profile_table(header, rows)
            return _parsed("table", _table_text(header, rows),
                           header, len(rows), types, ranges)
    finally:
        workbook.close()

    return refusal(
        "This spreadsheet has no sheet with a header row and at least one row "
        "of data in it."
    )


def parse_pdf(file_bytes: bytes) -> dict[str, Any]:
    """PDF — tables first, then text.

    **A table inside a PDF is still a table**, and the Belt who exported a
    report to PDF should not lose its columns because of the container. Tables
    are tried first; a PDF with none falls back to text, and one with neither
    is refused rather than indexed as an empty string.
    """
    try:
        import pdfplumber
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            tables = []
            for page in pdf.pages:
                tables.extend(page.extract_tables() or [])
            text_parts = [p.extract_text() or "" for p in pdf.pages]
            page_count = len(pdf.pages)
    except Exception as exc:  # noqa: BLE001
        logger.info("pdf parse failed: %s", exc)
        return refusal(
            "We could not read this PDF. If it is password-protected, please "
            "remove the protection and upload it again."
        )

    widest = max(tables, key=len) if tables else None
    if widest and len(widest) >= 2:
        header = [
            str(h).strip() if h is not None and str(h).strip()
            else f"column {i + 1}"
            for i, h in enumerate(widest[0])
        ]
        rows = [list(r) for r in widest[1:]]
        types, ranges = _profile_table(header, rows)
        return _parsed("table", _table_text(header, rows),
                       header, len(rows), types, ranges)

    text = "\n".join(t for t in text_parts if t.strip())
    if not text.strip():
        return refusal(
            f"This PDF has {page_count} page(s) but no text we can read — it is "
            "most likely a scan or a photograph. Uploading the original "
            "spreadsheet or document, or a photo of it as an image file, will "
            "let us read the contents."
        )
    return _parsed("prose", text, row_count=page_count)


def parse_docx(file_bytes: bytes) -> dict[str, Any]:
    """DOCX — tables first, then paragraphs. Same precedence as PDF."""
    try:
        import docx
        document = docx.Document(io.BytesIO(file_bytes))
    except Exception as exc:  # noqa: BLE001
        logger.info("docx parse failed: %s", exc)
        return refusal(
            "We could not open this Word document. If it is an older .doc "
            "file, re-saving it as .docx will let us read it."
        )

    for table in document.tables:
        grid = [[cell.text.strip() for cell in row.cells] for row in table.rows]
        grid = [r for r in grid if any(r)]
        if len(grid) >= 2:
            header = [h or f"column {i + 1}" for i, h in enumerate(grid[0])]
            rows: list[list[Any]] = [list(r) for r in grid[1:]]
            types, ranges = _profile_table(header, rows)
            return _parsed("table", _table_text(header, rows),
                           header, len(rows), types, ranges)

    paragraphs = [p.text.strip() for p in document.paragraphs if p.text.strip()]
    if not paragraphs:
        return refusal(
            "This Word document has no text and no tables we can read."
        )
    return _parsed("prose", "\n".join(paragraphs), row_count=len(paragraphs))


def parse_text(file_bytes: bytes) -> dict[str, Any]:
    """Plain text. Kept as its own parser so `.txt` has a real refusal path."""
    for encoding in ("utf-8-sig", "utf-8", "cp1252", "latin-1"):
        try:
            text = file_bytes.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        return refusal("We could not read the text encoding of this file.")

    if not text.strip():
        return refusal("This file is empty.")
    return _parsed("prose", text, row_count=len(text.splitlines()))


#: content_type (from `classify_content_type`) → its deterministic parser.
#: **Membership here is what `is_supported` means.** One table, so a format
#: cannot report as supported while having no parser — which is exactly the
#: state pdf and docx were in before this step (Part AP1).
PARSERS = {
    "spreadsheet": None,   # resolved by extension below — csv and xlsx differ
    "pdf": parse_pdf,
    "document": parse_docx,
    "text": parse_text,
}


def parse_upload(
    filename: str, file_bytes: bytes, content_type: str
) -> dict[str, Any]:
    """Deterministic parse for one upload. **Never calls a model** (ruling 4).

    Returns the `parsed=True` shape or a `parsed=False` refusal — the caller
    checks that one key. `image` is not handled here: an image has no
    deterministic structure to read, and its extraction is the vision call in
    `upload/agent.py`, which is the one model call this path is allowed.
    """
    if not file_bytes:
        return refusal("The uploaded file is empty (0 bytes).")

    name = (filename or "").lower()
    if content_type == "spreadsheet":
        return parse_csv(file_bytes) if name.endswith(".csv") \
            else parse_xlsx(file_bytes)

    parser = PARSERS.get(content_type)
    if parser is None:
        return refusal(
            f"We cannot read '{filename}' yet. Spreadsheets (.xlsx, .csv), "
            "PDFs, Word documents, plain text and images are supported."
        )
    return parser(file_bytes)
