"""Diagram types and schemas for `propose_diagram` — procedure step 6.2.

Canonical: **§29.2** (*"the diagram types and schemas live in
`core/diagrams.py`"*), **§60.2 — S-F20** (the tool), §50 (the UI contract).

THIS FILE DOES NOT CLOSE G-30, AND MUST NOT BE READ AS DOING SO
---------------------------------------------------------------
**SPEC-GAP G-30 is open and founder-owned**: *"no diagram type or schema is
stated anywhere in this document. The frontend contract this tool writes against
is therefore entirely undefined — to be designed with founder."*

What is below is **not a designed catalogue**. It is a transcription of the two
diagram shapes `ui/index.html` **already renders today**, read off the render
functions rather than invented:

    renderSipocDiagram   ui/index.html  — five column keys + draft + source
    render5W2HMindmap    ui/index.html  — visualisation.type == 'mindmap_5w2h'

**The distinction matters.** Inventing a type catalogue here would close a
founder-owned gap by implementation — the same mistake step 6.1 declined to make
with G-01 and DP1. Transcribing the live contract does not: it records what the
frontend can already draw, so `propose_diagram` has something true to write
against, and leaves the catalogue G-30 asks for entirely open. **A new diagram
type is a founder decision plus a frontend renderer, not an entry added here.**

WHAT THESE PAYLOADS ARE FOR — FOUNDER RULING, 2026-09-03
---------------------------------------------------------
*"Agent Improve does not export documents. The assembled `{Phase}Output` shown
on the UI is the record. `propose_diagram` returns structured JSON rendered by
the UI (`renderSipocDiagram`, `render5W2HMindmap`) … Neither emits a file; both
are coaching aids, not document generators."*

So a builder here produces something the app **draws during coaching**, and
nothing here is archival. The record is the gate document, assembled once at
`gate_apply` from `artifacts` (§33.2) — a diagram is not a second copy of it,
and must never become one.

WHY THE MODEL NEVER EMITS MARKUP
--------------------------------
**S-F20 B1** — structured JSON, never SVG. *"The model describes what to draw;
the frontend owns how it looks"* (§29.2): model-emitted SVG drifts from the
design system and cannot be restyled. So every builder below returns a plain
dict, and `propose_diagram` rejects a payload that looks like markup.

THE SIPOC KEYS ARE THE UI'S, AND THEY ARE NOT `process_map_sipoc`'s
-------------------------------------------------------------------
The renderer requires `suppliers`, `inputs`, `process_steps`, `outputs`,
`customers`. §10.8's captured field `process_map_sipoc` carries those five **and
`process_metrics`**, which the diagram does not draw. They are close enough to
be confused and are two different things: one is a gate-document field, the
other is a presentation payload. `sipoc_columns` below takes the field and drops
what the renderer has no column for, rather than either shape pretending to be
the other.
"""
from __future__ import annotations

from typing import Any

#: The two types the frontend can draw today. **Not the catalogue G-30 asks
#: for** — the list of renderers that exist, which is a different claim.
DIAGRAM_TYPES: tuple[str, ...] = ("sipoc", "mindmap_5w2h")

#: `renderSipocDiagram`'s five columns, in the order it lays them out. A sixth
#: key here would not be drawn; a missing one renders as an empty column.
SIPOC_COLUMNS: tuple[str, ...] = (
    "suppliers", "inputs", "process_steps", "outputs", "customers",
)

#: What `sipoc.source` may say. The UI prints a provenance note from it, so an
#: unrecognised value would render as an unexplained badge.
SIPOC_SOURCES: tuple[str, ...] = ("generated", "upload")


class DiagramError(ValueError):
    """A payload the frontend could not render. Raised to the tool, not the Belt.

    `propose_diagram` catches this and returns a plain-language message the
    coach can act on — the same posture as the computation tools' B3 (§69):
    a tool that raised into the agent loop would surface to the Belt as a
    tool-call failure rather than as something the coach can rephrase.
    """


def _as_lines(value: Any) -> list[str]:
    """Coerce one column to the list of short strings the renderer draws.

    Accepts what a coach realistically produces — a list, or newline/semicolon
    separated prose — because the alternative is a tool that rejects a correct
    SIPOC over its punctuation.
    """
    if value is None:
        return []
    if isinstance(value, (list, tuple)):
        return [str(v).strip() for v in value if str(v).strip()]
    text = str(value)
    parts = [p.strip() for chunk in text.split("\n") for p in chunk.split(";")]
    return [p for p in parts if p]


def sipoc_columns(data: dict[str, Any]) -> dict[str, list[str]]:
    """The five drawn columns, from a `process_map_sipoc` value or a loose dict.

    **Drops `process_metrics` deliberately** — §10.8 puts it on the captured
    field and the renderer has no column for it. Dropping it here is what keeps
    the gate document and the picture from having to agree on shape.
    """
    return {key: _as_lines(data.get(key)) for key in SIPOC_COLUMNS}


def build_sipoc(data: dict[str, Any], *, draft: bool = True,
                source: str = "generated") -> dict[str, Any]:
    """A `sipoc` payload in the shape `renderSipocDiagram` reads.

    `draft` defaults True: the renderer treats anything but an explicit `False`
    as a draft and badges it, and a coach-proposed SIPOC the Belt has not
    confirmed IS a draft. Only gate approval makes it `False` — which is the v1
    behaviour this transcribes (`orchestrate.py` sets `draft: False` from the
    confirmed value, `True` from a generated one).
    """
    if source not in SIPOC_SOURCES:
        raise DiagramError(
            f"source must be one of {', '.join(SIPOC_SOURCES)}; got {source!r}"
        )
    columns = sipoc_columns(data)
    if not any(columns.values()):
        raise DiagramError(
            "a SIPOC needs at least one populated column of "
            f"{', '.join(SIPOC_COLUMNS)}"
        )
    return {**columns, "draft": draft, "source": source}


def build_mindmap_5w2h(data: dict[str, Any]) -> dict[str, Any]:
    """A `mindmap_5w2h` payload — the 5W2H problem-definition mind map.

    `render5W2HMindmap` branches on `visualisation.type`, so the type tag rides
    inside the payload rather than beside it. `total_count` is what the UI
    prints as the progress denominator; the seven 5W2H slots are the count.
    """
    slots = ("what", "where", "when", "who_affected", "why", "how_much",
             "how_often")
    filled = {k: str(data[k]).strip() for k in slots
              if str(data.get(k) or "").strip()}
    if not filled:
        raise DiagramError(
            "a 5W2H mind map needs at least one of: " + ", ".join(slots)
        )
    return {"type": "mindmap_5w2h", **filled,
            "filled_count": len(filled), "total_count": len(slots)}


#: Builders by type. `propose_diagram` dispatches through this, so an
#: unrecognised type fails at the tool with a list of what IS renderable
#: rather than producing JSON the frontend silently drops.
BUILDERS = {
    "sipoc": build_sipoc,
    "mindmap_5w2h": build_mindmap_5w2h,
}


__all__ = [
    "DIAGRAM_TYPES",
    "SIPOC_COLUMNS",
    "SIPOC_SOURCES",
    "DiagramError",
    "BUILDERS",
    "sipoc_columns",
    "build_sipoc",
    "build_mindmap_5w2h",
]
