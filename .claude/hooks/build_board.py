#!/usr/bin/env python3
"""Generate `agent-improve/docs/board.html` from the documents. Step 6.16.

    python .claude/hooks/build_board.py           # write the board
    python .claude/hooks/build_board.py --check   # parse only, write nothing

WHY THIS FILE EXISTS
--------------------
**The refactor board was hand-made in a chat and went stale the moment a
commit landed.** Five captions in this repository have already outlived the
lists they describe (`DECISIONS.md` Part AR3, plus the 2026-09-11 audit's
per-phase tool totals, which reached FOUR disagreeing figures). A hand-written
board is the one a founder reads, so it is the one that must not be typed.

**Every figure here traces to a line a human approved.** Four sources and
nothing else:

    Appendix D            every step, its status, zone, impact, and the total
    ARCHITECTURE.md       the `> **BUILT:**` markers - state and closing step
    ARCHITECTURE.md §66   the gap register, for blocked reasons
    git log               which steps landed - `refactor(arch-v2): commit X.Y`

**Reading nothing else is a constraint, not a description of one.** A
generator that reached into the CODE would report something no reviewer
ratified - that is `verify_built.py`'s job and it is a different job. Git
history is a ratified record rather than an inference from the tree: rule 1 of
the commit-msg guard refuses a malformed spine subject, so a commit subject is
the most reviewed artefact this project produces.

TWO OF THIS STEP'S OWN PREMISES WERE STALE WHEN IT WAS BUILT
------------------------------------------------------------
Recorded because the step is about captions outliving their lists, and its own
specification had done exactly that between being written and being built:

1. **It named `ARCHITECTURE_STATUS.md` as the second source.** That file was
   archived on 2026-09-10 and its tables became the `> **BUILT:**` markers
   inside `ARCHITECTURE.md` (§55.2). The markers are read there instead, and
   sub-step 2's "parseable closer" landed on them as a trailing
   `**closes:** [X.Y]` / `[none]` token.
2. **Its lane table said `BUILDING NOW | the ▶ cursor` and
   `DONE | Appendix D says done`.** Both are gone - the cursor was deleted and
   the status column stopped carrying `done`, because completion is git's fact
   and a status cell claiming it is a second hand-maintained source. Lanes are
   derived below from git log plus the same next-step rule
   `session-start-context.py` uses, so the board and the session banner cannot
   disagree about what is next.

Python 3.11+, standard library only. Fail-soft: see `main`.
"""
from __future__ import annotations

import html
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = subprocess.run(["git", "rev-parse", "--show-toplevel"],
                      capture_output=True, text=True).stdout.strip() or "."
PROJECT = os.path.join(ROOT, "agent-improve")
PROCEDURE = os.path.join(PROJECT, "docs", "REFACTORING_PROCEDURE.md")
ARCH = os.path.join(PROJECT, "ARCHITECTURE.md")
OUT = os.path.join(PROJECT, "docs", "board.html")

# ── The zone↔block mapping, AS DATA. ──────────────────────────────────────
#
# Step 6.16: "Declare the table in the generator as DATA, not as a comment, so
# adding a block or a zone raises a KeyError rather than silently unmapping a
# step." Container 1 is drawn from the blocks and container 2 is coloured by
# zone; without a declared mapping the two cannot cross-highlight, which is
# most of what a board is for.
#
# NOT 1:1 - a 3→1 collapse and a 1→2 split. Eight Level-1 blocks, seven zones.
BLOCKS: dict[str, str] = {
    "1": "API surface",
    "2": "Supervisor graph",
    "3": "Phase subgraphs",
    "4": "Coaching agent",
    "5": "Middleware",
    "6": "Tools and knowledge",
    "7": "Validation, gates, escalation",
    "8": "Persistence and cross-cutting",
}
ZONE_TO_BLOCKS: dict[str, tuple[str, ...]] = {
    "UI":    ("1",),
    "SUP":   ("2",),
    "PHASE": ("3",),
    "COACH": ("4", "5", "6"),          # the 3→1 collapse
    "GATE":  ("7",),
    "STORE": ("8",),                   # block 8, persistence half
    "OPS":   ("8",),                   # block 8, cross-cutting half
}
# Where each BUILT marker lives: (block, zone). **Both, explicitly.**
#
# An earlier cut stored only the zone and let container 1 place the marker in
# every block that zone spans - so each COACH marker rendered three times
# (blocks 4, 5 and 6) and container 1 reported 17 open markers against a true
# 11. **A 3→1 collapse read backwards is a 1→3 duplication**, which is the
# trap the step's own "NOT 1:1" warning is about. The pair is declared here so
# neither direction is inferred.
MARKER_HOME: dict[str, tuple[str, str]] = {
    "§16":    ("8", "STORE"),
    "§19.1":  ("5", "COACH"),
    "§19.2":  ("5", "COACH"),
    "§19.3":  ("5", "COACH"),
    "§19.4":  ("5", "COACH"),
    "§19.5":  ("5", "COACH"),
    "§19.6":  ("5", "COACH"),   # gate-ish work, but structurally middleware
    "§19.7":  ("5", "COACH"),   # gate-ish work, but structurally middleware
    "§19.8":  ("5", "COACH"),   # gate-ish work, but structurally middleware
    "§17":    ("4", "COACH"),
    "§26":    ("4", "COACH"),
    "§30":    ("6", "COACH"),
    "§33":    ("7", "GATE"),
    "§34":    ("7", "GATE"),
    "§44":    ("8", "OPS"),
    "§46":    ("8", "OPS"),
    "§49":    ("1", "UI"),
    "§50.1":  ("1", "UI"),
    "§51":    ("8", "OPS"),
    "§53":    ("8", "OPS"),
    "§58.5":  ("4", "COACH"),        # S-C05 · CoachingResponse

    # ── MAIN: the three items the per-phase panel's first row covers. ───
    "§15":    ("2", "SUP"),          # the supervisor graph
    "§57.2":  ("2", "SUP"),          # S-C01 · SupervisorState
    "§58.2":  ("3", "PHASE"),        # S-C02 · PhaseState

    # ── Per-phase (§39.N.*). All block 3; the PANEL groups them by phase. ─
    "§39.1": ("3", "PHASE"), "§39.1.2": ("3", "PHASE"), "§39.1.7": ("3", "PHASE"),
    "§39.2.2": ("3", "PHASE"), "§39.2.7": ("3", "PHASE"), "§39.2.10": ("3", "PHASE"),
    "§39.3.2": ("3", "PHASE"), "§39.3.7": ("3", "PHASE"), "§39.3.10": ("3", "PHASE"),
    "§39.4.2": ("3", "PHASE"), "§39.4.7": ("3", "PHASE"), "§39.4.10": ("3", "PHASE"),
    "§39.5.2": ("3", "PHASE"), "§39.5.7": ("3", "PHASE"), "§39.5.10": ("3", "PHASE"),

    # ── The 2026-09-11 coverage sweep: every ratified section now ends in a
    #    marker or a NOT-MARKABLE note, so the markers that were missing are
    #    here. Block and zone are declared, not inferred from the number.
    "§7": ("3", "PHASE"),         # field typing law — the gate schemas
    "§8": ("8", "STORE"),         # checkpointer / store split
    "§9": ("8", "STORE"),         # the Store and the boundary mappers
    "§10": ("8", "STORE"),        # Azure Blob
    "§11": ("8", "OPS"),          # step_log
    "§13": ("3", "PHASE"),        # the five subgraph nodes
    "§14": ("3", "PHASE"),        # node contract
    "§18": ("4", "COACH"),        # create_agent
    "§21": ("4", "COACH"),        # LLM roles and the factory
    "§22": ("4", "COACH"),        # prompts
    "§23": ("6", "COACH"),        # the three indexes
    "§24": ("6", "COACH"),        # the rag_lookup_* tools
    "§25": ("6", "COACH"),        # multi-query + RRF
    "§27": ("6", "COACH"),        # retrieval failure semantics
    "§29": ("6", "COACH"),        # the data channel and the universal eight
    "§31": ("6", "COACH"),        # tool arg schemas
    "§32": ("4", "COACH"),        # SKILL.md
    "§35": ("7", "GATE"),         # two tiers + warning
    "§36": ("7", "GATE"),         # the two graders
    "§37": ("7", "GATE"),         # contradiction + re-approval cascade
    "§38": ("7", "GATE"),         # escalation
    "§40": ("7", "GATE"),         # the five {Phase}Output schemas
    "§41": ("7", "GATE"),         # structured dict fields
    "§42": ("7", "GATE"),         # cross-phase reference fields
    "§47": ("8", "STORE"),        # disconnect policy
    "§48": ("8", "OPS"),          # structured errors
    "§52": ("7", "GATE"),         # evaluation and regression

    # Spec entries that turned out NOT to be covered by their Part's alias
    # (checked 2026-09-11 rather than assumed).
    "§63.6": ("7", "GATE"),       # S-C32 · cross-phase reference keys
    "§63.9": ("7", "GATE"),       # S-C39 · phase_metrics
    "§69.7": ("6", "COACH"),      # the deliberately absent Measure chart tool
}

#: The per-phase panel's six rows. **MAIN is exactly three items** (founder,
#: 2026-09-11): the two state classes and the supervisor graph - all verified
#: exact, so this row should read green and stay that way.
MAIN_MARKERS = {"§15", "§57.2", "§58.2"}
PHASE_ROWS = [("MAIN", None), ("Define", "1"), ("Measure", "2"),
              ("Analyse", "3"), ("Improve", "4"), ("Control", "5")]


def phase_of(section: str) -> str | None:
    """Which panel row a marker belongs to, or None if it is cross-cutting.

    Derived from the section number - §39.N.* is phase N - so a new §39.x
    marker joins the panel with no second list to update.
    """
    if section in MAIN_MARKERS:
        return "MAIN"
    m = re.match(r"^§39\.(\d)", section)
    if not m:
        return None
    return {digit: name for name, digit in PHASE_ROWS[1:]}.get(m.group(1))
for _sec, (_b, _z) in MARKER_HOME.items():
    BLOCKS[_b]                                  # KeyError if the block is gone
    if _b not in ZONE_TO_BLOCKS[_z]:            # KeyError if the zone is gone
        raise KeyError(f"{_sec}: block {_b} is not in zone {_z}")

UNAVAILABLE = {"blocked", "gated", "external"}

# **`Seq` is column 1 and is what orders the board** (2026-09-11). The step
# number is a stable identifier. This regex is ANCHORED where the other two
# readers' are not, so adding the column broke it immediately and fail-soft -
# which is how a generator should react to its input changing shape.
_ROW = re.compile(
    r"^\| (?P<seq>\d+) \| \*\*Commit (?P<step>\d+\.\d+)\*\* \| (?P<title>.*?) \| ?(?P<status>\w*) ?"
    r"\| (?P<zone>\w+) \| (?P<scope>\w+) \| (?P<impact>.*?) \|$", re.M)
_SPINE = re.compile(r"refactor\(arch-v2\):\s*commit\s+(?P<step>\d+\.\d+)")
_PRECON = re.compile(r"^\| \*\*Precondition\*\* \| (?P<p>.*?) \|$", re.M)
_STEP_H = re.compile(r"^## Step (?P<step>\d+\.\d+) — (?P<title>.*)$", re.M)
_MARKER = re.compile(r"^> \*\*BUILT:\*\* (?P<body>.*)$", re.M)
_CLOSES = re.compile(r"\*\*closes:\*\* `\[(?P<tok>[^\]]*)\]`")
_GAP = re.compile(r"^\| \*\*(?P<gap>G-\d+)\*\* \| (?P<desc>.*?) \|", re.M)


def _ver(step: str) -> tuple[int, ...]:
    return tuple(int(p) for p in step.split("."))


def read_appendix_d() -> list[dict]:
    """Every step row, bounded to Appendix D so a stray `| **Commit X.Y** |`
    written inside a step's prose cannot enter the board."""
    text = Path(PROCEDURE).read_text(encoding="utf-8")
    lines = text.splitlines()
    start = next(i for i, ln in enumerate(lines)
                 if ln.startswith("## ") and "Appendix D" in ln)
    end = next((j for j in range(start + 1, len(lines))
                if lines[j].startswith("## ")), len(lines))
    rows = [m.groupdict() for m in _ROW.finditer("\n".join(lines[start:end]))]
    if not rows:
        raise ValueError("Appendix D found but no rows matched the row format")
    for r in rows:
        r["seq"] = int(r["seq"])
    seqs = [r["seq"] for r in rows]
    if len(set(seqs)) != len(seqs):
        dupes = sorted({n for n in seqs if seqs.count(n) > 1})
        raise ValueError(f"duplicate Seq values in Appendix D: {dupes}")
    return rows


_BAND = re.compile(
    r"^\| (?P<id>[A-D]) \| (?P<lo>\d+)–(?P<hi>\d+) \| (?P<name>[^|]+?) \| (?P<delivers>.*?) \|$",
    re.M)
# **Two forms, because the procedure uses two.** Most steps write
# `**Done when:** ...`; 6.17 and 6.14 use a `### Done when` heading with the
# text beneath. Matching only the first silently reported those steps as
# having no completion criterion, which is indistinguishable from the steps
# that genuinely have none - and the difference is the finding.
_DONE = re.compile(
    r"^(?:\*\*Done when[^:]*:?\*\*|### Done when\s*$)\s*(?P<text>.*)",
    re.M | re.S)


_HEAD = re.compile(r"^#{2,4} (?P<num>\d+(?:\.\d+)*)\.?\s+(?P<title>.+?)\s*$", re.M)
#: Words a heading can open with that add nothing to a short label.
_TRIM = re.compile(r"^(?:The|A|An)\s+", re.I)


def read_section_titles() -> dict[str, str]:
    """`§N -> a short name`, from the headings themselves.

    **PART 1's rule: no bare number anywhere the board renders.** A reader who
    has to hold "§49" in their head to know it means the API surface is doing
    the document's work for it, and the board exists so they do not have to.

    Titles come from the headings and are never written here. A heading with
    no usable text is returned as `""`, and `main --check` reports it — a
    section nobody could name is a finding about the section.
    """
    out: dict[str, str] = {}
    for m in _HEAD.finditer(Path(ARCH).read_text(encoding="utf-8")):
        t = m.group("title")
        t = re.sub(r"\*\*|`|—\s*$", "", t).strip()
        # "39.2.7 State parameters — Measure's use of PhaseState" -> keep it all;
        # "57.2 SAMPLE 1 — CLASS TEMPLATE — S-C01 SupervisorState" -> last part.
        if t.count(" — ") >= 2:
            t = t.split(" — ")[-1].strip()
        t = _TRIM.sub("", t)
        out.setdefault(f"§{m.group('num')}", t[:58])
    return out


_COMPLETENESS = re.compile(
    r"^\| (?P<group>[^|]+?) \| `(?P<sec>§[\d.x]+)` \| (?P<scope>SHARED|PHASE) \| "
    r"(?P<at>`§[\d.]+`|—) \|$", re.M)


def read_completeness_set() -> list[dict]:
    """§55.3's table — what ONE phase traverses end to end.

    **This is the denominator, and it lives in the document.** The board used
    to show each phase as a fraction of the three markers NAMED after it,
    which read "Define 1/3" and measured the wrong thing entirely: the
    sections named after a phase, not the sections a phase depends on.
    """
    text = Path(ARCH).read_text(encoding="utf-8")
    i = text.index("### 55.3 The phase completeness set")
    j = text.index("## 56. Amendment procedure", i)
    rows = [m.groupdict() for m in _COMPLETENESS.finditer(text[i:j])]
    if not rows:
        raise ValueError("§55.3 found but no rows matched the row format")
    for r in rows:
        r["at"] = "" if r["at"] == "—" else r["at"].strip("`")
        r["group"] = r["group"].strip()
    return rows


def phase_completeness(items: list[dict], markers: list[dict]) -> dict:
    """`phase -> [rows]`, each item carrying a state for that phase.

    **Roll-up, not exact match.** An item's state is the WORST state among the
    markers at or beneath its section: §19 has no marker of its own but eight
    beneath it, and §39.x resolves per phase to §39.N plus its subsections. A
    `Measured at` alias redirects the lookup where an item is specified in one
    place and marked in another (§5 → §57.2, §20 → §58.5) — without it those
    rows would read UNMEASURED, which would be false.

    **No marker anywhere is UNMEASURED, and UNMEASURED IS NOT A PASS.** A
    blank and a green look identical at a glance and mean opposite things, so
    they render differently and only `built` counts toward the fraction.
    """
    rank = {"built": 0, "defect": 1, "unbuilt": 2, "blocked": 3}
    by_sec: dict[str, list[dict]] = {}
    for m in markers:
        by_sec.setdefault(m["section"], []).append(m)

    def resolve(sec: str) -> list[dict]:
        hit = list(by_sec.get(sec, []))
        for k, v in by_sec.items():
            if k.startswith(sec + "."):
                hit += v
        return hit

    out: dict[str, list[dict]] = {}
    for name, digit in PHASE_ROWS[1:]:
        rows = []
        for it in items:
            sec = f"§39.{digit}" if it["sec"] == "§39.x" else it["sec"]
            found = resolve(it["at"] or sec)
            if found:
                worst = max(found, key=lambda m: rank[m["state"]])
                state, closes = worst["state"], worst["closes"]
            else:
                state, closes = "unmeasured", []
            rows.append({**it, "sec_resolved": sec, "state": state,
                         "closes": closes, "n_markers": len(found)})
        out[name] = rows
    return out


_VERIFY = re.compile(r"^\| \*\*Verify\*\* \| (?P<v>.*?) \|$", re.M)


def read_done_when_full() -> dict[str, str]:
    """`step -> its Done-when, VERBATIM`, flattened but not summarised.

    The bubble shows what the procedure actually says. A paraphrase would be a
    fourth copy of a sentence that already exists, and the one nobody edits.
    """
    text = Path(PROCEDURE).read_text(encoding="utf-8")
    heads = [(m.group("step"), m.start()) for m in _STEP_H.finditer(text)]
    out: dict[str, str] = {}
    for idx, (step, pos) in enumerate(heads):
        end = heads[idx + 1][1] if idx + 1 < len(heads) else len(text)
        m = _DONE.search(text, pos, end)
        if not m:
            continue
        body = text[m.start("text"):m.start("text") + 1400]
        # Stop at the next block: a heading, a blockquote, or a blank line
        # followed by bold - the shapes a Done-when paragraph ends on.
        body = re.split(r"\n\s*\n(?=[>#*\|]|\*\*)", body)[0]
        body = re.sub(r"\s+", " ", re.sub(r"\*\*|`|\*", "", body)).strip()
        out[step] = body
    return out


def read_verify() -> dict[str, str]:
    """`step -> its Verify method`, from each step's own table."""
    text = Path(PROCEDURE).read_text(encoding="utf-8")
    heads = [(m.group("step"), m.start()) for m in _STEP_H.finditer(text)]
    out: dict[str, str] = {}
    for idx, (step, pos) in enumerate(heads):
        end = heads[idx + 1][1] if idx + 1 < len(heads) else len(text)
        m = _VERIFY.search(text, pos, end)
        if m:
            out[step] = re.sub(r"`|\*\*", "", m.group("v")).strip()
    return out


#: The recurring subsection topics, matched on a distinctive phrase from the
#: heading. Declared because heading wording varies ("Two movements" vs
#: "SIPOC -> the detailed process map"); the PHRASES are read from the
#: headings, only the vocabulary is here.
_TOPICS = ("purpose", "ordered field list", "metric registry", "movements",
           "sipoc", "tools bound", "conditions", "state parameters",
           "metric literacy", "gate, storage", "skill.md content",
           "cross-phase reads")


def _topic(title: str) -> str:
    low = title.lower()
    return next((t for t in _TOPICS if t in low), low[:26])


def read_phase_subsections() -> dict[str, dict]:
    """Per phase: its subsections, and which CANONICAL topics it lacks.

    **Counted by topic, not by subtraction**, and the difference is the whole
    point for Define. It has 8 subsections against the other four's 12, so
    arithmetic says "4 missing" - but its eight are NOT the same eight. Three
    are Define-only (the composed-problem-statement rule, the `team`
    structure, SIPOC handling), so **six canonical topics have no Define
    section at all**: the metric registry, tools bound to the phase,
    conditions, state parameters, metric literacy, and cross-phase reads.

    Canonical = a topic all four of Measure/Analyse/Improve/Control carry. A
    topic only some carry is not a standard this document holds Define to.
    """
    text = Path(ARCH).read_text(encoding="utf-8")
    subs: dict[str, dict[str, str]] = {}
    for m in re.finditer(r"^#### 39\.(\d)\.(\d+)\s+(.+?)\s*$", text, re.M):
        subs.setdefault(m.group(1), {})[m.group(2)] = re.sub(
            r"\*\*|`", "", m.group(3))

    seen: dict[str, set] = {}
    for ph in "2345":
        for title in subs.get(ph, {}).values():
            seen.setdefault(_topic(title), set()).add(ph)
    canonical = {t for t, who in seen.items() if len(who) == 4}

    out: dict[str, dict] = {}
    for ph, items in subs.items():
        mine = {_topic(t) for t in items.values()}
        out[f"§39.{ph}"] = {
            "n": len(items),
            "canonical": len(canonical),
            "missing": sorted(canonical - mine),
        }
    return out


def read_bands() -> list[dict]:
    """Appendix D's band table - the PLAN, as data.

    **The Seq ranges live in the document, not here.** Hardcoding them would
    make the plan a thing only a developer can restate, which is the opposite
    of what a board is for; the founder edits the band and the board follows.
    """
    text = Path(PROCEDURE).read_text(encoding="utf-8")
    i = text.index("### The bands")
    j = text.index("| Seq | Step |", i)
    bands = [m.groupdict() for m in _BAND.finditer(text[i:j])]
    if not bands:
        raise ValueError("band table found but no rows matched")
    for b in bands:
        b["lo"], b["hi"] = int(b["lo"]), int(b["hi"])
        # The board renders text, not markdown — strip emphasis here rather
        # than asking the founder to write the band table without it.
        b["delivers"] = re.sub(r"\*\*|`|\*", "", b["delivers"]).strip()
        b["name"] = re.sub(r"\*\*|`|\*", "", b["name"]).strip()
    return bands


def read_done_when() -> dict[str, str]:
    """`step -> the first sentence of its Done-when`.

    **From the procedure, never written fresh** (founder, 2026-09-11). A card
    that restates its own title tells a reader nothing; the Done-when is the
    step's own statement of what it has to achieve, and it is already reviewed.
    """
    text = Path(PROCEDURE).read_text(encoding="utf-8")
    heads = [(m.group("step"), m.start()) for m in _STEP_H.finditer(text)]
    out: dict[str, str] = {}
    for idx, (step, pos) in enumerate(heads):
        end = heads[idx + 1][1] if idx + 1 < len(heads) else len(text)
        m = _DONE.search(text, pos, end)
        if not m:
            continue
        # Flatten the wrap, strip markdown, and take the first sentence.
        body = re.sub(r"\s+", " ", text[m.start("text"):m.start("text") + 900])
        body = re.sub(r"\*\*|`|\*", "", body)
        cut = re.search(r"(?<=[a-z0-9\)\]])[.;] (?=[A-Z§`])", body)
        first = body[:cut.start() + 1] if cut else body.split(". ")[0] + "."
        out[step] = first.strip()
    return out


def read_preconditions() -> dict[str, str]:
    """`step -> precondition cell`, from each step's own table in Part 1-10."""
    text = Path(PROCEDURE).read_text(encoding="utf-8")
    heads = [(m.group("step"), m.start()) for m in _STEP_H.finditer(text)]
    out: dict[str, str] = {}
    for idx, (step, pos) in enumerate(heads):
        end = heads[idx + 1][1] if idx + 1 < len(heads) else len(text)
        m = _PRECON.search(text, pos, end)
        out[step] = m.group("p").strip() if m else ""
    return out


def landed_steps() -> set[str]:
    """Steps with a `refactor(arch-v2): commit X.Y` subject in git log.

    Intersected with Appendix D by the caller: history carries five commits
    from before that table existed (0.1, 1.1, 1.2, 2.1, 2.2), and a step that
    landed under another subject - 9.0 as `feat(knowledge):` - is invisible
    here by construction, which is what its EXTERNAL status is for.
    """
    log = subprocess.run(["git", "log", "--pretty=%s"], cwd=ROOT,
                         capture_output=True, encoding="utf-8",
                         errors="replace").stdout
    return {m.group("step") for m in _SPINE.finditer(log)}


def read_markers() -> list[dict]:
    """The `> **BUILT:**` lines: state, the section they sit under, closer."""
    text = Path(ARCH).read_text(encoding="utf-8")
    lines = text.splitlines()
    sec, spec_id = "?", ""
    out = []
    for i, ln in enumerate(lines):
        h = re.match(r"^#{2,4} (?P<n>\d+(?:\.\d+)*)\s*(?P<spec>S-[CF]\d+)?", ln)
        if h:
            sec = h.group("n")
            spec_id = h.group("spec") or ""
        m = _MARKER.match(ln)
        if not m:
            continue
        body = m.group("body")
        state = ("built" if body.startswith("✅") else
                 "defect" if body.startswith("⚠") else
                 "blocked" if body.startswith("⛔") else "unbuilt")
        tok = _CLOSES.search(body)
        out.append({
            "section": f"§{sec}",
            # Both names for the same item: §66's rows cite S-C05 where the
            # heading is §58.5, and an attribution that knew only one would
            # silently miss every spec-layer gap.
            "aliases": {f"§{sec}", spec_id} - {""},
            "state": state,
            "closes": [] if not tok or tok.group("tok") == "none"
                      else [t.strip() for t in tok.group("tok").split(",")],
            "text": re.sub(r"\s*· \*\*closes:\*\*.*$", "", body),
        })
    return out


def read_gaps() -> dict[str, dict]:
    """`G-nn -> {desc, refs, closed}` from §66.

    `refs` is the row's last column - the sections the gap affects - and is
    what attributes a gap to a BUILT marker. `closed` is membership of
    §66.6, so a resolved gap never appears against a live defect.
    """
    text = Path(ARCH).read_text(encoding="utf-8")
    i = text.index("## 66. The SPEC-GAP register")
    closed_at = text.find("### 66.6 Closed", i)
    closed_end = text.find("### 66.7", closed_at) if closed_at > 0 else -1
    closed = set(re.findall(r"G-\d+", text[closed_at:closed_end])) \
        if closed_at > 0 else set()

    out: dict[str, dict] = {}
    for m in re.finditer(r"^\| \*\*(?P<gap>G-\d+)\*\* \|(?P<body>.*)\|\s*$",
                         text[i:], re.M):
        cells = m.group("body").split("|")
        desc = re.sub(r"\*\*|`", "", cells[0]).strip()
        refs = {r.strip() for r in re.split(r"[,·]", cells[-1])
                if r.strip()} if len(cells) > 1 else set()
        out[m.group("gap")] = {
            # **Not truncated here.** The first cut stored `desc[:240]`, which
            # cut off the step numbers G-49 names - so the bubble's "blocks"
            # line came back empty for the one gap that blocks four steps.
            # Truncation is a rendering decision and belongs at the render.
            "desc": desc,
            "refs": {r.strip("`") for r in refs},
            "closed": m.group("gap") in closed,
        }
    return out


def assign_lanes(rows: list[dict], landed: set[str],
                 precon: dict[str, str]) -> None:
    """Lane per step. **Nothing anywhere declares a lane** (6.16 sub-step 4).

    A declared lane is one more caption to keep current; a derived one cannot
    disagree with the table it came from.

    `BUILDING NOW` is the next-step pointer, computed with the SAME rule
    `session-start-context.py` uses - lowest Appendix D row whose status is
    not blocked/gated/external and whose version key is above the highest
    landed spine step - so the board and the session banner cannot disagree.
    """
    table = {r["step"] for r in rows}
    done = landed & table

    # **No watermark, and ordering is by `Seq`** (2026-09-11). The pointer is
    # the lowest-`Seq` row that has neither landed nor been made unavailable -
    # the same rule `session-start-context.py` uses, so the board and the
    # session banner cannot disagree about what is next. A row BELOW the last
    # completed one is reachable, which is what the old "strictly greater than"
    # rule made impossible and what cost a renumber on 2026-09-11.
    available = [(r["seq"], r["step"]) for r in rows
                 if r["status"].lower() not in UNAVAILABLE
                 and r["step"] not in done]
    pointer = min(available)[1] if available else None

    for r in rows:
        step, status = r["step"], r["status"].lower()
        if step in done:
            r["lane"] = "DONE"
        elif status in UNAVAILABLE:
            r["lane"] = "BLOCKED"
        elif step == pointer:
            r["lane"] = "BUILDING NOW"
        else:
            p = precon.get(step, "")
            names = re.findall(r"\b(\d+\.\d+)\b", p)
            unmet = [n for n in names if n in table and n not in done]
            blocked_on = "blocked on" in p.lower()
            r["lane"] = "QUEUED" if (unmet or blocked_on) else "READY"
        r["precondition"] = precon.get(step, "")


LANES = ["BUILDING NOW", "READY", "QUEUED", "BLOCKED", "DONE"]
LANE_CLASS = {"BUILDING NOW": "now", "READY": "ready", "QUEUED": "queued",
              "BLOCKED": "blocked", "DONE": "done"}


def render(rows: list[dict], markers: list[dict], gaps: dict[str, dict],
           landed: set[str], bands: list[dict], done_when: dict[str, str],
           titles: dict[str, str], comp_set: list[dict],
           done_when_full: dict[str, str], verify: dict[str, str],
           precon: dict[str, str]) -> str:
    """The board: the PLAN first, readiness second.

    **Bands replaced lanes as the organising axis on 2026-09-11**, by founder
    ruling, and the reason was a specific misreading: 11.1 and 11.2 sat in
    READY beside 6.18 - correct on readiness, and actively misleading about
    what to do next, because cleanup steps have no unmet preconditions and so
    look identical to the next thing that matters. **Readiness is a property
    of a step, not a plan**, so it is a badge now.
    """
    e = html.escape
    title_of = {r["step"]: r["title"] for r in rows}

    def named(sec: str) -> str:
        """`§49 — the API surface`. Never a bare number (PART 1)."""
        t = titles.get(sec, "")
        return f"{e(sec)} — {e(t)}" if t else f"{e(sec)} <i>(unnamed section)</i>"

    def closes_named(m: dict) -> str:
        """`6.20 write paths` — the step number with a short name beside it."""
        out = []
        for st in m["closes"]:
            t = title_of.get(st, "")
            short = " ".join(re.sub(r"[`—§]", "", t).split()[:3]) if t else ""
            out.append(f"{st} {short}".strip())
        return ", ".join(out)

    def step_named(step: str) -> str:
        t = title_of.get(step, "")
        return f"{e(step)} — {e(t)}" if t else e(step)

    STATE_WORDS = {"built": "built", "defect": "built and wrong",
                   "unbuilt": "not built", "blocked": "blocked",
                   "unmeasured": "unmeasured — not a pass"}
    glyph = {"built": "\u2705", "defect": "\u26a0\ufe0f", "unbuilt": "\u2610",
             "blocked": "\u26d4", "unmeasured": "?"}
    comp = phase_completeness(comp_set, markers)
    marker_of = {m["section"]: m for m in markers}
    seq_of_step = {r["step"]: r["seq"] for r in rows}
    band_of_step = {}
    for r in rows:
        b = next((x for x in bands if x["lo"] <= r["seq"] <= x["hi"]), None)
        if b:
            band_of_step[r["step"]] = b

    def bub(*parts: str) -> str:
        """A bubble, as an escaped attribute. Last part is always the source."""
        return e("".join(parts), quote=True)

    def src(doc: str, where: str) -> str:
        return f'<div class="bsrc">source: {e(doc)} \u00b7 {e(where)}</div>'

    def step_bubble(step: str) -> str:
        t = title_of.get(step, "")
        b = band_of_step.get(step)
        dw = done_when_full.get(step)
        pre = precon.get(step) or "\u2014"
        vfy = verify.get(step) or "\u2014"
        body = [f'<div class="bt">{e(step)} \u2014 {e(t)}</div>']
        if b:
            body.append(f'<div class="br"><span>band</span>{e(b["id"])} \u00b7 '
                        f'{e(b["name"])} \u2014 {e(b["delivers"])}</div>')
        if dw:
            body.append(f'<div class="br"><span>done when</span>{e(dw)}</div>')
        else:
            body.append('<div class="br bad"><span>done when</span>'
                        'no Done-when in the procedure \u2014 nothing states what '
                        'this step has to achieve</div>')
        body.append(f'<div class="br"><span>precondition</span>{e(pre)}</div>')
        body.append(f'<div class="br"><span>verify</span>{e(vfy)}</div>')
        body.append(src("REFACTORING_PROCEDURE.md",
                        f"Step {step} \u00b7 Appendix D"))
        return "".join(body)

    def section_bubble(sec: str, scope: str) -> str:
        m = marker_of.get(sec)
        t = titles.get(sec, "")
        body = [f'<div class="bt">{e(sec)} \u2014 {e(t)}</div>']
        st = m["state"] if m else "unmeasured"
        body.append(f'<div class="br"><span>state</span>{glyph[st]} '
                    f'{e(STATE_WORDS[st])}</div>')
        if m:
            why = re.sub(r"\s+", " ", re.sub(r"\*\*|`|>", "", m["text"])).strip()
            body.append(f'<div class="br"><span>why</span>{e(why[:520])}</div>')
            if m["closes"]:
                cl = ", ".join(f'{c} \u2014 {title_of.get(c, "")}'.strip(" \u2014")
                               for c in m["closes"])
                body.append(f'<div class="br"><span>closes</span>{e(cl)}</div>')
            elif st != "built":
                # A BUILT item needs no closing step; only an open one does,
                # and saying "no step owns this" on finished work reads as a
                # defect that is not there.
                body.append('<div class="br bad"><span>closes</span>'
                            'no step owns this</div>')
        else:
            body.append('<div class="br bad"><span>closes</span>'
                        'nothing marks it, so nothing measures it</div>')
        # Hoisted: Python 3.11 forbids a backslash inside an f-string
        # EXPRESSION, and these two strings carry an escaped em dash.
        scope_words = ("SHARED \u2014 every phase traverses it"
                       if scope == "SHARED" else "PHASE \u2014 per phase")
        body.append(
            '<div class="br"><span>scope</span>' + scope_words + "</div>")
        body.append(src("ARCHITECTURE.md", f"{sec} \u00b7 \u00a755.3"))
        return "".join(body)

    def gap_bubble(g: str) -> str:
        v = gaps.get(g, {})
        desc = re.sub(r"\s+", " ", v.get("desc", ""))[:340]
        blocks = [r["step"] for r in rows
                  if re.search(rf"\b{re.escape(r['step'])}\b", v.get("desc", ""))]
        body = [f'<div class="bt">{e(g)}</div>',
                f'<div class="br"><span>what it is</span>{e(desc)}</div>']
        if blocks:
            body.append('<div class="br"><span>blocks</span>'
                        + e(", ".join(f'{b} \u2014 {title_of.get(b, "")}'.strip(" \u2014")
                                      for b in blocks[:6])) + "</div>")
        body.append(src("ARCHITECTURE.md", f"\u00a766 \u00b7 the SPEC-GAP register"))
        return "".join(body)

    def gnums(m: dict) -> str:
        hits = [g for g, v in gaps.items()
                if not v["closed"] and (v["refs"] & m["aliases"])]
        return ", ".join(sorted(hits, key=lambda g: -int(g.split("-")[1])))

    by_seq = sorted(rows, key=lambda r: r["seq"])
    seq_of = {r["step"]: r["seq"] for r in rows}
    pointer = next((r["step"] for r in rows if r["lane"] == "BUILDING NOW"), None)

    n_done, n_all = sum(1 for r in rows if r["lane"] == "DONE"), len(rows)
    pct = round(100 * n_done / n_all)
    _done_rows = [r for r in rows if r["lane"] == "DONE"]
    last_spine = (max(_done_rows, key=lambda r: r["seq"])["step"]
                  if _done_rows else "none")

    # ── health panel: counts from the markers, G-numbers from the register ──
    built = [m for m in markers if m["state"] == "built"]
    defective = [m for m in markers if m["state"] == "defect"]
    unbuilt = [m for m in markers if m["state"] in ("unbuilt", "blocked")]

    health = []
    for title, items, cls, note in (
        ("Built", built, "ok", "exists and works as specified"),
        ("Built and defective", defective, "warn",
         "live code, doing something other than what is specified"),
        ("Not started", unbuilt, "none",
         "absent \u2014 nothing runs, nothing misbehaves"),
    ):
        shown = sorted(items, key=lambda m: m["section"])[:14]
        chips = "".join(
            f'<span class="hchip">{named(m["section"])}'
            + (f' <b>{e(gnums(m))}</b>' if gnums(m) else "") + "</span>"
            for m in shown)
        if len(items) > len(shown):
            chips += f'<span class="hchip">+{len(items) - len(shown)} more</span>'
        health.append(
            f'<div class="hcard {cls}"><div class="hn">{len(items)}</div>'
            f'<div class="ht">{title}</div><div class="hnote">{e(note)}</div>'
            f'<div class="hchips">{chips or "&mdash;"}</div></div>')

    # ── PART 2: the current SLICE, not the current step ────────────────────
    def band_of(seq: int) -> dict | None:
        return next((b for b in bands if b["lo"] <= seq <= b["hi"]), None)

    cur = band_of(seq_of[pointer]) if pointer else bands[0]
    in_cur = [r for r in by_seq if cur["lo"] <= r["seq"] <= cur["hi"]]
    cur_done = [r for r in in_cur if r["lane"] == "DONE"]
    cur_left = [r for r in in_cur if r["lane"] != "DONE"]

    slice_rows = []
    for r in cur_left:
        dw = done_when.get(r["step"])
        goal = (f'<div class="goal">{e(dw)}</div>' if dw else
                '<div class="goal none">no Done-when in the procedure \u2014 '
                'nothing states what this step has to achieve</div>')
        mark = ' \u25b6' if r["step"] == pointer else ""
        slice_rows.append(
            f'<li class="{"cursor" if r["step"] == pointer else ""}"'
            f' data-b="{bub(step_bubble(r["step"]))}">'
            f'<div class="sh"><b>{e(r["step"])}{mark}</b> {e(r["title"])}'
            f'<span class="badge {LANE_CLASS[r["lane"]]}">{e(r["lane"])}</span></div>'
            f'{goal}</li>')

    # ── the other bands, one summary line each ─────────────────────────────
    others = []
    for b in bands:
        if b is cur:
            continue
        mine = [r for r in by_seq if b["lo"] <= r["seq"] <= b["hi"]]
        left = [r for r in mine if r["lane"] != "DONE"]
        blocked = [r for r in mine if r["lane"] == "BLOCKED"]
        waits = (f'waits on {", ".join(e(r["step"]) for r in blocked)}'
                 if blocked else f'waits on band {e(cur["id"])}')
        others.append(
            f'<div class="obandrow"><b>{e(b["id"])} \u00b7 {e(b["name"].strip())}</b>'
            f'<span class="on">{len(left)} remaining</span>'
            f'<div class="od">{e(b["delivers"])}</div>'
            f'<div class="ow">{waits}</div></div>')

    # ── PART 1: the four bands, in Seq order, readiness as a badge ─────────
    band_html = []
    # Hoisted: Python 3.11 forbids a backslash inside an f-string EXPRESSION,
    # and this glyph is used inside one.
    cursor_mark = " \u25b6"
    for b in bands:
        mine = [r for r in by_seq if b["lo"] <= r["seq"] <= b["hi"]]
        left = [r for r in mine if r["lane"] != "DONE"]
        cards = "".join(
            f'<div class="bcard {LANE_CLASS[r["lane"]]}'
            f'{" cursor" if r["step"] == pointer else ""}"'
            f' data-b="{bub(step_bubble(r["step"]))}">'
            f'<div class="bstep">{e(r["step"])}'
            f'{cursor_mark if r["step"] == pointer else ""}</div>'
            f'<div class="btitle">{e(r["title"])}</div>'
            f'<div class="brow"><span class="badge {LANE_CLASS[r["lane"]]}">'
            f'{e(r["lane"])}</span><span class="bzone">{e(r["zone"])} \u00b7 '
            f'{e(r["scope"])}</span></div></div>'
            for r in mine)
        band_html.append(
            f'<section class="band"><h3><span class="bid">{e(b["id"])}</span>'
            f'{e(b["name"].strip())}'
            f'<span class="bn">{len(mine) - len(left)} of {len(mine)} done</span>'
            f'</h3><div class="bdel">{e(b["delivers"])}</div>'
            f'<div class="bcards">{cards}</div></section>')

    # ── The completeness panel (§55.3), with hover detail. ────────────────
    #
    # **COMPLETE and OPEN, both named.** The panel used to show five fractions
    # and a row of chips; a fraction says how far, never what is left. Every
    # item renders as "§49 — API surface" and never as a bare number.
    #
    # **Every bubble is read from a source document at generation time.** The
    # generator types no title, no Done-when and no gap text - if it did, the
    # bubble would be a fourth copy of a sentence nobody edits.
    # ── the SHARED block ──────────────────────────────────────────────────
    shared = [it for it in comp["Define"] if it["scope"] == "SHARED"]
    done_items = [it for it in shared if it["state"] == "built"]

    def blocks_soonest(it: dict) -> tuple:
        """Order OPEN by what blocks soonest: the Seq of its closing step."""
        seqs = [seq_of_step[c] for c in it["closes"] if c in seq_of_step]
        return (0, min(seqs)) if seqs else (1, 0)

    open_items = sorted([it for it in shared if it["state"] != "built"],
                        key=blocks_soonest)

    comp_html = "".join(
        f'<li class="ci built" data-b="{bub(section_bubble(it["sec_resolved"], it["scope"]))}">'
        f'\u2705 {named(it["sec_resolved"])}</li>' for it in done_items)

    open_html = []
    for it in open_items:
        sec = it["sec_resolved"]
        m = marker_of.get(sec)
        gn = gnums(m) if m else ""
        if it["closes"]:
            cl = " \u00b7 closes " + ", ".join(
                f'<u data-b="{bub(step_bubble(c))}">{e(c)} '
                f'{e(title_of.get(c, ""))}</u>'.strip()
                for c in it["closes"])
        else:
            cl = ' \u00b7 <b class="bad">no step owns this</b>'
        gtag = (f' <b class="gnum" data-b="{bub(gap_bubble(gn.split(", ")[0]))}">'
                f'{e(gn)}</b>') if gn else ""
        open_html.append(
            f'<li class="ci {it["state"]}" '
            f'data-b="{bub(section_bubble(sec, it["scope"]))}">'
            f'{glyph[it["state"]]} {named(sec)}{gtag} \u00b7 '
            f'<i>{e(STATE_WORDS[it["state"]])}</i>{cl}</li>')

    # ── one line per phase: what DIFFERS ──────────────────────────────────
    subs = read_phase_subsections()
    phase_rows = []
    for name, digit in PHASE_ROWS[1:]:
        own = f"\u00a739.{digit}"
        info = subs.get(own, {"n": 0, "canonical": 0, "missing": []})
        # the phase item from §55.3 (the one PHASE-scoped row)
        it = next(x for x in comp[name] if x["scope"] == "PHASE")
        m = marker_of.get(own)
        if info["missing"]:
            differs = (f'<b class="bad">{info["n"]} of {info["canonical"]} '
                       f'subsections</b> \u2014 {len(info["missing"])} missing: '
                       + e(", ".join(info["missing"])))
        else:
            lst = f"\u00a739.{digit}.2"
            lm = marker_of.get(lst)
            state = lm["state"] if lm else "unmeasured"
            differs = (f'{named(lst)} \u2014 <i>{e(STATE_WORDS[state])}</i>'
                       + ('' if (lm and lm["closes"]) else
                          ' \u00b7 <b class="bad">no step owns this</b>'))
        phase_rows.append(
            f'<tr><td class="pn" data-b="{bub(section_bubble(own, "PHASE"))}">'
            f'{glyph[it["state"]]} {named(own)}</td>'
            f'<td class="pd">{differs}</td></tr>')

    phase_html = (
        '<div class="shcard"><div class="shh">SHARED \u2014 the '
        + str(len(shared)) + ' items every phase traverses</div>'
        '<div class="shcols"><div><h5>Complete \u00b7 ' + str(len(done_items))
        + '</h5><ul class="cil">' + comp_html + '</ul></div>'
        '<div><h5>Open \u00b7 ' + str(len(open_items))
        + ' <i>\u2014 soonest-blocking first</i></h5><ul class="cil">'
        + "".join(open_html) + '</ul></div></div></div>'
        '<table class="phd"><tr><th>Phase \u00b7 its own spec</th>'
        '<th>What differs</th></tr>' + "".join(phase_rows) + "</table>")

    # ── architecture blocks (unchanged in substance) ───────────────────────
    blocks_html = []
    for bid, bname in BLOCKS.items():
        zones = sorted({MARKER_HOME[m["section"]][1] for m in markers
                        if MARKER_HOME[m["section"]][0] == bid})
        holes = [m for m in markers
                 if m["state"] in ("unbuilt", "defect", "blocked")
                 and MARKER_HOME[m["section"]][0] == bid]
        items = []
        for m in sorted(holes, key=lambda m: m["section"]):
            steps = closes_named(m) if m["closes"] else "no step owns this"
            lanes = {r["step"]: r["lane"] for r in rows}
            cls = LANE_CLASS.get(lanes.get(m["closes"][0], ""), "queued") \
                if m["closes"] else "none"
            items.append(
                f'<li><span class="g">{glyph[m["state"]]}</span> '
                f'<span class="sn">{named(m["section"])}</span>'
                f'<span class="chip {cls}">{e(steps)}</span></li>')
        ok = "" if items else '<li class="ok">\u2705 no open markers</li>'
        blocks_html.append(
            f'<div class="block"><h4>{bid} \u00b7 {e(bname)}'
            f'<span class="zs">{" ".join(e(z) for z in zones)}</span></h4>'
            f'<ul>{"".join(items) or ok}</ul></div>')

    landed_html = " ".join(
        f'<span class="lchip">{step_named(r["step"])}</span>' for r in by_seq
        if r["lane"] == "DONE")

    # ── PART 2: the legend. Prefixes in plain words, then the bands. ──────
    #
    # Generated rather than typed: the band half comes from Appendix D's band
    # table, so a band renamed there is renamed here. The prefix half is a
    # vocabulary, which does not live anywhere machine-readable - it is
    # declared once, here, and nowhere else.
    legend_prefix = [
        ("§", "a section of the architecture — the design"),
        ("G-", "a registered gap — something known wrong or missing"),
        ("F-", "a recurring fault pattern"),
        ("S-", "a named contract — a schema, or a function surface"),
        ("WATCH", "a standing hazard being tracked"),
    ]
    # **One meaning per colour, and the legend is where that is stated.**
    # A colour rule nobody can read off the page is a convention, not a key -
    # and the clash this replaced (READY green, DONE green) survived precisely
    # because nothing on the board ever said what green meant.
    legend_state = [
        ("done", "green", "exists and works",
         "DONE · ✅ built"),
        ("ready", "blue", "can start now",
         "READY"),
        ("now", "orange", "in progress",
         "BUILDING NOW — the cursor"),
        ("defect", "amber", "live, and wrong",
         "⚠️ built with a known defect"),
        ("blocked", "red", "cannot proceed",
         "BLOCKED · ⛔"),
        ("queued", "grey", "scheduled, not started",
         "QUEUED · ☐ not built"),
        ("unmeasured", "dashed", "unmeasured — not a pass",
         "no marker exists for it"),
    ]
    legend = (
        '<div class="lgcard"><h4>What the prefixes mean</h4>'
        + "".join(f'<div class="lgrow"><span class="lgk">{e(k)}</span>'
                  f'<span class="lgv">{e(v)}</span></div>'
                  for k, v in legend_prefix)
        + '</div><div class="lgcard"><h4>What the colours mean — one each</h4>'
        + "".join(f'<div class="lgrow"><span class="sw {c}"></span>'
                  f'<span class="lgk lgn">{e(name)}</span>'
                  f'<span class="lgv">{e(mean)} — <i>{e(where)}</i></span></div>'
                  for c, name, mean, where in legend_state)
        + '</div><div class="lgcard lgwide"><h4>What the bands deliver</h4>'
        + "".join(f'<div class="lgrow"><span class="lgk">{e(b["id"])} · '
                  f'{e(b["name"])}</span><span class="lgv">{e(b["delivers"])}'
                  "</span></div>" for b in bands)
        + "</div>")

    return TEMPLATE.format(
        legend=legend,
        last_spine=last_spine, n_done=n_done, n_all=n_all, pct=pct,
        n_markers=len(markers),
        n_open=sum(1 for m in markers if m["state"] != "built"),
        health="".join(health),
        slice_id=e(cur["id"]), slice_name=e(cur["name"].strip()),
        slice_delivers=e(cur["delivers"]),
        slice_done=len(cur_done), slice_all=len(in_cur),
        slice_rows="".join(slice_rows) or "<li>nothing left in this band</li>",
        others="".join(others),
        bands="".join(band_html),
        phases="".join(phase_html),
        blocks="".join(blocks_html),
        landed=landed_html)


TEMPLATE = """<!doctype html>
<meta charset="utf-8"><title>Agent Improve — refactor board</title>
<style>
:root{{--bg:#fbfbfa;--fg:#1a1a18;--mut:#6b6b66;--line:#e3e3de;--card:#fff;
--now:#c2410c;--ready:#1d4ed8;--queued:#6b6b66;--blocked:#b91c1c;--done:#3f6212;
--defect:#a16207}}
@media(prefers-color-scheme:dark){{:root{{--bg:#161614;--fg:#eceae5;--mut:#9b9b94;
--line:#2e2c28;--card:#1e1c1a;--now:#fb923c;--ready:#60a5fa;--queued:#9b9b94;
--blocked:#f87171;--done:#a3e635;--defect:#fbbf24}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 ui-sans-serif,
-apple-system,Segoe UI,Roboto,sans-serif;padding:28px;max-width:1280px}}
h1{{font-size:19px;margin:0 0 2px}}
.sub{{color:var(--mut);font-size:12px;margin-bottom:22px}}
h2{{font-size:12px;letter-spacing:.09em;text-transform:uppercase;color:var(--mut);
margin:30px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}}
.bar{{height:9px;background:var(--line);border-radius:5px;overflow:hidden;max-width:560px}}
.bar>i{{display:block;height:100%;width:{pct}%;background:var(--done)}}
.tl{{color:var(--mut);font-size:12px;margin-top:7px}}
.badge{{font-size:9.5px;letter-spacing:.07em;border:1px solid var(--line);border-radius:9px;
padding:0 6px;color:var(--mut);white-space:nowrap}}
.badge.now{{color:var(--now);border-color:var(--now)}}
.badge.ready{{color:var(--ready);border-color:var(--ready)}}
.badge.blocked{{color:var(--blocked);border-color:var(--blocked)}}
.badge.done{{color:var(--done);border-color:var(--done)}}
.legend{{display:grid;grid-template-columns:repeat(auto-fit,minmax(268px,1fr));gap:10px}}
.lgcard{{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:10px 12px}}
.lgcard.lgwide{{grid-column:1/-1}}
.lgcard h4{{margin:0 0 6px;font-size:11px;letter-spacing:.07em;text-transform:uppercase;
color:var(--mut)}}
.lgrow{{display:flex;gap:9px;font-size:12px;padding:2px 0;align-items:baseline}}
.lgk{{flex:0 0 132px;font-weight:600}}
.lgk.lgn{{flex:0 0 74px}}
.sw{{flex:0 0 14px;height:14px;border-radius:4px;border:1px solid var(--line);
align-self:center}}
.sw.done{{background:var(--done);border-color:var(--done)}}
.sw.ready{{background:var(--ready);border-color:var(--ready)}}
.sw.now{{background:var(--now);border-color:var(--now)}}
.sw.defect{{background:var(--defect);border-color:var(--defect)}}
.sw.blocked{{background:var(--blocked);border-color:var(--blocked)}}
.sw.queued{{background:var(--queued);border-color:var(--queued)}}
.sw.unmeasured{{background:transparent;border-style:dashed;border-color:var(--mut)}}
.lgv i{{font-style:normal;opacity:.75}}
.lgv{{color:var(--mut)}}
.sn{{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}}
/* current slice */
.slice{{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--now);
border-radius:10px;padding:15px 17px}}
.sname{{font-size:16px;font-weight:600}}
.sname .sid{{display:inline-block;background:var(--now);color:var(--bg);border-radius:5px;
padding:0 7px;margin-right:8px;font-size:13px}}
.sprog{{color:var(--mut);font-size:12px;margin:3px 0 4px}}
.sdel{{font-size:12.5px;color:var(--mut);margin-bottom:11px}}
.slice ol{{margin:0;padding:0;list-style:none;counter-reset:s}}
.slice li{{padding:9px 0;border-top:1px solid var(--line)}}
.slice li.cursor{{background:linear-gradient(90deg,color-mix(in srgb,var(--now) 9%,transparent),transparent);
margin:0 -17px;padding-left:17px;padding-right:17px}}
.sh{{display:flex;gap:8px;align-items:baseline;font-size:13px}}
.sh .badge{{margin-left:auto}}
.goal{{font-size:12px;color:var(--mut);margin-top:3px;max-width:92ch}}
.goal.none{{color:var(--blocked)}}
.obands{{display:grid;grid-template-columns:repeat(auto-fit,minmax(246px,1fr));gap:10px;
margin-top:12px}}
.obandrow{{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:9px 11px}}
.obandrow b{{font-size:12.5px}}
.obandrow .on{{float:right;font-size:11px;color:var(--mut)}}
.obandrow .od{{font-size:11.5px;color:var(--mut);margin-top:4px}}
.obandrow .ow{{font-size:11px;color:var(--mut);margin-top:4px;opacity:.8}}
/* bands */
.band{{margin-bottom:16px}}
.band h3{{font-size:13px;margin:0 0 3px;display:flex;gap:9px;align-items:center}}
.band .bid{{background:var(--fg);color:var(--bg);border-radius:5px;padding:0 7px;
font-size:11px}}
.band .bn{{margin-left:auto;font-size:11px;color:var(--mut);font-weight:400}}
.bdel{{font-size:11.5px;color:var(--mut);margin-bottom:8px;max-width:95ch}}
.bcards{{display:grid;grid-template-columns:repeat(auto-fill,minmax(186px,1fr));gap:8px}}
.bcard{{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--line);
border-radius:8px;padding:8px 10px}}
.bcard.now{{border-left-color:var(--now)}} .bcard.ready{{border-left-color:var(--ready)}}
.bcard.blocked{{border-left-color:var(--blocked)}} .bcard.done{{border-left-color:var(--done);opacity:.62}}
.bcard.cursor{{box-shadow:0 0 0 2px var(--now)}}
.bstep{{font-size:12px;font-weight:600}}
.btitle{{font-size:11.5px;color:var(--mut);margin:2px 0 6px;min-height:2.4em}}
.brow{{display:flex;gap:6px;align-items:center}}
.bzone{{margin-left:auto;font-size:9.5px;color:var(--mut);letter-spacing:.05em}}
.shcard{{background:var(--card);border:1px solid var(--line);border-radius:9px;
padding:12px 14px;margin-bottom:11px}}
.shh{{font-size:12px;letter-spacing:.05em;color:var(--mut);margin-bottom:9px}}
.shcols{{display:grid;grid-template-columns:1fr 1.35fr;gap:18px}}
@media(max-width:900px){{.shcols{{grid-template-columns:1fr}}}}
.shcols h5{{margin:0 0 6px;font-size:11px;letter-spacing:.07em;text-transform:uppercase;
color:var(--mut)}}
.shcols h5 i{{font-style:normal;opacity:.7;text-transform:none;letter-spacing:0}}
ul.cil{{margin:0;padding:0;list-style:none}}
.cil .ci{{font-size:12px;padding:2px 0;border-top:1px solid var(--line);cursor:help}}
.cil .ci:first-child{{border-top:0}}
.cil .ci.built{{color:var(--mut)}}
.cil .ci i{{font-style:normal;color:var(--mut)}}
.cil .ci b.bad{{color:var(--blocked);font-weight:600}}
.cil .ci b.gnum{{color:var(--defect);cursor:help}}
.cil .ci u{{text-decoration:none;border-bottom:1px dotted var(--mut);cursor:help}}
table.phd{{width:100%;border-collapse:collapse;font-size:12.5px}}
table.phd th{{text-align:left;font-size:10.5px;letter-spacing:.07em;text-transform:uppercase;
color:var(--mut);font-weight:600;padding:0 6px 5px}}
table.phd td{{border-top:1px solid var(--line);padding:7px 6px;vertical-align:top}}
td.pn{{width:340px;cursor:help}}
td.pd b.bad{{color:var(--blocked)}}
td.pd i{{font-style:normal;color:var(--mut)}}
/* the hover bubble - no library, no network */
#bub{{position:fixed;z-index:99;max-width:520px;background:var(--card);
border:1px solid var(--line);border-left:3px solid var(--now);border-radius:9px;
padding:10px 12px;box-shadow:0 6px 24px rgba(0,0,0,.18);font-size:12px;
pointer-events:none}}
#bub .bt{{font-weight:600;margin-bottom:5px}}
#bub .br{{display:flex;gap:8px;padding:2px 0;align-items:baseline}}
#bub .br>span{{flex:0 0 84px;color:var(--mut);font-size:10.5px;letter-spacing:.05em;
text-transform:uppercase}}
#bub .br.bad{{color:var(--blocked)}}
#bub .bsrc{{margin-top:7px;padding-top:6px;border-top:1px solid var(--line);
font-size:10.5px;color:var(--mut)}}
.pcard{{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:11px 13px}}
.ph1{{font-size:13px;font-weight:600;display:flex;align-items:baseline}}
.pfrac{{margin-left:auto;font-variant-numeric:tabular-nums;color:var(--mut);font-weight:400}}
.pbar{{height:6px;background:var(--line);border-radius:4px;overflow:hidden;margin:6px 0 5px}}
.pbar>i{{display:block;height:100%;background:var(--done)}}
.pmeta{{font-size:11px;color:var(--mut);margin-bottom:7px}}
.pmeta b{{color:var(--fg)}}
.cchips{{display:flex;flex-wrap:wrap;gap:3px}}
.cchip{{font-size:10px;border:1px solid var(--line);border-radius:8px;padding:0 5px;
color:var(--mut);white-space:nowrap}}
.cchip b{{opacity:.4;margin-left:3px}}
.cchip b.ph{{opacity:.85}}
.cchip.built{{border-color:color-mix(in srgb,var(--done) 50%,var(--line))}}
.cchip.defect{{border-color:color-mix(in srgb,var(--defect) 60%,var(--line));
color:var(--defect)}}
.cchip.unbuilt{{border-color:var(--line)}}
.cchip.blocked{{border-color:color-mix(in srgb,var(--blocked) 55%,var(--line));
color:var(--blocked)}}
.cchip.unmeasured{{border-style:dashed;border-color:var(--mut);color:var(--fg)}}
/* per-phase */
/* health */
.health{{display:grid;grid-template-columns:repeat(auto-fit,minmax(232px,1fr));gap:11px}}
.hcard{{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--line);
border-radius:9px;padding:11px 13px}}
.hcard.ok{{border-left-color:var(--done)}}
.hcard.warn{{border-left-color:var(--defect)}}
.hcard.none{{border-left-color:var(--queued)}}
.hn{{font-size:26px;font-weight:600;line-height:1.1}}
.hcard.ok .hn{{color:var(--done)}} .hcard.warn .hn{{color:var(--defect)}}
.hcard.none .hn{{color:var(--mut)}}
.ht{{font-size:12.5px;font-weight:600;margin-top:1px}}
.hnote{{font-size:11.5px;color:var(--mut);margin-top:3px}}
.hchips{{margin-top:8px;display:flex;flex-wrap:wrap;gap:4px}}
.hchip{{font-size:10.5px;border:1px solid var(--line);border-radius:9px;padding:1px 6px;
color:var(--mut);white-space:nowrap}}
.hchip b{{color:var(--defect)}}
/* blocks */
.blocks{{display:grid;grid-template-columns:repeat(auto-fill,minmax(258px,1fr));gap:11px}}
.block{{background:var(--card);border:1px solid var(--line);border-radius:9px;padding:11px 13px}}
.block h4{{margin:0 0 7px;font-size:13px;display:flex;justify-content:space-between;
align-items:center;gap:8px}}
.zs{{font-size:10px;color:var(--mut);font-weight:400;letter-spacing:.06em}}
.block ul{{margin:0;padding:0;list-style:none}}
.block li{{padding:3px 0;font-size:12.5px;display:flex;align-items:center;gap:6px;
border-top:1px solid var(--line)}}
.block li:first-child{{border-top:0}}
.block li.ok{{color:var(--mut)}}
.g{{width:17px;display:inline-block}}
.chip{{margin-left:auto;font-size:11px;padding:1px 7px;border-radius:9px;
border:1px solid var(--line);color:var(--mut);white-space:nowrap}}
/* A `closes` chip POINTS AT A STEP; it is not a state. Colouring it by
   that step's lane put green beside a "not built" marker, which is the
   one thing the colour rule forbids. Neutral, always. */
.lchip{{display:inline-block;font-size:10.5px;border:1px solid var(--line);border-radius:9px;
padding:0 6px;margin:0 3px 3px 0;color:var(--mut)}}
footer{{margin-top:34px;color:var(--mut);font-size:11.5px;border-top:1px solid var(--line);
padding-top:11px;max-width:860px}}
details>summary{{cursor:pointer;font-size:12px;color:var(--mut)}}
</style>
<h1>Agent Improve — refactor board</h1>
<div class="sub">Regenerated by <code>.claude/hooks/build_board.py</code> on every commit —
last spine step landed: <b>{last_spine}</b>.
Every figure traces to Appendix D, ARCHITECTURE.md's BUILT markers, §66, or git log.
<b>Nothing here is hand-written — edit the documents, not this page.</b></div>

<h2>Now → testing</h2>
<div class="bar"><i></i></div>
<div class="tl">{n_done} of {n_all} spine steps landed · {pct}% ·
{n_open} of {n_markers} BUILT markers still open</div>

<div id="bub" hidden></div>

<h2>How to read this board</h2>
<div class="legend">{legend}</div>

<h2>Building now — the current slice</h2>
<div class="slice">
  <div class="sname"><span class="sid">{slice_id}</span>{slice_name}</div>
  <div class="sprog">{slice_done} of {slice_all} steps done</div>
  <div class="sdel">{slice_delivers}</div>
  <ol>{slice_rows}</ol>
</div>
<div class="obands">{others}</div>

<h2>The plan — four bands, in Seq order</h2>
{bands}

<h2>What every phase traverses — complete and open (§55.3)</h2>
{phases}

<h2>Health — what the markers say, counted</h2>
<div class="health">{health}</div>

<h2>Architecture — every open marker carries the step that fills it</h2>
<div class="blocks">{blocks}</div>

<h2>Landed</h2>
<details><summary>{n_done} steps — show</summary><div style="margin-top:8px">{landed}</div></details>

<script>
/* Hover detail. Everything shown is baked into data-b at generation time by
   build_board.py, read from ARCHITECTURE.md and REFACTORING_PROCEDURE.md -
   so the page is self-contained and works opened as a local file. */
(function () {{
  var bub = document.getElementById('bub');
  function show(el, ev) {{
    bub.innerHTML = el.getAttribute('data-b');
    bub.hidden = false;
    var r = bub.getBoundingClientRect(), pad = 12;
    var x = Math.min(ev.clientX + 16, window.innerWidth - r.width - pad);
    var y = ev.clientY + 18;
    if (y + r.height > window.innerHeight - pad) y = ev.clientY - r.height - 12;
    bub.style.left = Math.max(pad, x) + 'px';
    bub.style.top = Math.max(pad, y) + 'px';
  }}
  document.addEventListener('mouseover', function (ev) {{
    var el = ev.target.closest('[data-b]');
    if (el) show(el, ev);
  }});
  document.addEventListener('mousemove', function (ev) {{
    var el = ev.target.closest('[data-b]');
    if (el && !bub.hidden) show(el, ev); else if (!el) bub.hidden = true;
  }});
  document.addEventListener('mouseout', function (ev) {{
    if (!ev.relatedTarget || !ev.relatedTarget.closest('[data-b]'))
      bub.hidden = true;
  }});
}})();
</script>

<footer><b>Bands are the plan; readiness is a badge.</b> Until 2026-09-11 this
board led with lanes, and 11.1 and 11.2 sat in READY beside 6.18 — correct on
readiness and misleading about what to do next, because cleanup has no unmet
preconditions. <b>Everything here is derived:</b> bands and their Seq ranges from
Appendix D's band table, each step's goal from its own Done-when in the
procedure, per-phase rows from the <code>&gt; **BUILT:**</code> markers on
§39.1–§39.5, G-numbers from §66's refs column filtered by its closed list, and
DONE from git log ∩ Appendix D. A step that landed under another subject is
invisible to the count by design — that is what EXTERNAL is for.</footer>
"""


def main(argv: list[str]) -> int:
    """Fail-SOFT. A hook that WRITES must never wedge a commit (6.16 §5).

    A generator that raises leaves the previous board in place and says so on
    stderr; it does not block the commit that would have refreshed it. The
    enforcement point is elsewhere: `commit-msg-refactor-guard.py`'s rule 2b
    watches `docs/board.html`, so a stale board is visible the same way a
    stale marker is - fail-soft writer, fail-closed checker.
    """
    try:
        rows = read_appendix_d()
        precon = read_preconditions()
        landed = landed_steps()
        markers = read_markers()
        gaps = read_gaps()
        assign_lanes(rows, landed, precon)

        if "--check" in argv:
            counts = {l: sum(1 for r in rows if r["lane"] == l) for l in LANES}
            print(f"{len(rows)} steps, {len(markers)} markers "
                  f"({sum(1 for m in markers if m['state'] != 'built')} open), "
                  f"{len(gaps)} gaps")
            print(" · ".join(f"{k} {v}" for k, v in counts.items()))
            unmapped = [m["section"] for m in markers
                        if m["section"] not in MARKER_HOME]
            if unmapped:
                print("UNMAPPED markers:", unmapped)
                return 1
            return 0

        Path(OUT).write_text(
            render(rows, markers, gaps, landed, read_bands(),
                   read_done_when(), read_section_titles(),
                   read_completeness_set(), read_done_when_full(),
                   read_verify(), read_preconditions()),
            encoding="utf-8")
        print(f"  [board] {os.path.relpath(OUT, ROOT)} regenerated "
              f"— {len(rows)} steps, {len(markers)} markers")
        return 0
    except Exception as exc:                        # noqa: BLE001
        print(f"  [board] NOT regenerated: {exc!r}", file=sys.stderr)
        return 0                                    # fail-soft, always


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
