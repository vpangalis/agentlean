# -*- coding: utf-8 -*-
"""Render `docs/control-board.html` — THE ONLY PROGRESS VIEW. Step 6.63.

Founder rulings 2026-09-25: *"The only progress view is the repo's generated
control-board.html. The published 'Control Board' artifact on claude.ai is
retired."* · *"Every number, label, diagram element and status colour on the
board is derived from the tree, never typed by hand."* · *"Headline: 'N of 35
capabilities proven · working on: <step name>'."*

WHAT THIS PAGE READS — and nothing else
    progress.progress()   every number, every status and its reference, the
                          plan and its forecast (the one function)
    progress.statuses()   the status set; each is rendered with `data-key`,
                          `data-ref` and a hover title naming its reference
    stories.py            the epic and story each step belongs to
    shape.shape()         the architecture diagram, and each container's
                          "what is there", read from the code

THE WATERFALL IS GROUPED THREE WAYS (step 6.64), a switch at the top:
    Container (default)   every registered step under its Appendix F Layer,
                          named by that table's `#### L<n> · <name>` headings
    Work package          the estimate table's WP0–WP6
    Epic / story          stories.py's epic -> story -> task tree

WHAT THE INTEGRITY CHECK (`check_board.py`) HOLDS IT TO
    every coloured element carries a `data-key` that `statuses()` recomputes
    to the same colour and reference; every diagram label carries a
    `data-key` that `shape.labels()` recomputes to the same text; the
    headline equals CONTINUITY.md's; the container view carries every
    registered step once, under the container the tree gives it. A colour or
    label typed by hand has no key, or a key that recomputes to something
    else, and fails the commit.

    python build_control_board.py [out.html] [--staged]
"""
from __future__ import annotations

import datetime as dt
import html
import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

import progress  # noqa: E402
import stories   # noqa: E402

OUT = progress.PROJECT / "docs" / "control-board.html"
E = html.escape


# ══ the model: everything the page shows, computed once ══════════════════════


def model(staged: bool = False, today: dt.date | None = None, with_shape: bool = True) -> dict:
    p = progress.progress(progress.procedure_text(staged), today=today)
    stories.resolve(p)
    m: dict[str, Any] = {"p": p, "statuses": progress.statuses(p),
                         "built_from": progress.built_from()}
    m["labels"] = {}
    if with_shape:
        import shape
        m["shape"] = shape.shape()
        m["labels"] = shape.labels(m["shape"])
    # 6.66 — Define's feature list, status only from test-results.json.
    import features
    m["labels"]["features"] = features.headline()
    return m


def summary(m: dict) -> dict:
    """What the page embeds for the session-start hook and the next commit's
    regression check: the headline, the forecast, and every status."""
    p = m["p"]
    wo = p["working_on"]
    return {"headline": p["headline"],
            "working_on": {"step": wo["step"], "title": wo["title"]} if wo else None,
            "forecast_define": p["plan"]["forecast_define"],
            "forecast_basis": p["plan"]["basis"],
            "conditional_on": p["plan"]["conditional_on"],
            "built_from": m["built_from"][0],
            "statuses": {k: {"colour": v["colour"], "ref": v["ref"]}
                         for k, v in sorted(m["statuses"].items())}}


# ══ small pieces ═════════════════════════════════════════════════════════════


def st(m: dict, key: str, text: str | None = None) -> str:
    """One status, with its reference on hover. The ONLY way a colour enters
    the page."""
    v = m["statuses"][key]
    label = text if text is not None else v["colour"]
    return (f'<span class="st c-{v["colour"]}" data-key="{E(key)}" data-ref="{E(v["ref"])}" '
            f'title="{E(v["ref"])} — {E(v["why"] or "")}">{E(label)}</span>')


def lbl(m: dict, key: str) -> str:
    """One diagram label, read from the code."""
    return f'<span class="lbl" data-key="{E(key)}">{E(m["labels"][key])}</span>'


def _d(s: str | None) -> dt.date | None:
    return dt.date.fromisoformat(s) if s else None


# ══ the waterfall ════════════════════════════════════════════════════════════


#: The waterfall's three groupings (6.64), the first the default.
VIEWS: tuple[tuple[str, str], ...] = (("ctr", "Container"), ("wp", "Work package"),
                                      ("epic", "Epic / story"))


def _row(s: str, stp: dict, bars: dict, today: dt.date) -> dict:
    """One step's bars: planned (from the plan, or from its estimate after it
    started) and actual (git's first commit to its landing commit)."""
    b = bars.get(s)
    a0, a1 = _d(stp["first_date"]), _d(stp["landed_date"])
    if b:
        p0, p1 = _d(b["start"]), _d(b["end"])
    elif a0 and stp["estimate"]:
        p0, p1 = a0, progress.add_workdays(a0, stp["estimate"])
    else:
        p0 = p1 = None
    # A step started and not yet landed runs to today — DONE in the tree
    # included: the commit that lands it is the one being built (6.61's own
    # pre-commit build, where the ✅ is staged before its landing commit exists).
    return {"s": s, "st": stp, "p0": p0, "p1": p1, "a0": a0,
            "a1": a1 or (today if a0 else None),
            "open": bool(a0 and not a1), "wait": (b or {}).get("waiting_on", [])}


def waterfall(m: dict) -> str:
    """The waterfall, three ways — one time axis, a switch at the top (6.64).

    The axis is the PLAN's: the work-package steps and the Order. The container
    view carries every registered step, so a step that landed before the axis
    begins shows its landing date instead of a bar."""
    p = m["p"]
    steps, plan = p["steps"], p["plan"]
    bars = {b["step"]: b for b in plan["bars"]}
    today = dt.date.fromisoformat(p["today"])
    shown = list(dict.fromkeys([s for s in steps if steps[s]["wp"]] + p["order"]))
    rows = {s: _row(s, steps[s], bars, today) for s in steps}
    dates = [d for s in shown for d in (rows[s]["p0"], rows[s]["p1"], rows[s]["a0"], rows[s]["a1"]) if d] + [today]
    lo, hi = min(dates) - dt.timedelta(days=2), max(dates) + dt.timedelta(days=4)
    span = (hi - lo).days or 1

    def x(d: dt.date) -> float:
        return round((max(d, lo) - lo).days / span * 100, 2)

    def bar(cls: str, a: dt.date, b: dt.date, tip: str) -> str:
        if b < lo:
            return ""
        left, width = x(a), max(0.8, x(b + dt.timedelta(days=1)) - x(a))
        return f'<div class="bar {cls}" style="left:{left}%;width:{width}%" title="{E(tip)}"></div>'

    ticks = []
    d = lo + dt.timedelta(days=(7 - lo.weekday()) % 7)
    while d <= hi:
        ticks.append(f'<div class="tick" style="left:{x(d)}%"><span>{d.strftime("%d %b")}</span></div>')
        d += dt.timedelta(days=7)
    marks = [f'<div class="today" style="left:{x(today)}%" title="today, {today.isoformat()}"></div>']
    fd = _d(plan["forecast_define"])
    if fd:
        marks.append(f'<div class="fline" style="left:{x(fd + dt.timedelta(days=1))}%" '
                     f'title="Define forecast finish (7.9): {fd.isoformat()}"></div>')
    grid = "".join(ticks) + "".join(marks)

    def row(r: dict, cv: str = "") -> str:
        s, stp = r["s"], r["st"]
        tag = stp["epic"] + (" (proposed)" if stp["epic_proposed"] else "") + \
            (f" · {stp['story']}" if stp["story"] else "")
        lanes = []
        if r["p0"]:
            tip = (f"planned {r['p0']} → {r['p1']} · {stp['estimate']:g} day(s) estimated"
                   if stp["estimate"] else "no estimate")
            if r["wait"]:
                tip += " · waiting on " + ", ".join(r["wait"])
            lanes.append(bar("plan" + (" wait" if r["wait"] else ""), r["p0"], r["p1"], tip))
        if r["a0"]:
            tip = (f"actual {stp['first_date']} ({stp['first_commit']}) → "
                   + (f"{stp['landed_date']} ({stp['landed_commit']})" if stp["landed_date"] else "not landed"))
            lanes.append(bar("act" + (" open" if r["open"] else ""), r["a0"], r["a1"], tip))
        wait = "".join(f'<span class="wt" title="a founder input — waiting, not late">waiting on {E(w)}</span>'
                       for w in r["wait"])
        est = f"{stp['estimate']:g} d" if stp["estimate"] else '<span class="miss">no estimate</span>'
        early = (f' <span class="na">landed {E(stp["landed_date"])}, before this axis</span>'
                 if r["a1"] and r["a1"] < lo else "")
        attr = f' data-cv="{E(s)}"' if cv else ""
        return (f'<div class="wrow"{attr}><div class="wlab"><b>{E(s)}</b> {E(stp["title"])}'
                f'<div class="meta"><span class="tag">{E(tag)}</span> {est} {st(m, f"step:{s}:state", stp["state"])} {wait}{early}</div></div>'
                f'<div class="wtrack">{grid}{"".join(lanes)}</div></div>')

    def group(title: str, meta: str, rs: list[dict], body: str, opened: bool = True,
              attr: str = "") -> str:
        """A collapsible group: its own bar spans its steps' earliest start to
        latest end. `title` and `meta` arrive escaped (meta may carry a pill)."""
        ends = [r["p1"] or r["a1"] for r in rs if (r["p1"] or r["a1"])]
        starts = [r["a0"] or r["p0"] for r in rs if (r["a0"] or r["p0"])]
        wbar = bar("wp", min(starts), max(ends), f"{title}: {min(starts)} → {max(ends)}") if starts else ""
        return (f'<details class="wp"{attr}{" open" if opened else ""}><summary><div class="wrow">'
                f'<div class="wlab"><b>{title}</b><div class="meta">{meta}</div></div>'
                f'<div class="wtrack">{grid}{wbar}</div></div></summary>{body}</details>')

    def num(s: str) -> tuple:
        return tuple(int(x) for x in s.split("."))

    in_order = set(p["order"])

    # ── Container (the default): every registered step, under its Layer ──
    ctr_out = []
    for c in p["containers"]:
        rs = sorted((rows[s] for s in c["steps"]),
                    key=lambda r: (r["st"]["order"] is None, r["st"]["order"] or 0, num(r["s"])))
        done = sum(r["st"]["done"] for r in rs)
        meta = f'{st(m, "ctr:" + c["id"], c["id"])} {done} of {len(rs)} done · {len(c["open"])} open'
        ctr_out.append(group(E(f'{c["id"]} · {c["name"]}'), meta, rs,
                             "".join(row(r, cv=c["id"]) for r in rs),
                             opened=any(s in in_order and not steps[s]["done"] for s in c["steps"]),
                             attr=f' data-ctr="{E(c["id"])}"'))

    # ── Work package, as 6.63 drew it ──
    groups: dict[str, list[dict]] = {}
    for s in shown:
        groups.setdefault(steps[s]["wp"] or "No work package", []).append(rows[s])
    wp_out = []
    for wp in sorted(groups, key=lambda w: (w == "No work package", w)):
        rs = groups[wp]
        ends = [r["p1"] or r["a1"] for r in rs if (r["p1"] or r["a1"])]
        done = sum(r["st"]["done"] for r in rs)
        wp_out.append(group(E(wp), f'{done} of {len(rs)} done · finishes {max(ends) if ends else "—"}',
                            rs, "".join(row(r) for r in rs)))

    # ── Epic / story: stories.py's tree, every status derived ──
    epic_out = []
    storied: set[str] = set()
    for ep in stories.EPICS:
        body, ep_rows = [], []
        for sto in ep["stories"]:
            pill = (st(m, f"story:{sto['id']}", "done" if sto["status"] == "done" else "open")
                    if sto["rows"] else '<span class="na">no acceptance rows — no source</span>')
            body.append(f'<div class="story"><b>{E(sto["id"])}</b> {E(sto["title"])} {pill}</div>')
            for code, title, comp, _state, _ref in sto["tasks"]:
                if code in steps:
                    storied.add(code)
                    ep_rows.append(rows[code])
                    body.append(row(rows[code]))
                else:
                    body.append(f'<div class="wrow"><div class="wlab"><b>task</b> {E(title)}'
                                f'<div class="meta">{E(comp)} · <span class="na">not a procedure step — '
                                f'its status has no source</span></div></div><div class="wtrack">{grid}</div></div>')
            for bug in sto["bugs"]:
                text, comp, where = bug[0], bug[1], bug[-1]
                body.append(f'<div class="wrow"><div class="wlab"><b>bug</b> {E(text)}'
                            f'<div class="meta">{E(comp)} · found at {E(where)} · <span class="na">'
                            f'status: no source in the tree</span></div></div><div class="wtrack">{grid}</div></div>')
        n_rows = sum(bool(sto["rows"]) for sto in ep["stories"])
        n_done = sum(sto["status"] == "done" for sto in ep["stories"] if sto["rows"])
        n_none = len(ep["stories"]) - n_rows
        meta = (f'{n_done} of {n_rows} stories done (by their acceptance rows)'
                + (f' · {n_none} with no rows, so no derived status' if n_none else '')
                if n_rows else
                f'{n_none} stories — none has acceptance rows, so none has a derived status')
        epic_out.append(group(E(f'{ep["id"]} · {ep["title"]}'), meta, ep_rows, "".join(body),
                              opened=any(r["s"] in in_order and not r["st"]["done"] for r in ep_rows)))
    rest = [rows[s] for s in shown if s not in storied]
    if rest:
        epic_out.append(group("Not in stories.py", "planned steps no story lists yet", rest,
                              "".join(row(r) for r in rest)))

    ms_rows = []
    for mid, mv in p["milestones"].items():
        needed = [bars[s]["start"] for s in mv["blocks"] if s in bars]
        dia = (f'<div class="dia" style="left:{x(dt.date.fromisoformat(min(needed)))}%" '
               f'title="{E(mid)} needed by {min(needed)}"></div>'
               if needed else "")
        where = "off the path" if mv["off_path"] else ("blocks " + ", ".join(mv["blocks"]))
        ms_rows.append(f'<div class="wrow"><div class="wlab"><b>◆ {E(mid)}</b> {E(mv["what"])}'
                       f'<div class="meta">{E(where)}' + (f" · needed by {min(needed)}" if needed else "")
                       + f'</div></div><div class="wtrack">{grid}{dia}</div></div>')
    founder = ('<details class="wp" open><summary><div class="wrow"><div class="wlab"><b>Founder inputs</b>'
               '<div class="meta">milestones — a step waiting on one is waiting, not late</div></div>'
               f'<div class="wtrack">{grid}</div></div></summary>' + "".join(ms_rows) + "</details>")
    head = ('<div class="wrow whead"><div class="wlab"></div><div class="wtrack">'
            + "".join(ticks) + "".join(marks) + "</div></div>")
    by_view = {"ctr": "".join(ctr_out), "wp": "".join(wp_out), "epic": "".join(epic_out)}
    radios = "".join(f'<input type="radio" name="wf" id="wf-{k}" class="vsw"{" checked" if i == 0 else ""}>'
                     for i, (k, _) in enumerate(VIEWS))
    labels = "".join(f'<label for="wf-{k}">{E(t)}</label>' for k, t in VIEWS)
    views = "".join(f'<div class="view view-{k}" data-view="{k}">{head}{by_view[k]}</div>' for k, _ in VIEWS)
    return f'{radios}<div class="vbar">Group by: {labels}</div>{views}{founder}'


# ══ the diagram ══════════════════════════════════════════════════════════════


def _graph_svg(m: dict, which: str) -> str:
    g = m["shape"][which]
    nodes = ["__start__"] + g["nodes"] + ["__end__"]
    w, gap, y = 118, 22, 70
    pos = {n: 10 + i * (w + gap) for i, n in enumerate(nodes)}
    width = 20 + len(nodes) * (w + gap)
    parts = []
    for i, e in enumerate(g["edges"]):
        key = f"g:{which}:e:{i}"
        a, b = pos[e["from"]] + w / 2, pos[e["to"]] + w / 2
        fwd = b > a
        if abs(b - a) <= w + gap and fwd and not e["conditional"]:
            d = f"M{a + w / 2},{y} L{b - w / 2},{y}"
        else:
            cy = y - 18 - abs(b - a) / 6 if fwd else y + 18 + abs(b - a) / 6
            sy = y - 14 if fwd else y + 14
            d = f"M{a},{sy} Q{(a + b) / 2},{cy} {b},{sy}"
        cls = "edge cond" if e["conditional"] else "edge"
        parts.append(f'<path d="{d}" class="{cls}" marker-end="url(#ah)" data-key="{key}">'
                     f'<title>{E(m["labels"][key])}</title></path>')
    for i, n in enumerate(nodes):
        cls = "gnode term" if n.startswith("__") else "gnode"
        parts.append(f'<rect x="{pos[n]}" y="{y - 14}" width="{w}" height="28" rx="6" class="{cls}"/>'
                     f'<text x="{pos[n] + w / 2}" y="{y + 4}" text-anchor="middle" class="gtext" '
                     f'data-key="g:{which}:n:{i}">{E(m["labels"][f"g:{which}:n:{i}"])}</text>')
    return (f'<svg viewBox="0 0 {width} 150" class="graph" role="img" aria-label="{E(which)}">'
            '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" class="arrow"/></marker></defs>'
            + "".join(parts) + "</svg>")


def diagram(m: dict) -> str:
    if "shape" not in m:
        return '<p class="miss">The diagram was not built: the code could not be read.</p>'
    sh = m["shape"]
    mw = "".join(
        f'<div class="mw"><div class="mwh"><b>{lbl(m, "mw:%d:class" % b["position"])}</b>'
        f'<span class="pos">{b["position"]}</span></div>'
        f'<div class="mwl">{lbl(m, "mw:%d:on" % b["position"])} · {lbl(m, "mw:%d:hooks" % b["position"])}</div>'
        + (f'<div class="mwc">{lbl(m, "mw:%d:config" % b["position"])}</div>' if b["config"] else "")
        + (f'<div class="mwc">{lbl(m, "skills:label")}</div>' if b["class"] == "DMAICSkillsMiddleware" else "")
        + f'<div class="src">{E(b["source"])}</div></div>'
        for b in sh["middleware"])
    blocks = []
    for i, blk in enumerate(sh["coach_inputs"]["blocks"]):
        secs = "".join(f'<li>{lbl(m, f"in:{i}:{j}")}</li>' for j, _ in enumerate(blk["sections"]))
        blocks.append(f'<div class="inb"><b>{lbl(m, f"in:{i}:block")}</b>'
                      + (f'<ol>{secs}</ol>' if secs else "")
                      + f'<div class="src">{E(blk["source"])}</div></div>')
    return f'''
<div class="ctr"><div class="ctrh">Container 1 · the turn graph <span class="src">POST /ask → backend/core/graph.py::get_graph("{E(sh["phase"])}")</span></div>
{_graph_svg(m, "turn_graph")}</div>
<div class="ctr"><div class="ctrh">Container 2 · the {E(sh["phase"])} phase subgraph <span class="src">backend/phases/subgraph_common.py::build_phase_subgraph — dashed = conditional</span></div>
{_graph_svg(m, "phase_graph")}</div>
<div class="ctr"><div class="ctrh">Container 3 · inside the executor node — create_agent's middleware, in declared order <span class="src">backend/phases/nodes_common.py::_build_executor</span></div>
<div class="mwgrid">{mw}</div>
<div class="sub">What the coach receives, in order — its system message as the middleware builds it</div>
<div class="ingrid">{"".join(blocks)}</div>
<div class="sub">Tools the coach can call</div>
<div class="tools">{lbl(m, "tools")} · registered by a middleware: {lbl(m, "skills:tools")}</div></div>'''


# ══ tables ═══════════════════════════════════════════════════════════════════


def steps_table(m: dict) -> str:
    p = m["p"]
    rows = []
    for s, stp in p["steps"].items():
        proven = st(m, f"step:{s}:proven", "proven") if stp["rows"] else '<span class="na">no row</span>'
        rows.append(f'<tr><td><b>{E(s)}</b></td><td>{E(stp["title"])}</td>'
                    f'<td>{st(m, f"step:{s}:built", "built")}</td><td>{st(m, f"step:{s}:wired", "wired")}</td>'
                    f'<td>{proven}</td><td>{st(m, f"step:{s}:state", stp["state"])}</td></tr>')
    return ('<table class="t"><thead><tr><th>Step</th><th>Title</th><th>Built</th><th>Wired</th>'
            '<th>Proven</th><th>State</th></tr></thead><tbody>' + "".join(rows) + "</tbody></table>")


def caps_table(m: dict) -> str:
    """Appendix H, grouped by container — through each row's owning steps'
    Layer (6.64). A row owned by steps in two containers is listed under both;
    a row no step owns is listed on its own, never dropped."""
    p = m["p"]
    names = {c["id"]: c["name"] for c in p["containers"]}

    def line(c: dict) -> str:
        return (f'<tr><td><b>{c["row"]}</b></td><td>{E(c["capability"])}</td>'
                f'<td>{E(", ".join(c["owners"]) or "—")}</td>'
                f'<td>{st(m, "cap:%d" % c["row"], "proven" if c["proven"] else c["colour"])}</td></tr>')

    body = []
    for cid, name in names.items():
        rows = [c for c in p["capabilities"] if cid in c["containers"]]
        if rows:
            proven = sum(c["proven"] for c in rows)
            body.append(f'<tr class="grp"><td colspan="4">{E(cid)} · {E(name)} — '
                        f'{proven} of {len(rows)} proven</td></tr>' + "".join(line(c) for c in rows))
    orphans = [c for c in p["capabilities"] if not c["containers"]]
    if orphans:
        body.append('<tr class="grp"><td colspan="4">No owning step — no container</td></tr>'
                    + "".join(line(c) for c in orphans))
    return ('<table class="t"><thead><tr><th>Row</th><th>Capability</th><th>Given by</th><th>State</th>'
            '</tr></thead><tbody>' + "".join(body) + "</tbody></table>")


#: The word a container's pill shows, per colour.
_CTR_WORD = {"green": "all done", "red": "open work", "built": "built, not wired", "waiting": "waiting"}


def container_cards(m: dict) -> str:
    """One card per container (6.64): what is there, read from the code, and
    the open steps from Appendix F, each with its derived colour and reference."""
    p, out = m["p"], []
    comps = (m.get("shape") or {}).get("components", {})
    for c in p["containers"]:
        cid = c["id"]
        items = comps.get(cid)
        if items is None:
            what = '<li class="na">no reader for this container — nothing is claimed</li>'
        else:
            what = "".join(f'<li>{lbl(m, f"cmp:{cid}:{i}")} <span class="src">{E(it["source"])}</span></li>'
                           for i, it in enumerate(items))
        steps = p["steps"]
        opened = sorted(c["open"], key=lambda s: (steps[s]["order"] is None, steps[s]["order"] or 0,
                                                  tuple(int(x) for x in s.split("."))))
        open_li = "".join(
            f'<li>{st(m, f"step:{s}:state", steps[s]["state"])} <b>{E(s)}</b> {E(steps[s]["title"])}'
            + (f' <span class="na">· Order {steps[s]["order"]}</span>' if steps[s]["order"] else "")
            + "</li>" for s in opened) or '<li class="na">nothing open</li>'
        done = [s for s in c["steps"] if steps[s]["done"]]
        colour = m["statuses"][f"ctr:{cid}"]["colour"]
        out.append(
            f'<div class="card"><div class="cardh"><b>{E(cid)} · {E(c["name"])}</b> '
            f'{st(m, f"ctr:{cid}", _CTR_WORD[colour])}</div>'
            f'<div class="sub">What is there — read from the code</div><ul class="cl">{what}</ul>'
            f'<div class="sub">Open steps — Appendix F ({len(opened)} of {len(c["steps"])})</div><ul class="cl">{open_li}</ul>'
            f'<div class="meta">done: {", ".join(done) or "none"}</div></div>')
    return f'<div class="cards">{"".join(out)}</div>'


# ══ the page ═════════════════════════════════════════════════════════════════

CSS = """
:root{--bg:#f7f7f5;--fg:#1d1d1b;--mut:#6b6b66;--line:#dcdcd6;--card:#fff;
--green:#2f8f4e;--amber:#c98a12;--red:#c0392b;--built:#3a6fc4;--waiting:#8a8a84;
--plan:#b9c7e6;--act:#2f8f4e;--wp:#d8d8d2;--today:#c0392b;--fline:#7a3fc4}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){--bg:#171716;--fg:#ecece8;--mut:#a3a39c;
--line:#34342f;--card:#20201e;--plan:#3a4a6e;--wp:#3a3a35}}
:root[data-theme="dark"]{--bg:#171716;--fg:#ecece8;--mut:#a3a39c;--line:#34342f;--card:#20201e;--plan:#3a4a6e;--wp:#3a3a35}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,-apple-system,Segoe UI,sans-serif}
.wrap{max-width:1400px;margin:0 auto;padding:20px 16px 60px}
h1{font-size:22px;margin:0 0 4px}h2{font-size:17px;margin:34px 0 10px;border-bottom:1px solid var(--line);padding-bottom:4px}
.built{color:var(--mut);font-size:12.5px}.fc{margin:10px 0 0;padding:10px 12px;background:var(--card);border:1px solid var(--line);border-radius:8px}
.st{display:inline-block;padding:0 7px;border-radius:9px;font-size:11.5px;color:#fff;cursor:help;white-space:nowrap}
.c-green{background:var(--green)}.c-amber{background:var(--amber)}.c-red{background:var(--red)}.c-built{background:var(--built)}.c-waiting{background:var(--waiting)}
.legend>span{margin-right:10px}
.sw{display:inline-block;padding:0 7px;border-radius:9px;font-size:11.5px;color:#fff}
.sw-green{background:var(--green)}.sw-amber{background:var(--amber)}.sw-red{background:var(--red)}.sw-built{background:var(--built)}.sw-waiting{background:var(--waiting)}
.wrow{display:grid;grid-template-columns:minmax(260px,32%) 1fr;align-items:center;border-bottom:1px solid var(--line);min-height:38px}
.wlab{padding:4px 8px 4px 0;font-size:13px}.meta{color:var(--mut);font-size:11.5px;margin-top:2px}
.tag{border:1px solid var(--line);border-radius:4px;padding:0 4px}.wt{color:var(--waiting);font-style:italic}
.wtrack{position:relative;height:30px}.whead .wtrack{height:22px}
.tick{position:absolute;top:0;bottom:0;border-left:1px dashed var(--line)}.tick span{font-size:10.5px;color:var(--mut);padding-left:3px}
.whead .tick{border:none}.wp>summary{list-style:none;cursor:pointer}.wp>summary .wlab b:before{content:"▾ ";color:var(--mut)}
.wp:not([open])>summary .wlab b:before{content:"▸ "}
.bar{position:absolute;height:9px;border-radius:3px}.bar.plan{top:5px;background:var(--plan)}
.bar.plan.wait{background:repeating-linear-gradient(45deg,var(--plan),var(--plan) 4px,transparent 4px,transparent 8px);border:1px solid var(--waiting)}
.bar.act{top:16px;background:var(--act)}.bar.act.open{background:repeating-linear-gradient(90deg,var(--act),var(--act) 6px,transparent 6px,transparent 9px)}
.bar.wp{top:10px;height:10px;background:var(--wp)}
.today{position:absolute;top:0;bottom:0;border-left:2px solid var(--today);z-index:2}
.fline{position:absolute;top:0;bottom:0;border-left:2px dotted var(--fline);z-index:2}
.dia{position:absolute;top:8px;width:13px;height:13px;background:var(--fline);transform:translateX(-6px) rotate(45deg)}
.miss{color:var(--red)}.na{color:var(--mut);font-size:12px}
.ctr{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px;margin:12px 0}
.ctrh{font-weight:600;margin-bottom:6px}.src{font-weight:400;color:var(--mut);font-size:11px;font-family:ui-monospace,Consolas,monospace}
svg.graph{width:100%;max-width:980px;height:auto}.gnode{fill:var(--bg);stroke:var(--fg)}.gnode.term{fill:var(--line)}
.gtext{font-size:12px;fill:var(--fg)}.edge{fill:none;stroke:var(--mut);stroke-width:1.4}.edge.cond{stroke-dasharray:5 4}.arrow{fill:var(--mut)}
.mwgrid,.ingrid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:8px}
.mw,.inb{border:1px solid var(--line);border-radius:8px;padding:8px}.mwh{display:flex;justify-content:space-between}
.pos{color:var(--mut)}.mwl,.mwc{font-size:12px;margin-top:3px}.mwc{color:var(--mut)}
.inb ol{margin:4px 0 0 18px;padding:0;font-size:12px}.sub{margin:14px 0 6px;font-weight:600}.tools{font-size:12.5px}
table.t{border-collapse:collapse;width:100%;font-size:12.5px}table.t td,table.t th{border-bottom:1px solid var(--line);padding:4px 6px;text-align:left;vertical-align:top}
details.all>summary{cursor:pointer;font-weight:600;margin:8px 0}
.prob{color:var(--red)}
.vsw{position:absolute;opacity:0;pointer-events:none}.view{display:none}
#wf-ctr:checked~.view-ctr,#wf-wp:checked~.view-wp,#wf-epic:checked~.view-epic{display:block}
.vbar{margin:8px 0}.vbar label{display:inline-block;border:1px solid var(--line);border-radius:14px;padding:2px 12px;margin-right:6px;cursor:pointer;background:var(--card)}
#wf-ctr:checked~.vbar label[for=wf-ctr],#wf-wp:checked~.vbar label[for=wf-wp],#wf-epic:checked~.vbar label[for=wf-epic]{background:var(--fg);color:var(--bg);border-color:var(--fg)}
.vsw:focus-visible~.vbar{outline:2px solid var(--built);outline-offset:2px}
.story{margin:10px 0 2px;padding:3px 0 3px 8px;border-left:3px solid var(--line);font-size:13px}
.cards{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(320px,100%),1fr));gap:10px}
.card{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:10px 12px}
.cardh{display:flex;justify-content:space-between;align-items:center;gap:8px}
ul.cl{margin:2px 0 6px 16px;padding:0;font-size:12.5px}ul.cl li{margin:2px 0}
tr.grp td{background:var(--line);font-weight:600}
@media (max-width:700px){.wrow{grid-template-columns:1fr}.wtrack{height:30px}}
"""


def render(m: dict) -> str:
    p = m["p"]
    plan = p["plan"]
    sha, subject = m["built_from"]
    probs = "".join(f'<li class="prob">{E(x)}</li>' for x in p["problems"])
    cond = ", ".join(plan["conditional_on"]) or "nothing"
    data = json.dumps(summary(m), ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    shape_data = json.dumps(m.get("labels", {}), ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    legend = ('<div class="legend meta"><span><span class="sw sw-green">green</span> its reference passes on the current source</span>'
              '<span><span class="sw sw-amber">amber</span> it exists but is older than the code</span>'
              '<span><span class="sw sw-red">red</span> it fails, or there is none</span>'
              '<span><span class="sw sw-built">built</span> built, not wired</span>'
              '<span><span class="sw sw-waiting">waiting</span> on a founder input</span> · hover any status for its reference</div>')
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Control board</title>
<style>{CSS}</style></head><body><div class="wrap">
<h1 data-key="headline">{E(p["headline"])}</h1>
<div class="built">Built from <b>{E(sha)}</b> — {E(subject)} · source {E(p["source_hash"])} · tests recorded on source {E(str(p["results_hash"]))} at commit {E(str(p["results_commit"] or "—"))} · generated by <code>tools/control_board/build_control_board.py</code> from <code>progress.py</code>; nothing on this page is typed by hand</div>
<div class="fc"><b>Define finishes (7.9): {E(plan["forecast_define"] or "—")}</b> · conditional on {E(cond)} · {E(plan["basis"])}</div>
<div class="fc">{lbl(m, "features")} · <code>docs/define_features.json</code>, each feature passing only when its end-to-end test passes</div>
{"<ul>" + probs + "</ul>" if probs else ""}
{legend}
<h2>The waterfall — Appendix F's Order, each step's card, git log</h2>
<div class="meta">Planned bar (top) from the estimate; actual bar (bottom) from the first commit to the landing commit; red line today; dotted line the Define forecast; ◆ a founder input, placed where it is needed. Container is each step's Appendix F Layer, named by that table's headings; work package is the estimate table's; epic and story are <code>stories.py</code>'s.</div>
{waterfall(m)}
<h2>The containers — what is there, and what is open</h2>
{container_cards(m)}
<h2>The shape of it — read from the code</h2>
{diagram(m)}
<h2>Capabilities by container — Appendix H ({p["proven"]} of {p["total_caps"]} proven)</h2>
{caps_table(m)}
<details class="all"><summary>Every step — built · wired · proven ({len(p["steps"])} steps)</summary>{steps_table(m)}</details>
<script type="application/json" id="progress-data">{data}</script>
<script type="application/json" id="shape-labels">{shape_data}</script>
</div></body></html>
"""


def main(argv: list[str]) -> int:
    staged = "--staged" in argv
    args = [a for a in argv[1:] if not a.startswith("--")]
    out = Path(args[0]) if args else OUT
    out.write_text(render(model(staged=staged)), encoding="utf-8", newline="\n")
    print(f"control board -> {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
