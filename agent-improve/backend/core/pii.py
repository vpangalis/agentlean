"""Personal data masked before a model sees it — T87, ADR-0062 (DEF-144).

The types: e-mail and card numbers (LangChain's own detectors), phone numbers and IBAN / account
numbers (narrow patterns below). Person names are never masked: the team element needs them
(ADR-0062 point 3). The strategy is `redact`, so a masked value reads `[REDACTED_EMAIL]` and no
part of it reaches a model.

Two places use it, both LangChain's own mechanism (rule 0.24):
  uploads      `mask(text)` over the parsed text before it is interpreted or indexed
               (`upload/agent.py::process_upload`); the file itself stays in Blob for the Belt
  coach input  `executor_middleware()` — one `PIIMiddleware` over all four types (a combined
               detector) on the executor, tool results only, never the Belt's own messages
               (ADR-0062 point 2)

Every masking is counted by type — never the value — for `step_log` (point 4).
"""
from __future__ import annotations

import re
from typing import Any, Literal, Optional

from langchain.agents.middleware import PIIMiddleware
from langchain.agents.middleware._redaction import apply_strategy, resolve_detector

#: An international number (+ and country code) or a national one (leading 0) with separators:
#: narrow on purpose, so an ISO date (2026-03-31), a month (2026-01) or a CSV row of figures
#: is never taken for a phone number.
PHONE = r"(?<![\w+])(?:\+\d{1,3}[ .-]?(?:\(\d{1,4}\)[ .-]?)?\d{2,4}(?:[ .-]?\d{2,4}){2,4}|0\d{2,4}[ /-]\d{3,4}[ -]?\d{3,4})(?![\w])"
#: An IBAN: two letters, two check digits, then 11-30 letters or digits, in groups of four or not.
IBAN = r"\b[A-Z]{2}\d{2}(?: ?[A-Z0-9]{4}){2,7}(?: ?[A-Z0-9]{1,4})?\b"
#: (type, detector) — `None` is LangChain's built-in detector for the type.
TYPES: tuple[tuple[str, Optional[str]], ...] = (
    ("email", None), ("credit_card", None), ("phone", PHONE), ("iban", IBAN))
STRATEGY: Literal["redact"] = "redact"


def detect(text: str) -> list[Any]:
    """Every personal-data value of `TYPES` in `text`, each match tagged with its own type;
    where two overlap, the earlier (then the longer) is kept."""
    found: list[Any] = []
    for pii_type, detector in TYPES:
        found += resolve_detector(pii_type, detector)(text or "")
    kept: list[Any] = []
    for m in sorted(found, key=lambda m: (m["start"], -(m["end"] - m["start"]))):
        if not kept or m["start"] >= kept[-1]["end"]:
            kept.append(m)
    return kept


def mask(text: str) -> tuple[str, dict[str, int]]:
    """`text` with every personal-data value redacted, and the count per type."""
    found = detect(text)
    counts: dict[str, int] = {}
    for m in found:
        counts[m["type"]] = counts.get(m["type"], 0) + 1
    return (apply_strategy(text, found, STRATEGY) if found else (text or "")), counts


def executor_middleware() -> list[Any]:
    """ONE `PIIMiddleware` over all four types (the combined detector), on tool results only
    (ADR-0062 point 2). One, not four: each instance is a graph node on every model call."""
    return [PIIMiddleware("personal_data", strategy=STRATEGY, detector=detect,
                          apply_to_input=False, apply_to_tool_results=True)]


def counted(texts: list[str]) -> dict[str, int]:
    """How many values of each type were redacted in `texts` (the markers `redact` leaves)."""
    counts: dict[str, int] = {}
    for pii_type, _ in TYPES:
        n = sum(len(re.findall(re.escape(f"[REDACTED_{pii_type.upper()}]"), t or "")) for t in texts)
        if n:
            counts[pii_type] = n
    return counts


__all__ = ["TYPES", "PHONE", "IBAN", "STRATEGY", "detect", "mask", "executor_middleware", "counted"]
