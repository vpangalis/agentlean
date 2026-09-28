"""The guard's message catalogue — ADR-0067 point 2 (ACCEPTED); R20, T71, T72, T92, T93.

One fixed text per threat. The wording is the founder's to change, and only here. A reply to a
block is assembled in CODE — never by a model, because handing a manipulative message to a model,
even to suggest a rephrasing, gives the attack what it wants — from:

  the fixed text of the threat,
  the element the Belt is working on (from the phase record),
  that element's sample answer from the phase's SKILL.md (the C3 sample), marked as a sample.

The same reply goes to every sender, whatever their role.
"""
from __future__ import annotations

import re
from functools import lru_cache
from typing import Any, Optional

#: Threat A — rewriting the coach's rules (T71).
A = ("This message was blocked for security reasons: it reads like an instruction to change how the "
     "coach works, rather than an answer about your project.")
#: Threat B — hidden instructions in a file (T72). `{filename}` is the file.
B = ("The file “{filename}” is kept in the case but the coach will not use it: it contains text "
     "addressed to the AI (it may be hidden by formatting, comments, hidden cells or sheets, or the "
     "file's properties). Remove that text and upload the file again if the coach should read it.")
#: Threat D — flooding (T93).
D_LENGTH = ("This message is longer than {limit:,} characters, the most the coach reads at once. "
            "Please split it into shorter messages — your text is still in the box.")
D_RATE = ("Please wait a moment before sending the next message — the coach takes at most {limit} "
          "messages a minute from one person. Your text is still in the box.")
D_UPLOAD_NOTICE = ("This file is large ({size_mb:.0f} MB). The coach reads only the text, so remove pictures "
                   "and pages it doesn't need next time.")
D_UPLOAD_MAX = ("This file is larger than {limit_mb} MB and was not uploaded. The coach reads only the "
                "text: remove pictures and pages it doesn't need, or split the file, and upload it again.")
#: The Azure deployment's content filter refused a model call (T92).
AZURE = ("The model service declined to process this message. Nothing was stored. Please describe your "
         "situation in plain project terms.")
#: Prompt Shields configured but unreachable (ADR-0057, fail closed).
UNAVAILABLE = ("The safety check that screens every message is unavailable right now, so this message was "
               "not read and nothing was saved. Please send it again in a minute — your text is still in the box.")
UPLOAD_UNAVAILABLE = ("The safety check for uploads is unavailable right now, so this file was not read and "
                      "nothing was saved. Please upload it again in a minute.")

_SHOW = re.compile(r"\*\*Show \(illustration[^)]*\):\*\*\s*\*[\"“]?(.+?)[\"”]?\*\s*$", re.M)


@lru_cache(maxsize=8)
def _elements(phase: str) -> dict[str, str]:
    """field -> the element's name, from the phase SKILL.md's element table."""
    from backend.middleware.skills import instructions
    rows = re.findall(r"^\| \d+ \| ([^|]+) \| ([^|]+) \|$", instructions(phase), re.M)
    return {f: name.strip() for name, fields in rows for f in re.findall(r"`(\w+)`", fields)}


def sample(phase: str, field: str) -> Optional[str]:
    """The field's C3 sample, from its script block's "Show (illustration …)" line."""
    try:
        from backend.middleware.skills import _field_blocks
        block = _field_blocks(phase).get(field, (0, ""))[1]
    except Exception:  # noqa: BLE001 — a missing script must not break a block reply
        return None
    m = _SHOW.search(block)
    return m.group(1).strip() if m else None


def element_name(phase: str, field: str) -> str:
    try:
        return _elements(phase).get(field) or field.replace("_", " ").capitalize()
    except Exception:  # noqa: BLE001
        return field.replace("_", " ").capitalize()


def reply(text: str, phase: Optional[str], field: Optional[str], **fmt: Any) -> str:
    """The fixed text, then the element being worked on and its sample (marked as a sample)."""
    out = text.format(**fmt) if fmt else text
    if phase and field:
        out += f" You were working on **{element_name(phase, field)}**."
        example = sample(phase, field)
        if example:
            out += f" Describe your situation instead, for example: *“{example}”* (sample only)."
    return out


__all__ = ["A", "B", "D_LENGTH", "D_RATE", "D_UPLOAD_NOTICE", "D_UPLOAD_MAX", "AZURE", "UNAVAILABLE",
           "UPLOAD_UNAVAILABLE", "reply", "sample", "element_name"]
