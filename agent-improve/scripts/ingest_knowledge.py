from __future__ import annotations

import hashlib
import logging
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from langchain_community.vectorstores.azuresearch import AzureSearch

from backend.core.config import settings
from backend.knowledge.retriever import get_knowledge_vectorstore

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).parent.parent / "data" / "knowledge"

# DMAIC phase detection keywords
PHASE_KEYWORDS = {
    "define":        ["define", "5w2h", "charter", "sipoc", "problem statement",
                      "scope", "baseline", "sponsor", "copq"],
    "measure":       ["measure", "data collection", "msa", "gage", "capability",
                      "cpk", "histogram", "baseline data", "sample size"],
    "analyse_phase": ["analyse", "analyze", "root cause", "fishbone", "5why",
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
    "Pareto":                      ("analyse_phase", "Pareto Analysis"),
    "Control chart":               ("control",       "Control Chart"),
    "I-MR Chart":                  ("control",       "I-MR Chart"),
    "Spider chart":                ("improve",       "Spider Chart"),
    "Process capability index":    ("measure",       "Process Capability Cpk"),
    "Correlation and Regression":  ("analyse_phase", "Correlation and Regression"),
    "Value analysis":              ("improve",       "Value Analysis"),
    "Line Balancing":              ("improve",       "Line Balancing"),
    "Box Plot":                    ("analyse_phase", "Box Plot"),
    "Impact & Effort Matrix":      ("improve",       "Impact and Effort Matrix"),
    "5 Why drill down":            ("analyse_phase", "5Why Drill Down"),
    "Cause & Effect Matrix":       ("analyse_phase", "Cause and Effect Matrix"),
    "Normality Test":              ("measure",       "Normality Test"),
    "Fishbone Diagram":            ("analyse_phase", "Fishbone Diagram"),
    "Y2X Matrix":                  ("analyse_phase", "Y2X Matrix"),
    "DPO and Z calculator":        ("control",       "DPO and Z Calculator"),
    "Hoshin Kanri":                ("improve",       "Hoshin Kanri"),
    "MSA Long Method":             ("measure",       "MSA Measurement System Analysis"),
}


def detect_phase(text: str) -> str:
    text_lower = text.lower()
    scores = {phase: 0 for phase in PHASE_KEYWORDS}
    for phase, keywords in PHASE_KEYWORDS.items():
        for kw in keywords:
            if kw in text_lower:
                scores[phase] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "all"


def chunk_text(text: str, chunk_size: int = 800,
               overlap: int = 100) -> list[str]:
    """Split text into overlapping chunks."""
    words = text.split()
    chunks = []
    i = 0
    while i < len(words):
        chunk = " ".join(words[i:i + chunk_size])
        chunks.append(chunk)
        i += chunk_size - overlap
    return chunks


def make_doc_id(source: str, chunk_idx: int) -> str:
    raw = f"{source}_{chunk_idx}"
    return hashlib.md5(raw.encode()).hexdigest()


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
    full_text = ""
    for page in reader.pages:
        full_text += page.extract_text() or ""

    chunks = chunk_text(full_text)
    now = datetime.now(timezone.utc).isoformat()
    docs_added = 0

    for i, chunk in enumerate(chunks):
        if len(chunk.strip()) < 50:
            continue
        phase = detect_phase(chunk)
        doc_id = make_doc_id(filepath.name, i)
        doc = {
            "doc_id": doc_id,
            "title": filepath.stem,
            "section_title": f"{filepath.stem} â chunk {i+1}",
            "content_text": chunk,
            "source": filepath.name,
            "phase": phase,
            "tool_name": "",
            "belt_level": "all",
            "chunk_type": "pdf_chunk",
            "page_start": i,
            "page_end": i,
            "char_count": len(chunk),
            "created_at": now,
        }
        try:
            vectorstore.add_texts(
                texts=[chunk],
                metadatas=[doc],
            )
            docs_added += 1
        except Exception as e:
            logger.warning("Failed to add chunk %d: %s", i, e)

    logger.info("PDF ingested: %d chunks from %s", docs_added, filepath.name)
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
    now = datetime.now(timezone.utc).isoformat()
    docs_added = 0

    with open_workbook(str(filepath)) as wb:
        for sheet_name in wb.sheets:
            if sheet_name == "Content":
                continue
            phase_tool = EXCEL_SHEET_TOOL_MAP.get(sheet_name)
            if phase_tool is None:
                logger.debug("Skipping unmapped sheet: %s", sheet_name)
                continue
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

            doc_id = make_doc_id(f"{filepath.name}_{sheet_name}", 0)
            doc = {
                "id": doc_id,
                "doc_id": doc_id,
                "title": tool_name,
                "section_title": sheet_name,
                "content_text": content[:2000],
                "source": filepath.name,
                "phase": phase,
                "tool_name": tool_name,
                "belt_level": "all",
                "chunk_type": "excel_sheet",
                "page_start": 0,
                "page_end": 0,
                "char_count": len(content),
                "created_at": now,
            }
            try:
                vectorstore.add_texts(
                    texts=[content[:2000]],
                    metadatas=[doc],
                )
                docs_added += 1
                logger.info("  Ingested sheet: %s -> %s (%s)",
                            sheet_name, tool_name, phase)
            except Exception as e:
                logger.warning("Failed sheet %s: %s", sheet_name, e)

    logger.info("Excel ingested: %d sheets from %s",
                docs_added, filepath.name)
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
