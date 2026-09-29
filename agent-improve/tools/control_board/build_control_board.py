"""Render `docs/control-board.html` — THE ONE PAGE, a value-stream picture. Brief Part F7
(founder, 2026-09-27); the layout is `docs/founder-inputs/control-board-mockup.html`'s.

Run by the pre-commit hook after `rank.py` and `wiring.py`. Inputs, nothing typed by hand:
every `docs/*_features.json` (Define today), `docs/test-results.json`, `docs/defects.json`,
business.md and platform.md, `docs/adr/`, the latest run-through record, the wiring findings,
`.claude/logs/prompts.jsonl`, `.claude/config/mypy-ratchet.json` and git log.

Top to bottom: phase tabs · Define complete (%, M1-M3 bars) · the Belt journey (the latest
run-through, a sparkline of the runs) · the value stream (stages × layers, one tile per
feature) · now per lane (with the next work package) · prompt flow · waiting for you · the
health strip · burn-up per milestone · last commits (collapsed). Hover shows a tooltip; a
click opens the side panel with everything behind a tile, bar or counter.

The Belt journey: each element square opens what the Belt provides, why it matters and its
acceptance criteria (the Define skill), what happened to it in the run (the run record) and the
features behind it; each stage square opens what happens there (the skill or business.md, per
`STAGE_SOURCES`), what happened in the run and the stage's features. White = not reached.

A feature's status is derived, never stored: green = its test passes; amber = its test is
written and fails, or it is its lane's current top-ranked feature; grey = open (a stub);
awaiting (green with a clock) = proven only by a live run-through whose record is older than the
source — not open, counted apart (founder ruling 1, 2026-09-29; `features.awaiting`).
In each cell the squares stand in the order of work (rank). A tier-1 (M1) square carries a
thick outline and its position in the order of work (tooling, founder 2026-09-28).

The page embeds `progress-data` (headline, statuses, next per lane) for `check_board.py`
(the commit guard's rule 10) and the session start.

    python tools/control_board/build_control_board.py [out.html] [--staged]
"""
from __future__ import annotations

import datetime as dt
import html
import json
import re
import statistics
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
PROMPTS = REPO / ".claude" / "logs" / "prompts.jsonl"
MYPY = REPO / ".claude" / "config" / "mypy-ratchet.json"
PHASES = ("define", "measure", "analyse", "improve", "control")
STAGES = (("open_case", "Open case"), ("coached", "Works through the 13 elements"), ("report", "Report"),
          ("approve", "Approve"), ("record_written", "Record written"), ("next_phase", "Next phase opens"))
#: The row names the founder ruled (control board item 0d, 2026-09-29).
LAYERS = (("screen", "What the Belt sees (Screen)"), ("api", "Screen ↔ coach connection (API)"),
          ("coaching", "What the coach does (Coaching)"), ("gate", "Checks and approval (Gate)"),
          ("persistence", "What is saved (Persistence)"), ("platform", "Security, speed, operations (Platform)"))
E = html.escape
#: The milestone names the founder ruled (BRIEF_m1_loop.md Part 1b, 2026-09-28).
MILESTONE_LABELS = {"M1": "M1 — must work for one Belt to finish Define", "M2": "M2 — the other must-haves",
                    "M3": "M3 — should- and could-haves"}


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


def _last_commit_per_test_file() -> dict[str, str]:
    out: dict[str, str] = {}
    cur = ""
    for line in _git("log", "-300", "--format=@%h %ad", "--date=short", "--name-only", "--",
                     "agent-improve/backend/tests").splitlines():
        if line.startswith("@"):
            cur = line[1:]
        elif line.strip() and line not in out:
            out[line.strip()] = cur
    return out


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


def milestone_counts(rows: list[dict]) -> dict[str, dict]:
    """THE milestone count — the box, the stage footers, the milestone panel, "What's left" and
    today's burn-up point all read this one function (control board item 0a, founder
    2026-09-29). Done = the square is green; every other square of the milestone is open, in
    the order of work. It used to be counted three ways — green squares (the box), numbered
    squares (the grid) and passing tests (the hand-written M1 line) — and they disagreed
    whenever a feature passed a test that is not end to end.

    Founder ruling 1, 2026-09-29: a square proven only on earlier code (status "awaiting") is
    neither done nor open — green + awaiting + open = total."""
    out: dict[str, dict] = {}
    for m, t in rank.MILESTONES.items():
        mine = [r for r in rows if r["tier"] == t]
        done = sorted((r for r in mine if r["status"] == "green"), key=_order)
        wait = sorted((r for r in mine if r["status"] == "awaiting"), key=_order)
        left = sorted((r for r in mine if r["status"] not in ("green", "awaiting")), key=_order)
        out[m] = {"m": m, "label": MILESTONE_LABELS[m], "tier": t, "total": len(mine), "green": len(done),
                  "awaiting": len(wait), "amber": sum(r["status"] == "amber" for r in left),
                  "done": [r["id"] for r in done], "waiting": [r["id"] for r in wait],
                  "open": [r["id"] for r in left]}
    return out


def triple(x: dict) -> str:
    """A milestone's three counts, as the founder worded them (ruling 1, 2026-09-29)."""
    return f"{x['green']} proven · {x['awaiting']} awaiting fresh run · {len(x['open'])} open"


def _blocker(f: dict, open_ids: set[str]) -> str:
    """What stands between an open feature and done, in the Belt-free words the panel shows."""
    if f["status"] == "green":
        return ""
    if f["status"] == "awaiting":
        return "a fresh run-through on the current source (it passed on the latest record, run on earlier code)"
    if f["held"]:
        return f"the design gate: {f['held']} is not ACCEPTED"
    deps = [d for d in f["depends_on"] if d in open_ids]
    if deps:
        return "waits for " + ", ".join(deps)
    if f["not_e2e"]:
        return "its test passes but does not drive the API or the graph (not end to end)"
    if f["stub"]:
        return "nothing — ready to build (its test is not written yet)"
    return "nothing — ready to build (its test is written and fails)"


def _waiting(reqs: dict[str, dict], records: dict[str, dict], hold: dict[str, str]) -> list[dict]:
    proposed = sorted((i for i, r in reqs.items() if r["status"] in ("PROPOSED", "DRAFT")),
                      key=lambda i: (i[0], int(re.sub(r"\D", "", i) or 0)))
    gated = [n for n, r in records.items() if r["status"] == "PROPOSED" and adrs.gated(n)]
    draft = [n for n, r in records.items() if r["status"] == "PROPOSED" and not adrs.gated(n)]
    unrated = [i for i, r in reqs.items() if r["moscow"] == "?" and r["status"] not in ("RETIRED",)]
    business = (features.REQUIREMENTS / "business.md").read_text(encoding="utf-8")
    block = business[business.find("## Open decisions"):business.find("# Part 1")]
    decisions = re.findall(r"^\| (\d+) \| ([^|]+) \|", block, re.M)
    held_by = {n: sorted(f for f, a in hold.items() if a == f"ADR-{n}") for n in gated}
    return [
        *[{"tag": "ADR", "text": f"ADR-{n} PROPOSED — holds {len(held_by[n])} feature(s)",
           "items": [f"ADR-{n} {records[n]['title']}", *held_by[n]]} for n in gated],
        {"tag": "ADR", "text": f"ADR 0001–0056: {len(draft)} of the architecture sort's drafts PROPOSED",
         "items": [f"ADR-{n} {records[n]['title']}" for n in draft]},
        {"tag": "Req", "text": f"{len(proposed)} requirements PROPOSED or DRAFT", "items": proposed},
        {"tag": "?", "text": f"MoSCoW for {len(unrated)} requirements", "items": sorted(unrated)},
        {"tag": "Dec", "text": f"{len(decisions)} open decisions in business.md",
         "items": [f"{n}: {q.strip()}" for n, q in decisions]},
    ]


def _health(feats: list[dict], st: dict[str, str], reqs: dict[str, dict], wires: list[dict]) -> list[dict]:
    defects = json.loads(DEFECTS.read_text(encoding="utf-8"))["defects"]
    open_defects = [d for d in defects if d["feature"] and any(st.get(f) != "passing" for f in d["feature"])]
    ok = features.citable(reqs)
    cited = {f["requirement"] for f in feats}
    uncovered = sorted(i for i in ok if (not i.startswith("T") or reqs[i]["proof_none"]) and i not in cited)
    try:
        types = json.loads(MYPY.read_text(encoding="utf-8"))
        record = types.get("errors", types.get("count", types.get("record", "?")))
    except (OSError, ValueError):
        record = "?"
    return [
        {"n": len(open_defects), "label": "open defects",
         "items": [f"{d['id']} → {', '.join(d['feature'])} (lane {', '.join(d['lane'])})" for d in open_defects]},
        {"n": len(wires), "label": "wiring findings", "items": [w["finding"] for w in wires]},
        {"n": len(uncovered), "label": "accepted requirements without a feature", "items": uncovered},
        {"n": record, "label": "type-error record", "items": [".claude/config/mypy-ratchet.json — may fall, never rise (rule 3b)"]},
    ]


def _prompts() -> list[dict]:
    if not PROMPTS.is_file():
        return []
    out = []
    for line in PROMPTS.read_text(encoding="utf-8").splitlines()[-15:]:
        try:
            r = json.loads(line)
        except ValueError:
            continue
        m = {k: float(v["value"]) for k, v in (r.get("minutes") or {}).items()}
        out.append({"subject": r.get("subject", ""), "start": r.get("start", ""), "commits": len(r.get("commits") or []),
                    "features": r.get("features") or [], "building": m.get("building", 0),
                    "tests_hooks": m.get("tests", 0) + m.get("hooks", 0),
                    "waiting": m.get("waiting_for_founder", 0), "rework": m.get("rework", 0),
                    "total": m.get("total", 0)})
    return out


def burnup(feats: list[dict], tiers: dict[str, int | None]) -> list[dict]:
    """Per day: passing features in all and per milestone, from git log of test-results.json."""
    rows = _git("log", "--format=%H %ad", "--date=short", "--since=30 days ago", "--",
                "agent-improve/docs/test-results.json").split("\n")
    last: dict[str, str] = {}
    for row in reversed([r for r in rows if r.strip()]):
        sha, day = row.split()
        last[day] = sha
    points = []

    def count(res: dict, day: str) -> dict:
        st = features.status(feats, res)
        p = {"day": day, "all": sum(v == "passing" for v in st.values())}
        for m, t in rank.MILESTONES.items():
            p[m] = sum(1 for i, v in st.items() if v == "passing" and tiers.get(i) == t)
        return p

    for day, sha in sorted(last.items()):
        try:
            points.append(count(json.loads(_git("show", f"{sha}:agent-improve/docs/test-results.json") or "{}"), day))
        except ValueError:
            continue
    today = dt.date.today().isoformat()
    now = count(features.results(), today)
    if points and points[-1]["day"] == today:
        points[-1] = now
    else:
        points.append(now)
    return points


def commits(n: int = 12) -> list[dict]:
    out = []
    for block in _git("log", f"-{n}", "--format=%h%x1f%ad%x1f%s%x1f%b%x1e", "--date=short").split("\x1e"):
        parts = block.strip().split("\x1f")
        if len(parts) < 4:
            continue
        sha, day, subject, body = parts
        timing = next((ln.split(":", 1)[1].strip() for ln in body.splitlines() if ln.startswith("Timing:")), "")
        out.append({"sha": sha, "day": day, "subject": subject, "timing": timing})
    return out


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
    pk = rank.packages(feats, ranked, res)
    failing = {i for i, s in st.items() if s != "passing"}
    dependents = rank._dependents(feats, failing)
    last = _last_commit_per_test_file()
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
        tops = f["id"] == nxt.get(f["lane"])
        # Founder 2026-09-28: a passing test the wiring check flags as not end to end (it drives
        # neither the graph nor the API) is amber, not green, until it is end to end.
        not_e2e = f["id"] in structural
        status = (("green" if not not_e2e else "amber") if st[f["id"]] == "passing" else
                  "awaiting" if f["id"] in waits else ("amber" if (not stub or tops) else "grey"))
        req = reqs.get(f["requirement"]) or {}
        r = by_rank.get(f["id"]) or {}
        rows.append({"id": f["id"], "description": f["description"], "lane": f["lane"],
                     "stage": f.get("stage"), "layer": f.get("layer"), "phase": f.get("phase", "define"),
                     "status": status, "tier": tiers.get(f["id"]), "rank": r.get("rank"),
                     "reason": ("proven on earlier code — awaiting a fresh run-through" if status == "awaiting"
                                else r.get("reason") or ("passes, but its test is not end to end (wiring check 3)"
                                                         if not_e2e else "passes — not ranked")),
                     "held": hold.get(f["id"]), "not_e2e": not_e2e, "stub": stub, "requirement": f["requirement"],
                     "moscow": req.get("moscow"), "design": req.get("design"), "test": f["test"],
                     "depends_on": f["depends_on"], "unblocks": sorted(dependents.get(f["id"], ())),
                     "last_commit": last.get(f"agent-improve/{file}", "—"), "defects": defect_of.get(f["id"], []),
                     "effort": f.get("effort"), "belt_impact": f.get("belt_impact"), "rework_risk": f.get("rework_risk")})
    ranked_feats = [x for x in rows if x["tier"] is not None]
    open_ids = {x["id"] for x in rows if x["status"] != "green"}
    for x in rows:
        x["blocker"] = _blocker(x, open_ids)
        x["m"] = next((m for m, t in rank.MILESTONES.items() if t == x["tier"]), None)
    counts = milestone_counts(rows)
    miles = list(counts.values())
    points = burnup(feats, tiers)
    points[-1].update({m: c["green"] for m, c in counts.items()})   # today's point is the board's count
    lanes = []
    for lane in features.LANES:
        q = [r["id"] for r in ranked if r["lane"] == lane and not r.get("held")]
        lanes.append({"lane": lane, "name": features.LANES[lane], "now": q[0] if q else None,
                      "next": q[1] if len(q) > 1 else None, "package": pk[lane]})
    phases = [p for p in PHASES if (features.PROJECT / "docs" / f"{p}_features.json").is_file()]
    j = journey()
    _journey_features(j, rows)
    return {"model": model(), "features": rows, "complete": {
                "passing": sum(x["status"] == "green" for x in ranked_feats), "total": len(ranked_feats)},
            "milestones": miles, "journey": j, "lanes": lanes, "prompts": _prompts(),
            "waiting": _waiting(reqs, adrs.load(), hold), "health": _health(feats, st, reqs, wires),
            "burnup": points, "commits": commits(), "phases": phases}


# ── the page ────────────────────────────────────────────────────────────────

CSS = """
:root{--ground:#F3F5F4;--panel:#FFFFFF;--ink:#17201D;--muted:#5B6763;--line:#CBD4D0;--sub:#EEF2F1;
--done:#2F8A55;--wip:#E0962A;--open:#C3CAC7;--t1:#B23A30;--accent:#1D5E73;--blue:#3A6FB0;
--on-done:#FFFFFF;--sans:"IBM Plex Sans",system-ui,sans-serif;--cond:"IBM Plex Sans Condensed","IBM Plex Sans",system-ui,sans-serif;--mono:"IBM Plex Mono",ui-monospace,monospace}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){color-scheme:dark;--ground:#121716;--panel:#1A2120;--ink:#E4EAE7;--muted:#9AA7A2;--line:#2E3936;--sub:#202927;--done:#5CC08A;--wip:#F0B04E;--open:#4A5552;--t1:#F07A6E;--accent:#6FB3C7;--blue:#7FA8E0;--on-done:#121716}}
:root[data-theme="dark"]{color-scheme:dark;--ground:#121716;--panel:#1A2120;--ink:#E4EAE7;--muted:#9AA7A2;--line:#2E3936;--sub:#202927;--done:#5CC08A;--wip:#F0B04E;--open:#4A5552;--t1:#F07A6E;--accent:#6FB3C7;--blue:#7FA8E0;--on-done:#121716}
*{box-sizing:border-box}
body{background:var(--ground);color:var(--ink);font:14px/1.5 var(--sans);margin:0;padding:20px 16px 48px}
.wrap{max-width:1120px;margin:0 auto;display:flex;flex-direction:column;gap:18px}
h1,h2{font-family:var(--cond);font-weight:600;margin:0}h1{font-size:24px}h2{font-size:16px}
.meta,.note{font-size:12.5px;color:var(--muted)}
.tabs{display:flex;gap:6px;flex-wrap:wrap}
.tab{padding:6px 12px;border-radius:6px 6px 0 0;border:1px solid var(--line);border-bottom:0;background:var(--sub);color:var(--muted);font-weight:500}
.tab.on{background:var(--panel);color:var(--ink)}.tab.off{opacity:.5}
.card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:14px;display:flex;flex-direction:column;gap:10px;min-width:0}
.top{display:grid;grid-template-columns:260px 1fr;gap:18px}@media (max-width:800px){.top{grid-template-columns:1fr}}
.pct{font:600 56px/1 var(--cond);font-variant-numeric:tabular-nums}.pct small{font-size:18px;color:var(--muted);font-weight:500}
.bar{display:grid;grid-template-columns:minmax(0,15em) 1fr 56px;gap:8px;align-items:center;font-size:12.5px;cursor:pointer}
.track{height:10px;background:var(--open);border-radius:5px;overflow:hidden;display:flex}.track i{display:block;height:100%}
.track i.await{background:repeating-linear-gradient(135deg,var(--done) 0 3px,color-mix(in srgb,var(--done) 45%,var(--panel)) 3px 6px)}
.split{margin:-6px 0 2px;font-variant-numeric:tabular-nums}
.num{font:600 12px var(--mono);text-align:right;font-variant-numeric:tabular-nums}
.journey{display:grid;grid-template-columns:1fr 3.2fr 1fr 1fr 1fr 1fr;gap:6px}
@media (max-width:700px){.journey{grid-template-columns:1fr 1fr}}
.stage{border-radius:6px;padding:8px;font-size:12.5px;font-weight:500;display:flex;flex-direction:column;gap:6px;border:1px solid var(--line);cursor:pointer}
.stage.done{background:color-mix(in srgb,var(--done) 18%,var(--panel));border-color:var(--done)}
.stage.wip{background:color-mix(in srgb,var(--wip) 22%,var(--panel));border-color:var(--wip)}
.els{display:grid;grid-template-columns:repeat(13,1fr);gap:3px}
.el{aspect-ratio:1;border-radius:3px;background:var(--panel);border:1px solid var(--line);cursor:pointer}.el.miss{background:var(--open);border-color:var(--open)}.el.done{background:var(--done);border-color:var(--done)}.el.wip{background:var(--wip);border-color:var(--wip)}
.grid{overflow-x:auto}
table.vs{border-collapse:separate;border-spacing:6px;min-width:860px;width:100%}
.vs th{font:600 11.5px var(--sans);text-transform:uppercase;letter-spacing:.05em;color:var(--muted);text-align:left;padding:0 4px}
.vs td{background:var(--sub);border-radius:6px;padding:7px;vertical-align:top;min-width:110px}
.vs td.l{background:none;font-weight:600;font-size:12.5px;min-width:90px;padding-left:0}
.vs tfoot td{background:none;font:600 12px var(--mono);color:var(--muted);padding-top:0}
.tiles{display:flex;flex-wrap:wrap;gap:4px}
.t{width:16px;height:16px;border-radius:3px;cursor:pointer;display:inline-block;border:0;padding:0}
.t.green{background:var(--done)}.t.amber{background:var(--wip)}.t.grey{background:var(--open)}
.t.awaiting{background:color-mix(in srgb,var(--done) 55%,var(--panel));color:var(--ink);font:600 10px/16px var(--mono);text-align:center}
.clock{display:inline-block;width:1.1em;text-align:center;font-weight:600}
.t.m1{outline:3px solid var(--ink);outline-offset:1px;width:auto;min-width:16px;padding:0 3px;font:600 10px/16px var(--mono);font-variant-numeric:tabular-nums;color:var(--ink)}
.t.m1.green{color:var(--on-done)}.t.m1.amber{color:#17201D}.t.m1.awaiting{color:var(--ink)}
.vs .t.dim{opacity:.15}.bar.on span:first-child{font-weight:700;color:var(--accent)}
.jhead{margin:4px 0 0;font-size:13px;font-weight:500}
.explain{margin:0;padding:8px 10px;border-radius:6px;background:var(--sub);font-size:12.5px}
.lefts{display:grid;grid-template-columns:repeat(3,1fr);gap:14px}@media (max-width:800px){.lefts{grid-template-columns:1fr}}
.left h3{margin:0 0 4px;font:600 13.5px var(--cond);cursor:pointer}.left ol{margin:0;padding-left:18px;font-size:12.5px;display:flex;flex-direction:column;gap:4px}
#panel h3{font:600 13.5px var(--cond);margin:14px 0 0}
.t.hl{box-shadow:0 0 0 3px var(--panel),0 0 0 6px var(--accent);position:relative;z-index:1}.t.held{background-image:repeating-linear-gradient(45deg,transparent 0 3px,var(--panel) 3px 5px)}
.legend{display:flex;flex-wrap:wrap;gap:6px 16px;font-size:12.5px;color:var(--muted);align-items:center}
.legend span{display:inline-flex;gap:6px;align-items:center}
.two{display:grid;grid-template-columns:1fr 1fr;gap:18px}@media (max-width:800px){.two{grid-template-columns:1fr}}
.row{display:grid;grid-template-columns:40px 1fr;gap:8px;font-size:13px;padding:5px 0;border-bottom:1px solid var(--line);cursor:pointer}
.row:last-child{border-bottom:0}
.lane{font:600 12px var(--mono);color:var(--accent)}
.health{display:grid;grid-template-columns:repeat(4,1fr);gap:10px}@media (max-width:700px){.health{grid-template-columns:repeat(2,1fr)}}
.h{background:var(--sub);border-radius:6px;padding:10px;display:flex;flex-direction:column;gap:2px;cursor:pointer;border:0;text-align:left;color:inherit;font:inherit}
.h b{font:600 22px var(--cond);font-variant-numeric:tabular-nums}.h span{font-size:12px;color:var(--muted)}
svg{width:100%;height:auto;display:block}
.lbl{fill:var(--muted);font-size:11px}.ax{stroke:var(--line)}
table.log{border-collapse:collapse;width:100%;font-size:12.5px}.log td{border-bottom:1px solid var(--line);padding:4px 6px;vertical-align:top}
#tip{position:fixed;pointer-events:none;background:var(--ink);color:var(--panel);font-size:12px;padding:6px 8px;border-radius:6px;max-width:340px;z-index:10;display:none}
#panel{position:fixed;top:0;right:0;height:100%;width:min(420px,100%);background:var(--panel);border-left:1px solid var(--line);padding:16px;overflow:auto;transform:translateX(100%);transition:transform .15s;z-index:9}
#panel.open{transform:none}#panel dt{font-weight:600;font-size:12px;color:var(--muted);margin-top:8px}#panel dd{margin:0;font-size:13px;overflow-wrap:anywhere}
#panel button{float:right;background:none;border:1px solid var(--line);border-radius:6px;color:var(--ink);cursor:pointer}
code{font:12px var(--mono)}
"""

JS = """
const D=JSON.parse(document.getElementById('board-data').textContent);
const F=Object.fromEntries(D.features.map(f=>[f.id,f]));
const tip=document.getElementById('tip'),panel=document.getElementById('panel'),body=document.getElementById('panel-body');
function esc(s){return String(s??'').replace(/[&<>"]/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]))}
document.addEventListener('mouseover',e=>{const t=e.target.closest('[data-tip]');if(!t){tip.style.display='none';return}
 tip.textContent=t.dataset.tip;tip.style.display='block'});
document.addEventListener('mousemove',e=>{tip.style.left=Math.min(e.clientX+12,innerWidth-360)+'px';tip.style.top=(e.clientY+14)+'px'});
function dl(pairs){return '<dl>'+pairs.map(([k,v])=>'<dt>'+esc(k)+'</dt><dd>'+v+'</dd>').join('')+'</dl>'}
function feature(id){const f=F[id];if(!f)return '';return '<h2>'+esc(f.id)+'</h2>'+dl([
 ['Description',esc(f.description)],['Requirement',esc(f.requirement)+' · MoSCoW '+esc(f.moscow)+' · Design '+esc(f.design)],
 ['Stage · Layer · Tier · Order of work',esc((D.stages[f.stage]||f.stage)+' · '+(D.layers[f.layer]||f.layer)+' · '
  +(f.tier?'tier '+f.tier+(f.tier===1?' (M1)':''):'not ranked')+' · '
  +(f.rank?'#'+f.rank+' of '+D.ranked:(f.status==='green'?'passes — out of the order':'not in the order')))],
 ['Lane',esc(f.lane)],['Status',esc(f.status)],['Held',esc(f.held||'—')],['Reason',esc(f.reason)],
 ['Belt impact · rework risk · effort',esc(f.belt_impact+' · '+f.rework_risk+' · '+f.effort)],
 ['Depends on',f.depends_on.map(d=>'<a href="#" data-f="'+d+'">'+d+'</a>').join(', ')||'—'],
 ['Unblocks',f.unblocks.map(d=>'<a href="#" data-f="'+d+'">'+d+'</a>').join(', ')||'—'],
 ['Test','<code>'+esc(f.test)+'</code>'],['Last commit touching its test file',esc(f.last_commit)],
 ['Defects',esc(f.defects.join(', ')||'—')]])}
function list(title,items){return '<h2>'+esc(title)+'</h2><ul>'+items.map(i=>{const m=String(i).match(/^DEF-\\d{3}$/);
 return '<li>'+(m?'<a href="#" data-f="'+i+'">'+i+'</a> '+esc(F[i]?F[i].description:''):esc(i))+'</li>'}).join('')+'</ul>'}
function open(h){body.innerHTML=h;panel.classList.add('open')}
function behind(ids){return ids.length?'<ul>'+ids.map(i=>{const f=F[i]||{};return '<li><a href="#" data-f="'+i+'">'+esc(i)+'</a> · '
 +esc(f.status)+' · '+(f.rank?'#'+f.rank:(f.status==='green'?'passes':'not in the order'))+' — '+esc(String(f.description||'').slice(0,110))+'</li>'}).join('')+'</ul>':'—'}
function lines(xs){return xs.map(esc).join('<br>')}
function element(i){const e=D.journey.elements[i];return '<h2>'+esc(e.n+' · '+e.name)+'</h2>'+dl([
 ['What the Belt provides',esc(e.what)],['Why it matters',esc(e.why)],
 ['Acceptance criteria (the Define skill, from R7)','<ul>'+e.criteria.map(([k,t])=>'<li><code>'+esc(k)+'</code> — '+esc(t)+'</li>').join('')+'</ul>'],
 ['In this run: '+e.state,lines(e.happened)+'<br><span class="note">'+esc(D.journey.file||'')+'</span>'],
 ['Fields',e.fields.map(x=>'<code>'+esc(x)+'</code>').join(', ')],['Features behind it',behind(e.features)]])}
function stage(k){const s=D.journey.stages[k];return '<h2>'+esc(s.label)+'</h2>'+dl([
 ['What happens at this stage',esc(s.what)+'<br><span class="note">'+esc(s.source)+'</span>'],
 ['In this run',lines(s.happened)+'<br><span class="note">'+esc(D.journey.file||'')+'</span>'],['Features behind it',behind(s.features)]])}
function dim(k){document.querySelectorAll('.vs .t').forEach(t=>t.classList.toggle('dim',!!k&&t.dataset.m!==k));
 document.querySelectorAll('.bar[data-milestone]').forEach(b=>b.classList.toggle('on',b.dataset.milestone===k))}
function milestone(k){const x=D.milestones.find(m=>m.m===k);dim(k);const by={};
 for(const id of [...x.open,...x.waiting,...x.done]){const f=F[id];const g=by[f.stage]=by[f.stage]||{done:[],wait:[],open:[]};(f.status==='green'?g.done:f.status==='awaiting'?g.wait:g.open).push(f)}
 let h='<h2>'+esc(x.label)+'</h2><p class="note">'+x.green+' proven · '+x.awaiting+' awaiting fresh run · '+x.open.length+' open, of '+x.total+' · its squares are highlighted in the value stream</p>';
 for(const [sk,label] of Object.entries(D.stages)){const g=by[sk];if(!g)continue;
  h+='<h3>'+esc(label)+'</h3>'+dl([['Open ('+g.open.length+')',g.open.length?'<ul>'+g.open.map(f=>'<li>'+(f.rank?'#'+f.rank:'—')
   +' <a href="#" data-f="'+f.id+'">'+f.id+'</a> '+esc(String(f.description).slice(0,90))+'<br><span class="note">blocked by: '+esc(f.blocker)+'</span></li>').join('')+'</ul>':'—'],
   ['Proven on earlier code, awaiting a fresh run ('+g.wait.length+')',g.wait.map(f=>'<a href="#" data-f="'+f.id+'">'+f.id+'</a>').join(', ')||'—'],
   ['Done ('+g.done.length+')',g.done.map(f=>'<a href="#" data-f="'+f.id+'">'+f.id+'</a>').join(', ')||'—']])}
 return h}
function mark(id){document.querySelectorAll('.vs .t.hl').forEach(t=>t.classList.remove('hl'));if(!id)return;
 const t=document.querySelector('.vs .t[data-f="'+id+'"]');if(t){t.classList.add('hl');t.scrollIntoView({block:'nearest',inline:'nearest',behavior:'smooth'})}}
document.addEventListener('click',e=>{const el=e.target.closest('[data-el]');if(el){mark(null);open(element(+el.dataset.el));return}
 const sg=e.target.closest('[data-stage]');if(sg){mark(null);open(stage(sg.dataset.stage));return}
 const a=e.target.closest('[data-f]');if(a){e.preventDefault();mark(a.dataset.f);open(feature(a.dataset.f));return}
 const l=e.target.closest('[data-list]');if(l){const [k,i]=l.dataset.list.split(':');const src=D[k][+i];
  open(list(src.label||src.text||src.m||src.stage||'',src.items||[]));return}
 const ms=e.target.closest('[data-milestone]');if(ms){mark(null);open(milestone(ms.dataset.milestone));return}
 if(e.target.closest('#close')){panel.classList.remove('open');mark(null);dim(null)}});
"""


def _pct(n: int, d: int) -> float:
    return 100 * n / d if d else 0


def _svg_prompts(ps: list[dict]) -> str:
    if not ps:
        return "<p class='note'>No prompt recorded yet — each prompt is recorded at its end (<code>.claude/hooks/prompt_record.py</code>).</p>"
    W, H, L, B = 640, 180, 30, 24
    top = max(max(p["total"] for p in ps), 60) * 1.1
    bw = (W - L - 10) / max(len(ps), 1)

    def y(v: float) -> float:
        return H - B - v / top * (H - B - 10)

    bars = []
    for i, p in enumerate(ps):
        x, base = L + i * bw + 2, 0.0
        tip = (f"{p['subject']} · {p['commits']} commits · {', '.join(p['features']) or 'no DEF'} · "
               f"{p['total']:.0f} min (building {p['building']:.0f}, tests and hooks {p['tests_hooks']:.0f}, "
               f"waiting {p['waiting']:.0f}, rework {p['rework']:.0f})")
        for key, colour in (("building", "var(--done)"), ("tests_hooks", "var(--blue)"),
                            ("waiting", "var(--open)"), ("rework", "var(--t1)")):
            v = p[key]
            bars.append(f"<rect x='{x:.1f}' y='{y(base + v):.1f}' width='{bw - 4:.1f}' height='{y(base) - y(base + v):.1f}' "
                        f"fill='{colour}' data-tip='{E(tip)}'/>")
            base += v
    med = statistics.median(p["total"] for p in ps)
    return (f"<svg viewBox='0 0 {W} {H}' role='img' aria-label='Prompt cycle times'>"
            f"<line x1='{L}' y1='{y(60):.1f}' x2='{W - 10}' y2='{y(60):.1f}' stroke='var(--t1)' stroke-dasharray='4 3'/>"
            f"<text x='{W - 12}' y='{y(60) - 4:.1f}' class='lbl' text-anchor='end'>60-minute box</text>"
            f"<line x1='{L}' y1='{y(med):.1f}' x2='{W - 10}' y2='{y(med):.1f}' stroke='var(--accent)'/>"
            f"<text x='{L + 4}' y='{y(med) - 4:.1f}' class='lbl'>median {med:.0f} min</text>"
            f"<line x1='{L}' y1='{H - B}' x2='{W - 10}' y2='{H - B}' class='ax'/>{''.join(bars)}</svg>"
            "<div class='legend'><span><i class='t green'></i>building</span><span><i class='t' style='background:var(--blue)'></i>tests and hooks</span>"
            "<span><i class='t grey'></i>waiting for the founder</span><span><i class='t' style='background:var(--t1)'></i>rework after a refusal</span></div>")


def _svg_burnup(points: list[dict], miles: list[dict]) -> str:
    if not points:
        return "<p class='note'>No recorded runs yet.</p>"
    W, H, L, B = 640, 200, 36, 26
    total = max(max(m["total"] for m in miles), 1)
    first = dt.date.fromisoformat(points[0]["day"])
    span = max((dt.date.fromisoformat(points[-1]["day"]) - first).days, 1)

    def x(day: str) -> float:
        return L + (dt.date.fromisoformat(day) - first).days / span * (W - L - 10)

    def y(n: float) -> float:
        return H - B - n / total * (H - B - 10)

    out = [f"<line x1='{L}' y1='{H - B}' x2='{W - 10}' y2='{H - B}' class='ax'/>"]
    for m, colour in zip(miles, ("var(--t1)", "var(--wip)", "var(--accent)")):
        path = " ".join(f"{'M' if i == 0 else 'L'}{x(p['day']):.1f},{y(p[m['m']]):.1f}" for i, p in enumerate(points))
        out.append(f"<path d='{path}' fill='none' stroke='{colour}' stroke-width='2'/>")
        out += [f"<circle cx='{x(p['day']):.1f}' cy='{y(p[m['m']]):.1f}' r='3' fill='{colour}' "
                f"data-tip='{m['m']} on {p['day']}: {p[m['m']]} of {m['total']} pass'/>" for p in points]
        out.append(f"<line x1='{L}' y1='{y(m['total']):.1f}' x2='{W - 10}' y2='{y(m['total']):.1f}' stroke='{colour}' stroke-dasharray='2 3'/>")
    out.append(f"<text x='{L}' y='{H - 8}' class='lbl'>{E(points[0]['day'])}</text>"
               f"<text x='{W - 10}' y='{H - 8}' class='lbl' text-anchor='end'>{E(points[-1]['day'])}</text>")
    legend = "".join(f"<span><i class='t' style='background:{c}'></i>{E(m['label'])} ({m['total']})</span>"
                     for m, c in zip(miles, ("var(--t1)", "var(--wip)", "var(--accent)")))
    return f"<svg viewBox='0 0 {W} {H}' role='img' aria-label='Burn-up per milestone'>{''.join(out)}</svg><div class='legend'>{legend}</div>"


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


#: The Belt journey strip's heading and the value stream's explanation, as the founder worded
#: them (control board items 0c and 0d, 2026-09-29).
JOURNEY_HEADING = ("Latest live test: a scripted Belt goes through Define on the real system · green = got through · "
                   "amber = stuck · grey = reached, not saved · white = not reached")
VALUE_STREAM_EXPLAIN = ("Each square = one feature (something that must work). Columns = the step of the Belt's journey. "
                        "Rows = the part of the software. Number = order of work (#1 = next).")


def tile_label(f: dict) -> str:
    """What an M1 square shows: its place in the order of work; an open M1 feature out of the
    order (it passes a test that is not end to end) shows "e2e", so every open M1 square is
    marked and the grid counts what the milestone box counts (item 0a)."""
    if f["status"] == "awaiting":
        return "◷"
    if f["tier"] != 1:
        return ""
    if f["rank"]:
        return str(f["rank"])
    return "e2e" if f["status"] != "green" else ""


def render(d: dict) -> str:
    m, fs = d["model"], d["features"]
    by_id = {f["id"]: f for f in fs}
    tabs = "".join(f"<span class='tab {'on' if p == 'define' else ('' if p in d['phases'] else 'off')}'>{p.capitalize()}</span>"
                   for p in PHASES)
    c = d["complete"]
    bars = "".join(
        f"<div class='bar' data-milestone='{x['m']}' role='button' tabindex='0' data-tip='{E(x['m'])}: {E(triple(x))}, "
        f"of {x['total']} — click to see them'><span>{E(x['label'])}</span><div class='track'>"
        f"<i style='width:{_pct(x['green'], x['total']):.1f}%;background:var(--done)'></i>"
        f"<i class='await' style='width:{_pct(x['awaiting'], x['total']):.1f}%'></i>"
        f"<i style='width:{_pct(x['amber'], x['total']):.1f}%;background:var(--wip)'></i></div>"
        f"<span class='num'>{x['green']}/{x['total']}</span></div>"
        f"<div class='note split' data-key='split-{x['m']}'>{E(x['m'])}: {E(triple(x))}</div>" for i, x in enumerate(d["milestones"]))
    j = d["journey"]
    els = "".join(f"<i class='el {s}' data-el='{i}' data-tip='{i + 1} · {E(e['name'])} — {E(e['state'])}'></i>"
                  for i, (s, e) in enumerate(zip(j["elements"], j["element_detail"])))
    stages = "".join(f"<div class='stage {j['stages'][k]}' data-stage='{k}' data-tip='{E(label)}: {j['stages'][k]}'>{E(label)}"
                     + (f"<div class='els'>{els}</div>" if k == "coached" else "") + "</div>" for k, label in STAGES)
    stale = " · <b>the record is older than the product source</b>" if j.get("stale") else ""
    head = "".join(f"<th>{E(label)}</th>" for _, label in STAGES)

    def in_order(sk: str, lk: str) -> list[dict]:
        """A cell's squares in the order of work; the unranked (passing, Won't-now) after them."""
        return sorted((f for f in fs if f["stage"] == sk and f["layer"] == lk),
                      key=lambda f: (f["rank"] is None, f["rank"] or 0, f["id"]))

    body_rows = []
    for lk, ll in LAYERS:
        cells = []
        for sk, _ in STAGES:
            tiles = "".join(
                f"<button class='t {f['status']}{' m1' if f['tier'] == 1 else ''}{' held' if f['held'] else ''}' data-f='{f['id']}' "
                f"data-tip='{E(f['id'])}{' · #' + str(f['rank']) if f['rank'] else ''}{' — held: ' + E(f['held']) if f['held'] else ''} — "
                f"{E(f['description'][:140])} · {E(f['reason'])}' data-m='{f['m'] or ''}'>{tile_label(f)}</button>"
                for f in in_order(sk, lk))
            cells.append(f"<td><div class='tiles'>{tiles}</div></td>")
        body_rows.append(f"<tr><td class='l'>{E(ll)}</td>{''.join(cells)}</tr>")
    stage_m1 = {sk: milestone_counts([f for f in fs if f["stage"] == sk])["M1"] for sk, _ in STAGES}
    foot = "".join(f"<td>{_pct(sum(f['status'] == 'green' for f in fs if f['stage'] == sk), sum(1 for f in fs if f['stage'] == sk)):.0f}%"
                   f"<br><span data-tip='M1 features of this stage that are done (green), of all of them'>M1 "
                   f"{stage_m1[sk]['green']} of {stage_m1[sk]['total']}</span>"
                   + (f"<br><span data-tip='M1 features of this stage proven on earlier code, awaiting a fresh run'>"
                      f"<span class='clock'>◷</span>{stage_m1[sk]['awaiting']} awaiting</span>" if stage_m1[sk]["awaiting"] else "")
                   + "</td>"
                   for sk, _ in STAGES)
    left = "".join(
        f"<div class='left'><h3 data-milestone='{x['m']}' role='button' tabindex='0'>{E(x['m'])} — {len(x['open'])} open of {x['total']}</h3>"
        f"<p class='note'>{E(triple(x))}</p>"
        + ("<ol>" + "".join(f"<li><a href='#' data-f='{i}'>{'#' + str(by_id[i]['rank']) if by_id[i]['rank'] else '—'} {E(i)}</a> "
                            f"{E(by_id[i]['description'][:70])}<br><span class='note'>blocked by: {E(by_id[i]['blocker'])}</span></li>"
                            for i in x["open"]) + "</ol>" if x["open"] else "<p class='note'>nothing left</p>")
        + "</div>" for x in d["milestones"])
    lanes = "".join(
        f"<div class='row' data-f='{x['now']}'><span class='lane'>{E(x['lane'][:5])}</span><span>"
        + (f"<b>{E(x['now'])}</b> {E(by_id[x['now']]['description'][:90])}" if x["now"] else "every feature passes")
        + (f" — next: <a href='#' data-f='{x['next']}'>{E(x['next'])}</a>" if x["next"] else "")
        + f"<br><span class='note'>next package: {', '.join(x['package']['features']) or '—'} "
          f"({x['package']['points']} of {rank.PACKAGE_POINTS} points)</span></span></div>" for x in d["lanes"])
    waiting = "".join(f"<div class='row' data-list='waiting:{i}'><span class='lane'>{E(w['tag'])}</span><span>{E(w['text'])}</span></div>"
                      for i, w in enumerate(d["waiting"]) if w["text"])
    health = "".join(f"<button class='h' data-list='health:{i}' data-tip='{E(h['label'])} — click for the list'>"
                     f"<b>{E(str(h['n']))}</b><span>{E(h['label'])}</span></button>" for i, h in enumerate(d["health"]))
    log = "".join(f"<tr><td><code>{E(x['sha'])}</code></td><td>{E(x['day'])}</td><td>{E(x['subject'])}</td>"
                  f"<td class='note'>{E(x['timing']) or '—'}</td></tr>" for x in d["commits"])
    progress = json.dumps({k: m[k] for k in ("headline", "passing", "total", "statuses", "next")},
                          ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    journey = {"elements": j["element_detail"], "stages": j["stage_detail"], "file": j["file"]}
    board = json.dumps({**{k: d[k] for k in ("features", "milestones", "waiting", "health")}, "journey": journey,
                        "stages": dict(STAGES), "layers": dict(LAYERS), "ranked": sum(1 for f in fs if f["rank"])},
                       ensure_ascii=False).replace("</", "<\\/")
    stale_run = "" if m["fresh"] else " <b>The recorded test run is older than the source.</b>"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Refactoring board</title>
<style>{CSS}</style></head><body><div class="wrap">
<div><h1>Agent Improve — refactoring board</h1>
<p class="meta" data-key="headline">{E(m['headline'])}.{stale_run} Generated on every commit by <code>tools/control_board/build_control_board.py</code>; nothing here is typed by hand. Hover for detail, click for everything behind it.</p></div>
<div class="tabs">{tabs}</div>
<div class="top">
<div class="card"><h2>Define complete</h2><div class="pct">{_pct(c['passing'], c['total']):.0f}<small>%</small></div>
<div class="note">{c['passing']} of {c['total']} ranked features pass</div>{bars}</div>
<div class="card"><div><h2>Belt journey</h2>
<p class="jhead" data-key="journey-subtitle">{E(JOURNEY_HEADING)}</p><p class="note" data-key="journey-date">Run of {E(j.get('date') or 'no run recorded')}</p></div><div class="journey">{stages}</div>
<div class="note">{E(j['note'])}{stale} · <code>{E(j['file'] or '—')}</code></div><div>{_spark(j['spark'], len(j['names']))}</div></div>
</div>
<div class="card"><div style="display:flex;justify-content:space-between;flex-wrap:wrap;gap:8px;align-items:baseline"><h2>Value stream</h2>
<div class="legend" data-key="legend">colour = status · outline = M1 · number = order of work · ◷ = proven on earlier code, awaiting a fresh run</div></div>
<p class="explain" data-key="explain">{E(VALUE_STREAM_EXPLAIN)}</p>
<div class="grid"><table class="vs"><thead><tr><th></th>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody><tfoot><tr><td></td>{foot}</tr></tfoot></table></div></div>
<div class="card"><h2>What's left</h2><div class="lefts">{left}</div></div>
<div class="two"><div class="card"><h2>Now per lane</h2>{lanes}</div>
<div class="card"><h2>Waiting for you</h2>{waiting}</div></div>
<div class="card"><h2>Prompt flow — the last 15 prompts</h2>{_svg_prompts(d['prompts'])}</div>
<div class="health">{health}</div>
<div class="card"><h2>Burn-up per milestone</h2>{_svg_burnup(d['burnup'], d['milestones'])}</div>
<details class="card"><summary><h2 style="display:inline">Last commits</h2></summary><table class="log">{log}</table></details>
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
