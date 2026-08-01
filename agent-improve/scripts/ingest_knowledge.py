"""Ingest DMAIC methodology sources into improve_knowledge_index.

═══════════════════════════════════════════════════════════════════════
HOW A DOCUMENT BECOMES A SEARCHABLE INDEX FIELD  (read before editing)
═══════════════════════════════════════════════════════════════════════

Documents are written through LangChain's `AzureSearch.add_texts`, which
builds each index document as:

    {id, content, content_vector, metadata: json.dumps(<your dict>)}

and then promotes metadata keys to top-level index fields with:

    additional_fields = {k: v for k, v in metadata.items()
                         if k in [x.name for x in self.fields]}

**A metadata key becomes a searchable/filterable field ONLY if its name
exactly matches a field on the index.** Anything else is readable only by
parsing the `metadata` JSON blob, and is invisible to `$filter`.

This is precisely how the original bug arose: the script emitted `phase`,
which is not a field on `improve_knowledge_index`, so `phase_relevance`
was never populated by this script and phase filtering could not work.

The live index has exactly these fields (ARCHITECTURE.md §7.1):

    id  content  content_vector  metadata  source_file  phase_relevance
    page_number

So the metadata dict below is deliberately limited to the three
promotable keys plus `char_count`, which stays in the blob by design —
matching the shape of all 1,369 documents already in the index:

    {"source_file": ..., "page_number": ..., "phase_relevance": ...,
     "char_count": ...}

═══════════════════════════════════════════════════════════════════════
HOW CONTENT MAPS TO A DMAIC PHASE
═══════════════════════════════════════════════════════════════════════

**Per-chunk keyword scoring — NOT chapter or section mapping.**

This was verified against the 1,369 live documents rather than assumed:

  - The BB eBook PDF carries **no outline/bookmarks**, so there is no
    chapter structure to read.
  - DMAIC words do not appear as sustained page headings; they occur
    throughout the text.
  - Every 50-page band of the eBook holds a **mix** of phases. A chapter
    mapping would make each band almost entirely one phase. It does not:

        p100-149  define:28  analyse:25  general:21
        p300-349  analyse:44  general:6   measure:4
        p600-649  measure:39  control:34  improve:9

    The *dominant* phase per band does advance in DMAIC order
    (define → measure → analyse → improve → control), which is why a
    chapter mapping looks plausible at first glance. The book is ordered
    by phase; its content is not partitioned by phase.

So each chunk is scored independently against `PHASE_KEYWORDS`; the
highest-scoring phase wins, and a chunk matching nothing is tagged
`general` — the cross-phase bucket that `rag_lookup_methodology` ORs into
every phase filter (§7.1).

**Re-ingestion reclassifies.** This classifier reproduces ~58% of the
existing `phase_relevance` values exactly. The pipeline that populated
the index originally is not in the repository and cannot be recovered, so
a re-ingest will relabel some chunks. That is acceptable — `general` is
always reachable and the filter ORs it in — but it means re-ingesting is
a content change, not an idempotent no-op. Ingest into a fresh index and
compare before replacing a working one.

Excel toolkit sheets bypass all of this: `EXCEL_SHEET_TOOL_MAP` assigns
each sheet a phase explicitly, which is exact rather than inferred.
"""
from __future__ import annotations

import hashlib
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain_community.vectorstores.azuresearch import AzureSearch

from backend.core.config import settings
from backend.knowledge.retriever import (
    CROSS_PHASE_RELEVANCE,
    get_knowledge_vectorstore,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data" / "knowledge"

# Chunking: one chunk per page, split further only when a page is long.
# Keeps page_number truthful — it is a citation field (§13), so a chunk
# spanning pages could not be cited honestly.
CHUNK_CHARS = 1200
CHUNK_OVERLAP_CHARS = 150
MIN_CHUNK_CHARS = 50

# Filename -> the `source_file` label stored on the index. The live values
# are short stable labels, not filenames: filenames carry version suffixes
# and spaces that would churn the citation string on every re-issue of a
# source document.
SOURCE_FILE_LABELS = {
    "5_BB_EB_MT_v11.1_PDF2_compressed (1).pdf": "BB_LSS_ebook",
    "Problem Solving 8D.pdf":                    "problem_solving_8D",
    "Lean-Six-Sigma Tools suite_20220912.xlsb":  "LSS_tools_suite",
}

# DMAIC phase detection keywords
PHASE_KEYWORDS = {
    "define":        ["define", "5w2h", "charter", "sipoc", "problem statement",
                      "scope", "baseline", "sponsor", "copq"],
    "measure":       ["measure", "data collection", "msa", "gage", "capability",
                      "cpk", "histogram", "baseline data", "sample size"],
    "analyse":       ["analyse", "analyze", "root cause", "fishbone", "5why",
                      "pareto", "regression", "hypothesis", "correlation"],
    "improve":       ["improve", "solution", "pilot", "impact", "effort",
                      "hoshin", "line balancing", "value analysis"],
    "control":       ["control", "control chart", "i-mr", "spc", "monitoring",
                      "handover", "sustain", "dpo", "z score"],
}

# Excel sheet to tool name mapping (from LeanSixSigma_Tools_suite)
EXCEL_SHEET_TOOL_MAP = {
    "5W2H - Problem Statement":    ("define",        "5W2H"),
    "Data Collection plan":        ("measure",       "Data Collection Plan"),
    "Histogram":                   ("measure",       "Histogram"),
    "Pareto":                      ("analyse",       "Pareto Analysis"),
    "Control chart":               ("control",       "Control Chart"),
    "I-MR Chart":                  ("control",       "I-MR Chart"),
    "Spider chart":                ("improve",       "Spider Chart"),
    "Process capability index":    ("measure",       "Process Capability Cpk"),
    "Correlation and Regression":  ("analyse",       "Correlation and Regression"),
    "Value analysis":              ("improve",       "Value Analysis"),
    "Line Balancing":              ("improve",       "Line Balancing"),
    "Box Plot":                    ("analyse",       "Box Plot"),
    "Impact & Effort Matrix":      ("improve",       "Impact and Effort Matrix"),
    "5 Why drill down":            ("analyse",       "5Why Drill Down"),
    "Cause & Effect Matrix":       ("analyse",       "Cause and Effect Matrix"),
    "Normality Test":              ("measure",       "Normality Test"),
    "Fishbone Diagram":            ("analyse",       "Fishbone Diagram"),
    "Y2X Matrix":                  ("analyse",       "Y2X Matrix"),
    "DPO and Z calculator":        ("control",       "DPO and Z Calculator"),
    "Hoshin Kanri":                ("improve",       "Hoshin Kanri"),
    "MSA Long Method":             ("measure",       "MSA Measurement System Analysis"),
}


def detect_phase(text: str) -> str:
    """Score a chunk against PHASE_KEYWORDS; highest count wins.

    Returns CROSS_PHASE_RELEVANCE ('general') when nothing matches. That
    sentinel is NOT free-form: `rag_lookup_methodology` ORs exactly this
    value into every phase filter, so a chunk tagged anything else that
    means "applies broadly" becomes unreachable from every phase.
    """
    text_lower = text.lower()
    scores = {phase: 0 for phase in PHASE_KEYWORDS}
    for phase, keywords in PHASE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[phase] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else CROSS_PHASE_RELEVANCE


def source_label(filename: str) -> str:
    """Stable `source_file` label for a source document.

    Falls back to the stem so an unmapped file still ingests, but warns —
    an unmapped label silently fragments citations across re-issues.
    """
    label = SOURCE_FILE_LABELS.get(filename)
    if label is None:
        label = Path(filename).stem
        logger.warning(
            "No SOURCE_FILE_LABELS entry for %r — falling back to %r. Add a "
            "mapping to keep citations stable across document re-issues.",
            filename, label,
        )
    return label


def chunk_text(text: str, chunk_size: int = CHUNK_CHARS,
               overlap: int = CHUNK_OVERLAP_CHARS) -> list[str]:
    """Split one page's text into overlapping character chunks."""
    text = text.strip()
    if not text:
        return []
    if len(text) <= chunk_size:
        return [text]
    chunks = []
    i = 0
    step = chunk_size - overlap
    while i < len(text):
        chunks.append(text[i:i + chunk_size])
        i += step
    return chunks


def make_doc_id(source_file: str, page_number: int, chunk_idx: int) -> str:
    """Deterministic document key.

    Deterministic on purpose: Azure Search upserts on key, so re-ingesting
    the same source replaces its documents instead of duplicating them.
    LangChain generates a random UUID key when none is supplied, which is
    why the key must be passed explicitly via `ids=`.
    """
    raw = f"{source_file}_{page_number}_{chunk_idx}"
    return hashlib.md5(raw.encode()).hexdigest()


def build_metadata(source_file: str, page_number: int, content: str,
                   phase_relevance: str) -> dict:
    """Metadata dict for one chunk.

    Key names are the contract: `source_file`, `page_number`, and
    `phase_relevance` match index fields and are promoted to top-level
    searchable/filterable fields. `char_count` has no matching field and
    stays inside the JSON blob — that asymmetry is intentional and mirrors
    the 1,369 documents already in the index. Renaming any of the first
    three silently demotes it to blob-only. See the module docstring.
    """
    return {
        "source_file": source_file,
        "page_number": page_number,
        "phase_relevance": phase_relevance,
        "char_count": len(content),
    }


def ingest_pdf(filepath: Path, vectorstore: AzureSearch,
               search_client: SearchClient) -> int:
    """Ingest a PDF file into the knowledge index."""
    try:
        from PyPDF2 import PdfReader
    except ImportError:
        try:
            from pypdf import PdfReader
        except ImportError:
            logger.error("No PDF library found â pip install pypdf")
            return 0

    logger.info("Ingesting PDF: %s", filepath.name)
    reader = PdfReader(str(filepath))
    source_file = source_label(filepath.name)
    docs_added = 0

    # Chunk PER PAGE, never across pages. page_number is a citation field
    # (§13, "this came from page 47 of the BB eBook"); a chunk spanning a
    # page boundary could not carry an honest page number.
    for page_number, page in enumerate(reader.pages, start=1):
        page_text = page.extract_text() or ""
        for chunk_idx, chunk in enumerate(chunk_text(page_text)):
            if len(chunk.strip()) < MIN_CHUNK_CHARS:
                continue
            metadata = build_metadata(
                source_file=source_file,
                page_number=page_number,
                content=chunk,
                phase_relevance=detect_phase(chunk),
            )
            try:
                vectorstore.add_texts(
                    texts=[chunk],
                    metadatas=[metadata],
                    ids=[make_doc_id(source_file, page_number, chunk_idx)],
                )
                docs_added += 1
            except Exception as e:
                logger.warning(
                    "Failed to add %s p%d chunk %d: %s",
                    source_file, page_number, chunk_idx, e,
                )

    logger.info("PDF ingested: %d chunks from %s (%d pages)",
                docs_added, source_file, len(reader.pages))
    return docs_added


def ingest_excel(filepath: Path, vectorstore: AzureSearch,
                 search_client: SearchClient) -> int:
    """Ingest Excel toolkit sheets into knowledge index."""
    try:
        from pyxlsb import open_workbook
    except ImportError:
        logger.error("pyxlsb not installed â pip install pyxlsb")
        return 0

    logger.info("Ingesting Excel toolkit: %s", filepath.name)
    source_file = source_label(filepath.name)
    docs_added = 0

    with open_workbook(str(filepath)) as wb:
        for sheet_idx, sheet_name in enumerate(wb.sheets, start=1):
            if sheet_name == "Content":
                continue
            phase_tool = EXCEL_SHEET_TOOL_MAP.get(sheet_name)
            if phase_tool is None:
                logger.debug("Skipping unmapped sheet: %s", sheet_name)
                continue
            # Excel phases are EXPLICIT, not inferred — one row per sheet in
            # EXCEL_SHEET_TOOL_MAP. detect_phase() is deliberately not used.
            phase, tool_name = phase_tool

            # Extract cell text from sheet
            rows_text = []
            with wb.get_sheet(sheet_name) as sheet:
                for row in sheet.rows():
                    vals = [str(c.v) for c in row
                            if c.v is not None and str(c.v).strip()]
                    if vals:
                        rows_text.append(" | ".join(vals[:10]))

            if not rows_text:
                continue

            content = f"Tool: {tool_name}\nPhase: {phase}\n\n"
            content += "\n".join(rows_text[:100])
            content = content[:2000]

            # A workbook has no pages; the sheet ordinal stands in for
            # page_number so a citation can name the sheet position.
            metadata = build_metadata(
                source_file=source_file,
                page_number=sheet_idx,
                content=content,
                phase_relevance=phase,
            )
            try:
                vectorstore.add_texts(
                    texts=[content],
                    metadatas=[metadata],
                    ids=[make_doc_id(source_file, sheet_idx, 0)],
                )
                docs_added += 1
                logger.info("  Ingested sheet: %s -> %s (%s)",
                            sheet_name, tool_name, phase)
            except Exception as e:
                logger.warning("Failed sheet %s: %s", sheet_name, e)

    logger.info("Excel ingested: %d sheets from %s",
                docs_added, source_file)
    return docs_added


def get_search_client() -> SearchClient:
    return SearchClient(
        endpoint=settings.AZURE_SEARCH_ENDPOINT,
        index_name=settings.AZURE_SEARCH_IMPROVE_KNOWLEDGE_INDEX,
        credential=AzureKeyCredential(settings.AZURE_SEARCH_API_KEY),
    )


if __name__ == "__main__":
    if not DATA_DIR.exists():
        logger.error(
            "Data directory not found: %s\n"
            "Create it and place your PDF and .xlsb files there.",
            DATA_DIR
        )
        sys.exit(1)

    vs = get_knowledge_vectorstore()
    sc = get_search_client()
    total = 0

    for f in DATA_DIR.iterdir():
        if f.suffix.lower() == ".pdf":
            total += ingest_pdf(f, vs, sc)
        elif f.suffix.lower() == ".xlsb":
            total += ingest_excel(f, vs, sc)
        else:
            logger.debug("Skipping: %s", f.name)

    logger.info("Ingestion complete â %d documents added", total)
