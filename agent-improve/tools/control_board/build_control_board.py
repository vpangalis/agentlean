"""Render `docs/control-board.html` — THE ONE PAGE. Step 6.67 (founder ruling 2026-09-26).

Generated from three sources only: `docs/define_features.json`,
`docs/test-results.json` and git log. Four parts:

  1. "N of 64 Define features pass", split by the five clauses and by lane
  2. the next failing feature per lane, with its description
  3. a burn-up — passing features per day, projected to the total, marked at 1 October
  4. the last commits with their timing lines (the `Timing:` trailer that
     `.githooks/prepare-commit-msg` writes)

The page embeds its numbers as JSON (`progress-data`) so `check_board.py`
(the commit guard's rule 10) and the session start can read them back.
The step waterfall, container, work-package, epic and architecture-diagram
views retired at 6.67: `docs/_archive/retired-tooling/control_board/`.

    python tools/control_board/build_control_board.py [out.html] [--staged]
"""
from __future__ import annotations

import datetime as dt
import html
import json
import subprocess
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

import features  # noqa: E402

OUT = features.PROJECT / "docs" / "control-board.html"
REPO = features.PROJECT.parent
TARGET = dt.date(2026, 10, 1)
E = html.escape


def _git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, encoding="utf-8",
                          errors="replace", timeout=60).stdout


def model() -> dict:
    """Everything the page shows, and everything the checker compares."""
    feats = features.load()
    s = features.summary(feats)
    by_id = {f["id"]: f for f in feats}
    nxt = {lane: ({"id": v["next"], "description": by_id[v["next"]]["description"],
                   "test": by_id[v["next"]]["test"]} if v["next"] else None)
           for lane, v in s["lanes"].items()}
    return {"headline": features.headline(s), "passing": s["passing"], "total": s["total"],
            "fresh": s["fresh"], "lanes": {k: {"passing": v["passing"], "total": v["total"]}
                                           for k, v in s["lanes"].items()},
            "clauses": s["clauses"], "next": nxt, "statuses": s["status"]}


def burnup(feats: list[dict]) -> list[tuple[str, int]]:
    """(date, passing) per day: the last recorded run of each day, scored
    against TODAY's feature list, from git log of test-results.json."""
    rows = _git("log", "--format=%H %ad", "--date=short", "--since=30 days ago", "--",
                "agent-improve/docs/test-results.json").split("\n")
    last: dict[str, str] = {}
    for row in reversed([r for r in rows if r.strip()]):
        sha, day = row.split()
        last[day] = sha                                   # later commits overwrite earlier ones
    out = []
    for day, sha in sorted(last.items()):
        try:
            res = json.loads(_git("show", f"{sha}:agent-improve/docs/test-results.json") or "{}")
        except ValueError:
            continue
        out.append((day, sum(v == "passing" for v in features.status(feats, res).values())))
    today = dt.date.today().isoformat()
    now = sum(v == "passing" for v in features.status(feats, features.results()).values())
    if not out or out[-1][0] != today:
        out.append((today, now))
    else:
        out[-1] = (today, now)
    return out


def projection(points: list[tuple[str, int]], total: int) -> str | None:
    """The day the straight line through the first and last point reaches `total`."""
    if len(points) < 2:
        return None
    d0, n0 = dt.date.fromisoformat(points[0][0]), points[0][1]
    d1, n1 = dt.date.fromisoformat(points[-1][0]), points[-1][1]
    days = (d1 - d0).days
    if days <= 0 or n1 <= n0:
        return None
    rate = (n1 - n0) / days
    return (d1 + dt.timedelta(days=round((total - n1) / rate))).isoformat()


def commits(n: int = 12) -> list[dict]:
    out = []
    for block in _git("log", f"-{n}", "--format=%h%x1f%ad%x1f%s%x1f%b%x1e", "--date=short").split("\x1e"):
        parts = block.strip().split("\x1f")
        if len(parts) < 4:
            continue
        sha, day, subject, body = parts
        timing = next((ln.split(":", 1)[1].strip() for ln in body.splitlines()
                       if ln.startswith("Timing:")), "")
        out.append({"sha": sha, "day": day, "subject": subject, "timing": timing})
    return out


def _svg(points: list[tuple[str, int]], total: int, proj: str | None) -> str:
    if not points:
        return "<p class='meta'>No recorded runs yet.</p>"
    first = dt.date.fromisoformat(points[0][0])
    last_day = max(TARGET, dt.date.fromisoformat(points[-1][0]),
                   dt.date.fromisoformat(proj) if proj else TARGET)
    span = max((last_day - first).days, 1)
    W, H, L, B = 640, 220, 40, 30

    def x(day: str) -> float:
        return L + (dt.date.fromisoformat(day) - first).days / span * (W - L - 10)

    def y(n: float) -> float:
        return H - B - n / max(total, 1) * (H - B - 10)

    path = " ".join(f"{'M' if i == 0 else 'L'}{x(d):.1f},{y(n):.1f}" for i, (d, n) in enumerate(points))
    dots = "".join(f"<circle cx='{x(d):.1f}' cy='{y(n):.1f}' r='3' class='pt'><title>{d}: {n}</title></circle>"
                   for d, n in points)
    proj_line = (f"<line x1='{x(points[-1][0]):.1f}' y1='{y(points[-1][1]):.1f}' x2='{x(proj):.1f}' "
                 f"y2='{y(total):.1f}' class='proj'/>") if proj else ""
    tx = x(TARGET.isoformat())
    return (f"<svg viewBox='0 0 {W} {H}' role='img' aria-label='Burn-up of passing Define features'>"
            f"<line x1='{L}' y1='{y(total):.1f}' x2='{W - 10}' y2='{y(total):.1f}' class='goal'/>"
            f"<text x='{L + 4}' y='{y(total) - 4:.1f}' class='lbl'>{total} — all Define features</text>"
            f"<line x1='{tx:.1f}' y1='10' x2='{tx:.1f}' y2='{H - B}' class='target'/>"
            f"<text x='{tx + 4:.1f}' y='22' class='lbl'>1 October</text>"
            f"<line x1='{L}' y1='{H - B}' x2='{W - 10}' y2='{H - B}' class='axis'/>"
            f"<text x='{L}' y='{H - 8}' class='lbl'>{first.isoformat()}</text>"
            f"<text x='{W - 10}' y='{H - 8}' class='lbl' text-anchor='end'>{last_day.isoformat()}</text>"
            f"{proj_line}<path d='{path}' class='line'/>{dots}</svg>")


CSS = """
:root{--bg:#fbfbf9;--fg:#1d1d1b;--muted:#6b6b66;--line:#e4e3de;--pass:#1f7a4d;--fail:#b3261e;--accent:#3559c7;--card:#ffffff}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#161615;--fg:#ecebe6;--muted:#a3a29c;--line:#34332f;--pass:#5cc08d;--fail:#f08a80;--accent:#8aa6ff;--card:#1f1f1d}}
:root[data-theme="dark"]{--bg:#161615;--fg:#ecebe6;--muted:#a3a29c;--line:#34332f;--pass:#5cc08d;--fail:#f08a80;--accent:#8aa6ff;--card:#1f1f1d}
body{background:var(--bg);color:var(--fg);font:15px/1.5 system-ui,sans-serif;margin:0}
.wrap{max-width:900px;margin:0 auto;padding:24px 16px}
h1{font-size:1.5rem;margin:0 0 4px}h2{font-size:1.1rem;margin:28px 0 8px}
.meta{color:var(--muted);font-size:.85rem}
table{border-collapse:collapse;width:100%}td,th{border-bottom:1px solid var(--line);padding:6px 8px;text-align:left;vertical-align:top}
th{font-weight:600}.num{text-align:right;white-space:nowrap}
.pass{color:var(--pass);font-weight:600}.fail{color:var(--fail);font-weight:600}
.card{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:12px}
svg{width:100%;height:auto}.line{fill:none;stroke:var(--accent);stroke-width:2}.pt{fill:var(--accent)}
.proj{stroke:var(--accent);stroke-dasharray:5 4}.goal{stroke:var(--pass);stroke-dasharray:2 3}
.target{stroke:var(--fail);stroke-dasharray:4 3}.axis{stroke:var(--line)}.lbl{fill:var(--muted);font-size:11px}
code{font-size:.8rem}
"""


def render(m: dict, points: list[tuple[str, int]], proj: str | None, log: list[dict]) -> str:
    def frac(v: dict) -> str:
        return f"{v['passing']} of {v['total']}"

    clauses = "".join(f"<tr><td>{E(c)}</td><td class='num'>{frac(v)}</td></tr>" for c, v in m["clauses"].items())
    lanes = "".join(f"<tr><td>{E(k)} — {E(features.LANES[k])}</td><td class='num'>{frac(v)}</td></tr>"
                    for k, v in m["lanes"].items())
    nxt = "".join(
        f"<tr><td>{E(k)}</td><td>" + (f"<b>{E(v['id'])}</b> — {E(v['description'])}<br><code>{E(v['test'])}</code>"
                                      if v else "every feature passes") + "</td></tr>"
        for k, v in m["next"].items())
    logrows = "".join(f"<tr><td><code>{E(c['sha'])}</code></td><td>{E(c['day'])}</td><td>{E(c['subject'])}</td>"
                      f"<td class='meta'>{E(c['timing']) or '—'}</td></tr>" for c in log)
    proj_txt = (f"At the rate so far, all {m['total']} pass on <b>{E(proj)}</b>." if proj
                else "No projection yet: it needs two days of recorded runs with progress between them.")
    data = json.dumps({k: m[k] for k in ("headline", "passing", "total", "statuses", "next")},
                      ensure_ascii=False, sort_keys=True).replace("</", "<\\/")
    stale = "" if m["fresh"] else "<p class='fail'>The recorded test run is older than the source — the numbers are from the last run.</p>"
    return f"""<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>Define board</title>
<style>{CSS}</style></head><body><div class="wrap">
<h1 data-key="headline">{E(m['headline'])}</h1>
<p class="meta">Generated by <code>tools/control_board/build_control_board.py</code> from <code>define_features.json</code>, <code>test-results.json</code> and git log. A feature passes only when its end-to-end test passes. Nothing here is typed by hand.</p>
{stale}
<h2>1 · By clause and by lane</h2>
<div class="card"><table><tr><th>Clause of "Define works end to end"</th><th class="num">Passing</th></tr>{clauses}</table></div>
<div class="card" style="margin-top:12px"><table><tr><th>Lane</th><th class="num">Passing</th></tr>{lanes}</table></div>
<h2>2 · Next failing feature per lane</h2>
<div class="card"><table>{nxt}</table></div>
<h2>3 · Burn-up</h2>
<div class="card">{_svg(points, m['total'], proj)}<p class="meta">{proj_txt} Dashed red: 1 October.</p></div>
<h2>4 · Last commits and their timing</h2>
<div class="card"><table><tr><th>Commit</th><th>Day</th><th>Subject</th><th>Timing</th></tr>{logrows}</table></div>
<script type="application/json" id="progress-data">{data}</script>
</div></body></html>
"""


def build(out: Path = OUT) -> Path:
    m = model()
    points = burnup(features.load())
    out.write_text(render(m, points, projection(points, m["total"]), commits()), encoding="utf-8")
    return out


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    print(f"control board -> {build(Path(args[0]) if args else OUT)}")
