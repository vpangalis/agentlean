"""THE ONE FUNCTION behind every progress number — step 6.63.

Founder rulings 2026-09-25: *"The only progress view is the repo's generated
control-board.html."* · *"Every number, label, diagram element and status
colour on the board is derived from the tree, never typed by hand."* ·
*"Headline: 'N of 35 capabilities proven · working on: <step name>'."*

`progress()` reads the tree and returns one dict. The control board, its
waterfall, its headline, CONTINUITY.md's status block and the session-start
hook all read THAT dict — nothing re-derives a number of its own, which is the
escape the 2026-09-25 8D found (four views, four numbers).

WHAT EACH FACT IS READ FROM — the owner, never a copy
    Appendix D           the registered steps (a step not here is unregistered)
    Appendix F           `Order` (priority) and each step's state + symbol anchor
    "The Define path — estimate and epic"   estimate, epic, work package
    the step's own card  `Precondition` (dependency — the card wins, founder 2026-09-25)
    Founder milestones   the table under the estimates
    Wiring proofs        which test proves a step WIRED, and the symbols it claims
    Appendix H           the capability register (row, check, state)
    test-results.json    whether a named test passed, and on which source
    git log              when a step's work started and when it landed

THREE STATES, EACH WITH ITS OWN PROOF (the brief, item 3)
    built   the Appendix F row is ✅ — its symbol anchor, which the referee
            (`verify_built.py`) resolves at every commit
    wired   its Wiring-proofs test passed on the current source
    proven  it owns a register row that is 🟢 and whose check passed on the
            current source
    A step is DONE only when wired, or proven if it owns a row.

EVERY STATUS CARRIES ITS REFERENCE, and its colour is computed from it:
    green  the reference passes on the current source
    amber  it exists but is older than the code it describes (the source
           changed since the recorded run), or it is RELAYED only
    red    it fails, or there is none
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

import sys as _sys
if str(Path(__file__).resolve().parent) not in _sys.path:
    _sys.path.insert(0, str(Path(__file__).resolve().parent))

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parents[1]                      # agent-improve/
ROOT = PROJECT.parent                          # the repo
PROCEDURE = PROJECT / "docs" / "REFACTORING_PROCEDURE.md"
RESULTS = PROJECT / "docs" / "test-results.json"

#: The source whose hash a recorded test run is bound to. A run recorded on a
#: different hash is OLDER than the code it describes — amber, not green.
SOURCE_GLOBS = ("backend/**/*.py", "ui/*.html", "skills/**/*.md")

#: Working days in a week the plan counts. The estimates are in working days.
WEEKDAYS = {0, 1, 2, 3, 4}

#: The rescale needs history: with fewer landed estimated steps than this the
#: forecast uses the plan as written (factor 1.0) and says so.
MIN_RESCALE_SAMPLE = 3

Reader = Callable[[Path], str]


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ══ Parsing — every reader returns plain data, and raises when it cannot read ══


def _section(text: str, heading: str, level: str = "## ") -> str:
    start = text.find(heading)
    if start < 0:
        raise ValueError(f"'{heading}' not found in the procedure")
    end = text.find("\n" + level, start + len(heading))
    return text[start:end if end > 0 else len(text)]


_D_ROW = re.compile(r"^\|\s*(?P<seq>\d+)\s*\|\s*\*\*Commit (?P<step>\d+\.\d+)\*\*\s*\|"
                    r"(?P<title>[^|]*)\|(?P<status>[^|]*)\|(?P<layer>[^|]*)\|(?P<scope>[^|]*)\|"
                    r"(?P<why>[^|]*)\|\s*$", re.M)


def appendix_d(text: str) -> dict[str, dict]:
    body = _section(text, "## Appendix D")
    out = {m["step"]: {"seq": int(m["seq"]), "title": m["title"].strip(),
                       "status": m["status"].strip(), "layer": m["layer"].strip(),
                       "why": m["why"].strip()}
           for m in _D_ROW.finditer(body)}
    if not out:
        raise ValueError("Appendix D has no step rows this reader recognises")
    return out


#: One Appendix F row. **The Zone cell sits between Order and the step** —
#: the cell the two old `read_order` regexes did not allow for (the 8D's
#: fifth cause), so both returned an empty plan against the real table.
_F_ROW = re.compile(r"^\|\s*L(?P<layer>\d+)\s*\|(?P<order>[^|]*)\|(?P<zone>[^|]*)\|\s*"
                    r"\*\*(?P<step>\d+\.\d+)\*\*\s*\|(?P<item>[^|]*)\|(?P<state>[^|]*)\|"
                    r"(?P<anchor>[^|]*)\|(?P<secs>[^|]*)\|\s*$", re.M)
_STATE = {"✅": "built", "⚠": "defect", "☐": "unbuilt", "⛔": "blocked"}


def appendix_f(text: str) -> dict[str, dict]:
    """step -> its MAIN row (Zone "—", else its only row) with the Order."""
    body = _section(text, "## Appendix F — The build matrix")
    rows: dict[str, list[dict]] = {}
    for m in _F_ROW.finditer(body):
        order = m["order"].strip()
        rows.setdefault(m["step"], []).append({
            "layer": int(m["layer"]), "order": int(order) if order.isdigit() else None,
            "zone": m["zone"].strip(), "item": m["item"].strip(),
            "state": _STATE.get(m["state"].strip(), m["state"].strip()),
            "mark": m["state"].strip(),
            "anchor": m["anchor"].strip().strip("`"), "sections": m["secs"].strip()})
    main = {}
    for step, rs in rows.items():
        dash = [r for r in rs if r["zone"] in ("—", "")]
        main[step] = (dash or rs)[0] if len(dash) <= 1 else dash[0]
        main[step]["orders"] = [r["order"] for r in rs if r["order"] is not None]
    return main


#: A container heading in Appendix F: `#### L3 · Phase subgraphs`.
_LAYER_HEAD = re.compile(r"^#### L(?P<n>\d+) · (?P<name>.+?)\s*$", re.M)


def layers(text: str) -> dict[int, str]:
    """Appendix F's containers — layer number -> the name its heading gives.

    Step 6.64. **The container a step belongs to is its Appendix F `Layer`**
    ("which part of the system the step changes", the column table), named by
    the table's own headings — never by a list typed here. Appendix F's `Zone`
    cell reads "—" on every step's own row, so it cannot group the steps."""
    body = _section(text, "## Appendix F — The build matrix")
    out = {int(m["n"]): m["name"].strip() for m in _LAYER_HEAD.finditer(body)}
    if not out:
        raise ValueError("Appendix F has no '#### L<n> · <name>' container headings")
    return out


def order_rows(text: str) -> list[dict]:
    """Every Appendix F row that carries an `Order` number, sorted by it:
    {n, step, item, state (the cell's mark)}. THE ONE READER of the column —
    `build_board.read_order` and `continuity_status.read_order` call this
    rather than keeping the two regex copies that lost the Zone cell. Raises
    on a duplicate number: two items numbered 3 is a person having edited one
    and not the other."""
    body = _section(text, "## Appendix F — The build matrix")
    out: list[dict] = []
    seen: dict[int, str] = {}
    for m in _F_ROW.finditer(body):
        o = m["order"].strip()
        if not o.isdigit():
            continue
        n = int(o)
        if n in seen:
            raise ValueError(f"Order {n} is on both {seen[n]} and {m['step']}")
        seen[n] = m["step"]
        out.append({"n": n, "step": m["step"], "item": m["item"].strip(),
                    "state": m["state"].strip()})
    return sorted(out, key=lambda r: r["n"])


def read_order(text: str) -> list[str]:
    """Appendix F's `Order` column as step numbers — THE PLAN."""
    return [r["step"] for r in order_rows(text)]


_CARD = re.compile(r"^## Step (?P<step>\d+\.\d+) — (?P<title>.+)$", re.M)
_CELL = lambda key: re.compile(r"^\|\s*\*\*" + key + r"\*\*\s*\|(?P<v>.*)\|\s*$", re.M)  # noqa: E731
_PRECON, _STATUS, _TOUCHES = _CELL("Precondition"), _CELL("Status"), _CELL("Touches")


def cards(text: str) -> dict[str, dict]:
    heads = list(_CARD.finditer(text))
    out = {}
    for i, m in enumerate(heads):
        end = heads[i + 1].start() if i + 1 < len(heads) else len(text)
        body = text[m.end():end]
        p, s, t = _PRECON.search(body), _STATUS.search(body), _TOUCHES.search(body)
        out[m["step"]] = {"title": m["title"].strip(),
                          "touches": t["v"].strip() if t else "",
                          "precondition": p["v"].strip() if p else "",
                          "status": s["v"].strip() if s else ""}
    return out


#: A step number in a precondition — not a section (§39.1.9), not a version
#: (v1.69), not part of a longer number.
_STEP_REF = re.compile(r"(?<![\w§.])(?<!v)(\d{1,2}\.\d{1,2})(?![\d.]*\d)")
_ORDER_RANGE = re.compile(r"`?Order`?\s+(\d+)\s*[–-]\s*(\d+)")


def depends_on(step: str, card: dict, order: list[str]) -> list[str]:
    """The card's precondition as step numbers. *"Order 1–17"* expands to the
    steps at those positions (7.9's card)."""
    text = card.get("precondition", "")
    # "none — …" names no dependency, whatever the explanation after the dash
    # mentions: 6.63's card reads "none — READY (6.61's Part 0 is committed)",
    # and reading 6.61 out of it made rule 11 refuse 6.63's own landing.
    if re.match(r"^\W*none\b", text, re.I):
        return []
    deps = [s for s in _STEP_REF.findall(text) if s != step]
    for a, b in _ORDER_RANGE.findall(text):
        deps += [s for s in order[int(a) - 1:int(b)] if s != step]
    return list(dict.fromkeys(deps))


_EST = re.compile(r"^\|\s*\*\*(?P<step>\d+\.\d+)\*\*\s*\|(?P<est>[^|]*)\|(?P<epic>[^|]*)\|"
                  r"(?:(?P<wp>[^|]*)\|)?\s*$", re.M)


def estimates(text: str) -> dict[str, dict]:
    body = _section(text, "### The Define path — estimate and epic", "### ")
    out = {}
    for m in _EST.finditer(body):
        est = m["est"].strip()
        out[m["step"]] = {"estimate": float(est) if re.fullmatch(r"\d+(\.\d+)?", est) else None,
                          "epic": re.sub(r"\*\(proposed\)\*", "", m["epic"]).strip(),
                          "epic_proposed": "(proposed)" in m["epic"],
                          "wp": (m["wp"] or "").strip()}
    return out


_MS = re.compile(r"^\|\s*\*\*(?P<id>[^*]+)\*\*\s*\|(?P<what>[^|]*)\|(?P<blocks>[^|]*)\|\s*$", re.M)


def milestones(text: str) -> dict[str, dict]:
    body = _section(text, "**Founder inputs — milestones, not slips.**", "### ")
    body = body[:body.find("\n\n**Done, off")] if "\n\n**Done, off" in body else body
    return {m["id"].strip(): {"what": m["what"].strip(),
                              "blocks": _STEP_REF.findall(m["blocks"]),
                              "off_path": "off the path" in m["blocks"]}
            for m in _MS.finditer(body) if m["id"].strip() not in ("Milestone",)}


_WIRE = re.compile(r"^\|\s*\*\*(?P<step>\d+\.\d+)\*\*\s*\|\s*`(?P<test>[^`]+)`(?P<note>[^|]*)\|"
                   r"(?P<symbols>[^|]*)\|\s*$", re.M)


def wiring(text: str) -> dict[str, dict]:
    """step -> {test, symbols, tooling}. A row whose Wired-by cell says
    *(tooling)* claims THE TOOLING ROUTE (founder, 2026-09-25): a step that
    touches nothing under backend/ or ui/ may name its own test as its proof."""
    try:
        body = _section(text, "### Wiring proofs", "### ")
    except ValueError:
        return {}
    return {m["step"]: {"test": m["test"].strip(),
                        "symbols": re.findall(r"`([^`]+)`", m["symbols"]),
                        "tooling": "tooling" in m["note"]}
            for m in _WIRE.finditer(body)}


#: What counts as PRODUCT for the tooling route: anything under backend/ or
#: ui/. Touches cells often name backend paths without the prefix
#: (`core/graph.py`, `gateway/routes.py`), so a path is also product when its
#: first segment is a directory or file directly under backend/.
_BACKEND_TOP = {p.name for p in (PROJECT / "backend").iterdir()} if (PROJECT / "backend").is_dir() else set()


def touches_product(touches: str) -> list[str]:
    """The paths in a card's Touches cell that are product code (backend/ or ui/).

    **`backend/tests/` is not product** (founder, 2026-09-25, answering 6.63's
    own case: its Touches named the test recorder and its tests, and the
    literal rule refused the step the route was ruled for). Every other path
    under backend/ or ui/ is."""
    tokens = re.findall(r"`([^`]+)`", touches) + re.findall(r"\]\(([^)]+)\)", touches)
    hits = []
    for t in tokens:
        p = re.sub(r"^(\.\./)+|^agent-improve/", "", t.strip()).split(":")[0].split("#")[0]
        whole_backend = p.rstrip("/") == "backend"
        p = p[len("backend/"):] if p.startswith("backend/") else p
        first = p.split("/")[0]
        if first == "tests" and not whole_backend:
            continue
        if whole_backend or first in ("backend", "ui") or first in _BACKEND_TOP:
            hits.append(t)
    return list(dict.fromkeys(hits))


_H_ROW = re.compile(r"^\|\s*\*\*(?P<row>\d+)\*\*\s*\|(?P<cap>[^|]*)\|(?P<check>[^|]*)\|\s*"
                    r"(?P<state>\U0001F7E2|\U0001F534)\s*\|(?P<given>[^|]*)\|\s*$", re.M)


def register(text: str) -> dict[int, dict]:
    body = _section(text, "## Appendix H")
    out = {int(m["row"]): {"capability": m["cap"].strip(),
                           "check": (re.search(r"`([^`]+::[^`]+)`", m["check"]) or [None, None])[1],
                           "green": m["state"] == "\U0001F7E2",
                           "owners": _STEP_REF.findall(m["given"])}
           for m in _H_ROW.finditer(body)}
    if not out:
        raise ValueError("Appendix H has no rows this reader recognises")
    return out


# ══ The recorded test run, and whether it is older than the code ══════════════


def source_hash(root: Path = PROJECT) -> str:
    h = hashlib.sha256()
    for pattern in SOURCE_GLOBS:
        for p in sorted(root.glob(pattern)):
            if "__pycache__" in p.parts or ".venv" in p.parts:
                continue
            h.update(p.relative_to(root).as_posix().encode())
            h.update(p.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]


def test_results(path: Path = RESULTS) -> dict:
    if not path.is_file():
        return {"source_hash": None, "outcomes": {}}
    return json.loads(path.read_text(encoding="utf-8"))


def verdict(test_id: str | None, results: dict, current_hash: str) -> dict:
    """A named test's colour: green / amber / red, with the reference."""
    if not test_id:
        return {"colour": "red", "ref": "none", "why": "no reference"}
    key = _nodeid(test_id)
    fresh = results.get("source_hash") == current_hash
    outcome = results.get("outcomes", {}).get(key)
    run_hash = results.get("source_hash")
    if outcome is None:
        older = results.get("older") or {}
        if key in (older.get("outcomes") or {}):
            outcome, run_hash, fresh = older["outcomes"][key], older.get("source_hash"), False
    if outcome is None:
        return {"colour": "red", "ref": key, "why": "never recorded as run"}
    if outcome != "passed":
        return {"colour": "red", "ref": key, "why": f"recorded {outcome} on source {run_hash}"}
    if not fresh:
        return {"colour": "amber", "ref": key,
                "why": f"passed on source {run_hash}; the code is now {current_hash}"}
    return {"colour": "green", "ref": key, "why": f"passed on source {current_hash}"}


def _nodeid(test_id: str) -> str:
    """`backend.tests.test_x::test_y` -> `backend/tests/test_x.py::test_y`."""
    mod, _, fn = test_id.partition("::")
    return mod.replace(".", "/") + ".py::" + fn if fn else test_id


# ══ git — when work started and when it landed ════════════════════════════════

_LAND = re.compile(r"^refactor\(arch-v2\): commit (\d+\.\d+)\b")
_WORK = re.compile(r"^Step:\s*(\d+\.\d+)\s*$", re.M)


def git_history(root: Path = ROOT) -> list[dict]:
    out = subprocess.run(["git", "log", "--reverse", "--format=%H%x1f%ad%x1f%s%x1f%b%x1e",
                          "--date=short"], cwd=root, capture_output=True, encoding="utf-8",
                         errors="replace", check=True).stdout
    commits = []
    for rec in out.split("\x1e"):
        if not rec.strip():
            continue
        sha, date, subject, body = (rec.strip("\n").split("\x1f") + ["", "", "", ""])[:4]
        commits.append({"sha": sha[:7], "date": date, "subject": subject, "body": body})
    return commits


def actuals(commits: list[dict]) -> dict[str, dict]:
    """step -> first and landing commit. Work starts at the first commit whose
    subject lands it or whose body carries `Step: X.Y`; it lands at
    `refactor(arch-v2): commit X.Y`."""
    out: dict[str, dict] = {}
    for c in commits:
        steps = set(_WORK.findall(c["body"]))
        m = _LAND.match(c["subject"])
        if m:
            steps.add(m[1])
        for s in steps:
            a = out.setdefault(s, {"first": c, "landed": None})
            if m and m[1] == s:
                a["landed"] = c
    return out


# ══ Working days ══════════════════════════════════════════════════════════════


def add_workdays(start: dt.date, days: float) -> dt.date:
    """The date `days` working days after `start` (start counts as day one)."""
    d, left = start, max(1, round(days))
    while d.weekday() not in WEEKDAYS:
        d += dt.timedelta(days=1)
    while left > 1:
        d += dt.timedelta(days=1)
        if d.weekday() in WEEKDAYS:
            left -= 1
    return d


def workdays_between(a: dt.date, b: dt.date) -> int:
    n, d = 0, a
    while d <= b:
        n += d.weekday() in WEEKDAYS
        d += dt.timedelta(days=1)
    return max(1, n)


def next_workday(d: dt.date) -> dt.date:
    d += dt.timedelta(days=1)
    while d.weekday() not in WEEKDAYS:
        d += dt.timedelta(days=1)
    return d


# ══ THE ONE FUNCTION ═════════════════════════════════════════════════════════


def progress(proc_text: str | None = None, *, commits: list[dict] | None = None,
             results: dict | None = None, current_hash: str | None = None,
             today: dt.date | None = None) -> dict[str, Any]:
    text = proc_text if proc_text is not None else _read(PROCEDURE)
    commits = commits if commits is not None else git_history()
    results = results if results is not None else test_results()
    current_hash = current_hash or source_hash()
    today = today or dt.date.today()

    import reach    # noqa: E402 — siblings; this directory is on sys.path
    import stories  # noqa: E402
    d, f, crd = appendix_d(text), appendix_f(text), cards(text)
    order, est, ms = read_order(text), estimates(text), milestones(text)
    lay = layers(text)
    wired_by, reg = wiring(text), register(text)
    act = actuals(commits)
    epic_of = stories.epic_of()
    claimed = sorted({sym for w in wired_by.values() for sym in w["symbols"]})
    not_reached = {x.split(" ")[0]: x for x in reach.unreachable(claimed)} if claimed else {}

    # ── capabilities ──
    caps = []
    for n, row in sorted(reg.items()):
        v = verdict(row["check"], results, current_hash) if row["check"] else \
            {"colour": "red", "ref": "none", "why": "no check written"}
        proven = row["green"] and v["colour"] == "green"
        colour = "green" if proven else ("amber" if row["green"] and v["colour"] == "amber" else "red")
        caps.append({"row": n, "capability": row["capability"], "owners": row["owners"],
                     "register_green": row["green"], "proven": proven, "colour": colour,
                     "ref": f"Appendix H row {n} · {v['ref']}", "why": v["why"]})
    proven_n = sum(c["proven"] for c in caps)

    # ── steps: built / wired / proven ──
    steps: dict[str, dict] = {}
    for s in sorted(set(d) | set(f), key=lambda x: tuple(int(p) for p in x.split("."))):
        row, card = f.get(s, {}), crd.get(s, {})
        built = row.get("state") == "built"
        w = wired_by.get(s)
        wv = verdict(w["test"], results, current_hash) if w else None
        unreached = [not_reached[x] for x in (w or {}).get("symbols", []) if x in not_reached]
        if wv and unreached:
            wv = {"colour": "red", "ref": wv["ref"], "why": "; ".join(unreached)}
        # THE TOOLING ROUTE (founder, 2026-09-25): only for a step whose Touches
        # name nothing under backend/ or ui/. A product step claiming it is
        # refused — red here, and a plan problem in `validate`.
        tooling_claim = bool(w and w.get("tooling"))
        product = touches_product(card.get("touches", "")) if tooling_claim else []
        if wv and tooling_claim and product:
            wv = {"colour": "red", "ref": wv["ref"],
                  "why": "claims the tooling route but touches product code: " + ", ".join(product)}
        elif wv and tooling_claim and wv["colour"] == "green":
            wv = dict(wv, why=wv["why"] + " — a tooling proof, not a product capability")
        wired = bool(wv and wv["colour"] == "green") and not tooling_claim
        tooling = bool(wv and wv["colour"] == "green") and tooling_claim
        owned = [c for c in caps if s in c["owners"]]
        proven = bool(owned) and all(c["proven"] for c in owned)
        done = wired or proven or tooling
        a = act.get(s, {})
        state = ("proven" if proven else "wired" if wired else "tooling" if tooling else
                 "built" if built else
                 "blocked" if d.get(s, {}).get("status") in ("BLOCKED", "GATED", "EXTERNAL")
                 else "unbuilt")
        steps[s] = {
            "step": s, "title": card.get("title") or d.get(s, {}).get("title", ""),
            "registered": s in d, "order": row.get("order"),
            "built": built, "wired": wired, "proven": proven, "tooling": tooling,
            "done": done, "state": state,
            "anchor": row.get("anchor", ""), "f_mark": row.get("mark", ""), "wired_ref": (wv or {}).get("ref"),
            "wired_colour": (wv or {}).get("colour"), "wired_why": (wv or {}).get("why"),
            "wired_symbols": (w or {}).get("symbols", []),
            "rows": [c["row"] for c in owned],
            "depends_on": depends_on(s, card, order) if card else [],
            "precondition": card.get("precondition", ""),
            "estimate": est.get(s, {}).get("estimate"),
            # The epic is stories.py's; the estimate table's is used only where
            # stories.py does not list the step, and is then marked proposed.
            "epic": epic_of[s][0] if s in epic_of else est.get(s, {}).get("epic", ""),
            "story": epic_of[s][1] if s in epic_of else "",
            "epic_proposed": s not in epic_of and bool(est.get(s, {}).get("epic")),
            "wp": est.get(s, {}).get("wp", ""),
            # 6.64 — the container: the Layer of its own Appendix F row, when
            # that layer has a heading. `None` is refused by `validate`.
            "container": (f"L{row['layer']}" if row and row.get("layer") in lay else None),
            "first_commit":(a.get("first") or {}).get("sha"),
            "first_date": (a.get("first") or {}).get("date"),
            "landed_commit": (a.get("landed") or {}).get("sha"),
            "landed_date": (a.get("landed") or {}).get("date"),
            "d_status": d.get(s, {}).get("status", ""),
        }

    # ── 6.64 — containers: every registered step under its Layer ──
    containers = []
    for n, name in sorted(lay.items()):
        cid = f"L{n}"
        members = [s for s, st in steps.items() if st["container"] == cid and st["registered"]]
        containers.append({"id": cid, "name": name, "steps": members,
                           "open": [s for s in members if not steps[s]["done"]]})
    for c in caps:
        c["containers"] = sorted({steps[o]["container"] for o in c["owners"]
                                  if o in steps and steps[o]["container"]},
                                 key=lambda x: int(x[1:]))

    working_on = next((steps[s] for s in order if not steps[s]["done"]), None)
    plan = schedule(order, steps, ms, today)
    head = (f"{proven_n} of {len(caps)} capabilities proven · working on: "
            + (f"{working_on['step']} — {working_on['title']}" if working_on else "nothing — the Order is empty"))
    return {"headline": head, "capabilities": caps, "proven": proven_n, "total_caps": len(caps),
            "working_on": working_on, "order": order, "steps": steps, "milestones": ms,
            "containers": containers,
            "plan": plan, "source_hash": current_hash,
            "results_hash": results.get("source_hash"),
            "results_commit": results.get("commit"),
            "results_recorded_at": results.get("recorded_at"),
            "today": today.isoformat(),
            "problems": validate(text, d, f, crd, order, est, lay)
            + [f"{s}'s epic is {st['epic']} in stories.py and {est[s]['epic']} in the estimate table"
               for s, st in steps.items() if s in est and s in epic_of and est[s]["epic"]
               and not est[s]["epic_proposed"] and est[s]["epic"] != st["epic"]]}


def schedule(order: list[str], steps: dict, ms: dict, today: dt.date) -> dict:
    """Planned bars from the estimates, one worker, in Order, each after its
    card's preconditions; actual bars from git; the remaining bars rescaled by
    actual/planned so far; the forecast finish of the last step (7.9's)."""
    # History is every step that LANDED with an estimate — including those that
    # have since left the Order (a landed step leaves it; 10.0 did).
    landed = [s for s, st in steps.items() if st["landed_date"] and st["first_date"] and st["estimate"]]
    history = [(workdays_between(dt.date.fromisoformat(steps[s]["first_date"]),
                                 dt.date.fromisoformat(steps[s]["landed_date"])),
                steps[s]["estimate"]) for s in landed]
    if len(history) >= MIN_RESCALE_SAMPLE:
        factor = sum(a for a, _ in history) / sum(p for _, p in history)
        basis = f"rescaled ×{factor:.2f} from {len(history)} landed step(s)"
    else:
        factor = 1.0
        basis = (f"the plan as estimated — {len(history)} landed step(s) with an estimate, "
                 f"{MIN_RESCALE_SAMPLE} needed before rescaling")
    blocked_by = {s: [m for m, v in ms.items() if s in v["blocks"]] for s in order}
    ends: dict[str, dt.date] = {}
    cursor = today
    bars = []
    for s in order:
        st = steps[s]
        if st["done"]:
            continue
        dep_ends = [ends[x] for x in st["depends_on"] if x in ends]
        dep_end = max(dep_ends) if dep_ends else None
        start = max(cursor, next_workday(dep_end) if dep_end else cursor)
        days = (st["estimate"] or 0) * factor
        end = add_workdays(start, days) if days else start
        ends[s] = end
        cursor = next_workday(end)
        bars.append({"step": s, "start": start.isoformat(), "end": end.isoformat(),
                     "planned_days": st["estimate"], "scaled_days": round(days, 1),
                     "waiting_on": blocked_by.get(s, []),
                     "actual_start": st["first_date"], "actual_end": st["landed_date"]})
    finish = ends.get(order[-1]) if order else None
    define_end = ends.get("7.9")
    return {"bars": bars, "factor": round(factor, 3), "basis": basis,
            "forecast_finish": finish.isoformat() if finish else None,
            "forecast_define": define_end.isoformat() if define_end else None,
            "conditional_on": sorted({m for b in bars for m in b["waiting_on"]})}


def validate(text: str, d: dict, f: dict, crd: dict, order: list[str], est: dict,
             lay: dict[int, str] | None = None) -> list[str]:
    """What the plan REFUSES (the brief, item 8): an unregistered step, a step
    in Order with no estimate, a card precondition naming a step that does not
    exist — and, since 6.64, a registered step with no container. Returned as
    sentences; a caller that finds any fails closed."""
    problems = []
    lay = lay if lay is not None else layers(text)
    for s in d:
        if s not in f:
            problems.append(f"{s} has no container — it has no Appendix F row, so no Layer")
        elif f[s].get("layer") not in lay:
            problems.append(f"{s} has no container — its Appendix F Layer L{f[s].get('layer')} "
                            "has no '#### L<n> · <name>' heading")
    for s in order:
        if s not in d:
            problems.append(f"{s} is in Appendix F's Order but not registered in Appendix D")
        if est.get(s, {}).get("estimate") is None:
            problems.append(f"{s} is in Order and has no Estimate")
    known = set(d)
    for s, card in crd.items():
        for dep in depends_on(s, card, order):
            if dep not in known:
                problems.append(f"{s}'s precondition names {dep}, which is not a registered step")
    for s, w in wiring(text).items():
        product = touches_product(crd.get(s, {}).get("touches", "")) if w["tooling"] else []
        if product:
            problems.append(f"{s} claims the tooling route but its Touches include product "
                            f"code ({', '.join(product)}) — a step touching backend/ or ui/ "
                            "can never use it (founder, 2026-09-25)")
    return problems


# ══ Every status on the board, with its reference ════════════════════════════

#: The colours a status may take. green / amber / red are a REFERENCE's verdict
#: (the brief, item 6); `built` and `waiting` are the two step states that are
#: neither done nor failed — built-only has its own colour (item 3), and a step
#: waiting on a founder input is shown waiting, not late (item 4).
COLOURS = ("green", "amber", "red", "built", "waiting")


def statuses(p: dict) -> dict[str, dict]:
    """key -> {colour, ref, why}. THE status set: the board renders exactly
    these and the integrity check recomputes exactly these."""
    out: dict[str, dict] = {}
    for c in p["capabilities"]:
        out[f"cap:{c['row']}"] = {"colour": c["colour"], "ref": c["ref"], "why": c["why"]}
    for s, st in p["steps"].items():
        anchor = st["anchor"] if st["anchor"] not in ("", "—") else ""
        if st["built"] and anchor:
            b = {"colour": "green", "ref": f"Appendix F ✅ · anchor {anchor}",
                 "why": "the referee (verify_built.py) resolves every ✅ anchor at each commit"}
        elif st["built"]:
            b = {"colour": "red", "ref": "none", "why": "✅ with no symbol anchor"}
        else:
            b = {"colour": "red",
                 "ref": f"Appendix F {st['f_mark']} · step {s}" if st["f_mark"] else "none",
                 "why": "its Appendix F row is not ✅" if st["f_mark"] else "no Appendix F row"}
        out[f"step:{s}:built"] = b
        if st["wired_ref"]:
            out[f"step:{s}:wired"] = {"colour": st["wired_colour"], "ref": st["wired_ref"],
                                      "why": st["wired_why"]}
        else:
            out[f"step:{s}:wired"] = {"colour": "red", "ref": "none",
                                      "why": "no row in Appendix F's Wiring proofs"}
        if st["rows"]:
            cols = [out[f"cap:{r}"]["colour"] for r in st["rows"]]
            colour = ("green" if all(c == "green" for c in cols)
                      else "red" if "red" in cols else "amber")
            out[f"step:{s}:proven"] = {"colour": colour,
                                       "ref": "Appendix H rows " + ", ".join(map(str, st["rows"])),
                                       "why": "every row it owns is proven" if colour == "green"
                                       else "a row it owns is not proven"}
        state = st["state"]
        if state == "proven":
            pill = {"colour": "green", "ref": out[f"step:{s}:proven"]["ref"], "why": "proven"}
        elif state == "wired":
            pill = {"colour": "green", "ref": st["wired_ref"], "why": "wired"}
        elif state == "tooling":
            pill = {"colour": "green", "ref": st["wired_ref"],
                    "why": "tooling — proven by its own test; not a product capability"}
        elif state == "built":
            pill = {"colour": "built", "ref": b["ref"], "why": "built, not wired: " + (
                st["wired_why"] or "no wiring proof")}
        elif state == "blocked":
            pill = {"colour": "waiting", "ref": f"Appendix D status {st['d_status']}",
                    "why": "waiting — not late"}
        else:
            pill = {"colour": "red", "ref": b["ref"], "why": "not built"}
        out[f"step:{s}:state"] = pill

    # 6.64 — a container's colour is its steps' states, counted: green when
    # every step in it is done, red while any is not built, `built` while any
    # is built and not wired, `waiting` when all that is left is waiting.
    for c in p.get("containers", []):
        states = [p["steps"][s]["state"] for s in c["steps"]]
        done = sum(p["steps"][s]["done"] for s in c["steps"])
        n = {k: states.count(k) for k in ("built", "blocked", "unbuilt")}
        colour = ("green" if done == len(states) else "red" if n["unbuilt"]
                  else "built" if n["built"] else "waiting")
        out[f"ctr:{c['id']}"] = {
            "colour": colour,
            "ref": (f"Appendix F {c['id']} · {len(states)} steps — {done} done, {n['built']} built, "
                    f"{n['blocked']} waiting, {n['unbuilt']} not built"),
            "why": {"green": "every step in it is done", "red": "a step in it is not built",
                    "built": "every step is built; one or more is not wired",
                    "waiting": "what is left waits on a founder input"}[colour]}

    # 6.64 — a story's colour is its acceptance rows' colours (Appendix H). A
    # story with no rows has no source and gets no colour at all.
    import stories  # noqa: E402 — a sibling; this directory is on sys.path
    caps = {c["row"]: c for c in p["capabilities"]}
    for ep in stories.EPICS:
        for sto in ep["stories"]:
            if not sto["rows"]:
                continue
            cols = [out[f"cap:{r}"]["colour"] for r in sto["rows"] if r in caps]
            colour = ("green" if cols and all(x == "green" for x in cols)
                      else "red" if "red" in cols or not cols else "amber")
            out[f"story:{sto['id']}"] = {
                "colour": colour, "ref": "Appendix H rows " + ", ".join(map(str, sto["rows"])),
                "why": {"green": "every row it is accepted by is proven",
                        "amber": "its rows passed on older code",
                        "red": "a row it is accepted by is not proven"}[colour]}
    return out


def procedure_text(staged: bool = False) -> str:
    """The procedure as the commit will carry it (`staged`) or as it is on disk."""
    if staged:
        r = subprocess.run(["git", "show", ":agent-improve/docs/REFACTORING_PROCEDURE.md"],
                           cwd=ROOT, capture_output=True, encoding="utf-8", errors="replace")
        if r.returncode == 0:
            return r.stdout
    return _read(PROCEDURE)


def built_from() -> tuple[str, str]:
    """(short sha, subject) of HEAD — in the pre-commit hook, the PARENT of the
    commit being made."""
    out = subprocess.run(["git", "log", "-1", "--pretty=%h%x09%s"], cwd=ROOT, capture_output=True,
                         encoding="utf-8", errors="replace", check=True).stdout.strip()
    sha, _, subject = out.partition("\t")
    return sha, subject


def continuity_headline(p: dict) -> str:
    """The line CONTINUITY.md carries — the same string the board shows."""
    return p["headline"]


if __name__ == "__main__":
    import sys
    p = progress()
    print(p["headline"])
    print("forecast (Define, 7.9):", p["plan"]["forecast_define"], "·", p["plan"]["basis"])
    for x in p["problems"]:
        print("PROBLEM:", x)
    sys.exit(1 if p["problems"] else 0)
