"""Define's feature list — status ONLY from test results. Steps 6.66, 6.67.

Anthropic, *Effective harnesses for long-running agents*
(https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents):
the work is ONE JSON feature list; a feature is done when its end-to-end test
passes, never when someone says so. `docs/define_features.json` carries no
status field; this module derives it from `docs/test-results.json`:

    passing   the feature's test is recorded `passed`
    failing   recorded anything else, or never recorded (the test is not written yet)

Since 6.67 it is the ONLY progress source: the board, CONTINUITY, the session
start and the commit guard's landing rule all read it. It owns what the retired
`progress.py` owned for the test recorder (`RESULTS`, `SOURCE_GLOBS`,
`source_hash`) and adds:

    the landing rule    a commit naming DEF-xxx lands only if that feature's
                        test passes and every depends_on feature passes
    the ratchet         once a feature has passed (`docs/features-ratchet.json`),
                        its test is required on every later commit

    python tools/control_board/features.py              # summary, next failing per lane
    python tools/control_board/features.py --lane A     # the lane's failing features
    python tools/control_board/rank.py                  # the ranked queue per lane (ADR-0058)
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
PROJECT = _HERE.parents[1]
FEATURES = PROJECT / "docs" / "define_features.json"
RESULTS = PROJECT / "docs" / "test-results.json"
RATCHET = PROJECT / "docs" / "features-ratchet.json"
RUNTHROUGH = PROJECT / "docs" / "runthrough"
LANES = {"A": "coaching", "B": "gate", "C": "screen and inputs", "integrator": "end-to-end joins"}
#: The product source a test run is bound to (moved here from progress.py at 6.67).
SOURCE_GLOBS = ("backend/**/*.py", "ui/*.html", "skills/**/*.md")
#: The feature tests that read the live run-through's record.
RUNTHROUGH_TESTS = "backend/tests/test_define_runthrough.py::"
#: The five-clause CORE (founder ruling 2026-09-26, D2/D21): "Define works end
#: to end" is ALL the features; the second number leaves out the features that
#: cover quality rows — 22 (the gate rubric) and 26-32 (founder-marked from a
#: traced run). Row 24 has an owner now (the gate lane), so it counts.
CORE_EXCLUDED_ROWS = frozenset({"22", *(str(r) for r in range(26, 33))})


def load(path: Path = FEATURES) -> list[dict]:
    return json.loads(path.read_text(encoding="utf-8"))["features"]


def results(path: Path = RESULTS) -> dict:
    return json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {"outcomes": {}}


def _hash(root: Path, skip_tests: bool) -> str:
    h = hashlib.sha256()
    for pattern in SOURCE_GLOBS:
        for f in sorted(root.glob(pattern)):
            rel = f.relative_to(root).as_posix()
            if "__pycache__" in f.parts or ".venv" in f.parts:
                continue
            if skip_tests and rel.startswith("backend/tests/"):
                continue
            h.update(rel.encode())
            h.update(f.read_bytes().replace(b"\r\n", b"\n"))
    return h.hexdigest()[:16]


def source_hash(root: Path = PROJECT) -> str:
    """The source a test outcome is bound to — product AND tests."""
    return _hash(root, skip_tests=False)


def product_hash(root: Path = PROJECT) -> str:
    """The product source only — what a live run's record is bound to. A new
    test changes no product behaviour, so it must not stale a run's record."""
    return _hash(root, skip_tests=True)


def node_id(test: str) -> str:
    """'backend/tests/x.py::t' as the recorder keys it (relative to agent-improve)."""
    return test[len("agent-improve/"):] if test.startswith("agent-improve/") else test


def status(features: list[dict], res: dict) -> dict[str, str]:
    outcomes = res.get("outcomes") or {}
    return {f["id"]: "passing" if outcomes.get(node_id(f["test"])) == "passed" else "failing"
            for f in features}


def in_core(feature: dict) -> bool:
    rows = set((feature.get("provenance") or {}).get("capability_rows") or [])
    return not rows & CORE_EXCLUDED_ROWS


def blockers(fid: str, features: list[dict], st: dict[str, str]) -> list[str]:
    """Every feature `fid` depends on, TRANSITIVELY, that does not pass —
    dependency blocking is strict (founder ruling 2026-09-26)."""
    by_id = {f["id"]: f for f in features}
    seen: set[str] = set()
    stack = list(by_id[fid]["depends_on"]) if fid in by_id else []
    out: list[str] = []
    while stack:
        d = stack.pop(0)
        if d in seen:
            continue
        seen.add(d)
        if st.get(d) != "passing":
            out.append(d)
        stack.extend(by_id[d]["depends_on"] if d in by_id else [])
    return out


def fresh(res: dict) -> bool:
    """Was the record run on the current source?"""
    return res.get("source_hash") == source_hash()


def shallow(features: list[dict]) -> set[str]:
    """Features whose test the wiring check flags as driving neither the graph nor the API.
    Founder 2026-09-28 (RULINGS §4): one passing count everywhere — such a feature is not
    passing on the board, in CONTINUITY or for rule 10 until its test is end to end."""
    import sys as _sys
    _sys.path.insert(0, str(_HERE.parent / "architecture"))
    try:
        import wiring
        flagged = wiring.check_feature_tests(wiring.named(), features)
    except Exception:  # noqa: BLE001 — a broken check must not change the count silently
        return set()
    return {w["name"] for w in flagged if "drives neither" in w["finding"]}


def summary(features: list[dict] | None = None, res: dict | None = None) -> dict:
    features = load() if features is None else features
    res = results() if res is None else res
    st = status(features, res)
    for fid in shallow(features):
        if st.get(fid) == "passing":
            st[fid] = "failing"
    lanes: dict[str, dict] = {}
    clauses: dict[str, dict] = {}
    import rank  # the computed order (ADR-0058, brief Part F3); imported here: rank imports this module
    nxt = rank.next_per_lane(rank.rank(features, res))
    for lane in LANES:
        mine = [f for f in features if f["lane"] == lane]
        failing = [f["id"] for f in mine if st[f["id"]] == "failing"]
        lanes[lane] = {"total": len(mine), "passing": len(mine) - len(failing), "next": nxt.get(lane)}
    for f in features:
        c = clauses.setdefault(f["clause"], {"total": 0, "passing": 0})
        c["total"] += 1
        c["passing"] += st[f["id"]] == "passing"
    core = [f["id"] for f in features if in_core(f)]
    return {"total": len(features), "passing": sum(v == "passing" for v in st.values()),
            "core": {"total": len(core), "passing": sum(st[i] == "passing" for i in core)},
            "fresh": fresh(res), "lanes": lanes, "clauses": clauses, "status": st}


REQUIREMENTS = PROJECT / "docs" / "requirements"
_BUSINESS_ID = re.compile(r"^\*\*([RCWM]\d+[a-z]?) [^*]*\*\* · (RATIFIED|ACCEPTED|PROPOSED|DRAFT|RETIRED)(.*)$", re.M)
_T_ROW = re.compile(r"^\| (T\d+) \| (.+) \|\s*$", re.M)
_T_RANGE = re.compile(r"T(\d+)–T(\d+) (ACCEPTED|PROPOSED)")
#: Brief Part F2 (founder, 2026-09-27): every entry carries both, on its heading line.
MOSCOW = ("Must", "Should", "Could", "Won't-now", "?")
_MOSCOW = re.compile(r"MoSCoW: (Must|Should|Could|Won't-now|\?)(?=\s|$)")
_DESIGN = re.compile(r"Design: (ADR-\d{4}|none)(?=\s|$)")


def _fields(text: str) -> dict:
    m, d = _MOSCOW.search(text), _DESIGN.search(text)
    return {"moscow": m.group(1) if m else None, "design": d.group(1) if d else None}


def requirements(folder: Path = REQUIREMENTS, texts: dict[str, str] | None = None) -> dict[str, dict]:
    """Every requirement id with its status, MoSCoW, Design (brief Part F2) and, for a T id,
    whether its proof is `none` — read from business.md and platform.md (brief Part A,
    2026-09-27), or from `texts` ({"business.md": …, "platform.md": …}, the guard's staged
    copies). A business id's status is the first on its heading line ("RATIFIED …, amended
    ACCEPTED …" is RATIFIED). A missing field reads as None: `field_problems` names it."""
    texts = texts or {n: (folder / n).read_text(encoding="utf-8") for n in ("business.md", "platform.md")}
    out: dict[str, dict] = {}
    for m in _BUSINESS_ID.finditer(texts["business.md"]):
        out[m.group(1)] = {"status": m.group(2), "proof_none": False, **_fields(m.group(3)),
                           "file": "business.md"}
    platform = texts["platform.md"]
    header = platform[platform.index("## Technical requirements"):platform.index("### State model")]
    status: dict[int, str] = {}
    for a, b, s in _T_RANGE.findall(header):
        for n in range(int(a), int(b) + 1):
            status[n] = s
    for m in _T_ROW.finditer(platform):
        tid, cells = m.group(1), m.group(2)
        st = "RETIRED" if "RETIRED" in cells else status.get(int(tid[1:]), "PROPOSED")
        cols = [c.strip() for c in cells.split("|")]
        moscow = cols[-3] if len(cols) >= 4 and cols[-3] in MOSCOW else None
        design = cols[-2] if len(cols) >= 4 and re.fullmatch(r"ADR-\d{4}|none", cols[-2]) else None
        out[tid] = {"status": st, "proof_none": cells.rstrip().endswith("| none"),
                    "moscow": moscow, "design": design, "file": "platform.md"}
    return out


def field_problems(reqs: dict[str, dict]) -> list[str]:
    """Entries missing `MoSCoW:` or `Design:` (brief Part F2) — the checker refuses them.
    A `?` MoSCoW is allowed until the founder ratifies it."""
    return [f"{i} ({r['file']}) has no {name}" for i, r in reqs.items()
            for name, key in (("MoSCoW: field", "moscow"), ("Design: field", "design")) if not r[key]]


def citable(reqs: dict[str, dict]) -> set[str]:
    """Ids a feature may cite: RATIFIED or ACCEPTED, never PROPOSED, DRAFT or RETIRED."""
    return {i for i, r in reqs.items() if r["status"] in ("RATIFIED", "ACCEPTED")}


def headline(s: dict | None = None) -> str:
    s = summary() if s is None else s
    lanes = " · ".join(f"{k} {v['passing']}/{v['total']}" for k, v in s["lanes"].items())
    stale = "" if s["fresh"] else " (record older than the source)"
    core = s.get("core") or {"passing": 0, "total": 0}
    return (f"{s['passing']} of {s['total']} Define features pass (core {core['passing']} of "
            f"{core['total']}) — {lanes}{stale}")


# ── the landing rule and the ratchet (the commit guard's rule 11) ───────────


def ratchet(path: Path = RATCHET) -> list[str]:
    """Features that have passed once and so must keep passing."""
    return sorted(json.loads(path.read_text(encoding="utf-8"))["passing"]) if path.is_file() else []


def runthrough_fresh() -> bool:
    """Is the newest run-through record bound to the current product source?"""
    files = sorted(RUNTHROUGH.glob("define_runthrough_*.json"))
    if not files:
        return False
    summary_line: dict = next((r for r in json.loads(files[-1].read_text(encoding="utf-8"))
                               if r.get("kind") == "summary"), {})
    return summary_line.get("product_hash") == product_hash()


def landing_refusal(fid: str, features: list[dict], res: dict) -> list[str]:
    """Why a commit naming `fid` may not land, or [] when it may."""
    by_id = {f["id"]: f for f in features}
    if fid not in by_id:
        return [f"{fid} is not in docs/define_features.json"]
    st = status(features, res)
    out = []
    if st[fid] != "passing":
        out.append(f"{fid}'s test does not pass: {by_id[fid]['test']}")
    out += [f"it depends on {d}, whose test does not pass: {by_id[d]['test']}"
            for d in blockers(fid, features, st)]
    return out


def ratchet_refusal(required: list[str], features: list[dict], res: dict) -> tuple[list[str], list[str]]:
    """(refusals, exempted) — every ratcheted feature must still pass. A
    run-through feature is EXEMPT while the run's record is stale: a product
    change stales it for every such feature at once, and only a new live run
    can refresh it. Ruled 2026-09-26: accepted; the integrator re-runs the
    run-through after each merge."""
    by_id = {f["id"]: f for f in features}
    st = status(features, res)
    stale = not runthrough_fresh()
    refused: list[str] = []
    exempt: list[str] = []
    for fid in required:
        if fid not in by_id or st.get(fid) == "passing":
            continue
        if stale and by_id[fid]["test"].startswith(RUNTHROUGH_TESTS):
            exempt.append(fid)
        else:
            refused.append(f"{fid} passed before and its test no longer passes: {by_id[fid]['test']}")
    return refused, exempt


def update_ratchet(features: list[dict] | None = None, res: dict | None = None,
                   path: Path = RATCHET) -> list[str]:
    """Add every feature passing now; never remove one. Returns the new ids."""
    features = load() if features is None else features
    res = results() if res is None else res
    have = set(ratchet(path))
    now = {fid for fid, s in status(features, res).items() if s == "passing"}
    new = sorted(now - have)
    if new or not path.is_file():
        path.write_text(json.dumps({"_about": "Generated by .githooks/pre-commit (step 6.67): every "
                                    "Define feature that has passed once. The commit guard's rule 11 "
                                    "requires each to keep passing. Never hand-edit; never remove an id.",
                                    "passing": sorted(have | now)}, indent=1) + "\n", encoding="utf-8")
    return new


def main(argv: list[str]) -> int:
    s = summary()
    if "--lane" in argv:
        lane = argv[argv.index("--lane") + 1]
        import rank
        by_id = {f["id"]: f for f in load()}
        for r in rank.rank():
            if r["lane"] == lane:
                f = by_id[r["id"]]
                print(f"#{r['rank']} {f['id']}  {f['test']}\n    {f['description']}\n    rank: {r['reason']}")
        return 0
    print(headline(s))
    for lane, v in s["lanes"].items():
        print(f"  lane {lane} ({LANES[lane]}): next failing {v['next'] or '—'}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
