"""Upload processing — classify, parse deterministically, interpret once.

Architecture: **§29.1** (the evidence channel), **§6** (the uploads entry
shape), **§23.2** (the index). Procedure step **6.11**. Rulings:
`docs/DECISIONS.md` Part AP2.

THE ORDER IS THE RULING
    Classify → parse deterministically → refuse if unreadable → interpret
    ONCE. Ruling 4 puts the deterministic parse first and confines the model
    to meaning; ruling 5 puts the refusal before the model call, so an
    unreadable file costs nothing and comes back with a reason rather than an
    empty success. Before this step the order was inverted in effect: images
    got a premium vision call, every other format got a stub summary saying
    extraction was "not yet available", and the file was stored anyway.

ONE CALL PER UPLOAD, NOT ONE PER QUESTION
    The interpretation is computed here, at ingest, and persisted on the
    upload record. Nothing downstream re-derives it, which is what bounds the
    cost of the channel to one operational-tier call per file.

WHY THE STRUCTURED RESULT IS PARSED RATHER THAN BOUND
    Both model calls here return JSON and are validated into a Pydantic model
    afterwards. **`with_structured_output` would be the better binding and is
    blocked in this package**: §4.6 scopes the builder-style call to "a plain
    model invocation inside a tool, middleware, or validator", plus the phase
    planner, and `deprecated_patterns.yaml` pattern-2 excludes exactly those
    paths. `backend/upload/**` is a fifth site of the same class and is not on
    the list — the registry's own comment calls this out twice, that "the
    exclusion list simply predated the files". Widening it is a governance
    change and §8 forbids amending a rule in passing during a feature change,
    so this step parses instead and the widening is left to be argued on its
    own. `UploadInterpretation(**payload)` still validates; only the binding
    is weaker.
"""
from __future__ import annotations

import base64
import json
import logging
from datetime import datetime, timezone
from typing import Any

from backend.core.llm import get_llm, block_text
from backend.core.prompts import UPLOAD_INTERPRET_PROMPT, VISION_EXTRACT_PROMPT
from backend.storage.models import UploadInterpretation
from backend.upload.classifier import (
    classify_content_type,
    classify_kind,
    is_image,
)
from backend.upload.parsers import parse_upload

logger = logging.getLogger(__name__)

#: Characters of parsed text shown to the interpretation call. The call is
#: given the measured structure in full and only a window of the contents —
#: it is being asked what the file means, not to read all of it.
INTERPRET_SAMPLE_CHARS = 4_000


def _json_object(text: str) -> dict[str, Any]:
    """The first JSON object in `text`, or `{}`.

    Shared by both model calls in this module so the fence-stripping and
    brace-finding exist once. Returns `{}` rather than raising: every caller
    here has a stated degradation for an unreadable reply, and none of them
    should turn a formatting slip into a lost upload.
    """
    body = (text or "").strip()
    if body.startswith("```"):
        parts = body.split("```")
        if len(parts) > 1:
            body = parts[1]
            if body.startswith("json"):
                body = body[4:]
    body = body.strip()
    start, end = body.find("{"), body.rfind("}") + 1
    if start < 0 or end <= start:
        return {}
    try:
        loaded = json.loads(body[start:end])
    except json.JSONDecodeError:
        return {}
    return loaded if isinstance(loaded, dict) else {}


async def process_upload(
    case_id: str,
    filename: str,
    file_bytes: bytes,
    mime_type: str,
    uploaded_by: str,
    phase: str,
    case_meta: dict,
    purpose: str = "",
    declared_kind: str = "",
) -> dict:
    """Process one uploaded file into an upload record.

    Returns a dict. **`parsed` is the key the caller must check**: `False`
    means the file was refused and `refusal_reason` carries a Belt-readable
    explanation. Nothing is indexed and nothing is persisted for a refusal —
    that decision belongs to the route, and it is ruling 5's whole content.
    """
    content_type = classify_content_type(filename, mime_type)
    kind, kind_declared = classify_kind(purpose, declared_kind)

    if is_image(content_type):
        parsed = await _extract_from_image(file_bytes, case_meta, phase)
    else:
        parsed = parse_upload(filename, file_bytes, content_type)

    base = {
        "filename": filename,
        "content_type": content_type,
        "mime_type": mime_type,
        "kind": kind,
        "kind_declared": kind_declared,
        "phase": phase,
        "uploaded_by": uploaded_by,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "indexed": False,
    }

    if not parsed.get("parsed"):
        logger.info(
            "Upload REFUSED: %s (%s) — %s",
            filename, content_type, parsed.get("refusal_reason"),
        )
        return {
            **base,
            "parsed": False,
            "refusal_reason": parsed.get("refusal_reason"),
        }

    interpretation = await _interpret(filename, parsed, case_meta, phase)

    return {
        **base,
        "parsed": True,
        "refusal_reason": None,
        # ── the deterministic half (ruling 4) ─────────────────────────
        "structure": parsed.get("structure"),
        "columns": parsed.get("columns") or [],
        "row_count": parsed.get("row_count"),
        "column_types": parsed.get("column_types") or {},
        "column_ranges": parsed.get("column_ranges") or {},
        "extracted_text": parsed.get("text") or "",
        # ── image-only structure, kept from the vision call ───────────
        "process_steps": parsed.get("process_steps") or [],
        "metrics_found": parsed.get("metrics_found") or [],
        "sipoc_columns": parsed.get("sipoc_columns"),
        # ── the one model call (ruling 4), with its citation (ruling 6)
        "summary": interpretation.summary,
        "interpretation": interpretation.model_dump(),
    }


async def _interpret(
    filename: str,
    parsed: dict[str, Any],
    case_meta: dict,
    phase: str,
) -> UploadInterpretation:
    """The single meaning call (ruling 4), with its source citation (ruling 6).

    **Operational tier, via the `extraction` role.** Ruling 4's own words are
    that a premium model must not be spent being told a spreadsheet has
    fourteen columns — and this call is not asked to find the columns, it is
    handed them. A new role would need a §56 amendment (`core/llm.py`), and
    `extraction` is the ratified role whose tier and temperature (0.0) match
    what this is.

    **A failed interpretation is not a failed upload.** The deterministic
    parse succeeded, so the file is real and indexable; the summary degrades
    to a stated fallback rather than discarding a file the Belt provided. The
    fallback SAYS that it is one — ruling 5's principle, applied to the half
    of the pipeline that is allowed to fail softly.
    """
    citation = {
        "source_filename": filename,
        # The route owns the blob path and fills it after the upload lands.
        "source_blob_path": "",
    }
    prompt = UPLOAD_INTERPRET_PROMPT.format(
        title=case_meta.get("title", "improvement project"),
        department=case_meta.get("department", "the department"),
        phase=phase,
        what=case_meta.get("what", "process improvement"),
        filename=filename,
        structure=parsed.get("structure") or "unknown",
        columns=", ".join(parsed.get("columns") or []) or "none",
        column_types=json.dumps(parsed.get("column_types") or {}),
        column_ranges=json.dumps(parsed.get("column_ranges") or {}, default=str),
        row_count=parsed.get("row_count"),
        sample=(parsed.get("text") or "")[:INTERPRET_SAMPLE_CHARS],
    )
    try:
        llm = get_llm("extraction")
        result = await llm.ainvoke(prompt)
        payload = _json_object(block_text(result))
        if payload.get("summary"):
            return UploadInterpretation(
                summary=str(payload.get("summary") or ""),
                supports=[str(x) for x in (payload.get("supports") or [])],
                caveats=[str(x) for x in (payload.get("caveats") or [])],
                **citation,
            )
        logger.warning(
            "Upload interpretation returned no summary for %s", filename,
        )
    except Exception as exc:  # noqa: BLE001 — degrade, never drop the upload
        logger.warning("Upload interpretation failed for %s: %s", filename, exc)

    columns = parsed.get("columns") or []
    detail = (
        f" with {len(columns)} columns and {parsed.get('row_count')} rows"
        if columns else ""
    )
    return UploadInterpretation(
        summary=(
            f"'{filename}' was read successfully as a "
            f"{parsed.get('structure') or 'file'}{detail}. An automatic "
            "description of what it shows was not available."
        ),
        caveats=["The automatic description of this file did not run."],
        **citation,
    )


async def _extract_from_image(
    file_bytes: bytes,
    case_meta: dict,
    phase: str,
) -> dict:
    """Vision extraction for images, in `parse_upload`'s return shape.

    **An image is the one format with no deterministic structure to read**, so
    the model call IS the parse here rather than an interpretation on top of
    one. It still returns the same keys as `parsers.py`, including a real
    refusal path — a photograph the model cannot read is refused for the same
    reason a scanned PDF is, rather than stored with an empty extraction and
    then skipped by the indexer without a word.
    """
    b64 = base64.b64encode(file_bytes).decode("utf-8")
    prompt = VISION_EXTRACT_PROMPT.format(
        title=case_meta.get("title", "improvement project"),
        department=case_meta.get("department", "the department"),
        phase=phase,
        what=case_meta.get("what", "process improvement"),
    )
    llm = get_llm("vision", temperature=0.0)
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
    extracted: dict[str, Any] = {}
    try:
        result = await llm.ainvoke([message])
        extracted = _json_object(block_text(result))
    except Exception as e:
        logger.error("Vision extraction failed: %s", e)

    body = (extracted.get("extracted_text") or "").strip()
    if not body:
        return {
            "parsed": False,
            "refusal_reason": (
                "We could not read any text from this image. A clearer photo, "
                "or the original document it was taken from, will work better."
            ),
            "structure": None, "columns": [], "row_count": None,
            "column_types": {}, "column_ranges": {}, "text": "",
        }

    raw_sipoc = extracted.get("sipoc_columns")
    return {
        "parsed": True,
        "refusal_reason": None,
        "structure": extracted.get("document_type") or "image",
        "columns": [],
        "row_count": None,
        "column_types": {},
        "column_ranges": {},
        "text": body,
        "process_steps": extracted.get("process_steps") or [],
        "metrics_found": extracted.get("metrics_found") or [],
        "sipoc_columns": raw_sipoc if raw_sipoc and any(
            v for v in raw_sipoc.values() if v
        ) else None,
    }
