"""Upload processing — classify, parse deterministically, interpret once.

THE ORDER IS THE RULE
    Classify → parse deterministically → refuse if unreadable → interpret
    ONCE. The deterministic parse comes first and the model is confined to
    meaning; the refusal comes before the model call, so an unreadable file
    costs nothing and comes back with a reason rather than an empty success.

ONE CALL PER UPLOAD, NOT ONE PER QUESTION
    The interpretation is computed here, at ingest, and persisted on the
    upload record. Nothing downstream re-derives it, which is what bounds the
    cost of the channel to one operational-tier call per file.

BOTH CALLS BIND STRUCTURED OUTPUT (ADR-0104)
    The interpretation binds `with_structured_output(UploadInterpretation)` and the image read
    `with_structured_output(ImageRead)` — its five typed fields. The builder-style call is for a
    plain model invocation; the drift registry's pattern 2 excludes exactly this file. Nothing is
    parsed out of the model's text, so an unreadable reply cannot be lost silently as an empty
    JSON object: it fails the call and takes the stated fallback.
"""
from __future__ import annotations

import base64
import json
import logging
from datetime import datetime, timezone
from typing import Any

from backend.core import content_safety, guard_messages, pii
from backend.upload import parsers
from backend.core.llm import UPLOAD_TIMEOUT, get_llm
from langchain_core.messages import HumanMessage, SystemMessage

from backend.core.prompts import (UPLOAD_ELEMENT_CHECK, UPLOAD_INTERPRET_DATA, UPLOAD_INTERPRET_SYSTEM,
                                  VISION_EXTRACT_PROMPT)
from backend.storage.models import ElementCheck, ImageRead, UploadInterpretation
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
    element: str | None = None,
) -> dict:
    """Process one uploaded file into an upload record.

    Returns a dict. **`parsed` is the key the caller must check**: `False`
    means the file was refused and `refusal_reason` carries a Belt-readable
    explanation. Nothing is indexed and nothing is persisted for a refusal —
    that decision belongs to the route.
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

    # T72 (ADR-0067): the WHOLE text — what a reader sees and what formatting, comments, hidden
    # cells or sheets and the file's properties hide — is screened BEFORE any model reads it.
    # Unreachable (or not configured in strict mode): refused, nothing written (fail closed).
    # An attack: the file is kept in the case, marked not used, and never interpreted.
    screened = (parsed.get("text") or "") + "\n" + parsers.hidden_text(filename, file_bytes, content_type)
    outcome = await _screen(screened)
    if outcome == "unavailable":
        logger.warning("Upload REFUSED: the document check is unavailable — %s", filename)
        return {**base, "parsed": False, "refusal_reason": guard_messages.UPLOAD_UNAVAILABLE}
    if outcome == "attack":
        logger.warning("Upload FLAGGED by the document check: %s — kept, not used by the coach", filename)
        return {**base, "parsed": True, "used_by_coach": False,
                "not_used_reason": guard_messages.B.format(filename=filename),
                "structure": parsed.get("structure"), "columns": parsed.get("columns") or [],
                "row_count": parsed.get("row_count"), "extracted_text": "", "summary": "",
                "interpretation": None}

    # T87 / ADR-0062 (DEF-144): e-mail, phone, IBAN and card numbers are redacted in the text a
    # model interprets and the index embeds; the file itself stays in Blob for the Belt. Names stay.
    masked_text, pii_masked = pii.mask(parsed.get("text") or "")
    parsed = {**parsed, "text": masked_text}
    interpretation = await _interpret(filename, parsed, case_meta, phase, element)
    interpretation = _table_value(interpretation, parsed, phase, element)

    return {
        **base,
        "parsed": True,
        "refusal_reason": None,
        # ── the deterministic half ────────────────────────────────────
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
        # ── the one model call, with its source citation ──────────────
        "summary": interpretation.summary,
        "interpretation": interpretation.model_dump(),
        # T87 — the count per type, never the value; the route writes it to step_log.
        "pii_masked": pii_masked,
    }


async def _screen(text: str) -> str:
    """Prompt Shields' document check over the WHOLE text, one call per 10,000 characters (its
    limit per call, ADR-0067). Returns "attack", "unavailable" or "" (clean, or skipped in
    explicit development mode without the service — T94)."""
    if not text.strip():
        return ""
    step = content_safety.MAX_CHARS
    for i in range(0, len(text), step):
        verdict = await content_safety.shield(documents=[text[i:i + step]])
        if not verdict["configured"]:
            return "" if content_safety.development_mode() else "unavailable"
        if not verdict["reachable"]:
            return "unavailable"
        if any(verdict["document_attacks"]):
            return "attack"
    return ""


async def _interpret(
    filename: str,
    parsed: dict[str, Any],
    case_meta: dict,
    phase: str,
    element: str | None = None,
) -> UploadInterpretation:
    """The single meaning call, with its source citation.

    **Operational tier, via the `extraction` role.** A premium model must not
    be spent being told a spreadsheet has fourteen columns — and this call is
    not asked to find the columns, it is handed them. A new role would need an
    amendment (`core/llm.py`), and `extraction` is the ratified role whose tier
    and temperature (0.0) match what this is.

    **A failed interpretation is not a failed upload.** The deterministic
    parse succeeded, so the file is real and indexable; the summary degrades
    to a stated fallback rather than discarding a file the Belt provided. The
    fallback SAYS that it is one — the refusal principle, applied to the half
    of the pipeline that is allowed to fail softly.
    """
    citation = {
        "source_filename": filename,
        # The route owns the blob path and fills it after the upload lands.
        "source_blob_path": "",
    }
    data = UPLOAD_INTERPRET_DATA.format(
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
    # ADR-0074 (DEF-108, W5): the current element's acceptance criteria, judged in this same call —
    # in the system message beside the other instructions (ADR-0067), never in the data block.
    from backend.middleware.skills import acceptance_criteria
    criteria = acceptance_criteria(phase, element) if element else []
    system = [{"type": "text", "text": UPLOAD_INTERPRET_SYSTEM}]
    if criteria:
        system.append({"type": "text", "text": UPLOAD_ELEMENT_CHECK.format(
            element=guard_messages.element_name(phase, str(element)), field=element,
            criteria="\n".join(f"- {cid}: {text}" for cid, text in criteria))})
    try:
        llm = get_llm("extraction", timeout=UPLOAD_TIMEOUT).with_structured_output(UploadInterpretation)
        # G-143: the instructions are the system message, the file only the user message (in T72's
        # labelled block) — as one user message the deployment's jailbreak filter refuses it.
        instructions = (SystemMessage(content_blocks=system) if len(system) > 1  # type: ignore[arg-type]
                        else SystemMessage(content=UPLOAD_INTERPRET_SYSTEM))
        result = await llm.ainvoke([instructions, HumanMessage(content=data)])
        if isinstance(result, UploadInterpretation) and result.summary.strip():
            check = result.element_check.model_dump() if result.element_check else None
            return UploadInterpretation(
                summary=result.summary, supports=result.supports, caveats=result.caveats,
                element_check=_element_check(check, str(element or ""), [cid for cid, _ in criteria]),
                **citation,
            )
        logger.warning(
            "Upload interpretation returned no summary for %s", filename,
        )
    except Exception as exc:  # noqa: BLE001 — degrade, never drop the upload
        logger.warning("Upload interpretation failed for %s: %s", filename, exc)

    return _interpretation_unavailable(filename, parsed, citation)


def _table_value(interpretation: UploadInterpretation, parsed: dict[str, Any], phase: str,
                 element: Any) -> UploadInterpretation:
    """G-236 (DEF-229): for a table file and a list element (the team), the value a read-back shows is the
    file's own rows as the parser labelled them — every column, written in code — not the model's copy, which
    can drop a column. The model still judges whether the file answers the element (an empty
    value stays empty) and each criterion."""
    from backend.phases.define import parse as define_parse
    check = interpretation.element_check
    lines = define_parse.table_lines(parsed.get("text"))
    if (phase != "define" or element not in define_parse.TABLE_ELEMENTS or parsed.get("structure") != "table"
            or check is None or not check.value.strip() or not define_parse.team_rows(lines)):
        return interpretation
    return interpretation.model_copy(update={"element_check": check.model_copy(update={"value": lines})})


def _element_check(raw: Any, element: str, ids: list[str]) -> ElementCheck | None:
    """ADR-0074 — the model's `element_check`, kept only for the element it was asked about and only
    with the criterion ids that element has. Malformed or absent: None, and the upload stands."""
    if not ids or not isinstance(raw, dict):
        return None
    try:
        check = ElementCheck.model_validate({**raw, "element": element})
    except ValueError as exc:
        logger.warning("Upload element check malformed for %s: %s", element, exc)
        return None
    kept = [c for c in check.criteria if c.criterion in ids]
    return check.model_copy(update={"criteria": kept}) if kept else None


def _interpretation_unavailable(
    filename: str,
    parsed: dict[str, Any],
    citation: dict[str, str],
) -> UploadInterpretation:
    """The fallback, and it SAYS it is one.

    **A fallback that reads like a summary would hide a dead interpretation
    path**: a fluent sentence about the file's shape would leave nothing — not
    the Belt, not the gate document, not the test suite — able to tell that
    the meaning call had produced no meaning.

    **The refusal principle one level down.** An unextractable FILE is refused
    outright; an uninterpreted file is real, parsed and indexable, so it is
    kept — but it is *reported*, never passed off as interpreted. The marker
    follows the `phase_context` convention: a WARNING for whoever reads logs,
    and `[!] … UNAVAILABLE` inside the value itself for whoever reads the
    artefact, because those are different people and the log reaches only one
    of them. `summary` is what the uploads entry shape carries into the gate
    document, so this text is what a reviewer sees there.
    """
    columns = parsed.get("columns") or []
    shape = parsed.get("structure") or "file"
    measured = (
        f"{shape}, {len(columns)} columns, {parsed.get('row_count')} rows"
        if columns else f"{shape}, {parsed.get('row_count')} rows"
    )
    return UploadInterpretation(
        summary=(
            f"[!] INTERPRETATION UNAVAILABLE — '{filename}' was read and its "
            f"structure recorded ({measured}), but the description of what it "
            f"CONTAINS did not run. Nothing here says what is in this file. "
            f"Ask the team what it shows; do not treat this line as a summary "
            f"of it."
        ),
        caveats=[
            "The automatic description of this file did not run — its "
            "contents have not been summarised by anything.",
        ],
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
    llm = get_llm("vision", temperature=0.0, timeout=UPLOAD_TIMEOUT).with_structured_output(ImageRead)
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
    extracted = ImageRead(extracted_text="")
    try:
        result = await llm.ainvoke([message])
        if isinstance(result, ImageRead):
            extracted = result
    except Exception as e:
        logger.error("Vision extraction failed: %s", e)

    body = extracted.extracted_text.strip()
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

    raw_sipoc = extracted.sipoc_columns.model_dump() if extracted.sipoc_columns else None
    return {
        "parsed": True,
        "refusal_reason": None,
        "structure": extracted.document_type or "image",
        "columns": [],
        "row_count": None,
        "column_types": {},
        "column_ranges": {},
        "text": body,
        "process_steps": extracted.process_steps,
        "metrics_found": extracted.metrics_found,
        "sipoc_columns": raw_sipoc if raw_sipoc and any(
            v for v in raw_sipoc.values() if v
        ) else None,
    }
