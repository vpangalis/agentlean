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
}
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
    r"\| (?P<zone>\w+) \| (?P<impact>.*?) \|$", re.M)
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
            "desc": desc[:240],
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


def render(rows: list[dict], markers: list[dict], gaps: dict[str, str],
           landed: set[str]) -> str:
    e = html.escape
    by_lane: dict[str, list[dict]] = {k: [] for k in LANES}
    for r in rows:
        by_lane[r["lane"]].append(r)
    for k in by_lane:
        by_lane[k].sort(key=lambda r: r["seq"])      # Seq, never the number

    closers = {}
    for m in markers:
        for c in m["closes"]:
            closers.setdefault(c, []).append(m["section"])

    # container 0 — the timeline
    n_done, n_all = len(by_lane["DONE"]), len(rows)
    pct = round(100 * n_done / n_all)

    # ── PART 5 — the health panel, GENERATED from the markers. ───────────
    #
    # Founder ruling 2026-09-11: "five defects and twenty unstarted steps look
    # identical on it". They are not the same thing and must not read the same
    # - a defect is live code doing the wrong thing, an unstarted step is
    # absent code doing nothing. The three counts come from the marker states
    # and the §66 register; none is typed anywhere.
    built = [m for m in markers if m["state"] == "built"]
    defective = [m for m in markers if m["state"] == "defect"]
    unbuilt = [m for m in markers if m["state"] in ("unbuilt", "blocked")]

    def _gnum(m: dict) -> str:
        """OPEN §66 gaps that name this marker's section, newest first.

        **From the REGISTER, never from the marker's prose.** Reading the first
        `G-\d+` out of the marker text put G-15 against §19.6 - a reference to
        a measurement, not the reason it is defective. A fabricated attribution
        in the panel whose job is to say what is wrong is worse than none, so
        where §66 names no gap for a section this returns empty and the chip
        carries only the section and its closing step.
        """
        hits = [g for g, v in gaps.items()
                if not v["closed"] and (v["refs"] & m["aliases"])]
        return ", ".join(sorted(hits, key=lambda g: -int(g.split("-")[1])))

    health = []
    for title, items, cls, note in (
        ("Built", built, "ok",
         "exists and works as specified"),
        ("Built and defective", defective, "warn",
         "live code, doing something other than what is specified"),
        ("Not started", unbuilt, "none",
         "absent — nothing runs, nothing misbehaves"),
    ):
        chips = "".join(
            f'<span class="hchip">{e(m["section"])}'
            + (f' <b>{e(_gnum(m))}</b>' if _gnum(m) else "")
            + (f' <i>{e(", ".join(m["closes"]))}</i>' if m["closes"] else "")
            + "</span>"
            for m in sorted(items, key=lambda m: m["section"]))
        health.append(
            f'<div class="hcard {cls}"><div class="hn">{len(items)}</div>'
            f'<div class="ht">{title}</div><div class="hnote">{e(note)}</div>'
            f'<div class="hchips">{chips or "&mdash;"}</div></div>')
    health_html = "".join(health)

    # container 1 — the nested architecture diagram, by block
    blocks_html = []
    for bid, bname in BLOCKS.items():
        zones = sorted({MARKER_HOME[m["section"]][1] for m in markers
                        if MARKER_HOME[m["section"]][0] == bid})
        holes = [m for m in markers
                 if m["state"] in ("unbuilt", "defect", "blocked")
                 and MARKER_HOME[m["section"]][0] == bid]
        items = []
        for m in holes:
            glyph = {"unbuilt": "☐", "defect": "⚠️",
                     "blocked": "⛔"}[m["state"]]
            steps = ", ".join(m["closes"]) if m["closes"] else "none"
            lanes = {r["step"]: r["lane"] for r in rows}
            cls = LANE_CLASS.get(lanes.get(m["closes"][0], ""), "queued") \
                if m["closes"] else "none"
            items.append(
                f'<li><span class="g">{glyph}</span> <b>{e(m["section"])}</b>'
                f'<span class="chip {cls}">{e(steps)}</span></li>')
        ok = "" if items else '<li class="ok">✅ no open markers</li>'
        blocks_html.append(
            f'<div class="block"><h4>{bid} · {e(bname)}'
            f'<span class="zs">{" ".join(e(z) for z in zones)}</span></h4>'
            f'<ul>{"".join(items) or ok}</ul></div>')

    # container 2 + 3 — lanes, each card carrying its impact
    lanes_html = []
    for lane in LANES:
        cards = []
        for r in by_lane[lane]:
            gap_note = ""
            if lane == "BLOCKED":
                found = [f"{g}: {v['desc']}" for g, v in gaps.items()
                         if not v["closed"]
                         and re.search(rf"\b{re.escape(r['step'])}\b", v["desc"])]
                reason = r["status"] or "blocked"
                if found:
                    gap_note = f'<div class="gap">{e(found[0][:200])}</div>'
                gap_note = f'<div class="why">{e(reason)}</div>' + gap_note
            fills = closers.get(r["step"], [])
            fill = (f'<div class="fills">fills {", ".join(e(f) for f in fills)}</div>'
                    if fills else "")
            cards.append(
                f'<details class="card {LANE_CLASS[lane]}">'
                f'<summary><b>{e(r["step"])}</b> {e(r["title"])}'
                f'<span class="zone">{e(r["zone"])}</span></summary>'
                f'<div class="impact"><span class="lbl">If never done</span>'
                f'{e(r["impact"])}</div>{gap_note}{fill}'
                f'<div class="pre">precondition: {e(r["precondition"]) or "—"}</div>'
                f'</details>')
        lanes_html.append(
            f'<section class="lane {LANE_CLASS[lane]}"><h3>{lane}'
            f'<span class="n">{len(by_lane[lane])}</span></h3>{"".join(cards)}</section>')

    # **NO WALL-CLOCK DATE IN THE OUTPUT, AND THAT IS LOAD-BEARING.**
    # `docs/board.html` is a rule-2b watched path, so a byte that changes for
    # a reason unrelated to the four sources would force `ARCHITECTURE.md`
    # into the first commit of every day - and a guard that fires for nothing
    # is one people route around with --no-verify, which the guard file itself
    # names as worse than no guard. The board therefore changes when, and only
    # when, Appendix D, a BUILT marker, §66 or the spine log changes. The last
    # spine commit below carries the recency a date would have.
    _done_rows = [r for r in rows if r["lane"] == "DONE"]
    last_spine = (max(_done_rows, key=lambda r: r["seq"])["step"]
                  if _done_rows else "none")
    return TEMPLATE.format(
        health=health_html,
        last_spine=last_spine,
        n_done=n_done, n_all=n_all, pct=pct,
        blocks="".join(blocks_html),
        lanes="".join(lanes_html),
        n_markers=len(markers),
        n_open=sum(1 for m in markers if m["state"] != "built"),
    )


TEMPLATE = """<!doctype html>
<meta charset="utf-8"><title>Agent Improve — refactor board</title>
<style>
:root{{--bg:#fbfbfa;--fg:#1a1a18;--mut:#6b6b66;--line:#e3e3de;--card:#fff;
--now:#b45309;--ready:#15803d;--queued:#6b6b66;--blocked:#b91c1c;--done:#3f6212}}
@media(prefers-color-scheme:dark){{:root{{--bg:#161614;--fg:#eceae5;--mut:#9b9b94;
--line:#2e2c28;--card:#1e1c1a;--now:#f59e0b;--ready:#4ade80;--queued:#9b9b94;
--blocked:#f87171;--done:#a3e635}}}}
*{{box-sizing:border-box}}
body{{margin:0;background:var(--bg);color:var(--fg);font:14px/1.5 ui-sans-serif,
-apple-system,Segoe UI,Roboto,sans-serif;padding:28px}}
h1{{font-size:19px;margin:0 0 2px}}
.sub{{color:var(--mut);font-size:12px;margin-bottom:22px}}
h2{{font-size:12px;letter-spacing:.09em;text-transform:uppercase;color:var(--mut);
margin:30px 0 12px;padding-bottom:6px;border-bottom:1px solid var(--line)}}
.bar{{height:9px;background:var(--line);border-radius:5px;overflow:hidden;max-width:560px}}
.bar>i{{display:block;height:100%;width:{pct}%;background:var(--done)}}
.tl{{color:var(--mut);font-size:12px;margin-top:7px}}
.health{{display:grid;grid-template-columns:repeat(auto-fit,minmax(232px,1fr));gap:11px;
margin-bottom:8px}}
.hcard{{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--line);
border-radius:9px;padding:11px 13px}}
.hcard.ok{{border-left-color:var(--done)}}
.hcard.warn{{border-left-color:var(--now)}}
.hcard.none{{border-left-color:var(--queued)}}
.hn{{font-size:26px;font-weight:600;line-height:1.1}}
.hcard.ok .hn{{color:var(--done)}} .hcard.warn .hn{{color:var(--now)}}
.hcard.none .hn{{color:var(--mut)}}
.ht{{font-size:12.5px;font-weight:600;margin-top:1px}}
.hnote{{font-size:11.5px;color:var(--mut);margin-top:3px}}
.hchips{{margin-top:8px;display:flex;flex-wrap:wrap;gap:4px}}
.hchip{{font-size:10.5px;border:1px solid var(--line);border-radius:9px;padding:1px 6px;
color:var(--mut);white-space:nowrap}}
.hchip b{{color:var(--now)}} .hchip i{{font-style:normal;opacity:.75}}
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
.g{{width:15px;display:inline-block}}
.chip{{margin-left:auto;font-size:11px;padding:1px 7px;border-radius:9px;
border:1px solid var(--line);color:var(--mut);white-space:nowrap}}
.chip.now{{color:var(--now);border-color:var(--now)}}
.chip.ready{{color:var(--ready);border-color:var(--ready)}}
.chip.blocked{{color:var(--blocked);border-color:var(--blocked)}}
.chip.done{{color:var(--done);border-color:var(--done)}}
.lanes{{display:grid;grid-template-columns:repeat(auto-fit,minmax(268px,1fr));gap:13px;
align-items:start}}
.lane h3{{font-size:12px;letter-spacing:.07em;margin:0 0 8px;display:flex;gap:7px;
align-items:center}}
.lane .n{{font-size:11px;color:var(--mut);border:1px solid var(--line);
border-radius:9px;padding:0 7px}}
.lane.now h3{{color:var(--now)}} .lane.ready h3{{color:var(--ready)}}
.lane.blocked h3{{color:var(--blocked)}} .lane.done h3{{color:var(--done)}}
.card{{background:var(--card);border:1px solid var(--line);border-left:3px solid var(--line);
border-radius:7px;margin-bottom:6px;padding:7px 10px}}
.card.now{{border-left-color:var(--now)}} .card.ready{{border-left-color:var(--ready)}}
.card.blocked{{border-left-color:var(--blocked)}} .card.done{{border-left-color:var(--done)}}
summary{{cursor:pointer;font-size:12.5px;display:flex;gap:7px;align-items:baseline}}
summary::-webkit-details-marker{{display:none}}
.zone{{margin-left:auto;font-size:10px;color:var(--mut);letter-spacing:.06em}}
.impact{{margin-top:8px;font-size:12.5px;color:var(--fg)}}
.lbl{{display:block;font-size:10px;letter-spacing:.08em;text-transform:uppercase;
color:var(--mut);margin-bottom:2px}}
.why,.gap,.fills,.pre{{margin-top:6px;font-size:11.5px;color:var(--mut)}}
.why{{color:var(--blocked)}}
footer{{margin-top:34px;color:var(--mut);font-size:11.5px;border-top:1px solid var(--line);
padding-top:11px;max-width:760px}}
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

<h2>Health — what the markers say, counted</h2>
<div class="health">{health}</div>

<h2>Architecture — every open marker carries the step that fills it</h2>
<div class="blocks">{blocks}</div>

<h2>Lanes — derived, never declared</h2>
<div class="lanes">{lanes}</div>

<footer><b>Lanes are derived.</b> DONE is git log ∩ Appendix D.
BLOCKED is Appendix D's status column — the only thing git cannot say.
BUILDING NOW is the next-step pointer, computed with the same rule
<code>session-start-context.py</code> uses, so this board and the session
banner cannot disagree about what is next. READY means every precondition has
landed; QUEUED is everything else, in Appendix D order.
<b>A step that landed under another subject is invisible to the count by
design</b> — that is what EXTERNAL is for.</footer>
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

        Path(OUT).write_text(render(rows, markers, gaps, landed),
                             encoding="utf-8")
        print(f"  [board] {os.path.relpath(OUT, ROOT)} regenerated "
              f"— {len(rows)} steps, {len(markers)} markers")
        return 0
    except Exception as exc:                        # noqa: BLE001
        print(f"  [board] NOT regenerated: {exc!r}", file=sys.stderr)
        return 0                                    # fail-soft, always


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
