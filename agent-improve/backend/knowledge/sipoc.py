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
from contextvars import ContextVar
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


#: Where a clause of the source ends, for the grounding check: a sentence end, a semicolon, a colon (a label), a line
#: break, a bracket or a dash between words.
_CLAUSE_END = re.compile(r"[.;:!?()\[\]\n]|\s[—–-]\s")


def _matches(word: str, stems: set[str]) -> bool:
    return _stem(word) in stems or any(s.startswith(word.lower()) for s in stems)


def grounded(value: str, source: str) -> bool:
    """§6.4 guard 2 (DEF-294, found live 2026-10-29 and 2026-10-30): a value the reading returned is the Belt's only when
    every word of four letters or more in it stands in ONE clause of the source — compared on its first five letters,
    so "sends" is "send" and "diagnoses" is "diagnose". The live readings of the founder's flawed SIPOC (no outputs)
    returned the outputs "the repair service" ("service" is nowhere in the source) and "the repaired device" ("repair"
    is a step, "device" an input: two clauses). Both are dropped, and the outputs are asked."""
    words = _WORD.findall(value)
    if not words:
        return True
    for clause in _CLAUSE_END.split(source):
        stems = {_stem(w) for w in _WORD.findall(clause)}
        if stems and all(_matches(w, stems) for w in words):
            return True
    return False


#: The reading's columns as text lists, keyed as the SIPOC stores them.
_COLUMNS = ("suppliers", "inputs", "outputs", "customers", "process_metrics")


def keep_grounded(reading: SipocReading, source: str) -> SipocReading:
    """The reading with every value the source does not contain left out — a column, a step, a problem or who said
    it. A source that labels its columns ("Suppliers: …. Inputs: …", two or more) gives only those columns: one it does
    not label is not taken (G-332, the rule a Confirm already applies). A dropped column is then a gap the Belt is
    asked, never an invented value read back."""
    labelled = parse.parse_sipoc(source)
    by_label = len(labelled) >= 2

    def items(key: str) -> list[str]:
        if by_label and key not in labelled:
            return []
        return [v for v in getattr(reading, key) if grounded(v, source)]
    steps = [s.model_copy(update={"problems": [p if grounded(p.said_by, source) else p.model_copy(update={"said_by": ""})
                                               for p in s.problems if grounded(p.note, source)]})
             for s in reading.process_steps if grounded(s.name, source)]
    if by_label and "process_steps" not in labelled:
        steps = []
    return reading.model_copy(update={k: items(k) for k in _COLUMNS} | {"process_steps": steps})


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
    columns = {k: _joined(getattr(reading, k)) for k in ("suppliers", "inputs", "outputs", "customers",
                                                        "process_metrics")}
    # A column the source does not give is left out, as a Confirm's label check leaves it out: the draft read back
    # is the value stored.
    return {**{k: v for k, v in columns.items() if v}, **({"process_steps": steps} if steps else {}),
            **({"process_performance": perf} if perf else {})}


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
    `prior` is the SIPOC confirmed before, so a step keeps its id. `source` is the text the reading was given — for a
    picture, the text read from it (the founder's ruling 2026-10-30): every value not grounded in it is left out
    (`keep_grounded`), so a picture with no text read gives no draft. A reading that is no process returns its plain
    reply and no draft."""
    if reading is None:
        return {"read": False, "is_process": False, "draft": None, "gaps": [], "checks": [], "flow": None,
                "reply": ""}
    reading = keep_grounded(reading, source)
    if not reading.is_process or not any(getattr(reading, k) for k in SIPOC_KEYS):
        return {"read": True, "is_process": False, "draft": None, "gaps": [], "checks": [], "flow": None,
                "reply": NOT_A_PROCESS}
    draft = parse.sipoc_with_performance(captured(reading), prior)
    return {"read": True, "is_process": True, "draft": draft, "gaps": gaps(draft),
            "checks": parse.duration_questions(draft),
            "flow": flow(draft, parse.missing_columns(draft)), "reply": ""}


#: The labels the draft is written with, which `parse.parse_sipoc` reads back.
_LABELS = {"suppliers": "Suppliers", "inputs": "Inputs", "process_steps": "Process steps", "outputs": "Outputs",
           "customers": "Customers", "process_metrics": "Process metrics"}


def _step_line(n: int, step: dict[str, Any]) -> str:
    times = [str((step["duration"].get(k) or {}).get("raw") or "").strip() for k in parse.DURATION_KEYS]
    said = ", ".join(dict.fromkeys(t for t in times if t))
    return f"{n}. {step['name']}" + (f" ({said})" if said else "")


def as_text(draft: dict[str, Any]) -> str:
    """The draft as the Belt reads it: one labelled line per column it has, the steps numbered with their times. It is
    the upload read-back's words; a Confirm's label check (`moves._sipoc_store`) reads the same labels back, so every
    column of the draft is kept and none is added."""
    lines = []
    for key in SIPOC_KEYS:
        if key == "process_steps":
            steps = parse.process_steps(draft.get(key))
            if steps:
                lines.append(f"{_LABELS[key]}: " + "; ".join(_step_line(i, s) for i, s in enumerate(steps, 1)))
        elif str(draft.get(key) or "").strip():
            lines.append(f"{_LABELS[key]}: {str(draft[key]).strip()}")
    return "\n".join(lines)


def summary(result: dict[str, Any]) -> str:
    """The upload's summary, written in code from the tool's result (the file list and the gate document show it)."""
    if not result.get("read"):
        return ""
    if not result.get("is_process"):
        return "Not a process description."
    steps = parse.step_names(result["draft"])
    missing = parse.missing_columns(result["draft"])
    return (f"A process map of {len(steps)} step{'s' if len(steps) != 1 else ''}"
            + (f", from “{steps[0]}” to “{steps[-1]}”" if len(steps) > 1 else "") + "."
            + (f" Not given: {', '.join(_LABELS[c].lower() for c in missing)}." if missing else ""))


def kept(result: dict[str, Any]) -> dict[str, Any]:
    """What an upload record keeps of the tool's result: everything but the drawing, which the read-back draws again
    from the draft by the same function."""
    return {k: v for k, v in result.items() if k != "flow"}


async def read_sipoc(text: str = "", *, image: Optional[bytes] = None, mime: str = "",
                     prior: Any = None) -> dict[str, Any]:
    """THE SIPOC TOOL (ADR-0095): one structured reading call, then `sipoc_draft` in code. `text` is the Belt's
    description or a file's screened text; `image` a picture of the map, read in the same single call through the
    vision role with its true type (`mime`); its values are checked against the text read from it, which the result
    carries as `picture_text`. A failed reading is never an invented draft: `read` is False."""
    reading = await _reading(text, image, mime)
    if not image:
        return sipoc_draft(reading, prior, source=text)
    seen = reading.picture_text.strip() if reading else ""
    return {**sipoc_draft(reading, prior, source=seen), "picture_text": seen}


#: R10 (ADR-0095 decision 4, DEF-296): the coach's call at element 12. TURN_PRIOR is the SIPOC read so far (the pending
#: read-back's draft, else the one carried or confirmed before), which the Belt's new words are merged over; TURN_READS
#: is where the executor finds the tool's result, so the read-back holds the tool's draft, never the coach's copy of it.
TURN_PRIOR: ContextVar[Optional[dict[str, Any]]] = ContextVar("sipoc_turn_prior", default=None)
TURN_READS: ContextVar[Optional[list[dict[str, Any]]]] = ContextVar("sipoc_turn_reads", default=None)


def merged(prior: dict[str, Any], added: dict[str, Any]) -> dict[str, Any]:
    """The Belt's new words over the SIPOC read so far: a column, the steps or the whole-process figures the new words
    give replace the earlier ones; everything else is kept as it was."""
    out = {k: v for k, v in prior.items() if k in (*SIPOC_KEYS, "process_performance")}
    out.update({k: v for k, v in added.items() if v})
    return parse.sipoc_with_performance(out, prior)


async def coach_reading(description: str) -> tuple[str, dict[str, Any]]:
    """The SIPOC tool as the coach calls it — the same one reading (`_reading`) and the same code (`sipoc_draft`). With
    a SIPOC read so far, the new words are an addition (the answer to a gap): what they give is merged over it, and the
    gaps are those of the whole. Returns what the coach reads — the SIPOC as read, the gaps to ask (the times question
    optional), the number checks, or the plain reply — and the result, also left for the executor."""
    prior = TURN_PRIOR.get()
    reading = await _reading(description, None, "")
    result = sipoc_draft(reading, prior, source=description)
    if reading is not None and isinstance(prior, dict) and prior:
        draft = merged(prior, captured(keep_grounded(reading, description)))
        result = {"read": True, "is_process": True, "draft": draft, "gaps": gaps(draft),
                  "checks": parse.duration_questions(draft), "flow": None, "reply": ""}
    sink = TURN_READS.get()
    if sink is not None:
        sink.append(kept(result))
    if not result["read"]:
        return "The description could not be read just now. Ask the Belt to send it again.", kept(result)
    if not result["is_process"]:
        return result["reply"], kept(result)
    needed = [g["question"] for g in result["gaps"] if not g["optional"]]
    lines = ["The SIPOC as read from the Belt's words (read it back as it is; nothing is stored until they confirm):",
             as_text(result["draft"])]
    lines += ["Still missing — ask only this:", *needed] if needed else ["Nothing required is missing."]
    lines += [f"Optional: {g['question']}" for g in result["gaps"] if g["optional"]]
    lines += result["checks"]
    return "\n".join(lines), kept(result)


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
           "READ_CHARS", "captured", "grounded", "keep_grounded", "gaps", "flow", "sipoc_draft", "as_text", "summary",
           "kept", "read_sipoc", "TURN_PRIOR", "TURN_READS", "merged", "coach_reading"]
