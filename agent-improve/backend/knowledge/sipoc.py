"""R10 (ADR-0095, DEF-294): the SIPOC tool — one plain function with no prompt loop of its own.

One structured reading call turns what the Belt gave — a typed description, a file's text, a picture of the map —
into the SIPOC's fields (`SipocReading`). Code then does the rest, never the model:

    the draft     the reading in the shape a Confirm stores (`parse.sipoc_with_performance`)
    the gaps      the columns and parts still missing, each with its one question (R-G's parts, asked only when
                  missing); step times are an optional gap (R17 amended: "leave it" is an answer)
    the checks    the numbers (`parse.duration_questions`: units, shortest ≤ average ≤ longest, the steps against
                  the lead time)
    the flow      the SIPOC drawn by the read-back's own function, with every missing column marked

Nothing is stored here: the draft is held for the Belt's Confirm (W5). The upload turn at element 12 calls it in
code; the coach is offered it at element 12 only (ADR-0095 decision 4). Both call `read_sipoc`.
"""
from __future__ import annotations

import base64
import logging
import re
from typing import Any, Optional

import openai
from langchain_core.exceptions import OutputParserException
from pydantic import ValidationError

from backend.phases.define import parse
from backend.phases.define.schema import SIPOC_KEYS, SipocReading

logger = logging.getLogger(__name__)

#: R-G's parts as the gap questions (founder rulings 2026-10-27 and 2026-10-29), each with the columns it fills and
#: its one example line. The measures have no part of their own in R-G; their question is the Ask's.
GAP_PARTS: tuple[dict[str, Any], ...] = (
    {"part": 1, "columns": ("process_steps",),
     "question": "What are the main steps of your process, from start to end, as it runs today? Four to eight "
                 "steps, each starting with a verb.",
     "example": "Receive order → Look up prices → Generate invoice → Review and approve → Send to client"},
    {"part": 2, "columns": ("outputs", "customers"),
     "question": "What comes out of the process, and who receives it?",
     "example": "Invoice (PDF), payment request → client finance team, credit control"},
    {"part": 3, "columns": ("inputs", "suppliers"),
     "question": "What goes into the process, and who supplies it?",
     "example": "Signed order, price list, client details ← sales team, pricing database, client"},
    {"part": "measures", "columns": ("process_metrics",),
     "question": "What do you measure on those outputs?",
     "example": "Days from order to invoice; invoices corrected after sending"},
)
#: R17 amended (founder 2026-10-29): the times question, word for word; optional — "leave it" counts as answered.
TIMES_QUESTION = "Do you know roughly how long each step takes? If not, leave it — Measure will measure it."
TIMES_EXAMPLE = "Receive order — about 10 min (5–30 min); orders arrive without a PO number (Anna)."
#: The step count the map needs (the `start-to-end` criterion, p. 26, p. 112).
FEWEST_STEPS, MOST_STEPS = 4, 8
#: What a file or a description that is no process gets (ADR-0095 decision 7).
NOT_A_PROCESS = ("This does not describe a process I can map — describe the main steps in a few lines, or upload a "
                 "map or a process description.")
#: The most of a description or a file's text the reading is given.
READ_CHARS = 6000


def _joined(items: list[str]) -> str:
    return "; ".join(i.strip() for i in items if i and i.strip())


#: A word as the grounding check reads it; words of three letters or fewer ("the", "and", "per") are not checked.
_WORD = re.compile(r"[A-Za-zÄÖÜäöüß]{4,}")


def _stem(word: str) -> str:
    return word.lower()[:5]


def grounded(value: str, source: str) -> bool:
    """§6.4 guard 2 (DEF-294, found live 2026-10-29): a value the reading returned is the Belt's only when every word
    of four letters or more in it is in the source — compared on its first five letters, so "sends" is "send" and
    "diagnoses" is "diagnose". The live reading of the founder's flawed SIPOC (no outputs) returned the outputs "the
    repair service": "service" is in no word of the source, so it is dropped and the outputs are asked."""
    stems = {_stem(w) for w in _WORD.findall(source)}
    return all(_stem(w) in stems or any(s.startswith(w.lower()) for s in stems) for w in _WORD.findall(value))


def keep_grounded(reading: SipocReading, source: str) -> SipocReading:
    """The reading with every value the source does not contain left out — a column, a step, a problem or who said
    it. A dropped column is then a gap the Belt is asked, never an invented value read back."""
    def items(values: list[str]) -> list[str]:
        return [v for v in values if grounded(v, source)]
    steps = [s.model_copy(update={"problems": [p if grounded(p.said_by, source) else p.model_copy(update={"said_by": ""})
                                               for p in s.problems if grounded(p.note, source)]})
             for s in reading.process_steps if grounded(s.name, source)]
    return reading.model_copy(update={k: items(getattr(reading, k)) for k in
                                      ("suppliers", "inputs", "outputs", "customers", "process_metrics")}
                              | {"process_steps": steps})


def captured(reading: SipocReading) -> dict[str, Any]:
    """The reading in the shape the coach's captured SIPOC takes — columns as text, steps as entries with their
    times, how often and problems as written — for `parse.sipoc_with_performance` to read in code."""
    steps = []
    for s in reading.process_steps:
        duration = {k: v.strip() for k, v in (("avg", s.time_avg), ("min", s.time_min), ("max", s.time_max))
                    if v and v.strip()}
        steps.append({"name": s.name.strip(), "duration": duration,
                      **({"runs_per_period": s.runs.strip()} if s.runs.strip() else {}),
                      "problems": [{"note": p.note.strip(), "said_by": p.said_by.strip()}
                                   for p in s.problems if p.note.strip()]})
    perf = {k: v.strip() for k, v in (("lead_time", reading.lead_time), ("runs_per_period", reading.runs_per_period))
            if v and v.strip()}
    return {"suppliers": _joined(reading.suppliers), "inputs": _joined(reading.inputs), "process_steps": steps,
            "outputs": _joined(reading.outputs), "customers": _joined(reading.customers),
            "process_metrics": _joined(reading.process_metrics), **({"process_performance": perf} if perf else {})}


def gaps(draft: dict[str, Any]) -> list[dict[str, Any]]:
    """What the draft still needs, in R-G's order, each gap once with its question: a part whose columns are missing;
    a step count outside four to eight; the step times when no step has one (optional). Empty when nothing is
    missing — a full answer to the one ask gets no further question."""
    missing = set(parse.missing_columns(draft))
    steps = parse.process_steps(draft.get("process_steps"))
    out: list[dict[str, Any]] = []
    for part in GAP_PARTS:
        cols = [c for c in part["columns"] if c in missing]
        if cols:
            out.append({"part": part["part"], "columns": cols, "question": part["question"],
                        "example": part["example"], "optional": False})
        elif part["part"] == 1 and not FEWEST_STEPS <= len(steps) <= MOST_STEPS:
            ask = (f"You named {len(steps)} steps — the map needs four to eight main steps from start to end. "
                   + ("Which steps come before or after these?" if len(steps) < FEWEST_STEPS
                      else "Which of them can be grouped into one main step?"))
            out.append({"part": 1, "columns": ["process_steps"], "question": ask, "example": part["example"],
                        "optional": False})
    if steps and not any(any(s["duration"].get(k) for k in parse.DURATION_KEYS) for s in steps):
        out.append({"part": 4, "columns": [], "question": TIMES_QUESTION, "example": TIMES_EXAMPLE,
                    "optional": True})
    return out


def flow(draft: dict[str, Any], missing: list[str]) -> Optional[dict[str, Any]]:
    """The SIPOC drawn by the read-back's own function (`visuals.draw`), not yet confirmed, with every missing
    column marked; None when there is nothing to draw yet."""
    from backend.phases.define import visuals
    drawn = visuals.draw("sipoc", {"process_map_sipoc": draft}, confirmed=False)
    return {**drawn, "gaps": list(missing)} if drawn else None


def sipoc_draft(reading: Optional[SipocReading], prior: Any = None, source: str = "") -> dict[str, Any]:
    """The code half of the tool — no model: the draft, its gaps, its number checks and its flow from one reading.
    `prior` is the SIPOC confirmed before, so a step keeps its id. `source` is the text the reading was given: every
    value not grounded in it is left out (`keep_grounded`); a picture has no text to check, and its read-back is the
    Belt's to confirm. A reading that is no process returns its plain reply and no draft."""
    if reading is None:
        return {"read": False, "is_process": False, "draft": None, "gaps": [], "checks": [], "flow": None,
                "reply": ""}
    if source.strip():
        reading = keep_grounded(reading, source)
    if not reading.is_process or not any(getattr(reading, k) for k in SIPOC_KEYS):
        return {"read": True, "is_process": False, "draft": None, "gaps": [], "checks": [], "flow": None,
                "reply": NOT_A_PROCESS}
    draft = parse.sipoc_with_performance(captured(reading), prior)
    return {"read": True, "is_process": True, "draft": draft, "gaps": gaps(draft),
            "checks": parse.duration_questions(draft),
            "flow": flow(draft, parse.missing_columns(draft)), "reply": ""}


async def read_sipoc(text: str = "", *, image: Optional[bytes] = None, mime: str = "",
                     prior: Any = None) -> dict[str, Any]:
    """THE SIPOC TOOL (ADR-0095): one structured reading call, then `sipoc_draft` in code. `text` is the Belt's
    description or a file's screened text; `image` a picture of the map, read in the same single call through the
    vision role with its true type (`mime`). A failed reading is never an invented draft: `read` is False."""
    return sipoc_draft(await _reading(text, image, mime), prior, source="" if image else text)


async def _reading(text: str, image: Optional[bytes], mime: str) -> Optional[SipocReading]:
    """The one structured call. Text through the extraction role, a picture through the vision role — the upload
    reader's roles; only the output schema (`SipocReading`) is this tool's (ADR-0095 decision 2)."""
    from langchain_core.messages import HumanMessage, SystemMessage

    from backend.core.llm import UPLOAD_TIMEOUT, get_llm
    from backend.core.prompts import SIPOC_READ_DATA, SIPOC_READ_SYSTEM, cut_at
    data = SIPOC_READ_DATA.format(text=cut_at(text or "", READ_CHARS))
    try:
        if image:
            llm = get_llm("vision", timeout=UPLOAD_TIMEOUT).with_structured_output(SipocReading)
            url = f"data:{mime or 'image/png'};base64,{base64.b64encode(image).decode('utf-8')}"
            message = HumanMessage(content=[{"type": "image_url", "image_url": {"url": url, "detail": "high"}},
                                            {"type": "text", "text": data}])
        else:
            llm = get_llm("extraction", timeout=UPLOAD_TIMEOUT).with_structured_output(SipocReading)
            message = HumanMessage(content=data)
        result = await llm.ainvoke([SystemMessage(content=SIPOC_READ_SYSTEM), message])
        return result if isinstance(result, SipocReading) else None
    except (openai.APIError, OutputParserException, ValidationError, TimeoutError, ValueError) as exc:
        # A failed reading is reported as not read, never invented (the service, the parse, the wait).
        logger.warning("the SIPOC reading failed: %s", exc)
        return None


__all__ = ["GAP_PARTS", "TIMES_QUESTION", "TIMES_EXAMPLE", "NOT_A_PROCESS", "FEWEST_STEPS", "MOST_STEPS",
           "READ_CHARS", "captured", "grounded", "keep_grounded", "gaps", "flow", "sipoc_draft", "read_sipoc"]
