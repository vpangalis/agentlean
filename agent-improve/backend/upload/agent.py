from __future__ import annotations

import base64
import json
import logging
from datetime import datetime, timezone

from backend.core.llm import get_llm
from backend.core.prompts import VISION_EXTRACT_PROMPT
from backend.upload.classifier import classify_content_type, is_image

logger = logging.getLogger(__name__)


def process_upload(
    case_id: str,
    filename: str,
    file_bytes: bytes,
    mime_type: str,
    uploaded_by: str,
    phase: str,
    case_meta: dict,
) -> dict:
    """Process an uploaded file: classify, extract, return upload record.

    Returns dict with keys:
      filename, content_type, mime_type, extracted_text, summary,
      process_steps, metrics_found, sipoc_columns, phase,
      uploaded_by, timestamp, indexed (False until indexing succeeds)
    """
    content_type = classify_content_type(filename, mime_type)
    extracted_text = ""
    summary = ""
    sipoc_columns = None
    process_steps = []
    metrics_found = []

    if is_image(content_type):
        extracted = _extract_from_image(file_bytes, case_meta, phase)
        extracted_text = extracted.get("extracted_text") or ""
        summary = extracted.get("summary") or ""
        process_steps = extracted.get("process_steps") or []
        metrics_found = extracted.get("metrics_found") or []
        raw_sipoc = extracted.get("sipoc_columns")
        if raw_sipoc and any(v for v in raw_sipoc.values() if v):
            sipoc_columns = raw_sipoc

    elif content_type == "text":
        try:
            extracted_text = file_bytes.decode("utf-8", errors="replace")
            summary = extracted_text[:300]
        except Exception as e:
            logger.warning("Text extraction failed for %s: %s", filename, e)

    else:
        summary = (
            f"File '{filename}' uploaded. "
            "Text extraction not yet available for this format."
        )
        logger.info("Non-image upload stored without extraction: %s", filename)

    return {
        "filename": filename,
        "content_type": content_type,
        "mime_type": mime_type,
        "extracted_text": extracted_text,
        "summary": summary,
        "process_steps": process_steps,
        "metrics_found": metrics_found,
        "sipoc_columns": sipoc_columns,
        "phase": phase,
        "uploaded_by": uploaded_by,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "indexed": False,
    }


def _extract_from_image(
    file_bytes: bytes,
    case_meta: dict,
    phase: str,
) -> dict:
    """Call GPT-4o vision to extract text and structure from an image."""
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    prompt = VISION_EXTRACT_PROMPT.format(
        title=case_meta.get("title", "improvement project"),
        department=case_meta.get("department", "the department"),
        phase=phase,
        what=case_meta.get("what", "process improvement"),
    )
    llm = get_llm("operational-premium", temperature=0.0)
    from langchain_core.messages import HumanMessage
    message = HumanMessage(
        content=[
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{b64}",
                    "detail": "high",
                },
            },
            {"type": "text", "text": prompt},
        ]
    )
    try:
        result = llm.invoke([message])
        text = result.content.strip()
        if text.startswith("```"):
            text = text.split("```")[1]
            if text.startswith("json"):
                text = text[4:]
        text = text.strip()
        start = text.find("{")
        end = text.rfind("}") + 1
        if start >= 0 and end > start:
            return json.loads(text[start:end])
    except Exception as e:
        logger.error("Vision extraction failed: %s", e)

    return {
        "document_type": "other",
        "extracted_text": "",
        "process_steps": [],
        "sipoc_columns": None,
        "metrics_found": [],
        "summary": "Image uploaded — automatic extraction failed.",
    }
