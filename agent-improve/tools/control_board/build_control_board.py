"""Render `docs/control-board.html` — ONE PICTURE AND ONE LIST that always agree. The control
board redesign (founder-ratified 2026-09-30); the layout is `docs/founder-inputs/board-mockup.html`'s.

Run by the pre-commit hook after `rank.py` and `wiring.py`. Inputs, nothing typed by hand:
every `docs/*_features.json` (Define today), `docs/test-results.json`, `docs/defects.json`,
business.md and platform.md, `docs/adr/`, the latest run-through record, the wiring findings,
`docs/board_waiting.md` and git (the commit the page was built on).

Top to bottom: the header (commit, date) · phase tabs (a phase is live once the registry has
features for it) · the milestone buttons · the value stream (stages × layers, one tile per
feature, the Belt journey strip at its top) · "What's left" beside the side box (Waiting on you,
Next up, Selected tile). A milestone button highlights its tiles, fades the rest, and switches
the list and Next up to it; the page opens on the first milestone that is not complete, or the
one its URL fragment names (`#M2`).

EVERY NUMBER on the page is read from `count()`: the buttons, the list's group counts, Next up
and the tile total. A tile has one meaning — colour = state, three states:
green = its test passes end to end on the current code; amber = built or partly built, not yet
proven (a written test that fails, a passing test that is not end to end, its lane's current
top, or proven only on earlier code and awaiting a fresh run-through — `features.awaiting`);
grey = not started (its test is a stub). A feature whose requirement is Won't-now is not shown.

The pilot cut: "Ready for pilot" and "Before customers" split M2 by each feature's `pilot`
field (true | false) in the feature registry, set by the founder's pilot-cut ruling. Until
every M2 feature carries it, M2 is one button, "Must-haves", and the page says the cut is not
ruled yet — the split is never guessed.

The Belt journey strip: each element square opens what the Belt provides, why it matters and
its acceptance criteria (the Define skill), what happened to it in the run (the run record) and
the features behind it; each stage square opens what happens there (the skill or business.md,
per `STAGE_SOURCES`), what happened in the run and the stage's features. White = not reached.

The page embeds `progress-data` (headline, statuses, next per lane) for `check_board.py`
(the commit guard's rule 10) and the session start.

    python tools/control_board/build_control_board.py [out.html] [--staged]
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))
sys.path.insert(0, str(_HERE.parent / "architecture"))

import adrs  # noqa: E402
import features  # noqa: E402
import rank  # noqa: E402
import wiring  # noqa: E402

OUT = features.PROJECT / "docs" / "control-board.html"
REPO = features.PROJECT.parent
DEFECTS = features.PROJECT / "docs" / "defects.json"
SKILL = features.PROJECT / "skills" / "dmaic-define-phase" / "SKILL.md"
#: The founder's open decisions the side box lists, one `- ` line each; none = no box.
WAITING = features.PROJECT / "docs" / "board_waiting.md"
PHASES = ("define", "measure", "analyse", "improve", "control")
STAGES = (("open_case", "Open case"), ("coached", "Works through the 13 elements"), ("report", "Report"),
          ("approve", "Approve"), ("record_written", "Record written"), ("next_phase", "Next phase opens"))
#: The row names and their one-line glosses, as the founder ruled them (board redesign, 2026-09-30).
LAYERS = (("screen", "Screens", "What the Belt sees"), ("api", "Access & files", "Sign-in, roles, uploads"),
          ("coaching", "Coaching", "How the coach teaches and checks"),
          ("gate", "Gate", "Report checks and approval"),
          ("persistence", "Data & audit", "History, revisions, what is kept"),
          ("platform", "Platform", "Security, errors, logging"))
E = html.escape
#: The milestone buttons, as the founder named them (board redesign, 2026-09-30): key, name, code.
ALL = ("all", "All of Define", "everything")
M1 = ("M1", "Belt gets through", "M1")
M2_ONE = ("M2", "Must-haves", "M2")
M2_PILOT = ("M2-pilot", "Ready for pilot", "M2 pilot")
M2_LATER = ("M2-later", "Before customers", "M2 later")
M3 = ("M3", "Nice to have", "M3")
PILOT_NOT_RULED = "pilot cut not ruled yet"
#: The three states, in the words the page uses.
STATE_WORDS = {"green": "done — passes end to end on the current code",
               "amber": "built, not yet proven", "grey": "not started"}


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, encoding="utf-8",
                          errors="replace", timeout=60).stdout


# ── the inputs ──────────────────────────────────────────────────────────────


def model() -> dict:
    """What `check_board.py` compares: headline, statuses and the next feature per lane."""
    feats = features.load()
    s = features.summary(feats)
    by_id = {f["id"]: f for f in feats}
    nxt = {lane: ({"id": v["next"], "description": by_id[v["next"]]["description"],
                   "test": by_id[v["next"]]["test"]} if v["next"] else None)
           for lane, v in s["lanes"].items()}
    return {"headline": features.headline(s), "passing": s["passing"], "total": s["total"],
            "fresh": s["fresh"], "statuses": s["status"], "next": nxt}


def _elements() -> list[tuple[str, list[str]]]:
    """The Define elements and their fields, from the SKILL.md table (its owner)."""
    rows = re.findall(r"^\| (\d+) \| ([^|]+) \| ([^|]+) \|$", SKILL.read_text(encoding="utf-8"), re.M)
    return [(name.strip(), re.findall(r"`(\w+)`", fields)) for n, name, fields in rows if 1 <= int(n) <= 13]


def _plain(s: str) -> str:
    """Markdown emphasis and code marks off, for a panel that shows text, not markup."""
    return re.sub(r"\*\*|(?<!\w)\*|\*(?!\w)|`", "", s).strip()


_BLOCK = re.compile(r"^\*\*\[(\d+) · \w+[^\]]*\]\*\*\n((?:>.*\n?)+)", re.M)
_CRITERION = re.compile(r"^- `([\w-]+)` — (.+)$")


def _element_content() -> dict[int, dict]:
    """Per element number, from the Define skill's coaching content (its owner): what it is,
    why it matters, and its acceptance criteria (the skill's paraphrase of R7)."""
    out: dict[int, dict] = {}
    for m in _BLOCK.finditer(SKILL.read_text(encoding="utf-8")):
        lines = [ln[1:].strip() for ln in m.group(2).splitlines()]
        lead = {k: next((_plain(ln[len(k):]) for ln in lines if ln.startswith(k)), "")
                for k in ("**What it is:**", "**Why it matters:**")}
        crit = [(c.group(1), _plain(c.group(2))) for c in map(_CRITERION.match, lines) if c]
        out[int(m.group(1))] = {"what": lead["**What it is:**"], "why": lead["**Why it matters:**"], "criteria": crit}
    return out


#: Where each stage's "what happens here" is read from: the file and the line that opens it.
STAGE_SOURCES = {"open_case": (SKILL, "### A — Phase opening"), "coached": (SKILL, "### C — Per-element coaching"),
                 "report": (SKILL, "### F — The Define report"), "approve": (features.REQUIREMENTS / "business.md", "**R6 "),
                 "record_written": (features.REQUIREMENTS / "business.md", "**R11 "),
                 "next_phase": (features.REQUIREMENTS / "business.md", "**f Carried forward.**")}


def _stage_text(path: Path, lead: str) -> tuple[str, str]:
    """The paragraph a stage's source opens with, and where it came from. A heading line (a
    markdown heading, or a requirement's id line) is skipped; a bold lead-in is kept inline."""
    text = path.read_text(encoding="utf-8")
    at = text.find(f"\n{lead}")
    if at < 0:
        return "", ""
    lines = text[at + 1:].splitlines()
    head = lines[0]
    heading = lead.startswith("#") or lead.startswith("**R")
    body = lines[1:] if heading else [head[len(lead):], *lines[1:]]
    while body and not body[0].strip():
        body = body[1:]
    para = []
    for ln in body:
        if not ln.strip() or ln.startswith("#") or ln.startswith("|"):
            break
        para.append(ln.strip())
    source = _plain((head if heading else lead).lstrip("#").split(" · ")[0]).rstrip(".")
    return _plain(" ".join(para)), f"{path.name} — {source}"


def _element_run(fields: list[str], turns: list[dict], stored: set[str], stuck: bool,
                 reached: bool, stopped: str) -> tuple[str, list[str]]:
    """What happened to one element in the run: its state and the facts the record holds."""
    on = [t for t in turns if t.get("field") in fields]
    stored_at = {t["stored_field"]: t.get("n") for t in turns if t.get("stored_field")}
    facts = [f"{f}: stored at turn {stored_at.get(f, '?')}" if f in stored
             else f"{f}: not stored" + ("" if any(t.get("field") == f for t in turns) else " — no turn of this run was on it")
             for f in fields]
    if on:
        moves: dict[str, int] = {}
        for t in on:
            moves[str(t.get("move"))] = moves.get(str(t.get("move")), 0) + 1
        facts.append(f"{len(on)} turn(s) on it, turns {on[0].get('n')}–{on[-1].get('n')}: "
                     + ", ".join(f"{k} ×{v}" for k, v in moves.items()))
        weak = [t.get("n") for t in on if t.get("verdict") == "insufficient"]
        if weak:
            facts.append(f"answer judged insufficient at turn(s) {', '.join(map(str, weak))}")
    if all(f in stored for f in fields):
        return "stored", facts
    if stuck:
        return "stuck", [*facts, f"the run record: {stopped}" if stopped else "the run record gives no reason"]
    if not reached:
        return "not reached", ["no turn of this run reached it"]
    return "not stored", [*facts, "the run record gives no reason beyond these turns"]


def run_date(name: str) -> str:
    """A run-through's date and time (UTC) from its record's file name, …_YYYYMMDDTHHMMSS.json."""
    m = re.search(r"(\d{4})(\d{2})(\d{2})T(\d{2})(\d{2})", name or "")
    return f"{m[1]}-{m[2]}-{m[3]} {m[4]}:{m[5]} UTC" if m else ""


def journey() -> dict:
    """The latest run-through as the six stages, and a sparkline of all of them. Per element and
    per stage it carries what the panel shows: the skill's and the requirements' text, and what
    the run record says happened."""
    runs = sorted(features.RUNTHROUGH.glob("define_runthrough_*.json"))
    elements = _elements()
    content = _element_content()
    spark = []
    latest: dict = {"stages": {k: "open" for k, _ in STAGES}, "elements": ["open"] * len(elements),
                    "note": "No run-through recorded yet.", "file": None, "reached": 0,
                    "element_run": [("not reached", ["no run-through recorded"])] * len(elements),
                    "stage_run": {k: ["no run-through recorded"] for k, _ in STAGES}}
    for path in runs:
        recs = json.loads(path.read_text(encoding="utf-8"))
        empty: dict = {}
        summ: dict = next((r for r in recs if r.get("kind") == "summary"), empty)
        turns = [r for r in recs if r.get("kind") == "turn"]
        final: dict = next((r for r in recs if r.get("kind") == "final_case"), empty)
        structured = final.get("define_structured") or {}
        stored = set(structured) if isinstance(structured, dict) else set(re.findall(r"'(\w+)':", str(structured)))
        done = [all(f in stored for f in fs) for _, fs in elements]
        spark.append({"run": path.stem[-15:], "elements": sum(done), "turns": len(turns)})
        stuck = summ.get("stuck_at")
        k = next((i for i, (_, fs) in enumerate(elements) if stuck in fs), None)
        touched = [i for i, (_, fs) in enumerate(elements)
                   if any(t.get("field") in fs for t in turns) or any(f in stored for f in fs)]
        last = k if k is not None else max(touched, default=-1)
        element_run = [_element_run(fs, turns, stored, i == k, i <= last, str(summ.get("stopped") or ""))
                       for i, (_, fs) in enumerate(elements)]
        # white = not reached in this run; grey = reached and not stored; amber = stuck
        els = [{"stored": "done", "stuck": "wip", "not stored": "miss"}.get(s, "open") for s, _ in element_run]
        sub: dict = next((r for r in recs if r.get("kind") == "gate_submit"), empty)
        body: dict = sub["body"] if isinstance(sub.get("body"), dict) else {}
        passed = body.get("passed") is True or "'passed': True" in str(sub.get("body") or "")
        moved = final.get("current_phase") not in (None, "define")
        stages = {"open_case": "done" if turns else "open",
                  "coached": "done" if all(done) else ("wip" if turns else "open"),
                  "report": "done" if passed else "open", "approve": "done" if moved else "open",
                  "record_written": "done" if moved else "open", "next_phase": "done" if moved else "open"}
        longest = max((float(t.get("seconds") or 0) for t in turns), default=0)
        reached = k + 1 if k is not None else sum(done)
        at_el = last if last >= 0 else 0
        stop_at = f"not reached: the run stopped at element {at_el + 1} ({elements[at_el][0]})"
        after = ([f"recorded after the stop — gate submit: {body.get('message', '')} "
                  f"Missing: {', '.join(body.get('missing_fields') or []) or '—'}"] if body and not all(done) else [])
        stage_run = {
            "open_case": [f"case {summ.get('case_id', '?')} opened; {len(turns)} turns recorded"] if turns else [stop_at],
            "coached": [f"{sum(done)} of {len(elements)} elements stored"]
                       + ([f"stuck at element {k + 1} ({elements[k][0]}): {summ.get('stopped', '')}"] if k is not None else []),
            "report": ["gate submit passed"] if passed else ([stop_at, *after] if not all(done)
                                                              else [f"gate submit: {body.get('message', 'not recorded')}"]),
            "approve": [f"approved — the case is now in {final.get('current_phase')}"] if moved else [stop_at if not all(done) else "not approved"],
            "record_written": [f"the record was written; the case is in {final.get('current_phase')}"] if moved
                              else [stop_at if not all(done) else "no record written"],
            "next_phase": [f"{final.get('current_phase')} opened"] if moved else [stop_at if not all(done) else "the next phase did not open"],
        }
        at = (f"element {reached} of {len(elements)} reached"
              + (f" (stuck at {elements[k][0]})" if k is not None else f" · {sum(done)} confirmed"))
        latest = {"stages": stages, "elements": els, "file": path.name, "reached": reached, "date": run_date(path.name),
                  "element_run": element_run, "stage_run": stage_run,
                  "note": f"{at} · {len(turns)} turns · {summ.get('model_calls', '?')} model calls · "
                          f"longest turn {longest:.0f} s · {'approved' if moved else 'not approved'}",
                  "stale": summ.get("product_hash") != features.product_hash()}
    latest["names"] = [n for n, _ in elements]
    latest["element_detail"] = [{"n": i + 1, "name": n, "fields": fs, **content.get(i + 1, {"what": "", "why": "", "criteria": []}),
                                 "state": latest["element_run"][i][0], "happened": latest["element_run"][i][1]}
                                for i, (n, fs) in enumerate(elements)]
    latest["stage_detail"] = {k: {"label": label, "state": latest["stages"][k], "happened": latest["stage_run"][k],
                                  **dict(zip(("what", "source"), _stage_text(*STAGE_SOURCES[k])))}
                              for k, label in STAGES}
    latest["spark"] = spark
    return latest


def _behind_element(f: dict, n: int, name: str, fields: list[str]) -> bool:
    """A coaching-stage feature is behind element n when it names it: 'Field n of 13', its test's
    [n-field] parameter, one of its field names, a two-word-or-longer part of its name, or its
    acronym (5W2H, SIPOC, CTQ)."""
    if f.get("stage") != "coached":
        return False
    desc, test = f["description"], f["test"]
    if re.search(rf"(?<!\w)Field {n} of \d+", desc) or f"[{n}-" in test:
        return True
    if any(re.search(rf"(?<!\w){re.escape(x)}(?!\w)", f"{desc} {test}") for x in fields if "_" in x):
        return True
    base = re.sub(r"\s*\(.*?\)", "", name)
    parts = {base, *re.split(r" from | and ", base)}
    if any(len(p.split()) >= 2 and p.lower() in desc.lower() for p in parts):
        return True
    return any(re.search(rf"(?<!\w){a}s?(?!\w)", desc) for a in re.findall(r"(?<!\w)([0-9A-Z]{3,})s?(?!\w)", name))


def _journey_features(j: dict, rows: list[dict]) -> None:
    """The features behind each element and each stage, in the order of work."""
    def order(fs: list[dict]) -> list[str]:
        return [f["id"] for f in sorted(fs, key=lambda f: (f["rank"] is None, f["rank"] or 0, f["id"]))]
    for e in j["element_detail"]:
        e["features"] = order([f for f in rows if _behind_element(f, e["n"], e["name"], e["fields"])])
    for k, s in j["stage_detail"].items():
        s["features"] = order([f for f in rows if f["stage"] == k])


def _order(f: dict) -> tuple:
    """The order of work: ranked first by rank, then the unranked, by id."""
    return (f["rank"] is None, f["rank"] or 0, f["id"])


def pilot_ruled(rows: list[dict]) -> bool:
    """The pilot cut is ruled once every M2 feature carries `pilot: true|false` in the registry —
    the founder's ruling sets it (a founder-owned change, with its `Ruling:` trailer)."""
    m2 = [r for r in rows if r["tier"] == rank.MILESTONES["M2"]]
    return bool(m2) and all(isinstance(r["pilot"], bool) for r in m2)


def milestones(rows: list[dict]) -> list[tuple[tuple[str, str, str], list[dict]]]:
    """The milestone buttons, left to right, each with its features; `rows` are the shown ones.
    M1-M3 are tiers 1-3 (`rank.MILESTONES`); M2 is split by `pilot` only once that is ruled."""
    tier = rank.MILESTONES
    m2 = [r for r in rows if r["tier"] == tier["M2"]]
    split = ([(M2_PILOT, [r for r in m2 if r["pilot"] is True]), (M2_LATER, [r for r in m2 if r["pilot"] is False])]
             if pilot_ruled(rows) else [(M2_ONE, m2)])
    return [(ALL, rows), (M1, [r for r in rows if r["tier"] == tier["M1"]]), *split,
            (M3, [r for r in rows if r["tier"] == tier["M3"]])]


def count(rows: list[dict]) -> dict:
    """THE COUNT — every number on the page is read from here (board redesign, founder
    2026-09-30): each button's done / total and its bar, each list group's "n left (k built, to
    prove)", Next up and the number of tiles. Done = a green tile; left = every other tile of the
    milestone, grouped by the grid's rows, in the order of work. It replaces the milestone box,
    the stage footers and the "What's left" columns, which counted the same features apart."""
    shown = [r for r in rows if not r["hidden"]]
    out = []
    for (key, name, code), mine in milestones(shown):
        mine = sorted(mine, key=_order)
        left = [r for r in mine if r["status"] != "green"]
        groups = [{"layer": lk, "name": ln, "left": [r["id"] for r in g], "built": sum(r["status"] == "amber" for r in g)}
                  for lk, ln, _ in LAYERS if (g := [r for r in left if r["layer"] == lk])]
        out.append({"key": key, "name": name, "code": code, "total": len(mine), "done": len(mine) - len(left),
                    "built": sum(r["status"] == "amber" for r in left),
                    "not_started": sum(r["status"] == "grey" for r in left),
                    "ids": [r["id"] for r in mine], "left": [r["id"] for r in left], "groups": groups,
                    "next": [r["id"] for r in left if r["rank"] and not r["held"]][:5]})
    default = next((m["key"] for m in out[1:] if m["done"] < m["total"]), ALL[0])
    return {"tiles": len(shown), "hidden": sorted(r["id"] for r in rows if r["hidden"]),
            "milestones": out, "default": default, "pilot_ruled": pilot_ruled(shown)}


def _blocker(f: dict, open_ids: set[str]) -> str:
    """What stands between a feature that is not done and done, in plain words."""
    if f["status"] == "green":
        return ""
    if f["awaiting"]:
        return "a fresh run-through on the current code (it passed on the latest run, which ran on earlier code)"
    if f["held"]:
        return f"the design decision {f['held']} is not accepted yet"
    deps = [d for d in f["depends_on"] if d in open_ids]
    if deps:
        return "waits for " + ", ".join(deps)
    if f["not_e2e"]:
        return "its test passes but does not drive the screens' connection or the coach (not end to end)"
    if f["stub"]:
        return "nothing — ready to build (its test is not written yet)"
    return "nothing — ready to build (its test is written and fails)"


def waiting_on_you(path: Path = WAITING) -> list[str]:
    """The founder's open decisions: one per `- ` line of `docs/board_waiting.md`. [] hides the box."""
    if not path.is_file():
        return []
    return [ln[2:].strip() for ln in path.read_text(encoding="utf-8").splitlines()
            if ln.startswith("- ") and ln[2:].strip()]


def live_phases() -> list[str]:
    """The phases the feature registry has features for — a tab is live once its phase has one."""
    have = {f.get("phase") for p in sorted((features.PROJECT / "docs").glob("*_features.json"))
            for f in features.load(p)}
    return [p for p in PHASES if p in have]


def built_on() -> dict:
    """The commit the page was built on (HEAD; the pre-commit build precedes its own commit)."""
    today = dt.date.today()
    return {"sha": _git("rev-parse", "--short", "HEAD").strip() or "—",
            "branch": _git("rev-parse", "--abbrev-ref", "HEAD").strip() or "—",
            "date": f"{today.day} {today:%b %Y}"}


def data() -> dict:
    """Everything the page draws."""
    feats = features.load()
    res = features.results()
    st = features.status(feats, res)
    reqs = features.requirements()
    ranked = rank.rank(feats, res, reqs)
    by_rank = {r["id"]: r for r in ranked}
    tiers = rank.tiers(feats, reqs)
    nxt = rank.next_per_lane(ranked)
    failing = {i for i, s in st.items() if s != "passing"}
    dependents = rank._dependents(feats, failing)
    defect_of: dict[str, list[str]] = {}
    for d in json.loads(DEFECTS.read_text(encoding="utf-8"))["defects"]:
        for f in d["feature"]:
            defect_of.setdefault(f, []).append(d["id"])
    hold = rank.held(feats, reqs)
    try:
        wires = wiring.findings()
    except Exception:  # noqa: BLE001 — the board must render
        wires = []
    structural = {w["name"] for w in wires if w.get("check") == 3 and "drives neither" in w.get("finding", "")}
    waits = features.awaiting(feats, st)
    rows = []
    for f in feats:
        file, _, func = f["test"].partition("::")
        calls = wiring._test_calls(features.PROJECT / file, func)
        stub = bool(calls and calls[1])
        # Founder 2026-09-28: a passing test the wiring check flags as not end to end (it drives
        # neither the graph nor the API) is built, not done, until it is end to end.
        not_e2e = f["id"] in structural
        # Colour = state, three states (founder 2026-09-30). Proven only on earlier code (ruling 1,
        # 2026-09-29) is built, not done: nothing is done unless it is proven on the current code.
        if st[f["id"]] == "passing":
            status = "amber" if not_e2e else "green"
        else:
            status = "amber" if (f["id"] in waits or not stub or f["id"] == nxt.get(f["lane"])) else "grey"
        req = reqs.get(f["requirement"]) or {}
        r = by_rank.get(f["id"]) or {}
        rows.append({"id": f["id"], "description": f["description"], "lane": f["lane"],
                     "stage": f.get("stage"), "layer": f.get("layer"), "phase": f.get("phase", "define"),
                     "status": status, "awaiting": f["id"] in waits, "tier": tiers.get(f["id"]), "rank": r.get("rank"),
                     "held": hold.get(f["id"]), "not_e2e": not_e2e, "stub": stub, "requirement": f["requirement"],
                     "moscow": req.get("moscow"), "hidden": req.get("moscow") == "Won't-now", "pilot": f.get("pilot"),
                     "test": f["test"], "depends_on": f["depends_on"], "unblocks": sorted(dependents.get(f["id"], ())),
                     "defects": defect_of.get(f["id"], [])})
    open_ids = {x["id"] for x in rows if x["status"] != "green"}
    for x in rows:
        x["blocker"] = _blocker(x, open_ids)
    j = journey()
    _journey_features(j, rows)
    return {"model": model(), "features": rows, "count": count(rows), "journey": j,
            "phases": live_phases(), "waiting": waiting_on_you(), "built_on": built_on()}


# ── the page ────────────────────────────────────────────────────────────────

CSS = """
:root{--ground:#F3F5F4;--panel:#FFFFFF;--ink:#17201D;--muted:#5B6763;--line:#CBD4D0;--sub:#EEF2F1;
--done:#2F8A55;--wip:#E0962A;--open:#C3CAC7;--accent:#1D5E73;--accent-bg:#E4EFF2;
--sans:system-ui,-apple-system,"Segoe UI",sans-serif;--mono:ui-monospace,"Cascadia Mono",Consolas,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--ground:#121716;--panel:#1A2120;--ink:#E4EAE7;--muted:#9AA7A2;--line:#2E3936;--sub:#202927;--done:#5CC08A;--wip:#F0B04E;--open:#4A5552;--accent:#6FB3C7;--accent-bg:#1B2C31}}
:root[data-theme="dark"]{color-scheme:dark;--ground:#121716;--panel:#1A2120;--ink:#E4EAE7;--muted:#9AA7A2;--line:#2E3936;--sub:#202927;--done:#5CC08A;--wip:#F0B04E;--open:#4A5552;--accent:#6FB3C7;--accent-bg:#1B2C31}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);font:14px/1.5 var(--sans);margin:0;padding:20px 16px 48px}
.wrap{max-width:1120px;margin:0 auto;display:flex;flex-direction:column;gap:14px}
h1,h2{font-weight:600;margin:0}h1{font-size:21px}h2{font-size:15px}
.mut,.note{color:var(--muted)}.small,.note{font-size:12px}
.top{display:flex;justify-content:space-between;align-items:baseline;flex-wrap:wrap;gap:8px}
.tabs{display:flex;gap:4px;flex-wrap:wrap}
.tab{padding:5px 14px;border-radius:6px;border:1px solid var(--line);background:var(--panel);font-weight:600}
.tab.on{border-color:var(--accent);color:var(--accent)}.tab.off{color:var(--muted);font-weight:400;background:transparent}
.ms{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px}
.m{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 12px;cursor:pointer;text-align:left;font:inherit;color:inherit;display:flex;flex-direction:column}
.m.sel{border:2px solid var(--accent);padding:9px 11px}.m b{font-size:13px}
.m .big{font-size:20px;font-weight:700;margin-top:2px;font-variant-numeric:tabular-nums}
.bar{height:6px;background:var(--open);border-radius:3px;overflow:hidden;display:flex;margin-top:6px}.bar i{display:block;height:100%}
.bar .d{background:var(--done)}.bar .b{background:var(--wip)}
.card{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:14px;display:flex;flex-direction:column;gap:10px;min-width:0}
.jhead{margin:4px 0 0;font-size:13px;font-weight:500}
.journey{display:grid;grid-template-columns:1fr 3.2fr 1fr 1fr 1fr 1fr;gap:6px}
@media (max-width:700px){.journey{grid-template-columns:1fr 1fr}}
.stage{border-radius:6px;padding:8px;font-size:12.5px;font-weight:500;display:flex;flex-direction:column;gap:6px;border:1px solid var(--line);cursor:pointer}
.stage.done{background:color-mix(in srgb,var(--done) 18%,var(--panel));border-color:var(--done)}
.stage.wip{background:color-mix(in srgb,var(--wip) 22%,var(--panel));border-color:var(--wip)}
.els{display:grid;grid-template-columns:repeat(13,1fr);gap:3px}
.el{aspect-ratio:1;border-radius:3px;background:var(--panel);border:1px solid var(--line);cursor:pointer}.el.miss{background:var(--open);border-color:var(--open)}.el.done{background:var(--done);border-color:var(--done)}.el.wip{background:var(--wip);border-color:var(--wip)}
.guide{font-size:12px;color:var(--muted);margin:4px 0 0;border-top:1px solid var(--line);padding-top:10px}
.gridwrap{overflow-x:auto}
.vs{display:grid;grid-template-columns:128px 1fr 2.6fr 1fr 1fr 1fr 1fr;gap:3px;min-width:820px}
.vs .h{font-size:12px;font-weight:600;padding:4px;text-align:center}
.vs .lay{font-size:12px;font-weight:600;padding:6px 4px;display:flex;flex-direction:column;justify-content:center}
.vs .lay small{font-weight:400;color:var(--muted)}
.cell{background:var(--ground);border-radius:6px;padding:5px;display:flex;flex-wrap:wrap;gap:3px;align-content:flex-start;min-height:34px}
.t{width:13px;height:13px;border-radius:3px;cursor:pointer;border:0;padding:0;transition:opacity .15s;display:inline-block}
.t.green{background:var(--done)}.t.amber{background:var(--wip)}.t.grey{background:var(--open)}
.t.fade{opacity:.12}.t.pick{outline:2px solid var(--accent);outline-offset:1px}
.legend{display:flex;gap:6px 14px;flex-wrap:wrap;font-size:12px;color:var(--muted);align-items:center}.legend span{display:inline-flex;gap:5px;align-items:center}
.cols{display:grid;grid-template-columns:2fr 1fr;gap:14px;align-items:start}@media (max-width:820px){.cols{grid-template-columns:1fr}}
.grp{border-top:1px solid var(--line);padding:8px 0}.grp:first-of-type{border-top:0}
.grp summary{cursor:pointer;font-weight:600}.grp summary span{color:var(--muted);font-weight:400}
.grp .gloss{font-size:12px;color:var(--muted);margin-left:1.1em}
.grp ul{margin:6px 0 0;padding:0;list-style:none}
.grp li{font-size:12.5px;padding:3px 0;border-top:1px dashed var(--line)}
.dot{display:inline-block;width:8px;height:8px;border-radius:2px;margin-right:5px}.dot.amber{background:var(--wip)}.dot.grey{background:var(--open)}.dot.green{background:var(--done)}
.side ol,.side ul{padding-left:18px;margin:0}.side li.none{list-style:none;margin-left:-18px}.side li{margin:0 0 6px;font-size:12.5px}
#detail{font-size:12.5px}#detail dl{margin:6px 0 0}#detail dt,#panel dt{font-weight:600;font-size:12px;color:var(--muted);margin-top:6px}#detail dd,#panel dd{margin:0;overflow-wrap:anywhere}
a{color:var(--accent)}code{font:12px var(--mono)}a code{color:inherit}
#tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--panel);font-size:12px;padding:6px 8px;border-radius:6px;max-width:340px;z-index:10;display:none}
#panel{position:fixed;top:0;right:0;height:100%;width:min(420px,100%);background:var(--panel);border-left:1px solid var(--line);padding:16px;overflow:auto;transform:translateX(100%);transition:transform .15s;z-index:9}
#panel.open{transform:none}#panel dd{font-size:13px}
#panel button{float:right;background:none;border:1px solid var(--line);border-radius:6px;color:var(--ink);cursor:pointer}
svg{height:auto;display:block}
"""

JS = r"""
const D=JSON.parse(document.getElementById('board-data').textContent);
const F=Object.fromEntries(D.features.map(f=>[f.id,f]));
const MS=D.count.milestones;
const tip=document.getElementById('tip'),panel=document.getElementById('panel'),body=document.getElementById('panel-body');
function esc(s){return String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
document.addEventListener('mouseover',e=>{const t=e.target.closest('[data-tip]');if(!t){tip.style.display='none';return}
 tip.textContent=t.dataset.tip;tip.style.display='block'});
document.addEventListener('mousemove',e=>{tip.style.left=Math.min(e.clientX+12,innerWidth-360)+'px';tip.style.top=(e.clientY+14)+'px'});
function dl(pairs){return '<dl>'+pairs.map(([k,v])=>'<dt>'+esc(k)+'</dt><dd>'+v+'</dd>').join('')+'</dl>'}
function links(ids){return ids.map(d=>'<a href="#" data-f="'+d+'">'+d+'</a>').join(', ')||'—'}
function milestoneOf(id){const m=MS.slice(1).find(x=>x.ids.includes(id));return m?m.name+' ('+m.code+')':'no milestone'}
function feature(id){const f=F[id];if(!f)return '';return '<b>'+esc(f.id)+'</b> · '+esc(D.words[f.status])+'<br>'+esc(f.description)+dl([
 ['Where',esc((D.stages[f.stage]||f.stage)+' · '+(D.layers[f.layer]||f.layer))],['Milestone',esc(milestoneOf(id))],
 ['Order of work',f.rank?'#'+f.rank:(f.status==='green'?'done':'not in the order of work')],
 ['What stands between it and done',esc(f.blocker||'nothing — it is done')],
 ['Requirement',esc(f.requirement+' · '+(f.moscow||'?'))],['Test','<code>'+esc(f.test)+'</code>'],
 ['Depends on',links(f.depends_on)],['Unblocks',links(f.unblocks)],['Registered defects',esc(f.defects.join(', ')||'—')]])}
function open(h){body.innerHTML=h;panel.classList.add('open')}
function behind(ids){return ids.length?'<ul>'+ids.map(i=>{const f=F[i]||{};return '<li><a href="#" data-f="'+i+'">'+esc(i)+'</a> · '
 +esc(D.words[f.status]||'')+(f.rank?' · #'+f.rank:'')+' — '+esc(String(f.description||'').slice(0,110))+'</li>'}).join('')+'</ul>':'—'}
function lines(xs){return xs.map(esc).join('<br>')}
function element(i){const e=D.journey.elements[i];return '<h2>'+esc(e.n+' · '+e.name)+'</h2>'+dl([
 ['What the Belt provides',esc(e.what)],['Why it matters',esc(e.why)],
 ['Acceptance criteria (the Define skill, from R7)','<ul>'+e.criteria.map(([k,t])=>'<li><code>'+esc(k)+'</code> — '+esc(t)+'</li>').join('')+'</ul>'],
 ['In this run: '+e.state,lines(e.happened)+'<br><span class="note">'+esc(D.journey.file||'')+'</span>'],
 ['Fields',e.fields.map(x=>'<code>'+esc(x)+'</code>').join(', ')],['Features behind it',behind(e.features)]])}
function stage(k){const s=D.journey.stages[k];return '<h2>'+esc(s.label)+'</h2>'+dl([
 ['What happens at this stage',esc(s.what)+'<br><span class="note">'+esc(s.source)+'</span>'],
 ['In this run',lines(s.happened)+'<br><span class="note">'+esc(D.journey.file||'')+'</span>'],['Features behind it',behind(s.features)]])}
function select(k){if(!MS.some(m=>m.key===k))k=D.count.default;
 document.querySelectorAll('.m[data-ms]').forEach(b=>{const on=b.dataset.ms===k;b.classList.toggle('sel',on);b.setAttribute('aria-pressed',String(on))});
 document.querySelectorAll('.vs .t').forEach(t=>t.classList.toggle('fade',!t.dataset.ms.split(' ').includes(k)));
 document.querySelectorAll('[data-for]').forEach(s=>{s.hidden=s.dataset.for!==k});
 try{history.replaceState(null,'','#'+k)}catch(e){}}
function pick(id){document.querySelectorAll('.vs .t.pick').forEach(t=>t.classList.remove('pick'));
 const t=document.querySelector('.vs .t[data-f="'+id+'"]');if(t){t.classList.add('pick');t.scrollIntoView({block:'nearest',inline:'nearest'})}
 document.getElementById('detail').innerHTML=feature(id)}
document.addEventListener('click',e=>{const el=e.target.closest('[data-el]');if(el){open(element(+el.dataset.el));return}
 const sg=e.target.closest('[data-stage]');if(sg){open(stage(sg.dataset.stage));return}
 const b=e.target.closest('.m[data-ms]');if(b){select(b.dataset.ms);return}
 const a=e.target.closest('[data-f]');if(a){e.preventDefault();pick(a.dataset.f);if(a.closest('#panel'))open(feature(a.dataset.f));return}
 if(e.target.closest('#close'))panel.classList.remove('open')});
select(decodeURIComponent(location.hash.slice(1))||D.count.default);
"""


def _spark(spark: list[dict], n: int) -> str:
    if not spark:
        return ""
    W, H = 160, 28
    pts = [(6 + i * (W - 12) / max(len(spark) - 1, 1), H - 4 - s["elements"] / max(n, 1) * (H - 8)) for i, s in enumerate(spark)]
    path = " ".join(f"{'M' if i == 0 else 'L'}{a:.1f},{b:.1f}" for i, (a, b) in enumerate(pts))
    dots = "".join(f"<circle cx='{a:.1f}' cy='{b:.1f}' r='2.5' fill='var(--accent)' data-tip='{E(s['run'])}: "
                   f"{s['elements']} of {n} elements, {s['turns']} turns'/>" for (a, b), s in zip(pts, spark))
    return (f"<svg viewBox='0 0 {W} {H}' style='width:160px' role='img' aria-label='Run-throughs'>"
            f"<path d='{path}' fill='none' stroke='var(--accent)'/>{dots}</svg>")


#: The Belt journey strip's heading, as the founder worded it (control board item 0c, 2026-09-29).
JOURNEY_HEADING = ("Latest live test: a scripted Belt goes through Define on the real system · green = got through · "
                   "amber = stuck · grey = reached, not saved · white = not reached")
GUIDE = ("How to read it: columns are the Belt's journey, rows are the part of the software, and colour is the "
         "state. Pick a milestone above: its tiles light up, and the list below shows only what's left in it.")
STATE_ORDER = {"green": 0, "amber": 1, "grey": 2}


def one_line(text: str, n: int = 140) -> str:
    """A description's first sentence, cut to n characters — what a tile's hover shows."""
    first = re.split(r"(?<=\.)\s", text.strip(), maxsplit=1)[0]
    return first if len(first) <= n else first[: n - 1].rstrip() + "…"


_CODE = re.compile(r"`([^`]+)`")


def _code(m: re.Match) -> str:
    return f"<code>{m.group(1)}</code>"


def _pct(n: int, d: int) -> float:
    return 100 * n / d if d else 0


def _journey_card(j: dict) -> str:
    """The Belt journey strip — unchanged by the redesign; it heads the value stream's card."""
    els = "".join(f"<i class='el {s}' data-el='{i}' data-tip='{i + 1} · {E(e['name'])} — {E(e['state'])}'></i>"
                  for i, (s, e) in enumerate(zip(j["elements"], j["element_detail"])))
    stages = "".join(f"<div class='stage {j['stages'][k]}' data-stage='{k}' data-tip='{E(label)}: {j['stages'][k]}'>{E(label)}"
                     + (f"<div class='els'>{els}</div>" if k == "coached" else "") + "</div>" for k, label in STAGES)
    stale = " · <b>the record is older than the product source</b>" if j.get("stale") else ""
    return (f"<div><h2>Belt journey</h2><p class=\"jhead\" data-key=\"journey-subtitle\">{E(JOURNEY_HEADING)}</p>"
            f"<p class=\"note\" data-key=\"journey-date\">Run of {E(j.get('date') or 'no run recorded')}</p></div>"
            f"<div class=\"journey\">{stages}</div>"
            f"<div class=\"note\">{E(j['note'])}{stale} · <code>{E(j['file'] or '—')}</code></div>"
            f"<div>{_spark(j['spark'], len(j['names']))}</div>")


def render(d: dict) -> str:
    m, fs, c, b = d["model"], d["features"], d["count"], d["built_on"]
    by_id = {f["id"]: f for f in fs}
    member: dict[str, list[str]] = {}
    for x in c["milestones"]:
        for i in x["ids"]:
            member.setdefault(i, []).append(x["key"])
    tabs = "".join(f"<span class='tab on'>{p.capitalize()}</span>" if p == "define" else
                   f"<span class='tab{'' if p in d['phases'] else ' off'}'>{p.capitalize()}"
                   f"{'' if p in d['phases'] else ' · not started'}</span>" for p in PHASES)
    buttons = "".join(
        f"<button type='button' class='m' data-ms='{x['key']}' aria-pressed='false' data-tip='{E(x['name'])}: "
        f"{x['done']} done · {x['built']} built, not yet proven · {x['not_started']} not started — of {x['total']}'>"
        f"<b>{E(x['name'])}</b><span class='small mut'>{E(x['code'])}</span>"
        f"<span class='big'>{x['done']}<span class='small mut'> / {x['total']} done</span></span>"
        f"<span class='bar'><i class='d' style='width:{_pct(x['done'], x['total']):.1f}%'></i>"
        f"<i class='b' style='width:{_pct(x['built'], x['total']):.1f}%'></i></span></button>" for x in c["milestones"])
    pilot = "" if c["pilot_ruled"] else f"<p class='note' data-key='pilot'>Ready for pilot / Before customers: {PILOT_NOT_RULED}.</p>"

    head = "<div></div>" + "".join(f"<div class='h'>{E(label)}</div>" for _, label in STAGES)
    cells = []
    for lk, ll, gloss in LAYERS:
        cells.append(f"<div class='lay'>{E(ll)}<small>{E(gloss)}</small></div>")
        for sk, _ in STAGES:
            mine = sorted((f for f in fs if f["stage"] == sk and f["layer"] == lk and not f["hidden"]),
                          key=lambda f: (STATE_ORDER[f["status"]], *_order(f)))
            cells.append("<div class='cell'>" + "".join(
                f"<button type='button' class='t {f['status']}' data-f='{f['id']}' data-ms='{' '.join(member[f['id']])}' "
                f"data-tip='{E(f['id'])} — {E(one_line(f['description']))}' aria-label='{E(f['id'])}'></button>"
                for f in mine) + "</div>")
    hidden = ("" if not c["hidden"] else
              f"<span data-key='hidden'>not shown: {len(c['hidden'])} feature(s) deferred (Won't-now) — {E(', '.join(c['hidden']))}</span>")

    def item(i: str) -> str:
        f = by_id[i]
        return (f"<li><i class='dot {f['status']}'></i><a href='#' data-f='{i}'><code>{E(i)}</code></a> "
                f"{E(one_line(f['description'], 110))}</li>")

    def group(g: dict) -> str:
        built = f" ({g['built']} built, to prove)" if g["built"] else ""
        gloss = next(gl for lk, _, gl in LAYERS if lk == g["layer"])
        return (f"<details class='grp' data-layer='{g['layer']}'><summary><b>{E(g['name'])}</b> <span>· "
                f"<span data-n='{len(g['left'])}'>{len(g['left'])} left</span>{built}</span></summary>"
                f"<div class='gloss'>{E(gloss)}</div><ul>{''.join(item(i) for i in g['left'])}</ul></details>")

    lefts, nexts = [], []
    for x in c["milestones"]:
        hide = "" if x["key"] == c["default"] else " hidden"
        groups = "".join(group(g) for g in x["groups"])
        lefts.append(f"<section data-for='{x['key']}'{hide}><h2>What's left · {E(x['name'])} · {len(x['left'])}</h2>"
                     + (groups or "<p class='mut'>Nothing left. This milestone is done.</p>") + "</section>")
        nexts.append(f"<ol data-for='{x['key']}'{hide}>"
                     + ("".join(f"<li><a href='#' data-f='{i}'><code>{E(i)}</code></a> {E(one_line(by_id[i]['description'], 80))}</li>"
                                for i in x["next"]) or "<li class='mut none'>nothing open in the order of work</li>") + "</ol>")
    waiting = ("" if not d["waiting"] else
               "<h2>Waiting on you</h2><ul data-key='waiting'>"
               + "".join(f"<li>{_CODE.sub(_code, E(w))}</li>" for w in d["waiting"]) + "</ul>")

    progress = json.dumps({k: m[k] for k in ("headline", "passing", "total", "statuses", "next")},
                          ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    j = d["journey"]
    journey = {"elements": j["element_detail"], "stages": j["stage_detail"], "file": j["file"]}
    board = json.dumps({"features": fs, "count": c, "journey": journey, "stages": dict(STAGES),
                        "layers": {k: n for k, n, _ in LAYERS}, "words": STATE_WORDS},
                       ensure_ascii=False).replace("</", "<\\/")
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Control board</title>
<style>{CSS}</style></head><body><div class="wrap">
<header class="top"><h1>Agent Improve · Control board</h1><span class="mut small" data-key="built-on">{E(b['branch'])} @ {E(b['sha'])} · {E(b['date'])} · every number from one count</span></header>
<nav class="tabs">{tabs}</nav>
<div><div class="ms">{buttons}</div>{pilot}</div>
<div class="card">{_journey_card(j)}
<p class="guide" data-key="guide">{E(GUIDE)}</p>
<div class="gridwrap"><div class="vs" data-tiles="{c['tiles']}">{head}{''.join(cells)}</div></div>
<div class="legend" data-key="legend"><span><i class="t green"></i>done (passes end to end)</span><span><i class="t amber"></i>built, not yet proven</span><span><i class="t grey"></i>not started</span><span><i class="t grey fade"></i>other milestone</span>{hidden}</div>
</div>
<div class="cols">
<div class="card" id="left">{''.join(lefts)}</div>
<div class="card side">{waiting}<h2>Next up</h2>{''.join(nexts)}<h2>Selected tile</h2><div id="detail" class="mut">Click a tile.</div></div>
</div>
</div>
<div id="tip" role="tooltip"></div>
<aside id="panel" aria-label="Detail"><button id="close" type="button">Close</button><div id="panel-body"></div></aside>
<script type="application/json" id="progress-data">{progress}</script>
<script type="application/json" id="board-data">{board}</script>
<script>{JS}</script>
</body></html>
"""


def build(out: Path = OUT) -> Path:
    out.write_text(render(data()), encoding="utf-8")
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    print(f"control board -> {build(Path(args[0]) if args else OUT)}")
