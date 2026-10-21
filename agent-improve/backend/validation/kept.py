"""Kept verdicts — the same answer gets the same verdict (DEF-224, G-225; founder ruling 2026-10-21).

Both places a model judges an answer — the planner's per-element judgment and the gate rubric (layer 2d) — keep
their verdict beside the element it judged, in that element's own `field_status` entry, with a fingerprint of the
exact answer and the version of what it was judged against (the phase script and the prompt). An unchanged
fingerprint reuses the verdict with no model call; a changed one is judged again. No new state field: the entry
is `dict[str, Any]`, checkpointed with the phase record.

  field_status[element]["judged"] = {"fp": ..., "verdict": {...}}         the planner's judgment
  field_status[element]["gate"]   = {criterion: {"fp", "status", "feedback"}}   the rubric's criteria on it

`moves.decide` rebuilds an element's entry when its status moves, so every writer of `field_status` carries the
kept verdicts forward with `carry`.
"""
from __future__ import annotations

import hashlib
import json
from typing import Any

#: The keys of an element's `field_status` entry that hold kept verdicts.
KEYS = ("judged", "gate")


def normalise(text: Any) -> str:
    """An answer's text as compared: whitespace collapsed, case kept (a changed word is a changed answer)."""
    return " ".join(str(text or "").split())


def answer(*parts: Any) -> list[str]:
    """The answer a judgment reads — its distinct non-empty parts, in order: the same message sent twice is one
    answer, not two."""
    return list(dict.fromkeys(p for p in (normalise(x) for x in parts) if p))


def fingerprint(*parts: Any) -> str:
    """A short, stable hash of the parts (JSON, sorted keys)."""
    raw = json.dumps(parts, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]


def carry(before: dict[str, Any], after: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """`after` with each element's kept verdicts carried from `before` where its entry was rebuilt without them.
    A kept verdict that no longer matches is harmless: its fingerprint will not match the next answer."""
    out = {f: dict(v) for f, v in (after or {}).items()}
    for field, entry in (before or {}).items():
        if field in out and isinstance(entry, dict):
            for key in KEYS:
                if key in entry and key not in out[field]:
                    out[field][key] = entry[key]
    return out


__all__ = ["KEYS", "answer", "carry", "fingerprint", "normalise"]
