"""Define's feature list — status ONLY from test results. Step 6.66.

Anthropic, *Effective harnesses for long-running agents*
(https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents):
the work is ONE JSON feature list; a feature is done when its end-to-end test
passes, never when someone says so. `docs/define_features.json` carries no
status field; this module derives it from `docs/test-results.json`:

    passing   the feature's test is recorded `passed`
    failing   recorded anything else, or never recorded (the test is not written yet)

and says whether that record is FRESH (run on the current source). The board,
CONTINUITY and the session-start routine read this, and nothing else.

It also names the sets the coverage test holds the list to — every Define
step, every capability row (Appendix H), every open Define gap:

    python tools/control_board/features.py              # summary, first failing per lane
    python tools/control_board/features.py --lane A     # the lane's failing features, in order
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
PROJECT = _HERE.parents[1]
FEATURES = PROJECT / "docs" / "define_features.json"
RESULTS = PROJECT / "docs" / "test-results.json"
LANES = {"A": "coaching", "B": "gate", "C": "screen and inputs", "integrator": "end-to-end joins"}
#: Work packages on the Define path that are NOT Define behaviour: WP0 the
#: board and tooling, WP6 the other four phases.
NOT_DEFINE_WP = ("WP0", "WP6")

sys.path.insert(0, str(_HERE))


def load(path: Path = FEATURES) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["features"]


def results(path: Path = RESULTS) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"outcomes": {}}


def node_id(test: str) -> str:
    """'backend/tests/x.py::t' as the recorder keys it (relative to agent-improve)."""
    return test[len("agent-improve/"):] if test.startswith("agent-improve/") else test


def status(features: list[dict], res: dict) -> dict[str, str]:
    outcomes = res.get("outcomes") or {}
    return {f["id"]: "passing" if outcomes.get(node_id(f["test"])) == "passed" else "failing"
            for f in features}


def product_hash(root: Path = PROJECT) -> str:
    """The board's source hash WITHOUT `backend/tests/` — what a live run's
    record is bound to. A new test changes no product behaviour, so it must
    not make a run's record stale; a product change must."""
    import hashlib
    import progress
    h = hashlib.sha256()
    for pattern in progress.SOURCE_GLOBS:
        for f in sorted(root.glob(pattern)):
            rel = f.relative_to(root).as_posix()
            if "__pycache__" in f.parts or ".venv" in f.parts or rel.startswith("backend/tests/"):
                continue
            h.update(rel.encode())
            h.update(f.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]


def fresh(res: dict) -> bool:
    """Was the record run on the current source? (the board's own freshness rule)"""
    try:
        import progress
        return res.get("source_hash") == progress.source_hash()
    except Exception:                                   # noqa: BLE001
        return False


def summary(features: list[dict] | None = None, res: dict | None = None) -> dict:
    features = load() if features is None else features
    res = results() if res is None else res
    st = status(features, res)
    lanes = {}
    for lane in LANES:
        mine = [f for f in features if f["lane"] == lane]
        failing = [f["id"] for f in mine if st[f["id"]] == "failing"]
        lanes[lane] = {"total": len(mine), "passing": len(mine) - len(failing),
                       "next": _next(failing, features, st)}
    return {"total": len(features), "passing": sum(v == "passing" for v in st.values()),
            "fresh": fresh(res), "lanes": lanes, "status": st}


def _next(failing: list[str], features: list[dict], st: dict[str, str]) -> str | None:
    """The first failing feature whose dependencies all pass — else the first failing one."""
    by_id = {f["id"]: f for f in features}
    for fid in failing:
        if all(st.get(d) == "passing" for d in by_id[fid]["depends_on"]):
            return fid
    return failing[0] if failing else None


def headline(s: dict | None = None) -> str:
    s = summary() if s is None else s
    lanes = " · ".join(f"{k} {v['passing']}/{v['total']}" for k, v in s["lanes"].items())
    stale = "" if s["fresh"] else " (record older than the source)"
    return f"Define features passing: {s['passing']} of {s['total']} — {lanes}{stale}"


# ── the sets the coverage test holds the list to ────────────────────────────
def define_steps(text: str) -> set[str]:
    """Every Define step, open or not: the Define path table (minus WP0/WP6),
    the owners of a capability row, epic E1, and the table's 'Off the path'."""
    import progress
    import stories
    est = progress.estimates(text)
    owners = {o for r in progress.register(text).values() for o in r["owners"]}
    e1 = {s for s, (e, _) in stories.epic_of().items() if e == "E1"}
    m = re.search(r"\*\*Off the path:\*\*([^\n]*\n[^\n]*)", text)
    off = set(progress._STEP_REF.findall(m.group(1))) if m else set()
    excluded = {s for s, e in est.items() if e["wp"].startswith(NOT_DEFINE_WP)}
    return ((set(est) | owners | e1 | off) - excluded) & set(progress.appendix_d(text))


def capability_rows(text: str) -> set[str]:
    import progress
    return {str(r) for r in progress.register(text)}


def open_gaps(text: str) -> dict[str, set[str]]:
    """Appendix G's open gaps -> the steps their Step cell names. Struck rows
    and §66.6 (closed) are not open."""
    import progress
    lines = text.splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("## Appendix G"))
    end = next(i for i, l in enumerate(lines) if l.startswith("## Appendix H"))
    sub, out = "", {}
    for line in lines[start:end]:
        h = re.match(r"^### (66\.\d+)", line)
        if h:
            sub = h.group(1)
        m = re.match(r"^\|\s*(~~)?\*\*(G-\d+)\*\*", line)
        if not m or m.group(1) or sub == "66.6":
            continue
        cells = line.split("|")
        cell = cells[-2]
        if "closed" in cell.lower():
            continue
        out[m.group(2)] = set(progress._STEP_REF.findall(cell))
    return out


def define_gaps(text: str) -> set[str]:
    """Open gaps whose Step cell names a Define step, or that a founder
    milestone lists as blocking one. (A G-number mentioned in a card's prose
    is not counted: prose moves, and the set must not move with it.)"""
    import progress
    steps = define_steps(text)
    gaps = {g for g, s in open_gaps(text).items() if s & steps}
    for key, ms in progress.milestones(text).items():
        g = re.match(r"G-\d+", key)
        if g and set(ms.get("blocks") or []) & steps and g.group(0) in open_gaps(text):
            gaps.add(g.group(0))
    return gaps


def main(argv: list[str]) -> int:
    s = summary()
    if "--lane" in argv:
        lane = argv[argv.index("--lane") + 1]
        for f in load():
            if f["lane"] == lane and s["status"][f["id"]] == "failing":
                print(f"{f['id']}  {f['test']}\n    {f['description']}")
        return 0
    print(headline(s))
    for lane, v in s["lanes"].items():
        print(f"  lane {lane} ({LANES[lane]}): next failing {v['next'] or '—'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
