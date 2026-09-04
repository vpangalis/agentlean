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

import logging
import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import SystemMessage
from langchain_core.tools import BaseTool, tool

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

    def __init__(self, phase: str) -> None:
        super().__init__()
        if phase not in SKILL_DIRS:
            raise ValueError(
                f"Unknown phase {phase!r}. The five (§12) are: "
                f"{', '.join(SKILL_DIRS)}."
            )
        self.phase = phase
        self.loaded: list[str] = []
        self._catalogue: str = ""
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
            "Call load_skill(name) to read one in full. You are coaching the "
            f"{self.phase} phase, so that is the one to load first; the others "
            "are listed because a Belt's question often reaches forward or "
            "back.\n\n"
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
        return request.override(
            system_message=SystemMessage(
                content_blocks=[*blocks,
                                {"type": "text", "text": self._catalogue}],
            )
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
]
