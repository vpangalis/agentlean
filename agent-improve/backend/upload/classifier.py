"""Content-type and kind classification for uploads — procedure step 6.11.

Architecture §29.1, §23.2. Rulings: `docs/_archive/DECISIONS.md` Part AP2.

TWO CLASSIFICATIONS, AND THEY ANSWER DIFFERENT QUESTIONS
    `classify_content_type` answers *"how do we read this file"* and selects a
    parser. `classify_kind` answers *"what is this file to the project"* and
    selects a DESTINATION. They are separate because a `.docx` can be either a
    supplier's incident report (evidence) or the team's own draft control plan
    (artefact), and the format tells you nothing about which.
"""
from __future__ import annotations

import logging

logger = logging.getLogger(__name__)

SUPPORTED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png",
    "image/webp", "image/gif"
}

_SPREADSHEET_MIMES = {
    "text/csv",
    "application/csv",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}

#: **EVIDENCE describes the world; an ARTEFACT is what the team designed.**
#: Ruling 3: one bucket would let a proposed future be retrieved later as a
#: fact about the present, which is a correctness failure in a system whose
#: premise is that an approved gate document is worth trusting. The purposes
#: below are the labels `auto_detect_purpose` and the UI already produce.
ARTEFACT_PURPOSES = {
    "Process map",          # a to-be map is a design, not an observation
    "Improvement plan",
    "Project document",
}
EVIDENCE_PURPOSES = {
    "Data file",
    "Survey data",
    "Capability report",
    "Analysis",
}

EVIDENCE = "evidence"
ARTEFACT = "artefact"


def classify_content_type(filename: str, mime_type: str) -> str:
    """Return a content_type label for the upload record.

    **`spreadsheet` was added at step 6.11.** Before it, csv and xlsx fell
    through to `other`, which had no parser and no place in `is_supported` —
    so the single most common thing a Belt uploads was stored, never parsed
    and never indexed (Part AP1).
    """
    mime = (mime_type or "").lower()
    fname = (filename or "").lower()
    if mime in SUPPORTED_IMAGE_TYPES or any(
        fname.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")
    ):
        return "image"
    if mime in _SPREADSHEET_MIMES or any(
        fname.endswith(ext) for ext in (".csv", ".xlsx", ".xlsm", ".xls")
    ):
        return "spreadsheet"
    if mime == "application/pdf" or fname.endswith(".pdf"):
        return "pdf"
    if "word" in mime or fname.endswith(".docx"):
        return "document"
    if mime == "text/plain" or fname.endswith(".txt"):
        return "text"
    return "other"


def classify_kind(purpose: str, declared_kind: str = "") -> tuple[str, bool]:
    """`(kind, was_declared)` — evidence or artefact, and how we know.

    **A declared kind always wins.** Where the UI or the Belt says which it is,
    that is the answer; the mapping below is only for the case where nobody
    said. The boolean is returned rather than discarded because *how* the
    system decided is the part a reviewer needs: a derived kind is a guess
    from a purpose label, and ruling 3's failure mode — a proposed future
    retrieved as a present fact — is silent when it happens.

    **The default is EVIDENCE, and the choice is deliberate.** An unrecognised
    purpose is far more often a data file nobody labelled than a design
    document, and defaulting to artefact would drop real evidence out of
    §29.1's only external channel without saying so. The derived case is
    logged, and 6.12's ask-binding replaces the guess with the coach's own
    request.
    """
    if declared_kind:
        normalised = declared_kind.strip().lower()
        if normalised in (EVIDENCE, ARTEFACT):
            return normalised, True
        logger.warning(
            "Unrecognised declared upload kind %r — falling back to the "
            "purpose mapping. Expected %r or %r.",
            declared_kind, EVIDENCE, ARTEFACT,
        )

    if purpose in ARTEFACT_PURPOSES:
        return ARTEFACT, False
    if purpose in EVIDENCE_PURPOSES:
        return EVIDENCE, False

    logger.info(
        "Upload purpose %r maps to no kind — defaulting to %s. 6.12's "
        "ask-binding is what replaces this guess.", purpose, EVIDENCE,
    )
    return EVIDENCE, False


def is_image(content_type: str) -> bool:
    return content_type == "image"


def is_supported(content_type: str) -> bool:
    """True only where a real extractor exists for `content_type`.

    **This used to lie about pdf and document** — both returned True with no
    extractor behind either (Part AP1). It is now the exact set of labels that
    `parse_upload` can handle, plus `image`, whose extractor is the vision
    call rather than a deterministic parser.
    """
    return content_type in {"image", "spreadsheet", "pdf", "document", "text"}
