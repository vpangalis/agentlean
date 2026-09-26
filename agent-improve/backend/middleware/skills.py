"""`DMAICSkillsMiddleware` — position 2 — procedure step 6.3.

Canonical: **§61.3 — S-C12**. Architecture **§19.2**, full treatment **§32**.

THREE LEVELS, AND WHAT EACH COSTS
    | Level | When | What loads |
    |---|---|---|
    | 1 | Startup | descriptions only — **under 2K for all five combined** (B1) |
    | 2 | On demand | that phase's full instructions, via `load_skill(name)` (B2) |
    | 3 | On demand | reference files, when explicitly needed |

    Measured on the five files as they stand: the descriptions total **~1,029
    tokens**, inside B1's budget; the files themselves run 20K–52K characters,
    which is why level 2 is on demand and not eager. `test_skills.py` asserts
    the budget, so a SKILL.md whose description grows past it fails there
    rather than quietly costing every startup.

STORAGE IS `FilesystemBackend` (B4)
    Git-versioned alongside the code, *"so a skill change is reviewable in the
    same PR as the code that depends on it"* (§32). `ContextHubBackend` is
    deferred to the multi-deployment stage. The backend here is a small local
    reader rather than an imported class: LangChain ships no skills backend to
    reuse, so §0.24's rule is satisfied by there being no primitive to
    reinvent — checked, and recorded rather than assumed.

`load_skill` IS REGISTERED BY THIS MIDDLEWARE, NOT BOUND BY THE EXECUTOR
    `AgentMiddleware.tools` is the framework's own registration point —
    *"Additional tools registered by the middleware"* — so `load_skill` reaches
    the model without appearing in `create_agent(tools=...)`.

    **That is why it is outside §30's per-phase totals**, and the five SKILL.md
    `allowed-tools` lists agree: §32 requires them to match §30's subset
    exactly, and not one of them names `load_skill`.

> **SPEC-GAP (G-33) is OPEN, and this file does not close it.** *"Whether
> `load_skill` is bound as an eighth universal tool is undetermined"*, and the
> register states the consequence precisely: **"if bound, Measure goes to 16
> against a cap of 16."** It is not bound as one here — it is middleware-
> registered — but the model still sees one more tool than §30 counts, so the
> BOUND totals are one higher than the ratified ones. Both are asserted in
> `test_skills.py`, and WATCH 25 carries the arithmetic. The collision is not
> live yet: Measure binds 13 today and reaches 16 only once the two owed
> universal tools land at 7.1 and 7.5.

> **SPEC-GAP (G-24):** constructor arguments are unstated. The single `phase`
> argument below is what B2 needs and no more.
"""
from __future__ import annotations

import hashlib
import logging
import re
import unicodedata
from difflib import SequenceMatcher
from functools import lru_cache
from pathlib import Path
from typing import Any, Callable, Optional

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool, tool

from backend.core.prompts import SECTION_SCRIPT, SECTION_STATE
from backend.phases.mappers_common import PHASE_ORDER

logger = logging.getLogger(__name__)

#: `agent-improve/skills/` — git-versioned beside the code (B4). Resolved from
#: this file rather than from the process CWD, which differs between the app,
#: pytest and a scratch script.
SKILLS_ROOT = Path(__file__).resolve().parents[2] / "skills"

#: §32's five, by phase. The directory name is the skill name.
SKILL_DIRS: dict[str, str] = {p: f"dmaic-{p}-phase" for p in PHASE_ORDER}

#: B1's budget for all five descriptions combined, at startup.
LEVEL_1_TOKEN_BUDGET = 2000

_FRONTMATTER = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.S)


class SkillNotFound(KeyError):
    """Asked for a skill that is not one of the five."""


@lru_cache(maxsize=len(PHASE_ORDER))
def _read(phase: str) -> str:
    """One SKILL.md, whole. Cached — the file is git-versioned and static."""
    try:
        directory = SKILL_DIRS[phase]
    except KeyError:
        raise SkillNotFound(
            f"Unknown skill {phase!r}. The five are: "
            f"{', '.join(SKILL_DIRS)}."
        ) from None
    path = SKILLS_ROOT / directory / "SKILL.md"
    if not path.is_file():
        raise SkillNotFound(f"{path} does not exist")
    return path.read_text(encoding="utf-8")


def frontmatter(phase: str) -> dict[str, str]:
    """The SKILL.md YAML header, as flat `key: value` pairs.

    Deliberately not a YAML parse: only the flat scalar keys are read
    (`name`, `description`, `allowed-tools`), and adding a YAML dependency to
    read three strings would be the reverse of §0.24's rule.
    """
    match = _FRONTMATTER.match(_read(phase))
    if not match:
        return {}
    out: dict[str, str] = {}
    for line in match.group(1).splitlines():
        if line.startswith((" ", "\t")) or ":" not in line:
            continue
        key, _, value = line.partition(":")
        out[key.strip()] = value.strip()
    return out


def description(phase: str) -> str:
    """**Level 1** — the description alone, which is all that loads at startup."""
    return frontmatter(phase).get("description", "")


def instructions(phase: str) -> str:
    """**Level 2** — the full phase instructions, minus the frontmatter."""
    return _FRONTMATTER.sub("", _read(phase), count=1).strip()


def allowed_tools(phase: str) -> list[str]:
    """That skill's `allowed-tools`, which §32 B3 requires to match §30."""
    raw = frontmatter(phase).get("allowed-tools", "")
    return [t.strip() for t in raw.split(",") if t.strip()]


# ── step 6.46 — the script on every call, and the §22 guard ──────────────

_VERSION = re.compile(r'^\s+version:\s*"?([^"\n]+?)"?\s*$', re.M)


@lru_cache(maxsize=len(PHASE_ORDER))
def script_record(phase: str) -> dict[str, Any]:
    """What one delivery of `phase`'s script IS — name, version, content hash.

    The hash is over exactly the text placed in the system message, so a
    `step_log` entry names the script the coach had, byte for byte.
    """
    body = instructions(phase)
    fm = _FRONTMATTER.match(_read(phase))
    version = _VERSION.search(fm.group(1)) if fm else None
    return {"script": SKILL_DIRS[phase],
            "version": version.group(1) if version else "",
            "sha256": hashlib.sha256(body.encode("utf-8")).hexdigest()[:16],
            "chars": len(body)}


_SHOW_LINE = re.compile(r'^>\s*\*\*Show[^*]*:\*\*\s*\*"(.+?)"\*', re.M)
_SHOW_TABLE = re.compile(
    r'^>\s*\*\*Show[^*]*table[^*]*:\*\*[ \t]*\n(?:>[ \t]*\n)?((?:>[ \t]*\|.*\n?)+)',
    re.M | re.I)

#: §22's guard — THE MATCHING RULE, stated once. Both texts are normalised
#: (lower case; letters, digits, % and currency signs kept; everything else one
#: space). A captured value is an example if the example is contained in it, it
#: is contained in the example, or their WORD-sequence similarity ratio
#: (difflib, autojunk off) is at least this.
#: Examples shorter than EXAMPLE_MIN_CHARS are not guarded: "30 September 2026"
#: is a date a Belt may genuinely choose, and refusing it would be wrong.
EXAMPLE_MATCH_RATIO = 0.80
EXAMPLE_MIN_CHARS = 25


def _norm(text: str) -> str:
    text = unicodedata.normalize("NFKC", text).lower()
    return " ".join(re.sub(r"[^\w%€£$]+", " ", text).split())


def _flatten(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(_flatten(v) for v in value.values())
    if isinstance(value, (list, tuple)):
        return " ".join(_flatten(v) for v in value)
    return "" if value is None else str(value)


@lru_cache(maxsize=len(PHASE_ORDER))
def worked_examples(phase: str) -> tuple[str, ...]:
    """Every worked example in `phase`'s script — the `**Show:**` quotations and
    the example table — normalised, at or above EXAMPLE_MIN_CHARS."""
    body = instructions(phase)
    raw = [m.group(1) for m in _SHOW_LINE.finditer(body)]
    # A table's example is its BODY rows: the header names columns, and a
    # Belt's own table shares those names without copying anything.
    raw += [" ".join(c for row in m.group(1).splitlines()[1:]
                     if "---" not in row
                     for c in row.lstrip("> ").strip("|").split("|"))
            for m in _SHOW_TABLE.finditer(body)]
    return tuple(n for n in (_norm(r) for r in raw) if len(n) >= EXAMPLE_MIN_CHARS)


def example_match(value: Any, phase: str) -> str | None:
    """The worked example `value` reproduces, or None (§22)."""
    v = _norm(_flatten(value))
    if len(v) < EXAMPLE_MIN_CHARS:
        return None
    words = v.split()
    for ex in worked_examples(phase):
        # Similarity over WORDS, with `autojunk` off: on strings over 200
        # characters difflib's junk heuristic discards the commonest characters
        # and scored a lightly edited example 0.62; over words it is 0.94, a
        # Belt's own answer 0.04, and 0E5's real answers at most 0.62.
        if ex in v or v in ex or SequenceMatcher(
                None, words, ex.split(), autojunk=False).ratio() >= EXAMPLE_MATCH_RATIO:
            return ex
    return None


# ── G-96 — the script step a reply performs, for layer 2a ─────────────────

#: One numbered field block: `**[5 · baseline_estimate · required · …]**`
#: followed by its quoted `>` lines. All five scripts number their fields.
_FIELD_BLOCK = re.compile(
    r'^\*\*\[(\d+) · (\w+) · [^\]]*\]\*\*[ \t]*\n((?:>.*(?:\n|$))+)', re.M)

#: Fields captured INSIDE a coached position -> that position's field —
#: derived from the schema's own map (`phases/define/schema._CAPTURED_INSIDE`),
#: never restated: the registry inside 5, the CTQs inside 3, the 5W2H inside 4.
from backend.phases.define.schema import _CAPTURED_INSIDE as _DEFINE_INSIDE  # noqa: E402
_CAPTURED_INSIDE = {inner: position for position, inners in _DEFINE_INSIDE.items()
                    for inner in inners}

#: The two moves a turn can make on a field (§43, "Explain → Show → Ask →
#: Confirm, on every field"): teach and ask for it, or read the Belt's value
#: back and check it.
CONFIRM, EXPLAIN_SHOW_ASK = "confirm", "explain_show_ask"


@lru_cache(maxsize=len(PHASE_ORDER))
def _field_blocks(phase: str) -> dict[str, tuple[int, str]]:
    """field -> (position, its script block)."""
    return {m.group(2): (int(m.group(1)), m.group(3).strip())
            for m in _FIELD_BLOCK.finditer(instructions(phase))}


def script_step(phase: str, captured: list[str],
                focus_field: str | None) -> dict[str, Any] | None:
    """The script step a reply performs — G-96, founder ruling Option A.

    **Derived from the reply, never asked of a model.** A turn that captured a
    value is at that field's ④ **Confirm**: the script has the coach read the
    value back and check it. A turn that captured nothing is teaching and
    asking for the planner's focus field (① Explain, ② Show, ③ Ask).

    `position` and `block` are the field's own, from the numbered script;
    `None` and empty for a field the script does not number — the pattern is
    still §43's, so the step is still returned.
    """
    if phase not in SKILL_DIRS:
        return None
    field = next((f for f in captured if f), None) or focus_field
    step = CONFIRM if captured else EXPLAIN_SHOW_ASK
    if not field:
        return {"position": None, "field": None, "step": step, "block": ""}
    position, block = _field_blocks(phase).get(
        _CAPTURED_INSIDE.get(field, field), (None, ""))
    return {"position": position, "field": field, "step": step, "block": block}


_BLOCK_HEAD = re.compile(r"^\*\*\[(?P<head>[^\]]+)\]\*\*[ \t]*$", re.M)


@lru_cache(maxsize=len(PHASE_ORDER))
def _script_blocks(phase: str) -> tuple[dict[str, str], str, str]:
    """`({field: its blocks}, opening, closing)` from the phase's coaching script.

    A numbered block `[n · field · …]` is that field's. An unnumbered block
    that names `field n` belongs to that field (METRIC LITERACY, field 5); a
    `TOOL` block to the numbered field before it (the savings calculation
    runs on the target). OPENING and the closing block are kept apart.
    """
    body = instructions(phase)
    heads = list(_BLOCK_HEAD.finditer(body))
    numbered: dict[int, str] = {}
    for m in heads:
        parts = [p.strip() for p in m["head"].split("·")]
        if parts[0].isdigit() and len(parts) > 1:
            numbered[int(parts[0])] = parts[1]
    fields: dict[str, list[str]] = {}
    opening = closing = ""
    last: Optional[str] = None
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(body)
        block = body[m.start():end].split("\n---\n")[0].rstrip()
        head = m["head"]
        parts = [p.strip() for p in head.split("·")]
        named = re.search(r"\bfield (\d+)\b", head)
        if head.startswith("OPENING"):
            opening = block
        elif parts[0].isdigit():
            last = numbered[int(parts[0])]
            fields.setdefault(last, []).append(block)
        elif named and int(named.group(1)) in numbered:
            fields.setdefault(numbered[int(named.group(1))], []).insert(0, block)
        elif head.startswith("TOOL") and last:
            fields.setdefault(last, []).append(block)
        else:
            closing = block
    return {f: "\n\n".join(b) for f, b in fields.items()}, opening, closing


def script_section(phase: str, field: Optional[str], opening: bool) -> str:
    """Section 2 of the coach's input — step 6.61 (founder, item 4): the
    opening on the phase's first turn only, plus the CURRENT field's script
    block and nothing else. With no current field (every one confirmed), the
    closing block. A phase whose script carries no block for the field gets
    its whole script rather than nothing."""
    blocks, open_block, closing = _script_blocks(phase)
    if field is None:
        chosen = closing
    else:
        chosen = blocks.get(_CAPTURED_INSIDE.get(field, field), "")
        if not chosen:
            return instructions(phase)
    return "\n\n".join(b for b in ((open_block if opening else ""), chosen) if b)


#: A block's labelled sections: `> **What it is:** …`, `> **Show (…):** …`.
_LABEL = re.compile(r"^\*\*(?P<label>[^*:(]+?)\s*(?:\([^)]*\))?\s*(?::\*\*|\*\*)")
#: One acceptance criterion: `- `id` — what it checks (p. n)`.
_CRITERION = re.compile(r"^-\s*`(?P<id>[a-z0-9-]+)`\s*[—-]+\s*(?P<text>.+)$")
#: The sections the judge reads (R3): what the element is, the question, and
#: the criteria. Never a Show — neither an example nor a demo table — so the
#: answer is measured against the criteria, not against one illustration.
_JUDGE_SECTIONS = ("What it is", "Ask", "Acceptance criteria", "Explain")


def _sections(block: str) -> dict[str, list[str]]:
    """label -> its lines, for a field block's `> **Label:**` sections."""
    out: dict[str, list[str]] = {}
    current = ""
    for raw in block.splitlines():
        line = raw.lstrip(">").strip()
        m = _LABEL.match(line)
        if m:
            current = m["label"].strip()
            out.setdefault(current, [])
        out.setdefault(current, []).append(raw)
    return out


def acceptance_criteria(phase: str, field: str) -> list[tuple[str, str]]:
    """`(id, what it checks)` for the element `field` belongs to — the R3
    validation layer's yardstick, parsed from the element's SKILL.md block."""
    if phase not in SKILL_DIRS:
        return []
    _position, block = _field_blocks(phase).get(_CAPTURED_INSIDE.get(field, field), (None, ""))
    lines = _sections(block).get("Acceptance criteria", [])
    return [(m["id"], m["text"].strip()) for m in
            (_CRITERION.match(ln.lstrip(">").strip()) for ln in lines) if m]


def field_needs(phase: str, field: str) -> str:
    """What the phase script says an element needs — what it is, its question
    and its ACCEPTANCE CRITERIA (R3, 2026-09-26). The planner's one judgment
    reads this, so "sufficient" is judged against the element's criteria and
    never against a model's own notion. No Show section reaches it: neither a
    worked example nor a demo table (until R3 the SIPOC and 5W2H tables did)."""
    if phase not in SKILL_DIRS:
        return ""
    _position, block = _field_blocks(phase).get(_CAPTURED_INSIDE.get(field, field), (None, ""))
    sections = _sections(block)
    if "Acceptance criteria" not in sections:
        # A script not yet written to R2/R3 (the other four phases): the
        # block without its worked example, as before (step 6.61).
        return "\n".join(line for line in block.splitlines()
                         if not line.lstrip("> ").startswith("**Show"))
    return "\n".join(line for label in _JUDGE_SECTIONS for line in sections.get(label, []))


def level_1_catalogue() -> str:
    """All five descriptions — what the coach sees before loading anything."""
    return "\n".join(
        f"  {SKILL_DIRS[p]}: {description(p)}" for p in PHASE_ORDER
    )


class DMAICSkillsMiddleware(AgentMiddleware):
    """Position 2. Progressive disclosure over the five phase skills.

    Constructed per turn with the phase in flight, alongside the agent.
    """

    name = "DMAICSkillsMiddleware"

    def __init__(
        self,
        phase: str,
        on_delivery: Optional[Callable[[dict[str, Any]], None]] = None,
        focus_field: Optional[str] = None,
        opening: bool = False,
    ) -> None:
        super().__init__()
        if phase not in SKILL_DIRS:
            raise ValueError(
                f"Unknown phase {phase!r}. The five (§12) are: "
                f"{', '.join(SKILL_DIRS)}."
            )
        self.phase = phase
        self.loaded: list[str] = []
        self._catalogue: str = ""
        #: 6.46 — each delivery of the script is handed to the node, which owns
        #: `step_log`; the middleware writes no state itself.
        self.on_delivery = on_delivery
        #: 6.61 (item 4) — section 2 carries the CURRENT field's script block
        #: and, on the phase's first turn only, the opening.
        self.focus_field = focus_field
        self.opening = opening
        #: **The framework's own registration point.** Not
        #: `create_agent(tools=...)` — see G-33 in the module docstring.
        self.tools: list[BaseTool] = [self._make_load_skill()]

    def _make_load_skill(self) -> BaseTool:
        """The registered `load_skill(name)` tool — §19.2's level-2 trigger."""
        middleware = self

        @tool
        def load_skill(name: str) -> str:
            """Load the full coaching instructions for one DMAIC phase.

            Call this when you need the detailed method for a phase — the
            field-by-field walk, the worked examples, the seven-step sequence
            for its computation tools. Pass the phase name: define, measure,
            analyse, improve or control. You start with descriptions only, so
            this is how you get the rest.
            """
            key = name.strip().lower().replace("dmaic-", "").replace("-phase", "")
            try:
                body = instructions(key)
            except SkillNotFound:
                return (f"There is no {name!r} skill. The five are: "
                        f"{', '.join(SKILL_DIRS)}.")
            if key not in middleware.loaded:
                middleware.loaded.append(key)
            logger.info("load_skill: level 2 loaded for %s (%d chars)",
                        key, len(body))
            return body

        return load_skill

    def before_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        """**Level 1.** Compose the catalogue — descriptions only (B1).

        Once per turn, for the same reason position 1 is: the five descriptions
        do not change within a turn, and `before_model` would re-send them on
        every tool round-trip.
        """
        self._catalogue = (
            "AVAILABLE COACHING SKILLS — descriptions only.\n"
            f"You are coaching the {self.phase} phase: its full instructions are "
            "in this message, above. The others are listed because a Belt's "
            "question often reaches forward or back — call load_skill(name) to "
            "read one of them in full.\n\n"
            f"{level_1_catalogue()}"
        )
        logger.info(
            "%s.skills: level 1 catalogue composed (%d chars, 5 descriptions); "
            "level 2 on demand", self.phase, len(self._catalogue),
        )
        return None

    async def abefore_agent(self, state: Any, runtime: Any) -> dict[str, Any] | None:
        return self.before_agent(state, runtime)

    # ── where level 1 actually reaches the coach ─────────────────────────

    def wrap_model_call(self, request: Any, handler: Any) -> Any:
        return handler(self._append_catalogue(request))

    async def awrap_model_call(self, request: Any, handler: Any) -> Any:
        return await handler(self._append_catalogue(request))

    def _append_catalogue(self, request: Any) -> Any:
        """Level 1 into the prompt, BELOW position 1's project state.

        **A catalogue that is composed and never delivered is not Level 1.**
        The first draft of this middleware logged that descriptions were
        "offered" and put them nowhere, which left the coach holding a
        `load_skill` tool with no idea what was loadable — the failure mode
        this project keeps naming, a mechanism that reports success while doing
        nothing. Found by 6.3's trace-check.

        Appended rather than prepended: position 1 is first by rule (S-C11 B4),
        and skills are instructions about method, not established project fact.

        **Content BLOCKS, never string concatenation** — §21 / CLAUDE.md §4.5,
        the rule step 2.6 applied across twenty sites. `.content` is
        `str | list[dict]`, so an f-string over a multi-part message writes
        ``"[{'type': 'text', ...}]"`` into the prompt with no error. Appending
        to `.content_blocks` is a list operation and cannot do that.

        **Position 1 runs first, so by the time this fires the system message
        is already multi-part** — which makes this the site where string
        concatenation would actually have bitten, not a hypothetical one.
        """
        if not self._catalogue:
            return request
        existing = request.system_message
        blocks = list(existing.content_blocks) if existing is not None else []
        # 6.46 (option A, founder ruling 2026-09-24) — THE CURRENT PHASE'S FULL
        # SCRIPT, ON EVERY MODEL CALL. §19.2's level 2 waited for the coach to
        # call `load_skill`, and it called it ZERO times in 30 traced turns. A
        # system-message block is never a tool result, so nothing enters the
        # conversation and the history does not grow by 7.6k tokens a turn.
        # The catalogue stays LAST.
        # 6.61 — SECTION 2 OF THE COACH'S INPUT (§19.1 v1.75): after section 1
        # (the rules), before section 3 (state), which position 1 composed;
        # appended when there is no section 3 (a stack without position 1).
        # Item 4: the opening (first turn only) and the CURRENT field's block
        # — high signal, not the whole 31k-character script every call.
        script = script_section(self.phase, self.focus_field, self.opening)
        section = [{"type": "text", "text": SECTION_SCRIPT},
                   {"type": "text", "text": script}]
        at = next((i for i, b in enumerate(blocks)
                   if str(b.get("text") or "").startswith(SECTION_STATE)), len(blocks))
        ordered = [*blocks[:at], *section, *blocks[at:]]
        if self.on_delivery is not None:
            # The headings of the message as it goes to the model — this is the
            # innermost of the two wraps, so what it sees is what is sent.
            self.on_delivery({**script_record(self.phase),
                              "delivered_part": ("opening + " if self.opening else "")
                              + (self.focus_field or "closing"),
                              "delivered_chars": len(script),
                              "sections": [str(b.get("text") or "").split("\n", 1)[0]
                                           for b in ordered
                                           if str(b.get("text") or "").startswith("## ")]})
        return request.override(
            system_message=SystemMessage(content_blocks=ordered)
        )


__all__ = [
    "DMAICSkillsMiddleware",
    "SKILLS_ROOT",
    "SKILL_DIRS",
    "LEVEL_1_TOKEN_BUDGET",
    "SkillNotFound",
    "frontmatter",
    "description",
    "instructions",
    "allowed_tools",
    "level_1_catalogue",
    "script_step",
]
