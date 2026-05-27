from __future__ import annotations

SUPPORTED_IMAGE_TYPES = {
    "image/jpeg", "image/jpg", "image/png",
    "image/webp", "image/gif"
}


def classify_content_type(filename: str, mime_type: str) -> str:
    """Return a content_type label for the upload record."""
    mime = (mime_type or "").lower()
    fname = (filename or "").lower()
    if mime in SUPPORTED_IMAGE_TYPES or any(
        fname.endswith(ext) for ext in (".jpg", ".jpeg", ".png", ".webp")
    ):
        return "image"
    if mime == "application/pdf" or fname.endswith(".pdf"):
        return "pdf"
    if "word" in mime or fname.endswith(".docx"):
        return "document"
    if mime == "text/plain" or fname.endswith(".txt"):
        return "text"
    return "other"


def is_image(content_type: str) -> bool:
    return content_type == "image"


def is_supported(content_type: str) -> bool:
    return content_type in {"image", "pdf", "document", "text"}
